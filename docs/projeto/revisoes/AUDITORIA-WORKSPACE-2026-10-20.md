# Auditoria do workspace — descobertas antes de correções

20/10/2026. Solicitada pelo pesquisador para testar a entrega e apresentar problemas antes de modificar a implementação. Nenhuma correção aplicada; não houve commit ou push.

## Método e alcance

- Executados os 23 testes existentes de `tests/test_backend.py`, com fixtures temporárias: **23 passaram**.
- Executados 16 cenários adicionais por HTTP contra servidores locais temporários, usando documentos fictícios e bancos isolados: **16 passaram**.
- Os 14 arquivos JavaScript próprios em `assets/` passaram pela análise sintática em QuickJS.
- Executados cenários de lógica cliente em JavaScript real, com DOM, rede, armazenamento e renderização simulados: fluxo de gravação privada aprovado, três falhas reproduzidas.
- Inspeção dos links confirmou que documentos da página de projeto não usam mais `target=_blank` e levam o ID explícito de projeto.

Não foi usado o backend real do pesquisador, nem alterados seus documentos, projetos ou bancos. Os testes adicionais e resultados ficam em `/tmp/`; somente este relatório foi acrescentado ao repositório.

O ambiente não oferece navegador/Node instalado. Foi instalado QuickJS exclusivamente em `/tmp/workspace-audit-tools`, sem alterar dependências do projeto. Os testes de interface não equivalem a uma sessão em Chrome/Firefox: não validam CSS, responsividade, foco, seleção real de texto, download nativo, visualizador PDF ou geometria de rolagem. Renderização Markdown foi substituída por stub nos testes de interação. A inspeção visual continua pendente.

A sandbox inicialmente impediu sockets e download; as execuções necessárias foram repetidas com permissão ampliada. Essas falhas iniciais eram do ambiente e não foram contadas como defeitos do aplicativo.

## O que funcionou nos testes executados

1. Gravar no projeto não modificou bytes dos originais, catálogo ou manifesto da fixture.
2. Dois projetos conservaram versões diferentes do mesmo documento/idioma.
3. Versões de trabalho persistiram após reiniciar o backend temporário.
4. Histórico restaurou o estado anterior à primeira gravação sem apagar a edição principal e mantendo revisão monotônica.
5. Uma prévia de versão de trabalho ficou inválida após outra gravação na mesma versão.
6. Incorporação recusou a ausência de confirmação explícita; uma prévia de incorporação foi bloqueada no endpoint editorial comum.
7. Alterações posteriores no acervo ou na versão do projeto impediram incorporações desatualizadas.
8. Tradução nova permaneceu privada até a incorporação.
9. A importação sinalizou divergências de identidade e removeu o envelope reconhecido do corpo.
10. Projeto arquivado e documento não vinculado recusaram gravações indevidas.
11. Editar diretamente o acervo preservou a versão de trabalho; a incorporação posterior avisou sobre a alteração da origem.
12. A incorporação atualizou busca e histórico editorial, registrando a origem no projeto.
13. Restaurar uma versão de projeto não desfez uma incorporação já realizada no acervo.
14. No teste cliente, o botão de salvar no projeto chamou `/api/editorial/workspace/save`, sem chamar a gravação canônica.

Esses resultados não são garantia de ausência de outros defeitos.

## Falhas reproduzidas

### A. Marcador de leitura compartilhado entre projetos e acervo

**Prioridade: alta para a consistência do workspace.**

Código: `assets/app.js:904`, `assets/app.js:1033` e `assets/app.js:1035`.

O registro usa `readingProgress:v1:ID_DO_DOCUMENTO`, sem identificar o projeto. No teste, marcamos um parágrafo no projeto A, passamos ao projeto B e marcamos o mesmo parágrafo. A segunda ação interpretou o registro de A como uma marca já existente e o removeu.

Consequência: a indicação e a retomada podem interferir entre projetos e leitura do acervo. Não houve alteração de texto, mas o isolamento de navegação está incompleto. Preferências de idioma e colunas também usam chaves por documento e devem ser avaliadas na mesma correção; não foram classificadas como falhas reproduzidas independentes.

**Correção proposta, ainda não aplicada:** definir uma chave comum de contexto para marcas/retomada, distinguindo acervo e cada projeto, com tratamento compatível das marcas antigas.

### B. Atalho geral da bancada pode esquecer ou trocar o workspace

**Prioridade: alta para navegação previsível.**

Código: `assets/workbench.js:19`–`22`.

O último documento é guardado sem o projeto; a recuperação procura a primeira aba com aquele ID. No cenário executado, o documento existia em abas dos projetos A e B, sendo B o contexto mais recente:

- Antes de inicializar as abas, `defaultURL()` retornou o documento sem projeto.
- Depois da inicialização, retornou a aba do projeto A, não a de B.

Consequência: um acesso geral à bancada pode levar ao acervo ou a outro projeto, apesar de o documento parecer o mesmo. A indicação de contexto continua visível, mas a retomada não é confiável.

**Correção proposta, ainda não aplicada:** persistir e recuperar o endereço completo do último workspace/documento, usando também o projeto como identidade da aba.

### C. Uma falha do histórico remove o editor inteiro

