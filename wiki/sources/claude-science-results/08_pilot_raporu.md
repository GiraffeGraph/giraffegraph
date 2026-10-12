# 08 — Pilot: deterministik isnad ayrıştırıcı ile LLM çıkarımının karşılaştırması

**Bu pilot gerçekten koşturuldu.** Kod `pilot_isnad.py`, örneklem `pilot_sample.json`, sayılar
`pilot_results.csv` ve `pilot_summary.json`, şekil `pilot_figure.png`. Aşağıdaki her sayı bu
dosyalardan okunmuştur; hiçbiri elle yazılmamıştır.

## 1. Veri

| | |
|---|---|
| Kaynak | **Sanadset 650K** (Mghari, Bouras & El Hibaoui 2022, *Data in Brief* 44:108540), Hugging Face aynası `freococo/650k_sanadset`, **lisans CC0-1.0** (dataset kartından teyit) |
| Erişim | 1,43 GB CSV'den HTTP Range ile ~10 MB'lık dilimler; tam dosya indirilmedi |
| Filtre | Kütüb-i Sitte koleksiyonları, `Sanad_Length ≥ 3`, `<SANAD>`+`<NAR>` etiketi mevcut, 120–1400 karakter |
| Örneklem | **50 hadis**, koleksiyon başına 10 (tabakalı), seed=20260930 |
| Koleksiyonlar | Sahîh-i Müslim, Sünen-i Ebû Dâvûd, Câmiu't-Tirmizî, Sünen-i Nesâî, Sünen-i İbn Mâce |
| Referans mention sayısı | **327** (hadis başına ortalama 6,36) |
| Zincir uzunluğu | 3–14 ravi (medyan 6) |

