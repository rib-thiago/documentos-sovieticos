"""Vínculos locais entre documentos, páginas e passagens; sem publicação implícita."""
from __future__ import annotations
import copy
import hashlib
import json
import secrets
import time
from . import catalog as model
from .editorial import EditorialError, text
from .pdf_sources import now
from .pdf_operations import page_selection
from .translations import split_export_headers


def sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


class PDFLinks:
    def __init__(self, sources):
        self.sources = sources
        self.previews = {}
        self.projects = self.workspace = None
        with sources.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS pdf_document_links (
                    id TEXT PRIMARY KEY, document_id TEXT NOT NULL, project_id TEXT NOT NULL,
                    revision INTEGER NOT NULL, data TEXT NOT NULL, updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS pdf_document_link_history (
                    id TEXT PRIMARY KEY, link_id TEXT NOT NULL, created_at TEXT NOT NULL,
                    before_state TEXT NOT NULL, after_state TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS pdf_links_document ON pdf_document_links(document_id,project_id);
            ''')

    def context(self, repository, document_id, project_id='', *, writing=False, source_id=None):
        if not isinstance(document_id, str) or not any(d['id'] == document_id for d in repository.catalog['documents']):
            raise EditorialError('Documento não encontrado', 404)
        if not isinstance(project_id, str):
            raise EditorialError('Contexto de projeto inválido')
        if project_id:
            project = self.projects.get(project_id)
            if document_id not in project['document_ids']:
                raise EditorialError('O documento não pertence a este projeto', 409)
            if writing and project['archived']:
                raise EditorialError('Reabra o projeto antes de alterar os vínculos', 409)
            if writing and source_id and source_id not in project['source_ids']:
                raise EditorialError('Vincule esta fonte PDF ao projeto antes de associar suas páginas', 409)

    def edition(self, repository, state, language):
        if language not in ('ru', 'pt', 'en'):
            raise EditorialError('Idioma inválido')
        edition_id = state['document_id']+':'+language
        if state['project_id']:
            result = self.workspace.edition(repository, state['project_id'], edition_id)
            content = result['content']
        else:
            edition = next((e for e in repository.catalog['editions'] if e['id'] == edition_id), None)
            if not edition:
                raise EditorialError('Versão não encontrada', 404)
            raw = model.content_bytes(repository.root, edition['file'])
            if model.sha256(raw) != edition['sha256']:
                raise EditorialError('A edição mudou fora do painel. Confira e reinicie o backend.', 409)
            content = raw.decode('utf-8')
        return split_export_headers(content)['body']

    def get(self, link_id):
        if not isinstance(link_id, str):
            raise EditorialError('Vínculo inválido')
        with self.sources.db() as db:
            row = db.execute('SELECT * FROM pdf_document_links WHERE id=?', (link_id,)).fetchone()
        if not row:
            raise EditorialError('Vínculo não encontrado', 404)
        return {'id': row['id'], 'revision': row['revision'], 'updated_at': row['updated_at'], **json.loads(row['data'])}

    def listing(self, repository, params):
        if set(params)-{'document', 'project', 'source'}:
            raise EditorialError('Filtro de vínculos inválido')
        document, project, source = params.get('document'), params.get('project', ''), params.get('source')
        if not document and not source:
            raise EditorialError('Escolha documento ou fonte')
        if document:
            self.context(repository, document, project)
        if source:
            self.sources.source(source)
        query, values = 'SELECT id FROM pdf_document_links WHERE project_id=?', [project]
        if document:
            query += ' AND document_id=?'; values.append(document)
        with self.sources.db() as db:
            ids = [r[0] for r in db.execute(query+' ORDER BY updated_at DESC', values)]
        items = []
        for link_id in ids:
            item = self.get(link_id)
            if source and item['source_id'] != source:
                continue
            self.context(repository, item['document_id'], project)
            with self.sources.db() as db:
                source_row = db.execute('SELECT filename,metadata FROM pdf_sources WHERE id=?', (item['source_id'],)).fetchone()
            item['source_title'] = (json.loads(source_row['metadata']).get('title') or source_row['filename']) if source_row else item['source_id']
            bodies = {}
            for anchor in item['anchors']:
                language = anchor['language']
                if language not in bodies:
                    try:
                        bodies[language] = sha(self.edition(repository, item, language))
                    except (EditorialError, model.CatalogError, UnicodeError):
                        bodies[language] = None
                anchor['stale_text'] = bodies[language] != anchor['body_sha256']
                with self.sources.db() as db:
                    page = db.execute('SELECT revision FROM pdf_page_reviews WHERE source_id=? AND page_number=?', (item['source_id'], anchor['page_number'])).fetchone()
                anchor['stale_page'] = (page['revision'] if page else 0) != anchor['page_revision']
            items.append(item)
        return {'items': items}

    def history(self, repository, link_id):
        item = self.get(link_id)
        self.context(repository, item['document_id'], item['project_id'])
        with self.sources.db() as db:
            rows = db.execute('SELECT * FROM pdf_document_link_history WHERE link_id=? ORDER BY created_at DESC', (link_id,)).fetchall()
        return {'items': [{**dict(r), 'before_state': json.loads(r['before_state']), 'after_state': json.loads(r['after_state'])} for r in rows]}

    def validate_state(self, repository, state):
        self.context(repository, state['document_id'], state['project_id'], writing=True, source_id=state['source_id'] if state['active'] else None)
        source = self.sources.source(state['source_id'])
        if not source['page_count']:
            raise EditorialError('Aguarde o inventário das páginas', 409)
        if not state['pages'] or len(set(state['pages'])) != len(state['pages']) or any(type(n) is not int or not 1 <= n <= source['page_count'] for n in state['pages']):
            raise EditorialError('Páginas do vínculo inválidas')
        if len(state['anchors']) > 2000:
            raise EditorialError('Limite de 2000 associações por vínculo')
        if any(a['page_number'] not in state['pages'] for a in state['anchors']):
            raise EditorialError('Remova antes as associações das páginas que deseja retirar')
        return source

    def anchor(self, repository, state, payload):
        if not isinstance(payload, dict) or set(payload)-{'unit_id'} != {'language', 'body_sha256', 'quote', 'start', 'end', 'page_number', 'notes'}:
            raise EditorialError('Associação de trecho inválida')
        language = payload['language']
        body = self.edition(repository, state, language)
        start, end = payload['start'], payload['end']
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(body.encode('utf-16-le'))//2:
            raise EditorialError('Limites do trecho inválidos')
        try:
            quote = body.encode('utf-16-le')[start*2:end*2].decode('utf-16-le')
        except UnicodeError as error:
            raise EditorialError('Limites Unicode inválidos') from error
        if payload['body_sha256'] != sha(body) or quote != payload['quote']:
            raise EditorialError('O texto exibido mudou. Atualize o documento antes de associar.', 409)
        if len(quote) > 100000 or not quote.strip():
            raise EditorialError('Trecho vazio ou grande demais')
        page_number = payload['page_number']
        if type(page_number) is not int or page_number not in state['pages']:
            raise EditorialError('Escolha uma página pertencente ao vínculo')
        with self.sources.db() as db:
            page = db.execute('SELECT revision,data FROM pdf_page_reviews WHERE source_id=? AND page_number=?', (state['source_id'], page_number)).fetchone()
        page_state = json.loads(page['data']) if page else {}
        existing = next((a for a in state['anchors'] if a['language'] == language and a['start'] == start and a['body_sha256'] == payload['body_sha256']), None)
        result = {'id': existing['id'] if existing else 'anchor-'+secrets.token_hex(16), **payload,
                  'quote_sha256': sha(quote), 'notes': text(payload['notes'], 4000), 'page_revision': page['revision'] if page else 0,
                  'printed_label': page_state.get('printed_label', ''), 'assertion': 'manual_page_association'}
        if payload.get('unit_id'):
            unit=next((u for u in page_state.get('units',[]) if u['id']==payload['unit_id']),None)
            if not unit:raise EditorialError('A unidade da página mudou. Atualize antes de associar.',409)
            result.update(unit_id=unit['id'],unit_sha256=unit['sha256'],unit_boxes=copy.deepcopy(unit.get('boxes',[])))
        state['anchors'] = [a for a in state['anchors'] if a['id'] != result['id']]+[result]
        return result

    def preview(self, repository, payload):
        if not isinstance(payload, dict):
            raise EditorialError('Pedido inválido')
        action = payload.get('action')
        with self.sources.lock:
            if action == 'create':
                if set(payload) != {'action', 'document_id', 'project_id', 'source_id', 'pages', 'notes'}:
                    raise EditorialError('Campos de vínculo inválidos')
                source = self.sources.source(text(payload['source_id'], 80))
                after = {'document_id': payload['document_id'], 'project_id': payload['project_id'], 'source_id': source['id'], 'source_sha256': source['sha256'],
                         'pages': page_selection(payload['pages'], source['page_count'] or 0), 'notes': text(payload['notes']), 'active': True, 'anchors': []}
                before, revision, link_id = {**copy.deepcopy(after), 'active': False}, 0, 'pdflink-'+secrets.token_hex(16)
            else:
                current = self.get(payload.get('id'))
                if type(payload.get('revision')) is not int or payload['revision'] != current['revision']:
                    raise EditorialError('Vínculo alterado em outra aba. Atualize e refaça a prévia.', 409)
                link_id, revision = current['id'], current['revision']
                before = {k:v for k,v in current.items() if k not in ('id','revision','updated_at')}
                after = copy.deepcopy(before)
                if action == 'update':
                    if type(payload.get('active')) is not bool:
                        raise EditorialError('Informe se o vínculo está ativo')
                    count = self.sources.source(after['source_id'])['page_count'] or 0
                    after.update(pages=page_selection(payload.get('pages', ''), count), notes=text(payload.get('notes')), active=payload['active'])
                elif action == 'anchor':
                    if not after['active']:
                        raise EditorialError('Reative o vínculo antes de associar trechos', 409)
                    self.anchor(repository, after, payload.get('anchor'))
                elif action == 'remove_anchor':
                    if not any(a['id'] == payload.get('anchor_id') for a in after['anchors']):
                        raise EditorialError('Associação não encontrada', 404)
                    after['anchors'] = [a for a in after['anchors'] if a['id'] != payload['anchor_id']]
                elif action == 'restore':
                    record = next((h for h in self.history(repository, link_id)['items'] if h['id'] == payload.get('history_id')), None)
                    if not record:
                        raise EditorialError('Histórico não encontrado', 404)
                    after = record['before_state']
                else:
                    raise EditorialError('Operação de vínculo inválida')
            source = self.validate_state(repository, after)
            # One source/document/context association; avoid accidental duplicate submissions.
            if action == 'create':
                with self.sources.db() as db:
                    for row in db.execute('SELECT data FROM pdf_document_links WHERE document_id=? AND project_id=?', (after['document_id'], after['project_id'])):
                        if json.loads(row['data'])['source_id'] == after['source_id']:
                            raise EditorialError('Esta fonte já está associada ao documento neste contexto. Edite ou reative o vínculo existente.', 409)
            self.previews = {k:v for k,v in self.previews.items() if v[0] > time.monotonic()}
            if len(self.previews) >= 100:
                raise EditorialError('Muitas prévias abertas. Aguarde a expiração.', 409)
            token = secrets.token_urlsafe(24)
            self.previews[token] = (time.monotonic()+900, {'id': link_id, 'revision': revision, 'before': before, 'after': after, 'source_sha256': source['sha256'], 'action': action})
            return {'preview_id': token, 'before': before, 'after': after}

    def save(self, repository, payload):
        with self.sources.lock:
            record = self.previews.get(payload.get('preview_id'))
            if not record or record[0] < time.monotonic():
                raise EditorialError('Prévia expirada. Confira novamente.', 409)
            plan = record[1]
            source = self.validate_state(repository, plan['after'])
            if source['sha256'] != plan['source_sha256']:
                raise EditorialError('A fonte mudou. Confira novamente.', 409)
            if plan['action'] == 'anchor':
                changed = next((a for a in plan['after']['anchors'] if a not in plan['before']['anchors']), None)
                if changed and sha(self.edition(repository, plan['after'], changed['language'])) != changed['body_sha256']:
                    raise EditorialError('A edição mudou depois da prévia. Atualize o documento.', 409)
                if changed:
                    with self.sources.db() as db:
                        page = db.execute('SELECT revision FROM pdf_page_reviews WHERE source_id=? AND page_number=?', (source['id'],changed['page_number'])).fetchone()
                    if (page['revision'] if page else 0) != changed['page_revision']:
                        raise EditorialError('A revisão da página mudou depois da prévia.', 409)
            with self.sources.db() as db:
                current = db.execute('SELECT revision FROM pdf_document_links WHERE id=?', (plan['id'],)).fetchone()
                if (current['revision'] if current else 0) != plan['revision']:
                    raise EditorialError('Vínculo alterado. Refaça a prévia.', 409)
                if not current:
                    rows = db.execute('SELECT data FROM pdf_document_links WHERE document_id=? AND project_id=?', (plan['after']['document_id'],plan['after']['project_id']))
                    if any(json.loads(r[0])['source_id'] == source['id'] for r in rows):
                        raise EditorialError('O vínculo já foi criado. Atualize a lista.', 409)
                db.execute('INSERT INTO pdf_document_link_history VALUES(?,?,?,?,?)', ('linkrev-'+secrets.token_hex(16),plan['id'],now(),json.dumps(plan['before']),json.dumps(plan['after'])))
                db.execute('INSERT OR REPLACE INTO pdf_document_links VALUES(?,?,?,?,?,?)', (plan['id'],plan['after']['document_id'],plan['after']['project_id'],plan['revision']+1,json.dumps(plan['after']),now()))
            del self.previews[payload['preview_id']]
            return self.get(plan['id'])
