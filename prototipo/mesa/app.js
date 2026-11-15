import {associatePassage,documentAssociations,alignPage,printDocument,bodyDigest,associatedTextRange,editAssociation} from './parity.js';
import {mountHomeActivity} from './library-home.js';
import {mountLibraryTools} from './library-tools.js';
import {beginPassageEdit,mountPassageEditor} from './passage-edit.js';
import {mountProjects,projectMaterials,projectDocumentKey,saveWorkspace,workspaceHistory,promoteWorkspace,importWorkspaceTranslation} from './projects.js';
import {mountReview} from './review.js';
import {mountCorpus} from './corpus.js';
import {menuGroup,menuSearch,installSplitter,zoomControls} from './controls.js';
import {sourcesView,sourceView,sourceFile} from './pdf-workflow.js';
import {mountCatalog,mountCollections} from './organization.js';
import {editorialRequest,detectEditorial,markdownPayload,uploadPdfSource} from './editorial.js';
import {snapshotDesk,restoreDesk,pendingCount} from './session.js';
import { asset, LANGUAGES, normalize, label, dateLabel, node as n, action as b, loadCatalog, editionText, renderMarkdown, download, fingerprint, comparisonLanguage, passageCitation, makeTextAnchor, resolveTextQuote, literalMatches, clearEditionCache,mergeDocumentLinks } from './data.js';
import { mountPdf, pageText, openPdf } from './pdf.js';
const $ = s => document.querySelector(s), content = $('#content'), controls = $('#task-controls');
const libraryState={q:'',collection:'',sub:'',scope:'catalog',language:'',offset:0,view:'home'};
let backendAvailable=false;
let activeMarkdownEditor=null;
let projectContext=null;
let panelTrail=[];
let catalog, materials = [], active, cleanup = () => { }, generation = 0, pinned = false, panelName = '', preview = null;
const KEY = 'biblioteca-mesa-piloto-v1';
let saved;
try {
    saved = JSON.parse(sessionStorage.getItem(KEY) || '{}');
}
catch {
    saved = {};
}
saved.scope = 'acervo';
saved.drafts ||= {};
saved.markers ||= {};
saved.history ||= [];
saved.metadata ||= {};
saved.notes ||= {};
saved.pages ||= {};
saved.catalogWork ||= {};saved.noteWork||={};saved.noteTrash||=[];saved.organizationWork||={};
let sessionTimer, storageFailed=false;
function queueSession(){clearTimeout(sessionTimer);sessionTimer=setTimeout(()=>{remember();persist();tabs();},600);}
function persist() { try {
    if(catalog)saved.workspace=snapshotDesk(materials,active,libraryState);
    sessionStorage.setItem(KEY, JSON.stringify(saved));storageFailed=false;
}
catch {
    storageFailed=true;toast('A sessão está cheia. Exporte seus rascunhos antes de continuar.');
} }
function toast(text) { $('#toast').textContent = storageFailed?text+' · Armazenamento cheio: exporte o trabalho; a última alteração está apenas na memória.':text; $('#toast').hidden = false; clearTimeout(toast.timer); toast.timer = setTimeout(() => $('#toast').hidden = true, 4500); }
const current = () => materials.find(m => m.key === active);
const button = (text, run, extra = '') => b(text, run, 'control ' + extra);
function select(values, value, change, title) { const el = n('select', { 'aria-label': title, class: 'control' }); for (const [v, t] of values)
    el.append(n('option', { value: v, text: t })); el.value = value; el.onchange = () => change(el.value); return el; }
function field(title, value = '', type = 'text') { const input = n('input', { value, type }); return { input, element: n('label', { class: 'field' }, [n('span', { text: title }), input]) }; }
function closePanel() { panelTrail=[];clearFindHighlights(); $('#open-tools').setAttribute('aria-expanded','false');panelName = ''; $('#auxiliary').hidden = true; $('#panel-backdrop').hidden = true; document.body.classList.remove('panel-pinned'); }
function togglePanel(title) { if (!$('#auxiliary').hidden && panelName === title) { closePanel(); return true; } return false; }
function panel(title,children,restoring=false){
 clearFindHighlights();hidePassageActions();const host=$('#auxiliary'),body=host.querySelector('.panel-body');
 if(!restoring&&!host.hidden&&panelName!==title&&body){panelTrail.push({title:panelName,children:[...body.childNodes],scroll:body.scrollTop});panelTrail=panelTrail.slice(-8);}
 $('#open-tools').setAttribute('aria-expanded','true');panelName=title;
 const back=panelTrail.length?b('‹ Voltar',()=>{const previous=panelTrail.pop();panel(previous.title,previous.children,true);host.querySelector('.panel-body').scrollTop=previous.scroll;},'panel-back'):null;
 host.replaceChildren(n('div',{class:'panel-heading'},[back,n('h2',{text:title,title}),b(pinned?'Soltar':'Fixar',event=>{pinned=!pinned;event.currentTarget.textContent=pinned?'Soltar':'Fixar';document.body.classList.toggle('panel-pinned',pinned);$('#panel-backdrop').hidden=pinned;},'control small'),b('×',closePanel,'icon-button',{'aria-label':'Fechar painel'})]),n('div',{class:'panel-body'},children));host.hidden=false;$('#panel-backdrop').hidden=pinned;document.body.classList.toggle('panel-pinned',pinned);
}
function dialog(title, children) { hidePassageActions(); const d = $('#dialog'); d.replaceChildren(n('div', { class: 'panel-heading' }, [n('h2', { text: title }), b('×', () => d.close(), 'icon-button', { 'aria-label': 'Fechar' })]), n('div', { class: 'dialog-body' }, children)); d.showModal(); }
function remember() { const m = current(); if (!m)
    return; const scroll = content.dataset.material===m.key?content.querySelector('.document-scroll'):null; if (scroll) {
    m.scroll = scroll.scrollTop;
    const block = [...scroll.querySelectorAll('[data-unit]')].find(e => e.getBoundingClientRect().bottom > scroll.getBoundingClientRect().top + 20);
    if (block)
        m.position = { unit: block.dataset.unit, offset: block.getBoundingClientRect().top - scroll.getBoundingClientRect().top };
} if(content.dataset.material===m.key)m.capture?.(); }
function navigate(hash) { remember(); if (location.hash === '#' + hash)
    render();
else
    location.hash = hash; }
function openDocument(doc,project=null) { remember();projectContext=project;const key=projectDocumentKey(doc.id,project?.id);let m = materials.find(x => x.key === key); if (!m) {
    m = { key, kind: 'document', doc,projectId:project?.id,project, lang: doc.languages?.some(x => x.code === 'pt') ? 'pt' : doc.languages?.[0]?.code, mode: 'read', scroll: 0 };
    materials.push(m);
}if(project){m.project=project;}else m.doc=doc;active = m.key;updateScope(); closePanel(); if (location.hash === '#mesa')
    render();
else
    location.hash = 'mesa'; }
function activateMaterial(key){
 if(!materials.some(item=>item.key===key))return;
 remember();preview=null;active=key;projectContext=current()?.project||null;updateScope();closePanel();navigate('mesa');
}
function closeMaterial(material){
 remember();
 if(pendingCount(material)&&!confirm('Fechar esta aba e descartar alterações ainda não confirmadas? As versões já salvas na sessão ou no backend serão preservadas.'))return;
 const index=materials.indexOf(material);preview=null;materials=materials.filter(item=>item!==material);
 material.pdf?.destroy();material.facsimile?.pdf?.destroy();if(active===material.key)active=materials[Math.min(index,materials.length-1)]?.key;
 render();
}
function tabs(){
 const host=$('#materials-tabs'),count=materials.length;host.replaceChildren();const visible=count>0&&location.hash==='#mesa';host.hidden=!visible;
 document.documentElement.style.setProperty('--tabs',visible?'28px':'0px');
 $('#tab-count').textContent='';const mesa=document.querySelector('[data-nav="desk"]');mesa.title=`Uma Mesa de pesquisa · ${count} materiais abertos`;mesa.setAttribute('aria-label',mesa.title);
 if(!visible)return;
 const strip=n('div',{class:'material-tab-strip',role:'tablist','aria-label':'Materiais da mesma Mesa'});
 for(const material of materials){
  const title=material.kind==='pdf'?'PDF · '+material.title:label(material.doc)+(material.projectId?' · Projeto: '+(material.project?.title||material.projectTitle||'local'):''),selected=material.key===active;
  const tab=b(title,()=>activateMaterial(material.key),'material-tab-open',{title,role:'tab','aria-selected':String(selected),'aria-label':title+(selected?' · ativo':''),'aria-controls':'content'});
  strip.append(n('div',{class:'material-tab'+(selected?' active':'')},[
    tab,pendingCount(material)&&n('span',{class:'tab-dirty',title:'Alterações ainda não confirmadas','aria-label':'Alterações ainda não confirmadas'}),
    b('×',()=>closeMaterial(material),'tab-close',{'aria-label':'Fechar aba: '+title,title:'Fechar esta aba'})
  ]));
 }
 const picker=n('select',{class:'open-material-picker','aria-label':'Alternar entre documentos e fontes da mesma Mesa'});
 picker.append(n('option',{value:'',text:`Abas abertas (${count})`,disabled:true,selected:true}));
 for(const material of materials)picker.append(n('option',{value:material.key,text:(material.key===active?'● ':'')+(material.kind==='pdf'?'PDF · '+material.title:material.doc.id+' · '+label(material.doc)+(material.projectId?' · Projeto':' · Acervo'))}));
 picker.onchange=()=>activateMaterial(picker.value);host.append(strip,picker);
 requestAnimationFrame(()=>{const selected=strip.querySelector('.material-tab.active');if(!selected)return;const left=selected.offsetLeft-strip.offsetLeft;if(left<strip.scrollLeft||left+selected.offsetWidth>strip.scrollLeft+strip.clientWidth)strip.scrollLeft=Math.max(0,left-strip.clientWidth/2+selected.offsetWidth/2);});
}
function heading(kicker, title, text) { return n('div', { class: 'page-heading' }, [n('div', {}, [n('p', { class: 'eyebrow', text: kicker }), n('h1', { text: title }), text && n('p', { class: 'lede', text })])]); }
function documentList(docs, host, page = 0) { host.replaceChildren(); const size = 20; for (const doc of docs.slice(page * size, (page + 1) * size))
    host.append(n('div', { class: 'document-item' }, [n('div', {}, [b(label(doc), () => openDocument(doc), 'doc-title'), n('span', { class: 'doc-date', text: dateLabel(doc) }), n('p', { class: 'doc-details', text: [doc.source_name, (doc.languages || []).map(l => LANGUAGES[l.code] || l.code).join(' · ')].filter(Boolean).join(' / ') })]), button('Abrir →', () => openDocument(doc), 'quiet')])); if (!docs.length)
    host.append(n('p', { text: 'Nenhum documento encontrado.' })); if (docs.length > size)
    host.append(n('div', { class: 'pagination' }, [button('← Anterior', () => documentList(docs, host, page - 1), 'quiet'), n('span', { text: `${page + 1} / ${Math.ceil(docs.length / size)} · ${docs.length} documentos` }), button('Próxima →', () => documentList(docs, host, page + 1), 'quiet')])); const buttons = host.querySelectorAll('.pagination button'); if (buttons.length) {
    buttons[0].disabled = page === 0;
    buttons[1].disabled = (page + 1) * size >= docs.length;
} }
function library(){
 const version=generation,shell=n('section',{class:'page-shell library-portal'}),results=n('div',{class:'library-results'}),cards=n('div',{class:'portal-cover-gallery'}),activity=n('section',{class:'portal-activity'});
 const query=n('input',{type:'search',maxlength:500,placeholder:'Título, ID, nome ou frase…','aria-label':'Pesquisar no acervo'});
 const collection=select([['','Todas as coleções'],...catalog.collections.map(c=>[c.id,label(c)])],libraryState.collection||'',()=>{updateSubs();searchTools?.search();},'Coleção'),sub=select([['','Todas as subcoleções']],libraryState.sub||'',()=>{},'Subcoleção');
 const scope=select([['catalog','Catálogo'],['text','Conteúdo dos documentos']],backendAvailable&&libraryState.scope==='text'?'text':'catalog',()=>{},'Onde pesquisar');scope.querySelector('option[value="text"]').disabled=!backendAvailable;
 const language=select([['','Todos os idiomas'],...Object.entries(LANGUAGES)],libraryState.language||'',()=>{},'Idioma');
 const field=(caption,input)=>n('label',{class:'library-search-field'},[n('span',{text:caption}),input]),subField=field('Subcoleção',sub);
 function updateSubs(){sub.replaceChildren(n('option',{value:'',text:'Todas as subcoleções'}));const root=catalog.collections.find(c=>c.id===collection.value);for(const child of root?.subcollections||[])sub.append(n('option',{value:child.id,text:label(child)}));subField.hidden=!root?.subcollections?.length;}
 updateSubs();sub.value=libraryState.sub||'';query.value=libraryState.q;
 let searchTools,lastIdentity='',lastDivision='',lastMode='';
 function goHome(){libraryState.view='home';query.value='';collection.value='';sub.value='';language.value='';updateSubs();searchTools.search();}
 function openSearch(){libraryState.view='search';searchTools.search({reset:false});requestAnimationFrame(()=>query.focus({preventScroll:true}));}
 function explore(id){libraryState.view='collection';query.value='';language.value='';collection.value=id;updateSubs();searchTools.search();content.scrollTop=0;window.scrollTo({top:0,behavior:'smooth'});}
 function openActivity(doc,lang){openDocument(doc);const material=current();if(lang&&doc.languages?.some(l=>l.code===lang))material.lang=lang;material.mode='read';material.showCanonical=true;persist();}
 function aboutProject(){dialog('Sobre o projeto',[
  n('p',{text:'Documentos Soviéticos é a interface pública do ShowTrials: um projeto de pesquisa histórica, preservação, organização e edição digital crítica de fontes sobre a história política da União Soviética.'}),
  n('p',{text:'O acervo concentra-se nas lutas internas do Partido Comunista, nas oposições, nas investigações e nos processos político-judiciais, especialmente nos anos 1930.'}),
  n('p',{text:'Consulte a origem e a referência de cada documento, compare original e tradução e examine as alegações das fontes em seu contexto. Traduções de trabalho podem receber novas revisões; a apresentação de uma acusação documental não a transforma em fato histórico estabelecido.'})
 ]);}
 const searchButton=button('Buscar',openSearch,'quiet');controls.append(searchButton);
 if(backendAvailable)controls.append(button('Organizar acervo',()=>{if(togglePanel('Organizar acervo'))return;panel('Organizar acervo',[
  menuGroup('Catálogo e revisão',[
   {title:'Catálogo',description:'Editar fichas de documentos com prévia.',run:()=>navigate('catalogo')},
   {title:'Coleções e subcoleções',description:'Criar e organizar os conjuntos do acervo.',run:()=>navigate('colecoes')},
   {title:'Importar corpus',description:'Cadastrar originais e traduções associados.',run:()=>navigate('importar')},
   {title:'Fila de revisão',description:'Prioridades, motivos e registro de avaliações.',run:()=>navigate('fila')}
  ]),menuGroup('Fontes e pesquisa',[
   {title:'Fontes PDF e OCR',description:'Preparação, transcrição e fac-símiles.',run:()=>navigate('fontes')},
   {title:'Projetos locais',description:'Organizar materiais e versões privadas.',run:()=>navigate('projetos')}
  ])
 ]);},'quiet'));
 const back=button('← Todas as coleções',goHome,'quiet portal-back'),identity=n('header',{class:'portal-opening'});
 const reset=button('Limpar filtros',()=>{query.value='';collection.value='';sub.value='';language.value='';updateSubs();searchTools.search();},'quiet');
 const searchHelp=n('p',{class:'library-search-help',text:backendAvailable?'Catálogo: títulos, IDs e referências. Conteúdo: palavras ou frases entre aspas, no idioma escolhido. Versões privadas ficam fora da busca.':'Busca no catálogo público. A pesquisa integral nos documentos exige o backend local.'});
 const searchPanel=n('section',{class:'library-search-panel portal-search-panel',hidden:true,'aria-label':'Busca e filtros do acervo'},[
  n('div',{class:'library-search-primary'},[field('Pesquisar em',scope),n('label',{class:'library-query-field'},[n('span',{class:'sr-only',text:'Termo da busca'}),query]),button('Pesquisar',()=>searchTools.search(),'primary')]),
  n('div',{class:'library-search-secondary'},[field('Coleção',collection),subField,field('Idioma',language),reset]),searchHelp
 ]);
 const heading=n('h2'),note=n('p',{class:'hint'}),summary=n('p',{class:'library-result-summary',role:'status'}),zipHost=n('div',{class:'library-zip-control',hidden:true}),divisions=n('nav',{class:'portal-subcollections',hidden:true,'aria-label':'Subcoleções'}),emptySearch=n('p',{class:'portal-search-empty',hidden:true,text:'Digite uma palavra, frase ou identificação para começar. Os filtros podem limitar o idioma e o conjunto documental.'});
 const descriptionText=n('p'),description=n('details',{class:'library-collection-description',hidden:true},[n('summary',{text:'Sobre este conjunto'}),descriptionText]);
 const catalogSection=n('section',{class:'portal-catalog'},[n('header',{class:'library-context-heading'},[n('div',{},[heading,note]),zipHost]),divisions,description,summary,emptySearch,results,cards]);
 for(const root of catalog.collections){
  const cover=n('div',{class:'portal-book-cover'}),image=root.cover?n('img',{src:asset(root.cover),alt:'',loading:'lazy'}):null;
  const placeholder=()=>n('div',{class:'portal-book-placeholder','aria-hidden':'true'},[n('span',{text:'Documentos Soviéticos'}),n('strong',{text:label(root)}),n('span',{text:'Coleção documental'})]);
  cover.append(image||placeholder());if(image)image.onerror=()=>cover.replaceChildren(placeholder());
  const languages=[...new Set(catalog.collectionDocuments(root).flatMap(doc=>(doc.languages||[]).map(l=>l.code)))];
  cards.append(n('button',{type:'button',class:'portal-book',onclick:()=>explore(root.id)},[cover,n('div',{class:'portal-book-caption'},[n('h3',{text:label(root)}),n('p',{text:root.subtitle_pt||root.description_pt||'Fontes, originais e traduções'}),n('span',{text:languages.map(code=>code.toUpperCase()).join(' · ')})])]));
 }
 const editions=catalog.all.reduce((sum,doc)=>sum+(doc.languages?.length||0),0),stats=n('div',{class:'portal-acervo-totals'},[
  [catalog.all.length,'documentos'],[editions,'versões em idiomas'],[catalog.collections.length,'coleções'],[new Set(catalog.links.filter(l=>!l.local).map(l=>l.document_id)).size,'textos com fac-símiles']
 ].map(([count,text])=>n('div',{},[n('strong',{text:count.toLocaleString('pt-BR')}),n('span',{text})])));
 const footer=n('footer',{class:'portal-footer'},[n('div',{class:'portal-footer-introduction'},[n('div',{},[n('p',{class:'eyebrow',text:'Pesquisa · Preservação · Edição crítica'}),n('h2',{text:'Ler as fontes. Conhecer sua origem.'}),n('p',{text:'Fontes históricas soviéticas acessíveis por suas coleções, traduções e proveniência. Na Mesa, documentos podem ser lidos, comparados e anotados no mesmo espaço de pesquisa.'})]),n('div',{class:'portal-footer-actions'},[button('Projeto e critérios editoriais',aboutProject,'quiet'),button(materials.length?'Retomar a Mesa · '+materials.length+' materiais':'Abrir a Mesa de pesquisa',()=>navigate('mesa'),'quiet')])]),stats]);
 shell.append(back,identity,searchPanel,catalogSection,activity,footer);
 searchTools=mountLibraryTools({catalog,state:libraryState,backend:backendAvailable,button,store:queueSession,current:()=>generation===version,
  onContext:({active,root,child})=>{
   const mode=libraryState.view==='search'?'search':root?'collection':active?'search':'home';libraryState.view=mode;shell.dataset.view=mode;
   back.hidden=mode==='home';searchPanel.hidden=mode!=='search';cards.hidden=mode!=='home';activity.hidden=mode!=='home';emptySearch.hidden=mode!=='search'||active;reset.disabled=!active;
   searchButton.classList.toggle('active',mode==='search');searchButton.setAttribute('aria-pressed',String(mode==='search'));
   if(mode==='home'&&lastMode!=='home'){if(typeof keyboardTarget!=='undefined'&&searchPanel.contains(keyboardTarget))keyboardTarget=null;setGlobalKeyboard(false);}lastMode=mode;
   const key=mode+'/'+(root?.id||'');if(lastIdentity!==key){
    identity.replaceChildren();
    if(mode==='home')identity.append(n('p',{class:'eyebrow',text:'Biblioteca de fontes históricas'}),n('h1',{},['Documentos ',n('em',{text:'Soviéticos'})]),n('p',{class:'portal-opening-mission',text:'História política da União Soviética, apresentada por suas fontes, coleções e traduções.'}));
    else if(mode==='search')identity.append(n('p',{class:'eyebrow',text:'Pesquisa transversal'}),n('h1',{text:'Buscar no acervo'}));
    else{const cover=n('div',{class:'portal-collection-cover'},[root.cover?n('img',{src:asset(root.cover),alt:''}):n('span',{class:'cover-placeholder',text:'д'})]);cover.querySelector('img')?.addEventListener('error',()=>cover.replaceChildren(n('span',{class:'cover-placeholder',text:'д'})));identity.append(cover,n('div',{},[n('p',{class:'eyebrow',text:'Coleção documental'}),n('h1',{text:label(root)}),n('p',{class:'portal-opening-mission',text:root.subtitle_pt||'Explore os documentos e suas divisões.'}),button('Buscar nesta coleção',openSearch,'quiet')]));}
    lastIdentity=key;
   }
   heading.textContent=mode==='home'?'Coleções':mode==='search'?(root?(child?label(child):label(root)):'Resultados da pesquisa'):(child?label(child):'Documentos da coleção');
   note.textContent=mode==='home'?'Escolha uma capa para entrar no conjunto documental.':root?(child?label(root)+' › '+label(child):'Originais e traduções deste conjunto'):active?'Resultados do acervo; versões privadas ficam fora desta consulta.':'';
   const divisionKey=(root?.id||'')+'/'+(child?.id||'')+'/'+mode;
   if(lastDivision!==divisionKey){divisions.replaceChildren();if(root&&mode==='collection')for(const entry of [{id:'',title_pt:'Todos os documentos'},...(root.subcollections||[])]){const item=button(label(entry),()=>{sub.value=entry.id;searchTools.search();},'quiet'+(sub.value===entry.id?' active':''));item.setAttribute('aria-current',sub.value===entry.id?'page':'false');divisions.append(item);}lastDivision=divisionKey;}
   divisions.hidden=!root?.subcollections?.length||mode!=='collection';
   const text=child?.description_pt||root?.description_pt||'';description.hidden=!root||!text;descriptionText.textContent=text;
   if(!active)results.replaceChildren();
  },
  open:(doc,match,q)=>{openDocument(doc);const material=current();if(match){material.lang=match.language;material.mode='read';material.showCanonical=true;material.findState={query:q.replace(/^"|"$/g,''),lang:match.language,caseSensitive:false,index:0};}persist();}
 },{query,collection,sub,scope,language,results,cards,heading,note,summary,zipHost});
 const activityController=new AbortController();cleanup=()=>{searchTools.dispose();activityController.abort();};content.append(shell);searchTools.search({reset:false});mountHomeActivity(activity,catalog,openActivity,{signal:activityController.signal});
}
function draftKey(m) { return `${m.projectId||saved.scope||'acervo'}:${m.doc.id}:${m.lang}`; }
async function bodyFor(m,lang=m.lang){
 let data;
 if(m.projectId){
  const snapshot=await editorialRequest('/api/editorial/workspace/edition?'+new URLSearchParams({project:m.projectId,edition:m.doc.id+':'+lang}));m.projectSnapshots||={};m.projectSnapshots[lang]=snapshot;
  data={source:snapshot.content,body:window.splitExportHeaders(snapshot.content).body,edition:{file:m.doc.languages?.find(l=>l.code===lang)?.file||m.doc.id+'.'+lang+'.md',format:snapshot.format}};
 }else data=await editionText(m.doc,lang);
 return {...data,body:m.showCanonical?data.body:(saved.drafts[`${m.projectId||saved.scope||'acervo'}:${m.doc.id}:${lang}`]??data.body)};
}
function mode(m, value) { remember();if(value==='facsimile'&&['read','paragraphs','parallel'].includes(m.mode))m.facsimileReturnMode=m.mode; m.capture = null;if(value==='edit'||value==='import-translation')m.returnMode=['read','paragraphs','parallel','facsimile'].includes(m.mode)?m.mode:'read';m.mode = value; render(); }
function mark(m, element) { const old = saved.markers[m.doc.id]; if (old?.signature === fingerprint(element.textContent) && old.lang === m.lang) {
    delete saved.markers[m.doc.id];
}
else
    saved.markers[m.doc.id] = { lang: m.lang, unit: Number(element.dataset.unit), signature: fingerprint(element.textContent) }; persist(); content.querySelectorAll('[data-unit]').forEach(e => e.toggleAttribute('data-marked', saved.markers[m.doc.id]?.signature === fingerprint(e.textContent) && saved.markers[m.doc.id]?.lang === m.lang)); docControls(m); }
