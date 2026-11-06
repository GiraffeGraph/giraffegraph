# 5 Sistem tasarımı

Bu bölümde `main` dalında gerçekleştirilen tasarım ele alınmaktadır. Yollar `backend/src/app/` dizinine göredir. Bazı kararlarla, önceki kodun incelenmesi sırasında bulunan kusurlar giderilmiştir (tasarım analizi, 30 Eylül 2026). Tasarımın açıklanmasına yardımcı olduğu durumlarda ilgili kusur da belirtilmektedir.

## 5.1 Tasarım ilkeleri

**Model öneri üretmektedir ve grafa yazamamaktadır.** Sağlayıcı, önerilen düğüm ve ilişkileri döndürmekte; bunlar `CandidateNode` ve `CandidateRelation` satırları olarak `pending` durumunda saklanmaktadır. Tek graf yazma işlemi olan `CanonicalGraphRepository.commit_bundle`, yalnızca `CommitManagementService.commit_run` tarafından çağrılmakta ve yalnızca `validated` adayları almaktadır.

**Her olgu bir alıntı taşımaktadır.** Aday, segment kimliği, alıntı ve isteğe bağlı konumları içeren `EvidenceRef` değerlerini tutmaktadır. Kanıtı olmayan çıkarılmış aday `missing_evidence` olarak işaretlenmektedir. Bu bir denetimdir; saklama kısıtı değildir. İnceleyici böyle bir adayı yine de kabul edebilmekte, elle girilen adaylar ise denetlenmemektedir.

**Denetimler sessizce reddetmek yerine inceleme için işaretlemektedir.** Kaynağa dayandırma, değer, eşik ya da yinelenen aday denetimi başarısız olduğunda durum `review` olarak belirlenmekte ve gerekçe kodu içeren bir inceleme öğesi oluşturulmaktadır. Adayı kullanılamaz bırakan yapısal hatalarda durum `rejected` olarak belirlenmekte; ancak bu hataların her biri doğrulama sonucu olarak saklanmaktadır.

**Her kabul, insan kararı ya da adı kayıtlı bir politika olarak kaydedilmektedir.** Doğrulanmış adayın izi, `review_decisions` içindeki bir satıra ya da adayı geçiren kuralla birlikte `auto_validated` politikasına kadar sürülebilmektedir.

**Alana özgü davranış eklentilerle eklenmekte; motor kodu genel kalmaktadır.** Bölütleme bir `SegmentationStrategy` ile yapılmakta, şema bir şablondan alınmakta ve çıkarım bir `LLMProvider` üzerinden yürütülmektedir. Çıkarım, doğrulama, inceleme ve commit kullanım senaryoları ravi ya da hadis adları içermemektedir. Bunun üç istisnası bulunmaktadır. Doğrulama, metin karşılaştırmasını `domain/hadith/grounding.py` içinden almakta; bu nedenle Arapça katlama her projeye uygulanmaktadır. Zincir okuma modeli (`domain/exploration/chains.py`, `ChainExplorationService`, `/chains` uç noktaları), `Narrator` ve `NARRATED_FROM` tiplerini adlarıyla kullanmaktadır. Eklentiler, `bootstrap/container.py` içinde kodla kaydedilmektedir.

## 5.2 Mimari

Arka uç, dört katmanlı tek bir FastAPI uygulamasıdır. Uygulama ve alan katmanları, altyapı ya da arayüz katmanlarından hiçbir şey içe aktarmamaktadır. Kullanım senaryoları `application/ports/` içindeki protokollere bağımlıdır; altyapı katmanı ise bu protokolleri gerçekleştirmektedir.

```text
  Dashboard (Next.js)             Worker CLI
        | HTTP                        |
        v                             v
+----------------------------------------------------------------------+
| interfaces     FastAPI routers and schemas                           |
+----------------------------------------------------------------------+
| application    use cases: schema, ingestion, extraction, validation, |
|                review, commit, jobs, exploration; ports (protocols)  |
+----------------------------------------------------------------------+
| domain         entities, segmentation strategies, identity keys,     |
|                Arabic normalisation and grounding helpers            |
+----------------------------------------------------------------------+
| infrastructure                                                       |
|   LLM providers        template catalog       persistence            |
|   noop, openai,        blank, story,          in-memory, or          |
|   anthropic,           isnad                  Postgres + Neo4j       |
|   rule_based_isnad                                                   |
+----------------------------------------------------------------------+
        |                                       |
        v                                       v
  Postgres: schemas, source text, runs,    Neo4j: committed nodes and
  candidates, validation results,          edges, links to source units
  review items, decisions, deltas          and segments, graph deltas
```

