"""Register the directly translated Leningrad investigation drafts as one local batch.

Default action records progress and structural diagnostics. --apply requires every
requested edition, preserves existing editions, and uses recoverable editorial
history. It neither translates nor publishes. No external dependencies.
"""
import argparse
import copy
import csv
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import catalog as model
from backend import translations
from backend.database import Repository
from backend.editorial import Editorial

REPORT = ROOT / 'docs/traducoes/leningrado-investigacao'
WORK = ROOT / '.local/traducoes/leningrado-investigacao'
BATCH_ID = 'traducoes-leningrado-investigacao'


def collect():
    scope = json.loads((REPORT / 'escopo.json').read_text())
    titles = {}
    for file in sorted(WORK.glob('titulos-lote-*.json')):
        for ident, langs in json.loads(file.read_text()).items():
            titles.setdefault(ident, {}).update(langs)
    rows, contents = [], {}
    for document in scope['pending']:
        source = ROOT / document['source']
        if model.sha256(source.read_bytes()) != document['source_sha256']:
            raise RuntimeError('O original mudou desde a preparação: ' + document['id'])
        original = source.read_text()
        original_structure = translations.structure(original)
        for language in document['languages']:
            filename = document['id'] + '.' + language + '.md'
            draft = WORK / 'preparadas' / filename
            row = {'document_id': document['id'], 'language': language,
                   'source_sha256': document['source_sha256'], 'status': 'pendente',
                   'file': 'originais/showtrials/' + filename,
                   'title': titles.get(document['id'], {}).get(language),
                   'original_structure': original_structure, 'warnings': []}
            if draft.is_file():
                content = draft.read_text()
                if not content.strip():
                    raise RuntimeError('Tradução vazia: ' + filename)
                if translations.split_export_headers(content)['header_count']:
                    raise RuntimeError('Remova o cabeçalho de exportação do rascunho: ' + filename)
                if content.strip() == original.strip():
                    raise RuntimeError('Rascunho idêntico ao original russo: ' + filename)
                row['translated_structure'] = translations.structure(content)
                row['sha256'] = model.sha256(content.encode())
                row['bytes'] = len(content.encode())
                row['status'] = 'preparada' if row['title'] else 'aguarda_titulo'
                if original_structure['study_blocks'] != row['translated_structure']['study_blocks']:
                    row['warnings'].append('Contagem de blocos diferente; cotejar fronteiras com o original.')
                # Diagnose suspiciously short extraction, without changing or aligning it.
                if len(content) < len(original) * .45:
                    row['warnings'].append('Tradução relativamente curta; conferir integralidade.')
                cyrillic = len(re.findall('[А-Яа-яЁё]', content))
                if cyrillic / max(1, len(content)) > .1:
                    row['warnings'].append('Proporção elevada de cirílico; conferir trechos não traduzidos.')
                contents[row['file']] = content
            rows.append(row)
    result = {'documents': len(scope['pending']), 'requested': len(rows),
              'prepared': sum(r['status'] == 'preparada' for r in rows),
              'drafts': len(contents), 'with_warnings': sum(bool(r['warnings']) for r in rows),
              'editions': rows}
    (REPORT / 'progresso.json').write_bytes(model.json_bytes(result))
    with (REPORT / 'progresso.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.writer(stream)
        writer.writerow(['documento', 'idioma', 'status', 'blocos_original', 'blocos_traducao', 'avisos', 'arquivo'])
        for row in rows:
            writer.writerow([row['document_id'], row['language'], row['status'],
                             row['original_structure']['study_blocks'],
                             row.get('translated_structure', {}).get('study_blocks', ''),
                             '; '.join(row['warnings']), row['file']])
    return scope, result, contents


def apply(scope, result, contents):
    if result['prepared'] != result['requested']:
        raise RuntimeError('Lote ainda incompleto; nenhum documento será cadastrado.')
    editorial = Editorial(ROOT)
    try:
        current = model.load(ROOT)
        # Preserve the editions already present when this task started.
        for edition in scope['existing_editions']:
            if model.sha256((ROOT / edition['file']).read_bytes()) != edition['sha256']:
                raise RuntimeError('Uma edição existente mudou; conferir antes de importar: ' + edition['file'])
        candidate = copy.deepcopy(current)
        documents = {doc['id']: doc for doc in candidate['documents']}
        editions = {(e['document_id'], e['language']) for e in candidate['editions']}
        changes = []
        files = dict(contents)
        for row in result['editions']:
            ident, lang = row['document_id'], row['language']
            if (ident, lang) in editions or (ROOT / row['file']).exists():
                raise RuntimeError('Versão já existente; não será sobrescrita: ' + row['file'])
            position = max((e['position'] for e in candidate['editions'] if e['document_id'] == ident), default=-1) + 1
            candidate['editions'].append({'id': ident + ':' + lang, 'document_id': ident,
                'language': lang, 'label': 'Tradução portuguesa' if lang == 'pt' else 'Tradução inglesa',
                'file': row['file'], 'format': 'markdown', 'position': position,
                'sha256': row['sha256'], 'bytes': row['bytes'], 'editorial_status': 'not_recorded',
                'extra': {}, 'compatibility_fields': ['code', 'label', 'file', 'format']})
            # Existing translated titles belong to the user's metadata; preserve them.
            documents[ident]['titles'].setdefault(lang, row['title'])
            changes.append({'field': ident + ' / Tradução ' + lang.upper(), 'before': None,
                            'after': {'file': row['file'], 'sha256': row['sha256']}})
        for name in ['documents', 'editions']:
            if current[name] != candidate[name]:
                files['data/catalog/' + name + '.json'] = model.json_bytes(candidate[name]).decode()
        files['data/manifest.json'] = model.json_bytes(model.export_manifest(candidate)).decode()
        ids = [doc['id'] for doc in scope['pending']]
        preview = editorial.store_preview(editorial.revision(), candidate, files, None, changes,
            entity={'kind': 'batch', 'id': BATCH_ID, 'document_ids': ids})
        repository = Repository(ROOT, ROOT / '.local/catalog.sqlite3', current, {})
        saved = editorial.save(repository, {'preview_id': preview['preview_id']})
        (REPORT / 'gravacao.json').write_bytes(model.json_bytes(saved))
        print(json.dumps(saved, ensure_ascii=False))
    finally:
        editorial.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    scope, result, contents = collect()
    print(json.dumps({k:v for k,v in result.items() if k != 'editions'}, ensure_ascii=False))
    if args.apply:
        apply(scope, result, contents)


if __name__ == '__main__':
    main()
