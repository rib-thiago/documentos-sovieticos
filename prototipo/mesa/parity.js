import {anchorComparisonRows} from './source-links.js';
/* Pontes da Mesa para serviços editoriais existentes; nenhuma publicação implícita. */
import {node as n,asset,label,LANGUAGES,renderMarkdown} from './data.js';
import {editorialRequest as api} from './editorial.js';
import {bodyDigest,checkedPassageRange} from './passage-edit.js';
export {bodyDigest};
export const codePointOffset=(text,offset)=>Array.from(text.slice(0,offset)).length;
export function anchorPayload(link,range,language,hash,page,unit='',notes=''){
 return {action:'anchor',id:link.id,revision:link.revision,anchor:{language,body_sha256:hash,quote:range.expected,start:range.start,end:range.end,page_number:Number(page),notes,...unit?{unit_id:unit}:{}}};
}
function field(title,value='',multi=false){const input=n(multi?'textarea':'input',{'aria-label':title,rows:multi?3:undefined});input.value=value;return {input,node:n('label',{class:'pdf-work-field'},[n('span',{text:title}),input])};}
async function linkConfirmation(env,payload){
 const result=await api('/api/editorial/pdf/links/preview',{body:payload});if(!env.current())return;
 const rows=anchorComparisonRows(result.before,result.after);
 env.preview({backend:true,title:payload.action==='remove_anchor'?'Conferir retirada da associação':'Conferir associação de trecho',before:'',after:'',propertyRows:[{field:'Documento',before:result.before.document_id,after:result.after.document_id},{field:'Fonte PDF',before:result.before.source_id,after:result.after.source_id},...rows],information:[['Contexto',result.after.project_id?'Projeto privado':'Acervo local']],destinationText:result.after.project_id?'Vínculo privado do projeto':'Vínculo local do documento',confirmText:'Conferi o trecho, a fonte e a página. Confirmo alterar somente esta associação, com histórico.',saveLabel:'Salvar associação',effectText:'Preserva o texto, a tradução e o PDF. Registra uma correspondência manual; não confirma automaticamente equivalência histórica e não publica arquivos.',confirm:async()=>{await api('/api/editorial/pdf/links/save',{body:{preview_id:result.preview_id}});await env.saved();}});
}
// Traduz o intervalo Markdown salvo para texto visível sem escolher frases repetidas por aproximação.
export function associatedTextRange(body,anchor,blockStart,blockEnd,visible,renderText){
 if(anchor.start<blockStart||anchor.end>blockEnd||body.slice(anchor.start,anchor.end)!==anchor.quote)return null;
 if(anchor.start===blockStart&&anchor.end===blockEnd)return {start:0,end:visible.length};
 let marker='MESAFACSIMILE7391';while(body.includes(marker)||visible.includes(marker))marker+='X';
 const marked=body.slice(blockStart,anchor.start)+marker+body.slice(anchor.end,blockEnd),display=renderText(marked),offset=display.indexOf(marker);
 if(offset<0||display.indexOf(marker,offset+marker.length)>=0||display.slice(0,offset)+anchor.quote+display.slice(offset+marker.length)!==visible)return null;
 return {start:offset,end:offset+anchor.quote.length};
}
export async function associatePassage(env,m,passage){
 try{
  const rendered=m.renderedBodies?.[passage.lang];if(!rendered||rendered.format==='text')throw Error('Abra uma versão Markdown para associar um trecho.');
  const response=await api('/api/editorial/pdf/links?'+new URLSearchParams({document:m.doc.id,project:m.projectId||''}));if(!env.current())return;
  const links=response.items.filter(l=>l.active);if(!links.length)throw Error('Primeiro abra a fonte PDF → Ferramentas → Vincular a documento existente, no mesmo contexto deste documento.');
  const range=checkedPassageRange(rendered.body,passage.sourceStart,passage.sourceEnd,passage,raw=>{const host=n('div');host.innerHTML=renderMarkdown(raw);return host.firstElementChild?.textContent??host.textContent;});
  const hash=await bodyDigest(rendered.body);if(!env.current())return;
  associationForm(env,m,links,range,passage.lang,hash);
 }catch(error){env.toast(error.message);}
}
export function storedAssociationRange(body,anchor,hash){
 if(hash!==anchor.body_sha256||!Number.isInteger(anchor.start)||!Number.isInteger(anchor.end)||anchor.start<0||anchor.end<=anchor.start||anchor.end>body.length||body.slice(anchor.start,anchor.end)!==anchor.quote)return null;
 return {start:anchor.start,end:anchor.end,expected:anchor.quote,exact:true};
}
export async function editAssociation(env,m,linkId,anchorId){
 try{
  const response=await api('/api/editorial/pdf/links?'+new URLSearchParams({document:m.doc.id,project:m.projectId||''}));if(!env.current())return;
  const link=response.items.find(l=>l.id===linkId&&l.active),anchor=link?.anchors.find(a=>a.id===anchorId);
  if(!anchor)throw Error('A associação não está mais ativa. Reabra a lista para conferir seu histórico.');
  const data=await env.body(anchor.language),hash=await bodyDigest(data.body);if(!env.current())return;
  const range=storedAssociationRange(data.body,anchor,hash);
  if(!range){env.dialog('Texto da associação alterado',[n('p',{text:'O texto mudou desde esta associação. Para evitar ligar a frase errada ou criar uma duplicação, selecione o trecho atual no documento e crie uma nova associação. A anterior permanece recuperável e pode ser retirada pela lista.'}),n('blockquote',{text:anchor.quote}),env.button('Abrir texto e página',()=>{env.closeDialog();env.openAnchor(link,anchor);},'quiet')]);return;}
  associationForm(env,m,[link],range,anchor.language,hash,anchor);
 }catch(error){env.toast(error.message);}
}
function associationForm(env,m,links,range,language,hash,existing=null){
 const source=env.select(links.map(l=>[l.id,l.source_title||l.source_id]),links[0].id,()=>load(),'Fonte PDF'),page=env.select([],null,()=>loadUnits(),'Página física'),unit=env.select([['','Somente página']], '',()=>{save.disabled=unit.value==='@missing';},'Unidade revisada'),notes=field('Nota da associação',existing?.notes||'',true),notice=n('p',{class:'hint',role:'status'});let serial=0;
 const selected=()=>links.find(l=>l.id===source.value);
 async function loadUnits(){const version=++serial;unit.replaceChildren(n('option',{value:'',text:'Somente página'}));save.disabled=true;
  try{const data=await api('/api/editorial/pdf/'+selected().source_id+'/pages/'+page.value+'/geometry');if(version!==serial||!env.current())return;
   for(const u of data.units)unit.append(n('option',{value:u.id,text:Array.from(data.text).slice(u.start,u.end).join('').slice(0,90)+(u.boxes?.length?' · '+u.boxes.length+' região(ões)':' · sem região')}));
   const previous=existing&&Number(page.value)===existing.page_number?existing.unit_id:null;
   if(previous){if(data.units.some(u=>u.id===previous))unit.value=previous;else{unit.append(n('option',{value:'@missing',text:'Unidade anterior removida — escolha outra',disabled:true}));unit.value='@missing';}}
   notice.textContent=unit.value==='@missing'?'A unidade anterior foi dividida ou unida. Escolha explicitamente a unidade atual ou Somente página.':'Confira a página e a unidade. Salvar atualiza a revisão e os retângulos desta associação.';save.disabled=unit.value==='@missing';
  }catch(error){if(version!==serial||!env.current())return;notice.textContent='Unidades indisponíveis: '+error.message;
   if(existing?.unit_id){unit.append(n('option',{value:'@missing',text:'Unidade não conferida — escolha Somente página para removê-la',disabled:true}));unit.value='@missing';save.disabled=true;}else save.disabled=false;
  }
 }
 function load(){page.replaceChildren(...selected().pages.map(p=>n('option',{value:p,text:'Página física '+p})));if(existing&&selected().pages.includes(existing.page_number))page.value=existing.page_number;loadUnits();}
 const save=env.button(existing?'Conferir atualização':'Conferir associação',async()=>{if(unit.value==='@missing')return;save.disabled=true;try{await linkConfirmation(env,anchorPayload(selected(),range,language,hash,page.value,unit.value,notes.input.value));}catch(error){notice.textContent=error.message;}finally{save.disabled=unit.value==='@missing';}},'primary');
 const labeled=(title,input)=>n('label',{class:'pdf-work-field'},[n('span',{text:title}),input]);
 env.dialog(existing?'Editar / reconfirmar associação':'Associar trecho ao fac-símile',[n('section',{class:'passage-association'},[
  n('section',{class:'association-excerpt'},[n('h3',{text:(existing?'Trecho associado · ':'Trecho selecionado · ')+LANGUAGES[language]}),n('p',{text:existing?'Atualize página, unidade ou nota. A frase e a fonte deste vínculo são preservadas; salvar reconfirma a revisão atual.':range.exact?'Frase selecionada com posição exata no Markdown.':'A seleção cruza formatação ou não é unívoca. Será associado o bloco Markdown completo mostrado abaixo; confira antes de continuar.'}),n('blockquote',{text:range.expected})]),
  n('section',{class:'association-destination'},[labeled('Fonte PDF',source),n('div',{class:'association-page-unit'},[labeled('Página física',page),labeled('Unidade revisada (opcional)',unit)]),notice,notes.node]),n('footer',{class:'association-footer'},[save])
 ])]);load();
}

