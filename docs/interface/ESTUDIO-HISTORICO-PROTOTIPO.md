# Estúdio documental — experimento de fluxo nativo

26/10/2026. Protótipo separado para avaliar uma mudança de concepção, sem substituir `/editorial` ou a home pública.

## Abrir

Reinicie `python3 -m backend` e abra **http://127.0.0.1:8000/prototipo/estudio/**. Use Ctrl+Shift+R. Nenhum npm ou serviço pago é necessário.

O ciclo é real: arquivos são recebidos pelas APIs existentes; OCR produz candidatos existentes; salvar uma prévia confirmada altera o armazenamento local com o histórico já implementado. Abrir o protótipo não grava nem processa documentos automaticamente.

## A ideia

O objeto de trabalho é uma fonte/página ou uma versão documental. Abas e ferramentas compartilham esse contexto, em vez de montar páginas editoriais completas e depois adaptá-las. O usuário pode arrastar os painéis, mas começa com uma composição útil: fac-símile à esquerda e transcrição à direita.

- O explorador alterna entre fontes e acervo; na fonte, passa a mostrar as páginas e seu progresso.
- OCR, candidatos, histórico, citações e ficha são ferramentas contextuais da mesma mesa.
- A comparação antes de salvar é um painel real de diferenças; a confirmação ocupa uma ferramenta contextual, sem estender o formulário inteiro.
- Projetos são escolhidos explicitamente para novos materiais. Abas existentes mantêm seu contexto. Recarregar começa sem projeto.
- Documento privado usa os endpoints de workspace. Não há promoção automática. Revisões de páginas PDF pertencem à fonte local compartilhada, e não criam cópias privadas de transcrição por projeto.
- Ctrl K abre comandos; Concentrar recolhe o entorno; Escape fecha a ferramenta ou restaura o entorno.

## Como começar a validação

1. Em **Continuar uma fonte**, escolha o PDF que já usou. A imagem e a transcrição devem mostrar os dados existentes. Não precisa reenviar o arquivo.
2. Navegue pelas páginas do explorador. A imagem e o editor devem acompanhar a mesma página. Rascunhos são guardados por contexto/página na sessão; não se promete persistência depois de encerrar a sessão.
3. Abra **OCR**. Confira o intervalo, idioma, resolução e segmentação. **Conferir lote** prepara a prévia; **Executar OCR local** inicia o trabalho real. Para avaliar o layout, não é necessário executar novo lote: use candidatos já existentes.
4. Em **Candidatos**, carregue uma versão no editor. Confira o texto, use o teclado russo e os comandos de formatação. O candidato passa a pendente de conferência; não é adotado silenciosamente como página revisada.
5. Em **Organizar mesa → Ficha / ferramentas**, registre rótulo impresso, estado e notas. **Conferir e salvar** mostra diferenças e metadados; **Confirmar gravação local** grava com histórico. O formulário não cresce para fora da área da mesa.
6. Abra **Histórico** e confira o acesso à extração bruta, download anterior e preparação de restauração. Não precisa restaurar se não houver uma mudança desejada.
7. Selecione um trecho salvo e use **Citar**. A unidade é incluída quando a seleção coincide exatamente com uma unidade salva. Um rascunho não é citado como se fosse a revisão aprovada. Não há alinhamento geométrico automático novo.
8. Em **Imagem**, prepare uma prévia com cinza, threshold, erosão e escala. Compare com a fonte ao lado e baixe imagem/receita. A receita indica expressamente que o derivado não foi usado no OCR do backend.
9. No **Acervo**, pesquise e abra um texto. O leitor oferece **Editar** e o editor oferece **Prévia**; arraste-os lado a lado. No projeto, abra outra versão PT/EN pela ficha para trabalhar em uma tradução privada. Sem projeto, a inclusão de uma tradução nova continua no importador existente.
10. Confira **Diagnóstico** no rodapé: ele lista duração e resultado das consultas. Informe qual pedido demora se houver problema. Uma falha deve oferecer mensagem e recuperação, não manter um carregamento indefinido.

## Implementado e limite desta entrega

| Frente | Situação no estúdio |
|---|---|
| Entrada e explorador | Componentes novos; nenhum adaptador da interface anterior |
| Abas/painéis | Dockview; arraste, ampliação e fechamento |
| PDF | PDF.js nativo, uma página de cada vez, cancelamento de renderização anterior; sem camada textual selecionável nesta etapa |
| Transcrição | CodeMirror, teclado russo, rascunho, candidato, prévia, salvamento e histórico existentes |
| OCR | Configuração, prévia, execução, andamento e retomada; idiomas instalados no backend |
| Markdown | Edição/preview/compare; salvamento canônico ou privado conforme contexto; TXT apenas consulta |
| Pesquisa | API paginada do índice, até 30 resultados; não transfere o catálogo inteiro |
| Projetos | Seleção explícita e versões privadas; administração e promoção permanecem no ambiente existente |
| Imagem | Ensaio funcional em Web Worker; não é ainda um pipeline ImageMagick do backend |
| Coleções | Criação de coleção/subcoleção e navegação central; prévia e histórico existentes |
| Classificação | Vincular fonte à coleção/subcoleção; adicionar coleção ao documento preservando vínculos anteriores |
| Incorporação | Novo documento de páginas conferidas, com proveniência; incorporação privada e operações avançadas continuam no ambiente anterior |
| Alinhamento e importação em lote | Acesso às ferramentas existentes; migração ainda pendente |
| Índice/marcador de leitura, estudo paralelo e edição de trecho | Permanecem no leitor oficial; ainda não portados a estes componentes |
| BookReader, impressão e imagem ampliável | Continuam no protótipo anterior; seleção dos visualizadores adequados fica para a próxima avaliação |

