"""Tests for the experiment analysis and the run comparison, on hand-computed inputs."""
import json

import pytest

import analyze_experiment
import compare_runs
import scorer

REFERENCE = {
    "H:1": ["أنس", "سفيان"],
    "H:2": ["مالك"],
    "H:3": ["الزهري"],
    "H:4": ["نافع"],  # the run was stopped before this hadith
    "H:5": ["عمر"],  # the run never received this hadith
}
# H:1  "أنس" matches; "سفيان بن عيينة" contains "سفيان" (M2 only); "زيد" matches nothing.
# H:2  "نافع" is not "مالك".  H:3  nothing proposed.
PROPOSED = {"H:1": ["أنس", "زيد", "سفيان بن عيينة"], "H:2": ["نافع"], "H:3": []}
VALIDATED = {"H:1": ["أنس"], "H:2": ["نافع"], "H:3": []}


def narrator(hadith_id, name, index, *, confidence=0.9, status="validated", reason_codes=()):
    return {
        "hadith_id": hadith_id, "kind": "node", "candidate_id": f"{hadith_id}-{index}",
        "type": "Narrator", "name": name, "confidence": confidence, "status": status,
        "reason_codes": list(reason_codes), "mention_indexes": [index],
    }


CANDIDATES = [
    narrator("H:1", "أنس", 0),
    narrator("H:1", "زيد", 1, confidence=0.4, status="review",
             reason_codes=["node_confidence_threshold"]),
    narrator("H:1", "سفيان بن عيينة", 2, confidence=0.8, status="review",
             reason_codes=["value_not_in_quote"]),
    {"hadith_id": "H:1", "kind": "node", "candidate_id": "H:1-hadith", "type": "Hadith",
     "name": None, "confidence": 0.9, "status": "validated", "reason_codes": []},
    {"hadith_id": "H:1", "kind": "relation", "candidate_id": "H:1-r", "type": "NARRATED_FROM",
     "from_name": "أنس", "to_name": "زيد", "confidence": 0.9, "status": "review",
     "reason_codes": ["relation_dependency_review"]},
    narrator("H:2", "نافع", 0),
]


def call(hadith_id, *, cost, tokens_in, tokens_out, cached=False, error_kind=None):
    return {
        "hadith_id": hadith_id, "call_index": 1, "cached": cached, "cost_usd": cost,
        "input_tokens": tokens_in, "output_tokens": tokens_out,
        "error": None if error_kind is None else "failed", "error_kind": error_kind,
    }


CALLS = [
    call("H:1", cost=0.001, tokens_in=300, tokens_out=30),
    call("H:2", cost=0.002, tokens_in=600, tokens_out=60, cached=True),
    call("H:3", cost=0.003, tokens_in=900, tokens_out=90, error_kind="max_tokens"),
]
OPEN_REVIEW_ITEMS = {"H:1": 3, "H:2": 0, "H:3": 1}


def write_run(directory, *, proposed=PROPOSED, validated=VALIDATED, candidates=None, calls=CALLS,
              open_review_items=None, condition="llm_isnad_chain", not_processed=("H:4",)):
    """Write a run directory. Other mentions than PROPOSED get one validated candidate each."""
    if candidates is None:
        candidates = CANDIDATES if proposed is PROPOSED else [
            narrator(hadith_id, mention, index)
            for hadith_id, mentions in proposed.items()
            for index, mention in enumerate(mentions)
        ]
    directory.mkdir(parents=True)
    for file_name, rows in (
        ("system_proposed.jsonl", [{"hadith_id": h, "mentions": m} for h, m in proposed.items()]),
        ("system_validated.jsonl", [{"hadith_id": h, "mentions": m} for h, m in validated.items()]),
        ("candidates.jsonl", candidates),
        ("calls.jsonl", calls),
    ):
        (directory / file_name).write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
        )
    report = {
        "condition": condition, "model": "claude-haiku-5-5", "effort": "low",
        "provider": "anthropic", "segmentation_strategy": "isnad",
        "budget_stopped": bool(not_processed), "stop_reason": "budget" if not_processed else None,
        "hadith_ids_not_processed": list(not_processed), "cost_usd": 0.004,
        "schema_proposals": [
            {"reason_code": "schema_property_proposal", "kind": "node", "type_name": "Narrator",
             "property_name": "kunya", "count": 2},
        ],
        "candidates_by_reason_code": {
            "node": {"node_confidence_threshold": 1, "value_not_in_quote": 1},
            "relation": {"relation_dependency_review": 1},
        },
        "committed_fact_invariants": {"holds": False},
        "committed_fact_invariants_with_grounding_normalisation": {"holds": True},
        "per_hadith": [
            {"hadith_id": h, "open_review_items": (open_review_items or OPEN_REVIEW_ITEMS).get(h, 0)}
            for h in proposed
        ],
    }
    (directory / "run_report.json").write_text(json.dumps(report), encoding="utf-8")
    return str(directory)


