"""Fluxo completo isolado: alinhamento, incorporação e projeção estática recuperável."""
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from backend import catalog as model
from backend.database import Repository,ensure_index
from backend.editorial import Editorial,EditorialError,QUEUE
from backend.pdf_sources import PDFSources
from backend.pdf_incorporation import PDFIncorporation
from backend.pdf_publication import PDFPublication
from backend.research_projects import ResearchProjects
from backend.workspace_editions import WorkspaceEditions
from test_backend import fixture
try:
 from pypdf import PdfReader,PdfWriter
except ImportError:PdfWriter=None


@unittest.skipUnless(PdfWriter,'Requer pypdf opcional')
class PipelineTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='pdf-pipeline-test-');self.root=Path(self.tmp.name);fixture(self.root);model.migrate(self.root);catalog=model.load(self.root)
  path=self.root/QUEUE;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('chave,prioridade,status,id,problema,dificuldade,dificuldade_encontrada,acao_sugerida,arquivo_markdown,url_teste,colecoes,titulo_ru,fonte,trechos\n')
  self.editorial=Editorial(self.root);db=self.root/'.local/catalog.sqlite3';info=ensure_index(self.root,db,catalog);self.repository=Repository(self.root,db,catalog,info)
  self.sources=PDFSources(self.root,start_worker=False);self.projects=ResearchProjects(self.root,self.sources);self.workspace=WorkspaceEditions(self.projects);self.sources.links.projects=self.projects;self.sources.links.workspace=self.workspace
  self.inc=PDFIncorporation(self.sources,self.editorial,self.workspace);self.pub=PDFPublication(self.sources,self.editorial)
  writer=PdfWriter()
  for number in range(3):writer.add_blank_page(width=200+number,height=300)
  stream=io.BytesIO();writer.write(stream);writer.close();self.pdf=stream.getvalue();self.id=self.sources.upload('fonte.pdf',self.pdf)['source_id']
  with self.sources.db() as db:
   db.execute("UPDATE pdf_sources SET page_count=3,state='completed' WHERE id=?",(self.id,))
   for number in (1,2,3):
    raw='Alpha beta gamma.\n\nSecond paragraph.' if number==1 else 'Texto da página '+str(number)
    start=raw.find('\n\n');ranges=[(0,start),(start+2,len(raw))] if start>=0 else [(0,len(raw))]
    units=[{'id':f'{self.id}-p{number}-u{i}','start':a,'end':b,'text_sha256':model.sha256(raw[a:b].encode())} for i,(a,b) in enumerate(ranges)]
    db.execute('INSERT INTO pdf_pages VALUES(?,?,?,?,?,?,?,?,?,?,?)',(f'{self.id}-p{number}',self.id,number,None,raw,model.sha256(raw.encode()),'text','fixture',None,json.dumps(units),'fixture'))
  self.review(1);self.review(2)

 def tearDown(self):self.sources.close();self.editorial.close();self.tmp.cleanup()
 def review(self,number):
  page=self.sources.review.page(self.id,number);data={k:page['review'][k] for k in ('text','status','printed_label','notes','basis')};data.update(status='reviewed',printed_label=str(10+number),notes='NOTA PRIVADA')
  plan=self.sources.review.preview({'source_id':self.id,'page_number':number,'revision':page['revision'],'review':data});return self.sources.review.save({'preview_id':plan['preview_id']})
 def structural(self,action,**extra):
  page=self.sources.review.page(self.id,1);unit=page['review']['units'][0]
  return self.sources.alignment.preview({'source_id':self.id,'page_number':1,'revision':page['revision'],'action':action,'unit_id':unit['id'],**extra})
 def save_review(self,plan):return self.sources.review.save({'preview_id':plan['preview_id']})
 def incorporation(self,**extra):
  args={'source_id':self.id,'pages':'1-2','mode':'create','project_id':'','document_id':'pdf-pilot','language':'ru','metadata':{'title':'Piloto PDF','title_pt':'Piloto PDF','collection_ids':['alpha']}};args.update(extra);return self.inc.preview(self.repository,args)
 def incorporate(self,**extra):
  plan=self.incorporation(**extra);return self.inc.save(self.repository,{'preview_id':plan['preview_id'],'confirm_replace':True,'acknowledge_warnings':True})
 def canonical_hashes(self):return {str(p.relative_to(self.root)):model.sha256(p.read_bytes()) for p in [*self.root.glob('originais/*'),*self.root.glob('data/catalog/*'),self.root/'data/manifest.json'] if p.is_file()}
 def link(self):
  return next(i for i in self.sources.links.listing(self.repository,{'document':'pdf-pilot'})['items'])
 def publish(self,**extra):
  link=self.link();args={'action':'publish','link_ids':[link['id']],'include_transcription':True};args.update(extra);return self.pub.preview(self.repository,args)

 def test_split_merge_preserve_text_and_lineage(self):
  page=self.sources.review.page(self.id,1);old=page['review']['units'][0]['id'];split=self.save_review(self.structural('split',offset=6))
  self.assertEqual(split['review']['text'],page['review']['text']);self.assertEqual(split['review']['units'][0]['parents'],[old]);self.assertEqual(len(split['review']['units']),3)
  merged=self.save_review(self.structural('merge'));self.assertEqual(merged['review']['text'],page['review']['text']);self.assertEqual(len(merged['review']['units']),2);self.assertEqual(len(merged['review']['units'][0]['parents']),2)
 def test_boxes_preserve_id_and_metadata_only_edit(self):
  before=self.sources.review.page(self.id,1);saved=self.save_review(self.structural('boxes',boxes=[[.1,.2,.3,.1]]));self.assertEqual(before['review']['units'][0]['id'],saved['review']['units'][0]['id'])
  after=self.review(1);self.assertEqual(after['review']['units'][0]['boxes'],[[.1,.2,.3,.1]])
 def test_invalid_geometry_and_stale_preview_blocked(self):
  for boxes in ([[0,0,2,1]],[[0,0,float('nan'),.1]],[[-.1,0,.2,.2]]):
   with self.assertRaises(EditorialError):self.structural('boxes',boxes=boxes)
  old=self.structural('merge');self.review(1)
  with self.assertRaises(EditorialError):self.save_review(old)
 def test_history_restores_retired_unit(self):
  before=self.sources.review.page(self.id,1);saved=self.save_review(self.structural('split',offset=6));h=saved['history'][0]
  plan=self.sources.review.preview({'source_id':self.id,'page_number':1,'revision':saved['revision'],'history_id':h['id']});restored=self.save_review(plan)
  self.assertEqual(restored['review']['units'],before['review']['units'])
 def test_incorporation_preview_does_not_write(self):
  before=self.canonical_hashes();plan=self.incorporation();self.assertIn('Alpha',plan['content']);self.assertEqual(self.canonical_hashes(),before)
 def test_create_updates_catalog_manifest_and_search(self):
  result=self.incorporate();edition=self.repository.edition('pdf-pilot:ru');self.assertTrue(edition['extra']['pdf_transcription']['pages']);self.assertIn('pdf-pilot',self.repository.documents({'q':'Alpha'})['items'][0]['id'])
  self.assertEqual(model.export_manifest(self.repository.catalog),json.loads((self.root/'data/manifest.json').read_text()));self.assertEqual(self.link()['pages'],[1,2]);self.assertTrue(result['saved'])
 def test_pending_pages_rejected(self):
  with self.assertRaises(EditorialError):self.incorporation(pages='3')
 def test_review_change_after_preview_rejected(self):
  plan=self.incorporation();self.review(1)
  with self.assertRaises(EditorialError):self.inc.save(self.repository,{'preview_id':plan['preview_id'],'confirm_replace':True,'acknowledge_warnings':True})
 def test_replacement_requires_explicit_confirmation(self):
  plan=self.incorporation(mode='edition',document_id='showtrials-1',language='ru')
  with self.assertRaises(EditorialError):self.inc.save(self.repository,{'preview_id':plan['preview_id']})
  saved=self.inc.save(self.repository,{'preview_id':plan['preview_id'],'confirm_replace':True,'acknowledge_warnings':True});self.assertTrue(saved['saved']);self.assertTrue(list(self.editorial.history_dir.glob('*.json.gz')))
 def project(self):
  p=self.projects.preview({'project':{'title':'Privado','description':'','collection_id':'alpha','document_ids':['showtrials-1'],'source_ids':[self.id],'archived':False}},self.repository.catalog);return self.projects.save({'preview_id':p['preview_id']},self.repository.catalog)['project_id']
 def test_private_incorporation_preserves_canonical(self):
  project=self.project();before=self.canonical_hashes();self.incorporate(mode='project',document_id='showtrials-1',project_id=project)
  self.assertEqual(self.canonical_hashes(),before);self.assertIn('Alpha',self.workspace.edition(self.repository,project,'showtrials-1:ru')['content'])
 def test_private_links_cannot_publish(self):
  project=self.project();self.incorporate(mode='project',document_id='showtrials-1',project_id=project)
  link=self.sources.links.listing(self.repository,{'document':'showtrials-1','project':project})['items'][0]
  with self.assertRaises(EditorialError):self.pub.preview(self.repository,{'action':'publish','link_ids':[link['id']],'include_transcription':True})
 def test_failed_binding_can_be_finished_without_rewriting_text(self):
  with patch.object(self.sources.links,'preview',side_effect=EditorialError('falha simulada')):result=self.incorporate()
  self.assertIn('warning',result);before=self.canonical_hashes();done=self.inc.finish(self.repository,result['receipt_id']);self.assertTrue(done['completed']);self.assertEqual(before,self.canonical_hashes())
 def test_publication_prepare_is_private_then_apply_is_static(self):
  self.incorporate();before=self.canonical_hashes();plan=self.publish();self.assertFalse(self.pub.index.exists());self.assertFalse((self.root/'assets/facsimiles').exists())
  preview=self.pub.preview_pdf(plan['release_id'],self.link()['id']);self.assertEqual(len(PdfReader(preview).pages),2)
  self.pub.apply(self.repository,{'release_id':plan['release_id'],'confirm':True});index=self.pub.state();self.assertEqual(len(index['links']),1)
  payload=json.dumps(index,ensure_ascii=False);self.assertNotIn('NOTA PRIVADA',payload);self.assertNotIn('.local/',payload);self.assertNotIn('project_id',payload)
  for relative in self.pub.paths(index):self.assertTrue((self.root/relative).is_file())
  self.assertEqual(self.canonical_hashes(),before);self.assertEqual(self.sources.file_path(self.id).read_bytes(),self.pdf)
 def test_publication_rejects_changes_after_prepare(self):
  self.incorporate();plan=self.publish();self.review(1)
  with self.assertRaises(EditorialError):self.pub.apply(self.repository,{'release_id':plan['release_id'],'confirm':True})
 def test_withdraw_restore_and_recovery(self):
  self.incorporate();plan=self.publish();first=self.pub.apply(self.repository,{'release_id':plan['release_id'],'confirm':True});old=self.pub.state();paths=self.pub.paths(old)
  withdrawal=self.pub.preview(self.repository,{'action':'withdraw','link_ids':[self.link()['id']]});removed=self.pub.apply(self.repository,{'release_id':withdrawal['release_id'],'confirm':True});self.assertEqual(self.pub.state()['links'],[])
  self.assertTrue(all(not (self.root/p).exists() for p in paths))
  restore=self.pub.preview(self.repository,{'action':'restore','history_id':removed['history_id']});self.pub.apply(self.repository,{'release_id':restore['release_id'],'confirm':True});self.assertEqual(self.pub.state(),old)
  # Simulate interrupted application; initialization restores the recorded before-state.
  target={'schema_version':1,'links':[]};model.atomic_write(self.pub.pending,model.json_bytes({'before':old,'after':target}));model.atomic_write(self.pub.index,model.json_bytes(target))
  reopened=PDFPublication(self.sources,self.editorial);self.assertEqual(reopened.state(),old)
 def test_unreviewed_transcription_can_be_omitted(self):
  self.incorporate();link=self.link();p=self.sources.links.preview(self.repository,{'action':'update','id':link['id'],'revision':link['revision'],'pages':'1-3','notes':'','active':True});self.sources.links.save(self.repository,{'preview_id':p['preview_id']})
  with self.assertRaises(EditorialError):self.publish()
  plan=self.publish(include_transcription=False);self.pub.apply(self.repository,{'release_id':plan['release_id'],'confirm':True});self.assertEqual(self.pub.state()['links'][0]['page_snapshots'][0]['review']['text'],'')
 @unittest.skipUnless(shutil.which('pdftoppm'),'Poppler opcional ausente')
 def test_geometry_images_survive_static_publication(self):
  saved=self.save_review(self.structural('boxes',boxes=[[.1,.1,.2,.2]]));image=self.sources.page_image(self.id,1);self.assertTrue(image.read_bytes().startswith(b'\x89PNG'))
  self.incorporate();plan=self.publish();self.pub.apply(self.repository,{'release_id':plan['release_id'],'confirm':True});self.assertTrue(self.pub.state()['links'][0]['image_urls']['1'].endswith('.png'))

 def test_editorial_history_restores_incorporation(self):
  result=self.incorporate();history=result['result']['history_id']
  plan=self.editorial.preview(self.repository,{'revision':self.editorial.revision(),'restore_id':history})
  restored=self.editorial.save(self.repository,{'preview_id':plan['preview_id'],'acknowledge_warnings':True})
  self.assertFalse(restored['document_exists']);self.assertIsNone(self.repository.document('pdf-pilot'));self.assertEqual(self.repository.documents({'q':'Alpha'})['items'],[])
  self.assertEqual(self.sources.file_path(self.id).read_bytes(),self.pdf);self.assertEqual(self.sources.review.page(self.id,1)['review']['status'],'reviewed')
 def test_publication_failure_rolls_back_and_can_retry(self):
  self.incorporate();plan=self.publish();real=model.atomic_write;failed=[False]
  def fail_once(path,data):
   real(path,data)
   if Path(path)==self.pub.index and not failed[0]:failed[0]=True;raise OSError('Falha simulada após escrever o índice')
  with patch('backend.pdf_publication.model.atomic_write',side_effect=fail_once):
   with self.assertRaises(OSError):self.pub.apply(self.repository,{'release_id':plan['release_id'],'confirm':True})
  self.assertFalse(self.pub.index.exists());self.assertFalse(self.pub.pending.exists())
  self.pub.apply(self.repository,{'release_id':plan['release_id'],'confirm':True});self.assertEqual(len(self.pub.state()['links']),1)
 def test_symlink_destination_is_rejected_without_journal(self):
  self.incorporate();plan=self.publish();(self.root/'assets/facsimiles').symlink_to(self.root/'originais',target_is_directory=True)
  with self.assertRaises(EditorialError):self.pub.apply(self.repository,{'release_id':plan['release_id'],'confirm':True})
  self.assertFalse(self.pub.index.exists());self.assertFalse(self.pub.pending.exists())
 def test_unit_citation_captures_geometry_and_rejects_wrong_unit(self):
  page=self.save_review(self.structural('boxes',boxes=[[.1,.2,.3,.2]]));self.incorporate();link=self.link();body=self.sources.links.edition(self.repository,link,'ru');quote='Alpha beta gamma.'
  anchor={'language':'ru','body_sha256':model.sha256(body.encode()),'quote':quote,'start':0,'end':len(quote),'page_number':1,'notes':'NOTA PRIVADA','unit_id':'wrong-unit'}
  with self.assertRaises(EditorialError):self.sources.links.preview(self.repository,{'action':'anchor','id':link['id'],'revision':link['revision'],'anchor':anchor})
  anchor['unit_id']=page['review']['units'][0]['id'];preview=self.sources.links.preview(self.repository,{'action':'anchor','id':link['id'],'revision':link['revision'],'anchor':anchor});saved=self.sources.links.save(self.repository,{'preview_id':preview['preview_id']})
  self.assertEqual(saved['anchors'][0]['unit_boxes'],[[.1,.2,.3,.2]]);self.assertEqual(saved['anchors'][0]['unit_sha256'],page['review']['units'][0]['sha256'])

 def test_large_incorporation_is_rejected_before_writing(self):
  huge={'revision':1,'review':{'text':'я'*1100000,'status':'reviewed','printed_label':'1','units':[]}}
  before=self.canonical_hashes()
  with patch.object(self.sources.review,'page',return_value=huge):
   with self.assertRaises(EditorialError) as error:self.inc.compose(self.id,'1-2')
  self.assertEqual(error.exception.status,413);self.assertEqual(before,self.canonical_hashes())
