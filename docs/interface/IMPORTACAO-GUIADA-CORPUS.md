# Importação guiada de corpus

## Fluxo

Na área editorial, abra **Importar lote**. O CSV deixou de ser obrigatório e continua disponível como opção avançada.

1. **Corpus:** escolha uma coleção principal e, se houver, uma de suas subcoleções. Informe o idioma habitual dos originais, autoria, fonte, URL e outros metadados compartilhados. Quantidade esperada é uma conferência opcional. Campos que variam entre documentos devem ficar vazios e podem ser completados no catálogo depois.
2. **Arquivos:** selecione originais e traduções Markdown/TXT em UTF-8. Até 100 arquivos, 4 MiB cada, 20 MiB no conjunto.
3. **Associação:** revise cada arquivo. O nome `carta-01.ru.md` sugere ID `carta-01` e russo; `carta-01.pt.md` sugere o mesmo documento e português. O primeiro título Markdown é sugerido como título da versão. IDs reconhecidos no cabeçalho também podem orientar a sugestão. Todas as sugestões são editáveis.
4. Escolha explicitamente original/tradução, idioma, ID e título em cada cartão. Deve haver um original por ID e uma versão por idioma. Se alterar o idioma comum depois de carregar arquivos, confira os papéis individuais: eles não são reescritos silenciosamente.
5. **Gerar prévia:** confira destinos, metadados, advertências de identificação e conteúdo. As traduções têm prévia própria e contagens de títulos, parágrafos, listas e tabelas comparadas ao original. As contagens não comprovam correspondência entre parágrafos.
6. **Confirmar e salvar:** usa o mecanismo transacional existente: grava versões e metadados, atualiza catálogo/manifesto/busca, cria pendência por documento e histórico recuperável do lote. Não publica via Git.

## Proteções e limites

Este fluxo cadastra documentos novos e suas traduções conjuntamente. IDs já cadastrados são recusados; para atualizar uma tradução existente, use **Importar tradução**, com diferenças e histórico próprios. Não há substituição implícita de arquivos. Traduções entram como versões de trabalho. Originais e traduções permanecem integrais; não há alinhamento automático.

A inferência de nomes/cabeçalhos é uma sugestão, não uma identificação histórica garantida. Arquivos com nomes diferentes podem ser associados manualmente ao mesmo ID. Metadados comuns valem para todos os originais, e cada tradução herda a associação documental e sua proveniência. Edição detalhada de autoria/data por documento permanece no catálogo; não foi introduzido OCR/PDF neste fluxo.

## Conferência manual

Reinicie `python3 -m backend`, abra `/editorial#/lote` e atualize com Ctrl+Shift+R.

- Use dois documentos fictícios novos, um com original russo e tradução portuguesa, outro apenas com original. Confirme que há três arquivos, mas apenas dois documentos.
- Escolha coleção/subcoleção por título, sem digitar IDs. Confira os metadados comuns na prévia.
- Troque manualmente o ID da tradução para um sem original: a prévia deve ser bloqueada. Restaure e repita com idioma duplicado.
- Informe quantidade esperada diferente da seleção: corrija o aviso antes de prosseguir.
- Confira uma divergência de ID no cabeçalho e os diagnósticos estruturais sem alteração automática do texto.
- Se optar por salvar o lote de teste, confira leitor, catálogo e busca. No histórico do lote use a recuperação existente para desfazê-lo.
- Abra **Usar CSV (avançado)** para conferir que o caminho antigo permanece acessível.

Não foram executados testes automatizados ou de navegador. Nenhum cadastro foi criado nesta entrega. Sem commit ou push.
