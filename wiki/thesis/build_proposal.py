"""Build the CSE 491 project proposal: write proposal/proposal.md into the course template and export PDF.

Usage (from this directory):
    uv run --no-project --python 3.12 --with python-docx python build_proposal.py

The course asks for its own template (proposal/template.docx, from the MS Teams assignment), so the
text is written into that file: the header and member tables, the nine numbered sections, the
section sub-labels and the template's tables keep their formatting, and the italic instructions are
removed as the template asks. The PDF is exported with Pages through AppleScript, because Word's
AppleScript "save as" fails on this machine. The proposal numbers its references by hand, so nothing
is resolved from the bibliography files.
"""

import copy
import re
import subprocess
import sys
import time
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = Path(__file__).resolve().parent
PROPOSAL = HERE / "proposal"
PAGES = Path("/Applications/Pages.app")
BODY_SIZE = 20  # half-points
CELL_SIZE = 18


def parse(md):
    """Split the Markdown into the two header tables and a list of (heading, blocks)."""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    lines = md.splitlines()
    header_tables, sections, blocks = [], [], None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# "):
            i += 1
            continue
        if line.startswith("## "):
            blocks = []
            sections.append((line[3:].strip(), blocks))
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            (header_tables if blocks is None else blocks).append(("table", rows))
            continue
        if line.startswith("```"):
            code = []
            i += 1
            while not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            blocks.append(("code", "\n".join(code)))
            i += 1
            continue
        if line.startswith("### "):
            blocks.append(("label", line[4:].strip()))
            i += 1
            continue
        if line.startswith("- "):
            item = [line[2:].strip()]
            i += 1
            while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                item.append(lines[i].strip())
                i += 1
            blocks.append(("bullet", " ".join(item)))
            continue
        if line.strip():
            para = [line.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("|", "#", "- ", "```")):
                para.append(lines[i].strip())
                i += 1
            blocks.append(("para", " ".join(para)))
            continue
        i += 1
    return header_tables, sections


def add_runs(paragraph, text, size):
    """Add text with **bold** and *italic* spans as runs."""
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if not part:
            continue
        bold = part.startswith("**")
        italic = not bold and part.startswith("*")
        run = paragraph.add_run(part.strip("*") if (bold or italic) else part)
        run.bold = bold or None
        run.italic = italic or None
        run.font.size = None
        rpr = run._r.get_or_add_rPr()
        for tag in ("w:sz", "w:szCs"):
            el = OxmlElement(tag)
            el.set(qn("w:val"), str(size))
            rpr.append(el)


def new_paragraph(doc, text, kind):
    p = doc.add_paragraph()
    if kind == "bullet":
        ppr = p._p.get_or_add_pPr()
        numpr = OxmlElement("w:numPr")
        for tag, val in (("w:ilvl", "0"), ("w:numId", "1")):
            el = OxmlElement(tag)
            el.set(qn("w:val"), val)
            numpr.append(el)
        ppr.append(numpr)
        p.paragraph_format.space_after = 0
    if kind == "code":
        run = p.add_run(text)
        run.font.name = "Consolas"
        rpr = run._r.get_or_add_rPr()
        el = OxmlElement("w:sz")
        el.set(qn("w:val"), "16")
        rpr.append(el)
        return p._p
    add_runs(p, text, BODY_SIZE)
    return p._p


def fill_cell(cell, text):
    paragraph = cell.paragraphs[0]
    for run in list(paragraph.runs):
        run._r.getparent().remove(run._r)
    add_runs(paragraph, text, CELL_SIZE)


def fill_table(table, rows, keep_header=True):
    """Fill a template table: keep its header row, clone its first body row for every Markdown row."""
    body = rows[1:] if keep_header else rows
    prototype = copy.deepcopy(table.rows[1]._tr)
    # The empty template rows have a minimum height for handwriting; filled rows size to their text.
    for height in prototype.iter(qn("w:trHeight")):
        height.getparent().remove(height)
    for row in list(table.rows)[1:]:
        table._tbl.remove(row._tr)
    for cells in body:
        tr = copy.deepcopy(prototype)
        table._tbl.append(tr)
        row = table.rows[-1]
        if len(row.cells) != len(cells):
            raise SystemExit(f"column count differs from the template: {cells[0]}")
        for cell, text in zip(row.cells, cells):
            fill_cell(cell, text)


