// Executável com Node, sem npm: node tests/mesa_pilot_helpers.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {loadCatalog,parseImportFile,pageNumbers,dateLabel,normalize,editionText} from '../prototipo/mesa/data.js';
vm.runInThisContext(fs.readFileSync(new URL('../assets/export-header.js',import.meta.url),'utf8'));
globalThis.window={splitExportHeaders:globalThis.splitExportHeaders};
assert.deepEqual(pageNumbers('1-3, 3; 7',8),[1,2,3,7]);
assert.throws(()=>pageNumbers('0-3',8));
assert.throws(()=>pageNumbers('9',8));
assert.equal(dateLabel({date:'1937-06-11'}),'11.06.1937');
assert.equal(dateLabel({collected_date:'2026-11-14'}),'');
assert.equal(normalize('História'),'historia');
const body='## Título histórico\n\nParágrafo preservado.\n';
const header='# Exportação\n\nID do documento: showtrials-1665\nIdioma: pt\nFonte: Exemplo\n\n---\n\n';
const parsed=parseImportFile('showtrials-9999.en.md',header+header+body);
assert.equal(parsed.id,'showtrials-1665');
assert.equal(parsed.lang,'pt');
assert.equal(parsed.body,body);
assert.equal(parseImportFile('novo-documento.ru.md',body).id,'novo-documento');
assert.equal(parseImportFile('sem-idioma.md',body).lang,'');
const manifest={documents:[{id:'one',title_ru:'Оригинал',languages:[{code:'pt',file:'originais/one.pt.md'}]}],collections:[{id:'c',document_ids:['one','legacy','one'],documents:[{id:'one',title_ru:'DUPLICADO'},{id:'legacy',languages:[]}]}]};
let editions=0;
globalThis.fetch=async url=>{
 const path=new URL(url).pathname;
 if(path.endsWith('/data/manifest.json'))return {ok:true,json:async()=>manifest};
 if(path.endsWith('/data/facsimiles.json'))return {ok:true,json:async()=>({links:[{active:true,document_id:'one'},{active:false,document_id:'legacy'}]})};
 if(path.endsWith('/originais/one.pt.md')){editions++;return {ok:true,text:async()=>header+header+body};}
 return {ok:false};
};
const catalog=await loadCatalog();
assert.equal(catalog.all.length,2);
assert.equal(catalog.documents.get('one').title_ru,'Оригинал');
assert.deepEqual(catalog.collectionDocuments(catalog.collections[0]).map(d=>d.id),['one','legacy']);
assert.equal(catalog.links.length,1);
assert.equal((await editionText(catalog.documents.get('one'),'pt')).body,body);
await editionText(catalog.documents.get('one'),'pt');
assert.equal(editions,1);
await assert.rejects(()=>editionText(catalog.documents.get('one'),'en'));
console.log('OK: catálogo misto, deduplicação, datas históricas, cabeçalhos, importação e seleção de páginas.');

const {snapshotDesk,restoreDesk,pendingCount}=await import('../prototipo/mesa/session.js');
const material={key:'one',kind:'document',doc:catalog.documents.get('one'),lang:'pt',mode:'edit',scroll:320,position:{unit:'4',offset:-10},buffers:{'acervo:one:pt':'rascunho não confirmado'}};
const file={name:'fonte.pdf',size:123};
const desk=snapshotDesk([material,{kind:'pdf',key:'upload:fonte.pdf:123',file,page:4,pageUnsaved:{'acervo:upload:fonte.pdf:123:4':'página em andamento'},pdf:{circular:true}}],'one',{q:'Nikolaev',collection:'c',sub:''});
assert.equal(desk.materials[1].file,undefined);
assert.equal(desk.materials[1].pdf,undefined);
const recovered=restoreDesk(JSON.parse(JSON.stringify(desk)),catalog);
assert.equal(recovered.active,'one');
assert.equal(recovered.materials[0].buffers['acervo:one:pt'],'rascunho não confirmado');
assert.equal(recovered.materials[0].position.unit,'4');
assert.equal(recovered.materials[1].needsFile,true);
assert.equal(recovered.materials[1].page,4);
assert.equal(pendingCount(recovered.materials[0]),1);
assert.equal(recovered.library.q,'Nikolaev');
assert.equal(restoreDesk({version:1,materials:[{kind:'document',documentId:'inexistente',key:'x'},{kind:'pdf',pdfUrl:'https://invalido.example',key:'y'}]},catalog).materials.length,0);
assert.equal(restoreDesk(null,catalog).materials.length,0);
console.log('OK: recuperação de abas, rascunhos pendentes e página de PDF sem serializar arquivos ou objetos das bibliotecas.');

