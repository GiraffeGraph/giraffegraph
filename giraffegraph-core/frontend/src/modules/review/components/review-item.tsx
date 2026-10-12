"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import type { CandidateNodeRecord, ReviewDecisionRequest } from "@/modules/projects/types";
import { EditForm, type EditedFields } from "@/modules/review/components/edit-form";
import { SuggestionView } from "@/modules/review/components/suggestion-view";
import { decisionRefusal, reasonSentence } from "@/modules/review/reasons";
import { describeSuggestion, quotesOf, type ReviewEntry } from "@/modules/review/suggestion";
import { ArabicText, findQuote, renderMarkedText, type TextMark } from "@/shared/ui/arabic-text";
import { Button } from "@/shared/ui/button";
import { Icon } from "@/shared/ui/icons";
import { ErrorNote, LoadingBlock } from "@/shared/ui/states";

export type DecisionDraft = Pick<ReviewDecisionRequest, "action" | "reviewer_note"> & EditedFields;

/** The hadith text is loading, could not be read, or is here. */
export type HadithText = { state: "loading" } | { state: "missing" } | { state: "ready"; raw: string };

function locateQuotes(raw: string, quotes: string[]): { marks: TextMark[]; notFound: string[] } {
  const found: TextMark[] = [];
  const notFound: string[] = [];
  for (const quote of quotes) {
    const range = findQuote(raw, quote);
    if (range) {
      found.push(range);
    } else {
      notFound.push(quote);
    }
  }
  found.sort((left, right) => left.start - right.start || right.end - left.end);
  const marks: TextMark[] = [];
  let cursor = 0;
  for (const mark of found) {
    if (mark.start >= cursor) {
      marks.push(mark);
      cursor = mark.end;
    }
  }
  return { marks, notFound };
}

