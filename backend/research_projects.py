"""Projetos locais: vínculos com o acervo, prévia e histórico; sem publicação."""
from __future__ import annotations

import json
import re
import secrets
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .editorial import EditorialError, text


def now():
    return datetime.now(timezone.utc).isoformat()


class ResearchProjects:
    def __init__(self, root, sources):
        self.path = Path(root) / '.local/research/projects.sqlite3'
        self.sources = sources
        self.lock = threading.RLock()
        self.previews = {}
        with self.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS research_projects (
                    id TEXT PRIMARY KEY, revision INTEGER NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS research_context (
                    id INTEGER PRIMARY KEY CHECK(id=1), active_id TEXT);
                INSERT OR IGNORE INTO research_context VALUES(1,NULL);
                CREATE TABLE IF NOT EXISTS research_project_history (
                    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, created_at TEXT NOT NULL,
                    before_state TEXT, after_state TEXT NOT NULL, reason TEXT NOT NULL);
            ''')

    @contextmanager
    def db(self):
        connection = sqlite3.connect(self.path, timeout=20)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _project(self, db, project_id):
        if not isinstance(project_id, str) or not re.fullmatch(r'project-[a-f0-9]{32}', project_id):
            raise EditorialError('Identificador de projeto inválido', 404)
        row = db.execute('SELECT * FROM research_projects WHERE id=?', (project_id,)).fetchone()
        if not row:
            raise EditorialError('Projeto não encontrado', 404)
        return {**{key: row[key] for key in ('id', 'revision', 'created_at', 'updated_at')}, **json.loads(row['data'])}

    def listing(self):
        with self.db() as db:
            active_id = db.execute('SELECT active_id FROM research_context WHERE id=1').fetchone()[0]
            rows = db.execute('SELECT id FROM research_projects ORDER BY updated_at DESC').fetchall()
            projects = [self._project(db, row['id']) for row in rows]
        return {'items': projects, 'active_id': active_id, 'visibility': 'local'}

    def get(self, project_id):
        with self.db() as db:
            return self._project(db, project_id)

    def activate(self, project_id):
        with self.lock, self.db() as db:
            if project_id is not None:
                project = self._project(db, project_id)
                if project['archived']:
                    raise EditorialError('Reabra o projeto arquivado antes de ativá-lo')
            db.execute('UPDATE research_context SET active_id=? WHERE id=1', (project_id,))
        return self.listing()

    def _clean(self, payload, catalog, allow_missing=False):
        fields = {'title', 'description', 'collection_id', 'document_ids', 'source_ids', 'archived'}
        if not isinstance(payload, dict) or set(payload) != fields:
            raise EditorialError('Campos de projeto inválidos')
        result = {'title': text(payload['title'], 1000), 'description': text(payload['description'], 20000),
                  'collection_id': text(payload['collection_id'], 120), 'archived': payload['archived']}
        if not result['title'] or type(result['archived']) is not bool:
            raise EditorialError('Informe o título e o estado do projeto')
        collections = {c['id'] for c in catalog['collections']}
        if result['collection_id'] and result['collection_id'] not in collections and not allow_missing:
            raise EditorialError('Coleção de referência não encontrada')
        docs = {d['id'] for d in catalog['documents']}
        sources = {s['id'] for s in self.sources.listing()['items']}
        for field, valid in (('document_ids', docs), ('source_ids', sources)):
            values = payload[field]
            if not isinstance(values, list) or len(values) > 5000 or any(not isinstance(v, str) or not v or len(v) > 150 for v in values):
                raise EditorialError('Lista de vínculos inválida ou acima de 5.000 itens')
            if not allow_missing and set(values) - valid:
                raise EditorialError('Há vínculos não encontrados. Reabra o projeto e confira os itens.')
            result[field] = list(dict.fromkeys(values))
        return result

    def state(self, project):
        return {key: project[key] for key in ('title', 'description', 'collection_id', 'document_ids', 'source_ids', 'archived')}

    def preview(self, payload, catalog):
        if not isinstance(payload, dict) or set(payload) - {'project_id', 'revision', 'project', 'history_id'}:
            raise EditorialError('Pedido de prévia inválido')
        with self.lock, self.db() as db:
            project_id = payload.get('project_id')
            current = self._project(db, project_id) if project_id else None
            revision = payload.get('revision')
            if current and (type(revision) is not int or revision != current['revision']):
                raise EditorialError('Este projeto mudou em outra aba ou recebeu uma fonte. Reabra antes de editar.', 409)
            before = self.state(current) if current else None
            if payload.get('history_id'):
                if not current:
                    raise EditorialError('Escolha um projeto para restaurar')
                row = db.execute('SELECT before_state FROM research_project_history WHERE id=? AND project_id=?',
                                 (payload['history_id'], project_id)).fetchone()
                if not row:
                    raise EditorialError('Histórico não encontrado', 404)
                after = json.loads(row[0]) if row[0] else {**before, 'archived': True}
                reason = 'Restauração de estado anterior'
                after = self._clean(after, catalog, allow_missing=True)
            else:
                after = self._clean(payload.get('project'), catalog)
                reason = 'Edição do projeto' if current else 'Criação do projeto'
            if before == after:
                raise EditorialError('Nenhuma alteração para salvar')
            project_id = project_id or 'project-' + secrets.token_hex(16)
            token = secrets.token_urlsafe(24)
            self.previews = {key: value for key, value in self.previews.items() if value['expires'] > time.monotonic()}
            self.previews[token] = {'id': project_id, 'revision': current['revision'] if current else None,
                                    'before': before, 'after': after, 'reason': reason, 'expires': time.monotonic() + 900}
            return {'preview_id': token, 'project_id': project_id, 'before': before, 'after': after, 'reason': reason}

    def _write(self, db, project_id, before, after, revision, reason):
        history_id = 'project-change-' + secrets.token_hex(16)
        stamp = now()
        db.execute('INSERT INTO research_project_history VALUES(?,?,?,?,?,?)',
                   (history_id, project_id, stamp, json.dumps(before, ensure_ascii=False) if before is not None else None,
                    json.dumps(after, ensure_ascii=False), reason))
        if revision is None:
            db.execute('INSERT INTO research_projects VALUES(?,?,?,?,?)', (project_id, 1, stamp, stamp, json.dumps(after, ensure_ascii=False)))
        else:
            db.execute('UPDATE research_projects SET data=?,revision=revision+1,updated_at=? WHERE id=?',
                       (json.dumps(after, ensure_ascii=False), stamp, project_id))
        if after['archived']:
            db.execute('UPDATE research_context SET active_id=NULL WHERE active_id=?', (project_id,))
        return history_id

    def save(self, payload, catalog):
        if not isinstance(payload, dict) or set(payload) != {'preview_id'}:
            raise EditorialError('Confirme uma prévia de projeto válida')
        with self.lock, self.db() as db:
            preview = self.previews.get(payload['preview_id'])
            if not preview or preview['expires'] < time.monotonic():
                raise EditorialError('Prévia expirada. Confira novamente.', 409)
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT revision FROM research_projects WHERE id=?', (preview['id'],)).fetchone()
            if (row['revision'] if row else None) != preview['revision']:
                raise EditorialError('O projeto mudou depois da prévia. Reabra e confira novamente.', 409)
            self._clean(preview['after'], catalog, allow_missing=preview['reason'].startswith('Restauração'))
            history_id = self._write(db, preview['id'], preview['before'], preview['after'], preview['revision'], preview['reason'])
            self.previews.pop(payload['preview_id'], None)
        return {'saved': True, 'project_id': preview['id'], 'history_id': history_id}

    def history(self, project_id):
        with self.db() as db:
            self._project(db, project_id)
            rows = db.execute('SELECT * FROM research_project_history WHERE project_id=? ORDER BY created_at DESC', (project_id,)).fetchall()
        return {'items': [{**dict(row), 'before_state': json.loads(row['before_state']) if row['before_state'] else None,
                           'after_state': json.loads(row['after_state'])} for row in rows]}

    def attach_source(self, project_id, source_id):
        self.attach_sources(project_id, [source_id], reason='Fonte recebida no projeto')

    def attach_sources(self, project_id, source_ids, *, reason):
        # Upload explicitamente direcionado: inclusão aditiva não substitui vínculos de outra aba.
        with self.lock, self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            project = self._project(db, project_id)
            if project['archived']:
                raise EditorialError('Não é possível vincular uma fonte a projeto arquivado', 409)
            additions = [source_id for source_id in dict.fromkeys(source_ids) if source_id not in project['source_ids']]
            if not additions:
                return
            if len(project['source_ids']) + len(additions) > 5000:
                raise EditorialError('O projeto atingiu o limite de 5.000 fontes. O PDF continua preservado.', 409)
            before = self.state(project)
            after = {**before, 'source_ids': [*before['source_ids'], *additions]}
            self._write(db, project_id, before, after, project['revision'], reason)
