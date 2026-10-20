# Ferramentas importadas: levantamento e reaproveitamento

19/10/2026. Levantamento estático de código, documentação e artefatos; não foram executados os scripts importados, seus testes, OCR, coleta, tradução, migrações ou instalações. A interface oficial permanece Carmim.

## Alcance e localização

Foram inventariados todos os `.py`, `.sh` e arquivos `requirements*` encontrados em `temporario/`, incluindo testes e versões antigas: **291 arquivos, 165 conteúdos distintos e 126 cópias idênticas**. Isso não significa 165 ferramentas prontas. O inventário registra hashes, dependências declaradas por imports, referências a caminhos antigos e duplicações. A leitura sintática não certifica funcionamento.

- [Inventário de scripts](inventario-scripts.csv): um registro por arquivo, com caminho completo relativo ao projeto.
- [Resumo do inventário](resumo-inventario.json): contagens por pacote/família e imports identificados.
- [Artefatos tabulares selecionados](artefatos-principais.csv): 18 tabelas relevantes, seus campos, contagens, estados e hashes.
- [Plano de implementação](../../projeto/PLANO-FERRAMENTAS-PESQUISA.md): entregas, dependências, integração e critérios de aceite.

A inspeção funcional examinou scripts representativos de cada família, documentação central, relatórios e tabelas selecionadas. Não foi uma revisão linha a linha de todo o código nem uma leitura crítica dos documentos históricos.

Para reduzir caminhos nas referências abaixo:

| Sigla | Raiz no repositório |
| --- | --- |
| P | `temporario/showtrials-portatil-20261015-003451/showtrials-portatil-20261015-003451/` |
| M | `temporario/showtrials-metodologia-20261015-141712/` |
| R | `P/referencia-projeto/` |
| A | `P/materiais-auxiliares/russian-archives-discovery/` |
| K | `temporario/frentes de pesquisa/` |

Essas siglas são apenas abreviações documentais. O CSV conserva os caminhos reais.

### Pacotes

1. **Portátil:** corpus, catálogos, 209 tabelas convertidas em JSON, cópia de scripts, dados/relatórios, PDFs auxiliares, descoberta externa e dossiês. `P/LEIA-ME.md` distingue documento, representação, achado e derivado.
2. **Metodologia:** cópia do Discovery, dados de aquisição, trilha metodológica e coletor WordPress novo/opcional. Os **125 scripts Python/shell de `R/scripts/` são byte a byte idênticos aos correspondentes em `M/original/scripts/`**. O inventário não identifica neles funcionalidades distintas entre essas duas cópias.
3. **Descoberta externa:** 27 arquivos Python em A, configurações e catálogo de achados; base aproveitável, não serviço já integrado.
4. **Kits de pesquisa:** coletores, inventários e modelos de fichas; parte já originou scripts neste repositório.
5. **Conversões e revisões posteriores:** `temporario/perpetrator2004-markdown/`, revisão de Ezhov e materiais de comparação. São resultados de trabalho, não novos motores de OCR ou tradução.
6. **Legado WSL:** três TSVs descritos pelo próprio pacote como exportação não validada; não substituem o catálogo atual nem comprovam a existência do banco original nesta máquina.

## Matriz de capacidades

