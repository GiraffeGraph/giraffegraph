"use client";

import { useId, useState, type KeyboardEvent } from "react";

import { GraphExplorer } from "@/modules/graph/components/graph-explorer";
import { useProject } from "@/modules/projects/components/project-shell";
import { JobsPanel } from "@/modules/runs/components/jobs-panel";
import { StepRunner } from "@/modules/runs/components/step-runner";
import { SchemaEditor } from "@/modules/schema-studio/components/schema-editor";

const SECTIONS = [
  { key: "schema", label: "Şema" },
  { key: "runner", label: "Adım adım işlem" },
  { key: "jobs", label: "İşler" },
  { key: "graph", label: "Ham graf" },
] as const;

type SectionKey = (typeof SECTIONS)[number]["key"];

/** Everything a developer needs and a researcher does not, behind one secondary entry. */
export function AdvancedScreen() {
  const { project } = useProject();
  const [section, setSection] = useState<SectionKey>("schema");
  const baseId = useId();

  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") {
      return;
    }
    const index = SECTIONS.findIndex((item) => item.key === section);
    const step = event.key === "ArrowRight" ? 1 : -1;
    const next = SECTIONS[(index + step + SECTIONS.length) % SECTIONS.length];
    setSection(next.key);
    document.getElementById(`${baseId}-${next.key}`)?.focus();
  }

  return (
    <section className="step-screen" aria-labelledby="advanced-title">
      <div className="step-intro">
        <h2 id="advanced-title">Gelişmiş</h2>
        <p className="lead">
          Bu bölüm sistemi geliştirenler içindir: şema tanımları, işlemin tek tek adımları, arka
          plan işleri ve grafın ham kayıtları. Günlük çalışma için yukarıdaki dört adım yeterlidir.
        </p>
      </div>

      <div className="tabs" role="tablist" aria-label="Gelişmiş bölümleri" onKeyDown={onKeyDown}>
        {SECTIONS.map((item) => (
          <button
            key={item.key}
            id={`${baseId}-${item.key}`}
            type="button"
            role="tab"
            className="tab"
            aria-selected={item.key === section}
            aria-controls={`${baseId}-panel`}
            tabIndex={item.key === section ? 0 : -1}
            onClick={() => setSection(item.key)}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div id={`${baseId}-panel`} role="tabpanel" aria-labelledby={`${baseId}-${section}`}>
        {section === "schema" ? (
          <SchemaEditor project={project} />
        ) : section === "runner" ? (
          <StepRunner project={project} />
        ) : section === "jobs" ? (
          <JobsPanel project={project} />
        ) : (
          <GraphExplorer project={project} />
        )}
      </div>
    </section>
  );
}
