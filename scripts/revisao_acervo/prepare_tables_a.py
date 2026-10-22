"""Prepare only the assigned three documents, with positional, hash-bound evidence."""
import difflib, hashlib, json, re
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'temporario/revisao-onda1/tabelas-a'
IDS={4504:15,4576:19,4578:19}
def sha(b):return hashlib.sha256(b).hexdigest()
def normmap(s):
 out=[];pos=[];i=0
 while i<len(s):
  if s[i]=='\\' and i+1<len(s) and s[i+1] in r'''!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~''':i+=1
  if not s[i].isspace():out.append(s[i]);pos.append(i)
  i+=1
 return ''.join(out),pos
class Source(HTMLParser):
 def __init__(self,s):
  super().__init__(convert_charrefs=True);self.tables=[];self.table=None;self.row=None;self.cell=None;self.anchor=None;self.anchors=[];self.feed(s)
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='table':self.table=[];self.tables.append(self.table)
  elif t=='tr':self.row=[];self.table.append(self.row)
  elif t in ('td','th'):
   assert not a.get('rowspan') and not a.get('colspan');self.cell=[];self.row.append(self.cell)
  elif t=='a':self.anchor={'href':a.get('href'),'name':a.get('name'),'text':''}
  elif t in ('p','br') and self.cell is not None:self.cell.append('\n')
 def handle_data(self,s):
  if self.cell is not None:self.cell.append(s)
  if self.anchor is not None:self.anchor['text']+=s
 def handle_endtag(self,t):
  if t=='a' and self.anchor is not None:self.anchors.append(self.anchor);self.anchor=None
  if t in ('td','th'):self.cell=None
  if t=='table':self.table=None

