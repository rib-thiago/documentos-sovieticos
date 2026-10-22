# Sakharov — adaptação e piloto real

Atualização: a coleta ampliada e a resolução da nota 1066 estão em [sakharov-etapa2.md](sakharov-etapa2.md). Este documento registra o piloto inicial.

Data: 20/10/2026. Esta etapa prepara candidatos em área de trabalho; nada foi incorporado ao catálogo público. Não houve commit ou push.

## O que foi entregue

Código durável: `scripts/coletores/sakharov/collect.py`, `extraction.py`, dependências opcionais, instruções e três verificações offline de preservação. O parser foi adaptado do pacote do pesquisador; o controlador antigo que regravava Markdown e inventário foi substituído.

Área de trabalho: `temporario/coletas-quatro/sakharov/`. Começar por `PILOTO.md`; `inventory.json` contém URLs, hashes, títulos, fontes brutas, candidatos, diagnósticos e tentativas. Os arquivos brutos são versionados por SHA-256; os candidatos também. Repetições usam cache; falhas não apagam resultados anteriores e alterações manuais não são sobrescritas. Uma atualização de fonte preserva a versão anterior. Um diretório de saída deve ter somente um processo escritor.

Dependências foram instaladas somente no ambiente temporário `/tmp/sakharov-collector-venv`. Houve uma tentativa inicial impedida pelo DNS do sandbox; o piloto foi então executado com acesso de rede autorizado, respeitando robots.txt. Essas primeiras falhas permanecem no histórico de tentativas, não indicam falha do resultado final.

## Resultados efetivamente obtidos

Cinco URLs HTML preservadas: três páginas russas, o índice inglês e um extrato inglês. Os três corpos russos são diferentes; o índice inglês revelou os 18 links previstos. Quantidades abaixo são caracteres de Markdown, não páginas impressas.

| Navegação/fonte | Conteúdo observado | Caracteres | Pontos de revisão |
|---|---|---:|---|
| RU `start=0` | Folha de rosto, expediente, agradecimentos e prefácio do editor científico | 20.783 | A página é composta; não transformar automaticamente em um documento histórico |
| RU `start=29` | § 2, mito do pedido de ajuda de Lenin a Trotsky | 20.195 | Chamadas 1043–1066; lista de notas termina em 1065 |
| RU `start=59` | APÊNDICES, reunindo vários documentos | 71.487 | Individualização interna necessária; uma tabela preservada |
| EN, *Two Concepts of NEP* | Extrato traduzido, com créditos editoriais e notas 224–276 | 49.789 | Não foi estabelecida correspondência com uma página russa |

Fontes consultadas:
- [Início russo](https://leninism.su/books/4135-politicheskoe-zaveshhanie-lenina-realnost-istorii-i-mify-politiki.html?start=0).
- [Seção intermediária russa](https://leninism.su/books/4135-politicheskoe-zaveshhanie-lenina-realnost-istorii-i-mify-politiki.html?start=29).
- [Apêndices russos](https://leninism.su/books/4135-politicheskoe-zaveshhanie-lenina-realnost-istorii-i-mify-politiki.html?start=59).
- [Índice inglês](https://neodemocracy.blogspot.com/2022/11/the-reality-of-history-and-myths-of.html).
- [Extrato inglês](https://neodemocracy.blogspot.com/2022/07/two-concepts-of-nep-new-economic-policy.html).

A tabela dos apêndices mantém as colunas `СЛУШАЛИ` e `ПОСТАНОВИЛИ` em Markdown. Os links de imagens e remissões foram tornados absolutos; a imagem da capa inglesa permanece remota e não foi baixada. O contador `Страница N из 60` foi retirado do corpo por ser navegação; a posição permanece no inventário. Os textos de notas foram preservados, sem inventar remissões nem completar referências.

## Pendências importantes

1. **Alta — nota 1066:** há chamada no corpo da página intermediária sem definição ao final dessa página. O defeito aparece na fonte coletada. Investigar página adjacente/PDF antes de corrigir; não foi alterado silenciosamente.
2. **Alta — apêndices:** a última página contém vários documentos distintos. Há base para individualização futura, mas suas fronteiras não foram aprovadas neste piloto.
3. **Média — correspondência bilíngue:** os extratos ingleses formam uma seleção. É preciso localizar sua seção russa antes de criar edições paralelas.
4. **Média — aparato editorial:** a versão russa termina com agradecimento dos responsáveis pelo site-fonte, preservado no candidato para revisão; o extrato inglês preserva capa/créditos. Separar aparato da fonte e conteúdo da obra explicitamente antes da incorporação.
5. **Diagnóstico automático não equivale a erro:** o marcador `[19]` nos apêndices ocorre em `с начала [19]22 г.` — recomposição do ano 1922, não uma nota faltante. Foi mantido como na fonte. O verificador de rótulos é apenas indício para revisão humana.
6. As 60 posições não foram integralmente coletadas, as fronteiras não foram todas conferidas, e o PDF não foi baixado. Não há tradução nova gerada, alinhamento automático ou garantia de equivalência com paginação impressa.

## Verificações e como reproduzir

Passaram três verificações offline: candidato com correção manual não é regravado; falha posterior não remove o sucesso; nova fonte preserva arquivo e metadados anteriores. O piloto foi repetido a partir do cache e os resultados cumulativos permaneceram disponíveis.

```bash
/tmp/sakharov-collector-venv/bin/python -m unittest discover -s scripts/coletores/sakharov -p test_collect.py
/tmp/sakharov-collector-venv/bin/python scripts/coletores/sakharov/collect.py
```

Para conferir manualmente, abrir `temporario/coletas-quatro/sakharov/PILOTO.md`, comparar começo e fim de cada candidato com o HTML vinculado e revisar notas/tabela. O piloto ainda não tem URL própria no site, porque não modifica o catálogo. As instruções para criar novamente o ambiente opcional estão em `scripts/coletores/sakharov/README.md`.
