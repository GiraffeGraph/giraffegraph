from app.domain.ingestion.entities import ProcessingRun, SourceUnit
from app.interfaces.api.schemas.ingestion import (
    ProcessingRunResponse,
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
