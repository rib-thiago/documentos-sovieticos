#!/usr/bin/env python3
"""Incorpora uma prévia aprovada usando a transação e o histórico editoriais.

Por padrão apenas descreve o plano. --apply grava o acervo local, sem Git ou rede.
"""
from __future__ import annotations

import argparse
import copy
import csv
import io
import json
from pathlib import Path

from preview_catalog import ROOT, FRONTS, model, reason_text
from backend.database import Repository
from backend.editorial import Editorial, QUEUE

REPORT = ROOT / "docs/pesquisa/quatro-coletores"


def load_approved(work, expected_hash, root=ROOT):
    if len(expected_hash) != 64 or any(c not in "0123456789abcdef" for c in expected_hash):
        raise ValueError("Informe o SHA-256 completo da prévia aprovada")
    package = (work / "preview" / expected_hash).resolve()
    if not package.is_relative_to((work / "preview").resolve()):
        raise ValueError("Pacote fora da área de prévia")
    metadata = model.read_json(package / "preview.json")
    if metadata.get("package_sha256") != expected_hash or metadata.get("mode") != "preview_only":
        raise ValueError("Identificação da prévia divergente")
    files = {}
    base = package / "files"
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):
            raise ValueError("Link ou arquivo fora do pacote")
        relative = path.relative_to(base).as_posix()
        allowed = {f"data/catalog/{name}.json" for name in model.FILES} | {"data/manifest.json"}
        if relative not in allowed:
            if not relative.startswith("originais/coletores/") or not relative.endswith(".md"):
                raise ValueError("Arquivo inesperado no pacote: " + relative)
            model.content_path(root, relative, allow_missing=True)
        files[relative] = path.read_bytes()
    digest = model.sha256(b"\0".join(key.encode() + b"\0" + files[key] for key in sorted(files)))
    if digest != expected_hash:
        raise ValueError("O conteúdo da prévia aprovada mudou; nenhuma gravação autorizada")
    candidate = {name: json.loads(files[f"data/catalog/{name}.json"]) for name in model.FILES}
    if json.loads(files["data/manifest.json"]) != model.export_manifest(candidate):
        raise ValueError("Manifesto do pacote diverge do catálogo")
    return metadata, candidate, files


def additions_only(current, candidate):
    additions = {}
    for name in ("documents", "editions", "collections"):
        old = {row["id"]: row for row in current[name]}
        new = {row["id"]: row for row in candidate[name]}
        if any(new.get(ident) != row for ident, row in old.items()):
            raise ValueError("A prévia modifica registros existentes em " + name)
        if candidate[name][:len(current[name])] != current[name]:
            raise ValueError("A prévia reordena registros existentes em " + name)
        additions[name] = [row for row in candidate[name] if row["id"] not in old]
    if candidate["memberships"][:len(current["memberships"])] != current["memberships"]:
        raise ValueError("A prévia remove ou reordena associações existentes")
    if candidate["vocabularies"] != current["vocabularies"]:
        raise ValueError("Este lote não autoriza alterar vocabulários")
    expected_provenance = copy.deepcopy(current["provenance"])
    expected_provenance["manifest_projection"]["global_document_ids"].extend(doc["id"] for doc in additions["documents"])
    if candidate["provenance"] != expected_provenance:
        raise ValueError("Mudança de proveniência fora do lote aprovado")
    return additions


def queue_append(root, current, candidate, metadata, additions):
    path = root / QUEUE
    previous = path.read_bytes().decode("utf-8")
    reader = csv.DictReader(io.StringIO(previous, newline=""))
    fields, existing = reader.fieldnames, list(reader)
    keys = {row["chave"] for row in existing}
    editions = {row["id"]: row for row in candidate["editions"]}
    notes = {}
    for decision in metadata["decisions"]:
        if decision["status"] == "prepared":
            notes.setdefault(decision["document_id"], []).append(decision)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields)
    for doc in additions["documents"]:
        ident = doc["id"]
        decisions = notes[ident]
        front = decisions[0]["front"]
        edition = editions[decisions[0]["edition_id"]]
        reasons = list(dict.fromkeys(reason_text(issue) for decision in decisions for issue in decision.get("issues", [])))
        reason = " | ".join(reasons) or "Conferir fonte preservada, notas, metadados e estrutura da edição de trabalho."
        key = ident + ":coleta_quatro_colecoes"
        if key in keys:
            raise ValueError("Pendência já cadastrada: " + key)
        row = dict.fromkeys(fields, "")
        row.update(chave=key, prioridade="media", dificuldade="media", status="pendente", id=ident,
                   colecoes=FRONTS[front][1], titulo_ru=doc["titles"].get("ru", ""),
                   problema="coleta_quatro_colecoes", dificuldade_encontrada=reason,
                   acao_sugerida="Comparar fonte e Markdown; conferir notas, datas, autoria e tipo documental. Registrar a revisão no histórico editorial.",
                   arquivo_markdown=edition["file"], url_teste="http://localhost:8000/#/doc/" + ident,
                   fonte=decisions[0]["source_url"], trechos="[]",
                   notas_do_revisor="Incluído a partir da prévia aprovada; revisão editorial de trabalho pendente.")
        writer.writerow(row)
    return previous + ("" if previous.endswith("\n") else "\r\n") + stream.getvalue()


