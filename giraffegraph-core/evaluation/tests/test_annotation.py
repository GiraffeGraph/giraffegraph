import csv
import json
from pathlib import Path

import pytest

import build_sheet
import scorer
import to_reference

SHEET = Path(build_sheet.__file__).with_name("hadiths_to_label.tsv")
COLUMNS = ["hadith_id", "collection", "text", "narrators", "notes", "seconds_spent"]

TAGGED_SAMPLE = [
    {
        "coll": "Nasai", "book": "سنن النسائى الصغرى", "num": str(n),
        "raw": f"<SANAD> أخبرنا <NAR>محمد بن منصور</NAR> قال حدثنا <NAR> سفيان</NAR> </SANAD><MATN> متن {n} </MATN>",
        "ref_nars": ["محمد بن منصور", "<NAR> سفيان"], "sanad_len": 2,
    }
    for n in range(1, 21)
]


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_sheet(path, rows):
    """rows: (hadith_id, narrators, notes, seconds_spent)"""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(COLUMNS)
        for hid, narrators, notes, seconds in rows:
            w.writerow([hid, hid.split(":")[0], "متن", narrators, notes, seconds])


# ------------------------------------------------------------- build_sheet
def test_strip_tags_removes_every_sanadset_tag():
    raw = "<SANAD>حدثنا <NAR>قتيبة</NAR> عن <NAR> مروان <IDF> يعني</IDF> ابن محمد</NAR></SANAD> <MATN>قال</MATN>"
    assert build_sheet.strip_tags(raw) == "حدثنا قتيبة عن مروان يعني ابن محمد قال"


def test_strip_tags_leaves_no_stray_angle_bracket():
    assert build_sheet.strip_tags("حدثنا <NAR قتيبة > عن") == "حدثنا عن"
    assert "<" not in build_sheet.strip_tags("a < b <NAR>c</NAR> >")