**Sahîh-i Buhârî örneklemde yok.** Range ile taradığım pencerelerde (dosyanın %8,5–%17,5'i)
`صحيح البخاري` satırları çıkmadı; Buhârî'nin *Târîhu'l-kebîr* ve *Edebü'l-müfred*'i çıktı.
Bu, Sanadset'in eksikliği değil benim örnekleme penceremin sınırı; gerçek deneyde tam dosya
indirilip Buhârî dahil edilmeli.

### Referans standardının statüsü — önemli uyarı
Sanadset'in `<NAR>` etiketleri **uzman altın standardı değil**, kaynak derlemelerin kendi
yapılandırmasından türetilmiş **gümüş standarttır**. Gürültüsü ölçülebilir biçimde mevcut:
örneklemde `وَسَعِيدُ بْنُ الْمُسَيَّبِ` gibi başında bağlaç taşıyan mention'lar ve iç içe
`<NAR>` etiketi artıkları var (temizleme adımı `pilot_isnad.clean_mention` içinde). Bu yüzden
aşağıdaki mutlak değerler **sistemler arası karşılaştırma** için kullanılmalı, bir yayında
"gerçek precision" olarak değil.

## 2. Koşullar

| Kod | Koşul | Açıklama |
|---|---|---|
| **Cx** | Deterministik isnad ayrıştırıcı | LLM yok. Sîga lügati (29 lafız: `حدثنا، حدثني، أخبرنا، أنبأنا، سمعت، قرأت على، عن، أن`…) + matn başlangıç ipuçları + tahvîl (`ح`) bölme + `و` ile eş-ravi ayırma + honorifik temizleme. ~210 satır Python, sıfır token. |
| **C1** | LLM + şema-only prompt | **GiraffeGraph'ın gerçek prompt'u** (`14`, `prompt_catalog.py`) ravi şemasına uyarlanmış: tip listesi, JSON kontratı, `evidence_refs.quote`. Few-shot yok, alan talimatı yok, "emin değilsen üretme" yok. |
| **C1d** | LLM + isnad-farkındalıklı prompt | Formdaki **E-4** taahhüdünün somut hâli: isnad/matn ayrımı, sîga lügati, tahvîl kuralı, "adı metinde yazıldığı gibi kopyala, künye/nisbe genişletme, kendi bilginden isim tamamlama", "Peygamber ve Allah düğüm değildir", "belirsizse yaz ama güveni düşür". |

Model: platformun akıl yürütme varsayılanı (`claude-sonnet-5`), `max_tokens` 4000 (gerekirse 8000/16000'e
yükseltildi), sıcaklık ayarı bu modelde desteklenmiyor. **Bu, formda taahhüt edilen 5 açık/kapalı
modelin yerine geçmez** — pilot tek model üzerinde niteliksel örüntüyü gösterir, model etkisini değil.

## 3. Metrikler

Mention düzeyinde **maksimum ağırlıklı ikili eşleştirme** (Hungarian, `scipy.optimize.linear_sum_assignment`)
ile TP/FP/FN. İki eşleşme kriteri:

- **Katı (strict):** normalize edilmiş string birebir eşit. Normalizasyon = harekelerin kaldırılması,
  `أإآٱ→ا`, `ى→ي`, `ة→ه`, tatvîl ve noktalama temizliği, boşluk sıkıştırma.
- **Gevşek (lenient):** birebir eşitlik **veya** biri diğerinin substring'i **veya** içerik-token
  F1 ≥ 0,60.

Ek olarak: **dayanaksızlık** (mention kaynak metinde substring değil), **zincir sırası uyumu**
(eşleşmiş çiftler üzerinde Kendall-tipi konkordans), **hadis düzeyinde cluster bootstrap** %95 GA
(B=2000), ve koşullar arası **eşleştirilmiş bootstrap** fark dağılımı (B=4000).

## 4. Sonuçlar

### 4.1 Ana tablo

| Koşul | Eşleşme | P | R | F1 | F1 %95 GA | F0.5 | dayanaksız | sıra uyumu |
|---|---|---|---|---|---|---|---|---|
| Cx deterministik | katı | 0,621 | 0,636 | 0,628 | [0,572 – 0,683] | 0,624 | 0,000 | 0,993 |
| Cx deterministik | gevşek | 0,869 | 0,890 | **0,879** | [0,848 – 0,910] | 0,873 | 0,000 | 0,995 |
| C1 LLM şema-only | katı | 0,780 | 0,758 | 0,769 | [0,725 – 0,813] | 0,776 | 0,041 | 0,997 |
| C1 LLM şema-only | gevşek | 0,877 | 0,853 | **0,865** | [0,823 – 0,903] | 0,872 | 0,041 | 0,991 |
| C1d LLM isnad-aware | katı | 0,920 | 0,807 | 0,860 | [0,793 – 0,920] | 0,895 | 0,000 | 1,000 |
| C1d LLM isnad-aware | gevşek | **1,000** | 0,878 | **0,935** | [0,876 – 0,979] | 0,973 | 0,000 | 0,993 |

### 4.2 Eşleştirilmiş farklar (gevşek, hadis-düzeyi cluster bootstrap)

| Karşılaştırma | ΔF1 | %95 GA | ΔP | %95 GA |
|---|---|---|---|---|
| LLM şema-only − deterministik | **−0,017** | [−0,072, +0,039] | +0,006 | [−0,063, +0,079] |
| isnad-aware − şema-only | **+0,073** | [+0,008, +0,129] | **+0,125** | [+0,084, +0,170] |
| isnad-aware − deterministik | +0,056 | [−0,006, +0,109] | **+0,131** | [+0,078, +0,187] |

### 4.3 Beş bulgu

**B1 — Ravi mention çıkarımında LLM, deterministik ayrıştırıcıyı geçmiyor.**
Şema-only LLM'in gevşek F1'i deterministik ayrıştırıcıdan **0,017 puan düşük** ve GA sıfırı kapsıyor
(P(Δ≤0) = 0,73). Recall'de deterministik ayrıştırıcı **önde** (0,890 vs 0,853). Yani `13`'teki
9. açık soru — "LLM şart mı?" — bu görev için cevabı **hayır**: mention tespiti ve zincir sırası
deterministik olarak çözülüyor ve **sıfır token maliyetiyle**.

**B2 — En yüksek kaldıraçlı müdahale şema kapısı değil, alan prompt'u.**
Aynı model, aynı şema, aynı veri: sadece prompt'a isnad bilgisi eklemek precision'ı
**+0,125 (GA [+0,084, +0,170])** yükseltti ve **tüm** FP'leri sıfırladı (39 → 0). Formdaki E-4
(5 prompt şablonu) ucuz bir kalem gibi görünüyor ama ölçülen en büyük etki onda.

**B3 — Kod ve sitedeki grounding kapısı, kendi sözünü tutamayacak yerde duruyor.**
- Modelin verdiği **605 kanıt alıntısının 605'i** kaynak metinde birebir substring (C1: 318/318,
  C1d: 287/287). Yani `05` #2'nin önerdiği `quote ⊂ segment.text` kontrolü bu pilotta **hiçbir şey
  yakalamıyor** — bedava geçiş.
- Ama C1'de **32/318 adayda (%10,1)** `properties.name` değeri, modelin kendi verdiği alıntının
  içinde geçmiyor. Örnek: alıntı `حَدَّثَنَا لَيْثٌ` (doğru, birebir), ad `الليث`.
