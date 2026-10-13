# 02b — TÜBİTAK 2209-A formu: taahhütler ve eleştirel okuma

Kaynak: `02a_TUBITAK_2209A_form_original.pdf` (2026 I. Dönem başvurusu). Aşağıdaki özet, PDF metninden Claude Code tarafından çıkarıldı. Bağlayıcı olan PDF'tir. Başvurunun kabul durumu bu pakette **kayıtlı değil**.

## Künye

- **Başlık:** Büyük Dil Modellerinde Halüsinasyon ve Şema Sapmasını Önleyen İnsan-Döngülü Bilgi Grafı Üretim Motoru: Hadis İsnad Zincirleri Üzerine Bir Uygulama
- **Başvuranlar:** Deniz Büyükşahin, Yahya Efe Kuruçay, İbrahim Çakır
- **Danışman:** Dr. Öğr. Üyesi Taha Yiğit Alkan
- **Kurum:** Akdeniz Üniv. Mühendislik Fak. Bilgisayar Müh.; alan uzmanı Prof. Dr. Rifat Atay (İlahiyat, destek beyanı ekli)
- **Süre:** 6 ay, 4 iş paketi
- **Yöntem çerçevesi:** Design science (Hevner 2004; Wieringa 2014) + karşılaştırmalı deney

## Bağlayıcı taahhütler

