"""Confere a fidelidade da importação piloto à exportação portátil."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(source):
    manifest = json.loads((ROOT / "data/manifest.json").read_text())
    imported = next(c for c in manifest["collections"] if c["id"] == "centro-de-leningrado")
    originals = {c["id"]: c for c in json.loads((source / "catalogos/colecoes.json").read_text())}
    docs = {d["id"]: d for d in imported["documents"]}
    assert len(docs) == len(imported["documents"]) == 175
    assert len(imported["subcollections"]) == 4
    memberships = set()
    for sub in imported["subcollections"]:
        original = originals[sub["source_id"]]
        expected = ["showtrials-" + d["id"] for d in original["documentos"]]
        assert sub["document_ids"] == expected, sub["id"]
        assert sub["source_url"] == original["url"]
        for member in original["documentos"]:
            doc_id = "showtrials-" + member["id"]
            memberships.add(doc_id)
            doc = docs[doc_id]
            assert doc["source_id"] == member["id"]
            assert doc["source_url"] == member["url"]
            assert doc["title_ru"] == member["titulo"]
            raw = (source / member["arquivo_md"]).read_bytes()
            expected_body = raw.partition(b"\n---\n\n")[2]
            assert expected_body
            assert (ROOT / doc["languages"][0]["file"]).read_bytes() == expected_body, doc_id
    assert memberships == set(docs), "Documento sem subcoleção"
    all_ids = [d["id"] for c in manifest["collections"] for d in c["documents"]]
    assert len(all_ids) == len(set(all_ids)), "ID duplicado no manifesto"
    for collection in manifest["collections"]:
        for doc in collection["documents"]:
            for lang in doc["languages"]:
                assert (ROOT / lang["file"]).is_file(), lang["file"]
    print("OK: 175 corpos idênticos à fonte; quatro subcoleções com ordem e vínculos preservados; IDs únicos e todos os idiomas locais disponíveis.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    check(parser.parse_args().source)
