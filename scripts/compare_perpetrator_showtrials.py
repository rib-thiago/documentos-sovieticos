"""Produce a non-destructive textual overlap inventory for future imports.

Only uses Python's standard library. This is source analysis, not a catalogue
mutation. Scores describe sampled nine-word sequences, not historical identity.
"""
import collections
import csv
import hashlib
import html
import json
import re
from pathlib import Path
import unicodedata
from urllib.parse import quote
import zlib

OUT = Path('docs/pesquisa/comparacao-perpetrator-showtrials')


def words(text):
    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, count=1, flags=re.S)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'https?://\S+', ' ', text)
    text = unicodedata.normalize('NFKC', html.unescape(text)).lower().replace('ё', 'е')
    return re.findall(r'[a-zа-я0-9]+', text)


def fingerprints(tokens):
    result = {}
    for i in range(len(tokens) - 8):
        phrase = ' '.join(tokens[i:i+9])
        if zlib.crc32(phrase.encode()) % 4 == 0:
            key = hashlib.blake2b(phrase.encode(), digest_size=12).hexdigest()
            result.setdefault(key, phrase)
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    docs = {d['id']: d for d in json.loads(Path('data/catalog/documents.json').read_text())}
    editions = [e for e in json.loads(Path('data/catalog/editions.json').read_text())
                if e['document_id'].startswith('showtrials-') and e['language'] == 'ru']
    inverted = collections.defaultdict(list)
    show = {}
    for edition in editions:
        path = Path(edition['file'])
        fp = fingerprints(words(path.read_text()))
        show[edition['document_id']] = (edition, fp)
        for key in fp:
            inverted[key].append(edition['document_id'])
    # Ubiquitous formulas cannot establish document identity.
    common = {key for key, ids in inverted.items() if len(ids) > 25}
    for _, fp in show.values():
        for key in common:
            fp.pop(key, None)
    conversions = json.loads(Path('docs/pesquisa/conversao-perpetrator2004/registro.json').read_text())['registros']
    records, pairs = [], []
    for source in conversions:
        if not source['markdown']:
            continue
        path = Path(source['markdown'])
        text = path.read_text()
        fp = fingerprints(words(text))
        fp = {k:v for k,v in fp.items() if k not in common}
        counts = collections.Counter(docid for key in fp for docid in inverted.get(key, []) if key not in common)
        candidates, covered = [], set()
        for docid, count in counts.most_common():
            edition, target = show[docid]
            left, right = count / max(1, len(fp)), count / max(1, len(target))
            if count < 12 or max(left, right) < .15:
                continue
            overlap = fp.keys() & target.keys()
            covered.update(overlap)
            relation = ('quase_integral_em_ambos' if min(left, right) >= .85 else
                        'showtrials_contido_no_perpetrator' if right >= .8 else
                        'perpetrator_contido_no_showtrials' if left >= .8 else 'sobreposicao_parcial')
            anchors = [fp[k] for k in sorted(overlap)[:3]]
            doc = docs[docid]
            candidate = dict(perpetrator=str(path), showtrials_id=docid,
                             titulo_ru=doc.get('titles', {}).get('ru', ''),
                             titulo_pt=doc.get('titles', {}).get('pt', ''),
                             data=doc.get('historical_date'), source=doc.get('source'),
                             arquivo_showtrials=edition['file'], url_site=f'/#/doc/{docid}',
                             sequencias_comuns=count, cobertura_perpetrator=round(left,4),
                             cobertura_showtrials=round(right,4), relacao=relation, trechos=anchors)
            candidates.append(candidate)
            pairs.append(candidate)
        coverage = len(covered) / max(1, len(fp))
        classification = ('candidato_a_redundancia_integral' if any(c['relacao']=='quase_integral_em_ambos' for c in candidates)
                          else 'sobreposicao_a_revisar' if candidates else 'sem_correspondencia_detectada')
        records.append(dict(arquivo=str(path), sha256=source['sha256_markdown'],
                            classificacao=classification, cobertura_conjunta=round(coverage,4),
                            candidatos=candidates, avisos_conversao=source['avisos']))
    result = dict(metodo='Sequências de nove palavras; amostragem determinística 1/4; fórmulas presentes em mais de 25 documentos descartadas.',
                  limites='Similaridade textual não certifica identidade documental. Ausência de coincidência não comprova ineditismo. Cobertura é de sequências amostradas, não de caracteres ou páginas.',
                  documentos_showtrials=len(show), arquivos_perpetrator=len(records),
                  resumo=dict(collections.Counter(r['classificacao'] for r in records)), registros=records)
    (OUT/'comparacao.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    fields = ['perpetrator','showtrials_id','titulo_pt','cobertura_perpetrator','cobertura_showtrials','relacao','url_site']
    with (OUT/'correspondencias.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader(); writer.writerows(pairs)
    with (OUT/'triagem.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['arquivo','classificacao','cobertura_conjunta','ids_showtrials','avisos_conversao'])
        for r in records:
            writer.writerow([r['arquivo'],r['classificacao'],r['cobertura_conjunta'],
                             '; '.join(c['showtrials_id'] for c in r['candidatos']),'; '.join(r['avisos_conversao'])])
    lines = ['# Perpetrator2004 × ShowTrials', '',
             f"Comparados {len(records)} arquivos do Perpetrator2004 com {len(show)} edições russas do catálogo atual ShowTrials.", '',
             result['metodo'], '', result['limites'], '',
             'Nenhum texto foi removido, cadastrado ou alterado no site. A classificação é uma triagem para revisão.', '',
             '## Como decidir a importação', '',
             '- Quase integral em ambos: candidato a aproveitar o documento já cadastrado; conferir fronteiras, notas e referências antes de dispensar a nova versão.',
             '- ShowTrials contido no Perpetrator: arquivo possivelmente compilatório ou com material adicional. Separar as unidades e preservar as partes novas.',
             '- Perpetrator contido no ShowTrials: verificar se é excerto ou edição diferente do mesmo documento.',
             '- Sobreposição parcial: pode ser citação, compilação ou variante; manter pendente.',
             '- Sem correspondência detectada: candidato à importação, sujeito à identificação editorial; não é garantia de ineditismo.', '',
             'Percentuais abaixo medem sequências textuais compartilhadas. Mesmo alta cobertura conjunta não autoriza descartar notas ou trechos exclusivos.', '',
             '## Inventário completo', '']
    for r in records:
        rel = quote('../../../'+r['arquivo'], safe='/.')
        lines += [f"### [{Path(r['arquivo']).name}]({rel})", '',
                  f"{r['classificacao']}; cobertura conjunta: {r['cobertura_conjunta']:.1%}.", '']
        if not r['candidatos']:
            lines += ['Nenhuma correspondência atingiu o limiar da análise.', '']
        for c in r['candidatos']:
            lines += [f"- **{c['showtrials_id']}** — {c['titulo_pt'] or c['titulo_ru']}. "
                      f"Perpetrator: {c['cobertura_perpetrator']:.1%}; ShowTrials: {c['cobertura_showtrials']:.1%}. "
                      f"`{c['relacao']}`. Abrir: `http://localhost:8000{c['url_site']}`."]
        lines += ['']
    (OUT/'README.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='registros'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
