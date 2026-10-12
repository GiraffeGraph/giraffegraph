import json
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest

from app.domain.hadith.normalization import normalize_arabic
from app.domain.hadith.segmenter import SegmentedHadith, segment_isnad

PILOT_SAMPLE_PATH = Path(
    "/Users/efe/projects/GiraffeGraph/claude-science-results/pilot_sample.json"
)


def _load_pilot_sample() -> list[dict[str, Any]]:
    if not PILOT_SAMPLE_PATH.exists():
        pytest.skip(f"pilot sample not found: {PILOT_SAMPLE_PATH}")
    records: list[dict[str, Any]] = json.loads(PILOT_SAMPLE_PATH.read_text(encoding="utf-8"))
    return records


def _mention_texts(segmented: SegmentedHadith) -> list[list[str]]:
    return [[mention.text for mention in chain.mentions] for chain in segmented.chains]


def _assert_structure(source: str, segmented: SegmentedHadith) -> None:
    previous_end = 0
    for chain_index, chain in enumerate(segmented.chains, start=1):
        assert chain.chain_no == chain_index
        assert chain.mentions
        for mention_index, mention in enumerate(chain.mentions, start=1):
            assert mention.position == mention_index
            assert mention.text != ""
            assert mention.text == mention.text.strip()
            assert source[mention.start : mention.end] == mention.text
            assert mention.start >= previous_end
            assert mention.sigha != ""
            previous_end = mention.end
    if segmented.matn_start is not None:
        assert 0 <= segmented.matn_start < len(source)


def test_segment_isnad_returns_mentions_with_sigha_and_offsets() -> None:
    source = (
        "حَدَّثَنَا سُفْيَانُ ، عَنِ الزُّهْرِيِّ ، عَنْ أَبِي هُرَيْرَةَ ، "
        "عَنْ رَسُولِ اللَّهِ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ ، قَالَ : لَا تُشَدُّ الرِّحَالُ"
    )

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["سُفْيَانُ", "الزُّهْرِيِّ", "أَبِي هُرَيْرَةَ"]]
    chain = segmented.chains[0]
    assert chain.chain_no == 1
    assert [mention.sigha for mention in chain.mentions] == ["حدثنا", "عن", "عن"]
    assert [mention.position for mention in chain.mentions] == [1, 2, 3]
    assert chain.mentions[1].start == source.index("الزُّهْرِيِّ")
    assert chain.mentions[1].end == source.index("الزُّهْرِيِّ") + len("الزُّهْرِيِّ")
    _assert_structure(source, segmented)


def test_segment_isnad_returns_matn_boundary_offset() -> None:
    source = "حَدَّثَنَا سُفْيَانُ ، عَنْ أَبِي هُرَيْرَةَ ، أَنَّ النَّبِيَّ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ نَامَ"

    segmented = segment_isnad(source)

    assert segmented.matn_start == source.index("النَّبِيَّ")
    assert _mention_texts(segmented) == [["سُفْيَانُ", "أَبِي هُرَيْرَةَ"]]


def test_segment_isnad_splits_parallel_chains_at_tahwil_marker() -> None:
    source = "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ . ح ، حَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ ، أَخْبَرَنَا اللَّيْثُ ، عَنِ ابْنِ شِهَابٍ"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [
        ["قُتَيْبَةُ بْنُ سَعِيدٍ", "لَيْثٌ"],
        ["مُحَمَّدُ بْنُ رُمْحٍ", "اللَّيْثُ", "ابْنِ شِهَابٍ"],
    ]
    assert [chain.chain_no for chain in segmented.chains] == [1, 2]
    assert [mention.sigha for mention in segmented.chains[1].mentions] == ["حدثنا", "اخبرنا", "عن"]
    assert [mention.position for mention in segmented.chains[1].mentions] == [1, 2, 3]
    assert segmented.matn_start is None
    _assert_structure(source, segmented)


