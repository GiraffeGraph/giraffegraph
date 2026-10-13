# 03 — Revize hadis deney protokolü

**Kısıt:** TÜBİTAK formundaki K-1…K-5 ve H1…H4 **korunur**. Bu protokol onları kapsar ve genişletir;
hiçbirini iptal etmez. Değişen şey **ölçüm birimi, eşleşme kriteri ve istatistik**; taahhüt edilen
çıktılar aynı kalır. Danışman onayı gerektiren dört revizyon §8'de listelidir.

---

## 1. Veri kaynağı ve dil kararı

### 1.1 Karar: Arapça birincil, Türkçe ikincil (iki katmanlı)

Gerekçe, kanıtla:

| | |
|---|---|
| **Arapça tam isnad mevcut ve lisanslı** | Sanadset 650K (Mghari vd. 2022, *Data in Brief* 44:108540) — bu pakette **kullanıldı**. HF aynası `freococo/650k_sanadset`, **CC0-1.0** (dataset kartından teyit). `<SANAD>/<NAR>/<MATN>` etiketli, 926 kitaptan 650.986 kayıt. Wirahman (2026) bu korpusta **185.216 tekil ravi ad varyantı** sayıyor |
| **Türkçe tam isnad `[UNVERIFIED]`** | Formdaki R2 riski ve `02b` #8 hâlâ açık. Telifsiz bir Türkçe hadis derlemesi bulamadım; bu yüzden "Türkçe meallerde isnad kısaltılmış mı?" sorusunu **test edemedim**. Bu, projenin **en yüksek riskli açık sorusudur** ve İP0'da (ilk 2 hafta) çözülmeli |
| **Telif riski** | Diyanet "Hadislerle İslam", İ. Canan tercümesi vb. **kullanılmamalı**. Form R2'nin cevabı: telifsiz metin + yalnızca üçlü düzeyinde paylaşım |

**Protokol:**
- **Katman AR (birincil, n=500):** Sanadset'ten tabakalı örnekleme. Tam isnad garanti. K-5 altın
  standardı buradan üretilir.
- **Katman TR (ikincil, n=150):** İP0'da bulunacak telifsiz Türkçe kaynak. **Amaç farklı:** H4'ün
  transliterasyon iddiasını test etmek. Eğer Türkçe kaynakta isnad kısaltılmışsa (sadece sahabi),
  katman TR **zincir çıkarımı için değil, yalnızca ravi adı normalizasyonu/ER için** kullanılır ve
  bu formda açıkça yazılır.

### 1.2 K-5 altın standardı: "Türkçe Hadis Ravi Ağı" adının dürüst hâli
Form K-5'i "Türkçe Hadis Ravi Ağı" diye adlandırıyor. Veri Arapça isnad + Türkçe TDV-tarzı
transliterasyonlu ravi otorite kimlikleri olacaksa isim şu olmalı:
**"Türkçe transliterasyonlu ravi otorite eşlemesi ile Arapça isnad altın standardı"**.
Uzun ama doğru; değerlendiricinin "Türkçe hadis metni nerede?" sorusunu engelliyor.

### 1.3 Ravi otorite listesi (`13` soru 5)
Aday: Hawramani `hadithtransmitters` (100.915 kayıt) ve `muslimscholars.info` (25.247 kayıt) —
ikisi de Wirahman (2026) tarafından kullanılmış ve eşleme korpusu açık kaynak yayımlanmış.
**Lisans her ikisi için ayrıca doğrulanmalı** `[UNVERIFIED]`; bu paketten teyit edemedim.
Otorite listesinin hataları (doğum/vefat yılı çelişkileri) **karar defterine yazılır**, upstream'de
düzeltilmez (`12` §3).