### Bilimsel katkılar (CORE'un üzerine)
| Kod | Taahhüt | Ölçülebilir çıktı |
|---|---|---|
| K-1 / E-1 | Hadith Schema & ontoloji (JSON-Schema) | ≥8 varlık tipi (Ravi, Hadis, Kitap, Bab, Yer, Dönem, Künye, Tabaka), ≥10 ilişki tipi (rivayet_etti, hoca_oldu, talebe_oldu, doğdu, vefat_etti, yaşadı_yer, kitabında_geçer…). Uzman onaylı v1.0. Pilot 25 metinde ≥%95 kapsama |
| K-2 / E-2 | Türkçe-Arapça transliterasyon-farkındalıklı entity resolution | Varyant sözlüğü + Levenshtein + Türkçe fonetik (Soundex/Metaphone uyarlaması) + tabaka kısıtı. Eşik altı → HITL. Duplicate-node oranında baz çizgiye göre ≥%50 azalma |
| K-3 / E-3 | İsnad-farkındalıklı tutarlılık kuralları | Muâsara (A vefat < B doğum → red/işaret), likâ (buluşma kaydı yok → HITL), tabaka tutarlılığı (aynı tabakada hoca/talebe → şüpheli) |
| E-4 | Hadis-özgü prompt şablonları | Few-shot + ontoloji-bilinçli, varyant sözlüğüne referanslı; 5 şablon |
| K-4 | Karşılaştırmalı deney | 5 BDM (Llama-3-8B, Mistral-7B, Qwen2-7B, GPT, Claude Sonnet) × 2 koşul (doğrudan üretim vs GiraffeGraph) × 3 tekrar × 500 hadis |
| K-5 | Türkçe Hadis Ravi Ağı altın standardı | 500 hadis (Kütüb-i Sitte'den tabakalı örnekleme), ≥5.000 üçlü, Cohen's κ ≥ 0,75, Zenodo/HF'de üçlü düzeyinde açık yayın |
| H-2 | Performans | ≥100 üçlü/dk, sıfır şema-dışı yazım |
| H-5 | Yaygın etki | ≥1 bildiri (UBMK, INISTA, EMNLP Workshop örnek verilmiş) ve/veya 1 hakemli yayın, arXiv preprint, açık kod/veri, 1 bölüm içi seminer |

### Araştırma sorusu
BDM ile KG çıkarımında deterministik şema doğrulama + HITL onay katmanı içeren hadis-farkındalıklı mimari (GiraffeGraph + Hadith Schema + transliterasyon-aware ER + isnad kuralları), doğrudan üretime kıyasla halüsinasyon ve şema sapma oranını ne ölçüde düşürür?

### Hipotezler
- **H1:** Precision, doğrudan BDM→graf yazımına göre en az **+0,15 (mutlak)** artar.
- **H2:** Şema sapma oranı **<%5**.
- **H3:** HITL reddetme oranı ile halüsinasyon oranı pozitif ve anlamlı (**p<0,05**) ilişkili.
- **H4:** Transliterasyon-aware ER, duplicate-node oranını baz çizgiye (yalnızca normalizasyon) göre **≥%50** düşürür.

### Metrik tanımları (formdaki haliyle)
Precision, Recall, F1 (üçlü düzeyinde, altın standarda göre); Şema Uyumluluk Oranı (SUO); Halüsinasyon Oranı = dayanaksız üçlü / toplam üçlü; HITL Reddetme Oranı = reddedilen / HITL'e ulaşan aday; Duplicate Node Oranı = tekrar düğümleşme / toplam ravi düğümü.

### İstatistik planı
İki yönlü ANOVA (mimari × BDM) + η²p; varsayım ihlalinde Friedman; duplicate oranı için iki orantı z-testi.

### Takvim
| Ay | İş paketi | Başarı ölçütü | Ağırlık |
|---|---|---|---|
| 1–2 | F1 Ontoloji + prompt v1 | Uzman onaylı şema, 25 metinde ≥%95 kapsama | %20 |
| 2–4 | F2 ER + kural seti + CORE entegrasyonu | ≥100 üçlü/dk, sıfır şema-dışı yazım, duplicate ≥%50 azalma | %30 |
| 3–5 | F3 500 hadis etiketleme | ≥5.000 üçlü, κ ≥ 0,75 | %25 |
| 5–6 | F4 Deneyler + istatistik + yayın | Sonuç tablosu, açık veri/kod, bildiri taslağı | %25 |

### Riskler / B planları
R1 API maliyeti → açık modeller öncelik, ticari modeller n=100 alt küme · R2 lisans → telifsiz meal, yalnızca üçlü paylaşımı · R3 κ düşük → kılavuz iterasyonu, 500→350 metin · R4 takvim → %15 tampon, 3→2 tekrar · R5 transliterasyon → sözlük + fonetik + HITL · R6 "CORE zaten yapılmış" algısı → ön çalışma beyanı.

## Formda "zaten var" denen şeyler (bkz. `05` — kodla karşılaştırma)
- "Açık kaynak olarak yayımlanmış", "uçtan uca çalışır" CORE
- "JSON-Schema ile tip ve kardinalite doğrulaması"
- "İdempotent ve geri alınabilir" Postgres + Neo4j çift yazım
- "(subject, predicate, object, source_span, confidence)" aday yapısı
- "Şüpheli kayıtlar kuyrukta uzmana sunulur"

## Metodolojik zayıflıklar (Claude Code'un okuması; Claude Science doğrulamalı)

1. **H1 karşılaştırması adil değil.** "GiraffeGraph" koşulu insan onayını içeriyor, baz çizgi içermiyor. İnsanın düzelttiği çıktının precision'ı yüksek çıkar, bu neredeyse tanım gereği. Otomatik filtrelemenin (şema + kurallar + grounding) etkisi ile insan etkisi **ayrı ayrı** ölçülmeli. En az şu koşullar gerekir: (i) ham LLM, (ii) +şema doğrulama, (iii) +grounding/kurallar, (iv) +ER, (v) +HITL. Ayrıca insan başına maliyet de raporlanmalı.
2. **Döngüsellik (circularity) riski.** HITL'de karar veren uzman ile altın standardı denetleyen uzman aynı kişi (Prof. Atay). HITL koşulu, altın standarda "sızabilir". Kör protokol ya da ayrı kodlayıcı gerekir.
3. **H2 mevcut kodda trivyal.** Kod, tanımsız tipi zaten reddediyor (`05`), yani yazılan graf %0 sapma verir. Anlamlı ölçüm, **ham model çıktısındaki sapma** ve **reddedilme yüzünden kaybolan bilgi**dir.
4. **H3'ün istatistik gücü çok düşük.** Model düzeyinde n=5 (×3 tekrar) gözlemle korelasyon ekolojik ve zayıf olur. Ayrıca HITL sadece düşük güvenli alt kümeyi görüyor (`05`), yani reddetme oranı yönlendirme politikasına koşullu. Öneri: aday düzeyinde, karışık etkili lojistik regresyon (rastgele etki: hadis, model).
5. **Tekrarlar temperature=0 ile anlamsızlaşabilir.** Kod `temperature: 0` gönderiyor (`14`, openai_provider). 3 tohum tekrarı API modellerinde neredeyse aynı çıktıyı verir. ANOVA'yı külliyat düzeyindeki 30 agregaya uygulamak gücü düşürür. Öneri: hadis düzeyinde eşleştirilmiş analiz, bootstrap güven aralıkları, permütasyon/McNemar, karışık etkili modeller.
6. **Açık uçlu çıkarımda Cohen's κ iyi tanımlı değil.** Sabit öğe kümesi ve negatif sınıf yok. IE literatüründe kodlayıcılar arası uyum genelde karşılıklı F1 ile raporlanır. κ ancak sabit bir aday kümesindeki kabul/red kararlarında anlamlıdır. İkisi birden raporlanmalı.
7. **ER metriği asimetrik olmalı.** Hadiste iki farklı raviyi yanlışlıkla birleştirmek (over-merge), tekrarı kaçırmaktan (under-merge) daha tehlikelidir çünkü zincirin hükmünü değiştirir. Sadece "duplicate node oranı" yetmez: pairwise P/R/F1, B-cubed, CEAF ve ayrı bir **yanlış-birleştirme oranı** gerekir.
8. **Veri riski: Türkçe meallerde isnad genelde kısaltılmıştır** `[UNVERIFIED — doğrula]`. Popüler Türkçe hadis derlemeleri çoğu zaman yalnızca sahabiyi verir ("Ebû Hüreyre'den rivayet edildiğine göre..."), tam zinciri vermez. Tam isnad için Arapça kaynak (ör. Sanadset, `08`) gerekebilir. Bu, "Türkçe altın standart" iddiasını ve dil tasarımını etkiler.
9. **Muâsara kuralı dış bilgi ister.** Doğum/vefat yılları hadis metninde yoktur, bir ravi otorite dosyasından (rical veritabanı) gelir. Bu yüzden E-2 aslında **dedup değil, otorite listesine entity linking** problemidir. Otorite listesinin kendisi küratörlü bir varlıktır ve karar defterinin parçası sayılmalıdır (`12`).
10. **Model listesi 2026 için eski.** Llama-3-8B, Mistral-7B ve Qwen2-7B 2024 modelleri. Aynı ailenin güncel sürümleri gerekçelendirilebilir, ama form değişikliği gerektirip gerektirmediği danışmana sorulmalı.
11. **"100 üçlü/dk" darboğazı yanlış yerde.** Asıl darboğaz insan onayı. Doğrulanmış üçlü başına uzman dakikası raporlanmalı (sitenin 3. araştırma sorusu tam da bu).
12. **Formdaki türler Neo4j'de çalışmaz.** `doğdu`, `yaşadı_yer`, `kitabında_geçer`, `Künye` gibi ASCII olmayan adlar mevcut koddaki `^[A-Za-z_][A-Za-z0-9_]*$` identifier regex'ine takılır, hem de ancak commit anında, insan onayından sonra (`05` #8).

## Referans doğrulama durumu (2026-09-30, hızlı web aramasıyla)

| Referans | Durum |
|---|---|
| Pan vd. 2024 TKDE (LLM+KG Roadmap) | Muhtemelen doğru (bilinen çalışma) |
| Edge vd. 2024 GraphRAG arXiv:2404.16130 | Muhtemelen doğru |
| Ji vd. 2023 ACM CSUR (Hallucination survey) | Çalışma gerçek. Ancak **"açık alan KG çıkarımında %15–%40 halüsinasyon" iddiası bu surveyde muhtemelen yok** `[UNVERIFIED — birincil kaynaktan kontrol et]` |
| Ye vd. 2023 "Generative KG Construction: A Review", Findings of EMNLP 2023 | Çalışma gerçek. **Venue/yıl muhtemelen yanlış** (EMNLP 2022 olabilir), kontrol et |
| Lewis vd. 2020 RAG NeurIPS | Doğru |
| Hevner vd. 2004; Wieringa 2014; Hogan vd. 2021; Kejriwal 2019 | Muhtemelen doğru |
| Zhang & Soh 2024 EDC, EMNLP 2024 | Muhtemelen doğru |
| **Al-Khatib & Stein 2024 "Schema-Guided IE with LLMs" LREC-COLING** | **Aramada bulunamadı.** Yazarların LREC-COLING 2024 bildirisi başka konuda. Uydurma olabilir |
| **Bulut, H. 2017 "Hadis Râvilerinin Tespitinde Tabakat Kitaplarının Yeri" İAD 38** | **Aramada bulunamadı.** Benzer başlık başka yazar/dergide var (Aslan 2017, Bingöl İFD). Uydurma olabilir |
| **Düzenli, Y. 2019 "Hadis İsnad Sistemi ve Râvi Ağ Analizleri" MÜİFD 56** | **Aramada bulunamadı.** Yazar adı dergide geçiyor ama başlık doğrulanamadı |
| TÜBİTAK 2024 ÜYZ Rehberi; 12. Kalkınma Planı | Kontrol et |

> Uyarı: Formun kendisi TÜBİTAK "Sorumlu ÜYZ" rehberine uyum iddia ediyor. Doğrulanamayan referanslar kabul sonrası rapor ve yayında ciddi risk taşır. Hepsi birincil kaynaktan kontrol edilmeli.
