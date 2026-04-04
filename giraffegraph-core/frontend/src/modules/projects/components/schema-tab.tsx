"use client";

import { useEffect, useState } from "react";

import {
  activateSchemaVersion,
  addNodeType,
  addRelationType,
  createSchemaVersion,
  listSchemaVersions,
} from "@/modules/projects/api";
import type { ProjectRecord, SchemaVersionRecord } from "@/modules/projects/types";

function toErr(e: unknown): string {
  return e instanceof Error ? e.message : "Bilinmeyen hata.";
}

// ── Schema Tab ────────────────────────────────────────────────────────────────

export function SchemaTab({ project }: { project: ProjectRecord }) {
  const [schemas, setSchemas] = useState<SchemaVersionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    void listSchemaVersions(project.project_id)
      .then((items) => {
        if (cancelled) return;
        setSchemas(items);
        setSelectedId((cur) => cur ?? items.find((s) => s.status === "active")?.schema_version_id ?? items[0]?.schema_version_id ?? null);
      })
      .catch((e: unknown) => { if (!cancelled) setError(toErr(e)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [project.project_id, reloadToken]);

  const reload = () => setReloadToken((t) => t + 1);
  const selected = schemas.find((s) => s.schema_version_id === selectedId) ?? null;

  return (
    <div className="content-grid schema-grid">
      {/* Sol: şema listesi + yeni şema */}
      <div className="panel review-list-panel">
        <div className="panel-header">
          <div>
            <p className="panel-eyebrow">Şema Versiyonları</p>
            <h3>{project.name}</h3>
          </div>
          <button className="ghost-button" type="button" onClick={reload}>Yenile</button>
        </div>

        {loading ? (
          <div className="panel-empty">Yükleniyor…</div>
        ) : error ? (
          <div className="panel-empty error-state">{error}</div>
        ) : (
          <div className="schema-list">
            {schemas.length === 0 && (
              <div className="panel-empty">Henüz şema yok. Aşağıdan oluşturun.</div>
            )}
            {schemas.map((s) => (
              <button
                key={s.schema_version_id}
                type="button"
                className={`schema-card${s.schema_version_id === selectedId ? " is-selected" : ""}`}
                onClick={() => setSelectedId(s.schema_version_id)}
              >
                <div className="schema-card-top">
                  <strong>v{s.version_no}</strong>
                  <span className={`tone-chip tone-${s.status === "active" ? "success" : s.status === "archived" ? "neutral" : "warning"}`}>
                    {s.status === "active" ? "aktif" : s.status === "archived" ? "arşiv" : "taslak"}
                  </span>
                </div>
                <p>
                  {s.node_types.length} düğüm tipi · {s.relation_types.length} ilişki tipi
                </p>
                {s.notes && <p>{s.notes}</p>}
              </button>
            ))}
          </div>
        )}

        <CreateSchemaForm projectId={project.project_id} nextVersionNo={(schemas[schemas.length - 1]?.version_no ?? 0) + 1} onCreated={(s) => { setSchemas((prev) => [...prev, s]); setSelectedId(s.schema_version_id); }} />
      </div>

      {/* Sağ: seçili şema detayı */}
      <div className="panel review-detail-panel">
        {!selected ? (
          <div className="panel-empty">Soldan bir şema seçin.</div>
        ) : (
          <SchemaDetail schema={selected} onUpdated={(updated) => { setSchemas((prev) => prev.map((s) => s.schema_version_id === updated.schema_version_id ? updated : s)); }} />
        )}
      </div>
    </div>
  );
}

// ── Create Schema Form ────────────────────────────────────────────────────────

function CreateSchemaForm({
  projectId,
  nextVersionNo,
  onCreated,
}: {
  projectId: string;
  nextVersionNo: number;
  onCreated: (s: SchemaVersionRecord) => void;
}) {
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      const schema = await createSchemaVersion(projectId, { version_no: nextVersionNo, notes: notes.trim() || null });
      onCreated(schema);
      setNotes("");
      setOpen(false);
    } catch (error: unknown) { setErr(toErr(error)); }
    finally { setBusy(false); }
  }

  if (!open) {
    return (
      <div style={{ marginTop: 14 }}>
        <button className="ghost-button" type="button" style={{ width: "100%" }} onClick={() => setOpen(true)}>
          + Yeni Şema v{nextVersionNo}
        </button>
      </div>
    );
  }

  return (
    <form className="decision-form" style={{ marginTop: 14 }} onSubmit={submit}>
      <div className="panel-header" style={{ marginBottom: 8 }}>
        <strong>Yeni Şema v{nextVersionNo}</strong>
        <button className="ghost-button" type="button" onClick={() => setOpen(false)}>İptal</button>
      </div>
      <label className="field">
        <span>Not (opsiyonel)</span>
        <input type="text" value={notes} onChange={(e) => setNotes(e.currentTarget.value)} placeholder="İlk şema, story domain…" />
      </label>
      {err && <div className="form-feedback error-state">{err}</div>}
      <button className="primary-button" type="submit" disabled={busy}>
        {busy ? "Oluşturuluyor…" : "Oluştur"}
      </button>
    </form>
  );
}

