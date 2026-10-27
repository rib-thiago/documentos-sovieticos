# Piloto Zinoviev: fac-símiles, OCR e edição

26/10/2026. Material escolhido pelo responsável em `temporario/Zinoviev/Sentença Merecida/`. Nenhuma incorporação ao catálogo ou publicação automática foi realizada.

## Diagnóstico dos PDFs

| Arquivo identificado pelo nome | Páginas físicas | Bytes | Texto extraível |
|---|---:|---:|---|
| RGASPI, f.17, op.171, d.425, arquivo -1 | 240 | 94.008.386 | Nenhum nas 240 páginas |
| RGASPI, f.17, op.171, d.426, arquivo -2 | 297 | 102.167.140 | Nenhum nas 297 páginas |

Os dois são PDFs digitalizados, sem criptografia, produzidos segundo seus metadados por ABBYY FineReader 12. O nome do produtor não significa que haja uma camada de OCR. `pdftotext` aplicado a cada arquivo inteiro não retornou caracteres não brancos. Os arquivos cabem individualmente no limite padrão de upload local de 256 MiB.

A inspeção visual amostral encontrou texto datilografado em russo, sublinhados, ruído de digitalização, marcas manuscritas e numerações distintas. Por exemplo, a página física 20 do d.426 mostra “18” datilografado e “19” manuscrito. Não inferir foliação arquivística ou paginação impressa a partir do índice do PDF. As referências arquivísticas acima são as indicadas pelos nomes dos arquivos; não foram autenticadas contra um inventário externo.

Executado OCR amostral somente da página física 20 de cada PDF, a 200 DPI, Tesseract `rus`, PSM 3. Foram obtidos respectivamente 1.320 e 1.270 caracteres. O resultado contém texto aproveitável, mas também erros em letras, espaços, hifens e sublinhados. Não houve avaliação estatística da precisão nem revisão integral. Esses textos são candidatos, não transcrições aprovadas.

Diagnóstico com hashes e amostras não revisadas: `temporario/zinoviev-piloto-diagnostico/`. Renderizações amostrais de inspeção ficaram em `/tmp/zinoviev-piloto/`. Os originais foram preservados. Não foi executado OCR das 537 páginas.

## É preciso converter o PDF antes?

Não manualmente. Nosso OCR já recebe um PDF: o backend usa Poppler para renderizar cada página na resolução escolhida e então passa a imagem ao Tesseract. A ferramenta executa essa conversão internamente e conserva os candidatos por página. PDFs com texto pesquisável seguem pela extração nativa, sem necessidade de OCR.

O BookReader trabalha com imagens de páginas. Nesta integração, PDF.js gera essas imagens no navegador conforme a navegação, com cache limitado. As geometrias das páginas são lidas antes da abertura para preservar tamanhos/proporções. Não se rasterizam as 537 páginas antecipadamente. As imagens de consulta têm lado maior limitado a 1.800 pixels; essa resolução não define a resolução do OCR. A busca textual e a seleção de palavras dentro do BookReader não foram implementadas nesta etapa.

## Integração entregue

- BookReader oficial **5.0.0-66**, distribuição pronta extraída do pacote oficial, sem npm na máquina do usuário e sem modificações nos scripts da biblioteca.
- Scripts, CSS, imagens, fontes, licença e arquivo oficial de origem mantidos localmente; hashes em `prototipo/oficina/vendor/bookreader-manifest.json`.
- A antiga demonstração de livros hospedados no Internet Archive foi substituída por um visualizador do nosso material.
- Aceita PDF selecionado no computador, fonte PDF cadastrada e os dois atalhos locais Zinoviev d.425/d.426.
- Navegação do BookReader com página individual, páginas duplas, miniaturas e zoom. Página consultada lembrada na sessão para fontes identificáveis.
- Fontes cadastradas têm ação “Ler fac-símiles · BookReader” na própria ferramenta PDF. Na bancada ela abre uma aba ao lado.
- “Revisão / OCR” volta à ferramenta existente na página física consultada. Para um arquivo ainda não cadastrado, a ação “Cadastrar para revisão / OCR” envia uma cópia ao fluxo de fontes locais existente; não cria um documento público. O OCR não começa automaticamente.
- Os dois atalhos piloto são somente leitura, expostos por endpoints locais restritos a esses arquivos. A árvore `temporario/` continua indisponível pelo servidor. Se os arquivos forem movidos, os atalhos desaparecem; seleção de arquivo e fontes cadastradas continuam disponíveis.
- Um PDF selecionado apenas para consulta não é persistido. Após recarregar, precisa ser escolhido novamente. Para persistência, use o cadastro de fonte.

