# Onda 5 — hierarquia, seções e representação de datas

Foram encerrados **16 apontamentos** e tratados parcialmente **11 cadastros locais**. O saldo passa de **732 para 716 apontamentos abertos**. Foram inseridos **45 títulos em dez edições russas**, preservando palavras, URLs, ordem e limites dos parágrafos. Nenhuma tradução foi substituída ou criada.

As cinco decisões de hierarquia que permaneciam na fila receberam encaminhamento documentado. Isso não significa revisão crítica integral das fontes ou aprovação visual do leitor. Não houve testes de aplicação, commit ou push.

## Títulos recuperados

| Documento | Títulos novos | Tratamento |
| --- | ---: | --- |
| 6762 | 6 | Partes explicitamente intituladas da minuta de acusação; chaves, colchetes, numeração alternativa e numerais romanos isolados preservados. |
| 8164 | 9 | Introdução, parte e rubricas tipográficas, distinguindo níveis de navegação. |
| 7995 | 4 | Capítulo II, identificação do extrato e suas seções 3/4; separadores e lacunas de numeração conservados. |
| 8623 | 6 | Seções 1, 2, 3, 4, 6 e 7, sem acrescentar 5 ou inferir perda de texto. |
| 4796 | 7 | Títulos das tabelas, formulário e resumo estatístico já existentes fora das grades. |
| 4849 | 6 | Título e cinco grupos do plano de relatório; formulações acusatórias continuam atribuídas à fonte. |
| 2537 | 2 | Transcrição e conclusões da perícia. |
| 2483 | 1 | Título da transcrição, preservando o título de sentença já recuperado anteriormente. |
| 5648 | 2 | Comunicação e ato; preservado o título do protocolo já existente. |
| 10713 | 2 | Partes alemã e russa da publicação, mantidas na edição composta existente. |

Não se criou uma numeração única para conciliar camadas de uma minuta. Em 6762, 7995 e 8623, notas explicitamente editoriais esclarecem a preservação da forma publicada e o papel dos níveis do índice. Não foi preenchido qualquer capítulo ou número ausente. Os destinatários, datas, marcas de sigilo e separadores tipográficos não foram promovidos indiscriminadamente a títulos.

## Cartas contínuas e alertas anteriores

- **7248 e 7250:** são cartas contínuas, com data, saudação, parágrafos, assinatura e referência arquivística. Não foram subdivididas em temas inventados. Em 7248, o marcador isolado `1.` aparece depois da nota final; foi preservado, sem transformá-lo em seção do corpo.
- **5793 e 6958:** os dois protocolos de cada documento já possuíam títulos recuperados na onda 2. A conferência atual confirmou a estrutura e o texto integral em ordem; o alerta anterior de navegabilidade foi encerrado sem nova edição do conteúdo.

Esses quatro documentos não receberam alterações textuais nesta onda. O encerramento significa que o encaminhamento estrutural foi decidido, não que os conteúdos ou traduções tenham sido aprovados integralmente.

## Como a fidelidade foi conferida

Os candidatos usam uma seleção editorial explícita de elementos do HTML preservado. A comparação exige correspondência integral e ordenada do texto visível, descontando apenas apresentação tabular, escapes e invólucros de links documentados nas ondas anteriores. Cada título precisa corresponder a um bloco completo e único do Markdown; títulos já marcados são preservados.

Somente prefixos Markdown são inseridos nos blocos selecionados. A inversão exata das inserções recupera os bytes anteriores; as três notas editoriais são apêndices separados. Não houve fusão ou divisão de parágrafos. As tabelas, vínculos e correções anteriores permaneceram intactos.

Foi corrigida uma limitação do localizador de blocos do preparador: um parágrafo de um único caractere, como `I`, podia ser agrupado com o parágrafo seguinte pela expressão anterior. A nova localização respeita a linha vazia. Antes disso, o candidato era recusado; não havia sido gravado texto corrompido. A limitação foi encontrada durante o cotejo real da minuta 6762, sem executar suíte de testes.

Receita: `scripts/revisao_acervo/prepare_wave5_sections.py`. Evidências, prefixos selecionados, títulos preexistentes e candidatos: `temporario/revisao-onda5/secoes/`. A base está em `temporario/revisao-onda5/baseline/`; o inventário anterior continua preservado e vinculado por hash.

