# Portal Documentos Soviéticos — leitura e estudo

27/10/2026. Proposta para a próxima fase; não implementa nem substitui o portal atual. Complementa a adoção do Estúdio. Decisões de missão e organização de `docs/projeto/ARQUITETURA-EDITORIAL-UX.md` continuam válidas.

## Direção

Uma biblioteca digital histórica com a identidade visual do Estúdio e três experiências graduais: descobrir, ler, estudar. A home é a entrada. O leitor começa simples; a mesa de estudo acrescenta instrumentos sem exigir acesso editorial. O Estúdio continua responsável por modificar o acervo.

Equivalência significa compartilhar componentes, linguagem visual, documentos e contexto, não colocar todas as ferramentas editoriais na leitura. O público pode comparar fontes, citar e consultar metadados no site estático. Uploads, OCR, edição canônica e promoção privada pertencem ao backend local.

## 1. Descobrir — home, coleções e busca

Navegação principal curta: Início, Coleções, Buscar, Sobre o acervo. Acesso ao Estúdio aparece quando houver backend local. Mesa de estudo é um percurso disponível a partir dos documentos e da seleção de resultados.

Home proposta:

1. Identidade e missão em duas linhas, campo de busca destacado e entrada igualmente visível para coleções.
2. Resumo do acervo: documentos únicos, versões por idioma, coleções e traduções; rótulos explicitam a unidade. Derivar do catálogo/manifesto, sem contar associações duplicadas como documentos.
3. Acervo em movimento: novos documentos, novas traduções e revisões editoriais como eventos diferentes; histórico real de incorporação e publicação, sem usar data histórica como data de atualização. Datas indisponíveis não são inventadas.
4. Explorar coleções: capas inteiras, cartões de altura consistente, carrossel manual acessível com alternativa Ver todas. Não rotacionar automaticamente.
5. Retomar nesta sessão, quando houver marca, em bloco discreto; apresentação de proveniência e critérios editoriais ao final.

Coleção: capa, apresentação curta, abrangência, proveniência e totais; lista de subcoleções claramente subordinadas; lista documental paginada. Cada linha apresenta título e data histórica juntos, idiomas, tipo e estado editorial quando registrado. Alternância lista/cartões; filtros recolhíveis. ZIP de coleção/subcoleção inclui o conjunto completo, não apenas a página visível, conservando o comportamento existente.

Busca: consulta e filtros preservados na URL, retorno ao mesmo resultado/página; coleção, subcoleção, idioma, tipo, período e disponibilidade de tradução/fac-símile conforme dados existentes. No site estático, anunciar o alcance real da busca; não apresentar pesquisa de título como texto integral. Pessoas e episódios serão acessos transversais quando houver entidades catalogadas, sem inferir relações de uma coincidência textual.

## 2. Ler — entrada normal de um documento

Cabeçalho curto: coleção/subcoleção, título, data, idioma e estado da tradução. Ficha completa e proveniência ficam em painel recolhível. Traduções de trabalho permanecem públicas, distinguindo as revisadas somente com evidência editorial cadastrada.

```text
Documentos Soviéticos             Coleções  Buscar  Sobre
Coleção › Subcoleção
Título do documento · data
[PT ▾] [Índice] [Retomar ●] [Estudar] [Citar] [Baixar] [Fixar]

                 texto com largura confortável
                 notas e tabelas preservadas

                 ← Anterior    Próximo →
```

Barra compacta, recolhida inicialmente, com idioma e retomada sempre visíveis. Fixar/soltar e recolher/expandir continuam. Oferecer fonte, tamanho, entrelinha e largura como preferências de leitura, sem multiplicar menus. Texto contínuo é o padrão; paginação visual é opcional e não cria números de páginas históricas.

Preservar: índice derivado dos títulos, marca por clique e remoção pelo segundo clique, retomada na sessão, PT inicial quando disponível e preferência de idioma, notas navegáveis com retorno, Markdown fiel e download por ID/idioma. Anterior/próximo somente ao final e na ordem da coleção de origem; documentos com múltiplas associações mantêm esse percurso.

No celular: página com rolagem natural; índice/ficha em painel modal com fechamento visível, uma camada por vez; barra compacta que não cobre o trecho ao navegar. Nenhum arraste é obrigatório. Foco visível, Escape, rótulos de controles, contraste e preferência por movimento reduzido são requisitos.

## 3. Estudar — mesa pública de consulta

Ao clicar Estudar, documento, idioma, marca, origem e posição são transportados à mesa. Abrir a mesma fonte não perde a leitura. A mesa usa Dockview apenas quando ativada; o leitor comum não carrega seu conjunto de bibliotecas.

