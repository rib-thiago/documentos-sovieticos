import { asset } from './data.js';
let engine;
export async function pdfEngine() {
    if (!engine)
        engine = import('../oficina/vendor/pdf.mjs').then(lib => { lib.GlobalWorkerOptions.workerSrc = asset('prototipo/oficina/vendor/pdf.worker.mjs'); return lib; }).catch(e => { engine = null; throw e; });
    return engine;
}
export async function openPdf(material) {
    if (material.pdf)
        return material.pdf;
    if (!material.pdfPromise)
        material.pdfPromise = pdfEngine().then(async (lib) => {
            const source = material.file ? { data: new Uint8Array(await material.file.arrayBuffer()) } : { url: asset(material.pdfUrl), disableAutoFetch: true, disableStream: true };
            material.loadingTask = lib.getDocument(source);
            const pdf = await material.loadingTask.promise;
            material.pdf = pdf;
            material.count = pdf.numPages;
            return pdf;
        }).catch(e => { material.pdfPromise = null; throw e; });
    return material.pdfPromise;
}
export async function pageText(material, page) {
    const pdf = await openPdf(material), sheet = await pdf.getPage(page), content = await sheet.getTextContent();
    return content.items.map(item => item.str + (item.hasEOL ? '\n' : ' ')).join('').trim();
}
// Mantém a numeração da fonte mesmo quando o PDF do portal contém só um recorte.
export function resolvePdfPage(requested,count,pageMap=null){
 if(pageMap){
  const pages=Object.keys(pageMap).map(Number).filter(n=>Number.isInteger(n)&&n>0).sort((a,b)=>pageMap[a]-pageMap[b]);
  const sourcePage=pages.includes(Number(requested))?Number(requested):pages[0],pdfPage=pageMap[sourcePage];
  if(!Number.isInteger(pdfPage)||pdfPage<1||pdfPage>count)throw Error('Mapa de páginas do fac-símile inválido.');
  return {sourcePage,pdfPage};
 }
 const page=Math.max(1,Math.min(count,Number(requested)||1));return {sourcePage:page,pdfPage:page};
}
export function mountPdf(material, host, onReady, onError) {
    let dead = false, renderTask = null, resizeTimer, serial = 0;
    const canvas = document.createElement('canvas'), info = document.createElement('div');
    info.className = 'pdf-loading';
    info.textContent = 'Abrindo a fonte…';
    host.append(info, canvas);
    async function render() {
        const version = ++serial;
        try {
            const pdf = await openPdf(material);
            if (dead || version !== serial)
                return;
            const selected=resolvePdfPage(material.page,pdf.numPages,material.pageMap);material.page=selected.sourcePage;
            const page = await pdf.getPage(selected.pdfPage);
            if (dead || version !== serial)
                return;
            if (renderTask) {
                renderTask.cancel();
                await renderTask.promise.catch(() => { });
                if (dead || version !== serial)
                    return;
            }
            const base = page.getViewport({ scale: 1 }), available = Math.max(200, host.clientWidth - 36), height = Math.max(220, host.clientHeight - 32);
            const scale = typeof material.zoom==='number'?material.zoom:material.zoom === 'width' ? available / base.width : Math.min(available / base.width, height / base.height);
            const ratio=Math.min(window.devicePixelRatio||1,1.65),effective=Math.max(.1,Math.min(scale,3,Math.sqrt(14000000/(base.width*base.height))/ratio));material.effectiveZoom=effective;const viewport=page.getViewport({scale:effective*ratio});
            canvas.width = Math.ceil(viewport.width);
            canvas.height = Math.ceil(viewport.height);
            canvas.style.width = viewport.width / ratio + 'px';
            canvas.style.height = viewport.height / ratio + 'px';
            renderTask = page.render({ canvasContext: canvas.getContext('2d'), viewport });
            await renderTask.promise;
            if (dead || version !== serial)
                return;
            info.hidden = true;
            canvas.hidden = false;
            onReady?.(pdf.numPages);
        }
        catch (e) {
            if (e.name !== 'RenderingCancelledException' && !dead) {
                info.textContent = 'A fonte não carregou. Tente novamente ou selecione outro PDF.';
                onError?.(e);
            }
        }
    }
    const observer = new ResizeObserver(() => { clearTimeout(resizeTimer); resizeTimer = setTimeout(render, 160); });
    observer.observe(host);
    render();
    const release=() => { dead = true; serial++; observer.disconnect(); clearTimeout(resizeTimer); renderTask?.cancel(); };release.refresh=render;return release;
}
