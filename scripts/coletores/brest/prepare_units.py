#!/usr/bin/env python3
"""Prepara unidades de Brest para prévia, sem escrever no catálogo público."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from markdownify import markdownify

from coletar import DEFAULT_OUTPUT, atomic_json, immutable, sha

TITLES = {
    "lenin-jan-07": "Para a história da questão da paz infeliz",
    "lenin-pt-jan": "Para a história da questão da paz infeliz",
    "lenin-jan-08": "Posfácio às teses sobre a conclusão imediata de uma paz separada e anexionista",
    "lenin-feb-18-manha": "Intervenções na reunião matinal do Comitê Central de 18 de fevereiro de 1918",
    "lenin-feb-23-ata": "Discursos na reunião do Comitê Central de 23 de fevereiro de 1918",
    "lenin-feb-23-paz-ou-guerra": "Paz ou guerra?",
    "lenin-feb-24-governo": "Decisão sobre a aceitação das condições de paz alemãs",
    "lenin-mar-05": "Uma lição séria e uma responsabilidade séria",
    "lenin-mar-14": "IV Congresso dos Sovietes — material para o discurso sobre a paz",
    "lenin-mar-comment": "Comentário sobre a conduta dos comunistas de esquerda",
    "lenin-mai-09": "O infantilismo de esquerda e a mentalidade pequeno-burguesa",
    "kommunist-teses-abril": "Teses sobre a situação atual — Kommunist",
    "radek-foreign-policy": "A política externa da República Soviética — Karl Radek",
    "tratado-marxists": "Tratado de paz de Brest-Litovsk, 3 de março de 1918",
    "cc-jan-11-lenin": "Intervenções na reunião do Comitê Central de 11 de janeiro de 1918",
    "cc-jan-19-lenin": "Intervenções na reunião do Comitê Central de 19 de janeiro de 1918",
    "cc-feb-18-noite": "Intervenções na reunião noturna do Comitê Central de 18 de fevereiro de 1918",
    "cc-feb-24-lenin": "Proposta na reunião do Comitê Central de 24 de fevereiro de 1918",
    "lenin-phrase": "Sobre a frase revolucionária",
    "lenin-socialist-fatherland": "A pátria socialista está em perigo!",
    "lenin-painful-lesson": "Uma lição dolorosa, mas necessária",
    "lenin-strange-monstrous": "Estranho e monstruoso",
    "trotsky-peace-negotiations": "As negociações de paz e a revolução",
    "trotsky-at-brest": "Em Brest-Litovsk",
}
CONGRESS_TITLES = [
    "Relatório político do Comitê Central, 7 de março de 1918",
    "Resposta ao debate sobre o relatório político do Comitê Central, 8 de março de 1918",
    "Resolução sobre a guerra e a paz",
    "Discursos contra as emendas de Trotsky à resolução sobre a guerra e a paz",
    "Discurso contra a declaração dos comunistas de esquerda em apoio à emenda de Trotsky",
    "Acréscimo à resolução sobre a guerra e a paz",
    "Discurso contra a emenda de Zinoviev ao acréscimo à resolução sobre a guerra e a paz",
    "Proposta referente à resolução sobre a guerra e a paz",
    "Relatório sobre a revisão do programa e a mudança do nome do partido",
    "Resolução sobre a mudança do nome e do programa do partido",
    "Proposta sobre a revisão do programa do partido",
    "Discurso sobre a proposta de Mgeladze para a elaboração do programa do partido",
    "Discurso contra a emenda de Larin ao nome do partido",
    "Discurso contra a emenda de Pelshe à resolução sobre o programa do partido",
    "Discurso contra a emenda de Bukharin à resolução sobre o programa do partido",
    "Discurso sobre as eleições para o Comitê Central",
    "Resolução sobre a recusa dos comunistas de esquerda em integrar o Comitê Central",
    "Esboço preliminar do projeto de programa",
]


def convert(raw, origin):
    soup = BeautifulSoup(raw, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    root = soup.select_one("article,main,#mainContent") or soup.body or soup
    root = BeautifulSoup(str(root), "html.parser")
    credits = [p.get_text(" ", strip=True) for p in root.select("p.information,p.info")]
    written = next((match.group(0).strip() for text in credits
                    if (match := re.search(r"(?:Written|Delivered|Escrito):\s*.*?(?=First Published:|Published:|Source:|Translated:|Transcription|Online Version:|$)", text))), None)
    for el in root.select("script,style,noscript,form,nav,footer,.toplink,.topnav,.navbar"):
        el.decompose()
    definitions, converted, unresolved = [], [], []
    anchors = {a.get("id", a.get("name")): a for a in root.select("a[id],a[name]")}
    targets = list(dict.fromkeys(a.get("href", "")[1:] for a in root.select('a[href^="#"]')))
    for target in targets:
        anchor = anchors.get(target)
        if anchor is None:
            continue
        block = anchor.find_parent("p")
        if block is None:
            continue
        classes = set(block.get("class", []))
        is_note = bool(classes & {"note", "footnote", "endnote"}) or bool(re.fullmatch(r"\d+n|t[nr]\d+", target))
        if not is_note:
            continue
        calls = [a for a in root.select('a[href^="#"]') if a.get("href") == "#" + target and block not in a.parents]
        if not calls:
            continue
        if len(block.select("a[id],a[name]")) > 1 or block.select("table"):
            unresolved.append(target)
            continue
        key = "src-" + re.sub(r"[^A-Za-z0-9_-]", "-", target)
        token = "BRESTNOTEREFERENCE" + str(len(converted)) + "END"
        # Remover somente retornos ao texto, conservando referências externas.
        for back in list(block.select('a[href^="#"]')):
            if back.get("href", "")[1:] not in targets or re.search(r"retornar|return|back", back.get_text(" ", strip=True), re.I):
                back.decompose()
        for link in block.select("a[href]"):
            link["href"] = urljoin(origin, link["href"])
        note = markdownify(str(block), heading_style="ATX", escape_underscores=False).strip()
        if not note:
            unresolved.append(target)
            continue
        for call in calls:
            call.replace_with(root.new_string(token))
        definitions.append(f"[^{key}]: " + note.replace("\n", "\n    "))
        converted.append((token, f"[^{key}]"))
        block.decompose()
    for tag, attribute in (("a", "href"), ("img", "src")):
        for el in root.find_all(tag):
            if el.get(attribute):
                el[attribute] = urljoin(origin, el[attribute])
    content = markdownify(str(root), heading_style="ATX", bullets="-", escape_underscores=False).strip()
    for token, reference in converted:
        content = content.replace(token, reference)
    if definitions:
        content += "\n\n" + "\n\n".join(definitions)
    return content + "\n", {"title_literal": title, "credits_literal": credits,
                              "written_literal": written,
                              "local_footnotes": len(definitions), "unresolved_notes": unresolved,
                              "tables": len(root.select("table")), "images": len(root.select("img"))}


def build(work):
    rows = json.loads((work / "inventario.json").read_text(encoding="utf-8"))
    units = []
    for row in rows:
        congress = re.fullmatch(r"/archive/lenin/works/1918/7thcong/(\d{2})\.htm", urlparse(row["url"]).path)
        congress_number = int(congress[1]) if congress else None
        title_pt = TITLES.get(row["id"])
        if congress_number and 1 <= congress_number <= len(CONGRESS_TITLES):
            title_pt = "VII Congresso — " + CONGRESS_TITLES[congress_number - 1]
        item = {"id": "brest-" + row["id"], "source_url": row["url"], "language": row["idioma"],
                "original_language": "ru", "title_literal": row.get("titulo_extraido", row["titulo"]),
                "title_pt": title_pt, "subcollection": row["grupo"],
                "subcollections": row.get("grupos", [row["grupo"]]),
                "kind": "document", "document_type": "article", "ready_for_import": False,
                "issues": [], "provenance": {"seed_id": row["id"], "seed_title": row["titulo"], "acquisition": row}}
        if row["id"].startswith("tratado-"):
            item["original_language"] = None
            item["provenance"]["language_note"] = "Versão inglesa do tratado; não atribuir um único idioma original ao instrumento multilateral sem conferência."
        if congress_number:
            item["provenance"]["congress_source_part"] = congress_number
            item["provenance"]["unit_basis"] = "Divisão explícita do índice de intervenções de Lenin no VII Congresso; não representa a ata integral do congresso."
            item["document_type"] = "draft_project" if congress_number == 18 else "decree_resolution" if congress_number in {3, 10, 17} else "speech" if congress_number in {1, 2, 4, 5, 7, 9, 12, 13, 14, 15, 16} else "memo_note"
        elif row["id"] == "tratado-marxists":
            item["document_type"] = None
        elif row["grupo"] == "02-comite-central":
            item["document_type"] = "speech"
        if row.get("estado_aquisicao") != "FOUND_HTML_UNREVIEWED":
            item["issues"].append(row.get("erro", "Fonte sem transcrição HTML integral nesta etapa: " + row["estado_aquisicao"]))
            units.append(item)
            continue
        raw_path = work / row["raw_path"]
        if not raw_path.resolve().is_relative_to(work.resolve()):
            raise ValueError("Fonte fora da frente de coleta")
        raw = raw_path.read_bytes()
        if sha(raw) != row["checksum_raw_sha256"]:
            raise ValueError("Fonte alterada: " + row["id"])
        content, detail = convert(raw, row.get("url_final", row["url"]))
        fingerprint = sha(content.encode("utf-8"))
        target = Path("units") / item["id"] / (fingerprint + "." + item["language"] + ".md")
        immutable(work / target, content.encode("utf-8"))
        item.update(markdown=str(target), markdown_sha256=fingerprint,
                    raw=row["raw_path"], raw_sha256=row["checksum_raw_sha256"],
                    date_literal=detail["written_literal"],
                    title_literal=detail["title_literal"] or item["title_literal"])
        item["provenance"]["conversion"] = detail
        item["issues"].append("Revisão editorial de tradução, notas e referências permanece pendente.")
        if title_pt and item["language"] in {"ru", "pt", "en"} and len(content.strip()) >= 250 and not detail["unresolved_notes"]:
            item["ready_for_import"] = True
        else:
            item["issues"].append("Unidade não liberada: conferir escopo composto, idioma, extensão ou notas.")
        if item["language"] == "de":
            item["issues"].append("A tradução alemã foi preservada como fonte de pesquisa; idioma fora do escopo desta prévia.")
        units.append(item)
    # Correspondência explícita do inventário, confirmada no corpo: introdução e
    # teses1–22 em ambas as línguas. Sem alinhamento automático de parágrafos.
    pair = {u["provenance"]["seed_id"]: u for u in units if u["provenance"]["seed_id"] in {"lenin-jan-07", "lenin-pt-jan"}}
    def full_theses(unit):
        source = BeautifulSoup((work / unit["raw"]).read_bytes(), "html.parser")
        numbers = {int(match[1]) for paragraph in source.find_all("p")
                   if (match := re.match(r"^(\d+)\.\s", paragraph.get_text(" ", strip=True)))}
        return set(range(1, 23)).issubset(numbers)
    if len(pair) == 2 and all(u["ready_for_import"] and full_theses(u) for u in pair.values()):
        for unit in pair.values():
            unit["document_id"] = "brest-lenin-jan-07"
            unit["provenance"]["edition_pair_basis"] = "Correspondência indicada na semente, títulos e escopo de introdução/teses1–22 conferidos; datas juliana/gregoriana preservadas nos textos."
    atomic_json(work / "units.json", {"schema_version": 1, "front": "brest", "units": units})
    return {"units": len(units), "ready_editions": sum(u["ready_for_import"] for u in units),
            "blocked": sum(not u["ready_for_import"] for u in units)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(build(args.workdir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
