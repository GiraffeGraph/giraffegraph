from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container


def test_source_unit_and_processing_run_flow() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project_response = client.post(
        "/api/projects",
        json={
            "name": "Ingestion Lab",
            "description": "Source unit and run orchestration",
            "template_id": "story",
        },
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["project_id"]

    schema_v1_response = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Ready for ingestion"},
    )
    assert schema_v1_response.status_code == 201
    schema_v1_id = schema_v1_response.json()["schema_version_id"]

    draft_ingest_response = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_v1_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "INT. HOUSE - NIGHT",
            "sequence_no": 1,
        },
    )
    assert draft_ingest_response.status_code == 422

    activate_response = client.post(
        f"/api/projects/{project_id}/schema-versions/{schema_v1_id}/activate"
    )
    assert activate_response.status_code == 200

    source_two_response = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_v1_id,
            "source_type": "episode_transcript",
            "title": "Episode 2",
            "raw_content": "SECOND EPISODE RAW CONTENT",
            "sequence_no": 2,
            "metadata_json": {"season": "1"},
        },
    )
    assert source_two_response.status_code == 201

    source_one_response = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_v1_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "FIRST EPISODE RAW CONTENT",
            "sequence_no": 1,
            "external_ref": "ep-1",
        },
    )
    assert source_one_response.status_code == 201
    source_one = source_one_response.json()
    source_one_id = source_one["source_unit_id"]
    assert source_one["status"] == "ready"
    assert source_one["raw_content"] == "FIRST EPISODE RAW CONTENT"

    list_sources_response = client.get(f"/api/projects/{project_id}/source-units")
    assert list_sources_response.status_code == 200
    source_units = list_sources_response.json()
    assert [item["sequence_no"] for item in source_units] == [1, 2]
    assert "raw_content" not in source_units[0]

    get_source_response = client.get(f"/api/source-units/{source_one_id}")
    assert get_source_response.status_code == 200
    assert get_source_response.json()["external_ref"] == "ep-1"

    schema_v2_response = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 2, "notes": "Draft rework"},
    )
    assert schema_v2_response.status_code == 201
    schema_v2_id = schema_v2_response.json()["schema_version_id"]

    draft_run_response = client.post(
        f"/api/source-units/{source_one_id}/runs",
        json={
            "schema_version_id": schema_v2_id,
            "pipeline_version": "v1",
        },
    )
    assert draft_run_response.status_code == 422

    activate_schema_v2_response = client.post(
        f"/api/projects/{project_id}/schema-versions/{schema_v2_id}/activate"
    )
    assert activate_schema_v2_response.status_code == 200

    mismatched_schema_run_response = client.post(
        f"/api/source-units/{source_one_id}/runs",
        json={
            "schema_version_id": schema_v2_id,
            "pipeline_version": "v1",
        },
    )
    assert mismatched_schema_run_response.status_code == 422
    assert "same schema version as their source unit" in mismatched_schema_run_response.json()[
        "detail"
    ]

    source_three_response = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_v2_id,
            "source_type": "episode_transcript",
            "title": "Episode 3",
            "raw_content": "THIRD EPISODE RAW CONTENT",
            "sequence_no": 3,
        },
    )
    assert source_three_response.status_code == 201
    source_three_id = source_three_response.json()["source_unit_id"]

    missing_pipeline_run_response = client.post(
        f"/api/source-units/{source_three_id}/runs",
        json={
            "schema_version_id": schema_v2_id,
            "pipeline_version": "v2",
        },
    )
    assert missing_pipeline_run_response.status_code == 422
    assert "require a pipeline definition" in missing_pipeline_run_response.json()["detail"]

    create_run_response = client.post(
        f"/api/source-units/{source_one_id}/runs",
        json={
            "schema_version_id": schema_v1_id,
            "pipeline_version": "v1",
            "llm_provider": "openai",
            "llm_model": "gpt-test",
        },
    )
    assert create_run_response.status_code == 201
    run = create_run_response.json()
    run_id = run["run_id"]
    assert run["project_id"] == project_id
    assert run["source_unit_id"] == source_one_id
    assert run["status"] == "pending"
    assert run["created_at"] is not None

    source_detail_response = client.get(f"/api/source-units/{source_one_id}")
    assert source_detail_response.status_code == 200
    assert source_detail_response.json()["status"] == "processing"

    parallel_run_response = client.post(
        f"/api/source-units/{source_one_id}/runs",
        json={
            "schema_version_id": schema_v1_id,
            "pipeline_version": "v1",
        },
    )
    assert parallel_run_response.status_code == 422

    list_runs_response = client.get(f"/api/projects/{project_id}/runs")
    assert list_runs_response.status_code == 200
    runs = list_runs_response.json()
    assert len(runs) == 1
    assert runs[0]["run_id"] == run_id

    get_run_response = client.get(f"/api/runs/{run_id}")
    assert get_run_response.status_code == 200
    assert get_run_response.json()["pipeline_version"] == "v1"
