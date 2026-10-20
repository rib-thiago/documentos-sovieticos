# Oficina PDF — entrega 1: fontes e extração pesquisável

20/10/2026. Implementação para validação manual do pesquisador; sem testes, servidor, navegador, instalação, commit ou push executados pelo assistente.

## O que está disponível

Na área editorial, **Fontes PDF** recebe o original, calcula SHA-256, detecta repetição do mesmo arquivo e extrai a camada textual página a página em um processo isolado. A fonte continua candidata até a confirmação de seus metadados, com prévia e histórico próprio. Uma fonte cadastrada ainda não é um documento publicado.

O painel mostra PDF original no visualizador nativo do navegador e texto bruto lado a lado, diagnóstico por página, referências candidatas de parágrafo e retomada da página física. Histórico permite recuperar o cadastro anterior sem apagar o arquivo ou a extração. Criação de coleção/subcoleção reutiliza as páginas existentes, em outra aba; o botão Atualizar opções incorpora as novas escolhas.

O teclado russo recolhível aparece junto aos campos de texto multilinha editáveis, inclusive no editor Markdown, nos rascunhos da bancada e na correção de trechos do estudo. Insere na posição do cursor ou substitui a seleção, tem maiúsculas, espaço e apagar, e aciona o fluxo normal de prévia/alterações pendentes.

## Antes de iniciar

Se o backend estiver aberto, encerre-o com Ctrl+C. Na pasta do projeto, usando o mesmo Python do backend:

```bash
python3 -m pip install -r backend/requirements-pdf.txt
python3 -m backend
```

A instalação é opcional para as demais funções: sem pypdf, leitor, catálogo e traduções continuam funcionando e a oficina informa como habilitar a extração. Se seu Python recusar instalação global, use um ambiente virtual e execute instalação e backend nele; não force a alteração do Python do sistema. Esta entrega não muda Poetry nem seu lock.

Abra http://127.0.0.1:8000/editorial#/pdf . Se usar outra porta, ajuste o endereço. Se o navegador mantiver a interface anterior, recarregue com Ctrl+Shift+R.

## Conferência manual, em ordem

### A. PDF pesquisável

1. Clique em **Receber PDF** e escolha um arquivo pequeno cujo texto você consiga selecionar no leitor habitual.
2. Clique em **Enviar e preparar prévia**. Aguarde o estado de extração concluída. O PDF é preservado mesmo antes de confirmar seu cadastro; não é publicado.
3. Confira a primeira, uma intermediária e a última página com os controles de página física. O visualizador do navegador pode também mostrar sua própria navegação: use os controles externos para atualizar conjuntamente o texto da oficina.
4. Compare notas, ordem do texto e caracteres russos. O diagnóstico “Texto extraído” não atesta qualidade editorial.
5. Expanda **Referências candidatas de parágrafo**. Os IDs identificam a fonte/página/unidade da extração; copiar inclui o hash da versão textual e a advertência de unidade candidata. PDFs sem linhas em branco podem produzir uma única unidade por página — não uma divisão editorial inventada.
6. Preencha título, coleção e idioma; deixe **Sem subcoleção** se desejar. Confira a prévia e confirme a gravação local. Nada será adicionado ainda à lista pública de documentos.

### B. Coleção e subcoleção

1. Use **Criar coleção / subcoleção**. A página de coleções abre em outra aba com o fluxo existente de prévia/histórico.
2. Cadastre o destino desejado e volte à fonte. Clique em **Atualizar opções** e selecione a nova coleção/subcoleção.
3. Tente escolher outra coleção: as subcoleções exibidas devem acompanhar sua escolha. Confirme e confira o histórico da fonte.

### C. Persistência e recuperação

1. Abra uma página intermediária já extraída e volte à lista de fontes; reabra a fonte. A página deve ser retomada.
2. Encerre e reinicie o backend. Abra a mesma fonte: PDF, extração, cadastro e página permanecem disponíveis.
3. Modifique o título, confira e salve. Abra **Histórico do cadastro da fonte**, confira o estado anterior mostrado e restaure. O PDF e a extração devem permanecer.
4. Envie o mesmo PDF novamente: deve abrir a mesma fonte, preservando o cadastro, sem criar uma cópia redundante.
5. Opcionalmente abra uma fonte em duas abas. Salve metadados numa delas; a outra deve rejeitar uma gravação com revisão antiga, pedindo que reabra a prévia.

### D. Escaneado e interrupção

1. Envie um pequeno PDF escaneado. As páginas sem texto devem informar possível necessidade de OCR; páginas brancas também precisam de avaliação visual.
2. Nesta entrega não existe botão para executar OCR: isso será a entrega 3, com russo, inglês e português.
3. Para conferir retomada, use um PDF que demore a processar, encerre o backend e reinicie. Se houver páginas pendentes, use **Retomar páginas pendentes ou com falha**. Páginas concluídas são reaproveitadas; páginas com erro são tentadas novamente.

