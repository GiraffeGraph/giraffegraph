# 01 — Asıl araştırma sorusu

## Soru

Ham veri (yapılandırılmamış veya yarı yapılandırılmış) + LLM + sınırlı insan uzman zamanı verildiğinde:

> **Hangi bilgi katmanı mimarisi**, (a) halüsinasyonu kaynağa girmeden durdurur, (b) şema/terim sapmasını (drift) önler, (c) kaynak değiştikçe güncel kalır, (d) insan emeğini en aza indirir, (e) ajanların (LLM'lerin) ve insanların sorularını doğru cevaplamasını sağlar ve (f) alanlar arasında (kod, hadis, Kur'an, hukuk, sağlık...) aktarılabilir?

Yazarın sözleri: *"Asıl plan wiki oluşturmayı çok iyi optimize etmek. Knowledge graph kullanmak zorunlu değil. Bu işi md'lerle yapmak da zorunlu değil. Hiçbir şey zorunlu değil. Optimum yolu bulmaya çalışıyorum. Bunu bulursak kodlamada, codebase'lerde, Kur'an projemizde veya raw data olan her yerde bu işi yapabiliriz."*

## Somut vakalar (aynı sorunun örnekleri)

| Vaka | Ham veri | Doğruluk kaynağı (source of truth) | Türetme maliyeti | Tipik sorgu |
|---|---|---|---|---|
| **A. Hadis isnad** (TÜBİTAK, zorunlu teslim) | Hadis metinleri (Arapça/Türkçe meal), rical kitapları | Metin + klasik rical literatürü + uzman hükmü | Yüksek: NL→yapı, deterministik değil, pahalı | "X kimden rivayet etti?", "Bu zincir muttasıl mı?", "Aynı ravi mi?" |
| **B. Kod tabanı wiki** (yazarın günlük işi) | Kaynak kod, git geçmişi, ticket'lar | Kodun kendisi (niyet/kararlar hariç) | Düşük: grep/read ucuz ve deterministik | "Bu modül nasıl genişletilir?", "Neden böyle yapıldı?" |
| **C. Kur'an uygulaması** (ikinci plan) | Meal metinleri, tefsir, embedding'ler, üçüncü parti API'ler | Doğrulanmış edisyon + provenance | Orta | "Bu meal hangi mütercimin?", semantik arama |

## "Optimum"un tanımı (değerlendirme ekseni önerisi, Claude Science tarafından sorgulanmalı)

1. **Doğruluk:** Katmanda yaşayan yanlış olgu oranı (kalıcı halüsinasyon). Asıl hedef ~0.
2. **Kapsam:** Kaynakta olup katmana girmeyen olgu oranı (recall).
3. **Tutarlılık:** Şema dışı tip, tekrar eden varlık (duplicate) ve çelişkili olgu oranı.
4. **Güncellik:** Kaynak değişince katmanın ne kadar hızlı ve ne kadar ucuza doğru hale geldiği. İnvalidation cascade var mı?
5. **İnsan maliyeti:** Doğrulanmış olgu başına uzman dakikası. Hangi kararlar insana düşmeli, hangileri deterministik kurala?
6. **Makine maliyeti:** Token ve hesaplama. İlk kurulum ve artımlı güncelleme ayrı ölçülmeli.
7. **Tüketim kalitesi:** Katman üzerinden cevaplanan soruların doğruluğu. Çıplak kaynak + ajanın grep/RAG'ına karşı ölçülmeli.
8. **İzlenebilirlik:** Her olgu için "hangi cümleden, hangi model/prompt sürümüyle, kim onayladı" cevaplanabiliyor mu?
9. **Aktarılabilirlik:** Yeni bir alana geçerken değişmesi gereken şeyin boyutu (şema + kurallar + promptlar).

## Kısıtlar

- **TÜBİTAK 2209-A formundaki taahhütler bağlayıcı** (`02b`). Hadis vakası, 5 BDM × 2 koşul deneyi, altın standart, H1–H4 hipotezleri teslim edilmeli. Genel "optimum" araştırması bu taahhütleri **kapsamalı veya genişletmeli**, onlarla çelişmemeli.
- **Süre:** 6 ay (form), 2–3 kişilik lisans ekibi, sınırlı bütçe (açık modeller öncelikli).
- **giraffegraph.com kamuya söz verdi** (`03`): "Nothing enters the graph unapproved", "No hallucinated facts", "reversible". Mevcut kod bunların bir kısmını karşılamıyor (`05`). Ya kod düzeltilmeli ya iddialar.
- Yazarın önceki bulgusu (`06a`): **türetilebilir olan saklanmamalı, sadece kararlar saklanmalı.** Bu, GiraffeGraph'ın "LLM çıkarımlarını canonical graph'a yaz" yaklaşımıyla gerilim yaratıyor. Bu gerilimin çözümü muhtemelen araştırmanın kalbi (`12`).

## Claude Science'tan beklenen çıktılar

1. **Tasarım uzayı analizi:** Temsil (KG / tipli markdown wiki / olay günlüğü + türetilmiş görünüm / sadece-RAG / hibrit) × doğrulama (deterministik kural / kaynak-span grounding / NLI / LLM-judge / insan) × güncelleme stratejisi (full rebuild / memoize / artımlı delta). Her hücre için kanıt ve maliyet.
2. **Optimum mimari önerisi** ve bunun **alan-bağımsız çekirdeği** ile **alan-özgü eklentileri**.
3. **Hadis vakası için uygulanabilir deney tasarımı.** TÜBİTAK hipotezleri korunacak; ablation, istatistik gücü ve altın standart protokolü revize edilecek.
4. **Mevcut koda somut değişiklik listesi** (öncelikli; `05`teki boşluklar).
5. **Genelleme deneyi:** Aynı mimarinin bir kod tabanında (B) ve Kur'an verisinde (C) nasıl sınanacağı.
6. **Referans doğrulaması:** Formdaki kaynakçanın doğrulanması (`02b` §Referanslar).
7. **Yayın planı:** Hangi katkı hangi venue'ya uygun (lisans öğrencisi gerçekçiliğiyle).
