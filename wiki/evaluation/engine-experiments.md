# Motor deneyleri: LLM koşulları, değer-alıntı kapısı ve kimlik taban çizgisi

## Purpose

Core boru hattı üzerinde 2026-10-12'de koşulan deneylerin tasarımını, başlık sayılarını ve bu sayıların
neyi gösterip neyi göstermediğini tek yerde tutmak. Ham sayılar sonuç dosyalarındadır; bu sayfa onlara
çapa verir.

## Scope

- In: koşullar, veri kümeleri, referansın niteliği, mention uyumu, eşli farklar, değer-alıntı kapısının
  yakalama gücü, inceleme yükü, maliyet, Sonnet yapılandırma hatası, ad yazımıyla kimlik taban çizgisi
- Out: katman modeli ve metrik tanımları (`wiki/evaluation/correctness-measurement.md`), boru hattı
  davranışı ve neden kodları (`wiki/domains/hadith/isnad-pipeline.md`), çalıştırma komutları
  (`giraffegraph-core/evaluation/README.md`), veri kümelerinin kuruluşu (`data/README.md`)

Statü: ölçüm. Bu sayfadaki hiçbir sayı doğruluk değildir. Referanslar platform ya da kural etiketidir;
insan altın standardı yoktur ve hiçbir koşuyu insan incelemedi.

## Tasarım

| Öğe | Değer |
|---|---|
| Motor | `giraffegraph-core` çalışma ağacı (kod `main` dalındadır), bellek içi depo; koşucu `backend/scripts/run_isnad_experiment.py` |
| Akış | bölütleme → çıkarım → doğrulama → açık inceleme öğesi olmayan koşunun commit'i. İnceleme kararı verilmez |
| Model | Claude Haiku 5.5, effort `low`; prompt sürümü her koşunun `run_report.json:prompt_version` alanında |
| Eşleşme | M1 katı ve M2 gevşek (`giraffegraph-core/evaluation/scorer.py`); başlık sayıları M2 |
| İstatistik | Hadis düzeyinde yüzdelik bootstrap, 2000 örnekleme, seed 0. Eşli farkta her örnekleme iki koşu için aynı hadisleri çeker |

Koşullar (`run_isnad_experiment.py:CONDITIONS`):

| Koşul | Bölütleme ve çağrı | Modele verilen şema |
|---|---|---|
| `rule` — kural tabanlı | `isnad`; LLM yok, `rule_based_isnad` sağlayıcısı | — |
| `llm_schema_whole` — şema-only | Hadis başına tek çağrı | İsnad şemasının yalnız yapısı: tip ve özellik açıklaması yok, çıkarım ipucu yok |
| `llm_isnad_whole` — isnad-farkındalıklı, tüm hadis | Hadis başına tek çağrı | İsnad şablonu, ipuçlarıyla |
| `llm_isnad_chain` — isnad-farkındalıklı, zincir başına | `isnad`; zincir başına bir çağrı | İsnad şablonu, ipuçlarıyla |

Veri kümeleri:

| Küme | İçerik | Referans | Not |
|---|---|---|---|
| `data/eval/sixbooks-fresh/` | 300 hadis: altı kitabın her birinden 50; 1.778 referans mention; 50 pilot hadisin hiçbiriyle örtüşmez | İfta platform etiketleri (`reference.jsonl`) | Test kümesi |
| `wiki/sources/claude-science-results/pilot_sample.json` (kopyası `data/eval/pilot50/`) | 50 pilot hadis, 327 referans mention | Sanadset `<NAR>` etiketleri (kural üretimi) | Kural tabanlı bölütleyici bu 50 hadiste ayarlandı; bu kümedeki sayı test sonucu değildir |
| `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/subset36.json` | 300'lük kümede her koleksiyonun ilk 6 hadisi, 36 hadis | İfta platform etiketleri | Sonnet denemesi |

### Referansın niteliği

İfta etiketleri, İfta Sünnet platformunun işaretlemesinin üçüncü bir kişi tarafından kazınıp yeniden
yapılandırılmış hâlidir. İnsan çift kodlamalı altın standart değildir; kaynak, platformun bu işaretlemeyi
nasıl ürettiğini söylemez ve kodlayıcılar arası uyum raporlamaz (`data/README.md`, "What the labels are").

