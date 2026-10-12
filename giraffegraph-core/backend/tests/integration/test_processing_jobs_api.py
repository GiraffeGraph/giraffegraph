from copy import deepcopy
from typing import Any

from fastapi.testclient import TestClient

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from app.infrastructure.llm.provider_registry import StaticLLMProviderRegistry
from test_helpers import create_pipeline_definition


class StaticLLMProvider:
    def __init__(self, response: dict[str, Any]) -> None:
        self.provider_name = "static-test"
        self._response = response

    def generate_structured(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        del prompt, schema_name, payload, model
        return deepcopy(self._response)


def _prepare_extraction_run(
    client: TestClient,
    *,
    pipeline_steps: list[dict[str, Any]] | None = None,
    llm_provider: str | None = "static-test",
    llm_model: str | None = "gpt-test",
) -> tuple[str, str]:
    project = client.post(
        "/api/projects",
        json={
            "name": "Processing Jobs Lab",
            "description": "Queue baseline",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Queue schema"},
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
    create_pipeline_definition(
        client,
        schema_id=schema_id,
        steps=pipeline_steps,
        description="Queue defaults",
    )
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali appears in the room.",
            "sequence_no": 1,
        },
    ).json()
    source_id = source["source_unit_id"]

    run_request = {
        "schema_version_id": schema_id,
        "pipeline_version": "v1",
    }
    if llm_provider is not None:
        run_request["llm_provider"] = llm_provider
    if llm_model is not None:
        run_request["llm_model"] = llm_model

    run = client.post(
        f"/api/source-units/{source_id}/runs",
        json=run_request,
    ).json()
    return source_id, run["run_id"]


def _prepare_processing_job_project(client: TestClient) -> tuple[str, str]:
    project = client.post(
        "/api/projects",
        json={
            "name": "Processing Jobs Queue View Lab",
            "description": "Project-level processing jobs queue",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Queue view schema"},
    ).json()
    schema_id = schema["schema_version_id"]
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")
    return project_id, schema_id


def _create_source_and_run(
    client: TestClient,
    *,
    project_id: str,
    schema_id: str,
    sequence_no: int,
) -> tuple[str, str]:
    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": f"Episode {sequence_no}",
            "raw_content": f"EPISODE {sequence_no} RAW CONTENT",
            "sequence_no": sequence_no,
        },
    ).json()
    source_id = source["source_unit_id"]
    run = client.post(
        f"/api/source-units/{source_id}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    return source_id, run["run_id"]


def test_processing_job_queue_executes_extraction_job() -> None:
    get_container.cache_clear()
    container = get_container()
    client = TestClient(create_app())

    source_id, run_id = _prepare_extraction_run(client)
    segments = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()
    segment_id = segments[0]["segment_id"]

    provider = StaticLLMProvider(
        {
            "nodes": [
                {
                    "ref": "n_ali",
                    "node_type": "Character",
                    "properties": {"name": "Ali"},
                    "confidence": 0.91,
                    "evidence_refs": [{"segment_id": segment_id}],
                }
            ],
            "relations": [],
        }
    )
    registry = StaticLLMProviderRegistry(providers=[provider])
    container.extraction_management_service.provider_registry = registry
    container.processing_job_management_service.extraction_management_service.provider_registry = (
        registry
    )

    enqueue_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={"job_type": "extract_candidates", "chain_on_success": []},
    )
    assert enqueue_response.status_code == 201
    enqueued_job = enqueue_response.json()
    assert enqueued_job["status"] == "pending"
    assert enqueued_job["attempt_count"] == 0

    process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"job_type": "extract_candidates", "run_id": run_id},
    )
    assert process_response.status_code == 200
    process_payload = process_response.json()
    assert process_payload["processed"] is True
    processed_job = process_payload["job"]
    assert processed_job["job_id"] == enqueued_job["job_id"]
    assert processed_job["status"] == "succeeded"
    assert processed_job["attempt_count"] == 1
    assert processed_job["output_json"]["execution_id"]
    assert processed_job["output_json"]["created_candidate_node_count"] == 1

    list_jobs_response = client.get(f"/api/runs/{run_id}/processing-jobs")
    assert list_jobs_response.status_code == 200
    listed_jobs = list_jobs_response.json()
    assert len(listed_jobs) == 1
    assert listed_jobs[0]["status"] == "succeeded"

    candidate_nodes_response = client.get(f"/api/runs/{run_id}/candidate-nodes")
    assert candidate_nodes_response.status_code == 200
    assert len(candidate_nodes_response.json()) == 1

    extraction_executions_response = client.get(f"/api/runs/{run_id}/extraction-executions")
    assert extraction_executions_response.status_code == 200
    executions = extraction_executions_response.json()
    assert len(executions) == 1
    assert executions[0]["status"] == "succeeded"


