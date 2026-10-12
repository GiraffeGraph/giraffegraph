"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  decideReviewItem,
  getProjectReviewQueue,
  getSourceUnit,
  listRunCandidateNodes,
} from "@/modules/projects/api";
import { useProject } from "@/modules/projects/components/project-shell";
import { nextStepWithWork, STEP_ACTION, stepHref } from "@/modules/projects/status";
import type {
  CandidateNodeRecord,
  ProjectReviewQueueRecord,
  ReviewDecisionRequest,
} from "@/modules/projects/types";
import { DecisionHistory } from "@/modules/review/components/decision-history";
import {
  ReviewItem,
  type DecisionDraft,
  type HadithText,
} from "@/modules/review/components/review-item";
import { ReviewerNameForm } from "@/modules/review/components/reviewer-name";
import { WriteToGraph } from "@/modules/review/components/write-to-graph";
import { readStoredReviewer, storeReviewer } from "@/modules/review/reviewer";
import { orderEntries } from "@/modules/review/suggestion";
import { ButtonLink } from "@/shared/ui/button";
import { EmptyState, ErrorNote, LoadingBlock } from "@/shared/ui/states";

const QUEUE_RUN_LIMIT = 100;

const DECISION_WORD: Record<ReviewDecisionRequest["action"], string> = {
  accept: "Kabul edildi.",
  reject: "Reddedildi.",
  edit: "Düzeltilerek kabul edildi.",
};

