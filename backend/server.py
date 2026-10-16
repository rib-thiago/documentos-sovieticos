"""HTTP local: site existente e API de consulta no mesmo endereço."""

from __future__ import annotations

import argparse
import html
import ipaddress
import json
import mimetypes
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from . import catalog as model
from .database import QueryError, Repository, ensure_index
from .editorial import Editorial, EditorialError, STATUSES, PRIORITIES
from .translations import MAX_TRANSLATION_BYTES


class LocalServer(ThreadingHTTPServer):
    # Ao encerrar, aguarda gravações em curso antes de liberar o bloqueio do acervo.
    daemon_threads = False

    def server_close(self):
        super().server_close()
        if hasattr(self, "editorial"):
            self.editorial.close()


def handler_for(repository, editorial):
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
            try:
                self.require_local_editorial()
                if self.path not in {"/api/editorial/preview", "/api/editorial/save", "/api/editorial/translations/preview", "/api/editorial/markdown/preview"}:
                    self.send_json({"error": "Operação não permitida"}, 405)
                    return
                if self.headers.get("Origin") != "http://" + self.headers.get("Host", ""):
                    raise EditorialError("A edição exige uma página aberta no próprio backend local", 403)
                if not secrets.compare_digest(self.headers.get("X-Editorial-Token", ""), editorial.token):
                    raise EditorialError("Sessão editorial expirada. Recarregue a página.", 403)
                if self.headers.get_content_type() != "application/json":
                    raise EditorialError("Envie JSON", 415)
                length = int(self.headers.get("Content-Length", "0"))
                maximum = MAX_TRANSLATION_BYTES * 6 + 200000 if self.path in {"/api/editorial/translations/preview", "/api/editorial/markdown/preview"} else 200000
                if not 1 <= length <= maximum:
                    raise EditorialError("Pedido vazio ou maior que o limite permitido", 413)
                self.connection.settimeout(30)
                payload = json.loads(self.rfile.read(length))
                with editorial.lock:
                    if self.path == "/api/editorial/translations/preview":
                        result = editorial.preview_translation(repository, payload)
                    elif self.path == "/api/editorial/markdown/preview":
                        result = editorial.preview_markdown(repository, payload)
                    elif self.path == "/api/editorial/preview":
                        result = editorial.preview(repository, payload)
                    else:
                        result = editorial.save(repository, payload)
                self.send_json(result)
            except EditorialError as error:
                self.send_json({"error": str(error)}, error.status)
            except (ValueError, TypeError, model.CatalogError) as error:
                self.send_json({"error": str(error)}, 400)
            except Exception:
                self.log_error("Falha na edição: %s", self.path)
                self.send_json({"error": "Não foi possível concluir a gravação. Reabra o documento; o histórico local permite recuperar uma interrupção."}, 500)

        def unsupported_write(self):
            self.send_json({"error": "Método não permitido"}, 405)

        do_PUT = unsupported_write
        do_PATCH = unsupported_write
        do_DELETE = unsupported_write

        def require_local_editorial(self):
            host = urlsplit("http://" + self.headers.get("Host", ""))
            try:
                local_host = host.hostname == "localhost" or ipaddress.ip_address(host.hostname).is_loopback
                local_peer = ipaddress.ip_address(self.client_address[0]).is_loopback
                local_bind = ipaddress.ip_address(self.server.server_address[0]).is_loopback
                port = host.port or 80
            except (ValueError, TypeError):
                raise EditorialError("Endereço local inválido", 403)
            if not local_host or not local_peer or not local_bind or port != self.server.server_port:
                raise EditorialError("A área editorial exige backend em 127.0.0.1 e acesso por localhost ou 127.0.0.1", 403)

        def do_GET(self):
            with editorial.lock:
                self.get_locked()

        def get_locked(self):
            try:
                request = urlsplit(self.path)
                path = unquote(request.path)
                if len(request.query) > 4000:
                    raise QueryError("Parâmetros de consulta muito extensos")
                raw_params = parse_qs(request.query, max_num_fields=30)
                if any(len(values) != 1 for values in raw_params.values()):
                    raise QueryError("Use cada parâmetro somente uma vez")
                params = {key: values[0] for key, values in raw_params.items()}
                if path == "/editorial":
                    self.require_local_editorial()
                    page = (Path(__file__).parent / "editorial.html").read_bytes()
                    self.send_data(page, "text/html; charset=utf-8")
                elif path.startswith("/api/editorial/"):
                    self.require_local_editorial()
                    if path == "/api/editorial/session":
                        self.send_json({"token": editorial.token, "statuses": STATUSES, "priorities": list(PRIORITIES), "revision": editorial.revision(),
                                        "features": ["translation_import", "markdown_edit", "reader_integration"]})
                    elif path == "/api/editorial/queue":
                        self.send_json(editorial.queue(repository, params))
                    elif path == "/api/editorial/history":
                        self.send_json(editorial.history(params.get("document")))
                    elif path.startswith("/api/editorial/documents/"):
                        self.send_json(editorial.document(repository, path.removeprefix("/api/editorial/documents/")))
                    elif path.startswith("/api/editorial/editions/"):
                        self.send_json(editorial.editable_edition(repository, path.removeprefix("/api/editorial/editions/")))
                    else:
                        self.send_json({"error": "Endpoint editorial não encontrado"}, 404)
                elif path in {"/api", "/api/"}:
                    self.send_json({"service": "Documentos Soviéticos", "schema_version": 1,
                        "endpoints": ["/api/health", "/api/collections", "/api/collections/centro-de-leningrado",
                            "/api/documents?limit=5", "/api/documents/showtrials-1665", "/api/vocabularies",
                            "/api/search?q=Николаева&language=ru&limit=5"], "site": "/", "guide": "/local"})
                elif path == "/api/health":
                    self.send_json({"status": "ok", "mode": "local_editorial", "schema_version": 1, **repository.info})
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
            except EditorialError as error:
                self.send_json({"error": str(error)}, error.status)
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
                ("Buscar no acervo", "/#/busca"),
                ("Área editorial local: revisão e metadados", "/editorial"),
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
            <p>Consulte o site, use a busca e abra a área editorial para revisar pendências e editar metadados com prévia e histórico. Os endpoints da API apresentam JSON.</p><ul>{links}</ul>
            <p>Para encerrar, pressione <kbd>Ctrl+C</kbd> no terminal. As gravações da área editorial atualizam manifesto e busca automaticamente. Edições externas dos arquivos exigem reinicialização.</p></html>'''
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
    editorial = Editorial(root)
    try:
        catalog = model.load(root)
        path = db_path or root / ".local/catalog.sqlite3"
        info = ensure_index(root, path, catalog, rebuild, progress)
        repository = Repository(root, path, catalog, info)
        server = LocalServer((host, port), handler_for(repository, editorial))
    except Exception:
        editorial.close()
        raise
    server.repository = repository
    server.editorial = editorial
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
    print(f"Site: http://{host}:{port}/\nAmbiente local: http://{host}:{port}/local\nÁrea editorial: http://{host}:{port}/editorial\nCtrl+C para encerrar.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
