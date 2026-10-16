/* Busca: API local para texto integral; títulos do manifesto na publicação estática. */
let searchCapabilities = null;
let activeSearchRequest = null;
const searchPageSize = 25;

async function searchEnvironment(signal) {
  if (searchCapabilities) return searchCapabilities;
  const response = await fetch(new URL("api/health", document.baseURI), { signal });
  if (response.status === 404) {
    searchCapabilities = { local: false, vocabularies: {} };
    return searchCapabilities;
  }
  if (!response.ok) throw new Error("Não foi possível consultar o serviço de busca. Tente novamente.");
  // Alguns hosts estáticos respondem com a página HTML para caminhos inexistentes.
  if (!(response.headers.get("content-type") || "").includes("application/json")) {
    searchCapabilities = { local: false, vocabularies: {} };
    return searchCapabilities;
  }
  const health = await response.json();
  if (health.status !== "ok" || health.schema_version !== 1) throw new Error("Serviço de busca incompatível.");
  const vocabResponse = await fetch(new URL("api/vocabularies", document.baseURI), { signal });
  if (!vocabResponse.ok) throw new Error("Não foi possível carregar os filtros. Tente novamente.");
  searchCapabilities = { local: true, vocabularies: await vocabResponse.json() };
  return searchCapabilities;
}

function searchURL(params) {
  const query = params.toString();
  return "#/busca" + (query ? "?" + query : "");
}

function searchSelect(name, caption, options, selected) {
  const select = el("select", { name, id: "search-" + name });
  for (const [value, label] of options) select.appendChild(el("option", { value, text: label }));
  select.value = selected || "";
  if (select.selectedIndex < 0) select.selectedIndex = 0;
  return { select, field: el("label", { class: "search-field", for: select.id }, [caption, select]) };
}

function foldedSearchText(value) {
  return (value || "").normalize("NFD").replace(/\p{M}/gu, "").toLocaleLowerCase();
}

function staticSearch(params) {
  const collection = state.manifest.collections.find(c => c.id === params.get("collection"));
  const sub = collection?.subcollections?.find(s => s.id === params.get("subcollection"));
  const documents = collection ? collectionDocuments(collection) : [
    ...new Map(state.manifest.collections.flatMap(c => collectionDocuments(c)).map(d => [d.id, d])).values()
  ];
  const terms = (params.get("q") || "").match(/"[^"]+"|\S+/g) || [];
  const items = documents.filter(doc => {
    if (sub && !sub.document_ids.includes(doc.id)) return false;
    if (params.get("language") && !doc.languages.some(l => l.code === params.get("language"))) return false;
    if (params.get("kind") && (doc.type || "document") !== params.get("kind")) return false;
    const title = foldedSearchText([doc.title_pt, doc.title_ru, doc.title_en].filter(Boolean).join(" "));
    return terms.every(term => title.includes(foldedSearchText(term.replace(/^"|"$/g, ""))));
  }).map(doc => ({ id: doc.id, titles: { pt: doc.title_pt, ru: doc.title_ru, en: doc.title_en },
    kind: doc.type || "document", languages: doc.languages.map(l => l.code), author_label: doc.author,
    historical_date: { display: doc.date }, document_type: null }));
  const sort = params.get("sort") || "title";
  if (sort !== "source") items.sort((a, b) => {
    const title = d => d.titles.pt || d.titles.ru || d.titles.en || d.id;
    return title(a).localeCompare(title(b), "pt") || a.id.localeCompare(b.id);
  });
  const offset = Number(params.get("offset") || 0);
  return { total: items.length, items: items.slice(offset, offset + searchPageSize), offset,
    limit: searchPageSize, has_more: offset + searchPageSize < items.length };
}

