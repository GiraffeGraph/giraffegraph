from collections.abc import Sequence
from dataclasses import dataclass
from re import split
from uuid import uuid4

from app.application.dto.contracts import (
    CandidateNodeInput,
    CandidateRelationInput,
    EvidenceRefInput,
    SegmentGenerationInput,
)
from app.application.errors import NotFoundError, RuleViolationError
from app.application.ports.repositories import (
    CandidateNodeRepository,
    CandidateRelationRepository,
    CanonicalGraphRepository,
    ProcessingRunRepository,
    ReviewItemRepository,
    SchemaRepository,
    SegmentRepository,
    SourceUnitRepository,
    ValidationResultRepository,
)
from app.domain.extraction.entities import CandidateNode, CandidateRelation, EvidenceRef
from app.domain.ingestion.entities import ProcessingRun, Segment, SourceUnit
from app.domain.ingestion.lifecycle import mark_run_started, reserve_source_for_run
from app.domain.review.entities import ReviewItem
from app.domain.schema.entities import NodeTypeDefinition, RelationTypeDefinition
from app.domain.shared.enums import CandidateStatus, RunStatus
from app.domain.shared.resolution import (
    build_candidate_node_resolution_key,
    build_candidate_relation_resolution_key,
    build_canonical_merge_key,
    candidate_node_identity_key,
    derive_merge_key_payload,
    is_missing_value,
)
from app.domain.validation.entities import ValidationResult


@dataclass(slots=True)
class RunValidationReport:
    run: ProcessingRun
    candidate_nodes: list[CandidateNode]
    candidate_relations: list[CandidateRelation]
    validation_results: list[ValidationResult]


