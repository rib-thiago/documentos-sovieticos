# Brest — PDF Soviet Foreign Policy, diagnóstico e extração

## O que foi adquirido

**Soviet Foreign Policy 1917–1980**, volume I: **1917–1945**, quarta edição revista e ampliada, sob edição de A. A. Gromyko e B. N. Ponomarev. Progress Publishers, Moscou, tradução inglesa de 1981. É uma história diplomática soviética com citações de fontes: **não é a coletânea documental Soviet Foreign Policy Documents** que aparece nas suas notas. Essa distinção evita incorporar narrativa dos organizadores como documento de 1918.

O PDF tem **505 páginas** e camada pesquisável preexistente criada pelo ABBYY FineReader PDF 15. Extração direta concluída em todas as páginas; nenhuma página ficou com menos de 30 caracteres não brancos. Não foi necessário executar OCR. A leitura de amostras mostra erros da camada existente (por exemplo `apiece` em vez de `a piece`, chamadas de notas concatenadas, hifens de fim de linha e nomes russos deformados). Portanto extração disponível não significa transcrição revisada.

SHA-256 do PDF: `08bfcf74e68f55fe19ebf21640b6c294b6b2fa46a5449a4cfd9aca4962192de1`.

O Poppler emite aviso repetitivo de tabela de linearização inválida, mas concluiu a identificação, extração das 505 páginas e renderização das duas amostras. O arquivo bruto foi preservado sem tentativa de reparo.

## Derivados locais úteis

Em `temporario/coletas-quatro/brest/pdf-study/`:

- `pages/pdf-0001.txt` a `pages/pdf-0505.txt`: texto por página, sem limpeza silenciosa.
- `pages.json`: ordinal PDF, paginação impressa esperada, contagens, hashes e caminhos.
- `full-layout.txt`: extração integral para pesquisa local, não publicada no catálogo.
- `sumario.txt`: PDF 7–10, páginas impressas 5–8.
- `capitulo-ii-brest.txt`: PDF 50–72, páginas impressas 48–70, capítulo completo sobre negociações e tratado.
- `capitulo-iii-desdobramentos.txt`: PDF 73–98, páginas impressas 71–96, intervenção e desdobramentos até novembro de 1918.
- `references.json`: doze localizadores de excertos/fontes citadas, com ação editorial e distinção entre citação, referência arquivística e narrativa.
- `facsimiles/pdf-0050-impressa-48.png` e `pdf-0069-impressa-67.png`: imagens para cotejo; primeira imagem conferida visualmente contra a extração, com título, texto e paginação legíveis.
- `extract_pages.py`: receita reproduzível de extração, usando utilitários Poppler existentes.

O deslocamento de paginação é **ordinal PDF = impressa + 2** nas páginas do corpo cotejadas. Algumas folhas não mostram número impresso; o ordinal PDF permanece a referência inequívoca. A coluna de página impressa é expressamente uma expectativa por deslocamento, não detecção individual certificada.

## Mapa de leitura e aproveitamento

| Conteúdo | Página impressa | Página PDF |
|---|---:|---:|
| Primeiro estágio das negociações | 48 | 50 |
| Exigências alemãs | 51 | 53 |
| Debate pela conclusão imediata da paz | 55 | 57 |
| Ruptura das negociações | 59 | 61 |
| Retomada das negociações | 61 | 63 |
| Conclusão do tratado | 65 | 67 |
| Guerra e paz no VII Congresso | 66 | 68 |
| Tratado suplementar com a Alemanha | 83 | 85 |
| Ruptura das relações e anulação | 93 | 95 |

As citações das negociações remetem à edição russa de 1920, páginas **7–10, 13, 28, 32, 68, 70–72, 92, 126, 130 e 213**. São úteis para cotejar Iskra e identificar lacunas de cobertura, mas não fornecem traduções integrais de cada sessão.

A referência mais promissora para ampliar o catálogo é o **registro taquigráfico do VII Congresso de 1962**, páginas **29, 79, 80 e 88**, contendo Bukharin, Sverdlov e Artem. O conjunto de discursos de Lenin já incorporado não equivale ao registro integral desse congresso. Outra pista é a carta **Hertling–Hindenburg, 7 de janeiro de 1918**, em coletânea alemã de 1929, volume II, p.129. A referência a radiograma de Czernin de 23 de fevereiro não oferece cota suficiente para declarar aquisição.

## Próxima ação editorial e limites

Usar os localizadores para obter as edições primárias completas e cotejar os documentos já existentes. Se forem exibidos excertos no futuro, rotulá-los como excertos de fonte citada por obra secundária, com página, tradução e contexto. A linguagem avaliativa da obra, inclusive alegações contra atores políticos, pertence aos autores dessa interpretação e não deve virar metadado factual dos documentos.

Não houve publicação do livro, criação de documentos canônicos, mudança nas unidades atuais, testes, commit ou push. As imagens e textos continuam na área de trabalho. A extração é insumo de revisão, sem pareamento automático de parágrafos.
