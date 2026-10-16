# Decisões do catálogo e backend — entrega 1

## D1. Fonte de verdade e compatibilidade

`data/catalog/` é o catálogo versionado. Documentos, versões por idioma, coleções e associações são registros independentes. SQLite é um índice descartável; não deve receber edição direta. `data/manifest.json` continua sendo o contrato do frontend estático e passa a ser gerado por `python3 -m backend.catalog export`.

A migração preservou o conteúdo e os bytes do manifesto inicial. O exportador conserva também ausências, campos extras e ordem das listas. A projeção guarda IDs globais e campos de compatibilidade para que as quatro coleções editoriais continuem funcionando ao lado das nove coleções importadas. Não há duplicação de valores legados: os campos de compatibilidade registram nomes/ordens, e o exportador consulta os valores padronizados. Novos títulos portugueses e outros metadados preenchidos no catálogo também são exportados.

Os caminhos `#/doc/ID`, `#/colecao/ID`, subcoleções e contexto de retorno continuam iguais. Os IDs de edições são `documento:idioma`; subcoleções usam internamente `colecao/slug`, permitindo repetir `investigacao` em processos diferentes.

## D2. Datas, autoria e classificação

As seis datas já cadastradas são conservadas em `historical_date.display`; `value` e `precision` permanecem sem inferência até revisão. Datas WordPress ficam exclusivamente em `source_metadata.wordpress_date`/`wordpress_modified`. O ID do usuário WordPress é `wordpress_author_id`, sem atribuição de autoria histórica.

Os 35 tipos já usados no ShowTrials receberam rótulos portugueses controlados. O método `rule_title_v4` e seus tipos coincidentes são copiados da tabela histórica, sem reclassificação silenciosa. Os sete registros editoriais sem tipo específico permanecem com `document_type: null` e podem ser encontrados pelo filtro `type=unspecified`. `kind` mantém a distinção geral entre documento e artigo.

Títulos russos, títulos portugueses e rótulos de autoria existentes foram preservados. Não foi executada nova tradução, inferência de pessoas, OCR ou deduplicação histórica. Relações entre versões editoriais e posts semelhantes devem ser avaliadas antes de qualquer fusão.

## D3. Uso da metodologia preservada

Foram importados campos selecionados de `showtrials_master_catalog.tsv` e `showtrials_document_types_v4.tsv` do pacote metodológico autorizado. `provenance.json` registra caminhos relativos e SHA256 dessas tabelas. O catálogo passa a conter os valores necessários; não abre o diretório temporário em execução.

As relações de coleção vêm do manifesto já conferido e preservam todas as associações e sua ordem, inclusive quando um documento aparece em vários processos. Não se usa `primary_collection` para restringir a busca. As tabelas de pessoas, aliases, organizações e papéis permanecem como material para a próxima etapa; não foram convertidas em relações históricas sem revisão.

## D4. Backend e índice

Python e biblioteca padrão: `http.server`, `sqlite3`, JSON e CSV. Não exige npm, pip, Poetry, framework ou serviço externo para iniciar este backend. A instalação de Python precisa oferecer SQLite FTS5; a inicialização confere isso e explica a falha quando ausente. O ambiente foi testado com Python 3.12.

O banco fica em `.local/catalog.sqlite3`, ignorado pelo Git. O índice novo é construído em arquivo temporário e substitui o anterior após concluir as transações. Chaves estrangeiras e consultas parametrizadas protegem a consistência. Uma revisão do catálogo define a identidade do índice, e hashes dos conteúdos são conferidos antes da reutilização. Não são armazenados trabalhos pessoais nesse banco descartável; anotações e decisões futuras precisam de persistência própria.

O serviço oferece apenas leitura nesta entrega e serve o frontend existente no mesmo endereço. A página `/local` reúne verificações manuais. A interface de busca, formulários, upload de traduções e edição editorial pertencem às entregas seguintes.

## D5. Busca e limites

FTS5 indexa todas as 2.197 versões, em Unicode, com títulos e texto. Os resultados são agrupados por documento, com idioma/edição do melhor resultado e trecho de contexto. Títulos têm maior peso que corpo. Filtros de idioma restringem a versão pesquisada; coleções/subcoleções consideram todas as associações. Paginação e ordenação pela fonte não duplicam registros por múltiplos vínculos.

`q` trata palavras como termos literais combinados por AND; aspas duplas delimitam uma frase. Não são expostos operadores SQL/FTS arbitrários. A busca não faz tradução entre idiomas, análise morfológica russa, resolução automática de aliases nem busca semântica. Títulos de todos os idiomas são incluídos nos metadados pesquisáveis; `language=pt` não significa que o título russo foi traduzido.

A extração para busca remove os marcadores de título e escapes Markdown e normaliza espaços. Os arquivos de leitura/exportação não são alterados. Links, notas e outros sinais podem permanecer no texto indexado; a limpeza editorial integral não é objetivo desta etapa.

## D6. Edição e ferramentas anteriores

Importadores e conversores anteriores que escreviam diretamente no manifesto recusam operações de escrita quando encontram o catálogo padronizado. Isso evita dois cadastros divergentes e não apaga dados. Verificadores e auditorias sem escrita continuam disponíveis. Uma nova importação de acervo exigirá adaptador para o catálogo, preservando metadados locais — trabalho posterior.

Edições intencionais de Markdown precisam da conferência editorial já existente. Depois de registrar uma correção na receita quando aplicável, use `refresh-files` para visualizar diferenças e `refresh-files --write` para atualizar os hashes das versões. Essa operação não certifica fidelidade à fonte nem substitui a revisão. Reiniciar o backend atualiza o índice. Metadados alterados exigem `export` antes da inicialização, para que site estático e API mostrem o mesmo cadastro.

