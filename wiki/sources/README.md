# Kaynak paketleri (donmuş)

## Purpose

Wiki sayfalarının çapa verdiği tarihli kaynak paketlerini tek yerde tutmak ve her birinin ne zaman,
kim tarafından, neye dayanarak üretildiğini söylemek. Bu klasördeki dosyalar belirli bir günün
fotoğrafıdır; projenin güncel durumu wiki sayfalarındadır.

## Scope

- In: paketlerin kimliği, bütünlük kontrolü, paketteki hangi bulgunun hangi wiki sayfasında güncel
  karşılığının durduğu
- Out: paketlerin içeriğinin özeti (her paketin kendi giriş dosyası vardır), yaşayan literatür
  dosyaları (`wiki/literature/`)

## Paketler

| Yol | Ne | Tarih | Üreten | Giriş dosyası |
|---|---|---|---|---|
| `wiki/sources/claude-science-context/` | Claude Science çalışmasına girdi olarak hazırlanan bağlam paketi: TÜBİTAK formu (PDF ve özet), site metni, Core mimarisi ve kod bundle'ı, iddia ↔ kod denetimi, hadis alan özeti, sentez hipotezi, 16 açık soru | 2026-09-30 | Claude Code; repoları, canlı siteyi ve formu okuyarak | `00_README_START_HERE.md` |
| `wiki/sources/claude-science-results/` | Aynı çalışmanın çıktısı: tasarım uzayı, revize deney protokolü, kaynak doğrulama ve doğrulanmış kaynakça, kod değişiklik listesi C1–C14, altı aylık iş planı, açık sorulara öneriler, 50 hadislik pilotun kodu, verisi ve raporu, yayın planı, oturum dökümü | 2026-09-30 | Claude Science | `01_yonetici_ozeti.md` |
| `wiki/sources/olcum-nasil-yapilir.html` | "Doğruluğu nasıl ölçeceğiz?": doğruluk ölçümünü teknik terim kullanmadan anlatan, on dakikalık okuma belgesi; danışman toplantısı için hazırlandı, sonunda danışmana sorulacak üç soru var. Ayrıntılı ve kaynaklı hâli `wiki/evaluation/correctness-measurement.md` | 2026-10-08 | Claude Code | kendisi |

İki pakette dosya numaraları birbirinden bağımsızdır: `claude-science-context/05_…` iddia ↔ kod
denetimidir, `claude-science-results/05_…` kod değişiklik listesidir. Paket içi metinler birbirine
yalnız numarayla atıf yapar (`02b`, `05`, `12`); sonuç paketindeki numarasız bir atıf çoğunlukla bağlam
paketini gösterir. Wiki'den atıf yaparken klasör adı yazılır.

`claude-science-context/06a_…` ve `06b_…`, "The Cache and the Ledger" denemesinin ve taslağının
2026-09-30 kopyasını taşır. O çalışmanın yaşayan hâli çalışma alanındaki `cache-and-ledger/` klasörüdür
ve bu repoya dahil değildir.

`claude-science-context/09_literature/`, `wiki/literature/` altındaki dosyaların 2026-09-30 kopyasıdır.
Literatürün güncel hâli `wiki/literature/` klasörüdür.

## Paketteki bulgu ↔ güncel karşılığı

Paketler 2026-09-30 durumunu anlatır: Core'un `main` dalı o gün iki commit'ti ve ölçüm 50 hadislik
pilottan ibaretti. Aşağıdaki konularda güncel durum wiki sayfasındadır; paket ile wiki çelişirse wiki
ve çapa verdiği ölçüm dosyası esas alınır.

| Paketteki konu | Paketin söylediği (2026-09-30) | Güncel karşılığı |
|---|---|---|
| Core'un davranışı (`claude-science-context/04a`, `05`, `14`) | Alıntı ve değer kontrolü yok; tanımsız tip tüm çıktıyı düşürür; ilişki anahtarı `(a, tip, b)`; karar kaydında inceleyici ve süre yok | `wiki/domains/hadith/isnad-pipeline.md`; hangi değişikliğin kodda durduğu `wiki/architecture/workspace-map.md`, "Bilinen durum notları" |
| Kod değişiklik listesi C1–C14 (`claude-science-results/05`) | Hepsi yapılacak iş | Aynı yer: C1, C2, C4, C5, C7, C8 kodda; C3, C10, C11, C12 kısmen; C6, C9, C13, C14 yok |
| Mention çıkarımı sayıları (`claude-science-results/08`, `pilot_*.json`) | 50 hadis, Sanadset kural etiketi, tek model | 300 hadis, İfta platform etiketi, dört koşul: `wiki/evaluation/engine-experiments.md` |
| "Deterministik ayrıştırıcı ≈ LLM" | ΔF1 −0,017, aralık sıfırı kapsar (50 hadis) | 300 hadiste kural tabanlı koşul şema-only LLM'den gevşek eşleşmede yüksek (+0,032 [0,006 – 0,060]), katı eşleşmede düşük (0,633'e 0,826): aynı sayfa |
| "LLM zincir başına çağrılsın" | Uzun zincirlerde recall düşüşü ve kesilen çağrılar (50 hadis) | 300 hadiste tüm hadis ile zincir başına arasındaki fark +0,008, aralık sıfırı içerir; bölütleme 300 hadisin 10'unu böldü: aynı sayfa |
| Değer-alıntı kontrolü | 32 / 318 aday (%10,1), motor dışında hesaplandı | Motor içinde kapı olarak ölçüldü, 155 / 1.688 mention: aynı sayfa, "Değer-alıntı kapısı" |
| Sanadset lisansı | "CC0, teyit edildi" | Hugging Face kartı `cc0-1.0`, özgün Mendeley Data kaydı "CC BY 4.0"; iki beyan çelişiyor: `data/README.md` |
| Ravi otorite listesi adayları (`claude-science-results/07` soru 5) | Hawramani ve `muslimscholars.info` | İndirilmiş ve kullanılan adaylar İfta ravi profilleri ile AR-Sanad ravi tablosudur: `wiki/evaluation/related-work.md`, "Hazır referans veri adayları" |
| Emsal çalışmalar (`claude-science-context/10`, `claude-science-results/09`) | Bir kısmı "doğrula" etiketli | Birincil kaynaktan okunan emsaller: `wiki/evaluation/related-work.md` |
| TÜBİTAK taahhütleri ve hipotezler | Taahhüt tablosu, eleştiri, dört revizyon önerisi | Taahhüt başına eldeki kanıt: `wiki/project/tubitak-commitments.md` |
| 16 açık soru ve öneriler (`claude-science-context/13`, `claude-science-results/07`) | Soru ve öneri | Soru başına fiilî durum ve karar statüsü: `wiki/project/open-decisions.md` |
| İş planı (`claude-science-results/06`) | İP0 ve F1–F4 | Sıradaki işler ve bağımlılıkları: `wiki/project/roadmap.md` |