**Prioridade: média, aumenta em caso de instabilidade local.**

Código: `assets/project-editor.js:82`–`86`.

O histórico é carregado depois que o editor já foi montado, mas dentro do mesmo bloco de tratamento de falhas. No teste com falha simulada apenas da requisição de histórico, a área funcional de edição foi substituída pela mensagem de erro: não restou textarea acessível.

Consequência: uma função auxiliar indisponível impede a edição mesmo quando a versão textual foi carregada. Não constatamos perda de versão salva nesse cenário.

**Correção proposta, ainda não aplicada:** separar os estados e erros de documento, editor e histórico; mostrar aviso e opção de tentar novamente apenas na seção afetada.

## Incompletudes de UX identificadas por inspeção

Estas não foram validadas visualmente em navegador:

- PDFs, configurações e gerenciamento de projetos ainda navegam para páginas editoriais completas. Permanecem na mesma guia, mas deixam a bancada. Ainda não são instrumentos abertos como abas internas de um workspace.
- O projeto explícito da URL e o projeto preferido no backend podem ser diferentes ao abrir um link diretamente. Os destinos explícitos evitam gravação silenciosa no outro projeto, mas a apresentação precisa deixar essa distinção compreensível ou unificar o conceito de forma deliberada.
- As versões de trabalho não salvas permanecem em memória; há aviso ao sair, mas ainda falta uma indicação persistente, como um ponto na aba, para identificar os buffers pendentes sem abrir cada editor.

## Sequência recomendada, sujeita à avaliação do pesquisador

1. Corrigir os identificadores de contexto e a retomada da bancada (A e B).
2. Isolar falhas auxiliares do editor (C).
3. Conferir visualmente lateral, abas, foco, rolagem e tamanhos de tela em navegador.
4. Evoluir os instrumentos editoriais para abas internas antes de multiplicar ferramentas na bancada.

Não aplicar essas mudanças antes de apresentar as descobertas e receber o direcionamento do pesquisador.

## Evidências da execução

- Regressão: `/tmp/workspace-backend-regression.log`.
- Cenários HTTP adicionais: `/tmp/test_workspace_audit.py` e `/tmp/workspace-audit-results.log`.
- Cenários JavaScript: `/tmp/workspace-js-audit.py` e `/tmp/workspace-js-audit-results.json`.

Arquivos em `/tmp/` são temporários. O resumo dos resultados e as reproduções essenciais estão preservados neste relatório.

## Correções autorizadas e verificadas

Após a apresentação desta auditoria, o pesquisador autorizou corrigir as três falhas e definiu: **o acesso inicial e o recarregamento do site começam sem projeto ativo**. A revisão visual foi adiada explicitamente.

- **A corrigida:** marcas usam chave por projeto/documento, separada da marca do acervo. As marcas antigas sem contexto são preservadas somente na leitura do acervo, com migração ao serem consultadas; não são distribuídas entre projetos. Desmarcar não ressuscita uma marca antiga remanescente.
- **B corrigida conforme a nova decisão:** o atalho geral da bancada não recupera um projeto de uma aba antiga. F5 remove o contexto de projeto da URL, preserva documento/idioma e limpa o projeto preferido no backend local. Entrar por um link explícito de projeto continua abrindo aquele workspace. Navegação deliberada por Voltar/Avançar não é tratada como F5. O reset não apaga projetos, versões, abas guardadas ou histórico.
- **C corrigida:** falhas do histórico ficam na seção de histórico, com botão de tentar novamente; o editor e seu texto não são substituídos. A nova tentativa conserva o buffer em edição.

Verificação dirigida: **16 cenários de comportamento e 14 análises sintáticas, todos aprovados**. Reutilizado QuickJS temporário com DOM/rede simulados; nenhuma instalação adicional, servidor real do pesquisador ou banco operacional real foi usado nesta verificação. A suíte de backend anterior não foi reexecutada: não houve mudança no backend nesta correção. Não houve alteração visual, commit ou push.

### Conferência manual após as correções

1. Recarregue o site, preferencialmente com Ctrl+Shift+R para obter os scripts atualizados. Se estava em um documento de projeto, ele deve abrir no contexto do acervo; o seletor mostra **Acervo · sem projeto**. Na área editorial, o seletor começa **Sem projeto ativo**.
2. Escolha explicitamente um projeto e abra um documento. Ele deve entrar no workspace normalmente, sem novas guias automáticas.
3. Marque um parágrafo no projeto A; marque outro no projeto B e confira também a leitura sem projeto. Cada contexto deve conservar sua própria marca. Desmarcar em B não remove a marca de A.
4. Saia para a home e use o acesso geral à bancada: ele não deve selecionar um projeto por coincidência de documento. Voltar ao projeto deve ser uma escolha explícita.
5. Para a falha de histórico, o cenário foi reproduzido automaticamente com rede simulada. A interface agora informa indisponibilidade apenas na seção afetada e oferece nova tentativa, mantendo o editor.

A integração de ferramentas como abas internas e a avaliação visual continuam pendentes. Resultados detalhados da verificação atual estão em `/tmp/workspace-js-corrections-results.json`; a lógica essencial e o resultado agregado foram registrados aqui para continuidade.
