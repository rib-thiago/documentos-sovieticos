# Documentos Soviéticos

Site estático de fontes primárias e ensaios históricos, em russo e em edições com traduções para português e inglês.

## Acervo

Além das edições de Bukharin/Astrov, Ryutin, Ordzhonikidze e Yezhov, o site inclui o Processo do Centro de Leningrado: 175 documentos em russo, nas subcoleções Materiais da investigação (152), Andamento do processo (3), Caso de Piotr Nikolaev (10) e Outros documentos (10).

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

Cada documento é registrado uma vez em `documents`. As subcoleções apontam para seus IDs em `document_ids`, na ordem da fonte. O ID `showtrials-N` conserva o identificador WordPress, permitindo múltiplos vínculos sem duplicar o texto.

Rotas de exemplo:

```text
#/colecao/centro-de-leningrado
#/colecao/centro-de-leningrado/subcolecao/investigacao
#/colecao/centro-de-leningrado/todos
#/doc/showtrials-2617?subcolecao=andamento
```

O parâmetro opcional `subcolecao` mantém o caminho de retorno. Links antigos `#/doc/ID` continuam funcionando.

## Importação piloto

```bash
python3 scripts/import_showtrials.py CAMINHO_DO_PACOTE_PORTATIL
python3 scripts/check_showtrials.py CAMINHO_DO_PACOTE_PORTATIL
```

O importador cobre o Centro de Leningrado. Conserva ordem, IDs e URLs, remove apenas o cabeçalho técnico gerado pela exportação Markdown e copia o corpo byte a byte. Referências e notas presentes no corpo são mantidas. Datas WordPress não são apresentadas como datas históricas.

Os documentos importados usam `format: "text"`: o leitor preserva sinais e quebras de linha sem interpretar asteriscos ou abreviações entre sinais de menor/maior como Markdown ou HTML. As edições existentes continuam usando Markdown. Não são aplicadas políticas de segmentação para tradução.

**Reimportar regenera os textos e metadados dessa coleção.** Depois de iniciar revisões ou acrescentar traduções, adapte o importador antes de executá-lo novamente. As outras coleções e a capa eventualmente adicionada à coleção piloto são preservadas.

Para acrescentar uma tradução manualmente, inclua o arquivo e uma entrada em `languages` no documento correspondente. Para acrescentar a capa, preencha `cover` na coleção, seguindo os exemplos existentes.

## Publicação

O site pode ser servido pelo GitHub Pages a partir da raiz, sem compilação. A publicação deve incluir `index.html`, `assets/`, `data/` e `originais/`. A pasta `temporario/` e as exportações de trabalho não precisam ser publicadas.
