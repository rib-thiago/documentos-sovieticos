# Oficina integrada — estudo, pesquisa e editoria

> Evolução: o núcleo editorial agora é montado diretamente na bancada; `/editorial` abre esse ambiente. Consulte [Bancada editorial nativa](BANCADA-EDITORIAL-NATIVA.md). As referências a hosts editoriais abaixo descrevem a etapa anterior.

25/10/2026. Implementação para validação manual no mesmo laboratório aprovado pelo responsável. A interface pública continua na home; nada foi publicado automaticamente. A revisão documental continua adiada.

## Acesso

Encerre o backend anterior com Ctrl+C e execute novamente:

```bash
python3 -m backend
```

Abra **http://127.0.0.1:8000/prototipo/oficina/** e use Ctrl+Shift+R. O backend recebeu a lista restrita dos novos módulos e do visualizador de páginas PDF. Não precisa de npm para usar.

## Decisão de integração

A bancada usa Dockview para grupos/abas e CodeMirror para os editores. Os fluxos existentes de estudo e editoria foram integrados por adaptadores na mesma origem, dentro das abas, com seus controles, APIs, prévias e históricos preservados. Isso permite transportar funções completas sem reimplementar regras críticas em um segundo editor. O adaptador compartilha o estilo, abre a navegação em abas do host, aplica CodeMirror aos campos de texto compatíveis e avisa o host depois de gravar.

Não é uma reescrita integral das ferramentas em componentes nativos do Dockview. Os componentes existentes continuam sendo responsáveis por segmentação, alinhamento, revisão e transações. A matriz abaixo identifica o mecanismo de cada acesso, para que uma mudança de apresentação não seja confundida com remoção de funções.

## Matriz de funções e acesso

