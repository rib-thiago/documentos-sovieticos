/* Datas do catálogo e da fonte ShowTrials. */
function documentDateInfo(document) {
  const historical=document.date||document.historical_date?.display||document.historical_date?.value;
  const collected=document.collected_date||document.source_metadata?.wordpress_date;
  const value=historical||collected;
  if(!value)return null;
  const match=String(value).match(/^(\d{4})-(\d{2})-(\d{2})(?:T|\s|$)/);
  return {text:match?`${match[3]}/${match[2]}/${match[1]}`:String(value),
    label:"Data do documento",source:!historical,
    iso:match?`${match[1]}-${match[2]}-${match[3]}`:null};
}
