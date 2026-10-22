# Onda 1 — índice tabular da sessão de 15 de janeiro de 1935

Lote `R1-tabelas_imagens-0024`; documento `showtrials-2644`. Entrega preparada fora do acervo, sem gravação canônica, testes de suíte/navegador, commit ou push.

## Resultado

A tabela inicial foi reconstruída em candidatos russo, português e inglês. O HTML preservado contém **24 linhas × 4 colunas = 96 células**, seis vazias: cabeçalho, 19 acusados, uma linha divisória «СВИДЕТЕЛИ» e três testemunhas. Não há mesclas. As células vazias da divisória e das últimas palavras das testemunhas foram mantidas. A separação em quatro colunas recupera a relação entre pessoa, página do interrogatório e página das últimas palavras; os números são paginação da fonte, não números de parágrafos do site.

Cotejo: todos os 96 campos russos foram confrontados com o HTML, incluindo nomes e cabeçalhos; os campos numéricos de PT/EN foram conferidos com as mesmas linhas da fonte. Os nomes e cabeçalhos traduzidos permanecem literalmente como nas traduções existentes; isto **não constitui revisão linguística integral** dessas versões. Todos os trechos fora da tabela permanecem byte a byte iguais e na mesma ordem. Nenhuma nota, título ou passagem do corpo foi reescrita. O primeiro cabeçalho ocupa dois parágrafos na versão linearizada; na tabela eles são unidos por `<br>`.

A receita registra os textos e os atributos/destinos originais de cada célula. Os hiperlinks não foram restaurados nesta operação estrutural; a chave própria de links continua aberta para cotejo sequencial dos 1.022 destinos da fonte. Não se presume que toda ligação externa seja nota ou que todos os links possam ser convertidos em destinos locais.

## Ressalvas preservadas

- TARASOV: página de últimas palavras **807**, exatamente como no HTML e nas três edições. Não foi emendada por plausibilidade para outra centena.
- SAKHOV: o HTML apresenta `<a …>21</a>1`, que forma visualmente `211`. A conversão anterior separou os fragmentos como `21 1`. O candidato preserva esse texto herdado, em vez de alterar silenciosamente o número ou o destino (o link original remete à sessão de 16 de janeiro). A relação documental e a tipografia dessa célula ficam discriminadas na evidência; eventual normalização deve ser explícita.
- O título de coluna `Стр<аница>` mantém os sinais editoriais, escapados em Markdown, não é convertido em elemento HTML.

## Blocos, sessões e citações

| Idioma | Blocos antes → depois¹ | Títulos preservados | Prefixo / sufixo byte-idênticos |
|---|---:|---:|---:|
| RU | 1.385 → 1.295 | 14 | 1.237 / 538.552 bytes |
| PT | 1.388 → 1.298 | 15 | 1.032 / 318.893 bytes |
| EN | 1.388 → 1.298 | 15 | 1.021 / 308.109 bytes |

¹ Contagem de blocos não vazios separados por linhas em branco, incluindo cabeçalhos de exportação já existentes; não é promessa da numeração renderizada do leitor. Em cada idioma, os 91 blocos da tabela viram um bloco, diferença de −90 para os blocos posteriores. As traduções possuem cabeçalho de exportação adicional; não foi forçado pareamento entre idiomas nem removido esse cabeçalho.

`assets/app.js` usa o índice salvo acompanhado de impressão do texto e procura o texto quando o índice muda. Passagens inalteradas posteriores têm como ser reencontradas, mas marcas antigas em células curtas (por exemplo `262` ou `1.`) podem corresponder a outro bloco idêntico. O preparador não acessa o armazenamento de sessão do navegador e **não afirma ter migrado esses marcadores**. Não reutilizar índices antigos cegamente. A transformação estrutural também muda as referências provisórias `§` posteriores.

O JSON registra offsets Unicode antes/depois, o delta aplicável ao sufixo inalterado e o intervalo substituído. Correções persistentes de trecho, associações PDF e rascunhos devem ser conferidos pelo integrador antes da gravação. Um vínculo dentro da tabela exige decisão específica; para o sufixo, preservar o conteúdo literal e revalidar os hashes/offsets é condição necessária. Não editar o banco ou migrar associações neste preparador.

O modo estudo atual agrupa a tabela Markdown como um bloco; sua renderização visual não foi verificada em navegador. A futura restauração de links trabalhará sobre os hashes pós-integração.

## Artefatos e estados

- Receita: `scripts/revisao_acervo/prepare_2644.py` (recusa fonte ou edições com hash diferente).
- Pacote: `temporario/revisao-onda1/tabela2644/`.
- `result.json`: hashes de entrada/saída, arquivos candidatos, equivalência exterior, contagens e offsets.
- `source-table.html` e `source-cells.json`: tabela literal e 96 células, URLs e atributos preservados.
- `{ru,pt,en}-cells.json`: textos das células de cada candidato.
- Três candidatos Markdown e três diffs: só substituem a região tabular.

Chave `showtrials-2644:tabelas_linearizadas`: candidato **corrigido com evidência**, pendente de integração e avaliação dos vínculos. Chave `showtrials-2644:links_nao_reconstruidos`: **parcial**, permanece aberta; os destinos da tabela foram inventariados como evidência, não restaurados.

Conferência manual após integração: abrir o documento em cada idioma, verificar as quatro colunas e a divisória de testemunhas, especialmente TARASOV/807 e SAKHOV/`21 1`; verificar o primeiro parágrafo após o índice e os títulos posteriores; alternar leitura/estudo e conferir novas marcações. Marcas anteriores dentro da tabela não devem ser consideradas migradas.
