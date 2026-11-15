# Biblioteca + Mesa

Piloto separado da interface oficial: `/prototipo/mesa/`.

Inicie `python3 -m backend` na raiz. Reinicie um backend que já estava aberto para carregar novas permissões de módulos.

Manual, limites e validação: [docs/interface/PILOTO-BIBLIOTECA-MESA.md](../../docs/interface/PILOTO-BIBLIOTECA-MESA.md).

Rascunhos usam sessionStorage. Com backend local, Markdown, tradução individual, metadados e coleções/subcoleções oferecem gravação real com prévia, confirmação e histórico.

Fontes PDF usa cadastro local, extração nativa, OCR, candidatos, revisão e incorporação ao acervo com proveniência. Cadastrar uma fonte ou salvar uma página não publica documento. Criar documento da revisão é outra confirmação. Projetos locais têm organização e materiais, abas contextuais, leitura/edição/importação de versões privadas, histórico próprio e incorporação explícita ao acervo. Revisões de fontes PDF continuam compartilhadas; a interface não as apresenta como cópias privadas por projeto. Vínculos de PDFs a documentos existentes e preparação estática selecionada de fac-símiles também estão disponíveis no piloto, com confirmação e históricos próprios. Não há publicação automática.

Importação de corpus é guiada por contexto e associação de arquivos, sem exigir CSV. O backend oferece prévia, cadastro real, busca atualizada e histórico/reversão do lote. IDs existentes não são sobrescritos; traduções existentes continuam no fluxo do documento. PDF temporário no navegador é distinto de Fonte PDF cadastrada no backend.

Preparação de fontes: extração/divisão com prévia e derivados rastreáveis; tratamento de imagem com comparação Original/Tratada, PNG e receita baixáveis. O OCR pode aplicar explicitamente a mesma receita. Originais e transcrições conferidas são preservados. BookReader permanece na interface anterior e não é dependência do piloto.

Fila de revisão: ☰ → Organizar acervo → Fila de revisão. Filtros, seleção de casos, situação/prioridade/diagnóstico/notas com prévia e histórico. Disponível também no menu do documento. Registrar a avaliação não altera seu texto.

Correção por trecho: selecionar uma frase numa tradução → Corrigir tradução. Editor com prévia e confirmação no contexto da aba (acervo ou projeto). Intervalos são mapeados ao Markdown; quando a seleção não é exata, o bloco completo é apresentado explicitamente. Rascunhos podem ser retomados; original e outras versões são preservados.

Biblioteca: busca por catálogo ou conteúdo (esta última requer backend), idiomas, coleção/subcoleção, resultados com contexto e paginação. ZIP de coleção/subcoleção exporta todas as versões canônicas e metadados, sem PDFs nem versões privadas; inclui progresso/cancelamento.

Entrada pública: galeria de capas, coleção contextual e busca acionada no cabeçalho; números do acervo no rodapé. A marca volta à entrada; Biblioteca conserva a navegação anterior. Ferramentas locais estão agrupadas em Organizar acervo. Registros de incorporação usam o histórico público existente, sem confundir coleta/data histórica com publicação.

Paridade v29: seleção de trecho → associação a página/unidade, delimitação manual de regiões com divisão/união de unidades, consulta com aviso de associação desatualizada, upload/derivados vinculados ao projeto real e impressão do idioma atual. Revisão OCR da fonte permanece compartilhada; vínculos privados não são preparados para o portal. Consulte o final do manual para o roteiro de conferência.

v38: associações locais podem ser editadas/reconfirmadas pela própria lista. Editar regiões no PDF leva à página/unidade e oferece Voltar à associação na fonte, conservando abas e contexto. Texto alterado exige seleção atual explícita; unidades removidas não são substituídas automaticamente.
