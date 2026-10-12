"use client";

import { useState, type FormEvent } from "react";

import type {
  CandidateNodeRecord,
  ReviewDecisionRequest,
  ReviewQueueItemRecord,
} from "@/modules/projects/types";
import {
  fieldLabel,
  NARRATED_FROM_TYPE,
  NARRATOR_TYPE,
  narratorName,
} from "@/modules/review/suggestion";
import { Button } from "@/shared/ui/button";

export type EditedFields = Pick<
  ReviewDecisionRequest,
  | "node_type"
  | "relation_type"
  | "properties"
  | "merge_key_payload"
  | "from_candidate_ref"
  | "to_candidate_ref"
>;

interface EditField {
  key: string;
  kind: "text" | "number";
  value: string;
}

/** What identifies a narrator link; shown even when the suggestion left one of them out. */
const LINK_FIELDS: Record<string, EditField["kind"]> = {
  hadith_ref: "text",
  chain_no: "number",
  position: "number",
  sigha: "text",
};

function buildFields(
  properties: Record<string, unknown>,
  isNarratorLink: boolean,
  hadithRef: string,
): EditField[] {
  const fields: EditField[] = Object.entries(properties).flatMap(([key, value]) =>
    typeof value === "string" || typeof value === "number"
      ? [{ key, kind: typeof value === "number" ? "number" : "text", value: String(value) }]
      : [],
  );
  if (isNarratorLink) {
    for (const [key, kind] of Object.entries(LINK_FIELDS)) {
      if (!fields.some((field) => field.key === key)) {
        fields.push({ key, kind, value: key === "hadith_ref" ? hadithRef : "" });
      }
    }
  }
  return fields;
}

function isArabicField(key: string): boolean {
  return key === "name" || key === "sigha";
}

/**
 * The correction form: one plain field per value of the suggestion. For a link the two
 * narrators can be changed as well, chosen among the narrators suggested for this hadith.
 */
export function EditForm({
  item,
  runNodes,
  hadithRef,
  busy,
  onSave,
  onCancel,
}: {
  item: ReviewQueueItemRecord;
  runNodes: CandidateNodeRecord[];
  hadithRef: string;
  busy: boolean;
  onSave: (fields: EditedFields) => void;
  onCancel: () => void;
}) {
  const node = item.candidate_node;
  const relation = item.candidate_relation;
  const original = node?.properties ?? relation?.properties ?? {};
  const [fields] = useState(() =>
    buildFields(original, relation?.relation_type === NARRATED_FROM_TYPE, hadithRef),
  );
  const [values, setValues] = useState<Record<string, string>>(() =>
    Object.fromEntries(fields.map((field) => [field.key, field.value])),
  );
  const [fromRef, setFromRef] = useState(relation?.from_candidate_ref ?? "");
  const [toRef, setToRef] = useState(relation?.to_candidate_ref ?? "");
  const [problem, setProblem] = useState<string | null>(null);

  const narrators = runNodes.filter(
    (candidate) => candidate.node_type === NARRATOR_TYPE && candidate.status !== "rejected",
  );

  function submit(event: FormEvent) {
    event.preventDefault();
    const properties: Record<string, unknown> = { ...original };
    for (const field of fields) {
      const typed = (values[field.key] ?? "").trim();
      if (typed === "") {
        setProblem(`“${fieldLabel(field.key)}” alanı boş bırakılamaz.`);
        return;
      }
      if (field.kind === "number") {
        const parsed = Number(typed);
        if (Number.isNaN(parsed)) {
          setProblem(`“${fieldLabel(field.key)}” alanına bir sayı yazmalısın.`);
          return;
        }
        properties[field.key] = parsed;
      } else {
        properties[field.key] = typed;
      }
    }
    setProblem(null);

    if (node) {
      const mergeKeys: Record<string, unknown> = { ...node.merge_key_payload };
      for (const key of Object.keys(mergeKeys)) {
        if (key in properties) {
          mergeKeys[key] = properties[key];
        }
      }
      onSave({ node_type: node.node_type, properties, merge_key_payload: mergeKeys });
    } else if (relation) {
      onSave({
        relation_type: relation.relation_type,
        properties,
        from_candidate_ref: fromRef,
        to_candidate_ref: toRef,
      });
    }
  }

  return (
    <form className="stack edit-form" onSubmit={submit}>
      <h3>Doğrusunu yaz</h3>
      {relation && narrators.length > 0 ? (
        <div className="field-grid">
          <label className="field">
            <span>Hadisi alan ravi</span>
            <select dir="rtl" lang="ar" value={fromRef} onChange={(event) => setFromRef(event.currentTarget.value)}>
              {narrators.map((candidate) => (
                <option key={candidate.candidate_node_id} value={candidate.candidate_node_id}>
                  {narratorName(candidate) ?? candidate.candidate_node_id}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Kimden almış</span>
            <select dir="rtl" lang="ar" value={toRef} onChange={(event) => setToRef(event.currentTarget.value)}>
              {narrators.map((candidate) => (
                <option key={candidate.candidate_node_id} value={candidate.candidate_node_id}>
                  {narratorName(candidate) ?? candidate.candidate_node_id}
                </option>
              ))}
            </select>
          </label>
        </div>
      ) : null}
      <div className="field-grid">
        {fields.map((field) => (
          <label key={field.key} className="field">
            <span>{fieldLabel(field.key)}</span>
            <input
              type="text"
              inputMode={field.kind === "number" ? "numeric" : undefined}
              dir={isArabicField(field.key) ? "rtl" : "auto"}
              lang={isArabicField(field.key) ? "ar" : undefined}
              className={isArabicField(field.key) ? "arabic-input" : undefined}
              value={values[field.key] ?? ""}
              onChange={(event) => {
                const value = event.currentTarget.value;
                setValues((current) => ({ ...current, [field.key]: value }));
              }}
            />
          </label>
        ))}
      </div>
      {problem ? (
        <p className="status status-attention" role="alert">
          {problem}
        </p>
      ) : null}
      <div className="row">
        <Button type="submit" variant="primary" busy={busy}>
          {busy ? "Kaydediliyor" : "Düzeltmeyi kaydet ve kabul et"}
        </Button>
        <Button variant="quiet" onClick={onCancel} disabled={busy}>
          Vazgeç
        </Button>
      </div>
    </form>
  );
}
