import json
from copy import deepcopy
from typing import Any

from fastapi.testclient import TestClient

from app.application.ports.prompt_catalog import StructuredPromptDefinition
from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from app.infrastructure.llm.openai_provider import OpenAILLMProvider
from app.infrastructure.llm.prompt_catalog import (
    CANDIDATE_GRAPH_EXTRACTION_PROMPT_KEY,
    StaticStructuredPromptCatalog,
)
from app.infrastructure.llm.provider_registry import StaticLLMProviderRegistry
from test_helpers import create_pipeline_definition


class StaticLLMProvider:
    def __init__(
        self,
        response: dict[str, Any],
        *,
        provider_name: str = "static-test",
    ) -> None:
        self._response = response
        self.provider_name = provider_name

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


class RecordingLLMProvider(StaticLLMProvider):
    def __init__(
        self,
        response: dict[str, Any],
        *,
        provider_name: str = "static-test",
    ) -> None:
        super().__init__(response, provider_name=provider_name)
        self.last_payload: dict[str, Any] | None = None
        self.last_prompt: str | None = None
        self.last_schema_name: str | None = None
        self.last_model: str | None = None

    def generate_structured(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        self.last_prompt = prompt
        self.last_schema_name = schema_name
        self.last_model = model
        self.last_payload = deepcopy(payload)
        return deepcopy(self._response)


class RecordingOpenAITransport:
    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response
        self.last_url: str | None = None
        self.last_headers: dict[str, str] | None = None
        self.last_payload: dict[str, object] | None = None
        self.last_timeout_seconds: float | None = None

    def __call__(
        self,
        *,
        url: str,
        headers: dict[str, str],
        payload: dict[str, object],
        timeout_seconds: float,
    ) -> dict[str, Any]:
        self.last_url = url
        self.last_headers = deepcopy(headers)
        self.last_payload = deepcopy(payload)
        self.last_timeout_seconds = timeout_seconds
        return deepcopy(self.response)


def test_extraction_skeleton_supports_dry_run_and_persists_candidates() -> None:
    get_container.cache_clear()
    container = get_container()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Extraction Lab",
            "description": "LLM extraction skeleton",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Extraction schema"},
    ).json()
    schema_id = schema["schema_version_id"]

    client.post(
        f"/api/schema-versions/{schema_id}/node-types",
        json={
            "name": "Character",
            "display_name": "Character",
            "description": "Narrative actor",
            "merge_keys": ["name"],
            "aliases": ["person"],
            "properties": [{"name": "name", "data_type": "string", "required": True}],
        },
    )
    client.post(
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "KNOWS",
            "from_type": "Character",
            "to_type": "Character",
            "description": "Character knows another character",
            "aliases": ["acquainted_with"],
            "confidence_threshold": 0.7,
            "properties": [{"name": "context", "data_type": "string", "required": False}],
        },
    )
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali knows Veli.",
            "sequence_no": 1,
        },
    ).json()
    run = client.post(
        f"/api/source-units/{source['source_unit_id']}/runs",
        json={
            "schema_version_id": schema_id,
            "pipeline_version": "v1",
            "llm_provider": "static-test",
            "llm_model": "gpt-test",
        },
    ).json()
    segments = client.post(
        f"/api/source-units/{source['source_unit_id']}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()
    segment_id = segments[0]["segment_id"]
    provider = RecordingLLMProvider(
        {
            "nodes": [
                {
                    "ref": "n_ali",
                    "node_type": "person",
                    "properties": {"name": "Ali"},
                    "confidence": 0.92,
                    "evidence_refs": [{"segment_id": segment_id}],
                },
                {
                    "ref": "n_veli",
                    "node_type": "person",
                    "properties": {"name": "Veli"},
                    "confidence": 0.91,
                    "evidence_refs": [{"segment_id": segment_id}],
                },
            ],
            "relations": [
                {
                    "relation_type": "acquainted_with",
                    "from_ref": "n_ali",
                    "to_ref": "n_veli",
                    "properties": {"context": "street"},
                    "confidence": 0.75,
                    "evidence_refs": [{"segment_id": segment_id}],
                }
            ],
        }
    )
    container.extraction_management_service.provider_registry = StaticLLMProviderRegistry(
        providers=[provider]
    )

    dry_run_response = client.post(
        f"/api/runs/{run['run_id']}/extract-candidates",
        json={"dry_run": True},
    )
    assert dry_run_response.status_code == 200
    dry_run_report = dry_run_response.json()
    assert dry_run_report["execution_id"]
    assert dry_run_report["dry_run"] is True
    assert dry_run_report["provider_name"] == "static-test"
    assert dry_run_report["requested_llm_provider"] == "static-test"
    assert dry_run_report["requested_llm_model"] == "gpt-test"
    assert dry_run_report["resolved_llm_model"] == "gpt-test"
    assert dry_run_report["segment_count"] == 1
    assert len(dry_run_report["suggested_nodes"]) == 2
    assert len(dry_run_report["suggested_relations"]) == 1
    assert sorted(item["node_type"] for item in dry_run_report["suggested_nodes"]) == [
        "Character",
        "Character",
    ]
    assert sorted(
        item["merge_key_payload"]["name"] for item in dry_run_report["suggested_nodes"]
    ) == ["Ali", "Veli"]
    assert dry_run_report["suggested_relations"][0]["relation_type"] == "KNOWS"
    assert dry_run_report["created_candidate_node_ids"] == []
    assert dry_run_report["created_candidate_relation_ids"] == []
    assert dry_run_report["started_at"]

    run_detail_response = client.get(f"/api/runs/{run['run_id']}")
    assert run_detail_response.status_code == 200
    assert run_detail_response.json()["status"] == "running"
    assert run_detail_response.json()["started_at"] is not None

    source_detail_response = client.get(f"/api/source-units/{source['source_unit_id']}")
    assert source_detail_response.status_code == 200
    assert source_detail_response.json()["status"] == "processing"
    assert dry_run_report["completed_at"]
    assert client.get(f"/api/runs/{run['run_id']}/candidate-nodes").json() == []
    assert client.get(f"/api/runs/{run['run_id']}/candidate-relations").json() == []
    assert provider.last_payload is not None
    assert provider.last_payload["schema"]["node_types"][0]["aliases"] == ["person"]
    assert provider.last_payload["schema"]["node_types"][0]["properties"] == [
        {
            "name": "name",
            "data_type": "string",
            "required": True,
            "description": None,
            "default_value": None,
            "enum_values": [],
        }
    ]
    assert provider.last_payload["schema"]["relation_types"][0]["confidence_threshold"] == 0.7
    assert provider.last_schema_name == "candidate_graph_extraction_v1"
    assert provider.last_model == "gpt-test"

    extract_response = client.post(f"/api/runs/{run['run_id']}/extract-candidates", json={})
    assert extract_response.status_code == 200
    extract_report = extract_response.json()
    assert extract_report["execution_id"]
    assert extract_report["dry_run"] is False
    assert len(extract_report["created_candidate_node_ids"]) == 2
    assert len(extract_report["created_candidate_relation_ids"]) == 1

    candidate_nodes = client.get(f"/api/runs/{run['run_id']}/candidate-nodes").json()
    candidate_relations = client.get(f"/api/runs/{run['run_id']}/candidate-relations").json()
    assert len(candidate_nodes) == 2
    assert len(candidate_relations) == 1
    assert sorted(item["properties"]["name"] for item in candidate_nodes) == ["Ali", "Veli"]
    assert sorted(item["merge_key_payload"]["name"] for item in candidate_nodes) == [
        "Ali",
        "Veli",
    ]
    assert sorted(item["node_type"] for item in candidate_nodes) == ["Character", "Character"]
    assert candidate_relations[0]["relation_type"] == "KNOWS"

    execution_history_response = client.get(
        f"/api/runs/{run['run_id']}/extraction-executions"
    )
    assert execution_history_response.status_code == 200
    execution_history = execution_history_response.json()
    assert len(execution_history) == 2
    executions_by_id = {
        execution["execution_id"]: execution for execution in execution_history
    }
    latest_execution = executions_by_id[extract_report["execution_id"]]
    assert latest_execution["execution_id"] == extract_report["execution_id"]
    assert latest_execution["dry_run"] is False
    assert latest_execution["status"] == "succeeded"
    assert latest_execution["prompt_key"] == "candidate_graph_extraction"
    assert latest_execution["prompt_version"] == "candidate_graph_extraction_v1"
    assert latest_execution["provider_name"] == "static-test"
    assert latest_execution["requested_llm_provider"] == "static-test"
    assert latest_execution["requested_llm_model"] == "gpt-test"
    assert latest_execution["resolved_llm_model"] == "gpt-test"
    assert latest_execution["segment_count"] == 1
    assert latest_execution["suggested_node_count"] == 2
    assert latest_execution["suggested_relation_count"] == 1
    assert latest_execution["created_candidate_node_count"] == 2
    assert latest_execution["created_candidate_relation_count"] == 1
    assert latest_execution["error_message"] is None
    assert latest_execution["completed_at"]

    previous_execution = executions_by_id[dry_run_report["execution_id"]]
    assert previous_execution["execution_id"] == dry_run_report["execution_id"]
    assert previous_execution["dry_run"] is True
    assert previous_execution["status"] == "succeeded"
    assert previous_execution["created_candidate_node_count"] == 0
    assert previous_execution["created_candidate_relation_count"] == 0

    second_extract_response = client.post(
        f"/api/runs/{run['run_id']}/extract-candidates",
        json={},
    )
    assert second_extract_response.status_code == 409
    assert "cannot append yet" in second_extract_response.json()["detail"]


def test_extraction_rejects_unknown_relation_refs_from_provider() -> None:
    get_container.cache_clear()
    container = get_container()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Extraction Guard",
            "description": "Extraction output guard rails",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Extraction guard schema"},
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
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali knows Veli.",
            "sequence_no": 1,
        },
    ).json()
    run = client.post(
        f"/api/source-units/{source['source_unit_id']}/runs",
        json={
            "schema_version_id": schema_id,
            "pipeline_version": "v1",
            "llm_provider": "static-test",
        },
    ).json()
    segments = client.post(
        f"/api/source-units/{source['source_unit_id']}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()
    segment_id = segments[0]["segment_id"]
    container.extraction_management_service.provider_registry = StaticLLMProviderRegistry(
        providers=[
            StaticLLMProvider(
                {
                    "nodes": [
                        {
                            "ref": "n_ali",
                            "node_type": "Character",
                            "properties": {"name": "Ali"},
                            "merge_key_payload": {"name": "Ali"},
                            "confidence": 0.92,
                            "evidence_refs": [{"segment_id": segment_id}],
                        }
                    ],
                    "relations": [
                        {
                            "relation_type": "KNOWS",
                            "from_ref": "n_ali",
                            "to_ref": "n_missing",
                            "properties": {},
                            "confidence": 0.75,
                            "evidence_refs": [{"segment_id": segment_id}],
                        }
                    ],
                }
            )
        ]
    )

    extract_response = client.post(f"/api/runs/{run['run_id']}/extract-candidates", json={})
    assert extract_response.status_code == 422
    assert "unknown node refs" in extract_response.json()["detail"]
    assert client.get(f"/api/runs/{run['run_id']}/candidate-nodes").json() == []

    execution_history_response = client.get(
        f"/api/runs/{run['run_id']}/extraction-executions"
    )
    assert execution_history_response.status_code == 200
    execution_history = execution_history_response.json()
    assert len(execution_history) == 1
    failed_execution = execution_history[0]
    assert failed_execution["dry_run"] is False
    assert failed_execution["status"] == "failed"
    assert failed_execution["provider_name"] == "static-test"
    assert failed_execution["requested_llm_provider"] == "static-test"
    assert failed_execution["prompt_version"] == "candidate_graph_extraction_v1"
    assert failed_execution["segment_count"] == 1
    assert failed_execution["suggested_node_count"] == 0
    assert failed_execution["suggested_relation_count"] == 0
    assert failed_execution["created_candidate_node_count"] == 0
    assert failed_execution["created_candidate_relation_count"] == 0
    assert "unknown node refs" in failed_execution["error_message"]
    assert failed_execution["completed_at"]


def test_extraction_rejects_relation_endpoint_type_mismatch() -> None:
    get_container.cache_clear()
    container = get_container()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Extraction Endpoint Guard",
            "description": "Schema-aware relation endpoint validation",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Extraction endpoint schema"},
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
            "name": "Location",
            "display_name": "Location",
            "description": "Narrative place",
            "merge_keys": ["name"],
            "properties": [{"name": "name", "data_type": "string", "required": True}],
        },
    )
    client.post(
        f"/api/schema-versions/{schema_id}/relation-types",
        json={
            "name": "VISITS",
            "from_type": "Character",
            "to_type": "Location",
            "description": "Character visits a location",
        },
    )
    create_pipeline_definition(client, schema_id=schema_id)
    client.post(f"/api/projects/{project_id}/schema-versions/{schema_id}/activate")

    source = client.post(
        f"/api/projects/{project_id}/source-units",
        json={
            "schema_version_id": schema_id,
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali visited Ankara.",
            "sequence_no": 1,
        },
    ).json()
    run = client.post(
        f"/api/source-units/{source['source_unit_id']}/runs",
        json={
            "schema_version_id": schema_id,
            "pipeline_version": "v1",
            "llm_provider": "static-test",
        },
    ).json()
    segments = client.post(
        f"/api/source-units/{source['source_unit_id']}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()
    segment_id = segments[0]["segment_id"]
    container.extraction_management_service.provider_registry = StaticLLMProviderRegistry(
        providers=[
            StaticLLMProvider(
                {
                    "nodes": [
                        {
                            "ref": "n_ali",
                            "node_type": "Character",
                            "properties": {"name": "Ali"},
                            "confidence": 0.92,
                            "evidence_refs": [{"segment_id": segment_id}],
                        },
                        {
                            "ref": "n_ankara",
                            "node_type": "Location",
                            "properties": {"name": "Ankara"},
                            "confidence": 0.89,
                            "evidence_refs": [{"segment_id": segment_id}],
                        },
                    ],
                    "relations": [
                        {
                            "relation_type": "VISITS",
                            "from_ref": "n_ankara",
                            "to_ref": "n_ali",
                            "properties": {},
                            "confidence": 0.75,
                            "evidence_refs": [{"segment_id": segment_id}],
                        }
                    ],
                }
            )
        ]
    )

    extract_response = client.post(f"/api/runs/{run['run_id']}/extract-candidates", json={})
    assert extract_response.status_code == 422
    assert "from_ref does not match" in extract_response.json()["detail"]
    assert client.get(f"/api/runs/{run['run_id']}/candidate-nodes").json() == []
    assert client.get(f"/api/runs/{run['run_id']}/candidate-relations").json() == []


def test_extraction_uses_default_provider_and_prompt_version() -> None:
    get_container.cache_clear()
    container = get_container()
    provider = RecordingLLMProvider(
        {
            "nodes": [],
            "relations": [],
        }
    )
    container.extraction_management_service.provider_registry = StaticLLMProviderRegistry(
        providers=[provider]
    )
    container.extraction_management_service.default_llm_provider = "static-test"
    container.extraction_management_service.default_llm_model = "gpt-default"
    container.extraction_management_service.prompt_catalog = StaticStructuredPromptCatalog(
        prompts=[
            StructuredPromptDefinition(
                prompt_key=CANDIDATE_GRAPH_EXTRACTION_PROMPT_KEY,
                version="candidate_graph_extraction_v1",
                schema_name="candidate_graph_extraction_v1",
                prompt_text="v1 prompt",
            ),
            StructuredPromptDefinition(
                prompt_key=CANDIDATE_GRAPH_EXTRACTION_PROMPT_KEY,
                version="candidate_graph_extraction_v2",
                schema_name="candidate_graph_extraction_v2",
                prompt_text="v2 prompt",
            ),
        ]
    )
    container.extraction_management_service.default_extraction_prompt_version = (
        "candidate_graph_extraction_v2"
    )
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Extraction Runtime Config",
            "description": "Default provider and prompt version resolution",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Extraction runtime schema"},
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
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali appears.",
            "sequence_no": 1,
        },
    ).json()
    run = client.post(
        f"/api/source-units/{source['source_unit_id']}/runs",
        json={"schema_version_id": schema_id, "pipeline_version": "v1"},
    ).json()
    client.post(
        f"/api/source-units/{source['source_unit_id']}/segments/generate",
        json={"strategy": "paragraphs"},
    )

    extract_response = client.post(
        f"/api/runs/{run['run_id']}/extract-candidates",
        json={"dry_run": True},
    )
    assert extract_response.status_code == 200
    report = extract_response.json()
    assert report["provider_name"] == "static-test"
    assert report["requested_llm_provider"] is None
    assert report["requested_llm_model"] is None
    assert report["resolved_llm_model"] == "gpt-default"
    assert report["prompt_version"] == "candidate_graph_extraction_v2"
    assert report["schema_name"] == "candidate_graph_extraction_v2"
    assert provider.last_prompt == "v2 prompt"
    assert provider.last_schema_name == "candidate_graph_extraction_v2"
    assert provider.last_model == "gpt-default"


