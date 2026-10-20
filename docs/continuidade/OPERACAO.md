> Atualização de continuidade — 20/10/2026: a interface Carmim, projetos/versões privadas, oficina PDF, OCR rus/eng/por, revisão por página e fac-símiles no estudo já estão implementados. Consulte os roteiros em `docs/projeto/pdf-ocr/`. Os ZIPs antigos e as propostas abaixo são fotografias históricas, não o estado executável atual. Dados de trabalho ficam em `.local/research/`; publicação exige seleção editorial e commit/push separados.

# Trabalhar no acervo hoje

## Abrir o ambiente certo

No terminal, dentro da pasta do projeto:

```bash
python3 -m backend
```

Abra http://127.0.0.1:8000/ e http://127.0.0.1:8000/editorial. O terminal precisa continuar aberto. Encerre com Ctrl+C. Se usar apenas `python3 -m http.server 8000`, terá o site estático, sem as operações editoriais. Não abra dois servidores na mesma porta.

O site em github.io mostra o que foi publicado. Uma tradução salva no computador só chegará lá depois de uma publicação autorizada. Se uma função editorial não aparece, primeiro confira se está no localhost com o backend correto.

## Traduzir e importar

1. Abra o documento e escolha o idioma original; exporte o Markdown pelo painel. Guarde o arquivo original intacto.
2. Traduza em outro arquivo UTF-8, preservando títulos, parágrafos, notas, links, tabelas e nomes/identificadores. Não traduza IDs ou caminhos. Se houver cabeçalho de exportação, mantenha a identificação do documento; não duplique o cabeçalho nem apresente russo como idioma da tradução. Indique `pt` ou `en` quando o campo representar o idioma da versão.
3. Use o padrão `showtrials-1665.pt.md` ou `showtrials-1665.en.md`, por exemplo. O número é o documento, não a ordem na lista. Para documentos de outra origem, conserve o ID real.
4. No leitor local, acesse a edição/importação do documento; ou vá à área editorial, **Importar tradução**. Link direto de exemplo: http://127.0.0.1:8000/editorial#/importar?documento=showtrials-1665&idioma=pt .
5. Escolha explicitamente o documento e o idioma de destino e selecione o arquivo. Confira título, ID, idioma, prévia e diferenças. Uma divergência de identidade exige conferência; não basta renomear um arquivo cujo conteúdo pertence a outro documento.
6. O diagnóstico de parágrafos aponta diferenças estruturais; igualdade de contagens não prova correspondência e diferença não prova erro. Não acrescente quebras só para fazer os números coincidirem.
7. Confirme a gravação. Se já havia tradução, a versão anterior fica no histórico. Reabra o leitor local, confira o idioma e a exportação.

Você não precisa editar JSON para importar uma tradução. Também não precisa pedir uma implementação nova a cada arquivo traduzido. Para um ajuste pequeno, use o editor Markdown ou a correção de trecho já existentes.

## Recuperar uma edição

Na área editorial, abra **Histórico**, localize o documento e confira a restauração proposta antes de confirmar. Restaurar produz outra alteração registrada. Edições posteriores nos mesmos arquivos podem exigir desfazer primeiro as mais recentes. O histórico está em `.local/editorial/history/`; apagar `.local/` pode destruir a possibilidade de recuperação.

Antes de manutenção importante, encerre o backend e copie a pasta do projeto para outro local, incluindo `.local/`. Uma cópia somente do repositório remoto não guarda esse histórico. Guarde também PDFs e outros arquivos de origem que não tenham sido incluídos no Git.

## Criar coleção, subcoleção e documento

1. Abra **Coleções** e **Nova coleção** em http://127.0.0.1:8000/editorial#/colecoes . Cadastre título, descrição e os demais campos apresentados, confira a prévia e salve.
2. Para uma divisão interna, use **Nova subcoleção** dentro da coleção. O modelo atual prevê coleção e um nível de subcoleção; não invente níveis adicionais sem evoluir o esquema.
3. Use **Novo documento**: http://127.0.0.1:8000/editorial#/novo-documento . Selecione a coleção/subcoleção adequada e envie Markdown ou TXT. PDF ainda não é aceito nesse cadastro.
4. IDs devem ser únicos e estáveis; no cadastro atual usam letras minúsculas sem acento, números e hífens. Título pode mudar; ID e URL devem permanecer estáveis. Em material do ShowTrials preserve o ID histórico quando aplicável.
5. Registre data do documento, origem, URL e referência arquivística quando disponíveis. Data de publicação de uma página não é necessariamente a data do documento.
6. Confira e salve. Depois importe as traduções no documento criado, evitando cadastrar cada idioma como documento independente.

Uma coleção organiza documentos; uma edição representa um idioma de um documento. Um PDF pode conter vários documentos; uma página não deve virar automaticamente um documento. Para lotes grandes, prepare inventário e diagnóstico de duplicatas antes de gravar.

## Levar alterações ao site público

Primeiro confira no localhost. Depois solicite uma revisão dos arquivos alterados e um commit/push com escopo definido. Não use `git add .` indiscriminadamente: existem alterações locais de outras frentes. Não envie `.local/`, rascunhos privados, credenciais ou arquivos temporários por acidente. O procedimento desta seção não executa publicação por conta própria.
