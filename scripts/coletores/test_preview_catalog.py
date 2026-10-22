import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
spec = importlib.util.spec_from_file_location("preview_catalog", Path(__file__).with_name("preview_catalog.py"))
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)


def empty_catalog():
    return {"documents": [], "editions": [], "collections": [], "memberships": [],
            "vocabularies": {"document_types": {"article": "Artigo"}, "kinds": {"document": "Documento", "article": "Artigo"},
                             "languages": {"ru": "Russo", "pt": "Português", "en": "Inglês"}},
            "provenance": {"schema_version": 1, "manifest_projection": {"fields": ["collections", "documents"], "global_document_ids": []}}}


def unit(work, front="brest", ident="new-document", text="# Title\n\nText preserved.\n"):
    folder = work / front
    folder.mkdir(parents=True, exist_ok=True)
    raw = b"<article>Text preserved.</article>"
    (folder / "raw.html").write_bytes(raw)
    (folder / (ident + ".md")).write_text(text, encoding="utf-8")
    return {"id": ident, "title_literal": "Title", "language": "en", "source_url": "https://example.org/document",
            "raw": "raw.html", "raw_sha256": preview.model.sha256(raw), "markdown": ident + ".md",
            "markdown_sha256": preview.model.sha256(text.encode()), "ready_for_import": True,
            "subcollection": "documents", "kind": "document", "document_type": "article"}


def save(work, front, units):
    (work / front / "units.json").write_text(json.dumps({"units": units}), encoding="utf-8")


class PreviewTests(unittest.TestCase):
    def test_structured_review_reasons_can_be_exported(self):
        reason = {"note": 1066, "definition_page": 30}
        rendered = preview.reason_text(reason)
        self.assertEqual(json.loads(rendered), reason)

    def test_new_document_is_staged_without_mutating_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            save(work, "brest", [unit(work)])
            current = empty_catalog()
            before = copy.deepcopy(current)
            result, files, decisions, counts = preview.build(current, work, work)
            self.assertEqual(current, before)
            self.assertEqual(counts["documents"], 1)
            self.assertEqual(decisions[0]["status"], "prepared")
            self.assertEqual(len(files), 1)
            self.assertFalse((work / "originais").exists())
            self.assertEqual(len(result["memberships"]), 2)

    def test_hash_mismatch_is_blocked_before_creating_any_record(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            record = unit(work)
            record["markdown_sha256"] = "incorrect"
            save(work, "brest", [record])
            result, files, decisions, _ = preview.build(empty_catalog(), work, work)
            self.assertEqual(result["documents"], [])
            self.assertEqual(files, {})
            self.assertEqual(decisions[0]["status"], "blocked")

    def test_invalid_membership_does_not_leave_orphan_document(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            record = unit(work)
            record["subcollection"] = "../../invalid"
            save(work, "brest", [record])
            result, _, decisions, _ = preview.build(empty_catalog(), work, work)
            self.assertEqual(result["documents"], [])
            self.assertEqual(decisions[0]["status"], "blocked")

    def test_same_text_in_two_fronts_reuses_document_and_memberships(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            save(work, "svitlana", [unit(work, "svitlana", "first-id")])
            save(work, "brest", [unit(work, "brest", "second-id")])
            result, files, decisions, _ = preview.build(empty_catalog(), work, work)
            self.assertEqual(len(result["documents"]), 1)
            self.assertEqual(len(result["editions"]), 1)
            self.assertEqual(len(result["memberships"]), 4)
            self.assertEqual(len(files), 1)
            self.assertTrue(decisions[1]["reuses_prepared"])

    def test_distinct_versions_of_same_language_do_not_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            first = unit(work, ident="first")
            second = unit(work, ident="second", text="# Different\n\nOther version.\n")
            first["document_id"] = second["document_id"] = "same-document"
            save(work, "brest", [first, second])
            result, _, decisions, _ = preview.build(empty_catalog(), work, work)
            self.assertEqual(len(result["editions"]), 1)
            self.assertEqual(decisions[1]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
