"""Integração do catálogo, índice e HTTP usando um acervo pequeno independente."""

import copy
import hashlib
import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from backend import catalog as model
from backend.database import QueryError, Repository, ensure_index
from backend.server import create_server
from scripts.catalog_guard import ensure_legacy_manifest_write_allowed


def fixture(root):
    (root / "data").mkdir()
    (root / "originais").mkdir()
    (root / "assets").mkdir()
    (root / "assets/style.css").write_text("body{}")
    (root / "index.html").write_text('<html lang="pt-BR">Site existente</html>')
    bodies = {"one.ru.md": "## Протокол\n\nНиколаева на красной площади. редкийтермин.\n",
              "one.pt.md": "## Protocolo\n\nTradução de Nikolaev. passagem exclusiva.\n",
              "two.ru.md": "Иванов. Свидетельство о заседании.\n", "editorial.pt.md": "Ensaio histórico inédito.\n"}
    for name, body in bodies.items():
        (root / "originais" / name).write_text(body)
    documents = [
        {"id": "showtrials-1", "type": "document", "title_ru": "Протокол Николаева", "title_pt": "Protocolo de Nikolaev",
         "source_id": "1", "source_name": "ShowTrials", "source_url": "https://example.org/one/", "document_type": "interrogation_protocol", "format": "text",
         "languages": [{"code": "ru", "label": "Russo", "file": "originais/one.ru.md", "format": "markdown"},
                       {"code": "pt", "label": "Português", "file": "originais/one.pt.md", "format": "markdown"}]},
        {"id": "showtrials-2", "type": "document", "title_ru": "Иванов", "document_type": "letter",
         "languages": [{"code": "ru", "label": "Russo", "file": "originais/two.ru.md"}]}]
    editorial = {"id": "editorial", "type": "article", "title_pt": "Ensaio", "title_ru": "Статья", "date": "2008",
                 "archive": "Referência editorial", "author": "Autor", "shortTitle": "Ensaio curto", "eyebrow": "História",
                 "custom": {"preservar": True}, "languages": [{"code": "pt", "label": "Português", "file": "originais/editorial.pt.md", "custom_language": 7}]}
    manifest = {"collections": [
        {"id": "alpha", "title_pt": "Alfa", "title_ru": "Альфа", "cover": "assets/cover.jpg", "document_ids": ["showtrials-2", "showtrials-1"],
         "subcollections": [{"id": "investigacao", "title_pt": "Investigação", "title_ru": "Следствие", "source_id": "10", "source_url": "https://example.org/collection", "document_ids": ["showtrials-2", "showtrials-1"]}]},
        {"id": "beta", "title_pt": "Beta", "title_ru": "Бета", "document_ids": ["showtrials-2"],
         "subcollections": [{"id": "investigacao", "title_pt": "Investigação", "title_ru": "Следствие", "document_ids": ["showtrials-2"]}]},
        {"id": "editorial", "title_pt": "Editoriais", "title_ru": "Статьи", "documents": [editorial]}], "documents": documents}
    (root / "data/manifest.json").write_bytes(model.json_bytes(manifest))
    return manifest


