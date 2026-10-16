# Interface, datas e navegação pelo acervo

Entrega para avaliação manual junto com o leitor integrado. Não foram executados testes pelo assistente e não houve novo commit ou push. Não foram alterados corpos de documentos ou traduções.

## O que mudou

- **Leitor:** os atalhos editoriais ficam recolhidos em **Editar documento**, ao lado da exportação. O menu separa metadados, importação e escolha da versão Markdown, com explicações curtas. Fechar com Escape ou clicando fora. A barra do leitor e os links têm tratamento visual consistente.
- **Área editorial:** navegação lateral no computador e abas horizontais no celular, seção atual destacada, campos e botões padronizados, cartões para resultados, datas junto aos títulos, tabelas e prévias com limites de rolagem. A distinção entre ações principais e secundárias é visual; salvar continua exigindo a prévia existente.
- **Listas:** 25 documentos por página, com controles no início e no fim e página na URL. A paginação também vale para a lista completa da coleção. A ordem cadastrada não foi alterada.
- **Datas:** ao lado do título aparece primeiro a data histórica cadastrada, quando disponível. Caso contrário, aparece a data coletada do ShowTrials, identificada no atributo acessível/tooltip e explicada na lista. Não há conversão de fuso horário nem promoção automática dessa data a histórica.
- **Documento anterior/próximo:** controles no início e no fim do leitor, na ordem da subcoleção escolhida. Sem contexto de subcoleção, seguem a coleção. Mostram a posição e permitem voltar à página da lista que contém aquele documento. Os limites não saltam para outra subcoleção.

## Como avaliar tudo junto

