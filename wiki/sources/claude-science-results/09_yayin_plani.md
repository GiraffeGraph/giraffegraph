# 09 — Yayın planı: hangi katkı özgün, nereye gönderilir

## 1. Katkıların özgünlük denetimi (sert)

Doğrulanmış literatür karşısında, formdaki ve `12`'deki katkı iddialarının durumu:

| Katkı | Özgünlük | Gerekçe / çakışan çalışma |
|---|---|---|
| **K-1 Hadith Schema / ontoloji** | **ÖZGÜN DEĞİL** | SemanticHadith (Kamran, Abro & Basharat 2023, *J. Web Semantics* 78:100797) Kütüb-i Sitte için RDF ontoloji ve KG yayımlamış. "≥8 varlık, ≥10 ilişki" bir mühendislik çıktısı, bilimsel katkı değil. **Özgün olabilecek kısım:** aktarım olayının reifikasyonu (`Transmission {hadith_id, position, sigha}`) — SemanticHadith'te bunun olup olmadığı kontrol edilmeli |
| **K-2 Transliterasyon-aware ER** | **BÜYÜK ÖLÇÜDE ÖNCELİKLENMİŞ** | Wirahman (2026, arXiv:2607.05424) Sanadset'teki 185.216 tekil ravi varyantını iki biyografi veritabanına çok-sinyalli ER ile bağlıyor; sinyaller ad benzerliği + **vefat yılı yakınlığı (muâsara)** + güvenilirlik polaritesi; 185.216 düğüm/814.093 kenarlı grafı ve eşleme korpusunu açık yayımlıyor. **Özgün kalan:** (i) Türkçe transliterasyon düzlemi, (ii) ER kararlarının insan onayı + karar defterine bağlanması (Wirahman tamamen otomatik) |
| **K-3 İsnad tutarlılık kuralları** | **KISMEN ÖZGÜN** | Muâsara/likâ/tabaka kuralları klasik hadis usûlünün makine karşılığı; Wirahman vefat yılını sinyal olarak kullanıyor ama **kural motoru + HITL yönlendirmesi** olarak formalize etmiyor. Kuralın sonucunun **karar talebi** olması (RED değil) özgün |
| **E-4 Hadis-özgü prompt şablonları** | ÖZGÜN DEĞİL (mühendislik) | Ama **ölçülmüş etkisi en büyük**: ΔP = +0,125 [+0,084, +0,170]. Bir yayında "katkı" değil **bulgu** olarak sunulmalı |
| **K-4 Karşılaştırmalı deney (ablation)** | **ÖZGÜN** | Hadis isnad çıkarımında şema kapısı / grounding kapısı / ER / HITL basamaklarının ayrı ayrı katkısını ölçen bir çalışma bulamadım. Haque & Islam (2026) "benchmark karşılaştırılabilirliğinin zayıflığı" ve "uzman-temelli doğrulamanın seyrekliği"ni alanın açık problemi olarak listeliyor — bu boşluk gerçek |
| **K-5 Altın standart veri seti** | **KISMEN ÖZGÜN** | Asgari-Bidhendi vd. (2025, arXiv:2510.03781) 1,2M rivayetlik LLM-destekli korpus yayımlamış ve zincir–metin ayrımında 6 uzmanla **9,33/10** almış. Wirahman eşleme korpusunu yayımlamış. **Özgün kalan:** (i) *insan tarafından üretilmiş*, çift-kodlayıcılı, κ raporlanmış bir altın standart (yukarıdakilerin ikisi de otomatik + örneklem denetimli), (ii) Türkçe otorite eşlemesi |
| **Değer-grounding kapısı** (`property_value ⊂ quote`) | **ÖZGÜN ve en kolay savunulur** | Literatürde grounding tartışması cümle/iddia düzeyinde (FActScore, SAFE, AIS). Üçlü çıkarımında **alıntı doğru ama property değeri alıntıda yok** durumunun ayrı bir hata sınıfı olduğunu ve ucuz bir deterministik kapıyla %10,1 oranında yakalandığını gösteren bir çalışma bulamadım |
| **Sınıf 2b: "model kararı"** (`02` Saldırı 3) | **ÖZGÜN** | `06a`'nın cache/decision ikiliğine üçüncü bir sınıf ekliyor: modelin kendi aldığı, kayda geçmemiş kanonikleştirme kararı. Ölçülmüş (%8,5) ve mimari sonucu var |
| **Kaynak + karar defteri + türetilmiş görünüm** (`12`) | **KISMEN ÖNCELİKLENMİŞ** | Datomic/Git/RFC/ADR/çift-kayıt soyağacı `06a`'da zaten tespit edilmiş (ve bu bir güç, uydurma bir yenilik iddiası değil). Raja (2026, arXiv:2607.24117) isnad–rical yöntemini çok-ajanlı bilgi sistemlerine aktarıyor ve serve/review/quarantine yönlendirmesi öneriyor — **çerçeve olarak yakın**. **Özgün kalan:** içerik-adresli karar hedefleri sayesinde **insan emeğinin modelden bağımsız birikmesi** (T3) — ve bu **henüz ölçülmedi** |
| **Deterministik parser ≈ LLM bulgusu** | **ÖZGÜN ve yayınlanabilir** | "Bu görevde LLM'e gerek yok" tipi negatif bulgular az yayımlanır ama değerlidir. Pilot: ΔF1 = −0,017 [−0,072, +0,039], recall'de deterministik önde |

