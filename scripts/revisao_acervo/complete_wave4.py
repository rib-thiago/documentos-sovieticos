#!/usr/bin/env python3
"""Conclui candidatos interrompidos, sem gravar textos/catálogo/fila."""
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/revisao_acervo'))
from prepare_source_links import Source, resolve_url, sha

WORK = ROOT / 'temporario/revisao-onda4'
OUT = WORK / 'completion'


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    OUT.mkdir(exist_ok=True)
    manifest = json.loads((WORK / 'baseline/manifest.json').read_text())
    owners = {d['id']: b['id'] for b in manifest['batches'] for d in b['documents']}
    editions = {e['id']: e for e in json.loads((ROOT / 'data/catalog/editions.json').read_text())}
    results = {}

    def result(uid):
        bid = owners[uid]
        return results.setdefault(bid, {'batch_id': bid, 'editions': [], 'issues': []})

    # Complete only the six candidates whose evidence was fully written.
    for ep in sorted((WORK / 'secoes').glob('*/*.evidence.json')):
        evidence = json.loads(ep.read_text())
        uid = evidence['document_id']
        edition = editions[uid + ':ru']
        raw = (ROOT / edition['file']).read_bytes()
        candidate = ep.parent / (uid + '.ru.md')
        if sha(raw) != evidence['before_sha256'] or sha(candidate.read_bytes()) != evidence['candidate_sha256']:
            raise ValueError('Candidato de título mudou: ' + uid)
        lines = raw.decode().splitlines(keepends=True)
        operations = evidence['heading_insertions']
        if len({op['line'] for op in operations}) != len(operations):
            raise ValueError('Linha duplicada')
        source = evidence['source']
        post = next(p for p in json.loads((ROOT / source['source_json']).read_text()) if p['id'] == int(uid.split('-')[1]))
        html = post['content']['rendered']
        if sha(html.encode()) != source['source_html_sha256']:
            raise ValueError('Fonte mudou')
        for op in operations:
            index = op['line'] - 1
            if lines[index].rstrip('\r\n') != op['literal_line']:
                raise ValueError('Título não corresponde ao canônico')
            # The captured element must exist as HTML text; no inferred heading.
            if Source(op['source_html']).text != ''.join(c for c in op['source_text'] if not c.isspace()):
                raise ValueError('Texto do elemento divergente')
            if Source(op['source_html']).text not in Source(html).text:
                raise ValueError('Título não está na fonte')
            lines[index] = '#' * op['level'] + ' ' + lines[index]
        if ''.join(lines).encode() != candidate.read_bytes():
            raise ValueError('Mudança além de prefixos de título')
        owner = result(uid)
        owner['editions'].append({'document_id': uid, 'language': 'ru', 'file': edition['file'],
                                  'before_sha256': sha(raw), 'candidate': str(candidate.relative_to(ROOT)),
                                  'candidate_sha256': sha(candidate.read_bytes()), 'source_evidence': str(ep.relative_to(ROOT))})
        owner['issues'].append({'key': uid + ':texto_longo_sem_secoes_suficientes', 'outcome': 'corrigido_com_evidencia',
                                'evidence': str(ep.relative_to(ROOT)), 'next_action': 'Títulos literais comprovados recuperados; nenhuma divisão temática inventada ou alegação validada como fato.'})

    # Repair four malformed wrappers inherited from the first table pilot.
    uid = 'showtrials-4576'
    edition = editions[uid + ':ru']
    text = (ROOT / edition['file']).read_text()
    pattern = re.compile(r'\\\[\[([12])\\\]\]\(<([^>]+)>\)')
    matches = list(pattern.finditer(text))
    if len(matches) != 4:
        raise ValueError('Forma inesperada dos quatro links legados')
    repaired = pattern.sub(lambda m: '[\\[' + m[1] + '\\]](<' + m[2] + '>)', text)
    spec = importlib.util.spec_from_file_location('table_projection', WORK / 'tabelas/prepare.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    prior = json.loads((WORK / 'tabelas' / (uid + '.evidence.json')).read_text())
    post = next(p for p in json.loads((ROOT / prior['source_json']).read_text()) if p['id'] == 4576)
    source = Source(post['content']['rendered'])
    normalized, spans, existing = module.projection(repaired)
    if normalized != source.text or len(existing) != 68:
        raise ValueError('Projeção integral dos links legados divergiu')
    checked = []
    for anchor in source.anchors:
        if anchor['href'] is None:
            continue
        url, reason = resolve_url(anchor['href'], post['link'], source.targets)
        begin, end = spans[anchor['start']][0], spans[anchor['end'] - 1][1]
        if reason or not any(e['begin'] == begin and e['end'] == end and e['url'] == url for e in existing):
            raise ValueError('Link não corresponde à âncora original')
        checked.append({'href': anchor['href'], 'resolved_href': url, 'label': repaired[begin:end]})
    note = ('\n\n---\n\n> **Редакционное примечание — Documentos Soviéticos**\n>\n'
            '> В исходной публикации имя Логинова Ивана Харитоновича связано со ссылкой, в адресе которой указано другое имя (Пётр Петрович). '
            'Опубликованный адрес сохранён; такая ссылка сама по себе не устанавливает тождество лиц.\n')
    target = OUT / (uid + '.ru.md')
    target.write_text(repaired + note)
    evidence = {'document_id': uid, 'before_sha256': sha(text.encode()), 'source_json': prior['source_json'],
                'source_html_sha256': sha(post['content']['rendered'].encode()), 'existing_links_verified': checked,
                'repairs': [{'before': m[0], 'after': pattern.sub(lambda n: '[\\[' + n[1] + '\\]](<' + n[2] + '>)', m[0])} for m in matches],
                'finding': 'Somente quatro invólucros legados corrigidos, com mesmos rótulos e URLs; igualdade integral da projeção HTML e 68 âncoras cotejadas. Nota editorial separada registra a divergência nominativa da URL sem corrigi-la.'}
    ep = OUT / (uid + '.evidence.json')
    dump(ep, evidence)
    result(uid)['editions'].append({'document_id': uid, 'language': 'ru', 'file': edition['file'], 'before_sha256': sha(text.encode()),
                                   'candidate': str(target.relative_to(ROOT)), 'candidate_sha256': sha(target.read_bytes()), 'source_evidence': str(ep.relative_to(ROOT))})
    result(uid)['issues'].append({'key': uid + ':links_nao_reconstruidos', 'outcome': 'corrigido_com_evidencia', 'evidence': str(ep.relative_to(ROOT)),
                                 'next_action': '68 destinos cotejados; quatro invólucros de notas reparados. Divergência nominativa do vínculo externo preservada e explicada; não constitui autoridade confirmada.'})

    # The missing HTML identifier does not prove that the note text is missing.
    uid = 'showtrials-2644'
    prior = json.loads((WORK / 'tabelas' / (uid + '.evidence.json')).read_text())
    retained = prior['retained']
    if len(retained) != 1 or retained[0]['href'] != '#_edn52':
        raise ValueError('Ressalva inesperada na nota52')
    notes = {
        'ru': 'В сохранённом HTML исходной публикации ссылка #_edn52 не имеет элемента с соответствующим идентификатором. Указатель и тексты примечаний сохранены; отсутствующий HTML-адрес не был заменён предположительной связью.',
        'pt': 'No HTML preservado da publicação de origem, a chamada #_edn52 não tem elemento com o identificador correspondente. A chamada e os textos das notas foram preservados; não se substituiu o destino HTML ausente por uma correspondência inferida.',
        'en': 'In the preserved HTML of the source publication, the #_edn52 reference has no element bearing the corresponding identifier. The marker and note texts are preserved; the missing HTML destination has not been replaced by an inferred correspondence.'}
    labels = {'ru': 'Редакционное примечание', 'pt': 'Nota editorial', 'en': 'Editorial note'}
    ep = OUT / (uid + '.evidence.json')
    dump(ep, {'document_id': uid, 'table_link_evidence': str((WORK / 'tabelas' / (uid + '.evidence.json')).relative_to(ROOT)),
              'source_json': prior['source_json'], 'source_html_sha256': prior['source_html_sha256'],
              'finding': '1021 destinos recuperados; ausência do identificador HTML52 explicitada nos três idiomas, sem afirmar ausência do texto da nota ou renumerá-la.'})
    for language in ('ru', 'pt', 'en'):
        edition = editions[uid + ':' + language]
        original = (ROOT / edition['file']).read_bytes()
        body = (WORK / 'tabelas' / (uid + '.ru.md')).read_bytes() if language == 'ru' else original
        target = OUT / (uid + '.' + language + '.md')
        target.write_bytes(body + ('\n\n---\n\n> **' + labels[language] + ' — Documentos Soviéticos**\n>\n> ' + notes[language] + '\n').encode())
        result(uid)['editions'].append({'document_id': uid, 'language': language, 'file': edition['file'],
                                       'before_sha256': sha(original), 'candidate': str(target.relative_to(ROOT)),
                                       'candidate_sha256': sha(target.read_bytes()), 'source_evidence': str(ep.relative_to(ROOT))})
    result(uid)['issues'].append({'key': uid + ':links_nao_reconstruidos', 'outcome': 'ressalva_da_fonte_preservada',
                                 'evidence': str(ep.relative_to(ROOT)), 'next_action': 'Destinos recuperados; defeito do identificador52 preservado com ressalva explícita. Não inferir que o texto da nota esteja ausente.'})
    for bid, value in results.items():
        dump(OUT / (bid + '.result.json'), value)
    print('Preparados seis documentos com títulos e conclusão de duas exceções de links; nenhum canônico alterado.')


if __name__ == '__main__':
    main()