function annotate(m, host) { let i = 0; for (const element of host.children) {
    if (element.matches('p,blockquote,ul,ol,table,h1,h2,h3,h4,h5,h6')) {
        element.dataset.unit = String(++i);
        element.toggleAttribute('data-marked', saved.markers[m.doc.id]?.signature === fingerprint(element.textContent) && saved.markers[m.doc.id]?.lang === m.lang);
        element.onclick = e => { if (e.target.closest('a,button,summary,input,textarea') || window.getSelection()?.toString())
            return; mark(m, element); };
    }
} }
function resume(m) { const marker = saved.markers[m.doc.id]; if (!marker)
    return; if (marker.lang !== m.lang) {
    m.lang = marker.lang;
    render().then(() => resume(m));
    return;
} const blocks = [...content.querySelectorAll('[data-unit]')]; const target = blocks.find(e => fingerprint(e.textContent) === marker.signature); if (target)
    target.scrollIntoView({ block: 'center', behavior: 'smooth' });
else
    toast('O trecho mudou nesta versão. Confira seu marcador antes de retomá-lo.'); }
function docControls(m) {
 const languages=(m.doc.languages||[]).map(l=>[l.code,LANGUAGES[l.code]||l.code]);
 controls.replaceChildren(...[
 m.projectId&&button('Materiais do projeto',()=>projectMaterials(projectEnvironment(generation,m),m.projectId),'quiet'),
 select(languages,m.lang,v=>{remember();m.capture=null;if(m.otherLang===v)m.otherLang=m.lang;m.lang=v;render();},'Idioma principal'),
 ['parallel','paragraphs'].includes(m.mode)&&comparisonLanguage(m)&&n('span',{class:'comparison-arrow',text:'⇄'}),
 ['parallel','paragraphs'].includes(m.mode)&&comparisonLanguage(m)&&select(languages.filter(([code])=>code!==m.lang),comparisonLanguage(m),v=>{remember();m.otherLang=v;render();},'Idioma de comparação'),
 select([['read','Leitura'],['paragraphs','Estudo por trecho'],['parallel','Comparar idiomas'],['edit','Editar Markdown'],...(documentLinks(m).length?[['facsimile','Texto + fac-símile']]:[]),...(backendAvailable&&(m.projectId||saved.scope==='acervo')?[['import-translation','Importar tradução']]:[])],m.mode,v=>mode(m,v),'Atividade'),
 button('Buscar',()=>findInDocument(m),'quiet'),button('Índice',()=>indexPanel(m),'quiet'),button('Notas',()=>notesPanel(m),'quiet'),saved.markers[m.doc.id]&&button('● Retomar',()=>resume(m),'quiet'),button('⋯',()=>materialPanel(m),'quiet')
 ].filter(Boolean));
}
function documentContext(m){
 const paths=[];
 for(const collection of catalog.collections){
   if(!catalog.collectionDocuments(collection).some(d=>d.id===m.doc.id))continue;
   const sub=(collection.subcollections||[]).filter(s=>(s.document_ids||(s.documents||[]).map(d=>d.id)).includes(m.doc.id));
   for(const member of sub.length?sub:[null])paths.push({collection,sub:member});
 }
 return n('nav',{class:'document-context','aria-label':'Coleção do documento'},paths.map(path=>n('div',{},[
  b(label(path.collection),()=>{libraryState.collection=path.collection.id;libraryState.sub=path.sub?.id||'';libraryState.q='';navigate('biblioteca');},'context-link'),
  path.sub&&n('span',{text:' › '}),path.sub&&b(label(path.sub),()=>{libraryState.collection=path.collection.id;libraryState.sub=path.sub.id;libraryState.q='';navigate('biblioteca');},'context-link')
 ])));
}
async function documentView(m,version){
 if(m.projectId){
  if(!backendAvailable)throw Error('Este material pertence a um projeto privado. Inicie o backend local para consultá-lo.');
  const [project,versions]=await Promise.all([editorialRequest('/api/editorial/projects/'+m.projectId),editorialRequest('/api/editorial/workspace/document?'+new URLSearchParams({project:m.projectId,document:m.doc.id}))]);if(version!==generation)return;
  m.project=project;const canonical=catalog.documents.get(m.doc.id);m.doc={...canonical,languages:[...(canonical.languages||[])]};for(const edition of versions.editions)if(!m.doc.languages.some(e=>e.code===edition.language))m.doc.languages.push({code:edition.language,file:m.doc.id+'.'+edition.language+'.md',format:edition.format});
  if(!m.doc.languages.some(e=>e.code===m.lang))m.lang=m.doc.languages[0]?.code;projectContext=project;updateScope();
 }

    m.documentLinks=catalog.links.filter(l=>l.document_id===m.doc.id&&!l.local);
    if(backendAvailable){try{const response=await editorialRequest('/api/editorial/pdf/links?'+new URLSearchParams({document:m.doc.id,project:m.projectId||''}));if(version!==generation)return;m.documentLinks=mergeDocumentLinks(m.documentLinks,response.items);}catch(error){if(version!==generation)return;toast('Vínculos locais indisponíveis: '+error.message);}}
    if(m.mode==='correct-passage'){const release=await mountPassageEditor(passageEnvironment(version,m),m);if(version===generation)cleanup=release||(()=>{});else release?.();return;}
    docControls(m);
    const data = await bodyFor(m);
    if (version !== generation)
        return;
    if(m.projectId&&m.project.archived&&['edit','import-translation'].includes(m.mode)){content.append(n('section',{class:'page-shell'},[heading('Projeto arquivado','Consulta preservada','Reabra o projeto para gravar versões privadas.'),button('Voltar à leitura',()=>mode(m,'read'),'quiet'),button('Organizar projeto',()=>navigate('projetos/'+m.projectId))]));return;}
    if(m.mode==='import-translation'){content.classList.add('task-scroll');controls.replaceChildren(button('Voltar ao texto',()=>mode(m,m.returnMode||'read'),'quiet'));await translationView(m,version);return;}
    if (m.mode === 'edit') {
        if(backendAvailable&&!m.projectId){try{m.backendSnapshot=await editorialRequest('/api/editorial/editions/'+encodeURIComponent(m.doc.id+':'+m.lang));if(version!==generation)return;if(saved.drafts[draftKey(m)]===undefined)data.body=window.splitExportHeaders(m.backendSnapshot.content).body;}catch(error){m.backendSnapshot=null;toast('Edição do acervo indisponível: '+error.message);}}
        await editorView(m, data, version);
        return;
    }
    const workspace = n('section', { class: 'workspace' }), scroll = n('div', { class: 'document-scroll' }), article = n('article', { class: 'reading' + (m.mode === 'paragraphs' ? ' numbered' : '') });
    article.append(n('header', { class: 'document-heading' }, [documentContext(m),n('p', { class: 'eyebrow', text: [dateLabel(m.doc), m.doc.source_name].filter(Boolean).join(' · ') }), n('h1', { text: label(m.doc) }),n('p',{class:'transcription-origin'},[n('span',{text:'Fonte da transcrição: '}),m.doc.source_url?n('a',{href:m.doc.source_url,target:'_blank',rel:'noopener',text:m.doc.source_name||'Fonte cadastrada'}):n('span',{text:m.doc.source_name||'Não informada'})]), n('p', { class: 'edition-caption', text: !m.showCanonical&&saved.drafts[draftKey(m)] !== undefined ? 'Rascunho do piloto · o texto do acervo está preservado' : `${LANGUAGES[m.lang]} · Clique em um parágrafo para marcar ou desmarcar.` })]));
    const text = n('div', { class: 'edition-body', lang: m.lang });
    m.renderedBodies={[m.lang]:{body:data.body,format:data.edition.format}};
    text.innerHTML = renderMarkdown(data.body, data.edition.format,true);
    annotate(m, text);
    if(m.projectId)article.querySelector('.edition-caption').textContent='Projeto: '+m.project.title+(m.projectSnapshots?.[m.lang]?.has_draft?' · versão privada salva no projeto':' · usando a versão do acervo; ainda sem edição privada neste idioma')+(m.project.archived?' · arquivado':'');
    article.append(text);
    scroll.append(article);
    workspace.append(scroll);
    content.append(workspace);
    if (m.mode === 'parallel') {
        const otherLang=comparisonLanguage(m);
        if(otherLang){
            const alt=await bodyFor(m,otherLang);
            if(version!==generation)return;
            m.renderedBodies[otherLang]={body:alt.body,format:alt.edition.format};
            const other=n('div');other.innerHTML=renderMarkdown(alt.body,alt.edition.format,true);
            const left=[...text.children],right=[...other.children];
            const pairs=n('div',{class:'paired-text'});
            const count=Math.max(left.length,right.length);
            for(let i=0;i<count;i++){
                const row=n('div',{class:'paired-row'});
                const a=n('div',{class:'paired-cell edition-body',lang:m.lang});
                const c=n('div',{class:'paired-cell edition-body',lang:otherLang});
                if(left[i])a.append(left[i]);else a.append(n('p',{class:'missing-pair',text:'Sem bloco nesta posição.'}));
                if(right[i]){right[i].dataset.comparisonUnit=String(i+1);c.append(right[i]);}
                else c.append(n('p',{class:'missing-pair',text:'Sem bloco nesta posição.'}));
                row.append(a,c);pairs.append(row);
            }
            text.replaceWith(pairs);
            article.classList.add('parallel-reading','numbered');
            scroll.classList.add('paired-scroll');
            article.querySelector('.edition-caption').textContent=`${LANGUAGES[m.lang]} ⇄ ${LANGUAGES[otherLang]} · Blocos alinhados pela ordem; correspondência documental a conferir.`;
        }else toast('Este documento possui apenas um idioma.');
    }
    if (m.mode === 'paragraphs') {
        const alt = m.doc.languages?.find(l => l.code === comparisonLanguage(m));
        if (alt) {
            const translated = await bodyFor(m, alt.code);
            if (version !== generation)
                return;
            const container = n('div');
            m.renderedBodies[alt.code]={body:translated.body,format:translated.edition.format};
            container.innerHTML = renderMarkdown(translated.body, translated.edition.format,true);
            const original = [...text.children], translation = [...container.children];
            original.forEach((el, i) => { if (!el.matches('p,blockquote'))
                return; const expansion = n('details', { class: 'translation-expand',open:m.expandedUnits?.includes(i) }, [n('summary', { text: `Abrir ${LANGUAGES[alt.code]} · correspondência por ordem a conferir` })]); if (translation[i])
                {const translatedBlock=translation[i].cloneNode(true);translatedBlock.dataset.comparisonUnit=String(i+1);expansion.append(n('div',{class:'translation-body',lang:alt.code},[translatedBlock]));}
            else
                expansion.append(n('p', { text: 'Sem trecho correspondente nesta posição.' })); expansion.addEventListener('toggle',()=>{const opened=new Set(m.expandedUnits||[]);if(expansion.open)opened.add(i);else opened.delete(i);m.expandedUnits=[...opened];queueSession();});el.after(expansion); });
        }
    }
    if(m.mode==='facsimile'){const remembered=m.facsimile?.anchor;if(remembered){const link=documentLinks(m).find(l=>l.id===m.facsimile.source),fresh=link?.anchors?.find(a=>a.id===remembered.id);m.facsimile.anchor=fresh?{...fresh}:null;if(fresh){try{const shown=fresh.language===m.lang?data:await bodyFor(m,fresh.language);const hash=await bodyDigest(shown.body);if(version!==generation)return;m.facsimile.anchor.stale_text=fresh.stale_text||hash!==fresh.body_sha256;}catch{if(version!==generation)return;m.facsimile.anchor.stale_text=true;}}}mountDocumentFacsimile(m,workspace,scroll);}
    scroll.scrollTop = m.scroll || 0;
    if (m.position) {
        const target = article.querySelector('[data-unit="' + m.position.unit + '"]');
        if (target)
            scroll.scrollTop += target.getBoundingClientRect().top - scroll.getBoundingClientRect().top - m.position.offset;
    }
    if(m.mode==='facsimile')highlightAssociatedText(m,text,data.body,version);
}
function indexPanel(m) { if(togglePanel('Índice'))return; const headings = [...content.querySelectorAll('.reading:first-child h1,.reading:first-child h2,.reading:first-child h3,.reading h2,.reading h3')]; panel('Índice', [...headings.map(h => b(h.textContent, () => { h.scrollIntoView({ block: 'start', behavior: 'smooth' }); if (!pinned)
        closePanel(); }, 'index-entry')), !headings.length && n('p', { text: 'Não há subtítulos nesta atividade.' })]); }
