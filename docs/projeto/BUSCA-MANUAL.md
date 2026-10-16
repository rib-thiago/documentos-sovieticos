# Verificação manual da busca

Esta entrega não teve testes executados pelo assistente, por solicitação do usuário. O roteiro abaixo descreve o comportamento esperado para sua avaliação.

## Iniciar

Na raiz do projeto, execute `python3 -m backend`. Se já estiver rodando, pode mantê-lo: esta entrega altera apenas arquivos da interface. Abra <http://localhost:8000/#/busca> e atualize com **Ctrl+Shift+R** para carregar os novos arquivos. Caso a porta esteja ocupada por `python3 -m http.server`, encerre esse servidor com **Ctrl+C** antes de iniciar o backend. Não precisa de npm.

## Conferir a interface

1. Na página inicial, deve aparecer um campo de busca antes das coleções. O link **Buscar** também deve aparecer na navegação superior, inclusive em documentos.
2. Na busca, deixe o campo de palavras vazio, sem filtros, e clique em **Buscar**. O catálogo atual deve informar **2.186 documentos**, com até **25 resultados por página**. Clique em **Próxima**, confira a mudança dos resultados e use **Anterior** ou **Primeira página**. A URL deve guardar os filtros e o deslocamento (`offset`).
3. Clique em **Limpar filtros**, selecione **Português** e busque sem palavras. O catálogo inicial tem **8 documentos com versão em português**. O filtro exige uma edição nesse idioma; com palavras, pesquisa também nessa edição.
4. Limpe os filtros, escolha **Centro de Leningrado**, selecione **Ordem na coleção** e busque sem palavras. São esperados **175 documentos**, começando pelo interrogatório de L. V. Nikolaev (`showtrials-1665`). Escolha uma subcoleção e confirme a redução da lista. Ao trocar a coleção, a subcoleção anterior deve ser limpa.
5. Limpe os filtros, pesquise **Николаева**, selecione **Russo** e **Títulos e texto completo**. Os resultados devem mostrar trechos em russo e indicar o idioma da correspondência. Compare com **Somente títulos**, que restringe o campo consultado. Você também pode copiar uma expressão de um documento e pesquisá-la entre aspas duplas.
6. Selecione um tipo, como **Protocolo de interrogatório**, e confira a classificação exibida nos resultados. **Categoria** distingue artigos de documentos; **Tipo documental** corresponde à classificação específica da fonte. **Sem classificação específica** reúne os itens ainda sem essa classificação.
7. Na segunda página de uma consulta com vários resultados, abra um documento. Confira o link **Voltar aos resultados da busca**, acima do cabeçalho. Ele deve recuperar palavras, filtros e página. O botão de voltar do navegador também deve retornar à consulta. Atualizar a página ou copiar sua URL deve preservar a consulta.
8. Confira um documento traduzido, alternando leitura/estudo, índice, marcador e exportação. A abertura pela busca conserva as URLs do leitor e acrescenta apenas parâmetros de contexto. Em modo leitura, uma correspondência em determinado idioma solicita essa versão; o marcador e a retomada existentes continuam disponíveis.
9. Pesquise uma sequência inexistente, como **zzzxxyysemresultado**, para conferir a mensagem de lista vazia. Troque rapidamente de consulta e navegue para uma coleção durante uma busca: resultados antigos não devem substituir a tela atual.
10. No celular ou reduzindo a janela, confira os filtros em uma coluna, os resultados sem rolagem horizontal e a navegação com coleção, busca e índice/marcador.

## Conferir a versão estática

Encerre o backend com **Ctrl+C** e execute `python3 -m http.server 8000`. Recarregue a página da busca. Deve aparecer uma explicação de que apenas títulos são pesquisados e de como habilitar o texto completo com o backend local. O tipo documental ficará desabilitado; coleção, subcoleção, idioma e categoria continuarão disponíveis. Pesquise **Nikolaev** para experimentar um título em português.

A busca estática considera os títulos do manifesto e ignora acentos e maiúsculas. O backend pesquisa palavras indexadas e frases com SQLite FTS5. Nenhuma das duas modalidades traduz a consulta ou reúne automaticamente variantes de nomes e flexões russas. Os resultados são documentos únicos, mesmo quando pertencem a várias coleções ou possuem traduções. Não há salto automático ao parágrafo do trecho nesta entrega.
