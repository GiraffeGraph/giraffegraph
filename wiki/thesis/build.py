"""Assemble the report: number citations, build the reference list, draw figures, export.

Usage (from this directory):
    uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build.py

Outputs: figures/*.png, build/thesis.md, build/thesis.docx, build/thesis.html, build/thesis.pdf
(the PDF needs Google Chrome; it is skipped when Chrome is not installed).
"""

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
RESULTS = WORKSPACE / "giraffegraph-core" / "evaluation" / "results"
BIB_FILES = [
    WORKSPACE / "wiki" / "sources" / "claude-science-results" / "04b_dogrulanmis_kaynakca.bib",
    WORKSPACE / "wiki" / "literature" / "extraction_eval_precedents.bib",
]
INTERNAL = {
    "internal-cache-ledger": (
        'Y. E. Kuruçay, "The Cache and the Ledger," project essay, GiraffeGraph workspace, '
        "`data/cache-and-ledger/README.md`, 2026 (unpublished)."
    ),
    "internal-data-manifest": (
        "GiraffeGraph project, data manifest: sources, licence statements and construction of the "
        "evaluation sets, `data/README.md`, 12 October 2026 (unpublished)."
    ),
}
ARABIC_CODE = re.compile(r"`([^`\n]*[\u0600-\u06FF][^`\n]*)`")
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def parse_bib(text):
    entries = {}
    position = 0
    while True:
        match = re.search(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text[position:])
        if not match:
            return entries
        start = position + match.end()
        depth = 1
        index = start
        while index < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[index], 0)
            index += 1
        body = text[start : index - 1]
        fields = {"ENTRYTYPE": match.group(1).lower()}
        cursor = 0
        while True:
            field = re.search(r"([A-Za-z_]+)\s*=\s*", body[cursor:])
            if not field:
                break
            value_start = cursor + field.end()
            opener = body[value_start : value_start + 1]
            if opener == "{":
                level = 1
                end = value_start + 1
                while end < len(body) and level:
                    level += {"{": 1, "}": -1}.get(body[end], 0)
                    end += 1
                value = body[value_start + 1 : end - 1]
            elif opener == '"':
                end = body.index('"', value_start + 1) + 1
                value = body[value_start + 1 : end - 1]
            else:
                stop = re.search(r"[,\n]", body[value_start:])
                end = value_start + (stop.start() if stop else len(body) - value_start)
                value = body[value_start:end]
            fields[field.group(1).lower()] = clean(value)
            cursor = end
        entries[match.group(2)] = fields
        position = index


def clean(value):
    value = re.sub(r"<scp>|</scp>", "", value)
    value = value.replace("---", "—").replace("--", "–").replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", value).strip()


def authors(raw):
    names = []
    for person in re.split(r"\s+and\s+", raw):
        if "," in person:
            last, first = [part.strip() for part in person.split(",", 1)]
        else:
            parts = person.split()
            last, first = parts[-1], " ".join(parts[:-1])
        initials = " ".join(f"{name[0]}." for name in first.replace("-", " ").split() if name)
        names.append(f"{initials} {last}".strip())
    if len(names) > 6:
        return f"{names[0]} et al."
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    if len(names) > 2:
        return ", ".join(names[:-1]) + ", and " + names[-1]
    return names[0]


def format_entry(fields):
    parts = []
    if fields.get("author"):
        parts.append(authors(fields["author"]) + ",")
    title = fields.get("title", "").rstrip(".")
    kind = fields["ENTRYTYPE"]
    if kind == "book":
        parts.append(f"*{title}*.")
    else:
        parts.append(f'"{title},"')
    if kind == "article" and fields.get("journal"):
        venue = f"*{fields['journal']}*"
        if fields.get("volume"):
            venue += f", vol. {fields['volume']}"
        if fields.get("number"):
            venue += f", no. {fields['number']}"
        if fields.get("pages"):
            venue += f", pp. {fields['pages']}"
        parts.append(venue + ",")
    elif kind in ("inproceedings", "inbook") and fields.get("booktitle"):
        venue = f"in *{fields['booktitle']}*"
        if fields.get("pages"):
            venue += f", pp. {fields['pages']}"
        parts.append(venue + ",")
    elif kind == "mastersthesis":
        parts.append(f"M.S. thesis, {fields.get('school', '')},")
    elif fields.get("eprint"):
        parts.append(f"arXiv:{fields['eprint']},")
    elif fields.get("publisher"):
        parts.append(f"{fields['publisher']},")
    parts.append(f"{fields.get('year', 'n.d.')}.")
    if fields.get("doi"):
        parts.append(f"doi:{fields['doi']}")
    elif fields.get("url"):
        parts.append(fields["url"])
    return " ".join(parts)


