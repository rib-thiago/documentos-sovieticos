# Mozokhin: adaptação conservadora de ingestão

O pacote importado permanece intacto em `temporario/proposta-coletores/coletor-mozokhin/`. Este adaptador usa somente Python padrão e produz candidatos em área de trabalho; não altera catálogo, manifesto, busca nem originais publicados.

Não atribui número documental pela posição do catálogo. Apenas cabeçalhos numerados efetivamente observados no corpo são candidatos. Uma lacuna bloqueia o segmento anterior, pois a ausência do cabeçalho pode ter fundido documentos. Número repetido/regressivo e fim sem fronteira comprovada também exigem revisão. Todos os extratos de ferramenta web ficam bloqueados para incorporação, independentemente das fronteiras internas.

## Uso com arquivo adquirido legitimamente

```bash
python3 scripts/coletores/mozokhin/adapter.py \
  --input /caminho/livro1.txt \
  --output temporario/coletas-quatro/mozokhin \
  --source-url https://djvu.online/file/Cpto0fbsiVoGW \
  --first 1 --last 215 --edition 2013-v1 --kind text
```

`--kind html` aceita apenas blocos OCR/pre explícitos, nunca o corpo inteiro da página. `--complete` só deve ser usado após verificar aquisição integral do livro. O fim do último documento exige também marcador de sumário ou comentário nominal; se não encontrado, permanece bloqueado. `--edition 2017` é recusado para segmentação: a edição disponível foi identificada como referência parcial.

Saídas: `raw/` com snapshots SHA-256 do arquivo fornecido; `candidates/` com Markdown versionado por hash; `runs/` com registro da execução; `inventory.json` cumulativo com todas as versões/ocorrências. Extratos web possuem proveniência `web_excerpt`: o snapshot é do extrato fornecido, **não HTML bruto nem livro integral**. Não editar derivados gerados: realizar revisão em outra cópia/fluxo editorial.

O texto OCR e suas quebras permanecem preservados. Não há reconstrução de tabelas, correção ortográfica silenciosa ou remontagem de notas. Títulos são sugestões literais das primeiras linhas, podendo conter saudação ou classificação; não são metadados finais. O adaptador pressupõe um único processo gravador por diretório.

## Verificação focada

```bash
python3 -m unittest discover -s scripts/coletores/mozokhin/tests -v
```

Casos: cabeçalho ausente, números internos falsos, sumário final, último extrato incompleto, numeração repetida, desafio de acesso, persistência cumulativa e bloqueio de extratos web. Relatório do piloto: `docs/pesquisa/quatro-coletores/mozokhin.md`.

## PDFs integrais localizados na segunda etapa

Em `https://wr-nsk.ru/partijnoe-stroitelstvo/` há links públicos diretos para os dois PDFs de 2013. Os endereços estão também em `sources.json`; não foi necessário contornar o desafio de djvu.online. Os PDFs adquiridos têm 514 e 437 páginas físicas e camada de texto pesquisável. O OCR existente pode conter erros: não foi executado novo OCR nem corrigido silenciosamente.

```bash
python3 scripts/coletores/mozokhin/prepare_books.py \
  --volume-1 /caminho/politbyuro-i-lev-troczkij-1-2013.pdf \
  --volume-2 /caminho/politbyuro-i-lev-troczkij-2-2013.pdf \
  --output temporario/coletas-quatro/mozokhin
```

Requer `pdfinfo` e `pdftotext` (Poppler), já disponíveis nesta máquina. O comando preserva os PDFs, extrai `-layout` e `-bbox-layout`, confere os números impressos e seus títulos contra o corpo e gera `units.json` para prévia. Não importa documentos. O número de página física do PDF não é o número impresso (exemplo: página PDF 17 contém página impressa 16 no livro I).

O sumário permite distinguir referências internas numeradas de verdadeiros cabeçalhos. Candidatos cujo título não encontre correspondência única permanecem bloqueados. Documentos com notas pequenas de rodapé detectadas por geometria, ou tabelas suspeitas, ficam bloqueados até revisão. A geometria é uma triagem conservadora; não comprova que todo erro de OCR/tabela/nota tenha sido detectado. Uma nota de documento anterior pode aparecer depois do cabeçalho do seguinte na extração: não é movida silenciosamente.

Os extratos web da primeira etapa permanecem bloqueados no inventário histórico. `units.json` desta segunda etapa referencia exclusivamente os PDFs integrais, não esses extratos.
