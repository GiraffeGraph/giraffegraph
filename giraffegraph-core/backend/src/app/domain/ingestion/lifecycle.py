from datetime import UTC, datetime

from app.domain.ingestion.entities import ProcessingRun, SourceUnit
from app.domain.shared.enums import RunStatus, SourceUnitStatus


def reserve_source_for_run(source_unit: SourceUnit) -> None:
    source_unit.status = SourceUnitStatus.PROCESSING


def mark_run_started(run: ProcessingRun) -> None:
    now = datetime.now(UTC)
    if run.started_at is None:
        run.started_at = now
    run.ended_at = None
    run.status = RunStatus.RUNNING


def mark_run_failed(run: ProcessingRun, source_unit: SourceUnit) -> None:
    now = datetime.now(UTC)
    if run.started_at is None:
        run.started_at = now
    run.status = RunStatus.FAILED
    run.ended_at = now
    source_unit.status = SourceUnitStatus.FAILED


def mark_run_completed(run: ProcessingRun, source_unit: SourceUnit) -> None:
    now = datetime.now(UTC)
    if run.started_at is None:
        run.started_at = now
    run.status = RunStatus.COMPLETED
    run.ended_at = now
    source_unit.status = SourceUnitStatus.PROCESSED
