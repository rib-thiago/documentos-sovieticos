# Área editorial local: revisão e metadados

Esta entrega foi implementada sem execução de testes pelo assistente, conforme solicitado. O usuário realizou o roteiro de edição, gravação e restauração, confirmou o funcionamento e autorizou o commit. Ajustes de layout e UI/UX ficaram para depois. O roteiro abaixo permanece como referência para verificações manuais.

## Iniciar

Encerre o backend anterior com **Ctrl+C**. Na raiz do projeto, execute:

```bash
python3 -m backend
```

Abra **http://localhost:8000/editorial**. Também existe um link em **http://localhost:8000/local**. Atualize com **Ctrl+Shift+R** se necessário. Não precisa instalar pacotes nem usar npm. O backend utiliza o Python e o SQLite existentes; o bloqueio de gravação utiliza `fcntl`, disponível no ambiente Linux do projeto.

Mantenha apenas um backend ativo para este acervo. Se outro programa ocupar a porta, use `--port 8001`, encerrando antes qualquer backend deste mesmo projeto. A área editorial exige o servidor vinculado a `127.0.0.1` e acesso por `localhost` ou `127.0.0.1`. O site estático continua publicado normalmente, mas a área editorial funciona somente com o backend local.

## O que é editável

- Títulos português e russo, categoria (documento/artigo), tipo documental, autoria registrada, referência arquivística, data histórica, título curto e rótulo editorial.
- Associações às coleções e subcoleções já existentes. Uma subcoleção exige sua coleção principal. Associações novas entram no fim; as mantidas conservam sua ordem relativa. Não são criados nem renomeados IDs de coleções.
- Prioridade, motivo, status e notas das pendências existentes. Os status são pendente, em revisão, corrigido e adiado. A ação sugerida e a dificuldade da triagem continuam disponíveis para consulta.

IDs, arquivos, traduções, conteúdo dos textos, idiomas, URLs de leitura e URLs da fonte são preservados. Esta etapa não edita o Markdown nem importa traduções. Mudar autoria ou data não significa certificação automática da informação histórica. A data histórica ISO exige precisão correspondente: `1934`, `1934-12` ou `1934-12-03`.

## Verificação manual sugerida

1. Abra **Fila de revisão**. Por padrão, aparecem pendências com status **Pendente**, ordenadas por prioridade. Confira filtros por prioridade, status, coleção e texto. O texto procura ID, títulos e motivo/notas, sem tradução automática. A lista é paginada em até 50 pendências; os contadores por status referem-se à fila inteira. Um documento pode ter várias pendências.
2. Escolha **Todos** no filtro de status e procure `showtrials-1699`. A pendência `tabelas_linearizadas` deve estar como **Corrigido**, com a nota já registrada sobre sua tabela. A outra pendência histórica desse documento não foi automaticamente encerrada.
3. Abra uma pendência. Confira motivo, ação sugerida, dificuldade, prioridade e status, além dos metadados e idiomas do documento. O link do leitor abre outra aba, preservando a edição.
4. Para experimentar a fila, mude uma pendência para **Em revisão** e acrescente uma nota identificada como teste manual. Clique em **Revisar alterações**. A prévia deve mostrar os valores anteriores e propostos. Até esse momento nenhum arquivo foi gravado. **Voltar à edição** descarta somente a prévia e mantém o formulário.
5. Clique em **Confirmar e salvar**. Aguarde a mensagem de conclusão. Reabra a fila e filtre por **Em revisão** para encontrar o item. Uma mudança apenas na fila não reconstrói a busca.
6. Abra **Editar catálogo**. Você pode procurar um título ou um ID exato, como `showtrials-1666`, inclusive para documentos sem pendências. Altere temporariamente o título curto ou o rótulo editorial e revise a prévia. Confirme a gravação: o índice é preparado antes da publicação das alterações, e o catálogo e o manifesto são atualizados juntos.
7. Recarregue a aba do site público e abra o mesmo documento. Confira os metadados alterados, os idiomas RU/PT/EN e as mesmas URLs. Para experimentar a indexação, você também pode acrescentar temporariamente uma expressão distintiva ao título português, salvar e buscá-la em **Somente títulos**. Depois restaure pelo histórico.
8. Abra **Histórico**, filtre pelo ID do documento e expanda **Ver alterações**. Clique em **Revisar restauração** na alteração mais recente e confira a inversão dos valores. **Confirmar e salvar** restaura o estado anterior e registra outra operação no histórico. Recarregue o leitor e a busca para conferir a restauração.
9. Se fizer várias alterações, desfaça da mais recente para a mais antiga. O histórico guarda snapshots dos arquivos afetados; uma restauração é recusada quando esses arquivos já receberam mudanças posteriores, mesmo em outro documento. Esse bloqueio impede apagar trabalho posterior. Não altera os textos originais.
10. Para conferir a proteção entre abas, abra o mesmo documento em duas abas antes de salvar. Salve uma mudança na primeira; na segunda tente gerar a prévia ou salvar uma prévia antiga. Deve aparecer uma mensagem pedindo para reabrir o documento. As alterações mais recentes não devem ser sobrescritas.
11. No celular ou com a janela estreita, confira os filtros e formulários em uma coluna. A tabela da prévia pode ser rolada horizontalmente. Ao sair de uma edição com alterações não salvas, o navegador pede confirmação para descartá-las.

