# Durum ve sıradaki işler

## Purpose

Projenin bugün nerede durduğunu ve bundan sonra hangi işin hangisini beklediğini tek sayfada vermek.
Yeni bir oturumun ya da ekibe yeni katılan birinin "şimdi ne yapılır" sorusuna cevabıdır.

## Scope

- In: çalışan ve ölçülmüş olanın özeti, açık işler, işler arası bağımlılık, her işin hangi taahhüdü
  karşıladığı
- Out: takvim ve notlandırma (`wiki/project/overview.md`, `wiki/project/supervisor-meetings.md`), ölçüm
  ayrıntısı (`wiki/evaluation/`), altı aylık iş paketleri
  (`wiki/sources/claude-science-results/06_6_aylik_is_plani.md`)

## Bugün elde olan (2026-10-13)

| Ne | Durum | Nerede |
|---|---|---|
| Çalışan motor | Hadis metni yüklenir, isnad bölütlenir, kural tabanlı ya da LLM sağlayıcısı aday üretir, kapılar adayı kabul eder ya da incelemeye yollar, onaylanan tek işlemde grafa yazılır. Testler: 273 geçer, 12'si gerçek veritabanı ister | `giraffegraph-core/`, `wiki/domains/hadith/isnad-pipeline.md` |
| Panel | Yükle, çıkar, incele, oku akışı; Türkçe arayüz | `giraffegraph-core/frontend/` |
| Ölçüm kiti | Motordan bağımsız puanlayıcı (M1 / M2, eşli bootstrap), koşu karşılaştırma ve kimlik taban çizgisi betikleri | `giraffegraph-core/evaluation/` |
| Ölçüm | 300 hadiste dört koşul, İfta platform etiketine karşı; değer-alıntı kapısının yakalama gücü; güven skorunun ayırma gücü; ad yazımıyla kimliğin taban çizgisi | `wiki/evaluation/engine-experiments.md` |
| Veri | Üç dış etiketli veri ailesi indirildi, üç değerlendirme kümesi kuruldu | `data/README.md` |
| Emsal taraması | Emsal çalışmaların ölçüm yöntemi birincil kaynaktan okundu; 38 makalelik metrik taraması | `wiki/evaluation/related-work.md`, `wiki/evaluation/literature-map.md` |
| Yazı | Tez taslağı (53 sayfa) ve makale biçimli taslak (11 sayfa); ekip ve danışman okumadı, gönderilmedi | `wiki/thesis/README.md` |

Ölçümlerin ortak sınırı: referans insan altın standardı değildir ve hiçbir koşuda bir insan inceleme
kararı vermedi. Projenin adındaki "insan döngüsü" kodda vardır, ölçümde yoktur.

## Sıradaki işler (öneri)

Bu sıra bir öneridir; ekip ve danışman onaylamadı. Sıralamanın gerekçesi bağımlılıktır: üstteki iş
bitmeden alttakinin emeği boşa gidebilir.

