# ShowTrials Discovery: workspace editorial inspirado em IDE

20/10/2026. Diagnóstico por inspeção do código e protótipo funcional separado. Esta proposta revisa a organização da **área de trabalho**, não substitui o portal e a leitura pública nem declara a migração concluída. A interface Carmim continua oficial até avaliação.

## 1. Decisão de arquitetura

Adotar a organização espacial de uma IDE para o trabalho documental: um explorador contextual, documentos e instrumentos em abas, grupos de editores, divisores redimensionáveis, ferramentas por atividade e acompanhamento inferior. Manter a identidade Carmim e a tipografia de leitura. Uma ficha documental não precisa ocupar o mesmo lugar que a árvore de documentos; um OCR não precisa esconder o texto que está sendo conferido.

O problema central é o modelo de interação, não a escolha entre CSS próprio e framework. Mudar cores ou introduzir um framework não torna independentes os documentos, ferramentas e contextos hoje acoplados. Recomendo validar este protótipo antes de escolher uma biblioteca de docking ou migrar toda a aplicação.

## 2. Diagnóstico da aplicação existente

Método: leitura dos pontos abaixo, confrontando-os com os fluxos solicitados. Não houve estudo com outros usuários, medição de desempenho ou auditoria visual em navegador gráfico. Severidade indica impacto estimado no trabalho, não uma estatística de uso.

| Constatação e evidência | Consequência prática | Prioridade / direção |
| --- | --- | --- |
| `assets/workbench.js`: `mount`, `capture` e `showTool` dependem de `state.activeDocument`, do leitor e da rota global. `renderTabs` muda o hash. | As abas são caminhos para o leitor ativo; não são editores independentes para comparar documentos arbitrários. | Alta: separar modelo documental, instância de visualização e grupo de editores. |
| `installInstruments` e `showTool` apresentam Markdown, índice, ficha e notas em um único `workspace-dock`, substituindo seu conteúdo. | Conferir uma ficha faz perder a ferramenta que ocupava aquele painel; não é possível organizar todos como abas. | Alta: instrumentos documentais tornam-se tipos de aba. |
| `assets/css/workbench.css` organiza lateral e frame do documento, sem um gerenciador geral de grupos. | A largura e a posição dos instrumentos seguem o layout do leitor. O espaço não acompanha a tarefa. | Alta: grupos lado a lado ou empilhados, com divisores. |
| `backend/editorial.html` tem sua própria navegação; `assets/editorial.js` escolhe páginas por `route`. A bancada tem outra navegação. | Edição, importação, pesquisa e ferramentas são acessadas por estruturas diferentes. O contexto precisa ser transportado em parâmetros. | Alta: uma entrada por atividade; comando documental recebe documento e idioma ativos. |
| `assets/app.js` mantém o painel do leitor com idioma, edição, exportação e navegação; a bancada acrescenta outra camada. | No trabalho intensivo, navegação e ações documentais concorrem pelo mesmo espaço. | Média: o portal conserva seu leitor; o workspace usa comandos contextuais compactos, sem repetir a navbar pública. |
| `assets/project-editor.js`, `backend/workspace_editions.py` e `assets/research-projects.js` já separam versões de projeto e acervo. | Existe uma proteção valiosa. Uma nova interface pode confundir essa separação se exibir apenas o título do documento. | Crítica: contexto e destino de gravação explícitos na aba e no formulário; promoção continua deliberada. |
| `assets/editorial.js`: `markdownPage`, `previewPanel`; backend editorial preserva versões. | Prévia, diferenças e histórico já resolvem a proteção da edição. | Preservar: trocar a navegação sem reimplementar a regra de gravação. |
| `pdf-sources.js`, `pdf-tools.js`, `pdf-review.js`, `pdf-alignment.js` e `pdf-workflow.js` contêm operações reais de ingestão e revisão. | Não precisamos inventar novas ferramentas; precisamos encaixá-las em tarefas e recursos. | Alta: fonte PDF e tarefa de OCR devem ser recursos do workspace, não uma sucessão de páginas soltas. |
| `data/manifest.json` combina documentos globais, coleções com `document_ids` e coleções legadas com documentos embutidos. | Somar listas ou assumir um único formato omite documentos e pode duplicá-los. | Alta: adaptador único de catálogo, deduplicação por ID e preservação da ordem/subcoleções. |
| Estado de leitura, abas, rascunhos e notas usam mecanismos de sessão; dados persistentes têm outro armazenamento. | “Retomar” e “salvar” têm sentidos diferentes. O usuário precisa saber o que sobrevive à sessão. | Alta: diferenciar rascunho de sessão, gravação privada, gravação canônica e publicação. |
| Publicação PDF prepara/aplica uma projeção local; Git/push são separados. | “Disponível localmente” não significa “publicado no GitHub”. | Preservar: nunca rotular uma gravação como publicação remota. |
| Portal, leitor, editoria e pesquisa têm necessidades distintas. | Aplicar uma IDE à página de leitura pública pode piorar o acesso à fonte. | Preservar: IDE para o editor-pesquisador; leitor público mantém simplicidade. |

