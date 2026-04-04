"use client";

import { useEffect, useState } from "react";

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
  ExtractionResultRecord,
  GraphDeltaRecord,
  ProcessingRunRecord,
  ProjectRecord,
  RunValidationRecord,
  SchemaVersionRecord,
  SegmentRecord,
  SourceUnitSummaryRecord,
} from "@/modules/projects/types";

function toErr(e: unknown): string {
  return e instanceof Error ? e.message : "Bilinmeyen hata.";
}

function fmtDate(v: string | null | undefined) {
  if (!v) return "—";
  return new Intl.DateTimeFormat("tr-TR", { dateStyle: "medium", timeStyle: "short" }).format(new Date(v));
}

// ── Pipeline Tab ──────────────────────────────────────────────────────────────

export function PipelineTab({ project }: { project: ProjectRecord }) {
  const [sourceUnits, setSourceUnits] = useState<SourceUnitSummaryRecord[]>([]);
  const [schemas, setSchemas] = useState<SchemaVersionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSourceUnitId, setSelectedSourceUnitId] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    void Promise.all([
      listSourceUnits(project.project_id),
      listSchemaVersions(project.project_id),
    ])
      .then(([units, schemaList]) => {
        if (cancelled) return;
        setSourceUnits(units);
        setSchemas(schemaList);
        setSelectedSourceUnitId((cur) => cur ?? units[0]?.source_unit_id ?? null);
      })
      .catch((e: unknown) => { if (!cancelled) setError(toErr(e)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [project.project_id, reloadToken]);

  const reload = () => setReloadToken((t) => t + 1);
  const activeSchema = schemas.find((s) => s.status === "active") ?? schemas[0] ?? null;
  const selected = sourceUnits.find((u) => u.source_unit_id === selectedSourceUnitId) ?? null;

  return (
    <div className="content-grid ingest-grid">
      {/* Sol: kaynak birimi listesi + yeni kaynak */}
      <div className="panel review-list-panel">
        <div className="panel-header">
          <div>
            <p className="panel-eyebrow">Kaynak Birimleri</p>
            <h3>{project.name}</h3>
          </div>
          <button className="ghost-button" type="button" onClick={reload}>Yenile</button>
        </div>

        {loading ? (
          <div className="panel-empty">Yükleniyor…</div>
        ) : error ? (
          <div className="panel-empty error-state">{error}</div>
        ) : (
          <div className="source-unit-list">
            {sourceUnits.length === 0 && (
              <div className="panel-empty">Henüz kaynak birimi yok. Aşağıdan ekleyin.</div>
            )}
            {sourceUnits.map((u) => (
              <button
                key={u.source_unit_id}
                type="button"
                className={`source-unit-card${u.source_unit_id === selectedSourceUnitId ? " is-selected" : ""}`}
                onClick={() => setSelectedSourceUnitId(u.source_unit_id)}
              >
                <div className="source-unit-card-top">
                  <strong>{u.title}</strong>
                  <span className={`tone-chip tone-${
                    u.status === "processed" ? "success" :
                    u.status === "processing" ? "warning" :
                    u.status === "failed" ? "danger" : "neutral"
                  }`}>
                    {u.status === "processed" ? "tamamlandı" :
                     u.status === "processing" ? "işleniyor" :
                     u.status === "failed" ? "hata" :
                     u.status === "ready" ? "hazır" : "taslak"}
                  </span>
                </div>
                <p>{u.source_type} · {fmtDate(u.created_at)}</p>
              </button>
            ))}
          </div>
        )}

        {!loading && (
          <CreateSourceUnitForm
            projectId={project.project_id}
            activeSchema={activeSchema}
            onCreated={(unit) => {
              setSourceUnits((prev) => [unit, ...prev]);
              setSelectedSourceUnitId(unit.source_unit_id);
            }}
          />
        )}
      </div>

      {/* Sağ: pipeline runner */}
      <div className="panel review-detail-panel">
        {!selected ? (
          <div className="panel-empty">Soldan bir kaynak birimi seçin.</div>
        ) : (
          <PipelineRunner
            sourceUnit={selected}
            schemas={schemas}
            activeSchema={activeSchema}
          />
        )}
      </div>
    </div>
  );
}

// ── Create Source Unit Form ───────────────────────────────────────────────────

function CreateSourceUnitForm({
  projectId,
  activeSchema,
  onCreated,
}: {
  projectId: string;
  activeSchema: SchemaVersionRecord | null;
  onCreated: (u: SourceUnitSummaryRecord) => void;
}) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [sourceType, setSourceType] = useState("episode");
  const [content, setContent] = useState("");
  const [seqNo, setSeqNo] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!activeSchema) { setErr("Önce aktif bir şema oluşturun."); return; }
    setBusy(true);
    setErr(null);
    try {
      const unit = await createSourceUnit(projectId, {
        schema_version_id: activeSchema.schema_version_id,
        source_type: sourceType.trim(),
        title: title.trim(),
        raw_content: content,
        sequence_no: seqNo ? Number(seqNo) : null,
      });
      onCreated(unit as unknown as SourceUnitSummaryRecord);
      setTitle(""); setContent(""); setSeqNo("");
      setOpen(false);
    } catch (error: unknown) { setErr(toErr(error)); }
    finally { setBusy(false); }
  }

  if (!open) {
    return (
      <div style={{ marginTop: 14 }}>
        <button className="ghost-button" type="button" style={{ width: "100%" }} onClick={() => setOpen(true)}>
          + Yeni kaynak ekle
        </button>
      </div>
    );
  }

  return (
    <form className="decision-form" style={{ marginTop: 14 }} onSubmit={submit}>
      <div className="panel-header" style={{ marginBottom: 8 }}>
        <strong>Yeni kaynak birimi</strong>
        <button className="ghost-button" type="button" onClick={() => setOpen(false)}>İptal</button>
      </div>
      {activeSchema ? (
        <div className="mini-empty" style={{ fontSize: "0.8rem" }}>Şema: v{activeSchema.version_no}</div>
      ) : (
        <div className="form-feedback error-state">Aktif şema bulunamadı. Önce Şema sekmesinden şema oluşturun.</div>
      )}
      <div className="field-grid">
        <label className="field">
          <span>Başlık *</span>
          <input required type="text" value={title} onChange={(e) => setTitle(e.currentTarget.value)} placeholder="S01E01" />
        </label>
        <label className="field">
          <span>Kaynak tipi</span>
          <input type="text" value={sourceType} onChange={(e) => setSourceType(e.currentTarget.value)} placeholder="episode" />
        </label>
      </div>
      <label className="field">
        <span>Sıra no (opsiyonel)</span>
        <input type="number" min={1} value={seqNo} onChange={(e) => setSeqNo(e.currentTarget.value)} placeholder="1" />
      </label>
      <label className="field">
        <span>Ham metin *</span>
        <textarea required className="code-area" rows={8} value={content} onChange={(e) => setContent(e.currentTarget.value)} placeholder="Transkript, senaryo, notlar…" />
      </label>
      {err && <div className="form-feedback error-state">{err}</div>}
      <button className="primary-button" type="submit" disabled={busy || !title.trim() || !content.trim() || !activeSchema}>
        {busy ? "Kaydediliyor…" : "Kaydet"}
      </button>
    </form>
  );
}

