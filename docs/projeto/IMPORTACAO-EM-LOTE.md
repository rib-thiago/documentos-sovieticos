# Importação local de documentos em lote

Esta entrega importa originais novos em Markdown ou TXT, acompanhados de CSV. Não substitui documentos existentes, não interpreta uma linha como tradução de outra e não publica no GitHub. O cadastro individual continua disponível.

O usuário autorizou o versionamento da implementação. Não foram executados testes, servidor de demonstração, compilação ou push pelo assistente. A conferência manual ampla continua descrita neste roteiro. O acervo não foi usado para uma importação de demonstração.

## Acessar

Pare o backend anterior com Ctrl+C e inicie novamente na raiz do projeto:

```bash
python3 -m backend
```

Abra http://localhost:8000/editorial#/lote e recarregue com Ctrl+Shift+R. A barra lateral também oferece **Importar lote**.

## Exercício com dois documentos

1. Clique em **Baixar modelo CSV**. O modelo usa ponto e vírgula e já tem duas linhas, para os arquivos abaixo. Mantenha os nomes e IDs para este exercício, ou altere ambos de forma correspondente se esses IDs já estiverem cadastrados.
2. No seu editor de texto, fora de `originais/`, crie um arquivo UTF-8 chamado `lote-exemplo-a.pt.md`:

```markdown
# Primeiro documento de exemplo

## Primeira seção

Este documento contém a expressão validacaolotealpha.
```

3. Crie também `lote-exemplo-b.en.txt`, em UTF-8:

```text
Second example document

This document contains the expression validacaolotebeta.
```

4. Na área editorial, selecione o CSV baixado no campo de planilha. No campo de documentos, selecione os dois arquivos juntos, usando Ctrl/Cmd ou seleção múltipla do seu sistema.
5. Em **Coleções padrão**, marque uma coleção de validação, criada antes pelo formulário de coleções. As duas linhas do modelo deixam `colecoes` em branco e usarão essa seleção. Se preferir uma subcoleção, sua coleção principal entra junto.
6. Clique em **Revisar lote**. Confira os dois IDs, idiomas, caminhos e associações. Abra os itens da prévia para ler seus conteúdos. **Nada foi gravado ainda.**
7. Se aparecerem avisos de identificação/duplicidade, confira os dados. A confirmação explícita fica obrigatória quando há avisos. IDs já existentes são erros bloqueantes e não podem ser substituídos por essa confirmação.
8. Clique em **Confirmar e salvar** e aguarde. A operação cria os dois arquivos, cadastros, associações e pendências da fila, atualizando manifesto e busca em conjunto.
9. Expanda **Documentos cadastrados** na confirmação e abra cada um no leitor. Confira o título português, o inglês, os conteúdos e a exportação.
10. Procure `validacaolotealpha` e `validacaolotebeta` na busca local. Na fila editorial, os dois IDs devem aparecer como pendentes de revisão.
11. Use **Histórico do lote / desfazer** na confirmação. Revise a restauração do registro mais recente desse lote e confirme. Os dois documentos, arquivos criados, associações e pendências devem sair do acervo ativo. O conteúdo continua recuperável no histórico.
12. Confira a coleção e a busca. Se criou uma coleção apenas para o exercício, desfaça a criação dela depois de desfazer o lote.

Não faça outras gravações entre a importação de validação e sua restauração, para evitar conflitos com os snapshots do catálogo compartilhado. Se houver edições posteriores, desfaça primeiro as mais recentes.

## Planilha

São aceitos CSV UTF-8 com ou sem BOM, separados por `;`, `,` ou tabulação. Use aspas conforme o formato CSV quando um valor contiver o separador ou quebras de linha. Colunas são identificadas pelo nome; maiúsculas e espaços nas bordas dos cabeçalhos são normalizados. Colunas desconhecidas ou repetidas são recusadas.

