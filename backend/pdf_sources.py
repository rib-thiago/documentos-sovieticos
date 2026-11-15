"""Fontes PDF locais e candidatas; não modifica catálogo nem edições públicas."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import re
import secrets
import signal
import sqlite3
import subprocess
import sys
import threading
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from . import catalog as model
from .editorial import EditorialError, text

MAX_PDF_BYTES = 256 * 1024 * 1024
MAX_PAGES = 1500


def now():
    return datetime.now(timezone.utc).isoformat()


class PDFSources:
    def __init__(self, root, *, start_worker=True):
        self.root = Path(root).resolve()
        try:
            limit = int(os.environ.get('SHOWTRIALS_PDF_MAX_MIB', str(MAX_PDF_BYTES // (1024 * 1024))))
            if not 1 <= limit <= 2048:
                raise ValueError
        except ValueError as error:
            raise model.CatalogError('SHOWTRIALS_PDF_MAX_MIB deve ser um número inteiro entre 1 e 2048') from error
        self.max_bytes = limit * 1024 * 1024
        self.directory = self.root / '.local/research'
        self.directory.mkdir(parents=True, exist_ok=True)
        self.files = self.directory / 'sources'
        self.files.mkdir(exist_ok=True)
        self.path = self.directory / 'jobs.sqlite3'
        self.lock = threading.RLock()
        self.stopping = threading.Event()
        self.wakeup = threading.Event()
        self.process = None
        with self.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS pdf_sources (
                    id TEXT PRIMARY KEY, sha256 TEXT NOT NULL UNIQUE,
                    filename TEXT NOT NULL, bytes INTEGER NOT NULL, created_at TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}', confirmed INTEGER NOT NULL DEFAULT 0,
                    revision INTEGER NOT NULL DEFAULT 0, page_count INTEGER,
                    state TEXT NOT NULL, error TEXT, last_page INTEGER NOT NULL DEFAULT 1);
                CREATE TABLE IF NOT EXISTS pdf_jobs (
                    id TEXT PRIMARY KEY, source_id TEXT NOT NULL UNIQUE, state TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, engine TEXT, error TEXT);
                CREATE TABLE IF NOT EXISTS pdf_pages (
                    id TEXT PRIMARY KEY, source_id TEXT NOT NULL, page_number INTEGER NOT NULL,
                    printed_label TEXT, raw_text TEXT NOT NULL, text_sha256 TEXT NOT NULL,
                    diagnosis TEXT NOT NULL, reason TEXT NOT NULL, error TEXT,
                    paragraphs TEXT NOT NULL, engine TEXT NOT NULL, UNIQUE(source_id,page_number));
                CREATE TABLE IF NOT EXISTS pdf_history (
                    id TEXT PRIMARY KEY, source_id TEXT NOT NULL, created_at TEXT NOT NULL,
                    before_state TEXT NOT NULL, after_state TEXT NOT NULL);
            ''')
            db.execute("UPDATE pdf_jobs SET state='interrupted', updated_at=? WHERE state='running'", (now(),))
            db.execute("UPDATE pdf_sources SET state='interrupted' WHERE state='running'")
        from .pdf_operations import PDFOperations
        self.operations = PDFOperations(self)
        from .pdf_review import PDFReview
        self.review = PDFReview(self)
        from .pdf_links import PDFLinks
        self.links = PDFLinks(self)
        from .pdf_alignment import PDFAlignment
        self.alignment = PDFAlignment(self)
        self.worker = None
        if start_worker:
            self.start()

    def start(self):
        if self.worker is None:
            self.worker = threading.Thread(target=self._loop, name='pdf-source-worker', daemon=True)
            self.worker.start()

    @contextmanager
    def db(self):
        connection = sqlite3.connect(self.path, timeout=20)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA journal_mode=WAL')
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def capabilities(self):
        from .pdf_preparation import image_capabilities
        return {'image':image_capabilities(),'extraction': importlib.util.find_spec('pypdf') is not None,
                'installation': 'python3 -m pip install -r backend/requirements-pdf.txt',
                'ocr': self.ocr_capabilities(), 'planned_ocr_languages': ['rus', 'eng', 'por'],
                'max_bytes': self.max_bytes, 'max_pages': MAX_PAGES, 'pdf_operations': ['extract', 'split'], 'max_outputs': 200}

    def ocr_capabilities(self):
        from .pdf_review import ocr_capabilities
        return ocr_capabilities()

    def page_image(self, source_id, number):
        import shutil
        source=self.source(source_id)
        if type(number) is not int or not source['page_count'] or not 1 <= number <= source['page_count']:
            raise EditorialError('Página inválida')
        if not shutil.which('pdftoppm'):
            raise EditorialError('Instale poppler-utils para visualizar a imagem de alinhamento',409)
        target=self.directory/'page-images'/(source['sha256']+'-'+str(number)+'.png')
        if not target.exists():
            process=subprocess.Popen([sys.executable,'-m','backend.pdf_image_worker',str(self.root),source_id,str(number)],cwd=Path(__file__).resolve().parents[1],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            try:
                process.wait(timeout=80)
            except subprocess.TimeoutExpired:
                self._stop_process(process,signal.SIGKILL);process.wait()
                raise EditorialError('A renderização excedeu o limite de tempo',409)
            finally:
                self._stop_process(process,signal.SIGKILL)
            if process.returncode or not target.exists():raise EditorialError('Não foi possível renderizar a página; confira a fonte e o Poppler',409)
        return target

    def require_engine(self):
        if importlib.util.find_spec('pypdf') is None:
            raise EditorialError('Extração PDF não instalada. Execute: python3 -m pip install -r backend/requirements-pdf.txt', 409)

    def file_path(self, source_id):
        if not re.fullmatch(r'pdf-[a-f0-9]{32}', source_id):
            raise EditorialError('Identificador de fonte inválido', 404)
        return self.files / (source_id + '.pdf')

    def upload(self, filename, data):
        return self.upload_stream(filename, io.BytesIO(data), len(data))

    def upload_stream(self, filename, stream, length, *, enforce_limit=True):
        self.require_engine()
        limit = self.max_bytes if enforce_limit else 2048 * 1024 * 1024
        if not 1 <= length <= limit:
            raise EditorialError(f'Envie um PDF válido de até {limit // (1024 * 1024)} MiB', 413)
        filename = text(filename, 250)
        if not filename.lower().endswith('.pdf') or '/' in filename or '\\' in filename or any(ord(c) < 32 for c in filename):
            raise EditorialError('Nome de arquivo PDF inválido')
        descriptor, temporary = tempfile.mkstemp(prefix='.upload-', dir=self.files)
        candidate = Path(temporary)
        try:
            digest, remaining = hashlib.sha256(), length
            with os.fdopen(descriptor, 'wb') as target:
                first = True
                while remaining:
                    if self.stopping.is_set():
                        raise EditorialError('Processamento interrompido. O original e os resultados concluídos foram preservados.', 409)
                    chunk = stream.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise EditorialError('Upload interrompido; envie novamente')
                    if first and not chunk.startswith(b'%PDF-'):
                        raise EditorialError('O arquivo não possui um cabeçalho PDF válido')
                    first = False
                    digest.update(chunk)
                    target.write(chunk)
                    remaining -= len(chunk)
            digest = digest.hexdigest()
            with self.lock, self.db() as db:
                existing = db.execute('SELECT id FROM pdf_sources WHERE sha256=?', (digest,)).fetchone()
                if existing:
                    return {'source_id': existing['id'], 'duplicate': True}
                source_id = 'pdf-' + secrets.token_hex(16)
                # Publica o arquivo completo sem carregar o PDF inteiro na memória do servidor.
                os.replace(candidate, self.file_path(source_id))
                db.execute('INSERT INTO pdf_sources(id,sha256,filename,bytes,created_at,state) VALUES(?,?,?,?,?,?)',
                           (source_id, digest, filename, length, now(), 'queued'))
                db.execute('INSERT INTO pdf_jobs(id,source_id,state,created_at,updated_at) VALUES(?,?,?,?,?)',
                           ('job-' + secrets.token_hex(16), source_id, 'queued', now(), now()))
        finally:
            candidate.unlink(missing_ok=True)
        self.wakeup.set()
        return {'source_id': source_id, 'duplicate': False}

    def source(self, source_id):
        self.file_path(source_id)
        with self.db() as db:
            row = db.execute('SELECT * FROM pdf_sources WHERE id=?', (source_id,)).fetchone()
            if not row:
                raise EditorialError('Fonte não encontrada', 404)
            result = dict(row)
            result['metadata'] = json.loads(result['metadata'])
            result['confirmed'] = bool(result['confirmed'])
            result['pages'] = [dict(r) for r in db.execute(
                'SELECT id,page_number,printed_label,diagnosis,reason,error FROM pdf_pages WHERE source_id=? ORDER BY page_number', (source_id,))]
            result['processed'] = len(result['pages'])
            result['job'] = dict(db.execute('SELECT * FROM pdf_jobs WHERE source_id=?', (source_id,)).fetchone())
        result['review_progress'] = self.review.overview(source_id)['pages']
        result['provenance'] = self.operations.provenance(source_id)
        return result

    def listing(self, *, include_capabilities=True):
        with self.db() as db:
            rows = db.execute('SELECT id,filename,created_at,state,page_count,confirmed,metadata FROM pdf_sources ORDER BY created_at DESC').fetchall()
        result = {'items': [{**dict(row), 'metadata': json.loads(row['metadata'])} for row in rows]}
        if include_capabilities:
            result['capabilities'] = self.capabilities()
        return result

    def page(self, source_id, number):
        self.file_path(source_id)
        with self.db() as db:
            row = db.execute('SELECT * FROM pdf_pages WHERE source_id=? AND page_number=?', (source_id, int(number))).fetchone()
            if not row:
                raise EditorialError('Página ainda não extraída', 404)
            result = dict(row)
            result['paragraphs'] = json.loads(result['paragraphs'])
            return result

    def action(self, payload, catalog):
        if not isinstance(payload, dict):
            raise EditorialError('Pedido inválido')
        source_id = text(payload.get('source_id'), 80)
        action = payload.get('action')
        self.file_path(source_id)
        with self.lock, self.db() as db:
            row = db.execute('SELECT * FROM pdf_sources WHERE id=?', (source_id,)).fetchone()
            if not row:
                raise EditorialError('Fonte não encontrada', 404)
            if action == 'resume':
                self.require_engine()
                if row['state'] not in ('failed', 'interrupted', 'completed_with_errors'):
                    raise EditorialError('A fonte não tem processamento interrompido ou com falhas', 409)
                db.execute("UPDATE pdf_sources SET state='queued',error=NULL WHERE id=?", (source_id,))
                db.execute("UPDATE pdf_jobs SET state='queued',error=NULL,updated_at=? WHERE source_id=?", (now(), source_id))
            elif action == 'position':
                number = payload.get('page_number')
                if type(number) is not int or not 1 <= number <= (row['page_count'] or 1):
                    raise EditorialError('Página inválida')
                db.execute('UPDATE pdf_sources SET last_page=? WHERE id=?', (number, source_id))
            elif action in ('confirm', 'restore'):
                if type(payload.get('revision')) is not int or payload['revision'] != row['revision']:
                    raise EditorialError('A fonte foi alterada em outra aba. Reabra a prévia.', 409)
                before = {'metadata': json.loads(row['metadata']), 'confirmed': bool(row['confirmed'])}
                if action == 'restore':
                    record = db.execute('SELECT before_state FROM pdf_history WHERE id=? AND source_id=?',
                                        (payload.get('history_id'), source_id)).fetchone()
                    if not record:
                        raise EditorialError('Registro de histórico não encontrado', 404)
                    after = json.loads(record['before_state'])
                else:
                    after = {'metadata': self.validate_metadata(payload.get('metadata'), catalog), 'confirmed': True}
                if after['confirmed']:
                    self.validate_metadata(after['metadata'], catalog)
                db.execute('INSERT INTO pdf_history VALUES(?,?,?,?,?)', ('change-' + secrets.token_hex(16), source_id, now(), json.dumps(before, ensure_ascii=False), json.dumps(after, ensure_ascii=False)))
                db.execute('UPDATE pdf_sources SET metadata=?,confirmed=?,revision=revision+1 WHERE id=?',
                           (json.dumps(after['metadata'], ensure_ascii=False), int(after['confirmed']), source_id))
            else:
                raise EditorialError('Operação PDF desconhecida')
        self.wakeup.set()
        return self.source(source_id)

    def validate_metadata(self, metadata, catalog):
        if not isinstance(metadata, dict) or set(metadata) != {'title', 'collection_id', 'subcollection_id', 'language', 'source_url', 'archive_reference'}:
            raise EditorialError('Metadados da fonte inválidos')
        cleaned = {key: text(value, 4000) for key, value in metadata.items()}
        by_id = {c['id']: c for c in catalog['collections']}
        collection = by_id.get(cleaned['collection_id'])
        child = by_id.get(cleaned['subcollection_id']) if cleaned['subcollection_id'] else None
        if not cleaned['title'] or not collection or collection['parent_id'] is not None:
            raise EditorialError('Informe título e coleção principal existente')
        if cleaned['subcollection_id'] and (not child or child['parent_id'] != collection['id']):
            raise EditorialError('Escolha uma subcoleção desta coleção ou nenhuma')
        if cleaned['language'] not in ('ru', 'pt', 'en', 'mixed'):
            raise EditorialError('Idioma inválido')
        from urllib.parse import urlsplit
        url = urlsplit(cleaned['source_url'])
        if cleaned['source_url'] and (url.scheme not in ('http', 'https') or not url.netloc):
            raise EditorialError('URL de origem inválida')
        return cleaned

    def history(self, source_id):
        self.file_path(source_id)
        with self.db() as db:
            return {'items': [{**dict(r), 'before_state': json.loads(r['before_state']), 'after_state': json.loads(r['after_state'])}
                              for r in db.execute('SELECT * FROM pdf_history WHERE source_id=? ORDER BY created_at DESC', (source_id,))]}

    def _loop(self):
        while not self.stopping.is_set():
            with self.db() as db:
                ocr = db.execute("SELECT id FROM pdf_ocr_jobs WHERE state='queued' ORDER BY created_at LIMIT 1").fetchone()
            if ocr:
                self._run_ocr(ocr['id'])
                continue
            with self.db() as db:
                operation = db.execute("SELECT id FROM pdf_operations WHERE state='queued' ORDER BY created_at LIMIT 1").fetchone()
            if operation:
                self._run_operation(operation['id'])
                continue
            with self.db() as db:
                row = db.execute("SELECT source_id FROM pdf_jobs WHERE state='queued' ORDER BY created_at LIMIT 1").fetchone()
            if not row:
                self.wakeup.wait(1)
                self.wakeup.clear()
                continue
            source_id = row['source_id']
            error = None
            try:
                self.process = subprocess.Popen([sys.executable, '-m', 'backend.pdf_worker', str(self.root), source_id],
                                                cwd=Path(__file__).resolve().parents[1], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.process.wait(timeout=600)
                if self.process.returncode:
                    error = 'O extrator foi interrompido ou excedeu seus recursos. Retome para tentar as páginas pendentes.'
            except subprocess.TimeoutExpired:
                self._stop_process(self.process, signal.SIGKILL)
                self.process.wait()
                error = 'Limite de 10 minutos atingido. As páginas concluídas foram preservadas; use Retomar.'
            except OSError:
                error = 'Não foi possível iniciar o processo de extração.'
            if error or self.stopping.is_set():
                with self.db() as db:
                    state = 'interrupted' if self.stopping.is_set() else 'failed'
                    db.execute('UPDATE pdf_jobs SET state=?,error=?,updated_at=? WHERE source_id=?', (state, error, now(), source_id))
                    db.execute('UPDATE pdf_sources SET state=?,error=? WHERE id=?', (state, error, source_id))
            self.process = None

    def _run_operation(self, operation_id):
        error = None
        try:
            self.process = subprocess.Popen([sys.executable, '-m', 'backend.pdf_operation_worker', str(self.root), operation_id],
                                            cwd=Path(__file__).resolve().parents[1], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.process.wait(timeout=600)
            if self.process.returncode:
                error = 'O processamento excedeu seus recursos ou foi interrompido. Resultados concluídos foram preservados; use Retomar.'
        except subprocess.TimeoutExpired:
            self._stop_process(self.process, signal.SIGKILL)
            self.process.wait()
            error = 'Limite de 10 minutos atingido. Use Retomar para continuar as partes pendentes.'
        except OSError:
            error = 'Não foi possível iniciar a ferramenta PDF.'
        try:
            if not self.stopping.is_set():
                self.operations.finish(operation_id)
        except Exception as failure:
            error = 'Não foi possível registrar todos os derivados: ' + str(failure)[:500]
        with self.db() as db:
            current = db.execute('SELECT state FROM pdf_operations WHERE id=?', (operation_id,)).fetchone()['state']
            if self.stopping.is_set() or (error and current != 'completed'):
                db.execute('UPDATE pdf_operations SET state=?,error=?,updated_at=? WHERE id=?',
                           ('interrupted' if self.stopping.is_set() else 'failed', error, now(), operation_id))
        self.process = None

    @staticmethod
    def _stop_process(process, sig):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass

    def _run_ocr(self, job_id):
        error = None
        try:
            self.process = subprocess.Popen([sys.executable, '-m', 'backend.pdf_ocr_worker', str(self.root), job_id],
                cwd=Path(__file__).resolve().parents[1], start_new_session=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.process.wait(timeout=1800)
            if self.process.returncode:
                error = 'OCR interrompido ou limite de recursos atingido. Retome o lote.'
        except subprocess.TimeoutExpired:
            self._stop_process(self.process, signal.SIGKILL)
            self.process.wait()
            error = 'Limite de 30 minutos atingido. Retome as páginas restantes.'
        except OSError:
            error = 'Não foi possível iniciar o OCR.'
        # Kill any renderer/OCR descendants left after a failed worker exits.
        if self.process:
            self._stop_process(self.process, signal.SIGKILL)
        if error or self.stopping.is_set():
            with self.db() as db:
                db.execute("UPDATE pdf_ocr_jobs SET state=?,error=?,updated_at=? WHERE id=?",
                    ('interrupted' if self.stopping.is_set() else 'failed', error, now(), job_id))
        self.process = None

    def close(self):
        self.stopping.set()
        self.wakeup.set()
        if self.worker is None:
            return
        self.worker.join(timeout=1)
        process = self.process
        if process and process.poll() is None:
            self._stop_process(process, signal.SIGTERM)
        self.worker.join(timeout=4)
        if self.worker.is_alive() and process and process.poll() is None:
            self._stop_process(process, signal.SIGKILL)
            self.worker.join(timeout=4)
        # Não liberar o bloqueio do acervo enquanto o supervisor confirma um resultado em disco.
        self.worker.join()
