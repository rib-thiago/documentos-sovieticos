> Atualização de continuidade — 20/10/2026: a interface Carmim, projetos/versões privadas, oficina PDF, OCR rus/eng/por, revisão por página e fac-símiles no estudo já estão implementados. Consulte os roteiros em `docs/projeto/pdf-ocr/`. Os ZIPs antigos e as propostas abaixo são fotografias históricas, não o estado executável atual. Dados de trabalho ficam em `.local/research/`; publicação exige seleção editorial e commit/push separados.

# Pedidos prontos para continuar

Envie o contexto curto em toda conversa nova. Acrescente apenas o material indicado para a tarefa. Substitua os campos entre colchetes.

## Traduzir, sem programar

> Traduza integralmente o Markdown anexado de russo para [português/inglês], no padrão do exemplo aprovado. Preserve títulos, fronteiras de parágrafos, notas, tabelas, links e IDs. Não resuma nem acrescente comentários dentro da fonte. Mantenha o ID do documento e indique corretamente o idioma da versão no cabeçalho, sem duplicá-lo. Entregue o arquivo UTF-8 [ID.pt.md/ID.en.md]. Liste dúvidas de leitura e decisões de nomes separadamente. Eu importarei pela área editorial existente; não altere o catálogo nem faça publicação.

Enviar: original + um exemplo de tradução aprovada. Importar conforme `OPERACAO.md`.

## Corrigir um problema de interface

> No projeto descrito no contexto, corrija [problema]. Para reproduzir: [passos]. Resultado atual: [descrição/erro]. Esperado: [descrição]. Preserve a interface Carmim e os recursos existentes. Leia os arquivos anexados; peça arquivos adicionais específicos se faltar contexto. Entregue um patch delimitado com caminhos e instruções para aplicar, além da validação manual e como reverter. Não execute testes, não faça commit nem push.

Enviar: arquivos do mapa correspondentes + erro completo ou captura quando útil. Não enviar todo o acervo.

## Organizar o backend

> Extraia de [módulo] a responsabilidade [uma responsabilidade específica], mantendo contratos da API e comportamento atual. Preserve prévia, confirmação, revisão-base, histórico, restauração e atualização de catálogo/manifesto/busca. Não migre framework nem reescreva o restante do backend. Primeiro indique as dependências encontradas; depois entregue a mudança e roteiro manual. Não execute testes nem faça commit/push.

Enviar: backend pertinente e frontend que chama os endpoints. Evitar “organize todo o backend” numa única entrega.

## Incorporar coleção

> Prepare a incorporação da coleção [nome] e subcoleções [nomes ou nenhuma], usando as fontes anexadas. Primeiro inventarie documentos, idiomas, datas, proveniência, fronteiras, notas/tabelas e possíveis duplicatas, distinguindo identidade comprovada de semelhança. Preserve IDs e URLs existentes e não duplique documentos por idioma. Gere prévia do cadastro e pendências por documento. Use o fluxo editorial atual; se houver mudança de código, explique por quê. Não grave sobre o acervo sem uma prévia concreta, não execute testes nem faça commit/push.

Enviar: inventário/fontes selecionadas + catálogo relacionado quando houver risco de duplicação. Se o chat não acessa seu computador, peça arquivos de importação e instruções para uso local; não aceite uma afirmação de que ele já salvou no projeto.

## PDF — P1, a próxima implementação recomendada

> Implemente apenas P1 de PDF-POR-PAGINA.md: recepção local de PDF com coleção obrigatória e subcoleção opcional, existente ou nova; proveniência, preservação do original/hash, inventário de páginas e persistência durável de processamento/revisão. Integre a entrada à área editorial Carmim. Não implemente OCR nesta entrega. Preserve cadastro Markdown/TXT, acervo, URLs e histórico. Declare dependências opcionais e backup; não execute testes, não faça commit/push. Explique o que eu já consigo usar e o que ainda depende de P2.

Enviar: contexto + especificação PDF + plano de ferramentas + backend e interface editorial atuais. P1 não entrega sozinha a oficina completa.

## PDF — P2, depois de conferir P1

> Com P1 já integrada e os arquivos atualizados anexados, implemente P2: extração por página para PDF pesquisável, bancada com fac-símile e texto editável, rascunhos duráveis, estados e retomada. Permita montar e conferir um documento, aplicar com prévia/histórico e atualizar catálogo, manifesto e busca. Preserve o texto bruto e não sobrescreva correções ao reprocessar. Não faça OCR ainda. Não execute testes nem faça commit/push; entregue roteiro manual com PDF de exemplo.

## PDF — P3, depois de conferir P2

> Implemente P3 sobre o código atualizado: diagnóstico por página para PDF pesquisável/escaneado/misto, OCR opcional de texto impresso em russo, escolha manual e reprocessamento com diferenças. Jobs devem poder interromper/retomar, preservar correções e não bloquear o leitor. Exponha erros e dependências ausentes com clareza. Não prometa manuscritos. Preserve o fluxo P1/P2. Não execute testes nem faça commit/push; explique a conferência manual.

## PDF — P4 e publicação

> Complete P4: seleção de intervalos e múltiplos documentos por fonte, notas/tabelas e continuidade entre páginas, referências estáveis e visualização pública de fac-símile + transcrição selecionados. Preserve URLs e histórico. Separe revisão, aprovação local e publicação; não implemente publicação automática. Não execute testes nem faça commit/push. Explique como conferir no localhost e quais arquivos seriam necessários numa publicação futura.

## Encerrar qualquer conversa

> Atualize o registro de continuidade: arquivos alterados, capacidades concluídas, decisões, pendências, recuperação e roteiro manual. Escreva o próximo pedido já pronto e liste exatamente quais arquivos atualizados devo anexar. Não afirme que executou algo que não executou.