def test_build_sheet_from_tagged_sample_leaks_no_label(tmp_path):
    sample = tmp_path / "sample.json"
    sample.write_text(json.dumps(TAGGED_SAMPLE, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "sheet.tsv"
    assert build_sheet.main([str(sample), "--out", str(out)]) == 0
    with open(out, encoding="utf-8", newline="") as fh:
        assert next(csv.reader(fh, delimiter="\t")) == COLUMNS
    rows = read_tsv(out)
    assert len(rows) == 20
    assert "<" not in out.read_text(encoding="utf-8")
    for row in rows:
        assert row["text"].startswith("أخبرنا محمد بن منصور قال حدثنا سفيان متن")
        assert row["collection"] == "Nasai"
        assert row["narrators"] == row["notes"] == row["seconds_spent"] == ""


def test_build_sheet_order_is_shuffled_and_reproducible(tmp_path):
    sample = tmp_path / "sample.json"
    sample.write_text(json.dumps(TAGGED_SAMPLE, ensure_ascii=False), encoding="utf-8")
    a, b = tmp_path / "a.tsv", tmp_path / "b.tsv"
    build_sheet.main([str(sample), "--out", str(a)])
    build_sheet.main([str(sample), "--out", str(b)])
    assert a.read_bytes() == b.read_bytes()
    ids = [r["hadith_id"] for r in read_tsv(a)]
    assert sorted(ids) == sorted(f"Nasai:{n}" for n in range(1, 21))
    assert ids != [f"Nasai:{n}" for n in range(1, 21)]


def test_build_sheet_rejects_duplicate_hadith_ids(tmp_path):
    sample = tmp_path / "sample.json"
    sample.write_text(json.dumps(TAGGED_SAMPLE[:1] * 2, ensure_ascii=False), encoding="utf-8")
    assert build_sheet.main([str(sample), "--out", str(tmp_path / "s.tsv")]) != 0


def test_generated_sheet_has_no_tag_and_no_label():
    rows = read_tsv(SHEET)
    assert len(rows) == 50
    assert list(rows[0]) == COLUMNS
    assert len({r["hadith_id"] for r in rows}) == 50
    for row in rows:
        assert "<" not in row["text"] and ">" not in row["text"]
        assert row["text"].strip()
        assert row["narrators"] == row["notes"] == row["seconds_spent"] == ""


def test_generated_sheet_matches_pilot_sample(pilot_sample_path, tmp_path):
    sample = json.loads(pilot_sample_path.read_text(encoding="utf-8"))
    rows = read_tsv(SHEET)
    assert {r["hadith_id"] for r in rows} == {f"{x['coll']}:{x['num']}" for x in sample}
    assert [r["hadith_id"] for r in rows] != [f"{x['coll']}:{x['num']}" for x in sample]
    fresh = tmp_path / "fresh.tsv"
    build_sheet.main([str(pilot_sample_path), "--out", str(fresh)])
    assert fresh.read_bytes() == SHEET.read_bytes()


# ------------------------------------------------------------ to_reference
def test_parse_narrators_splits_mentions_and_flattens_parallel_chains():
    assert to_reference.parse_narrators("محمد بن منصور | سفيان | الزهري") == ["محمد بن منصور", "سفيان", "الزهري"]
    assert to_reference.parse_narrators(" قتيبة | ليث || محمد بن رمح | الليث ") == ["قتيبة", "ليث", "محمد بن رمح", "الليث"]
    assert to_reference.parse_narrators("سفيان|الزهري") == ["سفيان", "الزهري"]
    assert to_reference.parse_narrators("") == []


def test_filled_sheet_becomes_scorer_reference(tmp_path):
    sheet, out = tmp_path / "a.tsv", tmp_path / "ref.jsonl"
    write_sheet(sheet, [
        ("Nasai:693", "محمد بن منصور | سفيان | الزهري | سعيد | أبي هريرة", "", "40"),
        ("Muslim:978", "قتيبة بن سعيد | ليث || محمد بن رمح | الليث", "isimsiz", "80"),
    ])
    assert to_reference.main([str(sheet), "--out", str(out)]) == 0
    assert scorer.load_jsonl(out) == {
        "Nasai:693": ["محمد بن منصور", "سفيان", "الزهري", "سعيد", "أبي هريرة"],
        "Muslim:978": ["قتيبة بن سعيد", "ليث", "محمد بن رمح", "الليث"],
    }


def test_two_sheets_report_mutual_f1_and_mean_seconds(tmp_path, capsys):
    a, b = tmp_path / "a.tsv", tmp_path / "b.tsv"
    write_sheet(a, [
        ("Nasai:693", "محمد بن منصور | سفيان | الزهري | سعيد | أبي هريرة", "", "40"),
        ("Tirmidhi:1", "مالك | نافع | ابن عمر", "", "20"),
    ])
    write_sheet(b, [
        ("Tirmidhi:1", "مالك بن أنس | نافع", "", "30"),
        ("Nasai:693", "محمد بن منصور | سفيان | الزهري | سعيد | أبي هريرة", "", ""),
    ])
    # M1: 5 + 1 shared, A-only 2, B-only 1 -> F1 = 12/15; M2 also pairs مالك with مالك بن أنس -> 14/15
    result = to_reference.agreement(to_reference.read_sheet(a), to_reference.read_sheet(b))
    assert result["M1"]["f1"] == pytest.approx(12 / 15)
    assert result["M2"]["f1"] == pytest.approx(14 / 15)
    swapped = to_reference.agreement(to_reference.read_sheet(b), to_reference.read_sheet(a))
    assert swapped["M1"]["f1"] == pytest.approx(result["M1"]["f1"])
    assert swapped["M2"]["f1"] == pytest.approx(result["M2"]["f1"])

    assert to_reference.main([str(a), str(b)]) == 0
    printed = capsys.readouterr().out
    assert "M1" in printed and "0.8000" in printed
    assert "M2" in printed and "0.9333" in printed
    assert "30.0" in printed  # both annotators average 30 s over the rows they timed


def test_two_sheets_must_cover_the_same_hadiths(tmp_path, capsys):
    a, b = tmp_path / "a.tsv", tmp_path / "b.tsv"
    write_sheet(a, [("Nasai:693", "سفيان", "", "")])
    write_sheet(b, [("Nasai:694", "سفيان", "", "")])
    assert to_reference.main([str(a), str(b)]) != 0
    assert "Nasai:694" in capsys.readouterr().err


def test_sheet_with_missing_column_is_rejected(tmp_path, capsys):
    sheet = tmp_path / "a.tsv"
    sheet.write_text("hadith_id\ttext\nNasai:693\tمتن\n", encoding="utf-8")
    assert to_reference.main([str(sheet), "--out", str(tmp_path / "ref.jsonl")]) != 0
    assert "narrators" in capsys.readouterr().err
