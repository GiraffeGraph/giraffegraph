"""Build the TÜBİTAK 2209-A form: number citations, add the reference list, export DOCX and PDF.

Usage (from this directory):
    uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build_form.py

The draft box at the top of tubitak/form.md and its last section ("Göndermeden önce") are notes for
the authors and are left out of the exported files.
"""

import re
import subprocess
import sys

import build

FORM = build.HERE / "tubitak"
NOTES_HEADING = "# Göndermeden önce"
REFERENCES_MARKER = "<!-- references -->"

CSS = """
body { font-family: Arial, Helvetica, sans-serif; font-size: 10pt; line-height: 1.35;
       max-width: 700px; margin: 1.5em auto; padding: 0 1em; color: #000; }
h1.title, header { display: none; }
h1 { font-size: 12pt; margin: 1.4em 0 0.5em; }
h2 { font-size: 10.5pt; margin: 1.1em 0 0.4em; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 0.6em 0 1em; }
th, td { border: 0.6px solid #000; padding: 4px 6px; vertical-align: top; text-align: left; }
p { margin: 0.45em 0; }
@page { size: A4; margin: 22mm 22mm; }
"""


def assemble(entries):
    text = (FORM / "form.md").read_text(encoding="utf-8")
    text = re.sub(r"\A(# [^\n]*\n)\n(?:>[^\n]*\n)+", r"\1", text)
    text = text.split(NOTES_HEADING)[0].rstrip() + "\n"
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

    text = re.sub(r"\[(@[^\]]+)\]", replace, text)
    references = "\n\n".join(
        f"[{number}] {build.INTERNAL.get(key) or build.format_entry(entries[key])}"
        for number, key in enumerate(order, start=1)
    )
    if REFERENCES_MARKER not in text:
        raise SystemExit("references marker is missing from tubitak/form.md")
    return text.replace(REFERENCES_MARKER, references), order


def main():
    import pypandoc

    document, order = assemble(build.load_references())
    out = FORM / "build"
    out.mkdir(exist_ok=True)
    markdown = out / "form.md"
    markdown.write_text(document, encoding="utf-8")
    common = ["--from=markdown+pipe_tables-smart", "--metadata=title:TÜBİTAK 2209-A Araştırma Önerisi Formu"]
    css = out / "form.css"
    css.write_text(CSS, encoding="utf-8")
    pypandoc.convert_file(
        str(markdown), "html5", outputfile=str(out / "form.html"),
        extra_args=common + ["--standalone", "--embed-resources", f"--css={css}"],
    )
    pypandoc.convert_file(str(markdown), "docx", outputfile=str(out / "form.docx"), extra_args=common)
    if build.CHROME.exists():
        subprocess.run(
            [str(build.CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={out / 'form.pdf'}", (out / "form.html").as_uri()],
            check=True, capture_output=True, timeout=180,
        )
    words = len(re.findall(r"\w+", document))
    print(f"{len(order)} references, about {words} words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
