"""Build a noncanonical, coordinate-based transcription aid; never marks ready."""
import csv,json,re,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
BASE=Path('temporario/coletas-quatro/mozokhin/lista100')
NS={'x':'http://www.w3.org/1999/xhtml'}
rows=[]; rejected=[]
for page_no,page in enumerate(ET.parse(BASE/'pages174-180.bbox.html').findall('.//x:page',NS),174):
    lo,hi=(411,772) if page_no==174 else (58,141) if page_no==180 else (55,777)
    for column in ('left','right'):
        words=[]
        for w in page.findall('.//x:word',NS):
            x,y=float(w.get('xMin')),float(w.get('yMin'))
            if lo<=y<=hi and ((x<280)==(column=='left')):
                words.append((y,x,w.text or '',float(w.get('xMax')),float(w.get('yMax'))))
        # Number anchors avoid confusing detached year baselines with new rows.
        anchor_x=(48 if page_no%2==0 else 76)+(241 if column=='right' else 0)
        anchors=[w for w in words if abs(w[1]-anchor_x)<3 and re.match(r'^\d+(?:\.|$)',w[2])]
        lines=[[] for _ in anchors]
        for w in words:
            if not anchors: continue
            idx=min(range(len(anchors)),key=lambda i:abs(anchors[i][0]-w[0]))
            if abs(anchors[idx][0]-w[0])<=4:lines[idx].append(w)
            else:rejected.append({'pdf_page':page_no,'column':column,'y':w[0],'text':w[2]})
        for line in lines:
            line.sort(key=lambda w:w[1]);text=' '.join(w[2] for w in line)
            m=re.match(r'^(\d+)(?:\.)?(.*)',text)
            if not m: rejected.append({'pdf_page':page_no,'column':column,'y':line[0][0],'text':text});continue
            number=m.group(1); note=''
            if number in ('19838','78039'):number,note=number[:-2],number[-2:]
            tail=m.group(2).lstrip('. ').strip()
            # Year fields occupy a distinct physical column; do not infer missing years.
            year_x=(176 if page_no%2==0 else 204)+(241 if column=='right' else 0)
            names=[w[2] for w in line if w[1]<year_x]
            years=[w[2] for w in line if w[1]>=year_x]
            name=re.sub(r'^\d+\.?\s*','',' '.join(names)).strip()
            if note:name=''
            year=' '.join(years)
            flags=[]
            if note: flags.append('linha_retocada_nota_'+note)
            if not year:flags.append('ano_vazio_na_camada_textual')
            elif not re.fullmatch(r'\d{4}(?:\s*г\.)?',year): flags.append('ano_ou_segmentacao_a_conferir')
            rows.append({'pdf_page':page_no,'column':column,'line_in_column':sum(r['pdf_page']==page_no and r['column']==column for r in rows)+1,'label_literal':number,'name_text_layer':name,'year_text_layer':year,'note':note,'bbox':[min(w[1] for w in line),min(w[0] for w in line),max(w[3] for w in line),max(w[4] for w in line)],'raw_text':text,'flags':flags})
for i,r in enumerate(rows):
    if i and int(r['label_literal'])!=int(rows[i-1]['label_literal'])+1:
        r['flags'].append('sequencia_literal_diverge_apos_'+rows[i-1]['label_literal'])
    r['reading_order_position']=i+1
(BASE/'rows.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
fields=['reading_order_position','pdf_page','column','line_in_column','label_literal','name_text_layer','year_text_layer','note','bbox','raw_text','flags']
with (BASE/'rows.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
md=['# Lista nominal — derivado de trabalho por coordenadas','', '> Não canônico. Camada textual do PDF, sem normalização de nomes ou números. Anos vazios permanecem vazios. Conferência lexical integral pendente.','']
for p in range(174,181):
    md+=['## Página PDF '+str(p),'','| Rótulo literal | Nome na camada textual | Ano | Coluna / linha | Pendência |','| --- | --- | --- | --- | --- |']
    for r in rows:
        if r['pdf_page']==p:
            name=r['name_text_layer']+(('[^'+r['note']+']') if r['note'] else '')
            md.append('| '+ ' | '.join([r['label_literal'],name,r['year_text_layer'],r['column']+' / '+str(r['line_in_column']),'; '.join(r['flags'])])+' |')
    md+=['']
md+=['[^38]: Строка заретуширована','', '[^39]: Строка заретуширована','']
(BASE/'lista-por-coordenadas.ru.md').write_text('\n'.join(md))
summary={'status':'retained','row_count':len(rows),'source_pdf_sha256':hashlib.sha256(Path('temporario/coletas-quatro/mozokhin/raw/e126b2104b4c2d0b508811388544d0556ecd727d62abe0daa7eafee7fbf0302d.pdf').read_bytes()).hexdigest(),'per_page':{p:{'left':sum(r['pdf_page']==p and r['column']=='left' for r in rows),'right':sum(r['pdf_page']==p and r['column']=='right' for r in rows)} for p in range(174,181)},'nonrow_fragments':rejected,'flagged_rows':[r for r in rows if r['flags']]}
(BASE/'diagnostic.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'rows':len(rows),'per_page':summary['per_page'],'nonrows':len(rejected),'flagged':len(summary['flagged_rows'])},ensure_ascii=False))
