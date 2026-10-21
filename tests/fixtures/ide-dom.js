/* DOM mínimo para testar identidade dos hosts, navegação e estado; não mede layout. */
var window=globalThis,innerWidth=1400,innerHeight=900,handlers={},timers=[],confirmResult=true;
window.addEventListener=(name,fn)=>(handlers[name]??=[]).push(fn);
var confirm=()=>confirmResult,setTimeout=fn=>(timers.push(fn),timers.length),clearTimeout=()=>{},getSelection=()=>({toString:()=>''});
var location={href:'http://localhost:8000/prototipo/ide/'};
class URL {constructor(path,base){this.href=resolveURL(String(path),String(base?.href||base||''));this.pathname=this.href.replace(/^https?:\/\/[^/]+/,'').split(/[?#]/)[0];}static createObjectURL(){return 'blob:fixture';}static revokeObjectURL(){}}
class URLSearchParams{constructor(input={}){this.map=new Map();if(typeof input==='string'){for(const x of input.replace(/^\?/,'').split('&')){if(!x)continue;const [k,v='']=x.split('=');this.map.set(decodeURIComponent(k),decodeURIComponent(v));}}else for(const [k,v]of Object.entries(input))this.map.set(k,String(v));}toString(){return [...this.map].map(([k,v])=>encodeURIComponent(k)+'='+encodeURIComponent(v)).join('&');}}
class Element{
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.parentElement=null;this.attrs={};this.dataset={};this.hidden=false;this.value='';this._text='';this.style={values:{},setProperty(k,v){this.values[k]=v;},removeProperty(k){delete this.values[k];},getPropertyValue(k){return this.values[k]||({'--sidebar-width':'278px','--bottom-height':'154px'}[k]||'');}};this.mounts=0;}
 get className(){return this.attrs.class||'';}set className(v){this.attrs.class=v;}
 get classList(){const e=this;return{contains(x){return e.className.split(/\s+/).includes(x);},toggle(x,on){let xs=e.className.split(/\s+/).filter(Boolean),has=xs.includes(x);if(on===undefined)on=!has;e.className=(on?[...new Set([...xs,x])]:xs.filter(y=>y!==x)).join(' ');return on;},add(x){this.toggle(x,true);},remove(x){this.toggle(x,false);}};}
 setAttribute(k,v){this.attrs[k]=String(v);if(k==='hidden')this.hidden=true;if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,x)=>x.toUpperCase())]=String(v);}
 getAttribute(k){return this.attrs[k]??null;}
 get id(){return this.attrs.id||'';}set id(v){this.attrs.id=v;}
 get textContent(){return this._text+this.children.map(c=>c.textContent).join('');}set textContent(v){this._text=String(v);this.replaceChildren();}
 set innerHTML(v){this._html=v;this.replaceChildren();}get innerHTML(){return this._html||'';}
 get childElementCount(){return this.children.length;}
 get isConnected(){return this===document.body||this===document.documentElement||!!this.parentElement?.isConnected;}
 append(...nodes){for(const n of nodes){if(typeof n==='string')continue;n.remove();n.parentElement=this;n.mounts++;this.children.push(n);}}
 insertBefore(n,reference){const i=this.children.indexOf(reference);n.remove();n.parentElement=this;n.mounts++;this.children.splice(i<0?this.children.length:i,0,n);}
 prepend(...nodes){for(const n of nodes.reverse()){n.remove();n.parentElement=this;n.mounts++;this.children.unshift(n);}}
 remove(){if(this.parentElement){const a=this.parentElement.children;a.splice(a.indexOf(this),1);this.parentElement=null;}}
 replaceChildren(...nodes){for(const n of this.children)n.parentElement=null;this.children=[];this.append(...nodes);}
 replaceWith(n){const p=this.parentElement;if(!p)return;const i=p.children.indexOf(this);n.remove();p.children[i]=n;n.parentElement=p;this.parentElement=null;}
 contains(n){return n===this||this.children.some(x=>x.contains(n));}
 closest(selector){return this.matches(selector)?this:this.parentElement?.closest(selector)||null;}
 matches(selector){if(selector.includes(' '))return false;const attr=selector.match(/\[([^=\]]+)(?:=['"]?([^'"\]]+)['"]?)?\]/);const base=selector.split('[')[0];if(base.startsWith('.')){if(!this.classList.contains(base.slice(1)))return false;}else if(base&&base!==this.tagName.toLowerCase())return false;if(attr){const val=this.getAttribute(attr[1]);if(val===null||attr[2]!==undefined&&val!==attr[2])return false;}return true;}
 querySelectorAll(selector){const all=[];for(const c of this.children){if(selector.split(',').some(s=>c.matches(s.trim())))all.push(c);all.push(...c.querySelectorAll(selector));}return all;}
 querySelector(s){return this.querySelectorAll(s)[0]||null;}
 focus(){document.activeElement=this;}click(){this.onclick?.({preventDefault(){},stopPropagation(){}});}addEventListener(){}scrollIntoView(){}getBoundingClientRect(){return{left:0,top:0,width:800,height:600};}
}
var document={body:new Element('body'),documentElement:new Element('html'),createElement:t=>new Element(t),getElementById:id=>[document.body,...document.body.querySelectorAll('[id]')].find(n=>n.id===id)||null,querySelectorAll:s=>document.body.querySelectorAll(s)};
var getComputedStyle=e=>e.style;
var sessionStorage={data:new Map(),getItem(k){return this.data.get(k)||null;},setItem(k,v){this.data.set(k,String(v));}};
var crypto={randomUUID:()=> 'a-test-draft-token'},Blob=class{};
window.markdownit=()=>({render:s=>s});window.DOMPurify={sanitize:s=>s};
var requests=[];
var fetch=async href=>{requests.push(href);const path=new URL(href).pathname;let data;
 if(path==='/data/manifest.json')data=fixtureManifest;
 else if(path==='/api/editorial/capabilities')data={features:['markdown_edit']};
 else if(path==='/api/editorial/projects')data={items:[{id:'private',title:'Projeto reservado',document_ids:['doc1']}]};
 else if(path==='/api/editorial/workspace/edition')data={content:'Texto privado',has_draft:true};
 else if(path.startsWith('/api/editorial/editions/'))data={content:'Fonte em português',edition:{sha256:'sha-base'}};
 else if(path.startsWith('/originais/'))return{ok:true,text:async()=>path.includes('.pt.')?'Fonte em português':'Русский текст'};
 else return{ok:false,status:404,json:async()=>({})};
 return{ok:true,json:async()=>data};};
if(!Array.prototype.at)Array.prototype.at=function(index){return this[index<0?this.length+index:index];};
