# 5 Sistem tasarımı

Bu bölümde `main` dalında gerçekleştirilen tasarımı anlatıyoruz. Yollar `backend/src/app/` dizinine göredir. Bazı kararlar, önceki kodun incelemesinde bulunan kusurları giderir (tasarım analizi, 30 Eylül 2026). Tasarımı açıklamaya yardımcı olduğunda ilgili kusuru belirtiyoruz.

## 5.1 Tasarım ilkeleri

**Model önerir ve grafa yazamaz.** Sağlayıcı, önerilen düğüm ve ilişkileri döndürür; bunlar `CandidateNode` ve `CandidateRelation` satırları olarak `pending` durumunda saklanır. Tek graf yazma işlemi olan `CanonicalGraphRepository.commit_bundle`, yalnızca `CommitManagementService.commit_run` tarafından çağrılır ve yalnızca `validated` adayları alır.

**Her olgu bir alıntı taşır.** Aday, `EvidenceRef` değerleri tutar: segment kimliği, alıntı ve isteğe bağlı konumlar. Kanıtı olmayan çıkarılmış aday `missing_evidence` olarak işaretlenir. Bu bir kontroldür, saklama kısıtı değildir: inceleyici böyle bir adayı yine de kabul edebilir; elle girilen adaylar ise kontrol edilmez.

**Kontroller sessizce reddetmek yerine inceleme için işaretler.** Başarısız kaynağa dayandırma, değer, eşik ya da yinelenen aday kontrolü, durumu `review` yapar ve gerekçe kodu içeren bir inceleme öğesi oluşturur. Adayı kullanılamaz bırakan yapısal hatalar durumu `rejected` yapar; ancak her biri doğrulama sonucu olarak saklanır.

**Her kabul, insan kararı ya da adı kayıtlı bir politika olarak kaydedilir.** Doğrulanmış adayın izi, `review_decisions` içindeki bir satıra ya da adayı geçiren kuralla birlikte `auto_validated` politikasına kadar sürülebilir.

**Alana özgü davranış eklentilerle eklenir; motor kodu genel kalır.** Bölütleme bir `SegmentationStrategy` ile yapılır, şema bir şablondan gelir ve çıkarım bir `LLMProvider` üzerinden yürür. Çıkarım, doğrulama, inceleme ve commit kullanım senaryoları ravi ya da hadis adları içermez. Üç istisna vardır. Doğrulama, metin karşılaştırmasını `domain/hadith/grounding.py` içinden alır; bu yüzden Arapça katlama her projeye uygulanır. Zincir okuma modeli (`domain/exploration/chains.py`, `ChainExplorationService`, `/chains` uç noktaları), `Narrator` ve `NARRATED_FROM` tiplerini adlarıyla kullanır. Eklentiler, `bootstrap/container.py` içinde kodla kaydedilir.

## 5.2 Mimari

Arka uç, dört katmanlı tek bir FastAPI uygulamasıdır. Uygulama ve alan katmanları, altyapı ya da arayüz katmanlarından hiçbir şey içe aktarmaz: kullanım senaryoları `application/ports/` içindeki protokollere bağımlıdır, altyapı katmanı ise bunları gerçekleştirir.

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

Postgres, yapılandırmayı, kaynak metni, henüz kabul edilmemiş her şeyi ve denetim izini tutar. Neo4j, yalnızca commit edilmiş öğeleri, kaynak birimlerine ve segmentlere geri bağlantılarıyla birlikte tutar. Depodaki ADR-002 bunun gerekçesini verir: üst veri yapılandırılmış kayıtlardan oluşur; commit edilmiş graf ise yoğun bağlantılıdır ve dolaşılarak okunur. Bu ayrımda aday hiçbir zaman graf deposunda bulunmaz. Bedeli, iki deponun tek bir işlemde güncellenmemesidir (Bölüm 6.9).

Bellekte çalışan arka uç, aynı depo protokollerini sözlüklerle gerçekleştirir. `REPOSITORY_BACKEND`, `postgres` olmadığında varsayılan olarak bu arka uç kullanılır; test paketi de onu kullanır.

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

Kanıt referansları, aday satırlarında JSON olarak saklanır. Yalnızca taslak şema sürümü düzenlenebildiği için bir koşunun tipleri değişmez.

## 5.4 Adım adım boru hattı

Metninde ح zincir geçiş işareti bulunan `Muslim:978` referanslı bir hadisi izliyoruz. Bölütleyici bu hadis için iki zincir döndürür. Referans etiketleri üç zincir verir: üçüncüsü rivayet metni başladıktan sonra başlar ve bölütleyici onu döndürmez.

