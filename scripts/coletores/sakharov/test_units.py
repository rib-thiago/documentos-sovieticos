"""Testa fronteiras documentais e notas sem rede."""
import unittest
from appendices import split_appendices
from prepare_units import definitions


class Boundaries(unittest.TestCase):
    def source(self, omitted=None):
        sections=[]
        for n in range(1,12):
            if n==omitted: continue
            sections.append(f'<p><strong>{n}</strong></p><p>TITLE {n}</p><p>'+f'Text of document {n}; '*20+'</p>')
        sections.append('<p>От авторов сайта спасибо helper</p>')
        return ('<div class="com-content-article__body">'+''.join(sections)+'</div>').encode()

    def test_eleven_numbered_boundaries_preserve_separation(self):
        docs=list(split_appendices(self.source(),'https://example.org/book'))
        self.assertEqual([d['number'] for d in docs],list(range(1,12)))
        self.assertIn('TITLE 11',docs[-1]['markdown_text'])
        self.assertNotIn('TITLE 11',docs[-2]['markdown_text'])
        self.assertNotIn('От авторов сайта',docs[-1]['markdown_text'])
        self.assertIn('От авторов сайта',docs[-1]['excluded_source_footer_html'])

    def test_missing_boundary_refuses_split(self):
        with self.assertRaises(ValueError):
            list(split_appendices(self.source(omitted=5),'https://example.org/book'))

    def test_inline_label_in_explicit_notes_section_is_definition(self):
        self.assertEqual(definitions('Body [749].\n\n**Notes:**\n\n[748] Bibliography. [749]\nAnother reference.'),{'748','749'})


if __name__=='__main__':unittest.main()
