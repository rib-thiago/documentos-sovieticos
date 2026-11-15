> **Adotado como interface oficial em 15/11/2026.** Acesse `/`; `/prototipo/mesa/` encaminha para essa entrada. O conteúdo abaixo registra a evolução e os testes do piloto, incluindo decisões históricas. Estado atual: [Interface oficial](INTERFACE-OFICIAL.md).

# Piloto Biblioteca + Mesa — 14/11/2026

Implementação separada aprovada para experimentação. **Não substitui a interface oficial**. Nesta evolução, edição Markdown e importação individual de tradução podem modificar o acervo local **somente após prévia e confirmação específicas**, usando o backend existente. Guardar rascunhos continua restrito à sessão; catálogo, metadados e coleções/subcoleções agora também oferecem gravação real com confirmação. Importação de corpus permanece demonstrativa. Base: [proposta de redesenho](PROPOSTA-REDESENHO-2026-11-14.md).

## Abrir

Na raiz do projeto, execute `python3 -m backend`. Se já estava aberto antes desta entrega, encerre com Ctrl+C e inicie novamente para carregar a nova rota. Acesse:

**http://127.0.0.1:8000/prototipo/mesa/**

A home habitual e `/estudio/` continuam disponíveis. O piloto também funciona com servidor estático na raiz (`python3 -m http.server 8000`). Não exige npm, instalação ou internet: usa as bibliotecas já presentes no repositório.

## O que experimentar

1. **Biblioteca:** escolha uma coleção e, quando houver, subcoleção. Pesquise um nome ou ID, navegue pela paginação e abra um documento com traduções — por exemplo, procure `1665`. O catálogo e os números vêm do manifesto atual; a data exibida é documental, nunca a data de coleta.
2. **Mesmo material, outra atividade:** no cabeçalho, alterne Leitura, Estudo por trecho e Comparar idiomas. O documento continua na mesma aba. No estudo, expanda uma tradução. Na comparação, o segundo idioma é escolhido na barra superior; cada par de blocos ocupa uma linha de altura comum, com rolagem única. Os números identificam blocos renderizados neste piloto; não são ainda identificadores permanentes de citação. A expansão usa ordem dos blocos e sinaliza que esse pareamento precisa ser conferido.
3. **Posição e espaço:** clique num parágrafo para marcar; clique novamente para desmarcar. Use Retomar, troque de atividade e confira a posição. Abra o Índice; clique novamente em Índice para recolher, ou feche pelo ×, Escape ou fora do painel. O menu ☰ também abre e recolhe os painéis. Fixar torna o painel persistente, mas pode ser desfeito. Sem fixação, ele se sobrepõe temporariamente ao texto.
4. **Vários materiais:** abra ☰ → Abrir outro documento. As abas aparecem desde o primeiro material aberto; com dois materiais, troque entre ambas e feche pelo ×. A busca da Biblioteca mantém seus filtros ao voltar. Para fechar o último material, use ☰ → Fechar material ativo.
5. **Markdown:** escolha Editar rascunho. O editor CodeMirror e a prévia ficam lado a lado. Altere uma frase, clique Conferir rascunho, compare as duas versões e marque a confirmação. Guardar retorna à leitura usando o rascunho. Nada foi escrito no arquivo original. Em ⋯ é possível baixar Markdown com o nome da versão do acervo.
6. **Recuperação:** abra ☰ → Histórico dos rascunhos. Restaure uma versão anterior ou exporte a sessão em JSON. O JSON é uma cópia de trabalho restaurável em ☰ → Rascunhos e recuperação → Restaurar cópia exportada. A confirmação baixa uma cópia da sessão anterior antes de substituí-la.
7. **PDF:** ☰ → Experimentar fac-símile do acervo abre uma fonte pesquisável relacionada ao documento 8687, na página física indicada no vínculo. Ou abra um PDF do computador. Use Extrair texto para obter a camada pesquisável da página atual, confira contra a imagem e ajuste a transcrição. A imagem e o texto ocupam a área principal. As notas sobre abrangência do vínculo estão em ⋯.
8. **Revisar uma página:** abra Teclado russo e teste ⇪, letras e espaço. O teclado fica encaixado abaixo da transcrição, sem encobrir o PDF ou o texto; o mesmo botão ou Recolher o fecha. Em Conferir e salvar, indique se conferiu a página e avance à prévia. Após confirmar, retorne à página para ver o rascunho. O botão ⋯ permite baixar as transcrições e ajustar a imagem à largura.
9. **Catálogo:** na Biblioteca, clique Catálogo. Procure um documento, altere sua ficha e confira a proposta. Cancele uma vez e confirme outra. A ficha guardada é um rascunho separado: não altera o manifesto nem finge já ser metadado publicado.
10. **Importar corpus:** para o primeiro teste, clique **Experimentar com dois arquivos de exemplo**. A coleção e os idiomas serão preenchidos; avance em **Conferir corpus**, veja um original russo e uma tradução portuguesa, confirme e observe o download da proposta JSON. Nada entra no catálogo real. Para testar seus próprios arquivos, escolha coleção/subcoleção, fonte, autoria e idioma original. Selecione arquivos como `documento.ru.md`, `documento.pt.md`. Confirme os idiomas identificados e veja a proposta por documento/versão. Duplicações de ID + idioma são bloqueadas; IDs existentes recebem alerta. Ao confirmar, o piloto guarda e exporta uma proposta JSON, **sem incorporar arquivos ao acervo**.

## Limites deliberados

- Rascunhos, notas, marcadores e histórico usam `sessionStorage`, na mesma aba do navegador. Não são backup durável. Exporte o trabalho antes de encerrar a sessão. O armazenamento do navegador tem limite; evite corpus grande neste piloto.
- As abas, atividades, posições e alterações em andamento são reconstruídas após recarregar a mesma aba. PDFs do acervo reabrem automaticamente; PDFs escolhidos no computador precisam ser selecionados novamente. A mesa mantém o nome, a página e as transcrições. Arquivos escolhidos não são enviados ao servidor.
- O contexto inicia em **Mesa principal**, identificado no cabeçalho como **Rascunhos · sessão**. O **Caderno experimental** demonstra a separação dos rascunhos de texto e transcrição; **não cria nem representa um projeto real do backend**. A Mesa principal habilita a preparação de gravações reais se o backend estiver disponível; trocar de área não grava e descarta prévias de gravação abertas. Notas, marcadores e materiais abertos são compartilhados.
- Fontes PDF agora executa extração nativa e OCR reais pelo backend existente, com prévia e revisão persistente. PDF temporário no navegador continua limitado à extração nativa e rascunhos da sessão, com acesso para cadastrar a fonte no backend. Cadastrar fonte, revisar página e criar documento são etapas distintas. Nenhuma delas faz publicação automática.
- Recuperação real do acervo, projetos, criação de coleções, filas, processamento OCR/imagem, alinhamentos certificados e incorporação definitiva ainda devem ser portados após a avaliação deste desenho.

## Matriz da primeira entrega

| Capacidade | Situação no piloto |
|---|---|
| Biblioteca, coleções/subcoleções, busca, paginação | Dados reais, consulta |
| Leitura, idiomas, índice, marcador e retomada | Interativos na mesma aba |
| Paralelo e expansão por trecho | Interativos; alinhamento por ordem não certificado |
| Vários documentos e PDF | Abas de materiais; fechamento disponível |
| Ficha, índice e notas | Um painel auxiliar por vez; fixação opcional |
| Editor Markdown e prévia | CodeMirror local, alternativa simples se falhar |
| Prévia antes/depois e histórico | Rascunhos da sessão, exportáveis |
| PDF e transcrição | PDF.js, extração nativa real e revisão manual |
| Teclado russo | Componente existente, com maiúsculas |
| Catálogo/importação | Propostas da sessão; sem gravação canônica |
| OCR e demais operações do backend | Permanecem na interface oficial |
| Arrastar, dividir e reorganizar painéis livremente | Evolução posterior |

## Decisões e verificações

A interface usa módulos JavaScript nativos e dependências locais já existentes. Nenhum framework, gerenciador de pacotes ou contrato de escrita novo foi introduzido. O servidor recebeu apenas a rota e a lista explícita dos dez arquivos executáveis do piloto; diretórios privados continuam bloqueados.

Verificações realizadas: sintaxe dos três módulos; auxiliares de catálogo, deduplicação, cabeçalhos repetidos, idiomas, datas e seleção de páginas; quatro testes HTTP em acervo temporário, incluindo recursos, redirecionamento, bloqueio de arquivos privados e preservação da home/catálogo oficiais. Nenhum teste usou ou alterou o acervo de produção.

Não houve teste visual automatizado: não há navegador disponível neste ambiente. O roteiro acima orienta a validação de navegação, espaço útil, foco, telas menores e revisão de PDFs reais.

Sem commit ou push. As frentes de coleta e revisão existentes permanecem separadas deste piloto.

## Ajustes após o primeiro teste

Comparação em linhas comuns e idioma secundário no cabeçalho; acionadores que também recolhem painéis; teclado russo encaixado abaixo da transcrição e recolhível; importação com exemplo demonstrativo explícito. Corrigido também o campo de busca do catálogo para não perder o foco durante a digitação.

## Continuidade da mesa — segunda evolução

O nome ambíguo “Acervo local” foi substituído por “Mesa principal”; “Projeto experimental” passou a “Caderno experimental”. São áreas de rascunho, não destinos de publicação. O texto da janela explica seus efeitos.

Teste adicional:

1. Abra dois documentos. Edite uma frase sem confirmar, aguarde um segundo e recarregue a mesma aba. Confira as abas, a atividade e o texto em andamento. Um ponto na aba indica alterações ainda não confirmadas.
2. Em ☰ → Rascunhos e recuperação, confira as alterações em andamento e os rascunhos já confirmados na sessão. Retome um deles.
3. Exporte a sessão, depois restaure o JSON exportado. Confira a prévia e confirme a substituição; uma cópia da sessão anterior é baixada automaticamente. O catálogo real continua intacto.
4. Abra um PDF do computador, vá a uma página, escreva um trecho e aguarde um segundo. Recarregue e selecione novamente o mesmo arquivo: página e transcrição devem reaparecer.
5. Abra a ficha de um documento por ⋯ → Ficha catalográfica → Ajustar metadados no piloto. Altere um campo, abra a prévia e volte sem confirmar: os campos em andamento são mantidos. “Voltar ao texto” retorna ao documento e à atividade anterior.

Verificação adicional: serialização e restauração de abas, idioma, atividade, posição e rascunhos pendentes; PDF enviado recuperado como fonte a reabrir, sem serializar o arquivo ou objetos do visualizador; rejeição de materiais desconhecidos; rota explícita do novo módulo. Os quatro testes HTTP passaram em acervo isolado. Navegação visual permanece para avaliação manual.

## Estudo multilíngue e Biblioteca — terceira evolução

O seletor do idioma secundário aparece no cabeçalho tanto em Comparar idiomas quanto em Estudo por trecho. O documento mantém a preferência ao alternar entre as atividades. Mudar o idioma secundário preserva os trechos expandidos; a abertura continua baseada na ordem dos blocos e não certifica alinhamento documental.

A Biblioteca recebeu composição editorial com busca em destaque, estatísticas calculadas do catálogo, coleção apresentada e capas em molduras uniformes, usando `object-fit: contain`. As imagens existentes não foram alteradas nem cortadas; coleções sem capa recebem um elemento tipográfico. Os cards mantêm estrutura regular e exibem idiomas e quantidade de documentos/subcoleções. Não foram inventadas datas de publicação ou listas de novidades.

Teste curto:

1. Atualize o piloto com Ctrl+Shift+R e procure um documento com RU, PT e EN, como 1665.
2. Escolha russo como idioma principal e Estudo por trecho. No segundo seletor, escolha English e abra um trecho. Troque para Português: o trecho continua aberto, mostrando a versão escolhida.
3. Alterne para Comparar idiomas: confira que o idioma secundário foi mantido. Recarregue e confira a recuperação da preferência e dos trechos abertos na sessão.
4. Volte à Biblioteca. Confira capas sem cortes, cards regulares, adaptação a uma janela estreita, coleção em destaque e retorno da Mesa com os filtros preservados.

Verificações adicionais: seleção válida do segundo idioma em documentos com três versões; alternativa quando o idioma escolhido coincide com o principal; documento monolíngue; recuperação da preferência e dos trechos expandidos. Sintaxe dos módulos e auxiliares passaram; aparência e navegação visual requerem conferência manual.

## Trechos, notas e citação — quarta evolução

As traduções expandidas recebem superfície própria com fundo claro, borda carmim e sombra discreta. O conteúdo traduzido usa um contêiner com idioma explícito e tipografia de leitura, separado do controle de expansão.

Selecionar palavras dentro de um único bloco abre uma pequena barra transitória com **Citar** e **Anotar**. Funciona no texto principal, no idioma secundário do paralelo e na tradução expandida. Não há barra permanente nova; Escape ou × recolhe as ações.

