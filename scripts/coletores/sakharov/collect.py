#!/usr/bin/env python3
"""Piloto e coleta incremental Sakharov; nunca escreve no catálogo público."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from extraction import (RUSSIAN_URL, ENGLISH_INDEX, UA, make_session, soup_from,
                        find_ru_toc, find_english_urls, clean_article, choose_article, normalized)


# The index's item 16 href is literal prose and returns404. This canonical post
# was independently located by its exact title on the same source site.
EN_LINK_CORRECTIONS = {
    normalized('Strengthening the Dictatory of the Proletariat Is the Main Condition for the Victory of the Revolution'):
        'https://neodemocracy.blogspot.com/2022/12/strengthening-dictatory-of-proletariat.html'
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    os.replace(tmp, path)


class Collector:
    def __init__(self, root, refresh=False, delay=2):
        self.root, self.refresh, self.delay = root, refresh, max(1, delay)
        self.session, self.robots, self.last = make_session(), {}, {}
        self.path = root / 'inventory.json'
        self.inventory = json.loads(self.path.read_text()) if self.path.exists() else {
            'schema': 1, 'work': 'Sakharov 2003', 'items': {}, 'attempts': []}
        self.attempt_start = len(self.inventory['attempts'])

    def pause(self, host):
        wait = self.delay - (time.monotonic() - self.last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        self.last[host] = time.monotonic()

    def fetch(self, url):
        previous = self.inventory['items'].get(url, {})
        if previous.get('raw') and not self.refresh:
            return (self.root / previous['raw']).read_bytes(), previous
        host = urlparse(url).netloc
        if host not in self.robots:
            robots_url = f'{urlparse(url).scheme}://{host}/robots.txt'
            self.pause(host)
            res = self.session.get(robots_url, timeout=(10, 30))
            rp = RobotFileParser(robots_url)
            if res.status_code in (404, 410):
                rp.parse([])
            else:
                res.raise_for_status()
                rp.parse(res.text.splitlines())
            self.robots[host] = rp
        if not self.robots[host].can_fetch(UA, url):
            raise PermissionError('robots.txt não permite a coleta: ' + url)
        self.pause(host)
        res = self.session.get(url, timeout=(10, 45), stream=True)
        res.raise_for_status()
        if urlparse(res.url).netloc != host:
            raise ValueError('Redirecionamento para outro domínio requer revisão: ' + res.url)
        if 'html' not in res.headers.get('Content-Type', '').lower():
            raise ValueError('Resposta não é HTML')
        chunks, size = [], 0
        for chunk in res.iter_content(65536):
            size += len(chunk)
            if size > 12_000_000:
                raise ValueError('HTML excede 12 MB; coleta interrompida, sem truncamento')
            chunks.append(chunk)
        raw = b''.join(chunks)
        sha = digest(raw)
        relative = Path('raw') / digest(url.encode())[:16] / (sha + '.html')
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(raw)
        meta = {'source_url': url, 'final_url': res.url, 'raw': str(relative),
                'raw_sha256': sha, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'content_type': res.headers.get('Content-Type'), 'bytes': len(raw)}
        return raw, meta

    def collect(self, url, language, navigation_index=None, title=None, index_only=False):
        now = datetime.now(timezone.utc).isoformat()
        try:
            raw, meta = self.fetch(url)
            if index_only:
                meta.update(language=language, status='index_preserved')
            else:
                soup = soup_from(raw)
                if language == 'ru' and not title:
                    title = find_ru_toc(soup).get(navigation_index)
                md = clean_article(soup, url)
                article = choose_article(soup)
                diagnostics = {'html_tables': len(article.select('table')),
                    'html_images': len(article.select('img')),
                    'html_heading_count': len(article.select('h1,h2,h3,h4,h5,h6')),
                    'numbered_note_labels': sorted(set(re.findall(r'\[(\d+)\]', md)), key=int),
                    'labels_without_line_definition': sorted(set(re.findall(r'\[(\d+)\]', md))
                        - set(re.findall(r'^\s*\[(\d+)\]', md, flags=re.M)), key=int)}
                # Hash-addressed derivatives preserve prior candidates and editorial copies.
                body_sha = digest(md.encode())
                rel = Path('candidates') / language / (digest(url.encode())[:16] + '-' + body_sha + '.md')
                dest = self.root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    dest.write_text(md, encoding='utf-8')
                meta.update(language=language, title=title or 'Título a conferir',
                    navigation_index=navigation_index, diagnostics=diagnostics, candidate=str(rel), markdown_sha256=body_sha,
                    candidate_file_sha256=digest(dest.read_bytes()),
                    candidate_locally_modified=digest(dest.read_bytes()) != body_sha,
                    characters=len(md), status='candidate_unreviewed', source_kind='later_historiography',
                    notes=['Página HTML não equivale automaticamente a capítulo ou documento.',
                           'Fronteiras, notas e correspondência entre idiomas requerem revisão.'])
            # Keep previous successful versions, even when source URL is refreshed.
            old = self.inventory['items'].get(url, {})
            versions = old.get('versions', [])
            if old.get('raw_sha256') and (old['raw_sha256'] != meta.get('raw_sha256')
                    or old.get('markdown_sha256') != meta.get('markdown_sha256')):
                versions.append({k: v for k, v in old.items() if k != 'versions'})
            meta['versions'] = versions
            self.inventory['items'][url] = meta
            self.inventory['attempts'].append({'at': now, 'url': url, 'status': meta['status']})
            print(meta['status'], language, navigation_index, url, flush=True)
            return raw
        except Exception as exc:
            self.inventory['attempts'].append({'at': now, 'url': url, 'status': 'error', 'error': str(exc)})
            print('ERROR', url, str(exc), flush=True)
            return None
        finally:
            atomic_json(self.path, self.inventory)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=Path('temporario/coletas-quatro/sakharov'))
    ap.add_argument('--ru-pages', default='0,29,59', help='Índices de navegação, base zero; não capítulos')
    ap.add_argument('--all-russian', action='store_true', help='Todas as 60 posições russas; prevalece sobre --ru-pages')
    ap.add_argument('--english', type=int, default=1, help='Número de extratos ingleses; zero desativa')
    ap.add_argument('--refresh', action='store_true', help='Nova fonte/versionamento; preserva anteriores')
    args = ap.parse_args()
    pages = list(range(60)) if args.all_russian else [int(x) for x in args.ru_pages.split(',') if x.strip()]
    if any(n < 0 or n > 59 for n in pages) or args.english < 0:
        ap.error('Páginas russas entre 0 e 59; quantidade inglesa não negativa')
    c = Collector(args.output, args.refresh)
    for n in pages:
        c.collect(RUSSIAN_URL + '?start=' + str(n), 'ru', n)
    if args.english:
        raw = c.collect(ENGLISH_INDEX, 'en', index_only=True)
        if raw:
            links = find_english_urls(soup_from(raw))
            discovered = [{'title': t, 'url': EN_LINK_CORRECTIONS.get(normalized(t), u),
                           'index_link_literal':u, 'link_corrected_explicitly':normalized(t) in EN_LINK_CORRECTIONS} for t,u in links]
            atomic_json(args.output / 'english-discovery.json', discovered)
            for n, item in enumerate(discovered[:args.english], 1):
                title,url=item['title'],item['url']
                c.collect(url, 'en', n, title)
                if url in c.inventory['items']:
                    c.inventory['items'][url]['index_link_literal']=item['index_link_literal']
                    c.inventory['items'][url]['link_corrected_explicitly']=item['link_corrected_explicitly']
                    atomic_json(c.path,c.inventory)
    return 1 if any(x['status'] == 'error' for x in c.inventory['attempts'][c.attempt_start:]) else 0


if __name__ == '__main__':
    raise SystemExit(main())
