# Cadastro local de documentos, coleções e subcoleções

Versionamento autorizado pelo usuário, junto da importação em lote. Nenhum teste, servidor de verificação, compilação ou push foi executado pelo assistente. O acervo não foi importado nem reescrito para demonstrar o recurso.

## Iniciar e acessar

Encerre o backend anterior com Ctrl+C. Na raiz do projeto:

```bash
python3 -m backend
```

Abra http://localhost:8000/editorial e recarregue com Ctrl+Shift+R. O servidor `python3 -m http.server` e o GitHub Pages não permitem gravar os cadastros.

A barra lateral contém:

- **Novo documento:** enviar um original Markdown ou TXT, selecionar idioma, preencher metadados e associar às coleções.
- **Coleções e subcoleções:** listar, criar e editar coleções, seus títulos, descrições, capa e cor.
- **Importar tradução:** adicionar traduções a documentos já cadastrados.
- **Editar catálogo / Editar Markdown:** trabalhar com os documentos existentes.
- **Histórico:** revisar e confirmar restaurações, inclusive dos cadastros novos.

Digitar, selecionar um arquivo e clicar em Revisar não grava o acervo. Somente Confirmar e salvar aplica a proposta localmente. Não há publicação automática.

## Exercício curto e isolado

Faça este exercício antes de iniciar cadastros de trabalho, para facilitar a restauração. Os identificadores sugeridos são exemplos; use outro se já existir.

### 1. Criar uma coleção

1. Entre em **Coleções e subcoleções → Nova coleção**.
2. Informe título `Coleção de validação` e identificador `colecao-validacao`.
3. Deixe **Coleção principal** em Nenhuma; capa e fonte podem ficar em branco. A cor padrão segue a paleta do site.
4. Clique em **Revisar coleção**. Confira o cadastro e a prévia visual. Nada foi gravado.
5. Clique em **Confirmar e salvar** e depois **Ver no site**. A coleção deve existir, ainda com zero documentos.

### 2. Criar uma subcoleção

1. Na área editorial, volte a **Coleções e subcoleções**. A nova coleção deve aparecer sem reiniciar o backend.
2. No cartão dela, escolha **Nova subcoleção**.
3. Informe título `Cartas de validação` e identificador `cartas-validacao`. Confira que Coleção principal aponta para Coleção de validação.
4. Revise e confirme. A subcoleção deve aparecer dentro da coleção no leitor e no catálogo editorial.

### 3. Cadastrar um documento

Crie fora do acervo, no seu editor de texto, um arquivo UTF-8 chamado `documento-validacao.en.md`:

```markdown
# Validation document

## First section

This is a temporary document for checking the local catalog.

## Second section

A second paragraph makes it possible to check navigation and bookmarks.
```

1. Abra **Novo documento** ou a ação correspondente da coleção.
2. Informe ID `documento-validacao`, título original `Validation document` e idioma **Inglês**. Deixe o título português em branco para conferir a apresentação de um documento somente em inglês.
3. Selecione o arquivo e marque **Cartas de validação**. A coleção principal será associada junto, automaticamente. Data, autoria, fonte e referência são opcionais; preencha o que você souber em documentos reais.
4. Clique em **Revisar novo documento**. Confira título, idioma, associações, arquivo de destino e prévia. O destino deve ser `originais/locais/documento-validacao.en.md`.
5. Confirme. Use **Ler documento**. O título inglês deve aparecer; confira índice, marcador e exportação. O idioma original é inglês e fica protegido nos fluxos de importação/correção de tradução.
6. Na busca, procure `temporary document`. Na fila de revisão, procure `documento-validacao`. Deve haver uma pendência média para conferir o novo cadastro.
7. No cadastro, confira se o título inglês pode ser editado. Se fizer uma alteração e salvar, ela também entrará no histórico e precisará ser desfeita antes do cadastro no exercício de limpeza.

Arquivos TXT também são aceitos, com o conteúdo exibido como texto. Não são convertidos automaticamente para Markdown. O editor Markdown continua disponível apenas para versões nesse formato. O idioma original pode ser russo, português ou inglês.

## Desfazer o exercício

A restauração compara os arquivos com o estado gravado. Desfaça da operação mais recente para a mais antiga; o catálogo é compartilhado entre os cadastros.

1. Em **Histórico**, filtre por `documento-validacao`. Se editou o documento depois de criá-lo, desfaça primeiro essas edições. Use **Revisar restauração**, confira e confirme para desfazer o cadastro. O documento, a edição, as associações, a pendência e o arquivo criado devem sair do acervo ativo. O histórico continua guardando o conteúdo.
2. Filtre pelo ID completo `colecao-validacao/cartas-validacao` e desfaça a criação da subcoleção.
3. Filtre por `colecao-validacao` e desfaça a criação da coleção principal.
4. Confira que os itens saíram das listas e da busca. Nenhum documento anterior ao exercício deve ter sido alterado.

