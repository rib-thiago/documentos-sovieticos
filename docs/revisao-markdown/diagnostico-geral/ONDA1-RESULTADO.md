# Onda 1 — resultados integrados e conferência manual

Execução iniciada em 21/10/2026, concluída nesta entrega na madrugada de 22/10 UTC. **76 apontamentos encerrados** com evidência por chave. A fila passou de **2.905 para 2.829 abertos**, distribuídos agora por 2.562 documentos. Há 2.825 pendentes, quatro em revisão e 78 corrigidos no histórico total. Não houve commit nem push.

## Resultado por escopo

| Escopo prioritário | Tratamento nesta entrega | Restante |
|---|---|---|
| 37 alertas de tabelas ShowTrials | 24 documentos tiveram estrutura reconstruída; 13 alertas eram quadros de disposição/diálogo já preservados | Nenhum dos 37 alertas de tabela desta base continua aberto |
| 31 conferências militares | 30 encerradas após cotejo das fontes; textos preservados | Julgamento em PDF: transcrição por OCR e revisão por página |
| Oito alertas de imagens | Sete conferidos e encerrados | Documento 5360: divergências entre testemunhos e anotações |
| Links nos pilotos | Duas chaves encerradas; duas parcialmente tratadas | Passagem de links/notas continua na onda 3 |

O fechamento não significa revisão histórica ou filológica integral. As tabelas e as alegações nelas contidas continuam pertencendo às respectivas fontes. Igualdade textual/numérica não comprova o que os documentos afirmam.

**28 edições em 24 documentos** receberam alterações estruturais: 24 russas e quatro traduções (PT/EN dos documentos 4504 e 2644). As palavras das traduções foram preservadas; não houve nova tradução, alinhamento automático nem reescrita para igualar contagens. As demais traduções permaneceram intactas. O documento 3405 conserva o diálogo rotulado em três idiomas, uma representação válida da disposição pergunta/resposta da fonte.

## Tabelas e cabeçalhos

As reconstruções localizaram o texto integral das tabelas em posições únicas, conferiram cada célula e sua ordem e preservaram o conteúdo exterior aos intervalos. Foram recuperadas também células cujas fronteiras estavam misturadas no interior de parágrafos. Não foram corrigidos nomes, números ou datas por plausibilidade.

Nas grades com mesclas, cada célula física aparece uma vez; `↳ LxCy` identifica a continuação e sua coordenada de origem na tabela-fonte. Uma nota explicitamente editorial explica a representação. Os cabeçalhos multinível e as unidades permanecem literais; o cabeçalho vazio de apresentação não transforma o primeiro registro em rótulo inventado. Nos documentos 4583 e 4771, linhas de largura integral que são títulos explícitos da fonte foram preservadas como seções antes das tabelas correspondentes. Os títulos anteriores não foram removidos; em 4583 a terceira seção explícita também foi recuperada.

No documento 5284, a coluna final de observações tem cabeçalho, mas os registros HTML não trazem a célula final: foram representados espaços vazios, conforme a grade, com essa ausência documentada. Nenhuma observação foi completada.

A classificação dos 13 quadros de disposição evita transformar cabeçalhos de telegrama, listas de distribuição de exemplares, uma lista em célula única e um diálogo rotulado em tabelas de dados artificiais. O texto foi comparado célula por célula e permaneceu em ordem no Markdown.

Receitas e evidências estão em `scripts/revisao_acervo/` e `temporario/revisao-onda1/`. Os candidatos foram gravados só depois de conferir hashes anteriores, fontes e conflitos. A receita de cada reconstrução e o diff permitem conferir valores e limites, além dos resumos dos pilotos [A](ONDA1-TABELAS-A.md) e [2644](ONDA1-TABELA2644.md).

## Militares: conferência sem reescrita desnecessária

