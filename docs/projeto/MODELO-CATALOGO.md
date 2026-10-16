# Modelo do catálogo — versão 1

O catálogo em `data/catalog/` é versionado. Os registros de conteúdo continuam em `originais/`; nomes e corpos dos arquivos não foram alterados. Campos não conhecidos permanecem nulos ou ausentes, conforme o caso, sem inferência histórica.

| Arquivo | Conteúdo |
| --- | --- |
| `documents.json` | 2.186 cadastros documentais únicos, incluindo as sete edições editoriais anteriores |
| `editions.json` | 2.197 versões por idioma com arquivo, formato e SHA256 |
| `collections.json` | 13 coleções e 28 subcoleções com pai, slug e posição |
| `memberships.json` | 4.460 associações ordenadas entre documentos e coleções/subcoleções |
| `vocabularies.json` | 35 tipos documentais, categorias gerais e idiomas com rótulos portugueses |
| `provenance.json` | Versão do modelo, identidade do manifesto de entrada, origem das tabelas e informações de projeção |

## Documento

- `id`: identidade estável do registro. O ID ShowTrials continua `showtrials-N`; não é uma referência arquivística.
- `kind`: `document` ou `article`, mantendo a classificação geral anterior.
- `titles`: títulos por idioma, atualmente `pt` e/ou `ru`. A ausência de tradução é mantida.
- `document_type`: chave do vocabulário específico, ou `null` se ainda não registrado.
- `historical_date`: `display` conserva a data textual anterior. `value` pode receber uma data ISO confirmada; `precision` registra sua precisão editorial, como `day`, `month` ou `year`. Inicialmente `value` é nulo e a precisão não foi inferida. Uma data em `value` não deve vir de um campo WordPress sem conferência.
- `archive_reference`: referência arquivística textual, quando existente.
- `author_label`: atribuição textual já cadastrada; não é uma entidade pessoal deduzida.
- `source`: nome, ID externo e URL de origem, quando existentes.
- `source_metadata`: datas e usuário WordPress, categorias/tags e procedência da classificação. São metadados de publicação/coleta, separados de dados históricos.
- `presentation`: título curto e rótulo editorial existentes.
- `default_format`: padrão legado usado na projeção do manifesto. O formato efetivo está em cada edição.
- `extra`: campos legados não reconhecidos, preservados sem perda.
- `compatibility_fields`: nomes/ordem dos campos do manifesto anterior; não contém cópia de seus valores.

As versões por idioma ficam em registros separados. Exemplo: `showtrials-1665` tem as edições `showtrials-1665:ru` e `showtrials-1665:pt`. O conteúdo é consultado pelo caminho da edição, sem deduplicação por título ou texto.

## Edição

`id`, `document_id`, `language`, `label`, `file`, `format`, `position`, `sha256` e `bytes` identificam a versão. `format` é sempre explícito (`markdown` ou `text`), resolvendo o formato herdado anteriormente do documento. `editorial_status: not_recorded` significa que o catálogo ainda não contém uma avaliação editorial da versão; não desfaz revisões já realizadas fora desse campo.

`extra` e `compatibility_fields` preservam campos adicionais e a ausência anterior de uma declaração de formato. O exportador emite uma declaração de formato por idioma quando ela já existia ou quando passa a ser necessária para representar o formato efetivo.

O hash identifica os bytes do arquivo cadastrado. Se o texto for alterado, é necessário conferir a revisão e atualizar o hash explicitamente. Isso é independente da conferência histórica e das receitas de conversão de TXT.

## Coleção e associação

Coleções e subcoleções usam o mesmo formato: `id`, `slug`, `parent_id`, `position`, `titles`, `subtitle`, `description`, `source`, `presentation` e os campos de preservação.

Uma coleção principal tem `parent_id: null`. Uma subcoleção tem ID completo, por exemplo `centro-de-leningrado/investigacao`, mas conserva o slug `investigacao` para as URLs existentes. O modelo de compatibilidade atual admite os dois níveis usados no site; uma profundidade adicional exigirá evolução do frontend e do exportador.

Cada associação tem `collection_id`, `document_id` e `position`, a partir de zero. Ela representa uma ocorrência ordenada na coleção, sem copiar o documento. As posições são contínuas, e todo documento de uma subcoleção também precisa constar na coleção principal. Todas as associações participam dos filtros da API.

## Operações da primeira entrega

- Migração inicial: `python3 -m backend.catalog migrate --source CAMINHO_DO_PACOTE_METODOLOGICO`. Já executada neste projeto; recusa sobrescrever um catálogo existente.
- Validação: `python3 -m backend.catalog check`.
- Conferência da projeção: `python3 -m backend.catalog export --check`.
- Atualização do manifesto após editar o catálogo: `python3 -m backend.catalog export`.
- Conferência/registro de mudanças em arquivos: `refresh-files` e `refresh-files --write`.

A edição de metadados nesta etapa é feita nos JSONs versionados, seguida de validação e exportação. Formulários de administração e novas importações serão implementados em outra entrega. O banco não deve ser usado para editar esses valores.

## Fora do escopo atual

Ainda não há modelo operacional de pessoas e aliases, autoria por entidades, componentes/anexos com IDs próprios, alinhamento persistente de parágrafos ou anotações pessoais. Os materiais históricos preservados orientarão essas ampliações. As pendências e decisões da revisão do Markdown continuam em `docs/revisao-markdown/`; não foram reinterpretadas como qualidade histórica das fontes.