```text
[Explorar]  Documento A ×  Documento B ×       [Concentrar]
           ┌────────────────┬────────────────┐
           │ RU · § blocos  │ PT · tradução  │
           │                │                │
           └────────────────┴────────────────┘
           [Índice] [Ficha] [Notas] [Fac-símile] [Citar]
```

Composições prontas: texto; original + tradução; texto + fac-símile; dois documentos. A composição inicial é simples, com ferramentas recolhidas. Documento, índice, ficha e notas podem virar abas e ser posicionados lado a lado. Fechar uma vista não retira o documento do acervo. Limitar painéis visíveis por padrão, oferecer Restaurar organização e alternativa por botões ao arraste. No celular, mostrar uma vista por vez com troca rápida e preservação da posição.

Estudo por parágrafos conserva § e tradução expansível; paralelo conserva idiomas explícitos e blocos identificáveis. Sincronização de rolagem é opcional. Pareamento validado permite sincronização por vínculo; sem isso, mostrar blocos por ordem sem atribuir correspondência exata. Evitar construir todo o DOM de duas traduções enormes ao abrir; renderizar por seção/janela, preservando seleção, notas e âncoras, e medir antes de adotar virtualização mais complexa.

Selecionar trecho abre ações discretas: citar, copiar link, anotar. No ambiente local, acrescenta Corrigir tradução / Abrir no Estúdio. No público, notas pessoais ficam somente no navegador, com exportação/importação explícita; não são notas editoriais publicadas. Inicialmente, manter marca e composição na sessão; persistência entre sessões deve ser opção clara e nunca promessa de sincronização entre dispositivos.

Passagem ao Estúdio transporta documento/idioma/trecho/contexto, com Voltar ao estudo. A mesa pública não ganha um segundo editor canônico concorrente. Projetos privados e fontes locais nunca entram no manifesto público como consequência de abrir uma aba.

## 4. Fac-símiles e referências

BookReader atende à leitura sequencial de páginas; PDF.js à renderização de PDF; OpenSeadragon ao exame de uma imagem em detalhe. Uma mesma fonte tem um adaptador de páginas, reutilizado pelos visualizadores, evitando baixar/renderizar o PDF inteiro a cada troca de vista. Carregamento sob demanda e cache limitado; cancelar pedidos de páginas abandonadas.

Publicação estática requer PDF/imagens e um manifesto de páginas efetivamente publicados. URLs locais `/api/editorial/pdf/...` não são fontes públicas. O visualizador só aparece quando há um derivado público válido. Documentos coletados de HTML, como a maioria do ShowTrials, não recebem um fac-símile inventado nem ficam bloqueados por sua ausência.

Distinguir sempre página física do PDF, numeração impressa e § da edição digital. Link texto↔imagem pode apontar à página quando esse vínculo existir; destaque de região depende de caixas/alinhamento validado, já separado no modelo editorial. A interface não deduz página histórica por posição de bloco.

Citação por trecho deve conter documento, edição/idioma, versão/hash, trecho e contexto, além de página/cota quando documentadas. § é localizador da edição digital e pode mudar em revisão; não basta como âncora persistente. Propor âncora com identificador de unidade + texto exato/prefixo/sufixo + posição e versão, inspirada no W3C Web Annotation. Uma revisão ambígua exige conferência, nunca reassociação silenciosa. Preparar isso antes de prometer links permanentes a parágrafos.

## 5. Bibliotecas e decisões

“EbookReader” pode designar produtos diferentes; sem um pacote identificado, não presumir que seja o BookReader já instalado. Avaliação por formato e tarefa:

| Biblioteca | Papel proposto | Decisão |
|---|---|---|
| markdown-it + footnotes + DOMPurify | Texto Markdown, notas e HTML sanitizado | Reutilizar; leitura HTML acessível e contínua |
| Dockview | Abas, grupos, painéis e composição da mesa | Reutilizar; somente no estudo |
| Internet Archive BookReader | Sequência de imagens/fac-símiles próprios, páginas simples/duplas e navegação | Reutilizar distribuição oficial local; não depende de ler livros hospedados no IA |
| PDF.js | Renderização de PDFs disponíveis, navegação e camada textual quando existente | Reutilizar; texto selecionável depende da camada do arquivo, não executa OCR |
| OpenSeadragon | Zoom, giro e navegação de imagens de alta resolução | Reutilizar apenas na vista de detalhe |
| Paged.js | Composição paginada para imprimir/salvar edição de trabalho | Sob demanda; não é o motor padrão do leitor nem gera paginação histórica |
| epub.js | EPUB com texto refluível, navegação e anotações | Piloto opcional se entrar EPUB real; não converter Markdown apenas para justificar a lib |
| Readium Web / Thorium Web | Plataforma alternativa para leitura de publicações digitais | Avaliar numa fase EPUB mais ampla; sobreposição excessiva para esta entrega |

