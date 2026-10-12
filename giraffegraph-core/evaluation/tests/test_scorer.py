import importlib
import importlib.util
import itertools
import json
import random
import sys
import types
from fractions import Fraction

import pytest

import scorer
from build_sheet import strip_tags

NESAI_693_REF = ["محمد بن منصور", "سفيان", "الزهري", "سعيد", "ابي هريره"]
NESAI_693_SYS = ["محمد بن منصور قال", "سفيان", "الزهري", "سعيد", "ابي هريره"]


def counts(ref, hyp, criterion):
    r = scorer.score_hadith(ref, hyp, criterion)
    return r["tp"], r["fp"], r["fn"]


# ------------------------------------------------------------- normalisation
def test_normalise_strips_diacritics_and_unifies_letters():
    assert scorer.normalise("أَبِي هُرَيْرَةَ") == "ابي هريره"
    assert scorer.normalise("إِبْرَاهِيمُ بْنُ مُوسَى") == "ابراهيم بن موسي"


def test_normalise_strips_honorific_and_leading_conjunction():
    assert scorer.normalise("عُمَرَ بْنَ الْخَطَّابِ رَضِيَ اللَّهُ عَنْهُ") == "عمر بن الخطاب"
    assert scorer.normalise("و سفيان") == "سفيان"
    # an attached conjunction is part of the token and is kept
    assert scorer.normalise("وسفيان") == "وسفيان"


def test_normalise_keeps_trailing_transmission_verb():
    assert scorer.normalise("محمد بن منصور قال") == "محمد بن منصور قال"


# ------------------------------------------------------------ hand-computed
def test_identical_chain_is_perfect_under_both_criteria():
    for criterion in ("M1", "M2"):
        r = scorer.score_hadith(["ا", "ب", "ج"], ["ا", "ب", "ج"], criterion)
        assert (r["tp"], r["fp"], r["fn"]) == (3, 0, 0)
        assert r["exact_chain"] is True
        assert r["order_concordance"] == 1.0


def test_empty_system_chain_is_all_false_negatives():
    r = scorer.score_hadith(["ا", "ب", "ج"], [], "M2")
    assert (r["tp"], r["fp"], r["fn"]) == (0, 0, 3)
    assert r["exact_chain"] is False
    assert r["order_concordance"] is None


def test_m1_requires_exact_equality_m2_accepts_substring():
    assert counts(["سعيد بن المسيب"], ["سعيد"], "M1") == (0, 1, 1)
    assert counts(["سعيد بن المسيب"], ["سعيد"], "M2") == (1, 0, 0)
    assert counts(["سعيد"], ["سعيد بن المسيب"], "M2") == (1, 0, 0)


def test_m2_token_f1_threshold_is_inclusive_at_060():
    # 3 shared of 5 and 5 content tokens: F1 = 0.60 exactly -> match
    assert counts(["k1 k2 k3 a1 a2"], ["k1 k2 k3 b1 b2"], "M2") == (1, 0, 0)
    # 2 shared of 3 and 3: F1 = 0.667 -> match
    assert counts(["k1 k2 a1"], ["k1 k2 b1"], "M2") == (1, 0, 0)
    # 1 shared of 2 and 2: F1 = 0.50 -> no match
    assert counts(["k1 a1"], ["k1 b1"], "M2") == (0, 1, 1)


def test_m2_token_f1_ignores_function_tokens():
    # shared 'بن' is not content: content overlap is 1 of 2 and 2 -> 0.50
    assert counts(["محمد بن سعيد"], ["احمد بن سعيد"], "M2") == (0, 1, 1)


def test_similarity_weights():
    assert scorer.similarity("سفيان", "سفيان", "M1") == 1
    assert scorer.similarity("سفيان", "سفيان الثوري", "M1") == 0
    assert scorer.similarity("سفيان", "سفيان الثوري", "M2") == Fraction(9, 10)
    assert scorer.similarity("k1 k2 a1", "k1 k2 b1", "M2") == Fraction(2, 3)
    assert scorer.similarity("k1 a1", "k1 b1", "M2") == 0


