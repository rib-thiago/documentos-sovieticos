"""Percurso real de PDF/OCR no Chromium, usando exclusivamente um acervo temporário.

Opcional: playwright + chromium; execute com python3 -m unittest tests.test_pdf_browser -v.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
from backend import catalog
from backend.server import create_server
from tests.test_backend import fixture
try:
 from playwright.sync_api import sync_playwright,expect
except ImportError:sync_playwright=None
try:
 from pypdf import PdfReader,PdfWriter
except ImportError:PdfReader=PdfWriter=None
ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(sync_playwright and PdfWriter,'Playwright/Chromium opcionais para a verificação no navegador')
class PDFBrowserTests(unittest.TestCase):
 def test_upload_ocr_review_save_and_pdf_operations(self):
  with tempfile.TemporaryDirectory(prefix='discovery-browser-') as temporary:
   root=Path(temporary);fixture(root);catalog.migrate(root)
   queue=root/'docs/revisao-markdown/pendencias.csv';queue.parent.mkdir(parents=True,exist_ok=True);queue.write_text('chave,prioridade,status,id,problema,dificuldade,dificuldade_encontrada,acao_sugerida,arquivo_markdown,url_teste,colecoes,titulo_ru,fonte,trechos\n')
   shutil.copytree(ROOT/'assets',root/'assets',dirs_exist_ok=True);shutil.copytree(ROOT/'prototipo',root/'prototipo');shutil.copyfile(ROOT/'index.html',root/'index.html')
   writer=PdfWriter();reader=PdfReader(ROOT/'fontes/tukhachevsky/julgamento-1937-06-11.ru.pdf')
   writer.add_page(reader.pages[0]);writer.add_page(reader.pages[1]);buffer=io.BytesIO();writer.write(buffer);writer.close();pdf=buffer.getvalue();source_hash=hashlib.sha256(pdf).hexdigest()
   unchanged={str(p.relative_to(root)):p.read_bytes() for p in (root/'data').rglob('*.json')}
   server=create_server(root,port=0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   address=f'http://127.0.0.1:{server.server_port}';errors=[]
   try:
    with sync_playwright() as p:
     browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
     context=browser.new_context(viewport={'width':1440,'height':1000});page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.set_default_timeout(20000)
     # Fonts are not part of this workflow and should not delay an offline test.
     page.route('https://fonts.googleapis.com/**',lambda route:route.abort());page.route('https://fonts.gstatic.com/**',lambda route:route.abort())
     try:
      page.goto(address+'/prototipo/ide/');expect(page.locator('#connection')).to_contain_text('Backend local disponível')
      page.locator('[data-section=tools]').click();page.locator('#sidebar-content .side-action').filter(has_text='Fontes PDF').first.click()
      frame=page.frame_locator('.editor-content:not([hidden]) iframe.embedded')
      frame.get_by_role('link',name='Receber PDF',exact=True).click()
      frame.get_by_label('Arquivo PDF').set_input_files({'name':'piloto-russo.pdf','mimeType':'application/pdf','buffer':pdf})
      frame.get_by_role('button',name='Enviar e preparar prévia').click()
      expect(frame.locator('.workspace-source-steps')).to_be_visible(timeout=30000)
      frame.locator('.workspace-source-steps').get_by_role('button',name='OCR',exact=True).click()
      expect(frame.get_by_role('button',name='Conferir lote OCR')).to_be_visible()
      expect(frame.locator('.pdf-ocr-controls')).to_have_attribute('open','')
      # This is the regression: both the configuration and its submit must be reachable.
      ocr_form=frame.locator('.pdf-ocr-controls form');ocr_form.get_by_label('Páginas físicas',exact=False).fill('1')
      expect(ocr_form.get_by_role('checkbox',name='Russo')).to_be_checked()
      frame.get_by_role('button',name='Conferir lote OCR').click()
      expect(frame.get_by_role('button',name='Confirmar e executar OCR local')).to_be_visible()
      frame.get_by_role('button',name='Confirmar e executar OCR local').click()
      expect(frame.get_by_role('button',name='Revisar resultado · página 1',exact=True)).to_be_visible(timeout=120000)
      frame.get_by_role('button',name='Revisar resultado · página 1',exact=True).click()
      expect(frame.get_by_role('button',name='Carregar este candidato no editor')).to_be_visible()
      frame.get_by_role('button',name='Carregar este candidato no editor').click()
      frame.locator('.workspace-review-sections').get_by_role('button',name='Texto',exact=True).click()
      frame.get_by_role('button',name='Transcrição',exact=True).click()
      text=frame.get_by_label('Texto da página');self.assertGreater(len(text.input_value().strip()),20)
      text.fill(text.input_value()+'\n\nNota técnica de teste isolado.')
      frame.get_by_label('Conferência',exact=True).select_option('reviewed')
      frame.get_by_role('button',name='Conferir alterações',exact=True).click()
      expect(frame.get_by_role('button',name='Confirmar gravação local',exact=True)).to_be_visible()
      frame.get_by_role('button',name='Confirmar gravação local',exact=True).click()
      expect(frame.get_by_text('Revisão salva. Texto bruto e original preservados.',exact=True)).to_be_visible()
      # Height changes and pane switches preserve the review host.
      frame.get_by_label('Altura da área de revisão em pixels').fill('620');frame.get_by_label('Altura da área de revisão em pixels').press('Tab')
      expect(frame.locator('[data-workspace-source]')).to_have_css('height','620px')
      # All diagnostic images live outside the repository.
      artifacts=Path(os.environ.get('DISCOVERY_BROWSER_ARTIFACTS','/tmp/discovery-browser-artifacts'));artifacts.mkdir(parents=True,exist_ok=True)
      page.screenshot(path=str(artifacts/'review.png'),full_page=True)
      # The source action opens the operation studio in the same workspace tab.
      frame.get_by_role('link',name='Extrair / dividir esta fonte',exact=True).click()
      expect(frame.get_by_role('button',name='Extrair páginas',exact=False)).to_be_visible()
      frame.get_by_label('Páginas a extrair',exact=True).fill('99')
      frame.get_by_role('button',name='Conferir operação antes de gerar').click()
      expect(frame.locator('.status.error')).to_be_visible()
      frame.get_by_label('Páginas a extrair',exact=True).fill('1')
      frame.get_by_role('button',name='Conferir operação antes de gerar').click()
      expect(frame.get_by_role('button',name='Confirmar e gerar PDFs locais')).to_be_visible()
      frame.get_by_role('button',name='Confirmar e gerar PDFs locais').click()
      expect(frame.get_by_role('link',name='Abrir resultado',exact=True)).to_be_visible(timeout=60000)
      page.screenshot(path=str(artifacts/'operations.png'),full_page=True)
      frame.get_by_role('button',name='Dividir em partes',exact=False).click()
      frame.get_by_label('Páginas por parte',exact=True).fill('1')
      frame.get_by_role('button',name='Conferir operação antes de gerar').click()
      expect(frame.get_by_role('button',name='Confirmar e gerar PDFs locais')).to_be_visible()
      frame.get_by_role('button',name='Confirmar e gerar PDFs locais').click()
      expect(frame.locator('.pdf-operation-progress').get_by_role('link',name='Abrir resultado',exact=True)).to_have_count(2,timeout=60000)
      page.screenshot(path=str(artifacts/'split.png'),full_page=True)
      # Narrow view: operation controls stay within the workspace and remain reachable.
      page.set_viewport_size({'width':600,'height':900})
      expect(frame.get_by_role('button',name='Dividir em partes',exact=False)).to_be_visible()
      self.assertTrue(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))

      # Verify no actual catalogue or source was overwritten.
      with server.pdf_sources.db() as db:
       sources=[dict(r) for r in db.execute('SELECT id,sha256 FROM pdf_sources')]
       source_id=next(s['id'] for s in sources if s['sha256']==source_hash)
       self.assertEqual(db.execute('SELECT count(*) FROM pdf_ocr_jobs WHERE state="completed"').fetchone()[0],1)
       self.assertEqual(db.execute('SELECT count(*) FROM pdf_operations WHERE state="completed"').fetchone()[0],2)
       saved=json.loads(db.execute('SELECT data FROM pdf_page_reviews WHERE source_id=? AND page_number=1',(source_id,)).fetchone()[0]);self.assertEqual(saved['status'],'reviewed')
      self.assertEqual(hashlib.sha256(server.pdf_sources.file_path(source_id).read_bytes()).hexdigest(),source_hash)
      for name,content in unchanged.items():self.assertEqual((root/name).read_bytes(),content,name)
      self.assertEqual(errors,[])
     except Exception:
      with server.pdf_sources.db() as db:
       print('SOURCE DIAGNOSTICS:',[dict(r) for r in db.execute('SELECT filename,state,error,page_count FROM pdf_sources')],flush=True)
      print('FRAME DIAGNOSTICS:',frame.locator('body').inner_text()[-7000:],flush=True)
      Path('/tmp/discovery-browser-artifacts').mkdir(exist_ok=True)
      page.screenshot(path='/tmp/discovery-browser-artifacts/failure.png',full_page=True)
      raise
     browser.close()
   finally:
    server.shutdown();thread.join();server.server_close()

if __name__=='__main__':unittest.main()
