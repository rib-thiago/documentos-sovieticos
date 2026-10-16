/* Interface exclusiva do backend local. Não depende do leitor público. */
(() => {
  const view = document.getElementById("editorial-view");
  let session, collections, vocabularies, controller;
  let dirty = false, saving = false, lastHash = location.hash || "#/fila";
  let readerReturn=null;
  let documentContext=null;
  const labels = {pendente:"Pendente",em_revisao:"Em revisão",corrigido:"Corrigido",adiado:"Adiado",
    urgente:"Urgente",alta:"Alta",media:"Média",baixa:"Baixa",titles:"Títulos",kind:"Categoria",
    cadastro_local:"Conferir cadastro",document_type:"Tipo documental",historical_date:"Data histórica",archive_reference:"Referência arquivística",
    author_label:"Autoria",presentation:"Rótulos editoriais",committed:"Concluída",rolled_back:"Revertida após interrupção",prepared:"Não concluída"};
  const label = key => labels[key] || key;
  function node(tag, attrs = {}, children = []) {
    const element = document.createElement(tag);
    if(tag==="a"&&!attrs.class)element.className="button";
    for (const [key,value] of Object.entries(attrs)) {
      if (key === "text") element.textContent = value ?? "";
      else if (value !== false && value != null) element.setAttribute(key, value === true ? "" : value);
    }
    for (const child of [].concat(children)) if (child != null) element.append(typeof child === "string" ? document.createTextNode(child) : child);
    return element;
  }
  function status(element, message, error = false) {
    element.textContent = message;
    element.classList.toggle("error", error);
  }
  async function api(path, body, signal) {
    const response = await fetch(path, {cache:"no-store",signal,method:body ? "POST" : "GET",
      headers:body ? {"Content-Type":"application/json","X-Editorial-Token":session.token} : {},
      body:body ? JSON.stringify(body) : undefined});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Não foi possível concluir a operação");
    if(path==="/api/editorial/save"&&data.saved) {
      if(session)session.revision=data.revision;
      if(data.document_exists===false&&(documentContext?.document.id===data.document_id||data.entity?.document_ids?.includes(documentContext?.document.id))){
        documentContext=null;document.querySelector(".sidebar-document").hidden=true;
        document.querySelector("[data-markdown-nav]").href="#/markdown";
      }
      try{localStorage.setItem("editorialCatalogChanged",Date.now()+":"+data.history_id);}catch{}
    }
    return data;
  }
  function safeReaderReturn(value) {
    try {
      const url=new URL(value,location.origin);
      return url.origin===location.origin&&url.pathname==="/"&&url.hash.startsWith("#/doc/")?url.pathname+url.hash:null;
    }catch{return null;}
  }
  function withReaderContext(hash) {
    if(!readerReturn||!hash.startsWith("#/"))return hash;
    const [path,query=""]=hash.split("?");const params=new URLSearchParams(query);params.set("leitor",readerReturn);
    return path+"?"+params;
  }
  function returnToReading(container,documentId) {
    if(!documentId&&!readerReturn)return;
    container.append(node("a",{class:"button reader-return",href:readerReturn||"/#/doc/"+encodeURIComponent(documentId),text:"← Voltar à leitura"}));
  }
  function field(caption, name, value = "", options = {}) {
    let input;
    if (options.choices) {
      input = node("select", {name});
      for (const [value,text] of options.choices) input.append(node("option", {value,text}));
      input.value = value ?? "";
    } else if (options.multiline) {
      input = node("textarea", {name,rows:"3",maxlength:options.maxlength || "10000",text:value || ""});
    } else input = node("input", {name,value:value || "",type:"text",maxlength:options.maxlength || "4000"});
    return {input,wrap:node("label", {class:"field" + (options.wide ? " wide" : "")}, [caption,input])};
  }
  function title(doc) {return doc.titles?.pt || doc.titles?.ru || doc.titles?.en || doc.id;}
  function dateBadge(doc) {
    const date=documentDateInfo(doc);
    return date?node(date.iso?"time":"span",{class:"doc-date",datetime:date.iso,title:date.label,"aria-label":date.label+": "+date.text,text:date.text}):null;
  }
  function routeURL(path, params) {const query=params.toString();return "#/"+path+(query?"?"+query:"");}
  function documentURL(id, issue = "") {
    return routeURL("documento/"+encodeURIComponent(id),new URLSearchParams({voltar:location.hash || "#/fila",...(issue?{pendencia:issue}:{})}));
  }
  function badges(row) {
    return node("div",{class:"badges"},[
      node("span",{class:"badge priority-"+row.prioridade,text:label(row.prioridade)}),
      node("span",{class:"badge",text:label(row.status)}),
      node("span",{class:"badge",text:row.id}),
    ]);
  }
  function paging(data, path, params, container) {
    const navigation=node("nav",{class:"pagination","aria-label":"Páginas"});
    for(const [caption,offset] of [["← Anterior",Math.max(0,data.offset-data.limit)],["Próxima →",data.offset+data.limit]]) {
      if((caption.startsWith("←") && data.offset===0)||(!caption.startsWith("←")&&!data.has_more)) continue;
      const next=new URLSearchParams(params);next.set("offset",String(offset));
      navigation.append(node("a",{class:"button",href:routeURL(path,next),text:caption}));
    }
    if(data.offset>0){const first=new URLSearchParams(params);first.delete("offset");navigation.prepend(node("a",{href:routeURL(path,first),text:"Primeira página"}));}
    container.append(navigation);
  }
  async function listPage(path, params, signal) {
    const queue=path==="fila";
    view.append(node("h1",{text:queue?"Fila de revisão":"Editar catálogo"}),node("p",{class:"help",text:queue
      ? "Pendências da revisão Markdown, ordenadas por prioridade. O motivo e a ação sugerida vêm dos registros existentes; você pode atualizar a triagem e suas notas."
      : "Localize qualquer documento para editar seus metadados, mesmo quando ele não tem pendências na fila."}));
    const form=node("form",{class:"panel"});
    const filters=node("div",{class:"filters"});
    const inputs=[field(queue?"Título, ID ou motivo":"Título ou ID exato", "q",params.get("q"))];
    if(queue) inputs.push(field("Status","status",params.has("status")?params.get("status"):"pendente",{choices:[["","Todos"],...session.statuses.map(v=>[v,label(v)])]}),
      field("Prioridade","priority",params.get("priority"),{choices:[["","Todas"],...session.priorities.map(v=>[v,label(v)])]}));
    inputs.push(field("Coleção","collection",params.get("collection"),{choices:[["","Todas"],...collections.map(c=>[c.id,c.titles.pt||c.id])]}));
    for(const input of inputs) filters.append(input.wrap);
    form.append(filters,node("div",{class:"actions"},[node("button",{class:"primary",type:"submit",text:queue?"Filtrar fila":"Localizar documentos"}),node("a",{href:"#/"+path,text:"Limpar"})]));
    form.addEventListener("submit",event=>{event.preventDefault();const next=new URLSearchParams();for(const [k,v]of new FormData(form)) next.set(k,String(v).trim());navigate(routeURL(path,next));});
    view.append(form);
    const notice=node("p",{class:"status",role:"status",text:"Carregando…"});view.append(notice);
    const request=new URLSearchParams();
    for(const input of inputs) if(input.input.value || input.input.name==="status") request.set(input.input.name,input.input.value);
    if(params.has("offset")) request.set("offset",params.get("offset"));
    request.set("limit",queue?"50":"25");
    if(!queue) request.set("scope","title");
    let data;
    const query=request.get("q")||"";
    if(!queue && /^[a-z0-9]+(?:-[a-z0-9]+)+$/.test(query)) {
      // Tenta um ID exato sem limitar a procura à primeira página do catálogo.
      const response=await fetch("/api/documents/"+encodeURIComponent(query),{cache:"no-store",signal});
      if(response.ok) {
        const doc=await response.json();
        const included=!request.get("collection")||doc.collections.some(c=>c.id===request.get("collection"));
        const offset=Number(request.get("offset")||0);
        data={items:included&&offset===0?[{...doc,languages:doc.editions.map(e=>e.language)}]:[],total:included?1:0,offset,limit:25,has_more:false};
      } else if(response.status!==404) throw new Error("Não foi possível localizar o documento");
    }
    if(!data)data=await api((queue?"/api/editorial/queue?":"/api/documents?")+request,null,signal);
    if(queue) {
      const counts=node("div",{class:"badges"});
      for(const [state,count]of Object.entries(data.status_counts)) counts.append(node("span",{class:"badge",text:label(state)+": "+count}));
      notice.before(counts);
    }
    status(notice,`${data.total} ${queue?"pendências":"documentos"} · exibindo ${data.items.length?data.offset+1:0}–${Math.min(data.offset+data.limit,data.total)}`);
    if(!data.items.length) view.append(node("p",{text:"Nenhum resultado nesta página. Amplie os filtros ou volte para a primeira página."}));
    for(const row of data.items) {
      const item=node("article",{class:"item"});
      if(queue) item.append(badges(row));
      item.append(node("div",{class:"document-title-line"},[node("h2",{},[node("a",{class:"document-title-link",href:documentURL(row.id,queue?row.chave:""),text:title(row)})]),dateBadge(row)]));
      if(queue) item.append(node("p",{text:row.dificuldade_encontrada}),node("p",{class:"muted",text:"Ação sugerida: "+row.acao_sugerida}));
      else item.append(node("p",{class:"muted",text:row.id+" · "+row.languages.map(l=>l.toUpperCase()).join(" · ")}));
      item.append(node("a",{href:routeURL("importar",new URLSearchParams({documento:row.id})),text:"Importar tradução para este documento"}));
      view.append(item);
    }
    const visible=new URLSearchParams(params);
    if(queue&&!visible.has("status")) visible.set("status","pendente");
    paging(data,path,visible,view);
  }
  function navigate(hash) {hash=withReaderContext(hash);if(location.hash===hash) route();else location.hash=hash;}
  function comparison(changes) {
    const table=node("table");table.append(node("thead",{},[node("tr",{},["Campo","Antes","Depois"].map(text=>node("th",{scope:"col",text})))]));
    const body=node("tbody");
    const display=value=>typeof value==="object"?JSON.stringify(value,null,2):String(value??"(vazio)");
    for(const change of changes) body.append(node("tr",{},[
      node("th",{scope:"row",text:label(change.field)}),node("td",{},[node("pre",{text:display(change.before)})]),node("td",{},[node("pre",{text:display(change.after)})])
    ]));
    table.append(body);return node("div",{class:"table-scroll"},[table]);
  }
  function previewPanel(preview, container, notice, afterSave, setBusy = () => {}) {
    const panel=node("section",{class:"panel preview",tabindex:"-1","aria-label":"Prévia das alterações"});
    panel.append(node("h2",{text:"Revise antes de salvar"}),comparison(preview.changes));
    if(preview.translation) panel.append(translationDetails(preview.translation));
    if(preview.creation?.kind==="document") {
      const created=preview.creation;
      panel.append(node("p",{class:"help",text:"Destino: "+created.file+" · Idioma original: "+created.language.toUpperCase()}));
      const contentPreview=node("details",{open:created.content.length<=200000},[node("summary",{text:"Prévia do documento"})]);
      let rendered=false;
      const render=()=>{if(!contentPreview.open||rendered)return;rendered=true;
        if(created.format==="markdown")contentPreview.append(markdownReading(created.content,created.language));
        else contentPreview.append(node("pre",{class:"import-source",text:created.content}));
      };
      contentPreview.addEventListener("toggle",render);render();panel.append(contentPreview);
    }
    if(preview.creation?.kind==="batch"){
      panel.append(node("p",{class:"help",text:preview.creation.count+" novos documentos. O lote será salvo em conjunto, com uma pendência por documento e um histórico para desfazer o conjunto."}));
      const list=node("div",{class:"batch-preview-list"});
      for(const item of preview.creation.items){
        const details=node("details",{class:"batch-preview-item"},[node("summary",{text:item.id+" · "+item.language.toUpperCase()+" · "+item.title})]);
        details.append(node("p",{class:"help",text:"Linha "+item.line+" · Destino: "+item.file}),node("p",{class:"help",text:"Coleções: "+item.collections.join(" · ")}));
        if(item.warnings.length)details.append(node("ul",{},item.warnings.map(text=>node("li",{class:"import-warning",text}))));
        let rendered=false;
        details.addEventListener("toggle",()=>{if(!details.open||rendered)return;rendered=true;
          if(item.format==="markdown")details.append(markdownReading(item.content,item.language));
          else details.append(node("pre",{class:"import-source",text:item.content}));
        });list.append(details);
      }
      panel.append(list);
    }
    if(preview.creation?.kind==="collection"){
      const created=preview.creation;const card=node("article",{class:"collection-preview"});
      if(created.cover)card.append(node("img",{src:"/"+created.cover,alt:"Capa da coleção",loading:"lazy"}));
      card.append(node("h3",{text:created.title}));
      if(created.subtitle)card.append(node("p",{class:"muted",text:created.subtitle}));
      if(created.description)card.append(node("p",{text:created.description}));
      panel.append(card);
    }
    if(preview.creation?.warnings?.length)panel.append(node("ul",{class:"import-findings"},preview.creation.warnings.map(text=>node("li",{class:"import-warning",text}))));
    if(preview.markdown_edit) {
      panel.append(node("h3",{text:"Versão Markdown: "+preview.markdown_edit.edition_id}),diffView(preview.markdown_edit.diff),
        markdownReading(preview.markdown_edit.content,preview.markdown_edit.language));
    }
    for(const file of preview.file_diffs || []) {
      panel.append(node("h3",{text:file.removed?"Arquivo incluído que será removido: "+file.file:"Arquivo que será restaurado: "+file.file}),diffView(file.diff));
    }
    panel.append(node("p",{class:"help",text:preview.creation?.kind==="batch"?"Confirmar grava todos os documentos mostrados, suas associações e pendências, atualizando catálogo, manifesto e busca. O histórico permitirá desfazer o lote inteiro.":preview.updates_index
      ? (preview.changes_content?"Ao confirmar, somente a versão mostrada na prévia será atualizada, com histórico do conteúdo anterior. Catálogo, manifesto e busca também serão atualizados. A gravação é local e pode levar alguns segundos.":"Ao confirmar, o catálogo e o manifesto serão gravados e o índice de busca será atualizado. Os textos não serão alterados. A gravação pode levar alguns segundos.")
      : "Ao confirmar, a fila será atualizada. Os textos e os metadados do documento não serão alterados."}));
    let acknowledgement=null;
    if(preview.requires_acknowledgement) {
      acknowledgement=node("input",{type:"checkbox"});
      const language=preview.translation?.language.toUpperCase()||"selecionado";
      panel.append(node("label",{class:"import-ack"},[acknowledgement,preview.creation
        ?preview.creation.kind==="batch"?"Li os avisos de identificação e duplicidade e confirmo cadastrar todos os documentos deste lote.":"Li os avisos de identificação e duplicidade e confirmo cadastrar este arquivo como um novo documento."
        :`Li as divergências e confirmo associar este arquivo ao documento ${preview.document_id}, no idioma ${language}.`]));
    }
    const save=node("button",{type:"button",class:"primary",text:"Confirmar e salvar",disabled:!!acknowledgement});
    acknowledgement?.addEventListener("change",()=>{save.disabled=!acknowledgement.checked;});
    const cancel=node("button",{type:"button",text:"Voltar à edição"});
    cancel.addEventListener("click",()=>{panel.remove();status(notice,"Prévia descartada. Você pode continuar editando.");});
    save.addEventListener("click",async()=>{
      saving=true;save.disabled=true;cancel.disabled=true;
      setBusy(true);
      let completed=false;
      status(notice,"Salvando e atualizando o acervo local. Aguarde…");
      try {
        const result=await api("/api/editorial/save",{preview_id:preview.preview_id,acknowledge_warnings:acknowledgement?.checked===true});
        completed=true;
        dirty=false;
        panel.replaceChildren(node("h2",{text:"Alterações salvas"}),node("p",{text:result.message}),node("p",{class:"muted",text:"Registro: "+result.history_id}));
        status(notice,"Salvo localmente. Atualize as abas do site que já estavam abertas para carregar a versão atualizada.");
        afterSave(result,panel);
        if(["collection","batch"].includes(result.entity?.kind)){
          const target=result.entity.kind==="collection"?"#/colecoes":"#/catalogo";
          if(!panel.querySelector("a[href='"+target+"']"))panel.append(node("a",{href:target,text:result.entity.kind==="collection"?"Voltar às coleções":"Voltar ao catálogo"}));
        }else if(result.document_exists!==false)returnToReading(panel,result.document_id);
        else panel.append(node("a",{href:"#/catalogo",text:"Voltar ao catálogo"}));
      }catch(error){status(notice,error.message,true);save.disabled=!!acknowledgement&&!acknowledgement.checked;cancel.disabled=false;}
      finally{saving=false;if(!completed)setBusy(false);}
    });
    panel.append(node("div",{class:"actions"},[save,cancel]));container.append(panel);
    panel.focus();panel.scrollIntoView({block:"start",behavior:"smooth"});
    return panel;
  }
  function setDocumentContext(catalogDocument,editions,preferred) {
    const language=editions.some(edition=>edition.language===preferred)?preferred:
      editions.find(edition=>edition.language==="pt")?.language||editions[0]?.language||"";
    documentContext={document:catalogDocument,editions,language};
    const slot=document.querySelector(".sidebar-document");slot.hidden=false;
    slot.replaceChildren(node("p",{class:"sidebar-caption",text:"Documento atual"}),
      node("p",{class:"sidebar-document-title",text:title(catalogDocument)}),
      node("a",{class:"sidebar-document-link",href:routeURL("documento/"+encodeURIComponent(catalogDocument.id),new URLSearchParams({idioma:language})),text:"Metadados e coleções"}),
      node("a",{class:"sidebar-document-link",href:routeURL("importar",new URLSearchParams({documento:catalogDocument.id})),text:"Adicionar tradução"}));
    document.querySelector("[data-markdown-nav]").href=routeURL("markdown",new URLSearchParams({documento:catalogDocument.id,idioma:language}));
  }
  async function markdownChooser(params,signal) {
    const id=params.get("documento")||documentContext?.document.id;
    if(!id){
      view.append(node("h1",{text:"Editar Markdown"}),node("p",{class:"help",text:"Selecione um documento pelo catálogo ou informe seu ID."}));
      const form=node("form",{class:"panel"});const input=field("ID do documento","documento");input.input.required=true;
      form.append(input.wrap,node("div",{class:"actions"},[node("button",{type:"submit",text:"Selecionar documento"}),node("a",{href:"#/catalogo",text:"Procurar no catálogo"})]));
      form.addEventListener("submit",event=>{event.preventDefault();navigate(routeURL("markdown",new URLSearchParams({documento:input.input.value.trim()})));});view.append(form);return;
    }
    const data=await api("/api/editorial/documents/"+encodeURIComponent(id),null,signal);
    setDocumentContext(data.document,data.editions,params.get("idioma")||documentContext?.language);
    const editable=data.editions.filter(edition=>edition.format==="markdown"&&edition.file.endsWith(".md"));
    const selected=editable.find(edition=>edition.language===documentContext.language);
    if(selected){await markdownPage(selected.id,params,signal);return;}
    view.append(node("h1",{text:"Editar Markdown"}),node("p",{text:title(data.document)}),node("p",{class:"help",text:"A versão selecionada não está disponível em Markdown. Escolha outra versão ou importe uma tradução."}));
    const actions=node("div",{class:"actions"});
    for(const edition of editable)actions.append(node("a",{href:routeURL("markdown/"+encodeURIComponent(edition.id),new URLSearchParams()),text:"Editar "+edition.language.toUpperCase()}));
    actions.append(node("a",{href:routeURL("importar",new URLSearchParams({documento:id})),text:"Importar tradução"}));view.append(actions);
  }
  async function documentPage(id,params,signal) {
    const data=await api("/api/editorial/documents/"+encodeURIComponent(id),null,signal);
    const doc=data.document;
    setDocumentContext(doc,data.editions,params.get("idioma")||(documentContext?.document.id===id?documentContext.language:null));
    returnToReading(view,id);
    const back=params.get("voltar");
    view.append(node("a",{href:back?.startsWith("#/")?back:"#/fila",text:"← Voltar à lista"}),node("h1",{text:title(doc)}));
    const publicLink=node("a",{href:"/#/doc/"+encodeURIComponent(id),target:"_blank",rel:"noopener",text:"Abrir documento no site ↗"});
    view.append(node("p",{class:"muted",text:id+" · "+data.editions.map(e=>e.language.toUpperCase()).join(" · ")}),publicLink);
    const date=dateBadge(doc);if(date)view.append(date);
    view.append(node("p",{},[node("a",{href:routeURL("importar",new URLSearchParams({documento:id})),text:"Importar tradução Markdown para este documento"})]));
    if(doc.source?.url && /^https?:\/\//.test(doc.source.url)) view.append(node("p",{},[node("a",{href:doc.source.url,target:"_blank",rel:"noopener",text:"Consultar a fonte ↗"})]));
    const form=node("form");const editable=node("fieldset");
    const fields=node("section",{class:"panel"},[node("h2",{text:"Metadados"})]);
    const grid=node("div",{class:"fields"});
    const controls={};
    const add=(caption,name,value,options={})=>{const f=field(caption,name,value,options);controls[name]=f.input;grid.append(f.wrap);};
    add("Título em português","pt",doc.titles.pt,{maxlength:2000});add("Título em russo","ru",doc.titles.ru,{maxlength:2000});add("Título em inglês","en",doc.titles.en,{maxlength:2000});
    add("Categoria","kind",doc.kind,{choices:Object.entries(vocabularies.kinds)});
    add("Tipo documental","document_type",doc.document_type,{choices:[["","Sem classificação específica"],...Object.entries(vocabularies.document_types).sort((a,b)=>a[1].localeCompare(b[1],"pt"))]});
    add("Autoria registrada","author_label",doc.author_label);add("Referência arquivística","archive_reference",doc.archive_reference);
    add("Data para exibição","date_display",doc.historical_date.display,{maxlength:500});add("Data histórica ISO","date_value",doc.historical_date.value,{maxlength:20});
    add("Precisão da data histórica","date_precision",doc.historical_date.precision,{choices:[["not_recorded","Não registrada"],["year","Ano: AAAA"],["month","Mês: AAAA-MM"],["day","Dia: AAAA-MM-DD"]]});
    add("Título curto","shortTitle",doc.presentation.shortTitle,{maxlength:1000});add("Rótulo editorial","eyebrow",doc.presentation.eyebrow,{maxlength:1000});
    fields.append(grid,node("p",{class:"help",text:"IDs, URLs de fonte, arquivos e idiomas são preservados."}));
    const sourceDate=documentDateInfo({collected_date:doc.source_metadata?.wordpress_date});
    if(sourceDate)fields.append(node("p",{class:"source-date-note",text:"Data: "+sourceDate.text}));
    editable.append(fields);
    const membershipPanel=node("section",{class:"panel"},[node("h2",{text:"Coleções e subcoleções"}),node("p",{class:"help",text:"Selecione ao menos uma coleção. Novas associações entram no fim da lista; as associações mantidas conservam a ordem existente."})]);
    const checks=node("div",{class:"collection-checks"});const memberInputs=new Map();
    for(const collection of collections) {
      const group=node("div",{class:"collection-group"});
      const checkbox=(entry,child)=>{
        const input=node("input",{type:"checkbox",value:entry.id,checked:data.collection_ids.includes(entry.id),"data-collection":entry.id});
        memberInputs.set(entry.id,input);group.append(node("label",{class:child?"child":""},[input,entry.titles.pt||entry.id]));return input;
      };
      const parent=checkbox(collection,false);
      for(const child of collection.children) {const input=checkbox(child,true);input.addEventListener("change",()=>{if(input.checked)parent.checked=true;});}
      parent.addEventListener("change",()=>{if(!parent.checked)for(const child of collection.children)memberInputs.get(child.id).checked=false;});
      checks.append(group);
    }
    membershipPanel.append(checks);editable.append(membershipPanel);
    const issueControls=[];
    const issuesPanel=node("section",{class:"panel"},[node("h2",{text:"Pendências deste documento"})]);
    if(!data.issues.length) issuesPanel.append(node("p",{class:"muted",text:"Este documento não tem pendências na fila existente. Seus metadados podem ser editados normalmente."}));
    for(const issue of data.issues) {
      const item=node("section",{class:"item",id:"issue-"+issue.chave});
      item.append(node("h3",{text:issue.problema.replaceAll("_"," ")}),node("p",{class:"muted",text:"Dificuldade: "+label(issue.dificuldade)+" · "+issue.chave}));
      const fields=node("div",{class:"fields"});const inputs={};
      for(const [caption,key,choices]of [["Prioridade","prioridade",session.priorities.map(v=>[v,label(v)])],["Status","status",session.statuses.map(v=>[v,label(v)])]]) {
        const f=field(caption,key,issue[key],{choices});inputs[key]=f.input;fields.append(f.wrap);
      }
      for(const [caption,key]of [["Motivo / dificuldade encontrada","dificuldade_encontrada"],["Notas do revisor","notas_do_revisor"]]) {
        const f=field(caption,key,issue[key],{multiline:true,wide:true});inputs[key]=f.input;fields.append(f.wrap);
      }
      item.append(fields,node("p",{class:"help",text:"Ação sugerida na triagem: "+issue.acao_sugerida}));issuesPanel.append(item);
      issueControls.push({key:issue.chave,inputs});
    }
    editable.append(issuesPanel);
    const submit=node("button",{type:"submit",class:"primary",text:"Revisar alterações"});
    editable.append(node("div",{class:"actions"},[submit,node("a",{href:"#/historico?document="+encodeURIComponent(id),text:"Histórico deste documento"})]));
    form.append(editable);view.append(form);
    const notice=node("p",{class:"status",role:"status","aria-live":"polite"});view.append(notice);
    let preview=null,formVersion=0;
    const changed=()=>{dirty=true;formVersion++;preview?.remove();preview=null;status(notice,"Há alterações ainda não salvas. Clique em Revisar alterações para conferir.");};
    form.addEventListener("input",changed);form.addEventListener("change",changed);
    form.addEventListener("submit",async event=>{
      event.preventDefault();submit.disabled=true;preview?.remove();
      const submittedVersion=formVersion;
      const value=key=>controls[key].value;
      const payload={revision:data.revision,document_id:id,document:{titles:{pt:value("pt"),ru:value("ru"),en:value("en")},kind:value("kind"),document_type:value("document_type")||null,
        author_label:value("author_label")||null,archive_reference:value("archive_reference")||null,
        historical_date:{display:value("date_display")||null,value:value("date_value")||null,precision:value("date_precision")},
        presentation:{shortTitle:value("shortTitle")||null,eyebrow:value("eyebrow")||null}},
        collection_ids:[...memberInputs].filter(([,input])=>input.checked).map(([key])=>key),
        issues:issueControls.map(({key,inputs})=>({chave:key,...Object.fromEntries(Object.entries(inputs).map(([k,input])=>[k,input.value]))}))};
      try {
        status(notice,"Preparando a prévia…");const result=await api("/api/editorial/preview",payload,signal);
        if(formVersion!==submittedVersion){status(notice,"O formulário mudou durante a preparação. Revise novamente para incluir as alterações mais recentes.");return;}
        preview=previewPanel(result,view,notice,(saved,panel)=>{
          editable.disabled=true;
          panel.append(node("div",{class:"actions"},[node("button",{type:"button",text:"Reabrir documento"}),node("a",{href:"#/historico?document="+encodeURIComponent(id),text:"Ver histórico / desfazer"})]));
          panel.querySelector("button").addEventListener("click",()=>route());
        },busy=>{editable.disabled=busy;});status(notice,"Confira os valores abaixo. Nada foi salvo ainda.");
      }catch(error){if(error.name!=="AbortError")status(notice,error.message,true);}
      finally{submit.disabled=false;}
    });
    const issue=params.get("pendencia");if(issue) document.getElementById("issue-"+issue)?.scrollIntoView({block:"start"});
  }

  function diffView(diff) {
    const details=node("details",{class:"import-diff",open:true},[node("summary",{text:"Diferenças linha a linha (+ inclusão, − remoção)"})]);
    details.append(node("pre",{text:diff.text||"Sem diferenças de texto."}));
    if(diff.truncated)details.append(node("p",{class:"help",text:"Comparação abreviada por tamanho. Confira também os textos completos abaixo; o arquivo será salvo inteiro."}));
    return details;
  }

  function markdownReading(content,language) {
    const section=node("section",{class:"markdown-reading"},[node("h3",{text:"Prévia renderizada"})]);
    const reading=node("div",{class:"import-reading",lang:language});
    const parser=markdownit({html:false,linkify:true,typographer:false}).use(markdownitFootnote);
    reading.innerHTML=DOMPurify.sanitize(parser.render(splitExportHeaders(content).body),{USE_PROFILES:{html:true},FORBID_TAGS:["style","form","input","button"],FORBID_ATTR:["style"]});
    for(const link of reading.querySelectorAll("a[href]"))if(!link.getAttribute("href").startsWith("#")){link.target="_blank";link.rel="noopener noreferrer";}
    reading.addEventListener("click",event=>{
      const link=event.target.closest("a[href^='#']");if(!link)return;event.preventDefault();
      let id;try{id=decodeURIComponent(link.getAttribute("href").slice(1));}catch{return;}
      [...reading.querySelectorAll("[id]")].find(element=>element.id===id)?.scrollIntoView({block:"nearest"});
    });
    for(const image of reading.querySelectorAll("img"))image.loading="lazy";
    section.append(reading);return section;
  }

  async function markdownPage(editionId,params,signal) {
    const data=await api("/api/editorial/editions/"+encodeURIComponent(editionId),null,signal);
    const contextData=await api("/api/editorial/documents/"+encodeURIComponent(data.document.id),null,signal);
    setDocumentContext(data.document,contextData.editions,data.edition.language);
    returnToReading(view,data.document.id);
    view.append(node("h1",{text:"Editar Markdown · "+data.edition.language.toUpperCase()}),node("p",{text:title(data.document)+" · "+data.edition.id}),
      node("p",{class:"help",text:"Você está editando esta versão do documento, inclusive se for o original russo. Somente Confirmar e salvar grava no acervo local. O conteúdo anterior fica no histórico; as outras versões não são alteradas."}),
      node("a",{href:routeURL("documento/"+encodeURIComponent(data.document.id),new URLSearchParams({idioma:data.edition.language})),text:"Editar metadados deste documento"}));
    const form=node("form");const editable=node("fieldset");
    const workspace=node("div",{class:"markdown-workspace"});
    const textarea=node("textarea",{class:"markdown-source",name:"markdown",rows:"24",spellcheck:"false","aria-label":"Conteúdo Markdown da versão selecionada"});
    textarea.value=data.content;
    const previewArea=node("div");
    workspace.append(node("label",{class:"field"},["Markdown completo que será salvo",textarea]),previewArea);
    const updatePreview=()=>{
      try{previewArea.replaceChildren(markdownReading(textarea.value,data.edition.language));}
      catch(error){previewArea.replaceChildren(node("p",{class:"status error",text:error.message}));}
    };
    const render=node("button",{type:"button",text:"Atualizar prévia"});render.addEventListener("click",updatePreview);
    const submit=node("button",{type:"submit",class:"primary",text:"Revisar alterações no Markdown"});
    editable.append(workspace,node("p",{class:"help",text:"A prévia separa o cabeçalho de exportação do corpo, como o leitor. Alterar um título dentro do Markdown não altera automaticamente os metadados do catálogo. Textos extensos atualizam a prévia pelo botão."}),
      node("div",{class:"actions"},[render,submit]));form.append(editable);view.append(form);
    const notice=node("p",{class:"status",role:"status","aria-live":"polite"});view.append(notice);
    let version=0,preview=null,timer;
    if(textarea.value.length<=200000)updatePreview();
    else previewArea.append(node("p",{class:"help",text:"Texto extenso. Clique em Atualizar prévia para renderizar quando desejar."}));
    textarea.addEventListener("input",()=>{
      dirty=true;version++;preview?.remove();preview=null;clearTimeout(timer);
      if(textarea.value.length<=200000)timer=setTimeout(()=>{if(!signal.aborted)updatePreview();},300);
      status(notice,"Há alterações ainda não salvas. Confira a prévia e revise antes de salvar.");
    });
    form.addEventListener("submit",async event=>{
      event.preventDefault();const submitted=version;submit.disabled=true;preview?.remove();
      try {
        status(notice,"Preparando diferenças e prévia. Nada foi salvo ainda…");
        const result=await api("/api/editorial/markdown/preview",{revision:data.revision,edition_id:data.edition.id,content_sha256:data.edition.sha256,content:textarea.value},signal);
        if(version!==submitted){status(notice,"O texto mudou durante a preparação. Revise novamente.");return;}
        preview=previewPanel(result,view,notice,(saved,panel)=>{
          editable.disabled=true;
          const reopen=node("button",{type:"button",text:"Reabrir esta versão"});reopen.addEventListener("click",()=>route());
          panel.append(node("div",{class:"actions"},[reopen,node("a",{href:"#/historico?document="+encodeURIComponent(saved.document_id),text:"Histórico / desfazer"})]));
        },busy=>{editable.disabled=busy;});
        status(notice,"Confira o conteúdo e as diferenças abaixo. Confirme somente se quiser gravar esta versão.");
      }catch(error){if(error.name!=="AbortError")status(notice,error.message,true);}
      finally{submit.disabled=false;}
    });
  }

  function translationDetails(translation) {
    const wrap=node("div",{class:"translation-preview"});
    wrap.append(node("h3",{text:translation.replaces?"Substituição da tradução existente":"Inclusão de uma nova tradução"}),
      node("p",{text:`Documento: ${translation.document_id} · ${translation.document_title}`}),
      node("p",{text:`Idioma selecionado: ${translation.language.toUpperCase()} · Original de referência: ${translation.original_language.toUpperCase()}`}),
      node("p",{class:"muted",text:"Arquivo no acervo: "+translation.target_file}));
    const identity=translation.identification;
    const identified=node("dl",{class:"import-identification"});
    for(const [caption,value]of [["Nome recebido",identity.filename],["IDs no cabeçalho",identity.document_ids.join(" · ")],["Idiomas no cabeçalho",identity.languages.join(" · ")],["Fontes no cabeçalho",identity.source_urls.join(" · ")],["Título no arquivo",identity.title]])
      identified.append(node("dt",{text:caption}),node("dd",{text:value||"Não declarado / não reconhecido"}));
    wrap.append(identified);
    if(translation.findings.length) {
      const findings=node("ul",{class:"import-findings"});
      for(const finding of translation.findings)findings.append(node("li",{class:finding.level==="warning"?"import-warning":"muted",text:finding.message}));
      wrap.append(findings);
    }else wrap.append(node("p",{class:"help",text:"Não foram encontradas divergências nos campos reconhecidos. Isso não confirma automaticamente a tradução nem o idioma do conteúdo."}));
    wrap.append(node("h3",{text:"Diagnóstico da estrutura — sem pareamento automático"}));
    const table=node("table");
    table.append(node("thead",{},[node("tr",{},["Estrutura","Original","Tradução atual","Arquivo enviado"].map(text=>node("th",{scope:"col",text})))]));
    const body=node("tbody");
    for(const [key,caption]of [["study_blocks","Blocos do corpo no modo estudo"],["paragraphs","Parágrafos aproximados"],["headings","Títulos do corpo"],["lists","Blocos de listas"],["tables","Blocos de tabelas"],["code_blocks","Blocos de código"],["export_headers","Cabeçalhos de exportação ignorados"]])
      body.append(node("tr",{},[node("th",{scope:"row",text:caption}),...["original","current","uploaded"].map(column=>node("td",{text:translation.structure[column]?.[key]??"—"}))]));
    table.append(body);wrap.append(node("div",{class:"table-scroll"},[table]));
    const same=translation.structure.original.study_blocks===translation.structure.uploaded.study_blocks;
    wrap.append(node("p",{class:same?"help":"import-warning",text:same
      ? "As quantidades de blocos do corpo coincidem, mas isso não comprova que cada trecho corresponda ao mesmo trecho do original. Confira o modo estudo depois de salvar."
      : "As quantidades de blocos do corpo diferem. Listas, tabelas e quebras de parágrafo podem deslocar as falas no modo estudo. A importação é permitida, sem juntar, dividir ou alinhar trechos automaticamente."}),
      node("p",{class:"help",text:"Cabeçalhos reconhecidos de exportação não entram na contagem nem no corpo renderizado. Títulos próprios do documento e quebras do corpo são preservados. Não há comparação semântica."}));
    if(translation.replaces)wrap.append(node("p",{class:"help",text:"As diferenças abaixo comparam o corpo do texto, sem os cabeçalhos reconhecidos de exportação. Os arquivos completos continuam disponíveis abaixo."}),diffView(translation.diff));
    const rendered=node("details",{class:"import-rendered",open:translation.content.length<=200000},[node("summary",{text:"Prévia renderizada do arquivo enviado"})]);
    const reading=node("div",{class:"import-reading",lang:translation.language});let renderedOnce=false;
    function render() {
      if(renderedOnce||!rendered.open)return;
      renderedOnce=true;
      try {
        const parser=markdownit({html:false,linkify:true,typographer:false}).use(markdownitFootnote);
        reading.innerHTML=DOMPurify.sanitize(parser.render(splitExportHeaders(translation.content).body),{USE_PROFILES:{html:true},FORBID_TAGS:["style","form","input","button"],FORBID_ATTR:["style"]});
        for(const link of reading.querySelectorAll("a[href]")) {
          if(!link.getAttribute("href").startsWith("#")){link.target="_blank";link.rel="noopener noreferrer";}
        }
        for(const image of reading.querySelectorAll("img"))image.loading="lazy";
      }catch(error){reading.textContent="Não foi possível renderizar a prévia. Confira o Markdown abaixo: "+error.message;}
    }
    reading.addEventListener("click",event=>{
      const link=event.target.closest("a[href^='#']");if(!link)return;
      event.preventDefault();
      let id;try{id=decodeURIComponent(link.getAttribute("href").slice(1));}catch{return;}
      const target=[...reading.querySelectorAll("[id]")].find(element=>element.id===id);target?.scrollIntoView({block:"nearest"});
    });
    rendered.append(reading);rendered.addEventListener("toggle",render);wrap.append(rendered);render();
    wrap.append(node("details",{},[node("summary",{text:"Markdown completo que será salvo"}),node("pre",{class:"import-source",text:translation.content})]));
    if(translation.replaces)wrap.append(node("details",{},[node("summary",{text:"Versão atual completa (será preservada no histórico)"}),node("pre",{class:"import-source",text:translation.current_content})]));
    return wrap;
  }

  async function importPage(params,signal) {
    if(readerReturn)returnToReading(view,params.get("documento")||"");
    view.append(node("h1",{text:"Importar tradução Markdown"}),node("p",{class:"help",text:"Escolha o documento, confirme o idioma e envie o arquivo. A prévia não grava nada; a tradução só entra no acervo local depois de Confirmar e salvar. Não há publicação automática."}));
    const chooser=node("form",{class:"panel"});const chooserFields=node("fieldset");
    const documentInput=field("ID do documento","document_id",params.get("documento"),{maxlength:200});
    documentInput.input.required=true;
    const choose=node("button",{type:"submit",text:"Selecionar documento"});
    chooserFields.append(documentInput.wrap,node("div",{class:"actions"},[choose,node("a",{href:"#/catalogo",text:"Procurar um documento pelo título"})]));
    chooser.append(chooserFields);view.append(chooser);
    const selected=node("section",{class:"panel import-selected",hidden:true});view.append(selected);
    const form=node("form",{class:"panel import-form"});const fields=node("fieldset",{disabled:true});
    const language=field("Idioma da tradução","language","",{choices:[["","Selecione explicitamente o idioma"]]});language.input.required=true;
    const filename=node("input",{type:"file",name:"markdown",accept:".md,.markdown,text/markdown,text/plain",required:true});
    const translationTitle=field("Título da tradução no catálogo (opcional)","title","",{maxlength:2000});
    const submit=node("button",{type:"submit",class:"primary",text:"Revisar importação",disabled:true});
    fields.append(language.wrap,node("label",{class:"field"},["Arquivo Markdown em UTF-8",filename]),translationTitle.wrap,
      node("p",{class:"help",text:"Arquivos .md ou .markdown de até 4 MiB. O conteúdo será mantido, incluindo cabeçalhos e quebras de parágrafo. O título opcional altera apenas o cadastro, sem reescrever o arquivo."}),
      node("div",{class:"actions"},[submit]));form.append(fields);view.append(form);
    const notice=node("p",{class:"status",role:"status","aria-live":"polite"});view.append(notice);
    let chosen=null,preview=null,version=0,selectionVersion=0,preparing=false;
    const ready=()=>{submit.disabled=preparing||saving||!chosen||!language.input.value||!filename.files?.length;};
    function invalidate(){version++;preview?.remove();preview=null;dirty=!!filename.files?.length;ready();}
    documentInput.input.addEventListener("input",()=>{
      selectionVersion++;chosen=null;fields.disabled=true;selected.hidden=true;invalidate();status(notice,"Selecione novamente o documento antes de continuar.");
    });
    form.addEventListener("input",invalidate);form.addEventListener("change",invalidate);
    language.input.addEventListener("change",()=>{
      translationTitle.input.value=chosen?.document.titles[language.input.value]||"";
      const exists=chosen?.editions.some(e=>e.language===language.input.value);
      status(notice,language.input.value?(exists?"Já existe uma tradução nesse idioma. A prévia mostrará as diferenças antes da substituição.":"Será incluída uma tradução nesse idioma."):"Selecione o idioma da tradução.");
    });
    async function selectDocument() {
      const attempt=++selectionVersion;choose.disabled=true;chosen=null;fields.disabled=true;invalidate();
      try {
        status(notice,"Localizando o documento…");
        const data=await api("/api/editorial/documents/"+encodeURIComponent(documentInput.input.value.trim()),null,signal);
        if(attempt!==selectionVersion)return;
        chosen=data;selected.hidden=false;
        selected.replaceChildren(node("h2",{text:"Documento selecionado: "+title(data.document)}),node("p",{text:data.document.id+" · Versões atuais: "+data.editions.map(e=>e.language.toUpperCase()).join(" · ")}),
          node("a",{href:"/#/doc/"+encodeURIComponent(data.document.id),target:"_blank",rel:"noopener",text:"Conferir o original no leitor ↗"}));
        const date=dateBadge(data.document);if(date)selected.append(date);
        const original=data.editions.find(e=>e.language===(data.document.source_metadata.original_language||"ru"))||data.editions[0];
        language.input.replaceChildren(node("option",{value:"",text:"Selecione explicitamente o idioma"}));
        for(const [code,caption]of [["pt","Português"],["en","Inglês"]])if(code!==original.language)
          language.input.append(node("option",{value:code,text:caption+(data.editions.some(e=>e.language===code)?" — substituir versão existente":" — nova versão")}));
        translationTitle.input.value="";fields.disabled=false;ready();
        status(notice,"Confira o documento acima, selecione o idioma e escolha o arquivo traduzido.");
      }catch(error){if(error.name!=="AbortError"&&attempt===selectionVersion)status(notice,error.message+". Use Editar catálogo para localizar o ID correto.",true);}
      finally{choose.disabled=false;}
    }
    chooser.addEventListener("submit",event=>{event.preventDefault();selectDocument();});
    form.addEventListener("submit",async event=>{
      event.preventDefault();if(!chosen)return;
      const file=filename.files?.[0];if(!file)return;
      preview?.remove();preview=null;preparing=true;ready();const submittedVersion=version;
      try {
        if(!/\.(md|markdown)$/i.test(file.name))throw new Error("Selecione um arquivo .md ou .markdown.");
        if(file.size>4*1024*1024)throw new Error("O arquivo deve ter no máximo 4 MiB.");
        let content;
        try{content=new TextDecoder("utf-8",{fatal:true,ignoreBOM:true}).decode(await file.arrayBuffer());}
        catch{throw new Error("Não foi possível ler o arquivo em UTF-8. Salve-o nessa codificação antes de importar.");}
        if(version!==submittedVersion)return;
        status(notice,"Preparando identificação, diferenças e diagnóstico. Nada será gravado nesta etapa…");
        const result=await api("/api/editorial/translations/preview",{revision:chosen.revision,document_id:chosen.document.id,
          language:language.input.value,filename:file.name,content,title:translationTitle.input.value},signal);
        if(version!==submittedVersion){status(notice,"A seleção mudou durante a preparação. Clique novamente em Revisar importação.");return;}
        preview=previewPanel(result,view,notice,(saved,panel)=>{
          fields.disabled=true;chooserFields.disabled=true;
          const again=node("button",{type:"button",text:"Importar outra tradução"});again.addEventListener("click",()=>route());
          panel.append(node("div",{class:"actions"},[node("a",{href:"/#/doc/"+encodeURIComponent(saved.document_id),target:"_blank",rel:"noopener",text:"Abrir documento atualizado ↗"}),
            node("a",{href:"#/historico?document="+encodeURIComponent(saved.document_id),text:"Ver histórico / desfazer"}),again]));
        },busy=>{fields.disabled=busy;chooserFields.disabled=busy;});
        status(notice,"Confira a identificação, o diagnóstico e a prévia abaixo. Nenhum arquivo foi salvo ainda.");
      }catch(error){if(error.name!=="AbortError")status(notice,error.message,true);}
      finally{preparing=false;ready();}
    });
    if(params.get("documento"))await selectDocument();
  }
  function slug(value) {
    return value.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"").slice(0,100).replace(/-$/g,"");
  }
  function collectionChoices(selected=[]) {
    const choices=node("div",{class:"collection-checks"});
    const inputs=new Map();
    for(const root of collections){
      const group=node("div",{class:"collection-group"});
      for(const item of [root,...root.children]){
        const input=node("input",{type:"checkbox",value:item.id,checked:selected.includes(item.id)});
        inputs.set(item.id,input);
        group.append(node("label",{class:item.parent_id?"child":""},[input,title(item)]));
        input.addEventListener("change",()=>{
          if(item.parent_id&&input.checked)inputs.get(item.parent_id).checked=true;
          if(!item.parent_id&&!input.checked)for(const child of root.children)inputs.get(child.id).checked=false;
        });
      }
      choices.append(group);
    }
    for(const root of collections)if(root.children.some(child=>inputs.get(child.id).checked))inputs.get(root.id).checked=true;
    return {element:choices,values:()=>[...inputs].filter(([,input])=>input.checked).map(([id])=>id)};
  }
  function bindCreation(form,fieldset,button,notice,payload,endpoint,afterSave,signal) {
    let preview=null,version=0;
    const invalidate=()=>{dirty=true;version++;preview?.remove();preview=null;status(notice,"Há alterações ainda não salvas. Revise antes de confirmar.");};
    form.addEventListener("input",invalidate);form.addEventListener("change",invalidate);
    form.addEventListener("submit",async event=>{
      event.preventDefault();const submitted=version;button.disabled=true;fieldset.disabled=true;preview?.remove();
      status(notice,"Preparando a prévia. Nenhum arquivo será gravado nesta etapa…");
      try{
        const proposed=await payload();
        if(signal.aborted||submitted!==version)return;
        const result=await api(endpoint,proposed,signal);
        if(signal.aborted||submitted!==version)return;
        if(result.can_save===false&&result.batch){
          preview=node("section",{class:"panel preview batch-errors",tabindex:"-1"},[
            node("h2",{text:"Corrija o lote antes de salvar"}),
            node("p",{text:result.batch.valid_count+" itens passaram pela conferência individual. Nenhum documento foi gravado."}),
            node("ul",{},result.batch.errors.map(error=>node("li",{text:(error.line?"Linha "+error.line+" · ":"")+(error.filename?error.filename+" · ":"")+error.message})))
          ]);
          view.append(preview);preview.focus();preview.scrollIntoView({block:"start",behavior:"smooth"});
          status(notice,"Há problemas no lote. Corrija a planilha/arquivos e gere uma nova prévia.",true);return;
        }
        preview=previewPanel(result,view,notice,afterSave,value=>{fieldset.disabled=value;});
        status(notice,"Confira a prévia e os destinos. Somente Confirmar e salvar grava no acervo local.");
      }catch(error){if(error.name!=="AbortError")status(notice,error.message,true);}
      finally{if(!signal.aborted){button.disabled=false;fieldset.disabled=false;}}
    });
  }
  async function newDocumentPage(params,signal) {
    view.append(node("h1",{text:"Novo documento"}),node("p",{class:"help",text:"Cadastre o arquivo original em Markdown ou TXT. Depois você poderá adicionar traduções. O cadastro só será gravado após revisar e confirmar."}));
    if(!collections.length){view.append(node("p",{text:"Crie uma coleção antes de cadastrar o documento."}),node("a",{href:"#/nova-colecao",text:"Criar coleção"}));return;}
    const revision=session.revision;
    const form=node("form",{class:"panel"});const fields=node("fieldset");const grid=node("div",{class:"fields"});
    const inputs={};
    const add=(caption,name,value="",options={})=>{const f=field(caption,name,value,options);inputs[name]=f.input;grid.append(f.wrap);return f.input;};
    const originalTitle=add("Título no idioma original","title","",{maxlength:2000});originalTitle.required=true;
    const id=add("Identificador para a URL","id","",{maxlength:100});id.required=true;id.pattern="[a-z0-9]+(-[a-z0-9]+)*";
    let customId=false;id.addEventListener("input",()=>customId=true);originalTitle.addEventListener("input",()=>{if(!customId)id.value=slug(originalTitle.value);});
    add("Idioma original","language","ru",{choices:[["ru","Russo"],["pt","Português"],["en","Inglês"]]});
    add("Título em português para o catálogo (opcional)","title_pt","",{maxlength:2000});
    inputs.language.addEventListener("change",()=>{
      const originalPortuguese=inputs.language.value==="pt";
      inputs.title_pt.closest("label").hidden=originalPortuguese;
      if(originalPortuguese)inputs.title_pt.value="";
    });
    add("Categoria","kind","document",{choices:Object.entries(vocabularies.kinds)});
    add("Tipo documental","document_type","",{choices:[["","Sem classificação específica"],...Object.entries(vocabularies.document_types).sort((a,b)=>a[1].localeCompare(b[1],"pt"))]});
    add("Data para exibição","date");add("Autoria","author");add("Referência arquivística","archive");add("Nome da fonte","source_name");
    add("URL da fonte","source_url","",{maxlength:2000}).type="url";add("ID na fonte (opcional)","source_id");
    fields.append(grid,node("p",{class:"help",text:"O identificador define uma URL permanente. Use letras minúsculas sem acentos, números e hífens; por exemplo, carta-exemplo-1937. O arquivo será copiado para originais/locais/, sem substituir documentos existentes."}));
    const file=node("input",{type:"file",accept:".md,.markdown,.txt,text/markdown,text/plain",required:true});
    fields.append(node("label",{class:"field wide"},["Arquivo original — UTF-8, até 4 MiB",file]),node("h2",{text:"Coleções e subcoleções"}));
    const choices=collectionChoices(params.get("colecao")?[params.get("colecao")]:[]);fields.append(choices.element);
    const submit=node("button",{type:"submit",class:"primary",text:"Revisar novo documento"});fields.append(node("div",{class:"actions"},[submit,node("a",{href:"#/nova-colecao",text:"Criar coleção"})]));form.append(fields);view.append(form);
    const notice=node("p",{class:"status",role:"status"});view.append(notice);
    bindCreation(form,fields,submit,notice,async()=>{
      const upload=file.files[0];if(!upload)throw new Error("Selecione o arquivo original.");
      if(upload.size>4*1024*1024)throw new Error("O arquivo deve ter no máximo 4 MiB.");
      let content;try{content=new TextDecoder("utf-8",{fatal:true,ignoreBOM:true}).decode(await upload.arrayBuffer());}catch{throw new Error("Salve o arquivo em UTF-8 antes de cadastrar.");}
      return {revision,...Object.fromEntries(Object.entries(inputs).map(([key,input])=>[key,input.value.trim()])),collection_ids:choices.values(),filename:upload.name,content};
    },"/api/editorial/documents/preview",(saved,panel)=>{
      panel.append(node("div",{class:"actions"},[node("a",{href:"#/documento/"+encodeURIComponent(saved.document_id),text:"Abrir cadastro do documento"}),node("a",{href:"/#/doc/"+encodeURIComponent(saved.document_id),text:"Ler documento"}),node("a",{href:"#/novo-documento",text:"Cadastrar outro documento"})]));
    },signal);
  }
  async function batchPage(params,signal) {
    view.append(node("h1",{text:"Importar documentos em lote"}),node("p",{class:"help",text:"Selecione uma planilha CSV e os arquivos originais correspondentes. Confira cada item antes de confirmar a gravação conjunta. Para traduções de documentos já cadastrados, use Importar tradução."}));
    const revision=session.revision;
    const template=node("button",{type:"button",text:"Baixar modelo CSV"});
    template.addEventListener("click",()=>{
      const content="\uFEFFarquivo;id;titulo;idioma;colecoes;titulo_pt;data\r\nlote-exemplo-a.pt.md;lote-exemplo-a;Primeiro documento de exemplo;pt;;;1937\r\nlote-exemplo-b.en.txt;lote-exemplo-b;Second example document;en;;;1938\r\n";
      const url=URL.createObjectURL(new Blob([content],{type:"text/csv;charset=utf-8"}));
      const link=node("a",{href:url,download:"modelo-documentos.csv"});document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
    });
    const reference=node("details",{},[node("summary",{text:"Colunas da planilha e identificadores das coleções"}),
      node("p",{class:"help",text:"Obrigatórias: arquivo, id, titulo, idioma (ru/pt/en). Opcionais: colecoes, titulo_pt, categoria, tipo_documental, data, autoria, referencia_arquivistica, nome_fonte, url_fonte, id_fonte. Cada arquivo deve aparecer exatamente uma vez. Em colecoes, separe IDs com |; deixe em branco para usar a seleção padrão abaixo. São aceitos CSV separados por ponto e vírgula, vírgula ou tabulação, com aspas quando necessário."})]);
    const ids=node("ul",{class:"batch-collection-reference"});
    for(const root of collections)for(const item of [root,...root.children])ids.append(node("li",{},[node("code",{text:item.id})," — "+title(item)]));
    reference.append(ids);view.append(node("div",{class:"actions"},[template,node("a",{href:"#/colecoes",text:"Organizar coleções"})]),reference);
    const form=node("form",{class:"panel"});const fields=node("fieldset");
    const csv=node("input",{type:"file",accept:".csv,text/csv",required:true});
    const files=node("input",{type:"file",accept:".md,.markdown,.txt,text/markdown,text/plain",multiple:true,required:true});
    fields.append(node("label",{class:"field"},["Planilha CSV em UTF-8 — até 1 MiB",csv]),
      node("label",{class:"field"},["Documentos originais — até 100 arquivos, 4 MiB por arquivo e 20 MiB no total",files]));
    const selection=node("p",{class:"help",role:"status",text:"Nenhum documento selecionado."});
    files.addEventListener("change",()=>{const list=[...files.files];selection.textContent=list.length+" documentos selecionados · "+(list.reduce((sum,file)=>sum+file.size,0)/(1024*1024)).toFixed(2)+" MiB";});
    fields.append(selection,node("h2",{text:"Coleções padrão (opcional)"}),node("p",{class:"help",text:"Esta seleção só vale nas linhas sem colecoes preenchidas. Uma subcoleção inclui sua coleção principal automaticamente."}));
    const choices=collectionChoices();fields.append(choices.element);
    const submit=node("button",{type:"submit",class:"primary",text:"Revisar lote"});fields.append(node("div",{class:"actions"},[submit]));form.append(fields);view.append(form);
    const notice=node("p",{class:"status",role:"status"});view.append(notice);
    bindCreation(form,fields,submit,notice,async()=>{
      const table=csv.files[0],uploads=[...files.files];
      if(!table||!uploads.length)throw new Error("Selecione o CSV e os documentos correspondentes.");
      if(table.size>1024*1024)throw new Error("A planilha deve ter no máximo 1 MiB.");
      if(uploads.length>100)throw new Error("Selecione no máximo 100 documentos por lote.");
      if(uploads.some(file=>file.size>4*1024*1024)||uploads.reduce((sum,file)=>sum+file.size,0)>20*1024*1024)throw new Error("Respeite 4 MiB por documento e 20 MiB no total.");
      const decode=async file=>{try{return new TextDecoder("utf-8",{fatal:true,ignoreBOM:true}).decode(await file.arrayBuffer());}catch{throw new Error("Não foi possível ler "+file.name+" em UTF-8.");}};
      const csvContent=await decode(table),uploaded=[];
      for(const file of uploads){if(signal.aborted)throw new DOMException("Navegação cancelada","AbortError");uploaded.push({filename:file.name,content:await decode(file)});}
      return {revision,csv_content:csvContent,files:uploaded,collection_ids:choices.values()};
    },"/api/editorial/batches/preview",(saved,panel)=>{
      panel.append(node("p",{text:saved.entity.document_ids.length+" documentos cadastrados. Cada um foi incluído na fila de revisão."}),node("div",{class:"actions"},[
        node("a",{href:routeURL("historico",new URLSearchParams({document:saved.entity.id})),text:"Histórico do lote / desfazer"}),
        node("a",{href:"#/catalogo",text:"Abrir catálogo"}),node("a",{href:"#/lote",text:"Importar outro lote"})]));
      panel.append(node("details",{},[node("summary",{text:"Documentos cadastrados"}),node("ul",{},saved.entity.document_ids.map(id=>node("li",{},[
        node("a",{href:"#/documento/"+encodeURIComponent(id),text:id}),node("a",{href:"/#/doc/"+encodeURIComponent(id),text:"Ler documento"})
      ])))]));
    },signal);
  }
  async function collectionsPage(params,signal) {
    view.append(node("h1",{text:"Coleções e subcoleções"}),node("p",{class:"help",text:"Crie coleções, organize subcoleções e revise seus títulos, descrição e capa. A associação dos documentos é feita no cadastro de cada documento."}),node("a",{href:"#/nova-colecao",text:"Nova coleção"}));
    for(const root of collections){
      const panel=node("section",{class:"panel"},[node("h2",{text:title(root)}),node("p",{class:"muted",text:root.id+" · "+root.document_count+" documentos"})]);
      panel.append(node("div",{class:"actions"},[node("a",{href:"#/colecao/"+encodeURIComponent(root.id),text:"Editar coleção"}),node("a",{href:routeURL("nova-colecao",new URLSearchParams({pai:root.id})),text:"Nova subcoleção"}),node("a",{href:routeURL("novo-documento",new URLSearchParams({colecao:root.id})),text:"Novo documento"}),node("a",{href:"/#/colecao/"+root.slug,text:"Ver no site"})]));
      for(const child of root.children)panel.append(node("div",{class:"collection-list-child"},[node("span",{text:title(child)+" · "+child.document_count+" documentos"}),node("a",{href:"#/colecao/"+encodeURIComponent(child.id),text:"Editar subcoleção"})]));
      view.append(panel);
    }
  }
  async function collectionForm(id,params,signal) {
    const data=id?await api("/api/editorial/collections/"+encodeURIComponent(id),null,signal):null;
    const collection=data?.collection;const revision=data?.revision||session.revision;
    const initialParent=collection?.parent_id||params.get("pai")||"";
    view.append(node("h1",{text:collection?"Editar "+(collection.parent_id?"subcoleção":"coleção"):initialParent?"Nova subcoleção":"Nova coleção"}),node("p",{class:"help",text:"Revise antes de salvar. Coleções e subcoleções novas entram ao final das listas. Identificadores existentes são preservados para manter as URLs."}));
    const form=node("form",{class:"panel"});const fields=node("fieldset");const grid=node("div",{class:"fields"});const inputs={};
    const add=(caption,name,value="",options={})=>{const f=field(caption,name,value,options);inputs[name]=f.input;grid.append(f.wrap);return f.input;};
    const name=add("Título em português","title_pt",collection?.titles.pt||"",{maxlength:2000});name.required=true;
    const slugInput=add("Identificador","slug",collection?.slug||"",{maxlength:100});slugInput.required=true;slugInput.pattern="[a-z0-9]+(-[a-z0-9]+)*";
    const parent=add("Coleção principal","parent_id",initialParent,{choices:[["","Nenhuma — criar coleção principal"],...collections.map(item=>[item.id,title(item)])]});
    if(collection){slugInput.readOnly=true;parent.disabled=true;}
    let customSlug=!!collection;slugInput.addEventListener("input",()=>customSlug=true);name.addEventListener("input",()=>{if(!customSlug)slugInput.value=slug(name.value);});
    add("Título em russo (opcional)","title_ru",collection?.titles.ru||"",{maxlength:2000});add("Subtítulo","subtitle",collection?.subtitle||"",{maxlength:2000});
    add("Descrição","description",collection?.description||"",{multiline:true,maxlength:12000,wide:true});
    add("Capa existente em assets/covers/ (opcional)","cover",collection?.presentation.cover||"",{maxlength:1000});
    add("Cor de destaque","accent",collection?.presentation.accent||"#8b2c2c",{maxlength:7});
    add("URL da fonte (opcional)","source_url",collection?.source.url||"",{maxlength:2000}).type="url";
    fields.append(grid,node("p",{class:"help",text:"A capa pode ficar em branco. Para usar uma imagem, coloque-a em assets/covers/ e informe o caminho, por exemplo assets/covers/minha-colecao.jpg. O cadastro não move nem substitui imagens."}));
    const submit=node("button",{type:"submit",class:"primary",text:"Revisar coleção"});fields.append(node("div",{class:"actions"},[submit,node("a",{href:"#/colecoes",text:"Voltar às coleções"})]));form.append(fields);view.append(form);
    const notice=node("p",{class:"status",role:"status"});view.append(notice);
    bindCreation(form,fields,submit,notice,async()=>({revision,collection_id:id||null,...Object.fromEntries(Object.entries(inputs).map(([key,input])=>[key,input.value.trim()]))}),"/api/editorial/collections/preview",(saved,panel)=>{
      const savedId=saved.entity.id;const [root,child]=savedId.split("/");
      panel.append(node("div",{class:"actions"},[node("a",{href:"#/colecoes",text:"Abrir coleções"}),node("a",{href:"/#/colecao/"+root+(child?"/subcolecao/"+child:""),text:"Ver no site"}),node("a",{href:routeURL("novo-documento",new URLSearchParams({colecao:savedId})),text:"Cadastrar documento nesta coleção"}),node("a",{href:routeURL("historico",new URLSearchParams({document:savedId})),text:"Histórico / desfazer"})]));
    },signal);
  }
  async function historyPage(params,signal) {
    view.append(node("h1",{text:"Histórico recuperável"}),node("p",{class:"help",text:"Cada gravação guarda o estado anterior e posterior dos arquivos alterados. Restaurar cria uma nova alteração com prévia. Se houver edições posteriores nos mesmos arquivos, desfaça primeiro as mais recentes. O histórico é local, em .local/editorial/history/, e não é enviado ao GitHub."}));
    const form=node("form",{class:"panel"});const input=field("ID do documento, coleção ou lote (opcional)","document",params.get("document"));
    form.append(input.wrap,node("div",{class:"actions"},[node("button",{type:"submit",text:"Filtrar histórico"}),node("a",{href:"#/historico",text:"Todos"})]));
    form.addEventListener("submit",event=>{event.preventDefault();const p=new URLSearchParams();if(input.input.value.trim())p.set("document",input.input.value.trim());navigate(routeURL("historico",p));});view.append(form);
    const data=await api("/api/editorial/history?"+new URLSearchParams(params.get("document")?{document:params.get("document")}:{}),null,signal);
    if(!data.items.length)view.append(node("p",{text:"Nenhuma gravação registrada para este filtro. O histórico começa com as alterações feitas pela área editorial."}));
    for(const record of data.items) {
      const panel=node("article",{class:"panel"});
      panel.append(node("h2",{text:(record.entity?.id||record.document_id||"Coleção")+" · "+new Date(record.created_at).toLocaleString("pt-BR")}),node("p",{class:"muted",text:label(record.state)+" · "+record.id}),node("p",{class:"summary",text:record.summary}));
      const details=node("details",{},[node("summary",{text:"Ver alterações"}),comparison(record.changes)]);panel.append(details);
      const notice=node("p",{role:"status",class:"status"});
      if(record.state==="committed") {
        const restore=node("button",{type:"button",text:"Revisar restauração"});
        let preview;
        restore.addEventListener("click",async()=>{
          restore.disabled=true;preview?.remove();
          try {
            const live=await api("/api/editorial/session",null,signal);session=live;
            const result=await api("/api/editorial/preview",{revision:live.revision,restore_id:record.id},signal);
            preview=previewPanel(result,panel,notice,(saved,confirmation)=>{restore.disabled=true;confirmation.append(node("button",{type:"button",text:"Atualizar histórico"}));confirmation.querySelector("button").addEventListener("click",()=>route());});
            status(notice,"A restauração ainda não foi salva. Revise e confirme abaixo.");
          }catch(error){if(error.name!=="AbortError")status(notice,error.message,true);}
          finally{restore.disabled=false;}
        });
        panel.append(node("div",{class:"actions"},[restore,node("a",{href:record.entity?.kind==="collection"?"#/colecoes":"#/catalogo",text:record.entity?.kind==="collection"?"Abrir coleções":"Abrir catálogo"})]));
      }
      panel.append(notice);view.append(panel);
    }
  }
  async function route() {
    if(saving){history.replaceState(null,"",lastHash);return;}
    if(dirty&&!confirm("Há alterações ainda não salvas. Deseja sair desta edição?")){history.replaceState(null,"",lastHash);return;}
    dirty=false;lastHash=location.hash||"#/fila";
    controller?.abort();controller=new AbortController();const signal=controller.signal;
    const [path,query=""]=lastHash.replace(/^#\//,"").split("?");const params=new URLSearchParams(query);
    if(params.has("leitor"))readerReturn=safeReaderReturn(params.get("leitor"));
    document.body.dataset.editorialView=path.split("/")[0];
    const active=path==="nova-colecao"||path.startsWith("colecao/")?"colecoes":path.startsWith("markdown")?"markdown":path.startsWith("documento/")?"catalogo":path.split("/")[0]||"fila";
    for(const link of document.querySelectorAll(".editorial-sidebar nav a")) {
      if(link.getAttribute("href").split("?")[0]==="#/"+active)link.setAttribute("aria-current","page");
      else link.removeAttribute("aria-current");
    }
    if(["novo-documento","lote","colecoes","nova-colecao"].includes(path)||path.startsWith("colecao/")){
      documentContext=null;document.querySelector("[data-markdown-nav]").href="#/markdown";
    }
    document.querySelector(".sidebar-document").hidden=!documentContext;
    view.replaceChildren();view.focus();window.scrollTo({top:0});
    try {
      const [freshSession,freshCollections]=await Promise.all([api("/api/editorial/session",null,signal),api("/api/collections",null,signal)]);
      if(signal.aborted)return;
      session=freshSession;collections=freshCollections.items;
      if(path==="lote")await batchPage(params,signal);
      else if(path==="novo-documento")await newDocumentPage(params,signal);
      else if(path==="colecoes")await collectionsPage(params,signal);
      else if(path==="nova-colecao")await collectionForm(null,params,signal);
      else if(path.startsWith("colecao/"))await collectionForm(decodeURIComponent(path.slice(8)),params,signal);
      else if(path==="importar")await importPage(params,signal);
      else if(path==="markdown")await markdownChooser(params,signal);
      else if(path.startsWith("markdown/"))await markdownPage(decodeURIComponent(path.slice(9)),params,signal);
      else if(path.startsWith("documento/"))await documentPage(decodeURIComponent(path.slice(10)),params,signal);
      else if(path==="historico")await historyPage(params,signal);
      else await listPage(path==="catalogo"?"catalogo":"fila",params,signal);
    }catch(error){
      if(error.name!=="AbortError") {
        const reload=node("button",{type:"button",text:"Recarregar a área editorial"});
        reload.addEventListener("click",()=>location.reload());
        view.append(node("p",{class:"status error",role:"alert",text:error.message}),reload);
      }
    }
  }
  window.addEventListener("beforeunload",event=>{if(dirty||saving){event.preventDefault();event.returnValue="";}});
  document.addEventListener("click",event=>{
    const anchor=event.target.closest("a[href]");if(!anchor)return;
    const href=anchor.getAttribute("href");if(href.startsWith("#/"))anchor.setAttribute("href",withReaderContext(href));
  });
  async function start() {
    try {
      vocabularies=await api("/api/vocabularies");
      window.addEventListener("hashchange",route);await route();
    }catch(error){view.replaceChildren(node("p",{role:"alert",class:"status error",text:error.message+". Reinicie com python3 -m backend e recarregue esta página."}));}
  }
  start();
})();
