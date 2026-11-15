// Reutiliza autenticação, revisão e transações da área editorial existente.
export {request as editorialRequest,upload as uploadPdfSource} from '../estudio/api.js';
import {asset} from './data.js';
export async function detectEditorial(){
 if(!['localhost','127.0.0.1','[::1]'].includes(location.hostname))return false;
 try{const response=await fetch(asset('api/editorial/capabilities'),{cache:'no-store',signal:AbortSignal.timeout(4000)});if(!response.ok)return false;const data=await response.json();return data.mode==='local_editorial'&&data.features?.includes('markdown_edit');}catch{return false;}
}
export function markdownPayload(snapshot,body){
 const envelope=globalThis.splitExportHeaders?.(snapshot.content);
 const prefix=envelope?.headers?.join('')||'';
 return {revision:snapshot.revision,edition_id:snapshot.edition.id,content_sha256:snapshot.edition.sha256,content:prefix+body};
}

export function metadataPayload(snapshot,values,memberships){
 return {revision:snapshot.revision,document_id:snapshot.document.id,document:{
  titles:{pt:values.title_pt||'',ru:values.title_ru||'',en:values.title_en||''},
  kind:values.kind,document_type:values.document_type||null,
  author_label:values.author||null,archive_reference:values.archive||null,
  historical_date:{display:values.date_display||null,value:values.date_value||null,precision:values.date_precision||'not_recorded'}
 },collection_ids:[...new Set(memberships)]};
}
export function collectionSlug(title){return String(title).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,100).replace(/-$/,'');}
export function collectionPayload(revision,existing,values){
 return {revision,collection_id:existing?.id||null,slug:existing?.slug||values.slug,parent_id:existing?existing.parent_id:values.parent_id||'',title_pt:values.title_pt||'',title_ru:values.title_ru||'',subtitle:values.subtitle||'',description:values.description||'',cover:values.cover||'',accent:values.accent||'#8b2c2c',source_url:values.source_url||''};
}
