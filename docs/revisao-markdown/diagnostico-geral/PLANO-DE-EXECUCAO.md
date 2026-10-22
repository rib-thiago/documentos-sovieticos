# Plano de revisão do acervo e preparação das fontes

> Execução em andamento: [onda 1](ONDA1-RESULTADO.md), [onda 2](ONDA2-RESULTADO.md) e [onda 3 — links e notas](ONDA3-RESULTADO.md). O saldo após a onda 3 é de 780 apontamentos abertos, incluindo 38 alertas de links. A base e a divisão abaixo são o planejamento original; consulte o diagnóstico e o progresso para o saldo atual. O OCR do julgamento foi adiado para priorizar intervenções delimitadas com fontes locais disponíveis.

> Atualização da [onda 4](ONDA4-RESULTADO.md): saldo de **732 apontamentos abertos**, nenhum alerta restante de reconstrução de links. Foram recuperados mais 88 títulos e encerradas quatro conferências de notas. Defeitos do HTML e vínculos externos ambíguos permanecem explicitados como ressalvas, sem emendas conjecturais. Próxima frente: 227 indicadores de seções, cinco decisões de hierarquia e revisão geral do catálogo.

> Atualização da [onda 5](ONDA5-RESULTADO.md): saldo atual de **716 apontamentos abertos**. Mais 45 títulos recuperados; as cinco decisões de hierarquia foram tratadas e onze cadastros tiveram a representação das datas normalizada, mantendo aberta a revisão geral. Restam 216 indicadores de seções, 486 conferências gerais de catálogo/cadastros, doze divergências e dois trabalhos de imagem/OCR.

Data-base do planejamento original: 21/10/2026. Àquela altura, havia somente diagnóstico e reconciliação da fila. A execução posterior está documentada nos resultados acima, com históricos recuperáveis. Não houve commit nem push dessas ondas.

## 1. Diagnóstico atual e alcance

A fila principal contém **2.907 registros**, dos quais **2.905 abertos em 2.603 documentos** e dois corrigidos. Prioridades dos apontamentos abertos: 50 urgentes, 267 altas, 552 médias e 2.036 baixas. São apontamentos, não contagem de erros comprovados ou documentos distintos.

| Natureza do trabalho | Apontamentos abertos | Diagnóstico |
|---|---:|---|
| Links | 2.042 | Alerta herdado da conversão, exige comparar destinos com versão atual; 64 só têm fragmentos internos e seis incluem anexos explícitos |
| Textos longos | 235 | Indicador de navegabilidade; fonte contínua não autoriza inventar seções |
| Tabelas | 37 | Possível perda de relações entre células; precisa cotejo, distinguindo conteúdo e layout |
| Imagens | 8 | Conteúdo ainda não inspecionado neste diagnóstico; não presumir ausência documental nem ornamento |
| Listas | 10 | Estrutura a confirmar na fonte |
| Títulos ambíguos / decisões de hierarquia | 11 | Resolver com evidência ou manter dúvida explicitamente |
| Compilação Ezhov individualizada | 24 | Fronteiras e divergências RU/PT/EN, especialmente datas |
| Ressalvas de traduções Leningrado | 17 | Agora na fila; revalidar no estado atual antes de corrigir |
| Fontes militares | 31 | Conferências de tabelas/notas, mais ficha de julgamento digitalizado sem transcrição |
| Novas coleções e cadastros locais | 486 | Revisão preventiva; não são 486 erros detectados |
| Notas Mozokhin já corrigidas | 4 | Conferência posterior, distinta de defeito de notas ainda aberto |

Os 2.345 apontamentos ShowTrials do diagnóstico inicial foram confrontados com o pacote HTML preservado: as fontes correspondem aos hashes das receitas. A reconciliação encerrou depois um desses alertas. Nenhum arquivo indicado pela fila está ausente ou com hash divergente do catálogo na conferência dos caminhos referenciados. Isso não audita todas as traduções do catálogo nem prova fidelidade integral aos HTMLs.

**Não houve leitura crítica integral de todos os textos.** O diagnóstico combina inventário completo, verificações de integridade e cotejos pontuais. As classes da planilha são encaminhamentos fundamentados, não uma certificação automática de defeito ou correção.

## 2. Reconciliação já aplicada

