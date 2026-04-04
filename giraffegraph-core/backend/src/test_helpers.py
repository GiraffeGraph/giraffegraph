from typing import cast

from fastapi.testclient import TestClient

from app.domain.orchestration.pipeline_definitions import (
    DEFAULT_PIPELINE_VERSION,
    build_default_pipeline_steps,
)

DEFAULT_PIPELINE_STEPS = [
    {
        "job_type": step.job_type.value,
        "chain_on_success": [job_type.value for job_type in step.chain_on_success],
    }
    for step in build_default_pipeline_steps()
]


def create_pipeline_definition(
    client: TestClient,
    *,
    schema_id: str,
    version: str = DEFAULT_PIPELINE_VERSION,
    description: str = "Default test pipeline",
    steps: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    existing_response = client.get(
        f"/api/schema-versions/{schema_id}/pipeline-definitions/{version}"
    )
    if existing_response.status_code == 200:
        pipeline_definition = cast(dict[str, object], existing_response.json())
        if steps is not None:
            assert pipeline_definition["steps"] == steps
        assert pipeline_definition["version"] == version
        return pipeline_definition

    response = client.post(
        f"/api/schema-versions/{schema_id}/pipeline-definitions",
        json={
            "version": version,
            "description": description,
            "steps": steps or DEFAULT_PIPELINE_STEPS,
        },
    )
    assert response.status_code == 201
    pipeline_definition = cast(dict[str, object], response.json())
    assert pipeline_definition["version"] == version
    return pipeline_definition
