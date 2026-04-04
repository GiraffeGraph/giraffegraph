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
from app.domain.review.entities import ReviewItem
from app.domain.schema.entities import NodeTypeDefinition, RelationTypeDefinition
from app.domain.shared.enums import CandidateStatus, ReviewStatus
from app.domain.shared.resolution import (
    build_candidate_node_resolution_key,
    build_candidate_relation_resolution_key,
    candidate_node_identity_key,
    derive_merge_key_payload,
    is_missing_value,
)


@dataclass(slots=True)
class RelationEvaluation:
    status: CandidateStatus
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

    def decide_review_item(self, review_item_id: str, payload: ReviewDecisionInput) -> ReviewItem:
        review_item = self.get_review_item(review_item_id)
        if review_item.status != ReviewStatus.OPEN:
            raise ConflictError(f"Review item '{review_item_id}' is already closed.")

        action = payload.action.strip().casefold()
        if action not in {"accept", "reject", "edit"}:
            raise RuleViolationError("Review action must be one of: accept, reject, edit.")

        affected_run_id = review_item.run_id
        if review_item.item_type == "candidate_node":
            node_candidate = deepcopy(self._require_candidate_node(review_item.item_ref))
            self._apply_node_decision(node_candidate, payload)
            if node_candidate.status != CandidateStatus.REJECTED:
                self._validate_candidate_node_state(node_candidate)
                self._ensure_node_relations_remain_compatible(node_candidate)
                self._ensure_candidate_node_unique_within_run(node_candidate)
            self.candidate_node_repository.save(node_candidate)
        elif review_item.item_type == "candidate_relation":
            relation_candidate = deepcopy(self._require_candidate_relation(review_item.item_ref))
            self._apply_relation_decision(relation_candidate, payload)
            if relation_candidate.status != CandidateStatus.REJECTED:
                self._validate_candidate_relation_state(relation_candidate)
                self._ensure_candidate_relation_unique_within_run(relation_candidate)
            self.candidate_relation_repository.save(relation_candidate)
        else:
            raise RuleViolationError(f"Unsupported review item type '{review_item.item_type}'.")

        if action == "accept":
            review_item.status = ReviewStatus.ACCEPTED
        elif action == "reject":
            review_item.status = ReviewStatus.REJECTED
        else:
            review_item.status = ReviewStatus.EDITED
        review_item.reviewer_note = payload.reviewer_note
        self.review_item_repository.save(review_item)
        self._refresh_relation_reviews_for_run(affected_run_id)
        return review_item

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

    def _validate_candidate_relation_state(self, candidate: CandidateRelation) -> None:
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

        candidate.relation_type = relation_type.name

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
    ) -> None:
        node_resolution_keys = {
            candidate_node.candidate_node_id: candidate_node_identity_key(candidate_node)
            for candidate_node in self.candidate_node_repository.list_by_run(candidate.run_id)
            if candidate_node.status != CandidateStatus.REJECTED
        }
        candidate_relation_key = build_candidate_relation_resolution_key(
            candidate,
            node_resolution_keys_by_candidate_id=node_resolution_keys,
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
        review_items = self.review_item_repository.list_by_run(run_id)
        review_items_by_ref: dict[str, list[ReviewItem]] = {}
        for item in review_items:
            review_items_by_ref.setdefault(item.item_ref, []).append(item)

        for relation in self.candidate_relation_repository.list_by_run(run_id):
            evaluation = self._evaluate_relation_candidate_state(
                relation=relation,
                relation_type_map=relation_type_map,
            )
            relation.status = evaluation.status
            self.candidate_relation_repository.save(relation)
            self._sync_relation_review_items(
                relation=relation,
                evaluation=evaluation,
                review_items=review_items_by_ref.get(relation.candidate_relation_id, []),
            )

    def _evaluate_relation_candidate_state(
        self,
        *,
        relation: CandidateRelation,
        relation_type_map: dict[str, RelationTypeDefinition],
    ) -> "RelationEvaluation":
        relation_type = relation_type_map.get(relation.relation_type.casefold())
        if relation_type is None:
            return RelationEvaluation(
                status=CandidateStatus.REJECTED,
                reason_code="relation_type_exists",
                messages=[
                    f"Relation type '{relation.relation_type}' is not defined in schema."
                ],
            )

        from_candidate = self._require_candidate_node(relation.from_candidate_ref)
        to_candidate = self._require_candidate_node(relation.to_candidate_ref)
        if from_candidate.run_id != relation.run_id or to_candidate.run_id != relation.run_id:
            return RelationEvaluation(
                status=CandidateStatus.REJECTED,
                reason_code="relation_candidate_refs",
                messages=[
                    "Relation references candidate nodes that do not exist in the run."
                ],
            )
        if (
            from_candidate.node_type.casefold() != relation_type.from_type.casefold()
            or to_candidate.node_type.casefold() != relation_type.to_type.casefold()
        ):
            return RelationEvaluation(
                status=CandidateStatus.REJECTED,
                reason_code="relation_type_mismatch",
                messages=[
                    "Relation references candidate nodes with incompatible node types."
                ],
            )
        if (
            from_candidate.status == CandidateStatus.REJECTED
            or to_candidate.status == CandidateStatus.REJECTED
        ):
            return RelationEvaluation(
                status=CandidateStatus.REJECTED,
                reason_code="relation_dependency_rejected",
                messages=[
                    "Relation depends on candidate nodes that failed validation."
                ],
            )
        if (
            from_candidate.status != CandidateStatus.VALIDATED
            or to_candidate.status != CandidateStatus.VALIDATED
        ):
            return RelationEvaluation(
                status=CandidateStatus.REVIEW,
                reason_code="relation_dependency_review",
                messages=[
                    "Relation depends on candidate nodes that require review."
                ],
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
            if is_missing_value(relation.properties.get(property_name))
        ]
        if missing_required:
            return RelationEvaluation(
                status=CandidateStatus.REJECTED,
                reason_code="required_relation_property",
                messages=[
                    "Relation is missing required properties: "
                    + ", ".join(missing_required)
                    + "."
                ],
            )

        if relation.confidence < relation_type.confidence_threshold:
            return RelationEvaluation(
                status=CandidateStatus.REVIEW,
                reason_code="relation_confidence_threshold",
                messages=[
                    "Relation confidence is below the schema threshold "
                    f"({relation_type.confidence_threshold:.2f})."
                ],
            )

        relation.relation_type = relation_type.name
        return RelationEvaluation(
            status=CandidateStatus.VALIDATED,
            reason_code="candidate_relation_valid",
            messages=["Candidate relation passed validation."],
        )

    def _sync_relation_review_items(
        self,
        *,
        relation: CandidateRelation,
        evaluation: "RelationEvaluation",
        review_items: list[ReviewItem],
    ) -> None:
        open_items = [
            item
            for item in review_items
            if item.status == ReviewStatus.OPEN
        ]
        messages = list(evaluation.messages)
        payload_json = {
            "relation_type": relation.relation_type,
            "confidence": relation.confidence,
            "messages": messages,
        }

        if relation.status == CandidateStatus.REVIEW:
            if open_items:
                for item in open_items:
                    item.reason_code = evaluation.reason_code
                    item.payload_json = payload_json
                    self.review_item_repository.save(item)
                return

            self.review_item_repository.save(
                ReviewItem(
                    review_item_id=str(uuid4()),
                    run_id=relation.run_id,
                    item_type="candidate_relation",
                    item_ref=relation.candidate_relation_id,
                    reason_code=evaluation.reason_code,
                    payload_json=payload_json,
                )
            )
            return

        if relation.status == CandidateStatus.VALIDATED:
            auto_status = ReviewStatus.ACCEPTED
            note = "Auto-resolved after dependent review decision."
        else:
            auto_status = ReviewStatus.REJECTED
            note = "Auto-closed after dependent review decision."

        for item in open_items:
            item.status = auto_status
            item.reviewer_note = note
            item.payload_json = payload_json
            self.review_item_repository.save(item)

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
