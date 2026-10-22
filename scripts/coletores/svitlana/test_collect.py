"""Verificações offline do contrato de segurança e conversão."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import json

from build_units import build

spec = importlib.util.spec_from_file_location('svitlana_collect', Path(__file__).with_name('collect.py'))
collect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect)


class CollectorContract(unittest.TestCase):
    def test_document_boundaries_and_approval_invalidation(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            source = out / 'source.md'
            body = 'First document\n\nNote for first\n\n***\n\nSecond document\n\nNote for second\n'
            source.write_text(body)
            latest = {'markdown': 'source.md', 'raw': 'raw.html', 'resolved_url': 'https://example.org/doc.htm',
                'language': 'en', 'original_language': 'ru', 'sha256': 'rawhash',
                'markdown_sha256': collect.digest(body), 'at': '2026-10-20', 'warnings': []}
            inv = {'sources': {}, 'candidates': {'one': {'url': latest['resolved_url'],
                'occurrences': [{'source_id': 'VOL-01'}], 'latest_success': latest}}}
            decisions = {'one': {'expected_markdown_sha256': collect.digest(body), 'separator': '\n\n***\n\n',
                'units': [{'suffix': str(n), 'title_literal': title, 'ready_for_import': True,
                           'reason': 'Checked boundary', 'range': n} for n, title in enumerate(['First document', 'Second document'])]}}
            collect.write_json(out / 'inventory.json', inv)
            rules = out / 'decisions.json'
            collect.write_json(rules, decisions)
            units = build(out, rules)['units']
            self.assertEqual(len(units), 2)
            self.assertTrue(all(u['ready_for_import'] for u in units))
            self.assertNotIn('Note for second', (out / units[0]['markdown']).read_text())
            self.assertIn('Note for second', (out / units[1]['markdown']).read_text())
            source.write_text(body + 'Changed source\n')
            latest['markdown_sha256'] = collect.digest(source.read_text())
            collect.write_json(out / 'inventory.json', inv)
            units = build(out, rules)['units']
            self.assertEqual(len(units), 1)
            self.assertFalse(units[0]['ready_for_import'])

    def test_structure_links_and_table(self):
        blob = b'''<html><body><nav>MENU</nav><h2>Heading</h2><p>Text <a href="../note.htm#n">note</a></p>
        <table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>
        <a name="note1"></a><p>Footnote</p></body></html>'''
        md, _, _, _ = collect.convert(blob, 'text/html', 'https://example.org/f/doc.htm')
        self.assertNotIn('MENU', md)
        self.assertIn('## Heading', md)
        self.assertIn('https://example.org/note.htm#n', md)
        self.assertIn('| A | B |', md)
        self.assertIn('<a id="note1"></a>', md)

    def test_failed_refresh_preserves_success_and_other_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            c = collect.Collector(Path(folder))
            c.fetch = lambda url: (b'<html><body><a href="doc.htm">Document</a></body></html>', url, 'text/html', 'abc', 'raw/abc.html')
            first = {'id': 'ONE', 'index_url': 'https://example.org/f/index.htm', 'title': 'First'}
            second = dict(first, id='TWO', title='Second')
            self.assertEqual(c.source(first)['status'], 'ok')
            c.source(second)
            self.assertEqual(len(c.inventory['candidates']), 1)
            self.assertEqual(len(next(iter(c.inventory['candidates'].values()))['occurrences']), 2)
            def fail(url):
                raise TimeoutError('offline')
            c.fetch = fail
            self.assertEqual(c.source(first)['status'], 'error')
            reopened = collect.Collector(Path(folder))
            self.assertEqual(reopened.inventory['sources']['ONE']['latest_success']['status'], 'ok')
            self.assertIn('TWO', reopened.inventory['sources'])
            self.assertEqual(len(reopened.inventory['candidates']), 1)

    def test_snapshots_do_not_overwrite_existing_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'raw.html'
            collect.immutable(path, b'first')
            with self.assertRaises(ValueError):
                collect.immutable(path, b'second')
            self.assertEqual(path.read_bytes(), b'first')

    def test_word_container_excludes_site_masthead_and_footer(self):
        blob = b'''<html><body><blockquote><b>WRONG VOLUME</b><div class="WordSection1">
        <p>Historical text</p><div style="border-top:1px">Non-profit digital library</div></div></blockquote></body></html>'''
        md, _, _, warnings = collect.convert(blob, 'text/html', 'https://example.org/doc.htm')
        self.assertEqual(md, 'Historical text\n')
        self.assertTrue(any('word_container' in x for x in warnings))


if __name__ == '__main__':
    unittest.main()
