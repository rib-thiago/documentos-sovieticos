"""Atualiza apenas o recorte público de incorporações a partir do Git local.

Uso: python3 scripts/update_portal_activity.py
Não altera catálogo, textos ou histórico editorial privado; não publica o site.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "data/manifest.json").read_text(encoding="utf-8"))
    documents = {doc["id"]: doc for doc in manifest.get("documents", [])}
    for collection in manifest["collections"]:
        for doc in collection.get("documents", []):
            documents[doc["id"]] = doc
    files = {edition["file"]: (doc["id"], edition["code"])
             for doc in documents.values() for edition in doc.get("languages", [])}
    history = subprocess.check_output(
        ["git", "log", "-25", "--diff-filter=A", "--format=@@%h|%cI|%s", "--name-only", "--", "originais"],
        cwd=root, text=True, encoding="utf-8")
    groups, current = [], None
    for line in history.splitlines():
        if line.startswith("@@"):
            revision, stamp, summary = line[2:].split("|", 2)
            current = {"commit": revision, "recorded_at": stamp, "summary": summary, "documents": {}}
            groups.append(current)
        elif current is not None and line in files:
            document_id, language = files[line]
            current["documents"].setdefault(document_id, []).append(language)
    events = []
    for group in groups:
        docs = group.pop("documents")
        if not docs:
            continue
        group["document_count"] = len(docs)
        group["version_count"] = sum(len(languages) for languages in docs.values())
        group["examples"] = [{"id": document_id, "languages": languages}
                             for document_id, languages in list(docs.items())[:4]]
        group["source_examples"] = [{"id": document_id, "languages": languages}
                                    for document_id, languages in docs.items() if "ru" in languages][:4]
        events.append(group)
    destination = root / "assets/acervo-activity.json"
    destination.write_text(json.dumps({
        "basis": "Adição de arquivos no histórico Git local; não equivale à data de publicação online.",
        "events": events,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(events)} registros preparados em {destination.relative_to(root)}. Nada foi publicado.")


if __name__ == "__main__":
    main()
