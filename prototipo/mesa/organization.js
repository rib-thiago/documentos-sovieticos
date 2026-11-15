import {node as n,action as b,label,normalize,asset} from './data.js';
import {editorialRequest as api,metadataPayload,collectionPayload,collectionSlug} from './editorial.js';
const title=entry=>entry.titles?.pt||entry.titles?.ru||entry.id;
function sectionTabs(groups){
 const host=n('div',{class:'organization-sections'}),bar=n('div',{class:'organization-tabs',role:'tablist'});host.append(bar);
 for(const [index,[name,body]]of groups.entries()){
  const button=b(name,()=>{for(const node of bar.children){node.classList.toggle('active',node===button);node.setAttribute('aria-selected',String(node===button));}groups.forEach(([,panel])=>panel.hidden=panel!==body);},'organization-tab'+(!index?' active':''),{role:'tab','aria-selected':String(!index)});
  body.hidden=index!==0;bar.append(button);host.append(body);
 }return host;
}
function inputField(env,values,key,caption,parent,{multiline=false,choices=null,readonly=false}={}){
 const input=choices?env.select(choices,values[key]??'',()=>{},caption):n(multiline?'textarea':'input',{'aria-label':caption,type:multiline?undefined:'text',rows:multiline?5:undefined});input.value=values[key]??'';input.readOnly=readonly;
 if(choices&&readonly)input.disabled=true;
 input.addEventListener('input',()=>{values[key]=input.value;env.store();});
 if(choices)input.addEventListener('change',()=>{values[key]=input.value;env.store();});
 parent.append(n('label',{class:'organization-field'},[n('span',{text:caption}),input]));return input;
}
function valueText(value){if(value===null||value===undefined||value==='')return '—';if(Array.isArray(value))return value.join('\n');if(typeof value==='object')return Object.entries(value).map(([k,v])=>`${k}: ${v??'—'}`).join('\n');return String(value);}
function labelsFromTree(tree){const map=new Map();for(const root of tree){map.set(root.id,title(root));for(const sub of root.children||[])map.set(sub.id,title(root)+' › '+title(sub));}return map;}
function propertyRows(result,tree=[]){
 const names=labelsFromTree(tree),fields={titles:'Títulos',historical_date:'Data histórica',author_label:'Autoria',archive_reference:'Referência arquivística',kind:'Categoria',document_type:'Tipo documental','Coleções/subcoleções':'Coleções e subcoleções'};
 return result.changes.map(change=>({field:fields[change.field]||change.field,before:valueText(change.field==='Coleções/subcoleções'?change.before.map(id=>names.get(id)||id):change.before),after:valueText(change.field==='Coleções/subcoleções'?change.after.map(id=>names.get(id)||id):change.after)}));
}
export async function mountCatalog(env,id){
 const {content,controls,button}=env;
 const shell=n('section',{class:'organization-page'},[env.heading('Organizar o acervo','Catálogo','Selecione um documento, ajuste sua ficha e confira o destino antes de confirmar.')]),list=n('section',{class:'organization-browser'}),sheet=n('section',{class:'organization-sheet'}),search=n('input',{type:'search',placeholder:'Título ou identificação…','aria-label':'Pesquisar documentos no catálogo'}),results=n('div'),pager=n('div',{class:'pagination'});let page=0,chosen=0;
 list.append(search,results,pager);shell.append(n('div',{class:'organization-grid'},[list,sheet]));content.append(shell);
 controls.append(button('Coleções e subcoleções',()=>env.navigate('colecoes'),'quiet'));
 const [response,vocabulary]=await Promise.all([api('/api/collections'),api('/api/vocabularies')]);if(!env.current())return;const tree=response.items;
 async function edit(doc){
  const token=++chosen;sheet.replaceChildren(n('p',{class:'hint',text:'Carregando a ficha…'}));
  try{
   const snapshot=await api('/api/editorial/documents/'+encodeURIComponent(doc.id));if(!env.current()||token!==chosen)return;
   const canonical=snapshot.document,workKey='document:'+doc.id;
   const initial={title_pt:canonical.titles.pt||'',title_ru:canonical.titles.ru||'',title_en:canonical.titles.en||'',kind:canonical.kind,document_type:canonical.document_type||'',author:canonical.author_label||'',archive:canonical.archive_reference||'',date_display:canonical.historical_date.display||'',date_value:canonical.historical_date.value||'',date_precision:canonical.historical_date.precision,memberships:[...snapshot.collection_ids]};
   env.saved.organizationImported||={};
   const legacy=!env.saved.organizationImported[doc.id]&&env.saved.metadata[doc.id];
   if(legacy&&Object.keys(legacy).length&&!env.work[workKey]){
     const migrated={...initial};for(const [oldKey,newKey]of [['title_pt','title_pt'],['date','date_display'],['author','author'],['archive','archive']])if(Object.hasOwn(legacy,oldKey))migrated[newKey]=legacy[oldKey]||'';
     env.work[workKey]=migrated;env.saved.organizationImported[doc.id]=true;env.store();
   }
   const recovered=Boolean(env.work[workKey]);const values=env.work[workKey]||={...initial};
   sheet.replaceChildren(n('header',{class:'organization-sheet-heading'},[n('h2',{text:label(doc)}),n('p',{class:'hint',text:doc.id+' · '+(recovered?'Preenchimento recuperado da sessão; ainda não gravado.':'Textos, idiomas, fonte e URLs preservados.')})]));
   const identity=n('div',{class:'organization-field-grid'}),date=n('div',{class:'organization-field-grid'}),members=n('div',{class:'membership-browser'});
   for(const [key,name]of [['title_pt','Título em português'],['title_ru','Título em russo'],['title_en','Título em inglês'],['author','Autoria']])inputField(env,values,key,name,identity);
   inputField(env,values,'kind','Categoria',identity,{choices:Object.entries(vocabulary.kinds)});inputField(env,values,'document_type','Tipo documental',identity,{choices:[['','Não informado'],...Object.entries(vocabulary.document_types)]});
   inputField(env,values,'date_display','Data histórica para exibição',date);inputField(env,values,'date_value','Data normalizada (AAAA, AAAA-MM ou AAAA-MM-DD)',date);inputField(env,values,'date_precision','Precisão da data',date,{choices:[['not_recorded','Não registrada'],['year','Ano'],['month','Mês'],['day','Dia']]});inputField(env,values,'archive','Referência arquivística',date,{multiline:true});
   date.append(n('p',{class:'hint',text:'A data de coleta não é usada como data histórica. Sem data normalizada, escolha Não registrada; o texto de exibição pode permanecer.'}));
   const checks=new Map(),selected=new Set(values.memberships||snapshot.collection_ids);
   const remember=()=>{values.memberships=[...checks].filter(([,input])=>input.checked).map(([key])=>key);env.store();};
   for(const root of tree){const group=n('div',{class:'membership-group'}),parent=n('input',{type:'checkbox',checked:selected.has(root.id)});checks.set(root.id,parent);group.append(n('label',{},[parent,n('strong',{text:title(root)})]));
    const children=[];for(const sub of root.children||[]){const input=n('input',{type:'checkbox',checked:selected.has(sub.id)});checks.set(sub.id,input);children.push(input);group.append(n('label',{class:'membership-child'},[input,n('span',{text:title(sub)})]));input.onchange=()=>{if(input.checked)parent.checked=true;remember();};}
    parent.onchange=()=>{if(!parent.checked)children.forEach(input=>input.checked=false);remember();};members.append(group);
   }
   members.prepend(n('p',{class:'hint',text:'O documento pode pertencer a várias coleções. Marcar uma subcoleção inclui a principal; retirar a principal também retira suas subcoleções.'}));
   sheet.append(sectionTabs([['Ficha',identity],['Data e referência',date],['Coleções',members]]));
   const prepare=button('Conferir alterações',async()=>{
    remember();const copied=JSON.parse(JSON.stringify(values)),payload=metadataPayload(snapshot,copied,copied.memberships);
    if(!payload.collection_ids.length){env.toast('Selecione pelo menos uma coleção.');return;}
    const session={title:'Conferir ficha · '+doc.id,before:valueText(initial),after:valueText(copied),propertyRows:[],confirm:()=>{env.saved.metadata[doc.id]={title_pt:copied.title_pt,date:copied.date_display,author:copied.author,archive:copied.archive};env.store();env.navigate('catalogo/'+doc.id);env.toast('Ficha guardada apenas como rascunho da sessão.');}};
    if(env.canWrite){const destination={session,prepare:async()=>{const token=env.generation();const result=await api('/api/editorial/preview',{body:payload});if(token!==env.generation())return;env.review(result,{title:'Conferir ficha · '+doc.id,returnRoute:'catalogo/'+doc.id,workKey,propertyRows:propertyRows(result,tree),destination});}};session.destination=destination;}
    const captions={title_pt:'Título em português',title_ru:'Título em russo',title_en:'Título em inglês',kind:'Categoria',document_type:'Tipo documental',author:'Autoria',archive:'Referência arquivística',date_display:'Data de exibição',date_value:'Data normalizada',date_precision:'Precisão da data',memberships:'Coleções e subcoleções'},names=labelsFromTree(tree);
    const display=(key,value)=>valueText(key==='memberships'?value.map(id=>names.get(id)||id):key==='kind'?vocabulary.kinds[value]||value:key==='document_type'?vocabulary.document_types[value]||value:value);
    session.propertyRows=Object.keys(copied).filter(k=>JSON.stringify(initial[k])!==JSON.stringify(copied[k])).map(k=>({field:captions[k]||k,before:display(k,initial[k]),after:display(k,copied[k])}));if(!session.propertyRows.length){env.toast('Nenhuma alteração na ficha para conferir.');return;}
    env.preview(session);
   },'primary');
   sheet.append(n('footer',{class:'organization-actions'},[recovered&&button('Usar ficha do acervo',()=>{if(confirm('Descartar o preenchimento em andamento desta ficha e carregar os metadados do acervo?')){delete env.work[workKey];env.store();edit(doc);}},'quiet'),button('Voltar à leitura',()=>env.open(doc),'quiet'),button('Histórico do documento',()=>env.history(doc.id,'catalogo/'+doc.id),'quiet'),prepare]));
  }catch(error){if(env.current()&&token===chosen)sheet.replaceChildren(n('p',{text:error.message}),button('Tentar novamente',()=>edit(doc),'quiet'));}
 }
 function draw(){const docs=env.catalog.all.filter(d=>normalize(label(d)+' '+d.id).includes(normalize(search.value)));const max=Math.max(0,Math.ceil(docs.length/20)-1);page=Math.min(page,max);results.replaceChildren(...docs.slice(page*20,page*20+20).map(doc=>b(label(doc),()=>edit(doc),'organization-list-entry')));pager.replaceChildren(button('←',()=>{page--;draw();},'quiet'),n('span',{text:`${page+1} / ${max+1} · ${docs.length}`}),button('→',()=>{page++;draw();},'quiet'));pager.firstChild.disabled=page===0;pager.lastChild.disabled=page>=max;}
 search.oninput=()=>{page=0;draw();};draw();await edit(env.catalog.documents.get(id)||env.catalog.all[0]);
}
export async function mountCollections(env,route){
 const {content,controls,button}=env,parts=route.split('?'),params=new URLSearchParams(parts[1]||'');
 const response=await api('/api/collections');if(!env.current())return;const tree=response.items;
 controls.append(button('Catálogo',()=>env.navigate('catalogo'),'quiet'),button('Nova coleção',()=>env.navigate('colecoes/nova'),'primary'));
 const editId=parts[0].startsWith('colecoes/editar/')?decodeURIComponent(parts[0].slice('colecoes/editar/'.length)):null;
 if(editId||parts[0]==='colecoes/nova'){
  const snapshot=editId?await api('/api/editorial/collections/'+encodeURIComponent(editId)):await api('/api/editorial/session');if(!env.current())return;const existing=snapshot.collection,workKey='collection:'+(editId||'nova:'+(params.get('pai')||''));
  const values=env.work[workKey]||={title_pt:existing?.titles.pt||'',title_ru:existing?.titles.ru||'',slug:existing?.slug||'',parent_id:existing?.parent_id||params.get('pai')||'',subtitle:existing?.subtitle||'',description:existing?.description||'',source_url:existing?.source.url||'',cover:existing?.presentation.cover||'',accent:existing?.presentation.accent||'#8b2c2c'};
  const shell=n('section',{class:'organization-page collection-editor'},[env.heading('Coleções e subcoleções',existing?'Editar '+title(existing):values.parent_id?'Nova subcoleção':'Nova coleção','Identificadores existentes são fixos para preservar as URLs. Preparar a prévia não grava.')]);
  const identity=n('div',{class:'organization-field-grid'}),description=n('div',{class:'organization-field-grid'});
  const name=inputField(env,values,'title_pt','Título em português',identity),slug=inputField(env,values,'slug','Identificador da URL',identity,{readonly:Boolean(existing)});let custom=Boolean(values.slug);
  slug.addEventListener('input',()=>custom=true);name.addEventListener('input',()=>{if(!existing&&!custom){values.slug=collectionSlug(name.value);slug.value=values.slug;}});
  inputField(env,values,'parent_id','Coleção principal',identity,{choices:[['','Nenhuma · coleção principal'],...tree.map(root=>[root.id,title(root)])],readonly:Boolean(existing)});
  inputField(env,values,'title_ru','Título em russo',identity);inputField(env,values,'subtitle','Subtítulo',identity);
  inputField(env,values,'description','Apresentação da coleção',description,{multiline:true});inputField(env,values,'source_url','URL da fonte',description);inputField(env,values,'cover','Capa existente em assets/covers/ (opcional)',description);inputField(env,values,'accent','Cor de destaque (por exemplo #8b2c2c)',description);
  description.append(n('p',{class:'hint',text:'A capa deve existir em assets/covers/. Deixar sem capa é permitido. Esta etapa não envia imagens.'}));
  shell.append(sectionTabs([['Identidade',identity],['Apresentação e fonte',description]]));
  const prepare=button('Conferir alterações',async()=>{try{const payload=collectionPayload(snapshot.revision,existing,values);if(!payload.title_pt||!payload.slug){env.toast('Preencha o título em português e o identificador.');return;}prepare.disabled=true;const token=env.generation();const result=await api('/api/editorial/collections/preview',{body:payload});if(token!==env.generation())return;const before=result.changes[0].before,after=result.changes[0].after;
   const rows=[['Título em português',before?.titles.pt,after.titles.pt],['Título em russo',before?.titles.ru,after.titles.ru],['Identificador',before?.slug,after.slug],['Coleção principal',before?.parent_id,after.parent_id],['Subtítulo',before?.subtitle,after.subtitle],['Apresentação',before?.description,after.description],['Fonte',before?.source.url,after.source.url],['Capa',before?.presentation.cover,after.presentation.cover],['Cor',before?.presentation.accent,after.presentation.accent]].filter(([,a,b])=>a!==b).map(([field,before,after])=>({field,before:valueText(before),after:valueText(after)}));
   env.review(result,{title:existing?'Conferir edição de coleção':'Conferir nova '+(after.parent_id?'subcoleção':'coleção'),returnRoute:'colecoes/editar/'+encodeURIComponent(result.entity.id),workKey,propertyRows:rows});
  }catch(error){env.toast(error.message);}finally{prepare.disabled=false;}},'primary');prepare.disabled=!env.canWrite;
  shell.append(n('footer',{class:'organization-actions'},[button('Voltar às coleções',()=>env.navigate('colecoes'),'quiet'),existing&&button('Histórico da coleção',()=>env.history(existing.id,'colecoes/editar/'+encodeURIComponent(existing.id)),'quiet'),prepare]));if(!env.canWrite)shell.append(n('p',{class:'hint',text:'Para gravar uma coleção, escolha Mesa principal com backend local. O preenchimento permanece na sessão.'}));content.append(shell);return;
 }
 const shell=n('section',{class:'organization-page'},[env.heading('Organizar o acervo','Coleções e subcoleções','Escolha uma coleção para editar sua apresentação ou acrescente uma subcoleção.')]),search=n('input',{type:'search','aria-label':'Buscar coleção ou subcoleção',placeholder:'Localizar coleção…',class:'organization-search'}),list=n('div',{class:'collection-management'});shell.append(search,list);content.append(shell);
 function draw(){list.replaceChildren();for(const root of tree){const q=normalize(search.value),children=(root.children||[]).filter(child=>normalize(title(child)).includes(q));if(q&&!normalize(title(root)).includes(q)&&!children.length)continue;
  list.append(n('section',{class:'collection-management-card'},[n('div',{class:'collection-management-heading'},[n('h2',{text:title(root)}),n('div',{},[button('Editar',()=>env.navigate('colecoes/editar/'+encodeURIComponent(root.id)),'quiet'),button('Nova subcoleção',()=>env.navigate('colecoes/nova?pai='+encodeURIComponent(root.id)),'quiet')])]),...(q&&!normalize(title(root)).includes(q)?children:root.children||[]).map(sub=>n('div',{class:'collection-management-child'},[n('span',{text:title(sub)}),button('Editar',()=>env.navigate('colecoes/editar/'+encodeURIComponent(sub.id)),'quiet')]))]));
 }}search.oninput=draw;draw();
}
