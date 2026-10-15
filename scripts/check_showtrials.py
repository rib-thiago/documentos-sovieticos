"""Confere a fidelidade de todo o acervo ShowTrials à exportação portátil."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(source):
    manifest = json.loads((ROOT / "data/manifest.json").read_text())
    originals = {c["id"]: c for c in json.loads((source / "catalogos/colecoes.json").read_text())}
    source_docs = {d["document_post_id"]: d for d in json.loads((source / "catalogos/documentos.json").read_text())}
    docs = {d["id"]: d for d in manifest["documents"]}
    assert len(docs) == len(manifest["documents"]) == len(source_docs) == 2179

    memberships, subcollections = set(), set()
    imported = [c for c in manifest["collections"] if "document_ids" in c]
    assert len(imported) == 9
    for collection in imported:
        collection_members = []
        for sub in collection["subcollections"]:
            subcollections.add(sub["source_id"])
            original = originals[sub["source_id"]]
            expected = ["showtrials-" + d["id"] for d in original["documentos"]]
            assert sub["document_ids"] == expected, sub["id"]
            assert sub["source_url"] == original["url"]
            for member in original["documentos"]:
                doc_id = "showtrials-" + member["id"]
                if doc_id not in collection_members:
                    collection_members.append(doc_id)
                memberships.add(doc_id)
                doc = docs[doc_id]
                assert doc["source_id"] == member["id"]
                assert doc["source_url"] == member["url"]
                assert doc["title_ru"] == member["titulo"]
                raw = (source / member["arquivo_md"]).read_bytes()
                expected_body = raw.partition(b"\n---\n\n")[2]
                assert expected_body
                ru = next(l for l in doc["languages"] if l["code"] == "ru")
                assert (ROOT / ru["file"]).read_bytes() == expected_body, doc_id
        assert collection["document_ids"] == collection_members
    assert subcollections == set(originals) - {"853"}
    assert memberships == set(docs), "Documento sem subcoleção"
    assert {d["source_id"] for d in docs.values()} == set(source_docs)
    all_docs = list(docs.values()) + [d for c in manifest["collections"] for d in c.get("documents", [])]
    all_ids = [d["id"] for d in all_docs]
    assert len(all_ids) == len(set(all_ids)), "ID duplicado no manifesto"
    for doc in all_docs:
        for lang in doc["languages"]:
            assert (ROOT / lang["file"]).is_file(), lang["file"]
    print("OK: 2.179 corpos idênticos à fonte; nove coleções e 28 subcoleções; ordem e vínculos preservados; IDs únicos e idiomas locais disponíveis.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    check(parser.parse_args().source)
