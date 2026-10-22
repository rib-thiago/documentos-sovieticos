# Svitlana — triagem integral e primeiro lote de revisão documental

> Atualização posterior: as 21 unidades desta prévia foram incorporadas em 21/10/2026, com histórico `20261021202030701731-12da7260f03e`. [Comprovante](svitlana-21-rodada5-gravacao.json). O texto abaixo registra a etapa de preparação.

## Entrega de 21/10/2026

Todas as **779 páginas adquiridas** passaram por diagnóstico estrutural mecânico. Houve cotejo documental de **22 páginas** nesta rodada: 20 candidatas individuais e duas compostas. Resultado: **21 novas unidades preparadas**, além das 13 versões já incorporadas que permanecem intactas. A revisão humana/editorial integral das demais páginas ainda não está concluída.

**Esta rodada não gravou novos documentos no site.** Gerou uma prévia local de incorporação, preservando o catálogo ativo e as URLs. Não foram executadas suítes de testes, testes no navegador, commit ou push. Conferências de fontes, hashes e validações de preparação foram executadas.

## Correção que recuperou texto

O conversor selecionava a maior div WordSection mesmo quando ela estava vazia, continha só um título ou deixava seções irmãs de fora. Assim, alguns Markdown muito curtos não representavam o conteúdo real do HTML já adquirido.

A seleção agora recorre ao corpo quando o conteúdo visível da seção é inferior a 85% do corpo. Esse limiar é proteção contra truncamento, não certificação editorial: o corpo mais amplo pode incluir navegação, que continua indicada para revisão. A reconversão usou somente fontes locais, sem nova coleta, e alterou **118 candidatos**. Os arquivos anteriores e o inventário anterior foram preservados. [Registro por hash](SVITLANA-RECONVERSAO-RODADA4.json).

As **13 versões já incorporadas** continuam coincidindo em ID, idioma e hash com o catálogo. Uma decisão nova afetada pela reconversão foi novamente cotejada, em vez de simplesmente receber o hash novo.

## Documentos revisados

- **16 peças individuais** preparadas, com títulos, datas e aparato cotejados. [Relatório das 20 candidatas](SVITLANA-SIMPLES-RODADA4.md).
- **Cinco unidades extraídas de duas páginas compostas:** carta de Ezhov, telegrama anexo de Uspensky, tratado preliminar de 1920, anexo de armistício e instrumento de ratificação. [Relatório e fronteiras](SVITLANA-COMPOSTAS-RODADA4.md).
- **Quatro candidatas individuais retidas:** duas notas ausentes já no HTML, uma votação cuja disposição visual precisa de reconstrução e um cabeçalho colado à navegação. Não foram inventadas notas nem votos.

A data da carta de Ezhov não foi herdada pelo telegrama sem data própria. As notas do telegrama não foram atribuídas à carta. A cota comum foi identificada como aparato compartilhado. A ausência do mapa mencionado no tratado, o corte explícito no telegrama e as aspas incompletas da fonte permanecem registrados.

As divisões usam faixas explícitas de caracteres vinculadas ao hash da página original, com hash final por unidade. O emissor bloqueia perda de texto não branco, sobreposição não declarada e divergências de hash; só exclui os trechos de navegação explicitamente demarcados. Fontes e versões integrais permanecem disponíveis.

## Situação após esta rodada

| Medida | Total |
|---|---:|
| Páginas adquiridas |779|
| Páginas com decisão editorial válida |35|
| Páginas ainda sem decisão editorial |744|
| Unidades após individualização |783|
| Versões já incorporadas |13|
| Novas unidades preparadas |21|
| Referências/envoltórios de PDF |24|
| Demais unidades retidas |725|

As 725 retidas incluem candidatas ainda não lidas e decisões de retenção específicas. Não representam 725 falhas de aquisição. As 24 referências não significam que seus PDFs tenham sido obtidos.

A triagem atual registra 29 páginas com tabelas complexas, 24 corpos curtos, 37 com múltiplos marcadores de aparato/anexo e 12 com texto normalizado igual a outro candidato. Categorias se sobrepõem. Igualdade de texto normalizado pode indicar mensagens de download iguais, não identidade entre documentos históricos. Não houve fusão ou exclusão automática.

[Diagnóstico por página em CSV](SVITLANA-ESTRUTURA.csv) e [evidências em JSON](SVITLANA-ESTRUTURA.json). A fila conserva prioridade, motivo, fonte, hashes, séries, início/fim e marcadores para orientar os próximos lotes. O [estado geral das quatro frentes](ESTADO-ATUAL.md) também foi atualizado.

## Prévia de incorporação

Pacote: `temporario/coletas-quatro/preview/97ece523f68c52694b8fa741c7d241f8c32f1286cabea86d7450e43777b603c1/`.

A prévia prevê **21 documentos/21 versões novos** e três subcoleções correspondentes às séries de origem. O catálogo resultante teria 2.726 documentos e 3.858 versões. É uma projeção: o acervo ativo continua com 2.705 documentos e 3.837 versões. A checagem de duplicatas não bloqueou as 21 novas peças; identidade histórica entre traduções diferentes ainda pode exigir cotejo posterior.

O pacote contém os textos individuais e a projeção de catálogo/manifesto. Não há URLs públicas novas nesta etapa. Uma incorporação posterior deve conferir novamente a revisão do catálogo; o gravador existente recusa bases divergentes, preserva históricos e atualiza busca/manifesto na transação.

## Conferência manual

1. Abrir os relatórios de peças simples e compostas acima e escolher uma candidata.
2. Em `temporario/coletas-quatro/svitlana/units.json`, localizar seu ID. Abrir `raw` e `provenance.source_markdown` a partir da pasta Svitlana para comparar a página integral com o HTML preservado.
3. Abrir o caminho `markdown` da unidade para conferir a versão individualizada. As faixas e o aparato compartilhado estão na proveniência; a versão integral nunca foi descartada.
4. Para ver a correção do conversor, consultar o registro de reconversão e comparar os arquivos de hashes anterior e atual. Exemplos: `svitlana-4ad77397c3c6d902` antes estava vazio; `svitlana-059b8fa3e518a235` antes continha somente um título. Agora o texto disponível no HTML foi recuperado, mas continua aguardando cotejo editorial.
5. Não procurar as 21 novas unidades na home ainda: esta entrega é de preparação e prévia, sem gravação canônica.

Próximo trabalho: continuar o cotejo das 744 páginas sem decisão, começando pelas reconvertidas e pelos sinais de tabelas, anexos e repetições; obter os PDFs das 24 referências como aquisição própria, sem tratá-los como textos já coletados.
