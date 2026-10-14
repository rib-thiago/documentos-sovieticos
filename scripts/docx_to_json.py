#!/usr/bin/env python3
"""
Converte um par de DOCX (RU + PT) em um JSON bilíngue para o site,
usando cabeçalhos (I., II., 1., 2. ...) como âncoras de alinhamento.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from docx import Document

ROMAN_HEADING = re.compile(r'^[IVX]+\.\s')
NUM_HEADING   = re.compile(r'^\d+\.\s')
PAGE_MARKER   = re.compile(r'^={2,}\s*Page\s+\d+\s*={2,}\s*$', re.I)
NUMBER_NOISE  = re.compile(r'^(\d+\.\s*)+$')
TITLE_LINE    = re.compile(r'^Показания\s+Н\.?\s*[И.]?\s*Бухарина', re.I)
FOOTNOTE_MARK = re.compile(r'(?=\[\d+\]\s)')      # quebra antes de [N]


def should_skip(text):
    t = text.strip()
    if not t:
        return True
    if t.replace('\xa0', '').strip() == '':
        return True
    if NUMBER_NOISE.match(t):
        return True
    if PAGE_MARKER.match(t):
        return True
    return False


def split_footnotes(text):
    """Se um parágrafo contém 2+ marcadores [N], quebra em vários."""
    if len(re.findall(r'\[\d+\]', text)) < 2:
        return [text]
    parts = FOOTNOTE_MARK.split(text)
    return [p.strip() for p in parts if p.strip()]


def is_heading(text):
    t = text.strip()
    return bool(ROMAN_HEADING.match(t) or NUM_HEADING.match(t))


def classify(text, idx):
    t = text.strip()
    if idx == 0 and len(t) < 120:
        return "h1"
    if TITLE_LINE.match(t):
        return "h1"
    if ROMAN_HEADING.match(t):
        return "h2"
    if NUM_HEADING.match(t):
        return "h3"
    return "p"


def read_docx(path):
    doc = Document(str(path))
    items = []
    idx = 0
    for p in doc.paragraphs:
        raw = p.text
        if should_skip(raw):
            continue
        text = PAGE_MARKER.sub('', raw.strip()).strip()
        if not text:
            continue
        for chunk in split_footnotes(text):
            items.append({"type": classify(chunk, idx), "text": chunk})
            idx += 1
    return items


def align_by_headings(ru_items, pt_items):
    r_head = [i for i, x in enumerate(ru_items) if is_heading(x["text"])]
    p_head = [i for i, x in enumerate(pt_items) if is_heading(x["text"])]

    print(f"Cabeçalhos RU: {len(r_head)} | PT: {len(p_head)}", file=sys.stderr)

    if len(r_head) != len(p_head):
        n = min(len(r_head), len(p_head))
        r_head = r_head[:n]
        p_head = p_head[:n]

    anchors = list(zip(r_head, p_head))

    pairs = []
    prev_r, prev_p = -1, -1
    for r_h, p_h in anchors:
        r_seg = list(range(prev_r + 1, r_h))
        p_seg = list(range(prev_p + 1, p_h))
        for k in range(max(len(r_seg), len(p_seg))):
            r_i = r_seg[k] if k < len(r_seg) else None
            p_i = p_seg[k] if k < len(p_seg) else None
            pairs.append((r_i, p_i))
        pairs.append((r_h, p_h))
        prev_r, prev_p = r_h, p_h

    r_tail = list(range(prev_r + 1, len(ru_items)))
    p_tail = list(range(prev_p + 1, len(pt_items)))
    for k in range(max(len(r_tail), len(p_tail))):
        r_i = r_tail[k] if k < len(r_tail) else None
        p_i = p_tail[k] if k < len(p_tail) else None
        pairs.append((r_i, p_i))

    rank = {"h1": 0, "h2": 1, "h3": 2, "p": 3}
    blocks = []
    for r_i, p_i in pairs:
        ru = ru_items[r_i] if r_i is not None else None
        pt = pt_items[p_i] if p_i is not None else None
        types = [x["type"] for x in (ru, pt) if x]
        btype = min(types, key=lambda t: rank.get(t, 99)) if types else "p"
        blocks.append({
            "type": btype,
            "ru": (ru or {}).get("text", ""),
            "pt": (pt or {}).get("text", ""),
        })
    return blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ru", required=True)
    ap.add_argument("--pt", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title-ru", default="")
    ap.add_argument("--title-pt", default="")
    args = ap.parse_args()

    ru_items = read_docx(args.ru)
    pt_items = read_docx(args.pt)

    print(f"RU: {len(ru_items)} blocos | PT: {len(pt_items)} blocos", file=sys.stderr)

    blocks = align_by_headings(ru_items, pt_items)
    print(f"Alinhados: {len(blocks)} blocos", file=sys.stderr)

    payload = {
        "id": args.id,
        "title_ru": args.title_ru,
        "title_pt": args.title_pt,
        "blocks": blocks,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: escrito em {out}", file=sys.stderr)


if __name__ == "__main__":
    main()