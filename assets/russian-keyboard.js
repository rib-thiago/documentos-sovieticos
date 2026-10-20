/* Teclado russo compartilhado. Insere na seleção e dispara o fluxo normal de edição. */
(() => {
  const attached = new WeakSet();
  const rows = ['йцукенгшщзхъ', 'фывапролджэ', 'ячсмитьбюё'];
  function attach(input) {
    if (attached.has(input) || input.readOnly || input.disabled || !input.parentNode) return;
    attached.add(input);
    const panel = document.createElement('details'); panel.className = 'russian-keyboard';
    const summary = document.createElement('summary'); summary.textContent = 'Я · Teclado russo';
    const description = document.createElement('p'); description.textContent = 'Posicione o cursor no texto. As teclas inserem caracteres sem mudar o idioma do computador.';
    const keys = document.createElement('div'); keys.className = 'russian-keyboard-keys';
    let uppercase = false;
    const letters = [];
    function insert(value, remove = false) {
      if(input.disabled || input.readOnly) return;
      const start = input.selectionStart ?? input.value.length, end = input.selectionEnd ?? start;
      const previous = Array.from(input.value.slice(0, start)).pop() || '';
      if(!remove && input.maxLength >= 0 && input.value.length - (end-start) + value.length > input.maxLength) return;
      input.setRangeText(value, remove && start === end ? start - previous.length : start, end, 'end');
      input.dispatchEvent(new Event('input', {bubbles:true}));
      input.focus({preventScroll:true});
    }
    function button(label, action, aria) {
      const key = document.createElement('button'); key.type = 'button'; key.textContent = label;
      if (aria) key.setAttribute('aria-label', aria);
      key.addEventListener('mousedown', event => event.preventDefault());
      key.addEventListener('click', event => {event.preventDefault(); action();}); return key;
    }
    for (const row of rows) {
      const line = document.createElement('div'); line.className = 'russian-keyboard-row';
      for (const letter of row) {
        const key = button(letter, () => insert(uppercase ? letter.toUpperCase() : letter));
        letters.push([key,letter]); line.append(key);
      }
      keys.append(line);
    }
    const controls = document.createElement('div'); controls.className = 'russian-keyboard-row';
    const shift = button('⇧ Maiúsculas', () => {
      uppercase = !uppercase; shift.setAttribute('aria-pressed', String(uppercase));
      for (const [key,letter] of letters) key.textContent = uppercase ? letter.toUpperCase() : letter;
    }); shift.setAttribute('aria-pressed','false');
    controls.append(shift, button('Espaço', () => insert(' ')), button('⌫', () => insert('',true), 'Apagar seleção ou caractere anterior'));
    keys.append(controls); panel.append(summary,description,keys); input.before(panel);
  }
  function scan(root) {
    if (root.matches?.('textarea')) attach(root);
    root.querySelectorAll?.('textarea').forEach(attach);
  }
  scan(document);
  new MutationObserver(records => {
    for (const record of records) for (const node of record.addedNodes) if(node.nodeType === 1) scan(node);
  }).observe(document.documentElement,{childList:true,subtree:true});
})();
