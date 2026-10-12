import identity_baseline as ib


def test_grouping_by_key_counts_conflation_and_splits():
    mentions = [
        ("h1", "سفيان", 10),
        ("h2", "سفيان", 11),
        ("h3", "سفيان", 10),
        ("h4", "سفيان الثوري", 10),
        ("h5", "مالك", 20),
    ]
    report = ib.evaluate(mentions, ib.exact_key)

    assert report["mentions"] == 5
    assert report["distinct_narrator_ids"] == 3
    assert report["distinct_keys"] == 3
    assert report["keys_covering_more_than_one_person"] == 1
    assert report["mentions_under_such_keys"] == 3
    assert report["people_split_over_several_keys"] == 1
    assert report["pairwise"]["same_key_pairs"] == 3
    assert report["pairwise"]["same_person_pairs"] == 3
    assert report["pairwise"]["pairs_in_both"] == 1
    assert report["pairwise"]["precision"] == 1 / 3
    assert report["pairwise"]["recall"] == 1 / 3


def test_placeholder_ids_are_skipped(tmp_path):
    path = tmp_path / "chains.jsonl"
    path.write_text(
        '{"hadith_id": "a", "chains": [["x", "y"]], "narrator_ids": [[1, 7]]}\n',
        encoding="utf-8",
    )
    mentions, skipped = ib.load_mentions(path)

    assert mentions == [("a", "y", 7)]
    assert skipped == 1
