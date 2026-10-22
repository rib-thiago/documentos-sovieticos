#!/usr/bin/env python3
"""Recupera quatro cabeçalhos anuais explícitos após a tabela já cotejada.

Prepara candidatos e evidência; não grava o acervo nem a fila.
"""
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'temporario/revisao-onda2/secoes4828'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    manifest = json.loads((ROOT / 'temporario/revisao-onda2/baseline/manifest.json').read_text())
    batch = next(b for b in manifest['batches'] if any(d['id'] == 'showtrials-4828' for d in b['documents']))
    doc = next(d for d in batch['documents'] if d['id'] == 'showtrials-4828')
    edition = next(e for e in doc['editions'] if e['language'] == 'ru')
    raw = (ROOT / edition['file']).read_bytes()
    if sha(raw) != edition['sha256']:
        raise ValueError('Edição mudou após o despacho')
    proposals = json.loads((ROOT / 'docs/revisao-markdown/diagnostico-geral/proposals-showtrials.json').read_text())
    source = next(x['evidencia'] for x in proposals['proposals'] if x['chave'] == 'showtrials-4828:decisao_editorial_pendente')
    post = next(p for p in json.loads((ROOT / source['source_json']).read_text()) if p['id'] == 4828)
    html = post['content']['rendered']
    if sha(html.encode()) != source['source_html_sha256']:
        raise ValueError('Fonte mudou')
    soup = BeautifulSoup(html, 'html.parser')
    outside = [p for p in soup.find_all('p') if not p.find_parent('table')]
    text = raw.decode()
    edits = []
    for year in range(1932, 1936):
        label = f'{year} г.'
        matches = [p for p in outside if p.get_text(' ', strip=True) == label]
        positions = list(re.finditer('^' + re.escape(label) + '$', text, re.M))
        if len(matches) != 1 or len(positions) != 1:
            raise ValueError('Cabeçalho sem contexto único: ' + label)
        p = matches[0]
        edits.append({'offset': positions[0].start(), 'text': label, 'html': str(p),
                      'following_source_paragraph': p.find_next('p').get_text(' ', strip=True)})
    candidate = text
    for edit in sorted(edits, key=lambda e: e['offset'], reverse=True):
        at = edit['offset']
        candidate = candidate[:at] + '## ' + candidate[at:]
    restored = re.sub(r'^## (193[2-5] г\.)$', r'\1', candidate, flags=re.M)
    if restored.encode() != raw:
        raise ValueError('Mudança além da marcação dos quatro títulos')
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / 'showtrials-4828.ru.md'
    target.write_text(candidate)
    evidence = {'source_json': source['source_json'], 'source_html_sha256': sha(html.encode()),
                'before_sha256': sha(raw), 'candidate_sha256': sha(target.read_bytes()),
                'heading_insertions': edits,
                'prior_table_collation_receipt': 'docs/revisao-markdown/diagnostico-geral/onda1-estruturas-20261021-gravacao.json',
                'finding': 'A grade financeira já foi reconstruída e cotejada na onda 1. A numeração é de registros, não de seções. Fora da tabela, quatro cabeçalhos anuais explícitos introduzem listas suplementares; apenas esses cabeçalhos recebem Markdown. Valores, listas, repetições, totais e cota permanecem integrais.'}
    ep = OUT / 'evidence.json'
    ep.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    result = {'batch_id': batch['id'], 'editions': [{
        'document_id': doc['id'], 'language': 'ru', 'file': edition['file'],
        'before_sha256': sha(raw), 'candidate': str(target.relative_to(ROOT)),
        'candidate_sha256': sha(target.read_bytes()), 'source_evidence': str(ep.relative_to(ROOT))}],
        'issues': [{'key': doc['id'] + ':' + problem, 'outcome': 'corrigido_com_evidencia',
                    'evidence': str(ep.relative_to(ROOT)),
                    'next_action': 'Grade financeira já cotejada; quatro títulos anuais explícitos recuperados. Não promover números de registros a títulos.'}
                   for problem in ['decisao_editorial_pendente', 'texto_longo_sem_secoes_suficientes']]}
    (OUT / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('Preparados quatro cabeçalhos; nenhum canônico alterado.')


if __name__ == '__main__':
    main()
