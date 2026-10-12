# 05 — Kod denetiminin doğrulanması ve önceliklendirilmiş değişiklik listesi

## Bölüm A — `05_claims_vs_code_gap_audit.md` bulgularının bağımsız doğrulaması

`14_giraffegraph_core_code_bundle.md` içindeki kaynak kod (20 dosya, 4013 satır) dosya dosya
ayrıştırılıp `05`'teki 17 iddianın her biri anchor'ıyla karşılaştırıldı.

**Sonuç: koddan doğrulanabilen 15 bulgunun 15'i doğru; anchor satır numaraları da doğru.**
Kalan ikisi bu paketten doğrulanamaz: **#14** (şema öneri özelliği) — bundle *alıntı* olduğu için
"bundle'da yok" ile "repoda yok" aynı şey değil; **#15** (LICENSE yokluğu, 2 commit, `uv.lock`
senkronsuzluğu, 47/48 test) — repo erişimi gerektirir, bu oturumdan teyit edilemedi
`[UNVERIFIED — repoya bakılmalı]`. `05`'i hazırlayan denetim, doğrulanabilen kısmında **hatasız**;
bu paketteki en sağlam belge.

Doğrulama kanıtları (özet):

| `05` # | İddia | Doğrulama |
|---|---|---|
| 1 | Yüksek güvenli aday insan görmeden VALIDATED | `pipeline_management.py:302-330` — eşiği geçen node doğrudan `CandidateStatus.VALIDATED`. `commit_management.py:36-57` — commit yalnızca *açık review item* veya *pending aday* varsa engelleniyor; otomatik VALIDATED olan aday review item **üretmiyor**, dolayısıyla geçiyor. ✔ |
| 2 | `quote` segment metninde aranmıyor | `extraction_management.py:420-435` — `_build_evidence_ref` yalnızca `segment_id in valid_segment_ids` kontrolü yapıyor. Tüm bundle'da `quote` 12 kez geçiyor, hiçbirinde karşılaştırma yok; `start_offset` 5 kez geçiyor, hiçbirinde doğrulama yok. ✔ |
| 3 | Tanımsız tip tüm batch'i düşürüyor | `extraction_management.py:542-569` — `_resolve_node_type`/`_resolve_relation_type` `RuleViolationError` fırlatıyor, `_normalize_output` içinden yukarı propagate ediyor. Aday-bazında yakalama yok. ✔ |
| 4 | JSON-Schema / `data_type` / `enum_values` doğrulanmıyor | `jsonschema` ve `json_schema` bundle'da **0 kez** geçiyor. `data_type` 4, `enum_values` 4 kez geçiyor; ikisi de yalnızca tanım (`contracts.py:26,30`) ve **prompt payload'ına serileştirme** (`extraction_management.py:270,274,294,298`) noktalarında. `cardinal*` 0 kez. ✔ **Nüans:** bu alanlar modele *bildiriliyor* ama zorlanmıyor — "modele söylenmiş, kontrol edilmemiş". |
| 5 | Geri alma yok, commit atomik değil | `revert`/`rollback` bundle'da **0 kez**. `neo4j/repositories.py:33-113` — `commit_bundle` her düğüm ve ilişki için ayrı `session.execute_write` çağırıyor; `GraphDelta` Postgres'e en sonda yazılıyor. ✔ |
| 6 | `ReviewItem`'da reviewer ve karar zamanı yok | `domain/review/entities.py:10-19` — alanlar: `review_item_id, run_id, item_type, item_ref, reason_code, payload_json, status, reviewer_note, created_at`. `reviewer_id` ve `decided_at` bundle'da **0 kez**. ✔ |
| 7 | ER = NFKC + casefold, diyakritik katlaması yok | `domain/shared/resolution.py:96-101`. Çalıştırıldı: `normalize_text("Ebû Hüreyre") != normalize_text("Ebu Hureyre")`. ✔ |
| 8 | Neo4j identifier regex Türkçe adları reddediyor, kontrol commit anında | `neo4j/repositories.py:26` → `IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")`, kullanım `:1109-1110` (`_quoted_identifier`). `contracts.py:36` → `NodeTypeDefinitionInput.name: str = Field(min_length=1, max_length=80)` — **desen yok**. ✔ |
| 9 | İlişki MERGE anahtarı `(a, type, b)`, kenar çöküyor | `neo4j/repositories.py:435-443` → `MERGE (from_node)-[r:TYPE {project_id, relation_type}]->(to_node) ... SET r += $properties`. ✔ |
| 10 | Node özellikleri sessizce üzerine yazılıyor | `neo4j/repositories.py:318` → `SET n += $properties`. ✔ |
| 11 | Alan kuralı kancası yok | `pipeline_management.py` içinde validation kuralları sabit metodlar. ✔ |
| 12 | Aday yapısı düğüm-merkezli, `confidence` kalibre değil | `extraction_management.py:60-86`. Pilotta ölçüldü: **AUC 0,626**, 318 adayın 261'i tam olarak 0,90. ✔ ve niceliklendirildi |
| 13 | Yalnız OpenAI-uyumlu provider | `openai_provider.py`, `temperature: 0` (`:95`). ✔ |
| 16 | Yalnızca paragraf segmentasyonu | `pipeline_management.py:61-79` → `if strategy != "paragraphs": raise RuleViolationError`. ✔ |
| 17 | Tüm segmentler tek LLM çağrısında | `extraction_management.py:149-161` — tek `_build_prompt_payload` + tek `generate_structured`. ✔ **Pilotta patladı:** 50 çağrının 6'sı `max_tokens` sınırında kesildi. |

