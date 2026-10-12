from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from app.domain.review.entities import ReviewItem
from app.domain.shared.enums import CandidateStatus
from test_helpers import create_pipeline_definition

AUTO_RESOLVED_NOTE = "Auto-resolved after dependent review decision."
AUTO_CLOSED_NOTE = "Auto-closed after dependent review decision."


def _client() -> TestClient:
    get_container.cache_clear()
    return TestClient(create_app())


def _start_run(client: TestClient, *, relation_merge_keys: list[str] | None = None) -> str:
    project_id = client.post(
        "/api/projects",
        json={"name": "Review Decision Lab", "template_id": "blank"},
    ).json()["project_id"]
    schema_id = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1},
    ).json()["schema_version_id"]
    assert (
        client.post(
            f"/api/schema-versions/{schema_id}/node-types",
            json={
                "name": "Person",
                "display_name": "Person",
                "description": "A person",
                "merge_keys": ["name"],
                "properties": [{"name": "name", "data_type": "string", "required": True}],
            },
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/api/schema-versions/{schema_id}/relation-types",
            json={
                "name": "TOLD",
                "from_type": "Person",
                "to_type": "Person",
                "description": "One person told another",
                "merge_keys": relation_merge_keys or [],
                "confidence_threshold": 0.7,
                "properties": [
                    {"name": "report_id", "data_type": "string"},
                    {"name": "wording", "data_type": "string"},
                ],
            },
        ).status_code
        == 201
    )
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")
    source_id = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "report",
            "title": "Reports",
            "raw_content": "Ali told Veli. Veli told Can.",
        },
    ).json()["source_unit_id"]
    run_id = client.post(
        f"/api/source-units/{source_id}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()["run_id"]
    return str(run_id)


def _add_node(client: TestClient, run_id: str, name: str, *, confidence: float = 0.95) -> str:
    response = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={"node_type": "Person", "properties": {"name": name}, "confidence": confidence},
    )
    assert response.status_code == 201
    return str(response.json()["candidate_node_id"])


def _add_relation(
    client: TestClient,
    run_id: str,
    from_id: str,
    to_id: str,
    *,
    properties: dict[str, object] | None = None,
    confidence: float = 0.95,
) -> str:
    response = client.post(
        f"/api/runs/{run_id}/candidate-relations",
        json={
            "relation_type": "TOLD",
            "from_candidate_ref": from_id,
            "to_candidate_ref": to_id,
            "properties": properties or {},
            "confidence": confidence,
        },
    )
    assert response.status_code == 201
    return str(response.json()["candidate_relation_id"])


def _validate(client: TestClient, run_id: str) -> None:
    assert client.post(f"/api/runs/{run_id}/validate").status_code == 200


def _review_items_for(client: TestClient, run_id: str, candidate_ref: str) -> list[dict[str, Any]]:
    return [
        item
        for item in client.get(f"/api/runs/{run_id}/review-items").json()
        if item["item_ref"] == candidate_ref
    ]


def _review_item_for(client: TestClient, run_id: str, candidate_ref: str) -> dict[str, Any]:
    items = _review_items_for(client, run_id, candidate_ref)
    assert len(items) == 1
    return items[0]


def _decide(
    client: TestClient,
    review_item_id: str,
    action: str,
    *,
    reviewer_id: str = "ayse",
    **body: object,
) -> Response:
    return client.post(
        f"/api/review-items/{review_item_id}/decision",
        json={"action": action, "reviewer_id": reviewer_id, **body},
    )


def _node_status(client: TestClient, run_id: str, candidate_node_id: str) -> str:
    return next(
        str(node["status"])
        for node in client.get(f"/api/runs/{run_id}/candidate-nodes").json()
        if node["candidate_node_id"] == candidate_node_id
    )


def _relation_status(client: TestClient, run_id: str, candidate_relation_id: str) -> str:
    return next(
        str(relation["status"])
        for relation in client.get(f"/api/runs/{run_id}/candidate-relations").json()
        if relation["candidate_relation_id"] == candidate_relation_id
    )


def _set_reason_code(review_item_id: str, reason_code: str) -> None:
    repository = get_container().review_management_service.review_item_repository
    review_item = repository.get(review_item_id)
    assert review_item is not None
    review_item.reason_code = reason_code
    repository.save(review_item)


