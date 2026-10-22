# Notas e tabelas — Sakharov / Mozokhin

21/10/2026. Esta frente modifica apenas candidatos na área de trabalho. Catálogo público, textos publicados, traduções existentes, commit e push não foram alterados por esta frente. Não foram executados testes.

## Resultado

| Frente | Resultado desta revisão |
| --- | --- |
| Sakharov | Quatro extratos ingleses com 14 notas supridas em suplemento editorial identificado, tradução inglesa e russo literal; prontos para prévia. |
| Mozokhin | 53 das 54 unidades retidas passaram à prévia; uma continua retida. Quatro candidatos anteriormente aptos também receberam correções de atribuição de notas. Total atual: 294 de 295 aptos à prévia. |

“Apto à prévia” significa que a pendência estrutural desta triagem foi resolvida; não significa revisão integral dos erros lexicais do OCR ou avaliação histórica das afirmações.

## Sakharov

`restore_editorial_notes.py` conserva integralmente a fonte inglesa e acrescenta uma seção explicitamente editorial. As 14 notas em inglês não são atribuídas ao tradutor do texto adquirido. O russo literal e sua proveniência acompanham cada nota. Foram conferidos o sentido das referências bibliográficas e os antecedentes de `Ibid.`; as expansões são identificadas como editoriais. A nota 1066 depende do contexto russo da página de navegação 29, mesmo aparecendo na 30, e isso está registrado. A tradução descritiva de título bibliográfico não afirma a existência de uma edição inglesa.

Foi corrigida uma inconsistência técnica: o hash do Markdown já estava atualizado em `hashes.markdown_sha256`, mas permanecia antigo no campo superior `markdown_sha256`, usado pela prévia. A receita agora sincroniza ambos inclusive em execução idempotente. Os quatro arquivos reais correspondem aos dois campos. Isso não mudou o texto dos suplementos.

Unidades: `sakharov-2003-en-nav-10`, `-11`, `-12`, `-13`. Decisão: `temporario/coletas-quatro/sakharov/reviewed/sakharov-editorial-notes-20261021/decision.json`.

## Mozokhin: como foram resolvidas as fronteiras

O rodapé muitas vezes estava dentro do documento seguinte, apesar de a chamada pertencer ao anterior. Foram conferidas as páginas renderizadas do PDF e realocadas definições para seus donos. Chamadas/definições receberam sintaxe de notas Markdown; os fólios isolados foram removidos apenas nas páginas efetivamente revistas. Grafias e alegações do OCR foram conservadas. Ruídos `г-р`/`-г-` foram retirados das definições 20 e 59 após comparação com a imagem, com registro expresso nas receitas.

A revisão também encontrou casos fora da triagem inicial:

- Nota 29: definição no nº 54, chamada no nº 52.
- Nota 40: definição no nº 102, chamada no nº 101.
- Notas 53/54: definições no começo do nº 147, pertencentes aos nºs 145/146.
- Nº 31: três notas com asterisco, além das notas 19–21. Foram atribuídos identificadores Markdown distintos aos três asteriscos, preservando texto, ordem e atribuição.
- Nº 173: notas 60/61, além da 62 que havia caído no nº 174.
- Nº 153: nota 56, além da tabela.

**Incluir as atualizações dos nºs 54, 101, 145 e 146 na próxima prévia**, pois eram candidatos anteriormente aptos e já podem existir no catálogo. Sem essas atualizações, as chamadas dos documentos donos continuariam sem as definições realocadas.

As notas 35 e 36 imprimem números diferentes para o mesmo número de jornal: `(2469)` e `(3469)`. As duas leituras da fonte foram conservadas; não houve harmonização silenciosa. Também foi conservada a indicação do nº 109 de enviar Piatakov à “Австралия”, tal como impressa; não foi corrigida por plausibilidade histórica.

Os nºs 294/295, já conferidos na rodada anterior e congelados para o lote inicial, não foram modificados.

## As seis sinalizações de tabelas