1. Encerre o backend anterior com Ctrl+C e inicie `python3 -m backend`. Recarregue o site e a área editorial com **Ctrl+Shift+R**, para carregar as novas versões de CSS e JavaScript.
2. Abra [a investigação do Centro de Leningrado](http://localhost:8000/#/colecao/centro-de-leningrado/subcolecao/investigacao). No catálogo atual há **152 documentos**, em **7 páginas**. A primeira deve exibir **1–25**, com datas junto dos títulos. Os primeiros interrogatórios de Nikolaev agora podem ser distinguidos por data.
3. Clique em página **2**: devem aparecer **26–50**, e a URL deve conter `pagina=2`. O primeiro dessa página é `showtrials-2698`. Abra-o e use **Voltar à lista**: deve retornar à página 2, não ao início da coleção.
4. Nesse documento, clique em **Anterior**. Deve abrir `showtrials-2697`, que encerra a primeira página. **Próximo** leva novamente a `2698`, atravessando a fronteira de páginas sem perder a subcoleção. Ao voltar à lista, a página deve corresponder ao documento atual.
5. No primeiro e no último documento da subcoleção, confira o controle indisponível na respectiva extremidade. Não deve circular para o começo nem mudar de subcoleção. O número “N de 152” indica a posição na sequência, não uma posição na busca.
6. No leitor, abra **Editar documento**. Confira que os três caminhos estão claros e escolha **Editar Markdown** na versão PT de um documento traduzido. Experimente a edição, prévia, gravação e restauração conforme [o roteiro integrado](LEITOR-EDITORIAL.md). Ao voltar, o contexto de coleção/subcoleção, página, idioma e modo continua disponível.
7. Na área editorial, navegue por Fila, Catálogo, Importação e Histórico. A seção atual deve ficar destacada. Compare botões principais, links secundários e cartões. No editor de metadados, a data coletada aparece como referência separada dos campos de data histórica.
8. No celular ou com a janela estreita, confira as abas, cartões, datas, menu de edição, paginação e controles anterior/próximo. Formulários ficam em uma coluna e tabelas extensas têm rolagem própria. O editor de Markdown mantém o texto e a prévia em áreas distintas.

Não é necessário salvar nada para conferir visual, datas, paginação e navegação. Se fizer edições temporárias para experimentar a integração, desfaça pelo histórico ao terminar.

## Origem das datas e publicação estática

O manifesto agora projeta `source_metadata.wordpress_date` como `collected_date`. Isso permite exibir a data na versão estática sem baixar os documentos e sem depender da API. O campo histórico `date` continua separado e tem prioridade quando preenchido. Não foi usada a data de modificação do WordPress.

O índice mantém os mesmos documentos e conteúdos; as datas já fazem parte dos metadados da API. O manifesto foi regenerado a partir do catálogo existente como operação necessária à entrega. O histórico de restauração reconstrói esse manifesto derivado a partir dos arquivos canônicos restaurados, sem exigir que um snapshot antigo já contenha o novo campo. Conflitos continuam sendo conferidos nos arquivos canônicos e nos corpos afetados.

A coleção/subcoleção é o contexto da sequência anterior/próximo. Quando o texto foi aberto por uma busca, o link de retorno à consulta continua disponível; os controles da sequência não pretendem seguir a ordenação dos resultados da busca. O idioma atual é levado ao documento seguinte quando ele possui essa versão, com fallback para os idiomas disponíveis.


## Ajustes após avaliação da interface

- Datas imediatamente após o título, inclusive em telas estreitas, com quebra natural quando faltar espaço.
- `wordpress_date` permanece metadado da fonte: não foi promovido a data histórica. O rótulo visível agora indica “fonte, não verificada”. A exportação Markdown inclui esse campo com sua identificação e mantém a data histórica separada quando cadastrada. Os reconhecedores de envelope no navegador e backend aceitam essas linhas para evitar duplicação e contagem incorreta de parágrafos. Não reescrevemos os documentos existentes.
- Exportação, idioma de leitura e apresentação do estudo usam menus com o mesmo tratamento visual da edição.
- Anterior/próximo aparecem somente após o corpo do documento.
- A barra começa no início do texto; “Fixar” ativa acompanhamento da rolagem abaixo da navbar. “Soltar” desfaz. A preferência dura a sessão da aba; a retomada por parágrafo considera a altura da barra fixada.

Para avaliar: reinicie o backend e recarregue com Ctrl+Shift+R. Abra uma lista e confira título/data; abra um documento com traduções e experimente os menus. Exporte Markdown e confira as linhas de data no cabeçalho. Use Fixar, role a página, use Soltar e confira a navegação apenas no rodapé. Nenhum teste foi executado nesta rodada.


### Painel de leitura expansível

A barra agora tem cabeçalho próprio, botões Fixar/Soltar e Recolher/Expandir e uma grade de controles. A preferência de expansão dura a sessão da aba, independentemente da fixação. Os menus abrem dentro do painel, sem sobrepor o texto, e apenas um permanece aberto por vez. Botões, seletores e menus seguem tipografia e alturas comuns à edição. No celular os controles passam para uma coluna; fixado, o painel limita sua altura e permite rolagem interna.

Avaliação manual: atualizar com Ctrl+Shift+R; comparar leitura e estudo; abrir cada menu, inclusive edição local; fixar e recolher, rolar o documento, expandir e soltar. Repetir numa tela estreita. Nenhum teste foi executado; alterações aguardam avaliação, sem commit ou push.


### Organização por função

O Painel do documento reúne Navegar no texto (índice e marcador), Visualização e idiomas e Trabalhar com o documento (exportação e edição local). Índice e marcador foram retirados da navbar; sua implementação de marcação e retomada continua a mesma. Exportação e edição mantêm posição independente do modo. Os grupos ficam em cartões com títulos e descrições, passando para uma coluna em telas pequenas. Não houve alteração do alinhamento dos textos nem dos modos de estudo existentes.

Avaliar manualmente índice e salto entre seções, marcação por clique e retomada, troca entre leitura/estudo, edição/exportação, fixação e expansão, incluindo no celular. Nenhum teste executado, commit ou push.


### Revisão: prioridade para o espaço de leitura

O painel começa sempre recolhido, inclusive após troca de modo ou documento; foi removida a persistência da expansão. Expandido, usa três grupos compactos no desktop, sem cartões internos ou descrições repetidas; menus e ações compartilham altura, fonte, bordas e cores. No celular as opções ficam em duas colunas por grupo, com adaptação a telas muito estreitas.

A troca de leitura/estudo e da apresentação de estudo captura o parágrafo visível antes de reconstruir o DOM, preserva sua posição na tela por idioma e conteúdo e reaplica a rolagem após o layout. Quando a segmentação difere, usa posição relativa no texto como aproximação. Não grava nem substitui o marcador manual.

Datas ShowTrials agora aparecem apenas como datas, sem ressalvas, tanto nas listas quanto na exportação e na edição. O campo original do catálogo permanece preservado. Esta decisão substitui os avisos registrados nas rodadas anteriores.

Avaliar manualmente alternância entre modos no meio de um documento, painel inicialmente recolhido, expansão no desktop/celular e exportação com uma única data no cabeçalho. Nenhum teste executado, commit ou push.


### Troca de visualização sem reconstruir o painel

Trocar leitura/estudo ou parágrafo/paralelo atualiza somente o corpo do documento e os estados dos controles. Cabeçalho, painel, menus, edição/exportação e navegação sequencial permanecem no DOM; não há navegação de rota ou recarga da página. O painel começa recolhido ao abrir um documento, mas permanece no estado escolhido durante trocas de visualização. Mantém a recuperação do parágrafo visível.

O cabeçalho mostra “● Retomar” sempre que existir uma marca de leitura da sessão, mesmo recolhido. A ação reaproveita a retomada existente. Opções internas de modo, idiomas, edição e exportação usam listas discretas, com seleção indicada por visto e fundo suave; elementos de ação continuam sendo botões/links acessíveis por teclado.

Avaliação manual: abrir documento com traduções, expandir e fixar o painel, trocar repetidamente os modos e conferir que ele permanece aberto e a leitura mantém posição. Marcar um parágrafo, recolher e usar “Retomar”; remover a marca e conferir que o atalho desaparece. Experimentar idiomas, exportação e edição local, também por teclado e em tela estreita. Nenhum teste executado; sem commit ou push.


### Posição definitiva do painel

O painel foi movido para antes do cabeçalho do documento, abaixo da navegação superior, mantendo fixação opcional e início recolhido. Para acessar edição a partir do leitor: Expandir → Trabalhar com o documento → Editar documento. O roteiro de integração e restauração está em LEITOR-EDITORIAL.md. Alteração de posição feita sem executar testes, commit ou push.


## Aprovação para versionamento

O usuário confirmou o funcionamento após a correção do carregamento editorial e autorizou os commits da entrega integrada. Os registros anteriores descrevem a evolução das decisões; o fluxo atual de edição parte de Editar no leitor e usa Editar Markdown na barra lateral editorial. Validação manual realizada pelo usuário; sem execução de testes pelo assistente e sem push.
