import hashlib
import json
from collections.abc import Sequence
from re import sub
from unicodedata import normalize

from app.domain.extraction.entities import CandidateNode, CandidateRelation
from app.domain.schema.entities import NodeTypeDefinition


def derive_merge_key_payload(
    *,
    node_type: NodeTypeDefinition,
    properties: dict[str, object],
    provided_merge_key_payload: dict[str, object],
) -> dict[str, object]:
    merge_key_payload: dict[str, object] = {}
    for merge_key in node_type.merge_keys:
        property_value = properties.get(merge_key)
        if not is_missing_value(property_value):
            merge_key_payload[merge_key] = property_value
            continue

        provided_value = provided_merge_key_payload.get(merge_key)
        if not is_missing_value(provided_value):
            merge_key_payload[merge_key] = provided_value
    return merge_key_payload


def build_candidate_node_resolution_key(candidate_node: CandidateNode) -> str:
    return (
        f"{normalize_text(candidate_node.node_type)}::"
        f"{normalized_payload_key(candidate_node.merge_key_payload)}"
    )


def missing_relation_merge_keys(
    *,
    merge_keys: Sequence[str],
    properties: dict[str, object],
) -> list[str]:
    return [
        merge_key for merge_key in merge_keys if is_missing_value(properties.get(merge_key))
    ]


def build_relation_identity_key(
    *,
    merge_keys: Sequence[str],
    properties: dict[str, object],
) -> str:
    merge_key_payload = {
        merge_key: properties[merge_key]
        for merge_key in merge_keys
        if not is_missing_value(properties.get(merge_key))
    }
    encoded = normalized_payload_key(merge_key_payload)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_candidate_relation_resolution_key(
    candidate_relation: CandidateRelation,
    *,
    node_resolution_keys_by_candidate_id: dict[str, str],
    merge_keys: Sequence[str] = (),
) -> str:
    from_key = node_resolution_keys_by_candidate_id.get(
        candidate_relation.from_candidate_ref,
        f"candidate::{candidate_relation.from_candidate_ref}",
    )
    to_key = node_resolution_keys_by_candidate_id.get(
        candidate_relation.to_candidate_ref,
        f"candidate::{candidate_relation.to_candidate_ref}",
    )
    return "::".join(
        [
            normalize_text(candidate_relation.relation_type),
            from_key,
            to_key,
            build_relation_identity_key(
                merge_keys=merge_keys,
                properties=candidate_relation.properties,
            ),
        ]
    )


def candidate_node_identity_key(candidate_node: CandidateNode) -> str:
    if candidate_node.merge_key_payload:
        return build_candidate_node_resolution_key(candidate_node)
    return f"candidate::{candidate_node.candidate_node_id}"


def build_canonical_merge_key(
    *,
    merge_key_payload: dict[str, object],
    fallback_payload: dict[str, object],
) -> str:
    payload = merge_key_payload if merge_key_payload else fallback_payload
    encoded = normalized_payload_key(payload)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def normalized_payload_key(payload: dict[str, object]) -> str:
    return json.dumps(
        normalize_object(payload),
        sort_keys=True,
        separators=(",", ":"),
    )


def normalize_object(value: object) -> object:
    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, list):
        return [normalize_object(item) for item in value]
    if isinstance(value, dict):
        return {
            normalize_text(str(key)): normalize_object(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    return value


def normalize_text(value: str) -> str:
    normalized_value = normalize("NFKC", value).strip()
    if normalized_value == "":
        return ""
    collapsed = sub(r"\s+", " ", normalized_value)
    return collapsed.casefold()


def is_missing_value(value: object | None) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, dict, set, tuple)):
        return len(value) == 0
    return False
