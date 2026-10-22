# Onda 3 — recuperação de links e destinos de notas

Esta entrega recupera **98.938 links em 2.022 documentos russos** e encerra **2.002 alertas** de reconstrução. A fila geral passa de **2.782 para 780 apontamentos abertos**. Permanecem 38 alertas de links: 20 parcialmente tratados e 18 retidos para passagem específica. Ela não certifica a disponibilidade atual dos sites externos nem a correção histórica das associações feitas por eles.

## Critério de recuperação

O preparador exige correspondência integral e ordenada entre o texto do HTML preservado e o texto canônico. A normalização ignora apenas espaços, escapes Markdown e prefixos estruturais reconhecidos. Cada rótulo é localizado pela posição da própria âncora nessa sequência, não por uma busca avulsa de nomes ou números que podem se repetir.

Os candidatos inserem somente os invólucros Markdown de link. A remoção exata dessas inserções deve recuperar todos os bytes anteriores, inclusive palavras, pontuação, espaços e quebras de parágrafo. As traduções não recebem links por associação automática de nomes: o escopo desta passagem é a edição russa indicada pela fila. Não foram reordenados parágrafos nem criadas relações entre coleções.

Os destinos são os publicados no HTML, resolvidos como URLs absolutas. Fragmentos da própria página só são reconstruídos quando há um destino único no HTML. Esquemas não admitidos, rótulos vazios, links que atravessam linhas/blocos e destinos locais ausentes ou duplicados são retidos para exame. Versões com tabelas reconstruídas ou links Markdown anteriores que impedem a correspondência integral também são preservadas.

O parecer independente está em `temporario/revisao-onda3/REVISAO-PREPARADOR-LINKS.md`; o diagnóstico de notas, em `NOTAS-DIAGNOSTICO.md`. As fontes HTML permanecem no pacote metodológico local. Não houve consulta de rede nesta rodada.

## Como as notas funcionam nesta entrega

As chamadas são links para o fragmento da **publicação original**. As notas literais continuam no fim do próprio Markdown, sem renumeração ou deslocamento. Não foram convertidas em notas locais `[^id]`: o modo estudo atualmente renderiza blocos separados e não compartilha o ambiente global necessário para associar essas chamadas a suas definições. Essa evolução exige trabalho próprio no leitor; não seria seguro introduzir apenas a sintaxe nos arquivos.

Portanto, clicar numa chamada recuperada pode levar ao site da fonte. A restauração do destino publicado não garante que essa página esteja acessível hoje. A leitura do conteúdo local das notas permanece disponível no documento. Essa distinção vale também para links biográficos e anexos externos.

## Casos retidos

- **2644:** a chamada da nota 52 não tem destino correspondente no HTML. A tabela já revisada exige cotejo específico para recuperar os demais links sem desfazer a reconstrução.
- **4576:** já contém links restaurados na revisão das tabelas. A publicação liga o nome de Ivan Kharitonovich Loginov a uma URL com outro nome; o vínculo publicado não autoriza concluir identidade nem substituir automaticamente o destino.
- **5785:** destino `_ftn1` duplicado; a chamada ambígua não foi atribuída a uma das notas por palpite.
- **1442 e 1733:** há anexos sem rótulo textual e vínculos históricos distintos das imagens atuais. Não foram publicados automaticamente novos fac-símiles ou textos inventados para as âncoras vazias.
- Os demais casos são discriminados no [registro de pendências desta passagem](ONDA3-PENDENCIAS.csv), com ID, motivo e endereço local. Um alerta parcial não significa que nenhum link tenha sido recuperado.

Uma revisão independente também identificou sete falsas recusas da normalização: linhas isoladas como `1.`, `4)` e `1929.` não são prefixos de listas com conteúdo. A regra passou a exigir conteúdo na mesma linha. O primeiro preparador foi preservado antes dessa correção; nenhum desses caracteres foi emendado nos documentos. A passagem complementar tem base e histórico próprios. Evidência: `temporario/revisao-onda3/RETIDOS-TEXTUAIS.md` e `textual-holds-evidence.json`.

## Leitor: listas no modo estudo

O modo estudo reconhecia somente listas com hífen e construía manualmente uma lista não numerada. Passou a reconhecer listas ordenadas e não ordenadas pelo interpretador Markdown e a renderizá-las com a mesma sanitização já usada para tabelas. Isso mantém limites dos blocos, números iniciais como 366, quebras e links internos aos itens. HTML bruto continua desativado. O ajuste não constitui novo alinhamento de parágrafos entre idiomas.

O JavaScript anterior a esse ajuste está preservado em `temporario/revisao-onda3/reader/`; a versão de carregamento no HTML foi atualizada. A conferência visual e funcional desse ajuste fica para o roteiro manual abaixo.

## Busca local