def test_alignment_is_maximum_weight_not_greedy():
    # Greedy takes the exact pair (ref0, sys1) first and strands ref1,
    # whose only partner is sys1. The optimum keeps both mentions matched.
    ref = ["سفيان", "سفيان بن عيينه"]
    hyp = ["سفيان الثوري", "سفيان"]
    assert counts(ref, hyp, "M2") == (2, 0, 0)
    assert sorted(scorer.match(ref, hyp, "M2")) == [(0, 0), (1, 1)]


def test_equal_weight_ties_prefer_more_matched_mentions():
    f = Fraction
    sim = [
        [f(9, 10), f(3, 5), f(0)],
        [f(0), f(9, 10), f(3, 5)],
        [f(3, 5), f(0), f(0)],
    ]
    # {(0,0),(1,1)} and {(0,1),(1,2),(2,0)} both weigh 1.8
    assert sorted(scorer.match_matrix(sim)) == [(0, 1), (1, 2), (2, 0)]


def test_repeated_mentions_are_not_cross_matched():
    ref = ["سفيان", "الزهري", "سفيان", "الزهري"]
    r = scorer.score_hadith(ref, list(ref), "M1")
    assert r["exact_chain"] is True
    assert r["order_concordance"] == 1.0


def test_order_concordance_and_exact_chain_on_reordered_chain():
    r = scorer.score_hadith(["ا", "ب", "ج"], ["ب", "ا", "ج"], "M1")
    assert (r["tp"], r["fp"], r["fn"]) == (3, 0, 0)
    assert r["exact_chain"] is False
    assert r["order_concordance"] == pytest.approx(2 / 3)
    r = scorer.score_hadith(["ا", "ب", "ج"], ["ج", "ب", "ا"], "M1")
    assert r["order_concordance"] == 0.0


def test_extra_system_mention_breaks_exact_chain():
    r = scorer.score_hadith(["ا", "ب"], ["ا", "ب", "ج"], "M1")
    assert (r["tp"], r["fp"], r["fn"]) == (2, 1, 0)
    assert r["exact_chain"] is False


def test_assignment_matches_brute_force_on_random_matrices():
    rng = random.Random(1)
    for _ in range(300):
        n, m = rng.randint(1, 5), rng.randint(1, 5)
        w = [[rng.choice([0, 0, 1, 3, 6, 9, 10]) for _ in range(m)] for _ in range(n)]
        cols = scorer.max_weight_assignment(w)
        got = sum(w[i][j] for i, j in enumerate(cols) if j is not None)
        assert len({j for j in cols if j is not None}) == sum(j is not None for j in cols)
        if n <= m:
            best = max(sum(w[i][p[i]] for i in range(n)) for p in itertools.permutations(range(m), n))
        else:
            best = max(sum(w[p[j]][j] for j in range(m)) for p in itertools.permutations(range(n), m))
        assert got == best


# ---------------------------------------------------------------- Nesâî 693
def test_nesai_693_m1_penalises_glued_transmission_verb():
    assert counts(NESAI_693_REF, NESAI_693_SYS, "M1") == (4, 1, 1)


def test_nesai_693_m2_accepts_all_five():
    assert counts(NESAI_693_REF, NESAI_693_SYS, "M2") == (5, 0, 0)


# -------------------------------------------------------------- aggregation
def test_micro_average_over_hadiths():
    reference = {"t:1": ["ا", "ب"], "t:2": ["ج", "د", "ه"]}
    system = {"t:1": ["ا", "ب", "ز"], "t:2": ["ج"]}
    m1 = scorer.score(reference, system, n_boot=200, seed=0)["M1"]
    assert (m1["tp"], m1["fp"], m1["fn"]) == (3, 1, 2)
    assert m1["precision"] == pytest.approx(3 / 4)
    assert m1["recall"] == pytest.approx(3 / 5)
    assert m1["f1"] == pytest.approx(2 / 3)
    assert m1["f0.5"] == pytest.approx(5 / 7)
    assert m1["exact_chain_rate"] == 0.0
    assert m1["order_concordance"] == 1.0  # only t:1 has two matched mentions


def test_hadith_missing_from_system_counts_as_zero_mentions():
    reference = {"t:1": ["ا", "ب"], "t:2": ["ج", "د"]}
    report = scorer.score(reference, {"t:1": ["ا", "ب"]}, n_boot=200, seed=0)
    assert report["n_hadiths"] == 2
    assert report["n_missing_from_system"] == 1
    m1 = report["M1"]
    assert (m1["tp"], m1["fp"], m1["fn"]) == (2, 0, 2)
    assert m1["exact_chain_rate"] == 0.5


