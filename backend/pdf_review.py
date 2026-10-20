"""Revisão local por página e candidatos OCR; nunca escreve edições do acervo."""
from __future__ import annotations
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import time
from .editorial import EditorialError
from .pdf_sources import now
from .pdf_operations import page_selection

LANGUAGES = ('rus', 'eng', 'por')
STATUSES = ('pending', 'reviewed', 'problem', 'blank')


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def ocr_capabilities():
    renderer, engine = shutil.which('pdftoppm'), shutil.which('tesseract')
    installed, error, selected = [], None, None
    configured = os.environ.get('SHOWTRIALS_TESSDATA_DIR')
    # Explicit project configuration wins. Otherwise try Tesseract's environment,
    # followed by conventional system installations (some shells override it).
    paths = [configured] if configured else [None, '/usr/share/tesseract-ocr/5/tessdata', '/usr/share/tesseract-ocr/4.00/tessdata', '/usr/share/tessdata']
    if engine:
        for directory in paths:
            if directory and not Path(directory).is_dir():
                continue
            try:
                command = [engine, '--list-langs'] + (['--tessdata-dir', directory] if directory else [])
                result = subprocess.run(command, capture_output=True, text=True, timeout=5)
                found = [line.strip() for line in result.stdout.splitlines() if line.strip() in LANGUAGES] if not result.returncode else []
                if found:
                    installed, selected = found, directory
                    break
            except (OSError, subprocess.TimeoutExpired):
                error = 'Não foi possível consultar o Tesseract.'
    return {'available': bool(renderer and engine and installed), 'renderer': bool(renderer),
            'engine': bool(engine), 'languages': installed, 'supported_languages': list(LANGUAGES),
            'tessdata_dir': selected, 'error': error,
            'installation': 'sudo apt install poppler-utils tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng tesseract-ocr-por'}


