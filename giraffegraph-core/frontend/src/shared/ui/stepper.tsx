import Link from "next/link";

import { Icon } from "@/shared/ui/icons";
import { Skeleton } from "@/shared/ui/states";

export type StepTone = "idle" | "done" | "attention";

export interface StepItem {
  key: string;
  href: string;
  title: string;
  /** One short line under the title: how much is here, or how much is waiting. */
  count: string | null;
  tone: StepTone;
}

export function Stepper({ steps, currentKey }: { steps: StepItem[]; currentKey: string | null }) {
  return (
    <nav aria-label="Adımlar">
      <ol className="stepper">
        {steps.map((step, index) => {
          const isCurrent = step.key === currentKey;
          const toneClass = step.tone === "idle" ? "" : ` is-${step.tone}`;
          return (
            <li key={step.key}>
              <Link
                href={step.href}
                className={`step${toneClass}`}
                aria-current={isCurrent ? "step" : undefined}
              >
                <span className="step-badge" aria-hidden="true">
                  {step.tone === "done" && !isCurrent ? <Icon name="check" /> : index + 1}
                </span>
                <span>
                  <span className="step-title">
                    <span className="visually-hidden">{index + 1}. adım: </span>
                    {step.title}
                  </span>
                  <span className="step-count num">
                    {step.count ?? <Skeleton width="70%" height="0.8em" />}
                  </span>
                </span>
              </Link>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
