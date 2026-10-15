# Documentos Soviéticos

Site estático de fontes primárias e ensaios históricos, em russo e em edições com traduções para português e inglês.

## Acervo

As edições de Bukharin/Astrov, Ryutin, Ordzhonikidze e Yezhov são acompanhadas pelo acervo ShowTrials: **2.179 documentos em russo**, organizados em nove coleções e 28 subcoleções.

- Processo do Centro de Leningrado: 175 documentos.
- Processo do Centro Moscovita: 426 documentos.
- Caso do Kremlin: 293 documentos.
- Processo de 19–23 de agosto de 1936: 515 documentos.
- Processo de 23–29 de janeiro de 1937: 482 documentos.
- Processo de 2–12 de março de 1938: 284 documentos.
- Trotsky: 31 documentos.
- Artigos do ShowTrials: 2 documentos.
- Documentos diversos: 5 documentos.

Um documento pode pertencer a várias coleções. As quantidades acima não devem ser somadas para obter o total do acervo.

Os títulos individuais do novo acervo permanecem em russo. Traduções podem ser acrescentadas por documento.

## Consulta local

Na raiz do projeto, execute:

```bash
python3 -m http.server 8000
```

Abra `http://localhost:8000/#/colecao/centro-de-leningrado`. Não é necessário instalar dependências para servir o site. As fontes do Google exigem internet; há fontes alternativas do navegador.

## Organização

- `data/manifest.json`: coleções, subcoleções, documentos e idiomas.
- `originais/`: textos carregados pelo leitor.
- `originais/showtrials/`: corpos importados, em texto UTF-8.
- `assets/app.js` e `assets/style.css`: navegação e leitura.
- `temporario/`: acervo de trabalho; não é uma dependência do site em execução.

Cada documento importado é registrado uma vez na lista global `documents` do manifesto. Coleções e subcoleções apontam para seus IDs em `document_ids`, na ordem da fonte. As quatro coleções editoriais anteriores mantêm seus documentos próprios. O ID `showtrials-N` conserva o identificador WordPress, permitindo múltiplos vínculos sem duplicar o texto.

Rotas de exemplo:

```text
#/colecao/centro-de-leningrado
#/colecao/centro-de-leningrado/subcolecao/investigacao
#/colecao/centro-de-leningrado/todos
#/doc/showtrials-2617?colecao=centro-de-leningrado&subcolecao=andamento
```

Os parâmetros opcionais `colecao` e `subcolecao` mantêm o caminho de retorno, inclusive quando o mesmo documento aparece em processos diferentes. Links antigos `#/doc/ID` continuam funcionando.

## Importação do ShowTrials

```bash
python3 scripts/import_showtrials.py CAMINHO_DO_PACOTE_PORTATIL
python3 scripts/check_showtrials.py CAMINHO_DO_PACOTE_PORTATIL
```

O importador cobre todas as 28 subcoleções do ShowTrials. A página geral da fonte é um índice e não é duplicada como coleção. Os nomes dos processos seguem o catálogo coletado, incluindo suas datas. Conserva ordem, IDs e URLs, remove apenas o cabeçalho técnico gerado pela exportação Markdown e copia o corpo byte a byte. Referências e notas presentes no corpo são mantidas. Datas WordPress não são apresentadas como datas históricas.

Os documentos importados usam `format: "text"`: o leitor preserva sinais e quebras de linha sem interpretar asteriscos ou abreviações entre sinais de menor/maior como Markdown ou HTML. As edições existentes continuam usando Markdown. Não são aplicadas políticas de segmentação para tradução.

**Reimportação:** arquivos locais diferentes da fonte interrompem a importação antes da escrita, para preservar revisões. Traduções e metadados de documentos já existentes têm precedência. Capas e descrições das coleções importadas são preservadas. As quatro coleções editoriais anteriores não são alteradas. Mudanças manuais nos títulos das coleções/subcoleções devem ser refletidas no mapeamento do importador antes de reimportar.

Para acrescentar uma tradução manualmente, inclua o arquivo e uma entrada em `languages` no documento correspondente. Para acrescentar a capa, preencha `cover` na coleção, seguindo os exemplos existentes.

## Publicação

O site pode ser servido pelo GitHub Pages a partir da raiz, sem compilação. A publicação deve incluir `index.html`, `assets/`, `data/` e `originais/`. A pasta `temporario/` e as exportações de trabalho não precisam ser publicadas.