def test_segment_isnad_keeps_first_narrator_of_chain_opened_by_waw_prefixed_sigha() -> None:
    source = "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ . ح ، وحَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ ، أَخْبَرَنَا اللَّيْثُ ، عَنِ ابْنِ شِهَابٍ"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [
        ["قُتَيْبَةُ بْنُ سَعِيدٍ", "لَيْثٌ"],
        ["مُحَمَّدُ بْنُ رُمْحٍ", "اللَّيْثُ", "ابْنِ شِهَابٍ"],
    ]
    assert [mention.sigha for mention in segmented.chains[1].mentions] == ["حدثنا", "اخبرنا", "عن"]
    assert segmented.chains[1].mentions[0].start == source.index("مُحَمَّدُ")
    _assert_structure(source, segmented)


def test_segment_isnad_reads_waw_prefixed_sigha_at_start_of_text() -> None:
    source = "وحَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، عَنْ مَالِكٍ"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["قُتَيْبَةُ بْنُ سَعِيدٍ", "مَالِكٍ"]]
    assert [mention.sigha for mention in segmented.chains[0].mentions] == ["حدثنا", "عن"]
    _assert_structure(source, segmented)


def test_segment_isnad_ends_mention_before_conjunction_prefixed_sigha() -> None:
    source = "حَدَّثَنَا سُفْيَانُ ، فَحَدَّثَنِي الزُّهْرِيُّ ، وَعَنْ سَالِمٍ"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["سُفْيَانُ", "الزُّهْرِيُّ", "سَالِمٍ"]]
    assert [mention.sigha for mention in segmented.chains[0].mentions] == ["حدثنا", "حدثني", "عن"]
    _assert_structure(source, segmented)


def test_segment_isnad_ignores_conjunction_prefixed_particles_in_matn() -> None:
    source = "حَدَّثَنَا لَيْثٌ ، عَنِ النَّبِيِّ قَالَ فَإِنَّ شِدَّةَ الْحَرِّ وَأَنَا مَعَهُ وَأَنَّ الْحَرَّ شَدِيدٌ"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["لَيْثٌ"]]


def test_segment_isnad_starts_new_chain_for_isnad_following_matn() -> None:
    source = (
        "حَدَّثَنَا لَيْثٌ ، عَنْ نَافِعٍ ، عَنِ النَّبِيِّ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ قَالَ الْحَرُّ . حَدَّثَنِي حَرْمَلَةُ ، أَخْبَرَنَا ابْنُ وَهْبٍ"
    )

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["لَيْثٌ", "نَافِعٍ"], ["حَرْمَلَةُ", "ابْنُ وَهْبٍ"]]
    assert [chain.chain_no for chain in segmented.chains] == [1, 2]
    assert segmented.matn_start == source.index("النَّبِيِّ")
    _assert_structure(source, segmented)


def test_segment_isnad_splits_co_narrators_joined_by_standalone_waw() -> None:
    source = "حَدَّثَنَا أَبُو بَكْرٍ و عُثْمَانُ ، عَنْ جَرِيرٍ"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["أَبُو بَكْرٍ", "عُثْمَانُ", "جَرِيرٍ"]]
    assert [mention.sigha for mention in segmented.chains[0].mentions] == ["حدثنا", "حدثنا", "عن"]
    _assert_structure(source, segmented)


def test_segment_isnad_excludes_honorific_from_mention() -> None:
    source = "سَمِعْتُ عُمَرَ بْنَ الْخَطَّابِ رَضِيَ اللَّهُ عَنْهُ ، يَقُولُ : كُنَّا مَعَ رَسُولِ اللَّهِ"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["عُمَرَ بْنَ الْخَطَّابِ"]]
    assert segmented.chains[0].mentions[0].sigha == "سمعت"


def test_segment_isnad_ends_stop_word_homograph_name_at_honorific() -> None:
    source = "عَنْ عَلِيٍّ رَضِيَ اللَّهُ عَنْهُ ، قَالَ : كُنَّا فِي جَنَازَةٍ"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["عَلِيٍّ"]]


