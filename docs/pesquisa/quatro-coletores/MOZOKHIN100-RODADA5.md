# Mozokhin nº 100 — cotejo e liberação com ressalvas da fonte

> Incorporação concluída após esta revisão: histórico `20261021202407360792-27bacdd7df3d`. [Comprovante](mozokhin-100-rodada5-gravacao.json).

## Decisão

O candidato `mozokhin-2013-v1-100` foi liberado para incorporação. A carta e a lista foram cotejadas visualmente com as páginas físicas 171–180 do PDF preservado. O texto canônico, o catálogo e a fila editorial não foram alterados por esta revisão; a gravação será centralizada na incorporação.

Isso resolve a retenção por colunas entrelaçadas, anos fragmentados e falta de cotejo da carta. As divergências aritméticas impressas permanecem explicitamente documentadas, sem emenda conjectural.

## Resultado material

- Carta introdutória integral, com o cabeçalho e as duas assinaturas de Smilga; nenhum texto dos documentos 99 ou 101 foi incluído.
- Lista com **858 linhas físicas**, em sete tabelas Markdown, ordenadas por página e, em cada página, coluna esquerda seguida da direita.
- **863 assinaturas declaradas**, último rótulo impresso **865**. Não tratamos nenhum desses números como contagem corrigida dos signatários.
- Duas linhas retocadas, rótulos 198 e 780, mantidas sem nome e com as notas impressas 38 e 39.
- Referência `РГАСПИ. Ф. 17. Оп. 171. Д. 88. Л. 100–111. Подлинник. Машинопись.` preservada.

### Correções de extração efetivamente feitas

| Local | Antes, camada textual | Depois, conforme imagem |
| --- | --- | --- |
| PDF 177, direita, nº 539 | `МЕП А РЕЙШВИЛИ И.` | `МЕПАРЕЙШВИЛИ И.` |
| PDF 178, esquerda, nº 575 | `НИКОЛ АЙШВИЛЛИ А.` | `НИКОЛАЙШВИЛЛИ А.` |
| PDF 178, esquerda, nº 576 | `НИКОЛ АЙШВИЛЛИ С.` | `НИКОЛАЙШВИЛЛИ С.` |
| PDF 180, direita, nº 857 | `1 92 4` | `1924` |
| PDF 180, direita, nº 858 | `1 9 1 8` | `1918` |
| PDF 180, direita, nº 860 | `1 92 1` | `1921` |
| PDF 180, direita, nº 861 | `1 92 0` | `1920` |
| PDF 180, direita, nº 862 | `1 90 5` | `1905` |
| PDF 180, direita, nº 863 | `1 92 3` | `1923` |
| PDF 180, direita, nº 864 | `1 92 4` | `1924` |
| PDF 180, direita, nº 865 | `1 9 1 7` | `1917` |

No nº 516, `МЕЛЬНИКОВ кандидат` foi separado em nome `МЕЛЬНИКОВ` e observação literal `кандидат`. O ano continua vazio. A qualificação não foi convertida em ano ou incorporada ao sobrenome.

Na carta, retiramos os rodapés 170–172 do fluxo do texto e desfizemos o espaçamento de extração `л и ц .` → `лиц.` na página PDF 173. Os demais possíveis erros gramaticais e grafias da edição foram preservados: cotejo não é reescrita da fonte.

## Anomalias confirmadas e preservadas

Os campos de ano vazios correspondem ao fac-símile; não foram completados por contexto. A antiga contagem de 28 campos sem ano inclui as duas linhas retocadas e a linha com `кандидат`.

Os saltos, a duplicação do rótulo 128 e os rótulos discrepantes 371, 468, 900, 949 e 950 são visíveis na edição. Não renumeramos a tabela nem inventamos oito nomes para preencher saltos. A nota editorial no próprio Markdown distingue a declaração de 863, as 858 linhas e o término em 865.

Não foi possível recuperar os dois nomes retocados, e a documentação disponível não explica a diferença entre as contagens. Isso é uma limitação da fonte, explicitada ao leitor, e não exige reter toda a carta.

## Rastreabilidade e limites

- PDF SHA-256: `e126b2104b4c2d0b508811388544d0556ecd727d62abe0daa7eafee7fbf0302d`.
- Markdown anterior preservado: SHA-256 `c2e65f9e0c73c1bf8eee00c5134f635e6551ac82deed796a0774553188ed79fa`.
- Novo Markdown: SHA-256 `7c3d1399ffbb29b07feb5070044e0dcebe59787a731d339044b927f9fdb2c686`.
- Diretório de decisão: `temporario/coletas-quatro/mozokhin/reviewed/mozokhin100-round5-20261021/`.
- `unit-before.json`, `decision.json` com antes/depois das 858 linhas e `changes.diff` preservam o percurso.
- Subcotejo das 458 linhas nas páginas 175–177: `temporario/coletas-quatro/mozokhin/lista100/cotejo175-177.json`.
- Receita: `scripts/coletores/mozokhin/prepare_lista100_reviewed.py`, vinculada aos hashes do PDF, tabela e Markdown anterior. Uma segunda execução reconhece a decisão já aplicada e não reescreve a unidade.

O cotejo foi visual, usando fac-símiles de página inteira. Não fizemos investigação prosopográfica nem cotejo com o documento arquivístico original. Não substituímos caracteres duvidosos por formas históricas consideradas mais prováveis. A decisão não certifica a exatidão factual da lista.

## Conferência manual

Após a incorporação, procure `mozokhin-2013-v1-100` no catálogo local e confira:

1. A carta começa em «В Редакцию “Правды”» e termina com a assinatura anterior à lista.
2. A lista tem sete seções de página; o nº 55 está sem ano, o nº 198 tem nota 38 e o nº 780 tem nota 39.
3. O nº 516 separa nome e qualificação; a página final conserva 949/950, termina em 865 e exibe os oito anos agora contínuos.
4. A referência arquivística e a nota editorial sobre as contagens estão presentes.

Sem testes de aplicação, commit ou push. O processamento de fonte e o cotejo não executam a aplicação.
