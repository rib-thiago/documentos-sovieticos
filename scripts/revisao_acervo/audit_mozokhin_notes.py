#!/usr/bin/env python3
"""Cotejo posterior de quatro atribuições já corrigidas; não grava o acervo."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'temporario/revisao-onda4/mozokhin-notas'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    recipes = {}
    for number in (4, 5, 6):
        path = ROOT / f'scripts/coletores/mozokhin/notes-round{number}-recipe.json'
        for unit in json.loads(path.read_text())['units']:
            recipes[unit['id']] = (path, unit)
    manifest = json.loads((OUT.parent / 'baseline/manifest.json').read_text())
    owners = {d['id']: b['id'] for b in manifest['batches'] for d in b['documents']}
    editions = {e['id']: e for e in json.loads((ROOT / 'data/catalog/editions.json').read_text())}
    related = {}
    for number in ('052', '054', '101', '102', '145', '146', '147'):
        uid = 'mozokhin-2013-v1-' + number
        edition = editions[uid + ':ru']
        raw = (ROOT / edition['file']).read_bytes()
        path, recipe = recipes[uid]
        if sha(raw) != edition['sha256'] or sha(raw) != recipe['expected_result_sha256']:
            raise ValueError('Edição posterior preservada; exige novo cotejo: ' + uid)
        text = raw.decode()
        related[number] = {'file': edition['file'], 'sha256': sha(raw),
                           'recipe': str(path.relative_to(ROOT)), 'recipe_sha256': sha(path.read_bytes()),
                           'calls': re.findall(r'\[\^([^\]]+)\](?!:)', text),
                           'definitions': re.findall(r'^\[\^([^\]]+)\]: (.*)$', text, re.M)}
    if '29' in related['054']['calls'] or related['054']['definitions']:
        raise ValueError('Nota indevida no nº54')
    expected = {'052': ('29', 'приложение приводится ниже'),
                '101': ('40', 'Подпись не разборчива.'),
                '145': ('53', 'Без приложения'), '146': ('54', 'подписал Т.Д.Дерибас')}
    for number, pair in expected.items():
        if related[number]['calls'].count(pair[0]) != 1 or related[number]['definitions'].count(pair) != 1:
            raise ValueError('Chamada/definição divergente: ' + number)
    if any(n in related['102']['calls'] for n in ['40']) or any(n in related['147']['calls'] for n in ['53', '54']):
        raise ValueError('Chamada atribuída ao vizinho')
    if any(n == '40' for n, _ in related['102']['definitions']) or any(n in ['53', '54'] for n, _ in related['147']['definitions']):
        raise ValueError('Definição duplicada no vizinho')
    evidence = {'scope': 'Atribuição das notas, não revisão crítica integral ou aprovação de renderização no navegador.',
                'related_editions': related, 'visual_collation': [],
                'previous_history': '20261021172931544115-d005bfa87be7'}
    observations = {94: 'Nota29 no rodapé pertence à chamada no fim do nº52, acima dos títulos53/54; não ao nº54.',
                    180: 'Chamada40 após assinatura do nº101; rodapé40 diz Подпись не разборчива. O nº102 começa entre eles.',
                    292: 'Chamada53 ao fim do nº145 e chamada54 após Ягода no nº146. Rodapé53 Без приложения;54 подписал Т.Д.Дерибас. Nº147 começa antes do rodapé.'}
    for page, observation in observations.items():
        path = ROOT / f'temporario/coletas-quatro/mozokhin/facsimile-checks/round3/v1-{page}.png'
        evidence['visual_collation'].append({'page': page, 'image': str(path.relative_to(ROOT)),
                                             'sha256': sha(path.read_bytes()), 'observation': observation})
    OUT.mkdir(parents=True, exist_ok=True)
    ep = OUT / 'evidence.json'
    ep.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    results = {}
    for number in ('054', '101', '145', '146'):
        uid = 'mozokhin-2013-v1-' + number
        result = results.setdefault(owners[uid], {'batch_id': owners[uid], 'editions': [], 'issues': []})
        result['issues'].append({'key': uid + ':conferencia_notas_20261021',
                                'outcome': 'corrigido_com_evidencia', 'evidence': str(ep.relative_to(ROOT)),
                                'next_action': 'Atribuição atual conferida com fac-símile e receitas; nenhuma nova alteração textual. A revisão geral de metadados/proveniência permanece no motivo coleta_quatro_colecoes.'})
    for bid, result in results.items():
        (OUT / (bid + '.result.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('Quatro conferências pontuais preparadas; nenhum texto ou catálogo alterado.')


if __name__ == '__main__':
    main()
