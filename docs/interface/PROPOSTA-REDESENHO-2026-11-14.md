# Proposta de redesenho integral — Biblioteca e Mesa

14/11/2026. Proposta conceitual solicitada pelo responsável, baseada na estrutura atual do portal e do Estúdio. Piloto separado implementado após aprovação; não adotado como interface oficial. A adoção de 27/10 permanece vigente até nova aprovação. A proposta original não alterou o acervo. A implementação posterior acrescenta somente `/prototipo/mesa/`, preservando as entradas oficiais. Roteiro: [Piloto Biblioteca + Mesa](PILOTO-BIBLIOTECA-MESA.md).

## Problema a resolver

A interface acumulou vocabulários e navegações de etapas distintas: portal, leitura, estudo, bancada, editoria, oficina e Estúdio. Fontes, acervo, coleções, edição e projetos aparecem como entradas equivalentes, embora representem materiais, classificações, tarefas e contextos diferentes. Cabeçalho, atividades, explorador, identidade, ações, abas e comandos da ferramenta disputam o mesmo espaço.

A nova arquitetura deve responder sempre: que material está aberto, qual tarefa está ativa, onde a gravação terá efeito e como voltar ao trabalho anterior. O usuário não deve conhecer a história dos módulos para percorrer a aplicação.

## Conceito

Organizar o produto em dois percursos da mesma aplicação:

- **Biblioteca:** descobrir, localizar e consultar o acervo. Home, coleções/subcoleções, busca e apresentação documental.
- **Mesa:** estudar e trabalhar com materiais abertos. Comparação, notas, edição, tradução, fontes, OCR e tarefas de organização, conforme as capacidades disponíveis.

Um documento ou PDF é um material. Ler, comparar, editar e revisar são atividades sobre materiais. Coleções são organização intelectual; projetos são contexto de pesquisa e de versões privadas. Esses quatro conceitos deixam de competir como se fossem departamentos equivalentes.

A Mesa também funciona na publicação estática, com leitura/estudo/notas/exportação. O backend local acrescenta gravação editorial, projetos privados e processamento. As capacidades são explícitas; não há login ou backend público novo como requisito.

## Biblioteca

Home com busca central, percursos temáticos, novidades reais, coleções em destaque e apresentação da política editorial. Números do catálogo acompanham a descoberta, sem transformar a entrada em painel administrativo.

Coleção como catálogo contextual: apresentação curta, subcoleções, lista com título/data/idiomas e filtros progressivos. Um único conjunto de filtros, com retorno preservado ao documento. Novo documento/coleção e importação aparecem entre ações locais de organização, sem serem exigidos para consultar.

Abrir um documento entrega imediatamente o texto. Metadados completos, índice e fac-símile são consultas acionáveis, sem ocupar permanentemente ambos os lados. Idioma, posição e caminho de retorno pertencem ao documento.

## Mesa

Ao acrescentar comparação, outro material ou uma tarefa editorial, a superfície de leitura se amplia para a Mesa, conservando o contexto. Rotas antigas encaminham ao novo estado equivalente. O contexto é material + atividade + escopo + posição; não somente uma página genérica de ferramenta.

**Abas representam materiais por padrão.** O documento mantém leitura, estudo e editor como apresentações da mesma aba. Acrescentar um segundo documento ou PDF abre outro material. Metadados, menu, diálogo de exportação e prévia de salvamento não geram uma nova aba a cada clique.

Índice, ficha, notas, comparação e visualizador podem ser destacados e fixados em painéis quando isso servir à pesquisa. Essa composição avançada é opcional; o padrão inicial privilegia uma superfície ampla.

Projetos usam seletor de contexto: `Acervo local` ou `Projeto: nome`. A versão privada e o destino da gravação são indicados por texto, não apenas por cor. Não selecionar automaticamente um projeto na entrada. A promoção para o acervo continua exigindo confirmação explícita.

## Espaço e controles

- Uma faixa principal compacta, com navegação, identidade do material, escopo e ações da tarefa.
- Faixa de abas somente quando houver vários materiais abertos.
- Sem explorador ou inspetor obrigatórios. A lista de materiais abre por botão e pode ser fixada deliberadamente.
- No máximo um painel auxiliar aberto pelo fluxo comum; abrir outro substitui seu conteúdo. Fixação e divisão avançadas permanecem disponíveis.
- Menus e painéis auxiliares sobrepõem a superfície quando transitórios. Uma ficha extensa ou configuração complexa recebe área central ampla, em vez de estreitar duas vezes o documento.
- Índice e ferramentas secundárias podem ser recolhidos por Escape; foco retorna ao material. Ações essenciais também têm nomes visíveis, não dependem só de ícones/atalhos.
- Duas colunas principais para comparação. Terceira coluna é escolha explícita, com tamanho mínimo adequado.
- Meta do protótipo: faixa permanente de aproximadamente 48–56px; com abas, cerca de 80–88px. São metas de projeto a validar, não dimensões já medidas da interface atual.
- O espaço ganho beneficia texto e ferramenta. A leitura simples conserva largura confortável de linha; não esticar prosa por toda a tela.

## Localização das funções

