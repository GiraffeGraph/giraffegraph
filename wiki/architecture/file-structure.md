# Wiki dosya yapısı

## Purpose

Wiki sayfalarının nereye konacağını, bağlam kalitesini bozmadan tanımlamak.

## Scope

- In: klasör yerleşimi, yönlendirme kuralları
- Out: sayfaların içeriği

## Rules

- MUST: bilgi konuya göre düzenlenir (`project`, `evaluation`, `domains`, `decisions`).
- MUST: yaşayan sayfa ile tarihli kaynak ayrı durur. `sources/` altındaki paketler düzenlenmez;
  `literature/` yaşayan tarama dosyalarıdır. Gerekçe: bir sayfanın güncel durumu mu, bir günün
  fotoğrafını mı anlattığı yolundan okunur.
- MUST: çalışma alanı genelindeki olgu ve kurallar `architecture/` altında durur.
- MUST: ekipçe verilmiş her önemli karar bir ADR dosyasıdır.
- MUST NOT: yer tutucu sayfa ya da boş klasör.
- SHOULD: dosya başına tek konu.
- SHOULD: bir repoya ait çalıştırma komutları o reponun README'sinde kalır; wiki bağlar.

## Canonical tree

Her dosya adıyla listelenir; küme küçüktür ve eksiksiz tutulur.

Yaşayan sayfalar adıyla listelenir. `sources/` altındaki paket dosyaları ile `thesis/` altındaki
bölümler tek tek listelenmez; `sources/` için tam liste `sources/MANIFEST.sha256` dosyasıdır.

```txt
CLAUDE.md                     # çalışma alanı kökü (repo dışı): wiki/CLAUDE.md dosyasını içe aktarır
wiki/                         # repo: GiraffeGraph/giraffegraph-wiki
  README.md                   # indeks + nereden başlanır
  CLAUDE.md                   # ajan kuralları, kapsam, değişmezler
  WIKI-CREATOR.md             # sayfa yazma protokolü
  .gitignore
  _templates/
    PAGE.md  ADR.md

  architecture/
    workspace-map.md          # klasör haritası, proje ilgisi, kapsam dışı repolar
    context-quality.md        # kalite çıtası
    file-structure.md         # bu dosya

  project/
    overview.md               # kimlik, ekip, iki çerçeve, araştırma sorusu
    roadmap.md                # bugün elde olan, sıradaki işler ve bağımlılıkları (öneri)
    tubitak-commitments.md    # taahhüt ve hipotez başına eldeki kanıt, eksik, önerilen revizyon
    open-decisions.md         # karar bekleyen sorular: öneri, fiilî durum, sahip
    supervisor-meetings.md    # CSE 491 danışman toplantıları ve aksiyonlar

  evaluation/
    correctness-measurement.md  # doğruluk katmanları, metrikler, ölçülen / ölçülmeyen
    engine-experiments.md       # motor deneyleri: koşullar, 300 hadislik İfta kümesi, kapı yakalama, maliyet, kimlik taban çizgisi
    literature-map.md           # 38 makalenin katmanlara eşlenmesi, boşluk
    related-work.md             # emsal çalışmaların ölçüm yöntemi, sayıları, projeye çıkarım

  decisions/                  # ilk ADR ile oluşur: INDEX.md + ADR-NNN-<slug>.md
  domains/
    hadith/
      isnad-pipeline.md       # bölütleme, grounding kapıları, inceleme ve red kodları, doğrulama durumu, bilinen sınırlar

  literature/                 # yaşayan literatür taraması
    efe_llm_eval_metrics_review.md                  # 38 makalenin listesi ve arXiv kimlikleri
    efe_reviews.md  efe_reviews_full.md             # makale başına NotebookLM review'ları (kısa ve tam)
    efe_literature_review_section.md                # APA 7 literatür bölümü taslağı
    llm_eval_metrics.bib                            # taramanın künyeleri
    extraction_eval_precedents.bib                  # emsal çalışmaların künyeleri

  thesis/                     # tez ve makale taslakları (İngilizce)
    README.md                 # statü, derleme komutu, derlemenin dayandığı dosyalar
    build.py  build_paper.py  # derleme betikleri
    chapters/                 # 00-front.md … 10-appendix.md
    figures/                  # build.py'nin ölçüm dosyalarından çizdiği şekiller
    build/thesis.pdf          # tezin okunacak çıktısı
    paper/paper.md            # makale metni
    paper/build/              # paper.pdf, paper.tex

  sources/                    # tarihli kaynak paketleri (donmuş)
    README.md                 # paket rehberi; paketteki bulgu ↔ güncel karşılığı
    MANIFEST.sha256           # paket dosyalarının sha256 değerleri
    claude-science-context/   # 2026-09-30 bağlam paketi
    claude-science-results/   # 2026-09-30 Claude Science çıktısı, pilot kodu ve verisi
    olcum-nasil-yapilir.html  # doğruluk ölçümünün sade anlatımı (2026-10-08)
```

## Yönlendirme

| Yazılacak şey | Yer |
|---|---|
| Yeni ölçüm, metrik kararı, altın standart protokolü | `evaluation/` |
| Ekip, takvim, taahhüt, toplantı | `project/` |
| Bir taahhüdün durumu değişti | `project/tubitak-commitments.md` |
| Yeni bir açık soru çıktı ya da bir soru karara bağlandı | `project/open-decisions.md`; karar `decisions/` |
| Bir iş bitti ya da sıra değişti | `project/roadmap.md` |
| Yeni makale review'u ya da künye | `literature/`; katmana eşlemesi `evaluation/literature-map.md` |
| Tez ya da makale metni | `thesis/chapters/`, `thesis/paper/paper.md`; ardından yeniden derleme |
| Dışarıdan gelen tarihli paket (analiz çıktısı, bağlam dökümü) | `sources/<paket-adı>/`; `sources/README.md` tablosuna satır |
| Hadis şeması, ER, isnad kuralları gibi alan davranışı | `domains/hadith/` |
| Core'un mimarisi | `giraffegraph-core/docs/` (wiki yalnız bağlar) |
| Onaylanmış karar ve tartılmış alternatifleri | `decisions/ADR-NNN-<slug>.md` |
| Klasör eklendi, repo taşındı, kapsam değişti | `architecture/workspace-map.md` |

## Verification checklist

- [ ] `git -C wiki ls-files | grep -v '^sources/claude-science\|^thesis/chapters/'` çıktısı ağaçla eşleşiyor
- [ ] `cd wiki/sources && shasum -a 256 -c MANIFEST.sha256` her satırda `OK`
- [ ] Yeni sayfa ağaca ve `wiki/README.md` indeksine eklendi
- [ ] Boş klasör yok

## Related docs

- `wiki/architecture/context-quality.md`
- `wiki/WIKI-CREATOR.md`
- `wiki/README.md`
- `wiki/sources/README.md`

## Last updated

2026-10-13
