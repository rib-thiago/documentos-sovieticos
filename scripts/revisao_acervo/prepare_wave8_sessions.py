#!/usr/bin/env python3
"""Títulos de sessões, extratos e anexos: seleção explícita e prefixos reversíveis."""
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/revisao_acervo'))
from prepare_source_links import Source, sha

WORK = ROOT / 'temporario/revisao-onda8'
OUT = WORK / 'secoes'
# Index within the frozen inventory's candidate list; level is navigational.
# No date/addressee is promoted and no missing section number is invented.
SELECTIONS = {1847: [(0, 2)], 2443: [(0, 2)], 2444: [(0, 2)], 2478: [(0, 2)], 2480: [(0, 2)], 2519: [(0, 2)], 2521: [(1, 2)], 2522: [(1, 2)], 2523: [(1, 2)], 2525: [(1, 2)], 2526: [(1, 2)], 2527: [(1, 2)], 2536: [(1, 2)], 2539: [(0, 2)], 2618: [(0, 2)], 11413: [(0, 2)], 2479: [(0, 2)], 2481: [(0, 2)], 2482: [(0, 2)], 2508: [(1, 2)], 2540: [(0, 2)], 4288: [(0, 2)], 4423: [(1, 2)], 4435: [(0, 2)], 4580: [(0, 2)], 4581: [(0, 2)], 4584: [(0, 2)], 4665: [(0, 2)], 6312: [(3, 2)], 6354: [(3, 2)], 6360: [(3, 2)], 8609: [(0, 2)], 8611: [(0, 2)], 8617: [(0, 2)], 8621: [(0, 2)], 9431: [(0, 2)], 10470: [(1, 2)], 8173: [(5, 2), (8, 2)], 810: [(0, 2), (3, 2), (4, 2), (8, 2), (10, 2)], 7275: [(4, 2), (5, 3), (6, 3), (7, 3)], 5779: [(3, 2), (4, 2)], 5766: [(8, 2), (11, 3)], 8938: [(0, 2), (1, 3), (2, 3), (3, 3)], 8946: [(0, 2), (1, 3), (2, 3), (3, 3)], 8951: [(0, 2), (1, 3), (2, 3), (3, 3)], 8954: [(0, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3)], 8956: [(0, 2), (1, 3), (2, 3), (3, 3)]}
NOTES = {}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    invpath = ROOT / 'temporario/revisao-onda4/secoes/inventory.json'
    inventory = {}
    for item in json.loads(invpath.read_text()):
        inventory.setdefault(item['id'], item)
    manifest = json.loads((WORK / 'baseline/manifest.json').read_text())
    owned = {d['id']: (b, d) for b in manifest['batches'] for d in b['documents']}
    editions = {e['id']: e for e in json.loads((ROOT / 'data/catalog/editions.json').read_text())}
    spec = importlib.util.spec_from_file_location('table_projection', ROOT / 'temporario/revisao-onda4/tabelas/prepare.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    open_keys = {r["chave"] for r in __import__("csv").DictReader((WORK / "baseline/queue.csv").open()) if r["status"] != "corrigido"}
    results, summary, held, cache = {}, [], [], {}
    for number in list(SELECTIONS):
        uid = f'showtrials-{number}'
        entry = inventory[uid]
        batch, task = owned[uid]
        edition = editions[uid + ':ru']
        raw = (ROOT / edition['file']).read_bytes()
        if sha(raw) != edition['sha256']:
            raise ValueError('Arquivo não coincide com catálogo')
        prior = next(e for e in task['editions'] if e['language'] == 'ru')
        if sha(raw) != prior['sha256']:
            raise ValueError('Edição mudou após o despacho')
        source = entry['source']
        file = source['source_json']
        if file not in cache:
            cache[file] = {p['id']: p for p in json.loads((ROOT / file).read_text())}
        html = cache[file][number]['content']['rendered']
        if sha(html.encode()) != source['source_html_sha256']:
            raise ValueError('HTML divergiu')
        text = raw.decode()
        normalized, _, _ = module.projection(text)
        source_text = Source(html).text
        at = normalized.find(source_text)
        if at < 0 or normalized.find(source_text, at + 1) >= 0:
            held.append({'id': uid, 'reason': 'Projeção integral sem correspondência única'})
            continue
        # A one-character paragraph such as "I" must not consume the next
        # paragraph. Preserve the blank-line boundary in the matcher itself.
        blocks = list(re.finditer(r'\S(?:[^\r\n]|\r?\n(?![ \t]*\r?\n))*', text))
        operations = []
        existing_headings = []
        reason = ''
        for index, level in SELECTIONS.get(number, []):
            heading = entry['candidates'][index]
            needle = Source(heading['html']).text
            if needle not in source_text or needle != ''.join(c for c in heading['text'] if not c.isspace()):
                raise ValueError('Título divergente no inventário')
            matches = [b for b in blocks if module.projection(b[0])[0] == needle]
            if len(matches) != 1 or '\n' in matches[0][0]:
                reason = 'Título repartido/repetido: ' + heading['text']
                break
            match = matches[0]
            if match[0].startswith('#'):
                existing_headings.append({'literal_markdown': match[0], 'source_text': heading['text']})
                continue
            operations.append({'start': match.start(), 'end': match.end(), 'level': level,
                               'literal_markdown': match[0], 'source_html': heading['html'],
                               'source_text': heading['text'], 'centered': heading.get('center'), 'bold': heading.get('bold')})
        if reason:
            held.append({'id': uid, 'reason': reason})
            continue
        candidate = text
        for op in sorted(operations, key=lambda o: o['start'], reverse=True):
            pos = op['start']
            candidate = candidate[:pos] + '#' * op['level'] + ' ' + candidate[pos:]
        # Invert precisely our insertions, never remove pre-existing markup.
        back = candidate
        delta, inserted = 0, []
        for op in sorted(operations, key=lambda o: o['start']):
            size = op['level'] + 1
            inserted.append((op['start'] + delta, size))
            delta += size
        for start, size in reversed(inserted):
            back = back[:start] + back[start + size:]
        if back.encode() != raw:
            raise ValueError('Conteúdo mudou além dos prefixos')
        if number in NOTES:
            candidate += '\n\n---\n\n> **Редакционное примечание — Documentos Soviéticos**\n>\n> ' + NOTES[number] + '\n'
        if number in (7248, 7250):
            decision = ('Carta contínua: data, saudação, parágrafos corridos, assinatura e cota. Não inventar subdivisões. '
                        + ('O marcador 1. aparece após a nota final; não é título de seção do corpo e permanece literal.' if number == 7248 else 'A anotação final permanece no contexto da carta.'))
            outcome = 'fonte_continua_legitima'
        elif number in (5793, 6958):
            headings = re.findall(r'^#{1,6} (.+)$', text, re.M)
            if headings != ['ПРОТОКОЛ ДОПРОСА', 'ПРОТОКОЛ ДОПРОСА']:
                raise ValueError('Estrutura atual inesperada')
            decision = 'Dois protocolos já possuem dois títulos recuperados na onda2, em contextos distintos. Alerta de navegabilidade anterior obsoleto; sem revisão semântica integral.'
            outcome = 'alerta_obsoleto_ou_falso_positivo'
        else:
            decision = 'Títulos explícitos cotejados; somente prefixos Markdown inseridos. Numeração, variantes, palavras e ordem preservadas. Ressalvas editoriais separadas quando necessárias.'
            outcome = 'corrigido_com_evidencia'
        if not operations and existing_headings:
            outcome = 'alerta_obsoleto_ou_falso_positivo'
            decision = 'As rubricas selecionadas já possuem títulos Markdown correspondentes ao HTML preservado. Cotejo integral ordenado confirmou a preservação; não inventar subdivisões temáticas. Encerrado somente o alerta de seções, não revisão semântica ou das traduções.'
        elif operations:
            decision = 'Rubricas explícitas recuperadas por prefixo Markdown reversível, preservando a grafia literal, identificação, data e todos os parágrafos. Não criar títulos temáticos, nem emendar as rubricas da fonte.'
        folder = OUT / batch['id']
        folder.mkdir(exist_ok=True)
        ep = folder / (uid + '.evidence.json')
        evidence = {'document_id': uid, 'source_json': file, 'source_html_sha256': sha(html.encode()),
                    'before_sha256': sha(raw), 'source_interval': [at, at + len(source_text)],
                    'full_source_text_in_order': True, 'inventory_sha256': sha(invpath.read_bytes()),
                    'heading_insertions': operations, 'existing_headings_preserved': existing_headings,
                    'exact_prefix_inversion': True, 'decision': decision,
                    'editorial_note': NOTES.get(number), 'scope': 'Estrutura e navegação, não validação histórica ou revisão integral da tradução.'}
        dump(ep, evidence)
        result = results.setdefault(batch['id'], {'batch_id': batch['id'], 'editions': [], 'issues': []})
        if candidate != text:
            cp = folder / (uid + '.ru.md')
            cp.write_text(candidate)
            result['editions'].append({'document_id': uid, 'language': 'ru', 'file': edition['file'],
                                       'before_sha256': sha(raw), 'candidate': str(cp.relative_to(ROOT)),
                                       'candidate_sha256': sha(cp.read_bytes()), 'source_evidence': str(ep.relative_to(ROOT))})
        keys = [key for key in task['issue_keys'] if key in open_keys and key.endswith((':texto_longo_sem_secoes_suficientes', ':decisao_editorial_pendente'))]
        for key in keys:
            result['issues'].append({'key': key, 'outcome': outcome, 'evidence': str(ep.relative_to(ROOT)), 'next_action': decision})
        summary.append({'id': uid, 'headings': len(operations), 'issues': len(keys), 'outcome': outcome})
    files = []
    for bid, value in results.items():
        path = OUT / (bid + '.result.json')
        dump(path, value)
        files.append(str(path.relative_to(ROOT)))
    dump(OUT / 'SUMMARY.json', {'prepared': summary, 'held': held, 'result_files': files})
    print(json.dumps({'prepared': summary, 'held': held}, ensure_ascii=False))


if __name__ == '__main__':
    main()
