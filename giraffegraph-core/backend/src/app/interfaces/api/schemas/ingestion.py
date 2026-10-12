from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.domain.orchestration.pipeline_definitions import DEFAULT_PIPELINE_VERSION
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


class SourceUnitBulkItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    external_ref: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
    ]
    title: str | None = Field(default=None, max_length=200)
    raw_content: str = Field(min_length=1)


class SourceUnitBulkCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version_id: str | None = None
    source_type: str = Field(default="document", min_length=1, max_length=80)
    items: list[SourceUnitBulkItemRequest] = Field(min_length=1, max_length=1000)


class SourceUnitBulkItemResponse(BaseModel):
    index: int
    external_ref: str
    status: str
    source_unit_id: str | None
    detail: str | None


class SourceUnitBulkCreateResponse(BaseModel):
    project_id: str
    schema_version_id: str
    created_count: int
    duplicate_count: int
    results: list[SourceUnitBulkItemResponse]


class SourceUnitProcessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_unit_ids: list[str] = Field(min_length=1, max_length=200)
    llm_provider: str | None = Field(default=None, max_length=80)
    llm_model: str | None = Field(default=None, max_length=120)
    segmentation_strategy: str | None = Field(default=None, max_length=50)
    pipeline_version: str = Field(default=DEFAULT_PIPELINE_VERSION, min_length=1, max_length=50)
    commit: bool = False


class SourceUnitProcessResultResponse(BaseModel):
    source_unit_id: str
    external_ref: str | None
    status: str
    run_id: str | None
    segment_count: int
    candidate_node_count: int
    candidate_relation_count: int
    validated_node_count: int
    validated_relation_count: int
    open_review_count: int
    failed_call_count: int
    detail: str | None


class SourceUnitProcessResponse(BaseModel):
    project_id: str
    segmentation_strategy: str
    llm_provider: str
    llm_model: str | None
    processed_count: int
    failed_count: int
    committed_count: int
    results: list[SourceUnitProcessResultResponse]
