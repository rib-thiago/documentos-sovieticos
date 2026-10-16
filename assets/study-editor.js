/* Correções locais de tradução: intervalo exato no Markdown, sem pareamento inferido. */
function installStudyPassageTools() {
  if(!state.passageAvailable||state.viewMode!=="study"||!state.activeDocument)return;
  const {meta,langs}=state.activeDocument;
  const original=meta.languages.find(language=>language.code==="ru")?.code||meta.languages[0]?.code;
  for(const row of document.querySelectorAll(".blocks > .block[data-study-block]")) {
    const index=Number(row.dataset.studyBlock);
    for(const language of langs) {
      if(!["pt","en"].includes(language.code)||language.code===original||(language.format||meta.format)==="text")continue;
      const block=language.blocks[index];
      const cell=row.querySelector('.cell.lang-'+language.code);
      if(!cell||!block?.sourceMarkdown||cell.querySelector(".study-passage-action"))continue;
      let selection="";
      const capture=()=>{
        const selected=window.getSelection();
        if(!selected?.rangeCount||selected.isCollapsed){selection="";return;}
        const range=selected.getRangeAt(0);
        selection=cell.contains(range.startContainer)&&cell.contains(range.endContainer)?selected.toString():"";
      };
      const action=el("button",{type:"button",class:"study-passage-action",text:"Corrigir tradução",
        "aria-label":"Corrigir trecho em "+language.label,title:"Editar este bloco ou uma seleção exata do texto"});
      cell.addEventListener("pointerup",event=>{if(!action.contains(event.target))capture();});
      cell.addEventListener("keyup",event=>{if(!action.contains(event.target))capture();});
      action.addEventListener("pointerdown",()=>{const selected=window.getSelection();if(selected&&!selected.isCollapsed)capture();});
      action.addEventListener("click",()=>openStudyPassageEditor(meta,language,block,selection,action));
      cell.append(action);
    }
  }
}