Postgres, yapılandırmayı, kaynak metni, henüz kabul edilmemiş her şeyi ve denetim izini tutmaktadır. Neo4j ise yalnızca commit edilmiş öğeleri, kaynak birimlerine ve segmentlere geri bağlantılarıyla birlikte tutmaktadır. Depodaki ADR-002 bu ayrımın gerekçesini açıklamaktadır: üst veri yapılandırılmış kayıtlardan oluşmakta, commit edilmiş graf ise yoğun bağlantılar içermekte ve dolaşılarak okunmaktadır. Bu ayrımda aday hiçbir zaman graf deposunda bulunmamaktadır. Bunun bedeli, iki deponun tek bir işlemde güncellenmemesidir (Bölüm 6.9).

Bellekte çalışan arka uç, aynı depo protokollerini sözlüklerle gerçekleştirmektedir. `REPOSITORY_BACKEND`, `postgres` olmadığında varsayılan olarak bu arka uç kullanılmakta; test paketi de aynı arka ucu kullanmaktadır.

## 5.3 Veri modeli

| Varlık | Ana alanlar | Saklandığı yer |
|---|---|---|
| Proje | ad, `template_id`, durum | `projects` |
| Şema sürümü | `version_no`, durum (`draft`, `published`, `active`, `retired`) | `schema_versions` |
| Düğüm tipi | ad, `display_name`, `merge_keys`, `confidence_threshold` (varsayılan 0,5), `extraction_hints` | `node_types` |
| İlişki tipi | ad, `from_type`, `to_type`, `merge_keys`, `confidence_threshold` (varsayılan 0,7) | `relation_types` |
| Özellik | ad, `data_type`, zorunlu, `enum_values` | `property_definitions` |
| Kaynak birimi | `raw_content`, `external_ref`, durum | `source_units` |
| Segment | sıra, metin, üst veri (strateji, zincir numarası, kaynak konumları) | `segments` |
| Koşu | kaynak birimi, şema sürümü, sağlayıcı, model, durum | `processing_runs` |
| Aday düğüm, aday ilişki | tip, özellikler, güven skoru, kanıt referansları, durum; düğümde `merge_key_payload`, ilişkide iki aday düğüm referansı bulunur | `candidate_nodes`, `candidate_relations` |
| Doğrulama sonucu | `candidate_ref`, `rule_code`, ciddiyet, sonuç, mesaj | `validation_results` |
| İnceleme öğesi | `item_type`, `item_ref`, `reason_code`, veri yükü, durum | `review_items` |
| İnceleme kararı | Bölüm 5.7'ye bakınız | `review_decisions` |
| Graf farkı | bir koşuda oluşturulan, birleştirilen ve reddedilen öğe sayıları | `graph_deltas`, `GraphDelta` düğümü |
| Kanonik düğüm | etiketleri `CanonicalNode` ve tip adıdır; anahtarı `project_id`, `node_type`, `merge_key` alanlarıdır | Neo4j |
| Kanonik kenar | bağlantı ilişki tipinin adını taşır; anahtarı `project_id`, `relation_type`, `relation_identity_key` alanlarıdır | Neo4j |

Kanıt referansları, aday satırlarında JSON olarak saklanmaktadır. Yalnızca taslak şema sürümü düzenlenebildiği için bir koşunun tipleri değişmemektedir.

## 5.4 Adım adım boru hattı

Boru hattı, metninde ح zincir geçiş işareti bulunan `Muslim:978` referanslı bir hadis üzerinden açıklanmaktadır. Bölütleyici bu hadis için iki zincir döndürmektedir. Referans etiketlerinde ise üç zincir bulunmaktadır; üçüncü zincir rivayet metni başladıktan sonra başlamakta ve bölütleyici tarafından döndürülmemektedir.

