/* Fac-símiles locais no estudo; associações manuais, com texto e revisão verificáveis. */
window.archiveFacsimiles=(()=>{
  const selections=new Map();let sequence=0;
  const node=(tag,attrs={},children=[])=>{const e=document.createElement(tag);for(const[k,v]of Object.entries(attrs))if(k==='text')e.textContent=v;else if(v!=null)e.setAttribute(k,v);for(const c of children)e.append(c);return e;};
  const button=(text,fn)=>{const e=node('button',{type:'button',class:'panel-button',text});e.onclick=fn;return e;};
  const key=()=> (state.workspaceProject?.id||'acervo')+':'+state.activeDocument?.meta.id;
  const api=(...args)=>archiveProjectEditor.api(...args);
  const hash=async value=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value)))).map(n=>n.toString(16).padStart(2,'0')).join('');
  function scope(){return state.workspaceProject?.id||'';}
  function show(link,page,anchor=null){selections.set(key(),{id:link.id,page,anchor});closeDocumentPanel();if(state.viewMode!=='study')setViewMode('study');else update();}
  function modal(title){
    const dialog=node('dialog',{class:'study-passage-dialog pdf-link-dialog','aria-label':title}),body=node('div',{class:'passage-content'}),close=button('Fechar',()=>dialog.close());
    dialog.append(node('div',{class:'passage-heading'},[node('h2',{text:title}),close]),body);document.body.append(dialog);dialog.addEventListener('close',()=>dialog.remove(),{once:true});dialog.showModal();return{dialog,body};
  }
  async function manager(){const doc=state.activeDocument;if(!doc)return;const {dialog,body}=modal('Fontes e fac-símiles · '+documentTitle(doc.meta));const controller=new AbortController();dialog.addEventListener('close',()=>controller.abort(),{once:true});try{await archivePDFLinks.renderManager(body,{api,documentId:doc.meta.id,projectId:scope(),signal:controller.signal});}catch(e){body.textContent=e.message;}}
  function toolbarHost(){const host=node('div',{class:'facsimile-controls'});host.append(node('p',{class:'control-help',text:'Conectando às fontes locais…'}));return host;}
  async function update(){
    const own=++sequence,doc=state.activeDocument,host=document.querySelector('.doc-toolbar .facsimile-controls');if(!doc||!host)return;
    const captured=key(),projectId=scope();
    try{
      let result=state.editorialAvailable?await api('/api/editorial/pdf/links?'+archivePDFLinks.query(doc.meta.id,projectId)):{items:[]};
      if(!projectId){
        const response=await fetch(absURL('data/facsimiles.json'),{cache:'no-store'});
        if(response.ok){const index=await response.json();const existing=new Set(result.items.map(i=>i.id));const hashes=new Map();
          for(const item of index.links||[])if(item.document_id===doc.meta.id&&!existing.has(item.id)){
            for(const anchor of item.anchors){if(!hashes.has(anchor.language)){const language=doc.langs.find(l=>l.code===anchor.language);try{hashes.set(anchor.language,language?await hash(language.source):null);}catch{hashes.set(anchor.language,null);}}anchor.stale_text=hashes.get(anchor.language)!==anchor.body_sha256;anchor.stale_page=false;}
            result.items.push({...item,static:true});
          }
        }
      }
      if(own!==sequence||captured!==key()||!host.isConnected)return;
      const active=result.items.filter(i=>i.active);host.replaceChildren();
      if(state.editorialAvailable)host.append(button('Gerenciar fontes e páginas',manager));
      if(!active.length)host.append(node('p',{class:'control-help',text:state.editorialAvailable?'Nenhuma fonte vinculada a este documento neste contexto.':'Nenhum fac-símile publicado para este documento.'}));
      for(const item of active)host.append(button((item.source_title||'Consultar PDF')+' · páginas '+item.pages.join(', '),()=>show(item,item.pages[0])));
      const current=selections.get(captured),selected=active.find(i=>i.id===current?.id);
      renderViewer(doc,selected,selected?.pages.includes(current?.page)?current.page:selected?.pages[0]);
      installAnchors(doc,active);
    }catch(e){if(own===sequence&&host.isConnected)host.replaceChildren(node('p',{class:'status',text:e.message}),button('Tentar consultar fontes novamente',update));}
  }
  function renderViewer(doc,link,page){
    const body=document.querySelector('.document-body');if(!body)return;
    const visible=(state.readingTracker?.entries||[]).find(entry=>{const r=entry.node.getBoundingClientRect();return r.height>0&&r.top>=0&&r.top<window.innerHeight;});const originalTop=visible?.node.getBoundingClientRect().top;
    const restore=()=>{if(visible?.node.isConnected&&body.isConnected)requestAnimationFrame(()=>{if(visible.node.isConnected)window.scrollBy({top:visible.node.getBoundingClientRect().top-originalTop,behavior:'instant'});});};
    body.querySelector('.document-facsimile')?.remove();body.classList.remove('with-facsimile');
    if(state.viewMode!=='study'||!link){restore();return;}
    body.classList.add('with-facsimile');
    const select=node('select',{'aria-label':'Página física do fac-símile'});for(const number of link.pages)select.append(node('option',{value:String(number),text:'Página física '+number}));select.value=String(page);
    const frame=node('iframe',{class:'pdf-facsimile',title:'Fac-símile da fonte '+link.source_id,src:(link.static?absURL(link.pdf_url):'/api/editorial/pdf/'+link.source_id+'/file')+'#page='+(link.static?link.published_page_map[String(page)]:page)});
    const status=node('p',{class:'help',role:'status',text:'Página física '+page+' · '+link.source_id}),transcript=node('details',{},[node('summary',{text:'Consultar transcrição da página'})]),text=node('pre',{class:'pdf-raw-text'});transcript.append(text);
    const imagePanel=node('div',{class:'facsimile-location-scroll',hidden:''}),picture=node('div',{class:'pdf-alignment-image'}),image=node('img',{alt:'Localização editorial na página'}),overlay=document.createElementNS('http://www.w3.org/2000/svg','svg');overlay.setAttribute('viewBox','0 0 1000 1000');overlay.setAttribute('preserveAspectRatio','none');picture.append(image,overlay);imagePanel.append(picture);
    let locationURL=null;
    const locationButton=button('Imagem e localização',()=>{if(!locationURL)return;image.src=locationURL;imagePanel.hidden=!imagePanel.hidden;frame.hidden=!imagePanel.hidden;});
    image.onerror=()=>{status.textContent='Imagem de alinhamento indisponível; consulte o PDF.';imagePanel.hidden=true;frame.hidden=false;};
    let request=0,pageInfo=null;
    function location(number){const anchor=selections.get(key())?.anchor;const boxes=anchor?.page_number===number?anchor.unit_boxes||[]:[];const url=link.static?link.image_urls?.[String(number)]:'/api/editorial/pdf/'+link.source_id+'/pages/'+number+'/image.png';locationButton.hidden=!url;overlay.replaceChildren();imagePanel.hidden=!boxes.length;frame.hidden=!!boxes.length&&!!url;locationURL=url?(link.static?absURL(url):url):null;if(boxes.length&&locationURL)image.src=locationURL;for(const box of boxes){const r=document.createElementNS('http://www.w3.org/2000/svg','rect');for(const[k,v]of Object.entries({x:box[0]*1000,y:box[1]*1000,width:box[2]*1000,height:box[3]*1000,class:'manual-box'}))r.setAttribute(k,String(v));overlay.append(r);}}

    async function open(number){if(!link.pages.includes(number))return;page=number;pageInfo=null;selections.set(key(),{id:link.id,page});select.value=String(page);frame.src=(link.static?absURL(link.pdf_url):'/api/editorial/pdf/'+link.source_id+'/file')+'#page='+(link.static?link.published_page_map[String(page)]:page);location(page);const own=++request;text.textContent='Carregando transcrição local…';try{const data=link.static?link.page_snapshots.find(p=>p.page_number===page):await api('/api/editorial/pdf/'+link.source_id+'/pages/'+page+'/review');if(!data)throw new Error('Transcrição não publicada para esta página.');if(!frame.isConnected||own!==request)return;pageInfo=data;status.textContent='Página física '+page+(data.review.printed_label?' · impressa '+data.review.printed_label:'')+' · revisão da transcrição '+data.revision;text.textContent=data.review.text||'(Página sem transcrição)';}catch(e){if(frame.isConnected&&own===request)text.textContent=e.message;}}
    const hide=button('Recolher fac-símile',()=>{selections.delete(key());renderViewer(doc,null);});
    const citation=button('Copiar referência da página',async()=>{const citation=documentTitle(doc.meta)+' · documento '+doc.meta.id+' · fonte '+link.source_id+' · página física '+page+(pageInfo?.review.printed_label?' · impressa '+pageInfo.review.printed_label:'')+(pageInfo?' · transcrição revisão '+pageInfo.revision:'')+' · PDF SHA-256 '+link.source_sha256+' · vínculo '+link.id+' revisão '+link.revision+(scope()?' · projeto '+scope():'');try{await navigator.clipboard.writeText(citation);status.textContent='Referência da página copiada.';}catch{window.prompt('Copie a referência:',citation);}});
    const viewer=node('aside',{class:'document-facsimile','aria-label':'Fac-símile do documento'},[node('h3',{text:'Fac-símile · '+(link.source_title||link.source_id)}),node('div',{class:'pdf-source-toolbar'},[button('←',()=>open(link.pages[link.pages.indexOf(page)-1])),select,button('→',()=>open(link.pages[link.pages.indexOf(page)+1])),hide]),status,locationButton,frame,imagePanel,citation,transcript]);body.append(viewer);select.onchange=()=>open(Number(select.value));open(page);restore();
  }
  function installAnchors(doc,links){
    document.querySelectorAll('.facsimile-passage-action,.facsimile-anchor-action').forEach(e=>e.remove());
    if(state.viewMode!=='study')return;
    for(const row of document.querySelectorAll('.blocks > .block[data-study-block]')){
      const index=Number(row.dataset.studyBlock);
      for(const language of doc.langs){const block=language.blocks[index],cell=row.querySelector('.cell.lang-'+language.code);if(!cell||!block?.sourceMarkdown||!Number.isInteger(block.sourceStart)||!Number.isInteger(block.sourceEnd))continue;
        for(const link of links)for(const anchor of link.anchors.filter(a=>a.language===language.code&&a.quote===block.sourceMarkdown&&(a.start===block.sourceStart||a.stale_text&&language.source.indexOf(a.quote)===language.source.lastIndexOf(a.quote)))){
          const stale=anchor.stale_text||anchor.stale_page;
          const action=button((stale?'Revisar vínculo':'Ver fac-símile')+' · p. '+anchor.page_number,()=>{show(link,anchor.page_number,anchor);if(stale)window.alert('O texto ou a revisão da página mudou. Esta associação precisa de conferência; não foi realinhada automaticamente.');});action.classList.add('facsimile-anchor-action');cell.append(action);
          const cite=button('Copiar referência com fac-símile',async()=>{const value=documentTitle(doc.meta)+' · '+doc.meta.id+' · '+language.code.toUpperCase()+' · fonte '+link.source_id+' · PDF SHA-256 '+link.source_sha256+' · página física '+anchor.page_number+(anchor.printed_label?' · impressa '+anchor.printed_label:'')+' · associação '+anchor.id+' · vínculo revisão '+link.revision+' · texto SHA-256 '+anchor.quote_sha256+' · versão do texto SHA-256 '+anchor.body_sha256+' · transcrição da página revisão '+anchor.page_revision+(anchor.unit_id?' · unidade '+anchor.unit_id+' · SHA-256 '+anchor.unit_sha256:'')+(stale?' · associação requer reconferência':'')+(scope()?' · projeto '+scope():'');try{await navigator.clipboard.writeText(value);cite.textContent='Referência copiada';}catch{window.prompt('Copie a referência:',value);}});cite.classList.add('facsimile-anchor-action');cell.append(cite);
        }
        if(links.some(l=>!l.static)&&state.editorialAvailable&&!state.workspaceProject?.archived){const action=button('Associar página PDF',()=>associate(doc,language,block,links.filter(l=>!l.static)));action.classList.add('facsimile-passage-action');cell.append(action);}
      }
    }
  }
  async function associate(doc,language,block,links){
    const {dialog,body}=modal('Associar trecho ao fac-símile');
    const notice=node('p',{role:'status',class:'status'}),source=node('select',{'aria-label':'Fonte vinculada'}),page=node('select',{'aria-label':'Página física'}),notes=node('textarea',{rows:'2',maxlength:'4000','aria-label':'Nota sobre a associação'}),preview=node('section',{class:'pdf-preview',hidden:''});
    for(const link of links)source.append(node('option',{value:link.id,text:(link.source_title||link.source_id)+' · páginas '+link.pages.join(', ')}));const chosen=selections.get(key());source.value=links.some(l=>l.id===chosen?.id)?chosen.id:links[0].id;
    const unitSelect=node('select',{'aria-label':'Unidade da transcrição na página'});let unitRequest=0;
    async function loadUnits(){const own=++unitRequest;unitSelect.replaceChildren(node('option',{value:'',text:'Somente a página'}));unitSelect.value='';try{const link=links.find(i=>i.id===source.value);const data=await api('/api/editorial/pdf/'+link.source_id+'/pages/'+page.value+'/review');if(own!==unitRequest||!dialog.isConnected)return;if(data.revision)for(const u of data.review.units)unitSelect.append(node('option',{value:u.id,text:Array.from(data.review.text).slice(u.start,u.end).join('').slice(0,120)}));}catch{}}
    const sample=node('iframe',{class:'pdf-facsimile',title:'Conferir a página escolhida para o trecho'});
    function pages(){const link=links.find(i=>i.id===source.value);page.replaceChildren();for(const number of link.pages)page.append(node('option',{value:String(number),text:'Página física '+number}));page.value=String(link.id===chosen?.id&&link.pages.includes(chosen.page)?chosen.page:link.pages[0]);sample.src='/api/editorial/pdf/'+link.source_id+'/file#page='+page.value;preview.hidden=true;loadUnits();}
    source.onchange=pages;pages();page.onchange=()=>{sample.src='/api/editorial/pdf/'+links.find(i=>i.id===source.value).source_id+'/file#page='+page.value;preview.hidden=true;loadUnits();};notes.oninput=()=>{preview.hidden=true;};
    body.append(node('p',{class:'help',text:'Associação editorial manual entre este bloco e uma página física. Não determina a posição exata do parágrafo na imagem.'}),node('pre',{class:'pdf-raw-text',text:block.sourceMarkdown}),source,page,unitSelect,sample,notes,notice);
    let version=0;body.addEventListener('input',()=>{version++;preview.hidden=true;});
    const prepare=button('Conferir associação',async()=>{const submitted=version;prepare.disabled=true;try{const link=links.find(i=>i.id===source.value);const result=await api('/api/editorial/pdf/links/preview',{action:'anchor',id:link.id,revision:link.revision,anchor:{language:language.code,body_sha256:await hash(language.source),quote:block.sourceMarkdown,start:block.sourceStart,end:block.sourceEnd,page_number:Number(page.value),notes:notes.value,...(unitSelect.value?{unit_id:unitSelect.value}:{})}});if(!dialog.isConnected||submitted!==version)return;preview.replaceChildren(node('p',{text:doc.meta.id+' · '+language.code.toUpperCase()+' → página física '+page.value}),node('pre',{class:'pdf-raw-text',text:block.sourceMarkdown}),node('p',{text:'Nota: '+(notes.value||'—')}));
        const save=button('Confirmar associação local',async()=>{save.disabled=true;try{await api('/api/editorial/pdf/links/save',{preview_id:result.preview_id});if(dialog.isConnected)dialog.close();document.dispatchEvent(new CustomEvent('archive:pdf-links-changed'));}catch(e){notice.textContent=e.message;save.disabled=false;}});preview.append(save);preview.hidden=false;
      }catch(e){notice.textContent=e.message;}finally{prepare.disabled=false;}});body.append(prepare,preview);
  }
  for(const name of ['archive:reader-updated','archive:capabilities','archive:pdf-links-changed','archive:pdf-review-saved'])document.addEventListener(name,()=>update());
  return {toolbarHost,update,manager};
})();