| Frente | Funções integradas | Onde acessar | Mecanismo |
|---|---|---|---|
| Leitura | Markdown/texto, idioma, índice, marcador, retomada, fixar/recolher painel, anterior/próximo | Selecionar documento → Leitura | Leitor existente adaptado; mesmo registro de posição do estudo. |
| Estudo | Parágrafo, paralelo, escolha de colunas, expandir tradução, numeração e correção de bloco/seleção | Estudo ou Documento → organização de estudo | Componentes reais de estudo, incluindo seus diálogos e validação de versão. |
| Fontes no estudo | Gerenciar vínculos, fac-símile, transcrição, unidade/região e copiar referência | Documento → Fontes e fac-símiles | Fluxo de associações existente, sem inventar alinhamento entre idiomas. |
| Bancada | Abas independentes, grupos, arraste, divisores, ampliação, fechamento, mover por menu | Faixa de abas e Painel… | Dockview; componentes montados permanecem vivos ao alternar/mover. |
| Markdown | Edição, prévia, comparação, rascunho recuperável, teclado russo, download e encaminhamento à revisão | Markdown; Documento → Prévia/Comparar | CodeMirror e renderer existente; TXT permanece protegido de edição como Markdown. |
| Índice e ficha | Ficha em aba e índice que aponta para leitura da versão salva | Documento → Ficha e índice | Instrumento nativo; índice usa o corpo salvo, sem o envelope de exportação. |
| Notas | Notas por documento/projeto e por contexto; download | Lateral Notas | Sessão, com reaproveitamento das notas legadas por documento. |
| Exportação | Nome e cabeçalho normalizados do documento, todos os idiomas disponíveis | Documento → Baixar Markdown | Mesma função de exportação do leitor; download de rascunho fica separado. |
| Coleções | Consulta, subcoleções, paginação e ZIP | Seletor de coleção/subcoleção → Consultar coleção / baixar ZIP | Página real da coleção e ZIP existente numa aba. |
| Busca | Busca de títulos no explorador; pesquisa integral e filtros com backend | Fontes e ferramentas → Busca integral e filtros; Área editorial → Catálogo | Busca existente integrada à área de trabalho. |
| Catálogo | Metadados, associações e pendências | Área editorial → Catálogo; Documento → Metadados do acervo | Formulários e prévias existentes; cadastro canônico claramente identificado. |
| Cadastro | Novo documento, coleção/subcoleção e lote guiado | Área editorial → Acervo | Fluxos completos de criação, diagnóstico e confirmação. |
| Tradução | Importação canônica e diagnóstico de identificação/estrutura, diferenças e histórico | Documento → Adicionar tradução; Área editorial → Textos e traduções | Importador existente; no projeto, abre a versão privada para carregar arquivo. |
| Revisão/histórico | Fila, prioridades, motivos, restauração de documento/coleção/lote | Área editorial → Revisão; Documento → Histórico | APIs e históricos existentes, sem alterar seu formato. |
| PDF/OCR | Upload, extração nativa, OCR rus/eng/por, fila/progresso/retomada, revisão por página | Área editorial → Fontes e processamento | Ferramenta existente; edição textual passa pelo adaptador CodeMirror. |
| Manipulação PDF | Seleções/divisão, derivados e proveniência | Área editorial → Manipular PDF | Fluxo configurável existente, sem sobrescrever fonte. |
| Alinhamento | Dividir/unir unidades, caixas, conflitos e histórico por página | Revisão de página → Fronteiras/localização | Editor estrutural original; preservada a seleção nativa no campo de divisão. |
| Incorporação | Transcrição revisada para documento/versão/projeto; concluir vínculo pendente | Ferramenta da fonte PDF | Confirmação e histórico existentes. |
| Fac-símile público | Preparar/aplicar/retirar/restaurar projeção estática selecionada | Gerenciar fontes/páginas ou fonte PDF | Operação local existente; GitHub depende de commit/push separados. |
| Visualizador PDF | Página, zoom e camada textual selecionável | + PDF; fac-símiles reconhecidos em revisão/estudo | PDF.js; na revisão, a página é comandada pela ferramenta para não divergir da transcrição. |
| Projetos | Criar/editar/arquivar, vincular documentos/fontes | Área editorial → Projetos | Administração existente; seletor da bancada escolhe explicitamente o contexto. |
| Versão privada | Markdown/preview, importação de arquivo, histórico/restauração e promoção | Selecionar projeto → Markdown; Documento → Versões e incorporação | Rascunho nativo encaminhado com hash/revisão ao editor privado existente. |
| Incorporação de projeto | Comparar com o acervo e confirmar substituição | Versão privada → Incorporar versão salva ao acervo | Confirmação específica existente, mantida separada de salvar privado. |
| Impressão | Edição paginada do rascunho e impressão pelo navegador | Documento → Preparar edição PDF | Paged.js; paginação da edição distinguida da fonte. |
| Imagens e livros | Imagem ampliável e BookReader externo | Fontes e ferramentas | OpenSeadragon local e incorporação hospedada no Internet Archive. |

## Contexto e recuperação

- Recarregar a oficina começa no **acervo, sem projeto ativo**, e pode recuperar a composição canônica da sessão. O layout de um projeto só é restaurado depois de escolhê-lo explicitamente.
- Ao trocar de contexto, a composição anterior é guardada. Formulários com alterações pendentes precisam ser salvos ou descartados antes da troca; rascunhos nativos podem permanecer na sessão. Rascunhos nativos permanecem separados por projeto/documento/idioma.
- Os fluxos de catálogo e metadados continuam canônicos, inclusive quando abertos a partir de um projeto. Seu nome indica “acervo”. A associação de documentos/fontes ao projeto usa a administração do projeto.
- Salvar privado não altera catálogo/texto principal. Incorporar exige uma confirmação distinta. O rascunho encaminhado é recusado se a versão-base mudou.
- Depois de salvar, catálogo, projetos e modelos abertos são atualizados. Se houver um rascunho divergente, ele permanece intacto; Comparar mostra a nova versão salva à esquerda. Recarregar salvo guarda uma recuperação separada antes de descartar o rascunho atual.
- Formulários embutidos mantêm suas proteções antes de fechar e os conflitos do backend. Sua gravação confirmada é real; o laboratório não é uma simulação de gravação.
- Posição e marcador usam os recursos existentes do leitor/estudo. A prévia do rascunho não cria outro marcador concorrente. Marcadores antigos do primeiro piloto só são aproveitados quando há uma passagem longa exatamente igual e única.
- Notas e rascunhos da sessão não substituem backup nem histórico persistente. Os formulários mantêm as proteções existentes; não há promessa de recuperar todo campo não salvo depois de encerrar a sessão.

