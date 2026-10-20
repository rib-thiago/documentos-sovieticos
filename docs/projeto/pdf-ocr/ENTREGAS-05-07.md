# Oficina documental — entregas 5 a 7

20/10/2026. Implementação conjunta, com etapas verificáveis. Entregas aprovadas pelo responsável e registradas em commits nesta rodada; nenhum push foi realizado. Não foram aplicadas incorporações ou publicações no acervo real durante os testes.

## Antes de testar

Encerre o backend anterior com Ctrl+C e reinicie:

```bash
python3 -m backend
```

Abra http://127.0.0.1:8000/editorial#/pdf e use Ctrl+Shift+R para renovar os arquivos da interface. Escolha uma fonte já recebida. Não há dependência Python nova; continuam valendo pypdf, Poppler e Tesseract opcionais da oficina. A delimitação manual precisa do Poppler (`pdftoppm`); não precisa executar OCR.

Para começar, use **uma ou duas páginas** e um documento piloto com ID reconhecível. Faça backup de `.local/research/` e dos arquivos do acervo antes de trabalhar com suas fontes definitivas. Os testes automatizados usam diretórios temporários; seu teste pela interface grava dados reais no ambiente local.

## Entrega 5 — fronteiras, sucessão de unidades e localização na imagem

### O que mudou

A revisão da página agora tem **Revisar fronteiras e localizar unidades na imagem**. As unidades são intervalos do texto, com IDs persistentes. Dividir ou unir cria IDs novos e registra de quais unidades eles vieram. O texto integral da página é preservado: esses comandos mudam a segmentação de referência, não apagam ou reescrevem a transcrição.

Caixas manuais usam coordenadas relativas à imagem da página. Palavras/coordenadas OCR podem ser mostradas como sugestões; não são adotadas automaticamente. Uma unidade pode receber até 16 retângulos, inclusive para texto que ocupa várias regiões da página.

### Como conferir

1. Abra a revisão de uma página e salve qualquer rascunho pendente. O alinhamento não grava enquanto houver texto ou metadados de revisão não salvos.
2. Expanda **Revisar fronteiras e localizar unidades na imagem** e escolha uma unidade.
3. No campo do texto selecionado, posicione o cursor onde deseja dividir. Clique em **Dividir na posição do cursor**.
4. Confira a sucessão de IDs, os textos resultantes e **Confirme a revisão estrutural**. O texto integral da página deve continuar igual; agora existem duas unidades onde havia uma.
5. Escolha a primeira e use **Unir à unidade seguinte**. Confira e confirme. Surge uma nova unidade com os dois IDs anteriores como pais.
6. Selecione uma unidade, encontre seu texto na imagem e arraste para desenhar um retângulo. Repita se precisar de mais regiões. Alternativamente, preencha x/y/largura/altura de 0 a 1 e use **Adicionar retângulo numérico**.
7. Exemplo: x `0.1`, y `0.2`, largura `0.3`, altura `0.1` corresponde a 10% da esquerda, 20% do topo, 30% da largura e 10% da altura da página.
8. Clique em **Conferir localização na imagem** e confirme a revisão estrutural. Reabra a página: o retângulo deve permanecer.
9. No **Histórico recuperável desta página**, prepare a restauração anterior à divisão ou à marcação. Os textos, unidades e caixas daquele estado devem reaparecer numa nova revisão.

Dividir/unir não transfere caixas antigas para unidades novas: é necessário localizá-las novamente. Uma alteração textual preserva IDs/caixas de unidades reconhecidas sem mudança; unidades retiradas e novos IDs ficam registrados no histórico. Se a alteração textual refizer fronteiras manuais, a prévia avisa que elas precisam ser conferidas.

A imagem usada para marcar caixas é uma renderização da página original, normalizada pela orientação exibida. Os offsets do texto da página são pontos de código Unicode. As associações de blocos do leitor usam offsets UTF-16, pois partem da seleção do navegador; são espaços diferentes e não devem ser misturados.

### Associar a localização a um bloco do documento

No documento, entre em **Estudo**, clique em **Associar página PDF**, escolha a página e, opcionalmente, uma **unidade da transcrição**. A unidade precisa ter revisão salva. Ao confirmar, a associação guarda seu ID, hash e caixas daquela revisão. **Ver fac-símile** pode mostrar a localização marcada; a referência copiada passa a incluir a unidade. Texto ou revisão alterados continuam exigindo reconferência.

Ainda se trata de uma associação editorial humana. O sistema não certifica que a tradução corresponda ao original ou que o retângulo selecionado contenha o trecho correto.

## Entrega 6 — incorporar transcrições revisadas

### Onde fica

Na página da fonte ou na revisão da fonte dentro de **Manipular PDF**, abra **Incorporar transcrição revisada**.

