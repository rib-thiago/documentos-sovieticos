# Reparação da navegação e apresentação editorial — 21/10/2026

## Decisão

A bancada de pesquisa existente não será substituída nem fundida compulsoriamente
com os formulários editoriais. A adaptação pedida é de layout e linguagem visual.
A home continua sendo a entrada pública.

- **Bancada de pesquisa:** documentos em abas, novos documentos pelo botão +,
  Markdown e prévia, índice, ficha, notas de trabalho, instrumentos laterais,
  estudos paralelos, fac-símiles e contexto de projeto.
- **Área editorial:** catálogo, cadastro de documentos e coleções/subcoleções,
  importação de traduções, revisão, histórico e ferramentas PDF/OCR. Seus fluxos
  completos continuam funcionando diretamente no ambiente editorial.
- **Editar** no leitor mantém o fluxo editorial contextual anterior; **Bancada**
  abre o ambiente de pesquisa sobre aquele documento. São ações diferentes.

## O que foi reparado

A comparação com o commit `3cf03d4` identificou redirecionamentos no leitor,
no gerador de links da bancada, nos projetos e no servidor. Esses desvios
encaminhavam os usuários à interface substituta. Foram retirados, restabelecendo
os componentes anteriores, sem alterar o acervo.

O servidor volta a servir os formulários completos em `/editorial`. O JavaScript
editorial não exige mais estar dentro de um iframe. `/prototipo/ide/` permanece
acessível no endereço original, para comparação, sem substituir a bancada ou a
área editorial. Os arquivos da tentativa de fusão foram guardados fora da árvore
ativa em `/tmp/documentos-interface-antes-reparacao-20261021`; esse backup é
provisório e não deve ser tratado como histórico permanente.

A área editorial recebe estrutura própria, com a paleta Carmim e as dimensões da
IDE: barra de atividades, navegação lateral com largura ajustável, recolhimento,
barra de tarefas recentes e rodapé compacto. Não há nova camada de iframes.
Os atalhos de tarefas recentes reabrem as rotas existentes; não mantêm múltiplos
formulários não salvos em memória e não substituem as abas de textos da bancada.
As proteções de saída sem salvar, prévia e histórico permanecem no roteador original.

## Dados preservados

Nenhuma gravação de catálogo, documento, tradução, projeto, PDF ou histórico foi
realizada nesta reparação. As alterações de dados da incorporação anterior e os
arquivos cadastrados pelo pesquisador permanecem no diretório de trabalho.
Nenhum armazenamento de sessão ou rascunho da bancada foi apagado.

## Como conferir

1. Encerrar e reiniciar `python3 -m backend`, pois a rota de `/editorial` mudou.
2. Abrir `http://localhost:8000/` e atualizar com Ctrl+Shift+R.
3. Abrir um documento e clicar em **Bancada**. Abrir outro texto com **+**;
   alternar entre abas e consultar Markdown, índice, ficha e notas laterais.
4. Abrir **Área editorial** na navegação. Confirmar que catálogo, novo documento,
   coleções, importação de tradução e fontes PDF estão na lateral.
5. Arrastar a divisória da lateral; recolhê-la pelo botão existente. Ctrl+B também
   recolhe, quando o foco estiver fora de campos de edição.
6. Navegar por catálogo, coleções e tradução; usar os atalhos recentes no alto.
   Se houver alteração não salva, cancelar a saída deve manter a edição atual.
7. Localizar a coleção e as duas subcoleções criadas pelo pesquisador; conferir
   seus documentos e versões. Não é necessário salvar nada para essa inspeção.
8. Abrir um PDF existente e conferir OCR, revisão e altura ajustável da comparação.
9. Pelo leitor, acessar **Editar** e conferir documento, idioma e retorno à leitura.

A reparação foi conferida por inspeção e checagem sintática, sem executar suítes
ou testes no navegador. Sem commit ou push. A apresentação visual aguarda a
conferência manual do pesquisador; não é declarada validada por este registro.

## Código

- `assets/workbench.js` e `assets/app.js`: bancada anterior, sem redirecionamento.
- `backend/editorial.html`: estrutura completa da área editorial.
- `assets/editorial-shell.js` e `assets/css/editorial-shell.css`: adaptação visual
  e navegação auxiliar, sem persistência de documentos.
