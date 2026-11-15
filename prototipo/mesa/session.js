import {projectDocumentKey} from './projects.js';
// Só descreve a mesa. Arquivos PDF e objetos das bibliotecas nunca são serializados.
export function snapshotDesk(materials, active, library) {
    return {
        version: 1, active, library: {...library},
        materials: materials.map(m => ({
            key:m.key, kind:m.kind, documentId:m.doc?.id,projectId:m.projectId,projectTitle:m.project?.title||m.projectTitle,projectBases:m.projectBases,
            lang:m.lang, otherLang:m.otherLang, mode:m.mode,facsimileReturnMode:m.facsimileReturnMode,
            scroll:m.scroll, position:m.position, buffers:m.buffers, expandedUnits:m.expandedUnits,noteSelection:m.noteSelection,findState:m.findState,returnMode:m.returnMode,showCanonical:m.showCanonical,facsimile:m.facsimile?{source:m.facsimile.source,page:m.facsimile.page,zoom:m.facsimile.zoom,splitRatio:m.facsimile.splitRatio}:undefined,translationWork:m.translationWork,passageWork:m.passageWork,lastPassageReceipt:m.lastPassageReceipt,
            title:m.title, pdfUrl:m.pdfUrl, page:m.page,
            scopeNote:m.scopeNote, pageUnsaved:m.pageUnsaved,
            keyboardOpen:m.keyboardOpen, zoom:m.zoom,splitRatio:m.splitRatio,
            backendSource:m.backendSource,associationReturn:m.associationReturn,backendDrafts:m.backendDrafts,backendRecoveries:m.backendRecoveries,incorporationWork:m.incorporationWork,pendingIncorporation:m.pendingIncorporation,imagePreparation:m.imagePreparation,showPreparedImage:m.showPreparedImage,pdfPartsWork:m.pdfPartsWork,lastPdfOperation:m.lastPdfOperation,linkWork:m.linkWork,lastPublicationReceipt:m.lastPublicationReceipt,filename:m.file?.name || m.filename, filesize:m.file?.size ?? m.filesize
        }))
    };
}
export function restoreDesk(snapshot, catalog) {
    const materials=[], seen=new Set();
    if(snapshot?.version!==1||!Array.isArray(snapshot.materials))return {materials,active:undefined,library:{}};
    for(const entry of (snapshot.materials||[]).slice(0,40)){
        if(!entry||seen.has(entry.key))continue;
        let material;
        if(entry.kind==='document'){
            const doc=catalog.documents.get(entry.documentId);
            if(!doc)continue;
            const languages=doc.languages||[];
            const projectId=typeof entry.projectId==='string'&&/^project-[a-f0-9]{32}$/.test(entry.projectId)?entry.projectId:undefined;
            material={...entry,key:projectDocumentKey(doc.id,projectId),projectId,project:projectId?{id:projectId,title:entry.projectTitle||'Projeto local'}:null,doc,lang:(projectId&&['ru','pt','en'].includes(entry.lang))||languages.some(l=>l.code===entry.lang)?entry.lang:languages[0]?.code,
                mode:['read','paragraphs','parallel','edit','facsimile','import-translation','correct-passage'].includes(entry.mode)?entry.mode:'read'};
        }else if(entry.kind==='pdf'){
            const link=entry.pdfUrl && catalog.links.find(l=>l.pdf_url===entry.pdfUrl);
            const backend=typeof entry.backendSource==='string'&&/^pdf-[a-f0-9]{32}$/.test(entry.backendSource);if(!link&&!entry.filename&&!backend)continue;
            const projectId=typeof entry.projectId==='string'&&/^project-[a-f0-9]{32}$/.test(entry.projectId)?entry.projectId:undefined;
            material={...entry,projectId,project:projectId?{id:projectId,title:entry.projectTitle||'Projeto local'}:null,pdfUrl:link?.pdf_url,count:0,needsFile:!link&&!backend,page:Math.max(1,Number(entry.page)||1)};
        }else continue;
        if(seen.has(material.key))continue;seen.add(material.key);materials.push(material);
    }
    const library=Object.fromEntries(['q','collection','sub','language','scope'].map(key=>[key,typeof snapshot.library?.[key]==='string'?snapshot.library[key]:'']));
    library.view=['home','collection','search'].includes(snapshot.library?.view)?snapshot.library.view:library.collection?'collection':library.q||library.language?'search':'home';
    library.scope=library.scope==='text'?'text':'catalog';library.language=['pt','ru','en'].includes(library.language)?library.language:'';library.offset=Number.isInteger(snapshot.library?.offset)&&snapshot.library.offset>=0?snapshot.library.offset:0;
    const collection=catalog.collections?.find(c=>c.id===library.collection);
    if(!collection){library.collection='';library.sub='';}else if(!(collection.subcollections||[]).some(s=>s.id===library.sub))library.sub='';
    return {materials,active:materials.some(m=>m.key===snapshot.active)?snapshot.active:materials[0]?.key,library};
}
export function pendingCount(material) {
    return (material.passageWork&&material.passageWork.replacement!==material.passageWork.expected?1:0)+Object.keys(material.buffers||{}).length+Object.keys(material.pageUnsaved||{}).length+Object.keys(material.backendDrafts||{}).length;
}
