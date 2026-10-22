"""Regressões de preservação e descoberta; sem acesso à rede."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("brest_coletar", Path(__file__).with_name("coletar.py"))
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class Fetch:
    def __init__(self, text):
        self.text = text

    def get(self, url):
        return self.text, "text/html"


class PreservationTests(unittest.TestCase):
    def test_duplicate_retains_both_memberships(self):
        rows = [dict(id="a", url="https://example.org/a#one", grupo="g1"),
                dict(id="b", url="https://example.org/a#two", grupo="g2")]
        combined = list(collector.sources_by_url(rows).values())
        self.assertEqual(len(combined), 1)
        self.assertEqual(combined[0]["grupos"], ["g1", "g2"])
        self.assertEqual(len(combined[0]["ocorrencias"]), 2)

    def test_refresh_preserves_edited_markdown_and_raw_versions(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            source = dict(id="sample", url="https://example.org/docs/a", grupo="g", idioma="ru", tipo="html")
            first = collector.process(source, Fetch(b"<article><h1>First</h1><p>Old text.</p></article>"), output, False)
            working = output / first["md_path"]
            working.write_text("Editorial correction\n", encoding="utf-8")
            second = collector.process(source, Fetch(b"<article><h1>Second</h1><p>New text.</p></article>"), output, True)
            self.assertEqual(working.read_text(), "Editorial correction\n")
            self.assertTrue(second["derivado_diverge_do_candidato"])
            self.assertTrue((output / first["raw_path"]).exists())
            self.assertTrue((output / second["raw_path"]).exists())
            self.assertNotEqual(first["raw_path"], second["raw_path"])
            self.assertIn("New text", (output / second["candidate_path"]).read_text())

    def test_partial_report_and_planning_do_not_erase_acquisitions(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            first = dict(id="a", url="https://example.org/a", estado_aquisicao="FOUND_HTML_UNREVIEWED")
            second = dict(id="b", url="https://example.org/b", estado_aquisicao="ERROR")
            collector.save_report(output, [first], [])
            collector.save_report(output, [second], [])
            collector.save_report(output, [{**first, "estado_aquisicao": "PLANEJADO"}], [])
            rows = json.loads((output / "inventario.json").read_text())
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["estado_aquisicao"], "FOUND_HTML_UNREVIEWED")

    def test_failed_sources_are_retried_without_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            source = dict(id="sample", url="https://example.org/a", grupo="g", idioma="en", tipo="html")
            class Failure:
                def get(self, url):
                    raise OSError("offline")
            self.assertEqual(collector.process(source, Failure(), output, False)["estado_aquisicao"], "ERROR")
            result = collector.process(source, Fetch(b"<article><p>Recovered document</p></article>"), output, False)
            self.assertEqual(result["estado_aquisicao"], "FOUND_HTML_UNREVIEWED")

    def test_relative_links_and_note_anchors(self):
        _, markdown = collector.html_root(b'<article><h1>Title</h1><p><a href="../other">Other</a> <a href="#note1">Note</a></p></article>', "https://example.org/docs/a")
        self.assertIn("https://example.org/other", markdown)
        self.assertIn("#note1", markdown)


if __name__ == "__main__":
    unittest.main()
