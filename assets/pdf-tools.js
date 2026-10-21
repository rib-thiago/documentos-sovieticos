/* Instrumento compartilhado pela bancada e área editorial: operações são candidatas locais. */
window.archivePDFTools=(()=>{
  const jobs=new Map();
  const states={queued:'Na fila',running:'Gerando PDFs',generated:'Registrando resultados',completed:'Concluída',failed:'Falha',interrupted:'Interrompida'};
  const node=(tag,attrs={},children=[])=>{const e=document.createElement(tag);for(const[k,v]of Object.entries(attrs))if(k==='text')e.textContent=v;else if(v!=null)e.setAttribute(k,v);for(const c of children)e.append(c);return e;};
  const button=(text,fn)=>{const e=node('button',{type:'button',text});e.onclick=fn;return e;};
  const link=(text,href)=>node('a',{class:'button',text,href});
  function ranges(pages){const parts=[];for(let i=0;i<pages.length;i++){const start=pages[i];let end=start;while(i+1<pages.length&&pages[i+1]===end+1)end=pages[++i];parts.push(start===end?String(start):start+'–'+end);}return parts.join(', ');}
  async function render(host,{api,projectId='',sourceId='',operationId='',signal=null,setDirty=()=>{},setSaving=()=>{}}){
    const shell=node('section',{class:'pdf-tools pdf-operation-studio'});host.replaceChildren(shell);
    const alive=()=>shell.isConnected&&!signal?.aborted;
    const notice=node('p',{class:'status',role:'status'});
    const error=e=>{notice.textContent=e.message;notice.classList.add('error');};
    const [sources,projects]=await Promise.all([api('/api/editorial/pdf/sources',null,signal),api('/api/editorial/projects',null,signal)]);
    if(!alive())return;
    shell.append(node('h2',{text:'Manipular PDF'}),node('p',{class:'help',text:'Extraia páginas ou divida a fonte em partes. O original será preservado; cada resultado terá sua correspondência de páginas. Nenhum texto será publicado.'}),notice);
    const form=node('form',{class:'pdf-source-form pdf-operation-form'}),fields=node('fieldset'),inputs={};
    const stages=node('nav',{class:'pdf-operation-stages','aria-label':'Etapas da operação PDF'}),sourceStage=node('section',{class:'pdf-operation-stage'}),recipeStage=node('section',{class:'pdf-operation-stage'});let fieldHost=sourceStage,stage=sourceId?'recipe':'source';
    const sourceStep=button('1 · Fonte',()=>showStage('source')),recipeStep=button('2 · Operação',()=>showStage('recipe'));stages.append(sourceStep,recipeStep);shell.append(stages);fields.append(sourceStage,recipeStage);
    sourceStage.append(node('h3',{text:'Escolha o material de trabalho'}));recipeStage.append(node('h3',{text:'O que deseja fazer com este PDF?'}));
    function showStage(next){if(next==='recipe'&&!source.value){error(new Error('Selecione um PDF antes de escolher a operação.'));return;}stage=next;sourceStage.hidden=next!=='source';recipeStage.hidden=next!=='recipe';sourceStep.setAttribute('aria-current',next==='source'?'step':'false');recipeStep.setAttribute('aria-current',next==='recipe'?'step':'false');}

    const add=(key,label,value='',choices=null)=>{const input=node(choices?'select':'input',choices?{}:{type:key==='pages_per_part'?'number':'text'});if(choices)for(const[v,t]of choices)input.append(node('option',{value:v,text:t}));input.value=value;inputs[key]=input;const wrap=node('label',{class:'field',text:label},[input]);fieldHost.append(wrap);return{input,wrap};};
    const source=add('source_id','PDF de origem',sourceId,[['','Selecione uma fonte'],...sources.items.map(s=>[s.id,(s.metadata.title||s.filename)+' · '+(s.page_count??'?')+' páginas'])]).input;source.required=true;
    const destination=add('project_id','Vincular os derivados ao projeto (opcional)',projectId,[['','Sem vínculo com projeto'],...projects.items.filter(p=>!p.archived).map(p=>[p.id,p.title])]).input;
    const sourceInfo=node('p',{class:'help'});sourceStage.append(sourceInfo);
    function describe(){const s=sources.items.find(s=>s.id===source.value);sourceInfo.textContent=s?(s.page_count?s.page_count+' páginas físicas. A numeração impressa pode ser diferente.':'Inventário ainda em processamento. Atualize a lista ou tente preparar a prévia novamente em instantes.'):'Escolha uma fonte recebida na oficina.';}
    const refresh=button('Atualizar lista de fontes',async()=>{refresh.disabled=true;try{const next=await api('/api/editorial/pdf/sources',null,signal);if(!alive())return;const selected=source.value;sources.items=next.items;source.replaceChildren(node('option',{value:'',text:'Selecione uma fonte'}));for(const s of sources.items)source.append(node('option',{value:s.id,text:(s.metadata.title||s.filename)+' · '+(s.page_count??'?')+' páginas'}));source.value=selected;describe();}catch(e){error(e);}finally{refresh.disabled=false;}});
    sourceStage.append(refresh,button('Continuar →',()=>showStage('recipe')));
    const reviewArea=node('section',{class:'pdf-tool-review'});shell.append(reviewArea);
    sourceStage.append(button('Revisar fonte / executar OCR',async()=>{
      if(!source.value){error(new Error('Escolha uma fonte PDF.'));return;}
      try{await archivePDFReview.renderSource(reviewArea,{api,sourceId:source.value,projectId:destination.value,signal,setDirty,setSaving});reviewArea.scrollIntoView({block:'start'});}catch(e){error(e);}
    }));
    fieldHost=recipeStage;
    const modeField=add('mode','Operação','extract',[['extract','Extrair páginas em um PDF'],['split','Dividir em vários PDFs']]);const mode=modeField.input;modeField.wrap.hidden=true;
    const choices=node('div',{class:'pdf-operation-choices',role:'group','aria-label':'Operação desejada'}),modeButtons=[];
    for(const [value,label,description]of [['extract','Extrair páginas','Um novo PDF com as páginas que você selecionar.'],['split','Dividir em partes','Vários PDFs organizados por tamanho ou intervalos.']]){const b=button(label,()=>{mode.value=value;form.dispatchEvent(new Event('input',{bubbles:true}));});b.append(node('small',{text:description}));b.dataset.mode=value;modeButtons.push(b);choices.append(b);}recipeStage.append(choices);
    const pages=add('pages','Páginas a extrair','1-5');pages.input.placeholder='1-5, 8, 12-15';
    const split=add('split_mode','Como dividir','size',[['size','Quantidade de páginas por parte'],['ranges','Intervalos definidos por mim']]);
    const size=add('pages_per_part','Páginas por parte','20');size.input.min='1';size.input.max='1500';
    const groups=add('ranges','Partes separadas por ponto e vírgula','1-5; 6-10');groups.input.placeholder='1-5; 6-10; 11-15';
    const explain=node('p',{class:'help',text:'Use as páginas físicas do PDF, começando em 1. Em extrair, a ordem digitada é preservada (por exemplo: 8, 1-3). Não são aceitas páginas repetidas ou partes sobrepostas.'});recipeStage.append(explain);
    const preview=node('section',{class:'pdf-preview',hidden:''}),review=node('button',{type:'submit',class:'primary',text:'Conferir operação antes de gerar'});
    recipeStage.append(review);form.append(fields,preview);shell.append(form);
    function controls(){for(const b of modeButtons)b.setAttribute('aria-pressed',String(b.dataset.mode===mode.value));recipeStep.disabled=!source.value;pages.wrap.hidden=mode.value!=='extract';split.wrap.hidden=mode.value!=='split';size.wrap.hidden=mode.value!=='split'||split.input.value!=='size';groups.wrap.hidden=mode.value!=='split'||split.input.value!=='ranges';describe();}
    const initialSource=sources.items.find(s=>s.id===source.value);if(initialSource?.page_count)pages.input.value=initialSource.page_count===1?'1':'1-'+Math.min(5,initialSource.page_count);
    controls();showStage(source.value?stage:'source');let version=0;
    form.oninput=()=>{version++;preview.hidden=true;setDirty(true);controls();};
    if(projectId&&projects.items.find(p=>p.id===projectId)?.archived){fields.disabled=true;notice.textContent='Este projeto está arquivado. Seus materiais podem ser consultados; reabra-o antes de gerar derivados neste contexto.';}
    if(!sources.capabilities.extraction){fields.disabled=true;notice.textContent='Instale a dependência PDF: '+sources.capabilities.installation;}
    const progress=node('section',{class:'panel pdf-operation-progress',hidden:''}),recent=node('details',{},[node('summary',{text:'Operações recentes neste contexto'})]),recentList=node('div');recent.append(recentList);shell.append(progress,recent);
    let timer,lastAnnounced=null,currentJob=operationId||jobs.get(projectId)||'';
    const contextURL=projectId?'?projeto='+encodeURIComponent(projectId):'';
    shell.append(link('Receber outra fonte PDF','/editorial#/pdf/novo'+contextURL));
    async function showJob(id){
      clearTimeout(timer);currentJob=id;jobs.set(projectId,id);
      try{const result=await api('/api/editorial/pdf/operations/'+id,null,signal);if(!alive())return;
        progress.hidden=false;progress.replaceChildren(node('h3',{text:'Operação '+id}),node('p',{class:'pdf-source-status',role:'status',text:(states[result.state]||result.state)+' · '+result.generated+' / '+result.outputs.length+' PDFs gerados · '+result.registered+' registrados'}));
        if(result.error)progress.append(node('p',{class:'status error',text:result.error}));
        if(result.warning)progress.append(node('p',{class:'status error',text:result.warning}));
        for(const output of result.outputs){const item=node('article',{class:'pdf-operation-output'},[node('strong',{text:output.filename}),node('p',{class:'help',text:'Páginas no original: '+ranges(output.pages)})]);
          if(output.result_source_id){const id=output.result_source_id;item.append(node('div',{class:'workspace-editor-actions'},[link('Abrir resultado','/editorial#/pdf/'+id+(result.project_id?'?projeto='+result.project_id:'')),node('a',{class:'button',href:'/api/editorial/pdf/'+id+'/file?download=1',download:output.filename,text:'Baixar PDF'})]));}
          progress.append(item);
        }
        if(['failed','interrupted'].includes(result.state)||(result.state==='completed'&&result.warning)){const resume=button('Retomar operação / vínculo ao projeto',async()=>{resume.disabled=true;try{await api('/api/editorial/pdf/operations/resume',{operation_id:id},signal);if(alive())await showJob(id);}catch(e){error(e);resume.disabled=false;}});progress.append(resume);}
        if(['queued','running','generated'].includes(result.state))timer=setTimeout(()=>{if(alive())showJob(id);},1800);
        else if(result.state==='completed'&&lastAnnounced!==id){lastAnnounced=id;archiveResearchProjects.announce();}
      }catch(e){if(e.name!=='AbortError'&&alive()){error(e);progress.hidden=false;progress.replaceChildren(node('p',{text:'Não foi possível atualizar o andamento. A operação continua salva no backend.'}),button('Consultar novamente',()=>showJob(id)));}}
    }
    signal?.addEventListener('abort',()=>clearTimeout(timer),{once:true});
    form.onsubmit=async event=>{
      event.preventDefault();if(!source.value){showStage('source');source.reportValidity();return;}const submitted=version;review.disabled=true;preview.hidden=true;notice.textContent='';
      try{
        const payload=Object.fromEntries(Object.entries(inputs).map(([key,input])=>[key,key==='pages_per_part'?Number(input.value):input.value]));
        const result=await api('/api/editorial/pdf/operations/preview',payload,signal);if(!alive()||submitted!==version)return;
        preview.replaceChildren(node('h3',{text:'Confira os derivados'}),node('p',{text:result.source_filename+' · '+result.recipe.selected_pages+' páginas selecionadas · '+result.outputs.length+' arquivo(s)'}),node('p',{text:'Destino: '+(projects.items.find(p=>p.id===result.project_id)?.title||'Sem projeto')}));
        if(result.recipe.omitted_pages)preview.append(node('p',{class:'pdf-source-status',text:result.recipe.omitted_pages+' páginas não serão incluídas nos derivados. Permanecem no original.'}));
        for(const output of result.outputs)preview.append(node('p',{text:output.filename+' ← páginas físicas '+ranges(output.pages)}));
        preview.append(node('p',{class:'help',text:'Esta ferramenta copia as páginas selecionadas. Marcadores de navegação do PDF não são copiados; confira formulários, links e anotações nos resultados quando existirem. O original permanece disponível.'}));
        const confirm=button('Confirmar e gerar PDFs locais',async()=>{
          setSaving(true);confirm.disabled=true;fields.disabled=true;
          try{const job=await api('/api/editorial/pdf/operations/start',{preview_id:result.preview_id},signal);setDirty(false);preview.hidden=true;fields.hidden=false;stages.hidden=false;if(alive()){await showJob(job.id);await listJobs();}}
          catch(e){error(e);confirm.disabled=false;}finally{fields.disabled=false;setSaving(false);}
        });preview.append(button('← Ajustar operação',()=>{preview.hidden=true;fields.hidden=false;stages.hidden=false;showStage('recipe');}),confirm);fields.hidden=true;stages.hidden=true;preview.hidden=false;preview.scrollIntoView({block:'start'});
      }catch(e){if(e.name!=='AbortError')error(e);}finally{review.disabled=false;}
    };
    async function listJobs(){try{const query=new URLSearchParams();if(projectId)query.set('project_id',projectId);const result=await api('/api/editorial/pdf/operations'+(query.size?'?'+query:''),null,signal);if(!alive())return;recentList.replaceChildren();for(const job of result.items)recentList.append(button((states[job.state]||job.state)+' · '+job.id,()=>showJob(job.id)));if(!result.items.length)recentList.append(node('p',{class:'help',text:'Nenhuma operação neste contexto.'}));}catch(e){if(e.name!=='AbortError')recentList.textContent='Histórico de operações indisponível. Você pode preparar uma nova operação.';}}
    await listJobs();if(currentJob&&alive())await showJob(currentJob);
  }
  return {render,ranges};
})();
