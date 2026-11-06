"""Build the TÜBİTAK 2209-A form: cite author-year, add the reference list, export DOCX and PDF.

Citations and the reference list follow TÜBİTAK's "Bibliyografik Verilerin Düzenlenmesi"
(https://tubitak.gov.tr/tr/duyuru/bibliyografik-verilerin-duzenlenmesi): "(Öztürk vd., 2000; Demir,
2012)" in the text, the list sorted by surname, DOI at the end of every entry that has one.

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


# The frozen bib package keeps Crossref's title as delivered, footnote marker included.
TITLE_FIXES = {"Design Science in Information Systems Research1": "Design Science in Information Systems Research"}
# Crossref registers this article by article number with no page range; the bib's "1--27" has no source.
DROP_PAGES = {"10.1177/22104968261431425"}


def people(raw):
    """(surname, initials) for each author of a bib `author` field."""
    result = []
    for person in re.split(r"\s+and\s+", raw):
        if "," in person:
            last, first = [part.strip() for part in person.split(",", 1)]
        else:
            parts = person.split()
            last, first = parts[-1], " ".join(parts[:-1])
        initials = " ".join(f"{name[0]}." for name in first.replace("-", " ").split() if name)
        result.append((last, initials))
    return result


def cite_label(fields):
    surnames = [last for last, _ in people(fields["author"])]
    if len(surnames) == 1:
        return surnames[0]
    if len(surnames) == 2:
        return f"{surnames[0]} ve {surnames[1]}"
    return f"{surnames[0]} vd."


def format_tubitak(fields):
    names = ", ".join(f"{last}, {initials}".rstrip(", ") for last, initials in people(fields["author"]))
    title = TITLE_FIXES.get(fields.get("title", ""), fields.get("title", "")).rstrip(".")
    kind = fields["ENTRYTYPE"]
    parts = [f"{names.rstrip('.')}. {fields.get('year', 't.y.')}."]
    if kind == "book":
        parts.append(f"{title}.")
        if fields.get("publisher"):
            parts.append(f"{fields['publisher']}.")
    else:
        venue = ""
        if kind == "article" and fields.get("journal"):
            venue = fields["journal"]
            if fields.get("volume"):
                venue += f", {fields['volume']}"
                if fields.get("number"):
                    venue += f" ({fields['number']})"
        elif fields.get("booktitle"):
            venue = fields["booktitle"]
        elif fields.get("eprint"):
            venue = f"arXiv:{fields['eprint']} (ön baskı)"
        if fields.get("pages") and fields.get("doi") not in DROP_PAGES:
            venue += f", {fields['pages']}"
        parts.append(f'"{title}", {venue}.' if venue else f'"{title}".')
    if fields.get("doi"):
        parts.append(f"DOI: {fields['doi']}")
    elif fields.get("url"):
        parts.append(fields["url"])
    return " ".join(parts).replace("\\&", "&")


def assemble(entries):
    text = (FORM / "form.md").read_text(encoding="utf-8")
    text = re.sub(r"\A(# [^\n]*\n)\n(?:>[^\n]*\n)+", r"\1", text)
    text = text.split(NOTES_HEADING)[0].rstrip() + "\n"
    keys = []
    for match in re.finditer(r"\[(@[^\]]+)\]", text):
        for key in re.split(r"\s*;\s*", match.group(1)):
            key = key.strip().lstrip("@")
            if key not in entries:
                raise SystemExit(f"unknown citation key: {key}")
            if key not in keys:
                keys.append(key)
    keys.sort(key=lambda key: (people(entries[key]["author"])[0][0], entries[key].get("year", "")))

    # Same label and year twice gets a letter after the year (Öztürk 2000a, 2000b).
    years = {}
    for key in keys:
        years.setdefault((cite_label(entries[key]), entries[key].get("year", "")), []).append(key)
    year_of = {}
    for (_, year), group in years.items():
        for index, key in enumerate(group):
            year_of[key] = year + ("abcdefghij"[index] if len(group) > 1 else "")

    def replace(match):
        cited = [key.strip().lstrip("@") for key in re.split(r"\s*;\s*", match.group(1))]
        return "(" + "; ".join(f"{cite_label(entries[key])}, {year_of[key]}" for key in cited) + ")"

    text = re.sub(r"\[(@[^\]]+)\]", replace, text)
    references = "\n\n".join(format_tubitak({**entries[key], "year": year_of[key]}) for key in keys)
    if REFERENCES_MARKER not in text:
        raise SystemExit("references marker is missing from tubitak/form.md")
    return text.replace(REFERENCES_MARKER, references), keys


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
