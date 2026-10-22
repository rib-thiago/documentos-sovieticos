# Brest-Litovsk — recuperação pelo Wayback, 21/10/2026

As seis fontes russas foram recuperadas como HTML bruto arquivado. Foram preparadas 11 unidades em Markdown, com proveniência por captura. **Ainda não incorporadas no catálogo do site.** Sem commit ou push desta rodada.

## Capturas preservadas

| Fonte | Captura Wayback (UTC) | URL |
|---|---|---|
| iskra-primeira-sessao | 2018-05-14 05:22:47 | [Captura](https://web.archive.org/web/20180514052247id_/http://iskra-research.org:80/USSR/Brest/1917-12-22.shtml) |
| iskra-27-dez | 2021-10-27 16:59:32 | [Captura](https://web.archive.org/web/20211027165932id_/https://iskra-research.org/USSR/Brest/1917-12-27.shtml) |
| iskra-jan-11 | 2021-10-27 17:25:56 | [Captura](https://web.archive.org/web/20211027172556id_/https://iskra-research.org/USSR/Brest/1918-1-11.shtml) |
| iskra-fase-2 | 2021-10-27 16:14:46 | [Captura](https://web.archive.org/web/20211027161446id_/https://iskra-research.org/USSR/Brest/1918-2.shtml) |
| iskra-jan-31 | 2021-10-27 16:11:24 | [Captura](https://web.archive.org/web/20211027161124id_/https://iskra-research.org/USSR/Brest/1918-1-31.shtml) |
| iskra-mar-1 | 2021-10-27 16:59:00 | [Captura](https://web.archive.org/web/20211027165900id_/https://iskra-research.org/USSR/Brest/1918-3-01.shtml) |

A API de disponibilidade `archive.org/wayback/available` deu timeout. O índice CDX de `web.archive.org` e as capturas `id_` funcionaram. Original solicitado, original arquivado, URL final, timestamp, resposta CDX e SHA-256 estão registrados. O CDX foi consultado com colapso por URL; não afirmamos ter escolhido a captura mais recente disponível.

## Unidades e fronteiras

| Unidade | Título |
|---|---|
| `brest-iskra-primeira-sessao` | Sessão plenária de 22/9 de dezembro de 1917 |
| `brest-iskra-27-dez` | Comissão Política — sessão de 27/14 de dezembro de 1917 |
| `brest-iskra-jan-11-manha` | Comissão Política — sessão da manhã de 11 de janeiro de 1918 |
| `brest-iskra-jan-11-tarde` | Comissão Política — sessão da tarde de 11 de janeiro de 1918 |
| `brest-iskra-fase-2-apresentacao` | Segundo período das negociações — apresentação editorial da fonte |
| `brest-iskra-fase-2-ioffe` | Segundo período das negociações — nota de A. Ioffe, abril de 1919 |
| `brest-iskra-fase-2-delegacoes` | Segundo período das negociações — composição das delegações |
| `brest-iskra-jan-31` | Comissão Política — sessão de 31 de janeiro de 1918 |
| `brest-iskra-mar-1-manha` | Sessão plenária da manhã de 1º de março de 1918 |
| `brest-iskra-mar-1-tarde` | Sessão plenária da tarde de 1º de março de 1918 |
| `brest-iskra-mar-1-presidentes` | Reunião dos presidentes das delegações de 1º de março de 1918 |

São oito transcrições de reuniões, dois textos editoriais e uma lista de delegações. A sessão de 27 de dezembro preserva também sua nota introdutória assinada por Ioffe em abril de 1919; ela não muda a data histórica da sessão. A página de 11 de janeiro reúne manhã e tarde; a de 1º de março contém duas plenárias e uma reunião de presidentes. A página do segundo período foi separada entre apresentação editorial da fonte, nota assinada por Ioffe e composição das delegações. Não foi inferida autoria para a apresentação nem uma data de redação para a lista.

## Conversão e preservação

- O corpo específico `#mainContent` exclui a navegação lateral; o HTML bruto integral continua preservado.
- Títulos e subtítulos da fonte foram representados em Markdown. Notas editoriais inline foram mantidas como blocos de citação, sem inventar numeração ou atribuição de chamadas.
- As tabelas de uma linha com retrato e texto foram desfeitas apenas como estrutura de layout, preservando imagem, legenda e fala. A tabela de duas colunas da delegação alemã foi mantida como tabela.
- Imagens conservam links absolutos de origem; os arquivos das imagens não foram baixados. Não se promete visualização offline desses retratos.
- A fração tipográfica em “5½” passou a “5 1⁄2”, impedindo que a retirada de `<sup>` produzisse “51⁄2”. Não houve alteração do horário declarado.
- Comentários HTML de template foram excluídos, preservando o texto documental. Grafias da transcrição, nomes e alegações permanecem como na fonte.
- As 11 unidades têm cobertura integral dos tokens textuais do respectivo trecho, além da conferência de abertura, encerramento, notas e fronteiras. Essa verificação não equivale a cotejo filológico com o exemplar impresso.

## Arquivos e retomada

- `temporario/coletas-quatro/brest/wayback/result.json`: seis resultados de aquisição.
- `wayback/prepared.json`: unidades, contagens e transformações.
- `wayback/preparation-history/`: versões anteriores de `units.json`.
- `raw/01-negociacoes/`: snapshots brutos por SHA-256.
- `units/brest-iskra-*/`: candidatos individuais por hash.
- `scripts/coletores/brest/wayback.py`: aquisição reproduzível.
- `scripts/coletores/brest/prepare_iskra.py`: decisões de fronteira vinculadas aos hashes adquiridos.

O conjunto Brest passa de 74 unidades / 42 preparáveis para 79 unidades / 53 preparáveis. A diferença decorre de substituir seis páginas antes retidas por 11 unidades, sem duplicar as páginas agregadas como documentos adicionais. Os 26 outros casos retidos de Brest permanecem retidos.

O registro anterior de seis falhas ao vivo continua verdadeiro como histórico. As falhas não foram apagadas: metadados anteriores foram preservados pelo coletor. A recuperação arquivada resolve a aquisição, sem afirmar que o acesso ao site atual voltou a funcionar.

## Conferência manual

Abrir uma captura acima e o Markdown correspondente em `units.json`. Conferir as duas sessões de 11 de janeiro, as três reuniões de 1º de março e as três partes da apresentação do segundo período. Na ata de 31 de janeiro, conferir “5 1⁄2”; na lista de delegações, conferir a tabela alemã. As unidades ainda não têm URLs novas no site, pois a próxima operação é preparar e incorporar um lote incremental com histórico, sem reaplicar o pacote inicial.

Não foram executados testes automatizados nem testes de navegador. Aquisição, comparação textual e preparação são operações sobre as fontes. Nenhum documento, tradução ou URL do acervo ativo foi regravado.
