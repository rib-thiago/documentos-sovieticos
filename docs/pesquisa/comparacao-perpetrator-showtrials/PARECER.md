# Parecer para a futura importação

Comparação dos 95 Markdown Perpetrator2004 com as 2.179 edições russas ShowTrials do catálogo local (mesma quantidade do pacote original).

| Resultado da triagem | Arquivos |
| --- | ---: |
| Candidatos com coincidência quase integral | 11 |
| Outras sobreposições a revisar | 20 |
| Sem correspondência textual detectada | 64 |

Não há uma lista de exclusão automática aprovada. Correspondência histórica não implica equivalência editorial: notas, referências, documentos anexos e fronteiras podem diferir. Nenhum arquivo foi removido.

## Candidatos a aproveitar documentos existentes

Confira as notas e os trechos exclusivos antes de evitar um novo cadastro. Os percentuais medem sequências de palavras, não certificam igualdade.

| Perpetrator2004 | ShowTrials |
| --- | --- |
| Kremlin_Affair_12.md | `showtrials-5005` |
| Kremlin_Affair_13.md | `showtrials-5009` |
| Kremlin_Affair_14.md | `showtrials-5013` |
| Kremlin_Affair_16.md | `showtrials-9872` |
| Kremlin_Affair_19.md | `showtrials-1704` |
| Kremlin_Affair_3.md | `showtrials-4869` |
| Kremlin_Affair_4.md | `showtrials-4870` |
| Kremlin_Affair_6.md | `showtrials-4883` |
| Kremlin_Affair_8.md | `showtrials-4949` |
| Kremlin_Affair_9.md | `showtrials-4963` |
| CPSU_Classified_Letter_on_Trotskyite_Zinovievite_Bloc.md | `showtrials-5723` |

## Casos que exigem tratamento por partes

- `Bukharin_Confrontations.md`: sete candidatos, incluindo 8609, 8611, 8613, 8641 e 8530. É uma compilação; sua primeira peça é uma nota de Agranov de 28 de dezembro de 1935, diferente do início do interrogatório 8609. Não dispensar o arquivo inteiro.
- `Bukharin_Letter_April15_1937.md` × 8707: mesma carta com forte coincidência; o ShowTrials traz resoluções e notas adicionais. Conferir como versões da mesma peça.
- `Bukharin_Letters.md`: candidatos 8536, 8712, 8600 e 8719. Avaliar as cartas individualmente.
- `Radek_Pyatakov_Trial.md`: sete candidatos de diferentes partes do processo. Comparar e segmentar antes de importar.
- `Trial_Record_Kotolynov_et_al.md` e `Trial_Record_Khanik.md`: trechos correspondentes ao 2618, que é muito maior. Forte indício de excertos; conferir os limites.
- `TheUnknownKirov.md`: livro de Alla Kirilina com citações de documentos do acervo; as coincidências cobrem apenas cerca de 0,6% das sequências amostradas do arquivo. Não classificar o livro como redundante.

## Pendência urgente encontrada na conversão anterior

Em 19 arquivos há 876 marcadores de notas sem conteúdo na extração DocBook do antiword. Isso inclui os dois documentos de Tukhachevsky. O Markdown foi gerado, mas as notas precisam ser recuperadas ou conferidas nos arquivos Word antes da importação. O relatório anterior contabilizava sucesso técnico de conversão, não preservação integral; este diagnóstico detalha essa limitação.

Lista completa: [pendencias-notas.csv](pendencias-notas.csv). Os originais continuam intactos. Não foram alterados os textos ou as notas nesta análise.

## Uso dos registros

- [Inventário legível, com os IDs e percentuais](README.md).
- [Triagem dos 95 arquivos](triagem.csv): primeiro filtro da futura importação.
- [Correspondências por par de documentos](correspondencias.csv): uma linha por candidato.
- [Evidências e trechos coincidentes](comparacao.json).

Próxima decisão editorial: aproveitar os cadastros existentes nos casos confirmados, segmentar compilações e avaliar separadamente os 64 sem correspondência detectada. Ausência de coincidência pode decorrer de transcrição diferente, OCR ou falhas de extração; não equivale a ineditismo. Não houve alteração no catálogo, manifesto, busca ou URLs.
