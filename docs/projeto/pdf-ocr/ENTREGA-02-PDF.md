# Oficina PDF — entrega 2: extração de páginas e divisão

20/10/2026. Implementada a manipulação inicial de PDFs, com prévia, processamento em fila, derivados locais e proveniência. OCR, edição da transcrição por página e publicação de fac-símiles continuam nas etapas seguintes. Sem commit ou push.

## O que mudou

- Recebimento em fluxo, sem manter todo o upload na memória do servidor.
- Limite padrão de **256 MiB**, configurável por `SHOWTRIALS_PDF_MAX_MIB` entre 1 e 2048. O limite vale para o recebimento; capacidade de processamento depende da estrutura do PDF e dos limites do worker.
- **Extrair páginas:** intervalos e páginas avulsas, respeitando a ordem digitada.
- **Dividir por quantidade:** um número de páginas por parte, incluindo a última parte com o restante.
- **Dividir por intervalos:** cada grupo separado por `;` gera um PDF.
- Prévia com nomes de arquivos, páginas, omissões e projeto de destino; nenhum arquivo é gerado antes da confirmação.
- Fila local persistente, resultados parciais preservados e retomada de operações interrompidas/com falha.
- Derivados registrados como novas fontes candidatas. Não substituem o original nem criam documentos públicos.
- Cada resultado guarda origem, SHA-256, receita/motor e mapa entre suas páginas físicas e as da origem.
- Resultados podem ser vinculados ao projeto escolhido numa única alteração recuperável do projeto.
- Download com nome do arquivo e acesso à proveniência na página da fonte.
- Instrumento **Manipular PDF** dentro da bancada, inclusive em projetos sem documentos, além da interface editorial.

Esta entrega adiciona controles funcionais aos componentes existentes. Não faz a revisão visual geral, não implementa painéis arrastáveis e não transforma todos os instrumentos anteriores em abas internas.

## Como abrir

Se o backend estiver aberto, encerre com Ctrl+C e reinicie:

```bash
python3 -m backend
```

Se a extração PDF já funcionava, não há nova dependência. Quando necessário, instale no mesmo Python:

```bash
python3 -m pip install -r backend/requirements-pdf.txt
```

- Fontes: http://127.0.0.1:8000/editorial#/pdf
- Ferramenta: http://127.0.0.1:8000/editorial#/pdf/ferramentas
- Bancada: entre explicitamente no projeto e escolha **Manipular PDF** na lateral.

O recarregamento continua começando sem projeto ativo. Escolha o workspace ou o destino do resultado explicitamente. Um link de projeto entra naquele contexto normalmente. Se os controles novos não aparecerem, use Ctrl+Shift+R.

### Alterar o limite de recebimento

Exemplo para uma execução do backend:

```bash
SHOWTRIALS_PDF_MAX_MIB=512 python3 -m backend
```

A interface consulta o limite em vigor. Valor inválido impede a inicialização com explicação; não é ignorado silenciosamente. O upload tem limite próprio; o worker continua com 1 GiB de memória, 300 segundos de CPU e até 10 minutos por execução. Não é uma promessa de processar todo PDF que caiba no upload. Original recebido fica preservado mesmo quando o processamento falha.

## Roteiro manual recomendado

### 1. Receber o PDF de Tukhachevsky

1. Abra **Fontes PDF → Receber PDF**.
2. Selecione `fontes/tukhachevsky/julgamento-1937-06-11.ru.pdf`, com aproximadamente 69,8 MiB.
3. Escolha o projeto de destino ou deixe sem vínculo. Envie e aguarde o inventário indicar **172 páginas**.
4. O PDF escaneado pode ficar sem texto extraível: nesta entrega não há OCR. Isso não impede a manipulação das páginas após o inventário.
5. Use **Extrair / dividir esta fonte**, ou selecione-a no instrumento da bancada.

### 2. Extrair uma amostra pequena

1. Escolha **Extrair páginas em um PDF** e digite `1-2`.
2. Clique em **Conferir operação antes de gerar**. Confira o arquivo de origem, o projeto de destino e as duas páginas. As outras 170 continuam no original.
3. Confirme. Aguarde **Concluída**, com um PDF gerado e registrado.
4. Baixe o resultado e confira suas duas páginas. Abra a fonte derivada e expanda **Proveniência e correspondência de páginas**: a página 1 deve apontar à página física 1 da origem, e a página 2 à página física 2.
5. Confira que o original de 172 páginas continua disponível, com o mesmo hash.

### 3. Dividir em partes

1. Volte à ferramenta e escolha **Dividir em vários PDFs → Quantidade de páginas por parte**.
2. Digite `20` para a fonte de 172 páginas.
3. A prévia deve indicar **9 arquivos**: oito partes de 20 páginas e a última com 12.
4. Confirme apenas se quiser manter esses candidatos locais. Abra partes do começo e do fim e confira as páginas de origem.
5. Como alternativa menor, use **Intervalos definidos por mim** com `1-4; 5-8; 9-12`. A prévia mostra três arquivos e as páginas não selecionadas.

