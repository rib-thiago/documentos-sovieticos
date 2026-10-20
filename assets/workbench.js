/* Bancada sobre o leitor existente. Gravações continuam no fluxo editorial com prévia. */
const archiveWorkspace=(()=>{
  const tabs=[],contexts=new Map(),drafts=new Map(),tools=new Map(),notes=new Map();
  let initialized=false,current=null,request=0,activeTool='markdown',refreshTool=null,leavingForEditor=false;
  const languages={pt:'Português',ru:'Русский',en:'English'};
  const side=()=>document.getElementById('workspace-instruments');
  const tabbar=()=>document.getElementById('document-tabs');
  const scope=()=>state.workspaceProject?.id||'';
  const scoped=id=>scope()+'|'+id;
  function bootstrap(){
    if(initialized)return;initialized=true;
    try{const stored=JSON.parse(sessionRead('workspaceTabs:v1')||'[]');const docs=archiveDocuments();for(const tab of stored){const projectId=new URLSearchParams(String(tab.hash||'').split('?')[1]||'').get('projeto')||'';if(tab?.id&&docs.has(tab.id)&&!tabs.some(t=>t.id===tab.id&&t.projectId===projectId))tabs.push({id:tab.id,projectId,hash:url(tab.id,tab.hash,true)});}}catch{}
  }
  function url(id,hash='',enabled=true){
    const [path,query='']=String(hash).split('?');const params=new URLSearchParams(path==='#/doc/'+id?query:'');
    params.delete('retorno_editorial');if(enabled)params.set('bancada','1');else {params.delete('bancada');params.delete('projeto');}
    return '#/doc/'+encodeURIComponent(id)+(params.size?'?'+params:'');
  }
  function defaultURL(){
    const docs=archiveDocuments(),last=sessionRead('workspaceLastDocument');
    const id=docs.has(last)?last:docs.has('showtrials-1665')?'showtrials-1665':docs.keys().next().value;
    // O acesso geral não herda o projeto de uma aba antiga. O workspace é escolhido explicitamente.
    return id?url(id,'',true):'#/bancada';
  }
  function persist(){sessionWrite('workspaceTabs:v1',JSON.stringify(tabs));}
  function notify(text){
    let node=document.querySelector('.workspace-notice');
    if(!node){node=el('p',{class:'workspace-notice',role:'status'});document.body.append(node);}
    node.hidden=false;node.textContent=text;clearTimeout(notify.timer);notify.timer=setTimeout(()=>{node.hidden=true;},5000);
  }
  function capture(){
    const tracker=state.readingTracker,doc=state.activeDocument;if(!tracker||!doc||tracker.meta.id!==doc.meta.id)return;
    const top=readingViewportTop();
    const entry=tracker.entries.find(e=>{const rect=e.node.getBoundingClientRect();return rect.height>0&&rect.width>0&&rect.bottom>top;});
    contexts.set(scoped(doc.meta.id),{document_id:doc.meta.id,mode:state.viewMode,studyMode:state.studyMode,
      language:readingLanguage(doc.meta,doc.langs),parallelCols:{...state.parallelCols},scroll:window.scrollY,
      position:entry?{language:entry.language,blockIndex:entry.blockIndex,signature:readingFingerprint(entry.node.textContent)}:null,
      top:entry?.node.getBoundingClientRect().top||0});
    if(current?.meta.id===doc.meta.id){const tab=tabs.find(t=>t.id===doc.meta.id&&t.projectId===scope());if(tab)tab.hash=url(doc.meta.id,tab.hash,true);}
  }
  function context(id){return contexts.get(scoped(id));}
  function prepare(enabled){
    bootstrap();request++;current=null;refreshTool=null;
    document.body.classList.toggle('has-workspace',enabled);
    document.body.classList.remove('has-project-workspace');
    document.getElementById('archive-workspace').classList.toggle('is-active',enabled);
    side().hidden=!enabled;tabbar().hidden=!enabled;
    if(!enabled){side().replaceChildren();tabbar().replaceChildren();}
  }
  function renderTabs(){
    const docs=archiveDocuments(),root=tabbar();root.replaceChildren();
    for(const tab of tabs){
      if((tab.projectId||'')!==scope())continue;
      const doc=docs.get(tab.id);if(!doc)continue;
      const holder=el('div',{class:'workspace-document-tab'+(tab.id===current?.meta.id?' is-active':'')});
      const link=el('a',{href:tab.hash,title:documentTitle(doc),'aria-current':tab.id===current?.meta.id?'page':null},[el('span',{class:'workspace-tab-title',text:documentTitle(doc)})]);
      link.prepend(archiveIcon('read'));
      const close=el('button',{type:'button',text:'×','aria-label':'Fechar '+documentTitle(doc)});
      close.addEventListener('click',()=>{
        const dirty=[...drafts.entries()].some(([key,value])=>key.startsWith(scoped(tab.id)+':')&&value.text!==value.baseline);
        if(dirty&&!confirm('Fechar esta aba descarta seus rascunhos de Markdown ainda não enviados à edição. Continuar?'))return;
        const index=tabs.indexOf(tab);tabs.splice(index,1);
        for(const key of drafts.keys())if(key.startsWith(scoped(tab.id)+':'))drafts.delete(key);
        const remaining=tabs.filter(t=>(t.projectId||'')===scope());
        persist();if(current?.meta.id===tab.id)location.hash=remaining.at(-1)?.hash||(scope()?'#/bancada?projeto='+scope():'#/');else renderTabs();
      });
      holder.append(link,close);root.append(holder);
    }
    const add=el('button',{type:'button',class:'workspace-new-tab',title:'Abrir outro documento','aria-label':'Abrir outro documento'});add.append(archiveIcon('plus'));add.onclick=openPicker;root.append(add);
    const links=[...root.querySelectorAll('a')];
    root.onkeydown=event=>{if(!event.altKey||!['ArrowLeft','ArrowRight'].includes(event.key))return;const index=links.findIndex(link=>link.getAttribute('aria-current')==='page');if(!links.length)return;event.preventDefault();links[(index+(event.key==='ArrowLeft'?-1:1)+links.length)%links.length].click();};
  }
  function openPicker(){
    const dialog=el('dialog',{class:'workspace-picker','aria-labelledby':'workspace-picker-title'});
    const close=el('button',{type:'button',class:'workspace-dialog-close',text:'×','aria-label':'Fechar seleção'});close.onclick=()=>dialog.close();
    const input=el('input',{type:'search',placeholder:'Título ou identificador: Nikolaev, 1665, sentença…','aria-label':'Buscar documento para abrir em uma aba'});
    const count=el('p',{class:'workspace-help',role:'status'}),list=el('div',{class:'workspace-picker-results'});
    dialog.append(close,el('h2',{id:'workspace-picker-title',text:'Abrir documento na bancada'}),input,count,list);
    const update=()=>{
      const query=input.value.normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();
      const docs=[...archiveDocuments().values()].filter(d=>(!state.workspaceProject||state.workspaceProject.document_ids.includes(d.id))&&[d.id,d.title_pt,d.title_ru,d.title_en].join(' ').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase().includes(query));
      count.textContent=docs.length+' documentos · até 30 resultados por consulta';list.replaceChildren();
      for(const doc of docs.slice(0,30)){
        const button=el('button',{type:'button'},[el('strong',{text:documentTitle(doc)}),el('small',{text:doc.id+' · '+doc.languages.map(l=>l.code.toUpperCase()).join(' / ')})]);
        button.onclick=()=>{const collection=findCollectionByDocId(doc.id);const params=new URLSearchParams();if(collection)params.set('colecao',collection.id);if(scope())params.set('projeto',scope());const hash=url(doc.id,'#/doc/'+doc.id+'?'+params,true);dialog.close();location.hash=hash;};list.append(button);
      }
      if(!docs.length)list.append(el('p',{text:'Nenhum título encontrado. Tente outra grafia ou identificador.'}));
    };
    input.oninput=update;input.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();list.querySelector('button')?.click();}};
    dialog.addEventListener('close',()=>dialog.remove());document.body.append(dialog);update();dialog.showModal();input.focus();
  }
  function installInstruments(){
    document.body.classList.toggle('has-project-workspace',Boolean(scope()));
    const root=side();root.replaceChildren();
    const heading=el('div',{class:'workspace-instruments-heading'},[el('span',{text:scope()?'Workspace':'Instrumentos'})]);
    const toggle=el('button',{type:'button',class:'workspace-collapse','aria-controls':'workspace-tool-list'});
    const list=el('div',{id:'workspace-tool-list'});let collapsed=sessionRead('workspaceToolsCollapsed')==='true';
    const apply=()=>{root.classList.toggle('is-collapsed',collapsed);document.getElementById('archive-workspace').classList.toggle('tools-collapsed',collapsed);list.hidden=collapsed;toggle.textContent=collapsed?'›':'‹';toggle.setAttribute('aria-expanded',String(!collapsed));toggle.setAttribute('aria-label',collapsed?'Expandir instrumentos':'Recolher instrumentos');};
    toggle.onclick=()=>{collapsed=!collapsed;sessionWrite('workspaceToolsCollapsed',String(collapsed));apply();updateReadingLayout();};heading.append(toggle);
    for(const [key,label,icon] of [['markdown','Markdown e prévia','edit'],['index','Índice','compass'],['metadata','Ficha documental','catalog'],['notes','Notas de trabalho','read']]){
      const button=el('button',{type:'button',class:'workspace-tool','data-workspace-tool':key,text:label,'aria-controls':'workspace-dock'});button.prepend(archiveIcon(icon));button.onclick=()=>showTool(key);list.append(button);
    }
    const pdf=el('button',{type:'button',class:'workspace-tool','data-workspace-tool':'pdf',text:'Manipular PDF','aria-controls':'workspace-dock'});pdf.hidden=!state.editorialAvailable;pdf.onclick=()=>showTool('pdf');list.append(pdf);
    const open=el('button',{type:'button',class:'workspace-tool workspace-open-document',text:'Abrir documento'});open.prepend(archiveIcon('plus'));open.onclick=openPicker;
    list.append(open,el('p',{class:'workspace-help',text:'As ferramentas acompanham o documento ativo. Notas são privadas desta sessão; salvar o acervo exige confirmação editorial.'}));
    if(state.editorialAvailable){
      const project=el('div',{class:'workspace-project-context'});list.prepend(project);
      archiveResearchProjects.workbenchContext(project,current?.meta.id,scope());
    }
    root.append(heading,list);apply();
  }
  async function mount(doc){
    if(!doc||!state.workspaceMode||parseRoute().id!==doc.meta.id)return;current=doc;
    sessionWrite('workspaceLastDocument',doc.meta.id);
    let tab=tabs.find(t=>t.id===doc.meta.id&&(t.projectId||'')===scope());if(!tab){tab={id:doc.meta.id,projectId:scope(),hash:location.hash};tabs.push(tab);}else tab.hash=location.hash;persist();renderTabs();installInstruments();
    document.querySelector('.doc-header')?.prepend(el('p',{class:'workspace-context-banner',text:state.workspaceProject?'Workspace: '+state.workspaceProject.title+' · versões de trabalho separadas do acervo':'Edição do acervo · sem contexto de projeto'}));
    const navigation=document.querySelector('.nav-workbench');if(navigation)navigation.href=tab.hash;
    const host=document.querySelector('.document-body');
    const frame=el('div',{class:'workspace-document-frame'}),dock=el('aside',{id:'workspace-dock',class:'workspace-dock','aria-label':'Instrumento do documento ativo'});
    host.replaceWith(frame);frame.append(host,dock);
    const publicLink=document.querySelector('.panel-workspace');if(publicLink)publicLink.href=url(doc.meta.id,location.hash,false);
    const requested=new URLSearchParams(location.hash.split('?')[1]||'');
    await showTool(requested.get('ferramenta')==='pdf'?'pdf':tools.get(scoped(doc.meta.id))?.active||'markdown',{sourceId:requested.get('fonte')||''});
  }
  async function mountEmpty(){
    current=null;state.activeDocument=null;renderTabs();installInstruments();
    const view=document.getElementById('view');view.replaceChildren(el('h1',{text:state.workspaceProject?.title||'Bancada de pesquisa'}),el('p',{class:'workspace-help',text:'Escolha um documento na lista lateral. Os documentos e fontes pertencem ao workspace selecionado.'}));
    for(const control of side().querySelectorAll('[data-workspace-tool]'))control.disabled=control.dataset.workspaceTool!=='pdf';
    const body=el('div',{class:'document-body'},[el('p',{class:'workspace-help',text:'Os derivados das ferramentas ficam disponíveis nas fontes do projeto.'})]);
    const dock=el('aside',{id:'workspace-dock',class:'workspace-dock','aria-label':'Ferramentas de pesquisa',hidden:''});
    view.append(el('div',{class:'workspace-document-frame'},[body,dock]));
    const params=new URLSearchParams(location.hash.split('?')[1]||'');
    if(params.get('ferramenta')==='pdf')await showTool('pdf',{sourceId:params.get('fonte')||''});
  }
  async function showTool(name,options={}){
    const doc=current,dock=document.getElementById('workspace-dock');if(!dock||(!doc&&name!=='pdf'))return;
    const ownRequest=++request;activeTool=name;refreshTool=null;
    const settings=doc?tools.get(scoped(doc.meta.id))||{}:{};settings.active=name;if(doc)tools.set(scoped(doc.meta.id),settings);
    dock.hidden=false;document.querySelectorAll('[data-workspace-tool]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.workspaceTool===name)));
    const titles={markdown:'Markdown e prévia',index:'Índice do texto',metadata:'Ficha documental',notes:'Notas de trabalho',pdf:'Manipular PDF'};
    const close=el('button',{type:'button',text:'×','aria-label':'Recolher instrumento'});
    close.onclick=()=>{request++;dock.hidden=true;document.querySelector('[data-workspace-tool][aria-pressed="true"]')?.focus();document.querySelectorAll('[data-workspace-tool]').forEach(b=>b.setAttribute('aria-pressed','false'));};
    const area=el('div',{class:'workspace-dock-body'});dock.replaceChildren(el('header',{class:'workspace-dock-heading'},[el('strong',{text:titles[name]}),close]),area);
    if(name==='pdf'){await archivePDFTools.render(area,{api:archiveProjectEditor.api,projectId:scope(),sourceId:options.sourceId||''});return;}
    if(name==='index'){
      const nav=el('nav',{'aria-label':'Seções do documento',class:'workspace-outline'});
      const render=()=>{nav.replaceChildren();const headings=state.readingTracker?.headings||[];if(!headings.length)nav.append(el('p',{class:'workspace-help',text:'Esta versão não contém títulos para gerar um índice.'}));for(const item of headings){const button=el('button',{type:'button',text:item.node.textContent});button.onclick=()=>jumpToReadingBlock(item.node);nav.append(button);}};
      area.append(nav);refreshTool=render;render();return;
    }
    if(name==='metadata'){
      const list=el('dl',{class:'workspace-facts'});
      for(const [caption,value] of [['Identificador',doc.meta.id],['Título',documentTitle(doc.meta)],['Data',documentDateInfo(doc.meta)?.text],['Referência',doc.meta.archive],['Fonte',doc.meta.source_name],['URL de origem',doc.meta.source_url],['Idiomas',doc.langs.map(l=>l.label||l.code).join(' · ')]])list.append(el('dt',{text:caption}),el('dd',{text:value||'Não cadastrado'}));
      area.append(list);if(state.editorialAvailable&&!scope())area.append(editorialLink(doc.meta,doc.langs,'Editar metadados','documento'));return;
    }
    if(name==='notes'){
      const input=el('textarea',{'aria-label':'Notas privadas deste documento',class:'workspace-notes',placeholder:'Passagens para conferir, referências e dúvidas de tradução…'});
      input.value=notes.get(scoped(doc.meta.id))??sessionRead('workspaceNotes:v1:'+scoped(doc.meta.id))??'';
      input.oninput=()=>{notes.set(scoped(doc.meta.id),input.value);sessionWrite('workspaceNotes:v1:'+scoped(doc.meta.id),input.value);};
      area.append(el('p',{class:'workspace-help',text:'Notas privadas da sessão deste navegador. Não são incluídas no texto nem publicadas.'}),input);return;
    }
    if(scope()){await archiveProjectEditor.render(area,doc);return;}
    const label=el('label',{text:'Versão '});const select=el('select',{'aria-label':'Idioma do Markdown'});
    for(const lang of doc.langs)select.append(el('option',{value:lang.code,text:languages[lang.code]||lang.label}));
    select.value=settings.language||documentActionLanguage(doc.meta,doc.langs);if(!select.value)select.selectedIndex=0;label.append(select);
    const views=el('div',{class:'workspace-view-switch',role:'group','aria-label':'Exibição do arquivo'});
    const sourceButton=el('button',{type:'button',text:'Markdown'}),previewButton=el('button',{type:'button',text:'Prévia'});views.append(sourceButton,previewButton);
    const editor=el('div',{class:'workspace-editor'}),notice=el('p',{class:'workspace-help',role:'status'});
    area.append(el('div',{class:'workspace-dock-controls'},[label,views]),notice,editor);
    let languageRequest=0;
    const load=async()=>{
      const language=select.value,languageVersion=++languageRequest,key=scoped(doc.meta.id)+':'+language;
      settings.language=language;editor.replaceChildren(el('p',{text:'Carregando versão…'}));notice.textContent=state.editorialAvailable
        ?'Rascunhos não alteram o acervo. A gravação é feita na área editorial, após revisão.'
        :'Rascunho apenas no navegador. Para gravar no acervo, use o backend local; você também pode baixar uma cópia.';
      try{
        const edition=doc.meta.languages.find(l=>l.code===language);
        let draft=drafts.get(key);
        if(!draft){
          const response=await fetch(encodeURI(edition.file),{cache:'no-cache'});
          if(!response.ok)throw new Error('Falha ao carregar a versão: '+response.status);
          const bytes=await response.arrayBuffer(),raw=new TextDecoder('utf-8',{ignoreBOM:true}).decode(bytes);
          draft={text:raw,baseline:raw,baselineBytes:bytes};
        }
        if(ownRequest!==request||languageVersion!==languageRequest||current!==doc)return;
        const input=el('textarea',{class:'workspace-markdown-source',spellcheck:'false','aria-label':'Rascunho Markdown da versão '+language.toUpperCase()});input.value=draft.text;
        const preview=el('div',{class:'reading-content workspace-markdown-preview',lang:language,hidden:'hidden'});
        preview.dataset.anchorPrefix='workspace-'+doc.meta.id+'-'+language;preview.addEventListener('click',handleReadingAnchor);
        const updatePreview=()=>{const body=splitExportHeaders(input.value).body;preview.innerHTML=(edition.format||doc.meta.format)==='text'?'<pre>'+escapeHTML(body)+'</pre>':safeMarkdown(body,{docId:preview.dataset.anchorPrefix});};
        const view=selected=>{settings.view=selected;const rendered=selected==='preview';input.hidden=rendered;preview.hidden=!rendered;sourceButton.setAttribute('aria-pressed',String(!rendered));previewButton.setAttribute('aria-pressed',String(rendered));if(rendered)updatePreview();};
        sourceButton.onclick=()=>view('source');previewButton.onclick=()=>view('preview');
        const actions=el('div',{class:'workspace-editor-actions'});
        const refresh=el('button',{type:'button',text:'Atualizar prévia'});refresh.onclick=()=>view('preview');actions.append(refresh);
        const transfer=el('button',{type:'button',class:'workspace-save-draft',text:'Revisar na área editorial'});
        transfer.hidden=!state.editorialAvailable||(edition.format||doc.meta.format)==='text';
        transfer.onclick=async()=>{
          transfer.disabled=true;
          try{
            const bytes=draft.baselineBytes||new TextEncoder().encode(draft.baseline),digest=await crypto.subtle.digest('SHA-256',bytes);
            const hash=[...new Uint8Array(digest)].map(byte=>byte.toString(16).padStart(2,'0')).join('');
            const token=Date.now().toString(36)+'-'+Math.random().toString(36).slice(2),key='workspaceDraft:v1:'+token;
            const payload={document_id:doc.meta.id,language,content:input.value,baseline_sha256:hash,created_at:Date.now()};
            if(!sessionWrite(key,JSON.stringify(payload)))throw new Error('O navegador não conseguiu guardar o rascunho para a edição. Baixe uma cópia e abra o editor pelo painel.');
            const params=new URLSearchParams({rascunho:token,idioma:language,leitor:editorialReturnAddress()});
            leavingForEditor=true;location.href='/editorial#/markdown/'+encodeURIComponent(doc.meta.id+':'+language)+'?'+params;
            setTimeout(()=>{leavingForEditor=false;},2000);
          }catch(error){notice.textContent=error.message;}finally{transfer.disabled=false;}
        };
        actions.append(transfer);
        const download=el('button',{type:'button',text:'Baixar rascunho'});download.onclick=()=>{const link=el('a',{download:doc.meta.id+'.'+language+'.rascunho.md'});const uri=URL.createObjectURL(new Blob([input.value],{type:'text/markdown;charset=utf-8'}));link.href=uri;link.click();setTimeout(()=>URL.revokeObjectURL(uri),1000);};actions.append(download);
        input.oninput=()=>{draft.text=input.value;if(draft.text===draft.baseline)drafts.delete(key);else drafts.set(key,draft);notice.textContent=draft.text===draft.baseline?'Arquivo preservado.':'Há um rascunho não salvo. Revise na área editorial ou baixe uma cópia antes de fechar a página.';};
        editor.replaceChildren(input,preview,actions);view(settings.view||'source');
      }catch(error){if(ownRequest===request&&languageVersion===languageRequest)editor.replaceChildren(el('p',{text:error.message}));}
    };
    select.onchange=load;await load();
  }
  document.addEventListener('archive:reader-updated',()=>{if(current&&state.workspaceMode&&activeTool==='index')refreshTool?.();});
  document.addEventListener('archive:capabilities',()=>{if(current&&state.workspaceMode)showTool(activeTool).catch(error=>notify(error.message));});
  const refreshProject=()=>{if(!state.workspaceMode||!state.editorialAvailable)return;const pdf=side()?.querySelector('[data-workspace-tool="pdf"]');if(pdf)pdf.hidden=false;let host=document.querySelector('.workspace-project-context');if(!host){const list=side()?.querySelector('#workspace-tool-list');if(!list)return;host=el('div',{class:'workspace-project-context'});list.prepend(host);}archiveResearchProjects.workbenchContext(host,current?.meta.id,scope());};
  window.addEventListener('storage',event=>{if(event.key==='researchProjectsChanged')refreshProject();});
  document.addEventListener('archive:capabilities',refreshProject);
  document.addEventListener('archive:projects-changed',refreshProject);
  window.addEventListener('beforeunload',event=>{if(!leavingForEditor&&[...drafts.values()].some(d=>d.text!==d.baseline)){event.preventDefault();event.returnValue='';}});
  return {defaultURL,url,capture,context,prepare,mount,mountEmpty,showTool};
})();
