"""Build the printed handouts for the domain expert: a one-page brief, the example sheet and the guideline.

Run from this folder:
    uv run --no-project --python 3.12 --with markdown python build.py
Writes build/brief.pdf, build/examples.pdf and build/guideline.pdf (Google Chrome is required for PDF).
"""

import csv
import html
import re
import subprocess
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
SHEET = HERE.parent / "hadiths_to_label.tsv"
GUIDELINE = HERE.parent / "GUIDELINE.md"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")

# Each example: hadith id from the sheet (None for the guideline's own example), the passages shown and the
# phrases highlighted. Passages and phrases are matched on the text without diacritics; the printed text keeps them.
EXAMPLES = [
    ("Nasai:374", ["أخبرنا قتيبة بن سعيد", "أنه سأل عائشة"], ["عن أبيه شريح"]),
    ("Tirmidhi:3204", ["حدثنا محمد بن بشار", "سمعت عمر بن الخطاب رضي الله عنه ، يقول"],
     ["عن أبيه", "ورواه بعضهم عن مالك مرسلا"], ["قال أبو عيسى", "مالك مرسلا ."]),
    ("AbuDawud:3122", ["حدثنا سليمان بن داود المهري", "عن أبي هريرة"],
     ["أو عبد العزيز بن محمد شك الشيخ", "يعني ابن محمد", " ح "]),
    ("AbuDawud:3307", ["حدثنا إبراهيم بن خالد", "فقال : خبيثة من الخبائث"], ["قال شيخ عنده : سمعت أبا هريرة"]),
    ("IbnMajah:1123", ["حدثنا أبو كريب", "عن جده"], ["عن أبيه ، عن جده", "جميعا", " ح "]),
    (None, ["عن نافع مولى ابن عمر", "عن نافع مولى ابن عمر"], ["مولى ابن عمر"]),
]


def plain_index(text):
    """Characters without diacritics, and for each of them its position in the original text."""
    keep = [(i, c) for i, c in enumerate(text) if not DIACRITICS.match(c)]
    return "".join(c for _, c in keep), [i for i, _ in keep]


def excerpt(text, start, end, phrases):
    plain, where = plain_index(text)
    a = plain.index(start)
    b = plain.index(end, a) + len(end)
    marks = []
    for phrase in phrases:
        pattern = r"(?<= )ح(?= )" if phrase == " ح " else re.escape(phrase)
        for match in re.finditer(pattern, plain[a:b]):
            marks.append((a + match.start(), a + match.end()))
    if not marks:
        raise ValueError(f"no highlighted phrase found in {start!r}")
    pieces, cursor = [], where[a]
    for s, e in sorted(marks):
        if where[s] < cursor:
            continue
        original_start, original_end = where[s], where[e - 1] + 1
        while original_end < len(text) and DIACRITICS.match(text[original_end]):
            original_end += 1
        pieces.append(html.escape(text[cursor:original_start]))
        pieces.append(f"<mark>{html.escape(text[original_start:original_end])}</mark>")
        cursor = original_end
    last = where[b - 1] + 1
    while last < len(text) and DIACRITICS.match(text[last]):
        last += 1
    pieces.append(html.escape(text[cursor:last]))
    return "".join(pieces)


def arabic_blocks():
    rows = {row["hadith_id"]: row["text"] for row in csv.DictReader(SHEET.open(encoding="utf-8"), delimiter="\t")}
    blocks = []
    for hadith, (start, end), phrases, *tail in EXAMPLES:
        text = rows[hadith] if hadith else "عن نافع مولى ابن عمر"
        block = excerpt(text, start, end, phrases)
        if tail:
            tail_start, tail_end = tail[0]
            block += " … " + excerpt(text, tail_start, tail_end, phrases)
        elif hadith:
            block += " …"
        blocks.append(block)
    return blocks


