/* Atalhos locais e retorno ao leitor, sem alterar a marcação manual de parágrafos. */
function captureEditorialReading() {
  const current=state.activeDocument;
  if(!current || parseRoute().view!=="document" || parseRoute().id!==current.meta.id)return null;
  const {meta,langs}=current;
  const offset=readingViewportTop();
  const entry=state.readingTracker?.entries.find(item=>{
    const rect=item.node.getBoundingClientRect();return rect.height>0&&rect.bottom>offset;
  });
  return {document_id:meta.id,mode:langs.length>1?state.viewMode:"reading",studyMode:state.studyMode,
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
  state.viewMode=context.mode==="study"&&doc.languages.length>1?"study":"reading";
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

function editorialReaderTools(meta,langs) {
  const group=el("div",{class:"toolbar-group editorial-controls",hidden:"hidden","aria-label":"Edição local do documento"});
  group.dataset.docId=meta.id;
  function populate() {
    if(!state.editorialAvailable||parseRoute().id!==meta.id)return;
    group.hidden=false;
    const menu=el("details",{class:"editorial-menu"});
    menu.append(el("summary",{text:"Editar"}));
    const panel=el("div",{class:"editorial-menu-body"});
    const field=languageField(langs,"editorial-language","Idioma para edição",documentActionLanguage(meta,langs));
    const select=field.select;
    const edit=el("a",{class:"editorial-link",text:"Editar"});
    const update=(capture=false)=>{
      edit.href="/editorial#/documento/"+encodeURIComponent(meta.id)+"?"+new URLSearchParams({idioma:select.value,leitor:capture?editorialReturnAddress():"/"+location.hash});
    };
    update();
    edit.addEventListener("pointerdown",()=>update(true));
    edit.addEventListener("click",()=>update(true));
    select.addEventListener("change",()=>update());
    panel.append(field.element,edit);
    menu.append(panel);group.replaceChildren(menu);
  }
  group.populateEditorial=populate;populate();return group;
}

async function detectReaderEditorial() {
  const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),3000);
  try {
    const response=await fetch("/api/editorial/session",{cache:"no-store",signal:controller.signal});
    const data=response.ok&&(response.headers.get("content-type")||"").includes("application/json")?await response.json():null;
    state.passageAvailable=typeof data?.token==="string"&&data.features?.includes("study_passage_edit")===true;
    state.editorialAvailable=typeof data?.token==="string"&&data.features?.includes("markdown_edit")===true;
  }catch{state.editorialAvailable=false;state.passageAvailable=false;}
  finally{clearTimeout(timeout);}
  for(const group of document.querySelectorAll(".editorial-controls"))group.populateEditorial?.();
  installStudyPassageTools();
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
