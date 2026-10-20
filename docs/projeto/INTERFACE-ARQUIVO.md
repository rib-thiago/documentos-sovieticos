# Interface — biblioteca digital e arquivo de pesquisa

Registro histórico das propostas anteriores. A interface oficial aprovada em 19 de outubro de 2026 é [Carmim — portal, leitor e bancada](PORTAL-BANCADA-CARMIM.md), identificada por `carmim-1`.

## Direção

A proposta `archive-2` combina a presença visual de biblioteca digital com a organização de arquivo de pesquisa, conforme a preferência do responsável. Usa os recursos nativos existentes: HTML, CSS e JavaScript, sem npm, framework ou etapa de compilação.

A identidade combina superfícies claras, tinta cinza-esverdeada e acentos em vinho. Inter identifica ferramentas e metadados; Source Serif 4 identifica títulos e textos. São as mesmas famílias já usadas pelo site; a área editorial passa a carregá-las também. Há fontes locais de sistema como alternativa caso o Google Fonts não esteja disponível.

## Mudanças

- Página inicial com abertura editorial, busca em primeiro plano e números calculados a partir do catálogo carregado. A estatística de documentos usa IDs únicos; não soma repetições entre coleções.
- Cartões com capas em área própria, sem recorte, títulos sobre fundo claro e uma chamada discreta para explorar cada coleção. Coleções sem capa usam uma composição tipográfica neutra.
- Cabeçalho de coleção com título legível e capa lateral no desktop; no celular, o título recebe prioridade.
- Listas com tratamento de catálogo, mantendo data junto ao título, idiomas, paginação e informações existentes.
- Leitor com hierarquia tipográfica mais definida; painel e menus preservam seus estados e comportamentos.
- Área editorial com o mesmo tema, botões uniformes, navegação lateral mais clara, formulários e prévias com superfícies consistentes. Recolhimento da lateral preservado.
- Link de salto para o conteúdo operável por teclado sem substituir a rota do documento, que usa hash.

`assets/css/tokens.css` concentra as variáveis compartilhadas. Os estilos ficam nos arquivos de seus componentes; não há um segundo tema carregado sobre o antigo. As entradas HTML e os imports usam a versão `archive-2` para evitar mistura de cache. `assets/interface.js` trata apenas o salto acessível para o conteúdo.

Nenhum documento, tradução, metadado, URL, histórico ou mecanismo de gravação foi modificado nesta entrega. Não há publicação automática. Não foram executados testes, servidor ou navegação automatizada; a avaliação visual e funcional é manual, ainda pendente. Sem commit ou push.

## Como avaliar

1. Inicie o backend com `python3 -m backend` e abra `http://localhost:8000/`. Recarregue com Ctrl+Shift+R se necessário.
2. Na página inicial, observe as capas completas, títulos, alinhamento dos cartões e busca. Confira uma coleção com capa e uma sem capa. Faça o mesmo no celular ou estreitando a janela.
3. Abra uma coleção e uma subcoleção com muitos documentos. Confira datas junto aos títulos, paginação, idiomas e abertura dos textos.
4. Abra um texto longo: alterne leitura/estudo/paralelo, mude o idioma, expanda e recolha o painel, fixe-o, abra o índice, marque e retome um parágrafo. Confira também exportação Markdown.
5. Pelos controles locais do documento, abra a área editorial. Confira fila, catálogo, metadados, importação de tradução, editor Markdown e prévias; recolha e reabra a lateral. Não é necessário salvar alterações só para avaliar o visual.
6. Use Tab desde o início da página: o primeiro link deve permitir saltar para o conteúdo sem sair da rota atual. Confira campos, botões e menus com o teclado.

O site estático também pode ser visto com `python3 -m http.server 8000`, mas as ferramentas editoriais continuam exigindo o backend local. A mudança visual não altera essa distinção.

## Próxima avaliação

