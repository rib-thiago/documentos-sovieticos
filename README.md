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

A barra superior oferece um seletor com todas as coleções e indica a coleção atual. Na página de cada documento, o botão **Exportar Markdown** baixa a versão escolhida com o mesmo nome do arquivo no projeto, trocando apenas a extensão `.txt` por `.md` quando necessário. Edições já em Markdown mantêm o arquivo original; textos importados recebem título, fonte, ID e idioma. A exportação usa o texto completo carregado, independentemente do modo de leitura ou dos parágrafos expandidos.

## Modos de visualização

- **Leitura**: texto contínuo em um idioma, com seleção de versão nos documentos traduzidos. É o padrão inicial.
- **Estudo → Por parágrafo**: versão principal com botões para expandir os outros idiomas por bloco.
- **Estudo → Paralelo**: duas versões lado a lado; documentos trilíngues permitem escolher as colunas.

Documentos com um único idioma oferecem leitura contínua. O modo e o submodo escolhidos são lembrados pelo navegador; o idioma de leitura é lembrado por documento. A preferência antiga de Leitura/Paralelo não altera o novo padrão inicial. A exportação segue disponível nos dois modos e acompanha o idioma selecionado na leitura, com opção de escolher outra versão para baixar.

A leitura Markdown usa markdown-it com suporte a notas de rodapé e sanitização por DOMPurify. HTML bruto permanece desativado. Os textos `.txt` são apresentados como texto, preservando parágrafos, abreviações e sinais. As ferramentas de estudo mantêm a segmentação anterior; a leitura contínua independe do alinhamento entre idiomas. Nenhum arquivo de conteúdo é reescrito para alternar entre os modos.

As bibliotecas estão incluídas em `assets/vendor/`, com versões fixas e licenças. **Não é necessário npm, instalação ou compilação** para usar ou publicar o site. A procedência e os hashes estão em `assets/vendor/manifest.json`.

### Índice e marcador de leitura na sessão

Ao visualizar um documento, Leitura e os dois submodos de Estudo oferecem o menu **Índice e marcador** na navegação superior (**Marcador** nos textos sem títulos). Há um único painel expansível, com retomada e índice, sem um segundo dropdown interno. O menu fica oculto na página inicial e nas páginas de coleção. Fecha ao clicar fora, pressionar Escape ou selecionar uma seção/retomar a leitura. Seu estado é lembrado por documento na sessão da aba. O índice respeita a hierarquia dos títulos exibidos; em Estudo paralelo, acompanha o idioma da coluna esquerda. Seus links não alteram a rota do documento.

Clique ou toque em um parágrafo para marcar o ponto; uma **bolinha vermelha** indica a marca. Outro clique no mesmo trecho remove a marca; clicar em outro parágrafo a transfere. Também é possível usar Enter ou Espaço com o trecho em foco. Selecionar texto, seguir links e usar os controles de idioma não altera a marca. Rolagem e navegação pelo índice não a substituem automaticamente.

A marca fica em `sessionStorage`, por documento, com o idioma e o modo de visualização. **Retomar leitura**, dentro da barra, restaura o trecho, o idioma e o submodo em que foi marcado, expandindo a tradução quando necessário. O marcador funciona também nos TXT, sem inventar títulos ou converter conteúdo. No Estudo, a bolinha identifica o bloco correspondente.

Os dados ficam na sessão daquela aba; não são enviados ao servidor nem sincronizados entre dispositivos. A marca permanece disponível ao navegar entre textos ou recarregar a página na mesma aba. Ao retomar, o conteúdo do bloco é conferido para evitar saltos para outro trecho se o documento tiver sido alterado. Se o armazenamento estiver bloqueado, a interface informa a impossibilidade de salvar. As posições antigas gravadas automaticamente continuam reconhecidas até serem removidas ou substituídas por um clique.

## Consulta local

O novo **backend local com catálogo padronizado** abre o mesmo site e oferece API de consulta e busca integral:

```bash
python3 -m backend
```

Abra `http://localhost:8000/local` para os links de teste ou `http://localhost:8000/` para o site. Se o servidor antigo estiver ocupando a porta, encerre-o com Ctrl+C ou use `python3 -m backend --port 8001`. A primeira execução prepara o índice SQLite; não é necessário instalar pacotes para o backend nem usar npm. O Python precisa oferecer SQLite FTS5. O [manual local](docs/projeto/BACKEND-LOCAL.md) explica como iniciar, testar e manter o ambiente.

O catálogo tem **2.186 documentos e 2.197 versões por idioma**, incluindo as edições editoriais anteriores ao ShowTrials. Seus metadados ficam em `data/catalog/`; o banco `.local/catalog.sqlite3` é derivado e ignorado pelo Git. O site mantém seus arquivos, traduções e URLs.

Use **Buscar** na navegação ou o campo da página inicial para abrir `#/busca`. Com o backend, a página pesquisa títulos e texto completo, filtra por coleção, subcoleção, idioma, categoria e tipo documental e apresenta resultados com trechos e paginação. A consulta fica na URL; ao abrir um resultado, o link **Voltar aos resultados da busca** recupera filtros e página. Na publicação estática, a mesma interface pesquisa somente os títulos do manifesto e informa essa limitação. Consulte o [roteiro manual da busca](docs/projeto/BUSCA-MANUAL.md).

