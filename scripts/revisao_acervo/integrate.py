#!/usr/bin/env python3
"""Integra resultados conferidos de agentes com conflitos, prévia e histórico.

Sem --apply, escreve só o diagnóstico de integração na área de trabalho.
"""
import argparse
import copy
import csv
from datetime import datetime,timezone
import io
import json
from pathlib import Path
import sqlite3
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from backend import catalog as model
from backend.editorial import Editorial,QUEUE
from backend.database import Repository
BASE=ROOT/'temporario/revisao-onda1/baseline'
OUT=ROOT/'docs/revisao-markdown/diagnostico-geral'
CLOSE={'corrigido_com_evidencia','alerta_obsoleto_ou_falso_positivo','fonte_continua_legitima','ressalva_da_fonte_preservada'}
OUTCOMES=CLOSE|{'parcial','bloqueado_fonte','decisao_editorial_necessaria','pendente'}


def path_in_root(value):
    path=Path(value);path=(path if path.is_absolute() else ROOT/path).resolve()
    if not path.is_relative_to(ROOT) or path.is_symlink():raise ValueError('Caminho fora do projeto')
    return path


def sha(path):return model.sha256(path.read_bytes())


def freeze(path,batch_id):
    path=path_in_root(path);data=path.read_bytes()
    target=ROOT/'temporario/revisao-onda1/frozen'/batch_id/(model.sha256(data)+'-'+path.name)
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and target.read_bytes()!=data:raise ValueError('Snapshot divergente')
    if not target.exists():target.write_bytes(data)
    return str(target.relative_to(ROOT))


def readers(data):
    reader=csv.DictReader(io.StringIO(data.decode()));return reader.fieldnames,list(reader)


def pdf_dependencies(changed):
    path=ROOT/'.local/research/jobs.sqlite3'
    if not path.exists():return []
    db=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
    try:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='pdf_document_links'").fetchone():return []
        findings=[]
        for uid,doc,project,data in db.execute('SELECT id,document_id,project_id,data FROM pdf_document_links'):
            if project:continue  # drafts are separate versions, never modified here
            state=json.loads(data)
            for anchor in state.get('anchors',[]):
                if (doc,anchor.get('language'))in changed:findings.append({'link_id':uid,'document_id':doc,'language':anchor['language']})
        return findings
    finally:db.close()


