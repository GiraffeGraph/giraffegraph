export type ProjectStatus = "draft" | "active" | "archived";
export type RunStatus = "pending" | "running" | "completed" | "failed";
export type SourceUnitStatus =
  | "draft"
  | "ready"
  | "processing"
  | "processed"
  | "failed";
export type CandidateStatus =
  | "pending"
  | "validated"
  | "rejected"
  | "review"
  | "committed";
export type ReviewStatus = "open" | "accepted" | "rejected" | "edited";
export type ReviewQueueStatusFilter = "open" | "closed" | "all";
export type ProcessingJobQueueStatusFilter =
  | "active"
  | "failed"
  | "succeeded"
  | "all";

export interface ProjectRecord {
  project_id: string;
  name: string;
  description: string | null;
  template_id: string | null;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
}

export interface ProcessingRunRecord {
  run_id: string;
  project_id: string;
  schema_version_id: string;
  source_unit_id: string;
  pipeline_version: string;
  status: RunStatus;
  llm_provider: string | null;
  llm_model: string | null;
  created_at: string;
  started_at: string | null;
  ended_at: string | null;
}

export interface SourceUnitRecord {
  source_unit_id: string;
  project_id: string;
  schema_version_id: string;
  source_type: string;
  title: string;
  raw_content: string;
  sequence_no: number | null;
  external_ref: string | null;
  metadata_json: Record<string, string>;
  status: SourceUnitStatus;
  created_at: string;
}

export interface SourceUnitSummaryRecord {
  source_unit_id: string;
  project_id: string;
  schema_version_id: string;
  source_type: string;
  title: string;
  sequence_no: number | null;
  external_ref: string | null;
  metadata_json: Record<string, string>;
  status: SourceUnitStatus;
  created_at: string;
}

export interface SegmentRecord {
  segment_id: string;
  source_unit_id: string;
  segment_order: number;
  text: string;
  metadata_json: Record<string, string>;
}

export interface EvidenceRefRecord {
  segment_id: string;
  quote: string | null;
  start_offset: number | null;
  end_offset: number | null;
}

export interface CandidateNodeRecord {
  candidate_node_id: string;
  run_id: string;
  node_type: string;
  properties: Record<string, unknown>;
  merge_key_payload: Record<string, unknown>;
  confidence: number;
  evidence_refs: EvidenceRefRecord[];
  status: CandidateStatus;
}

export interface CandidateRelationRecord {
  candidate_relation_id: string;
  run_id: string;
  relation_type: string;
  from_candidate_ref: string;
  to_candidate_ref: string;
  properties: Record<string, unknown>;
  confidence: number;
  evidence_refs: EvidenceRefRecord[];
  status: CandidateStatus;
}

export interface ReviewItemRecord {
  review_item_id: string;
  run_id: string;
  item_type: string;
  item_ref: string;
  reason_code: string;
  payload_json: Record<string, unknown>;
  status: ReviewStatus;
  reviewer_note: string | null;
  created_at: string;
}

