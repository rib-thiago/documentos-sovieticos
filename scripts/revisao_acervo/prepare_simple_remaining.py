#!/usr/bin/env python3
"""Preparar apenas tabelas sem mesclas com células localizadas integralmente.

Recusa correspondência parcial, fronteiras de parágrafo ambíguas e traduções
que exigiriam pareamento inferido. Não altera o acervo nem a fila.
"""
import difflib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from prepare_tables_a import normmap,sha
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'temporario/revisao-onda1/estruturas-root'
BASE=ROOT/'temporario/revisao-onda1/baseline'


def prepare(ident, source, before):
 soup=BeautifulSoup(source,'html.parser');tables=soup.select('table')
 if not tables:return None,'Sem tabela na fonte',[]
 if any(t.find_parent('table')for t in tables):return None,'Tabela aninhada exige cotejo específico',[]
 if any(int(c.get('rowspan',1))>1 or int(c.get('colspan',1))>1 for t in tables for c in t.select('td,th')):return None,'Mesclas exigem representação explícita e cotejo próprio',[]
 normalized,positions=normmap(before);blocks=list(re.finditer(r'\S(?:.*?\S)?(?=\n\s*\n|\s*\Z)',before,re.S));cursor=0;replacements=[];evidence=[]
 for number,t in enumerate(tables,1):
  rows=[[c.get_text('',strip=False).strip()for c in row.find_all(['td','th'],recursive=False)]for row in t.find_all('tr')]
  if not rows or not rows[0] or len({len(r)for r in rows})!=1:return None,'Grade irregular exige cotejo próprio',[]
  cells=[c for r in rows for c in r];sequence=''.join(normmap(c)[0]for c in cells)
  if not sequence:return None,'Tabela vazia',[]
  start=normalized.find(sequence,cursor)
  if start<0:return None,'Células não coincidem integralmente com candidato atual',[]
  if normalized.find(sequence,start+1)>=0:return None,'Texto da tabela ocorre mais de uma vez',[]
  end=start+len(sequence);bs,be=positions[start],positions[end-1]+1
  old=[m for m in blocks if m.start()>=bs and m.end()<=be]
  if normmap(''.join(m.group()for m in old))[0]!=sequence:return None,'Limites de célula cortam blocos existentes',[]
  cell_evidence=[];rendered=[];pi=0
  for ri,row in enumerate(rows):
   rendered_cells=[]
   for ci,raw in enumerate(row):
    target=normmap(raw)[0];collected='';parts=[]
    while collected!=target:
     if pi>=len(old):return None,'Célula ultrapassa blocos disponíveis',[]
     part=old[pi].group();pi+=1;collected+=normmap(part)[0]
     if not target.startswith(collected):return None,'Divisão entre células ambígua',[]
     parts.append(part)
    text=' '.join(x.replace('\n',' ')for x in parts)
    if re.search(r'(?<!\\)\|',text):return None,'Pipe literal precisa de tratamento individual',[]
    rendered_cells.append(text);cell_evidence.append({'row':ri+1,'column':ci+1,'source':raw,'candidate':text,'literal_normalized_equal':normmap(text)[0]==target})
   rendered.append('| '+' | '.join(rendered_cells)+' |')
  if pi!=len(old):return None,'Bloco não atribuído a célula',[]
  width=len(rows[0]);md='| '+' | '.join(['']*width)+' |\n| '+' | '.join(['---']*width)+' |\n'+'\n'.join(rendered)
  replacements.append((bs,be,md));evidence.append({'table':number,'rows':len(rows),'columns':width,'before_start':bs,'before_end':be,'old_blocks':len(old),'cells':cell_evidence})
  cursor=end
 after=before
 for a,b,repl in reversed(replacements):after=after[:a]+repl+after[b:]
 return after,None,evidence


def main():
 manifest=json.load(open(BASE/'manifest.json'));diagnostic=json.load(open(ROOT/'docs/revisao-markdown/diagnostico-geral/proposals-showtrials.json'));lookup={p['chave']:p for p in diagnostic['proposals']};editions=json.load(open(ROOT/'data/catalog/editions.json'));rows=list(__import__('csv').DictReader(open(BASE/'queue.csv')));issues={r['chave']:r for r in rows};report=[]
 for batch in manifest['batches']:
  if batch['wave']!=1 or batch['family']!='tabelas_imagens' or batch['id']in {'R1-tabelas_imagens-0024','R1-tabelas_imagens-0025'}:continue
  folder=OUT/batch['id'];folder.mkdir(parents=True,exist_ok=True);result={'batch_id':batch['id'],'editions':[],'issues':[]};findings=[]
  for doc in batch['documents']:
   ident=doc['id'];key=ident+':tabelas_linearizadas'
   if key not in issues:continue
   proposal=lookup[key];ev=proposal['evidencia'];post=next(p for p in json.load(open(ROOT/ev['source_json']))if p['id']==int(ident.split('-')[1]));source=post['content']['rendered']
   if sha(source.encode())!=ev['source_html_sha256']:raise ValueError('Fonte divergente')
   edition=next(e for e in editions if e['document_id']==ident and e['language']=='ru');before=(ROOT/edition['file']).read_text()
   if sha((ROOT/edition['file']).read_bytes())!=edition['sha256']:raise ValueError('Canônico divergente')
   after,reason,evidence=prepare(ident,source,before)
   other=[e for e in editions if e['document_id']==ident and e['language']!='ru']
   if after and other:
    reason='Há traduções; preparar estrutura correspondente por cotejo antes de alterar RU';after=None
   finding={'document_id':ident,'reason_retained':reason,'source_html_sha256':ev['source_html_sha256'],'source_json':ev['source_json'],'canonical_sha256':edition['sha256'],'tables':evidence}
   findings.append(finding);report.append({'batch_id':batch['id'],'id':ident,'prepared':bool(after),'reason':reason,'tables':len(evidence)})
   if not after:continue
   file=folder/(ident+'.ru.md');file.write_text(after)
   (folder/(ident+'.before.ru.md')).write_text(before)
   (folder/(ident+'.diff')).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True))))
   result['editions'].append({'document_id':ident,'language':'ru','file':edition['file'],'before_sha256':edition['sha256'],'candidate':str(file.relative_to(ROOT)),'candidate_sha256':sha(after.encode()),'source_evidence':str((folder/'cotejo.json').relative_to(ROOT))})
   result['issues'].append({'key':key,'outcome':'corrigido_com_evidencia','evidence':{'audit':str((folder/'cotejo.json').relative_to(ROOT)),'finding':'Todas as células localizadas e comparadas na ordem; apenas estrutura de tabela modificada, prefixos e sufixos preservados. Cabeçalhos vazios editoriais não promovem primeiro registro a título.'},'next_action':'Nenhuma perda de relação entre células permanece nesta tabela simples; demais motivos continuam independentes.'})
  (folder/'cotejo.json').write_text(json.dumps(findings,ensure_ascii=False,indent=2)+'\n')
  if result['editions']:(folder/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 (OUT/'preparacao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
