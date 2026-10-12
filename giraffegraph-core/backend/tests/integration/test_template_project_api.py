from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from app.domain.orchestration.pipeline_definitions import DEFAULT_PIPELINE_VERSION
from app.infrastructure.template.catalog import ISNAD_TEMPLATE_ID, ISNAD_TEMPLATE_SCHEMA


def _client() -> TestClient:
    get_container.cache_clear()
    return TestClient(create_app())


def test_isnad_project_creation_applies_the_template_schema_in_one_request() -> None:
    client = _client()

    response = client.post(
        "/api/projects",
        json={
            "name": "Isnad Demo",
            "template_id": ISNAD_TEMPLATE_ID,
            "apply_template_schema": True,
        },
    )

    assert response.status_code == 201, response.text
    project = response.json()
    assert project["template_id"] == ISNAD_TEMPLATE_ID
    applied = project["template_schema"]
    assert applied["version_no"] == 1
    assert applied["status"] == "active"
    assert applied["pipeline_version"] == DEFAULT_PIPELINE_VERSION
    assert applied["segmentation_strategy"] == "isnad"

    schema = client.get(f"/api/projects/{project['project_id']}/active-schema").json()
    assert schema["schema_version_id"] == applied["schema_version_id"]
    assert schema["status"] == "active"
    assert {node_type["name"] for node_type in schema["node_types"]} == {"Narrator", "Hadith"}
    relation_types = {item["name"]: item for item in schema["relation_types"]}
    assert set(relation_types) == {"NARRATED_FROM", "TRANSMITS"}
    assert relation_types["NARRATED_FROM"]["merge_keys"] == [
        "hadith_ref",
        "chain_no",
        "position",
    ]
    assert [item["name"] for item in relation_types["NARRATED_FROM"]["properties"]] == [
        property_definition.name
        for property_definition in ISNAD_TEMPLATE_SCHEMA.relation_types[0].properties
    ]

    pipeline_definitions = client.get(
        f"/api/schema-versions/{applied['schema_version_id']}/pipeline-definitions"
    ).json()
    assert [item["version"] for item in pipeline_definitions] == [DEFAULT_PIPELINE_VERSION]
    assert "isnad" in pipeline_definitions[0]["description"]

    source_unit = client.post(
        f"/api/projects/{project['project_id']}/source-units",
        json={
            "schema_version_id": applied["schema_version_id"],
            "source_type": "hadith",
            "title": "muslim:1",
            "raw_content": "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ",
            "external_ref": "muslim:1",
        },
    )
    assert source_unit.status_code == 201, source_unit.text


def test_isnad_project_without_the_flag_keeps_the_schema_manual() -> None:
    client = _client()

    response = client.post(
        "/api/projects",
        json={"name": "Manual Isnad", "template_id": ISNAD_TEMPLATE_ID},
    )

    assert response.status_code == 201
    project = response.json()
    assert project["template_schema"] is None
    assert client.get(f"/api/projects/{project['project_id']}/schema-versions").json() == []


def test_template_without_blueprint_is_unchanged_by_the_flag() -> None:
    client = _client()

    response = client.post(
        "/api/projects",
        json={"name": "Blank Lab", "template_id": "blank", "apply_template_schema": True},
    )

    assert response.status_code == 201
    project = response.json()
    assert project["template_id"] == "blank"
    assert project["template_schema"] is None
    assert client.get(f"/api/projects/{project['project_id']}/schema-versions").json() == []


def test_templates_expose_their_schema_blueprint() -> None:
    client = _client()

    templates = {item["template_id"]: item for item in client.get("/api/templates").json()}

    assert templates["blank"]["schema_blueprint"] is None
    assert templates["story"]["schema_blueprint"] is None
    assert templates[ISNAD_TEMPLATE_ID]["schema_blueprint"] == {
        "node_types": ["Narrator", "Hadith"],
        "relation_types": ["NARRATED_FROM", "TRANSMITS"],
        "segmentation_strategy": "isnad",
    }
