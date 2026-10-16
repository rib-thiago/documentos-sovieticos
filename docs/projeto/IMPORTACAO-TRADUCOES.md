# Importar traduções Markdown no acervo local

Implementação sem execução de testes pelo assistente, sem commit e sem push, conforme solicitado. Este roteiro descreve o comportamento esperado para sua verificação manual.

## O que esta tela faz

Você escolhe um documento já cadastrado, escolhe português ou inglês e envia um arquivo Markdown. A tela apresenta o que reconheceu da identificação do arquivo, as diferenças em relação à tradução atual, uma prévia de leitura e contagens estruturais. Só **Confirmar e salvar** grava no projeto.

Salvar é uma alteração real nos arquivos do seu computador. A tradução fica disponível no leitor e na busca locais; **não há envio ao GitHub nem publicação automática**. O original de referência não é substituído. Esta entrega não inclui editor de Markdown no navegador nem correções por trecho no modo estudo.

## Abrir

1. Encerre o backend anterior com **Ctrl+C**.
2. Na pasta do projeto, execute `python3 -m backend`.
3. Abra **http://localhost:8000/editorial#/importar**. Se a tela antiga estiver em cache, use **Ctrl+Shift+R**.

Você também pode procurar o documento em **Editar catálogo** e clicar em **Importar tradução para este documento**. No formulário de metadados existe o mesmo atalho. A seleção continua visível na tela de importação; o idioma precisa ser escolhido explicitamente.

## Exercício principal: substituir e desfazer

Este exercício usa um documento que já tem tradução, para que você possa conferir as diferenças e recuperar exatamente a versão anterior.

1. No leitor, abra **http://localhost:8000/#/doc/showtrials-1666**, selecione **PT** e exporte o Markdown. Trabalhe na cópia baixada, sem editar diretamente o arquivo do projeto.
2. Na cópia, acrescente ao final um parágrafo identificável, por exemplo: `Teste temporário da importação local.` Salve em UTF-8. Não altere o ID do documento. Mantenha um nome como `showtrials-1666.pt.md`.
3. Na área editorial, abra **Importar tradução**, informe `showtrials-1666` e clique em **Selecionar documento**. Confira o título e o ID mostrados.
4. Escolha **Português — substituir versão existente**, selecione a cópia e clique em **Revisar importação**. O título opcional do catálogo pode ficar como já está; esse campo não reescreve o título dentro do arquivo.
5. **Até aqui nada foi gravado.** A prévia deve informar que substituirá PT do documento 1666. Confira a identificação, o novo parágrafo nas diferenças e na prévia renderizada. O sinal `+` indica inclusão e `-` indica remoção. As contagens podem mudar com o parágrafo e com cabeçalhos de exportação.
6. Se aparecer uma divergência de nome, ID, idioma ou fonte, leia-a. Corrija a escolha ou o arquivo quando houver erro real. Se for apenas um nome antigo ou um cabeçalho desatualizado e você souber que escolheu a associação correta, marque a confirmação explícita. Sem essa confirmação, divergências não permitem salvar.
7. Clique em **Confirmar e salvar** e aguarde a conclusão. A tradução anterior entra no histórico antes da gravação da nova. O catálogo, o manifesto e o índice de busca são atualizados junto com o arquivo traduzido.
8. Clique em **Abrir documento atualizado**. Se o leitor já estiver aberto, recarregue-o. A versão PT deve mostrar o parágrafo de teste. Procure a expressão pela busca, filtrando **Português**; o documento deve aparecer. RU e EN continuam com seus conteúdos anteriores.
9. Entre em **Histórico**, filtre por `showtrials-1666` e escolha a operação mais recente. Clique em **Revisar restauração**. Confira a inversão das alterações e as diferenças do arquivo que será restaurado; confirme.
10. Recarregue o leitor. O parágrafo de teste deve desaparecer e a versão anterior deve voltar. A restauração também fica registrada no histórico.

O arquivo recebido é preservado, inclusive cabeçalhos e quebras de linha. Confira sua estrutura antes de salvar.

## Conferir uma divergência sem gravar

Depois de concluir e desfazer o exercício anterior, escolha outro documento na importação, mas envie a mesma cópia identificada como `1666`. A prévia deve apontar a divergência entre o documento selecionado e o nome/cabeçalho do arquivo. **Não confirme nem salve essa associação incorreta**; use Voltar à edição ou saia da tela.

Esse mecanismo não traduz nem compreende o conteúdo. Um texto russo chamado `.pt.md`, com cabeçalho PT, não será identificado semanticamente como russo. A conferência é dos campos reconhecidos; a seleção e a revisão continuam sob seu controle.

## Incluir uma tradução que ainda não existe

