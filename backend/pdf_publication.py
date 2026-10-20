"""Projeção estática selecionada; preparar/aplicar não executa Git nem publica projetos."""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import subprocess
import sys
import threading
import time
from . import catalog as model
from .editorial import EditorialError
from .pdf_sources import now


class PDFPublication:
    def __init__(self,sources,editorial):
        self.sources,self.editorial=sources,editorial
        self.base=sources.directory/'publications';self.blobs=self.base/'blobs';self.releases=self.base/'releases';self.history=self.base/'history'
        for folder in (self.blobs,self.releases,self.history):folder.mkdir(parents=True,exist_ok=True)
        self.index=sources.root/'data/facsimiles.json';self.pending=self.base/'pending.json';self.lock=threading.RLock()
        self.recover()

    def state(self):
        return json.loads(self.index.read_text()) if self.index.exists() else {'schema_version':1,'links':[]}

    @staticmethod
    def fingerprint(state):return model.sha256(model.json_bytes(state))

    def release_dir(self,release):
        if not isinstance(release,str) or not re.fullmatch(r'release-[a-f0-9]{32}',release):raise EditorialError('Preparação inválida',404)
        return self.releases/release

    def paths(self,state):
        paths=set()
        for item in state['links']:
            paths.add(item['pdf_url']);paths.update(item.get('image_urls',{}).values())
        for path in paths:
            if not re.fullmatch(r'assets/facsimiles/[a-f0-9]{64}\.(?:pdf|png)',path):raise EditorialError('Projeção contém caminho inválido',409)
        return paths

    def validate_layout(self):
        if any(path.is_symlink() for path in (self.index,self.index.parent,self.sources.root/'assets',self.sources.root/'assets/facsimiles')):
            raise EditorialError('A projeção pública não substitui links simbólicos',409)

    def install(self,desired,previous):
        targets=self.paths(desired);old=self.paths(previous)
        self.validate_layout()
        for relative in sorted(targets):
            name=Path(relative).name;blob=self.blobs/name;target=self.sources.root/relative
            if not blob.is_file():raise EditorialError('Backup do arquivo publicado não encontrado: '+name,409)
            with blob.open('rb') as handle:
                if hashlib.file_digest(handle,'sha256').hexdigest()!=name.split('.')[0]:raise EditorialError('Backup do fac-símile foi alterado',409)
            if target.is_symlink():raise EditorialError('O fac-símile de destino é um link simbólico',409)
            if target.exists():
                with target.open('rb') as handle:
                    if hashlib.file_digest(handle,'sha256').hexdigest()!=name.split('.')[0]:raise EditorialError('Arquivo público foi alterado fora da oficina; restaure ou confira antes de continuar',409)
            else:
                target.parent.mkdir(parents=True,exist_ok=True);temp=target.with_suffix(target.suffix+'.partial');shutil.copyfile(blob,temp);os.replace(temp,target)
        if desired.get('absent'):
            self.index.unlink(missing_ok=True)
        else:model.atomic_write(self.index,model.json_bytes(desired))
        for relative in old-targets:
            target=self.sources.root/relative
            if target.is_file():
                with target.open('rb') as handle:matches=hashlib.file_digest(handle,'sha256').hexdigest()==target.stem
                if matches:target.unlink()

    def recover(self):
        if self.pending.exists():
            record=json.loads(self.pending.read_text());self.install(record['before'],record['after']);self.pending.unlink()

    def snapshot(self,repository,ids,include_text):
        items=[];dependencies=[];count=0
        for link_id in ids:
            link=self.sources.links.get(link_id)
            if link['project_id']:raise EditorialError('Vínculos privados de projetos não podem ser publicados. Incorpore e confira no contexto do acervo.',409)
            link=next(i for i in self.sources.links.listing(repository,{'document':link['document_id']})['items'] if i['id']==link_id)
            if not link['active']:raise EditorialError('Reative o vínculo antes de publicá-lo',409)
            if any(a['stale_text'] or a['stale_page'] for a in link['anchors']):raise EditorialError('Reconﬁra as associações desatualizadas antes de publicar',409)
            count+=len(link['pages'])
            if count>200:raise EditorialError('Prepare até 200 páginas por publicação')
            pages=[];page_deps=[]
            for number in link['pages']:
                with self.sources.db() as db:row=db.execute('SELECT revision,data FROM pdf_page_reviews WHERE source_id=? AND page_number=?',(link['source_id'],number)).fetchone()
                review=json.loads(row['data']) if row else {}
                page_deps.append([number,row['revision'] if row else 0])
                if include_text and (not row or review.get('status') not in ('reviewed','blank')):raise EditorialError(f'Página {number}: confira a transcrição ou desmarque sua publicação',409)
                public_review={'printed_label':review.get('printed_label',''),'status':review.get('status','pending'),'text':review.get('text','') if include_text else '', 'units':review.get('units',[]) if include_text else []}
                pages.append({'page_number':number,'revision':row['revision'] if row else 0,'review':public_review})
            edition_hashes={}
            for a in link['anchors']:edition_hashes[a['language']]=a['body_sha256']
            dependencies.append({'id':link_id,'revision':link['revision'],'page_revisions':page_deps,'edition_hashes':edition_hashes})
            # Do not export notes, history, raw OCR, project context or local paths.
            anchors=[{k:v for k,v in a.items() if k not in ('notes','stale_text','stale_page')} for a in link['anchors']]
            items.append({k:copy.deepcopy(link[k]) for k in ('id','revision','document_id','source_id','source_sha256','source_title','pages')})
            items[-1].update(active=True,anchors=anchors,page_snapshots=pages)
        return items,dependencies

    def preview(self,repository,payload):
        if not isinstance(payload,dict):raise EditorialError('Pedido inválido')
        action=payload.get('action');release='release-'+secrets.token_hex(16)
        with self.lock,self.editorial.lock,self.sources.lock:
            before=self.state();self.paths(before)
            plan={'release_id':release,'action':action,'before':before,'before_absent':not self.index.exists(),'expires':time.time()+1800,'created_at':now(),'dependencies':[]}
            if action=='restore':
                name=payload.get('history_id')
                if not isinstance(name,str) or not re.fullmatch(r'pub-[a-f0-9]{32}',name):raise EditorialError('Histórico inválido')
                history=self.history/(name+'.json')
                if not history.is_file():raise EditorialError('Histórico não encontrado',404)
                plan['after']=json.loads(history.read_text())['before']
            else:
                ids=payload.get('link_ids')
                if action not in ('publish','withdraw') or not isinstance(ids,list) or not 1<=len(ids)<=20 or any(not isinstance(i,str) for i in ids) or len(set(ids))!=len(ids):raise EditorialError('Escolha de 1 a 20 vínculos para publicar ou retirar')
                plan['ids']=ids
                if action=='publish':
                    if type(payload.get('include_transcription')) is not bool:raise EditorialError('Escolha se deseja publicar a transcrição revisada')
                    items,deps=self.snapshot(repository,ids,payload['include_transcription']);plan.update(items=items,dependencies=deps,include_transcription=payload['include_transcription'])
                else:
                    if any(i not in {v['id'] for v in before['links']} for i in ids):raise EditorialError('Vínculo não está publicado')
                plan['after']={'schema_version':1,'links':[i for i in before['links'] if i['id'] not in ids]}
            directory=self.release_dir(release);directory.mkdir()
            model.atomic_write(directory/'recipe.json',model.json_bytes(plan))
        if action=='publish':
            process=subprocess.Popen([sys.executable,'-m','backend.pdf_publish_worker',str(self.sources.root),release],cwd=Path(__file__).resolve().parents[1],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            try:process.wait(timeout=360)
            except subprocess.TimeoutExpired:
                self.sources._stop_process(process,signal.SIGKILL);process.wait();raise EditorialError('A preparação excedeu seis minutos. Reduza a seleção e tente novamente.',409)
            finally:self.sources._stop_process(process,signal.SIGKILL)
            if process.returncode or not (directory/'output.json').exists():raise EditorialError('Não foi possível preparar os derivados; confira a fonte, dependências e tamanho da seleção',409)
            plan['after']['links'].extend(json.loads((directory/'output.json').read_text()))
        self.paths(plan['after'])
        if len(model.json_bytes(plan['after']))>16*1024*1024:raise EditorialError('A projeção excede 16 MiB. Reduza transcrições ou a seleção antes de preparar novamente.',413)
        model.atomic_write(directory/'plan.json',model.json_bytes(plan))
        return {'release_id':release,'action':action,'links':[{'id':i['id'],'document_id':i['document_id'],'pages':i['pages'],'pdf_url':i['pdf_url']} for i in plan['after']['links']], 'added_files':sorted(self.paths(plan['after'])-self.paths(before)),'removed_files':sorted(self.paths(before)-self.paths(plan['after'])),'before_count':len(before['links']),'after_count':len(plan['after']['links'])}

    def apply(self,repository,payload):
        if payload.get('confirm') is not True:raise EditorialError('Confirme explicitamente a aplicação da projeção pública local')
        directory=self.release_dir(payload.get('release_id'));path=directory/'plan.json'
        if not path.is_file():raise EditorialError('Preparação não encontrada',404)
        with self.lock,self.editorial.lock,self.sources.lock:
            plan=json.loads(path.read_text())
            if plan.get('applied') or plan['expires']<time.time():raise EditorialError('Preparação expirada ou já aplicada',409)
            if self.fingerprint(self.state())!=self.fingerprint(plan['before']) or self.index.exists()==plan['before_absent']:raise EditorialError('A projeção pública mudou. Prepare novamente.',409)
            if plan['action']=='publish':
                _,deps=self.snapshot(repository,plan['ids'],plan['include_transcription'])
                if deps!=plan['dependencies']:raise EditorialError('Vínculos, texto ou páginas mudaram após a preparação',409)
            # Preserve existing managed binaries in the local recovery store too.
            for relative in self.paths(plan['before']):
                target=self.sources.root/relative;blob=self.blobs/target.name
                if not blob.exists() and target.is_file():shutil.copyfile(target,blob)
            self.validate_layout()
            record={'id':'pub-'+secrets.token_hex(16),'created_at':now(),'before':{**plan['before'],**({'absent':True} if plan['before_absent'] else {})},'after':plan['after'],'action':plan['action']}
            model.atomic_write(self.pending,model.json_bytes(record))
            try:
                self.install(record['after'],record['before'])
                model.atomic_write(self.history/(record['id']+'.json'),model.json_bytes(record))
                self.pending.unlink()
            except Exception:
                self.recover();raise
            plan['applied']=True;model.atomic_write(path,model.json_bytes(plan))
            return {'saved':True,'history_id':record['id'],'files':sorted(self.paths(plan['after']))+['data/facsimiles.json'],'message':'Projeção estática aplicada somente ao acervo local; nenhum commit ou push executado.'}

    def listing(self):
        return {'published':self.state()['links'],'history':[{'id':p.stem,'created_at':json.loads(p.read_text())['created_at']} for p in sorted(self.history.glob('pub-*.json'),reverse=True)]}

    def preview_pdf(self,release,link_id):
        path=self.release_dir(release)/'plan.json'
        if not path.is_file():raise EditorialError('Preparação não encontrada',404)
        plan=json.loads(path.read_text());item=next((i for i in plan['after']['links'] if i['id']==link_id),None)
        if not item:raise EditorialError('Fac-símile não encontrado',404)
        self.paths({'links':[item]})
        return self.blobs/Path(item['pdf_url']).name