Uma restauração também gera histórico. Não é necessário desfazer essa restauração para continuar a limpeza do exercício; selecione a operação de criação seguinte, respeitando a ordem acima. Para refazer uma criação, revise a restauração da própria operação de restauração, desde que não existam conflitos posteriores.

## Conferências adicionais

- **Cancelar prévia:** preencha um cadastro e gere a prévia; saia sem confirmar. O item não deve aparecer no leitor.
- **ID repetido:** tente cadastrar outro documento com `showtrials-1666`. Deve recusar, sem substituir nada.
- **Possível duplicidade:** use outro ID e um arquivo/título/fonte já cadastrados. A prévia deve sinalizar coincidências e exigir confirmação explícita. Cancele o exercício se não pretende criar uma cópia.
- **Arquivo inválido:** confira a recusa de formato diferente de MD/TXT, conteúdo vazio, codificação inválida ou arquivo maior que 4 MiB.
- **Coleção antiga sem subcoleções:** a primeira subcoleção nova deve aparecer no leitor, sem perder o acesso aos documentos anteriores pelo link para todos os documentos.
- **Editar coleção:** mude título/descrição, revise e confirme. O identificador e a coleção principal ficam fixos, preservando a URL. Restaure a edição depois se foi apenas um teste.
- **Tradução de original novo:** em um cadastro de validação, importe português e confira o estudo e a proteção do original inglês. Desfaça primeiro a tradução antes de desfazer o cadastro do documento.
- **Duas abas:** abra o mesmo cadastro, salve uma alteração na primeira e tente confirmar uma proposta antiga na segunda. A versão antiga deve ser recusada, sem sobrescrever a primeira.
- **Tela estreita:** confira a navegação horizontal da lateral, campos, prévia e confirmação, sem ações cortadas.

## Capas e limites desta entrega

As coleções não exigem capa. Para usar uma, coloque a imagem em `assets/covers/` e informe o caminho relativo no formulário. A prévia mostra a imagem escolhida. São aceitos JPEG, PNG, WebP e AVIF existentes nessa pasta. O cadastro não move, apaga ou substitui as imagens; o histórico recupera a referência da capa.

Este formulário cadastra um original por vez, seguido das traduções, e coleções por formulário. A entrega seguinte acrescenta Importar lote para originais com CSV; veja IMPORTACAO-EM-LOTE.md. Pacotes ZIP/JSON e upload de capas pela interface continuam registrados como próximas melhorias.

## Preservação e funcionamento

- IDs e caminhos existentes não são renomeados. Arquivos novos usam `originais/locais/ID.IDIOMA.md` ou `.txt`; o nome enviado fica registrado, mas não define um caminho arbitrário de gravação.
- O arquivo original recebido é preservado em UTF-8, incluindo BOM e quebras de linha; o cadastro não converte nem segmenta o conteúdo no disco.
- Associar a uma subcoleção também associa à coleção principal. Novos itens entram no fim da ordem existente.
- O original declarado fica em `source_metadata.original_language`, sem inferir um idioma novo para o acervo antigo.
- O cadastro atualiza documentos, edições, associações, projeção global, manifesto e busca. A pendência de revisão nasce junto ao documento.
- A prévia aponta possíveis duplicidades por título, URL de fonte ou hash do arquivo, além das divergências de identificação reconhecidas. Isso não é comparação semântica.
- Novas coleções e edições de seus metadados também atualizam catálogo, manifesto e índice.
- O histórico salva os estados anterior e posterior antes de publicar os arquivos; a recuperação de interrupção reutiliza esse estado. Restaurar uma criação remove somente o arquivo criado por aquela operação e mantém sua cópia no histórico.
- A restauração de cadastros inclui coleções e proveniência. Mudanças posteriores incompatíveis são recusadas, em vez de apagadas silenciosamente.

## Backup para trabalhar nos próximos dias

Pare o backend antes da cópia e copie a pasta inteira do projeto para outro local, incluindo a pasta oculta `.local`. O acervo versionável está em `originais/`, `data/`, `assets/` e nos registros em `docs/`; o histórico recuperável fica em `.local/editorial/history/` e não entra no Git. O índice SQLite é derivado, mas o histórico não é substituído por ele. Reinicie com `python3 -m backend` após a cópia.

## API acrescentada

| Método e caminho | Uso |
| --- | --- |
| POST /api/editorial/documents/preview | Prévia do cadastro de um original com metadados e associações |
| GET /api/editorial/collections/ID | Metadados e revisão da coleção/subcoleção |
| POST /api/editorial/collections/preview | Prévia de criação ou edição de coleção/subcoleção |
| POST /api/editorial/save | Confirmação compartilhada com os demais fluxos editoriais |

Todos os caminhos editoriais continuam restritos ao backend local, mesma origem e sessão. A prévia é temporária; nenhuma gravação ocorre antes da confirmação.
