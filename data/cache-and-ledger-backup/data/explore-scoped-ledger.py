"""Scoped decision ledger: fixed keys versus scopes refined on contradiction.

Replays labelled isnad chains in random order. The ledger stores every human answer with its full
context (student name, name, teacher name -> person). The SCOPE under which an answer is reused is
not stored; it is a per-name level derived from the contradictions seen so far:

  level 0  reuse by name
  level 1  reuse by (student, name)
  level 2  reuse by (student, name, teacher)

A name moves one level down when a human answer contradicts the reused one. Contradictions are found
by random audits (rate eps), by a deterministic plausibility guard on the proposed teacher-student
pair (generation and death-year gaps from the narrator table), or both.

Cost  = human questions (new keys + audits + guard questions) per mention.
Error = reused answers that differ from the label and that no human saw, per mention.

usage: explore-scoped-ledger.py <chains.jsonl> <narrators.csv> [shuffles]
"""
import csv
import json
import math
import random
import re
import statistics
import sys
from collections import Counter, defaultdict

ORDINALS = [("الحادية عشر", 11), ("الثانية عشر", 12), ("الأولى", 1), ("الاولى", 1),
            ("الثانية", 2), ("الثالثة", 3), ("الرابعة", 4), ("الخامسة", 5), ("السادسة", 6),
            ("السابعة", 7), ("الثامنة", 8), ("التاسعة", 9), ("العاشرة", 10)]
# Bounds cover the central mass of true adjacent pairs in this dataset (see `guard_calibration`).
GENERATION_GAP = (-1, 5)
DEATH_GAP = (-20, 85)


def parse_generation(text):
    for word, number in ORDINALS:
        if word in text:
            return number
    if "صحاب" in text or "أم المؤمنين" in text or "صحبة" in text:
        return 1
    return None


def parse_death(text):
    match = re.search(r"(\d{1,3})\s*هـ", text) or re.search(r"(\d{2,3})", text)
    return int(match.group(1)) if match else None


