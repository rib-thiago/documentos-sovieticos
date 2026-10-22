# Svitlana/Erdogan — conclusão da aquisição, rodada 3

Data: 21/10/2026. Escopo: concluir as URLs descobertas nos índices preservados,
sem gravação no catálogo público. Não é declaração de completude de todo o site
de origem nem revisão filológica das traduções inglesas.

## Resultado

| Medida | Total |
| --- | ---: |
| URLs de páginas no inventário | 779 |
| Páginas adquiridas com HTML e Markdown preservados | 779 |
| URLs nunca tentadas | 0 |
| Falhas sem aquisição | 0 |
| Unidades candidatas emitidas | 780 |
| Unidades com decisão estrutural anterior válida | 13 |
| Unidades retidas para conferência | 767 |

A rodada partiu de 234 páginas adquiridas e acrescentou 545 aquisições.
As 13 decisões estruturais anteriores permanecem válidas, com os mesmos IDs e
hashes Markdown; nenhuma aprovação nova foi atribuída automaticamente.
O arquivo `SVITLANA-RODADA3.json` registra esses hashes e as contagens.

## Limitações que continuam relevantes

Aquisição bem-sucedida não significa texto documental integral: 24 páginas são
envoltórios de PDF e continuam como referências, sem considerar adquirido o texto
do PDF. Há 44 corpos curtos que exigem distinguir cabeçalhos/avisos de documentos.
21 páginas sinalizam tabelas complexas; 561 usam extração genérica do corpo.
As categorias se sobrepõem. Notas, tabelas, fronteiras, autoria, crédito individual
da tradução e possíveis duplicatas continuam dependendo de revisão por unidade.

As novas páginas permanecem na área de trabalho e não foram importadas.
`units.json` conserva todas as pendências e referências aos snapshots; nenhum
original, tradução pública ou URL do acervo foi alterado por esta rodada.

## Execução e recuperação

A rede restrita falhou ao resolver DNS; a coleta prosseguiu com acesso à rede
autorizado. Uma sessão longa recebeu SIGTERM externo, sem perder checkpoints.
As falhas transitórias iniciais se recuperaram na retomada; não havia falhas
restantes ao fim, dispensando rodada adicional de repetição.

Foi adicionada a opção `--unattempted` ao coletor: seleciona apenas URLs sem
tentativa anterior e permite lotes de 80 sem repetir falhas entre lotes.
Mantidos intervalo mínimo por host, conferência de robots.txt e snapshots
imutáveis. Apenas um processo escreveu o inventário em cada momento.

Comando usado nos lotes finais:

```sh
python3 scripts/coletores/svitlana/collect.py --documents --sources all --limit 80 --balanced --unattempted --timeout 20
python3 scripts/coletores/svitlana/build_units.py
```

Sem testes, commit ou push. A conferência descrita acima é uma comparação de
inventário, decisões e hashes existentes, sem nova aprovação editorial.
