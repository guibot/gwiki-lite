#!/usr/bin/env python3
"""Atualiza documentos feitos a partir do gwiki_multilite_template.html.

Extrai o conteúdo de cada documento (blocos, sessões, notas, título, tema,
larguras) e injeta-o na versão atual do template, ficando com o código novo.
O original fica guardado em bk/<nome>-AAAAMMDD-HHMMSS.html (pasta bk ao lado do documento).

Uso:
  python3 update_doc.py                            (abre uma janela para escolher o(s) ficheiro(s))
  python3 update_doc.py doc1.html [doc2.html ...]
  python3 update_doc.py doc.html -o novo.html     (não mexe no original)
  python3 update_doc.py doc.html --template outro_template.html
"""
import argparse, datetime, pathlib, re, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_TEMPLATE = HERE / 'gwiki_multilite_template.html'
DOTALL = re.DOTALL


def die(msg):
    sys.exit('erro: ' + msg)


def find(pattern, text, what, flags=DOTALL):
    m = re.search(pattern, text, flags)
    if not m:
        die('não encontrei %s' % what)
    return m


def extract(doc):
    """Devolve o estado de um documento: o que é seu (não código do template)."""
    main = find(r'<main\b[^>]*\bid="main"[^>]*>(.*?)</main>', doc, '<main id="main">').group(1)
    html_tag = find(r'<html\b[^>]*>', doc, '<html>').group(0)
    body_tag = find(r'<body\b[^>]*>', doc, '<body>').group(0)
    body_cls = (re.search(r'class="([^"]*)"', body_tag) or [None, ''])[1]
    st = {
        'main': main,
        'title': find(r'<title>(.*?)</title>', doc, '<title>').group(1),
        'doc_title': find(r'(<h1 id="docTitle"[^>]*>)(.*?)</h1>', doc, '#docTitle').group(2),
        'doc_subtitle': find(r'(<div class="meta" id="docSubtitle"[^>]*>)(.*?)</div>', doc, '#docSubtitle').group(2),
        'theme': (re.search(r'data-theme="([^"]*)"', html_tag) or [None, None])[1],
        'style': (re.search(r'style="([^"]*)"', html_tag) or [None, None])[1],
        # do body só interessa a sidebar escondida; o resto é estado de vista
        'body_class': ' '.join(c for c in body_cls.split() if c == 'sidebar-collapsed'),
    }
    return st


def section_type(sec):
    """text | steps, a partir de data-type, do data-mode antigo ou do conteúdo."""
    open_tag = re.match(r'<section\b[^>]*>', sec).group(0)
    m = re.search(r'data-type="(text|steps)"', open_tag)
    if m:
        return m.group(1)
    m = re.search(r'data-mode="(basic|tutorial)"', open_tag)
    if m:
        return 'steps' if m.group(1) == 'tutorial' else 'text'
    return 'steps' if 'step-block' in sec else 'text'


def with_type(sec, typ):
    open_tag = re.match(r'<section\b[^>]*>', sec).group(0)
    new = re.sub(r'\sdata-(?:type|mode)="[^"]*"', '', open_tag)
    new = new[:-1] + ' data-type="%s">' % typ
    return new + sec[len(open_tag):]


def build_main(st_main, tpl_main):
    """Zona de texto + zona de passos, com os cabeçalhos do próprio template."""
    zh = lambda z: find(r'<div class="zone-header" id="zone-%s".*?</div>' % z, tpl_main, 'cabeçalho da zona ' + z).group(0)
    sections = re.findall(r'<section\b.*?</section>', st_main, DOTALL)
    text, steps = [], []
    for sec in sections:
        typ = section_type(sec)
        (steps if typ == 'steps' else text).append(with_type(sec, typ))
    body = '\n' + zh('text') + '\n' + '\n'.join(text) + '\n' + zh('steps') + '\n' + '\n'.join(steps) + '\n  '
    return body, len(text), len(steps)


