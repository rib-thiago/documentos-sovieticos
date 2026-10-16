"""Conferência HTTP do acervo real, sem modificar catálogo ou textos.

O único artefato criado/reutilizado é o índice derivado em .local/.
"""

import json
import re
import threading
import unittest
from urllib.parse import quote, urlencode
from urllib.request import urlopen

from backend import catalog as model
from backend.server import create_server


class FullCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = model.ROOT
        cls.catalog = model.load()
        cls.server = create_server(cls.root, port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = "http://127.0.0.1:" + str(cls.server.server_address[1])

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def read(self, path):
        with urlopen(self.url + quote(path, safe="/?=&:%"), timeout=30) as response:
            return response.read()

    def test_every_record_is_reachable_without_duplicate_results(self):
        expected = {d["id"] for d in self.catalog["documents"]}
        found = []
        for offset in range(0, len(expected), 100):
            response = json.loads(self.read(f"/api/documents?limit=100&offset={offset}&sort=id"))
            self.assertEqual(response["total"], len(expected))
            found.extend(d["id"] for d in response["items"])
        self.assertEqual(set(found), expected)
        self.assertEqual(len(found), len(expected))

    def test_site_manifest_and_translation_bytes_are_preserved(self):
        self.assertEqual(self.read("/data/manifest.json"), (self.root / "data/manifest.json").read_bytes())
        self.assertIn(b'id="view"', self.read("/"))
        for doc_id in ("showtrials-1665", "ryutin-1932"):
            doc = json.loads(self.read("/api/documents/" + doc_id))
            for edition in doc["editions"]:
                expected = (self.root / edition["file"]).read_bytes()
                self.assertEqual(self.read(edition["content_url"]), expected)

    def test_real_body_search_and_collection_order(self):
        russian = json.loads(self.read("/api/search?" + urlencode({"q": "Николаева", "language": "ru", "limit": 5})))
        self.assertGreater(russian["total"], 0)
        edition = next(e for e in self.catalog["editions"] if e["id"] == "showtrials-1665:pt")
        document = next(d for d in self.catalog["documents"] if d["id"] == edition["document_id"])
        titles = " ".join(document["titles"].values()).casefold()
        body = (self.root / edition["file"]).read_text(encoding="utf-8")
        word = next(w for w in re.findall(r"[^\W\d_]{8,}", body) if w.casefold() not in titles)
        portuguese = json.loads(self.read("/api/search?" + urlencode({"q": word, "language": "pt", "limit": 100})))
        self.assertIn("showtrials-1665", {d["id"] for d in portuguese["items"]})
        expected = [m["document_id"] for m in self.catalog["memberships"] if m["collection_id"] == "centro-de-leningrado"]
        result = json.loads(self.read("/api/documents?collection=centro-de-leningrado&sort=source&limit=5"))
        self.assertEqual([d["id"] for d in result["items"]], expected[:5])
        self.assertEqual(result["total"], len(set(expected)))


if __name__ == "__main__":
    unittest.main()