def is_instruction(p):
    runs = p.findall(qn("w:r"))
    return bool(runs) and all(r.find(qn("w:rPr")) is not None and r.find(qn("w:rPr")).find(qn("w:i")) is not None
                              for r in runs)


def build_docx(md_path, template, out):
    header_tables, sections = parse(md_path.read_text(encoding="utf-8"))
    doc = Document(str(template))
    body = doc.element.body
    tables = {t._tbl: t for t in doc.tables}

    # Header: project information and group members (template rows are label | value).
    info = dict((r[0], r[1]) for r in header_tables[0][1][1:])
    for row in doc.tables[0].rows:
        label = row.cells[0].text.strip()
        if label in info:
            fill_cell(row.cells[1], info[label])
    fill_table(doc.tables[1], header_tables[1][1])

    elements = list(body.iterchildren())
    headings = [e for e in elements if e.tag == qn("w:p") and e.find(".//" + qn("w:pStyle")) is not None
                and e.find(".//" + qn("w:pStyle")).get(qn("w:val")) == "Heading1"]
    titles = ["".join(t.text for t in h.iter(qn("w:t"))).strip() for h in headings]
    by_title = dict(sections)
    for title in by_title:
        if title not in titles:
            raise SystemExit(f"section not in the template: {title}")

    for index, heading in enumerate(headings):
        title = titles[index]
        end = headings[index + 1] if index + 1 < len(headings) else body.find(qn("w:sectPr"))
        content, node = [], heading.getnext()
        while node is not None and node is not end:
            content.append(node)
            node = node.getnext()
        if title not in by_title:
            # Supervisor Approval: keep the table, drop the instruction.
            for el in content:
                if el.tag == qn("w:p") and is_instruction(el):
                    body.remove(el)
            continue
        template_tables = [tables[el] for el in content if el.tag == qn("w:tbl")]
        labels = {"".join(t.text for t in el.iter(qn("w:t"))).strip(): el for el in content if el.tag == qn("w:p")}
        for el in content:
            body.remove(el)
        anchor = heading
        for kind, value in by_title[title]:
            if kind == "table":
                table = template_tables.pop(0)
                fill_table(table, value)
                el = table._tbl
            elif kind == "label":
                el = copy.deepcopy(labels[value])
            else:
                el = new_paragraph(doc, value, kind)
            anchor.addnext(el)
            anchor = el
        if template_tables:
            raise SystemExit(f"unused template table in section: {title}")

    # Opening instruction ("Prepare this proposal together with ..."), grey but not italic.
    for p in list(body.iterchildren(qn("w:p"))):
        if "".join(t.text for t in p.iter(qn("w:t"))).startswith("Prepare this proposal"):
            body.remove(p)
    doc.save(str(out))


def export_pdf(docx, pdf):
    subprocess.run(["open", "-b", "com.apple.iWork.Pages", str(docx)], check=True)
    time.sleep(8)
    script = f'''
    tell application id "com.apple.iWork.Pages"
        export front document to (POSIX file "{pdf}") as PDF
        close front document saving no
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True, capture_output=True, timeout=180)


def main():
    out = PROPOSAL / "build"
    out.mkdir(exist_ok=True)
    docx = out / "proposal.docx"
    build_docx(PROPOSAL / "proposal.md", PROPOSAL / "template.docx", docx)
    if PAGES.exists():
        export_pdf(docx, out / "proposal.pdf")
    words = len(re.findall(r"\w+", (PROPOSAL / "proposal.md").read_text(encoding="utf-8")))
    print(f"about {words} words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
