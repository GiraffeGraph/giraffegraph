"""Mention-level scorer for isnad (narrator chain) extraction.

Standalone on purpose: the matching criteria are part of the measurement
protocol and are frozen here, independent of any system under test. Standard
library only; nothing is imported from the application code.

Protocol (same normalisation, weights and threshold as the pilot,
wiki/sources/claude-science-results/pilot_isnad.py):
  M1 strict  normalised mention strings are equal.
  M2 loose   equal, or one contains the other, or content-token F1 >= 0.60.
  Alignment  maximum-weight bipartite matching per hadith (equal = 1,
             containment = 0.9, token overlap = its F1). Equal-weight ties are
             resolved towards more matched mentions, then towards pairs that
             keep chain order, so the result does not depend on solver order.
  Aggregate  micro-average over hadiths; 95% percentile bootstrap intervals
             resample hadiths, the unit of analysis.

Usage:
  python evaluation/scorer.py --system system.jsonl --reference reference.jsonl
      [--bootstrap 2000] [--seed 0] [--out report.json]
"""
import argparse
import json
import math
import random
import re
import sys
import unicodedata
from fractions import Fraction

CRITERIA = ("M1", "M2")
SUBSTRING_WEIGHT = Fraction(9, 10)
TOKEN_F1_THRESHOLD = Fraction(3, 5)

# ---------------------------------------------------------------- normalisation
HARAKAT = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
PUNCT = re.compile(r"[،.؛:!؟\"'()\[\]{}«»\-–—/\\*·]")
HONORIFIC = re.compile(
    r"(رضي الله عنهما|رضي الله عنها|رضي الله عنهم|رضي الله عنه|"
    r"صلى الله عليه وسلم|عليه السلام|عليها السلام|رحمه الله|"
    r"ام المومنين|المومنين)"
)
LEADING_PARTICLE = re.compile(r"^(و|ف|ثم|قال|قالت|يقول|انه|انها|ان)\s+")

# Function words that carry no identity; excluded from content-token overlap.
STOP_TOKENS = frozenset({
    "الله", "رسول", "النبي", "قال", "قالت", "قالوا", "يقول", "انه", "انها",
    "ان", "عن", "في", "علي", "الي", "من", "مثله", "بهذا", "الاسناد", "نحوه",
    "جميعا", "كلاهما", "كلهم", "وهو", "يعني", "هو", "بن", "بنت",
})


def normalise(mention: str) -> str:
    """Diacritic- and orthography-insensitive form of a mention."""
    s = unicodedata.normalize("NFKC", mention)
    s = HARAKAT.sub("", s)
    s = PUNCT.sub(" ", s)
    s = re.sub(r"[أإآٱ]", "ا", s)
    s = s.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    s = re.sub(r"\s+", " ", s).strip()
    s = HONORIFIC.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    for _ in range(3):
        stripped = LEADING_PARTICLE.sub("", s)
        if stripped == s:
            break
        s = stripped
    return s.strip()


# ------------------------------------------------------------------- similarity
def token_f1(a: str, b: str) -> Fraction:
    ta, tb = set(a.split()) - STOP_TOKENS, set(b.split()) - STOP_TOKENS
    if not ta or not tb:
        ta, tb = set(a.split()), set(b.split())
    if not ta or not tb:
        return Fraction(0)
    return Fraction(2 * len(ta & tb), len(ta) + len(tb))


def similarity(a: str, b: str, criterion: str) -> Fraction:
    """Match weight of two normalised mentions; 0 means "not a match"."""
    if criterion not in CRITERIA:
        raise ValueError(f"unknown criterion: {criterion}")
    if not a or not b:
        return Fraction(0)
    if a == b:
        return Fraction(1)
    if criterion == "M1":
        return Fraction(0)
    if a in b or b in a:
        return SUBSTRING_WEIGHT
    f = token_f1(a, b)
    return f if f >= TOKEN_F1_THRESHOLD else Fraction(0)


