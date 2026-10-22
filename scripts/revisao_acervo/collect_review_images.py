#!/usr/bin/env python3
"""Adquire imagens apontadas pelo HTML preservado; não publica nem transcreve."""
import hashlib,json,time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'temporario/revisao-onda1/imagens';OUT.mkdir(parents=True,exist_ok=True)
ps=json.load(open(ROOT/'docs/revisao-markdown/diagnostico-geral/proposals-showtrials.json'))['proposals'];rows=[]
for p in ps:
 if ':imagens_sem_transcricao_confirmada'not in p['chave']or p['chave'].startswith('showtrials-3276:'):continue
 for i,item in enumerate(p['evidencia']['images'],1):
  url=item['src'];full=False
  if p['chave'].startswith('showtrials-5360:') and item.get('srcset'):
   choices=[entry.strip().rsplit(' ',1)for entry in item['srcset'].split(',')]
   url=max(choices,key=lambda x:int(x[1].removesuffix('w')))[0];full=True
  name=p['chave'].split(':')[0]+'-'+str(i)+('-full'if full else '')+Path(urlsplit(url).path).suffix;target=OUT/name;record={'document_id':p['chave'].split(':')[0],'url':url,'original_src':item['src'],'file':str(target.relative_to(ROOT))}
  if urlsplit(url).hostname not in {'showtrials.ru','www.showtrials.ru'}:raise ValueError('Host fora do escopo')
  try:
   if target.exists():data=target.read_bytes();record['cached']=True
   else:
    with urlopen(Request(url,headers={'User-Agent':'DocumentosSovieticosResearchCollector/0.1'}),timeout=15)as r:
     if urlsplit(r.url).hostname not in {'showtrials.ru','www.showtrials.ru'}:raise ValueError('Redirecionamento fora do escopo')
     if not r.headers.get('Content-Type','').startswith('image/'):raise ValueError('Resposta não é imagem')
     data=r.read(25*1024*1024+1)
     if len(data)>25*1024*1024:raise ValueError('Imagem acima de25MiB')
     target.write_bytes(data)
    time.sleep(2)
   record.update(state='acquired',sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
  except Exception as exc:record.update(state='unavailable',error=type(exc).__name__+': '+str(exc))
  rows.append(record);(OUT/'acquisition.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record,ensure_ascii=False),flush=True)
