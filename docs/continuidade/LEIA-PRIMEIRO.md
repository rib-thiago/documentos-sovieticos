> Continuação funcional: as entregas de alinhamento manual, incorporação de transcrições e projeção estática selecionada estão implementadas, aprovadas e registradas em commits, sem push nesta rodada. Consulte [o roteiro conjunto](../projeto/pdf-ocr/ENTREGAS-05-07.md). Preparar/aplicar arquivos públicos localmente não executa Git.

> Atualização de continuidade — 20/10/2026: a interface Carmim, projetos/versões privadas, oficina PDF, OCR rus/eng/por, revisão por página e fac-símiles no estudo já estão implementados. Consulte os roteiros em `docs/projeto/pdf-ocr/`. Os ZIPs antigos e as propostas abaixo são fotografias históricas, não o estado executável atual. Dados de trabalho ficam em `.local/research/`; publicação exige seleção editorial e commit/push separados.

# Como continuar o projeto com pouca troca de contexto

Preparado em 20/10/2026. Esta entrega documenta o estado encontrado e propõe o próximo trabalho; não implementa PDF/OCR nem altera o aplicativo.

## O que fazer agora

1. Leia `OPERACAO.md` para trabalhar com traduções e cadastros que já funcionam.
2. Para conversar com outro assistente, envie `CONTEXTO-PARA-CHAT.md` e diga qual tarefa quer resolver. Ele contém o essencial, sem nosso longo histórico.
3. Se a tarefa exigir código, envie apenas os arquivos indicados em `MAPA-DO-CODIGO.md`. O pacote `codigo-de-referencia.zip` reúne uma fotografia do código atual, caso seja necessário consultar mais arquivos.
4. Para o novo fluxo de PDF, envie também `PDF-POR-PAGINA.md` e escolha um dos pedidos em `PROMPTS.md`. Implemente uma entrega por vez.
5. Guarde uma cópia de segurança antes de aplicar alterações sugeridas. Se o assistente não tiver acesso ao seu computador, ele só conhece os arquivos que você anexar: peça arquivos completos pequenos ou um patch com caminhos explícitos e instruções para aplicar.

Os dois ZIPs estão em `entregas/continuidade-2026-10-20/`. O pacote de contexto inclui o plano e o levantamento anteriores. O pacote de código não é um projeto executável completo: exclui o acervo, capas, dependências de terceiros e dados operacionais. Se o ambiente da conversa não conseguir abrir ZIP, envie os Markdown e os arquivos de código necessários separadamente.

## Economizar sem perder continuidade

Não envie todas as traduções nem todos os materiais de `temporario/`. Comece com o contexto curto, um pedido delimitado, o erro completo e os arquivos relevantes. Para traduções, basta o original e um exemplo aprovado. Para PDF, um arquivo representativo pesquisável e um escaneado são mais úteis que dezenas de PDFs.

Ao concluir cada conversa, peça um registro: o que mudou, arquivos alterados, decisões, o que permanece pendente, como conferir manualmente e o próximo pedido. Atualize o contexto quando uma capacidade deixar de ser proposta e passar a funcionar. Não use a memória da conversa como único registro.

## Fotografia, não sincronização automática

Os ZIPs retratam os arquivos locais em 20/10/2026, incluindo código ainda não commitado. O último commit encontrado foi `923cf0a`; ele sozinho não contém toda a interface oficial atual. O pacote guarda a identificação do commit e o estado Git no momento da geração. Alterações futuras exigem nova cópia dos arquivos relevantes.

Não houve testes, instalações, execução de OCR, commit ou push nesta entrega. Documentos, traduções e URLs foram preservados.
