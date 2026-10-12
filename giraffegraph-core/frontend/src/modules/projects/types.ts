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

export interface ReviewDecisionRecord {
  decision_id: string;
  review_item_id: string;
  run_id: string;
  item_type: string;
  item_ref: string;
  action: "accept" | "reject" | "edit";
  reviewer_id: string;
  reviewer_note: string | null;
  duration_ms: number | null;
  before_json: Record<string, unknown> | null;
  after_json: Record<string, unknown> | null;
  decided_at: string;
}

export interface ReviewItemWithDecisionsRecord extends ReviewItemRecord {
  decisions: ReviewDecisionRecord[];
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
  review_item: ReviewItemWithDecisionsRecord;
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
  reviewer_id: string;
  duration_ms?: number | null;
  reviewer_note?: string | null;
  node_type?: string | null;
  relation_type?: string | null;
  from_candidate_ref?: string | null;
  to_candidate_ref?: string | null;
  properties?: Record<string, unknown>;
  merge_key_payload?: Record<string, unknown>;
  confidence?: number | null;
}

// ── Template project creation ────────────────────────────────────────────────

export interface TemplateSchemaBlueprintRecord {
  node_types: string[];
  relation_types: string[];
  segmentation_strategy: string;
}

export interface TemplateRecord {
  template_id: string;
  name: string;
  slug: string;
  description: string;
  is_system: boolean;
  created_at: string;
  schema_blueprint: TemplateSchemaBlueprintRecord | null;
}

export interface AppliedTemplateSchemaRecord {
  schema_version_id: string;
  version_no: number;
  status: string;
  pipeline_version: string;
  segmentation_strategy: string;
}

export interface ProjectCreateRecord extends ProjectRecord {
  template_schema: AppliedTemplateSchemaRecord | null;
}

// ── Bulk ingest & processing ─────────────────────────────────────────────────

export interface BulkSourceUnitItem {
  external_ref: string;
  title?: string | null;
  raw_content: string;
}

export interface BulkSourceUnitItemResultRecord {
  index: number;
  external_ref: string;
  status: "created" | "duplicate";
  source_unit_id: string | null;
  detail: string | null;
}

export interface BulkSourceUnitResultRecord {
  project_id: string;
  schema_version_id: string;
  created_count: number;
  duplicate_count: number;
  results: BulkSourceUnitItemResultRecord[];
}

export type SourceUnitProcessStatus = "committed" | "validated" | "needs_review" | "failed";

export interface SourceUnitProcessResultRecord {
  source_unit_id: string;
  external_ref: string | null;
  status: SourceUnitProcessStatus;
  run_id: string | null;
  segment_count: number;
  candidate_node_count: number;
  candidate_relation_count: number;
  validated_node_count: number;
  validated_relation_count: number;
  open_review_count: number;
  failed_call_count: number;
  detail: string | null;
}

export interface SourceUnitProcessRecord {
  project_id: string;
  segmentation_strategy: string;
  llm_provider: string;
  llm_model: string | null;
  processed_count: number;
  failed_count: number;
  committed_count: number;
  results: SourceUnitProcessResultRecord[];
}

// ── Chains ───────────────────────────────────────────────────────────────────

export interface FactEvidenceRecord {
  segment_id: string;
  segment_order: number | null;
  segment_text: string | null;
  quote: string | null;
  start_offset: number | null;
  end_offset: number | null;
  source_start_offset: number | null;
  source_end_offset: number | null;
}

export interface FactAcceptanceRecord {
  kind: "human" | "policy";
  policy: string | null;
  rule_code: string | null;
  action: string | null;
  reviewer_id: string | null;
  decided_at: string | null;
}

export interface ChainNarratorRecord {
  name: string;
  evidence: FactEvidenceRecord[];
  acceptance: FactAcceptanceRecord | null;
}

export interface ChainLinkRecord {
  position: number;
  from_narrator: string;
  to_narrator: string;
  sigha: string | null;
  evidence: FactEvidenceRecord[];
  acceptance: FactAcceptanceRecord | null;
}

export interface NarratorChainRecord {
  chain_no: number;
  narrators: string[];
  links: ChainLinkRecord[];
}

export interface HadithChainViewRecord {
  project_id: string;
  hadith_ref: string;
  committed: boolean;
  source_unit: { source_unit_id: string; title: string; raw_content: string } | null;
  runs: {
    run_id: string;
    committed_at: string | null;
    llm_provider: string | null;
    llm_model: string | null;
  }[];
  chains: NarratorChainRecord[];
  narrators: ChainNarratorRecord[];
}

export interface CommittedHadithRecord {
  hadith_ref: string;
  source_unit_id: string;
  title: string;
  run_id: string;
  committed_at: string | null;
}

export interface CommittedHadithListRecord {
  project_id: string;
  total_count: number;
  hadiths: CommittedHadithRecord[];
}

export interface NarratorNeighbourRecord {
  name: string;
  link_count: number;
  hadith_refs: string[];
}

export interface NarratorViewRecord {
  project_id: string;
  name: string;
  hadith_count: number;
  hadiths: { hadith_ref: string; source_unit_id: string; title: string }[];
  narrated_from_count: number;
  narrated_from: NarratorNeighbourRecord[];
  narrated_to_count: number;
  narrated_to: NarratorNeighbourRecord[];
}
