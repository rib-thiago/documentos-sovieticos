# Segunda entrega — coleta ampliada e prévia das quatro coleções

**Atualização:** o lote desta prévia foi incorporado ao acervo local após aprovação.
Usar o site normal na porta 8000. Ver [registro e recuperação](INCORPORACAO.md).
As instruções da porta 8001 abaixo documentam a etapa anterior de conferência.

Data: 20/10/2026. A prévia está pronta para conferência manual. O catálogo,
originais, traduções e URLs atuais não foram substituídos. Sem commit ou push.

## Resultados

| Frente | Aquisição e preparação | Versões incluídas na prévia | Unidades retidas |
|---|---|---:|---:|
| Sakharov | 60 páginas russas, 18 extratos ingleses e índice; 11 apêndices individualizados | 72 | 18 |
| Svitlana/Erdogan | 35 índices, 779 URLs candidatas, 792 ocorrências; 67 páginas obtidas | 10 | 58 |
| Mozokhin | Dois PDFs integrais de 2013, pesquisáveis; 295 documentos individualizados | 239 | 56 |
| Brest-Litovsk | 56 sementes tentadas e 18 partes do VII Congresso adquiridas; 51 páginas HTML e um PDF | 42 | 32 |
| **Total preparado** | **527 unidades avaliadas** | **363** | **164** |

A prévia acrescenta **362 documentos**, com **363 versões por idioma**. A diferença
vem das teses de Lenin sobre a paz: português e inglês foram associados ao mesmo
documento após conferir o escopo. Não há alinhamento automático de parágrafos.
Não foram inventadas traduções portuguesas ou inglesas ausentes.

Unidade retida não significa necessariamente erro: pode ser cabeçalho sem corpo,
referência bibliográfica, página composta, tradução alternativa, idioma ainda não
incluído ou texto que exige resolver notas/tabelas antes da incorporação.

## Como abrir e conferir

No terminal, dentro de `/home/thiago/documentos-sovieticos`, executar:

```bash
python3 scripts/coletores/serve_preview.py
```

Abrir **http://127.0.0.1:8001/**. O backend normal pode continuar aberto na porta
8000. A prévia tem seu próprio catálogo e usa os recursos visuais atuais do site.

Coleções:

- [Sakharov](http://127.0.0.1:8001/#/colecao/sakharov-testamento-lenin-2003)
- [Svitlana/Erdogan](http://127.0.0.1:8001/#/colecao/transcricoes-arquivos-sovieticos)
- [Mozokhin](http://127.0.0.1:8001/#/colecao/politburo-trotsky-mozokhin)
- [Brest-Litovsk](http://127.0.0.1:8001/#/colecao/brest-litovsk)

Exemplos diretos:

- [Introdução inglesa de Sakharov](http://127.0.0.1:8001/#/doc/sakharov-2003-en-introduction)
- [Relatório sobre Tiflis, 1903](http://127.0.0.1:8001/#/doc/svitlana-aa02ccdf0bad5a13-tiflis-1903)
- [Mozokhin — documento nº 1](http://127.0.0.1:8001/#/doc/mozokhin-2013-v1-001)
- [Lenin — história da questão da paz infeliz, com português e inglês](http://127.0.0.1:8001/#/doc/brest-lenin-jan-07)

Conferir os seguintes pontos:

1. Abrir cada coleção e suas subcoleções; observar ordem, títulos e idiomas.
2. Abrir os exemplos, usar leitura/estudo, índice e exportação de Markdown.
3. No exemplo de Brest, alternar português e inglês; observar as notas locais.
4. Comparar início e fim dos textos com as fontes preservadas, em especial os
   apêndices de Sakharov e as peças numeradas de Mozokhin.
5. Consultar `unidades-pendencias.csv` para os motivos das retenções. O número de
   fontes descobertas não deve ser confundido com o de documentos incluídos.

A prévia é somente de leitura. Edição, importação de traduções e gravações ficam
no backend normal; não são oferecidas pelo servidor de prévia. Encerrar com
Ctrl+C. Nenhuma ação na prévia incorpora as coleções ao acervo atual.

Se editar o catálogo no backend depois desta preparação, gerar novamente:

```bash
python3 scripts/coletores/preview_catalog.py --build-search
python3 scripts/coletores/serve_preview.py
```

O servidor recusa abrir uma prévia baseada em outra versão do catálogo.

## Fontes e divergências relevantes

**Sakharov:** as páginas curtas de cabeçalhos não foram cadastradas como artigos
vazios. A compilação dos apêndices continua preservada, com onze candidatos
individuais. A nota 1066 russa foi localizada na página seguinte e vinculada sem
deslocamento silencioso. Quatro extratos ingleses permanecem retidos por notas.
Detalhes: [relatório de Sakharov](sakharov-etapa2.md).

**Svitlana/Erdogan:** todos os índices foram adquiridos, mas não todas as 779 URLs.
O lote ampliado obteve 60 páginas adicionais ao piloto, recuperando três timeouts.
As dez unidades incluídas têm decisões de fronteira e metadados registradas; as
demais continuam preservadas para revisão. Há uma referência que incorpora PDF,
sem ser transcrição, e uma ocorrência duplicada de Tiflis retida.
Detalhes: [relatório de Svitlana/Erdogan](svitlana-etapa2.md).

**Mozokhin:** o bloqueio do DjVu Online foi superado por uma fonte alternativa
normal com os dois PDFs de 2013: 514 e 437 páginas. Foi extraída a camada de texto
existente, sem novo OCR. A numeração 1–295 foi conferida com os sumários. Cinquenta
e seis peças estão retidas para notas/tabelas, inclusive os nºs 294 e 295: uma nota
do 294 aparece fisicamente após o início do 295. Os extratos parciais antigos
continuam identificados no histórico e não substituem essas fontes integrais.
Detalhes: [relatório de Mozokhin](mozokhin-etapa2.md).

**Brest:** das 74 entradas finais, 51 têm HTML preservado, uma corresponde a PDF,
sete são índices, nove são referências e seis tiveram acesso bloqueado no Iskra.
As 18 partes do VII Congresso são intervenções e textos de Lenin conforme a
divisão da fonte, não a ata integral do congresso. As versões alemãs e as páginas
de escopo ainda não resolvido permanecem fora da prévia. O PDF é estudo posterior,
identificado como tal, sem presumir transcrição/OCR pronto.

## Preservação e estado da validação

- Fontes, candidatos e inventários ficam em `temporario/coletas-quatro/`, por frente.
- Cada `units.json` registra aptidão, motivo, proveniência e hashes.
- `preview-latest.json` identifica o pacote atual; `unidades-pendencias.csv` permite
  filtrar versões preparadas e retidas em uma planilha.
- `preview/<hash>/files/` contém cópias preparadas dos seis arquivos canônicos,
  manifesto e novos textos. O índice SQLite também é próprio desse pacote.
- O preparador usa a validação do catálogo e o construtor de busca existentes,
  sem alterar o banco ativo ou os arquivos do site. Textos idênticos podem ser
  reaproveitados entre coleções; conflitos de idioma ou de cadastro são retidos.

Catálogo, manifesto e índice SQLite da prévia foram gerados. Houve verificações
focadas dos coletores e do preparador durante o trabalho. **A conferência da
navegação e da renderização no navegador não foi executada e fica com o
pesquisador, conforme solicitado.** Não foram iniciados novos testes após essa orientação.

Após a conferência, a próxima entrega é a incorporação transacional do lote
preparado, com histórico recuperável e atualização do catálogo, manifesto e busca
ativos. A fila de 164 unidades retidas continuará separada para trabalho editorial.