def prepare(results,batch_id,baseline_root=BASE):
    baseline_fields,baseline_rows=readers((baseline_root/'queue.csv').read_bytes());baseline={r['chave']:r for r in baseline_rows}
    fields,rows=readers((ROOT/QUEUE).read_bytes());current_rows={r['chave']:r for r in rows}
    if fields!=baseline_fields or len(current_rows)!=len(rows):raise ValueError('Esquema ou chaves da fila mudaram')
    manifest=json.loads((baseline_root/'manifest.json').read_text());allowed_batches={b['id']:b for b in manifest['batches']}
    current=model.load(ROOT);candidate=copy.deepcopy(current);editions={e['id']:e for e in candidate['editions']}
    documents={d['id']:d for d in candidate['documents']};metadata_changed=[]
    files={};changes=[];summaries=[];seen_editions=set();seen_issues=set();changed=set();owned_docs=set()
    for result_path in results:
        result_path=path_in_root(result_path);result=json.loads(result_path.read_text())
        result_snapshot=freeze(result_path,batch_id)
        bid=result.get('batch_id')or result.get('id')
        if bid not in allowed_batches:raise ValueError('Lote desconhecido: '+str(bid))
        task=allowed_batches[bid];owned={d['id']:d for d in task['documents']}
        if owned_docs.intersection(owned):raise ValueError('Dois agentes editaram mesmo documento')
        owned_docs.update(owned)
        for ident, baseline_doc in owned.items():
            for prior in baseline_doc['editions']:
                eid=ident+':'+prior['language'];edition=editions.get(eid)
                if not edition or edition['sha256']!=prior['sha256'] or sha(ROOT/edition['file'])!=prior['sha256']:
                    raise ValueError('Edição do documento mudou após o despacho: '+eid)
        for item in result.get('editions',[]):
            ident=item['document_id'];lang=item['language'];eid=ident+':'+lang
            if ident not in owned or eid in seen_editions:raise ValueError('Edição fora do lote ou duplicada')
            seen_editions.add(eid);edition=editions[eid]
            if item['file']!=edition['file'] or item['before_sha256']!=edition['sha256'] or sha(ROOT/edition['file'])!=item['before_sha256']:raise ValueError('Edição humana posterior preservada: '+eid)
            proposed=path_in_root(item['candidate']);data=proposed.read_bytes()
            if model.sha256(data)!=item['candidate_sha256']:raise ValueError('Candidato divergente: '+eid)
            if data==(ROOT/edition['file']).read_bytes():continue
            review={'batch_id':batch_id,'agent_batch_id':bid,'result_file':str(result_path.relative_to(ROOT)),
                'result_snapshot':result_snapshot,
                'result_sha256':sha(result_path),'before_sha256':edition['sha256'],'after_sha256':model.sha256(data),
                'source_evidence':item.get('source_evidence'),'reviewed_at':datetime.now(timezone.utc).isoformat()}
            if isinstance(item.get('source_evidence'),str):
                review['source_evidence_snapshot']=freeze(item['source_evidence'],batch_id)
            edition.setdefault('extra',{}).setdefault('editorial_reviews',[]).append(review)
            edition.update(sha256=model.sha256(data),bytes=len(data));files[edition['file']]=data.decode('utf-8');changed.add((ident,lang))
            changes.append({'field':eid,'before':item['before_sha256'],'after':edition['sha256']})
        for item in result.get('documents',[]):
            ident=item['document_id'];doc=documents.get(ident)
            if ident not in owned or not doc or model.sha256(model.json_bytes(doc))!=item['before_sha256']:
                raise ValueError('Metadado mudou após preparação: '+ident)
            if set(item['fields'])-{'historical_date'}:raise ValueError('Campo fora desta revisão')
            before=copy.deepcopy(doc)
            doc.update(item['fields'])
            metadata_review={'batch_id':batch_id,'source_evidence':item['source_evidence'],
                             'before_historical_date':before['historical_date']}
            if isinstance(item.get('source_evidence'),str):
                metadata_review['source_evidence_snapshot']=freeze(item['source_evidence'],batch_id)
            doc.setdefault('source_metadata',{}).setdefault('editorial_reviews',[]).append(metadata_review)
            metadata_changed.append(ident)
            changes.append({'field':ident+':metadados','before':before,'after':copy.deepcopy(doc)})
        for issue in result.get('issues',[]):
            key=issue['key'];before=baseline.get(key);row=current_rows.get(key)
            if not before or before['id']not in owned or key in seen_issues:raise ValueError('Pendência fora do lote ou duplicada')
            seen_issues.add(key)
            if row!=before:raise ValueError('Estado da fila mudou: '+key)
            outcome=issue['outcome']
            if outcome not in OUTCOMES:raise ValueError('Resultado desconhecido: '+outcome)
            if not issue.get('evidence'):raise ValueError('Resultado sem evidência: '+key)
            note='Revisão '+batch_id+' / '+bid+': '+outcome+'. Evidência: '+str(issue['evidence'])
            if isinstance(issue['evidence'],str):
                note+=' Snapshot: '+freeze(issue['evidence'],batch_id)
            if issue.get('next_action'):note+=' Próxima ação: '+issue['next_action']
            row['notas_do_revisor']=(row['notas_do_revisor']+' | 'if row['notas_do_revisor']else'')+note
            if outcome in CLOSE:row['status']='corrigido'
            elif outcome=='parcial':row['status']='em_revisao'
            if outcome not in CLOSE and issue.get('next_action'):row['acao_sugerida']=issue['next_action']
            changes.append({'field':key,'before':before,'after':dict(row)})
        summaries.append({'batch_id':bid,'result_file':str(result_path.relative_to(ROOT)),
            'result_snapshot':result_snapshot,
            'result_sha256':sha(result_path),'editions_prepared':len(result.get('editions',[])),
            'issue_outcomes':[{k:i[k]for k in ['key','outcome']}for i in result.get('issues',[])]})
    dependencies=pdf_dependencies(changed)
    if dependencies:raise ValueError('Vínculos PDF precisam de migração/revalidação antes de integrar: '+json.dumps(dependencies,ensure_ascii=False))
    if changed:
        files['data/catalog/editions.json']=model.json_bytes(candidate['editions']).decode()
    if metadata_changed:
        files['data/catalog/documents.json']=model.json_bytes(candidate['documents']).decode()
    if changed or metadata_changed:
        files['data/manifest.json']=model.json_bytes(model.export_manifest(candidate)).decode()
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    if stream.getvalue().encode()!=(ROOT/QUEUE).read_bytes():files[QUEUE]=stream.getvalue()
    summary={'batch_id':batch_id,'editions_changed':len(changed),'issue_outcomes':len(seen_issues),
        'documents_metadata_changed':metadata_changed,
        'closed_issues':sum(i['outcome']in CLOSE for b in summaries for i in b['issue_outcomes']),
        'queue_before_sha256':sha(ROOT/QUEUE),'queue_after_sha256':model.sha256(stream.getvalue().encode()),
        'pdf_anchor_conflicts':dependencies,'batches':summaries}
    return candidate,files,changes,summary,current


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('results',nargs='+');ap.add_argument('--batch-id',required=True);ap.add_argument('--baseline-root',type=Path,default=BASE);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
    if not a.batch_id or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-'for c in a.batch_id):ap.error('Lote inválido')
    editorial=Editorial(ROOT)if a.apply else None
    try:
        candidate,files,changes,summary,current=prepare(a.results,a.batch_id,path_in_root(a.baseline_root))
        target=OUT/(a.batch_id+'-preview.json');target.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
        if a.apply:
            receipt_path=OUT/(a.batch_id+'-gravacao.json')
            if receipt_path.exists():raise ValueError('Histórico já registrado para lote')
            preview=editorial.store_preview(editorial.revision(),candidate,files,None,changes,entity={'kind':'batch','id':a.batch_id})
            receipt=editorial.save(Repository(ROOT,ROOT/'.local/catalog.sqlite3',current,{}),{'preview_id':preview['preview_id']})
            summary.update(receipt);receipt_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(summary,ensure_ascii=False))
    finally:
        if editorial:editorial.close()


if __name__=='__main__':main()