A citação traz trecho, título, data quando disponível, idioma, referência arquivística quando disponível, fonte e link do documento. Rascunhos confirmados da sessão são identificados como versões não publicadas. A numeração dos blocos é explicitamente provisória: não foi criado um sistema de endereçamento permanente nem certificado um alinhamento documental.

As notas podem ser gerais ou vinculadas ao trecho selecionado. Guardam citação, idioma, assinatura textual e horário; versões antigas de notas simples continuam legíveis. O texto de uma nota em elaboração também acompanha a sessão. O botão **Notas** fica junto do Índice, e as notas do documento podem ser baixadas em JSON.

**Localizar trecho** busca a assinatura textual na versão correta. Se o texto mudou ou houver várias ocorrências iguais, informa a situação e não escolhe outro parágrafo silenciosamente. A nota conserva sua citação. Isso não constitui validação histórica de uma afirmação da fonte.

Teste curto:

1. Em Estudo por trecho, abra uma tradução e confira a moldura. Troque o idioma secundário e confira o mesmo espaço.
2. Selecione algumas palavras de um único parágrafo, clique **Citar**, confira idioma/fonte e copie ou baixe a citação.
3. Selecione um trecho da tradução e clique **Anotar**. Escreva e guarde uma nota. Abra **Notas**, confira a citação e clique **Localizar trecho**.
4. Recarregue a mesma aba, abra Notas e confira a permanência. Exporte as notas do documento.
5. Opcional: edite o texto citado, confirme o rascunho e tente localizá-lo pela nota anterior. Deve informar que o trecho mudou, preservando a citação antiga.

A sintaxe e as verificações auxiliares passaram, incluindo o conteúdo da citação, a identificação do idioma e os avisos de numeração provisória/rascunho. A interação de seleção e a aparência precisam de validação manual no navegador. Não houve gravação canônica, commit ou push.

## Gestão de notas e localização exata — quinta evolução

O compositor separa **Nota geral** de **Nota sobre trecho**. A primeira informa que pertence ao documento inteiro; a segunda mostra a frase à qual será vinculada. Os botões de gravação dizem **Guardar nota geral** ou **Guardar nota deste trecho**. Para iniciar a segunda, selecione palavras e use **Anotar trecho**. A última seleção aparece explicitamente na prévia da nota; não se infere o trecho a partir do marcador de leitura.

Notas guardadas têm identificação de tipo, **Editar nota** e **Apagar nota**. A exclusão retira a nota da lista e a mantém em **Notas apagadas**, com **Desfazer última exclusão** e recuperação individual. Não há exclusão definitiva nesta etapa. Edições conservam a versão anterior no histórico recuperável. Notas antigas sem identificador são atualizadas sem apagar seu texto; notas e lixeira acompanham a cópia JSON da sessão e a exportação de notas do documento.

Novas âncoras guardam frase literal, idioma, limites de caracteres e contexto antes/depois. **Localizar frase** usa um Range do DOM para realçar somente a seleção original, preservando links, negrito e itálico. CSS Highlights é usado quando disponível; seleção nativa é a alternativa. Não se insere marcação que altere o texto ou a assinatura do parágrafo. O trecho é centralizado na área de leitura, sem pintar o parágrafo inteiro.

Se apenas o entorno mudou e a frase ainda é identificável literalmente, a localização informa essa mudança. Frases repetidas sem contexto suficiente geram aviso; frases modificadas não são substituídas por correspondências aproximadas. Notas anteriores sem limites de caracteres continuam usando a citação literal para localização, com a mesma precaução de ambiguidade.

Teste curto:

1. Clique em Notas: confira **Nova: nota geral do documento** e **Guardar nota geral**. Guarde uma observação.
2. Selecione uma frase curta dentro de um parágrafo, use **Anotar trecho** e confira a citação e o botão **Guardar nota deste trecho**. Guarde a nota.
3. Use **Localizar frase**: somente as palavras escolhidas devem ser realçadas. Repita selecionando uma frase que atravesse negrito ou itálico, quando disponível.
4. Edite uma nota e guarde. Apague outra; confira que desaparece da lista e use **Desfazer última exclusão**. Apague novamente e recupere pela lista **Notas apagadas**.
5. Recarregue e confira as notas, os tipos e a recuperação. Notas apagadas continuam preservadas na cópia JSON, sem gravar no acervo.

Verificações executadas: sintaxe dos módulos e testes de âncoras para seleção menor que o parágrafo, frases repetidas, mudança de entorno, frase ausente, espaços nas bordas e offsets UTF-16. A interação com Range, as exclusões e o aspecto do destaque devem ser conferidos no navegador pelo roteiro acima.

## Contraste das ações e busca no documento — sexta evolução

Corrigido o conflito em que a regra genérica `.panel-body > .control` removia o fundo de ações primárias e preservava sua letra branca. Ações primárias dos painéis agora conservam fundo carmim, texto branco e contraste nos estados normal, hover e foco. A correção abrange guardar notas gerais e notas sobre trechos.

A Mesa ganhou **Buscar** no cabeçalho dos documentos. O painel oferece busca literal de palavras/frases, idioma, diferenciação de maiúsculas/minúsculas, contagem, contexto dos resultados e navegação Anterior/Próxima (Enter/Shift+Enter). A consulta acompanha o material na sessão. O mesmo botão recolhe o painel.

A busca examina apenas os idiomas presentes na visualização atual, incluindo traduções recolhidas no estudo por trecho; ao navegar para uma delas, abre a tradução. Ela não é uma busca transversal em todas as edições do acervo. Para mudar o corpus examinado, altere o idioma principal/secundário ou a atividade. No editor, permanece a busca própria do CodeMirror.

Limites: mínimo de dois caracteres, até 500 ocorrências com aviso para refinar a consulta, lista de resultados apresentada em grupos de 40. Caracteres como colchetes e pontos são literais, não comandos de expressão regular. CSS Highlights realça as ocorrências sem alterar o texto; seleção nativa é a alternativa para a ocorrência atual em navegadores sem a API.

Teste curto:

1. Atualize com Ctrl+Shift+R. Abra Notas e confira o botão carmim **Guardar nota geral** antes de passar o mouse. Selecione uma frase, use Anotar trecho e confira **Guardar nota deste trecho**.
2. Abra um documento e clique **Buscar**. Digite um nome/palavra presente no texto. Confira contagem e destaque; use Próxima/Anterior ou Enter/Shift+Enter.
3. No estudo por trecho, busque uma palavra presente na tradução recolhida; escolha o idioma secundário no filtro e clique no resultado. A tradução deve abrir no lugar da ocorrência.
4. Clique em Buscar novamente ou Escape para recolher. Reabra e confira a consulta. Teste também um termo inexistente.

Verificações: sintaxe dos módulos; busca literal e sensibilidade de caixa em russo, metacaracteres, limites, offsets UTF-16 e recuperação da consulta; testes auxiliares anteriores mantidos. Aparência e interação exigem conferência manual no navegador. Sem mudança no acervo, commit ou push.

## Busca em traduções recolhidas — esclarecimento do percurso

O filtro agora distingue **Texto principal · idioma** de **Tradução por trecho · idioma**. Cada resultado informa se pertence a uma tradução aberta ou recolhida e exibe **Abrir tradução e mostrar ocorrência** quando necessário. Digitar a consulta não expande traduções automaticamente: a abertura ocorre ao clicar no resultado ou navegar até ele. Isso torna o efeito observável e preserva a organização da leitura durante a busca.

Teste reproduzível: abra 1665, escolha russo, Estudo por trecho e inglês como segundo idioma. Recolha a tradução que contém a resposta sobre o cartão de filiação partidária, se já estiver aberta. Em Buscar, escolha Tradução por trecho · English e procure `membership card`. Clique no resultado identificado como Tradução recolhida: a tradução deve expandir na própria página, com a expressão localizada. Nada é traduzido, importado ou editado por esta ação.

Próximas entregas imediatas propostas: integrar consulta de texto e fac-símile no mesmo espaço de trabalho; depois conectar edição/importação ao backend existente com prévia, efeito da gravação explícito e histórico real, mantendo as funções oficiais disponíveis durante a transição. São propostas de sequência, não funcionalidades já implementadas neste ajuste.

Sintaxe e verificações auxiliares passaram. Sem commit ou push.

## Texto + fac-símile e gravação editorial real — sétima evolução

### Mudança de capacidade

O piloto detecta o backend editorial local. Na Mesa principal, **Editar Markdown** oferece dois destinos explícitos:

- **Conferir rascunho da sessão:** mantém o arquivo do acervo intacto.
- **Conferir gravação no acervo:** prepara uma transação real do backend. A gravação só ocorre após **Confirmar e gravar no acervo local** e a confirmação marcada na prévia.

O Caderno experimental continua restrito aos rascunhos. Em hospedagem estática não são habilitadas as operações canônicas. Nada publica no GitHub, faz commit ou push. Os controles principais ficam indisponíveis enquanto uma gravação está em andamento.

Foram reutilizados token, revisão do catálogo, SHA da edição, prévias, limites, verificação de conflitos e histórico do backend. Não há implementação paralela de transações. Após salvar, o catálogo e o manifesto são recarregados, o cache textual é limpo e o documento volta à atividade anterior. A busca é atualizada pela transação do backend existente. Rascunhos de outras versões não são apagados; quando houver um rascunho da sessão, o menu permite escolher entre mostrar o rascunho e a versão do acervo.

### Teste 1: fonte e texto na mesma aba

1. Reinicie `python3 -m backend` para carregar o novo recurso do piloto. Atualize com Ctrl+Shift+R.
2. Procure **8687** na Biblioteca e abra o documento.
3. No seletor de atividade, escolha **Texto + fac-símile**. Também há acesso em ⋯ → Consultar texto + fac-símile.
4. Confira texto de um lado e imagem do outro. Mude página, ajuste à largura e teste Tela cheia; Escape retorna. Quando houver várias fontes, troque pelo seletor da fonte.
5. Leia Sobre a fonte. A página da imagem não certifica correspondência exata com o parágrafo do texto. Troque para Leitura e retorne: página e posição devem permanecer.

### Teste 2: edição e recuperação reais

1. Na Mesa principal, abra uma tradução Markdown e escolha **Editar Markdown**.
2. Faça uma pequena alteração e clique **Conferir gravação no acervo**. Confira as duas versões e diferenças. **Voltar sem gravar no acervo** deve preservar o rascunho, sem modificar o arquivo.
3. Para testar o ciclo real, prepare novamente, marque a confirmação e clique **Confirmar e gravar no acervo local**. Agora o arquivo é de fato alterado e o leitor é atualizado. Use uma correção legítima ou restaure o teste no passo seguinte.
4. Em ⋯ → **Histórico do acervo local**, escolha o registro da edição e **Conferir restauração**. Revise e confirme para recuperar a versão anterior. A restauração cria outro registro; não apaga o histórico.

A lista apresenta restaurações de transações individuais do documento. Operações de lote ou coleção continuam no Estúdio oficial, evitando apresentar restauração de vários documentos como se afetasse apenas um.

### Teste 3: importar uma tradução individual

1. Abra explicitamente o documento que receberá a tradução. Escolha **Importar tradução** no seletor de atividade.
2. Confira ID e título do documento. Selecione português ou inglês entre os idiomas permitidos, escolha seu Markdown e, se necessário, preencha o título traduzido.
3. Clique **Conferir importação no acervo**. A prévia mostra diferenças, identificação, avisos e diagnóstico de estrutura. O pareamento não é imposto automaticamente.
4. Divergências exigem leitura e confirmação adicional. Cancele para voltar sem gravar, ou confirme para atualizar o acervo local com histórico. Uma tradução existente é substituída com preservação da versão anterior no histórico.
5. Um arquivo idêntico à versão existente pode gerar “Nenhuma alteração para salvar”: isso é esperado.

O modo **Importar corpus** da Biblioteca continua sendo proposta da sessão. Ele não deve ser confundido com a nova importação individual real, contextualizada por documento. Catálogo e criação de coleções ainda não foram conectados à gravação real nesta interface.

### Verificação

Sintaxe dos cinco módulos e verificações auxiliares passaram, incluindo preservação de revisão/SHA/cabeçalhos e recuperação da consulta pareada sem serialização de objetos PDF. Seis testes HTTP e editoriais passaram em acervo temporário: recursos privados bloqueados, rotas oficiais preservadas, prévia sem escrita, edição/gravação/restauração, busca atualizada, exigência de confirmação de divergência e importação/restauração mantendo o original russo. Nenhum documento real foi alterado por esses testes.

A aparência, o PDF lado a lado e os formulários exigem a validação manual acima. Sem commit ou push.

## Proveniência visível, conferência e teclado global — oitava evolução

### Transcrição e fac-símile são fontes distintas

O cabeçalho da leitura exibe caminhos de coleção/subcoleção com acesso de retorno ao catálogo contextual. Exibe também **Fonte da transcrição** com o endereço cadastrado. O painel do PDF mantém o título de sua fonte, um aviso quando se trata de edição publicada em vez de imagem arquivística original e o link **Origem do PDF**. A nota completa permanece em Sobre a fonte.

