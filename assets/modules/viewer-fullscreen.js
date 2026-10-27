// Native fullscreen escapes the IDE chrome. Fallback overlays the viewport.
export function viewerFullscreen(target,{onChange=()=>{}}={}){
 const doc=target.ownerDocument;let overlay=false,placeholder=null,closed=false;
 const active=()=>overlay||!!(doc.fullscreenElement&&(doc.fullscreenElement===target||target.contains(doc.fullscreenElement)));
 const notify=()=>{if(!closed)onChange(active());};
 const exit=doc.createElement('button');exit.type='button';exit.className='viewer-fullscreen-exit';exit.textContent='Sair da tela inteira';exit.hidden=true;target.append(exit);
 function restore(){if(!overlay)return;overlay=false;target.classList.remove('viewer-overlay');if(placeholder?.parentNode)placeholder.replaceWith(target);placeholder=null;doc.body.classList.remove('viewer-overlay-open');exit.hidden=true;notify();}
 function expand(){if(closed||overlay)return;placeholder=doc.createComment('viewer-position');target.before(placeholder);overlay=true;target.classList.add('viewer-overlay');doc.body.classList.add('viewer-overlay-open');doc.body.append(target);exit.hidden=false;notify();}
 async function toggle(){if(closed)return;if(overlay){restore();return;}if(active()){await doc.exitFullscreen?.();return;}try{if(!target.requestFullscreen)throw Error('Fullscreen indisponível');await target.requestFullscreen();}catch{expand();}}
 const changed=()=>{exit.hidden=!active();notify();},escape=event=>{if(event.key==='Escape'&&overlay){event.preventDefault();restore();}};
 exit.onclick=()=>toggle();doc.addEventListener('fullscreenchange',changed);doc.addEventListener('keydown',escape);
 return{toggle,active,dispose(){if(closed)return;restore();if(active())doc.exitFullscreen?.().catch(()=>{});closed=true;doc.removeEventListener('fullscreenchange',changed);doc.removeEventListener('keydown',escape);exit.remove();}};
}
