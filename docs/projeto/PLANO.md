# Plano de evolução do acervo

## Autorização e escopo

Em 16/10/2026, foi autorizada a primeira entrega: catálogo padronizado e backend local em Python. Preservar documentos, traduções, IDs, URLs e a publicação estática. Aproveitar o acervo metodológico local, registrar decisões e verificar o resultado. **Não fazer commit até aprovação do usuário.** Escolhas técnicas reversíveis podem ser resolvidas durante a implementação.

## Entregas

1. **Validada pelo usuário e commitada (`f90937c`).** Cadastro unificado, migração verificável, validação, exportação do manifesto compatível, índice SQLite e API local de consulta. O servidor também apresenta o site existente.
2. **Validada manualmente pelo usuário; commit autorizado.** Busca integral com filtros, resultados contextualizados, paginação e retorno à consulta. Na publicação estática, busca limitada aos títulos do manifesto. Não foram executados testes pelo assistente nesta entrega por solicitação do usuário; roteiro em `BUSCA-MANUAL.md`.
3. **Planejada — área editorial.** Fila de revisão, edição com prévia e histórico, importação de traduções e conferência de alinhamento.
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

A migração e a compatibilidade do manifesto foram verificadas; os testes de consulta e HTTP com acervo de teste passaram. A varredura adicional do acervo real foi interrompida após detectar uma edição concorrente. O usuário confirmou que corrigiu apenas uma tabela em `showtrials-1699.ru.md`; seu hash foi atualizado no catálogo. Por solicitação do usuário, não foram repetidos testes por essa alteração. Após inspeção e autorização do usuário, a primeira entrega foi commitada em `f90937c`, incluindo essa correção e seu hash. A segunda entrega foi testada manualmente e aprovada pelo usuário, que autorizou seu commit. A próxima etapa planejada é a área editorial: começar pela fila de revisão e edição de metadados com prévia das alterações; depois acrescentar edição de textos, histórico e importação de traduções com conferência de alinhamento.
