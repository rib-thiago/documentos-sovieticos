#!/usr/bin/env python3
"""Adquire o recorte militar de 1934–1936 em .local/research; não publica.

Dependências de coleta são isoladas do backend. Preserva respostas antes de
qualquer extração e registra falhas sem criar supostos documentos vazios.
"""
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.robotparser import RobotFileParser

import requests

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".local/research/military-1934-1936"
KIT = ROOT / "data/research/military-1934-1936.json"
UA = "SovietDocumentsResearch/1.0"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", action="append")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--wayback", action="store_true", help="Obtém captura pública e registra data/URL do arquivo")
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    raw_dir = WORK / "raw"
    raw_dir.mkdir(exist_ok=True)
    items = json.loads(KIT.read_text())
    if any(row["collection"] not in {"conselho-1935", "industria"} for row in items):
        raise ValueError("Inventário contém documentos fora do recorte autorizado")
    (WORK / "inventory.json").write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept-Language": "ru,en;q=0.5"})
    robots_file = WORK / "robots.txt"
    if not robots_file.exists():
        response = session.get("https://istmat.org/robots.txt", timeout=(15, 45))
        response.raise_for_status()
        robots_file.write_bytes(response.content)
    robots = RobotFileParser()
    robots.parse(robots_file.read_text().splitlines())
    pause = max(10, robots.crawl_delay(UA) or 0)
    for row in items:
        if args.id and row["id"] not in args.id:
            continue
        metadata_file = WORK / (row["id"] + ".json")
        if metadata_file.exists():
            old = json.loads(metadata_file.read_text())
            if old.get("status") == "acquired" or not args.retry_failed:
                print("SKIP", row["id"], old.get("status"), flush=True)
                continue
        metadata = {"inventory": row, "attempted_at": datetime.now(timezone.utc).isoformat(), "attempts": []}
        if not robots.can_fetch(UA, row["url"]):
            metadata.update(status="failed", error="robots.txt não permite a coleta")
        else:
            print("GET", row["id"], row["url"], flush=True)
            try:
                target = row["url"]
                metadata["original_url"] = row["url"]
                if args.wayback:
                    cdx = session.get("https://web.archive.org/cdx/search/cdx", params={
                        "url": row["url"].split("://", 1)[-1], "output": "json",
                        "filter": ["statuscode:200", "mimetype:text/html"], "collapse": "digest",
                        "fl": "timestamp,original", "limit": "-3"}, timeout=(15, 45))
                    cdx.raise_for_status()
                    (WORK / (row["id"] + ".cdx.json")).write_bytes(cdx.content)
                    captures = cdx.json()
                    if len(captures) < 2:
                        raise ValueError("Nenhuma captura HTML com status 200 localizada no Wayback")
                    timestamp, original = captures[-1]
                    target = f"https://web.archive.org/web/{timestamp}id_/{original}"
                    metadata.update(provider="Wayback Machine", capture_timestamp=timestamp,
                                    captured_original_url=original, archive_url=f"https://web.archive.org/web/{timestamp}/{original}")
                    time.sleep(pause)
                response = session.get(target, timeout=(15, 60), stream=True)
                response.raise_for_status()
                payload = bytearray()
                for chunk in response.iter_content(65536):
                    payload.extend(chunk)
                    if len(payload) > 25 * 1024 * 1024:
                        raise ValueError("Resposta excedeu 25 MiB")
                raw = bytes(payload)
                path = raw_dir / (row["id"] + ".html")
                path.write_bytes(raw)
                metadata.update(status="acquired", final_url=response.url, status_code=response.status_code,
                                content_type=response.headers.get("Content-Type"), file=str(path.relative_to(ROOT)),
                                bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                print("SAVED", row["id"], len(raw), flush=True)
                response.close()
            except (requests.RequestException, OSError, ValueError) as error:
                metadata.update(status="failed", error=str(error))
                print("FAILED", row["id"], str(error), flush=True)
        if metadata_file.exists():
            previous = json.loads(metadata_file.read_text())
            metadata["attempts"] = previous.get("attempts", []) + [{"attempted_at": previous.get("attempted_at"), "status": previous.get("status"), "error": previous.get("error")}]
        metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
        time.sleep(pause)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit("Coleta interrompida; aquisições e registros concluídos foram preservados.")
