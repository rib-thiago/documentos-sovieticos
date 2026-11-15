# Interface oficial — Biblioteca e Mesa

Adotada em 15/11/2026 após aprovação do piloto e dos testes manuais. Substitui a entrada visual anterior de portal/Estúdio. A entrada do projeto continua sendo a home em `/`; consulta, estudo e edição usam a mesma interface, com ferramentas conforme as capacidades do ambiente.

## Entradas e compatibilidade

| Endereço | Comportamento |
|---|---|
| `/` | Biblioteca: capas, coleções, busca e novidades; dados do acervo no rodapé. |
| `#mesa` | Materiais abertos em abas; ler, comparar e editar são atividades do material. |
| `#mesa?documento=ID&idioma=ru&atividade=parallel` | Abre documento/idioma/atividade; a URL acompanha a aba ativa. |
| `#/doc/ID?idioma=pt` | Link anterior preservado: abre o documento na nova Mesa. |
| `#/colecao/ID/subcolecao/SUB` e `#/busca?q=…` | Links anteriores preservados: abrem a coleção ou a busca. |
| `#/estudo` / `#/estudo/ID` | Abrem a Mesa ou o documento em estudo por trecho. |
| `/editorial` e `/estudio/` | No backend local, encaminham à Mesa da interface oficial. Hash e consulta de contexto são tratados pela nova entrada. |
| `/prototipo/mesa/` | Alias que encaminha para a raiz, conservando consulta e fragmento. |
| `/editorial/form` | Formulário anterior de recuperação, mantido fora do percurso normal. |

Exemplo local: `http://127.0.0.1:8000/#/doc/showtrials-1665?idioma=ru`. A publicação GitHub Pages usa os mesmos fragmentos sob o prefixo do repositório. Recursos são resolvidos relativamente ao módulo/repositório; não dependem de npm ou de rotas de servidor na hospedagem estática.

## Uso público e local

Com `python3 -m backend`, abrir `http://127.0.0.1:8000/`. Reiniciar um backend que já estava aberto para carregar novas rotas e permissões. Atualizar o navegador com Ctrl+Shift+R após a migração.

Sem backend: Biblioteca, busca por metadados, leitura/idiomas, estudo por trechos/paralelo, expansão de tradução, índice, marcador, notas/citação, Markdown, ZIP, impressão e fac-símiles previamente publicados. PDFs temporários e rascunhos usam o navegador. A busca integral e as gravações editoriais exigem backend.

Com backend: menu ☰ e Organizar acervo dão acesso a catálogo/metadados, coleções/subcoleções, cadastro/importação de corpus, traduções, Markdown, correção de trechos, fila, projetos/versões privadas, fontes PDF, extração/divisão, OCR, imagem, revisão por página, unidades/regiões, associações e históricos. A fonte OCR tem revisão compartilhada; versões textuais e vínculos de projetos mantêm seu contexto privado. Cada gravação real tem prévia e confirmação. Leitor e fonte permanecem em abas distintas quando necessário; fechar o fac-símile não fecha o texto.

Associações permitem editar/reconfirmar pela lista e acessar diretamente a página/unidade no PDF, com retorno ao documento. Texto e região são destacados ao consultar uma associação válida. Alterações da fonte geram aviso e exigem reconfirmação; mudanças do corpo textual não são reconciliadas por aproximação.

Salvar modifica apenas o ambiente local. Preparar fac-símiles para o portal modifica arquivos locais selecionados; publicar exige commit/push autorizados. Não foi implementada publicação automática.

## Código, sessão e preservação

`index.html` contém a entrada oficial; `prototipo/mesa/` conserva os módulos aprovados e o CSS. O nome da pasta é histórico, não uma escolha de interface experimental. `entry.js` trata URLs anteriores e endereços compartilháveis da Mesa. Dependências locais em `prototipo/oficina/`, utilitários em `prototipo/estudio/` e distribuições em `assets/vendor/` são reutilizados. Recursos antigos permanecem disponíveis para compatibilidade/recuperação; não são carregados como uma segunda interface na entrada normal.

A chave de sessão do piloto foi preservada para manter abas, notas, marcadores e rascunhos já validados. Um projeto não é escolhido automaticamente na entrada sem contexto explícito. Arquivos PDF temporários precisam ser reabertos após recarregar; PDFs cadastrados são recuperados pelo backend. Sessões da interface antiga não são convertidas nem apagadas por esta entrega.

Esta migração não altera documentos, traduções, catálogo, manifesto, PDFs, banco local ou fila. Materiais de teste e alterações pendentes das outras frentes não entram no commit da interface. Os dois commits anteriores preservam o piloto aprovado antes da adoção.

## Validação e limites

Testes manuais aprovados no piloto: leitura/comparação, edição/importação e seus históricos, projetos, upload/derivados, unidades, desenho com rolagem, associações, destaques, invalidação, reconfirmação e recuperação. Isolamento de associações privadas coberto também por teste automatizado. Na adoção, verificadas rotas, recursos da home, resolução no GitHub Pages, tratamento dos links anteriores e redirecionamentos locais; não se declara teste de navegador adicional nesta etapa.

EPUB, busca integral estática, sincronização automática entre idiomas, entidades/relações históricas e novas incorporações documentais continuam evoluções separadas. A implantação não certifica o conteúdo histórico nem altera o estado de revisão do acervo.

- [Manual e registro dos testes de Biblioteca e Mesa](PILOTO-BIBLIOTECA-MESA.md)
- [Proposta conceitual original](PROPOSTA-REDESENHO-2026-11-14.md)
