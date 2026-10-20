# Aplicação da interface Carmim ao site

19 de outubro de 2026 — **interface oficial aprovada pelo responsável**, após avaliação manual: “aprovado, podemos adotar essa nova interface, como a interface oficial”. Identificador visual: `carmim-1`.

Portal, leitor, bancada e editoria nesta implementação são a referência para os próximos ajustes. O protótipo permanece como material de desenvolvimento; não é uma segunda interface oficial. A aprovação não implica conclusão das funcionalidades futuras de pesquisa, alinhamento e catalogação.

Não foram executados testes pelo assistente. Esta aprovação não incluiu solicitação de commit ou push; a publicação continua sendo uma operação separada.

## Resultado e decisões

A interface principal incorpora a direção aprovada: portal público, leitor confortável e bancada de pesquisa como experiências distintas. Não é mais necessário entrar em `/prototipo/` para avaliar essas mudanças.

- **Portal:** apresentação, busca, coleção em destaque, contagens do manifesto, registros de versões e fontes incorporadas e acesso às coleções com Capas/Lista e filtro preservados.
- **Identidade comum:** Carmim, superfícies claras, curvas suaves e os mesmos tokens no catálogo, busca, leitor, correção de trechos, editoria e página de entrada local.
- **Leitor:** painel com cabeçalho refinado, controles arredondados, estado/idioma, ações identificadas e expansão por tarefas. Começa recolhido, inclusive a faixa de abas das ferramentas. Retomar permanece disponível quando há marca. Fixação continua opcional.
- **Marcador:** segundo clique no trecho remove a marca. No estudo paralelo, a mesma linha é reconhecida mesmo se o segundo clique ocorrer na outra coluna. Seleção de texto, links e ações não marcam acidentalmente. O protótipo também recebeu a correção.
- **Estudo:** preserva tradução expansível, paralelo, números de bloco e correção de tradução por trecho no backend. Cada célula do paralelo identifica idioma e bloco. A cópia de referência deixa claro que o número é provisório desta versão, sem substituir uma referência arquivística.
- **Bancada:** documentos reais em abas; seleção por título/ID; instrumentos contextuais de Markdown/prévia, índice, ficha e notas. Sem repetir o catálogo inteiro na lateral ou criar outra faixa de ícones.

Mantidos textos, traduções, IDs, caminhos, URLs anteriores, paginação, navegação sequencial e APIs editoriais de gravação. Não houve migração de catálogo nem atribuição de estados de revisão.

## Arquitetura e arquivos

`assets/portal.js` compõe a home sobre o catálogo existente. `assets/workbench.js` monta os instrumentos ao redor da `.document-body` do leitor atual: não cria outro interpretador documental nem outra implementação dos modos de estudo.

A bancada usa o endereço existente do documento com `bancada=1`, por exemplo:

`/#/doc/showtrials-1665?colecao=centro-de-leningrado&bancada=1`

Remover esse parâmetro volta ao leitor público. Contexto de coleção/subcoleção e retorno editorial continuam nos parâmetros e mecanismos existentes. Idioma, modo e posição aproximada são conservados por documento durante a navegação nesta página. O idioma explicitamente solicitado por um link tem precedência sobre o contexto anterior.

Os estilos novos de portal e bancada ficam em `assets/css/portal.css` e `assets/css/workbench.css`. A identidade comum foi aplicada nos componentes existentes, sem carregar o CSS do protótipo em produção. HTMLs e imports usam `carmim-1` para atualização de cache.

## Rascunho da bancada e gravação real

O painel permite alterar um rascunho e ver sua renderização. O leitor ao lado continua mostrando o conteúdo preservado. O rascunho não é salvo automaticamente no acervo.

Com o backend local disponível, **Revisar na área editorial** envia o rascunho ao editor Markdown existente, com documento, idioma, retorno ao leitor e hash SHA256 dos bytes da versão de origem. O conteúdo não é transportado pela URL: fica temporariamente em `sessionStorage`. Arquivos com BOM são conservados na leitura do texto-fonte e no cálculo do hash.

O editor só aplica automaticamente o rascunho se documento, idioma e hash correspondem à versão atual. Se o arquivo mudou, mostra o rascunho preservado para comparação e mantém o texto atual no editor. Não substitui silenciosamente uma versão mais recente.

Depois disso, vale o fluxo já existente: **Revisar alterações no Markdown → conferir diferenças e prévia → Confirmar e salvar**. A gravação continua usando as APIs atuais, com revisão de catálogo, proteção de conflito, histórico recuperável e atualização de catálogo, manifesto e busca. Nenhuma publicação automática foi acrescentada.

No site estático, é possível ler, comparar, trabalhar com rascunhos e baixar uma cópia; gravação e importação continuam exigindo backend local. TXT permanece TXT: não foi incluída uma conversão implícita pelo editor da bancada.