def test_processing_job_queue_uses_pipeline_definition_defaults_for_chaining() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    source_id, run_id = _prepare_extraction_run(
        client,
        pipeline_steps=[
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
        llm_provider=None,
        llm_model=None,
    )
    client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    )

    enqueue_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={"job_type": "extract_candidates"},
    )
    assert enqueue_response.status_code == 201

    extraction_process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"job_type": "extract_candidates", "run_id": run_id},
    )
    assert extraction_process_response.status_code == 200
    extraction_job = extraction_process_response.json()["job"]
    assert extraction_job["status"] == "succeeded"
    assert extraction_job["output_json"]["chained_job_types"] == ["validate_run"]

    validate_process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"run_id": run_id},
    )
    assert validate_process_response.status_code == 200
    validate_job = validate_process_response.json()["job"]
    assert validate_job["job_type"] == "validate_run"
    assert validate_job["status"] == "succeeded"
    assert validate_job["output_json"]["chained_job_types"] == ["commit_run"]

    commit_process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"run_id": run_id},
    )
    assert commit_process_response.status_code == 200
    commit_job = commit_process_response.json()["job"]
    assert commit_job["job_type"] == "commit_run"
    assert commit_job["status"] == "succeeded"


def test_processing_job_queue_explicit_empty_chain_overrides_pipeline_definition_defaults() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    source_id, run_id = _prepare_extraction_run(
        client,
        pipeline_steps=[
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
        llm_provider=None,
        llm_model=None,
    )
    client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    )

    enqueue_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={"job_type": "extract_candidates", "chain_on_success": []},
    )
    assert enqueue_response.status_code == 201

    extraction_process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"job_type": "extract_candidates", "run_id": run_id},
    )
    assert extraction_process_response.status_code == 200
    extraction_job = extraction_process_response.json()["job"]
    assert extraction_job["status"] == "succeeded"
    assert "chained_job_types" not in extraction_job["output_json"]

    jobs_response = client.get(f"/api/runs/{run_id}/processing-jobs")
    assert jobs_response.status_code == 200
    jobs = jobs_response.json()
    assert len(jobs) == 1
    assert jobs[0]["job_type"] == "extract_candidates"


def test_processing_job_queue_chains_follow_up_jobs_after_extraction() -> None:
    get_container.cache_clear()
    container = get_container()
    client = TestClient(create_app())

    source_id, run_id = _prepare_extraction_run(client)
    segments = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()
    segment_id = segments[0]["segment_id"]

    provider = StaticLLMProvider(
        {
            "nodes": [
                {
                    "ref": "n_ali",
                    "node_type": "Character",
                    "properties": {"name": "Ali"},
                    "confidence": 0.91,
                    "evidence_refs": [{"segment_id": segment_id, "quote": "Ali appears"}],
                }
            ],
            "relations": [],
        }
    )
    registry = StaticLLMProviderRegistry(providers=[provider])
    container.extraction_management_service.provider_registry = registry
    container.processing_job_management_service.extraction_management_service.provider_registry = (
        registry
    )

    enqueue_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={
            "job_type": "extract_candidates",
            "chain_on_success": ["validate_run", "commit_run"],
        },
    )
    assert enqueue_response.status_code == 201

    extraction_process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"job_type": "extract_candidates", "run_id": run_id},
    )
    assert extraction_process_response.status_code == 200
    extraction_job = extraction_process_response.json()["job"]
    assert extraction_job["status"] == "succeeded"
    assert extraction_job["output_json"]["chained_job_types"] == [
        "validate_run",
        "commit_run",
    ]
    assert len(extraction_job["output_json"]["chained_job_ids"]) == 2

    jobs_after_extraction = client.get(f"/api/runs/{run_id}/processing-jobs").json()
    assert [job["job_type"] for job in jobs_after_extraction] == [
        "commit_run",
        "validate_run",
        "extract_candidates",
    ]
    pending_job_statuses = {
        job["job_type"]: job["status"]
        for job in jobs_after_extraction
        if job["job_type"] in {"validate_run", "commit_run"}
    }
    assert pending_job_statuses == {
        "validate_run": "pending",
        "commit_run": "pending",
    }

    validate_process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"run_id": run_id},
    )
    assert validate_process_response.status_code == 200
    validate_job = validate_process_response.json()["job"]
    assert validate_job["job_type"] == "validate_run"
    assert validate_job["status"] == "succeeded"

    commit_process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"run_id": run_id},
    )
    assert commit_process_response.status_code == 200
    commit_job = commit_process_response.json()["job"]
    assert commit_job["job_type"] == "commit_run"
    assert commit_job["status"] == "succeeded"
    assert commit_job["output_json"]["delta_id"]

    run_detail_response = client.get(f"/api/runs/{run_id}")
    assert run_detail_response.status_code == 200
    assert run_detail_response.json()["status"] == "completed"


