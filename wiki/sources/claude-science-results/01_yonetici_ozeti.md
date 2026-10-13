# 01 — Yönetici özeti (1 sayfa)

## Beş şey, önem sırasıyla

**1. Formdaki üç referans gerçek değil ve merkezî sayı kaynağında yok. Bu en acil iş.**
Al-Khatib & Stein (2024, LREC-COLING) — ACL Anthology'de iki yazarın da böyle bir yayını yok
(Al Khatib'in LREC-COLING 2024'teki tek bildirisi başka konuda). Bulut (2017, İAD 38) ve
Düzenli (2019, MÜİFD 56) — bu başlıklarla hiçbir yayın bulunamadı. Ve formu motive eden cümle —
*"Ji vd. (2023) … açık alan KG çıkarımında halüsinasyon oranlarının %15–%40 aralığında
değişebildiğini raporlamaktadır"* — surveyin 59 sayfalık tam metninde **yok**: metindeki tüm
yüzde ifadeleri 7 tanedir ve hiçbiri bu değil; survey KG çıkarımını bir görev olarak kapsamıyor
("triple" kelimesi 4 kez geçiyor). Doğru künyeler, gerçek ikameler ve düzeltme metni
`04a` + `04b`'de. **Kabul sonrası bir hakem bunu bulursa projenin itibarına mal olur.**

**2. `05`'teki kod denetimi güvenilir; ama daha kötü dört bulgu var.**
17 iddianın koddan doğrulanabilen 15'i **hatasız**, anchor satırları dahil. Ek olarak koddan
doğrulanan yeni bulgular: **(N1)** modelin uyduracağı property anahtarları hiçbir kontrolden
geçmeden `SET n += $properties` ile Neo4j'ye yazılıyor — "sıfır şema-dışı yazım" yalnızca *tip
adları* için doğru; **(N2)** aday-düzeyi duplicate anahtarı properties'i içeriyor, canonical MERGE
anahtarı içermiyor → aynı çift arası iki farklı ilişki adayı ikisi de VALIDATED olup commit'te
**tek kenara çöküyor, ikinci birincinin üzerine yazıyor, hiçbir review item oluşmuyor, bilgi
sessizce kayboluyor**; **(N3)** merge key'i olmayan aday hiç dedup edilmiyor; **(N4)** prompt metni
kodun kendi sözleşmesini yanlış anlatıyor (case-sensitive diyor, kod casefold yapıyor). Detay ve
öncelikli değişiklik listesi `05`.

**3. Pilot koşturuldu: ravi mention çıkarımı için LLM'e gerek yok, ama alan prompt'una var.**
50 hadis, 327 ravi mention, Kütüb-i Sitte'nin 5 koleksiyonu, Sanadset 650K (**CC0** — lisans teyit
edildi). Gevşek eşleşmeyle F1: deterministik isnad ayrıştırıcı (sîga lügati, sıfır token) **0,879**;
GiraffeGraph'ın mevcut şema-only prompt'uyla LLM **0,865** (ΔF1 = −0,017, %95 GA [−0,072, +0,039]);
alan-farkındalıklı prompt'la LLM **0,935**. Prompt'a isnad bilgisi eklemek precision'ı
**+0,125 [+0,084, +0,170]** artırdı ve **tüm** yanlış pozitifleri sıfırladı (39 → 0).
Formdaki en ucuz taahhüt (E-4, 5 prompt şablonu) ölçülen en büyük etkiyi taşıyor.
**Ama uzun zincirlerde LLM çöküyor:** 8–14 ravili hadislerde recall 0,654, ayrıştırıcının
0,776'sının altında; 50 çağrının 6'sı `max_tokens`'ta kesildi. → Deterministik segmentasyon
**önce**, LLM **zincir başına**.

**4. Sitenin ve kodun grounding kapısı yanlış yerde duruyor — ve doğru yer ölçüldü.**
Modelin verdiği **605 kanıt alıntısının 605'i** kaynakta birebir substring. Yani `quote ⊂ segment`
kontrolü (sitenin "ungrounded claims are flagged" sözünün doğal karşılığı) pilotta **hiçbir şey
yakalamıyor**. Ama şema-only koşulda **32/318 adayda (%10,1)** `properties.name` değeri modelin
*kendi* alıntısının içinde geçmiyor (ör. alıntı `حَدَّثَنَا لَيْثٌ` doğru, ad `الليث`).
Kapı `quote ⊂ segment` değil **`property_value ⊂ quote ⊂ segment`** olmalı; GiraffeGraph şu an
**ikisini de** yapmıyor. Bu, koda eklenecek en ucuz ve en yüksek getirili tek kontrol.
Ve LLM'in baskın "halüsinasyonu" uydurma ravi değil **kayda geçmemiş kanonikleştirme** (Arapça
i'râb hâl dönüşümü) — bu, `12`'nin dört olgu sınıfına **beşinci bir sınıf (2b: model kararı)**
eklemeyi gerektiriyor (`02` Saldırı 3).

