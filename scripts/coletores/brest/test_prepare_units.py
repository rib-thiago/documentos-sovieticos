import unittest
from prepare_units import convert


class FootnoteTests(unittest.TestCase):
    def test_english_note_becomes_local_without_losing_note_text(self):
        source = b'<html><title>Title</title><body><p>Body <sup><a id="1." href="#1n">[1]</a></sup></p><h3>Notes</h3><p><sup><a id="1n" href="#1.">[1]</a></sup>Preserved note text.</p></body></html>'
        content, detail = convert(source, "https://example.org/source.htm")
        self.assertIn("[^src-1n]", content)
        self.assertIn("[^src-1n]:", content)
        self.assertIn("Preserved note text.", content)
        self.assertEqual(detail["local_footnotes"], 1)
        self.assertNotIn("BRESTNOTEREFERENCE", content)

    def test_portuguese_endnote_and_credit_remain_present(self):
        source = '<html><title>Título</title><body><p class="info">Tradução: Crédito original</p><p>Corpo<a href="#tn244">[N244]</a></p><p class="note"><a name="tn244"></a>[N244] Nota preservada.</p></body></html>'.encode()
        content, detail = convert(source, "https://example.org/document.htm")
        self.assertIn("Nota preservada", content)
        self.assertIn("Crédito original", content)
        self.assertEqual(detail["local_footnotes"], 1)
        self.assertIn("Tradução:", detail["credits_literal"][0])

    def test_complex_note_stays_in_source_order_and_requires_review(self):
        source = b'<body><p>Body<a href="#1n">[1]</a></p><p><a id="1n"></a>Complex <a id="2n"></a>note.</p></body>'
        content, detail = convert(source, "https://example.org/source.htm")
        self.assertIn("Complex", content)
        self.assertIn("1n", detail["unresolved_notes"])
        self.assertNotIn("BRESTNOTEREFERENCE", content)

    def test_publication_date_is_not_invented_as_date_of_writing(self):
        source = b'<body><p class="information">First Published: 1972 Source: Later edition</p><p>Text.</p></body>'
        _, detail = convert(source, "https://example.org/a")
        self.assertIsNone(detail["written_literal"])


if __name__ == "__main__":
    unittest.main()
