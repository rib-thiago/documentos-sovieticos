import {node as n,download} from './data.js';
import {editorialRequest as api} from './editorial.js';
const names={pendente:'Pendente',em_revisao:'Em revisão',corrigido:'Corrigido',adiado:'Adiado',urgente:'Urgente',alta:'Alta',media:'Média',baixa:'Baixa'};
const title=item=>item.titles?.pt||item.titles?.ru||item.titles?.en||item.id;
export function issuePayload(revision,documentId,key,values){
 return {revision,document_id:documentId,issues:[{chave:key,prioridade:values.prioridade,status:values.status,dificuldade_encontrada:values.dificuldade_encontrada,notas_do_revisor:values.notas_do_revisor}]};
}
export async function mountReview(env,documentId=''){
 const work=env.saved.reviewWork||={status:'abertos',priority:'',collection:'',q:'',offset:0};
 if(documentId&&work.document!==documentId){work.q=documentId;work.status='abertos';work.priority='';work.collection='';work.offset=0;work.document=documentId;work.selected='';}
 const shell=n('section',{class:'organization-page review-queue-page'}),results=n('div'),sheet=n('section',{class:'organization-sheet queue-case'}),pager=n('div',{class:'pagination'}),summary=n('p',{class:'queue-summary',role:'status'}),browser=n('section',{class:'organization-browser'});
 shell.append(env.heading('Organizar o trabalho','Fila de revisão','Escolha uma pendência, examine a fonte e registre sua avaliação. Alterar a situação da revisão não modifica o texto do documento.'));env.content.append(shell);shell.classList.toggle('queue-focused',Boolean(work.focused));
 env.controls.append(env.button('Catálogo',()=>env.navigate('catalogo'),'quiet'),env.button('Importar corpus',()=>env.navigate('importar'),'quiet'));
 const [session,collections]=await Promise.all([api('/api/editorial/session'),api('/api/collections')]);if(!env.current())return;
 const query=n('input',{type:'search',value:work.q||'',placeholder:'Título, ID, motivo ou nota…','aria-label':'Buscar pendências'}),status=env.select([['abertos','Em aberto'],['','Todas as situações'],...session.statuses.map(v=>[v,names[v]||v])],work.status??'abertos',()=>{},'Situação'),priority=env.select([['','Todas as prioridades'],...session.priorities.map(v=>[v,names[v]||v])],work.priority||'',()=>{},'Prioridade'),collection=env.select([['','Todo o acervo'],...collections.items.flatMap(root=>[[root.id,root.titles.pt||root.id],...(root.children||[]).map(sub=>[sub.id,'↳ '+(sub.titles.pt||sub.id)])])],work.collection||'',()=>{},'Coleção ou subcoleção');
 const filters=n('details',{class:'queue-filter-options'},[n('summary',{text:'Filtros de revisão'}),n('div',{class:'queue-filter-grid'},[['Situação',status],['Prioridade',priority],['Coleção / subcoleção',collection]].map(([text,input])=>n('label',{class:'organization-field'},[n('span',{text}),input])))]),form=n('form',{class:'queue-query'},[n('div',{class:'queue-search'},[query,env.button('Buscar',apply,'primary'),env.button('Limpar filtros',()=>{query.value='';status.value='abertos';priority.value='';collection.value='';work.document='';apply();},'quiet')]),filters]);
 form.onsubmit=event=>{event.preventDefault();apply();};
 for(const input of [status,priority,collection])input.onchange=apply;
 browser.append(results,pager);shell.append(form,summary,n('div',{class:'organization-grid queue-layout'},[browser,sheet]));
 let request=0,selection=0;
 function apply(){work.q=query.value.trim();work.status=status.value;work.priority=priority.value;work.collection=collection.value;work.offset=0;work.selected='';env.store();load();}
 async function load(){
  const token=++request;summary.textContent='Consultando pendências…';
  try{
   const params=new URLSearchParams({q:work.q||'',status:work.status??'abertos',priority:work.priority||'',collection:work.collection||'',offset:String(work.offset||0),limit:'25'});
   const data=await api('/api/editorial/queue?'+params);if(!env.current()||token!==request)return;
   if(data.total&&work.offset>=data.total){work.offset=Math.floor((data.total-1)/25)*25;return load();}
   summary.textContent=`${data.total} pendências nesta seleção · ${data.items.length?data.offset+1:0}–${Math.min(data.offset+data.limit,data.total)} · prioridade mais alta primeiro`;
   results.replaceChildren(...data.items.map(item=>{
    const button=env.button('',()=>choose(item),'organization-list-entry'+(item.chave===work.selected?' selected':''));button.dataset.issue=item.chave;button.setAttribute('aria-pressed',String(item.chave===work.selected));
    button.append(n('span',{class:'queue-item-tags'},[n('span',{class:'queue-priority '+item.prioridade,text:names[item.prioridade]||item.prioridade}),n('span',{text:names[item.status]||item.status})]),n('strong',{text:title(item)}),n('span',{class:'queue-item-reason',text:item.problema||'Revisão documental'}));return button;
   }));
   pager.replaceChildren(env.button('‹ Anterior',()=>turn(-25),'quiet'),n('span',{text:`${Math.floor(data.offset/25)+1} / ${Math.max(1,Math.ceil(data.total/25))}`}),env.button('Próxima ›',()=>turn(25),'quiet'));pager.firstChild.disabled=!data.offset;pager.lastChild.disabled=!data.has_more;
   const item=data.items.find(item=>item.chave===work.selected)||data.items[0];
   if(item)await choose(item);else{++selection;sheet.replaceChildren(n('div',{class:'queue-empty'},[n('h2',{text:'Nenhuma pendência nesta seleção'}),n('p',{text:'Tente outra situação, coleção ou palavra. Os filtros não alteram o acervo.'})]));}
  }catch(error){if(env.current()&&token===request)summary.textContent=error.message;}
 }
 function turn(step){work.offset=Math.max(0,(work.offset||0)+step);work.selected='';env.store();load();}
 async function choose(item){
  const token=++selection;work.selected=item.chave;env.store();sheet.replaceChildren(n('p',{class:'hint',text:'Abrindo pendência…'}));
  for(const button of results.children){const active=button.dataset.issue===item.chave;button.classList.toggle('selected',active);button.setAttribute('aria-pressed',String(active));}
  try{
   const snapshot=await api('/api/editorial/documents/'+encodeURIComponent(item.id));if(!env.current()||token!==selection)return;
   const issue=snapshot.issues.find(row=>row.chave===item.chave);if(!issue)throw Error('A pendência não está mais neste documento. Atualize a seleção.');
   const key='issue:'+issue.chave;if(env.work[key]&&!env.work[key].dirty)delete env.work[key];
   const initial={prioridade:issue.prioridade,status:issue.status,dificuldade_encontrada:issue.dificuldade_encontrada||'',notas_do_revisor:issue.notas_do_revisor||''},draft=env.work[key]||={revision:snapshot.revision,values:{...initial}},values=draft.values;
   const expand=env.button(work.focused?'Mostrar lista':'Ampliar ficha',()=>{work.focused=!work.focused;shell.classList.toggle('queue-focused',work.focused);expand.textContent=work.focused?'Mostrar lista':'Ampliar ficha';expand.setAttribute('aria-pressed',String(work.focused));env.store();},'quiet');expand.setAttribute('aria-pressed',String(Boolean(work.focused)));
   const doc=env.catalog.documents.get(item.id),actions=n('div',{class:'queue-case-links'},[expand,doc&&env.button('Abrir texto',()=>env.open(doc),'quiet'),env.button('Editar ficha',()=>env.navigate('catalogo/'+encodeURIComponent(item.id)),'quiet'),env.button('Histórico do documento',()=>env.history(item.id,'fila'),'quiet')]);
   const body=n('div',{class:'queue-case-body'}),fields=n('div',{class:'queue-case-fields'}),notice=n('p',{class:'hint',role:'status'});
   for(const [caption,text]of [['Motivo registrado',issue.problema],['Ação sugerida',issue.acao_sugerida]])body.append(n('section',{class:'queue-evidence'},[n('h3',{text:caption}),n('p',{text:text||'Não registrado'})]));
   for(const [key,caption,options]of [['status','Situação',session.statuses],['prioridade','Prioridade',session.priorities],['dificuldade_encontrada','Diagnóstico / dificuldade',null],['notas_do_revisor','Notas da revisão',null]]){
    const input=options?env.select(options.map(v=>[v,names[v]||v]),values[key],()=>{},caption):n('textarea',{'aria-label':caption,rows:4});input.value=values[key];input.oninput=input.onchange=()=>{values[key]=input.value;draft.dirty=true;env.store();};fields.append(n('label',{class:'organization-field'},[n('span',{text:caption}),input]));
   }
   const stale=draft.revision!==snapshot.revision;
   if(stale)body.append(n('p',{class:'backend-warning',text:'O acervo ou a fila mudou desde este rascunho. Ele foi preservado. Exporte-o se necessário e recarregue a ficha antes de preparar outra gravação.'}));
   body.append(fields,n('p',{class:'hint',text:'Marcar Corrigido registra sua avaliação. Não corrige Markdown, não traduz nem confirma automaticamente um vínculo de fac-símile.'}),notice);
   const save=env.button('Conferir registro da revisão',async()=>{
    save.disabled=true;notice.textContent='Preparando a prévia; nada foi salvo.';
    try{
     const result=await api('/api/editorial/preview',{body:issuePayload(draft.revision,item.id,issue.chave,values)});if(!env.current()||token!==selection)return;
     env.review(result,{title:'Conferir registro da revisão',workKey:key,returnRoute:'fila',propertyRows:Object.keys(initial).filter(field=>initial[field]!==values[field]).map(field=>({field:({status:'Situação',prioridade:'Prioridade',dificuldade_encontrada:'Diagnóstico / dificuldade',notas_do_revisor:'Notas da revisão'})[field],before:names[initial[field]]||initial[field]||'—',after:names[values[field]]||values[field]||'—'})),information:[['Documento',item.id],['Pendência',issue.chave],['Motivo original',issue.problema]],effectText:'Altera somente prioridade, situação, diagnóstico e notas desta pendência, com histórico recuperável. Não modifica os textos, traduções, metadados ou vínculos do documento.',confirmText:'Confirmo registrar esta avaliação na fila local, sem alterar o texto do documento.',saveLabel:'Salvar registro da revisão',successText:'Avaliação registrada na fila, com histórico. O texto do documento permanece igual.'});
    }catch(error){notice.textContent=error.message;}finally{if(env.current())save.disabled=!env.canWrite||stale;}
   },'primary');save.disabled=!env.canWrite||stale;
   const reset=env.button('Recarregar ficha',()=>{if(JSON.stringify(values)!==JSON.stringify(initial)&&!confirm('Descartar o rascunho desta pendência e carregar os valores salvos?'))return;delete env.work[key];env.store();choose(item);},'quiet');
   sheet.replaceChildren(n('header',{class:'organization-sheet-heading'},[n('p',{class:'eyebrow',text:issue.id}),n('h2',{text:title(item)}),actions]),body,n('footer',{class:'organization-actions'},[env.button('Exportar rascunho',()=>download(issue.id+'-revisao.json',JSON.stringify({document_id:item.id,key:issue.chave,...draft},null,2),'application/json'),'quiet'),reset,save]));
  }catch(error){if(env.current()&&token===selection)sheet.replaceChildren(n('div',{class:'queue-empty'},[n('p',{text:error.message}),env.button('Atualizar lista',load,'quiet')]));}
 }
 env.controls.append(env.button('Atualizar fila',load,'quiet'));await load();
}
