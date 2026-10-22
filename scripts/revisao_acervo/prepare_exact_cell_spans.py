#!/usr/bin/env python3
"""Recupera fronteiras de células no interior de blocos, por fonte e posição exatas."""
import difflib,json,re
from pathlib import Path
from bs4 import BeautifulSoup
from prepare_tables_a import normmap,sha
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'temporario/revisao-onda1/estruturas-root'


def main():
 proposals=json.load(open(ROOT/'docs/revisao-markdown/diagnostico-geral/proposals-showtrials.json'));lookup={p['chave']:p for p in proposals['proposals']};manifest=json.load(open(ROOT/'temporario/revisao-onda1/baseline/manifest.json'));editions={e['id']:e for e in json.load(open(ROOT/'data/catalog/editions.json'))}
 for number in [10647,4580,5864,5284]:
  uid='showtrials-'+str(number);key=uid+':tabelas_linearizadas';task=next(b for b in manifest['batches']if any(d['id']==uid for d in b['documents']));folder=OUT/task['id'];ev=lookup[key]['evidencia'];post=next(p for p in json.load(open(ROOT/ev['source_json']))if p['id']==number);html=post['content']['rendered'];tables=BeautifulSoup(html,'html.parser').select('table');edition=editions[uid+':ru'];before=(ROOT/edition['file']).read_text();normalized,positions=normmap(before);cursor=0;repls=[];proof=[]
  if sha(html.encode())!=ev['source_html_sha256']or sha(before.encode())!=edition['sha256']:raise ValueError('Fonte ou texto divergiu')
  for ti,table in enumerate(tables,1):
   if any(int(c.get('rowspan',1))>1 or int(c.get('colspan',1))>1 for c in table.select('td,th')):raise ValueError('Mesclas fora do escopo')
   rows=[[c.get_text('',strip=False)for c in tr.find_all(['td','th'],recursive=False)]for tr in table.find_all('tr')]
   width=max(len(row)for row in rows)
   missing_cells=[{'row':i+1,'trailing_empty_cells':width-len(row)}for i,row in enumerate(rows)if len(row)<width]
   if missing_cells and number!=5284:raise ValueError('Grade irregular')
   rows=[row+['']*(width-len(row))for row in rows]
   sequence=''.join(normmap(c)[0]for row in rows for c in row);start=normalized.find(sequence,cursor)
   if start<0 or normalized.find(sequence,start+1)>=0:raise ValueError('Correspondência não unívoca')
   end=start+len(sequence);begin=positions[start];finish=positions[end-1]+1;cellcursor=start;rendered=[];cells=[]
   for ri,row in enumerate(rows):
    parts=[]
    for ci,cell in enumerate(row):
     needle=normmap(cell)[0]
     if not needle:value='';cs=ce=None
     else:
      if normalized[cellcursor:cellcursor+len(needle)]!=needle:raise ValueError('Célula divergiu')
      cs=positions[cellcursor];ce=positions[cellcursor+len(needle)-1]+1
      if cs and before[cs-1]=='\\':cs-=1
      value=re.sub(r'\s+',' ',before[cs:ce]).strip();cellcursor+=len(needle)
      if normmap(value)[0]!=needle:raise ValueError('Célula modificada')
     if re.search(r'(?<!\\)\|',value):raise ValueError('Pipe requer escape individual')
     parts.append(value);cells.append({'row':ri+1,'column':ci+1,'source_text':cell,'before_start':cs,'before_end':ce,'candidate_cell':value,'text_equal':True})
    rendered.append('| '+' | '.join(parts)+' |')
   if cellcursor!=end:raise ValueError('Texto não atribuído')
   width=len(rows[0]);repl='| '+' | '.join(['']*width)+' |\n| '+' | '.join(['---']*width)+' |\n'+'\n'.join(rendered)
   repls.append((begin,finish,repl));proof.append({'table':ti,'rows':len(rows),'columns':width,'cells':cells,'before_start':begin,'before_end':finish,'implicit_trailing_empty_cells':missing_cells,'empty_cell_policy':'Somente a coluna final de observações sem td na fonte5284 é representada vazia; nenhum valor foi completado.' if missing_cells else None});cursor=end
  after=before
  for a,b,t in reversed(repls):after=after[:a]+t+after[b:]
  path=folder/(uid+'.ru.md');path.write_text(after);audit=folder/(uid+'-cell-spans.json');audit.write_text(json.dumps({'source':ev,'tables':proof,'all_cells_equal':True,'outside_spans_unchanged':True,'method':'Fonte inteira da tabela coincide em uma única posição; limites de cada célula derivados sequencialmente da fonte, sem inferir divisão por parágrafo.'},ensure_ascii=False,indent=2)+'\n');(folder/(uid+'.diff')).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True))))
  rp=folder/'result.json';result=json.load(open(rp));result['editions']=[e for e in result['editions']if e['document_id']!=uid];result['issues']=[i for i in result['issues']if i['key']!=key]
  result['editions'].append({'document_id':uid,'language':'ru','file':edition['file'],'before_sha256':edition['sha256'],'candidate':str(path.relative_to(ROOT)),'candidate_sha256':sha(after.encode()),'source_evidence':str(audit.relative_to(ROOT))})
  result['issues'].append({'key':key,'outcome':'corrigido_com_evidencia','evidence':str(audit.relative_to(ROOT)),'next_action':'Fronteiras das células recuperadas integralmente; links e demais motivos continuam independentes.'});rp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(uid,'preparado',len(tables),'tabelas')


if __name__=='__main__':main()
