"""Extrator isolado: executado pelo backend, nunca no atendimento HTTP."""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def run(root, source_id):
    # Importação opcional só no worker. Não inicializar PDFSources (iniciaria outra fila).
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024, 1024 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, (300, 300))
    from pypdf import PdfReader, __version__
    directory = Path(root) / '.local/research'
    db = sqlite3.connect(directory / 'jobs.sqlite3', timeout=20)
    try:
        db.execute("UPDATE pdf_jobs SET state='running',engine=?,updated_at=? WHERE source_id=?", ('pypdf/' + __version__ + ';native-v1', timestamp(), source_id))
        db.execute("UPDATE pdf_sources SET state='running',error=NULL WHERE id=?", (source_id,))
        db.commit()
        path = directory / 'sources' / (source_id + '.pdf')
        with path.open('rb') as file:
            digest = hashlib.file_digest(file, 'sha256').hexdigest()
        expected = db.execute('SELECT sha256 FROM pdf_sources WHERE id=?', (source_id,)).fetchone()[0]
        if digest != expected:
            raise ValueError('O PDF preservado mudou. Recupere a fonte original do backup.')
        reader = PdfReader(path)
        if reader.is_encrypted:
            raise ValueError('PDF protegido: envie uma cópia desprotegida cuja leitura seja permitida.')
        count = len(reader.pages)
        if not 1 <= count <= 1500:
            raise ValueError('Este piloto aceita de 1 a 1500 páginas por PDF.')
        db.execute('UPDATE pdf_sources SET page_count=? WHERE id=?', (count, source_id))
        db.commit()
        for number, page in enumerate(reader.pages, 1):
            existing = db.execute('SELECT error FROM pdf_pages WHERE source_id=? AND page_number=?', (source_id, number)).fetchone()
            if existing and existing[0] is None:
                continue
            error = None
            try:
                content = page.get_contents()
                if content is not None and len(content.get_data()) > 20 * 1024 * 1024:
                    raise ValueError('Conteúdo expandido acima de 20 MiB; exige processamento específico.')
                raw = page.extract_text() or ''
                if len(raw) > 2_000_000:
                    raise ValueError('Texto desta página excede o limite de 2 milhões de caracteres.')
                visible = sum(not c.isspace() for c in raw)
                invalid = raw.count('\ufffd') + raw.count('\x00')
                if not visible:
                    diagnosis, reason = 'ocr_candidate', 'Sem texto extraível: conferir imagem, página branca ou necessidade de OCR.'
                elif invalid > max(2, visible * .02) or visible < 40:
                    diagnosis, reason = 'check', 'Texto curto ou com caracteres inválidos: conferir visualmente; OCR não é automático.'
                else:
                    diagnosis, reason = 'text', 'Camada textual extraída; ordem, notas e parágrafos ainda precisam de revisão.'
            except Exception as exc:
                raw, diagnosis, reason, error = '', 'error', 'Falha nesta página; as demais continuam.', str(exc)[:1000]
            page_id = source_id + '-p' + str(number).zfill(5)
            paragraphs = []
            # IDs persistidos da extração inicial; não são regenerados ao editar. Fronteiras candidatas.
            for index, match in enumerate(re.finditer(r'\S[\s\S]*?(?=\n[ \t]*\n|\Z)', raw), 1):
                paragraphs.append({'id': page_id + '-u' + str(index).zfill(5), 'start': match.start(), 'end': match.end(),
                                   'status': 'candidate', 'boundary': 'blank_line', 'text_sha256': hashlib.sha256(match[0].encode()).hexdigest()})
            db.execute('''INSERT OR REPLACE INTO pdf_pages VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
                       (page_id, source_id, number, None, raw,
                        hashlib.sha256(raw.encode()).hexdigest(), diagnosis, reason, error, json.dumps(paragraphs),
                        'pypdf/' + __version__ + ';native-v1'))
            db.execute('UPDATE pdf_jobs SET updated_at=? WHERE source_id=?', (timestamp(), source_id))
            db.commit()
        errors = db.execute('SELECT COUNT(*) FROM pdf_pages WHERE source_id=? AND error IS NOT NULL', (source_id,)).fetchone()[0]
        state = 'completed_with_errors' if errors else 'completed'
        db.execute('UPDATE pdf_sources SET state=? WHERE id=?', (state, source_id))
        db.execute('UPDATE pdf_jobs SET state=?,error=NULL,updated_at=? WHERE source_id=?', (state, timestamp(), source_id))
        db.commit()
    except Exception as exc:
        db.execute("UPDATE pdf_sources SET state='failed',error=? WHERE id=?", (str(exc)[:1000], source_id))
        db.execute("UPDATE pdf_jobs SET state='failed',error=?,updated_at=? WHERE source_id=?", (str(exc)[:1000], timestamp(), source_id))
        db.commit()
    finally:
        db.close()


if __name__ == '__main__':
    if len(sys.argv) != 3 or not re.fullmatch(r'pdf-[a-f0-9]{32}', sys.argv[2]):
        raise SystemExit('Uso interno: backend.pdf_worker ROOT SOURCE_ID')
    run(sys.argv[1], sys.argv[2])
