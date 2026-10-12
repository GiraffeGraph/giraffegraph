"use client";

import { useEffect, useState } from "react";

import { listProjects } from "@/modules/projects/api";
import { ProjectCard } from "@/modules/projects/components/project-card";
import { ProjectCreateForm } from "@/modules/projects/components/project-create-form";
import type { ProjectRecord } from "@/modules/projects/types";
import { Button } from "@/shared/ui/button";
import { EmptyState, ErrorNote, Skeleton } from "@/shared/ui/states";

export function HomeScreen() {
  const [projects, setProjects] = useState<ProjectRecord[] | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [reloadToken, setReloadToken] = useState(0);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    void listProjects()
      .then((items) => {
        if (!cancelled) {
          setProjects(items);
        }
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setError(reason);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [reloadToken]);

  return (
    <main id="icerik" className="page home">
      <section className="home-intro stack">
        <h1>Hadis metninden ravi zincirine</h1>
        <p className="lead">
          GiraffeGraph bir hadis metnindeki ravi zincirini çıkarır ve bir grafa kaydeder. Sistem
          önerir, her öneriyi metinle karşılaştırır; emin olamadığı yerde senin kararını bekler.
        </p>
      </section>

      <section className="stack" aria-labelledby="projects-title">
        <div className="section-title">
          <h2 id="projects-title">Projeler</h2>
          {!creating && !error ? (
            <Button variant="primary" icon="plus" onClick={() => setCreating(true)}>
              Yeni proje
            </Button>
          ) : null}
        </div>

        {creating ? <ProjectCreateForm onCancel={() => setCreating(false)} /> : null}

        {error ? (
          <ErrorNote
            title="Projeler okunamadı."
            error={error}
            onRetry={() => setReloadToken((token) => token + 1)}
          />
        ) : projects === null ? (
          <ul className="project-grid" aria-busy="true">
            {[0, 1].map((index) => (
              <li key={index} className="project-card is-placeholder" role="status">
                <span className="visually-hidden">Projeler yükleniyor</span>
                <Skeleton width="60%" height="1.3em" />
                <Skeleton width="80%" height="0.9em" />
                <Skeleton width="34%" height="0.9em" />
              </li>
            ))}
          </ul>
        ) : projects.length === 0 ? (
          creating ? null : (
            <EmptyState
              icon="book"
              title="Henüz proje yok"
              action={
                <Button variant="primary" icon="plus" onClick={() => setCreating(true)}>
                  İlk projeni oluştur
                </Button>
              }
            >
              Proje, birlikte çalışacağın hadislerin durduğu yerdir. Oluşturduğunda burada bir kart
              olarak görünür; içine kendi metinlerini ya da örnek hadisleri yükleyebilirsin.
            </EmptyState>
          )
        ) : (
          <ul className="project-grid">
            {projects.map((project) => (
              <li key={project.project_id}>
                <ProjectCard project={project} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
