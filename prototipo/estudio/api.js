export const timings=[];
let sessionPromise;
export async function request(path,{body,signal,timeout=body?120000:15000}={}){
 const started=performance.now(),controller=new AbortController(),abort=()=>controller.abort();
 if(signal?.aborted)throw new DOMException('Cancelado','AbortError');signal?.addEventListener('abort',abort,{once:true});
 const timer=setTimeout(abort,timeout);let status=0;
 try{const headers={};if(body!==undefined){headers['Content-Type']='application/json';headers['X-Editorial-Token']=(await session()).token;}
  const response=await fetch(path,{method:body===undefined?'GET':'POST',headers,body:body===undefined?undefined:JSON.stringify(body),signal:controller.signal,cache:'no-store'});status=response.status;
  const data=await response.json();if(!response.ok)throw Error(data.error||'Pedido recusado ('+status+')');return data;
 }catch(error){if(error.name==='AbortError'&&!signal?.aborted)throw Error(body?'A resposta da gravação demorou. Confira o histórico antes de repetir; seu rascunho permanece guardado.':'A consulta demorou mais de '+Math.round(timeout/1000)+' segundos. Você pode tentar novamente.');throw error;}
 finally{clearTimeout(timer);signal?.removeEventListener('abort',abort);timings.unshift({path,ms:Math.round(performance.now()-started),status});timings.length=Math.min(40,timings.length);window.dispatchEvent(new Event('studio:metrics'));}
}
export function session(){return sessionPromise??=request('/api/editorial/session').catch(error=>{sessionPromise=null;throw error;});}
export async function upload(file,project,onProgress){
 const token=(await session()).token;
 return new Promise((resolve,reject)=>{const xhr=new XMLHttpRequest();xhr.open('POST','/api/editorial/pdf/upload');xhr.timeout=180000;xhr.setRequestHeader('Content-Type','application/pdf');xhr.setRequestHeader('X-Editorial-Token',token);xhr.setRequestHeader('X-PDF-Filename',encodeURIComponent(file.name));xhr.setRequestHeader('X-Research-Project',project||'');xhr.upload.onprogress=event=>{if(event.lengthComputable)onProgress(Math.round(event.loaded/event.total*100));};xhr.onload=()=>{try{const data=JSON.parse(xhr.responseText);if(xhr.status>=400)throw Error(data.error||'Falha no upload');resolve(data);}catch(error){reject(error);}};xhr.onerror=()=>reject(Error('Envio interrompido. O arquivo original permanece no computador.'));xhr.ontimeout=()=>reject(Error('O envio demorou. Confira se a fonte já foi cadastrada antes de reenviar.'));xhr.send(file);});
}
export const node=(tag,attrs={},children=[])=>{const n=document.createElement(tag);for(const[k,v]of Object.entries(attrs))if(k==='text')n.textContent=v;else if(k==='class')n.className=v;else n.setAttribute(k,v);n.append(...children);return n;};
export const button=(label,action,cls='')=>{const b=node('button',{type:'button',text:label,class:cls});b.onclick=()=>Promise.resolve().then(action).catch(error=>window.dispatchEvent(new CustomEvent('studio:error',{detail:error})));return b;};
export const title=doc=>doc.titles?.pt||doc.titles?.ru||doc.title||doc.id;
export function download(name,content){const url=URL.createObjectURL(new Blob([content],{type:name.endsWith('.json')?'application/json;charset=utf-8':'text/markdown;charset=utf-8'})),a=node('a',{href:url,download:name});a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);}
