#!/usr/bin/env python3
"""Divisão editorial de fontes já adquiridas; não escreve no acervo canônico."""
from __future__ import annotations
import copy,json,re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup,Tag,Comment
from markdownify import markdownify
from coletar import atomic_json, immutable, sha

WORK=Path('temporario/coletas-quatro/brest')
HASHES={
 'brest-lenin-congresso-sovietes':'af006fff55715160a3fa8b46d9275274cb6f4dd4291560aa4f06983fb251d17d',
 'brest-lenin-pt-sovietes':'fb1d517f24dc5cc8bfb9e69868ec908715835b157dc9c8e8dc5bc7ff9b6edc33',
 'brest-lenin-apr-29':'e58c737f604420242de0022f89014299151180b8ff5c43e15b4762f179b70d5f',
 'brest-trotsky-documentos-governo':'f32e8ca4ec6f42f572e6f94a330a09009c4837ba69af63aa8cd959218477fec0',
 'brest-tratado-avalon':'3005dd3c14c05064ec93843d001ad1de0d5da039c5e704798aa613cca958ecf7',
}
TITLES_EN=['Projeto de resolução sobre a mensagem de Wilson','Relatório sobre a ratificação do tratado de paz, 14 de março de 1918','Resposta ao debate sobre a ratificação do tratado de paz, 15 de março de 1918','Resolução sobre a ratificação do tratado de Brest']
TROTSKY=[
 'Nota aos embaixadores aliados sobre o governo soviético e a proposta de armistício',
 'Declaração sobre a publicação dos tratados secretos',
 'Nota aos representantes de países neutros sobre a abertura das negociações de paz',
 'Resposta à embaixada britânica sobre as propostas soviéticas de paz',
 'Nota aos embaixadores aliados sobre as negociações com as Potências Centrais',
 'Nota ao embaixador romeno sobre os acontecimentos na Bessarábia',
 'Extratos de entrevista à imprensa sobre relações exteriores',
 'Nota ao governo persa sobre a retirada das tropas da Pérsia',
 'Extratos da declaração sobre a Polônia na conferência de Brest-Litovsk',
 'Declaração sobre a retirada da Rússia da guerra, 10 de fevereiro de 1918',
 'Nota ao coronel Robins sobre a posição dos Aliados em caso de rejeição do tratado',
 'Ordem às autoridades militares locais sobre prisioneiros de guerra',
]

def fragment(nodes):
 return ''.join(str(n) for n in nodes if not isinstance(n,Comment))

def clean_markup(html,origin):
 root=BeautifulSoup(html,'html.parser')
 for n in root.select('script,style,nav,footer,map,area,.toplink,.footer,.updat,.link'):
  n.decompose()
 for el in root.select('a[href],img[src]'):
  attr='href' if el.name=='a' else 'src'
  el[attr]=urljoin(origin,el[attr])
 return markdownify(str(root),heading_style='ATX',escape_underscores=False).strip()

def note_groups(soup):
 """Notes: anchored paragraph plus following same-class continuation paragraphs."""
 groups={}
 for a in soup.select('a[id],a[name]'):
  key=a.get('id') or a.get('name')
  if not re.fullmatch(r'(?:fw(?:\d+|\*)|tr\d+)' ,key or ''):continue
  p=a.find_parent('p')
  if not p:raise ValueError('Nota sem parágrafo: '+key)
  nodes=[p]
  for nxt in p.next_siblings:
   if not isinstance(nxt,Tag):continue
   if nxt.name!='p' or set(nxt.get('class',[]))!=set(p.get('class',[])):break
   if nxt.select('a[id],a[name]'):break
   nodes.append(nxt)
  groups[key]=fragment(nodes)
 return groups

def convert(html,soup,origin):
 root=BeautifulSoup(html,'html.parser');groups=note_groups(soup);notes=[];tokens={}
 for a in list(root.select('a[href^="#"]')):
  key=a['href'][1:]
  if key not in groups:continue
  token='BRESTNOTECALL'+str(len(tokens))+'END'
  a.replace_with(root.new_string(token));tokens[token]='[^src-'+key+']'
  if key in notes:continue
  notes.append(key)
 body=clean_markup(str(root),origin)
 for token,value in tokens.items():body=body.replace(token,value)
 defs=[]
 for key in notes:
  note=BeautifulSoup(groups[key],'html.parser')
  for a in list(note.select('a[href^="#"]')):
   if re.fullmatch(r'#(?:bk\d+|r\d+)',a['href']):a.decompose()
  text=clean_markup(str(note),origin)
  defs.append('[^src-'+key+']: '+text.replace('\n','\n    '))
 return body+'\n'+('\n'+'\n\n'.join(defs)+'\n' if defs else ''),notes