Use uma tradução sua para um documento que ainda não tenha aquele idioma. Selecione o documento e o idioma, envie o arquivo e revise. A tela deve indicar **Inclusão de uma nova tradução**. Depois de salvar, esse idioma passa a estar disponível no leitor, no estudo e na exportação.

Ao desfazer essa inclusão pelo histórico, a nova edição sai do catálogo e o arquivo criado nessa importação é removido. O conteúdo continua recuperável no histórico: a própria restauração pode ser desfeita, se não houver mudanças posteriores incompatíveis. Não é removido nenhum original nem uma tradução anterior que já existisse.

## O que significa o diagnóstico

| Informação | Como interpretar |
| --- | --- |
| Blocos do modo estudo | Quantidade de blocos do corpo que o segmentador atual encontra, considerando o formato de cada versão. Cabeçalhos de exportação podem ocupar blocos. |
| Parágrafos aproximados | Blocos que não foram reconhecidos como títulos, listas, tabelas ou código. Não é uma análise linguística. |
| Títulos, listas, tabelas e código | Sinais estruturais aproximados para orientar a conferência visual. |
| Quantidades diferentes | Pode haver deslocamento entre os trechos no modo estudo; não implica necessariamente erro de tradução. |
| Quantidades iguais | Não garante que os trechos correspondam nem que estejam na mesma ordem. |

Não são unidos, divididos, traduzidos ou pareados parágrafos automaticamente. A comparação estrutural não é gravada como um alinhamento confirmado. Depois de salvar uma tradução, confira o modo estudo manualmente.

## Identificação, limites e preservação

- São aceitos `.md` e `.markdown` em UTF-8, até **4 MiB**. O conteúdo, o BOM UTF-8 quando presente e as quebras de linha são preservados. Markdown vazio ou com byte nulo é recusado.
- São reconhecidos nomes como `showtrials-1666.pt.md` e cabeçalhos iniciais com `ID ShowTrials`/`ShowTrials ID`, `Idioma`/`Language`, `Fonte`/`Source` e título `#`. Não há leitura arbitrária de frontmatter YAML ou inferência de IDs citados no corpo. Nome e cabeçalho ausentes geram informação de identificação incompleta; divergências reconhecidas exigem confirmação.
- O nome enviado não determina onde gravar. O backend usa o documento e o idioma selecionados. Uma tradução Markdown existente conserva seu caminho. Uma edição legada em TXT pode ganhar um arquivo Markdown próprio, mantendo o TXT anterior e as URLs do leitor.
- A referência é RU quando disponível; em documentos sem RU, usa-se a primeira edição cadastrada. O idioma dessa edição não pode ser importado como tradução. Também é recusado um destino pertencente a outra edição ou ocupado por um arquivo ainda não cadastrado.
- O título opcional atualiza o cadastro no idioma selecionado. Deixá-lo vazio mantém o título atual; o cabeçalho do arquivo não é copiado para o cadastro sem essa escolha. Títulos EN passam a ser projetados como `title_en` quando preenchidos.
- Diferenças extensas são abreviadas, com indicação visível. Os textos completos permanecem consultáveis na prévia. Para arquivos grandes, abra a seção da prévia renderizada para processá-la sob demanda.
- Uma prévia dura 15 minutos. Trocar documento, idioma, arquivo ou título invalida a prévia visível. Alterações concorrentes no catálogo, na fila ou no arquivo de destino recusam a gravação e exigem nova prévia.

## Histórico e recuperação

O histórico continua em `.local/editorial/history/`, fora do Git. Agora ele também guarda os arquivos traduzidos antes e depois da operação e registra quando um arquivo ainda não existia. Mantenha uma cópia desse diretório se quiser preservar as possibilidades de desfazer fora deste computador.

Restaure da alteração mais recente para a mais antiga. Como o histórico preserva arquivos inteiros do catálogo e do manifesto, ele recusa uma restauração que apagaria mudanças posteriores, mesmo em outros documentos. Os registros antigos de edição apenas de metadados continuam aceitos.

O índice é preparado com o conteúdo proposto antes da publicação dos arquivos, sem expor essa proposta ao leitor. O marcador de transação e a recuperação de uma interrupção abrangem tanto o cadastro quanto o arquivo traduzido. O backend bloqueia gravação se detectar uma edição externa incompatível, em vez de sobrescrevê-la.

## API

`POST /api/editorial/translations/preview` recebe `revision`, `document_id`, `language`, `filename`, `content` e `title`. O texto do arquivo é enviado em JSON; não há upload para serviços externos. A resposta contém identificação, divergências, prévia, diferenças e diagnóstico. A gravação usa o endpoint existente `/api/editorial/save`, com `preview_id` e confirmação de divergências quando exigida.
