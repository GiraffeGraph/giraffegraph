import type { ReactNode } from "react";

type ArabicSize = "reading" | "md" | "sm";

const SIZE_CLASS: Record<ArabicSize, string> = {
  reading: "arabic arabic-reading",
  md: "arabic",
  sm: "arabic arabic-sm",
};

/** Arabic is always right-to-left and tagged with its language, wherever it appears. */
export function ArabicText({
  children,
  size = "md",
  as: Tag = "span",
  className,
}: {
  children: ReactNode;
  size?: ArabicSize;
  as?: "span" | "p" | "q" | "strong" | "h2" | "h3";
  className?: string;
}) {
  return (
    <Tag dir="rtl" lang="ar" className={`${SIZE_CLASS[size]}${className ? ` ${className}` : ""}`}>
      {children}
    </Tag>
  );
}

export interface TextMark {
  start: number;
  end: number;
  /** Clicking the mark calls this; without it the mark is a plain highlight. */
  onSelect?: () => void;
  selected?: boolean;
  title?: string;
}

/**
 * Splits a text into plain runs and highlighted runs.
 * Marks must be sorted and must not overlap. `unit` says how the offsets count:
 * the backend counts Unicode code points, JavaScript string methods count UTF-16 units.
 */
export function renderMarkedText(
  text: string,
  marks: TextMark[],
  unit: "codepoint" | "utf16" = "utf16",
): ReactNode[] {
  const chars = unit === "codepoint" ? Array.from(text) : null;
  const slice = (start: number, end?: number) =>
    chars ? chars.slice(start, end).join("") : text.slice(start, end);
  const length = chars ? chars.length : text.length;

  const parts: ReactNode[] = [];
  let cursor = 0;
  marks.forEach((mark, index) => {
    if (mark.start > cursor) {
      parts.push(slice(cursor, mark.start));
    }
    const onSelect = mark.onSelect;
    parts.push(
      onSelect ? (
        <mark
          key={index}
          role="button"
          tabIndex={0}
          title={mark.title}
          className={mark.selected ? "is-selected" : undefined}
          aria-pressed={mark.selected ?? false}
          onClick={onSelect}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              onSelect();
            }
          }}
        >
          {slice(mark.start, mark.end)}
        </mark>
      ) : (
        <mark key={index} title={mark.title}>
          {slice(mark.start, mark.end)}
        </mark>
      ),
    );
    cursor = mark.end;
  });
  if (cursor < length) {
    parts.push(slice(cursor));
  }
  return parts;
}

const ARABIC_MARKS = /[ً-ٰٟـ]/;

/**
 * Finds a quotation inside a text. Tries the exact words first, then ignores
 * Arabic vowel signs and elongation, which is how the server compares them too.
 * Returns UTF-16 offsets, or null when the words are not there.
 */
export function findQuote(text: string, quote: string): { start: number; end: number } | null {
  const needle = quote.trim();
  if (needle === "") {
    return null;
  }
  const exact = text.indexOf(needle);
  if (exact >= 0) {
    return { start: exact, end: exact + needle.length };
  }

  const positions: number[] = [];
  let folded = "";
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (ARABIC_MARKS.test(char)) {
      continue;
    }
    folded += char;
    positions.push(index);
  }
  const foldedNeedle = Array.from(needle)
    .filter((char) => !ARABIC_MARKS.test(char))
    .join("");
  if (foldedNeedle === "") {
    return null;
  }
  const found = folded.indexOf(foldedNeedle);
  if (found < 0) {
    return null;
  }
  const last = positions[found + foldedNeedle.length - 1];
  let end = last + 1;
  while (end < text.length && ARABIC_MARKS.test(text[end])) {
    end += 1;
  }
  return { start: positions[found], end };
}
