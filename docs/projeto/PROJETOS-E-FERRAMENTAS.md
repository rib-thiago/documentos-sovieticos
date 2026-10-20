# Projetos de pesquisa e ferramentas integradas

20/10/2026 — arquitetura aprovada em conversa e primeira implementação para validação manual. Não houve execução de testes, servidor, navegador, instalação, commit ou push nesta entrega.

## Direção do produto

Documentos Soviéticos publica uma edição histórica; a infraestrutura ShowTrials Discovery oferece um ambiente local de pesquisa. A bancada aproxima-se de um ambiente de desenvolvimento no sentido de documentos, instrumentos, configurações e resultados compartilharem um contexto de trabalho. Não se propõe implementar um terminal arbitrário ou copiar toda uma IDE antes de entregar ferramentas úteis.

Três entidades são distintas:

- **Projeto de pesquisa:** objetivo, notas de apresentação e vínculos com documentos/fontes. Pode permanecer local e produzir apenas artigos finais.
- **Coleção:** organização documental do catálogo. Um projeto pode tomar uma coleção como referência e reunir também documentos de outras coleções.
- **Publicação:** seleção deliberada dos resultados destinados ao site público. Revisado e público são estados distintos; nenhum projeto ou derivado se publica automaticamente.

Um documento pode participar de vários projetos por ID, sem duplicar seu texto. Uma fonte PDF também pode ser vinculada a vários projetos. A coleção de referência não altera a classificação do acervo nem sincroniza automaticamente suas inclusões futuras. Os vínculos de um projeto não estabelecem relações históricas entre as pessoas mencionadas nos documentos.

## Primeira implementação

### O que foi entregue

- Menu **Projetos de pesquisa** na área editorial.
- Cadastro de título, objetivo/descrição e coleção de referência opcional.
- Inclusão de documentos por busca de título/ID ou adição dos documentos atuais de uma coleção/subcoleção.
- Vínculos explícitos com PDFs já recebidos.
- Prévia antes de salvar, controle de revisão concorrente e histórico recuperável.
- Arquivamento reversível do projeto, preservando documentos, fontes e histórico.
- Projeto ativo persistido localmente, selecionável na navegação editorial.
- Destino explícito de projeto no upload PDF. Reenviar bytes idênticos reaproveita a fonte e pode vinculá-la a outro projeto sem duplicar o PDF.
- Lista de fontes filtrada pelo projeto, com **Mostrar todas as fontes** para consultar as demais.
- Indicação do projeto ativo e atalhos na lateral da bancada quando o backend editorial está disponível.
- Atalho **Iniciar projeto de pesquisa a partir desta coleção** na lista editorial de coleções. A inclusão dos documentos é uma ação explícita na prévia do projeto.

O projeto ativo é um contexto do ambiente local de um único pesquisador, compartilhado entre abas e persistido no backend. Operações já abertas mantêm o destino explicitamente escolhido; uma mudança de contexto não redireciona silenciosamente um upload em curso. Uma alteração concorrente de projeto pede nova abertura/prévia, preservando o que já foi salvo.

Projetos funcionam mesmo sem instalar a dependência PDF. Criar um projeto não altera catálogo, manifesto, índice de busca público/local ou textos: registra apenas vínculos operacionais. Alterações editoriais de documentos continuam no fluxo existente.

### Armazenamento e recuperação

- `backend/research_projects.py`: persistência, prévias, histórico, ativação e vínculos aditivos de fontes.
- `assets/research-projects.js`: cadastro, consulta, contexto editorial e acesso pela bancada.
- `.local/research/projects.sqlite3`: projetos, projeto ativo e histórico. Separado da busca e do banco de jobs.
- `.local/research/jobs.sqlite3` e `.local/research/sources/`: permanecem o armazenamento da oficina PDF.

As prévias de projeto expiram após 15 minutos ou reinício do backend; projetos e histórico confirmados permanecem. O histórico de projetos está dentro da página do projeto, separado do histórico editorial do acervo. Restaurar o estado anterior à criação arquiva o projeto, em vez de apagar seus materiais. Arquivar o projeto ativo remove sua ativação; reabri-lo não o ativa automaticamente.

Uma restauração pode reintroduzir referência a um item que deixou de existir: preserva-se o ID histórico, sem ressuscitar ou duplicar o documento. Uma edição posterior deve conferir/remover esses vínculos. Não há exclusão física de projetos nesta primeira versão.

**Backup:** encerre o backend e copie toda `.local/research/`, incluindo PDFs e os dois bancos. Ela é ignorada pelo Git. Nem push nem reconstrução da busca substituem esse backup. Não remover estado operacional para reindexar o catálogo.

## Roteiro manual