### 1.4 Mevcut çalışmalarla konumlanma (zorunlu)
Wirahman (2026, arXiv:2607.05424) **K-2'yi büyük ölçüne önceliyor**: Sanadset adlarını iki biyografi
veritabanına çok-sinyalli ER ile bağlıyor (ad benzerliği + **vefat yılı yakınlığı** = muâsara +
güvenilirlik derecesi polaritesi), 185.216 düğüm / 814.093 kenarlı grafı yayımlıyor.
**Sonuç:** K-2 artık "hadis ravileri için ER" olarak özgün değil. Özgün kalan iki şey:
(i) Türkçe transliterasyon düzlemi, (ii) ER kararlarının **insan onayı ve karar defteri** ile
birleştirilmesi (Wirahman tamamen otomatik ve HIGH/MED/LOW bantları insan onayından geçmiyor).
Protokol bu iki şeyi ölçecek biçimde kurulmalı ve Wirahman'ın eşleme korpusu **baz çizgi** olarak
kullanılmalıdır — bu, projeyi zayıflatmaz, karşılaştırma zemini verir.

---

## 2. Ablation merdiveni (H1'in adil sınanması)

`11`'deki merdiven doğru; pilot ışığında iki değişiklik: **Cx'in konumu yükseliyor** ve
**C3 ikiye ayrılıyor**.

