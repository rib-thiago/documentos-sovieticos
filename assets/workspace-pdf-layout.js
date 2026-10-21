/* Organização compartilhada das ferramentas PDF e da área editorial. Não move nem recria formulários. */
window.archiveWorkspacePDFLayout=(()=>{
  const phases=[['review','Revisar página'],['ocr','OCR'],['metadata','Cadastro da fonte'],['links','Vínculos'],['incorporation','Incorporar'],['publication','Disponibilizar']];
  const reviews=[['text','Texto'],['candidates','Candidatos OCR'],['alignment','Alinhamento'],['references','Referências'],['history','Histórico']];
  const state=new WeakMap();
  function button(label,run){const b=document.createElement('button');b.type='button';b.textContent=label;b.onclick=run;return b;}
  function switchPane(root,attribute,value){for(const pane of root.querySelectorAll('['+attribute+']')){const selected=pane.getAttribute(attribute)===value;pane.classList.toggle('workspace-pane-inactive',!selected);if(selected&&pane.tagName==='DETAILS'&&!pane.open)pane.open=true;}}
  function navigation(root,attribute,choices,selected,onChange,className){
    const nav=document.createElement('div');nav.className=className;nav.setAttribute('role','group');nav.setAttribute('aria-label',attribute==='data-workspace-zone'?'Etapas de trabalho da fonte':'Seções da tarefa');
    const update=value=>{for(const b of nav.querySelectorAll('button'))b.setAttribute('aria-pressed',String(b.dataset.value===value));switchPane(root,attribute,value);};
    for(const [key,label] of choices){const b=button(label,()=>{onChange(key);update(key);});b.dataset.value=key;nav.append(b);}
    root.prepend(nav);update(selected);return{nav,update};
  }
  function decorate(root){
    const grid=root.querySelector('[data-workspace-source]');if(!grid||grid.closest('[data-workspace-source-root]')!==root)return;
    const source=grid.getAttribute('data-workspace-source');let info=state.get(root);
    if(!info||info.source!==source||!info.main.nav.isConnected){
      info?.main.nav.remove();info={source,phase:'review',review:'text',ocr:'configuration',mode:window.innerWidth<850?'source':'compare',height:readHeight()};
      const main=navigation(root,'data-workspace-zone',phases,info.phase,value=>{info.phase=value;decorate(root);},'workspace-source-steps');info.main=main;state.set(root,info);root.classList.add('workspace-pdf-task');
    }
    compactSourceHeader(root);
    switchPane(root,'data-workspace-zone',info.phase);
    layoutPage(grid,info);
    const zones=[...root.querySelectorAll('[data-workspace-zone]')].map(n=>n.getAttribute('data-workspace-zone'));
    for(const b of info.main.nav.querySelectorAll('button')){b.disabled=!zones.includes(b.dataset.value);b.title=b.disabled?'Esta seção ainda não está disponível neste contexto.':'';}
    switchPane(root,'data-workspace-zone',info.phase);
    const form=root.querySelector('.pdf-review-form');
    if(form){const reviewRoot=form.parentElement;
      reviewRoot.classList.add('workspace-page-editor');
      if(!info.reviewNav?.nav.isConnected){
        info.reviewNav=navigation(reviewRoot,'data-workspace-review-pane',reviews,info.review,value=>{info.review=value;switchPane(root,'data-workspace-review-pane',value);},'workspace-review-sections');
        const detail=button('Notas',()=>{const expanded=reviewRoot.classList.toggle('workspace-review-details');detail.setAttribute('aria-expanded',String(expanded));});detail.setAttribute('aria-expanded',String(reviewRoot.classList.contains('workspace-review-details')));detail.className='workspace-review-notes-toggle';info.reviewNav.nav.append(detail);
      }
      switchPane(root,'data-workspace-review-pane',info.review);
    }
    const ocr=root.querySelector('.pdf-ocr-controls');
    if(ocr){if(info.phase==='ocr')ocr.open=true;if(!info.ocrNav?.nav.isConnected)info.ocrNav=navigation(ocr,'data-workspace-ocr-pane',[['configuration','Configurar lote'],['progress','Andamento dos lotes']],info.ocr,value=>{info.ocr=value;},'workspace-review-sections');switchPane(ocr,'data-workspace-ocr-pane',info.ocr);}
  }
  function compactSourceHeader(root){
    const actions=root.querySelector('[data-workspace-source-actions]');if(!actions)return;
    const title=root.querySelector('[data-workspace-source-title]'),back=root.querySelector('[data-workspace-source-back]');
    if(title&&title.parentElement!==actions){title.title=title.textContent;actions.prepend(title);}
    if(back&&back.parentElement!==actions){back.title='Voltar à lista de fontes PDF';back.setAttribute('aria-label','Voltar à lista de fontes PDF');back.textContent='← Fontes';actions.prepend(back);}
  }
  function layoutPage(grid,info){
    const facsimile=grid.querySelector('.pdf-facsimile');if(!facsimile)return;
    let left=facsimile.parentElement===grid?facsimile:facsimile.closest('section');
    if(left)left.classList.add('workspace-page-image');
    for(const item of grid.children)if(item!==left&&!item.classList.contains('workspace-page-divider'))item.classList.add('workspace-page-transcript');
    if(!info.viewNav?.isConnected){
      const nav=document.createElement('div');nav.className='workspace-page-views';nav.setAttribute('data-workspace-zone','review');nav.setAttribute('role','group');nav.setAttribute('aria-label','Disposição da revisão');
      for(const [key,label]of [['source','Fac-símile'],['compare','Comparar'],['text','Transcrição']]){const control=button(label,()=>{info.mode=key;layoutPage(grid,info);});control.dataset.value=key;nav.append(control);}
      const ratio=document.createElement('input');ratio.type='range';ratio.min='35';ratio.max='75';ratio.value='58';ratio.setAttribute('aria-label','Espaço do fac-símile na comparação');ratio.title='Ajustar proporção do fac-símile';ratio.oninput=()=>{info.ratio=Number(ratio.value);grid.style.setProperty('--workspace-image-ratio',info.ratio+'%');};nav.append(ratio);
      const heightLabel=document.createElement('label');heightLabel.className='workspace-page-height-label';heightLabel.textContent='Altura';
      const height=document.createElement('input');height.type='number';height.min='320';height.max='1400';height.step='20';height.setAttribute('aria-label','Altura da área de revisão em pixels');height.onchange=()=>{if(height.value.trim())setHeight(grid,info,Number(height.value));};heightLabel.append(height);nav.append(heightLabel);info.heightControl=height;
      const auto=button('Automática',()=>{info.height=null;saveHeight(null);applyHeight(grid,info);});auto.title='Ajustar à altura disponível da janela';nav.append(auto);info.autoHeight=auto;
      info.viewNav=nav;grid.parentElement.insertBefore(nav,grid);
      const handle=document.createElement('div');handle.className='workspace-page-height-handle';handle.setAttribute('data-workspace-zone','review');handle.setAttribute('role','separator');handle.setAttribute('aria-orientation','horizontal');handle.setAttribute('aria-label','Arraste para ajustar a altura da revisão; use as setas para ajustar pelo teclado');handle.setAttribute('tabindex','0');handle.setAttribute('aria-valuemin','320');handle.setAttribute('aria-valuemax','1400');
      let start=0,base=0;handle.onpointerdown=e=>{e.preventDefault();start=e.clientY;base=grid.getBoundingClientRect().height;handle.setPointerCapture(e.pointerId);};handle.onpointermove=e=>{if(handle.hasPointerCapture(e.pointerId))setHeight(grid,info,base+e.clientY-start);};
      handle.onkeydown=e=>{if(!['ArrowUp','ArrowDown','Home','End'].includes(e.key))return;e.preventDefault();setHeight(grid,info,e.key==='Home'?320:e.key==='End'?1400:(info.height||grid.getBoundingClientRect().height)+(e.key==='ArrowDown'?20:-20));};
      grid.parentElement.insertBefore(handle,grid.nextSibling);info.heightHandle=handle;
    }
    for(const b of info.viewNav.querySelectorAll('button'))b.setAttribute('aria-pressed',String(b.dataset.value===info.mode));
    grid.setAttribute('data-workspace-page-mode',info.mode);grid.style.setProperty('--workspace-image-ratio',(info.ratio||58)+'%');
    applyHeight(grid,info);
  }
  function readHeight(){try{const value=JSON.parse(sessionStorage.getItem('workspacePDFHeight:v1'));return Number.isFinite(value)&&value>=320&&value<=1400?value:null;}catch{return null;}}
  function saveHeight(value){try{sessionStorage.setItem('workspacePDFHeight:v1',JSON.stringify(value));}catch{}}
  function setHeight(grid,info,value){if(!Number.isFinite(value))return;info.height=Math.round(Math.min(1400,Math.max(320,value)));saveHeight(info.height);applyHeight(grid,info);}
  function applyHeight(grid,info){const top=grid.getBoundingClientRect().top;const height=info.height??Math.min(1400,Math.max(340,window.innerHeight-Math.max(0,top)-30));grid.style.setProperty('--workspace-page-height',height+'px');if(info.heightControl)info.heightControl.value=String(Math.round(height));if(info.autoHeight)info.autoHeight.disabled=info.height===null;if(info.heightHandle)info.heightHandle.setAttribute('aria-valuenow',String(Math.round(height)));}
  function start(){
    if(document.documentElement.dataset.workspacePdfLayout)return;document.documentElement.dataset.workspacePdfLayout='true';
    let scheduled=false;
    const apply=()=>{scheduled=false;for(const root of document.querySelectorAll('[data-workspace-source-root]'))decorate(root);};
    const observer=new MutationObserver(()=>{if(scheduled)return;scheduled=true;queueMicrotask(apply);});observer.observe(document.body,{childList:true,subtree:true});
    const activity=event=>{const root=event.target.closest('[data-workspace-source-root]'),info=root&&state.get(root);if(!info)return;if(event.type==='archive:pdf-ocr-started'){info.phase='ocr';info.ocr='progress';info.ocrNav?.update('progress');}else{info.phase='review';info.review='candidates';info.reviewNav?.update('candidates');}info.main.update(info.phase);decorate(root);};
    document.addEventListener('archive:pdf-ocr-started',activity);document.addEventListener('archive:pdf-review-opened',activity);
    window.addEventListener('resize',apply);window.addEventListener('pagehide',()=>{observer.disconnect();window.removeEventListener('resize',apply);document.removeEventListener('archive:pdf-ocr-started',activity);document.removeEventListener('archive:pdf-review-opened',activity);},{once:true});apply();
  }
  return{start,switchPane};
})();
window.archiveWorkspacePDFLayout.start();
