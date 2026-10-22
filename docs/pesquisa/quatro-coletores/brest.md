# Brest-Litovsk — primeiro piloto

Data: 20/10/2026. Fontes e derivados em `temporario/coletas-quatro/brest/`.
Código e configurações autônomos em `scripts/coletores/brest/`.

## Resultado

Das 56 sementes, quatro foram selecionadas para aquisição. Três páginas foram
obtidas e convertidas, permanecendo candidatas sem revisão editorial concluída:

| ID | Idioma | Conferência e pendências |
|---|---|---|
| `lenin-jan-07` | Inglês | Título, expediente, teses numeradas e nota final preservados. O expediente distingue as datas das teses, acréscimo e introdução; não reduzir tudo à data da URL. |
| `lenin-pt-jan` | Português | Tradução identificada na fonte, com créditos, datas duplas e notas de rodapé e de fim de tomo. A equivalência com o inglês está proposta no inventário, sem alinhamento automático de parágrafos. |
| `kommunist-teses-abril` | Inglês | Editorial e teses preservados. O diagnóstico da fonte não encontrou saltos entre os parágrafos numerados; conferir a sequência e as fronteiras contra a edição indicada. |
| `iskra-primeira-sessao` | Russo | Aquisição bloqueada: consulta a robots.txt recebeu HTTP 403. Não há transcrição russa obtida neste piloto; não houve contorno do bloqueio. |

As outras 52 sementes continuam planejadas. Nenhuma delas foi anunciada como
texto obtido. A aquisição não equivale a incorporação no catálogo.

Fontes selecionadas:
- https://www.marxists.org/archive/lenin/works/1918/jan/07.htm
- https://www.marxists.org/portugues/lenin/1918/01/20.htm
- https://www.marxists.org/history/ussr/publications/kommunist/april01/theses.htm
- https://iskra-research.org/USSR/Brest/1917-12-22.shtml

## Correções aplicadas ao coletor

- Inventário cumulativo; planejamento ou lote parcial não apaga aquisições.
- Todas as ocorrências e subcoleções preservadas na deduplicação por URL.
- Snapshots de fontes e candidatos por hash; revisão em `md/` não é sobrescrita.
- Histórico de metadados e nova tentativa de fontes com erro.
- Reconversão offline, com verificação de hash e preservação da data de coleta.
- Links relativos resolvidos e navegação superior separada do conteúdo.
- Diagnóstico de tabelas, âncoras e saltos de numeração, sem correções silenciosas.
- Corrigido erro do código original que comparava bytes com o MIME em string,
  impedindo processar respostas HTML válidas.

Cinco testes focados passaram, além da coleta remota descrita acima. O backend
não foi alterado nem recebeu dependências: elas foram instaladas somente em um
ambiente isolado de coleta. Catálogo, originais, traduções e URLs permanecem intactos.

## Conferência manual

Abrir `inventario.json`, localizar os IDs acima e comparar `raw_path` com
`candidate_path`. `md_path` identifica a cópia de trabalho preservada; ela pode
diferir do candidato após uma melhoria de conversão. Não usar o campo como prova
de que o candidato mais recente já foi aprovado.

Conferir início e fim, expediente, datas e notas em ambas as versões de Lenin.
Em Kommunist, verificar o editorial, a sequência das teses e o fim do texto
contra a fonte e, quando disponível, a edição impressa. A próxima etapa deve
concluir a revisão e converter referências de notas em notas locais antes da publicação.
