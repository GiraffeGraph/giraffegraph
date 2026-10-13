# TÜBİTAK 2209-A taahhütleri: eldeki kanıt

## Purpose

Formdaki her taahhüt ve hipotez için bugün elde ne olduğunu, neyin eksik olduğunu ve hangi revizyonun
önerildiğini tek tabloda tutmak. Bir plan ya da rapor yazılırken taahhüdün karşılanıp karşılanmadığı
buradan okunur.

## Scope

- In: K-1…K-5, E-4, H-2, H-5 taahhütleri; H1…H4 hipotezleri; formdaki kaynakça hataları; danışmana
  sunulması önerilen revizyonlar
- Out: taahhütlerin tam metni (`wiki/sources/claude-science-context/02a_TUBITAK_2209A_form_original.pdf`),
  ölçümlerin ayrıntısı (`wiki/evaluation/engine-experiments.md`), sıradaki işler (`wiki/project/roadmap.md`)

## Durum, bir bakışta

Başvuru gönderilmedi (proje sahibinin beyanı, 2026-10-13); form taslaktır ve aşağıdaki hedefler
gönderilmeden önce değiştirilebilir. Aşağıdaki tablo
taahhüdü form metniyle, kanıtı 2026-10-13 itibarıyla kod ve ölçüm dosyalarıyla verir. Ölçümlerin
hepsinde referans İfta platform etiketi ya da Sanadset kural etiketidir; hiçbiri insan altın standardı
değildir ve hiçbir koşuda inceleme kararı verilmedi.

| Kod | Taahhüt (form) | Eldeki | Eksik |
|---|---|---|---|
| K-1 / E-1 | Hadith Schema: en az 8 varlık tipi, en az 10 ilişki tipi, uzman onaylı v1.0, 25 metinde en az %95 kapsama | İsnad şablonu: 2 düğüm tipi (`Narrator`, `Hadith`), 2 ilişki tipi (`NARRATED_FROM`, `TRANSMITS`). Tip ve özellik adları ASCII olarak doğrulanır | 6 varlık tipi, 8 ilişki tipi, uzman onayı, kapsama ölçümü. Formdaki Türkçe karakterli teknik adlar (`doğdu`, `yaşadı_yer`) Neo4j'de geçersizdir; teknik ad ASCII, görünen ad Türkçe olmalıdır |
| K-2 / E-2 | Transliterasyon-farkındalıklı varlık çözümleme: varyant sözlüğü, Levenshtein, Türkçe fonetik, tabaka kısıtı | Yok. Ravi kimliği adın tam yazımıdır. Bu kimliğin referans üzerindeki taban çizgisi ölçüldü: 740 kişi 964 anahtara düşer; mention geçişlerinin %10,0'ı birden çok kişiyi kapsayan anahtardadır; kişilerin %25,8'i birden çok anahtara bölünür (300 hadis, 2.150 mention geçişi, İfta ravi numaraları) | Katmanın tamamı. Otorite listesi adayları indirildi: İfta ravi profilleri (20.957), AR-Sanad ravi tablosu (18.298); kaynaklardan yazılı izin kayıtlı değil |
| K-3 / E-3 | Muâsara, likâ, tabaka tutarlılık kuralları | Core'da yok; alan kuralı eklemek için bir kanca da yok. Motor dışı bir benzetimde tabaka ve vefat yılı kuralı AR-Sanad etiketleri üzerinde denendi: kural bir ravi kararının kapsamını daralttığında sessiz hata mention başına 0,053'ten 0,013'e iner (`wiki/evaluation/decision-ledger-experiments.md`, Sonuç 2) | Kural kancası, üç kural, doğum ve vefat yılı taşıyan otorite verisi |
| E-4 | Hadise özgü 5 prompt şablonu | Prompt kataloğunda 2 şablon. Deneyde şema-only ve isnad-farkındalıklı koşullar karşılaştırıldı: isnad-farkındalıklı koşul eşli F1'i +0,066 [0,041 – 0,091], precision'ı +0,083 artırır (300 hadis, M2) | 3 şablon; varyant sözlüğüne referans |
| K-4 | 5 BDM × 2 koşul × 3 tekrar × 500 hadis | 1 model (Claude Haiku 5.5, effort `low`) × 3 LLM koşulu ve 1 kural tabanlı koşul × 1 koşu × 300 hadis. `openai` uyumlu ve `anthropic` sağlayıcıları var | 4 model (açık modeller hiç koşulmadı), tekrarlar, 200 hadis. Claude Sonnet 5.5 denemesi yapılandırma hatasıyla sonuçlandı, model karşılaştırması sayılmaz |
| K-5 | 500 hadislik Türkçe altın standart, en az 5.000 üçlü, Cohen's κ ≥ 0,75, açık yayın | Yok. Etiketleme kiti hazır: kılavuz, etiketlenecek hadis tablosu, tabloyu referansa çeviren betik. Kodlayıcılara gönderilmedi | Altın standardın tamamı. Türkçe metinle hiçbir ölçüm yapılmadı; telifsiz Türkçe tam isnad kaynağının varlığı doğrulanmadı |
| H-2 | Dakikada en az 100 üçlü; sıfır şema dışı yazım | İsnad-farkındalıklı koşulda 300 hadis 516 saniyede işlendi ve grafa 2.886 kenar yazıldı (bellek içi depo, insan onayı yok; süreyi model sağlayıcısının gecikmesi belirler). Tanımsız tip adayı reddedilir, tanımsız özellik inceleme önerisi olur | Gerçek veritabanıyla ve insan onayıyla süre ölçümü |
| H-5 | En az 1 bildiri ya da hakemli yayın, arXiv ön baskı, açık kod ve veri, bölüm semineri | Kod GitHub'da açık (`GiraffeGraph/giraffegraph-core`); LICENSE dosyası yok. Makale biçimli taslak `wiki/thesis/paper/` altında, gönderilmedi | Lisans, veri yayını, gönderim, seminer |

