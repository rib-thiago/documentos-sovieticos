# Interface oficial — Documentos Soviéticos e Estúdio

Aprovada pelo responsável em 27/10/2026 após testes manuais e refinamentos do protótipo. Esta é a interface adotada para o trabalho e a consulta; não exige escolher uma versão experimental.

## Acessos

| Entrada | Papel |
|---|---|
| `/` | Portal público: home, coleções/subcoleções, busca e leitor |
| `#/doc/ID` | Leitura normal, preservando URLs existentes |
| `#/estudo` / `#/estudo/ID` | Mesa pública de estudo e comparação |
| `/estudio/` | Ambiente local oficial de pesquisa e edição |
| `/editorial` | Encaminha ao Estúdio |
| `/editorial/form` | Compatibilidade para recuperação; não é o percurso normal |

Iniciar com `python3 -m backend` e abrir http://127.0.0.1:8000/. O site público continua estático e utilizável sem backend; as capacidades editoriais ficam no ambiente local.

## Continuidade funcional

O Estúdio disponibiliza cadastro de documento/coleção/subcoleção, catálogo e metadados, importação de corpus e traduções, edição Markdown, prévias, histórico, fila de revisão, projetos e versões privadas, upload/manipulação PDF, OCR, candidatos, transcrição por página, teclado russo, vínculos e preparação selecionada de fac-símiles públicos. Os controladores e APIs existentes foram reutilizados; acervo e URLs não foram migrados para outro sistema.

O portal disponibiliza consulta, exportação Markdown/ZIP, leitura com índice/marca/retomada, idiomas, estudo por parágrafos/paralelo, expansão de versões, abas e painéis, notas pessoais, citações, impressão e fontes publicadas. Editar ou importar versões encaminha ao Estúdio com o documento e idioma.

A barra de leitura acompanha a aba ativa. BookReader é uma atividade própria: seleciona PDF/fontes em menu compacto, oferece ida explícita à revisão e tela inteira fora dos limites da mesa. Não herda comandos da transcrição apenas por ter sido aberto a partir de uma fonte.

## Código e distribuição

`prototipo/estudio/` contém a implementação do Estúdio servida pelo endereço oficial `/estudio/`. `prototipo/oficina/` preserva distribuições locais, o adaptador de páginas BookReader e compatibilidade. Esses caminhos foram mantidos para evitar quebrar importações e recursos; sua permanência não mantém uma escolha de interfaces experimentais no percurso oficial.

Bibliotecas e licenças são versionadas localmente. Não se exige npm para iniciar ou publicar. `node_modules/`, `.local/`, PDFs de teste e `temporario/` não integram esta entrega da interface. O histórico de alterações individuais não substitui backup do ambiente local.

## Critério desta aprovação e limites

O responsável avaliou manualmente os percursos e autorizou a adoção/commits. Verificações isoladas de rotas, recursos, catálogo e repositório e simulações de controles/retomada/tela inteira estão registradas nos roteiros. Não se declara cobertura universal de navegadores ou certificação de todo o conteúdo histórico.

EPUB, busca integral estática, entidades/relações, identificadores persistentes de unidades, sincronização por alinhamento validado e integração ImageMagick→OCR permanecem entregas posteriores. Não representam recursos anteriores removidos. A revisão documental e as novas incorporações mantêm sua fila separada.

Esta adoção não altera textos, traduções ou cadastros. As alterações documentais locais ainda pendentes ficam fora dos commits desta entrega. Nenhum push é realizado sem instrução.

- [Manual do Estúdio](../../prototipo/estudio/README.md)
- [Portal: implementação, ajustes e validação](PORTAL-LEITURA-ESTUDO-IMPLEMENTACAO.md)
- [Plano de evolução do portal](PORTAL-LEITURA-ESTUDO-PLANO.md)
