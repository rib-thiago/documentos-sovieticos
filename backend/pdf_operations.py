"""Operações locais de páginas: receita confirmada, derivados e proveniência."""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import time
from pathlib import Path

from .editorial import EditorialError
from .pdf_sources import now

MAX_OUTPUTS = 200


def page_selection(value, count):
    if not isinstance(value, str) or not value.strip() or len(value) > 12000:
        raise EditorialError('Informe páginas como 1-5, 8, 12-15')
    result = []
    for term in value.split(','):
        match = re.fullmatch(r'\s*(\d+)\s*(?:-\s*(\d+)\s*)?', term)
        if not match:
            raise EditorialError('Seleção inválida. Use números e intervalos separados por vírgulas.')
        start, end = int(match[1]), int(match[2] or match[1])
        if not 1 <= start <= end <= count:
            raise EditorialError(f'Use páginas físicas entre 1 e {count}, com intervalos crescentes.')
        result.extend(range(start, end + 1))
    if len(result) != len(set(result)):
        raise EditorialError('Há páginas repetidas na seleção. Cada página deve aparecer uma vez.')
    return result


def operation_directory(root, operation_id):
    if not isinstance(operation_id, str) or not re.fullmatch(r'pdfop-[a-f0-9]{32}', operation_id):
        raise EditorialError('Identificador de operação inválido', 404)
    return Path(root) / '.local/research/operations' / operation_id


