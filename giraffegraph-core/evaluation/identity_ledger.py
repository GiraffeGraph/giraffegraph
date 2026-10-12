"""How many identity decisions does a reviewer have to make, and how many reused ones are wrong?

Replays labelled isnad chains through a decision ledger. The ledger asks a reviewer the first time
it sees a key and reuses the answer afterwards. The reviewer is simulated from the labels of the
dataset. Every answer is stored with its full context (student name, name, teacher name); the scope
under which it is reused is a per-name level, moved one step down each time a reviewer answer
contradicts a reused one:

    level 0  reuse by name
    level 1  reuse by (student, name)
    level 2  reuse by (student, name, teacher)

Contradictions come from random audits, from a plausibility guard on the proposed student-teacher
pair (generation and death-year gaps taken from a narrator table), or both.

Reported per mention: questions (new keys, audits, guard questions), silent errors (reused answers
that differ from the label and that no reviewer saw) and wrong reviewer answers.
"""

import argparse
import ast
import csv
import json
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

PLACEHOLDER_IDS = {0, 1, 2}
ORDINALS = [
    ("الحادية عشر", 11),
    ("الثانية عشر", 12),
    ("الأولى", 1),
    ("الاولى", 1),
    ("الثانية", 2),
    ("الثالثة", 3),
    ("الرابعة", 4),
    ("الخامسة", 5),
    ("السادسة", 6),
    ("السابعة", 7),
    ("الثامنة", 8),
    ("التاسعة", 9),
    ("العاشرة", 10),
]
KINSHIP = frozenset("أبيه أبي جده أباه أمه عمه أبيها جدي أخيه".split())
# Chosen on the AR-Sanad test chains: 0.8% of their true adjacent pairs fall outside.
GENERATION_GAP = (-1, 5)
DEATH_GAP = (-20, 85)
SCOPES = 3


def parse_generation(text):
    for word, number in ORDINALS:
        if word in text:
            return number
    if "صحاب" in text or "أم المؤمنين" in text or "صحبة" in text:
        return 1
    return None


def parse_death_year(text):
    match = re.search(r"(\d{1,3})\s*هـ", text) or re.search(r"(\d{2,3})", text)
    return int(match.group(1)) if match else None


