/* Atalhos locais e retorno ao leitor, sem alterar a marcação manual de parágrafos. */
function captureEditorialReading() {
  const current=state.activeDocument;
  if(!current || parseRoute().view!=="document" || parseRoute().id!==current.meta.id)return null;
  const {meta,langs}=current;
  const offset=readingViewportTop();
  const entry=state.readingTracker?.entries.find(item=>{
    const rect=item.node.getBoundingClientRect();return rect.height>0&&rect.bottom>offset;
  });
  return {document_id:meta.id,mode:state.viewMode,studyMode:state.studyMode,
    language:readingLanguage(meta,langs),parallelCols:{...state.parallelCols},scroll:window.scrollY,
    position:entry?{language:entry.language,blockIndex:entry.blockIndex,signature:readingFingerprint(entry.node.textContent)}:null,
    top:entry?entry.node.getBoundingClientRect().top:0};
}

function editorialReturnAddress() {
  const context=captureEditorialReading();
  if(!context)return "/"+(location.hash||"#/");
  state.editorialDepartureContext=context;
  const token=Date.now().toString(36)+"-"+Math.random().toString(36).slice(2);
  const [path,query=""]=location.hash.split("?");const params=new URLSearchParams(query);
  if(sessionWrite("editorialReader:v1:"+token,JSON.stringify(context)))params.set("retorno_editorial",token);
  return "/"+path+"?"+params;
}

function editorialReadingContext(docId) {
  if(state.pendingEditorialContext?.document_id===docId)return state.pendingEditorialContext;
  const token=new URLSearchParams(location.hash.split("?")[1]||"").get("retorno_editorial");
  try {
    const saved=token&&JSON.parse(sessionRead("editorialReader:v1:"+token));
    return saved?.document_id===docId?saved:null;
  }catch{return null;}
}

function applyEditorialReading(context,doc) {
  if(!context)return;
  state.viewMode=context.mode==="study"?"study":"reading";
  if(["paragraph","parallel"].includes(context.studyMode))state.studyMode=context.studyMode;
  if(doc.languages.some(l=>l.code===context.language))state.readingLanguages.set(doc.id,context.language);
  const pair=context.parallelCols;
  try {
    if(pair?.left!==pair?.right&&doc.languages.some(l=>l.code===pair?.left)&&doc.languages.some(l=>l.code===pair?.right))
      localStorage.setItem("parallelCols:"+doc.id,`${pair.left},${pair.right}`);
  }catch{}
}

function restoreEditorialReading(context) {
  if(!context)return;
  requestAnimationFrame(()=>requestAnimationFrame(()=>{
    if(parseRoute().id!==context.document_id)return;
    const entry=context.position&&state.readingTracker&&resolveMarkedEntry(context.position,state.readingTracker.entries);
    const top=entry&&entry.node.getBoundingClientRect().height>0
      ? window.scrollY+entry.node.getBoundingClientRect().top-(Number(context.top)||0):Number(context.scroll)||0;
    window.scrollTo({top:Math.max(0,top),behavior:"instant"});
    const [path,query=""]=location.hash.split("?");const params=new URLSearchParams(query);
    if(params.has("retorno_editorial")) {
      params.delete("retorno_editorial");history.replaceState(null,"",path+(params.toString()?"?"+params:""));
    }
  }));
}

function localEditorialHost() {
  return ["localhost","127.0.0.1","[::1]"].includes(location.hostname);
}

function editorialLink(meta, langs, title, destination, icon="edit") {
  const link=el("a",{class:"editorial-action-link",text:title});
  link.prepend(archiveIcon(icon));
  const update=capture=>{
    const code=document.querySelector(".editorial-language")?.value||documentActionLanguage(meta,langs);
    const params=new URLSearchParams({idioma:code,leitor:capture?editorialReturnAddress():"/"+location.hash});
    if(state.workspaceProject){
      link.href='#/doc/'+encodeURIComponent(meta.id)+'?'+new URLSearchParams({bancada:'1',projeto:state.workspaceProject.id,idioma:code});
      return;
    }
    let path;
    if(destination==="importar"){path="importar";params.set("documento",meta.id);}
    else if(destination==="markdown"&&(langs.find(lang=>lang.code===code)?.format||meta.format)!=="text")path="markdown/"+encodeURIComponent(meta.id+":"+code);
    else path="documento/"+encodeURIComponent(meta.id);
    link.href="/editorial#/"+path+"?"+params;
  };
  update(false);
  link.addEventListener("pointerdown",()=>update(true));
  link.addEventListener("click",event=>{update(true);if(state.workspaceProject){event.preventDefault();history.replaceState(null,'',link.getAttribute('href'));archiveWorkspace.showTool(destination==='documento'?'metadata':'markdown');}});
  return link;
}

