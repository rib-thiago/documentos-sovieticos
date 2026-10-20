# Oficina PDF — entrega 4: documentos, fac-símiles e referências

20/10/2026. Continuação aprovada da revisão/OCR. Sem commit ou push.

## Resultado

Um documento pode ser associado explicitamente a uma ou mais fontes PDF locais e às páginas físicas que lhe correspondem. O modo estudo oferece consulta do fac-símile, navegação pelas páginas vinculadas e visualização da transcrição de trabalho. É possível associar manualmente um bloco Markdown a uma página e copiar uma referência com identificadores verificáveis.

Essa etapa não importa automaticamente a transcrição para um documento, não publica PDFs e não presume que os parágrafos de uma tradução tenham as mesmas fronteiras do original. A associação é uma decisão editorial humana, registrada por idioma e versão do texto.

## Como acessar

Reinicie o backend:

```bash
python3 -m backend
```

Acesse o site por http://127.0.0.1:8000/ . Se necessário, use Ctrl+Shift+R. Não há dependência nova além das ferramentas PDF/OCR da entrega anterior.

Há dois caminhos para cadastrar os vínculos:

- **Documento → Ferramentas → Fontes e fac-símiles → Gerenciar fontes e páginas.** O documento e o contexto já vêm definidos.
- **Área editorial → Fontes PDF → Abrir fonte e páginas → Vincular esta fonte a um documento.** Busque pelo título/termos ou informe o ID exato. A fonte já vem definida. A mesma opção existe no instrumento PDF da bancada, dentro da revisão da fonte.

Informe as páginas físicas, como `1-5, 8`, e uma nota de correspondência. Confira a prévia e confirme o vínculo. Não é preciso executar OCR antes de vincular um PDF cujo inventário já foi concluído.

## Roteiro manual

### 1. Vincular e consultar

1. Escolha um documento do site e uma fonte PDF recebida que efetivamente lhe corresponda. O sistema não verifica historicamente essa correspondência por conta própria.
2. No painel do documento, abra **Fontes e fac-símiles → Gerenciar fontes e páginas**.
3. Escolha a fonte, indique suas páginas físicas e escreva uma nota. **Conferir novo vínculo** mostra o estado proposto; só **Confirmar vínculo local** grava.
4. Feche a janela. A fonte deve aparecer na lista do painel, com seu título/nome e páginas.
5. Clique nela. O leitor entra em **Estudo** e mostra o fac-símile. Em telas largas, ele fica ao lado do texto; em telas menores, abaixo do texto. Isso também funciona em documentos com apenas um idioma.
6. Use o seletor de página e as setas. **Consultar transcrição da página** mostra o texto de trabalho da entrega anterior, incluindo correções salvas; não executa OCR nem o substitui por uma tradução.
7. **Recolher fac-símile** libera novamente a área do texto. Fixar a barra, marcar trecho e alternar os modos continuam disponíveis.
8. Reabra a fonte e use **Copiar referência da página**. Confira documento, fonte, página física, hash do PDF e revisão do vínculo. Se a transcrição foi carregada, a referência inclui seu rótulo impresso e revisão.

### 2. Associar um trecho

1. Mantenha o documento no modo **Estudo**, por parágrafo ou paralelo.
2. Em um bloco Markdown, clique em **Associar página PDF**.
3. Confira o trecho literal, escolha a fonte vinculada e a página física. A janela mostra o PDF da página escolhida para cotejo. O idioma é o da célula acionada; não é transferido automaticamente para as demais versões.
4. Escreva uma nota, use **Conferir associação** e depois **Confirmar associação local**.
5. O bloco passa a oferecer **Ver fac-símile · p. N** e **Copiar referência com fac-símile**.
6. Copie a referência e confira idioma, página, rótulo impresso quando cadastrado, ID da associação, revisão do vínculo e hashes do texto/PDF. O número visual do bloco permanece auxiliar; a referência não depende apenas dele.

A unidade é o bloco Markdown do modo estudo, que pode ser parágrafo, título, lista ou outra estrutura. Arquivos TXT sem limites Markdown verificáveis podem consultar o PDF vinculado, mas ainda não recebem associação de bloco por este mecanismo.

### 3. Alterar e recuperar vínculos

