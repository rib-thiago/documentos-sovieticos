# Svitlana — duas páginas compostas, rodada 4

Conferência de 21/10/2026 sobre os HTMLs locais e seus candidatos Markdown integrais. As decisões são vinculadas aos hashes de ambas as representações em `scripts/coletores/svitlana/decisions_compounds_round4.json`. Não houve importação canônica, testes, commit ou push neste trabalho.

## Carta de Ezhov e telegrama de Uspensky

Candidato `svitlana-4898e43af1b5adac`; HTML `8968269d09c219513932e142d7e6b8649d1381ff0b21ccfcc288b8b05a52cecf`; Markdown `92d3dbf94c99ab6940bcc6610a95e0f2104f48b4932da074c405fe0ba5991bcb`.

Duas unidades estruturalmente prontas:

1. Carta de encaminhamento nº 102983, de 15/04/1938: título, cota, data, classificação, destinatário, dois parágrafos e assinatura Ezhov. A assinatura encerra esta unidade.
2. Telegrama nº 926 de Uspensky: começa em “In accordance with your instructions”, termina na assinatura “USPENSKY”, seguido das notas [1] e [2]. Seu número é identificado na carta; **não há data própria**. O título desta unidade é editorial, não um cabeçalho descoberto no anexo.

A cota `AP RF. F. 3. Op. 58. D. 255. L. 24-41. Script. Typescript.` descreve o conjunto da página. Ela acompanha as duas unidades como referência compartilhada; não foram inventados fólios específicos. Apenas o anexo recebe as notas: [1] explica POV/POW e [2] reproduz a autorização manuscrita de Stalin, chamada no pedido de prisão. “On the first page” permanece literal; a individualização não pretende localizar fisicamente a anotação dentro dos fólios.

O anexo já contém `( .. )` sem os espaços, isto é, `(..)`: trata-se de um extrato na própria fonte. A nota [2] termina sem fechar as aspas no HTML e no Markdown; mantivemos a falta. “Owls. secret”, nomes inconsistentes e a redação inglesa também permanecem literais. Prontidão estrutural não significa tradução revisada nem comprovação das acusações.

## Paz preliminar e armistício de 1920

Candidato `svitlana-c5ed6f188cc197d3`; HTML `96914c0863402929ed1f2a746a8a264e84456f9ecf9f66ac157dc014524b67cb`; Markdown `be235fe06b16fd9c7290d309e4ae2e95109167964007e66acae754ed7e67ff66`.

Três unidades estruturalmente prontas:

1. Tratado preliminar assinado em Riga em **12/10/1920**: apresentação editorial/publicação Art. 516, preâmbulo, artigos I–XVII e primeira série de assinaturas, encerrada por Mikhail Vikhlinsky.
2. **Anexo nº 2**, acordo de armistício, também de **12/10/1920**: cabeçalhos próprios, §§ 1–13, fecho e segunda série de assinaturas. A vigência da cessação das hostilidades em 18/10 não foi confundida com assinatura.
3. Instrumento de ratificação, **Moscou, 23/10/1920**: início “After considering this treaty”, assinaturas Lutovinov/Yenukidze e informação final da troca dos instrumentos em Libau em **02/11/1920**. O título foi fornecido editorialmente. Essa informação final acompanha a ratificação; não virou quarto documento nem data de assinatura.

A referência à edição de 1943, pp. 755–763, é compartilhada pelas três peças. A menção ao **Anexo nº 1/mapa** é preservada, mas o mapa não está na página: não se declarou completude dos anexos. A tradução conserva “Polynia”, “Article XV I.”, topônimos/nomes variantes e “True Treaty”; nenhum foi corrigido silenciosamente. A página não fornece notas numeradas externas além do aparato integrado e das referências aos anexos.

## Receita e cobertura

`ranges` usa posições de caracteres Unicode, com início incluído e fim excluído, no Markdown original vinculado por hash. Cada faixa recebe `strip`, é unida às demais por duas quebras e recebe uma quebra final. Depois se removem apenas os prefixos de blockquote usados como layout da página e os excessos de linhas vazias; o hash final esperado está em cada unidade.

`shared_ranges` declara as únicas sobreposições: cota comum para Ezhov/Uspensky e referência bibliográfica para as três peças de 1920. `ignored_ranges` contém apenas o breadcrumb “Other Transcripts not in the books” da segunda página. Todo o conteúdo documental restante foi atribuído; as fontes compostas originais permanecem intactas. A documentação e os títulos editoriais distinguem as unidades, sem criar títulos falsamente atribuídos à fonte.

Para conferir manualmente, abrir cada HTML e os Markdown candidatos indicados no inventário; localizar as duas assinaturas de 1938 e as duas séries de assinaturas de 1920, além do fecho de ratificação. Confirmar que nenhuma nota de Uspensky migrou à carta e que a data desconhecida do telegrama continua vazia.
