"""Audita o HTML coletado e prepara versões Markdown com títulos revisados.

python3 scripts/prepare_markdown.py PACOTE [--apply-reviewed | --apply-pilot]
python3 scripts/prepare_markdown.py --check
Usa apenas a biblioteca padrão; não baixa nem traduz documentos.
"""

import argparse
import csv
import hashlib
import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from catalog_guard import ensure_legacy_manifest_write_allowed

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "data/markdown-conversions.json"
REVIEW = ROOT / "data/markdown-review.json"
PILOT = {"5855", "9470", "2645"}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def key(text):
    # O exportador inseriu espaços nas fronteiras entre tags inline.
    # A equivalência aqui serve somente para localizar títulos já revisados.
    return re.sub(r"\s+", "", text)


def blocks(text):
    return [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]


def legacy_text(source):
    """Reproduz a limpeza histórica somente para conferir a origem do TXT."""
    text = re.sub(r"<br\s*/?>", "\n", source, flags=re.I)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.I)
    text = re.sub(r"</div\s*>", "\n", text, flags=re.I)
    text = unescape(re.sub(r"<[^>]+>", " ", text))
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


class SourceHTML(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.paragraphs = []
        self.current = None
        self.heading_tags = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if re.fullmatch(r"h[1-6]", tag):
            self.heading_tags += 1
        if tag == "p":
            attrs = dict(attrs)
            centered = attrs.get("align", "").lower() == "center" or bool(
                re.search(r"text-align\s*:\s*center", attrs.get("style", ""), re.I)
            )
            self.current = [centered, []]
        elif tag == "br" and self.current is not None:
            self.current[1].append("\n")

    def handle_data(self, data):
        if self.current is not None:
            self.current[1].append(data)

    def handle_endtag(self, tag):
        if tag == "p" and self.current is not None:
            centered, parts = self.current
            text = "".join(parts).strip()
            if text:
                self.paragraphs.append((centered, text))
            self.current = None


def reviewed_headings(review, parsed, plain):
    selected = []
    for heading in review["headings"]:
        centered, text = parsed.paragraphs[heading["html_paragraph"]]
        if not centered or text != heading["html_text"]:
            raise ValueError(f"HTML diferente da seleção revisada: {review['id']}")
        matches = [i for i, block in enumerate(plain) if key(block) == key(text)]
        if len(matches) != 1 or "\n" in plain[matches[0]]:
            raise ValueError(f"Título ambíguo ou dividido, {review['id']}: {text}")
        selected.append({"block": matches[0], "level": heading["level"], "text": plain[matches[0]],
                         "html_text": text, "html_paragraph": heading["html_paragraph"],
                         "evidence": "p centralizado no HTML coletado"})
    if len(selected) < 2:
        raise ValueError(f"Estrutura insuficiente: {review['id']}")
    assert len({h["block"] for h in selected}) == len(selected)
    assert [h["block"] for h in selected] == sorted(h["block"] for h in selected)
    return selected


def escape_text(text):
    # Mantém sinais da fonte literais: notas [1], <expansões>, asteriscos etc.
    text = re.sub(r"([\\`*_{}\[\]<>#!|~&])", r"\\\1", text)
    text = re.sub(r"(?m)^([ \t]*)([-+=])", r"\1\\\2", text)
    text = re.sub(r"(?m)^([ \t]*\d+)([.)])(?=\s)", r"\1\\\2", text)
    return text


def render_conversion(original, headings):
    plain = blocks(original)
    assert len({h["block"] for h in headings}) == len(headings)
    assert all(0 <= h["block"] < len(plain) and 1 <= h["level"] <= 6 for h in headings)
    levels = {h["block"]: h for h in headings}
    output = []
    for i, block in enumerate(plain):
        if i in levels:
            assert block == levels[i]["text"]
        escaped = escape_text(block).replace("\n", "  \n")
        output.append("#" * levels[i]["level"] + " " + escaped if i in levels else escaped)
    result = "\n\n".join(output) + "\n"
    restored = []
    for i, block in enumerate(blocks(result)):
        if i in levels:
            block = block[levels[i]["level"] + 1:]
        block = block.replace("  \n", "\n")
        restored.append(re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])", r"\1", block))
    assert restored == plain, "Conteúdo ou limites de parágrafos alterados"
    return result


