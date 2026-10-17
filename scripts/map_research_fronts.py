#!/usr/bin/env python3
"""Gera inventário de pesquisa; somente lê o acervo e escreve docs/pesquisa.

Não coleta, traduz, testa, cadastra documentos ou modifica catálogos do site.
Correspondência de seção é uma pista editorial, nunca uma colação textual.
"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "temporario/frentes de pesquisa"
OUT = ROOT / "docs/pesquisa/mapeamento-frentes"

# Índices dos títulos H1/H2 na compilação: título principal e introdução ocupam 0/1.
# Comparação manual dos títulos portugueses com o inventário; RU/EN são candidatos
# pela posição editorial correspondente, ainda sem conferência do conteúdo integral.
SECTIONS = {
    "EZH-001": 2, "EZH-002": 3, "EZH-003": 4, "EZH-004": 5,
    "EZH-005": 6, "EZH-006": 7, "EZH-007": 8, "EZH-008": 9,
    "EZH-009": 10, "EZH-010": 11, "EZH-011": 12, "EZH-012": 13,
    "EZH-013": 14, "EZH-015": 15, "EZH-017": 16, "EZH-018": 17,
    "EZH-019": 18, "EZH-020": 19, "EZH-021": 21, "EZH-022": 22,
    "EZH-023": 23, "EZH-025": 24, "EZH-026": 25,
}
ALIASES = {
    "ezhov-1939-04-26": "EZH-003",
    "MER-001": "EZH-003", "MER-002": "EZH-003", "MER-003": "EZH-003",
    "MER-004": "EZH-012", "MER-005": "EZH-013", "MER-006": "EZH-026",
    "EZH-021B": "EZH-021", "EZH-REF-JULG": "EZH-026",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def url_key(url):
    parsed = urlsplit(url.strip())
    host = (parsed.hostname or "").lower().removeprefix("www.")
    return host + unquote(parsed.path).rstrip("/") + ("?" + parsed.query if parsed.query else "")


def save_csv(name, rows):
    with (OUT / name).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    documents = json.loads((ROOT / "data/catalog/documents.json").read_text())
    editions = json.loads((ROOT / "data/catalog/editions.json").read_text())
    memberships = json.loads((ROOT / "data/catalog/memberships.json").read_text())
    source_index = defaultdict(list)
    versions = defaultdict(list)
    collections = defaultdict(list)
    for doc in documents:
        if doc.get("source", {}).get("url"):
            source_index[url_key(doc["source"]["url"])].append(doc["id"])
    for edition in editions:
        versions[edition["document_id"]].append(edition)
    for membership in memberships:
        collections[membership["document_id"]].append(membership["collection_id"])
    headings = {}
    for language in ("pt", "ru", "en"):
        path = ROOT / f"originais/confessionezhov.{language}.md"
        headings[language] = [(line, text) for line, text in enumerate(path.read_text().splitlines(), 1)
                              if re.match(r"^#{1,2} ", text)]

    groups = [
        ("ezhov", SOURCE / "catalogo-critico-ezhov-1939-1940/inventario-ezhov-1939-1940.csv"),
        ("militar", SOURCE / "corpus-militar-sovietico-kit/corpus-militar-sovietico-kit/manifest.csv"),
        ("litvinov", SOURCE / "kit-litvinov-ezhov-fontes-publicadas/kit-litvinov-ezhov-fontes-publicadas/catalogos/fontes.csv"),
    ]
    mapped = []
    for front, path in groups:
        for item in read_csv(path):
            ident = item["id"]
            related = ident if front == "ezhov" else ALIASES.get(ident, ident if ident.startswith("EZH-") else "")
            direct = source_index.get(url_key(item["url"]), [])
            notes = [item.get("observacoes") or item.get("observacao") or ""]
            index = SECTIONS.get(related)
            doc_ids = []
            if direct:
                status = "fonte_url_correspondente"
                doc_ids = direct
                action = "Reutilizar cadastro; conferir edição/extensão e associar à coleção temática."
                notes.append("Correspondência da URL de origem, normalizando http/https, www e barra final; sem colação textual.")
            elif index is not None:
                status = "secao_candidata_na_compilacao"
                doc_ids = ["confessionezhov"]
                action = "Cotejar seção e edição; reaproveitar traduções existentes; publicar vínculo ou derivação com proveniência."
                notes.append("Correspondência temática/documental, não identidade textual confirmada nem acesso ao original integral.")
            elif ident == "EZH-REF-FURR":
                status = "compilacao_relacionada"
                doc_ids = ["confessionezhov"]
                action = "Relacionar compilação existente à referência; não cadastrar novamente como protocolo."
            else:
                status = "sem_correspondencia_identificada"
                action = "Localizar/obter fonte, delimitar texto ou fragmento e revisar antes de cadastrar."
            if front == "ezhov" and related in {"EZH-014", "EZH-016", "EZH-024"}:
                notes.append("Sem seção própria identificada por este mapeamento; não é prova de ausência de menções no corpo.")
            if related == "EZH-025":
                notes.append("Divergência: inventário 01/02/1940; título local 02.01.1940. Conferir edição antes de corrigir.")
            if related in {"EZH-013", "EZH-015", "EZH-019", "EZH-020"}:
                notes.append("Ordem dia/mês divergente em títulos RU e PT/EN; cotejo da data pendente.")
            if related == "EZH-002":
                notes.append("Inventário classifica como declaração; título local usa interrogatório e 23/24 abril.")
            if ident == "MER-003":
                notes.append("Ofício de 27/04 com anexo de 26/04: fac-símile não foi baixado nesta rodada.")
            if ident == "EZH-021B":
                notes.append("Extrato de 2018: seção local relacionada não substitui aquisição/cotejo desta edição.")
            row = {
                "frente": front, "id_inventario": ident,
                "inventario_origem": str(path.relative_to(ROOT)),
                "titulo_ou_tema": item.get("titulo") or item.get("title_ru") or item.get("tema", ""),
                "data_inventario": item.get("data") or item.get("date", ""),
                "tipo_inventario": item.get("tipo") or item.get("kind") or item.get("tipo_documento", ""),
                "classe_inventario": item.get("classe", ""),
                "integridade_inventario": item.get("integridade") or item.get("source_scope") or item.get("integridade_esperada", ""),
                "grupo_tematico_proposto": item.get("collection") or item.get("colecao") or "ezhov-1939-1940",
                "url_referencia": item["url"], "recurso_url_normalizado": url_key(item["url"]),
                "status_mapeamento": status, "documentos_site": ";".join(doc_ids),
                "registro_ezhov_relacionado": related,
                "idiomas_locais": ";".join(sorted({e["language"] for d in doc_ids for e in versions[d]})),
                "colecoes_atuais": ";".join(sorted({c for d in doc_ids for c in collections[d]})),
                "arquivos_locais": ";".join(e["file"] for d in doc_ids for e in versions[d]),
                "secao_pt": "", "linha_pt": "", "secao_ru_candidata": "", "linha_ru": "",
                "secao_en_candidata": "", "linha_en": "",
                "prioridade_inventario": item.get("priority") or item.get("prioridade", ""),
                "acao_proposta": action, "notas": " | ".join(n for n in notes if n),
            }
            if index is not None:
                for language, title_key in (("pt", "secao_pt"), ("ru", "secao_ru_candidata"), ("en", "secao_en_candidata")):
                    if index < len(headings[language]):
                        line, heading = headings[language][index]
                        row[title_key] = heading.lstrip("# ")
                        row["linha_" + language] = line
            mapped.append(row)
    OUT.mkdir(parents=True, exist_ok=True)
    save_csv("mapeamento.csv", mapped)
    (OUT / "mapeamento.json").write_text(json.dumps(mapped, ensure_ascii=False, indent=2) + "\n")
    for front, _ in groups:
        save_csv(front + ".csv", [r for r in mapped if r["frente"] == front])
    urls = defaultdict(list)
    for row in mapped:
        urls[row["recurso_url_normalizado"]].append(row)
    shared = [{"recurso_url": key, "registros": ";".join(r["frente"] + ":" + r["id_inventario"] for r in rows),
               "orientacao": "Mesmo recurso de consulta; pode conter peças distintas. Não deduplicar documentos apenas pela URL."}
              for key, rows in urls.items() if len(rows) > 1]
    save_csv("recursos-compartilhados.csv", shared)
    summary = {front: dict(Counter(r["status_mapeamento"] for r in mapped if r["frente"] == front)) for front, _ in groups}
    (OUT / "resumo.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
