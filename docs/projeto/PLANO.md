# Plano de evolução do acervo

## Autorização e escopo

Em 16/10/2026, foi autorizada a primeira entrega: catálogo padronizado e backend local em Python. Preservar documentos, traduções, IDs, URLs e a publicação estática. Aproveitar o acervo metodológico local, registrar decisões e verificar o resultado. **Não fazer commit até aprovação do usuário.** Escolhas técnicas reversíveis podem ser resolvidas durante a implementação.

## Entregas

1. **Validada pelo usuário e commitada (`f90937c`).** Cadastro unificado, migração verificável, validação, exportação do manifesto compatível, índice SQLite e API local de consulta. O servidor também apresenta o site existente.
2. **Validada manualmente pelo usuário e commitada (`1a7b134`).** Busca integral com filtros, resultados contextualizados, paginação e retorno à consulta. Na publicação estática, busca limitada aos títulos do manifesto. Não foram executados testes pelo assistente nesta entrega por solicitação do usuário; roteiro em `BUSCA-MANUAL.md`.
3. **Área editorial em evolução.** Primeira parte validada em `c971fcf`; importação validada em `7b569a2`; correção dos cabeçalhos validada em `eb9da8a`. A integração do leitor com metadados/importação e a edição de versões Markdown com prévia e histórico foram testadas manualmente e aprovadas pelo usuário, com commits autorizados nesta rodada e sem push. O retorno conserva contexto e tenta recuperar a posição sem alterar o marcador. Roteiro em `LEITOR-EDITORIAL.md`. Não foram executados testes pelo assistente. O refinamento do painel e da área editorial foi incorporado à entrega. Correções por trecho no estudo foram entregues em `b96701f`.
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

O usuário validou também a correção e autorizou os dois commits, concluídos separadamente em `7b569a2` e `eb9da8a`, sem push. O primeiro inclui as traduções 2676–2678 importadas pelo usuário e seus cadastros. Em seguida, autorizou o leitor integrado ao painel e a edição de Markdown. Essa nova entrega permanece sem commit/push e sem execução de testes; as contagens dos manuais foram atualizadas para o catálogo com essas traduções.

Após inspeção inicial da integração, o usuário antecipou os ajustes de UX/UI e solicitou paginação por subcoleção, datas coletadas junto dos títulos e navegação anterior/próximo. Essas alterações estão implementadas para avaliação conjunta com a integração, sem novo commit/push nem execução de testes pelo assistente. O roteiro `UX-CATALOGO.md` contém um percurso com paginação e travessia entre documentos. Correções por trecho no modo estudo continuam planejadas.

A migração e a compatibilidade do manifesto foram verificadas; os testes de consulta e HTTP com acervo de teste passaram. A varredura adicional do acervo real foi interrompida após detectar uma edição concorrente. O usuário confirmou que corrigiu apenas uma tabela em `showtrials-1699.ru.md`; seu hash foi atualizado no catálogo. Por solicitação do usuário, não foram repetidos testes por essa alteração. Após inspeção e autorização do usuário, a primeira entrega foi commitada em `f90937c`, incluindo essa correção e seu hash. A segunda entrega e a primeira parte editorial foram testadas manualmente e aprovadas pelo usuário. A continuidade atual da área editorial está registrada na entrega 3 acima.


## Aprovação da integração e dos ajustes de interface

Após validar o editor, revisar a interface e confirmar a correção do carregamento editorial, o usuário aprovou a entrega e autorizou os commits. A entrega compreende edição Markdown com prévia/histórico, integração do leitor, painel compacto com retomada, menus consistentes, datas ShowTrials, paginação e navegação sequencial. O assistente não executou testes, conforme solicitado; a validação foi manual pelo usuário. Os commits são locais; nenhum push foi solicitado. Correções de tradução por trecho no estudo permanecem como próxima entrega planejada.


## Correções de tradução no modo estudo — aprovadas pelo usuário

Após os commits f87ff2f e 2acd034, o usuário autorizou a terceira entrega sem commit/push e sem execução de testes. Implementada correção de bloco ou seleção exata de tradução PT/EN Markdown no próprio modo estudo, com prévia, diferenças, proteção do original, conferência de versão/intervalo e gravação pelo histórico existente. O leitor e o índice são atualizados após salvar; não há alinhamento automático ou publicação. Roteiro manual em CORRECOES-NO-ESTUDO.md. O usuário testou, confirmou o funcionamento e autorizou o commit. Nenhum teste foi executado pelo assistente; sem push.


## Estabilização e cadastro local — implementados para avaliação

A correção por trecho foi aprovada e commitada em b96701f, sem push. O usuário autorizou revisão de estabilização e cadastro individual de documentos, coleções e subcoleções, com prévia e histórico, sem testes/commit/push. Implementados os formulários, endpoints locais e recuperação de novas entidades; preservados o acervo e as URLs existentes. Revisão por inspeção documentada em ESTABILIZACAO.md, com roteiro em CADASTRO-LOCAL.md. Avaliação manual pendente antes de considerar a rodada estável para trabalho continuado. Upload de capas, importação em lote e consolidação ampla do CSS seguem registrados como melhorias posteriores.


