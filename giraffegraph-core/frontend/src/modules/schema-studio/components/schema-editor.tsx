"use client";

import { useEffect, useState, type FormEvent } from "react";

import {
  activateSchemaVersion,
  addNodeType,
  addRelationType,
  createSchemaVersion,
  listSchemaVersions,
} from "@/modules/projects/api";
import type { ProjectRecord, SchemaVersionRecord } from "@/modules/projects/types";
import { Button } from "@/shared/ui/button";
import { ErrorNote, LoadingBlock } from "@/shared/ui/states";

const STATUS_WORD: Record<SchemaVersionRecord["status"], { text: string; tone: string }> = {
  active: { text: "etkin", tone: "tag-done" },
  draft: { text: "taslak", tone: "tag-attention" },
  archived: { text: "arşiv", tone: "" },
};

function splitList(value: string): string[] {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

export function SchemaEditor({ project }: { project: ProjectRecord }) {
  const [schemas, setSchemas] = useState<SchemaVersionRecord[] | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    void listSchemaVersions(project.project_id)
      .then((items) => {
        if (cancelled) {
          return;
        }
        setSchemas(items);
        setSelectedId(
          (current) =>
            current ??
            items.find((schema) => schema.status === "active")?.schema_version_id ??
            items[0]?.schema_version_id ??
            null,
        );
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

  const selected = schemas?.find((schema) => schema.schema_version_id === selectedId) ?? null;
  const nextVersionNo = (schemas?.[schemas.length - 1]?.version_no ?? 0) + 1;

  function replaceSchema(updated: SchemaVersionRecord) {
    setSchemas(
      (current) =>
        current?.map((schema) =>
          schema.schema_version_id === updated.schema_version_id ? updated : schema,
        ) ?? null,
    );
  }

  return (
    <div className="adv-layout">
      <div className="card stack">
        <div className="row-between">
          <h3>Şema sürümleri</h3>
          <Button size="sm" variant="quiet" onClick={() => setReloadToken((token) => token + 1)}>
            Yenile
          </Button>
        </div>
        {error ? (
          <ErrorNote title="Şema sürümleri okunamadı." error={error} />
        ) : schemas === null ? (
          <LoadingBlock label="Şema sürümleri yükleniyor" />
        ) : schemas.length === 0 ? (
          <p className="muted small">
            Bu projede şema yok. Aşağıdan ilk sürümü oluşturup tür ekleyebilirsin.
          </p>
        ) : (
          <ul className="list-rows">
            {schemas.map((schema) => (
              <li key={schema.schema_version_id}>
                <button
                  type="button"
                  className={`list-row${schema.schema_version_id === selectedId ? " is-selected" : ""}`}
                  onClick={() => setSelectedId(schema.schema_version_id)}
                >
                  <span className="row-between">
                    <strong>Sürüm {schema.version_no}</strong>
                    <span className={`tag ${STATUS_WORD[schema.status].tone}`}>
                      {STATUS_WORD[schema.status].text}
                    </span>
                  </span>
                  <span className="muted small">
                    {schema.node_types.length} düğüm türü · {schema.relation_types.length} ilişki
                    türü
                  </span>
                  {schema.notes ? <span className="muted small">{schema.notes}</span> : null}
                </button>
              </li>
            ))}
          </ul>
        )}
        <CreateSchemaForm
          projectId={project.project_id}
          nextVersionNo={nextVersionNo}
          onCreated={(schema) => {
            setSchemas((current) => [...(current ?? []), schema]);
            setSelectedId(schema.schema_version_id);
          }}
        />
      </div>

      <div className="card stack">
        {selected ? (
          <SchemaDetail schema={selected} onUpdated={replaceSchema} />
        ) : (
          <p className="muted">Ayrıntısını görmek için soldan bir şema sürümü seç.</p>
        )}
      </div>
    </div>
  );
}

function CreateSchemaForm({
  projectId,
  nextVersionNo,
  onCreated,
}: {
  projectId: string;
  nextVersionNo: number;
  onCreated: (schema: SchemaVersionRecord) => void;
}) {
  const [open, setOpen] = useState(false);
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      onCreated(
        await createSchemaVersion(projectId, {
          version_no: nextVersionNo,
          notes: notes.trim() || null,
        }),
      );
      setNotes("");
      setOpen(false);
    } catch (reason: unknown) {
      setError(reason);
    } finally {
      setBusy(false);
    }
  }

  if (!open) {
    return (
      <Button size="sm" icon="plus" onClick={() => setOpen(true)}>
        Yeni şema sürümü ({nextVersionNo})
      </Button>
    );
  }

  return (
    <form className="card-plain stack" onSubmit={submit}>
      <h4>Yeni şema sürümü ({nextVersionNo})</h4>
      <label className="field">
        <span>Not (isteğe bağlı)</span>
        <input type="text" value={notes} onChange={(event) => setNotes(event.currentTarget.value)} />
      </label>
      {error ? <ErrorNote title="Şema sürümü oluşturulamadı." error={error} /> : null}
      <div className="row">
        <Button type="submit" variant="primary" size="sm" busy={busy}>
          Oluştur
        </Button>
        <Button variant="quiet" size="sm" onClick={() => setOpen(false)}>
          Vazgeç
        </Button>
      </div>
    </form>
  );
}

function SchemaDetail({
  schema,
  onUpdated,
}: {
  schema: SchemaVersionRecord;
  onUpdated: (schema: SchemaVersionRecord) => void;
}) {
  const [activating, setActivating] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function activate() {
    setActivating(true);
    setError(null);
    try {
      onUpdated(await activateSchemaVersion(schema.project_id, schema.schema_version_id));
    } catch (reason: unknown) {
      setError(reason);
    } finally {
      setActivating(false);
    }
  }

  return (
    <>
      <div className="row-between">
        <h3>Şema sürümü {schema.version_no}</h3>
        <span className={`tag ${STATUS_WORD[schema.status].tone}`}>
          {STATUS_WORD[schema.status].text}
        </span>
      </div>
      {schema.notes ? <p className="muted">{schema.notes}</p> : null}
      {schema.status !== "active" ? (
        <div className="stack-sm">
          <div>
            <Button variant="primary" size="sm" busy={activating} onClick={() => void activate()}>
              Bu sürümü etkinleştir
            </Button>
          </div>
          {error ? <ErrorNote title="Sürüm etkinleştirilemedi." error={error} /> : null}
        </div>
      ) : null}

      <section className="stack-sm">
        <h4>Düğüm türleri ({schema.node_types.length})</h4>
        {schema.node_types.length === 0 ? (
          <p className="muted small">Bu sürümde düğüm türü yok.</p>
        ) : (
          <ul className="row">
            {schema.node_types.map((nodeType) => (
              <li
                key={nodeType.node_type_id}
                className="tag"
                title={`Kimlik alanları: ${nodeType.merge_keys.join(", ") || "yok"}`}
              >
                {nodeType.name}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="stack-sm">
        <h4>İlişki türleri ({schema.relation_types.length})</h4>
        {schema.relation_types.length === 0 ? (
          <p className="muted small">Bu sürümde ilişki türü yok.</p>
        ) : (
          <ul className="row">
            {schema.relation_types.map((relationType) => (
              <li
                key={relationType.relation_type_id}
                className="tag"
                title={`${relationType.from_type} → ${relationType.to_type}`}
              >
                {relationType.name}
              </li>
            ))}
          </ul>
        )}
      </section>

      <AddNodeTypeForm schemaVersionId={schema.schema_version_id} onAdded={onUpdated} />
      {schema.node_types.length > 0 ? (
        <AddRelationTypeForm
          schemaVersionId={schema.schema_version_id}
          nodeTypes={schema.node_types.map((nodeType) => nodeType.name)}
          onAdded={onUpdated}
        />
      ) : (
        <p className="muted small">İlişki türü eklemek için önce bir düğüm türü gerekir.</p>
      )}
    </>
  );
}

function AddNodeTypeForm({
  schemaVersionId,
  onAdded,
}: {
  schemaVersionId: string;
  onAdded: (schema: SchemaVersionRecord) => void;
}) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [mergeKeys, setMergeKeys] = useState("");
  const [hints, setHints] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      onAdded(
        await addNodeType(schemaVersionId, {
          name: name.trim(),
          display_name: displayName.trim() || name.trim(),
          description: description.trim() || name.trim(),
          merge_keys: splitList(mergeKeys),
          extraction_hints: splitList(hints),
        }),
      );
      setName("");
      setDisplayName("");
      setDescription("");
      setMergeKeys("");
      setHints("");
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
          Düğüm türü ekle
        </Button>
      </div>
    );
  }

  return (
    <form className="card-plain stack" onSubmit={submit}>
      <h4>Düğüm türü ekle</h4>
      <div className="field-grid">
        <label className="field">
          <span>Ad (ASCII)</span>
          <input required type="text" value={name} onChange={(event) => setName(event.currentTarget.value)} placeholder="Narrator" />
        </label>
        <label className="field">
          <span>Görünen ad</span>
          <input type="text" value={displayName} onChange={(event) => setDisplayName(event.currentTarget.value)} placeholder="Ravi" />
        </label>
      </div>
      <label className="field">
        <span>Açıklama</span>
        <input type="text" value={description} onChange={(event) => setDescription(event.currentTarget.value)} />
      </label>
      <div className="field-grid">
        <label className="field">
          <span>Kimlik alanları (virgülle)</span>
          <input type="text" value={mergeKeys} onChange={(event) => setMergeKeys(event.currentTarget.value)} placeholder="name" />
        </label>
        <label className="field">
          <span>Çıkarım ipuçları (virgülle, isteğe bağlı)</span>
          <input type="text" value={hints} onChange={(event) => setHints(event.currentTarget.value)} />
        </label>
      </div>
      {error ? <ErrorNote title="Düğüm türü eklenemedi." error={error} /> : null}
      <div className="row">
        <Button type="submit" variant="primary" size="sm" busy={busy} disabled={name.trim() === ""}>
          Ekle
        </Button>
        <Button variant="quiet" size="sm" onClick={() => setOpen(false)}>
          Vazgeç
        </Button>
      </div>
    </form>
  );
}

function AddRelationTypeForm({
  schemaVersionId,
  nodeTypes,
  onAdded,
}: {
  schemaVersionId: string;
  nodeTypes: string[];
  onAdded: (schema: SchemaVersionRecord) => void;
}) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [fromType, setFromType] = useState(nodeTypes[0] ?? "");
  const [toType, setToType] = useState(nodeTypes[0] ?? "");
  const [description, setDescription] = useState("");
  const [hints, setHints] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      onAdded(
        await addRelationType(schemaVersionId, {
          name: name.trim(),
          from_type: fromType,
          to_type: toType,
          description: description.trim() || name.trim(),
          extraction_hints: splitList(hints),
        }),
      );
      setName("");
      setDescription("");
      setHints("");
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
          İlişki türü ekle
        </Button>
      </div>
    );
  }

  return (
    <form className="card-plain stack" onSubmit={submit}>
      <h4>İlişki türü ekle</h4>
      <label className="field">
        <span>Ad (ASCII)</span>
        <input required type="text" value={name} onChange={(event) => setName(event.currentTarget.value)} placeholder="NARRATED_FROM" />
      </label>
      <div className="field-grid">
        <label className="field">
          <span>Kaynak tür</span>
          <select value={fromType} onChange={(event) => setFromType(event.currentTarget.value)}>
            {nodeTypes.map((nodeType) => (
              <option key={nodeType} value={nodeType}>
                {nodeType}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Hedef tür</span>
          <select value={toType} onChange={(event) => setToType(event.currentTarget.value)}>
            {nodeTypes.map((nodeType) => (
              <option key={nodeType} value={nodeType}>
                {nodeType}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label className="field">
        <span>Açıklama</span>
        <input type="text" value={description} onChange={(event) => setDescription(event.currentTarget.value)} />
      </label>
      <label className="field">
        <span>Çıkarım ipuçları (virgülle, isteğe bağlı)</span>
        <input type="text" value={hints} onChange={(event) => setHints(event.currentTarget.value)} />
      </label>
      {error ? <ErrorNote title="İlişki türü eklenemedi." error={error} /> : null}
      <div className="row">
        <Button type="submit" variant="primary" size="sm" busy={busy} disabled={name.trim() === ""}>
          Ekle
        </Button>
        <Button variant="quiet" size="sm" onClick={() => setOpen(false)}>
          Vazgeç
        </Button>
      </div>
    </form>
  );
}