## Hipotezler

| Kod | Form metni | Eldeki ölçüm | Değerlendirme |
|---|---|---|---|
| H1 | Precision, doğrudan BDM → graf yazımına göre en az +0,15 (mutlak) artar | Şema-only koşulda modelin önerdiği çıktı P 0,914; incelemesiz kabul edilen çıktı P 0,985, R 0,849 (300 hadis, M2, İfta etiketi, insan yok) | Fark +0,071. Baz çizgi 0,914 iken ulaşılabilecek en büyük mutlak artış +0,086'dır; +0,15 aritmetik olarak ulaşılamaz. Aynı ölçüm hata payında 0,086 → 0,015 düşüş gösterir. İnsan onayının katkısı ölçülmedi |
| H2 | Şema sapma oranı %5'in altında | Üç LLM koşulunda 300'er hadis: tanımsız düğüm ya da ilişki tipi 0; tanımsız özellik önerisi 1 (`TRANSMITS.hadith_ref`, şema-only koşul) | Tip düzeyinde hipotez kendiliğinden sağlanır. Anlamlı ölçüm özellik düzeyinde ve ham model çıktısındadır |
| H3 | HITL red oranı ile halüsinasyon oranı pozitif ve anlamlı (p < 0,05) ilişkili | Veri yok: hiçbir koşuda inceleme kararı verilmedi. Kayıt altyapısı var (`review_decisions`: kim, ne zaman, süre) | Model düzeyinde 5 gözlemle korelasyon zayıftır; aday düzeyinde model önerilir |
| H4 | Transliterasyon-farkındalıklı ER, tekrar düğüm oranını baz çizgiye göre en az %50 düşürür | ER yok. Pilotta string tabanlı birleştirmenin tavanı %17,5 (50 hadis, 327 mention, 2026-09-30). 300 hadiste normalizasyon bölünmeyi azaltır, yanlış birleşmeyi artırır | %50, string yöntemleriyle ulaşılamaz; otorite listesine bağlama gerekir. Tek isimli mention'lar (`سفيان`, `أبيه`) yanlış birleşmenin kaynağıdır |

## Önerilen revizyonlar (karar değil)

Claude Science'ın danışmana sunulmasını önerdiği dört revizyon. Hiçbiri ekip ya da danışman tarafından
onaylanmadı; danışmana sunulduklarına dair kayıt yok.

| # | Revizyon | Form metni değişir mi | 2026-10-12 ölçümü ne diyor |
|---|---|---|---|
| R-a | H1 göreli hata azalması olarak yazılır: "hata oranını en az %50 düşürür" | Evet | Destekler: 300 hadiste baz çizgi precision'ı 0,914, mutlak +0,15 için yer yok |
| R-b | H2 özellik düzeyine taşınır | Evet | Destekler: üç LLM koşulunun 910 çağrısında tip düzeyinde sapma 0 |
| R-c | Model listesi aynı ailelerin güncel sürümleriyle güncellenir | Muhtemelen hayır; yazılı onay önerilir | Açık model koşusu yok, veri yok |
| R-d | Karar defteri katmanı eklenir | Muhtemelen hayır | Asgari hâli kodda: `review_decisions`. İçerik adresli hedef ve yeniden üretim betiği yok |

Formun yöntem bölümüne yönelik on iki maddelik eleştiri (adil olmayan H1 karşılaştırması, uzmanın hem
HITL'de hem altın standartta yer alması, açık uçlu çıkarımda κ'nın tanımsızlığı, ER metriğinin
asimetrisi ve diğerleri): `wiki/sources/claude-science-context/02b_tubitak_commitments_and_critique.md`,
"Metodolojik zayıflıklar".