def test_system_hadith_absent_from_reference_is_an_error():
    with pytest.raises(ValueError, match="t:9"):
        scorer.score({"t:1": ["ا"]}, {"t:1": ["ا"], "t:9": ["ب"]}, n_boot=10, seed=0)


def test_bootstrap_is_seeded_and_brackets_the_point_estimate():
    rng = random.Random(3)
    names = ["ا", "ب", "ج", "د", "ه", "ح", "ط", "ك"]
    reference = {f"t:{k}": rng.sample(names, rng.randint(2, 7)) for k in range(40)}
    system = {k: v[: rng.randint(0, len(v))] + ["ز"] * rng.randint(0, 2) for k, v in reference.items()}
    a = scorer.score(reference, system, n_boot=500, seed=0)
    b = scorer.score(reference, system, n_boot=500, seed=0)
    c = scorer.score(reference, system, n_boot=500, seed=1)
    assert a == b
    assert a["M1"]["ci95"] != c["M1"]["ci95"]
    for stat in ("precision", "recall", "f1"):
        lo, hi = a["M1"]["ci95"][stat]
        assert lo < a["M1"][stat] < hi


def test_report_does_not_depend_on_hadith_order():
    rng = random.Random(5)
    names = ["ا", "ب", "ج", "د", "ه", "ح", "ط", "ك"]
    reference = {f"t:{k}": rng.sample(names, rng.randint(2, 7)) for k in range(40)}
    system = {k: v[: rng.randint(0, len(v))] + ["ز"] * rng.randint(0, 2) for k, v in reference.items()}
    reordered = dict(sorted(reference.items(), key=lambda kv: rng.random()))
    assert list(reordered) != list(reference)
    assert scorer.score(reordered, system, n_boot=300, seed=0) == scorer.score(reference, system, n_boot=300, seed=0)


def test_bootstrap_interval_collapses_when_every_hadith_is_perfect():
    reference = {f"t:{k}": ["ا", "ب"] for k in range(5)}
    m1 = scorer.score(reference, dict(reference), n_boot=100, seed=0)["M1"]
    assert m1["ci95"] == {"precision": [1.0, 1.0], "recall": [1.0, 1.0], "f1": [1.0, 1.0]}


# ---------------------------------------------------------------------- CLI
def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def test_cli_writes_report(tmp_path, capsys):
    write_jsonl(tmp_path / "ref.jsonl", [{"hadith_id": "Nasai:693", "mentions": NESAI_693_REF}])
    write_jsonl(tmp_path / "sys.jsonl", [{"hadith_id": "Nasai:693", "mentions": NESAI_693_SYS}])
    out = tmp_path / "report.json"
    rc = scorer.main([
        "--system", str(tmp_path / "sys.jsonl"),
        "--reference", str(tmp_path / "ref.jsonl"),
        "--bootstrap", "50", "--seed", "0", "--out", str(out),
    ])
    assert rc == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert (report["M1"]["tp"], report["M1"]["fp"], report["M1"]["fn"]) == (4, 1, 1)
    assert (report["M2"]["tp"], report["M2"]["fp"], report["M2"]["fn"]) == (5, 0, 0)
    assert report["M2"]["exact_chain_rate"] == 1.0
    assert report["bootstrap"] == {"resamples": 50, "seed": 0, "unit": "hadith"}
    assert json.loads(capsys.readouterr().out) == report


def test_cli_rejects_system_only_hadith(tmp_path, capsys):
    write_jsonl(tmp_path / "ref.jsonl", [{"hadith_id": "a:1", "mentions": ["ا"]}])
    write_jsonl(tmp_path / "sys.jsonl", [{"hadith_id": "a:2", "mentions": ["ا"]}])
    rc = scorer.main(["--system", str(tmp_path / "sys.jsonl"), "--reference", str(tmp_path / "ref.jsonl")])
    assert rc != 0
    assert "a:2" in capsys.readouterr().err