@pytest.mark.parametrize(
    "body",
    [
        {"action": "accept"},
        {"action": "accept", "reviewer_id": ""},
        {"action": "accept", "reviewer_id": "   "},
        {"action": "accept", "reviewer_id": "ayse", "duration_ms": -1},
    ],
)
def test_decision_requires_reviewer_id_and_non_negative_duration(body: dict[str, object]) -> None:
    client = _client()
    run_id = _start_run(client)
    node_id = _add_node(client, run_id, "Ali", confidence=0.2)
    _validate(client, run_id)
    review_item = _review_item_for(client, run_id, node_id)

    response = client.post(
        f"/api/review-items/{review_item['review_item_id']}/decision",
        json=body,
    )

    assert response.status_code == 422
    assert _node_status(client, run_id, node_id) == "review"
    detail = client.get(f"/api/review-items/{review_item['review_item_id']}").json()
    assert detail["status"] == "open"
    assert detail["decisions"] == []


def test_decision_records_reviewer_time_and_duration() -> None:
    client = _client()
    run_id = _start_run(client)
    node_id = _add_node(client, run_id, "Ali", confidence=0.2)
    _validate(client, run_id)
    review_item = _review_item_for(client, run_id, node_id)

    before = datetime.now(UTC)
    response = _decide(
        client,
        review_item["review_item_id"],
        "accept",
        reviewer_id="  ayse  ",
        duration_ms=4200,
        reviewer_note="Checked against the source.",
    )
    after = datetime.now(UTC)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert len(body["decisions"]) == 1
    decision = body["decisions"][0]
    assert decision["review_item_id"] == review_item["review_item_id"]
    assert decision["run_id"] == run_id
    assert decision["item_type"] == "candidate_node"
    assert decision["item_ref"] == node_id
    assert decision["action"] == "accept"
    assert decision["reviewer_id"] == "ayse"
    assert decision["duration_ms"] == 4200
    assert decision["reviewer_note"] == "Checked against the source."
    assert decision["before_json"] is None
    assert decision["after_json"] is None
    assert before <= datetime.fromisoformat(decision["decided_at"]) <= after

    detail = client.get(f"/api/review-items/{review_item['review_item_id']}").json()
    assert detail["decisions"] == [decision]

    queue = client.get(
        f"/api/projects/{client.get(f'/api/runs/{run_id}').json()['project_id']}"
        "/review-queue?status_filter=closed"
    ).json()
    queued_item = queue["run_entries"][0]["review_items"][0]["review_item"]
    assert queued_item["decisions"] == [decision]


def test_decision_without_duration_stores_null_duration() -> None:
    client = _client()
    run_id = _start_run(client)
    node_id = _add_node(client, run_id, "Ali", confidence=0.2)
    _validate(client, run_id)
    review_item = _review_item_for(client, run_id, node_id)

    response = _decide(client, review_item["review_item_id"], "accept")

    assert response.status_code == 200
    assert response.json()["decisions"][0]["duration_ms"] is None


def test_second_decision_on_same_item_appends() -> None:
    client = _client()
    run_id = _start_run(client)
    node_id = _add_node(client, run_id, "Ali", confidence=0.2)
    _validate(client, run_id)
    review_item_id = _review_item_for(client, run_id, node_id)["review_item_id"]

    first = _decide(client, review_item_id, "reject", reviewer_id="ayse", duration_ms=1000)
    assert first.status_code == 200
    assert _node_status(client, run_id, node_id) == "rejected"

    second = _decide(client, review_item_id, "accept", reviewer_id="mehmet", duration_ms=2000)

    assert second.status_code == 200
    body = second.json()
    assert body["status"] == "accepted"
    assert [
        (decision["action"], decision["reviewer_id"], decision["duration_ms"])
        for decision in body["decisions"]
    ] == [("reject", "ayse", 1000), ("accept", "mehmet", 2000)]
    assert body["decisions"][0] == first.json()["decisions"][0]
    assert _node_status(client, run_id, node_id) == "validated"


