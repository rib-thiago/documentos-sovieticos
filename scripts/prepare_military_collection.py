#!/usr/bin/env python3
"""Prepara fontes militares adquiridas; --apply cadastra em transação local.

Sem testes, servidor ou Git. A aquisição é feita separadamente. Por padrão,
apenas prepara Markdown e relatório, sem alterar o acervo publicado.
"""
import argparse
import copy
import csv
import io
import importlib.metadata
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup, UnicodeDammit
from markdownify import markdownify

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import catalog as model
from backend.database import Repository
from backend.editorial import Editorial

WORK = ROOT / ".local/research/military-1934-1936"
REPORT = ROOT / "docs/pesquisa/colecao-militar-1934-1936"
INVENTORY = ROOT / "data/research/military-1934-1936.json"
COLLECTION = "exercito-industria-defesa-1934-1936"
SUBS = {"conselho-1935": ("conselho-militar-1935", "Conselho Militar de dezembro de 1935"),
        "industria": ("industria-defesa-1934-1936", "Indústria e abastecimento de defesa")}
TYPES = {"stenogram": "session_transcript", "minutes": "session_transcript",
         "order": "plan_instruction", "memorandum": "memo_note", "decree": "decree_resolution"}
REVIEWED_HEADINGS = {"nko35-08-am": {
    "Оперативная подготовка комсостава, начсостава и штабов", "По тактической подготовке",
    "Огневая подготовка", "По подготовке родов войск", "Задачи на 1936 г.",
    "Вопросы управления", "Белорусский военный округ", "Вопросы тыла",
    "Отрицательные моменты в нашей работе", "Общие выводы",
}}


def table_markdown(table, number):
    """Expande a grade HTML, combina níveis de cabeçalho e mantém dados sem duplicar números."""
    rows = [tr for tr in table.find_all("tr") if tr.find_parent("table") is table]
    matrix = [tr.find_all(["td", "th"], recursive=False) for tr in rows]
    if not matrix or not matrix[0]:
        raise ValueError("Tabela sem células identificáveis; conversão manual necessária")
    def cell_text(cell):
        return markdownify(cell.decode_contents(), heading_style="ATX").strip().replace("\n", " ").replace("|", r"\|")
    grid = {}
    merged = False
    for r, cells in enumerate(matrix):
        c = 0
        for cell in cells:
            while (r, c) in grid:
                c += 1
            rowspan, colspan = int(cell.get("rowspan", 1)), int(cell.get("colspan", 1))
            if not 1 <= rowspan <= len(rows) or not 1 <= colspan <= 100:
                raise ValueError("Dimensão de célula exige conferência manual")
            merged |= rowspan > 1 or colspan > 1
            owner = (r, c, cell_text(cell))
            for rr in range(r, min(r + rowspan, len(rows))):
                for cc in range(c, c + colspan):
                    if (rr, cc) in grid:
                        raise ValueError("Sobreposição de células na tabela; conferir o HTML")
                    grid[rr, cc] = owner
            c += colspan
    width = max(c for _, c in grid) + 1
    header_rows = max(int(cell.get("rowspan", 1)) for cell in matrix[0])
    if header_rows > 4 or header_rows >= len(rows):
        raise ValueError("Fronteira de cabeçalho da tabela ambígua; requer conversão manual")
    header = []
    for c in range(width):
        parts = []
        for r in range(header_rows):
            value = grid.get((r, c), (0, 0, ""))[2]
            if value and value not in parts:
                parts.append(value)
        header.append(" / ".join(parts) or ("Показатель" if c == 0 else f"Столбец {c+1}"))
    result = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    caption = table.find("caption", recursive=False)
    if caption:
        result.insert(0, "**" + cell_text(caption) + "**\n")
    for r in range(header_rows, len(rows)):
        values = []
        for c in range(width):
            owner = grid.get((r, c))
            values.append("" if owner is None else owner[2] if owner[:2] == (r, c) else "↳")
        result.append("| " + " | ".join(values) + " |")
    if merged:
        result.append("\n*Примечание к представлению: уровни заголовков объединены через « / ». Знак ↳ обозначает продолжение объединённой ячейки источника; её значение не дублируется. Исходная разметка сохранена в HTML.*")
    note = f"Tabela {number}: grade de {len(rows)} linhas e {width} colunas, {header_rows} linha(s) de cabeçalho. Cotejar números, unidades e cabeçalhos."
    if merged:
        note += " Cabeçalhos compostos e continuação de células mescladas representados em Markdown; HTML preservado."
    return "\n".join(result), "alta", note