| Unidade | Diagnóstico e tratamento |
| --- | --- |
| nº 100 | Tabela real e extensa, **continua retida**; detalhes abaixo. |
| nº 109 | Tabela de 41 linhas reconstruída em quatro colunas; linhas quebradas 2, 32, 35 e 40 reunidas na célula correta, conferidas na página PDF 190. Nota 42 atribuída ao documento. Grafias do OCR não foram modernizadas. |
| nº 138 | Falso positivo: espaços da composição em caixa alta, nas páginas PDF 264/266, não eram colunas de tabela. Texto conservado. |
| nº 142 | Tabela comparativa pequena da página PDF 285 reconstruída; valores e a expressão intermediária “им противостоят” preservados. Cabeçalhos descritivos de coluna adicionados editorialmente, registrados na proveniência. |
| nº 153 | Tabela de seis regiões e três colunas numéricas reconstruída contra a página PDF 300; agrupamento original dos cabeçalhos explicitado, números preservados. Cabeçalho vazio da coluna de regiões mantido. |
| nº 280 | Falso positivo: prosa com letras e palavras espaçadas na página PDF 313. A nota 11, indevidamente inserida em sua abertura, foi transferida ao nº 278. |

### Pendência concreta: nº 100

A lista nominal ocupa as páginas PDF 174–180 em duas colunas. As notas 38/39 foram ligadas às posições 198 e 780: a fonte diz que as linhas estão retocadas; não é permitido inventar os nomes. As imagens 175 e 179 mostram essas duas posições; a imagem 180 mostra a sequência final.

A fonte impressa contém os rótulos `900`, `949` e `950`, e termina em `865` apesar da referência a 863 assinaturas. Esses números não foram renumerados. A relação possível entre 865 posições e duas linhas retocadas deve ser apresentada como observação editorial, não como correção automática da fonte. Há também anos vazios, nomes/anos com leituras OCR duvidosas e lacunas no extrato que exigem conferência integral da tabela. As notas foram resolvidas, mas **o documento permanece bloqueado para incorporação** até reconstrução e cotejo dessa lista; o texto bruto e o PDF permanecem completos.

## Preservação e reprodução

Área: `temporario/coletas-quatro/mozokhin/`.

- `units.json`: candidatos atuais com hashes reais e pendências.
- `facsimile-checks/round3/`: imagens das páginas usadas, mantidas junto às fontes.
- `reviewed/mozokhin-v1-notes-round3-20261021/` e `reviewed/mozokhin-notes-round{4,5,6}-20261021/`: snapshots de unidades anteriores, diffs e decisões por unidade, com imagens identificadas por hash.
- `scripts/coletores/mozokhin/notes-round{3,4,5,6}-recipe.json`: decisões exatas, vinculadas aos hashes da fonte e do candidato anterior.
- `resolve_notes_round3.py` aplica a primeira receita; `apply_note_recipe.py` aplica as seguintes em ordem. As receitas recusam candidatos ou PDFs diferentes e não escrevem no catálogo.
- Os scripts podem ser repetidos imediatamente de forma idempotente; para reproduzir toda a sequência, começar do snapshot anterior à rodada 3 e aplicar 3, 4, 5 e 6 em ordem. Uma receita antiga não deve ser reaplicada sobre a saída de uma rodada posterior.

`NOTAS-RODADA3.json` separa 53 unidades recém-aptas, quatro atualizações de candidatos anteriormente aptos e o único caso retido. `NOTAS-RODADA3-mozokhin.csv` oferece uma linha por documento envolvido. Hashes dos 295 candidatos foram comparados com seus arquivos, como conferência de integridade da preparação, sem executar testes do projeto.

## Conferência manual

1. Abrir o PDF russo e as imagens das páginas 53, 81, 93, 94 e 181; comparar chamadas e definições com as respectivas diferenças.
2. Conferir a tabela de nº 109 contra PDF 190 e as pequenas tabelas de nºs 142/153 contra PDF 285/300.
3. No nº 173, conferir notas 60/61 na PDF 356 e 62 na PDF 361; esta última estava dentro do documento seguinte.
4. Abrir os quatro extratos ingleses Sakharov e conferir a divisão entre texto adquirido e suplemento editorial. O russo literal permite conferir cada nota sem supor alinhamento dos parágrafos.
5. Na futura prévia de incorporação, incluir os quatro documentos donos já existentes (54, 101, 145, 146) e conferir que o nº 100 permanece excluído.
