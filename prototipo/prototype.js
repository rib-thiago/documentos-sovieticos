/* Protótipo isolado: somente leitura do acervo. Sem API de gravação. */
(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fold = value => String(value || '').normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase();
  const title = item => item.title_pt || item.title_ru || item.title_en || item.id;
  const code = value => encodeURIComponent(value);
  const names = {pt:'Português',ru:'Русский',en:'English'};
  const content = $('#content');
  const memory = {manifest:null,docs:new Map(),collection:null,document:null,language:'pt',right:'ru',mode:'read',page:0,sub:'',query:'',render:0,cache:new Map(),marker:null,layout:'cards',currentView:null,positions:new Map(),tabs:[],docStates:new Map(),drafts:new Map(),notes:new Map(),openTool:null,activity:JSON.parse($('#activity-data').textContent)};
  const md = window.markdownit({html:false,linkify:false,typographer:false});
  if(window.markdownitFootnote) md.use(window.markdownitFootnote);
  function remember(key,value){try{sessionStorage.setItem('prototype:'+key,value);}catch{}}
  function recall(key,fallback){try{return sessionStorage.getItem('prototype:'+key)||fallback;}catch{return fallback;}}
  function toast(message){$('#notice').textContent=message;$('#notice').hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('#notice').hidden=true,4500);}
  function docURL(id,editor=false){return '#/'+(editor?'editorial':'documento')+'/'+code(id)+'?colecao='+code(memory.collection?.id||'');}
  function collectionDocs(collection){return collection.document_ids ? collection.document_ids.map(id=>memory.docs.get(id)).filter(Boolean) : collection.documents||[];}
  function date(doc){const value=doc.date||doc.collected_date;return value?String(value).replace(/T.*$/,''):'';}
  function action(label,attrs=''){return `<button type="button" class="btn" ${attrs}>${label}</button>`;}
  function crumbs(items){return `<div class="crumbs"><a href="#/inicio">Acervo</a>${items.map(([label,href])=>`<span aria-hidden="true">/</span>${href?`<a href="${esc(href)}">${esc(label)}</a>`:`<span>${esc(label)}</span>`}`).join('')}</div>`;}
  function side(view){
    const bench=view==='trabalho';$('#sidebar').hidden=!bench;$('#workspace-tabs').hidden=!bench;
    $('#shell').classList.toggle('is-workbench',bench);
    $('#shell').classList.toggle('is-reader',view==='documento');
    if(!bench)$('#shell').classList.remove('is-collapsed');
    if(bench){
      $('#sidebar-body').innerHTML=`<p class="caption">DOCUMENTO ATIVO</p><button class="instrument" data-tool="markdown"><span>¶</span><span>Markdown e prévia<small>Texto-fonte e renderização</small></span></button><button class="instrument" data-tool="index"><span>☷</span><span>Índice<small>Estrutura interna do texto</small></span></button><button class="instrument" data-tool="metadata"><span>ⓘ</span><span>Ficha documental<small>Identificação e procedência</small></span></button><button class="instrument" data-tool="notes"><span>✎</span><span>Notas de trabalho<small>Rascunho desta sessão</small></span></button><p class="caption">TRABALHAR COM O ACERVO</p><button class="instrument" id="open-document"><span>＋</span><span>Abrir documento<small>Adicionar uma aba</small></span></button><p class="side-note">As ferramentas acompanham a aba ativa. Rascunhos ficam nesta página; não alteram o acervo.</p>`;
      $('#open-document').onclick=openDocumentPicker;
      document.querySelectorAll('[data-tool]').forEach(b=>b.onclick=()=>memory.openTool?.(b.dataset.tool));
    }
    document.querySelectorAll('[data-nav]').forEach(link=>{if(link.dataset.nav===view)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');});
  }
  function card(collection){const docs=collectionDocs(collection);return `<a class="card" href="#/colecao/${code(collection.id)}"><div class="cover">${collection.cover?`<img src="../${esc(collection.cover)}" alt="" loading="lazy">`:'<span aria-hidden="true">§</span>'}</div><div class="card-body"><h3>${esc(title(collection))}</h3><p>${esc(collection.subtitle_pt||'Coleção documental')}</p></div><div class="card-footer"><span>${docs.length} documentos</span><span>Explorar coleção ↗</span></div></a>`;}
  function home(){
    const docs=[...memory.docs.values()],versions=docs.reduce((sum,d)=>sum+d.languages.length,0),pt=docs.filter(d=>d.languages.some(l=>l.code==='pt')).length;
    const events=memory.activity.events||[],recent=[],sources=[],seen=new Set(),sourceSeen=new Set();
    for(const event of events){
      for(const item of event.examples||[])if(!item.languages.includes('ru')&&!seen.has(item.id)&&memory.docs.has(item.id)){recent.push({...item,event});seen.add(item.id);}
      for(const item of event.source_examples||[])if(!sourceSeen.has(item.id)&&memory.docs.has(item.id)){sources.push({...item,event});sourceSeen.add(item.id);}
    }
    const featured=memory.manifest.collections.find(c=>c.id==='centro-de-moscou')||memory.manifest.collections[0];
    const formatStamp=stamp=>new Intl.DateTimeFormat('pt-BR',{day:'2-digit',month:'short',year:'numeric'}).format(new Date(stamp));
    const updateCard=item=>{const doc=memory.docs.get(item.id);return `<a class="update-card" href="#/documento/${code(doc.id)}"><div class="update-top"><span class="language-pill">${item.languages.map(l=>esc(l.toUpperCase())).join(' + ')}</span><time>${esc(formatStamp(item.event.recorded_at))}</time></div><h3>${esc(title(doc))}</h3><p>${esc(date(doc)||doc.id)}</p><span class="update-link">Ler documento ↗</span></a>`;};
    content.innerHTML=`<section class="portal-hero"><div class="portal-intro"><p class="eyebrow">Documentos Soviéticos / Edição digital de fontes</p><h1>Um arquivo aberto<br>à <em>pesquisa.</em></h1><p class="portal-lead">História política da União Soviética em documentos, traduções e percursos de leitura. Das coleções à comparação entre fontes.</p><form class="search-box" id="home-search"><input name="q" aria-label="Buscar nos títulos" placeholder="Encontre uma fonte, um nome, uma expressão…"><button class="btn primary">Buscar →</button></form><p class="search-hint">Busca nos títulos nesta prévia · russo, português e inglês</p></div><a class="portal-feature" href="#/colecao/${code(featured.id)}"><div class="feature-cover">${featured.cover?`<img src="../${esc(featured.cover)}" alt="">`:''}</div><div><p class="eyebrow">Percurso pelo acervo</p><h2>${esc(title(featured))}</h2><p>${collectionDocs(featured).length} documentos · fontes e traduções</p><span>Conhecer a coleção ↗</span></div></a></section><div class="acervo-strip"><span><strong>${docs.length.toLocaleString('pt-BR')}</strong> documentos únicos</span><span><strong>${memory.manifest.collections.length}</strong> coleções</span><span><strong>${pt.toLocaleString('pt-BR')}</strong> documentos em português</span><span><strong>${versions.toLocaleString('pt-BR')}</strong> versões linguísticas</span></div><section class="portal-updates"><div class="section-title"><div><p class="eyebrow">Acervo em movimento</p><h2>Traduções e versões incorporadas</h2></div><a class="text-link" href="#/busca">Consultar o catálogo ↗</a></div><div class="update-grid">${recent.slice(0,4).map(updateCard).join('')||'<p>As incorporações serão apresentadas quando houver registros disponíveis.</p>'}</div><p class="activity-note">Datas de incorporação registradas no Git local, não datas históricas dos documentos nem confirmação de publicação online. Recorte demonstrativo do histórico.</p></section><section class="portal-lower"><div><div class="section-title"><div><p class="eyebrow">Novas entradas no histórico</p><h2>Fontes incorporadas</h2></div></div><div class="source-feed">${sources.slice(0,3).map(item=>{const doc=memory.docs.get(item.id);return `<a href="#/documento/${code(item.id)}"><div><span>${esc(formatStamp(item.event.recorded_at))} · RU</span><h3>${esc(title(doc))}</h3><p>${esc(doc.id)} · ${esc(date(doc))}</p></div><span>↗</span></a>`;}).join('')||'<p>Nenhuma incorporação de fonte russa localizada no recorte do histórico.</p>'}</div></div><aside class="research-invitation"><p class="eyebrow">Além da leitura</p><h2>Seu espaço de trabalho com as fontes.</h2><p>Abra documentos em abas. Consulte o Markdown ao lado do texto. Organize notas e consulte a ficha sem perder o documento de vista.</p><a class="btn primary" href="#/trabalho/showtrials-1665">Abrir a bancada →</a><button class="text-link" id="research-more">Pessoas e episódios: próxima etapa ↗</button></aside></section><section id="portal-collections"><div class="section-title"><div><p class="eyebrow">Conjuntos documentais</p><h2>Explore as coleções</h2></div><div class="segment" aria-label="Apresentação das coleções"><button type="button" data-layout="cards" aria-pressed="${memory.layout==='cards'}">Capas</button><button type="button" data-layout="list" aria-pressed="${memory.layout==='list'}">Lista</button></div></div><div class="collections ${memory.layout==='list'?'list':''}">${memory.manifest.collections.map(card).join('')}</div></section><footer class="portal-about"><div><p class="eyebrow">Sobre o projeto</p><h2>Preservar, traduzir, tornar pesquisável.</h2><p>Documentos Soviéticos é a edição pública do ShowTrials: pesquisa histórica, organização de fontes e tradução cuidadosa, com proveniência verificável.</p></div><button class="text-link" id="about">Conhecer os critérios editoriais ↗</button></footer>`;
    $('#home-search').onsubmit=e=>{e.preventDefault();location.hash='#/busca?q='+code(new FormData(e.target).get('q'));};
    $('#about').onclick=()=>showInfo('Uma edição digital de fontes','Documentos Soviéticos é a interface pública do projeto ShowTrials: pesquisa, preservação e edição de fontes sobre a história política da União Soviética.','A política editorial e os critérios de revisão ainda estão sendo definidos. Este protótipo não atribui revisão às traduções existentes.');
    $('#research-more').onclick=()=>showInfo('Pessoas e episódios','Entradas complementares para percorrer o acervo. Os vínculos terão fonte, atribuição e passagem de apoio; a avaliação histórica será registrada separadamente.','Essas entidades ainda não estão implementadas.');
    document.querySelectorAll('[data-layout]').forEach(button=>button.onclick=()=>{const top=window.scrollY;memory.layout=button.dataset.layout;home();window.scrollTo({top});});
  }
  function row(doc){return `<a class="document-row" href="${esc(docURL(doc.id))}"><div class="row-title"><strong>${esc(title(doc))}</strong>${date(doc)?`<time>${esc(date(doc))}</time>`:''}</div><div class="row-meta"><span>${esc(doc.eyebrow||doc.document_type||(doc.type==='article'?'Artigo':'Documento'))}</span><span>${(doc.languages||[]).map(l=>esc(l.code.toUpperCase())).join(' · ')}</span><span>${esc(doc.id)}</span></div></a>`;}
  function catalog(search=false){
    const col=memory.collection;
    let docs=search?[...memory.docs.values()]:collectionDocs(col);
    if(!search&&memory.sub){const sub=col.subcollections?.find(s=>s.id===memory.sub);if(sub)docs=docs.filter(d=>sub.document_ids.includes(d.id));}
    docs=docs.filter(d=>fold([d.title_pt,d.title_ru,d.title_en].join(' ')).includes(fold(memory.query)));
    const total=docs.length;const pages=Math.max(1,Math.ceil(total/20));memory.page=Math.min(memory.page,pages-1);
    content.innerHTML=crumbs([[search?'Busca':title(col)]])+`<div class="collection-heading"><div><p class="eyebrow">${search?'Pesquisa no acervo':'Coleção documental'}</p><h1>${search?'Buscar documentos':esc(title(col))}</h1><p>${search?'Consulte títulos nas línguas disponíveis. Os resultados não traduzem a consulta nem reúnem automaticamente variantes de nomes.':esc(col.description_pt||'Documentos organizados em conjuntos para consulta e leitura. A apresentação editorial deste conjunto será desenvolvida em etapa própria.')}</p></div>${!search&&col.cover?`<img src="../${esc(col.cover)}" alt="">`:''}</div>${!search?`<div class="chips"><button class="chip" data-sub="" aria-pressed="${!memory.sub}">Todos os documentos</button>${(col.subcollections||[]).map(s=>`<button class="chip" data-sub="${esc(s.id)}" aria-pressed="${memory.sub===s.id}">${esc(title(s))}</button>`).join('')}</div>`:''}<form id="filter" class="search-box"><input aria-label="${search?'Buscar nos títulos':'Filtrar títulos desta coleção'}" name="q" value="${esc(memory.query)}" placeholder="${search?'Nome ou expressão no título…':'Filtrar documentos desta coleção…'}"><button class="btn primary">${search?'Buscar':'Filtrar'}</button></form><div class="catalog-bar"><span>${total} documentos ${memory.query?'encontrados':''}</span><span>${search?'Busca nos títulos':'Ordem editorial do acervo'}</span></div><div class="document-list">${docs.slice(memory.page*20,(memory.page+1)*20).map(row).join('')||'<p class="empty">Nenhum título encontrado. Tente outra grafia ou uma expressão mais curta.</p>'}</div><div class="pagination"><button class="btn" id="prev-page" ${memory.page===0?'disabled':''}>← Anterior</button><span>Página ${memory.page+1} de ${pages}</span><button class="btn" id="next-page" ${memory.page+1>=pages?'disabled':''}>Próxima →</button></div>`;
    function update(){const params=new URLSearchParams({q:memory.query,page:String(memory.page)});if(memory.sub)params.set('sub',memory.sub);location.hash=(search?'#/busca':'#/colecao/'+code(col.id))+'?'+params;}
    $('#filter').onsubmit=e=>{e.preventDefault();memory.query=String(new FormData(e.target).get('q')).trim();memory.page=0;update();};
    $('#prev-page').onclick=()=>{memory.page--;update();};$('#next-page').onclick=()=>{memory.page++;update();};
    document.querySelectorAll('[data-sub]').forEach(b=>b.onclick=()=>{memory.sub=b.dataset.sub;memory.page=0;update();});
  }
  function options(doc,selected){return doc.languages.map(l=>`<option value="${esc(l.code)}" ${l.code===selected?'selected':''}>${esc(names[l.code]||l.label||l.code)}</option>`).join('');}
  function publicURL(doc){return '../#/doc/'+code(doc.id)+(memory.collection?'?colecao='+code(memory.collection.id):'');}
  async function source(doc,language){
    const edition=doc.languages.find(l=>l.code===language);if(!edition)throw new Error('Não há versão nesse idioma.');
    const key=edition.file;if(memory.cache.has(key))return memory.cache.get(key);
    const url=new URL('../'+edition.file,location.href);if(url.origin!==location.origin)throw new Error('Fonte fora do acervo local.');
    const response=await fetch(url);if(!response.ok)throw new Error('Não foi possível carregar a versão: '+response.status);
    const raw=await response.text();const text=splitExportHeaders(raw).body;
    const result={raw,text,edition:{...edition,format:edition.format||doc.format}};memory.cache.set(key,result);return result;
  }
  function renderText(data){return DOMPurify.sanitize(data.edition.format==='text'?'<div style="white-space:pre-wrap">'+esc(data.text)+'</div>':md.render(data.text),{FORBID_TAGS:['form','input','button','textarea','select']});}
  function structuralBlocks(data){
    if(data.edition.format==='text')return data.text.split(/\n\s*\n/).filter(t=>t.trim()).map(text=>({raw:text,html:'<p>'+esc(text)+'</p>'}));
    const env={},tokens=md.parse(data.text,env),lines=data.text.split('\n'),blocks=[];
    for(let i=0;i<tokens.length;){
      const start=i,first=tokens[i];let depth=first.nesting;i++;
      if(depth>0)while(i<tokens.length&&depth>0){depth+=tokens[i].nesting;i++;}
      const group=tokens.slice(start,i),map=first.map;
      blocks.push({raw:map?lines.slice(map[0],map[1]).join('\n'):group.map(t=>t.content||'').join('\n'),html:DOMPurify.sanitize(md.renderer.render(group,md.options,env))});
    }
    return blocks;
  }
  function passageDemo(doc,language,index,block){
    const dialog=document.createElement('dialog');dialog.className='passage-dialog';
    dialog.innerHTML=`<form method="dialog"><button class="dialog-close" aria-label="Fechar editor de trecho">×</button></form><p class="eyebrow">Edição de trecho · demonstração</p><h2>${esc(doc.id)} · ${esc(language.toUpperCase())} · §${String(index+1).padStart(3,'0')}</h2><p class="muted">Prévia sem gravação. A numeração identifica blocos desta versão; ainda não é uma âncora permanente para citação.</p><label>Markdown do trecho<textarea rows="8" class="passage-input"></textarea></label><h3>Prévia renderizada</h3><div class="prose passage-preview"></div>`;
    document.body.append(dialog);const input=dialog.querySelector('textarea');input.value=block.raw;
    function preview(){dialog.querySelector('.passage-preview').innerHTML=DOMPurify.sanitize(md.render(input.value));}
    input.oninput=preview;preview();dialog.onclose=()=>dialog.remove();dialog.showModal();input.focus();
  }
  async function reader(doc){
    const token=memory.render;
    if(!doc.languages?.length)throw new Error('Este cadastro não tem versão textual disponível no protótipo.');
    if(!doc.languages.some(l=>l.code===memory.language))memory.language=doc.languages.some(l=>l.code==='ru')?'ru':doc.languages[0].code;
    if(!doc.languages.some(l=>l.code===memory.right)||memory.right===memory.language)memory.right=doc.languages.find(l=>l.code!==memory.language)?.code||memory.language;
    if(doc.languages.length<2)memory.mode='read';
    const storedMark=recall('marker:'+doc.id,'');try{memory.marker=storedMark?JSON.parse(storedMark):null;if(memory.marker&&(!Number.isInteger(memory.marker.index)||memory.marker.index<0||!doc.languages.some(l=>l.code===memory.marker.language)))memory.marker=null;}catch{memory.marker=null;}
    content.innerHTML=crumbs([[memory.collection?title(memory.collection):'Documento',memory.collection?'#/colecao/'+code(memory.collection.id):null],[doc.id]])+`<section class="toolbar" id="reader-toolbar" aria-label="Controles do documento"><div class="tool-head"><strong>¶ ${esc(doc.id)}</strong><select id="language" aria-label="Idioma principal">${options(doc,memory.language)}</select>${action('● Retomar','id="resume" hidden')}${action('Fixar barra','id="pin-toolbar" aria-pressed="false"')}${action('Ferramentas ⌄','id="tools" aria-expanded="false" aria-controls="tools-body"')}<a class="btn" href="${esc(docURL(doc.id,true))}">Editar ficha</a>${action('↓ Baixar','id="download"')}</div><div class="tool-body" id="tools-body" hidden><div class="segment" aria-label="Modo de leitura"><button data-mode="read" aria-pressed="true">Leitura</button><button data-mode="paragraph" aria-pressed="false" ${doc.languages.length<2?'disabled':''}>Estudo por trecho</button><button data-mode="parallel" aria-pressed="false" ${doc.languages.length<2?'disabled':''}>Paralelo</button></div><label id="right-label" hidden>Tradução / comparação <select id="right-language">${options(doc,memory.right)}</select></label>${action('Expandir traduções','id="expand-translations" hidden aria-pressed="false"')}${action('Índice','data-panel="toc" aria-pressed="false" aria-controls="aux"')}${action('Ficha e procedência','data-panel="metadata" aria-pressed="false" aria-controls="aux"')}</div></section><div class="reader-title"><p class="eyebrow">Fonte documental</p><h1>${esc(title(doc))}</h1>${doc.title_ru?`<p class="ru" lang="ru">${esc(doc.title_ru)}</p>`:''}<div class="reader-meta"><span>${esc(date(doc))}</span><span>Parágrafos marcáveis · seleção de trecho</span></div></div><div class="reader-workspace"><div class="text-columns" id="columns"><p role="status">Carregando texto…</p></div><aside class="aux" id="aux" aria-label="Informações auxiliares" hidden></aside></div><div class="reader-bottom" id="reader-bottom"></div>`;
    let activePanel='',currentBlocks={},columnRequest=0;
    $('#tools').onclick=()=>{const open=$('#tools-body').hidden;$('#tools-body').hidden=!open;$('#tools').setAttribute('aria-expanded',String(open));};
    const expandTranslations=$('#expand-translations');
    expandTranslations.onclick=()=>{const open=expandTranslations.getAttribute('aria-pressed')!=='true';document.querySelectorAll('[data-translation]').forEach(d=>d.open=open);expandTranslations.setAttribute('aria-pressed',String(open));expandTranslations.textContent=open?'Recolher traduções':'Expandir traduções';};
    const pin=$('#pin-toolbar'),toolbar=$('#reader-toolbar');
    function applyPin(pinned){toolbar.classList.toggle('is-pinned',pinned);pin.setAttribute('aria-pressed',String(pinned));pin.textContent=pinned?'Soltar barra':'Fixar barra';remember('pin',String(pinned));}
    applyPin(recall('pin','false')==='true');pin.onclick=()=>applyPin(!toolbar.classList.contains('is-pinned'));
    function captureAnchor(){const items=[...document.querySelectorAll('#columns [data-primary]')];const edge=Math.max(0,toolbar.getBoundingClientRect().bottom);return items.find(n=>n.getBoundingClientRect().bottom>edge)||null;}
    function mark(index,language){
      const same=memory.marker?.id===doc.id&&memory.marker.index===index&&memory.marker.language===language;memory.marker=same?null:{id:doc.id,language,index};remember('marker:'+doc.id,JSON.stringify(memory.marker));applyMarker();
    }
    function applyMarker(){
      document.querySelectorAll('#columns [data-block]').forEach(n=>n.classList.toggle('marked',memory.marker?.id===doc.id&&Number(n.dataset.block)===memory.marker.index&&n.dataset.language===memory.marker.language));
      document.querySelectorAll('[data-mark]').forEach(b=>b.setAttribute('aria-pressed',String(memory.marker?.index===Number(b.dataset.mark)&&memory.marker?.language===b.dataset.language)));
      $('#resume').hidden=memory.marker?.id!==doc.id;
    }
    function blockCell(block,index,language,primary){
      const number=String(index+1).padStart(3,'0');
      return `<section class="passage-cell ${primary?'primary-cell':'secondary-cell'}" data-block="${index}" data-language="${esc(language)}" ${primary?'data-primary="true"':''}><div class="passage-meta"><span class="passage-id">§${number} · ${esc(language.toUpperCase())}</span><div class="passage-actions"><button type="button" data-mark="${index}" data-language="${esc(language)}" aria-pressed="false" aria-label="Marcar o parágrafo" title="Marcar este trecho">●</button><button type="button" data-cite="${index}" data-language="${esc(language)}">Referência</button><button type="button" data-edit-passage="${index}" data-language="${esc(language)}">Editar trecho <span class="demo-tag">demo</span></button></div></div><div class="prose" lang="${esc(language)}">${block?block.html:'<p class="muted">Sem bloco nesta posição.</p>'}</div></section>`;
    }
    async function loadColumns(anchor=null){
      const request=++columnRequest,top=window.scrollY,offset=anchor?.getBoundingClientRect().top,index=anchor?Number(anchor.dataset.block):null;
      const language=memory.language,right=memory.right,mode=memory.mode;
      const data=await Promise.all((mode!=='read'?[language,right]:[language]).map(l=>source(doc,l)));
      if(token!==memory.render||request!==columnRequest)return;
      currentBlocks={};data.forEach((d,i)=>currentBlocks[i===0?language:right]=structuralBlocks(d));
      const left=currentBlocks[language],other=currentBlocks[right]||[],study=mode!=='read';
      $('#columns').className='text-columns '+(mode==='parallel'?'study-parallel':mode==='paragraph'?'study-paragraph':'continuous');
      $('#columns').innerHTML=(study?`<div class="alignment-note">Comparação por posição dos blocos · ${left.length} / ${other.length} blocos. A correspondência entre idiomas não foi confirmada. A numeração é local a esta versão.</div>`:'')+(mode==='parallel'?`<div class="parallel-head"><span>${esc(names[language]||language)} · principal</span><span>${esc(names[right]||right)} · comparação</span></div>`:'')+Array.from({length:study?Math.max(left.length,other.length):left.length},(_,i)=>{
        if(mode==='parallel')return `<div class="study-row">${blockCell(left[i],i,language,true)}${blockCell(other[i],i,right,false)}</div>`;
        return `<div class="study-row">${blockCell(left[i],i,language,true)}${mode==='paragraph'?`<details class="translation-block" data-translation="${i}"><summary>Expandir ${right==='pt'?'tradução portuguesa':'versão em '+esc(names[right]||right)} <span>§${String(i+1).padStart(3,'0')}</span></summary>${blockCell(other[i],i,right,false)}</details>`:''}</div>`;
      }).join('');
      document.querySelectorAll('#columns .primary-cell h1,#columns .primary-cell h2,#columns .primary-cell h3').forEach((h,i)=>h.id='section-0-'+i);
      document.querySelectorAll('[data-mark]').forEach(b=>{b.setAttribute('aria-label','Marcar trecho '+(Number(b.dataset.mark)+1));b.onclick=()=>mark(Number(b.dataset.mark),b.dataset.language);});
      document.querySelectorAll('#columns .passage-cell').forEach(cell=>cell.addEventListener('click',event=>{if(event.target.closest('a,button,summary,input,textarea')||window.getSelection()?.toString())return;mark(Number(cell.dataset.block),cell.dataset.language);}));
      document.querySelectorAll('[data-edit-passage]').forEach(b=>b.onclick=()=>{const block=currentBlocks[b.dataset.language]?.[Number(b.dataset.editPassage)];if(block)passageDemo(doc,b.dataset.language,Number(b.dataset.editPassage),block);else toast('Não há trecho nesta posição.');});
      document.querySelectorAll('[data-cite]').forEach(b=>b.onclick=async()=>{const reference=doc.id+' · '+b.dataset.language.toUpperCase()+' · bloco §'+String(Number(b.dataset.cite)+1).padStart(3,'0')+' (numeração provisória da prévia; não é referência arquivística).';try{await navigator.clipboard.writeText(reference);toast('Referência provisória copiada.');}catch{showInfo('Referência do trecho',reference);}});
      expandTranslations.hidden=mode!=='paragraph';expandTranslations.setAttribute('aria-pressed','false');expandTranslations.textContent='Expandir traduções';
      applyMarker();if(activePanel)panel(activePanel);
      if(index!==null){const target=document.querySelector(`#columns [data-primary][data-block="${index}"]`);if(target)window.scrollBy({top:target.getBoundingClientRect().top-offset});else window.scrollTo({top});}else window.scrollTo({top});
    }
    function safeLoad(anchor=captureAnchor()){loadColumns(anchor).catch(error=>{if(token===memory.render)toast(error.message);});}
    $('#language').onchange=e=>{memory.language=e.target.value;remember('language',memory.language);if(memory.right===memory.language){memory.right=doc.languages.find(l=>l.code!==memory.language)?.code||memory.language;$('#right-language').value=memory.right;}safeLoad();};
    $('#right-language').onchange=e=>{memory.right=e.target.value;safeLoad();};
    document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{const anchor=captureAnchor();memory.mode=b.dataset.mode;document.querySelectorAll('[data-mode]').forEach(n=>n.setAttribute('aria-pressed',String(n===b)));$('#right-label').hidden=memory.mode==='read';safeLoad(anchor);});
    function panel(which){
      activePanel=which;const aux=$('#aux');aux.hidden=false;
      document.querySelectorAll('[data-panel]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.panel===which)));
      aux.innerHTML='<button class="close-panel" aria-label="Fechar painel">×</button>'+(which==='toc'?'<h2>Índice do texto</h2><nav class="toc" aria-label="Seções do documento"></nav>':`<h2>Ficha documental</h2><dl><dt>Identificador</dt><dd>${esc(doc.id)}</dd><dt>Data apresentada no acervo</dt><dd>${esc(date(doc)||'Não cadastrada')}</dd><dt>Referência</dt><dd>${esc(doc.archive||'Não cadastrada')}</dd><dt>Idiomas</dt><dd>${doc.languages.map(l=>esc(names[l.code]||l.code)).join(' · ')}</dd><dt>Fonte cadastrada</dt><dd id="source-ref"></dd></dl><a href="${esc(publicURL(doc))}">Abrir no leitor atual ↗</a>`);
      if(which==='toc'){
        const headings=[...document.querySelectorAll('#columns .primary-cell h1,#columns .primary-cell h2,#columns .primary-cell h3')];
        if(!headings.length) $('.toc').textContent='Esta versão não contém títulos Markdown para gerar um índice.';
        headings.forEach(h=>{const a=document.createElement('a');a.href='#'+h.id;a.textContent=h.textContent;a.onclick=e=>{e.preventDefault();h.scrollIntoView({block:'start'});};$('.toc').append(a);});
      }else{const value=doc.source_url||doc.source_name||'Consulte a versão no leitor atual.';const target=$('#source-ref');try{const u=new URL(value,new URL('../',location.href));if(!['http:','https:'].includes(u.protocol))throw Error();const a=document.createElement('a');a.href=u.href;a.textContent=value;a.target='_blank';a.rel='noopener';target.append(a);}catch{target.textContent=value;}}
      $('.close-panel').onclick=()=>{aux.hidden=true;document.querySelector(`[data-panel="${which}"]`)?.focus();activePanel='';document.querySelectorAll('[data-panel]').forEach(b=>b.setAttribute('aria-pressed','false'));};
    }
    document.querySelectorAll('[data-panel]').forEach(b=>b.onclick=()=>panel(b.dataset.panel));
    $('#resume').onclick=async()=>{try{const mark=memory.marker;if(!mark||mark.id!==doc.id)return;memory.language=mark.language;$('#language').value=mark.language;remember('language',mark.language);if(memory.right===memory.language){memory.right=doc.languages.find(l=>l.code!==memory.language)?.code||memory.language;$('#right-language').value=memory.right;}await loadColumns();const target=document.querySelector(`#columns [data-block="${mark.index}"][data-language="${mark.language}"]`);if(target){const details=target.closest('details');if(details)details.open=true;target.scrollIntoView({block:'center'});}}catch(error){toast(error.message);}};
    $('#download').onclick=async()=>{try{const data=await source(doc,memory.language);const url=URL.createObjectURL(new Blob([data.raw],{type:'text/markdown;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=data.edition.file.split('/').pop();a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){toast(e.message);}};
    const docs=memory.collection?collectionDocs(memory.collection):[],index=docs.findIndex(d=>d.id===doc.id);
    $('#reader-bottom').innerHTML=(index>0?`<a href="${esc(docURL(docs[index-1].id))}">← Anterior<br>${esc(title(docs[index-1]))}</a>`:'<span></span>')+(index>=0&&index<docs.length-1?`<a href="${esc(docURL(docs[index+1].id))}">Próximo →<br>${esc(title(docs[index+1]))}</a>`:'');
    document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===memory.mode)));$('#right-label').hidden=memory.mode==='read';
    await loadColumns();if(token===memory.render&&memory.positions.has(doc.id))window.scrollTo({top:memory.positions.get(doc.id)});
  }
  function editorial(doc){
    content.innerHTML=crumbs([['Área editorial'],[doc.id]])+`<div class="editor-banner"><strong>Demonstração editorial.</strong> Você pode experimentar campos e conferir diferenças. Nada será salvo.</div><div class="section-title"><div><p class="eyebrow">Documento ativo · ${esc(doc.id)}</p><h1>${esc(title(doc))}</h1></div><a class="btn" href="${esc(docURL(doc.id))}">← Voltar à leitura</a></div><nav class="editor-tabs" aria-label="Seções da ficha"><button data-editor="metadata" aria-pressed="true">Metadados</button><button data-editor="versions" aria-pressed="false">Versões e traduções</button><button data-editor="collections" aria-pressed="false">Coleções</button><button data-editor="history" aria-pressed="false">Histórico</button></nav><section class="editor-card" id="editor-card"></section>`;
    const values={title:title(doc),date:date(doc),archive:doc.archive||'',source:doc.source_url||''};let draft={...values};
    function tab(which){
      document.querySelectorAll('[data-editor]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.editor===which)));
      const area=$('#editor-card');
      if(which==='metadata'){
        area.innerHTML=`<h2>Identificação e procedência</h2><p class="muted">Campos demonstrativos preenchidos a partir do acervo. A ficha real continua disponível no backend local.</p><form id="metadata-form"><div class="form-grid"><label class="wide">Título de apresentação<input name="title" value="${esc(draft.title)}"></label><label>Data apresentada<input name="date" value="${esc(draft.date)}"></label><label>Identificador<input value="${esc(doc.id)}" readonly></label><label class="wide">Referência arquivística ou bibliográfica<textarea name="archive">${esc(draft.archive)}</textarea></label><label class="wide">URL de procedência<input name="source" value="${esc(draft.source)}"></label></div><div class="editor-actions"><button class="btn primary">Conferir alterações</button><span>Prévia demonstrativa · sem gravação</span></div></form><div id="diff"></div>`;
        $('#metadata-form').oninput=e=>{if(e.target.name)draft[e.target.name]=e.target.value;$('#diff').replaceChildren();};
        $('#metadata-form').onsubmit=e=>{e.preventDefault();draft=Object.fromEntries(new FormData(e.target));const labels={title:'Título',date:'Data',archive:'Referência',source:'Procedência'};const changes=Object.keys(values).filter(k=>values[k]!==draft[k]);$('#diff').innerHTML=`<div class="diff"><h2>Prévia das alterações</h2>${changes.length?`<table><thead><tr><th>Campo</th><th>Antes</th><th>Proposta</th></tr></thead><tbody>${changes.map(k=>`<tr><th>${labels[k]}</th><td>${esc(values[k])||'—'}</td><td>${esc(draft[k])||'—'}</td></tr>`).join('')}</tbody></table><p class="muted">Fim da demonstração: nenhum arquivo foi alterado.</p>`:'<p>Nenhuma alteração para comparar.</p>'}</div>`;};
      }else if(which==='versions'){
        area.innerHTML='<h2>Versões e traduções</h2><p class="muted">A prévia não atribui estados de revisão às traduções existentes.</p>'+doc.languages.map(l=>`<div class="version-row"><div><strong>${esc(names[l.code]||l.code)}</strong><p>${esc(l.file)}</p><span class="status">Revisão não classificada nesta prévia</span></div><a class="btn" href="${esc(docURL(doc.id))}&idioma=${code(l.code)}">Ler versão ↗</a></div>`).join('')+'<p style="margin-top:24px">Importação e edição Markdown permanecem na área editorial atual. Nenhum envio é realizado por este protótipo.</p>';
      }else if(which==='collections'){
        const collections=memory.manifest.collections.filter(c=>collectionDocs(c).some(d=>d.id===doc.id));area.innerHTML='<h2>Organização no acervo</h2>'+collections.map(c=>`<div class="version-row"><strong>${esc(title(c))}</strong><a class="btn" href="#/colecao/${code(c.id)}">Explorar ↗</a></div>`).join('')+'<p class="muted" style="margin-top:24px">As associações são lidas do manifesto; o texto mantém uma identidade única.</p>';
      }else area.innerHTML='<h2>Histórico recuperável</h2><p>O histórico real continua no backend local. Esta prévia não cria operações nem consulta cópias privadas.</p><p class="muted">Na interface definitiva, esta seção reunirá as operações do documento e os caminhos de conferência e restauração existentes.</p>';
    }
    document.querySelectorAll('[data-editor]').forEach(b=>b.onclick=()=>tab(b.dataset.editor));tab('metadata');
  }
  function benchURL(id){const tab=memory.tabs.find(t=>t.id===id);return '#/trabalho/'+code(id)+(tab?.collection?'?colecao='+code(tab.collection):'');}
  function renderTabs(){
    const root=$('#workspace-tabs');root.innerHTML=memory.tabs.map(tab=>{const doc=memory.docs.get(tab.id);return `<div class="document-tab ${memory.document?.id===tab.id?'active':''}"><a href="${esc(benchURL(tab.id))}" ${memory.document?.id===tab.id?'aria-current="page"':''} title="${esc(title(doc))}"><span>¶</span>${esc(title(doc))}</a><button type="button" data-close-tab="${esc(tab.id)}" aria-label="Fechar ${esc(title(doc))}">×</button></div>`;}).join('')+'<button type="button" class="new-tab" aria-label="Abrir outro documento" title="Abrir outro documento">＋</button>';
    root.querySelector('.new-tab').onclick=openDocumentPicker;
    root.querySelectorAll('[data-close-tab]').forEach(b=>b.onclick=()=>{
      const id=b.dataset.closeTab,index=memory.tabs.findIndex(t=>t.id===id);
      if([...memory.drafts.keys()].some(key=>key.startsWith(id+':'))||memory.notes.get(id)){if(!confirm('Este documento tem rascunhos nesta prévia. Fechar a aba descarta esses rascunhos. Continuar?'))return;}
      memory.tabs.splice(index,1);[...memory.drafts.keys()].filter(key=>key.startsWith(id+':')).forEach(key=>memory.drafts.delete(key));memory.notes.delete(id);persistTabs();
      if(memory.document?.id===id){const next=memory.tabs[Math.min(index,memory.tabs.length-1)];location.hash=next?benchURL(next.id):'#/inicio';}else renderTabs();
    });
    root.querySelector('[aria-current="page"]')?.scrollIntoView({block:'nearest',inline:'nearest'});
  }
  function persistTabs(){remember('open-tabs',JSON.stringify(memory.tabs));}
  function openDocumentPicker(){
    const dialog=document.createElement('dialog');dialog.className='document-picker';
    dialog.innerHTML='<form method="dialog"><button class="dialog-close" aria-label="Fechar seleção de documento">×</button></form><p class="eyebrow">Bancada de pesquisa</p><h2>Abrir outro documento</h2><label>Buscar por título ou identificador<input type="search" class="picker-search" placeholder="Ex.: Nikolaev, 1665, sentença…"></label><p class="muted picker-count" aria-live="polite"></p><div class="picker-results"></div>';
    document.body.append(dialog);const input=dialog.querySelector('input'),results=dialog.querySelector('.picker-results');
    function update(){const q=fold(input.value);const matches=[...memory.docs.values()].filter(d=>fold([d.id,d.title_pt,d.title_ru,d.title_en].join(' ')).includes(q));dialog.querySelector('.picker-count').textContent=matches.length+' documentos · exibindo até 30';results.innerHTML=matches.slice(0,30).map(d=>`<button type="button" data-pick="${esc(d.id)}"><strong>${esc(title(d))}</strong><small>${esc(d.id)} · ${d.languages.map(l=>esc(l.code.toUpperCase())).join(' / ')}</small></button>`).join('')||'<p>Nenhum título ou identificador encontrado.</p>';results.querySelectorAll('[data-pick]').forEach(b=>b.onclick=()=>{const id=b.dataset.pick;if(!memory.tabs.some(t=>t.id===id)){const c=memory.manifest.collections.find(c=>collectionDocs(c).some(d=>d.id===id));memory.tabs.push({id,collection:c?.id||''});}persistTabs();dialog.close();location.hash=benchURL(id);});}
    input.oninput=update;input.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();results.querySelector('button')?.click();}};dialog.onclose=()=>dialog.remove();update();dialog.showModal();input.focus();
  }
  async function workbench(doc){
    const token=memory.render;
    if(!memory.tabs.some(t=>t.id===doc.id))memory.tabs.push({id:doc.id,collection:memory.collection?.id||''});persistTabs();renderTabs();
    await reader(doc);if(token!==memory.render)return;
    const controls=$('.tool-head');controls.insertAdjacentHTML('beforeend',`<a class="btn quiet" href="${esc(docURL(doc.id))}">Leitor público ↗</a>`);
    document.querySelectorAll('[data-panel]').forEach(b=>b.remove());
    const dock=document.createElement('aside');dock.className='research-dock';dock.setAttribute('aria-label','Instrumento de pesquisa do documento ativo');
    dock.innerHTML='<div class="dock-heading"><strong id="dock-title">Markdown e prévia</strong><button type="button" class="btn quiet" id="close-dock" aria-label="Recolher instrumento">×</button></div><div class="dock-content" id="dock-content"></div>';
    $('.reader-workspace').append(dock);let toolRequest=0;
    $('#close-dock').onclick=()=>{dock.hidden=true;document.querySelector('[data-tool][aria-pressed="true"]')?.focus();document.querySelectorAll('[data-tool]').forEach(b=>b.setAttribute('aria-pressed','false'));};
    memory.openTool=async which=>{
      ++toolRequest;if(token!==memory.render)return;dock.hidden=false;
      const toolState=memory.docStates.get(doc.id)||{};toolState.tool=which;memory.docStates.set(doc.id,toolState);
      document.querySelectorAll('[data-tool]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.tool===which)));
      const area=$('#dock-content');const labels={markdown:'Markdown e prévia',index:'Índice do documento',metadata:'Ficha documental',notes:'Notas de trabalho'};$('#dock-title').textContent=labels[which];
      if(which==='markdown'){
        const language=memory.docStates.get(doc.id)?.dockLanguage||memory.language;
        area.innerHTML=`<div class="dock-controls"><label>Versão <select id="dock-language">${options(doc,language)}</select></label><div class="segment"><button type="button" data-dock-view="source" aria-pressed="true">Markdown</button><button type="button" data-dock-view="preview" aria-pressed="false">Prévia</button></div></div><p class="dock-note">Rascunho nesta página · não salva no acervo.</p><div id="dock-editor"><p role="status">Carregando versão…</p></div>`;
        async function loadEditor(){
          const language=$('#dock-language').value,localRequest=++toolRequest,key=doc.id+':'+language;
          const state=memory.docStates.get(doc.id)||{};state.dockLanguage=language;memory.docStates.set(doc.id,state);
          try{
            const data=await source(doc,language);if(token!==memory.render||localRequest!==toolRequest)return;
            $('#dock-editor').innerHTML='<label class="sr-only" for="markdown-draft">Texto-fonte da versão selecionada</label><textarea id="markdown-draft" spellcheck="false"></textarea><div id="markdown-preview" class="prose" hidden></div><div class="dock-foot"><button type="button" class="btn" id="refresh-preview">Atualizar prévia</button><span id="draft-status">Arquivo preservado</span></div>';
            const textarea=$('#markdown-draft');textarea.value=memory.drafts.get(key)??data.raw;
            function updatePreview(){const body=splitExportHeaders(textarea.value).body;$('#markdown-preview').innerHTML=DOMPurify.sanitize(data.edition.format==='text'?'<pre>'+esc(body)+'</pre>':md.render(body));}
            function changeView(view){const preview=view==='preview';textarea.hidden=preview;$('#markdown-preview').hidden=!preview;document.querySelectorAll('[data-dock-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.dockView===view)));const state=memory.docStates.get(doc.id)||{};state.dockView=view;memory.docStates.set(doc.id,state);if(preview)updatePreview();}
            let previewTimer;
            textarea.oninput=()=>{if(textarea.value===data.raw)memory.drafts.delete(key);else memory.drafts.set(key,textarea.value);$('#draft-status').textContent=memory.drafts.has(key)?'Rascunho não salvo':'Arquivo preservado';clearTimeout(previewTimer);if(textarea.value.length<80000)previewTimer=setTimeout(()=>{if(token===memory.render&&localRequest===toolRequest&&$('#markdown-preview'))updatePreview();},350);};
            document.querySelectorAll('[data-dock-view]').forEach(b=>b.onclick=()=>changeView(b.dataset.dockView));$('#refresh-preview').onclick=()=>changeView('preview');
            $('#draft-status').textContent=memory.drafts.has(key)?'Rascunho não salvo':'Arquivo preservado';
            changeView(memory.docStates.get(doc.id)?.dockView||'source');
          }catch(error){if(token===memory.render&&localRequest===toolRequest)$('#dock-editor').textContent=error.message;}
        }
        $('#dock-language').onchange=loadEditor;loadEditor();
      }else if(which==='index'){
        area.innerHTML='<p class="dock-note">Títulos da versão principal exibida. Atualize após mudar de idioma ou modo.</p><button class="btn" id="refresh-outline">Atualizar índice</button><nav class="dock-outline" aria-label="Seções do documento"></nav>';
        function outline(){const nav=area.querySelector('nav');nav.replaceChildren();const headings=[...document.querySelectorAll('#columns .primary-cell h1,#columns .primary-cell h2,#columns .primary-cell h3')];if(!headings.length)nav.textContent='Esta versão não tem títulos Markdown para gerar um índice.';headings.forEach(h=>{const b=document.createElement('button');b.type='button';b.textContent=h.textContent;b.onclick=()=>h.scrollIntoView({block:'start'});nav.append(b);});}$('#refresh-outline').onclick=outline;outline();
      }else if(which==='metadata'){
        area.innerHTML=`<dl class="dock-metadata"><dt>Documento</dt><dd>${esc(doc.id)}</dd><dt>Título</dt><dd>${esc(title(doc))}</dd><dt>Data apresentada</dt><dd>${esc(date(doc)||'Não cadastrada')}</dd><dt>Referência</dt><dd>${esc(doc.archive||'Não cadastrada')}</dd><dt>Fonte cadastrada</dt><dd>${esc(doc.source_url||doc.source_name||'Não cadastrada')}</dd><dt>Idiomas disponíveis</dt><dd>${doc.languages.map(l=>esc(names[l.code]||l.code)).join(' · ')}</dd></dl><a class="btn" href="${esc(docURL(doc.id,true))}">Abrir ficha editorial</a>`;
      }else{
        area.innerHTML='<p class="dock-note">Notas deste documento, conservadas apenas enquanto esta página estiver aberta. Não são notas públicas nem alterações na fonte.</p><label for="research-notes">Seu rascunho</label><textarea id="research-notes" placeholder="Referências para conferir, dúvidas de tradução, passagens a comparar…"></textarea>';
        $('#research-notes').value=memory.notes.get(doc.id)||'';$('#research-notes').oninput=e=>memory.notes.set(doc.id,e.target.value);
      }
    };
    memory.openTool(memory.docStates.get(doc.id)?.tool||'markdown');
  }
  function showInfo(heading,...paragraphs){const dialog=$('#info');dialog.querySelector('h2').textContent=heading;dialog.querySelectorAll('p').forEach(p=>p.remove());paragraphs.forEach(text=>{const p=document.createElement('p');p.textContent=text;dialog.append(p);});dialog.showModal();}
  async function route(){
    if(['documento','trabalho'].includes(memory.currentView)&&memory.document){
      memory.positions.set(memory.document.id,window.scrollY);
      const state=memory.docStates.get(memory.document.id)||{};Object.assign(state,{language:memory.language,right:memory.right,mode:memory.mode});memory.docStates.set(memory.document.id,state);
    }
    memory.openTool=null;memory.render++;const token=memory.render;
    const [path,query='']=location.hash.slice(2).split('?');const [view='inicio',rawId]=path.split('/');const params=new URLSearchParams(query);
    memory.currentView=view;
    try{
      const id=rawId?decodeURIComponent(rawId):'';
      memory.collection=memory.manifest.collections.find(c=>c.id===(view==='colecao'?id:params.get('colecao')))||null;
      memory.query=params.get('q')||'';memory.sub=params.get('sub')||'';memory.page=Math.max(0,Number.parseInt(params.get('page'),10)||0);
      side(view);$('#workspace-state').textContent=view==='trabalho'?'Bancada · rascunhos sem gravação':view==='documento'?'Leitura pública':'Acervo em modo de leitura';window.scrollTo({top:0});
      if(view==='trabalho')setCollapsed(recall('tools-collapsed',String(innerWidth<=900))==='true');
      if(view==='inicio'||!view)home();
      else if(view==='busca')catalog(true);
      else if(view==='colecao'){if(!memory.collection)throw new Error('Coleção não encontrada.');catalog();}
      else if(['documento','editorial','trabalho'].includes(view)){
        const doc=memory.docs.get(id);if(!doc)throw new Error('Documento não encontrado.');memory.document=doc;
        const state=memory.docStates.get(id);if(state){memory.language=state.language||memory.language;memory.right=state.right||'ru';memory.mode=state.mode||'read';}
        if(params.get('idioma'))memory.language=params.get('idioma');
        $('#bench-nav').href='#/trabalho/'+code(doc.id)+(memory.collection?'?colecao='+code(memory.collection.id):'');
        if(view==='trabalho')await workbench(doc);
        else if(view==='documento'){
          await reader(doc);if(token!==memory.render)return;
          $('.tool-head').insertAdjacentHTML('beforeend',`<a class="btn quiet" href="${esc('#/trabalho/'+code(doc.id)+(memory.collection?'?colecao='+code(memory.collection.id):''))}">Abrir na bancada ↗</a>`);
        }else editorial(doc);
      }else throw new Error('Tela não encontrada no protótipo.');
      if(token===memory.render){content.focus({preventScroll:true});document.title=(view==='inicio'?'Acervo':view==='busca'?'Busca':view==='colecao'?title(memory.collection):title(memory.document))+' — Protótipo';}
    }catch(error){if(token===memory.render)content.innerHTML=`<h1>Não foi possível abrir esta tela</h1><p>${esc(error.message)}</p><a class="btn" href="#/inicio">Voltar ao acervo</a>`;}
  }
  function setCollapsed(collapsed){$('#shell').classList.toggle('is-collapsed',collapsed);$('#sidebar-body').hidden=collapsed;$('#collapse').textContent=collapsed?'›':'‹';$('#collapse').setAttribute('aria-expanded',String(!collapsed));$('#collapse').setAttribute('aria-label',collapsed?'Expandir instrumentos':'Recolher instrumentos');remember('tools-collapsed',String(collapsed));}
  $('#collapse').onclick=()=>setCollapsed(!$('#shell').classList.contains('is-collapsed'));
  document.body.dataset.palette='crimson';
  window.addEventListener('beforeunload',event=>{if(memory.drafts.size||[...memory.notes.values()].some(Boolean)){event.preventDefault();event.returnValue='';}});
  $('.skip').onclick=e=>{e.preventDefault();content.focus();};
  document.addEventListener('click',event=>{
    const link=event.target.closest('.prose a[href^="#"]');if(!link)return;event.preventDefault();
    let id;try{id=decodeURIComponent(link.getAttribute('href').slice(1));}catch{return;}
    const cell=link.closest('[data-block]'),root=cell?$('#columns'):link.closest('.prose');
    const target=[...root.querySelectorAll('[id]')].find(n=>n.id===id&&(!cell||n.closest('[data-language]')?.dataset.language===cell.dataset.language));
    if(target){const details=target.closest('details');if(details)details.open=true;target.scrollIntoView({block:'center'});target.setAttribute('tabindex','-1');target.focus({preventScroll:true});}
  });
  memory.language=recall('language','pt');
  fetch('../data/manifest.json').then(response=>{if(!response.ok)throw new Error('Manifesto indisponível.');return response.json();}).then(manifest=>{memory.manifest=manifest;[...(manifest.documents||[]),...manifest.collections.flatMap(c=>c.documents||[])].forEach(d=>memory.docs.set(d.id,d));try{memory.tabs=JSON.parse(recall('open-tabs','[]')).filter(t=>t&&memory.docs.has(t.id));}catch{memory.tabs=[];}window.addEventListener('hashchange',route);route();}).catch(error=>{content.innerHTML=`<h1>Acervo indisponível</h1><p>${esc(error.message)} Abra o protótipo pelo servidor do projeto, não diretamente pelo arquivo.</p>`;});
})();
