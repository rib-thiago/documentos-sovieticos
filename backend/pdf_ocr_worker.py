"""Lote OCR isolado: um candidato imutável por página, retomável após interrupção."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import resource
import sqlite3
import subprocess
import sys
import tempfile
from .pdf_sources import now


def run(root, job_id):
    if not __import__('re').fullmatch(r'ocr-[a-f0-9]{32}', job_id):
        return
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (600, 600))
    resource.setrlimit(resource.RLIMIT_FSIZE, (128*1024**2, 128*1024**2))
    db = sqlite3.connect(Path(root)/'.local/research/jobs.sqlite3', timeout=20)
    db.row_factory = sqlite3.Row
    try:
        job = db.execute('SELECT * FROM pdf_ocr_jobs WHERE id=?', (job_id,)).fetchone()
        if not job or job['state'] != 'queued':
            return
        recipe = json.loads(job['recipe'])
        source = Path(root)/'.local/research/sources'/(job['source_id']+'.pdf')
        sha = hashlib.sha256()
        with source.open('rb') as handle:
            for chunk in iter(lambda: handle.read(1024*1024), b''):
                sha.update(chunk)
        if sha.hexdigest() != job['source_sha256']:
            raise ValueError('O PDF difere da fonte registrada; OCR cancelado.')
        db.execute("UPDATE pdf_ocr_jobs SET state='running',updated_at=? WHERE id=?", (now(), job_id)); db.commit()
        from pypdf import PdfReader
        reader = PdfReader(source)
        env = {**os.environ, 'OMP_THREAD_LIMIT': '1'}
        version = subprocess.run(['tesseract', '--version'], capture_output=True, text=True, timeout=10, env=env, check=True).stdout.splitlines()[0]
        renderer_version = subprocess.run(['pdftoppm', '-v'], capture_output=True, text=True, timeout=10, check=True).stderr.splitlines()[0]
        for number in recipe['pages']:
            if db.execute('SELECT 1 FROM pdf_ocr_candidates WHERE job_id=? AND page_number=?', (job_id, number)).fetchone():
                continue
            page = reader.pages[number-1]
            w, h = float(page.mediabox.width)*recipe['dpi']/72, float(page.mediabox.height)*recipe['dpi']/72
            if max(w, h) > 10000 or w*h > 40000000:
                raise ValueError(f'Página {number} excede o limite de imagem. Tente DPI menor.')
            with tempfile.TemporaryDirectory(prefix='ocr-', dir=Path(root)/'.local/research') as temporary:
                prefix = str(Path(temporary)/'page')
                subprocess.run(['pdftoppm', '-f', str(number), '-l', str(number), '-singlefile', '-r', str(recipe['dpi']), '-png', str(source), prefix], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=90, check=True)
                subprocess.run(['tesseract', prefix+'.png', prefix, '-l', '+'.join(recipe['languages']), '--psm', str(recipe['psm'])] + (['--tessdata-dir', recipe['tessdata_dir']] if recipe.get('tessdata_dir') else []) + ['txt', 'tsv'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=180, env=env, check=True)
                raw_path, geometry_path = Path(prefix+'.txt'), Path(prefix+'.tsv')
                if raw_path.stat().st_size > 8*1024**2 or geometry_path.stat().st_size > 16*1024**2:
                    raise ValueError('Resultado OCR excedeu o limite por página.')
                value = raw_path.read_text(encoding='utf-8')
                if len(value) > 2000000:
                    raise ValueError('Texto OCR excedeu o limite por página.')
                geometry = geometry_path.read_text(encoding='utf-8')
                engine = f'{version}; {renderer_version}; ocr-v1; '+json.dumps(recipe, ensure_ascii=False)
                db.execute('INSERT INTO pdf_ocr_candidates VALUES(?,?,?,?,?,?,?,?,?)', ('ocrpage-'+__import__('secrets').token_hex(16), job_id, job['source_id'], number, value, hashlib.sha256(value.encode()).hexdigest(), engine, geometry, now()))
                db.execute('UPDATE pdf_ocr_jobs SET updated_at=? WHERE id=?', (now(), job_id)); db.commit()
        db.execute("UPDATE pdf_ocr_jobs SET state='completed',error=NULL,updated_at=? WHERE id=?", (now(), job_id)); db.commit()
    except Exception as error:
        message = str(error)[:1000]
        if isinstance(error, subprocess.CalledProcessError):
            message = 'Falha na ferramenta OCR: '+(error.stderr or b'').decode('utf-8', errors='replace')[-1000:]
        db.execute("UPDATE pdf_ocr_jobs SET state='failed',error=?,updated_at=? WHERE id=?", (message, now(), job_id)); db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
