# Traduções — Andamento do processo do Centro de Leningrado

**Concluído localmente:** os três documentos têm português e inglês, com seis novas versões cadastradas. Catálogo, manifesto e busca atualizados; histórico recuperável `20261018125441670303-e56cfded3265`. Os seis diagnósticos mantêm a contagem de blocos dos originais e a sequência dos marcadores de notas.

## Escopo

Seis novas versões, em português e inglês, dos três documentos existentes:

| ID | Português | Inglês |
| --- | --- | --- |
| showtrials-2617 | Peça de acusação | Indictment |
| showtrials-2618 | Sessão de 28 de dezembro de 1934 | Hearing of December 28, 1934 |
| showtrials-2619 | Sentença | Judgment |

Tradução direta do russo, mantendo os originais, as URLs, a ordem da subcoleção e os cadastros existentes. Não foram utilizados serviços externos de tradução. O 2618 foi dividido em três partes de trabalho apenas para permitir a tradução paralela; a edição final de cada idioma é reunida em **um único arquivo**, sem marcadores de parte ou resumos. Não se alterou a divisão documental do site.

## Registros

- [Escopo e hashes dos originais](escopo.json).
- [Fronteiras e contagens das partes da sessão](partes.json).
- [Marcadores das notas, na ordem documental](marcadores-notas.json).
- [Progresso e diagnóstico estrutural](progresso.csv).
- [Registro detalhado das seis versões](progresso.json).
- [Gravação e histórico recuperável](gravacao.json), após concluir a integração local.
- [Notas da acusação e da sentença](notas-2617-2619.md).
- [Notas da sessão, parte 1](notas-2618-parte-1.md).
- [Notas da sessão, parte 2](notas-2618-parte-2.md).
- [Notas da sessão, parte 3](notas-2618-parte-3.md).
- [Notas do trecho final da parte 2](notas-2618-parte-2-final.md), redistribuído ao primeiro tradutor disponível para acelerar a conclusão.

As contagens descrevem a estrutura e a sequência de referências, não certificam equivalência linguística. Os diálogos foram traduzidos integralmente, incluindo repetições, respostas negativas, falas longas, qualificações, assinaturas, referências e notas da edição. Lacunas e contradições foram mantidas; as dúvidas são registradas separadamente. As versões novas não recebem automaticamente uma marca de revisão humana concluída.

As alegações de culpa ou de atuação de organizações são as dos documentos e não conclusões novas dos tradutores. Expansões editoriais de abreviaturas russas são traduzidas como palavras completas. Não há cabeçalhos de exportação inseridos no corpo: o leitor continua a gerá-los quando o usuário baixa o arquivo.

## Pontos prioritários

Na acusação, preservados o artigo **53-8** na imputação coletiva (divergente das demais menções a 58-8), as iniciais discordantes dos réus e as lacunas do texto jornalístico. As quatro notas que fornecem informações da versão datilografada não foram incorporadas silenciosamente ao corpo. A sentença conserva a declaração de ausência de acusação e defesa na sessão judicial, as idades e a determinação de execução imediata. Seu ano bibliográfico **1917** foi mantido, com ressalva separada.

As notas de cada parte da sessão detalham grafias, datas, frases truncadas e outras anomalias preservadas. A sessão tem 75 notas numeradas e uma nota de letra i, incluindo referências a fontes e comentários da edição; não se suprimiram essas observações para abreviar a tradução.

## Como conferir

1. Inicie o backend com `python3 -m backend` e recarregue o site.
2. Abra `http://localhost:8000/#/colecao/centro-de-leningrado/subcolecao/andamento`.
3. Selecione português ou inglês no leitor. Para cotejar, use o estudo paralelo com russo na coluna esquerda e a tradução na direita.
4. Confira os três documentos, especialmente as listas dos réus, as notas ao fim dos textos e a continuidade da sessão extensa. A passagem entre as partes internas de trabalho não deve aparecer como mudança de documento.
5. Para correções, use o editor local ou a edição de tradução por trecho já existente. As seis novas versões pertencem a uma única operação recuperável no histórico editorial.

A integração atualiza catálogo, manifesto e índice de busca apenas no acervo local. Não foi implementada publicação automática. Nenhum teste, commit ou push foi executado nesta entrega.

O comando de produção `python3 scripts/import_leningrad_proceedings_translations.py --apply` reúne e cadastra somente versões completas. Recusa partes com contagens incompletas, divergências de marcadores de notas, alterações posteriores nos originais ou destinos já existentes. Após a gravação, use a área editorial para corrigir versões; não repita a importação para sobrescrever arquivos.
