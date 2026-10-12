from collections.abc import Callable
from copy import deepcopy
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from app.infrastructure.llm.provider_registry import StaticLLMProviderRegistry
from test_helpers import create_pipeline_definition

Responder = Callable[[dict[str, Any]], dict[str, Any]]


class ScriptedLLMProvider:
    def __init__(self, respond: Responder) -> None:
        self.provider_name = "scripted-test"
        self.payloads: list[dict[str, Any]] = []
        self._respond = respond

    def generate_structured(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        del prompt, schema_name, model
        self.payloads.append(deepcopy(payload))
        return self._respond(payload)


def _evidence(payload: dict[str, Any], quote: str | None) -> list[dict[str, Any]]:
    return [{"segment_id": payload["segments"][0]["segment_id"], "quote": quote}]


def _node(
    payload: dict[str, Any],
    ref: str,
    name: str,
    quote: str | None,
    *,
    node_type: str = "Person",
    confidence: float = 0.99,
    extra_properties: dict[str, object] | None = None,
) -> dict[str, Any]:
    return {
        "ref": ref,
        "node_type": node_type,
        "properties": {"name": name, **(extra_properties or {})},
        "confidence": confidence,
        "evidence_refs": _evidence(payload, quote),
    }


def _start_extraction_run(
    client: TestClient,
    *,
    raw_content: str,
    respond: Responder,
) -> tuple[str, ScriptedLLMProvider]:
    project_id = client.post(
        "/api/projects",
        json={"name": "Grounding Lab", "description": "Grounding gates"},
    ).json()["project_id"]
    schema_id = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Grounding schema"},
    ).json()["schema_version_id"]
    node_type_response = client.post(
        f"/api/schema-versions/{schema_id}/node-types",
        json={
            "name": "Person",
            "display_name": "Person",
            "description": "A person named in the text",
            "merge_keys": ["name"],
            "properties": [
                {"name": "name", "data_type": "string", "required": True},
                {"name": "role", "data_type": "string", "enum_values": ["hero", "villain"]},
            ],
        },
    )
    assert node_type_response.status_code == 201
    relation_type_response = client.post(
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "KNOWS",
            "from_type": "Person",
            "to_type": "Person",
            "description": "One person knows another",
            "merge_keys": ["context"],
            "properties": [
                {
                    "name": "context",
                    "data_type": "string",
                    "enum_values": ["street", "school"],
                }
            ],
        },
    )
    assert relation_type_response.status_code == 201
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")
    source_id = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "note",
            "title": "Grounding source",
            "raw_content": raw_content,
        },
    ).json()["source_unit_id"]
    run_id = client.post(
        f"/api/source-units/{source_id}/runs",
        json={
            "schema_version_id": schema_id,
            "pipeline_version": "v1",
            "llm_provider": "scripted-test",
        },
    ).json()["run_id"]
    segments_response = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    )
    assert segments_response.status_code == 201
    provider = ScriptedLLMProvider(respond)
    get_container().extraction_management_service.provider_registry = (
        StaticLLMProviderRegistry(providers=[provider])
    )
    return run_id, provider


def _extract_and_validate(client: TestClient, run_id: str) -> dict[str, Any]:
    extract_response = client.post(f"/api/runs/{run_id}/extract-candidates", json={})
    assert extract_response.status_code == 200, extract_response.text
    assert client.post(f"/api/runs/{run_id}/validate").status_code == 200
    report: dict[str, Any] = extract_response.json()
    return report


def _node_statuses(client: TestClient, run_id: str) -> dict[str, str]:
    return {
        node["properties"]["name"]: node["status"]
        for node in client.get(f"/api/runs/{run_id}/candidate-nodes").json()
    }


def _review_reasons(client: TestClient, run_id: str) -> list[tuple[str, str]]:
    return sorted(
        (item["item_type"], item["reason_code"])
        for item in client.get(f"/api/runs/{run_id}/review-items").json()
    )


def test_quote_missing_from_segment_routes_node_to_review_despite_high_confidence() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    run_id, provider = _start_extraction_run(
        client,
        raw_content="Ali knows Veli.",
        respond=lambda payload: {
            "nodes": [
                _node(payload, "n_ali", "Ali", "Ali greets Veli"),
                _node(payload, "n_veli", "Veli", "knows Veli"),
            ],
            "relations": [],
        },
    )

    _extract_and_validate(client, run_id)

    assert len(provider.payloads) == 1
    assert _node_statuses(client, run_id) == {"Ali": "review", "Veli": "validated"}
    assert _review_reasons(client, run_id) == [("candidate_node", "quote_not_in_segment")]


