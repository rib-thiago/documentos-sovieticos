"""Apply the recorded facsimile collation of no.100; no canonical writes."""
import copy
import difflib
import hashlib
import json
import re
from pathlib import Path

BASE = Path('temporario/coletas-quatro/mozokhin')
WORK = BASE / 'lista100'
OUT = BASE / 'reviewed/mozokhin100-round5-20261021'
EXPECTED_PDF = 'e126b2104b4c2d0b508811388544d0556ecd727d62abe0daa7eafee7fbf0302d'
EXPECTED_ROWS = '373bb67098d1ff9f584a674f31490dacd2887a9c9e94d5c69462bea72eb2ff87'
EXPECTED_OLD = 'c2e65f9e0c73c1bf8eee00c5134f635e6551ac82deed796a0774553188ed79fa'
sha = lambda b: hashlib.sha256(b).hexdigest()

def main():
    units = json.loads((BASE / 'units.json').read_text())
    unit = next(u for u in units if u['id'] == 'mozokhin-2013-v1-100')
    if unit.get('provenance', {}).get('review_decision') == 'mozokhin100-round5-20261021':
        print('Already prepared; no writes.'); return
    assert sha((BASE / unit['raw']).read_bytes()) == EXPECTED_PDF
    assert sha((WORK / 'rows.json').read_bytes()) == EXPECTED_ROWS
    old = (BASE / unit['markdown']).read_text()
    assert sha(old.encode()) == EXPECTED_OLD
    rows = json.loads((WORK / 'rows.json').read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'unit-before.json').write_text(json.dumps(unit, ensure_ascii=False, indent=2)+'\n')
    checks = []
    for row in rows:
        before = copy.deepcopy(row)
        label = row['label_literal']
        if row['pdf_page'] == 178 and label in ('575', '576'):
            row['name_text_layer'] = row['name_text_layer'].replace('НИКОЛ АЙ', 'НИКОЛАЙ')
        if row['pdf_page'] == 177 and label == '539':
            row['name_text_layer'] = row['name_text_layer'].replace('МЕП А РЕЙ', 'МЕПАРЕЙ')
        if row['pdf_page'] == 180:
            row['year_text_layer'] = row['year_text_layer'].replace(' ', '')
        row['qualification'] = ''
        if row['pdf_page'] == 177 and label == '516':
            row['name_text_layer'] = 'МЕЛЬНИКОВ'
            row['qualification'] = 'кандидат'
        checks.append({'pdf_page': row['pdf_page'], 'column': row['column'],
                       'line_in_column': row['line_in_column'], 'before': before,
                       'after': row, 'basis': 'facsimile visual collation',
                       'scope': 'literal transcription, not historical identification'})
    intro = old[:old.index('1. АСРАТЯН')]
    intro = re.sub(r'(?m)^17[0-2]\s*$', '', intro)
    intro = intro.replace('л и ц .', 'лиц.')
    intro = re.sub(r'\n{3,}', '\n\n', intro).rstrip()
    md = [intro, '', '> **Nota editorial / Редакционное примечание.** A carta declara 863 assinaturas; a lista impressa contém 858 linhas físicas, duas delas retocadas (notas 38 e 39), e seu último rótulo é 865. Mantivemos os números e campos vazios da edição, inclusive repetições e saltos. Não se inferiram nomes ausentes nem anos. A coluna «Observação literal» contém apenas a qualificação impressa «кандидат». As divisões por página abaixo são editoriais e correspondem ao PDF-fonte.', '']
    for page in range(174,181):
        md += [f'## Lista — PDF {page}, página impressa {page-1}', '',
               '| Nº literal | Nome | Ano / indicação da fonte | Observação literal |',
               '| --- | --- | --- | --- |']
        for r in rows:
            if r['pdf_page'] == page:
                name = r['name_text_layer'] + (f"[^{r['note']}]" if r['note'] else '')
                md.append('| '+' | '.join([r['label_literal'], name, r['year_text_layer'], r['qualification']])+' |')
        md += ['']
    md += ['РГАСПИ. Ф. 17. Оп. 171. Д. 88. Л. 100–111. Подлинник. Машинопись.', '',
           '[^38]: Строка заретуширована', '', '[^39]: Строка заретуширована', '']
    new = '\n'.join(md)
    digest = sha(new.encode())
    dest = OUT / f'mozokhin-2013-v1-100.{digest}.ru.md'
    dest.write_text(new)
    (OUT / 'changes.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile=unit['markdown'], tofile=str(dest))))
    decision = {'document':unit['id'], 'decision':'ready_with_explicit_source_anomalies',
                'source_sha256':EXPECTED_PDF, 'previous_sha256':EXPECTED_OLD,
                'markdown_sha256':digest, 'rows':858, 'declared_signatures':863,
                'last_literal_label':865, 'physical_pages':list(range(171,181)),
                'method':'Cotejo visual sequencial de carta171–174 e lista174–180; sem identificação prosopográfica, sem conjecturas nem renumeração.',
                'table_checks':checks, 'intro_changes':['Removeu rodapés170/171/172 do corpo; paginação preservada na proveniência.', 'Desfez espaços de extração l и ц → лиц, confirmado na página173.'],
                'remaining':'Divergências históricas/aritméticas pertencem à fonte; grafias literais não foram verificadas contra outros testemunhos.'}
    (OUT / 'decision.json').write_text(json.dumps(decision, ensure_ascii=False, indent=2)+'\n')
    unit['markdown'] = str(dest.relative_to(BASE)); unit['markdown_sha256'] = digest
    unit['ready_for_import'] = True
    unit['date_literal'] = '18 октября 1927 г.'
    unit['archive_reference'] = 'РГАСПИ. Ф. 17. Оп. 171. Д. 88. Л. 100–111. Подлинник. Машинопись.'
    unit['issues'] = ['Nota editorial explícita:863 assinaturas declaradas,858 linhas físicas,último rótulo865; numeração irregular e campos vazios preservados.', 'Grafias literais cotejadas visualmente; identificação histórica de pessoas e comparação com outros testemunhos não realizadas.']
    unit['provenance'].update({'previous_markdown':str(json.loads((OUT/'unit-before.json').read_text())['markdown']), 'previous_markdown_sha256':EXPECTED_OLD, 'review_decision':'mozokhin100-round5-20261021', 'review_record':str((OUT/'decision.json').relative_to(BASE)), 'reviewed_pdf_pages':list(range(171,181)), 'editorial_review':'visual_literal_collation_with_explicit_source_anomalies', 'text_extraction':'Existing PDF text layer, bbox reconstruction, visual collation; no new OCR', 'footer_note_review_required':False, 'date_source':'printed signature PDF174', 'archive_reference_source':'printed source citation PDF180'})
    (BASE / 'units.json').write_text(json.dumps(units, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'ready':unit['id'],'markdown':unit['markdown'],'sha256':digest,'rows':len(rows)}))

if __name__ == '__main__':
    main()