**5. Dört hipotezden ikisi ölçülmüş biçimde savunulamaz hâlde.**
- **H1 (+0,15 mutlak precision):** pilotta baz çizgi precision **0,886**; tavan 1,0; mümkün maksimum
  artış **+0,114 < 0,15**. Güç değil **aritmetik** sorun. Çözüm: göreli hata azalması olarak yeniden
  ifade et (*"hata oranını ≥%50 düşürür"*) — daha iddialı *ve* ulaşılabilir.
- **H2 (<%5 şema sapması):** pilotun 100 LLM çağrısında tanımsız tip **0**, şema dışı alan **0**.
  Trivyal. Çözüm: H2'yi **property düzeyine** taşı (N1) — orada hiç ölçüm yok.
- **H4 (≥%50 duplicate azalması):** GiraffeGraph'ın gerçek merge key'i 327 mention'ı 240 düğüme
  indiriyor; tek bir imlâ katlaması adımı 230'a (**%4,2**); string tabanlı **her şeyin tavanı %17,5**.
  ≥%50 string yöntemleriyle ulaşılamaz — bu bir dedup değil **otorite listesine linking** işi.
  Ve örneklemde over-merge tuzağı bizzat çıktı: `سفيان` üç ayrı raviye (es-Sevrî, b. Uyeyne,
  b. Habîb) token alt-kümesi olarak eşit uzaklıkta.
- **H3:** model düzeyinde n=5 ile korelasyon ekolojik; aday düzeyinde karışık etkili lojistik
  regresyona çevrilmeli (`03` §4). **Güven skoru yönlendirme için zayıf:** AUC **0,626**, monoton
  değil, 318 adayın 261'i tam olarak 0,90.

**Güç analizi iyi haber:** 500 hadis H1 için fazlasıyla yeterli (Δ=0,15 için n=100 bile %98 güç;
n=500 Δ=0,03'te %87). R3'ün "500→350" B planı istatistiksel olarak güvenli. **500'ün gerekçesi
güç değil kapsam olmalı** ve formda böyle yazılmalı.

## Sentez hipotezi (`12`) tutuyor mu? — Evet, tek bir revizyonla

Dört saldırı denedim. "Yalnız RAG yeter" hipotezi çürütmedi ama kapsamını daralttı: kalıcı katman
ancak yol/ağ sorguları (isnad zinciri, medâr) veya karar soruları varsa haklı — hadiste ikisi de var,
kodda yalnız ikincisi var (yani kodda **sadece karar defteri** haklı, türetilmiş sayfa değil).
"Fazla mühendislik" saldırısı kısmen tuttu: event sourcing'in tamamı değil, **append-only
`decision_events` + içerik-adresli hedef + `rebuild.py`** gerekli. "Dört sınıf yanlış bölünmüş"
saldırısı **tuttu** ve sınıf 2b eklendi. T3 (kararların alt-doğrusal büyümesi) **hâlâ ölçülmemiş**
bir hipotez ve deney merdivenine eklendi.

**Tek en kritik teknik kusur:** `ReviewItem.item_ref = candidate_id`. İçerik-adresli hedef olmadan
5 model × 3 tekrar denemesinde **500 hadislik insan emeği her yeniden çıkarımda sıfırlanır.**
Bu, tek başına projeyi teslim edilemez hâle getirir. `05` C3, P0.

## Bir sonraki üç hafta

1. **İP0 kapısı — dil kararı.** Telifsiz Türkçe hadis kaynağı var mı, varsa isnad kısaltılmış mı?
   50 metinde **ölç**. Bu paketten çözemedim (telifsiz Türkçe kaynak bulunamadı); projenin en
   yüksek riskli açık sorusu ve `03` §1'deki tüm plan buna bağlı.
2. **Formu düzelt** (`04a`) ve danışmana `03` §8'deki dört revizyonu sun.
3. **Mevcut çalışmaları oku ve konumlan:** Wirahman 2026 (arXiv:2607.05424) **K-2'yi büyük ölçüde
   öncelemiş** — Sanadset'teki 185.216 ravi varyantını iki biyografi veritabanına bağlamış, vefat
   yılı yakınlığını (muâsara) sinyal olarak kullanmış, grafı açık yayımlamış. Raja 2026
   (arXiv:2607.24117) isnad–rical çerçevesini bilgi sistemlerine aktarmış. Bu, katkıyı öldürmüyor
   ama **yeniden konumlandırmayı zorunlu kılıyor** (`09` §1): özgün kalan dört şey ablation
   merdiveni, insan-üretimli altın standart, değer-grounding kapısı ve "deterministik parser LLM'i
   geçiyor" bulgusu.

## Dosyalar

`02` tasarım uzayı + optimum mimari · `03` revize deney protokolü · `04a`/`04b` kaynak doğrulama +
BibTeX · `05` kod denetimi + değişiklik listesi · `06` 6 aylık iş planı · `07` açık sorulara
öneriler · `08` pilot raporu · `09` yayın planı · `pilot_isnad.py`, `pilot_results.csv`,
`pilot_summary.json`, `pilot_figure.png`, `pilot_sample.json`