def test_evidence_without_quote_routes_node_to_review() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    run_id, _ = _start_extraction_run(
        client,
        raw_content="Ali knows Veli.",
        respond=lambda payload: {
            "nodes": [_node(payload, "n_ali", "Ali", None)],
            "relations": [],
        },
    )

    _extract_and_validate(client, run_id)

    assert _node_statuses(client, run_id) == {"Ali": "review"}
    assert _review_reasons(client, run_id) == [("candidate_node", "quote_not_in_segment")]


def test_candidates_without_evidence_route_to_review_as_missing_evidence() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    def respond(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "nodes": [
                {**_node(payload, "n_ali", "Ali", None), "evidence_refs": []},
                _node(payload, "n_veli", "Veli", "Veli"),
                _node(payload, "n_can", "Can", "Can"),
            ],
            "relations": [
                {
                    "relation_type": "KNOWS",
                    "from_ref": "n_veli",
                    "to_ref": "n_can",
                    "properties": {"context": "street"},
                    "confidence": 0.99,
                    "evidence_refs": [],
                }
            ],
        }

    run_id, _ = _start_extraction_run(
        client,
        raw_content="Ali knows Veli. Veli knows Can.",
        respond=respond,
    )

    _extract_and_validate(client, run_id)

    assert _node_statuses(client, run_id) == {
        "Ali": "review",
        "Veli": "validated",
        "Can": "validated",
    }
    assert _review_reasons(client, run_id) == [
        ("candidate_node", "missing_evidence"),
        ("candidate_relation", "missing_evidence"),
    ]


def test_relation_quote_missing_from_segment_routes_relation_to_review() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    def respond(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "nodes": [
                _node(payload, "n_ali", "Ali", "Ali"),
                _node(payload, "n_veli", "Veli", "Veli"),
            ],
            "relations": [
                {
                    "relation_type": "KNOWS",
                    "from_ref": "n_ali",
                    "to_ref": "n_veli",
                    "properties": {"context": "street"},
                    "confidence": 0.99,
                    "evidence_refs": _evidence(payload, "Ali trusts Veli"),
                }
            ],
        }

    run_id, _ = _start_extraction_run(client, raw_content="Ali knows Veli.", respond=respond)

    _extract_and_validate(client, run_id)

    relations = client.get(f"/api/runs/{run_id}/candidate-relations").json()
    assert [relation["status"] for relation in relations] == ["review"]
    assert _review_reasons(client, run_id) == [("candidate_relation", "quote_not_in_segment")]


@pytest.mark.parametrize(
    ("name", "expected_status", "expected_reasons"),
    [
        ("الليث", "review", [("candidate_node", "value_not_in_quote")]),
        ("ليث", "validated", []),
    ],
)
def test_merge_key_value_must_occur_in_a_quote(
    name: str,
    expected_status: str,
    expected_reasons: list[tuple[str, str]],
) -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    run_id, _ = _start_extraction_run(
        client,
        raw_content="حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ",
        respond=lambda payload: {
            "nodes": [_node(payload, "n_layth", name, "حَدَّثَنَا لَيْثٌ")],
            "relations": [],
        },
    )

    _extract_and_validate(client, run_id)

    assert _node_statuses(client, run_id) == {name: expected_status}
    assert _review_reasons(client, run_id) == expected_reasons


def test_grounding_ignores_case_and_punctuation_in_latin_text() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    run_id, _ = _start_extraction_run(
        client,
        raw_content="Dr. Şükrü Gündoğdu, Ankara'da Veli ile görüştü.",
        respond=lambda payload: {
            "nodes": [
                _node(payload, "n_sukru", "şükrü gündoğdu", "DR ŞÜKRÜ GÜNDOĞDU, Ankara da")
            ],
            "relations": [],
        },
    )

    _extract_and_validate(client, run_id)

    assert _node_statuses(client, run_id) == {"şükrü gündoğdu": "validated"}