### Bölüm A2 — `05`'te olmayan, koddan doğrulanmış dört yeni bulgu

**N1 — Property düzeyinde şema sapması hem ölçülmüyor hem sessizce kalıcılaşıyor. (CONFLICT)**
`SuggestedNodeContract.properties: dict[str, object]` (`extraction_management.py:65`) ve sınıf
`model_config = ConfigDict(extra="ignore")` (`:61`). Yani:
- Modelin uyduracağı **üst düzey** alanlar sessizce **atılır** (hata değil) — prompt "Do not add any
  fields outside this schema" diyor, kod bunu *sessizce affediyor*, ölçüm yapmıyor.
- Modelin uyduracağı **property anahtarları** hiçbir kontrolden geçmez, `CandidateNode.properties`'e
  girer ve commit'te `SET n += $properties` ile Neo4j'ye **yazılır**.
→ "Sıfır şema-dışı yazım" taahhüdü **yalnızca tip adları için** doğru. Asıl drift yüzeyi korumasız.
Bu, H2'nin property düzeyine taşınmasının kod tarafındaki gerekçesidir.

**N2 — Aday-düzeyi duplicate anahtarı ile canonical MERGE anahtarı tutarsız. (CONFLICT)**
`resolution.py:36-56` (`build_candidate_relation_resolution_key`) duplicate anahtarına
`normalized_payload_key(candidate_relation.properties)` **dahil ediyor**. `neo4j/repositories.py:435-438`
ise MERGE anahtarına properties'i **dahil etmiyor**. Sonuç: aynı çift arasında farklı özellikli
(ör. farklı `hadith_id`, farklı `sigha`) iki ilişki adayı "duplicate değil" sayılır, ikisi de
VALIDATED olur, commit'te **tek kenara çöker ve ikinci kayıt birincinin üzerine yazar.**
**Hiçbir review item oluşmaz, hiçbir hata verilmez, bilgi sessizce kaybolur.** İsnad için ölümcül:
bu tam olarak `05` #9'un mekanizması ama `05` bunun *aday düzeyinde tespit edilemediğini*
kaydetmemiş.

**N3 — Merge key'i olmayan aday hiç dedup edilmiyor. (GAP)**
`resolution.py:59-62` (`candidate_node_identity_key`): `merge_key_payload` boşsa kimlik
`f"candidate::{candidate_node_id}"` oluyor — yani **her zaman yeni düğüm**. Ve
`build_canonical_merge_key` (`:65-72`) boş payload'da `fallback_payload`'a düşüyor, yani merge key
tüm properties'in hash'i olabiliyor → property'si bir harf farklı iki aday ayrı düğüm.
H4'ün baz çizgisi bu davranışı da içeriyor; ölçümde ayrıştırılmalı.

**N4 — Prompt, kodun kendi davranışını yanlış anlatıyor. (WEAK, ama dogfooding açısından ironik)**
`prompt_catalog.py:39`: *"'node_type' and 'relation_type' must exactly match schema names
(case-sensitive)."* Kod ise `_resolve_node_type`'da `requested_type.strip().casefold()` yapıyor
(`extraction_management.py:548`) — **case-insensitive**. Prompt metni kodun sözleşmesiyle drift
hâlinde. `06a`'nın anchor-check disiplini tam olarak bunu yakalamak için var; projenin kendi
prompt kataloğunda uygulanmamış.

