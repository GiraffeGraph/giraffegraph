"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { createProject } from "@/modules/projects/api";
import { stepHref } from "@/modules/projects/status";
import { Button } from "@/shared/ui/button";
import { ErrorNote } from "@/shared/ui/states";

/** New projects use the isnad template; its types and fields are applied in the same request. */
const DEFAULT_TEMPLATE_ID = "isnad";

export function ProjectCreateForm({ onCancel }: { onCancel: () => void }) {
  const router = useRouter();
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const project = await createProject({
        name: name.trim(),
        template_id: DEFAULT_TEMPLATE_ID,
        apply_template_schema: true,
      });
      router.push(stepHref(project.project_id, "yukle"));
    } catch (reason: unknown) {
      setError(reason);
      setBusy(false);
    }
  }

  return (
    <form className="card stack create-form" onSubmit={submit}>
      <label className="field">
        <span>Projene bir ad ver</span>
        <input
          type="text"
          name="project-name"
          required
          autoFocus
          maxLength={120}
          value={name}
          onChange={(event) => setName(event.currentTarget.value)}
          placeholder="Örneğin: Müslim’den seçmeler"
        />
        <span className="field-hint">
          Proje, hadis isnadı için hazır ayarlarla açılır; başka bir şey seçmen gerekmez.
        </span>
      </label>
      {error ? <ErrorNote title="Proje oluşturulamadı." error={error} /> : null}
      <div className="row">
        <Button type="submit" variant="primary" busy={busy} disabled={name.trim() === ""}>
          {busy ? "Oluşturuluyor" : "Projeyi oluştur"}
        </Button>
        <Button variant="quiet" onClick={onCancel} disabled={busy}>
          Vazgeç
        </Button>
      </div>
    </form>
  );
}
