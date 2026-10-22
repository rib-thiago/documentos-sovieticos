# Diagnóstico ShowTrials — 21 de outubro de 2026

> Diagnóstico anterior à gravação da reconciliação. Para o estado após a atualização da fila, consulte [o plano consolidado](PLANO-DE-EXECUCAO.md) e [o comprovante](RECONCILIACAO-GRAVACAO.json).

Leitura da fila, Markdown canônico, receitas e HTML WordPress preservado. Nenhum texto, catálogo ou status foi alterado por este diagnóstico. Não foram executados testes nem acessadas fontes na rede. As contagens descrevem apontamentos, não erros comprovados.

## Base e resultado

São **2.345 apontamentos ShowTrials: 2.344 pendentes e um corrigido**. Os pendentes se distribuem em 2.042 links, 236 textos longos, 37 tabelas, dez listas, oito imagens, seis decisões editoriais e cinco títulos ambíguos.

O pacote `temporario/showtrials-metodologia-20261015-141712/original/local/posts-json/` contém os 2.179 posts de referência. O campo `content.rendered` correspondente a **cada apontamento** coincide com o SHA-256 de HTML registrado em `data/markdown-conversions.json`: nenhuma divergência nesse universo. Isso verifica identidade da fonte, não correção histórica nem igualdade com o Markdown revisado.

[proposals-showtrials.json](proposals-showtrials.json) contém uma proposta por chave, hash atual do Markdown, caminho/identidade do HTML, contagens e limites. Esses hashes devem ser reavaliados antes da gravação; revisão humana posterior prevalece.

## Reconciliação comprovável

- `showtrials-1699:tabelas_linearizadas` já está **corrigido** e registra confirmação do responsável: preservar esse status. O canônico tem 148 linhas iniciadas por `|`, inclusive separadores e múltiplas tabelas; isso não significa 148 linhas documentais.
- `showtrials-1699:texto_longo_sem_secoes_suficientes` segue pendente, embora o canônico tenha **dez títulos**. A condição antiga de ausência de seções está obsoleta; propor encerrá-la com registro da evidência, sem alegar uma nova validação de conteúdo integral. SHA atual: `df58d2a5dd7f63352196b7c618df958a427c016c2f63931f3417931ec8b3092f`.
- Nos demais 235 alertas de texto longo, o detector atual encontrou no máximo um título. Isso confirma a condição mecânica, não que novos títulos devam ser inventados. Uma fonte contínua pode estar correta e não precisar de seções.
- **64 dos 2.042 alertas de links só contêm destinos `#fragmento`**. Não são anexos externos não coletados; são candidatos a reconstrução de chamadas/retornos. Não encerrar automaticamente: o vínculo pode efetivamente faltar no Markdown.
- Apenas **seis** alertas de links incluem extensão explícita PDF/DOC/imagem/DjVu. A heurística não detecta anexos servidos sem extensão; não usar esse número como inventário exaustivo.

## Amostras que orientam os lotes

| Caso | Evidência local | Tratamento |
| --- | --- | --- |
| 1699 | 783 células HTML, nove células mescladas; tabela corrigida pelo responsável | Preservar correção e reconciliar o alerta de seções |
| 2644 | 24 linhas/96 células HTML, sem mesclas; nenhuma linha de tabela Markdown | Candidato a reconstrução determinística, cotejando cabeçalhos/notas; manter 14 títulos já existentes |
| 4504 | 13 linhas/39 células HTML, sem mesclas; nenhuma linha de tabela Markdown | Piloto menor de tabela, sem alterar números/nomes |
| 1790 | Sessão extensa; zero títulos; 175 links, 68 fragmentos | Notas e divisões exigem cotejo; não criar título por fala ou janela de caracteres |
| 1633 | Alerta de links com destinos exclusivamente internos | Piloto de correspondência chamada/nota/retorno |
| 10722 | Duas imagens PNG no HTML, sem alt | Adquirir/abrir imagens antes de dizer se falta transcrição |
| 1442 | Três imagens JPG e links para elas | Verificar se fac-símile, texto repetido ou conteúdo adicional; preservar proveniência |
| 1733 | Três imagens JPG; uma declarada 16×16 com estilo de largura100% | Dimensão HTML não basta para classificar como ícone ou descartar conteúdo |

