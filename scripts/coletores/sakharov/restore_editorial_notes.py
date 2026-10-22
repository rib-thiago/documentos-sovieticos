#!/usr/bin/env python3
"""Append explicitly editorial translations of located Russian notes, never changing originals."""
import copy, difflib, hashlib, json
from pathlib import Path

def sha(b): return hashlib.sha256(b).hexdigest()
def refresh_issues(u):
    # Original blockers remain in the immutable before snapshot; do not retain a false missing-note warning.
    items=[i for i in u.get('issues',[]) if not (isinstance(i,dict) and (i.get('reason','').startswith('Referências numéricas sem definição localizada') or i.get('reason','').startswith('Suplemento editorial:')))]
    items.append({'priority':'medium','reason':'Suplemento editorial: conferir tradução das notas do aparato russo; fonte inglesa adquirida permanece inalterada e a suplementação está identificada.'})
    u['issues']=items
TRANSLATIONS = {
'692':'Izvestiya TsK KPSS. 1989. No. 12. p. 195.',
'693':'Ibid., p. 189. [Editorial expansion of the antecedent: Izvestiya TsK KPSS. 1989. No. 12.]',
'694':'Ibid., p. 191. [Editorial expansion of the antecedent: Izvestiya TsK KPSS. 1989. No. 12.]',
'696':'Ibid., p. 198. [Editorial expansion of the antecedent: Izvestiya TsK KPSS. 1989. No. 12; the preceding Russian note 695 cites the same issue, p. 195.]',
'697':'RGASPI. Fond 5. Inventory 2. File 27. Folio 88; Fond 17. Inventory 2. File 86. Folios 5, 5а–5г. [Cyrillic folio suffixes preserved.]',
'698':'Lenin, V. I. Complete Works. Vol. 54. pp. 327–328.',
'699':'Izvestiya TsK KPSS. 1989. No. 12. p. 191.',
'700':'Lenin, V. I. Complete Works. Vol. 54. pp. 327–328.',
'701':'Trotsky, L. Portraits of Revolutionaries. p. 279.',
'702':'Izvestiya TsK KPSS. 1989. No. 12. p. 191.',
'703':'RGASPI. Fond 558. Inventory 2. File 17. Folio 1. The publication (Izvestiya TsK KPSS. 1989. No. 12. p. 191) contains an inaccuracy: after the words “into factions” a comma was placed instead of a full stop.',
'705':'Ibid., pp. 25, 34. [Editorial expansion of the antecedent from Russian note 704: The Formation of the USSR. Collection of Documents. 1917–1924. Moscow; Leningrad, 1949.]',
'784':'RGASPI. Fond 5. Inventory 2. File 32. Folios 43–43 verso.',
'1066':'Ibid., p. 158. [Editorial expansion across the Russian page boundary: Izvestiya TsK KPSS. 1990. No. 9; notes 1064–1065 appear on Russian navigation page 29, while note 1066 appears on page 30.]',
}