def source(unit):
 raw=(WORK/unit['raw']).read_bytes()
 if sha(raw)!=HASHES[unit['id']]:raise ValueError('Fonte mudou: '+unit['id'])
 return BeautifulSoup(raw,'html.parser')

def write(parent,id,title,html,soup,**extra):
 origin=parent['source_url'];content,notes=convert(html,soup,origin);fingerprint=sha(content.encode())
 heads=BeautifulSoup(html,'html.parser').find_all(re.compile('^h[1-6]$'))
 literal=heads[-1].get_text(' ',strip=True) if heads else None
 target=Path('units')/id/(fingerprint+'.'+parent['language']+'.md')
 immutable(WORK/target,content.encode())
 unit=copy.deepcopy(parent);unit.update(id=id,title_pt=title,markdown=str(target),markdown_sha256=fingerprint,ready_for_import=True)
 unit.update(date_literal=None,title_literal=literal,document_type=None)
 unit.update(extra)
 unit['provenance']['date_note']='Data particular da unidade, quando explícita; créditos gerais não usados como data de cada parte.'
 unit['issues']=['Conferência editorial de tradução e cotejo com edição impressa permanecem pendentes.']
 unit['provenance']['round3']={'source_sha256':parent['raw_sha256'],'parent_unit':parent['id'],'boundaries':'Divisão explícita por âncoras/títulos da fonte; notas agrupadas com parágrafos de continuação até a próxima âncora.','footnotes':notes,'shared_credits':'Cabeçalho e créditos gerais da página conservados em cada parte, não tomados como autoria nova.'}
 return unit

def split_lenin(parent,prefix,titles,ids,documents=None):
 s=source(parent);nodes=list(s.body.children);starts=[s.find(id=prefix+str(i)) for i in range(1,len(titles)+1)];indices=[nodes.index(x) for x in starts]
 notes_heading=next(h for h in s.find_all('h3') if h.get_text(strip=True)=='Notes')
 end=nodes.index(notes_heading)
 # Global title, authorship and edition credits before TOC, excluding navigation.
 top=[]
 for node in nodes[:indices[0]]:
  if isinstance(node,Tag) and node.name=='h3' and node.get_text(' ',strip=True) in {'Contents','Table of Contents'}:break
  top.append(node)
 out=[]
 for i,title in enumerate(titles):
  body=fragment(nodes[indices[i]:indices[i+1] if i+1<len(indices) else end])
  extra={'document_id':documents[i]} if documents and documents[i] else {}
  extra.update(title_literal=starts[i].find_next('h3').get_text(' ',strip=True),document_type=('draft_project' if i==0 else 'decree_resolution' if i==3 else 'speech') if prefix=='toc' else 'speech')
  if prefix=='toc':extra['date_literal']=['13 March 1918','14 March 1918','15 March 1918',None][i]
  else:extra['date_literal']='29 April 1918'
  out.append(write(parent,ids[i],title,fragment(top)+body,s,**extra))
 return out

