#!/usr/bin/env python3
"""Apply hash-bound, visually reviewed note ownership decisions to working candidates."""
import copy,difflib,hashlib,json,re
from pathlib import Path

def sha(blob):return hashlib.sha256(blob).hexdigest()
def once(text,old,new):
    if text.count(old)!=1:raise ValueError(repr(old))
    return text.replace(old,new,1)
def resolve(root=Path('temporario/coletas-quatro/mozokhin')):
    recipe=json.loads(Path(__file__).with_name('notes-round3-recipe.json').read_text())
    path=root/'units.json';units=json.loads(path.read_text());by={u['id']:u for u in units};decision=recipe['decision'];prefix='mozokhin-2013-v1-';uid=lambda n:prefix+f'{n:03d}'
    chosen={i:by[i] for i in recipe['expected']}
    if all(u.get('provenance',{}).get('review_decision')==decision for u in chosen.values()):
        for u in chosen.values():
            if sha((root/u['markdown']).read_bytes())!=u['markdown_sha256']:raise ValueError(u['id'])
        return {'already_applied':True}
    original={};after={}
    for i,u in chosen.items():
        blob=(root/u['markdown']).read_bytes()
        if sha(blob)!=recipe['expected'][i] or sha((root/u['raw']).read_bytes())!=recipe['pdf_sha256']:raise ValueError(i)
        original[i]=blob.decode();after[i]=blob.decode()
    for group in recipe['groups']:
        for note in group['notes']:
            carrier=uid(note['carrier']);owner=uid(note['owner']);label=note['label']
            after[carrier]=once(after[carrier],label+' '+note['definition'],'')
            after[owner]=once(after[owner],note['call'],note['call'].replace(label,'[^'+label+']'))
            after[owner]=after[owner].rstrip()+'\n\n[^'+label+']: '+note['definition']+'\n'
        # Remove only the printed folio belonging to the visually reviewed page.
        folio=str(group['page']-1)
        for n in group['numbers']:
            i=uid(n);after[i]=re.sub(r'(?m)^'+folio+r'\n','',after[i])
    review=root/'reviewed'/decision;review.mkdir(parents=True,exist_ok=True)
    if not (review/'units-before.json').exists():(review/'units-before.json').write_bytes(path.read_bytes())
    report={'decision':decision,'catalog_changed':False,'basis':'Visual comparison of PDF pages 53,81,93,120,181 (printed 52,80,92,119,180). Original OCR spelling retained; only note ownership, Markdown syntax and five page folios changed.','recipe':recipe,'images':[], 'units':[]}
    for group in recipe['groups']:
        image=root/'facsimile-checks'/'round3'/f"v1-{group['page']}.png"
        report['images'].append({'path':str(image.relative_to(root)),'sha256':sha(image.read_bytes())})
    for i,u in chosen.items():
        text=after[i].rstrip()+'\n';digest=sha(text.encode());dest=review/(i+'.'+digest+'.ru.md');dest.write_text(text)
        (review/(i+'.diff')).write_text(''.join(difflib.unified_diff(original[i].splitlines(True),text.splitlines(True),fromfile=u['markdown'],tofile=str(dest.relative_to(root)))))
        before=copy.deepcopy(u);remaining=recipe['still_blocked'].get(i)
        u.update(markdown=str(dest.relative_to(root)),markdown_sha256=digest,ready_for_import=not bool(remaining))
        u['issues']=(['Pendente: '+remaining] if remaining else [])+['OCR original preservado; revisão estrutural não equivale a revisão histórica integral.']
        u['provenance'].update(review_decision=decision,previous_markdown=before['markdown'],previous_markdown_sha256=before['markdown_sha256'],review_record=str((review/'decision.json').relative_to(root)),footer_note_review_required=bool(remaining),editorial_review='note_ownership_partially_checked' if remaining else 'note_ownership_checked_against_facsimile',reviewed_pdf_pages=[g['page'] for g in recipe['groups'] if int(i[-3:]) in g['numbers']])
        report['units'].append({'id':i,'before':before,'after_markdown':u['markdown'],'after_sha256':digest,'ready_for_import':u['ready_for_import'],'remaining':remaining})
    (review/'decision.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(units,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
    return {'resolved':[i for i,u in chosen.items() if u['ready_for_import']], 'partially_resolved':[i for i,u in chosen.items() if not u['ready_for_import']]}
if __name__=='__main__':print(json.dumps(resolve(),ensure_ascii=False))