Não foram descartados os avanços anteriores: catálogo/proveniência, histórico, fronteiras editoriais, versões privadas, fac-símiles e tratamento das fontes são a base desta reorganização.

## 3. Arquitetura de informação proposta

```text
Portal / Documentos Soviéticos → leitura pública e busca
                  ↓ abrir na bancada
ShowTrials Discovery / workspace local
├── Barra superior: identidade, abrir documento/comando, voltar ao portal
├── Faixa de atividades
│   ├── Explorar: contexto explícito → coleção/subcoleção/documentos
│   ├── Buscar: localizar dentro do contexto; informar escopo da pesquisa
│   ├── Revisar: fila, histórico, comandos de tradução e edição
│   ├── Preparar fontes: PDF, operações, extração, OCR e alinhamento
│   └── Organizar: catálogo, coleções, projetos, cadastro e lote
├── Área central: grupos redimensionáveis
│   ├── Documento / idioma / leitura
│   ├── Documento / idioma / Markdown
│   ├── Documento / índice
│   ├── Documento / ficha
│   └── Ferramenta / fonte / tarefa
├── Acompanhamento inferior: atividade e notas; futuramente tarefas reais
└── Estado: backend, projeto, documento/idioma e rascunhos
```

A faixa de atividades responde **que tarefa estou fazendo**. A lateral responde **com quais recursos**. As abas respondem **o que está aberto**. Os comandos do documento respondem **o que fazer com a versão ativa**. A área inferior não repete a árvore nem as ações do leitor.

Índice e ficha usam o mesmo mecanismo de abas do documento. Ferramentas globais de catálogo/fila/histórico identificam o destino como acervo, mesmo se houver projeto selecionado. Ferramentas de fontes recebem o contexto do projeto quando aplicável. A entrada sempre começa sem projeto ativo; a escolha deve ser explícita.

## 4. Modelo de estado para a implementação definitiva

- **Contexto de trabalho:** acervo ou ID de projeto. É um contexto de dados; não é autenticação nem uma declaração de que todo comando naquele espaço modifica apenas o projeto.
- **Recurso:** documento, edição por idioma, fonte PDF, tarefa, ficha ou inventário. IDs e URLs públicas permanecem estáveis.
- **Modelo de edição:** conteúdo carregado, revisão/hash-base, rascunho, destino da gravação e estado de conflito. Duas visualizações podem compartilhar o modelo sem compartilhar cursor e rolagem.
- **Visualização:** leitura, Markdown, fac-símile, índice ou ficha. Mantém posição, seleção e foco próprios.
- **Grupo:** lista ordenada de visualizações, aba ativa e tamanho. Grupos não alteram o documento nem seu contexto.
- **Comando:** rótulo, contexto permitido, recurso alvo, capacidade necessária e resultado. Deve ficar desabilitado/explicado quando faltar documento ou backend.
- **Gravação:** prévia → comparação → confirmação → histórico → invalidação/atualização das visualizações afetadas. Publicação é um comando separado.

