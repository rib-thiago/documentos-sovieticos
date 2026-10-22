# Análise das quatro propostas de coleta

Data: 20/10/2026. Escopo: leitura dos projetos em `temporario/proposta-coletores/`, inventários e código, comparação com a plataforma e consulta de amostras das fontes. Não houve coleta integral, instalação de dependências, execução dos coletores ou importação no catálogo. A disponibilidade de amostras não comprova a completude dos acervos.

## 1. Sakharov — o testamento político de Lenin

Viável como coleção de uma obra historiográfica, identificada como estudo posterior, com subdivisões editoriais próprias. O pacote aponta 60 páginas de navegação em russo e 18 extratos em inglês: esses números não representam capítulos equivalentes nem tradução integral. A página russa confirma a navegação em 60 partes. A paginação digital também não deve ser confundida com a edição impressa.

Fontes: [obra russa](https://leninism.su/books/4135-politicheskoe-zaveshhanie-lenina-realnost-istorii-i-mify-politiki.html), [índice inglês](https://neodemocracy.blogspot.com/2022/11/the-reality-of-history-and-myths-of.html).

Adaptações:
- Conferir conteúdos distintos, sequência e fronteiras antes de transformar páginas HTML em documentos.
- Preservar notas, remissões e tabelas; converter links relativos.
- Associar extratos ingleses somente após correspondência textual comprovada.
- Impedir sobrescrita de Markdown revisado: `write_section` grava novamente o arquivo derivado; o manifesto também é reconstruído por execução.
- Separar os metadados do front matter do corpo consumido pelo leitor e pela exportação.

É a proposta mais delimitada. O artigo de 1997 e a obra de 2003 não devem ser confundidos.

## 2. Svitlana/Erdogan — transcrições dos arquivos soviéticos

Viável em etapas. O inventário contém 35 entradas de índices: 14 volumes e 21 agrupamentos temáticos ou relacionados. Há sete correspondências russas e seis links de amostra; não se trata de 35 documentos nem de sete traduções paralelas já estabelecidas. O total efetivo depende da descoberta e da deduplicação.

Fontes: [índice editorial](https://neodemocracy.blogspot.com/2024/08/transcripts-from-soviet-archives-index.html), [volume I](https://marxistleninists.org/Soviet%20Archives/Transcripts/Volume%201%20-%201903-%201926/Index.htm).

Adaptações:
- Substituir a extração simples de TXT por conversão estrutural de HTML para Markdown. O extrator atual perde hierarquia, links e estrutura de tabelas.
- Diferenciar índice, documento, referência e PDF; os PDFs são registrados, mas não coletados pelo fluxo atual.
- Preservar o inventário anterior quando a atualização de um índice falhar; detectar respostas truncadas no limite de leitura.
- Distinguir autoria do documento, organização editorial e crédito de tradução. Uma tradução inglesa não deve ser apresentada como original inglês.
- Registrar ocorrências em vários volumes sem duplicar o documento.
- Representar volumes e grupos temáticos no modelo existente de coleção/subcoleção, sem presumir navegação de profundidade arbitrária.

Sobreposição identificada: a fonte `istmat.org/node/27376`, reunião do Conselho Militar de 1º de junho de 1937 à noite, já está cadastrada como `tukhachevsky-nko37-01-pm`. Deve-se reaproveitar esse documento e verificar o alcance da eventual tradução inglesa. Não foi realizada conciliação integral dos dois acervos.

## 3. Mozokhin — Politburo e Lev Trotsky

Viável, com maior atenção à segmentação. O inventário de 2013 prevê 295 números documentais, divididos em dois livros. O de 2017 prevê 307 números. São posições de inventário, não textos coletados: a diferença numérica não comprova doze documentos novos. A edição de 2017 aparece como acesso parcial, não como livro completo disponível.

Fontes: [livro I de 2013](https://djvu.online/file/Cpto0fbsiVoGW), [livro II de 2013](https://djvu.online/file/B0n1vSjUG0odl), [amostra de 2017](https://djvu.online/file/j6lpXpwfotQwr).

Adaptações:
- Corrigir o segmentador antes da coleta massiva. Ele só aceita o próximo número esperado; se um cabeçalho faltar ou estiver mal reconhecido, os seguintes podem ser ignorados e absorvidos pelo documento anterior.
- Não atribuir números documentais apenas pela posição no resultado de descoberta do catálogo.
- Conferir início, fim, notas, comentários editoriais e índices; separar página impressa de página digital.
- Usar a conciliação aproximada entre edições apenas como sugestão de revisão.
- Manter arquivo e metadados da mesma versão quando uma nova extração for recusada para preservar o Markdown existente.
- Encaminhar PDFs à infraestrutura de extração/OCR já existente. DjVu exige uma etapa própria de extração ou conversão; o coletor não fornece OCR por si só.

O pacote já oferece cache, hashes, retomada e proteção contra sobrescrita em parte do fluxo. Isso reduz o trabalho de adaptação, mas não valida as fronteiras documentais reais.

## 4. Brest-Litovsk

Viável como coleção temática progressiva, começando pelo núcleo HTML. Há 56 entradas de fontes e dez subcoleções propostas, combinando negociações, textos políticos, tratados, referências e estudos posteriores. Nem todas as entradas dão acesso a texto integral.

Fontes: [negociações em russo](https://iskra-research.org/USSR/Brest/1917-12-22.shtml), [índice de Kommunist](https://www.marxists.org/history/ussr/publications/kommunist/index.htm).

Adaptações:
- Manter a distinção já prevista entre índice, metadados, texto e fac-símile; reforçar a identificação do corpo documental.
- Tornar cumulativos os relatórios: `save_report` substitui o inventário pela execução atual.
- Permitir nova tentativa de erros sem sobrescrever fontes e revisões anteriores.
- Preservar todas as associações temáticas: a deduplicação atual por URL mantém a primeira entrada e pode perder grupos posteriores.
- Conservar calendários e datas duplas explicitamente, sem normalização silenciosa.
- Preservar notas, tabelas, identificação de oradores e links relativos.
- Não confundir as séries de Kommunist de Moscou e Petrogrado, nem intervenções individuais com atas integrais.
- Resolver traduções alternativas no mesmo idioma antes da publicação: o modelo atual de edição por documento/idioma não representa automaticamente várias versões inglesas concorrentes.

## Adaptação comum à plataforma

Os coletores são ferramentas externas; ainda não são ferramentas acionáveis pela interface editorial. Primeiro devem produzir candidatos revisáveis, não alterar diretamente os arquivos públicos.

Contrato de entrega recomendado por documento:
1. Fonte bruta preservada, URL consultada e final, data de coleta, hash e indicação de acesso integral ou parcial.
2. Markdown candidato, metadados, proveniência e créditos, sem alterar os originais existentes.
3. Fronteiras e notas verificadas, divergências explícitas e pendências com motivo e prioridade.
4. Correspondências com documentos existentes: URL normalizada, título, data, referência arquivística e conteúdo, sem decisões automáticas baseadas apenas em semelhança de títulos.
5. Registro cumulativo de sucesso, erro e revisão; repetição segura sem apagar trabalho editorial.

Após revisão, a integração deve atualizar os seis arquivos canônicos do catálogo, o manifesto e a busca pelo fluxo comum, preservando URLs e histórico. Documentos compartilhados recebem associações adicionais; não novas cópias independentes por padrão. Livros, estudos posteriores, documentos históricos e traduções devem permanecer identificáveis como tipos distintos.

Dependências de coleta devem ficar em ambiente opcional próprio. O backend atual não precisa receber dependências globais nem executar scripts arbitrários enviados pela interface. Coleta, revisão local e publicação são etapas distintas; a disponibilidade técnica de uma obra na internet não constitui uma política editorial de republicação.

## Paralelismo proposto

É possível distribuir as quatro frentes, após combinar o contrato comum e realizar pequenos pilotos de fronteiras, notas e duplicatas. No limite atual de quatro agentes ativos, a divisão é três agentes auxiliares e o agente principal na quarta frente.

Cada responsável escreve apenas em sua área de trabalho e entrega inventário, fontes, candidatos e relatório. Um único integrador altera catálogo, manifesto e busca. Essa separação evita conflitos nos arquivos compartilhados e permite conciliar sobreposições entre Svitlana/Erdogan, Mozokhin, Brest e o acervo atual.

Sakharov oferece um primeiro resultado mais delimitado; Svitlana/Erdogan demanda descoberta e conciliação de volume ainda desconhecido; Mozokhin exige validar o segmentador; Brest deve avançar por núcleos acessíveis. Aprovar quatro frentes não significa prometer acesso integral a todas as obras e referências indicadas.