def test_grounding_gates_leave_runs_without_extraction_untouched() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    run_id, _ = _start_extraction_run(
        client,
        raw_content="Ali knows Veli.",
        respond=lambda payload: {"nodes": [], "relations": []},
    )

    response = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={"node_type": "Person", "properties": {"name": "Ali"}, "confidence": 0.95},
    )
    assert response.status_code == 201
    assert client.post(f"/api/runs/{run_id}/validate").status_code == 200

    assert _node_statuses(client, run_id) == {"Ali": "validated"}
    assert _review_reasons(client, run_id) == []


def test_unknown_node_type_is_dropped_alone_and_recorded_as_schema_proposal() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    def respond(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "nodes": [
                _node(payload, "n_ali", "Ali", "Ali"),
                _node(payload, "n_city", "Ankara", "in Ankara", node_type="City"),
                _node(payload, "n_veli", "Veli", "Veli"),
            ],
            "relations": [
                {
                    "relation_type": "KNOWS",
                    "from_ref": "n_ali",
                    "to_ref": "n_veli",
                    "properties": {"context": "street"},
                    "confidence": 0.99,
                    "evidence_refs": _evidence(payload, "Ali knows Veli"),
                },
                {
                    "relation_type": "KNOWS",
                    "from_ref": "n_ali",
                    "to_ref": "n_city",
                    "properties": {"context": "school"},
                    "confidence": 0.99,
                    "evidence_refs": _evidence(payload, "Ali knows Veli in Ankara"),
                },
            ],
        }

    run_id, _ = _start_extraction_run(
        client,
        raw_content="Ali knows Veli in Ankara.",
        respond=respond,
    )

    report = _extract_and_validate(client, run_id)

    assert report["dropped_node_count"] == 1
    assert report["dropped_relation_count"] == 1
    assert len(report["created_candidate_node_ids"]) == 2
    assert len(report["created_candidate_relation_ids"]) == 1
    assert _node_statuses(client, run_id) == {"Ali": "validated", "Veli": "validated"}
    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    assert [(item["item_type"], item["reason_code"]) for item in review_items] == [
        ("schema_proposal", "schema_type_proposal")
    ]
    proposal = review_items[0]
    assert proposal["status"] == "open"
    assert proposal["item_ref"] == report["execution_id"]
    assert proposal["payload_json"]["kind"] == "node"
    assert proposal["payload_json"]["type_name"] == "City"
    assert proposal["payload_json"]["count"] == 1
    assert proposal["payload_json"]["sample_quote"] == "in Ankara"
    assert proposal["payload_json"]["dropped_relation_count"] == 1

    blocked_commit = client.post(f"/api/runs/{run_id}/commit")
    assert blocked_commit.status_code == 422
    decision = client.post(
        f"/api/review-items/{proposal['review_item_id']}/decision",
        json={"action": "reject", "reviewer_id": "reviewer-1"},
    )
    assert decision.status_code == 200, decision.text
    graph_delta = client.post(f"/api/runs/{run_id}/commit")
    assert graph_delta.status_code == 200, graph_delta.text
    assert graph_delta.json()["nodes_created"] == 2


def test_unknown_relation_type_is_dropped_alone_and_recorded_as_schema_proposal() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    def respond(payload: dict[str, Any]) -> dict[str, Any]:
        relation = {
            "from_ref": "n_ali",
            "to_ref": "n_veli",
            "properties": {"context": "street"},
            "confidence": 0.99,
            "evidence_refs": _evidence(payload, "Ali knows Veli"),
        }
        return {
            "nodes": [
                _node(payload, "n_ali", "Ali", "Ali"),
                _node(payload, "n_veli", "Veli", "Veli"),
            ],
            "relations": [
                {**relation, "relation_type": "KNOWS"},
                {**relation, "relation_type": "TRUSTS"},
                {**relation, "relation_type": "trusts"},
            ],
        }

    run_id, _ = _start_extraction_run(client, raw_content="Ali knows Veli.", respond=respond)

    report = _extract_and_validate(client, run_id)

    assert report["dropped_relation_count"] == 2
    assert len(report["created_candidate_relation_ids"]) == 1
    assert [
        (proposal["reason_code"], proposal["kind"], proposal["type_name"], proposal["count"])
        for proposal in report["schema_proposals"]
    ] == [("schema_type_proposal", "relation", "TRUSTS", 2)]
    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    assert [item["reason_code"] for item in review_items] == ["schema_type_proposal"]
    assert review_items[0]["payload_json"]["sample_quote"] == "Ali knows Veli"


