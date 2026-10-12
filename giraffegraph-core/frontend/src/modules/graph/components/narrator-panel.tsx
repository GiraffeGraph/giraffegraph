"use client";

import { useEffect, useRef } from "react";

import type { NarratorNeighbourRecord, NarratorViewRecord } from "@/modules/projects/types";
import { ArabicText } from "@/shared/ui/arabic-text";
import { Button } from "@/shared/ui/button";
import { ErrorNote, LoadingBlock } from "@/shared/ui/states";

export function NarratorPanel({
  name,
  narrator,
  error,
  currentRef,
  onSelectNarrator,
  onSelectHadith,
  onClose,
}: {
  name: string;
  /** Null while it is loading. */
  narrator: NarratorViewRecord | null;
  error: unknown;
  currentRef: string | null;
  onSelectNarrator: (name: string) => void;
  onSelectHadith: (hadithRef: string) => void;
  onClose: () => void;
}) {
  const panelRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    panelRef.current?.scrollIntoView({ block: "nearest", behavior: reduceMotion ? "auto" : "smooth" });
  }, [name]);

  return (
    <aside className="card narrator-panel" ref={panelRef} aria-labelledby="narrator-title">
      <div className="row-between">
        <div className="stack-sm">
          <p className="muted small">Ravi</p>
          <ArabicText as="h3" size="reading" className="narrator-title">
            <span id="narrator-title">{narrator?.name ?? name}</span>
          </ArabicText>
        </div>
        <Button variant="quiet" size="sm" icon="close" onClick={onClose}>
          Kapat
        </Button>
      </div>

      {error ? (
        <ErrorNote title="Ravi bilgisi okunamadı." error={error} />
      ) : !narrator ? (
        <LoadingBlock label="Ravi bilgisi yükleniyor" lines={4} />
      ) : (
        <div className="stack">
          <p className="num">
            Bu ad {narrator.hadith_count} hadiste geçiyor.{" "}
            {narrator.narrated_from_count > 0
              ? `${narrator.narrated_from_count} raviden almış.`
              : "Birinden aldığını gösteren bir bağlantı yok."}{" "}
            {narrator.narrated_to_count > 0
              ? `${narrator.narrated_to_count} ravi ondan almış.`
              : "Ondan alan bir ravi yok."}
          </p>

          <NeighbourList
            title="Kimden almış?"
            empty="Grafa yazılmış böyle bir bağlantı yok."
            items={narrator.narrated_from}
            onSelectNarrator={onSelectNarrator}
          />
          <NeighbourList
            title="Ondan kimler almış?"
            empty="Grafa yazılmış böyle bir bağlantı yok."
            items={narrator.narrated_to}
            onSelectNarrator={onSelectNarrator}
          />

          <div className="stack-sm">
            <h4>Geçtiği hadisler</h4>
            <ul className="row">
              {narrator.hadiths.map((hadith) => (
                <li key={hadith.source_unit_id}>
                  <button
                    type="button"
                    className={`chip${hadith.hadith_ref === currentRef ? " is-selected" : ""}`}
                    aria-pressed={hadith.hadith_ref === currentRef}
                    onClick={() => onSelectHadith(hadith.hadith_ref)}
                  >
                    {hadith.hadith_ref}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <p className="muted small">
            Ravi, metinde yazıldığı adla tanınır; bu yüzden aynı adı taşıyan farklı kişiler burada
            tek kayıt olarak görünür.
          </p>
        </div>
      )}
    </aside>
  );
}

function NeighbourList({
  title,
  empty,
  items,
  onSelectNarrator,
}: {
  title: string;
  empty: string;
  items: NarratorNeighbourRecord[];
  onSelectNarrator: (name: string) => void;
}) {
  return (
    <div className="stack-sm">
      <h4>{title}</h4>
      {items.length === 0 ? (
        <p className="muted small">{empty}</p>
      ) : (
        <ul className="neighbour-list">
          {items.map((item) => (
            <li key={item.name}>
              <button
                type="button"
                className="neighbour"
                onClick={() => onSelectNarrator(item.name)}
              >
                <ArabicText>{item.name}</ArabicText>
                <span className="muted small num">
                  {item.link_count} bağlantı · {item.hadith_refs.join(", ")}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
