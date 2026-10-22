# Leitura, estudo e exportação de coleções — 22/10/2026

A revisão documental fica pausada durante esta entrega. Nenhum texto, tradução, ID ou URL foi alterado.

## Decisões

- Os endereços existentes `#/doc/ID` abrem a leitura normal, independentemente do último modo usado. Índice, marcador e seleção de idioma permanecem disponíveis.
- “Estudar” abre o documento na bancada existente (`?bancada=1`), agora iniciando em estudo. Preserva abas, instrumentos, fac-símiles e atalhos editoriais locais. Não foi criada outra bancada concorrente. “Leitor” retorna à leitura normal. Alternância entre parágrafos e paralelo continua sem navegação.
- O seletor compacto de idioma permanece visível com o painel recolhido. No paralelo, corresponde à coluna esquerda.
- O download ZIP abrange todos os documentos e todas as versões linguísticas da coleção ou subcoleção, independentemente da paginação. Usa a mesma exportação Markdown do leitor, nomes por ID e idioma, manifesto e LEIA-ME. Não inclui PDFs nem imagens externas. Funciona no site estático, sem serviços externos ou dependências. Em falhas, não baixa pacote parcial. Arquivos são reunidos em memória, sem compressão; coleções grandes podem demorar. Limite ZIP clássico: 4 GB e 65.535 entradas.
- A home mantém contagens derivadas do manifesto e recorte de atividade regenerado por `python3 scripts/update_portal_activity.py`. O recorte combina adições no Git com datas explícitas de coleta da proveniência, sem confundir datas históricas ou revisões de formatação com novas traduções. Regenerar antes de publicar novas incorporações. Os números se atualizam com o manifesto; o recorte é estático.

## Validação manual

1. Inicie `python3 -m backend`, abra http://127.0.0.1:8000/ e atualize com Ctrl+Shift+R. Confira totais, traduções e fontes recentes na home.
2. Abra uma coleção e baixe o ZIP; repita dentro de uma subcoleção. Descompacte e confira pastas por ID, versões disponíveis e manifesto. Uma coleção paginada deve exportar também documentos fora da primeira página.
3. Pelo acervo, abra um documento com tradução. Deve iniciar em leitura normal. Recolha o painel, altere o idioma e confira índice, marcação e retomada.
4. Clique “Estudar”: confira abas da bancada, ferramentas laterais, estudo por parágrafo e paralelo, fac-símiles quando existentes. Mude o idioma compacto no paralelo e confira a coluna esquerda.
5. No backend local, confira editar trecho, editar Markdown e importar tradução. Esses controles continuam condicionados ao backend. Use “Leitor” e confirme a volta à leitura normal. Reabra uma marca salva em estudo no leitor: ela não deve mudar o leitor para estudo.
6. Opcionalmente, sirva com `python3 -m http.server 8000` para conferir ZIP e leitura sem backend. Não haverá gravações editoriais nesse servidor.

Não foram executados testes automatizados nem testes de navegador nesta entrega. Sem commit ou push.

## Refinamento da home e dos controles

“Percurso pelo acervo” agora percorre todas as coleções com setas e contador, sem avanço automático. O recorte de versões inclui também versões coletadas com data de proveniência, identificadas como tal; os registros anteriores têm navegação própria. Isso não atribui autoria de tradução nem revisão editorial às versões coletadas. O botão ZIP recebeu o padrão carmim. O seletor de idioma duplicado do painel expandido foi removido; permanece o seletor compacto e, no paralelo, a escolha das duas colunas.

Conferência manual adicional: percorra o carrossel, navegue pelas páginas de versões, confira o botão ZIP em coleção e subcoleção e abra “Visualização” para confirmar que o seletor de leitura não está duplicado.
