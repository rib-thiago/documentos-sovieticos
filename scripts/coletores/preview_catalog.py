#!/usr/bin/env python3
"""Gera catálogo, manifesto e busca de prévia em área de trabalho; não publica."""
from __future__ import annotations

import argparse
import copy
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from backend import catalog as model
from backend.database import ensure_index
from consolidar import normalize_url, urls

FRONTS = {
    "sakharov": ("sakharov-testamento-lenin-2003", "O testamento político de Lenin — Sakharov (2003)"),
    "svitlana": ("transcricoes-arquivos-sovieticos", "Transcrições dos arquivos soviéticos — Svitlana/Erdogan"),
    "mozokhin": ("politburo-trotsky-mozokhin", "Politburo e Lev Trotsky — edição organizada por Mozokhin"),
    "brest": ("brest-litovsk", "Brest-Litovsk — negociações e debates políticos"),
}
GROUPS = {
    "preliminares": "Preliminares da obra", "parte-1-nep": "Parte I — NEP",
    "parte-2-testamento-fontes": "Parte II — O testamento de Lenin e suas fontes",
    "parte-3-luta-politica": "Parte III — A luta política", "conclusao": "Conclusão",
    "obra-russa": "Obra em russo", "selecao-inglesa": "Seleção em inglês", "apendices": "Apêndices documentais",
    "livro-1-2013": "Livro I — edição de 2013", "livro-2-2013": "Livro II — edição de 2013",
    "01-negociacoes": "Negociações e sessões diplomáticas", "02-comite-central": "Comitê Central — intervenções e decisões",
    "03-lenin": "Lenin — teses, discursos e polêmicas", "04-trotsky": "Trotsky — textos e intervenções",
    "05-comunistas-de-esquerda": "Comunistas de esquerda — imprensa e textos programáticos",
    "06-congressos": "VII Congresso do Partido e IV Congresso dos Sovietes",
    "07-tratados": "Tratados e atos diplomáticos", "08-facsimiles": "Fac-símiles e referências",
    "09-desdobramentos": "Desdobramentos de 1918", "10-interpretacoes": "Reconstituições e historiografia",
}


