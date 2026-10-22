#!/usr/bin/env python3
"""Reconciliação delimitada da fila; prévia por padrão, --apply usa histórico editorial.

Não altera textos, catálogo, manifesto ou busca. Recusa fila/fontes divergentes.
"""
import argparse
import csv
import io
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from backend import catalog as model
from backend.editorial import Editorial, QUEUE
from backend.database import Repository
OUT=ROOT/'docs/revisao-markdown/diagnostico-geral'


def checked(path,expected):
    data=(ROOT/path).read_bytes()
    if model.sha256(data)!=expected:raise ValueError('Evidência mudou: '+path)
    return data


def prepare():
    raw=(ROOT/QUEUE).read_bytes();expected=json.loads((OUT/'proposals-reconciliation.json').read_text())
    if model.sha256(raw)!=expected['queue_sha256']:raise ValueError('A fila mudou; reconciliar novamente sem sobrescrever novas edições.')
    reader=csv.DictReader(io.StringIO(raw.decode()));fields=reader.fieldnames;rows=list(reader);bykey={r['chave']:r for r in rows}
    if len(bykey)!=len(rows):raise ValueError('Chaves duplicadas')
    changes=[]
    for p in expected['proposals']:
        checked(p['arquivo'],p['sha256'])
        for ev in p['evidence']:checked(ev['file'],ev['sha256'])
        row=bykey[p['chave']];before=dict(row)
        if row['status']!=p['status_proposto'] or row['prioridade']!=p['prioridade_proposta']:raise ValueError('Estado humano mudou')
        row.update(dificuldade_encontrada=p['dificuldade_encontrada_proposta'],acao_sugerida=p['acao_sugerida_proposta'],notas_do_revisor=p['notas_do_revisor_propostas'])
        changes.append({'key':row['chave'],'kind':'correcao_aplicada_conferencia_preventiva','before':before,'after':dict(row)})
    props=json.loads((OUT/'proposals-showtrials.json').read_text())['proposals']
    p=next(p for p in props if p['chave']=='showtrials-1699:texto_longo_sem_secoes_suficientes')
    ev=p['evidencia'];text=checked(ev['canonical_path'],ev['canonical_sha256']).decode()
    if ev['current_heading_count']!=10:raise ValueError('Reavaliar evidência das seções')
    row=bykey[p['chave']];before=dict(row)
    if row['status']!='pendente':raise ValueError('Estado humano de1699 mudou')
    row['status']='corrigido'
    row['notas_do_revisor']=(row['notas_do_revisor']+' | ' if row['notas_do_revisor'] else '')+'Reconciliação de21/10/2026: alerta antigo de ausência de seções superado na versão atual, com dez títulos; SHA-256 '+ev['canonical_sha256']+'. Encerramento limitado ao indicador de navegação; não certifica conteúdo histórico nem faz nova validação integral das tabelas.'
    changes.append({'key':row['chave'],'kind':'alerta_obsoleto_resolvido','before':before,'after':dict(row),'evidence':ev})
    # Registrar ressalvas históricas em tarefas próprias, sem considerá-las erros atuais comprovados.
    source=ROOT/'docs/traducoes/leningrado-investigacao/pendencias-editoriais.csv';source_sha=model.sha256(source.read_bytes())
    catalog=model.load(ROOT);docs={d['id']:d for d in catalog['documents']};editions={e['id']:e for e in catalog['editions']}
    for issue in csv.DictReader(io.StringIO(source.read_text(encoding='utf-8-sig'))):
        ident=issue['documento'];key=ident+':ressalva_traducao_leningrado'
        if key in bykey:raise ValueError('Ressalva já representada: '+key)
        doc=docs[ident];edition=editions[ident+':ru'];checked(edition['file'],edition['sha256'])
        row=dict.fromkeys(fields,'');row.update(chave=key,prioridade=issue['prioridade'],dificuldade='alta',status='pendente',id=ident,
            colecoes='Processo do Centro de Leningrado / Materiais da Investigação',titulo_ru=doc['titles'].get('ru',''),
            problema='ressalva_traducao_leningrado',dificuldade_encontrada=issue['motivo'],
            acao_sugerida='Revalidar a ressalva no russo, português, inglês e fonte atuais. Distinguir erro de tradução, limitação literal da fonte e divergência histórica; corrigir somente com evidência.',
            arquivo_markdown=edition['file'],url_teste=issue['url_local'],fonte=doc.get('source',{}).get('url',''),trechos='[]',
            notas_do_revisor='Ressalva proveniente de '+str(source.relative_to(ROOT))+'; SHA-256 '+source_sha+'. Incluída na fila em21/10/2026 para revalidação: não é diagnóstico novo de erro confirmado. Nenhum texto foi modificado. Alertas de links do mesmo documento permanecem separados.')
        rows.append(row);bykey[key]=row
        changes.append({'key':key,'kind':'ressalva_historica_antes_fora_da_fila','before':None,'after':dict(row)})
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    result={'queue_before_sha256':model.sha256(raw),'queue_after_sha256':model.sha256(stream.getvalue().encode()),
        'rows_before':len(rows)-17,'rows_after':len(rows),'updated_rows':5,'added_rows':17,'new_closures':1,'source_texts_modified':False,'changes':changes}
    return catalog,stream.getvalue(),result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    editorial=Editorial(ROOT) if args.apply else None
    try:
        catalog,text,result=prepare()
        (OUT/'RECONCILIACAO-PREVIA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        if args.apply:
            changes=[{'field':'Fila editorial: '+c['key'],'before':c['before'],'after':c['after']}for c in result['changes']]
            preview=editorial.store_preview(editorial.revision(),catalog,{QUEUE:text},None,changes,
                entity={'kind':'batch','id':'diagnostico-reconciliacao-20261021','document_ids':sorted({c['after']['id']for c in result['changes']})})
            receipt=editorial.save(Repository(ROOT,ROOT/'.local/catalog.sqlite3',catalog,{}),{'preview_id':preview['preview_id']})
            result.update(receipt);(OUT/'RECONCILIACAO-GRAVACAO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items()if k not in {'changes','entity'}},ensure_ascii=False))
    finally:
        if editorial:editorial.close()


if __name__=='__main__':main()
