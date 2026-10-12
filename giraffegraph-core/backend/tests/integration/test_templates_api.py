from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from app.infrastructure.template.catalog import ISNAD_TEMPLATE_SCHEMA


def test_templates_are_listed_and_project_creation_defaults_to_blank() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    templates_response = client.get("/api/templates")
    assert templates_response.status_code == 200
    templates = templates_response.json()
    assert [template["template_id"] for template in templates] == ["blank", "isnad", "story"]

    create_project_response = client.post(
        "/api/projects",
        json={
            "name": "Generic Graph Lab",
            "description": "Template defaults should be explicit.",
        },
    )
    assert create_project_response.status_code == 201
    project = create_project_response.json()
    assert project["template_id"] == "blank"


def test_project_creation_rejects_unknown_template() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    create_project_response = client.post(
        "/api/projects",
        json={
            "name": "Invalid Template Lab",
            "description": "Unknown templates must fail fast.",
            "template_id": "unknown-template",
        },
    )
    assert create_project_response.status_code == 422
    assert "Unknown template" in create_project_response.json()["detail"]


def test_isnad_template_schema_declares_narrator_chain_types() -> None:
    node_types = {node_type.name: node_type for node_type in ISNAD_TEMPLATE_SCHEMA.node_types}
    relation_types = {
        relation_type.name: relation_type
        for relation_type in ISNAD_TEMPLATE_SCHEMA.relation_types
    }

    assert ISNAD_TEMPLATE_SCHEMA.segmentation_strategy == "isnad"
    assert {name: node_type.merge_keys for name, node_type in node_types.items()} == {
        "Narrator": ["name"],
        "Hadith": ["hadith_ref"],
    }
    assert all(node_type.display_name for node_type in node_types.values())
    assert {
        name: (relation_type.from_type, relation_type.to_type, relation_type.merge_keys)
        for name, relation_type in relation_types.items()
    } == {
        "NARRATED_FROM": ("Narrator", "Narrator", ["hadith_ref", "chain_no", "position"]),
        "TRANSMITS": ("Narrator", "Hadith", []),
    }
    assert [
        property_definition.name
        for property_definition in relation_types["NARRATED_FROM"].properties
    ] == ["hadith_ref", "chain_no", "position", "sigha"]
    narrator_hints = " ".join(node_types["Narrator"].extraction_hints)
    for expected in ("verbatim", "definite article", "transmission verbs", "Prophet"):
        assert expected in narrator_hints
    technical_names = [
        *node_types,
        *relation_types,
        *(
            property_definition.name
            for definition in (*node_types.values(), *relation_types.values())
            for property_definition in definition.properties
        ),
    ]
    assert all(name.isascii() for name in technical_names)
