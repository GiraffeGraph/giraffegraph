"""What kind of value does the value_not_in_quote check flag?

Reads one run directory written by backend/scripts/run_isnad_experiment.py, the hadith texts and a
reference file, and writes one record per proposed Narrator mention with deterministic features,
a class for every flagged mention, and summary tables. Standard library only; normalisation and
alignment come from scorer.py in this directory.

Definitions (repeated in the output under "definitions"):
  record                   one per mention index of a Narrator node candidate. A Narrator candidate
                           without a mention index is counted and left out. A mention that
                           normalises to nothing is not counted by the scorer; it is listed with
                           matched = null and left out of the summary.
  name                     the mention string of system_proposed.jsonl at that index.
  quotation                the first evidence quotation of the candidate.
  flagged                  value_not_in_quote is among the candidate's reason codes.
  matched                  the scorer's M2 alignment pairs the mention with a reference mention.
  latin_script             the name has at least one letter and no letter in U+0621-U+064A or
                           U+066E-U+06D3.
  name_in_text_normalised  scorer.normalise(name) is a non-empty substring of
                           scorer.normalise(hadith text). Character level, not token level.
  name_in_text_verbatim    the name is a substring of the hadith text as stored, code point for
                           code point.
  prophet_as_narrator      the normalised name contains "رسول الله" or "النبي", or the name contains
                           "rasul allah", "prophet" or "messenger" in any letter case.
  kinship_quote            the tokens of the normalised quotation, after dropping transmission
                           formulas and connectives (QUOTE_FUNCTION_TOKENS), are exactly one token
                           and it is a kinship reference (KINSHIP_TOKENS).
  case_ending_only         with the case forms folded (ابو/ابي/ابا, ابن/بن, اخو/اخي/اخا, also with
                           an attached و or ف) the tokens of the normalised name are a contiguous
                           run of the tokens of the normalised quotation, and without the folding
                           they are not. The normalisation removes vowel marks on both sides, so a
                           difference in vowel marks alone is no difference here.
  class                    flagged mentions only; the first that applies: latin_transliteration
                           (latin_script), kinship_resolved (kinship_quote), case_ending_only,
                           other_in_text (name_in_text_normalised), other_not_in_text.

Usage:
  python evaluation/classify_value_flags.py --run <run-dir> --hadiths hadiths.json
      --reference reference.jsonl --out value-flag-classes.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import scorer

FLAG_CODE = "value_not_in_quote"
CRITERION = "M2"
CLASSES = (
    "latin_transliteration",
    "kinship_resolved",
    "case_ending_only",
    "other_in_text",
    "other_not_in_text",
)
ARABIC_LETTER_RANGES = ((0x0621, 0x064A), (0x066E, 0x06D3))
PROPHET_ARABIC = ("رسول الله", "النبي")
PROPHET_LATIN = ("rasul allah", "prophet", "messenger")
QUOTE_FUNCTION_TOKENS = frozenset({
    "حدثنا", "حدثني", "حدثناه", "حدثنيه", "اخبرنا", "اخبرني", "انبانا", "انباني", "نبانا",
    "نباني", "حدثهم", "حدثه", "اخبرهم", "اخبره", "سمعت", "سمعنا", "ثنا", "نا", "انا", "عن",
    "ان", "قال", "قالت", "يقول", "و", "ف", "ثم",
})
KINSHIP_TOKENS = frozenset({
    "ابيه", "ابي", "ابيها", "ابيهما", "ابوه", "اباه", "جده", "جدي", "جدته", "جدتي", "امه",
    "امي", "امها", "عمه", "عمي", "عمته", "خاله", "خالته", "اخيه", "اخي", "اخته",
})
CASE_FORMS = {
    "ابو": "ابو", "ابي": "ابو", "ابا": "ابو",
    "ابن": "بن", "بن": "بن",
    "اخو": "اخو", "اخي": "اخو", "اخا": "اخو",
}
DEFINITIONS = {
    "record": (
        "One per mention index of a Narrator node candidate. A Narrator candidate without a "
        "mention index is counted and left out. A mention that normalises to nothing is listed "
        "with matched = null and left out of the summary."
    ),
    "name": "The mention string of system_proposed.jsonl at that index.",
    "quotation": "The first evidence quotation of the candidate.",
    "flagged": f"{FLAG_CODE} is among the candidate's reason codes.",
    "matched": f"The scorer's {CRITERION} alignment pairs the mention with a reference mention.",
    "latin_script": (
        "The name has at least one letter and no letter in U+0621-U+064A or U+066E-U+06D3."
    ),
    "name_in_text_normalised": (
        "scorer.normalise(name) is a non-empty substring of scorer.normalise(hadith text); "
        "character level, not token level."
    ),
    "name_in_text_verbatim": (
        "The name is a substring of the hadith text as stored, code point for code point."
    ),
    "prophet_as_narrator": (
        "The normalised name contains one of " + ", ".join(PROPHET_ARABIC) + ", or the name "
        "contains one of " + ", ".join(PROPHET_LATIN) + " in any letter case."
    ),
    "kinship_quote": (
        "The tokens of the normalised quotation, after dropping quote_function_tokens, are "
        "exactly one token and it is one of kinship_tokens."
    ),
    "case_ending_only": (
        "With case_forms folded (also with an attached و or ف) the tokens of the normalised name "
        "are a contiguous run of the tokens of the normalised quotation, and without the folding "
        "they are not. Vowel marks are removed on both sides by the normalisation."
    ),
    "class": (
        "Flagged mentions only; the first that applies: latin_transliteration (latin_script), "
        "kinship_resolved (kinship_quote), case_ending_only, other_in_text "
        "(name_in_text_normalised), other_not_in_text."
    ),
    "quote_function_tokens": sorted(QUOTE_FUNCTION_TOKENS),
    "kinship_tokens": sorted(KINSHIP_TOKENS),
    "case_forms": CASE_FORMS,
}


def read_jsonl(path):
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_hadith_texts(path):
    with open(path, encoding="utf-8") as handle:
        return {f"{row['coll']}:{row['num']}": row["raw"] for row in json.load(handle)}


def match_labels(reference_mentions, system_mentions):
    reference = [m for m in map(scorer.normalise, reference_mentions) if m]
    kept = [(i, m) for i, m in enumerate(map(scorer.normalise, system_mentions)) if m]
    matched = {j for _, j in scorer.match(reference, [m for _, m in kept], CRITERION)}
    labels = [None] * len(system_mentions)
    for position, (index, _) in enumerate(kept):
        labels[index] = position in matched
    return labels


def has_arabic_letter(text):
    return any(low <= ord(c) <= high for c in text for low, high in ARABIC_LETTER_RANGES)


def is_latin_script(name):
    return any(c.isalpha() for c in name) and not has_arabic_letter(name)


def is_prophet(name, normalised_name):
    folded = name.casefold()
    return any(term in normalised_name for term in PROPHET_ARABIC) or any(
        term in folded for term in PROPHET_LATIN
    )


def is_kinship_quote(normalised_quotation):
    content = [t for t in normalised_quotation.split() if t not in QUOTE_FUNCTION_TOKENS]
    return len(content) == 1 and content[0] in KINSHIP_TOKENS


def fold_case_form(token):
    if token in CASE_FORMS:
        return CASE_FORMS[token]
    if token[:1] in ("و", "ف") and token[1:] in CASE_FORMS:
        return CASE_FORMS[token[1:]]
    return token


def is_run(needle, haystack):
    width = len(needle)
    return width > 0 and any(
        haystack[start : start + width] == needle for start in range(len(haystack) - width + 1)
    )


def is_case_ending_only(normalised_name, normalised_quotation):
    name_tokens = normalised_name.split()
    quotation_tokens = normalised_quotation.split()
    return is_run(
        [fold_case_form(t) for t in name_tokens], [fold_case_form(t) for t in quotation_tokens]
    ) and not is_run(name_tokens, quotation_tokens)


def classify(features):
    if features["latin_script"]:
        return "latin_transliteration"
    if features["kinship_quote"]:
        return "kinship_resolved"
    if features["case_ending_only"]:
        return "case_ending_only"
    if features["name_in_text_normalised"]:
        return "other_in_text"
    return "other_not_in_text"


def build_records(run_dir, hadith_texts, reference):
    run_dir = Path(run_dir)
    proposed = scorer.load_jsonl(run_dir / "system_proposed.jsonl")
    unknown = sorted(set(proposed) - set(reference))
    if unknown:
        raise ValueError(f"system hadith_id not in reference: {', '.join(unknown)}")
    labels = {
        hadith_id: match_labels(reference[hadith_id], mentions)
        for hadith_id, mentions in proposed.items()
    }
    records = []
    without_mention = 0
    for candidate in read_jsonl(run_dir / "candidates.jsonl"):
        if candidate["kind"] != "node" or candidate["type"] != "Narrator":
            continue
        mention_indexes = candidate.get("mention_indexes") or []
        if not mention_indexes:
            without_mention += 1
            continue
        hadith_id = candidate["hadith_id"]
        text = hadith_texts[hadith_id]
        quotations = candidate["evidence_quotes"]
        quotation = quotations[0] if quotations else None
        normalised_quotation = scorer.normalise(quotation or "")
        flagged = FLAG_CODE in candidate["reason_codes"]
        for index in mention_indexes:
            name = proposed[hadith_id][index]
            normalised_name = scorer.normalise(name)
            features = {
                "latin_script": is_latin_script(name),
                "name_in_text_normalised": normalised_name != ""
                and normalised_name in scorer.normalise(text),
                "name_in_text_verbatim": name != "" and name in text,
                "prophet_as_narrator": is_prophet(name, normalised_name),
                "kinship_quote": is_kinship_quote(normalised_quotation),
                "case_ending_only": is_case_ending_only(normalised_name, normalised_quotation),
            }
            records.append({
                "hadith_id": hadith_id,
                "candidate_id": candidate["candidate_id"],
                "mention_index": index,
                "name": name,
                "quotation": quotation,
                "flagged": flagged,
                "matched": labels[hadith_id][index],
                **features,
                "class": classify(features) if flagged else None,
            })
    records.sort(key=lambda r: (r["hadith_id"], r["mention_index"]))
    return records, without_mention


def split_by_flag(records):
    return {
        "total": len(records),
        "flagged": sum(1 for r in records if r["flagged"]),
        "not_flagged": sum(1 for r in records if not r["flagged"]),
        "hadiths": len({r["hadith_id"] for r in records}),
    }


def summarise(records, without_mention):
    counted = [r for r in records if r["matched"] is not None]
    flagged = [r for r in counted if r["flagged"]]
    unmatched = [r for r in counted if not r["matched"]]
    by_class = {}
    for name in CLASSES:
        rows = [r for r in flagged if r["class"] == name]
        by_class[name] = {
            "flagged": len(rows),
            "unmatched": sum(1 for r in rows if not r["matched"]),
            "matched": sum(1 for r in rows if r["matched"]),
            "hadiths": len({r["hadith_id"] for r in rows}),
            "name_in_text_normalised": sum(1 for r in rows if r["name_in_text_normalised"]),
            "name_in_text_verbatim": sum(1 for r in rows if r["name_in_text_verbatim"]),
        }
    return {
        "mentions": {
            "total": len(counted),
            "matched": len(counted) - len(unmatched),
            "unmatched": len(unmatched),
            "normalising_to_nothing_left_out": len(records) - len(counted),
            "narrator_candidates_without_a_mention_left_out": without_mention,
        },
        "flagged": {
            "total": len(flagged),
            "unmatched": sum(1 for r in flagged if not r["matched"]),
            "matched": sum(1 for r in flagged if r["matched"]),
            "hadiths": len({r["hadith_id"] for r in flagged}),
            "name_in_text_normalised": sum(1 for r in flagged if r["name_in_text_normalised"]),
            "name_absent_from_normalised_text": sum(
                1 for r in flagged if not r["name_in_text_normalised"]
            ),
            "name_in_text_verbatim": sum(1 for r in flagged if r["name_in_text_verbatim"]),
        },
        "flagged_by_class": by_class,
        "unmatched_mentions": {
            "all": split_by_flag(unmatched),
            "prophet_as_narrator": split_by_flag(
                [r for r in unmatched if r["prophet_as_narrator"]]
            ),
            "name_absent_from_normalised_text": split_by_flag(
                [r for r in unmatched if not r["name_in_text_normalised"]]
            ),
            "name_present_in_normalised_text": split_by_flag(
                [r for r in unmatched if r["name_in_text_normalised"]]
            ),
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Classify the Narrator mentions flagged by the value_not_in_quote check."
    )
    parser.add_argument("--run", required=True, help="output directory of run_isnad_experiment.py")
    parser.add_argument("--hadiths", required=True, help="JSON list with coll, num and raw")
    parser.add_argument("--reference", required=True, help="reference JSONL")
    parser.add_argument("--out", required=True, help="JSON file to write")
    args = parser.parse_args(argv)
    try:
        records, without_mention = build_records(
            args.run, load_hadith_texts(args.hadiths), scorer.load_jsonl(args.reference)
        )
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    report = {
        "run": args.run,
        "hadiths": args.hadiths,
        "reference": args.reference,
        "flag_code": FLAG_CODE,
        "criterion": CRITERION,
        "definitions": DEFINITIONS,
        "summary": summarise(records, without_mention),
        "mentions": records,
    }
    Path(args.out).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
