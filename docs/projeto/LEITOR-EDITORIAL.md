# Do leitor à edição local e de volta

A importação aprovada foi commitada em `7b569a2`, incluindo as traduções 2676–2678 e seus cadastros. A correção dos cabeçalhos foi commitada separadamente em `eb9da8a`. Não houve push. A integração descrita neste documento foi validada manualmente pelo usuário, incluindo o editor e a correção do carregamento. Os commits foram autorizados, sem push. Não foram executados testes pelo assistente.

## Como abrir

Encerre o backend anterior com **Ctrl+C** e, na raiz do projeto, execute:

```bash
python3 -m backend
```

Abra o site em **http://localhost:8000/** e atualize com **Ctrl+Shift+R**. Entre em um documento. Acima do cabeçalho do documento, clique em **Expandir** no **Painel do documento**. No grupo **Trabalhar com o documento**, abra **Editar documento**, que reúne os controles locais:

- **Metadados:** abre o cadastro daquele documento.
- **Adicionar tradução:** abre a importação com o documento selecionado; o idioma continua sendo uma escolha explícita.
- **Editar Markdown:** abre a versão escolhida na lista de idiomas desse menu. A escolha é independente do idioma de leitura: confira Russo/Português/Inglês antes de abrir.

Os controles aparecem somente quando o backend local anuncia suporte à edição. Não aparecem no GitHub Pages nem com `python3 -m http.server`. Se não aparecerem, confira se reiniciou o backend atualizado, está usando a mesma porta no navegador e acessou por `localhost` ou `127.0.0.1`. Um servidor vinculado a `0.0.0.0` não habilita a área editorial.

## O que acontece ao editar

O editor mostra o **arquivo Markdown completo**, com cabeçalhos que ele já contenha, e a prévia renderizada de seu corpo. A prévia usa a mesma separação de cabeçalhos de exportação do leitor. Digitar atualiza a prévia com breve atraso em textos menores; em textos extensos, use **Atualizar prévia**.

**Revisar alterações no Markdown** mostra as diferenças e a renderização proposta. Não grava nenhum arquivo. **Confirmar e salvar** grava a versão escolhida, guarda o conteúdo anterior no histórico e atualiza hash, tamanho, manifesto e índice de busca. As demais versões e os caminhos/URLs permanecem iguais. O índice é preparado antes de publicar os arquivos.

Se escolher **RU**, estará editando explicitamente o original russo. Ele pode ser restaurado pelo histórico, mas não será mantido intocado nessa operação. A importação de traduções continua sem poder substituir o idioma original. Edições apenas em TXT não são convertidas pelo editor: essa tela aceita as versões Markdown cadastradas.

O título dentro do Markdown faz parte do texto; alterá-lo não modifica o título cadastrado. Para isso, use **Editar metadados deste documento**. Alterações de metadados e de Markdown têm prévias e gravações separadas, registradas no mesmo histórico.

## Exercício curto, com restauração

1. Abra `showtrials-1666` no leitor, de preferência navegando pela coleção ou a partir de uma busca. Escolha **Leitura → PT**, avance um pouco no texto e, se desejar, marque um parágrafo com a bolinha vermelha.
2. Abra **Editar documento**, escolha **PT** no seletor de edição e clique em **Editar Markdown**. Confira que o editor identifica `showtrials-1666:pt`. O texto da versão russa não será alterado nesse exercício.
3. Acrescente ao final um parágrafo como `Experimento temporário do editor integrado.` A prévia deve mostrar a inclusão. Até aqui, o site e o arquivo original continuam no estado anterior.
4. Clique em **Revisar alterações no Markdown**. Confira o parágrafo nas diferenças e a versão PT identificada. Confirme a gravação e aguarde a mensagem de sucesso.
5. Clique em **Voltar à leitura**. O mesmo documento deve abrir com o idioma/modo e o contexto de coleção ou busca anteriores. O texto novo deve estar presente e a exportação PT deve incluí-lo. A marcação manual não é substituída pelo mecanismo de retorno.
6. Na busca local, procure `Experimento temporário`, filtrando português. O documento deve aparecer com a nova expressão. Volte ao documento para continuar.
7. Abra **Metadados**, depois o **Histórico deste documento**. Na operação mais recente de Markdown, use **Revisar restauração** e confirme. Ao voltar à leitura, o parágrafo de experimento deve desaparecer. A restauração também atualiza exportação e busca e permanece registrada.

## Conferir os outros caminhos

