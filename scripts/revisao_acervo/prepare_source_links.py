#!/usr/bin/env python3
"""Prepara links com cotejo integral e posicional, sem modificar o acervo.

Destinos provêm exclusivamente do HTML preservado; não há coleta de rede,
inferência de identidade documental ou criação de notas editoriais no texto.
"""
import argparse
import csv
import difflib
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'temporario/revisao-onda3'
OUT = WORK / 'links'
PUNCT = r'''!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~'''


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def canonical_map(text):
    # Ignore only introduced structural prefixes; escaped literal punctuation
    # never qualifies as a prefix. Keep the original span of every codepoint.
    skipped = set()
    for match in re.finditer(r'(?m)^(?:#{1,6}[ \t]+|(?:\d+[.)]|[-+*])[ \t]+)(?=\S)', text):
        skipped.update(range(match.start(), match.end()))
    chars, spans = [], []
    i = 0
    while i < len(text):
        if i in skipped:
            i += 1
            continue
        start = i
        if text[i] == '\\' and i + 1 < len(text) and text[i + 1] in PUNCT:
            i += 1
        if not text[i].isspace():
            chars.append(text[i])
            spans.append((start, i + 1))
        i += 1
    return ''.join(chars), spans


class Source(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.length = 0
        self.anchors = []
        self.active = None
        self.targets = {}
        self.nested = False
        self.feed(html)
        self.close()
        if self.active is not None:
            raise ValueError('Âncora sem fechamento')
        self.text = ''.join(self.parts)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # A single element carrying id=name is one target, not two.
        for target in set(filter(None, (attrs.get('id'), attrs.get('name') if tag == 'a' else None))):
            self.targets[target] = self.targets.get(target, 0) + 1
        if tag == 'a':
            if self.active is not None:
                self.nested = True
                return
            self.active = {'href': attrs.get('href'), 'start': self.length,
                           'id': attrs.get('id'), 'name': attrs.get('name')}

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, text):
        normalized = ''.join(c for c in text if not c.isspace())
        self.parts.append(normalized)
        self.length += len(normalized)

    def handle_endtag(self, tag):
        if tag == 'a' and self.active is not None:
            self.active['end'] = self.length
            self.anchors.append(self.active)
            self.active = None


def resolve_url(href, page, targets):
    if not href or not href.strip():
        return None, 'Destino vazio'
    href = href.strip()
    if any(ord(c) < 32 for c in href):
        return None, 'Controle no destino'
    url = urljoin(page, href)
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https', 'mailto'):
        return None, 'Esquema não admitido'
    if parsed.scheme in ('http', 'https') and not parsed.netloc:
        return None, 'Destino HTTP sem host'
    # Only verify fragments when the source explicitly points to this page.
    base = urlsplit(page)
    same_page = (parsed.netloc.lower(), parsed.path.rstrip('/'), parsed.query) == (base.netloc.lower(), base.path.rstrip('/'), base.query)
    if parsed.fragment and (href.startswith('#') or same_page):
        count = targets.get(unquote(parsed.fragment), 0)
        if count != 1:
            return None, 'Fragmento da fonte com destino ' + ('ausente' if count == 0 else 'duplicado')
    # Percent-encoding preserves the URL semantics and keeps angle syntax valid.
    return quote(url, safe=":/?#[]@!$&'()*+,;=%~-._"), None


