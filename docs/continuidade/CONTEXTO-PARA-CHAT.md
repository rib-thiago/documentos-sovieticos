> Atualização de continuidade — 20/10/2026: a interface Carmim, projetos/versões privadas, oficina PDF, OCR rus/eng/por, revisão por página e fac-símiles no estudo já estão implementados. Consulte os roteiros em `docs/projeto/pdf-ocr/`. Os ZIPs antigos e as propostas abaixo são fotografias históricas, não o estado executável atual. Dados de trabalho ficam em `.local/research/`; publicação exige seleção editorial e commit/push separados.

# Contexto essencial — Documentos Soviéticos / ShowTrials

Fotografia de 20/10/2026. Leia este arquivo antes de sugerir mudanças. Peça os arquivos ausentes em vez de presumir sua implementação.

## Projeto e usuário

Sou pesquisador-editor, não programador profissional. Preciso de explicações didáticas e instruções manuais claras. O projeto publica fontes da história política soviética, especialmente dos anos 1930, em russo, português e inglês. Não transforme acusações contidas nas fontes em fatos estabelecidos. Preserve proveniência, notas, datas, fronteiras documentais e traduções.

ShowTrials Discovery é a infraestrutura de pesquisa; Documentos Soviéticos é a edição pública. Coleções e busca têm importância equivalente. Traduções de trabalho podem ser públicas, distinguindo as revisadas. Português é a preferência inicial quando disponível; lembrar a escolha na sessão. Pessoas e episódios serão importantes para pesquisa transversal, com relações atribuídas a documentos e passagens.

## Arquitetura atual

- Frontend HTML/CSS/JavaScript sem etapa obrigatória de npm/build. Interface Carmim aprovada: portal, leitor e bancada com abas, edição local e instrumentos contextuais.
- Público: GitHub Pages estático; lê conteúdos publicados. Não grava arquivos no projeto nem executa OCR.
- Local: `python3 -m backend`, em geral http://127.0.0.1:8000/. `/editorial` abre a área editorial; `/local` informa o ambiente.
- Backend Python com servidor HTTP da biblioteca padrão e SQLite para busca. Catálogo canônico em seis JSON de `data/catalog/`; `data/manifest.json` é uma projeção. Textos em `originais/`. Não editar só o manifesto.
- `.local/` contém estado privado, índice e histórico. Não é publicado pelo Git. O histórico editorial precisa de backup separado.
- Salvar localmente não publica. Commit e push são ações separadas, autorizadas explicitamente.

## Já funciona

Coleções/subcoleções, cadastro de documentos Markdown/TXT, catálogo e busca, metadados, fila de revisão, importação PT/EN de Markdown com documento/idioma explícitos, diagnóstico e diferenças, prévia antes de gravar, histórico recuperável, editor Markdown, correção de tradução por trecho no estudo, idiomas/modos, exportação Markdown, índice, marcação/retomada, barra fixável, bancada com abas e rascunhos. O estudo paralelo atual não é um alinhamento editorial validado de todas as passagens.

Na bancada, rascunhos e notas não equivalem a uma gravação editorial confirmada. Use o encaminhamento à área editorial e confira antes de salvar.

## Ainda proposto

Recepção de PDF, extração/OCR por página, fac-símile ligado à transcrição, revisão durável por página, jobs duráveis, editor de autoridades/glossário, alinhamento estável e tradução automática integrada. Não apresentar essas capacidades como prontas.

Há material legado em `temporario/`: levantamento identificou 291 arquivos técnicos, 165 conteúdos distintos e muitas cópias. Há extração PDF simples com pdfminer, mas não uma oficina OCR pronta. Não importar diretamente scripts antigos: vários dependem de caminhos antigos ou gravam ao serem executados. O plano está em `docs/projeto/PLANO-FERRAMENTAS-PESQUISA.md`.

## Código para localizar tarefas

`backend/server.py`: HTTP/API. `catalog.py`: esquema, validação e projeções. `database.py`: busca. `editorial.py`: prévias, gravação e histórico. `translations.py`: importação/envelopes. `backend/editorial.html` + `assets/editorial.js`: interface editorial. `assets/app.js`: navegação/leitor. `workbench.js`: bancada/rascunhos. `reader-editorial.js` e `study-editor.js`: integração editorial e trechos. `portal.js`: home. `assets/css/`: estilos; `tokens.css`: paleta.

## Regras de trabalho

Preservar IDs e URLs existentes, originais, traduções, notas, histórico e alterações locais alheias à tarefa. Não instalar ferramentas nem executar testes/servidores sem meu pedido; eu faço a validação manual. Não fazer commit ou push sem autorização. Mudanças reversíveis dentro do pedido podem ser resolvidas sem perguntas constantes. Fornecer arquivos/caminhos e explicar como conferir e recuperar.

A cópia de código inclui alterações locais ainda não commitadas; HEAD encontrado: `923cf0a`. README antigo e documentos históricos podem descrever uma interface anterior. Para a interface oficial, consultar `docs/projeto/PORTAL-BANCADA-CARMIM.md`.

## Meu próximo pedido

[Descrever uma única entrega, anexar arquivos relevantes e indicar o que devo observar na validação manual.]