def test_dry_run_reports_schema_proposals_without_recording_review_items() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    run_id, _ = _start_extraction_run(
        client,
        raw_content="Ali lives in Ankara.",
        respond=lambda payload: {
            "nodes": [_node(payload, "n_city", "Ankara", "Ankara", node_type="City")],
            "relations": [],
        },
    )

    response = client.post(f"/api/runs/{run_id}/extract-candidates", json={"dry_run": True})

    assert response.status_code == 200
    assert [proposal["type_name"] for proposal in response.json()["schema_proposals"]] == ["City"]
    assert client.get(f"/api/runs/{run_id}/review-items").json() == []


def test_undeclared_property_key_is_removed_and_recorded_as_schema_proposal() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    run_id, _ = _start_extraction_run(
        client,
        raw_content="Ali knows Veli.",
        respond=lambda payload: {
            "nodes": [
                _node(payload, "n_ali", "Ali", "Ali", extra_properties={"age": "40"}),
                _node(payload, "n_veli", "Veli", "Veli", extra_properties={"age": "35"}),
            ],
            "relations": [],
        },
    )

    report = _extract_and_validate(client, run_id)

    candidate_nodes = client.get(f"/api/runs/{run_id}/candidate-nodes").json()
    assert sorted(
        (node["properties"] for node in candidate_nodes),
        key=lambda properties: properties["name"],
    ) == [{"name": "Ali"}, {"name": "Veli"}]
    assert _node_statuses(client, run_id) == {"Ali": "validated", "Veli": "validated"}
    assert report["dropped_node_count"] == 0
    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    assert [(item["item_type"], item["reason_code"]) for item in review_items] == [
        ("schema_proposal", "schema_property_proposal")
    ]
    payload_json = review_items[0]["payload_json"]
    assert payload_json["kind"] == "node"
    assert payload_json["type_name"] == "Person"
    assert payload_json["property_name"] == "age"
    assert payload_json["count"] == 2
    assert payload_json["sample_value"] == "40"
    assert payload_json["sample_quote"] == "Ali"


def test_enum_value_outside_declared_values_routes_candidates_to_review() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    def respond(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "nodes": [
                _node(payload, "n_ali", "Ali", "Ali", extra_properties={"role": "sidekick"}),
                _node(payload, "n_veli", "Veli", "Veli", extra_properties={"role": "hero"}),
                _node(payload, "n_can", "Can", "Can"),
            ],
            "relations": [
                {
                    "relation_type": "KNOWS",
                    "from_ref": "n_veli",
                    "to_ref": "n_can",
                    "properties": {"context": "market"},
                    "confidence": 0.99,
                    "evidence_refs": _evidence(payload, "Veli knows Can"),
                }
            ],
        }

    run_id, _ = _start_extraction_run(
        client,
        raw_content="Ali knows Veli. Veli knows Can.",
        respond=respond,
    )

    _extract_and_validate(client, run_id)

    assert _node_statuses(client, run_id) == {
        "Ali": "review",
        "Veli": "validated",
        "Can": "validated",
    }
    assert _review_reasons(client, run_id) == [
        ("candidate_node", "property_value_not_allowed"),
        ("candidate_relation", "property_value_not_allowed"),
    ]


def test_prompt_payload_lists_relation_merge_keys() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    run_id, provider = _start_extraction_run(
        client,
        raw_content="Ali knows Veli.",
        respond=lambda payload: {"nodes": [], "relations": []},
    )

    response = client.post(f"/api/runs/{run_id}/extract-candidates", json={"dry_run": True})

    assert response.status_code == 200
    relation_types = provider.payloads[0]["schema"]["relation_types"]
    assert [(item["name"], item["merge_keys"]) for item in relation_types] == [
        ("KNOWS", ["context"])
    ]


