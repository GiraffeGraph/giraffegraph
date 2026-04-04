import { apiBaseUrl } from "@/shared/api/config";

import type {
  CandidateNodeRecord,
  CandidateRelationRecord,
  CanonicalNodeDetailRecord,
  CanonicalNodeRecord,
  CanonicalRelationDetailRecord,
  CanonicalRelationRecord,
  ExtractionResultRecord,
  GraphDeltaRecord,
  GraphOverviewRecord,
  GraphSnapshot,
  ProcessingJobQueueStatusFilter,
  ProcessingJobRecord,
  ProcessingRunRecord,
  ProjectProcessingJobQueueRecord,
  ProjectReviewQueueRecord,
  ProjectRecord,
  ReviewDecisionRequest,
  ReviewItemRecord,
  ReviewQueueStatusFilter,
  RunValidationRecord,
  SchemaVersionRecord,
  SegmentRecord,
  SourceUnitRecord,
  SourceUnitSummaryRecord,
} from "@/modules/projects/types";

type QueryValue = string | number | null | undefined;

interface RequestOptions extends RequestInit {
  query?: Record<string, QueryValue>;
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function buildUrl(path: string, query?: Record<string, QueryValue>): string {
  const url = new URL(path, apiBaseUrl);
  if (!query) {
    return url.toString();
  }

  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null || value === "") {
      continue;
    }
    url.searchParams.set(key, String(value));
  }

  return url.toString();
}

async function requestJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { query, headers, ...init } = options;
  const response = await fetch(buildUrl(path, query), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = (await response.json()) as { detail?: string };
      detail = payload.detail ?? detail;
    } catch {
      // Keep the default status text if the backend body is not JSON.
    }
    throw new ApiError(detail || "API isteği başarısız oldu.", response.status);
  }

  return (await response.json()) as T;
}

export async function listProjects(): Promise<ProjectRecord[]> {
  return requestJson<ProjectRecord[]>("/api/projects");
}

export async function getProject(projectId: string): Promise<ProjectRecord> {
  return requestJson<ProjectRecord>(`/api/projects/${projectId}`);
}

export async function getProjectReviewQueue(
  projectId: string,
  query: {
    statusFilter?: ReviewQueueStatusFilter;
    runLimit?: number;
  } = {},
): Promise<ProjectReviewQueueRecord> {
  return requestJson<ProjectReviewQueueRecord>(
    `/api/projects/${projectId}/review-queue`,
    {
      query: {
        status_filter: query.statusFilter ?? "open",
        run_limit: query.runLimit ?? 12,
      },
    },
  );
}

export async function getProjectProcessingJobs(
  projectId: string,
  query: {
    statusFilter?: ProcessingJobQueueStatusFilter;
    runLimit?: number;
  } = {},
): Promise<ProjectProcessingJobQueueRecord> {
  return requestJson<ProjectProcessingJobQueueRecord>(
    `/api/projects/${projectId}/processing-jobs`,
    {
      query: {
        status_filter: query.statusFilter ?? "active",
        run_limit: query.runLimit ?? 12,
      },
    },
  );
}

export async function listProjectRuns(projectId: string): Promise<ProcessingRunRecord[]> {
  return requestJson<ProcessingRunRecord[]>(`/api/projects/${projectId}/runs`);
}

export async function getSourceUnit(sourceUnitId: string): Promise<SourceUnitRecord> {
  return requestJson<SourceUnitRecord>(`/api/source-units/${sourceUnitId}`);
}

export async function listSourceUnitSegments(
  sourceUnitId: string,
): Promise<SegmentRecord[]> {
  return requestJson<SegmentRecord[]>(`/api/source-units/${sourceUnitId}/segments`);
}

export async function listRunCandidateNodes(runId: string): Promise<CandidateNodeRecord[]> {
  return requestJson<CandidateNodeRecord[]>(`/api/runs/${runId}/candidate-nodes`);
}

export async function listRunCandidateRelations(
  runId: string,
): Promise<CandidateRelationRecord[]> {
  return requestJson<CandidateRelationRecord[]>(`/api/runs/${runId}/candidate-relations`);
}

export async function listRunReviewItems(runId: string): Promise<ReviewItemRecord[]> {
  return requestJson<ReviewItemRecord[]>(`/api/runs/${runId}/review-items`);
}