İki etiket kümesinin birbirine uyumu: Sanadset etiketleri sistem, İfta etiketleri referans alındığında,
300 hadisten metni iki korpusta eşleşen 253'ünde M2 P 0,939 · R 0,979 · F1 0,959 [0,943; 0,972],
M1 F1 0,931 (2026-10-12; `data/README.md`, "Agreement between the two label sets"). Bu iki etiket
kümesi arasındaki uyumdur; ikisi de doğrunun kendisi değildir. 253 hadis rastgele bir alt küme değil,
ifadesi iki korpusta örtüşen hadislerdir.

## Mention uyumu: 300 hadis, İfta etiketleri

Önerilen çıktı (doğrulamadan önce), 1.778 referans mention. Kaynak:
`giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/compare-ifta.md`.

| Koşul | P (M2) | R (M2) | F1 (M2) [%95 GA] | F1 (M1) | Tam doğru zincir oranı (M2) |
|---|---|---|---|---|---|
| Kural tabanlı | 0,968 | 0,881 | 0,923 [0,910; 0,935] | 0,633 | 0,490 |
| Şema-only, tüm hadis | 0,914 | 0,868 | 0,890 [0,865; 0,914] | 0,826 | 0,567 |
| İsnad-farkındalıklı, tüm hadis | 0,997 | 0,919 | 0,956 [0,946; 0,966] | 0,904 | 0,690 |
| İsnad-farkındalıklı, zincir başına | 0,998 | 0,903 | 0,948 [0,936; 0,959] | 0,897 | 0,650 |

Eşli farklar (M2, aynı 300 hadis; aynı dosya, "Paired differences"):

| Karşılaştırma | Metrik | Fark [%95 GA] |
|---|---|---|
| Şema-only − kural tabanlı | F1 | −0,032 [−0,060; −0,006] |
| İsnad-farkındalıklı (tüm hadis) − kural tabanlı | F1 | +0,034 [0,021; 0,047] |
| İsnad-farkındalıklı (tüm hadis) − şema-only | Precision | +0,083 [0,059; 0,108] |
| İsnad-farkındalıklı (tüm hadis) − şema-only | F1 | +0,066 [0,041; 0,091] |
| Tüm hadis − zincir başına (isnad-farkındalıklı) | F1 | +0,008 [−0,002; 0,019] |

Okuma: şema açıklaması ve ipucu almayan model kural tabanlı ayrıştırıcının altında, isnad şablonuyla
üstünde uyum verir. Tek çağrı ile zincir başına çağrı arasındaki farkın aralığı sıfırı içerir. Katı
eşleşmede (M1) kural tabanlı koşul LLM koşullarının altındadır; bilinen bir nedeni mention aralığının
uzamasıdır (`wiki/domains/hadith/isnad-pipeline.md`, "Bilinen sınırlar").

Zincir sayısına göre recall (M2; `2026-10-12-sixbooks300/extra-tables-ifta.json`, `by_reference_chain_count`; referansa
göre tek zincirli 226, birden çok zincirli 74 hadis):

| Koşul | Recall, tek zincir | Recall, 2+ zincir |
|---|---|---|
| Kural tabanlı | 0,924 | 0,778 |
| Şema-only, tüm hadis | 0,886 | 0,824 |
| İsnad-farkındalıklı, tüm hadis | 0,940 | 0,868 |
| İsnad-farkındalıklı, zincir başına | 0,915 | 0,874 |

Aynı dosya koleksiyona ve referans mention sayısına göre kırılımı, yalnız commit edilen çıktının
puanını, güven eşiği tablosunu ve hadis başına çağrı sayısını da verir. Üreten betik:
`giraffegraph-core/evaluation/extra_tables.py`.

