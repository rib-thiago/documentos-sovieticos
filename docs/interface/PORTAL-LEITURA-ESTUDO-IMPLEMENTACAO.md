# Portal de leitura e estudo — entrega de 27/10/2026

O portal passa a usar a identidade carmim do Estúdio, mantendo a home como entrada pública. Implementação do núcleo do [plano](PORTAL-LEITURA-ESTUDO-PLANO.md), sem alteração de textos, traduções, IDs ou cadastros. Sem commit ou push.

## Entradas e capacidades

- `/` / `#/`: home com busca, coleção em carrossel manual, contagens deduplicadas, recorte de atividade existente, retomada da sessão e acesso ao estudo.
- `#/colecoes`: estante completa, capas/lista e filtro de coleções; detalhes e subcoleções preservam suas URLs e paginação.
- `#/doc/ID`: leitor normal. Barra compacta com idioma, marca/retomada, estudo, ficha, citação, download e fixação; índice e preferências recolhidos. Tamanho, largura e entrelinha na sessão.
- `#/estudo` / `#/estudo/ID?idioma=ru`: mesa pública de consulta. Abas fecháveis/arrastáveis, grupos laterais, concentração, ampliação, restauração e retomada explícita das abas guardadas na sessão.
- `#/sobre`: apresentação do projeto e critérios de leitura/edição.
- Estúdio: continua responsável por gravações locais, histórico, catálogo e projetos privados. Os acessos de edição só aparecem quando o backend oferece a capacidade necessária.

A mesa contém pesquisa por título/autoria/ID, leitura, parágrafos, paralelo, índice e ficha destacáveis, notas pessoais, Markdown somente consulta, citações, download, impressão e fac-símiles publicados. O paralelo mostra a ordem dos blocos sem afirmar alinhamento validado. A tradução expansível permanece no estudo da versão russa.

Selecione texto para citar ou acrescentar às notas pessoais. As notas ficam na sessão do navegador, por documento e idioma; têm exportação e importação, sem publicar conteúdo. O navegador pode impedir armazenamento; a interface informa a falha. Não há sincronização entre computadores.

Com backend, Corrigir trecho transporta o bloco e a seleção ao Estúdio. Uma assinatura SHA-256 do corpo precisa coincidir antes de abrir a correção; ela continua exigindo prévia, confirmação e histórico existentes. Importar tradução e editar Markdown também levam ao Estúdio, com retorno ao estudo. A mesa pública não salva no acervo.

## Visualizadores e carregamento

Markdown/footnotes/DOMPurify continuam na leitura. O renderizador de estudo foi extraído para `assets/modules/reading-surface.js` e compartilhado com o Estúdio; impressão Paged.js também foi compartilhada. Dockview, PDF.js/BookReader e imagens ampliáveis são carregados no uso da ferramenta. As dependências já estão no repositório: não é necessário npm.

O portal deixou de carregar controladores de projetos privados, OCR, cadastro e a adaptação antiga de páginas. A compatibilidade de navegação não monta a antiga bancada. A leitura pública não inicializa projetos locais.

BookReader usa apenas vínculos ativos de `data/facsimiles.json` e PDFs publicados. A inexistência desse arquivo é tratada como ausência de fac-símiles publicados. Arquivos de `.local` e de `temporario` não passam a ser públicos. Abrir um PDF de pesquisa no Estúdio não o publica automaticamente.

As páginas são mapeadas entre o derivado público e o PDF original. O seletor identifica página física; o zoom de imagem usa somente derivados de imagem realmente publicados. A impressão é uma edição de trabalho, não a paginação histórica da fonte. BookReader mantém o PDF aberto ao saltar entre páginas.

Citações incluem ID, idioma, URL e, quando disponível, assinatura do texto. A seleção é incluída como citação literal. Ainda não foi instituído um identificador permanente de unidade documental nem um serviço de resolução de seletores W3C. Não prometer permanência do § após revisão.

## Validação manual

