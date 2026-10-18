# Traduções — Materiais da investigação do Centro de Leningrado

**Concluído localmente:** 280 novas versões (139 PT e 141 EN), completando português e inglês nos 152 documentos da subcoleção. Catálogo, manifesto e busca atualizados; histórico recuperável `20261018060728947322-873669cc3840`. As versões anteriores e os originais foram preservados.

## Escopo

A subcoleção contém **152 documentos**. No início desta entrega faltavam **280 versões**, distribuídas por **141 documentos**: 139 portuguesas e 141 inglesas. As versões portuguesas de 2683 e 2684 pertencem ao piloto anterior e foram preservadas; suas versões inglesas entram nesta entrega. As demais traduções já existentes também foram preservadas.

Traduções diretas dos originais russos por agentes autorizados pelo usuário, sem uso de serviços externos de tradução e sem substituições automáticas para gerar o corpo dos textos. Originais, URLs e ordem da coleção são mantidos. Esta entrega é local; não publica alterações automaticamente.

## Registros

- [Progresso e diagnóstico em CSV](progresso.csv): uma linha por versão solicitada, idioma, número de blocos e eventuais ressalvas estruturais.
- [Pendências editoriais prioritárias](pendencias-editoriais.csv): pontos concretos da fonte para cotejo. As demais ressalvas estão nas notas dos lotes.
- [Registro detalhado](progresso.json): hashes das fontes e das versões, contagens estruturais e títulos.
- [Escopo inicial](escopo.json): ordem e idiomas que faltavam, com hashes para proteger as versões existentes.
- [Gravação e histórico](gravacao.json): disponível após concluir a integração local.
- [Notas do lote 1](notas-lote-1.md).
- [Notas do lote 2](notas-lote-2.md).
- [Notas do lote 3](notas-lote-3.md).
- [Notas do lote 4 e complementos](notas-lote-4.md).

Os números de blocos descrevem a estrutura, não certificam equivalência linguística. As traduções são entregues para avaliação do usuário, sem receber automaticamente a marca de revisão editorial concluída.

## Critérios editoriais

Preservados títulos internos, parágrafos, perguntas e respostas, assinaturas, subscrições, carimbos, anotações, notas e referências. Nas palavras russas abreviadas com expansão entre sinais angulares, a tradução emprega a palavra completa no idioma de destino; não inventa uma abreviatura portuguesa ou inglesa para reproduzir a forma russa. Não há cabeçalhos de exportação dentro das novas versões: eles continuam sendo gerados pelo leitor ao baixar Markdown.

Alegações sobre crimes, organizações e responsabilidades continuam atribuídas às falas dos documentos. Contradições entre depoimentos não foram harmonizadas. Grafias problemáticas, cronologias, siglas e trechos truncados são tratados nas notas de cada lote. Referências bibliográficas suspeitas, como o ano 1917, não foram corrigidas por conjectura.

As referências arquivísticas mantêm seus números; Ф./Оп./Д./Л. correspondem a fundo/inventário/dossiê/folha em português e fond/inventory/file/leaf em inglês. Datas foram escritas no idioma de destino sem mudança de calendário. Nas novas versões, as variantes latinas Petr/Pyotr e Artem/Artyom foram uniformizadas para Pyotr e Artyom; o [registro de padronização](padronizacao.json) lista os arquivos afetados. Não houve alteração nas versões anteriores.

## Pontos prioritários para avaliação

- **2717:** ano 19343 na fonte.
- **2723:** patronímico Vasilyevich diverge do Semyonovich dos depoimentos próximos de Antonov.
- **3020:** ano bibliográfico 219 na fonte.
- **3022:** grafia anômala do sobrenome de Rumyantsev, acompanhada de nota.
- **3131:** “этот путь будет заказан” foi traduzido como caminho vedado / path closed, apesar da contradição aparente com o contexto; não se alterou o russo para resolver a passagem. Recomendado cotejo com imagem.
- **3172:** construções “centro dirigido” e “c.-r. revolucionária” obscuras ou redundantes no original.
- **3175–3176:** palavra aparentemente intrusa e frase truncada sobre Kirov/Stalin. Não se inseriu uma negação ausente.
- **9725, 3188, 3193, 3194:** cronologias divergentes sobre a reunião ou funeral de Shurygin, preservadas por documento.
- **3228:** sigla GUGV no cargo de Lyushkov, discrepante da GUGB das demais ocorrências.

As notas dos lotes detalham outros pontos e as escolhas de vocabulário. Esses casos podem exigir apenas revisão de tradução ou cotejo com a imagem; a presente entrega não afirma que todos sejam erros históricos do documento.

## Como conferir no site

1. Com o backend encerrado durante a gravação, inicie-o depois com `python3 -m backend`. Se usar apenas o site estático local, sirva a pasta como de costume.
2. Recarregue a página e abra `http://localhost:8000/#/colecao/centro-de-leningrado/subcolecao/investigacao`.
3. Abra um documento e escolha português ou inglês no painel. No estudo paralelo, coloque russo à esquerda e a tradução à direita.
4. Para uma amostra distribuída, abra 2683 (início), 3005 (grupos investigados), 3063 (texto extenso), 3131 (passagem ambígua) e 3237 (fim da lista).
5. Confira notas e referências no fim dos textos. Ao exportar, o idioma escolhido deve estar no nome do arquivo e o cabeçalho de metadados deve aparecer uma única vez.

A integração usa uma única operação recuperável no histórico editorial, com atualização de catálogo, manifesto e índice de busca. A restauração dessa operação remove apenas as novas versões e devolve os registros ao estado anterior; as traduções que já existiam pertencem ao estado preservado.

Nenhum teste, servidor de teste, commit ou push é executado nesta entrega. O diagnóstico estrutural faz parte do preparo do acervo. O comando `python3 scripts/import_leningrad_translations.py` apenas atualiza esse diagnóstico; `--apply` realiza a gravação e recusa arquivos existentes ou fontes alteradas. Após a gravação, não repita `--apply` para tentar sobrescrever traduções: use a área editorial.
