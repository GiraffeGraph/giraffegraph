"use client";

import { useEffect, useState } from "react";

import {
  ApiError,
  decideReviewItem,
  getGraphNodeDetail,
  getProjectProcessingJobs,
  getGraphRelationDetail,
  getProjectReviewQueue,
  listProjects,
  loadGraphSnapshot,
} from "@/modules/projects/api";
import { SchemaTab } from "@/modules/projects/components/schema-tab";
import { PipelineTab } from "@/modules/projects/components/pipeline-tab";
import type {
  CanonicalNodeDetailRecord,
  CanonicalNodeRecord,
  CanonicalRelationDetailRecord,
  CanonicalRelationRecord,
  GraphSnapshot,
  ProcessingJobQueueRunEntryRecord,
  ProcessingJobQueueStatusFilter,
  ProcessingJobRecord,
  ProjectReviewQueueRecord,
  ProjectProcessingJobQueueRecord,
  ProjectRecord,
  ReviewDecisionRequest,
  ReviewQueueItemRecord,
  ReviewQueueStatusFilter,
  ReviewQueueRunEntryRecord,
} from "@/modules/projects/types";
import { apiBaseUrl } from "@/shared/api/config";

const GRAPH_LIMIT = 48;
const RUN_LIMIT_OPTIONS = [8, 12, 24, 48] as const;

type DashboardView = "schema" | "ingest" | "review" | "operations" | "graph";
type ReviewAction = "accept" | "reject" | "edit";

interface ReviewFormState {
  action: ReviewAction;
  reviewerNote: string;
  nodeType: string;
  relationType: string;
  fromCandidateRef: string;
  toCandidateRef: string;
  confidence: string;
  propertiesText: string;
  mergeKeyText: string;
}

interface ReviewQueueEntry {
  runEntry: ReviewQueueRunEntryRecord;
  queueItem: ReviewQueueItemRecord;
}

interface ProcessingJobEntry {
  runEntry: ProcessingJobQueueRunEntryRecord;
  job: ProcessingJobRecord;
}

type GraphSelection =
  | { kind: "node"; key: string }
  | { kind: "relation"; key: string }
  | null;

const emptyReviewForm = (): ReviewFormState => ({
  action: "accept",
  reviewerNote: "",
  nodeType: "",
  relationType: "",
  fromCandidateRef: "",
  toCandidateRef: "",
  confidence: "",
  propertiesText: "{}",
  mergeKeyText: "{}",
});

function stringifyPretty(value: unknown): string {
  return JSON.stringify(value ?? {}, null, 2);
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return "N/A";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("tr-TR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatShortId(value: string): string {
  return value.slice(0, 8);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "N/A";
  }
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  return JSON.stringify(value);
}

function getPrimaryProperty(
  properties: Record<string, unknown>,
): [string, string] | null {
  const preferredKeys = [
    "name",
    "title",
    "label",
    "display_name",
    "slug",
    "id",
  ];

  for (const key of preferredKeys) {
    const value = properties[key];
    if (typeof value === "string" && value.trim()) {
      return [key, value.trim()];
    }
  }

  for (const [key, value] of Object.entries(properties)) {
    if (typeof value === "string" && value.trim()) {
      return [key, value.trim()];
    }
  }

  return null;
}

function describeCanonicalNode(candidate: CanonicalNodeRecord): string {
  const primary = getPrimaryProperty(candidate.properties);
  if (primary) {
    return `${candidate.node_type} · ${primary[1]}`;
  }
  return `${candidate.node_type} · ${candidate.merge_key.slice(0, 10)}`;
}

function statusLabel(status: string): string {
  return status.replaceAll("_", " ");
}

function reviewStatusTone(status: string): string {
  if (
    status === "open" ||
    status === "review" ||
    status === "pending" ||
    status === "running" ||
    status === "processing"
  ) {
    return "warning";
  }
  if (
    status === "accepted" ||
    status === "validated" ||
    status === "completed" ||
    status === "active" ||
    status === "processed" ||
    status === "succeeded"
  ) {
    return "success";
  }
  if (status === "rejected" || status === "failed" || status === "archived") {
    return "danger";
  }
  return "neutral";
}

function buildReviewEntries(reviewQueue: ProjectReviewQueueRecord | null): ReviewQueueEntry[] {
  if (!reviewQueue) {
    return [];
  }

  const entries: ReviewQueueEntry[] = [];
  for (const runEntry of reviewQueue.run_entries) {
    for (const queueItem of runEntry.review_items) {
      entries.push({ runEntry, queueItem });
    }
  }

  entries.sort((left, right) => {
    if (
      left.queueItem.review_item.status === "open" &&
      right.queueItem.review_item.status !== "open"
    ) {
      return -1;
    }
    if (
      left.queueItem.review_item.status !== "open" &&
      right.queueItem.review_item.status === "open"
    ) {
      return 1;
    }
    return (
      Date.parse(right.queueItem.review_item.created_at) -
      Date.parse(left.queueItem.review_item.created_at)
    );
  });

  return entries;
}

function buildProcessingJobEntries(
  processingJobQueue: ProjectProcessingJobQueueRecord | null,
): ProcessingJobEntry[] {
  if (!processingJobQueue) {
    return [];
  }

  const entries: ProcessingJobEntry[] = [];
  for (const runEntry of processingJobQueue.run_entries) {
    for (const job of runEntry.jobs) {
      entries.push({ runEntry, job });
    }
  }

  entries.sort(
    (left, right) =>
      Date.parse(right.job.created_at) - Date.parse(left.job.created_at),
  );

  return entries;
}

function buildReviewFormState(entry: ReviewQueueEntry): ReviewFormState {
  if (entry.queueItem.candidate_node) {
    return {
      action: "accept",
      reviewerNote: "",
      nodeType: entry.queueItem.candidate_node.node_type,
      relationType: "",
      fromCandidateRef: "",
      toCandidateRef: "",
      confidence: entry.queueItem.candidate_node.confidence.toFixed(2),
      propertiesText: stringifyPretty(entry.queueItem.candidate_node.properties),
      mergeKeyText: stringifyPretty(entry.queueItem.candidate_node.merge_key_payload),
    };
  }

  if (entry.queueItem.candidate_relation) {
    return {
      action: "accept",
      reviewerNote: "",
      nodeType: "",
      relationType: entry.queueItem.candidate_relation.relation_type,
      fromCandidateRef: entry.queueItem.candidate_relation.from_candidate_ref,
      toCandidateRef: entry.queueItem.candidate_relation.to_candidate_ref,
      confidence: entry.queueItem.candidate_relation.confidence.toFixed(2),
      propertiesText: stringifyPretty(entry.queueItem.candidate_relation.properties),
      mergeKeyText: "{}",
    };
  }

  return emptyReviewForm();
}

function parseJsonObject(value: string, fieldLabel: string): Record<string, unknown> {
  const parsed = JSON.parse(value || "{}") as unknown;
  if (!isRecord(parsed)) {
    throw new Error(`${fieldLabel} geçerli bir JSON nesnesi olmalı.`);
  }
  return parsed;
}

function toErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Beklenmeyen bir hata oluştu.";
}

function nodeKey(node: CanonicalNodeRecord): string {
  return `${node.node_type}::${node.merge_key}`;
}

function relationKey(relation: CanonicalRelationRecord): string {
  return [
    relation.relation_type,
    relation.from_node_type,
    relation.from_merge_key,
    relation.to_node_type,
    relation.to_merge_key,
  ].join("::");
}

function buildCanonicalNodeLabelMap(nodes: CanonicalNodeRecord[]): Map<string, string> {
  return new Map(nodes.map((node) => [nodeKey(node), describeCanonicalNode(node)]));
}

