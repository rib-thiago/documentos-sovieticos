# Onda 2 — recortes, ressalvas, títulos e listas

Rodada local de 22/10/2026. Foram encerrados **47 apontamentos**; o saldo passou de **2.829 para 2.782 abertos**. São 70 edições alteradas em 34 documentos. Não significa revisão crítica integral desses documentos nem conclusão de toda a onda 2 do plano.

O OCR do julgamento de Tukhachevsky foi adiado: a ferramenta já existe, mas a transcrição e conferência das páginas constituem uma entrega própria. Nesta rodada foram priorizadas intervenções delimitadas, sustentadas pelo material local. Projetos, PDFs de trabalho, originais TXT, URLs e identidades documentais foram preservados. Não houve testes de aplicação, commit ou push.

## Ezhov

As 72 edições das 24 peças foram comparadas com os intervalos de bytes e linhas registrados na proveniência. Todas coincidiam com os recortes originais; os intervalos eram contíguos, sem lacuna ou sobreposição. Títulos, notas e referências pertencentes aos recortes foram preservados. Essa conferência encerrou **18 dúvidas preventivas de individualização**, não aprovou semanticamente todas as traduções.

**Uma correção textual foi aplicada em EN013:** `I could have done anything at all then…` passou a `I was not capable of anything then…`. O contexto russo diz `Я тогда ни на что не был способен…`; o português já dizia “Eu então não era capaz de nada…”. Somente essa frase inglesa foi alterada. A compilação mantém a tradução anterior e sua URL; peças individualizadas têm vida editorial própria, sem sincronização automática com a compilação. A diferença agora está registrada no histórico e na evidência da revisão.

Continuam em revisão EZH-002, 013, 015, 019, 020 e 025: classificação/título de declaração, datas numéricas e atribuições divergentes. Não se reinterpretou silenciosamente dia/mês nem se escolheu uma data externa por plausibilidade. A nota biográfica de EZH-001 foi preservada, sem validação histórica de suas afirmações.

Evidência: `temporario/revisao-onda2/ezhov/evidence.json`; relatório de escopo e limites: `temporario/revisao-onda2/ezhov/RESULTADO.md`.

## Leningrado

Os 17 pontos sinalizados foram cotejados no HTML russo preservado e nas versões RU/PT/EN. As dificuldades examinadas já constam da publicação eletrônica russa. Não são, por isso, erros comprovados de tradução.

Foram acrescentadas **51 notas editoriais, uma por idioma de cada documento**, após o conteúdo existente, separadas por linha e bloco de citação, com autoria explícita “Documentos Soviéticos”. O conteúdo anterior permanece como prefixo byte a byte de cada candidato. As notas novas não são apresentadas como notas do publicador russo ou afirmações dos depoentes.

Onze ressalvas foram tratadas com preservação e explicação da fonte: 2685, 2717, 2782, 3020, 3022, 3041, 3042, 3043, 3129, 3172 e 3228. “Corrigido” na fila significa que esse encaminhamento editorial foi concluído, não que se tenham emendado as anomalias ou cotejado o arquivo original. Por exemplo, “19343”, “219”, as chamadas [2]/[2i] e a sigla GUGV continuam literais.

Seis casos permanecem **em revisão**, apesar da advertência já disponível ao leitor: 2723 (identificação), 3064 (relação entre datas), 3112, 3131, 3175 e 3176 (sintaxe/leituras que exigem outro testemunho). Não se inseriu negação, suprimiu nome ou inverteu sentido por conjectura.

O cotejo também limitou avisos excessivos: a cota 66–98 de 3129 não prova truncamento; a direção Moscou em 3064 não contradiz, por si, visitas posteriores a Leningrado; o aviso biográfico genérico de 2717 não foi tomado como inconsistência estabelecida entre pessoas distintas.

Evidência: `temporario/revisao-onda2/leningrado-evidencias.json`; cotejo detalhado: `temporario/revisao-onda2/cotejo-leningrado.md`. A planilha histórica de ressalvas da tradução permanece como registro de origem; a situação atual está na fila principal, não em uma segunda fila independente.

## Títulos e listas

Foram recuperados **22 títulos literais**:

- 1790: seis títulos, incluindo as duas ocorrências de “ОБВИНИТЕЛЬНОЕ ЗАКЛЮЧЕНИЕ” em seus contextos distintos e as seções I/II/III. Não se fundiu a folha de rosto com o corpo da acusação.
- 4828: quatro cabeçalhos anuais explícitos, após a grade financeira já reconstruída na onda 1. Os números dos beneficiários não foram promovidos a títulos. Isso também encerrou a decisão editorial anterior sobre a disposição da tabela.
- 1611, 2484, 5793 e 6958: doze ocorrências de títulos repetidos, desambiguadas por sua posição e contexto, com cotejo integral e ordenado do texto HTML. Cada ocorrência foi preservada.