def reason_text(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def source_file(work, front, value, digest, cache=None):
    if not value or not digest:
        raise ValueError("Arquivo ou hash não informado")
    base = (work / front).resolve()
    value = Path(value)
    path = ROOT / value if value.parts[:2] == ("temporario", "coletas-quatro") else base / value
    path = path.resolve()
    if not path.is_relative_to(base):
        raise ValueError("Caminho fora da frente de coleta")
    stat = path.stat()
    key = (path, stat.st_size, stat.st_mtime_ns)
    cached = cache.get(key) if cache is not None else None
    if cached is None:
        data = path.read_bytes()
        actual = model.sha256(data)
        if cache is not None:
            cache[key] = (data, actual)
    else:
        data, actual = cached
    if actual != digest:
        raise ValueError("Hash divergente: " + str(path))
    return data


def slug(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,179}", value):
        raise ValueError("Identificador inválido: " + repr(value))
    return value


def collection(ident, title, position, parent=None):
    return {"id": ident if parent is None else parent + "/" + ident, "slug": ident, "parent_id": parent,
            "position": position, "titles": {"pt": title}, "subtitle": "Fontes e edições de pesquisa",
            "description": "Textos com fontes preservadas e proveniência registrada. Revisão editorial indicada por documento.",
            "source": {}, "presentation": {"accent": "#982d40"}, "extra": {},
            "compatibility_fields": ["id", "title_pt", "subtitle_pt", "description_pt", "accent", "documents", "subcollections"] if parent is None else ["id", "title_pt", "description_pt", "document_ids"]}


def group_names():
    names = dict(GROUPS)
    with (Path(__file__).parent / "svitlana/fontes.csv").open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            match = re.fullmatch(r"VOL-(\d+)", row["id"])
            title = "Volume " + str(int(match[1])) + " — " + row["years"] if match else row["title"]
            names[row["id"].lower()] = title
    return names


def build(current, work, root=ROOT):
    candidate = copy.deepcopy(current)
    staged, decisions = {}, []
    file_cache = {}
    current_urls, current_hashes = defaultdict(set), defaultdict(set)
    for doc in current["documents"]:
        for url in urls(doc):
            if normalize_url(url):
                current_urls[normalize_url(url)].add(doc["id"])
    for edition in current["editions"]:
        current_hashes[(edition["language"], edition["sha256"])].add(edition["document_id"])
    docs = {d["id"]: d for d in candidate["documents"]}
    editions = {e["id"]: e for e in candidate["editions"]}
    collections = {c["id"]: c for c in candidate["collections"]}
    members = {(m["collection_id"], m["document_id"]) for m in candidate["memberships"]}
    prepared_hashes = defaultdict(set)
    names = group_names()
    for front, (collection_id, collection_title) in FRONTS.items():
        path = work / front / "units.json"
        payload = model.read_json(path) if path.exists() else {"units": []}
        for unit in (payload if isinstance(payload, list) else payload["units"]):
            decision = {"front": front, "unit_id": unit["id"], "status": "blocked", "issues": unit.get("issues", []),
                        "source_url": unit.get("source_url"), "reason": unit.get("reason")}
            decisions.append(decision)
            if unit.get("ready_for_import") is not True:
                continue
            try:
                language = unit["language"]
                if language not in {"ru", "pt", "en"}:
                    raise ValueError("Idioma fora do escopo desta incorporação")
                hashes = unit.get("hashes", {})
                raw_hash = unit.get("raw_sha256", hashes.get("raw_sha256"))
                markdown_hash = unit.get("markdown_sha256", hashes.get("markdown_sha256"))
                source_file(work, front, unit.get("raw"), raw_hash, file_cache)
                data = source_file(work, front, unit.get("markdown"), markdown_hash, file_cache)
                content = data.decode("utf-8")
                if not content.strip() or "BRESTNOTEREFERENCE" in content:
                    raise ValueError("Texto vazio ou marcador de conversão pendente")
                ident = slug(unit.get("document_id", unit["id"]))
                exact = current_hashes.get((language, markdown_hash), set()) or prepared_hashes.get((language, markdown_hash), set())
                url_matches = set(current_urls.get(normalize_url(unit.get("source_url", "")), set()))
                # Uma compilação PDF contém vários documentos. Números impressos
                # distintos, cotejados na mesma fonte por hash, não são duplicatas.
                number = unit.get("provenance", {}).get("printed_document_number")
                if isinstance(number, int):
                    def independent_printed_unit(known_id):
                        known = docs[known_id].get("source_metadata", {})
                        previous = known.get("provenance", {}).get("printed_document_number")
                        return (known.get("collector_front") == front and
                                known.get("source_raw_sha256") == raw_hash and
                                isinstance(previous, int) and previous != number)
                    url_matches = {known_id for known_id in url_matches if not independent_printed_unit(known_id)}
                if len(exact) == 1:
                    ident = next(iter(exact))
                    decision["reuses_existing"] = ident in {d["id"] for d in current["documents"]}
                    decision["reuses_prepared"] = not decision["reuses_existing"]
                elif exact or url_matches:
                    raise ValueError("Correspondência prévia exige conciliação textual: " + ", ".join(sorted(exact or url_matches)))
                edition_id = ident + ":" + language
                if ident in {d["id"] for d in current["documents"]} and not decision.get("reuses_existing"):
                    raise ValueError("ID já cadastrado; nenhuma substituição automática")
                if edition_id in editions and editions[edition_id]["sha256"] != markdown_hash:
                    raise ValueError("Duas versões diferentes para documento/idioma; resolver antes de incorporar")
                groups = unit.get("subcollections") or [unit.get("subcollection", "documentos")]
                groups = [slug(group) for group in dict.fromkeys(groups)]
                literal_title = unit["title_literal"].strip()
                if not literal_title or unit.get("kind", "document") not in {"document", "article"}:
                    raise ValueError("Título ou natureza documental inválidos")
                target = f"originais/coletores/{front}/{slug(ident)}.{language}.md"
                if edition_id not in editions and (root / target).exists():
                    raise ValueError("Arquivo de destino já existe: " + target)
                if ident not in docs:
                    titles = {language: literal_title}
                    if unit.get("title_pt"):
                        titles["pt"] = unit["title_pt"].strip()
                    if not all(titles.values()):
                        raise ValueError("Título vazio")
                    document_type = unit.get("document_type")
                    if document_type not in candidate["vocabularies"]["document_types"]:
                        document_type = None
                    literal_date = unit.get("date_literal")
                    doc = {"id": ident, "kind": unit.get("kind", "document"), "titles": titles,
                           "document_type": document_type, "historical_date": {"display": literal_date, "value": None, "precision": "not_recorded"},
                           "archive_reference": unit.get("archive_reference"), "author_label": unit.get("author_label"),
                           "source": {"name": collection_title, "url": unit["source_url"], "id": unit["id"]},
                           "source_metadata": {"original_language": unit.get("original_language"), "collector_front": front,
                                               "provenance": unit.get("provenance", {}), "unit_id": unit["id"],
                                               "source_raw_sha256": raw_hash, "editorial_issues": unit.get("issues", [])},
                           "default_format": "markdown", "presentation": {}, "extra": {},
                           "compatibility_fields": ["id", "type", "title_pt", "title_ru", "title_en", "date", "archive", "author", "source_name", "source_id", "source_url", "original_language", "document_type", "format", "languages"]}
                    docs[ident] = doc
                    candidate["documents"].append(doc)
                    candidate["provenance"]["manifest_projection"]["global_document_ids"].append(ident)
                elif language not in docs[ident]["titles"] and not decision.get("reuses_existing"):
                    docs[ident]["titles"][language] = unit["title_literal"]
                if edition_id not in editions:
                    edition = {"id": edition_id, "document_id": ident, "language": language,
                               "label": {"ru": "Texto em russo", "pt": "Tradução em português", "en": "Texto em inglês"}[language],
                               "file": target, "format": "markdown", "position": sum(e["document_id"] == ident for e in editions.values()),
                               "sha256": markdown_hash, "bytes": len(data), "editorial_status": "not_recorded",
                               "extra": {"collector_provenance": unit.get("provenance", {})},
                               "compatibility_fields": ["code", "label", "file", "format"]}
                    candidate["editions"].append(edition)
                    editions[edition_id] = edition
                    staged[target] = data
                if collection_id not in collections:
                    item = collection(collection_id, collection_title, sum(c["parent_id"] is None for c in collections.values()))
                    collections[collection_id] = item
                    candidate["collections"].append(item)
                target_collections = [collection_id]
                for group in groups:
                    child_id = collection_id + "/" + group
                    if child_id not in collections:
                        child = collection(group, names.get(group, group.replace("-", " ").capitalize()),
                                           sum(c["parent_id"] == collection_id for c in collections.values()), collection_id)
                        candidate["collections"].append(child)
                        collections[child_id] = child
                    target_collections.append(child_id)
                for target_collection in target_collections:
                    if (target_collection, ident) not in members:
                        candidate["memberships"].append({"collection_id": target_collection, "document_id": ident,
                                                         "position": sum(m["collection_id"] == target_collection for m in candidate["memberships"])})
                        members.add((target_collection, ident))
                decision.update(status="prepared", document_id=ident, edition_id=edition_id, markdown_sha256=markdown_hash)
                prepared_hashes[(language, markdown_hash)].add(ident)
            except (ValueError, OSError, KeyError, TypeError) as error:
                # Falhas de hash/caminho/idioma ocorrem antes de cadastrar a unidade.
                # Conflitos de estrutura posteriores invalidam a prévia inteira na validação.
                decision.update(status="blocked", reason=str(error))
    counts = model.validate(candidate, root, check_manifest=False, content_overrides=staged)
    return candidate, staged, decisions, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path, default=ROOT / "temporario/coletas-quatro")
    parser.add_argument("--build-search", action="store_true", help="Construir SQLite de prévia, sem alterar a busca do site")
    args = parser.parse_args()
    current = model.load(ROOT)
    candidate, files, decisions, counts = build(current, args.workdir)
    for name in model.FILES:
        files[f"data/catalog/{name}.json"] = model.json_bytes(candidate[name])
    files["data/manifest.json"] = model.json_bytes(model.export_manifest(candidate))
    digest = model.sha256(b"\0".join(key.encode() + b"\0" + files[key] for key in sorted(files)))
    package = args.workdir / "preview" / digest
    package.mkdir(parents=True, exist_ok=True)
    for relative, data in files.items():
        target = package / "files" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != data:
            raise ValueError("Prévia imutável divergiu: " + relative)
        if not target.exists():
            target.write_bytes(data)
    summary = {"mode": "preview_only", "package": str(package), "package_sha256": digest,
               "catalog_counts": counts, "new_documents": len(candidate["documents"]) - len(current["documents"]),
               "new_editions": len(candidate["editions"]) - len(current["editions"]),
               "decisions_by_front": {front: dict(Counter(d["status"] for d in decisions if d["front"] == front)) for front in FRONTS},
               "base_catalog_sha256": model.sha256(b"\0".join(model.json_bytes(current[name]) for name in model.FILES)),
               "decisions": decisions}
    if args.build_search:
        ensure_index(ROOT, package / "catalog.sqlite3", candidate, rebuild=False, check_manifest=False,
                     revision=digest, content_overrides=files)
        summary["search_index"] = str(package / "catalog.sqlite3")
    model.atomic_write(package / "preview.json", model.json_bytes(summary))
    model.atomic_write(args.workdir / "preview-latest.json", model.json_bytes(summary))
    with (args.workdir / "unidades-pendencias.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["frente", "unidade", "estado", "documento_previsto", "motivo", "fonte"])
        for decision in decisions:
            reasons = ([decision["reason"]] if decision.get("reason") else []) + decision["issues"]
            writer.writerow([decision["front"], decision["unit_id"], decision["status"], decision.get("document_id", ""),
                             " | ".join(reason_text(reason) for reason in reasons), decision["source_url"]])
    print(json.dumps({key: value for key, value in summary.items() if key != "decisions"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
