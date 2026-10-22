# Onda 4 — exceções de links, índices e conferência de notas

Foram encerrados **48 apontamentos**, com 41 edições alteradas em 39 documentos. O saldo passa de **780 para 732 apontamentos abertos**. Foram tratados os **38 alertas restantes de reconstrução de links**, recuperados **88 títulos em seis textos extensos** e concluídas quatro conferências pontuais de notas de Mozokhin.

Encerrar uma reconstrução com ressalva não significa corrigir a publicação original ou estabelecer correspondências que ela não permite. As limitações da fonte permanecem explícitas nos textos e no [registro de ressalvas desta rodada](ONDA4-RESSALVAS-FONTE.csv). Nenhum teste de aplicação, commit ou push foi realizado.

## Links em tabelas e textos já revistos

Nos 18 documentos retidos por tabelas ou vínculos anteriores, a comparação integral foi feita contra uma projeção que remove apenas os separadores de apresentação, referências de continuação de células, legenda editorial e invólucros de links. O texto visível da fonte deve continuar em ordem e cada rótulo é localizado pela posição da própria âncora HTML. Células, valores, mesclas e limites entre parágrafos não são reconstruídos novamente.

Foram recuperados **4.371 links** nessa frente, incluindo 1.021 em 2644 e 1.461 em 5660. Em 9930, outro link foi recuperado depois de comprovar que os identificadores duplicados ocupam a mesma posição textual. São **4.372 links recuperados**, além dos anexos identificados abaixo.

No **4576**, 64 vínculos biográficos já estavam corretos. Quatro chamadas/retornos tinham invólucros Markdown incorretos herdados do primeiro piloto. Esses quatro invólucros foram reparados, preservando rótulos e URLs; as 68 âncoras foram então cotejadas por posição com a fonte. Uma nota editorial separada registra a divergência entre o nome Ivan Kharitonovich Loginov e o nome presente na URL externa. Não se substituiu a pessoa nem o endereço por inferência.

No **2644**, o HTML não fornece o elemento com identificador `#_edn52`. A ausência desse identificador **não prova ausência do texto da nota**. A chamada e as notas foram preservadas e a limitação recebeu advertência editorial em RU/PT/EN; não se inventou uma ligação ou renumeração. As traduções anteriores permanecem como prefixo exato, acrescidas somente dessa advertência.

Evidências e diffs: `temporario/revisao-onda4/tabelas/` e `completion/`. Os candidatos das tabelas têm prova reversível de que remover somente os novos invólucros recupera os bytes anteriores. O reparo de 4576 tem registro das quatro formas anteriores/posteriores e verificação integral das 68 âncoras.

## Âncoras vazias, anexos e defeitos da publicação

Os vinte casos parcialmente tratados na onda 3 foram cotejados individualmente:

- **1442 e 1733:** foram acrescentados apêndices explicitamente editoriais com quatro URLs de imagens anexadas no HTML. São destinos da publicação original, sem publicação automática de novos fac-símiles. Em 1733, o vínculo histórico do Google Sites foi preservado como tal, sem equipará-lo às três imagens modernas.
- **4882, 5087, 7377, 9411 e 10746:** as âncoras remanescentes não contêm texto nem imagem. Não há conteúdo visível perdido a reconstruir; as evidências HTML foram preservadas.
- **Treze documentos:** receberam ressalvas sobre identificadores ausentes ou repetidos em posições distintas. As chamadas e o conteúdo das notas permanecem literais, sem escolher uma correspondência por proximidade. Em 9930, apenas o destino comprovadamente equivalente foi recuperado; a outra ambiguidade continua explicada.

Essas decisões encerram o encaminhamento de conversão. Não certificam que toda URL externa funciona hoje ou que as associações biográficas da publicação são corretas. Não houve consulta de rede. As chamadas recuperadas continuam apontando para a publicação original, conforme a política da onda 3; não foram transformadas em notas locais `[^id]`.

## Índices de seis textos extensos

Foram integrados somente candidatos completos e conferidos, com **88 prefixos de título** em linhas já existentes:

| Documento | Organização recuperada |
| --- | --- |
| 4810 | Rubrica do relatório, cinco grupos explicitamente intitulados, quarta sessão e resolução do plenário. |
| 4811 | Sessões e palavras finais; mantidos os rótulos 1/4/5, sem inventar os números ausentes. |
| 2485 | Datas/publicações e títulos de cinco recortes do Pravda, preservando ocorrências repetidas. |
| 2487 | Cinco recortes da Montreal Gazette, com manchetes e entretítulos em níveis distintos. |
| 2488 | Sete manchetes e entretítulos tipograficamente explícitos; falas em negrito não viraram títulos. |
| 4203 | Informe e textos jornalísticos; destinatários e marcas de sigilo continuam como prosa. |