1. **Yükleme.** Metin, `external_ref = "Muslim:978"` değerini taşıyan ve projenin etkin şema sürümüne bağlı bir kaynak birimine dönüştürülmektedir.
2. **Koşuyu başlatma.** `ProcessingRun`, şema sürümünü, sağlayıcıyı ve modeli kaydetmektedir. Kaynak birimi `processing` olarak işaretlenmekte ve bu durumda ikinci bir koşu başlatılamamaktadır.
3. **Bölütleme.** `isnad` stratejisi, bulduğu her zincir için bir segment döndürmektedir. Yeni zincir yalnızca ح işaretinde başlatıldığı için çoğu hadisten tek segment elde edilmektedir. Her segmentin metni, `raw_content[start:end]` alt dizgisinin aynısıdır; konumlar segment üst verisinde saklanmaktadır. Zincir bulunamadığında metnin tamamı, `fallback: whole_text` işaretli tek bir segment olarak kullanılmaktadır.
4. **Çıkarım.** `isnad` stratejisinde motor segment başına bir sağlayıcı çağrısı yapmakta; `paragraphs` stratejisinde ise kaynak biriminin segmentlerini tek çağrıda göndermektedir. Veri yükü, kaynak birimi referansını, ipuçlarıyla birlikte şemayı ve segmenti içermektedir. Yanıt, `StructuredExtractionContract` ile ayrıştırılmaktadır. Tanımsız tip taşıyan düğüm ya da ilişki elenerek şema önerisi olarak kaydedilmekte; bildirilmemiş özellik de aynı biçimde kaldırılmaktadır. Çağrının dışındaki bir segmente atıf yapan, tanımsız düğüm referansı kullanan ya da yanlış tipteki düğümleri bağlayan yanıt, ilgili çağrının başarısız olmasına neden olmaktadır. Farklı çağrılardan gelen, tipi ve birleştirme anahtarı değeri aynı olan düğümler, tüm alıntıları koruyan tek bir adaya dönüştürülmektedir. Koşu ancak bütün çağrılar başarısız olduğunda başarısız sayılmaktadır.
5. **Doğrulama.** `validate_run`, Bölüm 5.5'teki denetimleri uygulamakta, her adayı `validated`, `review` ya da `rejected` durumuna getirmekte ve inceleme öğelerini oluşturmaktadır.
6. **İnceleme.** İnceleyici, açık öğeler hakkında karar vermektedir (Bölüm 5.7). Her karardan sonra bir düğümü bekleyen ilişkiler yenilenmektedir.
7. **Commit.** `commit_run`, hâlihazırda graf farkı, bekleyen adayı veya açık inceleme öğesi bulunan koşuyu reddetmektedir. Ayrıca, doğrulanmış ilişkilerinden birinin uç düğümü doğrulanmamışsa, birleştirme anahtarı değeri eksikse ya da doğrulanmış iki ilişki farklı özelliklerle tek kenara dönüşecekse koşu reddedilmektedir. Diğer durumlarda doğrulanmış adaylar tek bir graf işleminde yazılmakta, fark saklanmakta ve koşu `completed` durumuna geçmektedir.
8. **Okuma.** Zincir uç noktaları, hadisi sıralı zincirleriyle ve her bağlantının alıntısı ve kabul kaydıyla birlikte döndürmektedir.

2 ile 5 arasındaki adımlar ve açık öğesi olmayan koşular için 7. adım, tek istekte çalışabilmektedir (`POST /api/projects/{project_id}/source-units/process`). Ayrıca 4, 5 ve 7. adımlar kuyruklanmış işler olarak da çalışabilmektedir.

## 5.5 Doğrulama denetimleri

