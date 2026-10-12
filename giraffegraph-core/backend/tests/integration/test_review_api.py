from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from test_helpers import create_pipeline_definition


def test_project_review_queue_endpoint_returns_enriched_run_groups() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Review Queue Lab",
            "description": "Project-level review queue read model",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Review queue schema"},
    ).json()
    schema_id = schema["schema_version_id"]

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
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    review_source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali is mentioned once.",
            "sequence_no": 1,
        },
    ).json()
    review_run = client.post(
        f"/api/source-units/{review_source['source_unit_id']}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    review_segments = client.post(
        f"/api/source-units/{review_source['source_unit_id']}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()
    review_candidate = client.post(
        f"/api/runs/{review_run['run_id']}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.2,
            "evidence_refs": [{"segment_id": review_segments[0]["segment_id"]}],
        },
    ).json()
    validate_response = client.post(f"/api/runs/{review_run['run_id']}/validate")
    assert validate_response.status_code == 200

    clean_source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 2",
            "raw_content": "No extracted candidates yet.",
            "sequence_no": 2,
        },
    ).json()
    clean_run = client.post(
        f"/api/source-units/{clean_source['source_unit_id']}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()

    queue_response = client.get(
        f"/api/projects/{project_id}/review-queue?status_filter=all&run_limit=12"
    )
    assert queue_response.status_code == 200
    queue = queue_response.json()

    assert queue["project_id"] == project_id
    assert queue["status_filter"] == "all"
    assert queue["run_limit"] == 12
    assert queue["open_review_count"] == 1
    assert queue["total_review_count"] == 1
    assert queue["filtered_run_count"] == 2
    assert queue["returned_run_count"] == 2
    assert queue["returned_review_count"] == 1
    assert queue["has_more_runs"] is False
    assert len(queue["run_entries"]) == 2

    reviewed_entry = next(
        entry for entry in queue["run_entries"] if entry["run"]["run_id"] == review_run["run_id"]
    )
    assert reviewed_entry["source_unit"]["title"] == "Episode 1"
    assert reviewed_entry["open_review_count"] == 1
    assert reviewed_entry["total_review_count"] == 1
    assert len(reviewed_entry["review_items"]) == 1

    review_item = reviewed_entry["review_items"][0]
    assert review_item["headline"] == "Character · Ali"
    assert review_item["confidence"] == 0.2
    assert review_item["review_item"]["item_ref"] == review_candidate["candidate_node_id"]
    assert (
        review_item["candidate_node"]["candidate_node_id"]
        == review_candidate["candidate_node_id"]
    )
    assert review_item["candidate_relation"] is None
    assert review_item["evidence_snippets"] == [
        {
            "segment_id": review_segments[0]["segment_id"],
            "segment_order": 1,
            "text": "Ali is mentioned once.",
            "quote": None,
        }
    ]

    empty_entry = next(
        entry for entry in queue["run_entries"] if entry["run"]["run_id"] == clean_run["run_id"]
    )
    assert empty_entry["source_unit"]["title"] == "Episode 2"
    assert empty_entry["open_review_count"] == 0
    assert empty_entry["total_review_count"] == 0
    assert empty_entry["review_items"] == []

    open_queue_response = client.get(f"/api/projects/{project_id}/review-queue")
    assert open_queue_response.status_code == 200
    open_queue = open_queue_response.json()
    assert open_queue["status_filter"] == "open"
    assert open_queue["filtered_run_count"] == 1
    assert open_queue["returned_run_count"] == 1
    assert open_queue["returned_review_count"] == 1
    assert [entry["run"]["run_id"] for entry in open_queue["run_entries"]] == [
        review_run["run_id"]
    ]

    limited_queue_response = client.get(
        f"/api/projects/{project_id}/review-queue?status_filter=all&run_limit=1"
    )
    assert limited_queue_response.status_code == 200
    limited_queue = limited_queue_response.json()
    assert limited_queue["filtered_run_count"] == 2
    assert limited_queue["returned_run_count"] == 1
    assert limited_queue["has_more_runs"] is True


def test_review_queue_includes_canonical_match_context_messages() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Review Canonical Context Lab",
            "description": "Review queue should surface canonical match context",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Canonical context schema"},
    ).json()
    schema_id = schema["schema_version_id"]

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
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source_one = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali is present.",
            "sequence_no": 1,
        },
    ).json()
    run_one = client.post(
        f"/api/source-units/{source_one['source_unit_id']}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_one_id = run_one["run_id"]

    client.post(
        f"/api/runs/{run_one_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "confidence": 0.98,
        },
    )
    assert client.post(f"/api/runs/{run_one_id}/validate").status_code == 200
    assert client.post(f"/api/runs/{run_one_id}/commit").status_code == 200

    source_two = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 2",
            "raw_content": " ali is mentioned again.",
            "sequence_no": 2,
        },
    ).json()
    run_two = client.post(
        f"/api/source-units/{source_two['source_unit_id']}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_two_id = run_two["run_id"]

    review_candidate = client.post(
        f"/api/runs/{run_two_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": " ali "},
            "confidence": 0.2,
        },
    ).json()

    validate_two = client.post(f"/api/runs/{run_two_id}/validate")
    assert validate_two.status_code == 200

    queue_response = client.get(
        f"/api/projects/{project_id}/review-queue?status_filter=all&run_limit=12"
    )
    assert queue_response.status_code == 200
    queue = queue_response.json()

    reviewed_entry = next(
        entry for entry in queue["run_entries"] if entry["run"]["run_id"] == run_two_id
    )
    review_item = next(
        item
        for item in reviewed_entry["review_items"]
        if item["review_item"]["item_ref"] == review_candidate["candidate_node_id"]
    )
    assert any(
        "below the baseline review threshold" in message
        for message in review_item["messages"]
    )
    assert any("existing canonical node" in message for message in review_item["messages"])


