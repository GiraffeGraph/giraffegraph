"""Build the paper version: number citations, add references, export HTML, PDF, DOCX and LaTeX.

Usage (from this directory):
    uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build_paper.py
"""

import re
import subprocess
import sys

import build

PAPER = build.HERE / "paper"

CSS = """
body { font-family: 'CMU Serif', 'Latin Modern Roman', 'Times New Roman', Times, serif;
       font-size: 10.5pt; line-height: 1.38; max-width: 680px; margin: 1.5em auto;
       padding: 0 1em; color: #000; text-align: justify; hyphens: auto; }
h1.title, header { display: none; }
h1 { font-size: 12.5pt; margin: 1.5em 0 0.5em; text-align: left; }
h1:first-of-type { font-size: 17pt; text-align: center; margin: 0.5em 0 0.8em; line-height: 1.25; }
h2 { font-size: 11pt; margin: 1.2em 0 0.4em; text-align: left; }
.authors { text-align: center; font-size: 10.5pt; margin-bottom: 1.4em; }
.authors p { margin: 0.2em 0; }
.abstract { margin: 0 2.6em 1.6em; font-size: 9.6pt; }
table { border-collapse: collapse; width: 100%; font-size: 8.8pt; margin: 0.8em 0 1em;
        text-align: left; }
th { border-top: 1.2px solid #000; border-bottom: 0.8px solid #000; padding: 3px 6px; }
td { padding: 2.5px 6px; vertical-align: top; }
tr:last-child td { border-bottom: 1.2px solid #000; }
code { font-family: Menlo, Consolas, monospace; font-size: 8.6pt; }
img { max-width: 88%; display: block; margin: 0.8em auto 0.2em; }
figcaption { font-size: 9pt; text-align: center; }
span[lang=ar] { font-family: 'Geeza Pro', 'Noto Naskh Arabic', 'Amiri', serif; font-size: 11.5pt; }
p { margin: 0.45em 0; }
@page { size: A4; margin: 24mm 26mm; }
"""


def assemble(entries):
    order = []

    def replace(match):
        numbers = []
        for key in re.split(r"\s*;\s*", match.group(1)):
            key = key.strip().lstrip("@")
            if key not in entries and key not in build.INTERNAL:
                raise SystemExit(f"unknown citation key: {key}")
            if key not in order:
                order.append(key)
            numbers.append(order.index(key) + 1)
        return "[" + ", ".join(str(number) for number in sorted(numbers)) + "]"

    text = (PAPER / "paper.md").read_text(encoding="utf-8")
    text = re.sub(r"\[(@[^\]]+)\]", replace, text)
    text = build.ARABIC_CODE.sub(lambda match: f"[{match.group(1)}]{{lang=ar dir=rtl}}", text)
    references = ["# References", ""]
    for number, key in enumerate(order, start=1):
        references.append(f"[{number}] {build.INTERNAL.get(key) or build.format_entry(entries[key])}")
        references.append("")
    return text.rstrip() + "\n\n" + "\n".join(references) + "\n", order


def main():
    import pypandoc

    build.figures()
    document, order = assemble(build.load_references())
    out = PAPER / "build"
    out.mkdir(exist_ok=True)
    markdown = out / "paper.md"
    markdown.write_text(document, encoding="utf-8")
    common = [
        "--from=markdown+pipe_tables+implicit_figures+fenced_divs-smart",
        f"--resource-path={PAPER}",
        "--metadata=title:Quoted Correctly, Extracted Differently",
    ]
    css = out / "paper.css"
    css.write_text(CSS, encoding="utf-8")
    pypandoc.convert_file(
        str(markdown), "html5", outputfile=str(out / "paper.html"),
        extra_args=common + ["--standalone", "--embed-resources", f"--css={css}"],
    )
    pypandoc.convert_file(str(markdown), "docx", outputfile=str(out / "paper.docx"),
                          extra_args=common)
    pypandoc.convert_file(str(markdown), "latex", outputfile=str(out / "paper.tex"),
                          extra_args=common + ["--standalone"])
    if build.CHROME.exists():
        subprocess.run(
            [str(build.CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={out / 'paper.pdf'}", (out / "paper.html").as_uri()],
            check=True, capture_output=True, timeout=180,
        )
    words = len(re.findall(r"\w+", document))
    print(f"{len(order)} references, about {words} words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