@pytest.fixture
def analysis(tmp_path):
    run = analyze_experiment.load_run(write_run(tmp_path / "run"))
    return analyze_experiment.analyse(run, REFERENCE, n_boot=200, seed=0)


# ------------------------------------------------------------------------ scores
def test_only_hadiths_the_run_processed_are_evaluated(analysis):
    assert analysis["evaluated_hadiths"] == {
        "reference": 5, "evaluated": 3, "processed_by_run": 3, "not_processed_by_run": ["H:4"],
    }
    assert analysis["scores"]["proposed"]["n_hadiths"] == 3
    assert analysis["run"]["stop_reason"] == "budget"


def test_scores_for_proposed_and_validated_output(analysis):
    proposed, validated = analysis["scores"]["proposed"], analysis["scores"]["validated"]

    # M2: H:1 tp 2 fp 1, H:2 fp 1 fn 1, H:3 fn 1.
    assert (proposed["M2"]["tp"], proposed["M2"]["fp"], proposed["M2"]["fn"]) == (2, 2, 2)
    assert (proposed["M2"]["precision"], proposed["M2"]["recall"], proposed["M2"]["f1"]) == (
        0.5, 0.5, 0.5,
    )
    # M1: only "أنس" is an exact match.
    assert (proposed["M1"]["tp"], proposed["M1"]["fp"], proposed["M1"]["fn"]) == (1, 3, 3)
    assert proposed["M1"]["f1"] == 0.25
    assert proposed["M2"]["exact_chain_rate"] == 0.0
    # Validated only: H:1 tp 1 fn 1, H:2 fp 1 fn 1, H:3 fn 1.
    assert (validated["M2"]["tp"], validated["M2"]["fp"], validated["M2"]["fn"]) == (1, 1, 3)
    assert validated["M2"]["precision"] == 0.5
    assert validated["M2"]["recall"] == 0.25
    assert validated["M2"]["f1"] == pytest.approx(1 / 3)
    low, high = proposed["M2"]["ci95"]["f1"]
    assert 0.0 <= low <= 0.5 <= high <= 1.0


def test_system_hadith_missing_from_the_reference_is_an_error(tmp_path):
    run = analyze_experiment.load_run(write_run(tmp_path / "run"))

    with pytest.raises(ValueError, match="system hadith_id not in reference: H:3"):
        analyze_experiment.analyse(run, {"H:1": ["أنس"], "H:2": ["مالك"]}, n_boot=0)


# -------------------------------------------------------------------- gate table
def test_mentions_are_labelled_by_the_m2_alignment():
    assert analyze_experiment.label_mentions(REFERENCE["H:1"], PROPOSED["H:1"]) == [
        True, False, True,
    ]
    assert analyze_experiment.label_mentions(REFERENCE["H:1"], PROPOSED["H:1"], "M1") == [
        True, False, False,
    ]
    # A mention of punctuation only normalises to nothing and is not counted by the scorer.
    assert analyze_experiment.label_mentions(["أنس"], ["،", "أنس"]) == [None, True]
    # Two system mentions cannot both claim one reference mention.
    assert analyze_experiment.label_mentions(["أنس"], ["أنس", "أنس"]) == [True, False]


def test_gate_table_counts_errors_caught_missed_and_false_alarms(analysis):
    gates = analysis["gate_table"]

    # Correct: "أنس" (unflagged), "سفيان بن عيينة" (value_not_in_quote).
    # Wrong:   "زيد" (node_confidence_threshold), "نافع" (unflagged).
    assert (gates["criterion"], gates["mentions"], gates["correct"], gates["wrong"]) == (
        "M2", 4, 2, 2,
    )
    assert gates["rows"] == [
        {"gate": "node_confidence_threshold", "errors_caught": 1, "false_alarms": 0,
         "errors_missed": 1, "precision": 1.0, "recall": 0.5},
        {"gate": "value_not_in_quote", "errors_caught": 0, "false_alarms": 1,
         "errors_missed": 2, "precision": 0.0, "recall": 0.0},
        {"gate": "any gate", "errors_caught": 1, "false_alarms": 1,
         "errors_missed": 1, "precision": 0.5, "recall": 0.5},
    ]