// ── Schema Detail ─────────────────────────────────────────────────────────────

function SchemaDetail({
  schema,
  onUpdated,
}: {
  schema: SchemaVersionRecord;
  onUpdated: (s: SchemaVersionRecord) => void;
}) {
  const [activating, setActivating] = useState(false);
  const [activateErr, setActivateErr] = useState<string | null>(null);

  async function activate() {
    setActivating(true);
    setActivateErr(null);
    try {
      const updated = await activateSchemaVersion(schema.project_id, schema.schema_version_id);
      onUpdated(updated);
    } catch (e: unknown) { setActivateErr(toErr(e)); }
    finally { setActivating(false); }
  }

  return (
    <div className="detail-stack">
      {/* Header */}
      <div className="detail-block">
        <div className="detail-title-row">
          <h4>Şema v{schema.version_no}</h4>
          <span className={`tone-chip tone-${schema.status === "active" ? "success" : "warning"}`}>
            {schema.status === "active" ? "aktif" : schema.status === "archived" ? "arşiv" : "taslak"}
          </span>
        </div>
        {schema.notes && <p className="detail-copy">{schema.notes}</p>}
        {schema.status !== "active" && (
          <div style={{ marginTop: 12 }}>
            <button className="primary-button" type="button" disabled={activating} onClick={activate}>
              {activating ? "Aktive ediliyor…" : "Bu şemayı aktive et"}
            </button>
            {activateErr && <div className="form-feedback error-state" style={{ marginTop: 8 }}>{activateErr}</div>}
          </div>
        )}
      </div>

      {/* Mevcut tipler */}
      <div className="detail-block">
        <div className="panel-header" style={{ marginBottom: 12 }}>
          <h4>Düğüm tipleri ({schema.node_types.length})</h4>
        </div>
        {schema.node_types.length === 0 ? (
          <div className="mini-empty">Henüz düğüm tipi yok.</div>
        ) : (
          <div className="type-chip-row">
            {schema.node_types.map((n) => (
              <span key={n.node_type_id} className="type-chip node-chip" title={`merge_keys: ${n.merge_keys.join(", ")}`}>
                {n.name}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="detail-block">
        <div className="panel-header" style={{ marginBottom: 12 }}>
          <h4>İlişki tipleri ({schema.relation_types.length})</h4>
        </div>
        {schema.relation_types.length === 0 ? (
          <div className="mini-empty">Henüz ilişki tipi yok.</div>
        ) : (
          <div className="type-chip-row">
            {schema.relation_types.map((r) => (
              <span key={r.relation_type_id} className="type-chip relation-chip" title={`${r.from_type} → ${r.to_type}`}>
                {r.name}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Formlar */}
      <AddNodeTypeForm schemaVersionId={schema.schema_version_id} onAdded={onUpdated} />
      <AddRelationTypeForm schemaVersionId={schema.schema_version_id} nodeTypes={schema.node_types.map((n) => n.name)} onAdded={onUpdated} />
    </div>
  );
}

// ── Add Node Type Form ────────────────────────────────────────────────────────

function AddNodeTypeForm({
  schemaVersionId,
  onAdded,
}: {
  schemaVersionId: string;
  onAdded: (s: SchemaVersionRecord) => void;
}) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [mergeKeys, setMergeKeys] = useState("");
  const [hints, setHints] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      const updated = await addNodeType(schemaVersionId, {
        name: name.trim(),
        display_name: displayName.trim() || name.trim(),
        description: description.trim() || name.trim(),
        merge_keys: mergeKeys.split(",").map((k) => k.trim()).filter(Boolean),
        extraction_hints: hints.split(",").map((h) => h.trim()).filter(Boolean),
      });
      onAdded(updated);
      setName(""); setDisplayName(""); setDescription(""); setMergeKeys(""); setHints("");
      setOpen(false);
    } catch (error: unknown) { setErr(toErr(error)); }
    finally { setBusy(false); }
  }

  if (!open) {
    return (
      <button className="ghost-button" type="button" style={{ width: "100%" }} onClick={() => setOpen(true)}>
        + Düğüm tipi ekle
      </button>
    );
  }

  return (
    <form className="detail-block decision-form" onSubmit={submit}>
      <div className="panel-header" style={{ marginBottom: 4 }}>
        <h4>Düğüm tipi ekle</h4>
        <button className="ghost-button" type="button" onClick={() => setOpen(false)}>İptal</button>
      </div>
      <div className="field-grid">
        <label className="field">
          <span>Ad *</span>
          <input required type="text" value={name} onChange={(e) => setName(e.currentTarget.value)} placeholder="Character" />
        </label>
        <label className="field">
          <span>Görünen ad</span>
          <input type="text" value={displayName} onChange={(e) => setDisplayName(e.currentTarget.value)} placeholder="Karakter" />
        </label>
      </div>
      <label className="field">
        <span>Açıklama</span>
        <input type="text" value={description} onChange={(e) => setDescription(e.currentTarget.value)} placeholder="Hikayede yer alan kişi" />
      </label>
      <label className="field">
        <span>Birleştirme anahtarları (virgülle)</span>
        <input type="text" value={mergeKeys} onChange={(e) => setMergeKeys(e.currentTarget.value)} placeholder="name" />
      </label>
      <label className="field">
        <span>Çıkarım ipuçları (virgülle, opsiyonel)</span>
        <input type="text" value={hints} onChange={(e) => setHints(e.currentTarget.value)} placeholder="karakter, kişi, şahıs" />
      </label>
      {err && <div className="form-feedback error-state">{err}</div>}
      <button className="primary-button" type="submit" disabled={busy || !name.trim()}>
        {busy ? "Ekleniyor…" : "Ekle"}
      </button>
    </form>
  );
}

// ── Add Relation Type Form ────────────────────────────────────────────────────

function AddRelationTypeForm({
  schemaVersionId,
  nodeTypes,
  onAdded,
}: {
  schemaVersionId: string;
  nodeTypes: string[];
  onAdded: (s: SchemaVersionRecord) => void;
}) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [fromType, setFromType] = useState(nodeTypes[0] ?? "");
  const [toType, setToType] = useState(nodeTypes[0] ?? "");
  const [description, setDescription] = useState("");
  const [hints, setHints] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      const updated = await addRelationType(schemaVersionId, {
        name: name.trim(),
        from_type: fromType,
        to_type: toType,
        description: description.trim() || name.trim(),
        extraction_hints: hints.split(",").map((h) => h.trim()).filter(Boolean),
      });
      onAdded(updated);
      setName(""); setDescription(""); setHints("");
      setOpen(false);
    } catch (error: unknown) { setErr(toErr(error)); }
    finally { setBusy(false); }
  }

  if (nodeTypes.length === 0) {
    return <div className="mini-empty">İlişki tipi eklemek için önce düğüm tipi oluşturun.</div>;
  }

  if (!open) {
    return (
      <button className="ghost-button" type="button" style={{ width: "100%" }} onClick={() => setOpen(true)}>
        + İlişki tipi ekle
      </button>
    );
  }

  return (
    <form className="detail-block decision-form" onSubmit={submit}>
      <div className="panel-header" style={{ marginBottom: 4 }}>
        <h4>İlişki tipi ekle</h4>
        <button className="ghost-button" type="button" onClick={() => setOpen(false)}>İptal</button>
      </div>
      <label className="field">
        <span>İlişki adı *</span>
        <input required type="text" value={name} onChange={(e) => setName(e.currentTarget.value)} placeholder="KNOWS" />
      </label>
      <div className="field-grid">
        <label className="field">
          <span>Kaynak tipi</span>
          <select value={fromType} onChange={(e) => setFromType(e.currentTarget.value)}>
            {nodeTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <label className="field">
          <span>Hedef tipi</span>
          <select value={toType} onChange={(e) => setToType(e.currentTarget.value)}>
            {nodeTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
      </div>
      <label className="field">
        <span>Açıklama</span>
        <input type="text" value={description} onChange={(e) => setDescription(e.currentTarget.value)} placeholder="İki karakter arasındaki tanışıklık" />
      </label>
      <label className="field">
        <span>Çıkarım ipuçları (virgülle, opsiyonel)</span>
        <input type="text" value={hints} onChange={(e) => setHints(e.currentTarget.value)} placeholder="tanıyor, biliyor, arkadaş" />
      </label>
      {err && <div className="form-feedback error-state">{err}</div>}
      <button className="primary-button" type="submit" disabled={busy || !name.trim()}>
        {busy ? "Ekleniyor…" : "Ekle"}
      </button>
    </form>
  );
}
