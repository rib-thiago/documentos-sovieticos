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

## D13. Importação explícita de traduções

A rota editorial `#/importar` e os atalhos do catálogo/formulário permitem escolher um documento cadastrado, selecionar PT ou EN e carregar Markdown UTF-8 até 4 MiB. A referência é RU quando disponível ou a primeira edição quando não há RU; seu idioma fica protegido. Nenhum nome recebido vira caminho de gravação: traduções existentes mantêm seu caminho Markdown, e novas versões recebem nome definido pelo documento e idioma. Destinos de outra edição e arquivos não cadastrados são recusados.

O novo endpoint `/api/editorial/translations/preview` usa a mesma sessão local, origem, bloqueio e confirmação de gravação existentes. A prévia reconhece nome, ID, idioma e fonte do cabeçalho de exportação; inconsistências exigem confirmação explícita. Ausência de identificação é informada, sem dedução semântica do idioma ou da equivalência do texto. O conteúdo recebido é preservado, inclusive cabeçalhos; o título do catálogo só muda se preenchido explicitamente no formulário. O manifesto passa a representar `title_en` quando houver título inglês cadastrado.

## D14. Diagnóstico estrutural e visualização

São apresentados blocos do segmentador do estudo e estimativas de parágrafos, títulos, listas, tabelas e código para original, versão atual e arquivo enviado. Igualdade de contagens não certifica correspondência. Divergência não força cortes nem bloqueia uma tradução válida. A proposta não cria alinhamento e não reescreve o Markdown. A prévia renderizada usa as bibliotecas locais markdown-it, footnotes e DOMPurify; HTML cru não é interpretado. A comparação linha a linha é limitada para arquivos extensos, com indicação visível e acesso ao texto completo.

## D15. Histórico do conteúdo traduzido e publicação local

O histórico comprimido passa a conter também o arquivo traduzido, além do cadastro e manifesto, e representa a ausência anterior por `null`. Restaurar uma substituição recupera os bytes UTF-8 anteriores; restaurar uma inclusão remove somente o arquivo criado por essa operação e a edição cadastrada. A restauração cria outro registro e pode ser desfeita. Os históricos anteriores de metadados continuam legíveis. O marcador de recuperação abrange todos esses arquivos, com conferência contra alterações externas antes de reverter.

A validação e a preparação do SQLite aceitam conteúdo proposto em memória, com caminhos verificados e hashes correspondentes, sem exigir gravar o upload no acervo antes da confirmação. O índice é preparado antes da publicação. A revisão dos arquivos e o destino são conferidos novamente antes de escrever. A gravação atualiza arquivo traduzido, catálogo, manifesto e índice; não faz commit, push ou publicação remota. O histórico continua local em `.local/editorial/`, fora do Git.

A implementação da importação não executou testes, compilação, servidor de teste, importação real nem alteração dos corpos existentes. O roteiro manual está em `IMPORTACAO-TRADUCOES.md`; esta etapa permanece sem commit e sem push, conforme solicitado.

## D16. Cabeçalho de exportação separado do corpo

Após o teste manual, o usuário apontou divergências artificiais de blocos entre o russo sem envelope e traduções que carregavam o cabeçalho exportado, além da duplicação desse cabeçalho ao reexportar. A correção reconhece conservadoramente os envelopes iniciais do exportador e os separa do corpo na leitura, estudo, prévia, contagens, diferenças da importação e indexação do texto. Metadados continuam no cabeçalho comum do leitor; não são inseridos como parágrafos de um idioma.

Na exportação ShowTrials, todos os envelopes iniciais reconhecidos são substituídos por um único cabeçalho gerado com os metadados atuais. A identificação do upload continua lendo o arquivo recebido, e o histórico preserva seus bytes. Títulos próprios do corpo não são descartados. A regra exige título, idioma, fonte ou ID e separador; cabeçalhos incompletos ou arbitrários não são apagados por aproximação. Não houve migração nem alteração em massa dos arquivos locais. O índice derivado passa à versão 2 para ignorar os envelopes nos trechos pesquisáveis após reinicialização. A correção não executou testes, commit ou push.

