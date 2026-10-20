# Caso Tukhachevsky e documentação militar de 1937

## Entrega local

Coleção `caso-tukhachevsky-1937`, separada da coleção militar de 1934–1936. Não foram criadas relações entre coleções nem alterados documentos anteriores.

| Subcoleção | Conteúdo | Entradas |
| --- | --- | ---: |
| Conselho Militar de 1–4 de junho | Seis páginas de sessões, preservando a divisão da publicação | 6 |
| Reuniões do NKO de 9–10 de junho | Duas páginas de reuniões do aparelho central | 2 |
| Depoimentos de Tukhachevsky | Publicações de 26/05 e 01/06 | 2 |
| Julgamento de 11 de junho | Ficha de fonte digitalizada, com PDFs preservados | 1 |

São **dez documentos textuais russos em Markdown e uma ficha editorial de PDFs**. A ficha não é uma transcrição do julgamento. Os títulos portugueses permitem identificar os textos; não são traduções portuguesas dos corpos.

As sessões e reuniões são documentação institucional relacionada ao caso, não atas judiciais. O texto de 26/05 tem forma de declaração escrita ao NKVD; seu conteúdo e assinatura permanecem intactos. A referência arquivística é a fornecida pela publicação ou pelo inventário, sem confirmação de acesso ao original arquivístico.

## Fontes e conversão

As dez páginas HTML foram recuperadas pelo Wayback Machine. As capturas selecionadas vão de 06/09/2025 a 10/07/2026. HTML bruto, CDX, URL original, captura e SHA-256 ficam em `.local/research/tukhachevsky-1937/`. Essa pasta é ignorada pelo Git e precisa de backup local.

O inventário durável está em `data/research/tukhachevsky-1937.json`. `inventario.json` e `pendencias.csv` nesta pasta registram início/fim, origem e observações por entrada. `gravacao.json` registra a criação da coleção; `conversao-notas.json` registra o refinamento posterior das notas finais. Os arquivos textuais ficam em `originais/tukhachevsky/`.

A receita reutiliza a conversão da coleção militar: extrai o corpo documental Drupal, preserva as referências, normaliza links relativos e mantém títulos e conteúdo em russo. As notas de 1937 usam marcadores `edn`, distintos de `ftn` das fontes anteriores. Foram convertidas **201 definições identificáveis** para sintaxe Markdown, com chamadas correspondentes. Notas literais sem esses marcadores continuam no corpo. Não foram encontradas tabelas nas dez páginas textuais.

Inícios, finais e títulos das páginas foram inspecionados. O subtítulo centralizado da fala de encerramento do NKO em 10/06 foi representado como H2, com sua nota mantida. Não foram criadas divisões de falas por inferência nem alinhamento com traduções ausentes. O refinamento das notas atualizou novamente a busca, mantendo o histórico anterior recuperável.

## PDF do julgamento: o que foi preservado

Os dois arquivos já existiam no pacote original. Não foi necessário baixá-los novamente; foram copiados sem alteração para `fontes/tukhachevsky/`, com cópia também na área de trabalho e hash registrado na aquisição.

| Arquivo | Material | Tamanho |
| --- | --- | --- |
| `julgamento-1937-06-11.ru.pdf` | Digitalização russa, 172 páginas físicas | 73.195.742 bytes, aproximadamente 69,8 MiB |
| `julgamento-1937-06-11.en.pdf` | Apêndice inglês de *Trotsky and the Military Conspiracy*, 143 páginas | 4.546.422 bytes, aproximadamente 4,3 MiB |

Foi inspecionada visualmente a primeira e a última página do PDF russo. A primeira identifica a sessão de 11/06 e os oito acusados; a última registra o anúncio da sentença. A numeração datilografada não coincide necessariamente com o contador físico do PDF: a última página física tem 172 a lápis e 171 datilografado. As quatro primeiras páginas não produziram texto na extração; não se presumiu que o documento estivesse transcrito.

O início do PDF inglês foi examinado por extração: identifica o apêndice e o relatório da sessão, traz índice e aviso de paginação. Não houve cotejo integral com o russo. Por isso, o inglês é oferecido como publicação complementar em PDF, sem cadastrar uma tradução alinhada ao russo no leitor.

A ficha usa o tipo Informação de referência e o rótulo visível **Ficha editorial · PDF digitalizado**. Ela contém os links dos PDFs e explica seus limites. Exportar seu Markdown exporta somente a ficha; buscar no site pesquisa o texto da ficha, não as imagens internas do julgamento. A transcrição russa e o cotejo da tradução permanecem pendências de prioridade alta.

