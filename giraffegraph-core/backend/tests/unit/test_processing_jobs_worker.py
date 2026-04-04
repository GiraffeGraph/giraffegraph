import json
from types import SimpleNamespace

from pytest import CaptureFixture, MonkeyPatch

from app.domain.orchestration.entities import ProcessingJob
from app.domain.shared.enums import ProcessingJobStatus, ProcessingJobType
from app.interfaces.cli import processing_jobs_worker


class FakeProcessingJobManagementService:
    def __init__(self, jobs: list[ProcessingJob | None]) -> None:
        self._jobs = jobs
        self.calls: list[object] = []

    def process_next_job(self, payload: object) -> ProcessingJob | None:
        self.calls.append(payload)
        return self._jobs.pop(0)


def _patch_runtime(
    monkeypatch: MonkeyPatch,
    *,
    jobs: list[ProcessingJob | None],
) -> FakeProcessingJobManagementService:
    service = FakeProcessingJobManagementService(jobs=jobs)
    fake_container = SimpleNamespace(processing_job_management_service=service)

    def fake_get_container() -> SimpleNamespace:
        return fake_container

    fake_get_container.cache_clear = lambda: None  # type: ignore[attr-defined]

    monkeypatch.setattr(processing_jobs_worker, "get_container", fake_get_container)
    monkeypatch.setattr(
        processing_jobs_worker,
        "get_settings",
        lambda: SimpleNamespace(
            repository_backend="memory",
            should_auto_apply_postgres_migrations=False,
            processing_job_poll_interval_seconds=0.01,
        ),
    )
    monkeypatch.setattr(processing_jobs_worker, "dispose_neo4j_driver", lambda: None)
    monkeypatch.setattr(processing_jobs_worker, "dispose_postgres_engine", lambda: None)
    monkeypatch.setattr(processing_jobs_worker, "apply_postgres_migrations", lambda: None)
    return service


def test_processing_jobs_worker_processes_single_job(
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    job = ProcessingJob(
        job_id="job-1",
        project_id="project-1",
        run_id="run-1",
        source_unit_id="source-1",
        job_type=ProcessingJobType.EXTRACT_CANDIDATES,
        status=ProcessingJobStatus.SUCCEEDED,
        attempt_count=1,
        output_json={"execution_id": "exec-1"},
    )
    service = _patch_runtime(monkeypatch, jobs=[job])

    exit_code = processing_jobs_worker.main(
        ["--once", "--job-type", "extract_candidates", "--run-id", "run-1"]
    )

    assert exit_code == 0
    assert len(service.calls) == 1
    stdout = capsys.readouterr().out.strip()
    payload = json.loads(stdout)
    assert payload["processed"] is True
    assert payload["job_id"] == "job-1"
    assert payload["status"] == "succeeded"
    assert payload["output_json"]["execution_id"] == "exec-1"


def test_processing_jobs_worker_reports_idle_once(
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    _patch_runtime(monkeypatch, jobs=[None])

    exit_code = processing_jobs_worker.main(["--once"])

    assert exit_code == 0
    stdout = capsys.readouterr().out.strip()
    payload = json.loads(stdout)
    assert payload["processed"] is False
    assert payload["job_type"] is None
    assert payload["run_id"] is None