Contrato de cada ferramenta futura: montar em um host; receber contexto e capacidades; declarar se há alterações pendentes; fornecer título e ações; poder suspender/retomar sem perder dados; emitir eventos de recurso alterado; liberar listeners e requisições ao fechar. Esse contrato é mais importante que replicar o menu de um editor de programação.

## 5. Fluxos editoriais na nova organização

| Objetivo | Percurso esperado | Proteção que deve permanecer |
| --- | --- | --- |
| Comparar RU/PT | Abrir documento → duas visualizações com idiomas distintos → grupos lado a lado | Idiomas e rolagem por visualização; não prometer alinhamento automático. |
| Corrigir tradução | Abrir Markdown → comparar com original → editar → prévia/diferenças → salvar | Hash-base, idioma explícito e versão anterior recuperável. |
| Importar tradução | Ativar documento → Revisar → Importar tradução | Identificação, idioma, divergências e substituição confirmada. |
| Trabalhar privadamente | Selecionar projeto → abrir recurso → editar versão privada | Nenhuma substituição canônica silenciosa; promoção explícita. |
| Incorporar PDF | Escolher contexto → fonte → operação PDF → extração/OCR → revisão por página → alinhamento → incorporação | Fonte preservada, progresso persistente e proveniência por página/unidade. |
| Publicar fac-símile | Selecionar vínculos → preparar derivado → conferir → aplicar localmente | Excluir material privado; Git/push continuam separados. |
| Catalogar | Organizar → ficha/metadados/coleções → prévia → salvar | URL/ID preservados, catálogo/manifesto/busca atualizados. |

## 6. O protótipo entregue

Acesso: **`http://127.0.0.1:8000/prototipo/ide/`**. Reinicie o backend para carregar a autorização da nova rota. `python3 -m http.server 8000` também permite experimentar a parte estática. Em hospedagem com prefixo, os recursos do protótipo usam caminhos relativos à raiz daquele site.

### Funciona nesta entrega

- Catálogo real, com os dois formatos do manifesto, coleções e subcoleções; busca por metadados no contexto.
- Seleção explícita de projeto local, sem herdar projeto ativo do backend; consulta das versões privadas pelo endpoint existente.
- Abas independentes de leitura, Markdown, ficha e índice; idiomas por aba, rolagem preservada na alternância; índice abre/aponta uma leitura.
- Até **dois grupos**, à direita ou abaixo, redimensionáveis; arrastar abas entre grupos e reordenar. Alternativa por botão/comando para quem não arrasta.
- Rascunho Markdown e prévia compartilhados; recuperação na sessão, cópia baixável, proteção quando a fonte mudou; teclado russo existente.
- Marcador de bloco por clique, segundo clique desmarca e Retomar. Numeração é local a esta versão, não uma cota histórica nem um alinhamento RU/PT.
- Paleta de documentos/comandos, navegação de abas por teclado e lateral/área inferior retráteis.
- Fluxos existentes de edição, cadastro, PDF, OCR e histórico integrados em abas locais. Gravar continua sendo uma operação real do formulário.
- Rascunhos canônicos podem seguir para o editor existente por seu contrato de transferência de sessão, com conferência da fonte-base. A gravação exige a prévia existente.

### Limites explícitos