def test_edit_decision_stores_before_and_after() -> None:
    client = _client()
    run_id = _start_run(client)
    node_id = _add_node(client, run_id, "Ali", confidence=0.2)
    _validate(client, run_id)
    review_item_id = _review_item_for(client, run_id, node_id)["review_item_id"]

    response = _decide(
        client,
        review_item_id,
        "edit",
        properties={"name": "Mehmet"},
        confidence=0.99,
    )

    assert response.status_code == 200
    decision = response.json()["decisions"][0]
    assert decision["action"] == "edit"
    assert decision["before_json"] == {
        "node_type": "Person",
        "properties": {"name": "Ali"},
        "merge_key_payload": {"name": "Ali"},
        "confidence": 0.2,
    }
    assert decision["after_json"] == {
        "node_type": "Person",
        "properties": {"name": "Mehmet"},
        "merge_key_payload": {"name": "Mehmet"},
        "confidence": 0.99,
    }


def test_relation_edit_decision_stores_before_and_after() -> None:
    client = _client()
    run_id = _start_run(client)
    ali = _add_node(client, run_id, "Ali")
    veli = _add_node(client, run_id, "Veli")
    relation_id = _add_relation(
        client, run_id, ali, veli, properties={"wording": "told"}, confidence=0.2
    )
    _validate(client, run_id)
    review_item_id = _review_item_for(client, run_id, relation_id)["review_item_id"]

    response = _decide(
        client,
        review_item_id,
        "edit",
        from_candidate_ref=veli,
        to_candidate_ref=ali,
        properties={"wording": "informed"},
    )

    assert response.status_code == 200
    decision = response.json()["decisions"][0]
    assert decision["before_json"] == {
        "relation_type": "TOLD",
        "from_candidate_ref": ali,
        "to_candidate_ref": veli,
        "properties": {"wording": "told"},
        "confidence": 0.2,
    }
    assert decision["after_json"] == {
        "relation_type": "TOLD",
        "from_candidate_ref": veli,
        "to_candidate_ref": ali,
        "properties": {"wording": "informed"},
        "confidence": 0.2,
    }


def test_refused_decision_records_nothing() -> None:
    client = _client()
    run_id = _start_run(client)
    node_id = _add_node(client, run_id, "Ali", confidence=0.2)
    _validate(client, run_id)
    review_item_id = _review_item_for(client, run_id, node_id)["review_item_id"]

    response = _decide(client, review_item_id, "edit", node_type="Ghost")

    assert response.status_code == 422
    detail = client.get(f"/api/review-items/{review_item_id}").json()
    assert detail["status"] == "open"
    assert detail["decisions"] == []


def test_decision_history_survives_revalidation() -> None:
    client = _client()
    run_id = _start_run(client)
    node_id = _add_node(client, run_id, "Ali", confidence=0.2)
    _validate(client, run_id)
    review_item_id = _review_item_for(client, run_id, node_id)["review_item_id"]
    assert _decide(client, review_item_id, "reject").status_code == 200

    _validate(client, run_id)

    repository = get_container().review_management_service.review_item_repository
    decisions = repository.list_decisions_by_run(run_id)
    assert [(decision.item_ref, decision.action) for decision in decisions] == [
        (node_id, "reject")
    ]


def test_decision_on_completed_run_is_refused() -> None:
    client = _client()
    run_id = _start_run(client)
    node_id = _add_node(client, run_id, "Ali", confidence=0.2)
    _validate(client, run_id)
    review_item_id = _review_item_for(client, run_id, node_id)["review_item_id"]
    assert _decide(client, review_item_id, "accept").status_code == 200
    assert client.post(f"/api/runs/{run_id}/commit").status_code == 200

    response = _decide(client, review_item_id, "reject")

    assert response.status_code == 409
    assert _node_status(client, run_id, node_id) == "validated"
    assert len(client.get(f"/api/review-items/{review_item_id}").json()["decisions"]) == 1


def test_rejected_relation_stays_rejected_after_later_decision_on_another_item() -> None:
    client = _client()
    run_id = _start_run(client)
    ali = _add_node(client, run_id, "Ali")
    veli = _add_node(client, run_id, "Veli")
    can = _add_node(client, run_id, "Can", confidence=0.2)
    rejected_relation = _add_relation(client, run_id, ali, veli, confidence=0.2)
    dependent_relation = _add_relation(client, run_id, ali, can)
    _validate(client, run_id)
    rejected_item_id = _review_item_for(client, run_id, rejected_relation)["review_item_id"]
    dependent_item = _review_item_for(client, run_id, dependent_relation)
    assert dependent_item["reason_code"] == "relation_dependency_review"

    assert _decide(client, rejected_item_id, "reject").status_code == 200
    assert _relation_status(client, run_id, rejected_relation) == "rejected"

    can_item_id = _review_item_for(client, run_id, can)["review_item_id"]
    assert _decide(client, can_item_id, "accept").status_code == 200

    assert _relation_status(client, run_id, rejected_relation) == "rejected"
    rejected_item = _review_item_for(client, run_id, rejected_relation)
    assert rejected_item["review_item_id"] == rejected_item_id
    assert rejected_item["status"] == "rejected"
    assert _relation_status(client, run_id, dependent_relation) == "validated"
    resolved_item = _review_item_for(client, run_id, dependent_relation)
    assert resolved_item["status"] == "accepted"
    assert resolved_item["reviewer_note"] == AUTO_RESOLVED_NOTE

    commit_response = client.post(f"/api/runs/{run_id}/commit")
    assert commit_response.status_code == 200
    assert commit_response.json()["relations_created"] == 1


