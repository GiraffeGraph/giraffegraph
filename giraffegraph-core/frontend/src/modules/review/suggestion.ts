import type {
  CandidateNodeRecord,
  ProjectReviewQueueRecord,
  ReviewQueueItemRecord,
  ReviewQueueRunEntryRecord,
} from "@/modules/projects/types";

export const NARRATOR_TYPE = "Narrator";
export const NARRATED_FROM_TYPE = "NARRATED_FROM";

export interface ReviewEntry {
  runEntry: ReviewQueueRunEntryRecord;
  item: ReviewQueueItemRecord;
}

/** What the system suggested, in the shape the screen shows it. */
export type Suggestion =
  | { kind: "narrator"; name: string }
  | {
      kind: "link";
      from: string | null;
      to: string | null;
      sigha: string | null;
      chainNo: number | null;
      position: number | null;
    }
  | { kind: "record"; typeName: string; fields: { label: string; value: string }[] }
  | {
      kind: "proposal";
      typeName: string;
      fieldName: string | null;
      sampleValue: string | null;
      count: number | null;
    };

const FIELD_LABELS: Record<string, string> = {
  name: "İsim",
  sigha: "Rivayet lafzı",
  chain_no: "Zincir numarası",
  position: "Zincirdeki sıra",
  hadith_ref: "Hadis",
};

export function fieldLabel(key: string): string {
  return FIELD_LABELS[key] ?? key;
}

function asText(value: unknown): string | null {
  if (typeof value === "string") {
    return value.trim() === "" ? null : value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  return null;
}

function asNumber(value: unknown): number | null {
  return typeof value === "number" ? value : null;
}

export function narratorName(node: CandidateNodeRecord | undefined): string | null {
  return node ? asText(node.properties.name) : null;
}

function listFields(properties: Record<string, unknown>): { label: string; value: string }[] {
  return Object.entries(properties).flatMap(([key, value]) => {
    const text = asText(value);
    return text === null ? [] : [{ label: fieldLabel(key), value: text }];
  });
}

export function describeSuggestion(
  item: ReviewQueueItemRecord,
  runNodes: CandidateNodeRecord[],
): Suggestion {
  const node = item.candidate_node;
  if (node) {
    const name = asText(node.properties.name);
    if (node.node_type === NARRATOR_TYPE && name !== null) {
      return { kind: "narrator", name };
    }
    return { kind: "record", typeName: node.node_type, fields: listFields(node.properties) };
  }

  const relation = item.candidate_relation;
  if (relation) {
    if (relation.relation_type === NARRATED_FROM_TYPE) {
      const byId = new Map(runNodes.map((candidate) => [candidate.candidate_node_id, candidate]));
      return {
        kind: "link",
        from: narratorName(byId.get(relation.from_candidate_ref)),
        to: narratorName(byId.get(relation.to_candidate_ref)),
        sigha: asText(relation.properties.sigha),
        chainNo: asNumber(relation.properties.chain_no),
        position: asNumber(relation.properties.position),
      };
    }
    return {
      kind: "record",
      typeName: relation.relation_type,
      fields: listFields(relation.properties),
    };
  }

  const payload = item.review_item.payload_json;
  return {
    kind: "proposal",
    typeName: asText(payload.type_name) ?? "adı bilinmeyen tür",
    fieldName: asText(payload.property_name),
    sampleValue: asText(payload.sample_value),
    count: asNumber(payload.count),
  };
}

/** One short phrase that names a suggestion, for the history list and confirmations. */
export function suggestionTitle(suggestion: Suggestion): string {
  switch (suggestion.kind) {
    case "narrator":
      return "Ravi";
    case "link":
      return "Ravi bağlantısı";
    case "record":
      return suggestion.typeName;
    case "proposal":
      return suggestion.fieldName ? "Tanımsız alan" : "Tanımsız tür";
  }
}

export function quotesOf(item: ReviewQueueItemRecord): string[] {
  const quotes = item.evidence_snippets.flatMap((snippet) =>
    snippet.quote && snippet.quote.trim() !== "" ? [snippet.quote] : [],
  );
  if (quotes.length === 0) {
    const sample = asText(item.review_item.payload_json.sample_quote);
    if (sample !== null) {
      quotes.push(sample);
    }
  }
  return Array.from(new Set(quotes));
}

function itemRank(item: ReviewQueueItemRecord): number {
  if (item.review_item.reason_code === "relation_dependency_review") {
    return 3;
  }
  if (item.candidate_node) {
    return 0;
  }
  return item.candidate_relation ? 1 : 2;
}

/**
 * The order a person meets the suggestions in: hadith by hadith, narrators before the
 * links that depend on them, and links that only wait for a narrator last, because
 * they usually settle on their own.
 */
export function orderEntries(queue: ProjectReviewQueueRecord): ReviewEntry[] {
  return queue.run_entries.flatMap((runEntry) =>
    [...runEntry.review_items]
      .sort((left, right) => itemRank(left) - itemRank(right))
      .map((item) => ({ runEntry, item })),
  );
}