def load_ar_sanad(chains_path, narrators_path):
    documents = []
    with open(chains_path, encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            documents.append(list(zip(row["mentions"], row["narrator_ids"], strict=True)))
    people = {}
    with open(narrators_path, encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            people[int(row["id"])] = (
                parse_generation(row["tabaqa"]),
                parse_death_year(row["death_year"]),
            )
    return {"all": documents}, people


def load_ifta(hadiths_path, narrators_path):
    """Mentions in text order per hadith, grouped by collection. Placeholder ids are dropped."""
    books = defaultdict(list)
    with open(hadiths_path, encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            names = row["names"]
            if isinstance(names, str):
                names = ast.literal_eval(names)
            document = [
                (plain, int(narrator_id))
                for _, plain, narrator_id in names or []
                if narrator_id is not None and int(narrator_id) not in PLACEHOLDER_IDS
            ]
            if document:
                books[row["coll"]].append(document)
    people = {}
    for row in json.loads(Path(narrators_path).read_text(encoding="utf-8")):
        people[int(row["narrator_id"])] = (
            parse_generation(str(row["class_of_narrators"])),
            parse_death_year(str(row["date_of_death"])),
        )
    return dict(books), people


def implausible(student, teacher, people):
    """True when the narrator table says this student could hardly have heard this teacher."""
    student_generation, student_death = people.get(student, (None, None))
    teacher_generation, teacher_death = people.get(teacher, (None, None))
    if student_generation is not None and teacher_generation is not None:
        gap = student_generation - teacher_generation
        if not GENERATION_GAP[0] <= gap <= GENERATION_GAP[1]:
            return True
    if student_death is not None and teacher_death is not None:
        gap = student_death - teacher_death
        if not DEATH_GAP[0] <= gap <= DEATH_GAP[1]:
            return True
    return False


def context_keys(names, index):
    student = names[index - 1] if index else None
    teacher = names[index + 1] if index + 1 < len(names) else None
    return (names[index], (student, names[index]), (student, names[index], teacher))


@dataclass(frozen=True)
class Policy:
    fixed_level: int | None = None
    audit_rate: float = 0.0
    guard: bool = False
    kinship_starts_in_context: bool = False
    start_levels: tuple = ()


@dataclass
class Ledger:
    tables: tuple = field(default_factory=lambda: ({}, {}, {}))
    level: dict = field(default_factory=dict)

    def record(self, keys, person):
        for table, key in zip(self.tables, keys, strict=True):
            table.setdefault(key, person)

    def refine(self, name):
        self.level[name] = min(self.level.get(name, 0) + 1, SCOPES - 1)


@dataclass
class Tally:
    mentions: int = 0
    questions: int = 0
    silent_wrong: int = 0
    reviewer_wrong: int = 0
    guard_questions_on_errors: int = 0
    guard_questions_on_correct: int = 0

    def rates(self):
        if not self.mentions:
            return {}
        reused = self.mentions - self.questions
        return {
            "mentions": self.mentions,
            "questions_per_mention": self.questions / self.mentions,
            "silent_wrong_per_mention": self.silent_wrong / self.mentions,
            "silent_wrong_per_reuse": self.silent_wrong / reused if reused else 0.0,
            "reviewer_wrong_per_mention": self.reviewer_wrong / self.mentions,
            "guard_questions_on_errors": self.guard_questions_on_errors,
            "guard_questions_on_correct": self.guard_questions_on_correct,
        }


def confusable_people(documents):
    by_name = defaultdict(Counter)
    for document in documents:
        for name, person in document:
            by_name[name][person] += 1
    return {name: sorted(counts) for name, counts in by_name.items() if len(counts) > 1}


def replay(documents, people, policy, rng, ledger=None, tally=None, reviewer_error=0.0,
           confusable=None):
    """Run the documents through the ledger. `tally=None` warms the ledger without counting."""
    ledger = ledger if ledger is not None else Ledger()
    if policy.fixed_level is None:
        for name in policy.start_levels:
            ledger.level.setdefault(name, 1)
    counting = tally is not None
    tally = tally if counting else Tally()

    def level_of(name):
        if policy.fixed_level is not None:
            return policy.fixed_level
        if policy.kinship_starts_in_context and name in KINSHIP:
            return max(ledger.level.get(name, 0), 1)
        return ledger.level.get(name, 0)

    def ask(name, person):
        tally.questions += 1
        answer = person
        if reviewer_error and rng.random() < reviewer_error:
            others = [p for p in (confusable or {}).get(name, ()) if p != person]
            if others:
                answer = rng.choice(others)
                tally.reviewer_wrong += 1
        return answer

    for document in documents:
        names = [name for name, _ in document]
        truth = [person for _, person in document]
        proposals, reused = [], []
        for index, person in enumerate(truth):
            keys = context_keys(names, index)
            level = level_of(names[index])
            stored = ledger.tables[level].get(keys[level])
            tally.mentions += 1
            if stored is None:
                answer = ask(names[index], person)
                ledger.record(keys, answer)
                proposals.append(answer)
                reused.append(False)
            elif policy.audit_rate and rng.random() < policy.audit_rate:
                answer = ask(names[index], person)
                if answer != stored and policy.fixed_level is None:
                    ledger.refine(names[index])
                ledger.record(keys, answer)
                proposals.append(answer)
                reused.append(False)
            else:
                proposals.append(stored)
                reused.append(True)
        for index, was_reused in enumerate(reused):
            if not was_reused:
                continue
            stored = proposals[index]
            flagged = policy.guard and (
                (index > 0 and implausible(proposals[index - 1], stored, people))
                or (index + 1 < len(truth) and implausible(stored, proposals[index + 1], people))
            )
            if flagged:
                answer = ask(names[index], truth[index])
                if answer != stored:
                    tally.guard_questions_on_errors += 1
                    if policy.fixed_level is None:
                        ledger.refine(names[index])
                else:
                    tally.guard_questions_on_correct += 1
                ledger.record(context_keys(names, index), answer)
            elif stored != truth[index]:
                tally.silent_wrong += 1
    return ledger, tally


def policies(ambiguous_names):
    return {
        "name": Policy(fixed_level=0),
        "student+name": Policy(fixed_level=1),
        "name, guard asks about the flagged fact only": Policy(fixed_level=0, guard=True),
        "scope narrows on guard": Policy(guard=True),
        "scope narrows on guard, kinship terms start in context": Policy(
            guard=True, kinship_starts_in_context=True),
        "scope narrows on guard and 5% audit": Policy(guard=True, audit_rate=0.05),
        "scope narrows on 5% audit": Policy(audit_rate=0.05),
        "hindsight: names known to be ambiguous start in context": Policy(
            start_levels=tuple(sorted(ambiguous_names))),
    }


def mean_rates(runs):
    keys = runs[0].keys()
    return {key: round(statistics.mean(run[key] for run in runs), 4) for key in keys}


def describe(documents, people):
    by_name, pairs, flagged, with_table = defaultdict(Counter), 0, 0, 0
    mentions = 0
    for document in documents:
        ids = [person for _, person in document]
        for name, person in document:
            by_name[name][person] += 1
            mentions += 1
            with_table += people.get(person, (None, None)) != (None, None)
        for student, teacher in zip(ids, ids[1:], strict=False):
            pairs += 1
            flagged += implausible(student, teacher, people)
    ambiguous = {name for name, counts in by_name.items() if len(counts) > 1}
    return {
        "documents": len(documents),
        "mentions": mentions,
        "people": len({p for counts in by_name.values() for p in counts}),
        "names": len(by_name),
        "names_with_more_than_one_person": len(ambiguous),
        "share_of_mentions_under_such_names": round(
            sum(sum(by_name[name].values()) for name in ambiguous) / mentions, 4),
        "share_of_mentions_with_generation_or_death_year": round(with_table / mentions, 4),
        "guard_false_alarm_rate_on_labelled_adjacent_pairs": round(flagged / pairs, 4),
    }, ambiguous


def shuffled(documents, seed):
    order = list(documents)
    random.Random(seed).shuffle(order)
    return order


def evaluate_pooled(documents, people, seeds, reviewer_error=0.0):
    summary, ambiguous = describe(documents, people)
    confusable = confusable_people(documents)
    out = {}
    for name, policy in policies(ambiguous).items():
        runs = []
        for seed in range(seeds):
            _, tally = replay(shuffled(documents, seed), people, policy,
                              random.Random(1000 + seed), tally=Tally(),
                              reviewer_error=reviewer_error, confusable=confusable)
            runs.append(tally.rates())
        out[name] = mean_rates(runs)
    return summary, out


def evaluate_held_out(books, people, seeds):
    """For each collection: warm the ledger on the other collections, count on the held-out one."""
    out = {}
    for held_out, test_documents in sorted(books.items()):
        train_documents = [d for book, docs in books.items() if book != held_out for d in docs]
        _, ambiguous_in_training = describe(train_documents, people)
        out[held_out] = {"cold": {}, "after_the_other_collections": {}}
        for name, policy in policies(ambiguous_in_training).items():
            cold, warm = [], []
            for seed in range(seeds):
                rng = random.Random(1000 + seed)
                _, tally = replay(shuffled(test_documents, seed), people, policy, rng,
                                  tally=Tally())
                cold.append(tally.rates())
                ledger, _ = replay(shuffled(train_documents, seed), people, policy, rng)
                _, tally = replay(shuffled(test_documents, seed), people, policy, rng,
                                  ledger=ledger, tally=Tally())
                warm.append(tally.rates())
            out[held_out]["cold"][name] = mean_rates(cold)
            out[held_out]["after_the_other_collections"][name] = mean_rates(warm)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ar-sanad", nargs=2, metavar=("CHAINS", "NARRATORS"))
    parser.add_argument("--ifta", nargs=2, metavar=("HADITHS", "NARRATORS"))
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    report = {
        "seeds": args.seeds,
        "generation_gap_allowed": GENERATION_GAP,
        "death_gap_allowed": DEATH_GAP,
        "guard_bounds_chosen_on": "AR-Sanad test chains",
    }
    if args.ar_sanad:
        books, people = load_ar_sanad(*args.ar_sanad)
        summary, pooled = evaluate_pooled(books["all"], people, args.seeds)
        _, noisy = evaluate_pooled(books["all"], people, args.seeds, reviewer_error=0.05)
        report["ar_sanad"] = {
            "corpus": summary,
            "policies": pooled,
            "policies_when_the_reviewer_errs_5pct_on_ambiguous_names": noisy,
        }
    if args.ifta:
        books, people = load_ifta(*args.ifta)
        everything = [d for docs in books.values() for d in docs]
        summary, pooled = evaluate_pooled(everything, people, args.seeds)
        report["ifta"] = {
            "corpus": summary,
            "mentions_per_collection": {b: sum(len(d) for d in docs) for b, docs in books.items()},
            "policies": pooled,
            "held_out_collection": evaluate_held_out(books, people, args.seeds),
        }
    Path(args.out).write_text(
        json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
