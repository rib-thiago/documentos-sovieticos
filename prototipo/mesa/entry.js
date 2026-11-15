/* Compatibilidade de URLs; caminhos relativos à raiz do repositório no GitHub Pages. */
export function entryRoute(hash='',search=''){
 const local=new URLSearchParams(search).get('ambiente')==='local';
 if(!hash||hash==='#'||hash==='#/'){const params=new URLSearchParams(search);if(local&&params.get('documento'))return {kind:'document',id:params.get('documento'),language:params.get('idioma')||'',project:params.get('projeto')||'',mode:params.get('editar')==='1'?'edit':'read'};return local?{kind:'task',route:'mesa'}:null;}
 const [raw,query='']=hash.replace(/^#\/?/,'').split('?'),p=new URLSearchParams(query);
 const decode=value=>decodeURIComponent(value||'');
 const parts=raw.split('/'),head=parts[0],language=p.get('idioma')||p.get('lang')||'',project=p.get('projeto')||'';
 const mode=({leitura:'read',estudo:'paragraphs',paragrafo:'paragraphs',paralelo:'parallel',pdf:'facsimile'})[p.get('modo')]||p.get('atividade')||'read';
 const document=(id,activity=mode)=>({kind:'document',id:decode(id),language,project,mode:p.get('editar')==='1'?'edit':activity});
 if(head==='mesa'&&p.get('documento'))return document(p.get('documento'));
 if(head==='mesa'&&p.get('fonte'))return {kind:'source',id:p.get('fonte'),page:Number(p.get('pagina'))||1,project};
 if(head==='doc'&&parts[1])return document(parts.slice(1).join('/'));
 if(head==='estudo')return parts[1]?document(parts.slice(1).join('/'),p.get('modo')?mode:'paragraphs'):{kind:'task',route:'mesa'};
 if(head==='bancada')return {kind:'task',route:project?'projetos/'+encodeURIComponent(project):'mesa'};
 if(head==='colecao'&&parts[1])return {kind:'library',collection:decode(parts[1]),sub:parts[2]==='subcolecao'?decode(parts.slice(3).join('/')):'',page:Math.max(1,Number(p.get('pagina'))||1)};
 if(head==='busca')return {kind:'search',q:p.get('q')||'',collection:p.get('colecao')||p.get('collection')||'',language,scope:p.get('escopo')==='conteudo'?'text':'catalog'};
 if(head==='documento'&&parts[1])return {kind:'task',route:'catalogo/'+encodeURIComponent(decode(parts.slice(1).join('/')))};
 if(head==='markdown'){
  const edition=decode(parts.slice(1).join('/')),index=edition.lastIndexOf(':'),result=document(index>=0?edition.slice(0,index):edition||p.get('documento'),'edit');
  if(index>=0)result.language=edition.slice(index+1);return result.id?result:{kind:'task',route:'catalogo'};
 }
 if(head==='importar'&&p.get('documento'))return document(p.get('documento'),'import-translation');
 if(head==='pdf')return parts[1]?.startsWith('pdf-')?{kind:'source',id:parts[1],page:Number(p.get('pagina'))||1,project}:{kind:'task',route:'fontes'};
 if(hash.startsWith('#/')){
  const names={'catalogo':'catalogo','fila':'fila','colecoes':local?'colecoes':'biblioteca','projetos':'projetos','lote':'importar','novo-documento':'importar','importar':'importar','historico':'catalogo','sobre':'biblioteca'};
  if(names[head])return {kind:'task',route:names[head]+(parts.length>1?'/'+parts.slice(1).join('/'):'')};
 }
 return null;
}
export function materialURL(material){
 const params=new URLSearchParams();
 if(material.kind==='document'){params.set('documento',material.doc.id);params.set('idioma',material.lang);params.set('atividade',material.mode||'read');}
 else if(material.backendSource){params.set('fonte',material.backendSource);params.set('pagina',String(material.page||1));}
 else return '#mesa';
 if(material.projectId)params.set('projeto',material.projectId);
 return '#mesa?'+params;
}
