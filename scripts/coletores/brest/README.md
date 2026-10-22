# Brest-Litovsk — coleta de trabalho

Adaptação do pacote fornecido pelo pesquisador. Não modifica catálogo, manifesto,
índice de busca ou textos publicados. As 56 sementes são referências de coleta,
não 56 documentos completos.

## Preparação e execução

Na raiz do repositório:

```bash
python3 -m venv .local/coletores-venv
.local/coletores-venv/bin/python -m pip install -r scripts/coletores/brest/requirements.txt
.local/coletores-venv/bin/python scripts/coletores/brest/coletar.py planejar --somente-sementes
.local/coletores-venv/bin/python scripts/coletores/brest/coletar.py coletar --somente-sementes --id lenin-jan-07 --id lenin-pt-jan --id kommunist-teses-abril
.local/coletores-venv/bin/python scripts/coletores/brest/coletar.py relatorio
```

`--id` pode ser repetido. `--grupo` restringe a uma das subcoleções de
`colecao.yml`; `--limite` limita a seleção. `--somente-sementes` evita expansão
dos índices, mas `coletar` continua fazendo os downloads das fontes selecionadas.
Sem essa opção, `descobrir`/`coletar` expandem índices conforme `descoberta.yml`.

Saída padrão: `temporario/coletas-quatro/brest/`. `raw/` conserva fontes por
hash; `candidatos/` conserva versões geradas; `md/` é a primeira cópia de trabalho
e nunca é sobrescrita pelo coletor. `meta/`, `inventario.json`, `catalogo.csv` e
`historico/` permitem examinar proveniência e versões. Executar novamente ou
planejar um lote não apaga os resultados anteriores.

`--atualizar` consulta a fonte novamente e cria outra versão quando necessário.
Falhas são tentadas novamente mesmo sem essa opção; uma falha posterior não apaga
uma aquisição anterior. Um processo gravador por diretório de saída.

Para reconverter as fontes locais sem acessar a rede:

```bash
.local/coletores-venv/bin/python scripts/coletores/brest/coletar.py converter --somente-sementes --id lenin-jan-07 --id lenin-pt-jan --id kommunist-teses-abril
```

A reconversão verifica o hash e preserva a data da aquisição original. Se o novo
candidato divergir da cópia de trabalho, isso aparece nos metadados, sem substituir
uma revisão. Consultar `candidate_path` para a versão gerada mais recente.

O texto das notas é preservado. Nesta etapa os links de notas apontam à página
de origem; a conversão em notas locais integra a preparação editorial posterior.
Páginas HTML não recebem a classificação automática de documento integral.
Saltos em parágrafos numerados são registrados, sem completar o texto.

## Verificação

```bash
.local/coletores-venv/bin/python scripts/coletores/brest/test_coletar.py
```

Os testes não acessam a rede e verificam preservação de edições, snapshots,
relatórios cumulativos, retomada de falhas, associações múltiplas e links.
Resultado real do piloto em `docs/pesquisa/quatro-coletores/brest.md`.

## Preparar unidades após ampliar a coleta

```bash
.local/coletores-venv/bin/python scripts/coletores/brest/prepare_units.py
```

Produz `units.json` e candidatos versionados em `units/`, sem escrever no site.
As notas identificáveis viram notas locais Markdown; notas ambíguas permanecem
preservadas e impedem liberar a unidade. Créditos e datas literais de redação
são conservados, sem usar o ano de publicação da edição como data do documento.

A segunda etapa tentou as 56 sementes e expandiu as 18 partes do índice do
VII Congresso. Resultado: 74 entradas, das quais 51 páginas HTML obtidas,
um PDF de estudo posterior, sete índices, nove referências e seis bloqueios
do Iskra. Há 42 versões preparáveis; 32 entradas permanecem retidas.
O par português/inglês das teses sobre a paz usa um documento com duas edições,
com conferência do escopo de introdução e teses 1–22, sem alinhamento de parágrafos.

## Recuperação das seis fontes Iskra pelo Wayback

A aquisição de 21/10/2026 recuperou as seis páginas antes bloqueadas no coletor
ativo. A API `archive.org/wayback/available` falhou por timeout, mas o índice CDX
e a recuperação direta `id_` responderam. Não é necessário ignorar o erro no
robots.txt do site atual: a fonte adquirida é uma captura pública independente.

```bash
/tmp/brest-collector-venv/bin/python scripts/coletores/brest/wayback.py
/tmp/brest-collector-venv/bin/python scripts/coletores/brest/prepare_units.py
/tmp/brest-collector-venv/bin/python scripts/coletores/brest/prepare_iskra.py
```

O primeiro comando acessa a rede; os outros usam as fontes locais. Não executar
em paralelo com outro gravador da frente Brest. `prepare_units.py` produz a base
conservadora; executar `prepare_iskra.py` depois para aplicar a divisão conferida
nas capturas. Mudança no SHA-256 da fonte suspende a preparação específica até
nova revisão. Nenhum desses comandos incorpora textos no catálogo público.

`wayback/indexes/` guarda as respostas CDX por hash; os metadados das fontes
registram original, captura, timestamp e checksum. `wayback/prepared.json` registra
as 11 unidades resultantes, a cobertura lexical e as transformações de layout.
O índice usa colapso por URL: a captura escolhida não é declarada a mais recente
de todo o arquivo. A data da captura não é a data histórica do documento.

Ver [relatório da recuperação](../../../docs/pesquisa/quatro-coletores/BREST-WAYBACK-20261021.md).