1. **Yükleme.** Metin, `external_ref = "Muslim:978"` değerini taşıyan ve projenin etkin şema sürümüne bağlı bir kaynak birimi olur.
2. **Koşuyu başlatma.** `ProcessingRun`, şema sürümünü, sağlayıcıyı ve modeli kaydeder. Kaynak birimi `processing` olarak işaretlenir; bu durumda ikinci bir koşu başlatılamaz.
3. **Bölütleme.** `isnad` stratejisi, bulduğu her zincir için bir segment döndürür. Yeni zinciri yalnızca ح işaretinde başlatır; bu yüzden çoğu hadis tek segment verir. Her segmentin metni, `raw_content[start:end]` alt dizgisinin aynısıdır; konumlar segment üst verisinde saklanır. Zincir bulunamazsa metnin tamamı, `fallback: whole_text` işaretli tek segment olur.
4. **Çıkarım.** `isnad` stratejisinde motor segment başına bir sağlayıcı çağrısı yapar; `paragraphs` stratejisinde ise kaynak biriminin segmentlerini tek çağrıda gönderir. Veri yükü, kaynak birimi referansını, ipuçlarıyla birlikte şemayı ve segmenti içerir. Yanıt, `StructuredExtractionContract` ile ayrıştırılır. Tanımsız tip taşıyan düğüm ya da ilişki elenir ve şema önerisi olarak kaydedilir; bildirilmemiş özellik de aynı biçimde kaldırılır. Çağrının dışındaki bir segmente atıf yapan, tanımsız düğüm referansı kullanan ya da yanlış tipteki düğümleri bağlayan yanıt, o çağrıyı başarısız kılar. Farklı çağrılardan gelen, tipi ve birleştirme anahtarı değeri aynı olan düğümler, tüm alıntıları koruyan tek bir aday olur. Koşu ancak bütün çağrılar başarısız olursa başarısız olur.
5. **Doğrulama.** `validate_run`, Bölüm 5.5'teki kontrolleri uygular, her adayı `validated`, `review` ya da `rejected` durumuna getirir ve inceleme öğelerini oluşturur.
6. **İnceleme.** İnceleyici, açık öğeler hakkında karar verir (Bölüm 5.7). Her karardan sonra bir düğümü bekleyen ilişkiler yenilenir.
7. **Commit.** `commit_run`, hâlihazırda graf farkı, bekleyen adayı, açık inceleme öğesi, uç düğümü doğrulanmamış doğrulanmış ilişkisi, birleştirme anahtarı değeri olmayan doğrulanmış ilişkisi ya da farklı özelliklerle tek kenara dönüşecek iki doğrulanmış ilişkisi bulunan koşuyu reddeder. Aksi durumda doğrulanmış adaylar tek bir graf işleminde yazılır, fark saklanır ve koşu `completed` durumuna geçer.
8. **Okuma.** Zincir uç noktaları, hadisi sıralı zincirleriyle ve her bağlantının alıntısı ve kabul kaydıyla birlikte döndürür.

2 ile 5 arasındaki adımlar ve açık öğesi olmayan koşular için 7. adım, tek istekte çalışabilir (`POST /api/projects/{project_id}/source-units/process`). 4, 5 ve 7. adımlar kuyruklanmış işler olarak da çalışabilir.

## 5.5 Doğrulama kontrolleri

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
| `candidate_node_valid`, `candidate_relation_valid` | Bütün kontroller geçilmiştir | Doğrulanır | `auto_validated` politikasının dayanağıdır |
| `canonical_node_match`, `canonical_relation_match` | Aynı kimlik zaten grafta vardır | Durum değişmez | İnceleyiciye bağlam sağlar |
| `human_review_decision` | Adayın kayıtlı kararı vardır | Durum karara göre belirlenir | Bölüm 5.7 |

Alıntılar ve değerler, `normalize_for_grounding` uygulandıktan sonra karşılaştırılır. Bu işlev önce motorun `normalize_text` işlevini (Unicode NFKC, ardışık boşlukların tek boşluğa indirgenmesi, büyük-küçük harf katlama), ardından `normalize_arabic` işlevini uygular. İkincisi, kısa ünlü ve Kur'an işaretlerini ve uzatma karakterini kaldırır, noktalama işaretlerini boşluklarla değiştirir ve elif biçimlerini ا, ى harfini ي, ة harfini ه, ؤ harfini و ve ئ harfini ي biçimine katlar. Karşılaştırma, alt dizgi içerme testidir; boş alıntı hiçbir zaman eşleşmez. İlişki özelliklerinin değerleri alıntıyla karşılaştırılmaz.