## Importação em lote — implementada para avaliação

O usuário aprovou a direção do cadastro individual e pediu a próxima entrega. Implementada importação de até 100 originais novos Markdown/TXT com CSV de metadados, coleções por linha ou padrão, diagnóstico bloqueante, avisos de duplicidade, prévia individual e confirmação conjunta. Uma transação/histórico engloba arquivos, catálogo, manifesto, busca e fila; a restauração é do lote inteiro. O cadastro anterior continua preservado e ambas as entregas permanecem sem commit/push. Nenhum teste executado pelo assistente. Roteiro em IMPORTACAO-EM-LOTE.md. Upload de capas permanece como melhoria posterior.


## Versionamento do cadastro e da importação em lote

O usuário autorizou o commit das entregas de estabilização, cadastro individual e importação em lote. São versionadas juntas, pois compartilham formulários e transações editoriais. Não foram executados testes pelo assistente e não houve push. A autorização de versionamento não substitui a conferência visual ampla e o exercício completo de restauração descritos em ESTABILIZACAO.md.

Pendências atuais: upload local de capas com prévia/histórico; consolidação do CSS acumulado e avaliação visual em celular/desktop/teclado; backup do histórico local; ferramentas de pesquisa (consultas salvas, anotações, dossiês, citações e exportações conjuntas). Importação de traduções em lote e pacotes ZIP/JSON permanecem extensões futuras, sem implementação nesta rodada.


## Base visual stable-week-1 — pronta para uso prático pelo responsável

Após o commit 0d61f4f, o usuário solicitou consolidar o CSS e ajustar o JavaScript visual necessário, mantendo o layout aprovado, para uma semana de testes práticos próprios. Foram organizados os componentes em assets/css/, removidas regras antigas e unificados os estados/medidas do painel. Sem alteração do acervo, APIs ou URLs. Sem testes executados pelo assistente, commit ou push nesta rodada. O roteiro de início, observação e relato de problemas está em SEMANA-ESTAVEL.md. Durante a semana, priorizar correções pontuais dos problemas encontrados; novas funcionalidades ficam para depois da observação prática.

Posteriormente, o usuário autorizou o commit e o push da consolidação, incluindo o envio dos commits locais pendentes. A validação prática permanece a cargo do usuário; o assistente não executou testes.

## Individualização de confessionezhov

Entrega autorizada: preservar a compilação e seus três arquivos, derivar 24 peças com 72 edições, associá-las à coleção existente em uma subcoleção própria, registrar proveniência e divergências, atualizar catálogo, manifesto e índice local. A operação usa o histórico editorial recuperável e acrescenta a conferência dos recortes à fila. O roteiro de conferência, os limites da derivação e os endereços estão em ../pesquisa/individualizacao-ezhov/README.md. Não executar testes, commit ou push. A revisão manual do responsável permanece pendente; a divisão não resolve divergências históricas nem confirma novo alinhamento de parágrafos.

Após conferir o funcionamento, o usuário aprovou a entrega e autorizou commit e push. A autorização inclui a publicação das peças e dos registros associados; não houve execução de testes pelo assistente.

## Coleção militar de 1934–1936

Incorporadas localmente as 20 entradas autorizadas (Conselho de 1935: 13; indústria de 1934–1936: sete), em russo, recuperadas por capturas do Wayback após indisponibilidade do Istmat. Fontes brutas, metadados e receitas preservados; catálogo, manifesto e busca atualizados, sem mudar o acervo anterior ou criar relações entre coleções. Foram acrescentadas 20 pendências à fila; a prioridade de conferência são as tabelas e as limitações da edição de cada peça. A documentação de 1937 e os depoimentos investigativos permanecem fora desta entrega. Conferência manual pendente conforme ../pesquisa/colecao-militar-1934-1936/README.md. Sem testes executados, commit ou push.

Após avaliação manual, o responsável aprovou commit e push da coleção militar. Enviado 5862d9f, incluindo o commit anteriormente pendente da barra lateral. Autorizada a continuação com a coleção de 1937, mantendo as regras de trabalho.

## Caso Tukhachevsky e documentação militar de 1937

Criada separadamente a coleção caso-tukhachevsky-1937, com quatro subcoleções e 11 entradas: dez textos russos recuperados pelo Wayback e uma ficha de fontes do julgamento. PDFs RU/EN já locais foram preservados e disponibilizados como fontes, sem falsa transcrição ou pareamento. Catálogo, manifesto, pendências e busca atualizados; 201 notas finais convertidas. Pendentes conferência manual e edição textual do PDF russo. Roteiro em ../pesquisa/colecao-tukhachevsky-1937/README.md. Sem testes, commit ou push desta nova entrega.