O extrator do índice SQLite foi ajustado para indexar o **rótulo visível** dos novos links, sem acrescentar seus destinos codificados ao corpo pesquisável. Primeiro remove o invólucro de link com URL entre sinais angulares; só depois resolve os escapes do texto. Uma URL que seja o próprio rótulo continua pesquisável como texto visível. Textos literais escapados não são convertidos em vínculos por essa regra.

A versão interna do índice passou a 3 para impedir reutilização silenciosa do índice anterior. A gravação complementar reconstrói a busca com essa regra; não foram modificados os textos para conseguir esse resultado. O módulo anterior está preservado em `temporario/revisao-onda3/backend/`.

A [conferência operacional do índice](ONDA3-CONSISTENCIA.json) confirmou sua correspondência com o catálogo atual e a versão do indexador. O diagnóstico da fila não apontou divergências de integridade nos caminhos conferidos; isso não substitui a revisão crítica das fontes ou os testes manuais.

## Gravação, evidências e limites

As gravações usam o gravador editorial existente: prévia, conferência dos hashes anteriores, bloqueio de gravação concorrente, histórico recuperável e atualização de catálogo, manifesto e índice de busca. Projetos e rascunhos do usuário não são sobrescritos. A consulta de impacto não identificou âncoras PDF públicas nos idiomas candidatos que exigissem migração.

| Passagem | Documentos / links | Alertas encerrados | Comprovante |
| --- | --- | --- | --- |
| Principal | 2.015 / 98.829 | 1.995 | [Histórico](onda3-links-20261022-gravacao.json) |
| Complementar | 7 / 109 | 7 | [Histórico](onda3-complemento-20261022-gravacao.json) |

Identificadores recuperáveis: `20261022033714922979-939a768394ff` e `20261022034546361480-46b5536f5915`.

A base de despacho e a fila de entrada estão em `temporario/revisao-onda3/baseline/`; candidatos, diffs e provas por documento em `temporario/revisao-onda3/links/`. O complemento usa base posterior à primeira gravação em `temporario/revisao-onda3-complemento/baseline/`, sem reaproveitar hashes anteriores de documentos que já mudaram. Os resultados e evidências usados na gravação são congelados pelo integrador, com seus hashes nos registros das edições e nos recibos. O histórico completo em `.local/editorial/history/` deve acompanhar o backup local. O [registro de artefatos](ONDA3-ARQUIVOS-PRESERVADOS.json) identifica receitas, resumos, versões anteriores de código e provas congeladas sem duplicar novamente todos os textos do histórico.

[PROGRESSO.json](PROGRESSO.json) registra o escopo de cada lote e os motivos que permanecem abertos. O manifesto de despacho identifica sua base; números de lote de diagnósticos posteriores não substituem esses registros. Não reaplicar preparações antigas sobre arquivos editados posteriormente. O preparador agora recusa sobrescrever uma preparação concluída: uma nova passagem exige outra área de trabalho e outra base.

Não foram executadas suítes de testes ou testes no navegador. Foram realizados processamento documental, cotejo integral/posicional, inspeção independente de código e amostras, provas de preservação e validações transacionais. Fechar um alerta de reconstrução de links não declara revisado todo o documento nem suas traduções.

## Conferência manual

1. Reiniciar `python3 -m backend` se necessário e recarregar o site com Ctrl+Shift+R.
2. Abrir [1633](http://127.0.0.1:8000/#/doc/showtrials-1633) ou [2482](http://127.0.0.1:8000/#/doc/showtrials-2482), selecionar russo e conferir os links e chamadas de notas em leitura e estudo. O rótulo deve permanecer literal; o destino aponta para a fonte original.
3. Abrir [5785](http://127.0.0.1:8000/#/doc/showtrials-5785). Há links recuperados, mas a chamada ambígua continua pendente, sem destino escolhido arbitrariamente.
4. Abrir [3246](http://127.0.0.1:8000/#/doc/showtrials-3246) em estudo paralelo: os sete itens devem aparecer como listas nos três idiomas. Em [6431](http://127.0.0.1:8000/#/doc/showtrials-6431), conferir o número inicial 366 no estudo.
5. Marcar uma passagem longa, mudar de modo e voltar. O conteúdo dos parágrafos foi preservado; a proteção da versão textual continua ativa. Marcas antigas curtas ou ambíguas podem exigir nova marcação, sem deslocamento por palpite.
6. Na fila editorial, consultar “Corrigido” para os alertas encerrados e “Em revisão” para os parcialmente tratados. Abrir o histórico de uma alteração antes de restaurar; a restauração é uma gravação real e pode conflitar com edições posteriores.

Não houve commit nem push. A próxima passagem deve tratar as exceções de links, seções ainda pendentes e revisões preventivas, mantendo o OCR do julgamento separado.
