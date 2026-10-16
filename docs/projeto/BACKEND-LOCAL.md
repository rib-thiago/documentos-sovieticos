# Como iniciar e testar o catálogo local

Na raiz do projeto:

```bash
cd /home/thiago/documentos-sovieticos
python3 -m backend
```

Se o servidor antigo `python3 -m http.server 8000` estiver aberto, encerre-o com **Ctrl+C** antes. Alternativamente, inicie o novo backend em outra porta com `python3 -m backend --port 8001` e substitua a porta dos links abaixo.

Aguarde o terminal mostrar os endereços. Na primeira inicialização, ele confere o acervo e constrói o índice; nas seguintes reutiliza o banco quando o catálogo e os hashes continuam válidos. Não precisa instalar pacotes para o backend. Para encerrar, pressione **Ctrl+C**.

## Teste pelo navegador

1. Abra [a página de testes locais](http://localhost:8000/local). Ela deve mostrar **2.186 documentos, 2.206 versões por idioma, 13 coleções e 28 subcoleções**. O campo `memberships` da API deve ser **4.460**: associações, não documentos únicos.
2. Clique em **Abrir o site e o leitor existentes**. Navegue até uma coleção e abra um documento. Índice, marcador, leitura, estudo e exportação usam os mesmos arquivos anteriores.
3. Abra [Nikolaev pela API](http://localhost:8000/api/documents/showtrials-1665). A resposta JSON deve conter `editions` com russo e português, além das coleções a que pertence. Os links `content_url` retornam o texto da versão.
4. Abra [os documentos em português](http://localhost:8000/api/documents?language=pt&limit=20). O total esperado no catálogo atualizado é **12 documentos**.
5. Abra [a busca por Николаева](http://localhost:8000/api/search?q=Николаева&language=ru&limit=5). A resposta deve ter resultados e `match.snippet` com contexto em russo. `limit=5` limita a página; `total` indica a quantidade total de documentos encontrados.
6. Abra [o Centro de Leningrado na ordem original](http://localhost:8000/api/documents?collection=centro-de-leningrado&sort=source&limit=5). O total esperado é **175**, e o primeiro documento é `showtrials-1665`.
7. Abra [a subcoleção de investigação](http://localhost:8000/api/documents?collection=centro-de-leningrado&subcollection=investigacao&sort=source&limit=5). Ela mantém a ordem cadastrada na fonte.

As respostas da API aparecem em JSON. Para pesquisar pela interface do site, abra [Buscar no acervo](http://localhost:8000/#/busca). O [roteiro manual da busca](BUSCA-MANUAL.md) explica os filtros, a paginação e o retorno aos resultados. O guia de endpoints também está em [api](http://localhost:8000/api).

Para revisar pendências e editar metadados, abra [a área editorial local](http://localhost:8000/editorial). Reinicie o backend após atualizar o código. Mantenha somente um processo de backend neste acervo. O [manual editorial](EDITORIAL-LOCAL.md) explica a prévia, a confirmação, o histórico e a recuperação das alterações. As gravações pela interface atualizam automaticamente o manifesto e o índice; não é necessário exportá-los manualmente.

A tela **Importar tradução** inclui ou substitui Markdown em português/inglês, com seleção explícita do documento, prévia e histórico do conteúdo. Consulte o [exercício manual de importação e restauração](IMPORTACAO-TRADUCOES.md). Nenhuma dessas operações publica no GitHub automaticamente.

## Endpoints

| URL | Resultado |
| --- | --- |
| `/api/health` | Estado, revisão do índice e contagens |
| `/api/collections` | Coleções principais com suas subcoleções |
| `/api/collections/centro-de-leningrado/investigacao` | Uma subcoleção pelo ID completo |
| `/api/documents` | Documentos paginados |
| `/api/documents/ID` | Ficha normalizada, edições e todas as associações |
| `/api/editions/ID:IDIOMA/content` | Conteúdo original da edição, sem reescrita |
| `/api/search?q=PALAVRA` | Pesquisa integral, agrupada por documento |
| `/api/vocabularies` | Tipos e rótulos portugueses, idiomas e categorias gerais |

Filtros em `/api/documents` e `/api/search`: `collection`, `subcollection`, `language`, `type`, `kind`. Paginação: `limit` de 1 a 100 e `offset` a partir de zero. Ordenação: `title`, `id`, `relevance` ou `source` — a última exige uma coleção. `scope=title` pesquisa só os títulos; o padrão é `all`. Use `type=unspecified` para registros sem tipo específico cadastrado.

Palavras de `q` são combinadas por AND; uma expressão entre aspas duplas é uma frase. A busca distingue palavras russas flexionadas e não traduz automaticamente português para russo. Consultas inválidas retornam HTTP 400 com mensagem; IDs ausentes retornam 404. As APIs públicas não aceitam escrita. Os POSTs de prévia e gravação são exclusivos da área editorial local, conforme seu manual.

## Conferir e manter o catálogo

```bash
python3 -m backend.catalog check
python3 -m backend.catalog export --check
```

O primeiro confere registros, associações, arquivos, hashes e compatibilidade do manifesto. O segundo confirma que o site estático está atualizado, sem escrever arquivos.

Depois de uma edição nos metadados de `data/catalog/`, gere o manifesto e reinicie o backend:

```bash
python3 -m backend.catalog export
python3 -m backend
```

O comando `export` valida primeiro o catálogo e só então substitui o manifesto. Não o edite diretamente. Para campos novos, consulte o [modelo](MODELO-CATALOGO.md). Ainda não há formulário de edição.

Depois de alterar intencionalmente o conteúdo de uma versão, faça a revisão documental pertinente e confira os hashes:

```bash
python3 -m backend.catalog refresh-files
python3 -m backend.catalog refresh-files --write
```

O primeiro somente mostra quais arquivos mudaram; o segundo registra os hashes novos no catálogo. Ele não altera os textos e não confirma que uma alteração está historicamente correta. Em seguida, reinicie o backend. A validação das receitas de conversão continua independente e pode apontar mudanças editoriais que precisam de registro próprio.

Para reconstruir o índice derivado:

```bash
python3 -m backend --rebuild
```

O SQLite fica em `.local/catalog.sqlite3`, fora do Git. O backend não precisa do diretório temporário nem de conexão de rede. O site estático continua funcionando com `python3 -m http.server 8000` e pode ser publicado no GitHub Pages; apenas a API e `/local` exigem o novo servidor.

## Testes automatizados

```bash
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Os testes do backend criam um acervo temporário independente e abrem uma porta livre em localhost. Cobrem migração sem perda, extensões de metadados, formatos por idioma, integridade, busca russa/portuguesa, frases, filtros por múltiplas coleções, paginação, cache e HTTP. Não modificam o acervo do projeto.