Exemplo conferido no registro local do documento **8687**:

- Coleção: Processo de 2–12 de março de 1938 → Bukharin.
- Transcrição: coletada do ShowTrials.
- PDF: revista Вопросы истории / Voprosy istorii, 1992, nº 2–3, obtida no repositório publ.lib.ru; as 195 páginas originais foram preservadas.
- Carta de Bukharin de 20/2/1937: páginas físicas 6–7; nota relacionada na página 44.
- Proveniência: `data/facsimiles.json`, vínculo `assistente-edicao8687-8687-voprosy1992-02-03`.
- Limite: testemunho textual dos trechos examinados, não reprodução direta das folhas RGASPI. As marcas do comentário “Вранье” e autenticação arquivística não foram certificadas nesta edição. O candidato arquivístico 61777 continua não recuperado. Não se deve chamar a edição publicada de cópia arquivística original.

### Ajustes de espaço

A importação individual tem rolagem própria dentro da área de trabalho. O aviso vermelho foi removido da coluna de prévia do editor Markdown; uma indicação curta e discreta aparece nos controles, sem deslocar o texto em relação ao editor.

A conferência foi reconstruída como superfície com abas:

- **Conteúdo:** versões anterior/proposta lado a lado; Markdown renderizado ou corpo textual.
- **Diferenças:** diff em área central dedicada, sem comprimir as versões.
- **Identificação:** quando há importação, avisos e tabela de estrutura do original, versão atual e arquivo enviado.
- **Efeito da gravação:** destino, arquivos e alterações técnicas, separados do conteúdo.

A confirmação fica num rodapé próprio, sempre separado da área de comparação. Não há o antigo dropdown “Ver diferenças e arquivos afetados” empilhado acima do texto. Avisos e confirmação permanecem obrigatórios, mesmo ao alternar abas; a lógica de transação do backend não foi alterada.

### Teclado russo em campos do site

O botão **Я** do cabeçalho abre um teclado russo auxiliar para o campo de texto ativo. Funciona em buscas, metadados, notas, importação e editor CodeMirror. O cabeçalho do teclado informa seu destino. Clique primeiro no campo ou, com o teclado aberto, escolha outro campo. A tecla ⇪ alterna maiúsculas. Recolher ou Escape fecha o teclado.

O teclado reserva altura na área de trabalho; painéis, diálogos e revisão se ajustam para não deixar os comandos escondidos. Não digita em campos somente leitura ou desabilitados. No CodeMirror a inserção usa as transações do editor, preservando seu estado e desfazer; em campos comuns usa seleção/inserção nativas. O teclado local de transcrição de PDF continua disponível, mas abrir o global recolhe o local para evitar duplicação.

### Conferência manual curta

1. Atualize com Ctrl+Shift+R. Abra 8687 e confira coleção, subcoleção e Fonte da transcrição; em Texto + fac-símile, confira a distinção de fonte publicada e Origem do PDF.
2. Abra Importar tradução, reduza a altura da janela e role até o comando de conferir. Prepare uma prévia dos arquivos 4801, se necessário, sem confirmar gravação.
3. Na prévia, alterne Conteúdo, Diferenças, Identificação e Efeito da gravação. Confira que a confirmação não desaparece ao rolar o conteúdo. Cancele para retornar com o arquivo preparado.
4. Abra Editar Markdown e confira que a coluna de prévia não começa mais com uma tarja vermelha. Prepare e cancele uma edição para avaliar o mesmo desenho de conferência.
5. Clique na busca da Biblioteca, abra Я e escreva um nome russo. Repita no campo Autoria do catálogo e no editor Markdown. Confira maiúsculas, seleção, apagar e recolher. Não é necessário confirmar nenhuma gravação para testar o teclado.

Sintaxe, referências locais e testes auxiliares passaram. As mudanças desta evolução são de apresentação/interação; não foi executada nenhuma gravação no acervo real. A aparência e as interações de teclado/rolagem precisam da conferência manual acima. Sem commit ou push.

Próximos passos imediatos propostos: conectar catálogo, metadados e coleções/subcoleções à gravação real com o mesmo padrão de prévia/histórico; em seguida portar o fluxo existente de fonte PDF → OCR → revisão → incorporação, preservando as ferramentas oficiais durante a transição.

## Teclado pop-up e conferência única — nona evolução

O teclado auxiliar deixou de reservar altura. Ao focar um campo editável, surge um botão **Я** fixo no canto inferior direito da tela, independente da rolagem e do cabeçalho da página. Ele abre uma janela flutuante; arraste pelo cabeçalho para mudar sua posição, use Recolher ou Escape para fechar. A janela mantém o campo de destino identificado e preserva a inserção por seleção e as transações do CodeMirror. Não há redimensionamento da página ao abrir o teclado. O teclado local da revisão PDF continua disponível; abrir o global recolhe o local.

No editor Markdown, os dois botões concorrentes foram substituídos por **Conferir alterações**. Na conferência, o seletor **Destino** permite escolher:

- **Rascunho da sessão**: cópia temporária no navegador; não altera o arquivo do acervo. É a opção inicial.
- **Acervo local · gravação com histórico**: prepara uma prévia real do backend e só grava depois da confirmação explícita. A opção só aparece com backend local disponível e Mesa principal ativa.

Trocar para Acervo local prepara revisão/SHA/diferenças com o backend, sem gravar. Ao voltar para Rascunho, a proposta da sessão permanece. A identificação do destino, o rodapé de confirmação e os avisos obrigatórios se ajustam à escolha. Importação de tradução e restauração pelo histórico continuam com seu destino real explícito; não são convertidas em salvamento temporário.

Teste curto atualizado:

1. Clique numa busca ou campo de metadados. Abra **Я** no canto inferior direito, arraste a janela, role a página e teste letras/maiúsculas. O teclado não deve alterar a altura da página nem desaparecer junto ao cabeçalho. Recolha e reabra.
2. Abra Editar Markdown, faça uma pequena alteração e clique **Conferir alterações**. O destino inicial é Rascunho da sessão. Troque para Acervo local: o backend prepara a prévia, sem gravar. Volte para Rascunho e confira que o texto continua igual.
3. Cancele para retornar sem gravar, ou confirme o destino escolhido. A mensagem e o botão devem distinguir claramente gravação na sessão de gravação no acervo.

Sintaxe e verificações auxiliares passaram. Pop-up, arraste, foco e escolha do destino precisam de conferência manual no navegador. Sem alterações no acervo real, commit ou push nesta evolução.

## Catálogo e coleções com gravação real — décima evolução

O catálogo do piloto foi conectado ao backend existente. O navegador à esquerda oferece pesquisa e paginação; a ficha à direita usa três seções: **Ficha**, **Data e referência**, **Coleções**. É possível editar títulos nos três idiomas, categoria, tipo documental, autoria, data histórica, referência arquivística e associações. Idioma/arquivo do original, textos e URLs de fonte não são modificados por essa ficha.

A data de exibição é separada da data normalizada e sua precisão; a data de coleta não é promovida a data histórica. As associações podem incluir várias coleções/subcoleções. Marcar uma subcoleção marca a principal; retirar a principal retira suas subcoleções. O backend mantém a ordem das associações existentes e acrescenta as novas ao fim.

**Conferir alterações** abre uma comparação de propriedades, não um bloco de JSON na coluna de leitura. O destino inicial é a sessão; com backend e Mesa principal, o seletor permite preparar e confirmar a gravação real no acervo. Prévia não grava. Após confirmar, catálogo/manifesto/busca são atualizados pelo backend, e a ficha é recarregada. Preenchimentos ainda não confirmados ficam identificados como recuperados da sessão; o botão **Usar ficha do acervo** permite descartá-los explicitamente e carregar o estado canônico. Rascunhos antigos de metadados são migrados uma vez para o novo preenchimento, sem gravação automática.

### Coleções e subcoleções

A entrada **Coleções** na Biblioteca e **Coleções e subcoleções** no menu/catálogo abrem o gerenciamento. Há busca, edição e criação de subcoleções a partir da coleção principal. **Nova coleção** abre um cadastro próprio, dividido em Identidade e Apresentação e fonte.

Coleções novas recebem identificador sugerido pelo título, editável antes de salvar. Em coleções existentes, identificador e coleção principal são bloqueados tanto na interface quanto na construção do pedido e no backend, preservando URLs. Capa é opcional e deve ser uma imagem já existente em assets/covers/. Não há upload de capa nesta etapa.

A criação/edição de coleção exige Mesa principal e backend. Preparar mostra a comparação; confirmar cria a transação com histórico. A tela de edição oferece **Histórico da coleção**; restaurar exige outra prévia e cria novo registro. Se uma criação for restaurada, o retorno é à lista de coleções. Restaurações incompatíveis com alterações posteriores são recusadas pelo backend: deve-se reverter primeiro a operação mais recente que modificou aqueles arquivos.

### Teste manual curto

1. Reinicie `python3 -m backend` e atualize o piloto com Ctrl+Shift+R: o servidor precisa carregar a permissão do novo módulo organization.js.
2. Abra **Catálogo**, busque 4801 e selecione sua ficha. Alterne Ficha, Data e referência e Coleções. Altere um título, clique Conferir alterações e confira a tabela. Troque Destino para Acervo local e **cancele** para validar a prévia sem modificar o acervo.
3. Volte à ficha, marque uma subcoleção e confira que a principal é incluída. Desmarque a principal e confira as filhas. Não confirme associações de teste que não deseja manter; use Usar ficha do acervo para descartar o preenchimento em andamento.
4. Abra **Coleções**, escolha uma existente e clique Editar. Confira os identificadores bloqueados. Altere a apresentação, prepare a prévia e cancele, ou confirme uma correção legítima.
5. Use **Nova coleção** e **Nova subcoleção**, preencha título e apresentação e prepare a prévia. Cancele para evitar cadastrar material de teste. Se quiser testar a gravação, o histórico permite restaurar; reverta primeiro edições posteriores/subcoleções e depois a criação da principal.
6. Em uma alteração real, consulte Histórico do documento/Histórico da coleção e confira uma restauração. Esse fluxo nunca modifica os textos originais por editar uma ficha ou coleção.

### Validação

Oito testes HTTP/editoriais passaram em acervo temporário: prévia sem escrita; metadados e múltiplas associações; fonte/arquivos preservados; atualização de busca; criação de coleção e subcoleção; edição com ID estável; recusa de mudança de URL; restauração em ordem inversa. Os testes anteriores de edição/importação Markdown e recursos privados também passaram. Auxiliares de construção de pedidos e sintaxe dos seis módulos passaram. A navegação visual requer conferência manual.

Não foram criadas coleções nem alterados metadados no acervo real durante a implementação. A interface oficial continua preservada. Sem commit ou push. A próxima entrega proposta permanece o fluxo PDF → OCR → revisão → incorporação nesta interface.

## Fontes PDF, OCR e incorporação — décima primeira evolução

### Percurso e destinos

A Biblioteca e o menu oferecem **Fontes PDF**. Este percurso usa o backend real, sem projeto ativo. **PDF temporário** continua disponível para consulta sem cadastro; se o arquivo estiver aberto assim, Ferramentas oferece Cadastrar esta fonte para OCR.

1. **Cadastrar PDF:** confirma uma cópia local preservada por SHA-256. PDFs idênticos reutilizam a fonte já existente. O inventário e a extração de texto pesquisável começam automaticamente; não é preciso dividir páginas antes. Cadastrar fonte não cria documento nem publica PDF.
2. **Revisar página:** imagem e transcrição permanecem lado a lado. A área mostra texto nativo quando disponível; o OCR não substitui a revisão automaticamente. O seletor de base permite adotar um candidato e voltar à extração nativa. A adoção de candidato redefine o estado para Pendente. O rascunho anterior pode ser baixado quando preservado na sessão.
3. **Salvar revisão:** escolha o estado da página (Pendente, Conferida, Com problema ou Em branco), use Conferir página, confira o texto e confirme Salvar revisão da página. A revisão vai ao banco local com histórico; PDF e extração bruta permanecem intactos. Não altera um documento já incorporado.
4. **Criar documento:** em Ferramentas → Criar documento das páginas conferidas, escolha título, novo identificador, idioma, páginas, coleção e subcoleção. Somente páginas salvas como Conferida ou Em branco são aceitas. A prévia mostra conteúdo, páginas, fonte e avisos. Confirmar cria um documento novo, atualiza catálogo/manifesto/busca e registra proveniência por página e unidades textuais. Não substitui outro documento.

### OCR

Ferramentas → Configurar OCR oferece páginas físicas, russo/inglês/português (somente os modelos instalados são habilitados), 150/200/300 DPI e segmentação automática ou bloco único. O backend permite até 50 páginas por lote. Conferir prepara a receita; Executar OCR local enfileira o trabalho. Os candidatos são separados da transcrição revisada.

