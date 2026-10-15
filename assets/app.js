/* =========================================================
   Site bilíngue/trilíngue: coleções de documentos soviéticos.
   ========================================================= */

const state = {
  manifest: null,
  cache: new Map(),
  documentIndex: new Map(),
  activeCollection: null,
  viewMode: "reading",
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

/* ---------- Parser markdown ---------- */

function normalizeHeadingLevel(text, mdLevel) {
  if (/^[IVX]+\.\s/.test(text)) return 2;
  if (/^\d+[.)]\s/.test(text)) return 3;
  return mdLevel;
}

// As exportações ShowTrials são texto: asteriscos e outros sinais pertencem à fonte.
function parsePlainText(text) {
  return text.replace(/\r\n/g, "\n").split(/\n\s*\n/)
    .map(text => text.trim()).filter(Boolean)
    .map(text => ({ type: "text", text }));
}

function parseMarkdown(md) {
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
        const level = Math.min(h[1].length, 3);
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
  const rank = { h1: 0, h2: 1, h3: 2, image: 3, list: 4, quote: 4, p: 5, text: 5 };
  const n = Math.max(...langs.map(l => l.blocks.length));
  const out = [];
  for (let i = 0; i < n; i++) {
    const cells = {};
    const types = [];
    for (const l of langs) {
      const b = l.blocks[i] || null;
      cells[l.code] = (b || {}).text || "";
      if (b) types.push(b.type);
    }
    const btype = types.length
      ? types.reduce((a, b) => (rank[a] < rank[b] ? a : b))
      : "p";
    out.push({ type: btype, cells });
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

function inline(text) {
  let out = escapeHTML(text);
  out = out.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/\*(.+?)\*/g, "<em>$1</em>");
  out = out.replace(/!\[(.*?)\]\((.+?)\)/g, (_, alt, src) =>
    `<img class="md-img-inline" src="${absURL(src)}" alt="${alt}" loading="lazy">`);
  return out;
}

function baseLanguageCode(langs) {
  if (langs.some(l => l.code === "pt")) return "pt";
  if (langs.some(l => l.code === "en")) return "en";
  return langs[0].code;
}

/* ---------- Modo de visualização ---------- */

function setViewMode(mode) {
  state.viewMode = mode;
  try { localStorage.setItem("viewMode", mode); } catch (e) {}
  document.querySelectorAll(".doc-toolbar .mode-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.mode === mode);
  });
  const article = document.querySelector("article.doc");
  if (!article) return;
  article.classList.remove("mode-reading", "mode-parallel");
  article.classList.add("mode-" + mode);
  if (mode === "parallel") {
    applyParallelLayout();
  } else {
    article.querySelectorAll(".cell.hidden").forEach(c => {
      c.classList.remove("hidden");
      c.style.order = "";
    });
    const labels = article.querySelector(".col-labels");
    if (labels) {
      labels.querySelectorAll(":scope > div").forEach(d => {
        d.classList.remove("hidden");
        d.style.order = "";
      });
    }
  }
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
}

function setActiveNav(collectionId) {
  state.activeCollection = collectionId || null;
  const select = document.querySelector("#docNav .collection-select");
  if (select) select.value = collectionId || "";
  const home = document.querySelector("#docNav .nav-link");
  if (home) {
    if (!collectionId) home.setAttribute("aria-current", "page");
    else home.removeAttribute("aria-current");
  }
}

/* ---------- Renderização: documento ---------- */

