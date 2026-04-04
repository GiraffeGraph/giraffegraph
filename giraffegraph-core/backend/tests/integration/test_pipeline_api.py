from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from test_helpers import create_pipeline_definition


def test_segmentation_candidate_storage_and_validation_flow() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project_response = client.post(
        "/api/projects",
        json={
            "name": "Pipeline Lab",
            "description": "Segmentation and validation baseline",
            "template_id": "story",
        },
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["project_id"]

    schema_response = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Pipeline schema"},
    )
    assert schema_response.status_code == 201
    schema_id = schema_response.json()["schema_version_id"]

    add_character_response = client.post(
        f"/api/schema-versions/{schema_id}/node-types",
        json={
            "name": "Character",
            "display_name": "Character",
            "description": "Narrative actor",
            "merge_keys": ["name"],
            "properties": [
                {"name": "name", "data_type": "string", "required": True},
            ],
        },
    )
    assert add_character_response.status_code == 201

    add_event_response = client.post(
        f"/api/schema-versions/{schema_id}/node-types",
        json={
            "name": "Event",
            "display_name": "Event",
            "description": "Narrative event",
            "merge_keys": ["title"],
            "properties": [
                {"name": "title", "data_type": "string", "required": True},
            ],
        },
    )
    assert add_event_response.status_code == 201

    add_relation_response = client.post(
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "INVOLVED_IN",
            "from_type": "Character",
            "to_type": "Event",
            "description": "Character is involved in event",
            "confidence_threshold": 0.7,
            "required_properties": ["role"],
            "properties": [
                {"name": "role", "data_type": "string", "required": True},
            ],
        },
    )
    assert add_relation_response.status_code == 201

    create_pipeline_definition(client, schema_id=schema_id)
    activate_response = client.post(
        f"/api/projects/{project_id}/schema-versions/{schema_id}/activate"
    )
    assert activate_response.status_code == 200

    source_response = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali enters the room.\n\nA fight starts in the alley.",
            "sequence_no": 1,
        },
    )
    assert source_response.status_code == 201
    source_id = source_response.json()["source_unit_id"]

    run_response = client.post(
        f"/api/source-units/{source_id}/runs",
        json={
            "schema_version_id": schema_id,
            "pipeline_version": "v1",
            "llm_provider": "openai",
            "llm_model": "gpt-test",
        },
    )
    assert run_response.status_code == 201
    run_id = run_response.json()["run_id"]

    segments_response = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    )
    assert segments_response.status_code == 201
    segments = segments_response.json()
    assert [segment["segment_order"] for segment in segments] == [1, 2]
    first_segment_id = segments[0]["segment_id"]
    second_segment_id = segments[1]["segment_id"]

    character_candidate_response = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": first_segment_id, "quote": "Ali enters the room."}],
        },
    )
    assert character_candidate_response.status_code == 201
    character_candidate_id = character_candidate_response.json()["candidate_node_id"]

    event_candidate_response = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Event",
            "properties": {"title": "Alley Fight"},
            "merge_key_payload": {"title": "Alley Fight"},
            "confidence": 0.4,
            "evidence_refs": [
                {
                    "segment_id": second_segment_id,
                    "quote": "A fight starts in the alley.",
                }
            ],
        },
    )
    assert event_candidate_response.status_code == 201
    event_candidate_id = event_candidate_response.json()["candidate_node_id"]

    review_relation_response = client.post(
        f"/api/runs/{run_id}/candidate-relations",
        json={
            "relation_type": "INVOLVED_IN",
            "from_candidate_ref": character_candidate_id,
            "to_candidate_ref": event_candidate_id,
            "properties": {"role": "participant"},
            "confidence": 0.92,
            "evidence_refs": [{"segment_id": second_segment_id}],
        },
    )
    assert review_relation_response.status_code == 201

    rejected_relation_response = client.post(
        f"/api/runs/{run_id}/candidate-relations",
        json={
            "relation_type": "INVOLVED_IN",
            "from_candidate_ref": character_candidate_id,
            "to_candidate_ref": event_candidate_id,
            "properties": {},
            "confidence": 0.85,
        },
    )
    assert rejected_relation_response.status_code == 201

    validation_response = client.post(f"/api/runs/{run_id}/validate")
    assert validation_response.status_code == 200
    validation = validation_response.json()
    assert validation["node_total"] == 2
    assert validation["node_validated"] == 1
    assert validation["node_review"] == 1
    assert validation["node_rejected"] == 0
    assert validation["relation_total"] == 2
    assert validation["relation_validated"] == 0
    assert validation["relation_review"] == 1
    assert validation["relation_rejected"] == 1
    assert len(validation["validation_results"]) >= 4

    run_detail_response = client.get(f"/api/runs/{run_id}")
    assert run_detail_response.status_code == 200
    assert run_detail_response.json()["status"] == "running"
    assert run_detail_response.json()["started_at"] is not None

    source_detail_response = client.get(f"/api/source-units/{source_id}")
    assert source_detail_response.status_code == 200
    assert source_detail_response.json()["status"] == "processing"

    candidate_nodes_response = client.get(f"/api/runs/{run_id}/candidate-nodes")
    assert candidate_nodes_response.status_code == 200
    node_statuses = {
        item["candidate_node_id"]: item["status"]
        for item in candidate_nodes_response.json()
    }
    assert node_statuses[character_candidate_id] == "validated"
    assert node_statuses[event_candidate_id] == "review"

    candidate_relations_response = client.get(f"/api/runs/{run_id}/candidate-relations")
    assert candidate_relations_response.status_code == 200
    relation_statuses = [item["status"] for item in candidate_relations_response.json()]
    assert sorted(relation_statuses) == ["rejected", "review"]

    validation_results_response = client.get(f"/api/runs/{run_id}/validation-results")
    assert validation_results_response.status_code == 200
    validation_results = validation_results_response.json()
    assert any(result["result"] == "review" for result in validation_results)
    assert any(result["result"] == "failed" for result in validation_results)

    review_items_response = client.get(f"/api/runs/{run_id}/review-items")
    assert review_items_response.status_code == 200
    review_items = review_items_response.json()
    assert len(review_items) == 2
    assert sorted(item["item_type"] for item in review_items) == [
        "candidate_node",
        "candidate_relation",
    ]