Após o uso real, ajustar densidade das listas, proporção das capas e equilíbrio entre o painel e a leitura. Esta entrega estabelece uma linguagem visual comum; não declara aprovação visual antes da avaliação do responsável.

## Revisão de organização — workspace-3

A primeira proposta foi considerada conservadora pelo responsável: alterava sobretudo a aparência e não reorganizava suficientemente a experiência. Esta revisão modifica as ferramentas e a organização dos fluxos:

- Biblioteca com filtro imediato de coleções e alternância Capas/Lista, mantida na sessão. O filtro procura títulos portugueses/russos e subtítulos, sem substituir a busca de documentos.
- Painel do documento dividido em Leitura e idiomas, Índice e posição e Edição e arquivos. As abas abrem uma tarefa por vez; o painel começa recolhido. Editar e Baixar permanecem acessíveis no cabeçalho. A retomada continua visível quando houver parágrafo marcado.
- Seleção de leitura/estudo e de organização do estudo em controles segmentados. O índice fica direto na aba correspondente, sem uma segunda expansão.
- Ações editoriais distintas para Markdown, tradução e metadados, com o documento, idioma e retorno à leitura preservados. O atalho Editar leva à ficha editorial; o editor Markdown também pode ser aberto diretamente pela aba.
- Navegação lateral editorial agrupada em Revisão, Acervo e Textos e traduções, com ícones locais e identificação da área de trabalho. A lateral continua retrátil.
- Vinho identifica edição e seleção; verde identifica conexão/trabalho local e download. Não há bibliotecas externas de ícones.

### Acesso local e conexão encerrada

O leitor antes consultava `/api/editorial/session` com cancelamento em três segundos e ocultava os atalhos caso a resposta demorasse. A sessão calcula a revisão do catálogo, e todos os GET, inclusive envio de imagens, compartilhavam o bloqueio editorial. O log apresentado mostra uma resposta após o cliente encerrar a conexão: o BrokenPipeError era interpretado como erro de arquivo e provocava uma tentativa incorreta de enviar um segundo 404.

A consulta de capacidades usa agora `/api/editorial/capabilities`, leve e independente de revisão e do bloqueio do catálogo. Sessões autenticadas e gravações continuam com as proteções existentes. Os recursos estáticos publicados não ocupam mais esse bloqueio durante seu envio; as gravações continuam atômicas. A escrita de respostas tem timeout e trata desconexão/cancelamento sem uma segunda resposta.

No endereço local, falhas de conexão passam a exibir Conectar edição/Reconectar edição local. Não se presume disponibilidade editorial no GitHub Pages. O menu superior oferece Área editorial quando a detecção confirma o backend. Os controles de correção de trechos continuam vinculados à capacidade `study_passage_edit`.

### Conferência desta revisão

1. Encerre o backend anterior com Ctrl+C e execute novamente `python3 -m backend`. Isso é necessário para carregar o novo endpoint e o tratamento de conexão.
2. Abra o site e recarregue com Ctrl+Shift+R. Experimente o filtro de coleções e Capas/Lista.
3. Abra `http://localhost:8000/#/doc/showtrials-1665`. O cabeçalho do painel deve apresentar Editar e Baixar assim que a conexão local for detectada. Se não conectar, abra a aba Edição e arquivos e use Reconectar edição local.
4. Use Editar para abrir a ficha; em Edição e arquivos, confira os caminhos específicos de Markdown, importação de tradução e metadados. Volte à leitura pelo atalho editorial. Nada é salvo apenas por abrir esses caminhos.
5. Compare os modos de leitura e estudo; abra Índice e posição e confirme a navegação direta e a retomada. No estudo, confira Corrigir tradução no parágrafo.
6. Na editoria, confira os três grupos laterais, o contexto superior e o recolhimento da lateral. Avalie também no celular.

Sem testes executados, servidor iniciado pelo agente, commit ou push. O diagnóstico foi feito pelo log fornecido e pela inspeção do código; a validação em execução cabe à conferência manual.
