"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useProject } from "@/modules/projects/components/project-shell";
import { nextStepWithWork, stepHref } from "@/modules/projects/status";
import { LoadingBlock } from "@/shared/ui/states";

/** Opening a project without naming a step leads to the first step that still has work. */
export function ProjectEntry() {
  const router = useRouter();
  const { project, status } = useProject();

  useEffect(() => {
    if (status) {
      router.replace(stepHref(project.project_id, nextStepWithWork(status)));
    }
  }, [router, project.project_id, status]);

  return (
    <div className="card">
      <LoadingBlock label="Proje açılıyor" />
    </div>
  );
}