def test_validation_derives_merge_keys_and_detects_whitespace_normalized_duplicates() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Resolution Lab",
            "description": "Derived merge keys and normalized duplicate detection",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Resolution schema"},
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
            "source_type": "notes",
            "title": "Entity notes",
            "raw_content": "Ali Veli note",
        },
    ).json()
    run = client.post(
        f"/api/source-units/{source['source_unit_id']}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_id = run["run_id"]

    primary_node = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali   Veli"},
            "confidence": 0.95,
        },
    ).json()
    duplicate_node = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "character",
            "properties": {"name": " ali veli "},
            "confidence": 0.9,
        },
    ).json()

    validation_response = client.post(f"/api/runs/{run_id}/validate")
    assert validation_response.status_code == 200

    candidate_nodes = client.get(f"/api/runs/{run_id}/candidate-nodes").json()
    by_id = {item["candidate_node_id"]: item for item in candidate_nodes}
    assert by_id[primary_node["candidate_node_id"]]["merge_key_payload"] == {
        "name": "Ali   Veli"
    }
    assert by_id[duplicate_node["candidate_node_id"]]["merge_key_payload"] == {
        "name": " ali veli "
    }
    assert by_id[primary_node["candidate_node_id"]]["status"] == "validated"
    assert by_id[duplicate_node["candidate_node_id"]]["status"] == "review"

    validation_results = client.get(f"/api/runs/{run_id}/validation-results").json()
    duplicate_result = next(
        result
        for result in validation_results
        if result["candidate_ref"] == duplicate_node["candidate_node_id"]
        and result["rule_code"] == "potential_duplicate_node"
    )
    assert duplicate_result["result"] == "review"


