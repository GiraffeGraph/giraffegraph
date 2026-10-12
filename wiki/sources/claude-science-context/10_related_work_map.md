# 10 — Asıl soruya yönelik literatür haritası

> **Tamamı `[VERIFY]`.** Bu liste Claude Code'un belleğinden geliyor (bilgi kesimi 2026 ortası). Başlık, yıl ve venue birincil kaynaktan doğrulanmadan atıf yapılmamalı. Yazarın doğrulanmış taraması `09_literature/` klasöründe (38 makale, değerlendirme metrikleri odaklı). Bu harita ise **tasarım** sorusuna odaklanıyor. Her grupta Claude Science'ın cevaplaması istenen soru belirtildi.

## 1. LLM ile KG inşası (şema-kısıtlı vs açık)
- Zhang & Soh 2024 — **EDC: Extract, Define, Canonicalize** (EMNLP 2024). Açık çıkarım, ardından şemaya kanonikleştirme. Drift'e "sonradan kanonikleştir" yaklaşımı.
- Microsoft **GraphRAG** (Edge vd. 2024). Topluluk özetleri, yüksek indeks maliyeti, artımlı güncelleme sorunları (`06a`'da tartışılıyor). **LazyGraphRAG**.
- **LightRAG**, **HippoRAG / HippoRAG 2**, **KGGen**, **iText2KG**, **AutoKG**, Neo4j **LLM Graph Builder** / `neo4j-graphrag` SimpleKGPipeline, LangChain `LLMGraphTransformer`, LlamaIndex `PropertyGraphIndex`.
- Ye vd. (Generative KGC review), Pan vd. 2024 (LLM+KG roadmap).
- **Soru:** Şema-önce (GiraffeGraph) mi, açık-sonra-kanonikleştir (EDC) mi daha az drift ve daha çok recall verir? Maliyetleri nedir?

## 2. Grounding / attribution doğrulaması
- **FActScore** (Min vd. 2023) atomik olgu doğrulama. **SAFE** (Wei vd. 2024). **AlignScore**, **SummaC** (NLI tabanlı tutarlılık). **AIS / Attributable to Identified Sources** (Rashkin vd.). **RARR**. **Chain-of-Verification** (Dhuliawala vd.).
- **Soru:** Üçlü düzeyinde en ucuz güvenilir grounding kapısı hangisi? Alıntı alt-dizesi mi, NLI mı, LLM-judge mı? Hangisi ne kadar recall kaybettirir?

## 3. Güven skoru ve seçici tahmin
- LLM'lerin sözel güven beyanlarının kalibrasyonu (Kadavath vd. 2022 "LMs (mostly) know what they know"; Xiong vd. 2024 verbalized confidence). **Conformal prediction** ile yönlendirme (conformal risk control, selective prediction).
- **Soru:** HITL'e yönlendirme kararı kalibre olmayan öz-beyana mı dayanmalı, yoksa conformal/risk tabanlı bir politikaya mı? İnsan bütçesi sabitken hata garantisi verilebilir mi?

## 4. HITL, aktif öğrenme, zayıf denetim
- **Snorkel** / data programming (Ratner vd.). Etiketleme fonksiyonları, yani deterministik kuralların istatistiksel birleştirilmesi.
- Aktif öğrenme ile insan etiket bütçesi optimizasyonu. **Prodigy**/**Argilla** tarzı annotasyon iş akışları.
- Crowdsourcing kalite modelleri: Dawid–Skene.
- **Soru:** Uzmanın dakikası en çok hangi kararlara harcanmalı? Belirsizlik örneklemesi mi, risk mi, yayılım etkisi mi (bir merge kararı çok kenarı etkiler)?

## 5. Entity resolution / linking
- **Fellegi–Sunter** olasılıksal kayıt bağlama. **Splink**, **dedupe**, **Magellan**, **Ditto** (transformer ER). LLM tabanlı ER (ör. "entity matching with LLMs" çalışmaları, 2023–2025).
- Arapça isim eşleme ve transliterasyon (Arabic name matching, romanization variants). Hadis ravi disambiguation çalışmaları `[VERIFY varlık]`.
- Metrikler: pairwise P/R/F1, **B-cubed**, **CEAF**, generalized merge distance.
- **Soru:** Otorite listesine linking + bağlamsal (zincir komşuluğu, tabaka) özellikler mi, saf string benzerliği mi? LLM ER'nin over-merge eğilimi nedir?

## 6. Provenance, sürümleme, olay kaynaklı (event-sourced) veri
- **W3C PROV-O**. **Nanopublications** (assertion + provenance + publication info). **Wikidata**'nın ifade düzeyinde referans ve rank modeli. **Datomic** (değişmez olgular, zamanda sorgu). **Bitemporal** modelleme. **Event sourcing / CQRS**. `06a`'daki double-entry, Git, RFC ve ADR soyağacı.
- **Soru:** Kanonik bilgi = f(kaynaklar, karar olayları) şeklinde yeniden üretilebilir tutulursa, geri alma, denetim ve sürüm "bedava" gelir mi? Maliyeti nedir (`12`)?

## 7. Kod tabanı bilgi katmanları ve ajan bağlamı
- **DeepWiki** (Cognition), Google **Code Wiki**, **Mintlify**/**Swimm** (`06a`: Swimm'in auto-sync'i ve hataları). **AGENTS.md** konvansiyonu, **CLAUDE.md**, Aider **repo map** (tree-sitter + PageRank), **Agent Skills**.
- Karpathy'nin "LLM wiki / LLM knowledge base" fikri (2026) `[VERIFY varlık ve içerik]`.
- Context-rot / **Lost in the Middle** (Liu vd. 2023/2024), uzun bağlam performans düşüşü (Chroma "context rot" raporu `[VERIFY]`).
- SWE-bench tarzı değerlendirmelerde bağlam dosyalarının etkisi (AGENTS.md'nin ajan başarısına etkisini ölçen 2025–2026 çalışmaları `[VERIFY varlık]`).
- **Soru:** Kod için saklanan wiki, "ajan her seferinde grep yapsın" yaklaşımına karşı hangi soru sınıflarında kazanıyor? Tipik aday: niyet/karar soruları. Hangilerinde kaybediyor (bayat bilgi)?

## 8. Ajan belleği
- **Mem0**, **Zep / Graphiti** (zamansal KG, bi-temporal kenarlar), **Letta/MemGPT**, **A-MEM**. `06a`: bir üretim denetiminde %97,8 çöp ve 808 kopya "prefers Vim" `[UNVERIFIED]`.
- **Soru:** Yazma kapısı olmayan bellek neden bozuluyor? Karar defteri + kaynak-bağlı olgu ayrımı bunu çözer mi?

## 9. Veri kalitesi ve doküman çürümesi
- Literate programming tarihi, doküman–kod drift çalışmaları, API doc smells, kod yorumu tutarsızlığı tespiti (ör. Wen vd. 2019 "large-scale study of code-comment inconsistencies" `[VERIFY]`).
- **Soru:** Drift oranı zaman içinde nasıl modellenir? Anchor-temelli linter drift'in ne kadarını yakalar?

## 10. Dijital hadis çalışmaları
- SemanticHadith, Sanadset, isnad otomatik ayrıştırma ve ravi ağı analizi çalışmaları (Arapça NLP; ör. "isnad parsing", "narrator chain extraction") `[VERIFY varlık]`. Juynboll/Motzki ortak halka analizi (ağ analizi yöntemi olarak).
- İslami QA faithfulness: `09_literature` [35]–[38] (IslamicMMLU, Agentic RAG for Islamic QA…).
- **Soru:** Hadis için KG çıkarımını değerlendiren doğrudan bir benchmark var mı? Yoksa K-5 altın standardı özgün katkı mı?
