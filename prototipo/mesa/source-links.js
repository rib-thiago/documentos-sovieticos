import {node as n,asset,label,normalize} from './data.js';
import {editorialRequest as api} from './editorial.js';
function field(env,title,value,multiline=false){const input=n(multiline?'textarea':'input',{'aria-label':title,value:multiline?undefined:value,rows:multiline?4:undefined});input.value=value;return {input,node:n('label',{class:'organization-field'},[n('span',{text:title}),input])};}
export function linkPayload(source,document,pages,notes,existing=null,active=true,projectId=''){
 return existing?{action:'update',id:existing.id,revision:existing.revision,pages,notes,active}:{action:'create',document_id:document,project_id:projectId,source_id:source,pages,notes};
}
export function anchorComparisonRows(before,after){
 const old=new Map((before.anchors||[]).map(a=>[a.id,a])),next=new Map((after.anchors||[]).map(a=>[a.id,a]));
 const describe=a=>a?[{ru:'Russo',pt:'Português',en:'Inglês'}[a.language]||a.language,'Página física '+a.page_number,a.unit_id?'Unidade: '+a.unit_id:'Somente página','Regiões: '+(a.unit_boxes?.length||0),'Revisão da página: '+(a.page_revision??'Não informada'),'Trecho: '+a.quote,a.notes?'Nota: '+a.notes:''].filter(Boolean).join('\n'):'Sem associação';
 const rows=[{field:'Quantidade de trechos associados',before:String(old.size),after:String(next.size)}];
 for(const id of new Set([...old.keys(),...next.keys()]))if(JSON.stringify(old.get(id))!==JSON.stringify(next.get(id)))rows.push({field:!old.has(id)?'Trecho a recuperar / acrescentar':!next.has(id)?'Trecho a retirar':'Trecho a atualizar',before:describe(old.get(id)),after:describe(next.get(id))});
 return rows;
}
async function returnToLinks(env,m){await env.refreshFacsimiles();m.openSourceLinks=true;await env.back(m);}
async function confirmLink(env,m,payload){
 const result=await api('/api/editorial/pdf/links/preview',{body:payload});if(!env.current())return;
 const before=result.before,after=result.after;
 env.preview({backend:true,title:payload.action==='restore'?'Conferir restauração do vínculo e seus trechos':'Conferir vínculo entre documento e PDF',before:'',after:'',propertyRows:[
  ...anchorComparisonRows(before,after),
  {field:'Documento',before:before.document_id,after:after.document_id},
  {field:'Páginas físicas da fonte',before:before.pages.join(', '),after:after.pages.join(', ')},
  {field:'Situação local',before:before.active?'Ativo':'Inativo',after:after.active?'Ativo':'Inativo'},
  {field:'Nota sobre o alcance',before:before.notes||'—',after:after.notes||'—'}],information:[['Contexto',after.project_id?'Projeto '+(env.project?.title||after.project_id):'Acervo local'],['Fonte PDF',after.source_id],['Identificador SHA-256',after.source_sha256],['Limite','Associar páginas não certifica correspondência exata de cada parágrafo. A avaliação do conteúdo é do editor.']],destinationText:'Vínculo local · sem alterar a transcrição',confirmText:'Conferi o documento, as páginas e os trechos associados. Confirmo registrar este estado do vínculo local, sem substituir o texto ou publicar arquivos.',saveLabel:'Salvar vínculo local',effectText:'Atualiza o estado local do vínculo: páginas, notas, situação e trechos associados mostrados na prévia, com histórico. Não altera texto, tradução ou PDF original. Desativar aqui não retira uma preparação do portal já existente; essa retirada tem ação própria.',confirm:async()=>{await api('/api/editorial/pdf/links/save',{body:{preview_id:result.preview_id}});m.linkWork=null;await returnToLinks(env,m);env.toast('Vínculo local salvo com histórico; a transcrição não mudou.');}});
}
export function editSourceLink(env,m,existing=null){
 const key=existing?.id||'new';if(m.linkWork?.key!==key)m.linkWork={key,document:existing?.document_id||'',pages:existing?.pages.join(', ')||String(m.page),notes:existing?.notes||'',revision:existing?.revision||0,active:existing?.active??true};
 const work=m.linkWork,query=field(env,'Localizar documento por título ou ID',work.document),chosen=n('p',{class:'source-link-choice'}),results=n('div',{class:'source-link-matches'}),pages=field(env,'Páginas físicas (ex.: 1-3, 8)',work.pages),notes=field(env,'Nota local de alcance / diferenças (não vai ao portal)',work.notes,true),active=n('input',{type:'checkbox',checked:work.active});
 const store=()=>{work.pages=pages.input.value;work.notes=notes.input.value;work.active=active.checked;env.store();};pages.input.oninput=notes.input.oninput=active.onchange=store;
 function choose(id){work.document=id;const doc=env.catalog.documents.get(id);chosen.textContent=doc?id+' · '+label(doc):'Nenhum documento selecionado';env.store();}
 function search(){results.replaceChildren();const q=normalize(query.input.value.trim());if(q&&!existing)for(const doc of env.catalog.all.filter(d=>(!env.project||env.project.document_ids.includes(d.id))&&normalize(d.id+' '+label(d)).includes(q)).slice(0,20))results.append(env.button(doc.id+' · '+label(doc),()=>{choose(doc.id);results.replaceChildren();},'quiet'));}
 query.input.oninput=()=>{choose('');search();};choose(work.document);if(existing)query.input.readOnly=true;
 const stale=Boolean(existing&&work.revision!==existing.revision);
 const prepare=env.button('Conferir vínculo',async()=>{store();if(!env.catalog.documents.has(work.document)){env.toast('Localize e selecione explicitamente o documento.');return;}try{await confirmLink(env,m,linkPayload(m.backendSource,work.document,work.pages,work.notes,existing,work.active,env.projectId||''));}catch(error){env.toast(error.message);}},'primary');prepare.disabled=!env.canWrite||stale;
 env.panel(existing?'Editar vínculo local':'Vincular PDF a documento existente',[
  n('p',{class:'hint',text:'Use este caminho quando a transcrição já está cadastrada. Selecione o documento e as páginas correspondentes; seu texto não será substituído.'}),stale&&n('p',{class:'backend-warning',text:'O vínculo mudou desde este rascunho. Recarregue os dados salvos antes de conferir outra alteração.'}),stale&&env.button('Recarregar vínculo salvo',()=>{if(confirm('Descartar este rascunho do vínculo e carregar os dados salvos?')){m.linkWork=null;editSourceLink(env,m,existing);}},'quiet'),query.node,chosen,results,pages.node,notes.node,existing&&n('label',{class:'image-option'},[active,' Vínculo ativo no backend local']),prepare
 ]);
}
export async function sourceLinks(env,m){
 try{
  const [response,projection]=await Promise.all([api('/api/editorial/pdf/links?source='+encodeURIComponent(m.backendSource)+'&project='+encodeURIComponent(env.projectId||'')),api('/api/editorial/pdf/publication')]);if(!env.current())return;
  const prepared=new Map(projection.published.map(link=>[link.id,link]));
  env.panel('Documentos e fac-símiles da fonte',[
   n('p',{class:'hint',text:env.projectId?'Os vínculos desta lista pertencem ao projeto. A revisão OCR da fonte continua compartilhada. A publicação de vínculos privados não está disponível.':'Vincular relaciona o PDF ao documento no backend. Preparar para o portal cria arquivos locais selecionados; só chegam ao GitHub Pages após um commit e push autorizado.'}),env.button('Vincular a outro documento',()=>editSourceLink(env,m),'primary'),
   ...response.items.map(link=>n('section',{class:'note-card'},[
    n('strong',{text:link.document_id+' · '+(env.catalog.documents.has(link.document_id)?label(env.catalog.documents.get(link.document_id)):link.document_id)}),
    n('p',{class:'hint',text:'Páginas da fonte: '+link.pages.join(', ')+' · vínculo '+(link.active?'ativo':'inativo')}),
    n('p',{class:'hint',text:prepared.has(link.id)?'Arquivos do portal preparados'+(prepared.get(link.id).revision===link.revision?' para esta revisão.':' para outra revisão; confira antes de atualizar.'):'Disponível somente pelo backend local.'}),link.notes&&n('p',{text:link.notes}),
    env.button('Abrir texto + imagem',()=>env.openDocument(link.document_id,null,'facsimile'),'quiet'),env.button('Editar vínculo',()=>editSourceLink(env,m,link),'quiet'),env.button('Histórico do vínculo',()=>linkHistory(env,m,link),'quiet'),
    !env.projectId&&link.active&&env.button(prepared.has(link.id)?'Atualizar arquivos do portal':'Preparar fac-símile para o portal',()=>preparePublication(env,m,link),'quiet'),
    !env.projectId&&prepared.has(link.id)&&env.button('Conferir retirada do portal',()=>publicationPlan(env,m,{action:'withdraw',link_ids:[link.id]}),'quiet')
   ])),!response.items.length&&n('p',{text:'Nenhum documento vinculado a esta fonte neste contexto.'}),
   !env.projectId&&projection.history.length>0&&env.button('Histórico dos arquivos do portal',()=>publicationHistory(env,m,projection.history),'quiet')
  ]);
 }catch(error){env.toast(error.message);}
}
async function linkHistory(env,m,link){
 try{const response=await api('/api/editorial/pdf/links/'+encodeURIComponent(link.id)+'/history');if(!env.current())return;
  env.panel('Histórico do vínculo local',[n('p',{class:'hint',text:'Restaurar retorna o vínculo ao estado anterior à operação selecionada, com outra confirmação. Não altera o PDF nem desfaz arquivos preparados para o portal.'}),...response.items.map(entry=>n('section',{class:'note-card'},[n('strong',{text:new Date(entry.created_at).toLocaleString('pt-BR')}),n('p',{text:(entry.before_state.active?'Ativo':'Inativo')+' → '+(entry.after_state.active?'Ativo':'Inativo')+' · páginas '+entry.after_state.pages.join(', ')+' · trechos associados: '+(entry.before_state.anchors||[]).length+' → '+(entry.after_state.anchors||[]).length}),env.button('Conferir estado anterior',async()=>{try{await confirmLink(env,m,{action:'restore',id:link.id,revision:link.revision,history_id:entry.id});}catch(error){env.toast(error.message);}},'quiet')]))]);
 }catch(error){env.toast(error.message);}
}
function preparePublication(env,m,link){
 const include=n('input',{type:'checkbox'});
 const prepare=env.button('Preparar prévia dos arquivos',()=>publicationPlan(env,m,{action:'publish',link_ids:[link.id],include_transcription:include.checked},prepare),'primary');prepare.disabled=!env.canWrite;
 env.panel('Preparar fac-símile para o portal',[n('p',{text:'Será gerado um PDF contendo somente as páginas deste vínculo. O PDF original é preservado. A prévia ainda não muda os arquivos públicos locais.'}),n('p',{class:'hint',text:link.document_id+' · páginas '+link.pages.join(', ')}),n('label',{class:'image-option'},[include,' Incluir transcrição das páginas conferidas']),n('p',{class:'hint',text:'Notas locais e histórico não serão incluídos. Deixe desmarcado para disponibilizar só o fac-símile. Incluir a transcrição exige páginas salvas como Conferida ou Em branco; não altera o texto já cadastrado do documento.'}),prepare]);
}
async function publicationPlan(env,m,payload,button=null){
 if(!env.canWrite){env.toast('Escolha Mesa principal para preparar arquivos do portal.');return;}
 const progress=n('p',{class:'hint',role:'status',text:'Preparando a seleção local. PDFs extensos podem levar alguns minutos…'});if(button){button.disabled=true;button.after(progress);}
 try{
  const previous=await api('/api/editorial/pdf/publication');if(!env.current())return;
  const result=await api('/api/editorial/pdf/publication/preview',{body:payload,timeout:420000});if(!env.current())return;
  const withdrawing=payload.action==='withdraw',restoring=payload.action==='restore',remaining=new Set(result.links.map(link=>link.id)),removed=previous.published.filter(link=>!remaining.has(link.id));
  const effect=withdrawing?'Retira a seleção dos arquivos locais do portal. O PDF original e o vínculo de trabalho permanecem. Não altera a publicação remota sem commit e push.':restoring?'Repõe TODO o conjunto de fac-símiles do portal no estado anterior ao registro selecionado, incluindo outras fontes. PDFs originais e vínculos locais não mudam.':'Acrescenta ou atualiza os PDFs selecionados e data/facsimiles.json na cópia local do portal. O original e a transcrição do documento permanecem intactos. Não envia arquivos ao GitHub.';
  env.preview({backend:true,title:withdrawing?'Conferir retirada dos arquivos do portal':restoring?'Conferir restauração do conjunto do portal':'Conferir fac-símile para o portal',before:'',after:'',renderContent:()=>n('section',{class:'review-details'},[
   n('h2',{text:'Efeito local'}),n('p',{text:effect}),n('p',{text:`Fac-símiles no conjunto: ${result.before_count} → ${result.after_count}`}),
   ...result.links.filter(link=>restoring||payload.link_ids.includes(link.id)).map(link=>n('section',{class:'note-card'},[n('strong',{text:link.document_id}),n('p',{text:'Páginas da fonte: '+link.pages.join(', ')}),n('a',{class:'control',href:asset('api/editorial/pdf/publication/'+result.release_id+'/preview.pdf?link='+encodeURIComponent(link.id)),download:'previa-facsimile.pdf',text:'Baixar PDF da prévia'})])),
   removed.length>0&&n('section',{class:'note-card'},[n('strong',{text:'Serão retirados do conjunto do portal'}),...removed.map(link=>n('p',{text:link.document_id+' · páginas '+link.pages.join(', ')}))]),n('h3',{text:'Arquivos que serão acrescentados'}),n('pre',{class:'publication-file-list',text:result.added_files.join('\n')||'Nenhum'}),n('h3',{text:'Arquivos que serão retirados'}),n('pre',{class:'publication-file-list',text:result.removed_files.join('\n')||'Nenhum'})
  ]),destinationText:'Arquivos locais do portal · sem commit ou push',confirmText:restoring?'Confirmo repor TODO o conjunto local de fac-símiles no estado indicado, incluindo outras fontes e a retirada de preparações posteriores.':'Li o efeito e confirmo esta alteração nos arquivos locais do portal, sem envio automático ao GitHub.',saveLabel:withdrawing?'Retirar arquivos locais':restoring?'Restaurar conjunto local':'Gravar arquivos locais do portal',effectText:effect,confirm:async()=>{
   const receipt=await api('/api/editorial/pdf/publication/apply',{body:{release_id:result.release_id,confirm:true}});m.lastPublicationReceipt=receipt;env.store();await returnToLinks(env,m);env.toast('Arquivos locais do portal atualizados com histórico. Nenhum commit ou push foi executado.');
  }});
 }catch(error){env.toast(error.message);}finally{if(button){button.disabled=!env.canWrite;progress.remove();}}
}
function publicationHistory(env,m,entries){
 env.panel('Histórico dos arquivos do portal',[n('p',{class:'backend-warning',text:'Este histórico cobre TODO o conjunto de fac-símiles preparado para o portal, incluindo outras fontes. Restaurar um registro pode retirar preparações posteriores; confira a lista completa antes de confirmar.'}),...entries.map(entry=>n('section',{class:'note-card'},[n('p',{text:new Date(entry.created_at).toLocaleString('pt-BR')}),env.button('Conferir conjunto anterior',()=>publicationPlan(env,m,{action:'restore',history_id:entry.id}),'quiet')]))]);
}