As formulações acusatórias permanecem como títulos dos documentos e jornais, não afirmações históricas adotadas pelo editor. Nenhum artigo foi traduzido ou reclassificado por estar publicado em inglês dentro de uma edição já cadastrada. Nenhuma data, palavra, ordem de bloco ou URL foi alterada para criar esses índices.

O inventário abrange os 233 indicadores de textos longos e cinco decisões editoriais. Foram excluídos do preparador de seções os documentos simultaneamente tratados pela frente de links, evitando edições concorrentes. O inventário não constitui cotejo crítico integral ou autorização para encerrar os demais alertas. Os candidatos incompletos não foram integrados nem marcados como concluídos.

## Quatro notas de Mozokhin

Conferidos os documentos **054, 101, 145 e 146**, as edições vizinhas e as imagens das páginas físicas 94, 180 e 292 do volume 1:

- A nota 29 pertence ao documento 52, não ao 54.
- A nota 40 pertence à assinatura do 101, não ao 102.
- As notas 53/54 pertencem aos documentos 145/146, não ao começo do 147.

Os hashes atuais coincidem com os resultados das receitas e do histórico da correção anterior. Chamadas e definições estão nos respectivos donos, sem duplicação nos vizinhos. Não foi necessária nova alteração textual. O encerramento refere-se à atribuição dessas notas; os registros de revisão geral do catálogo continuam abertos. Também não significa aprovação da renderização dessas notas em todos os modos do leitor.

Evidência: `temporario/revisao-onda4/mozokhin-notas/evidence.json`. A receita de conferência, vinculada aos hashes e às páginas inspecionadas, está em `scripts/revisao_acervo/audit_mozokhin_notes.py`.

## Gravação e retomada

[Comprovante da gravação e identificador recuperável](onda4-revisao-20261022-gravacao.json). A operação usa a prévia editorial, hashes anteriores, bloqueio de gravação concorrente, histórico e atualização de catálogo, manifesto e busca local. As verificações de impacto não encontraram âncoras PDF públicas nos idiomas candidatos exigindo migração. Projetos e rascunhos do usuário não foram sobrescritos.

Histórico: `20261022092621546848-bbb25f5c1914`. A [conferência operacional](ONDA4-CONSISTENCIA.json) confirmou que o índice corresponde ao catálogo e à versão atual do indexador. Não é teste de navegação nem aprovação visual do leitor.

A base de despacho está em `temporario/revisao-onda4/baseline/`; resultados consolidados em `merged/`. Os lotes foram agrupados por proprietário antes de salvar; dois candidatos concorrentes do mesmo documento não foram aplicados em sequência. A integração central completou as evidências e os resultados preparados antes da interrupção dos agentes por limite de uso. Apenas resultados completos e verificáveis foram incluídos.

[PROGRESSO.json](PROGRESSO.json) preserva os recibos e as bases distintas, sem confundir números de lotes de gerações diferentes. O [registro de evidências congeladas](ONDA4-ARQUIVOS-PRESERVADOS.json) permite retomar o cotejo. O histórico completo em `.local/editorial/history/` deve acompanhar o backup local. Não reaplicar os preparadores sobre edições posteriores.

Não foram executados testes de aplicação ou de navegador. Houve cotejo documental, inspeção das imagens do PDF, verificação de hashes e validações transacionais. O exame funcional continua no roteiro manual abaixo.

## Como conferir manualmente

1. Iniciar ou reiniciar `python3 -m backend` e abrir o site com Ctrl+Shift+R.
2. Abrir [2644](http://127.0.0.1:8000/#/doc/showtrials-2644): conferir a tabela, os links e a advertência final sobre o identificador52 nos três idiomas. A tabela não deve perder células ou valores.
3. Abrir [4576](http://127.0.0.1:8000/#/doc/showtrials-4576): as duas chamadas e seus retornos devem aparecer como links, sem pedaços de sintaxe Markdown. A nota editorial final distingue o vínculo externo de uma identificação histórica confirmada.
4. Abrir [1442](http://127.0.0.1:8000/#/doc/showtrials-1442) e ir ao apêndice final: conferir os três links de imagens identificados como editoriais. Sua abertura depende da disponibilidade do site externo.
5. Abrir [2487](http://127.0.0.1:8000/#/doc/showtrials-2487) e [4810](http://127.0.0.1:8000/#/doc/showtrials-4810): o índice deve navegar por recortes/sessões e subseções. Conferir também a leitura no modo estudo, sem supor novo alinhamento entre idiomas.
6. Na fila, conferir os motivos encerrados e o histórico. Em Mozokhin, filtrar pela conferência de notas e distinguir esse encerramento da revisão geral do mesmo documento.

O próximo trabalho fica nos **227 indicadores de seções**, cinco decisões de hierarquia e conferências gerais do catálogo. As doze divergências entre versões e os dois trabalhos de imagem/OCR permanecem separados, sem emendas conjecturais.
