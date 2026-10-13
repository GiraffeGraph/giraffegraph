"""Deterministic isnad parser + mention-matching metrics for the GiraffeGraph pilot.

Scope: Arabic hadith text (Sanadset 650K, CC0). No LLM. Two jobs:
  1. rule_parse(raw)  -> ordered list of narrator-mention strings
  2. score(ref, hyp)  -> mention-level P/R/F1 under strict and lenient matching,
                         plus chain-order and ungrounded-mention diagnostics
"""
import re
import unicodedata
import numpy as np
from scipy.optimize import linear_sum_assignment

# ---------------------------------------------------------------- normalisation
HARAKAT = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]")
PUNCT = re.compile(r"[،.؛:!؟\"'()\[\]{}«»\-–—/\\*·]")


def norm(s: str) -> str:
    """Diacritic- and orthography-insensitive Arabic form used for matching."""
    s = unicodedata.normalize("NFKC", s)
    s = HARAKAT.sub("", s)
    s = PUNCT.sub(" ", s)
    s = re.sub(r"[أإآٱ]", "ا", s)
    s = s.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    s = re.sub(r"\s+", " ", s).strip()
    return s


HONORIFIC = re.compile(
    r"(رضي الله عنهما|رضي الله عنها|رضي الله عنهم|رضي الله عنه|"
    r"صلى الله عليه وسلم|عليه السلام|عليها السلام|رحمه الله|"
    r"ام المومنين|المومنين)"
)
# leading conjunction / siga residue that Sanadset itself sometimes keeps
LEAD_JUNK = re.compile(r"^(و|ف|ثم|قال|قالت|يقول|انه|انها|ان)\s+")


def clean_mention(s: str) -> str:
    s = norm(s)
    s = HONORIFIC.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    for _ in range(3):
        s2 = LEAD_JUNK.sub("", s)
        if s2 == s:
            break
        s = s2
    return s.strip()


# ------------------------------------------------------------------ siga lexicon
# Transmission verbs (tahammul/ada' formulae). Order matters: longest first.
SIGA = [
    "حدثنا", "حدثني", "حدثناه", "حدثنيه", "اخبرنا", "اخبرني", "انبانا", "انباني",
    "نبانا", "نباني", "حدثهم", "حدثه", "اخبرهم", "اخبره", "سمعت", "سمعنا",
    "قرات علي", "قرا علينا", "عرضت علي", "كتب الي", "فيما قرا", "ذكر لنا",
    "ثنا", "انا", "عن", "ان",
]
SIGA_RE = re.compile(r"(?:^|\s)(" + "|".join(sorted(SIGA, key=len, reverse=True)) + r")(?=\s|$)")

# Markers that the chain has ended and the matn has begun.
MATN_CUE = re.compile(
    r"(رسول الله|النبي|صلي الله عليه وسلم|قال\s*:|قالت\s*:|"
    r"انه قال|انها قالت|يقول\s*:|سالت|بلغه|نهي|امر\s*ب)"
)
# tahwil marker: a bare 'ح' separating parallel chains
TAHWIL = re.compile(r"(?:^|\s)ح(?=\s|$)")

STOP_TOKENS = {
    "الله", "رسول", "النبي", "قال", "قالت", "قالوا", "يقول", "انه", "انها",
    "ان", "عن", "في", "علي", "الي", "من", "مثله", "بهذا", "الاسناد", "نحوه",
    "جميعا", "كلاهما", "كلهم", "وهو", "يعني", "هو", "بن", "بنت",
}


def _looks_like_name(tok_list) -> bool:
    if not tok_list:
        return False
    content = [t for t in tok_list if t not in STOP_TOKENS]
    return len(content) >= 1


def rule_parse(raw: str, max_mentions: int = 40):
    """Sigha-driven isnad segmentation. Returns ordered narrator mentions."""
    text = norm(raw)
    # keep every parallel chain: split on tahwil, parse each side
    chunks = [c for c in TAHWIL.split(text) if c.strip()]
    out = []
    for chunk in chunks:
        # cut the chunk at the first matn cue that follows at least one siga
        first_siga = SIGA_RE.search(chunk)
        if first_siga is None:
            continue
        cue = MATN_CUE.search(chunk, first_siga.end())
        isnad = chunk[: cue.start()] if cue else chunk
        tail = chunk[cue.start():] if cue else ""
        # a second isnad can start inside the tail (new hadith / follow-up chain)
        pieces = [isnad]
        while tail:
            nxt = SIGA_RE.search(tail)
            if nxt is None:
                break
            sub = tail[nxt.start():]
            cue2 = MATN_CUE.search(sub, nxt.end() - nxt.start())
            pieces.append(sub[: cue2.start()] if cue2 else sub)
            tail = sub[cue2.start():] if cue2 else ""
        for piece in pieces:
            spans = [m.span(1) for m in SIGA_RE.finditer(piece)]
            for i, (s, e) in enumerate(spans):
                nxt_start = spans[i + 1][0] if i + 1 < len(spans) else len(piece)
                cand = piece[e:nxt_start]
                # 'و' introduces a co-narrator: split it out as its own mention
                for part in re.split(r"(?:^|\s)و(?=\s)", cand):
                    m = clean_mention(part)
                    toks = m.split()
                    if not _looks_like_name(toks):
                        continue
                    if len(toks) > 9:
                        toks = toks[:9]
                    out.append(" ".join(toks))
    # drop immediate repeats, cap length
    dedup = []
    for m in out:
        if not dedup or dedup[-1] != m:
            dedup.append(m)
    return dedup[:max_mentions]


