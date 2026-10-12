"""Tests for the silver reference builder."""
import json

import pytest

import build_silver_reference
import scorer

SAMPLE = [
    {
        "coll": "Nasai", "num": "693", "raw": "unused",
        "ref_nars": ["محمد بن منصور", "<NAR> سفيان", "مروان <IDF> يعني</IDF> ابن محمد"],
    },
    {"coll": "Muslim", "num": "978", "raw": "unused", "ref_nars": ["<NAR>", "قتيبة بن سعيد"]},
]


def test_reference_keeps_chain_order_and_strips_residual_tags():
    assert build_silver_reference.build_reference(SAMPLE) == [
        {"hadith_id": "Nasai:693", "mentions": ["محمد بن منصور", "سفيان", "مروان يعني ابن محمد"]},
        {"hadith_id": "Muslim:978", "mentions": ["قتيبة بن سعيد"]},
    ]


def test_duplicate_hadith_id_is_rejected():
    with pytest.raises(ValueError, match="duplicate hadith_id: Nasai:693"):
        build_silver_reference.build_reference([SAMPLE[0], SAMPLE[0]])


def test_written_file_is_readable_by_the_scorer(tmp_path):
    sample_path, out_path = tmp_path / "sample.json", tmp_path / "reference.jsonl"
    sample_path.write_text(json.dumps(SAMPLE, ensure_ascii=False), encoding="utf-8")

    assert build_silver_reference.main([str(sample_path), "--out", str(out_path)]) == 0

    reference = scorer.load_jsonl(out_path)
    assert reference == {
        "Nasai:693": ["محمد بن منصور", "سفيان", "مروان يعني ابن محمد"],
        "Muslim:978": ["قتيبة بن سعيد"],
    }
    report = scorer.score(reference, reference, n_boot=0)
    assert report["M1"]["f1"] == 1.0


def test_missing_sample_file_is_reported(tmp_path, capsys):
    assert build_silver_reference.main([str(tmp_path / "absent.json"), "--out", "unused"]) == 2
    assert "error:" in capsys.readouterr().err


def test_pilot_reference_has_every_mention_and_no_tag(pilot_sample_path, tmp_path):
    out_path = tmp_path / "reference.jsonl"

    assert build_silver_reference.main([str(pilot_sample_path), "--out", str(out_path)]) == 0

    reference = scorer.load_jsonl(out_path)
    sample = json.loads(pilot_sample_path.read_text(encoding="utf-8"))
    assert len(reference) == 50
    assert sum(len(mentions) for mentions in reference.values()) == 327
    assert sum("<" in m for x in sample for m in x["ref_nars"]) == 17
    assert not any("<" in m or ">" in m for mentions in reference.values() for m in mentions)
