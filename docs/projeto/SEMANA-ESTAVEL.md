# Base visual stable-week-1 — semana de uso prático

## Escopo da rodada

Consolidação do CSS do leitor e da área editorial, preservando a organização aprovada: painel recolhido acima do cabeçalho do documento, fixação opcional, menus internos em listas, índice/marcador no painel, navegação sequencial no fim do documento, cartões com capa inteira, formulários e ações editoriais na paleta atual.

O código anterior está no commit `0d61f4f`. Esta rodada não fez commit, push, publicação ou alterações no acervo. Não foram executados testes, navegador automatizado, servidor de demonstração, compilação ou captura de tela pelo assistente. A comparação visual e a validação de funcionamento serão feitas no uso prático pelo responsável.

## O que mudou

- `assets/style.css` e `assets/editorial.css` são entradas pequenas, com importações CSS locais explícitas. Não é necessário npm ou build.
- As regras estão organizadas por componente em `assets/css/`, com uma declaração por linha, fontes centralizadas e responsividade junto ao componente.
- Foram removidas as regras das versões antigas do painel, índice na navbar, menus flutuantes, modo de navegação sequencial no início e seletores abandonados de edição.
- O painel mantém apenas um controlador de abertura de menus e um observador de tamanho. O observador é desconectado ao trocar de documento ou sair do leitor.
- A altura da navbar e do painel fixado é usada pelo CSS, pelo salto do índice, pela retomada e pela captura do contexto editorial. O painel é medido novamente ao expandir/recolher ou abrir um menu.
- A animação de padding dos blocos de estudo foi removida, evitando movimento de texto durante mudanças de disposição; o realce de fundo e sombra foi mantido.
- O rótulo do botão de fixação acompanha seu estado já na abertura da página.
- Cliques e Escape em uma janela de correção não fecham menus atrás dela.
- Botões e links de ação nas linhas editoriais ficam com a mesma altura mínima no celular. Foram preservados os controles, tamanhos gerais, cores e conteúdo das telas.
- Mensagens de erro do leitor usam uma classe CSS, em vez de estilos estáticos dentro do JavaScript.

A limpeza não altera a segmentação dos textos, o pareamento de estudo, as APIs de gravação, o histórico, os arquivos, traduções, IDs ou URLs dos documentos. Fontes e imagens existentes foram mantidas.

## Começar a usar

Se o backend já está aberto, pode mantê-lo: esta rodada modifica arquivos estáticos. Caso precise iniciar:

```bash
python3 -m backend
```

Abra http://localhost:8000/ e http://localhost:8000/editorial. Recarregue **as duas páginas** com Ctrl+Shift+R para carregar a versão `stable-week-1`. Não há migração de dados a executar.

Antes de começar a semana, guarde uma cópia do projeto com o backend parado, incluindo a pasta oculta `.local`. O histórico recuperável fica em `.local/editorial/history/`, fora do Git. Uma cópia só dos arquivos versionados não inclui esse histórico.

## Conferência rápida inicial

1. Abra um documento antigo com traduções, como `/#/doc/showtrials-1666`.
2. Confira o painel recolhido acima do título. Expanda, abra as opções e confira se apenas um menu permanece aberto. Fixe, role e recolha.
3. No meio do documento, alterne leitura/estudo e parágrafo/paralelo. Confira o ponto de leitura, as colunas e a possibilidade de continuar usando o painel.
4. Abra o índice, salte para uma seção, marque um parágrafo e use Retomar com o painel recolhido. Confira se o destino está visível abaixo dos controles fixados.
5. Abra Corrigir tradução, digite algo e cancele. Confira a janela, o foco e o descarte. Não é necessário salvar para conferir o CSS.
6. Use Editar para entrar na área editorial. Abra metadados, editor Markdown, novo documento, coleções, importação e lote. Confira campos, botões, prévias e barra lateral.
7. Confira uma lista paginada e seus links anterior/próximo, uma busca e uma coleção com capa.
8. Repita os pontos usados com mais frequência em tela estreita. O painel conserva suas três áreas; no celular elas se empilham e as opções internas se distribuem em duas colunas quando há espaço.

## Durante a semana

Use os fluxos normais do trabalho: ler, comparar idiomas, corrigir, importar e cadastrar. Os roteiros detalhados de gravação/restauração continuam em CADASTRO-LOCAL.md, IMPORTACAO-EM-LOTE.md e CORRECOES-NO-ESTUDO.md.

Nesta semana, o objetivo é recolher problemas reais de uso e fazer correções pontuais quando necessárias, evitando novas reformulações visuais ou funcionalidades que dificultem identificar regressões.

Para cada problema, anote:

| Informação | Exemplo |
| --- | --- |
| Endereço e documento | URL copiada da barra do navegador |
| Tela/dispositivo | Desktop ou celular; navegador usado |
| Ação | Abri Estudo → Paralelo com o painel fixado |
| Resultado esperado | Continuar no mesmo parágrafo |
| Resultado observado | O parágrafo ficou escondido pela barra |
| Frequência | Sempre, às vezes, apenas neste documento |
| Prioridade | Impede salvar, atrapalha leitura ou detalhe visual |

Não é necessário conhecer nomes técnicos dos controles. Descrever a sequência de cliques e o que apareceu já permite investigar.

## Limites mantidos

A gravação continua somente local; publicação exige uma ação separada de commit/push. Importação em lote continua para originais novos, e capas usam imagens existentes em assets/covers/. O histórico continua baseado em snapshots e pode exigir desfazer operações mais recentes antes de uma antiga. Essas funcionalidades não foram ampliadas nesta consolidação.
