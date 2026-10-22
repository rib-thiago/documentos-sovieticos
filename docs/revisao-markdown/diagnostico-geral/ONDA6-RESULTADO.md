# Onda 6 — protocolos anexos e reconciliação de alertas de índice

Escopo: 18 documentos ShowTrials relativos a comunicações com protocolos anexos. Foram confrontados o HTML preservado, a edição russa atual e as rubricas tipográficas inventariadas. O cotejo exige correspondência integral e ordenada do texto projetado; a seleção de títulos é explícita, não uma classificação automática de frases ou nomes.

Foram encerrados **18 apontamentos**: a fila passa de **716 para 698 abertos**. Histórico recuperável: `20261022103819534645-d2d4dc99f1c4`.

## Resultado documental

- **16 alertas obsoletos:** 7625, 7627, 7630, 7644, 7707, 7713, 7724, 7726, 7756, 7787, 7792, 7840, 7878, 7913, 7952 e 8003. A rubrica do protocolo já estava marcada no Markdown. Não foi inventada subdivisão temática para fazer o texto atingir uma contagem arbitrária de seções. Esses arquivos não foram reescritos.
- **Dois títulos recuperados:** 7789 e 7915. Acrescentado apenas o prefixo Markdown à rubrica existente, com inversão exata dos prefixos recuperando os bytes anteriores. Nenhuma palavra, nota, data, parágrafo ou tradução foi alterada.
- Em 7915 foi mantida a grafia literal **ПРОТОКОЛ ВОПРОСА**; não foi emendada para a forma mais habitual. Em 7707 permanece a data literal de 1936 que consta na rubrica, sem harmonização por plausibilidade.

A revisão fecha somente o indicador de seções nesses documentos. Não equivale a revisão histórica integral, aprovação das traduções ou pareamento dos idiomas.

## Evidências e recuperação

Preparador: `scripts/revisao_acervo/prepare_wave6_protocols.py`.
Base e candidatos: `temporario/revisao-onda6/`; evidências incluem hash do HTML, hash da edição, intervalo de correspondência integral, seleção literal, títulos preexistentes e prova de inversão dos prefixos.

A integração usa o mecanismo existente com comparação da base, verificação das âncoras PDF, histórico antes/depois e atualização do catálogo, manifesto e busca. O recibo `onda6-protocolos-20261022-gravacao.json` registra a conclusão da gravação; sem ele, os candidatos permanecem apenas preparados.

## Conferência manual

- Abrir `http://127.0.0.1:8000/#/doc/showtrials-7789` e consultar o índice: deve incluir a rubrica do protocolo.
- Abrir `http://127.0.0.1:8000/#/doc/showtrials-7915`: conferir a rubrica literal sem correção ortográfica presumida e a identificação logo abaixo.
- Abrir `http://127.0.0.1:8000/#/doc/showtrials-7625`: a entrada do protocolo já existente deve continuar disponível.

A avaliação visual fica com o responsável. Não foram executados testes automatizados, de aplicação ou de navegador. Sem commit ou push. As alterações recentes da interface foram preservadas.
