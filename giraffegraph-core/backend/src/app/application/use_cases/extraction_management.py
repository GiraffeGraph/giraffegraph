from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, TypeVar
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.application.dto.contracts import ExtractionExecutionInput
from app.application.errors import ConflictError, NotFoundError, RuleViolationError
from app.application.ports.llm_provider import LLMProvider, LLMProviderRegistry
from app.application.ports.prompt_catalog import (
    StructuredPromptCatalog,
    StructuredPromptDefinition,
)
from app.application.ports.repositories import (
    CandidateNodeRepository,
    CandidateRelationRepository,
    ExtractionExecutionRepository,
    ProcessingRunRepository,
    SchemaRepository,
    SegmentRepository,
    SourceUnitRepository,
)
from app.domain.extraction.entities import (
    CandidateNode,
    CandidateRelation,
    EvidenceRef,
    ExtractionExecution,
    ExtractionExecutionReport,
    SuggestedNode,
    SuggestedRelation,
)
from app.domain.ingestion.entities import ProcessingRun, Segment, SourceUnit
from app.domain.ingestion.lifecycle import (
    mark_run_failed,
    mark_run_started,
    reserve_source_for_run,
)
from app.domain.schema.entities import NodeTypeDefinition, RelationTypeDefinition
from app.domain.shared.enums import ExtractionExecutionStatus, RunStatus
from app.domain.shared.resolution import derive_merge_key_payload

EXTRACTION_PROMPT_KEY = "candidate_graph_extraction"
SchemaTypeDefinition = TypeVar(
    "SchemaTypeDefinition",
    NodeTypeDefinition,
    RelationTypeDefinition,
)


class ExtractionEvidenceContract(BaseModel):
    model_config = ConfigDict(extra="ignore")

    segment_id: str
    quote: str | None = None
    start_offset: int | None = Field(default=None, ge=0)
    end_offset: int | None = Field(default=None, ge=0)