Histórico recuperável: `20261021203637587521-fce0573aeca7`. [Comprovante e antes/depois](RECONCILIACAO-GRAVACAO.json).

- Encerrado somente `showtrials-1699:texto_longo_sem_secoes_suficientes`: dez títulos já existem; a correção da tabela pelo responsável foi preservada. Não se declarou nova validação histórica da tabela.
- Quatro registros Mozokhin receberam descrição/ação/notas que reconhecem a correção comprovada pelos hashes. Continuam pendentes como conferência preventiva, sem alteração de prioridade.
- As 17 ressalvas documentadas das traduções Leningrado ganharam motivos próprios. Não substituem os alertas de links dos mesmos documentos, não são duplicação semântica e não foram declaradas erros atuais confirmados.

Nenhum texto, tradução, catálogo, manifesto ou índice de busca foi alterado nesta reconciliação. O aumento de 2.889 para 2.905 apontamentos abertos decorre de 17 registros antes dispersos e um encerramento; não foram encontrados 16 novos documentos defeituosos.

A interface editorial mantém os quatro estados existentes. Classes diagnósticas estão no CSV/JSON desta entrega; não foram adicionados filtros ou estados novos à interface. `pendente` pode significar conferência preventiva ou problema a cotejar, conforme a descrição.

## 3. Divisão operacional e autoridade de escrita

**Três agentes preparadores e um integrador principal.** Os preparadores não escrevem em `originais/`, `data/`, fila principal ou banco editorial. Cada documento pertence a um único lote, incluindo todos os motivos abertos; sugestões de outras especialidades vão ao proprietário do documento. Trabalho em idiomas diferentes também deve respeitar essa propriedade para não conflitar na integração.

O integrador é o único responsável pela gravação canônica, com prévia, histórico e atualização dos índices necessários. Mantém as sessões do backend protegidas pelo bloqueio já existente. Se houver edição humana ou hash diferente, o lote volta à conciliação; nunca substitui a edição silenciosamente.

O [manifesto de lotes](LOTES.json) cobre as **2.905 chaves abertas e 2.603 documentos, sem propriedade duplicada**. São **303 lotes técnicos**, que devem ser consumidos sucessivamente pelos agentes, não 303 pedidos de aprovação ao usuário. Os limites variam por risco e tamanho de todas as edições: até três documentos estruturais grandes, 12 de divergências e 30 de links/prevenção, com orçamento conservador de volume. Os 39 lotes que excedem o orçamento por conter documento grande exigem subetapas internas e revisão das fronteiras; continuam com um proprietário único.

Os IDs e snapshots do manifesto identificam esta linha de base. Antes de cada despacho, comparar a fila e os hashes: se a base mudou, replanejar somente o trabalho ainda não iniciado. [PROGRESSO.json](PROGRESSO.json) é o registro durável de resultados e não é apagado pela regeneração do diagnóstico. Não editar o status apenas no manifesto gerado e depois regenerá-lo, pois ele é uma projeção de planejamento.

## 4. Ondas de execução

| Onda | Preparador A | Preparador B | Preparador C | Condição de avanço |
|---|---|---|---|---|
| 0 — concluída | Diagnóstico ShowTrials | Reconciliação de correções | Filas complementares | Base reconciliada, fontes e tarefas identificadas |
| 1 — risco documental | Tabelas ShowTrials, começando pelo lote de 4504 | Tabelas complexas e imagens, começando por 2644 | Militares: 13 tabelas em três documentos; depois notas/fronteiras | Pilotos cotejados; mecanismo de gravação preserva texto e notas |
| 2 — estrutura e divergências | Textos longos e títulos explícitos | Ezhov: datas, fronteiras e notas entre idiomas | Leningrado: 17 ressalvas de fonte/tradução | Alterações sustentadas por passagem; limites de fonte separados de falhas de extração |
| 3 — vínculos e notas | Links/notas com alvo unívoco | Fragmentos internos e retornos | Anexos e casos repetidos/ambíguos | Alvos, rótulos, notas e destinos conferidos, sem substituição global de números |
| 4 — conferência preventiva | Sakharov e Mozokhin | Svitlana/Brest já incorporados | Cadastros locais e sobras dos outros lotes | Fechar somente o escopo realmente conferido |

