# Revisão de estabilização do leitor e da área editorial

## Escopo e evidência

Revisão feita por leitura do código, dos contratos do catálogo, da projeção do manifesto e do histórico. As entregas anteriores foram aprovadas manualmente pelo usuário. Esta rodada ainda depende de validação manual: não foram executados testes, navegador automatizado, servidor de demonstração, compilação, commit ou push. O acervo existente e seus arquivos de metadados não foram regravados durante a implementação.

O roteiro de cadastro e restauração está em [CADASTRO-LOCAL.md](CADASTRO-LOCAL.md). Os fluxos já existentes continuam documentados em LEITOR-EDITORIAL.md, IMPORTACAO-TRADUCOES.md e CORRECOES-NO-ESTUDO.md.

## Problemas tratados nesta rodada

| Área | Problema identificado no código | Tratamento |
| --- | --- | --- |
| Catálogo editorial | Coleções carregadas apenas ao iniciar a página | Sessão e coleções são buscadas novamente ao entrar em cada tela; cadastros e restaurações passam a aparecer nos formulários seguintes |
| Idiomas | Alguns títulos dependiam de PT/RU; inglês poderia aparecer como ID ou vazio | Fallback PT → RU → EN → ID no leitor, catálogo e ordenação do índice; título inglês editável nos metadados |
| Original | Importação/correção presumiam russo quando presente | Novos documentos registram explicitamente o idioma original; fluxos consultam esse dado, com a regra legada preservada para o acervo antigo |
| Coleções vazias | Array vazio de subcoleções era tratado como lista existente | Coleções sem subcoleções apresentam diretamente sua lista de documentos, inclusive vazia |
| Primeira subcoleção | A compatibilidade de uma coleção antiga poderia omitir o novo grupo no manifesto | Acrescenta a projeção de subcoleções ao pai sem alterar seu ID, seus textos ou associações existentes |
| Histórico | Restauração só recarregava documentos, edições e associações | Inclui todos os arquivos canônicos alterados, contemplando coleções e proveniência |
| Arquivos novos | Histórico aceitava somente MD | Recupera também TXT criado pelo cadastro, restrito a originais/ e aos arquivos da operação |
| Recuperação | Telas pressupunham que toda operação pertencia a um documento existente | Histórico identifica coleção/documento; restauração de criação não oferece retorno para um documento removido |
| Revisão | Novos documentos poderiam não aparecer na fila | Cadastro cria pendência média para conferir metadados, conteúdo e apresentação, recuperável junto ao cadastro |
| Interação | Escape de uma janela de correção também poderia fechar controles atrás dela | O leitor deixa a janela modal tratar Escape quando ela está aberta |
| Exportação TXT | Fontes diferentes do ShowTrials podiam receber rótulo ID ShowTrials | Usa ID do documento para os demais originais |
| Apresentação | Formulários, ações e estados vazios precisavam acompanhar o novo cadastro | Estilos comuns, lateral com foco visível, campos fixos legíveis, ações responsivas e prévia de capa; conteúdo extenso é renderizado sob demanda |

## Pendências e prioridade

| Prioridade | Pendência | Próxima ação |
| --- | --- | --- |
| Antes de considerar esta rodada estável | Avaliação manual dos novos cadastros e restauração completa | Executar o exercício isolado de CADASTRO-LOCAL.md e relatar divergências |
| Antes do trabalho continuado | Conferir regressões dos fluxos usados diariamente | Abrir um documento antigo, alternar leitura/estudo, marcar/retomar, exportar; revisar sem salvar metadados/tradução e editor; conferir uma busca |
| Antes do trabalho continuado | Backup do histórico local | Copiar o projeto com backend parado, incluindo `.local/editorial/history/` |
| Média | Upload de capas diretamente pelo formulário | Acrescentar imagens ao protocolo de histórico sem misturar bytes de imagem com snapshots de texto; hoje a capa usa caminho existente |
| Implementada; validação manual pendente | Entrada de muitos documentos de uma vez | CSV + originais, prévia individual e restauração conjunta; roteiro em IMPORTACAO-EM-LOTE.md |
| Média | CSS acumulado em sucessivas rodadas | Consolidar os estilos do painel/editorial após validar o comportamento atual; não fazer uma troca ampla de seletores durante a estabilização funcional |
| Média | Verificação visual ampla de telas e navegadores | Comparar celular, desktop e teclado com o responsável; não foi simulada nesta rodada |
| Baixa | Identificação semântica de duplicidades e traduções | Continua fora do cadastro: os alertas atuais conferem metadados e arquivos, não o significado dos textos |
| Baixa | Mais idiomas e hierarquias mais profundas | A criação oferece RU/PT/EN e coleção → subcoleção, compatíveis com a interface atual |

O histórico usa snapshots dos arquivos canônicos. Uma restauração antiga pode conflitar com edições posteriores mesmo em outro documento. Isso é uma proteção existente, não restauração independente por campo. Não foi substituída por um novo sistema nesta rodada.

## Percurso de regressão manual recomendado

1. Reiniciar o backend atualizado e recarregar com Ctrl+Shift+R.
2. Abrir http://localhost:8000/#/doc/showtrials-1666. Conferir que o painel começa recolhido, Retomar aparece se houver marca e Fixar continua opcional.
3. No meio do documento, alternar leitura/estudo e parágrafo/paralelo. Conferir a posição e a continuidade dos controles.
4. Exportar PT/RU e conferir os nomes e o cabeçalho único. Abrir Correção de tradução, digitar e cancelar, sem gravar.
5. Abrir Editar → Editar; conferir metadados, idiomas e entrada lateral Editar Markdown. Digitar e sair confirmando o descarte, sem salvar.
6. Conferir uma lista de subcoleção com várias páginas e a travessia anterior/próximo entre páginas.
7. Fazer uma busca por título e uma por trecho no backend local.
8. Executar a criação de coleção, subcoleção e documento e desfazer na ordem indicada em CADASTRO-LOCAL.md.

A marcação manual de leitura permanece por sessão da aba. Correções do próprio parágrafo marcado podem exigir uma nova marca, como registrado no manual de correções. O site público continua estático: cadastros só serão publicados após uma decisão separada de commit/push.


## Autorização de versionamento

O usuário autorizou o commit conjunto do cadastro local e da importação em lote. Os registros acima descrevem a revisão por inspeção e os percursos de validação; não houve execução de testes pelo assistente. A avaliação visual ampla e o backup local continuam sendo passos de preparação para o trabalho continuado. Nenhum push foi solicitado.