## Persistência

| Informação | Onde permanece |
| --- | --- |
| Textos e metadados oficiais | Arquivos/catalogação existentes, alterados apenas no fluxo editorial confirmado. |
| Abas abertas | IDs e contexto em `sessionStorage`; sem copiar documentos. |
| Idiomas, modo e posição por aba | Contextos em memória durante o uso desta página. Preferências e marcador continuam com os mecanismos existentes. |
| Notas de trabalho | `sessionStorage` por documento; privadas nesta sessão do navegador. Não são notas públicas ou backup. |
| Rascunhos Markdown | Memória da página, por documento e idioma; aviso antes de sair/recarregar com rascunhos. |
| Transferência ao editor | Registro temporário de sessão; removido após confirmação da gravação correspondente. |

Fechar uma aba com rascunho Markdown pede confirmação antes de descartá-lo. Notas não são apagadas ao fechar a aba, pois continuam associadas ao documento na sessão. Baixar rascunho permite preservar uma cópia independente.

## Novidades da home

`assets/acervo-activity.json` contém um recorte de adições de arquivos registradas no Git, sem consultar ou expor `.local/editorial/history/`. As contagens gerais são calculadas do manifesto atual; documentos repetidos entre coleções são contados uma única vez.

Datas de registro no Git não são apresentadas como datas históricas nem como confirmação de publicação online. Inclusões ainda não commitadas e simples alterações de texto não entram nesse recorte de adições.

Para atualizar o recorte depois de novos commits de documentos/traduções:

```bash
python3 scripts/update_portal_activity.py
```

O script atualiza apenas esse JSON de apresentação. Não altera textos, catálogo ou histórico, não faz testes, commit ou push. O JSON atualizado precisa ser incluído em um commit autorizado para aparecer na publicação. O arquivo inicial foi preparado a partir do histórico já disponível; o script fica registrado para as próximas atualizações.

Futura evolução: registrar eventos próprios de incorporação e publicação no fluxo editorial, independentes do Git e das datas dos documentos. Não foi inferida cronologia editorial para o legado.

## Validação manual

1. Encerre o backend com Ctrl+C e execute `python3 -m backend`. A reinicialização também carrega a atualização visual de `/local`. Abra **http://localhost:8000/** e recarregue com Ctrl+Shift+R.
2. **Portal e catálogo:** confira dados, novidades, capas completas, Capas/Lista e filtro. Abra uma coleção/subcoleção, confira datas junto dos títulos, paginação e busca. Navegue de um resultado ao documento e volte.
3. **Barra e marcador:** abra **http://localhost:8000/#/doc/showtrials-1665?colecao=centro-de-leningrado**. O painel começa recolhido. Clique em um parágrafo, confira a bolinha e Retomar. Clique de novo: ambos devem desaparecer. Repita com Enter/Espaço e nos modos de estudo. No paralelo, confira a remoção ao clicar na outra coluna da mesma linha. Selecione texto: não deve criar marca.
4. **Estudo:** alterne leitura/estudo e parágrafo/paralelo sem recarregar a página; confira posição aproximada, traduções expansíveis, idiomas, referência do trecho e Corrigir tradução. Fixe e solte a barra. Exporte idiomas diferentes, conferindo nome de arquivo e cabeçalho.
5. **Abas:** clique em Bancada no painel. Use o ＋ ou Abrir documento e procure `1666`. Alterne entre os dois documentos, idiomas e instrumentos. Confira posição, índice, ficha e notas. Volte ao leitor pelo botão Leitor; a home não deve herdar abas ou instrumentos.
6. **Markdown e prévia:** em uma versão PT, faça uma pequena alteração no rascunho. A prévia à direita muda; o leitor preservado à esquerda não deve mudar. Alterne abas e volte. Baixe o rascunho se quiser conservar uma cópia.
7. **Transferência:** use Revisar na área editorial. Confira a mensagem de rascunho recebido, o documento/idioma e as diferenças. Até clicar em Confirmar e salvar, nada muda no acervo. Se optar por salvar, use o histórico existente para restaurar a experiência depois; confira a atualização do leitor, exportação e busca. Metadados e importação de tradução continuam acessíveis pelos caminhos existentes.
8. **Editor e celular:** confira fila, catálogo, metadados, coleções, importação, editor Markdown e histórico com a identidade comum. No celular, confirme menus operáveis, lateral retrátil e painéis empilhados. Use Tab para acessar abas, fechar documento, selecionar idioma e marcar parágrafos.

Não foi iniciada execução de testes, servidor ou navegador pelo assistente. A entrega foi examinada por leitura do código; os comportamentos acima ainda dependem da sua avaliação prática.
