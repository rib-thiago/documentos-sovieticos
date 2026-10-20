"""Revisão e OCR em fontes e bancos temporários; não altera o acervo real."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from backend.pdf_sources import PDFSources
from backend.pdf_review import ocr_capabilities
from backend.editorial import EditorialError
try:
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
except ImportError:
    PdfWriter = None


@unittest.skipUnless(PdfWriter, 'Requer pypdf opcional')
class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='pdf-review-test-')
        self.root = Path(self.directory.name)
        self.sources = PDFSources(self.root, start_worker=False)
        writer = PdfWriter()
        page = writer.add_blank_page(width=595, height=842)
        font = DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')})
        page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
        content = DecodedStreamObject(); content.set_data(b'BT /F1 20 Tf 72 700 Td (Historical research document.) Tj 0 -40 Td (Preserve the original source.) Tj ET')
        page[NameObject('/Contents')] = writer._add_object(content)
        buffer = io.BytesIO(); writer.write(buffer); writer.close()
        self.raw = buffer.getvalue()
        self.id = self.sources.upload('fonte.pdf', self.raw)['source_id']
        subprocess.run([sys.executable, '-B', '-m', 'backend.pdf_worker', str(self.root), self.id], check=True)
        self.review = self.sources.review

    def tearDown(self):
        self.sources.close(); self.directory.cleanup()

    def payload(self, value='Texto corrigido.\n\nSegundo trecho.', **changes):
        page = self.review.page(self.id, 1)
        data = {key: page['review'][key] for key in ('text', 'status', 'printed_label', 'notes', 'basis')}
        data.update(text=value, status='reviewed', **changes)
        return {'source_id': self.id, 'page_number': 1, 'revision': page['revision'], 'review': data}

    def save(self, payload):
        preview = self.review.preview(payload)
        return self.review.save({'preview_id': preview['preview_id']})

    def test_preview_does_not_save_and_save_preserves_raw(self):
        raw = self.sources.page(self.id, 1)
        preview = self.review.preview(self.payload())
        self.assertEqual(self.review.page(self.id, 1)['revision'], 0)
        self.assertIn('Texto corrigido', preview['diff'])
        saved = self.review.save({'preview_id': preview['preview_id']})
        self.assertEqual(saved['revision'], 1)
        self.assertEqual(saved['review']['status'], 'reviewed')
        self.assertEqual(self.sources.page(self.id, 1), raw)
        self.assertEqual(self.sources.file_path(self.id).read_bytes(), self.raw)

    def test_history_restores_as_new_revision(self):
        first = self.save(self.payload('Primeira revisão'))
        self.save(self.payload('Segunda revisão'))
        preview = self.review.preview({'source_id': self.id, 'page_number': 1, 'revision': 2, 'history_id': first['history'][0]['id']})
        result = self.review.save({'preview_id': preview['preview_id']})
        self.assertEqual(result['revision'], 3)
        self.assertEqual(result['review']['text'], result['raw']['raw_text'])
        self.assertEqual(len(result['history']), 3)

    def test_stale_and_consumed_previews_rejected(self):
        payload = self.payload()
        a, b = self.review.preview(payload), self.review.preview(payload)
        self.review.save({'preview_id': a['preview_id']})
        for candidate in (a, b):
            with self.assertRaises(EditorialError):
                self.review.save({'preview_id': candidate['preview_id']})
        with self.assertRaises(EditorialError):
            self.review.preview(payload)

    def test_stable_units_preserved_on_edit_and_reorder(self):
        first = self.save(self.payload())
        second = self.save(self.payload('Segundo trecho.\n\nTexto corrigido.\n\nNovo.'))
        self.assertEqual(second['review']['units'][0]['id'], first['review']['units'][1]['id'])
        self.assertEqual(second['review']['units'][1]['id'], first['review']['units'][0]['id'])
        self.assertNotIn(second['review']['units'][2]['id'], [u['id'] for u in first['review']['units']])

    def test_native_unit_identity_is_retained(self):
        page = self.review.page(self.id, 1)
        result = self.save(self.payload(page['review']['text']))
        self.assertEqual(result['review']['units'][0]['id'], page['raw']['paragraphs'][0]['id'])

    def test_invalid_status_blank_text_and_ocr_identity(self):
        for change in ({'status': 'wrong'}, {'status': 'blank'}, {'basis': 'ocrpage-missing'}):
            payload = self.payload(); payload['review'].update(change)
            with self.assertRaises(EditorialError):
                self.review.preview(payload)
        payload = self.payload(''); payload['review']['status'] = 'blank'
        self.assertEqual(self.save(payload)['review']['status'], 'blank')

    def test_missing_ocr_dependency_is_clear(self):
        with patch('backend.pdf_review.ocr_capabilities', return_value={'available': False, 'languages': []}):
            with self.assertRaises(EditorialError) as error:
                self.review.ocr_preview({'source_id': self.id, 'languages': ['rus'], 'pages': '1', 'dpi': 300, 'psm': 3})
        self.assertEqual(error.exception.status, 409)

    def ocr(self):
        cap = ocr_capabilities()
        if not cap['available'] or 'eng' not in cap['languages']:
            self.skipTest('Poppler, Tesseract e modelo inglês opcionais não instalados')
        result = self.review.ocr_preview({'source_id': self.id, 'languages': ['eng'], 'pages': '1', 'dpi': 150, 'psm': 3})
        self.assertEqual(self.review.overview(self.id)['jobs'], [])
        job_id = self.review.ocr_start({'preview_id': result['preview_id']})['job_id']
        self.sources._run_ocr(job_id)
        return job_id

    def test_real_ocr_preserves_corrections_and_resumes_without_duplicate(self):
        self.save(self.payload())
        before = self.review.page(self.id, 1)
        job_id = self.ocr()
        result = self.review.page(self.id, 1)
        self.assertEqual(result['review'], before['review'])
        self.assertEqual(result['raw'], before['raw'])
        self.assertEqual(len(result['candidates']), 1)
        self.assertIn('Historical', result['candidates'][0]['raw_text'])
        self.assertEqual(self.review.overview(self.id)['jobs'][0]['state'], 'completed')
        with self.sources.db() as db:
            self.assertIn('left\ttop\twidth', db.execute('SELECT geometry FROM pdf_ocr_candidates').fetchone()[0])
            db.execute("UPDATE pdf_ocr_jobs SET state='interrupted' WHERE id=?", (job_id,))
        self.review.ocr_resume({'job_id': job_id}); self.sources._run_ocr(job_id)
        self.assertEqual(len(self.review.page(self.id, 1)['candidates']), 1)
        self.assertEqual(self.sources.file_path(self.id).read_bytes(), self.raw)

    def test_ocr_hash_mismatch_is_blocked(self):
        cap = ocr_capabilities()
        if not cap['available']:
            self.skipTest('OCR opcional ausente')
        preview = self.review.ocr_preview({'source_id': self.id, 'languages': [cap['languages'][0]], 'pages': '1', 'dpi': 150, 'psm': 3})
        job_id = self.review.ocr_start({'preview_id': preview['preview_id']})['job_id']
        self.sources.file_path(self.id).write_bytes(b'%PDF-corrupted')
        self.sources._run_ocr(job_id)
        job = self.review.overview(self.id)['jobs'][0]
        self.assertEqual(job['state'], 'failed')
        self.assertIn('difere', job['error'])
        self.assertEqual(job['completed_pages'], [])

    def test_restart_keeps_reviews_and_marks_running_ocr_interrupted(self):
        self.save(self.payload())
        with self.sources.db() as db:
            db.execute('INSERT INTO pdf_ocr_jobs VALUES(?,?,?,?,?,?,?,?)', ('ocr-'+'f'*32, self.id, hashlib.sha256(self.raw).hexdigest(), '{}', 'running', '2026', '2026', None))
        reopened = PDFSources(self.root, start_worker=False)
        self.assertEqual(reopened.review.page(self.id, 1)['revision'], 1)
        self.assertEqual(reopened.review.overview(self.id)['jobs'][0]['state'], 'interrupted')
        reopened.close()