Foram encerrados os **cinco avisos de títulos ambíguos** existentes. Os alertas de links dos mesmos documentos permanecem abertos. Nos textos longos, o inventário dos 235 alertas não encontrou tags HTML H1–H6: isso não prova ausência de divisões tipográficas. A recuperação continua exigindo examinar parágrafos, estilos e contexto; não será feita pela invenção automática de subtítulos temáticos.

Nos dez documentos com aviso de lista, foram recuperados **57 itens de 24 listas HTML**, preservando conteúdo, ordem e pontuação. São 12 edições: dez russas e as traduções PT/EN de 3246. Nesse documento, os sete itens e a ordem nominal foram cotejados nos três idiomas; não se declarou revisão integral da tradução.

Particularidades preservadas: início 366 em 6431; item 9 em 7196, sem corrigir a pontuação anterior `8..`; quatorze listas de um item em 6711; alemão e russo publicados na mesma edição de 10801. Nenhuma numeração foi completada por palpite.

As alterações de título e lista são inserções de prefixos nos pontos comprovados: sua remoção recupera exatamente o conteúdo anterior. Evidências e diffs: `temporario/revisao-onda2/secoes1790/`, `secoes4828/`, `titulos/` e `listas/`. Resultados do mesmo lote foram agrupados para uma única integração, sem alterações concorrentes do mesmo documento.

## Gravação e recuperação

| Entrega | Histórico recuperável | Comprovante |
| --- | --- | --- |
| Ezhov | `20261022030213010022-8d87ece4d0b3` | [Recibo](onda2-ezhov-20261022-gravacao.json) |
| Leningrado | `20261022030537438381-16089cc608b5` | [Recibo](onda2-leningrado-20261022-gravacao.json) |
| Seções 1790 e 4828 | `20261022030827836381-16ac18bef1fd` | [Recibo](onda2-secoes-20261022-gravacao.json) |
| Demais títulos e listas | `20261022031029915488-1c4003a6ddd5` | [Recibo](onda2-listas-titulos-20261022-gravacao.json) |

As gravações usaram prévia, hashes anteriores, verificação de conflitos, histórico e atualização de catálogo, manifesto e busca local. Não havia âncoras PDF públicas nos idiomas alterados exigindo migração. Não foram sobrescritos rascunhos de projetos. As proteções de marcadores da onda 1 continuam aplicáveis: marcas antigas curtas podem exigir nova marcação quando muda a versão textual.

O manifesto de despacho e a fila de entrada estão preservados em `temporario/revisao-onda2/baseline/`. [Artefatos congelados](ONDA2-ARQUIVOS-PRESERVADOS.json) e [progresso por lote](PROGRESSO.json) permitem retomar sem reaplicar candidatos sobre edições posteriores. Os preparadores são receitas da revisão, não comandos de manutenção a executar indiscriminadamente após salvar novas edições. O histórico recuperável reside em `.local/editorial/history/` e deve acompanhar o backup local.

## Conferência manual

1. Iniciar `python3 -m backend`, abrir o site e usar Ctrl+Shift+R. Se estava aberto antes das gravações, reiniciar o backend.
2. Abrir [EN013](http://127.0.0.1:8000/#/doc/confessionezhov-ezh-013), selecionar inglês e localizar a passagem “I was not capable of anything then…”. Comparar com RU/PT; o título/data não foi reescrito.
3. Abrir [2685](http://127.0.0.1:8000/#/doc/showtrials-2685) e [3112](http://127.0.0.1:8000/#/doc/showtrials-3112). No fim, conferir a nota editorial nos três idiomas, separada das notas originais. 3112 continua em revisão.
4. Abrir [1790](http://127.0.0.1:8000/#/doc/showtrials-1790) e [2484](http://127.0.0.1:8000/#/doc/showtrials-2484). O índice deve alcançar os títulos repetidos em posições distintas. Em [4828](http://127.0.0.1:8000/#/doc/showtrials-4828), conferir os quatro anos depois da tabela.
5. Abrir [3246](http://127.0.0.1:8000/#/doc/showtrials-3246): conferir os sete itens em leitura e estudo paralelo RU/PT/EN. Em [6431](http://127.0.0.1:8000/#/doc/showtrials-6431), a numeração recuperada começa em 366.
6. Na área editorial, filtrar “Corrigido” para os motivos tratados e “Em revisão” para as seis peças de Ezhov e seis ressalvas de Leningrado. Um documento pode continuar com outro motivo pendente, especialmente links. Consultar o histórico antes de restaurar; gravações posteriores podem impedir restauração sem conflito.

Não foram executadas suítes de testes ou testes no navegador. Houve processamento documental, cotejo, conferência de hashes e validação transacional do gravador. O próximo trabalho permanece nos títulos/seções ainda não tratados e na recuperação de links/notas, mantendo OCR e cotejo de variantes como entregas separadas.