def prepare_document(doc, batch, issue, proposal, editions, posts):
    uid = doc['id']
    edition = editions[uid + ':ru']
    raw = (ROOT / edition['file']).read_bytes()
    if sha(raw) != edition['sha256']:
        raise ValueError('Catálogo não corresponde ao arquivo: ' + uid)
    source_file = proposal['source_json']
    if source_file not in posts:
        posts[source_file] = {p['id']: p for p in json.loads((ROOT / source_file).read_text())}
    post = posts[source_file][int(uid.split('-')[1])]
    html = post['content']['rendered']
    if sha(html.encode()) != proposal['source_html_sha256']:
        raise ValueError('HTML mudou: ' + uid)
    source = Source(html)
    text = raw.decode()
    normalized, spans = canonical_map(text)
    audit = {'document_id': uid, 'source_json': source_file,
             'preparer_sha256': sha(Path(__file__).read_bytes()),
             'source_html_sha256': sha(html.encode()), 'source_url': post['link'],
             'canonical_file': edition['file'], 'before_sha256': sha(raw),
             'method': 'Texto HTML integral em ordem, ignorando somente whitespace e escapes/prefixos Markdown; cada link localizado por intervalo da própria âncora nesse texto. Nenhuma busca apenas pelo rótulo.',
             'network_checked': False, 'links': [], 'retained': []}
    if source.nested:
        raise ValueError('Âncoras aninhadas')
    # Existing Markdown destinations make this normalization incomplete; never
    # append a second link or replace a previously reviewed destination blindly.
    if re.search(r'(?<!\\)\]\(', text):
        return None, {'id': uid, 'reason': 'Já contém links Markdown; exige cotejo incremental específico'}
    at = normalized.find(source.text) if source.text else -1
    if at < 0 or normalized.find(source.text, at + 1) >= 0:
        return None, {'id': uid, 'reason': 'Texto integral HTML não corresponde de forma única à normalização canônica',
                      'source_normalized_length': len(source.text), 'canonical_normalized_length': len(normalized)}
    audit['source_interval_in_canonical_normalized'] = [at, at + len(source.text)]
    changes = []
    for anchor in source.anchors:
        if anchor['href'] is None:
            continue
        item = dict(anchor)
        destination, reason = resolve_url(anchor['href'], post['link'], source.targets)
        if anchor['end'] <= anchor['start']:
            reason = 'Âncora sem rótulo textual (imagem ou elemento vazio)'
        if not reason:
            begin = spans[at + anchor['start']][0]
            end = spans[at + anchor['end'] - 1][1]
            label = text[begin:end]
            if re.search(r'\n\s*\n', label):
                reason = 'Rótulo atravessa fronteira de bloco'
            elif '\n' in label or '\r' in label:
                # Preserve source bytes rather than introducing multiline link
                # semantics or moving its paragraph boundary.
                reason = 'Rótulo em mais de uma linha'
            elif any(begin < old_end and end > old_begin for old_begin, old_end, _ in changes):
                reason = 'Intervalos de âncoras sobrepostos'
            else:
                rendered = '[' + label + '](<' + destination + '>)'
                changes.append((begin, end, rendered))
                item.update(canonical_start=begin, canonical_end=end, label_markdown=label,
                            resolved_href=destination, prefix_context=text[max(0, begin-90):begin],
                            suffix_context=text[end:end+90])
        if reason:
            item['reason'] = reason
            audit['retained'].append(item)
        else:
            audit['links'].append(item)
    if not changes:
        return None, {'id': uid, 'reason': 'Nenhum link textual recuperável com esta passagem', 'retained': audit['retained']}
    candidate = text
    for begin, end, rendered in sorted(changes, reverse=True):
        candidate = candidate[:begin] + rendered + candidate[end:]
    # Strong byte preservation proof: remove only the exact inserted wrappers
    # at their new offsets and recover the original file, including whitespace.
    reconstructed, cursor, delta = [], 0, 0
    for begin, end, rendered in sorted(changes):
        new_begin = begin + delta
        if candidate[new_begin:new_begin+len(rendered)] != rendered:
            raise ValueError('Deslocamento do candidato divergiu: ' + uid)
        reconstructed.append(candidate[cursor:new_begin])
        reconstructed.append(text[begin:end])
        cursor = new_begin + len(rendered)
        delta += len(rendered) - (end - begin)
    reconstructed.append(candidate[cursor:])
    if ''.join(reconstructed).encode() != raw:
        raise ValueError('Conteúdo mudou além dos wrappers: ' + uid)
    folder = OUT / batch['id']
    folder.mkdir(parents=True, exist_ok=True)
    target, evidence = folder / (uid + '.ru.md'), folder / (uid + '.evidence.json')
    target.write_text(candidate)
    audit.update(candidate_sha256=sha(target.read_bytes()), exact_unwrap_recovers_original=True,
                 new_links=len(changes), source_href_count=sum(a['href'] is not None for a in source.anchors),
                 translations='Preservadas; cotejo de links restrito à edição russa apontada pela fila.',
                 fragments='Destinos absolutos da publicação original, não chamadas de notas locais; nenhuma nota foi movida/renumerada.')
    dump(evidence, audit)
    (folder / (uid + '.diff')).write_text(''.join(difflib.unified_diff(text.splitlines(True), candidate.splitlines(True), fromfile=edition['file'], tofile=str(target.relative_to(ROOT)))))
    outcome = 'parcial' if audit['retained'] else 'corrigido_com_evidencia'
    result = {'edition': {'document_id': uid, 'language': 'ru', 'file': edition['file'],
                          'before_sha256': sha(raw), 'candidate': str(target.relative_to(ROOT)),
                          'candidate_sha256': sha(target.read_bytes()), 'source_evidence': str(evidence.relative_to(ROOT))},
              'issue': {'key': issue['chave'], 'outcome': outcome, 'evidence': str(evidence.relative_to(ROOT)),
                        'next_action': ('Conferir âncoras retidas individualmente: ' + '; '.join(sorted({a['reason'] for a in audit['retained']}))) if audit['retained'] else 'Links textuais reconstruídos conforme HTML preservado. Destinos da publicação original; disponibilidade atual da rede e notas locais não foram validadas.'},
              'summary': {'id': uid, 'links': len(changes), 'retained': len(audit['retained']), 'outcome': outcome}}
    return result, None