def load_references():
    entries = {}
    for path in BIB_FILES:
        entries.update(parse_bib(path.read_text(encoding="utf-8")))
    return entries


def assemble(entries):
    order = []

    def replace(match):
        numbers = []
        for key in re.split(r"\s*;\s*", match.group(1)):
            key = key.strip().lstrip("@")
            if key not in entries and key not in INTERNAL:
                raise SystemExit(f"unknown citation key: {key}")
            if key not in order:
                order.append(key)
            numbers.append(order.index(key) + 1)
        return "[" + ", ".join(str(number) for number in sorted(numbers)) + "]"

    chapters = sorted((HERE / "chapters").glob("*.md"))
    body_parts, appendix_parts = [], []
    for chapter in chapters:
        text = chapter.read_text(encoding="utf-8")
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
        text = re.sub(r"\[(@[^\]]+)\]", replace, text)
        text = ARABIC_CODE.sub(lambda match: f"[{match.group(1)}]{{lang=ar dir=rtl}}", text)
        (appendix_parts if chapter.name.startswith("10-") else body_parts).append(text)

    references = ["# References", ""]
    for number, key in enumerate(order, start=1):
        entry = INTERNAL.get(key) or format_entry(entries[key])
        references.append(f"[{number}] {entry}")
        references.append("")
    document = "\n\n".join(body_parts + ["\n".join(references)] + appendix_parts) + "\n"
    return document, order


def load(run, analysis="analysis-ifta"):
    return json.loads((RESULTS / run / analysis / "analysis.json").read_text(encoding="utf-8"))


def figures():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    (HERE / "figures").mkdir(exist_ok=True)
    runs = [
        ("Rule", "2026-10-12-sixbooks300/rule"),
        ("LLM,\nschema only", "2026-10-12-sixbooks300/haiku-llm_schema_whole"),
        ("LLM,\nisnad-aware", "2026-10-12-sixbooks300/haiku-llm_isnad_whole"),
        ("LLM, isnad-aware,\nper chain", "2026-10-12-sixbooks300/haiku-llm_isnad_chain"),
    ]
    scores = [load(run)["scores"]["proposed"]["M2"] for _, run in runs]
    colours = {"precision": "#4c72b0", "recall": "#dd8452", "f1": "#55a868"}

    figure, axis = plt.subplots(figsize=(7.2, 3.6), dpi=200)
    width = 0.26
    for offset, metric in enumerate(("precision", "recall", "f1")):
        values = [score[metric] for score in scores]
        positions = [index + (offset - 1) * width for index in range(len(runs))]
        errors = None
        if metric == "f1":
            errors = [
                [score["f1"] - score["ci95"]["f1"][0] for score in scores],
                [score["ci95"]["f1"][1] - score["f1"] for score in scores],
            ]
        bars = axis.bar(
            positions, values, width, label=metric.capitalize() if metric != "f1" else "F1",
            color=colours[metric], yerr=errors, capsize=3,
        )
        for bar, value in zip(bars, values):
            axis.text(bar.get_x() + bar.get_width() / 2, value + 0.012, f"{value:.3f}",
                      ha="center", va="bottom", fontsize=6.5)
    axis.set_xticks(range(len(runs)))
    axis.set_xticklabels([label for label, _ in runs], fontsize=8)
    axis.set_ylim(0.8, 1.03)
    axis.set_ylabel("Loose matching, 300 hadiths")
    axis.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=8, frameon=False)
    axis.spines[["top", "right"]].set_visible(False)
    figure.tight_layout()
    figure.savefig(HERE / "figures" / "fig-7-1-conditions.png")
    plt.close(figure)

    gate = load("2026-10-12-sixbooks300/haiku-llm_schema_whole")["gate_table"]
    row = next(item for item in gate["rows"] if item["gate"] == "value_not_in_quote")
    correct_unflagged = gate["correct"] - row["false_alarms"]
    figure, axis = plt.subplots(figsize=(7.2, 1.7), dpi=200)
    segments = [
        ("Matched, not flagged", correct_unflagged, "#55a868"),
        ("Matched, flagged", row["false_alarms"], "#ccb974"),
        ("Not matched, flagged", row["errors_caught"], "#c44e52"),
        ("Not matched, not flagged", row["errors_missed"], "#8c8c8c"),
    ]
    left = 0
    for label, value, colour in segments:
        axis.barh([0], [value], left=left, color=colour, label=f"{label}: {value:,}")
        left += value
    axis.set_yticks([])
    axis.set_xlim(0, left)
    axis.set_xlabel("Proposed narrator mentions (schema-only condition)")
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2, fontsize=8, frameon=False)
    axis.spines[["top", "right", "left"]].set_visible(False)
    figure.tight_layout()
    figure.savefig(HERE / "figures" / "fig-7-2-gate.png")
    plt.close(figure)

    histogram = load("2026-10-12-sixbooks300/haiku-llm_schema_whole")["confidence"]["histogram"]
    bins = [item for item in histogram if item["correct"] + item["wrong"]]
    figure, axis = plt.subplots(figsize=(7.2, 3.0), dpi=200)
    labels = [f"{item['from']:.1f}–{item['to']:.1f}" for item in bins]
    axis.bar(labels, [item["correct"] for item in bins], color="#55a868", label="Matched")
    axis.bar(labels, [item["wrong"] for item in bins], bottom=[item["correct"] for item in bins],
             color="#c44e52", label="Not matched")
    for index, item in enumerate(bins):
        axis.text(index, item["correct"] + item["wrong"] + 12, f"{item['wrong']} not matched",
                  ha="center", fontsize=7)
    axis.set_xlabel("Model confidence")
    axis.set_ylabel("Mentions")
    axis.legend(fontsize=8, frameon=False)
    axis.spines[["top", "right"]].set_visible(False)
    figure.tight_layout()
    figure.savefig(HERE / "figures" / "fig-7-3-confidence.png")
    plt.close(figure)