export function ReviewScreen() {
  const { project, status, refreshStatus } = useProject();
  const projectId = project.project_id;

  /** Undefined until the browser storage has been read, so the name form does not flash. */
  const [reviewer, setReviewer] = useState<string | undefined>(undefined);
  const [changingName, setChangingName] = useState(false);

  const [open, setOpen] = useState<ProjectReviewQueueRecord | null>(null);
  const [closed, setClosed] = useState<ProjectReviewQueueRecord | null>(null);
  const [queueError, setQueueError] = useState<unknown>(null);
  const [queueVersion, setQueueVersion] = useState(0);

  const [decidedIds, setDecidedIds] = useState<ReadonlySet<string>>(new Set());
  const [skippedIds, setSkippedIds] = useState<readonly string[]>([]);
  const [busyAction, setBusyAction] = useState<ReviewDecisionRequest["action"] | null>(null);
  const [decisionError, setDecisionError] = useState<unknown>(null);
  const [lastDecision, setLastDecision] = useState<string | null>(null);
  const [wrote, setWrote] = useState(false);

  const [texts, setTexts] = useState<Record<string, HadithText>>({});
  const [runNodes, setRunNodes] = useState<Record<string, CandidateNodeRecord[]>>({});
  const requestedTextsRef = useRef(new Set<string>());
  const shownSinceRef = useRef<number | null>(null);

  useEffect(() => {
    setReviewer(readStoredReviewer());
  }, []);

  const loadQueues = useCallback(async () => {
    try {
      const [openQueue, closedQueue] = await Promise.all([
        getProjectReviewQueue(projectId, { statusFilter: "open", runLimit: QUEUE_RUN_LIMIT }),
        getProjectReviewQueue(projectId, { statusFilter: "closed", runLimit: QUEUE_RUN_LIMIT }),
      ]);
      setOpen(openQueue);
      setClosed(closedQueue);
      setDecidedIds(new Set());
      setQueueError(null);
      setQueueVersion((version) => version + 1);
    } catch (reason: unknown) {
      setQueueError(reason);
    }
  }, [projectId]);

  useEffect(() => {
    void loadQueues();
  }, [loadQueues]);

  const waiting = useMemo(() => {
    if (!open) {
      return [];
    }
    const entries = orderEntries(open).filter(
      (entry) => !decidedIds.has(entry.item.review_item.review_item_id),
    );
    const rank = (id: string) => {
      const index = skippedIds.indexOf(id);
      return index < 0 ? -1 : index;
    };
    return entries
      .map((entry, index) => ({ entry, index }))
      .sort(
        (left, right) =>
          rank(left.entry.item.review_item.review_item_id) -
            rank(right.entry.item.review_item.review_item_id) || left.index - right.index,
      )
      .map(({ entry }) => entry);
  }, [open, decidedIds, skippedIds]);

  const current = waiting[0] ?? null;
  const currentId = current?.item.review_item.review_item_id ?? null;
  const currentRunId = current?.runEntry.run.run_id ?? null;
  const currentSourceId = current?.runEntry.source_unit.source_unit_id ?? null;
  const reviewerReady = reviewer !== undefined && reviewer !== "" && !changingName;

  // Time on item: from the moment a suggestion is in front of the reviewer until the decision.
  useEffect(() => {
    shownSinceRef.current = reviewerReady && currentId !== null ? performance.now() : null;
    setDecisionError(null);
  }, [reviewerReady, currentId]);

  // The text of a hadith does not change, so it is fetched once and kept.
  useEffect(() => {
    if (currentSourceId === null || requestedTextsRef.current.has(currentSourceId)) {
      return;
    }
    requestedTextsRef.current.add(currentSourceId);
    void getSourceUnit(currentSourceId)
      .then((unit): HadithText => ({ state: "ready", raw: unit.raw_content }))
      .catch((): HadithText => ({ state: "missing" }))
      .then((text) => setTexts((known) => ({ ...known, [currentSourceId]: text })));
  }, [currentSourceId]);

  useEffect(() => {
    if (currentRunId === null) {
      return;
    }
    let cancelled = false;
    void listRunCandidateNodes(currentRunId)
      .then((nodes) => {
        if (!cancelled) {
          setRunNodes((known) => ({ ...known, [currentRunId]: nodes }));
        }
      })
      .catch(() => {
        // Without the list a link is shown without its narrator names; deciding still works.
      });
    return () => {
      cancelled = true;
    };
  }, [currentRunId, queueVersion]);

  async function decide(draft: DecisionDraft) {
    if (!current || !reviewer) {
      return;
    }
    const itemId = current.item.review_item.review_item_id;
    const shownSince = shownSinceRef.current;
    setBusyAction(draft.action);
    setDecisionError(null);
    try {
      await decideReviewItem(itemId, {
        ...draft,
        reviewer_id: reviewer,
        duration_ms:
          shownSince === null ? null : Math.max(0, Math.round(performance.now() - shownSince)),
      });
      setLastDecision(DECISION_WORD[draft.action]);
      setDecidedIds((ids) => new Set(ids).add(itemId));
      await Promise.all([loadQueues(), refreshStatus()]);
    } catch (reason: unknown) {
      setDecisionError(reason);
    } finally {
      setBusyAction(null);
    }
  }

  function saveReviewer(name: string) {
    storeReviewer(name);
    setReviewer(name);
    setChangingName(false);
  }

  const next = status ? nextStepWithWork(status) : null;
  const loading = open === null && !queueError;

  return (
    <section className="step-screen" aria-labelledby="step-title">
      <div className="step-intro">
        <h2 id="step-title">İncele</h2>
        <p className="lead">
          Burada yalnızca sistemin kendi başına kabul edemediği öneriler durur. Her birine metne
          bakarak sen karar verirsin; kararın adınla kaydedilir.
        </p>
      </div>

      {queueError ? (
        <ErrorNote
          title="Bekleyen öneriler okunamadı."
          error={queueError}
          onRetry={() => void loadQueues()}
        />
      ) : null}

      {loading || reviewer === undefined ? (
        <div className="card review-placeholder">
          <LoadingBlock label="Bekleyen öneriler yükleniyor" lines={4} />
        </div>
      ) : current && (reviewer === "" || changingName) ? (
        <ReviewerNameForm
          initial={reviewer}
          onSave={saveReviewer}
          onCancel={changingName ? () => setChangingName(false) : undefined}
        />
      ) : current && reviewer ? (
        <>
          <p className="muted small reviewer-line" aria-live="polite">
            {lastDecision ? (
              <span className="status status-done">{lastDecision}</span>
            ) : null}{" "}
            Kararlar “{reviewer}” adıyla kaydediliyor.{" "}
            <button type="button" className="text-link" onClick={() => setChangingName(true)}>
              Adı değiştir
            </button>
          </p>
          <ReviewItem
            key={current.item.review_item.review_item_id}
            entry={current}
            text={
              (currentSourceId ? texts[currentSourceId] : undefined) ?? { state: "loading" }
            }
            runNodes={(currentRunId ? runNodes[currentRunId] : undefined) ?? []}
            remaining={waiting.length}
            busyAction={busyAction}
            error={decisionError}
            onDecide={(draft) => void decide(draft)}
            onSkip={
              waiting.length > 1
                ? () =>
                    setSkippedIds((ids) => [
                      ...ids.filter((id) => id !== currentId),
                      ...(currentId ? [currentId] : []),
                    ])
                : null
            }
          />
        </>
      ) : !queueError && status && status.readyToWrite === 0 && !wrote ? (
        <EmptyState
          icon={lastDecision ? "check" : "inbox"}
          title="Seni bekleyen bir öneri yok"
          action={
            next && next !== "incele" ? (
              <ButtonLink
                href={stepHref(projectId, next)}
                variant="primary"
                iconAfter="arrowRight"
              >
                {STEP_ACTION[next]}
              </ButtonLink>
            ) : null
          }
        >
          {lastDecision
            ? "Bekleyen önerilerin hepsine karar verdin."
            : "Sistem bir öneriden emin olamadığında o öneri burada, tek tek karşına çıkar; metne bakıp kabul eder, reddeder ya da düzeltirsin."}
        </EmptyState>
      ) : null}

      {!loading && !current && lastDecision && status && status.readyToWrite > 0 ? (
        <p className="status status-done" role="status">
          {lastDecision} Bekleyen önerilerin hepsine karar verdin.
        </p>
      ) : null}

      {!loading ? (
        <WriteToGraph
          emphasis={current ? "secondary" : "primary"}
          onWritten={() => setWrote(true)}
        />
      ) : null}

      <DecisionHistory closed={closed} />

      {reviewer && !current && !changingName && !loading ? (
        <p className="muted small">
          Kararlar “{reviewer}” adıyla kaydediliyor.{" "}
          <button type="button" className="text-link" onClick={() => setChangingName(true)}>
            Adı değiştir
          </button>
        </p>
      ) : null}
      {changingName && !current && reviewer !== undefined ? (
        <ReviewerNameForm
          initial={reviewer}
          onSave={saveReviewer}
          onCancel={() => setChangingName(false)}
        />
      ) : null}
    </section>
  );
}
