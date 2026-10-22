# Quatro coletores — acompanhamento

**Estado mais recente:** [incorporação das 21 unidades Svitlana e fechamento Sakharov/Mozokhin](RODADA5-RESULTADO.md). Mozokhin possui 295 documentos incorporados; Sakharov, 76 unidades. [Estado geral atualizado](ESTADO-ATUAL.md).

Incorporações anteriores: [continuação da coleta de 21/10](RODADA3-RESULTADO.md).

## Incorporação inicial — histórico

[Incorporação definitiva no acervo local](INCORPORACAO.md).
As quatro coleções estão no site normal, com 362 novos documentos, 363 versões
por idioma e histórico recuperável. Há 362 novas entradas na fila editorial e
164 unidades retidas fora do catálogo. Sem commit ou push.

Histórico da preparação: [segunda entrega — coleta ampliada e prévia](ETAPA-2.md).

## Primeira entrega — histórico

Data: 20/10/2026. Esta entrega adapta os coletores e executa pilotos de aquisição
e conversão. Não é a incorporação integral das quatro coleções no site.

As frentes foram divididas entre três agentes auxiliares e o agente principal.
Cada frente trabalhou em diretório próprio; o catálogo público permaneceu
inalterado. Não houve commit nem push.

## Resultados reais

| Frente | Aquisição e conversão | Limite ou próximo trabalho |
|---|---|---|
| [Sakharov](sakharov.md) | Três páginas russas e um extrato inglês convertidos; índice inglês preservado, com 18 links identificados | Individualizar apêndices; conferir chamada de nota 1066 e correspondências entre idiomas |
| [Svitlana/Erdogan](svitlana.md) | Dois índices, 63 URLs candidatas e sete páginas inglesas convertidas | Separar páginas compostas e resolver metadados contraditórios; não são 63 documentos obtidos |
| [Mozokhin](mozokhin.md) | Segmentador adaptado; dez segmentos experimentais de extratos identificados | Zero documentos integrais adquiridos: acesso direto devolveu verificação; todos os segmentos estão bloqueados para incorporação |
| [Brest-Litovsk](brest.md) | Três páginas convertidas: duas inglesas e uma portuguesa; inventário das 56 sementes preservado | Fonte russa do Iskra bloqueada na consulta a robots.txt; 52 sementes ainda não adquiridas |

São 14 páginas convertidas de fontes HTML adquiridas, além dos dez segmentos
experimentais parciais de Mozokhin. Páginas, segmentos, entradas de inventário e
documentos históricos não são unidades equivalentes.

## Registro central

Área de trabalho: `temporario/coletas-quatro/`.

- `revisao.json`: resumo por frente, arquivos, hashes, estados, motivos e sugestões de correspondência com o catálogo.
- `pendencias.csv`: fila legível por planilha, com prioridade e motivo.
- Diretórios de cada frente: fontes, candidatos e inventários detalhados.

Regerar a consolidação sem acessar a rede ou alterar o site:

```bash
python3 scripts/coletores/consolidar.py
```

A consolidação compara URLs, inclusive capturas Wayback com a URL original, e
hashes dos candidatos com as edições cadastradas. Correspondência de URL não
comprova equivalência textual ou tradução integral. Nenhum resultado é mesclado
automaticamente. A referência `istmat.org/node/27376` foi conciliada com
`tukhachevsky-nko37-01-pm`, em `reference_matches`; não foi recriada nem associada
a uma tradução inglesa por suposição.

Todos os candidatos desta rodada têm `ready_for_import: false`. Os arquivos
Markdown servem à conferência, não representam aprovação editorial ou novas
URLs públicas. Os motivos específicos dos relatórios de Sakharov e Svitlana
também são incorporados à fila central.

## Como conferir

1. Abrir `pendencias.csv` em uma planilha ou os relatórios acima no editor.
2. Em `revisao.json`, escolher uma entrada com `markdown` e `raw` preenchidos.
3. Abrir os dois caminhos: o HTML no navegador e o Markdown no editor com prévia.
4. Comparar início, fim, títulos, notas, tabelas e fronteiras entre peças.
5. Em Mozokhin, observar `input_kind: web_excerpt` e `fulltext_acquired: false`;
   esses extratos não substituem o livro integral nem devem ser publicados.

Os coletores não sobrescrevem o trabalho publicado. Para revisar um candidato,
usar cópia editorial ou o fluxo de trabalho indicado no README da frente. Os
snapshots por hash servem para preservar a fonte e reproduzir a conversão.

## Verificações concluídas

- Sakharov: três testes de preservação e atualização do inventário.
- Svitlana/Erdogan: quatro testes de extração estrutural, ocorrências e preservação.
- Mozokhin: sete testes e ensaio de uma lacuna sobre extrato identificado.
- Brest: cinco testes de preservação, retomada, relatórios e links.
- Consolidação: quatro testes de integridade, limites de diretório e conciliação sem escrita no catálogo.

Total: 23 testes focados aprovados, além das aquisições remotas descritas.
A consolidação dos arquivos presentes não encontrou hashes divergentes ou
arquivos ausentes. A conferência Git não apontou alterações nos arquivos
versionados de `data/`, `originais/`, `backend/`, `assets/` ou `index.html`.

## Sequência de implementação

1. Aplicar os achados dos pilotos à preparação de unidades documentais:
   apêndices, páginas compostas, notas e metadados do corpo.
2. Ampliar a aquisição por lotes retomáveis, mantendo falhas e fontes parciais
   separadas dos textos completos. Para Mozokhin, obter fonte integral acessível
   antes de declarar a coleção coletada; a adaptação também aceita arquivo local.
3. Emitir prévia de novos documentos, edições e participações, com deduplicação
   e títulos portugueses de identificação. Não inventar traduções ausentes.
4. Incorporar pelo fluxo transacional existente, com histórico recuperável,
   atualizando catálogo, manifesto e busca. Conservar IDs e URLs existentes.

A camada de coleta ainda é de linha de comando. Expor esses processos como
ferramentas da bancada exige uma etapa própria de interface e execução de tarefas;
não foi acrescentada nesta rodada.
