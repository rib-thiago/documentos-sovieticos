import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("consolidar", Path(__file__).with_name("consolidar.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ConsolidationTests(unittest.TestCase):
    def test_wayback_and_original_share_comparison_key(self):
        original = "https://istmat.org/node/27376"
        archived = "https://web.archive.org/web/20250906080617id_/http://istmat.org/node/27376"
        self.assertEqual(module.normalize_url(original), module.normalize_url(archived))
        self.assertNotEqual(module.normalize_url(original), module.normalize_url("https://istmat.org/node/27377"))

    def test_files_outside_front_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            result = module.verify_file(Path(directory), "../../data/catalog/documents.json")
            self.assertIn("error", result)

    def test_hash_mismatch_is_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "candidate.md").write_text("Edited text")
            result = module.verify_file(root, "candidate.md", "not-the-actual-hash")
            self.assertFalse(result["hash_matches"])

    def test_matching_does_not_modify_catalog_or_approve_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "data/catalog/documents.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps([{"id": "existing", "source": {"url": "http://example.org/document"}}]))
            before = path.read_bytes()
            row = module.candidate("test", "new", {"source_url": "https://example.org/document"}, root)
            result = module.reconcile([row], root)[0]
            self.assertEqual(result["catalog_url_matches"], ["existing"])
            self.assertFalse(result["ready_for_import"])
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
