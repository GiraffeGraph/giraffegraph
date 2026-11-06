# 4 Gereksinimler ve kapsam

Bu bölümde sistemin ne yapması gerektiği, her gereksinimin nerede gerçekleştirildiği ve hangi testle kontrol edildiği belirtilmektedir. Başka bir dizinle başlamadıkları sürece gerçekleştirim yolları `backend/src/app/` dizinine göredir. Test dosyaları `backend/tests/unit/` ya da `backend/tests/integration/` dizininde bulunmaktadır. Yalnızca kodu `main` dalında bulunan gereksinimler listelenmektedir.

## 4.1 Kullanıcılar ve kullanım senaryoları

Sistemde kullanıcı hesabı bulunmadığından aşağıdaki roller yazılım tarafından uygulanmamaktadır.

- **Şema sahibi.** Proje oluşturmakta, düğüm ve ilişki tiplerini tanımlamakta ya da şema şablonu uygulamakta ve bir şema sürümünü etkinleştirmektedir.
- **Operatör.** Kaynak metni yüklemekte, işlemeyi başlatmakta ve bir koşuyu grafa commit etmektedir.
- **İnceleyici.** İnceleme kuyruğundaki adayları kabul eden, reddeden ya da düzenleyen, alan bilgisine sahip kişidir. İnceleyici tarafından bir ad girilmekte ve bu ad her kararla birlikte saklanmaktadır.
- **Okuyucu.** Commit edilmiş grafı gezmekte; vaka çalışmasında bir hadisi ravi zincirleri, alıntıları ve kabul kayıtlarıyla birlikte okumaktadır.

Kullanım senaryoları; şemalı bir projenin kurulması, metinlerin yüklenmesi, bir metnin işlenerek doğrulanmış adayların üretilmesi, açık inceleme öğeleri hakkında karar verilmesi, bir koşunun commit edilmesi ve commit edilmiş bir olgunun kaynak metnine ve kabulüne kadar izinin sürülmesidir.

## 4.2 İşlevsel gereksinimler

| Kimlik | Gereksinim | Gerçekleştirildiği yer | Doğrulayan test |
|---|---|---|---|
| FR1 | Projenin düğüm tipleri, ilişki tipleri, özellikleri ve birleştirme anahtarları içeren sürümlenmiş şemaları vardır. Adlar ASCII kimlikleridir. Yalnızca taslak sürüm düzenlenebilir. | `application/use_cases/schema_management.py`, `domain/schema/identifiers.py` | `test_project_schema_api.py` |
| FR2 | Proje oluşturulurken aynı istekte bir şema şablonu uygulanıp etkinleştirilebilir. | `ProjectSetupService`, `infrastructure/template/catalog.py` | `test_template_project_api.py` |
| FR3 | Kaynak metin tek tek birimler hâlinde ya da toplu yüklenir. Yinelenen dış referans her öğe için raporlanır. | `IngestionManagementService` | `test_ingestion_api.py`, `test_bulk_ingest_api.py` |
| FR4 | Kaynak birimi, adı belirtilen bir stratejiyle segmentlere ayrılır: `paragraphs` ya da ravi zinciri başına bir segment ve kaynak konumları üreten `isnad`. | `domain/extraction/segmentation.py`, `domain/hadith/segmentation.py` | `test_hadith_segmenter.py`, `test_isnad_segmentation.py` |
| FR5 | Sağlayıcı, segment başına adaylar önerir. Başarısız bir çağrı diğer çağrıları iptal etmez. Tanımsız tip ya da bildirilmemiş özellik tek başına elenir ve şema önerisi olarak kaydedilir. | `ExtractionManagementService.extract_candidates` | `test_isnad_pipeline_api.py`, `test_grounding_extraction_api.py` |
| FR6 | Adaylar şemaya göre doğrulanır: tip, zorunlu özellikler, birleştirme anahtarları, uç düğüm tipleri, izin verilen değerler, güven skoru eşikleri ve yinelenen adaylar kontrol edilir. | `PipelineManagementService.validate_run` | `test_pipeline_api.py` |
| FR7 | Çıkarılmış adayın alıntısı segmentinde, düğümün birleştirme anahtarı değeri de alıntıda geçmelidir. Başarısız denetim, adayı incelemeye gönderir. | `_evidence_findings`, `_merge_key_grounding_findings`, `domain/hadith/grounding.py` | `test_hadith_grounding.py`, `test_grounding_extraction_api.py` |
| FR8 | Aynı iki düğüm arasındaki, birleştirme anahtarı değerleri farklı iki ilişki, iki kenar olarak saklanır. | `domain/shared/resolution.py`, `infrastructure/persistence/neo4j/repositories.py` | `test_resolution.py`, `test_commit_api.py` |
| FR9 | İnceleyici bir inceleme öğesini kabul eder, reddeder ya da düzenler. Her karar, inceleyici, zaman ve isteğe bağlı süreyle birlikte saklanır; kararlara yalnızca yeni kayıt eklenir. Otomatik adımlar, hakkında karar verilmiş adayı değiştirmez. | `ReviewManagementService.decide_review_item`, `validate_run`, `review_decisions` tablosu | `test_review_decisions_api.py`, `test_review_api.py` |
| FR10 | Sistem, koşunun her doğrulanmış adayı için onu kabul eden insan kararını ya da otomatik politikayı raporlar. | `ReviewManagementService.list_acceptance_records` | `test_review_decisions_api.py` |
| FR11 | Koşu bir kez commit edilir; bunun için bekleyen aday ve açık inceleme öğesi bulunmamalıdır. | `CommitManagementService.commit_run` | `test_commit_api.py` |
| FR12 | Çıkarım, doğrulama ve commit, bir işçinin tükettiği kuyruklanmış işler olarak ya da kaynak birimleri listesi için tek bir eşzamanlı istekte çalışır. | `processing_job_management.py`, `interfaces/cli/processing_jobs_worker.py`, `SourceUnitProcessingService` | `test_processing_jobs_api.py`, `test_bulk_ingest_api.py` |
| FR13 | Commit edilmiş graf okunabilir; commit edilmiş bir hadis de alıntılar ve kabul kayıtları içeren sıralı zincirler olarak okunabilir. | `application/use_cases/exploration_management.py` | `test_exploration_api.py`, `test_chains_api.py` |
| FR14 | Tarayıcı paneli yukarıdaki adımları yürütür. | `frontend/src/modules/projects/` | Otomatik test yoktur; CI derler |