Documentação consultada em 27/10/2026: [BookReader](https://github.com/internetarchive/bookreader), [PDF.js](https://mozilla.github.io/pdf.js/getting_started/), [OpenSeadragon](https://openseadragon.github.io/), [Dockview](https://dockview.dev/docs/), [Paged.js](https://pagedjs.org/), [epub.js](https://github.com/futurepress/epub.js/), [Readium Web](https://readium.org/web/), [W3C Web Annotation](https://www.w3.org/TR/annotation-model/). São capacidades das bibliotecas, não garantia de que nossa integração já as ofereça.

Usar distribuições locais versionadas, licenças e hashes registrados; sem exigir npm no computador do responsável. Verificar compatibilidade, manutenção e requisitos de build antes de adotar uma biblioteca nova. Não atualizar todas as dependências junto com o redesign. Uma biblioteca de busca nova só entra depois de medir o índice estático: não fornece filtros ou qualidade de metadados automaticamente.

## 6. Arquitetura e aparência

Compartilhar tokens carmim, superfícies claras quentes, curvas discretas, ícones, botões, menus, cabeçalhos de painel e tipografia com o Estúdio. Serifada no documento, sem serifa na navegação. Cor organiza foco e estado, sem inferir certeza histórica. Evitar uma home dominada por números ou um painel técnico em torno de cada texto.

Separar módulos: navegação pública; dados publicados; apresentação de coleção/busca; renderização textual; âncoras/marcas/citações; visualizadores; mesa de estudo. O mesmo componente textual atende leitor, estudo e prévia editorial, com capacidades explícitas. Não embutir páginas antigas para depois restilizá-las. Eventos e recursos são descartados ao fechar painéis; nenhum observador global reconstrói continuamente a interface.

Provedor estático usa manifesto/arquivos publicados; provedor local acrescenta APIs e atalhos editoriais. Os dois expõem o mesmo contrato de leitura, mas capacidades diferentes. Todos os caminhos devem respeitar a base do GitHub Pages, inclusive publicação em subdiretório. Preservar `#/doc/ID`, coleções e URLs existentes com compatibilidade; não depender de reescrita de rotas no servidor.

## 7. Entregas e aceite

1. **Fundação e leitor piloto:** tokens compartilhados, capacidades estáticas/locais, barra compacta, índice/marca/idiomas, ficha, notas e exportação. Conferir três fontes: documento trilíngue ShowTrials, texto longo com títulos/notas/tabela e documento OCR com páginas vinculadas. Aceite: recursos existentes preservados, troca de vista/idioma sem reiniciar leitura, navegador Voltar útil, mobile sem sobreposição. Protótipo separado antes da adoção.
2. **Mesa de estudo pública:** Dockview sob demanda, múltiplos documentos, paralelo, painéis destacáveis, citação e ida/volta ao Estúdio. Aceite: funciona também sem backend, não expõe material privado, arraste tem alternativa e cada aba mantém idioma/contexto. Consolidar as diferentes implementações de estudo, evitando nova concorrência.
3. **Fontes visuais:** adaptador público de páginas, BookReader/PDF.js/zoom, continuidade texto↔página com vínculos existentes. Aceite: fonte publicada abre sem API local; fonte sem fac-símile continua plenamente legível; paginação/citação não inventa equivalências. ZIP continua disponível.
4. **Portal e descoberta:** home, coleção/subcoleção, filtros, atividade do acervo e retorno ao percurso. Aceite: contagens corretas, datas identificadas, cartões uniformes e pesquisa com alcance declarado. Home inicial pode ser desenhada junto ao piloto, mas só substituir quando leitor/estudo estiverem protegidos contra regressões.
5. **Ampliações condicionais:** EPUB real, exportação EPUB, busca integral estática, entidades/pessoas/episódios e relações documentadas. Não são pré-requisitos para lançar o novo portal. Prioridade posterior conforme corpus e custo medido.

Em cada entrega: verificar carregamento e recursos sob demanda, preservar textos/traduções/URLs e confirmar manualmente desktop/mobile com e sem backend. Casos obrigatórios incluem documento sem tradução, sem cabeçalhos, com notas, longo, imagem sem texto e falha de rede. Nenhuma alteração de acervo se justifica apenas pelo redesign. Testes e limites de cada entrega serão registrados quando implementada; nesta rodada houve somente planejamento.
