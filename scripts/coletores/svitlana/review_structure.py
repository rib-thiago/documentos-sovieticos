#!/usr/bin/env python3
"""Diagnóstico local de TODAS as páginas; não aprova nem modifica fontes/catalogo."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build(out, report):
    inventory = json.loads((out / 'inventory.json').read_text())
    decisions = json.loads(Path(__file__).with_name('unit_decisions.json').read_text())
    rows = []; groups = defaultdict(list)
    for cid, candidate in inventory['candidates'].items():
        latest = candidate.get('latest_success')
        if not latest:
            rows.append({'candidate_id': cid, 'source_url': candidate['url'], 'state': 'source_missing', 'priority': 1})
            continue
        blob = (out / latest['markdown']).read_bytes(); text = blob.decode('utf-8')
        raw = (out / latest['raw']).read_bytes()
        clean = re.sub(r'(?m)^\s*(?:>\s*)+', '', text)
        flags = []
        if sha(blob) != latest['markdown_sha256'] or sha(raw) != latest['sha256']:
            flags.append('source_hash_mismatch')
        warnings = latest.get('warnings', [])
        if latest.get('html_content_class') == 'pdf_wrapper': flags.append('pdf_reference_only')
        if 'complex_table_requires_review_source_html' in warnings: flags.append('complex_table')
        if 'short_body_requires_review' in warnings: flags.append('short_body')
        if 'generic_body_extraction_requires_boundary_review' in warnings: flags.append('generic_extraction')
        if '\ufffd' in text: flags.append('replacement_character')
        # Indicadores para localizar passagens, nunca uma decisão de segmentação.
        markers = [{'offset': m.start(), 'text': m.group(0).strip()[:200]} for m in re.finditer(
            r'(?mi)^\s*(?:Appendix\s*(?:No\.?|№|[0-9])[^\n]*|Enclosure[^\n]*|Archive\s*:[^\n]*|Notes and Comments[^\n]*)', clean)]
        if len(markers) > 1: flags.append('multiple_apparatus_or_appendix_markers')
        rule = decisions.get(cid)
        matches = bool(rule and rule.get('expected_markdown_sha256') == sha(blob))
        ready = sum(bool(u.get('ready_for_import')) for u in rule.get('units', [])) if matches else 0
        state = 'reviewed_ready' if ready else 'reviewed_retained' if matches else 'unreviewed'
        if rule and not matches: flags.append('stale_decision')
        if 'source_hash_mismatch' in flags: state = 'integrity_blocked'
        priority = 1 if any(f in flags for f in ['source_hash_mismatch','replacement_character','stale_decision']) else 2 if any(f in flags for f in ['complex_table','multiple_apparatus_or_appendix_markers']) else 3
        if 'pdf_reference_only' in flags: priority = 2
        row = {'candidate_id': cid, 'source_url': candidate['url'], 'state': state, 'priority': priority,
            'flags': flags, 'characters': len(text), 'paragraph_blocks': len(re.split(r'\n\s*\n', clean.strip())),
            'ready_units': ready, 'title_page_unverified': latest.get('title_page'),
            'first_240': clean[:240], 'last_240': clean[-240:], 'markers': markers,
            'raw': latest['raw'], 'markdown': latest['markdown'], 'raw_sha256': sha(raw),
            'markdown_sha256': sha(blob), 'source_series': sorted({o['source_id'] for o in candidate['occurrences']})}
        rows.append(row)
        # Somente igualdade literal após remoção de espaços/layout de blockquote.
        signature = sha(re.sub(r'\s+', ' ', clean).strip().encode())
        groups[signature].append(cid)
    duplicates = [v for v in groups.values() if len(v) > 1]
    for group in duplicates:
        for row in rows:
            if row['candidate_id'] in group:
                row['same_normalized_text_candidates'] = [x for x in group if x != row['candidate_id']]
                row['flags'].append('same_normalized_text_requires_review')
                row['priority'] = min(row['priority'], 2)
    result = {'generated_at': datetime.now(timezone.utc).isoformat(), 'automatic_approval': False,
        'scope': 'Diagnóstico mecânico de páginas; revisão editorial exige leitura do HTML e Markdown.',
        'counts': dict(Counter(r['state'] for r in rows)),
        'flags': dict(Counter(f for r in rows for f in r.get('flags', []))),
        'normalized_duplicate_groups': duplicates, 'pages': rows}
    report.mkdir(parents=True, exist_ok=True)
    (report / 'SVITLANA-ESTRUTURA.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    fields = ['candidate_id','source_url','state','priority','flags','characters','ready_units','source_series','same_normalized_text_candidates','raw','markdown','markdown_sha256']
    stream = io.StringIO(newline=''); writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore');writer.writeheader()
    for row in rows:
        writer.writerow({k: json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()})
    (report / 'SVITLANA-ESTRUTURA.csv').write_text(stream.getvalue())
    print(json.dumps({k: result[k] for k in ['counts','flags']},ensure_ascii=False))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=ROOT/'temporario/coletas-quatro/svitlana')
    ap.add_argument('--report',type=Path,default=ROOT/'docs/pesquisa/quatro-coletores')
    args=ap.parse_args();build(args.out,args.report)
