#!/usr/bin/env python3
"""Revisão de quadros de disposição e retenção explícita das grades complexas."""
import json
from pathlib import Path
from bs4 import BeautifulSoup
from prepare_tables_a import normmap,sha
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'temporario/revisao-onda1/estruturas-root'
LAYOUT={7075:'Lista de nomes em célula única; não há relações entre colunas a recuperar.',6680:'Cabeçalho de telegrama: endereço, marca do telefonista e horário; disposição tipográfica.',6687:'Cabeçalho de telegrama: endereço e marca do telefonista; última célula vazia.',7096:'Lista de distribuição de exemplares em colunas tipográficas.',7150:'Lista de distribuição de exemplares em colunas tipográficas.',7262:'Lista de distribuição de exemplares em colunas tipográficas.',7265:'Lista de distribuição de exemplares em colunas tipográficas.',7267:'Lista de distribuição de exemplares em colunas tipográficas.',7271:'Lista de distribuição de exemplares em colunas tipográficas.',7273:'Lista de distribuição de exemplares em colunas tipográficas.',7383:'Lista de distribuição de exemplares em colunas tipográficas.',7385:'Lista de distribuição de exemplares em colunas tipográficas.'}


def main():
 proposals=json.load(open(ROOT/'docs/revisao-markdown/diagnostico-geral/proposals-showtrials.json'));lookup={x['chave']:x for x in proposals['proposals']};editions={e['id']:e for e in json.load(open(ROOT/'data/catalog/editions.json'))};preparation=json.load(open(OUT/'preparacao.json'))
 manifest=json.load(open(ROOT/'temporario/revisao-onda1/baseline/manifest.json'));bydoc={d['id']:b for b in manifest['batches']for d in b['documents']}
 for item in preparation:
  uid=item['id'];n=int(uid.split('-')[1]);key=uid+':tabelas_linearizadas';batch=bydoc[uid];folder=OUT/batch['id'];rp=folder/'result.json';result=json.load(open(rp)) if rp.exists() else {'batch_id':batch['id'],'editions':[],'issues':[]}
  ev=lookup[key]['evidencia'];post=next(p for p in json.load(open(ROOT/ev['source_json']))if p['id']==n);html=post['content']['rendered'];soup=BeautifulSoup(html,'html.parser');tables=soup.select('table');edition=editions[uid+':ru'];text=(ROOT/edition['file']).read_text()
  if n in LAYOUT or not item['prepared']:result['issues']=[i for i in result['issues']if i['key']!=key]
  if sha(html.encode())!=ev['source_html_sha256'] or sha((ROOT/edition['file']).read_bytes())!=edition['sha256']:raise ValueError('Fonte/versão divergente')
  if n in LAYOUT:
   cells=[c.get_text('',strip=False)for t in tables for c in t.select('td,th')];body=normmap(text)[0];cursor=0;offsets=[]
   for cell in cells:
    needle=normmap(cell)[0]
    if not needle:offsets.append(None);continue
    at=body.find(needle,cursor)
    if at<0:raise ValueError('Conteúdo de layout não preservado: '+uid)
    offsets.append(at);cursor=at+len(needle)
   evidence={'source_json':ev['source_json'],'source_html_sha256':ev['source_html_sha256'],'canonical_sha256':edition['sha256'],'kind':'layout_table_not_relational_data','source_cells':cells,'ordered_offsets':offsets,'finding':LAYOUT[n]+' Todo texto das células permanece na ordem no Markdown; não precisa ser transformado em tabela de dados.'}
   audit=folder/(uid+'-layout.json');audit.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
   result['editions']=[e for e in result['editions']if e['document_id']!=uid];result['issues']=[i for i in result['issues']if i['key']!=key]
   result['issues'].append({'key':key,'outcome':'alerta_obsoleto_ou_falso_positivo','evidence':str(audit.relative_to(ROOT)),'next_action':'Preservar a transcrição atual e sua ordem; não há tabela relacional perdida neste quadro de disposição.'})
  elif not item['prepared']:
   evidence={'source_json':ev['source_json'],'source_html_sha256':ev['source_html_sha256'],'canonical_sha256':edition['sha256'],'table_count':len(tables),'source_cell_count':sum(len(t.select('td,th'))for t in tables),'merged_cells':sum(int(c.get('rowspan',1))>1 or int(c.get('colspan',1))>1 for t in tables for c in t.select('td,th')),'reason':item['reason'],'finding':'Candidato automático recusado; nenhum texto foi alterado. Precisa cotejo e reconstrução específica, não indisponibilidade de fonte.'}
   audit=folder/(uid+'-retencao.json');audit.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
   result['issues'].append({'key':key,'outcome':'parcial','evidence':str(audit.relative_to(ROOT)),'next_action':'Reconstruir individualmente a grade, cabeçalhos, mesclas e limites entre células. Se houver traduções, cotejar os limites de cada idioma antes de integrar; não usar HTML bruto nem alinhar por contagem.'})
  rp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 # Fac-símile manuscrito de Zinoviev: comparação visual pelo integrador.
 uid='showtrials-3276';batch=bydoc[uid];folder=OUT/batch['id'];rp=folder/'result.json';result=json.load(open(rp));image=ROOT/'temporario/revisao-onda1/estrutura-impares/images/3276.jpg'
 evidence={'source_image':'temporario/revisao-onda1/estrutura-impares/images/3276.jpg','source_image_sha256':sha(image.read_bytes()),'source_url':'http://showtrials.ru/wp-content/uploads/2021/06/pismo-zinoveva-16-dek-scaled.jpg','canonical_file':editions[uid+':ru']['file'],'canonical_sha256':editions[uid+':ru']['sha256'],'visual_collation':'Uma folha manuscrita, fólio 45 e número 76, carta de Zinoviev a Stalin. Cotejados destinatário, busca de 16 de dezembro às 7½, parágrafo sobre retorno de Kustanai, arquivos de 30 anos, juramento e memória de Lenin, fecho e assinatura. O corpo já tem a transcrição destas passagens; publicações/cota finais são aparato adicional. Não há texto adicional da imagem a transcrever.'}
 audit=folder/(uid+'-imagem.json');audit.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
 result['issues']=[i for i in result['issues']if i['key']!=uid+':imagens_sem_transcricao_confirmada']
 result['issues'].append({'key':uid+':imagens_sem_transcricao_confirmada','outcome':'corrigido_com_evidencia','evidence':str(audit.relative_to(ROOT)),'next_action':'Transcrição existente conferida contra o fac-símile; acesso à imagem e vínculo correspondente permanecem no motivo separado de links.'})
 rp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('Resultados estruturais classificados; imagem3276 conferida; demais imagens não encerradas.')


if __name__=='__main__':main()
