"""Impede que importadores anteriores criem duas fontes de verdade."""


def ensure_legacy_manifest_write_allowed(root):
    if (root / "data/catalog/provenance.json").exists():
        raise ValueError(
            "Este projeto já usa data/catalog/ como catálogo principal. "
            "Esta operação antiga escreve diretamente em data/manifest.json e foi interrompida antes da escrita. "
            "Use python3 -m backend.catalog check/export; novas importações devem ser adaptadas ao catálogo normalizado. "
            "As auditorias sem escrita e os verificadores anteriores continuam disponíveis."
        )
