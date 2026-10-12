import pytest

from app.domain.hadith.grounding import quote_in_segment, value_in_quote


@pytest.mark.parametrize(
    ("value", "quote"),
    [
        ("alice", "Alice met Bob."),
        ("ALICE", "alice met bob"),
        ("Jean Luc", "Dr. Jean-Luc arrived"),
        ("şükrü gündoğdu", "ŞÜKRÜ GÜNDOĞDU geldi"),
        ("strasse", "Die Straße ist lang"),
        ("ليث", "حَدَّثَنَا لَيْثٌ"),
    ],
)
def test_value_in_quote_ignores_case_and_punctuation_in_any_script(
    value: str,
    quote: str,
) -> None:
    assert value_in_quote(value, quote)


@pytest.mark.parametrize(
    ("value", "quote"),
    [
        ("Alicia", "Alice met Bob."),
        ("Bob Alice", "Alice met Bob."),
        ("الليث", "حَدَّثَنَا لَيْثٌ"),
    ],
)
def test_value_in_quote_rejects_text_absent_from_quote(value: str, quote: str) -> None:
    assert not value_in_quote(value, quote)


def test_quote_in_segment_matches_latin_quote_with_different_case_and_spacing() -> None:
    segment_text = "Ali enters the room.\nA fight starts in the alley."

    assert quote_in_segment("ali enters  the ROOM", segment_text)
    assert not quote_in_segment("Ali leaves the room", segment_text)
