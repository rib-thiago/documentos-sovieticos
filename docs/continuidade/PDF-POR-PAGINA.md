> Atualização de continuidade — 20/10/2026: a interface Carmim, projetos/versões privadas, oficina PDF, OCR rus/eng/por, revisão por página e fac-símiles no estudo já estão implementados. Consulte os roteiros em `docs/projeto/pdf-ocr/`. Os ZIPs antigos e as propostas abaixo são fotografias históricas, não o estado executável atual. Dados de trabalho ficam em `.local/research/`; publicação exige seleção editorial e commit/push separados.

# Proposta: oficina de PDF, extração e revisão por página

**Especificação para implementar. Não está pronta no aplicativo em 20/10/2026.** Esta proposta detalha o plano de ferramentas; não substitui as funções existentes de edição/tradução.

## Onde cada tarefa deve ficar

**Área editorial → Receber fonte:** entrada do PDF, destino, proveniência e operações de processamento.

**Bancada → Fonte / transcrição:** trabalho diário. Página do PDF de um lado; texto editável, diagnóstico e notas do outro. A mesma fonte abre no contexto do documento, sem refazer o cadastro.

**Leitor público:** transcrição aprovada e fac-símile autorizado, com referências de página. Sem botões de processamento local. GitHub Pages pode servir arquivos/imagens selecionados estaticamente, mas não executar OCR nem salvar correções.

## Percurso esperado

1. Escolher coleção existente ou criar coleção. Escolher subcoleção existente, criar uma ou deixar **Sem subcoleção**. Uma coleção é obrigatória no modelo atual; não é preciso fabricar subcoleção.
2. Enviar PDF; registrar título, origem, URL, referência arquivística, idioma(s) e condições de disponibilização conhecidas. Preservar bytes, nome original, hash SHA-256 e data de entrada.
3. Mostrar quantidade de páginas e uma prévia. Separar **arquivo-fonte** de **documento**: um livro pode originar vários documentos com intervalos de página. Escolher documento existente, candidato novo ou vários candidatos. Não criar automaticamente um documento por página.
4. Analisar cada página; apresentar texto encontrado, diagnóstico e método sugerido. PDF misto pode ter páginas pesquisáveis, imagens e páginas em branco.
5. Extrair a camada textual onde houver qualidade aproveitável. Sugerir OCR onde não houver texto ou ele parecer ruim; permitir decisão manual por página e reprocessamento. Texto selecionável não garante texto correto.
6. Abrir bancada de revisão com página visível e texto correspondente. Salvar rascunhos e progresso duráveis, mesmo ao fechar navegador ou reiniciar backend.
7. Revisar páginas e, separadamente, conferir a junção em documentos: títulos, fronteiras, notas, tabelas, continuidade de frases e hifens de fim de linha.
8. Conferir prévia/diferenças do Markdown final e confirmar inclusão/atualização local. Atualizar catálogo, manifesto e busca pela camada editorial, com histórico.
9. Selecionar o que vai ao público. Publicar só mediante autorização separada; rascunhos e OCR bruto não devem aparecer como edição revisada.

## Tela de trabalho

```text
Coleção / subcoleção · Fonte · Documento candidato
Página 12 de 86     [anterior] [ir à página] [próxima]
┌──────────────────────┬───────────────────────────────┐
│ Página PDF           │ Texto / prévia Markdown       │
│ zoom, girar exibição │ método: camada textual / OCR  │
│ referência impressa │ aviso, notas e editor         │
│                      │ salvo · pendente de revisão   │
└──────────────────────┴───────────────────────────────┘
[Salvar rascunho] [Marcar revisada] [Reabrir revisão]
Progresso: 25 revisadas · 3 precisam de ajuda · 58 pendentes
```

Adotar os componentes e a paleta Carmim existentes. Em telas estreitas, alternar Fonte/Texto sem perder a página e a posição. Lista lateral recolhível de páginas com estado e filtro **Pendentes / Com problema**. Nenhuma barra deve ocupar desnecessariamente o espaço de leitura.

## Regras de página e texto

- Número físico é o índice do PDF; número impresso é um campo separado e pode ser romano, ausente ou repetido. Referências devem identificar fonte e página de forma estável.
- Preservar PDF completo; “segmentar em páginas” pode ser um mapa e renderização sob demanda. Gerar PDFs individuais apenas quando necessário, sem destruir ou substituir o original.
- Guardar texto bruto extraído/OCR separado do texto corrigido e do Markdown aprovado. Reprocessar uma página não pode sobrescrever correções; mostrar novo candidato e diferenças.
- Extrair notas, cabeçalhos repetidos e tabelas com diagnóstico. Não eliminar silenciosamente conteúdo considerado rodapé. Não prometer conversão fiel de tabelas complexas ou manuscritos.
- Idioma OCR é configurável, incluindo páginas com mais de um idioma; registrar motor, versão e parâmetros. Não traduzir durante OCR.
- Quebras físicas de página não são fronteiras automáticas de parágrafo. Guardar o vínculo página → trechos, inclusive quando um parágrafo continua na página seguinte.
- Na primeira entrega, referências de página bastam. Alinhamento multilíngue e identificação estável de passagens exigem etapa própria, sem depender apenas de números de parágrafo.

## Detecção assistida de OCR