| Gerekçe kodu | Tetikleyen durum | Etki | Gerekçe |
|---|---|---|---|
| `node_type_exists`, `relation_type_exists` | Tip şema sürümünde yoktur | Reddedilir | Graf etiketleri yalnızca şemadan gelir; bu duruma yalnızca elle girilen kayıtlarda ulaşılır |
| `required_node_property`, `required_relation_property`, `node_merge_key` | Zorunlu özellik ya da düğümün birleştirme anahtarı değeri eksiktir | Reddedilir | Şemaya göre eksiktir; kimliği olmayan düğüm birleştirilemez |
| `relation_candidate_refs`, `relation_from_type`, `relation_to_type` | Uç düğüm koşuda yoktur ya da düğüm tipi ilişki tipinden farklıdır | Reddedilir | Şemaya uygunluk |
| `relation_dependency_rejected` | Uç düğüm reddedilmiştir | Reddedilir | Kenar her iki düğüme de ihtiyaç duyar |
| `missing_evidence` | Çıkarılmış adayın kanıt referansı yoktur | İncelemeye gider | Alıntısı olmayan olgu kontrol edilemez |
| `quote_not_in_segment` | Alıntı boştur ya da atıf yapılan segmentte bulunamaz | İncelemeye gider | Alıntı uydurulmuş olabilir |
| `value_not_in_quote` | Düğümün dizgi türündeki birleştirme anahtarı değeri hiçbir alıntısında geçmez ve kaynak biriminin `external_ref` değerinden farklıdır | İncelemeye gider | Ad değiştirilmiş ya da uydurulmuş olabilir |
| `property_value_not_allowed` | Dizgi değeri, özelliğin `enum_values` listesinin dışındadır | İncelemeye gider | Değer sapması |
| `node_confidence_threshold`, `relation_confidence_threshold` | Güven skoru tipin eşiğinin altındadır | İncelemeye gider | Model kuşku bildirir |
| `missing_relation_merge_key` | İlişkide bildirilmiş bir birleştirme anahtarının değeri eksiktir | İncelemeye gider | İnceleyici değeri sağlayabilir |
| `relation_dependency_review` | Uç düğüm incelemededir | İncelemeye gider | Kenar düğümünü bekler |
| `potential_duplicate_node`, `potential_duplicate_relation` | Koşunun başka bir adayı aynı kimliği taşır | Biri dışında hepsi incelemeye gider | Tek bir graf öğesine dönüşürler |
| `schema_type_proposal`, `schema_property_proposal` | Çıkarım tanımsız tip ya da bildirilmemiş özellik üretmiştir | Aday elenir ya da özellik kaldırılır; `schema_proposal` tipinde inceleme öğesi oluşturulur | Sapma kaydedilir, çağrı devam eder |
| `candidate_node_valid`, `candidate_relation_valid` | Bütün denetimler geçilmiştir | Doğrulanır | `auto_validated` politikasının dayanağıdır |
| `canonical_node_match`, `canonical_relation_match` | Aynı kimlik zaten grafta vardır | Durum değişmez | İnceleyiciye bağlam sağlar |
| `human_review_decision` | Adayın kayıtlı kararı vardır | Durum karara göre belirlenir | Bölüm 5.7 |

Alıntılar ve değerler, `normalize_for_grounding` uygulandıktan sonra karşılaştırılmaktadır. Bu işlev önce motorun `normalize_text` işlevini (Unicode NFKC, ardışık boşlukların tek boşluğa indirgenmesi, büyük-küçük harf katlama), ardından `normalize_arabic` işlevini uygulamaktadır. İkinci işlev, kısa ünlü ve Kur'an işaretlerini ve uzatma karakterini kaldırmakta, noktalama işaretlerini boşluklarla değiştirmekte ve elif biçimlerini ا, ى harfini ي, ة harfini ه, ؤ harfini و ve ئ harfini ي biçimine katlamaktadır. Karşılaştırma, alt dizgi içerme testidir; boş alıntı hiçbir zaman eşleşmemektedir. İlişki özelliklerinin değerleri ise alıntıyla karşılaştırılmamaktadır.

Başarısız denetim, güven skoru ne olursa olsun her zaman incelemeye yönlendirmektedir. Güven skoru, modelin kendisi hakkında bildirdiği bir sayıdır; bu nedenle şemaya uyan uydurma bir olgu yüksek değer taşıyabilmektedir. Denetimin sonucu bu skora bağlı değildir. Bununla birlikte, başarısızlığın geçerli bir nedeni olabileceğinden aday reddedilmemektedir. Örneğin ada belirli tanımlık ekleyen model, `value_not_in_quote` denetiminden geçememekte ve bu durum hakkında bir insanın karar vermesi gerekmektedir. Bağımlılık yenileme yalnızca bağımlılık gerekçeli öğeleri kapattığı için bu öğeleri açık bırakmaktadır.

Kanıt ve değer denetimleri, yalnızca koşuda başarılı bir çıkarım yürütümü bulunduğunda çalışmaktadır. API üzerinden girilen adaylar ise operatörün yazdığı adaylar olarak ele alınmaktadır.

