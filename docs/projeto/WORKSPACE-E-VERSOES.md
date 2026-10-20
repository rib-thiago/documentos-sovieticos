# Workspace de projeto e versões de trabalho

20/10/2026 — alteração implementada para conferência manual. Não foram executados testes, servidor, navegador, instalações, commit ou push.

## Mudança de comportamento

A bancada distingue explicitamente dois contextos:

| Contexto | Gravação de texto | Efeito no acervo |
| --- | --- | --- |
| Acervo, sem projeto | Editor/correção editorial existentes, com prévia e histórico | Atualiza a edição principal local ao confirmar a gravação. |
| Workspace de projeto | Editor e correção de trecho gravam uma versão de trabalho por projeto/documento/idioma | Não reescreve `originais/`, catálogo, manifesto ou busca. |
| Incorporação explícita | Versão de trabalho salva, diferenças contra o acervo atual e confirmação específica | Atualiza a edição principal local, projeções e índice, com histórico editorial. |

“Atualizar a edição principal local” não é publicar no GitHub. Commit/push permanecem separados e dependem de autorização. O projeto não envia automaticamente suas versões ao site público.

A versão do projeto é criada ao salvar a primeira alteração. Até então a leitura utiliza a edição atual do acervo. Uma versão de trabalho salva conserva a origem e fica isolada das alterações posteriores no acervo. Não há congelamento automático de todos os documentos ao criar um projeto.

## Interface

- **Abrir workspace** funciona mesmo em projeto sem documentos, mostrando a bancada e sua navegação.
- Links de documentos na página do projeto abrem a bancada na mesma guia, com `projeto=ID` explícito na URL.
- A lateral contém seletor de workspace, filtro e lista dos documentos vinculados, fontes PDF e atalhos de ferramentas/configuração.
- Documentos abrem como abas internas; cada projeto mantém seu conjunto de abas. A opção de abrir mais documentos lista os documentos do projeto quando há um workspace selecionado.
- O seletor oferece **Acervo · sem projeto** para trabalhar fora desse contexto. A existência de um projeto preferido no backend não transforma silenciosamente qualquer leitura/edição em edição daquele projeto.
- Notas de sessão, contexto de leitura e buffers da bancada usam chaves por projeto. Notas continuam sendo notas da sessão, não uma nova base durável de anotações.
- As versões salvas do projeto aparecem na leitura e no estudo daquele workspace. Uma tradução ainda ausente no acervo pode ser preparada no editor do projeto selecionando português ou inglês.
- A importação Markdown no editor do projeto carrega o arquivo como candidato, mostra identificação/diferenças e exige confirmação para salvar no projeto. Não usa a importação canônica como atalho oculto.
- No modo estudo, **Corrigir tradução** salva no projeto quando há contexto de projeto. Fora dele, mantém o fluxo editorial já existente.
- Ficha catalográfica no projeto é consulta ao cadastro do acervo. Metadados exclusivos por projeto ainda não são implementados; não oferecer edição canônica silenciosa a partir da ficha do workspace.
- Exportações do workspace usam sufixo `.projeto.md` para distinguir a cópia de trabalho.

Fontes PDF continuam abrindo na área editorial, na mesma guia e com o projeto no endereço. O encaixe de cada ferramenta como uma aba/painel interno é etapa posterior; esta entrega muda a navegação dos documentos e a semântica de gravação, sem prometer que todas as ferramentas já sejam painéis móveis.

## Conferência manual

### 1. Workspace e navegação

1. Reinicie o backend com `python3 -m backend` e abra http://127.0.0.1:8000/editorial#/projetos . Recarregue com Ctrl+Shift+R se necessário.
2. Abra um projeto e clique em **Abrir workspace**, ou num documento vinculado. A navegação deve acontecer na mesma guia do navegador.
3. Confira o seletor lateral, a lista de documentos e o destaque do documento aberto. Clique em outro documento: ele deve abrir numa aba da própria bancada.
4. Troque de projeto no seletor. Se o documento atual também pertencer ao destino, ele permanece aberto naquele contexto; senão, abre o primeiro documento disponível, ou a bancada vazia. As abas do projeto anterior ficam separadas.
5. Confira **Acervo · sem projeto** e retorne ao projeto. Não confundir esse contexto explícito da URL com o projeto preferido do formulário editorial.

### 2. Edição isolada e persistente

1. Escolha um documento pequeno com Markdown e faça uma alteração reconhecível no instrumento Markdown do projeto.
2. Clique em **Revisar e salvar no projeto**, confira as diferenças, marque a confirmação e salve.
3. A leitura do workspace deve exibir a alteração. Abra o mesmo documento fora do projeto pelo seletor **Acervo · sem projeto**: a alteração não deve aparecer.
4. Reinicie o backend e retorne ao workspace. A versão de trabalho deve permanecer disponível.
5. Se o mesmo documento estiver em dois projetos, salve versões diferentes em cada um e alterne entre eles. Os textos não devem se misturar.
6. Para descartar apenas o buffer não salvo, use **Recarregar versão salva**. Fechar o navegador sem salvar pode perder o buffer; o navegador deve avisar. Gravações confirmadas estão no banco local.

