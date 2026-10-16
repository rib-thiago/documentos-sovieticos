/* =========================================================
   Site bilíngue/trilíngue: coleções de documentos soviéticos.
   ========================================================= */

const state = {
  manifest: null,
  editorialAvailable: false,
  routeVersion: 0,
  cache: new Map(),
  documentIndex: new Map(),
  activeCollection: null,
  viewMode: "reading",
  studyMode: "paragraph",
  activeDocument: null,
  readingLanguages: new Map(),
  readingTracker: null,
  parallelCols: { left: null, right: null },
};

async function fetchText(url) {
  const r = await fetch(encodeURI(url), { cache: "no-cache" });
  if (!r.ok) throw new Error(`Falha ao carregar ${url}: ${r.status}`);
  return r.text();
}
async function fetchJSON(url) {
  const r = await fetch(encodeURI(url), { cache: "no-cache" });
  if (!r.ok) throw new Error(`Falha ao carregar ${url}: ${r.status}`);
  return r.json();
}
function absURL(path) { return new URL(path, document.baseURI).href; }

/* ---------- Segmentação legada, usada apenas nas ferramentas de estudo ---------- */

function normalizeHeadingLevel(text, mdLevel) {
  if (/^[IVX]+\.\s/.test(text)) return Math.max(mdLevel, 2);
  if (/^\d+[.)]\s/.test(text)) return Math.max(mdLevel, 3);
  return mdLevel;
}

// As exportações ShowTrials são texto: asteriscos e outros sinais pertencem à fonte.
function parsePlainText(text) {
  return text.replace(/\r\n/g, "\n").split(/\n\s*\n/)
    .map(text => text.trim()).filter(Boolean)
    .map(text => ({ type: "text", text }));
}

function parseStudyMarkdown(md) {
  const chunks=[];
  const separator=/\r?\n(?:\r?\n)+/g;
  let cursor=0,match;
  while((match=separator.exec(md))){chunks.push({raw:md.slice(cursor,match.index),offset:cursor});cursor=separator.lastIndex;}
  chunks.push({raw:md.slice(cursor),offset:cursor});
  const blocks = [];
  for (const part of chunks) {
    const trimmed=part.raw.trim();
    const start=part.offset+part.raw.length-part.raw.trimStart().length;
    const push=block=>blocks.push({...block,sourceStart:start,sourceEnd:start+trimmed.length,sourceMarkdown:trimmed});
    const chunk = trimmed.replace(/\r\n/g,"\n");
    if (!chunk) continue;
    if (/^-{3,}$/.test(chunk)) continue;

    if (!chunk.includes("\n")) {
      const h = chunk.match(/^(#{1,6})\s+(.+)$/);
      if (h) {
        const level = h[1].length;
        push({
          type: "h" + normalizeHeadingLevel(h[2].trim(), level),
          text: h[2].trim(),
        });
        continue;
      }
      if (/^!\[.*?\]\(.+?\)$/.test(chunk)) {
        push({ type: "image", text: chunk });
        continue;
      }
    }

    const lines = chunk.split("\n").map(l => l.trim()).filter(Boolean);

    if (lines.length && lines.every(l => l.startsWith("- "))) {
      push({ type: "list", text: lines.join("\n") });
      continue;
    }
    if (lines.length && lines.every(l => l.startsWith(">"))) {
      const quoted = lines.map(l => l.replace(/^>\s?/, "")).join(" ");
      push({ type: "quote", text: quoted });
      continue;
    }
    push({ type: "p", text: lines.join(" ") });
  }
  return blocks;
}

/* ---------- Alinhamento N-ário ---------- */

function zipBlocks(langs) {
  const rank = { h1: 0, h2: 1, h3: 2, h4: 3, h5: 4, h6: 5, image: 6, list: 7, quote: 7, p: 8, text: 8 };
  const n = Math.max(...langs.map(l => l.blocks.length));
  const out = [];
  for (let i = 0; i < n; i++) {
    const cells = {};
    const cellTypes = {};
    const types = [];
    for (const l of langs) {
      const b = l.blocks[i] || null;
      cells[l.code] = (b || {}).text || "";
      if (b) cellTypes[l.code] = b.type;
      if (b) types.push(b.type);
    }
    const btype = types.length
      ? types.reduce((a, b) => (rank[a] < rank[b] ? a : b))
      : "p";
    out.push({ type: btype, cells, cellTypes });
  }
  return out;
}

/* ---------- UI helpers ---------- */

function el(tag, attrs = {}, children = []) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k === "html") n.innerHTML = v;
    else if (k === "text") n.textContent = v;
    else if (v != null) n.setAttribute(k, v);
  }
  for (const c of [].concat(children)) {
    if (c == null) continue;
    n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  }
  return n;
}

function escapeHTML(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

let markdownRenderer = null;

function joinLiteralTextTokens(state) {
  for (const block of state.tokens) {
    if (!block.children) continue;
    const joined = [];
    for (const token of block.children) {
      if (token.type === "text_special") token.type = "text";
      const previous = joined[joined.length - 1];
      if (token.type === "text" && previous?.type === "text") previous.content += token.content;
      else joined.push(token);
    }
    block.children = joined;
  }
}

function markdown() {
  if (markdownRenderer) return markdownRenderer;
  markdownRenderer = markdownit({ html: false, linkify: true, typographer: false })
    .use(markdownitFootnote);
  // Resolve os escapes antes de reconhecer URLs: qr\_2.pdf deve apontar para qr_2.pdf.
  markdownRenderer.inline.ruler.disable("linkify");
  markdownRenderer.core.ruler.before("linkify", "join_literal_text", joinLiteralTextTokens);
  const imageRule = markdownRenderer.renderer.rules.image;
  markdownRenderer.renderer.rules.image = (tokens, index, options, env, renderer) => {
    const token = tokens[index];
    token.attrSet("src", absURL(token.attrGet("src")));
    token.attrSet("loading", "lazy");
    return imageRule(tokens, index, options, env, renderer);
  };
  markdownRenderer.renderer.rules.heading_open = (tokens, index, options, env, renderer) => {
    const text = tokens[index + 1].content;
    const slug = text.toLowerCase().normalize("NFC")
      .replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-|-$/g, "") || "secao";
    const counts = env.headingCounts || (env.headingCounts = new Map());
    let count = (counts.get(slug) || 0) + 1;
    const ids = env.headingIds || (env.headingIds = new Set());
    let id;
    do {
      id = `${env.docId || "markdown"}-${slug}${count > 1 ? "-" + count : ""}`;
      if (!ids.has(id)) break;
      count++;
    } while (true);
    counts.set(slug, count);
    ids.add(id);
    tokens[index].attrSet("id", id);
    return renderer.renderToken(tokens, index, options);
  };
  return markdownRenderer;
}

function safeMarkdown(source, env = {}, inlineOnly = false) {
  const html = inlineOnly ? markdown().renderInline(source, env) : markdown().render(source, env);
  return DOMPurify.sanitize(html, {
    USE_PROFILES: { html: true },
    FORBID_TAGS: ["style", "form", "input", "button"],
    FORBID_ATTR: ["style"],
  });
}

function inline(text) {
  return safeMarkdown(text, {}, true);
}

function baseLanguageCode(langs) {
  if (langs.some(l => l.code === "pt")) return "pt";
  if (langs.some(l => l.code === "en")) return "en";
  return langs[0].code;
}

/* ---------- Modo de visualização ---------- */

function refreshDocument(preservePosition=true) {
  if (!state.activeDocument) return;
  const { meta, langs, blocks, collection, subcollection } = state.activeDocument;
  const scrollY=window.scrollY;
  const viewportTop=readingViewportTop();
  const previous=state.readingTracker?.entries||[];
  const visible=previous.find(entry=>{
    const rect=entry.node.getBoundingClientRect();
    return rect.height>0&&rect.bottom>viewportTop&&rect.top<window.innerHeight;
  });
  const rect=visible?.node.getBoundingClientRect();
  const peers=visible?previous.filter(entry=>entry.language===visible.language):[];
  const position=visible?{
    language:visible.language,blockIndex:visible.blockIndex,
    signature:readingFingerprint(visible.node.textContent),
    fraction:Math.max(0,(viewportTop-rect.top)/rect.height),
    top:Math.max(rect.top,viewportTop),ratio:peers.indexOf(visible)/Math.max(1,peers.length-1)
  }:null;
  renderDocumentBody(meta,langs,blocks);
  document.querySelector(".doc-toolbar")?.updateViewing?.();
  if(!preservePosition){state.readingRenderVersion=(state.readingRenderVersion||0)+1;return;}
  const rendered=state.activeDocument;
  const renderVersion=(state.readingRenderVersion||0)+1;
  state.readingRenderVersion=renderVersion;
  const restore=()=>{
    if(state.activeDocument!==rendered||state.readingRenderVersion!==renderVersion)return;
    const entries=(state.readingTracker?.entries||[]).filter(entry=>{
      const bounds=entry.node.getBoundingClientRect();return bounds.height>0&&bounds.width>0;
    });
    const matching=position&&entries.find(entry=>entry.language===position.language&&readingFingerprint(entry.node.textContent)===position.signature);
    const sameLanguage=position&&entries.filter(entry=>entry.language===position.language);
    const candidates=sameLanguage?.length?sameLanguage:entries;
    const target=matching||(position&&candidates[Math.round(position.ratio*Math.max(0,candidates.length-1))]);
    const bounds=target?.node.getBoundingClientRect();
    const top=bounds?window.scrollY+bounds.top+bounds.height*position.fraction-position.top:scrollY;
    window.scrollTo({top:Math.max(0,top),behavior:"instant"});
  };
  restore();
  requestAnimationFrame(restore);
}