function documentLinks(m){return m.documentLinks||catalog.links.filter(l=>l.document_id===m.doc.id&&!l.local);}
function materialPanel(m){
 if(togglePanel('Documento e ferramentas'))return;
 const linked=documentLinks(m);
 panel('Documento e ferramentas',[
  menuGroup('Consultar',[
   {title:'Trechos associados ao fac-símile',description:'Página, unidade, região e alertas de revisão.',run:()=>documentAssociations(parityEnvironment(m),m,documentLinks(m))},
   backendAvailable&&{title:'Pendências deste documento',description:'Consultar e registrar a revisão sem alterar o texto.',run:()=>{closePanel();navigate('fila/'+encodeURIComponent(m.doc.id));}},
   {title:'Ficha catalográfica',description:'Coleções, data, referência e fonte do texto.',run:()=>panel('Ficha catalográfica',[documentContext(m),n('h3',{text:label(m.doc)}),...Object.entries({Identificação:m.doc.id,Data:dateLabel(m.doc),Fonte:m.doc.source_name,Arquivo:m.doc.archive,Origem:m.doc.source_url}).filter(([,value])=>value).map(([key,value])=>n('p',{},[n('strong',{text:key+': '}),n('span',{text:typeof value==='string'?value:JSON.stringify(value)})])),button('Editar ficha',()=>{closePanel();saved.catalogReturn={id:m.doc.id,lang:m.lang,mode:m.mode};navigate('catalogo/'+m.doc.id);})])},
   {title:'Notas do documento',description:'Anotações gerais e vinculadas a frases.',run:()=>notesPanel(m)},
   linked.length&&{title:'Texto + fac-símile',description:'Conferir a transcrição junto da imagem.',run:()=>{closePanel();mode(m,'facsimile');}}
  ]),
  linked.length&&menuGroup('Fontes disponíveis',linked.map(link=>({title:link.source_title||link.source_id,description:link.local?'Fonte local de trabalho':'PDF preservado do acervo',run:()=>openSource(link)}))),
  menuGroup('Versões e exportação',[
   m.passageWork&&{title:'Retomar correção de trecho',description:'Voltar ao rascunho do trecho sem perder a leitura.',run:()=>{remember();m.mode='correct-passage';render();}},
   m.projectId&&{title:'Histórico da versão privada',description:'Consultar e restaurar somente a versão do projeto.',run:()=>workspaceHistory(projectEnvironment(generation,m),m)},
   m.projectId&&{title:'Incorporar versão salva ao acervo',description:'Comparar e confirmar a substituição no acervo local.',run:()=>promoteWorkspace(projectEnvironment(generation,m),m)},
   m.projectId&&{title:'Abrir versão do acervo',description:'Abrir outra aba, fora do projeto.',run:()=>openDocument(catalog.documents.get(m.doc.id))},
   saved.drafts[draftKey(m)]!==undefined&&{title:m.showCanonical?'Mostrar rascunho da sessão':(m.projectId?'Mostrar versão salva no projeto':'Mostrar versão do acervo'),description:'Alternar a versão exibida sem gravar alterações.',run:()=>{remember();m.showCanonical=!m.showCanonical;closePanel();render();}},
   {title:'Imprimir / salvar como PDF',description:'Preparar a versão no idioma atual, com identificação da origem.',run:()=>printDocument(parityEnvironment(m),m)},
   {title:'Baixar Markdown',description:'Exportar a versão no idioma atual.',download:true,run:async()=>{const data=await bodyFor(m);download(data.edition.file.split('/').pop(),data.body);}},
   backendAvailable&&!m.projectId&&{title:'Histórico do acervo local',description:'Gravações reais e restauração com prévia.',run:()=>backendHistory(m)},
   {title:'Histórico da sessão',description:'Versões dos rascunhos temporários.',run:historyPanel}
  ])
 ]);
}
function mountDocumentFacsimile(m,workspace,scroll){
 const links=documentLinks(m);if(!links.length)return;
 const existing=m.facsimile||{},link=links.find(l=>l.id===existing.source)||links[0];
 if(existing.pdfUrl&&existing.pdfUrl!==link.pdf_url){existing.pdf?.destroy();m.facsimile=null;}
 const state=m.facsimile||={source:link.id,page:Number(link.pages?.[0])||1};
 state.source=link.id;state.pdfUrl=link.pdf_url;state.pageMap=link.local?null:link.published_page_map;state.page=Number(state.page)||Number(link.pages?.[0])||1;
 const stage=n('div',{class:'pdf-stage'}),side=n('section',{class:'document-facsimile','aria-label':'Fac-símile do documento'}),count=n('span',{text:'/ …'}),page=n('input',{class:'review-page-input',type:'number',min:1,value:state.page,'aria-label':'Página física do fac-símile'});
 const selectedPages=state.pageMap?Object.keys(state.pageMap).map(Number).sort((a,b)=>state.pageMap[a]-state.pageMap[b]):null;
 const turn=value=>{if(!Number.isInteger(value)||value<1||(selectedPages?!selectedPages.includes(value):state.count&&value>state.count)){page.value=state.page;return;}remember();state.page=value;render();};
 const step=delta=>turn(selectedPages?selectedPages[selectedPages.indexOf(state.page)+delta]:state.page+delta);page.onchange=()=>turn(Number(page.value));
 const source=select(links.map(l=>[l.id,l.source_title||l.source_id]),link.id,value=>{remember();state.pdf?.destroy();const selected=links.find(l=>l.id===value);m.facsimile={source:value,page:Number(selected.pages?.[0])||1};render();},'Fonte do fac-símile');
 side.append(n('div',{class:'facsimile-source'},[source,button('Sobre a fonte',()=>panel('Proveniência do fac-símile',[n('h3',{text:link.source_title||link.source_id}),n('p',{text:link.source_scope_note||'Confira o alcance desta fonte antes de citar.'}),link.provenance?.original_url&&n('a',{href:link.provenance.original_url,target:'_blank',rel:'noopener',text:'Abrir endereço de origem do PDF ↗'}),n('p',{class:'hint',text:'A página exibida não certifica o alinhamento entre cada parágrafo e sua posição na imagem.'}),n('a',{href:asset(link.pdf_url),download:'',text:state.pageMap?'Baixar PDF selecionado':'Baixar PDF original'})]),'quiet'),b('×',()=>mode(m,['read','paragraphs','parallel'].includes(m.facsimileReturnMode)?m.facsimileReturnMode:'read'),'icon-button close-facsimile',{'aria-label':'Fechar fac-símile e manter o texto aberto',title:'Fechar fac-símile'})]),n('div',{class:'facsimile-provenance'},[n('span',{text:link.local?(link.portalPrepared?'Fonte local · arquivos do portal preparados': 'Fonte de trabalho local · PDF ainda não preparado para o portal'):link.provenance?.archival_original_facsimile===false?'Imagem de edição publicada · não é cópia arquivística original':'Fonte do fac-símile · consulte a proveniência'}),link.provenance?.original_url&&n('a',{href:link.provenance.original_url,target:'_blank',rel:'noopener',text:'Origem do PDF ↗'})]),n('div',{class:'facsimile-pagination'},[
 button('‹',()=>step(-1),'quiet'),page,count,button('›',()=>step(1),'quiet'),
 zoomControls(state,()=>cleanup.refresh?.(),queueSession),
 button('Tela cheia',async()=>{try{await stage.requestFullscreen();}catch{toast('O navegador não permitiu a tela cheia.');}},'quiet')
 ]),stage);
 workspace.classList.add('text-facsimile-workspace');workspace.append(side);installSplitter(workspace,state,queueSession);
 cleanup=mountPdf(state,stage,total=>{count.textContent=selectedPages?'da fonte · '+(selectedPages.indexOf(state.page)+1)+'/'+total+' na seleção':'/ '+total;page.max=selectedPages?Math.max(...selectedPages):total;page.value=state.page;paintAnchorRegion(stage,state);},error=>toast('Fac-símile: '+error.message));
}
function highlightAssociatedText(m,host,body,version){
 const anchor=m.facsimile?.anchor;if(!anchor||anchor.page_number!==m.facsimile.page)return;
 if(anchor.stale_text){toast('O texto mudou desde a associação. Reconfirme o trecho antes de usar seu destaque.');return;}
 if(anchor.language!==m.lang)return;
 const blocks=[...host.querySelectorAll('[data-source-start][data-source-end]')],block=blocks.find(el=>Number(el.dataset.sourceStart)<=anchor.start&&Number(el.dataset.sourceEnd)>=anchor.end);
 const visible=block&&associatedTextRange(body,anchor,Number(block.dataset.sourceStart),Number(block.dataset.sourceEnd),block.textContent,raw=>{const holder=n('div');holder.innerHTML=renderMarkdown(raw);return holder.firstElementChild?.textContent??holder.textContent;});
 const range=visible&&rangeForText(block,visible.start,visible.end);
 if(!range){toast('A página foi aberta, mas não foi possível destacar com segurança o trecho nesta renderização.');return;}
 let target=range;
 if(globalThis.CSS?.highlights&&globalThis.Highlight)CSS.highlights.set('mesa-facsimile-phrase',new Highlight(range));
 else{const mark=n('mark',{class:'facsimile-text-match'});mark.append(range.extractContents());range.insertNode(mark);target=mark;}
 requestAnimationFrame(()=>{if(version!==generation||!host.isConnected)return;const scroll=block.closest('.document-scroll'),rect=target.getBoundingClientRect();if(scroll)scroll.scrollTo({top:scroll.scrollTop+rect.top-scroll.getBoundingClientRect().top-scroll.clientHeight/2+rect.height/2,behavior:'smooth'});});
}
function paintAnchorRegion(stage,state){stage.querySelector('.anchor-region-overlay')?.remove();const anchor=state.anchor,canvas=stage.querySelector('canvas');if(!canvas||!anchor||anchor.page_number!==state.page||anchor.stale_page||anchor.stale_text)return;const boxes=anchor.unit_boxes||[];if(!boxes.length)return;const overlay=n('div',{class:'anchor-region-overlay','aria-label':'Região associada manualmente'});overlay.style.cssText=`width:${canvas.style.width};height:${canvas.style.height};left:${canvas.offsetLeft}px;top:${canvas.offsetTop}px`;for(const [x,y,w,h]of boxes){const box=n('span');box.style.cssText=`left:${x*100}%;top:${y*100}%;width:${w*100}%;height:${h*100}%`;overlay.append(box);}stage.append(overlay);}
function translationView(m,version){
 if(m.projectId)return importWorkspaceTranslation(projectEnvironment(version,m),m);
 if(!backendAvailable||saved.scope!=='acervo'){content.append(n('section',{class:'page-shell'},[heading('Importar tradução','Backend local necessário','A importação real está disponível na Mesa principal, usando python3 -m backend.'),button('Voltar ao texto',()=>mode(m,m.returnMode||'read'))]));return;}
 return editorialRequest('/api/editorial/documents/'+encodeURIComponent(m.doc.id)).then(data=>{
  if(version!==generation)return;
  const original=data.document.source_metadata?.original_language||data.editions[0]?.language;
  const allowed=['pt','en'].filter(code=>code!==original),work=m.translationWork||={language:allowed[0],filename:'',content:'',title:''};
  if(!allowed.includes(work.language))work.language=allowed[0];
  const lang=select(allowed.map(code=>[code,LANGUAGES[code]+(data.editions.some(e=>e.language===code)?' · substituir versão existente':' · nova tradução')]),work.language,value=>{work.language=value;queueSession();},'Idioma da tradução'),file=n('input',{type:'file',accept:'.md,.markdown,text/markdown','aria-label':'Arquivo Markdown da tradução'}),status=n('p',{class:'hint',text:work.filename?'Arquivo preparado: '+work.filename:'Escolha um Markdown em UTF-8, até 4 MiB.'}),title=field('Título no idioma da tradução (opcional)',work.title);
  title.input.oninput=()=>{work.title=title.input.value;queueSession();};
  file.onchange=async()=>{try{const chosen=file.files[0];if(!chosen)return;if(!/\.(md|markdown)$/i.test(chosen.name)||chosen.size>4*1024*1024)throw Error('Escolha um Markdown de até 4 MiB.');work.content=new TextDecoder('utf-8',{fatal:true}).decode(await chosen.arrayBuffer());work.filename=chosen.name;status.textContent='Arquivo preparado: '+chosen.name;queueSession();}catch(error){toast(error.message);}};
  const prepare=button('Conferir importação no acervo',async()=>{
    if(!work.filename||!work.content.trim()){toast('Escolha o arquivo da tradução.');return;}
    prepare.disabled=true;
    try{const result=await editorialRequest('/api/editorial/translations/preview',{body:{revision:data.revision,document_id:m.doc.id,language:work.language,filename:work.filename,content:work.content,title:work.title||''}});if(version!==generation)return;backendPreview(m,result,work.language);}catch(error){toast(error.message);}finally{prepare.disabled=false;}
  },'primary');
  content.append(n('section',{class:'page-shell translation-import'},[heading('Importação real · acervo local',label(m.doc),'A associação será ao documento abaixo. A prévia verificará identificação, diferenças e estrutura; salvar altera apenas o acervo local, sem publicar no GitHub.'),n('div',{class:'editor-destination',text:'Documento selecionado: '+m.doc.id+' · Idioma original protegido: '+(LANGUAGES[original]||original)}),n('div',{class:'translation-import-fields'},[n('label',{text:'Idioma da tradução'}),lang,title.element,n('label',{text:'Arquivo Markdown'}),file,status,prepare]) ]));
 }).catch(error=>{toast(error.message);});
}
function backendPreview(m,result,language,destination=null){
 const detail=result.markdown_edit||result.translation;
 const before=detail?.current_content??JSON.stringify(result.changes.map(c=>({campo:c.field,valor:c.before})),null,2),after=detail?.content??JSON.stringify(result.changes.map(c=>({campo:c.field,valor:c.after})),null,2);
 previewChange({backend:true,destination,title:'Conferir alteração no acervo local · '+m.doc.id, before,after,proposal:result,
  confirm:async()=>{
    const receipt=await editorialRequest('/api/editorial/save',{body:{preview_id:result.preview_id,acknowledge_warnings:!result.requires_acknowledgement||previewWarningsAccepted}});
    // A confirmação já foi efetivada. Falhas ao atualizar a tela não devem repetir a transação.
    const key='acervo:'+m.doc.id+':'+language;if(language){delete saved.drafts[key];if(m.buffers)delete m.buffers[key];m.lang=language;}
    if(result.translation)m.translationWork=undefined;m.backendSnapshot=null;m.capture=null;m.mode=m.returnMode||'read';m.showCanonical=true;saved.lastBackendReceipt={document_id:m.doc.id,history_id:receipt.history_id,time:new Date().toISOString()};persist();
    preview=null;try{clearEditionCache();catalog=await loadCatalog();for(const material of materials)if(material.kind==='document'&&catalog.documents.has(material.doc.id))material.doc=catalog.documents.get(material.doc.id);await render();toast('Salvo no acervo local, com histórico. Nenhum commit ou push foi realizado.');}catch(error){content.replaceChildren(n('section',{class:'page-shell'},[heading('Gravação concluída','O acervo foi salvo.',`Histórico: ${receipt.history_id}. Recarregue para atualizar a interface; não repita a gravação.`)]));}
  }
 });
}
let previewWarningsAccepted=false;
async function backendHistory(m){
 try{const result=await editorialRequest('/api/editorial/history?document='+encodeURIComponent(m.doc.id));panel('Histórico do acervo local',[
  n('p',{text:'Transações individuais deste documento. Restaurar exige prévia e gera novo histórico. Alterações de lotes e coleções continuam disponíveis no Estúdio oficial.'}),
  ...result.items.filter(item=>item.state==='committed'&&item.document_id===m.doc.id&&(!item.entity?.kind||item.entity.kind==='document')).map(item=>n('div',{class:'note-card'},[n('p',{text:new Date(item.created_at).toLocaleString('pt-BR')}),n('p',{text:item.summary}),button('Conferir restauração',async()=>{try{const fresh=await editorialRequest('/api/editorial/documents/'+encodeURIComponent(m.doc.id));const proposal=await editorialRequest('/api/editorial/preview',{body:{revision:fresh.revision,restore_id:item.id}});backendPreview(m,proposal,null);}catch(error){toast(error.message);}},'quiet')])),
  !result.items.length&&n('p',{text:'Ainda não há gravações editoriais deste documento.'})
 ]);}catch(error){toast(error.message);}
}
function noteId(){return globalThis.crypto?.randomUUID?.()||'nota-'+Date.now()+'-'+Math.random().toString(36).slice(2);}
function documentNotes(m){
 saved.notes[m.key]=(saved.notes[m.key]||[]).filter(Boolean).map(entry=>typeof entry==='string'?{id:noteId(),text:entry,passage:null}:{...entry,id:entry.id||noteId()});
 return saved.notes[m.key];
}
function notesPanel(m,passage=null,editing=null) {
 if(passage)m.noteSelection=passage;
 const key='note:'+m.key+':'+(editing?.id||(passage?fingerprint(passage.signature+':'+passage.start+':'+passage.quote):'general'));
 const isPassage=Boolean(passage),type=isPassage?'Nota sobre trecho':'Nota geral do documento';
 const input=n('textarea',{'aria-label':editing?'Editar '+type:type,placeholder:isPassage?'Comente apenas o trecho citado abaixo…':'Escreva uma observação sobre o documento como um todo…',rows:5});
 const legacyKey='note:'+m.key+':'+(passage?.signature||'general');
 input.value=saved.noteWork[key]??(passage&&!editing?saved.noteWork[legacyKey]:undefined)??editing?.text??'';
 input.oninput=()=>{saved.noteWork[key]=input.value;queueSession();};
 const general=button('Nota geral',()=>notesPanel(m),!isPassage?'active':'quiet');
 const specific=button('Nota sobre trecho',()=>notesPanel(m,m.noteSelection),isPassage?'active':'quiet');specific.disabled=!m.noteSelection;
 const entries=documentNotes(m).map(note=>n('div',{class:'note-card'},[
   n('p',{class:'note-type',text:note.passage?'Nota sobre trecho · '+(LANGUAGES[note.passage.lang]||note.passage.lang):'Nota geral do documento'}),
   note.passage&&n('blockquote',{text:note.passage.quote}),n('p',{text:note.text}),
   n('div',{class:'note-actions'},[
    note.passage&&button('Localizar frase',()=>locatePassage(m,note.passage),'quiet'),
    note.passage&&button('Citar',()=>citePassage(m,note.passage),'quiet'),
    button('Editar nota',()=>notesPanel(m,note.passage,note),'quiet'),
    button('Apagar nota',()=>deleteNote(m,note.id),'quiet note-delete')
   ])
 ]));
 const deleted=saved.noteTrash.filter(entry=>entry.documentId===m.key);
 panel('Notas do documento',[
   n('div',{class:'note-kind-switch',role:'group','aria-label':'Tipo de nota'},[general,specific]),
   !m.noteSelection&&n('p',{class:'hint',text:'Para anotar uma frase: selecione palavras no texto e clique em Anotar trecho.'}),
   n('h3',{class:'note-composer-title',text:(editing?'Editar: ':'Nova: ')+type.toLocaleLowerCase()}),
   passage?n('div',{class:'note-anchor'},[n('p',{text:'Esta nota ficará vinculada exatamente à frase citada:'}),n('blockquote',{text:passage.quote})]):n('p',{class:'hint',text:'Esta nota pertence ao documento inteiro e não tem frase vinculada.'}),
   input,button(editing?'Atualizar nota':isPassage?'Guardar nota deste trecho':'Guardar nota geral',()=>{
      if(!input.value.trim())return;
      const notes=documentNotes(m);
      if(editing){const index=notes.findIndex(note=>note.id===editing.id);if(index<0){toast('Esta nota não está mais na lista.');return;}record('note',m.key,notes[index]);notes[index]={...notes[index],text:input.value.trim(),passage,updatedAt:new Date().toISOString()};}
      else notes.push({id:noteId(),text:input.value.trim(),passage,time:new Date().toISOString()});
      delete saved.noteWork[key];if(passage&&!editing)delete saved.noteWork[legacyKey];persist();notesPanel(m);toast(editing?'Nota atualizada na sessão.':'Nota guardada na sessão; não publicada.');
   },'primary'),
   editing&&button('Cancelar edição',()=>notesPanel(m),'quiet'),
   deleted.length&&n('div',{class:'note-undo'},[n('span',{text:'Notas apagadas podem ser recuperadas.'}),button('Desfazer última exclusão',()=>restoreNote(m,deleted.at(-1).trashId),'quiet')]),
   n('h3',{class:'note-list-title',text:`Notas guardadas · ${entries.length}`}),...entries,
   deleted.length&&button(`Notas apagadas · ${deleted.length}`,()=>deletedNotesPanel(m),'quiet'),
   button('Baixar notas deste documento',()=>download(m.doc.id+'.notas.json',JSON.stringify({document_id:m.doc.id,notes:saved.notes[m.key]||[],deleted_notes:saved.noteTrash.filter(e=>e.documentId===m.key)},null,2),'application/json'))
 ]);
 persist();
}
function deleteNote(m,id){
 const notes=documentNotes(m),index=notes.findIndex(note=>note.id===id);if(index<0)return;
 saved.noteTrash.push({trashId:noteId(),documentId:m.key,note:notes[index],index,deletedAt:new Date().toISOString()});
 notes.splice(index,1);persist();notesPanel(m);toast('Nota apagada. Use Desfazer última exclusão para recuperá-la.');
}
function restoreNote(m,trashId){
 const index=saved.noteTrash.findIndex(entry=>entry.trashId===trashId&&entry.documentId===m.key);if(index<0)return;
 const entry=saved.noteTrash[index],notes=documentNotes(m);
 if(notes.some(note=>note.id===entry.note.id)){toast('A nota já está na lista.');return;}
 notes.splice(Math.min(entry.index,notes.length),0,entry.note);saved.noteTrash.splice(index,1);persist();notesPanel(m);toast('Nota recuperada.');
}
function deletedNotesPanel(m){
 panel('Notas apagadas',[
  n('p',{text:'As notas abaixo saíram da lista, mas permanecem recuperáveis nesta sessão e na cópia JSON.'}),
  ...saved.noteTrash.filter(entry=>entry.documentId===m.key).map(entry=>n('div',{class:'note-card'},[
    n('p',{class:'note-type',text:entry.note.passage?'Nota sobre trecho':'Nota geral'}),entry.note.passage&&n('blockquote',{text:entry.note.passage.quote}),n('p',{text:entry.note.text}),button('Recuperar nota',()=>restoreNote(m,entry.trashId),'quiet')
  ])),button('Voltar às notas',()=>notesPanel(m),'quiet')
 ]);
}
function selectionPassage(){
 const m=current(),selection=window.getSelection();if(!m||m.kind!=='document'||['edit','correct-passage'].includes(m.mode)||selection?.isCollapsed||!selection?.rangeCount)return null;
 const element=node=>node?.nodeType===1?node:node?.parentElement;
 const block=node=>element(node)?.closest('[data-unit],[data-comparison-unit]');
 const start=block(selection.anchorNode),end=block(selection.focusNode);
 if(!start||start!==end||!content.contains(start))return null;
 const lang=start.closest('[lang]')?.lang||m.lang,range=selection.getRangeAt(0),prefix=document.createRange();
 prefix.selectNodeContents(start);prefix.setEnd(range.startContainer,range.startOffset);
 const offset=prefix.toString().length,raw=range.toString();
 const anchor=makeTextAnchor(start.textContent,offset,offset+raw.length,lang,Number(start.dataset.unit||start.dataset.comparisonUnit),!m.showCanonical&&saved.drafts[`${m.projectId||saved.scope||'acervo'}:${m.doc.id}:${lang}`]!==undefined);
 if(!anchor.quote)return null;
 Object.defineProperty(anchor,'renderedBlockText',{value:start.textContent,enumerable:false});
 anchor.sourceStart=start.dataset.sourceStart===undefined?null:Number(start.dataset.sourceStart);anchor.sourceEnd=start.dataset.sourceEnd===undefined?null:Number(start.dataset.sourceEnd);
 if(m.projectId)anchor.project={id:m.projectId,title:m.project.title,revision:m.projectSnapshots?.[lang]?.revision};
 return anchor;

}
const passageActions=n('div',{class:'passage-actions',hidden:true,role:'toolbar','aria-label':'Ações sobre o trecho selecionado'});document.body.append(passageActions);
function hidePassageActions(){passageActions.hidden=true;}
let selectionTimer;
document.addEventListener('selectionchange',()=>{clearTimeout(selectionTimer);selectionTimer=setTimeout(()=>{
 if(automaticTextSelection||$('#dialog').open||!$('#auxiliary').hidden){hidePassageActions();return;}
 const passage=selectionPassage();if(!passage){hidePassageActions();return;}
 const m=current();passageActions.replaceChildren(...[n('span',{text:`${LANGUAGES[passage.lang]} · trecho selecionado`}),button('Citar',()=>{hidePassageActions();citePassage(m,passage);}),button('Anotar trecho',()=>{hidePassageActions();notesPanel(m,passage);}),backendAvailable&&Number.isInteger(passage.sourceStart)&&button('Associar ao PDF',()=>{hidePassageActions();associatePassage(parityEnvironment(m),m,passage);}),backendAvailable&&saved.scope==='acervo'&&['pt','en'].includes(passage.lang)&&passage.lang!==(m.doc.original_language||(m.doc.languages.some(e=>e.code==='ru')?'ru':m.doc.languages[0]?.code))&&Number.isInteger(passage.sourceStart)&&button('Corrigir tradução',()=>{hidePassageActions();beginPassageEdit(passageEnvironment(generation,m),m,passage);}),b('×',hidePassageActions,'icon-button',{'aria-label':'Fechar ações do trecho'})].filter(Boolean));
 passageActions.hidden=false;
},120);});
passageActions.addEventListener('mousedown',event=>event.preventDefault());
function citePassage(m,passage){
 const citation=passageCitation(m.doc,passage,asset('index.html')+'#/doc/'+encodeURIComponent(m.doc.id));
 const input=n('textarea',{'aria-label':'Citação para copiar',class:'citation-text',rows:9,readonly:true});input.value=citation;
 dialog('Citar trecho',[n('p',{text:'O número do bloco pertence ao piloto e pode mudar se o texto for editado. Confira a referência e a versão antes de usar a citação em um trabalho.'}),input,
 button('Copiar citação',async()=>{try{await navigator.clipboard.writeText(citation);toast('Citação copiada.');}catch{input.focus();input.select();toast('Texto selecionado: use Ctrl+C ou o comando Copiar do navegador.');}},'primary'),
 button('Baixar citação',()=>download(m.doc.id+'.citacao.txt',citation,'text/plain;charset=utf-8'),'quiet')]);
}
let automaticTextSelection=false;
content.addEventListener('pointerdown',()=>automaticTextSelection=false);
content.addEventListener('keydown',()=>automaticTextSelection=false);
function rangeForText(host,start,end){
 const walker=document.createTreeWalker(host,NodeFilter.SHOW_TEXT),range=document.createRange();let node,offset=0,hasStart=false;
 while((node=walker.nextNode())){
   const next=offset+node.data.length;
   if(!hasStart&&start>=offset&&start<next){range.setStart(node,start-offset);hasStart=true;}
   if(hasStart&&end<=next){range.setEnd(node,end-offset);return range;}
   offset=next;
 }
 return null;
}
function clearLocatedPhrase(){globalThis.CSS?.highlights?.delete('mesa-note-phrase');}
async function locatePassage(m,passage){
 remember();active=m.key;m.lang=passage.lang;m.mode='paragraphs';closePanel();hidePassageActions();
 if(location.hash!=='#mesa'){location.hash='mesa';await new Promise(resolve=>setTimeout(resolve,0));}
 await render();
 const candidates=[...content.querySelectorAll('[data-unit],[data-comparison-unit]')]
   .filter(e=>e.closest('[lang]')?.lang===passage.lang)
   .map(block=>({block,match:resolveTextQuote(block.textContent,passage)}));
 const found=candidates.filter(c=>c.match.status==='found'),unchanged=found.filter(c=>c.match.exactBlock),contextual=found.filter(c=>c.match.context);
 const choices=unchanged.length?unchanged:contextual.length?contextual:found;
 if(choices.length!==1||(!unchanged.length&&!contextual.length&&candidates.some(c=>c.match.status==='ambiguous'))){toast(choices.length||candidates.some(c=>c.match.status==='ambiguous')?'A frase aparece mais de uma vez sem contexto suficiente. Nenhuma ocorrência foi escolhida automaticamente.':'A frase mudou ou não está nesta versão. A nota conserva a citação original.');return;}
 const {block,match}=choices[0],range=rangeForText(block,match.start,match.end);if(!range){toast('Não foi possível destacar a frase nesta renderização. A nota foi preservada.');return;}
 clearLocatedPhrase();
 if(globalThis.CSS?.highlights&&globalThis.Highlight)CSS.highlights.set('mesa-note-phrase',new Highlight(range));
 else{automaticTextSelection=true;const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);}
 const scroll=block.closest('.document-scroll'),rect=range.getBoundingClientRect();
 if(scroll)scroll.scrollTo({top:scroll.scrollTop+rect.top-scroll.getBoundingClientRect().top-scroll.clientHeight/2+rect.height/2,behavior:'smooth'});
 if(!match.exactBlock)toast('Frase localizada literalmente. O texto ao redor mudou desde a criação da nota.');
}
let findNativeSelection=false;
function clearFindHighlights(){
 if(findNativeSelection){window.getSelection()?.removeAllRanges();findNativeSelection=false;}
 globalThis.CSS?.highlights?.delete('mesa-find-all');globalThis.CSS?.highlights?.delete('mesa-find-current');
}
function findInDocument(m){
 if(togglePanel('Buscar no documento'))return;
 if(m.mode==='edit'){toast('Para buscar no editor, use o comando de busca do CodeMirror. Para percorrer a leitura, escolha Leitura ou Estudo.');return;}
 const blocks=[...content.querySelectorAll('[data-unit],[data-comparison-unit]')];
 if(!blocks.length){toast('Abra o texto para buscar nesta visualização.');return;}
 m.findState||={query:'',lang:'',caseSensitive:false,index:0};
 const state=m.findState,input=n('input',{type:'search',placeholder:'Nome, palavra ou frase…','aria-label':'Buscar neste documento',class:'document-find-input'});input.value=state.query;
 const langs=[...new Set(blocks.map(block=>block.closest('[lang]')?.lang).filter(Boolean))];
 const lang=select([['','Todos os idiomas desta visualização'],...langs.map(code=>[code,(code===m.lang?'Texto principal · ':m.mode==='paragraphs'?'Tradução por trecho · ':'Comparação · ')+(LANGUAGES[code]||code)])],langs.includes(state.lang)?state.lang:'',()=>run(),'Idioma da busca');
 const sensitive=n('input',{type:'checkbox'});sensitive.checked=Boolean(state.caseSensitive);
 const status=n('p',{class:'find-count',role:'status','aria-live':'polite'}),list=n('div',{class:'find-results'}),previous=button('← Anterior',()=>move(-1),'quiet'),next=button('Próxima →',()=>move(1),'quiet');
 let matches=[],timer,ranges=[];
 function run(preserveIndex=false){
   if(!input.isConnected||panelName!=='Buscar no documento'||current()!==m)return;
   clearTimeout(timer);timer=null;clearFindHighlights();const oldIndex=state.index;state.query=input.value;state.lang=lang.value;state.caseSensitive=sensitive.checked;state.index=preserveIndex?oldIndex:0;matches=[];ranges=[];
   if(input.value.length<2){list.replaceChildren();status.textContent='Digite pelo menos dois caracteres. A busca examina o texto desta visualização, incluindo traduções recolhidas.';previous.disabled=next.disabled=true;queueSession();return;}
   for(const block of blocks){
     const code=block.closest('[lang]')?.lang||m.lang;if(lang.value&&lang.value!==code)continue;
     const text=block.textContent;
     for(const match of literalMatches(text,input.value,{caseSensitive:sensitive.checked,limit:500-matches.length}))matches.push({block,lang:code,text,...match});
     if(matches.length>=500)break;
   }
   if(globalThis.CSS?.highlights&&globalThis.Highlight){ranges=matches.map(match=>rangeForText(match.block,match.start,match.end)).filter(Boolean);CSS.highlights.set('mesa-find-all',new Highlight(...ranges));}
   show(false);queueSession();
 }
 function show(scroll){
   if(!matches.length){status.textContent='Nenhuma ocorrência nesta visualização.';list.replaceChildren();previous.disabled=next.disabled=true;return;}
   previous.disabled=next.disabled=false;state.index=(state.index+matches.length)%matches.length;
   const match=matches[state.index],details=match.block.closest('details'),wasClosed=Boolean(details&&!details.open);
   if(scroll&&wasClosed)details.open=true;
   status.textContent=`${state.index+1} de ${matches.length} ocorrências${matches.length===500?' · limite atingido; refine a busca':''}`+(scroll&&details?` · Tradução em ${LANGUAGES[match.lang]||match.lang} aberta.`:'');
   const page=Math.floor(state.index/40)*40;list.replaceChildren();
   matches.slice(page,page+40).forEach((item,offset)=>{
     const index=page+offset,translation=item.block.closest('details'),closed=Boolean(translation&&!translation.open),context=item.text.slice(Math.max(0,item.start-55),Math.min(item.text.length,item.end+75));
     const location=translation?(closed?'Tradução recolhida':'Tradução aberta'):(item.lang===m.lang?'Texto principal':'Comparação');
     const result=b('',()=>{state.index=index;show(true);},'find-result'+(index===state.index?' active':''));
     result.append(n('span',{text:`${index+1} · ${LANGUAGES[item.lang]||item.lang} · ${location}`}),n('p',{text:context}),n('span',{class:'find-result-action',text:closed?'Abrir tradução e mostrar ocorrência →':'Mostrar ocorrência no texto →'}));
     list.append(result);
   });
   if(!scroll)return;
   const range=rangeForText(match.block,match.start,match.end);if(!range)return;
   if(globalThis.CSS?.highlights&&globalThis.Highlight)CSS.highlights.set('mesa-find-current',new Highlight(range));
   else{automaticTextSelection=true;findNativeSelection=true;const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);}
   const viewport=match.block.closest('.document-scroll'),rect=range.getBoundingClientRect();
   if(viewport)viewport.scrollTo({top:viewport.scrollTop+rect.top-viewport.getBoundingClientRect().top-viewport.clientHeight/2,behavior:'smooth'});
   queueSession();
 }
 function move(step){if(!matches.length)return;state.index+=step;show(true);}
 input.oninput=()=>{clearTimeout(timer);timer=setTimeout(run,180);};input.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();if(timer){clearTimeout(timer);run();show(true);}else move(event.shiftKey?-1:1);}};
 sensitive.onchange=()=>run();
 panel('Buscar no documento',[input,lang,n('p',{class:'find-guidance',text:m.mode==='paragraphs'?'A busca inclui traduções recolhidas. Nos resultados, clique em Abrir tradução e mostrar ocorrência: o trecho será expandido no próprio documento.':'Clique num resultado para ir à ocorrência. Para pesquisar traduções recolhidas, use Estudo por trecho e escolha o segundo idioma no cabeçalho.'}),n('label',{class:'find-case'},[sensitive,n('span',{text:'Diferenciar maiúsculas e minúsculas'})]),n('div',{class:'find-navigation'},[previous,next]),status,list]);run(true);input.focus();
}
async function editorView(m, data, version) {
    const area = n('div', { class: 'editor-grid' }), left = n('div', { class: 'editor-pane code-host' }), right = n('div', { class: 'editor-preview edition-body' });
    area.append(left, right);
    content.append(area);
    let value = data.body;
    const textarea = n('textarea', { class: 'plain-editor', 'aria-label': 'Markdown do rascunho', spellcheck: 'false' });
    textarea.value = value;
    left.append(textarea);
    const show = value => { right.innerHTML = renderMarkdown(value); };
    show(value);controls.append(n('span',{class:'editor-state',text:'Edição não gravada',title:m.projectId?'Edição privada. Conferir alterações prepara uma gravação somente no projeto.':'Sem gravação automática. Confira o destino antes de confirmar: sessão ou acervo local.'}));
    textarea.oninput = () => { value = textarea.value; show(value);queueSession(); };
    const editorKey = draftKey(m);
    m.buffers ||= {};
    m.capture=()=>{if(value!==data.body){m.buffers[editorKey]=value;if(m.projectId){m.projectBases||={};m.projectBases[editorKey]||={revision:m.projectSnapshots[m.lang].revision,content_sha256:m.projectSnapshots[m.lang].content_sha256};}}else{delete m.buffers[editorKey];delete m.projectBases?.[editorKey];}};
    if (m.buffers[editorKey] !== undefined) {
        value = m.buffers[editorKey];
        textarea.value = value;
        show(value);
    }
    controls.append(button('Conferir alterações',()=>{
      remember();const submitted=value;
      if(m.projectId){const snapshot=m.projectSnapshots[m.lang];saveWorkspace(projectEnvironment(generation,m),m,snapshot,submitted).catch(error=>toast(error.message));return;}
      const sessionProposal={title:'Conferir edição Markdown',before:data.body,after:submitted,confirm:()=>{
        const key=draftKey(m);record('markdown',key,saved.drafts[key]??data.body);saved.drafts[key]=submitted;delete m.buffers[key];m.capture=null;m.showCanonical=false;persist();m.mode='read';render();toast('Rascunho guardado na sessão; acervo preservado.');
      }};
      if(backendAvailable&&!m.projectId&&m.backendSnapshot&&saved.scope==='acervo'){
        const destination={session:sessionProposal,prepare:async()=>{
          const token=generation;
          const proposal=await editorialRequest('/api/editorial/markdown/preview',{body:markdownPayload(m.backendSnapshot,submitted)});
          if(token!==generation)return;
          backendPreview(m,proposal,m.lang,destination);
        }};
        sessionProposal.destination=destination;
      }
      previewChange(sessionProposal);
    },'primary'));

    try {
        const lib = await import('../oficina/vendor/libraries.js');
        if (version !== generation)
            return;
        const view = new lib.EditorView({ doc: value, extensions: [lib.basicSetup, lib.markdown(), lib.EditorView.updateListener.of(update => { if (update.docChanged) {
                    value = update.state.doc.toString();
                    show(value);queueSession();
                } })], parent: left });
        textarea.remove();activeMarkdownEditor=view;
        cleanup = () => {if(activeMarkdownEditor===view)activeMarkdownEditor=null;view.destroy();};
    }
    catch {
        toast('Editor simples ativo; a prévia Markdown continua disponível.');
    }
}
function record(kind, key, before) { saved.history.unshift({ kind, key, before, time: new Date().toISOString() }); saved.history = saved.history.slice(0, 40); }
function previewChange(change) { remember(); preview = change; showPreview(); }
function showPreview(){
 ++generation;cleanup();cleanup=()=>{};closePanel();document.body.classList.add('working');controls.replaceChildren();content.replaceChildren();if(globalKeyboardOpen)describeKeyboardTarget();
 const proposal=preview,real=Boolean(proposal.backend),check=n('input',{type:'checkbox'}),warnings=n('input',{type:'checkbox'}),notice=n('p',{class:'review-status',role:'status'});previewWarningsAccepted=false;
 const cancel=button(real?'Voltar sem gravar':'Voltar à edição',()=>{preview=null;render();},'quiet');
 const save=button(proposal.saveLabel||(real?'Confirmar gravação no acervo':'Guardar na sessão'),async()=>{
  if(!check.checked||proposal.proposal?.requires_acknowledgement&&!warnings.checked)return;
  save.disabled=true;cancel.disabled=true;if(real){document.body.classList.add('backend-saving');document.querySelectorAll('.global-controls button').forEach(button=>button.disabled=true);}previewWarningsAccepted=warnings.checked;notice.textContent=proposal.destinationText?'Concluindo operação local. Aguarde…':real?'Gravando no acervo local. Aguarde…':'Guardando rascunho…';
  try{if(!real)preview=null;await proposal.confirm();if(preview===proposal)preview=null;}catch(error){notice.textContent=error.message+' O rascunho foi preservado. Confira o histórico antes de repetir uma gravação interrompida.';save.disabled=true;cancel.disabled=false;}finally{document.body.classList.remove('backend-saving');document.querySelectorAll('.global-controls button').forEach(button=>button.disabled=false);}
 },'primary');save.disabled=true;
 const ready=()=>save.disabled=!check.checked||Boolean(proposal.proposal?.requires_acknowledgement&&!warnings.checked);check.onchange=ready;warnings.onchange=ready;
 controls.append(n('span',{class:'editor-state',text:proposal.destinationText|| (real?'Conferência · acervo local':'Conferência · rascunho da sessão')}));
 let destinationControl=n('span',{class:'review-destination',text:proposal.destinationText||(real?'Acervo local':'Sessão do navegador')});
 if(proposal.destination){
  const choose=select([['session','Rascunho da sessão'],['acervo','Acervo local · gravação com histórico']],real?'acervo':'session',async value=>{
    if(value==='session'){preview=proposal.destination.session;showPreview();return;}
    choose.disabled=true;notice.textContent='Preparando a prévia do acervo; nada foi gravado.';
    try{await proposal.destination.prepare();}catch(error){choose.value='session';choose.disabled=false;notice.textContent=error.message;}
  },'Destino da alteração');
  destinationControl=n('label',{class:'review-destination-choice'},[n('span',{text:'Destino:'}),choose]);
 }
 const detail=proposal.proposal?.translation,markdown=proposal.proposal?.markdown_edit;
 const diff=detail?.diff?.text||markdown?.diff?.text||(proposal.proposal?.file_diffs?.length?proposal.proposal.file_diffs.map(file=>file.file+'\n'+file.diff.text).join('\n\n'):null);
 const area=n('div',{class:'review-content'}),tabbar=n('div',{class:'review-tabs',role:'tablist','aria-label':'Conferência da alteração'}),buttons=[];
 const textOnly=Boolean(detail||markdown)||(!real&&/Markdown/.test(proposal.title)),renderChoice=n('input',{type:'checkbox'});renderChoice.checked=textOnly;
 function showTab(name){
  buttons.forEach(([key,button])=>{button.classList.toggle('active',key===name);button.setAttribute('aria-selected',String(key===name));});area.replaceChildren();
  if(name==='content'&&proposal.renderContent){area.append(proposal.renderContent());return;}
  if(name==='content'&&proposal.propertyRows){
   const table=n('table',{class:'property-comparison'},[n('thead',{},[n('tr',{},['Propriedade','Antes','Proposta'].map(text=>n('th',{text})))]),n('tbody')]);
   for(const row of proposal.propertyRows)table.lastChild.append(n('tr',{},[n('th',{text:row.field}),n('td',{text:row.before??'—'}),n('td',{text:row.after??'—'})]));
   area.append(n('div',{class:'property-comparison-scroll'},[table]));return;
  }
  if(name==='content'){
   const columns=n('div',{class:'review-columns'}),bodyBefore=window.splitExportHeaders?.(proposal.before||'').body??proposal.before,bodyAfter=window.splitExportHeaders?.(proposal.after||'').body??proposal.after;
   const draw=()=>{columns.replaceChildren();for(const [title,value]of [['Versão anterior',bodyBefore],['Versão proposta',bodyAfter]]){
     const body=n('div',{class:renderChoice.checked?'review-edition edition-body':'review-raw'});
     if(renderChoice.checked)body.innerHTML=renderMarkdown(value||'');else body.append(n('pre',{text:value||'Sem versão anterior.'}));
     columns.append(n('section',{class:'review-column'},[n('h2',{text:title}),body]));
   }};renderChoice.onchange=draw;
   if(textOnly)area.append(n('label',{class:'review-view-choice'},[renderChoice,n('span',{text:'Prévia renderizada do Markdown'})]));
   area.append(columns);draw();
  }else if(name==='context'){area.append(n('section',{class:'review-details'},[n('h2',{text:'Informações da operação'}),...(proposal.information||[]).map(([title,value])=>n('div',{class:'review-info'},[n('strong',{text:title}),n('p',{text:String(value??'—')})]))]));}
  else if(name==='diff')area.append(n('section',{class:'review-details'},[n('h2',{text:'Diferenças no texto'}),n('pre',{class:'review-diff',text:diff||'Confira as versões lado a lado.'})]));
  else if(name==='diagnostic'){
   const section=n('section',{class:'review-details'},[n('h2',{text:'Identificação e estrutura'})]);
   for(const item of detail.findings)section.append(n('p',{class:item.level==='warning'?'backend-warning':'review-info',text:item.message}));
   const table=n('table',{class:'structure-table'},[n('thead',{},[n('tr',{},['Estrutura','Original','Versão atual','Arquivo enviado'].map(text=>n('th',{text})))]),n('tbody')]);
   for(const [key,title]of Object.entries({study_blocks:'Blocos',paragraphs:'Parágrafos',headings:'Títulos',lists:'Listas',tables:'Tabelas',export_headers:'Cabeçalhos de exportação'}))table.lastChild.append(n('tr',{},[n('th',{text:title}),...['original','current','uploaded'].map(name=>n('td',{text:detail.structure[name]?.[key]??'—'}))]));
   section.append(table,n('p',{class:'hint',text:'A contagem é diagnóstica: não certifica pareamento automático entre parágrafos.'}));area.append(section);
  }else{
   const files=[...new Set([detail?.target_file,markdown?.file,...(proposal.proposal?.file_diffs||[]).map(file=>file.file)].filter(Boolean))];
   area.append(n('section',{class:'review-details'},[n('h2',{text:'Efeito da gravação'}),n('p',{text:proposal.effectText||(real?'O backend preserva a versão anterior no histórico e atualiza catálogo, manifesto e busca quando necessário. Não há publicação automática.':'Apenas a sessão do navegador será alterada. O acervo permanece intacto.')}),...files.map(file=>n('p',{},[n('code',{text:file})])),...(proposal.proposal?.changes||[]).map(change=>n('div',{class:'review-change'},[n('strong',{text:change.field}),n('pre',{text:JSON.stringify({antes:change.before,depois:change.after},null,2)})]))]));
  }
 }
 for(const [key,title]of [['content','Conteúdo'],...(diff?[['diff','Diferenças']]:[]),...(proposal.information?[['context','Informações']]:[]),...(detail?[['diagnostic','Identificação'+(proposal.proposal.requires_acknowledgement?' · avisos':'')]]:[]),['effect','Efeito da gravação']]){
  const button=b(title,()=>showTab(key),'review-tab',{role:'tab','aria-selected':'false'});buttons.push([key,button]);tabbar.append(button);
 }
 const confirmations=n('div',{class:'review-confirmations'},[
  n('label',{},[check,n('span',{text:proposal.confirmText||(real?'Confirmo alterar o acervo local, com histórico e sem publicação automática.':'Confirmo guardar apenas na sessão, sem modificar o acervo.')})]),
  proposal.proposal?.requires_acknowledgement&&n('label',{class:'review-warning-confirmation'},[warnings,n('span',{text:proposal.ackText||'Li os avisos em Identificação e confirmo o documento e o idioma selecionados.'})]),notice
 ]);
 content.append(n('section',{class:'review-workspace'},[
  n('header',{class:'review-heading'},[n('h1',{text:proposal.title}),destinationControl]),tabbar,area,
  n('footer',{class:'review-footer'},[confirmations,n('div',{class:'review-actions'},[cancel,save])])
 ]));showTab('content');tabs();
}
function changeTitle() { return preview?.title || 'Conferir alterações'; }
function historyPanel() { panel('Histórico recuperável', [n('p', { text: 'Versões anteriores dos rascunhos desta sessão.' }), ...saved.history.map((entry, index) => n('div', { class: 'note-card' }, [n('p', { text: `${entry.kind} · ${entry.key} · ${new Date(entry.time).toLocaleString('pt-BR')}` }), button('Restaurar como rascunho', () => { if (entry.kind === 'markdown')
            saved.drafts[entry.key] = entry.before;
        else if (entry.kind === 'metadata')
            saved.metadata[entry.key] = entry.before;
        else if (entry.kind === 'page')
            saved.pages[entry.key] = entry.before;
        else if(entry.kind==='note'){const list=saved.notes[entry.key]||=[];const index=list.findIndex(note=>note.id===entry.before.id);if(index<0)list.push(entry.before);else list[index]=entry.before;} persist(); closePanel(); render(); toast('Versão restaurada no piloto.'); }, 'quiet')])), button('Exportar sessão', exportSession)]); }
