# 06 — Altı aylık iş planı (2–3 kişilik lisans ekibi)

**Kısıt:** formdaki 4 iş paketi (F1–F4) ve ağırlıkları (%20/%30/%25/%25) korunur. Aşağıdaki plan
onların **içini** doldurur ve bir **İP0** (hafta 0–2) ekler. İP0 formda yok ama olmadan üç risk
patlar: dil kararı, lisans, ve etiketleme altyapısı.

Ekip rolleri (isimler `00`'dan): **E** = Yahya Efe Kuruçay (mimari, backend, deney altyapısı),
**D** = Deniz Büyükşahin (etiketleme altyapısı + kodlayıcı K1), **İ/A** = İbrahim Çakır /
Alperen Ulukaya (deterministik parser + ER + kodlayıcı K2). Alan uzmanı: Prof. Dr. Rifat Atay.

---

## Minimum uygulanabilir sürüm (MVS) vs ideal sürüm

Bu ayrım plandan önce gelmeli, çünkü **her şey yapılamaz**.

| | **MVS — teslim garantisi** | **İdeal — zaman kalırsa** |
|---|---|---|
| Temsil | Neo4j KG + hadis-kapsamlı kenar anahtarı | `Transmission` reifikasyonu |
| Karar | `decision_events` append-only tablo + içerik-adresli hedef + `rebuild.py` | Tam event sourcing, artımlı materialize, redaction yolu |
| Kapılar | C1 (değer grounding), C2 (per-item fail + proposal), C6 (blocklist + muâsara) | C9 (TransformRule), C10 (property şema), C14 (risk-tabanlı yönlendirme) |
| Çıkarım | Deterministik segmenter + zincir-başına LLM | 5 prompt şablonu × ablation |
| ER | B0→B1→B3 (otorite linking), Wirahman korpusu baz çizgi | B2 fonetik, bağlamsal ER, HITL merge UI |
| Deney | Cx, C1, C1d, C2, C3b, C4 × 3 model × 350 hadis | + C0, C3a, Cseg, C5 × 5 model × 500 hadis |
| Altın standart | 350 hadis, katman (a) 2 kodlayıcı + katman (b) uzman | 500 hadis + T-obscure alt kümesi |
| Genelleme | Kod vakası **tek bir soru setiyle** (20 soru), Kur'an vakası **yalnız vaka anlatısı** | İkisi de tam deney |
| Yayın | arXiv preprint + UBMK/INISTA bildirisi | + workshop bildirisi |

**MVS, formdaki tüm K-1…K-5 ve H1–H4 taahhütlerini karşılar.** İdeal sürüm, tez iddiasını
genişletmek içindir.

---

## İP0 — Hafta 0–2: risk kapatma (formda yok, ekleniyor)

| Görev | Kim | Çıktı | Başarı ölçütü |
|---|---|---|---|
| **Dil kararı:** telifsiz Türkçe hadis/meal kaynağı ara; bulunanda isnad kısaltılmış mı diye **ölç** (rastgele 50 metin, tam isnad oranı) | E + Atay | Karar notu (karar defterine ilk kayıt) | Ölçülmüş bir oran ve yazılı karar. `[Bu paketten çözülemedi — en yüksek riskli açık soru]` |
| **Lisans doğrulama:** Sanadset CC0 ✔ (teyit edildi); Hawramani ve muslimscholars.info lisansları | İ/A | Lisans tablosu | Her kaynak için yazılı lisans |
| **Formdaki hata düzeltmeleri:** 2 uydurma referans + Ji vd. sayısı → danışmana bildir | E | Düzeltilmiş kaynakça (`04b`) | Danışman onayı |
| **Mevcut çalışmaların okunması:** Wirahman 2026, Raja 2026, Haque & Islam 2026, Asgari-Bidhendi 2025, SemanticHadith | Tüm ekip | 2 sayfalık konumlanma notu | K-1/K-2'nin özgünlük iddiası yeniden yazılmış |
| **Repo hijyeni:** LICENSE, README, `uv.lock`, kırık test (C11) | E | Temiz repo | `uv sync && pytest` yeşil |
| **Site metni düzeltmesi** (`05` Bölüm C) | A | Güncellenmiş landing page | Kodla çelişen cümle kalmadı |

**İP0 kapısı:** dil kararı verilmemişse F3'e başlanmaz. Bu, R2'nin gerçek karşılığı.

---

## F1 — Ay 1–2: Ontoloji + prompt + çekirdek kapılar (%20)

| Görev | Kim | Kod ref |
|---|---|---|
| SemanticHadith ontolojisi incelenir; Hadith Schema **onun üzerine** kurulur (sıfırdan değil) | E + Atay | — |
| Hadith Schema v1.0: ≥8 varlık, ≥10 ilişki. **Teknik adlar ASCII, `display_name` Türkçe** | E | **C4** |
| Değer grounding kapısı | E | **C1** |
| Per-item fail + `schema_proposals` | E | **C2** |
| `decision_events` + içerik-adresli hedef | E | **C3** |
| Deterministik isnad segmenter (`pilot_isnad.py` temeli, karakter offset'li) | İ/A | **C7** |
| 5 prompt şablonu; C1 (şema-only) ve C1d (isnad-aware) referans olarak sabitlenir | D | — |
| Etiketleme kılavuzu v1 + etiketleme aracı (Argilla/Prodigy veya basit bir Streamlit) | D | — |

**Başarı ölçütü (form):** uzman onaylı şema; 25 metinlik pilotta ≥%95 kapsama.
**Ek ölçüt:** `pytest` yeşil; C1 kapısı 50 hadislik pilot verisinde `%10 ± 5` ihlal yakalıyor
(pilot referans değeri **%10,1**).

---

## F2 — Ay 2–4: ER + kural seti + entegrasyon (%30)

| Görev | Kim | Kod ref |
|---|---|---|
| Ravi otorite listesi ingest + **karar defterine** tarih çelişkileri | İ/A | — |
| ER merdiveni B0→B1→B2→B3, Wirahman korpusu baz çizgi | İ/A | — |
| `DomainRule` protokolü + muâsara/likâ/tabaka + blocklist | E | **C6** |
| Hadis-kapsamlı kenar anahtarı; aday/canonical anahtar hizalaması | E | **C5** |
| Zincir-başına çağrı + chunking | E | **C8** |
| `rebuild.py` | E | **C13** |
| Deney koşum altyapısı (Cx, C0–C4, Cseg) + token/süre/maliyet ölçümü | D | — |

**Başarı ölçütü (form):** ≥100 üçlü/dk; sıfır şema-dışı yazım; duplicate-node ≥%50 azalma.
**Revizyon (gerekçe `08` §4.6):** "≥%50 azalma" **B0→B3** karşılaştırması olarak ölçülür
(string tabanlı tavan Arapçada %17,5). Ayrıca **over-merge oranı birincil metrik** olarak eklenir.
**"100 üçlü/dk" için not:** `02b` #11 haklı, darboğaz insan onayı. Bu ölçüt korunur ama yanına
**doğrulanmış üçlü başına uzman saniyesi** konur (`decision_events.duration_ms`).

---

## F3 — Ay 3–5: Altın standart (%25)

| Görev | Kim |
|---|---|
| Tabakalı örnekleme: 500 hadis (MVS: 350) + T-obscure alt kümesi (Kütüb-i Sitte dışı) | D |
| Katman (a): mention span + sıra + sîga, **2 kodlayıcı, sistem çıktısı görmeden** | D (K1) + İ/A (K2) |
| Anlaşmazlık çözümü | E (K3) |
| Katman (b): mention → otorite ID, **sabit aday kümesinde** 2 bağımsız değerlendirici | Atay + 2. ilahiyat kodlayıcısı |
| Uyum: katman (a) karşılıklı F1 (M1 ve M2), katman (b) Cohen's κ | D |
| Kör atama tablosu; C5'te karar veren ≠ o hadisin altın standardını üreten | E |

**Başarı ölçütü (form):** ≥5.000 üçlü; κ ≥ 0,75 (katman b'ye bağlanır).
**Aritmetik uyarı:** pilotta hadis başına 6,36 mention → 500 hadis ≈ 3.180 mention,
≈ 2.680 `NARRATED_FROM` üçlüsü. **≥5.000 üçlüye ulaşmak için 8 varlık tipinin diğer ilişkileri
(doğdu/vefat_etti/kitabında_geçer/tabaka) de sayılmalı.** Bu, formda hesaplanmamış — F1'de
şema tasarlanırken üçlü bütçesi çıkarılmalı.

---

## F4 — Ay 5–6: Deney, istatistik, yayın (%25)

| Görev | Kim |
|---|---|
| Ablation merdiveni: Cx, C0–C4, Cseg × modeller × 500 (MVS: 3 model × 350) | D + E |
| C5 (HITL) × 1 model × 150 hadis × kör protokol; uzman saniyesi ölçümü | Atay + E |
| Veri sızıntısı testleri: T-mask, T-perturb, T-obscure | İ/A |
| **D-T3:** ikinci prompt/model ile yeniden çıkarım → içerik-adresli karar yeniden uygulama oranı | E |
| Kalibrasyon: AUC + reliability diagram + ECE | D |
| Tüketim kalitesi: 60 soruluk küme, graf vs RAG | İ/A |
| Karışık etkili modeller + cluster bootstrap + Holm; yardımcı ANOVA | E |
| Zenodo/HF yayını (yalnız üçlü düzeyinde), kod yayını, arXiv preprint, UBMK/INISTA bildirisi | Tüm ekip |
| Bölüm içi seminer | Tüm ekip |

**Başarı ölçütü (form):** sonuç tablosu, açık veri/kod, ≥1 bildiri taslağı.

---

## Genelleme vakaları (tez iddiasını genişletmek için; MVS'de hafif)

| Vaka | MVS kapsamı | Zaman |
|---|---|---|
| **B Kod tabanı** | Açık kaynak orta ölçekli bir repo; **20 soruluk** küme (10 yapısal + 10 niyet/karar); iki koşul: (i) ajan grep/read, (ii) karar defteri + linter. Şirket kodu **kullanılmaz** | F4 içinde 4 gün |
| **C Kur'an** | Yeni deney yok. `07`'deki olay, mimarinin üç failure mode'unu (SSOT ihlali, invalidation eksikliği, karar kaydının hatayı yakalaması) gösteren **vaka anlatısı** olarak yazılır | F4 içinde 1 gün |

---

## Risk yönetimi (formun R1–R6'sına ek)

| Risk | Erken uyarı sinyali | B planı |
|---|---|---|
| **R7 — Türkçe tam isnad yok** | İP0 ölçümü: tam isnad oranı <%20 | Katman TR'yi zincir çıkarımından çıkar, **yalnız ER/transliterasyon** için kullan; K-5'in adını `03` §1.2'deki hâle çevir |
| **R8 — K-2 önceliklenmiş (Wirahman 2026)** | İP0 okuması | Katkıyı "Türkçe düzlem + HITL + karar defteri" olarak yeniden konumla; Wirahman'ı **baz çizgi** yap. Bu, karşılaştırma zemini olduğu için katkıyı *güçlendirir* |
| **R9 — H1 tavan problemi** | F4 ilk koşumda baz çizgi precision >0,85 | H1'i göreli hata azalmasına çevir (`03` §4.1 R-a); danışman onayı İP0'da alınmış olsun |
| **R10 — Uzman zamanı yetmez** | F3'te κ oturumları 2 haftayı aşarsa | 500→350; C5 alt kümesini 150→75; katman (b)'yi yalnızca *belirsiz* mention'lara daralt |
| **R11 — Etiketleme aracı yazmak F1'i yer** | Hafta 6'da araç bitmediyse | Argilla/Prodigy yerine **TSV + iki kolonlu Google Sheet**. Araç yazmak araştırma değil |
| **R12 — Karar defteri refactor'u F1'i yer** | Hafta 8'de C3 bitmediyse | `decision_events`'i **yeni tablo** olarak ekle, `ReviewItem`'ı silme. Çift yazım geçici olarak kabul edilebilir |

---

## Kritik yol ve kapılar

```
İP0 (2 hf) ──► F1 (8 hf) ──► F2 (8 hf) ──► F4 (8 hf)
   │             │                            ▲
   │             └──► F3 (10 hf, F1 ile paralel başlar) ──┘
   │
   └─ KAPI 0: dil kararı yazılı mı?          (yoksa F3 başlamaz)
                 KAPI 1: C3 (karar defteri) bitti mi?  (bitmezse F3'teki emek F4'te kaybolur)
                          KAPI 2: κ ≥ 0,75 mi?         (değilse kılavuz iterasyonu, 500→350)
```

**En tehlikeli sıralama hatası:** F3 (etiketleme) C3'ten (karar defteri + içerik-adresli hedef)
**önce** tamamlanırsa, F4'teki her yeniden çıkarım o emeği geçersiz kılar. KAPI 1 bu yüzden var.

## Toplam iş yükü kontrolü

P0 (9 gün) + P1 (8 gün) + P2 (5 gün) = **22 iş günü kod**. 2–3 kişilik ekip, 26 haftada haftada
~1,5 kişi-gün kod ayırabilirse rahat sığar. Kalan zaman etiketleme (F3, en büyük kalem), deney
koşumu ve yazımdır. **Kod planın darboğazı değil; etiketleme ve uzman zamanı darboğaz.**
