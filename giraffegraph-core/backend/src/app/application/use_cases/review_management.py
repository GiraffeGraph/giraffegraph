from copy import deepcopy
from dataclasses import dataclass
from uuid import uuid4

from app.application.dto.contracts import ReviewDecisionInput
from app.application.errors import ConflictError, NotFoundError, RuleViolationError
from app.application.ports.repositories import (
    CandidateNodeRepository,
    CandidateRelationRepository,
    ProcessingRunRepository,
    ReviewItemRepository,
    SchemaRepository,
)
from app.domain.extraction.entities import CandidateNode, CandidateRelation
from app.domain.ingestion.entities import ProcessingRun
from app.domain.review.entities import AcceptanceRecord, ReviewDecision, ReviewItem
from app.domain.schema.entities import NodeTypeDefinition, RelationTypeDefinition
from app.domain.shared.enums import CandidateStatus, ReviewStatus, RunStatus
from app.domain.shared.resolution import (
    build_candidate_node_resolution_key,
    build_candidate_relation_resolution_key,
    candidate_node_identity_key,
    derive_merge_key_payload,
    is_missing_value,
    missing_relation_merge_keys,
)
from app.domain.validation.entities import ValidationResult

ACCEPTING_ACTIONS = frozenset({"accept", "edit"})
AUTO_VALIDATED_POLICY = "auto_validated"
PASSED_VALIDATION_RULE_CODES = frozenset({"candidate_node_valid", "candidate_relation_valid"})
DEPENDENCY_REVIEW_REASON = "relation_dependency_review"
DEPENDENCY_REJECTED_REASON = "relation_dependency_rejected"
DEPENDENCY_REASON_CODES = frozenset({DEPENDENCY_REVIEW_REASON, DEPENDENCY_REJECTED_REASON})
AUTO_RESOLVED_NOTE = "Auto-resolved after dependent review decision."
AUTO_CLOSED_NOTE = "Auto-closed after dependent review decision."


@dataclass(slots=True)
class PendingRelationReview:
    reason_code: str
    messages: list[str]