### 3. Tradução e correção por trecho

1. No editor do projeto, escolha português ou inglês e carregue um Markdown pequeno pertencente ao documento selecionado.
2. Confira a identificação e as diferenças antes de salvar. Divergências de nome/cabeçalho são sinalizadas; segmentação/alinhamento continuam sujeitos à revisão editorial.
3. Uma tradução nova deve ficar disponível no leitor do projeto após a gravação, sem surgir no acervo sem projeto.
4. Em modo estudo, corrija um trecho de uma tradução e confirme **Salvar no projeto**. Confira novamente fora do projeto: a tradução principal deve permanecer inalterada.

### 4. Incorporação explícita

1. Com uma versão já salva no projeto, clique em **Incorporar versão salva ao acervo…**. Digitar um rascunho não salvo não habilita sua incorporação.
2. Confira as diferenças contra a edição principal atual. Se ela mudou desde a origem do trabalho, haverá um aviso; não fazemos mesclagem automática.
3. Cancele uma vez: o acervo deve permanecer igual.
4. Prepare novamente e marque explicitamente a confirmação de incorporação ao acervo local. Confirme.
5. Abra o documento sem projeto e confira texto, idiomas e busca local. O histórico editorial deve registrar a alteração e a origem no projeto.
6. Não faça push para validar: o GitHub continua exibindo a publicação anterior até uma publicação autorizada.

### 5. Histórico e conflitos

1. Faça duas gravações numa versão de projeto. No instrumento Markdown, abra **Histórico desta versão no projeto** e prepare a restauração de um estado anterior. Confira as diferenças e confirme.
2. Restaurar o estado anterior à primeira gravação remove a versão própria e volta a consultar a edição do acervo; não apaga o original nem o histórico.
3. Abra a mesma versão do projeto em duas guias apenas para esta conferência. Salve numa delas; tente salvar uma prévia antiga na outra. Deve ser rejeitada, mantendo o texto digitado para cópia/revisão.
4. Prepare uma incorporação e, em outra guia, modifique a versão do projeto ou a edição principal. A incorporação antiga deve ser recusada até nova prévia.
5. Arquive um projeto e confira que ele permanece consultável, mas não aceita novas gravações ou incorporações.

## Persistência e proteção

Versões e histórico ficam nas tabelas `workspace_editions` e `workspace_edition_history` de `.local/research/projects.sqlite3`. O esquema é aditivo: não recria projetos existentes nem altera seus vínculos. IDs de documento/edição continuam os do acervo.

Cada versão guarda revisão, texto, origem textual e SHA-256 da origem; cada gravação tem estado anterior/posterior. Mesmo remover uma versão própria mantém um contador de revisão, para não aceitar uma prévia antiga por coincidência. As prévias expiram em 15 minutos ou no reinício do backend.

Incorporação usa as rotinas editoriais existentes e seus controles de catálogo/arquivos. A prévia preparada para incorporação não pode ser gravada pelo endpoint editorial comum: exige o caminho de confirmação específica do workspace. Mudanças no projeto, na versão de trabalho ou no acervo invalidam as operações pertinentes.

**Backup:** encerrar o backend e copiar toda `.local/research/`. O banco contém versões de trabalho e históricos que não são reconstruídos a partir da busca nem enviados ao Git. Recuperação do acervo após incorporação usa o histórico editorial em `.local/editorial/`; mantenha também seu backup.

## Limites desta etapa

Não implementa merge automático, alinhamento entre idiomas, edição de ficha catalográfica exclusiva por projeto, busca transversal nos rascunhos, painéis arrastáveis, controle multiusuário ou publicação automática. A oficina PDF/OCR segue a sequência registrada no plano. Originais TXT continuam preservados; não há conversão silenciosa deles em uma edição Markdown principal.

## Ajuste posterior à auditoria: entrada sem projeto

O padrão definido pelo pesquisador é **sem projeto ativo ao abrir o site sem contexto explícito ou recarregá-lo com F5**. Um link explícito de workspace continua permitindo entrar no projeto; a retomada geral não escolhe um projeto antigo automaticamente. O recarregamento preserva o documento/idioma, mas volta à edição do acervo, sem apagar a versão de trabalho. Marcas de leitura são separadas por projeto e acervo; as antigas sem contexto são mantidas apenas no acervo. Falha na consulta de histórico não bloqueia o editor. Evidências e roteiro atualizado em [Auditoria e correções](revisoes/AUDITORIA-WORKSPACE-2026-10-20.md).
