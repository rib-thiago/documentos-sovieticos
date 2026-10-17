#!/usr/bin/env python3
"""Individualiza a compilação local sem reescrever seus bytes.

Executa uma gravação editorial recuperável e atualiza o índice de produção.
Não inicia servidor, coleta fontes, executa testes ou publica no Git.
Recusa sobrescrever peças existentes e exige backend encerrado.
"""
import copy
import csv
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import catalog as model
from backend.database import Repository
from backend.editorial import Editorial

PARENT = "confessionezhov"
COLLECTION = "yezhov-vs-stalin"
SUBCOLLECTION = COLLECTION + "/documentos-individualizados"
REPORT = ROOT / "docs/pesquisa/individualizacao-ezhov"
SOURCE_HASHES = {
    "ru": "2e699340fe48dd3abf50a0458977e78814b4c7476a2958ae281edc73f7e66150",
    "pt": "d2c3f873c7961cfa245ee17b001e006398c6727ced8a8b1702c0fc9a2c2bc318",
    "en": "46960cbba6696c38ba5f3af09fd1cbef6fd53c446fc9fcb321406cfb662201bb",
}

# Cada início é um título editorial conferido nas três versões. A peça de
# agosto inclui o segundo H2 (referência e corpo pertencem ao mesmo documento).
# As datas são rótulos da compilação, não novas determinações históricas.
PIECES = [
    ("ezh-001", 35, "18–20.04.1939", "interrogation_extract", "Extratos e resumo de interrogatório"),
    ("ezh-002", 69, "23/24.04.1939", "statement", "Declaração escrita"),
    ("ezh-003", 105, "26.04.1939", "interrogation_extract", "Interrogatório e ofício de encaminhamento"),
    ("ezh-004", 853, "30.04.1939", "interrogation_extract", "Extrato e resumo de interrogatório"),
    ("ezh-005", 869, "05.05.1939", "summary", "Resumo de interrogatório"),
    ("ezh-006", 883, "11.05.1939", "interrogation_extract", "Trechos de interrogatório"),
    ("ezh-007", 941, "17.05.1939", "summary", "Resumo de interrogatório"),
    ("ezh-008", 951, "16.06.1939", "interrogation_extract", "Trechos de interrogatório"),
    ("ezh-009", 987, "19.06.1939", "summary", "Resumo de interrogatório"),
    ("ezh-010", 1007, "21.06.1939", "interrogation_extract", "Trechos de interrogatório"),
    ("ezh-011", 1035, "25.06.1939", "interrogation_extract", "Trechos de interrogatório"),
    ("ezh-012", 1079, "29.06.1939", "interrogation_extract", "Trechos de interrogatório"),
    ("ezh-013", 1113, "02.07.1939", "interrogation_extract", "Trechos de interrogatório"),
    ("ezh-015", 1275, "08.07.1939", "interrogation_extract", "Trechos de interrogatório"),
    ("ezh-017", 1401, "21.07.1939", "confrontation_protocol", "Acareação com Zhukovskii — trechos"),
    ("ezh-018", 1447, "24.07.1939", "interrogation_extract", "Trechos de interrogatório"),
    ("ezh-019", 1509, "02.08.1939", "interrogation_extract", "Trechos de interrogatório"),
    ("ezh-020", 1607, "03.08.1939", "interrogation_extract", "Trechos de interrogatório"),
    ("ezh-021", 1635, "04.08.1939", "interrogation_extract", "Extrato de interrogatório"),
    ("ezh-022", 1939, "20.09.1939", "confrontation_protocol", "Acareação com Bulatov — referência e resumo"),
    ("ezh-023", 1947, "25.10.1939", "interrogation_extract", "Trechos de interrogatório"),
    ("ezh-025", 2033, "02.01.1940", "reference_note", "Encerramento da investigação — trechos"),
    ("ezh-026", 2069, "03.02.1940", "speech", "Declaração final em julgamento e comentários"),
    ("revisao-1998", 2219, "1998", "verdict_or_sentence", "Decisão de 1998 — excerto e comentários"),
]
NOTES = {
    "ezh-001": "Intervalo 18–20/04: preservado como uma peça, sem inventar três protocolos.",
    "ezh-002": "Títulos usam interrogatório e 23/24 de abril; corpo é declaração datada de 24/04. Títulos e corpo preservados.",
    "ezh-003": "Inclui a referência Lubianka, ofício de Beria de 27/04 e protocolo de 26/04 como publicados na compilação. Cotas externas divergentes não substituem as do corpo.",
    "ezh-006": "Título H1 em RU/PT, H2 em EN. Níveis preservados.",
    "ezh-007": "Título H1 em RU, H2 em PT/EN. Níveis preservados.",
    "ezh-012": "Título H1 em PT, H2 em RU/EN. Níveis preservados.",
    "ezh-013": "Título RU 07.02.39; PT 02.07.1939; EN 07.02.39 em notação mês/dia. Nenhuma data do corpo ou título foi corrigida.",
    "ezh-015": "Título RU 07.08.39; PT 08.07.1939; EN 07.08.39 em notação mês/dia. Cabeçalhos preservados.",
    "ezh-017": "Acareação: manter identificação das falas e comentário de repetição do depoimento de junho.",
    "ezh-018": "A passagem atribuída a Frinovskii e as respostas de Ezhov permanecem juntas, com sua moldura editorial.",
    "ezh-019": "Título RU 08.02.39; PT 02.08.1939; EN 08.02.39. Ordem dia/mês divergente; atribuições 02/03 de agosto devem ser cotejadas.",
    "ezh-020": "Título RU 08.03.39; PT 03.08.1939; EN 08.03.39. Inclui nota [*] sobre texto atribuído a 02/08 em outra edição.",
    "ezh-021": "Os H2 das linhas 1635 e 1639 formam uma só peça: título, referência Petrov/Jansen e extrato. Não criar um documento vazio com a referência isolada.",
    "ezh-022": "A seção publica referência/resumo de acareação; não apresenta protocolo integral.",
    "ezh-025": "Título local 02.01.1940/02.01.40; inventário externo propõe 01/02/1940. Data ISO mantida nula; não reinterpretar silenciosamente. Divergência Esaulov/Sergienko preservada no texto.",
    "ezh-026": "Declaração final e comentários editoriais permanecem juntos. Não representa a ata integral do julgamento.",
    "revisao-1998": "Título original fala em reabilitação; não foi alterado nem interpretado como concessão de reabilitação. Excerto, comentários e entrevista citada permanecem juntos.",
}


