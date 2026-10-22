/* ZIP sem dependências: arquivos armazenados sem compressão, nomes UTF-8. */
function collectionZipControl(collection, subcollection) {
  const control=el('div',{class:'collection-download'});
  const button=el('button',{type:'button',class:'panel-button',text:'↓ Baixar '+(subcollection?'subcoleção':'coleção')+' · ZIP'});
  const status=el('span',{role:'status','aria-live':'polite'});
  let busy=false;
  button.addEventListener('click',async()=>{
    if(busy)return;busy=true;button.disabled=true;
    const all=collectionDocuments(collection);
    const ids=subcollection?new Set(subcollection.document_ids):null;
    const documents=all.filter(doc=>!ids||ids.has(doc.id));
    const files=[],encoder=new TextEncoder();
    const count=documents.reduce((n,d)=>n+d.languages.length,0);let done=0;
    try{
      for(const doc of documents)for(const language of doc.languages){
        status.textContent=`Preparando ${++done} de ${count} versões…`;
        const source=await fetchText(language.file);
        files.push({name:doc.id+'/'+markdownFilename(doc,language),data:encoder.encode(documentMarkdown(doc,{...language,source}))});
      }
      files.push({name:'manifesto.json',data:encoder.encode(JSON.stringify({collection,subcollection:subcollection||null,documents},null,2))});
      files.push({name:'LEIA-ME.txt',data:encoder.encode('Documentos Soviéticos\nExportação do acervo local disponível neste site. Todas as versões linguísticas estão organizadas por ID. Consulte manifesto.json para metadados e proveniência. Os arquivos são exportações Markdown; não incluem PDFs nem imagens externas.\n')});
      const blob=archiveStoredZip(files),url=URL.createObjectURL(blob);
      const link=el('a',{href:url,download:(subcollection?collection.id+'--'+subcollection.id:collection.id)+'.zip'});
      document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
      status.textContent=`ZIP preparado: ${documents.length} documentos, ${count} versões.`;
    }catch(error){status.textContent='Não foi possível concluir o ZIP. Nenhum pacote parcial foi baixado. '+error.message;}
    finally{busy=false;button.disabled=false;}
  });
  control.append(button,status);return control;
}
function archiveStoredZip(files){
  if(files.length>65535)throw new Error('Quantidade de arquivos excede o limite ZIP. Baixe por subcoleção.');
  const table=new Uint32Array(256);
  for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xedb88320^(c>>>1):c>>>1;table[n]=c>>>0;}
  const crc=data=>{let c=0xffffffff;for(const byte of data)c=table[(c^byte)&255]^(c>>>8);return(c^0xffffffff)>>>0;};
  const header=size=>{const bytes=new Uint8Array(size);return {bytes,view:new DataView(bytes.buffer)};};
  const parts=[],central=[];let offset=0,centralSize=0;
  for(const file of files){
    const name=new TextEncoder().encode(file.name),size=file.data.length,checksum=crc(file.data);
    if(offset+size+name.length+30>0xffffffff)throw new Error('Pacote excede 4 GB. Baixe por subcoleção.');
    const h=header(30);h.view.setUint32(0,0x04034b50,true);h.view.setUint16(4,20,true);h.view.setUint16(6,0x800,true);h.view.setUint16(12,33,true);h.view.setUint32(14,checksum,true);h.view.setUint32(18,size,true);h.view.setUint32(22,size,true);h.view.setUint16(26,name.length,true);
    parts.push(h.bytes,name,file.data);
    const c=header(46);c.view.setUint32(0,0x02014b50,true);c.view.setUint16(4,20,true);c.view.setUint16(6,20,true);c.view.setUint16(8,0x800,true);c.view.setUint16(14,33,true);c.view.setUint32(16,checksum,true);c.view.setUint32(20,size,true);c.view.setUint32(24,size,true);c.view.setUint16(28,name.length,true);c.view.setUint32(42,offset,true);
    central.push(c.bytes,name);centralSize+=46+name.length;offset+=30+name.length+size;
  }
  const end=header(22);end.view.setUint32(0,0x06054b50,true);end.view.setUint16(8,files.length,true);end.view.setUint16(10,files.length,true);end.view.setUint32(12,centralSize,true);end.view.setUint32(16,offset,true);
  return new Blob([...parts,...central,end.bytes],{type:'application/zip'});
}