def test_extraction_rejects_unconfigured_provider() -> None:
    get_container.cache_clear()
    container = get_container()
    container.extraction_management_service.provider_registry = StaticLLMProviderRegistry(
        providers=[StaticLLMProvider({"nodes": [], "relations": []}, provider_name="noop")]
    )
    container.extraction_management_service.default_llm_provider = "noop"
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "Extraction Provider Guard",
            "description": "Configured provider validation",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "Provider guard schema"},
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
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali appears.",
            "sequence_no": 1,
        },
    ).json()
    run = client.post(
        f"/api/source-units/{source['source_unit_id']}/runs",
        json={
            "schema_version_id": schema_id,
            "pipeline_version": "v1",
            "llm_provider": "openai",
        },
    ).json()
    client.post(
        f"/api/source-units/{source['source_unit_id']}/segments/generate",
        json={"strategy": "paragraphs"},
    )

    extract_response = client.post(
        f"/api/runs/{run['run_id']}/extract-candidates",
        json={"dry_run": True},
    )
    assert extract_response.status_code == 422
    assert "not configured for candidate extraction" in extract_response.json()["detail"]


def test_extraction_supports_openai_provider_adapter() -> None:
    get_container.cache_clear()
    container = get_container()
    client = TestClient(create_app())

    project = client.post(
        "/api/projects",
        json={
            "name": "OpenAI Provider Lab",
            "description": "OpenAI adapter extraction path",
            "template_id": "story",
        },
    ).json()
    project_id = project["project_id"]

    schema = client.post(
        f"/api/projects/{project_id}/schema-versions",
        json={"version_no": 1, "notes": "OpenAI adapter schema"},
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
            "source_type": "episode_transcript",
            "title": "Episode 1",
            "raw_content": "Ali appears.",
            "sequence_no": 1,
        },
    ).json()
    run = client.post(
        f"/api/source-units/{source['source_unit_id']}/runs",
        json={
            "schema_version_id": schema_id,
            "pipeline_version": "v1",
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini",
        },
    ).json()
    segments = client.post(
        f"/api/source-units/{source['source_unit_id']}/segments/generate",
        json={"strategy": "paragraphs"},
    ).json()
    segment_id = segments[0]["segment_id"]

    transport = RecordingOpenAITransport(
        {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "nodes": [
                                    {
                                        "ref": "n_ali",
                                        "node_type": "Character",
                                        "properties": {"name": "Ali"},
                                        "confidence": 0.93,
                                        "evidence_refs": [{"segment_id": segment_id}],
                                    }
                                ],
                                "relations": [],
                            }
                        )
                    }
                }
            ]
        }
    )
    container.extraction_management_service.provider_registry = StaticLLMProviderRegistry(
        providers=[
            OpenAILLMProvider(
                api_key="test-key",
                base_url="https://api.openai.com/v1",
                timeout_seconds=12.0,
                transport=transport,
            )
        ]
    )

    extract_response = client.post(
        f"/api/runs/{run['run_id']}/extract-candidates",
        json={"dry_run": True},
    )
    assert extract_response.status_code == 200
    report = extract_response.json()
    assert report["provider_name"] == "openai"
    assert report["resolved_llm_model"] == "gpt-4o-mini"
    assert len(report["suggested_nodes"]) == 1
    assert report["suggested_nodes"][0]["properties"]["name"] == "Ali"

    assert transport.last_url == "https://api.openai.com/v1/chat/completions"
    assert transport.last_headers == {
        "Authorization": "Bearer test-key",
        "Content-Type": "application/json",
    }
    assert transport.last_timeout_seconds == 12.0
    assert transport.last_payload is not None
    assert transport.last_payload["model"] == "gpt-4o-mini"
    assert transport.last_payload["response_format"] == {"type": "json_object"}
    messages = transport.last_payload["messages"]
    assert isinstance(messages, list)
    assert messages[0]["role"] == "system"
    user_payload = json.loads(messages[1]["content"])
    assert user_payload["schema_name"] == "candidate_graph_extraction_v1"
    assert user_payload["payload"]["segments"][0]["segment_id"] == segment_id
