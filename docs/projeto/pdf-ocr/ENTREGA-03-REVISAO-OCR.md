# Oficina PDF — entrega 3: revisão por página e OCR

20/10/2026. Continuação da entrega PDF aprovada. Sem commit ou push.

## O que está disponível

- Texto pesquisável continua sendo extraído com pypdf, sem OCR automático.
- Revisão local por página física, ao lado do fac-símile: transcrição, estado de conferência, rótulo impresso e notas.
- Estados: pendente, conferida, com problema, em branco. Página marcada em branco exige texto vazio.
- Prévia das diferenças antes de gravar; histórico recuperável, revisão concorrente e restauração como nova revisão.
- OCR opcional com Poppler/Tesseract, nos idiomas russo (`rus`), inglês (`eng`) e português (`por`), inclusive combinados.
- Escolha explícita de páginas físicas, 150/200/300 DPI e distribuição automática ou bloco único. Até 50 páginas por lote; para começar, use uma ou duas.
- Fila persistente com acompanhamento e retomada das páginas restantes. Cada página OCR concluída é confirmada separadamente.
- Resultados OCR são candidatos imutáveis; podem ser comparados e carregados no editor. Reprocessar não substitui a revisão salva.
- Extração nativa, candidatos OCR e texto corrigido são camadas separadas. O PDF permanece intacto.
- Teclado virtual russo disponível nos campos de texto, como nos demais editores.
- Rascunhos não salvos ficam na sessão do navegador, quando o armazenamento estiver disponível. Volte à página e use **Recuperar rascunho da sessão**. Para persistência independente do navegador, confira e salve a revisão no backend.

A revisão pertence à **fonte PDF local**, compartilhada pelos projetos que a referenciam. Não substitui as versões Markdown de documentos, sejam públicas ou privadas de um projeto. A interface sinaliza essa distinção; a incorporação editorial do resultado será uma etapa explícita posterior.

## Como iniciar e acessar

Encerre o backend anterior com Ctrl+C e inicie novamente:

```bash
python3 -m backend
```

Abra http://127.0.0.1:8000/editorial#/pdf e entre em **Abrir fonte e páginas**. Use Ctrl+Shift+R se o navegador mantiver arquivos antigos.

Na bancada, abra **Manipular PDF**, escolha a fonte e clique em **Revisar fonte / executar OCR**. A revisão aparece no instrumento, na mesma guia. Não é necessário gerar um derivado para revisar.

### Dependências

A extração pesquisável continua usando `backend/requirements-pdf.txt`. O OCR exige Poppler e Tesseract com modelos de idioma. A interface mostra disponibilidade e idiomas detectados.

No Ubuntu/Debian, caso faltem:

```bash
sudo apt install poppler-utils tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng tesseract-ocr-por
```

Não foi feita instalação de pacotes nesta entrega. Neste ambiente os três modelos já estavam instalados. A variável do terminal `TESSDATA_PREFIX` apontava para uma pasta sem modelos; a detecção agora verifica também instalações usuais do sistema e mostra a pasta efetivamente utilizada. Para escolher explicitamente outra pasta, use:

```bash
SHOWTRIALS_TESSDATA_DIR=/caminho/para/tessdata python3 -m backend
```

Uma configuração explícita inválida não é substituída por outra pasta. Em outros sistemas, instale os executáveis de modo que `pdftoppm` e `tesseract` estejam no PATH, e indique a pasta dos modelos quando necessário. O isolamento de recursos desta implementação usa Linux/Unix, como o backend atual.

## Roteiro manual

### 1. Revisar uma página pesquisável

1. Abra uma fonte que já possua texto extraído. O texto deve aparecer em **Transcrição de trabalho**, junto ao fac-símile.
2. Modifique uma palavra; informe um rótulo impresso e uma nota. Escolha **Conferida**.
3. Clique em **Conferir alterações**. Veja o texto alterado e os metadados propostos. Antes da confirmação, nada foi gravado na revisão.
4. Clique em **Confirmar gravação local**.
5. Vá à próxima página e volte. A correção deve permanecer. Em **Consultar extração bruta preservada**, o texto nativo continua como antes.
6. Encerre/reinicie o backend e confira novamente: a revisão deve permanecer.

### 2. OCR de uma página escaneada

Use a fonte `fontes/tukhachevsky/julgamento-1937-06-11.ru.pdf` já recebida, ou receba-a pela oficina. Também pode usar um derivado pequeno preparado na entrega anterior.

1. Abra **OCR configurável e progresso da revisão**.
2. Digite `1`, selecione **Russo**, **200 DPI** e **Automática**.
3. Clique em **Conferir lote OCR**. Confira páginas e idioma; depois confirme a execução.
4. Aguarde **Concluído**, com `1/1` página. O resultado não substitui o editor automaticamente.
5. Use **Atualizar página / candidatos OCR** (ou **Atualizar página**, na bancada).
6. Expanda **Candidatos OCR e comparação**. Consulte o texto e clique em **Comparar com a versão salva**.
7. Clique em **Carregar este candidato no editor**, faça as correções e confira/salve a revisão.
8. Reexecute OCR na mesma página. Após atualizar, deve existir outro candidato; sua transcrição corrigida deve permanecer.

