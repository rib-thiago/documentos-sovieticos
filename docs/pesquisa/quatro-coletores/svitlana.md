# Svitlana/Erdogan — adaptação e piloto

Data: 20/10/2026. Sem incorporação pública, alteração de textos existentes,
commit ou push. Fontes e candidatos em `temporario/coletas-quatro/svitlana/`.
Adaptador autônomo em `scripts/coletores/svitlana/`; sementes necessárias copiadas
para essa pasta, sem dependência de `temporario/proposta-coletores` em execução.

## Resultado real

- Dois índices obtidos: VOL-01 (11 URLs candidatas) e TEMA-TO-STALIN (50).
- 63 URLs candidatas únicas no inventário cumulativo, considerando amostras
explícitas de outras séries; não equivalem a 63 documentos históricos.
- Sete páginas inglesas obtidas e convertidas; nove snapshots HTML ao todo,
contando os dois índices. Todas permanecem `collected_unreviewed`.
- Nenhum original russo novo obtido nesta frente; o inglês é tradução candidata,
não foi apresentado como original. Créditos individuais ainda precisam de conferência.
- Dois índices são uma amostra dos 35 inventariados no pacote. Não foi feita coleta
integral das 35 séries.

O acesso inicial sem rede autorizada falhou por DNS; a primeira sondagem remota
recebeu HTTP 412. O piloto posterior, com acesso de rede autorizado, obteve os
dois índices e as sete páginas sem contornar CAPTCHA ou restrições de robots.

## Conferência por página

|Candidato|Conteúdo e tamanho final|Pendência|
|---|---|---|
|`svitlana-aa02ccdf0bad5a13`|Tiflis, 1903; 10.450 caracteres|Índice Volume I, título HTML Volume XIV/1934 e cabeçalho Volume XII/1932. Preservados na fonte; não usar como metadados históricos.|
|`svitlana-cf7c0161d6bb507f`|Notas Stalin/execuções maio de 1922; 4.008 caracteres|Ao menos dois documentos, números 24-7 e 24-1, na mesma página; segmentação editorial necessária.|
|`svitlana-8e787b136fb8a966`|Circular religiosa; 9.296 caracteres|URL diz 1922, mas corpo/título identificam 16 de agosto de 1923; registrar divergência.|
|`svitlana-c07a09902a9439f2`|Politburo, 26 de outubro de 1925; 185.105 caracteres|Sessão longa com notas até 34; conferir fronteiras/itens e notas contra fonte.|
|`svitlana-a7dae83755fbcdd4`|Carta Stalin/artigo Bukharin; 10.756 caracteres|Notas 66–71 e crédito editorial preservados. Crédito coletivo não prova tradutor individual.|
|`svitlana-4898e43af1b5adac`|Ezhov/Uspensky, 15 de abril de 1938; 22.282 caracteres|Carta de encaminhamento e telegrama anexado; preservar ligação e notas [1] e [2].|
|`svitlana-c5ed6f188cc197d3`|Acordo preliminar Rússia/Ucrânia/Polônia, 1920; 26.286 caracteres|Página reúne acordo e ratificação; decidir unidade de descrição sem separar silenciosamente.|

As notas finais e referências arquivísticas estavam presentes nas amostras
inspecionadas. Isso não equivale a uma colação completa com a edição impressa.
Algumas páginas usam blockquote como layout e mantêm essa estrutura no Markdown;
a simplificação deve ser feita com revisão, sem apagar citações legítimas.

## Contrato de segurança implementado

- Inventário cumulativo por URL, ocorrências independentes em várias séries e
tentativas datadas; erro de atualização conserva o último sucesso.
- Snapshots HTML e Markdown por hash, imutáveis; reconversão offline disponível.
- URLs relativas de links/imagens resolvidas; âncoras e texto de notas preservados;
Markdown estrutural em vez de TXT; tabelas simples convertidas e complexas sinalizadas.
- Robots.txt, intervalo mínimo por host, limitação explícita de tamanho sem
truncamento silencioso, tipos de resposta e redirecionamentos conferidos.
- Corpo WordSection selecionado quando presente; navegação e rodapé do site
separados. Título HTML permanece metadado de origem, não título histórico automático.
- Nenhuma atribuição automática de autoria/tradução aos organizadores da série.

## Sobreposição conhecida e integração futura

A correspondência russa `https://istmat.org/node/27376` já pertence ao documento
`tukhachevsky-nko37-01-pm` no catálogo existente. O vínculo consta em
`temporario/coletas-quatro/svitlana/review.json`. Não foi baixado/recriado nem
associado a uma tradução inglesa por presunção.

Antes da incorporação, revisar as páginas compostas, identificar autor/título/data
do corpo e tradutor quando creditado, comparar URLs/cotas e texto com o acervo,
então emitir candidatos de documento/edição/participação. Até isso ocorrer, os
Markdowns continuam na área de trabalho, sem novas URLs públicas.

## Reproduzir e conferir

```sh
python3 scripts/coletores/svitlana/collect.py --indexes --sources VOL-01,TEMA-TO-STALIN
python3 scripts/coletores/svitlana/collect.py --sample-documents --limit 4
python3 scripts/coletores/svitlana/collect.py --documents --sources VOL-01 --limit 3
python3 scripts/coletores/svitlana/collect.py --reconvert
python3 -m unittest discover -s scripts/coletores/svitlana -p 'test_*.py' -v
```

Os quatro testes offline passaram: preservação do último sucesso após falha,
ocorrências compartilhadas entre séries, imutabilidade de snapshots, estrutura
Markdown/links/âncoras/tabelas e seleção do contêiner Word sem masthead/rodapé.
Houve também o piloto remoto descrito acima, sem escrita no catálogo.

Para inspeção manual, abrir `inventory.json`, localizar um candidato pelo ID,
abrir os caminhos `latest_success.raw` e `latest_success.markdown` relativos à
pasta de coleta. Comparar começo, fim, números documentais e notas. O arquivo
`review.json` lista a prioridade e o motivo das pendências encontradas.