def test_processing_job_queue_rejects_duplicate_active_job_for_run() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    _, run_id = _prepare_extraction_run(client)

    first_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={"job_type": "extract_candidates"},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={"job_type": "extract_candidates"},
    )
    assert second_response.status_code == 409
    assert "already has an active 'extract_candidates' job" in second_response.json()["detail"]


def test_processing_job_queue_does_not_claim_second_job_while_run_has_running_job() -> None:
    get_container.cache_clear()
    container = get_container()
    client = TestClient(create_app())

    _, run_id = _prepare_extraction_run(client)

    validate_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={"job_type": "validate_run"},
    )
    assert validate_response.status_code == 201

    commit_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={"job_type": "commit_run"},
    )
    assert commit_response.status_code == 201

    claimed_job = container.processing_job_management_service.processing_job_repository.claim_next(
        run_id=run_id
    )
    assert claimed_job is not None
    assert claimed_job.job_type.value == "validate_run"
    assert claimed_job.status.value == "running"

    process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"run_id": run_id},
    )
    assert process_response.status_code == 200
    process_payload = process_response.json()
    assert process_payload["processed"] is False

    jobs_response = client.get(f"/api/runs/{run_id}/processing-jobs")
    assert jobs_response.status_code == 200
    jobs = jobs_response.json()
    statuses = {job["job_type"]: job["status"] for job in jobs}
    assert statuses["validate_run"] == "running"
    assert statuses["commit_run"] == "pending"


def test_processing_job_queue_marks_job_failed_when_execution_fails() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    _, run_id = _prepare_extraction_run(client)

    enqueue_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={"job_type": "extract_candidates"},
    )
    assert enqueue_response.status_code == 201

    process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"job_type": "extract_candidates", "run_id": run_id},
    )
    assert process_response.status_code == 200
    process_payload = process_response.json()
    assert process_payload["processed"] is True
    assert process_payload["job"]["status"] == "failed"
    assert "Segments must be generated" in process_payload["job"]["error_message"]

    extraction_executions_response = client.get(f"/api/runs/{run_id}/extraction-executions")
    assert extraction_executions_response.status_code == 200
    executions = extraction_executions_response.json()
    assert len(executions) == 1
    assert executions[0]["status"] == "failed"


def test_processing_job_queue_executes_validation_job() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    source_id, run_id = _prepare_extraction_run(client)
    segments = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()
    segment_id = segments[0]["segment_id"]

    candidate_response = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segment_id}],
        },
    )
    assert candidate_response.status_code == 201

    enqueue_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={"job_type": "validate_run"},
    )
    assert enqueue_response.status_code == 201

    process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"job_type": "validate_run", "run_id": run_id},
    )
    assert process_response.status_code == 200
    process_payload = process_response.json()
    assert process_payload["processed"] is True
    assert process_payload["job"]["job_type"] == "validate_run"
    assert process_payload["job"]["status"] == "succeeded"
    assert process_payload["job"]["output_json"]["node_total"] == 1
    assert process_payload["job"]["output_json"]["node_validated"] == 1
    assert process_payload["job"]["output_json"]["validation_result_count"] >= 1

    candidate_nodes_response = client.get(f"/api/runs/{run_id}/candidate-nodes")
    assert candidate_nodes_response.status_code == 200
    candidate_nodes = candidate_nodes_response.json()
    assert len(candidate_nodes) == 1
    assert candidate_nodes[0]["status"] == "validated"