### E. Teclado russo

1. Abra um documento russo no editor Markdown local ou seu rascunho na bancada.
2. Expanda **Я · Teclado russo**, posicione o cursor e clique em algumas letras, incluindo ё, й, ъ e ь.
3. Selecione uma palavra e substitua por letras do teclado; confira maiúsculas, espaço e apagar.
4. Confira que a prévia/indicação de alterações pendentes acompanha a edição. Para validar sem alterar uma fonte, use o rascunho e descarte depois.
5. O texto bruto extraído de PDF é somente leitura nesta entrega e, por isso, não recebe teclado. Na próxima etapa ele será aplicado também ao campo de revisão da página.

## Decisões e armazenamento

- Módulos novos: `backend/pdf_sources.py`, `backend/pdf_worker.py`; interface em `assets/pdf-sources.js`; teclado em `assets/russian-keyboard.js`; estilos compartilhados em `assets/css/pdf-sources.css`.
- Dados operacionais duráveis em `.local/research/jobs.sqlite3`, independentes do índice descartável `.local/catalog.sqlite3`.
- Originais imutáveis em `.local/research/sources/pdf-ID.pdf`. Identidade deduplicada por SHA-256; nome enviado nunca é usado como caminho livre.
- Texto bruto e unidades candidatas são persistidos por página. Offsets contam caracteres Unicode do texto bruto, com início inclusivo e fim exclusivo; hash distingue a versão. IDs não devem ser reconstruídos ao corrigir texto futuramente.
- Não inferimos numeração impressa a partir da posição física. O campo existe para futura revisão.
- O catálogo e o manifesto atuais não são modificados pela recepção de uma fonte. A criação de coleções, quando solicitada, segue a camada editorial já existente.
- HTTP continua atendendo leitor e catálogo durante extração. Um worker supervisor chama um processo extrator por vez; o processo tem limites de recursos e conserva cada página concluída.
- Limites iniciais: 60 MiB e 1.500 páginas por PDF; 1 GiB de memória e 300 segundos de CPU por processo, além de 10 minutos de tempo total por execução. São limites do piloto, com retomada, não uma promessa de processamento de qualquer PDF.
- PDFs protegidos devem ser enviados como cópias desprotegidas cuja leitura seja permitida. Arquivos malformados ou páginas muito grandes geram pendência, sem substituir o original.

**Backup:** encerre o backend e copie toda a pasta `.local/research/`, incluindo banco e PDFs. Ela está fora do Git; push não é backup desse trabalho. Nunca apague esse banco ao reconstruir a busca.

## Próximas entregas e pendências

1. **Entrega 2:** texto corrigido por página, revisão-base/histórico, progresso editorial, retomada e montagem do documento pelo fluxo de prévia; conectar fac-símile ao documento no modo estudo. O painel inicial usa o visualizador PDF do navegador; uma renderização controlada permitirá melhor integração.
2. **Entrega 3:** OCR opcional `rus`, `eng`, `por`, seleção por página, indicação dos idiomas instalados e comparação de reprocessamentos. Não confundir camada textual encontrada com texto necessariamente bom.
3. **Entrega 4:** intervalos de uma fonte para vários documentos, referências públicas por página e passagem e seleção de derivados públicos. Sem publicação automática.
4. **Citações por parágrafo:** manter IDs independentes da ordem visual, registrar revisão, página(s), texto e eventual região da imagem; permitir divisão/união com rastreamento. O candidato inicial não é uma referência editorial definitiva. A revisão de fronteiras deve fazer parte da entrega 2, sem aguardar um alinhamento automático perfeito.
5. Download Markdown da transcrição, edição de numeração impressa, seleção de regiões da imagem e OCR com coordenadas serão integrados nas etapas seguintes. Não há correção de tabelas ou notas automática nesta entrega.

## Referências técnicas

A extração usa a API pública de [pypdf](https://pypdf.readthedocs.io/en/stable/user/extract-text.html), que lê a camada textual e não executa OCR. A [instalação](https://pypdf.readthedocs.io/en/stable/user/installation.html) é mantida opcional. A ausência de uma estrutura semântica confiável em PDF exige revisão das fronteiras de parágrafos e da ordem de leitura.

## Atualização posterior

O limite histórico de 60 MiB foi substituído por upload em fluxo, com padrão de 256 MiB configurável. Extração de páginas e divisão foram implementadas na [entrega 2](ENTREGA-02-PDF.md), com integração ao painel da bancada, preservação da origem e retomada. As limitações de edição por página/OCR descritas nesta primeira entrega continuam até as próximas etapas.
