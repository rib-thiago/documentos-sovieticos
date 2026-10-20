"""Convert the supplied Word mirror without changing the published catalogue.

Requires antiword 0.37 and scripts/requirements-research.txt dependencies.
Example: PYTHONPATH=/tmp/soviet-military-collector-deps python3
scripts/convert_perpetrator_docs.py --antiword /path/to/antiword
--antiword-home /path/to/share/antiword
"""
import argparse
import csv
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

from markdownify import markdownify
from urllib.parse import quote


def write_guide(report, output, source, records, summary):
    lines = ['# Conversão do espelho Perpetrator2004', '',
             f"Foram encontrados {summary['total']} arquivos `.doc`: {summary['convertidos']} convertidos, "
             f"{summary['falhas']} falhas e {summary['com_alertas']} conversões com alertas estruturais.", '',
             f'Originais preservados em `{source}`.',
             f'Markdown: `{output}/markdown/`; extrações intermediárias: `{output}/docbook/`.', '',
             '## Limites e conferência manual', '',
             'Conversão por antiword 0.37 → DocBook XML → Markdown (markdownify). '
             'Os arquivos Word não foram alterados. A divisão em pastas foi mantida, inclusive '
             'os documentos já extraídos de arquivos compactados. Nenhum documento foi cadastrado no site nesta entrega.', '',
             'A conversão não certifica fidelidade integral. Compare o início, o fim e as notas com o Word; '
             'nos cinco arquivos com tabelas, confira também as células e a ordem de leitura. '
             'Imagens, objetos incorporados, paginação, comentários e controle de alterações do Word '
             'não têm preservação garantida por este método. Os alertas indicam estruturas detectadas, '
             'não uma revisão humana completa. Títulos internos não foram inferidos a partir do conteúdo.', '',
             'Propriedades do Word (autor do arquivo, data de edição e título de aplicativo) '
             'ficam preservadas no XML, sem serem confundidas com os metadados históricos do documento. '
             'Erros de grafia ou de codificação herdados não foram corrigidos silenciosamente.', '',
             'O CSV permite filtrar `status`, `avisos` e `erro`. O JSON inclui hashes dos originais e dos '
             'Markdown, diagnósticos do conversor, contagens de notas e trechos inicial e final.', '',
             '## Falhas', '']
    failed = [r for r in records if r['status'] == 'falhou']
    lines += [f"- `{r['origem']}`: {r['erro']}" for r in failed] or ['Nenhum arquivo deixou de gerar Markdown.']
    lines += ['', '## Arquivos e pendências', '', '| Arquivo convertido | Resultado | Conferência prioritária |',
              '| --- | --- | --- |']
    for row in records:
        dest = row['markdown']
        name = Path(row['origem']).name
        link = f'[{name}]({quote(os.path.relpath(dest, report), safe="/.")})' if dest else name
        lines.append(f"| {link} | {row['status']} | {'; '.join(row['avisos']) or row['erro'] or 'Conferência geral com o Word.'} |")
    (report / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--antiword', default='antiword')
    parser.add_argument('--antiword-home')
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path, default=Path('temporario/perpetrator2004-markdown'))
    args = parser.parse_args()
    source = args.source or next(Path('temporario').glob('showtrials-portatil-*/showtrials-portatil-*/referencia-projeto/data/perpetrator2004/raw/mirror'))
    output = args.output
    report = Path('docs/pesquisa/conversao-perpetrator2004')
    report.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    if args.antiword_home:
        env['ANTIWORDHOME'] = args.antiword_home
    records = []
    for path in sorted(source.rglob('*')):
        if path.suffix.lower() != '.doc' or not path.is_file():
            continue
        relative = path.relative_to(source)
        xmlpath = output / 'docbook' / relative.with_suffix('.xml')
        mdpath = output / 'markdown' / relative.with_suffix('.md')
        record = dict(origem=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      markdown='', status='falhou', avisos=[], erro='')
        try:
            if mdpath.exists() or xmlpath.exists():
                raise RuntimeError('Destino existente: recusado sobrescrever conversão anterior.')
            proc = subprocess.run([args.antiword, '-x', 'db', str(path)], env=env,
                                  capture_output=True, timeout=180)
            record['stderr'] = proc.stderr.decode('utf-8', errors='replace').strip()
            if proc.returncode or not proc.stdout.strip():
                raise RuntimeError(record['stderr'] or f'antiword retornou {proc.returncode}')
            xmlpath.parent.mkdir(parents=True, exist_ok=True)
            xmlpath.write_bytes(proc.stdout)
            root = ET.fromstring(proc.stdout)
            notes = []
            tags = {node.tag for node in root.iter()}

            def render(node):
                content = html.escape(node.text or '') + ''.join(render(child) + html.escape(child.tail or '') for child in node)
                tag = node.tag
                if tag == 'bookinfo':
                    return ''  # Word author/date are application properties, not source metadata.
                if tag == 'title':
                    if node is next(iter(root), None):
                        return ''  # Generated Word property title, retained in the XML.
                    return '<h2>' + content + '</h2>' if content.strip() else ''
                if tag == 'footnote':
                    notes.append(content)
                    return f' [^nota-{len(notes)}] '
                if tag == 'emphasis':
                    target = 'strong' if node.get('role') == 'bold' else 'em'
                else:
                    target = {'para':'p', 'simpara':'p', 'chapter':'section', 'sect1':'section',
                              'sect2':'section', 'book':'div', 'informaltable':'table',
                              'table':'table', 'row':'tr', 'entry':'td', 'thead':'thead',
                              'tbody':'tbody', 'itemizedlist':'ul', 'orderedlist':'ol',
                              'listitem':'li', 'literallayout':'pre', 'superscript':'sup',
                              'subscript':'sub'}.get(tag)
                if tag in {'tgroup', 'colspec'}:
                    return content
                if tag in {'ulink', 'link'}:
                    url = node.get('url')
                    return f'<a href="{html.escape(url, quote=True)}">{content}</a>' if url else content
                return f'<{target}>{content}</{target}>' if target else content

            body = render(root)
            md = markdownify(body, heading_style='ATX').strip()
            for i, note in enumerate(notes, 1):
                text = markdownify(note, heading_style='ATX').strip()
                md += '\n\n' + f'[^nota-{i}]: ' + text.replace('\n', '\n    ')
            if not md.strip():
                raise RuntimeError('Extração sem texto documental.')
            warnings = record['avisos']
            if tags & {'table', 'informaltable'}:
                warnings.append('Conferir tabelas, células mescladas e sequência de leitura no Word.')
            if notes:
                warnings.append('Conferir notas e referências: convertidas as notas identificadas no DocBook.')
            if tags & {'graphic', 'inlinegraphic', 'mediaobject', 'inlinemediaobject'}:
                warnings.append('Imagem mencionada no DocBook; conteúdo visual não incorporado ao Markdown.')
            if record['stderr']:
                warnings.append('O conversor emitiu diagnóstico; consultar stderr no registro JSON.')
            # Do not silently repair encoding inherited from the source/converter.
            if re.search(r'[ÃÏÐ][\u0080-\u00ff]|\ufffd', md):
                warnings.append('Possível problema de codificação no corpo; revisar sem correção automática.')
            mdpath.parent.mkdir(parents=True, exist_ok=True)
            mdpath.write_text(md + '\n', encoding='utf-8')
            record.update(markdown=str(mdpath), docbook=str(xmlpath),
                          status='convertido_com_alertas' if warnings else 'convertido',
                          caracteres=len(md), notas=len(notes), tags=sorted(tags),
                          sha256_markdown=hashlib.sha256(mdpath.read_bytes()).hexdigest(),
                          inicio=md[:200], fim=md[-200:])
        except Exception as exc:
            record['erro'] = str(exc)
        records.append(record)
    summary = dict(total=len(records), convertidos=sum(r['status'] != 'falhou' for r in records),
                   falhas=sum(r['status'] == 'falhou' for r in records),
                   com_alertas=sum(r['status'] == 'convertido_com_alertas' for r in records))
    (report / 'registro.json').write_text(json.dumps(dict(resumo=summary, ferramenta='antiword 0.37 / DocBook + markdownify',
                                                        registros=records), ensure_ascii=False, indent=2) + '\n')
    with (report / 'registro.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=['origem','markdown','status','avisos','erro'])
        writer.writeheader()
        for record in records:
            writer.writerow({key: '; '.join(record[key]) if key == 'avisos' else record[key] for key in writer.fieldnames})
    write_guide(report, output, source, records, summary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