def test_project_review_queue_enriches_relation_headlines_with_endpoint_nodes() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Relation Queue Lab",
            "description": "Relation review headline enrichment",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Relation queue schema"},
    ).json()
    schema_id = schema["schema_version_id"]

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
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "KNOWS",
            "from_type": "Character",
            "to_type": "Character",
            "description": "Character knows another character",
            "confidence_threshold": 0.7,
        },
    )
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali knows Veli.",
            "sequence_no": 1,
        },
    ).json()
    run = client.post(
        f"/api/source-units/{source['source_unit_id']}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    segments = client.post(
        f"/api/source-units/{source['source_unit_id']}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()

    ali = client.post(
        f"/api/runs/{run['run_id']}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    ).json()
    veli = client.post(
        f"/api/runs/{run['run_id']}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Veli"},
            "merge_key_payload": {"name": "Veli"},
            "confidence": 0.94,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    ).json()
    client.post(
        f"/api/runs/{run['run_id']}/candidate-relations",
        json={
            "relation_type": "KNOWS",
            "from_candidate_ref": ali["candidate_node_id"],
            "to_candidate_ref": veli["candidate_node_id"],
            "properties": {},
            "confidence": 0.2,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    )

    validate_response = client.post(f"/api/runs/{run['run_id']}/validate")
    assert validate_response.status_code == 200

    queue_response = client.get(f"/api/projects/{project_id}/review-queue")
    assert queue_response.status_code == 200
    queue = queue_response.json()

    assert queue["status_filter"] == "open"
    assert queue["run_limit"] == 12
    assert queue["filtered_run_count"] == 1
    assert queue["returned_run_count"] == 1
    assert queue["returned_review_count"] == 1
    assert queue["has_more_runs"] is False
    reviewed_entry = next(
        entry for entry in queue["run_entries"] if entry["run"]["run_id"] == run["run_id"]
    )
    assert reviewed_entry["open_review_count"] == 1
    assert reviewed_entry["total_review_count"] == 1

    review_item = reviewed_entry["review_items"][0]
    assert review_item["headline"] == "KNOWS · Character · Ali → Character · Veli"
    assert review_item["candidate_node"] is None
    assert review_item["candidate_relation"]["relation_type"] == "KNOWS"
    assert review_item["evidence_snippets"] == [
        {
            "segment_id": segments[0]["segment_id"],
            "segment_order": 1,
            "text": "Ali knows Veli.",
            "quote": None,
        }
    ]


def test_review_decision_and_duplicate_resolution_flow() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Review Lab",
            "description": "Review decisions and dedup",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Review schema"},
    ).json()
    schema_id = schema["schema_version_id"]

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
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali arrives.\n\nAnother Ali appears.\n\nA faint event is mentioned.",
            "sequence_no": 1,
        },
    ).json()
    source_id = source["source_unit_id"]

    run = client.post(
        f"/api/source-units/{source_id}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_id = run["run_id"]

    segments = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()

    client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    )
    duplicate_character = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.90,
            "evidence_refs": [{"segment_id": segments[1]["segment_id"]}],
        },
    ).json()
    low_confidence_event = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Event",
            "properties": {"title": "Faint Mention"},
            "merge_key_payload": {"title": "Faint Mention"},
            "confidence": 0.20,
            "evidence_refs": [{"segment_id": segments[2]["segment_id"]}],
        },
    ).json()

    validation_response = client.post(f"/api/runs/{run_id}/resolve-duplicates")
    assert validation_response.status_code == 200
    validation = validation_response.json()
    assert validation["node_validated"] == 1
    assert validation["node_review"] == 2
    assert validation["node_rejected"] == 0

    blocked_commit_response = client.post(f"/api/runs/{run_id}/commit")
    assert blocked_commit_response.status_code == 422

    review_items_response = client.get(f"/api/runs/{run_id}/review-items")
    assert review_items_response.status_code == 200
    review_items = review_items_response.json()
    assert len(review_items) == 2

    duplicate_review_item = next(
        item
        for item in review_items
        if item["item_ref"] == duplicate_character["candidate_node_id"]
    )
    event_review_item = next(
        item
        for item in review_items
        if item["item_ref"] == low_confidence_event["candidate_node_id"]
    )
    assert duplicate_review_item["reason_code"] == "potential_duplicate_node"
    assert event_review_item["reason_code"] == "node_confidence_threshold"

    duplicate_review_detail = client.get(
        f"/api/review-items/{duplicate_review_item['review_item_id']}"
    )
    assert duplicate_review_detail.status_code == 200
    assert duplicate_review_detail.json()["status"] == "open"

    edit_duplicate_response = client.post(
        f"/api/review-items/{duplicate_review_item['review_item_id']}/decision",
        json={
            "action": "edit",
            "reviewer_id": "ayse",
            "reviewer_note": "Second character is actually Mehmet.",
            "properties": {"name": "Mehmet"},
            "merge_key_payload": {"name": "Mehmet"},
            "confidence": 0.99,
        },
    )
    assert edit_duplicate_response.status_code == 200
    assert edit_duplicate_response.json()["status"] == "edited"

    reject_event_response = client.post(
        f"/api/review-items/{event_review_item['review_item_id']}/decision",
        json={
            "action": "reject",
            "reviewer_id": "ayse",
            "reviewer_note": "Noise candidate.",
        },
    )
    assert reject_event_response.status_code == 200
    assert reject_event_response.json()["status"] == "rejected"

    candidate_nodes_response = client.get(f"/api/runs/{run_id}/candidate-nodes")
    assert candidate_nodes_response.status_code == 200
    candidate_nodes = candidate_nodes_response.json()
    edited_duplicate = next(
        item
        for item in candidate_nodes
        if item["candidate_node_id"] == duplicate_character["candidate_node_id"]
    )
    rejected_event = next(
        item
        for item in candidate_nodes
        if item["candidate_node_id"] == low_confidence_event["candidate_node_id"]
    )
    assert edited_duplicate["status"] == "validated"
    assert edited_duplicate["properties"]["name"] == "Mehmet"
    assert rejected_event["status"] == "rejected"

    commit_response = client.post(f"/api/runs/{run_id}/commit")
    assert commit_response.status_code == 200
    graph_delta = commit_response.json()
    assert graph_delta["nodes_created"] == 2
    assert graph_delta["rejected_count"] == 1

    closed_review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    assert sorted(item["status"] for item in closed_review_items) == ["edited", "rejected"]


