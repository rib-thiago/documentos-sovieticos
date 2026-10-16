# Plano de evolução do acervo

## Autorização e escopo

Em 16/10/2026, foi autorizada a primeira entrega: catálogo padronizado e backend local em Python. Preservar documentos, traduções, IDs, URLs e a publicação estática. Aproveitar o acervo metodológico local, registrar decisões e verificar o resultado. **Não fazer commit até aprovação do usuário.** Escolhas técnicas reversíveis podem ser resolvidas durante a implementação.

## Entregas

1. **Validada pelo usuário e commitada (`f90937c`).** Cadastro unificado, migração verificável, validação, exportação do manifesto compatível, índice SQLite e API local de consulta. O servidor também apresenta o site existente.
2. **Validada manualmente pelo usuário e commitada (`1a7b134`).** Busca integral com filtros, resultados contextualizados, paginação e retorno à consulta. Na publicação estática, busca limitada aos títulos do manifesto. Não foram executados testes pelo assistente nesta entrega por solicitação do usuário; roteiro em `BUSCA-MANUAL.md`.
3. **Área editorial em evolução.** A primeira parte foi validada manualmente e commitada em `c971fcf`: fila de revisão, edição de metadados e associações, prévia e histórico. A importação de traduções está implementada e aguarda teste manual do usuário, sem commit ou push: seleção explícita de documento/idioma, identificação, diferenças, renderização, diagnóstico estrutural sem alinhamento automático e histórico do conteúdo. Nenhum teste foi executado pelo assistente nesta etapa; roteiro em `IMPORTACAO-TRADUCOES.md`. Integração direta com o leitor, edição do Markdown, correções por trecho no estudo e refinamento geral de layout/UX/UI continuam planejados.
4. **Planejada — ferramentas de pesquisa.** Consultas salvas, anotações, dossiês, citações e exportações conjuntas.

## Critérios da primeira entrega

- Um documento tem um cadastro, independentemente das coleções em que aparece; as edições por idioma têm IDs próprios.
- Coleções e subcoleções usam a mesma estrutura e associações ordenadas explícitas.
- Nenhum arquivo de conteúdo ou tradução é reescrito pela migração.
- O manifesto gerado tem o mesmo conteúdo do manifesto anterior, preservando as rotas e o comportamento do site.
- Datas WordPress ficam separadas de datas históricas. Classificações automáticas mantêm sua procedência e não viram autoria histórica.
- O catálogo versionado funciona sem o diretório temporário. SQLite é derivado e pode ser reconstruído.
- O ambiente local inicia com Python, sem npm ou instalação de pacotes para o backend.
- API com consulta de documentos, coleções, vocabulários, paginação e filtros; busca integral como base para a próxima interface.
- Testes de migração, preservação, busca e HTTP; manual de inicialização e URLs de teste.

## Decisões iniciais

- Usar a biblioteca padrão de Python: HTTP e SQLite com FTS5, verificando a disponibilidade de FTS5 ao iniciar.
- Manter Markdown e metadados versionados como base; o banco e o índice não serão uma segunda fonte de verdade do catálogo.
- Manter o frontend atual e seus caminhos. A primeira entrega não redesenha a navegação nem cria formulários de edição.
- O backend expõe consulta; escrita editorial será uma entrega própria. Não haverá necessidade de contas para o teste local.

## Continuidade

Consultar `docs/projeto/DECISOES.md` e o manual do backend para decisões consolidadas, comandos e validações. Atualizar este plano ao concluir a entrega ou mudar o escopo.

O commit `edbab93` publicou as traduções e o registro da tabela corrigida; o push para `origin/main` foi concluído antes de iniciar a área editorial. O usuário autorizou a implementação editorial com revisão manual, sem execução de testes e sem commit dessa nova etapa. A implementação mantém os arquivos de conteúdo e as URLs e utiliza a fila CSV existente; seu histórico de gravações fica somente em `.local/editorial/`.

Após realizar o roteiro de edição, gravação e restauração, o usuário confirmou o funcionamento da área editorial e autorizou seu commit, concluído em `c971fcf`. Em seguida, autorizou a importação local de traduções, implementada com identificação explícita de documento/idioma, comparação antes de substituir versões, histórico do conteúdo e atualização do catálogo e da busca. Diferenças de parágrafos são diagnosticadas sem presumir alinhamento automático correto. Essa implementação aguarda a verificação manual do usuário; não foram executados testes, commit ou push.

O usuário testou o mecanismo de tradução e confirmou seu funcionamento, apontando dois ajustes de cabeçalhos. Foi corrigida a separação entre envelope de exportação e corpo, removendo sua influência nas contagens e no estudo e gerando somente um cabeçalho na reexportação. A correção aguarda a conferência manual específica descrita em `IMPORTACAO-TRADUCOES.md`, sem testes executados pelo assistente, commit ou push.

A migração e a compatibilidade do manifesto foram verificadas; os testes de consulta e HTTP com acervo de teste passaram. A varredura adicional do acervo real foi interrompida após detectar uma edição concorrente. O usuário confirmou que corrigiu apenas uma tabela em `showtrials-1699.ru.md`; seu hash foi atualizado no catálogo. Por solicitação do usuário, não foram repetidos testes por essa alteração. Após inspeção e autorização do usuário, a primeira entrega foi commitada em `f90937c`, incluindo essa correção e seu hash. A segunda entrega e a primeira parte editorial foram testadas manualmente e aprovadas pelo usuário. A continuidade atual da área editorial está registrada na entrega 3 acima.
