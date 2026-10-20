"""Gera PDFs candidatos em processo isolado; nunca substitui o arquivo de origem."""
from __future__ import annotations
import hashlib
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def run(root, operation_id):
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024, 1024 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, (300, 300))
    from pypdf import PdfReader, PdfWriter, __version__
    directory = Path(root) / '.local/research'
    artifacts = directory / 'operations' / operation_id
    artifacts.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(directory / 'jobs.sqlite3', timeout=20)
    db.row_factory = sqlite3.Row
    try:
        operation = db.execute('SELECT * FROM pdf_operations WHERE id=?', (operation_id,)).fetchone()
        if not operation:
            raise ValueError('Operação não encontrada')
        db.execute("UPDATE pdf_operations SET state='running',error=NULL,updated_at=? WHERE id=?", (now(), operation_id))
        db.commit()
        path = directory / 'sources' / (operation['source_id'] + '.pdf')
        with path.open('rb') as source:
            digest = hashlib.file_digest(source, 'sha256').hexdigest()
        if digest != operation['source_sha256']:
            raise ValueError('O PDF de origem mudou. Recupere o original; nenhum derivado será sobrescrito.')
        reader = PdfReader(path)
        if reader.is_encrypted:
            raise ValueError('PDF protegido. Use uma cópia cuja leitura e manipulação sejam permitidas.')
        recipe = json.loads(operation['recipe'])
        if len(reader.pages) != recipe['source_page_count']:
            raise ValueError('A quantidade de páginas diverge da prévia. Confira a fonte.')
        rows = db.execute('SELECT * FROM pdf_operation_outputs WHERE operation_id=? ORDER BY position', (operation_id,)).fetchall()
        for output in rows:
            if output['result_source_id']:
                continue
            target = artifacts / f"part-{output['position']:03d}.pdf"
            if target.is_file() and output['artifact_sha256']:
                with target.open('rb') as stream:
                    if hashlib.file_digest(stream, 'sha256').hexdigest() == output['artifact_sha256']:
                        continue
            pages = json.loads(output['pages'])
            writer = PdfWriter()
            # append clona as páginas selecionadas e recursos; a ordem explícita é preservada.
            writer.append(reader, pages=[number - 1 for number in pages], import_outline=False)
            writer.add_metadata({'/Title': output['title'], '/Producer': 'Documentos Soviéticos · pdf-pages-v1',
                                 '/SourceID': operation['source_id'], '/SourceSHA256': operation['source_sha256'],
                                 '/SourcePhysicalPages': ','.join(map(str, pages))})
            temporary = target.with_suffix('.partial')
            try:
                with temporary.open('wb') as stream:
                    writer.write(stream)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
            with target.open('rb') as stream:
                sha = hashlib.file_digest(stream, 'sha256').hexdigest()
            db.execute('UPDATE pdf_operation_outputs SET artifact_sha256=?,engine=? WHERE operation_id=? AND position=?',
                       (sha, 'pypdf/' + __version__ + ';pdf-pages-v1', operation_id, output['position']))
            db.execute('UPDATE pdf_operations SET updated_at=? WHERE id=?', (now(), operation_id))
            db.commit()
            writer.close()
        db.execute("UPDATE pdf_operations SET state='generated',error=NULL,updated_at=? WHERE id=?", (now(), operation_id))
        db.commit()
    except Exception as error:
        db.execute("UPDATE pdf_operations SET state='failed',error=?,updated_at=? WHERE id=?", (str(error)[:1000], now(), operation_id))
        db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    if len(sys.argv) != 3 or not re.fullmatch(r'pdfop-[a-f0-9]{32}', sys.argv[2]):
        raise SystemExit('Uso interno: backend.pdf_operation_worker ROOT OPERATION_ID')
    run(sys.argv[1], sys.argv[2])