1. Reinicie `python3 -m backend`; abra http://127.0.0.1:8000/ e faça Ctrl+Shift+R. Confira Início, Coleções, Buscar, Estudo e Sobre.
2. Na home, percorra ambos os carrosséis. Confira altura uniforme dos cartões, números do catálogo e separação entre datas de incorporação e datas históricas. O feed conserva o recorte de atividade existente; esta entrega não inventa nem regenera eventos de incorporação.
3. Abra uma subcoleção; confira título/data, paginação e ZIP completo. Use a busca e retorne aos resultados pelo documento.
4. Abra `#/doc/showtrials-1665`. Mude idioma; amplie/recolha índice e aparência; fixe/solte a barra; marque um parágrafo e clique novamente para desmarcar. Marque outro e use Retomar. Confira notas e exportação com apenas um cabeçalho.
5. Abra um texto longo com títulos/notas/tabelas e confira o índice, a leitura em tela pequena e o retorno depois de navegar a outro texto.
6. Clique Estudar. Abra outro documento pelo explorador. Experimente Leitura, Parágrafos e Paralelo, índice e ficha como abas, arraste-as lado a lado e feche-as. Use Ampliar, Concentrar e Restaurar. No celular, os blocos das duas línguas se empilham e os botões oferecem alternativa ao arraste.
7. Selecione uma frase e use Anotar seleção ou Citar seleção. Exporte as notas. Experimente mudar de idioma e voltar. Notas não se confundem com notas editoriais do texto.
8. Use Retomar abas, após voltar ao portal e reabrir Estudo sem documento. Essa ação restaura a composição explicitamente, sem ativar projeto privado.
9. Com backend, confira Editar no Estúdio, Importar tradução e Corrigir trecho numa tradução PT/EN. Cancele a prévia se não desejar alterar o acervo. Após salvar deliberadamente, retorne pelo link do Estúdio: o catálogo/leitor é recarregado pelo fluxo existente.
10. Para fac-símiles, escolha um documento com projeção pública efetivamente publicada. Abra Fac-símile, navegue no BookReader e confira o mapeamento de página. Sem projeção pública, a mensagem deve informar ausência e o texto continuar utilizável. Este teste não requer publicar o PDF de Zinoviev; seu cadastro local permanece privado.
11. Repita a consulta com `python3 -m http.server 8001`, usando http://127.0.0.1:8001/. Devem funcionar leitura, estudo, notas, ZIP e arquivos publicados, sem controles de gravação. Confira também os caminhos no GitHub Pages após uma publicação autorizada; nenhuma publicação foi feita nesta entrega.

## Verificações realizadas

28 testes isolados de rotas, catálogo e repositório passaram, incluindo acesso público aos novos módulos e recusa de arquivos privados. Não houve uso do banco/acervo real nesses testes. Sintaxe JavaScript, referências da entrada, delimitadores CSS e diferenças de arquivos conferidos. Simulações isoladas verificaram rotas legadas/novas, preservação de fronteiras com cirílico/emoji/CRLF, assinatura da marca e notas multilinha.

Não foram executados testes de navegador nem uploads/OCR/gravações de documentos. O roteiro acima é a validação funcional pendente do responsável.

## Ampliações que continuam separadas

- EPUB real e eventual epub.js/Readium: dependem de corpus nesse formato; Markdown não foi convertido para EPUB.
- Busca integral no site estático, entidades/pessoas/episódios e relações: continuam dependentes das entregas de dados/índice; a mesa anuncia pesquisa de títulos/autoria/IDs.
- Identificadores persistentes de unidades, seletores de citação e alinhamento validado entre idiomas: não são deduzidos pela interface.
- Sincronização de rolagem por alinhamento, destaque de caixas no fac-símile e publicação de novos derivados não foram adicionados a esta entrega.
- Integração ImageMagick→OCR e motor de tradução permanecem no plano do Estúdio.

## Retorno de avaliação: cabeçalho, edição e home

Após a primeira avaliação, reduzido o cabeçalho global a uma linha compacta, inclusive no celular. No estudo, ele deixa de acompanhar a rolagem; a faixa de título também é mínima. Comandos secundários foram agrupados nos menus Documento e Organizar, mantendo Leitura/Parágrafos/Paralelo acessíveis.

A home ganhou uma composição nova: abertura carmim com busca e dados do catálogo, novidades na coluna principal, coleção em foco e acesso ao estudo na lateral, documentos incorporados no rodapé da abertura. A estante completa fica em Coleções, sem duplicar todos os cartões na home.

Editar no Estúdio usa `#/doc/ID?idioma=...&editar=1`: abre o documento e o editor Markdown lado a lado. A entrada não aguarda mais inventário de PDFs/pilotos para abrir um documento; conserva a URL para recarga e responde a mudanças de hash. Falha na abertura fica explícita e oferece nova tentativa, sem ser apagada pela conclusão do diagnóstico.

