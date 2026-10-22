# Filas complementares — diagnóstico de 21/10/2026

> Diagnóstico anterior à gravação da reconciliação. Para o estado após a atualização da fila, consulte [o plano consolidado](PLANO-DE-EXECUCAO.md) e [o comprovante](RECONCILIACAO-GRAVACAO.json).

Inventário por leitura dos CSVs/JSONs locais, sem testes, rede ou gravação no acervo. O [JSON](FILAS-COMPLEMENTARES.json) contém 1.406 registros de evidência com chaves estáveis, fonte e hash, classificação, encaminhamento e vínculos à fila pública. **1.406 não é o número de novas pendências**: inclui edições incorporadas, registros estruturais e referências, além de tarefas já representadas na fila pública.

## Contagens e sobreposição

| Origem | Registros inventariados | Relação com a fila pública | Encaminhamento |
| --- | ---: | --- | --- |
| Militares 1934–1936 | 20 documentos | Todos possuem `fonte_militar` | Conferência preventiva; priorizar três documentos com 13 tabelas ao todo |
| Tukhachevsky 1937 | 11 documentos | Todos possuem `fonte_militar` | Dez textos com notas e uma ficha PDF; não anunciar ficha como transcrição |
| Traduções Leningrado/investigação | 17 ressalvas concretas | Mesmos 17 IDs têm apenas alerta de links; motivos específicos NÃO estão representados | Criar motivos próprios de divergência da fonte/tradução, preservando alertas de links |
| Quatro coletores, incorporados | 478 versões em 475 documentos | 475 alertas genéricos + quatro conferências de notas Mozokhin | Não duplicar alerta por idioma; conferir evidências de correções para fechar motivos específicos |
| Quatro coletores, exteriores ao acervo | 785 unidades | Fora da fila pública de documentos incorporados | Separar preparação/coleta da revisão de publicados |
| Perpetrator | 95 arquivos | Comparação auxiliar, não importação autorizada | Manter fora do catálogo; usar para cotejo se necessário |

Os 785 registros exteriores são: 725 candidatos Svitlana, 24 referências Svitlana, três candidatos Brest, duas peças em alemão Brest, 17 referências Brest e 14 registros estruturais Sakharov. Não são 785 documentos faltantes. Uma página pode conter vários documentos; uma referência pode não levar a documento inédito; os 14 de Sakharov não exigem incorporação.

## Estados históricos que não devem ser lidos como pendências atuais

- Os 31 CSVs militares ainda dizem `prepared`, mas as duas gravações registram incorporação (`20261017122946131381-bddf1fec4801` e `20261017123705853113-8b07729738b6`). Isso descreve a preparação histórica, não falta de cadastro. As 20 fontes HTML de 1934–1936 existem localmente.
- O README de 1937 ainda contém o estado histórico “sem commit e sem push”. Não foi usada essa frase para inferir o estado Git atual. A fila deve ser reconciliada por conteúdo e recibos, não por rótulo narrativo antigo.
- `units.json` pode preservar flags como `canonical_import_performed:false`/`not_public_catalog:true`: são inventários de preparação, não recibos atuais. `ESTADO-ATUAL.json` registra incorporação com ID, idioma e hash; seu snapshot atual é de 21/10/2026 20:25 UTC.
- Mozokhin nº 100 já está incorporado. Sua retenção antiga e a falta das quatro unidades inglesas Sakharov são estados superados; permanecem ressalvas preventivas, não lacunas de incorporação.
- Os três alertas adicionais de versões Brest não faltam: 73 versões correspondem a 70 documentos; três idiomas compartilham cadastro. Não criar três documentos ou alertas artificiais.

## Trabalhos que agentes podem preparar

### M1 — tabelas militares, três documentos

`military-rkka-raw-materials-1934` (dez tabelas), `military-gosplan-aircraft-1935` (duas), `military-aviation-korolev-1935` (uma). Fontes HTML, Markdown de revisão e aquisição em `.local/research/military-1934-1936/`. Cotejar cada célula, cabeçalhos compostos, mesclas, campos vazios, totais e unidades. Entregar diferenças por tabela com hash da versão corrente. A representação de mesclas não é, por si, erro. Não alterar números por plausibilidade.

### M2 — notas e fronteiras militares, 27 documentos textuais restantes

Dividir por coleção/sessão, sem dois agentes editarem a mesma edição. Os lotes podem ser 13 documentos de Conselho1935, quatro textos de indústria sem tabelas e dez textos1937. Cotejar chamadas/definições contra HTML, títulos, assinaturas, começo/fim e extração completa. O protocolo1935 tem data própria versus período do evento: distinguir campos, não “corrigir” a fonte. As transcrições1937 tiveram 201 definições convertidas; isso é transformação já aplicada, não erro ainda comprovado.