class PDFOperations:
    def __init__(self, sources):
        self.sources = sources
        self.projects = None
        self.previews = {}
        with sources.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS pdf_operations (
                    id TEXT PRIMARY KEY, source_id TEXT NOT NULL, source_sha256 TEXT NOT NULL,
                    project_id TEXT, recipe TEXT NOT NULL, state TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, error TEXT, warning TEXT);
                CREATE TABLE IF NOT EXISTS pdf_operation_outputs (
                    operation_id TEXT NOT NULL, position INTEGER NOT NULL, pages TEXT NOT NULL,
                    filename TEXT NOT NULL, title TEXT NOT NULL, artifact_sha256 TEXT,
                    result_source_id TEXT, engine TEXT,
                    PRIMARY KEY(operation_id, position));
                CREATE INDEX IF NOT EXISTS pdf_outputs_source ON pdf_operation_outputs(result_source_id);
            ''')
            db.execute("UPDATE pdf_operations SET state='interrupted',updated_at=? WHERE state IN ('running','generated')", (now(),))

    def _project(self, project_id):
        if not project_id:
            return
        if not self.projects:
            raise EditorialError('O contexto de projetos não está disponível')
        if self.projects.get(project_id)['archived']:
            raise EditorialError('Escolha um projeto não arquivado')

    def preview(self, payload):
        allowed = {'source_id', 'project_id', 'mode', 'pages', 'split_mode', 'pages_per_part', 'ranges'}
        if not isinstance(payload, dict) or set(payload) != allowed:
            raise EditorialError('Configuração de PDF inválida')
        self.sources.require_engine()
        source = self.sources.source(payload['source_id'])
        count = source['page_count']
        if not count:
            raise EditorialError('Aguarde o inventário de páginas da fonte e tente novamente.', 409)
        project_id = payload['project_id'] or None
        self._project(project_id)
        mode = payload['mode']
        if mode == 'extract':
            groups = [page_selection(payload['pages'], count)]
        elif mode == 'split' and payload['split_mode'] == 'size':
            size = payload['pages_per_part']
            if type(size) is not int or not 1 <= size <= count:
                raise EditorialError(f'Informe de 1 a {count} páginas por parte')
            groups = [list(range(start, min(start + size, count + 1))) for start in range(1, count + 1, size)]
        elif mode == 'split' and payload['split_mode'] == 'ranges':
            ranges = payload['ranges']
            if not isinstance(ranges, str) or len(ranges) > 20000:
                raise EditorialError('Informe os intervalos das partes, separados por ponto e vírgula')
            groups = [page_selection(group, count) for group in ranges.split(';')]
        else:
            raise EditorialError('Escolha extrair páginas ou dividir por tamanho/intervalos')
        if len(groups) > MAX_OUTPUTS:
            raise EditorialError(f'Uma operação pode gerar até {MAX_OUTPUTS} partes. Aumente o tamanho de cada parte.')
        flat = [page for group in groups for page in group]
        if len(flat) != len(set(flat)):
            raise EditorialError('As partes possuem páginas sobrepostas. Confira os intervalos.')
        stem = Path(source['filename']).stem[:160]
        outputs = [{'position': index, 'pages': group,
                    'filename': f'{stem}-parte-{index:03d}.pdf',
                    'title': ((source['metadata'].get('title') or stem)[:3800] + f' · parte {index} ({len(group)} páginas)')}
                   for index, group in enumerate(groups, 1)]
        result = {'source_id': source['id'], 'source_sha256': source['sha256'], 'source_revision': source['revision'],
                  'source_filename': source['filename'], 'project_id': project_id, 'outputs': outputs,
                  'recipe': {'version': 'pdf-pages-v1', 'mode': mode, 'source_metadata': source['metadata'],
                             'source_page_count': count, 'selected_pages': len(flat), 'omitted_pages': count - len(flat)}}
        with self.sources.lock:
            self.previews = {key: item for key, item in self.previews.items() if item['expires'] > time.monotonic()}
            token = secrets.token_urlsafe(24)
            self.previews[token] = {'expires': time.monotonic() + 900, 'plan': result}
        return {'preview_id': token, **result}

    def enqueue(self, payload):
        if not isinstance(payload, dict) or set(payload) != {'preview_id'}:
            raise EditorialError('Confirme uma prévia de operação PDF')
        with self.sources.lock:
            preview = self.previews.get(payload['preview_id'])
            if not preview or preview['expires'] < time.monotonic():
                raise EditorialError('Prévia expirada. Confira a operação novamente.', 409)
            plan = preview['plan']
            source = self.sources.source(plan['source_id'])
            if source['sha256'] != plan['source_sha256'] or source['revision'] != plan['source_revision']:
                raise EditorialError('A fonte mudou depois da prévia. Confira novamente.', 409)
            self._project(plan['project_id'])
            operation_id, stamp = 'pdfop-' + secrets.token_hex(16), now()
            with self.sources.db() as db:
                db.execute('INSERT INTO pdf_operations VALUES(?,?,?,?,?,?,?,?,?,?)',
                           (operation_id, plan['source_id'], plan['source_sha256'], plan['project_id'], json.dumps(plan['recipe'], ensure_ascii=False), 'queued', stamp, stamp, None, None))
                for output in plan['outputs']:
                    db.execute('INSERT INTO pdf_operation_outputs VALUES(?,?,?,?,?,?,?,?)',
                               (operation_id, output['position'], json.dumps(output['pages']), output['filename'], output['title'], None, None, None))
            self.previews.pop(payload['preview_id'], None)
        self.sources.wakeup.set()
        return self.get(operation_id)

    def get(self, operation_id):
        operation_directory(self.sources.root, operation_id)
        with self.sources.db() as db:
            row = db.execute('SELECT * FROM pdf_operations WHERE id=?', (operation_id,)).fetchone()
            if not row:
                raise EditorialError('Operação PDF não encontrada', 404)
            outputs = db.execute('SELECT * FROM pdf_operation_outputs WHERE operation_id=? ORDER BY position', (operation_id,)).fetchall()
        return {**dict(row), 'recipe': json.loads(row['recipe']),
                'outputs': [{**dict(output), 'pages': json.loads(output['pages'])} for output in outputs],
                'generated': sum(bool(output['artifact_sha256']) for output in outputs),
                'registered': sum(bool(output['result_source_id']) for output in outputs)}

    def listing(self, params):
        if set(params) - {'source_id', 'project_id'}:
            raise EditorialError('Filtro de operações inválido')
        where, values = [], []
        for field, value in params.items():
            where.append(field + '=?')
            values.append(value)
        with self.sources.db() as db:
            rows = db.execute('SELECT id FROM pdf_operations' + (' WHERE ' + ' AND '.join(where) if where else '') + ' ORDER BY created_at DESC LIMIT 50', values).fetchall()
        return {'items': [self.get(row['id']) for row in rows]}

    def resume(self, payload):
        if not isinstance(payload, dict) or set(payload) != {'operation_id'}:
            raise EditorialError('Selecione a operação para retomar')
        with self.sources.lock, self.sources.db() as db:
            current = self.get(payload['operation_id'])
            if current['state'] not in ('failed', 'interrupted') and not (current['state'] == 'completed' and current['warning']):
                raise EditorialError('Esta operação não precisa de retomada', 409)
            self.sources.require_engine()
            db.execute("UPDATE pdf_operations SET state='queued',error=NULL,warning=NULL,updated_at=? WHERE id=?", (now(), current['id']))
        self.sources.wakeup.set()
        return self.get(current['id'])

    def finish(self, operation_id):
        """Registra resultados concluídos mesmo após falha parcial, sem apagar a origem."""
        operation = self.get(operation_id)
        metadata = operation['recipe']['source_metadata']
        directory = operation_directory(self.sources.root, operation_id)
        for output in operation['outputs']:
            if self.sources.stopping.is_set():
                return
            if output['result_source_id'] or not output['artifact_sha256']:
                continue
            path = directory / f"part-{output['position']:03d}.pdf"
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                if digest != output['artifact_sha256']:
                    raise EditorialError('Um resultado candidato mudou. Retome para regenerá-lo.', 409)
                stream.seek(0)
                result = self.sources.upload_stream(output['filename'], stream, path.stat().st_size, enforce_limit=False)
            with self.sources.lock, self.sources.db() as db:
                # A deduplicação não altera os metadados de uma fonte já existente.
                if not result['duplicate']:
                    inherited = {**metadata, 'title': output['title']}
                    db.execute('UPDATE pdf_sources SET metadata=?,page_count=? WHERE id=?',
                               (json.dumps(inherited, ensure_ascii=False), len(output['pages']), result['source_id']))
                db.execute('UPDATE pdf_operation_outputs SET result_source_id=? WHERE operation_id=? AND position=?',
                           (result['source_id'], operation_id, output['position']))
            # O arquivo já está no banco de fontes e o registro de proveniência foi confirmado.
            path.unlink(missing_ok=True)
        operation = self.get(operation_id)
        if operation['registered'] != len(operation['outputs']):
            return
        warning = None
        if operation['project_id']:
            try:
                self.projects.attach_sources(operation['project_id'], [out['result_source_id'] for out in operation['outputs']], reason='Derivados da operação ' + operation_id)
            except Exception as error:
                warning = 'Derivados preservados; não foi possível vinculá-los ao projeto. Confira se ele está aberto e use Retomar. ' + str(error)[:400]
        with self.sources.db() as db:
            db.execute("UPDATE pdf_operations SET state='completed',error=NULL,warning=?,updated_at=? WHERE id=?", (warning, now(), operation_id))

    def provenance(self, source_id):
        with self.sources.db() as db:
            rows = db.execute('''SELECT o.id AS operation_id,o.source_id AS parent_source_id,o.source_sha256,
                x.pages,x.position,x.engine FROM pdf_operation_outputs x JOIN pdf_operations o ON o.id=x.operation_id
                WHERE x.result_source_id=? ORDER BY o.created_at''', (source_id,)).fetchall()
        return [{**dict(row), 'pages': json.loads(row['pages'])} for row in rows]