export function DashboardHome() {
  const [projects, setProjects] = useState<ProjectRecord[]>([]);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState<string | null>(null);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<DashboardView>("review");

  const [reviewQueue, setReviewQueue] = useState<ProjectReviewQueueRecord | null>(null);
  const [reviewQueueLoading, setReviewQueueLoading] = useState(false);
  const [reviewQueueError, setReviewQueueError] = useState<string | null>(null);
  const [reviewQueueReloadToken, setReviewQueueReloadToken] = useState(0);
  const [reviewStatusFilter, setReviewStatusFilter] =
    useState<ReviewQueueStatusFilter>("open");
  const [reviewRunLimit, setReviewRunLimit] = useState<number>(12);
  const [processingJobQueue, setProcessingJobQueue] =
    useState<ProjectProcessingJobQueueRecord | null>(null);
  const [processingJobQueueLoading, setProcessingJobQueueLoading] = useState(false);
  const [processingJobQueueError, setProcessingJobQueueError] = useState<string | null>(
    null,
  );
  const [processingJobQueueReloadToken, setProcessingJobQueueReloadToken] = useState(0);
  const [processingJobStatusFilter, setProcessingJobStatusFilter] =
    useState<ProcessingJobQueueStatusFilter>("active");
  const [processingJobRunLimit, setProcessingJobRunLimit] = useState<number>(12);

  const [graphSnapshot, setGraphSnapshot] = useState<GraphSnapshot | null>(null);
  const [graphLoading, setGraphLoading] = useState(false);
  const [graphError, setGraphError] = useState<string | null>(null);
  const [graphDetailLoading, setGraphDetailLoading] = useState(false);
  const [graphDetailError, setGraphDetailError] = useState<string | null>(null);
  const [selectedNodeDetail, setSelectedNodeDetail] =
    useState<CanonicalNodeDetailRecord | null>(null);
  const [selectedRelationDetail, setSelectedRelationDetail] =
    useState<CanonicalRelationDetailRecord | null>(null);
  const [graphReloadToken, setGraphReloadToken] = useState(0);
  const [nodeTypeFilter, setNodeTypeFilter] = useState("");
  const [relationTypeFilter, setRelationTypeFilter] = useState("");
  const [graphSelection, setGraphSelection] = useState<GraphSelection>(null);

  const [selectedReviewId, setSelectedReviewId] = useState<string | null>(null);
  const [selectedProcessingJobId, setSelectedProcessingJobId] = useState<string | null>(
    null,
  );
  const [reviewForm, setReviewForm] = useState<ReviewFormState>(emptyReviewForm());
  const [reviewFormError, setReviewFormError] = useState<string | null>(null);
  const [reviewMutationState, setReviewMutationState] = useState<
    "idle" | "submitting"
  >("idle");
  const [reviewMutationNotice, setReviewMutationNotice] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setProjectsLoading(true);
    setProjectsError(null);

    void listProjects()
      .then((items) => {
        if (cancelled) {
          return;
        }

        setProjects(items);
        setSelectedProjectId((current) => {
          if (current && items.some((item) => item.project_id === current)) {
            return current;
          }
          return items[0]?.project_id ?? null;
        });
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        setProjectsError(toErrorMessage(error));
      })
      .finally(() => {
        if (!cancelled) {
          setProjectsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    setSelectedReviewId(null);
    setSelectedProcessingJobId(null);
    setReviewForm(emptyReviewForm());
    setReviewFormError(null);
    setReviewMutationNotice(null);
    setGraphSelection(null);
    setSelectedNodeDetail(null);
    setSelectedRelationDetail(null);
    setGraphDetailError(null);
    setReviewStatusFilter("open");
    setReviewRunLimit(12);
    setProcessingJobStatusFilter("active");
    setProcessingJobRunLimit(12);
    setNodeTypeFilter("");
    setRelationTypeFilter("");
  }, [selectedProjectId]);

  useEffect(() => {
    if (!selectedProjectId) {
      setReviewQueue(null);
      return;
    }

    let cancelled = false;
    setReviewQueueLoading(true);
    setReviewQueueError(null);

    void getProjectReviewQueue(selectedProjectId, {
      statusFilter: reviewStatusFilter,
      runLimit: reviewRunLimit,
    })
      .then((result) => {
        if (cancelled) {
          return;
        }
        setReviewQueue(result);
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        setReviewQueueError(toErrorMessage(error));
      })
      .finally(() => {
        if (!cancelled) {
          setReviewQueueLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selectedProjectId, reviewQueueReloadToken, reviewRunLimit, reviewStatusFilter]);

  useEffect(() => {
    if (!selectedProjectId) {
      setProcessingJobQueue(null);
      return;
    }

    let cancelled = false;
    setProcessingJobQueueLoading(true);
    setProcessingJobQueueError(null);

    void getProjectProcessingJobs(selectedProjectId, {
      statusFilter: processingJobStatusFilter,
      runLimit: processingJobRunLimit,
    })
      .then((result) => {
        if (cancelled) {
          return;
        }
        setProcessingJobQueue(result);
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        setProcessingJobQueueError(toErrorMessage(error));
      })
      .finally(() => {
        if (!cancelled) {
          setProcessingJobQueueLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [
    selectedProjectId,
    processingJobQueueReloadToken,
    processingJobRunLimit,
    processingJobStatusFilter,
  ]);

  useEffect(() => {
    if (!selectedProjectId) {
      setGraphSnapshot(null);
      setSelectedNodeDetail(null);
      setSelectedRelationDetail(null);
      return;
    }

    let cancelled = false;
    setGraphLoading(true);
    setGraphError(null);

    void loadGraphSnapshot(selectedProjectId, {
      nodeType: nodeTypeFilter || undefined,
      relationType: relationTypeFilter || undefined,
      limit: GRAPH_LIMIT,
    })
      .then((result) => {
        if (cancelled) {
          return;
        }
        setGraphSnapshot(result);
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        setGraphError(toErrorMessage(error));
      })
      .finally(() => {
        if (!cancelled) {
          setGraphLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selectedProjectId, nodeTypeFilter, relationTypeFilter, graphReloadToken]);

  const selectedProject =
    projects.find((project) => project.project_id === selectedProjectId) ?? null;
  const reviewEntries = buildReviewEntries(reviewQueue);
  const processingJobEntries = buildProcessingJobEntries(processingJobQueue);
  const selectedReviewEntry =
    reviewEntries.find((item) => item.queueItem.review_item.review_item_id === selectedReviewId) ??
    reviewEntries[0] ??
    null;
  const selectedProcessingJobEntry =
    processingJobEntries.find((item) => item.job.job_id === selectedProcessingJobId) ??
    processingJobEntries[0] ??
    null;

  useEffect(() => {
    if (reviewEntries.length === 0) {
      if (selectedReviewId !== null) {
        setSelectedReviewId(null);
      }
      return;
    }

    if (
      !selectedReviewId ||
      !reviewEntries.some(
        (entry) => entry.queueItem.review_item.review_item_id === selectedReviewId,
      )
    ) {
      const nextSelection =
        reviewEntries.find((entry) => entry.queueItem.review_item.status === "open") ??
        reviewEntries[0];
      setSelectedReviewId(nextSelection.queueItem.review_item.review_item_id);
    }
  }, [reviewEntries, selectedReviewId]);

  useEffect(() => {
    if (processingJobEntries.length === 0) {
      if (selectedProcessingJobId !== null) {
        setSelectedProcessingJobId(null);
      }
      return;
    }

    if (
      !selectedProcessingJobId ||
      !processingJobEntries.some((entry) => entry.job.job_id === selectedProcessingJobId)
    ) {
      setSelectedProcessingJobId(processingJobEntries[0].job.job_id);
    }
  }, [processingJobEntries, selectedProcessingJobId]);

  useEffect(() => {
    if (!selectedReviewEntry) {
      setReviewForm(emptyReviewForm());
      return;
    }

    setReviewForm(buildReviewFormState(selectedReviewEntry));
    setReviewFormError(null);
    setReviewMutationNotice(null);
  }, [selectedReviewEntry]);

  useEffect(() => {
    if (!graphSnapshot) {
      setGraphSelection(null);
      return;
    }

    if (!graphSelection) {
      if (graphSnapshot.nodes[0]) {
        setGraphSelection({ kind: "node", key: nodeKey(graphSnapshot.nodes[0]) });
      } else if (graphSnapshot.relations[0]) {
        setGraphSelection({
          kind: "relation",
          key: relationKey(graphSnapshot.relations[0]),
        });
      }
      return;
    }

    if (graphSelection.kind === "node") {
      const exists = graphSnapshot.nodes.some((item) => nodeKey(item) === graphSelection.key);
      if (!exists) {
        setGraphSelection(null);
      }
      return;
    }

    const exists = graphSnapshot.relations.some(
      (item) => relationKey(item) === graphSelection.key,
    );
    if (!exists) {
      setGraphSelection(null);
    }
  }, [graphSnapshot, graphSelection]);

  const canonicalNodeLabelMap = buildCanonicalNodeLabelMap(graphSnapshot?.nodes ?? []);

  const relationTypeOptions = Array.from(
    new Set((graphSnapshot?.relations ?? []).map((item) => item.relation_type)),
  ).sort((left, right) => left.localeCompare(right));
  if (relationTypeFilter && !relationTypeOptions.includes(relationTypeFilter)) {
    relationTypeOptions.push(relationTypeFilter);
    relationTypeOptions.sort((left, right) => left.localeCompare(right));
  }

  useEffect(() => {
    if (!selectedProjectId || !graphSelection) {
      setSelectedNodeDetail(null);
      setSelectedRelationDetail(null);
      setGraphDetailError(null);
      setGraphDetailLoading(false);
      return;
    }

    let cancelled = false;
    setGraphDetailLoading(true);
    setGraphDetailError(null);

    const loadDetail = async () => {
      if (graphSelection.kind === "node") {
        const node =
          graphSnapshot?.nodes.find((item) => nodeKey(item) === graphSelection.key) ?? null;
        if (!node) {
          throw new Error("Seçili düğüm mevcut veride bulunamadı.");
        }
        const detail = await getGraphNodeDetail(
          selectedProjectId,
          node.node_type,
          node.merge_key,
        );
        if (!cancelled) {
          setSelectedNodeDetail(detail);
          setSelectedRelationDetail(null);
        }
        return;
      }

      const relation =
        graphSnapshot?.relations.find(
          (item) => relationKey(item) === graphSelection.key,
        ) ?? null;
      if (!relation) {
        throw new Error("Seçili ilişki mevcut veride bulunamadı.");
      }
      const detail = await getGraphRelationDetail(selectedProjectId, {
        relationType: relation.relation_type,
        fromNodeType: relation.from_node_type,
        fromMergeKey: relation.from_merge_key,
        toNodeType: relation.to_node_type,
        toMergeKey: relation.to_merge_key,
      });
      if (!cancelled) {
        setSelectedRelationDetail(detail);
        setSelectedNodeDetail(null);
      }
    };

    void loadDetail()
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        setGraphDetailError(toErrorMessage(error));
        setSelectedNodeDetail(null);
        setSelectedRelationDetail(null);
      })
      .finally(() => {
        if (!cancelled) {
          setGraphDetailLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selectedProjectId, graphSelection, graphSnapshot]);

  async function submitReviewDecision(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedReviewEntry) {
      return;
    }

    const request: ReviewDecisionRequest = {
      action: reviewForm.action,
      reviewer_note: reviewForm.reviewerNote.trim() || null,
    };

    if (reviewForm.action === "edit") {
      try {
        request.properties = parseJsonObject(reviewForm.propertiesText, "Properties");
        const normalizedConfidence = reviewForm.confidence.trim();
        if (normalizedConfidence) {
          request.confidence = Number(normalizedConfidence);
          if (Number.isNaN(request.confidence)) {
            throw new Error("Güven skoru geçerli bir sayı olmalı.");
          }
        }

        if (selectedReviewEntry.queueItem.candidate_node) {
          request.node_type = reviewForm.nodeType.trim();
          request.merge_key_payload = parseJsonObject(
            reviewForm.mergeKeyText,
            "Merge key payload",
          );
        }

        if (selectedReviewEntry.queueItem.candidate_relation) {
          request.relation_type = reviewForm.relationType.trim();
          request.from_candidate_ref = reviewForm.fromCandidateRef.trim();
          request.to_candidate_ref = reviewForm.toCandidateRef.trim();
        }
      } catch (error: unknown) {
        setReviewFormError(toErrorMessage(error));
        return;
      }
    }

    setReviewMutationState("submitting");
    setReviewFormError(null);
    setReviewMutationNotice(null);

    try {
      await decideReviewItem(selectedReviewEntry.queueItem.review_item.review_item_id, request);
      setReviewMutationNotice("Karar başarıyla kaydedildi.");
      setReviewQueueReloadToken((value) => value + 1);
    } catch (error: unknown) {
      setReviewFormError(toErrorMessage(error));
    } finally {
      setReviewMutationState("idle");
    }
  }

  function refreshWorkspace() {
    setReviewQueueReloadToken((value) => value + 1);
    setProcessingJobQueueReloadToken((value) => value + 1);
  }

  function refreshGraph() {
    setGraphReloadToken((value) => value + 1);
  }

  return (
    <main className="ops-shell">
      <aside className="ops-sidebar">
        <div className="panel sidebar-panel">
          <div className="sidebar-topline">Yönetim Paneli</div>
          <h1>GiraffeGraph Core</h1>
          <p className="sidebar-copy">
            Ham veriyi bilgi grafiğine dönüştüren iç yönetim paneli.
          </p>
          <dl className="sidebar-facts">
            <div>
              <dt>API</dt>
              <dd>{apiBaseUrl}</dd>
            </div>
            <div>
              <dt>Kapsam</dt>
              <dd>Çekirdek motor + iç panel</dd>
            </div>
            <div>
              <dt>İşlem hattı</dt>
              <dd>Aday → Doğrulama → Kesinleşme</dd>
            </div>
          </dl>
        </div>

        <div className="panel sidebar-panel project-panel">
          <div className="panel-header">
            <div>
              <p className="panel-eyebrow">Projeler</p>
              <h2>Çalışma alanları</h2>
            </div>
            <button
              className="ghost-button"
              type="button"
              onClick={() => {
                setReviewQueueReloadToken((value) => value + 1);
                setProcessingJobQueueReloadToken((value) => value + 1);
                setGraphReloadToken((value) => value + 1);
              }}
            >
              Yenile
            </button>
          </div>

          {projectsLoading ? (
            <div className="panel-empty">Projeler yükleniyor…</div>
          ) : projectsError ? (
            <div className="panel-empty error-state">{projectsError}</div>
          ) : projects.length === 0 ? (
            <div className="panel-empty">
              Henüz proje yok. Başlamak için API üzerinden bir proje oluşturun.
            </div>
          ) : (
            <div className="project-list">
              {projects.map((project) => {
                const isSelected = project.project_id === selectedProjectId;
                return (
                  <button
                    key={project.project_id}
                    type="button"
                    className={`project-card${isSelected ? " is-selected" : ""}`}
                    onClick={() => setSelectedProjectId(project.project_id)}
                  >
                    <div className="project-card-top">
                      <strong>{project.name}</strong>
                      <span
                        className={`tone-chip tone-${reviewStatusTone(project.status)}`}
                      >
                        {statusLabel(project.status)}
                      </span>
                    </div>
                    <p>{project.description ?? "Açıklama girilmemiş."}</p>
                    <div className="project-card-meta">
                      <span>{project.template_id ?? "şablonsuz"}</span>
                      <span>{formatDateTime(project.updated_at)}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        <div className="panel sidebar-panel compact-panel">
          <div className="panel-eyebrow">Temel İlkeler</div>
          <ul className="principle-list">
            <li>Alana özel kavramları çekirdeğe gömmekten kaçın.</li>
            <li>İnsan incelemesi adımını atlama.</li>
            <li>Şema ve grafik yazma kararlarını panelden takip et.</li>
          </ul>
        </div>
      </aside>

      <section className="ops-main">
        <header className="panel hero-panel">
          <div>
            <p className="panel-eyebrow">İşlem Merkezi</p>
            <h2>{selectedProject?.name ?? "Proje seçimi bekleniyor"}</h2>
            <p className="hero-copy">
              {selectedProject?.description ??
                "İnceleme kuyruğu ve grafik gezgini API üzerinden bağlandı."}
            </p>
          </div>

          <div className="hero-controls">
            <div className="segmented-control" role="tablist" aria-label="Dashboard views">
              <button
                type="button"
                className={activeView === "schema" ? "is-active" : ""}
                onClick={() => setActiveView("schema")}
              >
                Şema
              </button>
              <button
                type="button"
                className={activeView === "ingest" ? "is-active" : ""}
                onClick={() => setActiveView("ingest")}
              >
                Veri & Pipeline
              </button>
              <button
                type="button"
                className={activeView === "review" ? "is-active" : ""}
                onClick={() => setActiveView("review")}
              >
                İnceleme Kuyruğu
              </button>
              <button
                type="button"
                className={activeView === "operations" ? "is-active" : ""}
                onClick={() => setActiveView("operations")}
              >
                İşlemler
              </button>
              <button
                type="button"
                className={activeView === "graph" ? "is-active" : ""}
                onClick={() => setActiveView("graph")}
              >
                Grafik Gezgini
              </button>
            </div>

            <div className="hero-actions">
              <button className="ghost-button" type="button" onClick={refreshWorkspace}>
                Kuyruğu yenile
              </button>
              <button className="ghost-button" type="button" onClick={refreshGraph}>
                Grafiği yenile
              </button>
            </div>
          </div>
        </header>

        <PipelineSteps
          activeStep={
            activeView === "graph" ? 6 :
            activeView === "operations" ? 3 :
            4
          }
        />

        <section className="metric-strip">
          <article className="metric-card">
            <span>Bekleyen incelemeler</span>
            <strong>{reviewQueue?.open_review_count ?? "—"}</strong>
          </article>
          <article className="metric-card">
            <span>Toplam inceleme</span>
            <strong>{reviewQueue?.total_review_count ?? "—"}</strong>
          </article>
          <article className="metric-card">
            <span>Aktif işler</span>
            <strong>{processingJobQueue?.active_job_count ?? "—"}</strong>
          </article>
          <article className="metric-card">
            <span>Başarısız işler</span>
            <strong>{processingJobQueue?.failed_job_count ?? "—"}</strong>
          </article>
          <article className="metric-card">
            <span>Kesinleşen düğümler</span>
            <strong>{graphSnapshot?.overview.node_count ?? "—"}</strong>
          </article>
          <article className="metric-card">
            <span>Kesinleşen ilişkiler</span>
            <strong>{graphSnapshot?.overview.relation_count ?? "—"}</strong>
          </article>
        </section>

        {!selectedProjectId ? (
          <section className="panel empty-stage">
            Devam etmek için sol panelden bir proje seçin.
          </section>
        ) : activeView === "schema" ? (
          <SchemaTab project={projects.find((p) => p.project_id === selectedProjectId)!} />
        ) : activeView === "ingest" ? (
          <PipelineTab project={projects.find((p) => p.project_id === selectedProjectId)!} />
        ) : activeView === "review" ? (
          <section className="content-grid review-grid">
            <div className="panel review-list-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-eyebrow">İnceleme Kuyruğu</p>
                  <h3>Çalıştırma bazlı karar akışı</h3>
                </div>
                <span className="subtle-copy">
                  {reviewQueue
                    ? `${reviewQueue.returned_run_count}/${reviewQueue.filtered_run_count} run`
                    : "0/0 run"}
                </span>
              </div>

              <div className="field-grid">
                <label className="field">
                  <span>Kuyruk durumu</span>
                  <select
                    value={reviewStatusFilter}
                    onChange={(event) =>
                      setReviewStatusFilter(
                        event.currentTarget.value as ReviewQueueStatusFilter,
                      )
                    }
                  >
                    <option value="open">Yalnızca bekleyenler</option>
                    <option value="all">Tüm geçmiş</option>
                    <option value="closed">Yalnızca kapatılanlar</option>
                  </select>
                </label>

                <label className="field">
                  <span>Çalıştırma limiti</span>
                  <select
                    value={String(reviewRunLimit)}
                    onChange={(event) =>
                      setReviewRunLimit(Number(event.currentTarget.value))
                    }
                  >
                    {RUN_LIMIT_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        Son {option} çalıştırma
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              {reviewQueueLoading ? (
                <div className="panel-empty">İnceleme kuyruğu yükleniyor…</div>
              ) : reviewQueueError ? (
                <div className="panel-empty error-state">{reviewQueueError}</div>
              ) : !reviewQueue || reviewQueue.run_entries.length === 0 ? (
                <div className="panel-empty">Bu proje için çalıştırma kaydı bulunamadı.</div>
              ) : (
                <div className="run-stack">
                  {reviewQueue.has_more_runs ? (
                    <div className="mini-empty">
                      Gösterilenden daha fazla çalıştırma var. Şu anki limit: {reviewQueue.run_limit}.
                    </div>
                  ) : null}
                  {reviewQueue.run_entries.map((runEntry) => (
                    <section key={runEntry.run.run_id} className="run-cluster">
                      <div className="run-cluster-header">
                        <div>
                          <div className="run-title">
                            {runEntry.source_unit.title}
                            <span
                              className={`tone-chip tone-${reviewStatusTone(
                                runEntry.run.status,
                              )}`}
                            >
                              {statusLabel(runEntry.run.status)}
                            </span>
                          </div>
                          <div className="run-meta">
                            <span>#{formatShortId(runEntry.run.run_id)}</span>
                            <span>{runEntry.source_unit.source_type}</span>
                            <span>{runEntry.run.pipeline_version}</span>
                          </div>
                        </div>
                        <div className="run-counts">
                          <strong>{runEntry.open_review_count}</strong>
                          <span>bekleyen / {runEntry.total_review_count} toplam</span>
                        </div>
                      </div>

                      {runEntry.review_items.length === 0 ? (
                        <div className="mini-empty">
                          Bu çalıştırmada inceleme gerektiren öğe yok. Temiz akış.
                        </div>
                      ) : (
                        <div className="review-item-list">
                          {reviewEntries
                            .filter(
                              (entry) => entry.runEntry.run.run_id === runEntry.run.run_id,
                            )
                            .map((entry) => {
                              const isSelected =
                                entry.queueItem.review_item.review_item_id ===
                                selectedReviewId;
                              return (
                                <button
                                  key={entry.queueItem.review_item.review_item_id}
                                  type="button"
                                  className={`review-card${isSelected ? " is-selected" : ""}`}
                                  onClick={() =>
                                    setSelectedReviewId(
                                      entry.queueItem.review_item.review_item_id,
                                    )
                                  }
                                >
                                  <div className="review-card-top">
                                    <strong>{entry.queueItem.headline}</strong>
                                    <span
                                      className={`tone-chip tone-${reviewStatusTone(
                                        entry.queueItem.review_item.status,
                                      )}`}
                                    >
                                      {statusLabel(entry.queueItem.review_item.status)}
                                    </span>
                                  </div>
                                  <p>{entry.queueItem.review_item.reason_code}</p>
                                  <div className="review-card-meta">
                                    <span>
                                      güven:{" "}
                                      {entry.queueItem.confidence !== null
                                        ? entry.queueItem.confidence.toFixed(2)
                                        : "—"}
                                    </span>
                                    <span>
                                      {formatDateTime(
                                        entry.queueItem.review_item.created_at,
                                      )}
                                    </span>
                                  </div>
                                </button>
                              );
                            })}
                        </div>
                      )}
                    </section>
                  ))}
                </div>
              )}
            </div>

            <div className="panel review-detail-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-eyebrow">Karar Paneli</p>
                  <h3>Seçili inceleme öğesi</h3>
                </div>
                {selectedReviewEntry ? (
                  <span className="subtle-copy">
                    {selectedReviewEntry.queueItem.review_item.item_type}
                  </span>
                ) : null}
              </div>

              {!selectedReviewEntry ? (
                <div className="panel-empty">
                  İncelemek için soldan bir öğe seçin.
                </div>
              ) : (
                <div className="detail-stack">
                  <section className="detail-block">
                    <div className="detail-title-row">
                      <h4>{selectedReviewEntry.queueItem.headline}</h4>
                      <span
                        className={`tone-chip tone-${reviewStatusTone(
                          selectedReviewEntry.queueItem.review_item.status,
                        )}`}
                      >
                        {statusLabel(selectedReviewEntry.queueItem.review_item.status)}
                      </span>
                    </div>
                    <p className="detail-copy">
                      neden:{" "}
                      <code>{selectedReviewEntry.queueItem.review_item.reason_code}</code>
                    </p>
                    <div className="definition-grid">
                      <div>
                        <span>Çalıştırma</span>
                        <strong>
                          {selectedReviewEntry.runEntry.source_unit.title} · #
                          {formatShortId(selectedReviewEntry.runEntry.run.run_id)}
                        </strong>
                      </div>
                      <div>
                        <span>Kaynak durumu</span>
                        <strong>
                          {statusLabel(selectedReviewEntry.runEntry.source_unit.status)}
                        </strong>
                      </div>
                      <div>
                        <span>Güven skoru</span>
                        <strong>
                          {selectedReviewEntry.queueItem.confidence !== null
                            ? selectedReviewEntry.queueItem.confidence.toFixed(2)
                            : "N/A"}
                        </strong>
                      </div>
                      <div>
                        <span>Oluşturulma</span>
                        <strong>
                          {formatDateTime(
                            selectedReviewEntry.queueItem.review_item.created_at,
                          )}
                        </strong>
                      </div>
                    </div>
                  </section>

                  <section className="detail-block">
                    <h4>Doğrulama mesajları</h4>
                    {selectedReviewEntry.queueItem.messages.length === 0 ? (
                      <div className="mini-empty">Ek mesaj yok.</div>
                    ) : (
                      <ul className="message-list">
                        {selectedReviewEntry.queueItem.messages.map((message) => (
                          <li key={message}>{message}</li>
                        ))}
                      </ul>
                    )}
                  </section>

                  <section className="detail-block">
                    <h4>Aday verisi</h4>
                    <pre className="json-block">
                      {selectedReviewEntry.queueItem.candidate_node
                        ? stringifyPretty({
                            node_type: selectedReviewEntry.queueItem.candidate_node.node_type,
                            status: selectedReviewEntry.queueItem.candidate_node.status,
                            properties: selectedReviewEntry.queueItem.candidate_node.properties,
                            merge_key_payload:
                              selectedReviewEntry.queueItem.candidate_node
                                .merge_key_payload,
                          })
                        : selectedReviewEntry.queueItem.candidate_relation
                          ? stringifyPretty({
                              relation_type:
                                selectedReviewEntry.queueItem.candidate_relation
                                  .relation_type,
                              status: selectedReviewEntry.queueItem.candidate_relation.status,
                              from_candidate_ref:
                                selectedReviewEntry.queueItem.candidate_relation
                                  .from_candidate_ref,
                              to_candidate_ref:
                                selectedReviewEntry.queueItem.candidate_relation
                                  .to_candidate_ref,
                              properties:
                                selectedReviewEntry.queueItem.candidate_relation.properties,
                            })
                          : stringifyPretty(
                              selectedReviewEntry.queueItem.review_item.payload_json,
                            )}
                    </pre>
                  </section>

                  <section className="detail-block">
                    <h4>Kanıt parçaları</h4>
                    {selectedReviewEntry.queueItem.evidence_snippets.length === 0 ? (
                      <div className="mini-empty">Bu öğe için kanıt parçası yok.</div>
                    ) : (
                      <div className="evidence-list">
                        {selectedReviewEntry.queueItem.evidence_snippets.map((snippet) => (
                          <article
                            key={`${snippet.segment_id}-${snippet.segment_order ?? "na"}`}
                            className="evidence-card"
                          >
                            <header>
                              <span>segment #{snippet.segment_order ?? "?"}</span>
                              <code>{formatShortId(snippet.segment_id)}</code>
                            </header>
                            <p>{snippet.quote ?? snippet.text ?? "Metin bulunamadı."}</p>
                          </article>
                        ))}
                      </div>
                    )}
                  </section>

                  <section className="detail-block">
                    <div className="detail-title-row">
                      <h4>Karar formu</h4>
                      {selectedReviewEntry.queueItem.review_item.status !== "open" ? (
                        <span className="subtle-copy">Kapatılmış</span>
                      ) : null}
                    </div>

                    <form className="decision-form" onSubmit={submitReviewDecision}>
                      <div className="segmented-control action-picker" aria-label="Review action">
                        {(["accept", "reject", "edit"] as ReviewAction[]).map((action) => (
                          <button
                            key={action}
                            type="button"
                            className={reviewForm.action === action ? "is-active" : ""}
                            disabled={
                              selectedReviewEntry.queueItem.review_item.status !== "open"
                            }
                            onClick={() =>
                              setReviewForm((current) => ({ ...current, action }))
                            }
                          >
                            {action}
                          </button>
                        ))}
                      </div>

                      <label className="field">
                        <span>İnceleme notu</span>
                        <textarea
                          rows={3}
                          value={reviewForm.reviewerNote}
                          disabled={
                            selectedReviewEntry.queueItem.review_item.status !== "open"
                          }
                          onChange={(event) =>
                            setReviewForm((current) => ({
                              ...current,
                              reviewerNote: event.currentTarget.value,
                            }))
                          }
                        />
                      </label>

                      <div className="field-grid">
                        {selectedReviewEntry.queueItem.candidate_node ? (
                          <>
                            <label className="field">
                              <span>Düğüm tipi</span>
                              <input
                                type="text"
                                value={reviewForm.nodeType}
                                disabled={
                                  selectedReviewEntry.queueItem.review_item.status !==
                                    "open" ||
                                  reviewForm.action !== "edit"
                                }
                                onChange={(event) =>
                                  setReviewForm((current) => ({
                                    ...current,
                                    nodeType: event.currentTarget.value,
                                  }))
                                }
                              />
                            </label>
                            <label className="field">
                              <span>Güven skoru</span>
                              <input
                                type="text"
                                value={reviewForm.confidence}
                                disabled={
                                  selectedReviewEntry.queueItem.review_item.status !==
                                    "open" ||
                                  reviewForm.action !== "edit"
                                }
                                onChange={(event) =>
                                  setReviewForm((current) => ({
                                    ...current,
                                    confidence: event.currentTarget.value,
                                  }))
                                }
                              />
                            </label>
                          </>
                        ) : null}

                        {selectedReviewEntry.queueItem.candidate_relation ? (
                          <>
                            <label className="field">
                              <span>İlişki tipi</span>
                              <input
                                type="text"
                                value={reviewForm.relationType}
                                disabled={
                                  selectedReviewEntry.queueItem.review_item.status !==
                                    "open" ||
                                  reviewForm.action !== "edit"
                                }
                                onChange={(event) =>
                                  setReviewForm((current) => ({
                                    ...current,
                                    relationType: event.currentTarget.value,
                                  }))
                                }
                              />
                            </label>
                            <label className="field">
                              <span>Güven skoru</span>
                              <input
                                type="text"
                                value={reviewForm.confidence}
                                disabled={
                                  selectedReviewEntry.queueItem.review_item.status !==
                                    "open" ||
                                  reviewForm.action !== "edit"
                                }
                                onChange={(event) =>
                                  setReviewForm((current) => ({
                                    ...current,
                                    confidence: event.currentTarget.value,
                                  }))
                                }
                              />
                            </label>
                            <label className="field">
                              <span>Kaynak aday ref</span>
                              <input
                                type="text"
                                value={reviewForm.fromCandidateRef}
                                disabled={
                                  selectedReviewEntry.queueItem.review_item.status !==
                                    "open" ||
                                  reviewForm.action !== "edit"
                                }
                                onChange={(event) =>
                                  setReviewForm((current) => ({
                                    ...current,
                                    fromCandidateRef: event.currentTarget.value,
                                  }))
                                }
                              />
                            </label>
                            <label className="field">
                              <span>Hedef aday ref</span>
                              <input
                                type="text"
                                value={reviewForm.toCandidateRef}
                                disabled={
                                  selectedReviewEntry.queueItem.review_item.status !==
                                    "open" ||
                                  reviewForm.action !== "edit"
                                }
                                onChange={(event) =>
                                  setReviewForm((current) => ({
                                    ...current,
                                    toCandidateRef: event.currentTarget.value,
                                  }))
                                }
                              />
                            </label>
                          </>
                        ) : null}
                      </div>

                      <label className="field">
                        <span>Özellikler (JSON)</span>
                        <textarea
                          rows={6}
                          className="code-area"
                          value={reviewForm.propertiesText}
                          disabled={
                            selectedReviewEntry.queueItem.review_item.status !== "open" ||
                            reviewForm.action !== "edit"
                          }
                          onChange={(event) =>
                            setReviewForm((current) => ({
                              ...current,
                              propertiesText: event.currentTarget.value,
                            }))
                          }
                        />
                      </label>

                      {selectedReviewEntry.queueItem.candidate_node ? (
                        <label className="field">
                          <span>Birleştirme anahtarı (JSON)</span>
                          <textarea
                            rows={5}
                            className="code-area"
                            value={reviewForm.mergeKeyText}
                            disabled={
                              selectedReviewEntry.queueItem.review_item.status !== "open" ||
                              reviewForm.action !== "edit"
                            }
                            onChange={(event) =>
                              setReviewForm((current) => ({
                                ...current,
                                mergeKeyText: event.currentTarget.value,
                              }))
                            }
                          />
                        </label>
                      ) : null}

                      {reviewFormError ? (
                        <div className="form-feedback error-state">{reviewFormError}</div>
                      ) : null}
                      {reviewMutationNotice ? (
                        <div className="form-feedback success-state">
                          {reviewMutationNotice}
                        </div>
                      ) : null}

                      <div className="form-actions">
                        <button
                          className="primary-button"
                          type="submit"
                          disabled={
                            selectedReviewEntry.queueItem.review_item.status !== "open" ||
                            reviewMutationState === "submitting"
                          }
                        >
                          {reviewMutationState === "submitting"
                            ? "Kaydediliyor…"
                            : "Kararı uygula"}
                        </button>
                      </div>
                    </form>
                  </section>
                </div>
              )}
            </div>
          </section>
        ) : activeView === "operations" ? (
          <section className="content-grid review-grid">
            <div className="panel review-list-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-eyebrow">İşlem Kuyruğu</p>
                  <h3>İş durumu ve takibi</h3>
                </div>
                <span className="subtle-copy">
                  {processingJobQueue
                    ? `${processingJobQueue.returned_run_count}/${processingJobQueue.filtered_run_count} run`
                    : "0/0 run"}
                </span>
              </div>

              <div className="field-grid">
                <label className="field">
                  <span>İş durumu</span>
                  <select
                    value={processingJobStatusFilter}
                    onChange={(event) =>
                      setProcessingJobStatusFilter(
                        event.currentTarget.value as ProcessingJobQueueStatusFilter,
                      )
                    }
                  >
                    <option value="active">Aktif</option>
                    <option value="failed">Başarısız</option>
                    <option value="succeeded">Tamamlanan</option>
                    <option value="all">Tüm geçmiş</option>
                  </select>
                </label>

                <label className="field">
                  <span>Çalıştırma limiti</span>
                  <select
                    value={String(processingJobRunLimit)}
                    onChange={(event) =>
                      setProcessingJobRunLimit(Number(event.currentTarget.value))
                    }
                  >
                    {RUN_LIMIT_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        Son {option} çalıştırma
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              {processingJobQueueLoading ? (
                <div className="panel-empty">İşlem kuyruğu yükleniyor…</div>
              ) : processingJobQueueError ? (
                <div className="panel-empty error-state">{processingJobQueueError}</div>
              ) : !processingJobQueue || processingJobQueue.run_entries.length === 0 ? (
                <div className="panel-empty">Bu filtre için iş kaydı bulunamadı.</div>
              ) : (
                <div className="run-stack">
                  {processingJobQueue.has_more_runs ? (
                    <div className="mini-empty">
                      Gösterilenden daha fazla çalıştırma var. Şu anki limit:{" "}
                      {processingJobQueue.run_limit}.
                    </div>
                  ) : null}
                  {processingJobQueue.run_entries.map((runEntry) => (
                    <section key={runEntry.run.run_id} className="run-cluster">
                      <div className="run-cluster-header">
                        <div>
                          <div className="run-title">
                            {runEntry.source_unit.title}
                            <span
                              className={`tone-chip tone-${reviewStatusTone(
                                runEntry.run.status,
                              )}`}
                            >
                              {statusLabel(runEntry.run.status)}
                            </span>
                          </div>
                          <div className="run-meta">
                            <span>#{formatShortId(runEntry.run.run_id)}</span>
                            <span>{runEntry.source_unit.source_type}</span>
                            <span>{runEntry.run.pipeline_version}</span>
                          </div>
                        </div>
                        <div className="run-counts">
                          <strong>{runEntry.active_job_count}</strong>
                          <span>
                            aktif / {runEntry.failed_job_count} başarısız /{" "}
                            {runEntry.total_job_count} toplam
                          </span>
                        </div>
                      </div>

                      {runEntry.jobs.length === 0 ? (
                        <div className="mini-empty">
                          Bu çalıştırmada filtreyle eşleşen iş yok.
                        </div>
                      ) : (
                        <div className="review-item-list">
                          {processingJobEntries
                            .filter((entry) => entry.runEntry.run.run_id === runEntry.run.run_id)
                            .map((entry) => {
                              const isSelected = entry.job.job_id === selectedProcessingJobId;
                              return (
                                <button
                                  key={entry.job.job_id}
                                  type="button"
                                  className={`review-card${isSelected ? " is-selected" : ""}`}
                                  onClick={() => setSelectedProcessingJobId(entry.job.job_id)}
                                >
                                  <div className="review-card-top">
                                    <strong>{entry.job.job_type}</strong>
                                    <span
                                      className={`tone-chip tone-${reviewStatusTone(
                                        entry.job.status,
                                      )}`}
                                    >
                                      {statusLabel(entry.job.status)}
                                    </span>
                                  </div>
                                  <p>
                                    {entry.job.error_message ??
                                      `deneme ${entry.job.attempt_count} · ${formatDateTime(
                                        entry.job.created_at,
                                      )}`}
                                  </p>
                                  <div className="review-card-meta">
                                    <span>job #{formatShortId(entry.job.job_id)}</span>
                                    <span>{formatDateTime(entry.job.completed_at)}</span>
                                  </div>
                                </button>
                              );
                            })}
                        </div>
                      )}
                    </section>
                  ))}
                </div>
              )}
            </div>

            <div className="panel review-detail-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-eyebrow">İş Detayı</p>
                  <h3>Seçili iş kaydı</h3>
                </div>
                {selectedProcessingJobEntry ? (
                  <span className="subtle-copy">
                    {selectedProcessingJobEntry.job.job_type}
                  </span>
                ) : null}
              </div>

              {!selectedProcessingJobEntry ? (
                <div className="panel-empty">
                  İncelemek için soldan bir iş kaydı seçin.
                </div>
              ) : (
                <div className="detail-stack">
                  <section className="detail-block">
                    <div className="detail-title-row">
                      <h4>{selectedProcessingJobEntry.job.job_type}</h4>
                      <span
                        className={`tone-chip tone-${reviewStatusTone(
                          selectedProcessingJobEntry.job.status,
                        )}`}
                      >
                        {statusLabel(selectedProcessingJobEntry.job.status)}
                      </span>
                    </div>
                    <div className="definition-grid">
                      <div>
                        <span>Çalıştırma</span>
                        <strong>
                          {selectedProcessingJobEntry.runEntry.source_unit.title} · #
                          {formatShortId(selectedProcessingJobEntry.runEntry.run.run_id)}
                        </strong>
                      </div>
                      <div>
                        <span>İş ID</span>
                        <strong>{selectedProcessingJobEntry.job.job_id}</strong>
                      </div>
                      <div>
                        <span>Deneme sayısı</span>
                        <strong>{selectedProcessingJobEntry.job.attempt_count}</strong>
                      </div>
                      <div>
                        <span>Oluşturulma</span>
                        <strong>{formatDateTime(selectedProcessingJobEntry.job.created_at)}</strong>
                      </div>
                      <div>
                        <span>Başlama</span>
                        <strong>{formatDateTime(selectedProcessingJobEntry.job.started_at)}</strong>
                      </div>
                      <div>
                        <span>Tamamlanma</span>
                        <strong>
                          {formatDateTime(selectedProcessingJobEntry.job.completed_at)}
                        </strong>
                      </div>
                    </div>
                  </section>

                  <section className="detail-block">
                    <h4>Giriş verisi</h4>
                    <pre className="json-block">
                      {stringifyPretty(selectedProcessingJobEntry.job.payload_json)}
                    </pre>
                  </section>

                  <section className="detail-block">
                    <h4>Çıktı</h4>
                    <pre className="json-block">
                      {stringifyPretty(selectedProcessingJobEntry.job.output_json)}
                    </pre>
                  </section>

                  <section className="detail-block">
                    <h4>Hata</h4>
                    {selectedProcessingJobEntry.job.error_message ? (
                      <div className="form-feedback error-state">
                        {selectedProcessingJobEntry.job.error_message}
                      </div>
                    ) : (
                      <div className="mini-empty">Bu iş için hata kaydı yok.</div>
                    )}
                  </section>
                </div>
              )}
            </div>
          </section>
        ) : (
          <section className="content-grid graph-grid">
            <div className="panel graph-summary-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-eyebrow">Grafik Özeti</p>
                  <h3>Kesinleşmiş veri genel bakış</h3>
                </div>
                <span className="subtle-copy">limit {GRAPH_LIMIT}</span>
              </div>

              {graphLoading ? (
                <div className="panel-empty">Grafik verisi yükleniyor…</div>
              ) : graphError ? (
                <div className="panel-empty error-state">{graphError}</div>
              ) : !graphSnapshot ? (
                <div className="panel-empty">Grafik verisi okunamadı.</div>
              ) : (
                <div className="detail-stack">
                  <section className="graph-overview-grid">
                    <article>
                      <span>Toplam düğüm</span>
                      <strong>{graphSnapshot.overview.node_count}</strong>
                    </article>
                    <article>
                      <span>Toplam ilişki</span>
                      <strong>{graphSnapshot.overview.relation_count}</strong>
                    </article>
                    <article>
                      <span>Yüklenen düğüm</span>
                      <strong>{graphSnapshot.nodes.length}</strong>
                    </article>
                    <article>
                      <span>Yüklenen ilişki</span>
                      <strong>{graphSnapshot.relations.length}</strong>
                    </article>
                  </section>

                  <section className="detail-block">
                    <h4>Filtreler</h4>
                    <div className="field-grid">
                      <label className="field">
                        <span>Düğüm tipi</span>
                        <select
                          value={nodeTypeFilter}
                          onChange={(event) => setNodeTypeFilter(event.currentTarget.value)}
                        >
                          <option value="">Tüm düğüm tipleri</option>
                          {graphSnapshot.overview.node_type_counts.map((item) => (
                            <option key={item.node_type} value={item.node_type}>
                              {item.node_type} ({item.count})
                            </option>
                          ))}
                        </select>
                      </label>

                      <label className="field">
                        <span>İlişki tipi</span>
                        <select
                          value={relationTypeFilter}
                          onChange={(event) =>
                            setRelationTypeFilter(event.currentTarget.value)
                          }
                        >
                          <option value="">Tüm ilişki tipleri</option>
                          {relationTypeOptions.map((item) => (
                            <option key={item} value={item}>
                              {item}
                            </option>
                          ))}
                        </select>
                      </label>
                    </div>
                  </section>

                  <section className="detail-block">
                    <h4>Düğüm tipi dağılımı</h4>
                    <div className="distribution-list">
                      {graphSnapshot.overview.node_type_counts.length === 0 ? (
                        <div className="mini-empty">Henüz kesinleşmiş düğüm yok.</div>
                      ) : (
                        graphSnapshot.overview.node_type_counts.map((item) => (
                          <div key={item.node_type} className="distribution-row">
                            <span>{item.node_type}</span>
                            <strong>{item.count}</strong>
                          </div>
                        ))
                      )}
                    </div>
                  </section>
                </div>
              )}
            </div>

            <div className="panel graph-list-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-eyebrow">Gezgin</p>
                  <h3>Düğüm ve ilişki listeleri</h3>
                </div>
                <span className="subtle-copy">Güncel durum</span>
              </div>

              {graphLoading ? (
                <div className="panel-empty">Grafik listeleri yükleniyor…</div>
              ) : graphError ? (
                <div className="panel-empty error-state">{graphError}</div>
              ) : !graphSnapshot ? (
                <div className="panel-empty">Grafik verisi yok.</div>
              ) : (
                <div className="graph-columns">
                  <section className="graph-column">
                    <div className="column-heading">Düğümler</div>
                    <div className="graph-record-list">
                      {graphSnapshot.nodes.length === 0 ? (
                        <div className="mini-empty">Filtreyle eşleşen düğüm yok.</div>
                      ) : (
                        graphSnapshot.nodes.map((node) => {
                          const isSelected =
                            graphSelection?.kind === "node" &&
                            graphSelection.key === nodeKey(node);
                          const primary = getPrimaryProperty(node.properties);
                          return (
                            <button
                              key={nodeKey(node)}
                              type="button"
                              className={`graph-record${isSelected ? " is-selected" : ""}`}
                              onClick={() =>
                                setGraphSelection({
                                  kind: "node",
                                  key: nodeKey(node),
                                })
                              }
                            >
                              <div className="graph-record-top">
                                <strong>{describeCanonicalNode(node)}</strong>
                                <span>{node.node_type}</span>
                              </div>
                              <p>
                                {primary
                                  ? `${primary[0]}: ${primary[1]}`
                                  : "Birincil özellik yok."}
                              </p>
                              <div className="graph-record-meta">
                                <span>{formatDateTime(node.updated_at)}</span>
                              </div>
                            </button>
                          );
                        })
                      )}
                    </div>
                  </section>

                  <section className="graph-column">
                    <div className="column-heading">İlişkiler</div>
                    <div className="graph-record-list">
                      {graphSnapshot.relations.length === 0 ? (
                        <div className="mini-empty">Filtreyle eşleşen ilişki yok.</div>
                      ) : (
                        graphSnapshot.relations.map((relation) => {
                          const isSelected =
                            graphSelection?.kind === "relation" &&
                            graphSelection.key === relationKey(relation);
                          const fromLabel =
                            canonicalNodeLabelMap.get(
                              `${relation.from_node_type}::${relation.from_merge_key}`,
                            ) ?? `${relation.from_node_type} · ${relation.from_merge_key.slice(0, 10)}`;
                          const toLabel =
                            canonicalNodeLabelMap.get(
                              `${relation.to_node_type}::${relation.to_merge_key}`,
                            ) ?? `${relation.to_node_type} · ${relation.to_merge_key.slice(0, 10)}`;
                          return (
                            <button
                              key={relationKey(relation)}
                              type="button"
                              className={`graph-record${isSelected ? " is-selected" : ""}`}
                              onClick={() =>
                                setGraphSelection({
                                  kind: "relation",
                                  key: relationKey(relation),
                                })
                              }
                            >
                              <div className="graph-record-top">
                                <strong>{relation.relation_type}</strong>
                                <span>{formatDateTime(relation.updated_at)}</span>
                              </div>
                              <p>
                                {fromLabel} → {toLabel}
                              </p>
                              <div className="graph-record-meta">
                                <span>{Object.keys(relation.properties).length} özellik</span>
                              </div>
                            </button>
                          );
                        })
                      )}
                    </div>
                  </section>
                </div>
              )}
            </div>

            <div className="panel graph-detail-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-eyebrow">Seçili Kayıt</p>
                  <h3>Detay görünümü</h3>
                </div>
                {selectedNodeDetail ? (
                  <span className="subtle-copy">düğüm</span>
                ) : selectedRelationDetail ? (
                  <span className="subtle-copy">ilişki</span>
                ) : null}
              </div>

              {graphDetailLoading ? (
                <div className="panel-empty">Detay yükleniyor…</div>
              ) : graphDetailError ? (
                <div className="panel-empty error-state">{graphDetailError}</div>
              ) : selectedNodeDetail ? (
                <div className="detail-stack">
                  <section className="detail-block">
                    <div className="detail-title-row">
                      <h4>{describeCanonicalNode(selectedNodeDetail.node)}</h4>
                      <span className="tone-chip tone-success">
                        {selectedNodeDetail.node.node_type}
                      </span>
                    </div>
                    <div className="definition-grid">
                      <div>
                        <span>Birleştirme anahtarı</span>
                        <strong>{selectedNodeDetail.node.merge_key}</strong>
                      </div>
                      <div>
                        <span>Son çalıştırma</span>
                        <strong>{selectedNodeDetail.node.last_run_id ?? "N/A"}</strong>
                      </div>
                      <div>
                        <span>Kaynak birim</span>
                        <strong>{selectedNodeDetail.node.source_unit_id ?? "N/A"}</strong>
                      </div>
                      <div>
                        <span>Güncellenme</span>
                        <strong>{formatDateTime(selectedNodeDetail.node.updated_at)}</strong>
                      </div>
                    </div>
                  </section>
                  <section className="detail-block">
                    <h4>Özellikler</h4>
                    <pre className="json-block">
                      {stringifyPretty(selectedNodeDetail.node.properties)}
                    </pre>
                  </section>

                  <section className="detail-block">
                    <h4>Kaynak birimler</h4>
                    {selectedNodeDetail.source_units.length === 0 ? (
                      <div className="mini-empty">Bu düğüm için kaynak birim bulunamadı.</div>
                    ) : (
                      <div className="distribution-list">
                        {selectedNodeDetail.source_units.map((sourceUnit) => (
                          <div key={sourceUnit.source_unit_id} className="distribution-row">
                            <span>
                              {sourceUnit.title ?? sourceUnit.source_unit_id} ·{" "}
                              {sourceUnit.source_type ?? "unknown"}
                            </span>
                            <strong>
                              sıra {sourceUnit.sequence_no ?? "N/A"}
                            </strong>
                          </div>
                        ))}
                      </div>
                    )}
                  </section>

                  <section className="detail-block">
                    <h4>Destekleyici parçalar</h4>
                    {selectedNodeDetail.supporting_segments.length === 0 ? (
                      <div className="mini-empty">Destekleyici parça yok.</div>
                    ) : (
                      <div className="evidence-list">
                        {selectedNodeDetail.supporting_segments.map((segment) => (
                          <article key={segment.segment_id} className="evidence-card">
                            <header>
                              <span>segment #{segment.segment_order ?? "?"}</span>
                              <code>{formatShortId(segment.segment_id)}</code>
                            </header>
                            <p>{segment.text}</p>
                          </article>
                        ))}
                      </div>
                    )}
                  </section>

                  <section className="detail-block">
                    <h4>Bağlı ilişkiler</h4>
                    {selectedNodeDetail.connected_relations.length === 0 ? (
                      <div className="mini-empty">Bu düğüme bağlı ilişki yok.</div>
                    ) : (
                      <div className="graph-record-list">
                        {selectedNodeDetail.connected_relations.map((relation) => (
                          <article
                            key={[
                              relation.direction,
                              relation.relation_type,
                              relation.other_node_type,
                              relation.other_merge_key,
                            ].join("::")}
                            className="graph-record"
                          >
                            <div className="graph-record-top">
                              <strong>
                                {relation.relation_type} · {relation.direction}
                              </strong>
                              <span>{formatDateTime(relation.updated_at)}</span>
                            </div>
                            <p>
                              {relation.other_node_type} ·{" "}
                              {formatValue(
                                getPrimaryProperty(relation.other_node_properties)?.[1] ??
                                  relation.other_merge_key.slice(0, 10),
                              )}
                            </p>
                            <div className="graph-record-meta">
                              <span>
                                {Object.keys(relation.properties).length} ilişki özelliği
                              </span>
                            </div>
                          </article>
                        ))}
                      </div>
                    )}
                  </section>
                </div>
              ) : selectedRelationDetail ? (
                <div className="detail-stack">
                  <section className="detail-block">
                    <div className="detail-title-row">
                      <h4>{selectedRelationDetail.relation.relation_type}</h4>
                      <span className="tone-chip tone-warning">ilişki</span>
                    </div>
                    <div className="definition-grid">
                      <div>
                        <span>Kaynak</span>
                        <strong>
                          {selectedRelationDetail.from_node.node_type} ·{" "}
                          {getPrimaryProperty(selectedRelationDetail.from_node.properties)?.[1] ??
                            selectedRelationDetail.from_node.merge_key}
                        </strong>
                      </div>
                      <div>
                        <span>Hedef</span>
                        <strong>
                          {selectedRelationDetail.to_node.node_type} ·{" "}
                          {getPrimaryProperty(selectedRelationDetail.to_node.properties)?.[1] ??
                            selectedRelationDetail.to_node.merge_key}
                        </strong>
                      </div>
                      <div>
                        <span>Son çalıştırma</span>
                        <strong>{selectedRelationDetail.relation.last_run_id ?? "N/A"}</strong>
                      </div>
                      <div>
                        <span>Güncellenme</span>
                        <strong>
                          {formatDateTime(selectedRelationDetail.relation.updated_at)}
                        </strong>
                      </div>
                    </div>
                  </section>
                  <section className="detail-block">
                    <h4>Özellikler</h4>
                    <pre className="json-block">
                      {stringifyPretty(selectedRelationDetail.relation.properties)}
                    </pre>
                  </section>

                  <section className="detail-block">
                    <h4>Uç nokta verileri</h4>
                    <div className="field-grid">
                      <pre className="json-block">
                        {stringifyPretty(selectedRelationDetail.from_node.properties)}
                      </pre>
                      <pre className="json-block">
                        {stringifyPretty(selectedRelationDetail.to_node.properties)}
                      </pre>
                    </div>
                  </section>

                  <section className="detail-block">
                    <h4>Kaynak birimler</h4>
                    {selectedRelationDetail.source_units.length === 0 ? (
                      <div className="mini-empty">
                        Bu ilişki için kaynak birim bulunamadı.
                      </div>
                    ) : (
                      <div className="distribution-list">
                        {selectedRelationDetail.source_units.map((sourceUnit) => (
                          <div key={sourceUnit.source_unit_id} className="distribution-row">
                            <span>
                              {sourceUnit.title ?? sourceUnit.source_unit_id} ·{" "}
                              {sourceUnit.source_type ?? "unknown"}
                            </span>
                            <strong>
                              sıra {sourceUnit.sequence_no ?? "N/A"}
                            </strong>
                          </div>
                        ))}
                      </div>
                    )}
                  </section>

                  <section className="detail-block">
                    <h4>Destekleyici parçalar</h4>
                    {selectedRelationDetail.supporting_segments.length === 0 ? (
                      <div className="mini-empty">Bu ilişki için destekleyici parça yok.</div>
                    ) : (
                      <div className="evidence-list">
                        {selectedRelationDetail.supporting_segments.map((segment) => (
                          <article key={segment.segment_id} className="evidence-card">
                            <header>
                              <span>segment #{segment.segment_order ?? "?"}</span>
                              <code>{formatShortId(segment.segment_id)}</code>
                            </header>
                            <p>{segment.text}</p>
                          </article>
                        ))}
                      </div>
                    )}
                  </section>
                </div>
              ) : (
                <div className="panel-empty">Düğüm veya ilişki seçilmedi.</div>
              )}
            </div>
          </section>
        )}
      </section>
    </main>
  );
}

const PIPELINE_STEPS = [
  {
    label: "Şema Tasarımı",
    desc: "Düğüm tiplerini, ilişkileri ve özellikleri tanımla. Yapay zeka ilk belgelerden şema önerebilir.",
    icon: (
      <svg viewBox="0 0 24 24">
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </svg>
    ),
  },
  {
    label: "Veri Yükleme",
    desc: "Transkript yapıştır, senaryo yükle, doküman ekle. Platform her kaynağı işlenebilir birimlere ayırır.",
    icon: (
      <svg viewBox="0 0 24 24">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="17 8 12 3 7 8" />
        <line x1="12" y1="3" x2="12" y2="15" />
      </svg>
    ),
  },
  {
    label: "Yapay Zeka Çıkarımı",
    desc: "Çıkarım motoru varlıkları, ilişkileri ve olayları tespit eder — tam olarak şemana göre.",
    icon: (
      <svg viewBox="0 0 24 24">
        <rect x="4" y="4" width="16" height="16" rx="2" />
        <rect x="9" y="9" width="6" height="6" />
        <line x1="9" y1="1" x2="9" y2="4" />
        <line x1="15" y1="1" x2="15" y2="4" />
        <line x1="9" y1="20" x2="9" y2="23" />
        <line x1="15" y1="20" x2="15" y2="23" />
        <line x1="20" y1="9" x2="23" y2="9" />
        <line x1="20" y1="14" x2="23" y2="14" />
        <line x1="1" y1="9" x2="4" y2="9" />
        <line x1="1" y1="14" x2="4" y2="14" />
      </svg>
    ),
  },
  {
    label: "İnceleme & Doğrulama",
    desc: "Yapay zeka belirsiz öğeleri inceleme için işaretler. Sen birleştir, reddet ya da düzenle.",
    icon: (
      <svg viewBox="0 0 24 24">
        <polyline points="20 6 9 17 4 12" />
      </svg>
    ),
  },
  {
    label: "Grafik Büyür",
    desc: "Her yeni girdi mevcut düğümlerin üzerine delta olarak eklenir. Grafik her bölümle gelişir.",
    icon: (
      <svg viewBox="0 0 24 24">
        <line x1="6" y1="3" x2="6" y2="15" />
        <circle cx="18" cy="6" r="3" />
        <circle cx="6" cy="18" r="3" />
        <path d="M18 9a9 9 0 0 1-9 9" />
      </svg>
    ),
  },
  {
    label: "Keşfet & Sorgula",
    desc: "Karakterleri, olayları ve ilişkileri görsel olarak gez. Cypher ile sorgula veya ajan katmanı kur.",
    icon: (
      <svg viewBox="0 0 24 24">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
    ),
  },
] as const;

function PipelineSteps({ activeStep }: { activeStep: number }) {
  return (
    <div className="pipeline-strip" aria-label="Platform pipeline adımları">
      {PIPELINE_STEPS.map((step, index) => {
        const stepNum = index + 1;
        const isActive = stepNum === activeStep;
        const isDone = stepNum < activeStep;
        const cls = `pipeline-step${isActive ? " is-active" : isDone ? " is-done" : ""}`;
        return (
          <div key={step.label} className={cls}>
            <div className="pipeline-step-icon-row">
              <div className="pipeline-step-circle">{step.icon}</div>
              {isActive && <div className="pipeline-step-dot" />}
              <span className="pipeline-step-badge">0{stepNum}</span>
            </div>
            <p className="pipeline-step-title">{step.label}</p>
            <p className="pipeline-step-desc">{step.desc}</p>
          </div>
        );
      })}
    </div>
  );
}