## Validação manual prioritária

### 1. Texto e estudo

Abra `showtrials-1665` ou outro documento com RU/PT/EN. Abra Leitura e Estudo; marque um parágrafo, mude para paralelo e depois retorne à leitura. Confira Retomar e a remoção ao clicar novamente. Teste índice, troca de idioma, expansão de tradução e correção por trecho. Para não gravar uma correção experimental, revise e cancele.

Abra Ficha e índice numa aba separada. Clique num título e confira a leitura na passagem correspondente. Abra dois documentos e verifique que a ficha, os idiomas e as ações seguem o painel ativo. Use os comandos de mover/reunir/ampliar sem arraste; feche e reabra abas.

### 2. Edição e gravação canônica

Edite um rascunho em Markdown. Confira Prévia e Comparar. Use Revisar e salvar: confira o editor editorial, a prévia e as diferenças. Cancele ou salve apenas uma alteração legítima. Se salvar, volte às abas abertas: a leitura deve atualizar e a comparação ficar reconciliada. Confirme que rascunhos diferentes não são sobrescritos. O histórico do documento precisa continuar acessível.

Use Documento → Baixar Markdown e compare o nome/cabeçalho com a exportação do leitor. O botão Baixar rascunho do editor baixa o texto em trabalho e é uma ação diferente.

### 3. Projeto privado e incorporação

Escolha explicitamente um projeto e um documento já vinculado. Edite uma pequena passagem em Markdown e encaminhe à revisão privada. Salve **somente no projeto**. Confira a versão no projeto e depois no acervo: a versão principal deve continuar intacta. Abra o histórico privado e a prévia de incorporação; cancele para testar sem alterar o acervo. A incorporação só deve acontecer se você marcar sua confirmação específica.

Teste uma versão PT/EN nova pelo menu Documento. Carregar um Markdown no editor privado continua disponível. Recarregue a oficina: ela deve iniciar sem projeto ativo; escolha o projeto para recuperar sua composição. Se quiser um piloto, use um projeto local com documento existente; não é preciso criar documentos públicos de teste.

### 4. Editorias e processamento

Abra, pela lateral Área editorial: fila, catálogo, coleções, novo documento, nova coleção/subcoleção, lote, importação e histórico. Confira os acessos e a apresentação comum; para testar formulários, use prévia e cancele, evitando criar registros de teste no acervo.

Abra uma fonte PDF existente. Na revisão, confira imagem/PDF e transcrição, mudança de página, zoom, seleção de texto, teclado russo e revisão estrutural. A página do fac-símile deve acompanhar o controle da ferramenta. Confira que campos de divisão de unidades ainda permitem posicionar o cursor. Execute OCR apenas quando desejar processar uma fonte real; visualizar o PDF não executa OCR.

### 5. Continuidade da bancada

Guarde uma nota no documento A, outra no B e outra no contexto. Alterne entre eles; confira que não se misturam. Reabra um rascunho da sessão e recarregue a página. A composição canônica e os rascunhos devem ser recuperados. Fechar uma tarefa com alterações pendentes deve pedir cuidado; não deve gravar por si só.

## Limites e próximas decisões

- A integração usa adaptadores/iframes da mesma origem para os fluxos existentes. Uma futura migração a componentes inteiramente nativos deverá manter a mesma matriz de funções.
- PDFs/imagens selecionados do computador precisam ser selecionados novamente após recarregar. BookReader continua externo; Annotorious/Mirador não foram adicionados.
- A validação visual, arraste, foco, impressão, OCR real, edição privada e ciclo HTTP de gravação não foram executados nesta entrega. O responsável solicitou realizar os testes de navegador. Foram conferidas sintaxe e referências estáticas; não houve processamento documental, criação de registros de teste, commit ou push.
- Esta entrega não declara a nova bancada estável nem substitui a home ou os acessos oficiais antes da validação. O objetivo é permitir avaliar os fluxos completos no novo ambiente sem remover o anterior.