### M3 — julgamento1937, tarefa independente por página

`fontes/tukhachevsky/julgamento-1937-06-11.ru.pdf`: 172 páginas físicas, fonte digitalizada. Aplicar OCR russo em área de trabalho, guardar página física/impressa, imagens, texto bruto e correções. Dividir em intervalos contíguos, revisão cruzada de limites e transferência de notas. O PDF inglês tem143 páginas e é publicação distinta; não alinhar automaticamente. Só substituir/complementar a ficha depois de transcrição conferida e decisão editorial explícita. Checar existência de transcrição feita pelo usuário na ferramenta antes de iniciar novo trabalho; o diagnóstico não leu projetos privados de OCR para presumir ausência absoluta.

### T1 — divergências RU/PT/EN de Leningrado, 17 casos

Dividir em dois lotes por IDs: 2685,2717,2723,2782,3020,3022,3041,3042,3043; 3064,3112,3129,3131,3172,3175,3176,3228. Fontes: Markdown russo e traduções correntes, notas dos quatro lotes em `docs/traducoes/leningrado-investigacao/`, HTML original quando preservado. Distinguir tradução corrigível de erro literal ou contradição histórica. Exemplos: ano19343, cronologia1931/1934, patronímico Antonov, frase interrompida e siglaGUGV. Resolver tradução mal interpretada com evidência; manter grafia/cronologia da fonte e registrar nota. Quando exigir imagem inexistente, declarar bloqueio específico, sem encerrar como corrigido.

### C1 — Svitlana, maior volume

779 URLs adquiridas,34 versões incorporadas;725 retidas e24 referências. Os primeiros lotes devem agrupar série de origem e candidatos compostos, priorizando118 páginas cuja reconversão recuperou texto antes omitido; esses conjuntos se sobrepõem. Entregar fronteiras, início/fim, notas, autoria atribuída pela fonte, proveniência e diagnóstico de duplicidade, sem impor alinhamento entre idiomas. O plano deve reservar agente de integração único. As24 referências são páginas de apontamento: extrair URLs de PDFs, verificar duplicidade e baixar somente fontes integrais identificáveis em etapa autorizada de aquisição. Uma ligação conhecida é `https://istmat.org/node/27376` versus `tukhachevsky-nko37-01-pm`: exige cotejo antes de vincular inglês.

### C2 — Brest, cinco candidatos e17 referências

Retidos: `brest-lenin-1920-brest`, `brest-bukharin-anarquia-traducao-alternativa`, `brest-tratado-avalon`; alemães: `brest-central-feb-22-alemao`, `brest-central-feb-23-alemao`. Um agente trata fronteiras e variantes, outro segue referências depois de priorização. Não substituir atas completas por discursos de Lenin; não duplicar tratado sem caracterizar testemunho textual. PDF historiográfico1981 já extraído em505 páginas: usar `temporario/coletas-quatro/brest/pdf-study/` e `BREST-PDF-RODADA3.md` para localizar fontes primárias, não importar narrativa como documento1918. Índices RSL/EBID e referências de livro não equivalem a texto integral.

### P1 — Perpetrator, auxiliar e condicionado

95 arquivos:11 candidatos a redundância integral,20 sobreposições,64 sem correspondência detectada. Em19 arquivos há876 marcadores de notas sem conteúdo. A reconstrução possível deve partir dos Word preservados, não inventar notas. Compilações podem conter trechos exclusivos, e similaridade não certifica identidade. **Não é tarefa de importar coleção Perpetrator**: conservar como testemunho externo, usar apenas para reparar/cotejar documentos já autorizados; qualquer incorporação nova fica condicionada a decisão posterior do responsável. Os19 alertas estão vinculados aos95 registros no JSON, evitando contá-los como19 arquivos adicionais.

## Regras de avanço e integração

Agentes produzem candidatos e relatório por ID/idioma, com hash inicial, fonte verificável, trechos antes/depois e motivo. Um integrador confere conflitos e executa transações com histórico; não sobrescrever edições humanas recentes. Reconciliar a fila por motivo, não por documento inteiro: resolver notas não resolve links, e adquirir uma fonte não conclui a revisão. Encerrar alerta só quando houver evidência relativa ao estado corrente. Reservar estados distintos para corrigido, falso positivo demonstrado, ressalva literal preservada e bloqueado por fonte ausente. Registrar progresso em unidades únicas por ID+idioma+motivo e nunca somar os785 exteriores às2.889 pendências públicas.