class CatalogFixture(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.manifest = fixture(self.root)

    def migrate(self):
        model.migrate(self.root)
        return model.load(self.root)


class CatalogTests(CatalogFixture):
    def test_round_trip_preserves_manifest_content_and_bytes_of_every_source(self):
        before = {p: p.read_bytes() for p in [self.root / "data/manifest.json", *list((self.root / "originais").iterdir())]}
        catalog = self.migrate()
        self.assertEqual(model.export_manifest(catalog), self.manifest)
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        self.assertEqual(len(catalog["documents"]), 3)
        self.assertEqual(len(catalog["editions"]), 4)
        self.assertEqual({c["id"] for c in catalog["collections"] if c["parent_id"]}, {"alpha/investigacao", "beta/investigacao"})

    def test_unknown_metadata_and_language_overrides_survive(self):
        catalog = self.migrate()
        exported = model.export_manifest(catalog)
        self.assertEqual(exported["collections"][2]["documents"][0]["custom"], {"preservar": True})
        self.assertEqual(exported["collections"][2]["documents"][0]["languages"][0]["custom_language"], 7)
        self.assertEqual(catalog["editions"][0]["format"], "markdown")
        self.assertNotIn("format", exported["documents"][1]["languages"][0])

    def test_repeat_migration_refuses_to_overwrite_catalog(self):
        self.migrate()
        path = self.root / "data/catalog/documents.json"
        before = path.read_bytes()
        with self.assertRaisesRegex(model.CatalogError, "já existe"):
            model.migrate(self.root)
        self.assertEqual(before, path.read_bytes())

    def test_orphan_association_and_duplicate_edition_are_rejected(self):
        catalog = self.migrate()
        invalid = copy.deepcopy(catalog)
        invalid["memberships"][0]["document_id"] = "ausente"
        with self.assertRaisesRegex(model.CatalogError, "órfã"):
            model.validate(invalid, self.root)
        invalid = copy.deepcopy(catalog)
        invalid["editions"].append(dict(invalid["editions"][0], id="duplicada"))
        with self.assertRaisesRegex(model.CatalogError, "Idioma repetido"):
            model.validate(invalid, self.root)

    def test_changed_text_requires_explicit_hash_refresh(self):
        catalog = self.migrate()
        (self.root / "originais/one.ru.md").write_text("Revisão intencional\n")
        with self.assertRaisesRegex(model.CatalogError, "Arquivo mudou"):
            model.validate(catalog, self.root)
        preview = model.refresh_files(self.root)
        self.assertFalse(preview["written"])
        self.assertEqual(len(preview["changes"]), 1)
        self.assertTrue(model.refresh_files(self.root, write=True)["written"])
        model.validate(model.load(self.root), self.root)

    def test_export_detects_manifest_drift(self):
        catalog = self.migrate()
        self.manifest["documents"][0]["title_pt"] = "Mudança fora do catálogo"
        (self.root / "data/manifest.json").write_bytes(model.json_bytes(self.manifest))
        with self.assertRaisesRegex(model.CatalogError, "Manifesto desatualizado"):
            model.validate(catalog, self.root)

    def test_new_metadata_is_exported_and_edition_format_is_kept(self):
        catalog = self.migrate()
        document = next(d for d in catalog["documents"] if d["id"] == "showtrials-2")
        document["titles"]["pt"] = "Título português acrescentado"
        document["historical_date"].update(value="1934-12-01", precision="day")
        edition = next(e for e in catalog["editions"] if e["document_id"] == "showtrials-2")
        edition["format"] = "text"
        exported = model.export_manifest(catalog)["documents"][1]
        self.assertEqual(exported["title_pt"], "Título português acrescentado")
        self.assertEqual(exported["date"], "1934-12-01")
        self.assertEqual(exported["languages"][0]["format"], "text")

    def test_subcollection_members_require_parent_membership(self):
        catalog = self.migrate()
        catalog["memberships"] = [m for m in catalog["memberships"] if not (m["collection_id"] == "beta")]
        with self.assertRaisesRegex(model.CatalogError, "ausente na coleção principal"):
            model.validate(catalog, self.root)

    def test_invalid_historical_dates_are_rejected(self):
        catalog = self.migrate()
        for value, precision in (("2022-12-08T15:06:30", "day"), ("1934-02-31", "day"), ("1934-14", "month"), ("1934", "not_recorded")):
            catalog["documents"][0]["historical_date"].update(value=value, precision=precision)
            with self.subTest(value=value), self.assertRaisesRegex(model.CatalogError, "Data histórica ISO inválida"):
                model.validate(catalog, self.root, check_manifest=False)

    def test_extra_fields_cannot_override_standard_metadata(self):
        catalog = self.migrate()
        catalog["documents"][0]["extra"]["document_type"] = "letter"
        with self.assertRaisesRegex(model.CatalogError, "duplicado em extra"):
            model.validate(catalog, self.root)

    def test_content_path_cannot_escape_originals(self):
        for path in ("../segredo", "/etc/passwd", "data/manifest.json", "originais/../index.html"):
            with self.subTest(path=path), self.assertRaises(model.CatalogError):
                model.content_path(self.root, path)

    def test_legacy_writers_are_blocked_after_migration(self):
        ensure_legacy_manifest_write_allowed(self.root)
        self.migrate()
        before = (self.root / "data/manifest.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "catálogo principal"):
            ensure_legacy_manifest_write_allowed(self.root)
        self.assertEqual((self.root / "data/manifest.json").read_bytes(), before)


class RepositoryTests(CatalogFixture):
    def setUp(self):
        super().setUp()
        self.catalog = self.migrate()
        self.db = self.root / ".local/catalog.sqlite3"
        self.info = ensure_index(self.root, self.db, self.catalog)
        self.repository = Repository(self.root, self.db, self.catalog, self.info)

    def test_search_matches_russian_body_and_portuguese_translation(self):
        ru = self.repository.documents({"q": "редкийтермин", "language": "ru"})
        self.assertEqual([d["id"] for d in ru["items"]], ["showtrials-1"])
        self.assertIn("редкийтермин", ru["items"][0]["match"]["snippet"])
        pt = self.repository.documents({"q": "passagem", "language": "pt"})
        self.assertEqual(pt["total"], 1)
        self.assertEqual(self.repository.documents({"q": "passagem", "language": "ru"})["total"], 0)

    def test_phrase_and_title_scope(self):
        self.assertEqual(self.repository.documents({"q": '"красной площади"'})["total"], 1)
        self.assertEqual(self.repository.documents({"q": "редкийтермин", "scope": "title"})["total"], 0)
        self.assertEqual(self.repository.documents({"q": "Николаева", "scope": "title"})["total"], 1)

    def test_multi_language_results_are_deduplicated_and_paginated(self):
        self.assertEqual(self.repository.documents({"q": "Николаева"})["total"], 1)
        result = self.repository.documents({"limit": "1", "offset": "1", "sort": "id"})
        self.assertEqual(result["total"], 3)
        self.assertEqual(len(result["items"]), 1)
        self.assertTrue(result["has_more"])

    def test_filters_cover_all_memberships_and_preserve_source_order(self):
        result = self.repository.documents({"collection": "alpha", "subcollection": "investigacao", "sort": "source"})
        self.assertEqual([d["id"] for d in result["items"]], ["showtrials-2", "showtrials-1"])
        self.assertEqual(self.repository.documents({"collection": "beta", "type": "letter"})["total"], 1)
        self.assertEqual(self.repository.documents({"collection": "alpha", "language": "pt"})["total"], 1)
        self.assertEqual(self.repository.documents({"type": "unspecified"})["total"], 1)

    def test_invalid_queries_are_rejected(self):
        for params in ({"limit": "1000"}, {"offset": "-1"}, {"subcollection": "investigacao"}, {"q": '"sem fim'},
                       {"collection": "' OR 1=1--"}, {"sort": "drop table"}, {"unknown": "x"}):
            with self.subTest(params=params), self.assertRaises(QueryError):
                self.repository.documents(params)

    def test_index_reuse_and_rebuild(self):
        self.assertFalse(ensure_index(self.root, self.db, self.catalog)["rebuilt"])
        self.db.write_bytes(b"indice danificado")
        self.assertTrue(ensure_index(self.root, self.db, self.catalog)["rebuilt"])
        self.assertEqual(self.repository.documents({})["total"], 3)

    def test_detail_includes_all_editions_and_collections(self):
        doc = self.repository.document("showtrials-2")
        self.assertEqual(len(doc["collections"]), 4)
        self.assertEqual(len(self.repository.document("showtrials-1")["editions"]), 2)
        self.assertIsNone(self.repository.document("ausente"))
        self.assertEqual(self.repository.collection("alpha")["children"][0]["document_count"], 2)


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.root = Path(cls.directory.name)
        fixture(cls.root)
        model.migrate(cls.root)
        cls.server = create_server(cls.root, port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = "http://127.0.0.1:" + str(cls.server.server_address[1])

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.directory.cleanup()

    def get(self, path):
        return urlopen(self.url + quote(path, safe="/?=&:%"), timeout=5)

    def test_site_and_operational_page(self):
        with self.get("/") as response:
            self.assertIn("Site existente", response.read().decode())
        with self.get("/local") as response:
            self.assertIn("3 documentos", response.read().decode())

    def test_health_document_and_original_content(self):
        with self.get("/api/health") as response:
            self.assertEqual(json.load(response)["documents"], 3)
        with self.get("/api/documents/showtrials-1") as response:
            doc = json.load(response)
        for edition in doc["editions"]:
            with self.get(edition["content_url"]) as response:
                self.assertEqual(response.read(), (self.root / edition["file"]).read_bytes())

    def test_http_search_and_concurrent_reads(self):
        path = "/api/search?" + urlencode({"q": "редкийтермин", "language": "ru"})
        def request(_):
            with self.get(path) as response:
                return json.load(response)["total"]
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(list(pool.map(request, range(8))), [1] * 8)

    def test_errors_and_unpublished_files(self):
        for path, code in (("/api/documents/ausente", 404), ("/api/search", 400), ("/api/documents?limit=0", 400),
                           ("/temporario/segredo", 404), ("/.git/config", 404), ("/assets/../data/catalog/documents.json", 404),
                           ("/data/catalog/provenance.json", 404), ("/api/documents?limit=1&limit=2", 400)):
            with self.subTest(path=path), self.assertRaises(HTTPError) as caught:
                self.get(path)
            self.assertEqual(caught.exception.code, code)
        with self.assertRaises(HTTPError) as caught:
            urlopen(Request(self.url + "/api/documents", data=b"{}", method="POST"))
        self.assertEqual(caught.exception.code, 405)


if __name__ == "__main__":
    unittest.main()
