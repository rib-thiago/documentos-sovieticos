"""Individualização conservadora dos11apêndices com marcadores HTML explícitos."""
import hashlib
import re
from extraction import choose_article, clean_article, soup_from


def split_appendices(raw, url):
    body=choose_article(soup_from(raw))
    children=[node for node in body.children if getattr(node,'name',None)]
    markers=[]
    for pos,node in enumerate(children):
        label=node.get_text(' ',strip=True)
        if node.name=='p' and re.fullmatch(r'\d+',label):
            markers.append((int(label),pos))
    if [n for n,_ in markers] != list(range(1,12)):
        raise ValueError('Fronteiras não correspondem à sequência explícita1–11; não individualizar.')
    footer=[]
    for n,(number,start) in enumerate(markers):
        end=markers[n+1][1] if n+1<len(markers) else len(children)
        group=children[start:end]
        if number==11:
            for k,node in enumerate(group):
                if node.get_text(' ',strip=True).startswith('От авторов сайта спасибо'):
                    footer=[str(x) for x in group[k:]]
                    group=group[:k]
                    break
        # Last-page Joomla controls are not part of the historical document.
        group=[node for node in group if not node.select('a[href*="start="]')]
        title=group[1].get_text(' ',strip=True)
        if number==1:
            title += ' ' + group[2].get_text(' ',strip=True)
        html='<article>'+''.join(str(x) for x in group)+'</article>'
        markdown=clean_article(soup_from(html.encode()),url)
        date_literal=None
        for node in group[2:5]:
            candidate=node.get_text(' ',strip=True)
            if re.fullmatch(r'\d{1,2}\s+[А-Яа-яёЁ]+\s+19\d\d\s*г\.?',candidate):
                date_literal=candidate
                break
        yield {'number':number,'title_literal':title,'date_literal':date_literal,
               'markdown_text':markdown,'segment':{'kind':'numbered_appendix','number':number,
               'start_direct_child':start,'end_direct_child_exclusive':end,
               'boundary_method':'HTML paragraph containing only appendix number; exact1–11sequence verified'},
               'excluded_source_footer_html':''.join(footer) if number==11 else None}