def test_node_accepted_after_failing_a_grounding_gate_stays_validated_on_revalidation() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    run_id, _ = _start_extraction_run(
        client,
        raw_content="Ali knows Veli.",
        respond=lambda payload: {
            "nodes": [
                _node(payload, "n_ali", "Ali", "Ali greets Veli"),
                _node(payload, "n_veli", "Veli", "knows Veli"),
            ],
            "relations": [
                {
                    "relation_type": "KNOWS",
                    "from_ref": "n_ali",
                    "to_ref": "n_veli",
                    "properties": {"context": "street"},
                    "confidence": 0.99,
                    "evidence_refs": _evidence(payload, "Ali knows Veli"),
                }
            ],
        },
    )
    _extract_and_validate(client, run_id)
    ali_item = next(
        item
        for item in client.get(f"/api/runs/{run_id}/review-items").json()
        if item["reason_code"] == "quote_not_in_segment"
    )
    decision = client.post(
        f"/api/review-items/{ali_item['review_item_id']}/decision",
        json={"action": "accept", "reviewer_id": "reviewer-1"},
    )
    assert decision.status_code == 200, decision.text

    validation = client.post(f"/api/runs/{run_id}/validate")

    assert validation.status_code == 200
    assert validation.json()["node_validated"] == 2
    assert validation.json()["relation_validated"] == 1
    assert _node_statuses(client, run_id) == {"Ali": "validated", "Veli": "validated"}
    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    assert [(item["review_item_id"], item["status"]) for item in review_items] == [
        (ali_item["review_item_id"], "accepted")
    ]
    assert [
        (decision["action"], decision["reviewer_id"]) for decision in review_items[0]["decisions"]
    ] == [("accept", "reviewer-1")]
    assert [
        result["rule_code"]
        for result in validation.json()["validation_results"]
        if result["candidate_ref"] == ali_item["item_ref"]
    ] == ["human_review_decision"]
    records = client.get(f"/api/runs/{run_id}/acceptance-records").json()
    ali_record = next(
        record for record in records if record["candidate_ref"] == ali_item["item_ref"]
    )
    assert ali_record["decision"]["reviewer_id"] == "reviewer-1"
    assert client.post(f"/api/runs/{run_id}/commit").status_code == 200


def test_repeated_extraction_keeps_one_open_item_per_schema_proposal() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    city_quotes = [["in Ankara"], ["Ankara", "Izmir"]]

    def respond(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "nodes": [
                _node(payload, f"n_city_{index}", quote, quote, node_type="City")
                for index, quote in enumerate(city_quotes.pop(0))
            ],
            "relations": [],
        }

    run_id, _ = _start_extraction_run(
        client,
        raw_content="Ali lives in Ankara, Veli in Izmir.",
        respond=respond,
    )

    first = client.post(f"/api/runs/{run_id}/extract-candidates", json={})
    assert first.status_code == 200, first.text
    first_items = client.get(f"/api/runs/{run_id}/review-items").json()
    second = client.post(f"/api/runs/{run_id}/extract-candidates", json={})
    assert second.status_code == 200, second.text

    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    assert len(first_items) == len(review_items) == 1
    proposal = review_items[0]
    assert proposal["review_item_id"] == first_items[0]["review_item_id"]
    assert proposal["status"] == "open"
    assert proposal["item_ref"] == second.json()["execution_id"]
    assert first_items[0]["payload_json"]["count"] == 1
    assert proposal["payload_json"]["count"] == 2
    assert proposal["payload_json"]["sample_quote"] == "Ankara"
    assert proposal["decisions"] == []


def test_repeated_extraction_does_not_reopen_a_decided_schema_proposal() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    run_id, _ = _start_extraction_run(
        client,
        raw_content="Ali lives in Ankara.",
        respond=lambda payload: {
            "nodes": [_node(payload, "n_city", "Ankara", "Ankara", node_type="City")],
            "relations": [],
        },
    )
    assert client.post(f"/api/runs/{run_id}/extract-candidates", json={}).status_code == 200
    proposal = client.get(f"/api/runs/{run_id}/review-items").json()[0]
    decision = client.post(
        f"/api/review-items/{proposal['review_item_id']}/decision",
        json={"action": "reject", "reviewer_id": "reviewer-1"},
    )
    assert decision.status_code == 200, decision.text

    assert client.post(f"/api/runs/{run_id}/extract-candidates", json={}).status_code == 200

    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    assert [(item["review_item_id"], item["status"]) for item in review_items] == [
        (proposal["review_item_id"], "rejected")
    ]
    assert review_items[0]["item_ref"] == proposal["item_ref"]
    assert len(review_items[0]["decisions"]) == 1