def main():
 OUT.mkdir(parents=True,exist_ok=True);result={'batch_id':'R1-tabelas_imagens-0025','editions':[],'issues':[],'preserved_editions':[]}
 for sid,page in IDS.items():
  did=f'showtrials-{sid}';f=f'originais/showtrials/{did}.ru.md';before=(ROOT/f).read_text();beforebytes=(ROOT/f).read_bytes()
  sourcefile=f'temporario/showtrials-metodologia-20261015-141712/original/local/posts-json/posts-page-{page}.json'
  post=next(x for x in json.loads((ROOT/sourcefile).read_text()) if x['id']==sid);html=post['content']['rendered'];src=Source(html)
  (OUT/f'{did}.source.html').write_text(html)
  normalized,positions=normmap(before);cursor=0;replacements=[];links=[]
  for a in src.anchors:
   label,_=normmap(a['text']);start=normalized.find(label,cursor)
   assert label and start>=0,(sid,a,cursor)
   end=start+len(label);bs,be=positions[start],positions[end-1]+1
   href=a['href'];href=post['link']+href if href.startswith('#') else href
   replacement='['+before[bs:be]+'](<'+href+'>)'
   replacements.append((bs,be,replacement));links.append({**a,'resolved_href':href,'before_start':bs,'before_end':be,'text_preserved':before[bs:be]});cursor=end
  linked=before
  for start,end,repl in reversed(replacements):linked=linked[:start]+repl+linked[end:]
  blocks=[m for m in re.finditer(r'\S(?:.*?\S)?(?=\n\s*\n|\s*\Z)',before,re.S)]
  # Source cells must equal the entire ordered old span, ignoring only whitespace/escaping.
  tables=[];table_repl=[];cursor=0
  for ti,table in enumerate(src.tables):
   cells=[''.join(c).strip() for row in table for c in row];assert all(len(row)==3 for row in table)
   sequence=''.join(normmap(c)[0] for c in cells);start=normalized.find(sequence,cursor);assert start>=0,(sid,ti)
   end=start+len(sequence);bs,be=positions[start],positions[end-1]+1
   oldparts=[(m.start(),m.end(),m.group()) for m in blocks if m.start()>=bs and m.end()<=be]
   assert normmap(''.join(x[2] for x in oldparts))[0]==sequence
   rendered=[];cell_evidence=[];pi=0
   for ri,row in enumerate(table):
    r=[]
    for ci,raw in enumerate(row):
     target=normmap(''.join(raw).strip())[0];parts=[];collected='';indices=[]
     while collected!=target:
      s,e,part=oldparts[pi];indices.append(next(i for i,m in enumerate(blocks) if m.start()==s));pi+=1
      collected+=normmap(part)[0];assert target.startswith(collected)
      for ls,le,lr in reversed(replacements):
       if s<=ls<le<=e:part=part[:ls-s]+lr+part[le-s:]
      parts.append(part)
     cell=' '.join(p.replace('\n',' ') for p in parts);r.append(cell)
     cell_evidence.append({'row':ri+1,'column':ci+1,'source_text':''.join(raw).strip(),'before_blocks_0based':indices,'candidate_cell':cell})
    rendered.append('| '+' | '.join(r)+' |')
   # Empty column headings avoid inventing labels or promoting the first data row to a header.
   md='|  |  |  |\n| --- | --- | --- |\n'+'\n'.join(rendered)
   table_repl.append((bs,be,md));tables.append({'table':ti+1,'rows':len(table),'columns':3,'merged_cells':0,'before_start':bs,'before_end':be,'cells':cell_evidence});cursor=end
  # Apply source-coordinate replacements together; links inside cells already included.
  combined=table_repl+[(s,e,r) for s,e,r in replacements if not any(ts<=s<e<=te for ts,te,_ in table_repl)]
  candidate=before
  for s,e,r in sorted(combined,reverse=True):candidate=candidate[:s]+r+candidate[e:]
  candidatepath=OUT/f'{did}.ru.md';candidatepath.write_text(candidate)
  (OUT/f'{did}.before.ru.md').write_bytes(beforebytes)
  (OUT/f'{did}.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),candidate.splitlines(True),fromfile=f,tofile=str(candidatepath.relative_to(ROOT)))))
  cb=[x.strip() for x in re.split(r'\n\s*\n',candidate) if x.strip()]
  mapping=[]
  # Every original block belongs to exactly one new block: either table or same prose.
  old_to_new={};newi=0;oldi=0
  while oldi<len(blocks):
   m=blocks[oldi];t=next((t for t in tables if t['before_start']==m.start()),None)
   if t:
    grouped=[i for i,b in enumerate(blocks) if t['before_start']<=b.start() and b.end()<=t['before_end']]
    for i in grouped:old_to_new[i]=newi
    oldi=grouped[-1]+1
   else:old_to_new[oldi]=newi;oldi+=1
   newi+=1
  assert newi==len(cb),(sid,newi,len(cb))
  evidence={'source_json':sourcefile,'source_html_sha256':sha(html.encode()),'source_url':post['link'],'tables':tables,'links':links,'all_cells_cotejadas':True,'method':'Cada célula cotejada com seus blocos canônicos; texto literal conservado, normalização somente de whitespace/escapes; relações de3colunas conferidas com HTML.','blocks_before':len(blocks),'blocks_after':len(cb),'old_to_new_block_0based':old_to_new,'internal_fragments':'Links de notas/restornos preservados como URL absoluta da fonte; não introduzidos IDs HTML desabilitados pelo leitor.'}
  ep=OUT/f'{did}.evidence.json';ep.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
  result['editions'].append({'document_id':did,'language':'ru','file':f,'before_sha256':sha(beforebytes),'candidate':str(candidatepath.relative_to(ROOT)),'candidate_sha256':sha(candidate.encode()),'source_evidence':str(ep.relative_to(ROOT)),'blocks_before':len(blocks),'blocks_after':len(cb),'integration_risk':'IDs e marcadores por índice mudam; app.js zipBlocks alinha por índice; PT/EN4504 ficam preservados e desalinhados. Exige migração/controle do integrador.'})
  for kind in ['tabelas_linearizadas','links_nao_reconstruidos']:
   result['issues'].append({'key':did+':'+kind,'outcome':'parcial' if sid==4576 and kind=='links_nao_reconstruidos' else 'corrigido_com_evidencia','evidence':str(ep.relative_to(ROOT)),'next_action':'Integrar somente com proteção de anotações, marcadores e alinhamento; fragmentos de notas usam destino externo original.'})
  if sid==4504:
   for lang in ['pt','en']:
    path=ROOT/f'originais/showtrials/{did}.{lang}.md';text=path.read_text();parts=[m for m in re.finditer(r'\S(?:.*?\S)?(?=\n\s*\n|\s*\Z)',text,re.S)]
    assert len(parts)==62
    # Read/cotejo confirms thirteen explicitly numbered fields, three blocks each,
    # identical field boundaries in both translations. No words are translated here.
    assert [parts[3+3*i].group() for i in range(13)]==[str(i)+'.' for i in range(1,14)]
    rows=['| '+' | '.join(parts[3+3*i+j].group() for j in range(3))+' |' for i in range(13)]
    replacement='|  |  |  |\n| --- | --- | --- |\n'+'\n'.join(rows)
    edited=text[:parts[3].start()]+replacement+text[parts[41].end():]
    target=OUT/f'{did}.{lang}.md';target.write_text(edited);(OUT/f'{did}.before.{lang}.md').write_bytes(path.read_bytes())
    (OUT/f'{did}.{lang}.diff').write_text(''.join(difflib.unified_diff(text.splitlines(True),edited.splitlines(True),fromfile=str(path.relative_to(ROOT)),tofile=str(target.relative_to(ROOT)))))
    ev={'source_evidence':str(ep.relative_to(ROOT)),'boundary_evidence':'Thirteen numbered1–13 biographical fields match RU categories in source order; each has number, field label, answer. All62prose blocks read; blocks3..41 form39cells.','cells':[{'row':i+1,'cells':[parts[3+3*i+j].group() for j in range(3)]} for i in range(13)],'all_words_unchanged':True,'blocks_before':62,'blocks_after':24,'old_to_new_block_0based':old_to_new,'links_not_transferred':True}
    evpath=OUT/f'{did}.{lang}.evidence.json';evpath.write_text(json.dumps(ev,ensure_ascii=False,indent=2)+'\n')
    result['editions'].append({'document_id':did,'language':lang,'file':str(path.relative_to(ROOT)),'before_sha256':sha(path.read_bytes()),'candidate':str(target.relative_to(ROOT)),'candidate_sha256':sha(edited.encode()),'source_evidence':str(evpath.relative_to(ROOT)),'blocks_before':62,'blocks_after':24,'integration_risk':'Número de blocos migra62→24; três idiomas têm limites equivalentes por cotejo de campos, não por simples contagem.'})
    result['editions'][0]['integration_risk']='Índices migram62→24; candidatos PT/EN também estruturados por fronteiras inequívocas, preservando palavras.'
 (OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps([{'id':e['document_id'],'before':e['blocks_before'],'after':e['blocks_after']} for e in result['editions']]))
if __name__=='__main__':main()
