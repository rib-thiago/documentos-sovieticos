#!/usr/bin/env python3
"""Cotejo documental local, sem gravação no acervo ou execução de testes.

Requer beautifulsoup4 (ambiente de aquisição). Não reutiliza o conversor.
"""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'temporario/revisao-onda1/militares'
KEYS = ['aviation-korolev-1935', 'gosplan-aircraft-1935', 'rkka-raw-materials-1934']

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def plain(s):
    s = re.sub(r'!?\[([^\]]+)\]\([^\n]*?\)', r'\1', s)
    s = re.sub(r'\\([\\`*_{}\[\]()#+.!|>-])', r'\1', s)
    s = re.sub(r'[*_`#]', '', s)
    return re.sub(r'\s+', '', s)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    documents = []
    for key in KEYS:
        ident = 'military-' + key
        source = ROOT / f'.local/research/military-1934-1936/raw/{key}.html'
        metadata = json.loads((source.parent.parent / f'{key}.json').read_text())
        assert digest(source) == metadata['sha256'], 'Fonte alterada'
        target = ROOT / f'originais/militares/{ident}.ru.md'
        text = target.read_text()
        body = BeautifulSoup(source.read_bytes(), 'html.parser').select_one('.field-name-body .field-item')
        md_tables = re.findall(r'^\|.*(?:\n\|.*)*', text, re.M)
        html_tables = body.select('table')
        assert len(md_tables) == len(html_tables)
        evidence = []
        for n, (table, md) in enumerate(zip(html_tables, md_tables), 1):
            cells, grid = [], {}
            rows = table.find_all('tr')
            for r, row in enumerate(rows):
                c = 0
                for cell in row.find_all(['td', 'th'], recursive=False):
                    while (r, c) in grid:
                        c += 1
                    value = cell.get_text('', strip=False)
                    rs, cs = int(cell.get('rowspan', 1)), int(cell.get('colspan', 1))
                    item = dict(row=r+1, column=c+1, rowspan=rs, colspan=cs, text=value)
                    cells.append(item)
                    for rr in range(r, r+rs):
                        for cc in range(c, c+cs):
                            assert (rr, cc) not in grid
                            grid[rr, cc] = item
                    c += cs
            width = max(c for r, c in grid) + 1
            header_count = max(x['rowspan'] for x in cells if x['row'] == 1)
            lines = [re.split(r'(?<!\\)\|', ln)[1:-1] for ln in md.splitlines()]
            assert len(lines[0]) == width
            comparisons = []
            for c in range(width):
                parts = []
                for r in range(header_count):
                    value = grid.get((r, c), {}).get('text', '')
                    if plain(value) and plain(value) not in [plain(p) for p in parts]:
                        parts.append(value)
                expected = ' / '.join(parts) or ('Показатель' if c == 0 else f'Столбец {c+1}')
                comparisons.append(dict(markdown_row=1, column=c+1, expected=expected, actual=lines[0][c], equal=plain(expected)==plain(lines[0][c])))
            for r in range(header_count, len(rows)):
                for c in range(width):
                    owner = grid.get((r, c))
                    expected = '' if owner is None else owner['text'] if (owner['row'],owner['column']) == (r+1,c+1) else '↳'
                    actual = lines[r-header_count+2][c]
                    comparisons.append(dict(html_row=r+1,column=c+1,expected=expected,actual=actual,equal=plain(expected)==plain(actual)))
            evidence.append(dict(table=n,html_rows=len(rows),columns=width,header_rows=header_count,cells=cells,comparisons=comparisons,all_equal=all(x['equal'] for x in comparisons),merged_cells=sum(x['rowspan']>1 or x['colspan']>1 for x in cells),empty_cells=sum(not plain(x['text']) for x in cells)))
        # Conferência separada de todos os parágrafos fora das tabelas, incluindo notas.
        paragraphs = [p for p in body.find_all(['p','h1','h2','h3','h4','h5','h6']) if not p.find_parent('table')]
        normalized = plain(text)
        passages = []
        cursor = 0
        for i, p in enumerate(paragraphs, 1):
            value = p.get_text('', strip=False)
            offset = normalized.find(plain(value), cursor)
            passages.append(dict(index=i,text=value,present=offset >= 0,ordered_offset=offset))
            if offset >= 0:
                cursor = offset + len(plain(value))
        documents.append(dict(document_id=ident,file=str(target.relative_to(ROOT)),before_sha256=digest(target),source=str(source.relative_to(ROOT)),source_sha256=digest(source),url=metadata['original_url'],capture=metadata['capture_timestamp'],tables=evidence,paragraphs=passages,table_mismatches=sum(not c['equal'] for t in evidence for c in t['comparisons']),missing_paragraphs=[p for p in passages if not p['present']]))
    (OUT/'cotejo.json').write_text(json.dumps(documents, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps([{k:d[k] for k in ['document_id','table_mismatches','missing_paragraphs']} for d in documents], ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
