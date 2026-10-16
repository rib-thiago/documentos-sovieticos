/* =========================================================
   Site bilíngue/trilíngue: coleções de documentos soviéticos.
   ========================================================= */

const state = {
  manifest: null,
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
  const text = md.replace(/\r\n/g, "\n").trim();
  const chunks = text.split(/\n{2,}/);
  const blocks = [];
  for (const raw of chunks) {
    const chunk = raw.trim();
    if (!chunk) continue;
    if (/^-{3,}$/.test(chunk)) continue;

    if (!chunk.includes("\n")) {
      const h = chunk.match(/^(#{1,6})\s+(.+)$/);
      if (h) {
        const level = h[1].length;
        blocks.push({
          type: "h" + normalizeHeadingLevel(h[2].trim(), level),
          text: h[2].trim(),
        });
        continue;
      }
      if (/^!\[.*?\]\(.+?\)$/.test(chunk)) {
        blocks.push({ type: "image", text: chunk });
        continue;
      }
    }

    const lines = chunk.split("\n").map(l => l.trim()).filter(Boolean);

    if (lines.length && lines.every(l => l.startsWith("- "))) {
      blocks.push({ type: "list", text: lines.join("\n") });
      continue;
    }
    if (lines.length && lines.every(l => l.startsWith(">"))) {
      const quoted = lines.map(l => l.replace(/^>\s?/, "")).join(" ");
      blocks.push({ type: "quote", text: quoted });
      continue;
    }
    blocks.push({ type: "p", text: lines.join(" ") });
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

function refreshDocument() {
  if (!state.activeDocument) return;
  const { meta, langs, blocks, collection, subcollection } = state.activeDocument;
  renderDocument(meta, langs, blocks, collection, subcollection, false);
}

function setViewMode(mode) {
  if (!["reading", "study"].includes(mode)) return;
  state.viewMode = mode;
  try { localStorage.setItem("documentViewMode", mode); } catch (e) {}
  refreshDocument();
}

function setStudyMode(mode) {
  if (!["paragraph", "parallel"].includes(mode)) return;
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
  renderReadingContent(meta, langs);
  const exportSelect = document.querySelector(".export-language");
  if (exportSelect) exportSelect.value = code;
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
  const active = state.activeDocument;
  if (active) setupStudyNavigation(active.meta, active.langs);
}

function updateParallelSelects() {
  document.querySelectorAll(".lang-select").forEach(sel => {
    sel.value = state.parallelCols[sel.dataset.side];
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

function collectionDocumentURL(doc, subcollection, collection) {
  const params = new URLSearchParams();
  params.set("colecao", collection.id);
  if (subcollection) params.set("subcolecao", subcollection.id);
  return `#/doc/${doc.id}?${params}`;
}

function renderBreadcrumbs(collection, subcollection, current) {
  const nav = el("nav", { class: "breadcrumbs", "aria-label": "Caminho de navegação" });
  nav.appendChild(el("a", { href: "#/", text: "Acervo" }));
  if (collection) {
    nav.appendChild(el("span", { text: " / ", "aria-hidden": "true" }));
    nav.appendChild(el("a", { href: `#/colecao/${collection.id}`, text: collection.title_pt }));
  }
  if (subcollection) {
    nav.appendChild(el("span", { text: " / ", "aria-hidden": "true" }));
    nav.appendChild(el("a", {
      href: `#/colecao/${collection.id}/subcolecao/${subcollection.id}`,
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
  header.appendChild(el("p", { class: "doc-eyebrow", text: meta.eyebrow || "Documento" }));
  header.appendChild(el("h1", {}, [
    meta.title_pt || meta.title_ru,
    meta.title_pt && meta.title_ru ? el("span", { class: "ru-title", lang: "ru", text: meta.title_ru }) : null,
  ]));
  if (!meta.title_pt && meta.title_ru) header.querySelector("h1").lang = "ru";
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
  [meta.date, meta.archive].filter(Boolean)
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
  const title = meta[`title_${language.code}`] || meta.title_ru || meta.title_pt;
  const lines = [`# ${escapeMarkdownText(title)}`, ""];
  if (meta.source_url) lines.push(`Fonte: ${meta.source_url}`);
  if (meta.source_id) lines.push(`ID ShowTrials: ${meta.source_id}`);
  lines.push(`Idioma: ${language.code.toUpperCase()}`, "", "---", "");
  lines.push(format === "text" ? escapeMarkdownText(language.source) : language.source);
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

function renderToolbar(langs, meta) {
  const bar = el("div", { class: "doc-toolbar" });
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
    bar.appendChild(modes);

    if (isStudy) {
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
      bar.appendChild(submodes);
    } else {
      const languageGroup = el("div", { class: "toolbar-group" });
      languageGroup.appendChild(el("span", { class: "toolbar-label", text: "Idioma:" }));
      const select = languageSelect(langs, "reading-language", "Idioma de leitura", readingLanguage(meta, langs));
      select.addEventListener("change", () => setReadingLanguage(meta, langs, select.value));
      languageGroup.appendChild(select);
      bar.appendChild(languageGroup);
    }
  }

  if (isStudy && state.studyMode === "parallel" && langs.length > 2) {
    const colGroup = el("div", { class: "toolbar-group parallel-only" });
    colGroup.appendChild(el("span", { class: "toolbar-label", text: "Colunas:" }));
    ["left", "right"].forEach(side => {
      const select = languageSelect(langs, "lang-select", side === "left" ? "Idioma à esquerda" : "Idioma à direita", state.parallelCols[side]);
      select.dataset.side = side;
      select.addEventListener("change", () => setParallelCols(side, select.value));
      colGroup.appendChild(select);
    });
    bar.appendChild(colGroup);
  }

  const exportGroup = el("div", { class: "toolbar-group export-group" });
  if (hasTranslations) {
    exportGroup.appendChild(languageSelect(langs, "export-language", "Idioma para exportação", readingLanguage(meta, langs)));
  }
  const button = el("button", { type: "button", class: "export-btn", text: "Exportar Markdown" });
  button.addEventListener("click", () => {
    const code = exportGroup.querySelector(".export-language")?.value || langs[0].code;
    downloadMarkdown(meta, langs.find(l => l.code === code));
  });
  exportGroup.appendChild(button);
  bar.appendChild(exportGroup);
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

function updateReadingLayout() {
  const header = document.querySelector(".site-header");
  document.documentElement.style.setProperty("--site-header-height", `${header?.getBoundingClientRect().height || 0}px`);
}

function readingViewportTop() {
  return (document.querySelector(".site-header")?.getBoundingClientRect().height || 0) + 24;
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
    }
  } catch (e) {}
  refreshDocument();
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
}

function setupParagraphNavigation(meta, langs, content, entries, headings, mode) {
  const tools = document.querySelector(".reading-tools");
  tools.innerHTML = "";
  const panel = el("details", { class: "reading-panel" });
  const summary = el("summary", {}, [
    el("span", { text: headings.length ? "Índice e marcador" : "Marcador" }),
    el("span", { class: "panel-marker", text: "●", title: "Há uma posição marcada", "aria-label": "Há uma posição marcada" }),
  ]);
  panel.appendChild(summary);
  const body = el("div", { class: "reading-panel-body" }, [
    el("div", { class: "reading-panel-heading" }, [
      el("p", { class: "reading-panel-caption", text: "Neste documento" }),
      el("p", { class: "reading-panel-title", text: meta.title_pt || meta.title_ru }),
    ]),
  ]);
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
  document.querySelector(".site-header")?.classList.add("has-document");
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
  if (typeof ResizeObserver !== "undefined") {
    tracker.observer = new ResizeObserver(updateReadingLayout);
    tracker.observer.observe(tools);
  }
  updateMarkerControls(meta, langs);
}

function stopReadingTracking() {
  const tools = document.querySelector(".reading-tools");
  if (tools) { tools.hidden = true; tools.innerHTML = ""; }
  document.querySelector(".site-header")?.classList.remove("has-document");
  updateReadingLayout();
  const tracker = state.readingTracker;
  if (!tracker) return;
  tracker.observer?.disconnect();
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
  article.appendChild(renderDocHeader(meta, collection, subcollection));
  article.appendChild(renderToolbar(langs, meta));

  if (isStudy) {
    const labels = el("div", { class: "col-labels cols-" + langs.length });
    for (const l of langs) {
      labels.appendChild(el("div", { class: "label-" + l.code, text: l.label }));
    }
    article.appendChild(labels);
    const blocksWrap = el("div", { class: "blocks cols-" + langs.length });
    for (const b of blocks) blocksWrap.appendChild(renderBlock(b, langs));
    article.appendChild(blocksWrap);
  } else {
    const content = el("div", { class: "reading-content" });
    content.addEventListener("click", handleReadingAnchor);
    article.appendChild(content);
  }
  root.appendChild(article);
  if (isStudy) {
    if (state.studyMode === "parallel") applyParallelLayout();
    setupStudyNavigation(meta, langs);
  } else renderReadingContent(meta, langs);
  setActiveNav(collection ? collection.id : null);
  if (scroll) window.scrollTo({ top: 0, behavior: "smooth" });
}

async function loadDocument(collection, docMeta, subcollection) {
  const requestedHash = location.hash;
  const cacheKey = docMeta.id;
  if (state.cache.has(cacheKey)) {
    const { langs, blocks } = state.cache.get(cacheKey);
    renderDocument(docMeta, langs, blocks, collection, subcollection);
    return;
  }

  const langs = await Promise.all(
    docMeta.languages.map(async l => {
      const source = await fetchText(l.file);
      const format = l.format || docMeta.format;
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
  state.cache.set(cacheKey, { langs, blocks });
  if (location.hash !== requestedHash) return;
  renderDocument(docMeta, langs, blocks, collection, subcollection);
}

/* ---------- Renderização: coleção ---------- */

function renderCollection(collection, subcollection = null, showAll = false) {
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

  if (collection.subcollections && !subcollection && !showAll) {
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
  wrap.appendChild(el("p", {
    class: "document-count", text: `${documents.length} ${documents.length === 1 ? "documento" : "documentos"}`,
  }));
  const list = el("div", { class: "doc-list" });
  for (const doc of documents) {
    const item = el("a", { class: "doc-list-item", href: collectionDocumentURL(doc, subcollection, collection) });

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

    item.appendChild(el("h2", {
      class: "doc-list-title", lang: doc.title_pt ? "pt-BR" : "ru",
      text: doc.title_pt || doc.title_ru,
    }));
    if (doc.title_pt && doc.title_ru)
      item.appendChild(el("p", { class: "doc-list-ru", lang: "ru", text: doc.title_ru }));

    const meta = el("div", { class: "doc-list-meta" });
    if (doc.author) meta.appendChild(el("span", { text: doc.author }));
    if (doc.date) meta.appendChild(el("span", { text: doc.date }));
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

  root.appendChild(wrap);
  setActiveNav(collection.id);
  window.scrollTo({ top: 0, behavior: "smooth" });
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
      text: c.subcollections
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
  };
  if (parts[0] === "doc" && parts[1]) return {
    view: "document", id: parts[1],
    subcollectionId: new URLSearchParams(query).get("subcolecao"),
    collectionId: new URLSearchParams(query).get("colecao"),
  };
  return { view: "home" };
}

async function route() {
  activeSearchRequest?.abort();
  stopReadingTracking();
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
      renderCollection(c, sub, r.showAll);
    } else if (r.view === "document") {
      const context = state.manifest.collections.find(c => c.id === r.collectionId);
      const c = context && collectionDocuments(context).some(d => d.id === r.id)
        ? context : findCollectionByDocId(r.id);
      if (!c) { location.hash = "#/"; return; }
      const doc = collectionDocuments(c).find(d => d.id === r.id);
      const language = new URLSearchParams(location.hash.split("?")[1] || "").get("idioma");
      if (doc.languages.some(l => l.code === language)) state.readingLanguages.set(doc.id, language);
      const sub = c.subcollections?.find(s => s.id === r.subcollectionId && s.document_ids.includes(doc.id));
      await loadDocument(c, doc, sub);
    }
  } catch (err) {
    console.error(err);
    document.getElementById("view").innerHTML =
      `<p style="color:#8b2c2c;font-family:Inter,sans-serif;padding:2rem">
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
    updateReadingLayout();
    if (typeof ResizeObserver !== "undefined") {
      new ResizeObserver(updateReadingLayout).observe(document.querySelector(".site-header"));
    }
    window.addEventListener("resize", updateReadingLayout);
    document.addEventListener("click", event => {
      const tools = document.querySelector(".reading-tools");
      if (tools && !tools.contains(event.target)) closeDocumentPanel();
    });
    document.addEventListener("keydown", event => {
      if (event.key === "Escape" && document.querySelector(".reading-panel")?.open) {
        closeDocumentPanel();
        document.querySelector(".reading-panel > summary")?.focus();
      }
    });
    window.addEventListener("pagehide", () => stopReadingTracking());
    window.addEventListener("pageshow", event => {
      if (event.persisted && document.querySelector("article.doc")) refreshDocument();
    });
    window.addEventListener("hashchange", route);
    await route();
  } catch (err) {
    console.error(err);
    document.getElementById("view").innerHTML =
      `<p style="color:#8b2c2c;font-family:Inter,sans-serif;padding:2rem">
         Erro ao carregar manifest: ${escapeHTML(err.message)}
       </p>`;
  }
}

document.addEventListener("DOMContentLoaded", main);