@dataclass(slots=True)
class ReviewManagementService:
    review_item_repository: ReviewItemRepository
    candidate_node_repository: CandidateNodeRepository
    candidate_relation_repository: CandidateRelationRepository
    processing_run_repository: ProcessingRunRepository
    schema_repository: SchemaRepository

    def get_review_item(self, review_item_id: str) -> ReviewItem:
        review_item = self.review_item_repository.get(review_item_id)
        if review_item is None:
            raise NotFoundError(f"Review item '{review_item_id}' was not found.")
        return review_item

    def decide_review_item(
        self,
        review_item_id: str,
        payload: ReviewDecisionInput,
        *,
        reviewer_id: str,
        duration_ms: int | None = None,
    ) -> ReviewItem:
        review_item = self.get_review_item(review_item_id)
        run = self._require_run(review_item.run_id)
        if run.status == RunStatus.COMPLETED:
            raise ConflictError(
                f"Processing run '{run.run_id}' is already completed; review item "
                f"'{review_item_id}' can no longer be decided."
            )

        action = payload.action.strip().casefold()
        if action not in {"accept", "reject", "edit"}:
            raise RuleViolationError("Review action must be one of: accept, reject, edit.")
        normalized_reviewer_id = reviewer_id.strip()
        if normalized_reviewer_id == "":
            raise RuleViolationError("Review decision requires a reviewer_id.")
        if duration_ms is not None and duration_ms < 0:
            raise RuleViolationError("Review decision duration_ms must not be negative.")

        before_json: dict[str, object] | None = None
        after_json: dict[str, object] | None = None
        if review_item.item_type == "candidate_node":
            stored_node = self._require_candidate_node(review_item.item_ref)
            before_json = self._node_snapshot(stored_node)
            node_candidate = deepcopy(stored_node)
            self._apply_node_decision(node_candidate, payload)
            if node_candidate.status != CandidateStatus.REJECTED:
                self._validate_candidate_node_state(node_candidate)
                self._ensure_node_relations_remain_compatible(node_candidate)
                self._ensure_candidate_node_unique_within_run(node_candidate)
            self.candidate_node_repository.save(node_candidate)
            after_json = self._node_snapshot(node_candidate)
        elif review_item.item_type == "candidate_relation":
            stored_relation = self._require_candidate_relation(review_item.item_ref)
            before_json = self._relation_snapshot(stored_relation)
            relation_candidate = deepcopy(stored_relation)
            self._apply_relation_decision(relation_candidate, payload)
            if relation_candidate.status != CandidateStatus.REJECTED:
                relation_type = self._validate_candidate_relation_state(relation_candidate)
                self._ensure_candidate_relation_unique_within_run(
                    relation_candidate,
                    merge_keys=relation_type.merge_keys,
                )
            self.candidate_relation_repository.save(relation_candidate)
            after_json = self._relation_snapshot(relation_candidate)
        elif review_item.item_type == "schema_proposal":
            if action == "edit":
                raise RuleViolationError("Schema proposals can only be accepted or rejected.")
        else:
            raise RuleViolationError(f"Unsupported review item type '{review_item.item_type}'.")

        self.review_item_repository.add_decision(
            ReviewDecision(
                decision_id=str(uuid4()),
                review_item_id=review_item.review_item_id,
                run_id=review_item.run_id,
                item_type=review_item.item_type,
                item_ref=review_item.item_ref,
                action=action,
                reviewer_id=normalized_reviewer_id,
                reviewer_note=payload.reviewer_note,
                duration_ms=duration_ms,
                before_json=before_json if action == "edit" else None,
                after_json=after_json if action == "edit" else None,
            )
        )
        if action == "accept":
            review_item.status = ReviewStatus.ACCEPTED
        elif action == "reject":
            review_item.status = ReviewStatus.REJECTED
        else:
            review_item.status = ReviewStatus.EDITED
        review_item.reviewer_note = payload.reviewer_note
        self.review_item_repository.save(review_item)
        self._refresh_relation_reviews_for_run(run.run_id)
        return self.get_review_item(review_item_id)

    def list_acceptance_records(
        self,
        run_id: str,
        *,
        validation_results: list[ValidationResult],
    ) -> list[AcceptanceRecord]:
        self._require_run(run_id)
        latest_decision_by_ref = {
            decision.item_ref: decision
            for decision in self.review_item_repository.list_decisions_by_run(run_id)
        }
        passed_rule_by_ref = {
            result.candidate_ref: result.rule_code
            for result in validation_results
            if result.rule_code in PASSED_VALIDATION_RULE_CODES and result.result == "passed"
        }
        auto_resolved_reason_by_ref = {
            item.item_ref: item.reason_code
            for item in self.review_item_repository.list_by_run(run_id)
            if item.status == ReviewStatus.ACCEPTED and not item.decisions
        }
        validated_candidates = [
            ("candidate_node", node.candidate_node_id)
            for node in self.candidate_node_repository.list_by_run(run_id)
            if node.status == CandidateStatus.VALIDATED
        ] + [
            ("candidate_relation", relation.candidate_relation_id)
            for relation in self.candidate_relation_repository.list_by_run(run_id)
            if relation.status == CandidateStatus.VALIDATED
        ]

        records: list[AcceptanceRecord] = []
        for candidate_type, candidate_ref in validated_candidates:
            decision = latest_decision_by_ref.get(candidate_ref)
            if decision is not None and decision.action in ACCEPTING_ACTIONS:
                records.append(
                    AcceptanceRecord(
                        candidate_type=candidate_type,
                        candidate_ref=candidate_ref,
                        decision=decision,
                    )
                )
                continue
            records.append(
                AcceptanceRecord(
                    candidate_type=candidate_type,
                    candidate_ref=candidate_ref,
                    policy=AUTO_VALIDATED_POLICY,
                    rule_code=passed_rule_by_ref.get(
                        candidate_ref,
                        auto_resolved_reason_by_ref.get(candidate_ref),
                    ),
                )
            )
        return records

    def _node_snapshot(self, candidate: CandidateNode) -> dict[str, object]:
        return {
            "node_type": candidate.node_type,
            "properties": deepcopy(candidate.properties),
            "merge_key_payload": deepcopy(candidate.merge_key_payload),
            "confidence": candidate.confidence,
        }

    def _relation_snapshot(self, candidate: CandidateRelation) -> dict[str, object]:
        return {
            "relation_type": candidate.relation_type,
            "from_candidate_ref": candidate.from_candidate_ref,
            "to_candidate_ref": candidate.to_candidate_ref,
            "properties": deepcopy(candidate.properties),
            "confidence": candidate.confidence,
        }

    def _apply_node_decision(self, candidate: CandidateNode, payload: ReviewDecisionInput) -> None:
        action = payload.action.strip().casefold()
        if action == "reject":
            candidate.status = CandidateStatus.REJECTED
            return

        if action == "edit":
            if payload.node_type is not None:
                candidate.node_type = payload.node_type.strip()
            if payload.properties:
                candidate.properties = payload.properties
            if payload.merge_key_payload:
                candidate.merge_key_payload = payload.merge_key_payload
            if payload.confidence is not None:
                candidate.confidence = payload.confidence

        candidate.status = CandidateStatus.VALIDATED

    def _apply_relation_decision(
        self,
        candidate: CandidateRelation,
        payload: ReviewDecisionInput,
    ) -> None:
        action = payload.action.strip().casefold()
        if action == "reject":
            candidate.status = CandidateStatus.REJECTED
            return

        if action == "edit":
            if payload.relation_type is not None:
                candidate.relation_type = payload.relation_type.strip()
            if payload.from_candidate_ref is not None:
                candidate.from_candidate_ref = payload.from_candidate_ref
            if payload.to_candidate_ref is not None:
                candidate.to_candidate_ref = payload.to_candidate_ref
            if payload.properties:
                candidate.properties = payload.properties
            if payload.confidence is not None:
                candidate.confidence = payload.confidence

        candidate.status = CandidateStatus.VALIDATED

    def _require_candidate_node(self, candidate_node_id: str) -> CandidateNode:
        candidate = self.candidate_node_repository.get(candidate_node_id)
        if candidate is None:
            raise NotFoundError(f"Candidate node '{candidate_node_id}' was not found.")
        return candidate

    def _require_candidate_relation(self, candidate_relation_id: str) -> CandidateRelation:
        candidate = self.candidate_relation_repository.get(candidate_relation_id)
        if candidate is None:
            raise NotFoundError(f"Candidate relation '{candidate_relation_id}' was not found.")
        return candidate

    def _validate_candidate_node_state(self, candidate: CandidateNode) -> None:
        run = self._require_run(candidate.run_id)
        node_type_map = self._node_type_map(run.schema_version_id)
        node_type = node_type_map.get(candidate.node_type.casefold())
        if node_type is None:
            raise RuleViolationError(
                f"Node type '{candidate.node_type}' is not defined in the active schema."
            )

        missing_required = [
            property_definition.name
            for property_definition in node_type.properties
            if property_definition.required
            and is_missing_value(candidate.properties.get(property_definition.name))
        ]
        if missing_required:
            raise RuleViolationError(
                "Candidate node is missing required properties: "
                + ", ".join(sorted(missing_required))
                + "."
            )

        candidate.merge_key_payload = derive_merge_key_payload(
            node_type=node_type,
            properties=candidate.properties,
            provided_merge_key_payload=candidate.merge_key_payload,
        )
        missing_merge_keys = [
            merge_key
            for merge_key in node_type.merge_keys
            if is_missing_value(candidate.merge_key_payload.get(merge_key))
        ]
        if missing_merge_keys:
            raise RuleViolationError(
                "Candidate node is missing merge keys: "
                + ", ".join(sorted(missing_merge_keys))
                + "."
            )

        candidate.node_type = node_type.name

    def _ensure_node_relations_remain_compatible(self, candidate: CandidateNode) -> None:
        run = self._require_run(candidate.run_id)
        relation_type_map = self._relation_type_map(run.schema_version_id)
        for relation in self.candidate_relation_repository.list_by_run(candidate.run_id):
            if relation.status == CandidateStatus.REJECTED:
                continue
            relation_type = relation_type_map.get(relation.relation_type.casefold())
            if relation_type is None:
                continue
            if (
                relation.from_candidate_ref == candidate.candidate_node_id
                and candidate.node_type.casefold() != relation_type.from_type.casefold()
            ):
                raise RuleViolationError(
                    "Review edit would invalidate an existing relation because the edited node "
                    f"no longer matches from_type '{relation_type.from_type}'."
                )
            if (
                relation.to_candidate_ref == candidate.candidate_node_id
                and candidate.node_type.casefold() != relation_type.to_type.casefold()
            ):
                raise RuleViolationError(
                    "Review edit would invalidate an existing relation because the edited node "
                    f"no longer matches to_type '{relation_type.to_type}'."
                )

    def _validate_candidate_relation_state(
        self,
        candidate: CandidateRelation,
    ) -> RelationTypeDefinition:
        run = self._require_run(candidate.run_id)
        relation_type_map = self._relation_type_map(run.schema_version_id)
        relation_type = relation_type_map.get(candidate.relation_type.casefold())
        if relation_type is None:
            raise RuleViolationError(
                f"Relation type '{candidate.relation_type}' is not defined in the active schema."
            )

        from_candidate = self._require_candidate_node(candidate.from_candidate_ref)
        to_candidate = self._require_candidate_node(candidate.to_candidate_ref)
        if from_candidate.run_id != candidate.run_id or to_candidate.run_id != candidate.run_id:
            raise RuleViolationError(
                "Candidate relation references candidate nodes outside of its run."
            )
        if (
            from_candidate.status != CandidateStatus.VALIDATED
            or to_candidate.status != CandidateStatus.VALIDATED
        ):
            raise RuleViolationError(
                "Candidate relation can only be accepted or edited when both node candidates "
                "are validated."
            )
        if from_candidate.node_type.casefold() != relation_type.from_type.casefold():
            raise RuleViolationError(
                f"Relation expects from_type '{relation_type.from_type}' but received "
                f"'{from_candidate.node_type}'."
            )
        if to_candidate.node_type.casefold() != relation_type.to_type.casefold():
            raise RuleViolationError(
                f"Relation expects to_type '{relation_type.to_type}' but received "
                f"'{to_candidate.node_type}'."
            )

        required_properties = {
            *relation_type.required_properties,
            *[
                property_definition.name
            for property_definition in relation_type.properties
            if property_definition.required
            ],
        }
        missing_required = [
            property_name
            for property_name in sorted(required_properties)
            if is_missing_value(candidate.properties.get(property_name))
        ]
        if missing_required:
            raise RuleViolationError(
                "Candidate relation is missing required properties: "
                + ", ".join(missing_required)
                + "."
            )

        missing_merge_keys = missing_relation_merge_keys(
            merge_keys=relation_type.merge_keys,
            properties=candidate.properties,
        )
        if missing_merge_keys:
            raise RuleViolationError(
                "Candidate relation is missing merge keys: "
                + ", ".join(sorted(missing_merge_keys))
                + "."
            )

        candidate.relation_type = relation_type.name
        return relation_type

    def _ensure_candidate_node_unique_within_run(self, candidate: CandidateNode) -> None:
        duplicate = next(
            (
                other
                for other in self.candidate_node_repository.list_by_run(candidate.run_id)
                if other.candidate_node_id != candidate.candidate_node_id
                and other.status != CandidateStatus.REJECTED
                and build_candidate_node_resolution_key(other)
                == build_candidate_node_resolution_key(candidate)
            ),
            None,
        )
        if duplicate is not None:
            raise RuleViolationError(
                "Review decision would create a duplicate candidate node merge key with "
                f"'{duplicate.candidate_node_id}'."
            )

    def _ensure_candidate_relation_unique_within_run(
        self,
        candidate: CandidateRelation,
        *,
        merge_keys: list[str],
    ) -> None:
        node_resolution_keys = {
            candidate_node.candidate_node_id: candidate_node_identity_key(candidate_node)
            for candidate_node in self.candidate_node_repository.list_by_run(candidate.run_id)
            if candidate_node.status != CandidateStatus.REJECTED
        }
        candidate_relation_key = build_candidate_relation_resolution_key(
            candidate,
            node_resolution_keys_by_candidate_id=node_resolution_keys,
            merge_keys=merge_keys,
        )
        duplicate = next(
            (
                other
                for other in self.candidate_relation_repository.list_by_run(candidate.run_id)
                if other.candidate_relation_id != candidate.candidate_relation_id
                and other.status != CandidateStatus.REJECTED
                and build_candidate_relation_resolution_key(
                    other,
                    node_resolution_keys_by_candidate_id=node_resolution_keys,
                    merge_keys=merge_keys,
                )
                == candidate_relation_key
            ),
            None,
        )
        if duplicate is not None:
            raise RuleViolationError(
                "Review decision would create a duplicate candidate relation with "
                f"'{duplicate.candidate_relation_id}'."
            )

    def _refresh_relation_reviews_for_run(self, run_id: str) -> None:
        run = self._require_run(run_id)
        relation_type_map = self._relation_type_map(run.schema_version_id)
        candidate_nodes = self.candidate_node_repository.list_by_run(run_id)
        candidate_node_map = {
            candidate_node.candidate_node_id: candidate_node for candidate_node in candidate_nodes
        }
        node_resolution_keys = {
            candidate_node.candidate_node_id: candidate_node_identity_key(candidate_node)
            for candidate_node in candidate_nodes
            if candidate_node.status != CandidateStatus.REJECTED
        }
        relations = self.candidate_relation_repository.list_by_run(run_id)
        review_items_by_ref: dict[str, list[ReviewItem]] = {}
        for item in self.review_item_repository.list_by_run(run_id):
            review_items_by_ref.setdefault(item.item_ref, []).append(item)
        human_decided_refs = {
            decision.item_ref
            for decision in self.review_item_repository.list_decisions_by_run(run_id)
        }

        for relation in relations:
            if relation.candidate_relation_id in human_decided_refs:
                continue
            relation_type = relation_type_map.get(relation.relation_type.casefold())
            from_candidate = candidate_node_map.get(relation.from_candidate_ref)
            to_candidate = candidate_node_map.get(relation.to_candidate_ref)
            if relation_type is None or from_candidate is None or to_candidate is None:
                continue

            relation_items = review_items_by_ref.get(relation.candidate_relation_id, [])
            dependency_item = next(
                (
                    item
                    for item in reversed(relation_items)
                    if item.reason_code in DEPENDENCY_REASON_CODES
                ),
                None,
            )
            endpoint_statuses = {from_candidate.status, to_candidate.status}

            if CandidateStatus.REJECTED in endpoint_statuses:
                if relation.status != CandidateStatus.REJECTED:
                    self._reject_relation_for_dependency(relation, dependency_item)
                continue

            if dependency_item is None:
                continue
            awaits_dependency = (
                relation.status == CandidateStatus.REVIEW
                and dependency_item.status == ReviewStatus.OPEN
            )
            rejected_for_dependency = (
                relation.status == CandidateStatus.REJECTED
                and dependency_item.status == ReviewStatus.REJECTED
                and dependency_item.reason_code == DEPENDENCY_REJECTED_REASON
            )
            if not awaits_dependency and not rejected_for_dependency:
                continue

            if endpoint_statuses != {CandidateStatus.VALIDATED}:
                if rejected_for_dependency:
                    self._save_relation_review_state(
                        relation,
                        dependency_item,
                        candidate_status=CandidateStatus.REVIEW,
                        review_status=ReviewStatus.OPEN,
                        reason_code=DEPENDENCY_REVIEW_REASON,
                        reviewer_note=None,
                        messages=["Relation depends on candidate nodes that require review."],
                    )
                continue

            pending_review = self._pending_relation_review(
                relation=relation,
                relation_type=relation_type,
                relations=relations,
                node_resolution_keys=node_resolution_keys,
            )
            if pending_review is not None:
                self._save_relation_review_state(
                    relation,
                    dependency_item,
                    candidate_status=CandidateStatus.REVIEW,
                    review_status=ReviewStatus.OPEN,
                    reason_code=pending_review.reason_code,
                    reviewer_note=None,
                    messages=pending_review.messages,
                )
                continue

            has_other_open_item = any(
                item.status == ReviewStatus.OPEN and item is not dependency_item
                for item in relation_items
            )
            self._save_relation_review_state(
                relation,
                dependency_item,
                candidate_status=(
                    CandidateStatus.REVIEW if has_other_open_item else CandidateStatus.VALIDATED
                ),
                review_status=ReviewStatus.ACCEPTED,
                reason_code=DEPENDENCY_REVIEW_REASON,
                reviewer_note=AUTO_RESOLVED_NOTE,
                messages=["Relation dependencies are validated."],
            )

    def _reject_relation_for_dependency(
        self,
        relation: CandidateRelation,
        dependency_item: ReviewItem | None,
    ) -> None:
        if dependency_item is None:
            dependency_item = ReviewItem(
                review_item_id=str(uuid4()),
                run_id=relation.run_id,
                item_type="candidate_relation",
                item_ref=relation.candidate_relation_id,
                reason_code=DEPENDENCY_REJECTED_REASON,
                payload_json={},
            )
        self._save_relation_review_state(
            relation,
            dependency_item,
            candidate_status=CandidateStatus.REJECTED,
            review_status=ReviewStatus.REJECTED,
            reason_code=DEPENDENCY_REJECTED_REASON,
            reviewer_note=AUTO_CLOSED_NOTE,
            messages=["Relation depends on candidate nodes that were rejected."],
        )

    def _save_relation_review_state(
        self,
        relation: CandidateRelation,
        dependency_item: ReviewItem,
        *,
        candidate_status: CandidateStatus,
        review_status: ReviewStatus,
        reason_code: str,
        reviewer_note: str | None,
        messages: list[str],
    ) -> None:
        relation.status = candidate_status
        self.candidate_relation_repository.save(relation)
        dependency_item.status = review_status
        dependency_item.reason_code = reason_code
        dependency_item.reviewer_note = reviewer_note
        dependency_item.payload_json = {
            **dependency_item.payload_json,
            "relation_type": relation.relation_type,
            "confidence": relation.confidence,
            "messages": messages,
        }
        self.review_item_repository.save(dependency_item)

    def _pending_relation_review(
        self,
        *,
        relation: CandidateRelation,
        relation_type: RelationTypeDefinition,
        relations: list[CandidateRelation],
        node_resolution_keys: dict[str, str],
    ) -> PendingRelationReview | None:
        missing_merge_keys = missing_relation_merge_keys(
            merge_keys=relation_type.merge_keys,
            properties=relation.properties,
        )
        if missing_merge_keys:
            return PendingRelationReview(
                reason_code="missing_relation_merge_key",
                messages=[
                    f"Missing merge key '{merge_key}' for candidate relation."
                    for merge_key in missing_merge_keys
                ],
            )

        if relation.confidence < relation_type.confidence_threshold:
            return PendingRelationReview(
                reason_code="relation_confidence_threshold",
                messages=[
                    "Relation confidence is below the schema threshold "
                    f"({relation_type.confidence_threshold:.2f})."
                ],
            )

        resolution_key = build_candidate_relation_resolution_key(
            relation,
            node_resolution_keys_by_candidate_id=node_resolution_keys,
            merge_keys=relation_type.merge_keys,
        )
        relation_rank = (-relation.confidence, relation.candidate_relation_id)
        for other in relations:
            if (
                other.candidate_relation_id == relation.candidate_relation_id
                or other.status == CandidateStatus.REJECTED
                or build_candidate_relation_resolution_key(
                    other,
                    node_resolution_keys_by_candidate_id=node_resolution_keys,
                    merge_keys=relation_type.merge_keys,
                )
                != resolution_key
            ):
                continue
            if (
                other.status == CandidateStatus.VALIDATED
                or (-other.confidence, other.candidate_relation_id) < relation_rank
            ):
                return PendingRelationReview(
                    reason_code="potential_duplicate_relation",
                    messages=[
                        f"Candidate relation may duplicate '{other.candidate_relation_id}'."
                    ],
                )
        return None

    def _require_run(self, run_id: str) -> ProcessingRun:
        run = self.processing_run_repository.get(run_id)
        if run is None:
            raise NotFoundError(f"Processing run '{run_id}' was not found.")
        return run

    def _node_type_map(self, schema_version_id: str) -> dict[str, NodeTypeDefinition]:
        return {
            node_type.name.casefold(): node_type
            for node_type in self.schema_repository.list_node_types(schema_version_id)
        }

    def _relation_type_map(self, schema_version_id: str) -> dict[str, RelationTypeDefinition]:
        return {
            relation_type.name.casefold(): relation_type
            for relation_type in self.schema_repository.list_relation_types(schema_version_id)
        }
