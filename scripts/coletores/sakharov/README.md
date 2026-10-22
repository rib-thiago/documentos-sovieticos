# Sakharov: coleta incremental em área de trabalho

Adaptação do pacote `temporario/proposta-coletores/coletor_sakharov_2003`, fornecido pelo pesquisador. A obra é historiografia posterior (2003), não um documento contemporâneo aos acontecimentos. O coletor não modifica catálogo, manifesto, busca ou edições públicas.

```bash
python3 -m venv /tmp/sakharov-collector-venv
/tmp/sakharov-collector-venv/bin/pip install -r scripts/coletores/sakharov/requirements.txt
/tmp/sakharov-collector-venv/bin/python scripts/coletores/sakharov/collect.py
```

O piloto padrão consulta três páginas russas (índices de navegação 0, 29 e 59), o índice inglês e o primeiro extrato inglês descoberto. As 60 páginas russas não devem ser chamadas automaticamente de capítulos. Os extratos ingleses são uma seleção e não devem ser alinhados aos russos pela posição.

Para escolher amostras: `--ru-pages 0,1,58,59 --english 2`. Para apenas um idioma: `--english 0` ou `--ru-pages ''`. `--output DIRETORIO` muda a área de trabalho; padrão `temporario/coletas-quatro/sakharov`.

- `raw/<hash-url>/<sha256>.html`: bytes recebidos, preservados por conteúdo.
- `candidates/<idioma>/<hash-url>-<hash-markdown>.md`: corpo Markdown sem front matter; nunca regravado se já existe. Se houver modificação manual, o inventário registra a divergência de hash sem apagá-la.
- `inventory.json`: inventário cumulativo por URL e todas as tentativas. Falhas não removem sucessos anteriores. Mudanças da fonte guardam os metadados anteriores em `versions`.
- `english-discovery.json`: links ingleses identificados no índice, sem presumir tradução integral ou correspondência.

Uma repetição usa o HTML já preservado. `--refresh` consulta novamente, preservando fontes e candidatos anteriores; requer conferência das versões. Há limitação explícita de 12 MB por HTML, checagem de tipo MIME, respeito a robots.txt e intervalo mínimo por domínio. Falha ao consultar robots impede a coleta, sem opção para ignorá-lo. Execute apenas um processo por diretório de saída.

A seleção e limpeza de corpo vêm do protótipo importado e foram refinadas conforme as amostras reais. Os candidatos continuam não revisados: conferir início/fim, títulos, notas, remissões, tabelas e eventuais menus residuais antes da publicação. A conversão não fornece paginação impressa nem alinhamento bilíngue confiável.

## Coleta ampliada e prévia de unidades

```bash
/tmp/sakharov-collector-venv/bin/python scripts/coletores/sakharov/collect.py --all-russian --english 18
/tmp/sakharov-collector-venv/bin/python scripts/coletores/sakharov/prepare_units.py
/tmp/sakharov-collector-venv/bin/python -m unittest discover -s scripts/coletores/sakharov -p 'test_*.py'
```

`prepare_units.py` usa apenas arquivos adquiridos. Produz `units.json`, `unit-plan.csv`, `UNIDADES.md` e compilações integrais por idioma. O campo `ready_for_import` é elegibilidade técnica para prévia: não publica, não garante revisão humana integral e não associa inglês/russo. Páginas de cabeçalho sem corpo são conservadas na compilação, mas retidas como unidades autônomas. Os onze apêndices são individualizados somente se a sequência HTML explícita 1–11 for validada; a compilação permanece intacta.

O índice inglês tem um endereço inválido no item 16. A resolução para o post de mesmo título no mesmo site está documentada no código, na descoberta e na proveniência. Não é substituição silenciosa. Referências a notas cuja definição está em outra página russa são registradas como tal; lacunas inglesas não são preenchidas com tradução automática.