function setViewMode(mode) {
  if (!["reading", "study"].includes(mode) || state.viewMode === mode) return;
  state.viewMode = mode;
  try { localStorage.setItem("documentViewMode", mode); } catch (e) {}
  refreshDocument();
}

function setStudyMode(mode) {
  if (!["paragraph", "parallel"].includes(mode) || state.studyMode === mode) return;
  state.studyMode = mode;
  try { localStorage.setItem("studyMode", mode); } catch (e) {}
  refreshDocument();
}

function readingLanguage(meta, langs) {
  let code = state.readingLanguages.get(meta.id);
  if (!code) {
    try { code = localStorage.getItem("readingLanguage:" + meta.id); } catch (e) {}
  }
  return langs.some(l => l.code === code) ? code : baseLanguageCode(langs);
}

function setReadingLanguage(meta, langs, code) {
  if (!langs.some(l => l.code === code)) return;
  state.readingLanguages.set(meta.id, code);
  try { localStorage.setItem("readingLanguage:" + meta.id, code); } catch (e) {}
  refreshDocument();
  const exportSelect = document.querySelector(".export-language");
  if (exportSelect) {exportSelect.value = code;exportSelect.updateOptions?.();}
}

/* ---------- Colunas paralelas ---------- */

function initParallelCols(docId, langs) {
  const key = "parallelCols:" + docId;
  const available = langs.map(l => l.code);
  let stored = null;
  try { stored = localStorage.getItem(key); } catch (e) {}
  if (stored) {
    const parts = stored.split(",");
    if (parts.length === 2 && available.includes(parts[0]) &&
        available.includes(parts[1]) && parts[0] !== parts[1]) {
      state.parallelCols = { left: parts[0], right: parts[1] };
      return;
    }
  }
  const baseCode = baseLanguageCode(langs);
  const firstOther = available.find(c => c !== baseCode);
  state.parallelCols = { left: baseCode, right: firstOther };
}

function applyParallelLayout() {
  const article = document.querySelector("article.doc");
  if (!article) return;
  const n = parseInt(article.dataset.langCount, 10) || 0;
  if (n <= 2) return;

  const order = {};
  order[state.parallelCols.left] = 1;
  order[state.parallelCols.right] = 2;

  article.querySelectorAll(".block .cell").forEach(cell => {
    const lang = [...cell.classList].find(c => c.startsWith("lang-"))?.slice(5);
    if (!lang) return;
    const show = (lang === state.parallelCols.left) ||
                 (lang === state.parallelCols.right);
    cell.classList.toggle("hidden", !show);
    cell.style.order = show ? order[lang] : "";
  });

  const labels = article.querySelector(".col-labels");
  if (labels) {
    labels.querySelectorAll(":scope > div").forEach(div => {
      const lang = [...div.classList].find(c => c.startsWith("label-"))?.slice(6);
      if (!lang) return;
      const show = (lang === state.parallelCols.left) ||
                   (lang === state.parallelCols.right);
      div.classList.toggle("hidden", !show);
      div.style.order = show ? order[lang] : "";
    });
  }
}

function setParallelCols(side, value) {
  const article = document.querySelector("article.doc");
  if (!article) return;
  const docId = article.dataset.docId;

  if (side === "left") {
    if (value === state.parallelCols.right) {
      state.parallelCols.right = state.parallelCols.left;
    }
    state.parallelCols.left = value;
  } else {
    if (value === state.parallelCols.left) {
      state.parallelCols.left = state.parallelCols.right;
    }
    state.parallelCols.right = value;
  }
  try {
    localStorage.setItem(
      "parallelCols:" + docId,
      state.parallelCols.left + "," + state.parallelCols.right
    );
  } catch (e) {}
  applyParallelLayout();
  updateParallelSelects();
  document.querySelector(".doc-toolbar")?.updateViewing?.();
  const active = state.activeDocument;
  if (active) setupStudyNavigation(active.meta, active.langs);
}

function updateParallelSelects() {
  document.querySelectorAll(".lang-select").forEach(sel => {
    sel.value = state.parallelCols[sel.dataset.side];
    sel.updateOptions?.();
  });
}

/* ---------- Navegação no topo ---------- */

function renderNav() {
  const nav = document.getElementById("docNav");
  nav.innerHTML = "";
  nav.appendChild(el("a", { class: "nav-link", href: "#/", text: "Todas as coleções" }));
  const select = el("select", {
    class: "collection-select", "aria-label": "Abrir coleção",
  });
  select.appendChild(el("option", { value: "", text: "Selecionar coleção…", disabled: "disabled" }));
  for (const c of state.manifest.collections) {
    select.appendChild(el("option", { value: c.id, text: c.title_pt }));
  }
  select.addEventListener("change", () => {
    if (select.value) location.hash = `#/colecao/${select.value}`;
  });
  nav.appendChild(select);
  nav.appendChild(el("a", { class: "nav-link search-nav-link", href: "#/busca", text: "Buscar" }));
}

function setActiveNav(collectionId) {
  state.activeCollection = collectionId || null;
  const select = document.querySelector("#docNav .collection-select");
  if (select) select.value = collectionId || "";
  const home = document.querySelector("#docNav .nav-link");
  if (home) {
    if (parseRoute().view === "home") home.setAttribute("aria-current", "page");
    else home.removeAttribute("aria-current");
  }
  const search = document.querySelector(".search-nav-link");
  if (search) {
    if (parseRoute().view === "search") search.setAttribute("aria-current", "page");
    else search.removeAttribute("aria-current");
  }
}

/* ---------- Renderização: documento ---------- */

function renderCellContent(block, code) {
  block = { ...block, type: block.cellTypes?.[code] || block.type };
  const frag = document.createDocumentFragment();
  const raw = (block.cells[code] || "").trim();
  if (!raw) { frag.appendChild(el("p", { text: "—" })); return frag; }

  if (block.type === "text") {
    frag.appendChild(el("p", { text: raw }));
    return frag;
  }

  if (block.type === "image") {
    const m = raw.match(/^!\[(.*?)\]\((.+?)\)$/);
    if (m && markdown().validateLink(m[2].trim())) {
      const fig = el("figure", { class: "md-figure" });
      fig.appendChild(el("img", {
        src: absURL(m[2].trim()), alt: m[1].trim(), loading: "lazy",
      }));
      if (m[1].trim()) fig.appendChild(el("figcaption", { text: m[1].trim() }));
      frag.appendChild(fig);
      return frag;
    }
  }

  if (block.type === "list") {
    const ul = el("ul");
    for (const line of raw.split("\n")) {
      const t = line.replace(/^-\s+/, "").trim();
      if (!t) continue;
      const li = el("li");
      li.innerHTML = inline(t);
      ul.appendChild(li);
    }
    frag.appendChild(ul);
    return frag;
  }

  if (block.type === "quote") {
    const bq = el("blockquote");
    bq.innerHTML = inline(raw);
    frag.appendChild(bq);
    return frag;
  }

  let tag = "p";
  if (/^h[1-6]$/.test(block.type)) tag = "h" + Math.min(Number(block.type.slice(1)) + 1, 6);

  const p = el(tag);
  p.innerHTML = inline(raw);
  frag.appendChild(p);
  return frag;
}

