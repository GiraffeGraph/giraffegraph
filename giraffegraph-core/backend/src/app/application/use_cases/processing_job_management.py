from collections.abc import Sequence
from dataclasses import dataclass
from uuid import uuid4

from app.application.dto.contracts import (
    ExtractionExecutionInput,
    ProcessingJobCreateInput,
    ProcessingJobProcessNextInput,
)
from app.application.errors import ConflictError, NotFoundError, RuleViolationError
from app.application.ports.repositories import (
    PipelineDefinitionRepository,
    ProcessingJobRepository,
    ProcessingRunRepository,
)
from app.application.use_cases.commit_management import CommitManagementService
from app.application.use_cases.extraction_management import ExtractionManagementService
from app.application.use_cases.pipeline_management import PipelineManagementService
from app.domain.extraction.entities import CandidateNode, CandidateRelation
from app.domain.ingestion.entities import ProcessingRun
from app.domain.orchestration.entities import ProcessingJob
from app.domain.orchestration.lifecycle import (
    mark_processing_job_failed,
    mark_processing_job_succeeded,
)
from app.domain.shared.enums import (
    CandidateStatus,
    ProcessingJobStatus,
    ProcessingJobType,
    RunStatus,
)


@dataclass(slots=True)
class ProcessingJobManagementService:
    processing_run_repository: ProcessingRunRepository
    pipeline_definition_repository: PipelineDefinitionRepository
    processing_job_repository: ProcessingJobRepository
    extraction_management_service: ExtractionManagementService
    pipeline_management_service: PipelineManagementService
    commit_management_service: CommitManagementService

    def enqueue_job(self, payload: ProcessingJobCreateInput) -> ProcessingJob:
        run = self._require_run(payload.run_id)
        if run.status == RunStatus.COMPLETED:
            raise RuleViolationError(
                f"Processing run '{run.run_id}' is already completed and cannot enqueue jobs."
            )
        chain_on_success = self._resolve_chain_on_success(
            run=run,
            job_type=payload.job_type,
            requested_chain_on_success=payload.chain_on_success,
        )
        job = self._enqueue_job(
            run=run,
            job_type=payload.job_type,
            dry_run=payload.dry_run,
            chain_on_success=chain_on_success,
            skip_if_active=False,
            skip_if_succeeded=False,
        )
        if job is None:
            raise RuntimeError("Processing job enqueue unexpectedly returned no job.")
        return job

    def list_jobs(self, run_id: str) -> list[ProcessingJob]:
        self._require_run(run_id)
        return self.processing_job_repository.list_by_run(run_id)

    def process_next_job(
        self,
        payload: ProcessingJobProcessNextInput,
    ) -> ProcessingJob | None:
        if payload.run_id is not None:
            self._require_run(payload.run_id)
        job = self.processing_job_repository.claim_next(
            job_type=payload.job_type,
            run_id=payload.run_id,
        )
        if job is None:
            return None

        try:
            output_json = self._execute_job(job)
            chained_jobs = self._enqueue_chained_jobs(job)
            if chained_jobs:
                output_json = {
                    **output_json,
                    "chained_job_ids": [item.job_id for item in chained_jobs],
                    "chained_job_types": [item.job_type.value for item in chained_jobs],
                }
            mark_processing_job_succeeded(job, output_json=output_json)
        except Exception as exc:
            mark_processing_job_failed(job, error_message=str(exc))

        self.processing_job_repository.save(job)
        return job

    def _execute_job(self, job: ProcessingJob) -> dict[str, object]:
        if job.job_type == ProcessingJobType.EXTRACT_CANDIDATES:
            extraction_report = self.extraction_management_service.extract_candidates(
                job.run_id,
                ExtractionExecutionInput(dry_run=self._dry_run(job)),
            )
            return {
                "execution_id": extraction_report.execution_id,
                "dry_run": extraction_report.dry_run,
                "prompt_version": extraction_report.prompt_version,
                "provider_name": extraction_report.provider_name,
                "resolved_llm_model": extraction_report.resolved_llm_model,
                "segment_count": extraction_report.segment_count,
                "suggested_node_count": len(extraction_report.suggested_nodes),
                "suggested_relation_count": len(extraction_report.suggested_relations),
                "created_candidate_node_count": len(
                    extraction_report.created_candidate_node_ids
                ),
                "created_candidate_relation_count": len(
                    extraction_report.created_candidate_relation_ids
                ),
            }
        if job.job_type == ProcessingJobType.VALIDATE_RUN:
            validation_report = self.pipeline_management_service.validate_run(job.run_id)
            return {
                "node_total": len(validation_report.candidate_nodes),
                "node_validated": self._count_candidates(
                    validation_report.candidate_nodes,
                    CandidateStatus.VALIDATED,
                ),
                "node_review": self._count_candidates(
                    validation_report.candidate_nodes,
                    CandidateStatus.REVIEW,
                ),
                "node_rejected": self._count_candidates(
                    validation_report.candidate_nodes,
                    CandidateStatus.REJECTED,
                ),
                "relation_total": len(validation_report.candidate_relations),
                "relation_validated": self._count_candidates(
                    validation_report.candidate_relations,
                    CandidateStatus.VALIDATED,
                ),
                "relation_review": self._count_candidates(
                    validation_report.candidate_relations,
                    CandidateStatus.REVIEW,
                ),
                "relation_rejected": self._count_candidates(
                    validation_report.candidate_relations,
                    CandidateStatus.REJECTED,
                ),
                "validation_result_count": len(validation_report.validation_results),
            }
        if job.job_type == ProcessingJobType.COMMIT_RUN:
            delta = self.commit_management_service.commit_run(job.run_id)
            return {
                "delta_id": delta.delta_id,
                "nodes_created": delta.nodes_created,
                "nodes_merged": delta.nodes_merged,
                "relations_created": delta.relations_created,
                "relations_merged": delta.relations_merged,
                "review_count": delta.review_count,
                "rejected_count": delta.rejected_count,
            }
        raise RuleViolationError(f"Unsupported processing job type '{job.job_type.value}'.")

    def _build_payload_json(
        self,
        *,
        job_type: ProcessingJobType,
        dry_run: bool,
        chain_on_success: list[ProcessingJobType],
    ) -> dict[str, object]:
        serialized_chain = [item.value for item in chain_on_success]
        if job_type == ProcessingJobType.EXTRACT_CANDIDATES:
            return {
                "dry_run": dry_run,
                "chain_on_success": serialized_chain,
            }
        if dry_run:
            raise RuleViolationError(
                f"Processing job type '{job_type.value}' does not support dry_run."
            )
        if job_type in {ProcessingJobType.VALIDATE_RUN, ProcessingJobType.COMMIT_RUN}:
            return {"chain_on_success": serialized_chain}
        raise RuleViolationError(f"Unsupported processing job type '{job_type.value}'.")

    def _dry_run(self, job: ProcessingJob) -> bool:
        dry_run = job.payload_json.get("dry_run", False)
        return dry_run if isinstance(dry_run, bool) else False

    def _chain_on_success(self, job: ProcessingJob) -> list[ProcessingJobType]:
        raw_values = job.payload_json.get("chain_on_success", [])
        if not isinstance(raw_values, list):
            return []

        chain: list[ProcessingJobType] = []
        for raw_value in raw_values:
            if not isinstance(raw_value, str):
                continue
            try:
                chain.append(ProcessingJobType(raw_value))
            except ValueError:
                continue
        return chain

    def _normalize_chain_on_success(
        self,
        current_job_type: ProcessingJobType,
        chain_on_success: list[ProcessingJobType],
    ) -> list[ProcessingJobType]:
        normalized: list[ProcessingJobType] = []
        seen: set[ProcessingJobType] = set()
        for job_type in chain_on_success:
            if job_type == current_job_type:
                raise RuleViolationError(
                    f"Processing job '{current_job_type.value}' cannot chain to itself."
                )
            if job_type in seen:
                continue
            normalized.append(job_type)
            seen.add(job_type)
        return normalized

    def _resolve_chain_on_success(
        self,
        *,
        run: ProcessingRun,
        job_type: ProcessingJobType,
        requested_chain_on_success: list[ProcessingJobType] | None,
    ) -> list[ProcessingJobType]:
        if requested_chain_on_success is not None:
            return self._normalize_chain_on_success(job_type, requested_chain_on_success)

        pipeline_definition = self.pipeline_definition_repository.get_by_schema_version_and_version(
            schema_version_id=run.schema_version_id,
            version=run.pipeline_version,
        )
        if pipeline_definition is None:
            return []

        for step in pipeline_definition.steps:
            if step.job_type == job_type:
                return list(step.chain_on_success)
        return []

    def _enqueue_chained_jobs(self, job: ProcessingJob) -> list[ProcessingJob]:
        run = self._require_run(job.run_id)
        enqueued_jobs: list[ProcessingJob] = []
        for job_type in self._chain_on_success(job):
            chain_on_success = self._resolve_chain_on_success(
                run=run,
                job_type=job_type,
                requested_chain_on_success=None,
            )
            chained_job = self._enqueue_job(
                run=run,
                job_type=job_type,
                dry_run=False,
                chain_on_success=chain_on_success,
                skip_if_active=True,
                skip_if_succeeded=True,
            )
            if chained_job is not None:
                enqueued_jobs.append(chained_job)
        return enqueued_jobs

    def _enqueue_job(
        self,
        *,
        run: ProcessingRun,
        job_type: ProcessingJobType,
        dry_run: bool,
        chain_on_success: list[ProcessingJobType],
        skip_if_active: bool,
        skip_if_succeeded: bool,
    ) -> ProcessingJob | None:
        jobs = self.processing_job_repository.list_by_run(run.run_id)
        existing_active_job = next(
            (
                job
                for job in jobs
                if job.job_type == job_type
                and job.status in {ProcessingJobStatus.PENDING, ProcessingJobStatus.RUNNING}
            ),
            None,
        )
        if existing_active_job is not None:
            if skip_if_active:
                return None
            raise ConflictError(
                f"Run '{run.run_id}' already has an active '{job_type.value}' job."
            )

        if skip_if_succeeded and any(
            job.job_type == job_type and job.status == ProcessingJobStatus.SUCCEEDED
            for job in jobs
        ):
            return None

        job = ProcessingJob(
            job_id=str(uuid4()),
            project_id=run.project_id,
            run_id=run.run_id,
            source_unit_id=run.source_unit_id,
            job_type=job_type,
            payload_json=self._build_payload_json(
                job_type=job_type,
                dry_run=dry_run,
                chain_on_success=chain_on_success,
            ),
        )
        self.processing_job_repository.add(job)
        return job

    def _count_candidates(
        self,
        candidates: Sequence[CandidateNode | CandidateRelation],
        status: CandidateStatus,
    ) -> int:
        return sum(
            candidate.status == status for candidate in candidates
        )

    def _require_run(self, run_id: str) -> ProcessingRun:
        run = self.processing_run_repository.get(run_id)
        if run is None:
            raise NotFoundError(f"Processing run '{run_id}' was not found.")
        return run