STYLE = """
@font-face { font-family: "Copernicus"; src: url("../assets/GalaxieCopernicus-Book.woff2") format("woff2"); }
:root { --navy: #1D2E47; --ink: #24344c; --bronze: #C4893A; --honey: #E9AE3F; --slate: #6b7480; --line: #d9dde2; }
@page { size: A4; margin: 15mm 18mm 14mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; background: #fff; color: var(--ink); font: 9.7pt/1.47 "Inter", "Helvetica Neue", Arial, sans-serif; }
header { display: flex; align-items: center; gap: 9pt; padding-bottom: 7pt; border-bottom: 1.4pt solid var(--honey); }
header img { width: 30pt; height: 30pt; }
header .name { font: 17pt/1 "Copernicus", Georgia, serif; color: var(--navy); }
header .meta { margin-left: auto; text-align: right; font-size: 8pt; color: var(--slate); line-height: 1.35; }
h1 { font: 15pt/1.25 "Copernicus", Georgia, serif; color: var(--navy); margin: 13pt 0 4pt; }
.lede { color: var(--slate); font-size: 8.8pt; margin: 0 0 6pt; }
h2 { font: 11.2pt/1.3 "Copernicus", Georgia, serif; color: var(--navy); margin: 11pt 0 3pt; padding-left: 7pt;
     border-left: 2.4pt solid var(--honey); }
h3 { font: 10.5pt/1.3 "Copernicus", Georgia, serif; color: var(--navy); margin: 0; }
p { margin: 0 0 5pt; }
ol { margin: 2pt 0 6pt; padding-left: 15pt; }
li { margin-bottom: 3pt; }
li::marker { color: var(--bronze); font-weight: 600; }
strong { color: var(--navy); font-weight: 600; }
footer { margin-top: 12pt; padding-top: 6pt; border-top: 0.6pt solid var(--line); font-size: 7.8pt; color: var(--slate);
         display: flex; justify-content: space-between; }
.example { border: 0.6pt solid var(--line); border-radius: 5pt; padding: 7pt 10pt 6pt; margin: 8pt 0; break-inside: avoid; }
.example .head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4pt; }
.example .source { font-size: 8pt; color: var(--slate); }
.arabic { direction: rtl; text-align: right; font: 13.5pt/1.95 "Amiri", "Geeza Pro", serif; color: var(--navy);
          background: #f8f6f1; border-radius: 3pt; padding: 3pt 8pt; margin: 0 0 5pt; }
mark { background: rgba(233, 174, 63, 0.28); color: inherit; border-bottom: 1pt solid var(--honey); padding: 0 1pt; }
.example p { margin-bottom: 3pt; }
.question { margin-top: 3pt; }
.question strong { color: var(--bronze); }
.guideline h1 { margin-top: 12pt; }
.guideline blockquote { margin: 6pt 0; padding: 5pt 9pt; background: #f8f6f1; border-left: 2.4pt solid var(--honey);
                        color: var(--ink); }
.guideline blockquote p { margin: 0 0 2pt; }
.ar { font: 12.5pt/1.5 "Amiri", "Geeza Pro", serif; color: var(--navy); }
code.ar { font: 12pt/1.6 "Amiri", "Geeza Pro", serif; background: #f3f1ec; }
code { font: 8.6pt "Menlo", "Amiri", "Geeza Pro", monospace; background: #f3f1ec; padding: 0 2pt; border-radius: 2pt; }
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Inter:wght@400;600&display=swap"'
         ' rel="stylesheet">')

HEADER = """<header><img src="../assets/logo.png" alt=""><span class="name">GiraffeGraph</span>
<div class="meta">Akdeniz Üniversitesi, Bilgisayar Mühendisliği<br>CSE 491 Bitirme Projesi · TÜBİTAK 2209-A</div></header>"""

FOOTER = """<footer><span>Yahya Efe Kuruçay · Deniz Büyükşahin · Alperen Ulukaya · Danışman: Dr. Taha Yiğit Alkan</span>
<span>{page}</span></footer>"""


def page(title, body, css_class=""):
    return (f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>{title}</title>{FONTS}'
            f'<style>{STYLE}</style></head><body class="{css_class}">{body}</body></html>')


ARABIC_RUN = re.compile(r"[\u0600-\u06FF][\u0600-\u06FF\s،]*[\u0600-\u06FF]|[\u0600-\u06FF]")


QUOTED_ARABIC = re.compile(r'(?:"|&quot;)(' + ARABIC_RUN.pattern + r')(?:"|&quot;)')


def arabic_spans(rendered):
    """Arabic phrases inside Turkish prose get the Arabic font and their own direction. Quotation marks around
    them are dropped: the script already sets them apart, and the marks land on the wrong side in mixed lines."""
    rendered = QUOTED_ARABIC.sub(lambda m: m.group(1), rendered)
    # A code span with Arabic is one right-to-left unit, so its separators (| and ||) keep the narrator order.
    pieces = re.split(r"(<code>[^<]*</code>)", rendered)
    out = []
    for piece in pieces:
        if piece.startswith("<code>") and ARABIC_RUN.search(piece):
            out.append(f'<bdi dir="rtl"><code class="ar">{piece[6:-7]}</code></bdi>')
        elif piece.startswith("<code>"):
            out.append(piece)
        else:
            out.append(ARABIC_RUN.sub(lambda m: f'<bdi class="ar" dir="rtl">{m.group(0)}</bdi>', piece))
    return "".join(out)


def render(text):
    return arabic_spans(markdown.markdown(text, extensions=["sane_lists"]))


def inline(text):
    return arabic_spans(html.escape(text))


def examples_html():
    text = (HERE / "examples.md").read_text(encoding="utf-8")
    parts = re.split(r"^### +Örnek +\d+\s*$", text, flags=re.M)[1:]
    blocks = arabic_blocks()
    if len(parts) != len(blocks):
        raise ValueError(f"examples.md has {len(parts)} examples, expected {len(blocks)}")
    cards = []
    for number, (part, arabic) in enumerate(zip(parts, blocks), start=1):
        lines = [line.strip() for line in part.strip().splitlines() if line.strip()]
        source = next(line for line in lines if line.startswith("**Kaynak:**"))[len("**Kaynak:**"):].strip()
        question = next(line for line in lines if line.startswith("**Soru:**"))[len("**Soru:**"):].strip()
        note = " ".join(line for line in lines if not line.startswith(("**Kaynak:**", "**Soru:**")))
        cards.append(f'<section class="example"><div class="head"><h3>Örnek {number}</h3>'
                     f'<span class="source">{html.escape(source)}</span></div>'
                     f'<div class="arabic">{arabic}</div><p>{inline(note)}</p>'
                     f'<p class="question"><strong>Soru:</strong> {inline(question)}</p></section>')
    intro = ('<h1>Kılavuzun açık soruları: örnekler</h1><p class="lede">Örnekler etiketlenecek 50 hadisten seçildi '
             '(Örnek 6 hariç). Vurgulanan yerler sorunun ilgili olduğu ifadelerdir; metinden alınan kısımlar '
             'kısaltılmıştır (…).</p>')
    return page("Örnekler", HEADER + intro + "".join(cards))


def guideline_html():
    text = GUIDELINE.read_text(encoding="utf-8")
    return page("Etiketleme kılavuzu", HEADER + '<div class="guideline">' + render(text) + "</div>", "guideline")


def brief_html():
    text = (HERE / "brief.md").read_text(encoding="utf-8")
    title = ('<h1>Hadis isnadı etiketleme çalışması için alan uzmanı desteği</h1>'
             '<p class="lede">Görüşme notu · Ekler: örnek sayfası ve etiketleme kılavuzu</p>')
    return page("Alan uzmanı desteği", HEADER + title + render(text) + FOOTER.format(page=""))


def main():
    BUILD.mkdir(exist_ok=True)
    for name, content in (("brief", brief_html()), ("examples", examples_html()), ("guideline", guideline_html())):
        (BUILD / f"{name}.html").write_text(content, encoding="utf-8")
        if CHROME.exists():
            subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            "--virtual-time-budget=8000", f"--print-to-pdf={BUILD / f'{name}.pdf'}",
                            (BUILD / f"{name}.html").as_uri()], check=True, capture_output=True)
        print(f"{name}: {BUILD / f'{name}.pdf'}")


if __name__ == "__main__":
    main()
