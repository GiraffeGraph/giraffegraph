from app.domain.extraction.entities import CandidateRelation
from app.domain.shared.resolution import (
    build_candidate_relation_resolution_key,
    build_canonical_merge_key,
    build_relation_identity_key,
    missing_relation_merge_keys,
)


def test_build_canonical_merge_key_normalizes_whitespace_and_case() -> None:
    primary_key = build_canonical_merge_key(
        merge_key_payload={"name": "Ali   Veli"},
        fallback_payload={"candidate_node_id": "node-1"},
    )
    normalized_duplicate_key = build_canonical_merge_key(
        merge_key_payload={"name": " ali veli "},
        fallback_payload={"candidate_node_id": "node-2"},
    )

    assert primary_key == normalized_duplicate_key


def test_build_canonical_merge_key_uses_fallback_payload_when_merge_key_missing() -> None:
    first_key = build_canonical_merge_key(
        merge_key_payload={},
        fallback_payload={"candidate_node_id": "node-1"},
    )
    second_key = build_canonical_merge_key(
        merge_key_payload={},
        fallback_payload={"candidate_node_id": "node-2"},
    )

    assert first_key != second_key


def _relation(
    candidate_relation_id: str,
    properties: dict[str, object],
) -> CandidateRelation:
    return CandidateRelation(
        candidate_relation_id=candidate_relation_id,
        run_id="run-1",
        relation_type="TRANSMITTED_TO",
        from_candidate_ref="node-a",
        to_candidate_ref="node-b",
        properties=properties,
    )


NODE_KEYS = {"node-a": "person::a", "node-b": "person::b"}


def test_relation_resolution_key_ignores_properties_outside_merge_keys() -> None:
    first_key = build_candidate_relation_resolution_key(
        _relation("relation-1", {"report_id": "r-1", "wording": "told us"}),
        node_resolution_keys_by_candidate_id=NODE_KEYS,
        merge_keys=["report_id"],
    )
    second_key = build_candidate_relation_resolution_key(
        _relation("relation-2", {"report_id": " R-1 ", "wording": "informed us"}),
        node_resolution_keys_by_candidate_id=NODE_KEYS,
        merge_keys=["report_id"],
    )

    assert first_key == second_key


def test_relation_resolution_key_separates_different_merge_key_values() -> None:
    first_key = build_candidate_relation_resolution_key(
        _relation("relation-1", {"report_id": "r-1"}),
        node_resolution_keys_by_candidate_id=NODE_KEYS,
        merge_keys=["report_id"],
    )
    second_key = build_candidate_relation_resolution_key(
        _relation("relation-2", {"report_id": "r-2"}),
        node_resolution_keys_by_candidate_id=NODE_KEYS,
        merge_keys=["report_id"],
    )

    assert first_key != second_key


def test_relation_resolution_key_without_merge_keys_is_the_endpoint_pair() -> None:
    first_key = build_candidate_relation_resolution_key(
        _relation("relation-1", {"report_id": "r-1"}),
        node_resolution_keys_by_candidate_id=NODE_KEYS,
    )
    second_key = build_candidate_relation_resolution_key(
        _relation("relation-2", {"report_id": "r-2"}),
        node_resolution_keys_by_candidate_id=NODE_KEYS,
    )

    assert first_key == second_key


def test_relation_resolution_key_ends_with_canonical_relation_identity_key() -> None:
    resolution_key = build_candidate_relation_resolution_key(
        _relation("relation-1", {"report_id": "r-1", "wording": "told us"}),
        node_resolution_keys_by_candidate_id=NODE_KEYS,
        merge_keys=["report_id"],
    )

    assert resolution_key.endswith(
        build_relation_identity_key(merge_keys=["report_id"], properties={"report_id": "R-1"})
    )


def test_missing_relation_merge_keys_reports_absent_and_blank_values() -> None:
    assert missing_relation_merge_keys(
        merge_keys=["report_id", "position", "chain"],
        properties={"report_id": "r-1", "position": " "},
    ) == ["position", "chain"]
