# Traduções e tabela revisada

Foram cadastradas as traduções portuguesas e inglesas fornecidas pelo responsável pelo acervo para os documentos abaixo. Seus textos foram mantidos, sem conversão ou revisão automática.

| Documento | Atualização | Abrir |
| --- | --- | --- |
| showtrials-1665 | Substituição da versão portuguesa e inclusão da inglesa | [Leitor](http://localhost:8000/#/doc/showtrials-1665) |
| showtrials-1666 | Inclusão de português e inglês | [Leitor](http://localhost:8000/#/doc/showtrials-1666) |
| showtrials-2674 | Inclusão de português e inglês | [Leitor](http://localhost:8000/#/doc/showtrials-2674) |
| showtrials-2675 | Inclusão de português e inglês | [Leitor](http://localhost:8000/#/doc/showtrials-2675) |
| showtrials-7032 | Inclusão de português e inglês | [Leitor](http://localhost:8000/#/doc/showtrials-7032) |
| showtrials-1699 | Tabela Markdown já corrigida pelo usuário e publicada; pendência de tabela marcada como corrigida | [Leitor](http://localhost:8000/#/doc/showtrials-1699) |

Os arquivos inicialmente chamados `showtrials-5677.pt.md` e `showtrials-5677.en.md` identificavam o documento 1665 no título, URL da fonte e ID interno. O usuário confirmou o erro nos nomes e autorizou a associação correta. Foram renomeados para `showtrials-1665.pt.md` e `showtrials-1665.en.md`. A comparação confirmou que a versão portuguesa anterior tem o mesmo corpo da nova, que acrescenta apenas título Markdown e metadados de fonte, ID e idioma. A cópia temporária anterior foi removida a pedido do usuário; permanece somente a versão portuguesa publicada em `originais/showtrials/showtrials-1665.pt.md`. O original russo do documento 5677 e suas associações não foram alterados.

O catálogo passa a ter **2.186 documentos e 2.206 versões por idioma**, incluindo **12 documentos com português**. O manifesto foi exportado do catálogo; os títulos portugueses dos quatro novos documentos traduzidos foram obtidos dos cabeçalhos fornecidos pelo usuário. As subcoleções exibem os idiomas efetivamente cadastrados, em vez do rótulo fixo “Em russo”. Os diagnósticos da conversão original permanecem históricos; a correção da tabela foi registrada em `docs/revisao-markdown/pendencias.csv` e no relatório prioritário.

Não foram executados testes nem feito commit. Para usar a busca atualizada, encerre o backend com Ctrl+C e inicie novamente com `python3 -m backend`: ele reconstrói o índice ao detectar a mudança do catálogo. Recarregue o navegador com Ctrl+Shift+R. No leitor dos cinco documentos traduzidos, confira as opções RU, PT e EN e a exportação em cada idioma. O site estático também passa a oferecer essas versões pelo manifesto atualizado.
