/* Contexto de pesquisa local: referências ao acervo, sem alterar publicação. */
window.archiveResearchProjects=(()=>{
  function node(tag,attrs={},children=[]){const el=document.createElement(tag);for(const [k,v]of Object.entries(attrs))if(k==='text')el.textContent=v;else if(v!=null)el.setAttribute(k,v);for(const c of children)el.append(c);return el;}
  const button=(text,run)=>{const el=node('button',{type:'button',text});el.onclick=run;return el;};
  const link=(text,href)=>node('a',{class:'button',text,href});
  const name=item=>item.titles?.pt||item.titles?.ru||item.title||item.id;
  const route=id=>'#/projetos/'+id;
  async function initializeContext(){
    if(window.parent!==window&&window.frameElement?.dataset.oficina==='true')return;
    const navigation=window.performance?.getEntriesByType?.('navigation')?.[0];
    const reload=navigation?.type==='reload';
    const [path,raw='']=location.hash.split('?');const params=new URLSearchParams(raw);
    if(reload){
      params.delete('projeto');
      const back=params.get('leitor');
      if(back){const [base,query='']=back.split('?');const nested=new URLSearchParams(query);nested.delete('projeto');params.set('leitor',base+(nested.size?'?'+nested:''));}
      history.replaceState(null,'',path+(params.size?'?'+params:''));
    }
    // Um link explícito abre seu workspace; um acesso inicial comum ou F5 começa sem projeto.
    if(params.get('projeto')||!['localhost','127.0.0.1','[::1]'].includes(location.hostname))return;
    const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),5000);
    try{
      const response=await fetch('/api/editorial/session',{cache:'no-store',signal:controller.signal});
      if(!response.ok)return;
      const session=await response.json();if(!session.token)return;
      await fetch('/api/editorial/projects/activate',{method:'POST',cache:'no-store',signal:controller.signal,
        headers:{'Content-Type':'application/json','X-Editorial-Token':session.token},body:JSON.stringify({project_id:null})});
    }catch{/* Sem backend, o leitor continua acessível e não herda contexto de projeto. */}
    finally{clearTimeout(timeout);}
  }
  function announce(){try{localStorage.setItem('researchProjectsChanged',String(Date.now()));}catch{}document.dispatchEvent(new Event('archive:projects-changed'));}
  async function mountContext(api,signal){
    const host=document.getElementById('research-project-context');if(!host)return;
    const result=await api('/api/editorial/projects',null,signal);if(signal?.aborted)return;
    const select=node('select',{'aria-label':'Projeto de pesquisa ativo'});
    select.append(node('option',{value:'',text:'Sem projeto ativo'}));
    for(const p of result.items.filter(p=>!p.archived))select.append(node('option',{value:p.id,text:p.title}));
    select.value=result.active_id||'';
    const message=node('p',{class:'help',role:'status',text:'Contexto local; mudar projeto não modifica o acervo.'});
    select.onchange=async()=>{select.disabled=true;try{await api('/api/editorial/projects/activate',{project_id:select.value||null},signal);announce();message.textContent='Projeto ativo atualizado. Operações já abertas mantêm o destino escolhido.';}catch(e){message.textContent=e.message;select.value=result.active_id||'';}finally{select.disabled=false;}};
    host.replaceChildren(node('label',{class:'field',text:'Projeto de pesquisa'},[select]),message);
  }
  async function render({view,path,params,signal,api,collections,navigate=hash=>{location.hash=hash;},reload=()=>location.reload(),setDirty,setSaving}){
    const all=await api('/api/editorial/projects',null,signal);if(signal.aborted)return;
    const notice=node('p',{class:'status',role:'status'});
    const fail=e=>{notice.textContent=e.message;notice.classList.add('error');};
    view.append(node('h1',{text:'Projetos de pesquisa'}),node('p',{class:'help',text:'Reúna documentos e fontes para uma investigação. Vínculos não duplicam textos, não mudam coleções e não tornam materiais públicos.'}),notice);
    if(path==='projetos'){
      view.append(link('Novo projeto',route('novo')));
      if(!all.items.length)view.append(node('p',{text:'Nenhum projeto criado. Comece com um projeto vazio ou use uma coleção como ponto de partida.'}));
      for(const project of all.items){
        const active=all.active_id===project.id;
        const activate=button(active?'Projeto ativo':'Ativar projeto',async()=>{activate.disabled=true;try{await api('/api/editorial/projects/activate',{project_id:project.id},signal);announce();navigate('/#/bancada?projeto='+project.id);}catch(e){fail(e);activate.disabled=false;}});
        activate.disabled=active||project.archived;
        view.append(node('article',{class:'panel'},[node('h2',{text:project.title+(project.archived?' · Arquivado':'')}),node('p',{text:project.description||'Sem descrição'}),node('p',{text:project.document_ids.length+' documentos · '+project.source_ids.length+' fontes PDF · Local'}),node('div',{class:'actions'},[link('Abrir projeto',route(project.id)),activate])]));
      }
      return;
    }
    const id=path.slice('projetos/'.length),creating=id==='novo';
    const project=creating?null:await api('/api/editorial/projects/'+encodeURIComponent(id),null,signal);
    const sources=await api('/api/editorial/pdf/sources',null,signal);if(signal.aborted)return;
    view.append(link('← Projetos','#/projetos'));
    const form=node('form',{class:'panel project-form'}),inputs={};
    const field=(key,label,value='',choices=null)=>{const input=node(choices?'select':key==='description'?'textarea':'input',choices?{}:{...(key==='description'?{rows:'4',maxlength:'20000'}:{type:'text',maxlength:'1000'})});if(choices)for(const [val,caption]of choices)input.append(node('option',{value:val,text:caption}));input.value=value;inputs[key]=input;form.append(node('label',{class:'field',text:label},[input]));return input;};
    field('title','Título do projeto',project?.title||'').required=true;
    field('description','Objetivo e notas de apresentação',project?.description||'');
    const collection=field('collection_id','Coleção de referência (opcional)',project?.collection_id||params.get('colecao')||'', [['','Sem coleção de referência'],...collections.flatMap(c=>[[c.id,name(c)],...c.children.map(s=>[s.id,'↳ '+name(s)])])]);
    const docs=new Set(project?.document_ids||[]),pdfs=new Set(project?.source_ids||[]),docLabels=new Map();
    const selected=node('div',{class:'project-selection'}),searchResults=node('div',{class:'project-search-results'});
    const docLinks=node('div',{class:'project-document-links'});
    const markDirty=()=>{setDirty(true);preview.hidden=true;};
    function selectedDocs(){selected.replaceChildren(node('p',{text:docs.size+' documentos vinculados'}));for(const docId of [...docs].slice(0,100))selected.append(node('div',{class:'project-selection-item'},[node('span',{text:docLabels.get(docId)||docId}),button('Remover vínculo',()=>{docs.delete(docId);selectedDocs();markDirty();})]));if(docs.size>100)selected.append(node('p',{text:'Exibindo os primeiros 100. Use a busca pelo ID para remover outros vínculos.'}));}
    const documents=node('section',{},[node('h3',{text:'Documentos do acervo'})]);
    const search=node('input',{type:'search',placeholder:'Título ou ID do documento','aria-label':'Buscar documento para vincular'});
    const searchButton=button('Buscar',async()=>{
      searchButton.disabled=true;
      try{const q=search.value.trim();if(!q)return;let items=[];
        if(/^[a-z0-9]+(?:-[a-z0-9]+)+$/.test(q)){
          const response=await fetch('/api/documents/'+encodeURIComponent(q),{cache:'no-store',signal});if(response.ok)items=[await response.json()];
        }
        if(!items.length){const result=await api('/api/documents?'+new URLSearchParams({q,scope:'title',limit:'15'}),null,signal);items=result.items;}
        if(signal.aborted)return;searchResults.replaceChildren();
        if(!items.length)searchResults.append(node('p',{text:'Nenhum documento encontrado.'}));
        for(const doc of items){docLabels.set(doc.id,name(doc));const toggle=button(docs.has(doc.id)?'Remover vínculo':'Vincular',()=>{if(docs.has(doc.id))docs.delete(doc.id);else docs.add(doc.id);toggle.textContent=docs.has(doc.id)?'Remover vínculo':'Vincular';selectedDocs();markDirty();});searchResults.append(node('div',{class:'project-selection-item'},[node('span',{text:name(doc)+' · '+doc.id}),toggle]));}
      }catch(e){if(e.name!=='AbortError')fail(e);}finally{searchButton.disabled=false;}
    });
    search.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();searchButton.click();}};
    if(params.get('documento'))search.value=params.get('documento');
    const useCollection=button('Adicionar documentos da coleção de referência',async()=>{
      if(!collection.value){fail(new Error('Escolha uma coleção de referência.'));return;}useCollection.disabled=true;
      try{let offset=0,more=true;while(more){const result=await api('/api/documents?'+new URLSearchParams({collection:collection.value,limit:'100',offset:String(offset),sort:'source'}),null,signal);if(signal.aborted)return;for(const doc of result.items){docs.add(doc.id);docLabels.set(doc.id,name(doc));}offset+=result.items.length;more=Boolean(result.has_more)&&result.items.length>0;}selectedDocs();markDirty();notice.textContent='Documentos adicionados à prévia. Inclusões futuras na coleção não entram automaticamente no projeto.';}
      catch(e){if(e.name!=='AbortError')fail(e);}finally{useCollection.disabled=false;}
    });
    documents.append(node('div',{class:'actions'},[search,searchButton]),searchResults,useCollection,selected);
    form.append(documents);
    const sourceSection=node('section',{},[node('h3',{text:'Fontes PDF locais'})]);
    for(const source of sources.items){const check=node('input',{type:'checkbox',value:source.id});check.checked=pdfs.has(source.id);check.onchange=()=>{if(check.checked)pdfs.add(source.id);else pdfs.delete(source.id);markDirty();};sourceSection.append(node('label',{class:'project-source-choice'},[check,node('span',{text:source.metadata.title||source.filename})]));}
    if(!sources.items.length)sourceSection.append(node('p',{text:'Nenhuma fonte recebida. Você pode cadastrar o projeto primeiro e enviar um PDF depois.'}));
    form.append(sourceSection);
    const archived=node('input',{type:'checkbox'});archived.checked=Boolean(project?.archived);
    if(!creating)form.append(node('label',{class:'project-source-choice'},[archived,node('span',{text:'Arquivar projeto (preserva documentos, fontes e histórico)'})]));
    const review=node('button',{type:'submit',class:'primary',text:'Conferir alterações'}),preview=node('div',{class:'pdf-preview',hidden:''});
    form.append(review,preview);view.append(form);selectedDocs();
    form.addEventListener('input',markDirty);
    async function confirmPreview(result){
      preview.replaceChildren(node('h3',{text:result.reason}));
      const summary=state=>state?state.title+' · '+state.document_ids.length+' documentos · '+state.source_ids.length+' PDFs'+(state.archived?' · Arquivado':''):'Projeto ainda não cadastrado';
      preview.append(node('p',{text:'Antes: '+summary(result.before)}),node('p',{text:'Depois: '+summary(result.after)}),node('p',{text:result.after.description||'Sem descrição'}),node('p',{text:'Coleção de referência: '+(result.after.collection_id||'Nenhuma')}));
      const diff=node('details',{},[node('summary',{text:'Conferir todos os campos e vínculos alterados'})]);diff.append(node('pre',{class:'project-diff',text:JSON.stringify({antes:result.before,depois:result.after},null,2)}));preview.append(diff);
      const save=button('Confirmar gravação local',async()=>{
        setSaving(true);save.disabled=true;const fields=[...form.querySelectorAll('input,textarea,select,button')];const previous=fields.map(el=>el.disabled);fields.forEach(el=>el.disabled=true);
        try{const saved=await api('/api/editorial/projects/save',{preview_id:result.preview_id},signal);setDirty(false);setSaving(false);announce();navigate(route(saved.project_id));if(!creating)reload();}
        catch(e){fail(e);}finally{fields.forEach((el,index)=>el.disabled=previous[index]);save.disabled=false;setSaving(false);}
      });preview.append(save);preview.hidden=false;
    }
    form.onsubmit=async event=>{event.preventDefault();review.disabled=true;try{const result=await api('/api/editorial/projects/preview',{...(project?{project_id:project.id,revision:project.revision}:{}),project:{title:inputs.title.value,description:inputs.description.value,collection_id:collection.value,document_ids:[...docs],source_ids:[...pdfs],archived:archived.checked}},signal);if(!signal.aborted)await confirmPreview(result);}catch(e){fail(e);}finally{review.disabled=false;}};
    if(project){
      const actions=node('div',{class:'actions'});
      const activate=button(all.active_id===project.id?'Projeto ativo':'Ativar projeto',async()=>{try{await api('/api/editorial/projects/activate',{project_id:project.id},signal);announce();await mountContext(api,signal);notice.textContent='Projeto ativado. O envio de PDF oferecerá este destino.';}catch(e){fail(e);}});activate.disabled=project.archived;
      actions.append(link('Abrir workspace','/#/bancada?projeto='+project.id),activate,link('Receber PDF neste projeto','#/pdf/novo?projeto='+project.id),link('Consultar fontes PDF','#/pdf?projeto='+project.id));
      view.append(actions,node('h2',{text:'Abrir materiais já vinculados'}),docLinks);
      for(const docId of project.document_ids.slice(0,100))docLinks.append(link('Abrir na bancada: '+docId,'/#/doc/'+encodeURIComponent(docId)+'?bancada=1&projeto='+project.id));
      for(const sourceId of project.source_ids)view.append(link('Abrir fonte '+sourceId,'#/pdf/'+sourceId));
      const history=node('details',{},[node('summary',{text:'Histórico recuperável do projeto'})]);const list=node('div');history.append(list);view.append(history);
      const records=await api('/api/editorial/projects/'+project.id+'/history',null,signal);if(signal.aborted)return;
      for(const record of records.items){const entry=node('article',{class:'panel'},[node('p',{text:record.created_at+' · '+record.reason}),node('pre',{class:'project-diff',text:JSON.stringify(record.before_state,null,2)})]);
        entry.append(button('Preparar restauração deste estado',async()=>{if(!confirm('Preparar restauração? Isso substituirá a prévia atual; seus campos não salvos continuarão no formulário.'))return;try{const result=await api('/api/editorial/projects/preview',{project_id:project.id,revision:project.revision,history_id:record.id},signal);await confirmPreview(result);preview.scrollIntoView({block:'center',behavior:'smooth'});}catch(e){fail(e);}}));list.append(entry);
      }
    }
  }
  async function workbenchContext(host,docId,projectId=''){
    try{const response=await fetch('/api/editorial/projects',{cache:'no-store'});if(!response.ok||!host.isConnected)return;const result=await response.json();if(!host.isConnected)return;const project=result.items.find(p=>p.id===projectId);
      const select=node('select',{'aria-label':'Workspace de pesquisa'});select.append(node('option',{value:'',text:'Acervo · sem projeto'}));
      for(const p of result.items.filter(p=>!p.archived||p.id===projectId))select.append(node('option',{value:p.id,text:p.title+(p.archived?' · arquivado':'')}));select.value=projectId;
      select.onchange=async()=>{select.disabled=true;try{await archiveProjectEditor.api('/api/editorial/projects/activate',{project_id:select.value||null});announce();const next=result.items.find(p=>p.id===select.value);if(next){const id=next.document_ids.includes(docId)?docId:next.document_ids.find(id=>archiveDocuments().has(id));location.hash=id?'#/doc/'+encodeURIComponent(id)+'?bancada=1&projeto='+next.id:'#/bancada?projeto='+next.id;}else location.hash=docId?'#/doc/'+encodeURIComponent(docId)+'?bancada=1':'#/bancada';}catch(e){select.disabled=false;select.value=projectId;alert(e.message);}};
      host.replaceChildren(node('label',{class:'workspace-project-label',text:'Workspace'},[select]),link('Gerenciar projetos','/editorial#/projetos'));
      if(project){
        host.append(node('p',{class:'workspace-scope-note',text:project.archived?'Projeto arquivado · consulta':'Versões de trabalho isoladas do acervo'}),link('Configuração e vínculos','/editorial'+route(project.id)));
        const search=node('input',{type:'search',placeholder:'Filtrar documentos…','aria-label':'Filtrar documentos do workspace'}),list=node('nav',{class:'workspace-project-documents','aria-label':'Documentos vinculados ao projeto'});
        function renderDocs(){list.replaceChildren();const docs=archiveDocuments();const q=search.value.toLocaleLowerCase();let count=0;for(const id of project.document_ids){const doc=docs.get(id);const caption=doc?documentTitle(doc):id+' (indisponível)';if(![caption,id].join(' ').toLocaleLowerCase().includes(q))continue;count++;const a=link(caption,'#/doc/'+encodeURIComponent(id)+'?bancada=1&projeto='+project.id);a.title=id;if(id===docId)a.setAttribute('aria-current','page');if(!doc){a.removeAttribute('href');a.setAttribute('aria-disabled','true');}list.append(a);}if(!count)list.append(node('p',{class:'workspace-help',text:'Nenhum documento neste filtro.'}));}
        search.oninput=renderDocs;host.append(node('h3',{text:'Documentos · '+project.document_ids.length}),search,list);renderDocs();
        const manipulate=link('Extrair / dividir PDF','#/bancada?projeto='+project.id+'&ferramenta=pdf');
        manipulate.onclick=event=>{event.preventDefault();archiveWorkspace.showTool('pdf');};
        host.append(node('h3',{text:'Fontes e ferramentas'}),manipulate,link('Receber PDF','/editorial#/pdf/novo?projeto='+project.id),link('Fontes deste projeto','/editorial#/pdf?projeto='+project.id));
        if(project.source_ids.length){const response=await fetch('/api/editorial/pdf/sources',{cache:'no-store'});if(!host.isConnected)return;if(response.ok){const sources=await response.json();if(!host.isConnected)return;for(const source of sources.items.filter(s=>project.source_ids.includes(s.id)))host.append(link(source.metadata.title||source.filename,'/editorial#/pdf/'+source.id+'?projeto='+project.id));}}
      }
    }catch{host.textContent='O contexto de pesquisa local está indisponível.';}
  }
  return {render,mountContext,workbenchContext,announce,initializeContext};
})();
