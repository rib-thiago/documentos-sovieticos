#!/usr/bin/env python3
"""Coletor do corpus Brest-Litovsk: inventário, descoberta controlada e aquisição local.

Não publica conteúdos no site e não faz tradução/OCR. Não ignora robots.txt.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import requests
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as to_markdown

BASE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = BASE.parents[2] / "temporario" / "coletas-quatro" / "brest"
UA = "BrestLitovskResearchCollector/0.1 (personal historical archive; polite crawler)"
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/pdf;q=0.8,*/*;q=0.5"}
AGENT_ROBOTS = "BrestLitovskResearchCollector"
MAX_BYTES = 60 * 1024 * 1024
URL_EXT = (".htm", ".html", ".shtml")


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def canonical(url: str) -> str:
    url, _ = urldefrag(url)
    p = urlparse(url.strip())
    return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path or "/", "", p.query, ""))


def ident(url: str) -> str:
    """Identificador determinístico por URL; nunca muda caso o título seja editado."""
    return hashlib.sha256(canonical(url).encode("utf-8")).hexdigest()[:14]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "-", value)[:80]


def html_root(html: bytes, origin: str = "") -> tuple[str, str]:
    """Extrai Markdown e título sem alterar o arquivo HTML original.

    A versão Markdown é derivada e exige revisão antes de publicação.
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag, attr in (("a", "href"), ("img", "src")):
        for el in soup.find_all(tag):
            value = el.get(attr, "")
            if value:
                el[attr] = urljoin(origin, value)
    title = (soup.find("h1") or soup.find("h2") or soup.title)
    page_title = title.get_text(" ", strip=True) if title else "Sem título identificado"
    for el in soup.find_all(["script", "style", "noscript", "form", "nav", "footer"]):
        el.decompose()
    for el in soup.select(".topnav, .navbar, .toplink, #navbar, #navigation, .cookie-consent"):
        el.decompose()
    candidates = [soup.select_one(sel) for sel in
                  ("article", "main", "#mainContent", "#content", "#main", ".main-content", ".content")]
    candidates = [c for c in candidates if c is not None]
    root = max(candidates, key=lambda x: len(x.get_text(" ", strip=True)), default=soup.body or soup)
    markdown = to_markdown(str(root), heading_style="ATX", bullets="-", strip=["font"])
    markdown = re.sub(r"\n{4,}", "\n\n\n", markdown).strip() + "\n"
    return page_title, markdown


def structure_diagnostics(raw: bytes) -> dict:
    soup = BeautifulSoup(raw, "html.parser")
    numbered = []
    for paragraph in soup.find_all("p"):
        match = re.match(r"^(\d{1,3})\.\s", paragraph.get_text(" ", strip=True))
        if match:
            numbered.append(int(match.group(1)))
    gaps = [{"apos": left, "proximo": right} for left, right in zip(numbered, numbered[1:]) if right > left + 1]
    return {
        "paragrafos_html": len(soup.find_all("p")),
        "tabelas_html": len(soup.find_all("table")),
        "ancoras_html": len(soup.select("a[id],a[name]")),
        "saltos_numeracao_observados": gaps,
        "politica_notas": "Texto das notas preservado; links de fragmento apontam à fonte. Converter para notas locais na preparação editorial.",
    }


def discover_links(html: bytes, origin: str, prefix: str,
                   extensions: list[str], anchor_pattern: str | None = None) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    found: dict[str, str] = {}
    for a in soup.select("a[href]"):
        text = a.get_text(" ", strip=True)
        href = canonical(urljoin(origin, a.get("href", "")))
        p = urlparse(href)
        if p.scheme not in {"http", "https"}:
            continue
        if not href.startswith(prefix):
            continue
        if not any(p.path.lower().endswith(x) for x in extensions):
            continue
        if anchor_pattern and not re.search(anchor_pattern, text, re.IGNORECASE):
            continue
        if href != canonical(origin) and href not in found:
            found[href] = text or p.path.rsplit("/", 1)[-1]
    return list(found.items())


