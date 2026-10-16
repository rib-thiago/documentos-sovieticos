"""Metadados e importação local de traduções com prévia, histórico e recuperação."""

from __future__ import annotations

import copy
import csv
import fcntl
import gzip
import io
import json
import os
import re
import secrets
import threading
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from . import catalog as model
from .database import INDEX_VERSION, ensure_index
from . import translations

QUEUE = "docs/revisao-markdown/pendencias.csv"
WRITABLE = {"data/catalog/documents.json", "data/catalog/editions.json", "data/catalog/memberships.json", "data/manifest.json", QUEUE}
PRIORITIES = {"urgente": 0, "alta": 1, "media": 2, "baixa": 3}
STATUSES = ("pendente", "em_revisao", "corrigido", "adiado")
ISSUE_FIELDS = ("prioridade", "status", "dificuldade_encontrada", "notas_do_revisor")
DOC_FIELDS = ("titles", "kind", "document_type", "historical_date", "archive_reference", "author_label", "presentation")


class EditorialError(ValueError):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def text(value, limit=4000, nullable=False):
    if value is None and nullable:
        return None
    if not isinstance(value, str) or len(value) > limit or "\0" in value:
        raise EditorialError(f"Texto inválido ou maior que {limit} caracteres")
    return value.strip() or (None if nullable else "")