- Os formulários e as ferramentas locais são incorporados por **iframe da mesma origem**. O cabeçalho/lateral duplicados da editoria são ocultados dentro da aba. É uma ponte para avaliar fluxos, não o destino arquitetural. Edição privada usa a bancada existente dentro da aba.
- Alternar abas preserva os hosts incorporados. **Mover um formulário entre grupos, reunir seu grupo ou fechá-lo pode recarregá-lo**; há confirmação antes dessas ações. O contexto de ferramenta não tem ainda contrato nativo de suspensão/rascunho.
- Depois de salvar no formulário incorporado, use **Atualizar acervo e versões abertas**. A integração de eventos automática entre hosts é pendência.
- Rascunhos privados digitados no editor Markdown do protótipo precisam ser copiados/baixados para o editor privado. O encaminhamento automático está implementado somente para versões canônicas.
- Abas reabertas após recarregar ficam em um grupo; não há docking arbitrário, múltiplas janelas ou restauração completa do layout. Projetos exigem seleção de novo.
- Notas e rascunhos desta bancada estão na sessão do navegador; não são os históricos persistentes do backend. Atividade inferior registra ações do protótipo, não é um monitor de jobs ou log de auditoria completo.
- Busca aqui é de metadados do manifesto, sem equivalência com o FTS local. Índice não inventa títulos. Ficha não inventa metadados ausentes.
- A alternância de idiomas abre uma perspectiva da versão disponível; o protótipo não recria ainda todo o estudo alinhado, a edição de trechos e os fac-símiles do leitor oficial. Esses recursos continuam no site existente.

## 7. Validação manual dirigida

1. Abra a URL do protótipo com o backend. Confira “Backend local disponível”, **Acervo · sem projeto**, árvore de coleções e grupos vazios. A interface oficial continua em `/`.
2. Expanda Centro de Leningrado e Materiais da investigação. Abra dois documentos. Alterne abas e confira que não se confundem os títulos, idiomas e posições de leitura.
3. Em um documento, escolha Markdown e **Ao lado**. Edite uma frase no rascunho; confira a prévia do mesmo documento no outro grupo. Não há gravação automática. Baixe uma cópia.
4. Abra Ficha e Índice. Arraste suas abas entre os grupos, reordene, use Dividir/Abaixo e ajuste o divisor. Use também o comando Mover para testar sem arraste. Confira que o índice aponta para a leitura da versão correspondente.
5. Marque um parágrafo, alterne abas, retorne e clique Retomar. Clique novamente no parágrafo para desmarcar. Essas marcas são do protótipo, separadas das marcas do leitor oficial.
6. Teste Ctrl/Cmd K para abrir documentos/comandos; Ctrl/Cmd B para a lateral; setas/Home/End na faixa de abas; Tab para os divisores e setas para redimensionar. No celular, a lateral abre sobre o trabalho e os grupos empilham.
7. No Markdown do acervo, use Editar e salvar. Confira o aviso de rascunho recebido no formulário, a prévia e diferenças **antes de confirmar qualquer alteração real**. Alterne para outra aba e volte: o formulário deve continuar carregado. Se optar por salvar um ajuste legítimo, atualize o acervo na lateral e confira o resultado e o Histórico.
8. Abra Ferramentas → Fontes PDF ou Manipular PDF; confira seus fluxos conhecidos dentro de uma aba. Cadastro, upload e confirmação nesses formulários são reais: use apenas material que queira guardar, ou um ambiente de teste separado.
9. Selecione um projeto existente. Confira apenas seus documentos, o aviso de contexto privado e a versão privada conhecida. Volte ao acervo e confirme que esse texto não substituiu a versão canônica.
10. Pare o backend e sirva com `python3 -m http.server 8000`. Leitura/rascunhos continuam; ferramentas locais ficam indisponíveis com explicação. Não aparece uma simulação de salvamento.

## 8. Próxima implementação, depois da avaliação

1. Corrigir o que a avaliação demonstrar no protótipo: hierarquia, nomes, densidade, uso de painéis e comandos. Não assumir que a preferência por IDE implica todos os atalhos ou recursos do VS Code.
2. Extrair o gerenciador de recursos/visualizações/grupos para um módulo próprio e testar foco, rolagem, conflitos e fechamento com rascunhos.
3. Converter primeiro o editor Markdown e a ficha em componentes nativos; preservar a API editorial. Integrar prévia/diferenças como etapa de trabalho, com histórico e destino visíveis.
4. Converter revisão PDF, OCR e fac-símile em recursos nativos de fonte/página/tarefa. Acompanhamento inferior recebe progresso real. Transferir rascunhos privados pelo contrato adequado.
5. Integrar invalidação de catálogo/busca e eventos de salvamento, estudo e citações. Só então considerar substituir a bancada oficial.