1. Volte a **Gerenciar fontes e páginas**. Cada vínculo existente permite alterar páginas, notas e seu estado ativo, com prévia.
2. Desativar recolhe o vínculo do leitor e preserva seu cadastro e suas associações.
3. O **Histórico do vínculo** permite consultar o estado anterior e **Preparar restauração**, novamente com prévia. Restaurar o estado anterior à criação o torna inativo; não apaga o PDF.
4. Associações de trechos podem ser removidas nessa mesma tela, com prévia e histórico recuperável.
5. Não é permitido retirar uma página enquanto houver uma associação de trecho apontando para ela. Remova primeiro essa associação.
6. Duas abas editando a mesma revisão não se sobrescrevem: a segunda gravação deve exigir atualizar/refazer a prévia.

### 4. Conferir desatualizações

1. Associe um bloco a uma página e depois altere a versão Markdown pelo editor existente.
2. Reabra o documento. Em **Gerenciar fontes e páginas**, a associação deve aparecer com **REVISAR: texto ou transcrição mudou**.
3. Se o trecho literal ainda for identificável de forma segura na tela, sua ação aparece como **Revisar vínculo**. Trechos que mudaram de conteúdo podem deixar de ter ação na célula; a associação antiga continua consultável no gerenciador e no histórico.
4. Não há realocação silenciosa. Confira o PDF e estabeleça a associação da versão atual; se necessário, remova a associação antiga pelo gerenciador.
5. Alterar a transcrição de trabalho da página também sinaliza reconferência. A referência antiga conserva a revisão que estava associada.

A invalidação do texto é conservadora: mudar qualquer parte do corpo da edição exige conferir suas associações, mesmo que um bloco específico pareça igual. O hash completo impede que uma mudança de versão passe despercebida. Restaurações de histórico não tornam automaticamente atuais associações de versões antigas.

### 5. Conferir o isolamento dos projetos

1. Entre explicitamente em um projeto que contenha tanto o documento quanto a fonte PDF. Faça os vínculos do projeto na bancada/na leitura naquele contexto.
2. Abra o mesmo documento sem projeto: os vínculos privados não devem aparecer. Vínculos sem projeto também não são copiados automaticamente para projetos.
3. Outro projeto mantém seus próprios vínculos e usa suas próprias versões Markdown.
4. Um projeto arquivado pode ser consultado; deve ser reaberto antes de alterar vínculos ou associar trechos.
5. Se o documento ou a fonte não pertencer ao projeto, vincule-os primeiro na página do projeto. Não há inclusão oculta de referências.

O início/recarregamento do site continua sem projeto ativo. Escolha o workspace explicitamente para conferir vínculos privados; não confunda a ausência deles no contexto geral com perda de dados.

## Dados preservados

Tabelas `pdf_document_links` e `pdf_document_link_history`, no banco durável `.local/research/jobs.sqlite3`. O PDF e a transcrição mantêm seus armazenamentos anteriores. Faça backup de toda `.local/research/` com o backend encerrado.

Cada associação registra: fonte/hash do PDF, documento e contexto, idioma, trecho literal e SHA-256, hash do corpo completo da edição, offsets UTF-16 (compatíveis com a seleção do navegador), página física, rótulo impresso e revisão da transcrição disponíveis no momento, nota e ID persistente. Histórico registra antes/depois. Offsets não são coordenadas na imagem.

Catálogo, manifesto, busca e textos não são regravados por vínculos. A publicação estática dessas fontes e relações ainda será uma operação editorial explícita; esta entrega funciona no backend local.

## Verificação e limites

Quatorze testes em acervo temporário cobrem prévia, gravação, restauração, concorrência, duplicação, páginas/trechos inválidos, preservação do acervo, isolamento de projetos e invalidação por mudança de texto/página. O fluxo HTTP foi conferido em servidor temporário, e onze verificações dos controles e do estudo monolíngue passaram com JavaScript e DOM/API simulados. A regressão JavaScript passou em 34 verificações de comportamento/sintaxe. Não houve inspeção visual com navegador real.

Pendências:

- Delimitar caixas de parágrafo na imagem, revisar coordenadas OCR e dividir/unir unidades com sucessão de IDs.
- Permitir que um mesmo bloco aponte para várias páginas, para parágrafos que atravessam uma virada; por enquanto, pode-se registrar a continuação na nota e consultar todas as páginas do vínculo.
- Criar URLs de citação por revisão para acesso público às versões históricas; os identificadores/hashes atuais não substituem esse futuro mecanismo.
- Mostrar avisos de associação desatualizada diretamente no catálogo/fila de revisão.
- Importar a transcrição revisada como versão Markdown mediante conferência editorial, com seleção de destino e confirmação de substituição.
- Publicar os fac-símiles escolhidos e suas projeções estáticas, respeitando a separação entre projeto privado e acervo público.

A associação manual atual relaciona **bloco textual e página**. Ela não deve ser apresentada como localização geométrica exata ou validação automática da tradução.
