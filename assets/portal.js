/* Portal público: catálogo vivo e recorte explicitamente identificado do Git. */
function archiveDocuments() {
  const documents=new Map(state.documentIndex);
  for(const collection of state.manifest.collections)
    for(const doc of collectionDocuments(collection))if(doc)documents.set(doc.id,doc);
  return documents;
}

function createPortalIntro() {
  const documents=[...archiveDocuments().values()],format=new Intl.NumberFormat("pt-BR");
  const wrap=el("div",{class:"portal-opening"});
  const hero=el("section",{class:"portal-hero"});
  const intro=el("div",{class:"portal-intro"},[
    el("p",{class:"doc-eyebrow",text:"Documentos Soviéticos / Edição digital de fontes"}),
    el("h1",{},["Um arquivo aberto",el("br"),"à ",el("em",{text:"pesquisa."})]),
    el("p",{class:"portal-lead",text:"História política da União Soviética em documentos, traduções e percursos de leitura. Das coleções à comparação entre fontes."})
  ]);
  const search=el("form",{class:"home-search",role:"search","aria-label":"Buscar no acervo"});
  const query=el("input",{type:"search",name:"q",maxlength:"500",placeholder:"Encontre uma fonte, um nome, uma expressão…","aria-label":"Palavras para buscar no acervo"});
  search.append(query,el("button",{type:"submit",class:"search-submit",text:"Buscar →"}));
  search.addEventListener("submit",event=>{event.preventDefault();const params=new URLSearchParams();if(query.value.trim())params.set("q",query.value.trim());location.hash=searchURL(params);});
  intro.append(search,el("p",{class:"home-search-hint",text:"Coleções, originais e traduções em português, russo e inglês."}));
  const featured=state.manifest.collections.find(c=>c.id==="centro-de-moscou")||state.manifest.collections[0];
  hero.append(intro);
  if(featured){
    const cover=el("div",{class:"feature-cover"});
    if(featured.cover)cover.append(el("img",{src:absURL(featured.cover),alt:"",loading:"lazy"}));
    hero.append(el("a",{class:"portal-feature",href:"#/colecao/"+featured.id},[cover,el("div",{},[
      el("p",{class:"doc-eyebrow",text:"Percurso pelo acervo"}),el("h2",{text:featured.title_pt}),
      el("p",{text:collectionDocuments(featured).length+" documentos · fontes e traduções"}),el("span",{text:"Conhecer a coleção ↗"})]) ]));
  }
  const strip=el("div",{class:"acervo-strip","aria-label":"Dados do catálogo"});
  for(const [number,label] of [[documents.length,"documentos únicos"],[state.manifest.collections.length,"coleções"],
    [documents.filter(d=>d.languages?.some(l=>l.code==="pt")).length,"documentos em português"],
    [documents.reduce((sum,d)=>sum+(d.languages?.length||0),0),"versões linguísticas"]])
    strip.append(el("span",{},[el("strong",{text:format.format(number)})," "+label]));
  const updates=el("section",{class:"portal-updates","aria-label":"Incorporações registradas no acervo"},[
    el("div",{class:"archive-section-heading"},[el("div",{},[el("p",{class:"doc-eyebrow",text:"Acervo em movimento"}),el("h2",{text:"Traduções e versões incorporadas"})]),
      el("a",{class:"portal-text-link",href:"#/busca",text:"Consultar o catálogo ↗"})]),
    el("div",{class:"update-grid",role:"status",text:"Carregando os registros de incorporação…"}),
    el("p",{class:"activity-note",text:"Recorte do histórico Git local: datas de incorporação, não datas históricas nem confirmação de publicação online."})
  ]);
  const feed=el("div",{class:"portal-source-area"},[el("div",{class:"archive-section-heading"},[
    el("div",{},[el("p",{class:"doc-eyebrow",text:"Entradas no histórico"}),el("h2",{text:"Fontes incorporadas"})])]),el("div",{class:"source-feed"})]);
  const invitation=el("aside",{class:"research-invitation"},[
    el("p",{class:"doc-eyebrow",text:"Além da leitura"}),el("h2",{text:"Seu espaço de trabalho com as fontes."}),
    el("p",{text:"Abra documentos em abas. Consulte o Markdown ao lado do texto, compare versões e reúna notas de trabalho."}),
    el("a",{class:"portal-primary",href:archiveWorkspace.defaultURL(),text:"Abrir a bancada →"}),
    el("p",{class:"portal-small",text:"Leitura e rascunhos no navegador. Gravações editoriais disponíveis com o backend local."})
  ]);
  wrap.append(hero,strip,updates,el("section",{class:"portal-lower"},[feed,invitation]));return wrap;
}

async function loadPortalActivity(root) {
  const updates=root.querySelector(".update-grid"),sources=root.querySelector(".source-feed");
  try{
    const activity=await fetchJSON("assets/acervo-activity.json"),documents=archiveDocuments();
    if(!root.isConnected)return;
    const recent=[],originals=[],seen=new Set(),sourceSeen=new Set();
    for(const event of activity.events||[]){
      for(const item of event.examples||[])if(!item.languages.includes("ru")&&!seen.has(item.id)&&documents.has(item.id)){recent.push({...item,event});seen.add(item.id);}
      for(const item of event.source_examples||[])if(!sourceSeen.has(item.id)&&documents.has(item.id)){originals.push({...item,event});sourceSeen.add(item.id);}
    }
    const stamp=value=>{const date=new Date(value);return Number.isNaN(date.getTime())?"Registro no Git":new Intl.DateTimeFormat("pt-BR",{day:"2-digit",month:"short",year:"numeric"}).format(date);};
    updates.replaceChildren();updates.removeAttribute("role");
    for(const item of recent.slice(0,4)){
      const doc=documents.get(item.id);
      updates.append(el("a",{class:"update-card",href:"#/doc/"+doc.id},[
        el("div",{class:"update-top"},[el("span",{class:"language-pill",text:item.languages.map(l=>l.toUpperCase()).join(" + ")}),el("time",{datetime:item.event.recorded_at,text:stamp(item.event.recorded_at)})]),
        el("h3",{text:documentTitle(doc)}),el("p",{text:documentDateInfo(doc)?.text||doc.id}),el("span",{class:"update-link",text:"Ler documento ↗"})]));
    }
    if(!recent.length)updates.append(el("p",{text:"Nenhuma versão localizada neste recorte do histórico."}));
    for(const item of originals.slice(0,3)){
      const doc=documents.get(item.id);sources.append(el("a",{href:"#/doc/"+doc.id},[
        el("div",{},[el("span",{text:stamp(item.event.recorded_at)+" · RU"}),el("h3",{text:documentTitle(doc)}),el("p",{text:doc.id+(documentDateInfo(doc)?" · "+documentDateInfo(doc).text:"")})]),el("span",{text:"↗","aria-hidden":"true"})]));
    }
    if(!originals.length)sources.append(el("p",{text:"Nenhuma fonte russa localizada neste recorte."}));
  }catch{
    if(root.isConnected){updates.textContent="O histórico de incorporações não pôde ser carregado. As coleções e a busca continuam disponíveis.";sources.textContent="Consulte o catálogo para explorar as fontes.";}
  }
}