"Zincir başına" koşulunda 300 hadisin yalnız 10'u birden fazla çağrıya bölündü (aynı dosya,
`hadiths_with_more_than_one_call`); bölütleyici yeni segmenti yalnız tahvîl işaretinde başlatır. Bu
koşul esas olarak modelin girdisini zincir aralığıyla sınırlamanın etkisini ölçer; uzun ve çok zincirli
hadislerde zincir başına çağrının etkisi ölçülmedi.

## Değer-alıntı kapısı hata yakalayıcı olarak

Yöntem (`giraffegraph-core/evaluation/analyze_experiment.py`): önerilen her `Narrator` mention'ı M2
hizalamasında bir referans mention'la eşleşiyorsa "doğru", eşleşmiyorsa "yanlış" sayılır. Kapı, neden
kodu o mention'ın aday düğümünde üretildiyse mention'ı işaretlemiş sayılır. "Yanlış" burada İfta
etiketiyle eşleşmeyen demektir. Kaynak: her koşunun `analysis-ifta/analysis.json` dosyası, `gate_table`.

| | Şema-only, tüm hadis | İsnad-farkındalıklı, tüm hadis |
|---|---|---|
| Önerilen mention | 1.688 | 1.639 |
| Yanlış mention | 145 | 5 |
| `value_not_in_quote` ile işaretlenen | 155 | 3 |
| İşaretlenen ve yanlış (yakalanan) | 122 | 3 |
| İşaretlenen ve doğru (yanlış alarm) | 33 | 0 |
| İşaretlenmeyen yanlış (kaçan) | 23 | 2 |
| `quote_not_in_segment` ile işaretlenen | 0 | 0 |
| İncelemesiz kabul edilen çıktı, M2 P / R / F1 | 0,985 / 0,849 / 0,912 | 0,999 / 0,919 / 0,957 |

- Her alıntı kendi segmentinde bulundu; alıntı kapısı iki koşulda da hiçbir şey işaretlemedi. Pilotun
  bulgusu motor içinde tekrarlandı: "alıntı kaynakta var mı" kontrolü bu hata türünü yakalamaz, "değer
  alıntıda var mı" kontrolü yakalar.
- Şema-only koşulunda kapı precision'ı 0,914'ten 0,985'e çıkarır, recall'u 0,868'den 0,849'a indirir;
  indirilen kısım incelemeye düşer, silinmez.
- LLM güven skorunun doğru mention'ı yanlıştan ayırma gücü şema-only koşulunda AUC 0,634 (1.543 doğru,
  145 yanlış mention; aynı dosya, `confidence`).

### Eşleşmeyen önerilerin bileşimi

"Yanlış" sayılan mention yanlış bir ravi demek değildir; İfta etiketinin yazımıyla eşleşmeyen öneri
demektir. Şema-only koşulunda işaretlenen 155 adın sabit kurallarla sınıflandırması
(`giraffegraph-core/evaluation/classify_value_flags.py`; çıktı
`2026-10-12-sixbooks300/haiku-llm_schema_whole/value-flag-classes.json`):

| Değişiklik türü | İşaretlenen | Eşleşmeyen | Eşleşen |
|---|---|---|---|
| Latin harfine çevrilmiş ad (14 hadis) | 79 | 79 | 0 |
| Adın i'râb hâli değişmiş (`أبي` → `أبو`) | 34 | 21 | 13 |
| Akrabalık ifadesi adla değiştirilmiş (`عن أبيه` → ad) | 25 | 18 | 7 |
| Diğer, ad metnin başka yerinde geçiyor | 7 | 3 | 4 |
| Diğer, ad metinde geçmiyor | 10 | 1 | 9 |

- İşaretlenen 155 adın 130'u normalize hadis metninde geçmez, 25'i geçer.
- Eşleşmeyen 145 önerinin 102'sinin adı metinde yoktur ve kapı 102'sini de işaretler; 43'ünün adı
  metinde vardır, kapı bunların 20'sini işaretler.
- Peygamber'i ravi sayan 10 eşleşmeyen öneri vardır; kapı ikisini işaretler (ikisi de Latin harfli),
  sekizini kaçırır. Bu kategori hatasını yakalayan bir kapı Core'da yoktur.