function editorialReaderTools(meta,langs) {
  const group=el("div",{class:"toolbar-group editorial-controls","aria-label":"Edição local do documento"});
  group.dataset.docId=meta.id;
  function populate() {
    if(parseRoute().id!==meta.id)return;
    group.replaceChildren();
    group.hidden=!state.editorialAvailable&&!localEditorialHost();
    if(group.hidden)return;
    if(!state.editorialAvailable) {
      group.append(el("p",{class:"control-help",text:state.editorialStatus==="checking"?"Conectando às ferramentas locais…":"A edição local não respondeu. Confira se o backend está aberto e tente novamente."}));
      const retry=el("button",{type:"button",class:"editorial-reconnect",text:"Reconectar edição local"});
      retry.disabled=state.editorialStatus==="checking";
      retry.addEventListener("click",()=>detectReaderEditorial());group.append(retry);return;
    }
    group.append(el("p",{class:"editorial-local-note",text:state.workspaceProject?"Versão de trabalho do projeto · acervo preservado":"Edição local · alterações com prévia e histórico"}));
    const field=languageField(langs,"editorial-language","Idioma da versão",documentActionLanguage(meta,langs));
    group.append(el("span",{class:"toolbar-label",text:"Versão para editar"}),field.element);
    const links=el("div",{class:"editorial-action-grid"});
    links.append(editorialLink(meta,langs,"Editar Markdown","markdown","edit"),
      editorialLink(meta,langs,"Adicionar tradução","importar","language"),
      editorialLink(meta,langs,"Metadados","documento","catalog"));
    // A rota de documento mantém o contexto; o editor Markdown continua na lateral editorial.
    group.append(links);
  }
  group.populateEditorial=populate;populate();return group;
}

function editorialQuickAction(meta,langs) {
  const group=el("div",{class:"editorial-controls editorial-quick-action"});
  group.populateEditorial=()=>{
    group.replaceChildren();group.hidden=!state.editorialAvailable&&!localEditorialHost();
    if(state.editorialAvailable) {
      const link=editorialLink(meta,langs,"Editar",state.workspaceProject?"markdown":"documento");link.classList.add("panel-button","panel-edit");group.append(link);
    } else if(localEditorialHost()) {
      const button=el("button",{type:"button",class:"panel-button",text:state.editorialStatus==="checking"?"Conectando…":"Conectar edição"});
      button.disabled=state.editorialStatus==="checking";button.addEventListener("click",()=>detectReaderEditorial());group.append(button);
    }
  };
  group.populateEditorial();return group;
}

async function detectReaderEditorial() {
  if(state.editorialDetection)return state.editorialDetection;
  state.editorialStatus="checking";
  document.querySelectorAll(".editorial-controls").forEach(group=>group.populateEditorial?.());
  state.editorialDetection=(async()=>{
    const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),15000);
    try {
      const response=await fetch("/api/editorial/capabilities",{cache:"no-store",signal:controller.signal});
      const data=response.ok&&(response.headers.get("content-type")||"").includes("application/json")?await response.json():null;
      const local=data?.mode==="local_editorial";
      state.passageAvailable=local&&data.features?.includes("study_passage_edit")===true;
      state.editorialAvailable=local&&data.features?.includes("markdown_edit")===true;
      state.editorialStatus=state.editorialAvailable?"available":"unavailable";
    }catch{state.editorialAvailable=false;state.passageAvailable=false;state.editorialStatus="unavailable";}
    finally{clearTimeout(timeout);}
    document.querySelectorAll(".editorial-controls").forEach(group=>group.populateEditorial?.());
    document.querySelector(".nav-editorial")?.toggleAttribute("hidden",!state.editorialAvailable);
    installStudyPassageTools();
    document.dispatchEvent(new CustomEvent("archive:capabilities"));
  })();
  try{await state.editorialDetection;}finally{state.editorialDetection=null;}
}

async function reloadEditorialCatalog(preferredContext=null) {
  if(state.editorialReload){state.editorialReloadAgain=true;return state.editorialReload;}
  const context=preferredContext||captureEditorialReading();
  state.editorialReload=(async()=>{
    state.manifest=await fetchJSON("data/manifest.json");
    state.documentIndex=new Map((state.manifest.documents||[]).map(doc=>[doc.id,doc]));
    state.cache.clear();state.pendingEditorialContext=context;renderNav();
    try{await route();}finally{state.pendingEditorialContext=null;}
  })();
  try{await state.editorialReload;}finally{
    state.editorialReload=null;
    if(state.editorialReloadAgain){state.editorialReloadAgain=false;reloadEditorialCatalog().catch(console.error);}
  }
}