function draftsPanel(){
 remember();persist();
 const entries=[];
 for(const [key,text] of Object.entries(saved.drafts)){
   const parts=key.split(':'),scope=parts.shift(),lang=parts.pop(),id=parts.join(':'),doc=catalog.documents.get(id);
   if(!doc)continue;
   entries.push(n('div',{class:'note-card'},[n('strong',{text:label(doc)}),n('p',{text:`${LANGUAGES[lang]||lang} · ${scope==='acervo'?'Mesa principal':scope.startsWith('project-')?'Projeto local':'Caderno experimental'} · rascunho confirmado na sessão`}),button('Abrir rascunho',async()=>{try{if(scope.startsWith('project-')){const project=await editorialRequest('/api/editorial/projects/'+scope);openDocument(doc,project);}else{saved.scope=scope;openDocument(doc);}updateScope();const m=current();m.lang=lang;m.mode='edit';render();}catch(error){toast(error.message);}},'quiet')]));
 }
 for(const m of materials.filter(m=>pendingCount(m)))entries.push(n('div',{class:'note-card'},[n('strong',{text:m.doc?label(m.doc):m.title}),n('p',{text:`${pendingCount(m)} alterações ainda não confirmadas`}),button('Retomar trabalho',()=>{active=m.key;closePanel();navigate('mesa');},'quiet')]));
 panel('Rascunhos e recuperação',[n('p',{text:'Confirmado significa guardado nesta sessão, não publicado. Alterações em andamento também são recuperadas ao recarregar a mesma aba.'}),...entries,!entries.length&&n('p',{text:'Ainda não há rascunhos de texto ou alterações em andamento.'}),button('Exportar cópia da sessão',exportSession),button('Restaurar cópia exportada',importSession)]);
}
function exportSession(){remember();persist();download('mesa-piloto-sessao.json',JSON.stringify(saved,null,2),'application/json');}
function importSession(){
 const input=n('input',{type:'file',accept:'.json,application/json'});
 input.onchange=async()=>{try{
  const file=input.files[0];if(!file)return;if(file.size>12*1024*1024)throw Error('Escolha uma cópia de até 12 MB.');
  const value=JSON.parse(await file.text());
  if(!value||typeof value!=='object'||Array.isArray(value)||!value.workspace||value.workspace.version!==1||!value.drafts||typeof value.drafts!=='object')throw Error('Este arquivo não é uma cópia compatível da Mesa.');
  const restored=restoreDesk(value.workspace,catalog);
  dialog('Restaurar uma cópia da mesa',[n('p',{text:`A cópia contém ${restored.materials.length} materiais reconhecidos e ${Object.keys(value.drafts).length} rascunhos de texto. Ela substituirá a sessão do piloto; o acervo não será alterado. Uma cópia da sessão atual será baixada antes da substituição.`}),button('Exportar sessão atual antes de substituir',exportSession),button('Substituir sessão do piloto',()=>{
   remember();persist();const previous=JSON.stringify(saved);download('mesa-anterior-restauracao.json',previous,'application/json');
   saved={...value,scope:'acervo',history:Array.isArray(value.history)?value.history:[],markers:value.markers||{},metadata:value.metadata||{},notes:value.notes||{},pages:value.pages||{},catalogWork:value.catalogWork||{},noteWork:value.noteWork||{},noteTrash:Array.isArray(value.noteTrash)?value.noteTrash:[],organizationWork:value.organizationWork||{}};
   materials=restored.materials;active=restored.active;Object.assign(libraryState,restored.library);persist();
   
   updateScope();$('#dialog').close();closePanel();navigate('mesa');toast('Cópia restaurada no piloto. PDFs do computador devem ser selecionados novamente.');
  },'primary')]);
 }catch(error){toast('Não foi possível restaurar: '+error.message);}};input.click();
}
function openSource(link) { if(link.local){openBackendSource(link.source_id,current()?.project||null);return;}remember(); const key = 'pdf:' + (link.source_id || link.pdf_url); let m = materials.find(x => x.key === key); if (!m) {
    m = { key, kind: 'pdf', title: link.source_title || 'Fac-símile', pdfUrl: link.pdf_url, page: Number(link.pages?.[0]) || 1, count: 0, scopeNote: link.source_scope_note || '' };
    materials.push(m);
} active = key; closePanel(); navigate('mesa'); }
function localPdf(file) { if (!file)
    return; remember(); const key = 'upload:' + file.name + ':' + file.size+(projectContext?'@'+projectContext.id:''); let m = materials.find(x => x.key === key); if (!m) {
    m = { key, kind: 'pdf', title: file.name, file, page: 1, count: 0,project:projectContext,projectId:projectContext?.id||null };
    materials.push(m);
} m.file=file;m.filename=file.name;m.filesize=file.size;m.needsFile=false;active = key; closePanel(); navigate('mesa'); }
function pickPdf() { const input = n('input', { type: 'file', accept: 'application/pdf,.pdf' }); input.onchange = () => localPdf(input.files[0]); input.click(); }
async function openBackendSource(id,project=null,focus=null){
 remember();const token=generation;
 try{const info=await editorialRequest('/api/editorial/pdf/'+encodeURIComponent(id));if(token!==generation)return;if(project){project=await editorialRequest('/api/editorial/projects/'+project.id);if(token!==generation)return;if(!project.source_ids.includes(id))throw Error('Esta fonte não está vinculada ao projeto.');}const key='source:'+id+(project?'@'+project.id:'');let m=materials.find(item=>item.key===key);if(!m){m={key,kind:'pdf',backendSource:id,pdfUrl:sourceFile(id),page:info.last_page||1,title:info.metadata?.title||info.filename,count:info.page_count||0};materials.push(m);}m.project=project;m.projectId=project?.id||null;if(focus){m.page=focus.page;m.openRegionEditor=true;m.regionUnitId=focus.unitId;m.regionTask='regions';m.associationReturn=focus.returnTo;}projectContext=project;updateScope();m.needsFile=false;active=key;closePanel();navigate('mesa');}catch(error){toast(error.message);}
}
function pdfEnvironment(version,m=null){
 const project=m?m.project:projectContext;
 return {project,projectId:project?.id||'',backToAssociation:()=>returnToAssociation(m),alignPage:()=>alignPage(parityEnvironment(m),m),content,controls,catalog,button,select,heading,toast,dialog,closeDialog:()=>$('#dialog').close(),saved,canWrite:backendAvailable&&saved.scope==='acervo'&&!project?.archived,current:()=>generation===version&&(!m||current()===m),remember,store:queueSession,panel,togglePanel,preview:proposal=>{if(!(backendAvailable&&saved.scope==='acervo')||project?.archived){toast('Reabra o projeto ou escolha Mesa principal para confirmar operações reais na fonte.');return;}previewChange(proposal);},acknowledged:()=>previewWarningsAccepted,rerender:()=>render(),updated:tabs,open:id=>openBackendSource(id,project),
  back:async source=>{preview=null;active=source.key;persist();if(location.hash==='#mesa')await render();else navigate('mesa');},
  refreshFacsimiles:async()=>{catalog=await loadCatalog();},
  openDocument:async(id,language,activity)=>{clearEditionCache();catalog=await loadCatalog();const doc=catalog.documents.get(id);if(!doc){toast('O documento não está no catálogo atual. Confira seu histórico.');return;}openDocument(doc,project);if(language)current().lang=language;if(activity)current().mode=activity;render();},
  incorporated:async(source,receipt,language)=>{
   preview=null;if(receipt.warning)source.pendingIncorporation=receipt.receipt_id;saved.lastPDFReceipt={receipt_id:receipt.receipt_id,document_id:receipt.document_id,warning:receipt.warning||'',time:new Date().toISOString()};persist();
   try{clearEditionCache();catalog=await loadCatalog();for(const material of materials)if(material.kind==='document'&&catalog.documents.has(material.doc.id))material.doc=catalog.documents.get(material.doc.id);const doc=catalog.documents.get(receipt.document_id);if(doc){openDocument(doc);current().lang=language;render();}}
   catch(error){content.replaceChildren(n('section',{class:'page-shell'},[heading('Gravação concluída','Documento salvo.',`Recibo ${receipt.receipt_id}. Recarregue e consulte as incorporações da fonte; não repita a criação.`)]));}
   if(receipt.warning)toast(receipt.warning+' · O texto já foi salvo. Não repita a criação.');else toast('Documento criado no acervo local com proveniência. Nenhum commit ou publicação foi realizado.');

  }
 };
}
async function pdfView(m, version) {
    if(m.backendSource&&backendAvailable){if(m.projectId){m.project=await editorialRequest('/api/editorial/projects/'+m.projectId);if(version!==generation)return;if(!m.project.source_ids.includes(m.backendSource))throw Error('Esta fonte deixou de pertencer ao projeto. Abra-a fora do projeto em Fontes PDF.');projectContext=m.project;updateScope();}const release=await sourceView(pdfEnvironment(version,m),m);if(version===generation)cleanup=release;else release?.();return;}
    if(m.needsFile){content.append(n('section',{class:'empty-desk'},[n('p',{class:'eyebrow',text:'Fonte preservada na mesa'}),n('h1',{text:m.title}),n('p',{text:`Reabra ${m.filename} para visualizar a imagem. A página ${m.page}, as transcrições e os rascunhos foram mantidos; o navegador não guarda o PDF enviado.`}),button('Selecionar novamente o PDF',pickPdf,'primary')]));return;}
    const area = n('section', { class: 'review-grid' }), image = n('div', { class: 'pdf-stage' }), transcript = n('div', { class: 'transcript' }), input = n('textarea', { 'aria-label': 'Transcrição da página', placeholder: 'Extraia a camada de texto ou escreva uma transcrição. O OCR não é executado neste piloto.', spellcheck: 'false' });
    const key = () => `${saved.scope || 'acervo'}:${m.key}:${m.page}`;
    let text = m.pageUnsaved?.[key()] ?? saved.pages[key()]?.text ?? '';
    input.value = text;
    input.oninput = () => { text = input.value; (m.pageUnsaved ||= {})[key()] = text;queueSession(); };
    const status = n('p', { class: 'transcript-status', text: saved.pages[key()]?.reviewed ? 'Conferida no piloto' : 'Transcrição de trabalho · página física ' + m.page });
    const keyboardDock=n('div',{class:'transcription-keyboard',hidden:true});
    const keyboardButton=button('Teclado russo',()=>showKeyboard(!m.keyboardOpen),'quiet');
    async function showKeyboard(open){
        if(open)setGlobalKeyboard(false);m.keyboardOpen=open;keyboardDock.hidden=!open;
        keyboardButton.setAttribute('aria-expanded',String(open));
        if(!open)return;
        if(keyboardDock.childElementCount)return;
        const {russianKeyboard}=await import('../estudio/russian-keyboard.js');
        if(version!==generation)return;
        const keyboard=russianKeyboard({
          write:t=>{input.setRangeText(t,input.selectionStart,input.selectionEnd,'end');input.dispatchEvent(new Event('input'));input.focus();},
          erase:()=>{const start=input.selectionStart;input.setRangeText('',input.selectionStart===input.selectionEnd?Math.max(0,start-1):start,input.selectionEnd,'end');input.dispatchEvent(new Event('input'));input.focus();},locked:()=>false
        });
        keyboard.open=true;
        keyboardDock.append(n('div',{class:'keyboard-dock-heading'},[n('span',{text:'Teclado · Русский'}),button('Recolher',()=>showKeyboard(false),'quiet')]),keyboard);
    }
    transcript.append(n('div',{class:'column-label'},[n('strong',{text:'Transcrição'}),keyboardButton]),status,input,keyboardDock);
    showKeyboard(Boolean(m.keyboardOpen));
    const imagePane=n('section',{class:'pdf-image-pane'},[n('div',{class:'image-zoom-bar'},[zoomControls(m,()=>cleanup.refresh?.(),queueSession)]),image]);area.append(imagePane,transcript);installSplitter(area,m,queueSession);content.append(area);
    const page = n('input', { type: 'number', min: 1, value: m.page, 'aria-label': 'Página física', class: 'review-page-input' });
    const turn = value => { if (value < 1 || m.count && value > m.count)
        return; m.page = value; render(); };
    page.onchange = () => turn(Number(page.value));
    const count = n('span', { class: 'page-count', text: '/ …' });
    controls.replaceChildren(button('‹', () => turn(m.page - 1), 'quiet'), page, count, button('›', () => turn(m.page + 1), 'quiet'), button('Extrair texto', async () => { const selected = m.page; try {
        toast('Lendo a camada textual…');
        const value = await pageText(m, selected);
        if (version !== generation || selected !== m.page)
            return;
        if (!value) {
            toast('Página sem texto pesquisável. Prepare o OCR nas ferramentas; ele não é executado neste piloto.');
            return;
        }
        if (text.trim() && !confirm('Substituir a transcrição de trabalho pela extração? O texto salvo na sessão será preservado.'))
            return;
        text = value;
        input.value = value;
        (m.pageUnsaved ||= {})[key()] = value;
        status.textContent = 'Extração nativa · confira contra a imagem';queueSession();
    }
    catch (e) {
        toast(e.message);
    } }), button('Conferir e salvar', () => { const reviewed = n('input', { type: 'checkbox' }); dialog('Situação da página', [n('label', {}, [reviewed, n('span', { text: 'Conferi a transcrição com a imagem' })]), button('Ver prévia', () => { $('#dialog').close(); previewChange({ title: `Página ${m.page} · conferir transcrição`, before: saved.pages[key()]?.text || '', after: text, confirm: () => { record('page', key(), saved.pages[key()] || { text: '', reviewed: false }); saved.pages[key()] = { text, reviewed: reviewed.checked }; delete m.pageUnsaved?.[key()]; persist(); render(); toast('Página guardada na sessão do piloto.'); } }); }, 'primary')]); }, 'primary'), button('⋯', () => pdfTools(m), 'quiet'));
    cleanup = mountPdf(m, image, total => { count.textContent = '/ ' + total; page.max = total; }, e => toast(e.message));
}
function registerPdfForOCR(m){
 if(!backendAvailable||!m.file){toast('Use Fontes PDF → Cadastrar PDF para iniciar uma revisão persistente.');return;}
 dialog('Cadastrar cópia da fonte para OCR',[
  n('p',{text:m.file.name+' será preservado no armazenamento local do backend. O cadastro inicia a extração nativa; OCR é preparado depois. Nenhum documento é publicado nesta ação.'}),
  button('Confirmar cadastro local',async event=>{const button=event.currentTarget;button.disabled=true;try{const result=await uploadPdfSource(m.file,m.projectId||projectContext?.id||'',percent=>toast('Enviando PDF · '+percent+'%'));$('#dialog').close();await openBackendSource(result.source_id,m.project||projectContext);}catch(error){toast(error.message);event.currentTarget.disabled=false;}},'primary')
 ]);
}
function pdfTools(m){
 if(togglePanel('Fonte e revisão'))return;
 panel('Fonte e revisão',[
  n('p',{class:'menu-context',text:m.title}),
  menuGroup('Visualizar',[
   {title:'Página inteira',description:'Ajustar a imagem ao espaço disponível.',run:()=>{m.zoom='fit';closePanel();render();}},
   {title:'Ajustar à largura',description:'Ampliar a imagem usando a largura do painel.',run:()=>{m.zoom='width';closePanel();render();}}
  ]),
  menuGroup('Trabalhar com a fonte',[
   backendAvailable&&m.file&&{title:'Cadastrar para OCR',description:'Preservar no backend e iniciar uma revisão persistente.',run:()=>registerPdfForOCR(m)},
   {title:'Fontes PDF e OCR',description:'Abrir as fontes cadastradas no backend local.',disabled:!backendAvailable,run:()=>{closePanel();navigate('fontes');}},
   {title:'Histórico dos rascunhos',description:'Revisões temporárias desta sessão.',run:historyPanel}
  ]),
  menuGroup('Exportar',[
   {title:'Baixar transcrições da sessão',description:'Exportar as páginas trabalhadas neste navegador.',download:true,run:()=>download('transcricoes-piloto.json',JSON.stringify(Object.fromEntries(Object.entries(saved.pages).filter(([key])=>key.startsWith((saved.scope||'acervo')+':'+m.key+':'))),null,2),'application/json')}
  ]),n('p',{class:'hint',text:'PDF temporário: estas revisões ficam na sessão. O cadastro no backend é uma ação separada.'})
 ]);
}
function passageEnvironment(version,m){
 return {content,controls,button,heading,toast,store:queueSession,current:()=>generation===version&&current()===m,preview:previewChange,
 openPassage:material=>{remember();material.capture=null;material.mode='correct-passage';persist();render();},
 returnPassage:material=>{material.capture=null;material.mode=material.passageWork?.returnMode||'read';persist();render();},
 setPassageEditor:editor=>{activeMarkdownEditor=editor;},
 finishPassage:async material=>{preview=null;const work=material.passageWork,receipt=material.lastPassageReceipt;saved.lastPassageReceipt={...receipt,document_id:material.doc.id,project_id:material.projectId||'',time:new Date().toISOString()};persist();
  try{if(!material.projectId){clearEditionCache();catalog=await loadCatalog();for(const item of materials)if(item.kind==='document'&&!item.projectId&&catalog.documents.has(item.doc.id))item.doc=catalog.documents.get(item.doc.id);}
   material.mode=work.returnMode||'read';material.passageWork=null;material.capture=null;persist();await render();toast(material.projectId?'Trecho corrigido na versão privada. Acervo preservado.':'Tradução corrigida com histórico. Original e outras versões preservados.');
  }catch(error){content.replaceChildren(n('section',{class:'page-shell'},[heading('Correção salva','Gravação concluída.',`Registro ${receipt.history_id}. Recarregue para atualizar a leitura; não repita a gravação.`)]));}
 }
 };
}
async function returnToAssociation(source){
 const destination=source?.associationReturn,material=materials.find(item=>item.key===destination?.documentKey);
 if(!material){toast('A aba do documento foi fechada. Reabra o documento para consultar suas associações.');return;}
 remember();active=material.key;projectContext=material.project||null;preview=null;closePanel();await render();
 if(current()!==material)return;
 await editAssociation(parityEnvironment(material),material,destination.linkId,destination.anchorId);
}
function parityEnvironment(m){const version=generation;return {button,select,toast,dialog,closeDialog:()=>$('#dialog').close(),panel,current:()=>version===generation&&current()===m,body:lang=>bodyFor(m,lang),preview:proposal=>{$('#dialog').close();previewChange(proposal);},saved:async()=>{preview=null;await render();toast('Associação ou estrutura salva com histórico.');},openRegions:(link,anchor)=>{closePanel();openBackendSource(link.source_id,m.project||null,{page:anchor.page_number,unitId:anchor.unit_id,returnTo:{documentKey:m.key,linkId:link.id,anchorId:anchor.id}});},openAnchor:(link,anchor)=>{remember();if(['read','paragraphs','parallel'].includes(m.mode))m.facsimileReturnMode=m.mode;if(m.doc.languages.some(e=>e.code===anchor.language))m.lang=anchor.language;m.mode='facsimile';m.facsimile={source:link.id,page:anchor.page_number,anchor};closePanel();render();}};}
function projectEnvironment(version,m=null){
 return {...organizationEnvironment(version),panel,preview:previewChange,acknowledged:()=>previewWarningsAccepted,
 openProjectDocument:(project,doc)=>openDocument(doc,project),
 openSource:(id,project)=>{openBackendSource(id,project);toast('Contexto do projeto preservado. A revisão OCR da fonte é compartilhada.');},
 enterProject:project=>{projectContext=project;updateScope();projectMaterials(projectEnvironment(generation),project.id);},
 leaveProject:()=>{projectContext=null;updateScope();navigate('biblioteca');},
 finishProject:id=>{preview=null;persist();if(projectContext?.id===id)projectContext=null;updateScope();navigate('projetos/'+id);toast('Organização do projeto salva com histórico. O acervo não mudou.');},
 refreshCatalog:async()=>{clearEditionCache();catalog=await loadCatalog();for(const material of materials)if(material.kind==='document'&&!material.projectId&&catalog.documents.has(material.doc.id))material.doc=catalog.documents.get(material.doc.id);},
 finishWorkspace:(material,language)=>{const key=material.projectId+':'+material.doc.id+':'+language;delete material.buffers?.[key];delete material.projectBases?.[key];delete saved.drafts[key];material.translationWork=null;material.lang=language;material.capture=null;material.showCanonical=false;material.mode=material.returnMode||'read';material.backendSnapshot=null;preview=null;persist();render();toast('Operação concluída. Você continua na versão do projeto.');}
 };
}
function organizationEnvironment(version){
 return {content,controls,button,field,select,heading,catalog,saved,work:saved.organizationWork,canWrite:backendAvailable&&saved.scope==='acervo',current:()=>generation===version,generation:()=>generation,navigate,open:openDocument,preview:previewChange,store:()=>{queueSession();},toast,review:organizationPreview,history:organizationHistory};
}
function organizationPreview(result,options){
 previewChange({backend:true,title:options.title,before:'',after:'',proposal:result,propertyRows:options.propertyRows,destination:options.destination,renderContent:options.renderContent,information:options.information,ackText:options.ackText,confirmText:options.confirmText,effectText:options.effectText,saveLabel:options.saveLabel,
 confirm:async()=>{
  const receipt=await editorialRequest('/api/editorial/save',{body:{preview_id:result.preview_id,acknowledge_warnings:!result.requires_acknowledgement||previewWarningsAccepted}});
  options.onSaved?.(receipt);if(options.workKey)delete saved.organizationWork[options.workKey];saved.lastBackendReceipt={history_id:receipt.history_id,entity:receipt.entity,time:new Date().toISOString()};persist();preview=null;
  try{catalog=await loadCatalog();for(const material of materials)if(material.kind==='document'&&catalog.documents.has(material.doc.id))material.doc=catalog.documents.get(material.doc.id);clearEditionCache();navigate(options.returnRoute||'catalogo');toast(options.successText||'Acervo local atualizado, com histórico. Textos e URLs existentes foram preservados.');}catch(error){content.replaceChildren(n('section',{class:'page-shell'},[heading('Gravação concluída','Alterações salvas.',`Registro ${receipt.history_id}. Recarregue para atualizar a interface; não repita a gravação.`)]));}
 }});
}
async function organizationHistory(id,returnRoute){
 try{const response=await editorialRequest('/api/editorial/history?document='+encodeURIComponent(id));const entries=response.items.filter(item=>item.state==='committed'&&(item.document_id===id||item.entity?.id===id)),batch=entries.some(entry=>entry.entity?.kind==='batch');
  panel(batch?'Histórico da importação':'Histórico do acervo local',[
   n('p',{text:batch?'Consultar este histórico não altera nada. Desfazer a importação retira do acervo os documentos e versões criados pelo lote. Você verá o efeito antes de confirmar; o histórico mantém uma cópia recuperável.':'Restaurar exige prévia e cria outro registro. Não apaga as versões anteriores.'}),...entries.map(entry=>{
   const isBatch=entry.entity?.kind==='batch';
   const restore=button(isBatch?(entry.restores?'Conferir desfazer esta reversão':'Conferir desfazer importação'):'Conferir restauração',async()=>{try{
    const fresh=await editorialRequest('/api/editorial/session'),result=await editorialRequest('/api/editorial/preview',{body:{revision:fresh.revision,restore_id:entry.id}});
    const removed=isBatch?result.changes.filter(change=>change.field.startsWith('Novo documento: ')&&change.after===null):[],added=isBatch?result.changes.filter(change=>change.field.startsWith('Novo documento: ')&&change.after!==null):[];
    const removing=removed.length>0,effect=removing?'Retira do catálogo, da busca e das coleções os documentos deste lote e remove seus arquivos cadastrados. Os arquivos e o estado anterior permanecem no histórico recuperável. Os arquivos originais que você enviou do seu computador não são alterados.':isBatch?'Recoloca no acervo os documentos e versões retirados pela reversão selecionada, usando a cópia preservada no histórico.':'Retorna os dados ao estado anterior à operação selecionada e cria outro registro de histórico.';
    organizationPreview(result,{title:isBatch?(removing?'Desfazer importação: retirar documentos do acervo':'Repor documentos da importação'):'Conferir restauração',returnRoute:entry.entity?.kind==='collection'?'colecoes':returnRoute,
     ...(isBatch?{information:[['O que será feito',effect],['Documentos afetados',(entry.entity.document_ids||[]).join('\n')],['Registro de origem',entry.id]],effectText:effect,confirmText:removing?'Entendi que os documentos e versões deste lote sairão do acervo e seus arquivos ficarão recuperáveis pelo histórico. Confirmo desfazer a importação.':'Confirmo repor os documentos e versões desta importação a partir do histórico.',saveLabel:removing?'Retirar lote do acervo':'Repor documentos',successText:removing?'Importação desfeita: documentos retirados do acervo, com cópia recuperável no histórico.':'Documentos repostos no acervo a partir do histórico.',propertyRows:[...removed.map(change=>({field:change.field.replace('Novo documento: ',''),before:'Cadastrado no acervo',after:'Será retirado do acervo; cópia preservada no histórico'})),...added.map(change=>({field:change.field.replace('Novo documento: ',''),before:'Retirado do acervo',after:'Será cadastrado novamente a partir do histórico'}))]}:{propertyRows:result.changes.map(change=>({field:change.field,before:JSON.stringify(change.before,null,2),after:JSON.stringify(change.after,null,2)}))})});
   }catch(error){toast(error.message);}},'quiet');restore.disabled=saved.scope!=='acervo';
   return n('div',{class:'note-card'},[n('p',{text:new Date(entry.created_at).toLocaleString('pt-BR')}),n('p',{text:isBatch?(entry.restores?'Reversão de uma operação do lote':'Cadastro do corpus')+' · '+(entry.entity.document_ids||[]).length+' documentos':entry.summary}),restore]);
  }),!entries.length&&n('p',{text:'Não há registros deste item no histórico.'})]);
 }catch(error){toast(error.message);}
}
function catalogView(id) {
    const shell = n('section', { class: 'page-shell' }, [heading('Organizar o acervo', 'Catálogo de trabalho', '1. Localize um documento · 2. Ajuste a ficha ao lado · 3. Confira antes de guardar. Só o rascunho do piloto será alterado.')]);
    const grid = n('div', { class: 'catalog-layout' }), list = n('div'), sheet = n('div', { class: 'property-sheet' }), search = n('input', { type: 'search', placeholder: 'Localizar documento…', 'aria-label': 'Localizar documento no catálogo' });
    function edit(doc) { sheet.replaceChildren(n('h2', { text: label(doc) }), n('p', { class: 'hint', text: doc.id + ' · rascunho do piloto' })); const previous = saved.metadata[doc.id] || {}; const fields = ['title_pt', 'date', 'author', 'archive']; const names = ['Título em português', 'Data histórica', 'Autoria', 'Referência arquivística']; const entries = fields.map((key, i) => { const value = saved.catalogWork[doc.id]?.[key] ?? previous[key] ?? doc[key] ?? ''; const f = field(names[i], typeof value === 'string' ? value : JSON.stringify(value)); f.input.oninput=()=>{(saved.catalogWork[doc.id]||={})[key]=f.input.value;queueSession();};sheet.append(f.element); return [key, f.input]; }); sheet.append(button('Conferir alterações', () => { const after = Object.fromEntries(entries.map(([key, input]) => [key, input.value])); previewChange({ title: 'Conferir ficha catalográfica', before: JSON.stringify(Object.fromEntries(fields.map(k => [k, previous[k] ?? doc[k] ?? ''])), null, 2), after: JSON.stringify(after, null, 2), confirm: () => { record('metadata', doc.id, previous); saved.metadata[doc.id] = after;delete saved.catalogWork[doc.id]; persist(); navigate('catalogo/' + doc.id); toast('Ficha guardada como rascunho do piloto.'); } }); }, 'primary')); }
    const entries=n('div');list.append(search,entries);
    function filter() { entries.replaceChildren(); const docs = catalog.all.filter(d => normalize(label(d) + ' ' + d.id).includes(normalize(search.value))).slice(0, 35); for (const d of docs)
        entries.append(b(label(d), () => edit(d), 'catalog-entry')); }
    search.oninput = filter;
    filter();
    grid.append(list, sheet);
    shell.append(grid);
    content.append(shell);
    edit(catalog.documents.get(id) || catalog.all[0]);
    controls.append(button('Importar corpus', () => navigate('importar')));
    if(saved.catalogReturn&&catalog.documents.has(saved.catalogReturn.id))controls.append(button('Voltar ao texto',()=>{const context=saved.catalogReturn;openDocument(catalog.documents.get(context.id));current().lang=context.lang;current().mode=context.mode;render();},'quiet'));
}
function tools(){
 if(!$('#auxiliary').hidden){closePanel();return;}
 const groups=[
  menuGroup('Abrir materiais',[
   {title:'Abrir documento',description:'Localizar um texto do acervo e acrescentar à Mesa.',run:()=>{const input=n('input',{type:'search',class:'action-menu-search',placeholder:'Título ou identificação…','aria-label':'Buscar documento'}),list=n('div');const update=()=>list.replaceChildren(...catalog.all.filter(d=>normalize(label(d)+' '+d.id).includes(normalize(input.value))).slice(0,25).map(d=>b(label(d),()=>openDocument(d),'index-entry')));input.oninput=update;panel('Abrir documento',[input,list]);update();input.focus();}},
   backendAvailable&&{title:'Fontes PDF e OCR',description:'Fontes cadastradas, extração, revisão e incorporação.',run:()=>{closePanel();navigate('fontes');}},
   {title:'PDF temporário',description:'Consultar um arquivo sem cadastrar no backend.',run:pickPdf}
  ]),
  menuGroup('Organizar acervo',[
   backendAvailable&&{title:'Projetos locais',description:'Materiais, versões privadas e incorporação explícita ao acervo.',run:()=>{closePanel();navigate('projetos');}},
   backendAvailable&&{title:'Fila de revisão',description:'Prioridades, motivos e registro de avaliações com histórico.',run:()=>{closePanel();navigate('fila');}},
   {title:'Catálogo e metadados',description:'Revisar fichas e associações dos documentos.',run:()=>{closePanel();navigate('catalogo');}},
   {title:'Coleções e subcoleções',description:'Organizar percursos e editar sua apresentação.',run:()=>{closePanel();navigate('colecoes');}},
   {title:'Importar corpus',description:'Associar originais e traduções; conferir cadastro local.',run:()=>{closePanel();navigate('importar');}}
  ]),
  menuGroup('Retomar trabalho',[
   {title:'Rascunhos e recuperação',description:'Retomar alterações, exportar ou restaurar a sessão.',run:draftsPanel},
   {title:'Histórico dos rascunhos',description:'Consultar versões anteriores da sessão.',run:historyPanel},
   current()&&{title:'Fechar material ativo',description:'Preservar versões salvas e conferir alterações pendentes.',run:()=>{closePanel();if(current())closeMaterial(current());}}
  ]),
  menuGroup('Ajuda', [{title:'Sobre o piloto',description:'Capacidades, destinos de gravação e interface oficial.',run:about}])
 ];panel('Ações e materiais',[menuSearch(groups),...groups]);
}
function about() { dialog('Biblioteca + Mesa', [n('p', { text: 'Um piloto de organização do trabalho: os materiais ficam abertos; ler, comparar e editar são atividades sobre eles.' }), n('p', { text: 'Usa documentos reais e permite rascunhos da sessão, além de gravação editorial local explicitamente confirmada quando o backend está disponível. Guardar rascunhos não modifica o acervo. Com o backend local, editar Markdown ou importar tradução também oferece gravação real, com prévia e confirmação explícitas. PDFs enviados permanecem no navegador e precisam ser reabertos após recarregar.' }), n('p', { text: 'A extração de texto pesquisável funciona com PDF.js. Fontes cadastradas permitem OCR e preparação de imagem/PDF. A importação de corpus, traduções e edição Markdown podem gravar no acervo local mediante prévia e confirmação.' }), button('Exportar meus rascunhos', exportSession), n('a', { href: asset('index.html'), text: 'Voltar à interface oficial' })]); }
async function render() { if(globalKeyboardOpen)requestAnimationFrame(describeKeyboardTarget);content.classList.remove('task-scroll');updateScope();clearLocatedPhrase();globalThis.CSS?.highlights?.delete('mesa-facsimile-phrase');hidePassageActions();persist();content.dataset.material=''; const version = ++generation; cleanup(); cleanup = () => { }; controls.replaceChildren(); content.replaceChildren(); closePanel(); tabs(); const route = location.hash.slice(1) || 'biblioteca'; const working = route === 'mesa'; document.body.classList.toggle('working', working); document.querySelectorAll('[data-nav]').forEach(el => el.classList.toggle('active', el.dataset.nav === (working ? 'desk' : 'library'))); if (preview) {
    showPreview();
    return;
} try {
    if (route === 'mesa') {
        const m = current();
        if(m)content.dataset.material=m.key;
        if (!m) {
            content.append(n('section', { class: 'empty-desk' }, [n('p', { class: 'eyebrow', text: 'Sua mesa de pesquisa' }), n('h1', { text: 'Comece por uma fonte.' }), n('p', { text: 'Abra documentos da biblioteca, compare idiomas e guarde rascunhos sem sair do mesmo material.' }), button('Escolher documento', tools, 'primary'), backendAvailable&&button('Fontes PDF / OCR',()=>navigate('fontes')),button('PDF temporário', pickPdf)]));
            return;
        }
        content.append(n('div', { class: 'loading-screen', text: 'Abrindo material…' }));
        if (m.kind === 'pdf') {
            content.replaceChildren();
            await pdfView(m, version);
        }
        else {
            content.replaceChildren();
            await documentView(m, version);
        }
    }
    else if(route==='projetos'||route.startsWith('projetos/')){if(backendAvailable)await mountProjects(projectEnvironment(version),decodeURIComponent(route.split('/')[1]||''));else content.append(n('section',{class:'page-shell'},[heading('Projetos privados','Backend local necessário','Inicie python3 -m backend para acessar os projetos locais.')]));}
    else if(route==='fontes'){if(backendAvailable)await sourcesView(pdfEnvironment(version));else content.append(n('section',{class:'page-shell'},[heading('Fontes PDF','Backend local necessário','Inicie python3 -m backend para cadastrar fontes e executar OCR.')]));}
    else if (route.startsWith('catalogo')){
        const id=decodeURIComponent(route.split('/')[1]||'');if(backendAvailable){await mountCatalog(organizationEnvironment(version),id);if(generation===version&&saved.catalogReturn&&catalog.documents.has(saved.catalogReturn.id))controls.append(button('Voltar ao texto',()=>{const context=saved.catalogReturn;openDocument(catalog.documents.get(context.id));current().lang=context.lang;current().mode=context.mode;render();},'quiet'));}else catalogView(id);
    }
    else if(route.startsWith('colecoes')){
      if(backendAvailable)await mountCollections(organizationEnvironment(version),route);else content.append(n('section',{class:'page-shell'},[heading('Organizar coleções','Backend local necessário','Inicie python3 -m backend para editar e criar coleções com histórico. A Biblioteca permanece disponível para consulta.'),button('Abrir Biblioteca',()=>navigate('biblioteca'))]));
    }
    else if(route==='fila'||route.startsWith('fila/')){
      if(backendAvailable)await mountReview(organizationEnvironment(version),decodeURIComponent(route.split('/')[1]||''));else content.append(n('section',{class:'page-shell'},[heading('Fila de revisão','Backend local necessário','Inicie python3 -m backend para consultar e registrar as revisões locais.')]));
    }
    else if (route === 'importar')
        mountCorpus(organizationEnvironment(version));
    else
        library();
}
catch (e) {
    if (version === generation) {
        content.replaceChildren(n('section', { class: 'page-shell' }, [heading('Não foi possível abrir', 'Vamos tentar novamente.', e.message), button('Reabrir material', render), button('Voltar à biblioteca', () => navigate('biblioteca'))]));
    }
} }
// Um único teclado auxiliar pode escrever no campo ativo, inclusive busca, ficha e CodeMirror.
let keyboardTarget=null,globalKeyboardOpen=false;
const keyboardDock=n('section',{class:'global-keyboard',hidden:true,'aria-label':'Teclado russo auxiliar'}),keyboardTargetLabel=n('span',{class:'keyboard-target',text:'Escolha um campo de texto'}),keyboardBody=n('div',{class:'global-keyboard-body'});
const keyboardToggle=b('Я',()=>setGlobalKeyboard(!globalKeyboardOpen),'floating-keyboard-trigger',{'aria-label':'Abrir ou recolher teclado russo','aria-expanded':'false',title:'Arraste para mover; clique para abrir ou recolher o teclado russo'});
keyboardToggle.onmousedown=event=>event.preventDefault();
document.body.append(keyboardToggle,keyboardDock);keyboardToggle.hidden=true;keyboardToggle.setAttribute('aria-controls','floating-russian-keyboard');keyboardDock.id='floating-russian-keyboard';
const keyboardHeaderToggle=b('Я',()=>setGlobalKeyboard(!globalKeyboardOpen),'icon-button',{'aria-label':'Teclado russo','aria-expanded':'false','aria-controls':'floating-russian-keyboard',title:'Abrir teclado russo'});keyboardHeaderToggle.onmousedown=event=>event.preventDefault();$('#open-tools').before(keyboardHeaderToggle);
keyboardDock.append(n('div',{class:'global-keyboard-heading'},[n('strong',{text:'Teclado · Русский'}),keyboardTargetLabel,b('Recolher',()=>setGlobalKeyboard(false),'control quiet')]),keyboardBody);
function availableKeyboardTarget(){return keyboardTarget?.isConnected&&!keyboardTarget.readOnly&&!keyboardTarget.disabled&&(!$('#dialog').open||$('#dialog').contains(keyboardTarget));}
function describeKeyboardTarget(){
 keyboardToggle.hidden=!globalKeyboardOpen&&!availableKeyboardTarget();
 if(!availableKeyboardTarget()){keyboardTargetLabel.textContent='Clique num campo de texto para digitar';return;}
 keyboardTargetLabel.textContent=keyboardTarget.closest('.cm-editor')?'Editor Markdown':keyboardTarget.getAttribute('aria-label')||keyboardTarget.labels?.[0]?.textContent?.trim().slice(0,70)||keyboardTarget.placeholder||'Campo de texto ativo';
}
document.addEventListener('focusin',event=>{
 const target=event.target;
 if(keyboardDock.contains(target)||target===keyboardToggle||target===keyboardHeaderToggle)return;
 if(target.matches('textarea,input:not([type]),input[type="text"],input[type="search"],input[type="url"],input[type="email"],.cm-content')){keyboardTarget=target;describeKeyboardTarget();}
});
function typeFromKeyboard(text,erase=false){
 if(!availableKeyboardTarget()){toast('Clique primeiro no campo onde deseja digitar.');return;}
 if(keyboardTarget.closest('.cm-editor')&&activeMarkdownEditor){
   const view=activeMarkdownEditor,selection=view.state.selection.main;
   let from=selection.from;if(erase&&selection.empty&&from>0){const before=view.state.doc.sliceString(0,from);from-=Array.from(before).at(-1)?.length||1;}
   view.dispatch({changes:{from,to:selection.to,insert:erase?'':text},selection:{anchor:from+(erase?0:text.length)},scrollIntoView:true});view.focus();return;
 }
 const start=keyboardTarget.selectionStart,end=keyboardTarget.selectionEnd;
 if(start===null||end===null){toast('Este campo não aceita inserção pelo teclado auxiliar.');return;}
 const previous=erase&&start===end?Array.from(keyboardTarget.value.slice(0,start)).at(-1)?.length||0:0;
 keyboardTarget.setRangeText(erase?'':text,start-previous,end,'end');keyboardTarget.dispatchEvent(new Event('input',{bubbles:true}));keyboardTarget.focus();
}
async function setGlobalKeyboard(open){
 globalKeyboardOpen=open;keyboardDock.hidden=!open;keyboardToggle.setAttribute('aria-expanded',String(open));keyboardHeaderToggle.setAttribute('aria-expanded',String(open));
 document.documentElement.style.setProperty('--keyboard-space','0px');if(!open){describeKeyboardTarget();return;}
 document.querySelectorAll('.transcription-keyboard').forEach(dock=>dock.hidden=true);if(current()?.kind==='pdf')current().keyboardOpen=false;document.querySelectorAll('.transcript .column-label button[aria-expanded]').forEach(button=>button.setAttribute('aria-expanded','false'));
 describeKeyboardTarget();
 try{if(!keyboardBody.childElementCount){const {russianKeyboard}=await import('../estudio/russian-keyboard.js');if(!globalKeyboardOpen||keyboardBody.childElementCount)return;const keyboard=russianKeyboard({write:text=>typeFromKeyboard(text),erase:()=>typeFromKeyboard('',true),locked:()=>false});keyboard.open=true;keyboardBody.append(keyboard);}
 requestAnimationFrame(()=>{if(globalKeyboardOpen)placeKeyboard();});
 }catch(error){toast('Não foi possível abrir o teclado: '+error.message);setGlobalKeyboard(false);}
}
let keyboardPosition=null,keyboardDrag=null;
function placeKeyboard(){
 const width=keyboardDock.offsetWidth,height=keyboardDock.offsetHeight;
 let x=keyboardPosition?.x??Math.max(12,window.innerWidth-width-18),y=keyboardPosition?.y??Math.max(12,window.innerHeight-height-75);
 if(!keyboardPosition&&availableKeyboardTarget()){
   const rect=keyboardTarget.getBoundingClientRect();
   if(rect.bottom>y&&rect.top<y+height)y=rect.top-height-15>=12?rect.top-height-15:Math.min(window.innerHeight-height-12,rect.bottom+15);
 }
 x=Math.max(8,Math.min(x,window.innerWidth-width-8));y=Math.max(8,Math.min(y,window.innerHeight-height-8));
 keyboardDock.style.left=x+'px';keyboardDock.style.top=y+'px';
}
const keyboardHandle=keyboardDock.querySelector('.global-keyboard-heading');keyboardHandle.setAttribute('title','Arraste para mover o teclado');
keyboardHandle.addEventListener('pointerdown',event=>{
 if(event.target.closest('button')||event.button!==0)return;
 const rect=keyboardDock.getBoundingClientRect();keyboardDrag={id:event.pointerId,x:event.clientX,y:event.clientY,left:rect.left,top:rect.top};keyboardHandle.setPointerCapture(event.pointerId);event.preventDefault();
});
keyboardHandle.addEventListener('pointermove',event=>{
 if(!keyboardDrag||keyboardDrag.id!==event.pointerId)return;
 keyboardPosition={x:keyboardDrag.left+event.clientX-keyboardDrag.x,y:keyboardDrag.top+event.clientY-keyboardDrag.y};placeKeyboard();
});
const finishKeyboardDrag=()=>keyboardDrag=null;
keyboardHandle.addEventListener('pointerup',finishKeyboardDrag);keyboardHandle.addEventListener('pointercancel',finishKeyboardDrag);
window.addEventListener('resize',()=>{if(globalKeyboardOpen)placeKeyboard();});
keyboardDock.addEventListener('pointerdown',event=>{const rect=keyboardDock.getBoundingClientRect();if(event.clientX>rect.right-24&&event.clientY>rect.bottom-24)keyboardPosition={x:rect.left,y:rect.top};});
new ResizeObserver(()=>{if(globalKeyboardOpen){keyboardDock.style.setProperty('--keyboard-key-font',Math.max(11,Math.min(22,keyboardDock.clientWidth/48,(keyboardDock.clientHeight-60)/10))+'px');placeKeyboard();}}).observe(keyboardDock);
let triggerDrag=null,triggerMoved=false;
keyboardToggle.addEventListener('pointerdown',event=>{if(event.button!==0)return;const rect=keyboardToggle.getBoundingClientRect();triggerDrag={id:event.pointerId,x:event.clientX,y:event.clientY,left:rect.left,top:rect.top};triggerMoved=false;keyboardToggle.setPointerCapture(event.pointerId);});
keyboardToggle.addEventListener('pointermove',event=>{if(!triggerDrag||triggerDrag.id!==event.pointerId)return;if(Math.hypot(event.clientX-triggerDrag.x,event.clientY-triggerDrag.y)>5)triggerMoved=true;if(!triggerMoved)return;keyboardToggle.style.right='auto';keyboardToggle.style.bottom='auto';keyboardToggle.style.left=Math.max(8,Math.min(window.innerWidth-keyboardToggle.offsetWidth-8,triggerDrag.left+event.clientX-triggerDrag.x))+'px';keyboardToggle.style.top=Math.max(8,Math.min(window.innerHeight-keyboardToggle.offsetHeight-8,triggerDrag.top+event.clientY-triggerDrag.y))+'px';});
window.addEventListener('resize',()=>{if(keyboardToggle.style.left){keyboardToggle.style.left=Math.max(8,Math.min(parseFloat(keyboardToggle.style.left),window.innerWidth-keyboardToggle.offsetWidth-8))+'px';keyboardToggle.style.top=Math.max(8,Math.min(parseFloat(keyboardToggle.style.top),window.innerHeight-keyboardToggle.offsetHeight-8))+'px';}});
keyboardToggle.addEventListener('pointerup',()=>triggerDrag=null);keyboardToggle.addEventListener('pointercancel',()=>{triggerDrag=null;triggerMoved=false;});
keyboardToggle.addEventListener('click',event=>{if(triggerMoved){event.preventDefault();event.stopImmediatePropagation();triggerMoved=false;}},true);


