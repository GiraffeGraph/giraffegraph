from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.domain.orchestration.pipeline_definitions import DEFAULT_PIPELINE_VERSION
from app.domain.schema.identifiers import IDENTIFIER_PATTERN
from app.domain.shared.enums import ProcessingJobType


class ProjectCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    template_id: str | None = None
    apply_template_schema: bool = False


class SchemaVersionCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str
    version_no: int = Field(ge=1)
    notes: str | None = Field(default=None, max_length=1000)


class PropertyDefinitionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120, pattern=IDENTIFIER_PATTERN.pattern)
    data_type: str = Field(min_length=1, max_length=50)
    required: bool = False
    description: str | None = Field(default=None, max_length=500)
    default_value: str | None = None
    enum_values: list[str] = Field(default_factory=list)


class NodeTypeDefinitionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=80, pattern=IDENTIFIER_PATTERN.pattern)
    display_name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)
    is_core: bool = False
    merge_keys: list[str] = Field(default_factory=list)
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    aliases: list[str] = Field(default_factory=list)
    extraction_hints: list[str] = Field(default_factory=list)
    properties: list[PropertyDefinitionInput] = Field(default_factory=list)


class RelationTypeDefinitionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=80, pattern=IDENTIFIER_PATTERN.pattern)
    from_type: str = Field(min_length=1, max_length=80)
    to_type: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=500)
    directional: bool = True
    aliases: list[str] = Field(default_factory=list)
    extraction_hints: list[str] = Field(default_factory=list)
    required_properties: list[str] = Field(default_factory=list)
    merge_keys: list[str] = Field(default_factory=list)
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    properties: list[PropertyDefinitionInput] = Field(default_factory=list)


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateSchema:
    node_types: tuple[NodeTypeDefinitionInput, ...]
    relation_types: tuple[RelationTypeDefinitionInput, ...]
    segmentation_strategy: str


class SourceUnitCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str
    schema_version_id: str
    source_type: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    raw_content: str = Field(min_length=1)
    sequence_no: int | None = Field(default=None, ge=1)
    external_ref: str | None = Field(default=None, max_length=200)
    metadata_json: dict[str, str] = Field(default_factory=dict)


class SourceUnitBulkItemInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    external_ref: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
    ]
    title: str | None = Field(default=None, max_length=200)
    raw_content: str = Field(min_length=1)


class SourceUnitBulkCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str
    schema_version_id: str | None = None
    source_type: str = Field(default="document", min_length=1, max_length=80)
    items: list[SourceUnitBulkItemInput] = Field(min_length=1, max_length=1000)


class SourceUnitProcessInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str
    source_unit_ids: list[str] = Field(min_length=1, max_length=200)
    llm_provider: str | None = Field(default=None, max_length=80)
    llm_model: str | None = Field(default=None, max_length=120)
    segmentation_strategy: str | None = Field(default=None, max_length=50)
    pipeline_version: str = Field(default=DEFAULT_PIPELINE_VERSION, min_length=1, max_length=50)
    commit: bool = False


class ProcessingRunStartInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version_id: str
    source_unit_id: str
    pipeline_version: str = Field(min_length=1, max_length=50)
    llm_provider: str | None = Field(default=None, max_length=80)
    llm_model: str | None = Field(default=None, max_length=120)


class PipelineStepDefinitionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_type: ProcessingJobType
    chain_on_success: list[ProcessingJobType] = Field(default_factory=list)


class PipelineDefinitionCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version_id: str
    version: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    steps: list[PipelineStepDefinitionInput] = Field(min_length=1)


class SegmentGenerationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_unit_id: str
    strategy: str = Field(default="paragraphs", min_length=1, max_length=50)


class ExtractionExecutionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool = False


class ProcessingJobCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    job_type: ProcessingJobType
    dry_run: bool = False
    chain_on_success: list[ProcessingJobType] | None = None


class ProcessingJobProcessNextInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_type: ProcessingJobType | None = None
    run_id: str | None = None


class EvidenceRefInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment_id: str
    quote: str | None = None
    start_offset: int | None = Field(default=None, ge=0)
    end_offset: int | None = Field(default=None, ge=0)


class CandidateNodeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_type: str = Field(min_length=1, max_length=80)
    properties: dict[str, object] = Field(default_factory=dict)
    merge_key_payload: dict[str, object] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_refs: list[EvidenceRefInput] = Field(default_factory=list)


class CandidateRelationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relation_type: str = Field(min_length=1, max_length=80)
    from_candidate_ref: str
    to_candidate_ref: str
    properties: dict[str, object] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_refs: list[EvidenceRefInput] = Field(default_factory=list)


class ReviewDecisionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(min_length=1, max_length=20)
    reviewer_note: str | None = Field(default=None, max_length=1000)
    node_type: str | None = Field(default=None, max_length=80)
    relation_type: str | None = Field(default=None, max_length=80)
    from_candidate_ref: str | None = None
    to_candidate_ref: str | None = None
    properties: dict[str, object] = Field(default_factory=dict)
    merge_key_payload: dict[str, object] = Field(default_factory=dict)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
