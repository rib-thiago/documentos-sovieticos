# Adaptador de candidatos Svitlana/Erdogan

Python 3.10+, biblioteca padrão. Não grava no catálogo, nos originais ou no backend.
As três sementes CSV nesta pasta são cópias do pacote recebido em 20/10/2026;
não há dependência de execução do diretório temporário original.

```sh
python3 scripts/coletores/svitlana/collect.py --indexes --sources VOL-01,TEMA-TO-STALIN
python3 scripts/coletores/svitlana/collect.py --sample-documents --limit 4
python3 scripts/coletores/svitlana/collect.py --documents --sources VOL-01 --limit 3
python3 scripts/coletores/svitlana/collect.py --reconvert
python3 scripts/coletores/svitlana/collect.py --indexes --sources all
python3 scripts/coletores/svitlana/collect.py --documents --sources VOL-01,TEMA-STALIN,TEMA-TO-STALIN,TEMA-OTHER --limit 60 --balanced
python3 scripts/coletores/svitlana/build_units.py
python3 -m unittest discover -s scripts/coletores/svitlana -p 'test_*.py' -v
```

Saída padrão: `temporario/coletas-quatro/svitlana/`; `--out` permite outra área
de trabalho. O limite de documentos conta páginas, não documentos históricos:
uma página pode conter anexos e documentos diferentes.
`--sources all` percorre as 35 sementes. Índices já obtidos usam o snapshot local;
`--refresh` pede nova consulta remota. Documentos já obtidos são pulados; o limite
conta novas tentativas, inclusive falhas. `--balanced` completa primeiro o Volume I
e alterna depois as séries prioritárias. Não há coleta integral implícita.
`--unattempted` limita a seleção a URLs sem tentativa anterior. Para aquisições
longas, use lotes de 80 com essa opção e faça uma rodada final sem ela para
repetir as falhas, sem retrabalhar URLs bem-sucedidas.

`inventory.json` é cumulativo. `sources` registra tentativas e o último sucesso
por índice. `candidates` identifica a URL por SHA-256 parcial e guarda todas as
ocorrências nas séries, tentativas, último sucesso, caminho raw/Markdown e hashes.
Falhas não removem o último sucesso nem candidatos anteriores. Links retirados
de um índice ficam no histórico; não há exclusão automática. `review.json`, criado
na conferência do piloto, é o registro editorial de pendências.

HTML bruto em `raw/SHA256.html` e candidatos em
`candidates/ID/SHA256.en.md` nunca são sobrescritos. Uma reconversão cria uma
versão nova se o conteúdo mudar, preservando a anterior. Nenhum desses arquivos
é tratado como tradução revisada. Autoria e tradutor individuais não são inferidos
dos organizadores da série; créditos e referências presentes no texto permanecem
na fonte e no candidato, com atribuição estruturada pendente de conferência.

Respeita robots.txt e intervalo mínimo de dois segundos por host. Falha ao consultar
robots interrompe a tentativa, salvo ausência HTTP 404/410; não se ignora bloqueio.
Uma resposta maior que 25 MB é rejeitada integralmente; redirecionamento para outro
host exige revisão. Não baixa PDF e não trata links externos como texto adquirido.

Conversão preserva títulos HTML, links absolutos, âncoras de notas, listas e
tabelas simples. O contêiner WordSection da fonte, quando existe, separa o corpo
da barra e masthead; o cabeçalho original continua no HTML bruto e no título de
página registrado. Tabelas complexas, layout em blockquote e notas sem vínculos
explícitos exigem revisão. O contador de parágrafos é um diagnóstico de blocos
Markdown, não um alinhamento com um original russo.

`build_units.py` emite `units.json` e arquivos individuais em `units/`, também por
hash. As decisões de `unit_decisions.json` estão vinculadas ao hash da versão
conferida: uma mudança suspende automaticamente a aprovação estrutural. A decisão
de prontidão não equivale à revisão filológica da tradução, nem elimina a
conciliação de duplicatas com o catálogo. Páginas não conferidas ou compostas
permanecem bloqueadas. O separador das duas notas de Stalin preserva cada bloco
de referência arquivística e notas com seu respectivo documento. A remoção de
blockquote usado como layout só ocorre nas unidades conferidas explicitamente;
o Markdown da página e o HTML bruto continuam disponíveis integralmente.

Não executar duas instâncias simultâneas sobre a mesma saída: o checkpoint é
atômico, mas não há coordenação de escritas concorrentes. Quatro coletores devem
usar quatro pastas; integração canônica continua centralizada.

## Revisão estrutural — rodada 4

```sh
python3 scripts/coletores/svitlana/review_structure.py
python3 scripts/coletores/svitlana/reconvert_changed.py
python3 scripts/coletores/svitlana/build_units.py
```

O diagnóstico lê todas as páginas e produz `SVITLANA-ESTRUTURA.json/.csv` nos
relatórios, sem aprovar candidatos. Marcadores de anexo, hashes, trechos inicial
/final e grupos com texto normalizado igual auxiliam a revisão; não comprovam
identidade histórica. Igualdade de mensagens de download não equivale a livros
iguais.

A seleção WordSection agora recorre ao corpo quando a maior seção representa
menos de 85% do Markdown visível do corpo: evita perder seções irmãs e documentos
fora de uma div. O resultado mais abrangente continua candidato não revisado;
pode conter navegação e não é publicado automaticamente. `reconvert_changed.py`
usa só HTML local, reconverte apenas resultados diferentes e preserva versões,
inventário anterior e relatório hash-bound. As 118 alterações da primeira
execução estão em `SVITLANA-RECONVERSAO-RODADA4.json`.

Decisões podem usar `ranges` de caracteres Unicode `[início,fim)` no Markdown
original. O emissor exige hash final, cobertura de todo texto não branco exceto
`ignored_ranges` explicitamente descritos, e só aceita sobreposição declarada em
`shared_ranges`. Isso permite compartilhar cota geral sem atribuir notas de um
anexo à carta de encaminhamento. `expected_raw_sha256`, quando presente, também
é conferido; mudanças suspendem a decisão. Os originais das decisões desta
rodada estão em `decisions_single_round4.json` e `decisions_compounds_round4.json`.
