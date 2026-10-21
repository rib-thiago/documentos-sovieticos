# Protótipo — portal, leitor e bancada de pesquisa

**Referência de desenvolvimento.** A interface Carmim foi incorporada ao site principal e aprovada como oficial em 19 de outubro de 2026. Use `/` para a interface adotada; esta pasta conserva o protótipo e suas limitações, não uma versão alternativa oficial. Veja [o registro da aprovação](../docs/projeto/PORTAL-BANCADA-CARMIM.md).

Versão `portal-workbench-3`. Prévia isolada da aplicação atual, com a direção Carmim escolhida pelo responsável. A referência ao Replit passa a orientar documentos em abas e instrumentos contextuais, sem impor essa organização à leitura pública.

## Acessar

Com o servidor do projeto aberto:

- **Portal:** http://localhost:8000/prototipo/
- **Leitor público:** http://localhost:8000/prototipo/#/documento/showtrials-1665?colecao=centro-de-leningrado
- **Bancada:** http://localhost:8000/prototipo/#/trabalho/showtrials-1665?colecao=centro-de-leningrado

Recarregue com Ctrl+Shift+R. Esta revisão usa os mesmos três arquivos já autorizados no backend, sem nova mudança nas rotas Python. Se ainda estiver usando o backend anterior à autorização de `/prototipo/`, encerre com Ctrl+C e execute novamente `python3 -m backend`. `python3 -m http.server 8000` também serve a prévia. Não abra o HTML diretamente pelo gerenciador de arquivos.

O site atual continua em `/`. Nenhum documento, tradução, cadastro, histórico editorial ou URL existente foi modificado.

## Três experiências distintas

### Portal

Página inicial com apresentação, busca, coleção em destaque, dados do catálogo, versões incorporadas, fontes incorporadas, entrada para a bancada e coleções. Sem navegação lateral ou faixa de ícones duplicando o cabeçalho.

As contagens vêm do manifesto carregado: documentos únicos, coleções, documentos com português e versões linguísticas. Não são somas de ocorrências nas coleções.

As novidades são um **recorte demonstrativo do histórico Git local**, incorporado ao HTML: adição de arquivos em 25 commits com entradas, da qual 18 operações correspondem a versões do manifesto atual. A lista mostra exemplos dessas operações, não todas as alterações. Datas são de registro do commit, não datas históricas nem confirmação de publicação online. Inclusões não commitadas não entram nesse recorte. O bloco de fontes reúne exemplos de adições de versões russas; não afirma que sejam originais arquivísticos.

Essa fotografia não se atualiza automaticamente ao importar uma tradução. Para a implementação definitiva, o catálogo precisa registrar eventos próprios de incorporação e publicação, mantendo-os separados das datas históricas. Não inferir essas datas a partir do WordPress ou da ordem do manifesto.

### Leitor público

Texto em primeiro plano, largura confortável e ferramentas recolhidas. Mantém barra fixável, idiomas, marcador por clique, retomada, estudo com traduções expansíveis e paralelo com blocos numerados. Identificações e ações ficam discretas na leitura contínua, sem perder acesso por teclado.

“Abrir na bancada” leva o mesmo documento para a experiência de trabalho. A ficha editorial demonstrativa continua acessível.

### Bancada de pesquisa

- Abas correspondem a **documentos reais**, não a links repetidos de navegação global.
- **＋** ou **Abrir documento** pesquisa títulos/IDs e acrescenta uma aba. A seleção mostra até 30 resultados, com contagem total.
- Alternar abas conserva idioma, modo, posição aproximada e instrumento escolhido por documento enquanto a página permanece aberta.
- Fechar uma aba retira o documento da bancada. Se houver rascunho de Markdown ou nota, a interface confirma seu descarte antes de fechar.
- Lateral contém apenas instrumentos do documento ativo: **Markdown e prévia**, **Índice**, **Ficha documental** e **Notas de trabalho**. Não repete o catálogo completo nem os links do cabeçalho.
- Painel à direita acompanha a aba ativa. Markdown e Prévia alternam o código e sua renderização; o leitor à esquerda continua exibindo a versão preservada. É possível escolher outro idioma no painel.
- Rascunhos de Markdown são separados por documento e idioma. Não modificam arquivos nem o leitor à esquerda. A prévia usa o mesmo separador de cabeçalhos e o sanitizador existentes.
- Notas de trabalho são rascunhos por documento, sem publicação ou alteração na fonte.
- Índice usa os títulos da versão principal visível e oferece atualização após mudar idioma/modo. Não inventa títulos.
- No celular, painéis são empilhados; lateral pode ser recolhida para preservar a área de trabalho.

