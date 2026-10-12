import decision_reapplication as dr


def test_targets_are_matched_by_name_or_by_quote():
    decided = {"h1": [("سفيان", frozenset({"حدثنا سفيان"})), ("مالك", frozenset({"عن مالك"}))]}
    extracted = {
        "h1": [
            ("سفيان", frozenset({"اخبرنا سفيان"})),  # same name, other quote
            ("malik", frozenset({"عن مالك"})),  # other name, same quote
            ("نافع", frozenset({"عن نافع"})),  # new
        ],
        "h2": [("سفيان", frozenset({"حدثنا سفيان"}))],  # other hadith: no target
    }

    assert dr.reapplication(decided, extracted) == {
        "candidates": 4,
        "name": 0.25,
        "quote": 0.25,
        "either": 0.5,
    }


def test_no_candidates():
    assert dr.reapplication({}, {}) == {"candidates": 0}
