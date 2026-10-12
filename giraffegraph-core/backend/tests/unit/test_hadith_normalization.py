import json
import re
import unicodedata
from pathlib import Path

import pytest

from app.domain.hadith.normalization import normalize_arabic, normalize_arabic_with_offsets

PILOT_SAMPLE_PATH = Path(
    "/Users/efe/projects/GiraffeGraph/claude-science-results/pilot_sample.json"
)


def _pilot_norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]", "", value)
    value = re.sub(r"[،.؛:!؟\"'()\[\]{}«»\-–—/\\*·]", " ", value)
    value = re.sub(r"[أإآٱ]", "ا", value)
    value = value.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    return re.sub(r"\s+", " ", value).strip()


def test_normalize_arabic_strips_diacritics_and_tatweel() -> None:
    assert normalize_arabic("حَدَّثَنَا") == "حدثنا"
    assert normalize_arabic("مـحـمـد") == "محمد"
    assert normalize_arabic("الرَّحْمٰن") == "الرحمن"


def test_normalize_arabic_folds_letter_variants() -> None:
    assert normalize_arabic("أإآٱ") == "اااا"
    assert normalize_arabic("موسى") == "موسي"
    assert normalize_arabic("فاطمة") == "فاطمه"
    assert normalize_arabic("مؤمن") == "مومن"
    assert normalize_arabic("عائشة") == "عايشه"


def test_normalize_arabic_replaces_punctuation_and_collapses_whitespace() -> None:
    assert normalize_arabic('  قَالَ :  « نَعَمْ » ،\n"لا" . ') == "قال نعم لا"


def test_normalize_arabic_returns_empty_for_blank_or_mark_only_input() -> None:
    assert normalize_arabic("") == ""
    assert normalize_arabic(" \n\t ") == ""
    assert normalize_arabic("َّ ، .") == ""


def test_normalize_arabic_expands_compatibility_forms() -> None:
    assert normalize_arabic("ﷺ") == "صلي الله عليه وسلم"
    assert normalize_arabic("ﻻ") == "لا"


def test_normalize_arabic_is_idempotent() -> None:
    normalized = normalize_arabic("حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ .")

    assert normalize_arabic(normalized) == normalized


def test_normalize_arabic_with_offsets_maps_spans_back_to_source() -> None:
    source = "  حَدَّثَنَا لَيْثٌ ، عَنِ ابْنِ شِهَابٍ ."

    normalized = normalize_arabic_with_offsets(source)

    assert normalized.text == "حدثنا ليث عن ابن شهاب"
    assert normalized.text == normalize_arabic(source)
    assert source[slice(*normalized.source_span(0, 5))] == "حَدَّثَنَا"
    assert source[slice(*normalized.source_span(6, 9))] == "لَيْثٌ"
    assert source[slice(*normalized.source_span(13, 21))] == "ابْنِ شِهَابٍ"


def test_normalize_arabic_with_offsets_keeps_trailing_tatweel_inside_span() -> None:
    source = "قالـ : محمدـــ"

    normalized = normalize_arabic_with_offsets(source)

    assert normalized.text == "قال محمد"
    assert source[slice(*normalized.source_span(0, 3))] == "قالـ"
    assert source[slice(*normalized.source_span(4, 8))] == "محمدـــ"


def test_normalize_arabic_matches_pilot_normalisation_on_sample() -> None:
    if not PILOT_SAMPLE_PATH.exists():
        pytest.skip(f"pilot sample not found: {PILOT_SAMPLE_PATH}")
    records = json.loads(PILOT_SAMPLE_PATH.read_text(encoding="utf-8"))

    for record in records:
        texts = [record["raw"], *record["ref_nars"]]
        for text in texts:
            assert normalize_arabic(text) == _pilot_norm(text)
