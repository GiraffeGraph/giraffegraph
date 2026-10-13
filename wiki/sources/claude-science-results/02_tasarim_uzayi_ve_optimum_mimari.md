# 02 — Tasarım uzayı, sentez hipotezinin sınanması ve optimum mimari

> Kural: doğrulanmamış her atıf `[UNVERIFIED]` işaretli. Bu dosyadaki tüm künyeler
> `04b_dogrulanmis_kaynakca.bib` içinde Crossref/arXiv'den çekilmiş hâlleriyle mevcut.
> Ölçülmüş sayılar `08_pilot_raporu.md` ve `pilot_summary.json`'dan.

---

## 0. Sorunun yeniden ifadesi

`01`'deki soru "hangi temsil?" diye kuruluyor. Pilot ve literatür birlikte gösteriyor ki bu **yanlış
eksen**. Temsil (KG / markdown / vektör) bir sorgu-iş-yükü kararıdır ve ucuzdur; yeniden üretilebilir.
Pahalı ve geri dönüşsüz olan üç başka karardır:

1. **Neyin saklanacağı** (kaynaktan türetilebilen mi, yoksa yalnızca insan kararı mı).
2. **Yazma kapısının nerede durduğu** (hangi düzeyde, hangi sinyalle).
3. **İnsan kararlarının neye bağlandığı** (aday kimliğine mi, içerik-adresli hedefe mi).

Bu üçü yanlışsa temsil doğru olsa da katman çürür; bu üçü doğruysa temsil değiştirilebilir. Bu dosyanın
geri kalanı bu iddiayı test ediyor.

---

## 1. Temsil × doğrulama × güncelleme matrisi

### 1.1 Temsil seçenekleri, `01`'deki 9 eksende

Ölçek: **+** güçlü, **o** orta, **−** zayıf. Hücrelerde kanıt tipi parantez içinde:
(ölç) = bu pakette ölçüldü, (lit) = doğrulanmış literatür, (arg) = yapısal argüman, (?) = kanıt yok.

