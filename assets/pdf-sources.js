/* Fontes locais: candidatos não alteram o acervo nem são publicados. */
window.archivePDFSources = (() => {
  const states = {queued:'Na fila',running:'Extraindo texto',completed:'Extração concluída',completed_with_errors:'Concluída com falhas',failed:'Falha',interrupted:'Interrompida'};
  const diagnoses = {text:'Texto extraído',check:'Conferir',ocr_candidate:'Conferir / possível OCR',error:'Falha'};
  function node(tag, attrs = {}, children = []) {
    const el = document.createElement(tag);
    for(const [key,value] of Object.entries(attrs)) {
      if(key === 'text') el.textContent = value;
      else if(value != null) el.setAttribute(key,value);
    }
    for(const child of children) el.append(child);
    return el;
  }
  const link = (text,href) => node('a',{class:'button',href,text});
  const button = (text,action) => {const el=node('button',{type:'button',text});el.onclick=action;return el;};
  const title = c => c.titles?.pt || c.titles?.ru || c.id;
  const url = id => '#/pdf/'+id;
  async function render({view, path, params, signal, api, collections, session, setDirty, setSaving}) {
    let ownDirty = false;
    const dirtyGuard = event => {if(ownDirty){event.preventDefault();event.returnValue='';}};
    window.addEventListener('beforeunload',dirtyGuard);
    signal.addEventListener('abort',()=>window.removeEventListener('beforeunload',dirtyGuard),{once:true});
    const notice=node('p',{role:'status',class:'status'});
    const error = e => {notice.textContent=e.message;notice.className='status error';};
    const data = await api('/api/editorial/pdf/sources',null,signal);
    const projects = await api('/api/editorial/projects',null,signal);
    const requestedProject=params.get('projeto')||(!params.has('todos')?projects.active_id:null);
    const project=projects.items.find(p=>p.id===requestedProject&&!p.archived);
    if(signal.aborted)return;
    view.append(node('h1',{text:'Fontes PDF'}),node('p',{class:'help',text:'Preserve a fonte e confira a extração por página. As fontes, transcrições e candidatos OCR são locais; não criam documentos públicos automaticamente.'}));
    if(!data.capabilities.extraction) view.append(node('p',{class:'pdf-source-status',text:'Para habilitar a extração, instale no mesmo Python do backend: '+data.capabilities.installation}));
    if(path === 'pdf') {
      view.append(link('Receber PDF','#/pdf/novo'+(project?'?projeto='+project.id:'')),notice);
      view.append(link('Extrair / dividir PDFs','#/pdf/ferramentas'+(project?'?projeto='+project.id:'')));
      if(project)view.append(node('p',{class:'pdf-source-status',text:'Fontes vinculadas ao projeto: '+project.title}),link('Mostrar todas as fontes','#/pdf?todos=1'));
      const items=project?data.items.filter(s=>project.source_ids.includes(s.id)):data.items;
      if(!items.length)view.append(node('p',{text:'Nenhuma fonte neste contexto. Envie um PDF ou vincule uma fonte existente na página do projeto.'}));
      for(const item of items) view.append(node('article',{class:'panel'},[
        node('h2',{text:item.metadata.title || item.filename}),
        node('p',{text:(states[item.state]||item.state)+' · '+(item.page_count ?? '?')+' páginas · '+(item.confirmed?'Fonte cadastrada':'Candidato ainda não confirmado')}),
        link('Abrir fonte e páginas',url(item.id))
      ]));
      return;
    }
    if(path === 'pdf/novo') {
      view.append(link('← Fontes PDF','#/pdf'));
      const form=node('form',{class:'panel pdf-source-form'});
      const upload=node('input',{type:'file',accept:'.pdf,application/pdf',required:'', 'aria-label':'Arquivo PDF'});
      const destination=node('select',{'aria-label':'Projeto de destino do PDF'});
      destination.append(node('option',{value:'',text:'Sem vínculo com projeto'}));
      for(const item of projects.items.filter(p=>!p.archived))destination.append(node('option',{value:item.id,text:item.title}));
      destination.value=project?.id||'';
      const submit=node('button',{type:'submit',class:'primary',text:'Enviar e preparar prévia'});
      submit.disabled=!data.capabilities.extraction;
      const limitMiB=Math.floor(data.capabilities.max_bytes/(1024*1024));
      form.append(node('label',{text:'Projeto de destino (opcional)'},[destination]),node('label',{text:'Arquivo original (até '+limitMiB+' MiB)'},[upload]),node('p',{class:'help',text:'O PDF será preservado e analisado sem OCR. Depois confira as páginas e escolha coleção e subcoleção antes de confirmar o cadastro da fonte.'}),submit,notice);
      form.onsubmit=async event=>{
        event.preventDefault();const file=upload.files[0];if(!file)return;
        if(file.size>data.capabilities.max_bytes){error(new Error('O limite atual é '+limitMiB+' MiB por PDF.'));return;}
        submit.disabled=true;ownDirty=true;setDirty(true);setSaving(true);notice.textContent='Enviando fonte…';
        try {
          const selectedProject=destination.value;
          const response=await fetch('/api/editorial/pdf/upload',{method:'POST',headers:{'Content-Type':'application/pdf','X-Editorial-Token':session.token,'X-PDF-Filename':encodeURIComponent(file.name),'X-Research-Project':selectedProject},body:file,signal});
          const result=await response.json();if(!response.ok)throw new Error(result.error||'Falha no envio');
          if(result.warning)alert(result.warning);
          if(selectedProject)archiveResearchProjects.announce();
          ownDirty=false;setDirty(false);location.hash=url(result.source_id)+(selectedProject?'?projeto='+selectedProject:'');
        }catch(e){if(e.name!=='AbortError')error(e);}
        finally{submit.disabled=false;ownDirty=false;setDirty(false);setSaving(false);}
      };
      view.append(form);return;
    }
    const id=path.slice(4);
    let source=await api('/api/editorial/pdf/'+encodeURIComponent(id),null,signal);
    if(signal.aborted)return;
    view.append(link('← Fontes PDF','#/pdf'),node('h2',{text:source.metadata.title || source.filename}),notice);
    const sourceProjects=projects.items.filter(p=>p.source_ids.includes(id));
    if(sourceProjects.length)view.append(node('p',{class:'help',text:'Projetos com vínculo a esta fonte: '+sourceProjects.map(p=>p.title).join(' · ')}));
    const progress=node('p',{class:'pdf-source-status',role:'status'}), actions=node('div',{class:'actions'});
    view.append(progress,node('p',{class:'pdf-source-id',text:'Fonte: '+id+' · SHA-256: '+source.sha256}),actions);
    actions.append(link('Extrair / dividir esta fonte','#/pdf/ferramentas?'+new URLSearchParams({fonte:id,...(project?{projeto:project.id}:{})})),node('a',{class:'button',href:'/api/editorial/pdf/'+id+'/file?download=1',download:source.filename,text:'Baixar PDF original desta fonte'}));
    if(source.provenance?.length){
      const provenance=node('details',{},[node('summary',{text:'Proveniência e correspondência de páginas'})]);
      for(const origin of source.provenance){
        provenance.append(node('p',{class:'pdf-source-id',text:'Origem: '+origin.parent_source_id+' · SHA-256: '+origin.source_sha256}),link('Consultar fonte de origem',url(origin.parent_source_id)+(project?'?projeto='+project.id:'')),node('p',{class:'help',text:origin.engine||'Motor registrado na operação'}),node('pre',{class:'pdf-raw-text',text:origin.pages.map((page,index)=>'Página '+(index+1)+' deste PDF → página física '+page+' da origem').join('\n')}));
      }
      view.append(provenance);
    }
    const resume=button('Retomar páginas pendentes ou com falha',async()=>{
      resume.disabled=true;
      try{source=await api('/api/editorial/pdf/action',{action:'resume',source_id:id},signal);updateProgress();schedule();}catch(e){error(e);}finally{resume.disabled=false;}
    });actions.append(resume);
    const pageNumber=node('input',{type:'number',min:'1',value:String(source.last_page||1),'aria-label':'Número físico da página'});
    const pageStatus=node('p',{class:'help'});
    const raw=node('pre',{class:'pdf-raw-text',tabindex:'0'});
    const units=node('details',{},[node('summary',{text:'Referências candidatas de parágrafo'})]);
    const unitList=node('div',{class:'pdf-source-units'});units.append(node('p',{class:'help',text:'Segmentação provisória por linhas em branco. IDs e offsets são preservados para a revisão futura; não equivalem a parágrafos validados.'}),unitList);
    const frame=node('iframe',{class:'pdf-facsimile',title:'Fac-símile do PDF original'});
    const external=link('Abrir PDF em outra aba','/api/editorial/pdf/'+id+'/file');external.target='_blank';external.rel='noopener';
    const reviewHost=node('section'),ocrHost=node('section');let reviewController=null;
    let current=Number(pageNumber.value), pageRequest=0, timer,opening=false;
    async function openPage(number) {
      if(!Number.isInteger(number)||number<1||(source.page_count&&number>source.page_count))return;
      if(opening||reviewController&&!reviewController.canLeave())return;
      reviewHost.replaceChildren();reviewController=null;
      current=number;pageNumber.value=String(number);const request=++pageRequest;
      if(frame.dataset.page!==String(number)){
        frame.src='/api/editorial/pdf/'+id+'/file#page='+number;frame.dataset.page=String(number);
      }
      external.href=frame.src;
      const page=source.pages.find(p=>p.page_number===number);
      raw.textContent='';unitList.replaceChildren();
      if(!page){pageStatus.textContent='Página ainda não extraída. Aguarde o processamento.';return;}
      opening=true;
      try {
        const result=await api('/api/editorial/pdf/'+id+'/pages/'+number,null,signal);
        if(signal.aborted||request!==pageRequest)return;
        pageStatus.textContent=(diagnoses[result.diagnosis]||result.diagnosis)+' · '+result.reason+(result.error?' '+result.error:'');
        raw.textContent=result.raw_text||'(Nenhum texto extraído nesta página.)';
        const characters=Array.from(result.raw_text);
        for(const unit of result.paragraphs) {
          const content=characters.slice(unit.start,unit.end).join('');
          const cite=button('Copiar referência',async()=>{try{await navigator.clipboard.writeText((source.metadata.title||source.filename)+' · fonte '+id+' · página física '+number+' · unidade candidata '+unit.id+' · texto SHA-256 '+result.text_sha256);notice.textContent='Referência copiada (unidade ainda não revisada).';}catch{error(new Error('Não foi possível copiar. Selecione o identificador exibido.'));}});
          unitList.append(node('div',{class:'panel'},[node('code',{class:'pdf-source-id',text:unit.id}),node('p',{text:content.slice(0,180)}),cite]));
        }
        reviewController=await archivePDFReview.mountPage(reviewHost,{api,sourceId:id,number,signal,setDirty:value=>{ownDirty=value;setDirty(value);},setSaving});
        await api('/api/editorial/pdf/action',{action:'position',source_id:id,page_number:number},signal);
      }catch(e){if(e.name!=='AbortError')error(e);}finally{opening=false;}
    }
    const toolbar=node('div',{class:'pdf-source-toolbar'},[button('← Anterior',()=>openPage(current-1)),node('span',{text:'Página física'}),pageNumber,button('Ir',()=>openPage(Number(pageNumber.value))),button('Próxima →',()=>openPage(current+1)),button('Atualizar página / candidatos OCR',()=>openPage(current)),external]);
    view.append(ocrHost,toolbar,node('div',{class:'pdf-source-grid'},[node('section',{},[node('h3',{text:'Fac-símile'}),frame]),node('section',{},[pageStatus,reviewHost,node('details',{},[node('summary',{text:'Segmentação nativa original'}),raw,units])])]));
    pageNumber.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();openPage(Number(pageNumber.value));}};
    function updateProgress(){
      progress.textContent=(states[source.state]||source.state)+' · '+source.processed+' / '+(source.page_count??'?')+' páginas extraídas'+(source.error?' · '+source.error:'');
      resume.hidden=!['failed','interrupted','completed_with_errors'].includes(source.state);
      if(source.page_count)pageNumber.max=String(source.page_count);
    }
    function schedule(){
      clearTimeout(timer);if(!['running','queued'].includes(source.state))return;
      timer=setTimeout(async()=>{
        try{const previous=source.processed;source=await api('/api/editorial/pdf/'+id,null,signal);if(signal.aborted)return;updateProgress();if(source.processed!==previous&&!ownDirty&&!opening)await openPage(current);schedule();}catch(e){if(e.name!=='AbortError')error(e);}
      },1800);
    }
    signal.addEventListener('abort',()=>clearTimeout(timer),{once:true});
    await archivePDFReview.mountOCR(ocrHost,{api,sourceId:id,currentPage:()=>current,signal});
    updateProgress();await openPage(current);schedule();
    const bindings=node('details',{class:'panel'},[node('summary',{text:'Vincular esta fonte a um documento'})]),bindingsHost=node('section');bindings.append(bindingsHost);view.append(bindings);
    let bindingsLoaded=false;bindings.addEventListener('toggle',async()=>{if(!bindings.open||bindingsLoaded)return;try{await archivePDFLinks.renderManager(bindingsHost,{api,sourceId:id,projectId:project?.id||'',signal});bindingsLoaded=true;}catch(e){bindingsHost.textContent=e.message;}});
    const form=node('form',{class:'panel pdf-source-form'}), inputs={};
    function field(name,label,value='',choices=null){const input=node(choices?'select':'input',{name,...(!choices?{type:'text',maxlength:'4000'}:{})});if(choices)for(const [key,caption]of choices)input.append(node('option',{value:key,text:caption}));input.value=value;inputs[name]=input;form.append(node('label',{text:label},[input]));return input;}
    form.append(node('h3',{text:'Cadastro local da fonte'}),node('p',{class:'help',text:'Confirme o destino da fonte. Isso ainda não cria um documento ou uma edição pública.'}));
    field('title','Título',source.metadata.title||source.filename).required=true;
    const suggestedRoot=collections.find(c=>c.id===project?.collection_id||c.children.some(s=>s.id===project?.collection_id));
    const collection=field('collection_id','Coleção',source.metadata.collection_id||suggestedRoot?.id||'', [['','Selecione…'],...collections.map(c=>[c.id,title(c)])]);collection.required=true;
    const child=field('subcollection_id','Subcoleção (opcional)','',[['','Sem subcoleção']]);
    function children(){child.replaceChildren(node('option',{value:'',text:'Sem subcoleção'}));for(const c of collections.find(c=>c.id===collection.value)?.children||[])child.append(node('option',{value:c.id,text:title(c)}));}
    collection.onchange=children;children();child.value=source.metadata.subcollection_id||(suggestedRoot?.children.some(s=>s.id===project?.collection_id)?project.collection_id:'');
    const newCollection=link('Criar coleção / subcoleção','#/colecoes');newCollection.target='_blank';newCollection.rel='noopener';
    const reload=button('Atualizar opções',async()=>{try{const result=await api('/api/collections',null,signal);collections=result.items;const selected=collection.value;collection.replaceChildren(node('option',{value:'',text:'Selecione…'}));for(const c of collections)collection.append(node('option',{value:c.id,text:title(c)}));collection.value=selected;children();}catch(e){error(e);}});
    form.append(node('div',{class:'actions'},[newCollection,reload]));
    field('language','Idioma da fonte',source.metadata.language||'ru',[['ru','Russo'],['en','Inglês'],['pt','Português'],['mixed','Mais de um idioma']]);
    field('source_url','URL de origem',source.metadata.source_url||'');
    field('archive_reference','Referência arquivística',source.metadata.archive_reference||'');
    const preview=node('div',{class:'pdf-preview',hidden:''});
    const review=node('button',{type:'submit',class:'primary',text:'Conferir cadastro antes de salvar'});
    form.append(review,preview);view.append(form);
    let snapshot, formRevision=source.revision;
    form.oninput=()=>{preview.hidden=true;setDirty(true);};
    form.onsubmit=event=>{
      event.preventDefault();snapshot=Object.fromEntries(Object.entries(inputs).map(([key,input])=>[key,input.value.trim()]));
      const revision=formRevision;
      preview.replaceChildren(node('h4',{text:'Prévia do cadastro'}));
      for(const [key,value] of Object.entries(snapshot))preview.append(node('p',{text:({title:'Título',collection_id:'Coleção',subcollection_id:'Subcoleção',language:'Idioma',source_url:'Origem',archive_reference:'Arquivo'}[key])+': '+(key==='collection_id'?collections.find(c=>c.id===value)?.titles.pt||value:value||'—')}));
      const save=button('Confirmar gravação local',async()=>{
        setSaving(true);save.disabled=true;review.disabled=true;for(const input of Object.values(inputs))input.disabled=true;
        try{source=await api('/api/editorial/pdf/action',{action:'confirm',source_id:id,revision,metadata:snapshot},signal);formRevision=source.revision;setDirty(false);notice.textContent='Fonte cadastrada localmente. Nenhum documento publicado ou texto do acervo modificado.';preview.hidden=true;await showHistory();}
        catch(e){error(e);}
        finally{save.disabled=false;review.disabled=false;for(const input of Object.values(inputs))input.disabled=false;setSaving(false);}
      });
      preview.append(save);preview.hidden=false;
    };
    const history=node('details',{class:'pdf-source-history'},[node('summary',{text:'Histórico do cadastro da fonte'})]);const records=node('div');history.append(records);view.append(history);
    async function showHistory(){
      const result=await api('/api/editorial/pdf/'+id+'/history',null,signal);if(signal.aborted)return;records.replaceChildren();
      for(const record of result.items){const entry=node('div',{class:'panel'},[node('p',{text:record.created_at}),node('pre',{class:'pdf-raw-text',text:JSON.stringify(record.before_state,null,2)})]);
        const restore=button('Restaurar este estado anterior',async()=>{if(!confirm('Restaurar o cadastro anterior mostrado? A fonte PDF e a extração serão preservadas.'))return;restore.disabled=true;try{await api('/api/editorial/pdf/action',{action:'restore',source_id:id,revision:source.revision,history_id:record.id},signal);location.reload();}catch(e){error(e);restore.disabled=false;}});entry.append(restore);records.append(entry);}
      if(!result.items.length)records.append(node('p',{text:'Nenhuma confirmação de cadastro ainda.'}));
    }
    await showHistory();
  }
  return {render};
})();
