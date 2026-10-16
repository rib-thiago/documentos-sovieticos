"""Índice SQLite derivado do catálogo versionado e dos textos locais."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import quote

from . import catalog as model

INDEX_VERSION = "1"


def fingerprint(root):
    chunks = [INDEX_VERSION.encode()]
    for name in model.FILES:
        chunks.append((root / "data/catalog" / (name + ".json")).read_bytes())
    return model.sha256(b"\0".join(chunks))


def plain_text(source, format):
    if format == "markdown":
        source = re.sub(r"(?m)^#{1,6}\s+", "", source)
        source = re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])", r"\1", source)
    return re.sub(r"\s+", " ", source).strip()


@contextmanager
def read_connection(path):
    connection = sqlite3.connect("file:" + quote(str(Path(path).resolve())) + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def ensure_index(root, path, catalog=None, rebuild=False, progress=None, *, check_manifest=True, revision=None, content_overrides=None):
    catalog = catalog or model.load(root)
    counts = model.validate(catalog, root, check_manifest=check_manifest, content_overrides=content_overrides)
    revision = revision or fingerprint(root)
    if path.exists() and not rebuild:
        try:
            with read_connection(path) as connection:
                cached = connection.execute("SELECT value FROM metadata WHERE key='revision'").fetchone()
                if cached and cached[0] == revision:
                    if progress:
                        progress("Catálogo conferido; reutilizando o índice local.")
                    return {"rebuilt": False, "revision": revision, **counts}
        except sqlite3.DatabaseError:
            pass  # Um índice descartável danificado pode ser reconstruído.
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".catalog-", suffix=".sqlite3", dir=path.parent)
    os.close(descriptor)
    connection = sqlite3.connect(temporary)
    try:
        if progress:
            progress(f"Construindo índice de {len(catalog['editions'])} versões por idioma...")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.executescript("""
            CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE documents(id TEXT PRIMARY KEY, title TEXT NOT NULL, title_sort TEXT NOT NULL,
                kind TEXT NOT NULL, document_type TEXT, data TEXT NOT NULL);
            CREATE TABLE editions(id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id),
                language TEXT NOT NULL, position INTEGER NOT NULL, data TEXT NOT NULL,
                UNIQUE(document_id, language));
            CREATE INDEX editions_document ON editions(document_id);
            CREATE TABLE collections(id TEXT PRIMARY KEY, parent_id TEXT REFERENCES collections(id),
                position INTEGER NOT NULL, data TEXT NOT NULL);
            CREATE TABLE memberships(collection_id TEXT NOT NULL REFERENCES collections(id),
                document_id TEXT NOT NULL REFERENCES documents(id), position INTEGER NOT NULL,
                PRIMARY KEY(collection_id, position));
            CREATE INDEX memberships_document ON memberships(document_id);
        """)
        try:
            connection.execute("CREATE VIRTUAL TABLE search USING fts5(document_id UNINDEXED, edition_id UNINDEXED, language UNINDEXED, title, body, tokenize='unicode61 remove_diacritics 2')")
        except sqlite3.OperationalError as error:
            raise model.CatalogError("Este Python/SQLite não oferece FTS5; use uma distribuição de Python com SQLite FTS5 habilitado") from error
        with connection:
            docs = {doc["id"]: doc for doc in catalog["documents"]}
            for doc in docs.values():
                title = doc["titles"].get("pt") or doc["titles"].get("ru") or doc["id"]
                connection.execute("INSERT INTO documents VALUES(?,?,?,?,?,?)", (doc["id"], title, title.casefold(), doc["kind"], doc["document_type"], json.dumps(doc, ensure_ascii=False)))
            for edition_number, edition in enumerate(catalog["editions"], 1):
                connection.execute("INSERT INTO editions VALUES(?,?,?,?,?)", (edition["id"], edition["document_id"], edition["language"], edition["position"], json.dumps(edition, ensure_ascii=False)))
                doc = docs[edition["document_id"]]
                titles = " ".join(dict.fromkeys(doc["titles"].values()))
                raw_content = model.content_bytes(root, edition["file"], content_overrides)
                if model.sha256(raw_content) != edition["sha256"]:
                    raise model.CatalogError(f"Arquivo mudou durante a indexação: {edition['file']}")
                body = plain_text(raw_content.decode("utf-8"), edition["format"])
                connection.execute("INSERT INTO search VALUES(?,?,?,?,?)", (doc["id"], edition["id"], edition["language"], titles, body))
                if progress and (edition_number % 250 == 0 or edition_number == len(catalog["editions"])):
                    progress(f"Indexadas {edition_number}/{len(catalog['editions'])} versões.")
            for collection in catalog["collections"]:
                connection.execute("INSERT INTO collections VALUES(?,?,?,?)", (collection["id"], collection["parent_id"], collection["position"], json.dumps(collection, ensure_ascii=False)))
            connection.executemany("INSERT INTO memberships VALUES(?,?,?)", [(m["collection_id"], m["document_id"], m["position"]) for m in catalog["memberships"]])
            connection.execute("INSERT INTO metadata VALUES('revision',?)", (revision,))
            connection.execute("INSERT INTO search(search) VALUES('optimize')")
            if connection.execute("PRAGMA foreign_key_check").fetchall():
                raise model.CatalogError("Índice com associações inválidas")
        connection.close()
        os.replace(temporary, path)
    finally:
        connection.close()
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {"rebuilt": True, "revision": revision, **counts}


class QueryError(ValueError):
    pass


def fts_expression(text):
    if len(text) > 500:
        raise QueryError("A consulta deve ter até 500 caracteres")
    if text.count('"') % 2:
        raise QueryError("Feche as aspas da expressão de busca")
    terms = [phrase or term for phrase, term in re.findall(r'"([^\"]+)"|(\S+)', text)]
    if not terms or not any(re.search(r"\w", t) for t in terms):
        raise QueryError("Informe uma palavra ou frase para pesquisar")
    return " AND ".join('"' + term.replace('"', '""') + '"' for term in terms)


class Repository:
    def __init__(self, root, path, catalog, info):
        self.root, self.path, self.catalog, self.info = root, path, catalog, info
        self.collections = {c["id"]: c for c in catalog["collections"]}

    def document(self, doc_id):
        with read_connection(self.path) as connection:
            row = connection.execute("SELECT data FROM documents WHERE id=?", (doc_id,)).fetchone()
            if row is None:
                return None
            doc = json.loads(row[0])
            doc["editions"] = [json.loads(r[0]) for r in connection.execute("SELECT data FROM editions WHERE document_id=? ORDER BY position", (doc_id,))]
            doc["collections"] = [json.loads(r[0]) for r in connection.execute("SELECT DISTINCT c.data FROM collections c JOIN memberships m ON m.collection_id=c.id WHERE m.document_id=? ORDER BY c.parent_id,c.position", (doc_id,))]
            for edition in doc["editions"]:
                edition["content_url"] = "/api/editions/" + quote(edition["id"], safe="") + "/content"
            return doc

    def edition(self, edition_id):
        with read_connection(self.path) as connection:
            row = connection.execute("SELECT data FROM editions WHERE id=?", (edition_id,)).fetchone()
            return json.loads(row[0]) if row else None

    def collection(self, collection_id):
        result = self.collections.get(collection_id)
        if result is None:
            return None
        with read_connection(self.path) as connection:
            count = connection.execute("SELECT COUNT(DISTINCT document_id) FROM memberships WHERE collection_id=?", (collection_id,)).fetchone()[0]
        return {**result, "document_count": count, "children": [self.collection(c["id"]) for c in self.collections.values() if c["parent_id"] == collection_id]}

    def collection_list(self):
        return [self.collection(c["id"]) for c in self.catalog["collections"] if c["parent_id"] is None]

    def documents(self, params):
        allowed = {"q", "collection", "subcollection", "language", "type", "kind", "limit", "offset", "sort", "scope"}
        if set(params) - allowed:
            raise QueryError("Parâmetros desconhecidos: " + ", ".join(sorted(set(params) - allowed)))
        try:
            limit, offset = int(params.get("limit", "25")), int(params.get("offset", "0"))
        except ValueError as error:
            raise QueryError("limit e offset devem ser inteiros") from error
        if not 1 <= limit <= 100 or offset < 0:
            raise QueryError("Use limit entre 1 e 100 e offset maior ou igual a zero")
        query = params.get("q", "").strip()
        sort = params.get("sort", "relevance" if query else "title")
        if sort not in {"title", "id", "source", "relevance"}:
            raise QueryError("Ordenação inválida: title, id, source ou relevance")
        scope = params.get("scope", "all")
        if scope not in {"all", "title"}:
            raise QueryError("scope deve ser all ou title")
        collection = params.get("collection")
        if params.get("subcollection"):
            if not collection or "/" in collection:
                raise QueryError("subcollection exige a coleção principal em collection")
            collection += "/" + params["subcollection"]
        if collection and collection not in self.collections:
            raise QueryError("Coleção ou subcoleção desconhecida")
        if sort == "source" and not collection:
            raise QueryError("sort=source exige collection")
        where, arguments = [], []
        if collection:
            where.append("EXISTS(SELECT 1 FROM memberships m WHERE m.document_id=d.id AND m.collection_id=?)")
            arguments.append(collection)
        if params.get("type"):
            if params["type"] == "unspecified":
                where.append("d.document_type IS NULL")
            else:
                if params["type"] not in self.catalog["vocabularies"]["document_types"]:
                    raise QueryError("Tipo documental desconhecido; consulte /api/vocabularies")
                where.append("d.document_type=?")
                arguments.append(params["type"])
        if params.get("kind"):
            if params["kind"] not in {"document", "article"}:
                raise QueryError("kind deve ser document ou article")
            where.append("d.kind=?")
            arguments.append(params["kind"])
        language = params.get("language")
        if language:
            if language not in self.catalog["vocabularies"]["languages"]:
                raise QueryError("Idioma desconhecido")
            where.append("EXISTS(SELECT 1 FROM editions e WHERE e.document_id=d.id AND e.language=?)")
            arguments.append(language)
        with read_connection(self.path) as connection:
            clause = " AND ".join(where) or "1=1"
            if query:
                expression = fts_expression(query)
                if scope == "title":
                    expression = "title : (" + expression + ")"
                snippet_column = "3" if scope == "title" else "4"
                sql = "SELECT d.id, d.data, d.title_sort, search.edition_id, search.language, bm25(search,0,0,0,8,1) AS score, snippet(search," + snippet_column + ",'','',' … ',24) AS snippet FROM search JOIN documents d ON d.id=search.document_id WHERE search MATCH ? AND " + clause
                values = [expression, *arguments]
                if language:
                    sql += " AND search.language=?"
                    values.append(language)
                try:
                    matches = connection.execute(sql + " ORDER BY score,d.id", values).fetchall()
                except sqlite3.OperationalError as error:
                    raise QueryError("Expressão de busca inválida") from error
                unique = {}
                for row in matches:
                    if row["id"] not in unique:
                        unique[row["id"]] = row
                rows = list(unique.values())
            else:
                rows = connection.execute("SELECT d.id,d.data,d.title_sort FROM documents d WHERE " + clause, arguments).fetchall()
            if sort == "source":
                order = {r[0]: r[1] for r in connection.execute("SELECT document_id,MIN(position) FROM memberships WHERE collection_id=? GROUP BY document_id", (collection,))}
                rows.sort(key=lambda r: (order[r["id"]], r["id"]))
            elif sort == "id":
                rows.sort(key=lambda r: r["id"])
            elif sort == "title" or not query:
                rows.sort(key=lambda r: (r["title_sort"], r["id"]))
            total = len(rows)
            selected = rows[offset:offset + limit]
            items = []
            for row in selected:
                doc = json.loads(row["data"])
                doc["languages"] = [r[0] for r in connection.execute("SELECT language FROM editions WHERE document_id=? ORDER BY position", (row["id"],))]
                doc["url"] = "/#/doc/" + doc["id"]
                if query:
                    doc["match"] = {"edition_id": row["edition_id"], "language": row["language"], "score": row["score"], "snippet": row["snippet"]}
                items.append(doc)
            return {"total": total, "limit": limit, "offset": offset, "has_more": offset + limit < total,
                    "sort": sort, "query": query, "items": items, "catalog_revision": self.info["revision"]}
