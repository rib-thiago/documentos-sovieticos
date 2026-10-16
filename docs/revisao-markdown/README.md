# Revisão estrutural dos textos

## Estado atual: lote integral

Os **2.179 documentos russos** foram convertidos e selecionados no manifesto. São **167.421 blocos preservados**, com **737 títulos em 487 documentos**. As 31 versões revisadas anteriormente mantêm seus títulos. Os 1.692 documentos sem títulos internos confirmados também estão em Markdown, com sinais literais e parágrafos preservados; podem continuar sem índice.

O ponto de partida da revisão agora é [REVISAO-PRIORITARIA.md](REVISAO-PRIORITARIA.md). A triagem inicial registra **50 documentos urgentes, 226 de prioridade alta, 12 média, 1.775 baixa e 116 sem pendências detectadas**. A prioridade é uma indicação automática para conferência, não uma declaração de erro histórico. Tabelas, imagens e links podem já ter perdido estrutura na extração anterior; a igualdade com o TXT não resolve essas perdas.

Arquivos atuais:

- [pendencias.csv](pendencias.csv): uma linha por dificuldade, com prioridade, ação sugerida, trechos, caminhos e links. `status` e `notas_do_revisor` são editáveis e preservados em novas auditorias.
- [acervo-completo.csv](acervo-completo.csv): situação individual dos 2.179 documentos e suas coleções/subcoleções.
- [lote-integral.json](lote-integral.json): totais e distribuição da triagem.
- [diagnosticos.json](diagnosticos.json): evidência e dificuldades detalhadas por documento.
- [markdown-conversions.json](../../data/markdown-conversions.json): receitas, títulos selecionados e hashes dos originais para conferência.

O lote automático usa rótulos documentais explícitos, seções numeradas e nomes de interrogados após marcadores. Células de tabelas, datas, endereçamentos e números de estrofes não são tratados como títulos. Candidatos repetidos, repartidos ou sem correspondência única são mantidos como parágrafos e registrados. As escolhas do lote manual anterior têm precedência; não se aplicam janelas de caracteres da tradução.

Na validação do lote, os 2.179 TXT foram comparados byte a byte à exportação portátil, e os 167.421 blocos foram conferidos contra as versões convertidas. Passaram 18 testes de fidelidade, proteção de revisões e triagem, além de 757 casos no interpretador Markdown incluído no site, cobrindo os 737 títulos e combinações de sinais literais. As URLs com sublinhados escapados foram conferidas também quanto ao destino: o leitor resolve os escapes antes de reconhecer links automaticamente. A navegação visual continua sujeita à conferência no navegador; os testes do interpretador não são testes de navegador.

Para reproduzir ou auditar o lote integral, use o pacote metodológico ou o portátil:

```bash
python3 scripts/convert_showtrials_all.py CAMINHO_DO_PACOTE
python3 scripts/convert_showtrials_all.py CAMINHO_DO_PACOTE --apply
python3 scripts/prepare_markdown.py --check
python3 scripts/check_showtrials.py CAMINHO_DO_PACOTE_PORTATIL
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Sem `--apply`, somente os relatórios são atualizados. Com `--apply`, todos os destinos são conferidos antes de escrever qualquer Markdown ou modificar o manifesto. Uma revisão local divergente interrompe a reaplicação sem sobrescrever o texto. Os comandos antigos `--apply-reviewed` e `--apply-pilot` pertencem à etapa parcial e recusam reaplicação após o lote integral, para não desfazer o acervo convertido.

Para corrigir apenas títulos, edite o `.ru.md` indicado na fila e registre a edição com:

```bash
python3 scripts/convert_showtrials_all.py --accept-headings showtrials-ID
```

O comando aceita somente mudanças dos marcadores `#`–`######`, mantendo o texto e todos os limites dos blocos. Em seguida, anote a correção e o status na planilha. Alterações de conteúdo, tabelas ou segmentação precisam de conferência editorial própria; o verificador estrito deve apontar essas diferenças até que sejam devidamente registradas. Não apague o TXT original.

## Histórico das etapas parciais

Os números e arquivos citados abaixo documentam o piloto e a ampliação anterior. `levantamento.csv`, `resumo.json` e `convertidos.md` são registros daquela etapa de 31 documentos; os arquivos do lote integral acima descrevem o estado atual.

O levantamento cobre os 2.179 documentos importados do ShowTrials. A fonte usada é o campo `content.rendered` dos JSONs WordPress preservados no pacote portátil, não as políticas de segmentação para tradução. As edições editoriais anteriores e os artigos inéditos do site não foram convertidos.

Consulte [levantamento.csv](levantamento.csv) para a situação de cada documento e [resumo.json](resumo.json) para os totais. A presença de um parágrafo centralizado ou numerado é apenas um sinal para revisão: datas, assinaturas, números de página, tabelas e cabeçalhos também usam essa formatação. Nenhum desses sinais autoriza conversão em massa.

## Piloto aprovado

| Documento | Estrutura recuperada | Rota para testar |
| --- | --- | --- |
| Declaração de P. F. Sapozhnikov sobre a atividade da organização dos direitistas | Seções I–VI e subseções 1–2, em dois níveis | `#/doc/showtrials-5855` |
| Georgi Borisovich Sinani-Skalov | Partes I–IX do texto biográfico | `#/doc/showtrials-9470` |
| Sessão de 16 de janeiro de 1935 | Nomes dos interrogados e títulos de interrogatórios de testemunhas | `#/doc/showtrials-2645` |

As divisões selecionadas estão explícitas em parágrafos centralizados no HTML. Na transcrição, “ДОПРОС” (interrogatório) e o nome aparecem em blocos separados; o índice usa o nome, mantendo o bloco anterior em seu lugar. Os nomes não foram traduzidos nem foram criados subtítulos interpretativos.

