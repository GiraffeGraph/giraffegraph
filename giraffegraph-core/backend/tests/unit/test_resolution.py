from app.domain.shared.resolution import build_canonical_merge_key


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
