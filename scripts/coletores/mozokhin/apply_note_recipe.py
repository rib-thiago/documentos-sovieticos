#!/usr/bin/env python3
"""Apply explicit, hash-bound editorial decisions to candidates; never canonical catalog."""
import argparse,copy,difflib,hashlib,json
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def apply(recipe_path,root):
    recipe=json.loads(recipe_path.read_text());decision=recipe['decision'];path=root/'units.json';units=json.loads(path.read_text());by={u['id']:u for u in units}
    selected=[by[r['id']] for r in recipe['units']]
    if all(u.get('provenance',{}).get('review_decision')==decision for u in selected):
        for u in selected:
            if sha((root/u['markdown']).read_bytes())!=u['markdown_sha256']:raise ValueError(u['id'])
        return {'already_applied':True}
    planned=[]
    for rec in recipe['units']:
        u=by[rec['id']];blob=(root/u['markdown']).read_bytes()
        if sha(blob)!=rec['expected_sha256'] or sha((root/u['raw']).read_bytes())!=rec['pdf_sha256']:raise ValueError(u['id'])
        text=blob.decode()
        for edit in rec['operations']:
            if text.count(edit['old'])!=1:raise ValueError((u['id'],edit['old']))
            text=text.replace(edit['old'],edit['new'],1)
        if rec['append_notes']:text=text.rstrip()+'\n\n'+'\n\n'.join(rec['append_notes'])+'\n'
        text=text.rstrip()+'\n'
        if sha(text.encode())!=rec['expected_result_sha256']:raise ValueError('Recipe result '+u['id'])
        planned.append((rec,u,blob,text))
    folder=root/'reviewed'/decision;folder.mkdir(parents=True,exist_ok=True)
    if not (folder/'units-before.json').exists():(folder/'units-before.json').write_bytes(path.read_bytes())
    report={'decision':decision,'scope':recipe['scope'],'catalog_changed':False,'units':[]}
    for rec,u,blob,text in planned:
        before=copy.deepcopy(u);digest=sha(text.encode());dest=folder/(u['id']+'.'+digest+'.ru.md');dest.write_text(text)
        (folder/(u['id']+'.diff')).write_text(''.join(difflib.unified_diff(blob.decode().splitlines(True),text.splitlines(True),fromfile=u['markdown'],tofile=str(dest.relative_to(root)))))
        images=[];vol=u['provenance']['edition'][-1]
        for page in rec['reviewed_pdf_pages']:
            image=root/'facsimile-checks'/'round3'/f'v{vol}-{page}.png'
            images.append({'path':str(image.relative_to(root)),'sha256':sha(image.read_bytes())})
        remaining=rec['remaining'];u.update(markdown=str(dest.relative_to(root)),markdown_sha256=digest,ready_for_import=not bool(remaining))
        u['issues']=(['Pendente: '+remaining] if remaining else [])+['OCR original preservado; revisão estrutural não equivale a revisão histórica integral.']
        u['provenance'].update(review_decision=decision,previous_markdown=before['markdown'],previous_markdown_sha256=before['markdown_sha256'],review_record=str((folder/'decision.json').relative_to(root)),footer_note_review_required=bool(remaining),editorial_review='note_ownership_partially_checked' if remaining else 'note_ownership_checked_against_facsimile',reviewed_pdf_pages=rec['reviewed_pdf_pages'])
        if rec.get('table_review'):u['provenance']['table_review']=rec['table_review']
        report['units'].append({'id':u['id'],'before':before,'after_markdown':u['markdown'],'after_sha256':digest,'remaining':remaining,'ready_for_import':u['ready_for_import'],'images':images})
    (folder/'decision.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    temp=path.with_suffix('.json.tmp');temp.write_text(json.dumps(units,ensure_ascii=False,indent=2)+'\n');temp.replace(path)
    return {'decision':decision,'processed':len(planned),'apt':sum(not rec['remaining'] for rec,_,_,_ in planned),'retained':sum(bool(rec['remaining']) for rec,_,_,_ in planned)}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('recipe',type=Path);p.add_argument('--root',type=Path,default=Path('temporario/coletas-quatro/mozokhin'));a=p.parse_args();print(json.dumps(apply(a.recipe,a.root)))
