/* Seções de trabalho comuns: os campos permanecem no mesmo formulário/payload. */
window.archiveEditorialTasks={
  sections(parent,definitions){
    const nav=document.createElement('div');nav.className='editorial-section-switch';nav.setAttribute('role','group');nav.setAttribute('aria-label','Etapas da tarefa');
    const panels=[],buttons=[];
    const show=index=>{panels.forEach((panel,i)=>panel.hidden=i!==index);buttons.forEach((button,i)=>button.setAttribute('aria-pressed',String(i===index)));};
    for(const [title,children]of definitions){
      const index=panels.length,section=document.createElement('section');section.className='editorial-edit-section';
      const heading=document.createElement('h2');heading.textContent=title;section.append(heading,...children);panels.push(section);
      const button=document.createElement('button');button.type='button';button.textContent=title;button.onclick=()=>show(index);buttons.push(button);nav.append(button);
    }
    parent.prepend(nav,...panels);show(0);
    parent.addEventListener('invalid',event=>{
      const form=parent.closest('form'),first=form&&[...form.elements].find(input=>input.willValidate&&!input.validity.valid);
      if(first&&first!==event.target)return;
      const index=panels.findIndex(panel=>panel.contains(event.target));if(index>=0)show(index);
    },true);
    return{show};
  },
  upload(input,title){
    const tile=document.createElement('label');tile.className='editorial-upload-tile';
    const heading=document.createElement('strong');heading.textContent=title;
    const info=document.createElement('span');info.className='editorial-upload-selection';info.setAttribute('role','status');
    const update=()=>{const files=[...input.files];info.textContent=files.length?files.map(file=>file.name).join(' · '):'Selecione '+(input.multiple?'os arquivos':'um arquivo')+' para começar';};
    input.addEventListener('change',update);update();tile.append(heading,input,info);return tile;
  }
};
