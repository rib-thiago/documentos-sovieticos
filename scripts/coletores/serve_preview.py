#!/usr/bin/env python3
"""Abre a prévia das coleções em leitura, sem mudar ou editar o acervo local."""
from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from preview_catalog import ROOT, model


def resolve_public(root, package, request_path):
    path = unquote(urlsplit(request_path).path)
    if "\\" in path or "\x00" in path:
        return None
    parts = PurePosixPath(path).parts
    if ".." in parts:
        return None
    relative = path.lstrip("/") or "index.html"
    first = relative.split("/", 1)[0]
    if relative != "index.html" and first not in {"assets", "originais", "data"}:
        return None
    if first == "data" and relative != "data/manifest.json" and relative not in {f"data/catalog/{name}.json" for name in model.FILES}:
        return None
    for base in (package / "files", root):
        candidate = (base / relative).resolve()
        if candidate.is_relative_to(base.resolve()) and candidate.is_file():
            return candidate
    return None


def handler(root, package):
    class PreviewHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            target = resolve_public(root, package, self.path)
            if target is None:
                self.send_error(404, "Recurso indisponível na prévia de leitura")
                return
            data = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(str(target)))
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_HEAD(self):
            target = resolve_public(root, package, self.path)
            if target is None:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(str(target)))
            self.send_header("Content-Length", str(target.stat().st_size))
            self.end_headers()

        def do_POST(self):
            self.send_error(405, "A prévia permite apenas leitura")

        do_PUT = do_POST
        do_DELETE = do_POST
        do_PATCH = do_POST
    return PreviewHandler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path, default=ROOT / "temporario/coletas-quatro")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    latest = json.loads((args.workdir / "preview-latest.json").read_text(encoding="utf-8"))
    package = Path(latest["package"]).resolve()
    if not package.is_relative_to((args.workdir / "preview").resolve()):
        parser.error("Pacote fora da área de prévia")
    current = model.load(ROOT)
    fingerprint = model.sha256(b"\0".join(model.json_bytes(current[name]) for name in model.FILES))
    if fingerprint != latest["base_catalog_sha256"]:
        parser.error("O catálogo mudou desde a prévia; gere-a novamente antes de abrir")
    print(f"Prévia de leitura: http://127.0.0.1:{args.port}/", flush=True)
    print("Catálogo público e área editorial permanecem separados. Ctrl+C encerra.", flush=True)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler(ROOT, package))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
