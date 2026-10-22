#!/usr/bin/env python3
"""Coteja textos militares contra HTML local; só grava evidências de preparação."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from audit_military_tables import plain

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'temporario/revisao-onda1/militares-restantes'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    plan = json.loads((ROOT/'docs/revisao-markdown/diagnostico-geral/LOTES.json').read_text())
    for batch in plan['batches']:
        if batch['family'] != 'fontes_militares' or batch['id'].endswith('0001'):
            continue
        folder = OUT/batch['id']; folder.mkdir(parents=True,exist_ok=True)
        details=[]
        for doc in batch['documents']:
            edition=doc['editions'][0]; canonical=ROOT/edition['file']; text=canonical.read_text()
            assert sha(canonical)==edition['sha256'], 'Edição modificada desde planejamento'
            if 'trial-1937' in doc['id']:
                details.append(dict(document_id=doc['id'],canonical_file=edition['file'],before_sha256=sha(canonical),pdf_card=True));continue
            prefix='military-' if doc['id'].startswith('military-') else 'tukhachevsky-'
            work=ROOT/'.local/research'/('military-1934-1936' if prefix=='military-' else 'tukhachevsky-1937')
            key=doc['id'][len(prefix):]; metadata=json.loads((work/f'{key}.json').read_text())
            source=ROOT/metadata['file']; assert sha(source)==metadata['sha256']
            soup=BeautifulSoup(source.read_bytes(),'html.parser')
            body=soup.select_one('.field-name-body .field-item, .field-name-body')
            normalized=plain(text); notes=[]
            for definition in list(body.select('div[id]')):
                m=re.fullmatch(r'(ftn|edn)(\d+)',definition.get('id',''))
                if not m:continue
                family,num=m.groups(); label=num if family=='ftn' else 'end'+num
                calls=body.select(f'a[href="#_{family}{num}"]')
                if not calls or definition.select('table'):continue
                note_copy=BeautifulSoup(str(definition),'html.parser')
                for back in note_copy.select(f'a[href="#_{family}ref{num}"]'):back.decompose()
                note=note_copy.get_text('',strip=False)
                matches=re.findall(r'^\[\^'+re.escape(label)+r'\]:\s*(.*?)(?=\n\[\^|\Z)',text,re.M|re.S)
                notes.append(dict(label=label,source_text=note,definition_equal=bool(matches) and plain(note)==plain(matches[0]),source_calls=len(calls),markdown_calls=len(re.findall(r'\[\^'+re.escape(label)+r'\]',text))-len(re.findall(r'^\[\^'+re.escape(label)+r'\]:',text,re.M))))
                for call in calls:call.replace_with(body.new_string(f'[^{label}]') if hasattr(body,'new_string') and body.new_string else soup.new_string(f'[^{label}]'))
                definition.decompose()
            # Every leaf paragraph/block must occur in order, not merely match a count.
            passages=[];cursor=0
            blocks=body.find_all(['p','h1','h2','h3','h4','h5','h6','li'])
            for i,p in enumerate(blocks,1):
                if p.find_parent('table') or p.find(['p','li']):continue
                value=p.get_text('',strip=False); needle=plain(value)
                offset=normalized.find(needle,cursor)
                passages.append(dict(index=i,text=value,present=offset>=0,ordered_offset=offset))
                if offset>=0:cursor=offset+len(needle)
            links=[]
            for a in body.select('a[href]'):
                href=a['href'];target=(metadata['archive_url']+href if metadata.get('archive_url') and href.startswith('#') else urljoin(metadata.get('captured_original_url',metadata['original_url']),href))
                links.append(dict(label=a.get_text('',strip=False),source_href=href,expected_target=target,present=target in text))
            complete_body = plain(body.get_text('',strip=False))
            complete_body_present = complete_body in normalized
            details.append(dict(document_id=doc['id'],canonical_file=edition['file'],before_sha256=sha(canonical),source=str(source.relative_to(ROOT)),source_sha256=sha(source),source_url=metadata['original_url'],capture=metadata.get('capture_timestamp'),source_title=soup.select_one('h1').get_text(' ',strip=True),source_tables=len(body.select('table')),source_images=[i.get('src') for i in body.select('img')],passages=passages,missing=[p for p in passages if not p['present']],notes=notes,links=links,complete_body_present=complete_body_present))
        (folder/'cotejo.json').write_text(json.dumps(details,ensure_ascii=False,indent=2)+'\n')
        print(batch['id'],[(d['document_id'],len(d.get('missing',[])),sum(not n['definition_equal'] or n['source_calls']!=n['markdown_calls'] for n in d.get('notes',[])),sum(not l['present'] for l in d.get('links',[]))) for d in details])

if __name__=='__main__':main()
