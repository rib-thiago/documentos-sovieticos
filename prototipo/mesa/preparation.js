import {node as n,asset,download} from './data.js';
import {editorialRequest as api} from './editorial.js';
const initialRecipe={grayscale:true,contrast:false,threshold:null,resize:100,erosion:0};
function input(title,value,type='text'){const field=n('input',{type,'aria-label':title,value});return {input:field,node:n('label',{class:'pdf-work-field'},[n('span',{text:title}),field])};}
function select(env,title,options,value){const field=env.select(options,value,()=>{},title);return {input:field,node:n('label',{class:'pdf-work-field'},[n('span',{text:title}),field])};}
export function pdfParts(env,m,info){
 const mode=select(env,'Operação',[['extract','Extrair páginas em um PDF'],['size','Dividir por quantidade de páginas'],['ranges','Dividir por intervalos']],m.pdfPartsWork?.mode||'extract'),pages=input('Páginas físicas (1-3, 8)',m.pdfPartsWork?.pages||String(m.page)),size=input('Páginas por parte',m.pdfPartsWork?.size||Math.max(1,Math.min(10,(info.page_count||2)-1)),'number'),ranges=input('Partes separadas por ponto e vírgula',m.pdfPartsWork?.ranges||(info.page_count>=4?'1-2; 3-4':info.page_count>=2?'1; 2':'1'));size.input.min=1;
 const update=()=>{pages.node.hidden=mode.input.value!=='extract';size.node.hidden=mode.input.value!=='size';ranges.node.hidden=mode.input.value!=='ranges';};mode.input.onchange=update;update();
 const prepare=env.button('Conferir PDFs derivados',async()=>{try{
  m.pdfPartsWork={mode:mode.input.value,pages:pages.input.value,size:Number(size.input.value),ranges:ranges.input.value};env.store();
  const result=await api('/api/editorial/pdf/operations/preview',{body:{source_id:m.backendSource,project_id:env.projectId||'',mode:mode.input.value==='extract'?'extract':'split',pages:pages.input.value,split_mode:mode.input.value==='extract'?'size':mode.input.value,pages_per_part:Number(size.input.value),ranges:ranges.input.value}});if(!env.current())return;
  env.preview({backend:true,title:'Conferir extração/divisão do PDF',before:'',after:'',proposal:{changes:[]},propertyRows:[{field:'Fonte original',before:info.filename,after:'Preservada integralmente'},{field:'Páginas escolhidas',before:String(info.page_count),after:String(result.recipe.selected_pages)},{field:'Páginas fora dos derivados',before:'—',after:String(result.recipe.omitted_pages)},...result.outputs.map(part=>({field:part.filename,before:'Não gerado',after:'Páginas físicas: '+part.pages.join(', ')}))],destinationText:env.project?'Derivados vinculados a '+env.project.title:'Fontes locais derivadas',confirmText:'Confirmo gerar estes PDFs derivados, preservando o original e registrando a origem das páginas.',saveLabel:'Gerar PDFs derivados',effectText:'Cria fontes locais novas com SHA-256 e mapa de páginas de origem. Não modifica o original nem cria documentos no catálogo.',confirm:async()=>{const job=await api('/api/editorial/pdf/operations/start',{body:{preview_id:result.preview_id}});m.lastPdfOperation=job.id;m.openPdfDerivatives=true;await env.back(m);env.toast('Operação iniciada. Os PDFs aparecerão aqui com o comando Abrir derivado.');}});
 }catch(error){env.toast(error.message);}},'primary');prepare.disabled=!env.canWrite;
 env.panel('Extrair ou dividir PDF',[n('p',{class:'hint',text:'O original não é cortado nem substituído. Cada resultado é cadastrado como outra fonte de trabalho.'}),mode.node,pages.node,size.node,ranges.node,prepare,env.button('Derivados e processamento',()=>pdfPartsJobs(env,m),'quiet')]);
}
export async function pdfPartsJobs(env,m){
 const list=n('div'),notice=n('p',{class:'hint',text:'Consultando PDFs derivados…'});
 let busy=false;
 async function refresh(){
  if(busy||!env.current()||!list.isConnected||list.closest('[hidden]'))return;
  busy=true;
  try{const response=await api('/api/editorial/pdf/operations?source_id='+encodeURIComponent(m.backendSource)+(env.projectId?'&project_id='+encodeURIComponent(env.projectId):''));if(!env.current()||!list.isConnected)return;
   response.items=response.items.filter(job=>(job.project_id||'')===(env.projectId||''));
   const pending=response.items.some(job=>['queued','running','generated'].includes(job.state));
   notice.textContent=pending?'Processando. Esta lista se atualiza automaticamente; abra uma parte assim que estiver cadastrada.':'Resultados locais. Abrir derivado acrescenta o PDF como outra aba da Mesa.';
   list.replaceChildren(...response.items.map(job=>n('section',{class:'note-card'},[
    n('strong',{text:({queued:'Na fila',running:'Processando',generated:'Gerados; cadastrando',completed:'Concluído',failed:'Falhou',interrupted:'Interrompido'})[job.state]||job.state}),n('p',{text:`${job.registered}/${job.outputs.length} fontes cadastradas`}),job.error&&n('p',{class:'backend-warning',text:job.error}),job.warning&&n('p',{class:'backend-warning',text:job.warning}),
    ...job.outputs.map(part=>n('div',{class:'derived-pdf-part'},[n('p',{text:part.title}),n('p',{class:'hint',text:'Páginas originais: '+part.pages.join(', ')}),part.result_source_id?env.button('Abrir derivado',()=>env.open(part.result_source_id),'primary'):n('p',{class:'hint',text:'Aguardando geração e cadastro…'})])),
    (['failed','interrupted'].includes(job.state)||job.warning)&&env.button('Retomar operação',async()=>{try{if(!env.canWrite)throw Error('Escolha Mesa principal.');await api('/api/editorial/pdf/operations/resume',{body:{operation_id:job.id}});refresh();}catch(error){env.toast(error.message);}},'quiet')
   ])),!response.items.length&&n('p',{text:'Nenhuma extração/divisão executada nesta fonte.'}));
   if(pending)setTimeout(refresh,2500);
  }catch(error){notice.textContent=error.message;}finally{busy=false;}
 }
 env.panel('Derivados e processamento',[notice,list,env.button('Atualizar andamento',refresh,'quiet')]);await refresh();
}
export function imagePreparation(env,m){
 const previous=m.imagePreparation,recipe=previous?.recipe||initialRecipe;
 const gray=n('input',{type:'checkbox',checked:recipe.grayscale}),contrast=n('input',{type:'checkbox',checked:recipe.contrast}),thresholdOn=n('input',{type:'checkbox',checked:recipe.threshold!==null}),threshold=input('Limiar preto/branco (0–255)',recipe.threshold??160,'number'),dpi=select(env,'Resolução da prévia e do OCR',[[150,'150 DPI'],[200,'200 DPI'],[300,'300 DPI']],previous?.dpi||300),resize=select(env,'Escala do derivado',[[50,'50%'],[75,'75%'],[100,'100%'],[125,'125%'],[150,'150%']],recipe.resize),erosion=select(env,'Erosão morfológica',[[0,'Não aplicar'],[1,'Erosão de 1 pixel']],recipe.erosion),notice=n('p',{class:'hint'});
 threshold.input.min=0;threshold.input.max=255;threshold.node.hidden=!thresholdOn.checked;thresholdOn.onchange=()=>threshold.node.hidden=!thresholdOn.checked;
 const prepare=env.button('Preparar e visualizar imagem',async()=>{
  prepare.disabled=true;notice.textContent='Renderizando e preparando derivado local…';const page=m.page;
  try{const value={grayscale:gray.checked,contrast:contrast.checked,threshold:thresholdOn.checked?Number(threshold.input.value):null,resize:Number(resize.input.value),erosion:Number(erosion.input.value)};
   const result=await api('/api/editorial/pdf/image/preview',{body:{source_id:m.backendSource,page_number:page,dpi:Number(dpi.input.value),recipe:value}});if(!env.current())return;
   m.imagePreparation=result;m.showPreparedImage=true;env.store();await env.back(m);env.toast('Derivado exibido. Compare com Original; aplicar ao OCR exige escolher essa opção na configuração do lote.');
  }catch(error){notice.textContent=error.message;}finally{prepare.disabled=false;}
 },'primary');prepare.disabled=!env.canWrite;
 env.panel('Preparar imagem',[n('p',{class:'hint',text:'Cinza, contraste, limiar, escala e erosão criam um PNG derivado. Não há recorte ou rotação; os eixos da página são preservados.'}),n('label',{class:'image-option'},[gray,' Escala de cinza']),n('label',{class:'image-option'},[contrast,' Normalizar contraste']),n('label',{class:'image-option'},[thresholdOn,' Aplicar limiar preto/branco']),threshold.node,dpi.node,resize.node,erosion.node,notice,prepare,
  previous&&env.button('Baixar PNG tratado',()=>{const link=n('a',{href:asset(previous.url),download:m.backendSource+'-p'+previous.page_number+'.png'});link.click();},'quiet'),
  previous&&env.button('Baixar receita e proveniência',()=>download(previous.image_id+'.json',JSON.stringify(previous,null,2),'application/json'),'quiet')
 ]);
}

export function describeImageRecipe(recipe){
 return [recipe.grayscale?'Cinza':null,recipe.contrast?'Contraste normalizado':null,recipe.threshold!==null?'Limiar '+recipe.threshold:null,'Escala '+recipe.resize+'%',recipe.erosion?'Erosão de 1 pixel':null].filter(Boolean).join(' · ');
}