- **Metadados:** parta do leitor e abra seu cadastro. Altere temporariamente um rótulo, revise, salve e use **Voltar à leitura**. Confira o rótulo no documento e desfaça pelo histórico depois.
- **Adicionar tradução:** abra a importação a partir do documento. Confira o ID já selecionado, escolha o idioma e use o fluxo de prévia/salvar existente. O retorno à leitura carrega novamente o manifesto, exibindo o idioma incluído. Não é necessário salvar só para conferir o atalho.
- **Estudo:** escolha um documento traduzido, entre em estudo por parágrafo ou paralelo, abra a edição e volte. O retorno deve manter modo e colunas válidas. A posição é recuperada pelo trecho quando ainda reconhecível, com fallback para a posição de rolagem quando o conteúdo tiver mudado muito.
- **Outra aba:** deixe o leitor aberto em uma aba e salve pela área editorial em outra aba do mesmo endereço e porta. O leitor recebe uma notificação local e recarrega o acervo, tentando manter seu contexto. Se o navegador bloquear o armazenamento local, recarregue a aba manualmente.
- **Botão Voltar do navegador:** o leitor também recarrega catálogo e conteúdo ao voltar de uma página mantida no cache de navegação. O link explícito **Voltar à leitura** é o caminho recomendado para preservar o contexto informado.
- **Versões distintas:** escolha EN ou RU no seletor de edição e apenas abra o editor para conferir a identificação. Não salve alterações desnecessárias. Para testar edições reais em outra versão, revise cuidadosamente e restaure a operação ao terminar.
- **Versão estática:** encerre o backend e inicie `python3 -m http.server 8000`. Recarregue o leitor: leitura, estudo, exportação e busca de títulos continuam disponíveis, sem os controles editoriais.

## Contexto, histórico e limites

O retorno usa um endereço interno e um registro pequeno em `sessionStorage` da mesma aba. Ele conserva documento, coleção/subcoleção, retorno à busca, idioma, modo de estudo, colunas e posição aproximada. Não cria nem apaga o marcador manual. Se o armazenamento da sessão estiver bloqueado, o link ainda volta ao documento, mas a recuperação da posição e do modo pode ser limitada. Após grandes mudanças de estrutura, a posição pode ser aproximada.

Uma gravação notifica as outras abas do mesmo endereço por uma chave em `localStorage`, sem enviar o conteúdo do documento. Ao retornar ao leitor, catálogo e arquivos são buscados novamente, e o cache em memória é descartado. Um aviso em outra aba não publica nem salva novas alterações por si só.

O histórico continua local em `.local/editorial/history/`, fora do Git. O campo interno legado `translation_files` agora também pode listar uma edição Markdown original, quando alterada explicitamente pelo editor. A importação mantém sua proteção própria. As restaurações conservam os controles de conflito: alterações posteriores nos mesmos arquivos devem ser desfeitas antes das anteriores.

Nenhuma publicação automática foi implementada. Para disponibilizar alterações no GitHub Pages, continua sendo necessário um commit e um push separados, autorizados por você.

## API acrescentada

| Método e caminho | Uso |
| --- | --- |
| `GET /api/editorial/editions/ID:IDIOMA` | Conteúdo e revisão de uma versão Markdown existente |
| `POST /api/editorial/markdown/preview` | Prévia da edição, vinculada à revisão e ao hash da versão aberta |
| `POST /api/editorial/save` | Confirmação compartilhada com metadados/importação e gravação do histórico |

Esses endpoints continuam restritos ao backend em loopback, mesma origem e token da sessão para gravação. O editor não recebe caminhos arbitrários para escrever: o destino vem da edição cadastrada. Arquivos compartilhados entre versões e links simbólicos são recusados para evitar alterações indiretas em outras versões.


## Fluxo simplificado de edição

No leitor: Expandir → Editar → escolher idioma (opcional) → Editar. O idioma inicial acompanha a leitura, ou a coluna esquerda no estudo paralelo, como na exportação. A ação abre os metadados e coleções do documento na área editorial. Ali, “Editar Markdown” na barra lateral abre a versão escolhida; “Metadados e coleções” volta ao cadastro. Na ausência de Markdown naquele idioma, a tela oferece as versões editáveis e a importação. Ao abrir Editar Markdown sem documento, é possível informar o ID ou procurar no catálogo. O retorno ao leitor continua preservado.

Conferir manualmente: idioma PT em leitura e RU à esquerda no paralelo; abrir Editar em cada contexto e observar a versão aberta pela opção lateral Editar Markdown. Conferir ações com aparência de botão em metadados, coleções, catálogo e histórico. Não foram executados testes, commit ou push.