- Ve **27/318'i (%8,5)** kaynak metinde birebir substring **değil**; bunların 17'si eşleşmeyen
  (FP) adaylar, 13'ü (%4,1) token düzeyinde de kaynakta bulunmuyor. Tipik örnek:
  `أَبَا هُرَيْرَةَ` (mansub hâl) → `ابو هريره` (ref hâli) dönüşümü.
- C1d'de bu üç sayının **hepsi 0**: 287/287 ad hem alıntının hem kaynağın içinde birebir geçiyor.

> **Tasarım sonucu:** kapı `quote ⊂ segment` değil **`property_value ⊂ quote ⊂ segment`** olmalı.
> GiraffeGraph şu an **ikisini de** yapmıyor. Bu, koda eklenecek en ucuz ve en yüksek getirili
> tek kontrol (`05_kod_degisiklik_listesi.md` C1).

**B4 — LLM'in asıl "halüsinasyonu" uydurma ravi değil, kayda geçmemiş kanonikleştirme.**
Hata taksonomisi (gevşek eşleşme, FP'ler):

| Koşul | dayanaksız (fabrikasyon/normalizasyon) | Peygamber/Allah ravi sayıldı | span sınırı hatası | parça (aşırı bölme) |
|---|---|---|---|---|
| Cx deterministik | 0 | 6 | 34 | 4 |
| C1 LLM şema-only | **17** | **19** | 1 | 2 |
| C1d LLM isnad-aware | **0** | **0** | **0** | **0** |

(Satır toplamları FP sayısına eşittir: 44 / 39 / 0. "Dayanaksız" kolonu yalnızca *eşleşmeyen*
adayları sayar; §B3'teki %8,5 tüm adaylar üzerindendir — eşleşmiş ama hâli dönüştürülmüş adaylar
da orada sayılır.)

Deterministik ayrıştırıcının hataları **yapısaldır** (isnad/matn sınırı kaçıyor, span matna sızıyor:
`يرخص له فيصلي في بيته...`) — makineyle tespit edilebilir ve deterministik olarak düzeltilebilir.
LLM'in şema-only hataları ise ya **dilbilgisel hâl dönüşümü** (aslında graf için *istenen* bir
kanonikleştirme, ama kaydı tutulmuyor) ya da **alan kuralı eksikliği** (Peygamber düğüm sayılıyor —
bir blocklist'le biten iş). *"%15–%40 halüsinasyon"* türü bir tablo çıkmadı.

**B5 — Tip düzeyinde şema sapması sıfır; H2 önemsiz bir hipotez.**
İki koşulun 100 çağrısında da **tanımsız node_type: 0, tanımsız relation_type: 0, şema dışı alan: 0**.
Güçlü bir modele şema listesi verildiğinde tip sapması *doğrulayıcıdan önce* zaten olmuyor.
`02b` #3 haklı: H2 (<%5 sapma) bu kurulumda trivyal olarak sağlanır.

> Buna karşılık **property düzeyinde** hiçbir koruma yok: `SuggestedNodeContract.properties` bir
> `dict[str, object]` ve `model_config = ConfigDict(extra="ignore")`. Modelin uyduracağı bir property
> anahtarı sessizce kabul edilir ve `SET n += $properties` ile Neo4j'ye yazılır. Pilotta bu tetiklenmedi
> çünkü şemada tek property vardı; 8 varlık tipli Hadith Schema'da tetiklenecek. **Gerçek drift riski
> tiplerde değil, property'lerde ve orada hiç ölçüm yok.**

### 4.4 Uzun ve paralel zincirler: üç koşulun hepsi düşüyor, LLM en çok

| Zincir uzunluğu | n | Cx recall | C1 recall | C1d recall |
|---|---|---|---|---|
| 3–5 | 19 | 0,933 | 0,921 | **1,000** |
| 6–7 | 21 | 0,954 | 0,893 | 0,977 |
| 8–14 | 10 | **0,776** | 0,748 | **0,654** |

**Üç koşulun hepsi uzun zincirlerde recall kaybediyor** — 3–5'ten 8–14'e düşüş: deterministik
ayrıştırıcı −0,157, şema-only LLM −0,174, isnad-aware LLM **−0,346**. Yani fark mutlak seviyede
değil **bozulma hızında**: isnad-aware LLM kısa zincirlerde kusursuz (1,000) ama uzun zincirlerde
her ikisinin de altına düşüyor (0,654 < 0,748 < 0,776).

Kaçırılan mention'ların zincirdeki bağıl konumu: deterministik ayrıştırıcıda 0,49 (rastgele,
beklenen 0,50), LLM'de **0,76 / 0,69** — kayıplar **zincirin sonunda** toplanıyor. 8+ ravili
hadislerde isnad-aware LLM recall'i 0,654'e düşüyor, deterministik ayrıştırıcının 0,776'sının altına.
Ayrıca **50 çağrının 6'sı (%12)** `max_tokens` sınırında kesildi (her iki koşulda da), yani JSON
kontratı bozuldu — `05` #17'de uyarılan tek-çağrı tasarımı 50 hadis ölçeğinde bile patlıyor.

