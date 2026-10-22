"""Prepare source-collated table candidates only; never write canonical editions."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib, json, re, difflib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'temporario/revisao-onda1/tabela2644'
SOURCE=Path('temporario/showtrials-metodologia-20261015-141712/original/local/posts-json/posts-page-15.json')
EXPECTED={'ru':'f87c8919467f1409379851f1752ee02bcd2df46c3c9cf92bf66b23ad2f3a5be8','pt':'d03724d9a3b7473dcc8c3ff36e69aa6c4915640667bab1cd9dee72efeea3c50d','en':'9e440cd7806c701f544866a1edb31f27972237fa84cb5397264e28447176c2bc'}
def sha(b):return hashlib.sha256(b).hexdigest()
class Table(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None;self.active=False;self.link=None
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='table':self.active=True
  if not self.active:return
  if tag=='tr':self.row=[]
  if tag in ('td','th'):self.cell={'parts':[],'links':[],'attrs':attrs}
  if self.cell is not None and tag in ('p','br'):self.cell['parts'].append(' ')
  if self.cell is not None and tag=='a':self.link={'href':attrs.get('href'),'parts':[]}
 def handle_data(self,data):
  if self.cell is not None:self.cell['parts'].append(data)
  if self.link is not None:self.link['parts'].append(data)
 def handle_endtag(self,tag):
  if tag=='a' and self.link is not None:
   self.link['label']=''.join(self.link.pop('parts'));self.cell['links'].append(self.link);self.link=None
  if tag in ('td','th') and self.cell is not None:
   self.cell['text']=' '.join(''.join(self.cell.pop('parts')).split());self.row.append(self.cell);self.cell=None
  if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
  if tag=='table':self.active=False

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 post=next(p for p in json.loads((ROOT/SOURCE).read_text()) if p['id']==2644)
 html=post['content']['rendered'];html_hash=sha(html.encode())
 if html_hash!='508f333a3d7007385d625a8ec319ba46b060aab857e3d3fc36656087f4c65a9f':raise ValueError('Source changed')
 table_html=re.search(r'<table\b.*?</table>',html,re.S).group()
 (OUT/'source-table.html').write_text(table_html)
 parser=Table();parser.feed(table_html);rows=parser.rows
 assert len(rows)==24 and all(len(row)==4 for row in rows)
 (OUT/'source-cells.json').write_text(json.dumps({'source':str(SOURCE),'source_html_sha256':html_hash,'rows':rows},ensure_ascii=False,indent=2)+'\n')
 result={'batch_id':'R1-tabelas_imagens-0024','document_id':'showtrials-2644','editions':[],'issues':[],'source_html_sha256':html_hash,'diagnostics':{}}
 for lang in EXPECTED:
  path=Path(f'originais/showtrials/showtrials-2644.{lang}.md');raw=(ROOT/path).read_bytes()
  if sha(raw)!=EXPECTED[lang]:raise ValueError(f'{lang}: canonical changed')
  text=raw.decode();blocks=text.split('\n\n')
  start=next(i for i,b in enumerate(blocks) if b.strip() in ('№№','Nºs','Nos.'))
  last=next(i for i in range(start,len(blocks)-1) if blocks[i].strip() in ('ХАРИТОНОВ','KHARITONOV') and blocks[i+1].strip()=='254')+2
  flattened=blocks[start:last];cells=[];cursor=0
  for r,row in enumerate(rows):
   out=[]
   for c,cell in enumerate(row):
    if not cell['text']:out.append('');continue
    n=2 if r==0 and c==0 else 1
    value='<br>'.join(flattened[cursor:cursor+n]);cursor+=n;out.append(value)
   cells.append(out)
  assert cursor==len(flattened),(lang,cursor,len(flattened))
  for r in range(1,24):
   for c in (0,2,3):
    src=rows[r][c]['text'];val=cells[r][c]
    if re.sub(r'\s','',src)!=re.sub(r'\s','',val):raise ValueError((lang,r,c,src,val))
  if lang=='ru':
   for r in range(24):
    for c in range(4):
     src=rows[r][c]['text'].replace('<','\\<').replace('>','\\>');val=cells[r][c].replace('<br>',' ')
     assert re.sub(r'\s','',src)==re.sub(r'\s','',val),(r,c,src,val)
  table='\n'.join(['| '+' | '.join(cells[0])+' |','| --- | --- | --- | --- |']+['| '+' | '.join(row)+' |' for row in cells[1:]])
  before='\n\n'.join(flattened);assert text.count(before)==1
  candidate=text.replace(before,table,1);candidate_path=OUT/path.name;candidate_path.write_text(candidate)
  (OUT/(path.name+'.diff')).write_text(''.join(difflib.unified_diff(text.splitlines(True),candidate.splitlines(True),fromfile=str(path),tofile=str(candidate_path.relative_to(ROOT)))))
  (OUT/(lang+'-cells.json')).write_text(json.dumps(cells,ensure_ascii=False,indent=2)+'\n')
  prefix,suffix=text.split(before);newprefix,newsuffix=candidate.split(table)
  assert prefix==newprefix and suffix==newsuffix
  headings=re.findall(r'^#{1,6} .+$',text,re.M);assert headings==re.findall(r'^#{1,6} .+$',candidate,re.M)
  result['editions'].append({'document_id':'showtrials-2644','language':lang,'file':str(path),'before_sha256':sha(raw),'candidate':str(candidate_path.relative_to(ROOT)),'candidate_sha256':sha(candidate.encode()),'source_evidence':str((OUT/'source-cells.json').relative_to(ROOT))})
  result['diagnostics'][lang]={'old_table_start_codepoint':len(prefix),'old_table_end_codepoint':len(prefix)+len(before),'new_table_start_codepoint':len(newprefix),'new_table_end_codepoint':len(newprefix)+len(table),'unchanged_suffix_offset_delta':len(table)-len(before),'unchanged_body_block_index_delta':-len(flattened)+1,'before_blocks_blankline':len([b for b in blocks if b.strip()]),'after_blocks_blankline':len([b for b in candidate.split('\n\n') if b.strip()]),'replaced_blocks':len(flattened),'table_blocks_after':1,'start_block_zero_based':start,'heading_count_preserved':len(headings),'prefix_bytes_unchanged':len(prefix.encode()),'suffix_bytes_unchanged':len(suffix.encode()),'all_table_cells':96,'table_rows_including_header':24,'source_empty_cells':sum(not c['text'] for row in rows for c in row),'cell_texts_preserved':True,'numeric_cells_source_collated':True,'source_anomalies_preserved':['TARASOV last-word page807','SAKHOV interrogation source<a>21</a>1; inherited Markdown21 1 retained'],'cell_evidence':str((OUT/(lang+'-cells.json')).relative_to(ROOT))}
 result['issues']=[{'key':'showtrials-2644:tabelas_linearizadas','outcome':'corrigido_com_evidencia','evidence':'24rows/96cells; RU literal source checked cell-by-cell; PT/EN numeric columns checked against RU source and existing translated cell texts preserved; all prefix/suffix and headings unchanged.','next_action':'Integrate only after verifying persistent anchors and canonical hashes; paragraph ordinals shift and session marks inside old cells may not resolve.'},{'key':'showtrials-2644:links_nao_reconstruidos','outcome':'parcial','evidence':'1022 source links catalogued in diagnostic, including table hyperlinks. Table content restored but destinations not restored or individually checked in this structural correction.','next_action':'Sequential links pass on post-integration hashes; distinguish source-internal witnesses and notes from outbound biography links.'}]
 result['limitations']=['Source211 is split in current Markdown as21 1: retained literal inherited typography, no numeric emendation.','Parallel study pairs are not manufactured; only same table block grouping across three editions.','Reader table study rendering remains current application behavior; no browser run.','SessionStorage inaccessible from filesystem: fingerprint fallback can resolve unchanged later blocks; old short numeric table marks can falsely match identical numbers elsewhere and must not be migrated blindly.']
 (OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result['diagnostics'],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
