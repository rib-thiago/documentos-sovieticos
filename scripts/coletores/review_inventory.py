#!/usr/bin/env python3
"""Fotografia das filas: aquisição, referências, candidatos e acervo já incorporado.

Lê inventários e catálogo; escreve somente relatórios. Não aprova nem incorpora.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime,timezone
import io
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FRONTS=('sakharov','svitlana','mozokhin','brest')


def reason_text(value):
    return value if isinstance(value,str)else json.dumps(value,ensure_ascii=False)


def describe(front,unit,editions):
    uid=unit['id'];language=unit.get('language');ident=unit.get('document_id',uid)
    fingerprint=unit.get('markdown_sha256')or unit.get('hashes',{}).get('markdown_sha256')
    edition=editions.get((ident,language))
    issues=[reason_text(x)for x in unit.get('issues',[])];reason=unit.get('reason')or' | '.join(issues)
    acquisition=unit.get('provenance',{}).get('acquisition',{})
    acquisition=acquisition if isinstance(acquisition,dict)else{}
    source_state=acquisition.get('estado_aquisicao')
    segment=unit.get('segment',{}).get('kind')
    if edition and edition['sha256']==fingerprint:
        state='incorporated' if unit.get('ready_for_import') else 'incorporated_review_required'
    elif unit.get('ready_for_import'):
        state='prepared_revision'if edition else'prepared_new'
    elif source_state in {'INDEX_ONLY','METADATA_ONLY'}or unit.get('kind')=='reference':
        state='reference_or_index'
    elif segment in {'heading_only_boundary','appendix_compilation'}:
        state='structural_record'
    elif language not in {'ru','pt','en'}:
        state='research_language'
    elif not unit.get('markdown') and (unit.get('raw') or acquisition.get('raw_path')):
        state='extraction_pending'
    elif not unit.get('markdown'):
        state='source_not_acquired'
    else:
        state='retained_review'
    return {'front':front,'unit_id':uid,'document_id':ident,'language':language,'state':state,
        'reason':reason,'source_url':unit.get('source_url'),'markdown':unit.get('markdown'),
        'markdown_sha256':fingerprint}


def build(work,report):
    editions={(e['document_id'],e['language']):e for e in json.loads((ROOT/'data/catalog/editions.json').read_text())}
    items=[];summary={};acquisition={}
    for front in FRONTS:
        path=work/front/'units.json'
        if not path.exists():continue
        payload=json.loads(path.read_text());units=payload if isinstance(payload,list)else payload['units']
        rows=[describe(front,u,editions)for u in units];items.extend(rows)
        summary[front]=dict(Counter(r['state']for r in rows))
    path=work/'svitlana/inventory.json'
    if path.exists():
        candidates=list(json.loads(path.read_text())['candidates'].values())
        acquisition['svitlana']={'urls':len(candidates),'acquired':sum(bool(c.get('latest_success'))for c in candidates),
            'failed':sum(not c.get('latest_success')and bool(c.get('attempts'))for c in candidates),
            'never_attempted':sum(not c.get('attempts')for c in candidates)}
    result={'generated_at':datetime.now(timezone.utc).isoformat(),'catalog_changed':False,'counts_are_units_not_unique_documents':True,'summary':summary,'acquisition':acquisition,'units':items}
    report.mkdir(parents=True,exist_ok=True)
    for name,data in [('ESTADO-ATUAL.json',json.dumps(result,ensure_ascii=False,indent=2)+'\n')]:
        target=report/name;tmp=target.with_suffix('.tmp');tmp.write_text(data);tmp.replace(target)
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=list(items[0])if items else['front','unit_id','state']);writer.writeheader();writer.writerows(items)
    target=report/'ESTADO-ATUAL.csv';tmp=target.with_suffix('.tmp');tmp.write_text(stream.getvalue());tmp.replace(target)
    lines=['# Estado atual das quatro frentes','',result['generated_at'],'','Contagens de unidades/versões candidatas, não de documentos históricos únicos. Referências, índices e registros estruturais não são automaticamente textos faltantes. Este relatório não modifica o acervo.','','| Frente | No acervo | No acervo com retenção nova | Novas preparadas | Revisões preparadas | Retidas para revisão | Referências/índices | Estrutura | Outro idioma | Extração pendente | Fonte ausente |','|---|---|---|---|---|---|---|---|---|---|---|']
    keys=['incorporated','incorporated_review_required','prepared_new','prepared_revision','retained_review','reference_or_index','structural_record','research_language','extraction_pending','source_not_acquired']
    for front,counts in summary.items():lines.append('| '+front+' | '+' | '.join(str(counts.get(k,0))for k in keys)+' |')
    if acquisition:
        a=acquisition['svitlana'];lines+=['',f"Svitlana: {a['acquired']}/{a['urls']} URLs adquiridas; {a['failed']} com falha e {a['never_attempted']} sem tentativa."]
    lines+=['','“Revisões preparadas” significa que há outro candidato para um documento/idioma já existente: não foi substituído automaticamente. “No acervo” exige coincidência do identificador, idioma e hash da edição. “Preparadas” não equivale a revisão crítica integral nem autorização de publicação automática.','','A lista por unidade, motivo e fonte está em [ESTADO-ATUAL.csv](ESTADO-ATUAL.csv). Os inventários e relatórios de cada frente preservam o detalhamento de aquisição e decisões.']
    target=report/'ESTADO-ATUAL.md';tmp=target.with_suffix('.tmp');tmp.write_text('\n'.join(lines)+'\n');tmp.replace(target)
    print(json.dumps({'summary':summary,'acquisition':acquisition},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workdir',type=Path,default=ROOT/'temporario/coletas-quatro')
    parser.add_argument('--reportdir',type=Path,default=ROOT/'docs/pesquisa/quatro-coletores')
    args=parser.parse_args();build(args.workdir,args.reportdir)