class Editorial:
    def __init__(self, root):
        self.root = Path(root)
        self.directory = self.root / ".local/editorial"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.history_dir = self.directory / "history"
        self.history_dir.mkdir(exist_ok=True)
        self.process_lock = (self.directory / "server.lock").open("a+")
        try:
            fcntl.flock(self.process_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            self.process_lock.close()
            raise model.CatalogError("Outro backend deste acervo está aberto. Encerre-o antes de iniciar novamente.") from error
        self.lock = threading.RLock()
        self.token = secrets.token_urlsafe(32)
        self.previews = {}
        self.recover_pending()

    def close(self):
        self.process_lock.close()

    def read_queue(self):
        with (self.root / QUEUE).open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            return reader.fieldnames, list(reader)

    def revision(self):
        files = [self.root / "data/catalog" / (name + ".json") for name in model.FILES]
        files.extend([self.root / "data/manifest.json", self.root / QUEUE])
        return model.sha256(b"\0".join(path.read_bytes() for path in files))

    def queue(self, repository, params):
        allowed = {"q", "status", "priority", "collection", "offset", "limit"}
        if set(params) - allowed:
            raise EditorialError("Filtro desconhecido na fila")
        try:
            offset, limit = int(params.get("offset", 0)), int(params.get("limit", 50))
        except (TypeError, ValueError) as error:
            raise EditorialError("Paginação inválida") from error
        if offset < 0 or not 1 <= limit <= 100:
            raise EditorialError("Use offset positivo e limit entre 1 e 100")
        _, rows = self.read_queue()
        docs = {d["id"]: d for d in repository.catalog["documents"]}
        status_counts = dict(Counter(row["status"] for row in rows))
        priority_counts = dict(Counter(row["prioridade"] for row in rows if row["status"] != "corrigido"))
        query = params.get("q", "").strip().casefold()
        collection = params.get("collection")
        members = {m["document_id"] for m in repository.catalog["memberships"] if m["collection_id"] == collection}
        def include(row):
            if params.get("status") and row["status"] != params["status"]:
                return False
            if params.get("priority") and row["prioridade"] != params["priority"]:
                return False
            if collection and row["id"] not in members:
                return False
            doc = docs.get(row["id"], {})
            haystack = " ".join([row["id"], *doc.get("titles", {}).values(), row["problema"], row["dificuldade_encontrada"], row["notas_do_revisor"]]).casefold()
            return not query or query in haystack
        filtered = [row for row in rows if include(row)]
        filtered.sort(key=lambda row: (PRIORITIES.get(row["prioridade"], 9), row["id"], row["chave"]))
        items = [{**row, "titles": docs.get(row["id"], {}).get("titles", {}),
                  "historical_date": docs.get(row["id"], {}).get("historical_date", {}),
                  "collected_date": docs.get(row["id"], {}).get("source_metadata", {}).get("wordpress_date")} for row in filtered[offset:offset + limit]]
        return {"items": items, "total": len(filtered), "offset": offset, "limit": limit,
                "has_more": offset + limit < len(filtered), "status_counts": status_counts, "open_priority_counts": priority_counts}

    def document(self, repository, doc_id):
        # O catálogo em disco pode ter sido alterado externamente: não mistura versões.
        if model.load(self.root) != repository.catalog:
            raise EditorialError("O catálogo mudou fora do backend. Reinicie-o antes de editar.", 409)
        doc = next((d for d in repository.catalog["documents"] if d["id"] == doc_id), None)
        if doc is None:
            raise EditorialError("Documento não encontrado", 404)
        _, rows = self.read_queue()
        return {"document": doc, "collection_ids": [m["collection_id"] for m in repository.catalog["memberships"] if m["document_id"] == doc_id],
                "issues": [row for row in rows if row["id"] == doc_id], "revision": self.revision(),
                "editions": [e for e in repository.catalog["editions"] if e["document_id"] == doc_id]}

    def history(self, document_id=None):
        records = []
        for path in self.history_dir.glob("*.meta.json"):
            entry = model.read_json(path)
            if not document_id or entry["document_id"] == document_id:
                records.append(entry)
        return {"items": sorted(records, key=lambda r: r["id"], reverse=True)[:100]}

    def history_record(self, record_id):
        if not isinstance(record_id, str) or not record_id or any(c not in "0123456789abcdef-" for c in record_id):
            raise EditorialError("Identificador de histórico inválido")
        path = self.history_dir / (record_id + ".json.gz")
        if not path.is_file():
            raise EditorialError("Histórico não encontrado", 404)
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            return json.load(stream)

    def file_state(self, file):
        path = self.root / file
        return path.read_bytes().decode("utf-8") if path.exists() else None

    def allow_file(self, file, translation_files):
        if file in WRITABLE:
            return
        if file not in translation_files or not file.endswith(".md"):
            raise model.CatalogError("Caminho inválido no histórico editorial")
        model.content_path(self.root, file, allow_missing=True)

    def write_states(self, files, translation_files):
        for file, content in files.items():
            self.allow_file(file, translation_files)
            if content is None:
                if file not in translation_files:
                    raise model.CatalogError("Não é permitido remover arquivos do catálogo")
                path = self.root / file
                if path.exists():
                    path.unlink()
            else:
                model.atomic_write(self.root / file, content.encode("utf-8"))

    def recover_pending(self):
        marker = self.directory / "pending.json"
        if not marker.exists():
            return
        record = self.history_record(model.read_json(marker)["id"])
        translation_files = record.get("translation_files", [])
        for file, content in record["before"].items():
            self.allow_file(file, translation_files)
            current = self.file_state(file)
            if current not in {content, record["after"][file]}:
                raise model.CatalogError("Há edição externa durante uma transação interrompida. Preserve .local/editorial e recupere antes de continuar.")
        self.write_states(record["before"], translation_files)
        metadata = {k: record[k] for k in ("id", "created_at", "document_id", "summary", "changes", "restores")}
        metadata["translation_files"] = translation_files
        metadata["state"] = "rolled_back"
        model.atomic_write(self.history_dir / (record["id"] + ".meta.json"), model.json_bytes(metadata))
        marker.unlink()

    def preview(self, repository, payload):
        if not isinstance(payload, dict) or set(payload) - {"revision", "document_id", "document", "collection_ids", "issues", "restore_id"}:
            raise EditorialError("Pedido de prévia inválido")
        revision = self.revision()
        if payload.get("revision") != revision:
            raise EditorialError("O catálogo ou a fila mudou. Reabra o documento e refaça a prévia.", 409)
        if model.load(self.root) != repository.catalog:
            raise EditorialError("O catálogo mudou externamente; reinicie o backend.", 409)
        candidate = copy.deepcopy(repository.catalog)
        fields, rows = self.read_queue()
        changes = []
        files = {}
        restores = payload.get("restore_id")
        if restores:
            record = self.history_record(restores)
            metadata = model.read_json(self.history_dir / (restores + ".meta.json"))
            if metadata["state"] != "committed":
                raise EditorialError("Esta transação não foi concluída e não pode ser restaurada")
            for file, after in record["after"].items():
                self.allow_file(file, record.get("translation_files", []))
                if file=="data/manifest.json" and any(key.startswith("data/catalog/") for key in record["after"]):
                    continue  # Projeção derivada: os arquivos canônicos têm a conferência de conflito.
                # read_bytes preserva CRLF da fila ao comparar o snapshot.
                if self.file_state(file) != after:
                    raise EditorialError("Há alterações posteriores nesses arquivos. Desfaça primeiro a alteração mais recente que os modificou.", 409)
            files = dict(record["before"])
            for file in files:
                self.allow_file(file, record.get("translation_files", []))
            for name in ("documents", "memberships", "editions"):
                file = "data/catalog/" + name + ".json"
                if file in files:
                    candidate[name] = json.loads(files[file])
            if "data/manifest.json" in files:
                files["data/manifest.json"] = model.json_bytes(model.export_manifest(candidate)).decode("utf-8")
            changes = [{"field": change["field"], "before": change["after"], "after": change["before"]} for change in record["changes"]]
            document_id = record["document_id"]
        else:
            document_id = payload.get("document_id")
            doc = next((d for d in candidate["documents"] if d["id"] == document_id), None)
            if doc is None:
                raise EditorialError("Documento não encontrado", 404)
            edits = payload.get("document", {})
            if not isinstance(edits, dict) or set(edits) - set(DOC_FIELDS):
                raise EditorialError("Campo de documento não editável")
            for key, value in edits.items():
                if key == "titles":
                    if not isinstance(value, dict) or set(value) - {"pt", "ru"}:
                        raise EditorialError("Edite apenas os títulos português e russo")
                    merged = dict(doc["titles"])
                    for language, title in value.items():
                        title = text(title, 2000)
                        if title:
                            merged[language] = title
                        else:
                            merged.pop(language, None)
                    value = merged
                elif key == "historical_date":
                    if not isinstance(value, dict) or set(value) != {"display", "value", "precision"}:
                        raise EditorialError("Data histórica inválida")
                    value = {"display": text(value["display"], 500, True), "value": text(value["value"], 20, True), "precision": text(value["precision"], 30)}
                    if (value["value"] is None) != (value["precision"] == "not_recorded"):
                        raise EditorialError("Informe a data ISO e sua precisão juntas, ou deixe a data sem registro")
                elif key == "presentation":
                    if not isinstance(value, dict) or set(value) - {"shortTitle", "eyebrow"}:
                        raise EditorialError("Rótulo editorial inválido")
                    merged = dict(doc["presentation"])
                    for name, content in value.items():
                        content = text(content, 1000, True)
                        if content is None:
                            merged.pop(name, None)
                        else:
                            merged[name] = content
                    value = merged
                else:
                    value = text(value, 4000, key not in {"kind"})
                if value != doc[key]:
                    changes.append({"field": key, "before": doc[key], "after": value})
                    doc[key] = value
            if "collection_ids" in payload:
                selected = payload["collection_ids"]
                collections = {c["id"]: c for c in candidate["collections"]}
                if not isinstance(selected, list) or not selected or any(not isinstance(c, str) or c not in collections for c in selected) or len(selected) != len(set(selected)):
                    raise EditorialError("Selecione ao menos uma coleção válida, sem repetições")
                if any(collections[c]["parent_id"] and collections[c]["parent_id"] not in selected for c in selected):
                    raise EditorialError("Uma subcoleção exige também a coleção principal")
                old = [m["collection_id"] for m in candidate["memberships"] if m["document_id"] == document_id]
                if set(old) != set(selected):
                    members = [m for m in candidate["memberships"] if m["document_id"] != document_id or m["collection_id"] in selected]
                    for collection_id in selected:
                        if collection_id not in old:
                            members.append({"collection_id": collection_id, "document_id": document_id, "position": sum(m["collection_id"] == collection_id for m in members)})
                    for collection_id in collections:
                        group = sorted((m for m in members if m["collection_id"] == collection_id), key=lambda m: m["position"])
                        for position, member in enumerate(group):
                            member["position"] = position
                    candidate["memberships"] = members
                    changes.append({"field": "Coleções/subcoleções", "before": old, "after": selected})
            issue_edits = payload.get("issues", [])
            if not isinstance(issue_edits, list):
                raise EditorialError("Lista de pendências inválida")
            seen = set()
            for edit in issue_edits:
                if not isinstance(edit, dict) or set(edit) != {"chave", *ISSUE_FIELDS} or edit["chave"] in seen:
                    raise EditorialError("Edição de pendência inválida ou repetida")
                seen.add(edit["chave"])
                row = next((r for r in rows if r["chave"] == edit["chave"] and r["id"] == document_id), None)
                if row is None:
                    raise EditorialError("Pendência não pertence a este documento")
                for key in ISSUE_FIELDS:
                    value = text(edit[key], 10000)
                    if key == "prioridade" and value not in PRIORITIES:
                        raise EditorialError("Prioridade inválida")
                    if key == "status" and value not in STATUSES:
                        raise EditorialError("Status inválido")
                    if value != row[key]:
                        changes.append({"field": row["chave"] + " / " + key, "before": row[key], "after": value})
                        row[key] = value
            for name in ("documents", "memberships"):
                if candidate[name] != repository.catalog[name]:
                    files["data/catalog/" + name + ".json"] = model.json_bytes(candidate[name]).decode("utf-8")
            if any(c["field"].startswith(tuple(row["chave"] + " / " for row in rows if row["id"] == document_id)) for c in changes):
                stream = io.StringIO(newline="")
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
                files[QUEUE] = stream.getvalue()
            if any(file.startswith("data/catalog/") for file in files):
                files["data/manifest.json"] = model.json_bytes(model.export_manifest(candidate)).decode("utf-8")
        return self.store_preview(revision, candidate, files, document_id, changes, restores)

    def store_preview(self, revision, candidate, files, document_id, changes, restores=None, translation=None, markdown_edit=None):
        if not files:
            raise EditorialError("Nenhuma alteração para salvar")
        translation_files = [file for file in files if file.startswith("originais/")]
        for file in files:
            self.allow_file(file, translation_files)
        overrides = {file: content.encode("utf-8") if content is not None else None for file, content in files.items() if file in translation_files}
        # Validação operacional da proposta; não escreve nem executa suíte de testes.
        model.validate(candidate, self.root, check_manifest=False, content_overrides=overrides)
        if "data/manifest.json" in files and json.loads(files["data/manifest.json"]) != model.export_manifest(candidate):
            raise EditorialError("O estado histórico não corresponde ao catálogo atual; restauração recusada")
        preview_id = secrets.token_urlsafe(24)
        self.previews = {key: value for key, value in self.previews.items() if value["expires"] > time.time()}
        while len(self.previews) >= 8:
            self.previews.pop(next(iter(self.previews)))
        self.previews[preview_id] = {"revision": revision, "candidate": candidate, "files": files, "document_id": document_id,
            "changes": changes, "restores": restores, "expires": time.time() + 900,
            "translation_files": translation_files, "before": {file: self.file_state(file) for file in files},
            "warnings": [f["message"] for f in translation["findings"] if f["level"] == "warning"] if translation else []}
        file_diffs = [{"file": file, "removed": files[file] is None,
                       "diff": translations.line_diff(self.file_state(file) or "", files[file] or "")} for file in translation_files] if restores else []
        return {"preview_id": preview_id, "changes": changes, "document_id": document_id, "expires_in": 900,
                "updates_index": any(file.startswith("data/catalog/") for file in files), "translation": translation,
                "file_diffs": file_diffs, "requires_acknowledgement": bool(self.previews[preview_id]["warnings"]),
                "changes_content": bool(translation_files), "markdown_edit": markdown_edit}

    def editable_edition(self, repository, edition_id):
        edition = next((e for e in repository.catalog["editions"] if e["id"] == edition_id), None)
        if edition is None:
            raise EditorialError("Versão não encontrada", 404)
        data = self.document(repository, edition["document_id"])
        if edition["format"] != "markdown" or not edition["file"].endswith(".md"):
            raise EditorialError("Esta versão não é Markdown editável. O arquivo TXT permanece preservado.")
        if (self.root / edition["file"]).is_symlink():
            raise EditorialError("A edição não substitui links simbólicos")
        raw = model.content_bytes(self.root, edition["file"])
        if model.sha256(raw) != edition["sha256"]:
            raise EditorialError("O arquivo mudou fora do painel. Confira o cadastro e reinicie o backend antes de editar.", 409)
        return {"document": data["document"], "edition": edition, "revision": data["revision"], "content": raw.decode("utf-8")}

    def preview_markdown(self, repository, payload):
        if not isinstance(payload, dict) or set(payload) != {"revision", "edition_id", "content_sha256", "content"}:
            raise EditorialError("Proposta de edição Markdown inválida")
        data = self.editable_edition(repository, payload["edition_id"])
        edition = data["edition"]
        if payload["revision"] != data["revision"] or payload["content_sha256"] != edition["sha256"]:
            raise EditorialError("A versão mudou. Reabra o editor antes de continuar.", 409)
        content = payload["content"]
        if not isinstance(content, str) or not content.strip("\ufeff \t\r\n") or "\0" in content:
            raise EditorialError("O Markdown está vazio ou contém caracteres inválidos")
        raw = content.encode("utf-8")
        if len(raw) > translations.MAX_TRANSLATION_BYTES:
            raise EditorialError("A versão editada deve ter no máximo 4 MiB", 413)
        if content == data["content"]:
            raise EditorialError("Nenhuma alteração no Markdown para salvar")
        target = model.content_path(self.root, edition["file"])
        if any(e["id"] != edition["id"] and model.content_path(self.root, e["file"]) == target for e in repository.catalog["editions"]):
            raise EditorialError("O arquivo é compartilhado por outra versão; a edição foi recusada para preservá-la")
        model.validate(repository.catalog, self.root)
        candidate = copy.deepcopy(repository.catalog)
        changed = next(e for e in candidate["editions"] if e["id"] == edition["id"])
        changed.update(sha256=model.sha256(raw), bytes=len(raw))
        files = {edition["file"]: content, "data/catalog/editions.json": model.json_bytes(candidate["editions"]).decode("utf-8"),
                 "data/manifest.json": model.json_bytes(model.export_manifest(candidate)).decode("utf-8")}
        changes = [{"field": "Conteúdo Markdown " + edition["language"].upper(),
                    "before": {"file": edition["file"], "sha256": edition["sha256"], "bytes": edition["bytes"]},
                    "after": {"file": edition["file"], "sha256": changed["sha256"], "bytes": changed["bytes"]}}]
        detail = {"edition_id": edition["id"], "language": edition["language"], "file": edition["file"],
                  "content": content, "diff": translations.line_diff(data["content"], content)}
        return self.store_preview(data["revision"], candidate, files, edition["document_id"], changes, markdown_edit=detail)

    def preview_translation(self, repository, payload):
        allowed = {"revision", "document_id", "language", "filename", "content", "title"}
        if not isinstance(payload, dict) or set(payload) != allowed:
            raise EditorialError("Selecione documento, idioma e arquivo para importar")
        revision = self.revision()
        if payload["revision"] != revision or model.load(self.root) != repository.catalog:
            raise EditorialError("O catálogo mudou. Reabra a importação antes de continuar.", 409)
        document_id = payload["document_id"]
        if not isinstance(document_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", document_id):
            raise EditorialError("ID de documento inválido")
        doc = next((d for d in repository.catalog["documents"] if d["id"] == document_id), None)
        if doc is None:
            raise EditorialError("Documento não encontrado", 404)
        editions = sorted((e for e in repository.catalog["editions"] if e["document_id"] == document_id), key=lambda e: e["position"])
        original = next((e for e in editions if e["language"] == "ru"), editions[0])
        language = payload["language"]
        if language not in {"pt", "en"} or language == original["language"]:
            raise EditorialError("Selecione português ou inglês como tradução; o idioma original está protegido")
        filename = text(payload["filename"], 255)
        if not re.search(r"\.(?:md|markdown)$", filename, re.I) or "/" in filename or "\\" in filename:
            raise EditorialError("Envie um arquivo .md ou .markdown")
        content = payload["content"]
        if not isinstance(content, str) or not content.strip("\ufeff \t\r\n") or "\0" in content:
            raise EditorialError("O Markdown está vazio ou contém caracteres inválidos")
        data = content.encode("utf-8")
        if len(data) > translations.MAX_TRANSLATION_BYTES:
            raise EditorialError("O arquivo deve ter no máximo 4 MiB", 413)
        proposed_title = text(payload["title"], 2000)
        # Verifica os arquivos atuais antes de mascarar a tradução substituída com a proposta.
        model.validate(repository.catalog, self.root)
        existing = next((e for e in editions if e["language"] == language), None)
        previous = model.content_bytes(self.root, existing["file"]).decode("utf-8") if existing else ""
        original_content = model.content_bytes(self.root, original["file"]).decode("utf-8")
        candidate = copy.deepcopy(repository.catalog)
        target = existing["file"] if existing and existing["file"].endswith(".md") else translations.markdown_filename(original["file"], document_id, language)
        target_path = model.content_path(self.root, target, allow_missing=True)
        if (self.root / target).is_symlink():
            raise EditorialError("O destino é um link simbólico. A importação não substitui links para preservar o arquivo existente.")
        for edition in repository.catalog["editions"]:
            if (not existing or edition["id"] != existing["id"]) and model.content_path(self.root, edition["file"]) == target_path:
                raise EditorialError("O destino pertence a outra versão; a importação não pode substituí-la")
        if (not existing or target != existing["file"]) and target_path.exists():
            raise EditorialError("Já existe um arquivo não associado nesse destino. Cadastre-o ou mova-o antes de importar.", 409)
        files = {}
        changes = []
        edition = next((e for e in candidate["editions"] if existing and e["id"] == existing["id"]), None)
        if edition is None:
            edition = {"id": document_id + ":" + language, "document_id": document_id, "language": language,
                       "label": "Tradução portuguesa" if language == "pt" else "Tradução inglesa", "file": target,
                       "format": "markdown", "position": len(editions), "sha256": "", "bytes": 0,
                       "editorial_status": "not_recorded", "extra": {}, "compatibility_fields": ["code", "label", "file", "format"]}
            candidate["editions"].append(edition)
        edition.update(file=target, format="markdown", sha256=model.sha256(data), bytes=len(data))
        if existing is None or previous != content or target != existing["file"]:
            files[target] = content
            changes.append({"field": "Tradução " + language.upper(),
                            "before": {"file": existing["file"], "sha256": existing["sha256"], "bytes": existing["bytes"]} if existing else None,
                            "after": {"file": target, "sha256": edition["sha256"], "bytes": len(data)}})
        if proposed_title and proposed_title != doc["titles"].get(language):
            changed_doc = next(d for d in candidate["documents"] if d["id"] == document_id)
            changed_doc["titles"][language] = proposed_title
            changes.append({"field": "Título " + language.upper(), "before": doc["titles"].get(language), "after": proposed_title})
            files["data/catalog/documents.json"] = model.json_bytes(candidate["documents"]).decode("utf-8")
        if candidate["editions"] != repository.catalog["editions"]:
            files["data/catalog/editions.json"] = model.json_bytes(candidate["editions"]).decode("utf-8")
        if files:
            files["data/manifest.json"] = model.json_bytes(model.export_manifest(candidate)).decode("utf-8")
        identity = translations.identification(filename, content)
        diagnostic = {"original": translations.structure(original_content, original["format"]),
                      "current": translations.structure(previous, existing["format"]) if existing else None,
                      "uploaded": translations.structure(content)}
        detail = {"document_id": document_id, "document_title": doc["titles"].get("pt") or doc["titles"].get("ru") or document_id,
                  "language": language, "original_language": original["language"], "target_file": target, "replaces": bool(existing),
                  "identification": identity, "findings": translations.findings(identity, doc, language),
                  "structure": diagnostic, "current_content": previous if existing else None, "content": content,
                  "diff": translations.line_diff(translations.split_export_headers(previous)["body"] if not existing or existing["format"] != "text" else previous,
                                                 translations.split_export_headers(content)["body"])}
        if not files:
            raise EditorialError("O arquivo e o título são iguais aos já cadastrados. Nenhuma alteração para salvar.")
        return self.store_preview(revision, candidate, files, document_id, changes, translation=detail)

    def save(self, repository, payload):
        if not isinstance(payload, dict) or "preview_id" not in payload or set(payload) - {"preview_id", "acknowledge_warnings"}:
            raise EditorialError("Envie apenas o identificador da prévia aprovada")
        plan = self.previews.get(payload["preview_id"])
        if not plan or plan["expires"] <= time.time():
            raise EditorialError("A prévia expirou. Gere uma nova antes de salvar.", 409)
        if plan["revision"] != self.revision():
            raise EditorialError("Houve outra edição desde a prévia. Reabra o documento.", 409)
        if plan["warnings"] and payload.get("acknowledge_warnings") is not True:
            raise EditorialError("Leia as divergências e confirme a associação de documento e idioma antes de salvar")
        if any(self.file_state(file) != content for file, content in plan["before"].items()):
            raise EditorialError("Um arquivo mudou depois da prévia. Reabra a importação ou edição.", 409)
        self.previews.pop(payload["preview_id"])
        record_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f") + "-" + secrets.token_hex(6)
        files = plan["files"]
        before = plan["before"]
        summary = "; ".join(c["field"] for c in plan["changes"])
        metadata = {"id": record_id, "created_at": datetime.now(timezone.utc).isoformat(), "document_id": plan["document_id"],
                    "summary": summary, "changes": plan["changes"], "restores": plan["restores"], "state": "prepared",
                    "translation_files": plan["translation_files"]}
        record = {**metadata, "before": before, "after": files}
        stage = self.directory / (record_id + ".sqlite3")
        info = repository.info
        catalog_changed = any(file.startswith("data/catalog/") for file in files)
        try:
            if catalog_changed:
                chunks = [INDEX_VERSION.encode()]
                for name in model.FILES:
                    file = "data/catalog/" + name + ".json"
                    chunks.append(files[file].encode("utf-8") if file in files else (self.root / file).read_bytes())
                revision = model.sha256(b"\0".join(chunks))
                overrides = {file: files[file].encode("utf-8") if files[file] is not None else None for file in plan["translation_files"]}
                info = ensure_index(self.root, stage, plan["candidate"], rebuild=True, check_manifest=False, revision=revision, content_overrides=overrides)
            if plan["revision"] != self.revision() or any(self.file_state(file) != content for file, content in before.items()):
                raise EditorialError("Um arquivo mudou durante a preparação. Nenhuma alteração foi publicada; reabra a edição.", 409)
            # O histórico fica completo antes da primeira escrita nos arquivos publicados.
            model.atomic_write(self.history_dir / (record_id + ".json.gz"), gzip.compress(model.json_bytes(record)))
            model.atomic_write(self.history_dir / (record_id + ".meta.json"), model.json_bytes(metadata))
            model.atomic_write(self.directory / "pending.json", model.json_bytes({"id": record_id}))
            self.write_states(files, plan["translation_files"])
            if catalog_changed:
                os.replace(stage, repository.path)
            metadata["state"] = "committed"
            model.atomic_write(self.history_dir / (record_id + ".meta.json"), model.json_bytes(metadata))
            (self.directory / "pending.json").unlink()
        except Exception:
            self.recover_pending()
            restored = model.load(self.root)
            repository.catalog = restored
            repository.collections = {c["id"]: c for c in restored["collections"]}
            repository.info = ensure_index(self.root, repository.path, restored)
            raise
        finally:
            if stage.exists():
                stage.unlink()
        repository.catalog = plan["candidate"]
        repository.collections = {c["id"]: c for c in plan["candidate"]["collections"]}
        repository.info = info
        return {"saved": True, "history_id": record_id, "document_id": plan["document_id"], "revision": self.revision(),
                "message": "Alterações salvas. Catálogo, manifesto e busca estão atualizados." if catalog_changed else "Fila de revisão atualizada; os metadados não foram alterados."}
