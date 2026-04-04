from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from test_helpers import create_pipeline_definition


def test_commit_flow_creates_graph_delta_and_updates_statuses() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project_response = client.post(
        "/api/projects",
        json={
            "name": "Commit Lab",
            "description": "Graph delta baseline",
            "template_id": "story",
        },
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["project_id"]

    schema_response = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Commit schema"},
    )
    assert schema_response.status_code == 201
    schema_id = schema_response.json()["schema_version_id"]

    client.post(
        f"/api/schema-versions/{schema_id}/node-types",
        json={
            "name": "Character",
            "display_name": "Character",
            "description": "Narrative actor",
            "merge_keys": ["name"],
            "properties": [{"name": "name", "data_type": "string", "required": True}],
        },
    )
    client.post(
        f"/api/schema-versions/{schema_id}/node-types",
        json={
            "name": "Event",
            "display_name": "Event",
            "description": "Narrative event",
            "merge_keys": ["title"],
            "properties": [{"name": "title", "data_type": "string", "required": True}],
        },
    )
    client.post(
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "INVOLVED_IN",
            "from_type": "Character",
            "to_type": "Event",
            "description": "Character is involved in event",
            "confidence_threshold": 0.7,
            "required_properties": ["role"],
            "properties": [{"name": "role", "data_type": "string", "required": True}],
        },
    )
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source_response = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali walks in.\n\nA fight starts.",
            "sequence_no": 1,
        },
    )
    source_id = source_response.json()["source_unit_id"]

    run_response = client.post(
        f"/api/source-units/{source_id}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    )
    run_id = run_response.json()["run_id"]

    segments = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()

    character_candidate = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    ).json()

    event_candidate = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Event",
            "properties": {"title": "Fight"},
            "merge_key_payload": {"title": "Fight"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segments[1]["segment_id"]}],
        },
    ).json()

    client.post(
        f"/api/runs/{run_id}/candidate-relations",
        json={
            "relation_type": "INVOLVED_IN",
            "from_candidate_ref": character_candidate["candidate_node_id"],
            "to_candidate_ref": event_candidate["candidate_node_id"],
            "properties": {"role": "participant"},
            "confidence": 0.95,
        },
    )

    validation_response = client.post(f"/api/runs/{run_id}/validate")
    assert validation_response.status_code == 200
    validation = validation_response.json()
    assert validation["node_validated"] == 2
    assert validation["relation_validated"] == 1

    review_items_response = client.get(f"/api/runs/{run_id}/review-items")
    assert review_items_response.status_code == 200
    assert review_items_response.json() == []

    commit_response = client.post(f"/api/runs/{run_id}/commit")
    assert commit_response.status_code == 200
    graph_delta = commit_response.json()
    assert graph_delta["project_id"] == project_id
    assert graph_delta["nodes_created"] == 2
    assert graph_delta["relations_created"] == 1
    assert graph_delta["review_count"] == 0
    assert graph_delta["rejected_count"] == 0

    get_graph_delta_response = client.get(f"/api/runs/{run_id}/graph-delta")
    assert get_graph_delta_response.status_code == 200
    assert get_graph_delta_response.json()["delta_id"] == graph_delta["delta_id"]

    run_detail_response = client.get(f"/api/runs/{run_id}")
    assert run_detail_response.status_code == 200
    assert run_detail_response.json()["status"] == "completed"

    source_detail_response = client.get(f"/api/source-units/{source_id}")
    assert source_detail_response.status_code == 200
    assert source_detail_response.json()["status"] == "processed"

    completed_run_mutation_response = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Later edit"},
            "merge_key_payload": {"name": "Later edit"},
            "confidence": 0.9,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    )
    assert completed_run_mutation_response.status_code == 422

    overview_response = client.get(f"/api/projects/{project_id}/graph/overview")
    assert overview_response.status_code == 200
    overview = overview_response.json()
    assert overview["node_count"] == 2
    assert overview["relation_count"] == 1
    assert overview["node_type_counts"] == [
        {"node_type": "Character", "count": 1},
        {"node_type": "Event", "count": 1},
    ]
