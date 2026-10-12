"use client";

import { Fragment, useMemo } from "react";

import { Acceptance, isHumanAccepted } from "@/modules/graph/components/acceptance";
import type {
  ChainLinkRecord,
  ChainNarratorRecord,
  FactAcceptanceRecord,
  HadithChainViewRecord,
  NarratorChainRecord,
} from "@/modules/projects/types";
import { formatDateTime } from "@/shared/format";
import { ArabicText, renderMarkedText, type TextMark } from "@/shared/ui/arabic-text";
import { Icon } from "@/shared/ui/icons";
import { Note } from "@/shared/ui/states";

const METHOD_NAMES: Record<string, string> = {
  rule_based_isnad: "kurallarla",
  openai: "dil modeliyle (OpenAI)",
  anthropic: "dil modeliyle (Claude)",
};

interface NarratorMark {
  start: number;
  end: number;
  name: string;
}

/** Where each accepted narrator is mentioned in the text; overlapping mentions keep the first. */
function buildNarratorMarks(narrators: ChainNarratorRecord[]): NarratorMark[] {
  const marks = narrators.flatMap((narrator) =>
    narrator.evidence.flatMap((evidence) =>
      evidence.source_start_offset !== null && evidence.source_end_offset !== null
        ? [
            {
              start: evidence.source_start_offset,
              end: evidence.source_end_offset,
              name: narrator.name,
            },
          ]
        : [],
    ),
  );
  marks.sort((left, right) => left.start - right.start || right.end - left.end);
  const kept: NarratorMark[] = [];
  let cursor = 0;
  for (const mark of marks) {
    if (mark.start >= cursor) {
      kept.push(mark);
      cursor = mark.end;
    }
  }
  return kept;
}

