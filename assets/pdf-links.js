/* Vínculos editoriais locais. Histórico e contexto não dependem da posição na lista. */
window.archivePDFLinks=(()=>{
  const node=(tag,attrs={},children=[])=>{const e=document.createElement(tag);for(const[k,v]of Object.entries(attrs))if(k==='text')e.textContent=v;else if(v!=null)e.setAttribute(k,v);for(const child of children)e.append(child);return e;};
  const button=(text,fn)=>{const e=node('button',{type:'button',text});e.onclick=fn;return e;};
  const select=(choices,value='')=>{const e=node('select');for(const[v,t]of choices)e.append(node('option',{value:v,text:t}));e.value=value;return e;};
  const label=(name,input)=>node('label',{class:'field',text:name},[input]);
  const query=(documentId,projectId)=>new URLSearchParams({document:documentId,project:projectId||''});
  async function renderManager(host,{api,documentId='',sourceId='',projectId='',signal,onSaved=()=>{}}){
    const shell=node('section',{class:'pdf-tools pdf-links-manager'});host.replaceChildren(shell);
    const notice=node('p',{class:'status',role:'status'}),list=node('div'),preview=node('section',{class:'pdf-preview',hidden:''});
    shell.append(node('h3',{text:'Documentos e fac-símiles'}),node('p',{class:'help',text:projectId?'Vínculos privados deste projeto. Não alteram os vínculos do acervo.':'Vínculos locais sem projeto. A disponibilização pública dos PDFs será uma ação editorial posterior.'}),notice);
    const sources=await api('/api/editorial/pdf/sources',null,signal);if(signal?.aborted||!shell.isConnected)return;
    const form=node('form',{class:'pdf-source-form'}),doc=node('input',{type:'text',required:'','aria-label':'ID do documento'});doc.value=documentId;doc.readOnly=!!documentId;
    if(!documentId){const search=node('input',{type:'search','aria-label':'Buscar documento por título ou termos'}),results=select([['','Selecione um resultado']]);const searchBox=node('div',{class:'pdf-source-toolbar'},[search,button('Buscar documento',async()=>{try{const result=await api('/api/documents?'+new URLSearchParams({q:search.value,limit:'30',scope:'all'}),null,signal);if(!shell.isConnected)return;results.replaceChildren(node('option',{value:'',text:'Selecione um resultado'}));for(const d of result.items)results.append(node('option',{value:d.id,text:d.id+' · '+(d.titles?.pt||d.titles?.ru||d.id)}));}catch(e){notice.textContent=e.message;}}),results]);results.onchange=()=>{if(results.value){doc.value=results.value;load();}};shell.append(searchBox);}
    const source=select([['','Escolha uma fonte PDF'],...sources.items.map(s=>[s.id,(s.metadata.title||s.filename)+' · '+(s.page_count??'?')+' páginas'])],sourceId);source.required=true;if(sourceId)source.disabled=true;
    const pages=node('input',{type:'text',placeholder:'1-5, 8',required:''}),notes=node('textarea',{rows:'2',maxlength:'4000'});
    const submit=node('button',{type:'submit',class:'primary',text:'Conferir novo vínculo'});
    form.append(label('ID do documento',doc),label('Fonte PDF',source),label('Páginas físicas que compõem este documento',pages),label('Notas sobre a correspondência',notes),submit);shell.append(form,preview,list);
    let version=0;form.oninput=()=>{version++;preview.hidden=true;};doc.onchange=load;
    async function prepare(payload){
      const submitted=version;
      try{const result=await api('/api/editorial/pdf/links/preview',payload,signal);if(!shell.isConnected||signal?.aborted||submitted!==version)return;
        preview.replaceChildren(node('h4',{text:'Confira o vínculo proposto'}),node('p',{text:result.after.document_id+' ← '+result.after.source_id}),node('p',{text:'Páginas físicas: '+result.after.pages.join(', ')+' · '+(result.after.active?'Ativo':'Inativo')}),node('p',{text:'Associações de trechos: '+result.before.anchors.length+' → '+result.after.anchors.length}),node('p',{text:'Notas: '+(result.before.notes||'—')+' → '+(result.after.notes||'—')}));
        const before=node('details',{},[node('summary',{text:'Ver estado anterior e proposto'}),node('pre',{class:'pdf-raw-text',text:JSON.stringify({antes:result.before,depois:result.after},null,2)})]);preview.append(before);
        const save=button('Confirmar vínculo local',async()=>{save.disabled=true;try{await api('/api/editorial/pdf/links/save',{preview_id:result.preview_id},signal);if(shell.isConnected){preview.hidden=true;notice.textContent='Vínculo salvo. Textos e arquivos do acervo foram preservados.';await load();onSaved();document.dispatchEvent(new CustomEvent('archive:pdf-links-changed'));}}catch(e){notice.textContent=e.message;save.disabled=false;}});preview.append(save);preview.hidden=false;
      }catch(e){notice.textContent=e.message;}
    }
    form.onsubmit=e=>{e.preventDefault();prepare({action:'create',document_id:doc.value.trim(),project_id:projectId,source_id:source.value,pages:pages.value,notes:notes.value});};
    async function load(){
      if(!doc.value.trim())return;
      const selected=doc.value.trim();
      try{const data=await api('/api/editorial/pdf/links?'+query(selected,projectId),null,signal);if(!shell.isConnected||signal?.aborted||doc.value.trim()!==selected)return;list.replaceChildren(node('h4',{text:'Vínculos existentes'}));
        for(const item of data.items.filter(i=>!sourceId||i.source_id===sourceId)){
          const range=node('input',{type:'text'});range.value=item.pages.join(', ');
          const comment=node('textarea',{rows:'2',maxlength:'4000'});comment.value=item.notes;
          const active=node('input',{type:'checkbox'});active.checked=item.active;
          const entry=node('article',{class:'panel pdf-link-entry'},[node('h4',{text:sources.items.find(s=>s.id===item.source_id)?.metadata.title||sources.items.find(s=>s.id===item.source_id)?.filename||item.source_id}),node('p',{class:'pdf-source-id',text:item.id+' · revisão '+item.revision}),label('Páginas físicas',range),label('Notas',comment),label('Vínculo ativo',active)]);
          entry.oninput=()=>{version++;preview.hidden=true;};
          entry.append(button('Conferir alteração do vínculo',()=>prepare({action:'update',id:item.id,revision:item.revision,pages:range.value,notes:comment.value,active:active.checked})));
          for(const anchor of item.anchors){const warning=anchor.stale_text||anchor.stale_page?' · REVISAR: texto ou transcrição mudou':'';entry.append(node('div',{class:'pdf-anchor-record'},[node('p',{text:anchor.language.toUpperCase()+' → página '+anchor.page_number+warning}),node('blockquote',{text:anchor.quote.slice(0,300)}),button('Conferir remoção desta associação',()=>prepare({action:'remove_anchor',id:item.id,revision:item.revision,anchor_id:anchor.id}))]));}
          const history=node('details',{},[node('summary',{text:'Histórico do vínculo'})]),records=node('div');history.append(records);history.addEventListener('toggle',async()=>{if(!history.open||records.childElementCount)return;try{const data=await api('/api/editorial/pdf/links/'+item.id+'/history',null,signal);if(!history.isConnected)return;for(const h of data.items)records.append(node('div',{class:'panel'},[node('p',{text:h.created_at}),node('details',{},[node('summary',{text:'Consultar estado anterior'}),node('pre',{class:'pdf-raw-text',text:JSON.stringify(h.before_state,null,2)})]),button('Preparar restauração',()=>prepare({action:'restore',id:item.id,revision:item.revision,history_id:h.id}))]));}catch(e){records.textContent=e.message;}});entry.append(history);list.append(entry);
        }
      }catch(e){notice.textContent=e.message;}
    }
    await load();
  }
  return {renderManager,query};
})();