O painel Processamento OCR mostra estado e progresso; lotes falhos/interrompidos podem ser retomados. Enquanto a fonte está aberta, inventário e OCR em andamento são consultados periodicamente sem substituir o texto em edição. Fechar ou mudar de material interrompe apenas a consulta do frontend, não os trabalhos do backend. Não são feitas chamadas de instalação automática de dependências.

A ficha da fonte permite guardar título, idioma, coleção/subcoleção, URL e referência com confirmação e histórico. Foliação e notas da página entram na mesma gravação da revisão. Há histórico da página com restauração por prévia. Páginas da fonte permite navegar sem perder o rascunho em andamento.

### Recuperação e limites

Rascunhos de página guardam a revisão e o SHA da extração que lhes deram origem. Se a revisão mudou em outra aba, o rascunho antigo não é aplicado silenciosamente: é preservado para download. Abas de fontes locais, página atual e rascunhos acompanham a sessão, sem serializar os arquivos PDF. A revisão confirmada permanece no backend ao encerrar o navegador.

Documentos incorporados / recibos permite conferir operações anteriores e concluir um vínculo pendente sem duplicar o documento. Um recibo conhecido de gravação concluída não é tratado como falha de criação se a atualização visual falhar. O usuário é orientado a recarregar e consultar o recibo, não a repetir a criação.

O documento criado tem acesso local a Texto + fac-símile pelo vínculo do backend. Essas fontes aparecem como **Fonte de trabalho local · PDF ainda não publicado**. O envio para a publicação estática continua separado; não há publicação automática de PDFs privados, nem commit/push. Projetos privados, alinhamento geométrico de parágrafos, processamento avançado de imagem e publicação de fac-símiles não foram portados nesta entrega.

### Teste manual em três etapas

1. Reinicie `python3 -m backend`, atualize o piloto com Ctrl+Shift+R e abra Fontes PDF. Use uma fonte já cadastrada ou Cadastre PDF. Confirme o envio e espere o inventário: a imagem deve aparecer, e páginas pesquisáveis devem receber texto sem executar OCR.
2. Em uma página que precisa de OCR, abra Ferramentas → Configurar OCR. Escolha apenas a página atual e seu idioma; confira e execute. Acompanhe Processamento OCR. Depois selecione o candidato no seletor acima da transcrição, corrija o texto, marque Conferida e use Conferir página → Salvar revisão da página.
3. Abra Ferramentas → Criar documento das páginas conferidas. Informe novo ID, título, idioma, páginas e coleção/subcoleção. Confira a prévia. Cancele se não quiser criar documento de teste; confirmar realmente cria o documento no acervo local. Depois confira sua leitura e Texto + fac-símile. O PDF ainda é local e não está automaticamente publicado no GitHub.

É possível parar após cada etapa. Fonte PDF e revisões confirmadas permanecem no backend; apenas a incorporação acrescenta um documento ao catálogo. O russo pode ser editado pelo teclado pop-up Я no campo de transcrição.

### Verificações realizadas

Nove testes HTTP/editoriais passaram em acervo temporário. O teste novo gerou um PDF com uma página pesquisável e uma segunda página renderizada como imagem, sem camada textual; confirmou a extração nativa, executou OCR real em inglês com Poppler/Tesseract, verificou que o OCR não substituiu a revisão existente, adotou um candidato e incorporou a página com proveniência/unidades e vínculo. Verificou também recusa de incorporação antes de conferir/salvar e preservação do SHA do PDF e do texto bruto. Nenhuma fonte real do projeto foi cadastrada nem documento real alterado por esses testes.

Os modelos eng, por e rus estavam disponíveis no ambiente consultado; o teste automatizado de reconhecimento foi em inglês. Sintaxe, construção dos pedidos e recuperação de rascunhos passaram. A aparência, navegação, adoção e edição no navegador devem ser conferidas pelo roteiro manual; não foi executado teste visual automatizado. Sem commit ou push.

## Menus, largura/zoom e teclado ajustáveis — décima segunda evolução

Os menus principal, do documento, da fonte temporária e da revisão PDF usam o mesmo componente de grupos e ações. Cada ação tem título, descrição curta e indicação de navegação/exportação. O menu principal agrupa Abrir materiais, Organizar acervo, Retomar trabalho e Ajuda, com filtro de ações. Submenus ganham **‹ Voltar**, preservando os campos, filtros e rolagem do painel anterior. X ou o acionador correspondente recolhe o painel inteiro. Formulários de ferramentas e botões de confirmação mantêm seus controles próprios.

Texto + fac-símile, PDF temporário e revisão persistente têm uma divisória arrastável. A divisão ajusta a largura de cada área sem recarregar documento, página ou transcrição. Duplo clique centraliza em 50%; a divisória também aceita teclado (setas, Shift para passos maiores e Home para centralizar). Em telas estreitas, ajusta alturas em vez de larguras. A preferência é guardada por material na sessão.

O zoom da imagem oferece Página inteira, Ajustar à largura, porcentagens de 50% a 300% e botões −/+. Atua somente na imagem renderizada; não muda o PDF original nem o texto. A renderização tem limite de pixels para evitar uso excessivo de memória em páginas grandes. O painel permite rolagem horizontal quando a imagem ampliada excede a largura, sem perder a margem esquerda. Os controles não ficam sobre a imagem.

O teclado ganhou novamente **Я na barra superior**, além do acesso fixo no canto da tela. O botão flutuante pode ser arrastado: movimento reposiciona, clique abre/recolhe. A janela do teclado continua móvel pelo cabeçalho e agora é redimensionável pelo canto inferior direito. Teclas se adaptam à área disponível. O teclado não reserva altura nem altera a rolagem da página; os dois acessos controlam a mesma janela e o mesmo campo ativo.

Teste manual:

| Recurso | Ação | Resultado esperado |
|---|---|---|
| Menu | Abra ☰, filtre uma ação e entre em Abrir documento; use ‹ Voltar. | Grupos legíveis; filtro anterior preservado; sem sair da Mesa. |
| Outros menus | Abra ⋯ do documento e Ferramentas de uma fonte PDF. | Mesmo padrão de ações e navegação de retorno. |
| Largura | Em Texto + fac-símile ou revisão PDF, arraste a divisória; dê duplo clique. | Áreas mudam de tamanho sem perder a página/texto; duplo clique centraliza. |
| Zoom | Escolha 150%, use −/+ e depois Ajustar à largura. | Só a imagem muda de escala; texto e transcrição permanecem. |
| Acessos ao teclado | Abra Я no cabeçalho; arraste o atalho flutuante e clique nele. | Os dois controlam o mesmo teclado; arrastar não abre/fecha acidentalmente. |
| Tamanho do teclado | Arraste seu cabeçalho e depois o canto inferior direito. | Janela muda de posição/tamanho, sem alterar a rolagem da página. |

Reinicie o backend para carregar controls.js e atualize com Ctrl+Shift+R. Sintaxe e auxiliares de limites/preferências passaram, assim como dois testes HTTP direcionados aos recursos e à entrada do piloto em acervo temporário. Não se repetiu processamento OCR, pois não houve alteração do motor ou das transações. A validação visual/interação é manual. Sem alterações no acervo, commit ou push.

## Uma Mesa, várias abas — décima terceira evolução

O número junto a “Mesa” contava materiais abertos, mas podia ser confundido com o identificador de outra mesa. Ele foi retirado da navegação principal. A Mesa continua sendo uma única área de trabalho: cada documento/PDF acrescenta uma aba, não uma mesa nova.

A faixa de abas é mostrada mesmo com um só material. Cada aba tem título, estado ativo, indicação de alterações pendentes quando houver e **× para fechar**. O seletor **Abas abertas (N)** fica na própria faixa, independente da quantidade de controles do cabeçalho, e lista todos os documentos/fontes da mesma Mesa. Ele permite alternar quando não há espaço para mostrar todas as abas. O título completo e a identificação ficam disponíveis no seletor/descrição acessível.

Ao fechar a aba ativa, um material vizinho é selecionado. Fechar a última deixa a Mesa vazia; não cria outra mesa. Alterações ainda não confirmadas exigem confirmação para descarte. Revisões gravadas na sessão ou backend permanecem preservadas.

Teste curto:

1. Atualize com Ctrl+Shift+R e abra 1665: uma aba com × deve aparecer abaixo do cabeçalho.
2. Abra 8687 pela Biblioteca ou ☰ → Abrir documento. As duas abas devem estar na mesma faixa.
3. Alterne clicando nos títulos e pelo seletor Abas abertas (2). Confira que posição/atividade de cada material é preservada.
4. Feche uma aba pelo ×; a outra permanece. Feche a última: a Mesa fica vazia.

Esta mudança não implementa múltiplas mesas/projetos independentes; esclarece a alternância de materiais na Mesa atual. Sintaxe e auxiliares passaram; conferir disposição e interação no navegador. Sem commit ou push.

## Preparação de fontes e decisão sobre BookReader — décima quarta evolução

O BookReader não será portado para o piloto nesta entrega. A navegação por página, zoom e divisão redimensionável de imagem/transcrição já atendem à conferência sem outro conjunto de comandos. A implementação anterior permanece preservada. Sua eventual volta será avaliada para consulta contínua de volumes, se esse uso exigir recursos ausentes no visualizador atual.

Ferramentas de uma fonte PDF agora oferece extração de páginas, divisão por quantidade ou intervalos e consulta dos derivados/processamentos. São usados os serviços existentes, com prévia, confirmação, registro de origem e preservação do PDF original. Fontes idênticas podem ser deduplicadas. O andamento dos derivados é atualizado pelo comando da lista.

Preparar imagem gera uma cópia PNG da página com receita restrita: cinza, contraste normalizado, limiar, escala e erosão. Permite comparar Original/Tratada e baixar PNG/receita. A receita e o resultado ficam identificados pela fonte, SHA-256, página, DPI e versão do motor. O original não muda. Recorte e rotação ficam de fora por exigirem transformação adicional das coordenadas de citação.

O OCR permite selecionar explicitamente o tratamento preparado, no mesmo DPI. A receita se aplica a todas as páginas escolhidas naquele lote. O resultado continua sendo um candidato: não substitui transcrição conferida automaticamente. O histórico de revisão e a incorporação permanecem com confirmação. Os derivados de imagem são privados do backend; não se tornam publicação estática.

Reinicie `python3 -m backend`, abra `/prototipo/mesa/` e atualize com Ctrl+Shift+R (versão v17). Use uma fonte PDF cadastrada; o PDF temporário do navegador não oferece essas operações persistentes. Arquivo pequeno disponível: `temporario/teste-pdf-ocr/tukhachevsky-paginas-004-005.ru.pdf`, duas páginas sem camada textual.

| Teste | Caminho e ação | Resultado esperado |
|---|---|---|
| Extrair | Fontes PDF → abrir fonte → Ferramentas → Extrair ou dividir PDF; extrair página 1, conferir e confirmar. | Em Derivados e processamento, atualizar e abrir o resultado de uma página; original mantém duas. |
| Dividir | Na mesma ferramenta, dividir a cada 1 página e confirmar. | Duas partes com vínculo às páginas de origem; original preservado. |
| Imagem | Preparar imagem → cinza/contraste, gerar prévia; alternar Original/Tratada. | Página tratada aparece na mesma área, com zoom e divisão; PNG e receita disponíveis para download. |
| OCR tratado | Configurar OCR → marcar Usar o tratamento preparado → escolher página e russo → conferir e executar. | Prévia identifica receita e DPI; candidato aparece sem apagar revisão salva. Conferir antes de adotar/salvar. |

Validação automatizada em acervo temporário: 12 testes passaram, incluindo ImageMagick, Poppler, OCR real em inglês, histórico, incorporação e extração/divisão. Sintaxe Python/JS e auxiliares passaram. A interação visual deve ser validada no navegador; OCR russo/português deve ser conferido pelo editor. Nenhum texto/fonte do acervo de produção foi alterado por esta entrega. Sem commit ou push.

## Acesso aos derivados e teste de imagem — ajuste v18

A faixa de abas aparece somente em `#mesa`, preservando os materiais ao navegar pela Biblioteca. A geração de PDFs abre automaticamente Derivados e processamento na fonte original; a lista acompanha operações ativas a cada 2,5 segundos enquanto visível e oferece Abrir derivado por parte cadastrada. O comando PDFs derivados na barra da fonte reabre essa lista. O resultado abre como outra aba, mantendo o original disponível.

O tratamento usa Poppler para renderizar a página e ImageMagick no backend para transformar o PNG; Tesseract faz o OCR quando solicitado. Não altera PDF ou transcrição.

Teste preciso: abrir fonte → Ferramentas → Preparar imagem → marcar cinza e contraste → Preparar e visualizar imagem. Alternar Original/Tratada na barra da imagem. Para uma mudança mais evidente, voltar à preparação e ativar limiar 160; gerar novamente. Limiar pode piorar letras: é uma opção para comparação, não uma melhoria garantida. Para reconhecer essa imagem, Ferramentas → Configurar OCR → marcar Usar o tratamento preparado → selecionar página/idioma → conferir e executar. Adotar o candidato e salvar revisão são decisões separadas.