| Capacidade | Evidência concreta | Situação encontrada | Aproveitamento |
| --- | --- | --- | --- |
| Coleta WordPress e preservação | `M/coletar_wordpress.py`; `M/exemplos/*-post-original.json`; `R/scripts/a-extraction/` | Coletor opcional preserva respostas e hashes; diagnósticos históricos existem. | Adaptar aquisição em área de trabalho, com URL original/final, horário e receita; não recadastrar corpus já existente. |
| Catálogo e classificação | `R/scripts/c-catalog-taxonomy/diagnose-showtrials-document-types-v4.py`; auditorias de datas, autoria, limpeza e árvore | Código e resultados. A classificação v4 usa regras sobre títulos, não compreensão universal de documentos. | Sugestões explicadas para cadastro, lista de problemas e revisão em lote. Atualizar só após prévia. |
| Busca | `R/scripts/b-json-export-search/showtrials-search-v2.py` e corpus TSV | Busca antiga em exportações. | Aproveitar filtros e diagnósticos; manter SQLite FTS5 atual em vez de instalar outro buscador paralelo. |
| Pessoas e variantes | `R/scripts/e-semantic-layer/diagnose-showtrials-person-normalization.py`, `build-showtrials-canonical-people.py`, `apply-showtrials-person-alias-decisions.py` | Regras manuais e heurísticas, candidatos, decisões e índices derivados. | Autoridades com IDs estáveis, variantes confirmadas e sugestões; busca por nomes alternativos sem reescrever os textos. |
| Organizações e funções | `build-showtrials-organization-hierarchy.py`, `build-showtrials-roles-v2.py`, matrizes e perfis na família E | Artefatos automáticos e versões revisáveis. | Vocabulário, instituições e vínculos atribuídos; não converter rótulo acusatório em ocupação ou filiação comprovada. |
| Glossário | `R/scripts/g-glossary/finalize-showtrials-translation-glossary-g4-1.py`; dados G4.1 | RU–EN com estados mistos e notas. Não contém a camada portuguesa pronta. | Base multilíngue revisável, orientação de tradução, consulta contextual e exportação por provedor. |
| Estrutura documental | `R/reports/d-structural-chunking/showtrials_chunking_policy_v1_1.txt`; blueprints e scripts da família D | Diagnósticos, políticas, planejamento e validações. O roadmap ainda prevê construir o segmentador operacional. | Unidades documentais de pergunta/resposta, falas, anexos e cartas; futura ancoragem, alinhamento e tradução. |
| Planejamento de tradução | `R/scripts/t-translation-planning/diagnose-showtrials-translation-cost.py`, `plan-showtrials-translation-profiles-v1.py` | Estimativas históricas e 35 perfis em estado `draft_profile`. | Receitas, cache, orçamento e lotes retomáveis. Limites/caracteres/preços antigos não são configuração atual. |
| Textos paralelos e extração HTML | `R/scripts/t-translation-assets/extract-translation-html-text.py`, `extract-ezhov-parallel-html.py`, `build-process-dossier-texts.py` | Extração e montagem para conjuntos específicos. Alguns caminhos apontam a `/srv/toolbox/shared/...`. | Coletores/adaptadores e corpus de comparação. Não há alinhador universal nem memória de tradução pronta. |
| Descoberta em arquivos | `A/russian_archives_discovery/discovery.py`, `web.py`, perfis e comandos por fonte | Consultas, cache, robots, limitação de requisições e classificação de achados. | Fila de fontes a coletar, distinção entre encontrado/citado/adquirido, enriquecimento de referências. |
| Referências arquivísticas | `A/russian_archives_discovery/archive_refs.py` | Expressão regular extrai arquivo, fundo, inventário, processo e folhas. | Extração de candidatos, conservando a citação literal. Confirmar campos e unidades antes de cadastro. |
| Deduplicação | `A/russian_archives_discovery/dedupe.py`; scripts locais de comparação | Heurística por cota, URL e título/ano; comparação textual mais recente já existe neste projeto. | Painel de candidatos com evidências e decisão editorial; nenhuma exclusão/fusão automática. |
| PDF textual | `A/scripts/extract_pdf_text.py` | Implementação simples baseada em `pdfminer.high_level.extract_text`. Grava TXT por nome do arquivo; não mantém uma edição paginada revisável. | Adaptar para extração por página com artefatos e proveniência. A instrução `pip install '.[pdf]'` não vem acompanhada de `pyproject.toml` nesse pacote. |
| Operações de PDF e visualizador | PDFs preservados; ausência de módulo completo nos pacotes | Não encontrado código integrado para dividir/juntar/reordenar páginas ou visualizar/cotejar no site. | Desenvolvimento novo sobre bibliotecas opcionais e adaptadores, preservando o original. |
| OCR | PDFs preservados e necessidade descrita nas análises; sem motor OCR importado identificado | **Não encontrado pipeline OCR operacional nos pacotes inspecionados.** | Nova integração; OCR é um derivado a corrigir, nunca substituto silencioso do original. |
| Tradução automatizada | `A/scripts/translate_titles.py` e família T | O script de títulos substitui sete expressões estáticas e conserva o restante. Família T planeja; não executa tradução integral por API. | Tradutor de documentos exige adaptador novo, configuração e revisão; preservar a importação manual já existente. |
| Fila, pipeline e Toolbox | `R/docs/artifact-inventory.md`, `roadmap.md`, `methodological-timeline.md` | Referências à futura integração com `run-jobs`/pipelines e caminhos de outro ambiente. Não localizei o motor Toolbox nesses pacotes. | Implementar fila local pequena; uma futura exportação da Toolbox pode ser comparada ao contrato, sem bloquear o plano. |
| Dossiês e bibliografia | `P/materiais-auxiliares/dossies-locais/`; fichas em K | Sínteses, roteiros e análises; não são transcrições primárias nem dados automaticamente aprovados. | Notas privadas, cadernos de pesquisa e apresentações após revisão; citar documentos de apoio. |

