"""Converte todo o ShowTrials e gera uma fila editorial em português, sem rede.

python3 scripts/convert_showtrials_all.py PACOTE --apply
Sem --apply, faz a conferência e grava apenas os relatórios.
As 31 seleções já revisadas têm precedência sobre as regras automáticas.
"""

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import prepare_markdown as base

ROOT = base.ROOT
OUT = ROOT / "docs/revisao-markdown"
POLICY = "mass-v1"
LABEL = re.compile(
    r"^(?:ПРОТОКОЛ(?:\s+(?:ДОПРОСА|ОЧНОЙ СТАВКИ))?|ДОПРОС(?:\s+.+)?|"
    r"ОБВИНИТЕЛЬНОЕ ЗАКЛЮЧЕНИЕ|ФОРМУЛА ОБВИНЕНИЯ|ПРИГОВОР|"
    r"ЗАЯВЛЕНИЕ|ПРИЛОЖЕНИЕ(?:\s*№?\s*\d.*)?|ВЫПИСКА ИЗ ПРОТОКОЛА.*|"
    r"ЧАСТЬ\s+[IVXХ\d]+.*|ГЛАВА\s+[IVXХ\d]+.*|"
    r"ВВЕДЕНИЕ\.?|ЗАКЛЮЧЕНИЕ\.?|ЗАКЛЮЧЕНИЯ\.?|"
    r"ПОСЛЕДНЕЕ СЛОВО.*|СУДЕБНЫЕ ПРЕНИЯ.*|СПИСОК СВИДЕТЕЛЕЙ\.?)$", re.I)
ROMAN = re.compile(r"^([IVX]+)\.\s+\S", re.I)
ARABIC = re.compile(r"^(\d{1,2})\.\s+[А-ЯЁA-Z]")
POEM = re.compile(r"(?:КОЛЫБЕЛЬНАЯ ПЕСНЯ|ЭПИГРАММА|СТИХОТВОРЕНИ[ЕЯ])", re.I)
PRIORITY = {"urgente": 0, "alta": 1, "media": 2, "baixa": 3, "sem_pendencia": 4}


class DocumentHTML(base.SourceHTML):
    def __init__(self, source):
        self.tags = Counter()
        self.table_depth = 0
        self.paragraph_info = []
        self.info = None
        self.images = []
        self.links = []
        super().__init__(source)

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1
        attributes = dict(attrs)
        if tag == "table":
            self.table_depth += 1
        if tag == "p":
            self.info = {"in_table": bool(self.table_depth)}
        if tag == "img":
            self.images.append({k: attributes.get(k, "") for k in ("src", "alt")})
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        super().handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        count = len(self.paragraphs)
        info = self.info
        super().handle_endtag(tag)
        if len(self.paragraphs) > count:
            self.paragraph_info.append(info)
        if tag == "p":
            self.info = None
        if tag == "table":
            self.table_depth = max(self.table_depth - 1, 0)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


def issue(code, priority, difficulty, detail, action, locations=None):
    return {"code": code, "priority": priority, "difficulty": difficulty,
            "detail": detail, "action": action, "locations": locations or []}


