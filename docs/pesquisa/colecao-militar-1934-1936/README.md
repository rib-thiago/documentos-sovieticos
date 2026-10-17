# Aquisição da coleção militar de 1934–1936

## Estado da entrega

**Concluída a incorporação local:** 20 documentos russos, com 13 entradas na subcoleção do Conselho de 1935 e sete na de indústria de defesa. Catálogo, manifesto e índice SQLite atualizados pela operação de histórico `20261017122946131381-bddf1fec4801`, registrada em `gravacao.json`. Os HTMLs preservados correspondem a capturas entre 22/06/2023 e 20/05/2026. Foram representadas 13 tabelas e convertidas 74 definições de notas para Markdown; outras notas literais permanecem no corpo. A conferência manual no leitor continua pendente.

Em 17/10/2026, foi preparada a aquisição de 20 entradas do kit militar: 13 do Conselho Militar de dezembro de 1935 e sete da indústria de defesa de 1934–1936. O acesso direto ao Istmat apresentou timeouts de conexão/leitura. Por indicação do responsável, a aquisição passou a usar capturas públicas do Wayback Machine, com URL original, data da captura e hash registrados. O estado individual atualizado está em `pendencias.csv` e `inventario.json`.

Enquanto não houver 20 fontes adquiridas e convertidas, a operação de incorporação recusa gravar. Uma ficha bibliográfica, resposta de erro ou trecho de resultado de busca não é transformado em transcrição. A coleção, seu manifesto e seu índice não são anunciados como concluídos antes da gravação real.

Foram respeitadas as exclusões: nenhuma peça de 1937 ligada a Tukhachevsky; nenhum depoimento investigativo de Ezhov, Taits, Lurie ou Lipshits. Não são implementadas relações entre coleções.

## Organização preparada

Coleção proposta: **Exército e indústria de defesa soviéticos, 1934–1936** (`exercito-industria-defesa-1934-1936`).

Subcoleções:

- `conselho-militar-1935`: 13 entradas, na ordem do inventário, distinguindo sessões, segmentos temáticos, ata e ordens.
- `industria-defesa-1934-1936`: sete relatórios, memorandos e resoluções.

O inventário durável está em `data/research/military-1934-1936.json`. Ele preserva os campos do kit e acrescenta descrições de trabalho em português; não equivale a cadastro público. Os IDs previstos são `military-` seguido do ID do inventário, sem substituir documentos ou URLs existentes.

## Preservação e conversão

Área de trabalho: `.local/research/military-1934-1936/`, ignorada pelo Git e separada dos textos publicados. Fazer backup dessa pasta para preservar a aquisição.

- `robots.txt`: cópia das regras do site. O intervalo de aquisição é de pelo menos dez segundos, conforme a regra obtida.
- `inventory.json`: recorte usado na aquisição.
- `raw/ID.html`: resposta HTML integral quando a aquisição for bem-sucedida.
- `ID.json`: URL, estado, erro, data da tentativa e, quando disponível, URL final, tipo, tamanho e hash dos bytes adquiridos.
- `ID.cdx.json`: resposta do índice de capturas do Wayback; a captura mais recente entre as retornadas com status 200 e tipo HTML foi selecionada. A fonte visível no leitor leva à captura, e a URL original continua nos metadados.
- `review/ID.ru.md` e `.json`: texto convertido e diagnóstico, gerados somente de uma cópia adquirida com hash correspondente.

A receita usa a região documental do HTML Drupal, sem recorrer automaticamente a toda a página caso não identifique o corpo. Conserva títulos e texto russos, transforma links relativos em links para a fonte e mantém as notas que estejam nessa região. Notas Word/Drupal com chamadas e definições identificáveis são convertidas para `[^N]`; notas sem pareamento ou contendo tabelas permanecem no corpo, sem descarte. Início/fim e contagens de tabelas ficam no diagnóstico para cotejo. Dez títulos temáticos centralizados da sessão da manhã de 08/12 foram conferidos no HTML e representados como H2, sem criar divisões por inferência do assunto.

As tabelas são representadas em Markdown a partir da grade HTML, considerando rowspan e colspan. Níveis de cabeçalho são combinados com « / »; células vazias de cabeçalho recebem rótulos editoriais genéricos. Nas linhas de dados, «↳» sinaliza a continuação de uma célula mesclada, sem repetir seu valor. Um aviso em russo explica essas escolhas quando há mesclas. A fonte HTML permanece disponível para cotejo visual, numérico e de unidades. Imagens não recebem transcrição ou OCR presumido.

A conversão foi aplicada às 20 páginas adquiridas. Foram inspecionados os títulos, inícios e finais de todos os corpos documentais, as estruturas de tabelas e exemplos do Markdown gerado. Isso não equivale a colação histórica integral ou confirmação numérica de todas as células. Não foi executada suíte de testes, servidor ou conferência no navegador.

## Conferências prioritárias por documento

