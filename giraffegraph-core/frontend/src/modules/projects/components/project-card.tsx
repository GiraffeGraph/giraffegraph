"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  describeStatus,
  loadProjectStatus,
  nextStepWithWork,
  STEP_ACTION,
  stepHref,
  type ProjectStatus,
} from "@/modules/projects/status";
import type { ProjectRecord } from "@/modules/projects/types";
import { Icon } from "@/shared/ui/icons";
import { Skeleton } from "@/shared/ui/states";

export function ProjectCard({ project }: { project: ProjectRecord }) {
  const [status, setStatus] = useState<ProjectStatus | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void loadProjectStatus(project.project_id)
      .then((result) => {
        if (!cancelled) {
          setStatus(result);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setFailed(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [project.project_id]);

  const needsPerson = status !== null && (status.openSuggestions > 0 || status.readyToWrite > 0);
  // The card leads to what its status line says is waiting; a person's decision comes first.
  const next = !status ? null : needsPerson ? "incele" : nextStepWithWork(status);
  const href = next ? stepHref(project.project_id, next) : `/proje/${project.project_id}`;

  return (
    <Link href={href} className="project-card">
      <h3>{project.name}</h3>
      <p className="muted num project-card-status">
        {status ? (
          describeStatus(status)
        ) : failed ? (
          "Sayılar şu an okunamadı"
        ) : (
          <Skeleton width="80%" height="0.9em" />
        )}
      </p>
      <span className={`status ${needsPerson ? "status-attention" : "status-accent"}`}>
        {next ? (
          <>
            {needsPerson ? <Icon name="person" /> : null}
            {STEP_ACTION[next]}
            <Icon name="arrowRight" />
          </>
        ) : failed ? (
          <>
            Projeyi aç
            <Icon name="arrowRight" />
          </>
        ) : (
          <Skeleton width="9ch" height="0.9em" />
        )}
      </span>
    </Link>
  );
}