def test_accepted_relation_stays_validated_after_later_decision_on_another_item() -> None:
    client = _client()
    run_id = _start_run(client)
    ali = _add_node(client, run_id, "Ali")
    veli = _add_node(client, run_id, "Veli")
    can = _add_node(client, run_id, "Can", confidence=0.2)
    accepted_relation = _add_relation(client, run_id, ali, veli, confidence=0.2)
    _validate(client, run_id)
    accepted_item_id = _review_item_for(client, run_id, accepted_relation)["review_item_id"]
    assert _decide(client, accepted_item_id, "accept").status_code == 200

    can_item_id = _review_item_for(client, run_id, can)["review_item_id"]
    assert _decide(client, can_item_id, "reject").status_code == 200

    assert _relation_status(client, run_id, accepted_relation) == "validated"
    accepted_item = _review_item_for(client, run_id, accepted_relation)
    assert accepted_item["status"] == "accepted"
    assert accepted_item["reviewer_note"] is None


@pytest.mark.parametrize(
    "reason_code",
    [
        "quote_not_in_segment",
        "missing_evidence",
        "value_not_in_quote",
        "schema_type_proposal",
        "schema_property_proposal",
        "property_value_not_allowed",
        "missing_relation_merge_key",
        "potential_duplicate_relation",
        "a_reason_code_added_later",
    ],
)
def test_open_item_with_reason_code_the_refresh_does_not_own_survives_refresh(
    reason_code: str,
) -> None:
    client = _client()
    run_id = _start_run(client)
    ali = _add_node(client, run_id, "Ali")
    can = _add_node(client, run_id, "Can", confidence=0.2)
    relation_id = _add_relation(client, run_id, ali, can)
    _validate(client, run_id)
    relation_item = _review_item_for(client, run_id, relation_id)
    _set_reason_code(relation_item["review_item_id"], reason_code)

    can_item_id = _review_item_for(client, run_id, can)["review_item_id"]
    assert _decide(client, can_item_id, "accept").status_code == 200

    surviving_item = _review_item_for(client, run_id, relation_id)
    assert surviving_item["review_item_id"] == relation_item["review_item_id"]
    assert surviving_item["status"] == "open"
    assert surviving_item["reason_code"] == reason_code
    assert surviving_item["reviewer_note"] is None
    assert surviving_item["payload_json"] == relation_item["payload_json"]
    assert _relation_status(client, run_id, relation_id) == "review"
    assert client.post(f"/api/runs/{run_id}/commit").status_code == 422


def test_schema_proposal_item_survives_refresh_and_is_closed_by_a_recorded_decision() -> None:
    client = _client()
    run_id = _start_run(client)
    node_id = _add_node(client, run_id, "Ali", confidence=0.2)
    _validate(client, run_id)
    get_container().review_management_service.review_item_repository.save(
        ReviewItem(
            review_item_id="proposal-1",
            run_id=run_id,
            item_type="schema_proposal",
            item_ref="execution-1",
            reason_code="schema_type_proposal",
            payload_json={"kind": "node", "type_name": "City", "sample_quote": "in Ankara"},
        )
    )

    node_item_id = _review_item_for(client, run_id, node_id)["review_item_id"]
    assert _decide(client, node_item_id, "accept").status_code == 200
    assert client.get("/api/review-items/proposal-1").json()["status"] == "open"
    assert client.post(f"/api/runs/{run_id}/commit").status_code == 422

    assert _decide(client, "proposal-1", "edit", node_type="City").status_code == 422
    response = _decide(client, "proposal-1", "reject", reviewer_id="mehmet", duration_ms=900)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert [
        (decision["action"], decision["reviewer_id"], decision["item_ref"])
        for decision in body["decisions"]
    ] == [("reject", "mehmet", "execution-1")]
    assert client.post(f"/api/runs/{run_id}/commit").status_code == 200