class PDFReview:
    def __init__(self, sources):
        self.sources = sources
        self.previews = {}
        with sources.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS pdf_page_reviews (
                    source_id TEXT, page_number INTEGER, revision INTEGER NOT NULL,
                    data TEXT NOT NULL, updated_at TEXT NOT NULL,
                    PRIMARY KEY(source_id,page_number));
                CREATE TABLE IF NOT EXISTS pdf_page_review_history (
                    id TEXT PRIMARY KEY, source_id TEXT, page_number INTEGER,
                    created_at TEXT, before_state TEXT, after_state TEXT);
                CREATE TABLE IF NOT EXISTS pdf_ocr_jobs (
                    id TEXT PRIMARY KEY, source_id TEXT, source_sha256 TEXT,
                    recipe TEXT, state TEXT, created_at TEXT, updated_at TEXT, error TEXT);
                CREATE TABLE IF NOT EXISTS pdf_ocr_candidates (
                    id TEXT PRIMARY KEY, job_id TEXT, source_id TEXT, page_number INTEGER,
                    raw_text TEXT NOT NULL, text_sha256 TEXT NOT NULL, engine TEXT NOT NULL,
                    geometry TEXT NOT NULL, created_at TEXT NOT NULL,
                    UNIQUE(job_id,page_number));
            ''')
            db.execute("UPDATE pdf_ocr_jobs SET state='interrupted',updated_at=? WHERE state='running'", (now(),))

    def page(self, source_id, number):
        # Raw extractor owns pdf_pages. Review and OCR are separate records.
        raw = self.sources.page(source_id, number)
        with self.sources.db() as db:
            row = db.execute('SELECT * FROM pdf_page_reviews WHERE source_id=? AND page_number=?', (source_id, number)).fetchone()
            review = json.loads(row['data']) if row else {'text': raw['raw_text'], 'status': 'pending', 'printed_label': raw['printed_label'] or '', 'notes': '', 'basis': 'native', 'units': [{'id': u['id'], 'start': u['start'], 'end': u['start']+len(raw['raw_text'][u['start']:u['end']].rstrip()), 'sha256': digest(raw['raw_text'][u['start']:u['end']].rstrip()), 'boundary': 'blank_line_candidate'} for u in raw['paragraphs']]}
            candidates = [dict(r) for r in db.execute('SELECT id,job_id,raw_text,text_sha256,engine,created_at FROM pdf_ocr_candidates WHERE source_id=? AND page_number=? ORDER BY created_at DESC', (source_id, number))]
            history = [dict(r) for r in db.execute('SELECT * FROM pdf_page_review_history WHERE source_id=? AND page_number=? ORDER BY created_at DESC', (source_id, number))]
        for item in history:
            item['before_state'] = json.loads(item['before_state'])
            item['after_state'] = json.loads(item['after_state'])
        return {'revision': row['revision'] if row else 0, 'review': review, 'candidates': candidates,
                'history': history, 'raw': raw}

    def overview(self, source_id):
        self.sources.file_path(source_id)
        with self.sources.db() as db:
            rows = db.execute('SELECT page_number,revision,data FROM pdf_page_reviews WHERE source_id=? ORDER BY page_number', (source_id,)).fetchall()
            jobs = [dict(r) for r in db.execute('SELECT * FROM pdf_ocr_jobs WHERE source_id=? ORDER BY created_at DESC', (source_id,))]
            for job in jobs:
                job['recipe'] = json.loads(job['recipe'])
                job['completed_pages'] = [r[0] for r in db.execute('SELECT page_number FROM pdf_ocr_candidates WHERE job_id=? ORDER BY page_number', (job['id'],))]
        with self.sources.db() as db:
            source = db.execute('SELECT page_count FROM pdf_sources WHERE id=?', (source_id,)).fetchone()
            if not source:
                raise EditorialError('Fonte não encontrada', 404)
        return {'total_pages': source['page_count'], 'pages': [{'page_number': r['page_number'], 'revision': r['revision'], 'status': json.loads(r['data'])['status']} for r in rows], 'jobs': jobs}

    def stash(self, kind, plan):
        self.previews = {k: v for k, v in self.previews.items() if v[0] > time.monotonic()}
        if len(self.previews) >= 100:
            raise EditorialError('Muitas prévias abertas. Aguarde ou reinicie o backend.', 409)
        key = secrets.token_urlsafe(24)
        self.previews[key] = (time.monotonic()+900, kind, plan)
        return key

    def take(self, payload, kind):
        record = self.previews.get(payload.get('preview_id', ''))
        if not record or record[0] < time.monotonic() or record[1] != kind:
            raise EditorialError('Prévia expirada. Confira novamente antes de salvar.', 409)
        return record[2]

    def preview(self, payload):
        with self.sources.lock:
            source_id, number = self.identity(payload)
            current = self.page(source_id, number)
            if type(payload.get('revision')) is not int or payload['revision'] != current['revision']:
                raise EditorialError('Página alterada em outra aba. Reabra a página antes de revisar.', 409)
            if payload.get('history_id'):
                entry = next((h for h in current['history'] if h['id'] == payload['history_id']), None)
                if not entry:
                    raise EditorialError('Histórico não encontrado', 404)
                after = entry['before_state'].copy()
            else:
                after = payload.get('review')
                if not isinstance(after, dict) or set(after) != {'text', 'status', 'printed_label', 'notes', 'basis'}:
                    raise EditorialError('Campos de revisão inválidos')
                after = after.copy()
                for key, maximum in [('text', 2000000), ('printed_label', 100), ('notes', 10000), ('basis', 100)]:
                    if not isinstance(after[key], str) or len(after[key]) > maximum or '\x00' in after[key]:
                        raise EditorialError('Conteúdo de revisão inválido: '+key)
                if after['status'] not in STATUSES or (after['status'] == 'blank' and after['text'].strip()):
                    raise EditorialError('Estado inválido: página em branco deve ter texto vazio')
                if after['basis'] != 'native' and not any(c['id'] == after['basis'] for c in current['candidates']):
                    raise EditorialError('Candidato OCR não pertence a esta página')
                old_units = current['review'].get('units', [])
                # Match exact unchanged paragraphs, retaining IDs across edits/reordering.
                pools = {}
                for unit in old_units:
                    pools.setdefault(unit['sha256'], []).append(unit)
                units = []
                for match in re.finditer(r'\S[\s\S]*?(?=\n\s*\n|\Z)', after['text']):
                    value = match.group().rstrip()
                    hashed = digest(value)
                    prior = pools.get(hashed, [])
                    previous = prior.pop(0) if prior else {}
                    units.append({**previous, 'id': previous.get('id') or 'unit-'+secrets.token_hex(16), 'start': match.start(), 'end': match.start()+len(value), 'sha256': hashed, 'boundary': previous.get('boundary','blank_line_candidate')})
                if after['text'] == current['review']['text']:
                    units = old_units
                after['units'] = units
                after['structure_events'] = current['review'].get('structure_events', [])[-199:]
                retired = [u['id'] for u in old_units if u['id'] not in {n['id'] for n in units}]
                if retired:
                    after['structure_events'] = after['structure_events']+[{'action':'text_edit','before':retired,'after':[u['id'] for u in units if u['id'] not in {n['id'] for n in old_units}]}]
            plan = {'source_id': source_id, 'page_number': number, 'revision': current['revision'],
                    'before': current['review'], 'after': after, 'raw_sha256': current['raw']['text_sha256']}
            diff = ''.join(difflib.unified_diff(current['review']['text'].splitlines(True), after['text'].splitlines(True), fromfile='Versão atual', tofile='Revisão proposta'))
            return {'preview_id': self.stash('review', plan), 'before': plan['before'], 'after': after, 'diff': diff}

    def save(self, payload):
        with self.sources.lock:
            plan = self.take(payload, 'review')
            current = self.page(plan['source_id'], plan['page_number'])
            if current['revision'] != plan['revision'] or current['raw']['text_sha256'] != plan['raw_sha256']:
                raise EditorialError('A página mudou. Faça nova prévia.', 409)
            stamp = now()
            with self.sources.db() as db:
                db.execute('INSERT INTO pdf_page_review_history VALUES(?,?,?,?,?,?)', ('rev-'+secrets.token_hex(16), plan['source_id'], plan['page_number'], stamp, json.dumps(plan['before']), json.dumps(plan['after'])))
                db.execute('INSERT OR REPLACE INTO pdf_page_reviews VALUES(?,?,?,?,?)', (plan['source_id'], plan['page_number'], current['revision']+1, json.dumps(plan['after']), stamp))
            del self.previews[payload['preview_id']]
            return self.page(plan['source_id'], plan['page_number'])

    def identity(self, payload):
        if not isinstance(payload, dict):
            raise EditorialError('Pedido inválido')
        source_id, number = payload.get('source_id'), payload.get('page_number')
        if not isinstance(source_id, str) or type(number) is not int or number < 1:
            raise EditorialError('Fonte ou página inválida')
        self.sources.file_path(source_id)
        return source_id, number

    def ocr_preview(self, payload):
        with self.sources.lock:
            source_id = payload.get('source_id')
            if not isinstance(source_id, str):
                raise EditorialError('Fonte inválida')
            source = self.sources.source(source_id)
            capabilities = ocr_capabilities()
            languages = payload.get('languages')
            if not isinstance(languages, list) or not languages or len(languages) > 3 or any(l not in LANGUAGES for l in languages) or len(set(languages)) != len(languages):
                raise EditorialError('Escolha russo, inglês e/ou português')
            if not capabilities['available'] or any(l not in capabilities['languages'] for l in languages):
                raise EditorialError('OCR indisponível para os idiomas escolhidos. Confira as dependências e modelos de idioma.', 409)
            count = source['page_count']
            if not count:
                raise EditorialError('Aguarde o inventário das páginas', 409)
            pages = page_selection(payload.get('pages', ''), count)
            if len(pages) > 50:
                raise EditorialError('Selecione até 50 páginas por lote OCR')
            dpi, psm = payload.get('dpi'), payload.get('psm')
            if type(dpi) is not int or dpi not in (150, 200, 300) or type(psm) is not int or psm not in (3, 6):
                raise EditorialError('Use 150, 200 ou 300 DPI; segmentação automática ou bloco único')
            plan = {'source_id': source['id'], 'source_sha256': source['sha256'], 'recipe': {'version': 'ocr-v1', 'pages': pages, 'languages': languages, 'dpi': dpi, 'psm': psm, 'tessdata_dir': capabilities['tessdata_dir']}}
            return {'preview_id': self.stash('ocr', plan), **plan}

    def ocr_start(self, payload):
        with self.sources.lock:
            plan = self.take(payload, 'ocr')
            job_id = 'ocr-'+secrets.token_hex(16)
            with self.sources.db() as db:
                db.execute('INSERT INTO pdf_ocr_jobs VALUES(?,?,?,?,?,?,?,?)', (job_id, plan['source_id'], plan['source_sha256'], json.dumps(plan['recipe']), 'queued', now(), now(), None))
            del self.previews[payload['preview_id']]
            self.sources.wakeup.set()
            return {'job_id': job_id}

    def ocr_resume(self, payload):
        with self.sources.lock, self.sources.db() as db:
            row = db.execute('SELECT * FROM pdf_ocr_jobs WHERE id=?', (payload.get('job_id'),)).fetchone()
            if not row or row['state'] not in ('failed', 'interrupted'):
                raise EditorialError('Lote não disponível para retomada', 409)
            capabilities = ocr_capabilities()
            if not capabilities['available'] or any(l not in capabilities['languages'] for l in json.loads(row['recipe'])['languages']):
                raise EditorialError('Instale as dependências e idiomas deste lote antes de retomar', 409)
            db.execute("UPDATE pdf_ocr_jobs SET state='queued',error=NULL,updated_at=? WHERE id=?", (now(), row['id']))
        self.sources.wakeup.set()
        return {'job_id': row['id']}
