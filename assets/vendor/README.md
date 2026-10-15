# Bibliotecas da leitura

Distribuições para navegador, incluídas no repositório para não depender de CDN em tempo de execução:

| Biblioteca | Versão | Origem | Licença |
| --- | --- | --- | --- |
| markdown-it | 15.0.2 | https://github.com/markdown-it/markdown-it | MIT |
| markdown-it-footnote | 4.0.0 | https://github.com/markdown-it/markdown-it-footnote | MIT |
| DOMPurify | 3.4.17 | https://github.com/cure53/DOMPurify | Apache-2.0 OR MPL-2.0 |

Os arquivos foram obtidos dos pacotes oficiais em registry.npmjs.org por HTTPS, sem executar npm. A integridade SHA-512 de cada tarball foi conferida antes da cópia. `manifest.json` registra os endereços, versões, integridade dos pacotes e SHA-256 dos scripts. Cada diretório inclui a licença fornecida pelo pacote. Ao atualizar, substitua a distribuição oficial, confira sua integridade, atualize o manifesto e repita os testes de leitura e sanitização.

HTML bruto é desativado no parser; o resultado passa pelo DOMPurify. Notas e referências internas são navegadas sem alterar a rota da aplicação.