## Conferências que mudam o reaproveitamento

### Glossário: usar o arquivo certo

Leitura do TSV **G4.1**, não inferência pelo relatório de prontidão anterior:

| Dado | Quantidade |
| --- | --- |
| Entradas | 892 |
| `approved` no legado | 188 |
| `auto_normalized_needs_review` | 429 |
| `auto_transliterated_needs_review` | 275 |
| Pendentes no total | 704 |
| Camada de pessoas | 794 |
| Organizações / processos / funções / tipos | 25 / 9 / 29 / 35 |
| Lista específica de revisão G4.1 | 61 |
| Candidatas no arquivo Google RU–EN | 153 |

As 61 entradas da lista específica não são todas as pendências. O relatório `showtrials_translation_glossary_freeze_readiness_report.txt` descreve uma etapa anterior com 187 aprovadas, não a situação do TSV G4.1. A análise antiga em `temporario/ANALISE_DO_ACERVO.md` deve ser lida como registro de 15/10, não como substituta desta conferência.

O arquivo Google tem **cinco colunas e cabeçalho** (`source_ru`, `target_en`, `layer`, `glossary_kind`, `confidence`). É um artefato intermediário, não um envio direto pronto: o formato unidirecional TSV/CSV documentado pelo provedor usa pares em duas colunas e sem cabeçalho. Precisaremos de exportador específico, sem perder o catálogo editorial rico. [Documentação oficial do Cloud Translation](https://docs.cloud.google.com/translate/docs/advanced/glossary).

Importar `approved` como `legacy_status`, com sua origem e versão, não como comprovação de revisão atual ou preenchimento automático de português. A taxonomia de tipos documentais e a identidade de pessoas também não devem ficar misturadas numa única tabela de substituições de palavras.

### Pessoas e relações

- `showtrials_canonical_people.tsv`: **771 registros derivados**. “Canonical” no nome do arquivo não certifica a identidade de cada pessoa.
- `showtrials_person_aliases_reviewed.tsv`: **832 formas**; o relatório registra **55 aprovações manuais e uma rejeição**, não 832 revisões humanas individuais. A tabela final não traz uma decisão manual por linha; ligar às tabelas de decisão e às regras que a produziram.
- `showtrials_organization_hierarchy.tsv`: **nove vínculos, todos `auto_proposed`**. Importar como candidatos.
- `showtrials_roles_v2.tsv`: **29 rótulos**, incluindo categorias que exigem atribuição à fonte.
- Normalização de pessoas usa padrões, remoção de iniciais e correspondência por substring. Isso pode confundir homônimos, variantes incompletas e grafias declinadas. Extrair sugestões; não fundir registros em massa.
- Índices de nomes originados nos títulos não garantem cobertura de todas as menções no corpo. Coocorrência, centralidade e frequência não demonstram relação histórica ou importância causal.

### Descoberta e redundância

O catálogo de descoberta tem **332 registros**: 322 `LOCAL_ALREADY_HAVE` e dez `REQUIRES_ACCESS`. Isso não representa 332 novos textos adquiridos.

A heurística antiga de deduplicação usa a referência arquivística assim que qualquer campo está preenchido. Uma referência reduzida ao nome do arquivo pode produzir falsos candidatos. Além disso, converte toda a URL para minúsculas e aponta duplicados por número de linha, que muda ao reordenar o TSV. O adaptador deverá exigir especificidade de cota, preservar partes sensíveis da URL e usar IDs estáveis. Nem mesmo a coincidência da cota exclui diferenças entre reprodução, trecho e edição.

## O que este projeto já incorporou

Não reconstruir o que já funciona:

- `backend/catalog.py`: catálogo versionado, IDs, projeção do manifesto, hashes e consistência.
- `backend/database.py`: índice SQLite FTS5 derivado para pesquisa local.
- `backend/editorial.py`: cadastro, metadados, importação, prévia, histórico e restauração.
- `backend/translations.py`: identificação, estrutura, comparação e envelope de exportação.
- `assets/workbench.js`: abas, Markdown/prévia, notas e instrumentos na interface Carmim.
- `scripts/collect_military_sources.py`: aquisição, respostas brutas, registro de falhas e Wayback.
- `scripts/convert_showtrials_all.py` e `prepare_markdown.py`: preparação de Markdown a partir do material coletado.
- `scripts/convert_perpetrator_docs.py`: antiword → DocBook → Markdown; preservação de fontes e alertas estruturais.
- `scripts/compare_perpetrator_showtrials.py`: comparação por sequências de palavras, com limites explicitados.

`scripts/docx_to_json.py` é uma ferramenta anterior específica: remove certos marcadores, divide notas e aproxima alinhamento por cabeçalhos. Não deve virar importador universal sem revisão de perdas, tabelas e notas. É outra evidência de código útil com recorte próprio.

## Dependências e ferramentas candidatas

Consulta à documentação oficial em 19/10/2026, sem instalar ou fixar versões nesta entrega:

| Ferramenta | Uso proposto | Estado no projeto |
| --- | --- | --- |
| [pdfminer.six](https://pdfminersix.readthedocs.io/en/latest/tutorial/highlevel.html) | Extrair texto de PDF textual; adaptar o script importado. | Referenciada pelo código importado; instalação/configuração ainda não verificada. |
| [pypdf](https://pypdf.readthedocs.io/en/stable/user/merging-pdfs.html) | Selecionar e reunir páginas, com registro da transformação. | Integração nova proposta. |
| [PDF.js](https://mozilla.github.io/pdf.js/) | Visualizar fac-símile ao lado de transcrição/OCR. | Integração nova proposta. |
| [Tesseract](https://tesseract-ocr.github.io/tessdoc/) | Reconhecimento de texto impresso em imagens. | Motor novo opcional; idiomas e qualidade precisam de piloto. |
| [OCRmyPDF](https://ocrmypdf.readthedocs.io/en/latest/introduction.html) | Produzir um PDF derivado pesquisável e tratar PDFs com imagens/texto. | Integração nova proposta. Não substitui revisão de ordem, notas ou estrutura; limitações do motor impedem prometer leitura de manuscritos. |
| `antiword`, `markdownify`, `requests`, `beautifulsoup4` | Conversão Word antigo e coleta já usadas nos scripts locais. | Reaproveitar adaptadores e separar dependências de pesquisa do núcleo do backend. |
| `python-docx` | Candidato a leitura DOCX, já referenciado em script local. | Adaptar apenas após diagnóstico de preservação; não presumir tabelas/notas completas. |
| Provedor de tradução | Executar lotes com glossário, cache e orçamento explícitos. | Não há tradutor integral configurado comprovado pelos pacotes; escolher e habilitar numa entrega própria. |

A presença de um import não comprova que o pacote esteja instalado. Estimativas históricas em dólares não são cotação atual. O plano não exige framework, npm, GPU, servidor remoto ou serviço de filas externo como ponto de partida.

## Consequência para o planejamento

O reaproveitamento principal é de **dados, políticas e algoritmos**, não a simples instalação de uma pasta de scripts. Vários scripts antigos executam leituras/gravações no nível do módulo; outros usam caminhos de outra máquina, descartam estrutura ou pressupõem os TSVs originais. Não importá-los diretamente no processo HTTP.

O padrão recomendado é: adaptador explícito → artefato candidato → diagnóstico → prévia editorial → confirmação → catálogo/manifesto/busca, mantendo as fontes e receitas. Essa passagem transforma materiais de pesquisa em instrumentos utilizáveis sem alterar silenciosamente o acervo.
