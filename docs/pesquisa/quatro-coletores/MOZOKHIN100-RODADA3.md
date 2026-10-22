# Mozokhin nº 100 — reconstrução da lista nominal

> Atualização: o cotejo posterior resolveu a retenção estrutural. Consulte [a revisão da rodada5](MOZOKHIN100-RODADA5.md). O texto abaixo preserva o diagnóstico anterior.

## Resultado e decisão

O documento `mozokhin-2013-v1-100` continua **retido**. A estrutura da lista foi recuperada por coordenadas, mas isso não equivale a uma transcrição lexical integralmente revisada. Nenhum texto canônico, catálogo ou estado de incorporação foi alterado.

A reconstrução identifica **858 linhas físicas**, incluindo as duas linhas retocadas nas posições literais 198 e 780; portanto, 856 linhas com algum nome na camada textual. Não transformar esse resultado em “858 assinaturas históricas”: a carta declara 863 assinaturas, e a numeração impressa termina em 865. São três informações diferentes, mantidas explicitamente.

## Derivados de trabalho

Diretório: `temporario/coletas-quatro/mozokhin/lista100/`.

- `lista-por-coordenadas.ru.md`: tabela por página, com rótulos literais, nomes, anos, coluna/linha e alertas.
- `rows.csv` e `rows.json`: 858 registros em ordem de leitura, cada qual com página PDF, coluna, linha física, coordenadas e texto bruto.
- `diagnostic.json`: resumo e 53 linhas sinalizadas; uma linha pode ter mais de um alerta.
- `pages174-180.bbox.html`: palavras e coordenadas fornecidas por Poppler.
- `pages174-180.layout.txt`: extração de comparação com disposição espacial.
- `page-174.png` a `page-180.png`: fac-símiles consultados.

Script reproduzível: `scripts/coletores/mozokhin/reconstruct_lista100.py`. Lê apenas o extrato bbox e o PDF preservado e escreve exclusivamente neste diretório de trabalho. Não executar `prepare_books.py` para esta revisão.

Fonte: PDF volume 1, SHA-256 `e126b2104b4c2d0b508811388544d0556ecd727d62abe0daa7eafee7fbf0302d`.

## Método e limites

A camada textual possui colunas desalinhadas em algumas páginas, particularmente os anos no final da página PDF 179. Agrupar todas as palavras apenas pela coordenada vertical cria linhas falsas de anos. O derivado ancora cada linha no número da assinatura e associa as palavras próximas, separando esquerda e direita e respeitando as coordenadas reais das colunas de anos. A ordem é a coluna esquerda inteira, depois a direita, por página.

As sete imagens foram inspecionadas para cotejar a estrutura, os limites, as notas e as principais irregularidades de numeração. Isso **não** constitui cotejo letra por letra dos 856 nomes. O Markdown original e a versão corrigida da rodada 6 permanecem intocados; este arquivo de trabalho não pretende substituir a carta inteira.

| Página PDF / impressa | Linhas esquerda | Linhas direita | Localização de pendências |
| --- | ---: | ---: | --- |
| 174 / 173 | 39 | 39 | Direita: salto literal 72→74; ano vazio em 55. Lista começa após a assinatura de Smilga. |
| 175 / 174 | 75 | 75 | Esquerda: dois rótulos 128, salto 137→139. Direita, linha 44: `198` com nota 38, sem nome, retocada. |
| 176 / 175 | 77 | 77 | Esquerda, linha 42: `371` entre 270 e 272. Direita: saltos 308→310 e 346→348; linha 60: `468` entre 367 e 369. |
| 177 / 176 | 77 | 77 | Esquerda: `390` sem ponto, preservado no texto bruto; salto 394→396. Direita: salto 494→496; 516 contém `кандидат`, sem ano numérico. |
| 178 / 177 | 77 | 77 | Direita: salto 628→630. Demais vazios/leituras a conferir no CSV. |
| 179 / 178 | 75 | 75 | Direita: salto 774→776; linha 8: `780` com nota 39, retocada; linha 28: `900` entre 799 e 801. Baselines dos anos deslocadas, recuperadas por proximidade ao número. |
| 180 / 179 | 9 | 9 | Esquerda: `949` e `950` entre 848 e 851. Direita termina em `865`. Oito anos estão fragmentados em múltiplas palavras na camada textual. Fim da lista antes da referência РГАСПИ; nº 101 excluído. |

## O que os números significam

Oito saltos de uma posição aparecem na sequência: 73, 138, 309, 347, 395, 495, 629 e 775. Há um rótulo 128 duplicado. Há ainda cinco rótulos discrepantes em relação à sequência: 371 entre 270/272, 468 entre 367/369, 900 entre 799/801, 949 e 950 entre 848/851. Estes rótulos foram preservados, sem serem substituídos pelos números esperados.

A contagem estrutural `865 − 8 + 1 = 858` descreve as linhas visíveis dessa lista, considerando os cinco rótulos discrepantes como linhas existentes. **Não** autoriza inventar os oito nomes ausentes na numeração, nem concluir que faltam oito pessoas: pode haver erros da própria numeração. Tampouco permite explicar a declaração de 863 assinaturas apenas pelas duas linhas retocadas.

## Revisão ainda necessária

1. Conferir os nomes e anos contra as imagens em todas as 858 linhas, registrando correções como transcrição e mantendo as grafias da fonte.
2. Conferir 28 campos de ano vazios na camada textual, incluindo as duas linhas retocadas; não completar por contexto. Campo vazio não é necessariamente erro de OCR.
3. Conferir os oito anos fragmentados no lado direito da página PDF 180. O derivado conserva os espaços da camada textual em vez de produzir anos silenciosamente normalizados.
4. Conferir a carta introdutória nas páginas anteriores: este trabalho isolou apenas a lista; números de página e erros de OCR do texto corrido não foram corrigidos.
5. Na incorporação futura, manter nota editorial explícita sobre 863 declaradas / 858 linhas reconstruídas / último rótulo 865 e sobre as duas linhas retocadas.

As seis palavras excluídas da tabela pelo agrupamento são os dois rodapés de notas (`38 Строка заретуширована` e `39 Строка заретуширована`), registrados em `diagnostic.json` e reproduzidos como notas Markdown. Nenhum fragmento restante de nome foi descartado pelo método nesta extração.

Sem testes, commit ou push. Esta execução foi processamento e conferência de fonte, não teste de aplicação.
