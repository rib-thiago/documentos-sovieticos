/* =========================================================
   Site bilíngue/trilíngue: coleções de documentos soviéticos.
   Roteamento por hash:
     #/                     → homepage
     #/colecao/:id          → página da coleção
     #/doc/:id              → documento (N colunas)
   ========================================================= */

const state = { manifest: null, cache: new Map(), activeCollection: null };

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

/* ---------- Utilidade: resolve URL relativa para absoluta ----------
   Necessário porque o navegador resolve `url(...)` em custom properties
   relativamente ao CSS (que está em /assets/), não ao HTML.             */
function absURL(path) {
  return new URL(path, document.baseURI).href;
}

/* ---------- Parser markdown ---------- */

function normalizeHeadingLevel(text, mdLevel) {
  if (/^[IVX]+\.\s/.test(text)) return 2;
  if (/^\d+[.)]\s/.test(text)) return 3;
  return mdLevel;
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
    }

    const lines = chunk.split("\n").map(l => l.trim()).filter(Boolean);
    if (lines.length && lines.every(l => l.startsWith("- "))) {
      blocks.push({ type: "list", text: lines.join("\n") });
      continue;
    }
    blocks.push({ type: "p", text: lines.join(" ") });
  }
  return blocks;
}

/* ---------- Alinhamento N-ário ---------- */

function zipBlocks(langs) {
  const rank = { h1: 0, h2: 1, h3: 2, list: 3, p: 3 };
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
  return escapeHTML(text)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>");
}

/* ---------- Navegação no topo ---------- */

function renderNav() {
  const nav = document.getElementById("docNav");
  nav.innerHTML = "";

  for (const c of state.manifest.collections) {
    const link = el("a", {
      class: "nav-link",
      href: `#/colecao/${c.id}`,
      "data-id": c.id,
    });
    link.appendChild(el("span", { class: "nav-link-dot" }));
    link.appendChild(document.createTextNode(c.title_pt));
    nav.appendChild(link);
  }
}

function setActiveNav(collectionId) {
  state.activeCollection = collectionId || null;
  document.querySelectorAll("#docNav .nav-link").forEach(a => {
    a.classList.toggle("active", a.dataset.id === collectionId);
  });
}

/* ---------- Renderização: documento ---------- */

function renderCellContent(block, code) {
  const frag = document.createDocumentFragment();
  const raw = (block.cells[code] || "").trim();
  if (!raw) { frag.appendChild(el("p", { text: "—" })); return frag; }

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

  let tag = "p";
  if (block.type === "h1") tag = "h2";
  else if (block.type === "h2") tag = "h3";
  else if (block.type === "h3") tag = "h4";

  const p = el(tag);
  p.innerHTML = inline(raw);
  frag.appendChild(p);
  return frag;
}

function renderBlock(b, langs) {
  const isHeading = b.type === "h1" || b.type === "h2" || b.type === "h3";
  const wrap = el("div", { class: "block" + (isHeading ? " is-heading" : "") });
  for (const l of langs) {
    const cell = el("div", { class: "cell lang-" + l.code });
    cell.appendChild(renderCellContent(b, l.code));
    wrap.appendChild(cell);
  }
  return wrap;
}

function renderDocHeader(meta, collection) {
  const header = el("header", { class: "doc-header" });
  if (collection) {
    header.appendChild(el("a", {
      class: "back-link",
      href: `#/colecao/${collection.id}`,
      text: `← ${collection.title_pt}`
    }));
  }
  header.appendChild(el("p", { class: "doc-eyebrow", text: meta.eyebrow || "Documento" }));
  header.appendChild(el("h1", {}, [
    meta.title_pt,
    el("span", { class: "ru-title", text: meta.title_ru }),
  ]));
  const m = el("div", { class: "doc-meta" });
  [meta.date, meta.archive].filter(Boolean)
    .forEach(t => m.appendChild(el("span", { text: t })));
  if (m.children.length) header.appendChild(m);
  return header;
}