Aceite da migração: nenhuma perda de edição na alternância/reorganização; contexto de gravação inequívoco; operações recuperáveis; todos os recursos do leitor preservados; foco e teclado utilizáveis; telas pequenas atendidas; nenhuma URL ou fonte histórica alterada por uma mudança de layout.

## 9. Verificações realizadas nesta entrega

- Nove verificações de interação passaram em QuickJS com DOM simulado: manifesto misto/subcoleções, hosts de ferramenta preservados, encaminhamento do rascunho para prévia, movimento entre grupos, contexto privado, cancelamento de movimento de formulário, ferramenta global explicitamente no acervo, recuperação após mudança da fonte e manutenção do host ao reorganizar o layout.
- Verificação HTTP em diretório temporário passou: redirecionamento da nova rota, HTML/CSS/JS disponíveis e arquivo não autorizado bloqueado. Não foi iniciado um backend sobre o acervo real.
- Sintaxe JavaScript/Python e `git diff --check` passaram. O QuickJS já disponível no ambiente foi usado sem instalar dependências no projeto; os testes de interação são opcionais quando ele não está instalado.
- Não houve avaliação visual, arraste real, foco real, leitura de PDF em navegador nem gravação editorial ponta a ponta nesta rodada: faltava navegador gráfico. O DOM simulado não substitui esses testes. Use a seção 7 para avaliá-los.
- Nenhum original, tradução, URL documental, catálogo ou manifesto foi alterado nesta entrega. Alterações locais desses dois últimos arquivos já existiam e foram preservadas. Não houve commit ou push.

## 10. Refinamento por tarefa — avaliação seguinte

A avaliação do responsável apontou excesso de rolagem em ferramentas como OCR. Esta revisão mantém o workspace e reorganiza o conteúdo:

- A lateral de Busca, Revisão, Ferramentas e Organização oferece **Abrir na área de trabalho**. A escolha abre ou reativa uma aba da atividade; não substitui documentos abertos.
- A busca completa tem filtros combináveis de coleção, subcoleção, idioma e tipo, termos por metadados, ordenação e paginação de 25 resultados. Mantém filtros ao alternar abas e permite abrir o resultado no outro grupo. O contexto de projeto restringe os resultados. Não é busca de texto completo.
- As demais atividades têm uma página central com tarefas e próximos acessos, em vez de obrigar o trabalho pela lateral estreita.
- As fontes PDF incorporadas na IDE passam a ter seções de **Revisar página / OCR / Cadastro da fonte / Vínculos / Incorporar / Disponibilizar**. Seções ainda indisponíveis ficam desabilitadas. Disponibilizar refere-se à projeção local já existente, sem Git/push automático.
- Dentro da revisão: **Texto / Candidatos OCR / Alinhamento / Referências / Histórico**. No OCR: **Configurar lote / Andamento dos lotes**. São seções da mesma tarefa, não etapas obrigatoriamente lineares.
- Os formulários continuam no mesmo DOM ao alternar seções: mudar de seção não salva, descarta, recria ou reinicializa o texto. As prévias e confirmações existentes continuam obrigatórias. Os rascunhos de página e o progresso continuam sob responsabilidade do backend e dos módulos existentes.
- Campos e fac-símile usam melhor a altura disponível; históricos e lotes longos têm rolagem delimitada. No espaço estreito os elementos empilham. O objetivo é reduzir o empilhamento de tarefas, não esconder o conteúdo de um documento longo.

Implementação: atributos semânticos adicionados aos módulos PDF existentes; o script e CSS de organização são carregados **somente nos formulários incorporados pelo protótipo IDE**. A área editorial oficial mantém sua apresentação. O adaptador observa a chegada de conteúdo assíncrono e não move formulários nem o iframe do fac-símile. O isolamento por raiz de fonte evita aplicar controles duplicados em fontes revisadas dentro da ferramenta de operações.

