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
from urllib.parse import urlsplit
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from . import catalog as model
from .database import INDEX_VERSION, ensure_index
from . import translations

QUEUE = "docs/revisao-markdown/pendencias.csv"
WRITABLE = {"data/catalog/documents.json", "data/catalog/editions.json", "data/catalog/memberships.json", "data/catalog/collections.json", "data/catalog/provenance.json", "data/manifest.json", QUEUE}
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
            if not document_id or entry["document_id"] == document_id or (entry.get("entity") or {}).get("id") == document_id or document_id in (entry.get("entity") or {}).get("document_ids", []):
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
        if file not in translation_files or not file.endswith((".md", ".txt")):
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
        metadata["entity"] = record.get("entity", {"kind": "document", "id": record["document_id"]})
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
            for name in model.FILES:
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
                    if not isinstance(value, dict) or set(value) - {"pt", "ru", "en"}:
                        raise EditorialError("Edite apenas os títulos português, russo e inglês")
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
        return self.store_preview(revision, candidate, files, document_id, changes, restores, entity=record.get("entity") if restores else None)

    def store_preview(self, revision, candidate, files, document_id, changes, restores=None, translation=None, markdown_edit=None, entity=None, creation=None):
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
            "warnings": [f["message"] for f in translation["findings"] if f["level"] == "warning"] if translation else [],
            "entity": entity or {"kind": "document", "id": document_id}, "creation": creation}
        file_diffs = [{"file": file, "removed": files[file] is None,
                       "diff": translations.line_diff(self.file_state(file) or "", files[file] or "")} for file in translation_files] if restores else []
        if creation:
            self.previews[preview_id]["warnings"] = creation.get("warnings", [])
        return {"preview_id": preview_id, "changes": changes, "document_id": document_id, "expires_in": 900,
                "updates_index": any(file.startswith("data/catalog/") for file in files), "translation": translation,
                "file_diffs": file_diffs, "requires_acknowledgement": bool(self.previews[preview_id]["warnings"]),
                "changes_content": bool(translation_files), "markdown_edit": markdown_edit,
                "entity": self.previews[preview_id]["entity"], "creation": creation}

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

    def preview_markdown(self, repository, payload, change_label=None):
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
        changes = [{"field": change_label or "Conteúdo Markdown " + edition["language"].upper(),
                    "before": {"file": edition["file"], "sha256": edition["sha256"], "bytes": edition["bytes"]},
                    "after": {"file": edition["file"], "sha256": changed["sha256"], "bytes": changed["bytes"]}}]
        detail = {"edition_id": edition["id"], "language": edition["language"], "file": edition["file"],
                  "content": content, "diff": translations.line_diff(data["content"], content)}
        return self.store_preview(data["revision"], candidate, files, edition["document_id"], changes, markdown_edit=detail)

    def preview_passage(self, repository, payload):
        required = {"revision", "edition_id", "content_sha256", "start", "end", "expected", "replacement"}
        if not isinstance(payload, dict) or set(payload) != required:
            raise EditorialError("Proposta de correção de trecho inválida")
        data = self.editable_edition(repository, payload["edition_id"])
        edition = data["edition"]
        editions = [item for item in repository.catalog["editions"] if item["document_id"] == edition["document_id"]]
        original = next((item for item in editions if item["language"] == data["document"]["source_metadata"].get("original_language", "ru")), editions[0])
        if edition["language"] not in {"pt", "en"} or edition["id"] == original["id"]:
            raise EditorialError("A correção de trechos aceita apenas traduções; o original está protegido")
        if payload["revision"] != data["revision"] or payload["content_sha256"] != edition["sha256"]:
            raise EditorialError("A tradução mudou. Recarregue o documento antes de corrigir o trecho.", 409)
        body = translations.split_export_headers(data["content"])["body"]
        start, end = payload["start"], payload["end"]
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(body):
            raise EditorialError("Não foi possível identificar o trecho na tradução")
        expected, replacement = payload["expected"], payload["replacement"]
        if not isinstance(expected, str) or body[start:end] != expected:
            raise EditorialError("O trecho mudou ou não corresponde ao arquivo. Recarregue o documento.", 409)
        if not isinstance(replacement, str) or not replacement.strip() or "\0" in replacement:
            raise EditorialError("A correção deve conter texto válido")
        if len(replacement.encode("utf-8")) > 200000:
            raise EditorialError("Correção extensa demais. Use o editor Markdown completo.", 413)
        prefix = data["content"][:len(data["content"]) - len(body)]
        content = prefix + body[:start] + replacement + body[end:]
        result = self.preview_markdown(repository, {
            "revision": data["revision"], "edition_id": edition["id"],
            "content_sha256": edition["sha256"], "content": content,
        }, change_label="Correção de trecho " + edition["language"].upper())
        result.pop("markdown_edit", None)
        result["passage_edit"] = {"language": edition["language"], "before": expected, "after": replacement,
                                 "diff": translations.line_diff(expected, replacement)}
        return result

    def require_current(self, repository, revision):
        if revision != self.revision() or model.load(self.root) != repository.catalog:
            raise EditorialError("O catálogo mudou. Reabra o formulário e refaça a prévia.", 409)

    def collection(self, repository, collection_id):
        self.require_current(repository, self.revision())
        collection = repository.collections.get(collection_id)
        if collection is None:
            raise EditorialError("Coleção não encontrada", 404)
        return {"collection": collection, "revision": self.revision()}

    @staticmethod
    def identifier(value):
        value = text(value, 100)
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
            raise EditorialError("Use um identificador com letras minúsculas sem acentos, números e hífens")
        return value

    @staticmethod
    def source_url(value):
        value = text(value, 2000, True)
        if value:
            parsed = urlsplit(value)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
                raise EditorialError("Informe uma URL de fonte HTTP ou HTTPS válida")
        return value

    def creation_files(self, repository, candidate, content=None):
        files = {"data/catalog/" + name + ".json": model.json_bytes(candidate[name]).decode("utf-8")
                 for name in model.FILES if candidate[name] != repository.catalog[name]}
        files["data/manifest.json"] = model.json_bytes(model.export_manifest(candidate)).decode("utf-8")
        if content:
            files.update(content)
        return files

    def preview_document_creation(self, repository, payload, *, _defer=False, _queue_fields=None):
        allowed = {"revision", "id", "title", "title_pt", "language", "kind", "document_type", "date", "author", "archive", "source_name", "source_url", "source_id", "collection_ids", "filename", "content"}
        if not isinstance(payload, dict) or set(payload) != allowed:
            raise EditorialError("Cadastro de documento inválido")
        if not _defer:
            self.require_current(repository, payload["revision"])
        document_id = self.identifier(payload["id"])
        if any(doc["id"] == document_id for doc in repository.catalog["documents"]):
            raise EditorialError("Este ID já pertence a um documento. Abra-o no catálogo para editar ou importar uma tradução.", 409)
        language = payload["language"]
        if language not in {"ru", "pt", "en"}:
            raise EditorialError("Selecione o idioma original: russo, português ou inglês")
        title = text(payload["title"], 2000)
        if not title:
            raise EditorialError("Informe o título no idioma original")
        filename = text(payload["filename"], 255)
        extension = Path(filename).suffix.lower()
        if extension not in {".md", ".markdown", ".txt"}:
            raise EditorialError("Selecione um arquivo Markdown ou TXT em UTF-8")
        content = payload["content"]
        if not isinstance(content, str) or not content.strip("\ufeff \t\r\n") or "\0" in content:
            raise EditorialError("O arquivo está vazio ou contém caracteres inválidos")
        raw = content.encode("utf-8")
        if len(raw) > translations.MAX_TRANSLATION_BYTES:
            raise EditorialError("O arquivo deve ter no máximo 4 MiB", 413)
        selected = payload["collection_ids"]
        collections = repository.collections
        if not isinstance(selected, list) or not selected or any(not isinstance(item, str) or item not in collections for item in selected):
            raise EditorialError("Selecione ao menos uma coleção ou subcoleção válida")
        selected = set(selected)
        selected.update(collections[item]["parent_id"] for item in list(selected) if collections[item]["parent_id"])
        kind = text(payload["kind"], 30)
        document_type = text(payload["document_type"], 100, True)
        if kind not in {"document", "article"} or document_type and document_type not in repository.catalog["vocabularies"]["document_types"]:
            raise EditorialError("Categoria ou tipo documental inválido")
        target = f"originais/locais/{document_id}.{language}." + ("txt" if extension == ".txt" else "md")
        path = model.content_path(self.root, target, allow_missing=True)
        if path.exists() or (self.root / target).is_symlink():
            raise EditorialError("Já existe um arquivo no destino. Ele não será substituído.", 409)
        source_id = text(payload["source_id"], 500, True)
        source_url = self.source_url(payload["source_url"])
        titles = {language: title}
        title_pt = text(payload["title_pt"], 2000)
        if title_pt and language != "pt":
            titles["pt"] = title_pt
        doc = {"id": document_id, "kind": kind, "titles": titles, "document_type": document_type,
               "historical_date": {"display": text(payload["date"], 500, True), "value": None, "precision": "not_recorded"},
               "archive_reference": text(payload["archive"], 4000, True), "author_label": text(payload["author"], 4000, True),
               "source": {"name": text(payload["source_name"], 500, True), "id": source_id, "url": source_url},
               "source_metadata": {"original_language": language, "imported_filename": filename},
               "default_format": "text" if extension == ".txt" else "markdown", "presentation": {}, "extra": {},
               "compatibility_fields": ["id", "type", "languages"]}
        label = {"ru": "Texto em russo", "pt": "Texto em português", "en": "Texto em inglês"}[language]
        edition = {"id": document_id + ":" + language, "document_id": document_id, "language": language, "label": label,
                   "file": target, "format": doc["default_format"], "position": 0, "sha256": model.sha256(raw), "bytes": len(raw),
                   "editorial_status": "not_recorded", "extra": {}, "compatibility_fields": ["code", "label", "file", "format"]}
        candidate = repository.catalog if _defer else copy.deepcopy(repository.catalog)
        if not _defer:
            candidate["documents"].append(doc)
            candidate["editions"].append(edition)
            candidate["provenance"]["manifest_projection"]["global_document_ids"].append(document_id)
            for collection in candidate["collections"]:
                if collection["id"] in selected:
                    position = sum(member["collection_id"] == collection["id"] for member in candidate["memberships"])
                    candidate["memberships"].append({"collection_id": collection["id"], "document_id": document_id, "position": position})
        duplicates = []
        normalized_titles = {value.casefold() for value in titles.values()}
        duplicate_content_ids = {item["document_id"] for item in repository.catalog["editions"] if item["sha256"] == edition["sha256"]}
        for existing in repository.catalog["documents"]:
            same_source = bool(source_url and existing["source"].get("url") and translations.normalized_url(source_url) == translations.normalized_url(existing["source"]["url"]))
            same_title = any(value.casefold() in normalized_titles for value in existing["titles"].values())
            same_bytes = existing["id"] in duplicate_content_ids
            if same_source or same_title or same_bytes:
                duplicates.append(existing["id"])
        findings = translations.findings(translations.identification(filename, content), doc, language)
        warnings = [item["message"] for item in findings if item["level"] == "warning"]
        if duplicates:
            warnings.append("Confira possíveis duplicidades (título, fonte ou arquivo): " + ", ".join(duplicates[:15]))
        detail = {"kind": "document", "id": document_id, "file": target, "language": language, "format": edition["format"],
                  "content": content, "warnings": warnings, "collections": sorted(selected)}
        changes = [{"field": "Novo documento", "before": None, "after": doc},
                   {"field": "Arquivo original", "before": None, "after": {"file": target, "language": language, "bytes": len(raw)}},
                   {"field": "Coleções", "before": None, "after": sorted(selected)}]
        files = None if _defer else self.creation_files(repository, candidate, {target: content})
        queue_fields, queue_rows = (_queue_fields, []) if _defer else self.read_queue()
        new_row = {field: "" for field in queue_fields}
        new_row.update(chave=document_id + ":cadastro_local", prioridade="media", dificuldade="baixa", status="pendente", id=document_id,
                       colecoes=" / ".join(collection["titles"].get("pt", collection["id"]) for collection in candidate["collections"] if collection["id"] in selected),
                       titulo_ru=titles.get("ru", ""), problema="cadastro_local", dificuldade_encontrada="Documento novo: conferir metadados, conteúdo e apresentação no leitor.",
                       acao_sugerida="Conferir o documento e marcar como corrigido após a revisão.", arquivo_markdown=target,
                       url_teste="/#/doc/" + document_id, fonte=source_url or "", trechos="[]")
        if _defer:
            return {"document": doc, "edition": edition, "collections": sorted(selected), "detail": detail, "changes": changes, "queue_row": new_row}
        queue_rows.append(new_row)
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=queue_fields)
        writer.writeheader()
        writer.writerows(queue_rows)
        files[QUEUE] = stream.getvalue()
        changes.append({"field": "Fila de revisão", "before": None, "after": "Pendente · prioridade média · conferir cadastro e apresentação"})
        return self.store_preview(payload["revision"], candidate, files, document_id, changes, creation=detail)

    def preview_batch(self, repository, payload):
        allowed = {"revision", "csv_content", "files", "collection_ids"}
        if not isinstance(payload, dict) or set(payload) != allowed:
            raise EditorialError("Lote inválido: envie a planilha CSV e os arquivos")
        self.require_current(repository, payload["revision"])
        uploaded, csv_content = payload["files"], payload["csv_content"]
        if not isinstance(uploaded, list) or not 1 <= len(uploaded) <= 100:
            raise EditorialError("Selecione entre 1 e 100 documentos por lote")
        if not isinstance(csv_content, str) or len(csv_content.encode("utf-8")) > 1024 * 1024:
            raise EditorialError("A planilha CSV deve ter no máximo 1 MiB")
        defaults = payload["collection_ids"]
        if not isinstance(defaults, list) or any(not isinstance(item, str) or item not in repository.collections for item in defaults):
            raise EditorialError("Coleções padrão inválidas")
        files_by_name, size = {}, 0
        for item in uploaded:
            if not isinstance(item, dict) or set(item) != {"filename", "content"} or not isinstance(item["content"], str):
                raise EditorialError("Arquivo de lote inválido")
            name = text(item["filename"], 255)
            if name in files_by_name:
                raise EditorialError("Existem arquivos com o mesmo nome no lote: " + name)
            size += len(item["content"].encode("utf-8"))
            files_by_name[name] = item["content"]
        if size > 20 * 1024 * 1024:
            raise EditorialError("O lote deve ter no máximo 20 MiB de documentos", 413)
        csv_content = csv_content.lstrip("\ufeff")
        first_line = csv_content.splitlines()[0] if csv_content.splitlines() else ""
        delimiter = max((",", ";", "\t"), key=first_line.count)
        reader = csv.DictReader(io.StringIO(csv_content, newline=""), delimiter=delimiter, strict=True)
        try:
            headers = reader.fieldnames or []
        except csv.Error as error:
            raise EditorialError("Cabeçalho CSV inválido: " + str(error)) from error
        normalized = [item.strip().lower() for item in headers]
        required = {"arquivo", "id", "titulo", "idioma"}
        optional = {"colecoes", "titulo_pt", "categoria", "tipo_documental", "data", "autoria", "referencia_arquivistica", "nome_fonte", "url_fonte", "id_fonte"}
        if len(set(normalized)) != len(normalized) or not required.issubset(normalized) or set(normalized) - required - optional:
            raise EditorialError("Cabeçalho CSV inválido. Use o modelo: arquivo, id, titulo e idioma são obrigatórios; não repita colunas.")
        reader.fieldnames = normalized
        errors, prepared, used_names, used_ids = [], [], set(), set()
        queue_fields, queue_rows = self.read_queue()
        try:
            for row in reader:
                if len(prepared) + len(errors) >= 100:
                    raise EditorialError("A planilha deve conter no máximo 100 documentos")
                line = reader.line_num
                if None in row or any(value is None for value in row.values()):
                    errors.append({"line": line, "message": "Quantidade de colunas diferente do cabeçalho."})
                    continue
                row = {key: value.strip() for key, value in row.items()}
                if not any(row.values()):
                    continue
                name, document_id = row.get("arquivo", ""), row.get("id", "")
                try:
                    if name not in files_by_name:
                        raise EditorialError("Arquivo não selecionado: " + name)
                    if name in used_names:
                        raise EditorialError("O mesmo arquivo aparece mais de uma vez na planilha: " + name)
                    if document_id in used_ids:
                        raise EditorialError("ID repetido dentro do lote: " + document_id)
                    used_names.add(name)
                    used_ids.add(document_id)
                    category = row.get("categoria") or "document"
                    category = {"documento": "document", "artigo": "article"}.get(category, category)
                    selected = [item.strip() for item in row.get("colecoes", "").split("|") if item.strip()] or defaults
                    item_payload = {"revision": payload["revision"], "id": document_id, "title": row["titulo"], "language": row["idioma"].lower(),
                        "title_pt": row.get("titulo_pt", ""), "kind": category, "document_type": row.get("tipo_documental", ""),
                        "date": row.get("data", ""), "author": row.get("autoria", ""), "archive": row.get("referencia_arquivistica", ""),
                        "source_name": row.get("nome_fonte", ""), "source_url": row.get("url_fonte", ""), "source_id": row.get("id_fonte", ""),
                        "collection_ids": selected, "filename": name, "content": files_by_name[name]}
                    entry = self.preview_document_creation(repository, item_payload, _defer=True, _queue_fields=queue_fields)
                    entry["line"] = line
                    prepared.append(entry)
                except (EditorialError, model.CatalogError, ValueError, TypeError) as error:
                    errors.append({"line": line, "id": document_id, "filename": name, "message": str(error)})
        except csv.Error as error:
            raise EditorialError("Não foi possível ler o CSV. Confira aspas e separadores: " + str(error)) from error
        for name in files_by_name.keys() - used_names:
            errors.append({"line": None, "filename": name, "message": "Arquivo selecionado sem uma linha correspondente na planilha."})
        if not prepared and not errors:
            raise EditorialError("A planilha não contém documentos")
        if errors:
            return {"can_save": False, "batch": {"errors": errors, "valid_count": len(prepared), "total_files": len(uploaded)}}
        candidate = copy.deepcopy(repository.catalog)
        contents, warnings, changes, items = {}, [], [], []
        for entry in prepared:
            doc, edition, detail = entry["document"], entry["edition"], entry["detail"]
            duplicates = []
            for earlier in items:
                same_file = earlier["sha256"] == edition["sha256"]
                same_title = any(value.casefold() in earlier["titles"] for value in doc["titles"].values())
                same_source = bool(doc["source"].get("url") and earlier["source_url"] and translations.normalized_url(doc["source"]["url"]) == translations.normalized_url(earlier["source_url"]))
                if same_file or same_title or same_source:
                    duplicates.append(earlier["id"])
            if duplicates:
                detail["warnings"].append("Possível duplicidade dentro do lote: " + ", ".join(duplicates))
            warnings.extend(doc["id"] + ": " + message for message in detail["warnings"])
            candidate["documents"].append(doc)
            candidate["editions"].append(edition)
            candidate["provenance"]["manifest_projection"]["global_document_ids"].append(doc["id"])
            for collection_id in entry["collections"]:
                position = sum(member["collection_id"] == collection_id for member in candidate["memberships"])
                candidate["memberships"].append({"collection_id": collection_id, "document_id": doc["id"], "position": position})
            queue_rows.append(entry["queue_row"])
            contents[edition["file"]] = detail["content"]
            items.append({**detail, "line": entry["line"], "title": doc["titles"].get("pt") or doc["titles"].get("ru") or doc["titles"].get("en"),
                          "sha256": edition["sha256"], "titles": [value.casefold() for value in doc["titles"].values()], "source_url": doc["source"].get("url")})
            changes.append({"field": "Novo documento: " + doc["id"], "before": None,
                            "after": {"title": items[-1]["title"], "language": edition["language"], "file": edition["file"], "collections": entry["collections"]}})
        files = self.creation_files(repository, candidate, contents)
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=queue_fields)
        writer.writeheader()
        writer.writerows(queue_rows)
        files[QUEUE] = stream.getvalue()
        batch_id = "lote-" + secrets.token_hex(6)
        entity = {"kind": "batch", "id": batch_id, "document_ids": [entry["document"]["id"] for entry in prepared]}
        detail = {"kind": "batch", "id": batch_id, "items": items, "warnings": warnings, "count": len(items)}
        return self.store_preview(payload["revision"], candidate, files, None, changes, entity=entity, creation=detail)

    def preview_collection(self, repository, payload):
        allowed = {"revision", "collection_id", "slug", "parent_id", "title_pt", "title_ru", "subtitle", "description", "cover", "accent", "source_url"}
        if not isinstance(payload, dict) or set(payload) != allowed:
            raise EditorialError("Cadastro de coleção inválido")
        self.require_current(repository, payload["revision"])
        existing = repository.collections.get(payload["collection_id"]) if payload["collection_id"] else None
        if payload["collection_id"] and existing is None:
            raise EditorialError("Coleção não encontrada", 404)
        slug = self.identifier(payload["slug"])
        parent = payload["parent_id"] or None
        if parent is not None and (parent not in repository.collections or repository.collections[parent]["parent_id"] is not None):
            raise EditorialError("Escolha uma coleção principal como destino da subcoleção")
        collection_id = parent + "/" + slug if parent else slug
        if existing and (existing["slug"] != slug or existing["parent_id"] != parent):
            raise EditorialError("O identificador e a coleção principal são fixos para preservar as URLs")
        if not existing and collection_id in repository.collections:
            raise EditorialError("Já existe uma coleção com este identificador nesse destino", 409)
        title = text(payload["title_pt"], 2000)
        if not title:
            raise EditorialError("Informe o título da coleção em português")
        cover = text(payload["cover"], 1000, True)
        if cover:
            cover_path = (self.root / cover).resolve()
            if not cover.startswith("assets/covers/") or ".." in Path(cover).parts or "\\" in cover or not cover_path.is_relative_to((self.root / "assets/covers").resolve()) or not cover_path.is_file() or cover_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".avif"}:
                raise EditorialError("Escolha uma imagem existente dentro de assets/covers/ ou deixe a capa em branco")
        accent = text(payload["accent"], 30) or "#8b2c2c"
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
            raise EditorialError("Informe uma cor no formato #8b2c2c")
        candidate = copy.deepcopy(repository.catalog)
        collection = next((item for item in candidate["collections"] if item["id"] == collection_id), None)
        if collection is None:
            collection = {"id": collection_id, "slug": slug, "parent_id": parent,
                          "position": sum(item["parent_id"] == parent for item in candidate["collections"]),
                          "titles": {}, "subtitle": None, "description": None, "source": {}, "presentation": {}, "extra": {},
                          "compatibility_fields": ["id", "title_pt", "title_ru", "subtitle_pt", "description_pt", "cover", "accent", "document_ids" if parent else "documents"]}
            if parent is None:
                collection["compatibility_fields"].append("subcollections")
            candidate["collections"].append(collection)
        if parent:
            parent_collection = next(item for item in candidate["collections"] if item["id"] == parent)
            if "subcollections" not in parent_collection["compatibility_fields"]:
                parent_collection["compatibility_fields"].append("subcollections")
        collection["titles"]["pt"] = title
        russian = text(payload["title_ru"], 2000)
        if russian:
            collection["titles"]["ru"] = russian
        else:
            collection["titles"].pop("ru", None)
        collection.update(subtitle=text(payload["subtitle"], 2000, True), description=text(payload["description"], 12000, True))
        source_url = self.source_url(payload["source_url"])
        if source_url:
            collection["source"]["url"] = source_url
        else:
            collection["source"].pop("url", None)
        if cover:
            collection["presentation"]["cover"] = cover
        else:
            collection["presentation"].pop("cover", None)
        collection["presentation"]["accent"] = accent
        if existing == collection:
            raise EditorialError("Nenhuma alteração na coleção para salvar")
        changes = [{"field": "Coleção" if existing else "Nova subcoleção" if parent else "Nova coleção", "before": existing, "after": collection}]
        detail = {"kind": "collection", "id": collection_id, "warnings": [], "new": existing is None,
                  "title": title, "subtitle": collection["subtitle"], "description": collection["description"], "cover": cover, "accent": accent}
        return self.store_preview(payload["revision"], candidate, self.creation_files(repository, candidate), None, changes,
                                  entity={"kind": "collection", "id": collection_id}, creation=detail)

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
        original = next((e for e in editions if e["language"] == doc["source_metadata"].get("original_language", "ru")), editions[0])
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
                    "translation_files": plan["translation_files"], "entity": plan.get("entity")}
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
        return {"saved": True, "history_id": record_id, "document_id": plan["document_id"], "revision": self.revision(), "entity": plan.get("entity"),
                "document_exists": any(doc["id"] == plan["document_id"] for doc in repository.catalog["documents"]),
                "message": "Alterações salvas. Catálogo, manifesto e busca estão atualizados." if catalog_changed else "Fila de revisão atualizada; os metadados não foram alterados."}
