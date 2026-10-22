import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))
from prepare_books import footer_markers, shared_page_note_risks


class Notes(unittest.TestCase):
    def test_small_footer_label_detected_but_page_number_ignored(self):
        xml = '''<doc><page width="595" height="842"><word xMin="88" yMin="755" yMax="763.1">13</word><word xMin="287" yMin="784" yMax="793">387</word><word xMin="88" yMin="350" yMax="359.9">14</word></page></doc>'''
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'bbox.xml'
            path.write_text(xml)
            markers = footer_markers(path)
        self.assertEqual([m['number_literal'] for m in markers[1]], ['13'])

    def test_shared_page_note_blocks_both_documents(self):
        text = '№294\nТекст13\n№295\nДругой14\n13 Старая сноска\n14 Новая сноска'
        split = text.index('№295')
        sections = [{'number': 294, 'start': 0, 'end': split},
                    {'number': 295, 'start': split, 'end': len(text)}]
        risks, pages = shared_page_note_risks(text, sections, {1: [{'number_literal': '13'}]})
        self.assertEqual(set(risks), {294, 295})
        self.assertEqual(pages[294], (1, 1))


if __name__ == '__main__':
    unittest.main()
