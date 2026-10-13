"""Copy check on a human-labelled corpus outside the hadith domain (BC5CDR).

A model extracts chemicals and diseases from PubMed abstracts, giving a name and a supporting quote
for each. Two deterministic checks split the output:

  copy         the quote occurs in the text and the name occurs in the quote
  transformed  the name is not in its own quote (the model rewrote something)
  unquoted     the quote does not occur in the text

Each part is scored against the human mention annotations of the same abstract (loose surface
match: equal, containment, or token F1 >= 0.60, one-to-one). Transformed names cannot match a
surface annotation by construction, so they are classified a second way, by concept: the gold
mention inside the model's own quote gives a MeSH id, and the rewritten name counts as "same
concept" when the corpus annotates that exact name with that id somewhere.

usage: explore-copy-check-bc5cdr.py <CDR_TestSet.PubTator.txt> <all PubTator files...> --env <.env>
       [--docs 300] [--cache <dir>] [--max-usd 0.80]
"""
import argparse
import hashlib
import json
import random
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODEL = "claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10, 0.50  # USD per million tokens
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["entities"],
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["type", "name", "quote", "confidence"],
                "properties": {
                    "type": {"type": "string", "enum": ["Chemical", "Disease"]},
                    "name": {"type": "string"},
                    "quote": {"type": "string"},
                    "confidence": {"type": "number"},
                },
            },
        }
    },
}
PROMPTS = {
    "schema_only": (
        "You extract entities from a biomedical abstract. Return every distinct chemical and every "
        "distinct disease that the text mentions. For each entity give its type, its name, a quote "
        "(a short excerpt of the text that supports it) and a confidence between 0 and 1."
    ),
    "verbatim": (
        "You extract entities from a biomedical abstract. Return every distinct chemical and every "
        "distinct disease that the text mentions. For each entity give its type, its name, a quote "
        "and a confidence between 0 and 1. The name must be copied character for character from "
        "the text, exactly as written there: do not expand abbreviations, do not normalise, do not "
        "correct spelling. The quote must be an exact excerpt of the text that contains the name."
    ),
}


def fold(text):
    return re.sub(r"\s+", " ", text.casefold()).strip()


def tokens(text):
    return re.findall(r"\w+", fold(text))


def read_pubtator(path):
    documents = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        head = re.match(r"^(\d+)\|([ta])\|(.*)$", line)
        if head:
            documents.setdefault(head.group(1), {"t": "", "a": "", "mentions": []})[
                head.group(2)] = head.group(3)
            continue
        parts = line.split("\t")
        if len(parts) >= 6 and parts[1].isdigit():
            documents[parts[0]]["mentions"].append((parts[3], parts[4], parts[5].strip()))
    return documents


def weight(a, b):
    a, b = fold(a), fold(b)
    if a == b:
        return 1.0
    if a and b and (a in b or b in a):
        return 0.9
    ta, tb = tokens(a), tokens(b)
    common = len(set(ta) & set(tb))
    if not common:
        return 0.0
    precision, recall = common / len(set(ta)), common / len(set(tb))
    f1 = 2 * precision * recall / (precision + recall)
    return f1 if f1 >= 0.60 else 0.0


def match(proposed, gold):
    """Greedy one-to-one matching by descending weight. Returns matched proposal indexes."""
    pairs = sorted(
        ((weight(p, g), i, j) for i, p in enumerate(proposed) for j, g in enumerate(gold)),
        reverse=True)
    used_p, used_g = set(), set()
    for w, i, j in pairs:
        if w <= 0:
            break
        if i in used_p or j in used_g:
            continue
        used_p.add(i)
        used_g.add(j)
    return used_p, used_g


def call(client, cache_dir, condition, doc_id, text):
    key = hashlib.sha256(json.dumps([MODEL, PROMPTS[condition], text]).encode()).hexdigest()
    cached = cache_dir / f"{key}.json"
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8")) | {"cached": True}
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=PROMPTS[condition],
        messages=[{"role": "user", "content": text}],
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
    )
    record = {
        "doc_id": doc_id,
        "condition": condition,
        "stop_reason": response.stop_reason,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "text": next((b.text for b in response.content if b.type == "text"), ""),
    }
    cached.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    return record | {"cached": False}


def auc(scored):
    """Probability that a matched item has higher confidence than an unmatched one."""
    positives = [s for s, ok in scored if ok]
    negatives = [s for s, ok in scored if not ok]
    if not positives or not negatives:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in positives for n in negatives)
    return wins / (len(positives) * len(negatives))