| Temsil | 1 Doğruluk | 2 Kapsam | 3 Tutarlılık | 4 Güncellik | 5 İnsan mal. | 6 Makine mal. | 7 Tüketim | 8 İzlenebilirlik | 9 Aktarılabilirlik |
|---|---|---|---|---|---|---|---|---|---|
| **Şema-kısıtlı KG** (GiraffeGraph) | + (ölç: tip sapması %0) | − (ölç: fail-closed tüm batch'i düşürüyor) | + (arg: kilitli şema) | − (arg: revert yok, invalidation yok) | − (arg: her aday bir karar) | o | + yol/ağ sorguları | o (kenar var, reviewer yok) | o (şema+kural+prompt) |
| **Açık çıkarım + sonradan kanonikleştirme** (EDC) | o (lit) | + (lit: şema kısıtı recall'ı kesmiyor) | o (arg: kanonikleştirme yeni hata kaynağı) | − | o | − (iki geçiş) | + | o | + (şema gerekmez) |
| **Tipli markdown wiki + anchor + linter** | o (lit+ölç: 315/315 anchor çözüldü ama 296 doğrulanamaz) | + | − (ölç: ~35 açık CONFLICT) | − (ölç: aylarca çelişik kalmış) | o | + | + niyet/karar soruları | o (anchor var, kim/ne zaman yok) | + |
| **Yalnız RAG (kalıcı katman yok)** | o (arg: kaynak hep doğru) | + | + (saklanan olgu yok → tutarsızlık yok) | + (bedava) | + (sıfır) | o (sorgu anında) | − yol sorguları, − niyet soruları | − | + |
| **GraphRAG (topluluk özetleri)** | o | + | o | **−−** (lit: artımlı güncelleme kapatıldı; LazyGraphRAG tüm LLM işini sorgu anına atıyor) | + | **−−** (`[UNVERIFIED]` ~375× indeks maliyeti — `06a`'da da doğrulanmamış işaretli) | + global özet soruları | − | o |
| **Bi-temporal KG** (Zep/Graphiti) | o | o | o | + (geçerlilik + kayıt zamanı ayrı) | o | o | + zamansal sorgular | + | o |
| **Nanopublication** (iddia + provenance + yayın bilgisi) | + (arg: her iddia kendi provenance'ıyla) | o | o | o | − (her iddia ayrı yayın nesnesi) | o | o | **+** | + |
| **Olay günlüğü + türetilmiş görünüm** (`12`) | + (arg: kapı olayda) | + (arg: red de bir olay, bilgi kaybolmuyor) | + (arg: görünüm tek kaynaktan) | + (arg: rebuild) | + (arg: karar yeniden kullanılır) | − (rebuild maliyeti) | + (çoklu görünüm) | **+** | + (S ve D sabit kalır) |

**Matristen çıkan tek net şey:** hiçbir temsil dokuz eksende birlikte kazanmıyor, ama **8. eksen
(izlenebilirlik) ve 4. eksen (güncellik) sadece olay-günlüğü ve nanopublication sütunlarında + alıyor**
— ve bu ikisi temsil değil, *kayıt disiplini*. Yani temsil seçimi 9 eksenin 7'sini belirliyor,
kalan 2'sini belirleyen şey ortogonal bir karardır. Bu, `12`'nin lehine ilk delildir.

### 1.2 Doğrulama seçenekleri (ölçülmüş maliyet/getiri)

| Kapı | Ne yakalar | Pilotta yakaladığı | Maliyet | Yanlış pozitif riski |
|---|---|---|---|---|
| **Şema tip doğrulaması** (mevcut kod) | tanımsız node/relation tipi | **0/100 çağrı** | ~0 | fail-closed olduğu için tüm batch kaybı |
| **Şema property doğrulaması** (yok) | uydurma property anahtarı, data_type/enum ihlali, kardinalite | ölçülmedi (pilotta tek property) | ~0 | düşük |
| **`quote ⊂ segment`** (`05` #2'nin önerisi) | uydurma alıntı | **0/605** | ~0 | ~0 |
| **`property_value ⊂ quote`** (kimsede yok) | kayda geçmemiş kanonikleştirme | **32/318 (%10,1)** | ~0 | orta: meşru normalizasyonu da yakalar → *reddetme değil, karar talebi* olmalı |
| **Alan kuralı** (muâsara/likâ/tabaka, Peygamber blocklist) | tarih çelişkisi, kategori hatası | Peygamber/Allah: **19/318** | ~0 (tarih verisi gerektirir) | orta |
| **NLI / entailment** (SummaC, AlignScore) | metinle çelişen iddia | ölçülmedi | model çağrısı/aday | yüksek (kısa isnad span'lerinde NLI zayıf) `[UNVERIFIED bu görevde]` |
| **Atomik olgu doğrulama** (FActScore, SAFE) | uzun-form olgusallık | ölçülmedi | yüksek (aday başına arama+çağrı) | — |
| **LLM-judge** | her şey | ölçülmedi | yüksek | yüksek; `06a`: freshness kararında deterministik çözüm LLM hükmünü 10+ puan geçiyor `[UNVERIFIED — 06a'da da işaretli]` |
| **Güven eşiği ile yönlendirme** (mevcut kod) | — | **AUC 0,626**, monoton değil | ~0 | yüksek: politika modelin skor alışkanlığına bağımlı |
| **Conformal / risk tabanlı yönlendirme** | insan bütçesi sabitken hata garantisi | ölçülmedi | kalibrasyon kümesi | düşük; teorik garanti var (Angelopoulos & Bates 2021) |
| **İnsan** | her şey | ölçülmedi (C5 koşulmadı) | uzman dakikası | — |

**Ölçülmüş sıralama (getiri/maliyet):**
1. **Alan-farkındalıklı prompt** — ΔP = **+0,125** [+0,084, +0,170], maliyet: bir prompt yazma oturumu.
2. **`property_value ⊂ quote` kapısı** — %10,1 yakalama, maliyet ~0.
3. **Alan blocklist'i** (Peygamber/Allah düğüm değil) — %6,0 yakalama, maliyet ~0.
4. **Per-item fail** (fail-closed yerine) — kayıp bilgiyi geri getirir, maliyet: bir refactor.
5. Şema tip kapısı — **ölçülen getiri 0**. Yine de kalmalı (regresyon koruması), ama H2'nin
   bilimsel iddia olarak değeri yok.

### 1.3 Güncelleme stratejileri

| Strateji | Koşul | Sonuç |
|---|---|---|
| **Full rebuild** | S ve P değişmediyse çıktı aynı | LLM'de **çalışmaz**: early cutoff `f(x)==f(x)` ister; LLM byte-eşit üretmez (`06a`, rustc determinizm şartı) |
| **Memoize** (`hash(S_dilimi, P_sürümü)` → dondurulmuş çıktı) | girdi eşitliği çıktıda değil **girdide** kontrol edilir | **Çalışır.** Senkronizasyon hiç denenmez. `12` §1 sınıf-2'nin çekirdeği |
| **Artımlı delta** | invalidation grafı doğruysa | KG'de çalışabilir; GraphRAG'ta çalışmıyor (topluluk özetleri global — bir doküman dokunmadığı toplulukları bile yeniden özetletebilir; Microsoft artımlı güncelleme sorununu kapattı ve LazyGraphRAG ile tüm LLM işini sorgu anına taşıdı) |
| **Hiç güncelleme (RAG)** | — | Güncellik bedava, ama yol/ağ sorguları ve niyet soruları cevaplanamaz |

**Kur'an vakası (`07` C) bu satırların ampirik kanıtı:** kaynak metin 5912 ayette onarıldı, 6236
embedding yeniden üretilmedi. Türetilmiş artefakt kaynak hash'ine bağlı olmadığı için bayatladı
ve kimse fark etmedi. Bu, "memoize et, senkronize etme" kuralının ihlalinin maliyetidir.

---

## 2. `12`'deki sentez hipotezini çürütme denemesi

Hipotez: **V = P(S, D)**; dört olgu sınıfı; kararlar içerik-adresli hedeflere bağlanır; canonical graf
bir materialize edilmiş görünümdür.

Dört ciddi saldırı denedim. Üçü kısmen tuttu, biri hipotezi bir yerde **kırdı**.

### Saldırı 1 — "Yalnız RAG yeter; kalıcı katmana hiç gerek yok"
En güçlü alternatif, çünkü 3., 4. ve 5. eksenleri bedavaya alıyor: saklanan olgu yok → tutarsızlık
yok, bayatlık yok, insan maliyeti yok.

**Nerede kazanıyor:** kod vakası (`01` B). `06a` bunu zaten kabul ediyor — kodda ajanın
`grep`/`read`'i rekabetçidir, çünkü kodun sömürülecek yapısı var (tekil tanımlayıcılar, çağrı grafı).

**Nerede kaybediyor — ve bu ölçülebilir:** iki soru sınıfı RAG ile cevaplanamaz.
(a) **Yol/ağ sorguları:** "Bu iki isnadın ortak halkası (medâr) kim?" Bir retrieval sistemi bunu
cevaplayamaz çünkü cevap hiçbir tek pasajda yazmıyor; graf traversal gerektiriyor. Ortak-halka
analizi hadis biliminin merkezî yöntemidir (Juynboll/Motzki); Alam & Schneider (2021) Sahîh-i
Buhârî ravi ağının **scale-free** olduğunu ve 16 topluluk içerdiğini ölçmüş — bu tür sonuçlar
yalnızca graf temsilinde vardır.
(b) **Niyet/karar soruları:** "Bu iki 'Süfyân' neden ayrı ravi sayıldı?" Cevap hiçbir kaynakta yok;
yalnızca bir insan kararında var.

**Hüküm:** RAG hipotezi çürütmüyor, **kapsamını daraltıyor**. Kalıcı katman ancak (a) yol sorguları
veya (b) karar soruları varsa haklıdır. Hadis vakasında ikisi de var → kalıcı katman haklı.
Kod vakasında (a) zayıf, (b) güçlü → **sadece karar defteri haklı, türetilmiş sayfa haklı değil**
(bu `06a`'nın sonucuyla birebir aynı ve `07` B'deki ~35 CONFLICT kaydı bunun ampirik bedeli).

### Saldırı 2 — "Karar defteri fazla mühendislik; append-only tablo yeter"
`12` §6 bu riski kendisi kabul ediyor. Test: event sourcing'in hangi özelliği **gerçekten** gerekli?

| Özellik | Gerekli mi | Gerekçe |
|---|---|---|
| Append-only karar kaydı | **Evet** | Şu anki `ReviewItem` üzerine yazılıyor; reviewer ve zaman yok → "doğrulanmış üçlü başına uzman dakikası" (**sitenin 3. araştırma sorusu**) ölçülemiyor |
| İçerik-adresli hedef | **Evet** | `ReviewItem.item_ref = candidate_id`. Yeni bir run'da tüm insan emeği sıfırlanıyor. Bu tek başına projeyi öldüren bir kusur: 500 hadislik etiketleme 5 model × 3 tekrar denemesinde yeniden yapılamaz |
| Türetilmiş back-link | Evet (bedava) | `06a` ölçtü: PEP'te CI linter'ı varken bile resiprosite %64; KEP'te 50 forward değerin 3'ü çözülüyor. Türetilen link yapı gereği %100 |
| Tam rebuild | **Hayır (şimdilik)** | Lisans projesi ölçeğinde rebuild scripti yeterli; artımlı materialize gerekmiyor |
| Upcaster / şema evrimi | Hayır | 6 ayda şema bir kez kilitlenecek |
| Redaction yolu | Evet (tasarımda) | `06a` doğru: sonradan eklenemiyor. `bin/ledger redact` deseni kopyalanabilir |

**Hüküm:** hipotez **asgari hâliyle** ayakta, tam hâliyle fazla. Uygulanması gereken şey event
sourcing değil: **append-only `decision_events` tablosu + içerik-adresli hedef + `rebuild.py`**.
Bu, `12` §6'nın kendi "asgari uygulanabilir versiyon"u ile aynı; onu onaylıyorum.

### Saldırı 3 — "Dört olgu sınıfı yanlış bölünmüş" — **bu saldırı tuttu**

`12`'nin sınıf 2'si ("pahalı-türetilebilir: memoize et, asla elle düzenleme") ile sınıf 3'ü ("karar:
bir kez sakla") arasında **pilotun ortaya çıkardığı bir üçüncü şey var**: LLM'in *kendi başına
aldığı kanonikleştirme kararları*.

Ölçüm: adayların **%8,5'inde** (27/318) `properties.name` kaynakta birebir yok; en yaygın hâli
`أَبَا هُرَيْرَةَ` → `ابو هريره` (mansub hâl → ref hâli). Bu:

- **Sınıf 2 değil**, çünkü memoize etmek sorunu çözmüyor: dondurulmuş çıktı *içinde* kayda geçmemiş
  bir karar var. Hash'i doğru, içeriği bir hüküm.
- **Sınıf 3 değil**, çünkü insan vermedi.
- **Sınıf 4 değil**, çünkü deterministik bir kontrol değil, bir dönüşüm.

Bu, `06a`'nın kendi **Metacrap-8** bulgusunun somut hâli: model, "bunu ben karar verdim" diye
işaretleyecek epistemik bir duruma sahip değil. Ve GiraffeGraph mimarisi bu sınıfı görmüyor:
`properties` bir `dict[str, object]`, `ConfigDict(extra="ignore")` ile geliyor ve `SET n += $properties`
ile Neo4j'ye yazılıyor. Kayıt yok, kapı yok.

**Hipotez bu noktada revize edilmeli.** Öneri: **sınıf 2b — "model kararı" (model-asserted
transformation)**.

> **Politika:** model bir değeri kaynak span'den *farklı* verdiğinde bu bir aday değil **karar
> talebi**dir. Kayıt: `{span_hash, verbatim_value, asserted_value, transform_type, model, prompt_sürümü}`.
> Deterministik bir dönüşüm kuralı (ör. Arapça i'râb hâl normalizasyonu) bunu **onaylayabilir** →
> otomatik geçer ve kural sürümüyle deftere yazılır. Kural onaylamazsa → insana gider.
> **Asla sessizce geçmez.**

Bu revizyon hipotezi güçlendiriyor: artık "her giriş ya bir insan ya da açıkça kayıtlı bir politika
tarafından onaylanır" cümlesi (site metninin dürüst hâli, `12` §4) **uygulanabilir** hâle geliyor,
çünkü "politika" somut bir nesne: bir dönüşüm kuralı + sürümü.

### Saldırı 4 — "T3 (kararların alt-doğrusal büyümesi) ölçülmemiş bir umut"
`12` §5 T3'ü "ekonomik çekirdek" ilan ediyor: ikinci bir modelle yeniden çıkarım yapıldığında
içerik-adresli kararların %X'i otomatik yeniden uygulanır.

Pilot bu oranın **üst sınırı** hakkında bir şey söylüyor: iki farklı prompt'la (C1 ve C1d) aynı
50 hadisten çıkan mention kümelerinin kesişimi, C1d'nin 287 adayının **tamamının** referansla
eşleştiği ve C1'in 279'unun eşleştiği bir yapıda. Yani span-düzeyinde hedefler prompt değişse de
büyük ölçüde stabil. Ama bu bir **vekil ölçüm**; T3'ün gerçek testi karar yeniden uygulama oranıdır
ve o ölçülmedi.

**Hüküm:** T3 hâlâ bir hipotez. Ama **ölçülebilir ve ucuz** bir hipotez ve deney merdivenine
eklenmesi gerekiyor (`03` §3, D-T3). Eğer T3 yanlışsa — yani kararlar yeniden çıkarımda yeniden
uygulanamıyorsa — hipotezin ekonomik gerekçesi çöker ve projenin geri kalanı yine de ayakta kalır
(çünkü grounding kapısı ve alan prompt'u T3'ten bağımsız kazanır). Bu, hipotezin **düşme riskinin
sınırlı** olduğu anlamına geliyor, ki iyi bir özellik.

### 2.5 Sonuç: hipotez tutuyor, tek yerde revize edilerek

| `12`'nin iddiası | Hüküm |
|---|---|
| V = P(S, D); temsil bir görünüm kararıdır | **Tutuyor.** Matris §1.1 bunu destekliyor: temsil 7 ekseni belirliyor, izlenebilirlik+güncellik ortogonal kayıt disiplininden geliyor |
| Sınıf 1 (ucuz-türetilebilir) saklanmaz | **Tutuyor ve pilotla güçlendi.** İsnad mention'ları ve zincir sırası deterministik olarak %87,9 F1 / %99,5 sıra uyumuyla türetilebiliyor. Bunları "canonical" saklamak bir önbellek saklamaktır |
| Sınıf 2 memoize edilir, senkronize edilmez | **Tutuyor.** Kur'an vakası ihlalin bedelini gösteriyor |
| Sınıf 3 kararlar bir kez saklanır, içerik-adresli hedefe bağlanır | **Tutuyor ve en kritik madde.** Mevcut kodun `candidate_id`'ye bağlaması, 500 hadislik emeği tek bir yeniden çıkarımda çöpe atıyor |
| Sınıf 4 linter işaretler, onaylamaz | **Tutuyor.** Pilot: `property ⊄ quote` durumunun %10,1'i *meşru* normalizasyondu → reddetme yanlış olurdu, işaretleme doğru |
| Dört sınıf yeterli | **TUTMUYOR.** Sınıf **2b (model kararı)** eklenmeli. Bkz. Saldırı 3 |
| T3: karar defteri alt-doğrusal büyür | **Doğrulanmadı.** Deney merdivenine eklenmeli |

---

## 3. Optimum mimari önerisi

### 3.1 Alan-bağımsız çekirdek (5 bileşen, hepsi zorunlu)

**K1 — İçerik-adresli kaynak deposu (S).**
`source_unit` + `segment`, her biri içerik hash'iyle. Segment **karakter offset'i taşır** (mevcut
kodda yok). Aynı metnin yeni sürümü yeni hash'tir; eski hash silinmez.

**K2 — Sürümlü prosedür kayıtları (P).**
`{parser_sürümü, prompt_sürümü, model_id, kural_seti_sürümü, şema_sürümü}` demeti tek bir
`procedure_version` nesnesi. Her çıkarım kaydı bir P'ye işaret eder. Mevcut kod bunun %70'ine
sahip (`ProcessingRun` + `StructuredPromptDefinition` + `schema_version`); eksik olan tek nesne
hâline getirilmesi.

**K3 — Değişmez çıkarım kayıtları (sınıf 2).**
`extraction_record` anahtarı `hash(segment_hash, procedure_version)`. Aynı anahtar → yeniden
çağrı yok. **Asla elle düzenlenmez.** Mevcut `candidate_nodes` tabloları bunun yerine geçebilir
ama `status` alanı kaldırılmalı: durum bir olayın sonucudur, kaydın özelliği değil.

**K4 — Dört katmanlı yazma kapısı (sınıf 4 + 2b).**
Sıra önemli; her katman **işaretler**, sadece ilk ikisi reddeder:

```
G1  yapı      : JSON kontratı, tanımsız tip → aday bazında RED (batch bazında DEĞİL) + schema_proposal kaydı
G2  grounding : evidence.quote ⊂ segment.text  VE  offset tutarlı → ihlal RED
G3  değer     : property_value ⊂ quote → ihlal ise 2b: dönüşüm kuralı onaylıyorsa otomatik+kayıt,
                onaylamıyorsa REVIEW    ← pilotta %10,1 yakalama, kodda YOK
G4  alan      : DomainRule protokolü (muâsara/likâ/tabaka, blocklist, enum/data_type/kardinalite)
                → REVIEW + gerekçe, asla sessiz RED
```

**K5 — Append-only karar defteri (D) + türetilmiş görünümler (V).**
`decision_events(actor_id, decided_at, duration_ms, target_hash, action, before, after, rationale,
evidence, supersedes, policy_version)`. `target_hash` **içerik-adresli**: `hash(span_hash, mention_text, node_type)`
— aday UUID'si değil. Canonical graf `rebuild(S, D, P)` ile üretilir. **Revert = olayı supersede et
+ yeniden üret.** Back-link'ler saklanmaz, taranarak türetilir.

### 3.2 Alan-özgü eklentiler (üç kanca, hepsi veri/konfigürasyon)

| Kanca | Arayüz | Hadis | Kod tabanı | Kur'an |
|---|---|---|---|---|
| **Segmenter** | `str → [Segment]` | isnad/matn ayrımı + tahvîl bölme + sîga tokenizasyonu (*deterministik, LLM yok*) | tree-sitter sembol sınırları | ayet/sure sınırı (zaten yapısal) |
| **DomainRule** | `Candidate → Verdict{pass, review, reject, reason}` | muâsara (vefat<doğum), likâ kaydı yok, tabaka tutarlılığı, Peygamber/Allah blocklist | anchor çözümleme, SSOT ihlali, "yalnız güncel durum" dil kuralı | edisyon kimliği ↔ etiket tutarlılığı, bayat embedding tespiti |
| **TransformRule** (yeni, sınıf 2b) | `(verbatim, asserted) → bool` | Arapça i'râb hâl normalizasyonu, honorifik temizleme, Türkçe transliterasyon eşdeğerliği | `Foo.cs` ↔ `FooController` kısaltmaları | ASCII bozulması onarımı |

Aktarılabilirlik maliyeti bu üç dosya + şema + promptlardır. `12` T5 tam olarak bunu öngörüyordu.

### 3.3 Temsil kararı, sorgu iş yüküne göre

| Vaka | Baskın sorgu | Görünüm | Neden |
|---|---|---|---|
| **A Hadis** | yol/ağ (zincir, medâr, muâsara kontrolü) | **KG (Neo4j)** + ravi sayfaları | Yol sorguları retrieval ile cevaplanamaz. Alam & Schneider (2021) bu sorgu sınıfının gerçekliğini gösteriyor |
| **B Kod** | "nasıl genişletirim", "neden böyle" | **yalnız karar defteri (ADR) + linter**; türetilmiş sayfa YOK | `06a`'nın sonucu + `07`'deki ~35 CONFLICT kaydı ampirik bedeli |
| **C Kur'an** | provenance, semantik arama | **provenance kaydı + kaynak-hash'e bağlı embedding**; KG opsiyonel | Olay tam olarak invalidation eksikliğiydi |

**Önemli:** üçü aynı S/D/P altyapısını paylaşır, sadece V ve segmenter/kural eklentileri değişir.
Bu, meta-sorunun ("aktarılabilirlik") cevabıdır ve doğrudan test edilebilir.

### 3.4 İsnad için somut modelleme kararı (mevcut kodun kırıldığı yer)

Mevcut kod ilişki MERGE anahtarını `{project_id, relation_type}` olarak kuruyor
(`neo4j/repositories.py:435-438`), yani **aynı çift arasında aynı tipten tek kenar** oluyor ve
özellikler `SET r += $properties` ile üzerine yazılıyor. İsnad için bu yıkıcı: A→B aktarımı 200
farklı hadiste geçiyorsa 200 aktarım olayı tek kenara çöküyor, sîga ve hadis kimliği kayboluyor.

Dahası **aday düzeyi ile canonical düzey tutarsız**: `build_candidate_relation_resolution_key`
(`resolution.py:36-56`) duplicate anahtarına `properties`'i **dahil ediyor**, yani aynı çift arası
farklı özellikli iki ilişki adayı "farklı" sayılıyor ve ikisi de VALIDATED olabiliyor; commit'te
ise tek kenara çöküyorlar. **Bilgi sessizce kaybolur ve hiçbir review item oluşmaz.** Bu, `05`'te
listelenmemiş, koddan doğrulanmış yeni bir bulgudur.

Çözüm: **aktarım olayını reifiye et.**
```
(:Narrator)-[:TRANSMITTED {position}]->(:Transmission {hadith_id, position, sigha, span_hash})-[:TO]->(:Narrator)
```
ya da minimum çözüm: kenar anahtarına `hadith_id` ve `position` ekle. Zincir-düzeyi metrikler
(tam zincir doğruluğu, zincir düzenleme mesafesi) buna bağlı.

### 3.5 Neyi uygulamayın

- **Tam event sourcing / CQRS.** Saldırı 2. Asgari hâli yeter.
- **Artımlı materialize.** 500 hadislik grafta rebuild saniyeler sürer.
- **GraphRAG tarzı topluluk özetleri.** Artımlı güncelleme sorunu çözülmemiş; isnad zaten yapısal,
  topluluk özetine ihtiyaç yok.
- **Kod tabanı için türetilmiş wiki sayfaları.** `06a` bunu zaten gömdü; `07` B ~35 CONFLICT ile
  bedeli ödedi.
- **LLM-judge'ı birincil kapı olarak.** Deterministik kapılar ölçülen işi yapıyor.
- **Güven eşiğini birincil yönlendirme sinyali olarak.** AUC 0,626.

---

## 4. Bu mimarinin kendi kendini çürütme testleri

Mimari yanlışsa aşağıdakilerden biri gözlenir. Bunları deneye koymak, mimariyi savunmaktan daha
değerli:

- **Ç1:** G3 (değer kapısı) yakaladığı ihlallerin çoğunda meşru normalizasyonu engelliyorsa
  (yanlış-pozitif > %70), kapı REVIEW yerine otomatik-dönüşüm olmalı. *Pilotta çapraz tablo
  hesaplandı (`pilot_g3_crosstab.json`): 318 adayın 32'si G3'ü ihlal ediyor (%10,1); bu 32'nin
  **19'u (%59,4)** altın standartla eşleşmeyen gerçek hata, **13'ü (%40,6)** eşleşen — yani meşru
  kanonikleştirme. Kapı ihlallerin %59'unda haklı, %41'inde fazla temkinli → **RED değil REVIEW
  doğru karar**, ve %41'lik kısım TransformRule ile otomatiğe alınabilecek olan kısım.*
- **Ç2:** İçerik-adresli karar yeniden uygulama oranı <%50 ise (T3 yanlış), karar defteri ekonomik
  gerekçesini kaybeder ve `candidate_id` bağlaması kadar kötüdür.
- **Ç3:** Deterministik segmenter + zincir-başına LLM, hadis-başına LLM'den daha kötü recall
  veriyorsa §3.4'teki mimari yanlış. *Pilot bunun tersini gösteriyor: 8+ ravili zincirlerde
  hadis-başına LLM recall 0,654'e düşüyor.*
- **Ç4:** Kod vakasında karar defteri + grep, anchor'lı wiki'den daha kötü cevap veriyorsa
  (niyet soruları dahil), `06a`'nın tezi yanlıştır.