## Roteiro manual sugerido

1. Abra o portal e observe a hierarquia entre busca, novidades, dados e coleções. Abra uma novidade para conferir o texto real. Datas de incorporação e datas dos documentos têm funções distintas.
2. No leitor do 1665, fixe a barra e role. Marque um trecho clicando nele ou na bolinha. Alterne Leitura, Estudo por trecho e Paralelo; confira retomada e expansões.
3. Clique em **Abrir na bancada**. No painel lateral, selecione **Markdown e prévia**. Altere uma palavra no rascunho e abra **Prévia**: a alteração aparece à direita, enquanto o texto preservado à esquerda permanece igual.
4. Clique no **＋** das abas, procure `1666` e abra. Volte à aba do 1665: o rascunho, idioma, modo e instrumento devem continuar associados ao documento certo.
5. No 1665, abra **Notas de trabalho** e digite uma observação. Alterne abas e volte; a nota deve continuar nesse documento. Confira Ficha e Índice.
6. Feche uma aba sem rascunho e outra com rascunho: a segunda pede confirmação antes de descartá-lo. Recarregar a página também pode pedir confirmação se existirem rascunhos.
7. Volte ao leitor público e depois à home. As barras de abas e instrumentos pertencem à bancada e não devem acompanhar essas páginas.
8. Confira no celular e com Tab: menus, abas, fechamento de documento, seleção, marcador e painéis.

## Persistência e limites

- **Acervo:** somente leitura. Não há chamadas de gravação nem importação.
- **Rascunhos e notas:** somente memória da página; sobrevivem à alternância de abas internas, não ao recarregamento. A interface informa essa condição e solicita confirmação de saída quando há rascunhos.
- **Abas abertas:** IDs/contextos guardados na sessão, sem os rascunhos. Podem reaparecer após recarregar, mas seus textos voltam aos arquivos preservados.
- **Marcadores, idioma, fixação e recolhimento dos instrumentos:** usam `sessionStorage` com prefixo `prototype:`, independente das preferências do site atual.
- **Posição:** aproximada e em memória. A troca de modo procura conservar o bloco visível.
- **Comparação:** pareamento por posição de blocos estruturais, sem alinhamento confirmado. Numeração provisória, não uma âncora bibliográfica permanente.
- **Editor de trecho, ficha editorial e histórico:** demonstrações; sem salvar ou restaurar versões reais. As ferramentas de produção continuam na área editorial atual.
- **Pessoas e episódios:** proposta ainda não implementada; nenhuma relação histórica fictícia é exibida.

## Registro técnico

Arquivos `index.html`, `prototype.css` e `prototype.js`, com autorização dos três em `backend/server.py` já preparada na primeira correção de acesso. O recorte de atividades está em JSON não executável no próprio HTML, sem acesso a `.local/` ou exposição do histórico editorial privado.

CSS reorganizado para distinguir portal, leitor e bancada, com Carmim, curvas mais suaves e componentes compartilhados. Sem dependências novas; renderizador Markdown, notas, sanitizador e separador de cabeçalhos reutilizados. Metadados são escapados e conteúdo renderizado é sanitizado.

Não foram executados testes, servidor, navegador, lint ou compilação. Avaliação visual e funcional em execução permanece manual. Sem commit ou push.

## Novo estudo de workspace IDE — 20/10/2026

O protótipo específico para reorganizar o trabalho editorial como IDE está em [`ide/`](ide/README.md), acessível em `/prototipo/ide/`. Ele tem grupos de abas, instrumentos documentais móveis e acesso aos fluxos locais existentes. Não substitui esta referência anterior nem a interface oficial. Veja o [diagnóstico e a proposta](../docs/projeto/WORKSPACE-IDE-DIAGNOSTICO.md).
