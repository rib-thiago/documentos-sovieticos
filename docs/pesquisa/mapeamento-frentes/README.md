# Mapeamento para coleções temáticas

## O que está disponível

O diretório temporário traz três pacotes de planejamento e aquisição: inventários CSV/JSON, fichas em Markdown, bibliografia, perguntas de pesquisa e programas Python. Esses arquivos podem ser lidos e aproveitados agora. Os espaços `dados/originais` e `dados/revisao` do kit Litvinov contêm somente arquivos de marcação `.gitkeep`; o kit militar tampouco traz o corpus coletado em `data/raw` ou `data/review`.

Assim, uma referência nova no inventário não equivale a uma transcrição nova já baixada. A análise anterior consultou algumas páginas externas, mas não transferiu um corpus documental para esses diretórios. Este mapeamento não executou os coletores nem fez novas consultas externas.

## Resultados

| Frente | Entradas | Mesmo documento cadastrado por URL de origem | Seção candidata na compilação existente | Compilação relacionada | Sem correspondência identificada |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ezhov | 26 | 0 | 23 | 0 | 3 |
| Militar | 36 | 3 | 1 | 0 | 32 |
| Litvinov/NKID | 31 | 0 | 12 | 1 | 18 |
| Total de entradas | 93 | 3 | 36 | 1 | 53 |

As linhas se sobrepõem entre inventários. Os números não representam 93 documentos independentes nem 53 documentos novos confirmados. Uma única seção da compilação aparece em várias linhas, e diferentes documentos podem estar publicados na mesma URL.

### Coleção temática 1: Ezhov — investigação e julgamento, 1939–1940

Proposta de organização, ainda não criada no site:

- Declarações e interrogatórios.
- Acareações.
- Encerramento da investigação e julgamento.
- Edições, fragmentos e referências complementares.

As 23 correspondências são seções da compilação `confessionezhov`, que já tem RU/PT/EN. Não são 23 documentos individuais já cadastrados. O CSV contém o título e a linha da seção em cada idioma. As correspondências RU/EN usam a posição editorial do título correspondente ao português; não houve conferência integral dos textos e das fronteiras de cada peça.

Três registros não tiveram seção própria identificada:

| Registro | Data do inventário | Situação | Próximo trabalho |
| --- | --- | --- | --- |
| EZH-014 | 07/07/1939 | Extrato publicado indicado no inventário | Obter a publicação, registrar extensão e cotejar antes de cadastrar |
| EZH-016 | 17/07/1939 | Referência indireta; texto não localizado no levantamento | Criar ficha de referência, sem inventar uma transcrição |
| EZH-024 | 31/01/1940 | Interrogatório referido; texto não localizado no levantamento | Registrar a referência e procurar a publicação identificável |

Ausência de seção própria não significa ausência de menções no corpo da compilação. O mapeamento não fez busca exaustiva de citações internas.

Antes de separar arquivos, cotejar particularmente EZH-002 (declaração versus título de interrogatório), EZH-013/015/019/020 (datas nos títulos russos), EZH-025 (01/02 versus 02.01) e EZH-021 (mais de uma edição/extrato). Não alterar as traduções existentes apenas para acompanhar um título de inventário.

### Coleção temática 2: Exército e indústria de defesa soviéticos

Proposta de subcoleções: Conselho Militar de 1935; Conselho Militar e reuniões do NKO de 1937; indústria de defesa; investigações e processo militar. A distribuição das 36 entradas acompanha o inventário: 13, oito, sete e oito, respectivamente.

Já cadastrados individualmente, com correspondência da URL de origem:

| ID do inventário | ID preservado no site | Documento |
| --- | --- | --- |
| taits-1936-09-01 | showtrials-5810 | Interrogatório de D. A. Taits |
| lurie-moisey-interrogation | showtrials-5711 | Interrogatório de M. I. Lurie |
| lipshits-interrogation | showtrials-5690 | Interrogatório de P. A. Lipshits |

O interrogatório Ezhov de 26/04/1939 tem seção candidata na compilação. As 32 demais entradas não tiveram correspondência pelos critérios deste mapa. São uma fila de investigação/coleta, não uma garantia de ineditismo no conjunto de textos ou referências do site.