| Coluna | Obrigatória | Conteúdo |
| --- | --- | --- |
| arquivo | Sim | Nome exato do arquivo selecionado, incluindo extensão; diferencia maiúsculas/minúsculas |
| id | Sim | ID novo, com letras minúsculas sem acentos, números e hífens |
| titulo | Sim | Título no idioma original |
| idioma | Sim | ru, pt ou en |
| colecoes | Não | IDs das coleções/subcoleções, separados por `\|`; em branco usa a seleção padrão do formulário |
| titulo_pt | Não | Título português para exibição, quando o original não é português |
| categoria | Não | document/documento ou article/artigo; padrão document |
| tipo_documental | Não | Código do vocabulário existente, como letter ou interrogation_protocol |
| data | Não | Data para exibição |
| autoria | Não | Autoria conhecida |
| referencia_arquivistica | Não | Referência de arquivo |
| nome_fonte | Não | Nome da publicação de origem |
| url_fonte | Não | URL HTTP/HTTPS da fonte |
| id_fonte | Não | ID na fonte original |

O painel **Colunas da planilha e identificadores das coleções** lista os IDs disponíveis para copiar. Por exemplo, uma linha com `colecoes` preenchida com `centro-de-leningrado/investigacao` entra nessa subcoleção e em sua coleção principal. Se preencher mais de uma associação, use `ID1|ID2`. A lista da linha substitui a seleção padrão para aquele documento; não é somada a ela.

Cada arquivo selecionado deve aparecer exatamente uma vez no CSV. Não há associação por ordem, semelhança de nome, idioma presumido ou leitura semântica. Uma mesma ID em duas linhas é erro, mesmo se os idiomas forem diferentes. Traduções de documentos existentes continuam pelo fluxo de importação de tradução.

## Erros e avisos

**Erros bloqueiam o lote inteiro:** arquivo ausente ou sem linha no CSV, nome repetido, ID repetido ou já existente, título/idioma inválido, coleção desconhecida, arquivo vazio, formato/codificação inválido e limites excedidos. A prévia mostra a linha e o arquivo quando reconhecidos. Não existe opção de gravar automaticamente só as linhas válidas.

**Avisos exigem conferência e confirmação:** divergências entre a identificação do arquivo/cabeçalho e a planilha, ou possíveis duplicidades por títulos, URLs e hashes de arquivo. A conferência considera o catálogo existente e os outros documentos do próprio lote. Isso não comprova equivalência ou diferença semântica entre documentos.

Para conferir os bloqueios sem salvar:

- Altere uma ID do modelo para `showtrials-1666`: deve impedir o lote inteiro.
- Informe um nome diferente do arquivo selecionado: deve apontar a linha e o arquivo ausente.
- Repita a mesma ID nas duas linhas: deve recusar.
- Deixe as coleções em branco no CSV e no formulário: deve exigir uma associação por documento.
- Selecione um arquivo extra, sem linha no CSV: deve recusar, sem ignorá-lo silenciosamente.
- Gere uma prévia, depois selecione novamente uma planilha alterada: a prévia anterior deve sair da tela e uma nova revisão será necessária.

Quando editar o CSV fora do navegador, selecione novamente o arquivo no formulário antes de revisar. O navegador conserva a seleção anterior; o sistema não vigia mudanças no arquivo do seu computador.

## Limites e recuperação

- Até 100 documentos, 4 MiB por documento, 20 MiB de textos no total e 1 MiB de CSV.
- Somente originais novos Markdown/TXT em UTF-8; arquivo, BOM e quebras de linha são preservados.
- Coleções devem existir antes do lote. ZIPs, criação automática de coleções e capas não fazem parte deste formato.
- Um lote gera uma única transação e um registro de histórico. A busca é preparada uma única vez para o conjunto.
- Cada documento recebe uma pendência média na fila. As associações incluem automaticamente os pais das subcoleções e mantêm a ordem do CSV ao acrescentar documentos.
- Desfazer o lote recupera o estado anterior do catálogo/fila e remove apenas os arquivos criados nessa operação, mantendo-os no histórico. A restauração continua sujeita à conferência de conflitos com alterações posteriores.
- O histórico pode ser filtrado pelo ID do lote ou por qualquer ID de documento que ele contém. A restauração é do lote inteiro, não só do documento usado como filtro.
- A recuperação de interrupção e os controles de revisão/hash são os mesmos do cadastro individual e das demais edições locais.

## API

`POST /api/editorial/batches/preview` recebe `revision`, `csv_content`, `files` (lista de filename/content) e `collection_ids` padrão. Um lote inválido retorna diagnóstico sem preview_id nem possibilidade de salvar. Um lote válido retorna a prévia compartilhada com detalhes individuais e alertas. A confirmação usa `POST /api/editorial/save` e exige o reconhecimento explícito dos avisos quando existirem.
