"""Record Moscow investigation progress and import completed documents locally.

Uses explicit completion markers so partial drafts are never registered. Each
--apply-ready transaction preserves a recoverable editorial history entry.
No translation service, publication, or tests are invoked.
"""
import argparse
import copy
import csv
import json
from pathlib import Path

import import_leningrad_translations as batch

batch.REPORT = batch.ROOT / 'docs/traducoes/moscou-investigacao'
batch.WORK = batch.ROOT / '.local/traducoes/moscou-investigacao'


def progress():
    scope, result, contents = batch.collect()
    current = batch.model.load(batch.ROOT)
    existing = {(e['document_id'], e['language']): e for e in current['editions']}
    for row in result['editions']:
        pair = row['document_id'], row['language']
        marker = batch.WORK / 'concluidas' / (pair[0] + '.' + pair[1] + '.json')
        if pair in existing:
            row['status'] = 'ja_cadastrada_preservada'
        elif row['status'] in {'preparada', 'aguarda_titulo'}:
            if not marker.exists():
                row['status'] = 'em_redacao'
            else:
                completion = json.loads(marker.read_text())
                if (completion.get('document_id'), completion.get('language'), completion.get('sha256')) != (pair[0], pair[1], row['sha256']):
                    row['status'] = 'marcador_divergente'
    result['registered'] = sum(r['status'] == 'ja_cadastrada_preservada' for r in result['editions'])
    result['prepared'] = sum(r['status'] == 'preparada' for r in result['editions'])
    (batch.REPORT / 'progresso.json').write_bytes(batch.model.json_bytes(result))
    with (batch.REPORT / 'progresso.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['documento', 'idioma', 'status', 'blocos_original', 'blocos_traducao', 'avisos', 'arquivo'])
        for row in result['editions']:
            writer.writerow([row['document_id'], row['language'], row['status'],
                             row['original_structure']['study_blocks'],
                             row.get('translated_structure', {}).get('study_blocks', ''),
                             '; '.join(row['warnings']), row['file']])
    return scope, result, contents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply-ready', action='store_true')
    parser.add_argument('--limit', type=int, default=30, help='Maximum complete documents per transaction.')
    args = parser.parse_args()
    scope, result, contents = progress()
    print(json.dumps({k:v for k,v in result.items() if k != 'editions'}, ensure_ascii=False), flush=True)
    if not args.apply_ready:
        return
    by_document = {}
    for row in result['editions']:
        by_document.setdefault(row['document_id'], []).append(row)
    selected = []
    for document in scope['pending']:
        rows = by_document[document['id']]
        if any(r['status'] == 'preparada' for r in rows) and all(r['status'] in {'preparada', 'ja_cadastrada_preservada'} for r in rows):
            selected.append(document['id'])
        if len(selected) >= args.limit:
            break
    if not selected:
        print('Nenhum documento completo novo para cadastrar.')
        return
    subset_scope = copy.deepcopy(scope)
    subset_scope['pending'] = [d for d in scope['pending'] if d['id'] in selected]
    subset_result = copy.deepcopy(result)
    subset_result['editions'] = [r for r in result['editions'] if r['document_id'] in selected and r['status'] == 'preparada']
    subset_result['requested'] = subset_result['prepared'] = len(subset_result['editions'])
    subset_contents = {r['file']: contents[r['file']] for r in subset_result['editions']}
    history_path = batch.REPORT / 'gravacoes.json'
    history = json.loads(history_path.read_text()) if history_path.exists() else []
    batch.BATCH_ID = f'traducoes-moscou-investigacao-{len(history)+1:04d}'
    batch.apply(subset_scope, subset_result, subset_contents)
    saved = json.loads((batch.REPORT / 'gravacao.json').read_text())
    history.append({'documents': selected, 'editions': len(subset_result['editions']), 'save': saved})
    history_path.write_bytes(batch.model.json_bytes(history))
    progress()


if __name__ == '__main__':
    main()
