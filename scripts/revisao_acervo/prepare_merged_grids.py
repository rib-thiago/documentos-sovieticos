#!/usr/bin/env python3
"""Reconstrução de grades mescladas com continuidade e origem explícitas.

Fonte e texto devem coincidir integralmente na ordem; não altera o acervo.
"""
import difflib,json,re
from pathlib import Path
from bs4 import BeautifulSoup
from prepare_tables_a import normmap,sha
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'temporario/revisao-onda1/estruturas-root'
IDS=[4583,4584,4771,4791,4796,4828,5660,8849,2537]


def one(before,html):
 tables=BeautifulSoup(html,'html.parser').select('table');normalized,positions=normmap(before);cursor=0;replacements=[];proof=[]
 for ti,table in enumerate(tables,1):
  if table.find_parent('table'):raise ValueError('Tabela aninhada')
  rows=table.find_all('tr');sourcecells=[c for row in rows for c in row.find_all(['td','th'],recursive=False)];sequence=''.join(normmap(c.get_text('',strip=False))[0]for c in sourcecells);start=normalized.find(sequence,cursor)
  if not sequence or start<0 or normalized.find(sequence,start+1)>=0:raise ValueError('Tabela sem correspondência única integral')
  end=start+len(sequence);a=positions[start];b=positions[end-1]+1;at=start;grid={};cells=[]
  for ri,row in enumerate(rows):
   ci=0
   for c in row.find_all(['td','th'],recursive=False):
    while (ri,ci)in grid:ci+=1
    rs,cs=int(c.get('rowspan',1)),int(c.get('colspan',1));raw=c.get_text('',strip=False);needle=normmap(raw)[0]
    if rs<1 or cs<1 or ri+rs>len(rows):raise ValueError('Mescla inconsistente na fonte')
    if normalized[at:at+len(needle)]!=needle:raise ValueError('Célula não corresponde')
    if needle:
     s=positions[at];e=positions[at+len(needle)-1]+1
     if s and before[s-1]=='\\':s-=1
     value=re.sub(r'\s+',' ',before[s:e]).strip()
    else:s=e=None;value=''
    if normmap(value)[0]!=needle or re.search(r'(?<!\\)\|',value):raise ValueError('Texto requer cotejo próprio')
    at+=len(needle);cell={'row':ri+1,'column':ci+1,'rowspan':rs,'colspan':cs,'source_text':raw,'candidate_text':value,'before_start':s,'before_end':e,'text_equal':True};cells.append(cell)
    for rr in range(ri,ri+rs):
     for cc in range(ci,ci+cs):
      if (rr,cc)in grid:raise ValueError('Sobreposição de mesclas')
      grid[rr,cc]=cell
    ci+=cs
  if at!=end:raise ValueError('Texto não atribuído')
  width=max(c for r,c in grid)+1;rendered=[]
  for ri in range(len(rows)):
   row=[]
   for ci in range(width):
    cell=grid.get((ri,ci))
    value=''if cell is None else cell['candidate_text']if (ri+1,ci+1)==(cell['row'],cell['column'])else f"↳ L{cell['row']}C{cell['column']}"
    row.append(value)
   rendered.append('| '+' | '.join(row)+' |')
  tablemd='| '+' | '.join(['']*width)+' |\n| '+' | '.join(['---']*width)+' |\n'+'\n'.join(rendered)
  legend='\n\n*Nota editorial de estrutura: ↳ LxCy indica continuação da célula mesclada cuja origem está na linha x, coluna y da tabela-fonte; a primeira linha da fonte vem após o cabeçalho vazio de apresentação. Os valores e campos vazios foram preservados.*'
  replacements.append((a,b,tablemd+legend));proof.append({'table':ti,'rows':len(rows),'columns':width,'source_cells':cells,'grid_covered_positions':len(grid),'before_start':a,'before_end':b,'method':'Cada célula física aparece uma vez; continuação indica coordenada de origem, sem replicar ou inventar valores.'});cursor=end
 after=before
 for a,b,repl in reversed(replacements):after=after[:a]+repl+after[b:]
 return after,proof


def main():
 lookup={p['chave']:p for p in json.load(open(ROOT/'docs/revisao-markdown/diagnostico-geral/proposals-showtrials.json'))['proposals']};manifest=json.load(open(ROOT/'temporario/revisao-onda1/baseline/manifest.json'));editions={e['id']:e for e in json.load(open(ROOT/'data/catalog/editions.json'))};summary=[]
 for n in IDS:
  uid='showtrials-'+str(n);key=uid+':tabelas_linearizadas';task=next(b for b in manifest['batches']if any(d['id']==uid for d in b['documents']));folder=OUT/task['id'];ev=lookup[key]['evidencia'];post=next(p for p in json.load(open(ROOT/ev['source_json']))if p['id']==n);html=post['content']['rendered'];edition=editions[uid+':ru'];before=(ROOT/edition['file']).read_text()
  if sha(html.encode())!=ev['source_html_sha256']or sha(before.encode())!=edition['sha256']:raise ValueError('Fonte/versão mudou')
  try:after,proof=one(before,html)
  except ValueError as exc:summary.append({'id':uid,'prepared':False,'reason':str(exc)});continue
  candidate=folder/(uid+'.ru.md');candidate.write_text(after);audit=folder/(uid+'-merged-grid.json');audit.write_text(json.dumps({'source':ev,'tables':proof,'outside_spans_unchanged':True,'editorial_legend_added':True},ensure_ascii=False,indent=2)+'\n');(folder/(uid+'.diff')).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True))))
  rp=folder/'result.json';result=json.load(open(rp));result['editions']=[e for e in result['editions']if e['document_id']!=uid];result['issues']=[i for i in result['issues']if i['key']!=key]
  result['editions'].append({'document_id':uid,'language':'ru','file':edition['file'],'before_sha256':edition['sha256'],'candidate':str(candidate.relative_to(ROOT)),'candidate_sha256':sha(after.encode()),'source_evidence':str(audit.relative_to(ROOT))})
  result['issues'].append({'key':key,'outcome':'corrigido_com_evidencia','evidence':str(audit.relative_to(ROOT)),'next_action':'Grade reconstruída com indicação editorial explícita das origens de mesclas; os números e palavras da fonte não foram emendados.'});rp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');summary.append({'id':uid,'prepared':True,'tables':len(proof),'physical_cells':sum(len(p['source_cells'])for p in proof)})
 (OUT/'merged-preparacao.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':main()
