# İsnad boru hattı: bölütleme, kapılar ve inceleme nedenleri

## Purpose

Core'un hadis isnadını işlerken hangi adımda neyi denetlediğini, bir adayın neden incelemeye
düştüğünü ve bilinen sınırları tek yerde tutmak. Bir ölçüm sayısı okunurken "sistem o sırada ne
yapıyordu" sorusunun cevabı buradadır.

## Scope

- In: isnad bölütleme stratejisi, isnad şablonu, sağlayıcılar, grounding kapıları, inceleme ve red
  kodları, karar kaydı, commit, doğrulama durumu, bilinen sınırlar
- Out: metrik tanımları ve ölçüm sonuçları (`wiki/evaluation/correctness-measurement.md`), çalıştırma
  komutları (`giraffegraph-core/README.md`, `giraffegraph-core/evaluation/README.md`)

Statü: bu davranış `giraffegraph-core` reposunun `main` dalındadır (`origin`, 2026-10-13). Ekip ve danışman onayı yoktur, ADR yazılmamıştır. Tasarımın kaynağı
`wiki/sources/claude-science-results/05_kod_degisiklik_listesi.md` içindeki önerilerdir. Akış gerçek Postgres ve
Neo4j'e karşı testle ve gerçek LLM çağrılarıyla koşulmuştur ("Doğrulama durumu").

## Akış

```txt
hadis metni ──► isnad bölütleme ──► zincir başına çağrı ──► kapılar ──► inceleme ──► canonical graf
                (kural tabanlı)     (LLM ya da kural)       (aşağıda)    (karar kaydı)
```

- Bir hadis bir kaynak birimidir; `external_ref` alanı `<koleksiyon>:<numara>` taşır.
- Bölütleme stratejisi `isnad`, her zinciri ayrı segment yapar; segment metni kaynağın birebir alt
  dizesidir. Tahvîl (`ح`) yeni zincir başlatır. Metin (matn) sınırından sonraki zincirler segment
  yapılmaz. Zincir bulunamazsa tüm metin tek segment olur ve segment metaverisine yazılır.
- Çıkarım zincir başına bir çağrıdır. Bir çağrının başarısız olması diğerlerinin sonucunu silmez.
- Sağlayıcı `rule_based_isnad` ağ kullanmaz: segmenti kuralla ayrıştırır, ravi adını metindeki hâliyle
  verir. "LLM'siz" deney koşulu budur.
- LLM sağlayıcıları `openai` ve `anthropic`'tir; her biri yalnız kendi API anahtarı tanımlıysa kaydedilir
  (`bootstrap/container.py`). `anthropic` sağlayıcısı her istekte `ANTHROPIC_EFFORT` ayarını gönderir.
- Toplu yol: `POST /api/projects/{id}/source-units/bulk` hadisleri kaynak birimi olarak yükler,
  `POST /api/projects/{id}/source-units/process` her birim için koşu başlatır, bölütler, çıkarır,
  doğrular ve `commit: true` ise açık inceleme öğesi olmayan koşuyu commit eder
  (`giraffegraph-core/docs/guides/isnad-demo.md`).
- Commit koşu başına tek Neo4j işlemidir; başarısız bir commit grafta o koşudan parça bırakmaz
  (`infrastructure/persistence/neo4j/repositories.py:commit_bundle`).
- Commit edilmiş zincirler `/api/projects/{id}/chains` altındaki uçlardan okunur: commit edilmiş hadisler,
  bir hadisin zincirleri (alıntı ve kabul kaydıyla), bir ravi ve komşuları. Paneldeki "Zincirleri oku" adımı
  bu uçları kullanır.

## İsnad şablonu

| Tip | Kimlik (merge key) | Not |
|---|---|---|
| `Narrator` | `name` | Ad, metindeki yazımıyla |
| `Hadith` | `hadith_ref` | Kaynak biriminin `external_ref` değeri |
| `NARRATED_FROM` (Narrator → Narrator) | `hadith_ref`, `chain_no`, `position` | Önce anılan ravi sonra anılandan almıştır. `sigha` özelliği rivayet lafzını taşır |
| `TRANSMITS` (Narrator → Hadith) | — | |