1. Encerre e reinicie com `python3 -m backend`. Abra http://127.0.0.1:8000/editorial#/projetos . Recarregue com Ctrl+Shift+R se necessário.
2. Clique em **Novo projeto**, preencha título/objetivo e deixe a coleção de referência vazia. Busque um documento pelo ID, por exemplo `showtrials-1665`, e vincule. Se houver PDFs recebidos, selecione um. Confira a prévia detalhada e confirme a gravação local.
3. Abra o projeto, ative-o e confira o seletor na lateral. Abra o documento na bancada: o contexto local e o acesso ao projeto devem aparecer sem alterar o texto.
4. Na área editorial, abra **Coleções** e use **Iniciar projeto de pesquisa a partir desta coleção**. Preencha o título e clique em **Adicionar documentos da coleção de referência**. Confira a quantidade e a prévia. Confirme: isso não deve duplicar arquivos ou alterar o catálogo.
5. Abra o primeiro projeto e vincule um documento de outra coleção. Remova um vínculo e confirme: o documento deve continuar disponível no acervo.
6. Use **Receber PDF neste projeto**. Confira o destino no formulário antes de enviar um PDF pequeno. Depois retorne ao projeto: a fonte deve constar nos vínculos. Na oficina, **Mostrar todas as fontes** permite sair do filtro do projeto.
7. Troque o projeto ativo em outra aba. Um formulário de upload já aberto deve manter o destino escolhido, evitando gravação silenciosa no novo contexto. Se isso alterar um projeto aberto em edição, sua prévia antiga deve ser rejeitada ao salvar.
8. Edite o objetivo do projeto, confira e salve. Abra seu **Histórico recuperável**, prepare a restauração de um estado anterior, confira a prévia e confirme. Fontes e documentos continuam intactos.
9. Arquive o projeto ativo, confira a prévia e salve. A ativação deve ser removida. Abra o projeto arquivado, desmarque o arquivamento e salve para reabri-lo.
10. Encerre e reinicie o backend: projetos, vínculos, histórico e último projeto ativo não arquivado devem permanecer.

Nenhuma etapa exige commit ou push. O site público não recebe a lista de projetos, o contexto ativo ou fontes locais. A mesma edição de texto continua sendo compartilhada entre projetos; versões independentes por projeto ainda não existem. Não usar um projeto como promessa de cópia isolada de um documento.

## Ferramentas: contrato a preservar nas próximas entregas

Cada ferramenta recebe entradas explícitas, configuração e contexto capturado; gera candidatos com proveniência antes da incorporação editorial:

**Entrada preservada → parâmetros/receita → processamento durável → resultado candidato → prévia → incorporação local → publicação separada.**

Registrar arquivo/hash, páginas de origem, motor/versão, parâmetros, estado e histórico. Reprocessar não deve substituir correção humana. Visibilidade pública é independente da conclusão técnica e da revisão.

### Ordem de implementação

1. **Esta entrega:** projeto ativo mínimo e vínculos com fontes/documentos, sem migração do acervo.
2. **Manipulação PDF:** recepção do PDF integral de Tukhachevsky, extração de intervalos e divisão; depois combinar, reordenar e girar. Aumentar/tornar configurável o limite de fonte sem depender de dividir o PDF para poder recebê-lo. Preservar original e mapa das páginas de origem nos derivados. O limite de 60 MiB ainda não mudou nesta entrega.
3. **Revisão e OCR:** correção durável por página, fronteiras de parágrafos, referências, fac-símile no estudo e OCR opcional `rus`, `eng`, `por`. Usar o mesmo projeto e banco de arquivos, sem uma interface paralela desconectada.
4. **Abas e painéis:** instrumentos como abas, abrir ao lado e movimentar; preservar rascunhos, foco e contexto. A lateral já pode ser recolhida; não refazer esse recurso.
5. **Imagens, tradução e dados:** adaptadores opcionais de tratamento de imagem, glossário/tradução e catalogação assistida, seguindo o mesmo contrato.

Não implementados aqui: split/merge/extract de PDFs, OCR, recorte/tratamento de imagens, tradução automática, artigos privados por projeto, permissões multiusuário, arraste de painéis e publicação de projetos. Não confundir vínculos de pesquisa com o futuro vínculo editorial entre parágrafo, página e região do fac-símile.

## Acesso e publicação

Atualmente existem dois ambientes reais: público estático e backend editorial em loopback, protegido pelos controles locais já existentes. “Local” não constitui um sistema de contas. Uma eventual hospedagem do backend exigirá autenticação, autorização e isolamento de arquivos/jobs no servidor, não apenas ocultar botões. Projetos locais não vão ao catálogo público por inferência; uma publicação futura terá seleção e projeção explícitas.

## Atualização — workspace e isolamento de versões

A entrega seguinte substitui a limitação inicial de edições compartilhadas: agora há versões de trabalho independentes por projeto/documento/idioma, com incorporação explícita ao acervo. Documentos abrem na mesma guia, com explorador e seletor na bancada. A afirmação anterior de que não existiam versões independentes descreve a primeira entrega, não o estado atual. Consulte [Workspace e versões](WORKSPACE-E-VERSOES.md) para comportamento, roteiro manual e limites.
