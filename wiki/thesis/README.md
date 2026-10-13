# Tez ve makale taslakları

## Purpose

CSE 491 bitirme raporunun (tez) ve aynı çalışmanın makale biçimli kısa sürümünün kaynağını, derleme
betiklerini ve okunacak çıktılarını tutmak. Metinler İngilizcedir; wiki sayfası değildir.

## Scope

- In: tez bölümleri, makale metni, derleme betikleri, şekiller, PDF çıktıları
- Out: proje önerisi ve imzalı toplantı formları (ders reposu, yol
  `wiki/architecture/workspace-map.md` içinde), ölçümlerin kendisi (`wiki/evaluation/`)

## Statü

İkisi de taslaktır (2026-10-13). Ekip üyeleri ve danışman okumadı; hiçbir yere gönderilmedi. Metin tek
kişinin yönlendirmesiyle, yapay zekâ ile yazıldı; ders yapay zekâ kullanımının raporda beyan edilmesini ister
(`wiki/project/overview.md`, "İki çerçeve"). Tezin ana iddiası karara bağlanmadı
(`wiki/project/open-decisions.md`, soru 2); taslak dar çerçeveyi taşır.

| Ne | Kaynak | Okunacak çıktı |
|---|---|---|
| Tez: "A Human-in-the-Loop Knowledge Graph Generation Engine …" | `wiki/thesis/chapters/00-front.md` … `10-appendix.md` | `wiki/thesis/build/thesis.pdf` (48 sayfa, 38 kaynak) |
| Makale: "Quoted Correctly, Extracted Differently …" | `wiki/thesis/paper/paper.md` | `wiki/thesis/paper/build/paper.pdf` (9 sayfa, 18 kaynak), `paper.tex` |

## Derleme

Çalışma alanı kökünden değil, bu klasörden çalıştırılır:

```
cd wiki/thesis
uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build.py
uv run --no-project --python 3.12 --with matplotlib --with pypandoc-binary python build_paper.py
```

`build.py` bölümleri birleştirir, `[@anahtar]` atıflarını kaynakça dosyalarından numaralar, 7. bölümün
üç şeklini ölçüm dosyalarından çizer ve Markdown, Word, HTML, PDF üretir. PDF için Google Chrome
gerekir (`build.py:CHROME`); yoksa PDF adımı atlanır.

Derlemenin okuduğu, bu klasörün dışındaki dosyalar:

| Dosya | Ne için | Nerede |
|---|---|---|
| `wiki/sources/claude-science-results/04b_dogrulanmis_kaynakca.bib` | Kaynakça | Bu repo |
| `wiki/literature/extraction_eval_precedents.bib` | Emsal çalışmaların künyeleri | Bu repo |
| `giraffegraph-core/evaluation/results/2026-10-12-*/**/analysis.json` | Şekiller | Core reposunda izlenmez; kopyası `data/core-backup/` altında, geri yükleme komutu `data/README.md` içinde |

Repoda yalnız PDF'ler ve `paper.tex` izlenir; Word, HTML ve birleştirilmiş Markdown çıktıları
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

## Source anchors

- `wiki/thesis/build.py` — `BIB_FILES`, `RESULTS`, `figures`, `export`
- `wiki/thesis/build_paper.py` — makale derlemesi
- `wiki/evaluation/engine-experiments.md` — 7. bölümdeki sayıların wiki karşılığı

## Verification checklist

- [ ] İki derleme komutu hatasız biter; çıktı "38 references" ve "18 references" der
- [ ] `wiki/thesis/build/thesis.pdf` 48 sayfa, `wiki/thesis/paper/build/paper.pdf` 9 sayfa
- [ ] 7. bölümdeki tablolar `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/compare-ifta.md` ile aynı

## Related docs

- `wiki/project/roadmap.md`
- `wiki/project/open-decisions.md`
- `wiki/evaluation/engine-experiments.md`
- `wiki/architecture/workspace-map.md`

## Last updated

2026-10-13
