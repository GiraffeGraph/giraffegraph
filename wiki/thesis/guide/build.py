"""Build the explainer for the team and outside readers: rehber.md -> build/rehber.pdf.

Run from this folder:
    uv run --no-project --python 3.12 --with markdown python build.py
The markers <!-- sekil:akis --> and <!-- sekil:graf --> in rehber.md are replaced by the two drawings
below. Google Chrome is required for the PDF.
"""

import re
import subprocess
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

NAVY, HONEY, BRONZE, SLATE, PAPER, LINE = "#1D2E47", "#E9AE3F", "#C4893A", "#6b7480", "#f8f6f1", "#d9dde2"


def box(x, y, w, h, title, sub, accent=False):
    stroke = HONEY if accent else LINE
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{PAPER if accent else "#fff"}" '
            f'stroke="{stroke}" stroke-width="{1.6 if accent else 1}"/>'
            f'<text x="{x + w / 2}" y="{y + h / 2 - 3}" text-anchor="middle" font-size="11" font-weight="600" fill="{NAVY}">{title}</text>'
            f'<text x="{x + w / 2}" y="{y + h / 2 + 12}" text-anchor="middle" font-size="9" fill="{SLATE}">{sub}</text>')


def arrow(x1, y1, x2, y2, color=NAVY):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.3" marker-end="url(#ok)"/>'


DEFS = (f'<defs><marker id="ok" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{NAVY}"/></marker></defs>')


def flow():
    steps = [("Hadis metni", "kaynak birimi"), ("Bölütleme", "isnad / metin"), ("Model önerir", "ad + alıntı"),
             ("Kontroller", "şema, alıntı, değer"), ("İnceleme", "kişi karar verir"), ("Bilgi grafı", "kabul kaydıyla")]
    w, h, gap, y = 104, 46, 18, 20
    parts = [DEFS]
    for i, (title, sub) in enumerate(steps):
        x = 6 + i * (w + gap)
        parts.append(box(x, y, w, h, title, sub, accent=title in ("Kontroller", "İnceleme")))
        if i < len(steps) - 1:
            parts.append(arrow(x + w, y + h / 2, x + w + gap - 2, y + h / 2))
    cx = 6 + 3 * (w + gap) + w / 2
    ix = 6 + 4 * (w + gap) + w / 2
    gx = 6 + 5 * (w + gap) + w / 2
    parts.append(f'<path d="M{cx},{y + h} C{cx},{y + h + 34} {gx},{y + h + 34} {gx},{y + h + 3}" fill="none" '
                 f'stroke="{SLATE}" stroke-width="1.1" stroke-dasharray="4 3" marker-end="url(#ok)"/>')
    parts.append(f'<text x="{(cx + gx) / 2}" y="{y + h + 40}" text-anchor="middle" font-size="9" fill="{SLATE}">'
                 f'kontrolden geçen öneri, adı kayıtlı bir kuralla kabul edilir</text>')
    parts.append(f'<text x="{ix}" y="{y - 6}" text-anchor="middle" font-size="9" fill="{BRONZE}">işaretlenen öneri silinmez, buraya gelir</text>')
    width = 6 + 6 * (w + gap) - gap + 6
    return f'<svg class="fig" viewBox="0 0 {width} 112" xmlns="http://www.w3.org/2000/svg" font-family="Inter, Arial, sans-serif">{"".join(parts)}</svg>'


def graph():
    names = [("el-Humeydî", "الحميدي"), ("Süfyân", "سفيان"), ("Yahyâ b. Saîd", "يحيى بن سعيد"),
             ("M. b. İbrâhîm et-Teymî", "محمد بن إبراهيم"), ("Alkame b. Vakkâs", "علقمة بن وقاص"), ("Ömer b. el-Hattâb", "عمر بن الخطاب")]
    w, h, gap, y = 104, 50, 18, 16
    parts = [DEFS]
    for i, (latin, arabic) in enumerate(names):
        x = 6 + i * (w + gap)
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="25" fill="#fff" stroke="{NAVY}" stroke-width="1.1"/>'
                     f'<text x="{x + w / 2}" y="{y + 21}" text-anchor="middle" font-size="12.5" fill="{NAVY}" '
                     f'font-family="Amiri, Geeza Pro, serif" direction="rtl">{arabic}</text>'
                     f'<text x="{x + w / 2}" y="{y + 38}" text-anchor="middle" font-size="8.6" fill="{SLATE}">{latin}</text>')
        if i < len(names) - 1:
            parts.append(arrow(x + w, y + h / 2, x + w + gap - 2, y + h / 2, HONEY))
    parts.append(f'<rect x="132" y="{y + h + 16}" width="480" height="34" rx="5" fill="{PAPER}" stroke="{LINE}"/>'
                 f'<text x="372" y="{y + h + 30}" text-anchor="middle" font-size="9.5" fill="{NAVY}">Her ok: "ondan rivayet etti" (NARRATED_FROM)</text>'
                 f'<text x="372" y="{y + h + 44}" text-anchor="middle" font-size="9" fill="{SLATE}">'
                 f'kimliği: hadis numarası + zincir numarası + zincirdeki sıra, kabul kaydıyla birlikte</text>')
    width = 6 + 6 * (w + gap) - gap + 6
    return f'<svg class="fig" viewBox="0 0 {width} 124" xmlns="http://www.w3.org/2000/svg" font-family="Inter, Arial, sans-serif">{"".join(parts)}</svg>'


ARABIC_RUN = re.compile(r"[؀-ۿ][؀-ۿ\s،]*[؀-ۿ]|[؀-ۿ]")


