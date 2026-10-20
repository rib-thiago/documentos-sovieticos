"""Renderização isolada de uma página para revisão geométrica."""
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import sqlite3
import subprocess
import sys
import tempfile


def run(root, source_id, number):
    if not re.fullmatch(r'pdf-[a-f0-9]{32}',source_id) or not number.isdecimal():
        raise SystemExit(2)
    resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3));resource.setrlimit(resource.RLIMIT_CPU,(60,60));resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024**2,32*1024**2))
    base=Path(root)/'.local/research';db=sqlite3.connect(base/'jobs.sqlite3')
    row=db.execute('SELECT sha256,page_count FROM pdf_sources WHERE id=?',(source_id,)).fetchone();db.close()
    if not row or not 1<=int(number)<=row[1]:raise SystemExit(2)
    source=base/'sources'/(source_id+'.pdf')
    with source.open('rb') as handle:
        if hashlib.file_digest(handle,'sha256').hexdigest()!=row[0]:raise SystemExit(3)
    directory=base/'page-images';directory.mkdir(exist_ok=True);target=directory/(row[0]+'-'+number+'.png')
    if target.exists():return
    with tempfile.TemporaryDirectory(dir=directory,prefix='render-') as temporary:
        prefix=str(Path(temporary)/'page')
        subprocess.run(['pdftoppm','-f',number,'-l',number,'-singlefile','-scale-to','2000','-png',str(source),prefix],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=65)
        os.replace(prefix+'.png',target)

if __name__=='__main__':run(*sys.argv[1:])