class SuggestedNodeContract(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ref: str = Field(min_length=1, max_length=120)
    node_type: str = Field(min_length=1, max_length=80)
    properties: dict[str, object] = Field(default_factory=dict)
    merge_key_payload: dict[str, object] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_refs: list[ExtractionEvidenceContract] = Field(default_factory=list)


class SuggestedRelationContract(BaseModel):
    model_config = ConfigDict(extra="ignore")

    relation_type: str = Field(min_length=1, max_length=80)
    from_ref: str = Field(min_length=1, max_length=120)
    to_ref: str = Field(min_length=1, max_length=120)
    properties: dict[str, object] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_refs: list[ExtractionEvidenceContract] = Field(default_factory=list)


class StructuredExtractionContract(BaseModel):
    model_config = ConfigDict(extra="ignore")

    nodes: list[SuggestedNodeContract] = Field(default_factory=list)
    relations: list[SuggestedRelationContract] = Field(default_factory=list)


@dataclass(slots=True)
class ExtractionManagementService:
    processing_run_repository: ProcessingRunRepository
    source_unit_repository: SourceUnitRepository
    segment_repository: SegmentRepository
    schema_repository: SchemaRepository
    candidate_node_repository: CandidateNodeRepository
    candidate_relation_repository: CandidateRelationRepository
    extraction_execution_repository: ExtractionExecutionRepository
    provider_registry: LLMProviderRegistry
    prompt_catalog: StructuredPromptCatalog
    default_llm_provider: str
    default_llm_model: str | None = None
    default_extraction_prompt_version: str = "candidate_graph_extraction_v1"

    def extract_candidates(
        self,
        run_id: str,
        payload: ExtractionExecutionInput,
    ) -> ExtractionExecutionReport:
        run = self._require_run(run_id)
        self._ensure_run_is_mutable(run)
        source_unit = self._require_source_unit(run.source_unit_id)
        execution = ExtractionExecution(
            execution_id=str(uuid4()),
            run_id=run.run_id,
            dry_run=payload.dry_run,
            status=ExtractionExecutionStatus.RUNNING,
            prompt_key=EXTRACTION_PROMPT_KEY,
            requested_llm_provider=run.llm_provider,
            requested_llm_model=run.llm_model,
        )
        self.extraction_execution_repository.add(execution)
        run_marked_running = False

        try:
            segments = self.segment_repository.list_by_source_unit(source_unit.source_unit_id)
            execution.segment_count = len(segments)
            node_types = self.schema_repository.list_node_types(run.schema_version_id)
            relation_types = self.schema_repository.list_relation_types(run.schema_version_id)
            if not segments:
                raise RuleViolationError(
                    "Segments must be generated before candidate extraction can run."
                )

            if not payload.dry_run:
                self._ensure_run_has_no_existing_candidates(run_id)

            self._mark_run_running(run=run, source_unit=source_unit)
            run_marked_running = True

            llm_provider = self._require_llm_provider(run.llm_provider)
            execution.provider_name = llm_provider.provider_name
            resolved_llm_model = self._resolve_llm_model(run.llm_model)
            execution.resolved_llm_model = resolved_llm_model
            prompt_definition = self._require_prompt_definition()
            execution.prompt_version = prompt_definition.version
            execution.schema_name = prompt_definition.schema_name
            node_type_registry = self._build_node_type_registry(node_types)
            relation_type_registry = self._build_relation_type_registry(relation_types)
            prompt_payload = self._build_prompt_payload(
                run=run,
                source_unit=source_unit,
                segments=segments,
                node_types=node_types,
                relation_types=relation_types,
            )
            raw_output = llm_provider.generate_structured(
                prompt=prompt_definition.prompt_text,
                schema_name=prompt_definition.schema_name,
                payload=prompt_payload,
                model=resolved_llm_model,
            )
            suggested_nodes, suggested_relations = self._normalize_output(
                raw_output,
                source_unit_id=source_unit.source_unit_id,
                node_type_registry=node_type_registry,
                relation_type_registry=relation_type_registry,
            )
            execution.suggested_node_count = len(suggested_nodes)
            execution.suggested_relation_count = len(suggested_relations)

            created_candidate_node_ids: list[str] = []
            created_candidate_relation_ids: list[str] = []
            if not payload.dry_run:
                node_ref_map = {}
                for node_suggestion in suggested_nodes:
                    candidate_node = CandidateNode(
                        candidate_node_id=str(uuid4()),
                        run_id=run.run_id,
                        node_type=node_suggestion.node_type,
                        properties=node_suggestion.properties,
                        merge_key_payload=node_suggestion.merge_key_payload,
                        confidence=node_suggestion.confidence,
                        evidence_refs=node_suggestion.evidence_refs,
                    )
                    self.candidate_node_repository.add(candidate_node)
                    node_ref_map[node_suggestion.ref] = candidate_node.candidate_node_id
                    created_candidate_node_ids.append(candidate_node.candidate_node_id)

                for relation_suggestion in suggested_relations:
                    candidate_relation = CandidateRelation(
                        candidate_relation_id=str(uuid4()),
                        run_id=run.run_id,
                        relation_type=relation_suggestion.relation_type,
                        from_candidate_ref=node_ref_map[relation_suggestion.from_ref],
                        to_candidate_ref=node_ref_map[relation_suggestion.to_ref],
                        properties=relation_suggestion.properties,
                        confidence=relation_suggestion.confidence,
                        evidence_refs=relation_suggestion.evidence_refs,
                    )
                    self.candidate_relation_repository.add(candidate_relation)
                    created_candidate_relation_ids.append(
                        candidate_relation.candidate_relation_id
                    )

            execution.created_candidate_node_count = len(created_candidate_node_ids)
            execution.created_candidate_relation_count = len(created_candidate_relation_ids)
            self._mark_execution_succeeded(execution)

            return ExtractionExecutionReport(
                execution_id=execution.execution_id,
                run_id=run.run_id,
                dry_run=payload.dry_run,
                prompt_version=prompt_definition.version,
                schema_name=prompt_definition.schema_name,
                provider_name=llm_provider.provider_name,
                requested_llm_provider=run.llm_provider,
                requested_llm_model=run.llm_model,
                resolved_llm_model=resolved_llm_model,
                segment_count=len(segments),
                suggested_nodes=suggested_nodes,
                suggested_relations=suggested_relations,
                created_candidate_node_ids=created_candidate_node_ids,
                created_candidate_relation_ids=created_candidate_relation_ids,
                started_at=execution.started_at,
                completed_at=execution.completed_at or execution.started_at,
            )
        except Exception as exc:
            self._mark_execution_failed(execution, error_message=str(exc))
            if run_marked_running:
                self._mark_run_failed(run=run, source_unit=source_unit)
            raise

    def list_executions(self, run_id: str) -> list[ExtractionExecution]:
        self._require_run(run_id)
        return self.extraction_execution_repository.list_by_run(run_id)

    def _build_prompt_payload(
        self,
        *,
        run: ProcessingRun,
        source_unit: SourceUnit,
        segments: list[Segment],
        node_types: list[NodeTypeDefinition],
        relation_types: list[RelationTypeDefinition],
    ) -> dict[str, Any]:
        return {
            "run": {
                "run_id": run.run_id,
                "schema_version_id": run.schema_version_id,
                "pipeline_version": run.pipeline_version,
            },
            "source_unit": {
                "source_unit_id": source_unit.source_unit_id,
                "source_type": source_unit.source_type,
                "title": source_unit.title,
                "sequence_no": source_unit.sequence_no,
            },
            "schema": {
                "node_types": [
                    {
                        "name": node_type.name,
                        "description": node_type.description,
                        "merge_keys": node_type.merge_keys,
                        "confidence_threshold": node_type.confidence_threshold,
                        "aliases": node_type.aliases,
                        "extraction_hints": node_type.extraction_hints,
                        "properties": [
                            {
                                "name": property_definition.name,
                                "data_type": property_definition.data_type,
                                "required": property_definition.required,
                                "description": property_definition.description,
                                "default_value": property_definition.default_value,
                                "enum_values": property_definition.enum_values,
                            }
                            for property_definition in node_type.properties
                        ],
                    }
                    for node_type in node_types
                ],
                "relation_types": [
                    {
                        "name": relation_type.name,
                        "from_type": relation_type.from_type,
                        "to_type": relation_type.to_type,
                        "description": relation_type.description,
                        "aliases": relation_type.aliases,
                        "extraction_hints": relation_type.extraction_hints,
                        "required_properties": relation_type.required_properties,
                        "confidence_threshold": relation_type.confidence_threshold,
                        "properties": [
                            {
                                "name": property_definition.name,
                                "data_type": property_definition.data_type,
                                "required": property_definition.required,
                                "description": property_definition.description,
                                "default_value": property_definition.default_value,
                                "enum_values": property_definition.enum_values,
                            }
                            for property_definition in relation_type.properties
                        ],
                    }
                    for relation_type in relation_types
                ],
            },
            "segments": [
                {
                    "segment_id": segment.segment_id,
                    "segment_order": segment.segment_order,
                    "text": segment.text,
                }
                for segment in segments
            ],
        }

    def _normalize_output(
        self,
        raw_output: dict[str, Any],
        *,
        source_unit_id: str,
        node_type_registry: dict[str, NodeTypeDefinition],
        relation_type_registry: dict[str, RelationTypeDefinition],
    ) -> tuple[list[SuggestedNode], list[SuggestedRelation]]:
        try:
            parsed = StructuredExtractionContract.model_validate(raw_output)
        except ValidationError as exc:
            raise RuleViolationError(
                "Structured extraction output did not match the configured "
                "extraction prompt schema."
            ) from exc

        evidence_segment_ids = {
            segment.segment_id
            for segment in self.segment_repository.list_by_source_unit(source_unit_id)
        }
        node_ref_set: set[str] = set()
        node_types_by_ref: dict[str, NodeTypeDefinition] = {}
        suggested_nodes: list[SuggestedNode] = []
        for node_contract in parsed.nodes:
            if node_contract.ref in node_ref_set:
                raise RuleViolationError(
                    f"Structured extraction returned duplicate node ref '{node_contract.ref}'."
                )
            resolved_node_type = self._resolve_node_type(
                node_contract.node_type,
                node_type_registry=node_type_registry,
            )
            node_ref_set.add(node_contract.ref)
            node_types_by_ref[node_contract.ref] = resolved_node_type
            evidence_refs = [
                self._build_evidence_ref(
                    evidence_ref,
                    valid_segment_ids=evidence_segment_ids,
                )
                for evidence_ref in node_contract.evidence_refs
            ]
            suggested_nodes.append(
                SuggestedNode(
                    ref=node_contract.ref,
                    node_type=resolved_node_type.name,
                    properties=node_contract.properties,
                    merge_key_payload=derive_merge_key_payload(
                        node_type=resolved_node_type,
                        properties=node_contract.properties,
                        provided_merge_key_payload=node_contract.merge_key_payload,
                    ),
                    confidence=node_contract.confidence,
                    evidence_refs=evidence_refs,
                )
            )

        suggested_relations: list[SuggestedRelation] = []
        for relation_contract in parsed.relations:
            if (
                relation_contract.from_ref not in node_ref_set
                or relation_contract.to_ref not in node_ref_set
            ):
                raise RuleViolationError(
                    "Structured extraction returned a relation that references "
                    "unknown node refs."
                )
            resolved_relation_type = self._resolve_relation_type(
                relation_contract.relation_type,
                relation_type_registry=relation_type_registry,
            )
            from_node_type = node_types_by_ref[relation_contract.from_ref]
            to_node_type = node_types_by_ref[relation_contract.to_ref]
            if from_node_type.name.casefold() != resolved_relation_type.from_type.casefold():
                raise RuleViolationError(
                    "Structured extraction returned a relation whose from_ref does not match "
                    f"relation type '{resolved_relation_type.name}' from_type "
                    f"'{resolved_relation_type.from_type}'."
                )
            if to_node_type.name.casefold() != resolved_relation_type.to_type.casefold():
                raise RuleViolationError(
                    "Structured extraction returned a relation whose to_ref does not match "
                    f"relation type '{resolved_relation_type.name}' to_type "
                    f"'{resolved_relation_type.to_type}'."
                )
            evidence_refs = [
                self._build_evidence_ref(
                    evidence_ref,
                    valid_segment_ids=evidence_segment_ids,
                )
                for evidence_ref in relation_contract.evidence_refs
            ]
            suggested_relations.append(
                SuggestedRelation(
                    relation_type=resolved_relation_type.name,
                    from_ref=relation_contract.from_ref,
                    to_ref=relation_contract.to_ref,
                    properties=relation_contract.properties,
                    confidence=relation_contract.confidence,
                    evidence_refs=evidence_refs,
                )
            )

        return suggested_nodes, suggested_relations

    def _build_evidence_ref(
        self,
        evidence_ref: ExtractionEvidenceContract,
        *,
        valid_segment_ids: set[str],
    ) -> EvidenceRef:
        if evidence_ref.segment_id not in valid_segment_ids:
            raise RuleViolationError(
                f"Evidence segment '{evidence_ref.segment_id}' does not belong to the run source."
            )
        return EvidenceRef(
            segment_id=evidence_ref.segment_id,
            quote=evidence_ref.quote,
            start_offset=evidence_ref.start_offset,
            end_offset=evidence_ref.end_offset,
        )

    def _require_llm_provider(self, requested_provider_name: str | None) -> LLMProvider:
        resolved_provider_name = self._normalize_optional(requested_provider_name)
        if resolved_provider_name is None:
            resolved_provider_name = self._normalize_optional(self.default_llm_provider)
        if resolved_provider_name is None:
            raise RuleViolationError(
                "No LLM provider is configured for candidate extraction."
            )

        provider = self.provider_registry.get(resolved_provider_name)
        if provider is None:
            raise RuleViolationError(
                f"LLM provider '{resolved_provider_name}' is not configured "
                "for candidate extraction."
            )
        return provider

    def _resolve_llm_model(self, requested_model: str | None) -> str | None:
        return self._normalize_optional(requested_model) or self._normalize_optional(
            self.default_llm_model
        )

    def _require_prompt_definition(self) -> StructuredPromptDefinition:
        configured_version = self._normalize_optional(self.default_extraction_prompt_version)
        if configured_version is None:
            raise RuleViolationError(
                "No extraction prompt version is configured for candidate extraction."
            )

        prompt_definition = self.prompt_catalog.get(
            prompt_key=EXTRACTION_PROMPT_KEY,
            version=configured_version,
        )
        if prompt_definition is None:
            raise RuleViolationError(
                f"Extraction prompt version '{configured_version}' is not registered."
            )
        return prompt_definition

    def _build_node_type_registry(
        self,
        node_types: list[NodeTypeDefinition],
    ) -> dict[str, NodeTypeDefinition]:
        registry: dict[str, NodeTypeDefinition] = {}
        for node_type in node_types:
            self._register_type_lookup(
                registry=registry,
                kind="node type",
                lookup_value=node_type.name,
                resolved_name=node_type.name,
                definition=node_type,
            )
            for alias in node_type.aliases:
                self._register_type_lookup(
                    registry=registry,
                    kind="node type",
                    lookup_value=alias,
                    resolved_name=node_type.name,
                    definition=node_type,
                )
        return registry

    def _build_relation_type_registry(
        self,
        relation_types: list[RelationTypeDefinition],
    ) -> dict[str, RelationTypeDefinition]:
        registry: dict[str, RelationTypeDefinition] = {}
        for relation_type in relation_types:
            self._register_type_lookup(
                registry=registry,
                kind="relation type",
                lookup_value=relation_type.name,
                resolved_name=relation_type.name,
                definition=relation_type,
            )
            for alias in relation_type.aliases:
                self._register_type_lookup(
                    registry=registry,
                    kind="relation type",
                    lookup_value=alias,
                    resolved_name=relation_type.name,
                    definition=relation_type,
                )
        return registry

    def _register_type_lookup(
        self,
        *,
        registry: dict[str, SchemaTypeDefinition],
        kind: str,
        lookup_value: str,
        resolved_name: str,
        definition: SchemaTypeDefinition,
    ) -> None:
        normalized_lookup = lookup_value.strip().casefold()
        if normalized_lookup == "":
            return

        existing = registry.get(normalized_lookup)
        if existing is not None and existing.name != resolved_name:
            raise RuleViolationError(
                f"Schema contains ambiguous {kind} lookup '{lookup_value.strip()}'."
            )
        registry[normalized_lookup] = definition

    def _resolve_node_type(
        self,
        requested_type: str,
        *,
        node_type_registry: dict[str, NodeTypeDefinition],
    ) -> NodeTypeDefinition:
        normalized_requested_type = requested_type.strip().casefold()
        node_type = node_type_registry.get(normalized_requested_type)
        if node_type is None:
            raise RuleViolationError(
                f"Structured extraction returned undefined node type '{requested_type.strip()}'."
            )
        return node_type

    def _resolve_relation_type(
        self,
        requested_type: str,
        *,
        relation_type_registry: dict[str, RelationTypeDefinition],
    ) -> RelationTypeDefinition:
        normalized_requested_type = requested_type.strip().casefold()
        relation_type = relation_type_registry.get(normalized_requested_type)
        if relation_type is None:
            raise RuleViolationError(
                "Structured extraction returned undefined relation type "
                f"'{requested_type.strip()}'."
            )
        return relation_type

    def _normalize_optional(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_value = value.strip()
        if normalized_value == "":
            return None
        return normalized_value

    def _mark_execution_succeeded(self, execution: ExtractionExecution) -> None:
        execution.status = ExtractionExecutionStatus.SUCCEEDED
        execution.completed_at = datetime.now(UTC)
        self.extraction_execution_repository.save(execution)

    def _mark_execution_failed(
        self,
        execution: ExtractionExecution,
        *,
        error_message: str,
    ) -> None:
        execution.status = ExtractionExecutionStatus.FAILED
        execution.error_message = error_message
        execution.completed_at = datetime.now(UTC)
        self.extraction_execution_repository.save(execution)

    def _ensure_run_has_no_existing_candidates(self, run_id: str) -> None:
        if self.candidate_node_repository.list_by_run(run_id):
            raise ConflictError(
                f"Run '{run_id}' already has candidate nodes. Extraction cannot append yet."
            )
        if self.candidate_relation_repository.list_by_run(run_id):
            raise ConflictError(
                f"Run '{run_id}' already has candidate relations. Extraction cannot append yet."
            )

    def _require_run(self, run_id: str) -> ProcessingRun:
        run = self.processing_run_repository.get(run_id)
        if run is None:
            raise NotFoundError(f"Run '{run_id}' was not found.")
        return run

    def _ensure_run_is_mutable(self, run: ProcessingRun) -> None:
        if run.status == RunStatus.COMPLETED:
            raise RuleViolationError(
                f"Processing run '{run.run_id}' is already completed and cannot be changed."
            )

    def _mark_run_running(self, *, run: ProcessingRun, source_unit: SourceUnit) -> None:
        reserve_source_for_run(source_unit)
        mark_run_started(run)
        self.source_unit_repository.save(source_unit)
        self.processing_run_repository.save(run)

    def _mark_run_failed(self, *, run: ProcessingRun, source_unit: SourceUnit) -> None:
        mark_run_failed(run, source_unit)
        self.processing_run_repository.save(run)
        self.source_unit_repository.save(source_unit)

    def _require_source_unit(self, source_unit_id: str) -> SourceUnit:
        source_unit = self.source_unit_repository.get(source_unit_id)
        if source_unit is None:
            raise NotFoundError(f"Source unit '{source_unit_id}' was not found.")
        return source_unit
