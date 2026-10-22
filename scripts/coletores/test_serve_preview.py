import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
spec = importlib.util.spec_from_file_location("serve_preview", Path(__file__).with_name("serve_preview.py"))
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class ReadOnlyPreviewTests(unittest.TestCase):
    def test_staged_manifest_wins_and_assets_fall_back_to_site(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root, package = base / "site", base / "preview"
            for path, value in [(root / "data/manifest.json", "old"), (package / "files/data/manifest.json", "new"),
                                (root / "assets/style.css", "styles")]:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value)
            self.assertEqual(server.resolve_public(root, package, "/data/manifest.json").read_text(), "new")
            self.assertEqual(server.resolve_public(root, package, "/assets/style.css?v=1").read_text(), "styles")

    def test_private_files_and_editorial_api_are_unavailable(self):
        root, package = Path("/tmp/site"), Path("/tmp/preview")
        for path in ("/temporario/private.pdf", "/.git/config", "/.local/editorial/history", "/api/editorial/session", "/editorial"):
            self.assertIsNone(server.resolve_public(root, package, path))

    def test_encoded_traversal_is_rejected(self):
        root, package = Path("/tmp/site"), Path("/tmp/preview")
        for path in ("/assets/%2e%2e/%2e%2e/.git/config", "/assets/..%5csecret", "/data/%00file"):
            self.assertIsNone(server.resolve_public(root, package, path))


if __name__ == "__main__":
    unittest.main()
