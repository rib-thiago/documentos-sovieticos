import {sourceLinks,editSourceLink} from './source-links.js';
import {pdfParts,pdfPartsJobs,imagePreparation,describeImageRecipe} from './preparation.js';
import {menuGroup,installSplitter,zoomControls} from './controls.js';
import {node as n,action as b,asset,download} from './data.js';
import {editorialRequest as api,collectionSlug} from './editorial.js';
import {upload} from '../estudio/api.js';
import {mountPdf,openPdf} from './pdf.js';
const statusNames={queued:'Na fila',running:'Processando',completed:'Concluído',completed_with_errors:'Concluído com erros',failed:'Falhou',interrupted:'Interrompido'};
const pageStates=[['pending','Pendente'],['reviewed','Conferida'],['problem','Com problema'],['blank','Em branco']];
const name=s=>s.metadata?.title||s.filename;
export const sourceFile=id=>'api/editorial/pdf/'+encodeURIComponent(id)+'/file';
const base=id=>'/api/editorial/pdf/'+encodeURIComponent(id);
function field(env,title,value='',multiline=false){const input=n(multiline?'textarea':'input',{'aria-label':title,type:multiline?undefined:'text',rows:multiline?4:undefined});input.value=value;return {input,node:n('label',{class:'pdf-work-field'},[n('span',{text:title}),input])};}
function choice(env,title,values,value,onchange=()=>{}){const input=env.select(values,value,onchange,title);return {input,node:n('label',{class:'pdf-work-field'},[n('span',{text:title}),input])};}
function picker(env,tree,parent='',child=''){
 const root=choice(env,'Coleção',tree.map(c=>[c.id,c.titles.pt||c.id]),parent||tree[0]?.id||''),sub=choice(env,'Subcoleção',[['','Nenhuma']],child);
 const update=()=>{const selected=tree.find(c=>c.id===root.input.value);sub.input.replaceChildren(n('option',{value:'',text:'Nenhuma'}),...(selected?.children||[]).map(c=>n('option',{value:c.id,text:c.titles.pt||c.id})));};root.input.onchange=update;update();sub.input.value=child;
 return {node:n('div',{class:'pdf-task-grid'},[root.node,sub.node]),root:root.input,child:sub.input,ids:()=>[root.input.value,...sub.input.value?[sub.input.value]:[]]};
}
export async function sourcesView(env){
 const shell=n('section',{class:'organization-page'},[env.heading('Fontes de trabalho','PDFs e transcrições','Cadastrar uma fonte preserva o PDF localmente. O inventário extrai texto pesquisável; OCR gera candidatos separados. Publicar um documento exige outra confirmação.')]),toolbar=n('div',{class:'sources-actions'}),list=n('div',{class:'source-library'}),query=n('input',{type:'search',class:'organization-search',placeholder:'Localizar fonte cadastrada…','aria-label':'Buscar fonte PDF'});shell.append(toolbar,query,list);env.content.append(shell);
 const choose=env.button('Cadastrar PDF',()=>{const input=n('input',{type:'file',accept:'.pdf,application/pdf'});input.onchange=()=>{const file=input.files[0];if(!file)return;env.dialog('Cadastrar fonte PDF local',[n('p',{text:`${file.name} · ${(file.size/1024/1024).toFixed(1)} MiB. O original será preservado, o processamento nativo começa automaticamente e nenhum documento é publicado por este cadastro.`}),env.button('Confirmar envio',async event=>{const button=event.currentTarget;button.disabled=true;try{const result=await upload(file,env.projectId||'',percent=>env.toast('Enviando PDF · '+percent+'%'));if(env.current()){env.closeDialog();await env.open(result.source_id);}if(result.warning)env.toast(result.warning);else env.toast(result.duplicate?'Esta fonte já estava cadastrada; a cópia existente foi aberta.':'PDF cadastrado. Inventário e extração nativa iniciados.');}catch(error){env.toast(error.message);button.disabled=false;}},'primary')]);};input.click();},'primary');choose.disabled=!env.canWrite;
 toolbar.append(choose,n('span',{class:'hint',text:env.project?'Projeto: '+env.project.title+' · revisão OCR compartilhada':'Sem projeto ativo · fonte local de trabalho'}));
 const response=await api('/api/editorial/pdf/sources?light=1');if(!env.current())return;
 const draw=()=>{list.replaceChildren();const q=query.value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();for(const source of response.items.filter(s=>(!env.project||env.project.source_ids.includes(s.id))&&name(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().includes(q)))list.append(n('article',{class:'source-card'},[n('div',{},[n('p',{class:'eyebrow',text:statusNames[source.state]||source.state}),n('h2',{text:name(source)}),n('p',{class:'hint',text:`${source.page_count??'…'} páginas · ${source.confirmed?'Ficha cadastrada':'Ficha pendente'}`})]),env.button('Abrir revisão',()=>env.open(source.id),'quiet')]));if(!list.childElementCount)list.append(n('p',{text:'Nenhuma fonte encontrada. Use Cadastrar PDF para começar.'}));};query.oninput=draw;draw();
}
export async function sourceView(env,m){
 let dead=false,timer,renderCleanup=()=>{},snapshot=null,overview=null,info=null,mounted=false;
 const alive=()=>!dead&&env.current();
 const area=n('section',{class:'review-grid'}),image=n('div',{class:'pdf-stage'}),pane=n('section',{class:'transcript'}),textarea=n('textarea',{'aria-label':'Transcrição revisada da página',spellcheck:false,placeholder:'Aguardando o inventário da página…'}),status=n('p',{class:'transcript-status'}),candidateHost=n('div',{class:'source-candidates'}),note=n('p',{class:'source-review-note'});
 const treated=n('img',{class:'prepared-page-image',alt:'Derivado tratado da página para comparação'}),modeHost=n('div',{class:'prepared-image-toggle'});image.append(treated);
 function redrawImage(){for(const button of modeHost.children){const active=button.textContent===(m.showPreparedImage?'Tratada':'Original');button.classList.toggle('active',active);button.classList.toggle('quiet',!active);button.setAttribute('aria-pressed',String(active));}const show=Boolean(m.showPreparedImage&&m.imagePreparation?.source_id===m.backendSource&&m.imagePreparation?.source_sha256===info?.sha256&&m.imagePreparation?.page_number===m.page);image.classList.toggle('show-prepared-image',show);if(show){const url=asset(m.imagePreparation.url);if(treated.src!==url)treated.src=url;const base=m.pageViewport;const scale=typeof m.zoom==='number'?m.zoom:m.zoom==='width'?(image.clientWidth-32)/(base?.width||612):Math.min((image.clientWidth-32)/(base?.width||612),(image.clientHeight-32)/(base?.height||792));m.effectiveZoom=scale;treated.style.width=(base?.width||612)*Math.max(.1,Math.min(3,scale))+'px';}else renderCleanup.refresh?.();}
 const imagePane=n('section',{class:'pdf-image-pane'},[n('div',{class:'image-zoom-bar'},[modeHost,zoomControls(m,redrawImage,env.store)]),image]);area.append(imagePane,pane);installSplitter(area,m,env.store);pane.append(status,candidateHost,textarea,note);env.content.append(area);
 const pageInput=n('input',{type:'number',min:1,value:m.page||1,class:'review-page-input','aria-label':'Página física da fonte'}),total=n('span',{text:'/ …'}),phase=n('span',{class:'source-phase',text:'Consultando fonte…'});
 const turn=page=>{if(!Number.isInteger(page)||page<1||m.count&&page>m.count)return;env.remember();m.page=page;env.rerender();};pageInput.onchange=()=>turn(Number(pageInput.value));
 const save=env.button('Conferir página',async()=>{try{const work=working();if(!snapshot)throw Error('Aguarde o inventário desta página.');const result=await api('/api/editorial/pdf/review/preview',{body:{source_id:m.backendSource,page_number:m.page,revision:snapshot.revision,review:work.review}});if(!alive())return;
  env.preview({backend:true,title:'Conferir revisão · página '+m.page,before:result.before.text,after:result.after.text,proposal:{markdown_edit:{diff:{text:result.diff}},changes:[]},destinationText:'Revisão local da fonte',confirmText:'Confirmo salvar esta revisão da página. O PDF e a extração bruta permanecem preservados; nenhum documento é publicado.',saveLabel:'Salvar revisão da página',effectText:'Altera somente a revisão local desta página, com histórico. Não altera o PDF, a extração original, o catálogo ou uma transcrição já incorporada.',information:[['Estado',pageStates.find(([v])=>v===work.review.status)?.[1]],['Foliação impressa',work.review.printed_label||'Não informada'],['Notas da revisão',work.review.notes||'—']],confirm:async()=>{await api('/api/editorial/pdf/review/save',{body:{preview_id:result.preview_id}});delete m.backendDrafts?.[m.page];m.capture=null;await env.back(m);env.toast('Revisão da página salva localmente, com histórico.');}});
 }catch(error){env.toast(error.message);}},'primary');save.disabled=true;
 env.controls.replaceChildren(...(m.associationReturn?[env.button('Voltar à associação',()=>env.backToAssociation(),'quiet')]:[]),env.button('‹',()=>turn((m.page||1)-1),'quiet'),pageInput,total,env.button('›',()=>turn((m.page||1)+1),'quiet'),phase,save,env.button('PDFs derivados',()=>pdfPartsJobs(env,m),'quiet'),env.button('Ferramentas',()=>tools(),'quiet'));
 function working(){const base=m.backendDrafts?.[m.page]?.review||snapshot.review;return {revision:snapshot.revision,raw_sha256:snapshot.raw.text_sha256,review:{text:textarea.value,status:base.status,printed_label:base.printed_label||'',notes:base.notes||'',basis:base.basis}};}
 function capture(){if(!snapshot)return;const work=working(),old=snapshot.review;if(JSON.stringify(work.review)!==JSON.stringify({text:old.text,status:old.status,printed_label:old.printed_label,notes:old.notes,basis:old.basis})){m.backendDrafts||={};m.backendDrafts[m.page]=work;}else if(m.backendDrafts)delete m.backendDrafts[m.page];}
 textarea.oninput=()=>{capture();env.store();};
 function candidates(){
  candidateHost.replaceChildren();if(!snapshot)return;
  const selected=m.backendDrafts?.[m.page]?.review?.basis||snapshot.review.basis;
  const select=env.select([['native','Texto pesquisável original'],...snapshot.candidates.map((c,i)=>[c.id,`Candidato OCR ${snapshot.candidates.length-i} · ${new Date(c.created_at).toLocaleString('pt-BR')}`])],selected,code=>{
   const previousBasis=working().review.basis;const text=code==='native'?snapshot.raw.raw_text:snapshot.candidates.find(c=>c.id===code)?.raw_text;
   if(text===undefined)return;
   if(textarea.value.trim()&&textarea.value!==text&&!confirm('Usar este candidato no lugar do texto em edição? A versão salva no backend permanece no histórico; o rascunho atual será preservado na sessão.')){select.value=previousBasis;return;}
   if(m.backendDrafts?.[m.page]){m.backendRecoveries||={};m.backendRecoveries[m.page]=m.backendDrafts[m.page];}
   m.backendDrafts||={};m.backendDrafts[m.page]={...working(),review:{...working().review,text,basis:code,status:'pending'}};textarea.value=text;reviewState.value='pending';capture();env.store();note.textContent='Candidato adotado no rascunho. Confira contra a imagem antes de marcar como Conferida.';
  },'Base da transcrição');candidateHost.append(select,env.button('Baixar extração bruta',()=>download(m.backendSource+'-p'+m.page+'.bruto.txt',snapshot.raw.raw_text,'text/plain;charset=utf-8'),'quiet'));
 }
 const reviewState=env.select(pageStates,'pending',value=>{if(!snapshot)return;const draft=working();draft.review.status=value;m.backendDrafts||={};m.backendDrafts[m.page]=draft;capture();env.store();},'Estado da revisão');
 pane.append(n('div',{class:'source-review-state'},[n('span',{text:'Estado da página'}),reviewState]));
 async function load(){
  info=await api(base(m.backendSource));if(!alive())return;
  m.pdfUrl=sourceFile(m.backendSource);m.title=name(info);env.updated?.();m.count=info.page_count||m.count;total.textContent='/ '+(m.count||'…');pageInput.max=m.count||1;
  phase.title=env.project?'Projeto: '+env.project.title+' · revisão OCR compartilhada':'';phase.textContent='Inventário: '+(statusNames[info.state]||info.state)+` · ${info.processed}/${info.page_count??'…'} páginas`;
  if(!mounted){mounted=true;renderCleanup=mountPdf(m,image,async count=>{total.textContent='/ '+count;pageInput.max=count;try{const page=await (await openPdf(m)).getPage(m.page);m.pageViewport=page.getViewport({scale:1});if(m.showPreparedImage&&m.imagePreparation?.source_id===m.backendSource&&m.imagePreparation?.source_sha256===info?.sha256&&m.imagePreparation?.page_number===m.page){redrawImage();}}catch{}},error=>env.toast(error.message));}
  if(info.pages.some(page=>page.page_number===m.page)){
   const fresh=await api(base(m.backendSource)+'/pages/'+m.page+'/review');if(!alive())return;const changedCandidates=!snapshot||snapshot.candidates.map(c=>c.id).join()!==fresh.candidates.map(c=>c.id).join();
   if(!snapshot){snapshot=fresh;let pending=m.backendDrafts?.[m.page];if(pending&&(pending.revision!==fresh.revision||pending.raw_sha256!==fresh.raw.text_sha256)){m.backendRecoveries||={};m.backendRecoveries[m.page]=pending;delete m.backendDrafts[m.page];pending=null;env.toast('Há um rascunho de outra revisão preservado para download. A página atual não foi substituída.');}
    textarea.value=pending?.review.text??fresh.review.text;reviewState.value=pending?.review.status??fresh.review.status;m.capture=capture;
   }else{snapshot.candidates=fresh.candidates;}
   if(changedCandidates||!candidateHost.childElementCount)candidates();status.textContent=`Página física ${m.page} · ${snapshot.raw.reason||snapshot.raw.diagnosis} · revisão ${snapshot.revision}`;save.disabled=!env.canWrite;textarea.disabled=false;
   note.textContent=working().review.basis!=='native'?'Base: candidato OCR adotado. Confira a transcrição contra a imagem.':snapshot.raw.raw_text.trim()?'Texto pesquisável extraído sem OCR. Revise contra a imagem.':'Sem texto pesquisável nesta página. Use Ferramentas → Configurar OCR para gerar candidatos.';
  }else{status.textContent='O inventário ainda não alcançou esta página.';textarea.disabled=true;note.textContent=info.error||'Você pode consultar a imagem enquanto a extração nativa avança.';}
  modeHost.replaceChildren();if(m.imagePreparation?.source_id===m.backendSource&&m.imagePreparation?.source_sha256===info?.sha256&&m.imagePreparation?.page_number===m.page){for(const [value,title]of [[false,'Original'],[true,'Tratada']])modeHost.append(env.button(title,()=>{m.showPreparedImage=value;redrawImage();env.store();},m.showPreparedImage===value?'active':'quiet'));}
  overview=await api(base(m.backendSource)+'/review');if(!alive())return;
  const active=overview.jobs.filter(job=>['queued','running'].includes(job.state));if(active.length)phase.textContent+=' · OCR em andamento';
  if(info.state==='queued'||info.state==='running'||active.length)timer=setTimeout(()=>load().catch(error=>{if(alive()){env.toast(error.message);timer=setTimeout(()=>load().catch(()=>{}),5000);}}),3000);
 }
 function jobs(){
  env.panel('Processamento OCR',[
   ...((overview?.jobs)||[]).map(job=>n('div',{class:'note-card'},[
    n('strong',{text:statusNames[job.state]||job.state}),n('p',{text:`${job.completed_pages.length}/${job.recipe.pages.length} páginas · ${job.recipe.languages.join(' + ')} · ${job.recipe.dpi} DPI`}),
    job.error&&n('p',{class:'backend-warning',text:job.error}),
    ['failed','interrupted'].includes(job.state)&&env.button('Retomar lote OCR',async()=>{try{if(!env.canWrite)throw Error('Escolha Mesa principal para retomar OCR.');await api('/api/editorial/pdf/ocr/resume',{body:{job_id:job.id}});env.rerender();}catch(error){env.toast(error.message);}},'quiet')
   ])),!(overview?.jobs?.length)&&n('p',{text:'Nenhum lote OCR iniciado nesta fonte.'}),env.button('Atualizar processamento',()=>env.rerender(),'quiet')
  ]);
 }
 function pageDetails(){
  if(!snapshot){env.toast('Aguarde o inventário desta página.');return;}
  const current=working(),printed=field(env,'Página impressa / foliação',current.review.printed_label),notes=field(env,'Notas da revisão',current.review.notes,true);
  const update=()=>{const draft=working();draft.review.printed_label=printed.input.value;draft.review.notes=notes.input.value;m.backendDrafts||={};m.backendDrafts[m.page]=draft;env.store();};printed.input.oninput=update;notes.input.oninput=update;
  env.panel('Foliação e notas',[printed.node,notes.node,n('p',{class:'hint',text:'As informações entram na mesma prévia de Conferir página, junto com a transcrição e o estado de revisão.'})]);
 }
 function tools(){if(env.togglePanel?.('Fonte PDF e revisão'))return;env.panel('Fonte PDF e revisão',[
  n('p',{class:'menu-context',text:m.title}),env.project&&n('p',{class:'hint',text:'Projeto: '+env.project.title+'. Revisão OCR compartilhada; derivados e vínculos usam este projeto.'}),
  menuGroup('Revisar',[
   {title:'Páginas e progresso',description:'Escolher a página física e consultar o inventário.',run:()=>pageNavigator(env,m,info)},
   {title:'Unidades e regiões da página',description:'Dividir ou unir blocos e delimitar regiões na imagem.',run:()=>{capture();if(m.backendDrafts?.[m.page]){env.toast('Salve ou descarte a edição da página antes de alterar suas unidades.');return;}env.alignPage();}},
   {title:'Foliação e notas',description:'Rótulo impresso e observações desta página.',run:pageDetails},
   {title:'Histórico da página',description:'Revisões salvas e restauração com prévia.',run:()=>reviewHistory(env,m,snapshot)},
   {title:'Atualizar candidatos',description:'Consultar resultados sem executar outro lote.',run:()=>env.rerender()}
  ]),
  menuGroup('Preparar fonte',[
   {title:'Extrair ou dividir PDF',description:'Criar derivados, preservando o original.',run:()=>pdfParts(env,m,info)},
   {title:'Derivados e processamento',description:'Abrir partes geradas e retomar operações.',run:()=>pdfPartsJobs(env,m)},
   {title:'Preparar imagem',description:'Comparar um PNG tratado e guardar a receita para OCR.',run:()=>imagePreparation(env,m)}
  ]),
  menuGroup('OCR e fonte',[
   {title:'Configurar OCR',description:'Páginas, idiomas e resolução do próximo lote.',run:()=>ocrTask(env,m,info)},
   {title:'Processamento OCR',description:'Acompanhar lotes e retomar os interrompidos.',run:jobs},
   {title:'Ficha da fonte',description:'Coleção, idioma, origem e referência.',run:()=>classifyTask(env,m,info)},
   info&&['failed','interrupted','completed_with_errors'].includes(info.state)&&{title:'Retomar inventário',description:'Continuar a extração nativa da fonte.',run:async()=>{if(!env.canWrite)throw Error('Escolha Mesa principal.');await api('/api/editorial/pdf/action',{body:{action:'resume',source_id:m.backendSource}});env.rerender();}}
  ]),
  menuGroup('Incorporar e preservar',[
   {title:'Vincular a documento existente',description:'Associar páginas sem substituir a transcrição cadastrada.',run:()=>editSourceLink(env,m)},
   {title:'Documentos e fac-símiles',description:'Vínculos locais, preparação do portal e históricos.',run:()=>sourceLinks(env,m)},
   {title:'Criar documento',description:'Incorporar páginas conferidas ao acervo local.',run:()=>incorporationTask(env,m,info)},
   {title:'Documentos e recibos',description:'Consultar incorporações e vínculos pendentes.',run:()=>incorporationReceipts(env,m)},
   {title:'Baixar PDF original',description:'Preservar uma cópia da fonte enviada.',download:true,run:()=>{const link=n('a',{href:asset(sourceFile(m.backendSource))+'?download=1',download:''});link.click();}},
   m.backendRecoveries?.[m.page]&&{title:'Baixar rascunho preservado',description:'Recuperar o texto de outra revisão da página.',download:true,run:()=>download(m.backendSource+'-p'+m.page+'.rascunho.json',JSON.stringify(m.backendRecoveries[m.page],null,2),'application/json')}
  ])
 ]);}

 await load();
 if(m.openRegionEditor&&alive()){delete m.openRegionEditor;if(m.backendDrafts?.[m.page])env.toast('Há uma edição da página em andamento. Salve-a antes de revisar as regiões.');else await env.alignPage();}
 if(m.openSourceLinks&&alive()){delete m.openSourceLinks;sourceLinks(env,m);}
 if(m.openPdfDerivatives&&alive()){delete m.openPdfDerivatives;pdfPartsJobs(env,m);}
 return ()=>{dead=true;clearTimeout(timer);renderCleanup();if(m.capture===capture)m.capture=null;};
}
function pageNavigator(env,m,info){
 env.panel('Páginas da fonte',[
  n('p',{class:'hint',text:'Escolha uma página física. O estado de revisão é salvo apenas após conferência.'}),
  n('div',{class:'source-page-grid'},(info?.pages||[]).map(page=>env.button(String(page.page_number),()=>{env.remember();m.page=page.page_number;env.rerender();},page.page_number===m.page?'active':'quiet')))
 ]);
}
async function ocrTask(env,m,info){
 try{const capability=await api('/api/editorial/pdf/capabilities');if(!env.current())return;
  if(!capability.ocr.available){env.panel('OCR indisponível',[n('p',{text:capability.ocr.installation||'Instale o renderizador e o Tesseract com os modelos de idioma.'}),n('p',{text:'O original, as revisões e a extração nativa permanecem disponíveis.'})]);return;}
  const pages=field(env,'Páginas físicas (por exemplo 1-3, 8)',String(m.page)),dpi=choice(env,'Resolução',[[150,'150 DPI'],[200,'200 DPI'],[300,'300 DPI']],300),psm=choice(env,'Disposição do texto',[[3,'Automático'],[6,'Um bloco de texto']],3),checks=[];
  const languages=n('fieldset',{class:'ocr-languages'},[n('legend',{text:'Idiomas do OCR'})]);
  for(const [code,title]of [['rus','Russo'],['eng','Inglês'],['por','Português']]){const input=n('input',{type:'checkbox',checked:code==='rus'&&capability.ocr.languages.includes(code),disabled:!capability.ocr.languages.includes(code)});checks.push([code,input]);languages.append(n('label',{},[input,n('span',{text:title+(input.disabled?' · modelo ausente':'')})]));}
  const useImage=n('input',{type:'checkbox'}),prepared=m.imagePreparation?.source_id===m.backendSource&&m.imagePreparation?.source_sha256===info?.sha256?m.imagePreparation:null;useImage.disabled=!prepared;useImage.onchange=()=>{if(useImage.checked){dpi.input.value=prepared.dpi;dpi.input.disabled=true;}else dpi.input.disabled=false;};
  const prepare=env.button('Conferir lote OCR',async()=>{try{const result=await api('/api/editorial/pdf/ocr/preview',{body:{source_id:m.backendSource,pages:pages.input.value,languages:checks.filter(([,input])=>input.checked).map(([code])=>code),dpi:Number(dpi.input.value),psm:Number(psm.input.value),...(useImage.checked?{image_recipe:prepared.recipe}:{})}});if(!env.current())return;
    env.preview({backend:true,title:'Conferir processamento OCR',before:'',after:'',propertyRows:[{field:'Páginas físicas',before:'Sem OCR novo',after:result.recipe.pages.join(', ')},{field:'Idiomas',before:'—',after:result.recipe.languages.join(' + ')},{field:'Resolução',before:'—',after:result.recipe.dpi+' DPI'},{field:'Texto revisado',before:'Preservado',after:'Preservado; resultados serão candidatos separados'},...(useImage.checked?[{field:'Tratamento da imagem',before:'Original',after:describeImageRecipe(prepared.recipe)}]:[])],proposal:{changes:[]},destinationText:'Processamento local',confirmText:'Confirmo executar este lote OCR local. O texto revisado não será substituído automaticamente.',saveLabel:'Executar OCR local',effectText:'Gera candidatos de texto por página. Não substitui a revisão, não cria documento no catálogo e não publica o PDF.',confirm:async()=>{const resultJob=await api('/api/editorial/pdf/ocr/start',{body:{preview_id:result.preview_id}});await env.back(m);env.toast('OCR adicionado à fila: '+resultJob.job_id);}});
  }catch(error){env.toast(error.message);}},'primary');prepare.disabled=!env.canWrite;
  env.panel('Configurar OCR',[n('p',{class:'hint',text:'Até 50 páginas por lote. Use OCR nas páginas sem camada textual ou quando a extração nativa precisar de outra tentativa.'}),pages.node,languages,n('label',{class:'image-option'},[useImage,n('span',{text:prepared?'Usar o tratamento preparado, no mesmo DPI. A receita será aplicada a todas as páginas deste lote.':'Prepare uma imagem antes de habilitar tratamento no OCR.'})]),dpi.node,psm.node,prepare]);
 }catch(error){env.toast(error.message);}
}
async function reviewHistory(env,m,snapshot){
 if(!snapshot){env.toast('Aguarde o inventário desta página.');return;}
 env.panel('Histórico da revisão',[
  n('p',{text:'A extração bruta é preservada; restaurar cria uma nova revisão.'}),
  ...(snapshot.history||[]).map(entry=>env.button('Restaurar versão de '+new Date(entry.created_at).toLocaleString('pt-BR'),async()=>{try{const result=await api('/api/editorial/pdf/review/preview',{body:{source_id:m.backendSource,page_number:m.page,revision:snapshot.revision,history_id:entry.id}});env.preview({backend:true,title:'Restaurar revisão da página '+m.page,before:result.before.text,after:result.after.text,proposal:{markdown_edit:{diff:{text:result.diff}},changes:[]},destinationText:'Revisão local da fonte',confirmText:'Confirmo restaurar esta revisão da página, preservando o histórico.',saveLabel:'Restaurar revisão',confirm:async()=>{await api('/api/editorial/pdf/review/save',{body:{preview_id:result.preview_id}});delete m.backendDrafts?.[m.page];await env.back(m);}});}catch(error){env.toast(error.message);}},'quiet')),
  !snapshot.history.length&&n('p',{text:'A primeira gravação inicia o histórico.'})
 ]);
}
async function classifyTask(env,m,info){
 if(!info)return;
 const response=await api('/api/collections');if(!env.current())return;const metadata=info.metadata||{},title=field(env,'Título da fonte',metadata.title||info.filename),url=field(env,'URL de origem',metadata.source_url||''),archive=field(env,'Referência arquivística',metadata.archive_reference||''),lang=choice(env,'Idioma da fonte',[['ru','Russo'],['en','Inglês'],['pt','Português'],['mixed','Vários idiomas']],metadata.language||'ru'),collections=picker(env,response.items,metadata.collection_id,metadata.subcollection_id);
 const prepare=env.button('Conferir ficha da fonte',()=>{const value={title:title.input.value,collection_id:collections.root.value,subcollection_id:collections.child.value,language:lang.input.value,source_url:url.input.value,archive_reference:archive.input.value};env.preview({backend:true,title:'Conferir classificação da fonte PDF',before:'',after:'',propertyRows:Object.entries(value).map(([field,after])=>({field,before:metadata[field]||'—',after})),proposal:{changes:[]},destinationText:'Ficha local da fonte',confirmText:'Confirmo guardar a classificação desta fonte local com histórico. Nenhum documento será publicado.',saveLabel:'Salvar ficha da fonte',effectText:'Atualiza apenas a ficha local do PDF e seu histórico. Não cadastra documento nem publica o PDF.',confirm:async()=>{await api('/api/editorial/pdf/action',{body:{action:'confirm',source_id:m.backendSource,revision:info.revision,metadata:value}});await env.back(m);}});},'primary');prepare.disabled=!env.canWrite;
 env.panel('Ficha da fonte',[title.node,collections.node,lang.node,url.node,archive.node,prepare]);
}
async function incorporationTask(env,m,info){
 if(!info)return;
 const response=await api('/api/collections');if(!env.current())return;
 const work=m.incorporationWork||={title:name(info),id:'',pages:String(m.page),language:info.metadata.language==='mixed'?'ru':info.metadata.language||'ru',collection:info.metadata.collection_id||'',subcollection:info.metadata.subcollection_id||''};
 const title=field(env,'Título do novo documento',work.title),id=field(env,'Identificador novo (sem acentos)',work.id),pages=field(env,'Páginas conferidas a incorporar',work.pages),language=choice(env,'Idioma do original',[['ru','Russo'],['pt','Português'],['en','Inglês']],work.language),collections=picker(env,response.items,work.collection,work.subcollection);
 if(!work.id)id.input.value=collectionSlug(work.title);
 const store=()=>{Object.assign(work,{title:title.input.value,id:id.input.value,pages:pages.input.value,language:language.input.value,collection:collections.root.value,subcollection:collections.child.value});env.store();};
 const prepare=env.button('Conferir novo documento',async()=>{store();try{
  const result=await api('/api/editorial/pdf/incorporation/preview',{body:{source_id:m.backendSource,pages:work.pages,mode:'create',document_id:work.id,language:work.language,project_id:'',metadata:{title:work.title,title_pt:work.language==='pt'?work.title:'',collection_ids:collections.ids(),date:''}}});if(!env.current())return;
  env.preview({backend:true,title:'Conferir incorporação · '+result.document_id,before:'',after:result.content,proposal:{markdown_edit:{diff:result.diff},changes:[],requires_acknowledgement:Boolean(result.warnings.length)},information:[['Documento novo',result.document_id],['Idioma',result.language],['Páginas físicas',result.provenance.pages.map(p=>p.page_number).join(', ')],['Fonte SHA-256',result.provenance.source_sha256],...result.warnings.map(text=>['Aviso',text])],ackText:'Li os avisos em Informações e confirmo a criação do documento e seu idioma.',destinationText:'Acervo local · novo documento',confirmText:'Confirmo criar este documento no acervo local a partir das páginas conferidas, com proveniência. Não haverá publicação automática.',saveLabel:'Criar documento no acervo',effectText:'Cria um documento e sua transcrição, atualiza catálogo, manifesto e busca e registra as páginas/unidades da fonte. Não substitui um documento existente.',confirm:async()=>{
    const receipt=await api('/api/editorial/pdf/incorporation/save',{body:{preview_id:result.preview_id,confirm_replace:false,acknowledge_warnings:env.acknowledged()}});m.incorporationWork=null;await env.incorporated(m,receipt,result.language);
  }});
 }catch(error){env.toast(error.message);}},'primary');prepare.disabled=!env.canWrite;
 const box=n('div',{class:'pdf-incorporation-form'},[n('p',{class:'hint',text:'Somente páginas salvas como Conferida ou Em branco podem ser incorporadas. Esta ação cria um documento novo; não substitui os já existentes.'}),title.node,id.node,pages.node,language.node,collections.node,prepare]);box.addEventListener('input',store);box.addEventListener('change',store);env.panel('Criar documento da revisão', [box]);
}

async function incorporationReceipts(env,m){
 try{const response=await api(base(m.backendSource)+'/incorporations');if(!env.current())return;env.panel('Incorporações da fonte',[
  n('p',{text:'Confira os recibos antes de repetir uma operação interrompida. Um vínculo pendente pode ser concluído sem criar outro documento.'}),
  ...response.items.map(item=>n('div',{class:'note-card'},[
    n('strong',{text:item.data.document_id}),n('p',{class:'hint',text:new Date(item.created_at).toLocaleString('pt-BR')+' · '+item.state}),item.error&&n('p',{class:'backend-warning',text:item.error}),
    ['saved','completed','prepared'].includes(item.state)&&env.button('Abrir documento',()=>env.openDocument(item.data.document_id,item.data.language),'quiet'),
    ['saved','prepared'].includes(item.state)&&env.button('Concluir vínculo',async()=>{try{if(!env.canWrite)throw Error('Escolha Mesa principal.');await api('/api/editorial/pdf/incorporation/finish',{body:{receipt_id:item.id}});delete m.pendingIncorporation;env.store();incorporationReceipts(env,m);}catch(error){env.toast(error.message);}},'quiet')
  ])),!response.items.length&&n('p',{text:'Nenhuma incorporação registrada nesta fonte.'})
 ]);}catch(error){env.toast(error.message);}
}
