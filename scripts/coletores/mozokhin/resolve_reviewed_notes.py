#!/usr/bin/env python3
"""Aplicar decisões de fronteira conferidas nas imagens, somente na área de trabalho.

Executar depois de prepare_books.py. Recusa versões diferentes das conferidas.
Não escreve catálogo ou textos públicos; guarda originais, diferenças e decisão.
"""
import argparse
import copy
import difflib
import hashlib
import json
from pathlib import Path

EXPECTED = {
    'mozokhin-2013-v2-294': '12d557adbea16dc085bd4d4cac9ab28dcbe0b782a5233d92812d3735cca82feb',
    'mozokhin-2013-v2-295': 'a2d8d043164ca02f11251d61c4bf67982020a866f474cdcdd701de9d0354131d',
}
PDF = 'eac5b4ed1735f5cdc7f46a9725d65036b03a4e264da1d8a34373954fae906614'
DECISION = 'mozokhin-v2-294-295-notes-20261021'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Passagem esperada ausente ou ambígua: '+repr(old))
    return text.replace(old, new, 1)


def resolve(root):
    path=root/'units.json'
    units=json.loads(path.read_text())
    selected={u['id']:u for u in units if u['id'] in EXPECTED}
    if len(selected)!=2:raise ValueError('Par de documentos incompleto')
    if all(u.get('provenance',{}).get('review_decision')==DECISION for u in selected.values()):
        for u in selected.values():
            if sha((root/u['markdown']).read_bytes())!=u['markdown_sha256']:raise ValueError('Versão revista divergente')
        return {'already_applied':True,'decision':DECISION}
    before={}
    for uid,u in selected.items():
        blob=(root/u['markdown']).read_bytes()
        if sha(blob)!=EXPECTED[uid] or u['raw_sha256']!=PDF or sha((root/u['raw']).read_bytes())!=PDF:
            raise ValueError('Fonte ou candidato diferente da versão conferida: '+uid)
        before[uid]=blob.decode()
    a,b=sorted(selected)
    note13='Опубликовано «Правда», 22 августа 1940 г. № 233'
    note14='Опубликовано «Правда» 24 августа 1940 г. № 235'
    note15='Опубликовано «Правда» 24 августа 1940 г. № 235'
    first=once(before[a],'Троцкого13.','Троцкого[^13].').rstrip()+'\n\n[^13]: '+note13+'\n'
    second=once(before[b],'\n13\n'+note13+'\n14\n'+note14+'\n387\n','\n')
    second=once(second,'\n388\n','\n')
    second=once(second,'15 '+note15,'')
    second=once(second,'\n389\n','\n')
    second=once(second,'окружения14.','окружения[^14].')
    second=once(second,'челе15.','челе[^15].').rstrip()+'\n\n[^14]: '+note14+'\n\n[^15]: '+note15+'\n'
    after={a:first,b:second}
    review=root/'reviewed'/DECISION;review.mkdir(parents=True,exist_ok=True)
    snapshot=review/'units-before.json'
    if not snapshot.exists():snapshot.write_bytes(path.read_bytes())
    report={'decision':DECISION,'physical_pdf_pages':[388,389,390],'printed_pages':[387,388,389],
        'basis':'Conferência visual das três páginas; chamada 13 no nº 294, chamadas 14/15 no nº 295.',
        'scope':'Realocação explícita da nota 13; conversão de chamadas/definições em notas Markdown; remoção de três fólios impressos isolados.',
        'limitations':'Texto OCR e suas grafias preservados; revisão estrutural não valida alegações históricas nem corrige ortografia.',
        'catalog_changed':False,'units':[]}
    for uid in sorted(selected):
        u=selected[uid];content=after[uid].encode();digest=sha(content);target=review/(uid+'.'+digest+'.ru.md')
        if target.exists() and target.read_bytes()!=content:raise ValueError('Destino conflitante')
        target.write_bytes(content)
        diff=''.join(difflib.unified_diff(before[uid].splitlines(True),after[uid].splitlines(True),fromfile=u['markdown'],tofile=str(target.relative_to(root))))
        (review/(uid+'.diff')).write_text(diff)
        report['units'].append({'id':uid,'before':copy.deepcopy(u),'after_markdown':str(target.relative_to(root)),'after_sha256':digest})
        u['markdown']=str(target.relative_to(root));u['markdown_sha256']=digest;u['ready_for_import']=True
        u['issues']=['OCR existente preservado; revisão editorial de conteúdo e metadados ainda pendente.']
        u['provenance'].update({'review_decision':DECISION,'footer_note_review_required':False,
            'editorial_review':'structure_and_note_ownership_checked_against_facsimiles',
            'previous_markdown_sha256':EXPECTED[uid],'note_ownership':{'13':a,'14':b,'15':b},
            'review_record':str((review/'decision.json').relative_to(root))})
    (review/'decision.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(units,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
    return {'decision':DECISION,'resolved':sorted(selected),'ready_total':sum(u['ready_for_import'] for u in units)}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path('temporario/coletas-quatro/mozokhin'))
    print(json.dumps(resolve(parser.parse_args().root),ensure_ascii=False))
