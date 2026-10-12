import { getProjectReviewQueue, listSourceUnits } from "@/modules/projects/api";
import type { SourceUnitSummaryRecord } from "@/modules/projects/types";
import { countWithPossessive } from "@/shared/format";

export type StepKey = "yukle" | "cikar" | "incele" | "oku";

export interface ProjectStatus {
  hadiths: SourceUnitSummaryRecord[];
  total: number;
  /** Loaded, chains not extracted yet (or the last attempt failed). */
  waitingToExtract: SourceUnitSummaryRecord[];
  /** Suggestions that need a person's decision. */
  openSuggestions: number;
  hadithsNeedingReview: number;
  /** Extracted and fully decided, not written to the graph yet. */
  readyToWrite: number;
  inGraph: number;
}

const REVIEW_RUN_LIMIT = 100;

/**
 * The API has no per-project summary, so the counts are put together from the
 * hadith list and the open review queue.
 */
export async function loadProjectStatus(projectId: string): Promise<ProjectStatus> {
  const [hadiths, queue] = await Promise.all([
    listSourceUnits(projectId),
    getProjectReviewQueue(projectId, { statusFilter: "open", runLimit: REVIEW_RUN_LIMIT }),
  ]);
  const needingReview = new Set(
    queue.run_entries
      .filter((entry) => entry.open_review_count > 0)
      .map((entry) => entry.source_unit.source_unit_id),
  );
  const inProgress = hadiths.filter((hadith) => hadith.status === "processing");

  return {
    hadiths,
    total: hadiths.length,
    waitingToExtract: hadiths.filter(
      (hadith) => hadith.status === "ready" || hadith.status === "failed",
    ),
    openSuggestions: queue.open_review_count,
    hadithsNeedingReview: needingReview.size,
    readyToWrite: inProgress.filter((hadith) => !needingReview.has(hadith.source_unit_id)).length,
    inGraph: hadiths.filter((hadith) => hadith.status === "processed").length,
  };
}

/** One plain line for a project card: "30 hadis · hepsi grafta · bekleyen yok". */
export function describeStatus(status: ProjectStatus): string {
  if (status.total === 0) {
    return "Henüz metin yüklenmedi";
  }
  const parts = [`${status.total} hadis`];
  if (status.inGraph === status.total) {
    parts.push("hepsi grafta");
  } else if (status.inGraph > 0) {
    parts.push(`${countWithPossessive(status.inGraph)} grafta`);
  } else {
    parts.push("grafta olan yok");
  }
  parts.push(describeWaiting(status) ?? "bekleyen yok");
  return parts.join(" · ");
}

export function describeWaiting(status: ProjectStatus): string | null {
  if (status.openSuggestions > 0) {
    return `${status.openSuggestions} öneri seni bekliyor`;
  }
  if (status.readyToWrite > 0) {
    return `${status.readyToWrite} hadis grafa yazılmayı bekliyor`;
  }
  if (status.waitingToExtract.length > 0) {
    return `${status.waitingToExtract.length} hadisin zinciri çıkarılmadı`;
  }
  return null;
}

/** The first step that still has work, in the order a person would do it. */
export function nextStepWithWork(status: ProjectStatus): StepKey {
  if (status.total === 0) {
    return "yukle";
  }
  if (status.waitingToExtract.length > 0) {
    return "cikar";
  }
  if (status.openSuggestions > 0 || status.readyToWrite > 0) {
    return "incele";
  }
  return "oku";
}

export const STEP_ACTION: Record<StepKey, string> = {
  yukle: "Metin yükle",
  cikar: "Zincirleri çıkar",
  incele: "İncelemeye geç",
  oku: "Zincirleri oku",
};

export function stepHref(projectId: string, step: StepKey | "gelismis"): string {
  return `/proje/${projectId}/${step}`;
}