## 5.6 İlişki kimliği

Önceki kodda kenar, iki uç düğümü ve tipi üzerinden birleştirilmiş, ardından özelliklerinin üzerine yazılmıştır. İki hadiste aynı iki ravi arasındaki iki aktarım tek kenara dönüştürülmüş; ikinci aktarımın hadis referansı ve aktarım ifadesi, ilkinin değerlerinin üzerine yazılmıştır. Adaylar arasındaki yinelenme denetiminde anahtar olarak tüm özellikler kullanıldığından bu aktarımlar iki farklı aday olarak değerlendirilmiş ve inceleme öğesi oluşturulmamıştır. Bu kayıp sessiz biçimde gerçekleşmiştir.

Mevcut tasarımda ilişki tipi `merge_keys` bildirmektedir; bunların, tipte bildirilmiş özelliklerin adları olması gerekmektedir. `build_relation_identity_key`, normalize edilmiş birleştirme anahtarı değerlerini SHA-256 ile özetlemekte; Neo4j ifadesi bu anahtar üzerinden birleştirme yapmaktadır:

```text
MERGE (from_node)-[r:`NARRATED_FROM` {project_id: $project_id,
       relation_type: $relation_type,
       relation_identity_key: $relation_identity_key}]->(to_node)
```

Aday düzeyindeki saptama aynı kimliği kullanmaktadır. `build_candidate_relation_resolution_key`, ilişki tipini, her iki uç düğümün kimlik anahtarlarını ve ilişki kimlik anahtarını bir araya getirmekte; birleştirme anahtarları dışındaki özellikleri dikkate almamaktadır. Dolayısıyla iki aday, tam olarak aynı kenara dönüşecekleri durumda yinelenmiş sayılmaktadır.

Birleştirme anahtarları olmayan tip, düğüm çifti başına tek kenar tutmaktadır. Bununla birlikte, mevcut tasarımda o çift için ikinci bir aday incelemeye yönlendirilmekte; commit işlemi de farklı özelliklerle tek kenara dönüşen iki doğrulanmış ilişkiyi reddetmektedir.

## 5.7 Karar kaydı

Kararlar `review_decisions` içinde saklanmaktadır. Depo protokolü yalnızca `add_decision` ve `list_decisions_by_run` sunmaktadır. Yeniden doğrulama, koşunun inceleme öğelerini değiştirmekte; kararlarını ise değiştirmemektedir.

Karar; inceleme öğesini, koşuyu, öğe tipini ve öğe referansını, eylemi (`accept`, `reject`, `edit`), `reviewer_id` alanını, isteğe bağlı notu, isteğe bağlı `duration_ms` alanını, zamanı ve düzenleme yapıldıysa adayın önceki ve sonraki hâlini saklamaktadır. Düzenleme, adayın bir kopyasına uygulanmakta ve şemaya ve koşudaki yinelenen adaylara karşı kontrol edilmektedir. Reddedilen kararda hiçbir şey saklanmamaktadır. Aynı öğe hakkındaki ikinci karar yeni kayıt olarak eklenmekte ve son karar geçerli sayılmaktadır. Tamamlanmış koşu ise karar kabul etmemektedir.

Otomatik adımlar için insan kararları kesindir. `validate_run` önce kararları okumaktadır. Hakkında karar verilmiş adayın durumu son karara göre belirlenmekte, adaya `human_review_decision` sonucu verilmekte, denetimler atlanmakta ve inceleme öğesi korunmaktadır. Yinelenen adayların ele alınması, hakkında karar verilmiş adayı hiçbir zaman yeniden incelemeye taşımamaktadır. Bağımlılık yenileme de hakkında karar verilmiş ilişkileri atlamaktadır.

Kabul kayıtları, istek geldiğinde `list_acceptance_records` tarafından hesaplanmakta; saklanmamaktadır. Her doğrulanmış aday için kayıt, kabul eden son kararı ya da adayı geçiren kural koduyla birlikte `auto_validated` politikasını içermektedir.

İki sınırlama bulunmaktadır: inceleyici adının kimliği doğrulanmamakta ve karar tek bir koşunun aday kimliğine bağlı tutulmaktadır. Bu nedenle aynı metin üzerinde yeni bir koşu bu kararı yeniden kullanmamaktadır.

