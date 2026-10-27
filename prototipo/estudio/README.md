# Estúdio — ambiente local de pesquisa e edição

Adotado em 27/10/2026 após aprovação do protótipo. Substitui a navegação local da bancada e da área editorial. A home e o leitor público usam o portal renovado; a mesa pública é de consulta e o Estúdio é o ambiente de edição. Consulte o [roteiro de validação do portal](../../docs/interface/PORTAL-LEITURA-ESTUDO-IMPLEMENTACAO.md).

## Iniciar

```sh
python3 -m backend
```

Abra **http://127.0.0.1:8000/estudio/** e faça Ctrl+Shift+R. O endereço `/editorial` encaminha ao Estúdio. Os atalhos locais da antiga bancada também encaminham ao novo ambiente, preservando documento, idioma e projeto quando informados. A home permanece em `/`. Não requer npm ou serviço pago.

## Organização

- **Fontes:** PDFs, grade de páginas, fac-símile, transcrição e progresso. Abra uma fonte existente; não precisa enviá-la novamente.
- **Acervo:** pesquisa paginada com filtros; versões documentais e suas traduções.
- **Coleções:** coleções/subcoleções, novos cadastros e associações.
- **Edição:** novo documento, importação de corpus ou tradução, catálogo/metadados, fila e histórico.
- **Projetos:** contexto explícito para documentos, fontes e versões privadas.
- **Mesa:** abas arrastáveis, divisões laterais, fechamento e ampliação. Os painéis contextuais e o explorador podem ser recolhidos; Concentrar libera espaço. Ctrl K abre comandos.

A seleção de projeto vale para novos materiais. Cada aba mantém o contexto no qual foi aberta. Recarregar começa sem projeto ativo. **Retomar composição** é uma ação explícita e pede confirmação quando inclui materiais de projetos. Rascunhos e composição são da sessão do navegador; não substituem o histórico salvo.

## O que salvar significa

No acervo, a confirmação de gravação altera os arquivos locais e atualiza catálogo, manifesto e busca pelas APIs existentes, com histórico recuperável. Isso não faz commit, push ou publicação na internet.

No projeto, a edição Markdown é privada. **Promover** exige comparação e confirmação explícita para substituir a versão do acervo local. As revisões de páginas PDF pertencem à fonte local compartilhada: não são cópias privadas por projeto.

OCR gera candidatos. Carregar um candidato prepara um rascunho; apenas a prévia confirmada grava a transcrição. A incorporação documental utiliza páginas salvas e conferidas. Os originais e a extração bruta permanecem preservados.

## Mapa de continuidade

| Recursos anteriores | Entrada no Estúdio |
|---|---|
| Bancada, vários documentos e painéis laterais | Mesa com Dockview e explorador de materiais abertos |
| Leitura, índice, marca e retomada | Documento → Leitura; clicar novamente na marca a remove |
| Estudo numerado, paralelo, tradução expansível | Documento → Estudo/Paralelo; tradução expansível no estudo russo |
| Correção de tradução por trecho e citação | Bloco de estudo → Corrigir trecho / Citar bloco |
| Editor Markdown e comparação | Documento → Editar; CodeMirror, prévia e painel de diferenças |
| Exportação e importação | Documento → Baixar / Importar tradução; prévia, diagnóstico e histórico |
| Metadados, catálogo e cadastro documental | Edição → Catálogo e metadados / Novo documento |
| Coleções e subcoleções | Coleções; criação e associações com prévia |
| Importação de corpus | Edição → Importar corpus |
| Revisão e histórico do acervo | Edição → Fila de revisão / Histórico e recuperação |
| Projetos e versões privadas | Projetos; edição contextual, histórico e promoção explícita |
| Fontes, extração e OCR | Fontes → abrir PDF → ferramentas contextuais |
| Divisão/extração de PDF | Edição → Manipular PDF; derivados com proveniência |
| Alinhamento, vínculos e projeção pública de PDF | Fonte aberta → ferramentas avançadas |
| Incorporação das transcrições | Fonte → Criar documento da transcrição |
| Fac-símiles e imagem ampliável | BookReader local e visualizador de imagem |
| Edição para impressão | Documento → edição paginada/PDF via Paged.js |

