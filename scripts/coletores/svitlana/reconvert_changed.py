#!/usr/bin/env python3
"""Reconverte só snapshots cujo resultado mudou; sem rede, preserva anteriores."""
import json
from pathlib import Path
from collect import Collector, DEFAULT_OUT, convert, digest, immutable, now, write_json


def main():
    collector = Collector(DEFAULT_OUT)
    before = (DEFAULT_OUT/'inventory.json').read_bytes()
    immutable(DEFAULT_OUT/'reviewed'/'round4'/f'inventory-before-{digest(before)}.json', before)
    changes=[]
    for cid, candidate in collector.inventory['candidates'].items():
        old=candidate.get('latest_success')
        if not old: continue
        raw=(DEFAULT_OUT/old['raw']).read_bytes()
        if digest(raw)!=old['sha256']: raise ValueError('Hash bruto divergente: '+cid)
        text,_,_,_=convert(raw,old.get('content_type','text/html'),old['resolved_url'])
        if digest(text)==old['markdown_sha256']: continue
        result=collector.document(cid,reconvert=True)
        if result['status']=='error': raise ValueError(result)
        changes.append({'candidate_id':cid,'before_sha256':old['markdown_sha256'],
            'after_sha256':result['markdown_sha256'],'before_characters':old.get('characters'),
            'after_characters':len(text),'raw_sha256':old['sha256']})
    report={'generated_at':now(),'network_used':False,'changed_pages':len(changes),'changes':changes}
    target=Path(__file__).resolve().parents[3]/'docs/pesquisa/quatro-coletores/SVITLANA-RECONVERSAO-RODADA4.json'
    # Execução posterior não apaga a evidência desta primeira migração.
    immutable(DEFAULT_OUT/'reviewed'/'round4'/f'reconversion-{digest(json.dumps(report,sort_keys=True))}.json',json.dumps(report,ensure_ascii=False,indent=2).encode())
    if changes or not target.exists(): write_json(target,report)
    print(json.dumps({'changed_pages':len(changes)},ensure_ascii=False))


if __name__=='__main__': main()