- Akrabalık durumlarının çoğu çıkarımdır: 25 adın 15'i metnin başka yerinde geçer (`هشام بن عروة عن أبيه`
  → `عروة`). Metinde hiçbir biçimde bulunmayan ek içeren bir işaretli ad saptandı (`عثمان` → `عثمان بن عفان`).
- İ'râb değişikliği iki kelimelik adda M2 eşiğinin altında kalıp "eşleşmedi", daha uzun adda "eşleşti"
  sayılır. Kapı da puanlayıcı da yüzey biçimini karşılaştırdığı için uyumlarının bir kısmı tanım gereğidir.

Katı eşleşmede sıra tersine döner: şema-only LLM (F1 0,826; tam doğru zincir 0,567) kural tabanlı
koşulun (0,633; 0,490) üstündedir. "Şema-only LLM kuralın altında" cümlesi yalnız M2 için geçerlidir.

Şema-only koşulunda grafa incelemesiz yazılan çıktı (açık inceleme öğesi olan 110 hadis boş sayılarak):
P 0,983, R 0,582, F1 0,731 (`extra-tables-ifta.json`, `committed_output_only`). "İncelemesiz kabul edilen
çıktı" satırı aday durumunu ölçer, grafı değil.

Güven eşiği ile kapının aynı ölçekte karşılaştırması (şema-only; `extra-tables-ifta.json`,
`confidence_as_review_signal`; modelin kullandığı ayrı güven değeri sayısı 7):

| Sinyal | İncelemeye giden mention | İçindeki eşleşmeyen (145 üzerinden) |
|---|---|---|
| Güven < 0,80 | 65 (%3,9) | 16 |
| Güven < 0,85 | 275 (%16,3) | 50 |
| Güven < 0,90 | 1.018 (%60,3) | 110 |
| `value_not_in_quote` | 155 (%9,2) | 122 |

İnceleme yükü ve commit (`analysis.json`, `review_workload`; `run_report.json`, `runs`):

| | Şema-only | İsnad, tüm hadis | İsnad, zincir başına |
|---|---|---|---|
| İncelemeye düşen aday | 538 (155 düğüm, 383 ilişki) | 16 | 6 |
| İnceleme öğesi çıkmayan hadis payı | 0,633 | 0,980 | 0,987 |
| İncelemesiz commit edilen koşu | 190 / 300 | 294 / 300 | 295 / 300 |

Kural tabanlı koşulda 300 koşunun 300'ü commit edildi ve inceleme öğesi çıkmadı. Zincir başına koşulda
310 çağrıdan biri motorun kabul etmediği bir çıktı döndürdü (tanımsız düğüme bağlanan ilişki); o hadis
commit edilmedi.

## Maliyet

Claude Haiku 5.5, 2026-10-06 liste fiyatı: milyon girdi token'ı 0,10 USD, milyon çıktı token'ı 0,50 USD
(`run_isnad_experiment.py:PRICES_USD_PER_MTOK`). Tutar, her yanıtın token sayısından hesaplanır.

| Koşul (300 hadis) | 1.000 hadis başına USD | Hadis başına token (girdi + çıktı) |
|---|---|---|
| Şema-only, tüm hadis | 1,87 | 6.276 |
| İsnad-farkındalıklı, tüm hadis | 2,29 | 7.381 |
| İsnad-farkındalıklı, zincir başına | 2,21 | 7.041 |

2026-10-12'deki sekiz ayrı LLM koşusunun yanıt önbelleği yok sayılarak hesaplanan tutarı toplam 3,49 USD'dir
(`run_report.json:cost_usd_without_response_cache`: pilot50 × 3, sixbooks300 × 3, subset36 Sonnet × 2).
subset36'daki iki Haiku koşusu tümüyle yanıt önbelleğinden geldi.

## 50 pilot hadis, Sanadset etiketleri

Kaynak: `giraffegraph-core/evaluation/results/2026-10-12-pilot50/compare-sanadset.md`. Referans kural
üretimi Sanadset `<NAR>` etiketleridir; 50 hadis, 327 referans mention.

