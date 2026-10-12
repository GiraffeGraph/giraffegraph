"use client";

import { useMemo, useRef, useState } from "react";

import { parseHadithJson, parseInput, type ParsedInput } from "@/modules/ingestion/parse-hadiths";
import { bulkCreateSourceUnits } from "@/modules/projects/api";
import { useProject } from "@/modules/projects/components/project-shell";
import { nextStepWithWork, STEP_ACTION, stepHref } from "@/modules/projects/status";
import type { BulkSourceUnitItem, SourceUnitStatus } from "@/modules/projects/types";
import { Button, ButtonLink } from "@/shared/ui/button";
import { ErrorNote, Note } from "@/shared/ui/states";

const SAMPLE_URL = "/samples/ornek-hadisler.json";
const SAMPLE_COUNT = 10;
const UPLOAD_BATCH_SIZE = 500;
const SHOWN_DUPLICATES = 5;

const HADITH_STATE: Record<SourceUnitStatus, string> = {
  draft: "taslak",
  ready: "zinciri çıkarılmadı",
  processing: "karar ya da yazma bekliyor",
  processed: "grafta",
  failed: "işlenemedi, yeniden denenebilir",
};

interface LoadResult {
  created: number;
  duplicates: string[];
}

function describeResult(result: LoadResult): string {
  const { created, duplicates } = result;
  if (created === 0) {
    return duplicates.length === 1
      ? "Yeni hadis eklenmedi; gönderdiğin hadis bu projede zaten var."
      : `Yeni hadis eklenmedi; gönderdiğin ${duplicates.length} hadisin hepsi bu projede zaten var.`;
  }
  if (duplicates.length === 0) {
    return `${created} hadis yüklendi.`;
  }
  const shown = duplicates.slice(0, SHOWN_DUPLICATES).join(", ");
  const rest = duplicates.length - SHOWN_DUPLICATES;
  return `${created} hadis yüklendi. ${duplicates.length} hadis bu projede zaten olduğu için atlandı: ${shown}${rest > 0 ? ` ve ${rest} tane daha` : ""}.`;
}