def test_open_item_the_refresh_does_not_own_stays_open_when_endpoint_is_rejected() -> None:
    client = _client()
    run_id = _start_run(client)
    ali = _add_node(client, run_id, "Ali")
    can = _add_node(client, run_id, "Can", confidence=0.2)
    relation_id = _add_relation(client, run_id, ali, can)
    _validate(client, run_id)
    relation_item = _review_item_for(client, run_id, relation_id)
    _set_reason_code(relation_item["review_item_id"], "quote_not_in_segment")

    can_item_id = _review_item_for(client, run_id, can)["review_item_id"]
    assert _decide(client, can_item_id, "reject").status_code == 200

    assert _relation_status(client, run_id, relation_id) == "rejected"
    items = {
        item["reason_code"]: item for item in _review_items_for(client, run_id, relation_id)
    }
    assert items["quote_not_in_segment"]["status"] == "open"
    assert items["relation_dependency_rejected"]["status"] == "rejected"
    assert items["relation_dependency_rejected"]["reviewer_note"] == AUTO_CLOSED_NOTE
    marker_detail = client.get(
        f"/api/review-items/{items['relation_dependency_rejected']['review_item_id']}"
    ).json()
    assert marker_detail["decisions"] == []


def test_rejecting_endpoint_node_rejects_dependent_relation_and_reaccepting_restores_it() -> None:
    client = _client()
    run_id = _start_run(client)
    ali = _add_node(client, run_id, "Ali")
    can = _add_node(client, run_id, "Can", confidence=0.2)
    relation_id = _add_relation(client, run_id, ali, can)
    _validate(client, run_id)
    relation_item_id = _review_item_for(client, run_id, relation_id)["review_item_id"]
    can_item_id = _review_item_for(client, run_id, can)["review_item_id"]

    assert _decide(client, can_item_id, "reject").status_code == 200
    assert _relation_status(client, run_id, relation_id) == "rejected"
    closed_item = _review_item_for(client, run_id, relation_id)
    assert closed_item["review_item_id"] == relation_item_id
    assert closed_item["status"] == "rejected"
    assert closed_item["reason_code"] == "relation_dependency_rejected"
    assert closed_item["reviewer_note"] == AUTO_CLOSED_NOTE

    assert _decide(client, can_item_id, "accept").status_code == 200
    assert _relation_status(client, run_id, relation_id) == "validated"
    resolved_item = _review_item_for(client, run_id, relation_id)
    assert resolved_item["review_item_id"] == relation_item_id
    assert resolved_item["status"] == "accepted"
    assert resolved_item["reviewer_note"] == AUTO_RESOLVED_NOTE

    assert _decide(client, can_item_id, "reject").status_code == 200
    assert _relation_status(client, run_id, relation_id) == "rejected"
    assert _review_item_for(client, run_id, relation_id)["status"] == "rejected"


def test_rejecting_endpoint_node_leaves_relabelled_relation_item_open() -> None:
    client = _client()
    run_id = _start_run(client)
    ali = _add_node(client, run_id, "Ali")
    veli = _add_node(client, run_id, "Veli")
    can = _add_node(client, run_id, "Can", confidence=0.2)
    relation_id = _add_relation(client, run_id, ali, veli)
    low_relation_id = _add_relation(client, run_id, ali, can, confidence=0.2)
    _validate(client, run_id)
    assert _relation_status(client, run_id, relation_id) == "validated"
    can_item_id = _review_item_for(client, run_id, can)["review_item_id"]
    assert _decide(client, can_item_id, "accept").status_code == 200
    low_item = _review_item_for(client, run_id, low_relation_id)
    assert low_item["status"] == "open"
    assert low_item["reason_code"] == "relation_confidence_threshold"

    assert _decide(client, can_item_id, "reject").status_code == 200

    assert _relation_status(client, run_id, relation_id) == "validated"
    assert _review_items_for(client, run_id, relation_id) == []
    assert _relation_status(client, run_id, low_relation_id) == "rejected"
    items = {
        item["reason_code"]: item for item in _review_items_for(client, run_id, low_relation_id)
    }
    assert items["relation_confidence_threshold"]["status"] == "open"
    assert items["relation_dependency_rejected"]["status"] == "rejected"