Ao terminar, use o histórico para desfazer as alterações feitas somente para experimentar. O histórico das gravações permanece disponível; o estado anterior de uma restauração também pode ser recuperado quando não houver conflito posterior.

## Histórico, publicação e recuperação

O catálogo e o manifesto continuam versionados no Git. A fila é `docs/revisao-markdown/pendencias.csv`; prioridade e motivo editados são preservados por novas gerações desse relatório, assim como status e notas. Os diagnósticos e as contagens antigas nos relatórios de conversão continuam sendo o registro da triagem original; a fila na interface lê o CSV atual.

Cada gravação guarda cópias completas dos arquivos modificados, antes e depois, comprimidas em `.local/editorial/history/`. Não inclui cópias dos corpos dos documentos. O histórico **não entra no Git e não é enviado ao GitHub**; para guardá-lo em outro local, copie esse diretório. Não apague `.local/editorial/` se quiser manter as opções de desfazer. O SQLite continua sendo um índice derivado, reconstruível.

Uma prévia vale por 15 minutos e só pode ser confirmada se catálogo, manifesto e fila continuarem na mesma versão. Uma nova edição no formulário descarta a prévia visível. As gravações são serializadas; o servidor também impede dois processos de backend no mesmo acervo. Requisições editoriais exigem origem local e um token da sessão do backend, sem introduzir contas ou login.

Antes de escrever, o backend prepara o novo índice e registra o histórico. Durante a publicação existe um marcador `.local/editorial/pending.json`. Uma interrupção nesse ponto leva à recuperação do estado anterior na próxima inicialização e à reconstrução do índice quando necessário. Se houver edições externas incompatíveis nos mesmos arquivos durante essa interrupção, a inicialização para para preservar ambos os estados. Nesse caso, mantenha `.local/editorial/` e os arquivos existentes para análise; não exclua o marcador manualmente.

O backend verifica os dados como parte normal da prévia e da gravação. Essas verificações operacionais fazem parte da implementação; nenhuma suíte de testes nem servidor de teste foi executado nesta entrega.

## Endpoints editoriais

| Método e URL | Função |
| --- | --- |
| `GET /api/editorial/session` | Sessão local, revisão e vocabulários de prioridade/status |
| `GET /api/editorial/queue` | Fila com filtros e paginação |
| `GET /api/editorial/documents/ID` | Metadados, associações e pendências de um documento |
| `GET /api/editorial/history?document=ID` | Até 100 operações recentes, com filtro opcional por documento |
| `POST /api/editorial/preview` | Validar e preparar proposta de edição ou restauração |
| `POST /api/editorial/save` | Confirmar a prévia existente e registrar o histórico |

As APIs públicas de consulta continuam disponíveis. Escritas são aceitas somente nos dois endpoints editoriais acima, por POST; não há escrita genérica de arquivos pela API.