**Özet:** formun "bilimsel katkı" olarak saydıklarının çoğu (K-1, K-2, E-4) 2026 itibarıyla
mühendislik veya önceliklenmiş. **Gerçekten yayınlanabilir dört şey var:** ablation merdiveni (K-4),
insan-üretimli altın standart (K-5'in insan kısmı), değer-grounding kapısı, ve "deterministik
parser LLM'i geçiyor" bulgusu. Tezin ve makalenin ekseni bunlar olmalı — K-1/K-2 **altyapı** olarak
sunulmalı, katkı olarak değil.

> Bu, formu yanlış yapmıyor: form 2026 I. dönem için yazıldı, yukarıdaki üç preprint 2026
> ortasında çıktı. Ama **yayın anında** bu literatür var olacak ve bir hakem bulacak.

## 2. Venue önerileri (lisans ekibi gerçekçiliğiyle)

| Hedef | Ne gönderilir | Risk | Zamanlama |
|---|---|---|---|
| **arXiv preprint** | Tam çalışma (ablation + altın standart + kapı bulguları) | Yok | F4 biter bitmez. **Hemen yapın** — öncelik iddiası için tek mekanizma |
| **UBMK veya INISTA** (formda taahhüt) | Tam çalışmanın Türkçe/İngilizce bildiri hâli | **Düşük.** Lisans ekibi için uygun, kabul oranları yüksek, Türkçe sunum mümkün | F4, ay 6 |
| ***Data in Brief*** veya benzeri data paper | Altın standart veri seti (yalnız üçlü düzeyinde) + etiketleme kılavuzu + κ | **Düşük.** Sanadset'in kendisi burada yayımlandı; format tam olarak bu | F3 biter bitmez, F4'e paralel |
| **LREC / LREC-COLING** (kaynak bildirisi) | Altın standart + eşleşme kriteri tartışması | **Orta.** Kaynak bildirileri lisans ekibinden kabul edilebilir; konferans döngüsü 2 yıl | Bir sonraki döngü |
| **ACL/EMNLP workshop** — Arapça NLP (WANLP), dijital beşeri bilimler (LaTeCH-CLfL), KG workshop'ları | Değer-grounding kapısı + deterministik-vs-LLM bulgusu (odaklı, kısa) | **Orta.** Workshop'lar bu tür odaklı negatif/mekanizma bulgularına açık | F4 sonrası |
| Dergi (*Journal of Web Semantics*, *Digital Scholarship in the Humanities*) | Tam mimari + üç vaka | **Yüksek.** 6 ayda gerçekçi değil; hakem döngüsü 6–12 ay | Tez sonrası |

**Formdaki "EMNLP Workshop" taahhüdü:** gerçekçi ama bir uyarı — EMNLP workshop'ları İngilizce ve
rekabetli. **Odaklı bir bildiri** (tek bulgu, sağlam ölçüm) tam çalışmayı sıkıştırmaktan daha yüksek
kabul şansı verir. "Property-level grounding: the gate that quote-level grounding misses" gibi tek
mesajlı bir bildiri, "our HITL KG engine for hadith" gibi geniş bir bildiriden daha iyi geçer.

## 3. Makale iskeleti (ana bildiri)

**Başlık önerisi** (sitedeki başlık çok geniş ve iddiayı zayıflatıyor):
*"Where should the gate sit? Measuring schema, grounding, entity-resolution and human gates in
LLM-based knowledge graph construction, with a hadith isnad case study"*

```
1  Giriş
   - Problem: LLM'ler bilgi katmanına yanlış olgu sokuyor. İki failure mode: halüsinasyon, drift.
   - AMA: bu iki kelime çok kaba. Bildirinin tezi: kapının NEREDE durduğu, kaç kapı olduğundan önemli.
   - Katkılar: (i) 7 basamaklı ablation merdiveni, (ii) değer-grounding kapısı ve ölçümü,
     (iii) insan-üretimli hadis altın standardı, (iv) deterministik parser baz çizgisi.

2  İlgili çalışmalar
   2.1 LLM ile KG inşası: şema-önce (Zhang & Soh 2024 EDC), açık-sonra-kanonikleştir,
       Ye vd. 2022 (EMNLP main — künye düzeltilmiş), Pan vd. 2024.
   2.2 Grounding ve attribution: Min vd. 2023 FActScore, Wei vd. 2024 SAFE, Rashkin vd. 2023 AIS,
       Laban vd. 2022 SummaC, Zha vd. 2023 AlignScore. → hepsi cümle/iddia düzeyinde; üçlü
       property düzeyinde boşluk var.
   2.3 Güven ve seçici tahmin: Kadavath vd. 2022, Xiong vd. 2024, Angelopoulos & Bates 2021.
   2.4 Entity resolution: Fellegi & Sunter 1969, Li vd. 2020 Ditto, Splink; metrikler
       B-cubed (Bagga & Baldwin 1998), CEAF (Luo 2005).
   2.5 Hadis hesaplamalı bilimi: Haque & Islam 2026 (review), Wirahman 2026 (ER),
       Raja 2026 (isnad-provenance), Asgari-Bidhendi vd. 2025 (Rezwan), Kamran vd. 2023
       (SemanticHadith), Mghari vd. 2022 (Sanadset), Alam & Schneider 2021 (SNA).
       → BURADA DÜRÜST OL: K-2 önceliklenmiş, bizim farkımız X.

3  Mimari
   3.1 Alan-bağımsız çekirdek: S (içerik-adresli kaynak), P (sürümlü prosedür),
       değişmez çıkarım kayıtları, dört katmanlı kapı, append-only karar defteri.
   3.2 Dört kapı: G1 yapı, G2 alıntı-grounding, G3 DEĞER-grounding, G4 alan kuralı.
   3.3 Alan eklentileri: Segmenter, DomainRule, TransformRule.
   3.4 İsnad modellemesi: aktarım olayının reifikasyonu; neden kenar anahtarı yetmez.

4  Deney tasarımı
   4.1 Veri: Sanadset 650K (CC0); tabakalı örnekleme; T-obscure sızıntı alt kümesi.
   4.2 Altın standart: iki katman, kör protokol, karşılıklı F1 + κ.
   4.3 Ablation merdiveni Cx, C0–C5, Cseg.
   4.4 Metrikler ve EŞLEŞME KRİTERLERİ (M1/M2/M3) — bu alt bölüm literatürde
       genellikle atlanıyor; burada öne çıkarılmalı.
   4.5 İstatistik: karışık etkili modeller, cluster bootstrap, Holm; güç simülasyonu.

5  Sonuçlar
   5.1 Merdiven: her basamağın marjinal katkısı.
   5.2 Tip düzeyinde drift ≈ 0; property düzeyinde drift X → H2'nin yeri.
   5.3 Alıntı-grounding 0 yakalıyor, değer-grounding %X yakalıyor.
   5.4 Güven skorunun AUC'si; yönlendirme politikası karşılaştırması.
   5.5 ER: B0→B3 merdiveni, over-merge oranı birincil.
   5.6 İnsan maliyeti: doğrulanmış üçlü başına uzman saniyesi.
   5.7 Deterministik parser baz çizgisi: LLM ne kadar ekliyor?
   5.8 Sızıntı testleri.

6  Tartışma
   - Kapı nerede durmalı: ölçülmüş getiri/maliyet sıralaması.
   - Sınıf 2b: modelin kendi kanonikleştirme kararı — üçüncü bir olgu sınıfı.
   - Aktarılabilirlik: kod ve Kur'an vakaları.

7  Geçerlilik tehditleri
   - Tek uzman; gümüş vs altın standart; Arapça↔Türkçe; model seçimi karıştırıcısı
     (JSON-mode desteği); eşleşme kriterinin sonucu ±0,25 oynatması; sızıntı.

8  Sonuç
```

**Uzunluk stratejisi:** 4 ve 5 bölüm bir **workshop bildirisine** (8 sayfa) sığmaz. İki parçaya
bölün: (A) workshop bildirisi = §3.2 + §5.2–5.4 + §5.7 (kapılar ve ölçümleri), (B) UBMK/INISTA
bildirisi = tam çalışma, Türkçe. arXiv preprint tam hâli taşır.

## 4. Açık bilim kontrol listesi (formdaki taahhütler)

- [ ] Kod: GitHub, **LICENSE ile** (şu an yok — C11)
- [ ] Altın standart: Zenodo/HF, **yalnız üçlü düzeyinde** (telif riski, form R2)
- [ ] Etiketleme kılavuzu (sürümlü) yayımlanır
- [ ] Karar defteri şeması + `rebuild.py` yayımlanır (tekrarlanabilirlik)
- [ ] Prompt'ların **tam metni** ve sürümleri yayımlanır (C1 ve C1d pilotta olduğu gibi)
- [ ] arXiv preprint
- [ ] `04b_dogrulanmis_kaynakca.bib` kullanılır; hiçbir künye elle yazılmaz
- [ ] ÜYZ kullanımı TÜBİTAK rehberine göre beyan edilir (bu paket dahil — danışmana sorun)