Başarısız kontrol, güven skoru ne olursa olsun her zaman incelemeye yönlendirir. Güven skoru, modelin kendisi hakkında bildirdiği bir sayıdır; bu yüzden şemaya uyan uydurma bir olgu yüksek değer taşıyabilir. Kontrolün sonucu buna bağlı değildir. Aday reddedilmez de; çünkü başarısızlığın geçerli bir nedeni olabilir: ada belirli tanımlık ekleyen model, `value_not_in_quote` kontrolünden geçemez ve bu durum hakkında bir insan karar vermelidir. Bağımlılık yenileme yalnızca bağımlılık gerekçeli öğeleri kapattığı için bu öğeleri açık bırakır.

Kanıt ve değer kontrolleri, yalnızca koşuda başarılı bir çıkarım yürütümü bulunduğunda çalışır; API üzerinden girilen adaylar operatörün yazdığı adaylar olarak ele alınır.

## 5.6 İlişki kimliği

Önceki kodda kenar, iki uç düğümü ve tipi üzerinden birleştiriliyor, ardından özelliklerinin üzerine yazılıyordu. İki hadiste aynı iki ravi arasındaki iki aktarım tek kenar oluyor; ikinci aktarım, ilkinin hadis referansını ve aktarım ifadesini değiştiriyordu. Adaylar arasındaki yinelenme kontrolü, anahtar olarak tüm özellikleri kullanıyordu; bu yüzden iki farklı aday görüyor ve inceleme öğesi oluşturmuyordu. Kayıp sessizdi.

Artık ilişki tipi `merge_keys` bildirir; bunlar, tipte bildirilmiş özelliklerin adları olmalıdır. `build_relation_identity_key`, normalize edilmiş birleştirme anahtarı değerlerini SHA-256 ile özetler; Neo4j ifadesi bu anahtar üzerinden birleştirir:

```text
MERGE (from_node)-[r:`NARRATED_FROM` {project_id: $project_id,
       relation_type: $relation_type,
       relation_identity_key: $relation_identity_key}]->(to_node)
```

Aday düzeyindeki saptama aynı kimliği kullanır. `build_candidate_relation_resolution_key`, ilişki tipini, her iki uç düğümün kimlik anahtarlarını ve ilişki kimlik anahtarını bir araya getirir; birleştirme anahtarları dışındaki özellikleri dikkate almaz. Dolayısıyla iki aday, tam olarak aynı kenara dönüşecekleri durumda yinelenmiş sayılır.

Birleştirme anahtarları olmayan tip, düğüm çifti başına tek kenar tutar. Ancak o çift için ikinci bir aday artık incelemeye gider; commit işlemi de farklı özelliklerle tek kenara dönüşen iki doğrulanmış ilişkiyi reddeder.

## 5.7 Karar kaydı

Kararlar `review_decisions` içinde saklanır. Depo protokolü yalnızca `add_decision` ve `list_decisions_by_run` sunar. Yeniden doğrulama, koşunun inceleme öğelerini değiştirir, kararlarını değiştirmez.

Karar; inceleme öğesini, koşuyu, öğe tipini ve öğe referansını, eylemi (`accept`, `reject`, `edit`), `reviewer_id` alanını, isteğe bağlı notu, isteğe bağlı `duration_ms` alanını, zamanı ve düzenleme yapıldıysa adayın önceki ve sonraki hâlini saklar. Düzenleme, adayın bir kopyasına uygulanır ve şemaya ve koşudaki yinelenen adaylara karşı kontrol edilir; reddedilen karar hiçbir şey saklamaz. Aynı öğe hakkındaki ikinci karar yeni kayıt olarak eklenir ve son karar geçerlidir. Tamamlanmış koşu karar kabul etmez.

Otomatik adımlar için insan kararları kesindir. `validate_run` önce kararları okur: hakkında karar verilmiş aday, durumunu son karardan alır, `human_review_decision` sonucunu alır, kontrolleri atlar ve inceleme öğesini korur. Yinelenen adayların ele alınması, hakkında karar verilmiş adayı hiçbir zaman yeniden incelemeye taşımaz; bağımlılık yenileme de hakkında karar verilmiş ilişkileri atlar.

