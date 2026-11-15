import {node as n,LANGUAGES,parseImportFile,renderMarkdown,download} from './data.js';
import {editorialRequest as api} from './editorial.js';

// Conteúdo dos arquivos permanece em memória até a gravação; não ocupa sessionStorage.
let files=[];
const bytes=text=>new TextEncoder().encode(text).length;
export function corpusProblems(entries,existing=new Set()){
 const problems=[],groups=new Map(),names=new Set();
 if(!entries.length)problems.push('Selecione os arquivos do corpus.');
 if(entries.length>100)problems.push('Use no máximo 100 arquivos por lote.');
 let total=0;
 for(const item of entries){
  const id=item.id.trim();total+=bytes(item.original);
  if(names.has(item.filename))problems.push('Nome de arquivo repetido: '+item.filename);names.add(item.filename);
  if(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(id))problems.push(item.filename+': ajuste o ID (minúsculas, números e hífens).');
  if(existing.has(id))problems.push(id+': já existe no acervo. Abra o documento e use Importar tradução.');
  if(!item.title.trim())problems.push(item.filename+': informe o título desta versão.');
  if(!LANGUAGES[item.lang])problems.push(item.filename+': confirme o idioma.');
  if(!['original','translation'].includes(item.role))problems.push(item.filename+': confirme original ou tradução.');
  if(!item.original.trim()||item.original.includes('\0'))problems.push(item.filename+': texto vazio ou inválido.');
  if(bytes(item.original)>4*1024*1024)problems.push(item.filename+': limite de 4 MiB por arquivo.');
  if(!groups.has(id))groups.set(id,[]);groups.get(id).push(item);
 }
 for(const [id,group]of groups){
  if(group.filter(item=>item.role==='original').length!==1)problems.push(id+': escolha exatamente um original e associe as traduções ao mesmo ID.');
  if(new Set(group.map(item=>item.lang)).size!==group.length)problems.push(id+': há idiomas repetidos.');
 }
 if(total>20*1024*1024)problems.push('Limite de 20 MiB para o conjunto.');
 return [...new Set(problems)];
}
export function corpusPayload(entries,defaults,revision){
 return {revision,defaults,entries:entries.map(item=>({filename:item.filename,content:item.original,id:item.id.trim(),title:item.title.trim(),language:item.lang,role:item.role}))};
}
function field(env,caption,value='',choices=null){
 const input=choices?env.select(choices,value,()=>{},caption):n('input',{'aria-label':caption,value});
 return {input,node:n('label',{class:'organization-field'},[n('span',{text:caption}),input])};
}
function corpusPreview(entries){
 const host=n('section',{class:'corpus-reading'}),choose=n('select',{'aria-label':'Conferir arquivo do corpus',class:'control'}),text=n('article',{class:'edition-body'}),identity=n('p',{class:'hint'});
 for(const [index,item]of entries.entries())choose.append(n('option',{value:index,text:`${item.id} · ${LANGUAGES[item.lang]} · ${item.role==='original'?'Original':'Tradução'} · ${item.filename}`}));
 const draw=()=>{const item=entries[Number(choose.value)];identity.textContent=item.title+' · conteúdo do arquivo selecionado, sem alinhamento automático';text.innerHTML=renderMarkdown(item.body);};
 choose.onchange=draw;host.append(choose,identity,text);draw();return host;
}
export function mountCorpus(env){
 const work=env.saved.corpusWork||={original:'ru'},shell=n('section',{class:'organization-page corpus-page'}),notice=n('p',{class:'corpus-notice',role:'status'}),errors=n('ul',{class:'corpus-errors',role:'alert'}),table=n('div',{class:'corpus-files'}),summary=n('p',{class:'hint'});
 const stages=[n('section'),n('section'),n('section')],bar=n('nav',{class:'organization-tabs corpus-stage-tabs','aria-label':'Etapas da importação'}),buttons=[];
 function show(index){stages.forEach((stage,i)=>stage.hidden=i!==index);buttons.forEach((button,i)=>{button.classList.toggle('active',i===index);button.setAttribute('aria-current',i===index?'step':'false');});work.stage=index;env.store();}
 for(const [index,title]of ['1 · Contexto','2 · Arquivos e versões','3 · Conferência'].entries()){const button=env.button(title,()=>{show(index);if(index===2)check();},'organization-tab');buttons.push(button);bar.append(button);}
 shell.append(env.heading('Incorporar fontes','Um corpus, suas versões.','Associe originais e traduções por documento. O cadastro só acontece após a prévia e a confirmação explícita.'),bar,notice,errors,...stages);env.content.append(shell);
 env.controls.append(env.button('Coleções',()=>env.navigate('colecoes'),'quiet'),env.button('Catálogo',()=>env.navigate('catalogo'),'quiet'));
 const collection=field(env,'Coleção',work.collection||'',[['','Escolha uma coleção'],...env.catalog.collections.map(c=>[c.id,c.title_pt||c.title_ru||c.title||c.id])]),sub=field(env,'Subcoleção',work.subcollection||'',[['','Sem subcoleção']]),original=field(env,'Idioma original sugerido',work.original,Object.entries(LANGUAGES));
 function syncSubs(){const previous=work.subcollection;sub.input.replaceChildren(n('option',{value:'',text:'Sem subcoleção'}),...(env.catalog.collections.find(c=>c.id===collection.input.value)?.subcollections||[]).map(c=>n('option',{value:c.id,text:c.title_pt||c.title_ru||c.title||c.id})));sub.input.value=[...sub.input.options].some(o=>o.value===previous)?previous:'';work.subcollection=sub.input.value;}
 collection.input.onchange=()=>{work.collection=collection.input.value;work.subcollection='';syncSubs();env.store();};sub.input.onchange=()=>{work.subcollection=sub.input.value;env.store();};syncSubs();
 original.input.onchange=()=>{work.original=original.input.value;env.store();};
 const common={};for(const [key,caption]of [['source_name','Nome da fonte'],['source_url','URL da fonte'],['author','Autoria compartilhada'],['date','Data histórica compartilhada'],['archive','Referência arquivística compartilhada']]){
  common[key]=field(env,caption,work[key]||'');common[key].input.oninput=()=>{work[key]=common[key].input.value;env.store();};
 }
 const context=n('div',{class:'corpus-context-grid'},[collection.node,sub.node,original.node,...Object.values(common).map(f=>f.node)]);
 stages[0].append(n('h2',{text:'Contexto do conjunto'}),n('p',{class:'hint',text:'Coleção é o conjunto principal; subcoleção é uma divisão opcional dele. Preencha autoria, data e referência apenas quando forem comuns a TODOS os documentos. O idioma sugerido ajuda na seleção; confirme cada versão na próxima etapa.'}),context,env.button('Selecionar arquivos →',()=>show(1),'primary'));
 const picker=n('input',{type:'file',multiple:true,accept:'.md,.markdown,.txt','aria-label':'Selecionar originais e traduções'}),drop=n('div',{class:'upload-area'},[n('strong',{text:'Originais e traduções'}),n('p',{text:'Markdown ou TXT em UTF-8. Exemplo: carta-01.ru.md, carta-01.pt.md. Até 100 arquivos, 4 MiB por arquivo e 20 MiB no total.'}),picker]);
 let loading=false;
 async function receive(selected){
  if(loading)return;loading=true;notice.textContent='Lendo os arquivos…';
  try{
   const incoming=[...selected];if(incoming.length+files.length>100)throw Error('Use no máximo 100 arquivos por lote.');
   let total=files.reduce((sum,item)=>sum+bytes(item.original),0);const additions=[],names=new Set(files.map(f=>f.filename));
   for(const file of incoming){
    if(!/\.(md|markdown|txt)$/i.test(file.name))throw Error('Formato não aceito: '+file.name);
    if(names.has(file.name))throw Error('Nome de arquivo repetido: '+file.name);names.add(file.name);
    total+=file.size;if(file.size>4*1024*1024||total>20*1024*1024)throw Error('Respeite 4 MiB por arquivo e 20 MiB no total.');
    let text;try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(await file.arrayBuffer());}catch{throw Error(file.name+': não foi possível ler como UTF-8.');}
    const item=parseImportFile(file.name,text);item.lang||=work.original;item.role=item.lang===work.original?'original':'translation';additions.push(item);
   }
   files.push(...additions);if(env.current())draw();notice.textContent=`${files.length} arquivos carregados. A associação é sugerida; confirme ID, idioma e papel de cada versão.`;
  }catch(error){notice.textContent=error.message;}finally{loading=false;picker.value='';}
 }
 picker.onchange=()=>receive(picker.files);drop.ondragover=e=>{e.preventDefault();drop.classList.add('dragover');};drop.ondragleave=()=>drop.classList.remove('dragover');drop.ondrop=e=>{e.preventDefault();drop.classList.remove('dragover');receive(e.dataTransfer.files);};
 function draw(){
  table.replaceChildren();summary.textContent=`${files.length} arquivos · ${new Set(files.map(f=>f.id.trim())).size} documentos sugeridos · originais e traduções precisam do mesmo ID.`;
  for(const item of files){
   const id=field(env,'ID do documento',item.id),title=field(env,'Título desta versão',item.title),lang=field(env,'Idioma',item.lang,Object.entries(LANGUAGES)),role=field(env,'Papel da versão',item.role,[['original','Original'],['translation','Tradução de trabalho']]);
   id.input.oninput=()=>item.id=id.input.value;title.input.oninput=()=>item.title=title.input.value;lang.input.onchange=()=>item.lang=lang.input.value;role.input.onchange=()=>item.role=role.input.value;
   table.append(n('article',{class:'corpus-file-card'},[n('header',{},[n('strong',{text:item.filename}),env.button('Remover',()=>{files=files.filter(f=>f!==item);draw();},'quiet')]),n('p',{class:'hint',text:item.identification+' · confirme as sugestões abaixo'}),n('div',{class:'corpus-associations'},[id.node,title.node,lang.node,role.node])]));
  }
 }
 stages[1].append(drop,summary,n('p',{class:'hint',text:'Cada documento novo precisa de um original. Arquivos com o mesmo ID são versões dele, em idiomas distintos. Para documentos já cadastrados, use Importar tradução no próprio documento. Os arquivos selecionados permanecem em memória até recarregar a página.'}),table,env.button('Conferir associações →',()=>{show(2);check();},'primary'));
 const grouping=n('div',{class:'corpus-grouping'}),review=env.button('Gerar prévia de cadastro',prepare,'primary');
 function check(){
  const problems=corpusProblems(files,new Set(env.catalog.documents.keys()));if(!collection.input.value)problems.unshift('Escolha a coleção na etapa Contexto.');
  errors.replaceChildren(...problems.map(text=>n('li',{text})));errors.hidden=!problems.length;
  const groups=new Map();for(const item of files){if(!groups.has(item.id))groups.set(item.id,[]);groups.get(item.id).push(item);}
  grouping.replaceChildren(...[...groups].map(([id,entries])=>n('article',{class:'note-card'},[n('strong',{text:id}),...entries.map(item=>n('p',{text:`${LANGUAGES[item.lang]||'Idioma não confirmado'} · ${item.role==='original'?'Original':'Tradução'} · ${item.title} · ${item.filename}`}))])));
  review.disabled=Boolean(problems.length)||!env.canWrite||loading;return problems;
 }
 async function prepare(){
  if(check().length)return;review.disabled=true;notice.textContent='Preparando a prévia; nada foi cadastrado.';
  try{
   const fresh=await api('/api/editorial/session');
   const defaults={...Object.fromEntries(Object.entries(common).map(([key,f])=>[key,f.input.value.trim()])),collection_ids:[collection.input.value,...sub.input.value?[sub.input.value]:[]]};
   const result=await api('/api/editorial/batches/preview',{body:corpusPayload(files,defaults,fresh.revision)});if(!env.current())return;
   if(result.can_save===false){errors.replaceChildren(...result.batch.errors.map(error=>n('li',{text:[error.filename||error.id,error.message].filter(Boolean).join(': ')})));errors.hidden=false;notice.textContent='O backend encontrou pendências. Corrija as associações antes de gerar outra prévia.';return;}
   const selected=files.map(item=>({...item}));
   env.review(result,{title:'Conferir cadastro do corpus',returnRoute:'importar',renderContent:()=>corpusPreview(selected),information:[['Destino',collection.input.selectedOptions[0].textContent+(sub.input.value?' › '+sub.input.selectedOptions[0].textContent:'')],['Quantidade',`${result.creation.count} documentos · ${selected.length} versões`],['Avisos',result.creation.warnings.join('\n')||'Nenhum aviso adicional.'],['Estrutura','As traduções são de trabalho. Não há alinhamento automático por parágrafos.']],ackText:'Li os avisos em Informações e conferi as identificações, os idiomas e os originais do corpus.',confirmText:'Confirmo cadastrar estes documentos e versões no acervo local, com histórico recuperável e sem publicação automática.',effectText:'Cria documentos novos, arquivos originais e traduções de trabalho; atualiza catálogo, manifesto, busca e fila de revisão. Preserva documentos existentes. O histórico do lote permite conferir a reversão.',onSaved:()=>{files=[];}});
  }catch(error){notice.textContent=error.message;}finally{if(env.current())review.disabled=!env.canWrite||loading;}
 }
 stages[2].append(n('h2',{text:'Documentos e versões associados'}),n('p',{class:'hint',text:'Confira o conjunto antes de pedir a prévia. Nela será possível ler cada arquivo e os avisos do backend; gerar a prévia ainda não grava nada.'}),grouping,review);
 if(!env.canWrite){notice.textContent='Cadastro disponível no backend local, na Mesa principal. Você pode organizar arquivos aqui sem gravar.';}
 const receipt=env.saved.lastBackendReceipt;
 if(receipt?.entity?.kind==='batch'){
  const present=(receipt.entity.document_ids||[]).filter(id=>env.catalog.documents.has(id)).length;
  const box=n('section',{class:'corpus-receipt'},[n('strong',{text:'Última operação de corpus'}),n('p',{class:'hint',text:receipt.entity.id+' · registro '+receipt.history_id+' · '+present+'/'+(receipt.entity.document_ids||[]).length+' documentos presentes no catálogo'}),n('p',{class:'hint',text:present?'O cadastro já foi concluído. O histórico é uma consulta opcional; desfazer a importação retira seus documentos do acervo e exige outra confirmação.':'Os documentos deste lote não estão no catálogo. Consulte o histórico para conferir as operações e, se necessário, preparar sua reposição.'}),env.button('Consultar histórico da importação',()=>env.history(receipt.entity.id,'importar'),'quiet')]);
  for(const id of receipt.entity.document_ids||[]){const doc=env.catalog.documents.get(id);if(doc)box.append(env.button('Abrir '+id,()=>env.open(doc),'quiet'));}shell.prepend(box);
 }
 env.controls.append(env.button('Exportar proposta',()=>{const defaults={...work};download('proposta-corpus.json',JSON.stringify({defaults,files},null,2),'application/json');},'quiet'));
 draw();show(work.stage||0);if(work.stage===2)check();
}
