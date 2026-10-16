"""Identificação e diagnóstico conservador de traduções Markdown, sem alinhamento."""

from __future__ import annotations

import difflib
import re
from pathlib import PurePosixPath
from urllib.parse import urlsplit

MAX_TRANSLATION_BYTES = 4 * 1024 * 1024


EXPORT_HEADER = re.compile(
    r"^(?:\ufeff)?(?:[ \t]*\r?\n)*#[ \t]+[^\r\n]+\r?\n"
    r"(?:(?:[ \t]*\r?\n)|(?:(?:Fonte|Source|ID\s+ShowTrials|ShowTrials\s+ID|"
    r"ID\s+(?:do\s+)?documento|Document\s+ID|Idioma|Language)[ \t]*:[^\r\n]*\r?\n))+"
    r"[ \t]*---[ \t]*(?:\r?\n|$)(?:[ \t]*\r?\n)*", re.I)


def split_export_headers(content):
    body = content
    headers = []
    while True:
        match = EXPORT_HEADER.match(body)
        if not match or not re.search(r"^(?:Idioma|Language)[ \t]*:", match[0], re.I | re.M) or not re.search(
                r"^(?:Fonte|Source|ID\s+ShowTrials|ShowTrials\s+ID|ID\s+(?:do\s+)?documento|Document\s+ID)[ \t]*:", match[0], re.I | re.M):
            break
        headers.append(match[0])
        body = body[match.end():]
    return {"body": body, "headers": headers, "header_count": len(headers)}


def identification(filename, content):
    result = {"filename": filename, "document_ids": [], "languages": [], "source_urls": [], "title": None,
              "has_export_header": False}
    match = re.fullmatch(r"(.+)\.([a-z]{2,3})\.(?:md|markdown)", filename, re.I)
    if match:
        result["filename_id"] = match[1]
        result["filename_language"] = match[2].lower()
    lines = content.lstrip("\ufeff").replace("\r\n", "\n").splitlines()
    if lines and re.match(r"^#\s+", lines[0]):
        result["title"] = re.sub(r"^#\s+", "", lines[0]).strip()
    # Reconhece o cabeçalho da exportação. Não varre o corpo em busca de IDs.
    start = 1 if result["title"] else 0
    saw_metadata = False
    for line in lines[start:80]:
        stripped = line.strip()
        if stripped == "---":
            result["has_export_header"] = saw_metadata
            break
        if not stripped:
            continue
        match = re.fullmatch(r"(?:ID\s+ShowTrials|ShowTrials\s+ID|ID\s+(?:do\s+)?documento|Document\s+ID)\s*:\s*(\S+)", stripped, re.I)
        if match:
            result["document_ids"].append(match[1])
            saw_metadata = True
            continue
        match = re.fullmatch(r"(?:Idioma|Language)\s*:\s*(.+)", stripped, re.I)
        if match:
            aliases = {"português": "pt", "portuguese": "pt", "inglês": "en", "english": "en", "russo": "ru", "russian": "ru"}
            value = match[1].strip().lower()
            result["languages"].append(aliases.get(value, value))
            saw_metadata = True
            continue
        match = re.fullmatch(r"(?:Fonte|Source)\s*:\s*(https?://\S+)", stripped, re.I)
        if match:
            result["source_urls"].append(match[1])
            saw_metadata = True
            continue
        break
    result["has_export_header"] = split_export_headers(content)["header_count"] > 0
    return result


def normalized_url(value):
    parsed = urlsplit(value)
    return ((parsed.hostname or "").lower().removeprefix("www."), parsed.path.rstrip("/"))


