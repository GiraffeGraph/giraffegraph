from app.domain.hadith.segmentation import IsnadSegmentation
from app.domain.hadith.segmenter import segment_isnad

TAHWIL_SOURCE = (
    "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ . ح ، وحَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ ، "
    "أَخْبَرَنَا اللَّيْثُ ، عَنِ ابْنِ شِهَابٍ"
)


def test_segment_isnad_reports_source_offset_of_each_transmission_formula() -> None:
    segmented = segment_isnad(TAHWIL_SOURCE)

    for chain in segmented.chains:
        for mention in chain.mentions:
            assert mention.sigha_start < mention.start
    second_chain = segmented.chains[1]
    assert TAHWIL_SOURCE[second_chain.mentions[0].sigha_start :].startswith("حَدَّثَنَا مُحَمَّدُ")
    assert TAHWIL_SOURCE[second_chain.mentions[2].sigha_start :].startswith("عَنِ ابْنِ")


def test_co_narrators_share_the_offset_of_their_transmission_formula() -> None:
    source = "حَدَّثَنَا أَبُو بَكْرٍ و عُثْمَانُ ، عَنْ جَرِيرٍ"

    mentions = segment_isnad(source).chains[0].mentions

    assert [mention.sigha_start for mention in mentions] == [0, 0, source.index("عَنْ")]


def test_isnad_segmentation_returns_one_draft_per_chain_with_source_offsets() -> None:
    drafts = IsnadSegmentation().split(TAHWIL_SOURCE)

    assert [draft.text for draft in drafts] == [
        "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ",
        "حَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ ، أَخْبَرَنَا اللَّيْثُ ، عَنِ ابْنِ شِهَابٍ",
    ]
    assert [draft.metadata["chain_no"] for draft in drafts] == ["1", "2"]
    for draft in drafts:
        start = int(draft.metadata["start_offset"])
        end = int(draft.metadata["end_offset"])
        assert TAHWIL_SOURCE[start:end] == draft.text


def test_isnad_segmentation_stops_at_matn_boundary() -> None:
    source = (
        "حَدَّثَنَا لَيْثٌ ، عَنْ نَافِعٍ ، عَنِ النَّبِيِّ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ قَالَ الْحَرُّ . "
        "حَدَّثَنِي حَرْمَلَةُ ، أَخْبَرَنَا ابْنُ وَهْبٍ"
    )
    assert len(segment_isnad(source).chains) == 2

    drafts = IsnadSegmentation().split(source)

    assert [draft.text for draft in drafts] == ["حَدَّثَنَا لَيْثٌ ، عَنْ نَافِعٍ"]


def test_isnad_segmentation_falls_back_to_whole_text_without_chain() -> None:
    drafts = IsnadSegmentation().split("  قَالَ رَجُلٌ لِصَاحِبِهِ \n")

    assert [(draft.text, draft.metadata) for draft in drafts] == [
        ("قَالَ رَجُلٌ لِصَاحِبِهِ", {"fallback": "whole_text"})
    ]


def test_isnad_segmentation_requests_one_extraction_call_per_segment() -> None:
    assert IsnadSegmentation().name == "isnad"
    assert IsnadSegmentation().one_call_per_segment is True