export interface ProcessingJobRecord {
  job_id: string;
  project_id: string;
  run_id: string;
  source_unit_id: string;
  job_type: string;
  status: "pending" | "running" | "succeeded" | "failed";
  payload_json: Record<string, unknown>;
  output_json: Record<string, unknown>;
  error_message: string | null;
  attempt_count: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface NodeTypeCountRecord {
  node_type: string;
  count: number;
}

export interface GraphOverviewRecord {
  project_id: string;
  node_count: number;
  relation_count: number;
  node_type_counts: NodeTypeCountRecord[];
}

export interface CanonicalNodeRecord {
  project_id: string;
  node_type: string;
  merge_key: string;
  properties: Record<string, unknown>;
  source_unit_id: string | null;
  last_run_id: string | null;
  updated_at: string | null;
}

export interface CanonicalRelationRecord {
  project_id: string;
  relation_type: string;
  from_node_type: string;
  from_merge_key: string;
  to_node_type: string;
  to_merge_key: string;
  properties: Record<string, unknown>;
  source_unit_id: string | null;
  last_run_id: string | null;
  updated_at: string | null;
}

export interface CanonicalSourceUnitRefRecord {
  source_unit_id: string;
  title: string | null;
  source_type: string | null;
  sequence_no: number | null;
}

export interface CanonicalSegmentSupportRecord {
  segment_id: string;
  source_unit_id: string | null;
  segment_order: number | null;
  text: string;
}

export interface ConnectedRelationRecord {
  relation_type: string;
  direction: "incoming" | "outgoing";
  other_node_type: string;
  other_merge_key: string;
  other_node_properties: Record<string, unknown>;
  properties: Record<string, unknown>;
  updated_at: string | null;
}

export interface CanonicalNodeDetailRecord {
  node: CanonicalNodeRecord;
  source_units: CanonicalSourceUnitRefRecord[];
  supporting_segments: CanonicalSegmentSupportRecord[];
  connected_relations: ConnectedRelationRecord[];
}

export interface CanonicalRelationEndpointRecord {
  node_type: string;
  merge_key: string;
  properties: Record<string, unknown>;
}

export interface CanonicalRelationDetailRecord {
  relation: CanonicalRelationRecord;
  from_node: CanonicalRelationEndpointRecord;
  to_node: CanonicalRelationEndpointRecord;
  source_units: CanonicalSourceUnitRefRecord[];
  supporting_segments: CanonicalSegmentSupportRecord[];
}

export interface ReviewEvidenceSnippetRecord {
  segment_id: string;
  segment_order: number | null;
  text: string | null;
  quote: string | null;
}

export interface ReviewQueueItemRecord {
  review_item: ReviewItemRecord;
  candidate_node: CandidateNodeRecord | null;
  candidate_relation: CandidateRelationRecord | null;
  headline: string;
  confidence: number | null;
  messages: string[];
  evidence_snippets: ReviewEvidenceSnippetRecord[];
}

export interface ReviewQueueRunEntryRecord {
  run: ProcessingRunRecord;
  source_unit: SourceUnitSummaryRecord;
  review_items: ReviewQueueItemRecord[];
  open_review_count: number;
  total_review_count: number;
}

export interface ProjectReviewQueueRecord {
  project_id: string;
  run_entries: ReviewQueueRunEntryRecord[];
  status_filter: ReviewQueueStatusFilter;
  run_limit: number;
  open_review_count: number;
  total_review_count: number;
  filtered_run_count: number;
  returned_run_count: number;
  returned_review_count: number;
  has_more_runs: boolean;
}

export interface ProcessingJobQueueRunEntryRecord {
  run: ProcessingRunRecord;
  source_unit: SourceUnitSummaryRecord;
  jobs: ProcessingJobRecord[];
  active_job_count: number;
  failed_job_count: number;
  total_job_count: number;
}

export interface ProjectProcessingJobQueueRecord {
  project_id: string;
  run_entries: ProcessingJobQueueRunEntryRecord[];
  status_filter: ProcessingJobQueueStatusFilter;
  run_limit: number;
  active_job_count: number;
  failed_job_count: number;
  succeeded_job_count: number;
  total_job_count: number;
  filtered_run_count: number;
  returned_run_count: number;
  returned_job_count: number;
  has_more_runs: boolean;
}

export interface GraphSnapshot {
  overview: GraphOverviewRecord;
  nodes: CanonicalNodeRecord[];
  relations: CanonicalRelationRecord[];
}

// ── Schema types ─────────────────────────────────────────────────────────────

export interface NodeTypeRecord {
  node_type_id: string;
  schema_version_id: string;
  name: string;
  display_name: string;
  description: string;
  merge_keys: string[];
  confidence_threshold: number;
  aliases: string[];
  extraction_hints: string[];
  is_active: boolean;
}

export interface RelationTypeRecord {
  relation_type_id: string;
  schema_version_id: string;
  name: string;
  from_type: string;
  to_type: string;
  description: string;
  directional: boolean;
  confidence_threshold: number;
  is_active: boolean;
}

export interface SchemaVersionRecord {
  schema_version_id: string;
  project_id: string;
  version_no: number;
  status: "draft" | "active" | "archived";
  notes: string | null;
  created_at: string;
  activated_at: string | null;
  node_types: NodeTypeRecord[];
  relation_types: RelationTypeRecord[];
}

// ── Pipeline types ────────────────────────────────────────────────────────────

export interface ExtractionResultRecord {
  execution_id: string;
  run_id: string;
  dry_run: boolean;
  segment_count: number;
  created_candidate_node_ids: string[];
  created_candidate_relation_ids: string[];
}

export interface RunValidationRecord {
  run_id: string;
  node_total: number;
  node_validated: number;
  node_review: number;
  node_rejected: number;
  relation_total: number;
  relation_validated: number;
  relation_review: number;
  relation_rejected: number;
}

export interface GraphDeltaRecord {
  delta_id: string;
  run_id: string;
  project_id: string;
  nodes_created: number;
  nodes_merged: number;
  relations_created: number;
  relations_merged: number;
  review_count: number;
  rejected_count: number;
  created_at: string;
}

export interface ReviewDecisionRequest {
  action: "accept" | "reject" | "edit";
  reviewer_note?: string | null;
  node_type?: string | null;
  relation_type?: string | null;
  from_candidate_ref?: string | null;
  to_candidate_ref?: string | null;
  properties?: Record<string, unknown>;
  merge_key_payload?: Record<string, unknown>;
  confidence?: number | null;
}
