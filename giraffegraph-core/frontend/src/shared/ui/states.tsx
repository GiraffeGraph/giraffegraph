import type { ReactNode } from "react";

import { explainError } from "@/shared/api/errors";
import { Button } from "@/shared/ui/button";
import { Icon, type IconName } from "@/shared/ui/icons";

/** What will appear here, and what to do next. */
export function EmptyState({
  icon = "inbox",
  title,
  children,
  action,
}: {
  icon?: IconName;
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="empty">
      <Icon name={icon} />
      <h3>{title}</h3>
      <p>{children}</p>
      {action}
    </div>
  );
}

type NoteTone = "neutral" | "attention" | "done";

const NOTE_ICON: Record<NoteTone, IconName> = {
  neutral: "info",
  attention: "alert",
  done: "check",
};

export function Note({
  tone = "neutral",
  children,
  actions,
  live = false,
}: {
  tone?: NoteTone;
  children: ReactNode;
  actions?: ReactNode;
  /** Announce the note to screen readers when it appears. */
  live?: boolean;
}) {
  return (
    <div
      className={`note${tone === "neutral" ? "" : ` note-${tone}`}`}
      role={live ? "status" : undefined}
    >
      <Icon name={NOTE_ICON[tone]} />
      <div className="note-body">
        {children}
        {actions ? <div className="note-actions">{actions}</div> : null}
      </div>
    </div>
  );
}

/** What happened, what the person can do, and the raw message behind a disclosure. */
export function ErrorNote({
  title,
  error,
  advice: specificAdvice,
  onRetry,
  actions,
}: {
  title: string;
  error: unknown;
  /** A sentence that fits this situation better than the general one for the error. */
  advice?: string | null;
  onRetry?: () => void;
  actions?: ReactNode;
}) {
  const explanation = explainError(error);
  const advice = specificAdvice ?? explanation.advice;
  const detail = explanation.detail;
  return (
    <div className="note note-attention" role="alert">
      <Icon name="alert" />
      <div className="note-body">
        <p>
          <strong>{title}</strong> {advice}
        </p>
        {detail ? (
          <details className="disclosure">
            <summary>ayrıntı</summary>
            <div className="disclosure-body">
              <pre>{detail}</pre>
            </div>
          </details>
        ) : null}
        {onRetry || actions ? (
          <div className="note-actions">
            {onRetry ? (
              <Button size="sm" onClick={onRetry}>
                Tekrar dene
              </Button>
            ) : null}
            {actions}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export function Skeleton({ width = "100%", height = "1em" }: { width?: string; height?: string }) {
  return <span className="skeleton" aria-hidden="true" style={{ width, height }} />;
}

/** A hidden live region plus a visible placeholder, so loading neither jumps nor stays silent. */
export function LoadingBlock({ label, lines = 3 }: { label: string; lines?: number }) {
  return (
    <div className="stack-sm" role="status">
      <span className="visually-hidden">{label}</span>
      {Array.from({ length: lines }, (_, index) => (
        <Skeleton key={index} width={`${92 - index * 14}%`} height="1.1em" />
      ))}
    </div>
  );
}