### Conferência desta revisão

1. Recarregue `/prototipo/ide/` com **Ctrl+Shift+R**. Reabra abas de ferramentas que já estavam abertas para carregar os novos recursos incorporados.
2. Clique Busca na faixa lateral e depois **Abrir busca detalhada na área de trabalho**. Combine coleção/subcoleção/idioma, aplique filtros, navegue páginas e use Abrir ao lado. Volte à aba de busca: os filtros devem continuar preenchidos.
3. Faça o mesmo em Revisão, Ferramentas e Organização. A área central deve apresentar as tarefas, sem fechar as abas de documentos.
4. Abra uma fonte PDF existente. Alterne Revisar página e OCR; dentro de OCR alterne Configurar lote e Andamento dos lotes. O processamento e a adoção de um candidato continuam sendo comandos explícitos.
5. Digite uma correção em Texto sem salvar, alterne para Candidatos/Histórico e volte. O conteúdo deve permanecer. Confira que a alternância não abriu nem confirmou uma prévia de gravação sozinha.
6. Confira cadastro, vínculos e incorporação separadamente; em projeto privado, a disponibilidade de publicação continua obedecendo ao fluxo existente.

Verificações executadas: 12 testes de interação do workspace passaram com DOM simulado; as verificações existentes de revisão (6), OCR (4) e incorporação/publicação (7) também passaram. Sintaxe dos cinco JavaScripts envolvidos e `git diff --check` conferidos. Não houve teste visual em navegador gráfico nem OCR real nesta rodada, e nenhuma fonte, tradução ou cadastro foi gravado. Não houve commit/push.

## 11. Mesa de revisão e reinício dos testes locais

O responsável apontou que a coluna do fac-símile ficava menor e menos útil que o formulário. A revisão ganhou modos **Fac-símile / Comparar / Transcrição**, proporção ajustável na comparação e uma altura útil comum para imagem e editor. Em uma área estreita, a visualização inicial privilegia o fac-símile; o usuário alterna a perspectiva explicitamente. Na comparação estreita, as duas áreas empilham.

A transcrição ocupa o centro do painel: aparência de folha de edição, configuração de conferência/rótulo compacta e notas recolhidas por botão. Teclado russo e prévia de gravação permanecem disponíveis. Alternar perspectivas não recria o iframe da fonte nem descarta o rascunho. A organização continua sendo experimental e carregada somente na bancada IDE.

Após implementar e conferir a lógica, foi executada a limpeza solicitada, com backend encerrado e lock exclusivo. Cópia recuperável em `.local/archives/test-reset-20261020T231256Z/`, com `AUDIT.json`, README, bases anteriores, PDFs, derivados e estado anterior dos dois JSON alterados. Foram retirados do ambiente ativo:

- Coleção vazia `teste01` e seu registro específico de criação no histórico.
- Dois projetos de teste, sem versões privadas gravadas.
- Treze fontes PDF de teste, operações de divisão, extrações, candidatos/lotes OCR e caches associados.
- Um vínculo experimental da fonte derivada com o documento `showtrials-1665` e seu histórico.

Os originais, traduções, documentos, URLs, coleção histórica de Tukhachevsky e seus PDFs em `fontes/`, demais históricos editoriais, materiais de trabalho militares e `temporario/` foram preservados. O catálogo/manifesto sem `teste01` coincidem com a versão já registrada no Git. O índice anterior foi arquivado; o backend construirá um novo ao iniciar. As bases ativas de fontes e projetos foram inicializadas vazias, sem workers. Não houve publicação, commit ou push.

Para avaliar: inicie `python3 -m backend`, feche a aba antiga e reabra `/prototipo/ide/` (ou use Ctrl+Shift+R para a aparência, caso deseje manter a sessão). Envie um PDF, abra a fonte, compare os três modos, ajuste a proporção e confira que notas, troca de perspectiva e retorno ao texto preservam o rascunho. A sessão do navegador não foi apagada remotamente: fechar a aba e iniciar outra permite começar sem seus rascunhos/abas anteriores.