Teknik adlar ASCII'dir; Türkçe ya da Arapça etiket `display_name` alanına yazılır. Proje oluşturma
isteğinde `apply_template_schema: true` verilirse şablonun şeması aynı istekte uygulanır: şema sürümü
oluşur ve etkinleşir, `v1` boru hattı tanımı yazılır (`schema_management.py:apply_template_schema`).
Alanın varsayılanı `false`'tur; o durumda şema, şema API'siyle yüklenir.

## Kapılar, inceleme ve red kodları

Her kural bir doğrulama sonucu (`rule_code`) yazar. Sonuç `review` ise aday incelemeye düşer ve inceleme
öğesinin `reason_code` alanı adayın ilk `review` sonucunun kodunu taşır; sonuç `failed` ise aday reddedilir.

### İncelemeye yollayan kodlar

Bu kodlardan birini alan aday reddedilmez, incelemeye düşer ve güven eşiğiyle otomatik onaylanmaz.

| Neden kodu | Ne zaman | Üretildiği yer |
|---|---|---|
| `missing_evidence` | Adayın kaynak alıntısı yok | `pipeline_management.py:_evidence_findings` |
| `quote_not_in_segment` | Alıntı, bağlı olduğu segmentin metninde geçmiyor | aynı |
| `value_not_in_quote` | Kimlik alanındaki metin değeri adayın hiçbir alıntısında geçmiyor ve kaynak biriminin `external_ref` değerine de eşit değil | `pipeline_management.py:_merge_key_grounding_findings` |
| `property_value_not_allowed` | Değer, özelliğin izinli değer listesinde yok | `pipeline_management.py:_enum_findings` |
| `node_confidence_threshold` | Düğüm adayının güveni, tipinin `confidence_threshold` değerinin altında | `pipeline_management.py:_validate_candidate_node` |
| `relation_confidence_threshold` | İlişki adayının güveni, ilişki tipinin eşiğinin altında | `pipeline_management.py:_validate_candidate_relation`, `review_management.py:_pending_relation_review` |
| `missing_relation_merge_key` | İlişkinin kimlik alanlarından biri boş | aynı |
| `relation_dependency_review` | İlişkinin uç düğümlerinden biri incelemede; düğümler onaylanınca öğe kendiliğinden kapanır | `pipeline_management.py:_validate_candidate_relation`, `review_management.py:DEPENDENCY_REVIEW_REASON` |
| `potential_duplicate_node` | Koşuda aynı kimlikte birden çok düğüm adayı var; insan kararı taşıyan, yoksa güveni en yüksek olan dışındakiler işaretlenir | `pipeline_management.py:_flag_duplicate_candidate_nodes` |
| `potential_duplicate_relation` | Koşuda aynı kimlikte birden çok ilişki adayı var | `pipeline_management.py:_flag_duplicate_candidate_relations` |
| `schema_type_proposal` | Model şemada olmayan bir tip yazdı; o aday düşer, diğerleri kalır | `extraction_management.py` |
| `schema_property_proposal` | Model tipte tanımlı olmayan bir özellik yazdı; özellik adaydan çıkarılır | `extraction_management.py` |

Şema önerisi öğeleri de açık inceleme öğesidir; kapanmadan koşu commit edilmez.

### Reddeden kodlar

Şemaya yapısal olarak uymayan aday incelemeye gitmez, reddedilir.

