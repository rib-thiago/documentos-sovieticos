"""Importa o Centro de Leningrado de uma exportação portátil ShowTrials.

Uso: python3 scripts/import_showtrials.py CAMINHO_DO_PACOTE
Preserva IDs, ordem e vínculos; não usa datas WordPress como datas históricas.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION_ID = "centro-de-leningrado"
SUBCOLLECTIONS = [
    ("858", "investigacao", "Materiais da investigação"),
    ("1293", "andamento", "Andamento do processo"),
    ("860", "piotr-nikolaev", "Caso de Piotr Nikolaev"),
    ("864", "outros-documentos", "Outros documentos"),
]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def import_collection(source):
    collections = {c["id"]: c for c in read_json(source / "catalogos/colecoes.json")}
    catalog = {d["document_post_id"]: d for d in read_json(source / "catalogos/documentos.json")}
    collection = {
        "id": COLLECTION_ID,
        "title_pt": "Processo do Centro de Leningrado",
        "title_ru": "Процесс «Ленинградского центра»",
        "subtitle_pt": "Documentos em russo · Acervo ShowTrials",
        "description_pt": "Documentação organizada nas subcoleções do ShowTrials: materiais da investigação, andamento do processo, caso de Piotr Nikolaev e outros documentos.",
        "accent": "#51465f",
        "subcollections": [],
        "documents": [],
    }
    bodies = {}
    for source_id, slug, title in SUBCOLLECTIONS:
        original = collections[source_id]
        sub = {
            "id": slug, "title_pt": title, "title_ru": original["titulo"],
            "source_id": source_id, "source_url": original["url"], "document_ids": [],
        }
        for member in original["documentos"]:
            source_doc = catalog[member["id"]]
            doc_id = "showtrials-" + member["id"]
            sub["document_ids"].append(doc_id)
            if doc_id in bodies:
                continue
            raw = (source / member["arquivo_md"]).read_bytes()
            _, separator, body = raw.partition(b"\n---\n\n")
            if not separator or not body.strip():
                raise ValueError(f"Cabeçalho ou corpo ausente: {member['arquivo_md']}")
            bodies[doc_id] = body
            collection["documents"].append({
                "id": doc_id, "type": "document",
                "title_ru": source_doc["document_title"],
                "source_id": member["id"], "source_name": "ShowTrials",
                "source_url": source_doc["document_url"],
                "document_type": source_doc["document_type"],
                "format": "text",
                "languages": [{"code": "ru", "label": "Disponível em russo", "file": f"originais/showtrials/{doc_id}.ru.txt"}],
            })
        collection["subcollections"].append(sub)

    # Só modifica arquivos depois de conferir todas as fontes de entrada.
    manifest_path = ROOT / "data/manifest.json"
    manifest = read_json(manifest_path)
    existing = next((i for i, c in enumerate(manifest["collections"]) if c["id"] == COLLECTION_ID), None)
    if existing is None:
        manifest["collections"].append(collection)
    else:
        # Uma reimportação preserva a capa adicionada pelo editor.
        if manifest["collections"][existing].get("cover"):
            collection["cover"] = manifest["collections"][existing]["cover"]
        manifest["collections"][existing] = collection
    output = ROOT / "originais/showtrials"
    output.mkdir(parents=True, exist_ok=True)
    for doc_id, body in bodies.items():
        (output / f"{doc_id}.ru.txt").write_bytes(body)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(bodies)} documentos; {len(collection['subcollections'])} subcoleções.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    import_collection(parser.parse_args().source)
