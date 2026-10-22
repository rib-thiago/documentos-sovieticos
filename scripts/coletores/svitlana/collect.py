#!/usr/bin/env python3
"""Coleta de candidatos Svitlana/Erdogan, sem escrita no catálogo público.

Biblioteca padrão; snapshots e candidatos são imutáveis por SHA-256.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
DEFAULT_OUT = ROOT / 'temporario/coletas-quatro/svitlana'
UA = 'DocumentosSovieticosResearchCollector/0.1'
MAX_BYTES = 25_000_000
VOID = {'br', 'hr', 'img', 'input', 'meta', 'link', 'wbr', 'source', 'area', 'base', 'embed', 'param', 'col'}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(blob):
    return hashlib.sha256(blob if isinstance(blob, bytes) else blob.encode()).hexdigest()


def normalize(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path, p.query, ''))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def immutable(path, blob):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != blob:
            raise ValueError(f'Não sobrescrever versão existente: {path}')
    else:
        with path.open('xb') as f:
            f.write(blob)


class Node:
    def __init__(self, tag='', attrs=None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.children = []

    def text(self):
        return ''.join(c.text() if isinstance(c, Node) else c for c in self.children)

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()


class Tree(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node('document')
        self.stack = [self.root]
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        # Legacy FrontPage HTML omits p/li closures; do not nest paragraphs.
        if tag in {'p', 'li', 'tr', 'td', 'th'} and self.stack[-1].tag == tag:
            self.stack.pop()
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def decode(blob, content_type):
    head = blob[:5000].decode('ascii', errors='ignore')
    found = re.search(r'charset\s*=\s*["\x27]?([\w-]+)', content_type + head, re.I)
    for enc in ([found.group(1)] if found else []) + ['utf-8', 'windows-1251', 'windows-1252']:
        try:
            return blob.decode(enc)
        except (UnicodeDecodeError, LookupError):
            pass
    raise ValueError('Codificação não reconhecida; revisão manual necessária')


def body_root(tree):
    # The source's main Word-exported container excludes its outer quotation
    # layout and repeated series masthead. These remain in the raw snapshot.
    word = [n for n in tree.root.walk() if n.tag == 'div' and 'WordSection' in n.attrs.get('class', '')]
    if word:
        selected = max(word, key=lambda n: len(n.text()))
        bodies = [n for n in tree.root.walk() if n.tag == 'body']
        if bodies:
            body = max(bodies, key=lambda n: len(n.text()))
            # Some exports close WordSection before the document or contain
            # several sibling sections. Never discard that text as masthead.
            visible = lambda node: len(re.sub(r'\s+', '', markdown(node, '')))
            if visible(selected) < .85 * visible(body):
                return body
        return selected
    for tag in ('article', 'main', 'body'):
        matches = [n for n in tree.root.walk() if n.tag == tag]
        if matches:
            return max(matches, key=lambda n: len(n.text()))
    raise ValueError('Resposta sem article/main/body HTML')


def markdown(node, base):
    if not isinstance(node, Node):
        return re.sub(r'\s+', ' ', node.replace('\u00a0', ' '))
    tag = node.tag
    if tag == 'div' and 'border-top:' in node.attrs.get('style', '') and 'Non-profit digital library' in node.text():
        return ''
    if tag in {'script', 'style', 'nav', 'footer', 'noscript', 'head', 'form'}:
        return ''
    content = ''.join(markdown(c, base) for c in node.children)
    if tag == 'br':
        return '\n'
    if tag == 'hr':
        return '\n\n---\n\n'
    anchor = node.attrs.get('id') or (node.attrs.get('name') if tag == 'a' else None)
    prefix = f'<a id="{html.escape(anchor, quote=True)}"></a>' if anchor else ''
    if tag == 'a' and node.attrs.get('href'):
        href = node.attrs['href']
        target = href if href.startswith('#') else urljoin(base, href)
        return prefix + f'[{content.strip() or target}](<{target}>)'
    if tag == 'img':
        return f'![{node.attrs.get("alt", "")}]({urljoin(base, node.attrs.get("src", ""))})'
    if re.fullmatch('h[1-6]', tag):
        return '\n\n' + prefix + '#' * int(tag[1]) + ' ' + content.strip() + '\n\n'
    if tag in {'b', 'strong'}:
        return f'**{content.strip()}**' if content.strip() else ''
    if tag in {'i', 'em'}:
        return f'*{content.strip()}*' if content.strip() else ''
    if tag in {'sup', 'sub'}:
        return f'<{tag}>{content}</{tag}>'
    if tag == 'blockquote':
        return '\n\n' + '\n'.join('> ' + l for l in content.strip().splitlines()) + '\n\n'
    if tag == 'li':
        return '\n- ' + content.strip() + '\n'
    if tag == 'table':
        rows = [n for n in node.walk() if n.tag == 'tr']
        cells = [[c for c in r.children if isinstance(c, Node) and c.tag in {'td', 'th'}] for r in rows]
        cells = [r for r in cells if r]
        # Actual two-dimensional simple tables only. FrontPage frequently wraps
        # the entire text in a one-cell layout table; do not turn it into a row.
        if cells and len(cells) > 1 and max(map(len, cells)) > 1 and not any(
            'rowspan' in c.attrs or 'colspan' in c.attrs for row in cells for c in row
        ):
            width = max(map(len, cells))
            values = [[markdown(c, base).strip().replace('|', '\\|').replace('\n', '<br>') for c in r] for r in cells]
            values = [r + [''] * (width - len(r)) for r in values]
            lines = ['| ' + ' | '.join(r) + ' |' for r in values]
            lines.insert(1, '| ' + ' | '.join(['---'] * width) + ' |')
            return '\n\n' + '\n'.join(lines) + '\n\n'
    if tag in {'p', 'div', 'section', 'article', 'main', 'tr', 'table', 'ul', 'ol', 'pre'}:
        return '\n\n' + prefix + content.strip() + '\n\n' if content.strip() or prefix else ''
    if tag in {'td', 'th'}:
        return content + '\n\n'
    return prefix + content


def convert(blob, mime, url):
    tree = Tree(decode(blob, mime))
    root = body_root(tree)
    text = markdown(root, url)
    text = re.sub(r'\n[ \t]+', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip() + '\n'
    titles = [n.text().strip() for n in tree.root.walk() if n.tag == 'title']
    links = [(urljoin(url, n.attrs['href']), ' '.join(n.text().split())) for n in root.walk()
             if n.tag == 'a' and n.attrs.get('href') and not n.attrs['href'].startswith(('#', 'mailto:', 'javascript:'))]
    warnings = ['generic_body_extraction_requires_boundary_review'] if root.tag == 'body' else []
    if 'WordSection' in root.attrs.get('class', ''):
        warnings.append('source_word_container_selected_series_masthead_preserved_in_raw')
    if any(n.tag in {'td', 'th'} and ('rowspan' in n.attrs or 'colspan' in n.attrs) for n in root.walk()):
        warnings.append('complex_table_requires_review_source_html')
    if len(text) < 300:
        warnings.append('short_body_requires_review')
    if '\ufffd' in text:
        warnings.append('replacement_characters')
    return text, links, titles[0] if titles else '', warnings


class Collector:
    def __init__(self, out, delay=2.0, timeout=35):
        self.out = out
        self.delay = max(2.0, delay)
        self.timeout = timeout
        self.last = {}
        self.robots = {}
        self.path = out / 'inventory.json'
        self.inventory = json.loads(self.path.read_text()) if self.path.exists() else {'schema_version': 1, 'sources': {}, 'candidates': {}}

    def checkpoint(self):
        self.inventory['updated_at'] = now()
        write_json(self.path, self.inventory)

    def request(self, url):
        host = urlsplit(url).netloc
        time.sleep(max(0, self.delay - (time.monotonic() - self.last.get(host, 0))))
        try:
            with urlopen(Request(url, headers={'User-Agent': UA}), timeout=self.timeout) as response:
                blob = response.read(MAX_BYTES + 1)
                if len(blob) > MAX_BYTES:
                    raise ValueError('Resposta excede 25 MB; não foi truncada nem aceita')
                return blob, response.url, response.headers.get('Content-Type', '')
        finally:
            self.last[host] = time.monotonic()

    def allowed(self, url):
        p = urlsplit(url)
        origin = f'{p.scheme}://{p.netloc}'
        if origin not in self.robots:
            rp = RobotFileParser()
            try:
                blob, _, _ = self.request(origin + '/robots.txt')
                rp.parse(blob.decode('utf-8', errors='replace').splitlines())
                self.robots[origin] = rp
            except Exception as exc:
                # Absence is allowed; transient failures are not silently bypassed.
                if getattr(exc, 'code', None) in (404, 410):
                    rp.parse([])
                    self.robots[origin] = rp
                else:
                    raise RuntimeError(f'Falha ao conferir robots.txt: {exc}') from exc
        if not self.robots[origin].can_fetch(UA, url):
            raise PermissionError(f'robots.txt não autoriza a coleta: {url}')

    def fetch(self, url):
        self.allowed(url)
        blob, final, mime = self.request(url)
        if urlsplit(final).netloc.lower() != urlsplit(url).netloc.lower():
            raise ValueError(f'Redirecionamento de host requer revisão: {final}')
        if not ('html' in mime.lower() or blob.lstrip().lower().startswith((b'<!doctype html', b'<html'))):
            raise ValueError(f'Resposta não HTML: {mime}')
        sha = digest(blob)
        path = self.out / 'raw' / (sha + '.html')
        immutable(path, blob)
        return blob, final, mime, sha, str(path.relative_to(self.out))

    def source(self, row, refresh=False):
        sid, url = row['id'], row['index_url']
        item = self.inventory['sources'].setdefault(sid, {'id': sid, 'url': url, 'attempts': []})
        attempt = {'at': now()}
        try:
            previous = item.get('latest_success')
            if previous and not refresh:
                raw = previous['raw']
                blob = (self.out / raw).read_bytes()
                final, mime, sha = previous['resolved_url'], previous.get('content_type', 'text/html'), digest(blob)
                attempt['operation'] = 'rediscover_cached_snapshot'
            else:
                blob, final, mime, sha, raw = self.fetch(url)
            text, links, title, warnings = convert(blob, mime, final)
            candidates = []
            for target, label in links:
                target = normalize(target)
                path = unquote(urlsplit(target).path).lower()
                if urlsplit(target).netloc != urlsplit(final).netloc or not path.endswith(('.htm', '.html')):
                    continue
                leaf = path.rsplit('/', 1)[-1]
                if target == normalize(final) or leaf in {'index.htm', 'index.html'}:
                    continue
                # Only links within the explicit source directory become candidates.
                if not path.startswith(unquote(urlsplit(final).path).rsplit('/', 1)[0].lower() + '/'):
                    continue
                cid = 'svitlana-' + digest(target)[:16]
                doc = self.inventory['candidates'].setdefault(cid, {'id': cid, 'url': target, 'occurrences': [], 'attempts': []})
                occurrence = {'source_id': sid, 'source_title': row['title'], 'label': label}
                if occurrence not in doc['occurrences']:
                    doc['occurrences'].append(occurrence)
                candidates.append(cid)
            references = [{'url': normalize(target), 'label': label} for target, label in links]
            attempt.update(status='ok', resolved_url=final, content_type=mime, sha256=sha, raw=raw, discovered_ids=sorted(set(candidates)), references=references, title=title, warnings=warnings)
            item['latest_success'] = attempt.copy()
        except Exception as exc:
            attempt.update(status='error', error=f'{type(exc).__name__}: {exc}')
        item['attempts'].append(attempt)
        self.checkpoint()
        return attempt

    def document(self, cid, reconvert=False):
        doc = self.inventory['candidates'][cid]
        attempt = {'at': now()}
        try:
            if reconvert:
                previous = doc.get('latest_success')
                if not previous:
                    raise ValueError('Sem fonte bruta coletada para reconversão')
                raw = previous['raw']
                blob = (self.out / raw).read_bytes()
                final, mime, sha = previous['resolved_url'], previous.get('content_type', 'text/html'), digest(blob)
                attempt['operation'] = 'reconvert_cached_snapshot'
                fetched_at = previous.get('fetched_at') or next((a['at'] for a in doc['attempts']
                    if a.get('status') == 'collected_unreviewed' and a.get('sha256') == sha
                    and a.get('operation') != 'reconvert_cached_snapshot'), previous['at'])
            else:
                blob, final, mime, sha, raw = self.fetch(doc['url'])
                fetched_at = attempt['at']
            text, links, title, warnings = convert(blob, mime, final)
            resources = [{'url': target, 'label': label} for target, label in links
                         if unquote(urlsplit(target).path).lower().endswith(('.pdf', '.djvu', '.djv'))]
            content_class = 'pdf_wrapper' if len(text) < 1000 and resources and 'support PDFs' in text else 'text_candidate'
            if content_class == 'pdf_wrapper':
                warnings.append('pdf_wrapper_not_document_text')
            md_sha = digest(text)
            md = self.out / 'candidates' / cid / (md_sha + '.en.md')
            immutable(md, text.encode())
            # Attribution is deliberately not guessed from collection editors.
            attempt.update(status='collected_unreviewed', resolved_url=final, content_type=mime, fetched_at=fetched_at, sha256=sha, raw=raw,
                markdown=str(md.relative_to(self.out)), markdown_sha256=md_sha, title_page=title,
                language='en', role='translation_candidate', original_language='ru',
                translator=None, document_author=None, translation_attribution_status='requires_source_review',
                linked_resources=resources, html_content_class=content_class,
                warnings=warnings, paragraphs=len([p for p in re.split(r'\n[> \t]*\n', text) if p.strip(' >\n')]),
                characters=len(text))
            doc['latest_success'] = attempt.copy()
        except Exception as exc:
            attempt.update(status='error', error=f'{type(exc).__name__}: {exc}')
        doc['attempts'].append(attempt)
        self.checkpoint()
        return attempt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=DEFAULT_OUT)
    ap.add_argument('--sources', default='VOL-01,TEMA-TO-STALIN')
    ap.add_argument('--indexes', action='store_true')
    ap.add_argument('--documents', action='store_true')
    ap.add_argument('--limit', type=int, default=3)
    ap.add_argument('--sample-documents', action='store_true', help='Coleta amostras inglesas explícitas do pacote, com sua associação de origem')
    ap.add_argument('--reconvert', action='store_true', help='Reconverter todas as fontes já coletadas, sem rede e sem sobrescrever Markdown anterior')
    ap.add_argument('--timeout', type=int, default=35)
    ap.add_argument('--refresh', action='store_true', help='Consultar novamente índices já preservados; por padrão usa cache')
    ap.add_argument('--balanced', action='store_true', help='Após Volume I, alternar séries prioritárias para amostragem distribuída')
    ap.add_argument('--unattempted', action='store_true', help='Tentar somente URLs ainda sem tentativas; permite lotes sem repetir falhas')
    args = ap.parse_args()
    rows = list(csv.DictReader((PACKAGE / 'fontes.csv').open(encoding='utf-8-sig', newline='')))
    wanted = {r['id'] for r in rows} if args.sources == 'all' else set(args.sources.split(','))
    if not wanted <= {r['id'] for r in rows}:
        ap.error('Identificador de fonte desconhecido')
    collector = Collector(args.out, timeout=args.timeout)
    if args.reconvert:
        for cid, doc in collector.inventory['candidates'].items():
            if doc.get('latest_success'):
                result = collector.document(cid, reconvert=True)
                print(cid, result['status'], result.get('error', result.get('characters')), flush=True)
    if args.indexes:
        for row in rows:
            if row['id'] in wanted:
                result = collector.source(row, refresh=args.refresh)
                print(row['id'], result['status'], result.get('error', len(result.get('discovered_ids', []))), flush=True)
    if args.documents:
        candidates = [(cid, d) for cid, d in collector.inventory['candidates'].items()
                      if not d.get('latest_success') and (not args.unattempted or not d.get('attempts'))
                      and any(o['source_id'] in wanted for o in d['occurrences'])]
        priority = ['VOL-01', 'TEMA-STALIN', 'TEMA-TO-STALIN', 'TEMA-OTHER']
        candidates.sort(key=lambda pair: min([priority.index(o['source_id']) if o['source_id'] in priority else len(priority) for o in pair[1]['occurrences']]))
        if args.balanced:
            groups = {sid: [] for sid in priority + ['other']}
            for pair in candidates:
                source = next((sid for sid in priority if any(o['source_id'] == sid for o in pair[1]['occurrences'])), 'other')
                groups[source].append(pair)
            candidates = groups.pop('VOL-01')
            while any(groups.values()):
                for group in groups.values():
                    if group:
                        candidates.append(group.pop(0))
        for cid, doc in candidates[:max(0, args.limit)]:
            result = collector.document(cid)
            print(cid, result['status'], result.get('error', result.get('characters')), flush=True)
    if args.sample_documents:
        samples = list(csv.DictReader((PACKAGE / 'amostra_documentos.csv').open(encoding='utf-8-sig', newline=''), delimiter=';'))
        for sample in [s for s in samples if s['idioma'] == 'en'][:max(0, args.limit)]:
            url = normalize(sample['url'])
            cid = 'svitlana-' + digest(url)[:16]
            doc = collector.inventory['candidates'].setdefault(cid, {'id': cid, 'url': url, 'occurrences': [], 'attempts': []})
            occurrence = {'source_id': sample['fonte'], 'source_title': 'Amostra explícita do pacote', 'label': sample['titulo']}
            if occurrence not in doc['occurrences']:
                doc['occurrences'].append(occurrence)
            result = collector.document(cid)
            print(cid, result['status'], result.get('error', result.get('characters')), flush=True)
    collector.checkpoint()


if __name__ == '__main__':
    main()
