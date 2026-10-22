# Sakharov — coleta ampliada e plano de unidades

Data: 20/10/2026. Esta etapa amplia o piloto anterior; não altera catálogo público, manifesto ou busca. Sem commit/push. A classificação e a elegibilidade são técnicas/editoriais preliminares, não atestação das interpretações históricas da obra.

## Aquisição concluída

Foram preservadas79 URLs HTML: todas as60 posições russas, os18 extratos ingleses e o índice inglês. A introdução inglesa, contida no índice após o cabeçalho literal INTRODUCTION, foi extraída separadamente. Nenhum PDF foi baixado nesta etapa. A aquisição respeitou robots.txt e intervalo por domínio, sem contornar bloqueios.

O item 16 do índice inglês contém um href inválido, formado pelo próprio texto do título, e retornou 404. O post correto foi localizado no mesmo site pelo título: [Strengthening the Dictatory…](https://neodemocracy.blogspot.com/2022/12/strengthening-dictatory-of-proletariat.html). Ambos os endereços constam de `english-discovery.json` e da proveniência da unidade. Essa resolução está explícita no código; não é uma troca silenciosa de fonte.

Os corpos completos adquiridos somam aproximadamente 2,6 milhões de caracteres Markdown, antes da contagem repetida dos apêndices individualizados. Fontes brutas, candidatos antigos e compilações permanecem preservados por hash.

## Unidades preparadas

`temporario/coletas-quatro/sakharov/units.json` contém 90 unidades:

| Grupo | Total | Preparáveis para prévia/importação |
|---|---:|---:|
| Páginas russas da obra |60|46|
| Extratos ingleses + introdução |19|15|
| Documentos russos dos apêndices |11|11|
| Total |90|72|

As 18 unidades retidas são 13 páginas russas contendo apenas cabeçalhos, quatro extratos ingleses com referências não localizadas e a página composta dos apêndices, já preservada e desmembrada em11 candidatos. As páginas de cabeçalho continuam na compilação integral; não são descartadas nem fingidas como artigos autônomos.

`ready_for_import=true` significa que a unidade tem corpo e fronteiras tecnicamente preparáveis para a prévia do integrador. Não significa revisão humana integral, autorização de publicação ou conferência de cada alegação histórica. As seções do livro têm`kind=article` e`source_kind=later_historiography`; os 11 apêndices têm`kind=document` e proveniência de reprodução em obra posterior. A autoria de Sakharov nunca é atribuída automaticamente aos documentos reproduzidos.

A estrutura proposta usa preliminares, três partes da obra, conclusão, apêndices e seleção inglesa. Nenhum extrato inglês foi automaticamente associado a uma seção russa.

## Fronteiras e divergências verificadas

- **Apêndices 1–11:** os números estão em parágrafos HTML diretos, formando uma sequência exata e sem lacunas. Cada candidato vai do marcador até o seguinte, conservando título, corpo, assinatura, referência arquivística e notas. A tabela com`СЛУШАЛИ` e `ПОСТАНОВИЛИ`pertence ao apêndice 8 e foi preservada. O agradecimento final dos responsáveis pelo site-fonte foi retirado apenas do documento 11 e guardado em `source-apparatus/appendices-site-thanks.html`; permanece também na página composta.
- **Nota 1066 russa:** a chamada está na navegação 29, mas a definição aparece na lista de notas da navegação 30. O problema inicialmente classificado como possível ausência ficou explicado pela fronteira HTML. A relação entre unidades está registrada em `diagnostics.note_definitions_elsewhere_in_work`. Não movi a nota nem a dupliquei no texto.
- **Página de capítulo curta:** o parser antigo escolhia um contêiner externo com menus quando o corpo do capítulo continha só um cabeçalho. Corrigido para respeitar o contêiner específico mesmo curto. Os candidatos antigos foram preservados e os atuais regenerados do HTML em cache.
- **Títulos:** títulos truncados de navegação foram mantidos como títulos de navegação, enquanto`title_literal`usa o cabeçalho completo do corpo. No inglês, o título da postagem é distinto do texto do link quando divergem; por exemplo, o último link do índice dizInstead Of Conclusion, mas a postagem se intitulaHow To Turn NEP Russia Into Socialist Russia. Ambos permanecem registrados.
- **Rótulos que não são notas:** `[19]22` é recomposição do ano 1922, e`[1922]` após May 25 é esclarecimento de data. Não foram apagados nem tratados como notas faltantes.
- **Notas agrupadas na mesma linha:** a nota 749 está no fim do parágrafo anterior da seção Notes. O diagnóstico foi ajustado para considerar essa definição real, em vez de acusá-la como ausência.

## Pendências remanescentes dos extratos ingleses

| Unidade | Referências sem definição no conjunto inglês adquirido |
|---|---|
| en-nav-10 |692,693,694,696–703|
| en-nav-11 |705|
| en-nav-12 |784|
| en-nav-13 |1066|

Esses quatro extratos permanecem retidos para conferência, sem fabricar traduções de notas ou copiar automaticamente o aparato russo. A falta no conjunto inglês não implica ausência da referência na obra russa. Os demais candidatos ainda precisam da revisão editorial habitual.

## Arquivos para conferir

- `temporario/coletas-quatro/sakharov/UNIDADES.md`: índice navegável de todos os candidatos, com estado e fonte.
- `units.json`: contrato para prévia de catálogo; caminhos relativos à área Sakharov, hashes, segmentos, proveniência, pendências e elegibilidade.
- `unit-plan.csv`: plano por página/unidade, legível em planilha.
- `inventory.json`: aquisição cumulativa por URL, tentativas, versões e fontes brutas.
- `compilations/`: derivados integrais por idioma, com limites de fonte explícitos; as versões usadas nesta etapa estão listadas em `units.json.compilations`.

## Verificações e reprodução

Sete testes offline passaram: preservação de correções manuais, retenção de sucesso após falha, versionamento de fonte, capítulo curto sem menus,11 fronteiras sem mistura, recusa quando falta um marcador e reconhecimento de nota agrupada. A auditoria dos 90 registros confirmou existência dos arquivos e correspondência dos hashes de fonte/Markdown. Não foi executada importação no site.

```bash
/tmp/sakharov-collector-venv/bin/python -m unittest discover -s scripts/coletores/sakharov -p 'test_*.py'
/tmp/sakharov-collector-venv/bin/python scripts/coletores/sakharov/prepare_units.py
```

Para repetir a aquisição completa:

```bash
/tmp/sakharov-collector-venv/bin/python scripts/coletores/sakharov/collect.py --all-russian --english 18
```

A repetição usa fontes já obtidas. O comando `--refresh` consulta versões novas sem apagar as anteriores. Instalação opcional e operação detalhadas em `scripts/coletores/sakharov/README.md`.