const {comparisonLanguage}=await import('../prototipo/mesa/data.js');
const trilingual={doc:{languages:[{code:'ru'},{code:'pt'},{code:'en'}]},lang:'ru',otherLang:'en'};
assert.equal(comparisonLanguage(trilingual),'en');
assert.equal(comparisonLanguage({...trilingual,otherLang:'pt'}),'pt');
assert.equal(comparisonLanguage({...trilingual,otherLang:'ru'}),'pt');
assert.equal(comparisonLanguage({doc:{languages:[{code:'ru'}]},lang:'ru'}),undefined);
const languageDesk=snapshotDesk([{...material,otherLang:'en',expandedUnits:[1,4]}],'one',{});
assert.deepEqual(restoreDesk(languageDesk,catalog).materials[0].expandedUnits,[1,4]);
assert.equal(restoreDesk(languageDesk,catalog).materials[0].otherLang,'en');
console.log('OK: escolha do segundo idioma e preservação dos trechos expandidos.');

const {passageCitation}=await import('../prototipo/mesa/data.js');
const citation=passageCitation({id:'one',title_pt:'Documento de pesquisa',date:'1937-06-11',source_url:'https://fonte.example/documento',archive:'Arquivo, folha 3'}, {quote:'Trecho traduzido.',lang:'en',unit:4,draft:true},'http://localhost/index.html#/doc/one');
assert.ok(citation.includes('“Trecho traduzido.”'));
assert.ok(citation.includes('Idioma: English'));
assert.ok(citation.includes('11.06.1937'));
assert.ok(citation.includes('numeração provisória'));
assert.ok(citation.includes('não publicada'));
assert.ok(citation.includes('https://fonte.example/documento'));
assert.ok(citation.includes('Arquivo, folha 3'));
assert.ok(!passageCitation({title_ru:'Документ'},{quote:'Текст',lang:'ru',unit:1,draft:false},'').includes('não publicada'));
console.log('OK: citação com fonte, idioma, referência, data e distinção de rascunho e numeração provisória.');

const {makeTextAnchor,resolveTextQuote}=await import('../prototipo/mesa/data.js');
const paragraph='До начала. Первая фраза. Ещё одна фраза. Конец.';
const selected='Ещё одна фраза.';
const at=paragraph.indexOf(selected);
const exactAnchor=makeTextAnchor(paragraph,at,at+selected.length,'ru',3);
const exact=resolveTextQuote(paragraph,exactAnchor);
assert.equal(paragraph.slice(exact.start,exact.end),selected);
assert.equal(exact.start,at);
assert.notEqual(exact.start,0);
assert.notEqual(exact.end,paragraph.length);
assert.equal(resolveTextQuote('Новый текст. '+paragraph,exactAnchor).status,'found');
assert.equal(resolveTextQuote(paragraph.replace(selected,'Изменённая фраза.'),exactAnchor).status,'missing');
const repeated='Frase igual. Intervalo. Frase igual.';
const repeatedStart=repeated.lastIndexOf('Frase igual.');
const repeatAnchor=makeTextAnchor(repeated,repeatedStart,repeated.length,'pt',2);
assert.equal(resolveTextQuote(repeated,repeatAnchor).start,repeatedStart);
assert.equal(resolveTextQuote(repeated,{quote:'Frase igual.'}).status,'ambiguous');
const spaces=makeTextAnchor('antes  frase exata  depois',5,20,'pt',1);
assert.equal(spaces.quote,'frase exata');
assert.equal(spaces.start,7);
assert.equal(spaces.end,18);
const unicode='🙂 Texto destacado e sequência.';
const unicodeStart=unicode.indexOf('Texto');
assert.equal(resolveTextQuote(unicode,makeTextAnchor(unicode,unicodeStart,unicodeStart+15,'pt',1)).start,unicodeStart);
console.log('OK: localização da frase exata, deslocamento do texto, contexto, ambiguidade, espaços e offsets UTF-16.');