def test_review_edit_revalidates_against_schema() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Schema Guard",
            "description": "Review edits must stay schema-safe",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Schema guard"},
    ).json()
    schema_id = schema["schema_version_id"]

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
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali is mentioned once.",
            "sequence_no": 1,
        },
    ).json()
    source_id = source["source_unit_id"]

    run = client.post(
        f"/api/source-units/{source_id}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_id = run["run_id"]

    segments = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()

    low_confidence_character = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.20,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    ).json()

    validation_response = client.post(f"/api/runs/{run_id}/validate")
    assert validation_response.status_code == 200

    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    review_item = next(
        item
        for item in review_items
        if item["item_ref"] == low_confidence_character["candidate_node_id"]
    )

    invalid_edit_response = client.post(
        f"/api/review-items/{review_item['review_item_id']}/decision",
        json={
            "action": "edit",
            "reviewer_id": "ayse",
            "reviewer_note": "Trying an undefined type.",
            "node_type": "Ghost",
            "confidence": 0.99,
        },
    )
    assert invalid_edit_response.status_code == 422
    assert "not defined in the active schema" in invalid_edit_response.json()["detail"]

    candidate_node = client.get(f"/api/runs/{run_id}/candidate-nodes").json()[0]
    assert candidate_node["status"] == "review"


