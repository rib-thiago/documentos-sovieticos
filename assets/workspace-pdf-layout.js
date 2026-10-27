/* Organização compartilhada das ferramentas PDF e da área editorial. Não move nem recria formulários. */
window.archiveWorkspacePDFLayout=(()=>{
  const phases=[['review','Revisar página'],['ocr','OCR'],['metadata','Cadastro da fonte'],['links','Vínculos'],['incorporation','Incorporar'],['publication','Disponibilizar']];
  const reviews=[['text','Texto'],['candidates','Candidatos OCR'],['alignment','Alinhamento'],['references','Referências'],['history','Histórico']];
  const state=new WeakMap(),resizers=new Set();
  function button(label,run){const b=document.createElement('button');b.type='button';b.textContent=label;b.onclick=run;return b;}
  function switchPane(root,attribute,value){for(const pane of root.querySelectorAll('['+attribute+']')){const selected=pane.getAttribute(attribute)===value;pane.classList.toggle('workspace-pane-inactive',!selected);if(selected&&pane.tagName==='DETAILS'&&!pane.open)pane.open=true;}}
  function navigation(root,attribute,choices,selected,onChange,className){
    const nav=document.createElement('div');nav.className=className;nav.setAttribute('role','group');nav.setAttribute('aria-label',attribute==='data-workspace-zone'?'Etapas de trabalho da fonte':'Seções da tarefa');
    const update=value=>{for(const b of nav.querySelectorAll('button'))b.setAttribute('aria-pressed',String(b.dataset.value===value));switchPane(root,attribute,value);};
    for(const [key,label] of choices){const b=button(label,()=>{onChange(key);update(key);});b.dataset.value=key;nav.append(b);}
    if(className==='workspace-review-sections'&&attribute==='data-workspace-review-pane'){
      const extra=document.createElement('details');extra.className='workspace-review-more';const summary=document.createElement('summary');summary.textContent='Mais ferramentas';extra.append(summary);for(const b of [...nav.children])if(!['text','candidates'].includes(b.dataset.value)){const run=b.onclick;b.onclick=()=>{run();extra.open=false;};extra.append(b);}const items=document.createElement('div');items.className='workspace-menu-items';for(const b of [...extra.querySelectorAll(':scope>button')])items.append(b);extra.append(items);nav.append(extra);
    }
    root.prepend(nav);update(selected);return{nav,update};
  }
  function sourceNavigation(root,info){
    const nav=document.createElement('div');nav.className='workspace-source-steps';nav.setAttribute('aria-label','Trabalho com a fonte');
    const page=button('Página e transcrição',()=>{info.phase='review';info.ocrOpen=false;update('review');decorate(root);});page.dataset.value='review';
    const ocr=button('Gerar OCR',()=>{info.phase='review';info.ocrOpen=!info.ocrOpen;update('review');decorate(root);});ocr.className='workspace-ocr-toggle';ocr.setAttribute('aria-expanded','false');
    const more=document.createElement('details');more.className='workspace-source-more';const summary=document.createElement('summary');summary.textContent='Dados e publicação';more.append(summary);
    for(const[key,label]of phases.filter(([key])=>!['review','ocr'].includes(key))){const b=button(label,()=>{info.phase=key;info.ocrOpen=false;more.open=false;update(key);decorate(root);});b.dataset.value=key;more.append(b);}
    const items=document.createElement('div');items.className='workspace-menu-items';for(const b of [...more.querySelectorAll(':scope>button')])items.append(b);more.append(items);nav.append(page,ocr,more);root.prepend(nav);
    const update=value=>{for(const b of nav.querySelectorAll('button[data-value]'))b.setAttribute('aria-pressed',String(b.dataset.value===value));switchPane(root,'data-workspace-zone',value);};update(info.phase);return{nav,update};
  }
  function integrateOCR(root,grid,info){
    const controls=root.querySelector('.pdf-ocr-controls');if(!controls)return;
    const transcript=grid.querySelector(':scope>.workspace-page-transcript');if(!transcript)return;
    if(!info.drawer?.isConnected){
      const original=controls.closest('[data-workspace-zone=ocr]');if(!original)return;
      const drawer=document.createElement('section');drawer.className='workspace-ocr-drawer';drawer.setAttribute('aria-label','OCR da fonte');drawer.hidden=true;
      const heading=document.createElement('header'),title=document.createElement('strong');title.textContent='Gerar e acompanhar OCR';const close=button('Voltar à transcrição',()=>{info.ocrOpen=false;decorate(root);info.main.nav.querySelector('.workspace-ocr-toggle')?.focus();});heading.append(title,close);
      original.removeAttribute('data-workspace-zone');original.classList.remove('workspace-pane-inactive');original.classList.add('workspace-ocr-drawer-body');drawer.append(heading,original);grid.append(drawer);info.drawer=drawer;
    }
    if(info.ocrOpen&&(info.mode==='source'||root.clientWidth<650&&info.mode!=='text')){info.mode=root.clientWidth<650?'text':'compare';layoutPage(grid,info);}
    if(info.drawer.hidden!==!info.ocrOpen)info.drawer.hidden=!info.ocrOpen;info.main.nav.querySelector('.workspace-ocr-toggle')?.setAttribute('aria-expanded',String(!!info.ocrOpen));
  }
  function decorate(root){
    const grid=root.querySelector('[data-workspace-source]');if(!grid||grid.closest('[data-workspace-source-root]')!==root)return;
    const source=grid.getAttribute('data-workspace-source');let info=state.get(root);
    if(!info||info.source!==source||!info.main.nav.isConnected){
      if(info?.resizer){info.resizer.disconnect();resizers.delete(info.resizer);}info?.main.nav.remove();info={source,phase:'review',review:'text',ocr:'configuration',mode:root.clientWidth<850?'source':'compare',height:readHeight()};
      const main=sourceNavigation(root,info);info.main=main;state.set(root,info);root.classList.add('workspace-pdf-task');const container=root.closest('.native-tool-main');if(container&&typeof ResizeObserver!=='undefined'){const resizer=new ResizeObserver(()=>{if(!grid.isConnected||root.getAttribute('data-workspace-source-root')!==info.source){resizer.disconnect();resizers.delete(resizer);}else applyHeight(grid,info);});info.resizer=resizer;resizers.add(resizer);resizer.observe(container);}
    }
    root.dataset.workspacePhase=info.phase;compactSourceHeader(root);
    switchPane(root,'data-workspace-zone',info.phase);
    layoutPage(grid,info);
    integrateOCR(root,grid,info);
    const zones=[...root.querySelectorAll('[data-workspace-zone]')].map(n=>n.getAttribute('data-workspace-zone'));
    for(const b of info.main.nav.querySelectorAll('button[data-value]')){b.disabled=!zones.includes(b.dataset.value);b.title=b.disabled?'Esta seção ainda não está disponível neste contexto.':'';}
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
    if(ocr){if(info.ocrOpen)ocr.open=true;if(!info.ocrNav?.nav.isConnected)info.ocrNav=navigation(ocr,'data-workspace-ocr-pane',[['configuration','Configurar lote'],['progress','Andamento dos lotes']],info.ocr,value=>{info.ocr=value;},'workspace-review-sections');switchPane(ocr,'data-workspace-ocr-pane',info.ocr);}
  }
  function compactSourceHeader(root){
    const actions=root.querySelector('[data-workspace-source-actions]');if(!actions)return;
    const title=root.querySelector('[data-workspace-source-title]'),back=root.querySelector('[data-workspace-source-back]');
    if(title&&title.parentElement!==actions){title.title=title.textContent;actions.prepend(title);}
    let menu=actions.querySelector('.workspace-source-actions-menu');if(!menu){menu=document.createElement('details');menu.className='workspace-source-actions-menu';const summary=document.createElement('summary');summary.textContent='Ações da fonte';const items=document.createElement('div');items.className='workspace-menu-items';menu.append(summary,items);actions.append(menu);}
    for(const item of [...actions.children])if(item!==menu&&item!==title)menu.querySelector('.workspace-menu-items').append(item);
    if(back){const items=menu.querySelector('.workspace-menu-items');if(back.parentElement!==items)items.append(back);back.title='Voltar à lista de fontes PDF';back.setAttribute('aria-label','Voltar à lista de fontes PDF');if(back.textContent!=='← Fontes')back.textContent='← Fontes';}
  }
  function layoutPage(grid,info){
    const facsimile=grid.querySelector('.pdf-facsimile');if(!facsimile)return;
    let left=facsimile.parentElement===grid?facsimile:facsimile.closest('section');
    if(left)left.classList.add('workspace-page-image');
    for(const item of grid.children)if(item!==left&&!item.classList.contains('workspace-page-divider')&&!item.classList.contains('workspace-ocr-drawer'))item.classList.add('workspace-page-transcript');
    if(!info.viewNav?.isConnected){
      const nav=document.createElement('div');nav.className='workspace-page-views';nav.setAttribute('data-workspace-zone','review');nav.setAttribute('role','group');nav.setAttribute('aria-label','Disposição da revisão');
      for(const [key,label]of [['source','Fac-símile'],['compare','Comparar'],['text','Transcrição']]){const control=button(label,()=>{info.mode=key;layoutPage(grid,info);});control.dataset.value=key;nav.append(control);}
      const settings=document.createElement('details');settings.className='workspace-view-settings';const summary=document.createElement('summary');summary.textContent='Ajustar espaço';const settingsBody=document.createElement('div');settingsBody.className='workspace-view-settings-body';settings.append(summary,settingsBody);nav.append(settings);
      const ratio=document.createElement('input');ratio.type='range';ratio.min='35';ratio.max='75';ratio.value='58';ratio.setAttribute('aria-label','Espaço do fac-símile na comparação');ratio.title='Ajustar proporção do fac-símile';ratio.oninput=()=>{info.ratio=Number(ratio.value);grid.style.setProperty('--workspace-image-ratio',info.ratio+'%');};settingsBody.append(ratio);
      const heightLabel=document.createElement('label');heightLabel.className='workspace-page-height-label';heightLabel.textContent='Altura';
      const height=document.createElement('input');height.type='number';height.min='240';height.max='1400';height.step='20';height.setAttribute('aria-label','Altura da área de revisão em pixels');height.onchange=()=>{if(height.value.trim())setHeight(grid,info,Number(height.value));};heightLabel.append(height);settingsBody.append(heightLabel);info.heightControl=height;
      const auto=button('Automática',()=>{info.height=null;saveHeight(null);applyHeight(grid,info);});auto.title='Ajustar à altura disponível da janela';settingsBody.append(auto);info.autoHeight=auto;
      const paging=grid.parentElement.querySelector('.pdf-source-toolbar[data-workspace-zone=review]');if(paging)nav.prepend(paging);info.viewNav=nav;grid.parentElement.insertBefore(nav,grid);
      const handle=document.createElement('div');handle.className='workspace-page-height-handle';handle.setAttribute('data-workspace-zone','review');handle.setAttribute('role','separator');handle.setAttribute('aria-orientation','horizontal');handle.setAttribute('aria-label','Arraste para ajustar a altura da revisão; use as setas para ajustar pelo teclado');handle.setAttribute('tabindex','0');handle.setAttribute('aria-valuemin','240');handle.setAttribute('aria-valuemax','1400');
      let start=0,base=0;handle.onpointerdown=e=>{e.preventDefault();start=e.clientY;base=grid.getBoundingClientRect().height;handle.setPointerCapture(e.pointerId);};handle.onpointermove=e=>{if(handle.hasPointerCapture(e.pointerId))setHeight(grid,info,base+e.clientY-start);};
      handle.onkeydown=e=>{if(!['ArrowUp','ArrowDown','Home','End'].includes(e.key))return;e.preventDefault();setHeight(grid,info,e.key==='Home'?240:e.key==='End'?1400:(info.height||grid.getBoundingClientRect().height)+(e.key==='ArrowDown'?20:-20));};
      grid.parentElement.insertBefore(handle,grid.nextSibling);info.heightHandle=handle;
    }
    for(const b of info.viewNav.querySelectorAll('button[data-value]'))b.setAttribute('aria-pressed',String(b.dataset.value===info.mode));
    grid.setAttribute('data-workspace-page-mode',info.mode);grid.style.setProperty('--workspace-image-ratio',(info.ratio||58)+'%');
    applyHeight(grid,info);
  }
  function readHeight(){try{const value=JSON.parse(sessionStorage.getItem('workspacePDFHeight:v1'));return Number.isFinite(value)&&value>=240&&value<=1400?value:null;}catch{return null;}}
  function saveHeight(value){try{sessionStorage.setItem('workspacePDFHeight:v1',JSON.stringify(value));}catch{}}
  function setHeight(grid,info,value){if(!Number.isFinite(value))return;info.height=Math.round(Math.min(1400,Math.max(240,value)));saveHeight(info.height);applyHeight(grid,info);}
  function applyHeight(grid,info){const container=grid.closest('.native-tool-main,.pane-body')||document.documentElement,bottom=Math.min(window.innerHeight,container.getBoundingClientRect().bottom),top=grid.getBoundingClientRect().top,available=Math.max(240,bottom-Math.max(0,top)-18);const height=Math.min(info.height??available,available);grid.style.setProperty('--workspace-page-height',Math.round(height)+'px');if(info.heightControl)info.heightControl.value=String(Math.round(height));if(info.autoHeight)info.autoHeight.disabled=info.height===null;if(info.heightHandle)info.heightHandle.setAttribute('aria-valuenow',String(Math.round(height)));}

  function start(){
    if(document.documentElement.dataset.workspacePdfLayout)return;document.documentElement.dataset.workspacePdfLayout='true';
    let scheduled=null;
    const observation={childList:true,subtree:true};
    const apply=()=>{
      if(scheduled!==null){cancelAnimationFrame(scheduled);scheduled=null;}
      // Layout changes must not enqueue another layout pass of their own.
      observer.disconnect();
      try{for(const root of document.querySelectorAll('[data-workspace-source-root]'))decorate(root);}
      finally{observer.observe(document.body,observation);}
    };
    const observer=new MutationObserver(()=>{if(scheduled===null)scheduled=requestAnimationFrame(apply);});observer.observe(document.body,observation);
    const activity=event=>{const root=event.target.closest('[data-workspace-source-root]'),info=root&&state.get(root);if(!info)return;if(event.type==='archive:pdf-ocr-started'){info.phase='review';info.ocrOpen=true;info.ocr='progress';info.ocrNav?.update('progress');}else{info.phase='review';info.ocrOpen=false;info.review=event.type==='archive:pdf-candidate-loaded'?'text':'candidates';info.reviewNav?.update(info.review);}info.main.update(info.phase);decorate(root);};
    document.addEventListener('archive:pdf-ocr-started',activity);document.addEventListener('archive:pdf-review-opened',activity);document.addEventListener('archive:pdf-candidate-loaded',activity);
    document.addEventListener('archive:workspace-space-changed',apply);window.addEventListener('resize',apply);window.addEventListener('pagehide',()=>{if(scheduled!==null)cancelAnimationFrame(scheduled);observer.disconnect();for(const resizer of resizers)resizer.disconnect();resizers.clear();document.removeEventListener('archive:workspace-space-changed',apply);window.removeEventListener('resize',apply);document.removeEventListener('archive:pdf-ocr-started',activity);document.removeEventListener('archive:pdf-review-opened',activity);document.removeEventListener('archive:pdf-candidate-loaded',activity);},{once:true});apply();
  }
  return{start,switchPane};
})();
window.archiveWorkspacePDFLayout.start();
