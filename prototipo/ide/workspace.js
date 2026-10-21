/* Protótipo funcional isolado. A gravação canônica permanece nos formulários existentes. */
'use strict';
(() => {
  const base=new URL('../../',location.href), $=id=>document.getElementById(id);
  const url=path=>new URL(path,base).href;
  const views=new Map(), frames=new WeakMap();
  const docs=new Map(), models=new Map(), groups=[{tabs:[],active:null}], events=[];
  let manifest,projects=[],project='',section='explorer',activeGroup=0,layout='right',ratio=50,bottom='activity',backend=false,serial=0,drag=null,sidebarQuery='';
  const labels={pt:'Português',ru:'Русский',en:'English'};
  const md=window.markdownit({html:false,linkify:true,typographer:false});
  if(window.markdownitFootnote)md.use(window.markdownitFootnote);
  function node(tag,props={},children=[]){const n=document.createElement(tag);for(const [k,v] of Object.entries(props)){if(k==='text')n.textContent=v;else if(k==='class')n.className=v;else n.setAttribute(k,String(v));}for(const c of children)n.append(c);return n;}
  function button(text,action,props={}){const n=node('button',{type:'button',text,...props});n.onclick=action;return n;}
  function tell(text){$('announcements').textContent=text;$('announcements').hidden=false;clearTimeout(tell.timer);tell.timer=setTimeout(()=>$('announcements').hidden=true,6500);}
  function read(key,fallback=null){try{return JSON.parse(sessionStorage.getItem('discoveryIDE:'+key))??fallback;}catch{return fallback;}}
  function write(key,value){try{sessionStorage.setItem('discoveryIDE:'+key,JSON.stringify(value));return true;}catch{tell('Armazenamento da sessão indisponível ou cheio. Baixe seus rascunhos antes de sair.');return false;}}
  function title(d){return d?.title_pt||d?.shortTitle||d?.title_ru||d?.id||'Documento';}
  function normalize(s){return String(s).normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();}
  const selectedProject=()=>projects.find(p=>p.id===project);
  const visibleDocs=()=>[...docs.values()].filter(d=>!project||selectedProject()?.document_ids.includes(d.id));
  function log(text){events.unshift({time:new Date().toLocaleTimeString('pt-BR'),text});if(events.length>70)events.pop();renderBottom();}
  function scopeKey(id,lang){return [project||'acervo',id,lang].join('|');}
  function currentTab(){const g=groups[activeGroup];return g?.tabs.find(t=>t.key===g.active);}
  function persistTabs(){write('tabs',groups.flatMap(g=>g.tabs).filter(t=>!t.project&&t.type!=='tool').map(({type,id,lang})=>({type,id,lang})));}
  function setSidebar(hidden){document.body.classList.toggle('sidebar-hidden',hidden);$('toggle-sidebar').setAttribute('aria-expanded',String(!hidden));write('sidebarHidden',hidden);}
  function setBottom(hidden){document.body.classList.toggle('bottom-hidden',hidden);$('toggle-bottom').setAttribute('aria-expanded',String(!hidden));write('bottomHidden',hidden);}
  function status(){const t=currentTab();$('scope-status').textContent=project?'Projeto privado: '+selectedProject()?.title:'Sem projeto · acervo';$('workspace-label').textContent=project?selectedProject()?.title+' / Workspace privado':'Acervo / Área de trabalho';$('document-status').textContent=t?.id?`${t.id} · ${labels[t.lang]||t.type}`:'Nenhum documento ativo';const dirty=[...models.values()].filter(m=>m.text!==m.original).length;$('draft-status').textContent=dirty?`${dirty} rascunho(s) de sessão · sem gravação no acervo`:'Sem gravação automática no acervo';}
  async function json(path){const r=await fetch(url(path),{cache:'no-store'});if(!r.ok)throw Error('Recurso indisponível ('+r.status+')');return r.json();}
  async function loadModel(tab){
    const key=[tab.project||'acervo',tab.id,tab.lang].join('|');if(models.has(key))return models.get(key);
    const d=docs.get(tab.id),edition=d?.languages.find(l=>l.code===tab.lang);if(!edition)throw Error('Versão não cadastrada.');
    const pending=(async()=>{let text,privateDraft=false;
      if(tab.project){const data=await json('api/editorial/workspace/edition?'+new URLSearchParams({project:tab.project,edition:tab.id+':'+tab.lang}));text=data.content;privateDraft=data.has_draft;}
      else{const r=await fetch(url(edition.file),{cache:'no-store'});if(!r.ok)throw Error('Não foi possível carregar o texto ('+r.status+').');text=await r.text();}
      const stored=read('draft:'+key);if(stored&&stored.baseline!==text)write('recovery:'+key,stored);let recovered=stored&&stored.baseline===text?stored.text:text;
      if(stored&&stored.baseline!==text){tell('A fonte de '+tab.id+' mudou. Seu rascunho anterior foi preservado como recuperação separada na aba Markdown.');}
      return {key,text:recovered,original:text,privateDraft,conflict:read('recovery:'+key)};})();
    models.set(key,pending);try{const model=await pending;models.set(key,model);return model;}catch(e){models.delete(key);throw e;}
  }
  function newTab(type,id=null,lang=null,extra={}){return {key:'tab-'+(++serial),type,id,lang:lang||docs.get(id)?.languages.find(l=>l.code==='pt')?.code||docs.get(id)?.languages[0]?.code,project,...extra};}
  function open(type,id=null,lang=null,target=activeGroup,extra={}){
    const g=groups[target]||groups[0];target=groups.indexOf(g);
    const p=extra.project??project;
    const existing=g.tabs.find(t=>t.type===type&&t.id===id&&t.project===p&&(!lang||t.lang===lang)&&t.route===extra.route&&t.area===extra.area);
    const tab=existing||newTab(type,id,lang,{...extra,project:p});if(!existing)g.tabs.push(tab);
    g.active=tab.key;activeGroup=target;renderGroups();persistTabs();status();if(innerWidth<640)setSidebar(true);return tab;
  }
  function split(direction='right'){
    layout=direction;if(groups.length===1)groups.push({tabs:[],active:null});
    renderGroups();log(direction==='right'?'Grupo lateral aberto. Arraste uma aba para ele.':'Grupo inferior aberto. Arraste uma aba para ele.');
  }
  function moveTab(key,target,index=null){
    const source=groups.find(g=>g.tabs.some(t=>t.key===key)),tab=source?.tabs.find(t=>t.key===key);if(!tab||!groups[target])return;
    if(tab.type==='tool'&&source!==groups[target]&&!confirm('Mover este formulário para outro grupo recarrega a ferramenta. Salve ou copie as alterações ainda não confirmadas antes de continuar. Mover?'))return;
    source.tabs.splice(source.tabs.indexOf(tab),1);if(source.active===key)source.active=source.tabs.at(-1)?.key||null;
    groups[target].tabs.splice(index??groups[target].tabs.length,0,tab);groups[target].active=key;activeGroup=target;renderGroups();persistTabs();status();
  }
  function closeTab(g,tab){
    if(tab.type==='tool'&&!confirm('Fechar esta ferramenta? Alterações ainda não confirmadas no formulário podem ser perdidas.'))return;
    const model=models.get([tab.project||'acervo',tab.id,tab.lang].join('|'));
    if(tab.type==='markdown'&&model?.text!==undefined&&model.text!==model.original&&!confirm('Fechar o editor? O rascunho permanece nesta sessão, mas ainda não está salvo no acervo.'))return;
    views.get(tab.key)?.remove();views.delete(tab.key);
    g.tabs.splice(g.tabs.indexOf(tab),1);if(g.active===tab.key)g.active=g.tabs.at(-1)?.key||null;renderGroups();persistTabs();status();
  }
  function tabTitle(t){if(t.type==='area')return areaLabels[t.area];if(t.type==='tool')return t.label;const suffix={text:'Leitura',markdown:'Markdown',metadata:'Ficha',outline:'Índice'}[t.type];return (docs.get(t.id)?.shortTitle||title(docs.get(t.id)))+' · '+suffix;}
  function renderGroups(){
    const root=$('editors');root.className=groups.length>1?'split-'+layout:'';root.style.removeProperty('grid-template-columns');root.style.removeProperty('grid-template-rows');
    const liveFrames=new Set();
    groups.forEach((g,index)=>{
      let frame=frames.get(g);if(!frame){frame=node('section',{class:'editor-group'+(index===activeGroup?' active-group':''),'aria-label':'Grupo de editores '+(index+1)});frames.set(g,frame);root.append(frame);}
      liveFrames.add(frame);frame.classList.toggle('active-group',index===activeGroup);
      frame.onpointerdown=()=>{activeGroup=index;document.querySelectorAll('.editor-group').forEach((f,i)=>f.classList.toggle('active-group',i===index));status();};
      const strip=node('div',{class:'tabstrip',role:'tablist','aria-label':'Abas do grupo '+(index+1)});
      for(const tab of g.tabs){const active=tab.key===g.active;const holder=node('div',{class:'tab'+(active?' active':''),draggable:'true'});
        const select=button(tabTitle(tab),()=>{g.active=tab.key;activeGroup=index;renderGroups();status();},{class:'tab-select',role:'tab','aria-selected':active,'aria-controls':'content-'+tab.key,id:'select-'+tab.key,title:tabTitle(tab),tabindex:active?'0':'-1'});
        select.onkeydown=e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();let i=g.tabs.indexOf(tab);i=e.key==='Home'?0:e.key==='End'?g.tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+g.tabs.length)%g.tabs.length;g.active=g.tabs[i].key;renderGroups();$('editors').querySelectorAll('.tabstrip')[index].querySelector('[aria-selected=true]')?.focus();};
        holder.append(select,button('×',()=>closeTab(g,tab),{class:'close','aria-label':'Fechar '+tabTitle(tab)}));
        holder.ondragstart=e=>{drag=tab.key;e.dataTransfer.setData('text/plain',tab.key);e.dataTransfer.effectAllowed='move';};holder.ondragend=()=>{drag=null;document.querySelectorAll('.drop-target').forEach(n=>n.classList.remove('drop-target'));};
        holder.ondragover=e=>{if(drag){e.preventDefault();e.stopPropagation();}};
        holder.ondrop=e=>{if(!drag)return;e.preventDefault();e.stopPropagation();moveTab(drag,index,g.tabs.indexOf(tab));drag=null;};strip.append(holder);
      }
      strip.append(button('＋',()=>palette(),{class:'group-menu','aria-label':'Abrir documento ou comando'}));
      if(groups.length>1)strip.append(button('⇄',()=>{const t=g.tabs.find(t=>t.key===g.active);if(t)moveTab(t.key,index===0?1:0);},{title:'Mover aba ativa para o outro grupo','aria-label':'Mover aba ativa para o outro grupo'}));
      if(groups.length>1)strip.append(button('⊗',()=>{if(g.tabs.some(t=>t.type==='tool')&&!confirm('Reunir os grupos recarrega os formulários movidos. Salve ou copie as alterações antes de continuar. Reunir?'))return;const other=index===0?1:0;groups[other].tabs.push(...g.tabs);groups.splice(index,1);activeGroup=0;renderGroups();persistTabs();status();},{title:'Reunir este grupo no outro','aria-label':'Reunir grupos'}));
      const oldStrip=frame.querySelector('.tabstrip');if(oldStrip)oldStrip.replaceWith(strip);else frame.prepend(strip);
      let empty=frame.querySelector('.empty-group');
      if(g.tabs.length){empty?.remove();}
      else if(!empty){empty=node('div',{class:'editor-content empty-group'});frame.append(empty);welcome(empty,index);}
      for(const tab of g.tabs){
        let content=views.get(tab.key),fresh=!content;
        if(fresh){content=node('div',{class:'editor-content',id:'content-'+tab.key,role:'tabpanel',tabindex:'0','aria-labelledby':'select-'+tab.key});views.set(tab.key,content);}
        content.hidden=tab.key!==g.active;
        if(content.parentElement!==frame)frame.append(content);
        if(fresh)renderTab(content,tab,index);
      }
      frame.ondragover=e=>{if(drag){e.preventDefault();frame.classList.add('drop-target');}};frame.ondragleave=e=>{if(!frame.contains(e.relatedTarget))frame.classList.remove('drop-target');};frame.ondrop=e=>{if(!drag)return;e.preventDefault();moveTab(drag,index);drag=null;};
    });
    for(const child of [...root.children])if(!liveFrames.has(child))child.remove();
    if(groups.length>1){
      const divider=node('div',{class:'group-divider',role:'separator',tabindex:'0','aria-label':'Redimensionar grupos','aria-valuemin':'25','aria-valuemax':'75'});
      const vertical=()=>layout==='right'&&innerWidth>1000;
      const adjust=value=>{ratio=Math.max(25,Math.min(75,value));root.style.setProperty('--group-ratio',ratio+'%');root.style.removeProperty('grid-template-columns');root.style.removeProperty('grid-template-rows');root.style.setProperty(vertical()?'grid-template-columns':'grid-template-rows',`minmax(0,${ratio}fr) minmax(0,${100-ratio}fr)`);divider.setAttribute('aria-valuenow',String(Math.round(ratio)));divider.setAttribute('aria-orientation',vertical()?'vertical':'horizontal');};
      divider.onpointerdown=e=>{e.preventDefault();divider.setPointerCapture(e.pointerId);};
      divider.onpointermove=e=>{if(!divider.hasPointerCapture(e.pointerId))return;const r=root.getBoundingClientRect();adjust(vertical()?(e.clientX-r.left)/r.width*100:(e.clientY-r.top)/r.height*100);};
      divider.onkeydown=e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();adjust(ratio+(['ArrowRight','ArrowDown'].includes(e.key)?5:-5));};root.append(divider);adjust(ratio);
    }
  }
  function welcome(root,index){
    const box=node('div',{class:'welcome'});box.append(node('p',{class:'eyebrow',text:'ShowTrials Discovery / bancada de pesquisa'}),node('h1',{text:index?'Um segundo ponto de vista.':'Documentos, ferramentas e contexto.'}),node('p',{text:'Leia, compare e prepare fontes históricas em um único espaço de trabalho. Arraste abas entre grupos ou use o comando mover.'}));
    box.append(node('div',{class:'welcome-actions'},[button('Abrir documento',()=>palette(),{class:'primary'}),button('Explorar fontes PDF',()=>tool('pdf','Fontes PDF'))]));
    const grid=node('div',{class:'welcome-grid'});
    for(const [heading,text] of [['Explorar','Coleções ou documentos do projeto escolhido. Sem projeto ativo na entrada.'],['Comparar','Abra leitura, Markdown, índice e ficha em abas independentes.'],['Preparar','PDF, OCR e revisão permanecem nos fluxos existentes, dentro de uma aba.'],['Conferir antes de salvar','Rascunhos daqui ficam na sessão. Os formulários editoriais mantêm prévia e histórico.']])grid.append(node('section',{},[node('h2',{text:heading}),node('p',{text})]));box.append(grid);root.append(box);
  }
  async function renderTab(root,tab,index){
    const stamp=Symbol();root.renderStamp=stamp;const targetIndex=()=>Math.max(0,groups.findIndex(g=>g.tabs.includes(tab)));root.replaceChildren();
    if(tab.type==='tool'){renderTool(root,tab);return;}
    if(tab.type==='area'){renderArea(root,tab);return;}
    root.append(node('p',{class:'subtle',text:'Carregando documento…'}));
    try{const model=await loadModel(tab);if(!root.isConnected||root.renderStamp!==stamp)return;root.replaceChildren();
      root.append(node('div',{class:'breadcrumbs',text:(tab.project?'Projeto privado / ':'Acervo / ')+tab.id+' / '+(labels[tab.lang]||tab.lang)}));
      const controls=node('div',{class:'document-toolbar'}),select=node('select',{'aria-label':'Idioma desta aba'});
      for(const l of docs.get(tab.id).languages)select.append(node('option',{value:l.code,text:labels[l.code]||l.code}));select.value=tab.lang;
      select.onchange=()=>{tab.lang=select.value;renderTab(root,tab,index);persistTabs();status();};controls.append(select);
      for(const [type,label] of [['text','Leitura'],['markdown','Markdown'],['outline','Índice'],['metadata','Ficha']])controls.append(button(label,()=>open(type,tab.id,tab.lang,targetIndex(),{project:tab.project}),{'aria-pressed':tab.type===type}));
      controls.append(node('span',{class:'spacer'}));
      controls.append(button('Ao lado',()=>{if(groups.length===1)split('right');open(tab.type==='markdown'?'text':'markdown',tab.id,tab.lang,targetIndex()===0?1:0,{project:tab.project});},{title:'Abrir a outra perspectiva no outro grupo'}));
      if(backend)controls.append(button('Editar e salvar…',()=>editorFor(tab),{title:'Abrir o fluxo editorial com prévia e histórico'}));
      root.append(controls);
      if(tab.type==='metadata'){renderFacts(root,tab,model);return;}
      if(tab.type==='outline'){renderOutline(root,tab,model);return;}
      if(tab.type==='markdown'){renderMarkdown(root,tab,model);return;}
      if(model.text!==model.original)root.append(node('p',{class:'editor-note',text:'Prévia do rascunho de sessão. Esta versão ainda não foi gravada no acervo.'}));
      const article=node('article',{class:'article',lang:tab.lang});article.innerHTML=DOMPurify.sanitize(md.render(model.text));
      for(const item of article.querySelectorAll('[id]'))item.id=tab.key+'-'+item.id;
      for(const link of article.querySelectorAll('a')){const href=link.getAttribute('href');if(href?.startsWith('#'))link.setAttribute('href','#'+tab.key+'-'+href.slice(1));}
      for(const image of article.querySelectorAll('img'))image.loading='lazy';
      let block=0;for(const n of article.querySelectorAll('p,li,blockquote,table,h1,h2,h3,h4,h5,h6')){if(n.closest('li')!==n&&n.closest('li'))continue;n.dataset.block=String(++block);const marker=read('marker:'+model.key);n.classList.toggle('marked',marker===block);n.prepend(node('span',{class:'block-number','aria-hidden':'true',text:String(block)}));}
      article.onclick=e=>{if(e.target.closest('a,button,input')||getSelection()?.toString())return;const n=e.target.closest('[data-block]');if(!n)return;const value=Number(n.dataset.block),old=read('marker:'+model.key);write('marker:'+model.key,old===value?null:value);article.querySelectorAll('.marked').forEach(n=>n.classList.remove('marked'));if(old!==value)n.classList.add('marked');};
      article.querySelectorAll('a').forEach(a=>{const href=a.getAttribute('href');if(href?.startsWith('#'))a.onclick=e=>{e.preventDefault();let id;try{id=decodeURIComponent(href.slice(1));}catch{return;}const dest=[...article.querySelectorAll('[id]')].find(n=>n.id===id);dest?.scrollIntoView({block:'center'});};else{a.target='_blank';a.rel='noopener noreferrer';}});
      controls.append(button('Retomar',()=>{article.querySelector('.marked')?.scrollIntoView({block:'center'});if(!article.querySelector('.marked'))tell('Clique em um parágrafo para marcar a posição nesta versão.');}));
      root.append(article);if(tab.scroll)root.scrollTop=tab.scroll;root.onscroll=()=>tab.scroll=root.scrollTop;
    }catch(error){root.replaceChildren(node('div',{class:'facts'},[node('h1',{text:'Não foi possível abrir esta versão'}),node('p',{text:error.message}),button('Tentar novamente',()=>renderTab(root,tab,index))]));}
  }
  function refreshViews(model){for(const g of groups)for(const t of g.tabs){if(t.type!=='markdown'&&[t.project||'acervo',t.id,t.lang].join('|')===model.key){const i=groups.indexOf(g);const root=views.get(t.key);if(root)renderTab(root,t,i);}}status();}
  function renderMarkdown(root,tab,model){
    root.append(node('p',{class:'editor-note',text:'Rascunho da sessão: alterações são recuperadas ao reabrir esta versão neste navegador. Para gravar, use Editar e salvar: no acervo, o rascunho segue para a prévia editorial. Em projeto, baixe ou copie para o editor privado.'}));
    const actions=node('div',{class:'document-toolbar'});actions.append(button('Baixar rascunho',()=>download(tab.id+'.'+tab.lang+'.rascunho.md',model.text)),button('Restaurar fonte carregada',()=>{if(!confirm('Descartar o rascunho desta sessão e restaurar o texto carregado?'))return;model.text=model.original;write('draft:'+model.key,{baseline:model.original,text:model.text});refreshViews(model);input.value=model.text;log('Rascunho restaurado: '+tab.id);status();}));
    if(model.conflict)actions.append(button('Baixar rascunho anterior recuperado',()=>download(tab.id+'.'+tab.lang+'.recuperado.md',model.conflict.text)));
    const input=node('textarea',{class:'source-editor','aria-label':'Rascunho Markdown de '+tab.id,spellcheck:'false',lang:tab.lang});input.value=model.text;
    input.oninput=()=>{model.text=input.value;write('draft:'+model.key,{baseline:model.original,text:model.text});clearTimeout(input.timer);input.timer=setTimeout(()=>refreshViews(model),200);status();};
    root.append(actions,input);
  }
  function download(name,content){const blob=URL.createObjectURL(new Blob([content],{type:'text/markdown;charset=utf-8'})),a=node('a',{href:blob,download:name});a.click();setTimeout(()=>URL.revokeObjectURL(blob),1500);log('Cópia baixada: '+name);}
  function renderFacts(root,tab,model){const d=docs.get(tab.id),body=node('div',{class:'facts'}),dl=node('dl');body.append(node('h1',{text:title(d)}));
    for(const [label,value] of [['Identificador',d.id],['Data documental',d.date],['Referência',d.archive],['Fonte',d.source_name],['Proveniência',d.source_url],['Idiomas',d.languages.map(l=>labels[l.code]||l.code).join(' · ')],['Contexto',tab.project?'Versão do projeto '+selectedProject()?.title:'Versão do acervo'],['Situação do texto',model.privateDraft?'Versão privada já salva':model.text!==model.original?'Rascunho desta sessão':'Texto carregado da fonte']])dl.append(node('dt',{text:label}),node('dd',{text:value||'Não cadastrado'}));body.append(dl);
    if(backend&&!tab.project)body.append(button('Editar metadados…',()=>tool('documento/'+encodeURIComponent(tab.id),'Metadados · '+tab.id),{class:'primary'}));
    root.append(body);
  }
  function renderOutline(root,tab,model){const parsed=new DOMParser().parseFromString(DOMPurify.sanitize(md.render(model.text)),'text/html'),headings=[...parsed.querySelectorAll('h1,h2,h3,h4,h5,h6')],body=node('div',{class:'outline'});body.append(node('h2',{text:'Índice · '+tab.id}));if(!headings.length)body.append(node('p',{class:'subtle',text:'Esta versão não possui títulos Markdown. Nenhum título foi inferido automaticamente.'}));
    headings.forEach((h,i)=>{const b=button(h.textContent,()=>{let targetGroup=groups.findIndex(g=>g.tabs.some(t=>t.key===g.active&&t.type==='text'&&t.id===tab.id&&t.lang===tab.lang&&t.project===tab.project));if(targetGroup<0){if(groups.length===1)split('right');targetGroup=groups.findIndex(g=>g.tabs.some(t=>t.key===tab.key))===0?1:0;}open('text',tab.id,tab.lang,targetGroup,{project:tab.project});setTimeout(()=>{views.get(groups[targetGroup]?.active)?.querySelectorAll('.article h1,.article h2,.article h3,.article h4,.article h5,.article h6')[i]?.scrollIntoView({block:'start'});},100);});b.style.paddingLeft=(8+(Number(h.tagName[1])-1)*13)+'px';body.append(b);});root.append(body);
  }
  async function editorFor(tab){
    const model=models.get([tab.project||'acervo',tab.id,tab.lang].join('|'));
    let draftQuery='';
    if(model?.text!==undefined&&model.text!==model.original&&!tab.project){
      try{const data=await json('api/editorial/editions/'+encodeURIComponent(tab.id+':'+tab.lang));
        if(data.content!==model.original){tell('A edição do acervo mudou. Baixe seu rascunho e compare com o texto atual antes de substituir.');return;}
        const token=crypto.randomUUID();sessionStorage.setItem('workspaceDraft:v1:'+token,JSON.stringify({document_id:tab.id,language:tab.lang,content:model.text,baseline_sha256:data.edition.sha256}));draftQuery='?rascunho='+token;log('Rascunho encaminhado à prévia editorial: '+tab.id+' · '+tab.lang);
      }catch(e){tell('Não foi possível encaminhar o rascunho: '+e.message+'. Baixe uma cópia.');return;}
    }else if(tab.project&&model?.text!==undefined&&model.text!==model.original)tell('Baixe ou copie este rascunho para o editor privado. A transferência de rascunhos de projeto será integrada na próxima etapa.');
    if(tab.project){const params=new URLSearchParams({bancada:'1',projeto:tab.project,idioma:tab.lang});open('tool',null,null,activeGroup,{project:tab.project,label:'Edição privada · '+tab.id,route:'#/doc/'+encodeURIComponent(tab.id)+'?'+params,reader:true});}
    else tool('markdown/'+encodeURIComponent(tab.id+':'+tab.lang)+draftQuery,'Editar · '+tab.id);
  }
  function tool(route,label){if(!backend){tell('Esta ferramenta exige o backend local: python3 -m backend.');return;}const globalTool=/^(catalogo|colecoes|novo-documento|lote|documento\/|historico|fila)(?:[/?]|$)/.test(route),context=globalTool?'':project;const query=context?'?'+new URLSearchParams({projeto:context}):'';open('tool',null,null,activeGroup,{route:route+query,label:(globalTool?'Acervo · ':'')+label,project:context});}
  function renderTool(root,tab){
    const note=node('div',{class:'integration-note',text:tab.project?'Projeto privado · confira o destino antes de salvar.':'Acervo local · gravações exigem confirmação; sem publicação automática.'});
    const iframe=node('iframe',{class:'embedded',title:tab.label,src:tab.reader?url(tab.route):url('editorial#/'+tab.route)});
    const host=node('div',{class:'tool-host'},[iframe]);root.append(note,host);
    iframe.onload=()=>{try{const d=iframe.contentDocument;if(!d||new URL(iframe.contentWindow.location.href).pathname!==new URL(url('editorial')).pathname)return;const style=d.createElement('style');style.textContent='.editorial-header,.editorial-sidebar,body>footer,.editorial-workspace-bar{display:none!important}.editorial-shell{display:block!important}.editorial-workspace{width:100%!important;max-width:none!important;margin:0!important}#editorial-view{max-width:none!important;padding:20px!important}';d.head.append(style);if(!iframe.contentWindow.archiveWorkspacePDFLayout){const css=d.createElement('link');css.rel='stylesheet';css.href=url('assets/css/workspace-pdf-layout.css?v=workflow-6');d.head.append(css);const script=d.createElement('script');script.src=url('assets/workspace-pdf-layout.js?v=workflow-6');d.body.append(script);}}catch{};};
  }
  function sideHeading(text){return node('h2',{class:'side-heading',text});}
  function docButton(d){const b=button(title(d),()=>open('text',d.id),{class:'document-item',title:title(d)});b.append(node('small',{text:d.id+' · '+d.languages.map(l=>l.code.toUpperCase()).join(' / ')+(d.date?' · '+d.date:'')}));return b;}
  const areaLabels={search:'Busca detalhada',review:'Revisão editorial',tools:'Preparação de fontes',catalog:'Organização do acervo'};
  function openArea(area){const tab=open('area',null,null,activeGroup,{area});if(area==='search'&&sidebarQuery){tab.searchState={...(tab.searchState||{}),q:sidebarQuery,page:1};renderArea(views.get(tab.key),tab);}return tab;}
  function renderArea(root,tab){
    if(tab.area==='search'){renderSearchArea(root,tab);return;}
    root.replaceChildren();const body=node('div',{class:'task-area'});
    const descriptions={review:'Escolha a tarefa de revisão. Os formulários abrem em suas próprias abas, com prévia e histórico.',tools:'Prepare a fonte, reconheça o texto quando necessário e confira o resultado antes de incorporá-lo.',catalog:'Organize o acervo e seus contextos de pesquisa. Cada gravação mantém sua confirmação.'};
    body.append(node('p',{class:'eyebrow',text:project?'Projeto / '+selectedProject()?.title:'Acervo / ambiente de trabalho'}),node('h1',{text:areaLabels[tab.area]}),node('p',{class:'subtle',text:descriptions[tab.area]}));
    const entries={tools:[['01','Receber a fonte','Preserve o PDF original e selecione o contexto de destino.','pdf/novo'],['02','Manipular o PDF — opcional','Extraia páginas ou divida um arquivo se desejar. O OCR também pode ser executado diretamente na fonte enviada.','pdf/ferramentas'],['03','OCR direto na fonte','Abra o PDF enviado, escolha OCR e selecione as páginas. Não é necessário extrair ou dividir antes.','pdf'],['04','Incorporar e disponibilizar','Na fonte, confira a transcrição, o destino e os fac-símiles a disponibilizar.','pdf']],review:[['01','Fila de revisão','Localize pendências por prioridade e motivo.','fila'],['02','Histórico recuperável','Confira as gravações e prepare uma restauração.','historico']],catalog:[['01','Catálogo e metadados','Localize o registro que precisa de complementação.','catalogo'],['02','Coleções e subcoleções','Organize os conjuntos documentais.','colecoes'],['03','Projetos de pesquisa','Organize documentos e fontes em um contexto privado.','projetos'],['04','Novo documento','Cadastre uma fonte com prévia.','novo-documento'],['05','Importar lote','Confira documentos e metadados antes de gravar.','lote']]};
    const cards=node('div',{class:'task-cards'});
    for(const [step,label,text,route] of entries[tab.area]||[]){const card=node('section',{class:'task-card'});card.append(node('span',{class:'task-number',text:step}),node('h2',{text:label}),node('p',{text}),button('Abrir tarefa →',()=>tool(route,label),{class:'primary'}));cards.append(card);}body.append(cards);root.append(body);
  }
  function searchDocuments(filters,context=project){
    let allowed=null;
    if(filters.collection){const c=manifest.collections.find(c=>c.id===filters.collection);const sub=c?.subcollections?.find(s=>s.id===filters.subcollection);allowed=new Set(sub?.document_ids||c?.document_ids||c?.documents?.map(d=>d.id)||[]);}
    const q=normalize(filters.q||'');
    const matches=[...docs.values()].filter(d=>(!context||projects.find(p=>p.id===context)?.document_ids.includes(d.id))&&(!allowed||allowed.has(d.id))&&(!filters.language||d.languages.some(l=>l.code===filters.language))&&(!filters.kind||(d.document_type||d.type)===filters.kind)&&normalize([title(d),d.id,d.title_ru,d.title_en,d.date,d.archive].join(' ')).includes(q));
    if(filters.sort==='id')matches.sort((a,b)=>a.id.localeCompare(b.id,'pt',{numeric:true}));
    else if(filters.sort==='title')matches.sort((a,b)=>title(a).localeCompare(title(b),'pt')||a.id.localeCompare(b.id));
    return matches;
  }
  function renderSearchArea(root,tab){
    root.replaceChildren();const state=tab.searchState??={q:'',collection:'',subcollection:'',language:'',kind:'',sort:'title',page:1};
    const body=node('div',{class:'task-area search-area'}),form=node('form',{class:'search-filters'}),fields={};
    body.append(node('p',{class:'eyebrow',text:tab.project?'Projeto / '+projects.find(p=>p.id===tab.project)?.title:'Acervo / catálogo'}),node('h1',{text:'Pesquisar documentos'}),node('p',{class:'subtle',text:'Busca por título, identificador, data textual e referência. Os filtros combinam-se; esta busca não pesquisa o corpo dos textos.'}));
    const field=(key,label,options=null)=>{const input=node(options?'select':'input',options?{'aria-label':label}:{type:'search',placeholder:'Nome, título, ID ou referência…','aria-label':label});if(options)for(const [value,text] of options)input.append(node('option',{value,text}));input.value=state[key]||'';fields[key]=input;form.append(node('label',{class:'filter-'+key,text:label},[input]));return input;};
    field('q','Termos da busca');const collection=field('collection','Coleção',[['','Todas as coleções'],...manifest.collections.map(c=>[c.id,c.title_pt||c.id])]);
    const sub=field('subcollection','Subcoleção',[['','Todas as subcoleções']]);
    const updateSub=()=>{const subs=manifest.collections.find(c=>c.id===collection.value)?.subcollections||[];sub.replaceChildren(node('option',{value:'',text:'Todas as subcoleções'}));for(const s of subs)sub.append(node('option',{value:s.id,text:s.title_pt||s.id}));sub.disabled=!subs.length;};updateSub();sub.value=state.subcollection||'';collection.onchange=updateSub;
    field('language','Idioma disponível',[['','Todos os idiomas'],['pt','Português'],['ru','Russo'],['en','Inglês']]);
    const types=[...new Set([...docs.values()].map(d=>d.document_type||d.type).filter(Boolean))].sort();const typeNames={interrogation_protocol:'Protocolo de interrogatório',letter:'Carta',document:'Documento',article:'Artigo',statement:'Declaração',report:'Relatório',sentence:'Sentença'};
    field('kind','Tipo documental',[['','Todos os tipos'],...types.map(t=>[t,typeNames[t]||t.replace(/_/g,' ')])]);field('sort','Ordenação',[['title','Título'],['id','Identificador'],['editorial','Ordem do catálogo']]);
    const actions=node('div',{class:'filter-actions'}),apply=node('button',{type:'submit',class:'primary',text:'Aplicar filtros'});actions.append(apply,button('Limpar filtros',()=>{tab.searchState=null;renderSearchArea(root,tab);}));form.append(actions);
    const results=node('div',{class:'search-results'}),summary=node('p',{class:'search-summary',role:'status','aria-live':'polite'});
    function show(){const matches=searchDocuments(state,tab.project),pages=Math.max(1,Math.ceil(matches.length/25));state.page=Math.max(1,Math.min(state.page||1,pages));summary.textContent=matches.length+' documentos · página '+state.page+' de '+pages;results.replaceChildren();
      if(!matches.length)results.append(node('p',{class:'empty-results',text:'Nenhum documento corresponde aos filtros. Remova um filtro ou experimente outra grafia.'}));
      for(const d of matches.slice((state.page-1)*25,state.page*25)){const row=node('article',{class:'search-result'});row.append(button(title(d),()=>open('text',d.id,null,Math.max(0,groups.findIndex(g=>g.tabs.includes(tab)))),{class:'result-title'}),node('p',{class:'subtle',text:d.id+(d.date?' · '+d.date:'')+' · '+d.languages.map(l=>labels[l.code]||l.code).join(' / ')}),button('Abrir ao lado',()=>{const index=Math.max(0,groups.findIndex(g=>g.tabs.includes(tab)));if(groups.length===1)split('right');open('text',d.id,null,index===0?1:0);},{class:'result-side'}));results.append(row);}
      const pagination=node('div',{class:'search-pagination'}),prev=button('← Anterior',()=>{state.page--;show();summary.scrollIntoView({block:'start'});}),next=button('Próxima →',()=>{state.page++;show();summary.scrollIntoView({block:'start'});});prev.disabled=state.page<=1;next.disabled=state.page>=pages;pagination.append(prev,node('span',{text:'Página '+state.page+' / '+pages}),next);results.append(pagination);
    }
    form.onsubmit=e=>{e.preventDefault();for(const [key,input] of Object.entries(fields))state[key]=input.value;state.page=1;show();};
    body.append(form,summary,results);root.append(body);show();
  }

  function renderSidebar(){
    $('section-title').textContent={explorer:'Explorador',search:'Busca no acervo',review:'Revisão editorial',tools:'Ferramentas',catalog:'Organização'}[section];document.querySelectorAll('[data-section]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.section===section)));
    const root=$('sidebar-content');root.replaceChildren();
    if(section!=='explorer')root.append(button('Abrir '+areaLabels[section].toLowerCase()+' na área de trabalho →',()=>openArea(section),{class:'open-task-area'}));
    if(section==='explorer'){
      root.append(sideHeading(project?'Documentos do projeto':'Coleções do acervo'));const tree=node('div',{class:'tree'});
      if(project){for(const d of visibleDocs())tree.append(docButton(d));if(!visibleDocs().length)tree.append(node('p',{class:'subtle',text:'Nenhum documento vinculado a este projeto.'}));root.append(button('Gerenciar projeto…',()=>tool('projetos/'+encodeURIComponent(project),'Projeto de pesquisa'),{class:'side-action'}));}
      else for(const collection of manifest.collections){const details=node('details'),count=new Set(collection.document_ids||collection.documents?.map(d=>d.id)||[]).size;details.append(node('summary',{text:collection.title_pt+' · '+count}));const list=node('div',{class:'tree'});let expanded=false;details.ontoggle=()=>{if(details.open&&!expanded){expanded=true;const membership=collection.document_ids||collection.documents?.map(d=>d.id)||[];const grouped=new Set();for(const sub of collection.subcollections||[]){const child=node('details');child.append(node('summary',{text:sub.title_pt+' · '+sub.document_ids.length}));for(const id of sub.document_ids){grouped.add(id);const d=docs.get(id);if(d)child.append(docButton(d));}list.append(child);}for(const id of membership){const d=docs.get(id);if(d&&!grouped.has(id))list.append(docButton(d));}}};details.append(list);tree.append(details);}
      root.append(tree,sideHeading('Documento ativo'));
      for(const [type,label] of [['outline','Índice como aba'],['metadata','Ficha como aba'],['markdown','Markdown como aba']])root.append(button(label,()=>{const t=currentTab();if(t?.id)open(type,t.id,t.lang);else tell('Abra primeiro um documento.');},{class:'side-action'}));
    }else if(section==='search'){
      const input=node('input',{type:'search',placeholder:'Título, ID, data ou referência…','aria-label':'Buscar no catálogo'}),results=node('div');root.append(input,node('p',{class:'subtle',text:'Busca no manifesto por título, ID e referência. O texto completo continua disponível na busca local do site.'}),results);
      input.value=sidebarQuery;input.oninput=()=>{sidebarQuery=input.value;const q=normalize(input.value),matches=visibleDocs().filter(d=>normalize([title(d),d.id,d.title_ru,d.title_en,d.date,d.archive].join(' ')).includes(q));results.replaceChildren(node('p',{class:'subtle',text:matches.length+' resultados · exibindo até 60'}));for(const d of matches.slice(0,60))results.append(docButton(d));};input.oninput();
    }else{
      const entries={review:[['Triagem e revisão',[['Fila de revisão','fila','Prioridade e motivo das pendências'],['Histórico recuperável','historico','Revisar e recuperar gravações anteriores']]],['Texto ativo',[['Editar e salvar Markdown','@edit','Prévia e confirmação no editor existente'],['Importar tradução','@import','Documento e idioma explícitos']]]],tools:[['Fontes e preparação',[['Fontes PDF','pdf','Upload, páginas e revisão de extração'],['Manipular PDF','pdf/ferramentas','Dividir, extrair e combinar arquivos']]],['OCR e transcrição',[['Revisar páginas e OCR','pdf','Abra uma fonte para configurar OCR e revisar páginas']]]],catalog:[['Organização',[['Catálogo e metadados','catalogo','Localizar e corrigir registros'],['Coleções e subcoleções','colecoes','Organizar conjuntos e descrições'],['Projetos de pesquisa','projetos','Contextos privados de trabalho']]],['Incorporação',[['Novo documento','novo-documento','Cadastrar com prévia'],['Importar lote','lote','CSV e arquivos associados']]]]};
      if(!backend)root.append(node('p',{class:'editor-note',text:'Ferramentas editoriais disponíveis somente com o backend local.'}));
      for(const [heading,items] of entries[section]){root.append(sideHeading(heading));for(const [label,route,description] of items){const b=button(label,()=>{
        const t=currentTab();if(route==='@edit'){if(t?.id)editorFor(t);else tell('Ative uma aba de documento para editar.');return;}
        if(route==='@import'){if(!t?.id){tell('Ative uma aba de documento para importar sua tradução.');return;}if(project){tell('Para traduções privadas, use Editar e salvar no contexto do projeto.');editorFor(t);return;}tool('importar?'+new URLSearchParams({documento:t.id,idioma:t.lang}),'Importar tradução');return;}
        tool(route,label);
      },{class:'side-action'});b.append(node('small',{text:description}));root.append(b);}}
    }
    root.append(sideHeading('Sincronização'),button('Atualizar acervo e versões abertas',()=>refreshCatalogue(),{class:'side-action'}));
  }
  async function refreshCatalogue(){
    if([...models.values()].some(m=>m?.text!==undefined&&m.text!==m.original)&&!confirm('Atualizar as fontes da bancada? Os rascunhos ficam preservados na sessão; se a fonte mudou, uma cópia recuperável será oferecida.'))return;
    try{await loadCatalogue();models.clear();for(const g of groups)for(const t of g.tabs)if(t.type!=='tool'){const view=views.get(t.key);if(view)renderTab(view,t,groups.indexOf(g));}renderSidebar();renderGroups();status();log('Catálogo e fontes atualizados.');}catch(e){tell(e.message);}
  }
  function renderBottom(){const root=$('bottom-content');root.replaceChildren();document.querySelectorAll('[data-bottom]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.bottom===bottom)));
    if(bottom==='notes'){const key='notes:'+(project||'acervo'),input=node('textarea',{'aria-label':'Notas privadas da sessão'});input.value=read(key,'');input.oninput=()=>write(key,input.value);root.append(node('p',{text:'Notas do contexto atual, privadas desta sessão. Não são notas editoriais publicadas.'}),input);}
    else{if(!events.length)root.append(node('p',{text:'Nenhuma operação nesta sessão. Este painel não substitui o histórico recuperável do backend.'}));for(const entry of events)root.append(node('p',{text:entry.time+' · '+entry.text}));}
  }
  function commands(){return [['Abrir busca detalhada',()=>openArea('search')],['Abrir preparação de fontes',()=>openArea('tools')],['Alternar lateral',()=>setSidebar(!document.body.classList.contains('sidebar-hidden'))],['Dividir editor à direita',()=>split('right')],['Dividir editor abaixo',()=>split('down')],['Mover aba para outro grupo',()=>{if(groups.length===1)split();const t=currentTab();if(t)moveTab(t.key,activeGroup===0?1:0);}],['Atualizar catálogo e textos',()=>refreshCatalogue()],['Abrir fontes PDF',()=>tool('pdf','Fontes PDF')],['Abrir fila de revisão',()=>tool('fila','Fila de revisão')]];}
  function palette(){const dialog=$('commands');if(!dialog.open)dialog.showModal();$('command-search').value='';paletteResults();$('command-search').focus();}
  function paletteResults(){const root=$('command-results'),q=normalize($('command-search').value);root.replaceChildren();for(const [label,action] of commands().filter(([label])=>normalize(label).includes(q)))root.append(button('› '+label,()=>{$('commands').close();action();}));let count=0;for(const d of visibleDocs()){if(!normalize(title(d)+' '+d.id+' '+d.title_ru).includes(q))continue;if(count++>=25)break;const b=button(title(d),()=>{$('commands').close();open('text',d.id);});b.append(node('small',{text:d.id+' · abrir documento'}));root.append(b);}if(!root.childElementCount)root.append(node('p',{class:'subtle',text:'Nenhum resultado neste contexto.'}));}
  async function loadCatalogue(){manifest=await json('data/manifest.json');docs.clear();for(const d of manifest.documents||[])docs.set(d.id,d);for(const c of manifest.collections)for(const d of c.documents||[])if(!docs.has(d.id))docs.set(d.id,d);}
  async function switchProject(value){
    if(value===project)return;
    if(!confirm('Trocar o contexto de trabalho? As abas serão fechadas; formulários não confirmados podem perder alterações. Os rascunhos Markdown e notas desta bancada permanecerão privados nesta sessão.')){$('project').value=project;return;}
    project=value;for(const v of views.values())v.remove();views.clear();groups.splice(0,groups.length,{tabs:[],active:null});activeGroup=0;renderGroups();renderSidebar();renderBottom();status();$('scope-description').textContent=project?'Versões privadas do projeto. Incorporar ao acervo exige confirmação no fluxo existente.':'Versões do acervo. Rascunhos deste protótipo ficam na sessão.';log(project?'Contexto escolhido explicitamente: '+selectedProject().title:'Retorno ao acervo, sem projeto ativo.');
  }
  function resize(handle,axis,variable,min,max){let start,size;const set=value=>document.documentElement.style.setProperty(variable,Math.min(max,Math.max(min,value))+'px');handle.onpointerdown=e=>{start=axis==='x'?e.clientX:e.clientY;size=parseInt(getComputedStyle(document.documentElement).getPropertyValue(variable));handle.setPointerCapture(e.pointerId);};handle.onpointermove=e=>{if(!handle.hasPointerCapture(e.pointerId))return;const pos=axis==='x'?e.clientX:e.clientY;set(size+(axis==='x'?pos-start:start-pos));};handle.onkeydown=e=>{const plus=axis==='x'?'ArrowRight':'ArrowUp',minus=axis==='x'?'ArrowLeft':'ArrowDown';if(e.key!==plus&&e.key!==minus)return;e.preventDefault();set(parseInt(getComputedStyle(document.documentElement).getPropertyValue(variable))+(e.key===plus?20:-20));};}
  async function init(){
    $('command-open').onclick=palette;$('command-search').oninput=paletteResults;$('commands-close').onclick=()=>$('commands').close();$('command-search').onkeydown=e=>{if(e.key==='ArrowDown'){$('command-results').querySelector('button')?.focus();e.preventDefault();}if(e.key==='Enter'){$('command-results').querySelector('button')?.click();e.preventDefault();}};
    $('toggle-sidebar').onclick=()=>setSidebar(!document.body.classList.contains('sidebar-hidden'));$('sidebar-close').onclick=()=>setSidebar(true);
    $('split-right').onclick=()=>split('right');$('split-down').onclick=()=>split('down');$('toggle-bottom').onclick=()=>setBottom(!document.body.classList.contains('bottom-hidden'));$('close-bottom').onclick=()=>setBottom(true);
    document.querySelectorAll('[data-section]').forEach(b=>b.onclick=()=>{if(section===b.dataset.section&&!document.body.classList.contains('sidebar-hidden'))setSidebar(true);else{section=b.dataset.section;setSidebar(false);renderSidebar();}});
    document.querySelectorAll('[data-bottom]').forEach(b=>b.onclick=()=>{bottom=b.dataset.bottom;renderBottom();});$('project').onchange=()=>switchProject($('project').value);
    resize($('sidebar-resizer'),'x','--sidebar-width',190,480);resize($('bottom-resizer'),'y','--bottom-height',100,400);
    window.addEventListener('keydown',e=>{if(!(e.ctrlKey||e.metaKey)||e.altKey)return;if(e.key.toLowerCase()==='k'){e.preventDefault();palette();}if(e.key.toLowerCase()==='b'){e.preventDefault();setSidebar(!document.body.classList.contains('sidebar-hidden'));}if(e.key==='\\'){e.preventDefault();split('right');}});
    window.addEventListener('resize',()=>renderGroups());
    window.addEventListener('beforeunload',e=>{if([...models.values()].some(m=>m?.text!==undefined&&m.text!==m.original)){e.preventDefault();e.returnValue='';}});
    setSidebar(read('sidebarHidden',innerWidth<640));setBottom(read('bottomHidden',true));renderGroups();renderBottom();
    try{await loadCatalogue();renderSidebar();
      const storedTabs=read('tabs',[]),cached=Array.isArray(storedTabs)?storedTabs:[];for(const t of cached.slice(0,16)){if(docs.has(t.id)&&['text','markdown','metadata','outline'].includes(t.type)&&docs.get(t.id).languages.some(l=>l.code===t.lang))open(t.type,t.id,t.lang,0);}
      if(!cached.length)log('Workspace iniciado sem projeto ativo. '+docs.size+' documentos disponíveis no acervo.');
    }catch(e){tell('Não foi possível carregar o catálogo: '+e.message);$('connection').textContent='Falha ao carregar acervo';return;}
    try{const capabilities=await json('api/editorial/capabilities');backend=capabilities.available===true||capabilities.enabled===true||Boolean(capabilities.features?.includes('markdown_edit'));
      if(backend){const data=await json('api/editorial/projects');projects=data.items||[];for(const p of projects.filter(p=>!p.archived))$('project').append(node('option',{value:p.id,text:p.title}));}
    }catch{backend=false;}
    $('connection').textContent=backend?'● Backend local disponível':'○ Acervo estático · rascunhos na sessão';$('project').disabled=!backend;renderSidebar();renderGroups();if(backend)for(const g of groups)for(const t of g.tabs){const view=views.get(t.key);if(view&&t.type!=='tool')renderTab(view,t,groups.indexOf(g));}status();
  }
  init();
})();