const {literalMatches}=await import('../prototipo/mesa/data.js');
assert.deepEqual(literalMatches('Москва и МОСКВА.','москва'),[{start:0,end:6},{start:9,end:15}]);
assert.equal(literalMatches('Москва и МОСКВА.','Москва',{caseSensitive:true}).length,1);
assert.equal(literalMatches('a.b axb [x]','a.b').length,1);
assert.equal(literalMatches('a.b axb [x]','[x]').length,1);
assert.equal(literalMatches('aaa aaa aaa','aaa',{limit:2}).length,2);
assert.equal(literalMatches('Текст','').length,0);
assert.equal(literalMatches('🙂 frase e frase','frase')[0].start,3);
assert.equal(literalMatches('one','one',{limit:0}).length,0);
const findDesk=snapshotDesk([{...material,findState:{query:'Москва',lang:'ru',caseSensitive:false,index:2}}],'one',{});
assert.equal(restoreDesk(findDesk,catalog).materials[0].findState.query,'Москва');
console.log('OK: busca literal, caracteres de expressão regular, russo, maiúsculas, limites e recuperação da consulta.');

const {markdownPayload}=await import('../prototipo/mesa/editorial.js');
const snapshot={revision:'revision-original',edition:{id:'one:pt',sha256:'sha-original'},content:header+body};
const payload=markdownPayload(snapshot,'## Texto novo\n\nCorpo editado.\n');
assert.equal(payload.revision,'revision-original');
assert.equal(payload.edition_id,'one:pt');
assert.equal(payload.content_sha256,'sha-original');
assert.equal(payload.content,header+'## Texto novo\n\nCorpo editado.\n');
const linkedDesk=snapshotDesk([{...material,mode:'facsimile',facsimile:{source:'fonte-1',page:13,pdf:{shouldNotPersist:true}},returnMode:'facsimile'}],'one',{});
assert.equal(linkedDesk.materials[0].facsimile.pdf,undefined);
const recoveredLinked=restoreDesk(linkedDesk,catalog);
assert.equal(recoveredLinked.materials[0].mode,'facsimile');
assert.equal(recoveredLinked.materials[0].facsimile.page,13);
console.log('OK: prévia editorial preserva revisão/SHA/cabeçalho e a consulta pareada recupera a página sem serializar PDF.');

const {metadataPayload,collectionPayload,collectionSlug}=await import('../prototipo/mesa/editorial.js');
const metadata=metadataPayload({revision:'r1',document:{id:'one'}},{title_pt:'Título',title_ru:'Документ',title_en:'',kind:'document',document_type:'letter',author:'Автор',archive:'F. 1',date_display:'1936',date_value:'1936',date_precision:'year'},['root','root/sub','root']);
assert.deepEqual(metadata.collection_ids,['root','root/sub']);
assert.equal(metadata.document.historical_date.value,'1936');
assert.equal(metadata.document.archive_reference,'F. 1');
assert.equal(metadata.document.author_label,'Автор');
assert.equal(metadata.revision,'r1');
assert.ok(!('source' in metadata.document));
assert.ok(!('id' in metadata.document));
const parentFixed=collectionPayload('r2',{id:'root/sub',slug:'sub',parent_id:'root'},{slug:'changed',parent_id:'other',title_pt:'Título editado'});
assert.equal(parentFixed.slug,'sub');
assert.equal(parentFixed.parent_id,'root');
assert.equal(parentFixed.collection_id,'root/sub');
assert.equal(collectionPayload('r3',null,{slug:'nova',title_pt:'Nova',parent_id:'root'}).collection_id,null);
assert.equal(collectionSlug('História política — 1934–1936'),'historia-politica-1934-1936');
console.log('OK: metadados preservam campos protegidos, associações sem repetição e identidade das URLs de coleções existentes.');

