from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.domain.shared.enums import (
    CandidateStatus,
    ExtractionExecutionStatus,
    ProcessingJobStatus,
    ProcessingJobType,
    ProjectStatus,
    ReviewStatus,
    RunStatus,
    SchemaStatus,
    SourceUnitStatus,
)


class Base(DeclarativeBase):
    pass


class ProjectModel(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    template_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus, native_enum=False),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    schema_versions: Mapped[list["SchemaVersionModel"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    source_units: Mapped[list["SourceUnitModel"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    processing_runs: Mapped[list["ProcessingRunModel"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    graph_deltas: Mapped[list["GraphDeltaModel"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class SchemaVersionModel(Base):
    __tablename__ = "schema_versions"
    __table_args__ = (UniqueConstraint("project_id", "version_no", name="uq_schema_version"),)

    schema_version_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    version_no: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[SchemaStatus] = mapped_column(
        SQLEnum(SchemaStatus, native_enum=False),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[ProjectModel] = relationship(back_populates="schema_versions")
    node_types: Mapped[list["NodeTypeModel"]] = relationship(
        back_populates="schema_version",
        cascade="all, delete-orphan",
    )
    relation_types: Mapped[list["RelationTypeModel"]] = relationship(
        back_populates="schema_version",
        cascade="all, delete-orphan",
    )
    source_units: Mapped[list["SourceUnitModel"]] = relationship(
        back_populates="schema_version",
        cascade="all, delete-orphan",
    )
    processing_runs: Mapped[list["ProcessingRunModel"]] = relationship(
        back_populates="schema_version",
        cascade="all, delete-orphan",
    )
    pipeline_definitions: Mapped[list["PipelineDefinitionModel"]] = relationship(
        back_populates="schema_version",
        cascade="all, delete-orphan",
    )


class NodeTypeModel(Base):
    __tablename__ = "node_types"
    __table_args__ = (UniqueConstraint("schema_version_id", "name", name="uq_node_type_name"),)

    node_type_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    schema_version_id: Mapped[str] = mapped_column(
        ForeignKey("schema_versions.schema_version_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_core: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    merge_keys: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    confidence_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    aliases: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    extraction_hints: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    schema_version: Mapped[SchemaVersionModel] = relationship(back_populates="node_types")
    properties: Mapped[list["PropertyDefinitionModel"]] = relationship(
        back_populates="node_type",
        cascade="all, delete-orphan",
    )


class RelationTypeModel(Base):
    __tablename__ = "relation_types"
    __table_args__ = (UniqueConstraint("schema_version_id", "name", name="uq_relation_type_name"),)

    relation_type_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    schema_version_id: Mapped[str] = mapped_column(
        ForeignKey("schema_versions.schema_version_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    from_type: Mapped[str] = mapped_column(String(80), nullable=False)
    to_type: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    directional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    aliases: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    extraction_hints: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    required_properties: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    confidence_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    schema_version: Mapped[SchemaVersionModel] = relationship(back_populates="relation_types")
    properties: Mapped[list["PropertyDefinitionModel"]] = relationship(
        back_populates="relation_type",
        cascade="all, delete-orphan",
    )


class PropertyDefinitionModel(Base):
    __tablename__ = "property_definitions"

    property_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    schema_version_id: Mapped[str] = mapped_column(
        ForeignKey("schema_versions.schema_version_id"),
        nullable=False,
    )
    owner_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    owner_type_name: Mapped[str] = mapped_column(String(120), nullable=False)
    node_type_id: Mapped[str | None] = mapped_column(
        ForeignKey("node_types.node_type_id"),
        nullable=True,
    )
    relation_type_id: Mapped[str | None] = mapped_column(
        ForeignKey("relation_types.relation_type_id"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    enum_values: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    node_type: Mapped[NodeTypeModel | None] = relationship(back_populates="properties")
    relation_type: Mapped[RelationTypeModel | None] = relationship(back_populates="properties")


class SourceUnitModel(Base):
    __tablename__ = "source_units"

    source_unit_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    schema_version_id: Mapped[str] = mapped_column(
        ForeignKey("schema_versions.schema_version_id"),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    sequence_no: Mapped[int | None] = mapped_column(nullable=True)
    external_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    metadata_json: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[SourceUnitStatus] = mapped_column(
        SQLEnum(SourceUnitStatus, native_enum=False),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    project: Mapped[ProjectModel] = relationship(back_populates="source_units")
    schema_version: Mapped[SchemaVersionModel] = relationship(back_populates="source_units")
    segments: Mapped[list["SegmentModel"]] = relationship(
        back_populates="source_unit",
        cascade="all, delete-orphan",
    )
    processing_runs: Mapped[list["ProcessingRunModel"]] = relationship(
        back_populates="source_unit",
        cascade="all, delete-orphan",
    )


class SegmentModel(Base):
    __tablename__ = "segments"
    __table_args__ = (UniqueConstraint("source_unit_id", "segment_order", name="uq_segment_order"),)

    segment_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_unit_id: Mapped[str] = mapped_column(
        ForeignKey("source_units.source_unit_id"),
        nullable=False,
    )
    segment_order: Mapped[int] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False, default=dict)

    source_unit: Mapped[SourceUnitModel] = relationship(back_populates="segments")


class ProcessingRunModel(Base):
    __tablename__ = "processing_runs"

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    schema_version_id: Mapped[str] = mapped_column(
        ForeignKey("schema_versions.schema_version_id"),
        nullable=False,
    )
    source_unit_id: Mapped[str] = mapped_column(
        ForeignKey("source_units.source_unit_id"),
        nullable=False,
    )
    pipeline_version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[RunStatus] = mapped_column(
        SQLEnum(RunStatus, native_enum=False),
        nullable=False,
    )
    llm_provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[ProjectModel] = relationship(back_populates="processing_runs")
    schema_version: Mapped[SchemaVersionModel] = relationship(back_populates="processing_runs")
    source_unit: Mapped[SourceUnitModel] = relationship(back_populates="processing_runs")
    extraction_executions: Mapped[list["ExtractionExecutionModel"]] = relationship(
        back_populates="processing_run",
        cascade="all, delete-orphan",
    )
    processing_jobs: Mapped[list["ProcessingJobModel"]] = relationship(
        back_populates="processing_run",
        cascade="all, delete-orphan",
    )
    candidate_nodes: Mapped[list["CandidateNodeModel"]] = relationship(
        back_populates="processing_run",
        cascade="all, delete-orphan",
    )
    candidate_relations: Mapped[list["CandidateRelationModel"]] = relationship(
        back_populates="processing_run",
        cascade="all, delete-orphan",
    )
    validation_results: Mapped[list["ValidationResultModel"]] = relationship(
        back_populates="processing_run",
        cascade="all, delete-orphan",
    )
    review_items: Mapped[list["ReviewItemModel"]] = relationship(
        back_populates="processing_run",
        cascade="all, delete-orphan",
    )
    graph_delta: Mapped["GraphDeltaModel | None"] = relationship(
        back_populates="processing_run",
        cascade="all, delete-orphan",
        uselist=False,
    )


class PipelineDefinitionModel(Base):
    __tablename__ = "pipeline_definitions"
    __table_args__ = (
        UniqueConstraint("schema_version_id", "version", name="uq_pipeline_definition_version"),
    )

    pipeline_definition_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    schema_version_id: Mapped[str] = mapped_column(
        ForeignKey("schema_versions.schema_version_id"),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    schema_version: Mapped[SchemaVersionModel] = relationship(back_populates="pipeline_definitions")


class StructuredPromptModel(Base):
    __tablename__ = "structured_prompts"
    __table_args__ = (
        UniqueConstraint("prompt_key", "version", name="uq_structured_prompt_version"),
    )

    prompt_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prompt_key: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[str] = mapped_column(String(120), nullable=False)
    schema_name: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )


class ExtractionExecutionModel(Base):
    __tablename__ = "extraction_executions"

    execution_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(
        ForeignKey("processing_runs.run_id"),
        nullable=False,
    )
    dry_run: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[ExtractionExecutionStatus] = mapped_column(
        SQLEnum(ExtractionExecutionStatus, native_enum=False),
        nullable=False,
    )
    prompt_key: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    schema_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    provider_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    requested_llm_provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    requested_llm_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    resolved_llm_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    segment_count: Mapped[int] = mapped_column(nullable=False, default=0)
    suggested_node_count: Mapped[int] = mapped_column(nullable=False, default=0)
    suggested_relation_count: Mapped[int] = mapped_column(nullable=False, default=0)
    created_candidate_node_count: Mapped[int] = mapped_column(nullable=False, default=0)
    created_candidate_relation_count: Mapped[int] = mapped_column(nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    processing_run: Mapped[ProcessingRunModel] = relationship(
        back_populates="extraction_executions"
    )


class ProcessingJobModel(Base):
    __tablename__ = "processing_jobs"

    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    run_id: Mapped[str] = mapped_column(
        ForeignKey("processing_runs.run_id"),
        nullable=False,
    )
    source_unit_id: Mapped[str] = mapped_column(
        ForeignKey("source_units.source_unit_id"),
        nullable=False,
    )
    job_type: Mapped[ProcessingJobType] = mapped_column(
        SQLEnum(ProcessingJobType, native_enum=False),
        nullable=False,
    )
    status: Mapped[ProcessingJobStatus] = mapped_column(
        SQLEnum(ProcessingJobStatus, native_enum=False),
        nullable=False,
    )
    payload_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    output_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempt_count: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    processing_run: Mapped[ProcessingRunModel] = relationship(
        back_populates="processing_jobs"
    )


class CandidateNodeModel(Base):
    __tablename__ = "candidate_nodes"

    candidate_node_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("processing_runs.run_id"), nullable=False)
    node_type: Mapped[str] = mapped_column(String(80), nullable=False)
    properties_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    merge_key_payload: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence_refs_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    status: Mapped[CandidateStatus] = mapped_column(
        SQLEnum(CandidateStatus, native_enum=False),
        nullable=False,
    )

    processing_run: Mapped[ProcessingRunModel] = relationship(back_populates="candidate_nodes")


class CandidateRelationModel(Base):
    __tablename__ = "candidate_relations"

    candidate_relation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("processing_runs.run_id"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(80), nullable=False)
    from_candidate_ref: Mapped[str] = mapped_column(String(36), nullable=False)
    to_candidate_ref: Mapped[str] = mapped_column(String(36), nullable=False)
    properties_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence_refs_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    status: Mapped[CandidateStatus] = mapped_column(
        SQLEnum(CandidateStatus, native_enum=False),
        nullable=False,
    )

    processing_run: Mapped[ProcessingRunModel] = relationship(back_populates="candidate_relations")


class ValidationResultModel(Base):
    __tablename__ = "validation_results"

    validation_result_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("processing_runs.run_id"), nullable=False)
    candidate_ref: Mapped[str] = mapped_column(String(36), nullable=False)
    rule_code: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    processing_run: Mapped[ProcessingRunModel] = relationship(back_populates="validation_results")


class ReviewItemModel(Base):
    __tablename__ = "review_items"

    review_item_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("processing_runs.run_id"), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    item_ref: Mapped[str] = mapped_column(String(36), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(120), nullable=False)
    payload_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[ReviewStatus] = mapped_column(
        SQLEnum(ReviewStatus, native_enum=False),
        nullable=False,
    )
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    processing_run: Mapped[ProcessingRunModel] = relationship(back_populates="review_items")


class GraphDeltaModel(Base):
    __tablename__ = "graph_deltas"
    __table_args__ = (UniqueConstraint("run_id", name="uq_graph_delta_run"),)

    delta_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("processing_runs.run_id"), nullable=False)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    nodes_created: Mapped[int] = mapped_column(nullable=False, default=0)
    nodes_merged: Mapped[int] = mapped_column(nullable=False, default=0)
    relations_created: Mapped[int] = mapped_column(nullable=False, default=0)
    relations_merged: Mapped[int] = mapped_column(nullable=False, default=0)
    review_count: Mapped[int] = mapped_column(nullable=False, default=0)
    rejected_count: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    processing_run: Mapped[ProcessingRunModel] = relationship(back_populates="graph_delta")
    project: Mapped[ProjectModel] = relationship(back_populates="graph_deltas")