def findings(identity, document, language):
    result = []
    def add(level, message):
        result.append({"level": level, "message": message})
    if identity.get("filename_id") and identity["filename_id"] != document["id"]:
        add("warning", f"O nome do arquivo indica {identity['filename_id']}; o documento selecionado é {document['id']}.")
    if identity.get("filename_language") and identity["filename_language"] != language:
        add("warning", f"O nome do arquivo indica idioma {identity['filename_language'].upper()}; você selecionou {language.upper()}.")
    for value in dict.fromkeys(identity["document_ids"]):
        expected = {document["id"]}
        if document["source"].get("id"):
            expected.add(str(document["source"]["id"]))
        if value not in expected:
            add("warning", f"O cabeçalho indica ID {value}; o documento selecionado é {document['id']}.")
    for value in dict.fromkeys(identity["languages"]):
        if value != language:
            add("warning", f"O cabeçalho indica idioma {value.upper()}; você selecionou {language.upper()}.")
    expected_url = document["source"].get("url")
    for value in dict.fromkeys(identity["source_urls"]):
        if expected_url and normalized_url(value) != normalized_url(expected_url):
            add("warning", f"A fonte indicada no arquivo ({value}) difere da fonte cadastrada ({expected_url}).")
    if not identity.get("filename_id") and not identity["document_ids"]:
        add("info", "Não foi encontrado um ID reconhecível no nome ou no cabeçalho. A associação será a escolhida explicitamente no formulário.")
    if not identity["languages"] and not identity.get("filename_language"):
        add("info", "O arquivo não declara um idioma reconhecível. O idioma selecionado será usado, sem classificação automática do texto.")
    if identity["has_export_header"]:
        add("info", "O cabeçalho de exportação será preservado no arquivo, mas ficará fora do corpo exibido e da contagem de parágrafos. Ao exportar novamente, será gerado somente um cabeçalho.")
    return result


def structure(content, format="markdown"):
    header_count = 0
    if format != "text":
        envelope = split_export_headers(content)
        content = envelope["body"]
        header_count = envelope["header_count"]
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n" if format == "text" else r"\n{2,}", content.replace("\r\n", "\n")) if chunk.strip()]
    counts = {"study_blocks": 0, "paragraphs": 0, "headings": 0, "lists": 0, "tables": 0, "code_blocks": 0, "export_headers": header_count}
    for chunk in chunks:
        if format != "text" and re.fullmatch(r"-{3,}", chunk):
            continue
        counts["study_blocks"] += 1
        if format != "text" and "\n" not in chunk and re.match(r"^#{1,6}\s+", chunk):
            counts["headings"] += 1
        elif format != "text" and re.match(r"^(?:[-*+]\s|\d+[.)]\s)", chunk):
            counts["lists"] += 1
        elif format != "text" and re.search(r"(?m)^\s*\|?.*\|.*\n\s*\|?\s*:?-{3,}", chunk):
            counts["tables"] += 1
        elif format != "text" and re.match(r"^(?:```|~~~)", chunk):
            counts["code_blocks"] += 1
        else:
            counts["paragraphs"] += 1
    return counts


def line_diff(previous, proposed):
    lines = []
    truncated = False
    # Sem SequenceMatcher quadrático sobre arquivos inteiros muito extensos.
    if len(previous) + len(proposed) > 800000:
        return {"text": "Arquivo extenso: a comparação linha a linha foi omitida. Consulte as versões completas na prévia.", "truncated": True}
    iterator = difflib.unified_diff(previous.splitlines(), proposed.splitlines(), fromfile="versão atual", tofile="arquivo enviado", n=3, lineterm="")
    characters = 0
    for line in iterator:
        if len(lines) >= 800 or characters + len(line) > 100000:
            truncated = True
            break
        lines.append(line)
        characters += len(line)
    if not lines and previous != proposed:
        lines.append("O conteúdo por linha é igual; há diferenças de quebras de linha, espaços finais ou marca de codificação.")
    return {"text": "\n".join(lines) or "O arquivo é idêntico à versão atual.", "truncated": truncated}


def markdown_filename(source_file, document_id, language):
    return str(PurePosixPath(source_file).parent / f"{document_id}.{language}.md")
