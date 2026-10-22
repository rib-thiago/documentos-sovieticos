# Incorporação local das quatro coleções

**Concluída.** Histórico: `20261021023427428117-c65dfd4f5642`.
O acervo ativo passou a 2.603 documentos, 3.722 versões, 19 coleções principais
e 55 subcoleções. Catálogo, manifesto, fila e busca foram gravados pela transação
editorial, com cópia recuperável do estado anterior.

## Lote autorizado

Prévia aprovada: `dc315c525f8c48bb6f3d203c71f3215f30153faeee683c598cf32f7574360449`.
O comprovante da gravação fica em [gravacao.json](gravacao.json), com identificador
do histórico, contagens, revisão e caminho da cópia recuperável.

O lote contém 362 documentos, 363 versões por idioma, quatro coleções principais
e vinte subcoleções. O histórico é uma operação conjunta: a restauração envolve
o lote inteiro, mantendo seus registros anteriores e posteriores.

| Coleção | Documentos | Versões |
|---|---:|---:|
| Sakharov — testamento político de Lenin | 72 | 72 |
| Transcrições dos arquivos soviéticos — Svitlana/Erdogan | 10 | 10 |
| Politburo e Lev Trotsky — Mozokhin | 239 | 239 |
| Brest-Litovsk | 41 | 42 |
| Total | 362 | 363 |

## Preservação e gravação

`scripts/coletores/incorporate.py` utiliza `Editorial.store_preview` e
`Editorial.save`, o mesmo mecanismo de transação e recuperação do backend.
O comando verifica o conteúdo do pacote aprovado pelo SHA-256 e recusa mudanças
de base, substituições de registros existentes ou arquivos de destino já presentes.

Os textos novos são copiados para `originais/coletores/<frente>/`. As edições e
os arquivos anteriores não são regravados. Catálogo canônico, manifesto, fila de
revisão e índice SQLite ativo são atualizados no fluxo editorial. O histórico
guarda o estado anterior e posterior antes da escrita dos arquivos públicos.

As 362 entradas de revisão dos documentos incluídos usam
`problema=coleta_quatro_colecoes`, preservando a fila anterior. São revisões
editoriais de trabalho; inclusão no catálogo não equivale a revisão crítica
integral ou validação das alegações históricas de cada fonte.

As fontes brutas, compilações, extrações, versões anteriores e candidatos retidos
continuam em `temporario/coletas-quatro/`. Nenhum bloqueio foi removido para
aumentar artificialmente o lote.

## Acesso depois da gravação

Na raiz do projeto:

```bash
python3 -m backend
```

Usar o site normal na porta 8000:

- [Sakharov](http://127.0.0.1:8000/#/colecao/sakharov-testamento-lenin-2003)
- [Svitlana/Erdogan](http://127.0.0.1:8000/#/colecao/transcricoes-arquivos-sovieticos)
- [Mozokhin](http://127.0.0.1:8000/#/colecao/politburo-trotsky-mozokhin)
- [Brest-Litovsk](http://127.0.0.1:8000/#/colecao/brest-litovsk)

Nesse ambiente, os controles editoriais normais podem ser usados nos documentos
incorporados. O servidor de prévia da porta 8001 é histórico e pode recusar a
abertura por ter sido preparado antes da incorporação. O trabalho passa a ser
feito no acervo normal, com histórico por gravação.

## Recuperação pelo histórico

Abrir [histórico do lote](http://127.0.0.1:8000/editorial#/historico?document=quatro-colecoes)
ou **Área editorial → Histórico** e localizar o identificador de `gravacao.json`.

**Restaurar** prepara uma prévia; a confirmação faz uma nova gravação com o estado
anterior. Os novos textos são retirados e catálogo, fila e busca voltam ao estado
anterior pelo fluxo editorial. As fontes de pesquisa e os candidatos temporários
permanecem preservados.

Se houver edições posteriores nos arquivos envolvidos, o sistema recusa a
restauração em conflito. Não apagar nem substituir manualmente os registros
de `.local/editorial/history/`; essa pasta contém a cópia recuperável local
e não acompanha o Git por padrão.

## Fila para a próxima etapa

- [fila-retidas.csv](fila-retidas.csv): 164 unidades que não foram incorporadas,
  com motivo e URL de origem. Permanecem fora do catálogo até resolução.
- **Fila editorial ativa:** 362 novas entradas, uma por documento incorporado;
  usar o filtro por coleção para acompanhar revisões e correções.
- **Coleta restante:** especialmente as 712 URLs de Svitlana/Erdogan ainda não
  adquiridas, as fontes russas bloqueadas de Brest e as referências sem texto.
  Os inventários completos e ocorrências por série permanecem na área de trabalho.

O próximo trabalho será definir o método de triagem e resolução dessas filas,
articulando notas, tabelas, fronteiras, variantes, metadados e retomada da coleta.
Nenhum novo lote de aquisição foi iniciado durante a incorporação.

## Operação reproduzível

O comando usado na incorporação é uma gravação autorizada, não uma suíte de testes:

```bash
python3 scripts/coletores/incorporate.py \
  --approved-package-sha256 dc315c525f8c48bb6f3d203c71f3215f30153faeee683c598cf32f7574360449 \
  --apply
```

Não repetir esse comando para atualizar ou corrigir documentos: após a
incorporação, a base já mudou e a operação é recusada. Usar a área editorial
para alterações posteriores. A execução sem `--apply` apenas descreve o plano,
desde que a base ainda corresponda à prévia.

Não há commit, push ou publicação automática nesse procedimento. A conferência
manual no navegador continua a cargo do pesquisador, conforme solicitado.
