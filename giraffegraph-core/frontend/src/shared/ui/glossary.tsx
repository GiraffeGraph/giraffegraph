"use client";

import { useRef } from "react";

import { Button } from "@/shared/ui/button";

const WORDS: { term: string; meaning: string }[] = [
  {
    term: "İsnad",
    meaning: "Bir hadisin başında, onu kimin kimden aktardığını sırayla sayan bölüm.",
  },
  {
    term: "Ravi",
    meaning: "Hadisi bir önceki kişiden alıp bir sonrakine aktaran kişi.",
  },
  {
    term: "Zincir",
    meaning: "Bir hadisi aktaran ravilerin, onu en son aktarandan ilk kaynağa doğru sıralanışı.",
  },
  {
    term: "Rivayet lafzı",
    meaning:
      "İki ravi arasındaki aktarımı bildiren söz; örneğin “haddesenâ” (bize anlattı) ya da “an” (ondan).",
  },
  {
    term: "Öneri",
    meaning:
      "Sistemin metinden çıkardığı, henüz kesinleşmemiş bilgi: bir ravi adı ya da iki ravi arasındaki bağlantı.",
  },
  {
    term: "Alıntı",
    meaning: "Bir önerinin dayandığı, metinden harfi harfine alınmış sözler.",
  },
  {
    term: "Graf",
    meaning: "Ravilerin birer nokta, aralarındaki aktarımların birer çizgi olarak tutulduğu kayıt.",
  },
  {
    term: "Grafa yazmak",
    meaning:
      "Kabul edilen önerileri kalıcı kayda geçirmek. Yazılan bilgi bu arayüzden geri alınamaz.",
  },
];

export function Glossary() {
  const dialogRef = useRef<HTMLDialogElement>(null);

  return (
    <>
      <Button
        variant="quiet"
        size="sm"
        icon="book"
        onClick={() => dialogRef.current?.showModal()}
      >
        Bu sayfadaki kelimeler
      </Button>
      <dialog
        ref={dialogRef}
        className="dialog"
        aria-labelledby="glossary-title"
        onClick={(event) => {
          if (event.target === dialogRef.current) {
            dialogRef.current.close();
          }
        }}
      >
        <div className="dialog-inner">
          <div className="row-between">
            <h2 id="glossary-title">Bu sayfadaki kelimeler</h2>
            <Button variant="quiet" size="sm" icon="close" onClick={() => dialogRef.current?.close()}>
              Kapat
            </Button>
          </div>
          <dl className="glossary">
            {WORDS.map((word) => (
              <div key={word.term}>
                <dt>{word.term}</dt>
                <dd>{word.meaning}</dd>
              </div>
            ))}
          </dl>
        </div>
      </dialog>
    </>
  );
}