| Koşul | F1 (M2) [%95 GA] |
|---|---|
| Kural tabanlı | 0,892 [0,850; 0,933] |
| Şema-only, tüm hadis | 0,828 [0,726; 0,921] |
| İsnad-farkındalıklı, tüm hadis | 0,945 [0,913; 0,971] |
| İsnad-farkındalıklı, zincir başına | 0,919 [0,880; 0,956] |

Kural tabanlı bölütleyici bu 50 hadis üzerinde ayarlandığı için kural tabanlı satır bu kümede iyimserdir.
2026-09-30 pilotunun LLM sayıları motorun dışında, `wiki/sources/claude-science-results/pilot_isnad.py` ve
`claude-sonnet-5` ile üretilmiştir (`wiki/sources/claude-science-results/08_pilot_raporu.md`, "Model"); koşul adları
benzerdir, düzenek aynı değildir.

## Sonnet 5.5, effort `low`: yapılandırma hatası

Claude Sonnet 5.5, effort `low`, 36 hadis, İfta etiketleri, iki tüm-hadis koşulu. Kaynak:
`giraffegraph-core/evaluation/results/2026-10-12-subset36/compare-ifta.md` ve koşuların `run_report.json`
dosyaları.

| | Sonnet, isnad-farkındalıklı | Sonnet, şema-only | Haiku, isnad-farkındalıklı | Haiku, şema-only |
|---|---|---|---|---|
| Recall (M2) | 0,237 | 0,530 | 0,916 | 0,828 |
| Precision (M2) | 0,981 | 0,966 | 0,995 | 0,894 |
| Commit edilemeyen koşu | 30 / 36 | 22 / 36 | 0 / 36 | 13 / 36 |

İsnad-farkındalıklı koşulda Sonnet 36 hadisin 28'inde tek bir `Narrator` düğümü döndürdü ve ravi adını
özellik değerine değil özellik anahtarı alanına yazdı. Motor 29 ayrı tanımsız özellik anahtarını
`schema_property_proposal` olarak kaydetti; adı boş kalan düğümler `node_merge_key` ve
`required_node_property` kurallarıyla reddedildi. Önerilen mention'ların precision'ı iki koşulda da
0,966'nın altına inmedi; adı olmayan düğümler grafa yazılmadı, açık şema önerisi taşıyan koşular commit
edilmedi.

Bu bir model karşılaştırması değildir. Sağlayıcının tel biçimi (`properties` nesnesi `{name, value}`
girdilerinin listesi olarak gider) ile effort ayarının birlikte verdiği bir yapılandırma hatasıdır
(`giraffegraph-core/backend/src/app/infrastructure/llm/anthropic_provider.py:_PROPERTY_ENTRIES_SCHEMA`).
Sonuç klasörlerinde başka effort düzeyiyle ya da başka tel biçimiyle Sonnet koşusu yoktur.

## Ad yazımıyla kimlik: taban çizgisi (L2)

Core'da `Narrator` düğümünün kimliği adın yazımıdır. Bu ölçüm, sistem çıktısına değil referansa bakar:
300 hadisin referans zincirlerindeki mention'lar İfta ravi numarası yerine ad yazımına göre gruplanırsa
ne olur? Betik `giraffegraph-core/evaluation/identity_baseline.py`, girdi
`data/eval/sixbooks-fresh/reference_chains.jsonl`, 2026-10-12. 2.150 mention geçişi, 740 kişi. Kaynak:
`giraffegraph-core/evaluation/results/2026-10-12-identity-baseline/sixbooks300.json`.

| | Adın tam yazımı | Normalize edilmiş ad |
|---|---|---|
| Ayrı anahtar | 964 | 878 |
| Birden çok kişiyi kapsayan anahtar | 24 | 28 |
| Bu anahtarların altındaki mention (over-merge) | 216 (%10,0) | 262 (%12,2) |
| Birden çok anahtara bölünen kişi | 191 (%25,8) | 161 (%21,8) |
| Pairwise P / R | 0,737 / 0,559 | 0,759 / 0,703 |
| B-cubed P / R | 0,941 / 0,715 | 0,931 / 0,792 |

