"""Prepare complete, locally acquired 2013 PDFs for a catalog PREVIEW only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

from adapter import printed_contents, segment, snapshot, stage


def footer_markers(bbox):
    """Geometric hints only; never silently relocate a note to another document."""
    output = {}
    number = 0
    for _, page in ET.iterparse(bbox, events=('end',)):
        if page.tag.rsplit('}', 1)[-1] != 'page':
            continue
        number += 1
        height = float(page.get('height'))
        markers = []
        for word in page.findall('.//{*}word'):
            value = word.text or ''
            x, y = float(word.get('xMin')), float(word.get('yMin'))
            size = float(word.get('yMax')) - y
            if re.fullmatch(r'\d{1,3}', value) and size < 9 and y > height * .5 and 45 < x < 130:
                markers.append({'number_literal': value, 'x': x, 'y': y, 'height': size})
        if markers:
            output[number] = markers
        page.clear()
    return output


def shared_page_note_risks(text, sections, notes):
    risks = {}
    pages = {}
    for section in sections:
        first = text[:section['start']].count('\f') + 1
        last = text[:section['end']].count('\f') + 1
        pages[section['number']] = (first, last)
        for page in range(first, last + 1):
            if page in notes:
                # All docs crossing this page need reconciliation of note ownership.
                risks.setdefault(section['number'], []).append(page)
    return risks, pages


def prepare(pdf, output, volume, *, text_file=None, bbox_file=None):
    first, last = (1, 215) if volume == 1 else (216, 295)
    edition = f'2013-v{volume}'
    url = f'https://wr-nsk.ru/wp-content/uploads/2023/04/politbyuro-i-lev-troczkij-{volume}-2013.pdf'
    pdf = Path(pdf)
    if not pdf.read_bytes().startswith(b'%PDF-'):
        raise ValueError('Arquivo fornecido não tem assinatura PDF')
    info = subprocess.run(['pdfinfo', str(pdf)], check=True, capture_output=True, text=True).stdout
    expected_pages = 514 if volume == 1 else 437
    found = re.search(r'(?m)^Pages:\s+(\d+)', info)
    if not found or int(found[1]) != expected_pages:
        raise ValueError(f'Paginação divergente: esperado {expected_pages}; conferir a edição antes de prosseguir')
    raw_pdf, pdf_hash = snapshot(output, pdf.read_bytes(), '.pdf')
    extracted = output / 'extracted'
    extracted.mkdir(parents=True, exist_ok=True)
    txt = extracted / f'{pdf_hash}.layout.txt'
    bbox = extracted / f'{pdf_hash}.bbox.html'
    if not txt.exists():
        if text_file:
            txt.write_bytes(Path(text_file).read_bytes())
        else:
            subprocess.run(['pdftotext', '-layout', str(raw_pdf), str(txt)], check=True)
    if not bbox.exists():
        if bbox_file:
            bbox.write_bytes(Path(bbox_file).read_bytes())
        else:
            subprocess.run(['pdftotext', '-bbox-layout', str(raw_pdf), str(bbox)], check=True)
    text = txt.read_text()
    titles = printed_contents(text, first, last)
    result = segment(text, first, last, source_complete=True, titles=titles)
    if len(titles) != last - first + 1 or result['missing']:
        raise ValueError('Sumário/cabeçalhos incompletos: revisar antes de preparar unidades')
    stage_run = stage(txt, output, url, first, last, kind='text', complete=True, edition=edition)
    notes = footer_markers(bbox)
    risks, page_map = shared_page_note_risks(text, result['sections'], notes)
    (output / f'v{volume}-footnote-markers.json').write_text(json.dumps(notes, ensure_ascii=False, indent=2) + '\n')
    by_number = {s['number']: s for s in result['sections']}
    units = []
    for record in stage_run['documents']:
        number = record['number']
        issues = list(record['issues'])
        blocking = record['status'] != 'candidate_unreviewed'
        if number in risks:
            issues.insert(0, f'Conferir chamada e atribuição das notas pequenas de rodapé nas páginas PDF {risks[number]}; notas não foram realocadas automaticamente')
            blocking = True
        body = by_number[number]['text']
        table_lines = [line for line in body.splitlines() if len(re.findall(r'\S[ \t]{7,}\S', line)) >= 2]
        if len(table_lines) >= 3 or number == 109:
            issues.insert(0, 'Possível tabela/lista multicoluna: conferir e reconstruir estrutura antes da incorporação')
            blocking = True
        first_page, last_page = page_map[number]
        provenance = {'edition': edition, 'editor': 'О. Б. Мозохин', 'publication_year': 2013,
                      'source_url': url, 'discovery_url': 'https://wr-nsk.ru/partijnoe-stroitelstvo/',
                      'acquisition': 'public_direct_pdf', 'physical_pdf_pages': expected_pages,
                      'pdf_page_start': first_page, 'pdf_page_end': last_page,
                      'printed_document_number': number, 'title_source': 'printed_contents_number_matched_to_body',
                      'text_extraction': 'pdftotext -layout; existing text layer; no new OCR',
                      'extracted_text': str(txt.relative_to(output)),
                      'extracted_text_sha256': record['source_sha256'],
                      'footer_note_review_required': number in risks,
                      'integral_source_acquired': True, 'editorial_review': 'unreviewed',
                      'boundary_check': 'body heading and unique printed-contents title correspondence'}
        units.append({'id': record['id'], 'title_literal': titles[number], 'title_pt': None,
                      'language': 'ru', 'original_language': 'ru', 'kind': 'document',
                      'document_type': 'documento', 'subcollection': f'livro-{volume}-2013',
                      'source_url': url, 'markdown': str(Path(record['markdown_path']).relative_to(output)),
                      'markdown_sha256': record['markdown_sha256'], 'raw': str(raw_pdf.relative_to(output)),
                      'raw_sha256': pdf_hash, 'ready_for_import': not blocking,
                      'issues': issues, 'provenance': provenance})
    report = {'volume': volume, 'pdf_pages': expected_pages, 'pdf_sha256': pdf_hash,
              'pdfinfo': info, 'numbered_documents': len(units), 'missing': result['missing'],
              'rejected_internal_headers': result['rejected_internal_headers'],
              'ready_for_import': sum(u['ready_for_import'] for u in units),
              'blocked_for_review': sum(not u['ready_for_import'] for u in units),
              'footer_note_pages': sorted(notes), 'units': units}
    (output / f'v{volume}-preparation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--volume-1', type=Path, required=True)
    parser.add_argument('--volume-2', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    reports = [prepare(args.volume_1, args.output, 1), prepare(args.volume_2, args.output, 2)]
    units = [u for report in reports for u in report['units']]
    (args.output / 'units.json').write_text(json.dumps(units, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'units': len(units), 'ready_for_import': sum(u['ready_for_import'] for u in units)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
