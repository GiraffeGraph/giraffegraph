import type { FactAcceptanceRecord } from "@/modules/projects/types";
import { formatDateTime } from "@/shared/format";
import { Icon } from "@/shared/ui/icons";

/**
 * Who accepted a fact. A person's approval and an automatic acceptance are worded
 * differently on purpose: passing the checks is not the same as being verified by someone.
 */
export function Acceptance({ acceptance }: { acceptance: FactAcceptanceRecord | null }) {
  if (!acceptance) {
    return (
      <span className="status status-attention">
        <Icon name="alert" />
        Kabul kaydı bulunamadı
      </span>
    );
  }
  if (acceptance.kind === "human") {
    return (
      <span className="status status-done">
        <Icon name="person" />
        İnsan onayladı: {acceptance.reviewer_id ?? "adı kaydedilmemiş"},{" "}
        {formatDateTime(acceptance.decided_at)}
        {acceptance.action === "edit" ? " (düzelterek)" : ""}
      </span>
    );
  }
  return (
    <span
      className="status status-neutral"
      title={acceptance.rule_code ? `Geçtiği kontrol: ${acceptance.rule_code}` : undefined}
    >
      <Icon name="rule" />
      Otomatik kabul edildi (kontrollerden geçti)
    </span>
  );
}

export function isHumanAccepted(acceptance: FactAcceptanceRecord | null | undefined): boolean {
  return acceptance?.kind === "human";
}
