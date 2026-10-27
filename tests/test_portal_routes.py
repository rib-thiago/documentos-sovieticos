"""Public resources are readable without granting local editorial capabilities."""
import unittest
from tests import test_studio_routes as fixtures


class PublicPortalRoutes(unittest.TestCase):
    def test_public_reading_modules_do_not_require_editorial_access(self):
        for path in ['/assets/portal-ui.js', '/assets/modules/portal-study.js',
                     '/assets/modules/reading-surface.js', '/assets/modules/reader-deps.js',
                     '/assets/modules/print-edition.js', '/assets/modules/viewer-fullscreen.js', '/assets/css/portal-study.css',
                     '/assets/css/portal-reader.css', '/assets/css/document-viewers.css', '/prototipo/oficina/book-frame.html',
                     '/prototipo/oficina/book-frame.js']:
            with self.subTest(path=path):
                response, _ = fixtures.StudioRoutes().handler(path, peer='203.0.113.2')
                self.assertEqual(response.status, 200)

    def test_public_entry_does_not_load_editorial_controllers(self):
        response, _ = fixtures.StudioRoutes().handler('/', peer='203.0.113.2')
        self.assertEqual(response.status, 200)
        html = response.wfile.getvalue()
        self.assertIn(b'assets/portal-ui.js', html)
        for script in [b'assets/workbench.js', b'assets/pdf-review.js',
                       b'assets/project-editor.js', b'host-boot.js']:
            self.assertNotIn(script, html)

    def test_private_data_still_not_served(self):
        for path in ['/temporario/zinoviev/test.pdf', '/.local/research/sources/test.pdf']:
            with self.subTest(path=path):
                response, _ = fixtures.StudioRoutes().handler(path, peer='203.0.113.2')
                self.assertEqual(response.status, 404)
