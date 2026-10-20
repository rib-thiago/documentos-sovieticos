/* Edições privadas por workspace. A incorporação ao acervo é uma ação separada. */
window.archiveProjectEditor=(()=>{
  const drafts=new Map();let token;
  const node=(tag,attrs={},children=[])=>{const e=document.createElement(tag);for(const[k,v]of Object.entries(attrs))if(k==='text')e.textContent=v;else if(v!=null)e.setAttribute(k,v);for(const c of children)e.append(c);return e;};
  const button=(text,run)=>{const e=node('button',{type:'button',text});e.onclick=run;return e;};
  async function api(path,payload){
    if(payload&&!token){const response=await fetch('/api/editorial/session',{cache:'no-store'});const data=await response.json();if(!response.ok)throw new Error(data.error);token=data.token;}
    const response=await fetch(path,{cache:'no-store',method:payload?'POST':'GET',headers:payload?{'Content-Type':'application/json','X-Editorial-Token':token}:{},body:payload?JSON.stringify(payload):undefined});
    const data=await response.json();if(!response.ok)throw new Error(data.error||'Não foi possível concluir a operação do projeto');return data;
  }
  function query(project,edition){return new URLSearchParams({project,edition});}
  function changed(){try{localStorage.setItem('researchDraftChanged',String(Date.now()));}catch{}}
  async function render(area,doc){
    const projectId=state.workspaceProject?.id;if(!projectId)return;
    const codes=[...new Set([...doc.langs.map(l=>l.code),'pt','en'])];
    const select=node('select',{'aria-label':'Idioma da versão do projeto'});
    for(const code of codes)select.append(node('option',{value:code,text:({ru:'Russo',pt:'Português',en:'Inglês'}[code]||code)}));
    select.value=new URLSearchParams(location.hash.split('?')[1]||'').get('idioma')||documentActionLanguage(doc.meta,doc.langs);if(!select.value)select.selectedIndex=0;
    const host=node('div');area.append(node('p',{class:'workspace-scope-note',text:'Workspace: '+state.workspaceProject.title+' · salvar aqui não altera a edição do acervo.'}),node('label',{text:'Versão de trabalho '},[select]),host);
    let generation=0;
    async function load(){
      const own=++generation,language=select.value,editionId=doc.meta.id+':'+language,key=projectId+'|'+editionId;
      host.replaceChildren(node('p',{text:'Carregando versão do projeto…'}));
      try{
        const data=await api('/api/editorial/workspace/edition?'+query(projectId,editionId));if(!host.isConnected||own!==generation)return;
        const pending=drafts.get(key);let content=pending?.text??data.content,filename=pending?.filename||'',editVersion=0;
        const originalState=pending?.base??data;
        const input=node('textarea',{class:'workspace-markdown-source',spellcheck:'false','aria-label':'Markdown da versão de trabalho do projeto'});input.value=content;
        const notice=node('p',{class:'workspace-help',role:'status',text:data.has_draft?'Versão de trabalho salva neste projeto.':'Nenhuma versão própria salva: usando a edição do acervo como ponto de partida.'});
        if(pending&&pending.base.revision!==data.revision)notice.textContent='Há um rascunho não salvo baseado em outra revisão. Baixe uma cópia antes de recarregar; a gravação antiga será rejeitada.';
        const preview=node('div',{class:'reading-content workspace-markdown-preview',lang:language});
        const reviewArea=node('section',{class:'workspace-review',hidden:''});
        const renderPreview=()=>{preview.innerHTML=safeMarkdown(splitExportHeaders(input.value).body,{docId:'project-preview-'+editionId});};
        renderPreview();
        const save=button('Revisar e salvar no projeto',()=>prepare());
        const renderButton=button('Prévia do texto',()=>{renderPreview();preview.hidden=!preview.hidden;});preview.hidden=true;
        const download=button('Baixar versão de trabalho',()=>{const a=node('a',{download:doc.meta.id+'.'+language+'.projeto.md'});const uri=URL.createObjectURL(new Blob([input.value],{type:'text/markdown;charset=utf-8'}));a.href=uri;a.click();setTimeout(()=>URL.revokeObjectURL(uri),1000);});
        const upload=node('input',{type:'file',accept:'.md,.markdown','aria-label':'Carregar tradução Markdown no projeto'});
        upload.onchange=async()=>{const file=upload.files[0];if(!file)return;try{if(file.size>4*1024*1024)throw new Error('O limite é 4 MiB.');const text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(await file.arrayBuffer());if(!host.isConnected||own!==generation)return;filename=file.name;input.value=text;input.dispatchEvent(new Event('input'));notice.textContent='Arquivo carregado como candidato. Confira a prévia e a identificação antes de salvar no projeto.';}catch(e){notice.textContent=e.message;}};
        const actions=node('div',{class:'workspace-editor-actions'},[save,renderButton,download]);
        const promote=button('Incorporar versão salva ao acervo…',()=>promotion());
        promote.disabled=!data.has_draft||data.content_sha256===data.canonical_sha256||Boolean(pending);
        actions.append(promote);
        if(data.archived){input.disabled=true;save.disabled=true;upload.disabled=true;promote.disabled=true;}
        if(data.format==='text'){save.disabled=true;notice.textContent='Esta edição TXT é apenas consultada. A conversão editorial para Markdown precisa de uma etapa própria.';}
        input.oninput=()=>{content=input.value;editVersion++;if(content===originalState.content&&!filename)drafts.delete(key);else drafts.set(key,{text:content,filename,base:originalState});reviewArea.hidden=true;promote.disabled=true;notice.textContent=drafts.has(key)?'Alterações ainda não salvas no projeto. O acervo permanece preservado.':'Sem alterações pendentes neste editor.';};
        actions.append(button('Recarregar versão salva',()=>{if(drafts.has(key)&&!confirm('Descartar somente o rascunho ainda não salvo e recarregar a versão atual do projeto?'))return;drafts.delete(key);load();}));
        host.replaceChildren(notice,input,node('label',{class:'workspace-help',text:'Importar Markdown para esta versão do projeto '},[upload]),actions,preview,reviewArea);
        const request=()=>({project_id:projectId,edition_id:editionId,revision:originalState.revision,content_sha256:originalState.content_sha256,content:input.value,...(filename?{filename}:{})});
        async function prepare(historyId){
          const submitted=editVersion;
          save.disabled=true;reviewArea.hidden=true;
          try{const payload=request();if(historyId)payload.history_id=historyId;const result=await api('/api/editorial/workspace/preview',payload);if(!host.isConnected||own!==generation)return;if(submitted!==editVersion){notice.textContent='O texto mudou durante a preparação. Revise novamente.';return;}
            showReview('Salvar somente neste projeto',result.diff.text,async()=>{await api('/api/editorial/workspace/save',{preview_id:result.preview_id});drafts.delete(key);changed();await route();},result.warnings?.map(w=>w.message)||[],result.discard?'A versão de trabalho será removida; a leitura volta à edição atual do acervo.':'O histórico da versão de trabalho será preservado. Nenhum arquivo do acervo será substituído.');
          }catch(e){notice.textContent=e.message;}finally{save.disabled=Boolean(data.archived)||data.format==='text';}
        }
        function showReview(title,diff,confirmAction,warnings=[],description=''){
          reviewArea.replaceChildren(node('h3',{text:title}),node('p',{text:description}));
          for(const warning of warnings)reviewArea.append(node('p',{class:'workspace-scope-note',text:warning}));
          reviewArea.append(node('pre',{class:'project-diff',text:diff}));
          const accepted=node('input',{type:'checkbox'});const isPromotion=title.includes('acervo');
          reviewArea.append(node('label',{class:'project-source-choice'},[accepted,node('span',{text:isPromotion?'Confirmo incorporar esta versão ao acervo local, substituindo a existente quando houver.':'Conferi as diferenças e eventuais divergências de identificação.'})]));
          const confirm=button(isPromotion?'Confirmar incorporação ao acervo':'Confirmar gravação no projeto',async()=>{
            confirm.disabled=true;input.disabled=true;select.disabled=true;upload.disabled=true;save.disabled=true;promote.disabled=true;
            try{await confirmAction();}catch(e){notice.textContent=e.message;confirm.disabled=false;}finally{input.disabled=Boolean(data.archived);select.disabled=false;upload.disabled=Boolean(data.archived);save.disabled=Boolean(data.archived);}
          });confirm.disabled=true;accepted.onchange=()=>confirm.disabled=!accepted.checked;
          reviewArea.append(confirm,button('Cancelar',()=>{reviewArea.hidden=true;}));reviewArea.hidden=false;
        }
        async function promotion(){
          if(drafts.has(key)){notice.textContent='Salve as alterações antes de incorporar a versão ao acervo.';return;}
          const submitted=editVersion;promote.disabled=true;
          try{const result=await api('/api/editorial/workspace/promotion-preview',{project_id:projectId,edition_id:editionId,revision:data.revision,content_sha256:data.content_sha256});if(!host.isConnected||own!==generation||submitted!==editVersion)return;
            const warnings=[];if(result.canonical_changed)warnings.push('A edição do acervo mudou desde a origem deste trabalho. Compare com atenção a versão atual mostrada nas diferenças.');
            for(const finding of result.translation?.findings||[])warnings.push(finding.message||String(finding));
            showReview('Incorporar ao acervo — confirmação explícita',result.workspace_diff.text,async()=>{
              const saved=await api('/api/editorial/workspace/promote',{promotion_id:result.workspace_promotion_id,confirm_replace:true,acknowledge_warnings:true});
              try{localStorage.setItem('editorialCatalogChanged',Date.now()+':'+saved.history_id);}catch{}
              await reloadEditorialCatalog();
            },warnings,'Esta ação modifica a edição principal local, catálogo, manifesto e busca, com histórico editorial. Enviar ao GitHub continua sendo uma operação separada.');
          }catch(e){notice.textContent=e.message;}finally{promote.disabled=!data.has_draft||data.content_sha256===data.canonical_sha256||drafts.has(key);}
        }
        const history=node('details',{},[node('summary',{text:'Histórico desta versão no projeto'})]),records=node('div');history.append(records);host.append(history);
        async function loadHistory(){
          records.replaceChildren(node('p',{class:'workspace-help',role:'status',text:'Carregando histórico…'}));
          try{
            const result=await api('/api/editorial/workspace/history?'+query(projectId,editionId));
            if(!host.isConnected||own!==generation)return;
            records.replaceChildren();
            for(const record of result.items){const item=node('div',{class:'workspace-history-item'},[node('p',{text:record.created_at}),node('p',{text:record.before_state?'Restaurar o texto salvo antes desta alteração.':'Voltar a usar a versão do acervo, sem apagar seu histórico.'})]);item.append(button('Conferir restauração',()=>prepare(record.id)));records.append(item);}
            if(!result.items.length)records.append(node('p',{class:'workspace-help',text:'Nenhuma versão de trabalho salva ainda.'}));
          }catch(e){
            if(!host.isConnected||own!==generation)return;
            records.replaceChildren(node('p',{class:'workspace-help',role:'status',text:'Histórico indisponível: '+e.message+'. O editor continua disponível.'}),button('Tentar carregar histórico novamente',loadHistory));
          }
        }
        await loadHistory();
      }catch(e){if(host.isConnected&&own===generation)host.replaceChildren(node('p',{text:e.message}));}
    }
    select.onchange=()=>{const [path,raw='']=location.hash.split('?');const params=new URLSearchParams(raw);params.set('idioma',select.value);history.replaceState(null,'',path+'?'+params);load();};await load();
  }
  window.addEventListener('beforeunload',event=>{if(drafts.size){event.preventDefault();event.returnValue='';}});
  return {render,api};
})();