## D17. Leitor integrado ao painel e contexto de retorno

Após os commits aprovados `7b569a2` (importação) e `eb9da8a` (cabeçalhos), sem push, o leitor ganhou atalhos locais para o cadastro, a importação e a versão Markdown escolhida. A detecção consulta a sessão editorial e suas capacidades; em servidor estático, backend antigo sem a capacidade ou acesso sem permissão local, os controles ficam ocultos. A seleção do idioma de edição é explícita e independente da leitura.

O contexto de retorno conserva a URL do documento (coleção/subcoleção e retorno à busca) e guarda idioma, modo, colunas e posição na sessão da aba. O link aceita somente endereço interno do leitor. A posição é restaurada por assinatura do trecho quando possível, com fallback para rolagem, sem modificar o marcador manual. O parâmetro transitório é consumido ao voltar. Ao salvar, uma notificação por localStorage informa outras abas; catálogo e cache de conteúdo são recarregados, com controle de versões de rota para evitar renderizações antigas. O retorno por cache de navegação também recarrega os dados.

## D18. Edição explícita de versões Markdown

O editor carrega uma edição existente pelo ID estável, mostra o arquivo completo e renderiza o corpo sem o envelope de exportação. Oferece prévia ao digitar para textos menores, atualização sob demanda para textos extensos e comparação antes da confirmação. A edição não altera automaticamente metadados a partir de títulos no corpo. Arquivos TXT não são convertidos nessa operação; caminhos compartilhados entre edições e links simbólicos são recusados.

É possível editar explicitamente RU, necessário para revisões do original, guardando seu conteúdo anterior no mesmo histórico recuperável. A importação continua recusando substituir o idioma original. O campo interno legado `translation_files` passa a abranger também o Markdown original quando editado explicitamente; a revisão da edição é vinculada ao hash aberto e à revisão do catálogo. A gravação altera somente o conteúdo escolhido e seu hash/tamanho, projeta o manifesto e prepara a busca antes da publicação local, sem mudar IDs ou caminhos. Restaurar usa o mesmo mecanismo de snapshots e conflitos já existente.

Os endpoints acrescentados são `GET /api/editorial/editions/ID:IDIOMA` e `POST /api/editorial/markdown/preview`; a confirmação continua em `/api/editorial/save`. Mantêm o limite de 4 MiB para a proposta, loopback, origem e token de sessão. Não foi implementada publicação automática. A nova implementação não executou testes, compilação, servidor de teste ou edição real de conteúdo; permanece sem commit e sem push para avaliação manual conforme `LEITOR-EDITORIAL.md`.

## D19. Interface e sequência do acervo

O usuário pediu antecipar a melhoria visual para facilitar a avaliação da integração. A área editorial ganhou estrutura com navegação lateral/abas móveis, seção ativa, hierarquia de ações, campos, cartões e prévias consistentes. No leitor, os controles locais ficam num menu recolhido. Não foram removidos os passos de revisão, confirmação ou histórico.

Listas de documentos usam 25 itens por página e `pagina` no hash. Links do leitor conservam coleção e subcoleção; anterior/próximo percorrem a ordem cadastrada nesse contexto, sem circular nem atravessar seus limites. O retorno à lista calcula a página do documento atual. Datas e identificação tornam visíveis diferenças entre títulos repetidos; o idioma corrente é preservado no próximo documento quando disponível.

## D20. Data coletada como campo de apresentação

A projeção do manifesto inclui `collected_date` a partir de `source_metadata.wordpress_date`, permitindo uso estático. A apresentação prioriza a data histórica já cadastrada e usa a coletada como fallback explicitamente identificado. A formatação preserva o dia escrito na fonte, sem conversão de fuso. Não se usa `wordpress_modified` nem se preenche automaticamente `historical_date`.

