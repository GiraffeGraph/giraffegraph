# 6 Gerçekleştirim

Bu bölümde `main` dalı esas alınarak `giraffegraph-core` deposunun kodu açıklanmaktadır. Bu daldaki kodun büyük kısmı, yazarların yönlendirmesiyle yapay zekâ kodlama asistanları kullanılarak yazılmıştır ve Bölüm 6.7'de açıklanan otomatik test paketiyle doğrulanmaktadır.

## 6.1 Teknoloji yığını

| Bileşen | Teknoloji | Bildirilen sürüm |
|---|---|---|
| Arka uç | Python, FastAPI, Uvicorn, Pydantic | Python `>=3.12` (Docker imajında ve CI'da 3,12), `fastapi>=0.115`, `uvicorn>=0.34`, `pydantic>=2.10` |
| Üst veri deposu | PostgreSQL, SQLAlchemy, psycopg, Alembic | imaj `postgres:16-alpine`, `sqlalchemy>=2.0`, `psycopg>=3.2`, `alembic>=1.15` |
| Graf deposu | Neo4j ve Python sürücüsü | imaj `neo4j:5`, `neo4j>=6.0,<7.0` |
| Model erişimi | `anthropic` SDK; standart kütüphane üzerinden OpenAI uyumlu HTTP API | `anthropic>=1.13,<2.0` |
| Panel | Next.js, React, TypeScript | `next ^15`, `react ^19`, `typescript ^5`; CI'da Node 22 |
| Araçlar | uv, pytest, ruff, katı kipte mypy | `pytest>=8.3`, `ruff>=0.11`, `mypy>=1.15` |

Sürümler, `backend/pyproject.toml`, `frontend/package.json` ve `docker-compose.yml` dosyalarında bildirilen kısıtlardır. Docker Compose ile beş servis başlatılmaktadır: `postgres`, `neo4j`, `backend`, `worker` ve `dashboard`.

## 6.2 Depo düzeni

```text
backend/
  src/app/domain/          entities, segmentation, hadith helpers, identity keys
  src/app/application/     use cases and ports
  src/app/infrastructure/  LLM providers, template catalog, persistence
  src/app/interfaces/      API routers and worker CLI
  src/app/bootstrap/       application wiring
  migrations/versions/     Alembic migrations 0001 to 0006
  scripts/                 baseline and experiment runners
  tests/unit, tests/integration
frontend/src/modules/projects/   dashboard components, API client, types
evaluation/                scorer, analysis, annotation kit, their tests
```

## 6.3 API arayüzü

`interfaces/api/routers/` içindeki 13 yönlendirici, 33 `GET` ve 20 `POST` olmak üzere 53 uç nokta tanımlamaktadır.

| Grup | Sayı | Örnek uç noktalar |
|---|---|---|
| Projeler, şablonlar | 4 | `POST /api/projects`, `GET /api/templates` |
| Şema | 7 | `POST /api/schema-versions/{schema_version_id}/node-types` |
| Boru hattı tanımları | 3 | `GET /api/schema-versions/{schema_version_id}/pipeline-definitions` |
| Veri alımı ve koşular | 8 | `POST /api/projects/{project_id}/source-units/bulk`, `POST /api/projects/{project_id}/source-units/process`, `POST /api/source-units/{source_unit_id}/runs` |
| Segmentler, adaylar, doğrulama | 10 | `POST /api/source-units/{source_unit_id}/segments/generate`, `POST /api/runs/{run_id}/validate`, `GET /api/runs/{run_id}/review-items` |
| Çıkarım | 2 | `POST /api/runs/{run_id}/extract-candidates` |
| İnceleme | 4 | `GET /api/projects/{project_id}/review-queue`, `POST /api/review-items/{review_item_id}/decision`, `GET /api/runs/{run_id}/acceptance-records` |
| Commit | 2 | `POST /api/runs/{run_id}/commit`, `GET /api/runs/{run_id}/graph-delta` |
| İşler | 4 | `POST /api/runs/{run_id}/processing-jobs`, `POST /api/processing-jobs/process-next` |
| Graf | 5 | `GET /api/projects/{project_id}/graph/nodes` |
| Zincirler | 3 | `GET /api/projects/{project_id}/chains/hadith`, `GET /api/projects/{project_id}/chains/narrator` |
| Sağlık | 1 | `GET /health` |

Uygulama hataları, `error_handlers.py` içinde 404, 409, 422 ve 502 durum kodlarına eşlenmektedir.

## 6.4 Model sağlayıcısı soyutlaması

`LLMProvider` portunda iki metot bulunmaktadır. `generate_structured` yanıtı sözlük olarak döndürmekte; `generate_structured_with_usage` ise yanıtla birlikte bir `LLMUsage` kaydı döndürmektedir. `StaticLLMProviderRegistry`, sağlayıcıları adlarına göre tutmaktadır. `noop` (aday döndürmemektedir) ve `rule_based_isnad` (Bölüm 5.8) her zaman kaydedilmektedir; `openai` ve `anthropic` ise yalnız API anahtarları ayarlandığında kaydedilmektedir.

- **OpenAI uyumlu** (`openai_provider.py`). `{base_url}/chat/completions` adresine, `temperature` değeri 0 ve `response_format` değeri `json_object` olacak biçimde istek göndermekte; belirteç sınırında kesilen yanıtı hata saymaktadır. Belirteç sayılarını raporlamamaktadır.
- **Anthropic** (`anthropic_provider.py`). Messages API'yi bir `output_config` ile çağırmaktadır. Bu yapılandırmada çaba ayarı ve bir JSON şeması (`EXTRACTION_WIRE_SCHEMA`) taşınmaktadır. Şema yalnız kapalı nesnelere izin verdiği için özellikler, ad ve değer girdilerinden oluşan bir liste olarak aktarılmakta ve ardından yeniden bir eşlemeye dönüştürülmektedir. Çaba ayarı `ANTHROPIC_EFFORT` değişkeninden gelmektedir (varsayılan `low`). Ret, kesilmiş yanıt ve her API hata sınıfı, bir `StructuredGenerationError` hatasına dönüştürülmekte; bu hata bir `kind` içermektedir. Kullanım kaydı; girdi ve çıktı belirteçlerini, önbellekten okunan ve önbellek oluşturmak için kullanılan belirteçleri, durma gerekçesini ve modeli tutmaktadır.

İstem kataloğu, tip adlarını eşleştirme kuralı bakımından farklılaşan `candidate_graph_extraction_v1` ve `candidate_graph_extraction_v2` sürümlerini tutmaktadır; varsayılan sürüm `v2`'dir.

`CachedLLMProvider`, bir sağlayıcıyı sarmalamakta ve her çağrı için bir JSON dosyası saklamaktadır. Anahtar; sağlayıcı adı, model, çaba, istem sürümü, istem metni ve veri yükünün SHA-256 özetidir. Özet alınmadan önce veri yükündeki koşu, şema sürümü, kaynak birimi ve segment kimlikleri, konumsal yer tutucularla değiştirilmektedir. Bu nedenle aynı içerikle yapılan sonraki koşu önbellekte bulunmakta ve saklanan yanıt yeni koşunun segment kimliklerine yeniden eşlenmektedir. Başarısız çağrılar saklanmamaktadır.

Çıkarım kullanım senaryosu, `generate_structured` metodunu çağırmakta ve belirteç sayılarını saklamamaktadır. Önbelleği ve kullanım kayıtlarını kullanan `scripts/run_isnad_experiment.py`, her çağrının belirteçlerini, gecikmesini ve maliyetini yazmakta; harcama sınırına ulaşıldığında çağrı yapmayı durdurmaktadır.

## 6.5 Kalıcı saklama

**Postgres.** ORM ile 18 tablo tanımlanmaktadır. `0001` göçü başlangıçtaki 15 tabloyu oluşturmakta; `0002` düğüm tipinin güven skoru eşiğini, `0003` `processing_jobs` tablosunu, `0004` `pipeline_definitions` tablosunu eklemektedir. `0005`, `merge_keys` sütununu `relation_types` tablosuna eklemekte; `0006` ise iki indeksli `review_decisions` tablosunu eklemektedir. `AUTO_APPLY_POSTGRES_MIGRATIONS` doğru olduğunda arka uç, başlangıçta göçleri uygulamaktadır. Bir iş, `FOR UPDATE SKIP LOCKED` ve koşu başına bir danışma kilidi ile alınmaktadır; çalışan işi olan koşuya ikinci bir iş verilmemektedir.

**Neo4j.** `commit_bundle`, `_write_bundle` fonksiyonunu `session.execute_write` metoduna geçirmekte; böylece bir koşunun bütün ifadeleri aynı veritabanı işlemini paylaşmaktadır. Önce kaynak birimini ve segmentlerini, sonra her düğümü (`project_id`, `node_type`, `merge_key`) üzerinden `CanonicalNode` ve tip adı etiketleriyle, ardından her ilişkiyi kimlik anahtarıyla birleştirmektedir. Köken bilgisi; kaynak birimine `DERIVED_FROM`, segmentlere `SUPPORTED_BY`, commit edilen her ilişki adayı için bir `RelationEvidence` düğümü ve bir `GraphDelta` düğümü olarak yazılmaktadır. Tip adları bir ifadeye girmeden önce tanımlayıcı örüntüsüne göre kontrol edilmektedir. Bir sürecin ilk commit işleminde `CREATE INDEX ... IF NOT EXISTS` ile beş indeks oluşturulmaktadır: düğüm anahtarı için bir indeks, `SourceUnit`, `Segment`, `RelationEvidence` ve `GraphDelta` tiplerinin id özelliği için de birer indeks. Benzersizlik kısıtı tanımlanmamıştır. Alıntılar ve konum ofsetleri Postgres'teki aday satırlarında kalmaktadır; graf, segmentlerin bütününe bağlanmaktadır.

## 6.6 Panel

Panel, geliştirici olmayan bir okuyucu için yazılmış Türkçe bir Next.js uygulamasıdır. Renkleri ve yazı biçimi, projenin kamuya açık sayfasını izlemektedir. Ana sayfada ürün iki cümleyle açıklanmakta ve projeler durum cümlesi içeren kartlar olarak listelenmektedir; örneğin "30 hadis · hepsi grafta · bekleyen yok" (30 hadis, hepsi grafta, bekleyen yok). Proje oluştururken yalnız ad sorulmaktadır; isnad şablonu ve şeması otomatik uygulanmaktadır.

Proje akışı, sayılarla birlikte adım göstergesinde sunulan dört adımdan oluşmaktadır. Her adım için bir ekran ve bir ana eylem bulunmaktadır.

1. **Metin yükle (metin yükleme).** Kullanıcı metin yapıştırarak, bir JSON dosyası seçerek ya da paketle gelen on örnek hadisi tek tıklamayla yükleyerek veri girişi yapmaktadır. Sonuç, yinelenen kayıtlar da dahil olmak üzere bir cümleyle bildirilmektedir.
2. **Zincirleri çıkar (zincir çıkarımı).** Kullanıcı, kurallar ya da sunucuda yapılandırılmışsa bir dil modeli arasından yöntem seçmektedir. Tek bir düğmeyle bekleyen bütün hadisler işlenmekte ve kaç hadisin grafa yazıldığı, kaçının karar beklediği özetlenmektedir.
3. **İncele (inceleme).** Yalnız bir kişinin kararını gerektiren öneriler, teker teker görünmektedir: alıntısı vurgulanmış hadis metni, önerilen değer, neden beklediğini açıklayan bir cümle ve üç eylem (kabul, ret, düzeltme). Her inceleme gerekçe kodu için ayrı bir cümle kullanılmakta; değer denetimi için "önerilen ad, sistemin gösterdiği alıntıda geçmiyor" yazmaktadır. İnceleyicinin adı bir kez sorularak tarayıcıda saklanmakta; bir öğenin açılması ile karar verilmesi arasında geçen süre kararla birlikte gönderilmektedir.
4. **Zincirleri oku (zincir okuma).** Commit edilen hadisler bir arama alanıyla listelenmektedir. Seçilen hadisin Arapça metni sağdan sola gösterilmekte ve her ravi geçişi, kaynaktaki konum ofsetlerinde vurgulanmaktadır. Her zincir yukarıdan aşağıya okunmaktadır: önce ravi, ardından aktarım ifadesi, alıntısı ve nasıl kabul edildiğiyle birlikte bağlantı gelmektedir. Kabul biçimi açıkça "otomatik kabul edildi (denetimleri geçti)" ya da ad ve tarihle birlikte "bir kişi tarafından kabul edildi" olarak yazılmaktadır. Bir ravi seçildiğinde, adın geçtiği hadisler ile kendisine aktaran ve kendisinin aktardığı kişilerin adları gösterilmektedir; ravinin yazılı adla tanımlandığını belirten bir not bulunmaktadır.

Şema düzenleyicisi, adım adım boru hattı çalıştırıcısı, iş listesi ve ham graf gezgini, ikincil bir giriş olan "Gelişmiş" (gelişmiş seçenekler) altında yer almaktadır. Beş terimlik sözlüğe her sayfadan ulaşılmaktadır. Her ekrana ait görüntüler `frontend/docs/screens/` dizininde bulunmaktadır.

## 6.7 Testler ve sürekli entegrasyon

`uv run pytest --collect-only -q` ile 285 test toplanmıştır: 14 dosyada 127 birim testi ve 21 dosyada 158 entegrasyon testi. `uv run pytest -q` ile gerçekleştirilen koşuda 273 test başarıyla tamamlanmış, 12 test atlanmıştır. Entegrasyon testleri, önceden tanımlanmış yanıtlar veren sağlayıcılarla bellek içi arka uçta, FastAPI'nin `TestClient` aracı üzerinden API'yi çalıştırmaktadır; dolayısıyla hiçbir test bir ağ servisini çağırmamaktadır.

Atlanan 12 test, `real_db` işaretini taşımaktadır. `test_realdb_migrations.py` (4 test), göç zincirini boş bir veritabanında çalıştırmakta, sonucu ORM modelleriyle karşılaştırmakta ve sürüm düşürmeyi kontrol etmektedir. `test_realdb_isnad_flow.py` (7 test), isnad akışını Postgres ve Neo4j üzerinde çalıştırmaktadır: iki hadiste aynı ravi çifti iki kenar üretmekte, grafın tekrar yazılması hiçbir şey eklememekte, kesintiye uğrayan yazma işlemi kısmi graf bırakmamakta ve arama indeksleri bulunmaktadır. `test_realdb_review_decisions.py` (1 test), kararların saklandığını ve eklenerek ilerlediğini kontrol etmektedir. Bu testler yalnız `GG_TEST_POSTGRES_DSN`, `GG_TEST_NEO4J_URI` ve `GG_TEST_NEO4J_PASSWORD` ayarlandığında çalışmaktadır; geçici Postgres veritabanları oluşturup silmektedir. 12 Ekim 2026'da yerel konteynerlerde PostgreSQL 16 ve Neo4j 5,26 üzerinde çalıştırılan testlerin 12'si de başarılı olmuştur; aynı gün, o sırada mevcut olan 214 test de bu veritabanlarında bir kez çalıştırılmış ve başarılı olmuştur. Bu doğrulamada, bellek içi arka ucun gizlediği dört kusur saptanmıştır. Bunlar arasında düğüm başına bir veritabanı işlemi kullanan ve kısmi graf bırakabilen bir graf yazma işlemi ile Neo4j indekslerinin bulunmaması yer almıştır. Dört kusur da giderilmiştir.

Değerlendirme kitinin `evaluation/tests/` dizinindeki kendi testleri, sekiz dosyada 81 testten oluşmaktadır. 80'i başarılı olmuştur; biri, puanlayıcıyı pilot betiğiyle karşılaştırdığı için `numpy` ve `scipy` kurulu olmadıkça atlanmaktadır. Panel için otomatik test bulunmamaktadır.

CI iş akışı, motorun klasörünü değiştiren her push ve pull request için iki iş çalıştırmaktadır. Arka uç işi `ruff check src tests`, `mypy src` ve `pytest -q` komutlarını; ön uç işi `npm ci` ve `npm run build` komutlarını çalıştırmaktadır. CI'da veritabanı değişkenleri ayarlanmadığından `real_db` testleri atlanmaktadır; değerlendirme kitinin testleri de çalıştırılmamaktadır.

## 6.8 Çalıştırma

Bütün yığın, deponun kökünden aşağıdaki komutlarla çalıştırılmaktadır:

```bash
cp .env.example .env
docker compose up --build
```

Bu komutların ardından panel `http://localhost:3000`, API ise `http://localhost:8000` adresinden erişilebilir durumdadır.

Arka uç testleri ve denetimleri aşağıdaki komutlarla yürütülmektedir:

```bash
cd backend
uv sync --extra dev
uv run pytest -q
uv run ruff check src tests
uv run mypy src
```

`docs/guides/isnad-demo.md` kılavuzunda, veritabanı ya da API anahtarı olmadan isnad demosunun çalıştırılması için aşağıdaki komutlar verilmektedir:

```bash
cd backend
REPOSITORY_BACKEND=memory ALLOWED_ORIGINS=http://localhost:3000 \
  uv run uvicorn app.main:app --app-dir src --port 8000
```

```bash
cd frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Kılavuzun devamında `isnad` şablonundan bir proje oluşturulması, toplu yükleme uç noktasından hadislerin yüklenmesi, `rule_based_isnad` sağlayıcısıyla işlenmesi ve zincirlerin okunması açıklanmaktadır.

## 6.9 Bilinen sınırlamalar

Alınan karar gereği üç yetenek bulunmamaktadır: commit edilen koşu geri alınamamaktadır; kimlik doğrulama ve ravi kimliği çözümlemesi bulunmamaktadır.

Kodun diğer sınırlamaları aşağıda belirtilmektedir.

- Graf farkı satırı, Neo4j veritabanı işleminden sonra Postgres'e yazılmaktadır. İkisi arasında bir hata olursa graf, üst verinin önüne geçmektedir.
- Düğüm özellikleri `SET n += $properties` ile yazılmaktadır; bu nedenle sonraki bir koşu, farklı bir değerin üzerine inceleme öğesi oluşturmadan yazmaktadır.
- Şema önerisinin kabul edilmesiyle inceleme öğesi kapatılmakta, şema değiştirilmemektedir.
- İşleme uç noktası istek içinde çalışmaktadır; zincir uç noktaları projenin bütün kaynak birimlerini ve koşularını taramaktadır.
- İlişki ayrıntısı uç noktasında kimlik anahtarı parametresi bulunmamaktadır; bu yüzden paralel kenarlardan birini döndürmektedir.
- Segmentlerin yeniden üretilmesi, saklanan segmentleri yeni kimliklerle değiştirmektedir; dolayısıyla önceki koşuların kanıt referansları artık var olmayan segmentleri göstermektedir.
- Bir önerinin birden fazla gerekçesi varsa panel yalnız ilkini göstermekte ve proje sayılarını proje başına iki istekle tarayıcıda hesaplamaktadır. Panelin otomatik testi bulunmamaktadır.
- Henüz bir lisans seçilmemiştir.