## Ampliação após o piloto

São **31 documentos, 268 títulos e 8.320 blocos preservados**: os três exemplos aprovados e mais 28 textos. A [lista completa](convertidos.md) oferece nomes em português para revisão, links de teste, estrutura, contagens e observações. Os nomes portugueses do relatório não substituem os títulos russos no site.

O lote recupera seções romanas e árabes, dois e três níveis de hierarquia, nomes de interrogados, títulos de cartas e limites de anexos comprovados no HTML. A seleção explícita está em [markdown-review.json](../../data/markdown-review.json); o conversor não decide títulos pela frequência de palavras nem aplica regras de tradução a documentos não selecionados.

O material metodológico orientou a distinção entre o documento completo, a comunicação de encaminhamento e os anexos. Esse uso segue as diferenças descritas nas análises D2/D3 e no blueprint v1.1. Os limites por quantidade de caracteres, os fragmentos para tradução e as hipóteses de detecção de anexos não foram importados para a apresentação. Cada divisão deste lote foi conferida no HTML; um anexo não se tornou um novo documento nem recebeu outro ID.

As entradas duplicadas de sumários impressos, os destinatários, datas, rótulos de tabelas e números de estrofes não geram títulos automaticamente. Numerações incompletas e grafias da fonte não foram corrigidas nem completadas. Em documentos com protocolos ou títulos repartidos em dois blocos, o índice usa o nome/título descritivo e mantém o marcador anterior em seu lugar.

Seis candidatos foram adiados com motivos individuais: uma tabela financeira, duas cartas sem seções internas suficientes, notas fragmentadas, uma carta com numeração isolada incompleta e uma minuta com numeração alternativa. Os demais TXT continuam como estavam; a ausência de seleção não significa ausência comprovada de subtítulos. Tabelas presentes em documentos convertidos continuam na disposição linear herdada do TXT e precisam de uma revisão própria para recuperar células.

Os `.txt` continuam intactos. Cada `.md` é uma versão adicional, selecionada pelo manifesto apenas para aquele idioma. Não foram recuperados negritos, links, tabelas ou notas a partir do HTML: a conversão acrescenta somente a hierarquia comprovada, escapando os sinais que o interpretador Markdown poderia confundir com formatação. Por exemplo, `<expansões>`, asteriscos e referências `[1]` continuam literais. Quebras internas usam quebras explícitas de Markdown.

São preservados o texto de cada bloco não vazio, sua ordem e seus limites. Espaços externos e blocos vazios são normalizados como o leitor TXT já fazia. A validação remove exclusivamente os marcadores introduzidos e exige igualdade de todos os blocos com o TXT original. Os títulos ocupam seus blocos anteriores, sem inserir parágrafos nem deslocar futuras traduções. Os 31 documentos atualmente só têm versão russa. O modo Estudo conserva os títulos explícitos até o sexto nível, inclusive os subtítulos romanos aninhados; a normalização dos títulos legados de primeiro nível permanece disponível.

As receitas em [markdown-conversions.json](../../data/markdown-conversions.json) registram cada bloco promovido a título, a posição e o texto correspondentes no HTML, a URL e o JSON de origem, além dos hashes do HTML e do TXT. A auditoria reproduz a limpeza histórica e compara todos os blocos dos TXT ao HTML coletado. Divergências ou títulos ambíguos interrompem a conversão. O script não substitui versões Markdown locais que já tenham recebido outras revisões; a reaplicação do piloto não desativa conversões posteriores.

## Reprodução e conferência

```bash
python3 scripts/prepare_markdown.py CAMINHO_DO_PACOTE
python3 scripts/prepare_markdown.py CAMINHO_DO_PACOTE --apply-pilot
python3 scripts/prepare_markdown.py CAMINHO_DO_PACOTE --apply-reviewed
python3 scripts/prepare_markdown.py --check
python3 scripts/check_showtrials.py CAMINHO_DO_PACOTE_PORTATIL
python3 -m unittest discover -s scripts -p test_prepare_markdown.py
```

O primeiro comando gera apenas os relatórios; `--apply-pilot` prepara os três casos iniciais e preserva os demais; `--apply-reviewed` aplica as 31 seleções revisadas. O preparador aceita tanto o pacote portátil anterior quanto a raiz do pacote metodológico, que contém `original/local/posts-json/`. O verificador do acervo completo continua usando o pacote portátil com `catalogos/`. Não é necessário npm nem acesso à internet. A reimportação normal continua conferindo os TXT e preservando as escolhas de idioma do manifesto.

## Conferência visual

Abra as três rotas no servidor local e confira o menu **Índice e marcador**, a hierarquia das seções e os saltos. Verifique também a exportação Markdown e a marcação de um parágrafo antes/depois de navegar para outro texto. A transcrição permite conferir abreviações entre `< >`; a biografia permite conferir separadores com asteriscos sem transformá-los em linhas horizontais.

Para conferir a ampliação, use estes exemplos:

| Documento | Rota | Resultado esperado |
| --- | --- | --- |
| Declaração de Bukharin aos membros do Pleno | `#/doc/showtrials-8690` | Partes com seções e subseções, em três níveis de recuo. |
| Interrogatório de Mayer e anexos | `#/doc/showtrials-5864` | Cinco entradas: o protocolo e quatro anexos. |
| Interrogatório de Bocharov e dois poemas | `#/doc/showtrials-6693` | Três entradas; as estrofes I–IX continuam como conteúdo do poema. |

Depois da revisão deste lote, o próximo passo é ampliar a seleção com base no HTML de cada documento. Textos sem estrutura explícita e artigos inéditos precisam de decisões editoriais próprias. Não é necessário converter todos os TXT para usar o marcador de leitura.
