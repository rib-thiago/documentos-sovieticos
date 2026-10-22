#!/usr/bin/env python3
"""Individualização conferida das seis capturas Iskra; somente candidatos locais."""
import argparse
from collections import Counter
import copy
import json
from pathlib import Path
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup,Tag,Comment
from markdownify import markdownify
from coletar import DEFAULT_OUTPUT,atomic_json,immutable,sha

HASHES={
'iskra-primeira-sessao':'b55e7b1ac4cdef1948ce498e9777a30df0ce9c7584a9ad2b551f636f2c9e93cf',
'iskra-27-dez':'61156b9aad6ffb236c36c21842950bbac2809ca65cd659e1d36586f255a64b5c',
'iskra-jan-11':'5f294e31cf212afd9a704546052cb578f3a4b49e88cc44779045f05ca0ebf415',
'iskra-fase-2':'3f7f3c5007df34af3951a2f4e7cb83eaa3a1a5105d2349890dd33b271d5990e9',
'iskra-jan-31':'cf056b860fffa80e89f56f06a12784ce0ecd85f8f0c5feb441c8f9782d89173b',
'iskra-mar-1':'4748c9c74ad4d73d2dd67bb24f1f1215a8c966009715163a8677379dc1a34691'}
# Sufixo, título editorial PT, tipo, data literal. Não alinhar automaticamente idiomas.
PARTS={
'iskra-primeira-sessao': [('', 'Sessão plenária de 22/9 de dezembro de 1917','session_transcript','22/9 декабря 1917 года')],
'iskra-27-dez':[('', 'Comissão Política — sessão de 27/14 de dezembro de 1917','session_transcript','27/14 декабря 1917 года')],
'iskra-jan-11':[('manha','Comissão Política — sessão da manhã de 11 de janeiro de 1918','session_transcript','11 января 1918 г. (29 декабря 1917 г.)'),('tarde','Comissão Política — sessão da tarde de 11 de janeiro de 1918','session_transcript','11 января 1918 г. (29 декабря 1917 г.)')],
'iskra-fase-2':[('apresentacao','Segundo período das negociações — apresentação editorial da fonte','article',None),('ioffe','Segundo período das negociações — nota de A. Ioffe, abril de 1919','article','Апрель 1919 г.'),('delegacoes','Segundo período das negociações — composição das delegações','list',None)],
'iskra-jan-31':[('', 'Comissão Política — sessão de 31 de janeiro de 1918','session_transcript','31 января 1918 г. (18 января 1918 г.)')],
'iskra-mar-1':[('manha','Sessão plenária da manhã de 1º de março de 1918','session_transcript','1 марта (16 февраля) 1918 года'),('tarde','Sessão plenária da tarde de 1º de março de 1918','session_transcript','1 марта (16 февраля) 1918 года'),('presidentes','Reunião dos presidentes das delegações de 1º de março de 1918','session_transcript','1 марта (16 февраля) 1918 года')]
}


def children_at(main,predicate):
    return [i for i,child in enumerate(main.contents) if isinstance(child,Tag) and predicate(child)]


def convert(fragment,base):
    root=BeautifulSoup(fragment,'html.parser');layout=0
    for sup in root.find_all('sup'):
        # Conservar o número misto 5½: não unir o inteiro ao numerador (51/2).
        if str(sup.next_sibling).strip()=='⁄' and getattr(sup.next_sibling.next_sibling,'name',None)=='sub':
            sup.insert_before(' ')
    for table in list(root.find_all('table')):
        # Tabelas de uma linha contendo retrato e texto são diagramação explícita.
        if len(table.find_all('tr'))==1 and table.find('img') and not table.find('th'):
            for cell in list(table.find_all(['td','th'])):cell.unwrap()
            for row in list(table.find_all('tr')):row.unwrap()
            table.unwrap();layout+=1
    retained_tables=len(root.find_all('table'))
    for item in root.find_all(['p']):
        classes=set(item.get('class',[]))
        if classes&{'title','subtitle'} and item.get_text(strip=True):item.name='h2' if 'title'in classes else 'h3'
        elif 'date' in classes:item.name='h4'
        elif 'footnote' in classes:item.name='blockquote'
    for tag,attr in [('a','href'),('img','src')]:
        for item in root.find_all(tag):
            if item.get(attr):item[attr]=urljoin(base,item[attr])
    text=markdownify(str(root),heading_style='ATX',escape_underscores=False).strip()+'\n'
    return text,layout,retained_tables