def main():
    editorial = Editorial(ROOT)
    try:
        current = model.load(ROOT)
        candidate = copy.deepcopy(current)
        parent_editions = {e["language"]: e for e in current["editions"] if e["document_id"] == PARENT}
        sources = {lang: (ROOT / edition["file"]).read_bytes() for lang, edition in parent_editions.items()}
        if set(sources) != set(SOURCE_HASHES) or any(model.sha256(raw) != SOURCE_HASHES[lang] for lang, raw in sources.items()):
            raise model.CatalogError("A compilação mudou desde a definição das fronteiras. Revisar os recortes; nenhum texto foi gravado.")
        lines = {lang: raw.splitlines(keepends=True) for lang, raw in sources.items()}
        ids = {doc["id"] for doc in current["documents"]}
        if any("confessionezhov-" + piece[0] in ids for piece in PIECES):
            raise model.CatalogError("Peças individualizadas já cadastradas; não sobrescrevendo edições posteriores.")
        if any(c["id"] == SUBCOLLECTION for c in current["collections"]):
            raise model.CatalogError("Subcoleção de destino já existe; não sobrescrevendo.")
        revision = editorial.revision()
        files, report = {}, []
        main_position = sum(m["collection_id"] == COLLECTION for m in candidate["memberships"])
        new_ids = []
        for position, (suffix, start, date_label, kind, label) in enumerate(PIECES):
            ident = "confessionezhov-" + suffix
            end = PIECES[position + 1][1] - 1 if position + 1 < len(PIECES) else None
            titles, derivations, piece_editions = {}, {}, []
            for lang in ("ru", "pt", "en"):
                raw = b"".join(lines[lang][start - 1:end])
                heading = lines[lang][start - 1].decode("utf-8").rstrip("\r\n")
                if not re.match(r"^#{1,2} ", heading):
                    raise model.CatalogError(f"Fronteira mudou em {lang}:{start}; revisar o recorte antes de gravar.")
                target = f"originais/ezhov/{ident}.{lang}.md"
                if (ROOT / target).exists():
                    raise model.CatalogError(f"Destino já existe: {target}")
                titles[lang] = re.sub(r"^#+\s+", "", heading)
                first_byte = sum(len(line) for line in lines[lang][:start - 1])
                segment = {
                    "parent_edition_id": parent_editions[lang]["id"],
                    "parent_file": parent_editions[lang]["file"],
                    "parent_sha256": model.sha256(sources[lang]),
                    "start_line": start, "end_line": end or len(lines[lang]),
                    "start_byte": first_byte, "end_byte_exclusive": first_byte + len(raw),
                    "slice_sha256": model.sha256(raw), "verbatim_slice": True,
                }
                derivations[lang] = segment
                content = raw.decode("utf-8")
                files[target] = content
                piece_editions.append({
                    "id": ident + ":" + lang, "document_id": ident,
                    "language": lang, "label": parent_editions[lang]["label"],
                    "file": target, "format": "markdown", "position": len(piece_editions),
                    "sha256": model.sha256(raw), "bytes": len(raw),
                    "editorial_status": "not_recorded", "extra": {},
                    "compatibility_fields": ["code", "label", "file", "format"],
                })
                report.append({"id": ident, "idioma": lang, "arquivo": target,
                               "titulo_original": titles[lang], "linha_inicial": start,
                               "linha_final": segment["end_line"], "bytes": len(raw),
                               "sha256": model.sha256(raw),
                               "blocos_separados_por_linha_vazia": len(re.split(r"\n\s*\n", content.strip())),
                               "observacoes": NOTES.get(suffix, "Fronteiras correspondentes; sem novo cotejo com edição externa.")})
            doc = {
                "id": ident, "kind": "document", "titles": titles,
                "document_type": kind,
                "historical_date": {"display": date_label, "value": None, "precision": "not_recorded"},
                "archive_reference": None, "author_label": None,
                "source": {"name": "Compilação de interrogatórios de Ezhov", "id": PARENT,
                           "url": "#/doc/confessionezhov?colecao=yezhov-vs-stalin"},
                "source_metadata": {
                    "original_language": "ru",
                    "compilation_derivation": {
                        "parent_document_id": PARENT,
                        "inventory_id": suffix.upper() if suffix.startswith("ezh-") else None,
                        "method": "verbatim_byte_ranges_v1", "editions": derivations,
                        "date_basis": "Rótulo português da compilação; sem normalização ISO ou correção histórica.",
                        "review_notes": NOTES.get(suffix, "Fronteiras editoriais correspondentes; não é novo cotejo de fonte externa."),
                        "alignment": "Estrutura herdada; nenhum alinhamento automático confirmado.",
                        "bibliographic_context": "Introdução e bibliografia geral preservadas na compilação confessionezhov; referências específicas mantidas no próprio trecho.",
                    },
                },
                "default_format": "markdown", "presentation": {"eyebrow": label},
                "extra": {},
                "compatibility_fields": ["id", "type", "title_pt", "title_ru", "title_en", "date",
                                         "document_type", "format", "eyebrow", "source_name", "source_id", "source_url", "languages"],
            }
            candidate["documents"].append(doc)
            candidate["editions"].extend(piece_editions)
            candidate["memberships"].extend([
                {"collection_id": COLLECTION, "document_id": ident, "position": main_position + position},
                {"collection_id": SUBCOLLECTION, "document_id": ident, "position": position},
            ])
            new_ids.append(ident)
        siblings = [c for c in candidate["collections"] if c["parent_id"] == COLLECTION]
        candidate["collections"].append({
            "id": SUBCOLLECTION, "slug": "documentos-individualizados", "parent_id": COLLECTION,
            "position": len(siblings),
            "titles": {"pt": "Documentos individualizados de Ezhov", "ru": "Документы Ежова — отдельные тексты"},
            "subtitle": "23 peças de 1939–1940 e um texto relativo à decisão de 1998 · RU/PT/EN",
            "description": "Recortes integrais das seções da compilação existente, com suas traduções e notas. Inclui extratos, resumos, declaração, acareações e manifestações judiciais; não são 24 protocolos integrais.",
            "source": {}, "presentation": {}, "extra": {},
            "compatibility_fields": ["id", "title_pt", "title_ru", "subtitle_pt", "description_pt", "document_ids"],
        })
        collection = next(c for c in candidate["collections"] if c["id"] == COLLECTION)
        collection["description"] += " Os documentos da compilação também estão disponíveis individualmente, com as traduções russa, portuguesa e inglesa preservadas."
        candidate["provenance"]["confessionezhov_individualization"] = {
            "parent_document_id": PARENT, "method": "verbatim_byte_ranges_v1",
            "documents": new_ids,
            "introduction": {lang: {"file": parent_editions[lang]["file"], "start_line": 1, "end_line": 34,
                                    "sha256": model.sha256(b"".join(lines[lang][:34]))} for lang in lines},
            "parent_files_unchanged": True,
            "historical_validation": "Não realizada; divergências preservadas no relatório e nos metadados.",
        }
        for name in model.FILES:
            if candidate[name] != current[name]:
                files[f"data/catalog/{name}.json"] = model.json_bytes(candidate[name]).decode("utf-8")
        queue_fields, _ = editorial.read_queue()
        queue_additions = io.StringIO(newline="")
        writer = csv.DictWriter(queue_additions, fieldnames=queue_fields)
        for suffix, _, _, _, _ in PIECES:
            ident = "confessionezhov-" + suffix
            doc = next(d for d in candidate["documents"] if d["id"] == ident)
            row = dict.fromkeys(queue_fields, "")
            row.update(chave=ident + ":individualizacao", prioridade="alta" if suffix in {
                "ezh-002", "ezh-013", "ezh-015", "ezh-019", "ezh-020", "ezh-025"} else "media",
                dificuldade="media", status="pendente", id=ident,
                colecoes="Yezhov vs Stalin / Documentos individualizados de Ezhov",
                titulo_ru=doc["titles"]["ru"], problema="individualizacao_compilacao",
                dificuldade_encontrada=NOTES.get(suffix, "Recorte literal; conferir metadados, notas e estrutura herdada entre idiomas."),
                acao_sugerida="Conferir RU/PT/EN na compilação; preservar o texto e registrar qualquer correção editorial futura.",
                arquivo_markdown=f"originais/ezhov/{ident}.ru.md",
                url_teste="http://localhost:8000/#/doc/" + ident,
                fonte="/#/doc/confessionezhov?colecao=yezhov-vs-stalin", trechos="[]")
            writer.writerow(row)
        queue_path = "docs/revisao-markdown/pendencias.csv"
        previous_queue = (ROOT / queue_path).read_bytes().decode("utf-8")
        files[queue_path] = previous_queue + ("" if previous_queue.endswith("\n") else "\r\n") + queue_additions.getvalue()
        files["data/manifest.json"] = model.json_bytes(model.export_manifest(candidate)).decode("utf-8")
        entity = {"kind": "batch", "id": "individualizacao-confessionezhov", "document_ids": [PARENT] + new_ids}
        preview = editorial.store_preview(revision, candidate, files, PARENT,
            [{"field": "Individualização de confessionezhov: 24 peças trilíngues, subcoleção e proveniência", "before": None, "after": new_ids}], entity=entity)
        repository = Repository(ROOT, ROOT / ".local/catalog.sqlite3", current, {})
        result = editorial.save(repository, {"preview_id": preview["preview_id"]})
        REPORT.mkdir(parents=True, exist_ok=True)
        with (REPORT / "recortes.csv").open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(report[0]))
            writer.writeheader()
            writer.writerows(report)
        (REPORT / "proveniencia.json").write_bytes(model.json_bytes({
            "operation": result, "source_editions": parent_editions,
            "documents": [d for d in candidate["documents"] if d["id"] in new_ids],
            "segments": report,
        }))
        print(json.dumps({"documents": len(new_ids), "editions": len(report), "history_id": result["history_id"],
                          "collection": SUBCOLLECTION, "index_updated": True}, ensure_ascii=False, indent=2))
    finally:
        editorial.close()


if __name__ == "__main__":
    try:
        main()
    except model.CatalogError as error:
        sys.exit(str(error))
