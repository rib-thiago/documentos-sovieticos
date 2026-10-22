# Continuação das quatro coletas — 21/10/2026

## Incorporação local concluída

Nesta continuação foram acrescentados **91 documentos e 93 versões linguísticas**, além da correção de notas em quatro versões existentes. O catálogo passou a **2.705 documentos e 3.837 versões**, preservando o acervo anterior, IDs e URLs. Catálogo, manifesto e busca foram atualizados nas transações. Não houve commit nem push nesta rodada.

| Lote | Documentos novos | Versões novas | Histórico recuperável |
|---|---:|---:|---|
| Iskra/Brest, Svitlana e Mozokhin | 16 | 16 | `20261021170901891656-f7f4322013df` |
| Notas Sakharov, Mozokhin e individualizações Brest | 75 | 77 | `20261021172633137876-22db7cf66c29` |
| Correção das notas Mozokhin 054, 101, 145 e 146 | 0 | 0 (quatro revistas) | `20261021172931544115-d005bfa87be7` |

Recibos: [primeiro lote](incremental-20261021-gravacao.json), [segundo lote](rodada3-20261021-gravacao.json), [correções](mozokhin-correcao-notas-20261021-gravacao.json). Os pacotes e fontes congeladas permanecem em `temporario/coletas-quatro/`; as versões anteriores estão no histórico editorial local.

## Estado e limites

A fotografia atualizada é [ESTADO-ATUAL.md](ESTADO-ATUAL.md), com motivos por unidade em [CSV](ESTADO-ATUAL.csv). Aquisição de URL, preparação de uma versão e incorporação ao catálogo são etapas distintas; uma página pode conter várias peças ou ser apenas um índice.

- **Sakharov:** 76 versões incorporadas; 14 registros estruturais não equivalem a textos faltantes. Os quatro extratos ingleses receberam suplemento editorial de notas, distinguido do texto da fonte. [Relatório](NOTAS-RODADA3.md).
- **Mozokhin:** 294 documentos incorporados. O nº 100 permanece retido: reconstrução disponível em Markdown/CSV/JSON com coordenadas; 858 linhas físicas e 53 linhas sinalizadas exigem cotejo de nomes, anos e numeração. [Relatório específico](MOZOKHIN100-RODADA3.md).
- **Brest:** 73 versões incorporadas. Permanecem variantes e atas em alemão, referências bibliográficas e fontes ainda sem peça documental integral. Não substituímos atas completas por discursos de Lenin. [Relatório documental](BREST-RODADA3.md).
- **PDF de política externa:** 505 páginas extraídas sem novo OCR. É historiografia de 1981, não a coletânea documental citada nas notas; foi classificado como referência no inventário de trabalho, com o inventário anterior preservado. Não foi publicado como fonte primária. [Extração e pistas](BREST-PDF-RODADA3.md).
- **Svitlana:** concluída a aquisição das **779/779 URLs inventariadas**, sem falhas pendentes. Foram emitidas 780 unidades: 13 já incorporadas com IDs e hashes preservados, 743 retidas para revisão e 24 referências/envoltórios de PDF. Entre as páginas há 44 corpos curtos e 21 tabelas complexas; as categorias se sobrepõem. As novas páginas precisam de separação e revisão antes de incorporação. Não foram publicadas automaticamente. [Relatório final](SVITLANA-RODADA3.md).

## Conferência manual

1. Iniciar `python3 -m backend` e abrir `http://127.0.0.1:8000/`.
2. Exemplos diretos: [Mozokhin 054](http://127.0.0.1:8000/#/doc/mozokhin-2013-v1-054), [relatório ao IV Congresso](http://127.0.0.1:8000/#/doc/brest-lenin-iv-relatorio), [extrato Sakharov](http://127.0.0.1:8000/#/doc/sakharov-2003-en-nav-10). Navegar pelas quatro coleções; conferir os documentos acrescentados listados nos recibos e as notas de Mozokhin 054, 101, 145 e 146.
3. Comparar início, fim, notas e tabelas com as fontes preservadas. As versões portuguesa e inglesa de Brest não receberam alinhamento automático de parágrafos.
4. Para as pendências, usar o CSV por unidade e os relatórios específicos; candidatos retidos ficam na área de trabalho, fora do catálogo.

Não foram executadas suítes de testes nem testes no navegador nesta continuação. Foram feitas validações transacionais, conferências de hashes/fontes e diagnóstico de chamadas de notas: nas 77 versões do segundo lote não ficaram chamadas Markdown sem definição. Isso não equivale a revisão crítica integral dos textos.
