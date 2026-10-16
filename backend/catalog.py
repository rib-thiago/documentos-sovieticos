"""Catálogo versionado, migração reversível e projeção do manifesto estático."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
FILES = ("documents", "editions", "collections", "memberships", "vocabularies", "provenance")
TYPE_LABELS = {
    "administrative_report": "Informe administrativo", "article": "Artigo", "autobiography": "Autobiografia",
    "biographical_article": "Artigo biográfico", "brochure": "Brochura", "confrontation_protocol": "Protocolo de acareação",
    "conversation_recording": "Registro de conversas", "correspondence": "Correspondência", "data_extract": "Extrato de dados",
    "decree_resolution": "Resolução", "draft_project": "Minuta", "explanation": "Esclarecimento",
    "indictment": "Peça de acusação", "interrogation_extract": "Extrato de interrogatório",
    "interrogation_protocol": "Protocolo de interrogatório", "letter": "Carta", "list": "Lista",
    "medical_act": "Laudo médico", "memo_note": "Nota", "plan_instruction": "Plano ou instrução",
    "plea_pardon": "Pedido de clemência", "poem": "Poema", "press_summary": "Relato de imprensa",
    "program": "Programa", "questionnaire_response": "Resposta a questionário", "reference_note": "Informação de referência",
    "search_protocol": "Auto de busca", "session_transcript": "Transcrição de sessão", "special_report": "Comunicação especial",
    "speech": "Discurso", "statement": "Declaração", "summary": "Síntese", "telegram": "Telegrama",
    "testimony": "Depoimento", "verdict_or_sentence": "Sentença",
}
DOC_FIELDS = {"id", "type", "title_pt", "title_ru", "date", "archive", "author", "source_name", "source_id",
              "source_url", "document_type", "format", "shortTitle", "eyebrow", "languages"}
COLLECTION_FIELDS = {"id", "title_pt", "title_ru", "subtitle_pt", "description_pt", "accent", "cover", "source_id",
                     "source_url", "subcollections", "document_ids", "documents"}


class CatalogError(ValueError):
    pass


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    """Publica um arquivo completo; não deixa JSON parcial após interrupção."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="." + path.name, dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def content_path(root, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise CatalogError(f"Caminho inválido: {relative!r}")
    parts = Path(relative).parts
    if Path(relative).is_absolute() or ".." in parts or parts[0] != "originais":
        raise CatalogError(f"Conteúdo deve ficar em originais/: {relative}")
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to((root / "originais").resolve()):
        raise CatalogError(f"Conteúdo fora do acervo: {relative}")
    if not resolved.is_file():
        raise CatalogError(f"Conteúdo ausente: {relative}")
    return resolved


def load(root=ROOT):
    directory = root / "data/catalog"
    try:
        return {name: read_json(directory / (name + ".json")) for name in FILES}
    except (OSError, json.JSONDecodeError) as error:
        raise CatalogError(f"Não foi possível abrir o catálogo: {error}") from error


def ordered_fields(values, fields):
    # Conserva os campos legados e sua ordem sem manter cópias dos valores.
    return {field: values[field] for field in fields}


def metadata_fields(values, fields, exclude=()):
    """Conserva ausências legadas, mas exporta metadados acrescentados depois."""
    return list(fields) + [key for key, value in values.items() if key not in fields and key not in exclude and value is not None]


