# Revisão/OCR com espaço de trabalho contínuo

26/10/2026. Ajuste após o piloto Zinoviev. O responsável conseguiu extrair e editar uma página, mas relatou pouco espaço, rolagens aninhadas e excesso de trocas de seção.

## Alterações

- **Concentrar:** botão da tarefa e do rodapé da bancada. Oculta cabeçalho público, explorador lateral e comandos superiores, mantendo abas e tarefa ativa. **Restaurar painéis** permanece no rodapé; Escape também restaura o ambiente. Não fecha abas nem descarta edições.
- **Recolher comandos:** reduz a barra superior à identificação e ao controle de expansão. A lateral mantém seu botão existente. O inspetor contextual das tarefas também pode ser recolhido por **Contexto**; na revisão PDF ele já fica oculto.
- **Uma revisão, um contexto:** configurar/acompanhar OCR abre um painel sobre a área da transcrição, com o fac-símile ao lado quando há largura suficiente. **Voltar à transcrição** ou **Página e transcrição** recolhe esse painel. Cadastro, vínculos, incorporação e disponibilização ficam agrupados em **Dados e publicação**.
- **Faixas menores:** navegação por página e escolha de disposição compartilham a mesma faixa. Proporção/altura ficam em **Ajustar espaço**, recolhido inicialmente. As ações sobre o arquivo ficam em **Ações da fonte**.
- **Transcrição e candidatos:** são as duas seções principais da página. Alinhamento, referências e histórico ficam em **Mais ferramentas**. Carregar um candidato retorna diretamente à transcrição e sincroniza o CodeMirror.
- **Rolagem delimitada:** altura automática considera o painel de abas disponível, inclusive em grupos divididos. A área editorial externa deixa de rolar durante a revisão; imagem e texto têm seus próprios controles. O OCR aberto tem uma única área rolável de configuração/andamento. A prévia de gravação ocupa a área da transcrição, sem alongar a tela inteira.
- **Reaproveitamento de abas:** o acesso à revisão de uma fonte já aberta ativa aquela aba e navega dentro dela, preservando a confirmação de alterações não salvas. Abrir novamente o BookReader de uma fonte cadastrada também reaproveita a aba correspondente.

O texto bruto, a transcrição salva, o rascunho de sessão, as prévias e o histórico permanecem nos fluxos existentes. Nenhuma gravação documental foi executada nesta alteração.

## Validar manualmente

1. Reinicie o backend, abra `/editorial` e use Ctrl+Shift+R. Abra a fonte usada no teste anterior e confira sua transcrição salva/rascunho.
2. Use **Concentrar**. Confira o ganho de espaço; restaure pelo rodapé e teste Escape. Experimente também **Recolher comandos**, a lateral e **Contexto** em outra tarefa.
3. Na fonte, alterne **Fac-símile / Comparar / Transcrição** e abra **Ajustar espaço**. A altura solicitada fica limitada à área disponível; a opção automática acompanha a janela. Em um painel estreito, abrir OCR prioriza a área textual para evitar dois retângulos inutilizáveis.
4. Clique **Gerar OCR**. Confira configuração e andamento sem sair da fonte. Recolha por **Voltar à transcrição**. Não é preciso executar novo lote para validar o layout.
5. Em uma página que já tenha candidato, abra **Candidatos OCR → Carregar este candidato no editor**. Confira a troca direta para Transcrição e a atualização do texto. Se houver rascunho, cancelar a confirmação deve preservá-lo.
6. Faça uma correção desejada, confira a prévia e salve. Verifique que a confirmação ocupa o painel textual e que o histórico continua acessível em **Mais ferramentas**.
7. Abra a mesma fonte pelo BookReader, escolha outra página e volte à revisão: deve reaproveitar a aba. Com uma edição não salva, cancelar a navegação deve manter a edição.
8. Confira também a revisão aberta no modo estudo: o layout compartilhado deve preservar seus controles, ainda que o botão de concentração pertença à bancada.

Conferidas sintaxe e referências estáticas. Testes de navegador ficam com o responsável. Sem testes de gravação, OCR adicional, commit ou push.

## Tratamento de imagem é uma ferramenta do projeto

A renderização interna do OCR não substitui as ferramentas de imagem. O fluxo previsto é:

**PDF/página original → derivado de imagem configurável → candidato OCR → transcrição revisada → tradução.**

O tratamento deve aparecer na própria tarefa da página, com prévia antes/depois e receita reaproveitável para um conjunto de páginas. ImageMagick deverá oferecer inicialmente resize/resolução, rotação, escala de cinza, threshold e operações morfológicas como erosão/dilatação. A ordem das operações e seus parâmetros precisam ser explícitos; nenhum filtro deve ser aplicado silenciosamente.

Cada derivado deve registrar fonte e hash, página física, receita, versão do motor e imagem produzida. O OCR deve registrar qual derivado e receita utilizou. Recortes, rotações e mudanças de escala exigem registrar a transformação para que caixas de palavras/parágrafos possam voltar às coordenadas da página original. Threshold e erosão exigem comparação porque podem apagar acentos, pontuação e traços; o original continua como referência de citação.

Estas operações **ainda não foram implementadas nesta rodada**. São a próxima camada de processamento, não foram descartadas nem substituídas pelo BookReader. A escolha de motor de tradução continua independente e não há configuração de serviço pago.


## Correção do travamento ao abrir Fontes

O retorno do responsável revelou um ciclo de MutationObserver: o layout reatribuía `textContent` ao link Fontes em todas as passagens. A escrita gerava uma nova mutação, que agendava o layout em uma microtarefa, mantendo o navegador ocupado. Corrigida a escrita para ocorrer somente quando o texto muda; o link também passa a ser movido uma única vez ao menu de ações. A visibilidade do painel OCR só é escrita quando muda.

O observador agora agrupa mudanças por quadro de renderização e fica desconectado enquanto o próprio layout ajusta o DOM, evitando observar as próprias alterações. Atualizada a versão do script para `desk-2` nas três entradas. Uma simulação focalizada do cabeçalho confirmou 20 mutações em 20 passagens repetidas antes da correção e nenhuma depois. Sintaxe conferida; não realizado teste de navegador nem upload/OCR adicional. Nenhum dado, fonte, rascunho ou histórico foi apagado. Validar recarregando com Ctrl+Shift+R e abrindo a fonte existente antes de tentar novo envio.