As 13 tabelas dos três documentos industriais já correspondiam às fontes; foram cotejadas posições, valores, mesclas e campos vazios. Nos demais 27 textos, o corpo foi localizado integralmente e em ordem no HTML preservado; chamadas/definições e destinos foram conferidos. Nenhuma alteração textual foi necessária. As omissões declaradas pelas publicações-fontes permanecem assim identificadas.

Foi corrigido somente o metadado da ata `military-nko35-protocol`: a datação literal é `[Не позднее 8 декабря 1935 г.]`. O catálogo agora mostra **“Não posterior a 8 de dezembro de 1935”**, mantendo valor ISO nulo, sem transformar limite superior em data exata. O período do evento presente no título foi preservado.

O julgamento de 1937 permanece corretamente identificado como ficha de fontes, não como transcrição. O próximo trabalho é OCR russo e revisão de 172 páginas na ferramenta existente, com guarda de progresso e das imagens. A publicação inglesa é distinta e não deve ser automaticamente alinhada ao russo. Não foi executado OCR nem alterado projeto/PDF do usuário nesta entrega.

## Imagens: aquisição e cotejo reais

As imagens foram adquiridas em área de trabalho e abertas para inspeção. Foram conferidos cartões frente/verso, cartas manuscritas, informes datilografados e capa. O conteúdo já transcrito foi distinguido de marcas postais, aparato editorial e elementos bibliográficos. Uma capa não foi confundida com corpo documental ausente. No caso 7391, a imagem é uma página parcial que corresponde à abertura transcrita; isso não certifica integralidade de toda a compilação.

No **5360**, a miniatura de 150 pixels não permitia leitura. A imagem integral foi obtida pelo `srcset` declarado na fonte. **A entrada 5, Novikov, apresenta na imagem as leituras 1891/1918, enquanto a transcrição atual traz 1899/1916.** Há também anotações manuscritas coloridas. Essa pendência continua em revisão: cotejar se são estados/testemunhos distintos e registrar variantes antes de emendar RU ou traduções. Nenhum desses números foi substituído silenciosamente.

O acesso de rede no ambiente restrito falhou por DNS; a aquisição foi retomada com acesso autorizado. As imagens ficam em `temporario/revisao-onda1/imagens/`, com URLs e hashes em `acquisition.json`; a carta 3276 permanece na pasta `estrutura-impares/images/`. Elas não foram automaticamente publicadas como novos fac-símiles no site.

## Leitor: proteção e renderização

A reconstrução muda o número de blocos; números antigos de parágrafo não devem ser tratados como identificadores permanentes. O marcador passou a registrar uma assinatura da versão textual. Após revisão, só se relocaliza uma passagem suficientemente longa com correspondência única; números curtos de células e correspondências ambíguas não são transferidos por palpite. Marcas antigas de trechos curtos podem precisar ser feitas novamente. Na mesma versão, continua possível marcar e desmarcar trechos curtos normalmente.

Também foi acrescentada a renderização de tabelas Markdown no modo estudo: anteriormente a segmentação juntava suas linhas como texto corrido. O modo estudo agora mantém o bloco da tabela e usa o mesmo interpretador com sanitização e HTML bruto desativado. Não se habilitaram tabelas HTML arbitrárias. A quebra `<br>` inicialmente preparada no cabeçalho de 2644 foi substituída por espaço, preservando palavras, em uma segunda transação identificada; não aparece como tag literal no leitor.

Antes de gravar os textos foram consultados os vínculos PDF locais: não havia âncoras persistentes nos idiomas alterados que exigissem migração. Correções de trecho continuam exigindo correspondência exata e versão atual. Projetos e rascunhos do usuário não foram sobrescritos; não foi efetuada migração cega de marcadores, citações ou offsets.

O JavaScript anterior está preservado em `temporario/revisao-onda1/reader/`; o ajuste de `index.html` apenas muda a versão de carregamento do script. A aprovação visual/funcional desse ajuste fica para a conferência manual abaixo: não houve teste no navegador.

## Históricos e retomada

