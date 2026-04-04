from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared.enums import RunStatus, SourceUnitStatus


class SourceUnitCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version_id: str
    source_type: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    raw_content: str = Field(min_length=1)
    sequence_no: int | None = Field(default=None, ge=1)
    external_ref: str | None = Field(default=None, max_length=200)
    metadata_json: dict[str, str] = Field(default_factory=dict)


class SourceUnitSummaryResponse(BaseModel):
    source_unit_id: str
    project_id: str
    schema_version_id: str
    source_type: str
    title: str
    sequence_no: int | None
    external_ref: str | None
    metadata_json: dict[str, str]
    status: SourceUnitStatus
    created_at: datetime


class SourceUnitResponse(SourceUnitSummaryResponse):
    raw_content: str


class ProcessingRunStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version_id: str
    pipeline_version: str = Field(min_length=1, max_length=50)
    llm_provider: str | None = Field(default=None, max_length=80)
    llm_model: str | None = Field(default=None, max_length=120)


class ProcessingRunResponse(BaseModel):
    run_id: str
    project_id: str
    schema_version_id: str
    source_unit_id: str
    pipeline_version: str
    status: RunStatus
    llm_provider: str | None
    llm_model: str | None
    created_at: datetime
    started_at: datetime | None
    ended_at: datetime | None