---

## Bölüm B — Önceliklendirilmiş değişiklik listesi

Sıralama ölçütü: **(ölçülmüş getiri) / (iş günü)**, ve "kamuya verilen sözü tutar mı".
Tahmini iş günleri 2–3 kişilik lisans ekibi için.

### P0 — Deneyi mümkün kılan, olmadan hiçbir sayı anlamlı olmayan (toplam ~9 gün)

| # | Değişiklik | Dosya | Gün | Neden P0 |
|---|---|---|---|---|
| **C1** | **Değer grounding kapısı:** `normalize(property_value) ⊆ normalize(quote) ⊆ normalize(segment.text)` + offset tutarlılığı. İhlal → REVIEW (RED değil), `reason_code="value_not_in_quote"` | `extraction_management.py` `_build_evidence_ref`, `pipeline_management.py` validate | 1,5 | **Pilotta %10,1 yakalama.** Sitenin "ungrounded claims are flagged" sözünün tek gerçek karşılığı. `quote ⊂ segment` tek başına pilotta 0/605 yakaladı — o da eklensin ama tek başına yeterli değil |
| **C2** | **Per-item fail + `schema_proposal` tablosu:** tanımsız tip gelirse yalnız o aday REJECTED, `schema_proposals(run_id, proposed_type, kind, count, sample_evidence)` kaydı | `extraction_management.py:542-569`, `_normalize_output` | 2 | Şu an bilgi kaybı **ölçülemiyor**. H2'nin anlamlı versiyonu buna bağlı. Sitenin "proposals, never silent additions" sözü de |
| **C3** | **`decision_events` (append-only) + içerik-adresli hedef:** `actor_id, decided_at, duration_ms, target_hash, action, before, after, rationale, evidence, supersedes, policy_version`. `target_hash = sha256(span_hash‖mention_text‖node_type)` | yeni `domain/decision/`, `review_management.py` | 3 | **Olmadan proje çöker:** `ReviewItem.item_ref = candidate_id` olduğu için 5 model × 3 tekrar denendiğinde 500 hadislik insan emeği her run'da sıfırlanır. Ayrıca "uzman dakikası" (sitenin 3. araştırma sorusu) ölçülemez ve κ için kodlayıcı ayrımı yapılamaz |
| **C4** | **ASCII teknik ad + Türkçe `display_name`; identifier doğrulaması şema oluşturma anına** | `contracts.py` `NodeTypeDefinitionInput.name` pattern, `RelationTypeDefinitionInput.name` | 0,5 | Aksi hâlde Hadith Schema (`doğdu`, `Künye`) **insan onayından sonra** commit anında patlar |
| **C5** | **Hadis-kapsamlı ilişki anahtarı** (minimum) veya `Transmission` reifikasyonu (tam). Aynı anda aday-düzeyi duplicate anahtarını canonical anahtarla hizala (N2) | `neo4j/repositories.py:435-443`, `resolution.py:36-56` | 2 | Aksi hâlde zincir-düzeyi metrikler ölçülemez ve **bilgi sessizce kaybolur** |

### P1 — Deney kalitesini belirleyen (toplam ~8 gün)