function searchResult(doc, params, environment) {
  const collection = state.manifest.collections.find(c => c.id === params.get("collection"));
  const target = new URLSearchParams({ busca: searchURL(params) });
  if (collection) target.set("colecao", collection.id);
  if (params.get("subcollection")) target.set("subcolecao", params.get("subcollection"));
  const language = doc.match?.language || params.get("language");
  if (language) target.set("idioma", language);
  const item = el("a", { class: "doc-list-item search-result", href: `#/doc/${doc.id}?${target}` });
  const title = doc.titles.pt || doc.titles.ru || doc.titles.en || doc.id;
  item.appendChild(el("h2", { class: "doc-list-title", text: title,
    lang: doc.titles.pt ? "pt-BR" : doc.titles.ru ? "ru" : "en" }));
  if (doc.titles.pt && doc.titles.ru) item.appendChild(el("p", { class: "doc-list-ru", lang: "ru", text: doc.titles.ru }));
  const metadata = el("div", { class: "doc-list-meta" });
  const type = environment.vocabularies.document_types?.[doc.document_type];
  metadata.appendChild(el("span", { text: type || (doc.kind === "article" ? "Artigo" : "Documento") }));
  if (doc.author_label) metadata.appendChild(el("span", { text: doc.author_label }));
  if (doc.historical_date?.display) metadata.appendChild(el("span", { text: doc.historical_date.display }));
  metadata.appendChild(el("span", { text: doc.languages.map(code => code.toUpperCase()).join(" · ") }));
  item.appendChild(metadata);
  if (doc.match?.snippet) {
    item.appendChild(el("p", { class: "search-snippet", lang: doc.match.language, text: doc.match.snippet }));
    item.appendChild(el("p", { class: "search-match-language", text: "Correspondência em " +
      (environment.vocabularies.languages?.[doc.match.language] || doc.match.language) }));
  }
  return item;
}