> **Mimari sonuç:** LLM'i hadis başına değil **zincir başına** çağırın. Deterministik ön işleme
> (isnad/matn ayrımı + tahvîl bölme + segmentasyon) **önce** gelmeli; LLM'in girdisi tek bir zincir
> olmalı. Bu hem recall hem token maliyeti hem kesilme riskini birlikte çözer.

### 4.5 Güven skoru bir yönlendirme sinyali değil

C1'de 318 adayın güven dağılımı **6 farklı değerden** oluşuyor ve **261'i (%82) tam olarak 0,90**.

| Güven | n | gerçekten doğru |
|---|---|---|
| < 0,80 | 12 | 0,667 |
| 0,80–0,89 | 13 | **0,385** |
| 0,90–0,94 | 261 | 0,904 |
| ≥ 0,95 | 32 | 0,906 |

**Monoton değil** — 0,80–0,89 bandı 0,90 bandından *daha kötü*. Doğruyu yanlıştan ayırma gücü
**AUC = 0,626** (n⁺=278, n⁻=40). ECE (4 bin) = 0,028, yani model *ortalamada* doğru kalibre
görünüyor; ama **ayırt edici değil.** GiraffeGraph'ın yönlendirme politikası tam olarak bu skora
dayanıyor (`pipeline_management.py:302-317`): eşik 0,5 ise hiçbir şey insana gitmez; eşik 0,95 ise
neredeyse her şey gider. **Politika, modelin skor kullanım alışkanlığının rehinesi.** `06a`'daki
Metacrap-8 argümanının ölçülmüş hâli.

### 4.6 H4'ün estimand'ı yanlış (Arapça üzerinde ölçüm)

GiraffeGraph'ın **gerçek** merge key normalizasyonu (`domain/shared/resolution.py:96-101`:
NFKC + trim + boşluk sıkıştırma + casefold) 327 referans mention'a uygulandı:

| | düğüm sayısı |
|---|---|
| GiraffeGraph merge key (mevcut kod) | **240** |
| + harekelerin/imlânın katlanması (tek normalizasyon adımı) | **230** |
| kısa-form (token alt-kümesi) adayları da birleştirilse | 198 |

- Tek bir normalizasyon adımının kazandırdığı: **%4,2** duplicate-node azalması.
- String tabanlı her şeyin tavanı: **%17,5**.
- **H4 hedefi ≥%50. String yöntemleriyle ulaşılamaz.** Kalan duplikasyon string düzeyinde değil
  **kimlik düzeyinde**: `سعيد بن المسيب` ile `ابن المسيب` aynı kişidir ve hiçbir string yöntemi
  bunu güvenle birleştiremez.
- Ve kısa-form birleştirme tam olarak **over-merge'ün yaşadığı yer**. Örneklemde bizzat çıktı:
  `سفيان` ⊂ {`سفيان بن سعيد الثوري`, `سفيان بن عيينه`, `سفيان بن حبيب`} — tek başına "Süfyân"
  üç ayrı raviye eşit uzaklıkta. `08_hadith_domain_primer`'ın teorik örneği 50 hadiste gerçekleşti.
  Benzer tuzaklar: `ايوب` ⊂ {`ابي ايوب الانصاري`, `سعيد بن ابي ايوب`}, `ابراهيم` ⊂ 6 farklı ad.

