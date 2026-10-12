"use client";

import { useEffect, useState } from "react";

import { getProjectProcessingJobs } from "@/modules/projects/api";
import type {
  ProcessingJobQueueStatusFilter,
  ProcessingJobRecord,
  ProjectProcessingJobQueueRecord,
  ProjectRecord,
} from "@/modules/projects/types";
import { formatDateTime } from "@/shared/format";
import { Button } from "@/shared/ui/button";
import { ErrorNote, LoadingBlock } from "@/shared/ui/states";

const RUN_LIMITS = [8, 12, 24, 48];

const JOB_STATUS: Record<ProcessingJobRecord["status"], { text: string; tone: string }> = {
  pending: { text: "sırada", tone: "tag-attention" },
  running: { text: "çalışıyor", tone: "tag-attention" },
  succeeded: { text: "tamamlandı", tone: "tag-done" },
  failed: { text: "hata", tone: "tag-attention" },
};

interface JobEntry {
  job: ProcessingJobRecord;
  sourceTitle: string;
}

function flattenJobs(queue: ProjectProcessingJobQueueRecord | null): JobEntry[] {
  if (!queue) {
    return [];
  }
  return queue.run_entries
    .flatMap((entry) => entry.jobs.map((job) => ({ job, sourceTitle: entry.source_unit.title })))
    .sort((left, right) => Date.parse(right.job.created_at) - Date.parse(left.job.created_at));
}

/** Developer view: background jobs of the project (queued extraction, validation, commit). */
export function JobsPanel({ project }: { project: ProjectRecord }) {
  const [queue, setQueue] = useState<ProjectProcessingJobQueueRecord | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [statusFilter, setStatusFilter] = useState<ProcessingJobQueueStatusFilter>("all");
  const [runLimit, setRunLimit] = useState(12);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    void getProjectProcessingJobs(project.project_id, { statusFilter, runLimit })
      .then((result) => {
        if (!cancelled) {
          setQueue(result);
        }
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setError(reason);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [project.project_id, statusFilter, runLimit, reloadToken]);

  const jobs = flattenJobs(queue);
  const selected = jobs.find((entry) => entry.job.job_id === selectedId) ?? jobs[0] ?? null;

  return (
    <div className="adv-layout">
      <div className="card stack">
        <div className="row-between">
          <h3>İşler</h3>
          <Button size="sm" variant="quiet" onClick={() => setReloadToken((token) => token + 1)}>
            Yenile
          </Button>
        </div>
        <div className="field-grid">
          <label className="field">
            <span>Durum</span>
            <select
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(event.currentTarget.value as ProcessingJobQueueStatusFilter)
              }
            >
              <option value="all">Hepsi</option>
              <option value="active">Sırada ya da çalışıyor</option>
              <option value="failed">Hata alanlar</option>
              <option value="succeeded">Tamamlananlar</option>
            </select>
          </label>
          <label className="field">
            <span>Kapsam</span>
            <select value={runLimit} onChange={(event) => setRunLimit(Number(event.currentTarget.value))}>
              {RUN_LIMITS.map((limit) => (
                <option key={limit} value={limit}>
                  Son {limit} çalıştırma
                </option>
              ))}
            </select>
          </label>
        </div>
        {error ? (
          <ErrorNote title="İşler okunamadı." error={error} />
        ) : queue === null ? (
          <LoadingBlock label="İşler yükleniyor" />
        ) : jobs.length === 0 ? (
          <p className="muted small">
            Bu filtreye uyan iş yok. İş kuyruğu yalnızca arka planda çalıştırılan adımlar için
            kayıt tutar; dört adımlı akış istekleri doğrudan işlediği için burada görünmez.
          </p>
        ) : (
          <ul className="list-rows list-rows-scroll">
            {jobs.map(({ job, sourceTitle }) => (
              <li key={job.job_id}>
                <button
                  type="button"
                  className={`list-row${job.job_id === selected?.job.job_id ? " is-selected" : ""}`}
                  onClick={() => setSelectedId(job.job_id)}
                >
                  <span className="row-between">
                    <strong>{job.job_type}</strong>
                    <span className={`tag ${JOB_STATUS[job.status].tone}`}>
                      {JOB_STATUS[job.status].text}
                    </span>
                  </span>
                  <span className="muted small">
                    {sourceTitle} · {formatDateTime(job.created_at)}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card stack">
        {selected ? (
          <>
            <div className="row-between">
              <h3>{selected.job.job_type}</h3>
              <span className={`tag ${JOB_STATUS[selected.job.status].tone}`}>
                {JOB_STATUS[selected.job.status].text}
              </span>
            </div>
            <dl className="def-grid">
              <div>
                <dt>Kaynak birimi</dt>
                <dd>{selected.sourceTitle}</dd>
              </div>
              <div>
                <dt>İş kimliği</dt>
                <dd>{selected.job.job_id}</dd>
              </div>
              <div>
                <dt>Run kimliği</dt>
                <dd>{selected.job.run_id}</dd>
              </div>
              <div>
                <dt>Deneme sayısı</dt>
                <dd>{selected.job.attempt_count}</dd>
              </div>
              <div>
                <dt>Başladı</dt>
                <dd>{formatDateTime(selected.job.started_at)}</dd>
              </div>
              <div>
                <dt>Bitti</dt>
                <dd>{formatDateTime(selected.job.completed_at)}</dd>
              </div>
            </dl>
            {selected.job.error_message ? (
              <p className="status status-attention">{selected.job.error_message}</p>
            ) : null}
            <section className="stack-sm">
              <h4>Girdi</h4>
              <pre className="json-block">{JSON.stringify(selected.job.payload_json, null, 2)}</pre>
            </section>
            <section className="stack-sm">
              <h4>Çıktı</h4>
              <pre className="json-block">{JSON.stringify(selected.job.output_json, null, 2)}</pre>
            </section>
          </>
        ) : (
          <p className="muted">Bir iş seçtiğinde girdisi, çıktısı ve varsa hatası burada görünür.</p>
        )}
      </div>
    </div>
  );
}