### 4. Validar seleção e destino

- Em extrair, `8, 1-3` deve produzir quatro páginas nessa ordem, sem ordenar automaticamente.
- `1-4; 4-8` deve ser recusado na divisão por sobreposição. Números fora do PDF e páginas repetidas também são recusados.
- No workspace, o projeto de destino vem preenchido e continua visível. O seletor de fonte permite consultar o banco local; escolher uma fonte não muda o projeto de destino.
- O resultado só é vinculado ao destino exibido na prévia. Alterar o projeto em outra tela não redireciona uma operação já confirmada.
- Os vínculos aparecem no projeto e na lateral ao concluir. Em **Histórico do projeto**, a alteração de inclusão dos derivados pode ser restaurada. Isso remove vínculos, sem apagar os PDFs.

### 5. Interrupção e retomada

1. Durante uma divisão com várias partes, encerre o backend com Ctrl+C e reinicie.
2. Abra a ferramenta e expanda **Operações recentes neste contexto**.
3. Selecione a operação interrompida e use **Retomar operação / vínculo ao projeto**.
4. Partes já registradas são reaproveitadas. Artefatos completos não registrados são conferidos pelo hash; os pendentes são gerados novamente. O original não é regravado.
5. Se o projeto for arquivado durante a operação, os resultados permanecem disponíveis, mas pode aparecer aviso de vínculo não concluído. Reabra o projeto e retome para tentar apenas o que falta.

Fechar a tela não cancela o processamento. Ele continua no backend e pode ser consultado depois. O botão de cancelamento/pausa granular não foi implementado nesta etapa.

## Decisões técnicas e limites

- Originais e derivados registrados ficam em `.local/research/sources/`; IDs próprios e deduplicação por bytes.
- Operações e saídas ficam nas tabelas `pdf_operations` e `pdf_operation_outputs` do banco `.local/research/jobs.sqlite3`.
- Arquivos em geração ficam em `.local/research/operations/ID/`. Após o registro confirmado da saída, a cópia de processamento é removida; o PDF no banco de fontes e a proveniência permanecem.
- Um processo isolado gera PDFs por vez, compartilhando a fila local com a extração pesquisável. Leitor e catálogo não ficam bloqueados durante a geração.
- Até **200 saídas** por operação. O limite inicial de inventário/extração continua em **1.500 páginas por fonte**.
- A divisão por intervalos pode omitir páginas deliberadamente. A prévia informa quantas; não apaga nada do original.
- O mapa é em relação à fonte imediatamente anterior. Se um derivado for dividido novamente, siga a cadeia de fontes para chegar ao arquivo inicial. Não inferimos números impressos ou correspondência de parágrafos a partir da paginação física.
- Navegação interna do PDF (marcadores) não é copiada. Formulários, links e anotações devem ser conferidos no resultado quando existirem. A cópia integral da fonte continua preservada.
- Uso de [pypdf para seleção e cópia de páginas](https://pypdf.readthedocs.io/en/stable/user/merging-pdfs.html), sem rasterização nem OCR.
- Não implementados: combinar PDFs de várias fontes, girar páginas, compressão, redigir/ocultar conteúdo, tratamento de imagens ou OCR. Reordenar páginas de uma fonte é possível pela ordem explícita de extração; não há arraste visual para isso.

### Backup

Encerre o backend e copie **toda `.local/research/`**: banco de jobs, banco de projetos, fontes e candidatos de operações interrompidas. O diretório é ignorado pelo Git; commit/push não guardam esse estado. Não reconstruir nem apagar esses bancos para atualizar a busca.

## Verificações executadas

- Testes novos de seleção, prévia, geração, proveniência, divisão, retomada parcial, vínculos recuperáveis, identidade da origem e upload em fluxo: `tests/test_pdf_operations.py`.
- Os 23 testes existentes de backend passaram em fixtures temporárias.
- Piloto HTTP temporário passou: upload → inventário real → prévia → confirmação → geração em segundo plano → download com nome → leitura por intervalo → vínculo no projeto. O catálogo/manifesto/textos da fixture ficaram iguais.
- Cópia isolada do PDF russo real: recebidos **73.195.742 bytes**, inventário de **172 páginas**, gerado um derivado de **2 páginas / 891.529 bytes**, mapa `[1,2]`; SHA-256 do original preservado: `afcb052ed8750c723ca5ed6e1b24c6f9b2128ff5f2e2c6d0073f3aa1d1c64cbb`.
- Regressão JavaScript de contexto e editor passou; o novo instrumento foi exercitado com DOM/rede simulados, incluindo ausência de geração antes da confirmação, destino explícito, andamento e link de download.
- Não há navegador gráfico neste ambiente: CSS, foco, rolagem, visualizador nativo e aparência ainda precisam da sua conferência manual. Não foram feitos commit ou push.