### Destinos

- **Novo documento no acervo local:** informe ID, título, idioma e coleção/subcoleção. Outros metadados podem ser completados depois pelo catálogo.
- **Versão de documento existente:** informe o ID e idioma. Se a edição já existir, sua substituição exige confirmação explícita. Uma tradução nova usa as regras de importação já existentes.
- **Versão privada do projeto:** disponível ao trabalhar naquele projeto; documento e fonte precisam pertencer a ele. A versão pública permanece intacta. Criar um documento canônico exige sair explicitamente do contexto privado.

### Como conferir

1. Nas páginas escolhidas, salve o estado **Conferida** ou **Em branco**. Páginas pendentes/com problema não podem ser incorporadas.
2. No instrumento de incorporação, escolha o destino e digite as páginas físicas na ordem desejada, por exemplo `1-2`.
3. Para um piloto novo, escolha um ID como `piloto-pdf-01`, preencha título, idioma e coleção.
4. Use **Conferir incorporação**. A prévia mostra destino, diferenças, Markdown completo e renderização. Não há gravação antes da confirmação.
5. Marque as confirmações de substituição/divergências quando aparecerem e clique em **Confirmar incorporação local**.
6. Use **Abrir documento incorporado**. O leitor deve mostrar o texto; o catálogo, manifesto e busca devem refletir a incorporação canônica. A bancada atualiza seu catálogo em memória para permitir abrir IDs novos.
7. Nas versões privadas, confira o texto no projeto e depois abra sem projeto: o acervo canônico deve permanecer igual.
8. A proveniência canônica fica na edição, em `extra.pdf_transcription`: fonte/hash, páginas, revisões, rótulos impressos, unidades e intervalos do texto incorporado. Versões privadas têm recibos equivalentes no armazenamento local.
9. O vínculo com o PDF é concluído automaticamente. Se houver falha depois de salvar o texto, a interface informa **Texto salvo; falta concluir o vínculo**. Use **Incorporações e vínculos pendentes → Concluir vínculo do texto salvo**; isso não regrava o texto.

O conteúdo reúne as transcrições salvas, com duas quebras de linha entre páginas. Não inventa cabeçalhos, não remove notas e não força pareamento com traduções. As fronteiras de referência revisadas são preservadas na proveniência; dividir/unir unidades não insere/remove automaticamente parágrafos Markdown no corpo. Se desejar essa mudança de apresentação, edite a transcrição/Markdown e confira sua prévia.

Limites: até 200 páginas por incorporação e 4 MiB de texto. Mudanças nas revisões, no destino ou no catálogo após a prévia impedem a gravação desatualizada.

### Recuperação

- Incorporação canônica: use o **histórico editorial do documento** já existente. A restauração de criação remove o documento criado e o retira da busca, preservando PDF e revisão de origem.
- Versão privada: use o histórico da versão no projeto.
- Vínculos têm histórico próprio. Recuperar uma versão canônica não publica/retira PDFs automaticamente; confira os vínculos e a projeção separadamente.
- Promover uma versão privada segue a confirmação de incorporação do projeto. Vínculos privados não são copiados silenciosamente para o contexto público.

## Entrega 7 — preparar a publicação estática selecionada

### O que significa “aplicar”

São três momentos distintos:

1. **Preparar:** gera derivados numa área privada `.local/research/publications/`. Nada novo é servido como arquivo público do site.
2. **Conferir e aplicar a projeção local:** grava somente os arquivos públicos selecionados no repositório local. O backend passa a servi-los como faria um servidor estático.
3. **Commit e push autorizados:** disponibilizam esses arquivos no GitHub Pages. A ferramenta não executa esses comandos.

A cópia original é preservada. Cada PDF público é um derivado **apenas das páginas físicas vinculadas**, com um mapa para a paginação do derivado. Marcadores de navegação e anotações do PDF não são copiados. O resultado precisa de conferência visual, especialmente em PDFs com formulários, anexos ou estruturas especiais.

### Onde fica e como conferir

1. Abra **Preparar publicação estática dos fac-símiles** na fonte, ou **Preparar publicação estática** em **Gerenciar fontes e páginas** do documento.
2. Carregue os vínculos do documento/fonte e marque somente os que deseja preparar. Vínculos privados de projetos são recusados.
3. Escolha publicar/atualizar ou retirar. Para publicar texto junto do PDF, marque **Incluir transcrições conferidas e suas unidades**. Sem essa opção, as transcrições não são incluídas; o PDF pode ser publicado sem OCR.
4. Use **Preparar e conferir projeção**. Confira a lista de arquivos, documentos, páginas e o **PDF derivado** de cada vínculo.
5. Antes de aplicar, os arquivos continuam apenas na preparação privada.
6. Marque a confirmação da seleção pública e use **Aplicar projeção estática local**. A interface lista o resultado e permite consultar o histórico.
7. Arquivos novos ficam em `assets/facsimiles/`, com nomes derivados de SHA-256, e o índice em `data/facsimiles.json`.
8. Para conferir sem backend, encerre-o e execute:

```bash
python3 -m http.server 8000
```

9. Abra o documento no site, entre em **Estudo → Fontes e fac-símiles** e consulte PDF, transcrição publicada e localização. O leitor usa os arquivos estáticos, sem chamar as APIs privadas. Em hospedagem sob um subdiretório, as URLs continuam relativas ao site.
10. Depois encerre o servidor estático e volte a `python3 -m backend` para continuar editando.

O índice não exporta notas privadas, histórico, candidatos OCR, caminhos locais ou contexto de projetos. Publica somente as páginas e os dados de referência selecionados. Se uma associação estiver desatualizada, a preparação exige reconferência. Se o texto público mudar depois, o leitor marca a referência antiga como pendente de revisão.

A preparação não limpa o repositório nem seleciona automaticamente arquivos para commit. **A coleção local `teste01` segue fora dos commits:** antes de uma futura publicação, o catálogo/manifesto a versionar precisam continuar excluindo esse e quaisquer outros testes da interface.

### Retirar e restaurar

- Escolha **Retirar vínculos selecionados da projeção**, confira e aplique. Arquivos gerenciados que deixarem de ser referenciados são retirados da árvore pública; fontes e backups locais permanecem.
- O **Histórico da projeção pública** prepara a restauração da projeção anterior, novamente com prévia e confirmação.
- Os blobs de recuperação ficam em `.local/research/publications/blobs/`. Faça backup da pasta inteira `.local/research/`; ela não está no Git.
- Gravações da projeção usam um registro pendente e recuperação após interrupção. Falhas não devem deixar índice apontando para arquivos incompletos.
- Retirar do repositório local não desfaz cópias já obtidas por leitores nem altera o GitHub antes de outro commit/push.

Limites atuais: 20 vínculos e 200 páginas por preparação; 80 MiB por artefato derivado; índice público de até 16 MiB. A preparação pesada é isolada do bloqueio editorial e pode levar até seis minutos. Para um primeiro teste, use uma página. Histórico público por URL imutável, índice paginado por documento e cancelamento/retomada da preparação pela interface são evoluções posteriores.

## Verificações realizadas

- Testes isolados de fronteiras, caixas, histórico, concorrência, integridade, incorporação, revisão de origem, substituição explícita, isolamento de projetos, recibos e conclusão de vínculos.
- Testes de catálogo/manifesto/busca após incorporação e recuperação pelo histórico editorial.
- Testes de preparação privada, PDFs com somente as páginas escolhidas, retirada/restauração, falhas de escrita, recuperação, proteção a links simbólicos e exclusão de notas privadas.
- Fluxo HTTP completo em acervo temporário, incluindo imagem de alinhamento, incorporação, preparação, conferência e aplicação.
- Consulta dos artefatos por servidor estático comum, sem APIs da aplicação; lógica do leitor estático conferida com JavaScript/DOM simulados, incluindo URLs sob subdiretório.
- Piloto em cópia da primeira página do PDF real de Tukhachevsky: original com o mesmo SHA-256 e renderização PNG do derivado idêntica à imagem de conferência. O texto usado nesse piloto era uma fixture técnica, não uma nova transcrição do julgamento.
- Regressão das funcionalidades anteriores de backend e PDF, além de análise sintática/controles JavaScript. Os testes de interface usam DOM simulado; aparência, arraste, foco e leitura do PDF no navegador real ainda precisam da sua validação manual.

## Pendências conhecidas

- Unidade que atravessa páginas: ainda exige referências por página e nota explicativa; não há unidade única multipágina.
- Cortar/rotacionar/restaurar imagens antes do OCR, ampliar opções de tratamento e revisão especializada de tabelas/notas.
- Confirmar sucessão de unidades após edições textuais extensas; as fronteiras retiradas permanecem no histórico, sem inferir alinhamento novo.
- Oferecer URLs públicas imutáveis por revisão de citação, além dos IDs/hashes já registrados.
- Tornar a preparação estática uma tarefa com progresso, cancelamento e retomada próprios.
- Refinar o layout geral dos instrumentos depois da validação funcional.

A conferência final também ajustou o backend para servir, com leitura parcial por HTTP, os dois PDFs já autorizados na ficha da coleção Tukhachevsky. A permissão é restrita a esses dois caminhos; não expõe a pasta `fontes/` inteira nem fontes privadas da oficina.