def test_gate_without_flags_or_without_errors_has_no_precision_or_recall():
    records = [{"correct": True, "confidence": 0.9, "reason_codes": []}]

    assert analyze_experiment.gate_table(records)["rows"] == [
        {"gate": "any gate", "errors_caught": 0, "false_alarms": 0, "errors_missed": 0,
         "precision": None, "recall": None},
    ]


def test_mention_without_a_candidate_is_an_error(tmp_path):
    run = analyze_experiment.load_run(write_run(tmp_path / "run", candidates=CANDIDATES[:1]))

    with pytest.raises(ValueError, match="no candidate for mention 1 of H:1"):
        analyze_experiment.analyse(run, REFERENCE, n_boot=0)


# -------------------------------------------------------------------- confidence
def test_auc_is_rank_based_and_counts_ties_as_one_half():
    # Pairs (correct, wrong): (.9,.4) 1, (.9,.9) 1/2, (.8,.4) 1, (.8,.9) 0  ->  2.5 / 4.
    assert analyze_experiment.auc([0.9, 0.8], [0.4, 0.9]) == 0.625
    assert analyze_experiment.auc([0.9, 0.8], [0.1, 0.2]) == 1.0
    assert analyze_experiment.auc([0.1], [0.9, 0.8]) == 0.0
    assert analyze_experiment.auc([0.5, 0.5], [0.5]) == 0.5
    assert analyze_experiment.auc([], [0.5]) is None
    assert analyze_experiment.auc([0.5], []) is None


def test_confidence_auc_and_histogram_of_the_run(analysis):
    confidence = analysis["confidence"]

    assert confidence["auc_correct_vs_wrong"] == 0.625
    filled = {
        (b["from"], b["to"]): (b["correct"], b["wrong"])
        for b in confidence["histogram"] if b["correct"] or b["wrong"]
    }
    assert filled == {(0.4, 0.5): (0, 1), (0.8, 0.9): (1, 0), (0.9, 1.0): (1, 1)}
    assert len(confidence["histogram"]) == 10


def test_confidence_of_exactly_one_falls_in_the_last_bin():
    histogram = analyze_experiment.confidence_analysis(
        [{"correct": True, "confidence": 1.0, "reason_codes": []}]
    )["histogram"]

    assert histogram[-1] == {"from": 0.9, "to": 1.0, "correct": 1, "wrong": 0}


# ------------------------------------------------------------- workload and cost
def test_review_workload_per_hadith(analysis):
    # In review: two narrators and one relation of H:1; nothing in H:2 and H:3.
    assert analysis["review_workload"] == {
        "hadiths": 3,
        "candidates_in_review": 3,
        "candidates_in_review_per_hadith": {"mean": 1.0, "median": 0, "max": 3},
        "open_review_items": 4,
        "share_hadiths_without_review_items": pytest.approx(1 / 3),
    }


def test_cost_and_tokens_per_hadith(analysis):
    cost = analysis["cost"]

    assert (cost["hadiths"], cost["calls"], cost["cached_calls"]) == (3, 3, 1)
    assert (cost["failed_calls"], cost["refused_calls"], cost["truncated_calls"]) == (1, 0, 1)
    assert cost["cost_usd"] == pytest.approx(0.006)
    assert cost["cost_usd_per_hadith"] == pytest.approx(0.002)
    assert cost["cost_usd_per_1000_hadiths"] == pytest.approx(2.0)
    assert cost["cost_usd_spent_by_this_run"] == 0.004
    assert (cost["input_tokens_per_hadith"], cost["output_tokens_per_hadith"]) == (600, 60)
    assert cost["calls_per_hadith"] == 1