def arabic_spans(rendered):
    """Arabic inside Turkish prose: a code span with Arabic is one right-to-left unit (its | separators keep
    the narrator order); a loose Arabic run gets the Arabic font and its own direction. SVG is left alone."""
    out = []
    for piece in re.split(r"(<svg.*?</svg>|<code>[^<]*</code>)", rendered, flags=re.S):
        if piece.startswith("<svg"):
            out.append(piece)
        elif piece.startswith("<code>") and ARABIC_RUN.search(piece):
            out.append(f'<bdi dir="rtl"><code class="ar">{piece[6:-7]}</code></bdi>')
        elif piece.startswith("<code>"):
            out.append(piece)
        else:
            out.append(ARABIC_RUN.sub(lambda m: f'<bdi class="ar" dir="rtl">{m.group(0)}</bdi>', piece))
    return "".join(out)


STYLE = f"""
@font-face {{ font-family: "Copernicus"; src: url("../assets/GalaxieCopernicus-Book.woff2") format("woff2"); }}
@page {{ size: A4; margin: 16mm 18mm 15mm; }}
* {{ box-sizing: border-box; }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ margin: 0; background: #fff; color: #24344c; font: 10pt/1.55 "Inter", "Helvetica Neue", Arial, sans-serif; }}
header {{ display: flex; align-items: center; gap: 9pt; padding-bottom: 7pt; border-bottom: 1.4pt solid {HONEY}; }}
header img {{ width: 28pt; height: 28pt; }}
header .name {{ font: 16pt/1 "Copernicus", Georgia, serif; color: {NAVY}; }}
header .meta {{ margin-left: auto; text-align: right; font-size: 8pt; color: {SLATE}; line-height: 1.35; }}
h1 {{ font: 20pt/1.2 "Copernicus", Georgia, serif; color: {NAVY}; margin: 16pt 0 4pt; }}
h1 + p em {{ color: {SLATE}; font-size: 9pt; }}
h2 {{ font: 13pt/1.3 "Copernicus", Georgia, serif; color: {NAVY}; margin: 18pt 0 5pt; padding-left: 8pt;
      border-left: 2.6pt solid {HONEY}; break-after: avoid; }}
h3 {{ font: 11pt/1.3 "Copernicus", Georgia, serif; color: {NAVY}; margin: 11pt 0 3pt; break-after: avoid; }}
p {{ margin: 0 0 7pt; orphans: 3; widows: 3; }}
ul, ol {{ margin: 2pt 0 8pt; padding-left: 17pt; }}
li {{ margin-bottom: 3pt; }}
li::marker {{ color: {BRONZE}; font-weight: 600; }}
strong {{ color: {NAVY}; font-weight: 600; }}
em {{ color: inherit; }}
table {{ width: 100%; border-collapse: collapse; margin: 5pt 0 10pt; font-size: 8.9pt; line-height: 1.42; }}
th {{ text-align: left; color: {NAVY}; font-weight: 600; border-bottom: 1.1pt solid {HONEY}; padding: 4pt 6pt; }}
td {{ border-bottom: 0.5pt solid {LINE}; padding: 4pt 6pt; vertical-align: top; }}
tr {{ break-inside: avoid; }}
blockquote {{ margin: 7pt 0; padding: 6pt 10pt; background: {PAPER}; border-left: 2.6pt solid {HONEY}; }}
blockquote p {{ margin: 0 0 3pt; }}
code {{ font: 8.8pt "Menlo", monospace; background: #f3f1ec; padding: 0 2pt; border-radius: 2pt; }}
.ar {{ font: 12.5pt/1.55 "Amiri", "Geeza Pro", serif; color: {NAVY}; }}
code.ar {{ font: 12pt/1.7 "Amiri", "Geeza Pro", serif; background: #f3f1ec; }}
svg.fig {{ width: 100%; height: auto; margin: 6pt 0 2pt; }}
footer {{ margin-top: 14pt; padding-top: 6pt; border-top: 0.6pt solid {LINE}; font-size: 7.8pt; color: {SLATE}; }}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">')

HEADER = """<header><img src="../assets/logo.png" alt=""><span class="name">GiraffeGraph</span>
<div class="meta">Akdeniz Üniversitesi, Bilgisayar Mühendisliği<br>CSE 491 Bitirme Projesi · TÜBİTAK 2209-A</div></header>"""

FOOTER = """<footer>Yahya Efe Kuruçay · Deniz Büyükşahin · Alperen Ulukaya · Danışman: Arş. Gör. Dr. Taha Yiğit Alkan · Alan uzmanı: Prof. Dr. Rifat Atay</footer>"""


def main():
    text = (HERE / "rehber.md").read_text(encoding="utf-8")
    for marker in ("<!-- sekil:akis -->", "<!-- sekil:graf -->"):
        if marker not in text:
            raise SystemExit(f"missing figure marker {marker}")
    body = markdown.markdown(text, extensions=["tables", "sane_lists"])
    body = body.replace("<!-- sekil:akis -->", flow()).replace("<!-- sekil:graf -->", graph())
    body = arabic_spans(body)
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    BUILD.mkdir(exist_ok=True)
    html_path = BUILD / "rehber.html"
    html_path.write_text(f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>{title}</title>{FONTS}'
                         f'<style>{STYLE}</style></head><body>{HEADER}{body}{FOOTER}</body></html>', encoding="utf-8")
    if CHROME.exists():
        subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=10000",
                        f"--print-to-pdf={BUILD / 'rehber.pdf'}", html_path.as_uri()], check=True, capture_output=True)
    print(BUILD / "rehber.pdf", len(re.findall(r"\w+", text)), "words")


if __name__ == "__main__":
    main()
