"""Integração de derivados PDF em bancos temporários; não usa o acervo real."""
import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    PdfReader = PdfWriter = None

from backend.pdf_sources import PDFSources
from backend.pdf_operations import page_selection
from backend.research_projects import ResearchProjects
from backend.editorial import EditorialError
from backend import catalog as model


class SelectionTests(unittest.TestCase):
    def test_selection_preserves_explicit_order(self):
        self.assertEqual(page_selection('6, 1-3', 6), [6, 1, 2, 3])

    def test_invalid_duplicate_and_out_of_range_pages_are_rejected(self):
        for value in ('', '1,1', '1-3,3', '0', '2-1', '7', '1;', '1-99'):
            with self.subTest(value=value), self.assertRaises(EditorialError):
                page_selection(value, 6)

    def test_upload_configuration_must_be_explicit_valid_number(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {'SHOWTRIALS_PDF_MAX_MIB': 'abc'}):
            with self.assertRaises(model.CatalogError):
                PDFSources(root, start_worker=False)


@unittest.skipUnless(PdfWriter, 'Instale backend/requirements-pdf.txt para conferir geração de PDFs')
class PDFOperationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='pdf-operations-test-')
        self.root = Path(self.directory.name)
        self.sources = PDFSources(self.root, start_worker=False)
        self.projects = ResearchProjects(self.root, self.sources)
        self.sources.operations.projects = self.projects
        writer = PdfWriter()
        for number in range(1, 7):
            writer.add_blank_page(width=100 + number, height=200)
        buffer = io.BytesIO()
        writer.write(buffer)
        writer.close()
        self.raw = buffer.getvalue()
        self.source_id = self.sources.upload('fonte.pdf', self.raw)['source_id']
        with self.sources.db() as db:
            db.execute('UPDATE pdf_sources SET page_count=6 WHERE id=?', (self.source_id,))
        self.catalog = {'documents': [], 'collections': []}

    def tearDown(self):
        self.sources.close()
        self.directory.cleanup()

    def plan(self, **changes):
        payload = {'source_id': self.source_id, 'project_id': '', 'mode': 'extract', 'pages': '6,1-3',
                   'split_mode': 'size', 'pages_per_part': 2, 'ranges': ''}
        payload.update(changes)
        return self.sources.operations.preview(payload)

    def run_operation(self, **changes):
        preview = self.plan(**changes)
        job = self.sources.operations.enqueue({'preview_id': preview['preview_id']})
        self.sources._run_operation(job['id'])
        return self.sources.operations.get(job['id'])

    def test_preview_creates_no_derivative_or_job(self):
        preview = self.plan()
        self.assertEqual(preview['outputs'][0]['pages'], [6, 1, 2, 3])
        self.assertEqual(len(self.sources.listing()['items']), 1)
        self.assertEqual(self.sources.operations.listing({})['items'], [])

    def test_extract_preserves_original_order_and_page_provenance(self):
        job = self.run_operation()
        self.assertEqual(job['state'], 'completed', job)
        self.assertEqual(self.sources.file_path(self.source_id).read_bytes(), self.raw)
        result = job['outputs'][0]
        reader = PdfReader(self.sources.file_path(result['result_source_id']))
        self.assertEqual([int(p.mediabox.width) for p in reader.pages], [106, 101, 102, 103])
        provenance = self.sources.source(result['result_source_id'])['provenance'][0]
        self.assertEqual(provenance['parent_source_id'], self.source_id)
        self.assertEqual(provenance['pages'], [6, 1, 2, 3])
        self.assertEqual(provenance['source_sha256'], hashlib.sha256(self.raw).hexdigest())

    def test_split_by_size_generates_remainder_part(self):
        job = self.run_operation(mode='split', pages_per_part=4)
        self.assertEqual(job['state'], 'completed', job)
        self.assertEqual([p['pages'] for p in job['outputs']], [[1, 2, 3, 4], [5, 6]])
        for output in job['outputs']:
            self.assertEqual(len(PdfReader(self.sources.file_path(output['result_source_id'])).pages), len(output['pages']))

    def test_custom_ranges_report_omitted_pages(self):
        preview = self.plan(mode='split', split_mode='ranges', ranges='1-2;5-6')
        self.assertEqual(preview['recipe']['omitted_pages'], 2)
        self.assertEqual([p['pages'] for p in preview['outputs']], [[1, 2], [5, 6]])
        with self.assertRaises(EditorialError):
            self.plan(mode='split', split_mode='ranges', ranges='1-3;3-4')

    def test_stale_preview_and_double_confirmation_are_rejected(self):
        preview = self.plan()
        with self.sources.db() as db:
            db.execute('UPDATE pdf_sources SET revision=revision+1 WHERE id=?', (self.source_id,))
        with self.assertRaises(EditorialError):
            self.sources.operations.enqueue({'preview_id': preview['preview_id']})
        preview = self.plan()
        self.sources.operations.enqueue({'preview_id': preview['preview_id']})
        with self.assertRaises(EditorialError):
            self.sources.operations.enqueue({'preview_id': preview['preview_id']})

    def test_project_receives_results_in_one_recoverable_change(self):
        before = self.projects.preview({'project': {'title': 'Projeto', 'description': '', 'collection_id': '', 'document_ids': [], 'source_ids': [self.source_id], 'archived': False}}, self.catalog)
        project_id = self.projects.save({'preview_id': before['preview_id']}, self.catalog)['project_id']
        job = self.run_operation(mode='split', pages_per_part=2, project_id=project_id)
        self.assertEqual(job['state'], 'completed', job)
        project = self.projects.get(project_id)
        self.assertEqual(len(project['source_ids']), 4)
        self.assertEqual(len(self.projects.history(project_id)['items']), 2)
        history = self.projects.history(project_id)['items'][0]
        proposal = self.projects.preview({'project_id': project_id, 'revision': project['revision'], 'history_id': history['id']}, self.catalog)
        self.projects.save({'preview_id': proposal['preview_id']}, self.catalog)
        self.assertEqual(self.projects.get(project_id)['source_ids'], [self.source_id])
        self.assertTrue(all(self.sources.file_path(out['result_source_id']).is_file() for out in job['outputs']))

    def test_partial_registration_failure_resumes_without_duplicate_results(self):
        preview = self.plan(mode='split', pages_per_part=2)
        job = self.sources.operations.enqueue({'preview_id': preview['preview_id']})
        original = self.sources.upload_stream
        calls = 0
        def interrupted(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('interrupção simulada')
            return original(*args, **kwargs)
        with patch.object(self.sources, 'upload_stream', side_effect=interrupted):
            self.sources._run_operation(job['id'])
        partial = self.sources.operations.get(job['id'])
        self.assertEqual(partial['state'], 'failed')
        self.assertEqual(partial['registered'], 1)
        first_id = partial['outputs'][0]['result_source_id']
        self.sources.operations.resume({'operation_id': job['id']})
        self.sources._run_operation(job['id'])
        complete = self.sources.operations.get(job['id'])
        self.assertEqual(complete['state'], 'completed', complete)
        self.assertEqual(complete['outputs'][0]['result_source_id'], first_id)
        self.assertEqual(len(self.sources.listing()['items']), 4)

    def test_changed_original_is_not_processed(self):
        preview = self.plan()
        job = self.sources.operations.enqueue({'preview_id': preview['preview_id']})
        self.sources.file_path(self.source_id).write_bytes(self.raw + b'changed')
        self.sources._run_operation(job['id'])
        result = self.sources.operations.get(job['id'])
        self.assertEqual(result['state'], 'failed')
        self.assertEqual(result['registered'], 0)
        self.assertIn('mudou', result['error'])

    def test_streaming_upload_is_bounded_and_rejects_truncation(self):
        class LimitedRead(io.BytesIO):
            def read(self, size=-1):
                if not 0 <= size <= 1024 * 1024:
                    raise AssertionError('Upload tentou ler o arquivo inteiro')
                return super().read(size)
        duplicate = self.sources.upload_stream('copia.pdf', LimitedRead(self.raw), len(self.raw))
        self.assertTrue(duplicate['duplicate'])
        with self.assertRaises(EditorialError):
            self.sources.upload_stream('truncado.pdf', io.BytesIO(self.raw), len(self.raw) + 10)
        self.assertFalse(list(self.sources.files.glob('.upload-*')))

    def test_shutdown_does_not_publish_partial_upload(self):
        self.sources.stopping.set()
        with self.assertRaises(EditorialError):
            self.sources.upload_stream('interrompido.pdf', io.BytesIO(self.raw), len(self.raw))
        self.assertFalse(list(self.sources.files.glob('.upload-*')))
        self.assertEqual(len(self.sources.listing()['items']), 1)
        self.assertEqual(self.sources.file_path(self.source_id).read_bytes(), self.raw)
