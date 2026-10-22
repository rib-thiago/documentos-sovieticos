# Svitlana/Erdogan — descoberta completa das sementes e lote ampliado

Data: 20/10/2026. Esta etapa mantém o catálogo público intocado. Os arquivos de
trabalho estão em `temporario/coletas-quatro/svitlana/`; código e sementes em
`scripts/coletores/svitlana/`.

## Contagens verificadas

|Objeto|Quantidade|Alcance|
|---|---:|---|
|Índices das sementes recuperados|35 de 35|Não significa que todas as referências tenham texto disponível.|
|URLs candidatas únicas|779|Links HTML internos nos diretórios das fontes; ainda sujeitos à revisão de tipo e identidade.|
|Ocorrências nos agrupamentos|792|Uma URL pode aparecer em mais de uma série.|
|Páginas novas obtidas nesta etapa|60|Três timeouts iniciais foram repetidos e resolvidos.|
|Páginas obtidas, incluindo o piloto|67|66 candidatas de texto e uma página que apenas incorpora um PDF.|
|Snapshots HTML preservados|102|35 índices e 67 páginas.|
|Links do Volume I obtidos|11 de 11|São páginas da fonte; nem todas constituem um único documento histórico.|
|URLs candidatas ainda sem coleta de página|712|Inventariadas, não adquiridas nem tratadas como documentos prontos.|
|Unidades emitidas em `units.json`|68|Uma página foi separada em duas unidades; inclui referências e itens bloqueados.|
|Unidades estruturalmente prontas|10|Aptas à prévia e conciliação central, com traduções ainda de trabalho.|
|Unidades retidas|58|Fronteiras não conferidas, página composta, variante duplicada ou referência sem texto.|

O lote começou pelo restante do Volume I e alternou depois as séries Stalin,
To Stalin e Other Transcripts. Não houve aquisição das 779 URLs nem de todos os
documentos citados nos livros. Índices como Education e Seventh Emergency Congress
não produziram links internos no filtro conservador; suas fontes e referências
externas continuam preservadas. Não foram classificados como coleções vazias.

## Unidades conferidas

As dez unidades prontas são:

1. Relatório sobre a organização social-democrata de Tiflis, aprovado em 9 de julho de 1903.
2. Nota de Stalin sobre o caso do clero de Moscou, documento 24-7, com a data literal da fonte entre colchetes.
3. Nota de Stalin de 2 de maio de 1922, documento 24-1.
4. Circular religiosa de 16 de agosto de 1923, cujo nome da URL contém 1922.
5. Comunicação sobre o levante na Geórgia, de 2 de setembro de 1924.
6. Sessão do Politburo de 26 de outubro de 1925, com as notas finais até o número 34.
7. Carta de Ezhov a Stalin de 2 de fevereiro de 1937, com a resolução em nota; os protocolos mencionados não estão incluídos na página.
8. Decreto de transferência do centro da província de Donetsk para Bakhmut, de 25 de novembro de 1920; publicação de 28 de novembro preservada separadamente no texto.
9. Conversa telefônica de Stalin e Ostrovityanov, de 7 de fevereiro de 1952.
10. Carta de Uspensky sobre as oficinas de reparação de Kirov e Kherson, de 29 de janeiro de 1938.

Prontidão significa conferência da unidade textual, título/data no corpo,
referências, começo e fim e alcance das notas. Não é revisão filológica da
tradução inglesa. A inconsistência de nomes e outros problemas da tradução de
origem permanecem no texto de trabalho; não foram corrigidos silenciosamente.
Autoria documental e tradutor individual não são preenchidos por inferência a
partir dos organizadores da série.

As duas notas de maio de 1922 foram separadas no divisor editorial existente:
o documento 24-7 conserva as referências às folhas 9 e 8; o documento 24-1 conserva
as referências às folhas 2 e 3 e sua nota final. A versão integral da página
permanece disponível. Nas quatro cartas curtas conferidas, a indentação em
blockquote usada como layout foi removida apenas da unidade derivada, preservando
parágrafos, palavras, notas e os arquivos anteriores.

## Bloqueios explícitos

- Outra página, `Stalin/From Soviet Archives/Report 1903.htm`, repete a peça de
Tiflis com a mesma cota RGIA e o mesmo começo e fim. Ficou retida como variante
de fonte: não gerar um segundo documento; comparar as variantes antes de agregar
proveniência à unidade principal.
- Carta Ezhov/Uspensky de abril de 1938: página composta, com encaminhamento e
telegrama, cuja individualização ainda está bloqueada.
- Acordo preliminar com a Polônia de 1920: página composta com ratificação e nota
de troca de instrumentos; fronteiras ainda pendentes.
- `To Stalin top secret.htm` contém apenas um incorporador de PDF e um link de
download. É referência, não texto histórico extraído; o PDF não foi adquirido
nesta etapa.
- Páginas longas e tabelas complexas não conferidas continuam na área de trabalho.
Nenhuma foi aprovada apenas porque o download ou a conversão terminou.
- A fonte russa `istmat.org/node/27376` continua mapeada ao documento existente
`tukhachevsky-nko37-01-pm`; nenhuma equivalência inglesa foi presumida. Comparações
adicionais com o corpus militar e Mozokhin pertencem à conciliação central.

## Contrato dos arquivos

`inventory.json` conserva todas as tentativas, referências descobertas e ocorrências
nas séries. Erros não substituem o último sucesso. Os três timeouts desta rodada
continuam no histórico mesmo após a recuperação.

`units.json` contém identidade estável, título e data literais, idioma, fonte,
caminhos relativos para HTML e Markdown, hashes, ocorrências, proveniência,
prontidão e motivo, pendências e evidência das fronteiras. As datas de coleta e
reconversão são distintas. `unit_decisions.json` vincula cada decisão de revisão
ao hash da versão conferida; uma alteração de fonte suspende essa prontidão.

Nenhum arquivo canônico foi alterado. Uma unidade pronta ainda deve passar pela
prévia e pela conciliação de duplicatas antes da eventual incorporação.

## Reproduzir e conferir

```sh
python3 scripts/coletores/svitlana/collect.py --indexes --sources all
python3 scripts/coletores/svitlana/collect.py --documents --sources VOL-01,TEMA-STALIN,TEMA-TO-STALIN,TEMA-OTHER --limit 60 --balanced
python3 scripts/coletores/svitlana/collect.py --reconvert
python3 scripts/coletores/svitlana/build_units.py
python3 -m unittest discover -s scripts/coletores/svitlana -p 'test_*.py' -v
```

O segundo comando, repetido, seleciona páginas ainda não coletadas; portanto pode
ampliar o acervo de trabalho. Para apenas reconstruir as unidades já existentes,
usar os comandos de reconversão e `build_units.py`, sem acesso à rede.

Validação desta etapa: cinco testes offline aprovados, incluindo separação de
documentos/notas e suspensão de aprovação após mudança do hash. Os caminhos e
hashes de HTML e Markdown de todas as 68 unidades foram conferidos. A coleta
remota efetiva é a descrita na tabela; não se inferiu a integridade dos livros
impressos a partir dela.
