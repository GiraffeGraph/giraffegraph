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


def _create_draft_schema(client: TestClient) -> str:
    project_id = client.post(
        "/api/projects",
        json={"name": "Schema Rules Lab", "template_id": "blank"},
    ).json()["project_id"]
    return str(
        client.post(
            f"/api/projects/{project_id}/schema-versions",
            json={"version_no": 1},
        ).json()["schema_version_id"]
    )


def _add_person_node_type(client: TestClient, schema_version_id: str) -> None:
    response = client.post(
        f"/api/schema-versions/{schema_version_id}/node-types",
        json={
            "name": "Person",
            "display_name": "Kişi / راوي",
            "description": "A person",
            "merge_keys": ["name"],
            "properties": [{"name": "name", "data_type": "string", "required": True}],
        },
    )
    assert response.status_code == 201
    assert response.json()["node_types"][0]["display_name"] == "Kişi / راوي"


def test_schema_accepts_ascii_identifiers_with_non_ascii_display_name() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    schema_version_id = _create_draft_schema(client)

    _add_person_node_type(client, schema_version_id)

    relation_response = client.post(
        f"/api/schema-versions/{schema_version_id}/relation-types",
        json={
            "name": "BORN_IN_2",
            "from_type": "Person",
            "to_type": "Person",
            "description": "Doğdu",
            "properties": [{"name": "_birth_place", "data_type": "string"}],
        },
    )
    assert relation_response.status_code == 201


def test_schema_rejects_non_identifier_type_and_property_names() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    schema_version_id = _create_draft_schema(client)
    _add_person_node_type(client, schema_version_id)

    def add_node_type(name: str, property_name: str) -> int:
        return client.post(
            f"/api/schema-versions/{schema_version_id}/node-types",
            json={
                "name": name,
                "display_name": "Yer",
                "description": "A place",
                "properties": [{"name": property_name, "data_type": "string"}],
            },
        ).status_code

    def add_relation_type(name: str, property_name: str) -> int:
        return client.post(
            f"/api/schema-versions/{schema_version_id}/relation-types",
            json={
                "name": name,
                "from_type": "Person",
                "to_type": "Person",
                "description": "Born in",
                "properties": [{"name": property_name, "data_type": "string"}],
            },
        ).status_code

    assert add_node_type("Şehir", "name") == 422
    assert add_node_type("City", "adı") == 422
    assert add_node_type("City Name", "name") == 422
    assert add_node_type("1City", "name") == 422
    assert add_relation_type("doğdu", "place") == 422
    assert add_relation_type("BORN-IN", "place") == 422
    assert add_relation_type("BORN_IN", "doğum_yeri") == 422

    schema = client.get(f"/api/schema-versions/{schema_version_id}").json()
    assert [node_type["name"] for node_type in schema["node_types"]] == ["Person"]
    assert schema["relation_types"] == []

    rejection = client.post(
        f"/api/schema-versions/{schema_version_id}/relation-types",
        json={
            "name": "doğdu",
            "from_type": "Person",
            "to_type": "Person",
            "description": "Born in",
        },
    )
    assert rejection.json()["detail"][0]["loc"] == ["body", "name"]


def test_relation_type_merge_keys_must_name_declared_properties() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())
    schema_version_id = _create_draft_schema(client)
    _add_person_node_type(client, schema_version_id)
    relation_type = {
        "name": "TOLD",
        "from_type": "Person",
        "to_type": "Person",
        "description": "One person told another",
        "properties": [{"name": "report_id", "data_type": "string"}],
    }

    rejected_response = client.post(
        f"/api/schema-versions/{schema_version_id}/relation-types",
        json={**relation_type, "merge_keys": ["report_id", "position"]},
    )
    assert rejected_response.status_code == 422
    assert "position" in rejected_response.json()["detail"]

    accepted_response = client.post(
        f"/api/schema-versions/{schema_version_id}/relation-types",
        json={**relation_type, "merge_keys": ["report_id"]},
    )
    assert accepted_response.status_code == 201
    assert accepted_response.json()["relation_types"][0]["merge_keys"] == ["report_id"]

    default_response = client.post(
        f"/api/schema-versions/{schema_version_id}/relation-types",
        json={**relation_type, "name": "HEARD"},
    )
    assert default_response.status_code == 201
    heard = next(
        item for item in default_response.json()["relation_types"] if item["name"] == "HEARD"
    )
    assert heard["merge_keys"] == []