Para usar somente o site estático, o comando anterior continua válido:

Na raiz do projeto, execute:

```bash
python3 -m http.server 8000
```

Abra `http://localhost:8000/#/colecao/centro-de-leningrado`. Não é necessário instalar dependências para servir o site. As fontes do Google exigem internet; há fontes alternativas do navegador.

## Organização

- `data/manifest.json`: coleções, subcoleções, documentos e idiomas.
- `data/catalog/`: catálogo normalizado e versionado; o manifesto é sua projeção compatível para o site.
- `backend/`: servidor local Python, validação, exportação e índice de consulta SQLite.
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

**Após a padronização:** os comandos de importação/conversão que escreviam diretamente no manifesto recusam escrita quando `data/catalog/` existe, para proteger a nova fonte de verdade. Os verificadores e as auditorias sem escrita continuam funcionando. Novas importações precisam de adaptação ao catálogo; não remova o catálogo para executar os importadores antigos. Para mudar metadados atuais, valide e exporte conforme o [modelo](docs/projeto/MODELO-CATALOGO.md).

O procedimento abaixo documenta a importação original:

```bash
python3 scripts/import_showtrials.py CAMINHO_DO_PACOTE_PORTATIL
python3 scripts/check_showtrials.py CAMINHO_DO_PACOTE_PORTATIL
```

O importador cobre todas as 28 subcoleções do ShowTrials. A página geral da fonte é um índice e não é duplicada como coleção. Os nomes dos processos seguem o catálogo coletado, incluindo suas datas. Conserva ordem, IDs e URLs, remove apenas o cabeçalho técnico gerado pela exportação Markdown e copia o corpo byte a byte. Referências e notas presentes no corpo são mantidas. Datas WordPress não são apresentadas como datas históricas.

Os documentos importados usam `format: "text"`: o leitor preserva sinais e quebras de linha sem interpretar asteriscos ou abreviações entre sinais de menor/maior como Markdown ou HTML. As edições existentes continuam usando Markdown. Não são aplicadas políticas de segmentação para tradução.

Todo o ShowTrials está disponível em Markdown: **2.179 versões russas, 167.421 blocos preservados e 737 títulos em 487 documentos**. As 31 seleções previamente revisadas foram mantidas. As versões são selecionadas por idioma no manifesto; seus TXT originais permanecem intactos. Os demais documentos foram convertidos com sinais literais, sem inventar subtítulos. A [fila editorial](docs/revisao-markdown/REVISAO-PRIORITARIA.md) e a [planilha de pendências](docs/revisao-markdown/pendencias.csv) registram prioridade, dificuldade, arquivo, fonte e ação sugerida; a triagem inicial aponta 50 documentos urgentes e 226 de prioridade alta. Isso inclui perdas anteriores da extração TXT, como tabelas linearizadas e imagens sem transcrição confirmada. A [documentação da conversão](docs/revisao-markdown/README.md) explica a reprodução e como registrar correções. Não são aplicados limites de fragmentos de tradução à leitura. O modo Estudo respeita títulos explícitos até o sexto nível.

**Reimportação:** arquivos locais diferentes da fonte interrompem a importação antes da escrita, para preservar revisões. Traduções e metadados de documentos já existentes têm precedência. Capas e descrições das coleções importadas são preservadas. As quatro coleções editoriais anteriores não são alteradas. Mudanças manuais nos títulos das coleções/subcoleções devem ser refletidas no mapeamento do importador antes de reimportar.

Para acrescentar uma tradução manualmente, inclua o arquivo e uma entrada em `languages` no documento correspondente. Para acrescentar a capa, preencha `cover` na coleção, seguindo os exemplos existentes.

As traduções dos documentos ShowTrials podem ficar em `originais/showtrials/ID.pt.md`. Cadastre também `title_pt` e, na entrada do idioma português, `format: "markdown"`, pois o documento russo pode continuar em texto simples. O formato de cada idioma tem precedência sobre o formato geral do documento. Se o arquivo veio da exportação do site, o título, a fonte, o ID e o idioma do cabeçalho devem ser cadastrados como metadados; o arquivo publicado contém o corpo, conservando seus parágrafos. A exportação recompõe esse cabeçalho. O documento `showtrials-1665` é um exemplo dessa organização.

## Publicação

O [plano de evolução](docs/projeto/PLANO.md), as [decisões](docs/projeto/DECISOES.md) e o [modelo do catálogo](docs/projeto/MODELO-CATALOGO.md) registram a primeira entrega e as próximas etapas. A API local é de leitura; edição editorial e upload de traduções pertencem a entregas posteriores.

O site pode ser servido pelo GitHub Pages a partir da raiz, sem compilação. A publicação deve incluir `index.html`, `assets/`, `data/` e `originais/`. A pasta `temporario/` e as exportações de trabalho não precisam ser publicadas.
