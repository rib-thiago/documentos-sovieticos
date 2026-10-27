/* Contrato comum entre a bancada e os fluxos completos existentes. */
export const editorialSections=[
 ['Acervo',[['catalogo','Catálogo e metadados'],['colecoes','Coleções e subcoleções'],['novo-documento','Novo documento'],['nova-colecao','Nova coleção / subcoleção'],['lote','Importar lote']]],
 ['Revisão',[['fila','Fila de revisão'],['historico','Histórico e recuperação']]],
 ['Textos e traduções',[['markdown','Editar versão do acervo'],['importar','Importar tradução ao acervo']]],
 ['Fontes e processamento',[['pdf','Fontes PDF e OCR'],['pdf/ferramentas','Manipular PDF']]],
 ['Projetos',[['projetos','Projetos de pesquisa'],['projetos/novo','Novo projeto']]]
];
export function attachEmbedded(frame,context,callbacks){
 frame.dataset.oficina='true';frame.dataset.context=JSON.stringify(context);
 let closed=false;const receive=event=>{if(event.origin!==location.origin||event.source!==frame.contentWindow||!event.data?.oficina)return;callbacks(event.data,frame);};window.addEventListener('message',receive);
 frame.onload=()=>{if(closed)return;try{const doc=frame.contentDocument;if(!doc||doc.querySelector('[data-oficina-bridge]'))return;const script=doc.createElement('script');script.type='module';script.src=new URL('embedded.js?v=3',import.meta.url).href;script.dataset.oficinaBridge='true';doc.head.append(script);}catch(e){callbacks({type:'error',message:e.message},frame);}};
 return()=>{closed=true;window.removeEventListener('message',receive);frame.onload=null;};
}
export function canCloseFrame(frame){try{return frame?.contentWindow?.oficinaEmbedded?.canClose()!==false;}catch{return false;}}
export function readerRoute(context){const params=new URLSearchParams(context.readerHash?.split('?')[1]||'');params.set('bancada','1');params.set('idioma',context.lang||'pt');params.delete('projeto');if(context.collection)params.set('colecao',context.collection);if(context.subcollection)params.set('subcolecao',context.subcollection);if(context.project)params.set('projeto',context.project);return '#/doc/'+encodeURIComponent(context.id)+'?'+params;}
export function editorialRoute(route,context){const [path,raw='']=route.split('?'),params=new URLSearchParams(raw);params.delete('leitor');
 // Catálogo e metadados são canônicos. Fontes/tarefas recebem o contexto explicitamente.
 if(context.project&&/^pdf(?:\/|$)/.test(path))params.set('projeto',context.project);
 else if(/^pdf(?:\/|$)/.test(path)){params.delete('projeto');params.set('todos','1');}
 return path+(params.size?'?'+params:'');
}
export function scopeKey(p){return [p.project||'acervo',p.id,p.lang].join('|');}