Kabul kayıtları, istek geldiğinde `list_acceptance_records` tarafından hesaplanır; saklanmaz. Her doğrulanmış aday için kayıt, kabul eden son kararı ya da adayı geçiren kural koduyla birlikte `auto_validated` politikasını içerir.

İki sınır vardır: inceleyici adının kimliği doğrulanmaz ve karar tek bir koşunun aday kimliğine bağlıdır; bu yüzden aynı metin üzerinde yeni bir koşu bu kararı yeniden kullanmaz.

## 5.8 İsnad vaka çalışmasının eklentileri

**Bölütleme stratejisi.** `IsnadSegmentation`, kural tabanlı `segment_isnad` işlevini sarmalar. Kaynak konumlarına eşleme tutarak metni normalize eder, ح işaretinde böler, 26 maddelik bir sözlükten aktarım kalıplarını bulur ve rivayet metninin ilk ipucunda zinciri bitirir. Strateji, `one_call_per_segment` değerini ayarlar.

**Şema şablonu.** `isnad` şablonu; `Narrator` (birleştirme anahtarı `name`), `Hadith` (birleştirme anahtarı `hadith_ref`), raviden raviye `NARRATED_FROM` (birleştirme anahtarları `hadith_ref`, `chain_no`, `position`; aktarım ifadesi için `sigha` özelliği) ve raviden hadise `TRANSMITS` tiplerini bildirir. Bölütleme stratejisinin adını da belirtir. Proje oluşturma, `apply_template_schema` ayarlandığında bu şablonu uygular.

**Kural tabanlı sağlayıcı.** `rule_based_isnad`, dil modeli olmayan koşuldur. İstemi dikkate almaz, her segment üzerinde aynı bölütleyiciyi çalıştırır ve yazıldığı biçimde ad taşıyan ravi düğümleri ile ardışık her çift için bir `NARRATED_FROM` ilişkisi döndürür. `Hadith` düğümleri oluşturmaz. Alıntıları segmentin dilimleridir; dolayısıyla çıktısı, tasarımı gereği kaynağa dayandırma kontrollerinden geçer.

**Çıkarım ipuçları.** Her tip, veri yükünün şema kısmında modele iletilen ipucu dizgilerinden oluşan bir liste taşır. Örneğin "Ravi adını segment metninden birebir kopyala."

## 5.9 Tasarım kararları ve alternatifler

| Karar | Değerlendirilen alternatif | Gerekçe |
|---|---|---|
| Kenar kimliğinin ilişki birleştirme anahtarlarından elde edilmesi | Her aktarım olayı için bir düğüm | Genel modelde daha küçük bir değişiklik gerektirir |
| Başarısız kontrolün incelemeye yönlendirmesi | Reddetmek ya da güven skoru eşiğinin üzerinde kabul etmek | Ret, geçerli varyantları gizler; eşik ise modelin kendi bildirdiği bir sayıya güvenir |
| Tanımsız tipte tek adayın elenmesi ve bunun kaydedilmesi | Önceden olduğu gibi tüm yanıtı başarısız saymak | Geçerli adaylar korunur ve sapma sayılabilir |
| Yalnızca yeni kayıt eklenen kararlar ve hesaplanan kabul kayıtları | Grafın yeniden kurulduğu bir olay günlüğü | Denetim izi için yeterlidir; yeniden kurma ve geri alma gerçekleştirilmemiştir |
| Zincir segmenti başına tek çağrıyla, modelden önce kullanılabilen kural tabanlı bölütleyici | Zincirleri modelin bulduğu, hadis başına tek çağrı | Birebir alt dizgiler ve konumlar, birbirinden yalıtılmış başarısızlıklar ve modelsiz bir taban çizgisi sağlar. Değerlendirmede çıkarım kalitesine katkı bulunmamıştır (Bölüm 7.5); bu yüzden iki strateji de seçilebilir durumdadır |
| Koşu başına tek graf işlemi | Önceden olduğu gibi düğüm başına tek işlem | Başarısız commit, kısmi graf bırakmaz |

Üç sınırı bilerek kabul ediyoruz. Ravi düğümü, harekeler dâhil tam yazılı adıyla tanımlanır; bu yüzden graf, aynı adı paylaşan kişileri birleştirir ve iki biçimde yazılan tek kişiyi ayırır. Rivayet metninin sınırından sonra başlayan zincirler bölütlenmez; çünkü oradaki aktarım edatları çoğunlukla anlatıya aittir. Kaynağa dayandırma kontrolleri yalnızca çıkarım çağrısından gelen adaylara uygulanır.