## Roteiro manual

1. Reinicie com `python3 -m backend`, abra **http://127.0.0.1:8000/editorial** e use Ctrl+Shift+R.
2. Na lateral **Fontes e ferramentas**, abra **Fac-símiles · BookReader**.
3. Clique em **Zinoviev · d.425**, aguarde a leitura da sequência e navegue pelas páginas. Experimente página dupla, miniaturas e zoom. Repita com d.426.
4. Selecione um dos PDFs diretamente do computador para conferir esse caminho alternativo. Abrir para consulta não deve cadastrar nem publicar o arquivo.
5. Para testar o ciclo persistente, clique **Cadastrar para revisão / OCR**. A fonte é copiada ao armazenamento local, passa pelo diagnóstico nativo e abre sua ferramenta de revisão. Se o mesmo conteúdo já existir, o backend reaproveita a fonte pelo hash.
6. Na ferramenta, use a seção **OCR**, escolha russo (`rus`), um intervalo curto, por exemplo `20-22`, DPI 300 e PSM 3. Confira a prévia e confirme o processamento. Não comece com as 537 páginas antes de avaliar amostras.
7. Examine os candidatos, compare com a página e aprove/corrija a transcrição pelo fluxo existente. Confira numeração, nomes, sublinhados e palavras quebradas. Não marcar como revisada apenas porque houve resultado OCR.
8. Na própria fonte, use **Ler fac-símiles · BookReader**, vá a outra página e clique **Revisão / OCR**. A ferramenta deve abrir na página física escolhida. O processamento inicial da fonte precisa ter disponibilizado aquela página.
9. Arraste as abas para ver fac-símile e ferramenta editorial lado a lado. Feche/reabra o BookReader e confira a retomada da página na sessão.

No ambiente de desenvolvimento, o detector do backend encontrou Poppler, Tesseract e os modelos `rus`, `eng`, `por`, apesar de uma variável de ambiente apontar inicialmente para uma pasta vazia. O detector já usa a instalação do sistema como alternativa. O ambiente do usuário deve ser conferido na própria ferramenta de OCR.

## Próximas camadas

**Tratamento de imagem:** ImageMagick pode produzir derivados configuráveis para rotação, correção de inclinação, recorte, contraste e limpeza. Não se aplicou limpeza automática a estes originais. Receitas e derivados devem registrar a relação com a página original; o resultado precisa poder ser comparado antes de usar no OCR. A camada atual de OCR já funciona sem ImageMagick.

**Tradução:** permanece independente do motor. Primeiro preservar texto OCR bruto, transcrição corrigida e referências por página/unidade; depois gerar candidatos de tradução associados à versão exata da transcrição. Nenhum provedor pago ou envio externo foi configurado.

**Editor Markdown:** já usamos CodeMirror 6, com busca, histórico de edição e suporte Markdown. Podemos acrescentar comandos de formatação, notas e tabelas. Milkdown é uma alternativa visual baseada em ProseMirror/remark. Uma futura avaliação deve comparar notas, tabelas e estabilidade do arquivo Markdown ao salvar, antes de substituir o editor.

## Verificações

Conferidas sintaxe JS/Python, referências CSS locais e integridade da distribuição contra o arquivo oficial e seu hash de publicação. Inspeção de PDF e OCR amostral são diagnósticos do material, não testes de navegador. A interação BookReader/PDF.js, o cadastro, OCR pela interface e o retorno entre abas aguardam a validação manual do responsável. Nenhum commit ou push.
