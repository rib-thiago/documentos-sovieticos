"""Edições de trabalho por projeto, isoladas do acervo e com promoção explícita."""
from __future__ import annotations

import json
import secrets
import time

from . import catalog as model, translations
from .editorial import EditorialError
from .research_projects import now


class WorkspaceEditions:
    def __init__(self, projects):
        self.projects = projects
        self.previews = {}
        self.promotions = {}
        with projects.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS workspace_editions (
                    project_id TEXT NOT NULL, edition_id TEXT NOT NULL, revision INTEGER NOT NULL,
                    content TEXT, base_sha256 TEXT, base_content TEXT, updated_at TEXT NOT NULL,
                    PRIMARY KEY(project_id, edition_id));
                CREATE TABLE IF NOT EXISTS workspace_edition_history (
                    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, edition_id TEXT NOT NULL,
                    created_at TEXT NOT NULL, before_state TEXT, after_state TEXT);
            ''')

    def _context(self, db, project_id, document_id, repository):
        project = self.projects._project(db, project_id)
        if document_id not in project['document_ids']:
            raise EditorialError('Este documento não está vinculado ao projeto. Vincule-o ou abra fora do workspace.', 409)
        document = next((d for d in repository.catalog['documents'] if d['id'] == document_id), None)
        if not document:
            raise EditorialError('Documento não encontrado no acervo', 404)
        return project, document

    def edition(self, repository, project_id, edition_id):
        if not isinstance(edition_id, str) or ':' not in edition_id:
            raise EditorialError('Versão inválida')
        document_id, language = edition_id.rsplit(':', 1)
        if language not in ('ru', 'pt', 'en'):
            raise EditorialError('Idioma inválido')
        with self.projects.db() as db:
            project, document = self._context(db, project_id, document_id, repository)
            row = db.execute('SELECT * FROM workspace_editions WHERE project_id=? AND edition_id=?', (project_id, edition_id)).fetchone()
        canonical = next((e for e in repository.catalog['editions'] if e['id'] == edition_id), None)
        if not canonical and language not in ('pt', 'en'):
            raise EditorialError('A versão original não existe no acervo', 404)
        canonical_content = model.content_bytes(repository.root, canonical['file']).decode('utf-8') if canonical else ''
        canonical_sha = model.sha256(canonical_content.encode('utf-8')) if canonical else None
        if canonical and canonical_sha != canonical['sha256']:
            raise EditorialError('A edição do acervo mudou fora do painel. Confira e reinicie o backend.', 409)
        has_draft = bool(row and row['content'] is not None)
        content = row['content'] if has_draft else canonical_content
        return {'project_id': project_id, 'project_title': project['title'], 'archived': project['archived'],
                'document_id': document_id, 'edition_id': edition_id, 'language': language,
                'content': content, 'content_sha256': model.sha256(content.encode('utf-8')),
                'revision': row['revision'] if row else 0, 'has_draft': has_draft,
                'format': 'markdown' if has_draft or not canonical else canonical['format'],
                'canonical_sha256': canonical_sha, 'base_sha256': row['base_sha256'] if has_draft else canonical_sha,
                'canonical_changed': has_draft and row['base_sha256'] != canonical_sha and model.sha256(content.encode('utf-8')) != canonical_sha,
                'canonical_exists': canonical is not None, 'canonical_content': canonical_content,
                'document': document}

    def document(self, repository, project_id, document_id):
        with self.projects.db() as db:
            self._context(db, project_id, document_id, repository)
            rows = db.execute('SELECT edition_id FROM workspace_editions WHERE project_id=? AND content IS NOT NULL', (project_id,)).fetchall()
        return {'editions': [self.edition(repository, project_id, row['edition_id']) for row in rows
                             if row['edition_id'].rsplit(':', 1)[0] == document_id]}

    def preview(self, repository, payload):
        required = {'project_id', 'edition_id', 'revision', 'content_sha256', 'content'}
        if not isinstance(payload, dict) or set(payload) - (required | {'filename', 'history_id'}) or not required.issubset(payload):
            raise EditorialError('Proposta de versão de projeto inválida')
        with self.projects.lock:
            current = self.edition(repository, payload['project_id'], payload['edition_id'])
            if current['archived']:
                raise EditorialError('Reabra o projeto arquivado antes de editar', 409)
            if type(payload['revision']) is not int or current['revision'] != payload['revision'] or current['content_sha256'] != payload['content_sha256']:
                raise EditorialError('A versão de trabalho mudou. Reabra o editor; seu texto não foi sobrescrito.', 409)
            content = payload['content']
            before = self._saved_state(payload['project_id'], payload['edition_id'])
            after = None
            if payload.get('history_id'):
                with self.projects.db() as db:
                    row = db.execute('SELECT before_state FROM workspace_edition_history WHERE id=? AND project_id=? AND edition_id=?',
                                     (payload['history_id'], payload['project_id'], payload['edition_id'])).fetchone()
                if not row:
                    raise EditorialError('Histórico não encontrado', 404)
                after = json.loads(row[0]) if row[0] else None
                content = after['content'] if after else current['canonical_content']
            else:
                if not isinstance(content, str) or not content.strip('\ufeff \t\r\n') or '\0' in content:
                    raise EditorialError('O Markdown está vazio ou contém caracteres inválidos')
                if len(content.encode('utf-8')) > translations.MAX_TRANSLATION_BYTES:
                    raise EditorialError('A versão de trabalho deve ter até 4 MiB', 413)
                # O envelope exportado não pertence ao corpo editorial da tradução.
                if payload.get('filename'):
                    content = translations.split_export_headers(content)['body']
                after = {'content': content, 'base_sha256': before['base_sha256'] if before else current['canonical_sha256'],
                         'base_content': before['base_content'] if before else current['canonical_content']}
            if after == before:
                raise EditorialError('Nenhuma alteração para salvar')
            warnings = []
            if payload.get('filename'):
                warnings = translations.findings(translations.identification(payload['filename'], payload['content']), current['document'], current['language'])
            token = secrets.token_urlsafe(24)
            self.previews = {k: v for k, v in self.previews.items() if v['expires'] > time.monotonic()}
            self.previews[token] = {'current': current, 'before': before, 'after': after, 'expires': time.monotonic() + 900}
            return {'preview_id': token, 'diff': translations.line_diff(current['content'], content), 'content': content,
                    'warnings': warnings, 'discard': after is None, 'project_title': current['project_title']}

    def _saved_state(self, project_id, edition_id):
        with self.projects.db() as db:
            row = db.execute('SELECT content,base_sha256,base_content FROM workspace_editions WHERE project_id=? AND edition_id=?', (project_id, edition_id)).fetchone()
        return dict(row) if row and row['content'] is not None else None

    def save(self, repository, payload):
        if not isinstance(payload, dict) or set(payload) != {'preview_id'}:
            raise EditorialError('Confirme a prévia da versão de trabalho')
        with self.projects.lock:
            proposed = self.previews.get(payload['preview_id'])
            if not proposed or proposed['expires'] < time.monotonic():
                raise EditorialError('Prévia expirada. Revise novamente.', 409)
            expected = proposed['current']
            current = self.edition(repository, expected['project_id'], expected['edition_id'])
            if current['archived'] or current['revision'] != expected['revision'] or current['content_sha256'] != expected['content_sha256']:
                raise EditorialError('A versão ou o projeto mudou depois da prévia. Reabra e confira.', 409)
            with self.projects.db() as db:
                stamp, history_id = now(), 'work-' + secrets.token_hex(16)
                db.execute('INSERT INTO workspace_edition_history VALUES(?,?,?,?,?,?)',
                           (history_id, current['project_id'], current['edition_id'], stamp,
                            json.dumps(proposed['before'], ensure_ascii=False) if proposed['before'] else None,
                            json.dumps(proposed['after'], ensure_ascii=False) if proposed['after'] else None))
                after = proposed['after'] or {}
                db.execute('''INSERT INTO workspace_editions VALUES(?,?,?,?,?,?,?)
                    ON CONFLICT(project_id,edition_id) DO UPDATE SET revision=excluded.revision,content=excluded.content,
                    base_sha256=excluded.base_sha256,base_content=excluded.base_content,updated_at=excluded.updated_at''',
                           (current['project_id'], current['edition_id'], current['revision'] + 1, after.get('content'),
                            after.get('base_sha256'), after.get('base_content'), stamp))
            self.previews.pop(payload['preview_id'], None)
        return {'saved': True, 'history_id': history_id, 'edition_id': current['edition_id'], 'project_id': current['project_id']}

    def history(self, repository, project_id, edition_id):
        self.edition(repository, project_id, edition_id)
        with self.projects.db() as db:
            rows = db.execute('SELECT * FROM workspace_edition_history WHERE project_id=? AND edition_id=? ORDER BY created_at DESC', (project_id, edition_id)).fetchall()
        return {'items': [{**dict(r), 'before_state': json.loads(r['before_state']) if r['before_state'] else None,
                           'after_state': json.loads(r['after_state']) if r['after_state'] else None} for r in rows]}

    def promotion_preview(self, repository, editorial, payload):
        if not isinstance(payload, dict) or set(payload) != {'project_id', 'edition_id', 'revision', 'content_sha256'}:
            raise EditorialError('Escolha uma versão de projeto salva para incorporar')
        with self.projects.lock:
            data = self.edition(repository, payload['project_id'], payload['edition_id'])
            if data['archived'] or not data['has_draft'] or data['revision'] != payload['revision'] or data['content_sha256'] != payload['content_sha256']:
                raise EditorialError('Salve e confira a versão atual do projeto antes de incorporá-la', 409)
            canonical = next((e for e in repository.catalog['editions'] if e['id'] == data['edition_id']), None)
            if canonical and canonical['format'] == 'markdown':
                result = editorial.preview_markdown(repository, {'revision': editorial.revision(), 'edition_id': data['edition_id'],
                    'content_sha256': canonical['sha256'], 'content': data['content']}, change_label='Incorporação explícita do projeto ' + data['project_title'])
            else:
                result = editorial.preview_translation(repository, {'revision': editorial.revision(), 'document_id': data['document_id'],
                    'language': data['language'], 'filename': data['document_id'] + '.' + data['language'] + '.md', 'content': data['content'], 'title': ''})
            token = secrets.token_urlsafe(24)
            self.promotions[token] = {'preview_id': result['preview_id'], 'project_id': data['project_id'], 'edition_id': data['edition_id'],
                                      'revision': data['revision'], 'content_sha256': data['content_sha256'], 'expires': time.monotonic() + 900}
            editorial.previews[result['preview_id']]['workspace_only'] = True
            editorial.previews[result['preview_id']]['changes'].append({'field': 'Origem da incorporação explícita', 'before': None,
                'after': {'project_id': data['project_id'], 'edition_id': data['edition_id'], 'workspace_revision': data['revision'], 'sha256': data['content_sha256']}})
            result['workspace_promotion_id'] = token
            result['canonical_changed'] = data['canonical_changed']
            result['workspace_diff'] = translations.line_diff(data['canonical_content'], data['content'])
            return result

    def promote(self, repository, editorial, payload):
        if not isinstance(payload, dict) or set(payload) != {'promotion_id', 'confirm_replace', 'acknowledge_warnings'} or payload['confirm_replace'] is not True:
            raise EditorialError('Confirme explicitamente a substituição no acervo')
        with self.projects.lock:
            item = self.promotions.get(payload['promotion_id'])
            if not item or item['expires'] < time.monotonic():
                raise EditorialError('Prévia de incorporação expirada. Confira novamente.', 409)
            data = self.edition(repository, item['project_id'], item['edition_id'])
            if data['archived'] or data['revision'] != item['revision'] or data['content_sha256'] != item['content_sha256']:
                raise EditorialError('A versão do projeto mudou. Prepare outra prévia.', 409)
            plan = editorial.previews.get(item['preview_id'])
            if not plan:
                raise EditorialError('Prévia editorial expirada. Confira novamente.', 409)
            plan['workspace_only'] = False
            try:
                result = editorial.save(repository, {'preview_id': item['preview_id'], 'acknowledge_warnings': payload['acknowledge_warnings']})
            finally:
                plan['workspace_only'] = True
            self.promotions.pop(payload['promotion_id'], None)
            return result
