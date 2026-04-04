import argparse
import json
import time
from collections.abc import Sequence

from app.application.dto.contracts import ProcessingJobProcessNextInput
from app.bootstrap.container import get_container
from app.domain.orchestration.entities import ProcessingJob
from app.domain.shared.enums import ProcessingJobType
from app.infrastructure.config.settings import get_settings
from app.infrastructure.persistence.neo4j.database import dispose_neo4j_driver
from app.infrastructure.persistence.postgres.database import dispose_postgres_engine
from app.infrastructure.persistence.postgres.migrations import apply_postgres_migrations


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    settings = get_settings()
    if (
        settings.repository_backend == "postgres"
        and settings.should_auto_apply_postgres_migrations
    ):
        apply_postgres_migrations()

    job_type = ProcessingJobType(args.job_type) if args.job_type is not None else None
    poll_interval = args.poll_interval_seconds or settings.processing_job_poll_interval_seconds
    processed_count = 0

    try:
        service = get_container().processing_job_management_service
        while True:
            job = service.process_next_job(
                ProcessingJobProcessNextInput(
                    job_type=job_type,
                    run_id=args.run_id,
                )
            )
            if job is None:
                if args.once:
                    print(
                        json.dumps(
                            {
                                "processed": False,
                                "job_type": job_type.value if job_type is not None else None,
                                "run_id": args.run_id,
                            }
                        )
                    )
                    return 0
                time.sleep(poll_interval)
                continue

            print(json.dumps(_build_job_output(job)))
            processed_count += 1
            if args.once:
                return 0
            if args.max_jobs is not None and processed_count >= args.max_jobs:
                return 0
    finally:
        dispose_neo4j_driver()
        if settings.repository_backend == "postgres":
            dispose_postgres_engine()
        get_container.cache_clear()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="processing-jobs-worker",
        description="Consume pending processing jobs from the metadata store.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process at most one pending job and exit.",
    )
    parser.add_argument(
        "--job-type",
        choices=[item.value for item in ProcessingJobType],
        default=None,
        help="Only consume a specific processing job type.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Only consume jobs for a specific run.",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        type=float,
        default=None,
        help="Polling interval in seconds for daemon mode.",
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=None,
        help="Maximum number of jobs to process before exiting in daemon mode.",
    )
    return parser


def _build_job_output(job: ProcessingJob) -> dict[str, object]:
    return {
        "processed": True,
        "job_id": job.job_id,
        "run_id": job.run_id,
        "job_type": job.job_type.value,
        "status": job.status.value,
        "attempt_count": job.attempt_count,
        "error_message": job.error_message,
        "output_json": job.output_json,
    }


if __name__ == "__main__":
    raise SystemExit(main())
