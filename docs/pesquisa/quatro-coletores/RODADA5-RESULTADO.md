# Incorporação Svitlana e fechamento Sakharov/Mozokhin

21/10/2026. Resultado local: **22 documentos/22 versões acrescentados**, com histórico recuperável, catálogo, manifesto e busca atualizados. Nenhum texto ou tradução anterior foi substituído. Não houve commit nem push.

## Svitlana: 21 unidades incorporadas

As 21 peças da prévia da rodada 4 estão agora no acervo. A coleção passa de 13 para **34 versões incorporadas**. Incluem 16 peças individuais e cinco unidades obtidas das duas páginas compostas: carta de Ezhov, telegrama anexo de Uspensky, tratado preliminar, anexo de armistício e instrumento de ratificação de 1920.

O telegrama sem data própria não herdou a data da carta; cotas compartilhadas e notas foram atribuídas conforme as decisões de individualização. Permanecem registradas as limitações das fontes e traduções de trabalho.

- Histórico: `20261021202030701731-12da7260f03e`.
- [Comprovante da transação](svitlana-21-rodada5-gravacao.json).
- [Conferência dos 21 arquivos gravados](SVITLANA-21-CONFERENCIA-GRAVACAO.json): todos os hashes coincidem com as edições cadastradas.

Isso não conclui a frente Svitlana: permanecem 725 unidades retidas para revisão e 24 referências/envoltórios de PDF. As 744 páginas sem decisão editorial apontadas na rodada 4 ainda exigem cotejo. Os arquivos coletados e as versões anteriores da reconversão permanecem preservados.

## Mozokhin: nº 100 incorporado; 295 documentos no acervo

A carta de Smilga de 18 de outubro de 1927 e sua lista foram cotejadas nas páginas PDF 171–180. O trabalho foi dividido entre agentes, com leitura sequencial das 858 linhas nas imagens da edição. Corrigiram-se espaços de extração em três sobrenomes, oito anos fragmentados e a separação da observação «кандидат»; campos vazios e rótulos irregulares foram mantidos.

A edição declara 863 assinaturas, a lista reconstruída apresenta 858 linhas físicas e termina no rótulo 865. A nota editorial explicita essas informações diferentes. Não foram renumeradas as linhas nem inventados os nomes nas duas posições retocadas. O cotejo é com a edição impressa digitalizada; não estabelece identidade prosopográfica nem equivalência com o testemunho arquivístico original.

A unidade foi cadastrada com data literal, referência arquivística e proveniência. Seu texto inclui sete tabelas por página, notas 38/39 e referência final. A conferência após gravação confirmou hash, 858 linhas numéricas e definições das duas notas.

- Histórico: `20261021202407360792-27bacdd7df3d`.
- [Comprovante da transação](mozokhin-100-rodada5-gravacao.json).
- [Cotejo e ressalvas](MOZOKHIN100-RODADA5.md).
- [Conferência da gravação](MOZOKHIN100-CONFERENCIA-GRAVACAO.json).

A retenção estrutural do último documento desta edição coletada está resolvida. A revisão crítica habitual, a qualidade lexical dos demais OCRs e o cruzamento de pessoas/fontes continuam sendo trabalho editorial posterior; não se declara revisão palavra por palavra de todos os 295 documentos.

## Sakharov: nenhuma importação adicional necessária

A conferência dos 90 registros confirmou os hashes das fontes e candidatos e a coincidência das 76 unidades aptas com as 76 edições canônicas. Os 14 registros restantes são 13 divisores de capítulo e uma compilação cujos 11 apêndices já estão individualizados.

Foi corrigido o motivo obsoleto que indicava individualização pendente da compilação. O registro passou de prioridade alta para informativa, com snapshot recuperável e ajuste do gerador para não ressuscitar a falsa pendência. Nenhum texto canônico foi alterado. Os quatro extratos ingleses mantêm os suplementos editoriais das 14 notas já incorporadas.

[Relatório de fechamento](SAKHAROV-FECHAMENTO.md), com limites: conclusão do conjunto HTML inventariado e de sua preparação estrutural, sem certificação filológica integral ou aquisição de todas as manifestações bibliográficas alternativas.

## Como conferir manualmente

Com `python3 -m backend` em execução:

1. Abrir [Mozokhin nº 100](http://127.0.0.1:8000/#/doc/mozokhin-2013-v1-100). Conferir carta, nota editorial das contagens, sete seções da lista e notas 38/39. No final, os rótulos 949/950 permanecem antes de 851, conforme a edição.
2. Comparar [carta de Ezhov](http://127.0.0.1:8000/#/doc/svitlana-4898e43af1b5adac-ezhov-cover-1938-04-15) e [telegrama de Uspensky](http://127.0.0.1:8000/#/doc/svitlana-4898e43af1b5adac-uspensky-telegram-926). As notas do telegrama não devem aparecer como notas da carta; a data própria do telegrama continua não informada.
3. Abrir [tratado preliminar](http://127.0.0.1:8000/#/doc/svitlana-c5ed6f188cc197d3-preliminary-peace-1920-10-12) e navegar pela coleção para localizar o anexo e a ratificação.
4. Em Sakharov, conferir os extratos ingleses 10–13 e os apêndices 1, 8 e 11. Não haverá novos documentos desta frente: a mudança foi corrigir o inventário de pendências.

Acervo total após as duas transações: **2.727 documentos e 3.859 versões**, 20 coleções e 61 subcoleções. O [estado atualizado](ESTADO-ATUAL.md) e seu CSV distinguem unidades incorporadas, estruturais, referências e retenções.

Não foram executadas suítes de testes nem testes no navegador. Foram realizadas conferências de fonte, integridade dos arquivos e validações transacionais do gravador existente. As versões e os registros anteriores permanecem nos diretórios de revisão e no histórico editorial local.
