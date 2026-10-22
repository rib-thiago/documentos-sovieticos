# Onda 1 — lote A: 4504, 4576 e 4578

Preparação local, sem escrita canônica, alteração da fila, testes de navegador/suítes, commit ou push.

## Resultado preparado

| Documento | Idiomas candidatos | Estrutura HTML cotejada | Blocos antes → depois |
|---|---|---|---|
| showtrials-4504 | RU/PT/EN | Uma tabela, 13 linhas, três colunas: número, campo, resposta | 62 → 24 em cada idioma |
| showtrials-4576 | RU | Cinco tabelas, respectivamente 1/2/10/9/1 linhas, três colunas; 69 células | 133 → 46 |
| showtrials-4578 | RU | Duas tabelas, 5/2 linhas, três colunas; 21 células | 34 → 6 |

Não há mesclas. A última tabela de 4576 contém a célula inicial vazia diante de ХАРИТОНОВ; ela permanece vazia. As cinco divisões da fonte foram preservadas, sem concatenar tabelas separadas por categorias de acusação. As tabelas não são mera decoração: relacionam campos e respostas (4504) ou pessoas e informações (4576/4578). Cabeçalhos vazios evitam inventar títulos editoriais ou converter o primeiro registro em cabeçalho.

As 129 células russas foram comparadas integralmente, na ordem, com os blocos canônicos e o HTML preservado. O registro individual identifica texto da fonte, texto do candidato e blocos antigos de cada célula. A normalização de comparação ignora apenas espaços e escapes Markdown. Dentro de célula, os parágrafos antigos são unidos por espaço; não foi usado HTML `<br>` porque o interpretador público usa `html:false`. Nenhum número, data, grafia ou alegação foi corrigido por plausibilidade. Em 4504 PT/EN, os treze campos numerados estão explicitamente na mesma ordem e têm fronteiras inequívocas; os 39 blocos são reorganizados mantendo literalmente todas as palavras das traduções. Não foram transferidos links russos para palavras traduzidas.

Foram restaurados 20/68/14 vínculos RU, respectivamente, usando posição sequencial de cada âncora na fonte e localização normalizada no canônico. Não houve substituição global de nomes. Os destinos externos são os da fonte, sem confirmação da identidade biográfica indicada. Há discrepâncias evidentes preservadas: Loginov com rótulo Ivan Kharitonovich aponta para Petr Petrovich; Ermolaeva tem1903 no texto e1908 no destino; Paio tem Fedor no rótulo e Felix no destino. Não presumir que links biográficos provam identificação.

Em 4576, as quatro âncoras internas são chamadas/retornos das duas notas já presentes; os candidatos recuperam o destino absoluto da página original com seu fragmento. Isso preserva a navegação disponível na fonte, mas não cria notas locais nem afirma ter validado a disponibilidade remota. Não houve acesso à rede. Os números e textos das notas foram preservados.

## Impacto na interface e decisão de integração

`assets/app.js:parseStudyMarkdown` segmenta por linhas vazias e `zipBlocks` alinha idiomas por índice. As três versões de4504 agora possuem as mesmas24fronteiras, cotejadas por campos documentais, de modo que o diálogo posterior continua correspondente. As tabelas passam a ser um bloco cada; não existe identidade nova por linha/célula.

`resolveReadingBlock` tenta a assinatura no índice e depois procura a mesma assinatura no documento. Marcadores em prosa fora das tabelas podem ser encontrados pelo fallback, pois o texto se conserva, mas marcadores de uma célula antiga não encontrarão exatamente a nova tabela. Os arquivos `.evidence.json` fornecem mapas completos de índice antigo→novo para uma migração eventual; não escrever em `sessionStorage` de usuários indiscriminadamente. Citações antigas por § mudam e são explicitamente provisórias no próprio leitor.

`assets/study-editor.js` confere offsets e correspondência literal ao texto antes de gravar uma correção de trecho, protegendo contra a edição de um bloco obsoleto. O integrador ainda deve conferir vínculos persistentes de projeto/fac-símile/offset, se existirem para estes documentos, antes da gravação. Este preparador não alterou banco local nem alegou a ausência desses vínculos. Conservar as versões anteriores no histórico e registrar a mudança de numeração.

Cinco chaves têm candidato `corrigido_com_evidencia`, condicionado à integração. A chave de links de4576 permanece `parcial` até uma decisão sobre as duas notas locais: quatro fragmentos preservados apontam para a fonte externa, embora os64links externos estejam reconstruídos.

## Artefatos

- Resultado estruturado: `temporario/revisao-onda1/tabelas-a/result.json`.
- Cinco candidatos Markdown, versões anteriores e diffs; HTML das três fontes e evidência por célula/âncora/índice.
- Receita reproduzível: `scripts/revisao_acervo/prepare_tables_a.py`.

O script apenas prepara artefatos fora do acervo. A integração é responsabilidade exclusiva do agente principal e deve verificar hashes anteriores.