| Sıra | İş | Neyi bekler | Neyi karşılar |
|---|---|---|---|
| 1 | **Kararlar.** CSE 491 proje önerisi tek proje çerçevesiyle yazılır ve danışmana sunulur (son gün 2026-10-18; çerçeve `wiki/project/overview.md`, "Çerçeve"); tez, makale ve öneri taslakları bu çerçevededir. TÜBİTAK formu gönderilmeden önce kaynakça hataları düzeltilir ve ölçümle çelişen hedefler gözden geçirilir; çalışma dili, platform etiketinin yeterliliği ve dönem kapsamı danışmanla konuşulur | Yok | `wiki/project/open-decisions.md` soru 1, 2, 4, 15, 17, 18, 22 |
| 2 | **Karar hedefini kalıcı yapmak.** İnceleme kararı adayın kimliğine değil içeriğine bağlanır | Yok | Değişiklik C3. Yapılmazsa 3. ve 4. işteki insan emeği her yeniden çıkarımda sıfırlanır |
| 3 | **İnsan altın standardı, küçük başlangıç.** İki kodlayıcı aynı hadisleri sistem çıktısını görmeden etiketler; kodlayıcılar arası karşılıklı F1 hesaplanır; 300 hadislik koşular bu referansa karşı yeniden puanlanır | Soru 11'deki atama; etiketleme kılavuzu üzerinde anlaşma | K-5'in ilk adımı; H1 ve L1 için mutlak sayı. Kit hazır: `giraffegraph-core/evaluation/annotation/` |
| 4 | **İncelemesi yapılmış bir koşu.** İnceleme kuyruğundaki adaylar (şema-only koşulda 538, isnad-farkındalıklı koşulda 16) kör protokolle karara bağlanır; red oranı ve aday başına süre kaydedilir | 2. iş; 3. işteki atama | H3 için ilk veri; "doğrulanmış olgu başına uzman süresi" |
| 5 | **Ravi kimliği.** Mention'lar bir otorite listesine bağlanır; yanlış birleşme oranı birincil ölçüttür | Soru 5 (otorite listesi ve izin) | K-2, H4. Taban çizgisi ölçüldü |
| 6 | **Alan kuralları.** Kural kancası; muâsara, likâ, tabaka kuralları ihlali incelemeye yollar | 5. iş (doğum ve vefat yılları otorite verisinden gelir) | K-3 |
| 7 | **Modeller ve tekrarlar.** En az bir açık model; koşul başına tekrar; `anthropic` tel biçiminin düzeltilmesi | Soru 10 ve 12 | K-4 |
| 8 | **Şemanın genişlemesi.** Uzmanla birlikte varlık ve ilişki tipleri; kapsama ölçümü | Soru 6; alan uzmanının zamanı | K-1 |
| 9 | **Soru-cevap katmanı.** Altın cevaplı soru kümesi; graf ile çıplak RAG karşılaştırması | Soru 18; 5. iş (yol ve ağ soruları kimlik ister) | CSE 491 kapsam ifadesi; L4 |
| 10 | **Yayım hijyeni.** Lisans, site metni, veri yayın biçimi | Soru 14, 19, 20 | H-5 |

2, 3 ve 10 numaralı işler birbirini beklemez ve farklı kişilerce aynı anda yürütülebilir.

## Rules

- MUST: bu sayfadaki sıra öneridir; onaylandığında `wiki/decisions/` altına ADR yazılır ve "öneri"
  etiketi kalkar.
- MUST: bir iş bittiğinde satırı "Bugün elde olan" tablosuna taşınır ve ilgili taahhüt satırı
  `wiki/project/tubitak-commitments.md` içinde güncellenir. Biten iş sıra tablosunda bırakılmaz.
- MUST: insan emeği isteyen iş (3, 4) kararın içerik adresli hedefi yazılmadan büyütülmez. Gerekçe:
  karar aday kimliğine bağlıyken model ya da prompt değişince bütün kararlar yetim kalır
  (`wiki/sources/claude-science-results/05_kod_degisiklik_listesi.md`, C3).
- SHOULD: yeni bir iş eklenirken hangi taahhüdü ya da açık soruyu karşıladığı yazılır; karşılığı
  olmayan iş eklenmez.

## Source anchors

- `wiki/architecture/workspace-map.md`, "Bilinen durum notları" — kodda duran değişiklikler, test sayıları
- `wiki/evaluation/correctness-measurement.md`, "Ölçülmemiş olanlar" ve "Önkoşullar"
- `wiki/sources/claude-science-results/06_6_aylik_is_plani.md` — iş paketleri, kritik yol, kapılar
- `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/*/run_report.json:candidates_in_review` — inceleme kuyruğundaki aday sayıları

## Verification checklist

- [ ] "Bugün elde olan" tablosundaki test sayısı `cd giraffegraph-core/backend && uv run pytest -q` çıktısıyla aynı
- [ ] Sıra tablosundaki her iş bir taahhüde ya da açık soruya bağlı
- [ ] Biten hiçbir iş sıra tablosunda durmuyor
- [ ] İnceleme kuyruğu sayıları koşu raporlarıyla aynı

## Related docs

- `wiki/project/tubitak-commitments.md`
- `wiki/project/open-decisions.md`
- `wiki/project/overview.md`
- `wiki/evaluation/correctness-measurement.md`
- `wiki/domains/hadith/isnad-pipeline.md`

## Last updated

2026-10-13
