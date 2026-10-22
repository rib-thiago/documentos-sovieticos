# Coletores de pesquisa

Ferramentas autônomas de coleta e preparação de acervo, separadas da publicação.
Os coletores e preparadores não escrevem em `data/catalog/`, `data/manifest.json`
ou `originais/`. A incorporação aprovada é uma operação separada, pelo mecanismo
transacional do backend. Resultados de trabalho em `temporario/coletas-quatro/`
por padrão, com estados e pendências explícitos.

- [Sakharov](sakharov/README.md): aquisição HTML e candidatos de uma obra.
- [Svitlana/Erdogan](svitlana/README.md): índices, ocorrências e traduções candidatas.
- [Mozokhin](mozokhin/README.md): segmentação conservadora de texto adquirido.
- [Brest-Litovsk](brest/README.md): sementes, descoberta e aquisição por subcoleção.

Os scripts e suas configurações são independentes dos pacotes temporários de
origem. Cada frente deve ter apenas um processo gravador no seu diretório;
frentes diferentes podem executar em paralelo. Dependências opcionais ficam
em ambiente virtual próprio; não é necessário instalar pacotes no Python do backend.

Consolidar os quatro inventários em uma prévia sem rede:

```bash
python3 scripts/coletores/consolidar.py
python3 -m unittest discover -s scripts/coletores -p test_consolidar.py -v
```

O consolidado verifica hashes e sugere correspondências com o catálogo, sem
aprovar candidatos ou importar documentos. Cada coletor preserva seu inventário
detalhado; `revisao.json` e `pendencias.csv` são projeções regeneráveis.

Resultados e instruções de conferência em
[docs/pesquisa/quatro-coletores](../../docs/pesquisa/quatro-coletores/README.md).

## Preparação e prévia navegável

Cada frente fornece `units.json`, distinguindo unidades preparáveis das retidas.
O preparador comum verifica fontes e textos por hash, protege IDs e caminhos,
concilia textos idênticos e monta uma cópia do catálogo com suas novas edições.

```bash
python3 scripts/coletores/preview_catalog.py --build-search
python3 scripts/coletores/serve_preview.py
```

Abrir `http://127.0.0.1:8001/`. Os arquivos preparados ficam em
`temporario/coletas-quatro/preview/<hash>/`; o ponteiro atual é
`preview-latest.json`. A lista por unidade está em `unidades-pendencias.csv`.
O índice SQLite é próprio da prévia e pode ser reutilizado quando a versão
preparada não mudou.

O servidor combina os arquivos preparados com os recursos visuais existentes do
site, permitindo conferir as novas coleções na interface atual. É somente leitura:
não oferece API editorial nem aceita gravações. Pode funcionar junto ao backend
normal em outra porta. Se o catálogo original mudar, gerar novamente a prévia.

O preparador não tem opção de aplicação automática. A incorporação definitiva
deve usar uma transação editorial com histórico, após a conferência da prévia.

## Incorporar um pacote aprovado

`incorporate.py --approved-package-sha256 <hash> --apply` verifica a identidade
do pacote, a base e a preservação dos registros anteriores; grava pela transação
editorial e reconstrói a busca ativa. O backend deve estar encerrado. Sem `--apply`,
apenas descreve o plano. A repetição sobre uma base já alterada é recusada.

O lote inicial das quatro coleções foi incorporado. Comprovante e orientações de
recuperação em [INCORPORACAO.md](../../docs/pesquisa/quatro-coletores/INCORPORACAO.md).
Os documentos incluídos têm pendências na fila editorial; as unidades retidas
continuam em arquivo próprio, sem registros documentais fictícios no catálogo.
