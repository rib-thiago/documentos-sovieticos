# Bancada editorial integrada — 25/10/2026

## Decisão e alcance

A bancada reúne pesquisa e edição em um ambiente de abas. A home pública continua em `/`. No backend local, `/editorial` encaminha para `/prototipo/oficina/`, preservando o destino indicado no fragmento da URL. A interface anterior permanece em `/editorial/form` durante a validação.

Catálogo, ficha de metadados, coleções, cadastros, importação, fila, histórico, administração de projetos e ferramentas PDF/OCR são montados diretamente em painéis da bancada. Não carregam a página editorial antiga em um iframe. O controlador editorial foi extraído como componente montável; as APIs, prévias, confirmação e histórico existentes continuam responsáveis pelas gravações.

Leitura, estudo e edição de versões privadas ainda reutilizam componentes existentes em adaptadores da mesma origem. Isso preserva marcador, correções por trecho, alinhamento e confirmação de incorporação. Não se declara uma reescrita integral desses componentes. O carregamento inicial dos adaptadores é preparado antes da exibição para evitar mostrar primeiro sua interface anterior.

## Organização do trabalho

- **Acervo:** localizar e abrir documentos; cada texto pode ocupar uma aba ou grupo.
- **Acervo e edição:** catálogo, cadastros, coleções, importação, revisão e histórico.
- **Fontes e ferramentas:** PDF/OCR e instrumentos de pesquisa.
- **Ficha documental:** propriedades divididas em identificação, classificação e data/referência; associações e pendências permanecem na mesma tarefa.
- **Cadastros e corpus:** etapas em uma coluna de navegação, com a etapa ativa na área central.
- **Importação:** documento e contexto na lateral; arquivo e conferência no centro. A prévia de tradução/Markdown oferece Diferenças, Texto e Diagnóstico, com confirmação ao final.

Salvar continua sendo uma operação local. Não publica no GitHub. Projetos conservam versões privadas e uma confirmação separada para substituir o acervo. Formulários alterados e rascunhos impedem fechamento silencioso; atualizações do catálogo não descartam rascunhos divergentes.

## Validação manual

Reinicie o backend com `python3 -m backend`. Abra **http://127.0.0.1:8000/editorial** e pressione **Ctrl+Shift+R**.

1. Abra **Acervo e edição → Catálogo**. Pesquise um documento e abra sua ficha. Confirme que aparece em uma aba da bancada, sem mostrar antes a página antiga.
2. Na ficha, alterne os grupos de propriedades. Modifique um campo, abra a prévia e confira o valor anterior/novo. Salve somente uma mudança que queira manter; confira o resultado no leitor e o registro em Histórico.
3. Abra **Novo documento**, **Coleções** e **Importar corpus**. Percorra as etapas pela coluna interna. Confira que os campos permanecem preenchidos ao alternar etapas. Não é preciso gravar cadastros de teste.
4. Para um documento conhecido, abra **Adicionar tradução**, escolha documento/idioma e carregue um Markdown. Confira **Diferenças**, **Texto** e **Diagnóstico** antes de confirmar. Uma substituição deve conservar a versão anterior no histórico.
5. Abra **Revisão** e **Histórico**. Confira filtros, paginação e acesso ao documento. A fila inicial reúne os estados ainda em aberto.
6. Abra uma fonte em **PDF/OCR**, navegue por páginas e confira fac-símile/transcrição, teclado russo e controles de processamento. A migração não altera a necessidade de ferramentas OCR instaladas no backend.
7. Abra duas tarefas, arraste uma aba para a borda e alterne entre elas. Feche uma edição com mudança não salva: deve haver confirmação. Cancele e confira que a edição permanece.
8. Selecione um projeto e confira que suas versões continuam privadas. Salvar privado e incorporar ao acervo devem continuar sendo ações distintas. Recarregue: o contexto inicial deve ficar sem projeto ativo.
9. Abra um texto em Leitura/Estudo e confira marcador, retomada, paralelo, correção de trecho e retorno após edição. Esses componentes preservados precisam de validação de regressão.

Para retornar à implementação anterior durante a conferência: **http://127.0.0.1:8000/editorial/form**. Não mantenha o mesmo documento em edição simultânea nas duas interfaces.

## Verificações e limites

Conferidas sintaxe JavaScript/Python e referências estáticas. Não foram executados testes de navegador, gravações de teste, OCR nem processamento documental nesta entrega, conforme orientação do responsável. A validação funcional e visual permanece pendente. Nenhum commit ou push foi feito. A revisão documental continua pausada.

## Arquivos centrais

- `prototipo/oficina/editorial-native.js`: montagem, navegação por painel e organização das ferramentas.
- `prototipo/oficina/editorial-native.css`: apresentação interna dos instrumentos.
- `assets/editorial.js`: controlador compartilhado com a interface anterior.
- `prototipo/oficina/oficina.js`: integração com abas, contexto e atualização após salvar.
- `prototipo/oficina/host-boot.js`: preparação antecipada dos adaptadores de leitura/estudo.
- `backend/server.py`: entrada local e liberação dos recursos estáticos.
