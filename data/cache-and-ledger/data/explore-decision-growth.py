"""How many human identity decisions does a ledger need as the corpus grows?

Replays labelled isnad chains in random order. A "decision" is asked whenever the
ledger has no entry for the key of a mention; afterwards the stored answer is
reused. A reuse is "wrong" when the stored person differs from the label.
"""
import json, math, random, statistics, sys
from collections import Counter

def load(path):
    rows = []
    with open(path, encoding="utf-8") as h:
        for line in h:
            r = json.loads(line)
            rows.append((tuple(r["mentions"]), tuple(r["narrator_ids"])))
    return rows

KEYS = {
    "name": lambda m, i: m[i],
    "name+teacher": lambda m, i: (m[i], m[i + 1] if i + 1 < len(m) else None),
    "student+name": lambda m, i: (m[i - 1] if i else None, m[i]),
    "student+name+teacher": lambda m, i: (m[i - 1] if i else None, m[i], m[i + 1] if i + 1 < len(m) else None),
}

def replay(rows, keyf):
    ledger, n, decisions, wrong = {}, 0, 0, 0
    curve = []
    for mentions, ids in rows:
        for i, pid in enumerate(ids):
            k = keyf(mentions, i)
            n += 1
            if k not in ledger:
                ledger[k] = pid; decisions += 1
            elif ledger[k] != pid:
                wrong += 1
            curve.append((decisions, wrong))
    return curve

def summarise(curves):
    n = len(curves[0])
    out = {}
    for frac in (0.01, 0.1, 0.25, 0.5, 1.0):
        i = int(n * frac) - 1
        out[f"decisions_after_{int(frac*100)}pct"] = round(statistics.mean(c[i][0] for c in curves))
    lo = int(n * 0.9)
    tail = n - lo
    out["tail10_decision_rate"] = round(statistics.mean((c[-1][0] - c[lo - 1][0]) / tail for c in curves), 4)
    out["tail10_wrong_reuse_rate"] = round(statistics.mean((c[-1][1] - c[lo - 1][1]) / tail for c in curves), 4)
    out["overall_wrong_reuse_rate"] = round(statistics.mean(c[-1][1] / n for c in curves), 4)
    # Heaps exponent: slope of log D vs log n between 1% and 100%
    xs = [int(n * f) for f in (0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0)]
    pts = [(math.log(x), math.log(statistics.mean(c[x - 1][0] for c in curves))) for x in xs]
    mx = statistics.mean(p[0] for p in pts); my = statistics.mean(p[1] for p in pts)
    out["heaps_beta"] = round(sum((p[0]-mx)*(p[1]-my) for p in pts) / sum((p[0]-mx)**2 for p in pts), 3)
    return out

def main(path, shuffles=10):
    rows = load(path)
    uniq = list(dict.fromkeys(rows))
    report = {"chains": len(rows), "distinct_chains": len(uniq),
              "mentions": sum(len(m) for m, _ in rows),
              "people": len({p for _, ids in rows for p in ids}),
              "name_strings": len({s for m, _ in rows for s in m})}
    for label, data in (("all_chains", rows), ("distinct_chains_only", uniq)):
        report[label] = {"mentions": sum(len(m) for m, _ in data)}
        for name, keyf in KEYS.items():
            curves = []
            for seed in range(shuffles):
                d = data[:]; random.Random(seed).shuffle(d)
                curves.append(replay(d, keyf))
            report[label][name] = summarise(curves)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main(sys.argv[1])
