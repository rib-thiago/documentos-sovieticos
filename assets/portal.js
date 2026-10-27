/* Portal público: catálogo vivo e recorte explicitamente identificado do Git. */
function archiveDocuments() {
  const documents=new Map(state.documentIndex);
  for(const collection of state.manifest.collections)
    for(const doc of collectionDocuments(collection))if(doc)documents.set(doc.id,doc);
  return documents;
}

function createPortalIntro() {
  const documents=[...archiveDocuments().values()],format=new Intl.NumberFormat("pt-BR");
  const wrap=el("div",{class:"portal-opening portal-frontpage"});
  const hero=el("section",{class:"portal-hero portal-hero-v2"});
  const intro=el("div",{class:"portal-intro"},[
    el("p",{class:"doc-eyebrow",text:"Documentos Soviéticos / Edição digital de fontes"}),
    el("h1",{},["História soviética.",el("br"),el("em",{text:"Fontes para investigar."})]),
    el("p",{class:"portal-lead",text:"Leia documentos históricos, percorra as coleções e compare originais e traduções em uma mesma mesa de estudo."})
  ]);
  const search=el("form",{class:"home-search",role:"search","aria-label":"Buscar no acervo"});
  const query=el("input",{type:"search",name:"q",maxlength:"500",placeholder:"Encontre uma fonte, um nome, uma expressão…","aria-label":"Palavras para buscar no acervo"});
  search.append(query,el("button",{type:"submit",class:"search-submit",text:"Buscar →"}));
  search.addEventListener("submit",event=>{event.preventDefault();const params=new URLSearchParams();if(query.value.trim())params.set("q",query.value.trim());location.hash=searchURL(params);});
  intro.append(search,el("div",{class:"portal-entry-links"},[el("a",{href:"#/colecoes",text:"Explorar as coleções →"}),el("a",{href:"#/estudo",text:"Abrir mesa de estudo ↗"})]));
  hero.append(intro);
  const collections=[...state.manifest.collections];
  const carousel=el("section",{class:"portal-carousel",role:"region","aria-roledescription":"carrossel","aria-label":"Percursos pelo acervo"});
  const stage=el("div",{class:"portal-carousel-stage"});
  const counter=el("span",{class:"carousel-counter","aria-live":"polite"});
  let current=0;
  const show=index=>{
    current=(index+collections.length)%collections.length;
    const featured=collections[current];if(!featured)return;
    const cover=el("div",{class:"feature-cover"});
    if(featured.cover)cover.append(el("img",{src:absURL(featured.cover),alt:"",loading:"lazy"}));
    else cover.append(archiveIcon("catalog"));
    stage.replaceChildren(el("a",{class:"portal-feature",href:"#/colecao/"+featured.id},[cover,el("div",{},[
      el("p",{class:"doc-eyebrow",text:"Percurso pelo acervo"}),el("h2",{text:featured.title_pt}),
      el("p",{text:collectionDocuments(featured).length+" documentos · "+(featured.subcollections?.length||0)+" subcoleções"}),
      el("span",{text:"Conhecer a coleção ↗"})])]));
    counter.textContent=(current+1)+" / "+collections.length;
  };
  const previous=el("button",{type:"button","aria-label":"Coleção anterior",text:"←"});
  const next=el("button",{type:"button","aria-label":"Próxima coleção",text:"→"});
  previous.onclick=()=>show(current-1);next.onclick=()=>show(current+1);
  carousel.addEventListener("keydown",event=>{if(event.key==="ArrowLeft"||event.key==="ArrowRight"){event.preventDefault();show(current+(event.key==="ArrowRight"?1:-1));}});
  carousel.append(stage,el("div",{class:"carousel-controls"},[previous,counter,next]));
  if(collections.length)show(0);
  const strip=el("div",{class:"acervo-strip portal-snapshot","aria-label":"Dados atuais do catálogo"});strip.append(el("p",{class:"doc-eyebrow",text:"O acervo, hoje"}));
  for(const [number,label] of [[documents.length,"documentos únicos"],[state.manifest.collections.length,"coleções"],
    [documents.filter(d=>d.languages?.some(l=>l.code==="pt")).length,"documentos em português"],
    [documents.reduce((sum,d)=>sum+(d.languages?.length||0),0),"versões linguísticas"]])
    strip.append(el("span",{},[el("strong",{text:format.format(number)})," "+label]));
  const updates=el("section",{class:"portal-updates","aria-label":"Incorporações registradas no acervo"},[
    el("div",{class:"archive-section-heading"},[el("div",{},[el("p",{class:"doc-eyebrow",text:"Acervo em movimento"}),el("h2",{text:"Para continuar a pesquisa"})]),
      el("a",{class:"portal-text-link",href:"#/busca",text:"Consultar o catálogo ↗"})]),
    el("div",{class:"update-grid",role:"status",text:"Carregando os registros de incorporação…"}),
    el("p",{class:"activity-note",text:"Datas de incorporação no Git ou de coleta registrada na proveniência; não são datas históricas dos documentos."})
  ]);
  const feed=el("div",{class:"portal-source-area"},[el("div",{class:"archive-section-heading"},[
    el("div",{},[el("p",{class:"doc-eyebrow",text:"Entradas no histórico"}),el("h2",{text:"Documentos incorporados"})])]),el("div",{class:"source-feed"})]);
  const invitation=el("aside",{class:"research-invitation"},[
    el("p",{class:"doc-eyebrow",text:"Além da leitura"}),el("h2",{text:"Coloque as fontes em diálogo."}),
    el("p",{text:"Compare idiomas e documentos lado a lado. Destaque o índice, consulte a ficha e reúna suas notas de leitura."}),
    el("a",{class:"portal-primary",href:archiveWorkspace.defaultURL(),text:"Abrir a mesa de estudo →"}),
    el("p",{class:"portal-small",text:"Consulta e notas pessoais no navegador. Edição do acervo no Estúdio local."})
  ]);
  hero.append(strip);
  const aside=el('aside',{class:'portal-discovery'},[el('div',{class:'archive-section-heading'},[el('h2',{text:'Coleção em foco'}),el('a',{href:'#/colecoes',text:'Ver todas →'})]),carousel,invitation]);
  wrap.append(hero,el('div',{class:'portal-content-grid'},[updates,aside]),el('section',{class:'portal-recent-sources'},[feed]));return wrap;
}