def prepare(work, approved_hash, root=ROOT):
    metadata, candidate, bundle = load_approved(work, approved_hash, root)
    current = model.load(root)
    fingerprint = model.sha256(b"\0".join(model.json_bytes(current[name]) for name in model.FILES))
    if fingerprint != metadata["base_catalog_sha256"]:
        raise ValueError("O catálogo mudou desde a aprovação, ou o lote já foi incorporado. Não será substituído.")
    additions = additions_only(current, candidate)
    if (len(additions["documents"]), len(additions["editions"])) != (metadata["new_documents"], metadata["new_editions"]):
        raise ValueError("As contagens da prévia divergem do pacote")
    new_files = {edition["file"] for edition in additions["editions"]}
    if {path for path in bundle if path.startswith("originais/")} != new_files:
        raise ValueError("Conteúdos do pacote não correspondem exatamente às novas edições")
    for path in new_files:
        if (root / path).exists() or (root / path).is_symlink():
            raise ValueError("Destino já existe; edição local preservada: " + path)
    model.validate(current, root)
    model.validate(candidate, root, check_manifest=False, content_overrides=bundle)
    files = {path: data.decode("utf-8") for path, data in bundle.items()
             if path in new_files or path == "data/manifest.json" or
             (path.startswith("data/catalog/") and current[Path(path).stem] != candidate[Path(path).stem])}
    files[QUEUE] = queue_append(root, current, candidate, metadata, additions)
    summary = {"approved_package_sha256": approved_hash, "new_documents": len(additions["documents"]),
               "new_editions": len(additions["editions"]), "new_collections": sum(c["parent_id"] is None for c in additions["collections"]),
               "new_subcollections": sum(c["parent_id"] is not None for c in additions["collections"]),
               "review_queue_added": len(additions["documents"]),
               "retained_units": sum(d["status"] == "blocked" for d in metadata["decisions"]),
               "files_to_write": len(files), "document_ids": [doc["id"] for doc in additions["documents"]]}
    return current, candidate, files, summary, metadata


def write_retained(metadata, prefix=""):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["frente", "unidade", "estado", "motivo", "fonte"])
    for decision in metadata["decisions"]:
        if decision["status"] == "blocked":
            reasons = ([decision["reason"]] if decision.get("reason") else []) + decision.get("issues", [])
            writer.writerow([decision["front"], decision["unit_id"], "retida",
                             " | ".join(reason_text(reason) for reason in reasons), decision["source_url"]])
    model.atomic_write(REPORT / (prefix + "fila-retidas.csv"), stream.getvalue().encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path, default=ROOT / "temporario/coletas-quatro")
    parser.add_argument("--approved-package-sha256", required=True)
    parser.add_argument("--apply", action="store_true", help="Incorporar pelo histórico editorial; backend deve estar encerrado")
    parser.add_argument("--batch-id", default="quatro-colecoes", help="Identificador do lote no histórico")
    parser.add_argument("--report-prefix", default="", help="Prefixo dos comprovantes, preservando os lotes anteriores")
    args = parser.parse_args()
    if any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in args.report_prefix) or not args.batch_id or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in args.batch_id):
        parser.error("Use apenas letras minúsculas, números e hífens no lote e prefixo")
    if not args.apply:
        _, _, _, summary, _ = prepare(args.workdir, args.approved_package_sha256)
        print(json.dumps({key: value for key, value in summary.items() if key != "document_ids"}, ensure_ascii=False, indent=2))
        return
    editorial = Editorial(ROOT)
    try:
        current, candidate, files, summary, metadata = prepare(args.workdir, args.approved_package_sha256)
        print(f"Incorporando {summary['new_documents']} documentos e {summary['new_editions']} versões pelo histórico editorial...", flush=True)
        entity = {"kind": "batch", "id": args.batch_id, "document_ids": summary["document_ids"],
                  "collection_ids": [value[0] for value in FRONTS.values()]}
        preview = editorial.store_preview(editorial.revision(), candidate, files, None,
            [{"field": "Incorporação das quatro coleções — lote aprovado", "before": None,
              "after": {key: value for key, value in summary.items() if key != "document_ids"}}], entity=entity)
        repository = Repository(ROOT, ROOT / ".local/catalog.sqlite3", current, {})
        result = editorial.save(repository, {"preview_id": preview["preview_id"]})
        receipt = {**result, **summary, "active_counts": repository.info,
                   "history_file": ".local/editorial/history/" + result["history_id"] + ".json.gz"}
        model.atomic_write(REPORT / (args.report_prefix + "gravacao.json"), model.json_bytes(receipt))
        write_retained(metadata, args.report_prefix)
        print(json.dumps({key: value for key, value in receipt.items() if key not in {"document_ids", "entity"}}, ensure_ascii=False, indent=2))
    finally:
        editorial.close()


if __name__ == "__main__":
    main()