function renderBlock(b, allLangs) {
  const isHeading = /^h[1-6]$/.test(b.type);
  const isImage = b.type === "image";
  const wrap = el("div", { class: "block" + (isHeading ? " is-heading" : "") });
  const baseCode = baseLanguageCode(allLangs);

  // Botões de tradução (só em Estudo → Por parágrafo, só se houver >1 idioma, exceto imagens)
  if (allLangs.length > 1 && !isImage) {
    const group = el("div", { class: "block-toggles" });
    for (const l of allLangs) {
      if (l.code === baseCode) continue;
      const btn = el("button", {
        type: "button",
        class: "block-toggle",
        "data-lang": l.code,
        "aria-expanded": "false",
        title: `Mostrar tradução em ${l.code.toUpperCase()}`,
      });
      btn.textContent = l.code.toUpperCase();
      btn.addEventListener("click", () => {
        const cell = wrap.querySelector(".cell.lang-" + l.code);
        if (!cell) return;
        const visible = cell.classList.toggle("visible");
        btn.classList.toggle("active", visible);
        btn.setAttribute("aria-expanded", String(visible));
      });
      group.appendChild(btn);
    }
    wrap.appendChild(group);
  }

  for (const l of allLangs) {
    const isBase = l.code === baseCode;
    const cell = el("div", {
      class: "cell lang-" + l.code + (isBase ? " base" : " secondary"),
      lang: l.code,
    });
    cell.setAttribute("data-lang-label", l.code.toUpperCase());
    cell.appendChild(renderCellContent(b, l.code));
    wrap.appendChild(cell);
  }
  return wrap;
}

function collectionDocuments(collection) {
  return collection.documents || collection.document_ids.map(id => state.documentIndex.get(id));
}

const COLLECTION_PAGE_SIZE = 25;

function collectionDocumentURL(doc, subcollection, collection, page = null) {
  const params = new URLSearchParams();
  params.set("colecao", collection.id);
  if (subcollection) params.set("subcolecao", subcollection.id);
  if(page)params.set("pagina",String(page));
  return `#/doc/${doc.id}?${params}`;
}

function collectionListURL(collection,subcollection,page=1) {
  const path=`#/colecao/${collection.id}`+(subcollection?`/subcolecao/${subcollection.id}`:collection.subcollections?.length?"/todos":"");
  return path+(page>1?`?pagina=${page}`:"");
}

function documentDateBadge(doc) {
  const date=documentDateInfo(doc);
  if(!date)return null;
  return el(date.iso?"time":"span",{class:"doc-date"+(date.source?" is-source-date":""),datetime:date.iso,
    title:date.label,"aria-label":`${date.label}: ${date.text}`,text:date.text});
}

function renderCollectionPagination(total,page,collection,subcollection) {
  const pages=Math.max(1,Math.ceil(total/COLLECTION_PAGE_SIZE));
  const nav=el("nav",{class:"catalog-pagination","aria-label":"Páginas dos documentos"});
  if(pages===1)return nav;
  const add=(label,target)=>el("a",{href:collectionListURL(collection,subcollection,target),text:label});
  nav.append(page>1?add("← Anterior",page-1):el("span",{class:"pagination-disabled","aria-disabled":"true",text:"← Anterior"}));
  let previous=0;
  for(const value of [...new Set([1,page-1,page,page+1,pages])].filter(n=>n>=1&&n<=pages).sort((a,b)=>a-b)) {
    if(previous&&value-previous>1)nav.append(el("span",{class:"pagination-gap",text:"…"}));
    nav.append(value===page?el("span",{class:"pagination-current","aria-current":"page",text:String(value)}):add(String(value),value));
    previous=value;
  }
  nav.append(page<pages?add("Próxima →",page+1):el("span",{class:"pagination-disabled","aria-disabled":"true",text:"Próxima →"}));
  return nav;
}

function renderDocumentSequence(meta,collection,subcollection) {
  const nav=el("nav",{class:"document-sequence","aria-label":"Navegação no fim do documento"});
  if(!collection)return nav;
  const all=collectionDocuments(collection);const map=new Map(all.map(doc=>[doc.id,doc]));
  const documents=subcollection?subcollection.document_ids.map(id=>map.get(id)).filter(Boolean):all;
  const index=documents.findIndex(doc=>doc.id===meta.id);
  if(index<0)return nav;
  const language=state.activeDocument?readingLanguage(meta,state.activeDocument.langs):null;
  const query=new URLSearchParams(location.hash.split("?")[1]||"");
  function adjacent(delta) {
    const doc=documents[index+delta];const caption=delta<0?"← Anterior":"Próximo →";
    if(!doc)return el("span",{class:"sequence-link is-disabled","aria-disabled":"true",text:caption});
    const [path,raw=""]=collectionDocumentURL(doc,subcollection,collection,Math.floor((index+delta)/COLLECTION_PAGE_SIZE)+1).split("?");
    const params=new URLSearchParams(raw);
    if(language&&doc.languages.some(l=>l.code===language))params.set("idioma",language);
    if(query.get("busca")?.startsWith("#/busca"))params.set("busca",query.get("busca"));
    const date=documentDateInfo(doc);
    const anchor=el("a",{class:"sequence-link",href:path+"?"+params,title:(documentTitle(doc))+(date?" · "+date.text:"")},[
      el("span",{class:"sequence-direction",text:caption}),el("strong",{class:"sequence-title",text:documentTitle(doc)}),documentDateBadge(doc)]);
    anchor.addEventListener("click",()=>{
      const current=state.activeDocument;
      const selected=current?.meta.id===meta.id?readingLanguage(meta,current.langs):language;
      if(selected&&doc.languages.some(l=>l.code===selected))params.set("idioma",selected);else params.delete("idioma");
      anchor.href=path+"?"+params;
    });
    return anchor;
  }
  const list=collectionListURL(collection,subcollection,Math.floor(index/COLLECTION_PAGE_SIZE)+1);
  nav.append(adjacent(-1),el("div",{class:"sequence-context"},[
    el("span",{text:`${index+1} de ${documents.length} · ${subcollection?"Subcoleção":"Coleção"}`}),
    el("a",{href:list,text:subcollection?.title_pt||collection.title_pt}),
  ]),adjacent(1));
  return nav;
}

function renderBreadcrumbs(collection, subcollection, current) {
  const nav = el("nav", { class: "breadcrumbs", "aria-label": "Caminho de navegação" });
  nav.appendChild(el("a", { href: "#/", text: "Acervo" }));
  if (collection) {
    nav.appendChild(el("span", { text: " / ", "aria-hidden": "true" }));
    nav.appendChild(el("a", { href: `#/colecao/${collection.id}`, text: collection.title_pt }));
  }
  if (subcollection) {
    const page=Number(new URLSearchParams(location.hash.split("?")[1]||"").get("pagina"));
    nav.appendChild(el("span", { text: " / ", "aria-hidden": "true" }));
    nav.appendChild(el("a", {
      href: `#/colecao/${collection.id}/subcolecao/${subcollection.id}`+(Number.isSafeInteger(page)&&page>1?`?pagina=${page}`:""),
      text: subcollection.title_pt,
    }));
  }
  nav.appendChild(el("span", { text: " / ", "aria-hidden": "true" }));
  nav.appendChild(el("span", { text: current, "aria-current": "page" }));
  return nav;
}

function renderDocHeader(meta, collection, subcollection) {
  const header = el("header", { class: "doc-header" });
  header.appendChild(renderBreadcrumbs(collection, subcollection, "Documento"));
  header.appendChild(el("p", { class: "doc-eyebrow", text: meta.eyebrow || (meta.type==="article"?"Artigo":"Documento") }));
  header.appendChild(el("h1", {}, [
    documentTitle(meta),
    meta.title_pt && meta.title_ru ? el("span", { class: "ru-title", lang: "ru", text: meta.title_ru }) : null,
  ]));
  if (!meta.title_pt) header.querySelector("h1").lang = meta.title_ru?"ru":"en";
  if (meta.source_url) {
    const source = el("p", { class: "source-info" }, [
      el("a", { href: meta.source_url, text: `Fonte: ${meta.source_name || "publicação de origem"}` }),
      meta.source_id ? ` · ID ${meta.source_id}` : "",
    ]);
    header.appendChild(source);
  }
  if (meta.author) {
    header.appendChild(el("p", { class: "doc-author", text: meta.author }));
  }
  const m = el("div", { class: "doc-meta" });
  const date=documentDateInfo(meta);
  if(date)m.appendChild(el("span",{text:`Data: ${date.text}`}));
  [meta.archive].filter(Boolean)
    .forEach(t => m.appendChild(el("span", { text: t })));
  if (m.children.length) header.appendChild(m);
  return header;
}