const {sourceFile}=await import('../prototipo/mesa/pdf-workflow.js');
const sourceId='pdf-'+('a'.repeat(32));
assert.equal(sourceFile(sourceId),'api/editorial/pdf/'+sourceId+'/file');
const persistentSource={kind:'pdf',key:'source:'+sourceId,backendSource:sourceId,page:4,title:'Fonte local',backendDrafts:{4:{revision:2,raw_sha256:'sha',review:{text:'Texto não salvo',basis:'native',status:'pending',notes:'',printed_label:''}}},pdf:{notSerializable:true}};
const sourceSnapshot=snapshotDesk([persistentSource],persistentSource.key,{});
assert.equal(sourceSnapshot.materials[0].pdf,undefined);
const restoredSource=restoreDesk(sourceSnapshot,catalog).materials[0];
assert.equal(restoredSource.needsFile,false);
assert.equal(restoredSource.backendSource,sourceId);
assert.equal(restoredSource.backendDrafts[4].review.text,'Texto não salvo');
assert.equal(pendingCount(restoredSource),1);
console.log('OK: fonte local recupera página e revisão pendente sem serializar o PDF.');

const {splitRatio,zoomValue}=await import('../prototipo/mesa/controls.js');
assert.equal(splitRatio(5),22);
assert.equal(splitRatio(95),78);
assert.equal(splitRatio(60),60);
assert.equal(splitRatio('invalid'),50);
assert.equal(zoomValue(.05),.25);
assert.equal(zoomValue(8),3);
assert.equal(zoomValue(1.25),1.25);
assert.equal(zoomValue('fit'),'fit');
const resizeDesk=snapshotDesk([{...material,splitRatio:65,facsimile:{source:'s',page:6,zoom:1.5,splitRatio:40}}],'one',{});
const restoredResize=restoreDesk(resizeDesk,catalog).materials[0];
assert.equal(restoredResize.splitRatio,65);
assert.equal(restoredResize.facsimile.splitRatio,40);
assert.equal(restoredResize.facsimile.zoom,1.5);
console.log('OK: limites de divisão/zoom e recuperação das preferências por material.');

const {corpusProblems,corpusPayload}=await import('../prototipo/mesa/corpus.js');
const originalCorpus={filename:'carta.ru.md',id:'carta',lang:'ru',role:'original',title:'Письмо',original:'# Письмо\n\nТекст.',body:'Текст.'};
const translatedCorpus={...originalCorpus,filename:'carta.pt.md',lang:'pt',role:'translation',title:'Carta',original:'# Carta\n\nTexto.'};
assert.deepEqual(corpusProblems([originalCorpus,translatedCorpus]),[]);
assert(corpusProblems([translatedCorpus]).some(message=>message.includes('exatamente um original')));
assert(corpusProblems([originalCorpus,translatedCorpus],new Set(['carta'])).some(message=>message.includes('já existe')));
assert(corpusProblems([originalCorpus,{...translatedCorpus,lang:'ru'}]).some(message=>message.includes('idiomas repetidos')));
assert(corpusProblems([originalCorpus,{...translatedCorpus,id:'outra'}]).some(message=>message.startsWith('outra:')));
const corpusTestPayload=corpusPayload([originalCorpus,translatedCorpus],{collection_ids:['c']},'rev');
assert.equal(corpusTestPayload.entries[0].content,originalCorpus.original);
assert.equal(corpusTestPayload.entries[1].role,'translation');
assert.deepEqual(Object.keys(corpusTestPayload).sort(),['defaults','entries','revision']);
console.log('OK: corpus preserva conteúdo e impede IDs existentes, versões órfãs e idiomas repetidos.');

const {issuePayload}=await import('../prototipo/mesa/review.js');
const queueProposal=issuePayload('revision','documento','documento:pendencia',{prioridade:'alta',status:'em_revisao',dificuldade_encontrada:'Conferir fonte',notas_do_revisor:'Nota',texto:'Não enviar'});
assert.deepEqual(Object.keys(queueProposal).sort(),['document_id','issues','revision']);
assert.deepEqual(Object.keys(queueProposal.issues[0]).sort(),['chave','dificuldade_encontrada','notas_do_revisor','prioridade','status']);
assert.equal(queueProposal.issues[0].chave,'documento:pendencia');
console.log('OK: registrar revisão envia apenas os campos da pendência, sem texto ou metadados.');

