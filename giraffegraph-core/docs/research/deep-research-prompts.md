# Deep Research Prompts

Bu belge, guncel teknik konularda kullanilmak uzere reusable prompt'lari toplar.

## Kullanim Kurali

Asagidaki durumlarda yeni bir arastirma prompt'u acilmali:

- Neo4j veya GraphRAG tarafinda surume duyarli karar alinacaksa
- Production ve experimental ayrimi net degilse
- Performans, maliyet veya deployment karari guncel veriye bagliysa
- Resmi dokuman kontrolu olmadan riskli mimari karari alinacaksa

## Neo4j + GraphRAG Deep Research Prompt

```text
Biz generic, schema-driven, AI-assisted bir graph construction platformu tasarliyoruz.
Ilk domain template'imiz dizi/film/senaryo verisi olacak, ama cekirdek sistem domain-agnostic olacak.

Lutfen asagidaki konularda 2025-2026 itibariyla guncel, teknik, derin ve uygulanabilir bir arastirma yap.
Oncelik resmi Neo4j dokumantasyonu, resmi driver belgeleri, resmi GraphRAG package belgeleri, Neo4j blog/developer guides, GDS belgeleri, ardindan guvenilir teknik kaynaklar olsun.

Arastirma hedefi:
- Urunun generic graph production engine mimarisini en saglam sekilde kurmak
- Neo4j + Python + schema-driven extraction + validation + graph commit hattini dogru modellemek
- GraphRAG, vector search, graph traversal ve knowledge graph builder tarafinda guncel en iyi pratikleri ogrenmek
- Deneysel ozelliklerle production-grade ozellikleri ayirmak
- Baslangic MVP ile uzun vadeli platform mimarisi arasinda net kararlar cikarmak

Lutfen su basliklarda arastir:

1) Neo4j'nin guncel yetenekleri
2) Neo4j GraphRAG for Python guncel durumu
3) Knowledge graph construction best practices
4) Schema-as-data / ontology management
5) Clean Architecture ve DDD acisindan oneriler
6) Ingestion + extraction orchestration
7) Testing ve reliability
8) Ilk 90 gun icin teknik roadmap onerisi

Her baslik icin:
- net oneriler ver
- tradeoff'lari belirt
- production icin uygun olanlarla arastirma/prototip seviyesinde olanlari ayir
- mumkunse karar matrisi olustur
- resmi kaynaklari ve tarihlerini belirt
- ozellikle son degisiklikleri vurgula

Ayrica su sorulara ozellikle cevap ver:

- GraphRAG paketi cekirdek urunde zorunlu dependency mi olmali, yoksa opsiyonel adapter mi?
- Neo4j canonical store, Postgres metadata/config store ayrimi dogru mu?
- Generic engine + domain templates yaklasimi teknik olarak surdurulebilir mi?
- Story template icin minimum node/relation seti ne olmali?
- Candidate -> validation -> commit hatti icin en guvenli veri modeli ne?
- Schema drift ve schema evolution nasil ele alinmali?
- Ilk production-grade surumde hangi ozellikleri kesinlikle disarida birakmaliyiz?
- Neo4j uzerinde graph write tarafinda en guvenli merge/upsert stratejileri neler?
- Vector search + graph traversal hibrit retrieval ileride nasil tasarlanmali?

Son ciktiyi su formatta ver:
1. Executive summary
2. Mimari oneri
3. Tavsiye edilen teknoloji ve paketler
4. Production-safe kararlar
5. Experimental / dikkatli kullanilacak parcalar
6. MVP roadmap
7. Acik riskler ve karar bekleyen konular
8. Kaynakca
```

## Cevap Geri Geldiginde

Arastirma sonucu gelince su uc is yapilir:

1. `docs/architecture/` altindaki ilgili belge guncellenir.
2. Gerekirse yeni ADR acilir veya mevcut ADR revize edilir.
3. Kod kontratlari ve backlog etkisi not edilir.
