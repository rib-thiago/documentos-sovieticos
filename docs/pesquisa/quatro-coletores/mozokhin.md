# Mozokhin — adaptação e piloto de fronteiras

Data: 20/10/2026. A coleção ainda não foi incorporada ao catálogo. Nenhum arquivo canônico, documento existente ou URL pública foi modificado nesta frente.

## Resultado desta rodada

- Adaptador reutilizável: `scripts/coletores/mozokhin/adapter.py`, sem dependências externas.
- Sete testes focados passaram: `python3 -m unittest discover -s scripts/coletores/mozokhin/tests -v`.
- Um ensaio adicional sobre o extrato real do meio removeu apenas o cabeçalho nº 108 em memória: nº 107 ficou bloqueado, nº 109 permaneceu independente e o último segmento continuou bloqueado. A fonte foi preservada. Resultado: `real-excerpt-gap-check.json` na área de trabalho.
- Zero livros integrais adquiridos; zero documentos prontos para incorporação; dez segmentos experimentais provenientes de extratos web, todos bloqueados por aquisição parcial.
- Piloto em três posições do livro I de 2013: início, meio e início do último documento. Também foi inspecionado o fim do corpo, notas e transição para o sumário.
- Edição de 2017 mantida como referência parcial; não transformada em 307 documentos supostamente coletados.

## Fontes e aquisição

Livro I: https://djvu.online/file/Cpto0fbsiVoGW

Livro II: https://djvu.online/file/B0n1vSjUG0odl

Referência parcial de 2017: https://djvu.online/file/j6lpXpwfotQwr

A tentativa HTTP direta do livro I, inclusive fora da restrição de rede do ambiente, recebeu HTML de aproximadamente 6 KB com desafio JavaScript de acesso; não recebeu o livro. A resposta foi preservada por hash, com diagnóstico em `temporario/coletas-quatro/mozokhin/access-blocked.json`. O desafio não foi executado nem contornado. Um retorno HTTP sem erro não é considerado aquisição bem-sucedida de texto.

A ferramenta de navegação disponibilizou vistas textuais limitadas. Elas foram preservadas em `web-excerpts/` com cabeçalhos e números de linha da ferramenta; cópias `.reader.txt` removem apenas o envelope `Lnnn:`. Essas cópias são **extratos de navegação, não HTML bruto, texto integral ou fac-símile**. Os metadados registram `input_kind: web_excerpt`, `fulltext_acquired: false` e `blocked_partial_acquisition`. A origem e a limitação também permanecem no inventário, evitando que uma fronteira aparentemente correta autorize sua publicação.

## Amostras e achados concretos

| Posição | Linhas da vista web | Cabeçalhos observados | Resultado |
|---|---|---|---|
| Início | 769–1116 | 1, 2, 3 | Fronteiras internas 1→2 e 2→3 detectadas; nº 3 interrompido no limite do extrato |
| Meio | 12137–12601 | 107, 108, 109, 110, 111, 112 | Nº 30411 não confundido com documento; nº 112 interrompido no limite |
| Último documento | 29095–29408 | 215 | Cabeçalho e início observados; texto com anexos continua além do extrato |
| Fim do corpo/sumário | 30572–30914 | Sumário a partir da linha 30798 | Notas editoriais finais precedem o sumário; não é seguro encerrar nº 215 logo depois da primeira comunicação |

O nº 109 apresenta lista/tabulação achatada pelo OCR. O adaptador não inventa colunas: preserva o texto e registra necessidade de conferir o fac-símile. Nos nºs 110–112, capturar duas linhas como título pode incluir saudação ou classificação documental; por isso o campo é `title_literal` com estado de sugestão não revisada, sem data/autoria inferidas automaticamente.

Nenhuma dessas amostras substitui a conferência de todo o livro, especialmente das notas e da ligação entre marcas e chamadas. Os dez segmentos experimentais permanecem bloqueados, inclusive aqueles com ambos os cabeçalhos internos observados. O resumo está em `temporario/coletas-quatro/mozokhin/pilot-summary.json`; candidatos e inventário no mesmo diretório.

## Correções implementadas

1. Todos os cabeçalhos observados delimitam segmentos; a ausência de nº 2 não impede localizar nºs 3 e 4.
2. Uma lacuna bloqueia o bloco anterior, pois ele pode conter material sem cabeçalho; não basta separar o próximo número e chamar o anterior de completo.
3. Cabeçalho precisa ocupar linha própria. Números internos como `No 108 от ...` e `No 30411` não viram documentos.
4. Numeração repetida ou regressiva é registrada, sem sobrescrever ocorrências.
5. O último segmento só recebe fronteira candidata se houver fonte declarada integral, último número esperado e marcador de sumário. Nenhum estado do adaptador equivale a revisão editorial aprovada.
6. IDs derivam do número efetivamente observado e da edição, nunca da posição de uma linha do catálogo EBID.
7. Fonte fornecida, Markdown candidato e versões anteriores são preservados por SHA-256; inventário cumulativo guarda todas as versões/ocorrências. Cada execução gera registro próprio.
8. Não há correções textuais silenciosas, reconstrução automática de tabelas ou remoção de notas.

## Como conferir manualmente

1. Abra o livro I no navegador e compare os nºs 1 e 2 com os candidatos em `candidates/mozokhin-2013-v1-001/` e `...-002/`.
2. Confira no nº 108 a fronteira até nº 109. No nº 109, examine a apresentação da lista antes de decidir como representar a tabela em Markdown.
3. Abra o nº 215 e avance até o fim do corpo, antes do sumário. O piloto contém apenas seu início: não publicá-lo como texto completo.
4. Abra `inventory.json` e confirme que todos os dez itens estão bloqueados e marcados como aquisição parcial.
5. Para continuar a coleta real, forneça HTML/texto integral obtido por acesso normal, ou um arquivo local disponível, e use o comando do README do adaptador. PDF passa pela extração/OCR já existente; DjVu precisa de extração/conversão específica. Não marcar `--complete` antes de conferir a integralidade.

## Pendências antes da incorporação

- **Alta:** obter as duas fontes integrais por acesso normal, preservando arquivo e proveniência; não usar o desafio de acesso como fonte documental.
- **Alta:** conferir cabeçalhos, lacunas, anexos e notas ao longo dos dois livros; validar início/meio/fim do livro II, ainda não adquirido nesta rodada.
- **Alta:** reconstruir e revisar as tabelas afetadas pelo OCR, começando pela lista do nº 109; conferir contra imagens.
- **Média:** ligar títulos/cotas do catálogo às identidades observadas no livro, sem renumerar pela posição do catálogo.
- **Média:** conciliar com acervo existente por referência arquivística, título, data e conteúdo; só então criar associações/reutilizar documentos.
- **Média:** revisão editorial dos títulos, datas, pessoas e créditos; a descrição de alegações permanece atribuída às fontes.
- **Futura:** conciliação da edição 2017 com 2013; diferenças de 295/307 não provam doze documentos novos.
