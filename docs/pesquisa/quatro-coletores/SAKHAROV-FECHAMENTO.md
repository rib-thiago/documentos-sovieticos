# Sakharov — fechamento da coleta e da preparação estrutural

21/10/2026. A aquisição e a incorporação do conjunto HTML inventariado estão concluídas: **76 unidades no acervo**, correspondentes aos candidatos atuais. Nenhuma unidade adicional precisava ser importada nesta rodada. Isso não equivale a revisão filológica integral nem a aquisição de todas as edições e PDFs alternativos citados pelo projeto de coletor.

## O que foi conferido agora

- Os 90 registros têm arquivos brutos e Markdown existentes; seus hashes coincidem com os campos superiores e internos de `units.json`.
- As 76 unidades aptas coincidem, por conteúdo e hash, com as 76 respectivas edições canônicas e os hashes do catálogo. Não houve substituição de edição nem gravação de texto público.
- As 13 páginas de cabeçalho não contêm corpo além dos títulos Markdown. Todas estão preservadas na compilação russa, com marcadores explícitos da URL e do identificador de origem.
- Os 11 apêndices compartilham a mesma fonte bruta, apresentam números 1–11 sem lacunas e fronteiras adjacentes coincidentes; seus 11 textos já estão no acervo. A conferência é estrutural e por integridade, apoiada na individualização HTML registrada anteriormente.
- As duas compilações integrais têm hashes válidos e contêm os marcadores de todas as unidades de página dos respectivos idiomas.
- Os quatro extratos ingleses `en-nav-10`, `-11`, `-12` e `-13` já incorporam o suplemento editorial anteriormente preparado: 14 notas, com tradução identificada como editorial, texto russo literal e proveniência. A fonte inglesa não foi silenciosamente corrigida. O caso da nota 1066 atravessando páginas russas permanece documentado.

O diagnóstico por unidade está em [SAKHAROV-FECHAMENTO.json](SAKHAROV-FECHAMENTO.json). A decisão das notas está em [NOTAS-RODADA3.md](NOTAS-RODADA3.md).

## Por que ainda aparecem 14 registros fora do acervo

São **13 divisores de parte/capítulo e uma compilação dos apêndices já individualizados**. Não representam 14 documentos faltantes. Importá-los como textos autônomos criaria páginas vazias ou duplicação dos apêndices.

Foi corrigido um motivo obsoleto em `sakharov-2003-ru-nav-59`: dizia que a individualização ainda precisava ser validada. O candidato agora explica que se trata de compilação estrutural preservada, cujos 11 apêndices já foram separados. Sua prioridade local passou de alta para informativa; a elegibilidade continua falsa. A mesma formulação foi aplicada ao gerador para não reapresentar a falsa pendência em futura preparação.

Essa correção alterou apenas metadados de trabalho em `units.json`, a linha correspondente em `unit-plan.csv` e o gerador. O snapshot anterior e a decisão com hashes estão em `temporario/coletas-quatro/sakharov/reviewed/sakharov-closure-20261021/`. Originais, traduções, catálogo, manifesto, busca e fila editorial pública permaneceram intactos nesta frente.

## O que ainda pode evoluir

Resta a revisão editorial habitual dos textos e traduções: grafia, referências bibliográficas, qualidade de tradução e avaliação crítica do conteúdo. Não foi feito cotejo palavra por palavra de toda a obra. PDFs alternativos e outras manifestações bibliográficas são possíveis ampliações futuras, não faltas de corpo documental identificadas no inventário HTML já incorporado. Não houve novo acesso de rede nesta conferência.

Para conferir manualmente, abra os extratos ingleses 10–13 e localize o suplemento editorial; compare as notas com o russo literal e suas URLs. Depois abra os apêndices 1, 8 e 11: confira início/fim, a tabela do nº 8 e a referência final do nº 11. As compilações e o HTML bruto estão preservados na área de trabalho para comparação.

Sem execução de suites de testes ou navegador, sem commit e sem push. Foram realizadas somente leituras de integridade, conferência dos registros estruturais e correção de metadado de trabalho.