function escapeMarkdownText(text) {
  return text.replace(/([\\`*_[\]<>#])/g, "\\$1");
}

function documentMarkdown(meta, language) {
  // As edições Markdown são exportadas diretamente, sem reconstruir os parágrafos.
  const format = language.format || meta.format;
  if (format !== "text" && meta.source_name !== "ShowTrials") return language.source;
  const title = meta[`title_${language.code}`] || documentTitle(meta);
  const body = format === "text" ? language.source : splitExportHeaders(language.source).body;
  const lines = [`# ${escapeMarkdownText(title)}`, ""];
  if (meta.source_url) lines.push(`Fonte: ${meta.source_url}`);
  if (meta.source_name==="ShowTrials"&&meta.source_id) lines.push(`ID ShowTrials: ${meta.source_id}`);
  else lines.push(`ID do documento: ${meta.id}`);
  const date=meta.date||meta.collected_date;
  if(date) lines.push(`Data do documento: ${String(date).split("T")[0]}`);
  lines.push(`Idioma: ${language.code.toUpperCase()}`, "", "---", "");
  lines.push(format === "text" ? escapeMarkdownText(body) : body);
  return lines.join("\n");
}

function markdownFilename(meta, language) {
  const file = meta.languages.find(l => l.code === language.code)?.file;
  const name = file?.split("/").pop();
  return name ? name.replace(/\.(?:md|txt)$/i, "") + ".md" : `${meta.id}.${language.code}.md`;
}

function downloadMarkdown(meta, language) {
  const blob = new Blob([documentMarkdown(meta, language)], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = el("a", { href: url, download: markdownFilename(meta, language) });
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function languageSelect(langs, className, label, code) {
  const select = el("select", { class: className, "aria-label": label });
  const names = { pt: "Português", ru: "Russo", en: "Inglês" };
  for (const l of langs) {
    select.appendChild(el("option", { value: l.code, text: names[l.code] || l.label }));
  }
  select.value = code;
  return select;
}

function documentActionLanguage(meta,langs) {
  return state.viewMode==="study"&&state.studyMode==="parallel"&&langs.some(lang=>lang.code===state.parallelCols.left)
    ?state.parallelCols.left:readingLanguage(meta,langs);
}

function languageField(langs,className,label,code) {
  const select=languageSelect(langs,className,label,code);
  select.hidden=true;
  const list=el("div",{class:"panel-option-list",role:"group","aria-label":label});
  const buttons=[];
  for(const option of select.options){
    const button=el("button",{type:"button",class:"panel-option",text:option.textContent});
    button.addEventListener("click",()=>{select.value=option.value;select.dispatchEvent(new Event("change",{bubbles:true}));});
    buttons.push([button,option.value]);list.append(button);
  }
  select.updateOptions=()=>buttons.forEach(([button,value])=>{button.classList.toggle("active",select.value===value);button.setAttribute("aria-pressed",String(select.value===value));});
  select.addEventListener("change",select.updateOptions);select.updateOptions();
  return {select,element:el("div",{class:"language-options"},[select,list])};
}

function renderToolbar(langs, meta) {
  const bar = el("section", { class: "doc-toolbar", "aria-label":"Painel do documento" });
  const controls=el("div",{class:"reader-panel-controls",id:"reader-panel-controls"});
  const actions=el("div",{class:"reader-panel-actions"});
  const heading=el("div",{class:"reader-panel-heading"},[
    el("span",{class:"reader-panel-title",text:"Painel do documento"}),
    el("span",{class:"reader-panel-status",text:state.viewMode==="study"&&langs.length>1?"Estudo":"Leitura"})
  ]);
  const quickResume=el("button",{type:"button",class:"panel-button panel-quick-resume",text:"● Retomar",hidden:"hidden",title:"Retomar o parágrafo marcado"});
  quickResume.addEventListener("click",()=>{const record=savedReadingProgress(meta,langs);if(record)resumeReading(meta,langs,record);});
  const head=el("div",{class:"reader-panel-head"},[heading,actions]);
  let expanded=false;
  const expand=el("button",{type:"button",class:"panel-button panel-expand","aria-controls":"reader-panel-controls"});
  const applyExpanded=()=>{
    controls.hidden=!expanded;
    expand.textContent=expanded?"Recolher ▴":"Expandir ▾";
    expand.setAttribute("aria-expanded",String(expanded));
    bar.classList.toggle("is-collapsed",!expanded);
    if(!expanded)for(const item of controls.querySelectorAll("details[open]"))item.open=false;
    updateReadingLayout();
  };
  expand.addEventListener("click",()=>{expanded=!expanded;applyExpanded();});
  const section=(title,className)=>{
    const body=el("div",{class:"control-section-body"});
    const group=el("section",{class:"control-section "+className},[
      el("div",{class:"control-section-heading"},[el("h2",{text:title})]),body
    ]);
    controls.append(group);
    return body;
  };
  const navigation=section("Navegar no texto","control-navigation");
  navigation.append(el("div",{class:"reading-tools",role:"group","aria-label":"Índice e marcador do documento",hidden:"hidden"}));
  const viewing=section("Visualização e idiomas","control-viewing");
  const documentActions=section("Trabalhar com o documento","control-document-actions");
  bar.append(head,controls);
  // Os menus compartilham a mesma estrutura, incluindo a edição carregada localmente.
  bar.addEventListener("toggle",event=>{
    if(event.target.tagName==="DETAILS"&&event.target.open)
      for(const other of controls.querySelectorAll("details[open]"))if(other!==event.target)other.open=false;
    updateReadingLayout();
  },true);
  const menu = (title, content) => {
    const details=el("details",{class:"editorial-menu reader-options"});
    details.append(el("summary",{text:title}),el("div",{class:"editorial-menu-body"},[content]));
    return details;
  };
  const pin=el("button",{type:"button",class:"toolbar-pin panel-button","aria-pressed":"false",title:"Fixar barra durante a rolagem",text:"Fixar"});
  let pinned=sessionRead("readerToolbarPinned")==="true";
  const applyPin=()=>{bar.classList.toggle("is-pinned",pinned);pin.setAttribute("aria-pressed",String(pinned));pin.textContent=pinned?"Soltar":"Fixar";pin.title=pinned?"Deixar barra no início do texto":"Fixar barra durante a rolagem";updateReadingLayout();};
  pin.addEventListener("click",()=>{pinned=!pinned;sessionWrite("readerToolbarPinned",String(pinned));applyPin();});
  const hasTranslations = langs.length > 1;
  const isStudy = hasTranslations && state.viewMode === "study";

  if (hasTranslations) {
    const modes = el("div", { class: "toolbar-group", role: "group", "aria-label": "Modo de visualização" });
    [["reading", "Leitura"], ["study", "Estudo"]].forEach(([code, label]) => {
      const active = state.viewMode === code;
      const button = el("button", {
        type: "button", class: "mode-btn" + (active ? " active" : ""),
        "data-mode": code, "aria-pressed": String(active), text: label,
      });
      button.addEventListener("click", () => setViewMode(code));
      modes.appendChild(button);
    });
    const modeMenu=menu("Modo · "+(isStudy?"Estudo":"Leitura"),modes);
    modeMenu.dataset.control="mode";viewing.appendChild(modeMenu);

    {
      const submodes = el("div", { class: "toolbar-group study-controls", role: "group", "aria-label": "Visualização de estudo" });
      [["paragraph", "Por parágrafo"], ["parallel", "Paralelo"]].forEach(([code, label]) => {
        const active = state.studyMode === code;
        const button = el("button", {
          type: "button", class: "study-btn" + (active ? " active" : ""),
          "data-study-mode": code, "aria-pressed": String(active), text: label,
        });
        button.addEventListener("click", () => setStudyMode(code));
        submodes.appendChild(button);
      });
      const studyMenu=menu("Estudo · "+(state.studyMode==="parallel"?"Paralelo":"Por parágrafo"),submodes);
      studyMenu.dataset.control="study";viewing.appendChild(studyMenu);
    }
    {
      const languageGroup = el("div", { class: "toolbar-group" });
      languageGroup.appendChild(el("span", { class: "toolbar-label", text: "Idioma:" }));
      const field = languageField(langs, "reading-language", "Idioma de leitura", readingLanguage(meta, langs));
      const select=field.select;
      select.addEventListener("change", () => setReadingLanguage(meta, langs, select.value));
      languageGroup.appendChild(field.element);
      const readingMenu=menu("Idioma de leitura",languageGroup);readingMenu.dataset.control="reading";viewing.appendChild(readingMenu);
    }
  } else {
    viewing.appendChild(el("p",{class:"control-help",text:"Uma versão disponível: "+(langs[0].label||langs[0].code.toUpperCase())+"."}));
  }

  if (langs.length > 2) {
    const colGroup = el("div", { class: "toolbar-group parallel-only" });
    colGroup.appendChild(el("span", { class: "toolbar-label", text: "Colunas:" }));
    ["left", "right"].forEach(side => {
      const field=languageField(langs,"lang-select",side === "left" ? "Idioma à esquerda" : "Idioma à direita",state.parallelCols[side]);
      const select=field.select;
      select.dataset.side = side;
      select.addEventListener("change", () => setParallelCols(side, select.value));
      colGroup.appendChild(el("span",{class:"toolbar-label",text:side==="left"?"Coluna esquerda":"Coluna direita"}));
      colGroup.appendChild(field.element);
    });
    const columns=menu("Idiomas das colunas",colGroup);columns.dataset.control="columns";viewing.appendChild(columns);
  }

  const exportGroup = el("div", { class: "toolbar-group export-group" });
  if (hasTranslations) {
    exportGroup.appendChild(languageField(langs, "export-language", "Idioma para exportação", documentActionLanguage(meta, langs)).element);
  }
  const button = el("button", { type: "button", class: "export-btn", text: "Exportar Markdown" });
  button.addEventListener("click", () => {
    const code = exportGroup.querySelector(".export-language")?.value || langs[0].code;
    downloadMarkdown(meta, langs.find(l => l.code === code));
  });
  exportGroup.appendChild(button);
  documentActions.appendChild(menu("Exportar Markdown",exportGroup));
  documentActions.appendChild(editorialReaderTools(meta,langs));
  actions.append(quickResume,pin,expand);
  bar.updateViewing=()=>{
    const study=langs.length>1&&state.viewMode==="study";
    bar.querySelector(".reader-panel-status").textContent=study?"Estudo":"Leitura";
    for(const select of bar.querySelectorAll(".reading-language,.export-language,.editorial-language")){
      if(select.classList.contains("reading-language"))select.value=readingLanguage(meta,langs);
      else if(select.classList.contains("export-language")||select.classList.contains("editorial-language")){
        select.value=documentActionLanguage(meta,langs);
      }
      select.updateOptions?.();
    }
    updateParallelSelects();
    for(const button of bar.querySelectorAll("[data-mode], [data-study-mode]")){
      const active=button.dataset.mode?button.dataset.mode===state.viewMode:button.dataset.studyMode===state.studyMode;
      button.classList.toggle("active",active);button.setAttribute("aria-pressed",String(active));
    }
    for(const item of bar.querySelectorAll("[data-control]")){
      const kind=item.dataset.control;
      item.hidden=kind==="study"?!study:kind==="reading"?study:kind==="columns"?!(study&&state.studyMode==="parallel"):false;
      if(item.hidden)item.open=false;
      if(kind==="mode")item.querySelector("summary").textContent="Modo · "+(study?"Estudo":"Leitura");
      if(kind==="study")item.querySelector("summary").textContent="Estudo · "+(state.studyMode==="parallel"?"Paralelo":"Por parágrafo");
    }
  };
  bar.updateViewing();applyExpanded();applyPin();
  if(typeof ResizeObserver!=="undefined"){
    bar.layoutObserver=new ResizeObserver(updateReadingLayout);
    bar.layoutObserver.observe(bar);
  }
  return bar;
}

/* ---------- Índice e posição de leitura: somente nesta sessão da aba ---------- */

function sessionRead(key) {
  try { return sessionStorage.getItem(key); } catch (e) { return null; }
}

function sessionWrite(key, value) {
  try { sessionStorage.setItem(key, value); return true; } catch (e) { return false; }
}

function readingFingerprint(text) {
  let hash = 2166136261;
  const normalized = text.trim().replace(/\s+/g, " ");
  for (let i = 0; i < normalized.length; i++) {
    hash = Math.imul(hash ^ normalized.charCodeAt(i), 16777619);
  }
  return (hash >>> 0).toString(36);
}

function savedReadingProgress(meta, langs) {
  let record;
  try { record = JSON.parse(sessionRead("readingProgress:v1:" + meta.id)); } catch (e) { return null; }
  if (!record || record.version !== 1 || !langs.some(l => l.code === record.language) ||
      !Number.isInteger(record.blockIndex) || record.blockIndex < 0 ||
      typeof record.signature !== "string" || !Number.isFinite(record.offset) ||
      record.offset < 0 || record.offset > 1) return null;
  return record;
}

function resolveReadingBlock(record, blocks) {
  const atIndex = blocks[record.blockIndex];
  if (atIndex && readingFingerprint(atIndex.textContent) === record.signature) return atIndex;
  return blocks.find(block => readingFingerprint(block.textContent) === record.signature) || null;
}

function readingLayoutMetrics() {
  return {
    header:document.querySelector(".site-header")?.getBoundingClientRect().height||0,
    panel:document.querySelector(".doc-toolbar.is-pinned")?.getBoundingClientRect().height||0
  };
}

function updateReadingLayout() {
  const metrics=readingLayoutMetrics();
  const style=document.documentElement.style;
  for(const [name,value] of [["--site-header-height",metrics.header],["--reader-panel-height",metrics.panel]]){
    const size=`${value}px`;
    if(style.getPropertyValue(name)!==size)style.setProperty(name,size);
  }
}

function stopPanelLayoutTracking() {
  document.querySelector(".doc-toolbar")?.layoutObserver?.disconnect();
  document.documentElement.style.setProperty("--reader-panel-height","0px");
}

function readingViewportTop() {
  const metrics=readingLayoutMetrics();
  return metrics.header+metrics.panel+24;
}

function closeDocumentPanel() {
  const panel = document.querySelector(".reading-panel");
  if (!panel || !panel.open) return;
  panel.open = false;
  if (state.activeDocument) sessionWrite("readingPanel:v1:" + state.activeDocument.meta.id, "false");
}

function jumpToReadingBlock(target, offset = 0) {
  closeDocumentPanel();
  updateReadingLayout();
  const rect = target.getBoundingClientRect();
  window.scrollTo({ top: Math.max(0, window.scrollY + rect.top + rect.height * offset - readingViewportTop()), behavior: "auto" });
  target.setAttribute("tabindex", "-1");
  target.focus({ preventScroll: true });
}

function buildReadingIndex(headings) {
  const list = el("ol", { class: "reading-toc-list" });
  const minLevel = Math.min(...headings.map(h => h.level));
  const stack = [{ level: minLevel, list, item: null }];
  for (const heading of headings) {
    const level = heading.level;
    while (stack.length > 1 && level < stack[stack.length - 1].level) stack.pop();
    let frame = stack[stack.length - 1];
    if (level > frame.level && frame.item) {
      const nested = el("ol");
      frame.item.appendChild(nested);
      frame = { level, list: nested, item: null };
      stack.push(frame);
    }
    const link = el("a", { href: "#" + heading.node.id, class: "reading-toc-link", text: heading.node.textContent });
    link.dataset.target = heading.node.id;
    link.addEventListener("click", event => {
      event.preventDefault();
      jumpToReadingBlock(heading.node);
    });
    frame.item = el("li", {}, [link]);
    frame.list.appendChild(frame.item);
  }
  return list;
}

function resolveMarkedEntry(record, entries) {
  const sameLanguage = entries.filter(entry => entry.language === record.language);
  const block = resolveReadingBlock(record, sameLanguage.map(entry => entry.node));
  return sameLanguage.find(entry => entry.node === block) || null;
}

function paintReadingMarker(record) {
  const tracker = state.readingTracker;
  if (!tracker) return;
  for (const entry of tracker.entries) {
    (entry.row || entry.node).classList.remove("reading-marked");
    entry.node.removeAttribute("aria-current");
  }
  const entry = record && resolveMarkedEntry(record, tracker.entries);
  if (entry) {
    (entry.row || entry.node).classList.add("reading-marked");
    entry.node.setAttribute("aria-current", "location");
  }
}

function updateMarkerControls(meta, langs, message) {
  const record = savedReadingProgress(meta, langs);
  const status = document.querySelector(".reading-session-status");
  if (status) status.textContent = message || (record
    ? "Parágrafo marcado nesta sessão. Clique novamente nele para remover a marca."
    : "Clique ou toque em um parágrafo para marcá-lo. Também funciona com Enter ou Espaço.");
  const resume = document.querySelector(".resume-btn");
  if (resume) resume.hidden = !record;
  const quickResume=document.querySelector(".panel-quick-resume");
  if(quickResume)quickResume.hidden=!record;
  const indicator = document.querySelector(".panel-marker");
  if (indicator) indicator.hidden = !record;
  paintReadingMarker(record);
  updateReadingLayout();
}

function markReadingEntry(entry) {
  const tracker = state.readingTracker;
  if (!tracker) return;
  const previous = savedReadingProgress(tracker.meta, tracker.langs);
  const record = {
    version: 1, language: entry.language, blockIndex: entry.blockIndex,
    signature: readingFingerprint(entry.node.textContent), offset: 0,
    mode: tracker.mode, studyMode: state.studyMode, parallelCols: { ...state.parallelCols },
  };
  const same = previous && resolveMarkedEntry(previous, tracker.entries)?.node === entry.node;
  let saved;
  if (same) {
    try { sessionStorage.removeItem("readingProgress:v1:" + tracker.meta.id); saved = true; } catch (e) { saved = false; }
  } else {
    saved = sessionWrite("readingProgress:v1:" + tracker.meta.id, JSON.stringify(record));
  }
  updateMarkerControls(tracker.meta, tracker.langs, saved
    ? same ? "Marca removida." : "Parágrafo marcado. A bolinha vermelha indica o ponto salvo nesta sessão."
    : "Não foi possível salvar a marca neste navegador.");
}

function handleParagraphMark(event) {
  const tracker = state.readingTracker;
  if (!tracker || event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return;
  if (event.target.closest("a, button, input, textarea, select, summary")) return;
  const node = event.target.closest("[data-reading-target]");
  const entry = tracker.entries.find(item => item.node === node);
  if (!entry) return;
  if (event.type === "keydown") {
    if (event.target !== node || !["Enter", " "].includes(event.key)) return;
    event.preventDefault();
  } else {
    if (event.button !== 0 || window.getSelection()?.isCollapsed === false) return;
  }
  markReadingEntry(entry);
}

function resumeReading(meta, langs, record) {
  stopReadingTracking();
  const study = record.mode === "study" && langs.length > 1;
  state.viewMode = study ? "study" : "reading";
  if (study && ["paragraph", "parallel"].includes(record.studyMode)) state.studyMode = record.studyMode;
  state.readingLanguages.set(meta.id, record.language);
  try {
    localStorage.setItem("readingLanguage:" + meta.id, record.language);
    localStorage.setItem("documentViewMode", state.viewMode);
    localStorage.setItem("studyMode", state.studyMode);
    const pair = record.parallelCols;
    if (pair && pair.left !== pair.right && langs.some(l => l.code === pair.left) && langs.some(l => l.code === pair.right)) {
      localStorage.setItem("parallelCols:" + meta.id, `${pair.left},${pair.right}`);
      state.parallelCols={...pair};
    }
  } catch (e) {}
  refreshDocument(false);
  const tracker = state.readingTracker;
  const entry = tracker && resolveMarkedEntry(record, tracker.entries);
  if (!entry) {
    updateMarkerControls(meta, langs, "O texto mudou; não foi possível localizar o parágrafo marcado.");
    return;
  }
  if (study) {
    const cell = entry.node.closest(".cell");
    if (state.studyMode === "paragraph" && cell.classList.contains("secondary")) {
      cell.classList.add("visible");
      const toggle = entry.row.querySelector(`.block-toggle[data-lang="${entry.language}"]`);
      if (toggle) { toggle.classList.add("active"); toggle.setAttribute("aria-expanded", "true"); }
    } else if (state.studyMode === "parallel" && cell.classList.contains("hidden")) {
      setParallelCols("left", entry.language);
    }
  }
  paintReadingMarker(record);
  jumpToReadingBlock(entry.node, record.offset);
}

function selectableParagraphs(content) {
  return Array.from(content.querySelectorAll("h1, h2, h3, h4, h5, h6, p, li, pre, table"))
    .filter(block => !block.closest(".footnotes") &&
      !(block.tagName === "LI" && block.querySelector("p")) && block.textContent.trim());
}

function setupReadingNavigation(meta, langs, language, content) {
  const headings = Array.from(content.querySelectorAll("h1, h2, h3, h4, h5, h6"))
    .map(node => ({ node, level: Number(node.tagName.slice(1)) }));
  const entries = selectableParagraphs(content)
    .map((node, blockIndex) => ({ node, blockIndex, language: language.code }));
  setupParagraphNavigation(meta, langs, content, entries, headings, "reading");
}

function setupStudyNavigation(meta, langs) {
  stopReadingTracking();
  const content = document.querySelector(".blocks");
  if (!content) return;
  const indexLanguage = state.studyMode === "parallel" ? state.parallelCols.left : baseLanguageCode(langs);
  const source = langs.find(l => l.code === indexLanguage);
  const entries = [], headings = [], counts = new Map();
  Array.from(content.querySelectorAll(".block")).forEach((row, rowIndex) => {
    for (const cell of row.querySelectorAll(".cell")) {
      const language = cell.getAttribute("lang");
      for (const node of selectableParagraphs(cell)) {
        const blockIndex = counts.get(language) || 0;
        entries.push({ node, blockIndex, language, row });
        counts.set(language, blockIndex + 1);
      }
      const type = source?.blocks[rowIndex]?.type;
      if (language === indexLanguage && /^h[1-6]$/.test(type || "")) {
        const node = cell.querySelector("h2, h3, h4, h5, h6");
        if (node) {
          node.id = `study-${meta.id}-${language}-section-${rowIndex}`;
          headings.push({ node, level: Number(type.slice(1)) });
        }
      }
    }
  });
  setupParagraphNavigation(meta, langs, content, entries, headings, "study");
  installStudyPassageTools();
}

function setupParagraphNavigation(meta, langs, content, entries, headings, mode) {
  const tools = document.querySelector(".doc-toolbar .reading-tools");
  if(!tools)return;
  tools.innerHTML = "";
  const panel = el("details", { class: "reading-panel editorial-menu" });
  const summary = el("summary", {}, [
    el("span", { text: headings.length ? `Índice do texto · ${headings.length} seções` : "Posição de leitura" }),
    el("span", { class: "panel-marker", text: "●", title: "Há uma posição marcada", "aria-label": "Há uma posição marcada" }),
  ]);
  panel.appendChild(summary);
  const body = el("div", { class: "reading-panel-body editorial-menu-body" });
  const status = el("p", { class: "reading-session-status", id: "reading-marker-instructions", role: "status" });
  const controls = el("div", { class: "reading-session" }, [status]);
  const resume = el("button", { type: "button", class: "resume-btn", text: "Retomar leitura" });
  resume.addEventListener("click", () => {
    const record = savedReadingProgress(meta, langs);
    if (record) resumeReading(meta, langs, record);
  });
  controls.appendChild(resume);
  body.appendChild(controls);
  if (headings.length) {
    body.appendChild(el("section", { class: "reading-index" }, [
      el("h2", { text: "Índice do texto" }),
      el("nav", { class: "reading-toc", "aria-label": "Índice do texto" }, [buildReadingIndex(headings)]),
    ]));
  }
  panel.appendChild(body);
  panel.open = sessionRead("readingPanel:v1:" + meta.id) === "true";
  panel.addEventListener("toggle", () => {
    sessionWrite("readingPanel:v1:" + meta.id, String(panel.open));
    updateReadingLayout();
  });
  tools.appendChild(panel);
  tools.hidden = false;

  const tracker = { meta, langs, content, entries, headings, mode };
  state.readingTracker = tracker;
  for (const [index, entry] of entries.entries()) {
    entry.previousTabindex = entry.node.getAttribute("tabindex");
    entry.previousDescription = entry.node.getAttribute("aria-describedby");
    entry.node.dataset.readingTarget = String(index);
    entry.node.setAttribute("tabindex", "0");
    entry.node.setAttribute("aria-describedby", "reading-marker-instructions");
  }
  content.addEventListener("click", handleParagraphMark);
  content.addEventListener("keydown", handleParagraphMark);
  updateMarkerControls(meta, langs);
}

function stopReadingTracking() {
  const tools = document.querySelector(".reading-tools");
  if (tools) { tools.hidden = true; tools.innerHTML = ""; }
  updateReadingLayout();
  const tracker = state.readingTracker;
  if (!tracker) return;
  tracker.content.removeEventListener("click", handleParagraphMark);
  tracker.content.removeEventListener("keydown", handleParagraphMark);
  for (const entry of tracker.entries) {
    delete entry.node.dataset.readingTarget;
    for (const [attribute, previous] of [["tabindex", entry.previousTabindex], ["aria-describedby", entry.previousDescription]]) {
      if (previous === null) entry.node.removeAttribute(attribute);
      else entry.node.setAttribute(attribute, previous);
    }
  }
  state.readingTracker = null;
}

function renderReadingContent(meta, langs) {
  stopReadingTracking();
  const content = document.querySelector(".reading-content");
  if (!content) return;
  const language = langs.find(l => l.code === readingLanguage(meta, langs));
  content.lang = language.code;
  content.innerHTML = "";
  const format = language.format || meta.format;
  content.classList.toggle("plain-text", format === "text");
  if (format === "text") {
    for (const block of parsePlainText(language.source)) {
      content.appendChild(el("p", { text: block.text }));
    }
  } else {
    content.dataset.anchorPrefix = `reading-${meta.id}-${language.code}`;
    content.innerHTML = safeMarkdown(language.source, { docId: content.dataset.anchorPrefix });
  }
  setupReadingNavigation(meta, langs, language, content);
}

function handleReadingAnchor(event) {
  const link = event.target.closest("a[href]");
  if (!link || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  const href = link.getAttribute("href");
  if (!href.startsWith("#") || href.startsWith("#/")) return;
  // O roteador usa o hash; as notas navegam no texto sem alterar a rota.
  event.preventDefault();
  const content = event.currentTarget;
  let id;
  try { id = decodeURIComponent(href.slice(1)); } catch (e) { return; }
  const target = document.getElementById(id) || document.getElementById(`${content.dataset.anchorPrefix}-${id}`);
  if (!target || !content.contains(target)) return;
  jumpToReadingBlock(target);
}

function renderDocument(meta, langs, blocks, collection, subcollection, scroll = true) {
  stopReadingTracking();
  stopPanelLayoutTracking();
  const root = document.getElementById("view");
  root.innerHTML = "";
  state.activeDocument = { meta, langs, blocks, collection, subcollection };
  initParallelCols(meta.id, langs);

  const isStudy = langs.length > 1 && state.viewMode === "study";
  const mode = isStudy ? `study mode-${state.studyMode}` : "reading";
  const article = el("article", { class: "doc mode-" + mode });
  article.dataset.docId = meta.id;
  article.dataset.langCount = String(langs.length);
  const searchReturn = new URLSearchParams(location.hash.split("?")[1] || "").get("busca");
  if (searchReturn === "#/busca" || searchReturn?.startsWith("#/busca?")) {
    article.appendChild(el("a", { class: "back-link search-return", href: searchReturn, text: "← Voltar aos resultados da busca" }));
  }
  article.appendChild(renderToolbar(langs, meta));
  article.appendChild(renderDocHeader(meta, collection, subcollection));

  article.appendChild(el("div",{class:"document-body"}));
  article.appendChild(renderDocumentSequence(meta,collection,subcollection));
  root.appendChild(article);
  renderDocumentBody(meta,langs,blocks);
  setActiveNav(collection ? collection.id : null);
  if (scroll) window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderDocumentBody(meta,langs,blocks) {
  stopReadingTracking();
  const article=document.querySelector("article.doc");
  const host=article?.querySelector(".document-body");
  if(!host)return;
  const study=langs.length>1&&state.viewMode==="study";
  article.className="doc mode-"+(study?"study mode-"+state.studyMode:"reading");
  if(study&&host.querySelector(".blocks")){
    if(state.studyMode==="parallel")applyParallelLayout();
    else for(const cell of host.querySelectorAll(".cell,.col-labels>div")){cell.classList.remove("hidden");cell.style.order="";}
    setupStudyNavigation(meta,langs);
    return;
  }
  host.replaceChildren();
  if(study){
    const labels=el("div",{class:"col-labels cols-"+langs.length});
    for(const lang of langs)labels.append(el("div",{class:"label-"+lang.code,text:lang.label}));
    const body=el("div",{class:"blocks cols-"+langs.length});
    for(const [index,block] of blocks.entries()){const row=renderBlock(block,langs);row.dataset.studyBlock=String(index);body.append(row);}
    host.append(labels,body);
    if(state.studyMode==="parallel")applyParallelLayout();
    setupStudyNavigation(meta,langs);
  }else{
    const content=el("div",{class:"reading-content"});
    content.addEventListener("click",handleReadingAnchor);
    host.append(content);
    renderReadingContent(meta,langs);
  }
}

async function loadDocument(collection, docMeta, subcollection) {
  const requestedHash = location.hash;
  const requestedVersion = state.routeVersion;
  const cacheKey = docMeta.id;
  if (state.cache.has(cacheKey)) {
    const { langs, blocks } = state.cache.get(cacheKey);
    renderDocument(docMeta, langs, blocks, collection, subcollection);
    return;
  }

  const langs = await Promise.all(
    docMeta.languages.map(async l => {
      const rawSource = await fetchText(l.file);
      const format = l.format || docMeta.format;
      const source = format === "text" ? rawSource : splitExportHeaders(rawSource).body;
      return {
        code: l.code,
        label: l.label,
        source,
        format,
        blocks: format === "text" ? parsePlainText(source) : parseStudyMarkdown(source),
      };
    })
  );

  const counts = langs.map(l => `${l.code}=${l.blocks.length}`).join(" ");
  console.log(`[${docMeta.id}] blocos ${counts}`);
  if (new Set(langs.map(l => l.blocks.length)).size > 1) {
    console.warn(`[${docMeta.id}] contagens diferentes — alinhamento pode deslocar`);
  }

  const blocks = zipBlocks(langs);
  if(state.routeVersion!==requestedVersion)return;
  state.cache.set(cacheKey, { langs, blocks });
  if (location.hash !== requestedHash) return;
  renderDocument(docMeta, langs, blocks, collection, subcollection);
}

/* ---------- Renderização: coleção ---------- */

function renderCollection(collection, subcollection = null, showAll = false, requestedPage = 1) {
  stopReadingTracking();
  const root = document.getElementById("view");
  root.innerHTML = "";

  const wrap = el("section", { class: "collection" });
  wrap.appendChild(renderBreadcrumbs(
    subcollection || showAll ? collection : null,
    null,
    subcollection ? subcollection.title_pt : showAll ? "Todos os documentos" : collection.title_pt
  ));

  const hero = el("header", { class: "collection-hero" });
  hero.style.setProperty("--accent", collection.accent || "#8b2c2c");
  if (collection.cover) {
    hero.classList.add("has-cover");
    hero.style.setProperty("--cover", `url("${absURL(collection.cover)}")`);
  }
  hero.appendChild(el("p", { class: "doc-eyebrow", text: subcollection ? "Subcoleção" : "Coleção" }));
  hero.appendChild(el("h1", {}, [
    subcollection ? subcollection.title_pt : collection.title_pt,
    el("span", { class: "ru-title", lang: "ru", text: subcollection ? subcollection.title_ru : collection.title_ru }),
  ]));
  if (collection.subtitle_pt)
    hero.appendChild(el("p", { class: "collection-subtitle", text: collection.subtitle_pt }));
  if (collection.description_pt)
    hero.appendChild(el("p", { class: "collection-description", text: collection.description_pt }));
  wrap.appendChild(hero);

  if (collection.subcollections?.length && !subcollection && !showAll) {
    const grid = el("div", { class: "subcollection-grid" });
    const documentMap = new Map(collectionDocuments(collection).map(doc => [doc.id, doc]));
    for (const sub of collection.subcollections) {
      const availableLanguages = new Set(sub.document_ids.flatMap(id =>
        (documentMap.get(id)?.languages || []).map(language => language.code.toUpperCase())));
      const card = el("a", {
        class: "doc-list-item", href: `#/colecao/${collection.id}/subcolecao/${sub.id}`,
      }, [
        el("h2", { class: "doc-list-title", text: sub.title_pt }),
        el("p", { class: "doc-list-ru", lang: "ru", text: sub.title_ru }),
        el("p", { class: "doc-list-meta", text: `${sub.document_ids.length} documentos · ${[...availableLanguages].join(" · ")}` }),
      ]);
      grid.appendChild(card);
    }
    wrap.appendChild(grid);
    wrap.appendChild(el("a", {
      class: "all-documents-link", href: `#/colecao/${collection.id}/todos`,
      text: `Ver todos os ${collectionDocuments(collection).length} documentos`,
    }));
    root.appendChild(wrap);
    setActiveNav(collection.id);
    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }

  if (subcollection && subcollection.source_url) {
    wrap.appendChild(el("p", { class: "source-info" }, [
      el("a", { href: subcollection.source_url, text: "Consultar esta subcoleção no ShowTrials" }),
    ]));
  }
  const documents = subcollection
    ? subcollection.document_ids.map(id => collectionDocuments(collection).find(doc => doc.id === id))
    : collectionDocuments(collection);
  const pages=Math.max(1,Math.ceil(documents.length/COLLECTION_PAGE_SIZE));
  const parsed=Number(requestedPage);
  const page=Number.isSafeInteger(parsed)&&parsed>0?Math.min(parsed,pages):1;
  const start=(page-1)*COLLECTION_PAGE_SIZE;
  wrap.appendChild(el("p", {
    class: "document-count", text: documents.length?`${start+1}–${Math.min(start+COLLECTION_PAGE_SIZE,documents.length)} de ${documents.length} documentos · Página ${page} de ${pages}`:"Nenhum documento",
  }));
  wrap.appendChild(renderCollectionPagination(documents.length,page,collection,subcollection));
  const list = el("div", { class: "doc-list" });
  for (const doc of documents.slice(start,start+COLLECTION_PAGE_SIZE)) {
    const item = el("a", { class: "doc-list-item", href: collectionDocumentURL(doc, subcollection, collection,page) });

    const topLine = el("div", { class: "doc-list-topline" });
    topLine.appendChild(el("span", {
      class: "doc-type doc-type-" + (doc.type || "document"),
      text: doc.type === "article" ? "Artigo" : "Documento",
    }));
    if (doc.eyebrow) {
      topLine.appendChild(document.createTextNode(" "));
      topLine.appendChild(el("span", { class: "doc-list-eyebrow", text: doc.eyebrow }));
    }
    item.appendChild(topLine);

    item.appendChild(el("div",{class:"document-title-line"},[el("h2", {
      class: "doc-list-title", lang: doc.title_pt ? "pt-BR" : doc.title_ru?"ru":"en",
      text: documentTitle(doc),
    }),documentDateBadge(doc)]));
    if (doc.title_pt && doc.title_ru)
      item.appendChild(el("p", { class: "doc-list-ru", lang: "ru", text: doc.title_ru }));

    const meta = el("div", { class: "doc-list-meta" });
    if (doc.author) meta.appendChild(el("span", { text: doc.author }));
    if (doc.archive) meta.appendChild(el("span", { text: doc.archive }));
    if (doc.languages.length === 1 && doc.languages[0].code === "ru") {
      meta.appendChild(el("span", { text: "Disponível em russo" }));
    }
    const tags = el("span", { class: "lang-tags" });
    for (const l of doc.languages) {
      tags.appendChild(el("span", { class: "lang-tag", text: l.code.toUpperCase() }));
    }
    meta.appendChild(tags);
    item.appendChild(meta);
    list.appendChild(item);
  }
  wrap.appendChild(list);
  wrap.appendChild(renderCollectionPagination(documents.length,page,collection,subcollection));

  root.appendChild(wrap);
  setActiveNav(collection.id);
  if(page>1)requestAnimationFrame(()=>wrap.querySelector(".document-count")?.scrollIntoView({block:"start",behavior:"instant"}));
  else window.scrollTo({ top: 0, behavior: "smooth" });
}

/* ---------- Renderização: homepage ---------- */

function renderHome() {
  stopReadingTracking();
  const root = document.getElementById("view");
  root.innerHTML = "";

  const wrap = el("section", { class: "home" });

  const intro = el("header", { class: "home-intro" });
  intro.appendChild(el("p", { class: "doc-eyebrow", text: "Arquivo" }));
  intro.appendChild(el("h1", {}, ["Documentos Soviéticos"]));
  intro.appendChild(el("p", {
    class: "home-subtitle",
    text: "Fontes primárias e ensaios históricos sobre o período stalinista, em russo e em edições com traduções para português e inglês."
  }));
  wrap.appendChild(intro);

  const homeSearch = el("form", { class: "home-search", role: "search", "aria-label": "Buscar no acervo" });
  const query = el("input", { type: "search", name: "q", maxlength: "500", "aria-label": "Palavras para buscar no acervo", placeholder: "Buscar no acervo…" });
  homeSearch.appendChild(query);
  homeSearch.appendChild(el("button", { type: "submit", class: "search-submit", text: "Buscar" }));
  homeSearch.addEventListener("submit", event => {
    event.preventDefault();
    const params = new URLSearchParams();
    if (query.value.trim()) params.set("q", query.value.trim());
    location.hash = searchURL(params);
  });
  wrap.appendChild(homeSearch);

  const grid = el("div", { class: "collection-grid" });
  for (const c of state.manifest.collections) {
    const card = el("a", { class: "collection-card", href: `#/colecao/${c.id}` });
    card.style.setProperty("--accent", c.accent || "#8b2c2c");
    if (c.cover) {
      card.classList.add("has-cover");
      card.style.setProperty("--cover", `url("${absURL(c.cover)}")`);
    }
    const body = el("div", { class: "collection-card-body" });
    body.appendChild(el("p", {
      class: "collection-card-eyebrow",
      text: c.subcollections?.length
        ? `${collectionDocuments(c).length} documentos · ${c.subcollections.length} subcoleções`
        : collectionDocuments(c).length === 1 ? "1 item" : `${collectionDocuments(c).length} itens`
    }));
    body.appendChild(el("h2", { text: c.title_pt }));
    body.appendChild(el("p", { class: "collection-card-ru", text: c.title_ru }));
    if (c.subtitle_pt)
      body.appendChild(el("p", { class: "collection-card-subtitle", text: c.subtitle_pt }));
    card.appendChild(body);
    grid.appendChild(card);
  }
  wrap.appendChild(grid);

  root.appendChild(wrap);
  setActiveNav(null);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/* ---------- Roteamento ---------- */

function findCollectionByDocId(docId) {
  for (const c of state.manifest.collections) {
    if (collectionDocuments(c).some(d => d.id === docId)) return c;
  }
  return null;
}

function parseRoute() {
  const hash = location.hash.replace(/^#\/?/, "").trim();
  if (!hash) return { view: "home" };
  const [path, query = ""] = hash.split("?");
  const parts = path.split("/");
  if (parts[0] === "busca") return { view: "search", params: new URLSearchParams(query) };
  if (parts[0] === "colecao" && parts[1]) return {
    view: "collection", id: parts[1],
    subcollectionId: parts[2] === "subcolecao" ? parts[3] : null,
    showAll: parts[2] === "todos",
    page: new URLSearchParams(query).get("pagina")||1,
  };
  if (parts[0] === "doc" && parts[1]) return {
    view: "document", id: parts[1],
    subcollectionId: new URLSearchParams(query).get("subcolecao"),
    collectionId: new URLSearchParams(query).get("colecao"),
  };
  return { view: "home" };
}

async function route() {
  state.routeVersion++;
  activeSearchRequest?.abort();
  stopReadingTracking();
  stopPanelLayoutTracking();
  const r = parseRoute();
  try {
    if (r.view === "home") {
      renderHome();
    } else if (r.view === "search") {
      await renderSearch(r.params);
    } else if (r.view === "collection") {
      const c = state.manifest.collections.find(x => x.id === r.id);
      if (!c) { location.hash = "#/"; return; }
      const sub = c.subcollections?.find(s => s.id === r.subcollectionId);
      if (r.subcollectionId && !sub) { location.hash = `#/colecao/${c.id}`; return; }
      renderCollection(c, sub, r.showAll,r.page);
    } else if (r.view === "document") {
      const context = state.manifest.collections.find(c => c.id === r.collectionId);
      const c = context && collectionDocuments(context).some(d => d.id === r.id)
        ? context : findCollectionByDocId(r.id);
      if (!c) { location.hash = "#/"; return; }
      const doc = collectionDocuments(c).find(d => d.id === r.id);
      const editorialContext = editorialReadingContext(doc.id);
      const language = new URLSearchParams(location.hash.split("?")[1] || "").get("idioma");
      if (doc.languages.some(l => l.code === language)) state.readingLanguages.set(doc.id, language);
      applyEditorialReading(editorialContext,doc);
      const sub = c.subcollections?.find(s => s.id === r.subcollectionId && s.document_ids.includes(doc.id));
      await loadDocument(c, doc, sub);
      if(parseRoute().id===doc.id)restoreEditorialReading(editorialContext);
    }
  } catch (err) {
    console.error(err);
    document.getElementById("view").innerHTML =
      `<p class="reader-error">
         Erro: ${escapeHTML(err.message)}
       </p>`;
  }
}

async function main() {
  try {
    try {
      const saved = localStorage.getItem("documentViewMode");
      if (saved === "reading" || saved === "study") state.viewMode = saved;
      const studyMode = localStorage.getItem("studyMode");
      if (studyMode === "paragraph" || studyMode === "parallel") state.studyMode = studyMode;
    } catch (e) {}

    state.manifest = await fetchJSON("data/manifest.json");
    state.documentIndex = new Map((state.manifest.documents || []).map(d => [d.id, d]));
    renderNav();
    detectReaderEditorial();
    updateReadingLayout();
    if (typeof ResizeObserver !== "undefined") {
      new ResizeObserver(updateReadingLayout).observe(document.querySelector(".site-header"));
    }
    window.addEventListener("resize", updateReadingLayout);
    document.addEventListener("click", event => {
      if(document.querySelector("dialog[open]"))return;
      for(const menu of document.querySelectorAll(".editorial-menu[open]"))if(!menu.contains(event.target))menu.open=false;
      const tools = document.querySelector(".reading-tools");
      if (tools && !tools.contains(event.target)) closeDocumentPanel();
    });
    document.addEventListener("keydown", event => {
      if(document.querySelector("dialog[open]"))return;
      if(event.key==="Escape")for(const menu of document.querySelectorAll(".editorial-menu[open]")){menu.open=false;menu.querySelector("summary")?.focus();}
      if (event.key === "Escape" && document.querySelector(".reading-panel")?.open) {
        closeDocumentPanel();
        document.querySelector(".reading-panel > summary")?.focus();
      }
    });
    window.addEventListener("pagehide", () => {stopReadingTracking();stopPanelLayoutTracking();});
    window.addEventListener("pageshow", event => {
      if (event.persisted) reloadEditorialCatalog(state.editorialDepartureContext).catch(console.error);
    });
    window.addEventListener("storage",event=>{
      if(event.key==="editorialCatalogChanged")reloadEditorialCatalog().catch(console.error);
    });
    window.addEventListener("hashchange", route);
    await route();
  } catch (err) {
    console.error(err);
    document.getElementById("view").innerHTML =
      `<p class="reader-error">
         Erro ao carregar manifest: ${escapeHTML(err.message)}
       </p>`;
  }
}

document.addEventListener("DOMContentLoaded", main);
