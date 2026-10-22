#!/usr/bin/env python3
"""Emitir unidades candidatas, com decisões explícitas e vínculo à versão revisada."""
import argparse
import json
from pathlib import Path
import re

from collect import DEFAULT_OUT, digest, immutable, now, write_json


def title_from_body(body):
    for line in body.splitlines():
        line = re.sub(r'^[> #]+', '', line).strip().strip('*').strip()
        if not line or line.startswith(('[', '<')) or line.lower().startswith(('transcripts from', 'archive:', 'source:')):
            continue
        return line[:600]
    return None


def ranged_text(body, entry):
    """Faixas editoriais explícitas, protegidas pelo hash da página inteira."""
    ranges = entry['ranges']
    if not isinstance(ranges, list) or not ranges:
        raise ValueError('Faixas documentais vazias')
    previous = 0
    chunks = []
    for interval in ranges:
        if (not isinstance(interval, list) or len(interval) != 2
                or any(type(x) is not int for x in interval)):
            raise ValueError('Faixa documental inválida')
        start, end = interval
        if not (previous <= start < end <= len(body)):
            raise ValueError('Faixa fora da fonte ou sobreposta na mesma unidade')
        chunks.append(body[start:end].strip())
        previous = end
    return '\n\n'.join(chunks).strip() + '\n'


def validate_coverage(body, rule):
    if not any('ranges' in entry for entry in rule['units']):
        return
    coverage = bytearray(len(body))
    shared = bytearray(len(body))
    ignored = bytearray(len(body))
    for key, target in [('shared_ranges', shared), ('ignored_ranges', ignored)]:
        for start, end in rule.get(key, []):
            if not 0 <= start < end <= len(body):
                raise ValueError('Faixa de aparato/navegação inválida')
            target[start:end] = b'\x01' * (end-start)
    for entry in rule['units']:
        ranged_text(body, entry)
        if not entry.get('expected_output_sha256'):
            raise ValueError('Unidade por faixas sem hash de saída conferido')
        for start, end in entry['ranges']:
            for offset in range(start, end):
                if coverage[offset] and not shared[offset]:
                    raise ValueError('Sobreposição documental não declarada')
                if ignored[offset] and not body[offset].isspace():
                    raise ValueError('Trecho ignorado também incluído em documento')
                coverage[offset] = 1
    if any(not coverage[i] and not ignored[i] and not char.isspace() for i, char in enumerate(body)):
        raise ValueError('Texto da fonte perdido entre unidades')


