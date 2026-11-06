# Proje özeti

## Purpose

Projenin kim tarafından, hangi çerçevede, hangi taahhütlerle yürütüldüğünü tek sayfada vermek.

## Scope

- In: kimlik, ekip, iki resmî çerçeve, araştırma sorusu, konumlanma
- Out: taahhüt başına durum (`wiki/project/tubitak-commitments.md`), karar bekleyen sorular
  (`wiki/project/open-decisions.md`), sıradaki işler (`wiki/project/roadmap.md`), deney protokolü
  (`evaluation/`), Core mimarisi (`giraffegraph-core/docs/`)

## Kimlik

| | |
|---|---|
| Başlık | A Human-in-the-Loop Knowledge Graph Generation Engine for Preventing Hallucination and Schema Drift in LLMs: An Application on Hadith Isnad Chains |
| Kurum | Akdeniz Üniversitesi, Mühendislik Fakültesi, Bilgisayar Mühendisliği |
| Danışman | Arş. Gör. Dr. Taha Yiğit Alkan |
| Alan uzmanları | Üç hadis uzmanı: Prof. Dr. Rifat Atay (İlahiyat) ve belirlenecek iki uzman (danışman kararı, 2026-10-16; `wiki/project/supervisor-meetings.md`) |
| Site | giraffegraph.com (`landing/`) |

## İki çerçeve

| | CSE 491 bitirme projesi | TÜBİTAK 2209-A başvurusu |
|---|---|---|
| Ekip | Yahya Efe Kuruçay, Deniz Büyükşahin, Alperen Ulukaya | Aynı ekip (proje sahibinin beyanı, 2026-10-13) |
| Kapsam ifadesi | Dini soru ve bilgilerin formal şeması → Knowledge Graph → RAG tabanlı soru-cevap; hadis isnad zinciri graf vakası | Model ile graf arasındaki kontrol katmanları tek tek eklendiğinde graf daha doğru oluyor mu, hangi katman hangi hatayı azaltıyor; saklanan insan kararının inceleme emeğini ve fark edilmeyen hatayı nasıl değiştirdiği (`wiki/thesis/tubitak/form.md`, "Araştırma sorusu") |
| Bağlayıcılık | Proje önerisi (vize ve final buna göre değerlendirilir) ve danışman toplantı formları (5 toplantı) | Başvuru danışman onayından geçti (TYBS durumu "ONAYLANDI", 2026-11-06; `wiki/thesis/tubitak/form.md`); H1…H4 ve Hedef 1–5 bağlar. Taahhüt başına eldeki kanıt: `wiki/project/tubitak-commitments.md` |
| Dönem çıktısı | Proje I çalışan bir ön prototiple biter; Proje II tamamlar | 6 ay, 4 iş paketi |
| Notlandırma / takvim | Öneri %20 (son gün 2026-10-18); 5 imzalı toplantı formu %20; vize raporu ve sunumu %20 (8. hafta); final raporu, sunum ve prototip demosu %40 (15. hafta / final dönemi). 9. haftadan itibaren tek grup reposu; commit geçmişi bireysel katkının kanıtıdır. Yapay zekâ kullanımı raporda beyan edilir | Form takvimi: `wiki/thesis/tubitak/form.md`, Bölüm 3.1 |
| Kaynak | İzlence: `/Users/efe/cse/CSE-491-Senior-Design-Project-I/resources/2026-2027-fall/CSE491_Senior_Design_Project_I_Syllabus_Fall_2026-2027.pdf` (§3–§6); toplantılar: `wiki/project/supervisor-meetings.md` | `wiki/thesis/tubitak/form.md`, özet: `wiki/project/tubitak-commitments.md` |

İki çerçeve aynı sistemi anlatır; fark vurgudadır. CSE 491 metni RAG katmanını açıkça içerir,
TÜBİTAK metni KG çıkarımına odaklanır. Değerlendirme bu yüzden iki ucu da kapsar
(`evaluation/correctness-measurement.md`, katman L1–L4).