const {linkPayload}=await import('../prototipo/mesa/source-links.js');
const {resolvePdfPage}=await import('../prototipo/mesa/pdf.js');
const {mergeDocumentLinks}=await import('../prototipo/mesa/data.js');
assert.deepEqual(resolvePdfPage(13,1,{'13':1}),{sourcePage:13,pdfPage:1});
assert.deepEqual(resolvePdfPage(5,2,{'13':1,'20':2}),{sourcePage:13,pdfPage:1});
assert.deepEqual(resolvePdfPage(20,2,{'13':1,'20':2}),{sourcePage:20,pdfPage:2});
assert.deepEqual(resolvePdfPage(99,10),{sourcePage:10,pdfPage:10});
assert.throws(()=>resolvePdfPage(13,1,{'13':2}));
const publicLink={id:'link1',document_id:'doc',pdf_url:'assets/facsimiles/a.pdf',pages:[13],published_page_map:{'13':1}};
const localLink={id:'link1',document_id:'doc',source_id:'pdf-source',pages:[13],active:true};
const mergedLinks=mergeDocumentLinks([publicLink],[localLink]);
assert.equal(mergedLinks.length,1);assert.equal(mergedLinks[0].local,true);assert.equal(mergedLinks[0].portalPrepared,true);
assert.equal(mergedLinks[0].pdf_url,'api/editorial/pdf/pdf-source/file');assert.equal(mergedLinks[0].published_page_map,undefined);
assert.deepEqual(mergeDocumentLinks([publicLink],[{...localLink,active:false}]),[publicLink]);
assert.deepEqual(mergeDocumentLinks(mergedLinks,[{...localLink,active:false}]),[]);
const createLinkPayload=linkPayload('pdf-id','doc','13','Nota');
assert.equal(createLinkPayload.action,'create');assert.equal(createLinkPayload.project_id,'');assert.equal(createLinkPayload.pages,'13');
const updateLinkPayload=linkPayload('pdf-id','doc','13-15','Nota',{id:'link1',revision:2},false);
assert.deepEqual(updateLinkPayload,{action:'update',id:'link1',revision:2,pages:'13-15',notes:'Nota',active:false});
console.log('OK: vínculo não substitui texto; PDF recortado conserva páginas físicas e consulta local não duplica o vínculo público.');

const {projectDocumentKey,workspacePayload}=await import('../prototipo/mesa/projects.js');
const privateProjectId='project-'+ 'a'.repeat(32);
assert.notEqual(projectDocumentKey('one',privateProjectId),projectDocumentKey('one'));
const projectSnapshot=snapshotDesk([{key:projectDocumentKey('one',privateProjectId),kind:'document',doc:catalog.documents.get('one'),projectId:privateProjectId,project:{title:'Pesquisa'},lang:'en',projectBases:{k:{revision:1,content_sha256:'hash'}},buffers:{private:'Texto'}}],projectDocumentKey('one',privateProjectId),{});
const privateRestore=restoreDesk(projectSnapshot,catalog);
assert.equal(privateRestore.materials[0].projectId,privateProjectId);
assert.equal(privateRestore.materials[0].lang,'en');
assert.equal(privateRestore.materials[0].key,projectDocumentKey('one',privateProjectId));
assert.equal(privateRestore.materials[0].project.title,'Pesquisa');
assert.deepEqual(privateRestore.materials[0].projectBases,{k:{revision:1,content_sha256:'hash'}});
const privateRequest=workspacePayload(privateProjectId,'one:pt',{revision:2,content_sha256:'h'},'Texto privado','one.pt.md');
assert.equal(privateRequest.project_id,privateProjectId);assert.equal(privateRequest.revision,2);assert.equal(privateRequest.filename,'one.pt.md');
assert(!('document' in privateRequest));assert(!('collection_ids' in privateRequest));
const privateCitation=passageCitation({id:'one',title:'Fonte'},{lang:'pt',unit:1,quote:'Texto privado',project:{id:privateProjectId,title:'Pesquisa'}},'https://example.org/doc');
assert(privateCitation.includes('Versão privada do projeto Pesquisa'));
assert(privateCitation.includes('não desta versão privada'));
console.log('OK: abas e buffers de projetos são isolados; tradução privada restaura idioma e citação identifica versão não publicada.');