class PoliteFetch:
    def __init__(self, delay: float = 3, timeout: int = 20):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.delay = delay
        self.timeout = timeout
        self.last: dict[str, float] = {}
        self.robots: dict[str, RobotFileParser | None] = {}
        self.cache: dict[str, tuple[bytes, str]] = {}
        self.final_urls: dict[str, str] = {}

    def pause(self, host: str) -> None:
        elapsed = time.monotonic() - self.last.get(host, -1e7)
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last[host] = time.monotonic()

    def robot(self, url: str) -> bool:
        p = urlparse(url)
        host = f"{p.scheme}://{p.netloc}"
        if host not in self.robots:
            robots_url = host + "/robots.txt"
            try:
                self.pause(host)
                r = self.session.get(robots_url, timeout=self.timeout)
                if r.status_code == 404 or r.status_code == 410:
                    self.robots[host] = None  # não existe robots.txt
                elif r.status_code == 200:
                    rp = RobotFileParser()
                    rp.parse(r.text.splitlines())
                    self.robots[host] = rp
                else:
                    raise RuntimeError(f"robots.txt com status {r.status_code}")
            except requests.RequestException as exc:
                raise RuntimeError(f"robots.txt inacessível: {exc}") from exc
        rp = self.robots[host]
        return rp is None or rp.can_fetch(AGENT_ROBOTS, url)

    def get(self, url: str) -> tuple[bytes, str]:
        url = canonical(url)
        if url in self.cache:
            return self.cache[url]
        if not self.robot(url):
            raise PermissionError(f"Robots proíbe a URL: {url}")
        p = urlparse(url)
        host = f"{p.scheme}://{p.netloc}"
        self.pause(host)
        with self.session.get(url, timeout=self.timeout, stream=True, allow_redirects=True) as r:
            if r.status_code == 429:
                raise RuntimeError("HTTP 429: limite do site; interrompa e tente mais tarde")
            r.raise_for_status()
            if urlparse(r.url).netloc.lower() != p.netloc.lower():
                # Evitar download inadvertido por redirecionamento externo.
                raise RuntimeError(f"Redirecionamento para outro host: {r.url}")
            ctype = r.headers.get("Content-Type", "").split(";", 1)[0].lower()
            if not ("html" in ctype or "pdf" in ctype or ctype == "application/octet-stream"):
                raise ValueError(f"Tipo MIME inesperado: {ctype}")
            chunks: list[bytes] = []
            size = 0
            for chunk in r.iter_content(64 * 1024):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise ValueError("Documento excede limite de 60 MiB")
                chunks.append(chunk)
            body = b"".join(chunks)
            if not body:
                raise ValueError("Resposta vazia")
            if body.lstrip()[:50].lower().startswith(b"<html") or "html" in ctype:
                if "access denied" in body[:3000].decode("utf-8", "ignore").lower():
                    raise PermissionError("Página com aviso de acesso negado")
            self.cache[url] = body, ctype
            self.final_urls[url] = r.url
            return body, ctype


def initial_sources() -> list[dict]:
    return load_yaml(BASE / "fontes.yml")["fontes"]


def sources_by_url(src: list[dict]) -> dict[str, dict]:
    items: dict[str, dict] = {}
    for source in src:
        url = canonical(source["url"])
        if url not in items:
            items[url] = dict(source)
            items[url]["url"] = url
            items[url]["grupos"] = [source["grupo"]]
            items[url]["ocorrencias"] = [dict(source)]
        else:
            items[url].setdefault("outras_referencias", []).append(source["id"])
            if source["grupo"] not in items[url]["grupos"]:
                items[url]["grupos"].append(source["grupo"])
            items[url]["ocorrencias"].append(dict(source))
    return items