A proposta não declara que todas as funções foram migradas. O ambiente existente permanece acessível porque a validação deste núcleo deve anteceder a migração completa.

## Desempenho e arquitetura

A entrada tem HTML/CSS/JS próprios, com aproximadamente 55 KB de JavaScript inicial, sem compressão. Dockview/CodeMirror são importados quando a mesa é aberta; PDF.js quando uma fonte é aberta; renderização Markdown somente quando há leitura/preview. As bibliotecas vêm da distribuição já preservada em `../oficina/vendor/`, sem novo build ou instalação npm.

O manifesto atual tem 7.402.728 bytes e não é solicitado por este protótipo. A busca usa o índice do backend. Não há iframes nem MutationObserver no núcleo novo. Pedidos de leitura têm prazo, pedidos obsoletos de página são cancelados e respostas atrasadas são ignoradas. A atualização periódica é limitada à fonte ativa em processamento e pausa quando a página fica oculta.

O backend ganhou `GET /api/editorial/pdf/sources?light=1`, que omite a detecção de motores. O contrato anterior permanece por padrão. A lista de arquivos permitidos da distribuição BookReader passou a ser lida uma vez de seu manifesto, substituindo a varredura recursiva em cada recurso estático. Isso beneficia também a interface anterior.

Esses são ganhos de estrutura, não um benchmark de navegação já comprovado no navegador. Consultas editoriais ainda podem validar o catálogo inteiro no backend; esse custo precisa ser medido antes de uma refatoração de servidor.

## Tratamento de imagens e OCR

O ensaio usa Canvas/OffscreenCanvas em Worker. Trabalha sobre a imagem de consulta renderizada, não sobre um fac-símile arquivístico original. Tem limite de pixels e é descartável. Erosão implementada como mínimo tonal de uma vizinhança 3×3: escurece/expande regiões pretas; é preciso definir a polaridade ao transformar isso em uma receita editorial.

O próximo pipeline definitivo deve usar ImageMagick no backend, preservar imagem original e derivados, registrar receita/motor/hash e transformações de escala/recorte/rotação para remapear coordenadas ao original. O OCR precisa declarar qual derivado usou. Não conectar a prévia visual ao OCR fingindo uma proveniência que ainda não foi implementada. Motor de tradução não foi configurado nem há envio externo.

## Verificações

Conferidas sintaxe JS/Python e referências/IDs de controles. Simulações isoladas verificaram proteção contra resposta atrasada de página, rascunho por contexto e estrutura da proposta de revisão. A consulta leve foi verificada sem instanciar o backend ou abrir banco real. Não executados testes de navegador, uploads, gravações documentais ou OCR real nesta entrega. A interação dos painéis e o ciclo completo aguardam validação manual. Sem commit ou push.

## Próximas entregas após a avaliação

1. Ajustar a mesa a partir do uso real e completar tratamentos de imagem com derivados e OCR rastreáveis.
2. Migrar vínculos, alinhamento, incorporação e tradução/importação para componentes do mesmo núcleo; manter confirmação separada de promoção.
3. Migrar catálogo/cadastros/coleções/revisão, depois instrumentos de estudo e visualizadores complementares, usando uma matriz de equivalência para não perder funções.


## Teclado russo e continuação do piloto — 27/10/2026

O teclado do Estúdio agora segue linhas ЙЦУКЕН, com números/pontuação, **⇪** para maiúsculas persistentes, apagar, Enter e espaço. As teclas preservam a seleção do editor; digitar substitui a seleção, em vez de acrescentar a letra ao trecho selecionado. O teclado abre sobre o texto para não reduzir permanentemente a área de edição. Requer reiniciar o backend para liberar o novo módulo e recarregar o protótipo.

Para continuar do OCR até o catálogo, os cadastros ainda são feitos na área editorial existente:

1. No Estúdio, confronte a página 4 com a imagem. Em **Organizar mesa → Ficha / ferramentas**, escolha **Conferida** apenas depois do cotejo. Use **Conferir e salvar → Confirmar gravação local**. Salvar como Pendente já preserva o trabalho, mas não habilita a incorporação.
2. Abra `/editorial#/nova-colecao`. Exemplo: título **Zinoviev — Sentença merecida**; identificador **zinoviev-sentenca-merecida**; coleção principal **Nenhuma — criar coleção principal**. Descrição e capa podem ficar para depois. Use **Revisar coleção**, confira e confirme.
3. Na ferramenta da fonte PDF, em **Dados e publicação → Cadastro da fonte**, selecione a nova coleção e idioma russo. Confira e confirme o cadastro. O PDF já está preservado no armazenamento de fontes; esta etapa registra sua classificação, sem repetir o upload nem criar ainda o documento de leitura.
4. Em **Dados e publicação → Incorporar**, escolha **Novo documento no acervo local**, idioma **Russo**, páginas **4**, ID por exemplo **zinoviev-sentenca-merecida-d425-p4** e título **Sentença merecida — transcrição parcial, d.425, página física 4**. Selecione a coleção criada. Deixe datas não determinadas em branco. Use **Conferir incorporação** e **Confirmar incorporação local**.
5. Abra o documento incorporado e confira texto e vínculo à fonte/página. O catálogo, manifesto e busca são atualizados pelo fluxo existente. Salvar localmente não faz push nem publica no GitHub Pages.

Uma coleção organiza fontes/documentos; a revisão da página preserva a transcrição; a incorporação cria o documento navegável no acervo. São registros relacionados, não três cópias de upload. Ao substituir uma versão por uma seleção maior, inclua também as páginas anteriores que deseja manter: a incorporação não é uma operação de acrescentar texto automaticamente. Para este piloto, incorpore somente a página que foi efetivamente conferida.


### Ações acessíveis na ficha — 27/10/2026

A ficha da página tem agora **Conferir e salvar** e **Voltar à mesa** em um rodapé fixo do painel. A confirmação da gravação também usa esse rodapé, sem exigir voltar ao botão da barra superior. **Recolher** substitui o ícone isolado de fechar. Recolher preserva o rascunho. Em telas largas, a ferramenta ocupa uma coluna própria; em telas menores, conserva a apresentação sobreposta com ações internas acessíveis. Validar após Ctrl+Shift+R: alterar Conferência, usar Conferir e salvar na própria ficha e confirmar no rodapé. Sem gravações de teste, commit ou push.


## Organização no próprio Estúdio — 27/10/2026

A grade de páginas permanece no explorador. Nas outras seções, a lateral oferece navegação e materiais abertos; a pesquisa do acervo, as fontes e as coleções aparecem na área central, com cartões e ações explícitas.

O painel direito pode ser recolhido por **Recolher**, pela alça **›** na borda ou por **Recolher painel** na barra da mesa. **Ferramentas ‹** reabre a ferramenta do contexto. Não é preciso manter o painel aberto para continuar lendo.

### Testar o ciclo da página 4 sem sair do Estúdio

1. Abra a fonte existente. Na barra da mesa, clique **Vincular coleção**. Há também esse acesso no cartão da fonte na seção Fontes.
2. Se a coleção ainda não existe, clique **Criar coleção ou subcoleção**. Preencha nome e identificador, escolha nenhuma coleção principal para criar uma raiz (ou escolha uma principal para criar uma subcoleção). Revise e confirme. A interface retorna à fonte com a coleção criada selecionada. O rascunho dos campos da classificação é conservado em memória durante essa ida e volta.
3. Confira título, coleção, subcoleção e idioma. Use **Revisar vínculo à coleção** e **Confirmar vínculo local** no rodapé. Isso classifica a fonte e mantém o PDF/revisões, sem criar um texto novo.
4. Confira a página com o fac-símile e salve-a como **Conferida**, se ainda estiver pendente. Clique **Criar documento** na barra da mesa. Selecione páginas **4**, revise título, ID, idioma e coleção. A prévia exige páginas já conferidas. Confirme para criar o documento local com o vínculo de proveniência.
5. Use **Abrir documento criado**. No Acervo, **Vincular a coleção** permite adicionar outros vínculos sem remover os anteriores ou alterar o conteúdo. Essa operação de catálogo é feita fora do contexto privado de projeto.
6. Alternativamente, use o botão **Coleções**, no topo ou na lateral, para ver coleções, abrir seus documentos e criar coleções/subcoleções. O acervo tem busca e paginação na área central.

Criar coleção, classificar fonte, adicionar vínculo de documento e incorporar transcrição são confirmações separadas. A interface agora oferece esses caminhos, mas não grava automaticamente apenas porque um destino foi selecionado. Os endpoints e seus históricos recuperáveis são os existentes. URLs e textos não são renomeados por essas operações.

Verificações desta etapa: sintaxe/IDs/referências; simulação da classificação de fonte preservando referência e idioma; simulação de adição de coleção preservando associações e sem envio de alterações textuais. Não houve gravação no backend real, criação de coleção de teste, upload ou teste de navegador. Reiniciar o backend e usar Ctrl+Shift+R para liberar o módulo novo. Sem commit ou push.