O manifesto é derivado: na restauração, conflitos são conferidos nos snapshots canônicos e nos conteúdos modificados; a projeção é regenerada com o modelo atual. Isso mantém utilizáveis os históricos anteriores à inclusão desse campo e preserva os controles contra sobrescrita de alterações nos dados canônicos. Não houve teste executado, commit ou push nesta etapa; roteiro em `UX-CATALOGO.md`.


### D21 — Datas da fonte e controles do leitor

O campo wordpress_date não comprova a data histórica: permanece separado, explicitamente não verificado, ao lado do título e no envelope de exportação. Não houve preenchimento automático de historical_date nem alteração dos textos existentes. Seletores do leitor seguem menus da edição, navegação sequencial fica no fim do documento e fixação da barra durante a rolagem é opcional, por sessão.


### D22 — Datas confirmadas e painel inicialmente recolhido

O responsável confirmou as datas ShowTrials; removemos avisos e ressalvas da interface e exportação. A expansão do painel deixa de persistir: cada montagem começa recolhida. A mudança de visualização preserva o parágrafo visível sem alterar a marcação manual. Controles do painel recebem dimensões e estilos comuns, em grupos compactos.


### D23 — Trocas de modo locais e menus como listas

Trocas de modo preservam o painel e atualizam o corpo do texto; parágrafo/paralelo reaproveitam os blocos existentes. A expansão escolhida permanece durante essas trocas; abrir outro documento começa recolhido. Um atalho de retomada no cabeçalho indica a marca mesmo com o painel fechado. Opções internas usam listas de ações com seleção discreta, mantendo semântica acessível. Nenhum teste executado nesta rodada; mudanças aguardam avaliação manual.


### D24 — Entrada editorial única e idioma contextual

No leitor, Editar oferece idioma e uma ação única que abre o cadastro editorial do documento. Exportação e edição usam inicialmente o idioma de leitura ou a coluna esquerda no estudo paralelo. O editor Markdown passa a ser acessado pela barra lateral editorial, mantendo documento, idioma e retorno ao leitor. Sem documento selecionado, oferece seleção por ID ou catálogo; versões sem Markdown não são convertidas implicitamente. Links de ação no cadastro recebem o mesmo estilo de botão; títulos do catálogo e links no corpo das prévias permanecem links de texto. Sem testes executados, commit ou push.


### Correção de carregamento do contexto editorial

O parâmetro document de setDocumentContext ocultava o objeto DOM global, causando document.querySelector is not a function ao abrir os metadados ou o editor Markdown. Renomeado para catalogDocument, preservando o formato do contexto. Atualizada a versão do script para invalidar cache. Correção por inspeção de código, sem executar testes, commit ou push.


### D25 — Correções locais por intervalo do Markdown no estudo

A renderização mantém intervalos exatos do arquivo em cada bloco de estudo. A correção usa o intervalo da própria tradução, sem deduzir correspondências com o russo e sem substituição global de texto. Seleção parcial é usada apenas quando aparece uma única vez no bloco bruto; nos outros casos, a interface informa e carrega o bloco inteiro. Divergência entre arquivo e tela recusa a correção e exige recarregar.

O backend recebe intervalo Unicode, conteúdo esperado, revisão e hash, protege o original e aceita apenas traduções PT/EN Markdown. Reaproveita a gravação transacional e o histórico da edição completa. A confirmação atualiza catálogo, manifesto, busca e leitor; apenas o intervalo é substituído no texto. Cabeçalhos e demais versões permanecem preservados. Nenhum teste executado, commit ou push nesta entrega; avaliação manual pendente.

A correção por trecho foi testada manualmente e aprovada pelo usuário, que autorizou o commit desta entrega. Sem testes executados pelo assistente e sem push.


### D26 — Entrada individual de documentos e organização local

