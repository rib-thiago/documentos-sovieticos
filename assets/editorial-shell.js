/* Mesmo vocabulário visual da bancada, sem substituir seus documentos e painéis.
   Navegação editorial usa o roteador existente, inclusive a proteção de edições. */
window.archiveEditorialShell=(()=>{
  if(window.parent!==window)return null;
  const shell=document.querySelector('.editorial-shell');
  if(!shell)return null;
  document.body.classList.add('editorial-desktop');
  const node=(tag,props={})=>Object.assign(document.createElement(tag),props);
  const rail=node('nav',{className:'editorial-activity'});
  rail.setAttribute('aria-label','Atividades editoriais');
  for(const [href,label,icon] of [
    ['#/projetos','Projetos','catalog'],['#/fila','Revisão','compass'],
    ['#/catalogo','Acervo','search'],['#/markdown','Textos e traduções','edit'],
    ['#/pdf','PDF e OCR','read']
  ]){
    const link=node('a',{href,title:label});link.setAttribute('aria-label',label);
    link.append(archiveIcon(icon));rail.append(link);
  }
  shell.prepend(rail);
  const resize=node('div',{className:'editorial-sidebar-resizer',tabIndex:0});
  resize.setAttribute('role','separator');resize.setAttribute('aria-orientation','vertical');
  resize.setAttribute('aria-label','Largura da navegação editorial');
  resize.setAttribute('aria-valuemin','190');resize.setAttribute('aria-valuemax','420');
  const setWidth=value=>{
    const width=Math.max(190,Math.min(420,value));shell.style.setProperty('--editorial-sidebar-width',width+'px');
    resize.setAttribute('aria-valuenow',String(width));
    try{sessionStorage.setItem('editorialSidebarWidth',String(width));}catch{}
  };
  let width=248;try{width=Number(sessionStorage.getItem('editorialSidebarWidth'))||248;}catch{}
  setWidth(width);
  document.querySelector('.editorial-sidebar').after(resize);
  resize.addEventListener('pointerdown',event=>{if(event.button!==0)return;event.preventDefault();resize.setPointerCapture(event.pointerId);});
  resize.addEventListener('pointermove',event=>{if(resize.hasPointerCapture(event.pointerId))setWidth(Math.round(event.clientX-rail.getBoundingClientRect().right));});
  resize.addEventListener('pointerup',event=>{if(resize.hasPointerCapture(event.pointerId))resize.releasePointerCapture(event.pointerId);});
  resize.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight'].includes(event.key))return;event.preventDefault();setWidth(Number(resize.getAttribute('aria-valuenow'))+(event.key==='ArrowLeft'?-16:16));});
  const tabs=node('nav',{className:'editorial-task-tabs'});tabs.setAttribute('aria-label','Tarefas editoriais abertas');
  document.querySelector('.editorial-workspace').prepend(tabs);
  // Somente atalhos visitados; os formulários continuam com prévia e confirmação.
  // Não armazenar conteúdo, tokens de retorno ou rascunhos nestes atalhos.
  const tasks=[];
  let activePath='',closeGuard=()=>true;
  function renderTabs(){
    tabs.replaceChildren();
    for(const task of tasks){
      const holder=node('div',{className:'editorial-task-tab'});
      const link=node('a',{href:task.hash,textContent:task.label,title:task.path});
      if(task.path===activePath)link.setAttribute('aria-current','page');
      const close=node('button',{type:'button',textContent:'×',title:'Fechar '+task.label});
      close.setAttribute('aria-label','Fechar '+task.label);
      close.addEventListener('click',()=>{
        const active=task.path===activePath;
        if(active&&!closeGuard())return;
        const index=tasks.indexOf(task);tasks.splice(index,1);renderTabs();
        if(active)location.hash=tasks[Math.min(index,tasks.length-1)]?.hash||'#/inicio';
      });
      holder.append(link,close);tabs.append(holder);
    }
    if(tasks.length){
      const closeAll=node('button',{type:'button',className:'editorial-close-all',textContent:'Fechar todas',title:'Fechar todas as tarefas'});
      closeAll.onclick=()=>{if(!closeGuard())return;tasks.length=0;renderTabs();location.hash='#/inicio';};tabs.append(closeAll);
    }
  }
  function activate(hash,label){
    const path=hash.split('?')[0],existing=tasks.find(task=>task.path===path);
    activePath=path;
    if(existing){existing.hash=hash;existing.label=label;}
    else if(path!=='#/inicio')tasks.push({path,hash,label});
    renderTabs();
    for(const link of rail.querySelectorAll('a')){
      const section=path.split('/')[1];
      const current=link.hash===path||
        (link.hash==='#/catalogo'&&['documento','colecoes','colecao','nova-colecao','novo-documento','lote'].includes(section))||
        (link.hash==='#/markdown'&&['markdown','importar'].includes(section))||
        (link.hash==='#/fila'&&section==='historico')||
        (link.hash==='#/pdf'&&section==='pdf')||
        (link.hash==='#/projetos'&&section==='projetos');
      if(current)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');
    }
    tabs.querySelector('[aria-current]')?.scrollIntoView({block:'nearest',inline:'nearest'});
    document.querySelector('.editorial-workspace').scrollTo({top:0});
  }
  document.addEventListener('keydown',event=>{
    if((event.ctrlKey||event.metaKey)&&!event.shiftKey&&event.key.toLowerCase()==='b'&&
       !event.target.closest('input,textarea,select,[contenteditable=true]')){
      event.preventDefault();document.querySelector('.sidebar-toggle')?.click();
    }
  });
  return{activate,setCloseGuard:guard=>{closeGuard=guard;}};
})();
