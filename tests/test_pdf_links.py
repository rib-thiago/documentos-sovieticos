"""Vínculos e passagens em acervo temporário, com isolamento de projeto."""
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from backend import catalog as model
from backend.pdf_sources import PDFSources
from backend.research_projects import ResearchProjects
from backend.workspace_editions import WorkspaceEditions
from backend.pdf_links import sha
from backend.editorial import EditorialError
from test_backend import fixture
try:
    from pypdf import PdfWriter
except ImportError:
    PdfWriter = None


@unittest.skipUnless(PdfWriter, 'Requer pypdf opcional')
class LinksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pdf-links-test-')
        self.root = Path(self.temp.name)
        fixture(self.root); model.migrate(self.root)
        self.repository = SimpleNamespace(root=self.root,catalog=model.load(self.root))
        self.sources = PDFSources(self.root,start_worker=False)
        self.projects = ResearchProjects(self.root,self.sources)
        self.workspace = WorkspaceEditions(self.projects)
        self.links = self.sources.links
        self.links.projects,self.links.workspace = self.projects,self.workspace
        writer = PdfWriter()
        for _ in range(3):writer.add_blank_page(width=200,height=300)
        stream = io.BytesIO();writer.write(stream);writer.close()
        self.id = self.sources.upload('fonte.pdf',stream.getvalue())['source_id']
        with self.sources.db() as db:db.execute('UPDATE pdf_sources SET page_count=3 WHERE id=?',(self.id,))

    def tearDown(self):
        self.sources.close();self.temp.cleanup()

    def create(self, project=''):
        return self.links.preview(self.repository,{'action':'create','document_id':'showtrials-1','project_id':project,'source_id':self.id,'pages':'1-3','notes':'Correspondência conferida'})

    def save(self, plan):
        return self.links.save(self.repository,{'preview_id':plan['preview_id']})

    def anchor(self, link, quote='Tradução de Nikolaev. passagem exclusiva.'):
        body = self.links.edition(self.repository,link,'pt')
        start = body.index(quote)
        payload = {'language':'pt','body_sha256':sha(body),'quote':quote,'start':len(body[:start].encode('utf-16-le'))//2,'end':len(body[:start+len(quote)].encode('utf-16-le'))//2,'page_number':2,'notes':'Correspondência manual'}
        return self.links.preview(self.repository,{'action':'anchor','id':link['id'],'revision':link['revision'],'anchor':payload})

    def project(self, title='Projeto', source=True):
        plan = self.projects.preview({'project':{'title':title,'description':'','collection_id':'alpha','document_ids':['showtrials-1'],'source_ids':[self.id] if source else [],'archived':False}},self.repository.catalog)
        return self.projects.save({'preview_id':plan['preview_id']},self.repository.catalog)['project_id']

    def hashes(self):
        return {str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*self.root.glob('originais/*'),*self.root.glob('data/catalog/*'),self.root/'data/manifest.json']}

    def test_preview_save_and_history_preserve_catalog(self):
        before = self.hashes();plan = self.create()
        self.assertEqual(self.links.listing(self.repository,{'document':'showtrials-1'})['items'],[])
        link = self.save(plan)
        self.assertEqual(link['revision'],1)
        history = self.links.history(self.repository,link['id'])['items']
        self.assertFalse(history[0]['before_state']['active'])
        self.assertEqual(before,self.hashes())

    def test_duplicate_creation_and_consumed_preview_rejected(self):
        a,b = self.create(),self.create();self.save(a)
        for plan in (a,b):
            with self.assertRaises(EditorialError):self.save(plan)
        with self.assertRaises(EditorialError):self.create()

    def test_update_conflict_and_restoration_are_revisions(self):
        link = self.save(self.create())
        a = self.links.preview(self.repository,{'action':'update','id':link['id'],'revision':1,'pages':'2-3','notes':'Nova nota','active':False})
        b = self.links.preview(self.repository,{'action':'update','id':link['id'],'revision':1,'pages':'1','notes':'Concorrência','active':True})
        self.save(a)
        with self.assertRaises(EditorialError):self.save(b)
        record = self.links.history(self.repository,link['id'])['items'][0]
        restored = self.save(self.links.preview(self.repository,{'action':'restore','id':link['id'],'revision':2,'history_id':record['id']}))
        self.assertEqual(restored['revision'],3);self.assertEqual(restored['pages'],[1,2,3]);self.assertTrue(restored['active'])

    def test_anchor_exact_text_and_page(self):
        link = self.save(self.create());saved = self.save(self.anchor(link))
        anchor = saved['anchors'][0]
        self.assertEqual(anchor['page_number'],2)
        self.assertEqual(anchor['quote_sha256'],sha(anchor['quote']))
        item = self.links.listing(self.repository,{'document':'showtrials-1'})['items'][0]
        self.assertFalse(item['anchors'][0]['stale_text']);self.assertFalse(item['anchors'][0]['stale_page'])
        with self.assertRaises(EditorialError):
            self.links.preview(self.repository,{'action':'update','id':saved['id'],'revision':2,'pages':'1','notes':'','active':True})

    def test_text_change_after_preview_blocks_save(self):
        link = self.save(self.create());plan = self.anchor(link)
        edition = next(e for e in self.repository.catalog['editions'] if e['id']=='showtrials-1:pt')
        path = self.root/edition['file'];path.write_text(path.read_text()+'\nNova passagem')
        edition['sha256'] = model.sha256(path.read_bytes())
        with self.assertRaises(EditorialError):self.save(plan)

    def test_changed_text_is_marked_stale_without_relocation(self):
        saved = self.save(self.anchor(self.save(self.create())))
        edition = next(e for e in self.repository.catalog['editions'] if e['id']=='showtrials-1:pt')
        path=self.root/edition['file'];path.write_text('Texto modificado\n'+path.read_text());edition['sha256']=model.sha256(path.read_bytes())
        item=self.links.listing(self.repository,{'document':'showtrials-1'})['items'][0]
        self.assertTrue(item['anchors'][0]['stale_text'])
        self.assertEqual(item['anchors'][0]['start'],saved['anchors'][0]['start'])

    def test_page_revision_change_is_marked_stale(self):
        self.save(self.anchor(self.save(self.create())))
        with self.sources.db() as db:db.execute('INSERT INTO pdf_page_reviews VALUES(?,?,?,?,?)',(self.id,2,1,json.dumps({'printed_label':'x'}),'2026'))
        item=self.links.listing(self.repository,{'document':'showtrials-1'})['items'][0]
        self.assertTrue(item['anchors'][0]['stale_page'])

    def test_project_links_do_not_leak_between_contexts(self):
        project=self.project();other=self.project('Outro')
        global_link=self.save(self.create());private_link=self.save(self.create(project))
        self.assertEqual([i['id'] for i in self.links.listing(self.repository,{'document':'showtrials-1'})['items']],[global_link['id']])
        self.assertEqual([i['id'] for i in self.links.listing(self.repository,{'document':'showtrials-1','project':project})['items']],[private_link['id']])
        self.assertEqual(self.links.listing(self.repository,{'document':'showtrials-1','project':other})['items'],[])

    def test_project_requires_source_membership(self):
        project=self.project(source=False)
        with self.assertRaises(EditorialError):self.create(project)

    def test_history_restoration_of_creation_deactivates(self):
        link=self.save(self.create());history=self.links.history(self.repository,link['id'])['items'][0]
        restored=self.save(self.links.preview(self.repository,{'action':'restore','id':link['id'],'revision':1,'history_id':history['id']}))
        self.assertFalse(restored['active'])
        self.assertTrue(self.sources.file_path(self.id).exists())

    def test_invalid_page_and_quote_rejected(self):
        with self.assertRaises(EditorialError):
            self.links.preview(self.repository,{'action':'create','document_id':'showtrials-1','project_id':'','source_id':self.id,'pages':'4','notes':''})
        link=self.save(self.create());plan=self.anchor(link)
        # Saved preview is valid; an independently malformed anchor must fail.
        body=self.links.edition(self.repository,link,'pt')
        with self.assertRaises(EditorialError):
            self.links.preview(self.repository,{'action':'anchor','id':link['id'],'revision':1,'anchor':{'language':'pt','body_sha256':sha(body),'quote':'Texto inventado','start':0,'end':5,'page_number':2,'notes':''}})

    def test_remove_anchor_is_recoverable(self):
        link=self.save(self.anchor(self.save(self.create())))
        removed=self.save(self.links.preview(self.repository,{'action':'remove_anchor','id':link['id'],'revision':link['revision'],'anchor_id':link['anchors'][0]['id']}))
        self.assertEqual(removed['anchors'],[])
        h=self.links.history(self.repository,link['id'])['items'][0]
        restored=self.save(self.links.preview(self.repository,{'action':'restore','id':link['id'],'revision':removed['revision'],'history_id':h['id']}))
        self.assertEqual(restored['anchors'],link['anchors'])

    def test_utf16_offsets_after_non_bmp_character(self):
        edition=next(e for e in self.repository.catalog['editions'] if e['id']=='showtrials-1:pt')
        path=self.root/edition['file'];path.write_text('Nota 📝\n\n'+path.read_text());edition['sha256']=model.sha256(path.read_bytes())
        link=self.save(self.create());saved=self.save(self.anchor(link))
        anchor=saved['anchors'][0];body=self.links.edition(self.repository,link,'pt')
        self.assertEqual(anchor['start'],body.index(anchor['quote'])+1)
        self.assertEqual(body.encode('utf-16-le')[anchor['start']*2:anchor['end']*2].decode('utf-16-le'),anchor['quote'])

    def test_private_edition_change_invalidates_only_private_association(self):
        project=self.project();global_link=self.save(self.anchor(self.save(self.create())))
        private_link=self.save(self.anchor(self.save(self.create(project))))
        current=self.workspace.edition(self.repository,project,'showtrials-1:pt')
        plan=self.workspace.preview(self.repository,{'project_id':project,'edition_id':'showtrials-1:pt','revision':current['revision'],'content_sha256':current['content_sha256'],'content':current['content']+'\nNota privada.'})
        self.workspace.save(self.repository,{'preview_id':plan['preview_id']})
        canonical=self.links.listing(self.repository,{'document':'showtrials-1'})['items'][0]
        private=self.links.listing(self.repository,{'document':'showtrials-1','project':project})['items'][0]
        self.assertFalse(canonical['anchors'][0]['stale_text'])
        self.assertTrue(private['anchors'][0]['stale_text'])