function renderDocument(meta, langs, blocks, collection) {
  const root = document.getElementById("view");
  root.innerHTML = "";

  const article = el("article", { class: "doc" });
  article.appendChild(renderDocHeader(meta, collection));

  const labels = el("div", { class: "col-labels cols-" + langs.length });
  for (const l of langs) {
    labels.appendChild(el("div", { class: "label-" + l.code, text: l.label }));
  }
  article.appendChild(labels);

  const blocksWrap = el("div", { class: "blocks cols-" + langs.length });
  for (const b of blocks) blocksWrap.appendChild(renderBlock(b, langs));
  article.appendChild(blocksWrap);

  root.appendChild(article);
  setActiveNav(collection ? collection.id : null);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function loadDocument(collection, docMeta) {
  const cacheKey = docMeta.id;
  if (state.cache.has(cacheKey)) {
    const { langs, blocks } = state.cache.get(cacheKey);
    renderDocument(docMeta, langs, blocks, collection);
    return;
  }

  const langs = await Promise.all(
    docMeta.languages.map(async l => ({
      code: l.code,
      label: l.label,
      blocks: parseMarkdown(await fetchText(l.file)),
    }))
  );

  const counts = langs.map(l => `${l.code}=${l.blocks.length}`).join(" ");
  console.log(`[${docMeta.id}] blocos ${counts}`);
  if (new Set(langs.map(l => l.blocks.length)).size > 1) {
    console.warn(`[${docMeta.id}] contagens diferentes — alinhamento pode deslocar`);
  }

  const blocks = zipBlocks(langs);
  state.cache.set(cacheKey, { langs, blocks });
  renderDocument(docMeta, langs, blocks, collection);
}

/* ---------- Renderização: coleção ---------- */

function renderCollection(collection) {
  const root = document.getElementById("view");
  root.innerHTML = "";

  const wrap = el("section", { class: "collection" });

  wrap.appendChild(el("a", {
    class: "back-link", href: "#/", text: "← Todas as coleções"
  }));

  const hero = el("header", { class: "collection-hero" });
  hero.style.setProperty("--accent", collection.accent || "#8b2c2c");

  if (collection.cover) {
    hero.classList.add("has-cover");
    hero.style.setProperty("--cover", `url("${absURL(collection.cover)}")`);
  }

  hero.appendChild(el("p", { class: "doc-eyebrow", text: "Coleção" }));
  hero.appendChild(el("h1", {}, [
    collection.title_pt,
    el("span", { class: "ru-title", text: collection.title_ru }),
  ]));
  if (collection.subtitle_pt)
    hero.appendChild(el("p", { class: "collection-subtitle", text: collection.subtitle_pt }));
  if (collection.description_pt)
    hero.appendChild(el("p", { class: "collection-description", text: collection.description_pt }));
  wrap.appendChild(hero);

  const list = el("div", { class: "doc-list" });
  for (const doc of collection.documents) {
    const item = el("a", { class: "doc-list-item", href: `#/doc/${doc.id}` });
    item.appendChild(el("p", { class: "doc-list-eyebrow", text: doc.eyebrow || "" }));
    item.appendChild(el("h2", { class: "doc-list-title", text: doc.title_pt }));
    item.appendChild(el("p", { class: "doc-list-ru", text: doc.title_ru }));
    const meta = el("div", { class: "doc-list-meta" });
    if (doc.date) meta.appendChild(el("span", { text: doc.date }));
    if (doc.archive) meta.appendChild(el("span", { text: doc.archive }));
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
    text: "Edições bilíngues e trilíngues de fontes primárias do período stalinista."
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
      text: c.documents.length === 1 ? "1 documento" : `${c.documents.length} documentos`
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
    if (c.documents.some(d => d.id === docId)) return c;
  }
  return null;
}

function parseRoute() {
  const hash = location.hash.replace(/^#\/?/, "").trim();
  if (!hash) return { view: "home" };
  const parts = hash.split("/");
  if (parts[0] === "colecao" && parts[1]) return { view: "collection", id: parts[1] };
  if (parts[0] === "doc" && parts[1])     return { view: "document",   id: parts[1] };
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
      renderCollection(c);
    } else if (r.view === "document") {
      const c = findCollectionByDocId(r.id);
      if (!c) { location.hash = "#/"; return; }
      const doc = c.documents.find(d => d.id === r.id);
      await loadDocument(c, doc);
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
    state.manifest = await fetchJSON("data/manifest.json");
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