def export_manifest(catalog):
    editions = defaultdict(list)
    for edition in catalog["editions"]:
        editions[edition["document_id"]].append(edition)
    documents = {}
    for doc in catalog["documents"]:
        languages = []
        for edition in sorted(editions[doc["id"]], key=lambda e: e["position"]):
            values = {"code": edition["language"], "label": edition["label"], "file": edition["file"],
                      "format": edition["format"], **edition["extra"]}
            fields = list(edition["compatibility_fields"])
            if edition["format"] != (doc["default_format"] or "markdown") and "format" not in fields:
                fields.append("format")
            fields.extend(key for key in edition["extra"] if key not in fields)
            languages.append(ordered_fields(values, fields))
        values = {"id": doc["id"], "type": doc["kind"], "title_pt": doc["titles"].get("pt"),
                  "title_ru": doc["titles"].get("ru"), "date": doc["historical_date"].get("display") or doc["historical_date"].get("value"),
                  "archive": doc["archive_reference"], "author": doc["author_label"],
                  "source_name": doc["source"].get("name"), "source_id": doc["source"].get("id"),
                  "source_url": doc["source"].get("url"), "document_type": doc["document_type"],
                  "format": doc["default_format"], "shortTitle": doc["presentation"].get("shortTitle"),
                  "eyebrow": doc["presentation"].get("eyebrow"), "languages": languages, **doc["extra"]}
        documents[doc["id"]] = ordered_fields(values, metadata_fields(values, doc["compatibility_fields"]))
    members = defaultdict(list)
    for member in sorted(catalog["memberships"], key=lambda m: (m["collection_id"], m["position"])):
        members[member["collection_id"]].append(member["document_id"])
    children = defaultdict(list)
    for collection in catalog["collections"]:
        children[collection["parent_id"]].append(collection)

    def collection_view(collection):
        ids = members[collection["id"]]
        values = {"id": collection["slug"], "title_pt": collection["titles"].get("pt"),
                  "title_ru": collection["titles"].get("ru"), "subtitle_pt": collection["subtitle"],
                  "description_pt": collection["description"], "accent": collection["presentation"].get("accent"),
                  "cover": collection["presentation"].get("cover"), "source_id": collection["source"].get("id"),
                  "source_url": collection["source"].get("url"), "document_ids": ids,
                  "documents": [documents[doc_id] for doc_id in ids],
                  "subcollections": [collection_view(c) for c in sorted(children[collection["id"]], key=lambda c: c["position"])],
                  **collection["extra"]}
        return ordered_fields(values, metadata_fields(values, collection["compatibility_fields"], {"documents", "document_ids", "subcollections"}))

    global_ids = catalog["provenance"]["manifest_projection"]["global_document_ids"]
    values = {"collections": [collection_view(c) for c in sorted(children[None], key=lambda c: c["position"])],
              "documents": [documents[doc_id] for doc_id in global_ids]}
    return ordered_fields(values, catalog["provenance"]["manifest_projection"]["fields"])


def validate(catalog, root=ROOT, check_files=True, check_manifest=True):
    try:
        return _validate(catalog, root, check_files, check_manifest)
    except (KeyError, TypeError, AttributeError) as error:
        raise CatalogError(f"Estrutura inválida no catálogo; confira o campo/valor {error}") from error