# ------------------------------------------------------------------- matching
def tok_f1(a: str, b: str) -> float:
    A, B = set(a.split()) - STOP_TOKENS, set(b.split()) - STOP_TOKENS
    if not A or not B:
        A, B = set(a.split()), set(b.split())
    if not A or not B:
        return 0.0
    inter = len(A & B)
    if inter == 0:
        return 0.0
    p, r = inter / len(A), inter / len(B)
    return 2 * p * r / (p + r)


def sim(a: str, b: str, mode: str) -> float:
    if mode == "strict":
        return 1.0 if a == b else 0.0
    # lenient: substring containment or token-F1 >= .6
    if a == b:
        return 1.0
    if a and b and (a in b or b in a):
        return 0.9
    f = tok_f1(a, b)
    return f if f >= 0.60 else 0.0


def align(ref, hyp, mode):
    if not ref or not hyp:
        return [], 0.0
    M = np.zeros((len(ref), len(hyp)))
    for i, a in enumerate(ref):
        for j, b in enumerate(hyp):
            M[i, j] = sim(a, b, mode)
    ri, ci = linear_sum_assignment(-M)
    pairs = [(i, j) for i, j in zip(ri, ci) if M[i, j] > 0]
    return pairs, float(sum(M[i, j] for i, j in pairs))


def score_one(ref_raw, hyp_raw, source_raw, mode="lenient"):
    ref = [clean_mention(x) for x in ref_raw]
    hyp = [clean_mention(x) for x in hyp_raw]
    ref = [x for x in ref if x]
    hyp = [x for x in hyp if x]
    pairs, _ = align(ref, hyp, mode)
    tp = len(pairs)
    src = norm(source_raw)
    ungrounded = sum(1 for h in hyp if h and h not in src and tok_f1_in(h, src) < 0.9)
    # order: Kendall-style concordance over matched pairs
    order_ok = order_concordance(pairs)
    return {
        "n_ref": len(ref), "n_hyp": len(hyp), "tp": tp,
        "fp": len(hyp) - tp, "fn": len(ref) - tp,
        "ungrounded": ungrounded,
        "order_conc": order_ok,
        "pairs": pairs, "ref": ref, "hyp": hyp,
    }


def tok_f1_in(mention: str, src: str) -> float:
    toks = [t for t in mention.split() if t not in STOP_TOKENS]
    if not toks:
        return 0.0
    return sum(1 for t in toks if t in src) / len(toks)


def order_concordance(pairs):
    if len(pairs) < 2:
        return None
    seq = [j for _, j in sorted(pairs)]
    conc = dis = 0
    for a in range(len(seq)):
        for b in range(a + 1, len(seq)):
            if seq[b] > seq[a]:
                conc += 1
            else:
                dis += 1
    tot = conc + dis
    return conc / tot if tot else None


def aggregate(per_item):
    tp = sum(d["tp"] for d in per_item)
    fp = sum(d["fp"] for d in per_item)
    fn = sum(d["fn"] for d in per_item)
    ung = sum(d["ungrounded"] for d in per_item)
    nhyp = sum(d["n_hyp"] for d in per_item)
    P = tp / (tp + fp) if tp + fp else 0.0
    R = tp / (tp + fn) if tp + fn else 0.0
    F1 = 2 * P * R / (P + R) if P + R else 0.0
    F05 = (1.25 * P * R / (0.25 * P + R)) if (0.25 * P + R) else 0.0
    oc = [d["order_conc"] for d in per_item if d["order_conc"] is not None]
    return {"P": P, "R": R, "F1": F1, "F0.5": F05, "tp": tp, "fp": fp, "fn": fn,
            "ungrounded": ung, "ungrounded_rate": ung / nhyp if nhyp else 0.0,
            "order_conc": float(np.mean(oc)) if oc else None, "n_hyp": nhyp}


def bootstrap_ci(per_item, stat="F1", B=2000, seed=7):
    rng = np.random.default_rng(seed)
    n = len(per_item)
    vals = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        vals.append(aggregate([per_item[i] for i in idx])[stat])
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))