def automatic_headings(parsed, plain, document_type):
    positions = defaultdict(list)
    for i, text in enumerate(plain):
        positions[base.key(text)].append(i)
    candidates, doubtful = [], []
    poetry = document_type == "poem"
    roman_present = any(c and ROMAN.match(t) and not info["in_table"]
                        for (c, t), info in zip(parsed.paragraphs, parsed.paragraph_info))
    standalone = [i for i, ((c, t), info) in enumerate(zip(parsed.paragraphs, parsed.paragraph_info))
                  if c and not info["in_table"] and re.fullmatch(r"[IVX]+\.?", t)]
    for i, ((centered, text), info) in enumerate(zip(parsed.paragraphs, parsed.paragraph_info)):
        if POEM.search(text) and centered:
            poetry = True
        if not centered or info["in_table"]:
            continue
        level, evidence, confidence = None, "", "alta"
        previous = parsed.paragraphs[i - 1] if i else (False, "")
        if previous == (True, "ДОПРОС") or previous == [True, "ДОПРОС"]:
            # Apenas o nome curto após um marcador explícito, sem juntar blocos.
            if len(text) <= 180 and not re.search(r"[?!:]", text):
                level, evidence = 2, "nome centralizado imediatamente após ДОПРОС"
        if LABEL.fullmatch(text):
            level, evidence = 2, "rótulo estrutural explícito centralizado"
        elif not poetry and ROMAN.match(text):
            level, evidence, confidence = 2, "seção romana centralizada", "media"
        elif not poetry and ARABIC.match(text):
            level, evidence, confidence = (3 if roman_present else 2), "seção árabe centralizada", "media"
        elif not poetry and i in standalone and len(standalone) >= 2:
            # Marcadores de partes mantêm seus nomes originais, sem criar resumos.
            level, evidence, confidence = 2, "marcador romano centralizado em série", "media"
        if level is None:
            continue
        if text == "ДОПРОС" and i + 1 < len(parsed.paragraphs):
            next_centered, next_text = parsed.paragraphs[i + 1]
            if next_centered and len(next_text) <= 180 and not re.search(r"[?!:]", next_text):
                continue
        matches = positions.get(base.key(text), [])
        if len(text) > 240 or "\n" in text or len(matches) != 1 or "\n" in plain[matches[0]]:
            doubtful.append({"html_paragraph": i, "text": text[:240], "matching_blocks": matches[:12],
                             "reason": "título repetido, comprido, repartido ou sem correspondência única"})
            continue
        block = matches[0]
        candidates.append({"block": block, "level": level, "text": plain[block],
                           "html_text": text, "html_paragraph": i,
                           "evidence": evidence, "confidence": confidence})
    # Um cabeçalho genérico no começo de um texto curto não é seção interna.
    if len(candidates) == 1 and candidates[0]["block"] < 6 and LABEL.fullmatch(candidates[0]["html_text"]):
        candidates = []
    headings = sorted({h["block"]: h for h in candidates}.values(), key=lambda h: h["block"])
    return headings, doubtful


def review_issues(parsed, plain, headings, doubtful, deferred=None):
    issues = []
    chars = sum(map(len, plain))
    cells = parsed.tags["td"] + parsed.tags["th"]
    if parsed.tags["table"]:
        issues.append(issue("tabelas_linearizadas", "urgente" if cells >= 20 else "alta", "alta",
            f"O HTML contém {parsed.tags['table']} tabela(s), {parsed.tags['tr']} linha(s) e {cells} célula(s). A extração TXT perdeu as relações entre células; esta conversão mantém o texto linear.",
            "Comparar a tabela na fonte e reconstruir suas linhas/colunas em Markdown. Conferir números, nomes e totais antes de usar a tabela como evidência."))
    if parsed.images:
        issues.append(issue("imagens_sem_transcricao_confirmada", "urgente" if chars < 800 else "alta", "alta",
            f"Há {len(parsed.images)} imagem(ns) no HTML. Não foi extraído ou validado texto de imagem; o Markdown conserva apenas o corpo textual já existente.",
            "Abrir a fonte e verificar se as imagens são fac-símiles com conteúdo documental. Transcrever/reinserir a imagem quando necessário; não presumir que o TXT reproduz o fac-símile.",
            parsed.images[:8]))
    if parsed.tags["script"] or parsed.tags["style"]:
        issues.append(issue("possivel_texto_tecnico", "urgente", "media",
            "O HTML contém script/style e o extrator histórico não os eliminava explicitamente. O TXT foi preservado, sem apagar trechos por suposição.",
            "Comparar HTML e Markdown e retirar eventual código técnico que tenha entrado no texto, registrando a correção."))
    if doubtful:
        issues.append(issue("titulos_ambiguos", "alta" if chars >= 20000 else "media", "media",
            f"{len(doubtful)} candidato(s) a título não foram promovidos por repetição, tamanho ou correspondência ambígua com os blocos TXT.",
            "Conferir os trechos indicados no HTML; acrescentar #/##/### apenas nos títulos confirmados, mantendo o texto dos blocos.", doubtful))
    if deferred:
        issues.append(issue("decisao_editorial_pendente", "alta", "media", deferred,
            "Conferir a estrutura indicada na fonte e decidir os títulos manualmente; o documento já foi convertido com seus sinais literais preservados."))
    if len(headings) <= 1 and (chars >= 30000 or len(plain) >= 150):
        issues.append(issue("texto_longo_sem_secoes_suficientes", "urgente" if chars >= 100000 else "alta", "alta",
            f"Texto com {chars} caracteres, {len(plain)} blocos e {len(headings)} título(s). Não há divisões internas suficientes identificadas com segurança.",
            "Revisar o HTML procurando mudanças de documento, títulos, anexos e interrogados. Não criar um título para cada pergunta/fala nem dividir por número de caracteres."))
    if parsed.links:
        files = [link for link in parsed.links if re.search(r"\.(?:pdf|docx?|jpe?g|png|djvu)(?:[?#]|$)", link, re.I)]
        issues.append(issue("links_nao_reconstruidos", "alta" if files else "baixa", "baixa",
            f"O HTML tem {len(parsed.links)} link(s), incluindo {len(files)} para arquivos/imagens. Os alvos dos links foram perdidos no TXT; os rótulos textuais existentes continuam preservados.",
            "Recolocar os links documentais e os vínculos de notas a partir do HTML; conferir primeiro os links para anexos ou fac-símiles.", files[:12] or parsed.links[:8]))
    if parsed.tags["ul"] or parsed.tags["ol"]:
        issues.append(issue("listas_sem_marcacao", "media", "media",
            f"Há {parsed.tags['ul'] + parsed.tags['ol']} lista(s) HTML. A extração anterior pode ter achatado itens sem separadores; o conversor não inventou limites novos.",
            "Comparar os itens na fonte e recuperar a marcação de lista quando os limites estiverem claros."))
    if parsed.heading_tags:
        issues.append(issue("cabecalhos_html_nativos", "alta", "media",
            f"Há {parsed.heading_tags} cabeçalho(s) HTML nativo(s) fora do padrão predominante deste snapshot.",
            "Conferir e recuperar a hierarquia das tags h1–h6 na fonte."))
    return issues


