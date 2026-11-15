// Sem npm: Node gera um ZIP que também é validado por zipfile no roteiro de verificação.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import {collectionDocuments,metadataDocuments,contentSearchParams,canonicalCollection,markdownExport,buildCollectionZip} from '../prototipo/mesa/library-tools.js';
vm.runInThisContext(await fs.readFile(new URL('../assets/export-header.js',import.meta.url),'utf8'));
vm.runInThisContext(await fs.readFile(new URL('../assets/collection-zip.js',import.meta.url),'utf8'));
globalThis.window={splitExportHeaders:globalThis.splitExportHeaders,privateDraft:'NUNCA_EXPORTAR_PRIVADO'};
const one={id:'one',title_pt:'Título português',title_ru:'Русский заголовок',archive:'RGASPI 1',languages:[{code:'ru',file:'originais/протокол.ru.md',format:'markdown'},{code:'pt',file:'originais/protocolo.pt.md',format:'markdown'}]};
const two={id:'two',title_en:'Another document',source_name:'Fonte',languages:[{code:'en',file:'originais/two.en.txt',format:'text'}]};
const group={id:'alpha',title_pt:'Coleção de teste',document_ids:['one'],subcollections:[{id:'investigacao',title_pt:'Investigação',document_ids:['one','two']},{id:'menor',document_ids:['two']}]};
const catalog={all:[one,two],documents:new Map([['one',one],['two',two]]),collections:[group],collectionDocuments:c=>c.document_ids.map(id=>catalog.documents.get(id))};
assert.deepEqual(collectionDocuments(catalog,'alpha').map(d=>d.id),['one','two']);
assert.deepEqual(collectionDocuments(catalog,'alpha','menor').map(d=>d.id),['two']);
assert.equal(canonicalCollection('alpha','investigacao'),'alpha/investigacao');
assert.equal(canonicalCollection('alpha','alpha/investigacao'),'alpha/investigacao');
assert.deepEqual(metadataDocuments(catalog,{q:'titulo',language:'pt'}).map(d=>d.id),['one']);
assert.deepEqual(metadataDocuments(catalog,{q:'RGASPI',language:'ru'}).map(d=>d.id),['one']);
assert.deepEqual(metadataDocuments(catalog,{q:'',collection:'alpha',sub:'menor',language:'pt'}),[]);
const params=contentSearchParams({q:'"palavra rara"',collection:'alpha',sub:'investigacao',language:'ru',offset:20});
assert.equal(params.get('collection'),'alpha/investigacao');assert.equal(params.get('q'),'"palavra rara"');assert.equal(params.get('language'),'ru');assert.equal(params.get('offset'),'20');
const header='# Exportação\n\nID do documento: one\nIdioma: pt\n\n---\n\n',sources={ru:'# Протокол\n\nОригинал.\n',pt:header+'# Tradução\n\nTexto preservado.\n',en:'Texto *literal* [não é link].\n'};
assert.equal(markdownExport(one,one.languages[1],sources.pt).content,sources.pt);
assert.equal(markdownExport(two,two.languages[0],sources.en).converted,true);
const progress=[];
const readEdition=async(doc,code)=>({source:sources[code]});
const exported=await buildCollectionZip(catalog,'alpha','',{readEdition,onProgress:(done,total)=>progress.push([done,total])});
assert.equal(exported.documentCount,2);assert.equal(exported.editionCount,3);assert.equal(progress.at(-1)[0],3);
await fs.writeFile('/tmp/mesa-collection-zip-test.zip',new Uint8Array(await exported.blob.arrayBuffer()));
const smaller=await buildCollectionZip(catalog,'alpha','menor',{readEdition});assert.equal(smaller.documentCount,1);assert.equal(smaller.editionCount,1);
await assert.rejects(buildCollectionZip(catalog,'alpha','missing',{readEdition}),/válida/);
await assert.rejects(buildCollectionZip(catalog,'alpha','',{readEdition,limitBytes:2}),/256 MiB/);
await assert.rejects(buildCollectionZip(catalog,'alpha','',{readEdition:async()=>{throw Error('Arquivo indisponível');}}),/indisponível/);
const controller=new AbortController();controller.abort();await assert.rejects(buildCollectionZip(catalog,'alpha','',{signal:controller.signal,readEdition}),{name:'AbortError'});
const duplicate={...one,languages:[{code:'ru',file:'originais/ru/protocolo.md',format:'markdown'},{code:'pt',file:'originais/pt/protocolo.md',format:'markdown'}]};
const duplicateCatalog={...catalog,all:[duplicate],documents:new Map([['one',duplicate]]),collectionDocuments:()=>[duplicate],collections:[{id:'duplicate',document_ids:['one']}]};
const paths=[];await buildCollectionZip(duplicateCatalog,'duplicate','',{readEdition,writer:files=>{paths.push(...files.map(f=>f.name));return new Blob();}});
assert(paths.includes('one/ru/protocolo.md'));assert(paths.includes('one/pt/protocolo.md'));
console.log('OK: filtros, escopo, conjunto completo, deduplicação, nomes UTF-8, TXT/Markdown, falha e cancelamento de ZIP.');

const {activityEntries}=await import('../prototipo/mesa/library-home.js');
const recorded=activityEntries({events:[
 {recorded_at:'2026-11-15',basis:'Data histórica ou coleta',examples:[{id:'one',languages:['pt']}]},
 {commit:'older',recorded_at:'2026-10-21',examples:[{id:'one',languages:['pt']}]},
 {commit:'newer',recorded_at:'2026-10-22',examples:[{id:'one',languages:['pt','en']},{id:'missing',languages:['pt']}],source_examples:[{id:'two',languages:['en']}]},
 {commit:'invalid-date',recorded_at:'sem data',examples:[{id:'one',languages:['pt']}]}
]},catalog);
assert.equal(recorded.versions.length,1);assert.equal(recorded.versions[0].commit,'newer');
assert.deepEqual(recorded.versions[0].languages,['pt']);assert.equal(recorded.documents[0].doc.id,'two');
assert.equal(recorded.versions[0].recordedAt,'2026-10-22');
console.log('OK: novidades usam registros Git válidos e versões existentes; datas históricas/coleta não são promovidas a publicação.');
