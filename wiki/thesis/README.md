# Tez ve makale taslakları

## Purpose

CSE 491 bitirme raporunun (tez) ve aynı çalışmanın makale biçimli kısa sürümünün kaynağını, derleme
betiklerini ve okunacak çıktılarını tutmak. Tez ve makale İngilizce yazılır ve Türkçe sürümleri
İngilizceden çevrilir; TÜBİTAK formu yalnız Türkçedir. Bu metinler wiki sayfası değildir.

## Scope

- In: tez bölümleri, makale metni, CSE 491 proje önerisi taslağı, TÜBİTAK 2209-A formu taslağı,
  derleme betikleri, şekiller, PDF çıktıları
- Out: imzalı toplantı formları (ders klasörü, yol `wiki/architecture/workspace-map.md` içinde),
  ölçümlerin kendisi (`wiki/evaluation/`), formdaki taahhütlerin eldeki kanıtı
  (`wiki/project/tubitak-commitments.md`)

## Statü

İkisi de taslaktır (2026-10-13). Ekip üyeleri ve danışman okumadı; hiçbir yere gönderilmedi. Metin tek
kişinin yönlendirmesiyle, yapay zekâ ile yazıldı; ders yapay zekâ kullanımının raporda beyan edilmesini ister
(`wiki/project/overview.md`, "İki çerçeve"). Proje sahibi tek proje çerçevesini seçti
(`wiki/project/overview.md`, "Çerçeve"; danışman onayı bekler). Tez ve makale bu çerçeveyi taşır
(2026-10-13): tezde özet, giriş, 8. bölüm (iki destek çalışması), 9.5 ve sonuç; makalede giriş
paragrafı, 5.7 ve tartışma. Kod ajanı deneyi makalede yer almaz. İki metin de kodun özel repoda
olduğunu ve proje sonunda yayımlanacağını söyler.

