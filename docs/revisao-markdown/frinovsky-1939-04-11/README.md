# Frinovsky — declaração de 11 de abril de 1939

Revisão editorial de 27/10/2026. Documento: `frinovsky-1939-04-11`, coleção existente Yezhov vs Stalin. Não houve criação de novo ID, mudança de URL ou exigência de fac-símile.

## Fontes conferidas

- [Russo — site de Grover Furr](https://msuweb.montclair.edu/~furrg/research/frinovskyru.html).
- [Inglês — site de Grover Furr](https://msuweb.montclair.edu/~furrg/research/frinovskyeng.html).

As duas páginas foram recuperadas integralmente e preservadas em `temporario/revisao-frinovsky-20261027/`, com hashes em [evidence.json](evidence.json). A página russa usa Windows-1251. A indicação bibliográfica de ambas é *ЛУБЯНКА. Сталин и НКВД — НКГБ — ГУКР «СМЕРШ». 1939 — март 1946*, Moscou, 2006, p. 33–50. O livro/manuscrito não foi examinado: a autoridade deste cotejo são as duas transcrições HTML indicadas pelo responsável.

## Resultado do cotejo

RU e EN correspondem às páginas indicadas. A comparação integral de tokens, após normalizações explicitadas de pontuação, páginas e palavras partidas, não encontrou diferenças lexicais não explicadas: 8.070 tokens RU e 10.766 EN. Em inglês foram separados da comparação os acréscimos já identificados como editoriais. A receita e os resultados estão em [source-comparison.json](source-comparison.json); isso não significa igualdade byte a byte nem certificação da exatidão histórica ou tradutória da publicação.

A versão portuguesa foi lida editorialmente e conferida quanto à cobertura e à estrutura do russo. Antes desta revisão havia 162 blocos RU, 164 PT e 171 EN. Os dois blocos adicionais PT são avisos editoriais; excluindo apenas esses avisos, a sequência RU/PT possui as mesmas 162 unidades, incluindo cabeçalhos, páginas e aparato. O [mapa de cobertura](coverage-ru-pt.csv) registra a correspondência. Ele não é um alinhamento automático de trechos para o leitor nem uma prova algorítmica de equivalência semântica.

As três versões representam o mesmo documento, mas não são traduções sem diferenças:

1. O HTML inglês omite o parágrafo sobre os encontros com Evdokimov em Moscou, existente no russo. A edição local EN/PT já o supria com aviso explícito de tradução do russo; esse aviso e o trecho foram preservados.
2. O inglês do site não reproduz o aparato das anotações marginais. As edições locais EN/PT já o incluíam como acréscimo editorial derivado do russo. A atribuição a Stalin provém da transcrição; não houve inspeção de caligrafia.
3. A primeira marca de página inglesa é `55`, enquanto RU/PT trazem `35`. Não se substituiu o testemunho inglês silenciosamente.
4. As formas russas `лаче`, `ВАКОВСКОГО` e `кололыциков` estão no HTML indicado. Permanecem no texto russo. As formas correntes das traduções não são tratadas como emendas do original.
5. O inglês contém pontos de interrogação numa glosa de Razvedupr e a forma `Lepis`, enquanto RU/PT trazem as formas correspondentes a Lepsis. São particularidades do testemunho inglês, preservadas. Suas explicações e glosas próprias não foram acrescentadas retroativamente ao russo.

## Correções realizadas

- Os sinais com asteriscos do aparato eram tratados em parte como ênfase Markdown e em parte como texto solto. Foram convertidos em **dez notas identificadas, com doze chamadas por idioma**. A nota sobre três sobrenomes possui três chamadas.
- Os sinais originais continuam registrados em cada definição; indicação de trecho circulado/sublinhado e texto de cada anotação foram preservados. Em EN, a associação das chamadas é editorial, derivada do RU, e está declarada.
- As palavras e números da narrativa não foram substituídos. As [diferenças RU](diff.ru.patch), [PT](diff.pt.patch) e [EN](diff.en.patch) permitem conferir as mudanças. O teste de invariância lexical do corpo foi incluído na preparação.
- Acrescentada nota de edição por idioma com proveniência e limites do cotejo; as divergências não foram removidas para fazer as versões parecerem idênticas.
- Fontes e referência bibliográfica registradas no catálogo; hashes, manifesto e índice de busca atualizados pela gravação editorial recuperável.

Não foram reatribuídos a Frinovsky comentários editoriais das versões modernas. Não foi feita nova tradução integral do inglês nem declarada aprovação histórica das afirmações do depoimento. O estado genérico de tradução revisada não foi marcado automaticamente: o escopo registrado é esta revisão de fonte, cobertura e formatação.

## Conferir no site

Reinicie o backend e abra:

- http://127.0.0.1:8000/#/doc/frinovsky-1939-04-11?idioma=pt
- http://127.0.0.1:8000/#/doc/frinovsky-1939-04-11?idioma=ru
- http://127.0.0.1:8000/#/doc/frinovsky-1939-04-11?idioma=en

Confira a fonte no cabeçalho/ficha. Procure a passagem sobre Roshal, clique na nota e teste o retorno. Confira a nota sobre os três sobrenomes e as notas finais sobre Belov. No inglês, confira o aviso do parágrafo acrescentado e a marca `55`. No russo, as grafias assinaladas acima devem permanecer. Exporte o Markdown e confira as chamadas/definições de notas.

O estudo por ordem de blocos não garante pareamento exato entre os idiomas; as diferenças de parágrafos e aparato estão documentadas e não foram escondidas para produzir contagens iguais.

A gravação e o histórico estão registrados em [receipt.json](receipt.json); a prévia está em [preview.json](preview.json). As versões anteriores podem ser recuperadas pelo histórico editorial. O renderizador Markdown do projeto confirmou dez notas e doze chamadas em cada idioma. Não houve teste de navegador, commit ou push nesta revisão; nada foi publicado automaticamente no GitHub Pages.