Novos originais são cadastrados por arquivo UTF-8 Markdown/TXT, com idioma explícito RU/PT/EN, ID estável, metadados e associações. Arquivos novos ficam em originais/locais/; não há renomeação ou substituição de documentos existentes. A criação inclui a projeção global, o manifesto, a busca e uma pendência média na fila. A prévia mostra destino e conteúdo, confere identificação e aponta coincidências por título, URL ou hash; avisos exigem confirmação explícita.

Coleções e subcoleções são criadas/editadas por formulário, na hierarquia existente de dois níveis. IDs/pai de coleções existentes são fixos para preservar URLs. As capas são opcionais e referenciam imagens existentes em assets/covers/; upload de imagens e importação em lote ficam registrados como pendências. Novas associações à subcoleção incluem o pai automaticamente, sem reordenar os itens anteriores.

### D27 — Histórico de cadastros e estabilização por inspeção

O histórico transacional passa a abranger coleções, proveniência e arquivos TXT criados no cadastro, mantendo compatibilidade com os snapshots anteriores. Operações identificam se afetam um documento ou uma coleção, e podem ser filtradas pelo ID de ambos. Desfazer a criação remove o arquivo criado do acervo ativo, preservando seu conteúdo no histórico. Restaurar continua recusando conflitos com alterações posteriores.

Foram corrigidos por inspeção títulos somente em inglês, atualização da lista editorial de coleções, apresentação de coleções sem subcoleções, projeção da primeira subcoleção em pais legados e Escape de janelas modais. Não houve regravação do acervo para demonstrar os recursos. O roteiro de avaliação está em CADASTRO-LOCAL.md; a revisão e as pendências estão em ESTABILIZACAO.md. Nenhum teste executado, commit ou push. A entrega aguarda avaliação manual do usuário.


### D28 — Lotes de originais com CSV e confirmação conjunta

A entrada em lote reutiliza a validação do cadastro individual sem gravar propostas intermediárias. O arquivo e o documento são associados explicitamente por CSV; cada arquivo/ID deve aparecer uma vez. Coleções informadas na linha prevalecem sobre a seleção padrão. Se houver um erro, o lote inteiro fica bloqueado. Coincidências de título, URL/hash e divergências reconhecidas exigem confirmação explícita, incluindo coincidências dentro do lote.

O lote é publicado em uma transação local, com uma atualização do índice e um snapshot recuperável. O histórico identifica todos os IDs envolvidos e pode ser filtrado por qualquer um, mas a restauração é conjunta. Limites operacionais: 100 originais, 4 MiB por arquivo, 20 MiB de textos e 1 MiB de CSV. A prévia renderiza cada conteúdo sob demanda. Importação de traduções em lote, ZIPs, coleções automáticas e imagens continuam fora desta etapa. Sem execução de testes, commit ou push; avaliação manual pendente.


### D29 — Consolidação visual para uma semana de uso prático

As entradas assets/style.css e assets/editorial.css foram preservadas, passando a importar módulos CSS locais por componente em assets/css/. Não há etapa de build ou dependência de npm. Foram consolidados os valores de apresentação já aprovados e removidas as regras das versões antigas do painel, índice na navbar, menus flutuantes e navegação sequencial no início. Visibilidade, estados ativos e breakpoints pertencem ao componente correspondente; fontes são variáveis de tema. A versão estática de cache desta rodada é stable-week-1.

O painel usa um único controlador de abertura e um observador de tamanho, liberado ao trocar de documento/sair do leitor. Navbar e painel fixado fornecem o mesmo deslocamento ao CSS e à navegação/retomada. A animação de padding dos blocos foi retirada para evitar movimento de texto durante alterações de disposição. Menus atrás de janelas modais não recebem cliques/Escape dessas janelas. Nenhuma API, texto, tradução, ID ou URL de documento foi alterada.

A documentação de manutenção fica em assets/css/README.md; o roteiro da semana e o formato de relato de problemas ficam em SEMANA-ESTAVEL.md. Não houve execução de testes, navegador, compilação, commit ou push pelo assistente. A avaliação visual e prática será feita pelo usuário durante a semana solicitada.
