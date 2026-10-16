"""Testa decisões estruturais e o fluxo de revisão do lote integral."""

import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import convert_showtrials_all as mass
import prepare_markdown as base


def detect(html, document_type="statement"):
    parsed = mass.DocumentHTML(html)
    plain = base.blocks(base.legacy_text(html))
    headings, doubtful = mass.automatic_headings(parsed, plain, document_type)
    return parsed, plain, headings, doubtful


class MassConversionTests(unittest.TestCase):
    def test_table_cells_are_not_section_headings(self):
        parsed, plain, headings, _ = detect('<table><tr><td><p align="center">I. Nomes</p></td><td><p align="center">II. Valores</p></td></tr></table>')
        self.assertEqual(headings, [])
        self.assertTrue(all(i["in_table"] for i in parsed.paragraph_info))
        problems = mass.review_issues(parsed, plain, headings, [])
        self.assertEqual(problems[0]["code"], "tabelas_linearizadas")

    def test_poem_stanzas_are_not_sections(self):
        _, _, headings, _ = detect('<p align="center">КОЛЫБЕЛЬНАЯ ПЕСНЯ</p><p align="center">I.</p><p>Verso</p><p align="center">II.</p><p>Verso</p>')
        self.assertEqual(headings, [])

    def test_dates_and_addresses_are_not_sections(self):
        _, _, headings, _ = detect('<p align="center">27.XII.1934 г.</p><p align="center">СЕКРЕТАРЮ ЦК ВКП(б)</p><p align="center">тов. СТАЛИНУ.</p><p>Corpo.</p>')
        self.assertEqual(headings, [])

    def test_standalone_generic_header_does_not_create_a_pointless_index(self):
        _, _, headings, _ = detect('<p align="center">ПРОТОКОЛ ДОПРОСА</p><p>Corpo.</p>')
        self.assertEqual(headings, [])

    def test_interrogated_names_replace_repeated_generic_markers(self):
        _, _, headings, _ = detect('<p align="center">ДОПРОС</p><p align="center">ИВАНОВА Ивана.</p><p>Corpo</p><p align="center">ДОПРОС</p><p align="center">ПЕТРОВА Петра.</p><p>Corpo</p>')
        self.assertEqual([h["text"] for h in headings], ["ИВАНОВА Ивана.", "ПЕТРОВА Петра."])

    def test_duplicate_titles_are_reported_without_arbitrary_mapping(self):
        _, _, headings, doubtful = detect('<p align="center">I. Раздел</p><p>Corpo</p><p align="center">I. Раздел</p>')
        self.assertEqual(headings, [])
        self.assertEqual(len(doubtful), 2)
        self.assertEqual(doubtful[0]["matching_blocks"], [0, 2])

    def test_numbered_subsections_preserve_their_blocks(self):
        _, plain, headings, _ = detect('<p align="center">I. Часть</p><p align="center">1. Раздел</p><p>Corpo</p><p align="center">II. Другая часть</p>')
        self.assertEqual([h["level"] for h in headings], [2, 3, 2])
        self.assertEqual(len(base.blocks(base.render_conversion("\n\n".join(plain), headings))), len(plain))

    def test_large_table_and_image_without_text_are_urgent(self):
        for html in ('<table><tr>' + '<td>1</td>' * 20 + '</tr></table>', '<p><img src="scan.jpg" /></p>'):
            parsed, plain, headings, doubtful = detect(html)
            problems = mass.review_issues(parsed, plain, headings, doubtful)
            self.assertEqual(problems[0]["priority"], "urgente")
            self.assertTrue(problems[0]["action"])

    def test_queue_preserves_reviewer_status_and_notes(self):
        record = {"id": "showtrials-1", "collections": ["Coleção / Subcoleção"], "title_ru": "Título",
                  "markdown": "originais/showtrials/showtrials-1.ru.md", "source_url": "fonte", "method": "automatico",
                  "blocks": 1, "headings": [], "priority": "alta", "issues": [mass.issue("exemplo", "alta", "media", "Dificuldade", "Conferir") ]}
        with tempfile.TemporaryDirectory() as directory, patch.object(mass, "OUT", Path(directory)):
            mass.write_reports([record], True)
            path = Path(directory) / "pendencias.csv"
            with path.open(newline="") as file:
                reader = csv.DictReader(file)
                fields, rows = reader.fieldnames, list(reader)
            rows[0].update(status="em_revisao", notas_do_revisor="Conferi a fonte")
            with path.open("w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            mass.write_reports([record], True)
            with path.open(newline="") as file:
                row = next(csv.DictReader(file))
            self.assertEqual(row["status"], "em_revisao")
            self.assertEqual(row["notas_do_revisor"], "Conferi a fonte")

    def test_accept_headings_keeps_original_content_and_rejects_body_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            txt = root / "source.txt"
            txt.write_text("Título\n\nCorpo <literal>\n")
            md = root / "edited.md"
            md.write_text("## Título\n\nCorpo \\<literal\\>\n")
            catalog = root / "recipes.json"
            recipe = {"id": "showtrials-1", "original": "source.txt", "markdown": "edited.md",
                      "original_sha256": base.digest(txt.read_bytes()), "blocks": 2, "headings": []}
            catalog.write_text(json.dumps({"documents": [recipe]}))
            with patch.object(mass, "ROOT", root), patch.multiple(base, ROOT=root, RECIPES=catalog), contextlib.redirect_stdout(io.StringIO()):
                mass.accept_headings("showtrials-1")
                registered = catalog.read_bytes()
                self.assertEqual(json.loads(registered)["documents"][0]["method"], "revisao_local")
                md.write_text("## Título\n\nCorpo alterado\n")
                with self.assertRaisesRegex(ValueError, "alterações além"):
                    mass.accept_headings("showtrials-1")
                self.assertEqual(catalog.read_bytes(), registered)


if __name__ == "__main__":
    unittest.main()
