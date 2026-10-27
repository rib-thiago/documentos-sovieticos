"""Fontes de demonstração locais explicitamente escolhidas pelo responsável.

Não cadastra, não publica e não expõe a árvore temporario/.
"""
from pathlib import Path

PILOTS = {
    'zinoviev-425': ('Zinoviev · d.425', 'rgaspi._f.17._op.171._d.425_zinovev._zasluzhennyy_prigovor-1.pdf'),
    'zinoviev-426': ('Zinoviev · d.426', 'rgaspi._f.17._op.171._d.426_zinovev-zasluzhennyy_prigovor_-2.pdf'),
}


def pilot_file(root, identifier):
    if identifier not in PILOTS:
        return None
    directory = (Path(root) / 'temporario/Zinoviev/Sentença Merecida').resolve()
    target = directory / PILOTS[identifier][1]
    if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(directory):
        return None
    return target


def listing(root):
    return {'items': [{'id': identifier, 'title': title,
                       'url': '/api/editorial/pdf-pilots/' + identifier + '/file',
                       'bytes': target.stat().st_size, 'filename': target.name}
                      for identifier, (title, _) in PILOTS.items()
                      if (target := pilot_file(root, identifier)) is not None]}
