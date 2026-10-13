"""Shared helpers for the data/scripts builders. Standard library only.

Nothing here is imported from the scorer; `normalise` reimplements the simple
part of its normalisation (diacritics, tatweel, alef/ya/ta-marbuta folding,
punctuation, whitespace) so label checks do not depend on scorer internals.
"""
import difflib
import hashlib
import json
import re
import unicodedata

SEED = 20261012

# ASCII collection key -> book title in each corpus.
COLLECTIONS = {
    "Bukhari": {"ifta_file": "sahih-al-bukhari.json", "sanadset_book": "صحيح البخاري"},
    "Muslim": {"ifta_file": "sahih-muslim.json", "sanadset_book": "صحيح مسلم"},
    "AbuDawud": {"ifta_file": "sunan-abi-dawud.json", "sanadset_book": "سنن أبي داود"},
    "Tirmidhi": {"ifta_file": "jami-al-tirmidhi.json", "sanadset_book": "جامع الترمذي"},
    "Nasai": {"ifta_file": "sunan-al-nasai.json", "sanadset_book": "سنن النسائى الصغرى"},
    "IbnMajah": {"ifta_file": "sunan-ibn-majah.json", "sanadset_book": "سنن ابن ماجه"},
}

DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
PUNCT = re.compile(r"[،.؛:!؟?\"'()\[\]{}«»\-–—/\\*·,;_]")
TAG = re.compile(r"<[^<>]*>")
PAGE_MARKER = re.compile(r"\[\s*\d+\s*/\s*\d+\s*\]")
# Print numbering of the edition: "15 - ", "99 (م) - ", "2953 (م 1) - ", "6 / 1 - ", "( 48 )", "408 409 ". The
# Arabic text itself has no ASCII digits.
_DASH = r"(?:\s*[-–](?=\s))?"
NUMBER_MARKER = re.compile(
    r"\d+(?:\s*/\s*\d+)*(?:\s*\(\s*م\s*\d*\s*\))?" + _DASH + r"|\(\s*(?:م\s*\d*|\d+)\s*\)" + _DASH
)
LEADING_DASH = re.compile(r"^[-–]\s+")
EDGE_PUNCT = "،.؛:!؟?\"'()[]{}«»-–—,; \t\r\n"


def normalise(text):
    """Diacritic-, orthography- and punctuation-insensitive form of a string."""
    s = unicodedata.normalize("NFKC", text)
    s = DIACRITICS.sub("", s)
    s = PUNCT.sub(" ", s)
    s = re.sub(r"[أإآٱ]", "ا", s)
    s = s.replace("ى", "ي").replace("ة", "ه")
    return re.sub(r"\s+", " ", s).strip()


def normalise_for_matching(text):
    """`normalise` plus digit removal, for comparing texts across corpora."""
    return re.sub(r"\s+", " ", re.sub(r"\d+", " ", normalise(text))).strip()


def strip_tags(text):
    """Remove every <...> tag and any stray angle bracket, then tidy whitespace."""
    text = TAG.sub(" ", text)
    text = text.replace("<", " ").replace(">", " ")
    return re.sub(r"\s+", " ", text).strip()


def clean_ifta_text(text, first_mention=None):
    """Ifta hadith text without layout artefacts.

    Returns (cleaned, flags, heading). Page markers such as [1/220] and the
    edition's print numbers ("15 - ", "99 (م) - ", "2953 (م 1) - ", "6 / 1 - ", "( 48 )") are
    removed; line breaks and runs of whitespace become one space; a dash left at
    the very start is dropped. `flags` names the rules that changed this text.

    A record that opens a chapter carries the chapter title before the hadith's
    own print number ("بَابُ ... 22 - حَدَّثَنَا ..."). When `first_mention` (the
    first labelled narrator mention, cleaned) is given, everything before the
    last print number that precedes that mention is cut off and returned as
    `heading`. A title with no print number after it stays in the text.
    """
    flags = []
    out = PAGE_MARKER.sub(" ", text)
    if out != text:
        flags.append("page_marker")
    if "\r" in out or "\n" in out:
        flags.append("line_break")
    marked = NUMBER_MARKER.sub(" \x01 ", out)
    if marked != out:
        flags.append("print_number")
    marked = re.sub(r"\s+", " ", marked).strip()
    heading = ""
    if first_mention:
        mention_at = marked.find(first_mention)
        cut = marked.rfind("\x01", 0, mention_at) if mention_at > 0 else -1
        if cut >= 0:
            before = re.sub(r"\s+", " ", marked[:cut].replace("\x01", " ")).strip()
            if before.strip(EDGE_PUNCT):
                heading = before
                flags.append("chapter_heading")
                marked = marked[cut:]
    collapsed = re.sub(r"\s+", " ", marked.replace("\x01", " ")).strip()
    # Unnumbered records keep the separator of the missing number: "-  حدثنا ...".
    without_dash = LEADING_DASH.sub("", collapsed)
    if without_dash != collapsed:
        flags.append("leading_dash")
    return without_dash, flags, heading


