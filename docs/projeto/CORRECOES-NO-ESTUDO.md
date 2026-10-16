# Corrigir traduções durante o estudo

Esta entrega permite editar um bloco ou uma seleção de uma tradução Markdown diretamente no modo estudo, por parágrafo ou paralelo. Salva apenas no acervo local, com prévia, confirmação e histórico. O usuário testou, confirmou o funcionamento e autorizou o commit. O assistente não executou testes nem fez push.

## Iniciar

Encerre o backend anterior com Ctrl+C e execute na raiz do projeto:

```bash
python3 -m backend
```

Abra http://localhost:8000/#/doc/showtrials-1666 e recarregue com Ctrl+Shift+R. O recurso depende do backend atualizado; não aparece no GitHub Pages nem com python3 -m http.server.

## Exercício principal, com restauração

1. Expanda o painel e escolha **Modo → Estudo**. Use **Estudo → Paralelo** para comparar russo e português. Se houver três idiomas, escolha as colunas desejadas.
2. Em um bloco português, clique em **Corrigir tradução**, logo abaixo do texto. O original russo não recebe esse controle. No estudo por parágrafo, o controle fica dentro da célula traduzida; se ela estiver recolhida, abra seu idioma primeiro.
3. A janela identifica documento e idioma. O campo contém o Markdown exato daquele bloco. Expanda **Ver trecho atual** para comparar; a prévia abaixo do campo renderiza a nova redação.
4. Acrescente ao fim do bloco `Experimento temporário da correção por trecho.` Confira a prévia. Nada foi gravado ainda.
5. Clique em **Revisar correção**. Confira as diferenças: `-` indica o trecho anterior; `+`, a proposta. **Continuar editando** permite ajustar a redação e exige nova revisão.
6. Clique em **Confirmar e salvar localmente**. Espere a confirmação. O sistema grava a versão traduzida, guarda a versão anterior e atualiza seu cadastro, manifesto e índice de busca. A janela fica aberta até você fechá-la.
7. Feche a janela e confira a correção no estudo. O documento, modo e colunas devem ser mantidos; a posição é recuperada pelo contexto anterior, com aproximação se o conteúdo visível tiver mudado. Confira também a exportação do idioma corrigido e a busca por `Experimento temporário da correção`.
8. Abra o histórico pelo link da janela após salvar ou por **Editar → Editar**, no painel, e **Histórico** na área editorial. Filtre por `showtrials-1666`.
9. A operação deve indicar **Correção de trecho PT**. Na mais recente, escolha **Revisar restauração**, confira e confirme. Recarregue o leitor: o trecho de teste deve desaparecer e a versão anterior voltar. A restauração também atualiza a busca.

Durante esse exercício, RU e EN devem permanecer iguais. A gravação não cria alinhamento automático nem publica no GitHub.

## Editar somente uma seleção

Selecione com mouse ou toque algumas palavras dentro de **uma única célula traduzida** e clique em **Corrigir tradução** nessa célula. Se essa seleção existir uma única vez no Markdown do bloco, a janela carregará apenas ela. Confira a mensagem e o campo antes de editar.

Se a seleção atravessar formatação Markdown, tiver espaços transformados pela renderização ou for ambígua dentro do bloco, não há adivinhação: o bloco inteiro é carregado, com aviso. Você pode corrigir somente as palavras desejadas no campo ou cancelar. Mesmo sem selecionar nada, sempre é possível editar o bloco inteiro.

Os intervalos são relativos à tradução; a posição na coluna russa não determina qual texto será substituído. Textos repetidos em outros blocos não são substituídos em massa.

## Outros caminhos a conferir

- **Cancelar:** altere o campo e feche a janela. Confirme o descarte. O arquivo e a busca devem continuar iguais.
- **Sem alterações:** abra um bloco e clique em Revisar correção sem mudar nada. Deve informar que não há alteração para salvar.
- **Outro idioma:** repita em um bloco inglês, confira a identificação EN e cancele ou restaure após salvar.
- **Conflito:** abra uma correção e salve outra alteração nesse documento pela área editorial em outra aba. Ao tentar revisar/salvar a janela antiga, ela deve recusar a versão desatualizada. Copie sua redação se necessário e reabra o documento. Não sobrescreve alterações concorrentes.
- **Parágrafo/paralelo:** alterne os submodos e confira que os controles continuam funcionando, sem aparecerem duplicados.
- **Mobile/teclado:** o controle deve ser acessível por toque e Tab/Enter. Escape fecha a janela com confirmação quando há alterações. Durante a gravação, o fechamento é bloqueado até a resposta.

## Preservação e limites

O segmentador de estudo mantém agora o início/fim de cada bloco no Markdown original. Mantém a segmentação e a ordem anteriores. A prévia compara o arquivo carregado com o exibido e confere o conteúdo exato do intervalo. O backend repete essa conferência, verifica revisão e hash, protege o original e reaproveita a transação editorial de Markdown e seu histórico recuperável. Cabeçalhos reconhecidos de exportação ficam fora dos intervalos editáveis. As partes fora do intervalo são mantidas, inclusive cabeçalhos e quebras de linha; o campo respeita o padrão CRLF/LF do arquivo ao salvar.

Nesta etapa, correções rápidas aceitam traduções PT/EN já cadastradas como Markdown e uma única célula por vez. Edições TXT não são convertidas implicitamente. Cada correção pode ter até 200 mil bytes e o arquivo final segue o limite de 4 MiB. Mudanças grandes de estrutura devem ser feitas no editor completo e conferidas no modo estudo; não há pareamento automático.

A marcação manual permanece independente da edição. Se você corrigir o próprio parágrafo marcado, sua assinatura muda e talvez seja necessário marcá-lo novamente; não se move a marca para outro parágrafo por aproximação.

O histórico é local, em `.local/editorial/history/`. Desfaça operações da mais recente para a mais antiga quando atingirem os mesmos arquivos do catálogo.

## API

`POST /api/editorial/passages/preview` recebe `revision`, `edition_id`, `content_sha256`, `start`, `end`, `expected` e `replacement`. Os limites do intervalo usam posições Unicode no corpo sem envelope. Retorna diferenças do trecho e um `preview_id`; nada é gravado. A confirmação usa `POST /api/editorial/save`, com os mesmos controles de origem, sessão e concorrência das outras edições.
