# Onda 7 — rubricas de protocolos e alertas anteriores

Encerrados **107 apontamentos**, reduzindo a fila de **698 para 591 abertos**. Restam **91 indicadores de seções**, além das demais frentes já registradas. Catálogo, manifesto e índice de busca foram atualizados pelo mecanismo transacional existente.

## Escopo conferido

- **75 alertas obsoletos:** a rubrica literal do protocolo já possuía marcação Markdown. Os arquivos não foram reescritos.
- **32 rubricas recuperadas:** acrescentado somente `## ` ao bloco do título existente. Datas, nomes, conteúdo, ordem, limites de parágrafos, notas, links e traduções foram preservados.
- Os demais elementos destacados desses cabeçalhos são nomes, datas, destinatários, marcas de sigilo ou de formulário. Não foram promovidos indiscriminadamente a seções. Não foram criadas subdivisões temáticas dentro de perguntas e respostas.

Documentos com título recuperado: 4944, 5358, 5511, 5554, 5567, 5618, 5638, 5649, 5659, 5663, 5668, 5711, 5725, 5801, 5812, 5816, 5837, 5850, 5859, 5863, 5878, 5879, 5882, 5886, 5887, 5893, 5914, 6390, 7045, 7415, 7937, 7974.

[Inventário dos 107 resultados](ONDA7-DOCUMENTOS.csv). O encerramento refere-se à navegabilidade estrutural, não a aprovação histórica integral nem revisão das traduções.

As datas literais atípicas permanecem na fonte: por exemplo, 7003 contém 1956 na rubrica e 5927 contém 1935. Não foram harmonizadas com a cronologia aparente. Estes dois arquivos não receberam alteração textual nesta onda; sua condição não foi convertida em certeza histórica.

## Cotejo e preservação

A lista de seleção está congelada em `scripts/revisao_acervo/prepare_wave7_protocols.py`. Cada título precisa corresponder a um bloco completo e único e à rubrica do HTML preservado. O cotejo exige correspondência integral e ordenada da projeção textual do HTML na edição corrente. A inversão precisa dos prefixos inseridos recupera os bytes anteriores. Palavras, notas e destinos de links não são modificados.

Foram preservadas cópias por hash de **13 arquivos JSON de fonte** em `temporario/revisao-onda7/fontes/`. A base, os candidatos e as evidências por documento ficam no mesmo diretório de trabalho. [Registro de preservação](ONDA7-ARQUIVOS-PRESERVADOS.json). A integração compara os hashes da base e o estado da fila, recusa conflitos com âncoras PDF e mantém snapshots das evidências.

Histórico recuperável: `20261022104113473556-cff2ea6b7761`. [Recibo da gravação](onda7-protocolos-20261022-gravacao.json). O histórico integral em `.local/editorial/history/` deve acompanhar o backup local. As mudanças recentes da interface permanecem preservadas.

## Conferência manual

1. Reinicie o backend e recarregue a página com Ctrl+Shift+R.
2. Abra [4944](http://127.0.0.1:8000/#/doc/showtrials-4944), [5801](http://127.0.0.1:8000/#/doc/showtrials-5801) e [7937](http://127.0.0.1:8000/#/doc/showtrials-7937): confira a entrada do protocolo no índice, o nome e a data logo abaixo.
3. Em [5149](http://127.0.0.1:8000/#/doc/showtrials-5149), confirme que o título já existente permanece; o fechamento foi reconciliação do alerta.
4. Se alternar para estudo, os mesmos parágrafos, links e notas devem permanecer. Não houve alteração de traduções ou pareamento automático.

Não foram executados testes automatizados, de aplicação ou navegador. Foram feitos processamento documental, cotejo integral e verificações transacionais de gravação. Sem commit ou push.
