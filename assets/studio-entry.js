/* Local editing links keep their document/project context; public reading stays put. */
(()=>{
 if(!['127.0.0.1','localhost','[::1]'].includes(location.hostname))return;
 const route=()=>{const [path,raw='']=location.hash.split('?'),params=new URLSearchParams(raw);if(path==='#/bancada'||path.startsWith('#/doc/')&&(params.get('bancada')==='1'||params.has('projeto')))location.replace('/estudio/'+location.hash);};
 window.addEventListener('hashchange',route);route();
})();