async function renderSearch(rawParams) {
  activeSearchRequest?.abort();
  const controller = new AbortController();
  activeSearchRequest = controller;
  const current = () => !controller.signal.aborted && parseRoute().view === "search";
  stopReadingTracking();
  state.activeDocument = null;
  setActiveNav(null);
  document.querySelector("#docNav .nav-link")?.removeAttribute("aria-current");
  const root = document.getElementById("view");
  const wrap = el("section", { class: "search-page", "aria-labelledby": "search-heading" });
  wrap.appendChild(el("h1", { id: "search-heading", text: "Buscar no acervo" }));
  const message = el("p", { class: "search-status", role: "status", "aria-live": "polite", text: "Preparando a busca…" });
  wrap.appendChild(message);
  root.replaceChildren(wrap);
  window.scrollTo({ top: 0 });
  try {
    const environment = await searchEnvironment(controller.signal);
    if (!current()) return;
    const params = new URLSearchParams();
    for (const key of ["q", "collection", "subcollection", "language", "type", "kind", "scope", "sort", "offset"]) {
      const value = rawParams.get(key);
      if (value) params.set(key, value);
    }
    const offset = Number(params.get("offset") || 0);
    if (!Number.isSafeInteger(offset) || offset < 0) params.delete("offset");
    if (!environment.local) {
      params.delete("type");
      params.set("scope", "title");
      if (params.get("sort") === "relevance") params.set("sort", "title");
    }
    const form = el("form", { class: "search-form", role: "search", "aria-label": "Buscar documentos" });
    const input = el("input", { type: "search", name: "q", id: "search-query", maxlength: "500",
      placeholder: "Palavras ou uma expressão entre aspas", value: params.get("q") || "" });
    form.appendChild(el("label", { class: "search-field", for: input.id }, ["O que você procura?", input]));
    const filters = el("div", { class: "search-filters" });
    const collection = searchSelect("collection", "Coleção", [["", "Todas as coleções"],
      ...state.manifest.collections.map(c => [c.id, c.title_pt])], params.get("collection"));
    const subcollection = searchSelect("subcollection", "Subcoleção", [], "");
    const updateSubcollections = (selected = "") => {
      const parent = state.manifest.collections.find(c => c.id === collection.select.value);
      subcollection.select.replaceChildren(el("option", { value: "", text: "Todas as subcoleções" }));
      for (const sub of parent?.subcollections || []) subcollection.select.appendChild(el("option", { value: sub.id, text: sub.title_pt }));
      subcollection.select.value = selected;
      if (subcollection.select.selectedIndex < 0) subcollection.select.selectedIndex = 0;
      subcollection.select.disabled = !parent?.subcollections?.length;
    };
    updateSubcollections(params.get("subcollection"));
    collection.select.addEventListener("change", () => {
      updateSubcollections();
      sourceOption.disabled = !collection.select.value;
      if (sort.select.value === "source" && sourceOption.disabled) sort.select.value = "title";
    });
    const language = searchSelect("language", "Idioma", [["", "Todos os idiomas"], ["ru", "Russo"], ["pt", "Português"], ["en", "Inglês"]], params.get("language"));
    const kind = searchSelect("kind", "Categoria", [["", "Documentos e artigos"], ["document", "Documento"], ["article", "Artigo"]], params.get("kind"));
    const type = searchSelect("type", "Tipo documental", [["", "Todos os tipos"],
      ...Object.entries(environment.vocabularies.document_types || {}).sort((a, b) => a[1].localeCompare(b[1], "pt")),
      ["unspecified", "Sem classificação específica"]], params.get("type"));
    type.select.disabled = !environment.local;
    const scope = searchSelect("scope", "Pesquisar em", environment.local
      ? [["all", "Títulos e texto completo"], ["title", "Somente títulos"]] : [["title", "Somente títulos"]], params.get("scope") || "all");
    const sort = searchSelect("sort", "Ordenar por", [
      ...(environment.local ? [["relevance", "Relevância"]] : []), ["title", "Título"], ["source", "Ordem na coleção"]
    ], params.get("sort") || (environment.local && params.get("q") ? "relevance" : "title"));
    const sourceOption = sort.select.querySelector('option[value="source"]');
    sourceOption.disabled = !collection.select.value;
    if (sort.select.value === "source" && sourceOption.disabled) sort.select.value = "title";
    for (const field of [collection, subcollection, language, kind, type, scope, sort]) filters.appendChild(field.field);
    form.appendChild(filters);
    form.appendChild(el("p", { class: "search-help", text: environment.local
      ? "Digite termos no idioma do documento. Use aspas para uma expressão exata; todas as palavras são exigidas. A busca não traduz termos nem reúne automaticamente flexões russas. Deixe o campo vazio para explorar pelos filtros."
      : "Nesta versão, a busca consulta os títulos disponíveis. Texto completo e tipos documentais estão disponíveis ao iniciar o backend local com python3 -m backend." }));
    const actions = el("div", { class: "search-actions" }, [el("button", { type: "submit", class: "search-submit", text: "Buscar" }),
      el("a", { href: "#/busca", text: "Limpar filtros" })]);
    form.appendChild(actions);
    form.addEventListener("submit", event => {
      event.preventDefault();
      const next = new URLSearchParams();
      for (const [key, value] of new FormData(form)) if (String(value).trim()) next.set(key, String(value).trim());
      const hash = searchURL(next);
      if (location.hash === hash) renderSearch(next);
      else location.hash = hash;
    });
    wrap.insertBefore(form, message);
    // Usa os valores efetivos dos controles, inclusive ao receber uma URL antiga ou inválida.
    const effective = new URLSearchParams();
    for (const [key, value] of new FormData(form)) if (String(value).trim()) effective.set(key, String(value).trim());
    if (params.has("offset")) effective.set("offset", params.get("offset"));
    message.textContent = "Buscando documentos…";
    message.setAttribute("aria-busy", "true");
    let data;
    if (environment.local) {
      const apiParams = new URLSearchParams(effective);
      apiParams.set("limit", String(searchPageSize));
      const response = await fetch(new URL("api/documents?" + apiParams, document.baseURI), { signal: controller.signal });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || "Não foi possível concluir a busca.");
      data = body;
    } else data = staticSearch(effective);
    if (!current()) return;
    message.removeAttribute("aria-busy");
    message.textContent = data.total
      ? `${data.total} ${data.total === 1 ? "documento encontrado" : "documentos encontrados"} · ${data.offset + 1}–${Math.min(data.offset + data.limit, data.total)}`
      : "Nenhum documento encontrado. Tente menos palavras ou amplie os filtros.";
    if (data.total && !data.items.length) message.textContent = "Esta página não tem resultados. Volte para a primeira página.";
    const list = el("div", { class: "doc-list search-results" });
    for (const doc of data.items) list.appendChild(searchResult(doc, effective, environment));
    wrap.appendChild(list);
    const pagination = el("nav", { class: "search-pagination", "aria-label": "Páginas de resultados" });
    const pageLink = (label, offset) => {
      const next = new URLSearchParams(effective);
      if (offset) next.set("offset", String(offset)); else next.delete("offset");
      return el("a", { href: searchURL(next), text: label });
    };
    if (data.offset > 0) {
      pagination.appendChild(pageLink("Primeira página", 0));
      pagination.appendChild(pageLink("← Anterior", Math.max(0, data.offset - searchPageSize)));
    }
    if (data.has_more) pagination.appendChild(pageLink("Próxima →", data.offset + searchPageSize));
    wrap.appendChild(pagination);
  } catch (error) {
    if (!current() || error.name === "AbortError") return;
    message.removeAttribute("aria-busy");
    message.textContent = error.message;
    const retry = el("button", { type: "button", class: "search-submit", text: "Tentar novamente" });
    retry.addEventListener("click", () => { searchCapabilities = null; renderSearch(rawParams); });
    wrap.appendChild(retry);
  }
}
