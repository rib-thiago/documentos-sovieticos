// Relative to this module, also works beneath a GitHub Pages project path.
export const assetURL=path=>new URL('../../'+path,import.meta.url).href;
export const node=(tag,attrs={},children=[])=>{const n=document.createElement(tag);for(const[k,v]of Object.entries(attrs))if(k==='text')n.textContent=v;else if(k==='class')n.className=v;else n.setAttribute(k,v);n.append(...children);return n;};
export const button=(text,fn,cls='')=>{const b=node('button',{type:'button',text,class:cls});b.onclick=()=>Promise.resolve().then(fn).catch(error=>window.dispatchEvent(new CustomEvent('studio:error',{detail:error})));return b;};
const pending=new Map();
export function script(url){if(!pending.has(url))pending.set(url,new Promise((resolve,reject)=>{const s=node('script',{src:url}),timer=setTimeout(()=>{s.remove();pending.delete(url);reject(Error('Não foi possível carregar a ferramenta. Tente novamente.'));},20000);s.onload=()=>{clearTimeout(timer);resolve();};s.onerror=()=>{clearTimeout(timer);pending.delete(url);reject(Error('Recurso indisponível: '+url));};document.head.append(s);}));return pending.get(url);}
let md;
export async function markdown(){if(md)return md;if(!window.markdownit)await script(assetURL('assets/vendor/markdown-it/markdown-it.umd.min.js'));if(!window.markdownitFootnote)await script(assetURL('assets/vendor/markdown-it-footnote/markdown-it-footnote.min.js'));if(!window.DOMPurify)await script(assetURL('assets/vendor/dompurify/purify.min.js'));return md=window.markdownit({html:false,linkify:true}).use(window.markdownitFootnote);}
export function download(name,value,type='text/plain;charset=utf-8'){const url=URL.createObjectURL(new Blob([value],{type})),a=node('a',{href:url,download:name});a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
