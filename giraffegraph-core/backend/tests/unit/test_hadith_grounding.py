import pytest

from app.domain.hadith.grounding import (
    quote_in_segment,
    value_equals_reference,
    value_in_quote,
)

SEGMENT_TEXT = "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ . ح ، وحَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ"


def test_quote_in_segment_accepts_verbatim_quote() -> None:
    assert quote_in_segment("حَدَّثَنَا لَيْثٌ", SEGMENT_TEXT)


def test_quote_in_segment_ignores_diacritics_punctuation_and_spacing() -> None:
    assert quote_in_segment("حدثنا  قتيبة بن سعيد، حدثنا ليث", SEGMENT_TEXT)


def test_quote_in_segment_rejects_text_absent_from_segment() -> None:
    assert not quote_in_segment("حَدَّثَنَا مَالِكٌ", SEGMENT_TEXT)


def test_quote_in_segment_rejects_reordered_words() -> None:
    assert not quote_in_segment("سعيد بن قتيبة", SEGMENT_TEXT)


@pytest.mark.parametrize("blank", ["", "   ", "\n\t", "َ ، ."])
def test_quote_in_segment_treats_blank_inputs_as_not_grounded(blank: str) -> None:
    assert not quote_in_segment(blank, SEGMENT_TEXT)
    assert not quote_in_segment("حَدَّثَنَا لَيْثٌ", blank)
    assert not quote_in_segment(blank, blank)


def test_value_in_quote_accepts_value_copied_from_quote() -> None:
    assert value_in_quote("ليث", "حَدَّثَنَا لَيْثٌ")
    assert value_in_quote("لَيْثٌ", "حَدَّثَنَا لَيْثٌ")


def test_value_in_quote_rejects_value_with_added_definite_article() -> None:
    assert not value_in_quote("الليث", "حَدَّثَنَا لَيْثٌ")


def test_value_in_quote_folds_orthographic_variants() -> None:
    assert value_in_quote("ابي هريرة", "عَنْ أَبِي هُرَيْرَةَ")


@pytest.mark.parametrize("blank", ["", "   ", "\n\t", "َ ، ."])
def test_value_in_quote_treats_blank_inputs_as_not_grounded(blank: str) -> None:
    assert not value_in_quote(blank, "حَدَّثَنَا لَيْثٌ")
    assert not value_in_quote("ليث", blank)
    assert not value_in_quote(blank, blank)


def test_value_equals_reference_uses_the_grounding_normaliser() -> None:
    assert value_equals_reference("Muslim:978", "muslim 978")
    assert value_equals_reference(" Muslim:978 ", "Muslim:978")


def test_value_equals_reference_rejects_partial_and_blank_values() -> None:
    assert not value_equals_reference("Muslim:97", "Muslim:978")
    assert not value_equals_reference("978", "Muslim:978")
    assert not value_equals_reference("", "")
    assert not value_equals_reference(" . ", " . ")