| Kural kodu | Ne zaman | Üretildiği yer |
|---|---|---|
| `node_type_exists` | Düğüm tipi şemada yok. Çıkarım çağrısında tanımsız tip bu kurala gelmeden `schema_type_proposal` olarak düşer | `pipeline_management.py:_validate_candidate_node` |
| `required_node_property` | Zorunlu bir düğüm özelliği boş | aynı |
| `node_merge_key` | Düğümün kimlik alanlarından biri boş | aynı |
| `relation_type_exists` | İlişki tipi şemada yok | `pipeline_management.py:_validate_candidate_relation` |
| `relation_candidate_refs` | İlişkinin gösterdiği aday düğüm koşuda yok | aynı |
| `relation_from_type`, `relation_to_type` | Uç düğümün tipi, ilişki tipinin beklediği tip değil | aynı |
| `required_relation_property` | Zorunlu bir ilişki özelliği boş | aynı |
| `relation_dependency_rejected` | İlişkinin uç düğümlerinden biri reddedildi | aynı, `review_management.py:DEPENDENCY_REJECTED_REASON` |

### Kayıt kodları

| Kural kodu | Anlamı | Üretildiği yer |
|---|---|---|
| `human_review_decision` | Adayın durumunu inceleme kararı belirledi; yeniden doğrulamada kapılar o adaya uygulanmaz | `pipeline_management.py:HUMAN_DECISION_RULE_CODE` |
| `candidate_node_valid`, `candidate_relation_valid` | Aday doğrulamadan geçti; kabul kaydında `auto_validated` politikasının kural kodudur | `pipeline_management.py`, `review_management.py:PASSED_VALIDATION_RULE_CODES` |
| `canonical_node_match`, `canonical_relation_match` | Aday, grafta var olan bir düğüme ya da ilişkiye çözülüyor | `pipeline_management.py:_annotate_canonical_matches` |

Karşılaştırma `normalize_for_grounding` ile yapılır: Arapça hareke ve harf biçimi katlaması ile genel
büyük-küçük harf katlamasının bileşimi (`domain/hadith/grounding.py`).

Alıntı ve değer kapıları yalnız gerçek bir çıkarım çağrısından gelen adaylara uygulanır; API'den elle
girilen adaylara uygulanmaz (`pipeline_management.py:_grounding_segments`).

## Karar kaydı

- Her inceleme kararı `review_decisions` tablosuna eklenir: `reviewer_id`, karar zamanı, `duration_ms`,
  eylem, düzeltmede önceki ve sonraki değer. Kayıtlar silinmez ve üzerine yazılmaz.
- İnsanın karar verdiği adayın durumunu yeniden doğrulama ya da bağımlılık tazelemesi değiştirmez.
- `GET /api/runs/{run_id}/acceptance-records`, onaylanmış her aday için ya insan kararını ya da
  `auto_validated` politikasını döndürür. Kabul kayıtları saklanmaz; istek anında kararlardan ve
  doğrulama sonuçlarından hesaplanır (`review_management.py:list_acceptance_records`).

## Bilinen sınırlar

