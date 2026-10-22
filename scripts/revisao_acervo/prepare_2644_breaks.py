"""Follow-up on frozen2644 candidates: represent split first header with a space."""
from pathlib import Path
import hashlib,json,difflib
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'temporario/revisao-onda1/tabela2644-breaks';out.mkdir(exist_ok=True)
previous=json.loads((ROOT/'temporario/revisao-onda1/tabela2644/result.json').read_text())
result={'batch_id':'R1-tabelas_imagens-0024-formato','editions':[],'issues':[]}
sha=lambda b:hashlib.sha256(b).hexdigest()
for e in previous['editions']:
 before=(ROOT/e['candidate']).read_bytes();assert sha(before)==e['candidate_sha256'];text=before.decode();assert text.count('<br>')==1
 after=text.replace('<br>',' ');dest=out/Path(e['file']).name;dest.write_text(after)
 (out/(dest.name+'.diff')).write_text(''.join(difflib.unified_diff(text.splitlines(True),after.splitlines(True))))
 result['editions'].append({'document_id':e['document_id'],'language':e['language'],'file':e['file'],'before_sha256':sha(before),'candidate':str(dest.relative_to(ROOT)),'candidate_sha256':sha(after.encode()),'source_evidence':e['source_evidence']})
result['evidence']='One first-cell source paragraph break replaced by a space per language, preserving all words. html:false reader would display literal<br>; no new renderer behavior introduced.96cells24rows unchanged. Frozen first2644result preserved.'
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