def test_load_jsonl_rejects_duplicate_ids(tmp_path):
    write_jsonl(tmp_path / "ref.jsonl", [{"hadith_id": "a:1", "mentions": []}] * 2)
    with pytest.raises(ValueError, match="a:1"):
        scorer.load_jsonl(tmp_path / "ref.jsonl")


# --------------------------------------------------------- pilot regression
def load_pilot(path):
    """Import the read-only pilot script without writing bytecode next to it.

    Only its pure-Python `rule_parse` is needed, so numpy/scipy are replaced by
    empty placeholders for the duration of the import when they are absent.
    Returns (module, True if the real numpy/scipy were available).
    """
    stubbed = []
    for name in ("numpy", "scipy", "scipy.optimize"):
        try:
            importlib.import_module(name)
        except ImportError:
            sys.modules[name] = types.ModuleType(name)
            stubbed.append(name)
    if "scipy.optimize" in stubbed:
        sys.modules["scipy.optimize"].linear_sum_assignment = None
    spec = importlib.util.spec_from_file_location("pilot_isnad", path)
    module = importlib.util.module_from_spec(spec)
    write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - any import failure means "cannot run"
        pytest.skip(f"pilot script could not be imported: {exc!r}")
    finally:
        sys.dont_write_bytecode = write_bytecode
        for name in stubbed:
            del sys.modules[name]
    return module, not stubbed


@pytest.fixture(scope="module")
def pilot(pilot_script_path, pilot_sample_path):
    module, has_scipy = load_pilot(pilot_script_path)
    sample = json.loads(pilot_sample_path.read_text(encoding="utf-8"))
    return module, has_scipy, sample


def hadith_id(x):
    return f"{x['coll']}:{x['num']}"


def test_pilot_rule_parser_reproduces_reported_f1(pilot):
    """Reported pilot values: M1 F1 0.628, M2 F1 0.879 (pilot_summary.json).

    The pilot removed residual Sanadset tags from `ref_nars` in memory before
    scoring; the saved pilot_sample.json still carries them, so the same
    clean-up is applied to the reference here.
    """
    module, _, sample = pilot
    assert len(sample) == 50
    reference = {hadith_id(x): [strip_tags(m) for m in x["ref_nars"]] for x in sample}
    system = {hadith_id(x): module.rule_parse(x["raw"]) for x in sample}
    assert len(reference) == 50
    report = scorer.score(reference, system, n_boot=200, seed=0)
    m1, m2 = report["M1"], report["M2"]
    assert m1["f1"] == pytest.approx(0.628, abs=0.01)
    assert m2["f1"] == pytest.approx(0.879, abs=0.01)
    assert (m1["tp"], m1["fp"], m1["fn"]) == (208, 127, 119)
    assert (m2["tp"], m2["fp"], m2["fn"]) == (291, 44, 36)


def test_residual_tags_in_saved_silver_labels_lower_m1(pilot):
    """Scored exactly as saved, 17 tagged reference mentions cost M1 11 matches."""
    module, _, sample = pilot
    assert sum("<" in m for x in sample for m in x["ref_nars"]) == 17
    reference = {hadith_id(x): x["ref_nars"] for x in sample}
    system = {hadith_id(x): module.rule_parse(x["raw"]) for x in sample}
    report = scorer.score(reference, system, n_boot=200, seed=0)
    m1, m2 = report["M1"], report["M2"]
    assert (m1["tp"], m1["fp"], m1["fn"]) == (197, 138, 130)
    assert (m2["tp"], m2["fp"], m2["fn"]) == (291, 44, 36)


def test_per_hadith_counts_equal_pilot_score_one(pilot):
    module, has_scipy, sample = pilot
    if not has_scipy:
        pytest.skip("numpy/scipy not installed; pilot score_one cannot run")
    for x in sample:
        hyp = module.rule_parse(x["raw"])
        for ref in (x["ref_nars"], [strip_tags(m) for m in x["ref_nars"]]):
            for criterion, mode in (("M1", "strict"), ("M2", "lenient")):
                theirs = module.score_one(ref, hyp, x["raw"], mode)
                ours = scorer.score_hadith(ref, hyp, criterion)
                assert (ours["tp"], ours["fp"], ours["fn"]) == (theirs["tp"], theirs["fp"], theirs["fn"]), (
                    hadith_id(x), criterion)
