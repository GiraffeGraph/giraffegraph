from app.application.use_cases.ingestion_management import (
    SourceUnitBulkCreateResult,
    SourceUnitProcessingReport,
)
from app.domain.ingestion.entities import ProcessingRun, SourceUnit
from app.interfaces.api.schemas.ingestion import (
    ProcessingRunResponse,
    SourceUnitBulkCreateResponse,
    SourceUnitBulkItemResponse,
    SourceUnitProcessResponse,
    SourceUnitProcessResultResponse,
    SourceUnitResponse,
    SourceUnitSummaryResponse,
)


def to_source_unit_summary_response(source_unit: SourceUnit) -> SourceUnitSummaryResponse:
    return SourceUnitSummaryResponse(
        source_unit_id=source_unit.source_unit_id,
        project_id=source_unit.project_id,
        schema_version_id=source_unit.schema_version_id,
        source_type=source_unit.source_type,
        title=source_unit.title,
        sequence_no=source_unit.sequence_no,
        external_ref=source_unit.external_ref,
        metadata_json=source_unit.metadata_json,
        status=source_unit.status,
        created_at=source_unit.created_at,
    )


def to_source_unit_response(source_unit: SourceUnit) -> SourceUnitResponse:
    return SourceUnitResponse(
        **to_source_unit_summary_response(source_unit).model_dump(),
        raw_content=source_unit.raw_content,
    )


def to_processing_run_response(run: ProcessingRun) -> ProcessingRunResponse:
    return ProcessingRunResponse(
        run_id=run.run_id,
        project_id=run.project_id,
        schema_version_id=run.schema_version_id,
        source_unit_id=run.source_unit_id,
        pipeline_version=run.pipeline_version,
        status=run.status,
        llm_provider=run.llm_provider,
        llm_model=run.llm_model,
        created_at=run.created_at,
        started_at=run.started_at,
        ended_at=run.ended_at,
    )


def to_source_unit_bulk_create_response(
    result: SourceUnitBulkCreateResult,
) -> SourceUnitBulkCreateResponse:
    return SourceUnitBulkCreateResponse(
        project_id=result.project_id,
        schema_version_id=result.schema_version_id,
        created_count=sum(item.status == "created" for item in result.items),
        duplicate_count=sum(item.status == "duplicate" for item in result.items),
        results=[
            SourceUnitBulkItemResponse(
                index=item.index,
                external_ref=item.external_ref,
                status=item.status,
                source_unit_id=(
                    item.source_unit.source_unit_id if item.source_unit is not None else None
                ),
                detail=item.detail,
            )
            for item in result.items
        ],
    )


def to_source_unit_process_response(
    report: SourceUnitProcessingReport,
) -> SourceUnitProcessResponse:
    failed_count = sum(item.status == "failed" for item in report.results)
    return SourceUnitProcessResponse(
        project_id=report.project_id,
        segmentation_strategy=report.segmentation_strategy,
        llm_provider=report.llm_provider,
        llm_model=report.llm_model,
        processed_count=len(report.results) - failed_count,
        failed_count=failed_count,
        committed_count=sum(item.status == "committed" for item in report.results),
        results=[
            SourceUnitProcessResultResponse(
                source_unit_id=item.source_unit_id,
                external_ref=item.external_ref,
                status=item.status,
                run_id=item.run_id,
                segment_count=item.segment_count,
                candidate_node_count=item.candidate_node_count,
                candidate_relation_count=item.candidate_relation_count,
                validated_node_count=item.validated_node_count,
                validated_relation_count=item.validated_relation_count,
                open_review_count=item.open_review_count,
                failed_call_count=item.failed_call_count,
                detail=item.detail,
            )
            for item in report.results
        ],
    )
