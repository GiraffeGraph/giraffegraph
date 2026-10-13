# 12 — Sentez hipotezi: Kaynak + Karar Defteri + Türetilmiş Görünümler

> Bu belge Claude Code'un, yazarın üç çalışmasını (GiraffeGraph, Cache & Ledger, kod wiki pratiği) birleştiren **sınanacak hipotezidir**. Kabul edilmiş bir karar değildir. Claude Science'tan bunu **çürütmeye çalışması**, alternatiflerle karşılaştırması ve gerekirse reddetmesi isteniyor.

## 0. Gerilim

- `06a` şunu söylüyor: *Türetilebilir olan bir önbellektir, saklama, yeniden üret. Türetilemeyen bir karardır, bir kez sakla.*
- GiraffeGraph ise tam tersini yapıyor: kaynaktan **türetilen** LLM çıkarımlarını kalıcı "canonical" grafa yazıyor. `06a`'nın mantığıyla bu, saklanan bir önbellek.
- Kod wiki'si (`07`) arada duruyor. Türetilebilir olguları saklıyor, ama anchor'larla bağlıyor ve drift'i denetliyor. Sonuç: ~35 kez çürüme görülmüş.

Üçü aynı problemin farklı noktaları. Aradaki fark **türetme maliyeti ve belirlenimciliği**.

## 1. Hipotez: dört olgu sınıfı

