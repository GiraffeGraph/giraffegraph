from typing import Any

from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from app.infrastructure.template.catalog import ISNAD_TEMPLATE_ID

FIRST_CHAIN = "حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ ، حَدَّثَنَا لَيْثٌ"
SECOND_CHAIN = "حَدَّثَنَا مُحَمَّدُ بْنُ رُمْحٍ ، أَخْبَرَنَا اللَّيْثُ ، عَنِ ابْنِ شِهَابٍ"
TAHWIL_SOURCE = f"{FIRST_CHAIN} . ح ، {SECOND_CHAIN}"
PROVIDER = "rule_based_isnad"


def _isnad_project(client: TestClient) -> str:
    response = client.post(
        "/api/projects",
        json={
            "name": "Bulk Isnad",
            "template_id": ISNAD_TEMPLATE_ID,
            "apply_template_schema": True,
        },
    )
    assert response.status_code == 201, response.text
    project_id: str = response.json()["project_id"]
    return project_id


def _client() -> TestClient:
    get_container.cache_clear()
    return TestClient(create_app())


def _bulk(client: TestClient, project_id: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    response = client.post(
        f"/api/projects/{project_id}/source-units/bulk",
        json={"source_type": "hadith", "items": items},
    )
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    return body


def test_bulk_ingest_creates_one_source_unit_per_item_on_the_active_schema() -> None:
    client = _client()
    project_id = _isnad_project(client)

    body = _bulk(
        client,
        project_id,
        [
            {"external_ref": "muslim:1", "title": "Muslim 1", "raw_content": FIRST_CHAIN},
            {"external_ref": "muslim:2", "raw_content": SECOND_CHAIN},
        ],
    )

    active_schema = client.get(f"/api/projects/{project_id}/active-schema").json()
    assert body["schema_version_id"] == active_schema["schema_version_id"]
    assert (body["created_count"], body["duplicate_count"]) == (2, 0)
    assert [item["status"] for item in body["results"]] == ["created", "created"]
    source_units = client.get(f"/api/projects/{project_id}/source-units").json()
    assert [
        (unit["external_ref"], unit["title"], unit["source_type"], unit["status"])
        for unit in source_units
    ] == [
        ("muslim:1", "Muslim 1", "hadith", "ready"),
        ("muslim:2", "muslim:2", "hadith", "ready"),
    ]
    assert {unit["source_unit_id"] for unit in source_units} == {
        item["source_unit_id"] for item in body["results"]
    }


def test_bulk_ingest_reports_duplicates_per_item_without_failing_the_request() -> None:
    client = _client()
    project_id = _isnad_project(client)
    _bulk(client, project_id, [{"external_ref": "muslim:1", "raw_content": FIRST_CHAIN}])

    body = _bulk(
        client,
        project_id,
        [
            {"external_ref": "muslim:1", "raw_content": FIRST_CHAIN},
            {"external_ref": "muslim:2", "raw_content": SECOND_CHAIN},
            {"external_ref": " muslim:2 ", "raw_content": SECOND_CHAIN},
        ],
    )

    assert (body["created_count"], body["duplicate_count"]) == (1, 2)
    assert [
        (item["index"], item["external_ref"], item["status"]) for item in body["results"]
    ] == [
        (0, "muslim:1", "duplicate"),
        (1, "muslim:2", "created"),
        (2, "muslim:2", "duplicate"),
    ]
    assert body["results"][0]["source_unit_id"] is None
    assert "muslim:1" in body["results"][0]["detail"]
    assert "already exists" in body["results"][0]["detail"]
    assert "more than once" in body["results"][2]["detail"]
    assert len(client.get(f"/api/projects/{project_id}/source-units").json()) == 2


def test_bulk_ingest_requires_an_active_schema() -> None:
    client = _client()
    project_id = client.post("/api/projects", json={"name": "No Schema"}).json()["project_id"]

    response = client.post(
        f"/api/projects/{project_id}/source-units/bulk",
        json={"items": [{"external_ref": "a:1", "raw_content": "text"}]},
    )

    assert response.status_code == 422
    assert "active schema" in response.json()["detail"]


def test_process_action_produces_validated_candidates_for_each_unit() -> None:
    client = _client()
    project_id = _isnad_project(client)
    created = _bulk(
        client,
        project_id,
        [
            {"external_ref": "muslim:1", "raw_content": TAHWIL_SOURCE},
            {"external_ref": "muslim:2", "raw_content": SECOND_CHAIN},
        ],
    )
    source_unit_ids = [item["source_unit_id"] for item in created["results"]]

    response = client.post(
        f"/api/projects/{project_id}/source-units/process",
        json={"source_unit_ids": source_unit_ids, "llm_provider": PROVIDER},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["segmentation_strategy"] == "isnad"
    assert body["llm_provider"] == PROVIDER
    assert (body["processed_count"], body["failed_count"], body["committed_count"]) == (2, 0, 0)
    assert [
        (
            item["external_ref"],
            item["status"],
            item["segment_count"],
            item["candidate_node_count"],
            item["candidate_relation_count"],
            item["validated_node_count"],
            item["validated_relation_count"],
            item["open_review_count"],
        )
        for item in body["results"]
    ] == [
        ("muslim:1", "validated", 2, 5, 3, 5, 3, 0),
        ("muslim:2", "validated", 1, 3, 2, 3, 2, 0),
    ]
    for item in body["results"]:
        run = client.get(f"/api/runs/{item['run_id']}").json()
        assert run["llm_provider"] == PROVIDER
        assert run["status"] == "running"
        candidate_nodes = client.get(f"/api/runs/{item['run_id']}/candidate-nodes").json()
        assert len(candidate_nodes) == item["candidate_node_count"]
        assert {node["status"] for node in candidate_nodes} == {"validated"}
        segments = client.get(f"/api/source-units/{item['source_unit_id']}/segments").json()
        assert {segment["metadata_json"]["strategy"] for segment in segments} == {"isnad"}


def test_process_action_commits_clean_runs_when_asked() -> None:
    client = _client()
    project_id = _isnad_project(client)
    created = _bulk(
        client,
        project_id,
        [{"external_ref": "muslim:1", "raw_content": TAHWIL_SOURCE}],
    )

    body = client.post(
        f"/api/projects/{project_id}/source-units/process",
        json={
            "source_unit_ids": [created["results"][0]["source_unit_id"]],
            "llm_provider": PROVIDER,
            "commit": True,
        },
    ).json()

    assert body["committed_count"] == 1
    result = body["results"][0]
    assert result["status"] == "committed"
    assert client.get(f"/api/runs/{result['run_id']}").json()["status"] == "completed"
    overview = client.get(f"/api/projects/{project_id}/graph/overview").json()
    assert (overview["node_count"], overview["relation_count"]) == (5, 3)


def test_process_action_reports_failures_per_unit() -> None:
    client = _client()
    project_id = _isnad_project(client)
    created = _bulk(
        client,
        project_id,
        [{"external_ref": "muslim:1", "raw_content": FIRST_CHAIN}],
    )
    source_unit_id = created["results"][0]["source_unit_id"]
    payload = {"source_unit_ids": [source_unit_id, "missing-unit"], "llm_provider": PROVIDER}

    first = client.post(f"/api/projects/{project_id}/source-units/process", json=payload).json()
    second = client.post(f"/api/projects/{project_id}/source-units/process", json=payload).json()

    assert [item["status"] for item in first["results"]] == ["validated", "failed"]
    assert "missing-unit" in first["results"][1]["detail"]
    assert (first["processed_count"], first["failed_count"]) == (1, 1)
    assert [item["status"] for item in second["results"]] == ["failed", "failed"]
    assert "already processing" in second["results"][0]["detail"]
    assert second["results"][0]["run_id"] is None


def test_process_action_rejects_an_unknown_provider_before_starting_runs() -> None:
    client = _client()
    project_id = _isnad_project(client)
    created = _bulk(
        client,
        project_id,
        [{"external_ref": "muslim:1", "raw_content": FIRST_CHAIN}],
    )

    response = client.post(
        f"/api/projects/{project_id}/source-units/process",
        json={
            "source_unit_ids": [created["results"][0]["source_unit_id"]],
            "llm_provider": "no-such-provider",
        },
    )

    assert response.status_code == 422
    assert "no-such-provider" in response.json()["detail"]
    assert client.get(f"/api/projects/{project_id}/runs").json() == []
    assert client.get(f"/api/projects/{project_id}/source-units").json()[0]["status"] == "ready"
