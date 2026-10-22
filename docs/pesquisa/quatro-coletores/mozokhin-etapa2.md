# Mozokhin — fontes integrais recuperadas e preparação dos 295 documentos

Data: 20/10/2026. Esta etapa supera o bloqueio de aquisição do primeiro piloto. **Não houve incorporação no acervo, commit ou push.** O relatório anterior continua descrevendo corretamente o piloto inicial, cujos dez extratos web permanecem bloqueados no histórico.

## Resultado

| Fonte de 2013 | Páginas físicas do PDF | Documentos numerados | Candidatos para prévia de importação | Bloqueados para revisão |
|---|---:|---:|---:|---:|
| Livro I | 514 | 215, nºs 1–215 | 174 | 41 |
| Livro II | 437 | 80, nºs 216–295 | 65 | 15 |
| Total | 951 | 295 | 239 | 56 |

Os 295 títulos/números foram cotejados automaticamente entre sumário impresso e cabeçalhos no corpo. Não há lacunas de numeração. Foram descartadas como fronteiras dez ocorrências internas numeradas no livro I; o texto dessas ocorrências permanece dentro dos respectivos documentos, e cada descarte está registrado com posição e motivo. Não foi feita revisão humana integral dos 951 fac-símiles: `ready_for_import` significa candidato tecnicamente apto à prévia, não edição crítica revisada.

## Aquisição verificável

A página [Партийное строительство](https://wr-nsk.ru/partijnoe-stroitelstvo/) oferece links normais aos dois PDFs:

- [Livro I, PDF](https://wr-nsk.ru/wp-content/uploads/2023/04/politbyuro-i-lev-troczkij-1-2013.pdf): 9.811.024 bytes, 514 páginas.
- [Livro II, PDF](https://wr-nsk.ru/wp-content/uploads/2023/04/politbyuro-i-lev-troczkij-2-2013.pdf): 7.867.730 bytes, 437 páginas.

Ambos foram adquiridos por HTTP normal com resposta 200, assinatura PDF verificada, sem criptografia. Não foi contornado o desafio do DjVu Online. A página de descoberta, as fichas EBID consultadas e os PDFs estão preservados por SHA-256; URLs, estados, hashes e caminhos estão em `temporario/coletas-quatro/mozokhin/access-map-stage2.json`.

As fichas RSL confirmam a bibliografia, mas a presença de texto genérico de modal “leitura livre” sem link funcional não foi tratada como prova de PDF integral acessível. A edição de 2017 permanece referência parcial e não foi usada como fonte substituta.

Os PDFs têm camada de texto pesquisável, produzida anteriormente com ABBYY FineReader. Foi usado Poppler `pdftotext -layout` e `-bbox-layout`, **sem executar novo OCR**. Erros do OCR existente não foram corrigidos silenciosamente. PDFs físicos, paginação impressa e datas dos documentos são conceitos distintos; o ano 2013 é o da edição.

## Correções motivadas pelos documentos reais

1. **Quebras de página:** cabeçalhos precedidos de form feed agora são reconhecidos. Antes, seriam perdidos 45 números do livro I e 19 do livro II.
2. **Referências internas:** números como “№ 40” dentro de uma transcrição não são automaticamente novos documentos. Títulos vinculados aos números do sumário permitem distinguir essas referências dos cabeçalhos. Correspondência ambígua continua bloqueada.
3. **Fronteira final do livro II:** o comentário nominal de cerca de quarenta páginas começa depois do nº 295 e antes do sumário. O adaptador reconhece `ИМЕННОЙ КОММЕНТАРИЙ16` e mantém esse apêndice fora do nº 295. O apêndice continua integralmente preservado no PDF e na extração completa.
4. **Notas atravessando fronteiras:** na página PDF 388 do livro II, a nota 13 pertence ao nº 294, mas seu rodapé aparece depois do cabeçalho nº 295. Esses documentos estão bloqueados para revisão; não houve realocação silenciosa. A detecção geométrica de notas pequenas e de tabelas bloqueou 56 documentos no conjunto.
5. **Tabela do nº 109:** lista multicoluna identificada no primeiro piloto continua bloqueada. A camada OCR não preserva sua estrutura suficiente para uma reconstrução automática segura.

As regras de notas e tabelas são triagem conservadora, não garantia de que todos os problemas tipográficos foram detectados. A extração preservada permite recuperar qualquer passagem; os candidatos ainda podem conter rodapés numéricos ou quebras de linha a revisar.

## Saídas e reprodução

- `scripts/coletores/mozokhin/prepare_books.py`: preparação reproduzível a partir dos dois PDFs locais.
- `scripts/coletores/mozokhin/sources.json`: endereços de descoberta e PDF incorporados à configuração durável.
- `temporario/coletas-quatro/mozokhin/units.json`: lista de 295 unidades, com IDs estáveis, títulos literais, idioma, subcoleção, Markdown/hash, PDF/hash, aptidão para prévia, pendências e proveniência.
- `v1-preparation.json` e `v2-preparation.json`: contagens, `pdfinfo`, fronteiras rejeitadas e unidades por livro.
- `extracted/`: extrações completas `-layout` e `-bbox-layout`, nomeadas pelo hash do PDF.
- `v1-footnote-markers.json` e `v2-footnote-markers.json`: pistas geométricas de notas, sem atribuição automática ao documento errado.
- `facsimile-checks/`: oito páginas renderizadas e inspecionadas: livro I páginas PDF 17, 189, 476 e 502; livro II páginas PDF 4, 205, 388 e 390.

Os caminhos dos arquivos em cada unidade são relativos à frente `temporario/coletas-quatro/mozokhin/`; `provenance.extracted_text` também. O campo `raw` aponta ao PDF integral, nunca a extrato de navegação. Os títulos portugueses permanecem vazios: não foram inventadas traduções nem autoria/data derivadas da posição no catálogo.

```bash
python3 scripts/coletores/mozokhin/prepare_books.py \
  --volume-1 /caminho/livro-1.pdf \
  --volume-2 /caminho/livro-2.pdf \
  --output temporario/coletas-quatro/mozokhin
```

Doze testes focados passaram:

```bash
python3 -m unittest discover -s scripts/coletores/mozokhin/tests -v
```

Também foram verificados 295 IDs únicos, existência de todos os Markdown e PDFs, correspondência dos hashes dos candidatos e das duas fontes, e bloqueio dos nºs 294/295. Nenhum teste geral do site foi executado nesta frente.

## Conferência manual recomendada

1. Abra `units.json`; filtre `ready_for_import: false` para os 56 casos e leia os motivos.
2. Confira os nºs 1, 108 e 215 no livro I; nºs 216, 255 e 295 no livro II. O nº 215 inclui anexos até a página impressa 501, não apenas a comunicação inicial.
3. Na página PDF 388 do livro II, confira a chamada 13 no nº 294 e sua nota no rodapé, já abaixo do início do nº 295. Essa atribuição precisa ser resolvida antes de incorporar os dois.
4. Confira o nº 109 contra suas imagens e reconstrua a tabela na edição local, mantendo o PDF como testemunho.
5. Antes da gravação canônica, concilie duplicatas/cotas com as coleções existentes. A prévia de 239 candidatos não significa autorização de publicação automática ou revisão crítica encerrada.
