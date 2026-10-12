from typing import Any

from app.application.use_cases.extraction_management import StructuredExtractionContract
from app.bootstrap.container import get_container
from app.infrastructure.llm.rule_based_isnad_provider import (
    RULE_CONFIDENCE,
    RuleBasedIsnadProvider,
)
from app.infrastructure.template.catalog import ISNAD_TEMPLATE_SCHEMA

TAHWIL_TEXT = (
    "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ . ح ، "
    "حَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ ، أَخْبَرَنَا اللَّيْثُ ، عَنِ ابْنِ شِهَابٍ"
)


def _generate(
    text: str,
    *,
    segment_order: int = 1,
    external_ref: str | None = "Muslim:978",
) -> dict[str, Any]:
    return RuleBasedIsnadProvider().generate_structured(
        prompt="unused",
        schema_name="unused",
        payload={
            "source_unit": {"external_ref": external_ref},
            "segments": [
                {"segment_id": "segment-1", "segment_order": segment_order, "text": text}
            ],
        },
    )


def test_tahwil_text_yields_one_narrator_per_mention_and_links_in_chain_order() -> None:
    output = _generate(TAHWIL_TEXT)

    names_by_ref = {node["ref"]: node["properties"]["name"] for node in output["nodes"]}
    assert list(names_by_ref.values()) == [
        "قُتَيْبَةُ بْنُ سَعِيدٍ",
        "لَيْثٌ",
        "مُحَمَّدُ بْنُ رُمْحٍ",
        "اللَّيْثُ",
        "ابْنِ شِهَابٍ",
    ]
    assert {node["node_type"] for node in output["nodes"]} == {"Narrator"}
    assert [
        (
            names_by_ref[relation["from_ref"]],
            names_by_ref[relation["to_ref"]],
            relation["properties"],
        )
        for relation in output["relations"]
    ] == [
        (
            "قُتَيْبَةُ بْنُ سَعِيدٍ",
            "لَيْثٌ",
            {"hadith_ref": "Muslim:978", "chain_no": 1, "position": 1, "sigha": "حدثنا"},
        ),
        (
            "مُحَمَّدُ بْنُ رُمْحٍ",
            "اللَّيْثُ",
            {"hadith_ref": "Muslim:978", "chain_no": 2, "position": 1, "sigha": "اخبرنا"},
        ),
        (
            "اللَّيْثُ",
            "ابْنِ شِهَابٍ",
            {"hadith_ref": "Muslim:978", "chain_no": 2, "position": 2, "sigha": "عن"},
        ),
    ]
    assert {relation["relation_type"] for relation in output["relations"]} == {"NARRATED_FROM"}


def test_every_quote_is_a_verbatim_segment_substring_that_contains_the_mention() -> None:
    output = _generate(TAHWIL_TEXT)

    for node in output["nodes"]:
        (evidence,) = node["evidence_refs"]
        assert evidence["segment_id"] == "segment-1"
        assert TAHWIL_TEXT[evidence["start_offset"] : evidence["end_offset"]] == evidence["quote"]
        assert node["properties"]["name"] in evidence["quote"]
    names_by_ref = {node["ref"]: node["properties"]["name"] for node in output["nodes"]}
    for relation in output["relations"]:
        (evidence,) = relation["evidence_refs"]
        quote = evidence["quote"]
        assert TAHWIL_TEXT[evidence["start_offset"] : evidence["end_offset"]] == quote
        assert quote.startswith(names_by_ref[relation["from_ref"]])
        assert quote.endswith(names_by_ref[relation["to_ref"]])


def test_output_fits_the_extraction_contract_with_confidence_above_template_thresholds() -> None:
    output = _generate(TAHWIL_TEXT)

    parsed = StructuredExtractionContract.model_validate(output)
    assert len(parsed.nodes) == 5
    assert len(parsed.relations) == 3
    thresholds = [
        *(node_type.confidence_threshold for node_type in ISNAD_TEMPLATE_SCHEMA.node_types),
        *(
            relation_type.confidence_threshold
            for relation_type in ISNAD_TEMPLATE_SCHEMA.relation_types
        ),
    ]
    assert RULE_CONFIDENCE > max(thresholds)
    assert {item.confidence for item in [*parsed.nodes, *parsed.relations]} == {RULE_CONFIDENCE}


def test_text_without_a_chain_yields_no_candidates() -> None:
    assert _generate("قَالَ رَجُلٌ لِصَاحِبِهِ") == {"nodes": [], "relations": []}


def test_name_written_twice_is_one_node_with_one_quote_per_mention() -> None:
    text = "حَدَّثَنَا قُتَيْبَةُ ، عَنْ مَالِكٍ . ح ، حَدَّثَنَا يَحْيَى ، عَنْ مَالِكٍ"

    output = _generate(text)

    assert [node["properties"]["name"] for node in output["nodes"]] == [
        "قُتَيْبَةُ",
        "مَالِكٍ",
        "يَحْيَى",
    ]
    malik = output["nodes"][1]
    assert [evidence["quote"] for evidence in malik["evidence_refs"]] == ["مَالِكٍ", "مَالِكٍ"]
    assert [evidence["start_offset"] for evidence in malik["evidence_refs"]] == [
        text.index("مَالِكٍ"),
        text.rindex("مَالِكٍ"),
    ]
    assert [relation["to_ref"] for relation in output["relations"]] == [malik["ref"]] * 2


def test_chain_number_follows_segment_order_and_missing_reference_is_left_out() -> None:
    output = _generate("حَدَّثَنَا لَيْثٌ ، عَنْ نَافِعٍ", segment_order=3, external_ref=None)

    assert [relation["properties"] for relation in output["relations"]] == [
        {"chain_no": 3, "position": 1, "sigha": "عن"}
    ]


def test_provider_is_registered_for_extraction_runs() -> None:
    get_container.cache_clear()

    provider = get_container().extraction_management_service.provider_registry.get(
        "rule_based_isnad"
    )

    assert isinstance(provider, RuleBasedIsnadProvider)