| Sınır | Etkisi |
|---|---|
| `Narrator` kimliği adın tam yazımıdır (hareke dahil) | Aynı kısa adı taşıyan farklı kişiler tek düğümde birleşir; aynı kişinin farklı hareke ya da yazımı ayrı düğüm olur. Ravi kimlik eşleştirmesi (L2) yoktur. Bu kimliğin referans üzerindeki taban çizgisi: `wiki/evaluation/engine-experiments.md`, "Ad yazımıyla kimlik" |
| Metin sınırından sonraki zincirler atılır | Bazı hadislerde gerçek devam zincirleri kaçar (Müslim 978: 14 referans mention'a karşı 7) |
| `و` ile bitişik yazılan ortak raviler tek mention kalır | Recall kaybı; `وكيع`, `وهب` gibi adlar yüzünden bölme kuralı eklenmedi |
| Mention aralığı uzayabilir (`أَبِيهِ ، قَال` gibi) | Katı eşleşme puanını düşürür |
| Kural tabanlı sağlayıcının çıktısı kapılardan yapısı gereği geçer | Bu koşul kapıların yakalama gücünü ölçmez |
| `anthropic` sağlayıcısının tel biçimi `properties` nesnesini `{name, value}` girdilerinin listesi olarak taşır | Claude Sonnet 5.5, effort `low` ile 36 hadiste ravi adını özellik anahtarı alanına yazdı; isnad-farkındalıklı koşulda 36 koşunun 30'u commit edilemedi. Claude Haiku 5.5 ile 300 hadiste bu görülmedi (`wiki/evaluation/engine-experiments.md`) |
| İlişki ayrıntı ucu ilişkiyi tipi ve iki uç düğümüyle adresler | Aynı iki ravi arasında aynı tipten birden çok kenar varsa (farklı hadis, zincir, konum) tek biri adreslenemez |
| Panel bir LLM yöntemini yalnız sunucu o sağlayıcıyı kabul ediyorsa listeler | Sağlayıcı listesi veren bir API ucu yoktur; panel bunu koşu başlatamayan bir istekle yoklar (`giraffegraph-core/frontend/src/modules/runs/methods.ts`) |
| Geri alma yok, kimlik doğrulama yok | Commit edilmiş koşu geri alınamaz; inceleyici adı istekle gelir ve doğrulanmaz |
| Hiçbir koşuda inceleme kararı verilmedi; referanslar platform ve kural etiketidir | Ölçülen sayılar etiket kümeleriyle uyumdur; insan altın standardı yoktur |

## Doğrulama durumu

| Ne | Durum | Kaynak |
|---|---|---|
| Bellek içi depoyla testler | `cd giraffegraph-core/backend && uv run pytest -q`: 285 test toplanır, 273 geçer, 12 atlanır (2026-10-12). Atlanan 12 test `real_db` işaretlidir | `giraffegraph-core/backend/tests/` |
| Gerçek veritabanı | `real_db` işaretli 12 test Alembic göçlerini, isnad akışını ve karar kaydını Postgres ve Neo4j'e karşı koşar. 2026-10-12'de yerel konteynerlerde PostgreSQL 16 ve Neo4j 5.26'ya karşı 12'si de geçti; o koşunun çıktısı dosya olarak kayıtlı değil. Yeniden üretim: `GG_TEST_POSTGRES_DSN`, `GG_TEST_NEO4J_URI`, `GG_TEST_NEO4J_PASSWORD` tanımlanıp `uv run pytest -q -m real_db` | `giraffegraph-core/backend/tests/conftest.py`, `tests/integration/test_realdb_*.py` |
| Gerçek LLM | `anthropic` sağlayıcısıyla Claude Haiku 5.5 (effort `low`) 300 hadiste üç koşulda koşuldu (2026-10-12) | `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/`, `wiki/evaluation/engine-experiments.md` |
| İnsan incelemesi | Hiçbir koşuda inceleme kararı verilmedi | aynı |

## Rules

- MUST: yeni bir kapı adayı reddetmez, incelemeye yollar ve kendi neden kodunu taşır. Gerekçe: red
  bilgiyi sessizce siler; incelemedeki aday sayılabilir.
- MUST: motor koduna hadise özgü ad girmez; alan davranışı strateji, şablon ya da sağlayıcı olarak
  eklenir. Gerekçe: Core genel bir motordur, hadis ilk vakadır. Kod bu kurala üç yerde uymaz:
  - `application/use_cases/pipeline_management.py` grounding karşılaştırma işlevlerini
    (`quote_in_segment`, `value_in_quote`, `value_equals_reference`) `domain/hadith/grounding.py`
    içinden içe aktarır; her projenin kapıları Arapça katlamalı bu normalizasyonla çalışır.
  - Zincir okuma kodu `Narrator` ve `NARRATED_FROM` adlarını sabit olarak taşır
    (`domain/exploration/chains.py:NARRATOR_NODE_TYPE`, `NARRATED_FROM_RELATION_TYPE`;
    `application/use_cases/exploration_management.py:ChainExplorationService`).
  - İsnad eklentileri (`IsnadSegmentation`, `RuleBasedIsnadProvider`) `bootstrap/container.py` içinde
    doğrudan kaydedilir; bir eklenti kayıt noktası yoktur.
- MUST: bu sayfadaki davranış commit edilip ekipçe kabul edildiğinde statü satırı güncellenir ve
  karar `wiki/decisions/` altına ADR olarak yazılır.
- SHOULD: `Narrator` düğüm sayısı raporlanırken kimliğin ad yazımı olduğu belirtilir.

## Source anchors

- `giraffegraph-core/backend/src/app/domain/hadith/segmenter.py` — `segment_isnad`, sîga deseni
- `giraffegraph-core/backend/src/app/domain/hadith/segmentation.py` — `IsnadSegmentation`
- `giraffegraph-core/backend/src/app/domain/hadith/grounding.py` — `quote_in_segment`, `value_in_quote`,
  `value_equals_reference`
- `giraffegraph-core/backend/src/app/infrastructure/template/catalog.py` — `ISNAD_TEMPLATE_SCHEMA`
- `giraffegraph-core/backend/src/app/infrastructure/llm/rule_based_isnad_provider.py`
- `giraffegraph-core/backend/src/app/infrastructure/llm/anthropic_provider.py` — tel biçimi
  (`EXTRACTION_WIRE_SCHEMA`, `_fold_wire_output`)
- `giraffegraph-core/backend/src/app/bootstrap/container.py` — sağlayıcı ve strateji kaydı
- `giraffegraph-core/backend/src/app/domain/exploration/chains.py`,
  `application/use_cases/exploration_management.py`, `interfaces/api/routers/chains.py` — zincir okuma
- `giraffegraph-core/backend/src/app/interfaces/api/routers/ingestion.py` — toplu yükleme ve işleme uçları
- `giraffegraph-core/backend/src/app/infrastructure/persistence/neo4j/repositories.py` — `commit_bundle`,
  `LOOKUP_INDEX_STATEMENTS`
- `giraffegraph-core/backend/src/app/application/use_cases/pipeline_management.py`,
  `extraction_management.py`, `review_management.py`
- `giraffegraph-core/backend/src/app/domain/shared/resolution.py` — `build_relation_identity_key`
- `giraffegraph-core/backend/migrations/versions/0005_add_relation_type_merge_keys.py`,
  `0006_add_review_decisions.py`
- `giraffegraph-core/backend/tests/integration/test_isnad_pipeline_api.py`,
  `test_grounding_extraction_api.py`, `test_review_decisions_api.py`, `test_chains_api.py`,
  `test_bulk_ingest_api.py`, `test_template_project_api.py`, `test_realdb_*.py`
- `giraffegraph-core/docs/guides/isnad-demo.md` — boş backend'den zincir okumaya API çağrı sırası

## Verification checklist

- [ ] `cd giraffegraph-core/backend && uv run pytest -q` geçiyor ve sayılar "Doğrulama durumu" tablosuyla aynı
- [ ] Üç tablodaki her kod `grep -rn "<kod>" giraffegraph-core/backend/src` ile bulunuyor
- [ ] `grep -rn "rule_code=\|reason_code=" giraffegraph-core/backend/src/app/application/use_cases` çıktısında
      tablolarda olmayan kod yok
- [ ] "Kod bu kurala üç yerde uymaz" listesindeki her içe aktarma ve sabit hâlâ yerinde; kalkan madde listeden silindi
- [ ] `git -C giraffegraph-core log -1` bu davranışı içeren bir commit gösteriyorsa statü satırı güncellendi
- [ ] Yeni bir kapı eklendiyse tabloya ve `correctness-measurement.md` L3 satırına işlendi

## Related docs

- `wiki/evaluation/correctness-measurement.md`
- `wiki/evaluation/engine-experiments.md`
- `wiki/evaluation/related-work.md`
- `giraffegraph-core/docs/guides/isnad-demo.md`
- `wiki/sources/claude-science-results/05_kod_degisiklik_listesi.md`
- `wiki/sources/claude-science-context/08_hadith_domain_primer.md`

## Last updated

2026-10-13