A associação acima é uma especialização, não autorização para sobrepor documentos. O manifesto mantém todos os motivos de um documento no lote de maior risco. Por exemplo, documentos de onda 1 com links já levam esses motivos: o preparador pode resolvê-los ou registrar a parte remanescente para uma segunda passagem sequencial, após o novo hash, nunca para agente concorrente.

**Primeiro despacho concreto:** `R1-tabelas_imagens-0025` (4504,4576,4578), `R1-tabelas_imagens-0024` (2644) e `R1-fontes_militares-0001` (três textos com tabelas). O integrador compara os dois pilotos ShowTrials antes de ampliar qualquer reconstrução automática. Os lotes restantes são redistribuídos entre os mesmos três slots conforme terminam, preservando prioridade e propriedade.

Não é preciso interromper a execução a cada lote para aprovação. Prosseguir nos trabalhos autorizados, relatando entregas verificáveis. Solicitar intervenção somente em decisão editorial substantiva ou impedimento que a evidência disponível não permita resolver. Commit/push continuam separados da execução local.

## 5. Trabalho fora da fila de publicados

Não somar estes inventários ao total de 2.905. [Detalhamento e localizadores](FILAS-COMPLEMENTARES.md); [inventário estruturado](FILAS-COMPLEMENTARES.json).

| Trilha | Escopo | Divisão e dependências |
|---|---|---|
| OCR do julgamento 1937 | PDF russo com 172 páginas | Primeiro verificar se já há trabalho do usuário na ferramenta. Um agente coordena o documento; subagentes podem trabalhar por intervalos de páginas com hashes, limites contíguos e notas. Revisar páginas antes de substituir/complementar a ficha. PDF inglês 143 páginas é outro testemunho, não tradução alinhada automática |
| Svitlana não incorporada | 725 candidatas retidas e 24 páginas de referência | Agrupar por série, começando pelas 118 reconversões e páginas compostas; revalidar decisões anteriores por hash. Preparar fronteiras, notas e metadados; aquisição de PDF é etapa própria. As744 páginas sem decisão e esses totais se sobrepõem |
| Brest | 3 retidos, 2 peças alemãs e 17 referências | Cotejar variantes e atas; depois seguir referências prioritárias. Não confundir índice, excerto, historiografia e fonte primária integral |
| Sakharov estrutural | 14 registros | Não importar: 13 divisores e uma compilação já individualizada. Fechamento do escopo inventariado documentado |
| Perpetrator auxiliar |95 arquivos,19 com 876 notas vazias | Usar originais Word como testemunho de cotejo quando útil. Não importar coleção, não presumir identidade por similaridade e não inventar notas. Nova incorporação exige decisão específica |

OCR local é tecnicamente viável neste ambiente: foram encontrados Poppler, Tesseract, `pypdf` e dados de idioma russo, inglês e português. Não foi executado OCR ou teste nesta entrega. O pipeline existente em `backend/pdf_*` deve ser reaproveitado; não criar segundo fluxo que ignore revisões e projetos do usuário.

A execução das trilhas externas deve disputar os mesmos três slots, sem abrir agentes ilimitados. Prioridade inicial é corrigir riscos dos documentos já acessíveis; quando um lote depender de rede/fonte ausente, outro agente pode continuar uma trilha independente. A transcrição do julgamento é uma entrega própria, não uma correção de poucas linhas.

## 6. Entrega obrigatória de cada lote

1. Identificador do lote, documentos/idiomas, chaves da fila e hash inicial de cada edição.
2. Fontes locais ou adquiridas, URL/captura, hash e indicação de página/célula/passagem.
3. Candidatos preservados fora do acervo, receita reproduzível e diff. Manter o bruto e a versão anterior.
4. Resultado por chave: `corrigido_com_evidencia`, `alerta_obsoleto_ou_falso_positivo`, `fonte_continua_legitima`, `ressalva_da_fonte_preservada`, `parcial`, `bloqueado_fonte` ou `decisao_editorial_necessaria`.
5. Explicação e passagem que sustenta cada resultado. Contagem de títulos, presença de `|` ou coincidência de hash isoladamente não provam fidelidade.
6. Diagnóstico de blocos/parágrafos por idioma quando a estrutura mudar. Não fabricar pareamento; avaliar impacto nos marcadores de leitura e nas correções de trecho já existentes antes da gravação. Se não houver migração segura, manter candidato fora do canônico e registrar dependência.
7. Integrador verifica base atual, escopo do diff e critérios abaixo; depois grava pelo histórico, atualiza catálogo/manifesto/busca quando o conteúdo mudar e só então reconcilia a chave específica.