TÜBİTAK başvurusu (1919B012619516) TYBS'de danışman onayından geçti (2026-11-06); sırada kurum yetkilisinin e-imzası (16–23 Kasım) ve TÜBİTAK değerlendirmesi var.

## Araştırma sorusu

Dar hâli (TÜBİTAK ve CSE 491; ekibin 2026-10-25 özeti): model ile graf arasındaki kontrol
katmanları (şema kontrolü, kaynak / kanıt kontrolü, insan incelemesi) tek tek eklendiğinde daha doğru
ve güvenilir bir graf elde ediliyor mu, hangi katman hangi tür hatayı azaltıyor?

Geniş hâli (yazarın asıl sorusu): ham veriden LLM destekli, halüsinasyona ve sapmaya dayanıklı,
insan tarafından doğrulanabilir bir bilgi katmanı kurmanın ve güncel tutmanın optimum yolu nedir?
Hadis ilk vaka; kod tabanı wiki'leri ve Kur'an verisi genelleme vakaları
(`wiki/sources/claude-science-context/01_meta_research_question.md`).

## Çerçeve

Proje sahibinin kararı (2026-10-13): bitirme projesi tek projedir ve tek bir iddia etrafında yürür.
Danışman onayı bekler. CSE 491 proje önerisi bu çerçeveyle yazılır (son gün 2026-10-18).

**İddia:** LLM'in ürettiği bir bilgi katmanında saklanması gereken şey insan kararıdır; kaynaktan
türetilebilen şey saklanmaz, türetilir.

| Parça | İddiaya katkısı | Nerede |
|---|---|---|
| Hadis motoru (ana kanıt) | Makine önerir, kapılar kaynağa dayanmayanı ayırır, insan karar verir, karar kaydedilir | `giraffegraph-core/`, `wiki/domains/hadith/isnad-pipeline.md`, `wiki/evaluation/engine-experiments.md` |
| Karar defteri (hadis verisinde benzetim) | Bir ravi kimliği kararı bir kez saklanır ve yeniden kullanılır; kararın kapsamı çelişkiden türetilir | `giraffegraph-core/evaluation/identity_ledger.py`, `wiki/evaluation/decision-ledger-experiments.md` |
| Kod ajanı deneyi (ikinci alan) | Ajan kararı koddan çıkaramaz; kodu anlatan belge yalnız arama kıtken işe yarar | `data/cache-and-ledger/data/agent-qa/`, `wiki/evaluation/wiki-for-agents-experiments.md` |

Sınırlar:

- İddia bu cümle kadar yazılır; "her alan için genel mimari" diye genişletilmez. Hadis dışına taşınan
  iki fikir ölçümde tutmadı (`wiki/evaluation/decision-ledger-experiments.md`, BLUF 3 ve 4).
- Üç parçanın hiçbirinde gerçek insan kararı yoktur; ilk insan verisi etiketleme kitinden gelecektir
  (`giraffegraph-core/evaluation/annotation/`).
- Tez ve makale taslakları bu çerçeveyi taşır (`wiki/thesis/README.md`, "Statü"). Proje önerisi
  taslağı da bu çerçevededir; içindeki "Open points" 8. madde danışman onayını bekler.

## Sistem, bir paragrafta

GiraffeGraph Core ham metni segmentlere böler, LLM'den şemaya uygun düğüm/ilişki adayları ister,
adayları deterministik kurallarla doğrular, düşük güvenlileri insan incelemesine yollar ve onaylananı
Neo4j'deki canonical grafa yazar. LLM grafa doğrudan yazamaz. İsnad şablonu, isnad bölütleme ve
grounding kapıları (alıntı segmentte, değer alıntıda) Core'un `main` dalındadır; davranışın tanımı
`wiki/domains/hadith/isnad-pipeline.md`. Tarih ve tabaka gibi alan kuralları (C6) ile ravi kimlik
eşleştirmesi Core'da yoktur; `wiki/sources/claude-science-results/05_kod_degisiklik_listesi.md`
değişiklikleri C1–C14 olarak sıralar, hangilerinin kodda durduğu `wiki/architecture/workspace-map.md`
içindedir. Core'un 2026-09-30 günkü hâlinin anlatımı:
`wiki/sources/claude-science-context/04a_giraffegraph_core_architecture.md`.