Atualizar o navegador com Ctrl+Shift+R (v18). Sintaxe dos módulos alterados conferida; interação visual pendente de validação manual. Sem commit ou push.

## Importação real por corpus — décima quinta evolução (v19)

A importação demonstrativa foi substituída pelo fluxo guiado do backend existente, sem exigir CSV. São três etapas: Contexto; Arquivos e versões; Conferência. Aceita um documento isolado ou conjunto de até 100 arquivos (4 MiB por arquivo, 20 MiB no total), em UTF-8, Markdown/TXT. Coleção e subcoleção são selecionadas separadamente. Metadados compartilhados devem ser preenchidos apenas quando valerem para todos os documentos do corpus. O idioma original sugerido orienta a associação inicial, mas papel e idioma de cada arquivo podem ser corrigidos explicitamente.

Os nomes/cabeçalhos sugerem ID e idioma; o editor confirma título, ID, idioma e papel. Um ID agrupa exatamente um original e suas traduções em idiomas distintos. IDs já cadastrados são bloqueados: atualizar traduções existentes continua sendo ação do documento. Arquivos repetidos, versões órfãs e idiomas repetidos são indicados antes da prévia. O backend valida novamente os dados, aponta divergências e mantém a proteção contra sobrescrita de arquivos.

A prévia permite selecionar e ler cada arquivo renderizado, consultar metadados e avisos em Informações e verificar Efeito da gravação. Avisos exigem confirmação adicional explícita. Não há alinhamento automático: traduções são cadastradas como versões de trabalho. Confirmar cria documentos/versões e atualiza catálogo, manifesto, busca e fila de revisão na transação existente. URLs e textos existentes são preservados. Salvar não faz commit, push ou publicação automática.

Após salvar, a importação oferece abrir documentos e acessar o histórico do lote. A reversão também exige prévia e confirmação, e o backend recusa restaurar quando há alterações posteriores conflitantes. A recuperação de um lote é coletiva, não restauração individual de um de seus documentos.

Metadados compartilhados permanecem na sessão. O conteúdo selecionado fica somente em memória até recarregar a página; navegar entre atividades ou cancelar a prévia mantém a seleção enquanto a página não for recarregada. Exportar proposta baixa JSON com os textos e associações para guarda externa; não implementa reimportação desse JSON. O uso sem backend permite preparar/exportar, mas não cadastrar. O contexto experimental continua sem gravação no acervo.

### Conferência manual

Reinicie o backend para liberar o módulo novo, abra `/prototipo/mesa/` e use Ctrl+Shift+R. Pela Biblioteca, clique Importar corpus. Material opcional: `temporario/teste-corpus-mesa-v19/`; selecione apenas os três arquivos `teste-corpus-mesa-20261114.*.md`. São fictícios, não documentos históricos.

| Etapa | Ação | Resultado esperado |
|---|---|---|
| Contexto | Escolher uma coleção de teste e idioma original russo. Fonte: Teste de interface — material fictício. | Subcoleções pertencem à coleção escolhida; campos compartilhados opcionais. |
| Arquivos | Selecionar os três arquivos .ru.md, .pt.md e .en.md. | Um ID comum, original russo e traduções portuguesa e inglesa. É possível corrigir cada associação. |
| Bloqueios | Temporariamente marcar a tradução como original; ir a Conferência. Depois corrigir. | Aponta dois originais no mesmo documento e impede gerar prévia. |
| Prévia | Gerar prévia, alternar entre os três arquivos e abrir Informações. Voltar sem gravar. | Textos renderizados; avisos legíveis; seleção mantida e nada cadastrado. |
| Gravar | Gerar nova prévia e confirmar os avisos e cadastro. Abrir o documento pelo recibo. | Um documento com três idiomas no catálogo; busca atualizada. |
| Recuperar | Sem outras edições no acervo, voltar a Importar corpus → Histórico / conferir reversão do lote. Conferir e confirmar. | Documento de teste sai do catálogo; histórico preservado. A coleção de teste, se criada separadamente, permanece. |

Validação: auxiliares de associação e preservação do conteúdo passaram; testes HTTP reais passaram para cadastro de dois documentos/uma tradução, busca, proteção de ID existente, consulta do histórico e reversão integral. O módulo novo é servido pelo backend; arquivos de trabalho permanecem privados. Sintaxe dos módulos conferida. Não foram executados testes de navegador, nem gravações no acervo de produção. Sem commit ou push.

### Ajuste de clareza e estilo da importação (v20)

As etapas Contexto / Arquivos e versões / Conferência receberam estilo específico que prevalece sobre `.control`: faixa segmentada, etapa ativa em carmim e estados de foco/hover. O recibo agora apresenta Consultar histórico da importação como consulta opcional, sem sugerir que desfazer seja continuação do cadastro.

Abrir o histórico não grava nada. Desfazer importação prepara uma prévia que nomeia os documentos que sairão do acervo, informa a retirada de catálogo/busca/coleções e dos arquivos cadastrados, e explica que a cópia fica recuperável no histórico. A confirmação final é Retirar lote do acervo, com declaração explícita do efeito. Desfazer uma reversão mostra Repor documentos quando esse for o efeito da operação. Não se alterou o contrato ou a proteção de conflitos do backend.

Teste visual: Ctrl+Shift+R; conferir as três etapas e consultar o histórico de um lote. Abrir a prévia de desfazer e cancelar deve manter o cadastro. Só confirmar Retirar lote do acervo o desfaz. Não é necessário desfazer lotes para usar o importador. Sem gravações no acervo durante este ajuste, commit ou push.

## Fila de revisão na Mesa — décima sexta evolução (v21)

A fila real foi portada para a nova interface, usando os contratos existentes. Entrada: ☰ → Organizar acervo → Fila de revisão. No menu Documento e ferramentas do texto, Pendências deste documento abre a mesma fila com o ID preenchido e filtros de situação em aberto. A seleção não abre outra aba de navegador nem fecha os materiais da Mesa.

A lista tem busca por título/ID/motivo/notas, filtros de situação, prioridade e coleção/subcoleção, paginação de 25 pendências e ordenação por prioridade do backend. Filtros e seleção acompanham a sessão. Cada pendência mostra motivo e ação sugerida, além dos campos editáveis de situação, prioridade, diagnóstico/dificuldade e notas da revisão. Texto e ficha permanecem acessíveis; Histórico do documento inclui as operações individuais do documento, não apenas mudanças da fila.

Conferir registro da revisão prepara uma transação sem gravar. Confirmar altera somente a pendência, com histórico. Marcar Corrigido NÃO muda o Markdown, não traduz e não certifica fac-símiles automaticamente. Cancelar a prévia mantém o rascunho. Rascunhos editados são guardados na sessão; alterações externas de revisão exigem recarregar a ficha antes de gravar, com opção de exportar o rascunho. Recarregar ficha descarta o rascunho somente após confirmação quando houver mudanças. Uma pendência salva como corrigida desaparece naturalmente do filtro Em aberto e permanece no filtro Corrigido/Todas as situações.

### Teste manual curto

Reinicie o backend, abra `/prototipo/mesa/` e atualize com Ctrl+Shift+R (v21).

| Teste | Ação | Resultado esperado |
|---|---|---|
| Consultar | ☰ → Organizar acervo → Fila de revisão. Buscar por um ID, motivo ou nome. Abrir Filtros de revisão. | Resultados paginados com prioridade, situação e motivo; filtros combinados. Limpar filtros volta aos casos em aberto. |
| Abrir material | Selecionar uma pendência → Abrir texto. No texto, Documento e ferramentas → Pendências deste documento. | Texto abre na Mesa, materiais anteriores permanecem; retorno mostra as pendências daquele ID. |
| Cancelar | Alterar notas ou situação e clicar Conferir registro da revisão; voltar sem gravar. | Mostra antes/depois e efeito restrito à fila. Rascunho permanece, backend não muda. |
| Gravar | Em um caso de teste, editar uma nota ou mudar para Em revisão, conferir e confirmar. | Registro salvo com histórico; texto e ficha não mudam. |
| Corrigido | Somente se a revisão estiver concluída, marcar Corrigido e confirmar. Depois filtrar por Corrigido ou Todas as situações. | Sai dos casos em aberto e continua consultável; não há correção automática do texto. |
| Recuperar | Selecionar a pendência, abrir Histórico do documento e conferir restauração do registro mais recente da fila. Cancelar ou confirmar deliberadamente. | Prévia mostra a inversão da avaliação. Confirmar restaura a situação/notas anteriores, sem alterar texto. Backend continua recusando conflitos posteriores. |

Verificações concluídas em acervo temporário: filtros por coleção/prioridade/situação, prévia sem gravação, registro, saída dos casos em aberto, consulta dos corrigidos e restauração exata da fila. Texto russo e manifesto permaneceram idênticos. Teste HTTP do módulo servido e auxiliares de payload/sintaxe passaram. Interação visual permanece para validação manual. Nenhum registro real da fila/acervo foi alterado. Sem commit ou push.

### Espaço da ficha de revisão — v22

A lista ocupa uma coluna limitada (até 280px no desktop), deixando a maior parte da largura para a ficha. Cabeçalho e ações foram compactados; motivos e campos de notas ganharam largura, entrelinha e altura. Na vista com lista, a ficha acompanha a rolagem da página em vez de comprimir seu corpo numa janela pequena.

Ampliar ficha oculta temporariamente lista, busca e apresentação da fila e usa a altura disponível para o caso selecionado, com rodapé de ações acessível. Mostrar lista retorna à seleção e aos filtros, sem recarregar o caso ou perder o rascunho. A preferência acompanha a sessão. Contratos, gravação e histórico permanecem iguais. Atualizar com Ctrl+Shift+R e testar os dois comandos enquanto uma nota estiver sendo editada. Sintaxe conferida; ajuste visual, sem novas transações, commit ou push.

## Vínculos de PDF e preparação do portal — décima sétima evolução (v23)

A fonte PDF oferece duas novas ações em Ferramentas → Incorporar e preservar: Vincular a documento existente e Documentos e fac-símiles. Elas usam os serviços de vínculos/publicação já existentes, sem mudar os contratos de gravação, as transcrições ou os originais.

### Três efeitos diferentes

- Vínculo local: associa um documento cadastrado às páginas físicas de um PDF da fonte. Tem prévia, confirmação e histórico próprios. Não copia nem substitui o texto; a associação de páginas é uma afirmação manual do editor, não certificação automática de alinhamento por parágrafo. Notas são locais e não entram na preparação pública.
- Preparação do portal: gera um PDF derivado com somente as páginas escolhidas e o índice estático `data/facsimiles.json`. A prévia ainda é privada e permite baixar o PDF. Só confirmar grava os arquivos do portal na cópia local do projeto. Incluir transcrições de páginas é opcional e requer revisões Conferida/Em branco; não altera a transcrição principal do documento. Notas, histórico e contexto privado não são exportados.
- Publicação remota: depende de commit e push posteriores, autorizados. Nenhuma ação desta entrega executa Git ou disponibiliza sozinha a novidade no GitHub Pages.

Desativar o vínculo afeta o acesso pelo backend, mas não desfaz uma preparação já existente no portal; há comando separado Conferir retirada do portal. A retirada conserva fonte original e vínculo local. O histórico do vínculo restaura uma associação individual; o Histórico dos arquivos do portal restaura TODO o conjunto anterior de fac-símiles, com aviso e prévia de documentos/arquivos que entrarão ou sairão. Essa restauração coletiva pode retirar preparações posteriores de outras fontes.

Documentos e fac-símiles mostra as páginas, situação local, disponibilidade no portal e eventual diferença de revisão. Permite abrir Texto + imagem na mesma Mesa, editar o vínculo e consultar históricos. Ao criar um documento a partir de páginas conferidas, o vínculo existente já aparece nessa lista; não se deve cadastrá-lo novamente. O backend impede duplicar o mesmo par documento/fonte/contexto.

### Numeração e consulta

O leitor conserva a página física original mesmo quando o PDF estático é recortado: página 13 da fonte pode ser página 1 do derivado. O mapa `published_page_map` controla a renderização e os comandos de navegação. Localmente, o backend continua oferecendo o PDF integral; links com mesmo ID não aparecem duplicados por também terem projeção estática. Preparar novamente após editar um vínculo é explícito; não há sincronização automática de alterações privadas com a projeção do portal.

### Teste manual

Reinicie o backend, abra `/prototipo/mesa/` e atualize com Ctrl+Shift+R. Use uma fonte e documento correspondentes ou materiais de teste identificados; não associe um PDF de teste a uma fonte histórica sem conferir.