@dataclass(slots=True)
class PipelineManagementService:
    source_unit_repository: SourceUnitRepository
    segment_repository: SegmentRepository
    processing_run_repository: ProcessingRunRepository
    schema_repository: SchemaRepository
    candidate_node_repository: CandidateNodeRepository
    candidate_relation_repository: CandidateRelationRepository
    validation_result_repository: ValidationResultRepository
    review_item_repository: ReviewItemRepository
    canonical_graph_repository: CanonicalGraphRepository

    def generate_segments(self, payload: SegmentGenerationInput) -> list[Segment]:
        source_unit = self._require_source_unit(payload.source_unit_id)
        strategy = payload.strategy.strip().casefold()
        if strategy != "paragraphs":
            raise RuleViolationError("Only the 'paragraphs' segmentation strategy is supported.")

        segment_texts = self._split_into_segments(source_unit.raw_content)
        segments = [
            Segment(
                segment_id=str(uuid4()),
                source_unit_id=source_unit.source_unit_id,
                segment_order=index,
                text=text,
                metadata_json={"strategy": strategy},
            )
            for index, text in enumerate(segment_texts, start=1)
        ]
        self.segment_repository.replace_for_source_unit(source_unit.source_unit_id, segments)
        return self.segment_repository.list_by_source_unit(source_unit.source_unit_id)

    def list_segments(self, source_unit_id: str) -> list[Segment]:
        self._require_source_unit(source_unit_id)
        return self.segment_repository.list_by_source_unit(source_unit_id)

    def add_candidate_node(self, run_id: str, payload: CandidateNodeInput) -> CandidateNode:
        run = self._require_run(run_id)
        self._ensure_run_is_mutable(run)
        self._mark_run_running(run)
        self._ensure_evidence_refs_belong_to_source_unit(
            source_unit_id=run.source_unit_id,
            evidence_refs=payload.evidence_refs,
        )

        candidate_node = CandidateNode(
            candidate_node_id=str(uuid4()),
            run_id=run_id,
            node_type=payload.node_type.strip(),
            properties=payload.properties,
            merge_key_payload=payload.merge_key_payload,
            confidence=payload.confidence,
            evidence_refs=[self._build_evidence_ref(item) for item in payload.evidence_refs],
        )
        self.candidate_node_repository.add(candidate_node)
        return candidate_node

    def list_candidate_nodes(self, run_id: str) -> list[CandidateNode]:
        self._require_run(run_id)
        return self.candidate_node_repository.list_by_run(run_id)

    def add_candidate_relation(
        self,
        run_id: str,
        payload: CandidateRelationInput,
    ) -> CandidateRelation:
        run = self._require_run(run_id)
        self._ensure_run_is_mutable(run)
        self._mark_run_running(run)
        self._ensure_evidence_refs_belong_to_source_unit(
            source_unit_id=run.source_unit_id,
            evidence_refs=payload.evidence_refs,
        )
        self._require_candidate_node_in_run(
            candidate_node_id=payload.from_candidate_ref,
            run_id=run_id,
        )
        self._require_candidate_node_in_run(
            candidate_node_id=payload.to_candidate_ref,
            run_id=run_id,
        )

        candidate_relation = CandidateRelation(
            candidate_relation_id=str(uuid4()),
            run_id=run_id,
            relation_type=payload.relation_type.strip(),
            from_candidate_ref=payload.from_candidate_ref,
            to_candidate_ref=payload.to_candidate_ref,
            properties=payload.properties,
            confidence=payload.confidence,
            evidence_refs=[self._build_evidence_ref(item) for item in payload.evidence_refs],
        )
        self.candidate_relation_repository.add(candidate_relation)
        return candidate_relation

    def list_candidate_relations(self, run_id: str) -> list[CandidateRelation]:
        self._require_run(run_id)
        return self.candidate_relation_repository.list_by_run(run_id)

    def validate_run(self, run_id: str) -> RunValidationReport:
        run = self._require_run(run_id)
        self._ensure_run_is_mutable(run)
        self._mark_run_running(run)
        node_type_map = {
            node_type.name.casefold(): node_type
            for node_type in self.schema_repository.list_node_types(run.schema_version_id)
        }
        relation_type_map = {
            relation_type.name.casefold(): relation_type
            for relation_type in self.schema_repository.list_relation_types(run.schema_version_id)
        }

        candidate_nodes = self.candidate_node_repository.list_by_run(run_id)
        candidate_relations = self.candidate_relation_repository.list_by_run(run_id)
        candidate_node_map = {
            candidate_node.candidate_node_id: candidate_node
            for candidate_node in candidate_nodes
        }

        validation_results: list[ValidationResult] = []
        for candidate_node in candidate_nodes:
            validation_results.extend(
                self._validate_candidate_node(
                    candidate_node=candidate_node,
                    node_type_map=node_type_map,
                )
            )
            self.candidate_node_repository.save(candidate_node)

        for candidate_relation in candidate_relations:
            validation_results.extend(
                self._validate_candidate_relation(
                    candidate_relation=candidate_relation,
                    relation_type_map=relation_type_map,
                    candidate_node_map=candidate_node_map,
                )
            )
        validation_results.extend(
            self._apply_duplicate_resolution(
                candidate_nodes=candidate_nodes,
                candidate_relations=candidate_relations,
                candidate_node_map=candidate_node_map,
            )
        )
        validation_results.extend(
            self._annotate_canonical_matches(
                project_id=run.project_id,
                candidate_nodes=candidate_nodes,
                candidate_relations=candidate_relations,
                candidate_node_map=candidate_node_map,
            )
        )

        for candidate_node in candidate_nodes:
            self.candidate_node_repository.save(candidate_node)
        for candidate_relation in candidate_relations:
            self.candidate_relation_repository.save(candidate_relation)

        self.validation_result_repository.replace_for_run(run_id, validation_results)
        self.review_item_repository.replace_for_run(
            run_id,
            self._build_review_items(
                candidate_nodes=candidate_nodes,
                candidate_relations=candidate_relations,
                validation_results=validation_results,
            ),
        )
        return RunValidationReport(
            run=run,
            candidate_nodes=self.candidate_node_repository.list_by_run(run_id),
            candidate_relations=self.candidate_relation_repository.list_by_run(run_id),
            validation_results=self.validation_result_repository.list_by_run(run_id),
        )

    def list_validation_results(self, run_id: str) -> list[ValidationResult]:
        self._require_run(run_id)
        return self.validation_result_repository.list_by_run(run_id)

    def list_review_items(self, run_id: str) -> list[ReviewItem]:
        self._require_run(run_id)
        return self.review_item_repository.list_by_run(run_id)

    def resolve_duplicates(self, run_id: str) -> RunValidationReport:
        return self.validate_run(run_id)

    def _validate_candidate_node(
        self,
        *,
        candidate_node: CandidateNode,
        node_type_map: dict[str, NodeTypeDefinition],
    ) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        node_type = node_type_map.get(candidate_node.node_type.casefold())
        if node_type is None:
            candidate_node.status = CandidateStatus.REJECTED
            results.append(
                self._build_validation_result(
                    run_id=candidate_node.run_id,
                    candidate_ref=candidate_node.candidate_node_id,
                    rule_code="node_type_exists",
                    severity="error",
                    result="failed",
                    message=f"Node type '{candidate_node.node_type}' is not defined in schema.",
                )
            )
            return results

        candidate_node.node_type = node_type.name
        candidate_node.merge_key_payload = derive_merge_key_payload(
            node_type=node_type,
            properties=candidate_node.properties,
            provided_merge_key_payload=candidate_node.merge_key_payload,
        )
        missing_required = [
            property_definition.name
            for property_definition in node_type.properties
            if property_definition.required
            and is_missing_value(candidate_node.properties.get(property_definition.name))
        ]
        missing_merge_keys = [
            merge_key
            for merge_key in node_type.merge_keys
            if is_missing_value(candidate_node.merge_key_payload.get(merge_key))
        ]

        for property_name in missing_required:
            results.append(
                self._build_validation_result(
                    run_id=candidate_node.run_id,
                    candidate_ref=candidate_node.candidate_node_id,
                    rule_code="required_node_property",
                    severity="error",
                    result="failed",
                    message=f"Missing required node property '{property_name}'.",
                )
            )

        for merge_key in missing_merge_keys:
            results.append(
                self._build_validation_result(
                    run_id=candidate_node.run_id,
                    candidate_ref=candidate_node.candidate_node_id,
                    rule_code="node_merge_key",
                    severity="error",
                    result="failed",
                    message=f"Missing merge key '{merge_key}' for candidate node.",
                )
            )

        if results:
            candidate_node.status = CandidateStatus.REJECTED
            return results

        if candidate_node.confidence < node_type.confidence_threshold:
            candidate_node.status = CandidateStatus.REVIEW
            results.append(
                self._build_validation_result(
                    run_id=candidate_node.run_id,
                    candidate_ref=candidate_node.candidate_node_id,
                    rule_code="node_confidence_threshold",
                    severity="warning",
                    result="review",
                    message=(
                        "Candidate node confidence is below the baseline review threshold "
                        f"({node_type.confidence_threshold:.2f})."
                    ),
                )
            )
            return results

        candidate_node.status = CandidateStatus.VALIDATED
        results.append(
            self._build_validation_result(
                run_id=candidate_node.run_id,
                candidate_ref=candidate_node.candidate_node_id,
                rule_code="candidate_node_valid",
                severity="info",
                result="passed",
                message="Candidate node passed validation.",
            )
        )
        return results

    def _validate_candidate_relation(
        self,
        *,
        candidate_relation: CandidateRelation,
        relation_type_map: dict[str, RelationTypeDefinition],
        candidate_node_map: dict[str, CandidateNode],
    ) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        relation_type = relation_type_map.get(candidate_relation.relation_type.casefold())
        if relation_type is None:
            candidate_relation.status = CandidateStatus.REJECTED
            results.append(
                self._build_validation_result(
                    run_id=candidate_relation.run_id,
                    candidate_ref=candidate_relation.candidate_relation_id,
                    rule_code="relation_type_exists",
                    severity="error",
                    result="failed",
                    message=(
                        f"Relation type '{candidate_relation.relation_type}' "
                        "is not defined in schema."
                    ),
                )
            )
            return results

        candidate_relation.relation_type = relation_type.name
        from_candidate = candidate_node_map.get(candidate_relation.from_candidate_ref)
        to_candidate = candidate_node_map.get(candidate_relation.to_candidate_ref)
        if from_candidate is None or to_candidate is None:
            candidate_relation.status = CandidateStatus.REJECTED
            results.append(
                self._build_validation_result(
                    run_id=candidate_relation.run_id,
                    candidate_ref=candidate_relation.candidate_relation_id,
                    rule_code="relation_candidate_refs",
                    severity="error",
                    result="failed",
                    message="Relation references candidate nodes that do not exist in the run.",
                )
            )
            return results

        if from_candidate.node_type.casefold() != relation_type.from_type.casefold():
            results.append(
                self._build_validation_result(
                    run_id=candidate_relation.run_id,
                    candidate_ref=candidate_relation.candidate_relation_id,
                    rule_code="relation_from_type",
                    severity="error",
                    result="failed",
                    message=(
                        f"Relation expects from_type '{relation_type.from_type}' but received "
                        f"'{from_candidate.node_type}'."
                    ),
                )
            )

        if to_candidate.node_type.casefold() != relation_type.to_type.casefold():
            results.append(
                self._build_validation_result(
                    run_id=candidate_relation.run_id,
                    candidate_ref=candidate_relation.candidate_relation_id,
                    rule_code="relation_to_type",
                    severity="error",
                    result="failed",
                    message=(
                        f"Relation expects to_type '{relation_type.to_type}' but received "
                        f"'{to_candidate.node_type}'."
                    ),
                )
            )

        required_properties = {
            *relation_type.required_properties,
            *[
                property_definition.name
                for property_definition in relation_type.properties
                if property_definition.required
            ],
        }
        for property_name in sorted(required_properties):
            if is_missing_value(candidate_relation.properties.get(property_name)):
                results.append(
                    self._build_validation_result(
                        run_id=candidate_relation.run_id,
                        candidate_ref=candidate_relation.candidate_relation_id,
                        rule_code="required_relation_property",
                        severity="error",
                        result="failed",
                        message=f"Missing required relation property '{property_name}'.",
                    )
                )

        if any(result.severity == "error" for result in results):
            candidate_relation.status = CandidateStatus.REJECTED
            return results

        if (
            from_candidate.status == CandidateStatus.REJECTED
            or to_candidate.status == CandidateStatus.REJECTED
        ):
            candidate_relation.status = CandidateStatus.REJECTED
            results.append(
                self._build_validation_result(
                    run_id=candidate_relation.run_id,
                    candidate_ref=candidate_relation.candidate_relation_id,
                    rule_code="relation_dependency_rejected",
                    severity="error",
                    result="failed",
                    message="Relation depends on candidate nodes that failed validation.",
                )
            )
            return results

        if (
            from_candidate.status == CandidateStatus.REVIEW
            or to_candidate.status == CandidateStatus.REVIEW
            or candidate_relation.confidence < relation_type.confidence_threshold
        ):
            candidate_relation.status = CandidateStatus.REVIEW
            if (
                from_candidate.status == CandidateStatus.REVIEW
                or to_candidate.status == CandidateStatus.REVIEW
            ):
                results.append(
                    self._build_validation_result(
                        run_id=candidate_relation.run_id,
                        candidate_ref=candidate_relation.candidate_relation_id,
                        rule_code="relation_dependency_review",
                        severity="warning",
                        result="review",
                        message="Relation depends on candidate nodes that require review.",
                    )
                )
            if candidate_relation.confidence < relation_type.confidence_threshold:
                results.append(
                    self._build_validation_result(
                        run_id=candidate_relation.run_id,
                        candidate_ref=candidate_relation.candidate_relation_id,
                        rule_code="relation_confidence_threshold",
                        severity="warning",
                        result="review",
                        message=(
                            "Relation confidence is below the schema threshold "
                            f"({relation_type.confidence_threshold:.2f})."
                        ),
                    )
                )
            return results

        candidate_relation.status = CandidateStatus.VALIDATED
        results.append(
            self._build_validation_result(
                run_id=candidate_relation.run_id,
                candidate_ref=candidate_relation.candidate_relation_id,
                rule_code="candidate_relation_valid",
                severity="info",
                result="passed",
                message="Candidate relation passed validation.",
            )
        )
        return results

    def _require_source_unit(self, source_unit_id: str) -> SourceUnit:
        source_unit = self.source_unit_repository.get(source_unit_id)
        if source_unit is None:
            raise NotFoundError(f"Source unit '{source_unit_id}' was not found.")
        return source_unit

    def _require_run(self, run_id: str) -> ProcessingRun:
        run = self.processing_run_repository.get(run_id)
        if run is None:
            raise NotFoundError(f"Processing run '{run_id}' was not found.")
        return run

    def _ensure_run_is_mutable(self, run: ProcessingRun) -> None:
        if run.status == RunStatus.COMPLETED:
            raise RuleViolationError(
                f"Processing run '{run.run_id}' is already completed and cannot be changed."
            )

    def _mark_run_running(self, run: ProcessingRun) -> None:
        source_unit = self._require_source_unit(run.source_unit_id)
        reserve_source_for_run(source_unit)
        mark_run_started(run)
        self.source_unit_repository.save(source_unit)
        self.processing_run_repository.save(run)

    def _require_candidate_node_in_run(
        self,
        *,
        candidate_node_id: str,
        run_id: str,
    ) -> CandidateNode:
        candidate_node = self.candidate_node_repository.get(candidate_node_id)
        if candidate_node is None or candidate_node.run_id != run_id:
            raise NotFoundError(
                f"Candidate node '{candidate_node_id}' was not found in run '{run_id}'."
            )
        return candidate_node

    def _ensure_evidence_refs_belong_to_source_unit(
        self,
        *,
        source_unit_id: str,
        evidence_refs: Sequence[EvidenceRefInput],
    ) -> None:
        segment_ids = {
            segment.segment_id
            for segment in self.segment_repository.list_by_source_unit(source_unit_id)
        }
        for evidence_ref in evidence_refs:
            if evidence_ref.segment_id not in segment_ids:
                raise RuleViolationError(
                    f"Evidence ref segment '{evidence_ref.segment_id}' "
                    f"does not belong to source unit '{source_unit_id}'."
                )

    def _build_evidence_ref(self, item: EvidenceRefInput) -> EvidenceRef:
        return EvidenceRef(
            segment_id=item.segment_id,
            quote=item.quote,
            start_offset=item.start_offset,
            end_offset=item.end_offset,
        )

    def _apply_duplicate_resolution(
        self,
        *,
        candidate_nodes: list[CandidateNode],
        candidate_relations: list[CandidateRelation],
        candidate_node_map: dict[str, CandidateNode],
    ) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        results.extend(self._flag_duplicate_candidate_nodes(candidate_nodes))
        node_resolution_keys = {
            candidate_node.candidate_node_id: candidate_node_identity_key(candidate_node)
            for candidate_node in candidate_nodes
            if candidate_node.status != CandidateStatus.REJECTED
        }
        results.extend(
            self._refresh_relation_dependency_statuses(candidate_relations, candidate_node_map)
        )
        results.extend(
            self._flag_duplicate_candidate_relations(
                candidate_relations,
                node_resolution_keys=node_resolution_keys,
            )
        )
        return results

    def _flag_duplicate_candidate_nodes(
        self,
        candidate_nodes: list[CandidateNode],
    ) -> list[ValidationResult]:
        groups: dict[str, list[CandidateNode]] = {}
        for candidate_node in candidate_nodes:
            if candidate_node.status == CandidateStatus.REJECTED:
                continue
            if not candidate_node.merge_key_payload:
                continue
            groups.setdefault(
                build_candidate_node_resolution_key(candidate_node),
                [],
            ).append(candidate_node)

        results: list[ValidationResult] = []
        for group in groups.values():
            if len(group) < 2:
                continue
            sorted_group = sorted(
                group,
                key=lambda item: (-item.confidence, item.candidate_node_id),
            )
            primary = sorted_group[0]
            for duplicate in sorted_group[1:]:
                duplicate.status = CandidateStatus.REVIEW
                results.append(
                    self._build_validation_result(
                        run_id=duplicate.run_id,
                        candidate_ref=duplicate.candidate_node_id,
                        rule_code="potential_duplicate_node",
                        severity="warning",
                        result="review",
                        message=(
                            f"Candidate node may duplicate '{primary.candidate_node_id}' "
                            "based on merge key payload."
                        ),
                    )
                )
        return results

    def _refresh_relation_dependency_statuses(
        self,
        candidate_relations: list[CandidateRelation],
        candidate_node_map: dict[str, CandidateNode],
    ) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        for candidate_relation in candidate_relations:
            if candidate_relation.status == CandidateStatus.REJECTED:
                continue
            from_candidate = candidate_node_map.get(candidate_relation.from_candidate_ref)
            to_candidate = candidate_node_map.get(candidate_relation.to_candidate_ref)
            if from_candidate is None or to_candidate is None:
                continue
            if (
                from_candidate.status == CandidateStatus.REJECTED
                or to_candidate.status == CandidateStatus.REJECTED
            ):
                candidate_relation.status = CandidateStatus.REJECTED
                results.append(
                    self._build_validation_result(
                        run_id=candidate_relation.run_id,
                        candidate_ref=candidate_relation.candidate_relation_id,
                        rule_code="relation_dependency_rejected",
                        severity="error",
                        result="failed",
                        message="Relation depends on candidate nodes that failed validation.",
                    )
                )
                continue
            if (
                from_candidate.status == CandidateStatus.REVIEW
                or to_candidate.status == CandidateStatus.REVIEW
            ):
                candidate_relation.status = CandidateStatus.REVIEW
                results.append(
                    self._build_validation_result(
                        run_id=candidate_relation.run_id,
                        candidate_ref=candidate_relation.candidate_relation_id,
                        rule_code="relation_dependency_review",
                        severity="warning",
                        result="review",
                        message="Relation depends on candidate nodes that require review.",
                    )
                )
        return results

    def _flag_duplicate_candidate_relations(
        self,
        candidate_relations: list[CandidateRelation],
        *,
        node_resolution_keys: dict[str, str],
    ) -> list[ValidationResult]:
        groups: dict[str, list[CandidateRelation]] = {}
        for candidate_relation in candidate_relations:
            if candidate_relation.status == CandidateStatus.REJECTED:
                continue
            groups.setdefault(
                build_candidate_relation_resolution_key(
                    candidate_relation,
                    node_resolution_keys_by_candidate_id=node_resolution_keys,
                ),
                [],
            ).append(candidate_relation)

        results: list[ValidationResult] = []
        for group in groups.values():
            if len(group) < 2:
                continue
            sorted_group = sorted(
                group,
                key=lambda item: (-item.confidence, item.candidate_relation_id),
            )
            primary = sorted_group[0]
            for duplicate in sorted_group[1:]:
                duplicate.status = CandidateStatus.REVIEW
                results.append(
                    self._build_validation_result(
                        run_id=duplicate.run_id,
                        candidate_ref=duplicate.candidate_relation_id,
                        rule_code="potential_duplicate_relation",
                        severity="warning",
                        result="review",
                        message=(
                            f"Candidate relation may duplicate '{primary.candidate_relation_id}'."
                        ),
                    )
                )
        return results

    def _build_review_items(
        self,
        *,
        candidate_nodes: list[CandidateNode],
        candidate_relations: list[CandidateRelation],
        validation_results: list[ValidationResult],
    ) -> list[ReviewItem]:
        all_messages_by_candidate: dict[str, list[str]] = {}
        review_messages_by_candidate: dict[str, list[str]] = {}
        review_reasons_by_candidate: dict[str, str] = {}
        for result in validation_results:
            all_messages_by_candidate.setdefault(result.candidate_ref, []).append(result.message)
            if result.result != "review":
                continue
            review_messages_by_candidate.setdefault(result.candidate_ref, []).append(result.message)
            review_reasons_by_candidate.setdefault(result.candidate_ref, result.rule_code)

        review_items: list[ReviewItem] = []
        for candidate_node in candidate_nodes:
            if candidate_node.status != CandidateStatus.REVIEW:
                continue
            review_items.append(
                ReviewItem(
                    review_item_id=str(uuid4()),
                    run_id=candidate_node.run_id,
                    item_type="candidate_node",
                    item_ref=candidate_node.candidate_node_id,
                    reason_code=review_reasons_by_candidate.get(
                        candidate_node.candidate_node_id,
                        "candidate_review",
                    ),
                    payload_json={
                        "node_type": candidate_node.node_type,
                        "confidence": candidate_node.confidence,
                        "messages": all_messages_by_candidate.get(
                            candidate_node.candidate_node_id,
                            [],
                        ),
                    },
                )
            )

        for candidate_relation in candidate_relations:
            if candidate_relation.status != CandidateStatus.REVIEW:
                continue
            review_items.append(
                ReviewItem(
                    review_item_id=str(uuid4()),
                    run_id=candidate_relation.run_id,
                    item_type="candidate_relation",
                    item_ref=candidate_relation.candidate_relation_id,
                    reason_code=review_reasons_by_candidate.get(
                        candidate_relation.candidate_relation_id,
                        "candidate_review",
                    ),
                    payload_json={
                        "relation_type": candidate_relation.relation_type,
                        "confidence": candidate_relation.confidence,
                        "messages": all_messages_by_candidate.get(
                            candidate_relation.candidate_relation_id,
                            [],
                        ),
                    },
                )
            )
        return review_items

    def _annotate_canonical_matches(
        self,
        *,
        project_id: str,
        candidate_nodes: list[CandidateNode],
        candidate_relations: list[CandidateRelation],
        candidate_node_map: dict[str, CandidateNode],
    ) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        canonical_merge_keys_by_candidate_id: dict[str, str] = {}

        for candidate_node in candidate_nodes:
            if candidate_node.status == CandidateStatus.REJECTED:
                continue
            if not candidate_node.merge_key_payload:
                continue

            canonical_merge_key = build_canonical_merge_key(
                merge_key_payload=candidate_node.merge_key_payload,
                fallback_payload={"candidate_node_id": candidate_node.candidate_node_id},
            )
            canonical_merge_keys_by_candidate_id[candidate_node.candidate_node_id] = (
                canonical_merge_key
            )
            if (
                self.canonical_graph_repository.get_node_detail(
                    project_id,
                    node_type=candidate_node.node_type,
                    merge_key=canonical_merge_key,
                )
                is None
            ):
                continue

            results.append(
                self._build_validation_result(
                    run_id=candidate_node.run_id,
                    candidate_ref=candidate_node.candidate_node_id,
                    rule_code="canonical_node_match",
                    severity="info",
                    result="passed",
                    message="Candidate node resolves to an existing canonical node.",
                )
            )

        for candidate_relation in candidate_relations:
            if candidate_relation.status == CandidateStatus.REJECTED:
                continue

            from_candidate = candidate_node_map.get(candidate_relation.from_candidate_ref)
            to_candidate = candidate_node_map.get(candidate_relation.to_candidate_ref)
            if from_candidate is None or to_candidate is None:
                continue

            from_merge_key = canonical_merge_keys_by_candidate_id.get(
                from_candidate.candidate_node_id
            )
            to_merge_key = canonical_merge_keys_by_candidate_id.get(
                to_candidate.candidate_node_id
            )
            if from_merge_key is None or to_merge_key is None:
                continue

            if (
                self.canonical_graph_repository.get_relation_detail(
                    project_id,
                    relation_type=candidate_relation.relation_type,
                    from_node_type=from_candidate.node_type,
                    from_merge_key=from_merge_key,
                    to_node_type=to_candidate.node_type,
                    to_merge_key=to_merge_key,
                )
                is None
            ):
                continue

            results.append(
                self._build_validation_result(
                    run_id=candidate_relation.run_id,
                    candidate_ref=candidate_relation.candidate_relation_id,
                    rule_code="canonical_relation_match",
                    severity="info",
                    result="passed",
                    message="Candidate relation resolves to an existing canonical relation.",
                )
            )

        return results

    def _split_into_segments(self, raw_content: str) -> list[str]:
        paragraph_chunks = [
            item.strip() for item in split(r"\n\s*\n", raw_content) if item.strip()
        ]
        if len(paragraph_chunks) > 1:
            return paragraph_chunks

        line_chunks = [line.strip() for line in raw_content.splitlines() if line.strip()]
        if line_chunks:
            return line_chunks
        return [raw_content.strip()]

    def _build_validation_result(
        self,
        *,
        run_id: str,
        candidate_ref: str,
        rule_code: str,
        severity: str,
        result: str,
        message: str,
    ) -> ValidationResult:
        return ValidationResult(
            validation_result_id=str(uuid4()),
            run_id=run_id,
            candidate_ref=candidate_ref,
            rule_code=rule_code,
            severity=severity,
            result=result,
            message=message,
        )
