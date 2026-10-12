"use client";

import { useState } from "react";

import { commitRun, getProjectReviewQueue, listProjectRuns } from "@/modules/projects/api";
import { useProject } from "@/modules/projects/components/project-shell";
import { stepHref } from "@/modules/projects/status";
import { explainError } from "@/shared/api/errors";
import { Button, ButtonLink } from "@/shared/ui/button";
import { ErrorNote, Note } from "@/shared/ui/states";

interface WriteResult {
  written: number;
  /** Hadiths where every suggestion was rejected, so there was nothing to write. */
  empty: number;
  failures: { ref: string; detail: string }[];
}

function describeWrite(result: WriteResult): string {
  const sentences: string[] = [];
  if (result.written > 0) {
    sentences.push(`${result.written} hadis grafa yazıldı.`);
  }
  if (result.empty > 0) {
    sentences.push(
      `${result.empty} hadiste kabul edilen bir bilgi kalmadığı için grafa bir şey eklenmedi.`,
    );
  }
  if (result.failures.length > 0) {
    sentences.push(`${result.failures.length} hadis yazılamadı; ayrıntıya bakıp tekrar deneyebilirsin.`);
  }
  return sentences.join(" ") || "Grafa yazılacak hadis bulunamadı.";
}

/**
 * Writes the hadiths whose suggestions are all decided. A hadith is written as a whole;
 * what is written cannot be taken back from this interface.
 */
export function WriteToGraph({
  emphasis,
  onWritten,
}: {
  emphasis: "primary" | "secondary";
  /** Called once a write has finished, so the screen can stop offering other next steps. */
  onWritten: () => void;
}) {
  const { project, status, refreshStatus } = useProject();
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<WriteResult | null>(null);
  const [error, setError] = useState<unknown>(null);

  const ready = status?.readyToWrite ?? 0;

  async function write() {
    if (!status) {
      return;
    }
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const [runs, queue] = await Promise.all([
        listProjectRuns(project.project_id),
        getProjectReviewQueue(project.project_id, { statusFilter: "open", runLimit: 100 }),
      ]);
      const stillWaiting = new Set(
        queue.run_entries
          .filter((entry) => entry.open_review_count > 0)
          .map((entry) => entry.run.run_id),
      );
      const unwritten = new Map(
        status.hadiths
          .filter((hadith) => hadith.status === "processing")
          .map((hadith) => [hadith.source_unit_id, hadith.external_ref ?? hadith.title]),
      );
      const outcome: WriteResult = { written: 0, empty: 0, failures: [] };
      for (const run of runs) {
        const ref = unwritten.get(run.source_unit_id);
        const open = run.status === "pending" || run.status === "running";
        if (ref === undefined || !open || stillWaiting.has(run.run_id)) {
          continue;
        }
        try {
          const delta = await commitRun(run.run_id);
          const changes =
            delta.nodes_created + delta.nodes_merged + delta.relations_created + delta.relations_merged;
          if (changes > 0) {
            outcome.written += 1;
          } else {
            outcome.empty += 1;
          }
        } catch (reason: unknown) {
          outcome.failures.push({ ref, detail: explainError(reason).detail ?? "bilinmeyen sorun" });
        }
      }
      setResult(outcome);
      onWritten();
      await refreshStatus();
    } catch (reason: unknown) {
      setError(reason);
    } finally {
      setBusy(false);
    }
  }

  if (result) {
    return (
      <Note
        tone={result.failures.length > 0 ? "attention" : "done"}
        live
        actions={
          result.written > 0 ? (
            <ButtonLink
              href={stepHref(project.project_id, "oku")}
              variant={emphasis}
              iconAfter="arrowRight"
            >
              Zincirleri oku
            </ButtonLink>
          ) : null
        }
      >
        <p>{describeWrite(result)}</p>
        {result.failures.length > 0 ? (
          <details className="disclosure">
            <summary>ayrıntı</summary>
            <ul className="disclosure-body stack-sm">
              {result.failures.map((failure) => (
                <li key={failure.ref}>
                  {failure.ref}: {failure.detail}
                </li>
              ))}
            </ul>
          </details>
        ) : null}
      </Note>
    );
  }

  if (ready === 0) {
    return null;
  }

  return (
    <div className="card stack write-card">
      <div className="stack-sm">
        <h3>
          {ready === 1
            ? "1 hadis grafa yazılmaya hazır"
            : `${ready} hadis grafa yazılmaya hazır`}
        </h3>
        <p className="muted measure">
          {ready === 1 ? "Bu hadisteki" : "Bu hadislerdeki"} önerilerin hepsi karara bağlandı.
          Kabul edilenler grafa yazılır, reddedilenler yazılmaz. Grafa yazılan bilgi bu arayüzden
          geri alınamaz.
        </p>
      </div>
      {error ? <ErrorNote title="Grafa yazılamadı." error={error} /> : null}
      <div>
        <Button variant={emphasis} busy={busy} onClick={() => void write()}>
          {busy ? "Yazılıyor" : ready === 1 ? "Hadisi grafa yaz" : `${ready} hadisi grafa yaz`}
        </Button>
      </div>
    </div>
  );
}
