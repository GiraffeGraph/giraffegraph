from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container


def test_templates_are_listed_and_project_creation_defaults_to_blank() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    templates_response = client.get("/api/templates")
    assert templates_response.status_code == 200
    templates = templates_response.json()
    assert [template["template_id"] for template in templates] == ["blank", "story"]

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
