#!/usr/bin/env python3
"""Prepara títulos explicitamente selecionados no HTML; não altera acervo/fila."""
import csv,difflib,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'temporario/revisao-onda4/secoes'
def sha(b):return hashlib.sha256(b).hexdigest()
def visible(s):
 s=re.sub(r'!?\[([^\]]*)\]\([^\n]*?\)',r'\1',s)
 s=re.sub(r'\\([!"#$%&\'()*+,./:;<=>?@\[\]^_`{|}~\-])',r'\1',s)
 return ''.join(s.split())
# Indices refer to the full preserved HTML inventory, not inferred word patterns.
SELECTION={
4810:{0:2,1:3,2:3,3:3,4:3,5:3,6:2,11:3},
4811:{0:2,4:3,5:3,6:3,7:2,8:2},
2485:{i:(2 if i%2==0 else 3) for i in range(10)},
2487:{**{i:2 for i in [0,13,23,25,33]},**{i:3 for i in [1,14,24,26,34]},**{i:4 for i in [3,7,8,9,10,12,15,19,20,21,22,28,32,36]}},
2488:{**{i:2 for i in [0,6,20,30,36,43,45]},**{i:3 for i in [2,3,8,10,11,12,13,14,15,16,17,18,19,22,24,25,26,27,28,29,32,34,35,38,39,40,41,42]}},
4203:{i:2 for i in [11,13,15,17,19]},
8164:{0:2,1:2,2:3,4:3,5:3,6:3,7:3,8:3,9:3},
6762:{2:2,3:3,4:3,5:3,6:3,7:3,8:3,9:3,10:2},
8623:{i:2 for i in range(2,8)},
}
# 7995 includes repeated separator paragraphs, so choose by exact explicit label.
SPECIAL7995={'1.':2,'Глава II.':2,'ВЫДЕРЖКИ':2,'3. ГОСУДАРСТВО.':3,'4. О ПЕРЕХОДЕ К НОВОЙ СИСТЕМЕ.':3}
NOTES={4810:'Relatório e resolução do plenário: cinco grupos acusatórios são títulos literais do documento, não fatos estabelecidos pelo editor.',4811:'Duas sessões de 6/7 de junho e palavras finais têm títulos próprios; a numeração 1/4/5 da fonte foi mantida sem inventar 2/3.',2485:'Cinco recortes do Pravda: data/publicação no nível 2 e título do artigo no nível 3; ocorrências repetidas conservadas em ordem.',2487:'Cinco recortes da Montreal Gazette: publicação/data, manchete e entretítulos distinguidos; linhas finas, assinatura e agência mantidas em prosa.',2488:'Recortes de jornal: sete manchetes e entretítulos tipograficamente explícitos; falas em negrito não promovidas a títulos.',4203:'Informe e quatro textos jornalísticos recebem entradas próprias; destinatários e marcas de sigilo permanecem prosa.',8164:'Roteiro de Bukharin: introdução, parte I e rubricas temáticas expressas; não transforma tópicos comuns em capítulos inventados.',6762:'Minuta de acusação: títulos de hierarquia equivalente preservam simultaneamente numeração romana e versões em chaves/colchetes. Não se decide qual versão substitui a outra; nenhum sinal é removido.',7995:'Excertos: números isolados e separadores não são convertidos indiscriminadamente; apenas 1, capítulo II, bloco de excertos e títulos temáticos 3/4 explícitos. A sequência parcial é preservada.',8623:'Carta com seções centralizadas 1,2,3,4,6,7: marcação respeita os seis limites literais. A ausência do 5 é da fonte, não foi completada.'}
def main():
 inv=json.load(open(OUT/'inventory.json'));manifest=json.load(open(ROOT/'temporario/revisao-onda4/baseline/manifest.json'));bydoc={d['id']:(b,d)for b in manifest['batches']for d in b['documents']};results={};summary=[]
 for n in list(SELECTION)+[7995]:
  uid=f'showtrials-{n}';item=next(x for x in inv if x['id']==uid)
  if item['excluded_link_owner']:raise ValueError('Documento reservado aos links')
  b,d=bydoc[uid];ed=next(e for e in d['editions']if e['language']=='ru');raw=(ROOT/ed['file']).read_bytes()
  if sha(raw)!=ed['sha256']:raise ValueError('Edição mudou')
  lines=raw.decode().splitlines(True);selections=SELECTION.get(n)or{i:SPECIAL7995[c['text']]for i,c in enumerate(item['candidates'])if c['text']in SPECIAL7995};used=set();changes=[]
  for ci,level in selections.items():
   c=item['candidates'][ci];match=[i for i,l in enumerate(lines)if visible(l)==visible(c['text'])and i not in used]
   if not match:raise ValueError(f'Cabeçalho sem linha exata {uid} {c["text"]}')
   # Repeated headings occur in distinct articles; source order gives the occurrence.
   li=match[0];used.add(li);changes.append({'line':li+1,'level':level,'literal_line':lines[li].rstrip('\n'),'source_html':c['html'],'source_text':c['text']});lines[li]='#'*level+' '+lines[li]
  after=''.join(lines);restored=after.splitlines(True)
  for c in changes:restored[c['line']-1]=restored[c['line']-1][c['level']+1:]
  if ''.join(restored).encode()!=raw:raise ValueError('Mudança além da inserção de #')
  folder=OUT/b['id'];folder.mkdir(parents=True,exist_ok=True);cp=folder/(uid+'.ru.md');cp.write_text(after);ep=folder/(uid+'.evidence.json');ep.write_text(json.dumps({'document_id':uid,'source':item['source'],'before_sha256':sha(raw),'candidate_sha256':sha(cp.read_bytes()),'method':'Seleção editorial explícita de rubricas do HTML; cotejo exato de linhas visíveis e prova reversível de que somente prefixos Markdown foram inseridos. Não certifica correção histórica nem revisão crítica integral do texto.','decision':NOTES[n],'heading_insertions':changes,'old_headings':item['current_headings'],'all_other_bytes_preserved':True},ensure_ascii=False,indent=2)+'\n');(folder/(uid+'.diff')).write_text(''.join(difflib.unified_diff(raw.decode().splitlines(True),after.splitlines(True))))
  result=results.setdefault(b['id'],{'batch_id':b['id'],'editions':[],'issues':[]});result['editions'].append({'document_id':uid,'language':'ru','file':ed['file'],'before_sha256':sha(raw),'candidate':str(cp.relative_to(ROOT)),'candidate_sha256':sha(cp.read_bytes()),'source_evidence':str(ep.relative_to(ROOT))})
  for key in d['issue_keys']:
   if key.split(':')[-1]in ['texto_longo_sem_secoes_suficientes','decisao_editorial_pendente']:result['issues'].append({'key':key,'outcome':'corrigido_com_evidencia' if n not in [6762,7995,8623]else 'ressalva_da_fonte_preservada','evidence':str(ep.relative_to(ROOT)),'next_action':NOTES[n]})
  summary.append({'id':uid,'headings_added':len(changes),'decision':NOTES[n]})
 for bid,r in results.items():(OUT/bid/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 (OUT/'prepared-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