As imagens foram inventariadas pelo HTML; **não houve cotejo visual** nesta tarefa. Não é seguro resolver os oito alertas pela extensão, dimensão ou nome do arquivo.

## Plano de trabalho com agentes

**Etapa A — prévia e reconciliação central.** Um integrador captura hash da fila, estados atuais, hashes dos documentos e histórico editorial. Aplica apenas decisões comprovadas, preservando status/notas humanas. Não regenerar a fila com o conversor antigo, porque isso mistura novos relatórios e decisões históricas. Separar problema confirmado, suspeita, conferência preventiva e resolvido.

**Etapa B — três agentes, uma unidade de escrita por documento.**

1. **Tabelas, listas e imagens:** começar pelo piloto4504 e tabela2644; depois tabelas simples em lotes de até dez, complexas em lotes de até cinco, dez listas e oito imagens. Células mescladas e fac-símiles entram em cotejo visual. Retornar candidatos, diff, contagens de células, hashes e ressalvas. Não fechar alerta pela mera existência de `|`.
2. **Links e notas:** primeiro seis documentos com anexos e64 documentos só com fragmentos; depois demais links por lotes de até100 documentos. Reconstrução automática somente com localização unívoca de rótulo e parágrafo e alvo resolvido; referências repetidas entram em revisão. Preservar definições e retornos; não converter números entre colchetes globalmente em notas.
3. **Seções e decisões:** 236 alertas longos (menos1699 após reconciliação), cinco títulos e seis decisões, em lotes de até20. Conferir títulos explícitos no HTML e seleções manuais. Sem título explícito, justificar manutenção da fonte contínua; títulos descritivos novos requerem política editorial/aprovação.

Os conjuntos se sobrepõem. O integrador gera previamente um mapa documento→agente: se um documento tiver tabela/imagem e links/títulos, o agente de estrutura controla a edição e recebe propostas dos outros **sem gravação concorrente**. Outra opção segura é executar ondas sequenciais tabela→links→títulos, recalculando hashes a cada onda.

**Etapa C — integração central verificável.** Cada lote deve entregar estado anterior/hash, fonte/hash, candidato, diff, decisões por chave, problemas remanescentes e inventário de alterações de blocos. O integrador confere que o canônico não mudou desde a preparação, grava com histórico recuperável e atualiza catálogo/manifesto/busca. Não alterar traduções para fabricar alinhamento: mudanças no número de blocos precisam de diagnóstico em cada idioma. Só encerrar uma pendência após comprovar a condição resolvida; fila original e diagnóstico permanecem recuperáveis.

## Código aproveitável e limites

- `scripts/prepare_markdown.py`: parser HTML, normalização, preservação de blocos, receitas, hashes e seleções revisadas. Reutilizar funções; não reaplicar o conversor completo sobre revisões humanas.
- `scripts/convert_showtrials_all.py`: coleta tags/imagens/links e gera os códigos de alerta; o diagnóstico nasce de presença de estrutura no HTML, não de comparação semântica atual. `--accept-headings` aceita apenas marcadores de títulos e não serve para tabelas, links ou notas.
- `data/markdown-review.json` e `data/markdown-conversions.json`: decisões manuais e evidências de origem, que têm precedência sobre heurística nova.
- `scripts/catalog_guard.py` e o mecanismo transacional editorial: usar bloqueio, prévia, histórico e publicação local do catálogo. Não empregar a escrita legada de manifesto em lote para essas correções.
- `scripts/check_showtrials.py`: utilitário histórico de integridade; executar somente quando autorizado/necessário, sem confundir igualdade com TXT com recuperação da estrutura perdida.

Não há neste diagnóstico evidência de que todas as pendências possam ser resolvidas sem intervenção humana. A equipe consegue preparar e cotejar a maior parte; ausência de fonte legível, ambiguidade de estrutura e novos títulos interpretativos devem permanecer explicitamente retidos.