def test_validation_flags_relations_as_duplicates_when_endpoints_share_identity() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Relation Resolution Lab",
            "description": "Relation dedup should use resolved endpoint identity",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Relation resolution schema"},
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
    client.post(
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "INVOLVED_IN",
            "from_type": "Character",
            "to_type": "Event",
            "description": "Character is involved in event",
            "required_properties": ["role"],
            "properties": [{"name": "role", "data_type": "string", "required": True}],
        },
    )
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "notes",
            "title": "Relation notes",
            "raw_content": "Ali participates in the alley fight.",
        },
    ).json()
    run = client.post(
        f"/api/source-units/{source['source_unit_id']}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_id = run["run_id"]

    primary_character = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali   Veli"},
            "confidence": 0.95,
        },
    ).json()
    duplicate_character = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "ali veli"},
            "confidence": 0.9,
        },
    ).json()
    event = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Event",
            "properties": {"title": "Alley Fight"},
            "confidence": 0.96,
        },
    ).json()

    primary_relation = client.post(
        f"/api/runs/{run_id}/candidate-relations",
        json={
            "relation_type": "INVOLVED_IN",
            "from_candidate_ref": primary_character["candidate_node_id"],
            "to_candidate_ref": event["candidate_node_id"],
            "properties": {"role": "participant"},
            "confidence": 0.95,
        },
    ).json()
    duplicate_relation = client.post(
        f"/api/runs/{run_id}/candidate-relations",
        json={
            "relation_type": "INVOLVED_IN",
            "from_candidate_ref": duplicate_character["candidate_node_id"],
            "to_candidate_ref": event["candidate_node_id"],
            "properties": {"role": "participant"},
            "confidence": 0.9,
        },
    ).json()

    validation_response = client.post(f"/api/runs/{run_id}/validate")
    assert validation_response.status_code == 200

    candidate_relations = client.get(f"/api/runs/{run_id}/candidate-relations").json()
    relation_by_id = {
        item["candidate_relation_id"]: item for item in candidate_relations
    }
    assert relation_by_id[primary_relation["candidate_relation_id"]]["status"] == "validated"
    assert relation_by_id[duplicate_relation["candidate_relation_id"]]["status"] == "review"

    validation_results = client.get(f"/api/runs/{run_id}/validation-results").json()
    duplicate_relation_result = next(
        result
        for result in validation_results
        if result["candidate_ref"] == duplicate_relation["candidate_relation_id"]
        and result["rule_code"] == "potential_duplicate_relation"
    )
    assert duplicate_relation_result["result"] == "review"