## Formdaki kaynakça hataları

Formun EK-1 kaynakçasındaki 15 referans 2026-09-30'da Crossref, arXiv ve ACL Anthology'den kontrol edildi
(`wiki/sources/claude-science-results/04a_kaynak_dogrulama_tablosu.md`).

| Sorun | Referans | Önerilen düzeltme |
|---|---|---|
| Bulunamadı | Al-Khatib & Stein 2024 (LREC-COLING) | Silinir |
| Bulunamadı | Bulut 2017 (İAD 38) | Aslan, Muhammed (2017), Bingöl Üniversitesi İlahiyat Fakültesi Dergisi 5/10, 269–290 |
| Bulunamadı | Düzenli 2019 (MÜİFD 56) | Alam & Schneider (2021), arXiv:2102.02009 |
| Künye yanlış | Ye vd., "Findings of EMNLP 2023" | EMNLP 2022 ana konferans, s. 1–17 |
| İddia kaynakta yok | Ji vd. 2023'e atfedilen "%15–%40 halüsinasyon" | Cümle kaldırılır ya da projenin kendi ölçümüyle değiştirilir |

Doğrulanmış künyeler: `wiki/sources/claude-science-results/04b_dogrulanmis_kaynakca.bib`. Bu hataların
danışmana ya da TÜBİTAK'a bildirildiğine dair kayıt yok. Bunlar revizyon değil, hata düzeltmesidir.

## Rules

- MUST: taahhüt metni aktarılırken form PDF'i esas alınır; bu sayfadaki tablo özettir.
- MUST: bir plan K-1…K-5 ya da H1…H4 ile çelişmez; taahhüdü kapsar ya da genişletir. Hipotez metnini
  değiştiren her öneri (R-a, R-b) danışmanın yazılı onayına bağlıdır.
- MUST: "Eldeki" sütununa yalnız dosyayla desteklenen şey yazılır; referans insan altın standardı
  değilse bu belirtilir. Gerekçe: K-5 ve H1 mutlak doğruluk iddia eder, eldeki sayılar etiket kümesiyle
  uyumdur.
- MUST: bir taahhüdün durumu değiştiğinde (yeni ölçüm, yeni kod, danışman kararı) bu sayfa aynı görevde
  güncellenir.
- SHOULD: formdan bir referans aktarılmadan önce doğrulama tablosuna bakılır.

## Source anchors

- `wiki/sources/claude-science-context/02a_TUBITAK_2209A_form_original.pdf` — form metni (gönderilmemiş taslak)
- `wiki/sources/claude-science-context/02b_tubitak_commitments_and_critique.md` — taahhüt tablosu, hipotezler, takvim, eleştiri
- `wiki/sources/claude-science-results/03_revize_deney_protokolu.md` §4.1, §6, §8 — H1 tavanı, H4 protokolü, R-a…R-d
- `wiki/sources/claude-science-results/04a_kaynak_dogrulama_tablosu.md` — kaynakça doğrulaması
- `giraffegraph-core/backend/src/app/infrastructure/template/catalog.py:ISNAD_TEMPLATE_SCHEMA` — şablondaki tipler
- `giraffegraph-core/backend/src/app/infrastructure/llm/prompt_catalog.py:DEFAULT_STRUCTURED_PROMPTS` — prompt şablonları
- `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/compare-ifta.md` — koşul başına P / R / F1 ve eşli farklar
- `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/*/run_report.json` — `schema_proposals`, `candidates_rejected`, `wall_time_seconds`, `canonical_graph`
- `giraffegraph-core/evaluation/results/2026-10-12-identity-baseline/sixbooks300.json` — ad yazımıyla kimlik taban çizgisi
- `giraffegraph-core/evaluation/annotation/` — etiketleme kiti (`GUIDELINE.md`, `hadiths_to_label.tsv`, `build_sheet.py`, `to_reference.py`)

## Verification checklist

- [ ] Tablodaki her taahhüt kodu form PDF'inde aynı sayılarla geçiyor
- [ ] "Eldeki" sütunundaki her sayı çapa verilen dosyada bulunuyor
- [ ] `ISNAD_TEMPLATE_SCHEMA` içindeki tip sayısı K-1 satırıyla aynı
- [ ] Onaylanmış bir revizyon varsa `wiki/decisions/` altında ADR'si var ve bu sayfada "öneri" diye durmuyor

## Related docs

- `wiki/project/overview.md`
- `wiki/project/open-decisions.md`
- `wiki/project/roadmap.md`
- `wiki/evaluation/correctness-measurement.md`
- `wiki/evaluation/engine-experiments.md`

## Last updated

2026-10-13