def test_rejecting_one_duplicate_relation_leaves_the_other_acceptable() -> None:
    client = _client()
    run_id = _start_run(client)
    ali = _add_node(client, run_id, "Ali")
    veli = _add_node(client, run_id, "Veli")
    first = _add_relation(
        client, run_id, ali, veli, properties={"wording": "told"}, confidence=0.3
    )
    second = _add_relation(
        client, run_id, ali, veli, properties={"wording": "informed"}, confidence=0.2
    )
    _validate(client, run_id)
    first_item_id = _review_item_for(client, run_id, first)["review_item_id"]
    second_item_id = _review_item_for(client, run_id, second)["review_item_id"]

    blocked = _decide(client, first_item_id, "accept")
    assert blocked.status_code == 422
    assert "duplicate candidate relation" in blocked.json()["detail"]

    assert _decide(client, second_item_id, "reject").status_code == 200
    assert _relation_status(client, run_id, second) == "rejected"
    still_open = _review_item_for(client, run_id, first)
    assert still_open["review_item_id"] == first_item_id
    assert still_open["status"] == "open"
    assert _relation_status(client, run_id, first) == "review"

    assert _decide(client, first_item_id, "accept").status_code == 200
    assert _relation_status(client, run_id, first) == "validated"
    assert _relation_status(client, run_id, second) == "rejected"
    assert _review_item_for(client, run_id, second)["status"] == "rejected"

    commit_response = client.post(f"/api/runs/{run_id}/commit")
    assert commit_response.status_code == 200
    assert commit_response.json()["relations_created"] == 1


def test_duplicate_hidden_behind_dependency_review_is_not_auto_accepted() -> None:
    client = _client()
    run_id = _start_run(client)
    ali = _add_node(client, run_id, "Ali")
    can = _add_node(client, run_id, "Can", confidence=0.2)
    primary = _add_relation(
        client, run_id, ali, can, properties={"wording": "told"}, confidence=0.95
    )
    duplicate = _add_relation(
        client, run_id, ali, can, properties={"wording": "informed"}, confidence=0.9
    )
    _validate(client, run_id)
    duplicate_item = _review_item_for(client, run_id, duplicate)
    assert duplicate_item["reason_code"] == "relation_dependency_review"

    can_item_id = _review_item_for(client, run_id, can)["review_item_id"]
    assert _decide(client, can_item_id, "accept").status_code == 200

    assert _relation_status(client, run_id, primary) == "validated"
    assert _review_item_for(client, run_id, primary)["status"] == "accepted"
    assert _relation_status(client, run_id, duplicate) == "review"
    relabelled_item = _review_item_for(client, run_id, duplicate)
    assert relabelled_item["review_item_id"] == duplicate_item["review_item_id"]
    assert relabelled_item["status"] == "open"
    assert relabelled_item["reason_code"] == "potential_duplicate_relation"
    assert primary in relabelled_item["payload_json"]["messages"][-1]


def test_missing_merge_key_hidden_behind_dependency_review_is_not_auto_accepted() -> None:
    client = _client()
    run_id = _start_run(client, relation_merge_keys=["report_id"])
    ali = _add_node(client, run_id, "Ali")
    can = _add_node(client, run_id, "Can", confidence=0.2)
    relation_id = _add_relation(client, run_id, ali, can)
    _validate(client, run_id)
    relation_item = _review_item_for(client, run_id, relation_id)
    _set_reason_code(relation_item["review_item_id"], "relation_dependency_review")

    can_item_id = _review_item_for(client, run_id, can)["review_item_id"]
    assert _decide(client, can_item_id, "accept").status_code == 200

    assert _relation_status(client, run_id, relation_id) == "review"
    relabelled_item = _review_item_for(client, run_id, relation_id)
    assert relabelled_item["status"] == "open"
    assert relabelled_item["reason_code"] == "missing_relation_merge_key"


