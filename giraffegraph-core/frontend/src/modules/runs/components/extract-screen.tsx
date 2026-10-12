"use client";

import { useEffect, useState } from "react";

import { processSourceUnits } from "@/modules/projects/api";
import { useProject } from "@/modules/projects/components/project-shell";
import { nextStepWithWork, STEP_ACTION, stepHref } from "@/modules/projects/status";
import type { SourceUnitProcessResultRecord } from "@/modules/projects/types";
import {
  listAvailableMethods,
  RULES_METHOD,
  type ExtractionMethod,
} from "@/modules/runs/methods";
import { Button, ButtonLink } from "@/shared/ui/button";
import { EmptyState, ErrorNote, Note, Skeleton } from "@/shared/ui/states";

interface Progress {
  done: number;
  total: number;
}

function Summary({ results }: { results: SourceUnitProcessResultRecord[] }) {
  const written = results.filter((row) => row.status === "committed").length;
  const needPerson = results.filter((row) => row.status === "needs_review").length;
  const failed = results.filter((row) => row.status === "failed");
  const partial = results.filter((row) => row.status !== "failed" && row.failed_call_count > 0);

  const sentences: string[] = [];
  if (written > 0) {
    sentences.push(`${written} hadis grafa yazıldı.`);
  }
  if (needPerson > 0) {
    sentences.push(`${needPerson} hadiste senin kararın gerekiyor.`);
  }
  if (failed.length > 0) {
    sentences.push(
      `${failed.length} hadis işlenemedi; bu adımı yeniden çalıştırdığında tekrar denenir.`,
    );
  }
  if (partial.length > 0) {
    sentences.push(
      `${partial.length} hadiste zincirlerin bir kısmı okunamadı; o zincirler için öneri üretilmedi.`,
    );
  }

  const problems = [...failed, ...partial];
  return (
    <>
      <p>{sentences.join(" ")}</p>
      {problems.length > 0 ? (
        <details className="disclosure">
          <summary>ayrıntı</summary>
          <ul className="disclosure-body stack-sm">
            {problems.map((row) => (
              <li key={row.source_unit_id}>
                {row.external_ref ?? row.source_unit_id}:{" "}
                {row.detail ?? `${row.failed_call_count} zincir okunamadı.`}
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </>
  );
}

export function ExtractScreen() {
  const { project, status, refreshStatus } = useProject();
  const [methods, setMethods] = useState<ExtractionMethod[] | null>(null);
  const [provider, setProvider] = useState(RULES_METHOD.provider);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [results, setResults] = useState<SourceUnitProcessResultRecord[] | null>(null);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    let cancelled = false;
    void listAvailableMethods(project.project_id).then((available) => {
      if (!cancelled) {
        setMethods(available);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [project.project_id]);

  const waiting = status?.waitingToExtract ?? [];
  const running = progress !== null;
  const method = methods?.find((item) => item.provider === provider) ?? RULES_METHOD;
  const next = status ? nextStepWithWork(status) : null;

  async function run() {
    const ids = waiting.map((hadith) => hadith.source_unit_id);
    const collected: SourceUnitProcessResultRecord[] = [];
    setError(null);
    setResults(null);
    setProgress({ done: 0, total: ids.length });
    try {
      for (let start = 0; start < ids.length; start += method.batchSize) {
        const report = await processSourceUnits(project.project_id, {
          source_unit_ids: ids.slice(start, start + method.batchSize),
          llm_provider: method.provider,
          commit: true,
        });
        collected.push(...report.results);
        setProgress({ done: collected.length, total: ids.length });
      }
    } catch (reason: unknown) {
      setError(reason);
    } finally {
      if (collected.length > 0) {
        setResults(collected);
      }
      await refreshStatus();
      setProgress(null);
    }
  }

  if (status && status.total === 0) {
    return (
      <section className="step-screen" aria-labelledby="step-title">
        <div className="step-intro">
          <h2 id="step-title">Zincirleri çıkar</h2>
        </div>
        <EmptyState
          icon="upload"
          title="Önce metin gerekli"
          action={
            <ButtonLink
              href={stepHref(project.project_id, "yukle")}
              variant="primary"
              icon="arrowLeft"
            >
              Metin yükle
            </ButtonLink>
          }
        >
          Bu projede henüz hadis yok. Metin yüklediğinde, zincirlerini buradan tek düğmeyle
          çıkarabilirsin.
        </EmptyState>
      </section>
    );
  }

  const nothingWaiting = status !== null && waiting.length === 0 && !running;

  return (
    <section className="step-screen" aria-labelledby="step-title">
      <div className="step-intro">
        <h2 id="step-title">Zincirleri çıkar</h2>
        <p className="lead">
          Sistem her hadisin isnadını okur; ravileri ve kimin kimden aldığını önerir, sonra her
          öneriyi metinle karşılaştırır. Kontrolden geçenler grafa yazılır, emin olunamayanlar
          senin incelemen için bekler.
        </p>
      </div>

      <fieldset className="method-list" disabled={running}>
        <legend>Nasıl çıkarılsın?</legend>
        {methods === null ? (
          <div className="method-option" role="status">
            <span className="visually-hidden">Yöntemler kontrol ediliyor</span>
            <Skeleton width="1.1em" height="1.1em" />
            <span className="stack-sm">
              <Skeleton width="16ch" />
              <Skeleton width="38ch" height="0.85em" />
            </span>
          </div>
        ) : (
          methods.map((item) => (
            <label
              key={item.provider}
              className={`method-option${item.provider === provider ? " is-selected" : ""}`}
            >
              <input
                type="radio"
                name="method"
                value={item.provider}
                checked={item.provider === provider}
                onChange={() => setProvider(item.provider)}
              />
              <span>
                <strong>{item.title}</strong>
                <span className="muted small">{item.description}</span>
              </span>
            </label>
          ))
        )}
        {methods !== null && methods.length === 1 ? (
          <p className="muted small">
            Bu sunucuda bir dil modeli tanımlı değil; şimdilik yalnızca kurallarla çıkarım
            yapılabiliyor.
          </p>
        ) : null}
      </fieldset>

      {error ? (
        <ErrorNote
          title="Çıkarma işlemi yarıda kaldı."
          error={error}
          onRetry={waiting.length > 0 ? () => void run() : undefined}
        />
      ) : null}

      {progress ? (
        <div className="card progress" aria-live="polite">
          <p className="num">
            {progress.done} / {progress.total} hadis işlendi
          </p>
          <div
            className="progress-track"
            role="progressbar"
            aria-label="Çıkarma ilerlemesi"
            aria-valuemin={0}
            aria-valuemax={progress.total}
            aria-valuenow={progress.done}
          >
            <div
              className="progress-bar"
              style={{ transform: `scaleX(${progress.total ? progress.done / progress.total : 0})` }}
            />
          </div>
          <p className="muted small">
            Bitene kadar bu sayfada kal. Yarıda kalırsa işlenenler kaybolmaz; kalanlar için
            yeniden başlatabilirsin.
          </p>
        </div>
      ) : null}

      {results && !running ? (
        <Note
          tone={results.some((row) => row.status === "needs_review") ? "attention" : "done"}
          live
          actions={
            next && next !== "cikar" && next !== "yukle" ? (
              <ButtonLink
                href={stepHref(project.project_id, next)}
                variant="primary"
                iconAfter="arrowRight"
              >
                {STEP_ACTION[next]}
              </ButtonLink>
            ) : null
          }
        >
          <Summary results={results} />
          {status &&
          status.openSuggestions > 0 &&
          !results.some((row) => row.status === "needs_review") ? (
            <p>
              Bu projede ayrıca {status.openSuggestions} öneri senin kararını bekliyor.
            </p>
          ) : null}
        </Note>
      ) : null}

      {nothingWaiting && !results ? (
        <Note
          tone="done"
          actions={
            next && next !== "cikar" && next !== "yukle" ? (
              <ButtonLink
                href={stepHref(project.project_id, next)}
                variant="primary"
                iconAfter="arrowRight"
              >
                {STEP_ACTION[next]}
              </ButtonLink>
            ) : null
          }
        >
          <p>
            Yüklü hadislerin hepsinin zinciri çıkarıldı. Yeni metin yüklediğinde burada yeniden
            sıraya girer.
          </p>
        </Note>
      ) : null}

      {!nothingWaiting ? (
        <div>
          <Button
            variant={results && !running ? "secondary" : "primary"}
            busy={running}
            disabled={status === null || methods === null || waiting.length === 0}
            onClick={() => void run()}
          >
            {running
              ? "Çıkarılıyor"
              : status === null
                ? "Zincirleri çıkar"
                : `${waiting.length} hadisin zincirini çıkar`}
          </Button>
        </div>
      ) : null}
    </section>
  );
}
