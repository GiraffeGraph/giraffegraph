from app.domain.orchestration.pipeline_definitions import (
    PipelineDefinition,
    PipelineStepDefinition,
)
from app.interfaces.api.schemas.pipeline_definitions import (
    PipelineDefinitionResponse,
    PipelineStepDefinitionResponse,
)


def to_pipeline_definition_response(
    pipeline_definition: PipelineDefinition,
) -> PipelineDefinitionResponse:
    return PipelineDefinitionResponse(
        pipeline_definition_id=pipeline_definition.pipeline_definition_id,
        schema_version_id=pipeline_definition.schema_version_id,
        version=pipeline_definition.version,
        description=pipeline_definition.description,
        steps=[to_pipeline_step_definition_response(step) for step in pipeline_definition.steps],
        created_at=pipeline_definition.created_at,
        updated_at=pipeline_definition.updated_at,
    )


def to_pipeline_step_definition_response(
    step: PipelineStepDefinition,
) -> PipelineStepDefinitionResponse:
    return PipelineStepDefinitionResponse(
        job_type=step.job_type,
        chain_on_success=step.chain_on_success,
    )