def build_inventory(fetcher: PoliteFetch, do_discover: bool, limit: int = 0, group: str | None = None):
    items = sources_by_url(initial_sources())
    incidents: list[dict] = []
    if do_discover:
        for entry in load_yaml(BASE / "descoberta.yml")["indices"]:
            if group and entry["grupo"] != group:
                continue
            prefix = entry["prefixo_url"]
            depth_max = entry.get("profundidade", 1)
            extensions = entry.get("extensoes", list(URL_EXT))
            limit_index = entry.get("limite", 200)
            queue = deque([(entry["url"], 0)])
            visited = set()
            count = 0
            while queue and count < limit_index:
                url, depth = queue.popleft()
                url = canonical(url)
                if url in visited or depth >= depth_max:
                    continue
                visited.add(url)
                try:
                    body, ctype = fetcher.get(url)
                    if "html" not in ctype and not body.lstrip().startswith(b"<"):
                        continue
                    # O filtro do primeiro nível vale apenas para caminhos pelo índice inicial.
                    pattern = entry.get("texto_ancora_primeiro_nivel") if depth == 0 else None
                    if entry.get("texto_ancora"):
                        pattern = entry["texto_ancora"]
                    links = discover_links(body, url, prefix, extensions, pattern)
                    for target, title in links:
                        if target not in items:
                            items[target] = {
                                "id": f"d-{ident(target)}", "titulo": title,
                                "url": target, "grupo": entry["grupo"],
                                "idioma": entry["idioma"], "tipo": "html",
                                "estado": "descoberto_no_indice",
                                "indice_origem": entry["id"],
                                "grupos": [entry["grupo"]],
                                "ocorrencias": [],
                            }
                        elif entry["grupo"] not in items[target].setdefault("grupos", [items[target]["grupo"]]):
                            items[target]["grupos"].append(entry["grupo"])
                        occurrence = {"indice_origem": entry["id"], "grupo": entry["grupo"], "titulo": title}
                        if occurrence not in items[target].setdefault("ocorrencias", []):
                            items[target]["ocorrencias"].append(occurrence)
                        if depth + 1 < depth_max and target not in visited:
                            queue.append((target, depth + 1))
                        count += 1
                        if count >= limit_index:
                            break
                except Exception as exc:
                    incidents.append({"index": entry["id"], "url": url, "erro": str(exc)})
    result = [s for s in items.values() if not group or group in s.get("grupos", [s["grupo"]])]
    if limit:
        result = result[:limit]
    return result, incidents


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def immutable(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as stream:
            stream.write(data)
    except FileExistsError:
        if path.read_bytes() != data:
            raise ValueError(f"Colisão ou alteração em snapshot preservado: {path}")


def process(source: dict, fetcher: PoliteFetch, output: Path, refresh: bool) -> dict:
    url = source["url"]
    name = safe_id(source["id"])
    group = source["grupo"]
    meta_path = output / "meta" / group / f"{name}.json"
    md_path = output / "md" / group / f"{name}.{source['idioma']}.md"
    raw_base = output / "raw" / group / name
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    row = dict(source)
    row["coletado_em"] = datetime.now(timezone.utc).isoformat()
    previous = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    if previous:
        old = json.dumps(previous, ensure_ascii=False, sort_keys=True).encode("utf-8")
        immutable(output / "historico" / name / (sha(old) + ".json"), old)
    if previous and not refresh and previous.get("estado_aquisicao") != "ERROR":
        previous.update({key: source[key] for key in ("grupos", "ocorrencias", "outras_referencias") if key in source})
        atomic_json(meta_path, previous)
        return previous
    if source["tipo"] in {"registro", "indice"}:
        row["estado_aquisicao"] = "METADATA_ONLY" if source["tipo"] == "registro" else "INDEX_ONLY"
    else:
        try:
            raw, ctype = fetcher.get(url)
            extension = ".pdf" if ("pdf" in ctype or raw.startswith(b"%PDF")) else ".html"
            raw_path = raw_base / (sha(raw) + extension)
            immutable(raw_path, raw)
            row["raw_path"] = str(raw_path.relative_to(output))
            row["checksum_raw_sha256"] = sha(raw)
            row["mime"] = ctype
            row["bytes"] = len(raw)
            row["url_final"] = getattr(fetcher, "final_urls", {}).get(canonical(url), url)
            if extension == ".html":
                title, markdown = html_root(raw, row["url_final"])
                text_hash = sha(markdown.encode("utf-8"))
                candidate = output / "candidatos" / group / name / (text_hash + f".{source['idioma']}.md")
                immutable(candidate, markdown.encode("utf-8"))
                md_path.parent.mkdir(parents=True, exist_ok=True)
                if not md_path.exists():
                    immutable(md_path, markdown.encode("utf-8"))
                row["titulo_extraido"] = title
                row["md_path"] = str(md_path.relative_to(output))
                row["candidate_path"] = str(candidate.relative_to(output))
                row["checksum_texto_sha256"] = sha(md_path.read_bytes())
                row["checksum_candidato_sha256"] = text_hash
                row["derivado_diverge_do_candidato"] = row["checksum_texto_sha256"] != text_hash
                row["estado_aquisicao"] = "FOUND_HTML_UNREVIEWED"
                row["pendencias"] = ["Conferir fronteiras, notas e integralidade antes de incorporar."]
                row["diagnostico_estrutura"] = structure_diagnostics(raw)
                if row["diagnostico_estrutura"]["saltos_numeracao_observados"]:
                    row["pendencias"].append("Há salto em parágrafos numerados na fonte: conferir sem completar ou renumerar silenciosamente.")
                if len(markdown.strip()) < 300:
                    row["pendencias"].append("Texto curto: pode ser índice, bloqueio ou extração incompleta.")
                if row["derivado_diverge_do_candidato"]:
                    row["pendencias"].append("Markdown de trabalho preservado; novo candidato exige comparação.")
            else:
                row["estado_aquisicao"] = "FOUND_SCAN_UNREVIEWED"
        except Exception as exc:
            row["estado_aquisicao"] = "ERROR"
            row["erro"] = str(exc)
            if previous and previous.get("estado_aquisicao") != "ERROR":
                previous["ultima_tentativa_falha"] = {"quando": row["coletado_em"], "erro": str(exc)}
                row = previous
    # Todos os status de tradução começam vazios; sem criação de versões falsas.
    row.setdefault("status_traducao", "NAO_INICIADA")
    atomic_json(meta_path, row)
    return row


def save_report(output: Path, records: list[dict], incidents: list[dict]):
    output.mkdir(parents=True, exist_ok=True)
    path = output / "inventario.json"
    existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    merged = {canonical(row["url"]): row for row in existing}
    for row in records:
        key = canonical(row["url"])
        if row.get("estado_aquisicao") == "PLANEJADO" and merged.get(key, {}).get("estado_aquisicao") not in (None, "PLANEJADO"):
            continue
        merged[key] = row
    records = list(merged.values())
    atomic_json(path, records)
    columns = ("id", "grupo", "idioma", "tipo", "estado_aquisicao", "titulo", "url", "md_path", "raw_path", "checksum_raw_sha256", "erro")
    with (output / "catalogo.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for row in records:
            w.writerow(row)
    error_path = output / "erros_descoberta.json"
    old_errors = json.loads(error_path.read_text(encoding="utf-8")) if error_path.exists() else []
    atomic_json(error_path, old_errors + incidents)


def reprocess_local(source: dict, output: Path) -> dict:
    meta_path = output / "meta" / source["grupo"] / (safe_id(source["id"]) + ".json")
    previous = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    if not previous.get("raw_path"):
        return previous or {**source, "estado_aquisicao": "PLANEJADO"}
    raw_path = output / previous["raw_path"]
    if not raw_path.resolve().is_relative_to(output.resolve()):
        raise ValueError("Fonte local fora da área de trabalho")
    class LocalFetch:
        final_urls = {canonical(source["url"]): previous.get("url_final", source["url"])}

        def get(self, url):
            data = raw_path.read_bytes()
            if sha(data) != previous["checksum_raw_sha256"]:
                raise ValueError("Hash da fonte local diverge do inventário")
            return data, previous["mime"]
    row = process(source, LocalFetch(), output, True)
    row["reprocessado_em"] = row["coletado_em"]
    row["coletado_em"] = previous["coletado_em"]
    atomic_json(meta_path, row)
    return row


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coletor local Brest-Litovsk")
    parser.add_argument("comando", choices=["planejar", "descobrir", "coletar", "converter", "relatorio"])
    parser.add_argument("--saida", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--atraso", type=float, default=3.0, help="Segundos entre requisições ao mesmo host")
    parser.add_argument("--limite", type=int, default=0, help="Limite de documentos (0=todos)")
    grupos = [g["id"] for g in load_yaml(BASE / "colecao.yml")["organizacao"]]
    parser.add_argument("--grupo", choices=grupos, help="Restringir a uma subcoleção, inclusive sua descoberta")
    parser.add_argument("--id", action="append", dest="ids", help="Selecionar fonte por ID; pode repetir")
    parser.add_argument("--somente-sementes", action="store_true", help="Não expandir índices pela internet")
    parser.add_argument("--atualizar", action="store_true", help="Obter novo snapshot/candidato sem substituir o Markdown de trabalho")
    args = parser.parse_args(argv)
    if args.atraso < 1:
        parser.error("Atraso mínimo de 1 segundo por host")
    if args.comando == "relatorio":
        path = args.saida / "inventario.json"
        if not path.is_file():
            print("Nenhum inventário existente. Execute 'planejar' primeiro.")
            return 1
        rows = json.loads(path.read_text(encoding="utf-8"))
        from collections import Counter
        for k, n in sorted(Counter(x.get("estado_aquisicao", "PLANEJADO") for x in rows).items()):
            print(f"{k}: {n}")
        print(f"Total: {len(rows)}")
        return 0
    online = args.comando in ("descobrir", "coletar") and not args.somente_sementes
    fetcher = PoliteFetch(delay=args.atraso)
    documents, incidents = build_inventory(fetcher, do_discover=online, limit=args.limite, group=args.grupo)
    if args.ids:
        known = {s["id"] for s in documents}
        if set(args.ids) - known:
            parser.error("ID não encontrado na seleção: " + ", ".join(sorted(set(args.ids) - known)))
        documents = [s for s in documents if s["id"] in args.ids]
    rows = []
    for i, source in enumerate(documents, start=1):
        if args.comando == "coletar":
            record = process(source, fetcher, args.saida, refresh=args.atualizar)
        elif args.comando == "converter":
            record = reprocess_local(source, args.saida)
        else:
            record = {**source, "estado_aquisicao": "PLANEJADO"}
        rows.append(record)
        print(f"[{i}/{len(documents)}] {record['estado_aquisicao']}: {source['id']}", flush=True)
    save_report(args.saida, rows, incidents)
    print(f"Inventário: {args.saida / 'catalogo.csv'}; erros de descoberta: {len(incidents)}")
    return 1 if incidents or any(row.get("estado_aquisicao") == "ERROR" for row in rows) else 0


if __name__ == "__main__":
    sys.exit(run())
