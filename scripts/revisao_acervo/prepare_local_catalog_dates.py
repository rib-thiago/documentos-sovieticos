#!/usr/bin/env python3
"""Normaliza a representação de datas já cadastradas; não consulta fontes externas.

Não valida a data histórica/publicação e não encerra a revisão de conteúdo ou UI.
"""
import csv
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from backend import catalog as model

WORK = ROOT / 'temporario/revisao-onda5'
OUT = WORK / 'catalogo-local'


def main():
    catalog = model.load(ROOT)
    documents = {d['id']: d for d in catalog['documents']}
    manifest = json.loads((WORK / 'baseline/manifest.json').read_text())
    owners = {d['id']: b['id'] for b in manifest['batches'] for d in b['documents']}
    results, summary = {}, []
    OUT.mkdir(exist_ok=True)
    for row in csv.DictReader((WORK / 'baseline/queue.csv').open()):
        if row['problema'] != 'cadastro_local' or row['status'] == 'corrigido':
            continue
        uid = row['id']
        doc = documents[uid]
        before = doc['historical_date']
        display = before['display'] or ''
        if before['value'] is not None or before['precision'] != 'not_recorded':
            raise ValueError('Data já estruturada; não sobrescrever: ' + uid)
        year = re.fullmatch(r'\d{4}', display)
        numeric = re.fullmatch(r'(\d{2})/(\d{2})/(\d{4})', display)
        portuguese = re.fullmatch(r'(\d{1,2}) de junho de (\d{4})', display)
        url_date = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', urlsplit(doc['source'].get('url') or '').path)
        if year:
            value, precision = display, 'year'
        elif numeric:
            day, month, year_value = map(int, numeric.groups())
            value, precision = date(year_value, month, day).isoformat(), 'day'
            if not url_date or value != '-'.join(url_date.groups()):
                raise ValueError('Rótulo numérico sem concordância com o caminho já cadastrado: ' + uid)
        elif portuguese:
            day, year_value = map(int, portuguese.groups())
            value, precision = date(year_value, 6, day).isoformat(), 'day'
        else:
            raise ValueError('Formato exige decisão, não normalização automática: ' + uid)
        after = {'display': display, 'value': value, 'precision': precision}
        evidence = {'document_id': uid, 'before_date': before, 'after_date': after,
                    'source_url_already_in_catalog': doc['source'].get('url'),
                    'url_path_date_matches_label': bool(url_date),
                    'basis': 'Transcrição estruturada do rótulo de data já existente. Exibição preservada; ano não convertido em 1º de janeiro. Caminho URL usado apenas para desambiguar os nove rótulos numéricos.',
                    'not_verified': ['Data real de publicação na página externa', 'Autoria e metadados gerais', 'Revisão integral de conteúdo/traduções', 'Apresentação no navegador'],
                    'editions_preserved': [{k: e[k] for k in ['id', 'file', 'sha256']} for e in catalog['editions'] if e['document_id'] == uid]}
        ep = OUT / (uid + '.evidence.json')
        ep.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
        bid = owners[uid]
        result = results.setdefault(bid, {'batch_id': bid, 'editions': [], 'documents': [], 'issues': []})
        result['documents'].append({'document_id': uid, 'before_sha256': model.sha256(model.json_bytes(doc)),
                                    'fields': {'historical_date': after}, 'source_evidence': str(ep.relative_to(ROOT))})
        result['issues'].append({'key': row['chave'], 'outcome': 'parcial', 'evidence': str(ep.relative_to(ROOT)),
                                 'next_action': 'Representação ISO da data já cadastrada normalizada; rótulo, URLs, autoria e textos preservados. Ainda conferir autoria/proveniência na fonte, conteúdo/traduções e apresentação manual no leitor. Não é confirmação externa da data.'})
        summary.append({'id': uid, 'date': after, 'review_remains_open': True})
    for bid, result in results.items():
        (OUT / (bid + '.result.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'SUMMARY.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print('Normalizações preparadas:', len(summary), '; revisões gerais continuam abertas.')


if __name__ == '__main__':
    main()
