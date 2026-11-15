import {node as n,asset,label,LANGUAGES} from './data.js';

// Somente registros de incorporação no Git; datas de coleta e datas históricas não viram novidades.
export function activityEntries(activity,catalog){
 const events=(activity.events||[]).filter(event=>event.commit&&Number.isFinite(Date.parse(event.recorded_at))).sort((a,b)=>Date.parse(b.recorded_at)-Date.parse(a.recorded_at)),versions=[],documents=[],seenVersions=new Set(),seenDocuments=new Set();
 for(const event of events){
  for(const item of event.examples||[]){const doc=catalog.documents.get(item.id),languages=(item.languages||[]).filter(code=>code!=='ru'&&doc?.languages?.some(l=>l.code===code));if(doc&&languages.length&&!seenVersions.has(item.id)){seenVersions.add(item.id);versions.push({doc,languages,recordedAt:event.recorded_at,commit:event.commit});}}
  for(const item of event.source_examples||[]){const doc=catalog.documents.get(item.id),languages=(item.languages||[]).filter(code=>doc?.languages?.some(l=>l.code===code));if(doc&&languages.length&&!seenDocuments.has(item.id)){seenDocuments.add(item.id);documents.push({doc,languages,recordedAt:event.recorded_at,commit:event.commit});}}
 }
 return {versions:versions.slice(0,3),documents:documents.filter(item=>!seenVersions.has(item.doc.id)).slice(0,3)};
}
export async function mountHomeActivity(host,catalog,open,{signal}={}){
 try{
  const response=await fetch(asset('assets/acervo-activity.json'),{signal,cache:'no-store'});if(!response.ok)return;const activity=await response.json();if(signal?.aborted||!host.isConnected)return;
  const entries=activityEntries(activity,catalog);if(!entries.versions.length&&!entries.documents.length)return;
  const date=value=>new Intl.DateTimeFormat('pt-BR',{day:'2-digit',month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(value));
  host.append(n('header',{class:'portal-section-heading'},[n('p',{class:'eyebrow',text:'O trabalho de edição'}),n('h2',{text:'Registros de incorporação'})]),n('div',{class:'portal-activity-columns'},[
   ...[['Traduções e versões',entries.versions],['Documentos incorporados',entries.documents]].filter(([,items])=>items.length).map(([title,items])=>n('section',{},[n('h3',{text:title}),...items.map(item=>n('button',{type:'button',class:'portal-activity-item',onclick:()=>open(item.doc,item.languages[0])},[
    n('span',{class:'portal-activity-meta'},[n('span',{text:item.languages.map(code=>LANGUAGES[code]||code).join(' · ')}),n('time',{datetime:item.recordedAt,text:date(item.recordedAt)})]),n('strong',{text:label(item.doc)}),n('span',{class:'portal-activity-id',text:item.doc.id+' · Abrir documento →'})
   ]))]))
  ]),n('p',{class:'portal-activity-note',text:'Recorte do histórico de incorporação ao projeto. Estas datas são dos registros, não dos acontecimentos históricos nem da publicação online.'}));
 }catch(error){if(error.name!=='AbortError'&&host.isConnected)host.textContent='Consulte as coleções para acompanhar os documentos disponíveis no acervo.';}
}