## Konumlanma

Öneridir; tezin ana iddiası karara bağlanmadı (`wiki/project/open-decisions.md`, soru 2).

Literatürde karşılığı olan ve özgün katkı diye sunulmayacak kalemler: hadis korpusundan bilgi grafı ve
zincir halkasının ayrı sınıf olması (SemanticHadith), ravi kimlik eşleştirmesi (Wirahman 2026,
AR-Sanad 280K), ince ayarlı modellerle isnad ayrıştırma (ilişki düzeyinde F1 0,95; Oumer 2025). Ham
çıkarım doğruluğu bu yüzden projenin iddiası olamaz (`wiki/evaluation/related-work.md`, "Projeye
çıkarımlar").

Emsallerde bulunmayan ve projenin üzerine kurulabileceği dört şey, bugünkü kanıtıyla:

| Kalem | Eldeki kanıt (300 hadis, İfta platform etiketi, 2026-10-12) | Eksik |
|---|---|---|
| Kapıların katkısının ayrı ayrı ölçülmesi | Dört koşul aynı hadislerde eşli karşılaştırıldı; kapının incelemeye yolladığı ve incelemesiz kabul ettiği çıktı ayrı puanlandı | İnsan onayı basamağı; tek model |
| Değer-alıntı kapısı (değer alıntıda, alıntı segmentte) | Motor içinde çalışır. Şema-only koşulda 1.688 mention'ın 155'ini işaretler; etiketle eşleşmeyen 145 mention'ın 122'si bunların içindedir. Eşleşmeyenlerin çoğu uydurma ravi değil, kayda geçmemiş dönüştürmedir (Latin harfine çevirme, i'râb, akrabalık ifadesinin adla değiştirilmesi) | İnsan hükmüyle doğrulama |
| Kural tabanlı ayrıştırıcı ile LLM'in karşılaştırılması | Kural tabanlı koşul şema-only LLM'i gevşek eşleşmede geçer (+0,032 [0,006 – 0,060]), katı eşleşmede geride kalır; isnad-farkındalıklı LLM ikisinin de üstündedir (F1 0,956) | Açık modeller, tekrarlar |
| İnsan üretimi, çift kodlanmış altın standart | Yok; etiketleme kiti hazır | Tamamı |

Ayrıntı ve tam tablolar: `wiki/evaluation/engine-experiments.md`. 2026-09-30 literatür denetiminin
konumlanma önerisi: `wiki/sources/claude-science-results/09_yayin_plani.md` §1.

## Rules

- MUST: ekip ya da kapsam hakkında yazarken hangi çerçeveden söz edildiği belirtilir.
- MUST: taahhüt metni için özet değil form PDF'i esas alınır.
- SHOULD: kamuya açık bir iddia (site, form, rapor) yazılmadan önce kodda karşılığı kontrol edilir
  (`wiki/sources/claude-science-context/05_claims_vs_code_gap_audit.md`).

## Verification checklist

- [ ] Ekip listesi imzalı toplantı formu ve TÜBİTAK formuyla eşleşiyor
- [ ] Başlık imzalı formdaki başlıkla aynı
- [ ] Core hakkındaki cümleler `wiki/domains/hadith/isnad-pipeline.md` ile çelişmiyor
- [ ] "Konumlanma" bölümündeki her sayı `wiki/evaluation/engine-experiments.md` içindeki satırla aynı

## Related docs

- `wiki/project/roadmap.md`
- `wiki/project/tubitak-commitments.md`
- `wiki/project/open-decisions.md`
- `wiki/architecture/workspace-map.md`
- `wiki/evaluation/correctness-measurement.md`
- `wiki/evaluation/related-work.md`
- `wiki/domains/hadith/isnad-pipeline.md`

## Last updated

2026-10-17