def _validate(catalog, root, check_files, check_manifest):
    if catalog["provenance"].get("schema_version") != SCHEMA_VERSION:
        raise CatalogError("Versão de catálogo não suportada")
    maps = {}
    for name in ("documents", "editions", "collections"):
        records = catalog[name]
        maps[name] = {r["id"]: r for r in records}
        if len(maps[name]) != len(records):
            raise CatalogError(f"IDs repetidos em {name}")
    docs, editions, collections = (maps[k] for k in ("documents", "editions", "collections"))
    allowed_types = set(catalog["vocabularies"]["document_types"])
    edition_pairs = set()
    positions = defaultdict(list)
    for edition in editions.values():
        if edition["document_id"] not in docs or edition["format"] not in {"markdown", "text"}:
            raise CatalogError(f"Edição inválida: {edition['id']}")
        if not re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z0-9]+)*", edition["language"]):
            raise CatalogError(f"Idioma inválido: {edition['id']}")
        pair = (edition["document_id"], edition["language"])
        if pair in edition_pairs:
            raise CatalogError(f"Idioma repetido: {pair}")
        edition_pairs.add(pair)
        if edition["id"] != edition["document_id"] + ":" + edition["language"]:
            raise CatalogError(f"ID de edição incompatível com documento/idioma: {edition['id']}")
        if set(edition["extra"]) & {"code", "label", "file", "format"}:
            raise CatalogError(f"Campo de edição duplicado em extra: {edition['id']}")
        positions[edition["document_id"]].append(edition["position"])
        path = content_path(root, edition["file"])
        if check_files and sha256(path.read_bytes()) != edition["sha256"]:
            raise CatalogError(f"Arquivo mudou: {edition['file']}. Confira a edição e execute refresh-files --write para registrar o novo hash.")
    for doc in docs.values():
        if doc["kind"] not in {"document", "article"} or not any(doc["titles"].values()):
            raise CatalogError(f"Documento inválido: {doc['id']}")
        if doc["document_type"] is not None and doc["document_type"] not in allowed_types:
            raise CatalogError(f"Tipo sem vocabulário: {doc['id']}")
        if set(doc["extra"]) & DOC_FIELDS:
            raise CatalogError(f"Campo documental duplicado em extra: {doc['id']}")
        if not all(isinstance(value, str) and value.strip() for value in doc["titles"].values()):
            raise CatalogError(f"Títulos inválidos: {doc['id']}")
        historical = doc["historical_date"]
        if historical["precision"] not in {"not_recorded", "day", "month", "year"}:
            raise CatalogError(f"Precisão de data inválida: {doc['id']}")
        value = historical["value"]
        if value is not None:
            try:
                precision = historical["precision"]
                if precision == "day" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                    date.fromisoformat(value)
                elif precision == "month" and re.fullmatch(r"\d{4}-\d{2}", value):
                    date.fromisoformat(value + "-01")
                elif precision == "year" and re.fullmatch(r"\d{4}", value):
                    date.fromisoformat(value + "-01-01")
                else:
                    raise ValueError("formato/precisão incompatíveis")
            except (ValueError, TypeError) as error:
                raise CatalogError(f"Data histórica ISO inválida: {doc['id']}") from error
        if not positions[doc["id"]] or sorted(positions[doc["id"]]) != list(range(len(positions[doc["id"]]))):
            raise CatalogError(f"Ordem/edições inválidas: {doc['id']}")
    sibling_positions = defaultdict(list)
    for collection in collections.values():
        parent = collection["parent_id"]
        if parent is not None and (parent not in collections or collections[parent]["parent_id"] is not None):
            raise CatalogError(f"Hierarquia inválida: {collection['id']}")
        expected_id = collection["slug"] if parent is None else parent + "/" + collection["slug"]
        if collection["id"] != expected_id:
            raise CatalogError(f"ID de coleção incompatível com slug/pai: {collection['id']}")
        if set(collection["extra"]) & COLLECTION_FIELDS:
            raise CatalogError(f"Campo de coleção duplicado em extra: {collection['id']}")
        sibling_positions[parent].append(collection["position"])
    for positions_list in sibling_positions.values():
        if sorted(positions_list) != list(range(len(positions_list))):
            raise CatalogError("Ordem de coleções inválida")
    member_positions = defaultdict(list)
    connected = set()
    for membership in catalog["memberships"]:
        if membership["document_id"] not in docs or membership["collection_id"] not in collections:
            raise CatalogError(f"Associação órfã: {membership}")
        member_positions[membership["collection_id"]].append(membership["position"])
        connected.add(membership["document_id"])
    if connected != set(docs):
        raise CatalogError("Há documentos sem coleção")
    for position_list in member_positions.values():
        if sorted(position_list) != list(range(len(position_list))):
            raise CatalogError("Ordem de documentos inválida")
    member_ids = defaultdict(set)
    for membership in catalog["memberships"]:
        member_ids[membership["collection_id"]].add(membership["document_id"])
    for collection in collections.values():
        if collection["parent_id"] and not member_ids[collection["id"]].issubset(member_ids[collection["parent_id"]]):
            raise CatalogError(f"Subcoleção contém documento ausente na coleção principal: {collection['id']}")
    try:
        projection = export_manifest(catalog)
    except (KeyError, RecursionError) as error:
        raise CatalogError(f"Projeção incompatível: {error}") from error
    if check_manifest and projection != read_json(root / "data/manifest.json"):
        raise CatalogError("Manifesto desatualizado em relação ao catálogo. Execute python3 -m backend.catalog export.")
    return {"documents": len(docs), "editions": len(editions), "collections": sum(c["parent_id"] is None for c in collections.values()),
            "subcollections": sum(c["parent_id"] is not None for c in collections.values()), "memberships": len(catalog["memberships"])}