def load(chains_path, narrators_path):
    chains = []
    with open(chains_path, encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            chains.append((tuple(row["mentions"]), tuple(row["narrator_ids"])))
    people = {}
    with open(narrators_path, encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            people[int(row["id"])] = (parse_generation(row["tabaqa"]), parse_death(row["death_year"]))
    return chains, people


def implausible(student, teacher, people):
    """True when the narrator table says this student could hardly have heard this teacher."""
    s_gen, s_death = people.get(student, (None, None))
    t_gen, t_death = people.get(teacher, (None, None))
    if s_gen is not None and t_gen is not None:
        if not GENERATION_GAP[0] <= s_gen - t_gen <= GENERATION_GAP[1]:
            return True
    if s_death is not None and t_death is not None:
        if not DEATH_GAP[0] <= s_death - t_death <= DEATH_GAP[1]:
            return True
    return False


def context_keys(mentions, i):
    student = mentions[i - 1] if i else None
    teacher = mentions[i + 1] if i + 1 < len(mentions) else None
    return (mentions[i], (student, mentions[i]), (student, mentions[i], teacher))


def replay(chains, people, policy, rng):
    """policy: dict(level=fixed level or None, eps=audit rate, guard=bool, start=dict name->level)."""
    tables = ({}, {}, {})
    level = defaultdict(int, policy.get("start", {}))
    fixed = policy.get("level")
    eps, use_guard = policy.get("eps", 0.0), policy.get("guard", False)
    total = sum(len(m) for m, _ in chains)
    tail_from = int(total * 0.9)
    seen = questions = silent_wrong = tail_questions = tail_wrong = 0
    guard_hits = guard_false = contradictions = 0

    def record(keys, person):
        for table, key in zip(tables, keys):
            table.setdefault(key, person)

    for mentions, ids in chains:
        proposals, reused = [], []
        for i, person in enumerate(ids):
            keys = context_keys(mentions, i)
            lvl = fixed if fixed is not None else level[mentions[i]]
            stored = tables[lvl].get(keys[lvl])
            in_tail = seen >= tail_from
            seen += 1
            if stored is None:
                questions += 1
                tail_questions += in_tail
                record(keys, person)
                proposals.append(person)
                reused.append(None)
                continue
            if eps and rng.random() < eps:
                questions += 1
                tail_questions += in_tail
                if stored != person:
                    contradictions += 1
                    if fixed is None and lvl < 2:
                        level[mentions[i]] = lvl + 1
                record(keys, person)
                proposals.append(person)
                reused.append(None)
                continue
            proposals.append(stored)
            reused.append(in_tail)
        for i, in_tail in enumerate(reused):
            if in_tail is None:
                continue
            person, stored = ids[i], proposals[i]
            flagged = use_guard and (
                (i > 0 and implausible(proposals[i - 1], stored, people))
                or (i + 1 < len(ids) and implausible(stored, proposals[i + 1], people))
            )
            if flagged:
                questions += 1
                tail_questions += in_tail
                if stored != person:
                    guard_hits += 1
                    contradictions += 1
                    name = mentions[i]
                    if fixed is None and level[name] < 2:
                        level[name] += 1
                else:
                    guard_false += 1
                record(context_keys(mentions, i), person)
            elif stored != person:
                silent_wrong += 1
                tail_wrong += in_tail
    tail = total - tail_from
    return {
        "questions_per_mention": questions / total,
        "silent_wrong_per_mention": silent_wrong / total,
        "tail10_questions_per_mention": tail_questions / tail,
        "tail10_silent_wrong_per_mention": tail_wrong / tail,
        "questions": questions,
        "silent_wrong": silent_wrong,
        "contradictions_found": contradictions,
        "guard_questions_that_found_an_error": guard_hits,
        "guard_questions_on_correct_answers": guard_false,
        "names_refined": sum(1 for value in level.values() if value) if fixed is None else None,
    }


def average(runs):
    out = {}
    for key in runs[0]:
        values = [run[key] for run in runs]
        if values[0] is None:
            out[key] = None
        else:
            mean = statistics.mean(values)
            out[key] = round(mean, 4) if mean < 10 else round(mean)
    return out


def entropy(counter):
    total = sum(counter.values())
    return -sum(c / total * math.log2(c / total) for c in counter.values())


def information(chains):
    people, by_name = Counter(), defaultdict(Counter)
    for mentions, ids in chains:
        for name, person in zip(mentions, ids):
            people[person] += 1
            by_name[name][person] += 1
    total = sum(people.values())
    conditional = sum(sum(c.values()) / total * entropy(c) for c in by_name.values())
    ambiguous = {name for name, c in by_name.items() if len(c) > 1}
    return {
        "bits_to_name_a_person_H(P)": round(entropy(people), 3),
        "bits_left_after_the_name_H(P|name)_plug_in": round(conditional, 3),
        "names": len(by_name),
        "names_with_more_than_one_person": len(ambiguous),
        "share_of_mentions_under_such_names": round(
            sum(sum(by_name[n].values()) for n in ambiguous) / total, 4),
    }, ambiguous


def guard_calibration(chains, people):
    pairs = flagged = 0
    for _, ids in chains:
        for student, teacher in zip(ids, ids[1:]):
            pairs += 1
            flagged += implausible(student, teacher, people)
    return {"true_adjacent_pairs": pairs, "flagged_by_guard": flagged,
            "false_alarm_rate_on_true_pairs": round(flagged / pairs, 4),
            "generation_gap_allowed": GENERATION_GAP, "death_gap_allowed": DEATH_GAP}


def main(chains_path, narrators_path, shuffles=10):
    chains, people = load(chains_path, narrators_path)
    info, ambiguous = information(chains)
    policies = {
        "fixed: name": {"level": 0},
        "fixed: student+name": {"level": 1},
        "fixed: student+name+teacher": {"level": 2},
        "refine on audit, eps=0.02": {"eps": 0.02},
        "refine on audit, eps=0.05": {"eps": 0.05},
        "refine on audit, eps=0.10": {"eps": 0.10},
        "refine on audit, eps=0.20": {"eps": 0.20},
        "refine on guard": {"guard": True},
        "refine on guard + audit, eps=0.02": {"guard": True, "eps": 0.02},
        "refine on guard + audit, eps=0.05": {"guard": True, "eps": 0.05},
        "refine on guard + audit, eps=0.10": {"guard": True, "eps": 0.10},
        "fixed: name, with guard questions": {"level": 0, "guard": True},
        "hindsight: ambiguous names start at student+name": {"start": {n: 1 for n in ambiguous}},
    }
    report = {
        "chains": len(chains),
        "mentions": sum(len(m) for m, _ in chains),
        "shuffles": shuffles,
        "information": info,
        "guard_calibration": guard_calibration(chains, people),
        "policies": {},
    }
    for name, policy in policies.items():
        runs = []
        for seed in range(shuffles):
            order = chains[:]
            random.Random(seed).shuffle(order)
            runs.append(replay(order, people, policy, random.Random(1000 + seed)))
        report["policies"][name] = average(runs)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10)