function renderCellContent(block, code) {
  const frag = document.createDocumentFragment();
  const raw = (block.cells[code] || "").trim();
  if (!raw) { frag.appendChild(el("p", { text: "—" })); return frag; }

  if (block.type === "text") {
    frag.appendChild(el("p", { text: raw }));
    return frag;
  }

  if (block.type === "image") {
    const m = raw.match(/^!\[(.*?)\]\((.+?)\)$/);
    if (m) {
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
  if (block.type === "h1") tag = "h2";
  else if (block.type === "h2") tag = "h3";
  else if (block.type === "h3") tag = "h4";

  const p = el(tag);
  p.innerHTML = inline(raw);
  frag.appendChild(p);
  return frag;
}

function renderBlock(b, allLangs) {
  const isHeading = b.type === "h1" || b.type === "h2" || b.type === "h3";
  const isImage = b.type === "image";
  const wrap = el("div", { class: "block" + (isHeading ? " is-heading" : "") });
  const baseCode = baseLanguageCode(allLangs);

  // Botões de tradução (só no modo Leitura, só se houver >1 idioma, exceto imagens)
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
  if (meta.format !== "text") return language.source;
  const title = meta[`title_${language.code}`] || meta.title_ru || meta.title_pt;
  const lines = [`# ${escapeMarkdownText(title)}`, ""];
  if (meta.source_url) lines.push(`Fonte: ${meta.source_url}`);
  if (meta.source_id) lines.push(`ID ShowTrials: ${meta.source_id}`);
  lines.push(`Idioma: ${language.code.toUpperCase()}`, "", "---", "");
  lines.push(escapeMarkdownText(language.source));
  return lines.join("\n");
}

function downloadMarkdown(meta, language) {
  const blob = new Blob([documentMarkdown(meta, language)], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = el("a", { href: url, download: `${meta.id}.${language.code}.md` });
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function renderToolbar(langs, meta) {
  const bar = el("div", { class: "doc-toolbar" });

  if (langs.length > 1) {
    const modeGroup = el("div", { class: "toolbar-group" });
    modeGroup.appendChild(el("span", { class: "toolbar-label", text: "Modo:" }));
    [["reading", "Leitura"], ["parallel", "Paralelo"]].forEach(([code, label]) => {
      const btn = el("button", {
        type: "button",
        class: "mode-btn" + (state.viewMode === code ? " active" : ""),
        "data-mode": code,
        text: label,
      });
      btn.addEventListener("click", () => setViewMode(code));
      modeGroup.appendChild(btn);
    });
    bar.appendChild(modeGroup);
  }

  if (langs.length > 2) {
    const colGroup = el("div", { class: "toolbar-group parallel-only" });
    colGroup.appendChild(el("span", { class: "toolbar-label", text: "Colunas:" }));
    ["left", "right"].forEach(side => {
      const sel = el("select", {
        class: "lang-select",
        "data-side": side,
        "aria-label": side === "left" ? "Idioma à esquerda" : "Idioma à direita",
      });
      for (const l of langs) {
        sel.appendChild(el("option", { value: l.code, text: l.code.toUpperCase() }));
      }
      sel.value = state.parallelCols[side] || langs[0].code;
      sel.addEventListener("change", () => setParallelCols(side, sel.value));
      colGroup.appendChild(sel);
    });
    bar.appendChild(colGroup);
  }

  const exportGroup = el("div", { class: "toolbar-group export-group" });
  let exportCode = baseLanguageCode(langs);
  if (langs.length > 1) {
    const select = el("select", { class: "export-language", "aria-label": "Idioma para exportação" });
    const names = { pt: "Português", ru: "Russo", en: "Inglês" };
    for (const l of langs) {
      select.appendChild(el("option", { value: l.code, text: names[l.code] || l.label }));
    }
    select.value = exportCode;
    select.addEventListener("change", () => { exportCode = select.value; });
    exportGroup.appendChild(select);
  }
  const button = el("button", { type: "button", class: "export-btn", text: "Exportar Markdown" });
  button.addEventListener("click", () => {
    downloadMarkdown(meta, langs.find(l => l.code === exportCode));
  });
  exportGroup.appendChild(button);
  bar.appendChild(exportGroup);
  return bar;
}

function renderDocument(meta, langs, blocks, collection, subcollection) {
  const root = document.getElementById("view");
  root.innerHTML = "";

  initParallelCols(meta.id, langs);

  const mode = langs.length === 1 ? "reading" : state.viewMode;
  const article = el("article", { class: "doc mode-" + mode });
  article.dataset.docId = meta.id;
  article.dataset.langCount = String(langs.length);

  article.appendChild(renderDocHeader(meta, collection, subcollection));
  article.appendChild(renderToolbar(langs, meta));

  const labels = el("div", { class: "col-labels cols-" + langs.length });
  for (const l of langs) {
    labels.appendChild(el("div", { class: "label-" + l.code, text: l.label }));
  }
  article.appendChild(labels);

  const blocksWrap = el("div", { class: "blocks cols-" + langs.length });
  for (const b of blocks) blocksWrap.appendChild(renderBlock(b, langs));
  article.appendChild(blocksWrap);

  root.appendChild(article);

  if (state.viewMode === "parallel" && langs.length > 2) {
    applyParallelLayout();
  }

  setActiveNav(collection ? collection.id : null);
  window.scrollTo({ top: 0, behavior: "smooth" });
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
      return {
        code: l.code,
        label: l.label,
        source,
        blocks: docMeta.format === "text" ? parsePlainText(source) : parseMarkdown(source),
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
    for (const sub of collection.subcollections) {
      const card = el("a", {
        class: "doc-list-item", href: `#/colecao/${collection.id}/subcolecao/${sub.id}`,
      }, [
        el("h2", { class: "doc-list-title", text: sub.title_pt }),
        el("p", { class: "doc-list-ru", lang: "ru", text: sub.title_ru }),
        el("p", { class: "doc-list-meta", text: `${sub.document_ids.length} documentos · Em russo` }),
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
  const r = parseRoute();
  try {
    if (r.view === "home") {
      renderHome();
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
      const saved = localStorage.getItem("viewMode");
      if (saved === "reading" || saved === "parallel") state.viewMode = saved;
    } catch (e) {}

    state.manifest = await fetchJSON("data/manifest.json");
    state.documentIndex = new Map((state.manifest.documents || []).map(d => [d.id, d]));
    renderNav();
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