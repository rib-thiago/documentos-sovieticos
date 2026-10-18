"""Assemble complete session translations and import the three proceedings locally.

No translation engine, publication, or test execution. The three internal chunks
remain work files; the reader receives one whole edition per language/document.
"""
import json
import re
from pathlib import Path

import import_leningrad_translations as batch

batch.REPORT = batch.ROOT / 'docs/traducoes/leningrado-andamento'
batch.WORK = batch.ROOT / '.local/traducoes/leningrado-andamento'
batch.BATCH_ID = 'traducoes-leningrado-andamento'


def assemble():
    scope = json.loads((batch.REPORT / 'escopo.json').read_text())
    # The final 180 blocks of part 2 were handed off to the first available
    # translator; join only at the recorded boundary, never by text guessing.
    for language in ['pt', 'en']:
        main = batch.WORK / 'preparadas' / f'2618-parte-2.{language}.md'
        tail = batch.WORK / 'preparadas' / f'2618-parte-2-final.{language}.md'
        if main.exists() and tail.exists():
            head_text, tail_text = main.read_text().strip(), tail.read_text().strip()
            head_blocks = len(re.split(r'\n\s*\n', head_text))
            tail_blocks = len(re.split(r'\n\s*\n', tail_text))
            if head_blocks == 714 and tail_blocks == 180:
                main.write_text(head_text + '\n\n' + tail_text + '\n')
    diagnostics = []
    complete = True
    for language in ['pt', 'en']:
        contents = []
        for part in scope['parts']:
            file = batch.WORK / 'preparadas' / f"2618-parte-{part['part']}.{language}.md"
            content = file.read_text() if file.exists() else ''
            blocks = len([b for b in re.split(r'\n\s*\n', content.strip()) if b.strip()])
            diagnostics.append({'part': part['part'], 'language': language,
                                'expected_blocks': part['blocks'], 'translated_blocks': blocks})
            if blocks != part['blocks']:
                complete = False
            contents.append(content.strip())
        if all(row['expected_blocks'] == row['translated_blocks']
               for row in diagnostics if row['language'] == language):
            output = batch.WORK / 'preparadas' / f'showtrials-2618.{language}.md'
            output.write_text('\n\n'.join(contents) + '\n')
    (batch.REPORT / 'partes.json').write_bytes(batch.model.json_bytes(diagnostics))
    if not complete:
        print(json.dumps({'session_complete': False, 'parts': diagnostics}, ensure_ascii=False))
        raise SystemExit('A sessão ainda está incompleta; nenhuma versão parcial será cadastrada.')
    normalized = []
    for language in ['pt', 'en']:
        file = batch.WORK / 'preparadas' / f'showtrials-2618.{language}.md'
        content = file.read_text()
        revised = re.sub(r'\bULRICH\b', 'ULRIKH', content)
        revised = re.sub(r'\bUlrich\b', 'Ulrikh', revised)
        if revised != content:
            file.write_text(revised)
            normalized.append(file.name)
    (batch.REPORT / 'padronizacao.json').write_bytes(batch.model.json_bytes({
        'transliteration': {'Ulrich': 'Ulrikh', 'ULRICH': 'ULRIKH'},
        'files': normalized, 'scope': 'Somente novas versões; originais preservados.'}))
    # Editorial inventory of reference markers; this does not align or rewrite text.
    markers = []
    for ident in scope['documents']:
        source = (batch.ROOT / f'originais/showtrials/{ident}.ru.md').read_text()
        reference = re.findall(r'\\?\[(\d+|i)\\?\]', source)
        for language in ['pt', 'en']:
            target = (batch.WORK / 'preparadas' / f'{ident}.{language}.md').read_text()
            translated = re.findall(r'\\?\[(\d+|i)\\?\]', target)
            markers.append({'document_id': ident, 'language': language,
                            'original_markers': reference, 'translated_markers': translated,
                            'same_sequence': reference == translated})
    (batch.REPORT / 'marcadores-notas.json').write_bytes(batch.model.json_bytes(markers))
    if any(not row['same_sequence'] for row in markers):
        raise SystemExit('Há divergências de marcadores de notas; conferir os textos antes de cadastrar.')


if __name__ == '__main__':
    assemble()
    batch.main()