| # | Değişiklik | Gün | Neden |
|---|---|---|---|
| **C6** | **`DomainRule` protokolü + kural kayıt defteri.** `Candidate → Verdict{pass,review,reject,reason}`. İlk kurallar: Peygamber/Allah blocklist (**pilotta %6,0**), muâsara (vefat<doğum), likâ kaydı yok, tabaka tutarlılığı | 2 | E-3 taahhüdü. Kural sonuçları REJECTED değil **REVIEW + gerekçe** |
| **C7** | **Deterministik isnad segmenter** (`Segmenter` protokolü): isnad/matn ayrımı, tahvîl (`ح`) bölme, sîga tokenizasyonu, **karakter offset'leri**. `pilot_isnad.py` başlangıç noktası | 2,5 | Pilotta tek başına F1 0,879. Ayrıca C1/C3'ün offset kontrolü buna bağlı. `05` #16 |
| **C8** | **Zincir-başına çağrı + chunking:** `SourceUnit` = bir hadis, LLM çağrısı = bir zincir | 1 | Pilotta 50 çağrının 6'sı kesildi; 8+ ravili zincirlerde recall 0,654 |
| **C9** | **`TransformRule` protokolü (sınıf 2b):** `(verbatim, asserted) → bool`. İlk kural: Arapça i'râb hâl normalizasyonu, honorifik temizleme | 1,5 | C1 kapısının yakaladığı 32 ihlalin **13'ü (%40,6)** meşru kanonikleştirme (`pilot_g3_crosstab.json`); bunlar otomatik geçmeli ama **kural sürümüyle deftere yazılmalı**. Kalan 19'u (%59,4) gerçek hata |
| **C10** | **Property şema doğrulaması:** `data_type`, `enum_values`, `required`, kardinalite; şemada olmayan property anahtarı → REVIEW + `schema_proposal`. `extra="ignore"` → `extra="forbid"` + sayım | 1 | N1. Form iddiası ("JSON-Schema ile tip ve kardinalite doğrulaması") şu an koddan güçlü |

### P2 — İtibar, tekrarlanabilirlik, yayın (toplam ~5 gün)

| # | Değişiklik | Gün | Neden |
|---|---|---|---|
| **C11** | **LICENSE (Apache-2.0 veya MIT) + README'de hadis vakası + `uv.lock` senkronu + kırık testin düzeltilmesi** (`test_prompt_catalog`) | 1 | Form "açık kaynak yayımlanmış" diyor, repoda LICENSE yok, 2 commit var. Değerlendirici bakarsa görür |
| **C12** | **Atomik commit** (tek transaction / `UNWIND`) + outbox deseni | 1,5 | "İdempotent ve geri alınabilir" iddiası |
| **C13** | **`rebuild.py`:** `rebuild(S, D, P)` → canonical grafı sıfırdan üret. **Revert = supersede + rebuild** | 1,5 | Sitenin "reversible" sözü; `12`'nin çekirdeği; T3 deneyinin ön koşulu |
| **C14** | **Risk-tabanlı yönlendirme politikası** (grounding ihlali + kural ihlali + ER belirsizliği), güven eşiği yerine. Politika sürümlü ve deftere yazılır | 1 | **AUC 0,626** — güven skoru yönlendirme sinyali olarak ölçülmüş biçimde zayıf |

### P3 — İyi olur, 6 ayda gerekmez
Anthropic/yerel provider (`05` #13; `OPENAI_BASE_URL` ile çözülebilir) · şema öneri özelliği
(site iddiası #14) · merge öneri UI'ı · artımlı materialize · conformal yönlendirme.

---

## Bölüm C — Sitedeki sözlerin düzeltilmesi (kodla uyumlu hâle getirme)

C1–C5 ve C13 yapılsa bile şu üç cümle hâlâ yanlış kalır. Kod düzeltmesiyle **birlikte** metin de
değişmeli:

| Site cümlesi | Durum | Önerilen metin |
|---|---|---|
| "**Nothing enters the graph unapproved.**" | Otomatik kabul varsa **yanlış**. Kaldırılırsa insan bütçesi patlar | "Every fact enters the graph either through a human decision or through an explicitly recorded policy — and the record says which." (`12` §4) |
| "Ungrounded claims are flagged" | Şu an **hiçbir şey** kontrol edilmiyor | C1 yapıldıktan sonra doğru olur. C1'den önce cümle kalkmalı |
| "every change is tracked, auditable and **reversible**" | Geri alma yok | C13'ten sonra doğru olur. C13'ten önce "auditable" kalır, "reversible" kalkar |
| "AI can suggest a schema from your first few documents" | Özellik **yok** | Kaldır veya "planned" etiketi koy |
| "**Can I use it today? Not yet**" ↔ form: "açık kaynak yayımlanmış, uçtan uca çalışır" | Çelişki | Form doğru okunuşla haklı (CORE gerçekten çalışıyor, 47/48 test geçiyor). Site "Not yet" yerine **"The engine runs; the hadith domain layer and the paper are in development"** demeli. LICENSE eklenmeli |
| Katkıcı listesi: formda İbrahim Çakır, sitede Alperen Ulukaya | Tutarsızlık | İkisi de listelensin, rolleri yazılsın. TÜBİTAK formu bağlayıcı olduğundan formdaki isimler değişmemeli |