export async function documentAssociations(env,m,links){
 const hashes=new Map();for(const language of new Set(links.flatMap(l=>(l.anchors||[]).map(a=>a.language)))){try{const data=await env.body(language);hashes.set(language,await bodyDigest(data.body));}catch{hashes.set(language,null);}if(!env.current())return;}
 const entries=links.flatMap(link=>(link.anchors||[]).map(anchor=>({link,anchor:{...anchor,stale_text:anchor.stale_text||hashes.get(anchor.language)!==anchor.body_sha256}})));
 env.panel('Trechos e fac-símiles',[n('p',{class:'hint',text:'Selecione uma frase no texto e use Associar ao PDF. As regiões são delimitadas na revisão da página da fonte.'}),...entries.map(({link,anchor:a})=>n('section',{class:'note-card'},[
  n('strong',{text:LANGUAGES[a.language]+' · página física '+a.page_number+(a.printed_label?' · foliação '+a.printed_label:'')}),n('blockquote',{text:a.quote}),n('p',{class:'hint',text:link.source_title||link.source_id}),
  (a.stale_text||a.stale_page)&&n('p',{class:'backend-warning',text:'Reconfirmar: '+[a.stale_text?'texto alterado':'',a.stale_page?'revisão da página alterada':''].filter(Boolean).join(' e ')+'. A região não será destacada enquanto esta associação estiver desatualizada.'}),
  env.button('Abrir página associada',()=>env.openAnchor(link,a),'quiet'),link.local&&env.button('Editar / reconfirmar associação',()=>editAssociation(env,m,link.id,a.id),'quiet'),link.local&&env.button('Editar regiões no PDF',()=>env.openRegions(link,a),'quiet'),link.local&&env.button('Retirar associação',async()=>{try{await linkConfirmation(env,{action:'remove_anchor',id:link.id,revision:link.revision,anchor_id:a.id});}catch(error){env.toast(error.message);}},'quiet')
 ])),!entries.length&&n('p',{text:'Ainda não há trechos associados neste contexto.'})]);
}
function alignmentPreview(result,source,page){
 const operation={boxes:'Localização de regiões na imagem',split:'Divisão de uma unidade',merge:'União de unidades'}[result.structure.action];
 const shell=n('section',{class:'review-details'},[n('h2',{text:operation}),n('p',{text:'A transcrição não mudou. Você está confirmando '+(result.structure.action==='boxes'?'as regiões destacadas na imagem.':'a organização das unidades textuais.')}),n('p',{class:'hint',text:'Página física '+page+' · alterações com histórico; PDF original preservado.'})]),columns=n('div',{class:'alignment-preview-columns'});
 for(const [title,state,ids]of [['Antes',result.before,result.structure.before],['Proposta',result.after,result.structure.after]]){
  const selected=state.units.filter(u=>ids.includes(u.id)),picture=n('div',{class:'alignment-picture'}),layer=n('div',{class:'alignment-regions'});
  picture.append(n('img',{src:asset('api/editorial/pdf/'+source+'/pages/'+page+'/image.png'),alt:title+' · página física '+page}),layer);
  for(const unit of selected)for(const [x,y,w,h]of unit.boxes||[]){const box=n('span');box.style.cssText=`left:${x*100}%;top:${y*100}%;width:${w*100}%;height:${h*100}%`;layer.append(box);}
  columns.append(n('section',{},[n('h3',{text:title}),n('p',{text:selected.length+' unidade(s) · '+selected.reduce((sum,u)=>sum+(u.boxes?.length||0),0)+' região(ões)'}),picture,...selected.map(u=>n('div',{class:'note-card'},[n('strong',{text:u.id}),n('p',{text:Array.from(state.text).slice(u.start,u.end).join('')})]))]));
 }
 shell.append(columns);return shell;
}
// Velocidade de rolagem proporcional à proximidade da borda visível.
export function regionScrollSpeed(position,lower,upper){
 const band=Math.min(64,(upper-lower)/3);
 if(band<=0)return 0;
 if(position<lower+band)return -Math.min(1,(lower+band-position)/band)*720;
 if(position>upper-band)return Math.min(1,(position-upper+band)/band)*720;
 return 0;
}
export async function alignPage(env,m){
 try{
  const source=m.backendSource,page=m.page,data=await api('/api/editorial/pdf/'+source+'/pages/'+page+'/geometry');if(!env.current())return;
  const missingUnit=Boolean(m.regionUnitId&&!data.units.some(u=>u.id===m.regionUnitId));
  const units=env.select([...(missingUnit?[['','Unidade anterior removida — escolha a unidade atual']]:[]),...data.units.map(u=>[u.id,u.id+' · '+Array.from(data.text).slice(u.start,u.end).join('').slice(0,55)])],missingUnit?'':m.regionUnitId||data.units[0]?.id||'',()=>choose(),'Unidade revisada'),text=n('textarea',{readonly:true,rows:7,'aria-label':'Texto da unidade; posicione o cursor para dividir'}),picture=n('div',{class:'alignment-picture'}),image=n('img',{src:asset('api/editorial/pdf/'+source+'/pages/'+page+'/image.png'),alt:'Página física '+page}),layer=n('div',{class:'alignment-regions'}),notice=n('p',{role:'status',class:'hint'});if(missingUnit)notice.textContent='A unidade anterior não existe mais. Escolha a unidade atual antes de marcar regiões.';picture.append(image,layer);let boxes=[],start=null,busy=false,pointer=null,scrollFrame=0,lastFrame=0;
  const unit=()=>data.units.find(u=>u.id===units.value);
  function draw(draft=null){layer.replaceChildren(...[...boxes,...draft?[draft]:[]].map(([x,y,w,h],index)=>{const box=n('span',{class:index===boxes.length?'region-drawing':''});box.style.cssText=`left:${x*100}%;top:${y*100}%;width:${w*100}%;height:${h*100}%`;return box;}));}
  function choose(){const u=unit();text.value=u?Array.from(data.text).slice(u.start,u.end).join(''):'';boxes=(u?.boxes||[]).map(b=>[...b]);draw();}choose();
  const point=e=>{const rect=image.getBoundingClientRect();return [Math.max(0,Math.min(1,(e.clientX-rect.left)/rect.width)),Math.max(0,Math.min(1,(e.clientY-rect.top)/rect.height))];};
  const scroller=n('section',{class:'alignment-image-scroll',tabindex:0,'aria-label':'Página: role para percorrer a imagem ou arraste junto à borda para continuar um retângulo'},[picture]);
  function stopDrawing(){start=null;pointer=null;cancelAnimationFrame(scrollFrame);scrollFrame=0;lastFrame=0;draw();}
  function followEdge(time){
   scrollFrame=0;
   if(!start||!pointer||!picture.isConnected||!picture.closest('dialog')?.open){stopDrawing();return;}
   const rect=scroller.getBoundingClientRect(),dt=Math.min(40,lastFrame?time-lastFrame:16)/1000;lastFrame=time;
   scroller.scrollTop+=regionScrollSpeed(pointer.clientY,rect.top,rect.bottom)*dt;
   scroller.scrollLeft+=regionScrollSpeed(pointer.clientX,rect.left,rect.right)*dt;
   draw(rectangle(point(pointer)));scrollFrame=requestAnimationFrame(followEdge);
  }
  picture.onpointerdown=e=>{if(e.button!==0||busy||!image.naturalWidth||!unit())return;start=point(e);pointer={clientX:e.clientX,clientY:e.clientY};picture.setPointerCapture(e.pointerId);scrollFrame=requestAnimationFrame(followEdge);e.preventDefault();};
  const rectangle=end=>[Math.min(start[0],end[0]),Math.min(start[1],end[1]),Math.abs(end[0]-start[0]),Math.abs(end[1]-start[1])];
  picture.onpointermove=e=>{if(start){pointer={clientX:e.clientX,clientY:e.clientY};draw(rectangle(point(pointer)));}};
  scroller.addEventListener('scroll',()=>{if(start&&pointer)draw(rectangle(point(pointer)));},{passive:true});
  picture.onpointerup=e=>{if(!start)return;const box=rectangle(point(e));if(box[2]>.003&&box[3]>.003&&boxes.length<16)boxes.push(box);stopDrawing();};picture.onpointercancel=picture.onlostpointercapture=stopDrawing;
  image.onerror=()=>notice.textContent='Imagem indisponível; confira o processamento da fonte antes de delimitar regiões.';
  async function prepare(action,extra={}){if(busy||!unit())return;busy=true;notice.textContent='Preparando prévia…';try{const result=await api('/api/editorial/pdf/alignment/preview',{body:{source_id:source,page_number:page,revision:data.revision,unit_id:unit().id,action,...extra}});if(!env.current())return;
   env.preview({backend:true,title:(action==='boxes'?'Conferir regiões da imagem':'Conferir organização do texto')+' · página '+page,before:result.before.text,after:result.after.text,renderContent:()=>alignmentPreview(result,source,page),information:[['Operação',result.diff],['Estrutura',JSON.stringify(result.structure)],['Unidades após a alteração',JSON.stringify(result.after.units)]],destinationText:'Revisão compartilhada da fonte PDF',confirmText:action==='boxes'?'Confirmo salvar as regiões desta unidade na imagem, preservando a transcrição e o PDF original.':'Confirmo reorganizar as unidades, preservando integralmente o texto e o PDF original.',saveLabel:action==='boxes'?'Salvar regiões da unidade':'Salvar organização do texto',effectText:'Registra histórico da revisão. Dividir ou unir cria unidades com proveniência, sem inventar regiões. Associações anteriores podem precisar de reconferência.',confirm:async()=>{await api('/api/editorial/pdf/review/save',{body:{preview_id:result.preview_id}});await env.saved();}});
  }catch(error){notice.textContent=error.message;}finally{busy=false;}}
  const split=env.button('Dividir no cursor',()=>prepare('split',{offset:codePointOffset(text.value,text.selectionStart)}),'quiet'),merge=env.button('Unir à seguinte',()=>prepare('merge'),'quiet');
  function updateMerge(){merge.disabled=!unit()||data.units.indexOf(unit())===data.units.length-1;merge.title=merge.disabled?'Não há unidade seguinte para unir.':'Reúne esta unidade com a próxima, preservando o texto.';}
  units.onchange=()=>{choose();updateMerge();};updateMerge();
  const textPanel=n('section',{id:'alignment-text-panel',class:'alignment-task alignment-text-task',role:'tabpanel','aria-labelledby':'alignment-text-tab'},[
   n('p',{class:'alignment-instruction',text:'Clique entre duas palavras para dividir este bloco. Unir reúne a unidade escolhida com a seguinte. As palavras permanecem iguais.'}),text,
   n('footer',{class:'alignment-task-footer'},[n('p',{text:'Dividir ou unir abre uma prévia. As novas unidades precisam ter suas regiões delimitadas novamente.'}),n('div',{class:'alignment-text-actions'},[split,merge])])
  ]);
  const regionPanel=n('section',{id:'alignment-region-panel',class:'alignment-task alignment-region-task',role:'tabpanel','aria-labelledby':'alignment-region-tab',hidden:true},[
   n('div',{class:'alignment-region-toolbar'},[n('p',{class:'alignment-instruction',text:'Arraste para marcar. Ao chegar à borda, mantenha pressionado: a imagem rola para continuar o desenho.'}),n('div',{class:'alignment-region-actions'},[
    env.button('Desfazer retângulo',()=>{boxes.pop();draw();},'quiet'),
    env.button('Limpar regiões',()=>{boxes=[];draw();},'quiet'),
    env.button('Conferir regiões',()=>prepare('boxes',{boxes}),'primary')
   ])]),scroller
  ]);
  const panels=[textPanel,regionPanel],tabbar=n('div',{class:'alignment-task-tabs',role:'tablist','aria-label':'Tarefa sobre a página'}),tabs=[];
  function showTask(index){if(start)stopDrawing();panels.forEach((panel,i)=>panel.hidden=i!==index);tabs.forEach((tab,i)=>{tab.setAttribute('aria-selected',String(i===index));tab.tabIndex=i===index?0:-1;});}
  for(const [index,title]of ['Organizar texto','Marcar regiões'].entries()){
   const tab=env.button(title,()=>showTask(index),'alignment-task-tab');tab.id=index?'alignment-region-tab':'alignment-text-tab';tab.setAttribute('role','tab');tab.setAttribute('aria-controls',panels[index].id);
   tab.onkeydown=event=>{let next;if(event.key==='ArrowRight'||event.key==='ArrowLeft')next=1-index;else if(event.key==='Home')next=0;else if(event.key==='End')next=1;else return;event.preventDefault();showTask(next);tabs[next].focus();};tabs.push(tab);tabbar.append(tab);
  }
  showTask(m.regionTask==='regions'?1:0);delete m.regionTask;delete m.regionUnitId;
  env.dialog('Unidades e regiões da página',[n('section',{class:'alignment-workspace alignment-tabbed'},[
   tabbar,n('label',{class:'alignment-unit-picker'},[n('span',{text:'Unidade em trabalho · '+data.units.length+' nesta página'}),units]),textPanel,regionPanel,notice
  ])]);
 }catch(error){env.toast(error.message);}
}
export async function printDocument(env,m){
 try{const data=await env.body(m.lang);if(!env.current())return;
  const frame=n('iframe',{class:'mesa-print-frame',title:'Prévia de impressão do documento'}),caption=(data.body!==window.splitExportHeaders(data.source||'').body?'Rascunho da sessão · ':'')+(m.projectId?'Versão privada do projeto '+m.project.title:'Acervo local · versão no idioma selecionado'),title=label(m.doc);
  // srcdoc is built with DOM text nodes for metadata and sanitized Markdown for the body.
  const doc=document.implementation.createHTMLDocument(title);doc.documentElement.lang=m.lang;
  doc.head.append(n('style',{text:'body{font:12pt/1.6 Georgia,serif;color:#161616;margin:1.5cm auto;max-width:19cm;padding:0 1cm}h1{font-size:22pt;line-height:1.2}h2,h3{break-after:avoid}p,li{orphans:3;widows:3}table{border-collapse:collapse;width:100%}td,th{border:1px solid #aaa;padding:.3em}img{max-width:100%}pre{white-space:pre-wrap}header{border-bottom:1px solid #aaa;margin-bottom:1.5em;font:10pt/1.5 sans-serif}a{color:inherit}@page{margin:18mm}@media print{body{max-width:none;margin:0;padding:0}}'}));
  const body=n('article');body.innerHTML=renderMarkdown(data.body,data.edition.format);doc.body.append(n('header',{},[n('h1',{text:title}),n('p',{text:m.doc.id+' · '+LANGUAGES[m.lang]}),n('p',{text:caption}),m.doc.source_url&&n('p',{text:'Fonte da transcrição: '+m.doc.source_url}),n('p',{text:'Originais, traduções e arquivos permanecem preservados.'})]),body);
  frame.srcdoc='<!doctype html>'+doc.documentElement.outerHTML;
  const print=env.button('Imprimir / salvar como PDF',()=>{frame.contentWindow.focus();frame.contentWindow.print();},'primary');print.disabled=true;frame.onload=()=>print.disabled=false;
  env.dialog('Impressão do documento',[n('section',{class:'mesa-print-preview'},[n('p',{class:'hint',text:caption+' A impressão usa o idioma atual; a comparação em colunas continua disponível na Mesa.'}),print,frame])]);
 }catch(error){env.toast(error.message);}
}