def clean_ifta_mention(surface):
    """Ifta `names` surface form as a bare mention: same artefacts out, edge punctuation off."""
    out = NUMBER_MARKER.sub(" ", PAGE_MARKER.sub(" ", surface))
    out = re.sub(r"\s+", " ", out).strip()
    return out.strip(EDGE_PUNCT)


def similarity(a, b, long_block=20):
    """Character overlap of two strings.

    Returns (ratio, containment): ratio = 2*M/(len(a)+len(b)) with M the matched
    characters; containment = characters matched in blocks of at least
    `long_block` characters, divided by the shorter length.
    """
    if not a or not b:
        return 0.0, 0.0
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    blocks = matcher.get_matching_blocks()
    matched = sum(block.size for block in blocks)
    long_matched = sum(block.size for block in blocks if block.size >= long_block)
    return 2 * matched / (len(a) + len(b)), long_matched / min(len(a), len(b))


class TextIndex:
    """Finds the candidate texts closest to a query, by token-set Jaccard then character overlap."""

    def __init__(self, items):
        # items: list of (key, normalised text)
        self.items = items
        self.token_sets = [frozenset(text.split()) for _, text in items]

    def best(self, query, top_k=8):
        """Returns [(ratio, containment, key)] for the top_k Jaccard candidates, best ratio first."""
        q = frozenset(query.split())
        if not q:
            return []
        scored = []
        for idx, tokens in enumerate(self.token_sets):
            inter = len(q & tokens)
            if inter:
                scored.append((inter / (len(q) + len(tokens) - inter), inter / min(len(q), len(tokens)), idx))
        picked = {idx for _, _, idx in sorted(scored, reverse=True)[:top_k]}
        picked |= {idx for _, _, idx in sorted(scored, key=lambda x: (x[1], x[0]), reverse=True)[:top_k]}
        results = []
        for idx in picked:
            key, text = self.items[idx]
            ratio, containment = similarity(query, text)
            results.append((ratio, containment, key))
        return sorted(results, key=lambda x: (x[0], x[1]), reverse=True)


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def link_by_text(queries, candidates, threshold=0.9):
    """Link each query text to its closest candidate text of the same collection.

    queries / candidates: lists of dicts with `coll`, `raw` and an id under
    `key`. Returns one row per query with the best candidate, its ratio and
    containment, and `matched` (ratio >= threshold or equal normalised text).
    """
    indexes = {}
    for candidate in candidates:
        indexes.setdefault(candidate["coll"], []).append(
            (candidate["key"], normalise_for_matching(candidate["raw"]))
        )
    indexes = {coll: TextIndex(items) for coll, items in indexes.items()}
    rows = []
    for query in queries:
        index = indexes.get(query["coll"])
        results = index.best(normalise_for_matching(query["raw"])) if index else []
        if results:
            ratio, containment, key = results[0]
        else:
            ratio, containment, key = 0.0, 0.0, None
        rows.append({
            "key": query["key"],
            "best_candidate": key,
            "ratio": round(ratio, 4),
            "containment": round(containment, 4),
            "matched": ratio >= threshold,
            "candidates_at_or_above_threshold": sum(1 for r, _, _ in results if r >= threshold),
        })
    return rows