async function openStudyPassageEditor(meta,language,block,selection,trigger) {
  if(document.querySelector(".study-passage-dialog"))return;
  const context=captureEditorialReading();
  const dialog=el("dialog",{class:"study-passage-dialog","aria-labelledby":"passage-editor-title"});
  const title=el("h2",{id:"passage-editor-title",text:"Corrigir tradução · "+language.label});
  const notice=el("p",{class:"passage-status",role:"status","aria-live":"polite",text:"Carregando a versão local…"});
  const close=el("button",{type:"button",class:"passage-close",text:"Fechar"});
  const main=el("div",{class:"passage-content"});
  const heading=el("div",{class:"passage-heading"},[title,close]);
  dialog.append(heading,el("p",{class:"passage-document",text:(meta.title_pt||meta.title_ru)+" · "+meta.id}),notice,main);
  document.body.append(dialog);
  let dirty=false,busy=false;
  const unload=event=>{if(dirty||busy){event.preventDefault();event.returnValue="";}};
  window.addEventListener("beforeunload",unload);
  const leave=()=>{
    if(busy)return;
    if(dirty&&!confirm("Descartar a correção ainda não salva?"))return;
    dialog.close();
  };
  close.addEventListener("click",leave);
  dialog.addEventListener("cancel",event=>{event.preventDefault();leave();});
  dialog.addEventListener("close",()=>{
    window.removeEventListener("beforeunload",unload);dialog.remove();
    if(trigger.isConnected)trigger.focus({preventScroll:true});
  },{once:true});
  dialog.showModal();
  const message=(text,error=false)=>{notice.textContent=text;notice.classList.toggle("is-error",error);};
  let token;
  async function api(path,payload) {
    const response=await fetch(path,{cache:"no-store",method:payload?"POST":"GET",
      headers:payload?{"Content-Type":"application/json","X-Editorial-Token":token}:{},
      body:payload?JSON.stringify(payload):undefined});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||"Não foi possível concluir a correção");
    return data;
  }
  try {
    const [session,data]=await Promise.all([api("/api/editorial/session"),api("/api/editorial/editions/"+encodeURIComponent(meta.id+":"+language.code))]);
    if(!dialog.isConnected)return;
    if(!session.features?.includes("study_passage_edit"))throw new Error("Reinicie o backend atualizado para corrigir trechos.");
    token=session.token;
    const body=splitExportHeaders(data.content).body;
    let start=block.sourceStart,end=block.sourceEnd;
    if(!Number.isInteger(start)||!Number.isInteger(end)||body!==language.source||body.slice(start,end)!==block.sourceMarkdown)throw new Error("A versão exibida mudou ou não corresponde ao Markdown local. Feche esta janela e recarregue o documento antes de corrigir.");
    let selectionNote="Você está editando o bloco Markdown deste trecho.";
    if(selection) {
      const offset=block.sourceMarkdown.indexOf(selection);
      if(offset>=0&&block.sourceMarkdown.indexOf(selection,offset+1)<0){start+=offset;end=start+selection.length;selectionNote="Você está editando somente a seleção identificada no Markdown.";}
      else selectionNote="A seleção não corresponde de forma única ao Markdown. O bloco completo foi carregado para você conferir e editar.";
    }
    const expected=body.slice(start,end);
    const newline=data.content.includes("\r\n")?"\r\n":"\n";
    const textarea=el("textarea",{class:"passage-source",rows:"7","aria-label":"Correção do trecho em Markdown",spellcheck:"true"});
    textarea.value=expected;
    const original=el("details",{class:"passage-original"},[el("summary",{text:"Ver trecho atual"}),el("pre",{text:expected})]);
    const rendered=el("div",{class:"passage-rendered reading-content",lang:language.code});
    const review=el("button",{type:"button",class:"passage-primary",text:"Revisar correção"});
    const preview=el("section",{class:"passage-review",hidden:"hidden","aria-label":"Revisão da correção"});
    const actions=el("div",{class:"passage-actions"},[review]);
    main.append(el("p",{class:"passage-help",text:selectionNote+" O original e as outras versões serão preservados."}),original,
      el("label",{class:"passage-label",text:"Nova redação em Markdown"},[textarea]),
      el("p",{class:"passage-label",text:"Prévia do trecho"}),rendered,actions,preview);
    let version=0,proposed=null,timer;
    const replacement=()=>textarea.value.replace(/\r?\n/g,newline);
    const render=()=>{
      try {
        rendered.innerHTML=safeMarkdown(textarea.value,{docId:"passage-preview-"+meta.id});
        for(const link of rendered.querySelectorAll("a")){link.target="_blank";link.rel="noopener noreferrer";}
      } catch(error) {rendered.textContent="Não foi possível renderizar a prévia: "+error.message;}
    };
    render();
    const setBusy=value=>{busy=value;close.disabled=value;textarea.disabled=value;review.disabled=value;};
    textarea.addEventListener("input",()=>{
      dirty=replacement()!==expected;version++;proposed=null;preview.hidden=true;preview.replaceChildren();
      clearTimeout(timer);timer=setTimeout(()=>{if(dialog.isConnected)render();},200);
      message(dirty?"Alterações ainda não salvas. Revise a correção para continuar.":"Nenhuma alteração no trecho.");
    });
    review.addEventListener("click",async()=>{
      const submitted=version;
      setBusy(true);proposed=null;preview.hidden=true;
      message("Preparando as diferenças. Nada foi gravado ainda…");
      try {
        const result=await api("/api/editorial/passages/preview",{revision:data.revision,edition_id:data.edition.id,content_sha256:data.edition.sha256,
          start:Array.from(body.slice(0,start)).length,end:Array.from(body.slice(0,end)).length,expected,replacement:replacement()});
        if(!dialog.isConnected||version!==submitted)return;
        proposed=result;
        const save=el("button",{type:"button",class:"passage-primary",text:"Confirmar e salvar localmente"});
        const back=el("button",{type:"button",text:"Continuar editando"});
        back.addEventListener("click",()=>{proposed=null;preview.hidden=true;textarea.focus();});
        const diff=el("pre",{class:"passage-diff",text:result.passage_edit.diff.text});
        preview.replaceChildren(el("h3",{text:"Confira a correção · "+data.edition.language.toUpperCase()}),
          el("p",{class:"passage-help",text:"Somente este intervalo será substituído. A versão anterior ficará no histórico; o leitor, catálogo e busca serão atualizados."}),diff,
          el("div",{class:"passage-actions"},[save,back]));
        preview.hidden=false;save.focus({preventScroll:true});message("Confira as diferenças antes de confirmar. Nada foi gravado ainda.");
        save.addEventListener("click",async()=>{
          if(!proposed||busy)return;
          setBusy(true);save.disabled=true;back.disabled=true;
          message("Salvando a correção e atualizando o acervo local…");
          try {
            const result=await api("/api/editorial/save",{preview_id:proposed.preview_id,acknowledge_warnings:false});
            dirty=false;proposed=null;
            try{localStorage.setItem("editorialCatalogChanged",Date.now()+":"+result.history_id);}catch{}
            const history=el("a",{class:"passage-history",href:"/editorial#/historico?"+new URLSearchParams({document:meta.id,leitor:editorialReturnAddress()}),text:"Abrir histórico / desfazer"});
            main.replaceChildren(el("p",{text:"Correção salva localmente. A versão anterior está preservada no histórico."}),history);
            message("Salvo. Atualizando o documento…");
            try{await reloadEditorialCatalog(context);message("Documento atualizado. Você pode fechar esta janela e continuar a leitura.");}
            catch(error){message("A correção foi salva, mas não foi possível atualizar o leitor. Feche e recarregue a página. "+error.message,true);}
          }catch(error){message(error.message,true);save.disabled=false;back.disabled=false;}
          finally{setBusy(false);}
        });
      }catch(error){message(error.message,true);}
      finally{setBusy(false);}
    });
    message("Confira a versão e o trecho. Digitar ou revisar não grava alterações.");
    textarea.focus({preventScroll:true});
  }catch(error){if(dialog.isConnected)message(error.message,true);}
}
