"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/shared/ui/button";

/** Asked once, kept in the browser, sent with every decision as the reviewer's name. */
export function ReviewerNameForm({
  initial,
  onSave,
  onCancel,
}: {
  initial: string;
  onSave: (name: string) => void;
  onCancel?: () => void;
}) {
  const [name, setName] = useState(initial);

  function submit(event: FormEvent) {
    event.preventDefault();
    const trimmed = name.trim();
    if (trimmed !== "") {
      onSave(trimmed);
    }
  }

  return (
    <form className="card stack reviewer-form" onSubmit={submit}>
      <div className="stack-sm">
        <h3>{initial ? "Adını değiştir" : "Önce tanışalım"}</h3>
        <p className="muted measure">
          Verdiğin her karar adınla birlikte kaydedilir; böylece bir bilgiyi kimin onayladığı
          sonradan görülebilir. Bu bir hesap değildir, yazdığın ad olduğu gibi saklanır.
        </p>
      </div>
      <label className="field">
        <span>Adın</span>
        <input
          type="text"
          name="reviewer-name"
          required
          autoFocus
          maxLength={120}
          autoComplete="name"
          value={name}
          onChange={(event) => setName(event.currentTarget.value)}
        />
      </label>
      <div className="row">
        <Button type="submit" variant="primary" disabled={name.trim() === ""}>
          {initial ? "Kaydet" : "İncelemeye başla"}
        </Button>
        {onCancel ? (
          <Button variant="quiet" onClick={onCancel}>
            Vazgeç
          </Button>
        ) : null}
      </div>
    </form>
  );
}