Os controles de cadastro reutilizam os controladores editoriais existentes diretamente dentro das abas do Estúdio, com escopo próprio de navegação e estilo. Não carregam a página antiga em um iframe. BookReader e impressão usam isolamento próprio para suas bibliotecas. Bibliotecas e ferramentas pesadas são carregadas sob demanda.

## Validação manual sugerida

1. Reinicie o backend. Entre pela home e pelo acesso editorial. Confira que abre o Estúdio diretamente. Abra também `/editorial` e confirme o encaminhamento.
2. Em Fontes, reabra o PDF já trabalhado e a página 4. Confira a transcrição existente antes de alterar qualquer coisa. Navegue entre páginas e confira o fac-símile correspondente.
3. Recolha explorador e ferramentas, use Concentrar, arraste abas lado a lado e feche uma aba. Reabra o material pelo explorador.
4. Abra OCR, configure páginas/idioma/DPI e confira o lote. Execute somente se desejar gerar novos candidatos. Adote um candidato ou edite a transcrição; teste o teclado russo e Shift. Confira a prévia antes de salvar. Consulte o histórico.
5. Em Coleções, crie uma coleção/subcoleção de teste somente se desejar gravar novos registros. Confira a prévia. Na fonte, use Vincular coleção e confira o destino. Use Criar documento da transcrição para conferir o ciclo de incorporação; cancelar não cadastra documento.
6. Em Acervo, pesquise e aplique filtros. Abra um documento com tradução. Teste índice, marcar/desmarcar, retomada, idiomas, estudo e paralelo. Os blocos são apresentados por ordem: não representam alinhamento validado automaticamente.
7. Abra Editar e Prévia lado a lado. Faça uma pequena alteração deliberada, confira diferenças e salve apenas se desejado. Consulte o histórico e a opção de restauração com prévia. TXT permanece somente consulta.
8. Em um bloco traduzido, teste Corrigir trecho. Para uma seleção parcial, ela precisa coincidir literalmente e de forma única com o Markdown do bloco; caso contrário, revise o bloco completo. Confira a proposta antes da confirmação.
9. Abra Edição: catálogo, fila, novo documento, importação de corpus e de tradução. Confirme que cada tarefa abre em uma aba fechável, mantém prévias e não exige retornar à interface antiga.
10. Selecione um projeto e abra um documento vinculado. Confira a indicação Privado, edite/salve e verifique que o acervo não foi substituído. Examine Promover e cancele se não deseja substituir o acervo. Trocar o seletor não muda o destino de abas já abertas.
11. Teste BookReader de uma fonte local, imagem ampliável e edição para impressão. Recarregue e use Retomar composição, verificando os contextos das abas.

## Verificações e limites

Foram executados 25 testes isolados de catálogo/repositório e rotas, sem abrir servidor ou modificar o banco/acervo real. Também foram conferidas sintaxe JavaScript, referências de controles e diferenças de arquivos. Os testes de navegador ficam com o responsável; não se afirma que todos os fluxos foram exercitados no navegador.

O ensaio de imagem em Worker permite cinza, threshold, erosão, escala e download da receita. **Ainda não alimenta o OCR**: a integração de derivados ImageMagick com proveniência/coordenadas é uma próxima entrega. Motor de tradução automática também permanece separado. A edição manual e a importação de traduções estão disponíveis.

A compatibilidade `/editorial/form` foi preservada para recuperação, sem aparecer como percurso normal. Nenhum texto, tradução ou URL documental foi migrado por esta adoção. Sem commit ou push nesta entrega.

O registro anterior do experimento está em [Histórico do protótipo](../../docs/interface/ESTUDIO-HISTORICO-PROTOTIPO.md).