## Oficina de pesquisa — levantamento e plano de incorporação

Em 19/10/2026, após a adoção da interface Carmim, o responsável solicitou o levantamento dos recursos dos pacotes importados. Inventariados 291 arquivos técnicos, com 165 conteúdos distintos; os 125 scripts do Discovery repetidos entre os dois pacotes principais são idênticos. Foram distinguidos algoritmos/dados reutilizáveis, propostas documentadas e ferramentas ainda por integrar, especialmente OCR e tradução integral por provedor.

O [plano de ferramentas de pesquisa](PLANO-FERRAMENTAS-PESQUISA.md) organiza nove entregas: oficina de arquivos/tarefas; catalogação, nomes e glossário; PDF/Word; OCR; passagens/alinhamento; tradução; descoberta/deduplicação; pesquisa transversal; preparação de publicação. A recomendação inicial é F01, com diagnóstico de Markdown como tarefa piloto. O [levantamento com evidências](../pesquisa/ferramentas-importadas/LEVANTAMENTO.md) e os inventários conservam caminhos e limites. Planejamento apenas: sem implementação dessas ferramentas, instalação, testes, commit ou push nesta tarefa.

## Oficina PDF/OCR — início em 20/10/2026

Primeira entrega implementada para validação manual: recepção local de PDF, extração pesquisável em processo separado, persistência por página, cadastro com prévia/histórico e teclado virtual russo nos editores existentes. Não executa OCR nem cria automaticamente edições públicas. Referências candidatas de parágrafo preparam citações revisáveis. Próxima etapa: revisão durável de páginas/fronteiras e integração do fac-símile ao modo estudo; depois OCR rus/eng/por e publicação estática selecionada. Roteiro e pendências em [PDF — entrega 1](pdf-ocr/ENTREGA-01.md).

## Projetos e instrumentos de pesquisa — 20/10/2026

Implementado para validação manual o contexto mínimo de projetos locais: vínculos com documentos e PDFs, projeto ativo, prévia e histórico, filtro de fontes e integração à bancada. Não há migração do acervo ou publicação de projetos. Próxima entrega: recepção de fontes maiores e manipulação PDF com derivados/proveniência, começando por intervalos e divisão. Arquitetura, roteiro manual e pendências em [Projetos e ferramentas](PROJETOS-E-FERRAMENTAS.md).

## Workspace e versões — 20/10/2026

Ajustada a bancada para navegação na mesma guia, explorador lateral e seletor de projetos. Implementadas versões de trabalho por projeto/edição, incluindo correção de trecho e importação Markdown no projeto, com histórico e incorporação explícita ao acervo. Edição sem projeto mantém o fluxo principal. Aguardando validação manual conforme [Workspace e versões](WORKSPACE-E-VERSOES.md); PDF/OCR permanece a próxima frente funcional.

## Manipulação PDF — 20/10/2026

Entregue para validação manual: upload em fluxo de até 256 MiB por padrão (configurável), extração por seleção ordenada e divisão por quantidade/intervalos, com prévia, fila, retomada, derivados, correspondência de páginas e vínculos recuperáveis no projeto. Ferramenta disponível no painel da bancada e na área editorial. Piloto com o PDF integral de Tukhachevsky passou em cópia isolada. Próxima frente: revisão durável por página e OCR rus/eng/por. Combinar PDFs, girar páginas e revisão visual geral permanecem pendentes. Consulte [Entrega PDF 2](pdf-ocr/ENTREGA-02-PDF.md).

## Revisão por página e OCR — 20/10/2026

Implementadas revisão durável com prévia/histórico/conflitos, estados de conferência e OCR opcional rus/eng/por em lotes selecionados. Disponíveis na fonte editorial e no instrumento PDF da bancada. Extração nativa, candidatos OCR e revisão são preservados separadamente; não há gravação automática no acervo. Pilotos RU/EN e verificações isoladas passaram. Aguarda validação manual conforme [Entrega PDF 3](pdf-ocr/ENTREGA-03-REVISAO-OCR.md). Próxima frente: vínculos fonte/documento, fac-símile no estudo e revisão de fronteiras/alinhamento para citações; depois incorporação editorial e publicação selecionada.

## Fac-símiles no estudo — 20/10/2026

Implementados vínculos locais documento/fonte/páginas, separados por contexto, com prévia, histórico e proteção concorrente. O estudo consulta PDF/transcrição e associa manualmente blocos Markdown a páginas por idioma/versão, sinalizando desatualizações e fornecendo referências com IDs/hashes. Documentos monolíngues também podem usar estudo. Aguarda validação manual conforme [Entrega PDF 4](pdf-ocr/ENTREGA-04-FACSIMILES.md). Próximas frentes: delimitação visual/divisão e união de unidades, continuação entre páginas, incorporação da transcrição revisada e publicação selecionada dos fac-símiles. Sem commit ou push.
