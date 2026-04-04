from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container


def test_project_and_schema_management_flow() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    create_project_response = client.post(
        "/api/projects",
        json={
            "name": "Story Graph Lab",
            "description": "Internal dashboard workspace",
            "template_id": "story",
        },
    )
    assert create_project_response.status_code == 201
    project = create_project_response.json()
    project_id = project["project_id"]
    assert project["status"] == "active"

    create_schema_response = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Initial draft"},
    )
    assert create_schema_response.status_code == 201
    schema = create_schema_response.json()
    schema_version_id = schema["schema_version_id"]
    assert schema["status"] == "draft"

    pipeline_definitions_response = client.get(
        f"/api/schema-versions/{schema_version_id}/pipeline-definitions"
    )
    assert pipeline_definitions_response.status_code == 200
    pipeline_definitions = pipeline_definitions_response.json()
    assert len(pipeline_definitions) == 1
    assert pipeline_definitions[0]["version"] == "v1"
    assert pipeline_definitions[0]["steps"][0]["job_type"] == "extract_candidates"

    add_character_response = client.post(
        f"/api/schema-versions/{schema_version_id}/node-types",
        json={
            "name": "Character",
            "display_name": "Character",
            "description": "A story character",
            "merge_keys": ["name"],
            "confidence_threshold": 0.65,
            "properties": [
                {
                    "name": "name",
                    "data_type": "string",
                    "required": True,
                }
            ],
        },
    )
    assert add_character_response.status_code == 201
    assert len(add_character_response.json()["node_types"]) == 1
    assert add_character_response.json()["node_types"][0]["confidence_threshold"] == 0.65

    add_event_response = client.post(
        f"/api/schema-versions/{schema_version_id}/node-types",
        json={
            "name": "Event",
            "display_name": "Event",
            "description": "A story event",
        },
    )
    assert add_event_response.status_code == 201
    assert len(add_event_response.json()["node_types"]) == 2
    event_node = next(
        item
        for item in add_event_response.json()["node_types"]
        if item["name"] == "Event"
    )
    assert event_node["confidence_threshold"] == 0.5

    add_relation_response = client.post(
        f"/api/schema-versions/{schema_version_id}/relation-types",
        json={
            "name": "INVOLVED_IN",
            "from_type": "Character",
            "to_type": "Event",
            "description": "Character participates in event",
            "required_properties": ["role"],
            "properties": [
                {
                    "name": "role",
                    "data_type": "string",
                    "required": True,
                }
            ],
        },
    )
    assert add_relation_response.status_code == 201
    assert len(add_relation_response.json()["relation_types"]) == 1

    activate_response = client.post(
        f"/api/projects/{project_id}/schema-versions/{schema_version_id}/activate"
    )
    assert activate_response.status_code == 200
    activated_schema = activate_response.json()
    assert activated_schema["status"] == "active"

    active_schema_response = client.get(f"/api/projects/{project_id}/active-schema")
    assert active_schema_response.status_code == 200
    active_schema = active_schema_response.json()
    assert active_schema["schema_version_id"] == schema_version_id
    assert len(active_schema["node_types"]) == 2
    assert len(active_schema["relation_types"]) == 1

    rejected_edit_response = client.post(
        f"/api/schema-versions/{schema_version_id}/node-types",
        json={
            "name": "Location",
            "display_name": "Location",
            "description": "A story location",
        },
    )
    assert rejected_edit_response.status_code == 422
