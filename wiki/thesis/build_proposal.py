"""Build the CSE 491 project proposal: export DOCX, HTML and PDF from proposal/proposal.md.

Usage (from this directory):
    uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build_proposal.py

The proposal numbers its references by hand, so nothing is resolved from the bibliography files.
"""

import re
import subprocess
import sys

import build

PROPOSAL = build.HERE / "proposal"

CSS = """
body { font-family: Arial, Helvetica, sans-serif; font-size: 10pt; line-height: 1.4;
       max-width: 720px; margin: 1.5em auto; padding: 0 1em; color: #000; }
header { display: none; }
h1 { font-size: 15pt; margin: 0 0 0.8em; }
h2 { font-size: 12pt; margin: 1.4em 0 0.5em; }
table { border-collapse: collapse; width: 100%; font-size: 8.8pt; margin: 0.6em 0 1em; }
th, td { border: 0.6px solid #000; padding: 3px 5px; vertical-align: top; text-align: left; }
pre { font-size: 8.5pt; background: #f4f4f4; padding: 6px; overflow-x: auto; }
p { margin: 0.5em 0; }
@page { size: A4; margin: 20mm 20mm; }
"""


def main():
    import pypandoc

    source = PROPOSAL / "proposal.md"
    out = PROPOSAL / "build"
    out.mkdir(exist_ok=True)
    common = ["--from=markdown+pipe_tables-smart", "--metadata=title:CSE 491 Project Proposal"]
    css = out / "proposal.css"
    css.write_text(CSS, encoding="utf-8")
    pypandoc.convert_file(
        str(source), "html5", outputfile=str(out / "proposal.html"),
        extra_args=common + ["--standalone", "--embed-resources", f"--css={css}"],
    )
    pypandoc.convert_file(str(source), "docx", outputfile=str(out / "proposal.docx"), extra_args=common)
    if build.CHROME.exists():
        subprocess.run(
            [str(build.CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={out / 'proposal.pdf'}", (out / "proposal.html").as_uri()],
            check=True, capture_output=True, timeout=180,
        )
    words = len(re.findall(r"\w+", source.read_text(encoding="utf-8")))
    print(f"about {words} words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
