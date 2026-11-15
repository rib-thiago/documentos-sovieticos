import {node as n,LANGUAGES,renderMarkdown,download} from './data.js';
import {editorialRequest as api} from './editorial.js';
const bodyOf=snapshot=>window.splitExportHeaders(snapshot.content).body;
export async function bodyDigest(body){const hash=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(body));return Array.from(new Uint8Array(hash),b=>b.toString(16).padStart(2,'0')).join('');}
export function passageRange(body,start,end,quote){
 if(!Number.isInteger(start)||!Number.isInteger(end)||start<0||end>body.length||end<=start)throw Error('O bloco não tem um intervalo Markdown válido. Use o editor completo.');
 const block=body.slice(start,end),offset=quote?block.indexOf(quote):-1;
 if(offset>=0&&block.indexOf(quote,offset+1)<0)return {start:start+offset,end:start+offset+quote.length,expected:quote,exact:true};
 return {start,end,expected:block,exact:false};
}
export function checkedPassageRange(body,start,end,passage,renderText){
 const range=passageRange(body,start,end,passage.quote);if(!range.exact)return range;
 const marker='MESASELECAOEXATA7391',block=body.slice(start,end),test=block.slice(0,range.start-start)+marker+block.slice(range.end-start),display=passage.renderedBlockText;
 if(typeof display!=='string'||display.slice(passage.start,passage.end)!==passage.quote||renderText(test)!==display.slice(0,passage.start)+marker+display.slice(passage.end))return {start,end,expected:block,exact:false};
 return range;
}
export function passagePayload(snapshot,body,work){return {revision:snapshot.revision,edition_id:snapshot.edition.id,content_sha256:snapshot.edition.sha256,start:Array.from(body.slice(0,work.start)).length,end:Array.from(body.slice(0,work.end)).length,expected:work.expected,replacement:work.replacement};}
async function snapshotFor(m,language){return api(m.projectId?'/api/editorial/workspace/edition?'+new URLSearchParams({project:m.projectId,edition:m.doc.id+':'+language}):'/api/editorial/editions/'+encodeURIComponent(m.doc.id+':'+language));}
export async function beginPassageEdit(env,m,passage){
 try{
  const rendered=m.renderedBodies?.[passage.lang];if(!rendered||rendered.format==='text')throw Error('Esta versão não tem um mapa Markdown editável. Use Editar Markdown.');
  const pendingKey=(m.projectId||'acervo')+':'+m.doc.id+':'+passage.lang;if(m.buffers?.[pendingKey]!==undefined)throw Error('Há uma edição Markdown em andamento neste idioma. Salve ou descarte essa edição antes de corrigir um trecho.');
  const snapshot=await snapshotFor(m,passage.lang);if(!env.current())return;
  const doc=snapshot.document,original=doc.source_metadata?.original_language||'ru';
  if(!['pt','en'].includes(passage.lang)||passage.lang===original)throw Error('A correção por trecho aceita traduções; o original permanece protegido.');
  if(snapshot.archived)throw Error('Reabra o projeto antes de corrigir sua tradução.');
  const body=bodyOf(snapshot);if(body!==rendered.body)throw Error('A versão exibida difere da versão salva. Reabra o documento ou conclua o rascunho antes de corrigir este trecho.');
  const range=checkedPassageRange(body,passage.sourceStart,passage.sourceEnd,passage,raw=>{const node=document.createElement('div');node.innerHTML=renderMarkdown(raw);return node.firstElementChild?.textContent??node.textContent;}),work={...range,language:passage.lang,replacement:range.expected,quote:passage.quote,body_sha256:await bodyDigest(body),content_sha256:m.projectId?snapshot.content_sha256:snapshot.edition.sha256,edition_revision:m.projectId?snapshot.revision:null,returnMode:m.mode};
  if(!env.current())return;
  if(m.passageWork&&m.passageWork.replacement!==m.passageWork.expected){
   if(m.passageWork.language===work.language&&m.passageWork.start===work.start&&m.passageWork.expected===work.expected){env.openPassage(m);return;}
   if(!confirm('Há outra correção de trecho não salva nesta aba. Substituir esse rascunho pela nova seleção?'))return;
  }
  m.passageWork=work;env.openPassage(m);
 }catch(error){env.toast(error.message);}
}
export async function mountPassageEditor(env,m){
 const work=m.passageWork;if(!work){env.returnPassage(m);return;}
 env.controls.replaceChildren(env.button('Voltar ao documento',()=>env.returnPassage(m),'quiet'),n('span',{class:'passage-destination',text:LANGUAGES[work.language]+' · '+(m.projectId?'versão privada':'tradução do acervo')}));
 const shell=n('section',{class:'passage-edit-workspace'}),status=n('p',{class:'passage-edit-status',role:'status'});env.content.append(shell);
 try{
  const snapshot=await snapshotFor(m,work.language);if(!env.current())return;
  const body=bodyOf(snapshot),hash=m.projectId?snapshot.content_sha256:snapshot.edition.sha256;
  if(snapshot.archived)throw Error('O projeto foi arquivado. A correção em andamento foi preservada; reabra o projeto para gravar.');
  if(hash!==work.content_sha256||(m.projectId&&snapshot.revision!==work.edition_revision)||await bodyDigest(body)!==work.body_sha256||body.slice(work.start,work.end)!==work.expected)throw Error('A versão mudou desde a seleção. Sua correção foi preservada. Exporte o rascunho e selecione o trecho novamente na versão atual.');
  const input=n('textarea',{class:'plain-editor','aria-label':'Correção do trecho em Markdown',spellcheck:false}),preview=n('article',{class:'edition-body passage-rendered'}),left=n('section',{class:'editor-pane code-host'}),right=n('section',{class:'editor-preview'});input.value=work.replacement;left.append(input);right.append(preview);
  shell.append(n('header',{class:'passage-edit-heading'},[n('h1',{text:'Corrigir tradução · '+LANGUAGES[work.language]}),n('p',{text:m.doc.id+' · '+(work.exact?'Somente a frase selecionada':'Bloco Markdown completo: a seleção cruza formatação ou se repete; confira o bloco inteiro antes de alterar.')}),n('p',{class:'hint',text:m.projectId?'A correção será salva somente no projeto.':'A confirmação atualizará esta tradução no acervo local, com histórico. Original e outras versões permanecem iguais.'})]),n('div',{class:'editor-grid passage-edit-grid'},[left,right]),status);
  const render=value=>{work.replacement=value;preview.innerHTML=renderMarkdown(value);env.store();};input.oninput=()=>render(input.value);preview.innerHTML=renderMarkdown(work.replacement);
  const save=env.button('Conferir correção',async()=>{
   if(!work.replacement.trim()){status.textContent='O trecho não pode ficar vazio.';return;}
   save.disabled=true;status.textContent='Preparando a prévia; nada foi salvo.';
   try{
    const prefix=snapshot.content.slice(0,snapshot.content.length-body.length),content=prefix+body.slice(0,work.start)+work.replacement+body.slice(work.end);
    const result=await api(m.projectId?'/api/editorial/workspace/preview':'/api/editorial/passages/preview',{body:m.projectId?{project_id:m.projectId,edition_id:snapshot.edition_id,revision:snapshot.revision,content_sha256:snapshot.content_sha256,content}:passagePayload(snapshot,body,work)});if(!env.current())return;
    env.preview({backend:true,title:'Conferir correção de tradução',before:work.expected,after:work.replacement,proposal:{...result,markdown_edit:{diff:result.passage_edit?.diff||result.diff}},destinationText:m.projectId?'Projeto privado · correção de trecho':'Acervo local · correção de tradução',confirmText:m.projectId?'Confirmo corrigir este trecho somente na versão privada do projeto.':'Confirmo corrigir este trecho da tradução no acervo local, com histórico, sem alterar o original ou outras versões.',saveLabel:m.projectId?'Salvar correção privada':'Salvar correção da tradução',effectText:m.projectId?'Substitui somente o intervalo indicado na versão privada, preservando todo o conteúdo fora dele. O acervo permanece intacto.':'Substitui somente o intervalo indicado na tradução, preservando todo o conteúdo fora dele; atualiza catálogo, manifesto e busca com histórico. Nenhum commit ou push é executado.',confirm:async()=>{const receipt=await api(m.projectId?'/api/editorial/workspace/save':'/api/editorial/save',{body:m.projectId?{preview_id:result.preview_id}:{preview_id:result.preview_id,acknowledge_warnings:false}});m.lastPassageReceipt=receipt;env.store();await env.finishPassage(m);}});
   }catch(error){status.textContent=error.message;}finally{if(env.current())save.disabled=false;}
  },'primary');env.controls.append(save);
  try{const lib=await import('../oficina/vendor/libraries.js');if(!env.current())return;const editor=new lib.EditorView({doc:work.replacement,extensions:[lib.basicSetup,lib.markdown(),lib.EditorView.updateListener.of(update=>{if(update.docChanged)render(update.state.doc.toString());})],parent:left});input.remove();env.setPassageEditor(editor);return ()=>{env.setPassageEditor(null);editor.destroy();};}catch{status.textContent='Editor simples disponível; prévia e confirmação continuam funcionando.';}
 }catch(error){shell.replaceChildren(n('div',{class:'page-shell'},[n('h1',{text:'Correção preservada'}),n('p',{text:error.message}),env.button('Exportar rascunho da correção',()=>download(m.doc.id+'-correcao.json',JSON.stringify(work,null,2),'application/json'),'quiet'),env.button('Voltar ao documento',()=>env.returnPassage(m),'quiet')]));}
}
