#!/usr/bin/env python3
"""Preserva títulos de seção e reconstrói tabelas por grupo da fonte."""
import difflib,json,re
from pathlib import Path
from bs4 import BeautifulSoup
from prepare_tables_a import sha
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'temporario/revisao-onda1/estruturas-root'


def mapped(text):
 ignore={i for m in re.finditer(r'(?m)^#{1,6}[ \t]+',text)for i in range(m.start(),m.end())};out=[];positions=[];i=0
 while i<len(text):
  if i in ignore:i+=1;continue
  if text[i]=='\\'and i+1<len(text)and text[i+1]in r'''!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~''':i+=1
  if not text[i].isspace():out.append(text[i]);positions.append(i)
  i+=1
 return ''.join(out),positions


def main():
 ps=json.load(open(ROOT/'docs/revisao-markdown/diagnostico-geral/proposals-showtrials.json'))['proposals'];m=json.load(open(ROOT/'temporario/revisao-onda1/baseline/manifest.json'));es={e['id']:e for e in json.load(open(ROOT/'data/catalog/editions.json'))}
 for n in [4583,4771]:
  uid='showtrials-'+str(n);key=uid+':tabelas_linearizadas';task=next(b for b in m['batches']if any(d['id']==uid for d in b['documents']));folder=OUT/task['id'];ev=next(p for p in ps if p['chave']==key)['evidencia'];post=next(p for p in json.load(open(ROOT/ev['source_json']))if p['id']==n);html=post['content']['rendered'];before=(ROOT/es[uid+':ru']['file']).read_text();norm,pos=mapped(before);cursor=0;repls=[];proof=[]
  if sha(html.encode())!=ev['source_html_sha256']or sha(before.encode())!=es[uid+':ru']['sha256']:raise ValueError('Fonte mudou')
  for ti,t in enumerate(BeautifulSoup(html,'html.parser').select('table'),1):
   rows=[tr.find_all(['td','th'],recursive=False)for tr in t.find_all('tr')];seq=''.join(mapped(c.get_text('',strip=False))[0]for row in rows for c in row);at=norm.find(seq,cursor)
   if at<0 or norm.find(seq,at+1)>=0:raise ValueError('Fonte não coincide integralmente')
   start=pos[at];end=pos[at+len(seq)-1]+1;line=before.rfind('\n',0,start)+1
   if re.fullmatch(r'#{1,6}[ \t]+',before[line:start]):start=line
   width=max(sum(int(c.get('colspan',1))for c in row)for row in rows);pieces=[];data=[];cells=[];cellpos=at;sections=[]
   def flush():
    if data:
     pieces.append('| '+' | '.join(['']*width)+' |\n| '+' | '.join(['---']*width)+' |\n'+'\n'.join(data));data.clear()
   for ri,row in enumerate(rows):
    values=[]
    for ci,c in enumerate(row):
     needle=mapped(c.get_text('',strip=False))[0]
     if norm[cellpos:cellpos+len(needle)]!=needle:raise ValueError('Célula divergente')
     if needle:
      s=pos[cellpos];e=pos[cellpos+len(needle)-1]+1
      if s and before[s-1]=='\\':s-=1
      value=re.sub(r'\s+',' ',before[s:e]).strip()
     else:value=''
     if mapped(value)[0]!=needle or re.search(r'(?<!\\)\|',value):raise ValueError('Texto de célula não conservado')
     values.append(value);cells.append({'row':ri+1,'column':ci+1,'source':c.get_text('',strip=False),'candidate':value,'colspan':int(c.get('colspan',1)),'equal':True});cellpos+=len(needle)
    if len(row)==1 and int(row[0].get('colspan',1))==width:
     flush();pieces.append('## '+values[0]);sections.append(values[0])
    else:
     if len(row)!=width or any(int(c.get('rowspan',1))!=1 or int(c.get('colspan',1))!=1 for c in row):raise ValueError('Outra mescla requer cotejo')
     data.append('| '+' | '.join(values)+' |')
   flush();repls.append((start,end,'\n\n'.join(pieces)));proof.append({'table':ti,'source_cells':cells,'sections':sections,'columns':width});cursor=at+len(seq)
  after=before
  for a,b,text in reversed(repls):after=after[:a]+text+after[b:]
  oldheads=re.findall(r'(?m)^#{1,6} (.*)$',before);newheads=re.findall(r'(?m)^#{1,6} (.*)$',after)
  if any(h not in newheads for h in oldheads):raise ValueError('Título antigo perdido')
  candidate=folder/(uid+'.ru.md');candidate.write_text(after);audit=folder/(uid+'-sections.json');audit.write_text(json.dumps({'source':ev,'tables':proof,'old_headings':oldheads,'new_headings':newheads,'outside_spans_unchanged':True,'editorial_action':'Linhas de largura total e texto explícito da fonte ficam como títulos de seção; demais células em tabelas separadas, sem perder valores.'},ensure_ascii=False,indent=2)+'\n');(folder/(uid+'.diff')).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True))))
  rp=folder/'result.json';r=json.load(open(rp));r['editions']=[e for e in r['editions']if e['document_id']!=uid];r['issues']=[i for i in r['issues']if i['key']!=key];r['editions'].append({'document_id':uid,'language':'ru','file':es[uid+':ru']['file'],'before_sha256':es[uid+':ru']['sha256'],'candidate':str(candidate.relative_to(ROOT)),'candidate_sha256':sha(after.encode()),'source_evidence':str(audit.relative_to(ROOT))});r['issues'].append({'key':key,'outcome':'corrigido_com_evidencia','evidence':str(audit.relative_to(ROOT)),'next_action':'Títulos explícitos e relações das células preservados; demais motivos são independentes.'});rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(uid,'preparado; títulos',len(oldheads),'→',len(newheads))


if __name__=='__main__':main()
