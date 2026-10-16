"""Edição local de metadados com prévia, controle de concorrência e recuperação."""

from __future__ import annotations

import copy
import csv
import fcntl
import gzip
import io
import json
import os
import secrets
import threading
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from . import catalog as model
from .database import INDEX_VERSION, ensure_index

QUEUE = "docs/revisao-markdown/pendencias.csv"
WRITABLE = {"data/catalog/documents.json", "data/catalog/memberships.json", "data/manifest.json", QUEUE}
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
        items = [{**row, "titles": docs.get(row["id"], {}).get("titles", {})} for row in filtered[offset:offset + limit]]
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

    def recover_pending(self):
        marker = self.directory / "pending.json"
        if not marker.exists():
            return
        record = self.history_record(model.read_json(marker)["id"])
        for file, content in record["before"].items():
            if file not in WRITABLE:
                raise model.CatalogError("Caminho inválido no histórico de recuperação")
            current = (self.root / file).read_bytes().decode("utf-8")
            if current not in {content, record["after"][file]}:
                raise model.CatalogError("Há edição externa durante uma transação interrompida. Preserve .local/editorial e recupere antes de continuar.")
        for file, content in record["before"].items():
            model.atomic_write(self.root / file, content.encode("utf-8"))
        metadata = {k: record[k] for k in ("id", "created_at", "document_id", "summary", "changes", "restores")}
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
                if file not in WRITABLE:
                    raise EditorialError("Arquivo de histórico inválido")
                # read_bytes preserva CRLF da fila ao comparar o snapshot.
                if (self.root / file).read_bytes().decode("utf-8") != after:
                    raise EditorialError("Há alterações posteriores nesses arquivos. Desfaça primeiro a alteração mais recente que os modificou.", 409)
            files = record["before"]
            for name in ("documents", "memberships"):
                file = "data/catalog/" + name + ".json"
                if file in files:
                    candidate[name] = json.loads(files[file])
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
        if not files:
            raise EditorialError("Nenhuma alteração para salvar")
        # Validação operacional da proposta; não escreve nem executa suíte de testes.
        model.validate(candidate, self.root, check_manifest=False)
        if "data/manifest.json" in files and json.loads(files["data/manifest.json"]) != model.export_manifest(candidate):
            raise EditorialError("O estado histórico não corresponde ao catálogo atual; restauração recusada")
        preview_id = secrets.token_urlsafe(24)
        self.previews = {key: value for key, value in self.previews.items() if value["expires"] > time.time()}
        while len(self.previews) >= 8:
            self.previews.pop(next(iter(self.previews)))
        self.previews[preview_id] = {"revision": revision, "candidate": candidate, "files": files, "document_id": document_id,
            "changes": changes, "restores": restores, "expires": time.time() + 900}
        return {"preview_id": preview_id, "changes": changes, "document_id": document_id, "expires_in": 900,
                "updates_index": any(file.startswith("data/catalog/") for file in files)}

    def save(self, repository, payload):
        if not isinstance(payload, dict) or set(payload) != {"preview_id"}:
            raise EditorialError("Envie apenas o identificador da prévia aprovada")
        plan = self.previews.pop(payload["preview_id"], None)
        if not plan or plan["expires"] <= time.time():
            raise EditorialError("A prévia expirou. Gere uma nova antes de salvar.", 409)
        if plan["revision"] != self.revision():
            raise EditorialError("Houve outra edição desde a prévia. Reabra o documento.", 409)
        record_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f") + "-" + secrets.token_hex(6)
        files = plan["files"]
        before = {file: (self.root / file).read_bytes().decode("utf-8") for file in files}
        summary = "; ".join(c["field"] for c in plan["changes"])
        metadata = {"id": record_id, "created_at": datetime.now(timezone.utc).isoformat(), "document_id": plan["document_id"],
                    "summary": summary, "changes": plan["changes"], "restores": plan["restores"], "state": "prepared"}
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
                info = ensure_index(self.root, stage, plan["candidate"], rebuild=True, check_manifest=False, revision=revision)
            # O histórico fica completo antes da primeira escrita nos arquivos publicados.
            model.atomic_write(self.history_dir / (record_id + ".json.gz"), gzip.compress(model.json_bytes(record)))
            model.atomic_write(self.history_dir / (record_id + ".meta.json"), model.json_bytes(metadata))
            model.atomic_write(self.directory / "pending.json", model.json_bytes({"id": record_id}))
            for file, content in files.items():
                model.atomic_write(self.root / file, content.encode("utf-8"))
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