Os PDFs são fontes preservadas independentes do cadastro. Restaurar o lote remove seus documentos e associações, mas mantém esses arquivos-fonte e a área de aquisição. Essa preservação evita perder os originais ao desfazer a apresentação editorial.

## Atualizações e histórico

Catálogo, manifesto, associações, fila editorial e índice SQLite foram atualizados. Foram acrescentadas 11 pendências. A gravação e o refinamento das notas usam transações editoriais com snapshot recuperável. Para desfazer toda a entrega, revisar primeiro a restauração da conversão de notas e depois a da criação da coleção. Edições posteriores podem exigir restauração na ordem inversa ou causar conflito; conferir a prévia antes de salvar.

A coleção militar aprovada foi versionada em `5862d9f` e enviada ao remoto, junto do commit pendente da barra lateral. Esta coleção de 1937 permanece **sem commit e sem push**, aguardando avaliação. Não houve execução de testes, servidor ou navegador; a leitura das fontes, a extração PDF, a conversão e a atualização operacional do índice não são suítes de testes.

## Como conferir manualmente

1. Inicie `python3 -m backend` na raiz e atualize com Ctrl+Shift+R.
2. Abra http://localhost:8000/#/colecao/caso-tukhachevsky-1937. Devem aparecer quatro subcoleções e 11 entradas na lista geral.
3. Abra uma sessão do Conselho e confira título/data, começo, fim, chamadas e notas. Use a fonte no cabeçalho para a captura correspondente.
4. Abra o depoimento de 26/05: ele é curto e termina com assinatura e identificação de quem recebeu a declaração. O de 01/06 é extenso e conserva sua nota final.
5. Na reunião de 10/06, confira o subtítulo da fala de encerramento e sua nota.
6. Abra a ficha do julgamento. Os dois links devem abrir PDFs locais. O arquivo russo é grande: o tamanho está indicado antes de abrir. A página deve explicar que o Markdown é uma ficha, sem anunciar uma transcrição russa disponível.
7. Confira exportação, edição local e navegação anterior/próximo nos documentos textuais. A importação de traduções continua disponível, mas nenhuma tradução foi fabricada nesta entrega.
8. Faça uma busca por expressão dos documentos textuais: as novas peças devem participar da busca integral local. As imagens do PDF não entram nessa busca. Não use a presença do PDF como confirmação de texto pesquisável.

### Endereços diretos

- Coleção: http://localhost:8000/#/colecao/caso-tukhachevsky-1937
- Conselho: http://localhost:8000/#/colecao/caso-tukhachevsky-1937/subcolecao/conselho-militar
- NKO: http://localhost:8000/#/colecao/caso-tukhachevsky-1937/subcolecao/reunioes-nko
- Depoimentos: http://localhost:8000/#/colecao/caso-tukhachevsky-1937/subcolecao/depoimentos
- Julgamento: http://localhost:8000/#/colecao/caso-tukhachevsky-1937/subcolecao/julgamento
- Sessão: http://localhost:8000/#/doc/tukhachevsky-nko37-01-pm
- Depoimento curto: http://localhost:8000/#/doc/tukhachevsky-tukh-1937-05-26
- Depoimento extenso: http://localhost:8000/#/doc/tukhachevsky-tukh-1937-06-01
- Ficha e PDFs: http://localhost:8000/#/doc/tukhachevsky-tukh-trial-1937-06-11

## Ferramentas para manutenção

As dependências de pesquisa continuam separadas do backend em `scripts/requirements-research.txt`. Não é necessário instalá-las para ler ou editar pelo site.

```bash
# Aquisição somente das entradas HTML, sem baixar outra vez as fontes preservadas.
.local/research-venv/bin/python scripts/collect_military_sources.py --wayback --inventory data/research/tukhachevsky-1937.json --work .local/research/tukhachevsky-1937

# Preparação de Markdown e relatórios, sem alterar o acervo cadastrado.
.local/research-venv/bin/python scripts/prepare_military_collection.py --profile tukhachevsky-1937
```

`--apply` é a gravação inicial e recusa uma coleção já existente. `--apply --refresh-conversion` atualiza uma receita somente se hashes e proveniência indicarem ausência de edição textual posterior; exige backend encerrado e produz histórico. Para o trabalho cotidiano, preferir o editor local, preservando suas correções. Não executar novamente as rotinas de aquisição/conversão apenas para conferir visualmente a entrega.