| Etapa | Ação | Resultado esperado |
|---|---|---|
| Localizar | Fontes PDF → abrir fonte → Ferramentas → Documentos e fac-símiles. | Se já criou documento da revisão, seu vínculo aparece. Abrir texto + imagem conserva a fonte como outra aba. |
| Novo vínculo | Vincular a documento existente → buscar e clicar no documento correto → informar páginas e nota local → Conferir vínculo. | Prévia identifica documento/páginas e afirma que o texto não mudará. Voltar cancela; confirmar cria só o vínculo local. |
| Conferir portal | Na lista de vínculos, Preparar fac-símile para o portal → manter transcrição desmarcada → Preparar prévia dos arquivos. | Pode baixar o PDF da prévia; contém somente páginas selecionadas. Ainda não muda o portal local. |
| Aplicar | Ler o efeito e confirmar Gravar arquivos locais do portal. | Grava PDF selecionado e índice estático com histórico; não executa commit/push. Fonte integral permanece. |
| Ver sem backend (opcional) | Manter backend e iniciar `python3 -m http.server 8001` na raiz; abrir `http://127.0.0.1:8001/prototipo/mesa/`, documento → Texto + fac-símile. | Consulta usa só arquivos preparados. Página física original é conservada mesmo que o derivado tenha uma única página. |
| Retirar (opcional) | Pelo backend, Conferir retirada do portal → ler documentos/arquivos afetados → cancelar ou confirmar deliberadamente. | Confirmar retira somente os arquivos/índice selecionados, preservando fonte e vínculo local. Histórico permite recuperar. |

Validação real em acervo temporário: upload de PDF com duas páginas distintas, criação de vínculo sem substituir texto, preparação privada de uma página, download da prévia, aplicação estática com mapa 2→1 e acesso HTTP ao PDF. Restauração do conjunto anterior e desativação pelo histórico do vínculo passaram. PDF original, Markdown russo e manifesto permaneceram idênticos. Auxiliares conferiram mapeamento de páginas, payloads e não duplicação de vínculo local/público; sintaxe e recurso HTTP do novo módulo passaram. Interação visual segue para avaliação manual. Sem alterações no acervo de produção, commit ou push.

## Projetos reais e versões privadas — décima oitava evolução (v24)

O Caderno experimental foi substituído na seleção principal por projetos reais do backend. O seletor oferece Acervo local (sem projeto), projetos não arquivados e organização/criação de projetos. Também há ☰ → Organizar acervo → Projetos locais. A entrada nova não usa nem ativa automaticamente o último projeto gravado pelo Estúdio. Ao recarregar, inicia sem projeto ativo; abas privadas anteriores permanecem disponíveis para reabertura explícita. Rascunhos antigos do Caderno continuam exportáveis e recuperáveis pela sessão, identificados como legados.

### Organização do projeto

A ficha tem três seções: Ficha, Documentos e Fontes PDF. Nome, descrição, coleção de referência, materiais vinculados e arquivamento usam prévia, confirmação e histórico próprios do serviço existente. A coleção de referência não inclui automaticamente seus documentos. Arquivar conserva dados e versões privadas; consultar materiais arquivados continua possível, mas a gravação é recusada até reabrir o projeto. Desfazer a criação pelo histórico arquiva o projeto em vez de destruir seu conteúdo.

Materiais do projeto é uma lista acionável, não um explorador permanente. Abrir um documento dessa lista cria uma aba contextual com chave documento@projeto. O mesmo documento pode ficar aberto ao lado em sua versão do acervo, sem compartilhar buffers ou rascunhos. Notas novas da sessão usam a chave da aba/contexto; citações de trechos privados indicam o projeto e deixam claro que a URL do acervo é apenas referência do documento, não publicação daquela versão. Marcadores continuam pertencendo ao documento e são localizados por assinatura textual; divergências não são corrigidas automaticamente.

As fontes PDF vinculadas usam a revisão compartilhada do serviço de fontes: abrir uma delas mostra aviso e sai do contexto de versão privada de texto. Esta entrega não cria cópias privadas das revisões OCR por projeto, nem transforma uma revisão de página em alteração de documento público. Uploads e derivados podem ser cadastrados pelo fluxo de fontes e vinculados explicitamente na ficha do projeto; não há associação automática nesta interface.

### Edição, importação e promoção

Na aba do projeto, Editar Markdown utiliza o editor já existente, com prévia renderizada. Conferir alterações prepara uma gravação privada; não há seletor de destino capaz de transformar esse salvamento em gravação canônica. A leitura e comparação usam a versão privada salva, ou a base do acervo quando o projeto ainda não tem edição naquele idioma. Traduções privadas em português/inglês podem ser importadas, inclusive em idioma ainda ausente do acervo, com comparação e avisos de identificação. São versões de trabalho sem alinhamento automático.

Buffers privados conservam a revisão/hash sobre a qual começaram. O backend recusa salvar um buffer baseado numa edição privada que mudou concorrentemente. O histórico privado pode repor uma versão anterior; desfazer a primeira edição retira a sobreposição privada e volta a usar a versão do acervo, conservando os registros. A organização do projeto, as versões privadas e o acervo têm históricos distintos.

Incorporar versão salva ao acervo é ação separada em Documento e ferramentas → Versões e exportação. Mostra versão atual do acervo versus versão privada, origem e aviso quando o acervo mudou desde a base do projeto. Exige confirmação explícita de substituição/acréscimo, usa endpoint próprio de promoção e atualiza catálogo/manifesto/busca com histórico canônico. A versão privada permanece. O backend impede aplicar essa prévia pelo salvamento editorial comum. Nada executa commit/push.

Limite herdado: a incorporação de uma edição canônica ainda em TXT exige tratar previamente sua conversão para Markdown; a versão privada continua salva. Não foi implementada conversão silenciosa do original. Os fluxos de promoção existentes para Markdown e novas traduções são preservados.

### Teste manual sem alterar o acervo

Reinicie o backend e abra `/prototipo/mesa/` com Ctrl+Shift+R (v24).

| Etapa | Ação | Resultado esperado |
|---|---|---|
| Criar | ☰ → Organizar acervo → Projetos locais → Novo projeto. Nome: Teste de versões privadas. | Ficha privada com as seções Ficha, Documentos e Fontes PDF. |
| Vincular | Na seção Documentos, buscar 1665 e clicar no resultado para adicioná-lo. Conferir projeto e confirmar. | Projeto criado; documento não muda de coleção e não é duplicado no acervo. |
| Abrir | Abrir materiais do projeto → escolher o documento. | Aba indica Projeto; cabeçalho nomeia o projeto. Leitura usa a base do acervo até salvar uma versão privada. |
| Salvar privado | Editar Markdown → acrescentar uma linha claramente identificada como teste privado → Conferir alterações. Voltar uma vez, conferir novamente e salvar versão privada. | Cancelar conserva o buffer; confirmar guarda só no projeto. |
| Comparar contextos | Documento e ferramentas → Abrir versão do acervo. Alternar pelas abas. | Duas abas distintas: texto do acervo sem a linha e texto do projeto com a linha. |
| Importar tradução | Na aba privada, selecionar Importar tradução, idioma e Markdown. Conferir e salvar. | Versão fica no projeto, sem aparecer como nova tradução no acervo. Idiomas privados tornam-se disponíveis naquela aba. |
| Conferir promoção | Na aba privada → menu ⋯ → Incorporar versão salva ao acervo. Ler antes/depois e VOLTAR sem gravar. | Prévia mostra a diferença; cancelar preserva acervo e versão privada. Não é necessário incorporar o texto de teste. |
| Recuperar privado | Histórico da versão privada → conferir versão anterior → confirmar deliberadamente. | A edição privada volta ao estado anterior; se era a primeira gravação, passa a usar o texto do acervo. |
| Retomar | Recarregar a página. Clicar explicitamente na aba privada ou selecionar o projeto e material. | Nenhum projeto é escolhido automaticamente; projetos e versões salvos no backend continuam disponíveis. |

Para testar promoção real, use uma alteração editorial legítima e aprovada para o acervo. Não é necessário gravar uma linha fictícia no documento público para validar a interface.

Verificações: serviço HTTP em acervo temporário passou para criação/prévia do projeto, salvamento privado, importação de tradução inglesa ausente do acervo, isolamento entre dois projetos, ausência de alteração em arquivos/manifesto/busca pública, promoção explícita com busca atualizada e restauração do acervo e da versão privada. A promoção pelo endpoint editorial comum foi recusada como esperado. Auxiliares de chaves, restauração de abas/idioma/bases e citação privada passaram; sintaxe e entrega HTTP do novo módulo passaram. Navegador e aparência ficam para validação manual. Nenhum projeto ou texto real foi alterado durante os testes. Sem commit ou push.

## Ficha de projeto ampla e correção direta de tradução — décima nona evolução (v25)

Projetos novos abrem com a lista lateral recolhida e a ficha usando a área disponível. Ampliar ficha / Mostrar projetos alterna o espaço sem reconstruir os campos. A ficha de um projeto existente também pode ser ampliada; a vista com lista deixou de limitar o formulário a um corpo pequeno. Prévia, transações e histórico de projetos permanecem iguais.

### Correção de trecho

Com backend local, selecionar uma frase numa tradução portuguesa/inglesa oferece Corrigir tradução ao lado de Citar/Anotar. Funciona no texto principal, coluna paralela e tradução expandida. O original é protegido pelo serviço canônico; a interface também verifica o idioma original na abertura da correção privada. A seleção é vinculada ao intervalo Markdown por mapas de linha dos tokens do interpretador existente, sem regex para adivinhar fronteiras documentais.

Se uma frase literal única puder ser comprovada no texto renderizado, somente seu intervalo é editado. A verificação renderiza um marcador no intervalo candidato e compara o resultado com a seleção visível. Isso evita confundir texto de links, entidades HTML e outras marcações com ocorrências ocultas no Markdown. Quando não houver correspondência exata ou a frase se repetir, a interface abre o bloco Markdown completo, com aviso explícito. Não há substituição aproximada nem remoção silenciosa de formatação.

A atividade central tem editor Markdown, prévia e Conferir correção. É usado o CodeMirror local, com alternativa de textarea se o componente falhar; teclado russo global permanece disponível. O destino é o contexto da aba: tradução do acervo ou versão privada do projeto. Não há promoção implícita na correção privada. Confirmar preserva o conteúdo fora do intervalo, original e outras versões. O backend canônico atualiza catálogo/manifesto/busca e histórico; no projeto, muda só a edição privada e seu histórico.

O texto exibido precisa corresponder à versão salva. Diferenças de revisão/hash ou edição Markdown em andamento impedem sobrescrita silenciosa. Um rascunho da sessão que difira da versão salva deve ser concluído antes da correção. Voltar ao documento ou cancelar a prévia conserva o rascunho do trecho, recuperável em menu ⋯ → Retomar correção de trecho. Ao fechar uma aba com correção não confirmada, há confirmação de descarte. A sessão serializa os dados da correção, não os objetos do editor. Se a versão mudar, o rascunho pode ser exportado em vez de aplicado ao texto errado.

Salvar retorna ao idioma principal, comparação e modo anteriores; corrigir o idioma secundário não o transforma no idioma principal. A posição de leitura é mantida pelo mecanismo existente. Citações e notas continuam usando âncoras próprias; esta entrega não implementa ainda as caixas de alinhamento no fac-símile.

### Teste manual

Reinicie o backend e atualize `/prototipo/mesa/` com Ctrl+Shift+R. Recomenda-se usar primeiro o projeto de teste já criado, com o documento 1665 vinculado.

| Etapa | Ação | Resultado esperado |
|---|---|---|
| Espaço | Projetos locais → Novo projeto. Alternar Mostrar projetos / Ampliar ficha enquanto preenche nome/descrição. | Ficha nova ampla por padrão; preenchimento permanece ao alternar. Não é necessário criar outro projeto. |
| Selecionar | Abrir 1665 pelo projeto; escolher português em Leitura ou Estudo por trecho. Selecionar uma frase dentro de um parágrafo e clicar Corrigir tradução. | Abre editor e prévia. Cabeçalho indica seleção exata ou bloco completo e destino privado. |
| Cancelar | Fazer pequena mudança, Conferir correção e voltar sem salvar. | Correção permanece. Voltar ao documento também conserva o rascunho em ⋯ → Retomar correção de trecho. |
| Salvar privado | Conferir novamente e confirmar Salvar correção privada. | Retorna à leitura do projeto; o idioma/mode anteriores permanecem. Texto do acervo não muda. |
| Conferir contexto | Abrir versão do acervo e alternar as abas. Consultar Histórico da versão privada se desejar desfazer. | Diferença existe somente no projeto; o histórico privado permite retornar à versão anterior. |
| Comparar idiomas | Na aba privada, estudar russo/português em paralelo ou expandir português por trecho; selecionar frase portuguesa e corrigir. | Edita o idioma selecionado; ao retornar mantém russo como principal e português como comparação. |
| Destino canônico | Na aba do acervo, selecionar frase da tradução e preparar correção. Ler a prévia e CANCELAR para não mudar fonte publicada. | Destino indica Acervo local, diferente do projeto. Confirmação real só deve ser usada para uma correção editorial desejada. |

Validação em acervo temporário: prévia sem gravação, correção de intervalo com emoji anterior, preservação exata do restante do arquivo e do original russo, busca atualizada, rejeição de versão obsoleta e do original e recuperação completa pelo histórico passaram. Auxiliares com o markdown-it real verificaram mapas CRLF, seleção dentro de ênfase, entidades/links ocultos, frases repetidas e conversão UTF-16 para índices do backend. Sintaxe e recurso HTTP passaram. Não houve teste de navegador nem gravação no acervo real. Sem commit ou push.