def check_conversion(recipe):
    original = ROOT / recipe["original"]
    assert digest(original.read_bytes()) == recipe["original_sha256"], original
    assert all(key(h["html_text"]) == key(h["text"]) for h in recipe["headings"])
    expected = render_conversion(original.read_text(), recipe["headings"])
    assert (ROOT / recipe["markdown"]).read_text() == expected, recipe["markdown"]
    assert len(blocks(expected)) == recipe["blocks"]


def check():
    catalog = json.loads(RECIPES.read_text())
    recipes = catalog["documents"]
    manifest = json.loads((ROOT / "data/manifest.json").read_text())
    docs = {d["id"]: d for d in manifest["documents"]}
    reviews = {d["id"]: d for d in json.loads(REVIEW.read_text())["documents"]}
    assert len({r["id"] for r in recipes}) == len(recipes)
    for recipe in recipes:
        check_conversion(recipe)
        if recipe["id"] in reviews and recipe.get("method") != "revisao_local":
            assert [(h["html_text"], h["level"]) for h in recipe["headings"]] == [
                (h["html_text"], h["level"]) for h in reviews[recipe["id"]]["headings"]]
        ru = next(l for l in docs[recipe["id"]]["languages"] if l["code"] == "ru")
        assert ru["file"] == recipe["markdown"] and ru["format"] == "markdown"
    if catalog.get("scope") == "all_showtrials":
        assert {r["id"] for r in recipes} == set(docs)
    print(f"OK: {len(recipes)} conversões; conteúdo, blocos, títulos, hashes e manifesto conferidos.")


