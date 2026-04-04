from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared.enums import ProcessingJobType


class PipelineStepDefinitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_type: ProcessingJobType
    chain_on_success: list[ProcessingJobType] = Field(default_factory=list)


class PipelineDefinitionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    steps: list[PipelineStepDefinitionRequest] = Field(min_length=1)


class PipelineStepDefinitionResponse(BaseModel):
    job_type: ProcessingJobType
    chain_on_success: list[ProcessingJobType]


class PipelineDefinitionResponse(BaseModel):
    pipeline_definition_id: str
    schema_version_id: str
    version: str
    description: str | None
    steps: list[PipelineStepDefinitionResponse]
    created_at: datetime
    updated_at: datetime