def test_processing_job_queue_executes_commit_job_after_validation_job() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    source_id, run_id = _prepare_extraction_run(client)
    segments = client.post(
        f"/api/source-units/{source_id}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()
    segment_id = segments[0]["segment_id"]

    candidate_response = client.post(
        f"/api/runs/{run_id}/candidate-nodes",
        json={
            "node_type": "Character",
            "properties": {"name": "Ali"},
            "merge_key_payload": {"name": "Ali"},
            "confidence": 0.95,
            "evidence_refs": [{"segment_id": segment_id}],
        },
    )
    assert candidate_response.status_code == 201

    validate_enqueue_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={"job_type": "validate_run"},
    )
    assert validate_enqueue_response.status_code == 201

    commit_enqueue_response = client.post(
        f"/api/runs/{run_id}/processing-jobs",
        json={"job_type": "commit_run"},
    )
    assert commit_enqueue_response.status_code == 201

    first_process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"run_id": run_id},
    )
    assert first_process_response.status_code == 200
    first_job = first_process_response.json()["job"]
    assert first_job["job_type"] == "validate_run"
    assert first_job["status"] == "succeeded"

    second_process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"run_id": run_id},
    )
    assert second_process_response.status_code == 200
    second_job = second_process_response.json()["job"]
    assert second_job["job_type"] == "commit_run"
    assert second_job["status"] == "succeeded"
    assert second_job["output_json"]["delta_id"]
    assert second_job["output_json"]["nodes_created"] == 1

    graph_delta_response = client.get(f"/api/runs/{run_id}/graph-delta")
    assert graph_delta_response.status_code == 200
    assert graph_delta_response.json()["delta_id"] == second_job["output_json"]["delta_id"]

    run_detail_response = client.get(f"/api/runs/{run_id}")
    assert run_detail_response.status_code == 200
    assert run_detail_response.json()["status"] == "completed"

    source_detail_response = client.get(f"/api/source-units/{source_id}")
    assert source_detail_response.status_code == 200
    assert source_detail_response.json()["status"] == "processed"


def test_project_processing_job_queue_groups_and_filters_jobs() -> None:
    get_container.cache_clear()
    client = TestClient(create_app())

    project_id, schema_id = _prepare_processing_job_project(client)
    _, pending_run_id = _create_source_and_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        sequence_no=1,
    )
    _, succeeded_run_id = _create_source_and_run(
        client,
        project_id=project_id,
        schema_id=schema_id,
        sequence_no=2,
    )

    pending_enqueue_response = client.post(
        f"/api/runs/{pending_run_id}/processing-jobs",
        json={"job_type": "extract_candidates", "chain_on_success": []},
    )
    assert pending_enqueue_response.status_code == 201

    succeeded_enqueue_response = client.post(
        f"/api/runs/{succeeded_run_id}/processing-jobs",
        json={"job_type": "validate_run", "chain_on_success": []},
    )
    assert succeeded_enqueue_response.status_code == 201

    process_response = client.post(
        "/api/processing-jobs/process-next",
        json={"run_id": succeeded_run_id},
    )
    assert process_response.status_code == 200
    assert process_response.json()["job"]["status"] == "succeeded"

    active_queue_response = client.get(
        f"/api/projects/{project_id}/processing-jobs",
        params={"status_filter": "active", "run_limit": 12},
    )
    assert active_queue_response.status_code == 200
    active_queue = active_queue_response.json()
    assert active_queue["status_filter"] == "active"
    assert active_queue["active_job_count"] == 1
    assert active_queue["failed_job_count"] == 0
    assert active_queue["succeeded_job_count"] == 1
    assert active_queue["total_job_count"] == 2
    assert active_queue["filtered_run_count"] == 1
    assert active_queue["returned_run_count"] == 1
    assert active_queue["returned_job_count"] == 1
    assert active_queue["run_entries"][0]["run"]["run_id"] == pending_run_id
    assert active_queue["run_entries"][0]["jobs"][0]["status"] == "pending"

    succeeded_queue_response = client.get(
        f"/api/projects/{project_id}/processing-jobs",
        params={"status_filter": "succeeded", "run_limit": 12},
    )
    assert succeeded_queue_response.status_code == 200
    succeeded_queue = succeeded_queue_response.json()
    assert succeeded_queue["filtered_run_count"] == 1
    assert succeeded_queue["run_entries"][0]["run"]["run_id"] == succeeded_run_id
    assert succeeded_queue["run_entries"][0]["jobs"][0]["job_type"] == "validate_run"
    assert succeeded_queue["run_entries"][0]["jobs"][0]["status"] == "succeeded"