def test_merge_keyed_relations_with_different_merge_key_values_can_both_be_accepted() -> None:
    client = _client()
    run_id = _start_run(client, relation_merge_keys=["report_id"])
    ali = _add_node(client, run_id, "Ali")
    veli = _add_node(client, run_id, "Veli")
    first = _add_relation(
        client, run_id, ali, veli, properties={"report_id": "r-1"}, confidence=0.2
    )
    second = _add_relation(
        client, run_id, ali, veli, properties={"report_id": "r-2"}, confidence=0.2
    )
    _validate(client, run_id)

    for relation_id in (first, second):
        review_item_id = _review_item_for(client, run_id, relation_id)["review_item_id"]
        response = _decide(client, review_item_id, "accept")
        assert response.status_code == 200, response.json()

    assert _relation_status(client, run_id, first) == "validated"
    assert _relation_status(client, run_id, second) == "validated"
    commit_response = client.post(f"/api/runs/{run_id}/commit")
    assert commit_response.status_code == 200
    assert commit_response.json()["relations_created"] == 2


def test_merge_keyed_relations_with_same_merge_key_value_cannot_both_be_accepted() -> None:
    client = _client()
    run_id = _start_run(client, relation_merge_keys=["report_id"])
    ali = _add_node(client, run_id, "Ali")
    veli = _add_node(client, run_id, "Veli")
    first = _add_relation(
        client, run_id, ali, veli, properties={"report_id": "r-1"}, confidence=0.3
    )
    second = _add_relation(
        client, run_id, ali, veli, properties={"report_id": "R-1 "}, confidence=0.2
    )
    _validate(client, run_id)

    response = _decide(
        client, _review_item_for(client, run_id, first)["review_item_id"], "accept"
    )

    assert response.status_code == 422
    assert second in response.json()["detail"]


def test_relation_without_merge_key_value_cannot_be_accepted_until_edited() -> None:
    client = _client()
    run_id = _start_run(client, relation_merge_keys=["report_id"])
    ali = _add_node(client, run_id, "Ali")
    veli = _add_node(client, run_id, "Veli")
    relation_id = _add_relation(client, run_id, ali, veli, properties={"wording": "told"})
    _validate(client, run_id)
    review_item = _review_item_for(client, run_id, relation_id)
    assert review_item["reason_code"] == "missing_relation_merge_key"

    accept_response = _decide(client, review_item["review_item_id"], "accept")
    assert accept_response.status_code == 422
    assert "report_id" in accept_response.json()["detail"]
    assert _relation_status(client, run_id, relation_id) == "review"

    edit_response = _decide(
        client,
        review_item["review_item_id"],
        "edit",
        properties={"wording": "told", "report_id": "r-1"},
    )
    assert edit_response.status_code == 200
    assert _relation_status(client, run_id, relation_id) == "validated"
    assert client.post(f"/api/runs/{run_id}/commit").status_code == 200


def test_acceptance_records_distinguish_human_decisions_from_policy() -> None:
    client = _client()
    run_id = _start_run(client)
    ali = _add_node(client, run_id, "Ali")
    veli = _add_node(client, run_id, "Veli")
    can = _add_node(client, run_id, "Can", confidence=0.2)
    noise = _add_node(client, run_id, "Noise", confidence=0.2)
    auto_relation = _add_relation(client, run_id, ali, veli)
    reviewed_relation = _add_relation(client, run_id, veli, ali, confidence=0.2)
    dependent_relation = _add_relation(client, run_id, ali, can)
    _validate(client, run_id)

    can_item_id = _review_item_for(client, run_id, can)["review_item_id"]
    assert _decide(client, can_item_id, "reject", reviewer_id="ayse").status_code == 200
    can_decision = _decide(
        client, can_item_id, "accept", reviewer_id="mehmet", duration_ms=1500
    ).json()["decisions"][-1]
    noise_item_id = _review_item_for(client, run_id, noise)["review_item_id"]
    assert _decide(client, noise_item_id, "reject").status_code == 200
    reviewed_item_id = _review_item_for(client, run_id, reviewed_relation)["review_item_id"]
    reviewed_decision = _decide(
        client, reviewed_item_id, "edit", reviewer_id="ayse", confidence=0.9
    ).json()["decisions"][-1]

    response = client.get(f"/api/runs/{run_id}/acceptance-records")

    assert response.status_code == 200
    records = {record["candidate_ref"]: record for record in response.json()}
    assert set(records) == {
        ali,
        veli,
        can,
        auto_relation,
        reviewed_relation,
        dependent_relation,
    }
    for node_id in (ali, veli):
        assert records[node_id] == {
            "candidate_type": "candidate_node",
            "candidate_ref": node_id,
            "policy": "auto_validated",
            "rule_code": "candidate_node_valid",
            "decision": None,
        }
    assert records[auto_relation] == {
        "candidate_type": "candidate_relation",
        "candidate_ref": auto_relation,
        "policy": "auto_validated",
        "rule_code": "candidate_relation_valid",
        "decision": None,
    }
    assert records[dependent_relation] == {
        "candidate_type": "candidate_relation",
        "candidate_ref": dependent_relation,
        "policy": "auto_validated",
        "rule_code": "relation_dependency_review",
        "decision": None,
    }
    assert records[can] == {
        "candidate_type": "candidate_node",
        "candidate_ref": can,
        "policy": None,
        "rule_code": None,
        "decision": can_decision,
    }
    assert records[can]["decision"]["reviewer_id"] == "mehmet"
    assert records[reviewed_relation]["policy"] is None
    assert records[reviewed_relation]["decision"] == reviewed_decision

    assert client.post(f"/api/runs/{run_id}/commit").status_code == 200
    committed_records = client.get(f"/api/runs/{run_id}/acceptance-records").json()
    assert {record["candidate_ref"] for record in committed_records} == set(records)


