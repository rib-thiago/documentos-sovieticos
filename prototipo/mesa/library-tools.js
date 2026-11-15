import {node as n,label,dateLabel,normalize,LANGUAGES,asset} from './data.js';
import {editorialRequest as api} from './editorial.js';
export function canonicalCollection(root,sub=''){return sub?(sub.startsWith(root+'/')?sub:root+'/'+sub):root;}
export function collectionDocuments(catalog,rootId,subId=''){
 const root=catalog.collections.find(c=>c.id===rootId);if(!root)return [];
 if(subId){const sub=(root.subcollections||[]).find(s=>s.id===subId);return [...new Set(sub?.document_ids||(sub?.documents||[]).map(d=>d.id))].map(id=>catalog.documents.get(id)).filter(Boolean);}
 return [...new Map([...catalog.collectionDocuments(root),...(root.subcollections||[]).flatMap(sub=>(sub.document_ids||(sub.documents||[]).map(d=>d.id)).map(id=>catalog.documents.get(id)).filter(Boolean))].map(doc=>[doc.id,doc])).values()];
}
export function metadataDocuments(catalog,state){
 const docs=state.collection?collectionDocuments(catalog,state.collection,state.sub):catalog.all,q=normalize(state.q).trim();
 return docs.filter(doc=>(!state.language||doc.languages?.some(l=>l.code===state.language))&&(!q||normalize([doc.id,doc.title_pt,doc.title_ru,doc.title_en,doc.title,doc.author,doc.author_label,doc.archive,doc.archive_reference,doc.source_name,doc.source_url,dateLabel(doc)].filter(Boolean).join(' ')).includes(q)));
}
export function contentSearchParams(state){
 const params=new URLSearchParams({q:state.q.trim(),offset:String(state.offset||0),limit:'20',scope:'all',sort:state.q.trim()?'relevance':state.collection?'source':'title'});
 if(state.collection)params.set('collection',canonicalCollection(state.collection,state.sub));if(state.language)params.set('language',state.language);return params;
}
function safeName(value){if(!value||value.includes('\\')||value.startsWith('/')||value.split('/').some(p=>!p||p==='.'||p==='..'))throw Error('Nome de arquivo inválido no pacote.');return value;}
const escapeMarkdown=value=>value.replace(/([\\`*_[\]<>#])/g,'\\$1');
export function markdownExport(doc,language,source){
 if((language.format||doc.format||(language.file.endsWith('.txt')?'text':'markdown'))!=='text')return {content:source,converted:false};
 const body=window.splitExportHeaders?.(source).body??source,title=doc['title_'+language.code]||label(doc);
 const lines=['# '+escapeMarkdown(title),'',...(doc.source_url?['Fonte: '+doc.source_url]:[]),'ID do documento: '+doc.id,...(dateLabel(doc)?['Data do documento: '+dateLabel(doc)]:[]),'Idioma: '+language.code.toUpperCase(),'','---','',escapeMarkdown(body)];return {content:lines.join('\n'),converted:true};
}
async function readCatalogEdition(doc,code,{signal}={}){const edition=doc.languages?.find(l=>l.code===code);if(!edition)throw Error('Versão ausente no catálogo.');const response=await fetch(asset(edition.file),{signal,cache:'no-store'});if(!response.ok)throw Error('Arquivo indisponível: '+edition.file);return {source:await response.text()};}
export async function buildCollectionZip(catalog,rootId,subId='',{signal,readEdition=readCatalogEdition,writer=globalThis.archiveStoredZip,onProgress=()=>{},limitBytes=256*1024*1024}={}){
 const root=catalog.collections.find(c=>c.id===rootId),sub=subId?(root?.subcollections||[]).find(s=>s.id===subId):null;
 if(!root||subId&&!sub)throw Error('Selecione uma coleção ou subcoleção válida.');
 const documents=collectionDocuments(catalog,rootId,subId);if(!documents.length)throw Error('O conjunto não tem documentos para exportar.');
 if(typeof writer!=='function')throw Error('O componente ZIP não carregou. Atualize a página.');
 const jobs=documents.flatMap(doc=>(doc.languages||[]).map(language=>({doc,language})));if(!jobs.length)throw Error('Não há versões disponíveis neste conjunto.');
 const parts=new Array(jobs.length),records=new Array(jobs.length),names=new Set(),encoder=new TextEncoder();let total=0,done=0,next=0,failure=null;
 function add(name,content){name=safeName(name);if(names.has(name))throw Error('Nome repetido no pacote: '+name);names.add(name);const data=encoder.encode(content);total+=data.length;if(total>limitBytes)throw Error('O pacote excede 256 MiB. Exporte uma subcoleção por vez.');return {name,data};}
 async function worker(){while(next<jobs.length&&!failure){if(signal?.aborted)throw new DOMException('Cancelado','AbortError');const index=next++,{doc,language}=jobs[index];try{
   // A leitura usa somente as edições do catálogo; nunca consulta buffers ou projetos.
   const data=await readEdition(doc,language.code,{signal});if(signal?.aborted)throw new DOMException('Cancelado','AbortError');
   const result=markdownExport(doc,language,data.source),base=language.file.split('/').pop(),stem=base.replace(/\.(?:txt|markdown)$/i,'.md'),duplicate=(doc.languages||[]).filter(l=>l.file.split('/').pop().replace(/\.(?:txt|markdown)$/i,'.md')===stem).length>1;
   const path=doc.id+'/'+(duplicate?language.code+'/':'')+stem,files=[add(path,result.content)];
   let original=null;if(result.converted){original=doc.id+'/originais/'+language.code+'/'+base;files.push(add(original,data.source));}
   parts[index]=files;records[index]={document_id:doc.id,language:language.code,source_file:language.file,markdown_file:path,original_copy:original,converted_from_text:result.converted};onProgress(++done,jobs.length);
  }catch(error){failure=error;throw error;}}}
 const workers=await Promise.allSettled([worker(),worker(),worker()]);if(failure)throw failure;const rejected=workers.find(r=>r.status==='rejected');if(rejected)throw rejected.reason;if(signal?.aborted)throw new DOMException('Cancelado','AbortError');
 const clean=object=>Object.fromEntries(Object.entries(object).filter(([key])=>!['documents','subcollections'].includes(key)));
 const metadata={schema_version:1,exported_at:new Date().toISOString(),scope:'canonical_catalog',collection:{...clean(root),subcollections:(root.subcollections||[]).map(s=>({...clean(s),document_ids:s.document_ids||(s.documents||[]).map(d=>d.id)}))},subcollection:sub?clean(sub):null,documents,files:records};
 const files=[...parts.flat(),add('manifesto.json',JSON.stringify(metadata,null,2)),add('LEIA-ME.txt','Documentos Soviéticos\n\nColeção: '+label(root)+(sub?' / '+label(sub):'')+'\n\nContém todas as versões do acervo dos documentos escolhidos, independentemente dos filtros de busca/idioma na tela. Arquivos Markdown preservam o conteúdo recebido do acervo. Versões TXT têm exportação Markdown e uma cópia do texto de origem. Consulte manifesto.json para metadados, arquivos de origem e correspondência de nomes. Não inclui PDFs, imagens, notas ou versões privadas de projetos.\n')];
 return {blob:writer(files),filename:(rootId+(subId?'--'+subId:'')).replace(/[/\\]/g,'--')+'.zip',documentCount:documents.length,editionCount:jobs.length};
}
export function mountLibraryTools(env,ui){
 const {query,collection,sub,scope,language,results,cards,heading,note,summary,zipHost}=ui,state=env.state;let dead=false,request=0,timer,controller,zipController,busy=false;
 const zipButton=env.button('',downloadZip,'quiet'),zipCancel=env.button('Cancelar ZIP',()=>zipController?.abort(),'quiet'),zipStatus=n('span',{role:'status'});zipCancel.hidden=true;zipHost.append(zipButton,zipCancel,zipStatus);
 function zipLabel(){if(!busy)zipButton.textContent=sub.value?'Baixar subcoleção completa · ZIP':'Baixar coleção completa · ZIP';zipHost.hidden=!collection.value;zipButton.disabled=busy;}
 async function downloadZip(){
  if(busy)return;const root=collection.value,child=sub.value,title=label(env.catalog.collections.find(c=>c.id===root));busy=true;zipController=new AbortController();zipCancel.hidden=false;zipLabel();zipStatus.textContent='Preparando '+title+'…';
  try{const result=await buildCollectionZip(env.catalog,root,child,{signal:zipController.signal,readEdition:env.readEdition,onProgress:(done,total)=>{zipStatus.textContent=title+' · '+done+'/'+total+' versões';}});if(dead)return;
   const url=URL.createObjectURL(result.blob),link=n('a',{href:url,download:result.filename});document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);zipStatus.textContent=`${result.documentCount} documentos · ${result.editionCount} versões exportadas.`;
  }catch(error){if(!dead)zipStatus.textContent=error.name==='AbortError'?'ZIP cancelado; nenhum pacote parcial baixado.':'Não foi possível concluir o ZIP. '+error.message;}finally{busy=false;zipCancel.hidden=true;zipLabel();}
 }
 function saveState(reset){Object.assign(state,{q:query.value,collection:collection.value,sub:sub.value,scope:scope.value,language:language.value});if(reset)state.offset=0;env.store();}
 async function search({reset=true,debounce=false}={}){
  clearTimeout(timer);controller?.abort();saveState(reset);zipLabel();const token=++request;
  const active=Boolean(state.q.trim()||state.collection||state.language);cards.hidden=active;results.hidden=!active;summary.hidden=!active;
  const root=env.catalog.collections.find(c=>c.id===state.collection),child=root?.subcollections?.find(c=>c.id===state.sub);heading.textContent=child?label(child):root?label(root):active?'Resultados da busca':'Coleções do acervo';
  note.textContent=root?(child?.description_pt||root.description_pt||root.subtitle_pt||'Documentos deste conjunto.'):(active?'Resultados do acervo; versões privadas não são pesquisadas aqui.':'Percursos documentais, organizados por suas fontes e contextos.');
  env.onContext?.({active,root,child});
  if(!active)return;
  if(debounce){results.replaceChildren();summary.textContent='Preparando a busca…';timer=setTimeout(()=>run(token),300);return;}await run(token);
 }
 async function run(token){
  if(dead||!env.current()||token!==request)return;controller=new AbortController();results.replaceChildren();summary.textContent='Buscando…';
  try{
   let page;
   if(state.scope==='text'&&env.backend){const params=contentSearchParams(state);page=await api((state.q.trim()?'/api/search?':'/api/documents?')+params,{signal:controller.signal});}
   else{const docs=metadataDocuments(env.catalog,state);page={total:docs.length,offset:state.offset||0,limit:20,has_more:(state.offset||0)+20<docs.length,items:docs.slice(state.offset||0,(state.offset||0)+20)};}
   if(dead||!env.current()||token!==request)return;
   if(page.total&&page.offset>=page.total){state.offset=Math.floor((page.total-1)/20)*20;env.store();await search({reset:false});return;}
   summary.textContent=`${page.total} documentos · ${page.items.length?page.offset+1:0}–${Math.min(page.offset+page.limit,page.total)} · ${state.scope==='text'?'conteúdo pelo backend local':'catálogo'}`;
   if(page.items.some(item=>!env.catalog.documents.has(item.id)))throw Error('O catálogo mudou em outra janela. Atualize a página com Ctrl+Shift+R para consultar os documentos novos.');
   for(const item of page.items){const doc=env.catalog.documents.get(item.id),match=item.match;if(!doc)continue;
    results.append(n('article',{class:'document-item library-result'},[n('div',{},[env.button(label(doc),()=>env.open(doc,match,state.q),'doc-title'),n('span',{class:'doc-date',text:dateLabel(doc)}),n('p',{class:'doc-details',text:[doc.id,doc.source_name,(doc.languages||[]).map(l=>l.code.toUpperCase()).join(' / ')].filter(Boolean).join(' · ')}),match&&n('p',{class:'library-snippet',text:(LANGUAGES[match.language]||match.language)+' · '+match.snippet})]),env.button(match?'Abrir em '+(LANGUAGES[match.language]||match.language):'Abrir →',()=>env.open(doc,match,state.q),'quiet')]));
   }
   if(!page.items.length)results.append(n('p',{class:'library-no-results',text:'Nenhum documento encontrado. Experimente outro termo, idioma ou conjunto.'}));
   if(page.total>20){const previous=env.button('‹ Anterior',()=>turn(-20),'quiet'),next=env.button('Próxima ›',()=>turn(20),'quiet');previous.disabled=!page.offset;next.disabled=!page.has_more;results.append(n('div',{class:'pagination'},[previous,n('span',{text:Math.floor(page.offset/20)+1+' / '+Math.ceil(page.total/20)}),next]));}
  }catch(error){if(error.name!=='AbortError'&&!dead&&token===request){summary.textContent='Busca não concluída.';results.replaceChildren(n('p',{class:'backend-warning',text:error.message}),env.button('Tentar novamente',()=>search({reset:false}),'quiet'));}}
 }
 function turn(step){state.offset=Math.max(0,(state.offset||0)+step);search({reset:false});}
 query.oninput=()=>search({debounce:true});query.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();search();}};
 scope.onchange=language.onchange=sub.onchange=()=>search();
 return {search,dispose:()=>{dead=true;++request;clearTimeout(timer);controller?.abort();zipController?.abort();}};
}
