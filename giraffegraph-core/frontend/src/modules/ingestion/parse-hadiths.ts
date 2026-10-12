import type { BulkSourceUnitItem } from "@/modules/projects/types";

export interface ParsedInput {
  items: BulkSourceUnitItem[];
  /** How the text was understood, so the screen can say it back. */
  kind: "json" | "text";
}

function requireText(value: unknown, field: string, rowNo: number): string {
  const text = typeof value === "number" ? String(value) : value;
  if (typeof text !== "string" || text.trim() === "") {
    throw new Error(`${rowNo}. kayıtta “${field}” alanı boş ya da yazı değil.`);
  }
  return text;
}

/**
 * Reads a JSON list of hadiths. Two shapes are accepted:
 * {external_ref, title, raw_content} and the corpus shape {coll, num, raw}.
 */
export function parseHadithJson(text: string): BulkSourceUnitItem[] {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    throw new Error(
      "Bu metin bir JSON listesi gibi başlıyor ama okunamadı. Dosyadan kopyaladıysan başını ve sonunu eksiksiz aldığından emin ol.",
    );
  }
  if (!Array.isArray(parsed) || parsed.length === 0) {
    throw new Error("JSON içinde en az bir hadis bulunan bir liste olmalı.");
  }
  return parsed.map((row: unknown, index) => {
    const rowNo = index + 1;
    if (typeof row !== "object" || row === null || Array.isArray(row)) {
      throw new Error(`${rowNo}. kayıt beklenen biçimde değil.`);
    }
    const record = row as Record<string, unknown>;
    if ("external_ref" in record || "raw_content" in record) {
      const externalRef = requireText(record.external_ref, "external_ref", rowNo).trim();
      return {
        external_ref: externalRef,
        title:
          typeof record.title === "string" && record.title.trim() ? record.title : externalRef,
        raw_content: requireText(record.raw_content, "raw_content", rowNo),
      };
    }
    if ("coll" in record || "num" in record || "raw" in record) {
      const externalRef = `${requireText(record.coll, "coll", rowNo).trim()}:${requireText(record.num, "num", rowNo).trim()}`;
      return {
        external_ref: externalRef,
        title: externalRef,
        raw_content: requireText(record.raw, "raw", rowNo),
      };
    }
    throw new Error(
      `${rowNo}. kayıt tanınmadı. Her kayıtta ya “external_ref” ve “raw_content” ya da “coll”, “num” ve “raw” alanları olmalı.`,
    );
  });
}

/**
 * Reads pasted plain text: hadiths are separated by an empty line. Each one gets
 * a reference "<label>:<n>", numbered after the ones the project already has.
 */
export function parsePlainText(
  text: string,
  label: string,
  existingRefs: readonly string[],
): BulkSourceUnitItem[] {
  const prefix = `${label.trim() || "metin"}:`;
  const taken = existingRefs
    .filter((ref) => ref.startsWith(prefix))
    .map((ref) => Number(ref.slice(prefix.length)))
    .filter((value) => Number.isInteger(value));
  let next = taken.length > 0 ? Math.max(...taken) + 1 : 1;

  return text
    .split(/\n\s*\n/)
    .map((block) => block.trim())
    .filter((block) => block !== "")
    .map((block) => {
      const externalRef = `${prefix}${next}`;
      next += 1;
      return { external_ref: externalRef, title: externalRef, raw_content: block };
    });
}

export function parseInput(
  text: string,
  label: string,
  existingRefs: readonly string[],
): ParsedInput {
  const trimmed = text.trim();
  if (trimmed.startsWith("[") || trimmed.startsWith("{")) {
    return { items: parseHadithJson(trimmed), kind: "json" };
  }
  return { items: parsePlainText(trimmed, label, existingRefs), kind: "text" };
}
