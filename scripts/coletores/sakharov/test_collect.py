"""Verificações offline de preservação; não acessam rede nem catálogo."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from collect import Collector
from extraction import clean_article, soup_from

HTML = ('<html><body><article><h1>Sample</h1><p>' + 'A substantive source paragraph. ' * 20 + '</p></article></body></html>').encode()
URL = 'https://example.org/chapter'


class Preservation(unittest.TestCase):
    def make(self, root, raw=HTML):
        c = Collector(root)
        def fetch(url):
            sha = hashlib.sha256(raw).hexdigest()
            target = root / 'raw' / (sha + '.html')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            return raw, {'source_url': url, 'raw': str(target.relative_to(root)), 'raw_sha256': sha}
        c.fetch = fetch
        return c

    def test_short_chapter_heading_does_not_select_navigation(self):
        source = ('<html><body><div class="item-page"><h1>Site menu</h1>'
                  '<p>' + 'Unrelated navigation ' * 30 + '</p>'
                  '<div class="com-content-article__body"><h3>ГЛАВА 3. ПРОБЛЕМЫ УСТАНОВЛЕНИЯ АВТОРСТВА</h3></div>'
                  '</div></body></html>').encode()
        text = clean_article(soup_from(source), URL)
        self.assertIn('ГЛАВА 3.', text)
        self.assertNotIn('Unrelated navigation', text)
        self.assertNotIn('Site menu', text)

    def test_manual_candidate_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            c = self.make(root)
            c.collect(URL, 'en', title='Sample')
            candidate = root / c.inventory['items'][URL]['candidate']
            candidate.write_text('Editorial correction\n')
            c.collect(URL, 'en', title='Sample')
            self.assertEqual(candidate.read_text(), 'Editorial correction\n')
            self.assertTrue(c.inventory['items'][URL]['candidate_locally_modified'])

    def test_failure_does_not_drop_previous_success(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            c = self.make(root)
            c.collect(URL, 'en', title='Sample')
            old = c.inventory['items'][URL].copy()
            c = Collector(root)
            def fail(url):
                raise OSError('Connection failed')
            c.fetch = fail
            c.collect(URL, 'en')
            state = json.loads((root / 'inventory.json').read_text())
            self.assertEqual(state['items'][URL], old)
            self.assertEqual(state['attempts'][-1]['status'], 'error')

    def test_new_source_preserves_old_version(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            c = self.make(root)
            c.collect(URL, 'en', title='Sample')
            first = c.inventory['items'][URL]
            c = self.make(root, HTML.replace(b'Sample', b'Changed'))
            c.collect(URL, 'en', title='Changed')
            current = c.inventory['items'][URL]
            self.assertEqual(current['versions'][0]['raw_sha256'], first['raw_sha256'])
            self.assertTrue((root / first['candidate']).exists())
            self.assertTrue((root / first['raw']).exists())


if __name__ == '__main__':
    unittest.main()
