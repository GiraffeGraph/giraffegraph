"""Build the printed handouts for the supervisor meeting of 16 October 2026.

Run from this folder:
    uv run --no-project --python 3.12 --with markdown --with pypdf python build.py
Writes build/NN-name.pdf for each NN-name.md and build/toplanti-belgeleri.pdf with all of them
(Google Chrome is required for PDF).
"""

import re
import subprocess
from pathlib import Path

import markdown
from pypdf import PdfWriter

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

STYLE = """
@font-face { font-family: "Copernicus"; src: url("../assets/GalaxieCopernicus-Book.woff2") format("woff2"); }
:root { --navy: #1D2E47; --ink: #24344c; --bronze: #C4893A; --honey: #E9AE3F; --slate: #6b7480; --line: #d9dde2; }
@page { size: A4; margin: 15mm 17mm 14mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; background: #fff; color: var(--ink); font: 9.8pt/1.5 "Inter", "Helvetica Neue", Arial, sans-serif; }
header { display: flex; align-items: center; gap: 9pt; padding-bottom: 7pt; border-bottom: 1.4pt solid var(--honey); }
header img { width: 28pt; height: 28pt; }
header .name { font: 16pt/1 "Copernicus", Georgia, serif; color: var(--navy); }
header .meta { margin-left: auto; text-align: right; font-size: 8pt; color: var(--slate); line-height: 1.35; }
h1 { font: 16pt/1.25 "Copernicus", Georgia, serif; color: var(--navy); margin: 13pt 0 6pt; }
h2 { font: 11.4pt/1.3 "Copernicus", Georgia, serif; color: var(--navy); margin: 13pt 0 4pt; padding-left: 7pt;
     border-left: 2.4pt solid var(--honey); break-after: avoid; }
h3 { font: 10.4pt/1.3 "Copernicus", Georgia, serif; color: var(--navy); margin: 9pt 0 3pt; break-after: avoid; }
p { margin: 0 0 6pt; }
ul, ol { margin: 2pt 0 7pt; padding-left: 16pt; }
li { margin-bottom: 3pt; }
li::marker { color: var(--bronze); font-weight: 600; }
strong { color: var(--navy); font-weight: 600; }
table { width: 100%; border-collapse: collapse; margin: 4pt 0 9pt; font-size: 8.9pt; line-height: 1.4; break-inside: auto; }
th { text-align: left; color: var(--navy); font-weight: 600; border-bottom: 1.1pt solid var(--honey); padding: 4pt 6pt; }
td { border-bottom: 0.5pt solid var(--line); padding: 4pt 6pt; vertical-align: top; }
tr { break-inside: avoid; }
blockquote { margin: 6pt 0; padding: 5pt 9pt; background: #f8f6f1; border-left: 2.4pt solid var(--honey); }
blockquote p { margin: 0; }
code { font: 8.8pt "Menlo", monospace; background: #f3f1ec; padding: 0 2pt; border-radius: 2pt; }
footer { margin-top: 12pt; padding-top: 6pt; border-top: 0.6pt solid var(--line); font-size: 7.8pt; color: var(--slate); }
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">')

HEADER = """<header><img src="../assets/logo.png" alt=""><span class="name">GiraffeGraph</span>
<div class="meta">CSE 491 Bitirme Projesi · Danışman toplantısı<br>16 Ekim 2026</div></header>"""

FOOTER = """<footer>Yahya Efe Kuruçay · Deniz Büyükşahin · Alperen Ulukaya · Danışman: Arş. Gör. Dr. Taha Yiğit Alkan</footer>"""


def page(title, body):
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>{title}</title>{FONTS}'
            f'<style>{STYLE}</style></head><body>{HEADER}{body}{FOOTER}</body></html>')


def main():
    BUILD.mkdir(exist_ok=True)
    pdfs = []
    for source in sorted(HERE.glob("[0-9][0-9]-*.md")):
        text = source.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", text, re.M).group(1)
        html_path = BUILD / f"{source.stem}.html"
        html_path.write_text(page(title, markdown.markdown(text, extensions=["tables", "sane_lists"])), encoding="utf-8")
        pdf_path = BUILD / f"{source.stem}.pdf"
        if CHROME.exists():
            subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            "--virtual-time-budget=8000", f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                           check=True, capture_output=True)
            pdfs.append(pdf_path)
    if pdfs:
        writer = PdfWriter()
        for pdf in pdfs:
            writer.append(str(pdf))
        writer.write(str(BUILD / "toplanti-belgeleri.pdf"))
    for pdf in pdfs:
        print(pdf.name)


if __name__ == "__main__":
    main()