Conferência manual adicional: atualizar o navegador; abrir um documento PT e outro RU e usar Editar; conferir título, idioma e editor do documento correto. Recarregar o Estúdio deve reabrir a mesma entrada. Na home, conferir a nova composição e o acesso à estante por Coleções. No estudo, conferir Documento/Organizar e o espaço liberado acima das abas. Sem commit ou push.

## Alternância na própria aba e expansão de idiomas

Leitura, Parágrafos e Paralelo agora mudam a renderização da aba documental atual, tanto nos comandos internos quanto na barra da mesa. O título e os parâmetros da aba acompanham o modo; o trecho visível é preservado por assinatura/posição quando possível. Abrir outra vista lado a lado continua sendo uma ação explícita em Organizar.

O estudo por parágrafos oferece expansão dos outros idiomas disponíveis em cada bloco, inclusive quando o idioma inicial é português. Os controles identificam Original ou Tradução e o código do idioma; o conteúdo é carregado sob demanda. As expansões são lembradas ao alternar modos dentro da mesma vista. Pareamento por ordem continua sem validação automática.

Conferência: com uma única aba documental, alternar Parágrafos → Paralelo → Leitura → Parágrafos, verificando que o número de abas não aumenta. Em PT, expandir original RU e tradução EN; em RU, expandir PT. Recolher e expandir novamente. Repetir no Estúdio. Simulação isolada do renderizador confirmou expansão em PT e troca em quatro etapas sem chamada para abrir outra aba; sintaxe verificada. Sem teste de navegador, commit ou push.

## Barra contextual única e fechamento da versão

A mesa pública e as vistas documentais do Estúdio usam uma barra superior compartilhada. Os controles não ficam mais dentro de cada painel de leitura: ao ativar uma aba, o idioma, modo, retomada e segundo idioma do paralelo acompanham aquela vista. Abas de ficha/índice/notas não recebem controles de leitura inadequados. A troca de idioma mantém a aba e o tipo de visualização. Os painéis continuam independentes; ativar um deles não altera a língua ou modo dos demais.

Validar: abrir dois documentos em grupos laterais, escolher modos/idiomas diferentes, alternar o foco e conferir a barra superior; mudar o idioma e o modo, verificar que não surgem abas extras; voltar à primeira vista e conferir seu estado. Fechar a aba ativa, abrir ficha/notas e voltar ao texto. Repetir nas vistas de leitura/estudo do Estúdio. Controles próprios de edição Markdown e processamento PDF continuam nas ferramentas correspondentes.

Para considerar fechada esta versão da interface:

1. Validar no navegador desktop e celular os percursos de home/coleções/busca/leitor/estudo e ida/volta ao Estúdio. Conferir troca de foco, idioma, marca, índice, notas, exportação e ZIP, também com servidor estático sem backend.
2. Conferir os percursos editoriais de cadastro, importação, correção, prévia, salvamento/histórico e trabalho privado, além de um ciclo PDF/OCR já existente. Corrigir regressões encontradas, sem ampliar o escopo durante a estabilização.
3. Conferir a composição da publicação: dependências locais necessárias, caminhos do GitHub Pages, contagens/recorte de atividade, ausência de arquivos privados e possibilidade de recuperação dos dados locais. Histórico de cada alteração não substitui uma cópia de segurança do ambiente de trabalho.
4. Após aprovação, organizar commits e publicar a versão autorizada. Manter uma referência Git recuperável para esta versão e registrar as pendências fora dela.

São evoluções posteriores, não requisitos para esse fechamento: EPUB/Readium, busca integral estática, entidades/relações, resolução permanente de seletores de citação, sincronização por alinhamento validado e integração ImageMagick→OCR. Pendências de revisão/incorporação de documentos continuam em sua fila própria e não devem ser confundidas com regressões da interface. A aceitação da interface não certifica que todo o acervo foi revisado.

Verificação desta unificação: nove testes isolados de recursos/rotas passaram; sintaxe e referências de controles conferidas. Simulação com duas vistas confirmou ausência das barras internas e preservação de idioma/modo ao alternar a barra compartilhada. Teste de navegador permanece pendente. Sem commit ou push.


## Auditoria dos visualizadores: BookReader pequeno

