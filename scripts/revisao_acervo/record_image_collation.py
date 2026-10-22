#!/usr/bin/env python3
"""Registra cotejos visuais realizados; não é OCR ou aprovação automática."""
import json
from pathlib import Path
from prepare_tables_a import sha
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'temporario/revisao-onda1/estruturas-root'
FINDINGS={
10722:('corrigido_com_evidencia','Cartão postal frente/verso. Cotejados endereço do remetente em Berlim, destinatário Leo Sedoff em Buyuk Ada, saudação a Lev Lvovich, recebimento/correção do cartão, encaminhamento do apelo, iniciais M/G, fecho e 29/III. O texto já transcreve estas passagens; marcas postais não foram convertidas em data da carta.','Corpo e endereços conferidos; não há texto documental adicional desta imagem a recuperar.'),
1442:('corrigido_com_evidencia','Três folhas da carta de Zinoviev a Rumyantsev de 30/VI/1928, fólios 168–170. Cotejados início sobre viagem de Z.I., pedido à CCC, declaração, questões novas, entrada no partido, Moscou, ruptura em dezembro de 1927, trabalho/amizade, fecho e assinatura. O corpo integral já aparece no Markdown. Não se incorporam rasuras canceladas como texto corrente nem se certifica identificação histórica por esta leitura.','Transcrição do corpo existente conferida nas três imagens; preservar expansões e aparato da edição.'),
1733:('corrigido_com_evidencia','Três informes datilografados e anotações manuscritas de encaminhamento/arresto. Cotejados Konstantinova, Avdeeva e Katynskaya, declarações, salário 260, fome e anotações com datas 16/17-XII, 27-I e 24-I. Transcrições e expansões entre colchetes já existem, inclusive a leitura 27/I/34, que não foi harmonizada por plausibilidade. A conferência não atesta veracidade dos rumores ou autoria histórica das rubricas.','Conteúdo das três imagens representado no corpo e aparato existentes; conservar datas literais e expansões editoriais.'),
3277:('corrigido_com_evidencia','Carta manuscrita de Safarov a Stalin, 16/XII/34, fólio 46/número 75. Cotejados destinatário, rompimento com o trotskismo, pedido de esclarecimento, trabalho no interior, juramento/confiança, fecho e assinatura. O corpo está transcrito; referência bibliográfica final é aparato adicional, não texto da imagem.','Corpo conferido; o vínculo com fac-símile segue motivo independente de links.'),
7391:('corrigido_com_evidencia','Fac-símile parcial: abertura da carta a Stalin de 23/I/1935, fólio 13/número 18. Cotejados saudação e parágrafos sobre Kamenev, carta de 17/I, pedido de leitura do anexo e culpa/retrato. O trecho visível encontra-se no Markdown; o recorte termina no interior dafrase. A imagem não é atestação de integralidade das demais cartas da página.','Abertura visível transcrita; manter a distinção entre fac-símile parcial e compilação textual.'),
9061:('alerta_obsoleto_ou_falso_positivo','Imagem é capa: ВАЛЕНТИН ОЛЬБЕРГ, ПРОБЛЕМЫ ВОЙНЫ, 1929, com anotações arquivísticas. O texto da obra começa no Markdown e contém título/ano; capa não representa página de texto corrente perdida. Não se afirma que todas páginas do livro foram cotejadas com esta capa.','Não há corpo documental a extrair desta capa; preservar seu papel bibliográfico.'),
5360:('parcial','A miniatura 150×150 era insuficiente. A aquisição da fonte picture1-scaled.jpg declarada no srcset permite ler a cópia anotada. O corpo inicial está transcrito, mas os valores da entrada 5, Novikov divergem: na imagem leem-se 1891 e 1918; oMarkdown atual traz 1899 e 1916. Há anotações coloridas manuscritas que exigem cotejo separado. Não se presume que se trate do mesmo estado textual nem se emendam dados por plausibilidade.','Cotejar a entrada 5, Novikov (1891/1918 na imagem; 1899/1916 na transcrição), a identidade do testemunho e anotação manuscrita; registrar variantes antes de alterar RU ou traduções.')}


def main():
 manifest=json.load(open(ROOT/'temporario/revisao-onda1/baseline/manifest.json'));es={e['id']:e for e in json.load(open(ROOT/'data/catalog/editions.json'))};acquisition=json.load(open(ROOT/'temporario/revisao-onda1/imagens/acquisition.json'))
 for n,(outcome,finding,action)in FINDINGS.items():
  uid='showtrials-'+str(n);key=uid+':imagens_sem_transcricao_confirmada';task=next(b for b in manifest['batches']if any(d['id']==uid for d in b['documents']));folder=OUT/task['id'];rp=folder/'result.json';result=json.load(open(rp));images=[i for i in acquisition if i['document_id']==uid]
  for image in images:
   if image['state']!='acquired'or sha((ROOT/image['file']).read_bytes())!=image['sha256']:raise ValueError('Imagem divergente')
  if not images:raise ValueError('Sem imagem adquirida')
  edition=es[uid+':ru'];data=(ROOT/edition['file']).read_bytes()
  if sha(data)!=edition['sha256']:raise ValueError('Canônico divergente')
  audit=folder/(uid+'-visual.json');audit.write_text(json.dumps({'document_id':uid,'canonical_file':edition['file'],'canonical_sha256':edition['sha256'],'images':images,'review_kind':'visual_collation_by_integrator','finding':finding,'outcome':outcome,'next_action':action,'canonical_text_changed':False},ensure_ascii=False,indent=2)+'\n')
  result['issues']=[i for i in result['issues']if i['key']!=key];result['issues'].append({'key':key,'outcome':outcome,'evidence':str(audit.relative_to(ROOT)),'next_action':action});rp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('Sete cotejos visuais registrados;5360 permanece parcial.')


if __name__=='__main__':main()