def prepare(package, apply_ids=None):
    if apply_ids is not None:
        ensure_legacy_manifest_write_allowed(ROOT)
    manifest_path = ROOT / "data/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    docs = {d["source_id"]: d for d in manifest["documents"]}
    review = json.loads(REVIEW.read_text())
    reviews = {d["id"].removeprefix("showtrials-"): d for d in review["documents"]}
    deferred = {d["id"].removeprefix("showtrials-"): d["reason"] for d in review["deferred"]}
    existing = json.loads(RECIPES.read_text())["documents"] if RECIPES.exists() else []
    if any(r["id"].removeprefix("showtrials-") not in reviews for r in existing):
        raise ValueError("Acervo convertido em lote integral; use scripts/convert_showtrials_all.py para auditar ou reaplicar")
    active = {r["id"] for r in existing}
    if apply_ids is not None:
        active.update("showtrials-" + sid for sid in apply_ids)
    source_dir = next((p for p in (package / "originais/showtrials/posts-json", package / "original/local/posts-json") if p.is_dir()), None)
    if source_dir is None:
        raise ValueError("Pacote sem JSONs de posts")
    rows, recipes, seen = [], [], set()
    for file in sorted(source_dir.glob("*.json")):
        for post in json.loads(file.read_text()):
            sid = str(post["id"])
            if sid not in docs:
                continue
            assert sid not in seen, f"ID repetido: {sid}"
            seen.add(sid)
            source = post["content"]["rendered"]
            parsed = SourceHTML(source)
            path = f"originais/showtrials/showtrials-{sid}.ru.txt"
            raw = (ROOT / path).read_bytes()
            plain = blocks(raw.decode("utf-8"))
            if plain != blocks(legacy_text(source)):
                raise ValueError(f"HTML e TXT não correspondem: {docs[sid]['id']}")
            centered = [t for c, t in parsed.paragraphs if c]
            numbered = [t for t in centered if re.match(r"^(?:[IVX]+(?:\.|$)|\d+\.)", t)]
            selection = reviews.get(sid)
            headings = reviewed_headings(selection, parsed, plain) if selection else []
            status = "markdown" if docs[sid]["id"] in active else "seleção revisada" if selection else "adiado" if sid in deferred else "revisar" if numbered else "sem seleção automática"
            rows.append([docs[sid]["id"], docs[sid]["title_ru"], len(plain),
                         parsed.heading_tags, len(centered), len(numbered),
                         status, docs[sid]["source_url"], len(headings),
                         selection["notes"] if selection else deferred.get(sid, "")])
            if selection:
                recipes.append({"id": docs[sid]["id"], "original": path,
                    "markdown": path.removesuffix(".txt") + ".md",
                    "original_sha256": digest(raw), "html_sha256": digest(source.encode()),
                    "source_json": file.relative_to(package).as_posix(),
                    "source_url": docs[sid]["source_url"], "blocks": len(plain), "headings": headings})
    assert seen == set(docs), "Coleta incompleta"
    assert {r["id"].removeprefix("showtrials-") for r in recipes} == set(reviews)
    recipes.sort(key=lambda r: r["id"])
    out = ROOT / "docs/revisao-markdown"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "levantamento.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "titulo_ru", "blocos_txt", "tags_h1_h6", "paragrafos_centralizados",
                         "centralizados_numerados", "situacao", "fonte", "titulos_revisados", "observacao"])
        writer.writerows(sorted(rows))
    summary = {"documentos": len(rows), "com_tags_h1_h6": sum(r[3] > 0 for r in rows),
               "com_paragrafos_centralizados": sum(r[4] > 0 for r in rows),
               "com_centralizados_numerados": sum(r[5] > 0 for r in rows),
               "piloto": [{"id": r["id"], "blocos": r["blocks"], "titulos": len(r["headings"])} for r in recipes if r["id"].removeprefix("showtrials-") in PILOT],
               "convertidos": [{"id": r["id"], "blocos": r["blocks"], "titulos": len(r["headings"])} for r in recipes if r["id"] in active],
               "titulos_publicados": sum(len(r["headings"]) for r in recipes if r["id"] in active),
               "adiados": review["deferred"]}
    (out / "resumo.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    report = ["# Documentos com estrutura revisada", "",
              "Os nomes portugueses desta tabela servem à revisão; os títulos e corpos russos do site não foram traduzidos. Os links de teste pressupõem o servidor local na porta 8000.", "",
              "| Documento | Estrutura | Títulos | Blocos preservados | Abrir no site local |",
              "| --- | --- | ---: | ---: | --- |"]
    for recipe in sorted(recipes, key=lambda r: int(r["id"].removeprefix("showtrials-"))):
        if recipe["id"] not in active:
            continue
        selection = reviews[recipe["id"].removeprefix("showtrials-")]
        report.append(f"| {selection['title_pt']} | {selection['structure']} | {len(recipe['headings'])} | {recipe['blocks']} | [{recipe['id']}](http://localhost:8000/#/doc/{recipe['id']}) |")
    report.extend(["", "## Observações por documento", ""])
    for sid, selection in reviews.items():
        if selection["notes"]:
            report.append(f"- **{selection['id']}**: {selection['notes']}")
    report.extend(["", "## Casos adiados", ""])
    for sid, reason in deferred.items():
        report.append(f"- **showtrials-{sid}**: {reason}")
    (out / "convertidos.md").write_text("\n".join(report) + "\n")
    if apply_ids is not None:
        # Prepara e valida tudo antes de alterar arquivos de publicação.
        for recipe in existing:
            check_conversion(recipe)
        prepared = [(r, render_conversion((ROOT / r["original"]).read_text(), r["headings"])) for r in recipes if r["id"] in active]
        for recipe, text in prepared:
            target = ROOT / recipe["markdown"]
            if target.exists() and target.read_text() != text:
                raise ValueError(f"Revisão local diferente: {target}")
            ru = next(l for l in docs[recipe["id"].removeprefix("showtrials-")]["languages"] if l["code"] == "ru")
            if ru["file"] not in {recipe["original"], recipe["markdown"]}:
                raise ValueError(f"Versão russa local diferente: {recipe['id']}")
        for recipe, text in prepared:
            (ROOT / recipe["markdown"]).write_text(text)
            ru = next(l for l in docs[recipe["id"].removeprefix("showtrials-")]["languages"] if l["code"] == "ru")
            ru.update(file=recipe["markdown"], format="markdown")
        RECIPES.write_text(json.dumps({"version": 1, "documents": [r for r, _ in prepared]}, ensure_ascii=False, indent=2) + "\n")
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        check()
    print(f"Levantamento: {len(rows)} documentos; {len(active)} versões Markdown; {summary['titulos_publicados']} títulos; {len(deferred)} casos adiados.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, nargs="?")
    apply = parser.add_mutually_exclusive_group()
    apply.add_argument("--apply-pilot", action="store_true", help="Aplica os três exemplos iniciais, preservando as demais conversões")
    apply.add_argument("--apply-reviewed", action="store_true", help="Aplica todas as seleções explícitas de data/markdown-review.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    elif args.package:
        ids = set(d["id"].removeprefix("showtrials-") for d in json.loads(REVIEW.read_text())["documents"]) if args.apply_reviewed else PILOT if args.apply_pilot else None
        prepare(args.package, ids)
    else:
        parser.error("Informe o pacote portátil ou --check")