| Função | Lugar proposto |
|---|---|
| Buscar e navegar coleções | Biblioteca; busca rápida disponível na Mesa |
| Abrir materiais / retomar sessão | Lista de materiais da Mesa |
| Original, tradução e idioma | Controle junto da identidade do documento |
| Parágrafos, paralelo, expansão de idioma | Apresentações do documento na mesma aba |
| Índice / marcador / notas | Acesso junto ao texto; painel acionável ou destacável |
| Markdown / correção por trecho | Atividade Editar no documento, mantendo posição e escopo |
| Importar tradução | Ação do documento; prévia/diferenças na superfície de trabalho |
| Metadados | Ficha consultável; edição por propriedades com revisão conjunta |
| Novo material | Um comando Adicionar, com arquivo, documento ou tradução contextual |
| Catálogo e coleções | Atividades centrais de organização; listas e propriedades, sem várias barras de navegação |
| Dividir/extrair PDF | Preparar fonte; resultado como derivado com receita |
| OCR e revisão | Atividade Transcrever na fonte selecionada |
| BookReader / PDF.js | Apresentações da fonte; comandos próprios e tela inteira real |
| Conferência de fac-símile | Documento e fonte em duas colunas, com vínculo/abrangência explícitos |
| Fila e processamento | Lista de tarefas com filtro por projeto/material; execução em segundo plano e retorno ao contexto |
| Histórico | Ação do material ou da tarefa, com prévia de restauração |
| Exportação | Ação do material/coleção; configurações adicionais sob demanda |

A paleta de comandos acelera percursos e busca ações. Ela não substitui a localização visível das funções essenciais.

## Percursos exemplares

### Ler, estudar, corrigir

Biblioteca → coleção ou busca → documento → comparar com original na própria aba → selecionar trecho → editar tradução → revisar diferenças → salvar no destino indicado → voltar ao mesmo trecho e à comparação.

A confirmação usa a área principal temporariamente, com antes/depois e efeito da gravação explícitos. Não fica ao final de uma página extensa. Cancelar conserva o rascunho e retorna ao contexto anterior.

### PDF para transcrição

Adicionar PDF → fonte aberta → diagnóstico nativo/OCR → escolher páginas/idiomas → iniciar processamento → revisar imagem e transcrição em duas áreas amplas → salvar a página → próxima página.

Miniaturas e parâmetros são auxiliares recolhíveis. Página, progresso e gravação permanecem acessíveis. A receita avançada de OCR/imagem tem espaço próprio quando aberta; não ocupa permanentemente a coluna de revisão. BookReader é uma vista de consulta da fonte e não herda uma barra de OCR fora de contexto.

### Conferir um vínculo

Fila → caso → transcrição e PDF candidato → navegar às páginas indicadas → registrar correspondência, abrangência, variante ou rejeição → prévia → confirmação local → próximo caso. A evidência e o histórico são preservados.

### Organizar ou importar

Mesa → Organizar acervo → catálogo/coleção ou Adicionar → escolher conjunto e arquivos → associar metadados por grupo → conferir exceções e resultado → prévia conjunta → salvar. Itens mais longos usam tela própria; não uma sucessão de formulários comprimidos em barras laterais.

## Linguagem visual

Carmim como cor de identidade e ações selecionadas; superfícies claras, bordas discretas, espaçamento de leitura e tipografia editorial. Tipografia de interface para controles e propriedades; serifada para leitura longa; monoespaçada para Markdown quando útil. Contraste, foco de teclado, toque e rótulos textuais fazem parte do desenho.

Aplicar estilo consistente às próprias ferramentas: um layout externo novo não resolve uma tarefa interna que continua organizada como formulário vertical interminável. Catálogo pode combinar tabela/lista e ficha; OCR usa superfície de revisão; comparação usa duas versões; importação usa associação por conjunto e quadro de exceções.

## Preservação e migração

Preparar uma matriz de capacidades antes de substituir percursos: leitura, índice, marca/retomada, idiomas, parágrafos/paralelo, expansão, múltiplos documentos, fichas/notas destacáveis, Markdown, correções, importação, catálogo, coleções, projetos, versões privadas, PDF/derivados/OCR/teclado, unidades/caixas, fac-símiles, histórico, prévias, exportações e publicação selecionada.

URLs, acervo, contratos de API, revisões e históricos são preservados. A camada de apresentação deve evoluir por fluxos completos. Não trocar frontend, modelo de dados e backend simultaneamente por obrigação do redesenho.

## Próxima entrega proposta

1. Protótipo navegável separado, com quatro cenas: Biblioteca; documento/Mesa; revisão PDF/OCR; catálogo/importação. Usar materiais representativos, sem gravação real inicialmente.
2. Validar caminhos, espaço útil, retorno ao trecho, cancelamento, comparação, teclado/celular e distinção de destino público/privado.
3. Portar um fluxo completo e comparar com a matriz de capacidades. A interface atual continua recuperável.
4. Expandir por tarefas até haver paridade comprovada; só então propor adoção oficial.

A proposta precisa ser avaliada quanto à navegação e ao trabalho real antes de escolher uma nova arquitetura de componentes ou outra biblioteca. A implementação atual contém recursos e regras que devem ser reaproveitados; sua disposição não limita o desenho novo.