Normalizasyon bölünmeyi azaltır, yanlış birleşmeyi artırır. En çok kişiyi kapsayan anahtar iki durumda da
"babası" ifadesidir (`أبيه`: 34 kişi, 57 mention). Kişi numaraları İfta derleyicisinin atamasıdır; uzman
hükmü değildir (`data/README.md`, "What the labels are").

## Sınırlar

- Referans insan altın standardı değildir; İfta etiketlerinde derleyici notundaki raviler tutarsız
  etiketlenmiştir ve sistem bunları çıkardığında yanlış sayılır (`data/README.md`, "Caveats").
- Hiçbir koşuda inceleme kararı verilmedi; HITL'in katkısı ve uzman süresi ölçülmedi.
- Ölçüm mention düzeyindedir. `NARRATED_FROM` ilişkileri için ayrı P / R hesaplanmadı.
- 300 hadislik kümede tek model ve tek effort düzeyi koşuldu (Claude Haiku 5.5, `low`).
- Modelin isnadı metinden mi çıkardığı, eğitim verisinden mi hatırladığı ayrıştırılmadı.
- Her koşul bir kez koşuldu; aynı koşulun tekrarları arasındaki oynaklık kayıtlı değil.

## Rules

- MUST: bu sayfadaki sayılar aktarılırken referansın adı (İfta platform etiketi / Sanadset kural etiketi)
  ve eşleşme kriteri birlikte yazılır; "doğruluk" kelimesi kullanılmaz. Gerekçe: iki referans da insan
  altın standardı değildir.
- MUST: 50 pilot hadisteki kural tabanlı sayı test sonucu olarak sunulmaz. Gerekçe: bölütleyici o
  hadislerde ayarlandı.
- MUST: Sonnet koşuları model karşılaştırması olarak aktarılmaz. Gerekçe: ölçülen şey tel biçimi ile
  effort ayarının hatasıdır.
- SHOULD: yeni bir koşu eklenirken sonuç klasörü `giraffegraph-core/evaluation/results/<tarih>-<ad>/`
  altına yazılır ve bu sayfanın ilgili tablosuna satır eklenir.

## Source anchors

- `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/` — `compare-ifta.md`, `extra-tables-ifta.json`,
  koşu başına `run_report.json` ve `analysis-ifta/analysis.json`
- `giraffegraph-core/evaluation/results/2026-10-12-pilot50/compare-sanadset.md`
- `giraffegraph-core/evaluation/results/2026-10-12-subset36/compare-ifta.md`
- `giraffegraph-core/evaluation/results/2026-10-12-identity-baseline/sixbooks300.json`
- `giraffegraph-core/backend/scripts/run_isnad_experiment.py` — `CONDITIONS`, `PRICES_USD_PER_MTOK`, harcama sınırı
- `giraffegraph-core/evaluation/analyze_experiment.py`, `compare_runs.py`, `identity_baseline.py`, `scorer.py`
- `data/README.md` — veri kümelerinin kuruluşu, etiketlerin kaynağı, iki etiket kümesinin uyumu
- `data/eval/sixbooks-fresh/` — `hadiths.json`, `reference.jsonl`, `reference_chains.jsonl`, `provenance.json`

## Verification checklist

- [ ] "Mention uyumu" tablosundaki her sayı `2026-10-12-sixbooks300/compare-ifta.md` içindeki satırla eşleşiyor
- [ ] Kapı tablosundaki sayılar ilgili koşunun `analysis-ifta/analysis.json:gate_table` alanıyla eşleşiyor
- [ ] `python giraffegraph-core/evaluation/identity_baseline.py --reference-chains data/eval/sixbooks-fresh/reference_chains.jsonl`
      çıktısı kimlik tablosuyla aynı
- [ ] Sayfada referans etiketine karşı ölçülen hiçbir değer "doğruluk" diye anılmıyor

## Related docs

- `wiki/evaluation/correctness-measurement.md`
- `wiki/evaluation/related-work.md`
- `wiki/domains/hadith/isnad-pipeline.md`
- `giraffegraph-core/evaluation/README.md`

## Last updated

2026-10-12