# -------------------------------------------------------------------- alignment
def max_weight_assignment(weights):
    """Hungarian algorithm. Returns, per row, its column (None if unassigned).

    Every row of the smaller side is assigned, including to zero-weight cells.
    """
    n = len(weights)
    m = len(weights[0]) if n else 0
    if n == 0 or m == 0:
        return [None] * n
    if n > m:
        rows = max_weight_assignment([[weights[i][j] for i in range(n)] for j in range(m)])
        cols = [None] * n
        for j, i in enumerate(rows):
            cols[i] = j
        return cols
    inf = float("inf")
    u, v = [0] * (n + 1), [0] * (m + 1)
    owner, way = [0] * (m + 1), [0] * (m + 1)  # owner[j]: row holding column j
    for i in range(1, n + 1):
        owner[0] = i
        j0 = 0
        minv = [inf] * (m + 1)
        used = [False] * (m + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = owner[j0], inf, 0
            for j in range(1, m + 1):
                if used[j]:
                    continue
                cur = -weights[i0 - 1][j - 1] - u[i0] - v[j]
                if cur < minv[j]:
                    minv[j], way[j] = cur, j0
                if minv[j] < delta:
                    delta, j1 = minv[j], j
            for j in range(m + 1):
                if used[j]:
                    u[owner[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if owner[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            owner[j0] = owner[j1]
            j0 = j1
    cols = [None] * n
    for j in range(1, m + 1):
        if owner[j]:
            cols[owner[j] - 1] = j - 1
    return cols


def match_matrix(sim):
    """Maximum-weight matching over a matrix of Fraction weights.

    Returns (row, col) pairs with positive weight. The objective is
    lexicographic: total weight, then number of pairs, then least squared
    positional offset (which never crosses two interchangeable pairs).
    """
    n = len(sim)
    m = len(sim[0]) if n else 0
    if n == 0 or m == 0:
        return []
    denom = math.lcm(*(x.denominator for row in sim for x in row))
    k, longest = min(n, m), max(n, m)
    step = k * longest * longest + 1  # one extra pair outweighs all offsets
    unit = (k + 1) * step             # one weight quantum outweighs all pair bonuses
    weights = [
        [int(sim[i][j] * denom) * unit + step - (i - j) ** 2 if sim[i][j] > 0 else 0
         for j in range(m)]
        for i in range(n)
    ]
    cols = max_weight_assignment(weights)
    return [(i, j) for i, j in enumerate(cols) if j is not None and sim[i][j] > 0]


def match(ref, hyp, criterion):
    """Align two lists of normalised mentions; returns (ref_index, sys_index) pairs."""
    return match_matrix([[similarity(a, b, criterion) for b in hyp] for a in ref])


def order_concordance(pairs):
    """Share of matched-pair couples whose relative order agrees; None below two pairs."""
    if len(pairs) < 2:
        return None
    seq = [j for _, j in sorted(pairs)]
    total = len(seq) * (len(seq) - 1) // 2
    concordant = sum(seq[b] > seq[a] for a in range(len(seq)) for b in range(a + 1, len(seq)))
    return concordant / total


# ---------------------------------------------------------------------- scoring
def score_hadith(ref_mentions, sys_mentions, criterion):
    ref = [m for m in map(normalise, ref_mentions) if m]
    hyp = [m for m in map(normalise, sys_mentions) if m]
    pairs = match(ref, hyp, criterion)
    tp = len(pairs)
    fp, fn = len(hyp) - tp, len(ref) - tp
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "exact_chain": fp == 0 and fn == 0 and all(i == j for i, j in pairs),
        "order_concordance": order_concordance(pairs),
    }


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    f05 = 1.25 * p * r / (0.25 * p + r) if p + r else 0.0
    return p, r, f1, f05


def aggregate(items):
    tp, fp, fn = (sum(d[k] for d in items) for k in ("tp", "fp", "fn"))
    p, r, f1, f05 = prf(tp, fp, fn)
    conc = [d["order_concordance"] for d in items if d["order_concordance"] is not None]
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": p, "recall": r, "f1": f1, "f0.5": f05,
        "exact_chain_rate": sum(d["exact_chain"] for d in items) / len(items),
        "order_concordance": sum(conc) / len(conc) if conc else None,
    }


def percentile(values, q):
    """Linear-interpolation percentile, q in [0, 100]."""
    xs = sorted(values)
    pos = (len(xs) - 1) * q / 100
    lo = math.floor(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def bootstrap_ci(items, n_boot, seed):
    """95% percentile intervals for P, R, F1, resampling hadiths with replacement."""
    rng = random.Random(seed)
    n = len(items)
    counts = [(d["tp"], d["fp"], d["fn"]) for d in items]
    samples = {"precision": [], "recall": [], "f1": []}
    for _ in range(n_boot):
        tp = fp = fn = 0
        for _ in range(n):
            a, b, c = counts[rng.randrange(n)]
            tp, fp, fn = tp + a, fp + b, fn + c
        p, r, f1, _ = prf(tp, fp, fn)
        samples["precision"].append(p)
        samples["recall"].append(r)
        samples["f1"].append(f1)
    return {k: [percentile(v, 2.5), percentile(v, 97.5)] for k, v in samples.items()}


def score(reference, system, n_boot=2000, seed=0):
    """Score {hadith_id: mentions} dicts. Every reference hadith is scored;
    one absent from `system` contributes zero system mentions."""
    if not reference:
        raise ValueError("reference contains no hadiths")
    unknown = sorted(set(system) - set(reference))
    if unknown:
        raise ValueError(f"system hadith_id not in reference: {', '.join(unknown)}")
    report = {
        "n_hadiths": len(reference),
        "n_missing_from_system": sum(1 for h in reference if h not in system),
        "bootstrap": {"resamples": n_boot, "seed": seed, "unit": "hadith"},
    }
    hadith_ids = sorted(reference)  # resampling must not depend on file order
    for criterion in CRITERIA:
        items = [score_hadith(reference[h], system.get(h, []), criterion) for h in hadith_ids]
        result = aggregate(items)
        result["ci95"] = bootstrap_ci(items, n_boot, seed) if n_boot > 0 else None
        report[criterion] = result
    return report


# -------------------------------------------------------------------------- I/O
def load_jsonl(path):
    """Read {"hadith_id": str, "mentions": [str, ...]} lines into a dict."""
    out = {}
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            where = f"{path}:{lineno}"
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{where}: invalid JSON ({exc.msg})") from exc
            hid, mentions = (row.get("hadith_id"), row.get("mentions")) if isinstance(row, dict) else (None, None)
            if not isinstance(hid, str) or not hid:
                raise ValueError(f"{where}: missing string 'hadith_id'")
            if not isinstance(mentions, list) or not all(isinstance(m, str) for m in mentions):
                raise ValueError(f"{where}: 'mentions' must be a list of strings")
            if hid in out:
                raise ValueError(f"{where}: duplicate hadith_id {hid}")
            out[hid] = mentions
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Score isnad mention extraction against reference labels.")
    ap.add_argument("--system", required=True, help="system output JSONL")
    ap.add_argument("--reference", required=True, help="reference JSONL")
    ap.add_argument("--bootstrap", type=int, default=2000, help="bootstrap resamples (default 2000)")
    ap.add_argument("--seed", type=int, default=0, help="bootstrap seed (default 0)")
    ap.add_argument("--out", help="also write the JSON report to this path")
    args = ap.parse_args(argv)
    try:
        report = score(load_jsonl(args.reference), load_jsonl(args.system), args.bootstrap, args.seed)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