def convert(row, metadata):
    path = ROOT / metadata["file"]
    raw = path.read_bytes()
    if model.sha256(raw) != metadata["sha256"]:
        raise ValueError("Cópia HTML alterada desde a aquisição")
    decoded = UnicodeDammit(raw, is_html=True).unicode_markup
    if decoded is None:
        raise ValueError("Não foi possível determinar a codificação")
    soup = BeautifulSoup(decoded, "html.parser")
    source_title = soup.select_one("h1#page-title, h1.title, h1")
    title = source_title.get_text(" ", strip=True) if source_title else row["title_ru"]
    source = soup.select_one(".field-name-body .field-item, .field-name-body")
    if source is None or len(source.get_text(" ", strip=True)) < 90:
        raise ValueError("Corpo documental não identificado; HTML mantido, sem publicar navegação como documento")
    section = BeautifulSoup(str(source), "html.parser")
    for unwanted in section.select("script,style,form,iframe,nav,.share-buttons,.social-share"):
        unwanted.decompose()
    source_text = section.get_text(" ", strip=True)
    promoted = []
    for paragraph in section.select("p.rtecenter,p[align='center']"):
        text = paragraph.get_text(" ", strip=True)
        if text in REVIEWED_HEADINGS.get(row["id"], set()):
            paragraph.name = "h2"
            promoted.append(text)
    # Notas Word/Drupal: só deslocar definições que tenham chamada identificável.
    # Sem pareamento, conservar o bloco original em vez de descartar uma nota.
    footnotes, footnote_tokens = [], {}
    for definition in list(section.select("div[id]")):
        match = re.fullmatch(r"ftn(\d+)", definition.get("id", ""))
        if not match:
            continue
        number = match.group(1)
        calls = section.select(f'a[href="#_ftn{number}"]')
        if not calls or definition.select("table"):
            continue
        for back in definition.select(f'a[href="#_ftnref{number}"]'):
            back.decompose()
        for link in definition.select("a[href]"):
            link["href"] = urljoin(metadata.get("captured_original_url", metadata.get("original_url", metadata["final_url"])), link["href"])
        note = markdownify(str(definition), heading_style="ATX", bullets="-").strip()
        footnotes.append(f"[^{number}]: " + note.replace("\n", "\n    "))
        token = f"MILITARYFOOTNOTEREF{number}END"
        footnote_tokens[token] = f"[^{number}]"
        for call in calls:
            call.replace_with(section.new_string(token))
        definition.decompose()
    for tag in section.select("a[href],img[src]"):
        attr = "href" if tag.name == "a" else "src"
        relative = tag[attr]
        if metadata.get("archive_url") and relative.startswith("#"):
            tag[attr] = metadata["archive_url"] + relative
        else:
            tag[attr] = urljoin(metadata.get("captured_original_url", metadata.get("original_url", metadata["final_url"])), relative)
    flags = []
    if row["id"] == "nko35-protocol":
        flags.append({"priority": "media", "reason": "O corpo indica 'não posterior a 8 de dezembro de 1935', enquanto o título cobre o Conselho de 8–14/12. As formulações foram preservadas; conferir a data catalogada."})
    if footnotes:
        flags.append({"priority": "media", "reason": f"{len(footnotes)} notas convertidas para sintaxe Markdown; cotejar chamadas, definições e navegação."})
    replacements = {}
    tables = list(section.select("table"))
    for number, table in enumerate(tables, 1):
        rendered, priority, note = table_markdown(table, number)
        token = f"MILITARYTABLEPLACEHOLDER{number}END"
        replacements[token] = rendered
        flags.append({"priority": priority, "reason": note})
        table.replace_with(section.new_string("\n\n" + token + "\n\n"))
    if section.select("sup,[id],a[href*='#']"):
        flags.append({"priority": "media", "reason": "Conferir notas, chamadas e âncoras; links relativos apontam para a fonte original."})
    if section.select("img"):
        flags.append({"priority": "alta", "reason": "Fonte contém imagem; conteúdo gráfico não recebeu OCR nem foi presumido transcrito."})
    converted = markdownify(str(section), heading_style="ATX", bullets="-", escape_underscores=False).strip()
    for token, rendered in replacements.items():
        converted = converted.replace(token, rendered)
    for token, rendered in footnote_tokens.items():
        converted = converted.replace(token, rendered)
    if footnotes:
        converted += "\n\n" + "\n\n".join(footnotes)
    content = "# " + title + "\n\n" + converted + "\n"
    archive = soup.select_one(".field-name-field-archive .field-item")
    publication = soup.select_one(".field-name-field-source .field-item")
    date_field = soup.select_one(".field-name-field-date .field-item")
    source_date = date_field.get_text(" ", strip=True) if date_field else None
    if source_date and row["date"].replace("-", ".") not in source_date:
        flags.append({"priority": "alta", "reason": f"Data na fonte ({source_date}) difere da indicação do inventário ({row['date']}); conferir sem corrigir o texto."})
    detail = {"source_title": title, "source_text_characters": len(source_text),
              "source_start": source_text[:240], "source_end": source_text[-240:],
              "tables": len(tables), "footnotes": len(footnotes), "reviewed_headings": promoted, "flags": flags,
              "archive_reference": archive.get_text(" ", strip=True) if archive else None,
              "source_date": source_date,
              "publication": publication.get_text(" ", strip=True) if publication else row["edition"],
              "recipe": "military-html-v1", "source_sha256": metadata["sha256"],
              "dependencies": {package: importlib.metadata.version(package) for package in ("beautifulsoup4", "markdownify")},
              "content_sha256": model.sha256(content.encode())}
    return content, detail


