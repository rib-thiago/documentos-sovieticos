"""Verificações de fidelidade e proteção de revisões na conversão estrutural."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import prepare_markdown as converter


class ConversionTests(unittest.TestCase):
    def test_literal_signs_and_internal_breaks(self):
        text = "<слово> &amp; [1] * * * _текст_ `abc` \\x\n1. texto\n> fala\n===\n\nFim"
        result = converter.render_conversion(text, [])
        self.assertEqual(len(converter.blocks(result)), 2)
        for literal in (r"\<слово\>", r"\&amp;", r"\[1\]", r"\* \* \*", r"1\. texto", r"\> fala", r"\==="):
            self.assertIn(literal, result)

    def test_headings_keep_block_positions_and_depth(self):
        text = "Parte\n\nSeção\n\nSubseção\n\nCorpo"
        headings = [{"block": i, "level": i + 2, "text": t} for i, t in enumerate(["Parte", "Seção", "Subseção"])]
        self.assertEqual(converter.render_conversion(text, headings), "## Parte\n\n### Seção\n\n#### Subseção\n\nCorpo\n")

    def test_duplicate_or_invalid_heading_positions_are_rejected(self):
        heading = {"block": 0, "level": 2, "text": "Título"}
        for headings in ([heading, heading], [dict(heading, block=2)], [dict(heading, level=7)]):
            with self.subTest(headings=headings), self.assertRaises(AssertionError):
                converter.render_conversion("Título", headings)

    def test_html_and_txt_inline_spacing_can_differ_without_changing_characters(self):
        source = converter.SourceHTML('<p style="text-align:center">I. <strong>Título</strong>.</p><p align="center">II. Outro</p>')
        review = {"id": "exemplo", "headings": [
            {"html_paragraph": 0, "html_text": "I. Título.", "level": 2},
            {"html_paragraph": 1, "html_text": "II. Outro", "level": 3},
        ]}
        result = converter.reviewed_headings(review, source, ["I. Título .", "II. Outro"])
        self.assertEqual([h["block"] for h in result], [0, 1])
        self.assertEqual([h["level"] for h in result], [2, 3])

    def test_ambiguous_titles_are_rejected(self):
        source = converter.SourceHTML('<p align="center">Título</p>')
        review = {"id": "exemplo", "headings": [{"html_paragraph": 0, "html_text": "Título", "level": 2}]}
        with self.assertRaisesRegex(ValueError, "ambíguo"):
            converter.reviewed_headings(review, source, ["Título", "Título"])

    def test_changed_source_is_rejected(self):
        source = converter.SourceHTML('<p align="center">Outro título</p>')
        review = {"id": "exemplo", "headings": [{"html_paragraph": 0, "html_text": "Título", "level": 2}]}
        with self.assertRaisesRegex(ValueError, "HTML diferente"):
            converter.reviewed_headings(review, source, ["Título"])

    def test_legacy_extraction_preserves_editorial_brackets(self):
        html = "<p>A <b>B</b> &lt;expansão&gt;<br>C</p><div>D</div>E"
        self.assertEqual(converter.legacy_text(html), "A B <expansão>\nC\n\n D\nE")

    def test_local_markdown_revision_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            originals = root / "originais/showtrials"
            originals.mkdir(parents=True)
            package = root / "package"
            posts = package / "original/local/posts-json"
            posts.mkdir(parents=True)
            html = '<p align="center">Primeiro</p><p align="center">Segundo</p>'
            (posts / "posts-page-1.json").write_text(json.dumps([{"id": 1, "content": {"rendered": html}}]))
            txt = originals / "showtrials-1.ru.txt"
            txt.write_text("Primeiro\n\nSegundo\n")
            md = originals / "showtrials-1.ru.md"
            md.write_text("Revisão feita pelo editor\n")
            manifest = root / "data/manifest.json"
            manifest.write_text(json.dumps({"documents": [{"id": "showtrials-1", "source_id": "1", "title_ru": "Exemplo", "source_url": "fonte", "languages": [{"code": "ru", "file": "originais/showtrials/showtrials-1.ru.txt"}]}]}))
            review = root / "data/markdown-review.json"
            review.write_text(json.dumps({"documents": [{"id": "showtrials-1", "title_pt": "Exemplo", "structure": "seções", "notes": "", "headings": [{"html_paragraph": i, "html_text": t, "level": 2} for i, t in enumerate(["Primeiro", "Segundo"])]}], "deferred": []}))
            before = {p: p.read_bytes() for p in (manifest, txt, md)}
            with patch.multiple(converter, ROOT=root, REVIEW=review, RECIPES=root / "data/markdown-conversions.json"):
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, "Revisão local diferente"):
                    converter.prepare(package, {"1"})
            self.assertEqual({p: p.read_bytes() for p in before}, before)
            self.assertFalse((root / "data/markdown-conversions.json").exists())


if __name__ == "__main__":
    unittest.main()
