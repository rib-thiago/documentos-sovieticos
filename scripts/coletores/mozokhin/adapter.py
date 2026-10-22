"""Conservative, dependency-free staging adapter for the Mozokhin 2013 books.

Never writes public catalog files. Printed document numbers must occur in source
headings; catalog row position is deliberately not an identity source.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re

HEADER = re.compile(r"(?m)^[ \t\f]*(?:№|N[oо]|N[º°])\s*(\d{1,3})[ \t]*[.:]?[ \t]*$")
TOC = re.compile(r"(?mi)^[ \t\f]*(?:Содержание|Оглавление)[ \t]*$")
# The second book has a long personal commentary AFTER its last document.
END = re.compile(r"(?mi)^[ \t\f]*(?:Содержание|Оглавление|ИМЕННОЙ[ \t]+КОММЕНТАРИЙ\d*)[ \t]*$")


def normalized(value):
    return ''.join(re.findall('[а-яёa-z0-9]', value.lower()))


def printed_contents(text, first, last):
    """Read actual printed numbers from the final contents, never list position."""
    markers = list(TOC.finditer(text))
    if not markers or markers[-1].start() < len(text) * .5:
        return {}
    contents = text[markers[-1].end():]
    matches = list(re.finditer(r'(?m)^[ \t\f]*(?:№|No)\s*(\d{1,3})\.\s*', contents))
    titles = {}
    for i, match in enumerate(matches):
        number = int(match[1])
        if not first <= number <= last:
            continue
        stop = matches[i + 1].start() if i + 1 < len(matches) else len(contents)
        block = contents[match.end():stop]
        title = re.split(r'\.{3,}|(?:\s*\.\s*){5,}', block)[0]
        title = re.sub(r'\s+', ' ', title).strip()
        if number in titles:
            raise ValueError(f'Número {number} repetido no sumário; conciliação manual necessária')
        titles[number] = title
    return titles


class ReaderHTML(HTMLParser):
    """Only explicit OCR/pre blocks qualify; never treat the whole page as book."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.active = None
        self.blocks = []
        self.current = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        hint = (attrs.get('id', '') + ' ' + attrs.get('class', '')).lower()
        if tag not in {'br', 'hr', 'img', 'input', 'meta', 'link', 'source', 'wbr'}:
            self.depth += 1
            if self.active is None and (tag in {'pre', 'textarea'} or re.search(r'\b(?:ocr|book-text|reader-text)\b', hint)):
                self.active = self.depth
                self.current = []
        if self.active and tag in {'br', 'p', 'div', 'tr'}:
            self.current.append('\n')

    def handle_endtag(self, tag):
        if tag in {'br', 'hr', 'img', 'input', 'meta', 'link', 'source', 'wbr'}:
            return
        if self.active == self.depth:
            self.blocks.append(''.join(self.current))
            self.active = None
        self.depth = max(0, self.depth - 1)

    def handle_data(self, data):
        if self.active:
            self.current.append(data)


def extract_reader(html):
    parser = ReaderHTML()
    parser.feed(html)
    blocks = [b for b in parser.blocks if len(re.findall('[А-Яа-яЁё]', b)) >= 200 and HEADER.search(b)]
    if not blocks:
        raise ValueError('Nenhum bloco OCR confiável; possível verificação de acesso ou página incompleta')
    return max(blocks, key=len).replace('\r\n', '\n').replace('\r', '\n').replace('\xa0', ' ')


def segment(text, first, last, *, source_complete=False, titles=None):
    """Every observed heading is a boundary, even after a numbering gap.

    A gap quarantines the PRECEDING block: its missing next heading means that
    block might already include another document. Nothing is silently repaired.
    Final blocks require an observed end marker and complete-source declaration.
    """
    if not 1 <= first <= last <= 999:
        raise ValueError('Intervalo documental inválido')
    end = END.search(text)
    cutoff = end.start() if end else len(text)
    hits = [m for m in HEADER.finditer(text[:cutoff]) if first <= int(m[1]) <= last]
    rejected = []
    ambiguous = set()
    if titles:
        selected = []
        for number in range(first, last + 1):
            group = [m for m in hits if int(m[1]) == number]
            scored = []
            for match in group:
                expected = normalized(titles.get(number, ''))[:80]
                observed = normalized(text[match.end():match.end() + 900])[:len(expected)]
                score = SequenceMatcher(None, expected, observed).ratio() if expected else 0
                scored.append((score, match))
            good = [(score, match) for score, match in scored if score >= .8]
            if len(good) == 1:
                selected.append(good[0][1])
                for score, match in scored:
                    if match is not good[0][1]:
                        rejected.append({'number': number, 'offset': match.start(), 'reason': 'Referência interna: título diverge do sumário impresso', 'title_similarity': score})
            else:
                # Retain uncertain observed boundaries rather than merge silently.
                selected.extend(group)
                ambiguous.add(number)
        hits = sorted(selected, key=lambda match: match.start())
    counts = Counter(int(m[1]) for m in hits)
    sections = []
    for i, hit in enumerate(hits):
        number = int(hit[1])
        next_hit = hits[i + 1] if i + 1 < len(hits) else None
        stop = next_hit.start() if next_hit else cutoff
        body = text[hit.start():stop].strip()
        issues = ['OCR e fronteiras ainda exigem conferência com o fac-símile; tabelas não reconstruídas']
        blocking = []
        if number in ambiguous:
            blocking.append('Correspondência entre cabeçalho e sumário ambígua ou insuficiente')
        if counts[number] > 1:
            blocking.append('Número repetido: possível referência interna ou erro de OCR')
        if next_hit and int(next_hit[1]) != number + 1:
            blocking.append('Próximo cabeçalho fora de sequência; bloco anterior pode conter documento sem cabeçalho')
        if not next_hit and not (number == last and end and source_complete):
            blocking.append('Fim documental não comprovado: limite do extrato ou fonte parcial')
        if i and number <= int(hits[i - 1][1]):
            blocking.append('Numeração regressiva: revisar identificação documental')
        title_lines = body.splitlines()[1:3]
        sections.append({'number': number, 'title_literal': ' '.join(x.strip() for x in title_lines),
                         'start': hit.start(), 'end': stop, 'text': body,
                         'status': 'blocked_boundary' if blocking else 'candidate_unreviewed',
                         'issues': blocking + issues})
    return {'sections': sections, 'missing': sorted(set(range(first, last + 1)) - set(counts)),
            'rejected_internal_headers': rejected,
            'end_marker_found': bool(end), 'source_complete_declared': source_complete}