def collection_record(slug, title, position, parent=None):
    description = "Documentos do Conselho Militar de 1935 e da indústria de defesa de 1934–1936, em russo. Inclui notas e referências das edições publicadas."
    if parent and slug == "conselho-militar-1935":
        description = "Sessões e segmentos temáticos, ata e ordens relacionadas ao Conselho Militar de dezembro de 1935, preservando a divisão das páginas da fonte."
    elif parent:
        description = "Relatórios, memorandos e resoluções de 1934–1936 sobre aviação, armamentos, matérias-primas e indústria de defesa."
    return {"id": parent + "/" + slug if parent else slug, "slug": slug, "parent_id": parent,
            "position": position, "titles": {"pt": title}, "subtitle": "Documentação em russo",
            "description": description,
            "source": {}, "presentation": {}, "extra": {},
            "compatibility_fields": ["id", "title_pt", "subtitle_pt", "description_pt", "document_ids" if parent else "documents"]}


def apply(prepared):
    editorial = Editorial(ROOT)
    try:
        current = model.load(ROOT)
        candidate = copy.deepcopy(current)
        if any(c["id"] == COLLECTION for c in current["collections"]):
            raise model.CatalogError("Coleção já existe; não sobrescrevendo edições posteriores")
        candidate["collections"].append(collection_record(COLLECTION, "Exército e indústria de defesa soviéticos, 1934–1936",
                                                        sum(c["parent_id"] is None for c in current["collections"])))
        for number, (_, (slug, title)) in enumerate(SUBS.items()):
            candidate["collections"].append(collection_record(slug, title, number, COLLECTION))
        files, ids = {}, []
        queue_fields, _ = editorial.read_queue()
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=queue_fields)
        for position, (row, metadata, content, detail) in enumerate(prepared):
            ident = "military-" + row["id"]
            target = f"originais/militares/{ident}.ru.md"
            if any(d["id"] == ident for d in current["documents"]) or (ROOT / target).exists():
                raise model.CatalogError("Destino já existe: " + ident)
            subgroup = COLLECTION + "/" + SUBS[row["collection"]][0]
            doc = {"id": ident, "kind": "document", "titles": {"ru": detail["source_title"], "pt": row["title_pt"]},
                   "document_type": TYPES[row["kind"]],
                   "historical_date": {"display": detail["source_date"] or row["date"], "value": None, "precision": "not_recorded"},
                   "archive_reference": detail["archive_reference"] or row["archive_reference"] or None, "author_label": None,
                   "source": {"name": "Istmat · Wayback Machine" if metadata.get("archive_url") else "Istmat", "id": row["url"].rstrip("/").split("/")[-1], "url": metadata.get("archive_url", row["url"])},
                   "source_metadata": {"original_language": "ru", "acquisition": metadata, "conversion": detail,
                                       "inventory_archive_reference": row["archive_reference"],
                                       "historical_review": "Data e atribuição do inventário preservadas; cotejo histórico pendente."},
                   "default_format": "markdown", "presentation": {"eyebrow": "Documentação militar · Russo"}, "extra": {},
                   "compatibility_fields": ["id", "type", "title_pt", "title_ru", "date", "archive", "document_type", "format", "eyebrow", "source_name", "source_id", "source_url", "languages"]}
            candidate["documents"].append(doc)
            candidate["editions"].append({"id": ident + ":ru", "document_id": ident, "language": "ru", "label": "Русский оригинал",
                                          "file": target, "format": "markdown", "position": 0, "bytes": len(content.encode()),
                                          "sha256": model.sha256(content.encode()), "editorial_status": "not_recorded", "extra": {},
                                          "compatibility_fields": ["code", "label", "file", "format"]})
            for collection_id in (COLLECTION, subgroup):
                candidate["memberships"].append({"collection_id": collection_id, "document_id": ident,
                                                 "position": sum(m["collection_id"] == collection_id for m in candidate["memberships"])})
            files[target] = content
            ids.append(ident)
            issue = dict.fromkeys(queue_fields, "")
            issue.update(chave=ident + ":fonte_militar", prioridade="alta" if any(f["priority"] == "alta" for f in detail["flags"]) else "media",
                         dificuldade="media", status="pendente", id=ident, colecoes="Exército e indústria de defesa / " + SUBS[row["collection"]][1],
                         titulo_ru=detail["source_title"], problema="fonte_militar", dificuldade_encontrada=" | ".join(f["reason"] for f in detail["flags"]) or "Conferir início, fim, referências e possíveis sobreposições com sessões temáticas.",
                         acao_sugerida="Cotejar HTML preservado com Markdown, notas e dados numéricos; registrar a revisão.",
                         arquivo_markdown=target, url_teste="http://localhost:8000/#/doc/" + ident, fonte=row["url"], trechos="[]")
            writer.writerow(issue)
        for name in model.FILES:
            if current[name] != candidate[name]:
                files[f"data/catalog/{name}.json"] = model.json_bytes(candidate[name]).decode()
        files["data/manifest.json"] = model.json_bytes(model.export_manifest(candidate)).decode()
        queue_path = "docs/revisao-markdown/pendencias.csv"
        previous = (ROOT / queue_path).read_bytes().decode()
        files[queue_path] = previous + ("" if previous.endswith("\n") else "\r\n") + stream.getvalue()
        preview = editorial.store_preview(editorial.revision(), candidate, files, None,
            [{"field": "Coleção militar 1934–1936", "before": None, "after": ids}],
            entity={"kind": "batch", "id": COLLECTION, "document_ids": ids})
        repository = Repository(ROOT, ROOT / ".local/catalog.sqlite3", current, {})
        result = editorial.save(repository, {"preview_id": preview["preview_id"]})
        (REPORT / "gravacao.json").write_bytes(model.json_bytes(result))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        editorial.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    items = json.loads(INVENTORY.read_text())
    prepared, report = [], []
    (WORK / "review").mkdir(parents=True, exist_ok=True)
    for row in items:
        info_path = WORK / (row["id"] + ".json")
        metadata = json.loads(info_path.read_text()) if info_path.exists() else {"status": "not_attempted"}
        record = {"id": row["id"], "titulo_pt": row["title_pt"], "subcolecao": row["collection"],
                  "url": row["url"], "status": metadata["status"], "motivo": metadata.get("error", ""),
                  "captura_wayback": metadata.get("capture_timestamp", ""), "url_captura": metadata.get("archive_url", ""),
                  "html_local": metadata.get("file", ""), "markdown_preparado": "", "tabelas": "", "notas_markdown": "",
                  "data_na_fonte": "", "inicio_texto": "", "fim_texto": ""}
        if metadata["status"] == "acquired":
            try:
                content, detail = convert(row, metadata)
                target = WORK / "review" / (row["id"] + ".ru.md")
                target.write_text(content)
                (WORK / "review" / (row["id"] + ".json")).write_bytes(model.json_bytes(detail))
                prepared.append((row, metadata, content, detail))
                record.update(status="prepared", motivo=" | ".join(f["reason"] for f in detail["flags"]),
                              markdown_preparado=str(target.relative_to(ROOT)), tabelas=detail["tables"],
                              notas_markdown=detail["footnotes"], data_na_fonte=detail["source_date"],
                              inicio_texto=detail["source_start"], fim_texto=detail["source_end"])
            except (ValueError, OSError) as error:
                record.update(status="conversion_pending", motivo=str(error))
        report.append(record)
    REPORT.mkdir(parents=True, exist_ok=True)
    with (REPORT / "pendencias.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(report[0]))
        writer.writeheader()
        writer.writerows(report)
    (REPORT / "inventario.json").write_bytes(model.json_bytes(report))
    print(f"Preparados: {len(prepared)}/{len(items)}. Relatório: {REPORT.relative_to(ROOT)}", flush=True)
    if args.apply:
        if len(prepared) != len(items):
            raise model.CatalogError("Aquisição/conversão incompleta: acervo e coleção não alterados. Consultar pendencias.csv.")
        apply(prepared)


if __name__ == "__main__":
    try:
        main()
    except model.CatalogError as error:
        sys.exit(str(error))
