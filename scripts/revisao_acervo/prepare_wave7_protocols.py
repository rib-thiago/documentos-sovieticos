#!/usr/bin/env python3
"""Rubricas de protocolos: seleção congelada, cotejo integral e prefixos reversíveis."""
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/revisao_acervo'))
from prepare_source_links import Source, sha

WORK = ROOT / 'temporario/revisao-onda7'
OUT = WORK / 'secoes'
# Index within the frozen inventory's candidate list; level is navigational.
# No date/addressee is promoted and no missing section number is invented.
SELECTIONS = {4944: [(0, 2)], 5149: [(3, 2)], 5206: [(3, 2)], 5358: [(0, 2)], 5366: [(3, 2)], 5387: [(3, 2)], 5511: [(0, 2)], 5514: [(3, 2)], 5550: [(3, 2)], 5554: [(0, 2)], 5567: [(0, 2)], 5590: [(3, 2)], 5595: [(3, 2)], 5617: [(3, 2)], 5618: [(0, 2)], 5623: [(3, 2)], 5625: [(3, 2)], 5629: [(3, 2)], 5636: [(3, 2)], 5638: [(0, 2)], 5641: [(3, 2)], 5649: [(0, 2)], 5654: [(3, 2)], 5656: [(3, 2)], 5657: [(3, 2)], 5659: [(0, 2)], 5663: [(0, 2)], 5668: [(0, 2)], 5669: [(3, 2)], 5684: [(3, 2)], 5707: [(3, 2)], 5711: [(0, 2)], 5721: [(3, 2)], 5725: [(0, 2)], 5729: [(3, 2)], 5732: [(3, 2)], 5736: [(3, 2)], 5742: [(3, 2)], 5800: [(3, 2)], 5801: [(0, 2)], 5812: [(0, 2)], 5816: [(0, 2)], 5833: [(3, 2)], 5837: [(0, 2)], 5850: [(0, 2)], 5853: [(3, 2)], 5859: [(0, 2)], 5860: [(3, 2)], 5863: [(0, 2)], 5873: [(3, 2)], 5876: [(3, 2)], 5878: [(0, 2)], 5879: [(0, 2)], 5882: [(0, 2)], 5884: [(3, 2)], 5886: [(0, 2)], 5887: [(0, 2)], 5893: [(0, 2)], 5895: [(3, 2)], 5903: [(4, 2)], 5910: [(3, 2)], 5914: [(0, 2)], 5916: [(2, 2)], 5920: [(3, 2)], 5923: [(3, 2)], 5924: [(3, 2)], 5925: [(3, 2)], 5927: [(3, 2)], 6074: [(3, 2)], 6206: [(3, 2)], 6265: [(3, 2)], 6294: [(4, 2)], 6303: [(3, 2)], 6309: [(3, 2)], 6316: [(3, 2)], 6390: [(0, 2)], 6527: [(3, 2)], 6550: [(3, 2)], 6796: [(3, 2)], 7003: [(3, 2)], 7013: [(3, 2)], 7015: [(3, 2)], 7045: [(0, 2)], 7071: [(3, 2)], 7082: [(3, 2)], 7101: [(3, 2)], 7103: [(2, 2)], 7124: [(3, 2)], 7141: [(3, 2)], 7155: [(3, 2)], 7159: [(3, 2)], 7162: [(3, 2)], 7174: [(3, 2)], 7230: [(4, 2)], 7296: [(4, 2)], 7379: [(3, 2)], 7410: [(2, 2)], 7415: [(0, 2)], 7444: [(3, 2)], 7462: [(3, 2)], 7517: [(4, 2)], 7553: [(3, 2)], 7555: [(3, 2)], 7561: [(3, 2)], 7576: [(3, 2)], 7937: [(0, 2)], 7974: [(0, 2)]}
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
            decision = 'O protocolo anexo já possui título Markdown correspondente à rubrica explícita do HTML preservado. Cotejo integral ordenado confirmou a preservação; não inventar subdivisões temáticas dentro do protocolo. Encerrado somente o alerta de seções, não revisão semântica ou das traduções.'
        elif operations:
            decision = 'Rubrica explícita do protocolo recuperada por prefixo Markdown reversível, preservando a grafia literal, identificação, data e todos os parágrafos. Não criar títulos para perguntas ou respostas nem emendar a rubrica da fonte.'
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
        keys = [key for key in task['issue_keys'] if key.endswith((':texto_longo_sem_secoes_suficientes', ':decisao_editorial_pendente'))]
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