| Transação | Histórico recuperável | Comprovante |
|---|---|---|
| Pilotos, oito edições e três conferências militares | `20261021204824392420-5b077efb2083` | [Recibo](onda1-pilotos-20261021-gravacao.json) |
| Formatação de 2644 nos três idiomas | `20261022021517706345-57f8d0df1695` | [Recibo](onda1-formato2644-20261021-gravacao.json) |
| Demais militares e datação da ata | `20261022021610754400-d727206af8f9` | [Recibo](onda1-militares-restantes-20261021-gravacao.json) |
| Estruturas e imagens restantes | `20261022023857336344-7f4739c22525` | [Recibo](onda1-estruturas-20261021-gravacao.json) |

O histórico guarda antes/depois dos textos, fila e arquivos de catálogo alterados. Catálogo, manifesto e busca foram atualizados nas transações de conteúdo/metadados. Os 139 artefatos congelados estão identificados em [ONDA1-ARQUIVOS-PRESERVADOS.json](ONDA1-ARQUIVOS-PRESERVADOS.json). Não reaplicar preparadores antigos sobre edições posteriores; usar o snapshot, os hashes de entrada e os recibos.

[PROGRESSO.json](PROGRESSO.json) registra os resultados dos 39 lotes originais da onda 1. “Integrado com pendências” inclui motivos de links/seções que pertencem a passagens seguintes; não significa que todas as chaves do documento tenham sido encerradas. Os agentes foram interrompidos pelo limite de uso; o integrador concluiu os artefatos disponíveis e o cotejo estrutural com fontes preservadas, sem registrar como concluído o que dependia de nova transcrição ou exame de variantes.

[Diagnóstico atual](DIAGNOSTICO.csv) e [novos lotes das chaves remanescentes](LOTES.json). O manifesto original da onda está preservado em `temporario/revisao-onda1/baseline/` e nos snapshots. A próxima frente prevista é a onda 2, além das duas entregas delimitadas de OCR/variantes que ficaram em revisão.

## Como conferir manualmente

1. Iniciar `python3 -m backend`, abrir o site e recarregar com **Ctrl+Shift+R**.
2. Abrir [4504](http://127.0.0.1:8000/#/doc/showtrials-4504). Conferir a ficha inicial em tabela e o texto posterior; alternar entre leitura, estudo e paralelo RU/PT/EN.
3. Abrir [2644](http://127.0.0.1:8000/#/doc/showtrials-2644). O índice inicial deve ter quatro colunas, seis campos vazios e nenhum `<br>` literal. Os valores estranhos `807` e `21 1` foram preservados e documentados.
4. Abrir [4791](http://127.0.0.1:8000/#/doc/showtrials-4791) ou [2537](http://127.0.0.1:8000/#/doc/showtrials-2537): conferir cabeçalhos em níveis, referências `↳ LxCy`, legenda editorial e rolagem horizontal da tabela.
5. Abrir [4771](http://127.0.0.1:8000/#/doc/showtrials-4771): os seis títulos de seção continuam disponíveis e as tabelas ficam em seus respectivos grupos.
6. Marcar um parágrafo de prosa, mudar de modo e voltar ao documento; a marca deve permitir retomada. Clicar de novo remove a marca. Marcas antigas em células curtas anteriores à reconstrução podem não ser retomadas: o leitor deve avisar que não localizou, em vez de apontar para outro número igual.
7. Na área editorial, abrir **Fila de revisão**. Para ver os casos parcialmente tratados, escolher **Em revisão**: 5360, julgamento PDF e os dois motivos de links dos pilotos. Para comparar fechamentos, escolher **Corrigido**. Ler notas e histórico de uma chave sem presumir que todo o documento recebeu revisão crítica integral.

Não foram executadas suítes de testes nem testes no navegador. Houve processamento e cotejo de fontes, conferências de hashes/células, diagnóstico de impactos e validações transacionais do gravador. O exame visual do leitor permanece a cargo da validação manual.
