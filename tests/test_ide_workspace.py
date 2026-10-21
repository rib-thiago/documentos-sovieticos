"""Verificações do protótipo IDE. Sem gravar no acervo ou iniciar workers."""
import json
from pathlib import Path
import tempfile
import threading
import unittest
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from types import SimpleNamespace
from urllib.parse import urljoin
from urllib.request import urlopen
from urllib.error import HTTPError
from backend.server import handler_for

ROOT=Path(__file__).resolve().parents[1]
try:
    import quickjs
except ImportError:
    quickjs=None

class IDs(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.buttons=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append((tag,attrs['id']))
        if tag=='button' and any(k in attrs for k in ('data-section','data-bottom')):self.buttons.append(attrs)

@unittest.skipUnless(quickjs,'QuickJS opcional para verificar interações sem navegador')
class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.js=quickjs.Context();self.js.add_callable('resolveURL',lambda path,base:urljoin(base,path));self.js.eval((ROOT/'tests/fixtures/ide-dom.js').read_text())
        parser=IDs();parser.feed((ROOT/'prototipo/ide/index.html').read_text())
        for tag,id_ in parser.ids:self.js.eval(f"document.body.append(Object.assign(new Element({json.dumps(tag)}),{{id:{json.dumps(id_)}}}));")
        for attrs in parser.buttons:self.js.eval('var b=new Element("button");'+''.join(f'b.setAttribute({json.dumps(k)},{json.dumps(v)});' for k,v in attrs.items())+'document.body.append(b);')
        manifest={'collections':[{'id':'grouped','title_pt':'Coleção com IDs','document_ids':['doc1'],'subcollections':[{'id':'sub','title_pt':'Subcoleção','document_ids':['doc1']}]},{'id':'legacy','title_pt':'Legado','documents':[{'id':'doc2','title_pt':'Documento dois','languages':[{'code':'ru','file':'originais/two.ru.md'}]}]}],'documents':[{'id':'doc1','title_pt':'Documento um','languages':[{'code':'pt','file':'originais/one.pt.md'},{'code':'ru','file':'originais/one.ru.md'}]}]}
        self.js.eval('var fixtureManifest='+json.dumps(manifest)+';')
        code=(ROOT/'prototipo/ide/workspace.js').read_text().replace('  init();','  globalThis.testIDE={init,open,split,moveTab,tool,groups,views,models,loadModel,currentTab,renderGroups,switchProject,editorFor,refreshCatalogue,openArea,searchDocuments,getProject:()=>project}; init();')
        self.js.eval(code);self.flush()
    def flush(self):
        for _ in range(500):
            if not self.js.execute_pending_job():break
    def run_js(self,code):self.js.eval(code);self.flush()
    def test_full_manifest_and_subcollections(self):
        self.assertIn('Backend local disponível',self.js.eval("document.getElementById('connection').textContent"))
        self.assertEqual('',self.js.eval('testIDE.getProject()'))
        self.run_js("document.getElementById('sidebar-content').querySelector('details').open=true;document.getElementById('sidebar-content').querySelector('details').ontoggle();")
        self.assertIn('Subcoleção',self.js.eval("document.getElementById('sidebar-content').textContent"))
        self.run_js("testIDE.open('text','doc1');testIDE.open('text','doc2');")
        self.assertEqual(2,self.js.eval('testIDE.groups[0].tabs.length'))
    def test_tabs_preserve_tool_host(self):
        self.run_js("var t=testIDE.open('tool',null,null,0,{label:'Editor',route:'markdown/doc1:pt'});var host=testIDE.views.get(t.key);var iframe=host.querySelector('iframe');var mounts=iframe.mounts;testIDE.open('text','doc1');testIDE.open('tool',null,null,0,{label:'Editor',route:'markdown/doc1:pt'});")
        self.assertTrue(self.js.eval('host===testIDE.views.get(t.key)&&iframe===host.querySelector("iframe")&&iframe.mounts===mounts'))
    def test_draft_recovery_and_transfer(self):
        self.run_js("var t=testIDE.open('markdown','doc1','pt');")
        self.run_js("var input=testIDE.views.get(t.key).querySelector('textarea');input.value='Tradução revista';input.oninput();")
        self.assertIn('Tradução revista',self.js.eval("sessionStorage.getItem('discoveryIDE:draft:acervo|doc1|pt')"))
        self.run_js('testIDE.editorFor(t);')
        self.assertEqual('Tradução revista',self.js.eval("JSON.parse(sessionStorage.getItem('workspaceDraft:v1:a-test-draft-token')).content"))
        self.assertIn('?rascunho=',self.js.eval('testIDE.currentTab().route'))
        self.assertFalse(self.js.eval('requests.some(p=>p.includes("/save"))'))
    def test_group_movement_keeps_document_and_language(self):
        self.run_js("var t=testIDE.open('markdown','doc1','ru');testIDE.split('down');testIDE.moveTab(t.key,1);")
        self.assertEqual('doc1',self.js.eval('testIDE.groups[1].tabs[0].id'))
        self.assertEqual('ru',self.js.eval('testIDE.groups[1].tabs[0].lang'))
        self.assertEqual(0,self.js.eval('testIDE.groups[0].tabs.length'))
    def test_private_context_loads_private_text(self):
        self.run_js("testIDE.switchProject('private');testIDE.open('markdown','doc1','pt');")
        self.assertEqual('Texto privado',self.js.eval('testIDE.views.get(testIDE.currentTab().key).querySelector("textarea").value'))
        self.assertTrue(self.js.eval('requests.some(p=>p.includes("workspace/edition?"))'))
        self.assertEqual('private',self.js.eval('testIDE.currentTab().project'))
    def test_declining_tool_move_preserves_form(self):
        self.run_js("var t=testIDE.open('tool',null,null,0,{label:'Editor',route:'markdown/doc1:pt'});testIDE.split();confirmResult=false;testIDE.moveTab(t.key,1);")
        self.assertEqual(1,self.js.eval('testIDE.groups[0].tabs.length'))
        self.assertEqual(0,self.js.eval('testIDE.groups[1].tabs.length'))

    def test_global_catalog_tool_explicitly_targets_acervo(self):
        self.run_js("testIDE.switchProject('private');testIDE.tool('catalogo','Catálogo');")
        self.assertEqual('',self.js.eval('testIDE.currentTab().project'))
        self.assertEqual('catalogo',self.js.eval('testIDE.currentTab().route'))
        self.assertIn('Acervo',self.js.eval('testIDE.currentTab().label'))
    def test_changed_source_preserves_recovery(self):
        self.run_js("sessionStorage.setItem('discoveryIDE:draft:acervo|doc1|pt',JSON.stringify({baseline:'Fonte antiga',text:'Meu trabalho anterior'}));testIDE.open('markdown','doc1','pt');")
        self.assertEqual('Fonte em português',self.js.eval('testIDE.views.get(testIDE.currentTab().key).querySelector("textarea").value'))
        self.assertEqual('Meu trabalho anterior',self.js.eval("JSON.parse(sessionStorage.getItem('discoveryIDE:recovery:acervo|doc1|pt')).text"))
    def test_layout_changes_keep_same_tool_frame(self):
        self.run_js("var t=testIDE.open('tool',null,null,0,{label:'PDF',route:'pdf'});var frame=testIDE.views.get(t.key).querySelector('iframe');var count=frame.mounts;testIDE.split('right');testIDE.split('down');testIDE.renderGroups();")
        self.assertTrue(self.js.eval('frame===testIDE.views.get(t.key).querySelector("iframe")&&frame.mounts===count'))

    def test_task_areas_are_independent_tabs(self):
        self.run_js("testIDE.openArea('search');testIDE.openArea('tools');")
        self.assertEqual(2,self.js.eval('testIDE.groups[0].tabs.length'))
        self.assertEqual('tools',self.js.eval('testIDE.currentTab().area'))
    def test_combined_search_filters_and_project_scope(self):
        self.assertEqual(1,self.js.eval("testIDE.searchDocuments({collection:'grouped',subcollection:'sub',language:'pt',q:'um'}).length"))
        self.assertEqual(0,self.js.eval("testIDE.searchDocuments({collection:'legacy',language:'pt'}).length"))
        self.run_js("testIDE.switchProject('private');testIDE.openArea('search');")
        self.assertEqual(1,self.js.eval("testIDE.searchDocuments({}).length"))
    def test_pdf_sections_preserve_editor_and_confirmation_state(self):
        code=(ROOT/'assets/workspace-pdf-layout.js').read_text().replace('return{start,switchPane};','return{start,switchPane,decorate};').replace('window.archiveWorkspacePDFLayout.start();','')
        self.js.eval(code)
        self.run_js("""
          var root=new Element('main');root.setAttribute('data-workspace-source-root','source-1');document.body.append(root);
          var grid=new Element('div');grid.setAttribute('data-workspace-source','source-1');grid.setAttribute('data-workspace-zone','review');root.append(grid);
          var form=new Element('form');form.className='pdf-review-form';form.setAttribute('data-workspace-review-pane','text');grid.append(form);
          var draft=new Element('textarea');draft.value='Minha correção não salva';form.append(draft);
          var preview=new Element('section');preview.hidden=true;form.append(preview);
          var ocr=new Element('section');ocr.setAttribute('data-workspace-zone','ocr');root.append(ocr);
          archiveWorkspacePDFLayout.decorate(root);
          root.querySelectorAll('button').find(b=>b.dataset.value==='ocr').click();
          root.querySelectorAll('button').find(b=>b.dataset.value==='review').click();
          archiveWorkspacePDFLayout.decorate(root);
        """)
        self.assertEqual('Minha correção não salva',self.js.eval('draft.value'))
        self.assertTrue(self.js.eval('draft.parentElement===form&&preview.hidden'))
        self.assertEqual(1,self.js.eval("root.querySelectorAll('.workspace-source-steps').length"))
        self.assertFalse(self.js.eval("grid.classList.contains('workspace-pane-inactive')"))

    def test_pdf_comparison_keeps_facsimile_and_editor_mounted(self):
        code=(ROOT/'assets/workspace-pdf-layout.js').read_text().replace('return{start,switchPane};','return{start,switchPane,decorate};').replace('window.archiveWorkspacePDFLayout.start();','')
        self.js.eval(code)
        self.run_js("""
          var root=new Element('main');root.setAttribute('data-workspace-source-root','source-2');document.body.append(root);
          var grid=new Element('div');grid.setAttribute('data-workspace-source','source-2');grid.setAttribute('data-workspace-zone','review');root.append(grid);
          var image=new Element('iframe');image.className='pdf-facsimile';grid.append(image);
          var editor=new Element('section');grid.append(editor);var form=new Element('form');form.className='pdf-review-form';form.setAttribute('data-workspace-review-pane','text');editor.append(form);
          var text=new Element('textarea');text.value='Rascunho da página';form.append(text);
          var mounts=image.mounts;archiveWorkspacePDFLayout.decorate(root);
          root.querySelectorAll('button').find(b=>b.dataset.value==='source').click();
          root.querySelectorAll('button').find(b=>b.dataset.value==='text'&&b.textContent==='Transcrição').click();
          root.querySelectorAll('button').find(b=>b.dataset.value==='compare').click();
        """)
        self.assertEqual('compare',self.js.eval("grid.getAttribute('data-workspace-page-mode')"))
        self.assertTrue(self.js.eval('image.parentElement===grid&&image.mounts===mounts&&text.value==="Rascunho da página"'))
        self.assertEqual('58%',self.js.eval("grid.style.getPropertyValue('--workspace-image-ratio')"))

    def test_pdf_height_manual_keyboard_and_automatic(self):
        code=(ROOT/'assets/workspace-pdf-layout.js').read_text().replace('return{start,switchPane};','return{start,switchPane,decorate};').replace('window.archiveWorkspacePDFLayout.start();','')
        self.js.eval(code)
        self.run_js("""
          var root=new Element('main');root.setAttribute('data-workspace-source-root','height-source');document.body.append(root);
          var grid=new Element('div');grid.setAttribute('data-workspace-source','height-source');grid.setAttribute('data-workspace-zone','review');root.append(grid);
          var image=new Element('iframe');image.className='pdf-facsimile';grid.append(image);grid.append(new Element('section'));
          archiveWorkspacePDFLayout.decorate(root);
          var height=root.querySelector('.workspace-page-height-label').querySelector('input');height.value='760';height.onchange();
        """)
        self.assertEqual('760px',self.js.eval("grid.style.getPropertyValue('--workspace-page-height')"))
        self.run_js("root.querySelector('.workspace-page-height-handle').onkeydown({key:'ArrowDown',preventDefault(){}});")
        self.assertEqual('780',self.js.eval("sessionStorage.getItem('workspacePDFHeight:v1')"))
        self.run_js("root.querySelectorAll('button').find(b=>b.textContent==='Automática').click();")
        self.assertEqual('null',self.js.eval("sessionStorage.getItem('workspacePDFHeight:v1')"))

class PrototypeHTTPTests(unittest.TestCase):
    def test_routes_are_allowlisted_without_exposing_work_files(self):
        with tempfile.TemporaryDirectory(prefix='ide-http-') as temp:
            root=Path(temp)
            for relative in ['prototipo/ide/index.html','prototipo/ide/workspace.css','prototipo/ide/workspace.js']:
                target=root/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/relative).read_bytes())
            secret=root/'prototipo/ide/private.txt';secret.write_text('Not published')
            server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(SimpleNamespace(root=root),None))
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                base=f'http://127.0.0.1:{server.server_port}'
                for path in ['/prototipo/ide','/prototipo/ide/','/prototipo/ide/workspace.css','/prototipo/ide/workspace.js']:
                    with urlopen(base+path) as response:self.assertEqual(200,response.status)
                with self.assertRaises(HTTPError) as denied:urlopen(base+'/prototipo/ide/private.txt')
                self.assertEqual(404,denied.exception.code)
            finally:server.shutdown();thread.join();server.server_close()

if __name__=='__main__':unittest.main()
