#!/usr/bin/env python3
"""Diagnóstico reproduzível e lotes por documento; nunca altera fila ou acervo."""
import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/revisao-markdown/diagnostico-geral'
QUEUE=ROOT/'docs/revisao-markdown/pendencias.csv'
PRIORITY={'urgente':0,'alta':1,'media':2,'baixa':3}
# Escopos não são sentenças sobre a qualidade factual de um documento.
RULES={
 'links_nao_reconstruidos':('suspeita_automatica','recuperacao_links',3,'Comparar links do HTML com o Markdown atual, preservando rótulos e destinos; não excluir navegação por heurística sem registrar.'),
 'tabelas_linearizadas':('suspeita_automatica','tabelas_imagens',1,'Cotejar células e cabeçalhos com HTML/imagem; distinguir tabela documental de layout antes de reconstruir.'),
 'imagens_sem_transcricao_confirmada':('suspeita_automatica','tabelas_imagens',1,'Inspecionar imagem; identificar fac-símile documental, ornamento ou anexo. OCR é candidato, nunca fonte final.'),
 'texto_longo_sem_secoes_suficientes':('indicador_navegabilidade','secoes_listas',2,'Conferir divisões explícitas na fonte; não inventar títulos porque o documento é longo.'),
 'listas_sem_marcacao':('suspeita_automatica','secoes_listas',2,'Confirmar itens e limites; preservar texto e distinção entre lista e tabela.'),
 'titulos_ambiguos':('decisao_editorial','secoes_listas',2,'Resolver hierarquia somente com evidência documental; manter ambiguidade se fonte não permite decidir.'),
 'decisao_editorial_pendente':('decisao_editorial','secoes_listas',2,'Cotejar marcadores/ordem; registrar decisão sem emendar conteúdo por plausibilidade.'),
 'individualizacao_compilacao':('divergencia_registrada','divergencias_idiomas',2,'Comparar RU/PT/EN e fonte; distinguir data literal, interpretação e título; não harmonizar testemunhos.'),
 'fonte_militar':('conferencia_fonte','fontes_militares',1,'Desdobrar a ressalva: tabelas/notas ou ficha de PDF sem transcrição; conferir fonte preservada.'),
 'coleta_quatro_colecoes':('revisao_preventiva','conferencia_colecoes',4,'Usar proveniência e revisões anteriores; separar aspectos já conferidos de metadados/tradução ainda não revistos.'),
 'cadastro_local':('revisao_preventiva','conferencia_colecoes',4,'Conferir cadastro sem presumir erro; preservar documentos criados pelo usuário.'),
 'conferencia_notas_20261021':('correcao_aplicada_conferencia_posterior','conferencia_colecoes',4,'Conferir evidência da correção já aplicada; revisão preventiva restante não é erro de nota ainda aberto.'),
 'ressalva_traducao_leningrado':('divergencia_registrada_a_revalidar','divergencias_idiomas',2,'Revalidar ressalva histórica no RU/PT/EN atual e fonte, registrando se é limitação da fonte ou erro de tradução.'),
}