## D7. Proteção dos arquivos de trabalho

O servidor publica somente `index.html`, `assets/`, `originais/` e o manifesto compatível. Não publica diretório temporário, arquivos Git, catálogo interno nem banco. A API retorna os registros necessários à consulta, sem fornecer navegação arbitrária de arquivos. O endereço inicial é `127.0.0.1`; não foi introduzido cadastro de usuários nesta etapa local.

## D8. Alteração externa durante a implementação

Durante a verificação HTTP do acervo real, `originais/showtrials/showtrials-1699.ru.md` foi substituído externamente por uma versão com tabela reorganizada; também apareceu seu arquivo auxiliar `Zone.Identifier`. O backend não realizou essa edição. A validação interrompeu corretamente o uso do hash anterior (`52db6ffb298dfb8497a8d4479300cc4651941691b1421d0215f77a46cba3a106`).

A versão presente foi preservada e seus bytes registrados explicitamente por `refresh-files --write` (`df58d2a5dd7f63352196b7c618df958a427c016c2f63931f3417931ec8b3092f`), sem certificação da revisão documental. O arquivo e o auxiliar são alterações externas, não parte da implementação do backend. As receitas da conversão anterior podem continuar apontando a divergência intencional dessa edição até uma revisão própria. O manifesto e todos os caminhos permaneceram iguais.

## D9. Busca na interface e publicação estática

A rota `#/busca` utiliza a API local quando disponível. Consultas vazias exploram o catálogo por filtros; consultas com palavras pesquisam títulos e corpo ou somente títulos. Resultados apresentam o trecho fornecido pela API como texto, sem interpretar HTML da fonte. Coleção e subcoleção usam os IDs existentes; categoria editorial e tipo documental específico são filtros separados. Não foi necessário alterar a API ou o catálogo nesta entrega.

Sem a API, a página pesquisa os títulos do manifesto já carregado, com aviso visível e sem baixar todos os documentos. Tipos documentais específicos ficam indisponíveis nessa modalidade. Falhas do serviço local apresentam erro e opção de tentar novamente. Pedidos antigos são cancelados ao trocar de consulta ou sair da busca.

Palavras, filtros, ordenação e página ficam no hash da URL, compatível com GitHub Pages e histórico do navegador. Links dos resultados acrescentam o endereço de retorno à consulta e o contexto da coleção, sem mudar as rotas existentes. Não há salto automático ao parágrafo encontrado; a marcação de leitura continua independente. O usuário testou e aprovou a busca e autorizou seu commit. Nenhum teste foi executado pelo assistente nesta entrega, conforme solicitado.

## D10. Área editorial local e fila existente

Após o commit e push `edbab93`, foi implementada a primeira parte editorial em `/editorial`. A fila vem de `docs/revisao-markdown/pendencias.csv`, sem reclassificar automaticamente o acervo nem executar novamente a conversão. Prioridade, motivo, status e notas são editáveis e preservados em futuras gerações do CSV. Os relatórios antigos continuam sendo o registro da triagem original. Documentos sem pendências são acessíveis pela consulta do catálogo.

O formulário edita títulos PT/RU, categoria, tipo documental, autoria textual, referência arquivística, data histórica, rótulos e associações às coleções existentes. Não altera IDs, URLs, corpos, arquivos de idiomas nem os dados de coleta. Datas WordPress continuam separadas das históricas. Associações novas entram no fim da coleção; relações mantidas conservam sua ordem relativa. Não há reordenação manual nesta etapa.

## D11. Prévia, gravação e recuperação

Cada proposta é validada sem escrita e recebe um identificador temporário com validade de 15 minutos. A gravação aceita somente uma prévia existente, vinculada à revisão dos arquivos. Mudanças entre abas ou externas exigem reabrir a edição. Requisições são serializadas; `fcntl.flock` impede dois processos de backend no mesmo acervo no ambiente Linux. O servidor aguarda gravações em curso ao encerrar normalmente.

Metadados são escritos no catálogo versionado e projetados para o manifesto. O novo índice é preparado separadamente, antes da publicação, com a revisão dos arquivos propostos. O histórico comprimido registra antes/depois dos arquivos alterados; não copia os corpos dos documentos. Um marcador de transação permite reverter uma publicação interrompida no início seguinte e reconstruir o SQLite. Edições externas incompatíveis durante uma interrupção suspendem a recuperação automática para preservar o trabalho existente.

O histórico fica em `.local/editorial/history/`, fora do Git, com até 100 operações recentes exibidas por consulta. Restaurar exige nova prévia e gera outro registro. Como os snapshots são de arquivos completos, mudanças posteriores nos mesmos arquivos precisam ser desfeitas antes de restaurar uma alteração antiga. É uma escolha reversível para esta etapa de uso individual, documentada na interface e no manual; não oferece mesclagem de históricos independentes. O histórico precisa de cópia separada para sobreviver à exclusão de `.local/editorial/`.

## D12. Limite local de escrita e avaliação

As APIs de consulta continuam disponíveis. Os únicos endpoints de escrita são `/api/editorial/preview` e `/api/editorial/save`, por POST JSON, com token da sessão, origem correspondente ao backend, Host local, cliente em loopback e servidor vinculado a loopback. A rota `/editorial` funciona com o backend local, sem perfis ou login; a publicação no GitHub Pages continua estática. O backend continua usando a biblioteca padrão do Python.

Não foram executados testes, compilação ou servidor de teste pelo assistente para esta implementação, conforme solicitado. As validações de prévia e gravação são comportamento operacional do backend, não verificações executadas pelo assistente. O usuário realizou as verificações manuais de edição, gravação e restauração, confirmou o funcionamento da área editorial e autorizou o commit. Ajustes de layout e UI/UX foram adiados.
