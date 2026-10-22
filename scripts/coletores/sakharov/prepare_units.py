#!/usr/bin/env python3
"""Prepara unidades da obra sem alterar o catálogo público ou alinhar idiomas."""
from __future__ import annotations
import argparse
import csv
from collections import Counter, defaultdict
import hashlib
import json
import re
from pathlib import Path
from collect import atomic_json
from appendices import split_appendices
from extraction import choose_article, clean_article, soup_from, ENGLISH_INDEX


def sha(value):
    return hashlib.sha256(value).hexdigest()


def definitions(text):
    # Blogspot occasionally joins the end of one note to the next label.
    # Within the explicit notes section those inline labels remain definitions.
    notes=re.search(r'(?im)^\s*(?:\*\*)?(?:Notes|Примечания):?(?:\*\*)?\s*$',text)
    if notes:
        return set(re.findall(r'\[(\d+)\]',text[notes.end():]))
    return set(re.findall(r'^\s*\[(\d+)\]', text, re.M))


def build(root):
    inventory = json.loads((root / 'inventory.json').read_text())
    units, texts, defs_by_lang = [], {}, defaultdict(lambda: defaultdict(list))
    for item in inventory['items'].values():
        if not item.get('candidate'):
            continue
        raw = (root / item['raw']).read_bytes()
        text = (root / item['candidate']).read_text()
        soup = soup_from(raw)
        article = choose_article(soup)
        headings = [h.get_text(' ', strip=True) for h in article.select('h1,h2,h3,h4,h5,h6')]
        lang = item['language']
        n = item.get('navigation_index')
        ident = f'sakharov-2003-{lang}-nav-{n:02}'
        title = headings[0] if lang == 'ru' and headings and n != 0 else item['title']
        post_heading=soup.select_one('.post-title,.entry-title') if lang=='en' else None
        if post_heading and post_heading.get_text(' ',strip=True):
            title=post_heading.get_text(' ',strip=True)
        if n == 0 and lang == 'ru':
            title = next((h for h in headings if 'Политическое завещание' in h), headings[0] if headings else item['title'])
        unit = dict(id=ident, source_url=item['source_url'], language=lang,
                    title_literal=title, title_navigation_literal=item['title'],
                    raw=item['raw'], markdown=item['candidate'],
                    hashes={'raw_sha256':sha(raw), 'markdown_sha256':sha(text.encode())},
                    source_kind='later_historiography',
                    segment={'kind':'whole_html_article_body','navigation_index_zero_based':n,
                             'not_printed_page':True,'headings_literal':headings},
                    provenance={'author':'Валентин Александрович Сахаров', 'work_year':2003,
                                'retrieved_at':item.get('retrieved_at'), 'final_url':item.get('final_url'),
                                'edition_scope':'russian_work_html' if lang == 'ru' else 'english_selected_extract',
                                'translation_credit':'See source body and selection index' if lang == 'en' else None},
                    ready_for_import=True, reason='Unidade de obra historiográfica; corpo integral da página e título de fonte preservados. Revisão editorial pendente.',
                    notes=[], diagnostics=item.get('diagnostics',{}), aligned_edition=None)
        if item.get('link_corrected_explicitly'):
            unit['provenance']['index_link_literal']=item.get('index_link_literal')
            unit['provenance']['link_resolution']='Índice contém href inválido; post canônico de mesmo título localizado no mesmo site e coletado.'
            unit['notes'].append('URL de coleta difere do href quebrado do índice; ambos preservados explicitamente.')
        non_heading = re.sub(r'(?m)^#{1,6}[^\n]*(?:\n|$)', '', text).strip()
        if not non_heading:
            unit['segment']['kind']='heading_only_boundary'
            unit.update(ready_for_import=False,reason='Página contém somente cabeçalho de parte/capítulo; preservada na compilação, não documento autônomo.')
        if lang == 'ru' and n == 59:
            unit['segment']['kind'] = 'appendix_compilation'
            unit.update(ready_for_import=False,reason='Compilação de apêndices preservada integralmente; individualização interna ainda não validada.')
        if lang == 'ru' and n == 0:
            unit['segment']['kind'] = 'composite_front_matter'
            unit['notes'].append('Folha, expediente, agradecimentos e prefácio mantidos como uma unidade de paratexto, não documento histórico individual.')
        texts[ident] = text
        for label in definitions(text):
            defs_by_lang[lang][label].append(ident)
        units.append(unit)

    # Numbered historical documents are distinct from the book's historiographical sections.
    appendix_source=next((i for i in inventory['items'].values() if i.get('language')=='ru' and i.get('navigation_index')==59),None)
    if appendix_source:
        raw=(root/appendix_source['raw']).read_bytes()
        for fragment in split_appendices(raw,appendix_source['source_url']):
            n=fragment['number'];text=fragment['markdown_text']
            ident=f'sakharov-2003-ru-appendix-{n:02}'
            relative=Path('candidates/ru/appendices')/(ident+'-'+sha(text.encode())+'.md')
            path=root/relative;path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():path.write_text(text)
            text=path.read_text()
            units.append(dict(id=ident,source_url=appendix_source['source_url'],language='ru',
                title_literal=fragment['title_literal'],date_literal=fragment['date_literal'],
                raw=appendix_source['raw'],markdown=str(relative),
                hashes={'raw_sha256':sha(raw),'markdown_sha256':sha(text.encode())},
                source_kind='historical_document_reproduced_in_later_work',segment=fragment['segment'],
                provenance={'containing_work_author':'Валентин Александрович Сахаров','work_year':2003,
                    'retrieved_at':appendix_source.get('retrieved_at'),'containing_unit':'sakharov-2003-ru-nav-59',
                    'publication_context':'Apêndice de obra historiográfica; autoria do livro não é autoria automática do documento.',
                    'archival_reference':'Preserved literally in document body; not normalized automatically'},
                ready_for_import=True,reason='Fronteiras numeradas1–11 conferidas no HTML; texto, referência e notas preservados.',
                notes=['Não confundir número de apêndice com número de arquivo ou paginação.'],diagnostics={},aligned_edition=None))
            texts[ident]=text
            for label in definitions(text):defs_by_lang['ru'][label].append(ident)
            if fragment['excluded_source_footer_html']:
                path=root/'source-apparatus'/'appendices-site-thanks.html';path.parent.mkdir(exist_ok=True)
                if not path.exists():path.write_text(fragment['excluded_source_footer_html'])

    # The English selection index also contains a genuine introduction after navigation.
    idx = inventory['items'].get(ENGLISH_INDEX)
    if idx:
        raw = (root / idx['raw']).read_bytes()
        all_md = clean_article(soup_from(raw), ENGLISH_INDEX)
        match = re.search(r'(?im)^\s*\*\*INTRODUCTION\*\*\s*$', all_md)
        if match:
            intro = all_md[match.start():].lstrip()
            relative = Path('candidates/en') / ('introduction-' + sha(intro.encode()) + '.md')
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text(intro)
            text = path.read_text()
            ident = 'sakharov-2003-en-introduction'
            units.append(dict(id=ident,source_url=ENGLISH_INDEX,language='en',title_literal='INTRODUCTION',
                raw=idx['raw'],markdown=str(relative),hashes={'raw_sha256':sha(raw),'markdown_sha256':sha(text.encode())},
                source_kind='later_historiography',segment={'kind':'introduction_embedded_in_index','start_heading_literal':'INTRODUCTION','navigation_excluded':True},
                provenance={'author':'Валентин Александрович Сахаров','work_year':2003,'retrieved_at':idx.get('retrieved_at'),
                    'edition_scope':'english_selected_extract','translation_credit':'Comrade Svitlana, Marxist Leninist Discussion Group, and unnamed paid translator; index states credits collectively, not paragraph-specific.'},
                ready_for_import=True,reason='Introdução delimitada pelo cabeçalho literal após o índice, sem associar automaticamente à versão russa.',
                notes=['O índice avisa que artigos e livro final podem ter pequenas diferenças.'],diagnostics={},aligned_edition=None))
            texts[ident]=text
            for label in definitions(text):
                defs_by_lang['en'][label].append(ident)

    hashes = Counter(u['hashes']['markdown_sha256'] for u in units)
    for unit in units:
        text = texts[unit['id']]
        refs = set(re.findall(r'\[(\d+)\]',text))
        own = definitions(text)
        candidates = refs-own
        # Bracketed partial years ([19]22) are editorial reconstruction, not notes.
        year_reconstructions = set(re.findall(r'\[(\d+)\]\d{2}',text))
        candidates -= year_reconstructions
        explicit_non_notes = {'1922'} if unit['id']=='sakharov-2003-en-nav-06' else set()
        candidates -= explicit_non_notes
        if explicit_non_notes:
            unit['notes'].append('[1922] depois de May25 é esclarecimento do ano, não chamada de nota; texto preservado.')
        unresolved=[]
        outside=[]
        for label in sorted(candidates,key=int):
            other=defs_by_lang[unit['language']].get(label,[])
            if other:
                outside.append({'label':label,'definition_in':other})
            else:
                unresolved.append(label)
        unit['diagnostics'].update({'note_definitions':sorted(own,key=int),
            'note_labels_without_definition_in_acquired_language':unresolved,
            'note_definitions_elsewhere_in_work':outside,
            'bracketed_year_reconstructions':sorted(year_reconstructions,key=int)})
        if unresolved:
            unit['ready_for_import']=False
            unit['reason']='Referências numéricas sem definição localizada no acervo adquirido: '+', '.join(unresolved)+'. Conferir fonte sem completar silenciosamente.'
        if hashes[unit['hashes']['markdown_sha256']]>1:
            unit['ready_for_import']=False
            unit['reason']='Corpo idêntico a outra unidade; conferir paginação/duplicata antes da incorporação.'
        if sha((root/unit['markdown']).read_bytes()) != unit['hashes']['markdown_sha256']:
            unit['ready_for_import']=False
            unit['reason']='Hash do arquivo divergente; revisão necessária.'

    for unit in units:
        unit['markdown_sha256']=unit['hashes']['markdown_sha256']
        unit['raw_sha256']=unit['hashes']['raw_sha256']
        unit['kind']='document' if unit['segment']['kind']=='numbered_appendix' else 'article'
        unit['document_type']=('letter' if 'ПИСЬМО' in unit['title_literal'] else 'document') if unit['kind']=='document' else 'article'
        unit['original_language']='ru'
        unit['order']=(unit['segment'].get('navigation_index_zero_based',-1)+1)*100
        if unit['segment']['kind']=='numbered_appendix':unit['order']=6000+unit['segment']['number']
        if unit['segment']['kind']=='appendix_compilation':
            unit['reason']='Compilação preservada como registro estrutural; os 11 apêndices foram individualizados por fronteiras HTML explícitas. Não importar novamente para evitar duplicação.'
        unit['issues']=([{'priority':'info' if unit['segment']['kind'] in {'heading_only_boundary','appendix_compilation'} else 'high','reason':unit['reason']}] if not unit['ready_for_import'] else [])
        n=unit['segment'].get('navigation_index_zero_based',-1)
        unit['subcollection']=('apendices' if unit['segment']['kind']=='numbered_appendix' else 'selecao-inglesa' if unit['language']=='en' else
            'preliminares' if n<4 else 'parte-1-nep' if n<20 else
            'parte-2-testamento-fontes' if n<41 else 'parte-3-luta-politica' if n<58 else
            'conclusao' if n==58 else 'apendices')
    units.sort(key=lambda u:(u['language'],u['segment'].get('navigation_index_zero_based',-1)))
    prepared={'schema':1,'path_base':str(root), 'not_public_catalog':True,
        'alignment':'none; no automatic cross-language pairing',
        'units':units,'summary':{'total':len(units),'ready_for_import':sum(u['ready_for_import'] for u in units),
        'by_language':dict(Counter(u['language'] for u in units)),
        'unresolved_units':[u['id'] for u in units if not u['ready_for_import']]}}
    # Whole-work reading derivatives retain every page body, with explicit source boundaries.
    compilations=[]
    for lang in ('ru','en'):
        selected = [u for u in units if u['language']==lang and u['segment']['kind']!='numbered_appendix']
        selected.sort(key=lambda u:u['segment'].get('navigation_index_zero_based',-1))
        compilation = '\n\n'.join(f"<!-- SOURCE {u['source_url']} | UNIT {u['id']} -->\n\n"+texts[u['id']] for u in selected)
        folder=root/'compilations';folder.mkdir(exist_ok=True)
        path=folder/f'sakharov-2003-{lang}-{sha(compilation.encode())}.md'
        if not path.exists():path.write_text(compilation)
        compilations.append({'language':lang,'markdown':str(path.relative_to(root)),'markdown_sha256':sha(path.read_bytes()),'page_units':len(selected)})
    prepared['compilations']=compilations
    atomic_json(root/'units.json',prepared)
    with (root/'unit-plan.csv').open('w',encoding='utf-8',newline='') as fh:
        fields=['id','language','title_literal','subcollection','kind','ready_for_import','reason','markdown','source_url']
        writer=csv.DictWriter(fh,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(units)
    lines=['# Sakharov — inventário de unidades candidatas','','Não é catálogo público; ready_for_import indica preparo técnico, não revisão historiográfica ou publicação.','']
    for unit in sorted(units,key=lambda u:(u['language'],u['order'])):
        state='preparável' if unit['ready_for_import'] else 'retida'
        lines.append(f"- {unit['language']} · {unit['id']} · **{state}** — [{unit['title_literal']}]({unit['markdown']}) — [fonte]({unit['source_url']})")
    (root/'UNIDADES.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(json.loads((root/'units.json').read_text())['summary'],ensure_ascii=False,indent=2))
    return units


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=Path('temporario/coletas-quatro/sakharov'))
    build(ap.parse_args().output)