export function ReviewItem({
  entry,
  text,
  runNodes,
  remaining,
  busyAction,
  error,
  onDecide,
  onSkip,
}: {
  entry: ReviewEntry;
  text: HadithText;
  runNodes: CandidateNodeRecord[];
  remaining: number;
  busyAction: ReviewDecisionRequest["action"] | null;
  error: unknown;
  onDecide: (draft: DecisionDraft) => void;
  onSkip: (() => void) | null;
}) {
  const { item, runEntry } = entry;
  const [editing, setEditing] = useState(false);
  const [note, setNote] = useState("");
  const textRef = useRef<HTMLDivElement>(null);

  const hadithRef = runEntry.source_unit.external_ref ?? runEntry.source_unit.title;
  const suggestion = useMemo(() => describeSuggestion(item, runNodes), [item, runNodes]);
  const quotes = useMemo(() => quotesOf(item), [item]);
  const located = useMemo(
    () => (text.state === "ready" ? locateQuotes(text.raw, quotes) : null),
    [text, quotes],
  );
  const fallbackText = item.evidence_snippets.find((snippet) => snippet.text)?.text ?? null;
  const reviewerNote = note.trim() || null;
  const busy = busyAction !== null;
  // A link that only waits for one of its narrators cannot be accepted yet; the server refuses it.
  const waitsForNarrator = item.review_item.reason_code === "relation_dependency_review";
  const canAccept = !waitsForNarrator;
  const canEdit = suggestion.kind !== "proposal" && !waitsForNarrator;

  useEffect(() => {
    const container = textRef.current;
    const mark = container?.querySelector("mark");
    if (container && mark) {
      container.scrollTop = Math.max(0, mark.offsetTop - container.clientHeight / 3);
    }
  }, [located]);

  const details = [
    ...Array.from(new Set(item.messages)),
    item.confidence !== null ? `Sistemin güven puanı: ${item.confidence.toFixed(2)}` : null,
    `Neden kodu: ${item.review_item.reason_code}`,
  ].filter((line): line is string => line !== null);

  return (
    <article className="review-item" aria-labelledby="review-item-title">
      <header className="row-between">
        <div className="stack-sm">
          <p className="status status-attention">
            <Icon name="person" />
            Senin kararını bekliyor
          </p>
          <h3 id="review-item-title">{hadithRef}</h3>
        </div>
        <p className="muted small num" role="status">
          {remaining === 1 ? "Bekleyen son öneri" : `Bekleyen ${remaining} öneri var`}
        </p>
      </header>

      <div className="review-layout">
        <section className="stack-sm" aria-label="Hadis metni">
          <div className="arabic-block review-text" ref={textRef} tabIndex={0}>
            {text.state === "loading" ? (
              <LoadingBlock label="Hadis metni yükleniyor" lines={5} />
            ) : text.state === "ready" ? (
              <ArabicText as="p" size="reading">
                {renderMarkedText(text.raw, located?.marks ?? [])}
              </ArabicText>
            ) : fallbackText ? (
              <ArabicText as="p" size="reading">
                {fallbackText}
              </ArabicText>
            ) : (
              <p className="muted">Hadis metni okunamadı.</p>
            )}
          </div>
          <p className="muted small">
            {text.state === "missing" && fallbackText
              ? "Metnin tamamı okunamadı; yalnızca önerinin çıkarıldığı bölüm gösteriliyor."
              : located && located.marks.length > 0
                ? "Renkli bölüm, sistemin bu öneri için gösterdiği alıntıdır."
                : "Bu öneri için metinde işaretlenecek bir alıntı yok."}
          </p>
        </section>

        <div className="stack">
          <section className="card stack" aria-labelledby="suggestion-title">
            <h4 id="suggestion-title">Sistemin önerisi</h4>
            <SuggestionView suggestion={suggestion} />
            {quotes.length > 0 ? (
              <div className="stack-sm">
                <p className="muted small">
                  {located && located.notFound.length > 0
                    ? "Gösterdiği alıntı (metinde bulunamadı):"
                    : "Dayandığı alıntı:"}
                </p>
                {quotes.map((quote) => (
                  <ArabicText key={quote} as="q" size="sm" className="quote">
                    {quote}
                  </ArabicText>
                ))}
              </div>
            ) : null}
          </section>

          <section className="note note-attention" aria-labelledby="reason-title">
            <Icon name="alert" />
            <div className="note-body">
              <h4 id="reason-title">Neden bekliyor?</h4>
              <p>{reasonSentence(item.review_item.reason_code)}</p>
              <details className="disclosure">
                <summary>ayrıntı</summary>
                <ul className="disclosure-body stack-sm">
                  {details.map((line) => (
                    <li key={line}>{line}</li>
                  ))}
                </ul>
              </details>
            </div>
          </section>

          {error ? (
            <ErrorNote
              title="Karar kaydedilemedi."
              error={error}
              advice={decisionRefusal(error)}
            />
          ) : null}

          {editing ? (
            <EditForm
              item={item}
              runNodes={runNodes}
              hadithRef={hadithRef}
              busy={busyAction === "edit"}
              onSave={(fields) => onDecide({ action: "edit", reviewer_note: reviewerNote, ...fields })}
              onCancel={() => setEditing(false)}
            />
          ) : (
            <div className="stack">
              <div className="decision-actions">
                {canAccept ? (
                  <Button
                    variant="primary"
                    icon="check"
                    busy={busyAction === "accept"}
                    disabled={busy}
                    onClick={() => onDecide({ action: "accept", reviewer_note: reviewerNote })}
                  >
                    Doğru, kabul et
                  </Button>
                ) : null}
                <Button
                  icon="close"
                  busy={busyAction === "reject"}
                  disabled={busy}
                  onClick={() => onDecide({ action: "reject", reviewer_note: reviewerNote })}
                >
                  Yanlış, reddet
                </Button>
                {canEdit ? (
                  <Button icon="pencil" disabled={busy} onClick={() => setEditing(true)}>
                    Düzelt
                  </Button>
                ) : null}
              </div>
              <div className="row">
                {onSkip ? (
                  <Button variant="quiet" size="sm" disabled={busy} onClick={onSkip}>
                    Şimdilik geç
                  </Button>
                ) : null}
                <details className="disclosure">
                  <summary>Karara not ekle</summary>
                  <label className="field review-note">
                    <span className="visually-hidden">Kararın için not</span>
                    <textarea
                      name="reviewer-note"
                      rows={2}
                      value={note}
                      onChange={(event) => setNote(event.currentTarget.value)}
                      placeholder="İstersen neden böyle karar verdiğini yaz."
                    />
                  </label>
                </details>
              </div>
            </div>
          )}
        </div>
      </div>
    </article>
  );
}