- `assets/editorial.js`: fluxos e proteção de alterações existentes.
- `assets/workspace-pdf-layout.js`: disposição de revisão/OCR preservada.

Evoluções futuras de integração devem partir dessas capacidades, com comparação
explícita de recursos, em vez de substituir os ambientes por uma versão reduzida.

## Refinamento das tarefas editoriais

O catálogo e a fila passam a usar uma barra de busca, com filtros recolhíveis e
indicação de quantos filtros estão ativos. Os resultados apresentam ações de
revisão/ficha, importação de tradução e abertura na bancada.

Coleções são exploradas em uma árvore expansível, com busca por título ou ID da
coleção e de suas subcoleções. Cada nível oferece ações para editar, cadastrar
um documento e consultar os documentos associados. Os acessos a projeto, site e
criação de subcoleções foram preservados.

O editor de coleção separa identificação, apresentação e fonte em seções. A ficha
do documento separa metadados, associações e pendências. Trocar de seção conserva
os valores; **Revisar** reúne todas as seções na mesma prévia de confirmação. Se
um campo obrigatório estiver em outra seção, a validação abre essa seção. Links
da fila com pendência específica abrem diretamente a seção de pendências.

Conferência manual adicional (sem necessidade de salvar):

1. Buscar um documento no catálogo; abrir filtros e restringir por coleção.
2. Filtrar a fila por prioridade/status e abrir uma pendência: a seção de
   pendências deve estar selecionada.
3. Buscar uma subcoleção pelo nome em Coleções; expandir a coleção e conferir
   os atalhos para documentos e edição.
4. Criar uma coleção ou subcoleção de exemplo, trocar entre as três seções,
   preencher os dados e gerar a prévia. Cancelar sem salvar conserva o acervo.
5. Na ficha de um documento, alterar um valor e alternar entre seções; conferir
   que o valor permanece e que a prévia reúne as alterações.

Sem mudanças na API ou no modelo dos dados. Checagem sintática JavaScript
concluída; não foram executados testes no navegador nem commit ou push.

## Aplicação sistemática e fechamento de tarefas

Os componentes comuns em `assets/editorial-tasks.js` organizam campos em seções
sem criar novos formulários nem modificar os payloads do backend. A mesma área
de seleção de arquivos é usada em documentos, lotes, traduções e PDFs.

- Novo documento: Arquivo, Identificação, Destino e Proveniência.
- Lote: Arquivos, Destino padrão e Guia da planilha.
- PDF: listagem com busca e filtro por estado; envio com Arquivo e Destino.
- Importar tradução: seleção compacta do documento e área comum de upload.
- Histórico e demais formulários recebem os controles e superfícies compactos.
- Revisão de páginas e OCR preservam seu layout de trabalho já existente.

Cada tarefa da barra tem botão × e a barra oferece Fechar todas. Fechar a tarefa
ativa com alterações pede confirmação; cancelar mantém a tarefa e seus dados.
Durante uma gravação, o fechamento da tarefa ativa ou de todas é bloqueado. Fechar
uma tarefa inativa não interfere na edição atual. Fechar a última deixa a área
central vazia, com acessos para começar outra tarefa. As tarefas não são mais
removidas automaticamente ao atingir oito atalhos. Elas continuam usando um único
formulário ativo: não prometem guardar edições não salvas ao trocar de tarefa.
A bancada de documentos mantém seu mecanismo de abas independente e preservado.

Conferência adicional:

1. Em Novo documento, escolher um arquivo, preencher identificação, selecionar
   destino e proveniência. Gerar prévia e cancelar sem salvar para conferir o fluxo.
2. Em Lote, selecionar CSV e arquivos; alternar para Destino e Guia, voltar e
   conferir os arquivos selecionados. Gerar prévia apenas com um lote desejado.
3. Em Fontes PDF, buscar por nome/ID e filtrar estado. No envio, escolher PDF,
   alternar destino e voltar: o arquivo deve continuar selecionado.
4. Abrir algumas tarefas e fechar uma inativa. Na ativa, alterar um campo e
   clicar ×: cancelar a confirmação deve conservar a aba e a alteração.
5. Fechar todas; confirmar a saída quando desejado. A área central deve apresentar
   o início editorial, sem reabrir compulsoriamente a fila.

Não foram executados testes de navegador ou suítes nesta entrega; foram feitas
checagens sintáticas. Nenhum acervo, projeto ou PDF foi modificado pela implementação.