No piloto real, a página escaneada sem camada textual produziu 378 caracteres em russo. O OCR reconheceu equivocadamente o ano como **1987**; o reconhecimento não é uma edição crítica nem garante fidelidade de datas, nomes ou notas. O candidato foi preservado sem correção silenciosa. A função da tela é permitir esse cotejo humano.

### 3. Histórico, conflitos e rascunho

1. Salve duas revisões diferentes de uma página.
2. Abra **Histórico recuperável desta página**, veja o estado anterior e escolha **Preparar restauração**.
3. Confira e confirme. A restauração cria outra revisão e mantém as anteriores.
4. Abra a mesma página em duas abas, salve na primeira e tente salvar a segunda sem atualizá-la. Deve haver aviso de conflito, preservando a revisão mais recente.
5. Digite uma alteração sem salvar, mude de instrumento na bancada e volte à revisão da fonte: recupere o rascunho da sessão. Confira antes de salvar, especialmente se a revisão mudou em outra aba.
6. Ao navegar entre páginas com alterações pendentes, o sistema pede confirmação. Sair não equivale a salvar; o rascunho da sessão serve apenas como recuperação auxiliar.

### 4. Retomada

1. Confirme um lote pequeno de várias páginas e encerre o backend durante o processamento.
2. Reinicie, abra a fonte e expanda o painel OCR.
3. O lote interrompido oferece **Retomar páginas restantes**. As páginas já concluídas não são duplicadas dentro do mesmo lote.
4. Para produzir outro resultado de uma página concluída, crie um novo lote. Isso preserva os candidatos anteriores.

## Citações e evolução do alinhamento

Unidades da revisão têm ID, página física, offsets em pontos de código Unicode e SHA-256. Trechos que permanecem idênticos conservam seus IDs mesmo quando reordenados; trechos alterados ou criados recebem novos IDs. O histórico preserva o contexto das revisões anteriores. Use **Referências dos trechos da revisão → Copiar referência**.

As fronteiras ainda são candidatas por linhas em branco. Não se deve confundir essas referências com parágrafos já validados ou caixas alinhadas manualmente. O worker guarda também o TSV de palavras/coordenadas do Tesseract e a receita/motores utilizados, preparando o trabalho de alinhamento visual. Não há ainda editor de caixas, comando explícito de dividir/unir com mapa de sucessão, nem correspondência geométrica verificada entre a transcrição corrigida e o fac-símile.

## Armazenamento e limites

Banco durável: `.local/research/jobs.sqlite3`, com tabelas próprias de revisão, histórico, lotes e candidatos OCR. Arquivos temporários de imagem são descartados ao concluir; imagens de uma interrupção abrupta podem permanecer em diretórios temporários de trabalho, sem substituir o PDF. Faça backup de **toda** `.local/research/` com o backend encerrado. A busca reconstruível não substitui esse backup.

OCR executa em processo separado; limites por execução: 30 minutos de parede, 600 segundos de CPU e 2 GiB de memória virtual. Cada renderização tem 90 segundos e cada reconhecimento 180 segundos. Há limites de imagem e de saída por página. Ao falhar, reduza DPI/tamanho do lote e retome; um novo parâmetro exige novo lote. Encerrar o backend encerra também os subprocessos das ferramentas.

A extração nativa e as ferramentas usam um supervisor serial: um lote OCR longo faz as demais tarefas aguardarem. Ainda não há cancelamento pela interface, rotação/correção de inclinação configurável, tratamento especial de tabelas ou painel de coordenadas.

## Verificação realizada

- Dez testes em bancos temporários: prévia, revisão, histórico, concorrência, IDs estáveis, validações, dependência ausente, OCR real em inglês, retomada sem duplicação, integridade da fonte e persistência após reabertura.
- Fluxo HTTP completo em servidor temporário: upload, extração, revisão, conflito e OCR pela fila real, preservando hashes do catálogo da fixture.
- Piloto OCR russo na primeira página do julgamento de Tukhachevsky, em cópia temporária; fonte real intacta.
- Verificação de lógica/sintaxe JavaScript e dez verificações das telas de revisão/OCR com DOM/API simulados. A regressão das operações PDF também passou (13 testes). Isso não substitui sua inspeção visual em navegador.

## Próxima entrega

Vincular explicitamente a fonte/páginas a documentos e disponibilizar fac-símiles no modo estudo, com revisão de fronteiras e alinhamento para citações. Depois, incorporação controlada das transcrições ao acervo e publicação estática selecionada. As regras de versões privadas por projeto e confirmação antes de substituir uma edição pública continuam valendo.

Referência do adaptador: [documentação oficial de linha de comando do Tesseract](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html), para idiomas, segmentação e saídas de texto/TSV.
