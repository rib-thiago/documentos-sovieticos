"""Derivados públicos isolados: somente páginas selecionadas e imagens aprovadas."""
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
from pypdf import PdfReader,PdfWriter


def run(root,release):
    if not re.fullmatch(r'release-[a-f0-9]{32}',release):raise SystemExit(2)
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));resource.setrlimit(resource.RLIMIT_CPU,(300,300));resource.setrlimit(resource.RLIMIT_FSIZE,(80*1024**2,80*1024**2))
    base=Path(root)/'.local/research';directory=base/'publications/releases'/release
    recipe=json.loads((directory/'recipe.json').read_text());blobs=base/'publications/blobs';blobs.mkdir(exist_ok=True)
    def blob(path,extension):
        with path.open('rb') as handle:hashed=hashlib.file_digest(handle,'sha256').hexdigest()
        target=blobs/(hashed+extension)
        if not target.exists():shutil.copyfile(path,target)
        return 'assets/facsimiles/'+hashed+extension
    for index,item in enumerate(recipe['items']):
        path=base/'sources'/(item['source_id']+'.pdf')
        with path.open('rb') as handle:
            if hashlib.file_digest(handle,'sha256').hexdigest()!=item['source_sha256']:raise ValueError('Fonte PDF alterada')
        reader=PdfReader(path);writer=PdfWriter()
        writer.append(reader,pages=[n-1 for n in item['pages']],import_outline=False,excluded_fields=['/Annots','/B'])
        writer.add_metadata({'/Title':item['source_title'],'/Producer':'Documentos Sovieticos; selecao editorial de paginas'})
        target=directory/(str(index)+'.pdf')
        with target.open('wb') as handle:writer.write(handle)
        writer.close();item['pdf_url']=blob(target,'.pdf');target.unlink()
        item['published_page_map']={str(number):i+1 for i,number in enumerate(item['pages'])}
        item['image_urls']={}
        image_pages={a['page_number'] for a in item['anchors'] if a.get('unit_boxes')}
        for page in item['page_snapshots']:
            if any(u.get('boxes') for u in page.get('review',{}).get('units',[])):image_pages.add(page['page_number'])
        for number in sorted(image_pages):
            subprocess.run([sys.executable,'-m','backend.pdf_image_worker',str(root),item['source_id'],str(number)],check=True,timeout=80,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            image=base/'page-images'/(item['source_sha256']+'-'+str(number)+'.png');item['image_urls'][str(number)]=blob(image,'.png')
    temporary=directory/'output.partial';temporary.write_text(json.dumps(recipe['items'],ensure_ascii=False));os.replace(temporary,directory/'output.json')

if __name__=='__main__':run(*sys.argv[1:])
