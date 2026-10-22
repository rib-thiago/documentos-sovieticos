#!/usr/bin/env python3
"""Consolida os quatro pilotos para revisão. Nunca escreve no acervo público."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]


def read(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def normalize_url(url):
    """Chave de comparação; não substitui a URL histórica cadastrada."""
    if not isinstance(url, str):
        return ""
    parts = urlsplit(url)
    if parts.hostname == "web.archive.org":
        for marker in ("/https://", "/http://"):
            if marker in parts.path:
                return normalize_url(parts.path[parts.path.index(marker) + 1:] + ("?" + parts.query if parts.query else ""))
    host = (parts.hostname or "").lower().removeprefix("www.")
    if not host:
        return ""
    if parts.port:
        host += ":" + str(parts.port)
    # Apenas uma chave de conciliação: HTTP/HTTPS não geram novos documentos.
    return urlunsplit(("https", host, unquote(parts.path) or "/", urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True))), ""))


def urls(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ("url", "source_url", "original_url", "captured_original_url", "archive_url") and isinstance(child, str):
                yield child
            elif isinstance(child, (dict, list)):
                yield from urls(child)
    elif isinstance(value, list):
        for child in value:
            yield from urls(child)


def verify_file(base, value, expected_hash=None):
    if not value:
        return None
    path = Path(value)
    # Mozokhin registra caminho relativo ao repositório; outros, à frente.
    path = ROOT / path if path.parts[:2] == ("temporario", "coletas-quatro") else base / path
    path = path.resolve()
    if not path.is_relative_to(base.resolve()):
        return {"path": str(value), "error": "Caminho fora da frente de coleta"}
    if not path.is_file():
        return {"path": str(value), "error": "Arquivo não encontrado"}
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path), "sha256": digest,
            "hash_matches": digest == expected_hash if expected_hash else None}


def candidate(front, key, row, base, *, path=None, raw=None, digest=None, raw_digest=None, issues=()):
    return {
        "front": front, "id": str(key), "source_url": row.get("source_url", row.get("url", "")),
        "language": row.get("language", row.get("idioma")),
        "title": row.get("title", row.get("title_page", row.get("title_literal", row.get("titulo", "")))),
        "status": row.get("status", row.get("estado_aquisicao", "discovered")),
        "markdown": verify_file(base, path, digest), "raw": verify_file(base, raw, raw_digest),
        "issues": list(issues), "ready_for_import": False,
        "priority": "alta" if row.get("status", row.get("estado_aquisicao")) in ("blocked_partial_acquisition", "ERROR", "error") else "media",
        "review_reason": "Piloto: conferir fonte, fronteiras, notas e metadados antes da incorporação.",
    }


def gather(work):
    records = []
    base = work / "sakharov"
    for key, row in read(base / "inventory.json", {}).get("items", {}).items():
        records.append(candidate("sakharov", key, row, base, path=row.get("candidate"), raw=row.get("raw"),
                                 digest=row.get("markdown_sha256"), raw_digest=row.get("raw_sha256"), issues=row.get("notes", [])))
    base = work / "svitlana"
    for key, row in read(base / "inventory.json", {}).get("candidates", {}).items():
        current = row.get("latest_success", {})
        merged = {**row, **current}
        if not current and row.get("attempts"):
            merged.update(row["attempts"][-1])
        record = candidate("svitlana", key, merged, base, path=current.get("markdown"), raw=current.get("raw"),
                           digest=current.get("markdown_sha256"), raw_digest=current.get("sha256"), issues=current.get("warnings", []))
        record["occurrences"] = row.get("occurrences", [])
        records.append(record)
    base = work / "mozokhin"
    for key, row in read(base / "inventory.json", {}).get("items", {}).items():
        record = candidate("mozokhin", key, row, base, path=row.get("markdown_path"), raw=row.get("raw_path"),
                           digest=row.get("markdown_sha256"), raw_digest=row.get("source_sha256"), issues=row.get("issues", []))
        record["input_kind"] = row.get("input_kind")
        record["fulltext_acquired"] = row.get("fulltext_acquired", False)
        records.append(record)
    base = work / "brest"
    for row in read(base / "inventario.json", []):
        records.append(candidate("brest", row["id"], row, base, path=row.get("candidate_path", row.get("md_path")),
                                 raw=row.get("raw_path"), digest=row.get("checksum_candidato_sha256", row.get("checksum_texto_sha256")),
                                 raw_digest=row.get("checksum_raw_sha256"), issues=row.get("pendencias", []) + ([row["erro"]] if row.get("erro") else [])))
    annotate(records, work)
    return records


def annotate(records, work):
    for finding in read(work / "sakharov/pendencias.json", []):
        for row in records:
            if row["front"] == "sakharov" and (finding.get("source_url") == row["source_url"] or (not finding.get("source_url") and row["language"] == "en" and row["markdown"])):
                row["issues"].append(finding["reason"])
                if finding.get("priority") == "high":
                    row["priority"] = "alta"
    for finding in read(work / "svitlana/review.json", {}).get("document_findings", []):
        for row in records:
            if row["front"] == "svitlana" and finding["candidate_id"] == row["id"]:
                row["issues"].extend(finding.get("notes", []))
                if finding.get("priority") == "high":
                    row["priority"] = "alta"


def reconcile(records, root=ROOT):
    by_url, by_hash = defaultdict(set), defaultdict(set)
    for document in read(root / "data/catalog/documents.json", []):
        for url in urls(document):
            key = normalize_url(url)
            if key:
                by_url[key].add(document["id"])
    for edition in read(root / "data/catalog/editions.json", []):
        if edition.get("sha256"):
            by_hash[edition["sha256"]].add(edition["document_id"])
    for record in records:
        record["catalog_url_matches"] = sorted(by_url.get(normalize_url(record["source_url"]), []))
        record["catalog_text_matches"] = sorted(by_hash.get((record["markdown"] or {}).get("sha256"), []))
        for file in (record["raw"], record["markdown"]):
            if file and (file.get("error") or file.get("hash_matches") is False):
                record["issues"].append("Integridade exige revisão: " + file["path"])
                record["priority"] = "alta"
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path, default=ROOT / "temporario/coletas-quatro")
    args = parser.parse_args()
    # Resumos ficam somente na própria área de trabalho.
    work = args.workdir.resolve()
    records = reconcile(gather(work))
    references = []
    for overlap in read(work / "svitlana/review.json", {}).get("known_overlaps", []):
        reference = candidate("svitlana", "reference:" + overlap["source_url"], overlap, work / "svitlana")
        reference["evidence"] = overlap.get("evidence")
        reference["status"] = "reference_only_requires_textual_match"
        references.extend(reconcile([reference]))
    summaries = {}
    for front in ("sakharov", "svitlana", "mozokhin", "brest"):
        rows = [r for r in records if r["front"] == front]
        summaries[front] = {"inventory_entries": len(rows), "markdown_candidates": sum(bool(r["markdown"]) for r in rows),
                            "statuses": dict(Counter(r["status"] for r in rows)), "ready_for_import": 0}
    output = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
              "mode": "review_only", "summary": summaries, "records": records, "reference_matches": references}
    work.mkdir(parents=True, exist_ok=True)
    path = work / "revisao.json"
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    with (work / "pendencias.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["frente", "id", "estado", "prioridade", "motivo", "url", "markdown", "correspondencias_catalogo"])
        for row in records:
            writer.writerow([row["front"], row["id"], row["status"], row["priority"],
                             " | ".join(row["issues"] or [row["review_reason"]]), row["source_url"],
                             (row["markdown"] or {}).get("path", ""), " | ".join(row["catalog_url_matches"])])
    print(json.dumps(summaries, ensure_ascii=False, indent=2))
    print(f"Prévia consolidada: {path}")


if __name__ == "__main__":
    main()