def source_tables(package):
    if package is None:
        return {}, {}, []
    directory = package / "original/data/c-catalog-taxonomy"
    tables, evidence = [], []
    for name in ("showtrials_master_catalog.tsv", "showtrials_document_types_v4.tsv"):
        path = directory / name
        with path.open(encoding="utf-8", newline="") as file:
            rows = list(csv.DictReader(file, delimiter="\t"))
        by_id = {row["document_post_id"]: row for row in rows}
        if len(by_id) != len(rows):
            raise CatalogError(f"IDs repetidos na fonte {name}")
        tables.append(by_id)
        evidence.append({"file": "original/data/c-catalog-taxonomy/" + name, "sha256": sha256(path.read_bytes()), "rows": len(rows)})
    return *tables, evidence


def migrate(root=ROOT, package=None):
    directory = root / "data/catalog"
    if directory.exists():
        raise CatalogError("O catálogo já existe; a migração não sobrescreve metadados")
    manifest_path = root / "data/manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    source, types, evidence = source_tables(package)
    documents, editions, collections, memberships = [], [], [], []
    seen = {}

    def add_document(original):
        if original["id"] in seen:
            if seen[original["id"]] != original:
                raise CatalogError(f"Cadastro conflitante: {original['id']}")
            return
        seen[original["id"]] = original
        sid = original.get("source_id")
        inherited = source.get(sid, {})
        classification = types.get(sid, {})
        if classification and classification["document_type"] != original.get("document_type"):
            raise CatalogError(f"Classificação diferente da fonte: {original['id']}")
        doc = {"id": original["id"], "kind": original["type"],
               "titles": {language: original["title_" + language] for language in ("pt", "ru") if "title_" + language in original},
               "document_type": original.get("document_type"),
               "historical_date": {"display": original.get("date"), "value": None, "precision": "not_recorded"},
               "archive_reference": original.get("archive"), "author_label": original.get("author"),
               "source": {key: original["source_" + key] for key in ("name", "id", "url") if "source_" + key in original},
               "source_metadata": {"wordpress_date": inherited.get("document_date"), "wordpress_modified": inherited.get("document_modified"),
                   "wordpress_author_id": inherited.get("wp_author"),
                   "categories": [s.strip() for s in inherited.get("category_names", "").split("|") if s.strip()],
                   "tags": [s.strip() for s in inherited.get("tag_names", "").split("|") if s.strip()],
                   "classification": {"method": classification.get("reason"),
                       "matched_types": [s.strip() for s in classification.get("matched_types", "").split("|") if s.strip()]}},
               "default_format": original.get("format"),
               "presentation": {key: original[key] for key in ("shortTitle", "eyebrow") if key in original},
               "extra": {key: value for key, value in original.items() if key not in DOC_FIELDS},
               "compatibility_fields": list(original)}
        documents.append(doc)
        for position, language in enumerate(original["languages"]):
            path = content_path(root, language["file"])
            data = path.read_bytes()
            editions.append({"id": original["id"] + ":" + language["code"], "document_id": original["id"],
                "language": language["code"], "label": language["label"], "file": language["file"],
                "format": language.get("format", original.get("format", "markdown")), "position": position,
                "sha256": sha256(data), "bytes": len(data), "editorial_status": "not_recorded",
                "extra": {key: value for key, value in language.items() if key not in {"code", "label", "file", "format"}},
                "compatibility_fields": list(language)})

    def add_collection(original, position, parent=None):
        collection_id = original["id"] if parent is None else parent + "/" + original["id"]
        collections.append({"id": collection_id, "slug": original["id"], "parent_id": parent, "position": position,
            "titles": {language: original["title_" + language] for language in ("pt", "ru") if "title_" + language in original},
            "subtitle": original.get("subtitle_pt"), "description": original.get("description_pt"),
            "source": {key: original["source_" + key] for key in ("id", "url") if "source_" + key in original},
            "presentation": {key: original[key] for key in ("accent", "cover") if key in original},
            "extra": {key: value for key, value in original.items() if key not in COLLECTION_FIELDS},
            "compatibility_fields": list(original)})
        embedded = original.get("documents", [])
        for doc in embedded:
            add_document(doc)
        ids = original.get("document_ids", [doc["id"] for doc in embedded])
        memberships.extend({"collection_id": collection_id, "document_id": doc_id, "position": i} for i, doc_id in enumerate(ids))
        for i, sub in enumerate(original.get("subcollections", [])):
            add_collection(sub, i, collection_id)

    for doc in manifest.get("documents", []):
        add_document(doc)
    for i, collection in enumerate(manifest["collections"]):
        add_collection(collection, i)
    catalog = {"documents": documents, "editions": editions, "collections": collections, "memberships": memberships,
        "vocabularies": {"document_types": TYPE_LABELS, "kinds": {"document": "Documento", "article": "Artigo"},
            "languages": {"ru": "Russo", "pt": "Português", "en": "Inglês"}},
        "provenance": {"schema_version": SCHEMA_VERSION, "migration": "manifest-v1", "manifest_sha256": sha256(manifest_bytes),
            "manifest_projection": {"fields": list(manifest), "global_document_ids": [d["id"] for d in manifest.get("documents", [])]},
            "source_tables": evidence,
            "decisions": ["Datas WordPress não são datas históricas", "Ausência de dado não é inferida do título",
                          "Coleções não definem a identidade histórica de uma pessoa", "Relações documentais não são deduplicadas por semelhança de texto"]}}
    counts = validate(catalog, root)
    if export_manifest(catalog) != manifest:
        raise CatalogError("A migração alteraria a projeção do site")
    # Diretório publicado de uma só vez depois da validação completa.
    staging = Path(tempfile.mkdtemp(prefix=".catalog-", dir=root / "data"))
    try:
        for name in FILES:
            (staging / (name + ".json")).write_bytes(json_bytes(catalog[name]))
        os.replace(staging, directory)
    finally:
        if staging.exists():
            for path in staging.iterdir():
                path.unlink()
            staging.rmdir()
    return counts


