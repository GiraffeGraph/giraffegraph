import type { Suggestion } from "@/modules/review/suggestion";
import { ArabicText } from "@/shared/ui/arabic-text";
import { Icon } from "@/shared/ui/icons";

const UNKNOWN_NARRATOR = "adı okunamayan ravi";

function NarratorName({ name }: { name: string | null }) {
  return name ? (
    <ArabicText as="p" size="md" className="suggestion-name">
      {name}
    </ArabicText>
  ) : (
    <p className="muted">{UNKNOWN_NARRATOR}</p>
  );
}

/** What the system suggested, without any of its internal names. */
export function SuggestionView({ suggestion }: { suggestion: Suggestion }) {
  if (suggestion.kind === "narrator") {
    return (
      <div className="stack-sm">
        <p className="muted">Sistem bu metinde bir ravi adı buldu:</p>
        <ArabicText as="p" size="reading" className="suggestion-name">
          {suggestion.name}
        </ArabicText>
      </div>
    );
  }

  if (suggestion.kind === "link") {
    const place = [
      suggestion.chainNo !== null ? `${suggestion.chainNo}. zincir` : null,
      suggestion.position !== null ? `${suggestion.position}. bağlantı` : null,
    ]
      .filter(Boolean)
      .join(", ");
    return (
      <div className="stack-sm">
        <p className="muted">Sistem iki ravi arasında bir aktarım öneriyor:</p>
        <div className="link-figure">
          <NarratorName name={suggestion.from} />
          <p className="link-figure-arrow">
            <Icon name="arrowDown" />
            <span>
              şu raviden almış
              {suggestion.sigha ? (
                <>
                  ; rivayet lafzı: <ArabicText size="sm">{suggestion.sigha}</ArabicText>
                </>
              ) : null}
            </span>
          </p>
          <NarratorName name={suggestion.to} />
        </div>
        {place ? <p className="muted small">Yeri: {place}.</p> : null}
      </div>
    );
  }

  if (suggestion.kind === "record") {
    return (
      <div className="stack-sm">
        <p className="muted">
          Sistem bir kayıt öneriyor (<code>{suggestion.typeName}</code>):
        </p>
        <dl className="field-list">
          {suggestion.fields.map((field) => (
            <div key={field.label}>
              <dt>{field.label}</dt>
              <dd dir="auto">{field.value}</dd>
            </div>
          ))}
        </dl>
      </div>
    );
  }

  return (
    <div className="stack-sm">
      <p>
        {suggestion.fieldName ? (
          <>
            Sistem, <code>{suggestion.typeName}</code> türünde tanımlı olmayan bir alan kullandı:{" "}
            <code>{suggestion.fieldName}</code>.
          </>
        ) : (
          <>
            Sistem, tanımlı olmayan bir tür kullandı: <code>{suggestion.typeName}</code>.
          </>
        )}
      </p>
      {suggestion.sampleValue ? (
        <p className="muted small" dir="auto">
          Örnek değer: {suggestion.sampleValue}
        </p>
      ) : null}
      {suggestion.count !== null ? (
        <p className="muted small">Bu hadiste {suggestion.count} kez geçti.</p>
      ) : null}
    </div>
  );
}