Os resultados detalhados pertencem ao registro de progresso. Nos quatro estados atuais da interface: corrigido/falso positivo comprovado podem encerrar a chave com explicação; parcial permanece pendente ou em revisão; bloqueado fica pendente com motivo ou adiado com justificativa, sem fingir conclusão. Ressalva literal da fonte só encerra o defeito de extração quando a preservação e a explicação forem adequadas; a dúvida histórica permanece documentada.

## 7. Critérios de resolução e limites da autonomia

**Podemos resolver autonomamente:** recuperar links quando a correspondência for única; reconstruir tabelas/listas cotejadas; restaurar notas presentes na fonte; corrigir OCR legível na imagem; recuperar títulos explícitos; corrigir tradução demonstravelmente equivocada; completar metadados expressos; individualizar documentos com fronteiras verificáveis; concluir falsos positivos demonstrados.

**Podemos preparar, mas talvez reste dependência:** OCR com imagem insuficiente, notas ausentes na fonte adquirida, fontes inacessíveis, identificação de pessoas por contexto, datas contraditórias entre testemunhos e títulos interpretativos novos. Tentar fontes alternativas legítimas e cotejo antes de devolver a questão ao usuário. Não converter alegações históricas em fatos do catálogo nem corrigir fonte por plausibilidade.

Para links: preservar rótulo, destino e localização, distinguir citação/nota/retorno/navegação. Para tabelas: conferir todos os valores e relações, mesclas, vazios, unidades e totais; não recalcular silenciosamente. Para traduções: preservar RU e registrar antes/depois na edição correspondente. Para seções: conteúdo literal não pode desaparecer, e índices devem refletir fronteiras justificadas.

O objetivo é resolver tudo o que as fontes permitirem, **não zerar artificialmente a fila**. Não é possível prometer quantas chaves serão encerradas antes do cotejo. Arquivos brutos faltantes e ambiguidades reais devem resultar em bloqueios específicos e reutilizáveis, não em filas genéricas sem próxima ação.

## 8. Controle de evolução e retomada

Por entrega, registrar em `PROGRESSO.json`: manifesto/base usados, lote, documentos, responsável, estado, versões antes/depois, caminhos de receita/diff, chaves resolvidas/parciais/bloqueadas, histórico da gravação, observações e próxima ação. Medir por chaves e por documentos únicos separadamente; não usar número de agentes ou linhas baixadas como progresso editorial.

Estados operacionais: planejado → em preparação → pronto para integração → integrado; alternativas: parcial, conflito de edição, bloqueado por fonte ou por decisão. Não confundir preparado com integrado. O integrador atualiza o diagnóstico após cada grupo de integrações, preservando o manifesto e os resultados anteriores; replaneja chaves remanescentes sem sobrescrever trabalho em curso.

Painel de cada entrega: saldo inicial/final de abertos, novas ressalvas encontradas, resolvidos por categoria, limitações preservadas, conflitos, fontes obtidas e próximos lotes. Não apresentar fechamento estrutural como revisão filológica integral.

Para retomar: **“Execute a onda 1 do plano de revisão, usando agentes, com integração local e histórico recuperável. Continue os lotes autorizados, registre o progresso e as dependências. Não faça commit nem push.”** Depois disso, basta pedir para continuar a próxima onda, sem reconstruir contexto ou reenviar todos os arquivos.

Ferramentas desta entrega:

```sh
python3 scripts/diagnose_review_queue.py
```

Esse comando atualiza apenas diagnóstico, lotes e snapshots; não altera fila/textos nem apaga `PROGRESSO.json`. `scripts/reconcile_review_queue.py` registra a reconciliação específica desta data; já foi aplicado e recusará reaplicação sobre a fila alterada. Não usar esse script como rotina genérica de fechamento.

Não foram executadas suítes de testes nem testes no navegador. Esta entrega fez leitura de fontes/registros, conferências de integridade e uma transação exclusivamente da fila. Correções futuras devem receber verificações proporcionais ao risco e instruções de validação manual; mudanças estruturais nos scripts exigem validação própria, sem repetir testes amplos a cada alteração editorial pequena.