def restore(root, located):
    path=root/'units.json'; model=json.loads(path.read_text()); units={u['id']:u for u in model['units']}
    records=json.loads(located.read_text()); decision='sakharov-editorial-notes-20261021'
    review=root/'reviewed'/decision; review.mkdir(parents=True,exist_ok=True)
    if not (review/'units-before.json').exists(): (review/'units-before.json').write_bytes(path.read_bytes())
    report={'decision':decision,'catalog_changed':False,'translation_credit':'English supplements translated editorially by the project from the Russian apparatus; not attributed to the translator of the English source.','units':[]}
    for uid in sorted({r['english_unit'] for r in records}):
        u=units[uid]
        if u.get('provenance',{}).get('review_decision')==decision:
            blob=(root/u['markdown']).read_bytes()
            if sha(blob)!=u['hashes']['markdown_sha256']:raise ValueError(uid)
            u['markdown_sha256']=sha(blob)
            refresh_issues(u)
            if 'markdown_bytes' in u: u['markdown_bytes']=len(blob)
            continue
        original=(root/u['markdown']).read_bytes()
        if sha(original)!=u['hashes']['markdown_sha256']:raise ValueError(uid)
        selected=[r for r in records if r['english_unit']==uid]; lines=[]
        for r in selected:
            match,=r['matches_in_russian_work']; ru=units[match['unit']]; blob=(root/ru['markdown']).read_bytes()
            if sha(blob)!=match['markdown_sha256'] or match['definition_ru'] not in blob.decode():raise ValueError(r)
            lines.append(f"[{r['note']}] {TRANSLATIONS[r['note']]}\n\nRussian apparatus, verbatim: {match['definition_ru']}\n\nSource: [{match['unit']}]({match['url']}).")
        if any(r['note']=='1066' for r in selected):
            context=units['sakharov-2003-ru-nav-29']; blob=(root/context['markdown']).read_bytes()
            if sha(blob)!=context['hashes']['markdown_sha256'] or '[1064] Известия ЦК КПСС. 1990. № 9. С. 157.' not in blob.decode() or '[1065] Там же. С. 151–152.' not in blob.decode(): raise ValueError('1066 antecedent')
        after=original.decode().rstrip()+'\n\n---\n\n## Editorial supplement: notes absent from the English web extract\n\nThe English source above is preserved verbatim. The numbered entries below were located in the Russian edition and translated into English by the project. They are an editorial supplement, not part of the acquired English translation. Russian wording is included for verification. Bibliographic titles are translated descriptively; this does not assert an English edition. Bracketed expansions resolve “Ibid.” editorially. No cross-language paragraph alignment is asserted.\n\n'+'\n\n'.join(lines)+'\n'
        digest=sha(after.encode()); dest=review/(uid+'.'+digest+'.en.md');dest.write_text(after)
        (review/(uid+'.diff')).write_text(''.join(difflib.unified_diff(original.decode().splitlines(True),after.splitlines(True),fromfile=u['markdown'],tofile=str(dest.relative_to(root)))))
        report['units'].append({'id':uid,'before':copy.deepcopy(u),'notes':[r['note'] for r in selected],'after_markdown':str(dest.relative_to(root)),'after_sha256':digest,'russian_sources':[r['matches_in_russian_work'][0] for r in selected]})
        u['provenance'].update(review_decision=decision,previous_markdown=u['markdown'],previous_markdown_sha256=u['hashes']['markdown_sha256'],editorial_supplement=True,editorial_supplement_language='en',editorial_supplement_translation_credit=report['translation_credit'],review_record=str((review/'decision.json').relative_to(root)))
        u['markdown']=str(dest.relative_to(root));u['hashes']['markdown_sha256']=digest;u['markdown_sha256']=digest;u['ready_for_import']=True
        if 'markdown_bytes' in u: u['markdown_bytes']=len(after.encode())
        u['reason']='Notas ausentes da fonte inglesa supridas em suplemento editorial identificado, com russo literal, proveniência e contexto bibliográfico; fonte inglesa inalterada.'
        u['notes'].append('Suplemento editorial traduzido do aparato russo; numeração e corpo da fonte inglesa preservados.')
        u['diagnostics']['editorially_supplemented_note_labels']=[r['note'] for r in selected]
        u['diagnostics']['note_labels_without_definition_in_acquired_language_original']=u['diagnostics']['note_labels_without_definition_in_acquired_language']
        u['diagnostics']['note_labels_without_definition_in_acquired_language']=[]
        refresh_issues(u)
    if report['units']:(review/'decision.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    tmp=path.with_suffix('.json.tmp');tmp.write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
    return report
if __name__=='__main__':
    r=restore(Path('temporario/coletas-quatro/sakharov'),Path('docs/pesquisa/quatro-coletores/sakharov-notas-localizadas.json'))
    print(json.dumps({'decision':r['decision'],'prepared':[u['id'] for u in r['units']]},ensure_ascii=False))