def build(out, decisions_path=None):
    inventory = json.loads((out / 'inventory.json').read_text())
    decisions = json.loads((decisions_path or Path(__file__).with_name('unit_decisions.json')).read_text())
    units = []
    for cid, candidate in inventory['candidates'].items():
        latest = candidate.get('latest_success')
        if not latest:
            continue
        body = (out / latest['markdown']).read_text()
        rule = decisions.get(cid)
        valid = rule and digest(body) == rule['expected_markdown_sha256']
        if valid and rule.get('expected_raw_sha256'):
            valid = digest((out / latest['raw']).read_bytes()) == rule['expected_raw_sha256']
        if valid:
            validate_coverage(body, rule)
        entries = rule['units'] if valid else [{'suffix': 'unreviewed', 'range': 'whole',
            'title_literal': title_from_body(body), 'date_literal': None, 'ready_for_import': False,
            'reason': 'Fronteiras, título, datas e extensão das notas ainda não conferidos; pode haver documentos compostos.'}]
        if rule and not valid:
            entries[0]['reason'] = 'A versão do Markdown mudou após a conferência; decisão anterior suspensa até nova revisão.'
        chunks = body.split(rule['separator']) if valid and rule.get('separator') else [body]
        if valid and rule.get('separator') and len(chunks) != len(entries):
            raise ValueError(f'Separador documental inesperado: {cid}')
        for entry in entries:
            text = ranged_text(body, entry) if 'ranges' in entry else body if entry['range'] == 'whole' else chunks[entry['range']].strip() + '\n'
            if entry.get('normalize_layout_quotes'):
                text = re.sub(r'(?m)^[ \t]*(?:>[ \t]*)+', '', text)
                text = re.sub(r'\n{3,}', '\n\n', text).strip() + '\n'
                # The source breadcrumb is navigation, not part of the document.
                if text.startswith('['):
                    first, separator, rest = text.partition('\n\n')
                    if '](<' in first and 'index.htm' in first.lower():
                        text = rest
            if entry.get('expected_output_sha256') and digest(text) != entry['expected_output_sha256']:
                raise ValueError(f'Hash do documento individualizado divergente: {cid}')
            uid = cid + '-' + entry['suffix']
            sha = digest(text)
            relative = Path('units') / uid / (sha + '.en.md')
            immutable(out / relative, text.encode())
            # Unknown individual translators remain unknown; organizers do not
            # become authors or translators merely through collection membership.
            units.append({'id': uid, 'candidate_id': cid, 'source_url': candidate['url'],
                'language': latest['language'], 'original_language': latest['original_language'],
                'title_literal': entry['title_literal'], 'date_literal': entry.get('date_literal'),
                'raw': latest['raw'], 'markdown': str(relative),
                'markdown_sha256': sha, 'raw_sha256': latest['sha256'],
                'kind': 'reference' if latest.get('html_content_class') == 'pdf_wrapper' else 'document', 'document_type': None,
                'extent': entry.get('extent', 'not_assessed'),
                'subcollection': candidate['occurrences'][0]['source_id'].lower(),
                'hashes': {'raw_sha256': latest['sha256'], 'markdown_sha256': sha,
                           'source_markdown_sha256': latest['markdown_sha256']},
                'occurrences': candidate['occurrences'],
                'provenance': {'source_url': candidate['url'], 'resolved_url': latest['resolved_url'],
                    'source_markdown': latest['markdown'], 'collected_at': latest.get('fetched_at', latest['at']),
                    'converted_at': latest['at'],
                    'index_sources': [{'id': o['source_id'], 'url': inventory['sources'].get(o['source_id'], {}).get('url')}
                                      for o in candidate['occurrences']],
                    'translator': latest.get('translator'), 'document_author': latest.get('document_author'),
                    'attribution_status': 'individual_translator_not_established',
                    'linked_resources': latest.get('linked_resources', []),
                    'document_ranges': entry.get('ranges'),
                    'shared_apparatus_ranges': rule.get('shared_ranges') if valid else None,
                    'excluded_navigation_ranges': rule.get('ignored_ranges') if valid else None,
                    'decision_matches_source_hash': bool(valid)},
                'ready_for_import': entry['ready_for_import'], 'reason': entry['reason'],
                'warnings': latest['warnings'],
                'issues': entry.get('issues', [] if entry['ready_for_import'] else ['document_boundaries_unreviewed'])
                          + ['individual_translator_not_established'],
                'boundary_evidence': {'first_160': text[:160], 'last_160': text[-160:]}})
    payload = {'schema_version': 1, 'generated_at': now(), 'canonical_import_performed': False,
        'review_scope': 'Prontidão estrutural e proveniência; não revisão filológica da tradução nem eliminação final de duplicatas.',
        'known_overlap': {'source_url': 'https://istmat.org/node/27376',
            'existing_document_id': 'tukhachevsky-nko37-01-pm',
            'action': 'Verificar a equivalência textual antes de vincular qualquer tradução inglesa.'},
        'units': units}
    write_json(out / 'units.json', payload)
    print(json.dumps({'units': len(units), 'ready_for_import': sum(u['ready_for_import'] for u in units)}, ensure_ascii=False))
    return payload


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=DEFAULT_OUT)
    build(ap.parse_args().out)