Güncel karşılığı olmayan ve pakette hâlâ tek kaynak olan içerik: tasarım uzayı ve mimari tartışması
(`claude-science-results/02`), istatistik planı ve güç analizi (`claude-science-results/03` §4), ezber
kontrolü testleri (aynı belge §7), form kaynakçasının satır satır doğrulaması
(`claude-science-results/04a`, `04b`), yayın planı (`claude-science-results/09`), hadis alan özeti
(`claude-science-context/08`), sentez hipotezi (`claude-science-context/12`), Kur'an ve kod tabanı
vakaları (`claude-science-context/07`).

## Bütünlük

`wiki/sources/MANIFEST.sha256`, bu klasördeki 43 dosyanın sha256 değerini taşır: bağlam paketi 22, sonuç
paketi 20, okuma belgesi 1 (2026-10-13). Paketler
çalışma alanı kökünden bu klasöre taşınırken her dosya taşıma öncesi değeriyle karşılaştırıldı; içerik
değişmedi. Taşıma sırasında silinen iki şey paket içeriği değildir: `claude-science-results/__pycache__/`
ve `claude-science-context/.DS_Store`.

```
cd wiki/sources && shasum -a 256 -c MANIFEST.sha256
```

## Rules

- MUST: bu klasördeki dosyalar düzenlenmez. Gerekçe: wiki sayfaları, Core testleri
  (`giraffegraph-core/evaluation/tests/conftest.py`, `backend/tests/unit/test_hadith_segmenter.py`) ve tez
  derleme betiği bu dosyaların belirli içeriğine dayanır; pilot sayıları `pilot_sample.json` ve
  `pilot_isnad.py` ile yeniden üretilir.
- MUST: yeni bulgu wiki sayfasına ya da `giraffegraph-core/evaluation/results/` altında yeni bir sonuç
  klasörüne yazılır; pakete eklenmez.
- MUST: paketteki bir sayı aktarılırken tarihi ve örneklemi yazılır (2026-09-30, 50 hadis, Sanadset
  kural etiketi). Gerekçe: aynı metrik 300 hadiste ve başka bir referansa karşı da ölçüldü; iki sayı
  karıştırılırsa yanlış kıyas çıkar.
- MUST: paketteki protokol ve mimari öneridir. Ekip ve danışman onayladığında `wiki/decisions/` altına
  ADR olarak yazılır.
- SHOULD: yeni bir tarihli paket eklenirse kendi klasörüyle bu klasöre konur, tabloya satır eklenir ve
  `MANIFEST.sha256` yeniden üretilir.

## Source anchors

- `wiki/sources/MANIFEST.sha256` — 43 dosyanın sha256 değeri (22 + 20 + 1)
- `wiki/sources/claude-science-context/00_README_START_HERE.md` — bağlam paketinin dosya haritası ve tarihi
- `wiki/sources/claude-science-results/01_yonetici_ozeti.md` — sonuç paketinin özeti ve dosya listesi
- `data/README.md` — Sanadset lisans beyanlarının kaydı

## Verification checklist

- [ ] `cd wiki/sources && shasum -a 256 -c MANIFEST.sha256` çıktısında her satır `OK`
- [ ] "Güncel karşılığı" sütunundaki her sayfa var ve ilgili konuyu taşıyor
- [ ] `git -C wiki log -- sources/claude-science-context sources/claude-science-results` ilk commit dışında değişiklik göstermiyor

## Related docs

- `wiki/README.md`
- `wiki/architecture/workspace-map.md`
- `wiki/project/tubitak-commitments.md`
- `wiki/project/open-decisions.md`

## Last updated

2026-10-13
