from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.infrastructure.persistence.postgres.database import get_postgres_engine
from test_helpers import create_pipeline_definition

pytestmark = pytest.mark.real_db


def _start_run(client: TestClient) -> tuple[str, str]:
    project_id = client.post(
        "/api/projects",
        json={"name": "Review decisions on real databases", "template_id": "blank"},
    ).json()["project_id"]
    schema_id = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1},
    ).json()["schema_version_id"]
    node_type = client.post(
        f"/api/schema-versions/{schema_id}/node-types",
        json={
            "name": "Person",
            "display_name": "Person",
            "description": "A person",
            "merge_keys": ["name"],
            "properties": [{"name": "name", "data_type": "string", "required": True}],
        },
    )
    assert node_type.status_code == 201, node_type.text
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")
    source_unit_id = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "report",
            "title": "Reports",
            "raw_content": "Ali told Veli.",
        },
    ).json()["source_unit_id"]
    run_id = client.post(
        f"/api/source-units/{source_unit_id}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()["run_id"]
    return project_id, run_id


def _add_node(client: TestClient, run_id: str, name: str, *, confidence: float) -> str:
    response = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={"node_type": "Person", "properties": {"name": name}, "confidence": confidence},
    )
    assert response.status_code == 201, response.text
    return str(response.json()["candidate_node_id"])


def _review_item_id(client: TestClient, run_id: str, candidate_ref: str) -> str:
    items = [
        item
        for item in client.get(f"/api/runs/{run_id}/review-items").json()
        if item["item_ref"] == candidate_ref
    ]
    assert len(items) == 1
    return str(items[0]["review_item_id"])


def _decide(client: TestClient, review_item_id: str, **body: object) -> dict[str, Any]:
    response = client.post(f"/api/review-items/{review_item_id}/decision", json=body)
    assert response.status_code == 200, response.text
    return dict(response.json())


def test_review_decisions_are_stored_appended_and_returned(real_db_client: TestClient) -> None:
    client = real_db_client
    project_id, run_id = _start_run(client)
    trusted_node_id = _add_node(client, run_id, "Veli", confidence=0.95)
    doubtful_node_id = _add_node(client, run_id, "Ali", confidence=0.2)
    assert client.post(f"/api/runs/{run_id}/validate").status_code == 200
    review_item_id = _review_item_id(client, run_id, doubtful_node_id)

    first = _decide(
        client,
        review_item_id,
        action="reject",
        reviewer_id="ayse",
        duration_ms=1000,
        reviewer_note="Not in the source.",
    )
    second = _decide(
        client,
        review_item_id,
        action="edit",
        reviewer_id="mehmet",
        duration_ms=2000,
        properties={"name": "Ali bin Veli"},
        confidence=0.99,
    )

    assert [
        (decision["action"], decision["reviewer_id"], decision["duration_ms"])
        for decision in second["decisions"]
    ] == [("reject", "ayse", 1000), ("edit", "mehmet", 2000)]
    assert second["decisions"][0] == first["decisions"][0]
    edit = second["decisions"][1]
    assert (edit["before_json"]["properties"], edit["after_json"]["properties"]) == (
        {"name": "Ali"},
        {"name": "Ali bin Veli"},
    )
    assert client.get(f"/api/review-items/{review_item_id}").json()["decisions"] == (
        second["decisions"]
    )
    queue = client.get(
        f"/api/projects/{project_id}/review-queue",
        params={"status_filter": "closed"},
    ).json()
    assert queue["run_entries"][0]["review_items"][0]["review_item"]["decisions"] == (
        second["decisions"]
    )
    with get_postgres_engine().connect() as connection:
        stored = connection.execute(
            text(
                "SELECT action, reviewer_id, duration_ms, reviewer_note, before_json IS NULL, "
                "after_json -> 'properties' ->> 'name', decided_at = :decided_at "
                "FROM review_decisions WHERE run_id = :run_id ORDER BY decided_at"
            ),
            {"run_id": run_id, "decided_at": edit["decided_at"]},
        ).all()
    assert [tuple(row) for row in stored] == [
        ("reject", "ayse", 1000, "Not in the source.", True, None, False),
        ("edit", "mehmet", 2000, None, False, "Ali bin Veli", True),
    ]

    records = {
        record["candidate_ref"]: record
        for record in client.get(f"/api/runs/{run_id}/acceptance-records").json()
    }
    assert records[doubtful_node_id]["decision"] == edit
    assert records[trusted_node_id]["policy"] == "auto_validated"
    assert records[trusted_node_id]["decision"] is None

    commit = client.post(f"/api/runs/{run_id}/commit")
    assert commit.status_code == 200, commit.text
    nodes = client.get(f"/api/projects/{project_id}/graph/nodes").json()
    assert sorted(node["properties"]["name"] for node in nodes) == ["Ali bin Veli", "Veli"]
