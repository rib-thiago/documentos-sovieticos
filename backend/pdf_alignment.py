"""Fronteiras e caixas manuais, com sucessão de unidades no histórico da página."""
import copy
import json
import math
import secrets
from .editorial import EditorialError
from .pdf_review import digest


class PDFAlignment:
    def __init__(self, sources):
        self.sources = sources

    def preview(self, payload):
        with self.sources.lock:
            source_id, number = self.sources.review.identity(payload)
            page = self.sources.review.page(source_id, number)
            if type(payload.get('revision')) is not int or payload['revision'] != page['revision']:
                raise EditorialError('A revisão da página mudou. Atualize antes de alinhar.', 409)
            before = page['review']; after = copy.deepcopy(before)
            units = after['units']; action = payload.get('action')
            indices = [i for i,u in enumerate(units) if u['id'] == payload.get('unit_id')]
            if not indices:
                raise EditorialError('Unidade não encontrada', 404)
            index = indices[0]; unit = units[index]; replaced = [unit['id']]
            def new_unit(start,end,parents):
                return {'id':'unit-'+secrets.token_hex(16),'start':start,'end':end,
                        'sha256':digest(after['text'][start:end]),'boundary':'manual', 'parents':parents,'boxes':[]}
            if action == 'split':
                offset = payload.get('offset')
                if type(offset) is not int or not 0 < offset < unit['end']-unit['start']:
                    raise EditorialError('Posicione o corte dentro da unidade (caracteres Unicode)')
                cut = unit['start']+offset
                left = after['text'][unit['start']:cut].rstrip();right = after['text'][cut:unit['end']].lstrip()
                if not left or not right:
                    raise EditorialError('A divisão deve gerar duas unidades com texto')
                new = [new_unit(unit['start'],unit['start']+len(left),replaced),new_unit(unit['end']-len(right),unit['end'],replaced)]
                units[index:index+1] = new
            elif action == 'merge':
                if index+1 == len(units):
                    raise EditorialError('Não existe unidade seguinte para unir')
                following = units[index+1];replaced.append(following['id'])
                new = [new_unit(unit['start'],following['end'],replaced)]
                units[index:index+2] = new
            elif action == 'boxes':
                boxes = payload.get('boxes')
                if not isinstance(boxes,list) or len(boxes)>16:
                    raise EditorialError('Use até 16 retângulos por unidade')
                for box in boxes:
                    if not isinstance(box,list) or len(box)!=4 or any(type(n) not in (int,float) or not math.isfinite(n) for n in box):
                        raise EditorialError('Retângulo inválido')
                    x,y,w,h = box
                    if min(x,y)<0 or min(w,h)<=0 or x+w>1.000001 or y+h>1.000001:
                        raise EditorialError('O retângulo deve estar dentro da página')
                unit.update(boxes=boxes,geometry_status='manual',geometry_space='normalized_display_page')
                new = [unit]
            else:
                raise EditorialError('Operação de alinhamento inválida')
            event = {'action':action,'before':replaced,'after':[u['id'] for u in new]}
            after['structure_events'] = before.get('structure_events',[])[-199:]+[event]
            plan={'source_id':source_id,'page_number':number,'revision':page['revision'],'before':before,'after':after,'raw_sha256':page['raw']['text_sha256']}
            return {'preview_id':self.sources.review.stash('review',plan),'before':before,'after':after,'diff':'Texto integral preservado. Operação: '+action,'structure':event}

    def geometry(self, source_id, number):
        page=self.sources.review.page(source_id,number)
        with self.sources.db() as db:
            row=db.execute('SELECT geometry FROM pdf_ocr_candidates WHERE id=? AND source_id=? AND page_number=?',(page['review']['basis'],source_id,number)).fetchone()
        # OCR words are suggestions only, never adopted as manual boxes implicitly.
        words=[]
        if row:
            import csv,io
            records=list(csv.DictReader(io.StringIO(row['geometry']),delimiter='\t'))
            size=next((r for r in records if r.get('level')=='1'),None)
            if size:
                width,height=float(size['width']),float(size['height'])
                if width>0 and height>0:
                    for r in records:
                        if r.get('level')=='5' and r.get('text','').strip():
                            words.append({'text':r['text'],'confidence':float(r['conf']),'box':[float(r[k])/total for k,total in [('left',width),('top',height),('width',width),('height',height)]]})
        return {'revision':page['revision'],'units':page['review']['units'],'text':page['review']['text'],'words':words[:20000]}
