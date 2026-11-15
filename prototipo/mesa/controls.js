import {node as n,action as b,normalize} from './data.js';
export function menuGroup(title,items){
 return n('section',{class:'action-menu-group'},[n('h3',{text:title}),...items.filter(Boolean).map(itemNode)]);
}
function itemNode(item){
 const button=b('',()=>Promise.resolve().then(item.run).catch(error=>document.dispatchEvent(new CustomEvent('mesa:error',{detail:error}))),'action-menu-item',{disabled:item.disabled||false});
 button.append(n('span',{class:'action-menu-copy'},[n('strong',{text:item.title}),item.description&&n('span',{text:item.description})]),n('span',{class:'action-menu-arrow','aria-hidden':true,text:item.download?'↓':'›'}));return button;
}
export function menuSearch(groups){
 const input=n('input',{type:'search',class:'action-menu-search',placeholder:'Localizar uma ação…','aria-label':'Filtrar ações do menu'});
 input.oninput=()=>{const q=normalize(input.value);for(const group of groups){let visible=0;for(const button of group.querySelectorAll('.action-menu-item')){button.hidden=!normalize(button.textContent).includes(q);if(!button.hidden)visible++;}group.hidden=!visible;}};return input;
}
export function splitRatio(value){const number=Number(value);return Number.isFinite(number)?Math.max(22,Math.min(78,number)):50;}
export function installSplitter(host,state,store=()=>{}){
 const separator=n('div',{class:'workspace-splitter',role:'separator',tabindex:0,'aria-label':'Ajustar espaço da imagem e do texto','aria-valuemin':'22','aria-valuemax':'78'});
 const vertical=()=>window.matchMedia('(max-width:570px)').matches;
 const update=()=>{host.style.setProperty('--split-ratio',splitRatio(state.splitRatio??50)+'%');separator.setAttribute('aria-valuenow',String(Math.round(splitRatio(state.splitRatio??50))));separator.setAttribute('aria-orientation',vertical()?'horizontal':'vertical');};
 host.classList.add('adjustable-workspace');host.insertBefore(separator,host.children[1]);update();let dragging=false;
 separator.onpointerdown=event=>{if(event.button!==0)return;dragging=true;separator.setPointerCapture(event.pointerId);separator.classList.add('dragging');event.preventDefault();};
 separator.onpointermove=event=>{if(!dragging)return;const rect=host.getBoundingClientRect();state.splitRatio=splitRatio(vertical()?(event.clientY-rect.top)/rect.height*100:(event.clientX-rect.left)/rect.width*100);update();};
 const finish=()=>{if(!dragging)return;dragging=false;separator.classList.remove('dragging');store();};separator.onpointerup=finish;separator.onpointercancel=finish;
 separator.onkeydown=event=>{let value=Number(state.splitRatio??50);if(event.key==='Home')value=50;else if(['ArrowLeft','ArrowUp'].includes(event.key))value-=event.shiftKey?10:2;else if(['ArrowRight','ArrowDown'].includes(event.key))value+=event.shiftKey?10:2;else return;event.preventDefault();state.splitRatio=splitRatio(value);update();store();};
 separator.ondblclick=()=>{state.splitRatio=50;update();store();};return separator;
}
export function zoomValue(value){const number=Number(value);return Number.isFinite(number)&&number>0?Math.max(.25,Math.min(3,number)):'fit';}
export function zoomControls(state,refresh,store=()=>{}){
 const select=n('select',{'aria-label':'Zoom da imagem'});
 for(const [value,title]of [['fit','Página inteira'],['width','Ajustar à largura'],[.5,'50%'],[.75,'75%'],[1,'100%'],[1.25,'125%'],[1.5,'150%'],[2,'200%'],[3,'300%']])select.append(n('option',{value,text:title}));
 const sync=()=>{const value=String(state.zoom??'fit');if(![...select.options].some(option=>option.value===value))select.append(n('option',{value,text:Math.round(Number(value)*100)+'%'}));select.value=value;};sync();
 const apply=value=>{state.zoom=value;sync();refresh();store();};select.onchange=()=>apply(['fit','width'].includes(select.value)?select.value:zoomValue(select.value));
 const control=n('div',{class:'pdf-zoom-controls'},[b('−',()=>apply(zoomValue((state.effectiveZoom||Number(state.zoom)||1)/1.2)),'control quiet',{'aria-label':'Diminuir zoom'}),select,b('+',()=>apply(zoomValue((state.effectiveZoom||Number(state.zoom)||1)*1.2)),'control quiet',{'aria-label':'Aumentar zoom'})]);
 return control;
}
