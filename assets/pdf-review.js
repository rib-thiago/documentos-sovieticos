/* Revisão de fontes locais; não substitui documentos ou traduções do acervo. */
window.archivePDFReview=(()=>{
  const node=(tag,attrs={},children=[])=>{const e=document.createElement(tag);for(const[k,v]of Object.entries(attrs))if(k==='text')e.textContent=v;else if(v!=null)e.setAttribute(k,v);for(const c of children)e.append(c);return e;};
  const button=(text,fn)=>{const e=node('button',{type:'button',text});e.onclick=fn;return e;};
  const statuses={pending:'Pendente',reviewed:'Conferida',problem:'Com problema',blank:'Em branco'};
  const states={queued:'Na fila',running:'Executando OCR',completed:'Concluído',failed:'Falha',interrupted:'Interrompido'};
  function field(host,label,input){host.append(node('label',{class:'field',text:label},[input]));return input;}
  function select(choices,value){const e=node('select');for(const[v,t]of choices)e.append(node('option',{value:v,text:t}));e.value=value;return e;}
  async function mountPage(host,{api,sourceId,number,signal,setDirty=()=>{},setSaving=()=>{}}){
    const base='/api/editorial/pdf/'+sourceId+'/pages/'+number+'/review';
    let state=await api(base,null,signal),dirty=false,saving=false,version=0,disposed=false;
    const draftKey='pdfReviewDraft:v1:'+sourceId+':'+number;
    if(signal?.aborted||!host.isConnected)return {canLeave:()=>true};
    host.replaceChildren();
    const controls=node('fieldset'),notice=node('p',{class:'status',role:'status'}),preview=node('section',{class:'pdf-preview',hidden:''});
    const text=field(controls,'Transcrição de trabalho',node('textarea',{class:'pdf-review-text',rows:'24',spellcheck:'false','aria-label':'Texto da página'}));
    const status=field(controls,'Conferência',select(Object.entries(statuses),state.review.status));
    const printed=field(controls,'Número ou rótulo impresso (opcional)',node('input',{type:'text',maxlength:'100'}));
    const notes=field(controls,'Notas de revisão',node('textarea',{rows:'3',maxlength:'10000'}));
    for(const [input,name] of [[text,'transcription'],[status,'status'],[printed,'printed'],[notes,'notes']])input.parentElement?.setAttribute('data-workspace-review-field',name);
    status.setAttribute('aria-label','Conferência');printed.setAttribute('aria-label','Número ou rótulo impresso');notes.setAttribute('aria-label','Notas de revisão');
    const basis=node('p',{class:'help'});
    const raw=node('details',{'data-workspace-review-pane':'references'},[node('summary',{text:'Consultar extração bruta preservada'}),node('pre',{class:'pdf-raw-text',text:state.raw.raw_text||'(Sem texto pesquisável)'}),node('p',{class:'pdf-source-id',text:state.raw.engine+' · SHA-256 '+state.raw.text_sha256})]);
    const candidates=node('details',{'data-workspace-review-pane':'candidates'},[node('summary',{text:'Candidatos OCR e comparação'})]),candidateBody=node('div');candidates.append(candidateBody);
    const history=node('details',{'data-workspace-review-pane':'history'},[node('summary',{text:'Histórico recuperável desta página'})]),records=node('div');history.append(records);
    const alignmentHost=node('section',{'data-workspace-review-pane':'alignment'});
    const units=node('details',{'data-workspace-review-pane':'references'},[node('summary',{text:'Referências dos trechos da revisão'})]),unitBody=node('div');units.append(unitBody);
    const form=node('form',{class:'pdf-source-form pdf-review-form','data-workspace-review-pane':'text'},[controls,preview]);
    const review=node('button',{type:'submit',class:'primary',text:'Conferir alterações'});controls.append(review);
    host.append(node('h3',{text:'Revisão · página física '+number}),notice,basis,candidates,form,raw,units,alignmentHost,history);
    const alive=()=>!disposed&&host.isConnected&&!signal?.aborted;
    const change=()=>{dirty=true;version++;setDirty(true);preview.hidden=true;try{sessionStorage.setItem(draftKey,JSON.stringify({revision:state.revision,text:text.value,status:status.value,printed_label:printed.value,notes:notes.value,basis:state.review.basis}));}catch{notice.textContent='Rascunho não pôde ser guardado na sessão. Salve antes de sair.';}};
    form.oninput=change;
    const guard=e=>{if(alive()&&dirty){e.preventDefault();e.returnValue='';}};window.addEventListener('beforeunload',guard);
    let observer;
    const dispose=()=>{disposed=true;window.removeEventListener('beforeunload',guard);observer?.disconnect();};signal?.addEventListener('abort',dispose,{once:true});
    if(typeof MutationObserver!=='undefined'){observer=new MutationObserver(()=>{if(!host.isConnected)dispose();});observer.observe(document.documentElement,{childList:true,subtree:true});}
    function fill(){text.value=state.review.text;status.value=state.review.status;printed.value=state.review.printed_label;notes.value=state.review.notes;basis.textContent='Revisão '+state.revision+' · base: '+(state.review.basis==='native'?'extração nativa':state.review.basis)+'. Correções permanecem locais à fonte PDF.';}
    function showLists(){
      if(window.archivePDFAlignment)archivePDFAlignment.mount(alignmentHost,{api,sourceId,number,signal,canEdit:()=>!dirty&&!saving,onSaved:next=>{state=next;fill();showLists();notice.textContent='Revisão estrutural salva; texto preservado.';document.dispatchEvent(new CustomEvent('archive:pdf-review-saved'));}}).catch(e=>{if(alive())notice.textContent=e.message;});
      candidateBody.replaceChildren();
      for(const c of state.candidates){const value=node('pre',{class:'pdf-raw-text',text:c.raw_text||'(OCR sem texto)'}),comparison=node('pre',{class:'pdf-raw-text'});
        const adopt=button('Carregar este candidato no editor',()=>{if(saving)return;if(dirty&&!confirm('Substituir o rascunho não salvo pelo candidato OCR?'))return;text.value=c.raw_text;state.review.basis=c.id;change();notice.textContent='Candidato carregado. Confira e salve para adotá-lo como transcrição de trabalho.';host.dispatchEvent(new CustomEvent('archive:pdf-candidate-loaded',{bubbles:true}));text.dispatchEvent(new Event('input',{bubbles:true}));});
        candidateBody.append(node('article',{class:'panel'},[node('p',{class:'pdf-source-id',text:c.created_at+' · '+c.engine}),node('details',{},[node('summary',{text:'Ver texto OCR'}),value]),button('Comparar com a versão salva',async()=>{try{const result=await api('/api/editorial/pdf/review/preview',{source_id:sourceId,page_number:number,revision:state.revision,review:{text:c.raw_text,status:state.review.status,printed_label:state.review.printed_label,notes:state.review.notes,basis:c.id}},signal);if(alive())comparison.textContent=result.diff||'Textos iguais.';}catch(e){notice.textContent=e.message;}}),comparison,adopt]));
      }
      if(!state.candidates.length)candidateBody.append(node('p',{class:'help',text:'Nenhum candidato OCR nesta página. Use o painel OCR para gerar um.'}));
      records.replaceChildren();
      for(const item of state.history)records.append(node('article',{class:'panel'},[node('p',{text:item.created_at+' · estado anterior: '+statuses[item.before_state.status]}),node('details',{},[node('summary',{text:'Ver versão anterior'}),node('pre',{class:'pdf-raw-text',text:item.before_state.text})]),button('Preparar restauração',async()=>{if(saving||dirty&&!confirm('Descartar o rascunho para preparar a restauração?'))return;await prepare({history_id:item.id});})]));
      if(!state.history.length)records.append(node('p',{class:'help',text:'O primeiro salvamento iniciará o histórico.'}));
      unitBody.replaceChildren(node('p',{class:'help',text:'Limites candidatos por linhas em branco; ainda não são alinhamento geométrico validado. A referência inclui fonte, página, unidade, revisão e hash do trecho.'}));
      for(const unit of state.review.units||[])unitBody.append(node('article',{class:'panel'},[node('code',{class:'pdf-source-id',text:unit.id}),node('p',{text:Array.from(state.review.text).slice(unit.start,unit.end).join('').slice(0,160)}),button('Copiar referência',async()=>{try{await navigator.clipboard.writeText('Fonte '+sourceId+' · página física '+number+(state.review.printed_label?' · impressa '+state.review.printed_label:'')+' · revisão '+state.revision+' · unidade '+unit.id+' · SHA-256 '+unit.sha256);notice.textContent='Referência copiada.';}catch{notice.textContent='Não foi possível copiar automaticamente.';}})]));
    }
    async function prepare(extra={}){
      review.disabled=true;const submitted=version;
      try{const result=await api('/api/editorial/pdf/review/preview',{source_id:sourceId,page_number:number,revision:state.revision,...(extra.history_id?extra:{review:{text:text.value,status:status.value,printed_label:printed.value,notes:notes.value,basis:state.review.basis}})},signal);if(!alive()||submitted!==version)return;
        preview.replaceChildren(node('h4',{text:'Confira antes de salvar'}),node('p',{text:'Conferência: '+statuses[result.before.status]+' → '+statuses[result.after.status]}),node('p',{text:'Rótulo impresso: '+(result.before.printed_label||'—')+' → '+(result.after.printed_label||'—')}),node('pre',{class:'pdf-raw-text',text:result.diff||'O texto não mudou.'}),node('p',{class:'help',text:result.before.units?.some(u=>u.boxes?.length||u.boundary==='manual')&&result.before.text!==result.after.text?'A mudança textual pode retirar fronteiras/caixas das unidades alteradas; confira a revisão estrutural após salvar.':''}),node('p',{text:'Notas: '+(result.before.notes||'—')+' → '+(result.after.notes||'—')}),node('p',{class:'pdf-source-id',text:'Base: '+result.before.basis+' → '+result.after.basis}));
        const save=button('Confirmar gravação local',async()=>{saving=true;controls.disabled=true;save.disabled=true;setSaving(true);try{const next=await api('/api/editorial/pdf/review/save',{preview_id:result.preview_id},signal);state=next;dirty=false;try{sessionStorage.removeItem(draftKey);}catch{}setDirty(false);if(alive()){fill();showLists();preview.hidden=true;notice.textContent='Revisão salva. Texto bruto e original preservados.';document.dispatchEvent(new CustomEvent('archive:pdf-review-saved'));}}catch(e){if(alive())notice.textContent=e.message;}finally{saving=false;controls.disabled=false;save.disabled=false;setSaving(false);}});preview.append(save);preview.hidden=false;
      }catch(e){if(alive())notice.textContent=e.message;}finally{review.disabled=false;}
    }
    form.onsubmit=e=>{e.preventDefault();prepare();};fill();showLists();
    try{const draft=JSON.parse(sessionStorage.getItem(draftKey)||'null');if(draft){notice.textContent='Existe um rascunho não salvo nesta sessão'+(draft.revision!==state.revision?' baseado em outra revisão. Confira as diferenças antes de salvar.':'.');host.prepend(node('div',{class:'pdf-source-toolbar'},[button('Recuperar rascunho da sessão',()=>{text.value=draft.text;status.value=draft.status;printed.value=draft.printed_label;notes.value=draft.notes;state.review.basis=draft.basis;change();}),button('Descartar rascunho da sessão',()=>{sessionStorage.removeItem(draftKey);notice.textContent='Rascunho descartado; a revisão salva foi preservada.';})]));}}catch{}

    return {canLeave(){if(saving){notice.textContent='Aguarde a gravação terminar.';return false;}if(dirty&&!confirm('Sair desta página sem salvar o rascunho?'))return false;dirty=false;setDirty(false);dispose();return true;}};
  }

  async function mountOCR(host,{api,sourceId,currentPage=()=>1,signal}){
    const capabilities=await api('/api/editorial/pdf/capabilities',null,signal);
    if(signal?.aborted||!host.isConnected)return;
    const cap=capabilities.ocr,shell=node('details',{class:'panel pdf-ocr-controls'},[node('summary',{text:'OCR configurável e progresso da revisão'})]);host.replaceChildren(shell);
    const form=node('form',{class:'pdf-source-form','data-workspace-ocr-pane':'configuration'}),languages=node('fieldset'),checks=[];
    languages.append(node('legend',{text:'Idiomas do reconhecimento'}));
    for(const [key,label]of [['rus','Russo'],['eng','Inglês'],['por','Português']]){const input=node('input',{type:'checkbox',value:key});input.checked=key==='rus'&&cap.languages.includes(key);input.disabled=!cap.languages.includes(key);checks.push(input);languages.append(node('label',{text:label+(input.disabled?' — modelo ausente':'')},[input]));}
    const pages=field(form,'Páginas físicas (até 50 por lote)',node('input',{type:'text',value:String(currentPage()),required:''}));
    const dpi=field(form,'Resolução',select([['150','150 DPI'],['200','200 DPI'],['300','300 DPI']],'300'));
    const psm=field(form,'Distribuição do texto',select([['3','Automática (inclui colunas)'],['6','Bloco único de texto']],'3'));
    const notice=node('p',{role:'status',class:'status'}),preview=node('section',{class:'pdf-preview',hidden:'','data-workspace-ocr-pane':'configuration'}),jobs=node('div',{'data-workspace-ocr-pane':'progress'}),progress=node('p',{class:'pdf-source-status','data-workspace-ocr-pane':'progress'});
    const review=node('button',{type:'submit',text:'Conferir lote OCR',class:'primary'});review.disabled=!cap.available;
    form.append(languages,review);shell.append(node('p',{class:'help',text:'O OCR gera candidatos separados, sem apagar a extração nativa ou suas correções. Reprocessar uma página exige adotar o resultado explicitamente no editor.'}),node('p',{class:'help',text:cap.available?'OCR disponível: '+cap.languages.join(', ')+(cap.tessdata_dir?' · modelos em '+cap.tessdata_dir:''):'Dependências ausentes. Ubuntu/Debian: '+cap.installation}),button('Usar página atual',()=>{pages.value=String(currentPage());version++;preview.hidden=true;}),form,notice,preview,progress,jobs);
    let inventoryReady=false;review.disabled=true;
    const availability=node('p',{class:'help',role:'status'});shell.append(availability);
    let version=0,timer;const alive=()=>shell.isConnected&&!signal?.aborted;
    form.oninput=()=>{version++;preview.hidden=true;};
    async function poll(){clearTimeout(timer);try{const data=await api('/api/editorial/pdf/'+sourceId+'/review',null,signal);if(!alive())return;inventoryReady=Boolean(data.total_pages);review.disabled=!cap.available||!inventoryReady;availability.textContent=inventoryReady?'Escolha as páginas e confira o lote antes de executar.':'Preparando o inventário do PDF. O OCR será liberado quando a contagem de páginas estiver disponível.';const counts={};for(const p of data.pages)counts[p.status]=(counts[p.status]||0)+1;progress.textContent='Conferidas: '+((counts.reviewed||0)+(counts.blank||0))+' · com problema: '+(counts.problem||0)+' · pendentes: '+Math.max(0,(data.total_pages||0)-(counts.reviewed||0)-(counts.blank||0)-(counts.problem||0))+' · total: '+(data.total_pages??'?');shell.querySelector('summary').textContent='OCR e revisão · '+((counts.reviewed||0)+(counts.blank||0))+' / '+(data.total_pages??'?')+' páginas conferidas';
        jobs.replaceChildren();for(const job of data.jobs){const item=node('article',{class:'pdf-operation-output'},[node('p',{text:(states[job.state]||job.state)+' · '+job.completed_pages.length+'/'+job.recipe.pages.length+' páginas · '+job.recipe.languages.join('+')+' · '+job.recipe.dpi+' DPI'}),node('p',{class:'pdf-source-id',text:job.id})]);if(job.state==='completed')for(const number of job.recipe.pages)item.append(button('Revisar resultado · página '+number,()=>host.dispatchEvent(new CustomEvent('archive:pdf-open-review',{bubbles:true,detail:{number}}))));if(job.error)item.append(node('p',{class:'status error',text:job.error}));if(['failed','interrupted'].includes(job.state))item.append(button('Retomar páginas restantes',async()=>{try{await api('/api/editorial/pdf/ocr/resume',{job_id:job.id},signal);poll();}catch(e){notice.textContent=e.message;}}));jobs.append(item);}
        if(data.jobs.some(j=>['queued','running'].includes(j.state))||!inventoryReady)timer=setTimeout(poll,1800);
      }catch(e){if(alive())notice.textContent=e.message;}}
    form.onsubmit=async e=>{e.preventDefault();const submitted=version;review.disabled=true;try{const result=await api('/api/editorial/pdf/ocr/preview',{source_id:sourceId,pages:pages.value,languages:checks.filter(c=>c.checked).map(c=>c.value),dpi:Number(dpi.value),psm:Number(psm.value)},signal);if(!alive()||submitted!==version)return;preview.replaceChildren(node('h4',{text:'Prévia do lote OCR'}),node('p',{text:'Páginas: '+result.recipe.pages.join(', ')+' · idiomas: '+result.recipe.languages.join('+')+' · '+result.recipe.dpi+' DPI'}),node('p',{class:'help',text:'Depois do processamento, use “Atualizar página” para comparar os novos candidatos. A transcrição de trabalho não será substituída.'}));const start=button('Confirmar e executar OCR local',async()=>{start.disabled=true;try{await api('/api/editorial/pdf/ocr/start',{preview_id:result.preview_id},signal);if(alive()){preview.hidden=true;host.dispatchEvent(new CustomEvent('archive:pdf-ocr-started',{bubbles:true}));poll();}}catch(e){notice.textContent=e.message;start.disabled=false;}});preview.append(start);preview.hidden=false;}catch(e){if(alive())notice.textContent=e.message;}finally{review.disabled=!cap.available||!inventoryReady;}};
    const saved=()=>{if(alive())poll();else document.removeEventListener('archive:pdf-review-saved',saved);};document.addEventListener('archive:pdf-review-saved',saved);
    let observer;const cleanup=()=>{clearTimeout(timer);document.removeEventListener('archive:pdf-review-saved',saved);observer?.disconnect();};
    signal?.addEventListener('abort',cleanup,{once:true});
    if(typeof MutationObserver!=='undefined'){observer=new MutationObserver(()=>{if(!shell.isConnected)cleanup();});observer.observe(document.documentElement,{childList:true,subtree:true});}
    shell.append(button('Atualizar andamento',poll));await poll();
  }

  async function renderSource(host,{api,sourceId,projectId='',signal,setDirty=()=>{},setSaving=()=>{}}){
    const source=await api('/api/editorial/pdf/'+sourceId,null,signal);if(signal?.aborted||!host.isConnected)return;
    host.setAttribute('data-workspace-source-root',sourceId);
    host.replaceChildren(node('h3',{text:source.metadata.title||source.filename}),node('p',{class:'help',text:'Revisão compartilhada da fonte PDF local. Não altera versões Markdown públicas ou privadas de projetos.'}));
    let current=source.last_page||1,controller=null,loading=false;
    const ocr=node('section',{'data-workspace-zone':'ocr'}),editor=node('section'),frame=node('iframe',{class:'pdf-facsimile',title:'Fac-símile original'}),input=node('input',{type:'number',min:'1',max:String(source.page_count||1),value:String(current),'aria-label':'Página física'}),notice=node('p',{role:'status'});
    async function open(number){if(loading||!Number.isInteger(number)||number<1||number>(source.page_count||1)||controller&&!controller.canLeave())return;loading=true;current=number;input.value=String(number);frame.src='/api/editorial/pdf/'+sourceId+'/file#page='+number;try{controller=await mountPage(editor,{api,sourceId,number,signal,setDirty,setSaving});await api('/api/editorial/pdf/action',{action:'position',source_id:sourceId,page_number:number},signal);notice.textContent='';return true;}catch(e){notice.textContent=e.message;return false;}finally{loading=false;}}
    const openOCRResult=async event=>{if(await open(Number(event.detail?.number)))host.dispatchEvent(new CustomEvent('archive:pdf-review-opened',{bubbles:true}));};host.addEventListener('archive:pdf-open-review',openOCRResult);signal?.addEventListener('abort',()=>host.removeEventListener('archive:pdf-open-review',openOCRResult),{once:true});
    host.append(ocr,node('div',{class:'pdf-source-toolbar','data-workspace-zone':'review'},[button('← Anterior',()=>open(current-1)),input,button('Ir',()=>open(Number(input.value))),button('Próxima →',()=>open(current+1)),button('Atualizar página',()=>open(current))]),notice,node('div',{class:'pdf-source-grid','data-workspace-zone':'review','data-workspace-source':sourceId},[frame,editor]));
    const bindings=node('details',{class:'panel','data-workspace-zone':'links'},[node('summary',{text:'Vincular fonte a um documento'})]),bindingsHost=node('section');bindings.append(bindingsHost);host.append(bindings);
    let loaded=false;bindings.addEventListener('toggle',async()=>{if(!bindings.open||loaded)return;try{await archivePDFLinks.renderManager(bindingsHost,{api,sourceId,projectId,signal});loaded=true;}catch(e){bindingsHost.textContent=e.message;}});
    const workflow=node('section');host.append(workflow);await archivePDFWorkflow.mount(workflow,{api,sourceId,projectId,signal});
    await mountOCR(ocr,{api,sourceId,currentPage:()=>current,signal});await open(current);
  }
  return {mountPage,mountOCR,renderSource};
})();
