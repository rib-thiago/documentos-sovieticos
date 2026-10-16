/* Separa apenas o envelope reconhecido da exportação, sem remover títulos do corpo. */
function splitExportHeaders(source) {
  let body = source;
  const headers = [];
  const pattern = /^(?:\uFEFF)?(?:[ \t]*\r?\n)*#[ \t]+[^\r\n]+\r?\n(?:(?:[ \t]*\r?\n)|(?:(?:Fonte|Source|ID\s+ShowTrials|ShowTrials\s+ID|ID\s+(?:do\s+)?documento|Document\s+ID|Idioma|Language|Data do documento|Data na fonte\s*\(não verificada\))[ \t]*:[^\r\n]*\r?\n))+[ \t]*---[ \t]*(?:\r?\n|$)(?:[ \t]*\r?\n)*/i;
  while (true) {
    const match = body.match(pattern);
    if (!match || !/^(?:Idioma|Language)[ \t]*:/im.test(match[0]) ||
        !/^(?:Fonte|Source|ID\s+ShowTrials|ShowTrials\s+ID|ID\s+(?:do\s+)?documento|Document\s+ID)[ \t]*:/im.test(match[0])) break;
    headers.push(match[0]);
    body = body.slice(match[0].length);
  }
  return { body, headers, header_count: headers.length };
}