def migrate(doc, template):
    st = extract(doc)
    tpl_main_m = find(r'(<main\b[^>]*\bid="main"[^>]*>)(.*?)(</main>)', template, '<main> do template')
    main_inner, n_text, n_steps = build_main(st['main'], tpl_main_m.group(2))

    out = template
    # <main>
    m = re.search(r'(<main\b[^>]*\bid="main"[^>]*>)(.*?)(</main>)', out, DOTALL)
    out = out[:m.start(2)] + main_inner + out[m.end(2):]
    # título / subtítulo
    out = re.sub(r'<title>.*?</title>', lambda _: '<title>%s</title>' % st['title'], out, count=1, flags=DOTALL)
    out = re.sub(r'(<h1 id="docTitle"[^>]*>).*?(</h1>)', lambda m: m.group(1) + st['doc_title'] + m.group(2), out, count=1, flags=DOTALL)
    out = re.sub(r'(<div class="meta" id="docSubtitle"[^>]*>).*?(</div>)', lambda m: m.group(1) + st['doc_subtitle'] + m.group(2), out, count=1, flags=DOTALL)
    # <html>: tema e larguras da sidebar/notas
    html_tag = re.search(r'<html\b[^>]*>', out).group(0)
    attrs = re.sub(r'\s(?:data-theme|style)="[^"]*"', '', html_tag)[:-1]
    if st['theme']:
        attrs += ' data-theme="%s"' % st['theme']
    if st['style']:
        attrs += ' style="%s"' % st['style']
    out = out.replace(html_tag, attrs + '>', 1)
    # <body>
    out = re.sub(r'<body\b[^>]*>', '<body class="%s">' % st['body_class'], out, count=1)

    # verificação: nada do conteúdo se perdeu
    for label, pat in (('blocos', r'<section\b'), ('sessões', r'class="sub-section"'),
                       ('passos', r'class="step-block"'), ('notas', r'\sdata-note="'),
                       ('imagens', r'<img\b')):
        a, b = len(re.findall(pat, st['main'])), len(re.findall(pat, main_inner))
        if a != b:
            die('verificação falhou (%s: %d no original, %d no resultado); nada foi gravado' % (label, a, b))
    return out, n_text, n_steps, len(re.findall(r'\sdata-note="', st['main']))


def choose_files():
    """Janela para escolher um ou mais documentos (macOS: diálogo nativo; senão tkinter)."""
    if sys.platform == 'darwin':
        script = [
            'set fs to choose file with prompt "Escolhe o(s) documento(s) a atualizar" of type {"public.html"} with multiple selections allowed',
            'set out to ""',
            'repeat with f in fs',
            'set out to out & POSIX path of f & linefeed',
            'end repeat',
            'return out',
        ]
        cmd = ['osascript'] + [a for line in script for a in ('-e', line)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:  # cancelado (ou erro)
            return []
        return [pathlib.Path(l) for l in r.stdout.splitlines() if l.strip()]
    try:
        import tkinter
        from tkinter import filedialog
    except ImportError:
        die('sem janela de escolha neste sistema; passa os ficheiros como argumento')
    root = tkinter.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(title='Escolhe o(s) documento(s) a atualizar',
                                        filetypes=[('HTML', '*.html *.htm')])
    root.destroy()
    return [pathlib.Path(f) for f in files]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('docs', nargs='*', type=pathlib.Path, help='sem argumentos abre uma janela de escolha')
    ap.add_argument('-o', '--output', type=pathlib.Path, help='grava aqui em vez de substituir o original (só com 1 documento)')
    ap.add_argument('--template', type=pathlib.Path, default=DEFAULT_TEMPLATE)
    args = ap.parse_args()
    if not args.docs:
        args.docs = choose_files()
        if not args.docs:
            sys.exit('nenhum ficheiro escolhido')
    if args.output and len(args.docs) != 1:
        die('-o só funciona com um documento')
    if not args.template.exists():
        die('template não encontrado: %s' % args.template)
    template = args.template.read_text(encoding='utf-8')

    for path in args.docs:
        if not path.exists():
            die('não existe: %s' % path)
        out, n_text, n_steps, n_notes = migrate(path.read_text(encoding='utf-8'), template)
        if args.output:
            args.output.write_text(out, encoding='utf-8')
            dest = args.output
            bak = None
        else:
            stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            bak_dir = path.parent / 'bk'
            bak_dir.mkdir(exist_ok=True)
            bak = bak_dir / ('%s-%s%s' % (path.stem, stamp, path.suffix))
            shutil.copy2(path, bak)
            path.write_text(out, encoding='utf-8')
            dest = path
        print('%s: %d bloco(s) de texto, %d de passos, %d nota(s)%s' % (
            dest, n_text, n_steps, n_notes, '' if not bak else ' — backup: bk/' + bak.name))


if __name__ == '__main__':
    main()
