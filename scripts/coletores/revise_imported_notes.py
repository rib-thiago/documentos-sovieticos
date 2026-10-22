#!/usr/bin/env python3
"""Aplicar quatro correções conferidas em versões já incorporadas, com histórico.

Recusa conteúdo divergente da versão inicial: nunca sobrescreve edição posterior.
Sem --apply apenas prepara o diagnóstico. Nenhuma publicação ou operação Git.
"""
import argparse
import copy
import csv
import io
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from backend import catalog as model
from backend.database import Repository
from backend.editorial import Editorial,QUEUE

IDS=('mozokhin-2013-v1-054','mozokhin-2013-v1-101','mozokhin-2013-v1-145','mozokhin-2013-v1-146')
REPORT=ROOT/'docs/pesquisa/quatro-coletores'


def prepare():
    work=ROOT/'temporario/coletas-quatro/mozokhin'
    initial=json.loads((work/'reviewed/mozokhin-v2-294-295-notes-20261021/units-before.json').read_text())
    original={u['id']:u for u in initial};units={u['id']:u for u in json.loads((work/'units.json').read_text())}
    current=model.load(ROOT);candidate=copy.deepcopy(current);editions={e['id']:e for e in candidate['editions']};docs={d['id']:d for d in candidate['documents']}
    files={};changes=[];updates=[];already=[]
    for uid in IDS:
        unit=units[uid];old=original[uid];edition=editions[uid+':ru'];doc=docs[uid]
        if not unit.get('ready_for_import'):raise ValueError('Revisão não preparada: '+uid)
        source=(work/unit['raw']).resolve();text=(work/unit['markdown']).resolve()
        if not source.is_relative_to(work.resolve())or not text.is_relative_to(work.resolve()):raise ValueError('Caminho fora da frente')
        data=text.read_bytes()
        if model.sha256(data)!=unit['markdown_sha256']or model.sha256(source.read_bytes())!=unit['raw_sha256']:raise ValueError('Fonte/candidato divergente: '+uid)
        actual=model.content_bytes(ROOT,edition['file'])
        if model.sha256(actual)!=edition['sha256']:raise ValueError('Arquivo canônico alterado fora do catálogo: '+uid)
        if edition['sha256']==unit['markdown_sha256']:already.append(uid);continue
        if edition['sha256']!=old['markdown_sha256']:raise ValueError('Edição posterior preservada; conciliação necessária: '+uid)
        if doc.get('source_metadata',{}).get('source_raw_sha256')!=unit['raw_sha256']:raise ValueError('Proveniência diferente: '+uid)
        correction={'kind':'source_note_ownership_review','source_raw_sha256':unit['raw_sha256'],'before_sha256':edition['sha256'],'after_sha256':unit['markdown_sha256'],'review_provenance':copy.deepcopy(unit['provenance'])}
        edition.setdefault('extra',{}).setdefault('editorial_corrections',[]).append(correction)
        doc.setdefault('source_metadata',{}).setdefault('editorial_corrections',[]).append(correction)
        changes.append({'field':'Correção de notas em '+uid,'before':{'file':edition['file'],'sha256':edition['sha256']},'after':{'file':edition['file'],'sha256':unit['markdown_sha256'],'source_pdf':unit['source_url']}})
        edition.update(sha256=unit['markdown_sha256'],bytes=len(data));files[edition['file']]=data.decode('utf-8');updates.append(uid)
    if not updates:return current,candidate,{},changes,updates,already
    for name in ['documents','editions']:files['data/catalog/'+name+'.json']=model.json_bytes(candidate[name]).decode()
    files['data/manifest.json']=model.json_bytes(model.export_manifest(candidate)).decode()
    previous=(ROOT/QUEUE).read_bytes().decode('utf-8');reader=csv.DictReader(io.StringIO(previous));headers=reader.fieldnames;known={r['chave']for r in reader}
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=headers)
    for uid in updates:
        key=uid+':conferencia_notas_20261021'
        if key in known:raise ValueError('Registro de revisão já existe: '+uid)
        row=dict.fromkeys(headers,'');row.update(chave=key,prioridade='media',dificuldade='media',status='pendente',id=uid,colecoes='Politburo e Lev Trotsky — Mozokhin',titulo_ru=docs[uid]['titles'].get('ru',''),problema='conferencia_notas_20261021',dificuldade_encontrada='Atribuição das notas corrigida por cotejo com fac-símiles; conferir edição corrigida e demais metadados.',acao_sugerida='Conferir versão atual e diferenças no histórico; a versão anterior foi preservada.',arquivo_markdown=editions[uid+':ru']['file'],url_teste='http://localhost:8000/#/doc/'+uid,fonte=units[uid]['source_url'],trechos='[]',notas_do_revisor='Correção estrutural de notas; não representa revisão crítica integral ou alteração das alegações da fonte.')
        writer.writerow(row)
    files[QUEUE]=previous+(''if previous.endswith('\n')else'\n')+stream.getvalue()
    model.validate(candidate,ROOT,check_manifest=False,content_overrides={name:content.encode()for name,content in files.items()})
    return current,candidate,files,changes,updates,already


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    editorial=Editorial(ROOT)if args.apply else None
    try:
        current,candidate,files,changes,updates,already=prepare()
        if not args.apply or not updates:print(json.dumps({'prepared_updates':updates,'already_current':already,'applied':False},ensure_ascii=False));return
        preview=editorial.store_preview(editorial.revision(),candidate,files,None,changes,entity={'kind':'batch','id':'mozokhin-correcao-notas-20261021','document_ids':updates})
        repo=Repository(ROOT,ROOT/'.local/catalog.sqlite3',current,{})
        print('Gravando quatro correções de notas com histórico e busca...',flush=True)
        saved=editorial.save(repo,{'preview_id':preview['preview_id']})
        receipt={**saved,'updated_documents':updates,'already_current':already,'active_counts':repo.info}
        model.atomic_write(REPORT/'mozokhin-correcao-notas-20261021-gravacao.json',model.json_bytes(receipt))
        print(json.dumps({k:v for k,v in receipt.items()if k!='entity'},ensure_ascii=False,indent=2))
    finally:
        if editorial:editorial.close()


if __name__=='__main__':main()
