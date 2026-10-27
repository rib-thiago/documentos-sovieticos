# Oficina documental — implementação anterior e dependências compartilhadas

Registro histórico de 25/10/2026. A interface oficial adotada em 27/10/2026 é o Estúdio (`/estudio/`) com o portal público na home. Este diretório preserva adaptadores de compatibilidade e distribuições locais usadas pela interface oficial. O texto abaixo descreve a etapa anterior; consulte [a adoção oficial](../../docs/interface/INTERFACE-OFICIAL.md).

## Abrir

Reinicie o backend para carregar os novos recursos liberados:

```bash
python3 -m backend
```

Abra **http://127.0.0.1:8000/editorial** (encaminha à bancada integrada) e use Ctrl+Shift+R. Não precisa instalar npm.

O [roteiro completo, matriz de funções e limites](../../docs/interface/OFICINA-INTEGRADA.md) é a referência desta entrega.

## Organização

- **Acervo:** explorador com coleção, subcoleção, títulos/IDs e acesso à consulta/ZIP da coleção.
- **Área editorial:** catálogo, cadastros, coleções, importação guiada, traduções, fila, histórico, fontes PDF/OCR, manipulação e projetos, agrupados por tarefa.
- **Documento:** leitura, estudo por parágrafo/paralelo, correção por trecho, fac-símiles, metadados, versões, exportação e preparação de impressão.
- **Markdown:** CodeMirror, teclado russo, prévia, comparação, recuperação e encaminhamento ao fluxo de revisão correspondente ao contexto.
- **Projetos:** seleção explícita, documentos/fontes vinculados, versões privadas e incorporação ao acervo com confirmação separada. Recarregar começa sem projeto ativo.
- **Painéis:** arraste ou use o menu Painel para mover, reunir, ampliar e fechar. A composição é guardada por contexto na sessão.
- **Notas:** por documento/projeto ou pelo contexto de trabalho, com download.

## Como as funções foram transportadas

Dockview organiza as abas. Catálogo, cadastros, importação, revisão, histórico e PDF/OCR são montados diretamente em painéis pelo controlador editorial compartilhado. Leitura/estudo e versões privadas preservam adaptadores de mesma origem. APIs, histórico e confirmação de incorporação continuam existentes. Consulte a [arquitetura e validação da bancada editorial](../../docs/interface/BANCADA-EDITORIAL-NATIVA.md).

Campos Markdown e transcrição compatíveis recebem CodeMirror; o campo estrutural para posicionar o cursor e dividir unidades permanece nativo. Fac-símiles reconhecidos usam uma página PDF.js com zoom e seleção textual, enquanto a ferramenta original comanda a página e conserva o alinhamento. A prévia do rascunho não tem um segundo marcador: leitura e estudo compartilham o marcador existente.

Depois de salvar, a bancada atualiza o catálogo/modelos. Um rascunho divergente é preservado para comparação; não há sobrescrita automática. Salvar é local e não faz commit/push. Os formulários abertos são reais, portanto confirmar uma gravação altera o ambiente local com o histórico existente.

## Bibliotecas

| Componente | Biblioteca fixada |
|---|---|
| Painéis | Dockview Core 4.11.0 |
| Editor | CodeMirror 6.0.2 + lang-markdown 6.3.4 |
| Comparação | @codemirror/merge 6.10.2 |
| PDF | PDF.js 4.10.38 |
| Impressão | Paged.js 0.4.3 |
| Imagem | OpenSeadragon 5.0.1 |
| Fac-símiles | BookReader oficial 5.0.0-66, distribuição local |
| Markdown | markdown-it, footnote e DOMPurify existentes |

Versões foram fixadas para reproduzir o experimento; não são uma afirmação de serem as mais recentes. Arquivos de distribuição, hashes e licenças ficam em `vendor/`. BookReader abre PDFs locais e fontes cadastradas, usando PDF.js como provedor de imagens. Não exige npm nem envia arquivos ao Archive. [Piloto Zinoviev e roteiro](../../docs/interface/PILOTO-ZINOVIEV-BOOKREADER.md). Annotorious/Mirador não foram incorporados.

## Recuperação e limites

Rascunhos nativos, notas, layouts e posições ficam na sessão; baixe uma cópia para trabalho importante. Os históricos persistentes do backend continuam separados e precisam de backup de `.local/`. Arquivos PDF/imagem selecionados no computador precisam ser escolhidos novamente após recarregar. Campos não confirmados de formulários conservam as proteções existentes; não se promete restauração completa de todo formulário depois de encerrar o navegador.

As operações de tratamento PDF/OCR, seleção de unidades/regiões e preparação de fac-símiles continuam nos componentes existentes. A diagramação Paged.js é uma edição de impressão, sem equivalência automática à paginação histórica ou garantia de notas ao pé de cada página.

## Validação

Sintaxe dos módulos/servidor e referências estáticas conferidas. Não foram executados testes de navegador, gravações de teste, OCR ou processamento do acervo nesta entrega. A validação funcional e visual está a cargo do responsável, especialmente contexto de projeto, gravação/retorno, adaptação CodeMirror e movimentação de hosts. Sem commit ou push.

## Reconstrução das bibliotecas

`package.json` e `package-lock.json` fixam a resolução. Com Node/npm no ambiente de desenvolvimento: `npm ci --ignore-scripts` e `npm run build` neste diretório geram `vendor/libraries.js`. Os outros arquivos de distribuição são copiados de `dockview-core/dist/styles/dockview.css`, `pdfjs-dist/build/pdf.min.mjs`, `pdfjs-dist/build/pdf.worker.min.mjs`, `pdfjs-dist/web/pdf_viewer.css` e `pagedjs/dist/paged.polyfill.js`, com nomes registrados no manifesto. Ao atualizar, recopie licenças/hashes e valide o piloto. Os módulos `oficina.js`, `workspace.js`, `embedded.js` e `pdf-frame.js` não precisam de compilação.