| Ne | Kaynak | Okunacak çıktı |
|---|---|---|
| CSE 491 ara rapor, Grup 10, 8 Kasım 2026 teslim tarihi | `wiki/thesis/midterm/build_midterm.py`; ders şablonu `midterm/template.docx`; okunabilir metin `midterm/report.md` | `wiki/thesis/midterm/10_MidtermReport.docx` (10 sayfa, yönergeler kaldırılmış). Etiketleme ve uzman değerlendirmesi henüz başlamadı; ayrıntı `midterm/README.md` |
| Tez: "A Human-in-the-Loop Knowledge Graph Generation Engine …" | `wiki/thesis/chapters/00-front.md` … `11-appendix.md` | `wiki/thesis/build/thesis.pdf` (55 sayfa, 51 kaynak) |
| Tezin Türkçe sürümü | `wiki/thesis/chapters-tr/` (aynı dosya adları) | `wiki/thesis/build/thesis-tr.pdf` (55 sayfa) |
| CSE 491 proje önerisi (son gün 2026-10-18) | `wiki/thesis/proposal/proposal.md`; ders şablonu `wiki/thesis/proposal/template.docx` (Teams ödevinden) | `wiki/thesis/proposal/build/proposal.docx` (şablonun kendisi, doldurulmuş) ve `proposal.pdf` (6 sayfa, Pages ile dışa aktarılır); başlıklar, alt başlıklar ve tablo sütunları şablonu izler |
| Rehber: projeyi hiç bilmeyen bir okur için baştan sona anlatım (Türkçe) | `wiki/thesis/guide/rehber.md` | `wiki/thesis/guide/build/rehber.pdf` (18 sayfa) |
| Danışman toplantısı belgeleri (2026-10-16) | `wiki/thesis/meeting/2026-10-16/01-durum.md` … `04-gundem.md` | `wiki/thesis/meeting/2026-10-16/build/toplanti-belgeleri.pdf`; ekibin toplantıda doldurduğu form (imzasız): `build/supervisor-meeting-form.docx` |
| TÜBİTAK 2209-A araştırma önerisi formu (Türkçe; TYBS'ye girilen metin, başvuru 1919B012619516) | `wiki/thesis/tubitak/form.md` | `wiki/thesis/tubitak/build/form.pdf` (9 sayfa, 12 kaynak); derleme `form.docx` de üretir. Atıflar TÜBİTAK'ın yazar-yıl biçimindedir ("Öztürk vd., 2000"), kaynakça soyadına göre sıralanır ve DOI taşır (`build_form.py`); tezin IEEE kaynakçası ayrıdır. TYBS'nin kendi önizlemesi: `wiki/thesis/tubitak/tybs/arastirma-onerisi.pdf`. Sondaki "Göndermeden önce" bölümü ve baştaki durum kutusu çıktıya girmez |
| Makale: "Quoted Correctly, Extracted Differently …" | `wiki/thesis/paper/paper.md` | `wiki/thesis/paper/build/paper.pdf` (11 sayfa, 23 kaynak), `paper.tex` |
| Makalenin Türkçe sürümü: "Alıntı doğru, çıkarılan değer farklı …" | `wiki/thesis/paper/paper-tr.md` | `wiki/thesis/paper/build/paper-tr.pdf` |

## Bölüm başına dayanak

Bir bölümü değiştirecek kişi önce o bölümün dayandığı yeri açar. Tabloda olmayan bir dosya tezin
dayanağı değildir.

| Bölüm | Dayandığı wiki sayfası | Kod, veri ya da ölçüm dosyası |
|---|---|---|
| 1 Introduction, 4 Requirements | `wiki/project/overview.md`, `wiki/project/tubitak-commitments.md` | `wiki/sources/claude-science-context/02b_tubitak_commitments_and_critique.md` |
| 2 Background, 3 Related work | `wiki/evaluation/related-work.md`, `wiki/evaluation/literature-map.md` | `wiki/literature/`, iki `.bib` dosyası; 2.6 için `data/cache-and-ledger/README.md` |
| 5 Design, 6 Implementation | `wiki/domains/hadith/isnad-pipeline.md` | `giraffegraph-core/docs/`, `giraffegraph-core/backend/` |
| 7 Evaluation | `wiki/evaluation/engine-experiments.md`, `wiki/evaluation/correctness-measurement.md` | `giraffegraph-core/evaluation/results/2026-10-12-*/`, `data/eval/`, `data/README.md` |
| 8.1 Karar defteri benzetimi (makalede 5.7) | `wiki/evaluation/decision-ledger-experiments.md` | `giraffegraph-core/evaluation/identity_ledger.py`, `decision_reapplication.py`, `giraffegraph-core/evaluation/results/2026-10-13-identity-ledger/` |
| 8.2 Kod ajanı deneyi | `wiki/evaluation/wiki-for-agents-experiments.md` | `data/cache-and-ledger/data/agent-qa/` (`README.md`, `analysis.json`) |
| 9.6 "One domain" paragrafı | `wiki/evaluation/decision-ledger-experiments.md` | `data/cache-and-ledger/data/explore-copy-check-bc5cdr.py`, `copy-check-bc5cdr.json` |
| 10.1 Plan | `wiki/project/roadmap.md`, `wiki/project/open-decisions.md` | `giraffegraph-core/evaluation/annotation/` |
| Appendix | Bu sayfa | `giraffegraph-core/README.md`, `data/README.md` |

İki destek çalışmasının teze girmeyen kolları (tanık ömrü, beş ajanla fikir oturumları, not
yerleşiminin ayrıntıları) wiki sayfalarında ve `data/cache-and-ledger/MEASUREMENTS.md` içindedir.
Ripple-Down Rules atfının (`compton1990philosophical`) künyesi Crossref'ten doğrulanmıştır; kaynak
metin okunmamıştır ve tez bunu söyler.

## Derleme

Çalışma alanı kökünden değil, bu klasörden çalıştırılır:

```
cd wiki/thesis
uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build.py
uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build_paper.py
uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build_form.py
uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build.py --lang tr
uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build_paper.py --lang tr
uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build_proposal.py
cd meeting/2026-10-16 && uv run --no-project --python 3.12 --with markdown --with pypdf python build.py
cd guide && uv run --no-project --python 3.12 --with markdown python build.py
```

`build.py` bölümleri birleştirir, `[@anahtar]` atıflarını kaynakça dosyalarından numaralar, 7. bölümün
üç şeklini ölçüm dosyalarından çizer ve Markdown, Word, HTML, PDF üretir. PDF için Google Chrome
gerekir (`build.py:CHROME`); yoksa PDF adımı atlanır.

Derlemenin okuduğu, bu klasörün dışındaki dosyalar:

| Dosya | Ne için | Nerede |
|---|---|---|
| `wiki/sources/claude-science-results/04b_dogrulanmis_kaynakca.bib` | Kaynakça | Bu repo |
| `wiki/literature/extraction_eval_precedents.bib` | Emsal çalışmaların künyeleri | Bu repo |
| `giraffegraph-core/evaluation/results/2026-10-12-*/**/analysis.json` | Şekiller | `giraffegraph-core/` altında izlenmez; kopyası `data/core-backup/` altında, geri yükleme komutu `data/README.md` içinde |

Repoda yalnız PDF'ler, `paper.tex`, `proposal.docx` ve doldurulmuş toplantı formu izlenir; Word, HTML ve birleştirilmiş Markdown çıktıları
derlemeyle yeniden üretilir.

## Rules

- MUST: tezdeki her sayı bir ölçüm dosyasından gelir ve referansın adıyla (İfta platform etiketi,
  Sanadset kural etiketi) birlikte yazılır; "accuracy" kelimesi bu etiketlere karşı ölçülen değer için
  kullanılmaz. Gerekçe: iki referans da insan altın standardı değildir
  (`wiki/evaluation/engine-experiments.md`, "Rules").
- MUST: bir ölçüm ya da kod davranışı değiştiğinde ilgili bölüm ve wiki sayfası aynı görevde
  güncellenir, PDF yeniden derlenir.
- MUST: kaynakça yalnız iki `.bib` dosyasından gelir; bölüme elle künye yazılmaz. Gerekçe: TÜBİTAK
  formunda bellekten yazılmış üç referans gerçek çıkmadı.
- SHOULD: bölüm metni değişince yalnız kaynak commit edilmez, PDF de yenilenir; okuyan kişi PDF'e bakar.
- MUST: İngilizce bir bölüm ya da makale değiştiğinde Türkçe karşılığı aynı görevde güncellenir; çeviri
  `wiki/thesis/turkish-edition.md` içindeki kurallara ve terim tablosuna uyar. Gerekçe: iki sürüm
  ayrı sayılar taşırsa hangisinin doğru olduğu metinden anlaşılmaz.

## Source anchors

- `wiki/thesis/build.py` — `BIB_FILES`, `RESULTS`, `figures`, `export`
- `wiki/thesis/build_paper.py` — makale derlemesi
- `wiki/thesis/build_form.py` — TÜBİTAK formu derlemesi (`assemble`)
- `wiki/thesis/build.py` — `EDITIONS`, `edition_from_arguments`: Türkçe sürümün derlemesi
- `wiki/thesis/turkish-edition.md` — çeviri kuralları, sayı biçimi, terim tablosu
- `wiki/evaluation/engine-experiments.md` — 7. bölümdeki sayıların wiki karşılığı

## Verification checklist

- [ ] İki derleme komutu hatasız biter; çıktı "51 references" ve "23 references" der
- [ ] `wiki/thesis/build/thesis.pdf` 55 sayfa, `wiki/thesis/paper/build/paper.pdf` 11 sayfa
- [ ] 7. bölümdeki tablolar `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/compare-ifta.md` ile aynı

## Related docs

- `wiki/project/roadmap.md`
- `wiki/project/open-decisions.md`
- `wiki/evaluation/engine-experiments.md`
- `wiki/architecture/workspace-map.md`

## Last updated

2026-11-09
