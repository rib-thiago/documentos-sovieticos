# Traduções — Materiais da investigação do Centro de Moscou

## Escopo e estado

Entrega iniciada após o commit e push **16a63af**, que publicou as seis traduções do andamento do processo de Leningrado. A subcoleção de investigação do Centro de Moscou contém **367 documentos**, inicialmente apenas em russo: são **734 versões** solicitadas, em português e inglês, com cerca de 3 MB de originais russos.

As **734 traduções integrais dos 367 documentos estão concluídas e cadastradas localmente**, em português e inglês. Catálogo, manifesto e índice de busca foram atualizados em 16 gravações com histórico recuperável. O estado de cadastro por documento e idioma está em [progresso.csv](progresso.csv) e [progresso.json](progresso.json); as gravações locais constam de [gravacoes.json](gravacoes.json). A conclusão da tradução não equivale a revisão humana: as versões permanecem disponíveis para o cotejo e os ajustes editoriais do responsável pelo acervo.

## Método e preservação

Tradução direta pelos agentes autorizados pelo usuário, sem serviços externos de tradução nem substituições automáticas para gerar o corpo dos documentos. As fontes são lidas integralmente e as versões mantêm parágrafos, perguntas, respostas, nomes, notas, assinaturas e referências. Expansões de abreviaturas russas são vertidas como palavras completas. Não se inserem cabeçalhos de exportação no corpo das traduções.

Alegações dos depoimentos continuam atribuídas às fontes. Datas, grafias ou cronologias problemáticas não são corrigidas silenciosamente: as ressalvas ficam nas notas de cada lote. Originais, traduções anteriores, metadados existentes e URLs são preservados.

Cada versão integral recebe um marcador de conclusão com hash na área de trabalho `.local/traducoes/moscou-investigacao/concluidas/`. Arquivos parciais não recebem esse marcador. A importação exige marcador válido, título e documento completo nos idiomas pendentes; não sobrescreve versões que já tenham sido cadastradas ou editadas pelo usuário.

## Registros e retomada

- [Escopo inicial e hashes](escopo.json).
- [Progresso legível](progresso.csv) e [detalhamento](progresso.json).
- [Histórico das gravações locais](gravacoes.json), uma entrada para cada grupo importado.
- [Notas do lote inicial e complementos](notas-lote-root.md).
- [Pontos de atenção para o cotejo manual](pontos-de-atencao.md).
- Notas incrementais dos lotes paralelos em `notas-lote-1.md`, `notas-lote-2.md` e `notas-lote-3.md`; o documento longo 4532 tem registro próprio em `notas-lote-final4532.md`.

A área de trabalho conserva os lotes atribuídos, as versões preparadas, os mapas de títulos e os marcadores de conclusão. Esses registros permitem retomar após interrupções sem refazer versões completas nem tomar um arquivo parcialmente escrito por uma tradução concluída.

## Cadastro e leitura local

O comando de produção `python3 scripts/import_moscow_translations.py` atualiza o diagnóstico de progresso. Com `--apply-ready`, cadastra até 30 documentos completos por gravação; `--limit` ajusta esse limite. As gravações utilizam o mecanismo editorial existente, com histórico recuperável e atualização de catálogo, manifesto e índice de busca.

O backend deve estar encerrado durante a gravação, conforme a proteção de concorrência já existente. Depois, inicie-o com `python3 -m backend`, recarregue a página e abra:

`http://localhost:8000/#/colecao/centro-moscovita/subcolecao/investigacao`

Exemplos para abrir diretamente após iniciar o backend:

- Curto, com perguntas e respostas: `http://localhost:8000/#/doc/showtrials-3902`.
- Longo, com notas: `http://localhost:8000/#/doc/showtrials-4358`.
- Com variantes entre cópias em cinco notas: `http://localhost:8000/#/doc/showtrials-3451`.

Nos documentos já traduzidos, selecione português ou inglês. O estudo paralelo permite cotejar a tradução com o russo. As correções posteriores devem ser feitas pelas ferramentas editoriais existentes, preservando o histórico.

Contagens de blocos descrevem a estrutura, não certificam qualidade linguística. As versões não recebem automaticamente uma marca de revisão humana concluída. A gravação é somente local: **não há autorização de commit ou push das traduções de Moscou nesta etapa**. Não são executados testes, servidores de teste ou publicação automática.