def test_validation_reports_matches_against_existing_canonical_graph() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Canonical Resolution Lab",
            "description": "Validation should detect existing canonical matches",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Canonical resolution schema"},
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
    client.post(
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "INVOLVED_IN",
            "from_type": "Character",
            "to_type": "Event",
            "description": "Character is involved in event",
            "required_properties": ["role"],
            "properties": [{"name": "role", "data_type": "string", "required": True}],
        },
    )
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source_one = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "notes",
            "title": "Source 1",
            "raw_content": "Ali joins the alley fight.",
            "sequence_no": 1,
        },
    ).json()
    run_one = client.post(
        f"/api/source-units/{source_one['source_unit_id']}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_one_id = run_one["run_id"]

    character_one = client.post(
        f"/api/runs/{run_one_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "confidence": 0.98,
        },
    ).json()
    event_one = client.post(
        f"/api/runs/{run_one_id}/candidate-nodes",
        json={
            "node_type": "Event",
            "properties": {"title": "Alley Fight"},
            "confidence": 0.97,
        },
    ).json()
    client.post(
        f"/api/runs/{run_one_id}/candidate-relations",
        json={
            "relation_type": "INVOLVED_IN",
            "from_candidate_ref": character_one["candidate_node_id"],
            "to_candidate_ref": event_one["candidate_node_id"],
            "properties": {"role": "participant"},
            "confidence": 0.96,
        },
    )

    validate_one = client.post(f"/api/runs/{run_one_id}/validate")
    assert validate_one.status_code == 200
    commit_one = client.post(f"/api/runs/{run_one_id}/commit")
    assert commit_one.status_code == 200

    source_two = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "notes",
            "title": "Source 2",
            "raw_content": " ali   joins the alley fight again.",
            "sequence_no": 2,
        },
    ).json()
    run_two = client.post(
        f"/api/source-units/{source_two['source_unit_id']}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_two_id = run_two["run_id"]

    character_two = client.post(
        f"/api/runs/{run_two_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": " ali "},
            "confidence": 0.98,
        },
    ).json()
    event_two = client.post(
        f"/api/runs/{run_two_id}/candidate-nodes",
        json={
            "node_type": "Event",
            "properties": {"title": " Alley Fight "},
            "confidence": 0.97,
        },
    ).json()
    relation_two = client.post(
        f"/api/runs/{run_two_id}/candidate-relations",
        json={
            "relation_type": "INVOLVED_IN",
            "from_candidate_ref": character_two["candidate_node_id"],
            "to_candidate_ref": event_two["candidate_node_id"],
            "properties": {"role": "participant"},
            "confidence": 0.96,
        },
    ).json()

    validate_two = client.post(f"/api/runs/{run_two_id}/validate")
    assert validate_two.status_code == 200

    validation_results = client.get(f"/api/runs/{run_two_id}/validation-results").json()
    node_match_ids = {
        result["candidate_ref"]
        for result in validation_results
        if result["rule_code"] == "canonical_node_match"
    }
    relation_match_ids = {
        result["candidate_ref"]
        for result in validation_results
        if result["rule_code"] == "canonical_relation_match"
    }

    assert character_two["candidate_node_id"] in node_match_ids
    assert event_two["candidate_node_id"] in node_match_ids
    assert relation_two["candidate_relation_id"] in relation_match_ids


def test_validation_uses_node_type_confidence_threshold_from_schema() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Node Threshold Lab",
            "description": "Node threshold should come from schema data",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Node threshold schema"},
    ).json()
    schema_id = schema["schema_version_id"]

    client.post(
        f"/api/schema-versions/{schema_id}/node-types",
        json={
            "name": "Character",
            "display_name": "Character",
            "description": "Narrative actor",
            "merge_keys": ["name"],
            "confidence_threshold": 0.7,
            "properties": [{"name": "name", "data_type": "string", "required": True}],
        },
    )
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "notes",
            "title": "Threshold notes",
            "raw_content": "Ali appears in the source.",
        },
    ).json()
    run = client.post(
        f"/api/source-units/{source['source_unit_id']}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    run_id = run["run_id"]

    candidate = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "confidence": 0.6,
        },
    ).json()

    validation_response = client.post(f"/api/runs/{run_id}/validate")
    assert validation_response.status_code == 200
    validation = validation_response.json()
    assert validation["node_validated"] == 0
    assert validation["node_review"] == 1

    candidate_nodes = client.get(f"/api/runs/{run_id}/candidate-nodes").json()
    assert candidate_nodes[0]["candidate_node_id"] == candidate["candidate_node_id"]
    assert candidate_nodes[0]["status"] == "review"

    validation_results = client.get(f"/api/runs/{run_id}/validation-results").json()
    threshold_result = next(
        result
        for result in validation_results
        if result["candidate_ref"] == candidate["candidate_node_id"]
        and result["rule_code"] == "node_confidence_threshold"
    )
    assert "(0.70)" in threshold_result["message"]