export function HadithChains({
  view,
  selectedNarrator,
  onSelectNarrator,
}: {
  view: HadithChainViewRecord;
  selectedNarrator: string | null;
  onSelectNarrator: (name: string) => void;
}) {
  const marks = useMemo(() => buildNarratorMarks(view.narrators), [view.narrators]);
  const acceptanceByName = useMemo(
    () => new Map(view.narrators.map((narrator) => [narrator.name, narrator.acceptance])),
    [view.narrators],
  );
  const mentionCount = view.narrators.reduce((total, narrator) => total + narrator.evidence.length, 0);
  const linkedNames = new Set(view.chains.flatMap((chain) => chain.narrators));
  const unlinked = view.narrators.filter((narrator) => !linkedNames.has(narrator.name));
  const latestRun = view.runs[0] ?? null;
  const unmarked = mentionCount - marks.length;

  const textMarks: TextMark[] = marks.map((mark) => ({
    start: mark.start,
    end: mark.end,
    selected: mark.name === selectedNarrator,
    title: "Bu raviyi aç",
    onSelect: () => onSelectNarrator(mark.name),
  }));

  return (
    <div className="stack-lg">
      <header className="stack-sm">
        <h3 className="hadith-title">{view.hadith_ref}</h3>
        {latestRun ? (
          <p className="muted small">
            Grafa yazıldı: {formatDateTime(latestRun.committed_at)}. Zincir{" "}
            {METHOD_NAMES[latestRun.llm_provider ?? ""] ?? "sunucunun varsayılan yöntemiyle"}{" "}
            çıkarıldı.
            {view.runs.length > 1 ? ` Bu hadis ${view.runs.length} kez işlendi.` : ""}
          </p>
        ) : null}
      </header>

      {!view.source_unit ? (
        <Note tone="attention">
          <p>Bu adla yüklenmiş bir hadis bulunamadı.</p>
        </Note>
      ) : (
        <>
          <section className="stack-sm" aria-label="Hadis metni">
            <div className="arabic-block">
              <ArabicText as="p" size="reading">
                {renderMarkedText(view.source_unit.raw_content, textMarks, "codepoint")}
              </ArabicText>
            </div>
            <p className="muted small">
              {marks.length > 0
                ? "İşaretli adlar bu hadisin ravileridir; bir ada tıkladığında o ravi açılır."
                : "Bu metinde işaretlenecek ravi adı yok."}
              {unmarked > 0
                ? ` ${unmarked} ad ayrıca işaretlenemedi: metindeki yeri saklanmamış ya da başka bir adla aynı yere denk geliyor.`
                : ""}
            </p>
          </section>

          <section className="stack" aria-labelledby="chains-title">
            <div className="stack-sm">
              <h4 id="chains-title">{view.chains.length > 1 ? "Zincirler" : "Zincir"}</h4>
              {view.chains.length > 0 ? (
                <p className="muted small measure">
                  Yukarıdan aşağıya okunur: üstteki ravi hadisi bir alttakinden almıştır.
                  {view.chains.length > 1
                    ? ` Bu hadis ${view.chains.length} ayrı zincirle aktarılmış.`
                    : ""}{" "}
                  Yanında not olmayan raviler otomatik kabul edildi (kontrollerden geçti).
                </p>
              ) : null}
            </div>

            {!view.committed ? (
              <Note>
                <p>
                  Bu hadis için grafa yazılmış bir zincir yok. Bekleyen öneriler varsa önce İncele
                  adımında karara bağlanmaları gerekir.
                </p>
              </Note>
            ) : view.chains.length === 0 ? (
              <Note>
                <p>Bu hadiste iki ravi arasında kabul edilmiş bir bağlantı yok.</p>
              </Note>
            ) : (
              <div className="chain-columns">
                {view.chains.map((chain) => (
                  <ChainColumn
                    key={chain.chain_no}
                    chain={chain}
                    acceptanceByName={acceptanceByName}
                    selectedNarrator={selectedNarrator}
                    onSelectNarrator={onSelectNarrator}
                  />
                ))}
              </div>
            )}

            {unlinked.length > 0 ? (
              <div className="stack-sm">
                <p className="muted small">Kabul edilmiş ama bir zincire bağlanmamış raviler:</p>
                <ul className="row">
                  {unlinked.map((narrator) => (
                    <li key={narrator.name}>
                      <NarratorButton
                        name={narrator.name}
                        acceptance={narrator.acceptance}
                        selected={narrator.name === selectedNarrator}
                        onSelect={onSelectNarrator}
                      />
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </section>
        </>
      )}
    </div>
  );
}

function ChainColumn({
  chain,
  acceptanceByName,
  selectedNarrator,
  onSelectNarrator,
}: {
  chain: NarratorChainRecord;
  acceptanceByName: Map<string, FactAcceptanceRecord | null>;
  selectedNarrator: string | null;
  onSelectNarrator: (name: string) => void;
}) {
  const renderNarrator = (name: string) => (
    <li>
      <NarratorButton
        name={name}
        acceptance={acceptanceByName.get(name) ?? null}
        selected={name === selectedNarrator}
        onSelect={onSelectNarrator}
      />
    </li>
  );

  return (
    <article className="chain-column">
      <header>
        <strong>{chain.chain_no}. zincir</strong>
        <span className="muted small num">{chain.narrators.length} ravi</span>
      </header>
      <ol className="chain-list">
        {chain.links.map((link, index) => {
          const previous = chain.links[index - 1];
          const continues = previous !== undefined && previous.to_narrator === link.from_narrator;
          return (
            <Fragment key={link.position}>
              {previous !== undefined && !continues ? (
                <li className="chain-gap">
                  <Icon name="alert" />
                  Zincir burada kesik: aradaki bağlantı grafa yazılmamış.
                </li>
              ) : null}
              {!continues ? renderNarrator(link.from_narrator) : null}
              <ChainLink link={link} />
              {renderNarrator(link.to_narrator)}
            </Fragment>
          );
        })}
      </ol>
    </article>
  );
}

function ChainLink({ link }: { link: ChainLinkRecord }) {
  return (
    <li className="chain-link">
      <span className="chain-link-arrow">
        <Icon name="arrowDown" label="şundan almış" />
      </span>
      <div className="chain-link-body">
        <p>
          <span className="muted small">Rivayet lafzı:</span>{" "}
          {link.sigha ? (
            <ArabicText size="sm">{link.sigha}</ArabicText>
          ) : (
            <span className="muted small">kaydedilmemiş</span>
          )}
        </p>
        {link.evidence.length === 0 ? (
          <p className="muted small">Bu bağlantı için alıntı saklanmamış.</p>
        ) : (
          link.evidence.map((evidence, index) => (
            <p key={index} className="chain-link-quote">
              <span className="muted small">Alıntı:</span>{" "}
              {evidence.quote ? (
                <ArabicText as="q" size="sm" className="quote">
                  {evidence.quote}
                </ArabicText>
              ) : (
                <span className="muted small">saklanmamış</span>
              )}
            </p>
          ))
        )}
        <Acceptance acceptance={link.acceptance} />
      </div>
    </li>
  );
}

function NarratorButton({
  name,
  acceptance,
  selected,
  onSelect,
}: {
  name: string;
  acceptance: FactAcceptanceRecord | null;
  selected: boolean;
  onSelect: (name: string) => void;
}) {
  return (
    <div className="chain-narrator">
      <button
        type="button"
        className={`narrator-button${selected ? " is-selected" : ""}`}
        aria-pressed={selected}
        title="Bu raviyi aç"
        onClick={() => onSelect(name)}
      >
        <ArabicText>{name}</ArabicText>
      </button>
      {acceptance === null || isHumanAccepted(acceptance) ? (
        <Acceptance acceptance={acceptance} />
      ) : null}
    </div>
  );
}
