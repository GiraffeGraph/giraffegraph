# 03 — giraffegraph.com: kamuya verilen sözler

Kaynak: `GiraffeGraph/web` reposu (`src/components/landing/*.tsx`). Canlı site 2026-09-30'da WebFetch ile kontrol edildi ve içerik repo ile birebir aynı. Next.js statik export, GitHub Pages (CNAME), sigma.js/graphology ile görsel mockup. Son commit'ler (2026-09-18): *"reposition as open-source HITL KG engine with isnad case study"*, SEO, dead-code temizliği.

## Metadata
- **Title:** GiraffeGraph — Open-Source Human-in-the-Loop Knowledge Graph Engine
- **Description:** "An open-source engine where LLMs propose knowledge graph facts and humans verify them — preventing hallucination and schema drift. First case study: hadith isnad chains."
- **Keywords:** knowledge graph, human-in-the-loop, LLM hallucination, schema drift, hadith isnad, entity resolution, open source

## Hero
- Rozet: "✦ Open Source · In Development"
- Başlık: **"LLMs Propose. Humans Verify."**
- Alt metin: "GiraffeGraph is an open-source knowledge graph engine that keeps a human in the loop — so LLM extraction stays grounded in the source and the schema stays what you designed. **No hallucinated facts. No schema drift.**"
- "First case study: hadith isnad chains · Paper in preparation"
- Mockup (concept preview): Schema Studio "v1 locked". Node tipleri: Narrator, Hadith, Collection, Source Span. İlişkiler: `NARRATED_FROM` (Narrator→Narrator), `TRANSMITS` (Narrator→Hadith), `RECORDED_IN` (Hadith→Collection)

## Problem / Çözüm
**The Challenge — "LLMs are fluent. That doesn't make them faithful."**
- Hallucination: plausible narrators and links that no source contains
- Schema drift: ad-hoc types like HEARD_FROM, TOLD and narratedBy pile up across runs
- Name variants silently merged — or the same person split in two
- No trace of which sentence a fact came from, or who approved it

**The Solution — "Every fact is grounded and approved."**
- Each extracted triple is tied to the source span it came from
- The schema is locked — new types are proposals, never silent additions
- Entity merges are suggested by the model and decided by a human
- Every change is versioned, so the graph stays auditable

## How it works (6 adım)
1. **Schema Design:** Define node/relation types and properties. *AI can suggest a schema from your first few documents.*
2. **Ingest Sources:** Each source is split into citable units.
3. **AI Extraction:** Proposes entities and relations, constrained to your schema and linked to the exact source span.
4. **Review & Validate:** "**Nothing enters the graph unapproved.** You accept, reject, edit or merge — ungrounded claims are flagged."
5. **Graph Grows:** Each approved batch lands as a versioned delta — never an overwrite.
6. **Explore & Query:** Walk chains visually, trace any fact back to its source **and its reviewer**.

## Features
- **Schema Studio (Drift Guard):** "when the model wants a type that doesn't exist, it becomes a **proposal** you approve or reject"
- **AI Extraction Engine:** every triple carries the source span
- **Human-in-the-Loop Review:** "Ungrounded claims are flagged, name variants are resolved by a human." Örnek kuyruk: ✓ "al-Ḥumaydī NARRATED_FROM Sufyān", ✕ "ʿUmar NARRATED_FROM Abū Hurayra — no source span", ? "'Ibn ʿUyayna' = 'Sufyān b. ʿUyayna'?" [Merge]
- **Iterative Graph Growth:** never overwrites
- **Full Versioning:** "Schema versions, extraction runs, graph deltas — every change is tracked, auditable and **reversible**."
- **Any Domain:** Hadith, History, Legal, Research, Medical, Story

## Case study: Hadith Isnad Chains
Örnek: Ṣaḥīḥ al-Bukhārī #1 ("Actions are judged by intentions"), `NARRATED_FROM ↓`:
al-Bukhārī (collector) → al-Ḥumaydī (ʿAbd Allāh b. al-Zubayr) → Sufyān b. ʿUyayna (also written "Ibn ʿUyayna") → Yaḥyā b. Saʿīd al-Anṣārī (pivot of the chain) → Muḥammad b. Ibrāhīm al-Taymī → ʿAlqama b. Waqqāṣ al-Laythī → ʿUmar b. al-Khaṭṭāb (companion) → The Prophet ﷺ

Neden isnad?
- **Ground truth exists:** classical rijāl literature documents who narrated from whom
- **Zero tolerance for errors:** one invented or misplaced narrator changes how a hadith is graded
- **Names vary everywhere:** kunya, nisba, laqab. ER needs a human expert in the loop

> Not: Site Arapça transliterasyon kullanıyor (ISO/ALA-LC tarzı: Ḥ, ʿ, ā). TÜBİTAK formu ise **Türkçe** meal ve Türkçe transliterasyonu ("Ebû Hureyre") hedefliyor. Hangi dilde çalışılacağı açık bir karar (`13`).

## Research ("Built Alongside a Paper", In preparation)
Başlık: *A Human-in-the-Loop Knowledge Graph Generation Engine for Preventing Hallucination and Schema Drift in LLMs: An Application on Hadith Isnad Chains*
Makalenin cevaplayacağı sorular:
1. How much does **source-span grounding plus human review** reduce hallucinated triples?
2. Does a **locked schema with a proposal gate** keep the graph consistent across extraction runs?
3. **How much expert effort does the review loop cost per verified chain?**

"The preprint and the code will be linked here once they are published."

## Contributors
Yahya Efe Kuruçay (@efekurucay), Alperen Ulukaya (@ulukayalperen7), Deniz Büyükşahin (@Dnzbykshn), Taha Yiğit Alkan (@tahayigitalkan, Academic Supervisor).
> Tutarsızlık: TÜBİTAK formunda İbrahim Çakır var, sitede yok. Sitede Alperen Ulukaya var, formda yok.

## FAQ (birebir özet)
- Open source? "Yes… will be published on GitHub under an open-source license. No paid plans."
- **Can I use it today? "Not yet. The engine and the paper are both in development."**
- Hallucination nedir? "An extracted fact that the source text does not support… GiraffeGraph ties every proposed triple to its source span and keeps it out of the graph until a human approves it."
- Schema drift nedir? "HEARD_FROM in one batch, TOLD or narratedBy in the next… GiraffeGraph locks the schema and turns every new type into a proposal instead."
- Replace scholars? "No. The model only proposes; the expert decides."

## Sitenin form ve kodla gerilimi (özet; detay `05`)
- Site "Can I use it today? Not yet" diyor. Form "uçtan uca çalışır, açık kaynak yayımlanmış" diyor. GitHub'da `giraffegraph-core` public (HTTP 200) ama **LICENSE dosyası yok** ve 2 commit var (son: 2026-04-05).
- Site "Nothing enters the graph unapproved" diyor. Kodda yüksek güvenli ve geçerli adaylar **insan görmeden** commit ediliyor.
- Site "proposal gate" diyor. Kodda tanımsız tip gelince **tüm çıkarım çıktısı reddediliyor**, öneri mekanizması yok.
- Site "ungrounded claims are flagged" diyor. Kodda alıntının segmentte geçip geçmediği **kontrol edilmiyor**.
- Site "reversible", "trace to reviewer" diyor. Kodda geri alma yok, reviewer kimliği tutulmuyor.