## Busca por conteúdo e ZIP de coleções — vigésima evolução (v26)

A Biblioteca oferece Catálogo e Conteúdo no mesmo conjunto de filtros. Catálogo mantém consulta local ao manifesto (títulos, IDs, referência, fonte/data/autoria), funcionando também na hospedagem estática. Conteúdo usa a busca FTS do backend existente, com palavras ou frases entre aspas, filtro de idioma, coleção/subcoleção, paginação de 20 documentos e trecho da versão encontrada. Idioma no catálogo filtra documentos com aquela versão; em Conteúdo filtra a língua pesquisada. Um documento com resultados em vários idiomas aparece uma vez, na melhor correspondência conforme o serviço existente.

Abrir um resultado de Conteúdo seleciona o idioma encontrado e a versão canônica, preservando buffers existentes. O termo fica disponível ao clicar Buscar dentro do documento; não se abre automaticamente um painel que reduziria a área de leitura. Consultas FTS com palavras separadas podem encontrar termos em posições distintas; a busca interna continua literal. A interface não promete alinhar automaticamente um resultado transversal a uma citação exata.

Busca tem atraso curto de 300ms durante digitação, cancelamento da consulta anterior, proteção contra respostas fora de ordem e mensagem em erros. Consulta, escopo, idioma, coleção/subcoleção e página acompanham a sessão e o retorno da Mesa. Na publicação estática, Conteúdo fica indisponível e a limitação é explícita; não se faz download silencioso de milhares de documentos. Um índice público estático integral permanece como evolução separada, não requisito novo introduzido nesta entrega. Versões privadas de projetos não são incluídas pela busca do acervo.

### ZIP

Ao selecionar coleção ou subcoleção, aparece Baixar coleção/subcoleção completa · ZIP. O conjunto exportado inclui todos os seus documentos e idiomas, independentemente da palavra ou idioma usados no filtro da tela. A hierarquia e os vínculos ficam no manifesto do pacote; participações repetidas não duplicam documentos/edições. PDFs, imagens, notas, rascunhos da sessão e versões privadas não entram.

Markdown preserva o conteúdo recebido do arquivo canônico, sem acrescentar outro cabeçalho de exportação. TXT recebe exportação Markdown identificada e uma cópia do texto de origem em `documento/originais/idioma/`. Nomes originais são mantidos; quando duas versões têm o mesmo basename, ficam separadas em pastas de idioma. `manifesto.json` relaciona IDs, idiomas, arquivos do acervo, arquivos exportados e metadados. `LEIA-ME.txt` explica o pacote.

O gravador ZIP já usado pelo portal anterior é reutilizado sem modificar aquela implementação: ZIP armazenado, sem compressão, com nomes UTF-8. Preparação lê até três versões simultaneamente, mostra progresso e pode ser cancelada. Erro em qualquer arquivo impede download de pacote parcial. Há limite de 256 MiB de conteúdo por pacote; conjuntos maiores devem ser exportados por subcoleção. Sair da Biblioteca interrompe uma preparação ainda em andamento. Não há gravação no servidor, histórico ou publicação em uma operação de download.

### Teste manual

Reinicie o backend e abra `/prototipo/mesa/` com Ctrl+Shift+R.

| Teste | Ação | Resultado esperado |
|---|---|---|
| Preparar busca | Abrir 1665 em português e copiar de três a cinco palavras consecutivas de um parágrafo. Voltar à Biblioteca. | Ter uma frase do corpo, sem depender de um exemplo inventado. |
| Conteúdo | Selecionar Buscar no conteúdo, idioma Português e colar a frase entre aspas. | Documento aparece com um trecho do texto e indicação do idioma. |
| Abrir e voltar | Abrir o resultado; depois voltar à Biblioteca. | Abre a versão portuguesa canônica; consulta e filtros permanecem ao voltar. |
| Filtrar | Selecionar uma coleção/subcoleção e outro idioma. Testar Anterior/Próxima quando houver resultados suficientes. | Resultados respeitam o conjunto e a língua; página é preservada ao abrir/retornar. |
| ZIP | Escolher uma subcoleção pequena ou coleção de teste e clicar Baixar subcoleção/coleção completa · ZIP. | Progresso até concluir; pacote contém pastas por ID, manifesto e LEIA-ME. Inclui todos os idiomas, não só o filtro selecionado. |
| Cancelar ZIP | Em conjunto com várias versões, iniciar e clicar Cancelar ZIP antes de concluir. | Nenhum pacote parcial é baixado. |
| Consulta estática (opcional) | Abrir o piloto servido por `python3 -m http.server 8001`. | Catálogo e ZIP funcionam; busca por conteúdo indica a necessidade do backend local. |

Verificações: filtros de conteúdo por língua/conjunto, frase entre aspas e snippets passaram em servidor HTTP com acervo temporário. Novos módulos e gravador compartilhado foram servidos com MIME correto. Node verificou conjunto completo/subcoleção, duplicações de nomes, texto original, falha, limite e cancelamento; Python zipfile conferiu CRC, nomes cirílicos, cabeçalho único, cópia TXT, manifesto/hierarquia e ausência de rascunhos privados. Auxiliares de sessão anteriores e sintaxe passaram. Sem testes visuais de navegador ou alterações no acervo real. Sem commit ou push.

## Biblioteca centrada na busca — vigésima primeira evolução (v27)

A entrada deixou de separar o campo de pesquisa dos filtros por uma apresentação grande do acervo. Há um cabeçalho curto e um único painel inicial: escopo Catálogo/Conteúdo, consulta/Pesquisar, coleção/subcoleção, idioma e Limpar busca. Todos os filtros ficam próximos ao campo; subcoleção só aparece quando a coleção possui essa divisão. Enter e atualização por digitação permanecem.

Sem filtros ativos, números reais, um percurso em destaque e acesso à Mesa aparecem abaixo da pesquisa, seguidos das coleções. Ao pesquisar ou selecionar coleção/idioma, essa apresentação se recolhe e os resultados começam logo abaixo do painel. Os controles não mudam de posição durante a digitação. Limpar busca retorna à exploração de todo o acervo. Uma coleção selecionada exibe título/caminho, ZIP junto do contexto e descrição completa em Sobre este conjunto, em vez de empurrar os resultados com texto introdutório extenso.

Capas inteiras, cartões estáveis, consulta no corpo pelo backend, catálogo estático, ZIP, paginação e retorno com filtros foram preservados. O painel não é fixo e não cria outra barra permanente de leitura. Idiomas/coleções quebram em linhas em telas estreitas, mantendo rótulos visíveis. A imagem de destaque usa object-fit contain; não se fabrica uma lista de novidades com datas de coleta histórica.

Teste: Ctrl+Shift+R (v27). Na entrada, conferir campo e filtros antes dos números/capas. Digitar um termo: números/destaque devem recolher e os resultados ficar próximos da busca. Limpar busca deve restaurar a exploração. Abrir uma coleção/subcoleção deve manter os filtros no topo e exibir ZIP/descrição junto do conjunto. Abrir documento e voltar deve conservar busca/idioma/página. Conferir disposição em janela estreita. Ajuste de apresentação; sem gravações no acervo, commit ou push. Sintaxe e auxiliares de busca/exportação conferidos; avaliação visual fica para o navegador.

## Portal das coleções — vigésima segunda evolução (v28)

O responsável aprovou substituir a abertura centrada na busca por uma biblioteca apresentada por suas coleções. A entrada tem nome/missão curtos, capas grandes em galeria de três colunas no desktop e títulos abaixo, sem cartões fechados. As capas existentes são 16:9 e aparecem inteiras, sem forçar proporção de livro vertical. Coleções sem imagem recebem composição tipográfica identificada pelo título, sem fabricar fac-símiles ou novas fontes. Em telas menores a galeria passa para duas e depois uma coluna.

Há três estados na mesma Biblioteca:

- Entrada: galeria de coleções, recorte de incorporações registradas e apresentação institucional/números ao final.
- Coleção: capa e título do conjunto, navegação direta nas subcoleções, descrição acionável, lista de documentos e ZIP. Buscar nesta coleção conserva o conjunto selecionado.
- Busca: acionada por Buscar no cabeçalho, com campo, filtros e resultados ocupando a área principal. Sem consulta, mostra orientação de início, sem galeria competindo com a tarefa. Limpar filtros conserva a área de busca; Todas as coleções retorna explicitamente à entrada.

O link Biblioteca mantém o estado de navegação anterior quando o leitor volta de um documento. Clicar na marca Documentos Soviéticos retorna à entrada e limpa a seleção da Biblioteca. Rascunhos, materiais abertos e versões privadas não são apagados por esse retorno. O estado entrada/coleção/busca acompanha a sessão. A pesquisa integral continua local; catálogo e ZIP permanecem disponíveis na hospedagem estática.

Fontes PDF/OCR, catálogo, coleções/subcoleções, importação, fila e projetos estão em Organizar acervo, no cabeçalho quando houver backend, e continuam no menu global de ações. A home pública não apresenta essa lista administrativa como sua abertura visual. A Mesa continua no cabeçalho principal e no rodapé institucional.

### Registros editoriais

Foi reutilizado `assets/acervo-activity.json`, já existente no portal anterior. A seção mostra um recorte do histórico: somente eventos com commit e data válidos, IDs ainda presentes e idiomas efetivamente disponíveis. Datas baseadas apenas em coleta/proveniência não entram como novidades. Exemplos duplicados usam o registro mais recente; as listas não repetem o mesmo documento nas duas colunas. As entradas são denominadas Traduções e versões / Documentos incorporados, sem atribuir revisão ou qualidade não registrada.

O recorte não é um monitor em tempo real do backend e não implica publicação online na data do registro. Seu texto explica a diferença. Não se executou o gerador do histórico nem se alteraram dados do acervo. Percursos temáticos comentados dependem de curadoria futura; esta entrega não inventa relações entre coleções ou seleções históricas.

### Conferência manual

Reinicie o backend para liberar o módulo novo e atualize o piloto com Ctrl+Shift+R. Se a sessão restaurar uma pesquisa anterior, clique na marca Documentos Soviéticos ou Todas as coleções para avaliar a entrada.

| Conferir | Ação | Resultado esperado |
|---|---|---|
| Entrada | Clicar na marca Documentos Soviéticos. | Capas ocupam a abertura; não há campo de busca grande nem números antes delas. |
| Coleção | Clicar em uma capa e alternar subcoleções. | Capa identifica o conjunto; lista/subcoleções/ZIP acessíveis, sem voltar a uma home genérica. |
| Busca | Buscar no cabeçalho; testar Catálogo/Conteúdo e idiomas. | Busca ocupa a área central com seus filtros e resultados. Galeria fica recolhida. |
| Retorno | Abrir um documento e clicar Biblioteca. Depois clicar Todas as coleções. | Primeiro conserva seleção/pesquisa; segundo volta à galeria. |
| Ferramentas | Organizar acervo no cabeçalho. | Catálogo, coleções, importação, fila, fontes PDF/OCR e projetos disponíveis. |
| Rodapé | Rolar ao final da entrada. | Missão/critério editorial, acesso à Mesa e números reais do acervo no final. |
| Janela estreita | Reduzir a largura e percorrer os três estados. | Capas inteiras, galeria adaptada e filtros/resultados acessíveis. |

Sintaxe Python/JS e auxiliares existentes de leitura, sessão, projetos, busca e ZIP passaram. Agregação das novidades foi verificada com datas inválidas, datas de coleta sem commit, idiomas indisponíveis e repetição de documentos. Teste HTTP do novo módulo passou em acervo temporário. A avaliação visual/interação é manual. Sem alterações no acervo real, commit ou push; a interface oficial anterior permanece até a adoção aprovada.

## Paridade funcional — vínculos, contexto de PDFs e impressão (v29)

Esta entrega fecha os três itens de paridade então pendentes. Continua no piloto `/prototipo/mesa/`; não altera a entrada oficial, o acervo ou o histórico real durante as verificações.

### Decisões e funcionamento

