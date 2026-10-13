# 07 — Vakalar B ve C: kod tabanı wiki'si ve Kur'an uygulaması

## B. Endüstriyel kod tabanı wiki'si (yazarın işyeri, anonimleştirildi)

> Gizlilik: Bu vaka yazarın çalıştığı şirketin özel kod tabanından. Dosyalar pakete **kopyalanmadı**. Aşağıda sadece yöntem ve sayılar var. `06a`'daki `B2C_Faq` örneği bu kod tabanından geliyor.

**Bağlam:** Üç kardeş repo (C#/.NET backend + iki React istemci, SQL Server), çok kiracılı CMS + B2C seyahat sitesi. Wiki ayrı bir repoda duruyor ve hem insanlar hem AI ajanları (Claude Code) için ilk okuma yüzeyi.

**Ölçek (2026-09-30):** ~185 markdown sayfa. DDD bounded context'lere göre `domains/<context>/<module>/{module,api,ui}.md`, `cross-cutting/<area>/`, `architecture/`, `decisions/` (24 ADR, immutable, supersession ile), 13 Agent Skill (prosedürel iş akışları), 6 deterministik hook (guard), `known-issues.md` (kodun kendi dokümanıyla çeliştiği ~35 açık CONFLICT kaydı, numaralar asla yeniden kullanılmıyor). Wiki git geçmişi 50 commit.

**Kalite kuralları (`context-quality.md`, özet):**
1. **SSOT:** Her olgunun tek bir yeri var, diğer yerler link veriyor. Birbirine yakın çift sayfalar en kötü distractor sınıfı sayılıyor.
2. **Her davranış/API/güvenlik iddiası çözülebilir bir `file:symbol` anchor'ı ile bitiyor** (repo-köklü). Çözülmeyen anchor bir DRIFT bug'ı.
3. **Kod otoritedir.** Önem sırası: CONFLICT > DRIFT > staleness > bloat. Doğrulanamayan iddia silinir.
4. **BLUF, atomik, tek kavram/dosya.** Sayfa ~80 satırı geçer veya bağımsız değişiyorsa bölünüyor. "Bu satırı silmek bir hataya yol açar mı?" testi uygulanıyor.
5. **Yalnızca güncel durum.** Tarihçe sadece ADR'de. Yasaklı kelimeler: previously, legacy, used to, önceden, eskiden…
6. **Dürüst boşluk > emin uydurma.** Kullanılan işaret: "Not recorded — verify in code". ADR'de sadece gerçekten tartılmış alternatifler yazılıyor.
7. Sadece İngilizce (retrieval bulanıklığını önlemek için).
8. **Retrieval-şekilli adlandırma:** Ajanın sorgulayacağı kelimeler (gerçek sembol adları) kullanılıyor, gerekirse `Aliases:` satırı ekleniyor.

**Deterministik zorlama:** Hook'lar (PreToolUse/PostToolUse/Stop) wiki markdown'ında dil ve anchor-kök kuralını kontrol ediyor. Oturum sonunda "kod değişti ama wiki değişmedi" durumunda wiki-sync prosedürünü hatırlatıyor. Bir hook kural **sahibi** olamaz, kuralın sahibi olan dokümana işaret eder. Ayrıca `wiki-check` adlı bir drift denetçisi var (anchor çözümleme, davranış/API kontratı, index ağacı).

**Skill tetikleme eval'i:** `cases.tsv` (beklenen skill + prompt, pozitif ve negatif çiftler), headless `claude -p` sürücüsüyle çalışıyor. Baseline 2026-08-20: dokuz iş akışı skill'inde Sonnet ile 18/18. Bilinen sınır: "review" türü promptlar skill yerine yerleşik davranışı tetikliyor.

**Önceki ölçüm (`06a`):** 120 dokümanlık bir wiki'de 315 repo-köklü anchor'ın 315'i çözüldü, ama 296 bare mention (ör. `FaqDtos.cs`) makineyle doğrulanamıyor.

**Bu vakanın araştırma için önemi:**
- Bu wiki, `06a`'nın "türetilebilir olanı saklama" tezine **karşı pratik bir uzlaşma**. Modül dokümanları türetilebilir olgular (tablo, controller, akış) içeriyor, ama her birine anchor bağlanıyor ve drift denetleniyor. `known-issues.md`'deki ~35 CONFLICT, bu saklanan önbelleğin gerçekten çürüdüğünün ampirik kanıtı. Doküman aylarca kodla çelişik kalmış.
- Yani soru "saklamak mı, saklamamak mı" değil. Soru şu: **hangi olgu sınıfı saklanmalı, hangisi her sorguda türetilmeli, saklananın tazeliği nasıl garanti edilmeli?**
- Açık kaynak bir kod tabanında tekrarlanabilir deney fikri: git geçmişinden doküman↔kod drift oranını zaman içinde ölçmek, sonra "wiki + anchor + linter" ile "sadece ajan grep'i" ve "LLM-üretimli wiki (DeepWiki tarzı)" yaklaşımlarını aynı soru setinde karşılaştırmak (`11`).

## C. Kur'an uygulaması (ikinci plan)

**Bağlam:** Expo mobil istemci + App Service (FastAPI) + Resource Service. Resource Service `knowledge_units`, içerik embedding'leri, anahtar kelime taksonomisi ve **Neo4j grafı** tutuyor. Kaynak türleri arasında Kur'an meali (6236 ayet) var.

**Olay (yazarın Claude Code belleğinden, 2026-07-30):**
- `knowledge_units` içindeki Türkçe meal gerçekte **Elmalılı Hamdi Yazır** tercümesi. Ama `source_provider` alanı, bir JSON dosyası ve ham veri dosyasının provenance altbilgisi "Diyanet İşleri" diyor. Sebep: upstream (fawazahmed0/quran-api) `tur-diyanetisleri1` edisyonu, kendi `tur-elmalilihamdiya` edisyonunun yanlış etiketlenmiş ve ASCII'ye bozulmuş bir kopyası. İkisinin kelime kelime aynı olduğu karşılaştırmayla kanıtlandı.
- Metin onarıldı: 5912 ayette ş/ğ/ı/İ geri getirildi, noktalama düzeltildi, Âl-i İmrân 3:9–3:21 yeniden numaralandı, dipnot artıkları temizlendi.
- **Ama 6236 embedding yeniden üretilmedi.** Vektörler hâlâ bozuk metni kodluyor.

**Araştırma için önemi:** Bu vaka üç şeyi aynı anda gösteriyor. (1) **Provenance, veri kalitesinin birinci sınıf olgusu.** Yanlış bir atıf, üç ayrı yerde kopyalanıp saklanmış (SSOT ihlali). (2) **Türetilmiş önbellek (embedding) kaynağı onarılınca bayatlıyor** ve invalidation mekanizması olmadığı için bunu kimse fark etmiyor. Bu tam olarak `06a`'daki early-cutoff/invalidation problemi. (3) Hatayı yakalayan şey model değil, **insan kararıyla kaydedilmiş bir not** (ajan belleği = karar defteri). Genel mimari, bu üç failure mode'u yapısal olarak önlemeli: tek provenance kaydı, kaynak hash'ine bağlı türetilmiş artefaktlar, karar olayları.
