# 6 Gerçekleştirim

Bu bölümde `main` dalını esas alarak `giraffegraph-core` deposunun kodunu açıklıyoruz. Bu daldaki kodun büyük kısmı, yazarların yönlendirmesiyle yapay zekâ kodlama asistanları kullanılarak yazılmıştır ve Bölüm 6.7'de açıklanan otomatik test paketiyle doğrulanmaktadır.

## 6.1 Teknoloji yığını

| Bileşen | Teknoloji | Bildirilen sürüm |
|---|---|---|
| Arka uç | Python, FastAPI, Uvicorn, Pydantic | Python `>=3.12` (Docker imajında ve CI'da 3,12), `fastapi>=0.115`, `uvicorn>=0.34`, `pydantic>=2.10` |
| Üst veri deposu | PostgreSQL, SQLAlchemy, psycopg, Alembic | imaj `postgres:16-alpine`, `sqlalchemy>=2.0`, `psycopg>=3.2`, `alembic>=1.15` |
| Graf deposu | Neo4j ve Python sürücüsü | imaj `neo4j:5`, `neo4j>=6.0,<7.0` |
| Model erişimi | `anthropic` SDK; standart kütüphane üzerinden OpenAI uyumlu HTTP API | `anthropic>=1.13,<2.0` |
| Panel | Next.js, React, TypeScript | `next ^15`, `react ^19`, `typescript ^5`; CI'da Node 22 |
| Araçlar | uv, pytest, ruff, katı kipte mypy | `pytest>=8.3`, `ruff>=0.11`, `mypy>=1.15` |

Sürümler, `backend/pyproject.toml`, `frontend/package.json` ve `docker-compose.yml` dosyalarında bildirilen kısıtlardır. Docker Compose beş servisi başlatır: `postgres`, `neo4j`, `backend`, `worker` ve `dashboard`.

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

`interfaces/api/routers/` içindeki 13 yönlendirici, 33 `GET` ve 20 `POST` olmak üzere 53 uç nokta tanımlar.

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

Uygulama hataları, `error_handlers.py` içinde 404, 409, 422 ve 502 durum kodlarına eşlenir.

## 6.4 Model sağlayıcısı soyutlaması

`LLMProvider` portunun iki metodu vardır. `generate_structured` yanıtı sözlük olarak döndürür; `generate_structured_with_usage` ise yanıtla birlikte bir `LLMUsage` kaydı döndürür. `StaticLLMProviderRegistry`, sağlayıcıları adlarına göre tutar. `noop` (aday döndürmez) ve `rule_based_isnad` (Bölüm 5.8) her zaman kaydedilir; `openai` ve `anthropic` ise yalnız API anahtarları ayarlandığında kaydedilir.

- **OpenAI uyumlu** (`openai_provider.py`). `{base_url}/chat/completions` adresine, `temperature` değeri 0 ve `response_format` değeri `json_object` olacak biçimde istek gönderir; belirteç sınırında kesilen yanıtı hata sayar. Belirteç sayılarını raporlamaz.
- **Anthropic** (`anthropic_provider.py`). Messages API'yi bir `output_config` ile çağırır. Bu yapılandırma çaba ayarını ve bir JSON şemasını (`EXTRACTION_WIRE_SCHEMA`) taşır. Şema yalnız kapalı nesnelere izin verdiği için özellikler, ad ve değer girdilerinden oluşan bir liste olarak aktarılır ve sonra yeniden bir eşlemeye dönüştürülür. Çaba ayarı `ANTHROPIC_EFFORT` değişkeninden gelir (varsayılan `low`). Ret, kesilmiş yanıt ve her API hata sınıfı bir `StructuredGenerationError` olur; bu hata bir `kind` içerir. Kullanım kaydı; girdi ve çıktı belirteçlerini, önbellekten okunan ve önbellek oluşturmak için kullanılan belirteçleri, durma gerekçesini ve modeli tutar.

İstem kataloğu, tip adlarını eşleştirme kuralı bakımından farklılaşan `candidate_graph_extraction_v1` ve `candidate_graph_extraction_v2` sürümlerini tutar; varsayılan sürüm `v2`'dir.

`CachedLLMProvider`, bir sağlayıcıyı sarmalar ve her çağrı için bir JSON dosyası saklar. Anahtar; sağlayıcı adı, model, çaba, istem sürümü, istem metni ve veri yükünün SHA-256 özetidir. Özet alınmadan önce veri yükündeki koşu, şema sürümü, kaynak birimi ve segment kimlikleri, konumsal yer tutucularla değiştirilir. Bu nedenle aynı içerikle yapılan sonraki koşu önbellekte bulunur ve saklanan yanıt yeni koşunun segment kimliklerine yeniden eşlenir. Başarısız çağrılar saklanmaz.

Çıkarım kullanım durumu, `generate_structured` metodunu çağırır ve belirteç sayılarını saklamaz. Önbelleği ve kullanım kayıtlarını kullanan `scripts/run_isnad_experiment.py`, her çağrının belirteçlerini, gecikmesini ve maliyetini yazar; harcama sınırına ulaşıldığında çağrı yapmayı durdurur.

## 6.5 Kalıcı saklama

**Postgres.** ORM, 18 tablo tanımlar. `0001` göçü başlangıçtaki 15 tabloyu oluşturur; `0002` düğüm tipinin güven skoru eşiğini, `0003` `processing_jobs` tablosunu, `0004` `pipeline_definitions` tablosunu ekler. `0005`, `merge_keys` sütununu `relation_types` tablosuna ekler; `0006` ise iki indeksli `review_decisions` tablosunu ekler. `AUTO_APPLY_POSTGRES_MIGRATIONS` doğru olduğunda arka uç, başlangıçta göçleri uygular. Bir iş, `FOR UPDATE SKIP LOCKED` ve koşu başına bir danışma kilidi ile alınır; çalışan işi olan koşuya ikinci bir iş verilmez.

**Neo4j.** `commit_bundle`, `_write_bundle` fonksiyonunu `session.execute_write` metoduna geçirir; böylece bir koşunun bütün ifadeleri aynı veritabanı işlemini paylaşır. Önce kaynak birimini ve segmentlerini, sonra her düğümü (`project_id`, `node_type`, `merge_key`) üzerinden `CanonicalNode` ve tip adı etiketleriyle, ardından her ilişkiyi kimlik anahtarıyla birleştirir. Köken bilgisi; kaynak birimine `DERIVED_FROM`, segmentlere `SUPPORTED_BY`, commit edilen her ilişki adayı için bir `RelationEvidence` düğümü ve bir `GraphDelta` düğümü olarak yazılır. Tip adları bir ifadeye girmeden önce tanımlayıcı örüntüsüne göre kontrol edilir. Bir sürecin ilk commit işleminde `CREATE INDEX ... IF NOT EXISTS` ile beş indeks oluşturulur: düğüm anahtarı için bir indeks, `SourceUnit`, `Segment`, `RelationEvidence` ve `GraphDelta` tiplerinin id özelliği için de birer indeks. Benzersizlik kısıtı tanımlanmamıştır. Alıntılar ve konum ofsetleri Postgres'teki aday satırlarında kalır; graf, segmentlerin bütününe bağlanır.

## 6.6 Panel

Panel, geliştirici olmayan bir okuyucu için yazılmış Türkçe bir Next.js uygulamasıdır. Renkleri ve yazı biçimi, projenin kamuya açık sayfasını izler. Ana sayfa ürünü iki cümleyle açıklar ve projeleri, durum cümlesi içeren kartlar olarak listeler; örneğin "30 hadis · hepsi grafta · bekleyen yok" (30 hadis, hepsi grafta, bekleyen yok). Proje oluştururken yalnız ad sorulur; isnad şablonu ve şeması otomatik uygulanır.

Bir proje, sayılarla birlikte adım göstergesinde sunulan dört adımdan oluşur. Her adımın bir ekranı ve bir ana eylemi vardır.

1. **Metin yükle (metin yükleme).** Kullanıcı metin yapıştırır, bir JSON dosyası seçer ya da paketle gelen on örnek hadisi tek tıklamayla yükler. Sonuç, yinelenen kayıtlar da dahil olmak üzere bir cümleyle bildirilir.
2. **Zincirleri çıkar (zincir çıkarımı).** Kullanıcı bir yöntem seçer: kurallar ya da sunucuda yapılandırılmışsa bir dil modeli. Tek bir düğme, bekleyen bütün hadisleri işler ve kaç hadisin grafa yazıldığını, kaçının karar beklediğini özetler.
3. **İncele (inceleme).** Yalnız bir kişinin kararını gerektiren öneriler, teker teker görünür: alıntısı vurgulanmış hadis metni, önerilen değer, neden beklediğini açıklayan bir cümle ve üç eylem (kabul, ret, düzeltme). Her inceleme gerekçe kodunun kendi cümlesi vardır; değer kontrolü için "önerilen ad, sistemin gösterdiği alıntıda geçmiyor" yazar. İnceleyicinin adı bir kez sorulur ve tarayıcıda saklanır; bir öğenin açılması ile karar verilmesi arasında geçen süre kararla birlikte gönderilir.
4. **Zincirleri oku (zincir okuma).** Commit edilen hadisler bir arama alanıyla listelenir. Seçilen hadisin Arapça metni sağdan sola gösterilir ve her ravi geçişi, kaynaktaki konum ofsetlerinde vurgulanır. Her zincir yukarıdan aşağıya okunur: önce ravi, ardından aktarım ifadesi, alıntısı ve nasıl kabul edildiğiyle birlikte bağlantı gelir. Kabul biçimi açıkça "otomatik kabul edildi (kontrolleri geçti)" ya da ad ve tarihle birlikte "bir kişi tarafından kabul edildi" olarak yazılır. Bir ravi seçildiğinde, adın geçtiği hadisler ile kendisine aktaran ve kendisinin aktardığı kişilerin adları gösterilir; ravinin yazılı adla tanımlandığını belirten bir not bulunur.

Şema düzenleyicisi, adım adım boru hattı çalıştırıcısı, iş listesi ve ham graf gezgini, ikincil bir giriş olan "Gelişmiş" (gelişmiş seçenekler) altında yer alır. Beş terimlik sözlüğe her sayfadan ulaşılır. Her ekranın görüntüleri `frontend/docs/screens/` içindedir.

## 6.7 Testler ve sürekli entegrasyon

`uv run pytest --collect-only -q`, 285 test toplar: 14 dosyada 127 birim testi ve 21 dosyada 158 entegrasyon testi. `uv run pytest -q` koşumuzda 273 test geçti, 12 test atlandı. Entegrasyon testleri, önceden tanımlanmış yanıtlar veren sağlayıcılarla bellek içi arka uçta, FastAPI'nin `TestClient` aracı üzerinden API'yi çalıştırır; dolayısıyla hiçbir test bir ağ servisini çağırmaz.

Atlanan 12 test, `real_db` işaretini taşır. `test_realdb_migrations.py` (4 test), göç zincirini boş bir veritabanında çalıştırır, sonucu ORM modelleriyle karşılaştırır ve sürüm düşürmeyi kontrol eder. `test_realdb_isnad_flow.py` (7 test), isnad akışını Postgres ve Neo4j üzerinde çalıştırır: iki hadiste aynı ravi çifti iki kenar üretir, grafın tekrar yazılması hiçbir şey eklemez, kesintiye uğrayan yazma işlemi kısmi graf bırakmaz ve arama indeksleri bulunur. `test_realdb_review_decisions.py` (1 test), kararların saklandığını ve eklenerek ilerlediğini kontrol eder. Bu testler yalnız `GG_TEST_POSTGRES_DSN`, `GG_TEST_NEO4J_URI` ve `GG_TEST_NEO4J_PASSWORD` ayarlandığında çalışır; geçici Postgres veritabanları oluşturup silerler. 12 Ekim 2026'da yerel konteynerlerde PostgreSQL 16 ve Neo4j 5,26 üzerinde çalıştırıldılar ve 12'si de geçti; aynı gün, o sırada mevcut olan 214 test de bu veritabanlarında bir kez çalıştırıldı ve geçti. Bu doğrulamada, bellek içi arka ucun gizlediği dört kusur bulundu. Bunlar arasında düğüm başına bir veritabanı işlemi kullanan ve kısmi graf bırakabilen bir graf yazma işlemi ile Neo4j indekslerinin hiç bulunmaması vardı. Dördü de düzeltildi.

Değerlendirme kitinin `evaluation/tests/` içinde kendi testleri vardır: sekiz dosyada 81 test. 80'i geçer; biri, puanlayıcıyı pilot betiğiyle karşılaştırdığı için `numpy` ve `scipy` kurulu olmadıkça atlanır. Panelin otomatik testi yoktur.

CI iş akışı, motorun klasörünü değiştiren her push ve pull request için iki iş çalıştırır. Arka uç işi `ruff check src tests`, `mypy src` ve `pytest -q` komutlarını; ön uç işi `npm ci` ve `npm run build` komutlarını çalıştırır. CI'da veritabanı değişkenleri ayarlanmadığından `real_db` testleri atlanır; değerlendirme kitinin testleri de çalıştırılmaz.

## 6.8 Çalıştırma

Deponun kökünden bütün yığını çalıştırmak için:

```bash
cp .env.example .env
docker compose up --build
```

Ardından panel `http://localhost:3000`, API ise `http://localhost:8000` adresindedir.

Arka uç testleri ve kontrolleri:

```bash
cd backend
uv sync --extra dev
uv run pytest -q
uv run ruff check src tests
uv run mypy src
```

`docs/guides/isnad-demo.md` kılavuzuna göre, veritabanı ya da API anahtarı olmadan isnad demosu:

```bash
cd backend
REPOSITORY_BACKEND=memory ALLOWED_ORIGINS=http://localhost:3000 \
  uv run uvicorn app.main:app --app-dir src --port 8000
```

```bash
cd frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Kılavuz daha sonra `isnad` şablonundan bir proje oluşturur, toplu yükleme uç noktasından hadisleri yükler, `rule_based_isnad` sağlayıcısıyla işler ve zincirleri okur.

## 6.9 Bilinen sınırlamalar

Üç yetenek, alınan karar gereği yoktur: commit edilen koşu geri alınamaz, kimlik doğrulama yoktur ve ravi kimliği çözümlemesi yoktur.

Kodun ayrıca şu sınırları vardır.

- Graf değişimi satırı, Neo4j veritabanı işleminden sonra Postgres'e yazılır. İkisi arasında bir hata olursa graf, üst verinin önüne geçer.
- Düğüm özellikleri `SET n += $properties` ile yazılır; bu nedenle sonraki bir koşu, farklı bir değerin üzerine inceleme öğesi oluşturmadan yazar.
- Şema önerisini kabul etmek inceleme öğesini kapatır, şemayı değiştirmez.
- İşleme uç noktası istek içinde çalışır; zincir uç noktaları projenin bütün kaynak birimlerini ve koşularını tarar.
- İlişki ayrıntısı uç noktasında kimlik anahtarı parametresi bulunmaz; bu yüzden paralel kenarlardan birini döndürür.
- Segmentlerin yeniden üretilmesi, saklanan segmentleri yeni kimliklerle değiştirir; dolayısıyla önceki koşuların kanıt başvuruları artık var olmayan segmentleri gösterir.
- Bir önerinin birden fazla gerekçesi varsa panel yalnız ilkini gösterir, proje sayılarını proje başına iki istekle tarayıcıda hesaplar ve otomatik testi yoktur.
- Henüz bir lisans seçilmemiştir.