Her bilgi katmanı şunun fonksiyonudur: **V = P(S, D)**
- **S (Sources):** Değişmez, içerik-adresli (hash'li) ham kaynaklar. Kod + git, hadis metinleri, meal edisyonları.
- **D (Decisions):** Append-only karar defteri. İnsan/uzman/otorite hükümleri: kabul, red, düzeltme, **varlık birleştirme/ayırma**, otoriteye bağlama, şema önerisi kabulü, çelişki çözümü, provenance tespiti, mimari niyet (ADR). Her kayıt: kim, ne zaman, neye (içerik-adresli hedef), gerekçe, dayanak, supersedes.
- **P (Procedures):** Sürümlü türetme prosedürleri. Parser'lar, LLM prompt + model + parametreler, kural setleri, şema sürümü.
- **V (Views):** Türetilmiş her şey. Aday üçlüler, canonical graf, markdown wiki sayfaları, embedding'ler, arama indeksleri.

Olgular dört sınıfa ayrılır:

| Sınıf | Tanım | Politika | Örnek |
|---|---|---|---|
| **1. Ucuz-türetilebilir** | S'den deterministik ve ucuz türetilir | **Saklama.** Sorgu anında hesapla | Kodda "controller nerede" (grep). Hadiste isnad metni içindeki sîga lafızları |
| **2. Pahalı-türetilebilir** | S'den türetilir, ama pahalı ve/veya deterministik değil (LLM) | **Memoize et, senkronize etme.** Çıktıyı `hash(S_dilimi, P_sürümü)` anahtarlı dondurulmuş artefakt olarak sakla. Asla elle düzenleme. Girdi veya prosedür değişince geçersiz say | LLM aday üçlüleri, embedding'ler, LLM-üretimli özetler |
| **3. Karar** | Hiçbir S'den türetilemez. İnsan veya otorite hükmü | **Defterde bir kez sakla** (write-once, forward-link, türetilmiş back-link, supersession kuralla) | "İbn Uyeyne = Süfyân b. Uyeyne", "bu üçlü reddedildi", "meal Elmalılı'dır", "FAQ kendi item'larına sahiptir" |
| **4. Makine-denetlenebilir değişmez** | S, D, V üzerinde deterministik kontrol | **Linter:** işaretler, asla onaylamaz. Çıktısı karar değil, karar *talebi* (review) | Şema uyumu, alıntı ⊂ segment, muâsara, anchor çözümleme, SSOT ihlali |

**Kilit hamle (sınıf 2):** `06a`, LLM çıktısı deterministik olmadığı için early-cutoff'un çalışmadığını gösteriyor. Çözüm şu: eşitliği **çıktıda değil girdide** kontrol etmek. Çıktı bir kez üretilir ve içerik-adresli olarak dondurulur. Bu, derleyici önbelleği değil, bir **ölçüm kaydıdır** (hangi model, hangi prompt, hangi kaynakla ne dedi). Senkronizasyon hiç denenmez. Yeniden üretim, yeni bir kayıt demektir.

**Kilit hamle (sınıf 3):** Kararlar **aday UUID'lerine değil, içerik-adresli hedeflere** bağlanır: kaynak span hash'i, mention metni + bağlamı, otorite ID'si, üçlü imzası. Böylece model veya prompt değiştiğinde yeniden çıkarım yapılsa bile **insan kararları kaybolmaz, yeniden uygulanır.** Mevcut kodda `ReviewItem.item_ref = candidate_id` olduğu için bu yapılamıyor. Yeni bir run, tüm insan emeğini sıfırlıyor.

## 2. Temsil seçimi bir görünüm seçimidir

KG mi, markdown mı, vektör mü sorusu çekirdek bir karar değil, **V katmanında sorgu iş yüküne göre** verilen bir karar. Aynı S+D'den birden fazla görünüm üretilebilir:
- **Graf görünümü:** Yol ve ağ sorguları için (isnad zinciri, ortak halka, muâsara kontrolü). Hadis için KG'yi haklı çıkaran şey bu sorgu sınıfı.
- **Sayfa görünümü (md):** Niyet, açıklama, "nasıl genişletirim" soruları için (kod wiki'si). Kararlar (sınıf 3) sayfa olarak okunur. Türetilebilir kısımlar ya anchor olarak kalır ya da sorgu anında üretilir.
- **Vektör/metin indeksi:** Bulanık geri çağırma için. Her zaman sınıf 2 kuralına tabidir (kaynak hash'ine bağlı).

## 3. Üç vakaya eşleme

| | A. Hadis | B. Kod wiki'si | C. Kur'an uygulaması |
|---|---|---|---|
| S | Hadis metinleri (edisyon + hash), rical kaynakları | Kod + git | Meal edisyonları (doğrulanmış upstream + hash) |
| D | Kabul/red/düzeltme, ravi merge/split, otorite linking, tarih çelişkisi çözümü, şema önerisi | ADR'ler, niyet notları, known-issue kararları | Provenance tespitleri ("bu Elmalılı"), onarım kararları |
| P | İsnad parser, LLM çıkarım (model/prompt sürümü), ER, kurallar | Anchor çözücü, (opsiyonel) LLM özetleyici | Ingest scriptleri, embedding modeli |
| V | Canonical isnad grafı, ravi sayfaları, istatistikler | Modül sayfaları, index, repo map | knowledge_units, embedding'ler, Neo4j |
| Linter | Şema, grounding, muâsara/likâ/tabaka, over-merge şüphesi | Anchor-check, SSOT, current-state, dil | Edisyon kimliği ↔ etiket tutarlılığı, bayat embedding tespiti |

## 4. GiraffeGraph'a etkisi (somut)

- `review_items` → **decision_events** (append-only). Alanlar: `actor_id`, `decided_at`, `target` (içerik-adresli), `action`, `before`, `after`, `rationale`, `evidence`, `supersedes`.
- `candidate_*` tabloları → `extraction_records` (hash(S_dilimi, P) anahtarlı, değişmez).
- Neo4j canonical graf → **materialize edilmiş görünüm.** `rebuild(S, D, P)` ile yeniden üretilebilir. **Revert = olayı supersede et + yeniden üret.** "Reviewer'a kadar izle" doğrudan cevaplanır.
- Otomatik kabul, de facto bir "politika kararı"dır. O da deftere politika sürümüyle yazılmalıdır. Site metni ("nothing enters unapproved") ancak böyle dürüst hale gelir: "her giriş ya bir insan ya da açıkça kayıtlı bir politika tarafından onaylanır."

## 5. Sınanabilir tahminler

- **T1:** Canonical grafta kalıcı hataların çoğunluğu *şemaya uyan, yüksek güvenli, dayanaksız* üçlülerden gelir. Grounding kapısı (C3) bunları en ucuza keser.
- **T2:** Uzman zamanının çoğu ER/merge kararlarına gider. Aynı zamanda en yüksek kaldıraç da burada: tek bir merge kararı birçok mention'ı düzeltir.
- **T3 (ekonomik çekirdek):** Karar defteri boyutu graf boyutuna göre **alt-doğrusal** büyür (karar yeniden kullanımı). İkinci bir modelle veya yeni bir prompt'la yeniden çıkarım yapıldığında, içerik-adresli kararların %X'i otomatik yeniden uygulanır. Bu, "insan emeği modelden bağımsız birikir" iddiasıdır ve ölçülebilir.
- **T4:** Kod vakasında saklanan türetilebilir sayfalar zamanla r oranında drift eder. Kararlar drift etmez, sadece supersede edilir. Niyet soruları yalnızca D varken doğru cevaplanır, yapısal sorular D'siz de (grep ile) cevaplanır.
- **T5:** Temsil (KG vs md) değişince D ve S aynı kalır. Değişen sadece V ve P'dir. Yani aktarılabilirlik maliyeti, şema + kurallar + promptlarla sınırlıdır.

## 6. Karşı argümanlar ve riskler
- **Yeniden üretim maliyeti:** Büyük graflarda tam rebuild pahalı olabilir. Artımlı materialize gerekebilir, bu da `06a`'nın uyardığı karmaşıklığı geri getirebilir.
- **İçerik-adresli hedef zorluğu:** Yeni bir çıkarım, eski mention'ı biraz farklı span'le verebilir. Hedef eşleme bulanık olursa kararların yeniden uygulanması hataya açılır.
- **Karar defterinin kendisi bozulabilir:** Yanlış bir uzman kararı. `06a`: kararların doğal bir checksum'ı yok. Kararlar arası çelişki linter'ı gerekir.
- **Aşırı mühendislik riski:** 6 aylık lisans projesi için event sourcing ağır gelebilir. Asgari uygulanabilir versiyon: append-only karar tablosu + içerik-adresli hedef + rebuild scripti.
- **Alternatif hipotezler** (Claude Science karşılaştırmalı): (a) sadece RAG, kalıcı katman yok, (b) LLM-üretimli wiki + periyodik tam yeniden üretim, (c) klasik ETL + manuel küratörlük, LLM yok, (d) GraphRAG tarzı topluluk özetleri, (e) bi-temporal KG (Graphiti tarzı), (f) nanopublication tabanlı iddia modeli.

## 7. TÜBİTAK ile uyum
Hipotez formdaki kapsamı bozmuyor. CORE'a eklenen bir "mimari katman" olarak konumlanabilir. K-1..K-5 aynen korunur. Deney merdivenine (`11`) T3 eklenebilir: "ikinci model çalıştırmasında kararların yeniden uygulanma oranı". Bu, H-2 (100 üçlü/dk) yerine daha anlamlı bir verimlilik ölçütü olabilir. Formda değişiklik gerekip gerekmediği danışmana sorulmalı.