def refresh_files(root=ROOT, write=False):
    catalog = load(root)
    validate(catalog, root, check_files=False)
    changes = []
    for edition in catalog["editions"]:
        data = content_path(root, edition["file"]).read_bytes()
        new_hash = sha256(data)
        if new_hash != edition["sha256"]:
            changes.append({"edition": edition["id"], "file": edition["file"], "old_sha256": edition["sha256"], "new_sha256": new_hash})
            edition.update(sha256=new_hash, bytes=len(data))
    if write and changes:
        atomic_write(root / "data/catalog/editions.json", json_bytes(catalog["editions"]))
    return {"written": bool(write and changes), "changes": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    migration = sub.add_parser("migrate")
    migration.add_argument("--source", type=Path)
    sub.add_parser("check")
    export = sub.add_parser("export")
    export.add_argument("--check", action="store_true", help="Confere sem escrever")
    refresh = sub.add_parser("refresh-files")
    refresh.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "migrate":
            result = migrate(package=args.source)
        elif args.command == "refresh-files":
            result = refresh_files(write=args.write)
        else:
            catalog = load()
            result = validate(catalog, check_manifest=args.command != "export" or args.check)
            if args.command == "export" and not args.check:
                atomic_write(ROOT / "data/manifest.json", json_bytes(export_manifest(catalog)))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (CatalogError, OSError) as error:
        parser.exit(1, f"Erro: {error}\n")


if __name__ == "__main__":
    main()