def build(work):
    rows={r['id']:r for r in json.loads((work/'inventario.json').read_text())}
    path=work/'units.json';before=path.read_bytes();payload=json.loads(before)
    originals={u['id']:u for u in payload['units']};result=[];reports=[]
    for seed,expected in HASHES.items():
        row=rows[seed];raw=(work/row['raw_path']).read_bytes()
        if sha(raw)!=expected:raise ValueError('Captura diferente da conferida: '+seed)
        main=BeautifulSoup(raw,'html.parser').select_one('#mainContent')
        if main is None:raise ValueError('Corpo ausente')
        for comment in main.find_all(string=lambda value:isinstance(value,Comment)):comment.extract()
        cuts=[0]
        if seed=='iskra-jan-11':
            marks=children_at(main,lambda x:x.name=='p' and 'title'in x.get('class',[])and x.get_text(' ',strip=True)=='Заседание Политической комиссии.')
            if len(marks)!=2:raise ValueError('Duas sessões esperadas em 11 de janeiro')
            cuts.append(marks[1])
        elif seed=='iskra-fase-2':
            for text in ['Второй период мирных переговоров.','Состав Мирной Конференции.']:
                marks=children_at(main,lambda x:x.get_text(' ',strip=True)==text)
                if len(marks)!=1:raise ValueError('Fronteira editorial ambígua: '+text)
                cuts.append(marks[0])
        elif seed=='iskra-mar-1':
            marks=children_at(main,lambda x:x.name=='p' and x.get_text(' ',strip=True)in ['Пленарное заседание мирной конференции.','Совещание Председателей делегаций.'])
            if len(marks)!=3:raise ValueError('Três reuniões esperadas em 1º de março')
            cuts.extend(marks[1:])
        if cuts!=sorted(set(cuts)) or len(cuts)!=len(PARTS[seed]):raise ValueError('Partição ambígua')
        cuts.append(len(main.contents))
        for i,(suffix,title_pt,doctype,date)in enumerate(PARTS[seed]):
            fragment=''.join(str(n)for n in main.contents[cuts[i]:cuts[i+1]])
            soup=BeautifulSoup(fragment,'html.parser');source_text=soup.get_text(' ',strip=True)
            converted,layout,tables=convert(fragment,row['url'])
            missing=Counter(re.findall(r'\w+',source_text))-Counter(re.findall(r'\w+',converted))
            baseid='brest-'+seed;uid=baseid+('-'+suffix if suffix else '')
            title_tag=next((p for p in soup.find_all('p')if p.get_text(strip=True)and set(p.get('class',[]))&{'title','subtitle'}),None)
            title_literal=title_tag.get_text(' ',strip=True)if title_tag else row['titulo_extraido']
            digest=sha(converted.encode());target=Path('units')/uid/(digest+'.ru.md');immutable(work/target,converted.encode())
            base=copy.deepcopy(originals.get(baseid,{}))
            unit={**base,'id':uid,'source_url':row['url'],'language':'ru','original_language':'ru','title_literal':title_literal,'title_pt':title_pt,'kind':'article'if doctype=='article'else'document','document_type':doctype,'subcollection':row['grupo'],'subcollections':row.get('grupos',[row['grupo']]),'raw':row['raw_path'],'raw_sha256':expected,'markdown':str(target),'markdown_sha256':digest,'date_literal':date,'ready_for_import':not bool(missing),'issues':['Revisão editorial de OCR/transcrição e metadados permanece pendente; imagens externas não foram adquiridas.'],'provenance':{'seed_id':seed,'seed_title':row['titulo'],'acquisition':row,'wayback':row['wayback'],'segmentation':{'source_part':i+1,'source_parts':len(PARTS[seed]),'direct_child_range':[cuts[i],cuts[i+1]],'method':'explicit source headings; no inferred paragraph alignment'},'layout_tables_unwrapped':layout,'tables_retained':tables,'inline_source_notes_retained':len(soup.select('p.footnote')),'lexical_coverage_missing':dict(missing),'editorial_review':'source boundaries, opening/closing and note extent checked; not a philological review','dating_note':'Datas históricas literais, data da nota de Ioffe e data da captura são campos distintos. Na apresentação e na lista de delegações não foi inferida data de redação.'}}
            if missing:unit['issues'].append('Conferir palavras não preservadas na conversão: '+str(dict(missing)))
            result.append(unit);reports.append({'id':uid,'source':seed,'title_pt':title_pt,'ready':unit['ready_for_import'],'raw_sha256':expected,'markdown_sha256':digest,'layout_tables_unwrapped':layout,'tables_retained':tables,'source_notes':unit['provenance']['inline_source_notes_retained'],'missing_tokens':dict(missing)})
    replaced={'brest-'+seed for seed in HASHES}
    old_extra={u['id']for u in payload['units']if u.get('provenance',{}).get('segmentation',{}).get('method')=='explicit source headings; no inferred paragraph alignment'and u.get('provenance',{}).get('seed_id')in HASHES}
    payload['units']=[u for u in payload['units']if u['id']not in replaced|old_extra]+result
    immutable(work/'wayback/preparation-history'/(sha(before)+'.units.json'),before)
    atomic_json(work/'wayback/prepared.json',{'sources':6,'units':len(result),'ready':sum(u['ready_for_import']for u in result),'catalog_changed':False,'units_review':reports})
    atomic_json(path,payload)
    print(json.dumps({'sources':6,'new_units':len(result),'ready':sum(u['ready_for_import']for u in result),'brest_units':len(payload['units']),'brest_ready':sum(u['ready_for_import']for u in payload['units'])}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workdir',type=Path,default=DEFAULT_OUTPUT);build(parser.parse_args().workdir)