# ------------------------------------------------------------------------ output
def test_main_writes_json_and_markdown(tmp_path, capsys):
    run_dir = write_run(tmp_path / "run")
    reference_path = tmp_path / "reference.jsonl"
    reference_path.write_text(
        "".join(
            json.dumps({"hadith_id": h, "mentions": m}, ensure_ascii=False) + "\n"
            for h, m in REFERENCE.items()
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "analysis"

    exit_code = analyze_experiment.main([
        "--run", run_dir, "--reference", str(reference_path), "--bootstrap", "50",
        "--out", str(out_dir),
    ])

    assert exit_code == 0
    written = json.loads((out_dir / "analysis.json").read_text(encoding="utf-8"))
    assert written["gate_table"]["rows"][-1]["errors_caught"] == 1
    assert written["scores"]["proposed"]["bootstrap"] == {
        "resamples": 50, "seed": 0, "unit": "hadith",
    }
    assert written["committed_fact_invariants"] == {
        "exact_quote": False, "quote_with_grounding_normalisation": True,
    }
    markdown = (out_dir / "analysis.md").read_text(encoding="utf-8")
    assert markdown == capsys.readouterr().out.removesuffix("\n")
    assert "Evaluated hadiths: 3 of 5 in the reference" in markdown
    assert "| any gate | 1 | 1 | 1 | 0.500 | 0.500 |" in markdown
    assert "| node_confidence_threshold | 1 | 0 | 1 | 1.000 | 0.500 |" in markdown
    assert "ties count one half): 0.625" in markdown
    assert "| 3 | 3 | 1.000 | 0 | 3 | 4 | 0.333 |" in markdown
    assert "| 3 | 1 | 1 | 0 | 1 | 0.002000 | 2.0000 | 600.0 | 60.0 | 0.004000 |" in markdown
    assert "| schema_property_proposal | node | Narrator | kunya | 2 |" in markdown
    assert "| relation | relation_dependency_review | 1 |" in markdown


def test_main_reports_a_missing_run_directory(tmp_path, capsys):
    reference_path = tmp_path / "reference.jsonl"
    reference_path.write_text('{"hadith_id": "H:1", "mentions": []}\n', encoding="utf-8")

    exit_code = analyze_experiment.main([
        "--run", str(tmp_path / "absent"), "--reference", str(reference_path),
        "--out", str(tmp_path / "analysis"),
    ])

    assert exit_code == 2
    assert "FileNotFoundError" in capsys.readouterr().err


# -------------------------------------------------------------------- comparison
def test_paired_difference_of_two_runs():
    # a: tp 2 fp 2 fn 2 -> P, R, F1 = .5; b: tp 3 fp 1 fn 0 -> P .75, R 1, F1 6/7.
    result = compare_runs.paired_bootstrap([(2, 1, 0), (0, 1, 2)], [(2, 1, 0), (1, 0, 0)], 0, 0)

    assert result["precision"] == {"a": 0.5, "b": 0.75, "difference": -0.25, "ci95": None}
    assert result["recall"] == {"a": 0.5, "b": 1.0, "difference": -0.5, "ci95": None}
    assert result["f1"]["difference"] == pytest.approx(0.5 - 6 / 7)


def test_paired_bootstrap_draws_the_same_hadiths_for_both_runs():
    # Equal per hadith but different across hadiths: with shared resamples every
    # difference is exactly zero, with independent resamples it would not be.
    counts = [(5, 0, 0), (0, 4, 1), (1, 1, 3), (2, 0, 2)]

    result = compare_runs.paired_bootstrap(counts, list(counts), 300, 7)

    for metric in ("precision", "recall", "f1"):
        assert result[metric]["difference"] == 0.0
        assert result[metric]["ci95"] == [0.0, 0.0]


def test_paired_bootstrap_interval_when_every_hadith_differs_alike():
    # Every resample has a: P .5, R 1 and b: P 1, R .5, whatever hadiths it draws.
    result = compare_runs.paired_bootstrap([(1, 1, 0)] * 6, [(1, 0, 1)] * 6, 200, 3)

    assert result["precision"]["ci95"] == [-0.5, -0.5]
    assert result["recall"]["ci95"] == [0.5, 0.5]
    assert result["f1"]["ci95"] == [0.0, 0.0]


def test_paired_bootstrap_interval_covers_the_observed_difference():
    result = compare_runs.paired_bootstrap(
        [(3, 0, 0), (1, 2, 2), (2, 1, 1), (0, 0, 3)],
        [(1, 1, 2), (1, 2, 2), (3, 0, 0), (0, 2, 3)],
        500,
        11,
    )

    for metric in ("precision", "recall", "f1"):
        low, high = result[metric]["ci95"]
        assert low <= result[metric]["difference"] <= high
        assert low < high


def test_paired_bootstrap_rejects_unpaired_input():
    with pytest.raises(ValueError, match="same, non-empty list"):
        compare_runs.paired_bootstrap([(1, 0, 0)], [], 10, 0)


def test_compare_writes_one_row_per_run_and_the_paired_differences(tmp_path, capsys):
    first = write_run(tmp_path / "chain")
    # Second run: H:1 and H:2 exact, H:3 with one extra mention; it also processed H:4.
    second = write_run(
        tmp_path / "rule",
        proposed={"H:1": ["أنس", "سفيان"], "H:2": ["مالك"], "H:3": ["الزهري", "زيد"],
                  "H:4": ["نافع"]},
        validated={"H:1": ["أنس", "سفيان"], "H:2": ["مالك"], "H:3": ["الزهري", "زيد"],
                   "H:4": ["نافع"]},
        calls=[], open_review_items={}, condition="rule", not_processed=(),
    )
    reference_path = tmp_path / "reference.jsonl"
    reference_path.write_text(
        "".join(
            json.dumps({"hadith_id": h, "mentions": m}, ensure_ascii=False) + "\n"
            for h, m in REFERENCE.items()
        ),
        encoding="utf-8",
    )
    out_path = tmp_path / "comparison.md"

    exit_code = compare_runs.main([
        "--runs", first, second, "--reference", str(reference_path), "--out", str(out_path),
        "--bootstrap", "100",
    ])

    assert exit_code == 0
    markdown = out_path.read_text(encoding="utf-8")
    assert markdown == capsys.readouterr().out.removesuffix("\n")
    rows = [line for line in markdown.splitlines() if line.startswith(("| chain |", "| rule |"))]
    summary = {row.split(" | ")[0].strip("| "): row.split(" | ") for row in rows[:2]}
    assert summary["chain"][1:5] == ["llm_isnad_chain", "claude-haiku-5-5", "low", "3"]
    assert summary["chain"][5] == "0.250"
    assert summary["chain"][8].startswith("0.500 [")
    assert summary["chain"][13:16] == ["0.500", "0.500", "0.625"]
    assert summary["chain"][18:] == ["2.0000", "660.0", "1 |"]
    assert summary["rule"][4] == "4"
    assert "different numbers of hadiths" in markdown
    # Shared hadiths H:1-H:3: chain tp 2 fp 2 fn 2; rule tp 4 fp 1 fn 0.
    assert "| chain | rule | 3 | precision | 0.500 | 0.800 | -0.300 | [" in markdown
    assert "| chain | rule | 3 | recall | 0.500 | 1.000 | -0.500 | [" in markdown
    assert "| chain | rule | 3 | f1 | 0.500 | 0.889 | -0.389 | [" in markdown


def test_compare_limits_the_pairs_and_rejects_unknown_or_duplicate_names(tmp_path):
    runs = [write_run(tmp_path / name, not_processed=()) for name in ("a", "b", "c")]

    _, pairs = compare_runs.compare(runs, REFERENCE, n_boot=0)
    _, chosen = compare_runs.compare(runs, REFERENCE, pair_names=[["c", "a"]], n_boot=0)

    assert list(pairs) == [("a", "b"), ("a", "c"), ("b", "c")]
    assert list(chosen) == [("c", "a")]
    assert chosen[("c", "a")]["hadiths"] == 3
    assert chosen[("c", "a")]["metrics"]["f1"] == {
        "a": 0.5, "b": 0.5, "difference": 0.0, "ci95": None,
    }
    with pytest.raises(ValueError, match="unknown run: z"):
        compare_runs.compare(runs, REFERENCE, pair_names=[["a", "z"]], n_boot=0)
    other = write_run(tmp_path / "elsewhere" / "a", not_processed=())
    with pytest.raises(ValueError, match="distinct names"):
        compare_runs.compare([runs[0], other], REFERENCE, n_boot=0)


def test_scorer_alignment_is_the_one_used_for_labels():
    ref = [scorer.normalise(m) for m in REFERENCE["H:1"]]
    hyp = [scorer.normalise(m) for m in PROPOSED["H:1"]]

    assert scorer.match(ref, hyp, "M2") == [(0, 0), (1, 2)]
