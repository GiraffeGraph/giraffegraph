import extra_tables


def test_mention_bins():
    assert extra_tables.mention_bin(2) == "2-4"
    assert extra_tables.mention_bin(4) == "2-4"
    assert extra_tables.mention_bin(5) == "5-6"
    assert extra_tables.mention_bin(6) == "5-6"
    assert extra_tables.mention_bin(7) == "7-11"


def test_grouped_scores_each_group_separately():
    items = {
        "A:1": {"tp": 2, "fp": 0, "fn": 0, "exact_chain": True, "order_concordance": 1.0},
        "A:2": {"tp": 1, "fp": 1, "fn": 1, "exact_chain": False, "order_concordance": None},
        "B:1": {"tp": 0, "fp": 0, "fn": 3, "exact_chain": False, "order_concordance": None},
    }
    groups = extra_tables.grouped(items, lambda hadith_id: hadith_id.split(":")[0])

    assert groups["A"]["hadiths"] == 2
    assert (groups["A"]["tp"], groups["A"]["fp"], groups["A"]["fn"]) == (3, 1, 1)
    assert groups["A"]["precision"] == 0.75
    assert groups["B"]["recall"] == 0.0
