"""Incorporação explícita de transcrições revisadas pelos fluxos editoriais existentes."""
import copy
import json
import secrets
import time
from . import catalog as model
from .editorial import EditorialError
from .pdf_operations import page_selection
from .pdf_review import digest
from .pdf_sources import now
from .translations import line_diff


class PDFIncorporation:
    def __init__(self, sources, editorial, workspace):
        self.sources,self.editorial,self.workspace=sources,editorial,workspace
        self.previews={}
        with sources.db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS pdf_incorporations(id TEXT PRIMARY KEY,created_at TEXT,data TEXT,state TEXT,error TEXT)')

    def compose(self, source_id, pages):
        if not isinstance(source_id,str):raise EditorialError('Escolha uma fonte PDF')
        source=self.sources.source(source_id);selected=page_selection(pages,source['page_count'] or 0)
        if len(selected)>200:raise EditorialError('Incorpore até 200 páginas por entrega')
        parts=[];mapping=[];cursor=0;bytes_total=0
        for number in selected:
            page=self.sources.review.page(source_id,number);review=page['review']
            if page['revision']<1 or review['status'] not in ('reviewed','blank'):
                raise EditorialError(f'Confira e salve a página {number} como conferida ou em branco antes de incorporar',409)
            value=review['text'];bytes_total+=len(value.encode('utf-8'))+(2 if parts else 0)
            if bytes_total>4*1024*1024:raise EditorialError('A transcrição selecionada excede 4 MiB. Incorpore em partes.',413)
            mapping.append({'page_number':number,'printed_label':review['printed_label'],'review_revision':page['revision'],'text_sha256':digest(value),'start':cursor,'end':cursor+len(value),'units':copy.deepcopy(review['units'])})
            parts.append(value);cursor+=len(value)+2
        content='\n\n'.join(parts)
        if not content.strip():raise EditorialError('A seleção não contém texto para incorporar')
        provenance={'source_id':source_id,'source_sha256':source['sha256'],'offset_space':'unicode_codepoints','pages':mapping,'content_sha256':digest(content)}
        return content,provenance

    def preview(self, repository, payload):
        with self.editorial.lock,self.sources.lock:
            if not isinstance(payload,dict):raise EditorialError('Pedido inválido')
            mode=payload.get('mode');document=payload.get('document_id');language=payload.get('language');project=payload.get('project_id','')
            if language not in ('ru','pt','en') or mode not in ('create','edition','project'):raise EditorialError('Destino ou idioma inválido')
            document=self.editorial.identifier(document)
            if not isinstance(project,str):raise EditorialError('Contexto de projeto inválido')
            if project and mode!='project':raise EditorialError('No projeto, salve uma versão privada; abra sem projeto para incorporar ao acervo',409)
            content,provenance=self.compose(payload.get('source_id'),payload.get('pages'))
            existing=next((e for e in repository.catalog['editions'] if e['id']==str(document)+':'+language),None)
            replace=False;previous=''
            if mode=='project':
                self.sources.links.context(repository,document,project,writing=True,source_id=provenance['source_id'])
                if not project:raise EditorialError('Escolha um projeto')
                current=self.workspace.edition(repository,project,document+':'+language)
                result=self.workspace.preview(repository,{'project_id':project,'edition_id':document+':'+language,'revision':current['revision'],'content_sha256':current['content_sha256'],'content':content})
                replace=current['has_draft'];previous=current['content']
            elif mode=='create':
                metadata=payload.get('metadata',{})
                if not isinstance(metadata,dict):raise EditorialError('Metadados inválidos')
                source=self.sources.source(provenance['source_id'])
                args={'revision':self.editorial.revision(),'id':document,'title':metadata.get('title',''),'title_pt':metadata.get('title_pt',''),'language':language,'kind':'document','document_type':metadata.get('document_type',''),'date':metadata.get('date',''),'author':metadata.get('author',''),'archive':metadata.get('archive',source['metadata'].get('archive_reference','')),'source_name':'Fonte PDF local revisada','source_url':source['metadata'].get('source_url',''),'source_id':provenance['source_id'],'collection_ids':metadata.get('collection_ids',[]),'filename':str(document)+'.'+language+'.md','content':content}
                result=self.editorial.preview_document_creation(repository,args)
            elif existing:
                current=self.editorial.editable_edition(repository,existing['id']);previous=current['content']
                result=self.editorial.preview_markdown(repository,{'revision':current['revision'],'edition_id':existing['id'],'content_sha256':existing['sha256'],'content':content});replace=True
            else:
                result=self.editorial.preview_translation(repository,{'revision':self.editorial.revision(),'document_id':document,'language':language,'filename':str(document)+'.'+language+'.md','content':content,'title':''})
            underlying=result['preview_id']
            if mode!='project':
                plan=self.editorial.previews.pop(underlying)
                edition=next(e for e in plan['candidate']['editions'] if e['id']==document+':'+language)
                edition['extra']['pdf_transcription']=provenance
                files=dict(plan['files']);files.update(self.editorial.creation_files(repository,plan['candidate']))
                result=self.editorial.store_preview(plan['revision'],plan['candidate'],files,document,plan['changes']+[{'field':'Proveniência PDF e revisão por página','before':None,'after':provenance}],translation=plan.get('translation'),creation=plan.get('creation'))
                # Forward creation/import warnings; wrapper is the only permitted save route.
                plan2=self.editorial.previews[result['preview_id']];plan2['warnings']=plan['warnings'];plan2['incorporation_only']=True
            self.previews={k:v for k,v in self.previews.items() if v['expires']>time.monotonic()}
            token=secrets.token_urlsafe(24)
            self.previews[token]={'expires':time.monotonic()+900,'underlying':result['preview_id'],'mode':mode,'document_id':document,'language':language,'project_id':project,'provenance':provenance,'content':content,'replace':replace}
            return {'preview_id':token,'mode':mode,'document_id':document,'language':language,'project_id':project,'content':content,'provenance':provenance,'replace':replace,'warnings':self.editorial.previews[result['preview_id']]['warnings'] if mode!='project' else result.get('warnings',[]),'diff':line_diff(previous,content)}

    def save(self, repository, payload):
        with self.editorial.lock,self.sources.lock:
            plan=self.previews.get(payload.get('preview_id'))
            if not plan or plan['expires']<time.monotonic():raise EditorialError('Prévia expirada. Confira novamente.',409)
            if plan['replace'] and payload.get('confirm_replace') is not True:raise EditorialError('Confirme explicitamente a substituição da versão existente',409)
            content,provenance=self.compose(plan['provenance']['source_id'],','.join(str(p['page_number']) for p in plan['provenance']['pages']))
            if provenance!=plan['provenance']:raise EditorialError('A revisão das páginas mudou depois da prévia',409)
            receipt_id='inc-'+secrets.token_hex(16)
            receipt={k:v for k,v in plan.items() if k not in ('expires','underlying','content')}
            with self.sources.db() as db:db.execute('INSERT INTO pdf_incorporations VALUES(?,?,?,?,?)',(receipt_id,now(),json.dumps(receipt),'prepared',None))
            try:
                if plan['mode']=='project':
                    result=self.workspace.save(repository,{'preview_id':plan['underlying']})
                else:
                    target=self.editorial.previews.get(plan['underlying'])
                    if not target:raise EditorialError('Prévia editorial expirada',409)
                    target.pop('incorporation_only',None)
                    try:result=self.editorial.save(repository,{'preview_id':plan['underlying'],'acknowledge_warnings':payload.get('acknowledge_warnings') is True})
                    except Exception:
                        if plan['underlying'] in self.editorial.previews:target['incorporation_only']=True
                        raise
            except Exception as error:
                with self.sources.db() as db:db.execute('UPDATE pdf_incorporations SET state=?,error=? WHERE id=?',('failed',str(error),receipt_id))
                raise
            with self.sources.db() as db:db.execute("UPDATE pdf_incorporations SET state='saved',data=? WHERE id=?",(json.dumps({**receipt,'result':result}),receipt_id))
            del self.previews[payload['preview_id']]
            response={'saved':True,'receipt_id':receipt_id,'result':result,'document_id':plan['document_id'],'project_id':plan['project_id']}
            try:self.finish(repository,receipt_id)
            except Exception as error:response['warning']='Texto salvo; falta concluir o vínculo PDF. Use Concluir vínculo: '+str(error)
            return response

    def finish(self, repository, receipt_id):
        with self.editorial.lock,self.sources.lock:
            with self.sources.db() as db:row=db.execute('SELECT * FROM pdf_incorporations WHERE id=?',(receipt_id,)).fetchone()
            if not row:raise EditorialError('Recibo não encontrado',404)
            if row['state']=='completed':return {'completed':True}
            if row['state'] not in ('saved','prepared'):raise EditorialError('Esta tentativa não contém gravação pendente de vínculo',409)
            plan=json.loads(row['data']);provenance=plan['provenance'];project=plan['project_id']
            current=self.sources.links.edition(repository,plan,plan['language'])
            if digest(current)!=provenance['content_sha256']:raise EditorialError('O destino mudou; confira antes de vincular as páginas',409)
            items=self.sources.links.listing(repository,{'document':plan['document_id'],'project':project})['items']
            existing=next((i for i in items if i['source_id']==provenance['source_id']),None)
            pages=[p['page_number'] for p in provenance['pages']]
            if existing:
                required=sorted(set(existing['pages']+pages))
                payload={'action':'update','id':existing['id'],'revision':existing['revision'],'pages':','.join(map(str,required)),'notes':existing['notes'],'active':True}
            else:payload={'action':'create','document_id':plan['document_id'],'project_id':project,'source_id':provenance['source_id'],'pages':','.join(map(str,pages)),'notes':'Transcrição incorporada; recibo '+receipt_id}
            preview=self.sources.links.preview(repository,payload);link=self.sources.links.save(repository,{'preview_id':preview['preview_id']})
            with self.sources.db() as db:db.execute("UPDATE pdf_incorporations SET state='completed',error=NULL,data=? WHERE id=?",(json.dumps({**plan,'link_id':link['id']}),receipt_id))
            return {'completed':True,'link_id':link['id']}

    def receipts(self, source_id):
        with self.sources.db() as db:rows=db.execute('SELECT * FROM pdf_incorporations ORDER BY created_at DESC LIMIT 100').fetchall()
        return {'items':[{**dict(r),'data':json.loads(r['data'])} for r in rows if json.loads(r['data'])['provenance']['source_id']==source_id]}