CSS = """
body { font-family: Georgia, 'Times New Roman', serif; font-size: 11pt; line-height: 1.45;
       max-width: 720px; margin: 2em auto; padding: 0 1em; color: #111; }
h1 { font-size: 18pt; margin-top: 2.2em; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; font-size: 20pt; }
h2 { font-size: 13.5pt; margin-top: 1.6em; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 1em 0; }
th, td { border: 1px solid #999; padding: 3px 6px; vertical-align: top; text-align: left; }
th { background: #eee; }
code, pre { font-family: Menlo, Consolas, monospace; font-size: 8.5pt; }
pre { background: #f5f5f5; padding: 8px; overflow-x: auto; white-space: pre-wrap; }
img { max-width: 100%; display: block; margin: 1em auto 0.3em; }
span[lang=ar] { font-family: 'Geeza Pro', 'Noto Naskh Arabic', 'Amiri', serif; font-size: 12.5pt; }
figcaption, p > img + em { font-size: 9pt; }
#TOC { page-break-after: always; }
#TOC ul { list-style: none; padding-left: 1.2em; }
@page { size: A4; margin: 22mm 20mm; }
"""


def export(document):
    build = HERE / "build"
    build.mkdir(exist_ok=True)
    markdown = build / "thesis.md"
    markdown.write_text(document, encoding="utf-8")
    try:
        import pypandoc
    except ImportError:
        print("pypandoc not available: wrote build/thesis.md only")
        return
    common = ["--from=markdown+pipe_tables+implicit_figures-smart", "--toc", "--toc-depth=2",
              f"--resource-path={HERE}", "--metadata=title:GiraffeGraph senior design report"]
    pypandoc.convert_file(str(markdown), "docx", outputfile=str(build / "thesis.docx"),
                          extra_args=common)
    css = build / "thesis.css"
    css.write_text(CSS, encoding="utf-8")
    pypandoc.convert_file(
        str(markdown), "html5", outputfile=str(build / "thesis.html"),
        extra_args=common + ["--standalone", "--embed-resources", f"--css={css}"],
    )
    if CHROME.exists():
        subprocess.run(
            [str(CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={build / 'thesis.pdf'}", (build / "thesis.html").as_uri()],
            check=True, capture_output=True, timeout=180,
        )


def main():
    entries = load_references()
    figures()
    document, order = assemble(entries)
    export(document)
    words = len(re.findall(r"\w+", document))
    print(f"{len(order)} references, about {words} words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