- **Trecho → página → unidade → região:** selecionar texto Markdown oferece **Associar ao PDF**. Escolhem-se um vínculo já existente no contexto da aba, uma página desse vínculo e, opcionalmente, uma unidade revisada. Há prévia e confirmação antes de gravar. Posições e SHA referem-se ao corpo Markdown salvo, sem o cabeçalho de exportação. Uma frase que cruza formatação ou não possui correspondência inequívoca é apresentada explicitamente como bloco completo. Texto de rascunho incompatível com a versão salva é recusado pelo backend.
- **Unidades e regiões:** na fonte cadastrada, **Ferramentas → Unidades e regiões da página** abre texto e imagem num diálogo amplo. É possível dividir no cursor, unir à seguinte, desenhar até 16 retângulos por unidade, desfazer o último desenho ou limpar as regiões propostas. Tudo passa pela prévia e pelo histórico da revisão existente. Salve uma edição textual em andamento antes de alterar a estrutura. Divisão/união preservam integralmente o texto; não inventam caixas para as unidades novas. A divisão converte corretamente o cursor UTF-16 do navegador em pontos Unicode do backend.
- **Consulta:** **Documento e ferramentas → Trechos associados ao fac-símile** lista associações e abre sua página, destacando as regiões manuais disponíveis. Alterações no texto ou na revisão da página geram aviso de reconferência e suspendem o destaque. Retirar uma associação também exige prévia; o histórico do vínculo, acessível pela fonte, permite recuperá-la. Associações públicas herdadas podem ser consultadas em projetos, mas não editadas como vínculos privados. O idioma exibido é conferido por SHA também nas associações públicas.
- **Contexto de projeto para PDFs:** enviar PDF a partir de **Materiais do projeto → Cadastrar PDF neste projeto** cadastra e vincula a fonte ao projeto real. Abrir suas fontes e derivados conserva o contexto em abas separadas das fontes abertas fora do projeto. Extração/divisão encaminha `project_id` ao serviço existente; seus resultados são vinculados automaticamente pelo backend. O painel de derivados filtra pelo contexto da aba. A restauração da sessão conserva a identidade do projeto, validada novamente ao abrir a fonte; recarregar não escolhe automaticamente um projeto ativo.
- **Limite importante do contexto:** a revisão OCR de uma fonte é compartilhada. O projeto não cria uma cópia privada dessa revisão. Isso aparece no menu da fonte e na identificação do inventário. Vínculos de passagens e versões textuais do projeto são privados; somente documentos e fontes vinculados ao projeto podem receber esses vínculos. Preparação pública não é oferecida para vínculos privados, e o backend também a rejeita. Criar documento a partir de páginas continua sendo uma gravação explicitamente identificada no acervo local, não uma promoção automática de projeto.
- **Impressão:** **Documento e ferramentas → Versões e exportação → Imprimir / salvar como PDF** prepara o idioma atual em uma prévia própria, com título, ID, origem e indicação de projeto/rascunho quando aplicável. O botão abre a impressão do navegador; salvar PDF depende das opções do navegador. Não modifica Markdown ou PDFs originais. A impressão é do idioma atual; comparação lado a lado permanece uma atividade da Mesa.

### Como conferir manualmente

Reinicie `python3 -m backend` para liberar `parity.js` e abra `http://127.0.0.1:8000/prototipo/mesa/` com Ctrl+Shift+R. Use um projeto e um documento de teste para não registrar associações históricas fictícias em documentos reais.

| Teste | Caminho e ação | Esperado |
|---|---|---|
| PDF no projeto | Contexto de trabalho → projeto → Materiais → Cadastrar PDF neste projeto. Envie um PDF pequeno e confirme. | Fonte vinculada ao projeto, aba contextual; revisão OCR identificada como compartilhada. |
| Derivado | Na fonte: Ferramentas → Extrair ou dividir PDF → selecione uma página → confira e confirme → Derivados e processamento → Abrir derivado. | Nova aba no mesmo projeto; o PDF original permanece inteiro. O derivado aparece nas fontes do projeto. |
| Unidade e região | Salve a revisão textual de uma página. Ferramentas → Unidades e regiões da página → selecione uma unidade, desenhe um retângulo → Conferir regiões → confirme. | Região salva com histórico; transcrição integral preservada. Opcional: dividir no cursor e unir à seguinte, cada qual com confirmação. |
| Associação | Na fonte: Vincular a documento existente → escolha um documento já vinculado ao mesmo projeto e a página → confirme. Abra esse documento, selecione uma frase → Associar ao PDF → página/unidade → confira e confirme. | Associação privada com frase ou bloco explicitamente mostrado, página física e unidade. |
| Consulta e revisão | No documento: Documento e ferramentas → Trechos associados ao fac-símile → Abrir página associada. Depois altere e salve a revisão dessa página e reabra a lista. | Primeiro destaca a região; depois apresenta aviso de reconferência sem reutilizar o destaque antigo como válido. |
| Recuperação | Retire a associação com confirmação. Na fonte: Documentos e fac-símiles → Histórico do vínculo → confira o estado anterior e confirme. | Associação recuperada; texto e PDF intactos. |
| Impressão | No documento: Documento e ferramentas → Versões e exportação → Imprimir / salvar como PDF. | Prévia do idioma aberto e indicação correta do contexto; botão abre a impressão sem as barras da Mesa. |
| Isolamento | Abra o mesmo documento fora do projeto; consulte Trechos associados. | O vínculo privado não aparece no acervo. Preparação pública não é oferecida para o vínculo privado. |

### Verificações realizadas

Sintaxe de todos os módulos JS e auxiliares Node de catálogo/sessão/projetos/Markdown/ZIP. Um teste HTTP novo, com acervo temporário, executou upload com cabeçalho de projeto, vinculação automática, revisão de página, divisão, retângulos, associação, isolamento, recusa de publicação privada, invalidação por revisão, remoção/restauração e geração/vinculação de derivado, verificando os bytes do PDF, do original russo e do manifesto. O teste de entrega HTTP de todos os módulos também passou. Não houve teste de navegador nesta entrega; impressão, desenho e distribuição visual ficam para a conferência manual. Nenhum commit ou push foi feito.

### Ajuste após teste de regiões (v30)

O usuário confirmou desenho e desfazer; divisão/união ainda não foram testadas manualmente. O retângulo agora acompanha o ponteiro durante o arraste; cancelar o gesto descarta somente o desenho provisório. A confirmação estrutural apresenta imagens Antes/Proposta com regiões, quantidade de unidades/regiões e os textos das unidades afetadas. Explica que a transcrição integral não mudou: confirma-se a localização ou estrutura, não uma nova redação. Sintaxe JS conferida; interação visual permanece para teste manual. Sem commit/push.

### Separação de comandos estruturais e visuais (v31)

Após aprovação manual de divisão/união, os comandos foram separados espacialmente: Texto e unidades à esquerda (seletor rotulado, transcrição, dividir/unir) e Regiões na imagem à direita (desfazer/limpar/conferir junto da imagem). Cada área explica seu objeto. Unir à seguinte fica desabilitado na última unidade. Prévia e botão final distinguem Salvar organização do texto de Salvar regiões da unidade. Sintaxe conferida; sem alterações em dados, commit ou push.

### Organização por tarefa e contraste (v32)

A disposição em duas colunas foi substituída por abas Organizar texto e Marcar regiões. A unidade selecionada é comum às abas; alternar entre elas mantém o cursor do texto e os retângulos propostos. Texto e imagem usam a largura da janela ampliada. A aba textual tem campo amplo e ações no rodapé; a visual tem comandos compactos acima da imagem. Cores explícitas aumentam o contraste de textos, controles, contornos e aba ativa carmim; navegação de abas oferece setas/Home/End e foco visível. Sintaxe JS conferida. Conferência visual: atualizar com Ctrl+Shift+R, alternar abas e confirmar espaço/contraste e preservação do desenho entre abas; não é necessário repetir gravações já aprovadas. Sem alterações no acervo, commit ou push.

### Altura e rolagem durante a marcação (v33)

Janela de unidades/regiões ocupa 96% da altura disponível, respeitando o espaço do teclado virtual. Cabeçalho, abas, seletor e comandos compactados; somente a imagem possui rolagem na aba visual. Durante o arraste, proximidade às bordas do visor aciona rolagem contínua proporcional ao tempo, atualizando o retângulo contra a posição real da imagem. Soltar, cancelar, trocar aba ou fechar diálogo encerra a rolagem. Rolagem manual também atualiza o desenho em curso. Verificadas sintaxe e função de velocidade (centro, bordas, limites e área vazia); interação fica para conferência manual. Testar arrastando da parte superior à borda inferior, mantendo o mouse pressionado até a página rolar, soltando depois e conferindo a região proposta. Sem commit/push.

### Associação a página aprovada; diálogo ampliado (v34)

Usuário confirmou associação listada e abertura da página junto ao texto. A janela de associação foi ampliada para até 1120px, com trecho à esquerda e destino à direita. Fonte, página e unidade recebem rótulos visíveis; nota e confirmação possuem áreas próprias, com rolagem interna em telas baixas e coluna única em telas estreitas. Nenhuma alteração no contrato ou nos vínculos salvos. Sintaxe JS conferida. Falta conferência manual do destaque de região associada. Sem commit/push.

### Fechar o painel de fac-símile (v35)

Botão × visível junto ao seletor de fonte, inclusive em telas estreitas, fecha apenas o painel da imagem e retorna à atividade de leitura anterior (ou Leitura). Documento, associações e configuração do fac-símile permanecem preservados; o modo de retorno acompanha a sessão. Sintaxe dos módulos alterados conferida; sem commit/push.

### Correspondência visual entre texto e região (v36)

Abrir página associada também destaca a frase no texto em carmim claro e a centraliza na área de leitura, mantendo o destaque da região no PDF. O mapeamento usa offsets Markdown e validação da renderização, incluindo frases repetidas e Unicode; não escolhe outra ocorrência por aproximação. Texto alterado gera aviso sem destaque indevido. Há fallback com mark para navegadores sem CSS Custom Highlight. Destaque limpo na troca de atividade/material. Sintaxe e auxiliares de mapeamento conferidos. Conferência manual: atualizar, reabrir associação existente e observar frase destacada junto da região; não é necessário salvar novamente. Sem commit/push.

### Prévia de recuperação de trechos (v37)

A prévia genérica do vínculo omitira anchors, tornando uma restauração de trecho visualmente idêntica quando páginas/notas não mudavam. Corrigido: quantidade Antes/Proposta no início e linhas explícitas para cada trecho acrescentado, retirado ou atualizado, com idioma, página, unidade, quantidade de regiões e citação. Histórico identifica também a mudança na quantidade de trechos. Confirmação e efeito abrangem todo o estado do vínculo. Sintaxe/auxiliares verificaram adição, retirada e ausência de diferenças. Retomar teste abrindo novamente a prévia do registro de retirada; esperado 0 → 1 e frase recuperada. Documento a reabrir: teste-facsimile-tukhachevsky ([TESTE] Fac-símile Tukhachevsky). Sem commit/push.

## Edição e reconfirmação pela lista de associações (v38)

Em Trechos associados ao fac-símile, vínculos locais oferecem Editar / reconfirmar associação e Editar regiões no PDF. A primeira ação recarrega o vínculo atual, preserva a frase e a fonte, preenche página/unidade/nota e permite conferir a atualização sem selecionar o texto novamente. Usa a operação existente de associação: mantendo hash/idioma/offset, o backend atualiza a mesma associação em vez de duplicá-la. Se o corpo textual mudou, a edição é interrompida com explicação e acesso ao texto; não se adivinham offsets nem se reconfirma um trecho antigo contra outro corpo. A revisão apenas da página pode ser reconfirmada normalmente.

Unidades removidas por divisão/união aparecem como escolha pendente, exigindo seleção explícita da unidade atual ou Somente página; falhas de carregamento não removem a unidade silenciosamente. A prévia apresenta Antes/Proposta, incluindo revisão da página para tornar a reconfirmação compreensível.

Editar regiões no PDF abre/reutiliza a aba da fonte, posiciona na página e seleciona a unidade, entrando em Marcar regiões. Unidade anterior inexistente exige nova seleção. A aba do texto permanece aberta. Na aba do PDF, Voltar à associação retorna ao documento e abre a edição atualizada da associação para reconfirmar depois de salvar regiões. O destino de retorno acompanha a sessão; se a aba do texto tiver sido fechada, há aviso sem salvar outra associação. Revisão da fonte continua compartilhada e os vínculos mantêm seu contexto privado/canônico. Se houver edição textual pendente na página, ela precisa ser salva antes de abrir a edição estrutural.

### Conferência manual curta

Atualize o piloto com Ctrl+Shift+R.

| Aba | Ação | Esperado |
|---|---|---|
| Texto: [TESTE] Fac-símile Tukhachevsky | Documento e ferramentas → Trechos associados → Editar / reconfirmar associação. | Frase, página, unidade e nota preenchidas; nenhuma seleção textual necessária. |
| Ainda na aba do texto | Alterar somente a nota para Teste de edição direta → Conferir atualização → conferir e Salvar associação. | Uma única associação, nota atualizada e histórico preservado. |
| Ainda na aba do texto | Reabrir a lista → Editar regiões no PDF. | Aba da fonte original, página 1 e unidade correta; diálogo abre em Marcar regiões. |
| PDF original | Para avaliar o caminho, feche o diálogo sem alterar regiões e clique Voltar à associação na barra superior. | Retorna à aba do texto e abre a associação preenchida. Não precisa salvar se não alterou nada. |

Sintaxe dos módulos alterados e auxiliares Node passaram, cobrindo intervalos Unicode, preservação dos parâmetros de atualização, rejeição de corpo alterado e comparação das revisões. Nenhum dado real alterado pelas verificações; interação visual fica para validação manual. Sem commit/push.