def test_review_edit_rejects_whitespace_normalized_duplicate_merge_key() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Review Duplicate Guard Lab",
            "description": "Review edits must not create normalized duplicate merge keys",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Duplicate guard schema"},
    ).json()
    schema_id = schema["schema_version_id"]

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
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali is mentioned once. Mehmet is also mentioned.",
            "sequence_no": 1,
        },
    ).json()
    source_id = source["source_unit_id"]

    run = client.post(
        f"/api/source-units/{source_id}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_id = run["run_id"]

    segments = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()

    client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali   Veli"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    )
    review_candidate = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Mehmet"},
            "confidence": 0.20,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    ).json()

    validation_response = client.post(f"/api/runs/{run_id}/validate")
    assert validation_response.status_code == 200

    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    review_item = next(
        item for item in review_items if item["item_ref"] == review_candidate["candidate_node_id"]
    )

    duplicate_edit_response = client.post(
        f"/api/review-items/{review_item['review_item_id']}/decision",
        json={
            "action": "edit",
            "reviewer_id": "ayse",
            "reviewer_note": "Trying to normalize into an existing merge key.",
            "properties": {"name": " ali veli "},
            "confidence": 0.99,
        },
    )
    assert duplicate_edit_response.status_code == 422
    assert "duplicate candidate node merge key" in duplicate_edit_response.json()["detail"]

    candidate_nodes = client.get(f"/api/runs/{run_id}/candidate-nodes").json()
    unchanged_candidate = next(
        node
        for node in candidate_nodes
        if node["candidate_node_id"] == review_candidate["candidate_node_id"]
    )
    assert unchanged_candidate["properties"]["name"] == "Mehmet"
    assert unchanged_candidate["status"] == "review"


def test_node_review_decision_refreshes_dependent_relation_reviews() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Review Dependency Lab",
            "description": "Node reviews should refresh dependent relations",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Dependency schema"},
    ).json()
    schema_id = schema["schema_version_id"]

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
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "KNOWS",
            "from_type": "Character",
            "to_type": "Character",
            "description": "Character knows another character",
            "confidence_threshold": 0.7,
        },
    )
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali arrives.\n\nAnother Ali appears.\n\nVeli observes the scene.",
            "sequence_no": 1,
        },
    ).json()
    source_id = source["source_unit_id"]

    run = client.post(
        f"/api/source-units/{source_id}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_id = run["run_id"]

    segments = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()

    client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segments[0]["segment_id"]}],
        },
    )
    duplicate_character = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.90,
            "evidence_refs": [{"segment_id": segments[1]["segment_id"]}],
        },
    ).json()
    veli = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Veli"},
            "merge_key_payload": {"name": "Veli"},
            "confidence": 0.96,
            "evidence_refs": [{"segment_id": segments[2]["segment_id"]}],
        },
    ).json()
    relation = client.post(
        f"/api/runs/{run_id}/candidate-relations",
        json={
            "relation_type": "KNOWS",
            "from_candidate_ref": duplicate_character["candidate_node_id"],
            "to_candidate_ref": veli["candidate_node_id"],
            "properties": {},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segments[2]["segment_id"]}],
        },
    ).json()

    validation_response = client.post(f"/api/runs/{run_id}/resolve-duplicates")
    assert validation_response.status_code == 200
    validation = validation_response.json()
    assert validation["relation_review"] == 1

    review_items = client.get(f"/api/runs/{run_id}/review-items").json()
    duplicate_review_item = next(
        item
        for item in review_items
        if item["item_ref"] == duplicate_character["candidate_node_id"]
    )
    relation_review_item = next(
        item
        for item in review_items
        if item["item_ref"] == relation["candidate_relation_id"]
    )
    assert relation_review_item["reason_code"] == "relation_dependency_review"

    edit_duplicate_response = client.post(
        f"/api/review-items/{duplicate_review_item['review_item_id']}/decision",
        json={
            "action": "edit",
            "reviewer_id": "ayse",
            "reviewer_note": "Second character is Mehmet.",
            "properties": {"name": "Mehmet"},
            "merge_key_payload": {"name": "Mehmet"},
            "confidence": 0.99,
        },
    )
    assert edit_duplicate_response.status_code == 200

    relation_candidates = client.get(f"/api/runs/{run_id}/candidate-relations").json()
    refreshed_relation = next(
        item
        for item in relation_candidates
        if item["candidate_relation_id"] == relation["candidate_relation_id"]
    )
    assert refreshed_relation["status"] == "validated"

    review_items_after = client.get(f"/api/runs/{run_id}/review-items").json()
    refreshed_relation_review = next(
        item
        for item in review_items_after
        if item["review_item_id"] == relation_review_item["review_item_id"]
    )
    assert refreshed_relation_review["status"] == "accepted"
    assert refreshed_relation_review["reviewer_note"] == (
        "Auto-resolved after dependent review decision."
    )

    commit_response = client.post(f"/api/runs/{run_id}/commit")
    assert commit_response.status_code == 200
    assert commit_response.json()["relations_created"] == 1
