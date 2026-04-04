from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container


def _create_draft_schema(client: TestClient) -> str:
    project = client.post(
        "/api/projects",
        json={
            "name": "Pipeline Definition Lab",
            "description": "Pipeline definition tests",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]
    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Draft schema"},
    ).json()
    schema_id = schema["schema_version_id"]
    assert isinstance(schema_id, str)
    return schema_id


def test_pipeline_definition_api_creates_lists_and_gets_definition() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    schema_id = _create_draft_schema(client)

    list_response = client.get(f"/api/schema-versions/{schema_id}/pipeline-definitions")
    assert list_response.status_code == 200
    seeded_definitions = list_response.json()
    assert len(seeded_definitions) == 1
    assert seeded_definitions[0]["version"] == "v1"

    get_response = client.get(f"/api/schema-versions/{schema_id}/pipeline-definitions/v1")
    assert get_response.status_code == 200
    seeded_definition = get_response.json()
    assert seeded_definition["steps"][1]["chain_on_success"] == ["commit_run"]

    create_response = client.post(
        f"/api/schema-versions/{schema_id}/pipeline-definitions",
        json={
            "version": "v2",
            "description": "Alternate queue flow",
            "steps": [
                {
                    "job_type": "extract_candidates",
                    "chain_on_success": ["validate_run"],
                },
                {
                    "job_type": "validate_run",
                    "chain_on_success": ["commit_run"],
                },
                {
                    "job_type": "commit_run",
                    "chain_on_success": [],
                },
            ],
        },
    )
    assert create_response.status_code == 201
    created_definition = create_response.json()
    assert created_definition["version"] == "v2"
    assert created_definition["steps"][0]["job_type"] == "extract_candidates"

    list_response = client.get(f"/api/schema-versions/{schema_id}/pipeline-definitions")
    assert list_response.status_code == 200
    listed_definitions = list_response.json()
    assert len(listed_definitions) == 2
    assert (
        listed_definitions[1]["pipeline_definition_id"]
        == created_definition["pipeline_definition_id"]
    )

    get_response = client.get(f"/api/schema-versions/{schema_id}/pipeline-definitions/v2")
    assert get_response.status_code == 200
    fetched_definition = get_response.json()
    assert (
        fetched_definition["pipeline_definition_id"]
        == created_definition["pipeline_definition_id"]
    )
    assert fetched_definition["steps"][1]["chain_on_success"] == ["commit_run"]


def test_pipeline_definition_api_rejects_circular_chain() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    schema_id = _create_draft_schema(client)

    create_response = client.post(
        f"/api/schema-versions/{schema_id}/pipeline-definitions",
        json={
            "version": "v2",
            "steps": [
                {
                    "job_type": "extract_candidates",
                    "chain_on_success": ["validate_run"],
                },
                {
                    "job_type": "validate_run",
                    "chain_on_success": ["extract_candidates"],
                },
            ],
        },
    )
    assert create_response.status_code == 422
    assert "circular chains" in create_response.json()["detail"]


def test_pipeline_definition_api_rejects_duplicate_seeded_version() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    schema_id = _create_draft_schema(client)

    create_response = client.post(
        f"/api/schema-versions/{schema_id}/pipeline-definitions",
        json={
            "version": "v1",
            "steps": [
                {
                    "job_type": "extract_candidates",
                    "chain_on_success": ["validate_run"],
                },
                {
                    "job_type": "validate_run",
                    "chain_on_success": ["commit_run"],
                },
                {
                    "job_type": "commit_run",
                    "chain_on_success": [],
                },
            ],
        },
    )
    assert create_response.status_code == 409
    assert "already exists" in create_response.json()["detail"]
