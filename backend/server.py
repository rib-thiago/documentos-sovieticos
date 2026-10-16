"""HTTP local: site existente e API de consulta no mesmo endereço."""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from . import catalog as model
from .database import QueryError, Repository, ensure_index


def handler_for(repository):
    class Handler(BaseHTTPRequestHandler):
        server_version = "DocumentosSovieticos/1"

        def send_data(self, data, content_type, status=200):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(data)

        def send_json(self, value, status=200):
            self.send_data(model.json_bytes(value), "application/json; charset=utf-8", status)

        def do_HEAD(self):
            self.do_GET()

        def do_POST(self):
            self.send_json({"error": "Esta entrega oferece somente consulta; edição será uma etapa própria"}, 405)

        do_PUT = do_POST
        do_PATCH = do_POST
        do_DELETE = do_POST

        def do_GET(self):
            try:
                request = urlsplit(self.path)
                path = unquote(request.path)
                if len(request.query) > 4000:
                    raise QueryError("Parâmetros de consulta muito extensos")
                raw_params = parse_qs(request.query, max_num_fields=30)
                if any(len(values) != 1 for values in raw_params.values()):
                    raise QueryError("Use cada parâmetro somente uma vez")
                params = {key: values[0] for key, values in raw_params.items()}
                if path in {"/api", "/api/"}:
                    self.send_json({"service": "Documentos Soviéticos", "schema_version": 1,
                        "endpoints": ["/api/health", "/api/collections", "/api/collections/centro-de-leningrado",
                            "/api/documents?limit=5", "/api/documents/showtrials-1665", "/api/vocabularies",
                            "/api/search?q=Николаева&language=ru&limit=5"], "site": "/", "guide": "/local"})
                elif path == "/api/health":
                    self.send_json({"status": "ok", "mode": "read_only", "schema_version": 1, **repository.info})
                elif path == "/api/vocabularies":
                    self.send_json(repository.catalog["vocabularies"])
                elif path in {"/api/documents", "/api/search"}:
                    if path == "/api/search" and not params.get("q", "").strip():
                        raise QueryError("A busca exige q")
                    self.send_json(repository.documents(params))
                elif path.startswith("/api/documents/"):
                    doc = repository.document(path.removeprefix("/api/documents/"))
                    self.send_json(doc if doc else {"error": "Documento não encontrado"}, 200 if doc else 404)
                elif path == "/api/collections":
                    items = repository.collection_list()
                    self.send_json({"total": len(items), "items": items})
                elif path.startswith("/api/collections/"):
                    collection = repository.collection(path.removeprefix("/api/collections/"))
                    self.send_json(collection if collection else {"error": "Coleção não encontrada"}, 200 if collection else 404)
                elif path.startswith("/api/editions/") and path.endswith("/content"):
                    edition = repository.edition(path.removeprefix("/api/editions/").removesuffix("/content"))
                    if not edition:
                        self.send_json({"error": "Edição não encontrada"}, 404)
                    else:
                        data = model.content_path(repository.root, edition["file"]).read_bytes()
                        if model.sha256(data) != edition["sha256"]:
                            self.send_json({"error": "O texto mudou desde a indexação. Confira a edição e reinicie/reindexe o backend."}, 409)
                        else:
                            self.send_data(data, "text/plain; charset=utf-8")
                elif path.startswith("/api/"):
                    self.send_json({"error": "Endpoint não encontrado"}, 404)
                elif path == "/local":
                    self.local_page()
                else:
                    self.static_file(path)
            except (QueryError, ValueError) as error:
                self.send_json({"error": str(error)}, 400)
            except OSError:
                self.send_json({"error": "Arquivo indisponível"}, 404)
            except Exception:
                self.log_error("Falha inesperada ao atender %s", self.path)
                self.send_json({"error": "Falha interna; consulte o terminal do backend"}, 500)

        def local_page(self):
            info = repository.info
            examples = [
                ("Abrir o site e o leitor existentes", "/"),
                ("Saúde e contagens do catálogo", "/api/health"),
                ("Coleções e subcoleções", "/api/collections"),
                ("Documento de Nikolaev com russo e português", "/api/documents/showtrials-1665"),
                ("Documentos do Centro de Leningrado na ordem da fonte", "/api/documents?collection=centro-de-leningrado&sort=source&limit=5"),
                ("Documentos com versão portuguesa", "/api/documents?language=pt&limit=20"),
                ("Pesquisa no corpo russo por Николаева", "/api/search?q=Николаева&language=ru&limit=5"),
                ("Vocabulário de tipos documentais", "/api/vocabularies"),
            ]
            links = "".join(f'<li><a href="{html.escape(url, quote=True)}">{html.escape(label)}</a></li>' for label, url in examples)
            page = f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
            <title>Ambiente local — Documentos Soviéticos</title><style>body{{max-width:760px;margin:3rem auto;padding:0 1rem;font:17px/1.6 system-ui;color:#252525;background:#faf8f4}}h1{{font:600 1.8rem Georgia,serif}}a{{color:#8b2c2c}}li{{margin:.6rem 0}}code{{font-size:.9em}}</style>
            <h1>Ambiente local do acervo</h1><p>{info['documents']} documentos · {info['editions']} versões por idioma · {info['collections']} coleções · {info['subcollections']} subcoleções.</p>
            <p>O site mantém a navegação atual. Esta página reúne os testes de consulta do novo catálogo; as respostas da API aparecem em JSON. A interface de busca será a próxima entrega.</p><ul>{links}</ul>
            <p>Para encerrar, pressione <kbd>Ctrl+C</kbd> no terminal. Depois de editar metadados, exporte o manifesto e reinicie o backend para atualizar o índice.</p></html>'''
            self.send_data(page.encode("utf-8"), "text/html; charset=utf-8")

        def static_file(self, path):
            relative = path.lstrip("/") or "index.html"
            # Apenas os recursos publicados do site; não expõe temporario/, Git ou o banco.
            if not (relative == "index.html" or relative == "data/manifest.json" or relative.startswith(("assets/", "originais/"))):
                self.send_json({"error": "Recurso não publicado"}, 404)
                return
            if ".." in Path(relative).parts or "\\" in relative or any(part.startswith(".") for part in Path(relative).parts):
                self.send_json({"error": "Caminho inválido"}, 404)
                return
            target = (repository.root / relative).resolve()
            if not target.is_relative_to(repository.root.resolve()) or not target.is_file() or target.name.endswith(":Zone.Identifier"):
                self.send_json({"error": "Arquivo não encontrado"}, 404)
                return
            media = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            if media.startswith("text/") or media in {"application/javascript", "application/json"}:
                media += "; charset=utf-8"
            self.send_data(target.read_bytes(), media)

    return Handler


def create_server(root, host="127.0.0.1", port=8000, db_path=None, rebuild=False, progress=None):
    catalog = model.load(root)
    path = db_path or root / ".local/catalog.sqlite3"
    info = ensure_index(root, path, catalog, rebuild, progress)
    repository = Repository(root, path, catalog, info)
    server = ThreadingHTTPServer((host, port), handler_for(repository))
    server.daemon_threads = True
    server.repository = repository
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--rebuild", action="store_true", help="Reconstrói o índice SQLite derivado")
    args = parser.parse_args()
    try:
        print("Conferindo catálogo e preparando o backend local...", flush=True)
        server = create_server(model.ROOT, args.host, args.port, rebuild=args.rebuild, progress=lambda message: print(message, flush=True))
    except (model.CatalogError, OSError) as error:
        parser.exit(1, f"Não foi possível iniciar: {error}\nSe a porta estiver ocupada, encerre o servidor anterior ou use --port 8001.\n")
    host, port = server.server_address
    print(f"Site: http://{host}:{port}/\nTestes locais: http://{host}:{port}/local\nCtrl+C para encerrar.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
