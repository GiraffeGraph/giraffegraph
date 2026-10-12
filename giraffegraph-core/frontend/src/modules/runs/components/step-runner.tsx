"use client";

import { useEffect, useState, type FormEvent } from "react";

import {
  commitRun,
  createSourceUnit,
  extractCandidates,
  generateSegments,
  listSchemaVersions,
  listSourceUnits,
  resolveDuplicates,
  startProcessingRun,
  validateRun,
} from "@/modules/projects/api";
import type {
  ProjectRecord,
  SchemaVersionRecord,
  SourceUnitStatus,
  SourceUnitSummaryRecord,
} from "@/modules/projects/types";
import { explainError } from "@/shared/api/errors";
import { formatDateTime } from "@/shared/format";
import { Button } from "@/shared/ui/button";
import { ErrorNote, LoadingBlock } from "@/shared/ui/states";

const UNIT_STATUS: Record<SourceUnitStatus, { text: string; tone: string }> = {
  draft: { text: "taslak", tone: "" },
  ready: { text: "hazır", tone: "" },
  processing: { text: "işleniyor", tone: "tag-attention" },
  processed: { text: "grafta", tone: "tag-done" },
  failed: { text: "hata", tone: "tag-attention" },
};

const PROVIDERS = [
  { value: "rule_based_isnad", label: "rule_based_isnad (kurallar, anahtar gerekmez)" },
  { value: "anthropic", label: "anthropic (sunucuda anahtar gerekir)" },
  { value: "openai", label: "openai (sunucuda anahtar gerekir)" },
  { value: "noop", label: "noop (öneri üretmez)" },
];