Verificações: 13 testes do workspace em DOM simulado passaram, incluindo a permanência do iframe e da transcrição ao alternar os três modos; 6 verificações existentes da revisão e 4 de OCR passaram. Sintaxe JavaScript e whitespace conferidos. Na limpeza, o catálogo foi validado, os hashes dos demais arquivos canônicos comparados e as bases ativas de fontes/projetos confirmadas vazias. Avaliação visual continua manual.

### Cabeçalho compacto da fonte

Retirado, somente na bancada IDE, o bloco introdutório repetido “Fontes PDF” e sua explicação. O nome da fonte e o retorno à lista agora integram a barra de ações, com título truncado e identificação completa acessível ao passar o cursor. SHA, vínculos de projeto e proveniência ficam na seção Cadastro da fonte; progresso e avisos de erro permanecem visíveis. O formulário de cadastro e o fac-símile não são recriados. Reabra a ferramenta após Ctrl+Shift+R para conferir o espaço vertical liberado. As 13 verificações existentes foram ignoradas nesta rodada porque o QuickJS opcional não está disponível neste ambiente; não foi feita instalação para este ajuste visual. Avaliação visual manual pendente. Sem alterações no acervo, commit ou push.


### Altura ajustável e identidade comum na editoria

O OCR já era operacional sobre a fonte enviada: extrair/dividir páginas não é pré-requisito. As instruções de upload e os cartões da preparação agora explicitam essa possibilidade, evitando a impressão de uma sequência obrigatória.

A altura da área de revisão pode ser ajustada entre 320 e 1400 px pelo campo **Altura**, pela borda inferior arrastável ou com setas quando o divisor tem foco. **Automática** volta a acompanhar a janela. A preferência é da sessão do navegador e vale para as fontes abertas depois; não modifica páginas, texto ou configurações de OCR. A proporção horizontal permanece independente. A borda e os controles de revisão ficam ocultos nas outras seções, como OCR e cadastro.

Por solicitação do responsável, o padrão visual foi estendido à área editorial direta e às ferramentas da bancada existente: campos, rótulos, painéis, ações, importações e prévias compartilham uma escala compacta. O portal e a leitura pública não recebem o layout de formulário. As fontes PDF da editoria passam a usar as mesmas seções e mesa de revisão do protótipo. O carregamento do adaptador é único, inclusive nas abas incorporadas, para não duplicar controles/listeners. Não há mudança nas APIs ou nas regras de gravação.

Validação: sintaxe de quatro JavaScripts conferida em V8; cinco verificações em DOM simulado passaram para altura manual, teclado, preferência de sessão, preservação do iframe e retorno ao modo automático. Recursos de CSS/JS das duas entradas HTML existem e `git diff --check` foi conferido. Não houve instalação de dependências, execução de OCR, gravação no acervo, avaliação visual em navegador, commit ou push.

Conferência manual: recarregue com Ctrl+Shift+R e reabra a ferramenta. Envie um PDF, abra a fonte, escolha **OCR** e informe as páginas diretamente. Em Revisar página, ajuste Altura ou arraste a borda inferior; alterne as perspectivas e confira que a altura permanece; escolha Automática para restaurar o ajuste à janela. Confira também `/editorial` em catálogo, importação e fontes PDF para comparar a consistência visual.

### Revisão funcional após o bloqueio no OCR

O painel OCR continuava fechado enquanto seu expansor era ocultado pelo estilo. Os testes anteriores com DOM simulado não detectaram esse bloqueio visual. A correção e a nova validação por Chromium, com OCR real, revisão salva, extração e divisão, estão registradas em [REVISAO-FLUXO-IDE.md](pdf-ocr/REVISAO-FLUXO-IDE.md). O percurso gráfico passou, assim como 59 testes existentes. A manipulação PDF agora usa uma sequência Fonte → Operação → Conferência; os estados das telas e a acessibilidade dos controles foram corrigidos. O acervo real foi preservado e não houve commit/push.
