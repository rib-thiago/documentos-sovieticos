"""O piloto só acrescenta recursos públicos explícitos, sem abrir arquivos de trabalho."""
import json
import shutil
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend import catalog as model
from backend.server import create_server
from tests.test_backend import fixture


class MesaPilotHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.root = Path(cls.directory.name)
        fixture(cls.root)
        queue=cls.root/"docs/revisao-markdown/pendencias.csv"
        queue.parent.mkdir(parents=True)
        queue.write_text("chave,prioridade,status,id,problema,dificuldade,dificuldade_encontrada,acao_sugerida,arquivo_markdown,url_teste,colecoes,titulo_ru,fonte,trechos,notas_do_revisor\n")
        source = Path(__file__).resolve().parents[1] / 'prototipo/mesa'
        target = cls.root / 'prototipo/mesa'
        target.mkdir(parents=True)
        for name in ('index.html', 'pilot.css', 'app.js', 'data.js', 'pdf.js', 'session.js', 'editorial.js', 'organization.js', 'pdf-workflow.js', 'controls.js', 'preparation.js', 'corpus.js', 'review.js', 'source-links.js', 'projects.js', 'passage-edit.js', 'library-tools.js', 'library-home.js', 'parity.js', 'entry.js'):
            shutil.copyfile(source / name, target / name)
        shutil.copyfile(Path(__file__).resolve().parents[1]/'assets/collection-zip.js',cls.root/'assets/collection-zip.js')
        (target / 'README.md').write_text('Arquivo privado para este teste')
        model.migrate(cls.root)
        cls.server = create_server(cls.root, port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:' + str(cls.server.server_address[1])

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.directory.cleanup()

    def test_directory_redirect_and_real_entry(self):
        with urlopen(self.url + '/prototipo/mesa', timeout=5) as response:
            self.assertTrue(response.url.endswith('/prototipo/mesa/'))
            self.assertIn('Biblioteca & Mesa', response.read().decode())

    def test_explicit_assets_and_mime(self):
        for name, mime in [('pilot.css', 'text/css'), ('app.js', 'javascript'),
                           ('data.js', 'javascript'), ('pdf.js', 'javascript'), ('session.js', 'javascript'), ('editorial.js', 'javascript'), ('organization.js', 'javascript'), ('pdf-workflow.js', 'javascript'), ('controls.js', 'javascript'), ('preparation.js', 'javascript'), ('corpus.js', 'javascript'), ('review.js', 'javascript'), ('source-links.js', 'javascript'), ('projects.js', 'javascript'), ('passage-edit.js', 'javascript'), ('library-tools.js', 'javascript'), ('library-home.js', 'javascript'), ('parity.js', 'javascript'), ('entry.js', 'javascript')]:
            with self.subTest(name=name), urlopen(self.url + '/prototipo/mesa/' + name) as response:
                self.assertIn(mime, response.headers['Content-Type'])
                self.assertGreater(len(response.read()), 50)

    def test_shared_zip_writer_is_served(self):
        with urlopen(self.url+'/assets/collection-zip.js') as response:
            self.assertIn('javascript',response.headers['Content-Type'])
            self.assertIn('function archiveStoredZip',response.read().decode())

    def test_private_files_not_exposed(self):
        for path in ('/prototipo/mesa/README.md', '/temporario/segredo.txt',
                     '/prototipo/mesa/../../backend/server.py'):
            with self.subTest(path=path), self.assertRaises(HTTPError) as error:
                urlopen(self.url + path, timeout=5)
            self.assertEqual(error.exception.code, 404)

    def test_official_home_and_catalog_remain_available(self):
        with urlopen(self.url + '/') as response:
            self.assertIn('Site existente', response.read().decode())
        with urlopen(self.url + '/data/manifest.json') as response:
            self.assertIn('showtrials-1', response.read().decode())

    def api(self, path, payload=None):
        token=self.server.editorial.token
        request=Request(self.url+path,data=None if payload is None else json.dumps(payload).encode(),headers={'Content-Type':'application/json','X-Editorial-Token':token,'Origin':self.url})
        with urlopen(request,timeout=15) as response:
            return json.load(response)

    def test_real_markdown_preview_save_and_recover_in_isolated_collection(self):
        original=(self.root/'originais/one.pt.md').read_text()
        russian=(self.root/'originais/one.ru.md').read_bytes()
        edition=self.api('/api/editorial/editions/showtrials-1:pt')
        proposal=self.api('/api/editorial/markdown/preview',{'revision':edition['revision'],'edition_id':edition['edition']['id'],'content_sha256':edition['edition']['sha256'],'content':original+'\n\npilotomesaunico\n'})
        self.assertEqual((self.root/'originais/one.pt.md').read_text(),original)
        saved=self.api('/api/editorial/save',{'preview_id':proposal['preview_id'],'acknowledge_warnings':False})
        self.assertIn('pilotomesaunico',(self.root/'originais/one.pt.md').read_text())
        self.assertGreater(self.api('/api/search?q=pilotomesaunico')['total'],0)
        history=self.api('/api/editorial/history?document=showtrials-1')
        self.assertTrue(any(item['id']==saved['history_id'] for item in history['items']))
        fresh=self.api('/api/editorial/documents/showtrials-1')
        restore=self.api('/api/editorial/preview',{'revision':fresh['revision'],'restore_id':saved['history_id']})
        self.api('/api/editorial/save',{'preview_id':restore['preview_id'],'acknowledge_warnings':False})
        self.assertEqual((self.root/'originais/one.pt.md').read_text(),original)
        self.assertEqual((self.root/'originais/one.ru.md').read_bytes(),russian)
        self.assertEqual(self.api('/api/search?q=pilotomesaunico')['total'],0)

    def test_corpus_preview_save_and_recover_in_isolated_collection(self):
        before_manifest=(self.root/'data/manifest.json').read_bytes()
        before_original=(self.root/'originais/one.ru.md').read_bytes()
        defaults={'collection_ids':['alpha','alpha/investigacao'],'source_name':'Fonte de teste','source_url':'https://example.org/corpus','author':'','date':'','archive':''}
        entries=[
            {'filename':'corpus-piloto-um.ru.md','id':'corpus-piloto-um','title':'Первый документ','language':'ru','role':'original','content':'# Первый документ\n\nПодлинный текст.\n'},
            {'filename':'corpus-piloto-um.pt.md','id':'corpus-piloto-um','title':'Primeiro documento','language':'pt','role':'translation','content':'# Primeiro documento\n\ncorpuspilotopesquisavel\n'},
            {'filename':'corpus-piloto-dois.en.md','id':'corpus-piloto-dois','title':'Second document','language':'en','role':'original','content':'# Second document\n\nOriginal in another language.\n'}]
        revision=self.api('/api/editorial/session')['revision']
        # Mesmo ID do acervo não pode ser sobrescrito por uma importação.
        conflict={**entries[0],'id':'showtrials-1'}
        rejected=self.api('/api/editorial/batches/preview',{'revision':revision,'defaults':defaults,'entries':[conflict]})
        self.assertFalse(rejected['can_save'])
        self.assertEqual((self.root/'data/manifest.json').read_bytes(),before_manifest)
        proposal=self.api('/api/editorial/batches/preview',{'revision':revision,'defaults':defaults,'entries':entries})
        self.assertEqual(proposal['creation']['count'],2)
        self.assertEqual(proposal['creation']['items'][0]['translations'][0]['language'],'pt')
        self.assertEqual((self.root/'data/manifest.json').read_bytes(),before_manifest)
        self.assertFalse((self.root/'originais/locais/corpus-piloto-um.ru.md').exists())
        receipt=self.api('/api/editorial/save',{'preview_id':proposal['preview_id'],'acknowledge_warnings':True})
        for item in entries:
            self.assertEqual((self.root/'originais/locais'/item['filename']).read_text(),item['content'])
        document=self.api('/api/editorial/documents/corpus-piloto-um')
        self.assertEqual(set(document['collection_ids']),{'alpha','alpha/investigacao'})
        self.assertEqual(document['document']['titles']['pt'],'Primeiro documento')
        self.assertEqual(self.api('/api/search?q=corpuspilotopesquisavel')['total'],1)
        history=self.api('/api/editorial/history?document='+receipt['entity']['id'])
        self.assertTrue(any(entry['id']==receipt['history_id'] for entry in history['items']))
        restore=self.api('/api/editorial/preview',{'revision':receipt['revision'],'restore_id':receipt['history_id']})
        self.api('/api/editorial/save',{'preview_id':restore['preview_id'],'acknowledge_warnings':True})
        self.assertEqual((self.root/'data/manifest.json').read_bytes(),before_manifest)
        self.assertEqual((self.root/'originais/one.ru.md').read_bytes(),before_original)
        self.assertEqual(self.api('/api/search?q=corpuspilotopesquisavel')['total'],0)
        for item in entries:self.assertFalse((self.root/'originais/locais'/item['filename']).exists())

    def test_review_queue_filter_save_and_restore_without_editing_text(self):
        import csv
        import io
        queue=self.root/'docs/revisao-markdown/pendencias.csv'
        old_queue=queue.read_bytes()
        reader=csv.DictReader(io.StringIO(old_queue.decode()))
        fields,rows=reader.fieldnames,list(reader)
        row={field:'' for field in fields}
        row.update(chave='showtrials-1:piloto-revisao',id='showtrials-1',prioridade='alta',status='pendente',problema='Revisar formatação piloto',dificuldade_encontrada='Conferir títulos',acao_sugerida='Examinar o Markdown')
        rows.append(row)
        stream=io.StringIO(newline='')
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
        queue.write_text(stream.getvalue())
        before_queue=queue.read_bytes()
        original=(self.root/'originais/one.ru.md').read_bytes()
        manifest=(self.root/'data/manifest.json').read_bytes()
        result=self.api('/api/editorial/queue?q=showtrials-1&status=abertos&priority=alta&collection=alpha&limit=25')
        self.assertEqual(result['total'],1)
        self.assertEqual(result['items'][0]['chave'],row['chave'])
        document=self.api('/api/editorial/documents/showtrials-1')
        proposal=self.api('/api/editorial/preview',{'revision':document['revision'],'document_id':'showtrials-1','issues':[{'chave':row['chave'],'status':'corrigido','prioridade':'baixa','dificuldade_encontrada':'Títulos conferidos','notas_do_revisor':'Revisão piloto concluída'}]})
        self.assertEqual(queue.read_bytes(),before_queue)
        receipt=self.api('/api/editorial/save',{'preview_id':proposal['preview_id'],'acknowledge_warnings':False})
        self.assertEqual(self.api('/api/editorial/queue?q=showtrials-1&status=abertos')['total'],0)
        reviewed=self.api('/api/editorial/queue?q=showtrials-1&status=corrigido&priority=baixa')['items']
        self.assertEqual(reviewed[0]['notas_do_revisor'],'Revisão piloto concluída')
        self.assertEqual((self.root/'originais/one.ru.md').read_bytes(),original)
        self.assertEqual((self.root/'data/manifest.json').read_bytes(),manifest)
        restore=self.api('/api/editorial/preview',{'revision':receipt['revision'],'restore_id':receipt['history_id']})
        self.api('/api/editorial/save',{'preview_id':restore['preview_id'],'acknowledge_warnings':False})
        self.assertEqual(queue.read_bytes(),before_queue)
        queue.write_bytes(old_queue)

    def test_source_link_and_static_selection_preserve_source_and_transcription(self):
        import io
        import time
        import hashlib
        from pypdf import PdfWriter, PdfReader
        original=(self.root/'originais/one.ru.md').read_bytes()
        manifest=(self.root/'data/manifest.json').read_bytes()
        writer=PdfWriter()
        for width in (201,202):writer.add_blank_page(width=width,height=300)
        stream=io.BytesIO();writer.write(stream);writer.close();source_bytes=stream.getvalue()
        request=Request(self.url+'/api/editorial/pdf/upload',data=source_bytes,headers={'Content-Type':'application/pdf','X-Editorial-Token':self.server.editorial.token,'X-PDF-Filename':'vinculo-piloto.pdf','Origin':self.url})
        with urlopen(request,timeout=15) as response:source=json.load(response)['source_id']
        for _ in range(100):
            info=self.api('/api/editorial/pdf/'+source)
            if info['page_count']==2:break
            time.sleep(.1)
        self.assertEqual(info['page_count'],2)
        empty=self.api('/api/editorial/pdf/links?source='+source)['items']
        self.assertEqual(empty,[])
        proposal=self.api('/api/editorial/pdf/links/preview',{'action':'create','source_id':source,'project_id':'','document_id':'showtrials-1','pages':'2','notes':'Teste técnico; não certifica correspondência histórica.'})
        self.assertEqual(self.api('/api/editorial/pdf/links?source='+source)['items'],[])
        link=self.api('/api/editorial/pdf/links/save',{'preview_id':proposal['preview_id']})
        self.assertEqual(link['pages'],[2])
        before_projection=self.api('/api/editorial/pdf/publication')['published']
        plan=self.api('/api/editorial/pdf/publication/preview',{'action':'publish','link_ids':[link['id']],'include_transcription':False})
        self.assertEqual(self.api('/api/editorial/pdf/publication')['published'],before_projection)
        with urlopen(self.url+'/api/editorial/pdf/publication/'+plan['release_id']+'/preview.pdf?link='+link['id']) as response:
            preview=PdfReader(io.BytesIO(response.read()))
            self.assertEqual(len(preview.pages),1)
            self.assertEqual(float(preview.pages[0].mediabox.width),202)
        receipt=self.api('/api/editorial/pdf/publication/apply',{'release_id':plan['release_id'],'confirm':True})
        projected=self.api('/api/editorial/pdf/publication')['published']
        public=next(item for item in projected if item['id']==link['id'])
        self.assertEqual(public['published_page_map'],{'2':1})
        self.assertNotIn('notes',public)
        self.assertNotIn('project_id',public)
        with urlopen(self.url+'/'+public['pdf_url']) as response:self.assertEqual(len(PdfReader(io.BytesIO(response.read())).pages),1)
        self.assertEqual((self.root/'originais/one.ru.md').read_bytes(),original)
        self.assertEqual((self.root/'data/manifest.json').read_bytes(),manifest)
        with urlopen(self.url+'/api/editorial/pdf/'+source+'/file') as response:self.assertEqual(hashlib.sha256(response.read()).digest(),hashlib.sha256(source_bytes).digest())
        restore=self.api('/api/editorial/pdf/publication/preview',{'action':'restore','history_id':receipt['history_id']})
        self.api('/api/editorial/pdf/publication/apply',{'release_id':restore['release_id'],'confirm':True})
        self.assertEqual(self.api('/api/editorial/pdf/publication')['published'],before_projection)
        self.assertTrue(self.api('/api/editorial/pdf/links?source='+source)['items'][0]['active'])
        history=self.api('/api/editorial/pdf/links/'+link['id']+'/history')['items']
        revert=self.api('/api/editorial/pdf/links/preview',{'action':'restore','id':link['id'],'revision':link['revision'],'history_id':history[0]['id']})
        self.api('/api/editorial/pdf/links/save',{'preview_id':revert['preview_id']})
        self.assertFalse(self.api('/api/editorial/pdf/links?source='+source)['items'][0]['active'])

    def test_project_pdf_derivatives_units_anchors_and_recovery(self):
        import io
        import time
        import hashlib
        from urllib.parse import urlencode
        from pypdf import PdfWriter
        from backend.translations import split_export_headers
        original=(self.root/'originais/one.ru.md').read_bytes()
        manifest=(self.root/'data/manifest.json').read_bytes()
        project={'title':'Paridade PDF isolada','description':'','collection_id':'alpha','document_ids':['showtrials-1'],'source_ids':[],'archived':False}
        proposal=self.api('/api/editorial/projects/preview',{'project_id':None,'revision':None,'project':project})
        project_id=self.api('/api/editorial/projects/save',{'preview_id':proposal['preview_id']})['project_id']
        writer=PdfWriter();writer.add_blank_page(width=219,height=311)
        stream=io.BytesIO();writer.write(stream);writer.close();pdf=stream.getvalue()
        request=Request(self.url+'/api/editorial/pdf/upload',data=pdf,headers={'Content-Type':'application/pdf','X-Editorial-Token':self.server.editorial.token,'X-PDF-Filename':'paridade-projeto.pdf','X-Research-Project':project_id,'Origin':self.url})
        with urlopen(request,timeout=15) as response:source=json.load(response)['source_id']
        self.assertIn(source,self.api('/api/editorial/projects/'+project_id)['source_ids'])
        for _ in range(100):
            info=self.api('/api/editorial/pdf/'+source)
            if info['state']=='completed':break
            time.sleep(.1)
        review=self.api('/api/editorial/pdf/'+source+'/pages/1/review')
        content='😀 Первый абзац. Второй абзац.'
        plan=self.api('/api/editorial/pdf/review/preview',{'source_id':source,'page_number':1,'revision':review['revision'],'review':{'text':content,'status':'reviewed','printed_label':'4','notes':'Teste isolado','basis':'native'}})
        self.api('/api/editorial/pdf/review/save',{'preview_id':plan['preview_id']})
        geometry=self.api('/api/editorial/pdf/'+source+'/pages/1/geometry')
        first=geometry['units'][0]
        split=self.api('/api/editorial/pdf/alignment/preview',{'source_id':source,'page_number':1,'revision':geometry['revision'],'unit_id':first['id'],'action':'split','offset':content.index('Второй')})
        self.assertEqual(split['after']['text'],content)
        self.api('/api/editorial/pdf/review/save',{'preview_id':split['preview_id']})
        geometry=self.api('/api/editorial/pdf/'+source+'/pages/1/geometry')
        self.assertEqual(len(geometry['units']),2)
        first=geometry['units'][0]
        boxes=[[.1,.2,.5,.1]]
        locate=self.api('/api/editorial/pdf/alignment/preview',{'source_id':source,'page_number':1,'revision':geometry['revision'],'unit_id':first['id'],'action':'boxes','boxes':boxes})
        self.api('/api/editorial/pdf/review/save',{'preview_id':locate['preview_id']})
        plan=self.api('/api/editorial/pdf/links/preview',{'action':'create','source_id':source,'project_id':project_id,'document_id':'showtrials-1','pages':'1','notes':'Associação técnica fictícia do teste'})
        link=self.api('/api/editorial/pdf/links/save',{'preview_id':plan['preview_id']})
        body=split_export_headers(original.decode())['body'];quote=body[:min(20,len(body))]
        association={'language':'ru','body_sha256':hashlib.sha256(body.encode()).hexdigest(),'quote':quote,'start':0,'end':len(quote.encode('utf-16-le'))//2,'page_number':1,'notes':'','unit_id':first['id']}
        plan=self.api('/api/editorial/pdf/links/preview',{'action':'anchor','id':link['id'],'revision':link['revision'],'anchor':association})
        link=self.api('/api/editorial/pdf/links/save',{'preview_id':plan['preview_id']})
        self.assertEqual(link['anchors'][0]['unit_boxes'],boxes)
        self.assertEqual(self.api('/api/editorial/pdf/links?document=showtrials-1')['items'],[])
        scoped=self.api('/api/editorial/pdf/links?'+urlencode({'document':'showtrials-1','project':project_id}))['items'][0]
        self.assertFalse(scoped['anchors'][0]['stale_page'])
        with self.assertRaises(HTTPError):self.api('/api/editorial/pdf/publication/preview',{'action':'publish','link_ids':[link['id']],'include_transcription':False})
        geometry=self.api('/api/editorial/pdf/'+source+'/pages/1/geometry')
        merge=self.api('/api/editorial/pdf/alignment/preview',{'source_id':source,'page_number':1,'revision':geometry['revision'],'unit_id':first['id'],'action':'merge'})
        self.api('/api/editorial/pdf/review/save',{'preview_id':merge['preview_id']})
        scoped=self.api('/api/editorial/pdf/links?'+urlencode({'document':'showtrials-1','project':project_id}))['items'][0]
        self.assertTrue(scoped['anchors'][0]['stale_page'])
        remove=self.api('/api/editorial/pdf/links/preview',{'action':'remove_anchor','id':link['id'],'revision':link['revision'],'anchor_id':link['anchors'][0]['id']})
        removed=self.api('/api/editorial/pdf/links/save',{'preview_id':remove['preview_id']})
        history=self.api('/api/editorial/pdf/links/'+link['id']+'/history')['items'][0]
        restore=self.api('/api/editorial/pdf/links/preview',{'action':'restore','id':link['id'],'revision':removed['revision'],'history_id':history['id']})
        restored=self.api('/api/editorial/pdf/links/save',{'preview_id':restore['preview_id']})
        self.assertEqual(restored['anchors'][0]['quote'],quote)
        plan=self.api('/api/editorial/pdf/operations/preview',{'source_id':source,'project_id':project_id,'mode':'extract','pages':'1','split_mode':'size','pages_per_part':1,'ranges':''})
        job=self.api('/api/editorial/pdf/operations/start',{'preview_id':plan['preview_id']})
        for _ in range(150):
            operation=self.api('/api/editorial/pdf/operations/'+job['id'])
            if operation['state'] in ('completed','failed','interrupted'):break
            time.sleep(.1)
        self.assertEqual(operation['state'],'completed')
        derived=operation['outputs'][0]['result_source_id']
        self.assertIn(derived,self.api('/api/editorial/projects/'+project_id)['source_ids'])
        self.assertEqual(self.server.pdf_sources.file_path(source).read_bytes(),pdf)
        self.assertEqual((self.root/'originais/one.ru.md').read_bytes(),original)
        self.assertEqual((self.root/'data/manifest.json').read_bytes(),manifest)

    def test_private_project_save_promotion_and_history_are_separate(self):
        from urllib.parse import urlencode
        original=(self.root/'originais/one.pt.md').read_text()
        manifest=(self.root/'data/manifest.json').read_bytes()
        project={'title':'Projeto piloto isolado','description':'Teste de versões privadas','collection_id':'alpha','document_ids':['showtrials-1'],'source_ids':[],'archived':False}
        proposal=self.api('/api/editorial/projects/preview',{'project_id':None,'revision':None,'project':project})
        self.assertFalse(any(p['id']==proposal['project_id'] for p in self.api('/api/editorial/projects')['items']))
        receipt=self.api('/api/editorial/projects/save',{'preview_id':proposal['preview_id']})
        project_id=receipt['project_id']
        params=urlencode({'project':project_id,'edition':'showtrials-1:pt'})
        snapshot=self.api('/api/editorial/workspace/edition?'+params)
        self.assertFalse(snapshot['has_draft'])
        draft=snapshot['content']+'\n\nprivadamesaprojetounico\n'
        private=self.api('/api/editorial/workspace/preview',{'project_id':project_id,'edition_id':snapshot['edition_id'],'revision':snapshot['revision'],'content_sha256':snapshot['content_sha256'],'content':draft})
        self.assertFalse(self.api('/api/editorial/workspace/edition?'+params)['has_draft'])
        saved=self.api('/api/editorial/workspace/save',{'preview_id':private['preview_id']})
        fresh=self.api('/api/editorial/workspace/edition?'+params)
        self.assertTrue(fresh['has_draft'])
        self.assertIn('privadamesaprojetounico',fresh['content'])
        self.assertEqual((self.root/'originais/one.pt.md').read_text(),original)
        self.assertEqual((self.root/'data/manifest.json').read_bytes(),manifest)
        self.assertEqual(self.api('/api/search?q=privadamesaprojetounico')['total'],0)
        # Tradução ainda inexistente também fica restrita ao projeto.
        english_params=urlencode({'project':project_id,'edition':'showtrials-1:en'})
        english=self.api('/api/editorial/workspace/edition?'+english_params)
        self.assertFalse(english['canonical_exists'])
        translation=self.api('/api/editorial/workspace/preview',{'project_id':project_id,'edition_id':english['edition_id'],'revision':english['revision'],'content_sha256':english['content_sha256'],'content':'# Private translation\n\nText kept inside this project.\n','filename':'showtrials-1.en.md'})
        self.api('/api/editorial/workspace/save',{'preview_id':translation['preview_id']})
        versions=self.api('/api/editorial/workspace/document?'+urlencode({'project':project_id,'document':'showtrials-1'}))['editions']
        self.assertIn('en',[edition['language'] for edition in versions])
        self.assertEqual((self.root/'data/manifest.json').read_bytes(),manifest)
        # Versão de outro projeto não vê a edição privada do primeiro.
        second=self.api('/api/editorial/projects/preview',{'project_id':None,'revision':None,'project':{**project,'title':'Outro projeto'}})
        other=self.api('/api/editorial/projects/save',{'preview_id':second['preview_id']})['project_id']
        self.assertNotIn('privadamesaprojetounico',self.api('/api/editorial/workspace/edition?'+urlencode({'project':other,'edition':'showtrials-1:pt'}))['content'])
        promotion=self.api('/api/editorial/workspace/promotion-preview',{'project_id':project_id,'edition_id':fresh['edition_id'],'revision':fresh['revision'],'content_sha256':fresh['content_sha256']})
        self.assertEqual((self.root/'originais/one.pt.md').read_text(),original)
        # A prévia de promoção não pode ser aplicada pelo salvamento editorial comum.
        with self.assertRaises(HTTPError):self.api('/api/editorial/save',{'preview_id':promotion['preview_id'],'acknowledge_warnings':True})
        incorporated=self.api('/api/editorial/workspace/promote',{'promotion_id':promotion['workspace_promotion_id'],'confirm_replace':True,'acknowledge_warnings':True})
        self.assertIn('privadamesaprojetounico',(self.root/'originais/one.pt.md').read_text())
        self.assertGreater(self.api('/api/search?q=privadamesaprojetounico')['total'],0)
        canonical_restore=self.api('/api/editorial/preview',{'revision':incorporated['revision'],'restore_id':incorporated['history_id']})
        self.api('/api/editorial/save',{'preview_id':canonical_restore['preview_id'],'acknowledge_warnings':True})
        self.assertEqual((self.root/'originais/one.pt.md').read_text(),original)
        self.assertEqual((self.root/'data/manifest.json').read_bytes(),manifest)
        private_history=self.api('/api/editorial/workspace/history?'+params)['items']
        self.assertTrue(any(entry['id']==saved['history_id'] for entry in private_history))
        current=self.api('/api/editorial/workspace/edition?'+params)
        undo=self.api('/api/editorial/workspace/preview',{'project_id':project_id,'edition_id':current['edition_id'],'revision':current['revision'],'content_sha256':current['content_sha256'],'content':current['content'],'history_id':saved['history_id']})
        self.assertTrue(undo['discard'])
        self.api('/api/editorial/workspace/save',{'preview_id':undo['preview_id']})
        self.assertFalse(self.api('/api/editorial/workspace/edition?'+params)['has_draft'])
        project_history=self.api('/api/editorial/projects/'+project_id+'/history')['items']
        self.assertTrue(any(entry['id']==receipt['history_id'] for entry in project_history))

    def test_passage_correction_preserves_context_original_and_history(self):
        original=(self.root/'originais/one.pt.md').read_text()
        russian=(self.root/'originais/one.ru.md').read_bytes()
        before_manifest=(self.root/'data/manifest.json').read_bytes()
        snapshot=self.api('/api/editorial/editions/showtrials-1:pt')
        body=original.replace('Tradução','😀 Tradução',1)
        seed=self.api('/api/editorial/markdown/preview',{'revision':snapshot['revision'],'edition_id':'showtrials-1:pt','content_sha256':snapshot['edition']['sha256'],'content':body})
        seed_receipt=self.api('/api/editorial/save',{'preview_id':seed['preview_id'],'acknowledge_warnings':False})
        fresh=self.api('/api/editorial/editions/showtrials-1:pt')
        start=body.index('Nikolaev');end=start+len('Nikolaev')
        payload={'revision':fresh['revision'],'edition_id':'showtrials-1:pt','content_sha256':fresh['edition']['sha256'],'start':start,'end':end,'expected':'Nikolaev','replacement':'Nikolaev passagemcorrigidapiloto'}
        preview=self.api('/api/editorial/passages/preview',payload)
        self.assertEqual((self.root/'originais/one.pt.md').read_text(),body)
        receipt=self.api('/api/editorial/save',{'preview_id':preview['preview_id'],'acknowledge_warnings':False})
        self.assertEqual((self.root/'originais/one.pt.md').read_text(),body[:start]+payload['replacement']+body[end:])
        self.assertEqual((self.root/'originais/one.ru.md').read_bytes(),russian)
        self.assertGreater(self.api('/api/search?q=passagemcorrigidapiloto')['total'],0)
        with self.assertRaises(HTTPError):self.api('/api/editorial/passages/preview',payload)
        protected=self.api('/api/editorial/editions/showtrials-1:ru')
        with self.assertRaises(HTTPError):self.api('/api/editorial/passages/preview',{'revision':protected['revision'],'edition_id':'showtrials-1:ru','content_sha256':protected['edition']['sha256'],'start':0,'end':2,'expected':protected['content'][:2],'replacement':'Outro'})
        undo=self.api('/api/editorial/preview',{'revision':receipt['revision'],'restore_id':receipt['history_id']})
        undo_receipt=self.api('/api/editorial/save',{'preview_id':undo['preview_id'],'acknowledge_warnings':False})
        self.assertEqual((self.root/'originais/one.pt.md').read_text(),body)
        unseed=self.api('/api/editorial/preview',{'revision':undo_receipt['revision'],'restore_id':seed_receipt['history_id']})
        self.api('/api/editorial/save',{'preview_id':unseed['preview_id'],'acknowledge_warnings':False})
        self.assertEqual((self.root/'originais/one.pt.md').read_text(),original)
        self.assertEqual((self.root/'data/manifest.json').read_bytes(),before_manifest)

    def test_library_content_search_has_language_snippet_and_collection_filter(self):
        from urllib.parse import urlencode
        result=self.api('/api/search?'+urlencode({'q':'редкийтермин','language':'ru','collection':'alpha','scope':'all','limit':'20'}))
        self.assertEqual(result['total'],1)
        self.assertEqual(result['items'][0]['id'],'showtrials-1')
        self.assertEqual(result['items'][0]['match']['language'],'ru')
        self.assertIn('редкийтермин',result['items'][0]['match']['snippet'])
        self.assertEqual(self.api('/api/search?'+urlencode({'q':'редкийтермин','language':'pt'}))['total'],0)
        self.assertEqual(self.api('/api/search?'+urlencode({'q':'редкийтермин','collection':'beta/investigacao'}))['total'],0)
        phrase=self.api('/api/search?'+urlencode({'q':'"passagem exclusiva"','language':'pt'}))
        self.assertEqual(phrase['total'],1)
        self.assertEqual(phrase['items'][0]['match']['language'],'pt')

    def test_real_translation_warning_and_recovery_in_isolated_collection(self):
        original=(self.root/'originais/two.ru.md').read_bytes()
        document=self.api('/api/editorial/documents/showtrials-2')
        proposal=self.api('/api/editorial/translations/preview',{'revision':document['revision'],'document_id':'showtrials-2','language':'pt','filename':'outro-documento.en.md','content':'# Tradução de teste\n\ntraducaopilotomesaunica\n','title':''})
        self.assertTrue(proposal['requires_acknowledgement'])
        self.assertIn('structure',proposal['translation'])
        target=self.root/proposal['translation']['target_file']
        self.assertFalse(target.exists())
        with self.assertRaises(HTTPError) as error:
            self.api('/api/editorial/save',{'preview_id':proposal['preview_id'],'acknowledge_warnings':False})
        self.assertEqual(error.exception.code,400)
        self.assertFalse(target.exists())
        saved=self.api('/api/editorial/save',{'preview_id':proposal['preview_id'],'acknowledge_warnings':True})
        self.assertTrue(target.exists())
        self.assertEqual((self.root/'originais/two.ru.md').read_bytes(),original)
        self.assertGreater(self.api('/api/search?q=traducaopilotomesaunica')['total'],0)
        fresh=self.api('/api/editorial/documents/showtrials-2')
        restore=self.api('/api/editorial/preview',{'revision':fresh['revision'],'restore_id':saved['history_id']})
        self.api('/api/editorial/save',{'preview_id':restore['preview_id'],'acknowledge_warnings':False})
        self.assertFalse(target.exists())
        self.assertEqual((self.root/'originais/two.ru.md').read_bytes(),original)

    def test_metadata_memberships_and_recovery_preserve_sources(self):
        original={p.name:p.read_bytes() for p in (self.root/'originais').glob('*.md')}
        snapshot=self.api('/api/editorial/documents/showtrials-1')
        result=self.api('/api/editorial/preview',{'revision':snapshot['revision'],'document_id':'showtrials-1','document':{'titles':{'pt':'Título pilotometadadosunico'},'historical_date':{'display':'3 de dezembro de 1934','value':'1934-12-03','precision':'day'},'author_label':'Автор','archive_reference':'Arquivo de teste'},'collection_ids':['alpha','alpha/investigacao','beta','beta/investigacao']})
        self.assertEqual(self.api('/api/editorial/documents/showtrials-1')['document'],snapshot['document'])
        receipt=self.api('/api/editorial/save',{'preview_id':result['preview_id'],'acknowledge_warnings':False})
        changed=self.api('/api/editorial/documents/showtrials-1')
        self.assertEqual(changed['document']['titles']['pt'],'Título pilotometadadosunico')
        self.assertEqual(set(changed['collection_ids']),{'alpha','alpha/investigacao','beta','beta/investigacao'})
        self.assertEqual(changed['document']['source'],snapshot['document']['source'])
        self.assertEqual(original,{p.name:p.read_bytes() for p in (self.root/'originais').glob('*.md')})
        self.assertGreater(self.api('/api/search?q=pilotometadadosunico')['total'],0)
        restore=self.api('/api/editorial/preview',{'revision':changed['revision'],'restore_id':receipt['history_id']})
        self.api('/api/editorial/save',{'preview_id':restore['preview_id'],'acknowledge_warnings':False})
        restored=self.api('/api/editorial/documents/showtrials-1')
        self.assertEqual(restored['document'],snapshot['document'])
        self.assertEqual(set(restored['collection_ids']),set(snapshot['collection_ids']))

    def test_collection_subcollection_lifecycle_preserves_identifiers(self):
        def proposal(identifier,slug,title,parent='',existing=None):
            return self.api('/api/editorial/collections/preview',{'revision':self.api('/api/editorial/session')['revision'],'collection_id':existing,'slug':slug,'parent_id':parent,'title_pt':title,'title_ru':'Коллекция','subtitle':'','description':'Apresentação de teste','cover':'','accent':'#8b2c2c','source_url':'https://example.org/fonte'})
        root='mesa-teste-isolado'
        before=self.api('/api/collections')
        first=proposal(root,root,'Coleção piloto isolada')
        self.assertEqual(self.api('/api/collections'),before)
        saved_root=self.api('/api/editorial/save',{'preview_id':first['preview_id'],'acknowledge_warnings':False})
        child=proposal(root+'/fontes','fontes','Subcoleção de fontes',root)
        saved_child=self.api('/api/editorial/save',{'preview_id':child['preview_id'],'acknowledge_warnings':False})
        changed=proposal(root+'/fontes','fontes','Subcoleção revisada',root,root+'/fontes')
        saved_edit=self.api('/api/editorial/save',{'preview_id':changed['preview_id'],'acknowledge_warnings':False})
        current=self.api('/api/editorial/collections/'+root+'%2Ffontes')['collection']
        self.assertEqual(current['id'],root+'/fontes')
        self.assertEqual(current['titles']['pt'],'Subcoleção revisada')
        with self.assertRaises(HTTPError) as error:
            proposal(root+'/fontes','outra-url','Não deve salvar',root,root+'/fontes')
        self.assertEqual(error.exception.code,400)
        for receipt in (saved_edit,saved_child,saved_root):
            restore=self.api('/api/editorial/preview',{'revision':self.api('/api/editorial/session')['revision'],'restore_id':receipt['history_id']})
            self.api('/api/editorial/save',{'preview_id':restore['preview_id'],'acknowledge_warnings':False})
        self.assertEqual(self.api('/api/collections'),before)

    def test_pdf_native_ocr_review_and_incorporation_without_touching_original(self):
        import hashlib
        import io
        import subprocess
        import time
        import zlib
        try:
            from pypdf import PdfWriter, PdfReader
            from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject, NumberObject
        except ImportError:
            self.skipTest('pypdf opcional ausente')
        writer=PdfWriter();page=writer.add_blank_page(width=612,height=792)
        font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
        page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
        stream=DecodedStreamObject();stream.set_data(b'BT /F1 23 Tf 72 700 Td (Historical research document.) Tj 0 -45 Td (Preserve the original source.) Tj ET');page[NameObject('/Contents')]=writer._add_object(stream)
        native=io.BytesIO();writer.write(native);writer.close()
        final=PdfWriter();final.add_page(PdfReader(io.BytesIO(native.getvalue())).pages[0]);scan=final.add_blank_page(width=612,height=792)
        if shutil.which('pdftoppm'):
            input_path=self.root/'entrada-nativa-teste.pdf';input_path.write_bytes(native.getvalue());prefix=self.root/'imagem-teste'
            subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to','1000',str(input_path),str(prefix)],check=True,capture_output=True,timeout=20)
            ppm=prefix.with_suffix('.ppm').read_bytes();magic,dimensions,maximum,pixels=ppm.split(b'\n',3)
            self.assertEqual(magic,b'P6');self.assertEqual(maximum,b'255');width,height=map(int,dimensions.split())
            image=DecodedStreamObject();image.set_data(pixels);image.update({NameObject('/Type'):NameObject('/XObject'),NameObject('/Subtype'):NameObject('/Image'),NameObject('/Width'):NumberObject(width),NameObject('/Height'):NumberObject(height),NameObject('/ColorSpace'):NameObject('/DeviceRGB'),NameObject('/BitsPerComponent'):NumberObject(8)})
            image=image.flate_encode();scan[NameObject('/Resources')]=DictionaryObject({NameObject('/XObject'):DictionaryObject({NameObject('/Im1'):final._add_object(image)})})
            drawing=DecodedStreamObject();drawing.set_data(b'q 612 0 0 792 0 0 cm /Im1 Do Q');scan[NameObject('/Contents')]=final._add_object(drawing)
        output=io.BytesIO();final.write(output);final.close();pdf=output.getvalue()
        req=Request(self.url+'/api/editorial/pdf/upload',data=pdf,headers={'Origin':self.url,'X-Editorial-Token':self.server.editorial.token,'Content-Type':'application/pdf','X-PDF-Filename':'piloto-isolado.pdf'})
        with urlopen(req,timeout=20) as response:source=json.load(response)['source_id']
        deadline=time.monotonic()+35
        while time.monotonic()<deadline:
            info=self.api('/api/editorial/pdf/'+source)
            if info['state'] in ('completed','completed_with_errors','failed'):break
            time.sleep(.15)
        self.assertEqual(info['state'],'completed')
        self.assertEqual(info['page_count'],2)
        first=self.api('/api/editorial/pdf/'+source+'/pages/1/review');second=self.api('/api/editorial/pdf/'+source+'/pages/2/review')
        self.assertIn('Historical research',first['raw']['raw_text']);self.assertFalse(second['raw']['raw_text'].strip())
        with self.assertRaises(HTTPError) as error:
            self.api('/api/editorial/pdf/incorporation/preview',{'source_id':source,'pages':'2','mode':'create','document_id':'pdf-piloto-isolado','language':'en','project_id':'','metadata':{'title':'PDF piloto isolado','collection_ids':['alpha']}})
        self.assertEqual(error.exception.code,409)
        manual='Manual transcription preserved until OCR candidate adoption.'
        review={'text':manual,'status':'reviewed','printed_label':'2','notes':'Teste isolado','basis':'native'}
        plan=self.api('/api/editorial/pdf/review/preview',{'source_id':source,'page_number':2,'revision':second['revision'],'review':review})
        self.assertEqual(self.api('/api/editorial/pdf/'+source+'/pages/2/review')['revision'],0)
        saved=self.api('/api/editorial/pdf/review/save',{'preview_id':plan['preview_id']})
        cap=self.api('/api/editorial/pdf/capabilities')['ocr']
        if cap['available'] and 'eng' in cap['languages'] and shutil.which('pdftoppm'):
            treatment={'grayscale':True,'contrast':True,'threshold':160,'resize':125,'erosion':0}
            image_cap=self.api('/api/editorial/pdf/capabilities')['image']
            if image_cap['available']:
                preview_image=self.api('/api/editorial/pdf/image/preview',{'source_id':source,'page_number':2,'dpi':150,'recipe':treatment})
                with urlopen(self.url+preview_image['url']) as image_response:
                    image_bytes=image_response.read();self.assertTrue(image_bytes.startswith(b'\x89PNG'));self.assertEqual(hashlib.sha256(image_bytes).hexdigest(),preview_image['derivative_sha256'])
                repeated=self.api('/api/editorial/pdf/image/preview',{'source_id':source,'page_number':2,'dpi':150,'recipe':treatment})
                self.assertEqual(repeated['image_id'],preview_image['image_id']);self.assertEqual(repeated['derivative_sha256'],preview_image['derivative_sha256'])
            ocr=self.api('/api/editorial/pdf/ocr/preview',{'source_id':source,'pages':'2','languages':['eng'],'dpi':150,'psm':6,**({'image_recipe':treatment} if image_cap['available'] else {})})
            if image_cap['available']:self.assertEqual(ocr['recipe']['image_recipe'],treatment)
            job=self.api('/api/editorial/pdf/ocr/start',{'preview_id':ocr['preview_id']})
            deadline=time.monotonic()+40
            while time.monotonic()<deadline:
                overview=self.api('/api/editorial/pdf/'+source+'/review');current=next(j for j in overview['jobs'] if j['id']==job['job_id'])
                if current['state'] in ('completed','failed','interrupted'):break
                time.sleep(.2)
            self.assertEqual(current['state'],'completed',current.get('error'))
            fresh=self.api('/api/editorial/pdf/'+source+'/pages/2/review')
            self.assertEqual(fresh['review']['text'],manual)
            self.assertTrue(fresh['candidates'])
            candidate=fresh['candidates'][0];self.assertIn('historical',candidate['raw_text'].lower())
            if image_cap['available']:self.assertIn('ocr-image-v1',candidate['engine'])
            review={**review,'text':candidate['raw_text'],'basis':candidate['id']}
            plan=self.api('/api/editorial/pdf/review/preview',{'source_id':source,'page_number':2,'revision':fresh['revision'],'review':review})
            saved=self.api('/api/editorial/pdf/review/save',{'preview_id':plan['preview_id']})
            geometry=self.api('/api/editorial/pdf/'+source+'/pages/2/geometry')
            self.assertTrue(geometry['words'])
            for word in geometry['words']:
                x,y,w,h=word['box'];self.assertGreaterEqual(min(x,y,w,h),0);self.assertLessEqual(x+w,1.0001);self.assertLessEqual(y+h,1.0001)
        proposal=self.api('/api/editorial/pdf/incorporation/preview',{'source_id':source,'pages':'2','mode':'create','document_id':'pdf-piloto-isolado','language':'en','project_id':'','metadata':{'title':'PDF piloto isolado','collection_ids':['alpha','alpha/investigacao']}})
        receipt=self.api('/api/editorial/pdf/incorporation/save',{'preview_id':proposal['preview_id'],'confirm_replace':False,'acknowledge_warnings':True})
        self.assertTrue(receipt['saved']);self.assertNotIn('warning',receipt)
        document=self.api('/api/editorial/documents/pdf-piloto-isolado')
        provenance=document['editions'][0]['extra']['pdf_transcription']
        self.assertEqual(provenance['source_id'],source);self.assertEqual(provenance['pages'][0]['page_number'],2);self.assertTrue(provenance['pages'][0]['units'])
        links=self.api('/api/editorial/pdf/links?document=pdf-piloto-isolado')
        self.assertTrue(any(link['source_id']==source and link['pages']==[2] for link in links['items']))
        self.assertEqual(hashlib.sha256(self.server.pdf_sources.file_path(source).read_bytes()).hexdigest(),hashlib.sha256(pdf).hexdigest())
        self.assertEqual(self.api('/api/editorial/pdf/'+source+'/pages/2/review')['raw']['raw_text'],second['raw']['raw_text'])
        self.assertTrue(self.api('/api/editorial/pdf/'+source+'/pages/2/review')['history'])
        canonical_before={str(p.relative_to(self.root)):p.read_bytes() for p in (self.root/'data').rglob('*.json')}
        for mode in ['extract','split']:
            plan=self.api('/api/editorial/pdf/operations/preview',{'source_id':source,'project_id':'','mode':mode,'pages':'2','split_mode':'size','pages_per_part':1,'ranges':''})
            expected=1 if mode=='extract' else 2
            self.assertEqual(len(plan['outputs']),expected)
            operation=self.api('/api/editorial/pdf/operations/start',{'preview_id':plan['preview_id']})
            deadline=time.monotonic()+35
            while time.monotonic()<deadline:
                operation=self.api('/api/editorial/pdf/operations/'+operation['id'])
                if operation['state'] in ('completed','failed','interrupted'):break
                time.sleep(.15)
            self.assertEqual(operation['state'],'completed',operation.get('error'))
            self.assertEqual(operation['registered'],expected)
            for part in operation['outputs']:
                derived=self.api('/api/editorial/pdf/'+part['result_source_id'])
                self.assertEqual(derived['page_count'],len(part['pages']))
                self.assertTrue(any(p['parent_source_id']==source and p['pages']==part['pages'] for p in derived['provenance']))
        self.assertEqual(canonical_before,{str(p.relative_to(self.root)):p.read_bytes() for p in (self.root/'data').rglob('*.json')})
        self.assertEqual(self.server.pdf_sources.file_path(source).read_bytes(),pdf)