/** Developer view: one source unit, each pipeline call run by hand. */
export function StepRunner({ project }: { project: ProjectRecord }) {
  const [sourceUnits, setSourceUnits] = useState<SourceUnitSummaryRecord[] | null>(null);
  const [schemas, setSchemas] = useState<SchemaVersionRecord[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    void Promise.all([listSourceUnits(project.project_id), listSchemaVersions(project.project_id)])
      .then(([units, schemaList]) => {
        if (cancelled) {
          return;
        }
        setSourceUnits(units);
        setSchemas(schemaList);
        setSelectedId((current) => current ?? units[0]?.source_unit_id ?? null);
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setError(reason);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [project.project_id, reloadToken]);

  const activeSchema = schemas.find((schema) => schema.status === "active") ?? schemas[0] ?? null;
  const selected = sourceUnits?.find((unit) => unit.source_unit_id === selectedId) ?? null;

  return (
    <div className="adv-layout">
      <div className="card stack">
        <div className="row-between">
          <h3>Kaynak birimleri</h3>
          <Button size="sm" variant="quiet" onClick={() => setReloadToken((token) => token + 1)}>
            Yenile
          </Button>
        </div>
        {error ? (
          <ErrorNote title="Kaynak birimleri okunamadı." error={error} />
        ) : sourceUnits === null ? (
          <LoadingBlock label="Kaynak birimleri yükleniyor" />
        ) : sourceUnits.length === 0 ? (
          <p className="muted small">
            Bu projede kaynak birimi yok. Aşağıdan bir tane ekleyebilir ya da “Metin yükle”
            adımını kullanabilirsin.
          </p>
        ) : (
          <ul className="list-rows list-rows-scroll">
            {sourceUnits.map((unit) => (
              <li key={unit.source_unit_id}>
                <button
                  type="button"
                  className={`list-row${unit.source_unit_id === selectedId ? " is-selected" : ""}`}
                  onClick={() => setSelectedId(unit.source_unit_id)}
                >
                  <span className="row-between">
                    <strong>{unit.title}</strong>
                    <span className={`tag ${UNIT_STATUS[unit.status].tone}`}>
                      {UNIT_STATUS[unit.status].text}
                    </span>
                  </span>
                  <span className="muted small">
                    {unit.source_type} · {formatDateTime(unit.created_at)}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
        {sourceUnits !== null ? (
          <CreateSourceUnitForm
            project={project}
            activeSchema={activeSchema}
            onCreated={(unit) => {
              setSourceUnits((current) => [unit, ...(current ?? [])]);
              setSelectedId(unit.source_unit_id);
            }}
          />
        ) : null}
      </div>

      <div className="card stack">
        {selected ? (
          <Runner
            key={selected.source_unit_id}
            project={project}
            sourceUnit={selected}
            schemas={schemas}
            activeSchema={activeSchema}
          />
        ) : (
          <p className="muted">Adımlarını çalıştırmak için soldan bir kaynak birimi seç.</p>
        )}
      </div>
    </div>
  );
}

function CreateSourceUnitForm({
  project,
  activeSchema,
  onCreated,
}: {
  project: ProjectRecord;
  activeSchema: SchemaVersionRecord | null;
  onCreated: (unit: SourceUnitSummaryRecord) => void;
}) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [sourceType, setSourceType] = useState(project.template_id === "isnad" ? "hadith" : "document");
  const [content, setContent] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!activeSchema) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      onCreated(
        await createSourceUnit(project.project_id, {
          schema_version_id: activeSchema.schema_version_id,
          source_type: sourceType.trim(),
          title: title.trim(),
          raw_content: content,
        }),
      );
      setTitle("");
      setContent("");
      setOpen(false);
    } catch (reason: unknown) {
      setError(reason);
    } finally {
      setBusy(false);
    }
  }

  if (!open) {
    return (
      <div>
        <Button size="sm" icon="plus" onClick={() => setOpen(true)}>
          Tek kaynak birimi ekle
        </Button>
      </div>
    );
  }

  return (
    <form className="card-plain stack" onSubmit={submit}>
      <h4>Yeni kaynak birimi</h4>
      {activeSchema ? (
        <p className="muted small">Şema sürümü {activeSchema.version_no} ile kaydedilir.</p>
      ) : (
        <p className="status status-attention">
          Etkin şema yok. Önce Şema bölümünden bir sürüm oluşturup etkinleştir.
        </p>
      )}
      <div className="field-grid">
        <label className="field">
          <span>Başlık</span>
          <input required type="text" value={title} onChange={(event) => setTitle(event.currentTarget.value)} />
        </label>
        <label className="field">
          <span>Kaynak türü</span>
          <input type="text" value={sourceType} onChange={(event) => setSourceType(event.currentTarget.value)} />
        </label>
      </div>
      <label className="field">
        <span>Ham metin</span>
        <textarea required rows={6} dir="auto" value={content} onChange={(event) => setContent(event.currentTarget.value)} />
      </label>
      {error ? <ErrorNote title="Kaynak birimi kaydedilemedi." error={error} /> : null}
      <div className="row">
        <Button
          type="submit"
          variant="primary"
          size="sm"
          busy={busy}
          disabled={!title.trim() || !content.trim() || !activeSchema}
        >
          Kaydet
        </Button>
        <Button variant="quiet" size="sm" onClick={() => setOpen(false)}>
          Vazgeç
        </Button>
      </div>
    </form>
  );
}

type StepState = "idle" | "running" | "done" | "error";

interface StepResult {
  state: StepState;
  /** What the call returned, in a short phrase, or what went wrong. */
  summary: string | null;
}

type StepKey = "segments" | "run" | "extract" | "validate" | "resolve" | "commit";

const STEP_ORDER: StepKey[] = ["segments", "run", "extract", "validate", "resolve", "commit"];

const STEP_TEXT: Record<StepKey, { label: string; hint: string }> = {
  segments: { label: "Segment oluştur", hint: "Metni işlenebilir parçalara böler." },
  run: { label: "Çalıştırma başlat", hint: "Şema ve pipeline sürümüyle bir run açar." },
  extract: { label: "Aday çıkar", hint: "Sağlayıcı, segmentlerden düğüm ve ilişki adayları üretir." },
  validate: { label: "Doğrula", hint: "Adayları şema kurallarına ve metne göre denetler." },
  resolve: { label: "Yinelenenleri çöz", hint: "Aynı kimliği taşıyan adayları işaretler." },
  commit: { label: "Grafa yaz", hint: "Doğrulanan adayları grafa yazar. Geri alınamaz." },
};

const IDLE_STEPS: Record<StepKey, StepResult> = {
  segments: { state: "idle", summary: null },
  run: { state: "idle", summary: null },
  extract: { state: "idle", summary: null },
  validate: { state: "idle", summary: null },
  resolve: { state: "idle", summary: null },
  commit: { state: "idle", summary: null },
};

function Runner({
  project,
  sourceUnit,
  schemas,
  activeSchema,
}: {
  project: ProjectRecord;
  sourceUnit: SourceUnitSummaryRecord;
  schemas: SchemaVersionRecord[];
  activeSchema: SchemaVersionRecord | null;
}) {
  const isIsnad = project.template_id === "isnad";
  const [steps, setSteps] = useState(IDLE_STEPS);
  const [runId, setRunId] = useState<string | null>(null);
  const [schemaId, setSchemaId] = useState(activeSchema?.schema_version_id ?? "");
  const [pipelineVersion, setPipelineVersion] = useState("v1");
  const [provider, setProvider] = useState(isIsnad ? "rule_based_isnad" : "openai");
  const [model, setModel] = useState("");

  async function runStep(key: StepKey) {
    setSteps((current) => ({ ...current, [key]: { state: "running", summary: null } }));
    try {
      let summary: string;
      if (key === "segments") {
        const segments = await generateSegments(
          sourceUnit.source_unit_id,
          isIsnad ? "isnad" : "paragraphs",
        );
        summary = `${segments.length} segment oluşturuldu.`;
      } else if (key === "run") {
        const run = await startProcessingRun(sourceUnit.source_unit_id, {
          schema_version_id: schemaId,
          pipeline_version: pipelineVersion,
          llm_provider: provider || null,
          llm_model: model.trim() || null,
        });
        setRunId(run.run_id);
        summary = `Run ${run.run_id.slice(0, 8)} açıldı.`;
      } else if (runId === null) {
        return;
      } else if (key === "extract") {
        const result = await extractCandidates(runId);
        summary = `${result.created_candidate_node_ids.length} düğüm adayı, ${result.created_candidate_relation_ids.length} ilişki adayı.`;
      } else if (key === "validate" || key === "resolve") {
        const result = key === "validate" ? await validateRun(runId) : await resolveDuplicates(runId);
        summary = `Düğüm: ${result.node_validated} doğrulandı, ${result.node_review} incelemede, ${result.node_rejected} reddedildi. İlişki: ${result.relation_validated} doğrulandı, ${result.relation_review} incelemede, ${result.relation_rejected} reddedildi.`;
      } else {
        const delta = await commitRun(runId);
        summary = `${delta.nodes_created} yeni düğüm, ${delta.nodes_merged} birleşen düğüm, ${delta.relations_created} yeni ilişki, ${delta.relations_merged} birleşen ilişki.`;
      }
      setSteps((current) => ({ ...current, [key]: { state: "done", summary } }));
    } catch (reason: unknown) {
      const { advice, detail } = explainError(reason);
      setSteps((current) => ({
        ...current,
        [key]: { state: "error", summary: detail ? `${advice} (${detail})` : advice },
      }));
    }
  }

  return (
    <>
      <div className="row-between">
        <h3>{sourceUnit.title}</h3>
        <span className={`tag ${UNIT_STATUS[sourceUnit.status].tone}`}>
          {UNIT_STATUS[sourceUnit.status].text}
        </span>
      </div>

      {steps.run.state !== "done" ? (
        <div className="field-grid">
          <label className="field">
            <span>Şema sürümü</span>
            <select value={schemaId} onChange={(event) => setSchemaId(event.currentTarget.value)}>
              {schemas.length === 0 ? <option value="">Şema yok</option> : null}
              {schemas.map((schema) => (
                <option key={schema.schema_version_id} value={schema.schema_version_id}>
                  Sürüm {schema.version_no}
                  {schema.status === "active" ? " (etkin)" : ""}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Pipeline sürümü</span>
            <input type="text" value={pipelineVersion} onChange={(event) => setPipelineVersion(event.currentTarget.value)} />
          </label>
          <label className="field">
            <span>Sağlayıcı</span>
            <select value={provider} onChange={(event) => setProvider(event.currentTarget.value)}>
              {PROVIDERS.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Model (boşsa sunucu varsayılanı)</span>
            <input type="text" value={model} onChange={(event) => setModel(event.currentTarget.value)} />
          </label>
        </div>
      ) : null}

      <ol className="run-steps">
        {STEP_ORDER.map((key, index) => {
          const step = steps[key];
          const previous = index === 0 ? null : steps[STEP_ORDER[index - 1]];
          const canRun =
            (step.state === "idle" || step.state === "error") &&
            (previous === null || previous.state === "done") &&
            (key !== "run" || schemaId !== "");
          return (
            <li key={key} className={`run-step is-${step.state}`}>
              <span className="step-badge num" aria-hidden="true">
                {index + 1}
              </span>
              <div>
                <strong>{STEP_TEXT[key].label}</strong>
                <p className={`small ${step.state === "error" ? "status-attention" : "muted"}`}>
                  {step.summary ?? STEP_TEXT[key].hint}
                </p>
              </div>
              {step.state === "done" ? (
                <span className="tag tag-done">tamam</span>
              ) : (
                <Button
                  size="sm"
                  busy={step.state === "running"}
                  disabled={!canRun}
                  onClick={() => void runStep(key)}
                >
                  {step.state === "error" ? "Tekrar dene" : "Çalıştır"}
                </Button>
              )}
            </li>
          );
        })}
      </ol>
    </>
  );
}
