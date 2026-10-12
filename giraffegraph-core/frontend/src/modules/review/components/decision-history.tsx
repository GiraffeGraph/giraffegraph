import type { ProjectReviewQueueRecord, ReviewQueueItemRecord } from "@/modules/projects/types";
import { describeSuggestion, orderEntries, suggestionTitle } from "@/modules/review/suggestion";
import { formatDateTime, formatSeconds } from "@/shared/format";
import { ArabicText } from "@/shared/ui/arabic-text";
import { Icon } from "@/shared/ui/icons";

function outcome(item: ReviewQueueItemRecord): { text: string; accepted: boolean; byPerson: boolean } {
  const decisions = item.review_item.decisions;
  const last = decisions[decisions.length - 1];
  if (last) {
    if (last.action === "accept") {
      return { text: "Kabul edildi", accepted: true, byPerson: true };
    }
    if (last.action === "edit") {
      return { text: "Düzeltilerek kabul edildi", accepted: true, byPerson: true };
    }
    return { text: "Reddedildi", accepted: false, byPerson: true };
  }
  return item.review_item.status === "rejected"
    ? { text: "Kendiliğinden reddedildi", accepted: false, byPerson: false }
    : { text: "Kendiliğinden kabul edildi", accepted: true, byPerson: false };
}

/** Closed suggestions, newest hadith first. Read-only: a decision cannot be taken back here. */
export function DecisionHistory({ closed }: { closed: ProjectReviewQueueRecord | null }) {
  const entries = closed ? orderEntries(closed) : [];
  if (entries.length === 0) {
    return null;
  }

  return (
    <details className="disclosure">
      <summary>Karar geçmişi ({entries.length})</summary>
      <ul className="history-list">
        {entries.map(({ item, runEntry }) => {
          const suggestion = describeSuggestion(item, []);
          const result = outcome(item);
          const decisions = item.review_item.decisions;
          const last = decisions[decisions.length - 1];
          const duration = last ? formatSeconds(last.duration_ms) : null;
          return (
            <li key={item.review_item.review_item_id}>
              <span className={`status ${result.accepted ? "status-done" : "status-neutral"}`}>
                <Icon name={result.accepted ? "check" : "close"} />
                {result.text}
              </span>
              <span>
                {suggestionTitle(suggestion)}
                {suggestion.kind === "narrator" ? (
                  <>
                    {": "}
                    <ArabicText size="sm">{suggestion.name}</ArabicText>
                  </>
                ) : null}
                {suggestion.kind === "link" && suggestion.position !== null
                  ? ` (${suggestion.chainNo ?? "?"}. zincir, ${suggestion.position}. bağlantı)`
                  : null}
              </span>
              <span className="muted small num">
                {runEntry.source_unit.external_ref ?? runEntry.source_unit.title}
                {last
                  ? ` · ${last.reviewer_id} · ${formatDateTime(last.decided_at)}${duration ? ` · ${duration}` : ""}`
                  : " · bağlı olduğu raviye verilen karar üzerine"}
              </span>
              {last?.reviewer_note ? (
                <span className="muted small history-note">Not: {last.reviewer_note}</span>
              ) : null}
            </li>
          );
        })}
      </ul>
    </details>
  );
}