export async function decideReviewItem(
  reviewItemId: string,
  request: ReviewDecisionRequest,
): Promise<ReviewItemRecord> {
  return requestJson<ReviewItemRecord>(`/api/review-items/${reviewItemId}/decision`, {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getGraphOverview(projectId: string): Promise<GraphOverviewRecord> {
  return requestJson<GraphOverviewRecord>(`/api/projects/${projectId}/graph/overview`);
}

export async function listGraphNodes(
  projectId: string,
  query: { nodeType?: string; limit?: number } = {},
): Promise<CanonicalNodeRecord[]> {
  return requestJson<CanonicalNodeRecord[]>(`/api/projects/${projectId}/graph/nodes`, {
    query: {
      node_type: query.nodeType,
      limit: query.limit ?? 40,
    },
  });
}

export async function listGraphRelations(
  projectId: string,
  query: { relationType?: string; limit?: number } = {},
): Promise<CanonicalRelationRecord[]> {
  return requestJson<CanonicalRelationRecord[]>(
    `/api/projects/${projectId}/graph/relations`,
    {
      query: {
        relation_type: query.relationType,
        limit: query.limit ?? 40,
      },
    },
  );
}

export async function getGraphNodeDetail(
  projectId: string,
  nodeType: string,
  mergeKey: string,
): Promise<CanonicalNodeDetailRecord> {
  return requestJson<CanonicalNodeDetailRecord>(
    `/api/projects/${projectId}/graph/nodes/${encodeURIComponent(nodeType)}/${encodeURIComponent(mergeKey)}`,
  );
}

export async function getGraphRelationDetail(
  projectId: string,
  relation: {
    relationType: string;
    fromNodeType: string;
    fromMergeKey: string;
    toNodeType: string;
    toMergeKey: string;
  },
): Promise<CanonicalRelationDetailRecord> {
  const {
    relationType,
    fromNodeType,
    fromMergeKey,
    toNodeType,
    toMergeKey,
  } = relation;
  return requestJson<CanonicalRelationDetailRecord>(
    "/api/projects/"
      + `${projectId}/graph/relations/${encodeURIComponent(relationType)}`
      + `/${encodeURIComponent(fromNodeType)}`
      + `/${encodeURIComponent(fromMergeKey)}`
      + `/${encodeURIComponent(toNodeType)}`
      + `/${encodeURIComponent(toMergeKey)}`,
  );
}

export async function loadGraphSnapshot(
  projectId: string,
  query: { nodeType?: string; relationType?: string; limit?: number } = {},
): Promise<GraphSnapshot> {
  const [overview, nodes, relations] = await Promise.all([
    getGraphOverview(projectId),
    listGraphNodes(projectId, {
      nodeType: query.nodeType,
      limit: query.limit,
    }),
    listGraphRelations(projectId, {
      relationType: query.relationType,
      limit: query.limit,
    }),
  ]);

  return {
    overview,
    nodes,
    relations,
  };
}

// ── Projects ──────────────────────────────────────────────────────────────────

export async function createProject(body: {
  name: string;
  description?: string | null;
  template_id?: string | null;
}): Promise<ProjectRecord> {
  return requestJson<ProjectRecord>("/api/projects", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

// ── Schema ────────────────────────────────────────────────────────────────────

export async function listSchemaVersions(projectId: string): Promise<SchemaVersionRecord[]> {
  return requestJson<SchemaVersionRecord[]>(`/api/projects/${projectId}/schema-versions`);
}

export async function createSchemaVersion(
  projectId: string,
  body: { version_no: number; notes?: string | null },
): Promise<SchemaVersionRecord> {
  return requestJson<SchemaVersionRecord>(`/api/projects/${projectId}/schema-versions`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function activateSchemaVersion(
  projectId: string,
  schemaVersionId: string,
): Promise<SchemaVersionRecord> {
  return requestJson<SchemaVersionRecord>(
    `/api/projects/${projectId}/schema-versions/${schemaVersionId}/activate`,
    { method: "POST" },
  );
}

export async function addNodeType(
  schemaVersionId: string,
  body: {
    name: string;
    display_name: string;
    description: string;
    merge_keys: string[];
    confidence_threshold?: number;
    aliases?: string[];
    extraction_hints?: string[];
  },
): Promise<SchemaVersionRecord> {
  return requestJson<SchemaVersionRecord>(
    `/api/schema-versions/${schemaVersionId}/node-types`,
    { method: "POST", body: JSON.stringify({ properties: [], ...body }) },
  );
}

export async function addRelationType(
  schemaVersionId: string,
  body: {
    name: string;
    from_type: string;
    to_type: string;
    description: string;
    directional?: boolean;
    aliases?: string[];
    extraction_hints?: string[];
  },
): Promise<SchemaVersionRecord> {
  return requestJson<SchemaVersionRecord>(
    `/api/schema-versions/${schemaVersionId}/relation-types`,
    { method: "POST", body: JSON.stringify({ properties: [], ...body }) },
  );
}

// ── Ingestion ─────────────────────────────────────────────────────────────────

export async function listSourceUnits(projectId: string): Promise<SourceUnitSummaryRecord[]> {
  return requestJson<SourceUnitSummaryRecord[]>(`/api/projects/${projectId}/source-units`);
}

export async function createSourceUnit(
  projectId: string,
  body: {
    schema_version_id: string;
    source_type: string;
    title: string;
    raw_content: string;
    sequence_no?: number | null;
  },
): Promise<SourceUnitRecord> {
  return requestJson<SourceUnitRecord>(`/api/projects/${projectId}/source-units`, {
    method: "POST",
    body: JSON.stringify({ metadata_json: {}, ...body }),
  });
}

export async function generateSegments(
  sourceUnitId: string,
  strategy = "paragraphs",
): Promise<SegmentRecord[]> {
  return requestJson<SegmentRecord[]>(`/api/source-units/${sourceUnitId}/segments/generate`, {
    method: "POST",
    body: JSON.stringify({ strategy }),
  });
}

export async function startProcessingRun(
  sourceUnitId: string,
  body: {
    schema_version_id: string;
    pipeline_version: string;
    llm_provider?: string | null;
    llm_model?: string | null;
  },
): Promise<ProcessingRunRecord> {
  return requestJson<ProcessingRunRecord>(`/api/source-units/${sourceUnitId}/runs`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function extractCandidates(
  runId: string,
  dryRun = false,
): Promise<ExtractionResultRecord> {
  return requestJson<ExtractionResultRecord>(`/api/runs/${runId}/extract-candidates`, {
    method: "POST",
    body: JSON.stringify({ dry_run: dryRun }),
  });
}

export async function validateRun(runId: string): Promise<RunValidationRecord> {
  return requestJson<RunValidationRecord>(`/api/runs/${runId}/validate`, { method: "POST" });
}

export async function resolveDuplicates(runId: string): Promise<RunValidationRecord> {
  return requestJson<RunValidationRecord>(`/api/runs/${runId}/resolve-duplicates`, {
    method: "POST",
  });
}

export async function commitRun(runId: string): Promise<GraphDeltaRecord> {
  return requestJson<GraphDeltaRecord>(`/api/runs/${runId}/commit`, { method: "POST" });
}
