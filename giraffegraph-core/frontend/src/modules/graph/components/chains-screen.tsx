"use client";

import { useEffect, useState } from "react";

import { HadithChains } from "@/modules/graph/components/hadith-chains";
import { NarratorPanel } from "@/modules/graph/components/narrator-panel";
import { getHadithChains, getNarrator, listCommittedHadiths } from "@/modules/projects/api";
import { useProject } from "@/modules/projects/components/project-shell";
import { nextStepWithWork, STEP_ACTION, stepHref } from "@/modules/projects/status";
import type {
  CommittedHadithRecord,
  HadithChainViewRecord,
  NarratorViewRecord,
} from "@/modules/projects/types";
import { formatDateTime } from "@/shared/format";
import { ButtonLink } from "@/shared/ui/button";
import { EmptyState, ErrorNote, LoadingBlock, Skeleton } from "@/shared/ui/states";

export function ChainsScreen() {
  const { project, status } = useProject();
  const projectId = project.project_id;

  const [hadiths, setHadiths] = useState<CommittedHadithRecord[] | null>(null);
  const [listError, setListError] = useState<unknown>(null);
  const [reloadToken, setReloadToken] = useState(0);
  const [search, setSearch] = useState("");
  const [selectedRef, setSelectedRef] = useState<string | null>(null);

  const [view, setView] = useState<HadithChainViewRecord | null>(null);
  const [viewError, setViewError] = useState<unknown>(null);

  const [narratorName, setNarratorName] = useState<string | null>(null);
  const [narrator, setNarrator] = useState<NarratorViewRecord | null>(null);
  const [narratorError, setNarratorError] = useState<unknown>(null);

  useEffect(() => {
    let cancelled = false;
    setListError(null);
    void listCommittedHadiths(projectId)
      .then((result) => {
        if (cancelled) {
          return;
        }
        setHadiths(result.hadiths);
        setSelectedRef((current) => current ?? result.hadiths[0]?.hadith_ref ?? null);
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setListError(reason);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, reloadToken]);

  useEffect(() => {
    if (!selectedRef) {
      setView(null);
      return;
    }
    let cancelled = false;
    setViewError(null);
    void getHadithChains(projectId, selectedRef)
      .then((result) => {
        if (!cancelled) {
          setView(result);
        }
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setView(null);
          setViewError(reason);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, selectedRef, reloadToken]);

  useEffect(() => {
    setNarrator(null);
    setNarratorError(null);
    if (!narratorName) {
      return;
    }
    let cancelled = false;
    void getNarrator(projectId, narratorName)
      .then((result) => {
        if (!cancelled) {
          setNarrator(result);
        }
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setNarratorError(reason);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, narratorName, reloadToken]);

  const needle = search.trim().toLocaleLowerCase("tr");
  const visible = (hadiths ?? []).filter(
    (hadith) =>
      needle === "" ||
      hadith.hadith_ref.toLocaleLowerCase("tr").includes(needle) ||
      hadith.title.toLocaleLowerCase("tr").includes(needle),
  );
  const next = status ? nextStepWithWork(status) : null;
  const viewIsCurrent = view !== null && view.hadith_ref === selectedRef;

  return (
    <section className="step-screen" aria-labelledby="step-title">
      <div className="step-intro">
        <h2 id="step-title">Zincirleri oku</h2>
        <p className="lead">
          Grafa yazılmış hadisler burada. Her bağlantının yanında, metinde dayandığı sözleri ve onu
          kimin ya da hangi otomatik kontrolün kabul ettiğini görürsün.
        </p>
      </div>

      {listError ? (
        <ErrorNote
          title="Hadis listesi okunamadı."
          error={listError}
          onRetry={() => setReloadToken((token) => token + 1)}
        />
      ) : hadiths !== null && hadiths.length === 0 ? (
        <EmptyState
          icon="chain"
          title="Henüz grafa yazılmış hadis yok"
          action={
            next && next !== "oku" ? (
              <ButtonLink
                href={stepHref(projectId, next)}
                variant="primary"
                iconAfter="arrowRight"
              >
                {STEP_ACTION[next]}
              </ButtonLink>
            ) : null
          }
        >
          Bir hadisin zinciri çıkarılıp önerileri kabul edildiğinde burada listelenir; metnini,
          ravilerini ve her bağlantının dayandığı alıntıyı buradan okursun.
        </EmptyState>
      ) : (
        <div className="chains-layout">
          <nav className="hadith-nav" aria-label="Grafa yazılmış hadisler">
            <label className="field">
              <span>Hadis ara</span>
              <input
                type="search"
                name="hadith-search"
                value={search}
                onChange={(event) => setSearch(event.currentTarget.value)}
                placeholder="Örneğin: Muslim:974"
              />
            </label>
            {hadiths === null ? (
              <div className="stack-sm" role="status">
                <span className="visually-hidden">Hadisler yükleniyor</span>
                {[0, 1, 2, 3].map((index) => (
                  <Skeleton key={index} height="52px" />
                ))}
              </div>
            ) : visible.length === 0 ? (
              <p className="muted small">
                “{search}” ile eşleşen hadis yok. Aramayı kısaltmayı deneyebilirsin.
              </p>
            ) : (
              <ul className="hadith-list">
                {visible.map((hadith) => (
                  <li key={hadith.source_unit_id}>
                    <button
                      type="button"
                      className={`hadith-row${hadith.hadith_ref === selectedRef ? " is-selected" : ""}`}
                      aria-current={hadith.hadith_ref === selectedRef ? "true" : undefined}
                      onClick={() => setSelectedRef(hadith.hadith_ref)}
                    >
                      <strong>{hadith.hadith_ref}</strong>
                      <span className="muted small num">{formatDateTime(hadith.committed_at)}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {hadiths !== null && hadiths.length > 0 ? (
              <p className="muted small num">
                {visible.length === hadiths.length
                  ? `${hadiths.length} hadis`
                  : `${hadiths.length} hadisten ${visible.length} tanesi gösteriliyor`}
              </p>
            ) : null}
          </nav>

          <div className={`chains-detail${narratorName ? " has-narrator" : ""}`}>
            <div className="card chains-main">
              {viewError ? (
                <ErrorNote
                  title="Bu hadisin zincirleri okunamadı."
                  error={viewError}
                  onRetry={() => setReloadToken((token) => token + 1)}
                />
              ) : view ? (
                <div className={viewIsCurrent ? undefined : "is-stale"} aria-busy={!viewIsCurrent}>
                  <HadithChains
                    view={view}
                    selectedNarrator={narratorName}
                    onSelectNarrator={setNarratorName}
                  />
                </div>
              ) : (
                <div className="stack-lg">
                  <Skeleton width="12ch" height="1.4em" />
                  <LoadingBlock label="Zincirler yükleniyor" lines={6} />
                </div>
              )}
            </div>

            {narratorName ? (
              <NarratorPanel
                name={narratorName}
                narrator={narrator}
                error={narratorError}
                currentRef={selectedRef}
                onSelectNarrator={setNarratorName}
                onSelectHadith={setSelectedRef}
                onClose={() => setNarratorName(null)}
              />
            ) : null}
          </div>
        </div>
      )}
    </section>
  );
}
