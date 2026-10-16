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