def main():
    global WORK, OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-root', type=Path, default=WORK)
    parser.add_argument('--only', nargs='+', help='IDs de documentos para uma passagem delimitada')
    args = parser.parse_args()
    WORK = args.work_root.resolve()
    if not WORK.is_relative_to(ROOT):
        parser.error('Área de trabalho fora do projeto')
    OUT = WORK / 'links'
    if (OUT / 'SUMMARY.json').exists():
        parser.error('Preparação já existe; preservar evidências e usar nova área de trabalho/base')
    manifest = json.loads((WORK / 'baseline/manifest.json').read_text())
    rows = {r['chave']: r for r in csv.DictReader((WORK / 'baseline/queue.csv').open())}
    proposals = {p['chave']: p['evidencia'] for p in json.loads((ROOT / 'docs/revisao-markdown/diagnostico-geral/proposals-showtrials.json').read_text())['proposals']}
    editions = {e['id']: e for e in json.loads((ROOT / 'data/catalog/editions.json').read_text())}
    posts, results, prepared, retained = {}, {}, [], []
    OUT.mkdir(parents=True, exist_ok=True)
    for batch in manifest['batches']:
        for doc in batch['documents']:
            if args.only and doc['id'] not in args.only:
                continue
            key = doc['id'] + ':links_nao_reconstruidos'
            if key not in doc['issue_keys'] or key not in proposals:
                continue
            try:
                result, hold = prepare_document(doc, batch, rows[key], proposals[key], editions, posts)
            except (ValueError, IndexError, KeyError) as error:
                result, hold = None, {'id': doc['id'], 'reason': str(error)}
            if hold:
                retained.append(hold)
                continue
            owner = results.setdefault(batch['id'], {'batch_id': batch['id'], 'editions': [], 'issues': []})
            owner['editions'].append(result['edition'])
            owner['issues'].append(result['issue'])
            prepared.append(result['summary'])
    files = []
    for bid, result in results.items():
        path = OUT / bid / 'result.json'
        dump(path, result)
        files.append(str(path.relative_to(ROOT)))
    dump(OUT / 'SUMMARY.json', {'prepared': prepared, 'retained_documents': retained, 'result_files': files,
                              'scope': 'Candidatos apenas; acervo, fila e catálogo inalterados; sem testes ou rede'})
    print(json.dumps({'documents': len(prepared), 'links': sum(d['links'] for d in prepared),
                      'closed_candidates': sum(d['outcome'] != 'parcial' for d in prepared),
                      'partial_candidates': sum(d['outcome'] == 'parcial' for d in prepared),
                      'retained_documents': len(retained), 'batches': len(results)}), flush=True)


if __name__ == '__main__':
    main()
