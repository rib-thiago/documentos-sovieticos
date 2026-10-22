# Reconciliação por escopo da pendência — 21/10/2026

> Diagnóstico anterior à gravação da reconciliação. Para o estado após a atualização da fila, consulte [o plano consolidado](PLANO-DE-EXECUCAO.md) e [o comprovante](RECONCILIACAO-GRAVACAO.json).

Nenhuma alteração de fila ou acervo foi feita por esta auditoria. O arquivo `proposals-reconciliation.json` fornece quatro atualizações de descrição, preservando chave, status e prioridade. Não propomos encerramentos: as linhas existentes pedem conferências que vão além das intervenções já comprovadas.

## Quatro correções Mozokhin

Os documentos 054, 101, 145 e 146 tiveram atribuição de notas corrigida no histórico `20261021172931544115-d005bfa87be7`. Nesta auditoria, o SHA-256 de cada Markdown atual foi comparado diretamente com o candidato corrigido em `temporario/coletas-quatro/mozokhin/units.json`: quatro coincidências. A evidência é o recibo `mozokhin-correcao-notas-20261021-gravacao.json`, complementado por `NOTAS-RODADA3.md` e CSV por documento.

As quatro linhas `conferencia_notas_20261021` já dizem que a atribuição foi corrigida; portanto não são quatro erros ativos de atribuição. São conferências preventivas posteriores. As quatro linhas genéricas `coleta_quatro_colecoes` continuam pendentes porque cobrem também OCR, fronteiras, datas, autoria e tipo documental. A correção de notas não prova revisão integral desses aspectos.

## Demais frentes

| Grupo | Registros atuais | Diagnóstico e próximo trabalho |
|---|---:|---|
| mozokhin | 299 | 295 documentos e quatro conferências posteriores. As 53 liberações da rodada 3 corrigiram pontos específicos; registrar esse resultado por componente, sem encerrar conferência integral. O nº 100 tem carta/colunas/anos/notas cotejados e incorporação comprovada. Suas 858 linhas físicas, 863 assinaturas declaradas e rótulo final 865 são discrepâncias preservadas da fonte. Não tentar corrigi-las inventando signatários; identificação histórica externa é outra tarefa. |
| sakharov | 76 | 76 unidades incorporadas. SAKHAROV-FECHAMENTO.json comprova integridade, fronteiras e ausência de lacunas no conjunto HTML inventariado; seu escopo exclui revisão filológica integral. Quatro extratos ingleses receberam notas editoriais suplementares: o cotejo da tradução dessas notas continua uma tarefa legítima. Os 14 registros estruturais não representam textos faltantes. |
| svitlana | 34 | 34 versões incorporadas. O recibo SVITLANA-21-CONFERENCIA-GRAVACAO.json comprova hashes e gravação das 21 adicionais; não prova revisão integral de metadados e aparato. Não confundir a fila do catálogo com centenas de candidatos ainda fora dele. |
| confessionezhov | 24 | 24 registros. Individualização literal registrada em recortes.csv e proveniencia.json; compilação preservada. Divergências de data, rótulo e idioma são explicitadas; igualdade de blocos não comprova equivalência semântica. Conservar ressalvas e cotejar os três idiomas, sem corrigir silenciosamente. |
| military | 20 | 31 registros de fonte militar. As conversões de notas e inspeções de fronteiras estão documentadas; continuam conferência de chamadas, tabelas, fidelidade da fonte e apresentação. A ficha do PDF do julgamento não é uma transcrição. Restrições de acesso/fonte devem ser classificadas como tais, não como defeitos de Markdown corrigíveis. |

## Evidências e critérios

- `docs/pesquisa/quatro-coletores/MOZOKHIN100-RODADA5.md` e `MOZOKHIN100-CONFERENCIA-GRAVACAO.json`: cotejo e hash da incorporação.
- `docs/pesquisa/quatro-coletores/SAKHAROV-FECHAMENTO.json`: escopo explícito de integridade/estrutura, não filologia integral.
- `docs/pesquisa/quatro-coletores/SVITLANA-21-CONFERENCIA-GRAVACAO.json`: gravação de 21 versões, não todos os candidatos.
- `docs/pesquisa/individualizacao-ezhov/README.md`, `proveniencia.json`, `recortes.csv`: recortes e divergências preservadas.
- `docs/pesquisa/colecao-militar-1934-1936/README.md` e `docs/pesquisa/colecao-tukhachevsky-1937/README.md`: âmbito das conversões e limites das fontes.

O recibo de gravação prova a operação realizada. O hash igual prova qual versão atual foi auditada. Nenhum dos dois, sozinho, prova a qualidade integral da edição. Fechamento futuro exige comparar o escopo exato da linha com evidência do mesmo escopo. Não foram executados testes, commit ou push.