Usar sinais explicáveis por página: quantidade de texto, caracteres inválidos, distribuição do texto, presença de imagens e amostra visual. Classificação sugerida: **camada aproveitável**, **requer OCR**, **conferir**, **branca confirmada**. Não usar só um limite de caracteres: página de título curta não equivale a falha. Exibir a razão e permitir substituir a decisão.

Primeiro suporte: texto impresso, com piloto em russo. PDF protegido, corrompido ou idioma OCR indisponível deve gerar mensagem e pendência; não travar a fila nem fingir conclusão. Manuscritos permanecem revisão/transcrição manual ou trabalho futuro.

## Persistência proposta

| Registro | Campos essenciais |
| --- | --- |
| Fonte | ID, hash, nome, caminho, origem, data, idioma, total de páginas, proveniência e política de exposição. |
| Página | ID estável, fonte, índice físico, rótulo impresso, rotação, diagnóstico, método escolhido. |
| Execução | ID, fonte/hash, operação, receita, motor/versão, parâmetros, estado, progresso, erros e tentativas. |
| Revisão | Página, texto bruto, texto corrigido, revisão-base, estado, data, notas e histórico. |
| Vínculo documental | Documento/candidato, fonte, páginas/intervalos e correspondência com trechos. |

Proposta física: fontes preservadas no banco de arquivos a consolidar; jobs em `.local/research/jobs.sqlite3`; resultados candidatos em `.local/research/`; vínculos aprovados em dados versionados com esquema explícito. Não usar `sessionStorage` como armazenamento principal desse trabalho. O banco da busca pode ser reconstruído; jobs e revisões não podem desaparecer junto dele. Fornecer instruções de backup e recuperação antes do uso diário.

Estados de processamento e de revisão são independentes. Exemplo: OCR **concluído**, página **a revisar**. Página revisada deve poder voltar a pendente, com histórico. Progresso deve distinguir extraídas, revisadas, com falha e deliberadamente em branco, sem contar falhas como sucesso.

## Execução e segurança das gravações

Worker separado do atendimento HTTP, inicialmente uma operação pesada por vez. Persistir conclusão por página. Cancelar conserva trabalho concluído; reiniciar reconhece execução interrompida e permite retomar só o restante. Repetir a mesma receita pode reutilizar resultado pelo hash + motor/versão + parâmetros; alterar idioma ou receita invalida esse reaproveitamento.

Upload com limites explícitos e mensagens compreensíveis; validar arquivo e caminhos, sem usar nome enviado como caminho livre. Salvar correção com revisão-base para impedir que uma aba antiga sobrescreva outra. Trabalho pesado não segura o bloqueio do catálogo. Confirmação editorial é curta e recuperável; conflito exige nova prévia.

## Ferramentas candidatas, a confirmar na implementação

- Extração: avaliar o pdfminer já referenciado no legado; preservação de coordenadas e página deve orientar a escolha final.
- Visualização: avaliar PDF.js, servido localmente, com imagens derivadas quando conveniente para publicação.
- OCR: avaliar Tesseract e OCRmyPDF para texto impresso; um PDF com camada OCR não é automaticamente Markdown estruturado.
- Operações de página: avaliar biblioteca própria para leitura/manipulação sem impor ferramentas pesadas ao backend básico.

Não instalar todas preventivamente. A entrega deve declarar dependências opcionais, versões e licença, detectar disponibilidade e explicar como habilitar. Usar documentação oficial atual ao implementar; estas são candidatas, não uma afirmação de compatibilidade já validada.

## Entregas em ordem

**P1 — Entrada e progresso durável:** recepção, destino, arquivo preservado, páginas, proveniência, jobs e rascunhos. Sem OCR. Não mudar o cadastro Markdown existente. Esta etapa estabelece a base F01 do plano anterior.

**P2 — PDF pesquisável:** extração por página e bancada Fonte/Texto, correção, estados, retomada e histórico. Piloto completo de montagem/aprovação de um documento, incluindo manifesto/busca. Corresponde ao núcleo PDF de F03.

**P3 — PDF escaneado e misto:** detecção assistida, OCR opcional, seleção de páginas, retomada de falhas, reprocessamento com diferenças. Corresponde a F04.

**P4 — Edição e fac-símile público:** intervalos para múltiplos documentos, notas/tabelas, referências de página e escolha dos derivados públicos. Refinar o piloto da P2 sem alterar URLs existentes. Publicação continua separada.

## Roteiro manual de aceitação

- PDF pesquisável: escolher coleção, deixar sem subcoleção, conferir duas páginas contra a imagem e corrigir uma.
- Fechar e reabrir: texto corrigido, página ativa e progresso devem reaparecer.
- PDF misto: página com texto usa extração; página escaneada oferece OCR; página branca exige confirmação apropriada.
- Cancelar OCR e reiniciar backend: retomar preservando páginas concluídas e correções.
- Reprocessar uma página corrigida: comparar candidatos, sem perder a revisão anterior.
- Abrir duas abas e salvar versões concorrentes: mostrar conflito e preservar os dois trabalhos recuperáveis.
- Montar documento de duas páginas com frase e nota atravessando a quebra: conferir integralidade e proveniência na prévia.
- Confirmar localmente: verificar texto, coleção, metadados e busca. Conferir restauração pelo histórico.
- Verificar que rascunhos permanecem privados e que a visualização pública depende dos arquivos deliberadamente selecionados para publicação.

A implementação deve trazer seu próprio roteiro específico. Este documento não executa verificações nem afirma que esses cenários já passaram.
