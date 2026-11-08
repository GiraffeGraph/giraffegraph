# Ajan kuralları (wiki kanonik)

## Purpose

GiraffeGraph bitirme çalışma alanı için oturum kuralları. Her oturum başında okunur.

## İlk okuma sırası

1. `wiki/README.md` — indeks ve projenin tek paragraflık özeti
2. `wiki/architecture/workspace-map.md` — hangi klasör ne, hangisi kapsam dışı
3. `wiki/project/roadmap.md` — bugün elde olan ve sıradaki işler
4. `wiki/evaluation/correctness-measurement.md` — projenin açık ana sorusu
5. Göreve göre ilgili sayfa

## Kapsam

| Kapsam içi | Kapsam dışı |
|---|---|
| `giraffegraph-core/`, `data/` (`data/cache-and-ledger/` dahil), `landing/`, `wiki/` (`wiki/literature/`, `wiki/sources/`, `wiki/thesis/` dahil) | Aynı organizasyondaki `giraffle` ve `giraffe-code` repoları |

`giraffle` (not/planlama uygulaması) ve `giraffe-code` (çok-ajanlı kodlama aracı) aynı GitHub
organizasyonunda durur ama bitirme projesinin parçası değildir ve çalışma alanında klonları yoktur.
Çalışma alanı kökünde yalnız dört proje klasörü ve `CLAUDE.md` durur. Ayrıntı:
`architecture/workspace-map.md`.

## Değişmezler

- **Kaynak paketleri düzenlenmez.** `wiki/sources/claude-science-context/` ve
  `wiki/sources/claude-science-results/` 2026-09-30 tarihli donmuş paketlerdir; bütünlükleri
  `wiki/sources/MANIFEST.sha256` ile sınanır. Yeni bulgu wiki sayfasına ya da yeni bir sonuç klasörüne
  yazılır. Paketteki bir bulgunun güncel karşılığı: `wiki/sources/README.md`.
- **Sayı = ölçüm.** Bir script ya da birincil kaynakla üretilmemiş sayı `[UNVERIFIED]` etiketi taşır.
  Her sayı neyin, kaç veri üzerinde, hangi referansa karşı ölçüldüğünü söyler.
- **Kaynakça bellekten yazılmaz.** Künye Crossref / arXiv / ACL Anthology'den çekilir. TÜBİTAK
  formunda üç uydurma referans tespit edildi (`wiki/sources/claude-science-results/04a_kaynak_dogrulama_tablosu.md`).
- **Sanadset `<NAR>` etiketleri gümüş standarttır.** Onlara karşı ölçülen değer sistemler arası
  karşılaştırmada kullanılır; "gerçek doğruluk" diye sunulmaz.
- **TÜBİTAK 2209-A başvurusu danışman onayından geçti ve bağlayıcıdır** (başvuru 1919B012619516, TYBS
  durumu "ONAYLANDI", 2026-11-06; metin `wiki/thesis/tubitak/form.md`). H1…H4 ve Hedef 1–5 ile çelişen
  plan önerilmez; plan bunları kapsar ya da genişletir. Taahhüt başına eldeki
  kanıt: `wiki/project/tubitak-commitments.md`.
- **CSE 491 proje önerisi bağlayıcıdır.** Vize ve final ona göre değerlendirilir; son teslim günü
  2026-10-18 (`wiki/project/overview.md`, "İki çerçeve").
- **Öneri ile karar ayrıdır.** `wiki/sources/claude-science-results/` içindeki protokol ve mimari Claude Science
  önerisidir. Ekip ve danışman onayladığında `wiki/decisions/` altına ADR olarak yazılır. Karar bekleyen
  sorular ve kodun fiilen varsaydığı yanıtlar: `wiki/project/open-decisions.md`.

## Wiki disiplini

Davranış, ölçüm, plan ya da karar değiştiğinde wiki aynı görevde güncellenir. Wiki, motor ve veri tek repodadır
(`GiraffeGraph/giraffegraph`, 2026-11-09 itibarıyla public); kod ve wiki değişikliği aynı commit'te gidebilir.
Yönlendirme kuralları: `WIKI-CREATOR.md`. Kalite çıtası: `architecture/context-quality.md`.

Wiki yapısı değişirken dokunma sırası:

1. `wiki/README.md`
2. `wiki/CLAUDE.md`
3. `wiki/architecture/context-quality.md`
4. `wiki/architecture/file-structure.md`
5. `wiki/WIKI-CREATOR.md`
6. `wiki/_templates/*`

## Dil

Wiki Türkçedir; kaynak belgeler (`wiki/sources/`, `wiki/literature/`) Türkçe olduğu
için tek söz dağarcığı korunur. Tez ve makale (`wiki/thesis/`) İngilizce yazılır; Türkçe sürümleri ondan çevrilir (`wiki/thesis/turkish-edition.md`). Teknik terimler ve kod kimlikleri özgün hâliyle yazılır. Dosya adları
İngilizce `kebab-case`.

## Verification checklist

- [ ] Sayfa doğru klasörde
- [ ] Her iddia bir kaynak çapasına bağlı (çalışma alanı köküne göre yol)
- [ ] Her sayı yöntemiyle birlikte
- [ ] `Last updated` tarihi var
- [ ] Yeni sayfa `wiki/README.md` indeksine eklendi
- [ ] `wiki/sources/` altındaki paket dosyalarına dokunulmadı

## Related docs

- `wiki/README.md`
- `wiki/WIKI-CREATOR.md`
- `wiki/architecture/workspace-map.md`
- `wiki/sources/README.md`

## Last updated

2026-11-09