def analyse(records, documents, concept_names):
    rows, gold_total, gold_found, failed = [], 0, 0, 0
    for record in records:
        document = documents[record["doc_id"]]
        text = fold(document["t"] + " " + document["a"])
        if record["stop_reason"] != "end_turn":
            failed += 1
            continue
        try:
            entities = json.loads(record["text"])["entities"]
        except (json.JSONDecodeError, KeyError):
            failed += 1
            continue
        gold = sorted({m[0] for m in document["mentions"]})
        gold_ids = defaultdict(set)
        for surface, _, identity in document["mentions"]:
            gold_ids[fold(surface)].add(identity)
        seen, proposed = set(), []
        for entity in entities:
            if fold(entity["name"]) not in seen:
                seen.add(fold(entity["name"]))
                proposed.append(entity)
        matched, used_gold = match([e["name"] for e in proposed], gold)
        gold_total += len(gold)
        gold_found += len(used_gold)
        for index, entity in enumerate(proposed):
            name, quote = fold(entity["name"]), fold(entity["quote"])
            quote_in_text = bool(quote) and quote in text
            name_in_quote = bool(name) and name in quote
            part = "copy" if quote_in_text and name_in_quote else (
                "transformed" if quote_in_text else "unquoted")
            in_quote_ids = set()
            for surface, ids in gold_ids.items():
                if surface in quote:
                    in_quote_ids |= ids
            rows.append({
                "part": part,
                "matched": index in matched,
                "confidence": entity["confidence"],
                "gold_mention_in_quote": bool(in_quote_ids),
                "same_concept": bool(in_quote_ids & concept_names.get(name, set())),
                "name_in_text": name in text,
            })
    total = len(rows)
    out = {"documents_scored": len(records) - failed, "calls_failed_or_truncated": failed,
           "proposed": total, "gold_strings": gold_total,
           "precision": round(sum(r["matched"] for r in rows) / total, 4),
           "recall": round(gold_found / gold_total, 4), "parts": {}}
    unmatched_total = sum(not r["matched"] for r in rows)
    for part in ("copy", "transformed", "unquoted"):
        subset = [r for r in rows if r["part"] == part]
        if not subset:
            out["parts"][part] = {"proposed": 0}
            continue
        unmatched = [r for r in subset if not r["matched"]]
        out["parts"][part] = {
            "proposed": len(subset),
            "share_of_proposed": round(len(subset) / total, 4),
            "surface_matched": sum(r["matched"] for r in subset),
            "surface_precision": round(sum(r["matched"] for r in subset) / len(subset), 4),
            "unmatched": len(unmatched),
            "share_of_all_unmatched": round(len(unmatched) / unmatched_total, 4)
            if unmatched_total else None,
            "unmatched_with_gold_mention_in_quote": sum(r["gold_mention_in_quote"] for r in unmatched),
            "unmatched_same_concept_by_corpus_synonym": sum(r["same_concept"] for r in unmatched),
            "unmatched_whose_name_occurs_elsewhere_in_text": sum(r["name_in_text"] for r in unmatched),
        }
    flagged = [r for r in rows if r["part"] != "copy"]
    out["confidence_auc_for_surface_match"] = (
        round(auc([(r["confidence"], r["matched"]) for r in rows]), 4)
        if auc([(r["confidence"], r["matched"]) for r in rows]) is not None else None)
    by_confidence = sorted(rows, key=lambda r: r["confidence"])[:len(flagged)]
    out["same_review_budget"] = {
        "items_sent_to_review": len(flagged),
        "unmatched_caught_by_copy_check": sum(not r["matched"] for r in flagged),
        "unmatched_caught_by_lowest_confidence": sum(not r["matched"] for r in by_confidence),
        "unmatched_total": unmatched_total,
    }
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("test_file")
    parser.add_argument("corpus_files", nargs="+")
    parser.add_argument("--env", required=True)
    parser.add_argument("--docs", type=int, default=300)
    parser.add_argument("--cache", default=str(Path(__file__).parent / ".cache-bc5cdr"))
    parser.add_argument("--max-usd", type=float, default=0.80)
    args = parser.parse_args()

    import anthropic

    api_key = None
    for line in Path(args.env).read_text(encoding="utf-8").splitlines():
        if line.startswith("ANTHROPIC_API_KEY="):
            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY not found in the env file")
    client = anthropic.Anthropic(api_key=api_key, timeout=120)
    cache_dir = Path(args.cache)
    cache_dir.mkdir(exist_ok=True)

    documents = read_pubtator(args.test_file)
    concept_names = defaultdict(set)
    for path in args.corpus_files:
        for document in read_pubtator(path).values():
            for surface, _, identity in document["mentions"]:
                concept_names[fold(surface)].add(identity)
    doc_ids = sorted(documents)
    random.Random(0).shuffle(doc_ids)
    doc_ids = doc_ids[:args.docs]

    report = {"model": MODEL, "effort": "low", "documents": len(doc_ids),
              "prices_usd_per_mtok": [PRICE_IN, PRICE_OUT], "conditions": {}}
    spent = 0.0
    for condition in PROMPTS:
        def work(doc_id, condition=condition):
            document = documents[doc_id]
            return call(client, cache_dir, condition, doc_id, document["t"] + " " + document["a"])
        with ThreadPoolExecutor(max_workers=6) as pool:
            records = list(pool.map(work, doc_ids))
        cost = sum(r["input_tokens"] * PRICE_IN + r["output_tokens"] * PRICE_OUT
                   for r in records) / 1e6
        spent += sum(r["input_tokens"] * PRICE_IN + r["output_tokens"] * PRICE_OUT
                     for r in records if not r["cached"]) / 1e6
        result = analyse(records, documents, concept_names)
        result["cost_usd_without_cache"] = round(cost, 4)
        report["conditions"][condition] = result
        if spent > args.max_usd:
            report["stopped"] = "spending limit reached"
            break
    report["spent_this_run_usd"] = round(spent, 4)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
