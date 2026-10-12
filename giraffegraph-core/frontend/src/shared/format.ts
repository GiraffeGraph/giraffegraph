const DATE_TIME = new Intl.DateTimeFormat("tr-TR", { dateStyle: "medium", timeStyle: "short" });

export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return "tarih yok";
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : DATE_TIME.format(date);
}

export function formatSeconds(durationMs: number | null): string | null {
  if (durationMs === null) {
    return null;
  }
  return `${Math.max(1, Math.round(durationMs / 1000))} sn`;
}

const UNIT_SUFFIX = ["", "'i", "'si", "'ü", "'ü", "'i", "'sı", "'si", "'i", "'u"];
const TENS_SUFFIX = ["", "'u", "'si", "'u", "'ı", "'si", "'ı", "'i", "'i", "'ı"];

/**
 * A count with its Turkish possessive ending, as in "30'u grafta" or "2'si bekliyor".
 * The ending follows how the number is read aloud, so it depends on the last spoken part.
 */
export function countWithPossessive(count: number): string {
  const n = Math.abs(Math.trunc(count));
  const unit = n % 10;
  const ten = Math.trunc(n / 10) % 10;
  let suffix: string;
  if (n === 0) {
    suffix = "'ı";
  } else if (unit !== 0) {
    suffix = UNIT_SUFFIX[unit];
  } else if (ten !== 0) {
    suffix = TENS_SUFFIX[ten];
  } else if (n % 1000 !== 0) {
    suffix = "'ü";
  } else if (n % 1_000_000 !== 0) {
    suffix = "'i";
  } else {
    suffix = "'u";
  }
  return `${n}${suffix}`;
}