Prioridade sugerida: relatório Kuibyshev–Berezin de 21/11/1935, expediente Yagoda–Taits de 04/09/1936 e cotejo de Ezhov de 26/04. Depois, avançar por sessão militar ou eixo industrial. O expediente e seu anexo podem exigir duas identidades documentais relacionadas; não resolver isso apenas pelo nome do PDF.

### Coleção temática 3: Ezhov, Litvinov e as acusações no NKID

Proposta de subcoleções: Ezhov e Merano; correspondência e atuação diplomática; Koltsov/Gnedin/Girshfeld; revisões posteriores e memórias. A fila geral dos 26 registros de Ezhov pertence à base compartilhada da primeira coleção, sem nova cópia.

As 12 seções candidatas incluem republicações e referências ao mesmo conteúdo de Ezhov. Por exemplo, MER-001, MER-002, MER-003 e EZH-003 remetem ao conjunto de abril de 1939, embora representem publicações ou suportes diferentes. EZH-021B aponta para um extrato de 2018: a seção local sobre 04/08 é relacionada, mas não substitui obter e conferir esse extrato.

As 18 entradas sem correspondência abrangem os sete itens LIT, os três KOL, os três GNE, GIR-001, os dois RUD, EZH-014 e OPC-001. Há livros, índices e referências; não são 18 transcrições prontas para importação.

O primeiro núcleo documental recomendado é Ezhov 26/04 e os fragmentos de 29/06 e 02/07 já relacionados à compilação, acrescidos dos trechos localizados de Koltsov/Gnedin e da revisão de Rudenko. Correspondências e itinerários podem ser incorporados progressivamente.

## Como usar os arquivos

- `mapeamento.csv`: planilha geral das 93 entradas, em UTF-8 com BOM, para abrir em planilha.
- `ezhov.csv`, `militar.csv`, `litvinov.csv`: recortes por frente.
- `mapeamento.json`: os mesmos dados em formato estruturado.
- `recursos-compartilhados.csv`: URLs que aparecem em mais de uma entrada, para organizar aquisição sem confundir recurso com identidade documental.
- `resumo.json`: contagens por critério de correspondência.

Os campos `documentos_site`, `arquivos_locais` e `colecoes_atuais` identificam o que pode ser reutilizado. `linha_pt`, `linha_ru` e `linha_en` localizam títulos nos arquivos atuais; edições futuras podem mudar esses números. `acao_proposta` e `notas` indicam a próxima tarefa. Datas, classes e integridade dos inventários foram preservadas como informações do levantamento, sem validação automática ou correção silenciosa.

O programa `scripts/map_research_fronts.py` reproduz esses arquivos. Ele lê o catálogo e os inventários; escreve apenas nesta pasta. A execução realizada foi geração do mapa solicitado, sem testes ou coleta. CSV/JSON gerados são relatórios de pesquisa, não arquivos importáveis diretamente pelo cadastro do site.

## Próxima entrega para tornar as coleções navegáveis

1. Criar as três coleções e suas subcoleções sem alterar as coleções de origem.
2. Associar os três documentos ShowTrials usando os IDs existentes.
3. Escolher a representação dos trechos de Ezhov: primeiro, links explícitos às seções da compilação; depois, documentos derivados revisados, com proveniência e relação com a compilação. Não duplicar silenciosamente todo o texto em cada tema.
4. Manter as fichas sem texto separadas dos documentos disponíveis. Para que elas participem plenamente do catálogo e do leitor, implementar essa representação: o cadastro atual pressupõe uma edição textual.
5. Adquirir e revisar as fontes faltantes em uma área de trabalho; publicar apenas os registros e conteúdos selecionados.

Links para seções são viáveis como conteúdo editorial, mas documentos individuais requerem delimitação do texto. A data temática e a correspondência por título não bastam para esse recorte. As URLs e traduções atuais devem ser mantidas.

Nenhuma coleção, texto, tradução, manifesto ou catálogo do site foi modificado neste mapeamento. Não houve commit ou push desta entrega.