| Kod | Koşul | Ne ölçer | Maliyet |
|---|---|---|---|
| **Cx** | Deterministik isnad ayrıştırıcı (sîga lügati + tahvîl + otorite eşleme). **LLM yok** | "LLM gerekli mi?" | ~0 |
| **C0** | Ham LLM → doğrudan graf, şema bilgisi yok (formdaki baz çizgi) | referans | düşük |
| **C1** | + şema-kısıtlı prompt (tip listesi + JSON kontratı) = **GiraffeGraph'ın mevcut prompt'u** | prompt/şema etkisi | düşük |
| **C1d** | + alan-farkındalıklı prompt (E-4: sîga, isnad/matn, "birebir kopyala", blocklist) | **alan prompt'u etkisi** | düşük |
| **C2** | + deterministik şema doğrulama, **aday bazında** red + `schema_proposal` kaydı | drift filtresi + bilgi kaybı | ~0 |
| **C3a** | + `quote ⊂ segment` + offset kapısı | alıntı grounding'i | ~0 |
| **C3b** | + `property_value ⊂ quote` + TransformRule kapısı | **değer grounding'i** | ~0 |
| **C4** | + otorite listesine ER + isnad kuralları (muâsara/likâ/tabaka) | alan bilgisi | orta |
| **C5** | + HITL, yönlendirme politikası P ∈ {tümü, eşik, risk-tabanlı} | **insan katkısı ve maliyeti** | yüksek |
| **Cseg** | Deterministik segmentasyon + **zincir başına** LLM çağrısı (C1d prompt'u) | uzun zincir recall'ı | düşük |

**Kapsam:** Cx, C0–C4 ve Cseg tüm 5 model × 500 hadis üzerinde koşturulur (otomatik, ucuz).
**C5 yalnız** en iyi otomatik koşul × 1 model × 150 hadislik alt küme × kör protokol.

**Neden Cseg eklendi:** pilotta hadis-başına tek çağrı, 8+ ravili zincirlerde recall'i 0,654'e
düşürdü ve 50 çağrının 6'sı `max_tokens`'ta kesildi. Zincir-başına çağrı hipotezi test edilmeli.

---

## 3. Metrik tanımları (eşleşme kriterleri dahil)

### 3.1 İki katmanlı altın standart
- **Katman (a) — mention ve sıra:** metinden doğrulanabilir. Ravi mention span'leri (karakter
  offset'leri) + zincir sırası + sîga etiketi. İki öğrenci kodlayıcı.
- **Katman (b) — otorite kimliği:** mention → ravi otorite ID. Uzman hükmü (Prof. Atay).

İki katman **ayrı raporlanır**. Formdaki "≥5.000 üçlü" hedefi katman (a) ile sağlanır (pilotta
hadis başına 6,36 mention → 500 hadis ≈ 3.180 mention ve ≈ 2.680 `NARRATED_FROM` üçlüsü;
**≥5.000 üçlüye ulaşmak için ya 8 varlık tipinin diğer ilişkileri sayılmalı ya da n artırılmalı.
Bu aritmetik formda yapılmamış — düzeltilmeli**).

### 3.2 Eşleşme kriterleri (formda hiç tanımlı değil; en önemli düzeltme)
Her metrik **üç** kriterle raporlanır:

| Kriter | Tanım | Ne için |
|---|---|---|
| **M1 katı (exact)** | Normalize edilmiş mention string'leri birebir eşit. Normalizasyon: hareke kaldırma, `أإآٱ→ا`, `ى→ي`, `ة→ه`, tatvîl/noktalama temizliği (Türkçe için: şapka kaldırma, `İ/ı` katlanması) | Span sınırı kalitesi |
| **M2 gevşek (partial)** | Birebir eşitlik **veya** substring **veya** içerik-token F1 ≥ 0,60 | Küme doğruluğu |
| **M3 otorite (linked)** | Aynı ravi otorite ID'sine bağlanmış | **Asıl hedef.** Zincir hükmünü belirleyen budur |

Pilot M1 ile M2 arasındaki farkın ne kadar büyük olduğunu gösteriyor: deterministik ayrıştırıcı
M1'de F1=0,628, M2'de F1=0,879. **Tek kriterle raporlamak sonucu ±0,25 oynatabilir.** Form bu
yüzden eşleşme kriterini yazmadan precision taahhüt etmemeli.

Eşleştirme algoritması: **maksimum ağırlıklı ikili eşleştirme** (Hungarian), greedy değil.
Referans uygulama `pilot_isnad.py:align`.

### 3.3 Metrik listesi

**Mention/üçlü düzeyi:** P, R, F1, **F0.5** (asimetrik hata maliyeti; `08` #4.6'daki over-merge
tuzakları gerekçe). Her biri M1/M2/M3 için.

**Zincir düzeyi:** tam doğru zincir oranı; zincir düzenleme mesafesi (eksik/uydurma/sıra hatası
ayrı sayılır); sıra konkordansı.

**Halüsinasyon — üç ayrı sayı, "halüsinasyon oranı" tek sayısı yerine:**
1. **Extrinsic:** kaynak metinde substring olmayan mention (pilot C1: %8,5).
2. **Değer-dayanaksızlığı:** `property_value ⊄ quote` (pilot C1: %10,1). **Yeni metrik, formda yok.**
3. **Kategori hatası:** alan kuralı ihlali, ör. Peygamber/Allah düğümü (pilot C1: %6,0).

**Şema sapması — iki düzeyde:**
- **Tip düzeyi:** tanımsız node/relation tipi oranı, **ham model çıktısında** (C0/C1'de).
  *Pilotta %0. H2 bu düzeyde trivyal.*
- **Property düzeyi:** şemada olmayan property anahtarı, `data_type`/`enum_values` ihlali,
  kardinalite ihlali. **Asıl drift buradadır ve hiç ölçülmemiş.** H2 bu düzeye taşınmalı.
- **Red kaynaklı recall kaybı:** C2'de reddedilen adayların altın standarda göre kaçı doğruydu.
  *"Sıfır şema-dışı yazım" ancak bu sayıyla birlikte anlamlıdır.*

**ER (K-2/H4):** pairwise P/R/F1; **B-cubed** (Bagga & Baldwin 1998); **CEAF-e** (Luo 2005);
**yanlış-birleştirme (over-merge) oranı — ayrı ve birincil**; duplicate-node oranı (H4 için).

**Kalibrasyon:** LLM güven skorunun **AUC**'u (doğruyu yanlıştan ayırma), reliability diagram,
ECE. *Pilot: AUC 0,626, ECE 0,028, monoton değil. Yani ECE tek başına yanıltıcı — AUC birincil
raporlanmalı.*

**HITL:** yönlendirme politikasına **koşullu** red oranı; **doğrulanmış üçlü başına uzman saniyesi**
(sitenin 3. araştırma sorusu; `decision_events.duration_ms` ile ölçülür); düzenleme oranı; insanlar
arası uyum.

**Maliyet:** token, TL, duvar saati. İlk kurulum ve artımlı güncelleme **ayrı**.

**Tüketim kalitesi:** 60 soruluk bir küme (20 yapısal: "X kimden rivayet etti?"; 20 yol/ağ:
"bu iki isnadın medârı?"; 20 karar: "bu iki Süfyân neden ayrı?"). Aynı küme (i) graf üzerinden,
(ii) çıplak metin + RAG ile cevaplanır. **Bu, "kalıcı katman gerekli mi?" sorusunun tek gerçek testi.**

---

## 4. İstatistik

**Analiz birimi: hadis.** Tasarım eşleştirilmiş (her hadis tüm koşullarda işlenir).

**Birincil analiz — karışık etkili lojistik regresyon (aday düzeyi):**
```
correct ~ condition + model + condition:model + chain_length_z + (1 | hadith) + (1 | narrator_authority_id)
```
`(1|narrator_authority_id)` eklenmesinin gerekçesi: bazı raviler (Ebû Hüreyre, Zührî) çok sayıda
zincirde geçiyor ve hata oranı raviye bağımlı; bu rastgele etki olmadan model hadis-içi
korelasyonu eksik modeller.

**İkincil — hadis düzeyinde F1 üzerinde lineer karışık model.** Güven aralıkları **hadis düzeyinde
cluster bootstrap** ile (B≥2000). Referans uygulama `pilot_isnad.bootstrap_ci`.

**İkili koşul karşılaştırmaları:** eşleştirilmiş permütasyon testi + **Holm** düzeltmesi.
Merdivende 9 basamak var → düzeltme zorunlu.

**Formdaki ANOVA korunur** ama **yardımcı analiz** olarak ve birim **hadis** (30 agrega değil).
Bu, `02b` #5'in karşılığı. `02b`'nin dediği gibi 30 agrega ile ANOVA gücü boşa harcıyor.

**H3 yeniden formüle:** model düzeyinde n=5 ile korelasyon ekolojik. Yerine:
```
human_reject ~ hallucination_label + (1 | hadith) + (1 | model)
```
ve ayrıca **HITL'in halüsinasyon tespitinde duyarlılık/özgüllüğü** (2×2 tablo) raporlanır. Formdaki
"pozitif ve anlamlı ilişki" iddiası bu modelin `hallucination_label` katsayısıyla test edilir —
form metnini değiştirmeye gerek yok, sadece testi doğru kuruyoruz.

**Tekrarlar (`13` soru 12):** platform modellerinde sıcaklık ayarı her zaman mümkün değil
(pilotta `temperature` parametresi modelde desteklenmedi). Karar:
- Açık modeller (vLLM ile servis) için **T=0,7 ile 3 tohum** → örnekleme varyansı ölçülür.
- API modelleri için **3 prompt paraphrase** → prompt duyarlılığı ölçülür.
- İkisi farklı şeyler ölçer ve **ayrı raporlanır**. "3 tekrar" taahhüdü her iki yolla da sağlanır.

### 4.1 Güç analizi (simülasyonla; `08` §5)

Pilotun ampirik parametreleriyle (hadis başına 6,36 mention, hadis düzeyi precision ~ Beta(3,41;0,50)):

| n hadis | Δ=0,03 | Δ=0,05 | Δ=0,10 | Δ=0,15 |
|---|---|---|---|---|
| 100 | 0,32 | 0,66 | **0,98** | 1,00 |
| 350 | 0,76 | 0,97 | 1,00 | 1,00 |
| 500 | **0,87** | 1,00 | 1,00 | 1,00 |

**Sonuç 1:** 500 hadis H1 için **fazlasıyla** yeterli; Δ=0,15 için n=100 bile %98 güç veriyor.
R3 planındaki "500→350 düşürme" istatistiksel olarak tamamen güvenli.
**500'ün gerekçesi güç değil, kapsam ve açık-veri katkısı olmalı — formda böyle yazılmalı.**

**Sonuç 2 — H1 için uyarı:** precision'ın tavanı 1,0; pilotta baz çizgi **0,886**. Mümkün maksimum
artış **+0,114 < 0,15**. H1 ancak baz çizgi *gerçekten zayıf* bir modelle kurulursa anlamlı.
Üç seçenek:
- **(i) Tercih edilen:** H1'i **göreli hata azalması** olarak yeniden ifade et: *"hata oranını
  (1−P) en az %50 düşürür"*. Tavan problemi yok, literatürde standart. Pilottaki C1→C1d geçişi
  bunu zaten sağlıyor: 1−0,877 = 0,123 → 1−1,000 = 0,000.
- **(ii)** Baz çizgiyi açıkça "en zayıf model × şema bilgisi olmayan prompt (C0)" olarak tanımla
  ve +0,15'i orada ara. Bu dürüst ama baz çizgiyi kasten kötüleştirmek gibi görünme riski taşır.
- **(iii)** H1'i olduğu gibi bırak ve **başarısız olma riskini kabul et**. Bir 2209-A projesinde
  hipotezin reddedilmesi başarısızlık değildir — ama bunu rapora böyle yazmak gerekir.

---

## 5. Altın standart ve kör protokol (`02b` #2, #6)

### 5.1 Döngüselliği kıran atama
Form'daki risk gerçek: HITL kararını veren ile altın standardı denetleyen aynı kişi (Prof. Atay).

**Protokol:**
1. **Katman (a)** iki öğrenci kodlayıcı (K1, K2) tarafından, **sistem çıktısını görmeden**,
   ham metinden üretilir. Anlaşmazlıklar üçüncü bir öğrenci (K3) tarafından çözülür.
2. **Katman (b)** otorite eşlemesi: Prof. Atay + bir ikinci ilahiyat kodlayıcısı (lisansüstü
   öğrenci yeter) **sabit bir aday kümesi** üzerinde bağımsız kabul/red verir.
3. **C5 (HITL) koşulunda** karar veren kişi, o hadisin altın standardını üretmemiş olan kişidir.
   Atama tablosu önceden yazılır ve `decision_events.actor_id` ile denetlenir.
4. Etiketleme kılavuzu **sürümlenir**; mutabakat oturumlarının kararları **karar defterine yazılır**
   (dogfooding — `12` §7).

### 5.2 Uyum metrikleri (`02b` #6 doğru)
- **Katman (a):** açık uçlu çıkarımda κ iyi tanımlı değil (sabit öğe kümesi ve negatif sınıf yok).
  **Kodlayıcılar arası karşılıklı F1** raporlanır (IE literatürünün standardı), M1/M2 kriterleriyle.
- **Katman (b):** sabit aday kümesinde kabul/red → **Cohen's κ**. **Formdaki κ ≥ 0,75 hedefi buraya
  bağlanır.** Bu, taahhüdü koruyan ve teknik olarak doğru olan tek okuma.
- İkisi birden raporlanır; form metninde κ'nın hangi katmana ait olduğu netleştirilir.

---

## 6. H4 / K-2 protokolü (pilot ışığında yeniden yazıldı)

Pilot bulgusu: GiraffeGraph'ın mevcut merge key'i (NFKC+casefold) ile Arapça 327 mention'dan
**240 düğüm**; tek bir imlâ katlaması adımı bunu **230**'a düşürüyor (**%4,2**); string tabanlı her
şeyin tavanı **%17,5**. **H4'ün ≥%50 hedefi string yöntemleriyle ulaşılamaz.**

**Revize protokol:**

1. **Baz çizgi B0 = mevcut kod** (`resolution.normalize_text`). Bu zaten implement edilmiş, ölçülmesi
   bedava. *Pilotta ölçüldü.*
2. **B1 = + imlâ/diyakritik katlaması.** Arapça: hareke + alef/ya/ta-marbuta. Türkçe: şapka
   (`â→a`, `û→u`), `İ/ı`. Beklenen kazanç Arapçada %4,2 (ölçüldü); **Türkçede ölçülmeli** —
   formun H4'ü tam olarak bu adım hakkında ve Türkçe rakam yok.
3. **B2 = + fonetik** (Soundex/Metaphone Türkçe uyarlaması). Formda taahhüt; ölçülmeli ama
   beklentiyi düşük tutun.
4. **B3 = + otorite listesine linking** (bağlamsal: zincir komşuluğu + tabaka + vefat yılı).
   **Asıl kazanç burada.** Baz çizgi olarak Wirahman (2026) eşleme korpusu kullanılır.
5. **B4 = + HITL merge onayı.**

**Birincil metrik over-merge oranı olmalı, duplicate-node oranı ikincil.** Gerekçe ölçümle:
örneklemde `سفيان` üç ayrı raviye (Süfyân es-Sevrî, Süfyân b. Uyeyne, Süfyân b. Habîb)
token alt-kümesi olarak eşit uzaklıkta; `ايوب` iki ayrı kişiye; `ابراهيم` altı farklı ada.
Kısa-form birleştirme duplicate oranını düşürür ve **aynı anda zincirin hükmünü bozar.**

**H4 taahhüdünü koruma yolu:** H4'ü **B0→B3** karşılaştırması olarak oku (form "transliterasyon-aware
varlık çözümleme katmanı" diyor; otorite linking bu katmanın parçası olarak sunulabilir).
B0→B1 tek başına %50'yi vermez ve bu formda yazılmamış bir varsayımdı.

---

## 7. Veri sızıntısı (ezber) kontrolü — formda yok, zorunlu

Modeller Kütüb-i Sitte isnadlarını eğitim verisinden ezberlemiş olabilir. Ayırt edici üç test:

| Test | Yöntem | Beklenti |
|---|---|---|
| **T-mask** | İsnadın metinden **silinmesi**, sadece matn verilmesi ve zincir istenmesi | Ezber varsa model yine de doğru zincir üretir → **ezber kanıtı** |
| **T-perturb** | Ravi adlarının sistematik olarak değiştirilmesi (ör. `Süfyân`→`Kâsım`), zincir yapısı korunarak | Ezber varsa model orijinal adı geri getirir |
| **T-obscure** | Kütüb-i Sitte dışı, az bilinen derlemelerden (Sanadset'te 926 kitap var) eşleştirilmiş bir alt küme | Ezber varsa Kütüb-i Sitte ile obscure arasında büyük performans farkı olur |

T-obscure en ucuz ve en bilgilendirici: **Sanadset zaten 926 kitap içeriyor**, örneklemeyi
koleksiyon popülerliğine göre tabakalamak yeterli. Bu testin sonucu yayının en güçlü metodolojik
parçası olabilir; Haque & Islam (2026) bu eksiği alanın açık problemi olarak listeliyor.

---

## 8. Danışmana sorulması gereken dört revizyon

| # | Revizyon | Form metni değişiyor mu? |
|---|---|---|
| R-a | **H1'in göreli hata azalmasına çevrilmesi** (§4.1). Tavan problemi aritmetik | **Evet.** Ama "en az 0,15 mutlak" yerine "hata oranında ≥%50 azalma" daha iddialı *ve* ulaşılabilir |
| R-b | **H2'nin property düzeyine taşınması** (§3.3). Tip düzeyinde pilotta %0 | **Evet**, ama hipotez güçleniyor: trivyal olmaktan çıkıyor |
| R-c | **Model listesinin güncellenmesi** (`02b` #10). Llama-3-8B/Mistral-7B/Qwen2-7B 2024 modelleri | Muhtemelen **hayır** — "aynı ailenin güncel sürümü" gerekçelendirilebilir. Yine de yazılı onay alın |
| R-d | **Karar defteri katmanının eklenmesi** (`12`). Formdaki kapsamı bozmuyor, CORE'a ek mimari katman | Muhtemelen **hayır**; yaygın etki tablosuna bir madde eklenir |

Formdaki iki uydurma referans ve Ji vd.'ye atfedilen sayı (`04a`) ayrıca ve **mutlaka** danışmana
bildirilmeli; bunlar revizyon değil **hata düzeltmesi**.