def test_segment_isnad_keeps_name_following_leading_honorific() -> None:
    source = "عَنْ أُمِّ الْمُؤْمِنِينَ عَائِشَةَ ، عَنِ النَّبِيِّ"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["عَائِشَةَ"]]


def test_segment_isnad_strips_leading_connectives_from_mention() -> None:
    source = "حَدَّثَنَا ثُمَّ قَالَ سُفْيَانُ ، عَنِ الزُّهْرِيِّ"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["سُفْيَانُ", "الزُّهْرِيِّ"]]


def test_segment_isnad_drops_candidates_without_name_tokens() -> None:
    source = "حَدَّثَنَا سُفْيَانُ ، عَنْ مثله"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["سُفْيَانُ"]]


def test_segment_isnad_limits_mention_to_nine_tokens() -> None:
    source = "عَنْ زيد بن عمرو بن خالد بن سعد بن بكر بن مالك بن نصر"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["زيد بن عمرو بن خالد بن سعد بن بكر"]]


def test_segment_isnad_drops_immediately_repeated_mention() -> None:
    source = "حَدَّثَنَا سُفْيَانُ ، عَنْ سُفْيَانَ ، عَنِ الزُّهْرِيِّ"

    segmented = segment_isnad(source)

    assert _mention_texts(segmented) == [["سُفْيَانُ", "الزُّهْرِيِّ"]]
    assert segmented.chains[0].mentions[0].start == source.index("سُفْيَانُ")
    assert [mention.position for mention in segmented.chains[0].mentions] == [1, 2]


@pytest.mark.parametrize("source", ["", "   ", "قَالَ رَجُلٌ لِصَاحِبِهِ"])
def test_segment_isnad_returns_no_chains_without_transmission_formula(source: str) -> None:
    segmented = segment_isnad(source)

    assert segmented.chains == ()
    assert segmented.matn_start is None


def test_segment_isnad_result_is_immutable() -> None:
    segmented = segment_isnad("حَدَّثَنَا سُفْيَانُ")

    with pytest.raises(FrozenInstanceError):
        segmented.chains[0].mentions[0].start = 0  # type: ignore[misc]


@pytest.mark.parametrize(
    ("collection", "number", "chain_no", "first_narrator", "sigha"),
    [
        ("Muslim", "978", 2, "محمد بن رمح", "حدثنا"),
        ("Muslim", "978", 3, "حرمله بن يحيي", "حدثني"),
        ("AbuDawud", "3122", 2, "احمد بن عبد الواحد الدمشقي", "حدثنا"),
        ("IbnMajah", "1123", 2, "محمد بن رمح", "حدثنا"),
        ("Muslim", "3745", 1, "ابو بكر بن ابي شيبه", "حدثنا"),
        ("Muslim", "3745", 2, "ابن نمير", "حدثنا"),
        ("Muslim", "1003", 1, "عون بن سلام الكوفي", "حدثنا"),
    ],
)
def test_segment_isnad_keeps_narrator_after_waw_prefixed_sigha_on_pilot_sample(
    collection: str,
    number: str,
    chain_no: int,
    first_narrator: str,
    sigha: str,
) -> None:
    records = _load_pilot_sample()
    source = next(
        record["raw"]
        for record in records
        if record["coll"] == collection and record["num"] == number
    )

    segmented = segment_isnad(source)

    first_mention = segmented.chains[chain_no - 1].mentions[0]
    assert normalize_arabic(first_mention.text) == first_narrator
    assert first_mention.sigha == sigha


def test_segment_isnad_holds_offset_invariant_on_pilot_sample() -> None:
    records = _load_pilot_sample()
    assert len(records) == 50

    for record in records:
        source = record["raw"]
        segmented = segment_isnad(source)

        _assert_structure(source, segmented)
        if record["ref_nars"]:
            mention_count = sum(len(chain.mentions) for chain in segmented.chains)
            assert mention_count >= 1, f"{record['coll']} {record['num']}"
