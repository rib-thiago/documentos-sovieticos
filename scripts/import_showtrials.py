"""Importa todas as coleções de uma exportação portátil ShowTrials.

Uso: python3 scripts/import_showtrials.py CAMINHO_DO_PACOTE
Preserva IDs, ordem e vínculos; não usa datas WordPress como datas históricas.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# IDs e ordem das subcoleções da fonte; os títulos de navegação são portugueses.
COLLECTIONS = [
    ("centro-de-leningrado", "Processo do Centro de Leningrado", "#51465f", [
        ("858", "investigacao", "Materiais da investigação"),
        ("1293", "andamento", "Andamento do processo"),
        ("860", "piotr-nikolaev", "Caso de Piotr Nikolaev"),
        ("864", "outros-documentos", "Outros documentos"),
    ]),
    ("centro-moscovita", "Processo do Centro Moscovita", "#46576a", [
        ("955", "investigacao", "Materiais da investigação"),
        ("950", "andamento", "Andamento do processo"),
        ("959", "informes", "Informes da Comissão de Controle do Partido e do Instituto de Marxismo-Leninismo"),
        ("957", "outros-documentos", "Outros documentos"),
    ]),
    ("caso-do-kremlin", "Caso do Kremlin", "#655443", [
        ("965", "investigacao", "Materiais da investigação"),
        ("963", "apuracao-partidaria", "Materiais da apuração partidária"),
        ("9401", "sinani-skalov", "Georgi Borisovich Sinani-Skalov"),
        ("967", "outros-documentos", "Outros documentos"),
    ]),
    ("processo-1936", "Processo de 19–23 de agosto de 1936", "#6a4141", [
        ("981", "investigacao", "Materiais da investigação"),
        ("1799", "andamento", "Andamento do processo"),
        ("9048", "olberg", "Valentin Olberg"),
        ("985", "informes", "Informes de referência"),
        ("983", "outros-documentos", "Outros documentos"),
    ]),
    ("processo-1937", "Processo de 23–29 de janeiro de 1937", "#465d50", [
        ("989", "investigacao", "Materiais da investigação"),
        ("987", "andamento", "Andamento do processo"),
        ("991", "outros-documentos", "Outros documentos"),
    ]),
    ("processo-1938", "Processo de 2–12 de março de 1938", "#5c4864", [
        ("8189", "antecedentes", "Antecedentes"),
        ("7488", "investigacao", "Materiais da investigação"),
        ("8261", "bukharin", "Bukharin"),
        ("8927", "pleno-1937", "Pleno de fevereiro–março de 1937"),
        ("7496", "outros-documentos", "Outros documentos"),
    ]),
    ("trotsky", "Trotsky", "#61573e", [("11016", "documentos", "Documentos")]),
    ("artigos-showtrials", "Artigos do ShowTrials", "#3f6063", [("9346", "artigos", "Artigos")]),
    ("documentos-diversos", "Documentos diversos", "#5c5a56", [("975", "documentos", "Documentos diversos")]),
]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def import_collection(source):
    originals = {c["id"]: c for c in read_json(source / "catalogos/colecoes.json")}
    catalog = {d["document_post_id"]: d for d in read_json(source / "catalogos/documentos.json")}
    manifest_path = ROOT / "data/manifest.json"
    manifest = read_json(manifest_path)
    previous = {c["id"]: c for c in manifest["collections"]}
    old_docs = {d["id"]: d for d in manifest.get("documents", [])}
    for collection in manifest["collections"]:
        old_docs.update({d["id"]: d for d in collection.get("documents", [])})
    collections, documents, bodies = [], {}, {}
    for collection_id, title, accent, subcollections in COLLECTIONS:
        old_collection = previous.get(collection_id, {})
        collection = {
            "id": collection_id, "title_pt": title,
            "title_ru": originals[subcollections[0][0]]["processo"],
            "subtitle_pt": "Documentos em russo · Acervo ShowTrials",
            "accent": accent, "subcollections": [], "document_ids": [],
        }
        for field in ("cover", "description_pt"):
            if field in old_collection:
                collection[field] = old_collection[field]
        for source_id, slug, sub_title in subcollections:
            original = originals[source_id]
            sub = {
                "id": slug, "title_pt": sub_title, "title_ru": original["titulo"],
                "source_id": source_id, "source_url": original["url"], "document_ids": [],
            }
            for member in original["documentos"]:
                source_doc = catalog[member["id"]]
                doc_id = "showtrials-" + member["id"]
                sub["document_ids"].append(doc_id)
                if doc_id not in collection["document_ids"]:
                    collection["document_ids"].append(doc_id)
                if doc_id in bodies:
                    continue
                raw = (source / member["arquivo_md"]).read_bytes()
                _, separator, body = raw.partition(b"\n---\n\n")
                if not separator or not body.strip():
                    raise ValueError(f"Cabeçalho ou corpo ausente: {member['arquivo_md']}")
                relative = f"originais/showtrials/{doc_id}.ru.txt"
                destination = ROOT / relative
                if destination.exists() and destination.read_bytes() != body:
                    raise ValueError(f"Texto local diferente da fonte; preserve a revisão antes de importar: {relative}")
                bodies[doc_id] = body
                documents[doc_id] = {
                    "id": doc_id,
                    "type": "article" if source_doc["document_type"] in ("article", "biographical_article") else "document",
                    "title_ru": source_doc["document_title"],
                    "source_id": member["id"], "source_name": "ShowTrials",
                    "source_url": source_doc["document_url"],
                    "document_type": source_doc["document_type"], "format": "text",
                    "languages": [{"code": "ru", "label": "Disponível em russo", "file": relative}],
                }
                # Traduções e metadados editoriais já existentes têm precedência.
                documents[doc_id].update(old_docs.get(doc_id, {}))
            collection["subcollections"].append(sub)
        collections.append(collection)
    assert {d["source_id"] for d in documents.values()} == set(catalog), "Catálogo incompleto"
    assert {s[0] for _, _, _, subs in COLLECTIONS for s in subs} == set(originals) - {"853"}, "Coleção de origem não mapeada"
    # Modifica arquivos somente depois de conferir todas as fontes e textos locais.
    imported_ids = {c["id"] for c in collections}
    manifest["collections"] = [c for c in manifest["collections"] if c["id"] not in imported_ids] + collections
    manifest["documents"] = list(documents.values())
    output = ROOT / "originais/showtrials"
    output.mkdir(parents=True, exist_ok=True)
    for doc_id, body in bodies.items():
        destination = output / f"{doc_id}.ru.txt"
        if not destination.exists():
            destination.write_bytes(body)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(bodies)} documentos; {len(collections)} coleções; {sum(len(c['subcollections']) for c in collections)} subcoleções.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    import_collection(parser.parse_args().source)