def collection_paths(manifest):
    paths = defaultdict(list)
    for collection in manifest["collections"]:
        for sub in collection.get("subcollections", []):
            for doc_id in sub["document_ids"]:
                paths[doc_id].append(collection["title_pt"] + " / " + sub["title_pt"])
    return paths


def write_reports(records, applied):
    OUT.mkdir(parents=True, exist_ok=True)
    queue = OUT / "pendencias.csv"
    previous = {}
    if queue.exists():
        with queue.open(encoding="utf-8", newline="") as file:
            previous = {r["chave"]: r for r in csv.DictReader(file)}
    fields = ["chave", "prioridade", "dificuldade", "status", "id", "colecoes", "titulo_ru", "problema",
              "dificuldade_encontrada", "acao_sugerida", "arquivo_markdown", "url_teste", "fonte", "trechos", "notas_do_revisor"]
    entries = []
    for record in records:
        for problem in record["issues"]:
            stable = record["id"] + ":" + problem["code"]
            old = previous.get(stable, {})
            entries.append({"chave": stable, "prioridade": problem["priority"], "dificuldade": problem["difficulty"],
                "status": old.get("status", "pendente"), "id": record["id"], "colecoes": " | ".join(record["collections"]),
                "titulo_ru": record["title_ru"], "problema": problem["code"], "dificuldade_encontrada": problem["detail"],
                "acao_sugerida": problem["action"], "arquivo_markdown": record["markdown"],
                "url_teste": "http://localhost:8000/#/doc/" + record["id"], "fonte": record["source_url"],
                "trechos": json.dumps(problem["locations"], ensure_ascii=False), "notas_do_revisor": old.get("notas_do_revisor", "")})
    entries.sort(key=lambda r: (PRIORITY[r["prioridade"]], int(r["id"].removeprefix("showtrials-")), r["problema"]))
    with queue.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(entries)
    overview = ["id", "colecoes", "titulo_ru", "metodo", "blocos_preservados", "titulos", "prioridade", "pendencias", "arquivo_markdown", "url_teste", "fonte"]
    with (OUT / "acervo-completo.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=overview)
        writer.writeheader()
        for record in records:
            writer.writerow(dict(zip(overview, [record["id"], " | ".join(record["collections"]), record["title_ru"], record["method"],
                record["blocks"], len(record["headings"]), record["priority"], len(record["issues"]), record["markdown"],
                "http://localhost:8000/#/doc/" + record["id"], record["source_url"]])))
    summary = {"policy": POLICY, "aplicado": applied, "documentos": len(records),
        "blocos_preservados": sum(r["blocks"] for r in records), "titulos": sum(len(r["headings"]) for r in records),
        "documentos_com_indice": sum(bool(r["headings"]) for r in records),
        "documentos_sem_titulos_confirmados": sum(not r["headings"] for r in records),
        "documentos_por_prioridade": dict(Counter(r["priority"] for r in records)),
        "ocorrencias_por_problema": dict(Counter(e["problema"] for e in entries)),
        "pendencias": len(entries), "revisoes_preservadas": sum(r["method"] == "revisado" for r in records)}
    (OUT / "lote-integral.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "diagnosticos.json").write_text(json.dumps({"policy": POLICY, "documents": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Fila de revisão do ShowTrials", "",
        "O lote converte todos os documentos; as prioridades abaixo indicam dificuldades editoriais e perdas herdadas da extração TXT. Igualdade com o TXT não garante reprodução integral de tabelas, imagens ou links do HTML.", "",
        "A fila completa está em [pendencias.csv](pendencias.csv). Abra-a no LibreOffice Calc e filtre `prioridade`, `colecoes` ou `problema`. Cada linha explica a dificuldade, sugere a correção e aponta para o Markdown, o teste local e a fonte. As colunas `status` e `notas_do_revisor` são editáveis e preservadas em novas auditorias. Os nomes dos problemas e as orientações estão em português; os títulos russos identificam os documentos sem traduções inventadas.", "",
        "- **urgente**: tabelas maiores sem relações entre células, imagens com pouco texto, possível código técnico ou textos muito longos sem seções suficientes.",
        "- **alta**: tabelas menores, imagens em textos, anexos externos, títulos ambíguos em textos longos e decisões editoriais pendentes.",
        "- **media**: listas e candidatos a títulos que precisam de conferência.",
        "- **baixa**: recuperação de links que não apontam diretamente para arquivos.", "",
        f"Total: **{len(records)} documentos**, **{summary['blocos_preservados']} blocos** e **{summary['titulos']} títulos**. Prioridades por documento: " + ", ".join(f"{k}: {v}" for k, v in sorted(summary["documentos_por_prioridade"].items(), key=lambda p: PRIORITY[p[0]])) + ".", "",
        "## Documentos urgentes", "", "| Documento | Coleção/subcoleção | Dificuldade | Abrir |", "| --- | --- | --- | --- |"]
    for record in records:
        if record["priority"] == "urgente":
            problems = "; ".join(p["detail"] for p in record["issues"] if p["priority"] == "urgente")
            lines.append(f"| {record['id']} | {'; '.join(record['collections']).replace('|', '/')} | {problems.replace('|', '/')} | [Site](http://localhost:8000/#/doc/{record['id']}) · [Markdown](../../{record['markdown']}) · [Fonte]({record['source_url']}) |")
    lines.extend(["", "## Como corrigir", "",
        "1. Abra o documento pela URL de teste e compare com a fonte/HTML coletado. O campo `trechos` da planilha indica os candidatos problemáticos quando disponíveis.",
        "2. Edite o arquivo `.ru.md` indicado. Para um título, acrescente `##`, `###` ou `####` no bloco existente; evite fundir ou repartir os parágrafos usados no pareamento.",
        "3. Marque `status` como `em_revisao` ou `corrigido` e descreva a mudança em `notas_do_revisor`. A prioridade original registra o motivo da triagem e não é uma declaração de erro confirmado.",
        "4. A conferência estrita detectará alterações editoriais em relação à receita. Para registrar somente alterações de títulos preservando o corpo, use `python3 scripts/convert_showtrials_all.py --accept-headings showtrials-ID`. Mudanças de tabelas, conteúdo ou limites de parágrafo precisam de conferência editorial própria; não apague o TXT de referência.", "",
        "A reaplicação do lote recusa sobrescrever Markdown diferente da receita. As 31 versões previamente revisadas mantêm seus títulos. Documentos sem divisões comprovadas recebem Markdown literal e podem continuar sem índice; isso, por si só, não é erro."])
    (OUT / "REVISAO-PRIORITARIA.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def convert(package, apply=False):
    manifest_path = ROOT / "data/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    docs = {d["source_id"]: d for d in manifest["documents"]}
    paths = collection_paths(manifest)
    selection = json.loads(base.REVIEW.read_text(encoding="utf-8"))
    reviews = {d["id"]: d for d in selection["documents"]}
    deferred = {d["id"]: d["reason"] for d in selection["deferred"]}
    old = json.loads(base.RECIPES.read_text(encoding="utf-8"))["documents"] if base.RECIPES.exists() else []
    previous = {r["id"]: r for r in old}
    source_dir = next((p for p in (package / "original/local/posts-json", package / "originais/showtrials/posts-json") if p.is_dir()), None)
    if source_dir is None:
        raise ValueError("Pacote sem JSONs WordPress")
    records, prepared, seen = [], [], set()
    for file in sorted(source_dir.glob("*.json")):
        for post in json.loads(file.read_text(encoding="utf-8")):
            sid = str(post["id"])
            if sid not in docs:
                continue
            if sid in seen:
                raise ValueError(f"ID repetido: {sid}")
            seen.add(sid)
            doc = docs[sid]
            doc_id = doc["id"]
            original = f"originais/showtrials/{doc_id}.ru.txt"
            raw = (ROOT / original).read_bytes()
            plain = base.blocks(raw.decode("utf-8"))
            source = post["content"]["rendered"]
            if plain != base.blocks(base.legacy_text(source)):
                raise ValueError(f"HTML e TXT diferentes: {doc_id}")
            parsed = DocumentHTML(source)
            assert len(parsed.paragraphs) == len(parsed.paragraph_info)
            auto, doubtful = automatic_headings(parsed, plain, doc["document_type"])
            if doc_id in previous and previous[doc_id].get("method") == "revisao_local":
                base.check_conversion(previous[doc_id])
                headings = previous[doc_id]["headings"]
                method = "revisao_local"
            elif doc_id in reviews:
                headings = base.reviewed_headings(reviews[doc_id], parsed, plain)
                doubtful = []  # As escolhas do lote revisado substituem os candidatos automáticos.
                method = "revisado"
            else:
                headings = [] if doc_id in deferred else auto
                method = "automatico" if headings else "literal_sem_titulos"
            problems = review_issues(parsed, plain, headings, doubtful, deferred.get(doc_id))
            priority = min((p["priority"] for p in problems), key=PRIORITY.get, default="sem_pendencia")
            recipe = {"id": doc_id, "original": original, "markdown": original.removesuffix(".txt") + ".md",
                "original_sha256": base.digest(raw), "html_sha256": base.digest(source.encode("utf-8")),
                "source_json": file.relative_to(package).as_posix(), "source_url": doc["source_url"],
                "blocks": len(plain), "headings": headings, "method": method, "policy": POLICY}
            markdown = base.render_conversion(raw.decode("utf-8"), headings)
            target = ROOT / recipe["markdown"]
            if target.exists() and target.read_text(encoding="utf-8") != markdown:
                raise ValueError(f"Revisão local protegida; não será sobrescrita: {doc_id}")
            ru = next(l for l in doc["languages"] if l["code"] == "ru")
            if ru["file"] not in {original, recipe["markdown"]}:
                raise ValueError(f"Caminho russo local diferente: {doc_id}")
            prepared.append((recipe, markdown, ru))
            records.append({**recipe, "title_ru": doc["title_ru"], "collections": paths[doc_id],
                            "priority": priority, "issues": problems})
        print(f"Conferido {file.name}: {len(seen)} documentos", flush=True)
    if seen != set(docs) or len(docs) != 2179:
        raise ValueError("Snapshot incompleto; nenhum documento foi aplicado")
    # Todo conteúdo, destino e revisão local já foi conferido antes da primeira escrita.
    if apply:
        for recipe, text, ru in prepared:
            (ROOT / recipe["markdown"]).write_text(text, encoding="utf-8")
            ru.update(file=recipe["markdown"], format="markdown")
        base.RECIPES.write_text(json.dumps({"version": 2, "scope": "all_showtrials", "policy": POLICY,
            "documents": sorted((r for r, _, _ in prepared), key=lambda r: r["id"])}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        base.check()
    records.sort(key=lambda r: (PRIORITY[r["priority"]], int(r["id"].removeprefix("showtrials-"))))
    summary = write_reports(records, apply)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def accept_headings(doc_id):
    """Registra títulos editados pelo usuário, exigindo igualdade de todos os blocos."""
    catalog = json.loads(base.RECIPES.read_text(encoding="utf-8"))
    recipe = next(r for r in catalog["documents"] if r["id"] == doc_id)
    raw = (ROOT / recipe["original"]).read_bytes()
    if base.digest(raw) != recipe["original_sha256"]:
        raise ValueError("TXT original alterado")
    plain = base.blocks(raw.decode("utf-8"))
    edited = (ROOT / recipe["markdown"]).read_text(encoding="utf-8")
    current = base.blocks(edited)
    if len(current) != len(plain):
        raise ValueError("Os limites dos blocos foram alterados; requer revisão editorial própria")
    headings = []
    for i, (source, text) in enumerate(zip(plain, current)):
        match = re.match(r"^(#{1,6}) (.+)$", text)
        if match:
            headings.append({"block": i, "level": len(match[1]), "text": source, "html_text": source,
                             "evidence": "título registrado por revisão editorial local"})
    if base.render_conversion(raw.decode("utf-8"), headings) != edited:
        raise ValueError("Há alterações além dos marcadores de título; nenhum registro foi atualizado")
    recipe.update(headings=headings, method="revisao_local")
    base.RECIPES.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    base.check_conversion(recipe)
    print(f"Revisão de títulos registrada: {doc_id}. As demais pendências continuam na planilha.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, nargs="?")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--accept-headings", metavar="ID")
    args = parser.parse_args()
    if args.accept_headings:
        accept_headings(args.accept_headings)
    elif args.package:
        convert(args.package, args.apply)
    else:
        parser.error("Informe o pacote ou --accept-headings ID")