document.addEventListener('mesa:error',event=>toast(event.detail?.message||'Não foi possível concluir a ação.'));
document.querySelectorAll('.main-nav a,.identity').forEach(a=>a.addEventListener('click',event=>{remember();if(a.dataset.nav==='library'||a.classList.contains('identity')){projectContext=null;saved.scope='acervo';updateScope();}if(a.classList.contains('identity')){event.preventDefault();Object.assign(libraryState,{q:'',collection:'',sub:'',language:'',offset:0,view:'home'});navigate('biblioteca');}}));
$('#open-tools').onclick = tools;
$('#help-button').onclick = about;
$('#panel-backdrop').onclick = closePanel;
async function scopeDialog(){
 if(!backendAvailable){dialog('Contexto de trabalho',[n('p',{text:'Você está consultando o acervo. Projetos privados exigem o backend local.'}),button('Rascunhos e recuperação',()=>{$('#dialog').close();draftsPanel();},'quiet')]);return;}
 try{const response=await editorialRequest('/api/editorial/projects');dialog('Contexto de trabalho',[
  n('p',{text:'O projeto organiza versões privadas. As abas indicam de qual contexto cada documento foi aberto. Trocar aqui não grava nem promove alterações ao acervo.'}),
  button('Acervo local · sem projeto',()=>{$('#dialog').close();projectContext=null;updateScope();navigate('biblioteca');}),
  ...response.items.filter(p=>!p.archived).map(project=>button(project.title,()=>{$('#dialog').close();projectContext=project;updateScope();projectMaterials(projectEnvironment(generation),project.id);})),
  button('Organizar / criar projetos',()=>{$('#dialog').close();navigate('projetos');},'quiet'),button('Rascunhos e recuperação',()=>{$('#dialog').close();draftsPanel();},'quiet')]);}catch(error){toast(error.message);}
}
function updateScope(){const project=location.hash==='#mesa'?current()?.project:projectContext,button=$('#scope-button');button.textContent=project?'Projeto: '+project.title+' ⌄':saved.scope==='projeto-piloto'?'Caderno legado · sessão ⌄':'Acervo local ⌄';button.title=project?'Versões privadas do projeto '+project.title:'Sem projeto ativo. Cada gravação indica seu destino.';}
$('#scope-button').onclick=scopeDialog;
document.addEventListener('keydown', e => { if (e.key === 'Escape'){if(globalKeyboardOpen){setGlobalKeyboard(false);return;}hidePassageActions();closePanel();} });
window.addEventListener('hashchange', () => { preview = null; render(); });
window.addEventListener('beforeunload', () => { remember(); persist(); });
try {
    [catalog,backendAvailable]=await Promise.all([loadCatalog(),detectEditorial()]);
    const restored=restoreDesk(saved.workspace,catalog);materials=restored.materials;active=restored.active;Object.assign(libraryState,restored.library);if(current()?.projectId)active=materials.find(m=>!m.projectId)?.key;updateScope();
    await render();
}
catch (e) {
    content.replaceChildren(n('div', { class: 'page-shell' }, [n('h1', { text: 'A biblioteca não carregou.' }), n('p', { text: e.message }), button('Tentar novamente', () => location.reload())]));
}