async function loadPortalActivity(root) {
  const updates=root.querySelector(".update-grid"),sources=root.querySelector(".source-feed");
  try{
    const activity=await fetchJSON("assets/acervo-activity.json"),documents=archiveDocuments();
    if(!root.isConnected)return;
    const recent=[],originals=[],seen=new Set(),sourceSeen=new Set();
    for(const event of activity.events||[]){
      for(const item of event.examples||[])if(item.languages.some(code=>code!=="ru")&&!seen.has(item.id)&&documents.has(item.id)){recent.push({...item,event});seen.add(item.id);}
      for(const item of event.source_examples||[])if(!sourceSeen.has(item.id)&&documents.has(item.id)){originals.push({...item,event});sourceSeen.add(item.id);}
    }
    const stamp=value=>{const date=new Date(value);return Number.isNaN(date.getTime())?"Registro no Git":new Intl.DateTimeFormat("pt-BR",{day:"2-digit",month:"short",year:"numeric"}).format(date);};
    updates.replaceChildren();updates.removeAttribute("role");
    let page=0;
    const renderRecent=()=>{
    updates.replaceChildren();
    for(const item of recent.slice(page*4,page*4+4)){
      const doc=documents.get(item.id);
      updates.append(el("a",{class:"update-card",href:"#/doc/"+doc.id},[
        el("div",{class:"update-top"},[el("span",{class:"language-pill",text:item.languages.map(l=>l.toUpperCase()).join(" + ")}),el("time",{datetime:item.event.recorded_at,text:stamp(item.event.recorded_at)})]),
        el("h3",{text:documentTitle(doc),title:documentTitle(doc)}),el("p",{text:(item.event.basis?"Versão coletada · ":"Incorporação · ")+(documentDateInfo(doc)?.text||doc.id)}),el("span",{class:"update-link",text:"Ler documento ↗"})]));
    }
    if(!recent.length)updates.append(el("p",{text:"Nenhuma versão localizada neste recorte do histórico."}));
    };
    renderRecent();
    if(recent.length>4){
      const previous=el("button",{type:"button",text:"← Mais recentes"});
      const next=el("button",{type:"button",text:"Anteriores →"});
      const status=el("span",{"aria-live":"polite"});
      const refresh=()=>{previous.disabled=page===0;next.disabled=(page+1)*4>=recent.length;status.textContent=(page+1)+" / "+Math.ceil(recent.length/4);};
      previous.onclick=()=>{page--;renderRecent();refresh();};next.onclick=()=>{page++;renderRecent();refresh();};
      refresh();updates.after(el("div",{class:"carousel-controls activity-controls"},[previous,status,next]));
    }
    for(const item of originals.slice(0,3)){
      const doc=documents.get(item.id);sources.append(el("a",{href:"#/doc/"+doc.id},[
        el("div",{},[el("span",{text:stamp(item.event.recorded_at)+" · "+item.languages.map(code=>code.toUpperCase()).join(" + ")}),el("h3",{text:documentTitle(doc)}),el("p",{text:doc.id+(documentDateInfo(doc)?" · "+documentDateInfo(doc).text:"")})]),el("span",{text:"↗","aria-hidden":"true"})]));
    }
    if(!originals.length)sources.append(el("p",{text:"Nenhuma fonte localizada neste recorte."}));
  }catch{
    if(root.isConnected){updates.textContent="O histórico de incorporações não pôde ser carregado. As coleções e a busca continuam disponíveis.";sources.textContent="Consulte o catálogo para explorar as fontes.";}
  }
}