def build():
 payload=json.loads((WORK/'units.json').read_text());units=payload['units'];by={u['id']:u for u in units};new=[]
 # Recover original compound sources after a previous run, without reverting unrelated units.
 for saved in sorted((WORK/'round3'/'history').glob('*.json')):
  for original in json.loads(saved.read_text())['units']:
   if original['id'] in HASHES and original['id'] not in by:by[original['id']]=original
 ids=['brest-lenin-iv-wilson','brest-lenin-iv-relatorio','brest-lenin-iv-resposta','brest-lenin-iv-resolucao']
 new+=split_lenin(by['brest-lenin-congresso-sovietes'],'toc',TITLES_EN,ids,[None,ids[1],None,ids[3]])
 new+=split_lenin(by['brest-lenin-apr-29'],'sec',['Relatório sobre as tarefas imediatas do poder soviético, 29 de abril de 1918','Resposta ao debate sobre as tarefas imediatas do poder soviético, 29 de abril de 1918'],['brest-lenin-apr-29-relatorio','brest-lenin-apr-29-resposta'])
 p=by['brest-lenin-pt-sovietes'];s=source(p);nodes=list(s.body.children)
 starts=[h for h in s.find_all('h2') if h.get_text(strip=True) in {'1','2'}];ix=[nodes.index(x) for x in starts]
 end=next(i for i,n in enumerate(nodes) if isinstance(n,Tag) and n.name=='p' and 'note' in n.get('class',[]))
 # Preserve authorized translation credit, edition and copyright notice in shared prefix.
 top=fragment(nodes[:ix[0]])
 for i,(title,id) in enumerate([(TITLES_EN[1],ids[1]),(TITLES_EN[3],ids[3])]):
  new.append(write(p,id+'-pt',title,top+fragment(nodes[ix[i]:ix[i+1] if i==0 else end]),s,document_id=id,title_literal=starts[i].get_text(' ',strip=True)+' — '+(starts[i].find_next('p').get_text(' ',strip=True)[:180]),date_literal='14 March 1918' if i==0 else None,document_type='speech' if i==0 else 'decree_resolution'))
 p=by['brest-trotsky-documentos-governo'];s=source(p);nodes=list(s.body.children);heads=s.find_all('h4');assert len(heads)==12
 ix=[nodes.index(h) for h in heads]
 end=next(i for i,n in enumerate(nodes) if i>ix[-1] and isinstance(n,Tag) and n.name=='h3')
 for i,title in enumerate(TROTSKY):
  html=fragment(nodes[ix[i]:ix[i+1] if i+1<len(ix) else end]);date_block=heads[i].find_next('p').get_text(' ',strip=True);date_match=re.search(r'\b\d{1,2} [A-Z][a-z]+ 19\d{2}\b',date_block);date=date_match.group(0) if date_match else None
  new.append(write(p,'brest-trotsky-governo-'+str(i+1).zfill(2),title,fragment(nodes[:ix[0]])+html,s,date_literal=date,title_literal=heads[i].get_text(' ',strip=True),document_type='memo_note'))
 p=by['brest-tratado-avalon'];s=source(p);root=s.select_one('.text-properties');nodes=list(root.children)
 start=next(i for i,n in enumerate(nodes) if isinstance(n,Tag) and n.get('class')==['document-title'])
 end=next(i for i,n in enumerate(nodes) if isinstance(n,Tag) and n.find('a',attrs={'name':'art14'}))
 end=next(i for i in range(end+1,len(nodes)) if isinstance(nodes[i],Tag) and nodes[i].name=='div')
 html=fragment(nodes[start:end]);frag=BeautifulSoup(html,'html.parser')
 for n in list(frag.find_all('table')):n.decompose()
 u=write(p,p['id'],'Tratado de paz de Brest-Litovsk — versão inglesa Avalon/FRUS',str(frag),s,original_language=None,document_type=None)
 u['ready_for_import']=False;u['issues']=['Variante inglesa dos 14 artigos; preservar como testemunho textual separado, sem duplicar o tratado já publicado nem substituir sua tradução. Anexos mencionados não constam desta página.']
 u['provenance']['round3']['variant_of']='brest-tratado-marxists';new.append(u)
 # German committee minutes: keep their own language and testimony identity.
 for id in ['brest-central-feb-22-alemao','brest-central-feb-23-alemao']:
  p=by[id];raw=(WORK/p['raw']).read_bytes();s=BeautifulSoup(raw,'html.parser')
  root=s.select_one('#sites-canvas-main-content')
  if root is None:raise ValueError('German content container missing: '+id)
  u=write(p,id,'Reunião do Comitê Central — '+('22' if '22' in id else '23')+' de fevereiro de 1918 — versão alemã',str(root),s,document_type='session_transcript')
  u['ready_for_import']=False
  u['issues']=['Testemunho alemão preparado e separado da navegação; associação documental com intervenções russas/inglesas requer cotejo integral. Não substituir atas completas por discursos de Lenin.']
  u['provenance']['round3']['variant_language']='de'
  new.append(u)
 # Idempotent application with immutable pre-change snapshots; Iskra and other fronts untouched.
 replaced=set(HASHES)
 old=new.copy();newids={u['id'] for u in new}
 kept=[u for u in units if u['id'] not in replaced and u['id'] not in newids]
 snapshot=json.dumps(payload,ensure_ascii=False,indent=2).encode();immutable(WORK/'round3'/'history'/(sha(snapshot)+'.json'),snapshot)
 payload['units']=kept+new;atomic_json(WORK/'units.json',payload)
 report={'replaced_parent_units':sorted(replaced),'prepared':[{'id':u['id'],'language':u['language'],'document_id':u.get('document_id'),'markdown':u['markdown'],'ready':u['ready_for_import'],'notes':u['provenance']['round3']['footnotes']} for u in new]}
 atomic_json(WORK/'round3'/'prepared.json',report)
 print(json.dumps({'new_units':len(new),'ready':sum(u['ready_for_import'] for u in new),'all_units':len(payload['units'])}))
if __name__=='__main__':build()