def snapshot(root, data, suffix):
    digest = sha256(data).hexdigest()
    path = root / 'raw' / (digest + suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open('xb') as handle:
            handle.write(data)
    return path, digest


def stage(input_path, output, source_url, first, last, *, kind='text', complete=False, edition='2013-v1'):
    if edition == '2017':
        raise ValueError('Edição de 2017: referência parcial, não autorizada como fonte integral pelo adaptador')
    output = Path(output)
    data = Path(input_path).read_bytes()
    raw_path, digest = snapshot(output, data, Path(input_path).suffix or '.txt')
    text = data.decode('utf-8-sig')
    if kind == 'html':
        text = extract_reader(text)
    titles = printed_contents(text, first, last) if complete else {}
    result = segment(text, first, last, source_complete=complete, titles=titles)
    if kind == 'web_excerpt':
        for section in result['sections']:
            section['status'] = 'blocked_partial_acquisition'
            section['issues'].insert(0, 'Extrato de ferramenta web: ausência de fonte integral; incorporação bloqueada')
    index_path = output / 'inventory.json'
    inventory = json.loads(index_path.read_text()) if index_path.exists() else {'schema': 1, 'items': {}}
    stamp = datetime.now(timezone.utc).isoformat()
    run = {'source_url': source_url, 'input_kind': kind, 'source_sha256': digest,
           'raw_path': str(raw_path), 'processed_at': stamp, 'edition': edition,
           'missing_in_supplied_range': result['missing'], 'documents': []}
    run['rejected_internal_headers'] = result['rejected_internal_headers']
    run['printed_contents_count'] = len(titles)
    for section in result['sections']:
        ident = f'mozokhin-{edition}-{section["number"]:03d}'
        body = section.pop('text')
        # Preserve OCR line structure, notes, tables flattened by upstream OCR.
        heading = titles.get(section['number'], section['title_literal'])
        markdown = '# ' + heading + '\n\n' + '\n'.join(line.lstrip() for line in body.splitlines()) + '\n'
        md_hash = sha256(markdown.encode()).hexdigest()
        path = output / 'candidates' / ident / (md_hash + '.ru.md')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(markdown, encoding='utf-8')
        record = dict(section, id=ident, language='ru', markdown_path=str(path),
                      markdown_sha256=md_hash, source_sha256=digest, source_url=source_url,
                      raw_path=str(raw_path), input_kind=kind, edition=edition,
                      title_status='literal_suggestion_unreviewed',
                      fulltext_acquired=bool(complete and kind != 'web_excerpt'))
        if section['number'] in titles:
            record['title_literal'] = titles[section['number']]
            record['title_status'] = 'printed_contents_correspondence_unreviewed'
        key = f'{ident}:{digest}:{section["start"]}'
        inventory['items'][key] = record
        run['documents'].append(record)
    runs = output / 'runs'
    runs.mkdir(exist_ok=True)
    run_path = runs / (stamp.replace(':', '-') + '.json')
    run_path.write_text(json.dumps(run, ensure_ascii=False, indent=2) + '\n')
    temp = index_path.with_suffix('.tmp')
    temp.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')
    temp.replace(index_path)
    return run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-url', required=True)
    parser.add_argument('--first', type=int, required=True)
    parser.add_argument('--last', type=int, required=True)
    parser.add_argument('--kind', choices=['html', 'text', 'web_excerpt'], default='text')
    parser.add_argument('--edition', choices=['2013-v1', '2013-v2', '2017'], required=True)
    parser.add_argument('--complete', action='store_true', help='Somente para livro integral, nunca para extrato')
    args = parser.parse_args()
    if args.kind == 'web_excerpt' and args.complete:
        parser.error('Extrato web não pode ser declarado fonte completa')
    run = stage(args.input, args.output, args.source_url, args.first, args.last,
                kind=args.kind, complete=args.complete, edition=args.edition)
    print(json.dumps({'documents': len(run['documents']), 'missing': run['missing_in_supplied_range']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