{
vm.runInThisContext(fs.readFileSync(new URL('../assets/vendor/markdown-it/markdown-it.umd.min.js',import.meta.url),'utf8'));
window.markdownit=globalThis.markdownit;window.DOMPurify={sanitize:html=>html};
const {markdownSourceRanges,renderMarkdown}=await import('../prototipo/mesa/data.js');
const {passageRange,checkedPassageRange,passagePayload}=await import('../prototipo/mesa/passage-edit.js');
const mapMarkdown=window.markdownit(),mappedBody='# Título\r\n\r\nUma **frase** traduzida.\r\n\r\nOutro bloco.\r\n';
const sourceRanges=markdownSourceRanges(mappedBody,mapMarkdown.parse(mappedBody,{}));
assert.deepEqual(sourceRanges.map(r=>mappedBody.slice(r.start,r.end)),['# Título','Uma **frase** traduzida.','Outro bloco.']);
assert(renderMarkdown(mappedBody,'markdown',true).includes('data-source-start="12"'));
const inlineText=raw=>mapMarkdown.parse(raw,{}).find(t=>t.type==='inline').children.filter(t=>t.type==='text'||t.type==='code_inline').map(t=>t.content).join('');
const mappedBlock='Uma **frase** traduzida.';
const exactPhrase=checkedPassageRange(mappedBlock,0,mappedBlock.length,{quote:'frase',renderedBlockText:'Uma frase traduzida.',start:4,end:9},inlineText);
assert.equal(exactPhrase.exact,true);assert.equal(exactPhrase.expected,'frase');
const crossesMarkup=passageRange(mappedBlock,0,mappedBlock.length,'Uma frase');assert.equal(crossesMarkup.exact,false);
const repeated=passageRange('duas duas',0,9,'duas');assert.equal(repeated.exact,false);
const entity='A &amp; B';assert.equal(checkedPassageRange(entity,0,entity.length,{quote:'&',renderedBlockText:'A & B',start:2,end:3},inlineText).exact,false);
const hidden='&#65; [link](https://example.org/A)';assert.equal(checkedPassageRange(hidden,0,hidden.length,{quote:'A',renderedBlockText:'A link',start:0,end:1},inlineText).exact,false);
const unicodeBody='😀 Texto traduzido.',unicodeStart=unicodeBody.indexOf('Texto');
assert.equal(passagePayload({revision:'r',edition:{id:'doc:pt',sha256:'h'}},unicodeBody,{start:unicodeStart,end:unicodeStart+5,expected:'Texto',replacement:'Trecho'}).start,2);
console.log('OK: mapas Markdown preservam CRLF; seleção não adivinha entidades/links ocultos; offsets Unicode chegam corretos ao backend.');

}

// O vínculo usa UTF-16 do Markdown; a divisão de unidade usa pontos Unicode.
{
 const {anchorPayload,codePointOffset}=await import('../prototipo/mesa/parity.js');
 const {linkPayload}=await import('../prototipo/mesa/source-links.js');
 const source='😀 Привет';const start=source.indexOf('Привет');
 const payload=anchorPayload({id:'link-1',revision:4},{start,end:source.length,expected:'Привет'},'ru','hash',2,'unit-1','Conferido');
 assert.equal(payload.anchor.start,3);
 assert.equal(codePointOffset(source,start),2);
 assert.equal(payload.anchor.quote,'Привет');
 assert.equal(payload.anchor.page_number,2);
 assert.equal(payload.anchor.unit_id,'unit-1');
 assert.equal(payload.revision,4);
 assert.equal(linkPayload('pdf-1','document','1','',null,true,'project-123').project_id,'project-123');
 assert.equal(linkPayload('pdf-1','document','1','').project_id,'');
 const projectId='project-'+'a'.repeat(32);
 const pdf={key:'source:pdf-1@'+projectId,kind:'pdf',backendSource:'pdf-'+'b'.repeat(32),projectId,project:{title:'Pesquisa'},page:2};
 const {snapshotDesk,restoreDesk}=await import('../prototipo/mesa/session.js');
 const restored=restoreDesk(snapshotDesk([pdf],pdf.key,{}),{documents:new Map(),collections:[],links:[]});
 assert.equal(restored.materials[0].project.id,projectId);
 assert.equal(restored.materials[0].project.title,'Pesquisa');
}