## Onze datas já cadastradas

Os onze artigos locais possuíam rótulo de data, mas `value` nulo e precisão `not_recorded`. Foi normalizada **somente a representação desses rótulos já cadastrados**, sem afirmar uma nova data histórica ou consultar a página externa:

- Nove datas numéricas da série *Menshevik attempt to overthrow Bolshevism*: a interpretação dia/mês foi confrontada com o caminho ano/mês/dia da URL já cadastrada.
- `13 de junho de 2023`: representação estruturada `2023-06-13` e precisão de dia.
- `2004`: representação `2004` e precisão de ano, sem inventar 1º de janeiro.

O rótulo público, títulos, autoria, URLs, coleções, documentos e traduções foram preservados. A normalização não confirma autoria, data real de publicação ou conteúdo na fonte externa. Por isso, os **onze motivos continuam abertos, em revisão**, com próxima ação específica. Nenhuma revisão completa de cadastro foi encerrada apenas por integridade de arquivos.

Receita: `scripts/revisao_acervo/prepare_local_catalog_dates.py`. Evidências antes/depois e limites da verificação: `temporario/revisao-onda5/catalogo-local/`. O integrador também passou a congelar a evidência dos metadados, como já fazia para alterações de edições.

## Gravação e recuperação

[Comprovante da operação recuperável](onda5-secoes-catalogo-20261022-gravacao.json). A gravação usa prévia, comparação com hashes e estado de fila anteriores, bloqueio de concorrência e atualização de catálogo, manifesto e índice local. Os candidatos não apresentaram conflitos com âncoras PDF públicas. Projetos e rascunhos do usuário não foram sobrescritos.

Histórico: `20261022094412895057-b9679b4ff129`. A [conferência operacional](ONDA5-CONSISTENCIA.json) confirmou a correspondência do índice gravado com o catálogo atual e a versão do indexador.

[Registro de evidências congeladas](ONDA5-ARQUIVOS-PRESERVADOS.json) e [progresso](PROGRESSO.json). Os resultados consolidados estão em `temporario/revisao-onda5/merged/`. Cada número de lote está associado ao manifesto de sua base; não se devem confundir lotes de diagnósticos posteriores. O histórico completo em `.local/editorial/history/` deve acompanhar o backup local.

Não foram executados testes de aplicação ou navegador. Houve processamento documental, cotejo estrutural, provas de preservação e validações transacionais. A avaliação visual permanece com o responsável.

## Conferência manual

1. Iniciar ou reiniciar `python3 -m backend`, abrir o site e recarregar com Ctrl+Shift+R.
2. Abrir [6762](http://127.0.0.1:8000/#/doc/showtrials-6762). Usar o índice e conferir as chaves, colchetes e numerações alternativas; a nota editorial deve explicar que não foram unificadas.
3. Abrir [8623](http://127.0.0.1:8000/#/doc/showtrials-8623). O índice deve mostrar 1/2/3/4/6/7, sem seção 5 inventada. Em [7995](http://127.0.0.1:8000/#/doc/showtrials-7995), conferir capítulo II e os extratos.
4. Abrir [4796](http://127.0.0.1:8000/#/doc/showtrials-4796). Navegar pelos títulos das tabelas e conferir que as grades continuam intactas em leitura e estudo.
5. Abrir [10713](http://127.0.0.1:8000/#/doc/showtrials-10713). Os dois títulos devem permitir chegar às partes alemã e russa sem criar novos documentos ou idiomas artificiais.
6. Na área editorial, abrir um dos artigos locais, como `ep-1-arkhangelsk`: a data exibida deve continuar `29/05/2024`, com valor ISO `2024-05-29`. O artigo de 2004 deve ter precisão de ano. Os onze motivos de cadastro permanecem em revisão; não salvar alterações de conferência sem considerar que serão edições reais.

Restam **216 indicadores de seções**, **486 conferências gerais de catálogo/cadastros**, **12 divergências entre versões** e **dois trabalhos de imagem/OCR**. As cinco decisões anteriores de hierarquia e os alertas de reconstrução de links estão tratados, preservando as ressalvas da fonte.
