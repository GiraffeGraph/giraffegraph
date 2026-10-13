# GiraffeGraph — Wiki

Bitirme projesinin yaşayan bilgi katmanı: ne yapıyoruz, neden, ne ölçüldü, ne açık.
Kod ve ölçüm dosyaları nihai otoritedir; wiki *neden* ve *nasıl ilerlenir* sorularını taşır.

Bu klasör proje reposunun (`GiraffeGraph/giraffegraph`, özel) `wiki/` klasörüdür; motor
(`giraffegraph-core/`) ve veri (`data/`) aynı repodadır. Projenin kod dışındaki bütün bağlamı buradadır: yaşayan sayfalar, literatür taraması,
tarihli kaynak paketleri, tez ve makale taslakları.

**Proje:** *A Human-in-the-Loop Knowledge Graph Generation Engine for Preventing Hallucination and
Schema Drift in LLMs: An Application on Hadith Isnad Chains.* LLM destekli, insan onaylı bir bilgi
grafı üretim motoru (GiraffeGraph Core); ilk vaka hadis isnad zincirleri, üzerine RAG tabanlı
soru-cevap katmanı. Projenin tek iddiası ve onu taşıyan üç parça: `project/overview.md`, "Çerçeve".

**Açık ana soru:** işlediğimiz verinin ve ürettiğimiz çıktının doğru olduğunu nasıl ölçeriz?
→ `evaluation/correctness-measurement.md`

**Yığın (Core):** Python 3.12 · FastAPI · Postgres 16 · Neo4j 5 · Next.js 15 iç panel.

## Where to start

1. `CLAUDE.md` — ajan kuralları, kapsam, değişmezler
2. `architecture/workspace-map.md` — klasör klasör çalışma alanı; hangisi projeyle ilgili, hangi repo nerede
3. `project/roadmap.md` — bugün elde olan ve sıradaki işler, bağımlılık sırasıyla

Proje:

- `project/overview.md` — ekip, danışman, iki çerçeve (CSE 491 + TÜBİTAK 2209-A), araştırma sorusu
- `project/tubitak-commitments.md` — K-1…K-5 ve H1…H4: taahhüt başına eldeki kanıt, eksik, önerilen revizyon, formdaki kaynakça hataları
- `project/open-decisions.md` — ekibin ve danışmanın vermesi gereken kararlar: öneri, fiilî durum, sahip
- `project/supervisor-meetings.md` — danışman toplantıları ve aksiyonlar

Ölçüm:

- `evaluation/correctness-measurement.md` — doğruluk ölçümü: katmanlar, metrikler, ölçülen/ölçülmeyen
- `evaluation/engine-experiments.md` — motor deneyleri: 300 hadiste LLM koşulları, değer-alıntı kapısı, maliyet, kimlik taban çizgisi
- `evaluation/decision-ledger-experiments.md` — karar defteri keşif deneyleri: bir ravi kararı kaç kez yeniden kullanılır, kapsamı çelişkiden türetmek, kopya kontrolünün hadis dışında tutmaması
- `evaluation/wiki-for-agents-experiments.md` — LLM'in tuttuğu wiki ajana ne kazandırır: karar defteri, taze ve bayat belge, tanık notu, araç bütçesi; belge atıflarının git geçmişindeki ömrü; ağaç içi notlar ve arama sonucunun sırası
- `evaluation/related-work.md` — emsal çalışmalar çıkarım doğruluğunu nasıl ölçmüş, nerede eksik
- `evaluation/literature-map.md` — 38 makalelik taramanın ölçüm katmanlarına eşlenmesi ve boşluk

Alan ve motor:

- `domains/hadith/isnad-pipeline.md` — Core isnadı nasıl işliyor: bölütleme, kapılar, inceleme ve red kodları, sınırlar

## Wiki'nin kendisi

- `architecture/file-structure.md` — wiki yerleşimi
- `architecture/context-quality.md` — bir sayfanın yerini hak etme ölçütü
- `WIKI-CREATOR.md` — sayfa yazma/güncelleme protokolü
- `_templates/` — `PAGE.md`, `ADR.md`

## Kaynak ve literatür (wiki içinde)

Yaşayan sayfalar bunları tekrar etmez; bağlar.

| Yol | Ne |
|---|---|
| `sources/README.md` | Tarihli kaynak paketlerinin rehberi: ne, ne zaman, kim; paketteki hangi bulgunun güncel karşılığı hangi sayfada |
| `sources/claude-science-context/` | 2026-09-30 bağlam paketi (donmuş): TÜBİTAK formu, site metni, kod denetimi, alan özeti, açık sorular |
| `sources/claude-science-results/` | 2026-09-30 Claude Science çıktısı (donmuş): protokol, pilot, kaynakça, iş planı |
| `sources/olcum-nasil-yapilir.html` | Doğruluk ölçümünün teknik terimsiz, on dakikalık anlatımı |
| `literature/` | Literatür taraması (yaşayan): 38 makalenin review'ları ve iki `.bib` dosyası; haritası `evaluation/literature-map.md` |
| `thesis/` | Tez ve makale taslakları (İngilizce): bölümler, derleme betikleri, PDF çıktıları; statü ve derleme `thesis/README.md` |

Paketlerde en sık açılan belgeler:

| Belge | Ne için açılır |
|---|---|
| `wiki/sources/claude-science-results/01_yonetici_ozeti.md` | 2026-09-30 analizinin bir sayfalık özeti |
| `wiki/sources/claude-science-results/03_revize_deney_protokolu.md` | Önerilen deney protokolü, metrik tanımları, istatistik |
| `wiki/sources/claude-science-results/08_pilot_raporu.md` | 50 hadislik pilotun tüm sayıları |
| `wiki/sources/claude-science-results/05_kod_degisiklik_listesi.md` | Core için öncelikli değişiklikler C1–C14 |
| `wiki/sources/claude-science-results/06_6_aylik_is_plani.md` | İş paketleri, MVS / ideal ayrımı, riskler |
| `wiki/sources/claude-science-results/07_acik_sorulara_oneriler.md` | 16 açık karar için öneri |
| `wiki/sources/claude-science-context/02b_tubitak_commitments_and_critique.md` | Bağlayıcı taahhütler K-1…K-5, H1…H4 |
| `wiki/sources/claude-science-context/08_hadith_domain_primer.md` | İsnad, rical, tabaka, muâsara: mühendis için özet |

## Wiki dışındaki birincil belgeler

| Belge | Ne için açılır |
|---|---|
| `giraffegraph-core/docs/` | Core mimarisi ve ADR'ler |
| `giraffegraph-core/evaluation/results/` | Ölçüm koşularının ham çıktıları (koşu raporu, analiz, karşılaştırma tabloları) |
| `data/README.md` | İndirilen dış etiketli veri, lisans beyanları, değerlendirme kümelerinin kuruluşu |

## Naming rules

- Dosya adları `kebab-case.md`, İngilizce
- Dosya başına tek konu; bölmek bağlamı zayıflatıyorsa birleştir
- Yol çapaları çalışma alanı köküne göredir (`giraffegraph-core/backend/...`); bu repodaki bir dosya
  `wiki/` önekiyle yazılır (`wiki/evaluation/related-work.md`)

## Quality bar (every doc)

1. Purpose
2. Scope / sınır
3. Source anchors
4. Rules ve gerekçesi
5. Verification checklist
6. Related docs
7. Last updated (`YYYY-MM-DD`)

Tam ölçüt: `architecture/context-quality.md`.

## Last updated

2026-10-13