| Documento | Pendência |
| --- | --- |
| `military-rkka-raw-materials-1934` | Dez tabelas; cotejar grade, anos, unidades, valores e campos vazios. Há projeções até 1937 dentro de um documento de 1934; isso não o transforma em peça de 1937. |
| `military-gosplan-aircraft-1935` | Duas tabelas; cotejar cabeçalhos compostos, percentuais e períodos. A fonte informa seções omitidas; o texto é um extrato. |
| `military-aviation-korolev-1935` | Uma tabela; cotejar cabeçalhos e números. O título russo indica extrato de relatório. |
| `military-voroshilov-artillery-1936` | Notas informam anexos não publicados; esses anexos não foram coletados nem inventados. |
| `military-nko35-protocol` | O corpo indica “não posterior a 8 de dezembro”, enquanto o título se refere ao Conselho de 8–14/12. Conferir a distinção entre data da peça e período do evento. |
| Sessões do Conselho | Conferir notas convertidas e referências a notas da edição impressa. As páginas temáticas de uma mesma sessão não foram concatenadas. |

As 20 entradas de revisão estão também na fila editorial. Os três documentos com tabelas receberam prioridade alta. Os demais mantêm a conferência de fronteiras, notas, metadados e referências como pendência média.

## Retomar a aquisição

O backend não precisa ser encerrado para adquirir fontes e preparar a área de revisão. Para gravar a coleção, ele precisa estar encerrado, pois a transação usa o bloqueio editorial existente.

As ferramentas de pesquisa têm dependências separadas do backend. Elas podem ser instaladas em ambiente local ignorado pelo Git:

```bash
python3 -m venv .local/research-venv
.local/research-venv/bin/pip install -r scripts/requirements-research.txt
.local/research-venv/bin/python scripts/collect_military_sources.py --wayback --retry-failed
.local/research-venv/bin/python scripts/prepare_military_collection.py
```

É possível selecionar uma fonte com `--id nko35-08-am` no coletor. Cópias já adquiridas não são baixadas novamente; falhas só são tentadas novamente com `--retry-failed`. Na execução inicial, as dependências foram instaladas em `/tmp/soviet-military-collector-deps`, sem modificar o Python do backend.

Após a aquisição/conversão completa e a conferência dos relatórios:

```bash
.local/research-venv/bin/python scripts/prepare_military_collection.py --apply
```

Esse comando faz a gravação solicitada, não um teste: cria a coleção e subcoleções, arquivos russos, cadastros, pendências editoriais, manifesto e índice SQLite usando a transação editorial com snapshot recuperável. Recusa aquisições incompletas, coleções ou destinos existentes. Nenhum commit, push ou publicação automática faz parte da operação.

## Conferência manual depois de incorporar

1. Iniciar `python3 -m backend` e atualizar o navegador com Ctrl+Shift+R.
2. Abrir `http://localhost:8000/#/colecao/exercito-industria-defesa-1934-1936`. Somente após gravação bem-sucedida, devem existir as duas subcoleções e os 20 documentos em russo.
3. Abrir uma sessão longa, a ata e um relatório industrial; cotejar início, fim, data, referências, falas e notas contra o HTML preservado.
4. Conferir números, unidades e estrutura de cada tabela; usar os cabeçalhos compostos, indicadores de mescla e o original HTML. As pendências editoriais permanecem abertas até essa revisão.
5. Experimentar índice, exportação e navegação anterior/próximo. O título português identifica a peça, mas não significa que exista tradução portuguesa do corpo.
6. No backend local, conferir edição de metadados/Markdown e pesquisar uma expressão do texto. A busca estática publicada continua limitada aos títulos.
7. Consultar o histórico da operação antes de qualquer restauração: desfazer o lote remove a nova coleção e os novos textos/cadastros, sem apagar a área de fontes. Edições posteriores podem impedir restauração conjunta por conflito.

O material de pesquisa, os originais existentes e as URLs publicadas permanecem preservados. A incorporação está concluída localmente; a revisão manual pelo responsável e a autorização de versionamento/publicação permanecem pendentes.

### Endereços sugeridos para conferência

- Coleção: http://localhost:8000/#/colecao/exercito-industria-defesa-1934-1936
- Conselho: http://localhost:8000/#/colecao/exercito-industria-defesa-1934-1936/subcolecao/conselho-militar-1935
- Indústria: http://localhost:8000/#/colecao/exercito-industria-defesa-1934-1936/subcolecao/industria-defesa-1934-1936
- Sessão com índice e notas: http://localhost:8000/#/doc/military-nko35-08-am?colecao=exercito-industria-defesa-1934-1936&subcolecao=conselho-militar-1935
- Dez tabelas: http://localhost:8000/#/doc/military-rkka-raw-materials-1934?colecao=exercito-industria-defesa-1934-1936&subcolecao=industria-defesa-1934-1936
- Relatório Kuibyshev–Berezin: http://localhost:8000/#/doc/military-kpk-kuibyshev-1935?colecao=exercito-industria-defesa-1934-1936&subcolecao=industria-defesa-1934-1936
