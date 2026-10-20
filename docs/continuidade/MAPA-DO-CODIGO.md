> Atualização de continuidade — 20/10/2026: a interface Carmim, projetos/versões privadas, oficina PDF, OCR rus/eng/por, revisão por página e fac-símiles no estudo já estão implementados. Consulte os roteiros em `docs/projeto/pdf-ocr/`. Os ZIPs antigos e as propostas abaixo são fotografias históricas, não o estado executável atual. Dados de trabalho ficam em `.local/research/`; publicação exige seleção editorial e commit/push separados.

# Mapa do projeto e seleção de arquivos

## Como o conteúdo circula

Arquivo ou edição → prévia editorial → confirmação → histórico + arquivos de texto + catálogo canônico → manifesto estático + índice de busca local → leitor. Commit/push, quando autorizados, disponibilizam os arquivos públicos; não são parte automática de salvar.

## Pastas

| Caminho | Função | Cuidado |
| --- | --- | --- |
| `originais/` | Edições RU/PT/EN, Markdown ou TXT | Nome histórico não significa que só haja originais russos. |
| `data/catalog/` | `documents`, `editions`, `collections`, `memberships`, `vocabularies`, `provenance`, em JSON | Fonte canônica; manter referências e hashes consistentes. |
| `data/manifest.json` | Projeção usada no site público | Não modificar isoladamente. |
| `.local/` | Busca SQLite, histórico e estado local | Parte é recuperável por reconstrução; histórico não. Não apagar tudo. |
| `fontes/` | Fontes coletadas preservadas | Não confundir arquivo-fonte com edição pública. |
| `assets/` | Interface, estilos, bibliotecas e imagens | Bibliotecas em `vendor/` não exigem npm. |
| `backend/` | API local, catálogo e gravações | Preservar prévia, controle de revisão e histórico. |
| `scripts/` | Ferramentas pontuais | Ler antes de executar; nem todo script é rotina atual. |
| `docs/projeto/` | Decisões e planos | Documentos históricos podem ter sido superados. |
| `temporario/` | Kits do projeto anterior e materiais de pesquisa | Referência; não dependência de execução do site. |

## Qual código enviar para cada mudança

| Pedido | Arquivos iniciais |
| --- | --- |
| Importar tradução, cabeçalhos, diferenças | `backend/translations.py`, `backend/editorial.py`, `backend/server.py`, `assets/editorial.js`, `assets/export-header.js`; exemplo de original e tradução. |
| Metadados, coleção e novo documento | `backend/catalog.py`, `backend/editorial.py`, `backend/server.py`, `assets/editorial.js`, `backend/editorial.html`; amostra relacionada do catálogo. |
| Histórico e gravação | `backend/editorial.py`, `backend/catalog.py`, `backend/server.py`; esquema do histórico sem expor notas privadas. |
| Busca | `backend/database.py`, `backend/server.py`, `assets/search.js`, `assets/catalog-ui.js`; caso de consulta e resultado esperado. |
| Leitor, idiomas, marcador, modos | `assets/app.js`, `assets/reader-editorial.js`, `assets/study-editor.js`, `assets/css/reader.css`, `assets/css/reader-panel.css`, `assets/css/study-editor.css`. |
| Bancada, abas e rascunhos | `assets/workbench.js`, `assets/app.js`, `assets/editorial.js`, `assets/css/workbench.css`. |
| Home e visual geral | `index.html`, `assets/portal.js`, `assets/interface.js`, `assets/style.css`, `assets/css/tokens.css`, `assets/css/site.css`, `assets/css/catalog.css`, `assets/css/portal.css`. |
| Visual da área editorial | `backend/editorial.html`, `assets/editorial.js`, `assets/editorial.css`, `assets/css/editorial-*.css`, `assets/css/tokens.css`. |
| PDF/OCR | `PDF-POR-PAGINA.md`, plano de ferramentas, `backend/` completo e integração de bancada/editorial; depois um PDF de exemplo. |

Arquivos adicionais podem ser necessários conforme o problema; este mapa orienta a primeira leitura, não delimita artificialmente a mudança.

## Organizar o backend sem quebrar o trabalho

O módulo `editorial.py` reúne muitas responsabilidades. Uma evolução prudente extrai uma responsabilidade por entrega — arquivos-fonte, jobs, PDF, autoridades — preservando a API existente e a camada comum de gravação/histórico. Não trocar o framework e o armazenamento ao mesmo tempo que se implementa OCR. A escolha de biblioteca PDF pode exigir uma dependência opcional; o leitor e a importação Markdown devem continuar funcionando sem ela.

Os seis JSON são canônicos. A busca SQLite é uma projeção reconstruível. A fila de processamento possui persistência própria, para que reconstruir a busca não apague progresso de OCR. Operações pesadas não devem manter o bloqueio editorial durante todo o processamento.

## O que já fizemos — por capacidades

- Incorporamos acervos, coleções/subcoleções, traduções e individualização da compilação de Ezhov, preservando a compilação e suas URLs.
- Convertimos fontes para Markdown e registramos pendências, com notas e divergências a conferir; conversão não é garantia universal de perfeição.
- Criamos catálogo estruturado e backend local, busca e fluxos editoriais com prévia, histórico e restauração.
- Integramos importação de tradução, editor Markdown e revisão por trecho ao leitor.
- Desenvolvemos índice, retomada, modos de leitura/estudo, exportação, navegação e painel de controle.
- Adotamos a interface Carmim, com portal e bancada de múltiplos documentos. A interface e suas integrações estão registradas nos commits de evolução.
- Inventariamos os kits legados e escrevemos um plano de ferramentas. PDF/OCR e revisão por página foram implementados; os roteiros atuais estão em `docs/projeto/pdf-ocr/`.

Para datas e alterações exatas, consultar Git e documentos do repositório; esta lista não é uma auditoria de cada documento publicado.

## Referências principais

- `docs/projeto/PORTAL-BANCADA-CARMIM.md`: interface oficial aprovada.
- `docs/projeto/ARQUITETURA-EDITORIAL-UX.md`: arquitetura editorial/UX.
- `docs/projeto/PLANO-FERRAMENTAS-PESQUISA.md`: evolução das ferramentas.
- `docs/pesquisa/ferramentas-importadas/LEVANTAMENTO.md`: evidências dos kits.
- `docs/projeto/DECISOES.md` e `PLANO.md`: registro acumulado.

Não trate o README antigo como retrato completo da interface atual.

## Módulos atuais da oficina

- `backend/pdf_sources.py`, `pdf_worker.py`: recepção e extração nativa.
- `backend/pdf_operations.py`, `pdf_operation_worker.py`: derivados PDF.
- `backend/pdf_review.py`, `pdf_ocr_worker.py`: revisão, histórico e OCR.
- `backend/pdf_links.py`, `assets/reader-facsimile.js`: vínculos e fac-símiles.
- `backend/research_projects.py`, `workspace_editions.py`: projetos e versões privadas.