// ── Pipeline Runner ───────────────────────────────────────────────────────────

type StepStatus = "idle" | "running" | "done" | "error";

interface PipelineState {
  segments: { status: StepStatus; count: number; error: string | null };
  run: { status: StepStatus; record: ProcessingRunRecord | null; error: string | null };
  extract: { status: StepStatus; result: ExtractionResultRecord | null; error: string | null };
  validate: { status: StepStatus; result: RunValidationRecord | null; error: string | null };
  resolve: { status: StepStatus; result: RunValidationRecord | null; error: string | null };
  commit: { status: StepStatus; result: GraphDeltaRecord | null; error: string | null };
}

const initialPipeline = (): PipelineState => ({
  segments: { status: "idle", count: 0, error: null },
  run: { status: "idle", record: null, error: null },
  extract: { status: "idle", result: null, error: null },
  validate: { status: "idle", result: null, error: null },
  resolve: { status: "idle", result: null, error: null },
  commit: { status: "idle", result: null, error: null },
});

function PipelineRunner({
  sourceUnit,
  schemas,
  activeSchema,
}: {
  sourceUnit: SourceUnitSummaryRecord;
  schemas: SchemaVersionRecord[];
  activeSchema: SchemaVersionRecord | null;
}) {
  const [pipeline, setPipeline] = useState<PipelineState>(initialPipeline);
  const [selectedSchemaId, setSelectedSchemaId] = useState(activeSchema?.schema_version_id ?? "");
  const [pipelineVersion, setPipelineVersion] = useState("v1");
  const [llmProvider, setLlmProvider] = useState("openai");
  const [llmModel, setLlmModel] = useState("gpt-4o");

  // Reset when source unit changes
  useEffect(() => {
    setPipeline(initialPipeline());
  }, [sourceUnit.source_unit_id]);

  useEffect(() => {
    if (activeSchema) setSelectedSchemaId(activeSchema.schema_version_id);
  }, [activeSchema]);

  const runId = pipeline.run.record?.run_id ?? null;

  // Step 1: Segment oluştur
  async function doSegments() {
    setPipeline((p) => ({ ...p, segments: { status: "running", count: 0, error: null } }));
    try {
      const segs: SegmentRecord[] = await generateSegments(sourceUnit.source_unit_id);
      setPipeline((p) => ({ ...p, segments: { status: "done", count: segs.length, error: null } }));
    } catch (e: unknown) {
      setPipeline((p) => ({ ...p, segments: { status: "error", count: 0, error: toErr(e) } }));
    }
  }

  // Step 2: Çalıştırma başlat
  async function doRun() {
    if (!selectedSchemaId) return;
    setPipeline((p) => ({ ...p, run: { status: "running", record: null, error: null } }));
    try {
      const record = await startProcessingRun(sourceUnit.source_unit_id, {
        schema_version_id: selectedSchemaId,
        pipeline_version: pipelineVersion,
        llm_provider: llmProvider || null,
        llm_model: llmModel || null,
      });
      setPipeline((p) => ({ ...p, run: { status: "done", record, error: null } }));
    } catch (e: unknown) {
      setPipeline((p) => ({ ...p, run: { status: "error", record: null, error: toErr(e) } }));
    }
  }

  // Step 3: LLM çıkarımı
  async function doExtract() {
    if (!runId) return;
    setPipeline((p) => ({ ...p, extract: { status: "running", result: null, error: null } }));
    try {
      const result = await extractCandidates(runId);
      setPipeline((p) => ({ ...p, extract: { status: "done", result, error: null } }));
    } catch (e: unknown) {
      setPipeline((p) => ({ ...p, extract: { status: "error", result: null, error: toErr(e) } }));
    }
  }

  // Step 4: Doğrulama
  async function doValidate() {
    if (!runId) return;
    setPipeline((p) => ({ ...p, validate: { status: "running", result: null, error: null } }));
    try {
      const result = await validateRun(runId);
      setPipeline((p) => ({ ...p, validate: { status: "done", result, error: null } }));
    } catch (e: unknown) {
      setPipeline((p) => ({ ...p, validate: { status: "error", result: null, error: toErr(e) } }));
    }
  }

  // Step 5: Tekrar tespit
  async function doResolve() {
    if (!runId) return;
    setPipeline((p) => ({ ...p, resolve: { status: "running", result: null, error: null } }));
    try {
      const result = await resolveDuplicates(runId);
      setPipeline((p) => ({ ...p, resolve: { status: "done", result, error: null } }));
    } catch (e: unknown) {
      setPipeline((p) => ({ ...p, resolve: { status: "error", result: null, error: toErr(e) } }));
    }
  }

  // Step 6: Grafiğe yaz
  async function doCommit() {
    if (!runId) return;
    setPipeline((p) => ({ ...p, commit: { status: "running", result: null, error: null } }));
    try {
      const result = await commitRun(runId);
      setPipeline((p) => ({ ...p, commit: { status: "done", result, error: null } }));
    } catch (e: unknown) {
      setPipeline((p) => ({ ...p, commit: { status: "error", result: null, error: toErr(e) } }));
    }
  }

  return (
    <div className="detail-stack">
      {/* Kaynak bilgisi */}
      <div className="detail-block">
        <div className="detail-title-row">
          <h4>{sourceUnit.title}</h4>
          <span className={`tone-chip tone-${sourceUnit.status === "processed" ? "success" : sourceUnit.status === "failed" ? "danger" : "neutral"}`}>
            {sourceUnit.status}
          </span>
        </div>
        <div className="definition-grid" style={{ marginTop: 10 }}>
          <div><span>Kaynak tipi</span><strong>{sourceUnit.source_type}</strong></div>
          <div><span>Oluşturulma</span><strong>{fmtDate(sourceUnit.created_at)}</strong></div>
        </div>
      </div>

      {/* Çalıştırma ayarları (run başlatılmamışsa göster) */}
      {pipeline.run.status === "idle" && (
        <div className="detail-block decision-form">
          <h4>Çalıştırma ayarları</h4>
          <div className="field-grid">
            <label className="field">
              <span>Şema versiyonu</span>
              <select value={selectedSchemaId} onChange={(e) => setSelectedSchemaId(e.currentTarget.value)}>
                {schemas.length === 0 && <option value="">Şema yok</option>}
                {schemas.map((s) => (
                  <option key={s.schema_version_id} value={s.schema_version_id}>
                    v{s.version_no} {s.status === "active" ? "✓" : ""}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Pipeline versiyonu</span>
              <input type="text" value={pipelineVersion} onChange={(e) => setPipelineVersion(e.currentTarget.value)} placeholder="v1" />
            </label>
            <label className="field">
              <span>LLM sağlayıcı</span>
              <select value={llmProvider} onChange={(e) => setLlmProvider(e.currentTarget.value)}>
                <option value="openai">OpenAI</option>
                <option value="noop">Noop (test)</option>
              </select>
            </label>
            <label className="field">
              <span>Model</span>
              <input type="text" value={llmModel} onChange={(e) => setLlmModel(e.currentTarget.value)} placeholder="gpt-4o" />
            </label>
          </div>
        </div>
      )}

      {/* Pipeline adımları */}
      <div className="detail-block">
        <h4 style={{ marginBottom: 14 }}>Pipeline adımları</h4>
        <div className="step-runner">
          <StepItem
            num={1}
            label="Segment oluştur"
            desc={pipeline.segments.status === "done" ? `${pipeline.segments.count} segment oluşturuldu` : "Metni işlenebilir parçalara böl"}
            status={pipeline.segments.status}
            error={pipeline.segments.error}
            canRun={pipeline.segments.status === "idle" || pipeline.segments.status === "error"}
            onRun={doSegments}
          />
          <StepItem
            num={2}
            label="Çalıştırma başlat"
            desc={pipeline.run.record ? `Run #${pipeline.run.record.run_id.slice(0, 8)}` : "Şema + pipeline tanımıyla çalıştırma oluştur"}
            status={pipeline.run.status}
            error={pipeline.run.error}
            canRun={pipeline.segments.status === "done" && (pipeline.run.status === "idle" || pipeline.run.status === "error")}
            onRun={doRun}
          />
          <StepItem
            num={3}
            label="LLM çıkarımı"
            desc={pipeline.extract.result
              ? `${pipeline.extract.result.created_candidate_node_ids.length} düğüm · ${pipeline.extract.result.created_candidate_relation_ids.length} ilişki adayı`
              : "LLM metni okuyup varlık ve ilişki adayları üretir"}
            status={pipeline.extract.status}
            error={pipeline.extract.error}
            canRun={pipeline.run.status === "done" && (pipeline.extract.status === "idle" || pipeline.extract.status === "error")}
            onRun={doExtract}
          />
          <StepItem
            num={4}
            label="Şema doğrulama"
            desc={pipeline.validate.result
              ? `${pipeline.validate.result.node_validated} düğüm onaylı · ${pipeline.validate.result.node_review} inceleme bekliyor`
              : "Adayları şema kurallarına göre doğrula"}
            status={pipeline.validate.status}
            error={pipeline.validate.error}
            canRun={pipeline.extract.status === "done" && (pipeline.validate.status === "idle" || pipeline.validate.status === "error")}
            onRun={doValidate}
          />
          <StepItem
            num={5}
            label="Tekrar tespit"
            desc={pipeline.resolve.result
              ? `Tamamlandı`
              : "Duplicate adayları birleştir"}
            status={pipeline.resolve.status}
            error={pipeline.resolve.error}
            canRun={pipeline.validate.status === "done" && (pipeline.resolve.status === "idle" || pipeline.resolve.status === "error")}
            onRun={doResolve}
          />
          <StepItem
            num={6}
            label="Grafiğe yaz"
            desc={pipeline.commit.result
              ? `+${pipeline.commit.result.nodes_created} düğüm · +${pipeline.commit.result.relations_created} ilişki · ${pipeline.commit.result.review_count} inceleme kuyruğuna düştü`
              : "Doğrulanan adayları Neo4j'ye yaz"}
            status={pipeline.commit.status}
            error={pipeline.commit.error}
            canRun={pipeline.resolve.status === "done" && (pipeline.commit.status === "idle" || pipeline.commit.status === "error")}
            onRun={doCommit}
          />
        </div>
      </div>

      {/* Commit sonucu */}
      {pipeline.commit.status === "done" && pipeline.commit.result && (
        <div className="detail-block">
          <h4>Grafik güncellendi ✓</h4>
          <div className="definition-grid" style={{ marginTop: 10 }}>
            <div><span>Yeni düğüm</span><strong>{pipeline.commit.result.nodes_created}</strong></div>
            <div><span>Birleştirilen düğüm</span><strong>{pipeline.commit.result.nodes_merged}</strong></div>
            <div><span>Yeni ilişki</span><strong>{pipeline.commit.result.relations_created}</strong></div>
            <div><span>Birleştirilen ilişki</span><strong>{pipeline.commit.result.relations_merged}</strong></div>
            <div><span>İnceleme kuyruğu</span><strong>{pipeline.commit.result.review_count}</strong></div>
            <div><span>Reddedilen</span><strong>{pipeline.commit.result.rejected_count}</strong></div>
          </div>
          <div className="form-feedback success-state" style={{ marginTop: 12 }}>
            İşlem tamamlandı. Grafik Gezgini sekmesinden sonucu görebilirsin.
          </div>
        </div>
      )}
    </div>
  );
}

// ── Step Item ─────────────────────────────────────────────────────────────────

function StepItem({
  num,
  label,
  desc,
  status,
  error,
  canRun,
  onRun,
}: {
  num: number;
  label: string;
  desc: string;
  status: StepStatus;
  error: string | null;
  canRun: boolean;
  onRun: () => void;
}) {
  const cls = `step-item${status === "done" ? " is-done" : status === "running" ? " is-running" : status === "error" ? " is-error" : ""}`;

  return (
    <div className={cls}>
      <div className="step-num">{num}</div>
      <div className="step-body">
        <strong>{label}</strong>
        <p>{error ?? desc}</p>
      </div>
      <div className="step-action">
        {status === "done" ? (
          <span className="tone-chip tone-success">✓</span>
        ) : status === "running" ? (
          <span className="tone-chip tone-warning">…</span>
        ) : (
          <button
            className="ghost-button"
            type="button"
            disabled={!canRun}
            onClick={onRun}
          >
            {status === "error" ? "Tekrar dene" : "Çalıştır"}
          </button>
        )}
      </div>
    </div>
  );
}
