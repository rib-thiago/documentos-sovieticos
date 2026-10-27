import {node} from './api.js';
export const RUSSIAN_ROWS=[
 [['ё','Ё'],['1','!'],['2','"'],['3','№'],['4',';'],['5','%'],['6',':'],['7','?'],['8','*'],['9','('],['0',')'],['-','_'],['=','+']],
 [...'йцукенгшщзхъ'].map(c=>[c,c.toUpperCase()]).concat([['\\','/']]),
 [...'фывапролджэ'].map(c=>[c,c.toUpperCase()]),
 [...'ячсмитьбю'].map(c=>[c,c.toUpperCase()]).concat([['.',',']])
];
export function russianKeyboard({write,erase,locked=()=>false}){
 const keyboard=node('details',{class:'keyboard ru-keyboard'}),summary=node('summary',{text:'Я · Teclado russo'}),layout=node('div',{class:'ru-layout','aria-label':'Teclado russo ЙЦУКЕН'}),letters=[];let uppercase=false;
 const key=(label,run,className='',aria=label)=>{const b=node('button',{type:'button',text:label,class:'ru-key '+className,'aria-label':aria});b.onmousedown=e=>e.preventDefault();b.onclick=()=>{if(!locked())run();};return b;};
 const caps=key('⇪',()=>{}, 'ru-wide','Ativar maiúsculas');caps.setAttribute('aria-pressed','false');caps.onclick=()=>{uppercase=!uppercase;summary.textContent=uppercase?'Я · Teclado russo · MAIÚSCULAS':'Я · Teclado russo';caps.setAttribute('aria-pressed',String(uppercase));caps.setAttribute('aria-label',uppercase?'Desativar maiúsculas':'Ativar maiúsculas');caps.title=uppercase?'Maiúsculas ativadas':'Maiúsculas desativadas';for(const {button,values}of letters){button.textContent=values[uppercase?1:0];button.setAttribute('aria-label','Digitar '+button.textContent);}};caps.title='Ativar maiúsculas';
 RUSSIAN_ROWS.forEach((row,index)=>{const line=node('div',{class:'ru-row ru-row-'+index});if(index===2)line.append(caps);for(const values of row){const b=key(values[0],()=>write(values[uppercase?1:0]),'','Digitar '+values[0]);letters.push({button:b,values});line.append(b);}if(index===0)line.append(key('⌫',erase,'ru-wide','Apagar seleção ou caractere anterior'));if(index===2)line.append(key('↵',()=>write('\n'),'ru-wide','Nova linha'));layout.append(line);});
 const last=node('div',{class:'ru-row ru-row-space'});last.append(key('Espaço',()=>write(' '),'ru-space','Inserir espaço'));layout.append(last);keyboard.append(summary,layout);keyboard.addEventListener('keydown',event=>{if(event.key==='Escape'){keyboard.open=false;event.stopPropagation();}});return keyboard;
}
