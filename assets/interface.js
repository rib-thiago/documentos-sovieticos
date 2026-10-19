/* Preserve o roteamento por hash ao saltar diretamente para o conteúdo. */
document.addEventListener("click", event => {
  const link = event.target.closest?.(".skip-link");
  if (!link) return;
  const target = document.getElementById(link.getAttribute("href").slice(1));
  if (!target) return;
  event.preventDefault();
  target.focus({preventScroll:true});
  target.scrollIntoView({block:"start",behavior:"instant"});
});

/* Ícones funcionais locais; o nome acessível permanece no botão ou link. */
function archiveIcon(name) {
  const paths = {
    read:'M4 4h6l2 2 2-2h6v15h-6l-2 2-2-2H4z M12 6v15',
    compass:'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18 M16 8l-2 6-6 2 2-6z',
    edit:'M14 5l5 5 M4 20l4-1L20 7l-5-5L3 14z',
    download:'M12 3v12 M7 10l5 5 5-5 M4 16v5h16v-5',
    language:'M3 5h12 M9 3v2 M5 5c0 6 7 10 7 10 M13 5c0 6-7 10-7 10 M14 21l4-10 4 10 M16 17h4',
    catalog:'M5 3h14v18H5z M8 7h8 M8 11h8 M8 15h5',
    plus:'M12 4v16 M4 12h16',
    chevron:'M6 9l6 6 6-6',
    pin:'M9 3h6l-1 7 4 4H6l4-4z M12 14v7',
    search:'M10 3a7 7 0 1 0 0 14 7 7 0 0 0 0-14 M15 15l6 6',
    arrow:'M4 12h16 M14 6l6 6-6 6',
    history:'M3 11a9 9 0 1 1 3 8 M3 4v7h7 M12 7v5l3 2'
  };
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
  for(const [key,value] of Object.entries({viewBox:'0 0 24 24',fill:'none',stroke:'currentColor','stroke-width':'1.6','stroke-linecap':'round','stroke-linejoin':'round','aria-hidden':'true',focusable:'false',class:'ui-icon'}))svg.setAttribute(key,value);
  const path=document.createElementNS(svg.namespaceURI,'path');path.setAttribute('d',paths[name]||paths.catalog);svg.append(path);return svg;
}