> **Sonuç:** K-2/H4 bir **deduplication** işi değil, bir **otorite listesine entity linking** işidir
> (`02b` #9 doğru) ve metriği duplicate-node oranı değil **over-merge oranı** olmalıdır.
> Ayrıca Wirahman (2026, arXiv:2607.05424, sunum 2026-06-30) bunu Sanadset üzerinde zaten yaptı:
> 185.216 tekil ravi varyantını iki biyografi veritabanına bağlıyor (Hadithtransmitters/Hawramani
> 100.915 kayıt; Muslimscholars 25.247 kayıt), **vefat yılı yakınlığını** (muâsara) ad benzerliği ve
> güvenilirlik derecesi polaritesiyle birlikte ağırlıklı sinyal olarak kullanıyor, HIGH/MED/LOW güven
> bantlarıyla ve 185.216 düğümlü / 814.093 kenarlı grafla açık yayımlıyor.
>
> *Provenans:* bu paragraftaki sayıların tamamı arXiv Atom API'sinden çekilip `arxiv_records.json`
> dosyasına kaydedilen **özet (abstract) metninden** alınmıştır. Makalenin tam metni okunmadı;
> yöntem ayrıntıları, eşleme kalitesi ve HIGH/MED bantlarının doğruluğu `[UNVERIFIED]` — İP0'da
> okunmalı.

**Not:** bu ölçüm **Arapça** üzerinedir. Arapçadaki normalizasyon problemi (hareke + i'râb hâl sonları)
formdaki Türkçe problemden (`Ebû` vs `Ebu` — şapka) **farklıdır**. Türkçe H4 baz çizgisi Türkçe veriyle
ölçülmeli; protokolü `03_revize_deney_protokolu.md` §6'da.

## 5. Güç analizi (500 hadis yeter mi?)

Pilotun ampirik parametreleriyle simülasyon: hadis başına mention ~ Poisson(6,36); hadis düzeyinde
precision ~ Beta(3,41; 0,50) (pilot momentlerinden, ortalama 0,886, sd 0,151); eşleştirilmiş tasarım;
test = hadis düzeyinde cluster bootstrap %95 GA'nın sıfırı dışlaması. 400 replikasyon/hücre.

| n hadis | Δ=0,02 | Δ=0,03 | Δ=0,05 | Δ=0,10 | Δ=0,15 |
|---|---|---|---|---|---|
| 100 | 0,19 | 0,32 | 0,66 | **0,98** | 1,00 |
| 200 | 0,35 | 0,56 | 0,90 | 1,00 | 1,00 |
| 350 | 0,49 | 0,76 | **0,97** | 1,00 | 1,00 |
| 500 | 0,59 | **0,87** | 1,00 | 1,00 | 1,00 |

**İki sonuç:**

1. **İstatistik gücü bağlayıcı kısıt değil.** H1'in hedefi Δ=0,15; onun için **n=100 bile %98 güç**
   veriyor. 500 hadis, Δ=0,03 gibi *çok* küçük etkileri bile yakalar. Yani 500 hadislik etiketleme
   yükünün gerekçesi güç değil, **kapsam** (koleksiyon/tabaka çeşitliliği) ve **açık veri katkısı**
   olmalı — formda bu böyle gerekçelendirilmiyor.
2. **Ama H1 aritmetik olarak imkânsıza yakın.** Baz çizgi precision pilotta **0,886**. Precision'ın
   tavanı 1,0. Yani mümkün olan maksimum artış **+0,114 < 0,15**. H1 ancak baz çizgi gerçekten
   kötü bir modelle (ör. Llama-3-8B, Türkçe, şema-only) kurulursa anlamlı olur — **ve ekip o baz
   çizgiyi hiç ölçmemiş.** H1'i savunmanın tek dürüst yolu: baz çizgiyi *en zayıf* modelle tanımlamak
   ve bunu formda açıkça yazmak; ya da hedefi **relative error reduction** (ör. "hata oranını ≥%50
   düşürür") olarak yeniden ifade etmek. İkincisi tavan problemi olmayan ve literatürde standart olan
   ifadedir.

## 6. Bu pilotun ölçmediği şeyler (dürüst boşluklar)

- **Tek model.** Model etkisi, açık modellerin davranışı, JSON-mode farkları ölçülmedi.
- **Arapça.** Türkçe meal davranışı ölçülmedi. Türkçe meallerde isnadın kısaltılıp kısaltılmadığı
  `[UNVERIFIED]` olarak kaldı — Türkçe telifsiz bir meal/hadis derlemesi bulunamadığı için test
  edilemedi. Bu, form R2 riski için kritik ve **ilk iki hafta içinde çözülmesi gereken şey**.
- **Gümüş standart.** Uzman hükmü yok; otorite ID düzeyinde eşleşme (katman b) hiç ölçülmedi.
- **İnsan maliyeti.** HITL koşulu (C5) koşulmadı; doğrulanmış üçlü başına uzman dakikası ölçülmedi.
- **İlişki düzeyi.** `NARRATED_FROM` üçlülerinin P/R'si ayrıca ölçülmedi; zincir sırası uyumu
  (0,99) bunun için bir vekil ama yerine geçmez.
- **Veri sızıntısı.** Modelin Kütüb-i Sitte isnadlarını ezberlemiş olup olmadığı test edilmedi
  (protokol `03` §7).
