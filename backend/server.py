"""HTTP local: site existente e API de consulta no mesmo endereço."""

from __future__ import annotations

import argparse
import html
import ipaddress
import json
import mimetypes
import secrets
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlsplit

from . import catalog as model
from .database import QueryError, Repository, ensure_index
from .editorial import Editorial, EditorialError, STATUSES, PRIORITIES
from .translations import MAX_TRANSLATION_BYTES
from .pdf_sources import PDFSources
from .research_projects import ResearchProjects
from .workspace_editions import WorkspaceEditions


class LocalServer(ThreadingHTTPServer):
    # Ao encerrar, aguarda gravações em curso antes de liberar o bloqueio do acervo.
    daemon_threads = False

    def server_close(self):
        super().server_close()
        if hasattr(self, "pdf_sources"):
            self.pdf_sources.close()
        if hasattr(self, "editorial"):
            self.editorial.close()


def handler_for(repository, editorial):
    class Handler(BaseHTTPRequestHandler):
        server_version = "DocumentosSovieticos/1"

        def send_data(self, data, content_type, status=200):
            try:
                self.write_response(data, content_type, status)
            except (ConnectionError, TimeoutError):
                # O cliente pode cancelar/recarregar a página. Não enviar uma segunda resposta.
                self.close_connection = True

        def write_response(self, data, content_type, status=200):
            self.connection.settimeout(30)
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
                request_path = urlsplit(self.path).path
                if request_path not in {"/api/editorial/pdf/publication/preview", "/api/editorial/pdf/publication/apply", "/api/editorial/pdf/alignment/preview", "/api/editorial/pdf/incorporation/preview", "/api/editorial/pdf/incorporation/save", "/api/editorial/pdf/incorporation/finish", "/api/editorial/pdf/links/preview", "/api/editorial/pdf/links/save", "/api/editorial/pdf/review/preview", "/api/editorial/pdf/review/save", "/api/editorial/pdf/ocr/preview", "/api/editorial/pdf/ocr/start", "/api/editorial/pdf/ocr/resume", "/api/editorial/pdf/operations/preview", "/api/editorial/pdf/operations/start", "/api/editorial/pdf/operations/resume", "/api/editorial/workspace/preview", "/api/editorial/workspace/save", "/api/editorial/workspace/promotion-preview", "/api/editorial/workspace/promote", "/api/editorial/projects/preview", "/api/editorial/projects/save", "/api/editorial/projects/activate", "/api/editorial/pdf/upload", "/api/editorial/pdf/action", "/api/editorial/preview", "/api/editorial/save", "/api/editorial/translations/preview", "/api/editorial/markdown/preview", "/api/editorial/passages/preview", "/api/editorial/documents/preview", "/api/editorial/collections/preview", "/api/editorial/batches/preview"}:
                    self.send_json({"error": "Operação não permitida"}, 405)
                    return
                if self.headers.get("Origin") != "http://" + self.headers.get("Host", ""):
                    raise EditorialError("A edição exige uma página aberta no próprio backend local", 403)
                if not secrets.compare_digest(self.headers.get("X-Editorial-Token", ""), editorial.token):
                    raise EditorialError("Sessão editorial expirada. Recarregue a página.", 403)
                if request_path == "/api/editorial/pdf/upload":
                    project_id = self.headers.get("X-Research-Project", "")
                    if project_id and editorial.projects.get(project_id)["archived"]:
                        raise EditorialError("Selecione um projeto não arquivado")
                    if self.headers.get_content_type() != "application/pdf":
                        raise EditorialError("Envie um arquivo PDF", 415)
                    length = int(self.headers.get("Content-Length", "0"))
                    if not 1 <= length <= editorial.pdf_sources.max_bytes:
                        raise EditorialError(f"O PDF deve ter até {editorial.pdf_sources.max_bytes // (1024 * 1024)} MiB", 413)
                    self.connection.settimeout(60)
                    result = editorial.pdf_sources.upload_stream(unquote(self.headers.get("X-PDF-Filename", "fonte.pdf")), self.rfile, length)
                    if project_id:
                        try:
                            editorial.projects.attach_source(project_id, result["source_id"])
                        except EditorialError as error:
                            result["warning"] = "PDF preservado, mas não vinculado ao projeto: " + str(error)
                    self.send_json(result)
                    return
                if self.headers.get_content_type() != "application/json":
                    raise EditorialError("Envie JSON", 415)
                length = int(self.headers.get("Content-Length", "0"))
                maximum = 130 * 1024 * 1024 if self.path == "/api/editorial/batches/preview" else MAX_TRANSLATION_BYTES * 6 + 200000 if self.path in {"/api/editorial/translations/preview", "/api/editorial/markdown/preview", "/api/editorial/passages/preview", "/api/editorial/documents/preview", "/api/editorial/collections/preview", "/api/editorial/batches/preview"} else 200000
                if request_path.startswith("/api/editorial/pdf/links/"):
                    maximum = 1024 * 1024
                if request_path.startswith("/api/editorial/pdf/review/"):
                    maximum = 16 * 1024 * 1024
                if request_path.startswith("/api/editorial/projects/"):
                    maximum = 2 * 1024 * 1024
                if request_path.startswith("/api/editorial/workspace/"):
                    maximum = MAX_TRANSLATION_BYTES * 6 + 200000
                if not 1 <= length <= maximum:
                    raise EditorialError("Pedido vazio ou maior que o limite permitido", 413)
                self.connection.settimeout(30)
                payload = json.loads(self.rfile.read(length))
                if request_path.startswith("/api/editorial/pdf/publication/"):
                    if not isinstance(payload,dict):raise EditorialError("Pedido inválido")
                    operation=request_path.rsplit("/",1)[1]
                    self.send_json(getattr(editorial.pdf_sources.publication,operation)(repository,payload))
                    return
                if request_path == "/api/editorial/pdf/alignment/preview":
                    self.send_json(editorial.pdf_sources.alignment.preview(payload))
                    return
                if request_path.startswith("/api/editorial/pdf/incorporation/"):
                    if not isinstance(payload,dict):raise EditorialError("Pedido inválido")
                    operation=request_path.rsplit("/",1)[1]
                    result=editorial.pdf_sources.incorporation.finish(repository,payload.get('receipt_id')) if operation=="finish" else getattr(editorial.pdf_sources.incorporation,operation)(repository,payload)
                    self.send_json(result)
                    return
                if request_path.startswith("/api/editorial/pdf/links/"):
                    if not isinstance(payload, dict):
                        raise EditorialError("Pedido inválido")
                    with editorial.lock:
                        operation = request_path.rsplit("/", 1)[1]
                        self.send_json(getattr(editorial.pdf_sources.links, operation)(repository, payload))
                    return
                if request_path.startswith(("/api/editorial/pdf/review/", "/api/editorial/pdf/ocr/")):
                    if not isinstance(payload, dict):
                        raise EditorialError("Pedido inválido")
                    kind, operation = request_path.rsplit("/", 2)[-2:]
                    method = {("review", "preview"): "preview", ("review", "save"): "save",
                              ("ocr", "preview"): "ocr_preview", ("ocr", "start"): "ocr_start",
                              ("ocr", "resume"): "ocr_resume"}[(kind, operation)]
                    self.send_json(getattr(editorial.pdf_sources.review, method)(payload))
                    return
                if request_path.startswith("/api/editorial/pdf/operations/"):
                    operation = request_path.rsplit("/", 1)[1]
                    if operation == "preview":
                        result = editorial.pdf_sources.operations.preview(payload)
                    elif operation == "start":
                        result = editorial.pdf_sources.operations.enqueue(payload)
                    else:
                        result = editorial.pdf_sources.operations.resume(payload)
                    self.send_json(result)
                    return
                if request_path.startswith("/api/editorial/workspace/"):
                    with editorial.lock:
                        operation = request_path.rsplit("/", 1)[1]
                        if operation == "preview":
                            result = editorial.workspace.preview(repository, payload)
                        elif operation == "save":
                            result = editorial.workspace.save(repository, payload)
                        elif operation == "promotion-preview":
                            result = editorial.workspace.promotion_preview(repository, editorial, payload)
                        else:
                            result = editorial.workspace.promote(repository, editorial, payload)
                    self.send_json(result)
                    return
                if request_path.startswith("/api/editorial/projects/"):
                    with editorial.lock:
                        snapshot = repository.catalog
                    operation = request_path.rsplit("/", 1)[1]
                    if operation == "activate":
                        if not isinstance(payload, dict) or set(payload) != {"project_id"}:
                            raise EditorialError("Escolha um projeto ou nenhum")
                        result = editorial.projects.activate(payload["project_id"])
                    elif operation == "preview":
                        result = editorial.projects.preview(payload, snapshot)
                    else:
                        result = editorial.projects.save(payload, snapshot)
                    self.send_json(result)
                    return
                if request_path == "/api/editorial/pdf/action":
                    # Extrações e consultas da oficina não seguram o bloqueio do catálogo.
                    with editorial.lock:
                        catalog_snapshot = repository.catalog
                    self.send_json(editorial.pdf_sources.action(payload, catalog_snapshot))
                    return
                with editorial.lock:
                    if self.path == "/api/editorial/batches/preview":
                        result = editorial.preview_batch(repository, payload)
                    elif self.path == "/api/editorial/documents/preview":
                        result = editorial.preview_document_creation(repository, payload)
                    elif self.path == "/api/editorial/collections/preview":
                        result = editorial.preview_collection(repository, payload)
                    elif self.path == "/api/editorial/translations/preview":
                        result = editorial.preview_translation(repository, payload)
                    elif self.path == "/api/editorial/passages/preview":
                        result = editorial.preview_passage(repository, payload)
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
            path = unquote(urlsplit(self.path).path)
            # Recursos estáticos e capacidades não leem o estado mutável do catálogo.
            # Uma conexão lenta não deve impedir o leitor de descobrir a edição local.
            if not path.startswith("/api/") or path == "/api/editorial/capabilities" or path.startswith("/api/editorial/pdf/") or path.startswith("/api/editorial/projects"):
                self.get_locked()
            else:
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
                if path in {"/editorial", "/editorial/", "/editorial/form", "/editorial/form/"}:
                    self.require_local_editorial()
                    page = (Path(__file__).parent / "editorial.html").read_bytes()
                    self.send_data(page, "text/html; charset=utf-8")
                elif path.startswith("/api/editorial/"):
                    self.require_local_editorial()
                    if path == "/api/editorial/workspace/document":
                        self.send_json(editorial.workspace.document(repository, params.get("project"), params.get("document")))
                    elif path == "/api/editorial/workspace/edition":
                        self.send_json(editorial.workspace.edition(repository, params.get("project"), params.get("edition")))
                    elif path == "/api/editorial/workspace/history":
                        self.send_json(editorial.workspace.history(repository, params.get("project"), params.get("edition")))
                    elif path == "/api/editorial/projects":
                        self.send_json(editorial.projects.listing())
                    elif path.startswith("/api/editorial/projects/"):
                        parts = path.removeprefix("/api/editorial/projects/").split("/")
                        if len(parts) == 2 and parts[1] == "history":
                            self.send_json(editorial.projects.history(parts[0]))
                        elif len(parts) == 1:
                            self.send_json(editorial.projects.get(parts[0]))
                        else:
                            raise EditorialError("Recurso de projeto não encontrado", 404)
                    elif path.startswith("/api/editorial/pdf/"):
                        suffix = path.removeprefix("/api/editorial/pdf/")
                        if suffix == "publication":
                            self.send_json(editorial.pdf_sources.publication.listing())
                        elif suffix.startswith("publication/") and suffix.endswith("/preview.pdf"):
                            parts=suffix.split("/")
                            self.send_pdf(None,file_path=editorial.pdf_sources.publication.preview_pdf(parts[1],params.get("link")),filename="previa-facsimile.pdf")
                        elif suffix == "links":
                            with editorial.lock:
                                self.send_json(editorial.pdf_sources.links.listing(repository, params))
                        elif suffix.startswith("links/") and suffix.endswith("/history"):
                            with editorial.lock:
                                self.send_json(editorial.pdf_sources.links.history(repository, suffix.split("/")[1]))
                        elif suffix == "operations":
                            self.send_json(editorial.pdf_sources.operations.listing(params))
                        elif suffix.startswith("operations/"):
                            self.send_json(editorial.pdf_sources.operations.get(suffix.removeprefix("operations/")))
                        elif suffix == "sources":
                            self.send_json(editorial.pdf_sources.listing())
                        elif suffix == "capabilities":
                            self.send_json(editorial.pdf_sources.capabilities())
                        else:
                            parts = suffix.split("/")
                            source_id = parts[0]
                            if len(parts) == 2 and parts[1] == "file":
                                self.send_pdf(source_id, download=params.get("download") == "1")
                            elif len(parts) == 2 and parts[1] == "history":
                                self.send_json(editorial.pdf_sources.history(source_id))
                            elif len(parts) == 2 and parts[1] == "review":
                                self.send_json(editorial.pdf_sources.review.overview(source_id))
                            elif len(parts) == 2 and parts[1] == "incorporations":
                                self.send_json(editorial.pdf_sources.incorporation.receipts(source_id))
                            elif len(parts) == 4 and parts[1] == "pages" and parts[3] == "geometry":
                                self.send_json(editorial.pdf_sources.alignment.geometry(source_id,int(parts[2])))
                            elif len(parts) == 4 and parts[1] == "pages" and parts[3] == "image.png":
                                self.send_data(editorial.pdf_sources.page_image(source_id,int(parts[2])).read_bytes(),"image/png")
                            elif len(parts) == 4 and parts[1] == "pages" and parts[3] == "review":
                                self.send_json(editorial.pdf_sources.review.page(source_id, int(parts[2])))
                            elif len(parts) == 3 and parts[1] == "pages":
                                self.send_json(editorial.pdf_sources.page(source_id, parts[2]))
                            elif len(parts) == 1:
                                self.send_json(editorial.pdf_sources.source(source_id))
                            else:
                                raise EditorialError("Recurso PDF não encontrado", 404)
                    elif path == "/api/editorial/capabilities":
                        self.send_json({"mode": "local_editorial",
                                        "features": ["translation_import", "markdown_edit", "reader_integration", "study_passage_edit", "pdf_sources", "pdf_review", "pdf_ocr", "pdf_document_links", "pdf_alignment", "pdf_incorporation", "static_facsimiles", "research_projects", "workspace_versions"]})
                    elif path == "/api/editorial/session":
                        self.send_json({"token": editorial.token, "statuses": STATUSES, "priorities": list(PRIORITIES), "revision": editorial.revision(),
                                        "features": ["translation_import", "markdown_edit", "reader_integration", "study_passage_edit", "catalog_intake", "batch_intake", "pdf_sources", "pdf_review", "pdf_ocr", "pdf_document_links", "pdf_alignment", "pdf_incorporation", "static_facsimiles", "research_projects", "workspace_versions"]})
                    elif path == "/api/editorial/queue":
                        self.send_json(editorial.queue(repository, params))
                    elif path == "/api/editorial/history":
                        self.send_json(editorial.history(params.get("document")))
                    elif path.startswith("/api/editorial/documents/"):
                        self.send_json(editorial.document(repository, path.removeprefix("/api/editorial/documents/")))
                    elif path.startswith("/api/editorial/collections/"):
                        self.send_json(editorial.collection(repository, path.removeprefix("/api/editorial/collections/")))
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

        def send_pdf(self, source_id, *, download=False, file_path=None, filename=None):
            source = editorial.pdf_sources.source(source_id) if file_path is None else {'filename':filename}
            path = editorial.pdf_sources.file_path(source_id) if file_path is None else file_path
            size = path.stat().st_size
            start, end, status = 0, size - 1, 200
            requested = self.headers.get("Range")
            if requested:
                match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested)
                if not match or not any(match.groups()):
                    raise EditorialError("Intervalo PDF inválido", 416)
                if match[1]:
                    start = int(match[1])
                    end = min(int(match[2]), size - 1) if match[2] else size - 1
                else:
                    start, end = max(0, size - int(match[2])), size - 1
                if not 0 <= start <= end < size:
                    raise EditorialError("Intervalo PDF indisponível", 416)
                status = 206
            try:
                self.connection.settimeout(30)
                self.send_response(status)
                self.send_header("Content-Type", "application/pdf")
                disposition = 'attachment' if download else 'inline'
                self.send_header("Content-Disposition", f"{disposition}; filename=\"fonte.pdf\"; filename*=UTF-8''{quote(source['filename'], safe='')}")
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Length", str(end - start + 1))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Security-Policy", "frame-ancestors 'self'")
                if status == 206:
                    self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.end_headers()
                if self.command == "HEAD":
                    return
                with path.open("rb") as stream:
                    stream.seek(start)
                    remaining = end - start + 1
                    while remaining:
                        chunk = stream.read(min(1024 * 1024, remaining))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
            except (ConnectionError, TimeoutError):
                self.close_connection = True

        def local_page(self):
            info = repository.info
            examples = [
                ("Abrir o site e o leitor existentes", "/"),
                ("Buscar no acervo", "/#/busca"),
                ("Bancada de pesquisa: documentos e Markdown", "/#/doc/showtrials-1665?bancada=1"),
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
            <title>Ambiente local — Documentos Soviéticos</title><link rel="stylesheet" href="/assets/style.css?v=carmim-1">
            <body><main class="local-guide"><a class="brand" href="/"><span class="brand-mark" aria-hidden="true">§</span><span class="brand-text"><strong>Documentos Soviéticos</strong><small>Ambiente local</small></span></a>
            <h1>Ambiente local do acervo</h1><p>{info['documents']} documentos · {info['editions']} versões por idioma · {info['collections']} coleções · {info['subcollections']} subcoleções.</p>
            <p>Consulte o site, use a busca e abra a área editorial para revisar pendências e editar metadados com prévia e histórico. Os endpoints da API apresentam JSON.</p><ul>{links}</ul>
            <p>Para encerrar, pressione <kbd>Ctrl+C</kbd> no terminal. As gravações da área editorial atualizam manifesto e busca automaticamente. Edições externas dos arquivos exigem reinicialização.</p></main></body></html>'''
            self.send_data(page.encode("utf-8"), "text/html; charset=utf-8")

        def static_file(self, path):
            if path in {"/prototipo", "/prototipo/ide"}:
                self.send_response(302)
                self.send_header("Location", path + "/")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            relative = path.lstrip("/") or "index.html"
            if relative in {"prototipo/", "prototipo/ide/"}:
                relative += "index.html"
            # Apenas os recursos publicados do site; não expõe temporario/, Git ou o banco.
            # Fontes já incorporadas à coleção de 1937; não abrir fontes/ em geral.
            legacy_pdfs = {"fontes/tukhachevsky/julgamento-1937-06-11.ru.pdf", "fontes/tukhachevsky/julgamento-1937-06-11.en.pdf"}
            prototype_files = {"prototipo/index.html", "prototipo/prototype.css", "prototipo/prototype.js",
                               "prototipo/ide/index.html", "prototipo/ide/workspace.css", "prototipo/ide/workspace.js"}
            if not (relative == "index.html" or relative in {"data/manifest.json","data/facsimiles.json"} or relative in prototype_files or relative in legacy_pdfs or relative.startswith(("assets/", "originais/"))):
                self.send_json({"error": "Recurso não publicado"}, 404)
                return
            if ".." in Path(relative).parts or "\\" in relative or any(part.startswith(".") for part in Path(relative).parts):
                self.send_json({"error": "Caminho inválido"}, 404)
                return
            target = (repository.root / relative).resolve()
            if not target.is_relative_to(repository.root.resolve()) or not target.is_file() or target.name.endswith(":Zone.Identifier"):
                self.send_json({"error": "Arquivo não encontrado"}, 404)
                return
            if relative in legacy_pdfs:
                self.send_pdf(None,file_path=target,filename=target.name)
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
        editorial.pdf_sources = PDFSources(root, start_worker=False)
        editorial.projects = ResearchProjects(root, editorial.pdf_sources)
        editorial.pdf_sources.operations.projects = editorial.projects
        editorial.workspace = WorkspaceEditions(editorial.projects)
        editorial.pdf_sources.links.projects = editorial.projects
        editorial.pdf_sources.links.workspace = editorial.workspace
        from .pdf_incorporation import PDFIncorporation
        editorial.pdf_sources.incorporation = PDFIncorporation(editorial.pdf_sources,editorial,editorial.workspace)
        from .pdf_publication import PDFPublication
        editorial.pdf_sources.publication = PDFPublication(editorial.pdf_sources,editorial)
        server = LocalServer((host, port), handler_for(repository, editorial))
        editorial.pdf_sources.start()
    except Exception:
        if hasattr(editorial, "pdf_sources"):
            editorial.pdf_sources.close()
        editorial.close()
        raise
    server.repository = repository
    server.editorial = editorial
    server.pdf_sources = editorial.pdf_sources
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