def test_acceptance_records_for_unknown_run_returns_404() -> None:
    client = _client()

    assert client.get("/api/runs/missing-run/acceptance-records").status_code == 404


def test_rejected_candidate_stays_rejected_after_revalidation() -> None:
    client = _client()
    run_id = _start_run(client)
    kept = _add_node(client, run_id, "Ali", confidence=0.9)
    duplicate = _add_node(client, run_id, "Ali", confidence=0.8)
    _validate(client, run_id)
    duplicate_item = _review_item_for(client, run_id, duplicate)
    assert duplicate_item["reason_code"] == "potential_duplicate_node"
    assert _decide(client, duplicate_item["review_item_id"], "reject").status_code == 200

    _validate(client, run_id)

    assert _node_status(client, run_id, duplicate) == "rejected"
    assert _node_status(client, run_id, kept) == "validated"
    surviving_item = _review_item_for(client, run_id, duplicate)
    assert surviving_item["review_item_id"] == duplicate_item["review_item_id"]
    assert surviving_item["status"] == "rejected"
    assert [
        (decision["action"], decision["reviewer_id"]) for decision in surviving_item["decisions"]
    ] == [("reject", "ayse")]
    delta = client.post(f"/api/runs/{run_id}/commit")
    assert delta.status_code == 200, delta.text
    assert delta.json()["nodes_created"] == 1
    assert delta.json()["rejected_count"] == 1


def test_revalidation_recomputes_candidates_without_a_decision() -> None:
    client = _client()
    run_id = _start_run(client)
    ali = _add_node(client, run_id, "Ali", confidence=0.2)
    can = _add_node(client, run_id, "Can", confidence=0.2)
    relation_id = _add_relation(client, run_id, ali, can, properties={"report_id": "r-1"})
    _validate(client, run_id)
    ali_item_id = _review_item_for(client, run_id, ali)["review_item_id"]
    assert _decide(client, ali_item_id, "accept").status_code == 200
    veli = _add_node(client, run_id, "Veli")
    late = _add_node(client, run_id, "Derya", confidence=0.2)
    node_repository = get_container().pipeline_management_service.candidate_node_repository
    drifted = node_repository.get(can)
    assert drifted is not None
    drifted.status = CandidateStatus.VALIDATED
    node_repository.save(drifted)

    _validate(client, run_id)

    assert _node_status(client, run_id, ali) == "validated"
    assert _node_status(client, run_id, veli) == "validated"
    assert _node_status(client, run_id, can) == "review"
    assert _node_status(client, run_id, late) == "review"
    assert _relation_status(client, run_id, relation_id) == "review"
    ali_item = _review_item_for(client, run_id, ali)
    assert (ali_item["review_item_id"], ali_item["status"]) == (ali_item_id, "accepted")
    assert len(ali_item["decisions"]) == 1
    assert _review_items_for(client, run_id, veli) == []
    assert {
        candidate_ref: (
            _review_item_for(client, run_id, candidate_ref)["reason_code"],
            _review_item_for(client, run_id, candidate_ref)["status"],
        )
        for candidate_ref in (can, late, relation_id)
    } == {
        can: ("node_confidence_threshold", "open"),
        late: ("node_confidence_threshold", "open"),
        relation_id: ("relation_dependency_review", "open"),
    }
