"""Estúdio oficial: rotas e recursos, sem servidor, workers ou banco do acervo."""
import io
import unittest
from pathlib import Path
from types import SimpleNamespace

from backend.server import handler_for

ROOT = Path(__file__).resolve().parents[1]


class StudioRoutes(unittest.TestCase):
    def handler(self, path, peer='127.0.0.1'):
        listing_calls = []
        def listing(**kwargs):
            listing_calls.append(kwargs)
            return {'items': []}
        repository = SimpleNamespace(root=ROOT)
        editorial = SimpleNamespace(pdf_sources=SimpleNamespace(listing=listing))
        handler = object.__new__(handler_for(repository, editorial))
        handler.path, handler.command = path, 'GET'
        handler.headers = {'Host': '127.0.0.1:8000'}
        handler.client_address = (peer, 12345)
        handler.server = SimpleNamespace(server_address=('127.0.0.1', 8000), server_port=8000)
        handler.connection = SimpleNamespace(settimeout=lambda _: None)
        handler.wfile = io.BytesIO()
        handler.response_headers = {}
        handler.send_response = lambda status: setattr(handler, 'status', status)
        handler.send_header = lambda name, value: handler.response_headers.__setitem__(name, value)
        handler.end_headers = lambda: None
        handler.log_error = lambda *_: None
        handler.get_locked()
        return handler, listing_calls

    def test_editorial_enters_official_studio(self):
        for path in ['/editorial', '/editorial/', '/prototipo/oficina/']:
            with self.subTest(path=path):
                h, _ = self.handler(path)
                self.assertEqual(h.status, 302)
                self.assertEqual(h.response_headers['Location'], '/estudio/')

    def test_canonical_entry_serves_new_interface(self):
        h, _ = self.handler('/estudio/')
        self.assertEqual(h.status, 200)
        self.assertIn(b'Est\xc3\xbadio', h.wfile.getvalue())
        self.assertIn(b'doc-language', h.wfile.getvalue())

    def test_official_module_resources_are_allowed(self):
        for name in ['app.js', 'editorial-host.js', 'document-tools.js', 'study.js', 'visualizers.js', 'loaders.js']:
            with self.subTest(name=name):
                h, _ = self.handler('/estudio/' + name)
                self.assertEqual(h.status, 200)

    def test_unpublished_paths_remain_unavailable(self):
        for path in ['/estudio/../../.local/research/jobs.sqlite3', '/estudio/package-lock.json', '/temporario/teste.pdf']:
            with self.subTest(path=path):
                h, _ = self.handler(path)
                self.assertEqual(h.status, 404)

    def test_canonical_studio_requires_local_client(self):
        h, _ = self.handler('/estudio/', peer='203.0.113.2')
        self.assertEqual(h.status, 403)

    def test_source_listing_can_omit_engine_detection(self):
        h, calls = self.handler('/api/editorial/pdf/sources?light=1')
        self.assertEqual(h.status, 200)
        self.assertEqual(calls, [{'include_capabilities': False}])


if __name__ == '__main__':
    unittest.main()
