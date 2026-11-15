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
                self.assertEqual(h.response_headers['Location'], '/?ambiente=local')

    def test_canonical_entry_serves_new_interface(self):
        h, _ = self.handler('/estudio/')
        self.assertEqual(h.status, 302)
        self.assertEqual(h.response_headers['Location'], '/?ambiente=local')
        root, _ = self.handler('/')
        self.assertEqual(root.status, 200)
        self.assertIn(b'prototipo/mesa/app.js', root.wfile.getvalue())
        self.assertNotIn(b'assets/studio-entry.js', root.wfile.getvalue())

    def test_entry_redirect_keeps_editorial_query_context(self):
        for path in ['/editorial?documento=showtrials-1665', '/estudio/?documento=showtrials-1665']:
            h, _ = self.handler(path)
            self.assertEqual(h.response_headers['Location'], '/?ambiente=local&documento=showtrials-1665')

    def test_new_official_root_assets_and_compatibility_entry(self):
        from html.parser import HTMLParser
        from urllib.parse import urlsplit
        class Assets(HTMLParser):
            paths=[]
            def handle_starttag(self,tag,attrs):
                values=dict(attrs)
                for field in ['src','href']:
                    value=values.get(field,'')
                    if value and not value.startswith('#'):
                        self.paths.append(urlsplit(value).path)
        parser=Assets();parser.feed((ROOT/'index.html').read_text())
        for path in parser.paths:
            with self.subTest(path=path):
                h,_=self.handler('/'+path)
                self.assertEqual(h.status,200)
        h,_=self.handler('/prototipo/mesa/')
        self.assertIn(b'location.replace',h.wfile.getvalue())
        h,_=self.handler('/prototipo/mesa/entry.js')
        self.assertEqual(h.status,200)

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
