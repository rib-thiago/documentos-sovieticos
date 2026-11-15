export const ROOT = new URL('../../', import.meta.url);
export const asset = path => new URL(String(path).replace(/^\//, ''), ROOT).href;
export const LANGUAGES = { pt: 'Português', ru: 'Русский', en: 'English' };
export const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
export const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export const label = d => d?.title_pt || d?.title_ru || d?.title_en || d?.title || d?.id || 'Documento';
export const shortLabel = d => d?.shortTitle || label(d);
export function dateLabel(d) {
    const date = d.historical_date?.display || (typeof d.historical_date === 'string' ? d.historical_date : '') || d.date || '';
    const match = String(date).match(/^(\d{4})-(\d{2})-(\d{2})$/);
    return match ? `${match[3]}.${match[2]}.${match[1]}` : date;
}
export function node(tag, attrs = {}, children = []) {
    const element = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
        if (key === 'text')
            element.textContent = value;
        else if (key === 'class')
            element.className = value;
        else if (key.startsWith('on') && typeof value === 'function')
            element.addEventListener(key.slice(2), value);
        else if (value !== undefined && value !== null && value !== false)
            element.setAttribute(key, value === true ? '' : value);
    }
    element.append(...children.filter(Boolean));
    return element;
}
export const action = (text, run, className = '', attrs = {}) => node('button', { type: 'button', text, class: className, onclick: run, ...attrs });
export function download(filename, content, type = 'text/markdown;charset=utf-8') {
    const url = URL.createObjectURL(new Blob([content], { type }));
    const a = node('a', { href: url, download: filename });
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export async function loadCatalog() {
    const response = await fetch(asset('data/manifest.json'),{cache:'no-store'});
    if (!response.ok)
        throw Error('Não foi possível abrir o catálogo. Use um servidor HTTP na raiz do projeto.');
    const manifest = await response.json();
    const documents = new Map((manifest.documents || []).map(d => [d.id, d]));
    for (const collection of manifest.collections || []) {
        for (const doc of collection.documents || [])
            if (!documents.has(doc.id))
                documents.set(doc.id, doc);
        for (const sub of collection.subcollections || [])
            for (const doc of sub.documents || [])
                if (!documents.has(doc.id))
                    documents.set(doc.id, doc);
    }
    const collectionDocuments = c => {
        const ids = c.document_ids || (c.documents || []).map(d => d.id);
        return [...new Set(ids)].map(id => documents.get(id)).filter(Boolean);
    };
    let links = [];
    try {
        const res = await fetch(asset('data/facsimiles.json'),{cache:'no-store'});
        if (res.ok)
            links = (await res.json()).links.filter(l => l.active !== false);
    }
    catch { }
    return { manifest, documents, all: [...documents.values()], collections: manifest.collections || [], collectionDocuments, links };
}
const textCache = new Map();
export async function editionText(doc, lang) {
    const edition = doc.languages?.find(e => e.code === lang);
    if (!edition)
        throw Error('Esta versão ainda não está disponível.');
    if (!textCache.has(edition.file))
        textCache.set(edition.file, fetch(asset(edition.file)).then(r => { if (!r.ok)
            throw Error('Não foi possível carregar a versão.'); return r.text(); }).catch(error => { textCache.delete(edition.file); throw error; }));
    const source = await textCache.get(edition.file);
    return { source, body: window.splitExportHeaders ? window.splitExportHeaders(source).body : source, edition };
}
let markdown;
export function renderMarkdown(text, format = 'markdown', withSources=false) {
    if (format === 'text')
        return text.split(/\n\s*\n/).map(p => `<p>${escape(p).replace(/\n/g, '<br>')}</p>`).join('');
    if (!window.markdownit || !window.DOMPurify)
        throw Error('Os componentes locais de leitura não carregaram.');
    if (!markdown) {
        markdown = window.markdownit({ html: false, linkify: true, breaks: false });
        if (window.markdownitFootnote)
            markdown.use(window.markdownitFootnote);
    }
    if(!withSources)return window.DOMPurify.sanitize(markdown.render(text));
    const env={},tokens=markdown.parse(text,env),ranges=markdownSourceRanges(text,tokens);
    for(const {token,start,end}of ranges){token.attrSet('data-source-start',String(start));token.attrSet('data-source-end',String(end));}
    return window.DOMPurify.sanitize(markdown.renderer.render(tokens,markdown.options,env));
}
export function fingerprint(value) {
    let hash = 2166136261;
    for (let i = 0; i < value.length; i++) {
        hash ^= value.charCodeAt(i);
        hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(16);
}
export function parseImportFile(name, text) {
    const filename = name.replace(/\.(md|markdown|txt)$/i, '');
    const match = filename.match(/^(.*?)[._-](ru|pt|en)$/i);
    const envelope = window.splitExportHeaders?.(text);
    const header = envelope?.headers?.join('\n') || '';
    const id = header.match(/^(?:ID\s+(?:do\s+)?documento|Document\s+ID|ID\s+ShowTrials|ShowTrials\s+ID)\s*:\s*(.+)$/im)?.[1]?.trim();
    const lang = header.match(/^(?:Idioma|Language)\s*:\s*(ru|pt|en)\b/im)?.[1]?.toLowerCase();
    const body = envelope?.body ?? text;
    return { filename: name, id: id ? (/^\d+$/.test(id) ? 'showtrials-' + id : id) : match?.[1] || filename, lang: lang || match?.[2]?.toLowerCase() || '', body, original: text, title: body.match(/^#\s+(.+)$/m)?.[1] || (match?.[1] || filename).replace(/[-_]/g, ' '), identification: header ? 'Identificação do cabeçalho' : match ? 'Identificação pelo nome' : 'Idioma a confirmar' };
}
export function pageNumbers(value, max) {
    const result = [];
    for (const token of String(value).split(/[,;\s]+/).filter(Boolean)) {
        const match = token.match(/^(\d+)(?:-(\d+))?$/);
        if (!match)
            throw Error('Use páginas como 1-3, 5, 8.');
        const first = Number(match[1]), last = Number(match[2] || first);
        if (first < 1 || last < first || last > max)
            throw Error(`Escolha páginas entre 1 e ${max}.`);
        for (let n = first; n <= last; n++)
            if (!result.includes(n))
                result.push(n);
    }
    if (!result.length)
        throw Error('Selecione pelo menos uma página.');
    return result;
}

// A preferência do documento vale tanto para paralelo quanto para expansão por trecho.
export function comparisonLanguage(material) {
    const options=(material.doc.languages||[]).filter(l=>l.code!==material.lang);
    return options.some(l=>l.code===material.otherLang)?material.otherLang:options[0]?.code;
}

export function passageCitation(doc,passage,portalURL) {
    const parts=[label(doc),dateLabel(doc),`Idioma: ${LANGUAGES[passage.lang]||passage.lang}`];
    if(passage.project)parts.push('Versão privada do projeto '+passage.project.title+' — não publicada');
    else if(passage.draft)parts.push('Rascunho da sessão — versão não publicada');
    parts.push(`Bloco ${passage.unit} — numeração provisória do piloto`);
    if(doc.archive)parts.push(typeof doc.archive==='string'?doc.archive:JSON.stringify(doc.archive));
    if(doc.source_url)parts.push(`Fonte: ${doc.source_url}`);
    if(portalURL)parts.push(`${passage.project?'Referência do documento no acervo, não desta versão privada':'Documento'}: ${portalURL}`);
    return `“${passage.quote}”\n\n${parts.filter(Boolean).join(' · ')}`;
}

// Offsets usam UTF-16, como Range e os nós de texto do navegador.
export function makeTextAnchor(text, start, end, lang, unit, draft=false) {
    const raw=text.slice(start,end),leading=raw.length-raw.trimStart().length;
    const quote=raw.trim();start+=leading;end=start+quote.length;
    return {lang,unit,quote,start,end,prefix:text.slice(Math.max(0,start-48),start),suffix:text.slice(end,end+48),signature:fingerprint(text),draft};
}
export function resolveTextQuote(text, anchor) {
    const quote=anchor.quote;if(!quote)return {status:'missing'};
    const exactBlock=fingerprint(text)===anchor.signature;
    const at=anchor.start;
    if(exactBlock&&Number.isInteger(at)&&text.slice(at,at+quote.length)===quote)
        return {status:'found',start:at,end:at+quote.length,exactBlock,context:true};
    const matches=[];let index=0;
    while((index=text.indexOf(quote,index))!==-1){
        const end=index+quote.length;
        const context=Boolean(anchor.prefix||anchor.suffix)&&
          (!anchor.prefix||text.slice(Math.max(0,index-anchor.prefix.length),index)===anchor.prefix)&&
          (!anchor.suffix||text.slice(end,end+anchor.suffix.length)===anchor.suffix);
        matches.push({status:'found',start:index,end,exactBlock,context});index++;
    }
    const contextual=matches.filter(m=>m.context);
    if(contextual.length===1)return contextual[0];
    if(matches.length===1)return matches[0];
    return {status:matches.length?'ambiguous':'missing'};
}

export function literalMatches(text,query,{caseSensitive=false,limit=500}={}) {
    if(!query||limit<1)return [];
    const escaped=query.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    const pattern=new RegExp(escaped,caseSensitive?'gu':'giu'),matches=[];
    let match;
    while((match=pattern.exec(text))&&matches.length<limit)matches.push({start:match.index,end:match.index+match[0].length});
    return matches;
}

export function clearEditionCache(){textCache.clear();}

// A consulta local usa o PDF integral; a projeção estática conserva seu mapa de seleção.
export function mergeDocumentLinks(current,local){
 const known=new Set(local.map(link=>link.id)),active=local.filter(link=>link.active),ids=new Set(active.map(link=>link.id)),publicById=new Map(current.filter(link=>!link.local).map(link=>[link.id,link]));
 return [...current.filter(link=>!ids.has(link.id)&&!(link.local&&known.has(link.id))),...active.map(link=>({...link,local:true,portalPrepared:publicById.has(link.id),pdf_url:'api/editorial/pdf/'+encodeURIComponent(link.source_id)+'/file',source_scope_note:'Fonte de trabalho vinculada localmente ao documento. Páginas físicas: '+link.pages.join(', ')+'. '+(link.notes||'')+' A associação de páginas não certifica alinhamento exato por parágrafo.'}))];
}

export function markdownSourceRanges(text,tokens){
 const offsets=[0];for(const match of text.matchAll(/\r\n|\r|\n/g))offsets.push(match.index+match[0].length);
 return tokens.filter(t=>t.level===0&&t.nesting===1&&t.map).map(token=>{const start=offsets[token.map[0]]??text.length;let end=offsets[token.map[1]]??text.length;while(end>start&&/[\r\n]/.test(text[end-1]))end--;return {token,start,end};}).filter(r=>r.end>r.start);
}