## 5.8 İsnad vaka çalışmasının eklentileri

**Bölütleme stratejisi.** `IsnadSegmentation`, kural tabanlı `segment_isnad` işlevini sarmalamaktadır. Kaynak konumlarına eşleme tutarak metni normalize etmekte, ح işaretinde bölmekte, 26 maddelik bir sözlükten aktarım kalıplarını bulmakta ve rivayet metninin ilk ipucunda zinciri bitirmektedir. Strateji, `one_call_per_segment` değerini ayarlamaktadır.

**Şema şablonu.** `isnad` şablonu; `Narrator` (birleştirme anahtarı `name`), `Hadith` (birleştirme anahtarı `hadith_ref`), raviden raviye `NARRATED_FROM` (birleştirme anahtarları `hadith_ref`, `chain_no`, `position`; aktarım ifadesi için `sigha` özelliği) ve raviden hadise `TRANSMITS` tiplerini bildirmektedir. Ayrıca bölütleme stratejisinin adını belirtmektedir. Proje oluşturulurken `apply_template_schema` ayarlandığında bu şablon uygulanmaktadır.

**Kural tabanlı sağlayıcı.** `rule_based_isnad`, dil modeli olmayan koşuldur. İstemi dikkate almamakta, her segment üzerinde aynı bölütleyiciyi çalıştırmakta ve yazıldığı biçimde ad taşıyan ravi düğümleri ile ardışık her çift için bir `NARRATED_FROM` ilişkisi döndürmektedir. `Hadith` düğümleri oluşturmamaktadır. Alıntıları segmentin dilimleridir; dolayısıyla çıktısı, tasarımı gereği kaynağa dayandırma denetimlerinden geçmektedir.

**Çıkarım ipuçları.** Her tip, veri yükünün şema kısmında modele iletilen ipucu dizgilerinden oluşan bir liste taşımaktadır. Bu ipuçlarına "Ravi adını segment metninden birebir kopyala." ifadesi örnek verilebilmektedir.

## 5.9 Tasarım kararları ve alternatifler

| Karar | Değerlendirilen alternatif | Gerekçe |
|---|---|---|
| Kenar kimliğinin ilişki birleştirme anahtarlarından elde edilmesi | Her aktarım olayı için bir düğüm | Genel modelde daha küçük bir değişiklik gerektirir |
| Başarısız denetimin incelemeye yönlendirmesi | Reddetmek ya da güven skoru eşiğinin üzerinde kabul etmek | Ret, geçerli varyantları gizler; eşik ise modelin kendi bildirdiği bir sayıya güvenir |
| Tanımsız tipte tek adayın elenmesi ve bunun kaydedilmesi | Önceden olduğu gibi tüm yanıtı başarısız saymak | Geçerli adaylar korunur ve sapma sayılabilir |
| Yalnızca yeni kayıt eklenen kararlar ve hesaplanan kabul kayıtları | Grafın yeniden kurulduğu bir olay günlüğü | Denetim izi için yeterlidir; yeniden kurma ve geri alma gerçekleştirilmemiştir |
| Zincir segmenti başına tek çağrıyla, modelden önce kullanılabilen kural tabanlı bölütleyici | Zincirleri modelin bulduğu, hadis başına tek çağrı | Birebir alt dizgiler ve konumlar, birbirinden yalıtılmış başarısızlıklar ve modelsiz bir taban çizgisi sağlar. Değerlendirmede çıkarım kalitesine katkı bulunmamıştır (Bölüm 7.5); bu yüzden iki strateji de seçilebilir durumdadır |
| Koşu başına tek graf işlemi | Önceden olduğu gibi düğüm başına tek işlem | Başarısız commit, kısmi graf bırakmaz |

Üç sınırlama bilinçli olarak kabul edilmiştir. Ravi düğümü, harekeler dâhil tam yazılı adıyla tanımlanmaktadır. Bu nedenle graf, aynı adı paylaşan kişileri birleştirmekte ve iki biçimde yazılan tek kişiyi ayırmaktadır. Rivayet metninin sınırından sonra başlayan zincirler, oradaki aktarım edatları çoğunlukla anlatıya ait olduğundan bölütlenmemektedir. Kaynağa dayandırma denetimleri ise yalnızca çıkarım çağrısından gelen adaylara uygulanmaktadır.