export function LoadScreen() {
  const { project, status, refreshStatus } = useProject();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [text, setText] = useState("");
  const [label, setLabel] = useState("metin");
  const [fileName, setFileName] = useState<string | null>(null);
  const [busy, setBusy] = useState<"load" | "sample" | null>(null);
  const [result, setResult] = useState<LoadResult | null>(null);
  const [error, setError] = useState<{ title: string; reason: unknown } | null>(null);

  const existingRefs = useMemo(
    () => (status?.hadiths ?? []).flatMap((hadith) => hadith.external_ref ?? []),
    [status],
  );

  const preview = useMemo<{ parsed: ParsedInput | null; problem: string | null }>(() => {
    if (text.trim() === "") {
      return { parsed: null, problem: null };
    }
    try {
      return { parsed: parseInput(text, label, existingRefs), problem: null };
    } catch (reason: unknown) {
      return {
        parsed: null,
        problem: reason instanceof Error ? reason.message : "Metin okunamadı.",
      };
    }
  }, [text, label, existingRefs]);

  const items = preview.parsed?.items ?? [];
  const hasText = text.trim() !== "";
  const total = status?.total ?? 0;
  const next = status ? nextStepWithWork(status) : null;

  async function upload(hadiths: BulkSourceUnitItem[]): Promise<LoadResult> {
    const outcome: LoadResult = { created: 0, duplicates: [] };
    for (let start = 0; start < hadiths.length; start += UPLOAD_BATCH_SIZE) {
      const report = await bulkCreateSourceUnits(project.project_id, {
        source_type: project.template_id === "isnad" ? "hadith" : "document",
        items: hadiths.slice(start, start + UPLOAD_BATCH_SIZE),
      });
      outcome.created += report.created_count;
      outcome.duplicates.push(
        ...report.results.filter((row) => row.status === "duplicate").map((row) => row.external_ref),
      );
    }
    return outcome;
  }

  async function run(kind: "load" | "sample") {
    setBusy(kind);
    setError(null);
    setResult(null);
    try {
      let hadiths = items;
      if (kind === "sample") {
        const response = await fetch(SAMPLE_URL);
        if (!response.ok) {
          throw new Error("Örnek dosyası uygulamanın içinde bulunamadı.");
        }
        hadiths = parseHadithJson(await response.text());
      }
      const outcome = await upload(hadiths);
      setResult(outcome);
      if (kind === "load" && outcome.created > 0) {
        setText("");
        setFileName(null);
      }
      await refreshStatus();
    } catch (reason: unknown) {
      setError({
        title: kind === "sample" ? "Örnek hadisler yüklenemedi." : "Hadisler yüklenemedi.",
        reason,
      });
    } finally {
      setBusy(null);
    }
  }

  async function readFile(file: File | undefined) {
    if (!file) {
      return;
    }
    setError(null);
    setResult(null);
    try {
      setText(await file.text());
      setFileName(file.name);
    } catch (reason: unknown) {
      setError({ title: "Dosya okunamadı.", reason });
    }
  }

  const samplePrimary = !hasText && total === 0 && result === null;
  const loadPrimary = hasText;

  return (
    <section className="step-screen" aria-labelledby="step-title">
      <div className="step-intro">
        <h2 id="step-title">Metin yükle</h2>
        <p className="lead">
          Üzerinde çalışacağın hadisleri buraya ekle. Her hadis ayrı bir kayıt olur; isnadı bir
          sonraki adımda çıkarılır.
        </p>
      </div>

      {result ? (
        <Note
          tone={result.created > 0 ? "done" : "neutral"}
          live
          actions={
            next && next !== "yukle" ? (
              <ButtonLink
                href={stepHref(project.project_id, next)}
                variant={hasText ? "secondary" : "primary"}
                iconAfter="arrowRight"
              >
                {STEP_ACTION[next]}
              </ButtonLink>
            ) : null
          }
        >
          <p>{describeResult(result)}</p>
        </Note>
      ) : total > 0 && next && next !== "yukle" ? (
        <Note
          actions={
            <ButtonLink
              href={stepHref(project.project_id, next)}
              variant={hasText ? "secondary" : "primary"}
              iconAfter="arrowRight"
            >
              {STEP_ACTION[next]}
            </ButtonLink>
          }
        >
          <p>
            Bu projede {total} hadis var. Yeni metin ekleyebilir ya da kaldığın adıma
            geçebilirsin.
          </p>
        </Note>
      ) : null}

      {error ? <ErrorNote title={error.title} error={error.reason} /> : null}

      <div className="load-layout">
        <div className="card stack">
          <label className="field">
            <span>Hadis metnini yapıştır</span>
            <textarea
              className="arabic-input"
              name="hadith-text"
              rows={6}
              dir="auto"
              value={text}
              onChange={(event) => {
                setText(event.currentTarget.value);
                setFileName(null);
                setResult(null);
              }}
              placeholder="حَدَّثَنَا …"
            />
            <span className="field-hint">
              Birden fazla hadis yapıştırıyorsan aralarında boş bir satır bırak.
            </span>
          </label>

          <div className="row">
            <input
              ref={fileInputRef}
              className="visually-hidden"
              type="file"
              accept=".json,application/json"
              tabIndex={-1}
              aria-hidden="true"
              onChange={(event) => {
                void readFile(event.currentTarget.files?.[0]);
                event.currentTarget.value = "";
              }}
            />
            <Button icon="file" size="sm" onClick={() => fileInputRef.current?.click()}>
              Dosya seç (.json)
            </Button>
            {fileName ? <span className="muted small">{fileName} okundu.</span> : null}
            <details className="disclosure">
              <summary>Dosya nasıl olmalı?</summary>
              <div className="disclosure-body stack-sm">
                <p>Dosya, hadislerin listesi olmalı. İki biçim de kabul edilir:</p>
                <pre dir="ltr">{'[{"external_ref": "Muslim:978", "title": "Müslim 978", "raw_content": "حَدَّثَنَا …"}]'}</pre>
                <pre dir="ltr">{'[{"coll": "Muslim", "num": "978", "raw": "حَدَّثَنَا …"}]'}</pre>
              </div>
            </details>
          </div>

          {preview.parsed?.kind === "text" ? (
            <label className="field load-label-field">
              <span>Bu metinlere verilecek kısa ad</span>
              <input
                type="text"
                name="hadith-label"
                maxLength={60}
                value={label}
                onChange={(event) => setLabel(event.currentTarget.value)}
              />
              <span className="field-hint">
                Her hadis bu adla numaralanır; listede {items[0]?.external_ref ?? "metin:1"} gibi
                görünür.
              </span>
            </label>
          ) : null}

          <p className="load-preview muted small" role="status">
            {preview.problem ? (
              <span className="status status-attention">{preview.problem}</span>
            ) : items.length > 0 ? (
              `${items.length} hadis okundu: ${items
                .slice(0, 4)
                .map((item) => item.external_ref)
                .join(", ")}${items.length > 4 ? " ve diğerleri" : ""}.`
            ) : (
              "Metin eklediğinde kaç hadis okunduğu burada yazar."
            )}
          </p>

          <div>
            <Button
              variant={loadPrimary ? "primary" : "secondary"}
              icon="upload"
              busy={busy === "load"}
              disabled={items.length === 0 || busy !== null}
              onClick={() => void run("load")}
            >
              {busy === "load"
                ? "Yükleniyor"
                : items.length > 0
                  ? `${items.length} hadisi yükle`
                  : "Yükle"}
            </Button>
          </div>
        </div>

        <aside className="card-plain stack">
          <h3>Elinde metin yok mu?</h3>
          <p className="muted">
            {SAMPLE_COUNT} örnek hadisi tek tıkla yükleyip bütün adımları deneyebilirsin. Örnekler
            Sanadset 650K derleminden alındı.
          </p>
          <div>
            <Button
              variant={samplePrimary ? "primary" : "secondary"}
              busy={busy === "sample"}
              disabled={busy !== null}
              onClick={() => void run("sample")}
            >
              {busy === "sample" ? "Yükleniyor" : "Örnek hadislerle dene"}
            </Button>
          </div>
        </aside>
      </div>

      {status && status.total > 0 ? (
        <details className="disclosure">
          <summary>Bu projedeki {status.total} hadisi göster</summary>
          <ul className="disclosure-body hadith-ref-list">
            {status.hadiths.map((hadith) => (
              <li key={hadith.source_unit_id}>
                <span>{hadith.external_ref ?? hadith.title}</span>
                <span className="muted">{HADITH_STATE[hadith.status]}</span>
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </section>
  );
}
