# Organização dos estilos

As entradas públicas continuam sendo `assets/style.css` e `assets/editorial.css`. Elas importam CSS local nativo; não há npm, pré-processador ou etapa de build. Os caminhos relativos funcionam tanto no backend quanto no GitHub Pages.

## Leitor

Ordem declarada em `style.css`:

0. `tokens.css`: identidade e variáveis compartilhadas com a editoria.
1. `site.css`: tema, reset, navegação superior, estrutura e coleções.
   `portal.css`: composição da home, contagens e registros de incorporação.
2. `catalog.css`: listas, datas, paginação, navegação sequencial e busca.
3. `reader.css`: cabeçalho do documento, Markdown, estudo e marcador de parágrafo.
4. `reader-panel.css`: painel de controle, idiomas, menus, índice, retomada e estados recolhido/fixado.
5. `study-editor.css`: janela de correção de tradução e suas ações.
6. `workbench.css`: abas reais, instrumentos e integração da bancada com o leitor.

## Área editorial

Ordem declarada em `editorial.css`:

0. `tokens.css`: identidade compartilhada.
1. `editorial-base.css`: tema, links, botões, mensagens e estados ocultos.
2. `editorial-layout.css`: cabeçalho, lateral, catálogo e listas de coleções.
3. `editorial-forms.css`: campos, associações, pendências e estados de formulário.
4. `editorial-preview.css`: prévias, diferenças, Markdown, importações e lotes.

As duas páginas têm entradas independentes. Não se carrega o CSS editorial no leitor nem o inverso. Ambas importam `tokens.css` para compartilhar paleta, tipografia, superfícies e foco; os componentes continuam separados.

## Manutenção

- Alterar o componente responsável, sem acrescentar um novo bloco de correções no final das entradas.
- Manter a regra base, estados (`:hover`, `.active`, `[open]`, `[aria-pressed]`) e responsividade no mesmo arquivo.
- Não mover o índice de volta para a navbar nem recriar as versões antigas dos menus. O painel é o único dono desses controles.
- `[hidden]` é a regra de visibilidade compartilhada; as classes `.hidden` das colunas de estudo continuam com escopo próprio.
- `--site-header-height` e `--reader-panel-height` são calculadas pelo leitor. O CSS usa as duas para o espaço dos destinos de navegação; não adicionar deslocamentos fixos independentes.
- Observar o painel inteiro com um `ResizeObserver`, desconectado ao sair do documento; não acrescentar observadores por menu.
- Reservar estilos inline para dados de apresentação específicos, como cor/capa de coleção e ordem das colunas. Estilos estáticos pertencem a estes arquivos.
- Ao alterar uma versão visual, atualizar as consultas `?v=` das entradas HTML e dos imports CSS para não misturar arquivos em cache.

A interface oficial é `carmim-1`, aprovada pelo responsável em 19 de outubro de 2026 para portal, leitor, bancada e editoria. Os próximos ajustes devem partir dessa identidade e organização. O histórico de `workspace-3` está em `docs/projeto/INTERFACE-ARQUIVO.md`; a referência mais antiga era `stable-week-1`. Não foi criado um build, uma tag Git ou um mecanismo de publicação. O registro da aprovação e o roteiro manual estão em `docs/projeto/PORTAL-BANCADA-CARMIM.md`.
