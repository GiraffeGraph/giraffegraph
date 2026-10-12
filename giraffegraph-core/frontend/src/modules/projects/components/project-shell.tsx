"use client";

import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { getProject } from "@/modules/projects/api";
import {
  describeStatus,
  loadProjectStatus,
  stepHref,
  type ProjectStatus,
  type StepKey,
} from "@/modules/projects/status";
import type { ProjectRecord } from "@/modules/projects/types";
import { ApiError } from "@/shared/api/errors";
import { ButtonLink } from "@/shared/ui/button";
import { Icon } from "@/shared/ui/icons";
import { EmptyState, ErrorNote, Note, Skeleton } from "@/shared/ui/states";
import { Stepper, type StepItem } from "@/shared/ui/stepper";

interface ProjectContextValue {
  project: ProjectRecord;
  /** Null until the first counts arrive. */
  status: ProjectStatus | null;
  /** Reads the counts again; call it after anything that changes them. */
  refreshStatus: () => Promise<ProjectStatus | null>;
}

const ProjectContext = createContext<ProjectContextValue | null>(null);

export function useProject(): ProjectContextValue {
  const value = useContext(ProjectContext);
  if (!value) {
    throw new Error("useProject, ProjectShell içinde kullanılmalı.");
  }
  return value;
}

function buildSteps(projectId: string, status: ProjectStatus | null): StepItem[] {
  const waiting = status?.waitingToExtract.length ?? 0;
  return [
    {
      key: "yukle",
      href: stepHref(projectId, "yukle"),
      title: "Metin yükle",
      count: status ? (status.total > 0 ? `${status.total} hadis yüklü` : "Henüz metin yok") : null,
      tone: status && status.total > 0 ? "done" : "idle",
    },
    {
      key: "cikar",
      href: stepHref(projectId, "cikar"),
      title: "Zincirleri çıkar",
      count: !status
        ? null
        : status.total === 0
          ? "Önce metin gerekli"
          : waiting > 0
            ? `${waiting} hadis sırada`
            : "Hepsi işlendi",
      tone: status && status.total > 0 && waiting === 0 ? "done" : "idle",
    },
    {
      key: "incele",
      href: stepHref(projectId, "incele"),
      title: "İncele",
      count: !status
        ? null
        : status.openSuggestions > 0
          ? `${status.openSuggestions} öneri seni bekliyor`
          : status.readyToWrite > 0
            ? `${status.readyToWrite} hadis yazılmaya hazır`
            : "Bekleyen yok",
      tone:
        status && (status.openSuggestions > 0 || status.readyToWrite > 0) ? "attention" : "idle",
    },
    {
      key: "oku",
      href: stepHref(projectId, "oku"),
      title: "Zincirleri oku",
      count: status ? (status.inGraph > 0 ? `${status.inGraph} hadis grafta` : "Henüz yok") : null,
      tone: status && status.inGraph > 0 ? "done" : "idle",
    },
  ];
}

const STEP_KEYS: readonly StepKey[] = ["yukle", "cikar", "incele", "oku"];

export function ProjectShell({ children }: { children: ReactNode }) {
  const { projectId } = useParams<{ projectId: string }>();
  const pathname = usePathname();
  const segment = pathname.split("/")[3] ?? "";
  const currentStep = STEP_KEYS.find((key) => key === segment) ?? null;
  const onAdvanced = segment === "gelismis";

  const [project, setProject] = useState<ProjectRecord | null>(null);
  const [projectError, setProjectError] = useState<unknown>(null);
  const [status, setStatus] = useState<ProjectStatus | null>(null);
  const [statusError, setStatusError] = useState<unknown>(null);
  const [reloadToken, setReloadToken] = useState(0);

  const refreshStatus = useCallback(async () => {
    try {
      const next = await loadProjectStatus(projectId);
      setStatus(next);
      setStatusError(null);
      return next;
    } catch (error: unknown) {
      setStatusError(error);
      return null;
    }
  }, [projectId]);

  useEffect(() => {
    let cancelled = false;
    setProjectError(null);
    void getProject(projectId)
      .then((record) => {
        if (!cancelled) {
          setProject(record);
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setProjectError(error);
        }
      });
    void refreshStatus();
    return () => {
      cancelled = true;
    };
  }, [projectId, reloadToken, refreshStatus]);

  const steps = useMemo(() => buildSteps(projectId, status), [projectId, status]);
  const contextValue = useMemo(
    () => (project ? { project, status, refreshStatus } : null),
    [project, status, refreshStatus],
  );

  if (projectError) {
    const missing = projectError instanceof ApiError && projectError.status === 404;
    return (
      <div className="page stack-lg">
        {missing ? (
          <EmptyState
            icon="search"
            title="Bu proje bulunamadı"
            action={
              <ButtonLink href="/" variant="primary" icon="arrowLeft">
                Projelere dön
              </ButtonLink>
            }
          >
            Adres yanlış olabilir ya da sunucu yeniden başlatılmış olabilir. Sunucu verileri
            bellekte tutuyorsa yeniden başlatınca projeler silinir.
          </EmptyState>
        ) : (
          <ErrorNote
            title="Proje açılamadı."
            error={projectError}
            onRetry={() => setReloadToken((token) => token + 1)}
            actions={
              <ButtonLink href="/" size="sm">
                Projelere dön
              </ButtonLink>
            }
          />
        )}
      </div>
    );
  }

  return (
    <div className="page project-page">
      <div className="project-header">
        <div className="stack-sm">
          <Link href="/" className="back-link">
            <Icon name="arrowLeft" />
            Projeler
          </Link>
          <h1>{project ? project.name : <Skeleton width="14ch" height="1em" />}</h1>
          <p className="muted num project-status-line" role="status">
            {status ? describeStatus(status) : <Skeleton width="26ch" height="0.9em" />}
          </p>
        </div>
        <ButtonLink
          href={onAdvanced ? stepHref(projectId, "yukle") : stepHref(projectId, "gelismis")}
          variant="quiet"
          size="sm"
          icon={onAdvanced ? "arrowLeft" : "gear"}
        >
          {onAdvanced ? "Adımlara dön" : "Gelişmiş"}
        </ButtonLink>
      </div>

      <Stepper steps={steps} currentKey={currentStep} />

      {statusError ? (
        <ErrorNote
          title="Projenin güncel sayıları okunamadı."
          error={statusError}
          onRetry={() => void refreshStatus()}
        />
      ) : null}

      {project && project.template_id !== "isnad" && !onAdvanced ? (
        <Note>
          <p>
            Bu proje hadis isnadı şablonuyla açılmamış. Dört adım isnad için tasarlandı; bu
            projenin türlerini ve alanlarını{" "}
            <Link className="text-link" href={stepHref(projectId, "gelismis")}>
              Gelişmiş
            </Link>{" "}
            bölümünden yönetebilirsin.
          </p>
        </Note>
      ) : null}

      <main id="icerik" className="project-main">
        {contextValue ? (
          <ProjectContext.Provider value={contextValue}>{children}</ProjectContext.Provider>
        ) : (
          <div className="card" role="status">
            <span className="visually-hidden">Proje yükleniyor</span>
            <div className="stack">
              <Skeleton width="30%" height="1.4em" />
              <Skeleton width="80%" />
              <Skeleton width="64%" />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