Confirmada dependência indevida do BookReader em `.pane-toolbar`, `.pane-body` e `.book-frame` da antiga `oficina.css`. O Estúdio não carregava essas regras: o iframe ficava no tamanho padrão do navegador. Criado `assets/css/document-viewers.css`, carregado explicitamente pelas entradas do portal e do Estúdio, com regras próprias para os visualizadores. Não foi reintroduzido o layout completo da Oficina.

| Área inspecionada | Resultado e ajuste |
|---|---|
| BookReader local do Estúdio | Faltavam as regras de tamanho e comandos. Contêiner e iframe agora ocupam o espaço restante do painel; controles e aviso têm estilo compacto próprio. |
| BookReader de fac-símiles públicos | Já possuía dimensionamento no estudo; contrato flexível reforçado na folha compartilhada. |
| Impressão Paged.js | Já havia altura flexível; recebeu escopo próprio e iframe com dimensionamento explícito. |
| Imagem ampliável/OpenSeadragon | Já havia área flexível; reforçados largura mínima, posição e limite do contêiner. |
| PDF nativo, editor e comparação Markdown | Cadeia de altura e regras dos componentes presentes. Não identificado o mesmo problema estrutural na inspeção de código. |
| Prévia PDF em ferramentas editoriais | Regra explícita para `.pdf-facsimile`, evitando o tamanho padrão do iframe nos hosts editoriais. |
| Catálogo, cadastro, importação, fila e projetos | Hosts `.studio-task` e estilos comuns presentes. Não identificado o mesmo vínculo com a folha da Oficina; validação visual continua necessária. |

A lista de fontes do BookReader também passou a usar a consulta leve, sem detectar motores de OCR apenas para preencher o seletor. Nenhum PDF foi enviado ou processado.

Verificação: nove testes isolados de recursos/rotas passaram; sintaxe, delimitadores CSS e caminhos dos recursos conferidos. Não houve teste de navegador. Conferir manualmente BookReader numa aba inteira e num grupo lateral, ampliar/restaurar o painel e redimensionar a divisão; repetir com impressão e imagem ampliável. O quadro acima registra inspeção estrutural, não certificação visual em todos os tamanhos de tela. Sem commit ou push.

## BookReader como atividade própria e tela inteira

A barra do Estúdio passou a considerar o tipo da aba ativa. BookReader não apresenta mais paginação da transcrição, OCR, candidatos, imagem ou salvamento da fonte de origem, mesmo que essa fonte tenha sido usada para abri-lo e suas abas de revisão tenham sido fechadas. A exploração lateral também deixa de mostrar a grade de revisão como se controlasse o BookReader. O acompanhamento periódico de fontes é retomado ao voltar à revisão.

Os controles do BookReader ficam na barra compartilhada: Abrir PDF (arquivo, fontes cadastradas e pilotos em menu), Revisão/OCR, Tela inteira e Sobre/licenças. O nome e o estado indicam o PDF realmente aberto no leitor, sem alterar o contexto ou os rascunhos da fonte anterior. Revisão/OCR abre a fonte e página escolhidas explicitamente. Abrir arquivo por esse menu permanece uma consulta até um cadastro confirmado.

Tela inteira usa a API nativa do navegador, incluindo o botão interno do BookReader e o atalho F. Se o navegador recusar ou não disponibilizar a API, usa uma sobreposição acima de toda a aplicação, fora das restrições de tamanho dos grupos da mesa. Há saída por botão e Escape; a disposição anterior é restaurada. Quando a sobreposição exigir reinserir o iframe, a fonte/página atual é reenviada. O mesmo controle de tela inteira foi aplicado ao fac-símile público.

Verificação: sintaxe, IDs, CSS e nove testes isolados de rotas/recursos passaram. Simulações verificaram ocultação/restauração dos comandos de revisão conforme a aba ativa, tela inteira nativa e fallback com restauração por Escape. Nenhum teste de navegador, upload, OCR ou gravação documental foi realizado. A autorização real de tela inteira depende do navegador e precisa de conferência manual.

Roteiro: abrir fonte → BookReader; conferir ausência da barra OCR/páginas; fechar as abas de fonte/transcrição e continuar lendo. Testar Abrir PDF com outro arquivo sem cadastrar. Acionar Tela inteira pelo comando superior e pelo ícone interno; sair com Escape. Voltar à mesa e conferir abas/divisões. Abrir Revisão/OCR e conferir a fonte/página corretas e os comandos de revisão restaurados. Sem commit ou push.
