# Onda 1 — cotejo das tabelas militares

Lote `R1-fontes_militares-0001`, 21/10/2026. **Três prevenções prontas para encerramento pelo integrador; nenhuma alteração textual necessária.** Fila e acervo não foram gravados por este preparador.

| Documento | Tabelas | Células físicas HTML | Posições cotejadas no Markdown | Mesclas HTML | Vazios HTML | Parágrafos fora das tabelas | Notas |
|---|---:|---:|---:|---:|---:|---:|---:|
| military-aviation-korolev-1935 | 1 | 25 | 24 | 5 | 0 | 58 | 7 |
| military-gosplan-aircraft-1935 | 2 | 73 | 71 | 5 | 1 | 41 | 5 |
| military-rkka-raw-materials-1934 | 10 | 257 | 245 | 16 | 34 | 49 | 1 |
| **Total** | **13** | **355** | **340** | **26** | **35** | **148** | **13** |

As contagens de células físicas e posições representadas diferem porque cabeçalhos multinível são reunidos; não indicam células perdidas. Cada posição tem valor esperado/real e coordenadas no registro detalhado. Nenhuma divergência encontrada. Os números não foram recalculados ou corrigidos por plausibilidade.

## Método e evidência

As cópias HTML em `.local/research/military-1934-1936/raw/` foram confrontadas com os hashes de aquisição. Capturas Wayback, URLs e hashes canônicos estão em [result.json](../../../temporario/revisao-onda1/militares/result.json) e [cotejo.json](../../../temporario/revisao-onda1/militares/cotejo.json). Esses caminhos são locais de trabalho, não material público do site.

Receita: `scripts/revisao_acervo/audit_military_tables.py`, executada com `/tmp/brest-round3-venv/bin/python`, ambiente já disponível com BeautifulSoup. A receita não importa nem reaplica o conversor original. Expande separadamente coordenadas HTML e confere todas as células representadas, cabeçalhos, continuações `↳`, vazios, unidades e valores. Remove apenas formatação Markdown e espaços na comparação; preserva números e pontuação. Todos os 148 parágrafos fora das tabelas foram localizados na mesma ordem, incluindo chamadas, definições e referências arquivísticas. Os treze sinais de nota têm chamada e definição no Markdown.

As tabelas de matérias-primas conservam relações ano/necessidade/produção e os cabeçalhos de amônia e de capacidade de produção. A primeira tabela Gosplan conserva produção de 1932/1933 e plano/relatório de 1934; a segunda conserva a célula inicial mesclada e os percentuais. Korolev conserva velocidade por altitude, tempo de subida, teto e tiros por minuto, inclusive `10,5`.

## Limites da fonte preservados

- Korolev: a nota 2 informa que uma tabela comparativa internacional foi omitida **na publicação-fonte**; notas 3–6 informam outras omissões. Não há tabela HTML perdida para reconstruir.
- Gosplan: a nota 3 declara anexos não publicados; a nota 5 enumera seções omitidas. A referência `Л. 62-57` e a formulação `1933 гг.` estão no HTML e foram mantidas, sem correção silenciosa.
- Matérias-primas: a nota remete ao documento de 9/9/1933. O documento presente termina com assinaturas, anotação de Tukhachevsky, essa nota e referência RGVA; essas fronteiras foram preservadas.
- Os rótulos neutros `Показатель`/`Столбец` em cabeçalhos vazios e a nota de representação das mesclas já existentes são recursos de apresentação. Não foram confundidos com palavras literais da fonte.

## Integração

Encerrar somente `military-aviation-korolev-1935:fonte_militar`, `military-gosplan-aircraft-1935:fonte_militar` e `military-rkka-raw-materials-1934:fonte_militar`, após o integrador confirmar os hashes registrados. Resultado: `alerta_obsoleto_ou_falso_positivo`, pois o alerta era preventivo e as tabelas já estavam reconstruídas corretamente. Isso não certifica verdade histórica das cifras nem cotejo do manuscrito arquivístico.

Sem mudanças de parágrafos, candidatos ou diffs: não há impacto em traduções, marcadores ou correções de trecho. Não foram executados testes, suítes, navegador, commit ou push.