## 4.3 İşlevsel olmayan gereksinimler

| Kimlik | Gereksinim | Gerçekleştirildiği yer | Doğrulayan test |
|---|---|---|---|
| NFR1 | İzlenebilirlik: commit edilmiş düğüm ya da kenar, kaynak birimine ve onu destekleyen segmentlere bağlanır. | `DERIVED_FROM`, `SUPPORTED_BY` ve `RelationEvidence`, `Neo4jCanonicalGraphRepository` tarafından yazılır | `test_exploration_api.py` (bellekte), `test_realdb_isnad_flow.py` (`real_db`) |
| NFR2 | Atomik graf yazımı: başarısız commit, grafta koşunun hiçbir parçasını bırakmaz. | `commit_bundle`, `_write_bundle` işlemini tek bir `execute_write` işlemi içinde çalıştırır | `test_realdb_isnad_flow.py` (`real_db`) |
| NFR3 | Motor, veritabanı, ağ ya da API anahtarı olmadan çalışır ve test edilir. | `infrastructure/persistence/memory/`, `infrastructure/llm/rule_based_isnad_provider.py` | Varsayılan test koşusu, `test_isnad_baseline_script.py` |
| NFR4 | Alana özgü davranış, bölütleme stratejisi, şablon ya da sağlayıcı olarak eklenir. | `SegmentationStrategy`, `StaticDomainTemplateCatalog`, `StaticLLMProviderRegistry`, `bootstrap/container.py` | `test_isnad_pipeline_api.py`, `test_rule_based_isnad_provider.py` |
| NFR5 | Yinelenen model çağrıları önbellekten karşılanır ve belirteç kullanımı çağrı başına raporlanır. | `infrastructure/llm/cached_provider.py`, `infrastructure/llm/anthropic_provider.py` | `test_llm_cache_provider.py`, `test_anthropic_provider.py` |
| NFR6 | Veritabanı şeması yalnızca göçler yoluyla oluşturulur ve ORM modelleriyle eşleşir. | `backend/migrations/versions/`, `0001` ile `0006` arası | `test_review_decisions_migration.py`, `test_realdb_migrations.py` (`real_db`) |
| NFR7 | Arka uç kodu her push işleminde lint ve katı tip kontrolünden geçer. | `backend/pyproject.toml`, `.github/workflows/ci.yml` | CI iş akışı |

`real_db` işaretli testler çalışan veritabanları gerektirmekte; bu koşul sağlanmadığında atlanmaktadır (Bölüm 6.7). NFR4, Bölüm 5.1'de listelenen istisnalarla geçerlidir.

## 4.4 Kapsam dışı

Her öğe kodla karşılaştırılarak kontrol edilmiştir.

- **Ravi kimlik çözümleme.** `Narrator` tipinin tek birleştirme anahtarı `name`'dir. Karşılaştırmada yalnızca Unicode NFKC normalizasyonu, ardışık boşlukların tek boşluğa indirgenmesi ve büyük-küçük harf katlama uygulanmaktadır (`normalize_text`). Aynı yazılı adı taşıyan kişiler bir düğümü paylaşmakta; iki farklı biçimde yazılan tek kişi ise iki düğümle temsil edilmektedir.
- **Biyografik tarihler gerektiren alan kuralları.** İsnad şemasında tarih özellikleri bulunmamaktadır; ayrıca doğrulamada iki ravinin aynı dönemde yaşayıp yaşamadığını kontrol etmek gibi kurallar için bir kanca yer almamaktadır.
- **Sıhhat derecelendirmesi.** Hiçbir tip ya da özellikte hadis veya ravi için bir derece tutulmamaktadır.
- **Kimlik doğrulama ve kullanıcılar.** Hiçbir yönlendiricinin kimlik doğrulama bağımlılığı bulunmamaktadır; inceleyici adı serbest metindir.
- **Commit edilmiş koşunun geri alınması.** API'de 33 `GET` ve 20 `POST` uç noktası bulunmaktadır; `PUT`, `PATCH` ya da `DELETE` bulunmamaktadır. Tamamlanmış koşu değiştirilememektedir.
- **Türkçe hadis metni.** Normalizasyon ve aktarım kalıpları sözlüğü yalnızca Arap yazısını kapsamaktadır; yalnızca panel arayüzü Türkçedir.
- **Graf üzerinden soru yanıtlama.** Okuma uç noktaları düğümleri, ilişkileri ve zincirleri listelemekte ve göstermektedir. `EmbeddingProvider` protokolü, `application/ports/llm_provider.py` içinde bildirilmiştir; ancak gerçekleştirilmemiştir ve bilgi getirme uç noktası bulunmamaktadır.

İki şema alanı saklanmakta, ancak uygulanmamaktadır. Özelliğin `data_type` alanı modele gönderilmekte ve doğrulama sırasında kontrol edilmemektedir. İlişki tipinin `directional` bayrağı ise saklandıktan sonra kullanılmamaktadır.