def digest(data):return hashlib.sha256(data).hexdigest()


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    raw=QUEUE.read_bytes();rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
    docs={d['id']:d for d in json.loads((ROOT/'data/catalog/documents.json').read_text())}
    editions=defaultdict(list)
    for e in json.loads((ROOT/'data/catalog/editions.json').read_text()):editions[e['document_id']].append(e)
    keys=Counter(r['chave']for r in rows);records=[];by_doc=defaultdict(list);content={}
    for r in rows:
        ident=r['id'];kind,family,wave,action=RULES.get(r['problema'],('requer_classificacao','triagem_manual',1,'Classificar escopo antes de alterar.'))
        target=r['arquivo_markdown'];target_path=ROOT/target if target else None
        if target not in content:
            data=target_path.read_bytes() if target_path and target_path.is_file() else None
            text=data.decode('utf-8') if data is not None else ''
            known=next((e for e in editions[ident]if e['file']==target),None)
            content[target]={'sha256':digest(data) if data is not None else None,'characters':len(text),
                'headings_observed':len(re.findall(r'(?m)^#{1,6} +\S',text)),
                'catalog_hash_matches':bool(known and data is not None and digest(data)==known['sha256']),
                'file_exists':data is not None}
        state=content[target]
        integrity=[]
        if ident not in docs:integrity.append('documento_fora_catalogo')
        if not state['file_exists']:integrity.append('arquivo_ausente')
        if not state['catalog_hash_matches']:integrity.append('arquivo_sem_hash_catalogo_coincidente')
        if keys[r['chave']]>1:integrity.append('chave_duplicada')
        if integrity:wave=0
        item={**r,'diagnostic_class':kind,'work_family':family,'wave':wave,'next_action':action,
            'classification_basis':'categoria original; não revisão integral da fonte',
            'content_snapshot':state,'integrity_alerts':integrity}
        records.append(item)
        if r['status'] in {'pendente','em_revisao'}:by_doc[ident].append(item)
    # Um documento é propriedade de um único lote mesmo tendo problemas de famílias diferentes.
    pools=defaultdict(list)
    for ident,issues in by_doc.items():
        owner=min(issues,key=lambda i:(i['wave'],PRIORITY.get(i['prioridade'],9),i['work_family']))
        scope='showtrials' if ident.startswith('showtrials-') else ident.split('-')[0]
        if owner['work_family']=='conferencia_colecoes':
            scope=docs.get(ident,{}).get('source_metadata',{}).get('collector_front') or 'cadastros_locais'
        pools[(owner['wave'],owner['work_family'],scope)].append((ident,issues))
    batches=[];assigned={}
    for (wave,family,scope),items in sorted(pools.items()):
        items.sort(key=lambda x:(min(PRIORITY.get(i['prioridade'],9)for i in x[1]),x[0]))
        # Limites de preparação; fontes grandes podem exigir sublote de um documento.
        maxdocs=3 if family in {'tabelas_imagens','fontes_militares','secoes_listas'} else 12 if family=='divergencias_idiomas' else 30
        limit=220000 if family!='recuperacao_links' else 400000
        bucket=[];chars=0
        def flush():
            nonlocal bucket,chars
            if not bucket:return
            bid=f'R{wave}-{family}-{len(batches)+1:04d}'
            task={'id':bid,'wave':wave,'family':family,'source_scope':scope,'status':'planejado_nao_executado',
              'worker_role':'preparador','integrator_role':'agente_principal',
              'source_access':'verificar fontes locais antes de execução; diagnósticos complementares indicam localizadores',
              'conservative_edition_workload':chars,'exceeds_workload_budget':chars>limit,
              'depends_on':['reconciliacao_da_fila','verificar_hashes_antes_da_execucao'],
              'documents':bucket}
            batches.append(task)
            for doc in bucket:assigned[doc['id']]=bid
            bucket=[];chars=0
        for ident,issues in items:
            size=max(max(i['content_snapshot']['characters']for i in issues),
                     sum(e.get('bytes',0)for e in editions[ident]))
            if bucket and (len(bucket)>=maxdocs or chars+size>limit):flush()
            bucket.append({'id':ident,'issue_keys':[i['chave']for i in issues],
                'issue_families':sorted({i['work_family']for i in issues}),
                'editions':[{k:e.get(k)for k in ['language','file','sha256','bytes']}for e in editions[ident]],
                'source_url':docs.get(ident,{}).get('source',{}).get('url'),
                'priority':min(issues,key=lambda i:PRIORITY.get(i['prioridade'],9))['prioridade'],
                'conservative_edition_workload':size})
            chars+=size
        flush()
    for item in records:item['batch_id']=assigned.get(item['id']) if item['status']in {'pendente','em_revisao'} else None
    active=[i for i in records if i['status']in {'pendente','em_revisao'}]
    result={'generated_at':datetime.now(timezone.utc).isoformat(),'queue_sha256':digest(raw),
        'scope':'Fila do acervo incorporado; coletores retidos e outras filas são inventariados à parte.',
        'source_or_text_modified':False,'queue_rows':len(rows),'open_rows':len(active),
        'open_documents':len(by_doc),'statuses':dict(Counter(r['status']for r in rows)),
        'priorities':dict(Counter(i['prioridade']for i in active)),
        'classes':dict(Counter(i['diagnostic_class']for i in active)),
        'problems':dict(Counter(i['problema']for i in active)),
        'integrity_alert_rows':sum(bool(i['integrity_alerts'])for i in records),
        'batches':len(batches),'records':records}
    (OUT/'DIAGNOSTICO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    fields=['chave','id','status','prioridade','problema','diagnostic_class','work_family','wave','batch_id','next_action','integrity_alerts','arquivo_markdown']
    stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');w.writeheader()
    for item in records:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list))else v for k,v in item.items()})
    (OUT/'DIAGNOSTICO.csv').write_text(stream.getvalue())
    manifest={'generated_at':result['generated_at'],'queue_sha256':result['queue_sha256'],'plan_algorithm_version':2,
      'canonical_writer':'agente_principal_exclusivo','concurrent_workers_max':3,
      'coverage_open_issues':sum(len(d['issue_keys'])for b in batches for d in b['documents']),
      'unique_owned_documents':len(assigned),'batches':batches}
    (OUT/'LOTES.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    version=OUT/'lotes'/result['queue_sha256'];version.mkdir(parents=True,exist_ok=True)
    plan_sha=digest(json.dumps({'queue':manifest['queue_sha256'],'batches':batches},sort_keys=True,ensure_ascii=False).encode())
    snapshot=version/(plan_sha+'.json')
    if not snapshot.exists():
        snapshot.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    progress=OUT/'PROGRESSO.json'
    if not progress.exists():
        progress.write_text(json.dumps({'schema_version':1,'baseline_queue_sha256':result['queue_sha256'],
            'execution_started':False,'batch_results':[],
            'note':'Atualizar resultados por lote; regenerar diagnóstico não apaga este registro.'},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='records'},ensure_ascii=False))


if __name__=='__main__':build()