{
 const {regionScrollSpeed}=await import('../prototipo/mesa/parity.js');
 assert.equal(regionScrollSpeed(300,100,500),0);
 assert(regionScrollSpeed(105,100,500)<0);
 assert(regionScrollSpeed(495,100,500)>0);
 assert.equal(regionScrollSpeed(900,100,500),720);
 assert.equal(regionScrollSpeed(-100,100,500),-720);
 assert.equal(regionScrollSpeed(100,100,100),0);
}

{
 const {associatedTextRange}=await import('../prototipo/mesa/parity.js');
 const raw='😀 Frase repetida. Frase repetida.';
 const start=raw.lastIndexOf('Frase repetida.');
 assert.deepEqual(associatedTextRange(raw,{start,end:raw.length,quote:'Frase repetida.'},0,raw.length,raw,s=>s),{start,end:raw.length});
 assert.equal(associatedTextRange(raw,{start,end:raw.length,quote:'Trecho alterado'},0,raw.length,raw,s=>s),null);
 const formatted='**Pergunta**: resposta.';
 assert.deepEqual(associatedTextRange(formatted,{start:14,end:formatted.length,quote:'resposta.'},0,formatted.length,'Pergunta: resposta.',s=>s.replaceAll('**','')),{start:10,end:19});
 assert.deepEqual(associatedTextRange('**Título**',{start:0,end:10,quote:'**Título**'},0,10,'Título',s=>s),{start:0,end:6});
}

{
 const {anchorComparisonRows}=await import('../prototipo/mesa/source-links.js');
 const anchor={id:'anchor-1',language:'ru',page_number:1,quote:'Подсудимый КОРК',unit_boxes:[]};
 const rows=anchorComparisonRows({anchors:[]},{anchors:[anchor]});
 assert.deepEqual(rows[0],{field:'Quantidade de trechos associados',before:'0',after:'1'});
 assert.equal(rows[1].before,'Sem associação');
 assert(rows[1].after.includes('Подсудимый КОРК'));
 assert(rows[1].after.includes('Página física 1'));
 assert.equal(anchorComparisonRows({anchors:[anchor]},{anchors:[]})[1].after,'Sem associação');
 assert.equal(anchorComparisonRows({anchors:[anchor]},{anchors:[anchor]}).length,1);
}

{
 const {storedAssociationRange,anchorPayload}=await import('../prototipo/mesa/parity.js');
 const body='😀 Председатель: Вопрос?';
 const anchor={start:3,end:body.length,quote:body.slice(3),body_sha256:'original'};
 const range=storedAssociationRange(body,anchor,'original');
 assert.deepEqual(range,{start:3,end:body.length,expected:body.slice(3),exact:true});
 assert.equal(storedAssociationRange(body,anchor,'new-version'),null);
 assert.equal(storedAssociationRange(body,{...anchor,quote:'Outra frase'},'original'),null);
 const updated=anchorPayload({id:'same-link',revision:9},range,'ru','original',2,'new-unit','Nota revisada');
 assert.equal(updated.id,'same-link');assert.equal(updated.revision,9);
 assert.equal(updated.anchor.start,anchor.start);assert.equal(updated.anchor.body_sha256,anchor.body_sha256);
 assert.equal(updated.anchor.page_number,2);assert.equal(updated.anchor.unit_id,'new-unit');assert.equal(updated.anchor.notes,'Nota revisada');
 const {anchorComparisonRows}=await import('../prototipo/mesa/source-links.js');
 const old={...anchor,id:'anchor',language:'ru',page_number:1,page_revision:1};
 const rows=anchorComparisonRows({anchors:[old]},{anchors:[{...old,page_revision:2}]});
 assert(rows[1].before.includes('Revisão da página: 1'));assert(rows[1].after.includes('Revisão da página: 2'));
}
