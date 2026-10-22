import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('mozokhin_adapter', Path(__file__).parents[1] / 'adapter.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class Boundaries(unittest.TestCase):
    def test_missing_number_does_not_swallow_following(self):
        result = adapter.segment('№1\nПервый текст\n№3\nТретий текст\n№4\nЧетвертый', 1, 4)
        self.assertEqual([x['number'] for x in result['sections']], [1, 3, 4])
        self.assertEqual(result['missing'], [2])
        self.assertNotIn('Третий', result['sections'][0]['text'])
        self.assertEqual(result['sections'][0]['status'], 'blocked_boundary')

    def test_inline_numbers_not_headings(self):
        text = 'No1\nПисьмо\nNo 108 от 27.2.29 г.\nNo 30411\nNo2\nОтвет\nСодержание\nNo1. Индекс'
        result = adapter.segment(text, 1, 2, source_complete=True)
        self.assertEqual([x['number'] for x in result['sections']], [1, 2])
        self.assertEqual(result['sections'][1]['status'], 'candidate_unreviewed')
        self.assertNotIn('Индекс', result['sections'][1]['text'])

    def test_last_excerpt_is_blocked(self):
        result = adapter.segment('№215\nЗаписка\nТекст', 215, 215)
        self.assertEqual(result['sections'][0]['status'], 'blocked_boundary')

    def test_formfeed_header_and_commentary_end(self):
        text = '\f № 294\nСообщение\nТекст\n\f №295\nСтатья\nКонец\n\f ИМЕННОЙ КОММЕНТАРИЙ16\nБиография'
        result = adapter.segment(text, 294, 295, source_complete=True)
        self.assertEqual([x['number'] for x in result['sections']], [294, 295])
        self.assertNotIn('Биография', result['sections'][-1]['text'])
        self.assertEqual(result['sections'][-1]['status'], 'candidate_unreviewed')

    def test_contents_disambiguates_internal_number(self):
        text = '№1\nПервое письмо адресату\n№2\n1. Вложенный пункт\n№2\nВторое письмо адресату\n' + 'Текст документа.\n' * 20 + '\f Оглавление\n№ 1. Первое письмо адресату....... 3\n№ 2. Второе письмо адресату....... 5'
        titles = adapter.printed_contents(text, 1, 2)
        self.assertEqual(len(titles), 2)
        result = adapter.segment(text, 1, 2, source_complete=True, titles=titles)
        self.assertEqual(len(result['sections']), 2)
        self.assertEqual(len(result['rejected_internal_headers']), 1)
        self.assertIn('Вложенный пункт', result['sections'][0]['text'])

    def test_ambiguous_title_correspondence_stays_blocked(self):
        result = adapter.segment('№1\nПервый\n№2\nДругой\nСодержание', 1, 2,
                                 source_complete=True, titles={1: 'Первый', 2: 'Несовпадающий'})
        self.assertEqual(result['sections'][1]['status'], 'blocked_boundary')

    def test_duplicates_are_not_overwritten(self):
        result = adapter.segment('№1\nА\n№2\nБ\n№1\nВ', 1, 2)
        self.assertEqual(len(result['sections']), 3)
        self.assertTrue(all(x['status'] == 'blocked_boundary' for x in result['sections']))

    def test_challenge_is_not_a_book(self):
        with self.assertRaises(ValueError):
            adapter.extract_reader('<html><script>challenge</script><button>Verify</button></html>')

    def test_cumulative_inventory_and_immutable_versions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'source.txt'
            output = root / 'staging'
            source.write_text('№1\nПервое письмо\nТело')
            first = adapter.stage(source, output, 'https://example.org/book', 1, 1)
            original = Path(first['documents'][0]['markdown_path'])
            old_text = original.read_text()
            source.write_text('№2\nВторое письмо\nТело')
            adapter.stage(source, output, 'https://example.org/book', 2, 2)
            inventory = adapter.json.loads((output / 'inventory.json').read_text())
            self.assertEqual(len(inventory['items']), 2)
            self.assertEqual(original.read_text(), old_text)

    def test_web_excerpts_never_ready_for_incorporation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'source.txt'
            source.write_text('№1\nПервое письмо\nТело\n№2\nВторое письмо\nТело')
            run = adapter.stage(source, root / 'staging', 'https://example.org/book', 1, 2, kind='web_excerpt')
            self.assertTrue(all(x['status'] == 'blocked_partial_acquisition' for x in run['documents']))
            self.assertTrue(all(not x['fulltext_acquired'] for x in run['documents']))


if __name__ == '__main__':
    unittest.main()
