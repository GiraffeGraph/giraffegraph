# 04a — TÜBİTAK formu kaynakçası: birincil kaynaktan doğrulama

**Yöntem.** `02a_TUBITAK_2209A_form_original.pdf` sayfa 11 (EK-1: KAYNAKLAR) metni PDF'ten çıkarıldı;
15 referansın her biri Crossref REST API (DOI çözümleme + künye alanları), arXiv Atom API, ACL Anthology
yazar sayfaları ve — Türkçe dergiler için — web araması ile kontrol edildi. DBLP bot korumasına
takıldığından yazar-bazlı kontrol ACL Anthology yazar sayfalarından yapıldı (bu, ACL/EMNLP/LREC
künyeleri için birincil kaynaktır). Her satırda **VAR / HATALI-KÜNYE / YOK** hükmü ve doğru künye var.

> Doğrulama tarihi: bu oturum. Doğrulanamayan hiçbir şey "doğru" sayılmadı.

## Özet skor

| Hüküm | Sayı | Referanslar |
|---|---|---|
| **VAR** (künye birebir doğru) | 7 | Pan, Ji, Lewis, Wieringa, Kejriwal, Hogan, Zhang&Soh |
| **VAR ama künye eksik/kusurlu** | 4 | Edge (yazar listesi eksik), Hevner (sayfa aralığı), TÜBİTAK Rehberi (sürüm/tarih yok), Kalkınma Planı (resmî künye yok) |
| **HATALI-KÜNYE** (çalışma gerçek, künye yanlış) | 1 | Ye vd. |
| **YOK — uydurma** | 3 | **Al-Khatib & Stein 2024**, **Bulut 2017**, **Düzenli 2019** |
| **İçerik iddiası kaynakta YOK** | 1 | Ji vd. 2023'e atfedilen "%15–%40" |

## Satır satır

### 1. Pan vd. (2024) — **VAR**
Form: *IEEE Transactions on Knowledge and Data Engineering, 36(7), 3580–3599.*
Crossref (`10.1109/TKDE.2024.3352100`): başlık, 6 yazar (Pan, Luo, Wang, Chen, Wang, Wu), cilt 36,
sayı 7, s. 3580–3599, 2024. **Birebir doğru.** DOI eklenmeli.

### 2. Edge vd. (2024) — **VAR, yazar listesi eksik**
Form 8 yazar sayıyor: Edge, Trinh, Cheng, Bradley, Chao, Mody, Truitt, Larson.
arXiv (`2404.16130`, v1 2024-04-24, v2 2025-02-19) **10 yazar** listeliyor; formda eksik olanlar:
**Dasha Metropolitansky** ve **Robert Osazuwa Ness**. Başlık ve arXiv kimliği doğru.
→ Yazar listesi tamamlanmalı veya "vd." kullanılmalı.

### 3. Ji vd. (2023) — **künye VAR, ama formun ona dayandırdığı sayı YOK**
Künye doğrulandı (`10.1145/3571730`): ACM Computing Surveys 55(12), 1–38, 2023, 10 yazar. **Doğru.**

**Ancak:** form §1.1'de şöyle diyor: *"Ji vd. (2023) hallucination üzerine yapılan kapsamlı taramada,
açık alan KG çıkarımında halüsinasyon oranlarının %15–%40 aralığında değişebildiğini raporlamaktadır."*
Surveyin tam metni (arXiv:2202.03629, 59 sayfa) tarandı:

- Metindeki **tüm** yüzde ifadeleri 7 tanedir: %62 (WikiBio infobox dışı bilgi), %25 (soyutlayıcı özetleme,
  iki ayrı yerde), %74 (QMSum tutarsız olgular), %41→%21 (InstructGPT, kapalı-alan), ve tıbbi örnek
  içindeki SpO₂ değerleri. **"%15–%40" ifadesi metinde yok.**
- Survey **KG çıkarımını bir görev olarak kapsamıyor**. "knowledge graph" 8 kez geçiyor ve hepsi
  KG-temelli diyalog (KGD) veya KG→metin üretimi bağlamında. "triple" kelimesi 4 kez geçiyor.

> **Bu, formdaki en ciddi tek bulgudur.** Projeyi motive eden merkezî sayı, atfedildiği kaynakta
> mevcut değil ve o kaynak zaten o görevi incelemiyor. Kabul sonrası raporda veya yayında bu tespit
> edilirse ciddi itibar riski. Düzeltme önerisi için bkz. §Düzeltme önerileri.

### 4. Ye vd. — **HATALI-KÜNYE**
Form: *Findings of EMNLP 2023.*
Doğrusu (`10.18653/v1/2022.emnlp-main.1`): **Proceedings of EMNLP 2022 (main conference), s. 1–17.**
Yani hem **yıl** (2023→2022) hem **track** (Findings→main) yanlış. Yazarlar (Ye, Zhang, Chen, Chen) doğru.
`02b`'deki şüphe haklı çıktı.

### 5. Lewis vd. (2020) — **VAR**
NeurIPS 2020, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks". Crossref NeurIPS
bildirilerini tutarlı indekslemediği için arXiv:2005.11401 + NeurIPS 33 künyesi kullanılmalı. Künye doğru.

### 6. Hevner vd. (2004) — **VAR, sayfa aralığı tartışmalı**
Form: *MIS Quarterly, 28(1), 75–105.* Crossref (`10.2307/25148625`): 28(1), **75–106**.
Literatürde yaygın olarak 75–105 kullanılıyor. Kritik değil; JSTOR künyesini kullanmak en güvenlisi.

### 7. Wieringa (2014) — **VAR**
Springer kitabı, `10.1007/978-3-662-43839-8`. Birebir doğru.

### 8. Bulut, H. (2017) — **YOK (uydurma olma olasılığı yüksek)**
Form: *"Hadis Râvilerinin Tespitinde Tabakat Kitaplarının Yeri." İslam Araştırmaları Dergisi, 38, 45–72.*

- Bu başlıkla hiçbir yayın bulunamadı (başlığın tam eşleşmeli aranması hiçbir sonuç vermedi).
- İslam Araştırmaları Dergisi (İSAD) **sayı 38** gerçekten 2017 Aralık'ta yayımlandı, 10 makale içeriyor;
  bu başlık listede yok.
- **En yakın gerçek çalışma:** Aslan, Muhammed. "Tabakat Kitapları ve Hadis İlmine Sağladıkları
  Faydalar." *Bingöl Üniversitesi İlahiyat Fakültesi Dergisi* 5/10 (Aralık 2017), 269–290.
  (DergiPark kayıt no 370129; isamveri.org'da PDF mevcut.) `02b`'deki tahmin doğru, yazar soyadı
  "Aslan" olarak teyit edildi.

→ **Formdaki referans silinmeli ve Aslan (2017) ile değiştirilmeli.**

### 9. Düzenli, Y. (2019) — **YOK (doğrulanamadı; uydurma olma olasılığı yüksek)**
Form: *"Hadis İsnad Sistemi ve Râvi Ağ Analizleri." Marmara Üniversitesi İlahiyat Fakültesi Dergisi, 56, 101–130.*

- MÜİFD sayı 56 gerçekten 30.06.2019'da yayımlandı; bu başlık içeriğinde bulunamadı.
- Yaşar Düzenli MÜİFD'de yayın yapan gerçek bir yazar, ancak çalışma alanı hadis isnad ağ analizi değil.
- **"Râvi ağ analizi" konusunda gerçek ve atıf yapılabilir çalışma:** Alam, T. & Schneider, J. (2021).
  *Social Network Analysis of Hadith Narrators from Sahih Bukhari.* arXiv:2102.02009. (Scale-free ağ,
  16 topluluk, etkili raviler.) Bu, formun kastettiği içeriği gerçekten sağlıyor.

→ **Formdaki referans silinmeli; Alam & Schneider (2021) veya klasik Juynboll/Motzki literatürü konmalı.**

### 10. Kejriwal (2019) — **VAR**
`10.1007/978-3-030-12375-8`, "Domain-Specific Knowledge Graph Construction", SpringerBriefs in
Computer Science. Birebir doğru.

### 11. Hogan vd. (2021) — **VAR**
`10.1145/3447772`, ACM Computing Surveys 54(4), 1–37, 18 yazar. Birebir doğru.

### 12. Al-Khatib & Stein (2024) — **YOK (uydurma)**
Form: *"Schema-Guided Information Extraction with Large Language Models." Proceedings of LREC-COLING 2024.*

Kesin delil:
- ACL Anthology yazar sayfası **Khalid Al Khatib**: 38 yayın. LREC-COLING 2024'teki tek bildirisi
  *"Reference-guided Style-Consistent Content Transfer"* (`2024.lrec-main.1201`). Başlığında "schema"
  veya "information extraction" geçen **hiçbir** yayını yok.
- ACL Anthology yazar sayfası **Benno Stein**: 95 yayın. "Information extraction" içeren iki yayını var
  (`I13-1061`, `C12-2125`), ikisi de 2012–2013 ve LLM ile ilgisiz.
- İki yazarın ortak 2024 yayını **tek**: `2024.lrec-main.1201` (yukarıdaki).
- Crossref'te bu başlıkla bir kayıt yok.

→ **Bu referans uydurmadır. Silinmeli.** İçerik olarak kastedileni karşılayan gerçek çalışmalar:
- Bai, F. vd. (2024). *Schema-Driven Information Extraction from Heterogeneous Tables.*
  Findings of EMNLP 2024. `10.18653/v1/2024.findings-emnlp.600` (arXiv:2305.14336).
- Zhang & Soh (2024) EDC — formda zaten var, şema-kısıtlı çıkarım için doğru atıf.

### 13. Zhang & Soh (2024) — **VAR**
`10.18653/v1/2024.emnlp-main.548`, EMNLP 2024 main, s. **9820–9836**. Doğru; sayfa aralığı eklenmeli.

### 14. TÜBİTAK (2024) ÜYZ Rehberi — **VAR, künye eksik**
"TÜBİTAK Destek Süreçlerinde Üretken Yapay Zekânın (ÜYZ) Sorumlu ve Güvenilir Kullanımı Rehberi"
tubitak.gov.tr üzerinde PDF olarak yayımlanmış gerçek bir dokümandır. **Sürüm numarası ve yayım
tarihi PDF'in kapağından alınıp künyeye yazılmalıdır** (birden fazla sürüm dolaşımda; bu paket
içinden sürümü kesinleştiremedim — `[UNVERIFIED: sürüm/tarih]`). Ayrıca form bu rehbere *uyum iddia
ediyor*; rehberin kendisi ÜYZ kullanımının beyan edilmesini isteyebilir — **bu paketin ve formun
LLM yardımıyla hazırlanmış kısımları beyan edilmeli mi, danışmana sorulmalı.**

### 15. On İkinci Kalkınma Planı (2024–2028) — **VAR, resmî künye kullanılmalı**
Gerçek. TBMM Genel Kurulu'nda 1 Kasım 2023'te kabul edildi; 1/11/2023 tarihli ve 32357 (2. Mükerrer)
sayılı Resmî Gazete'de yayımlandı (TBMM Kararı No. 1518). Hazırlayan kurum T.C. Cumhurbaşkanlığı
Strateji ve Bütçe Başkanlığı — formdaki atıf kurum ve yıl olarak doğru, sadece resmî künye
(RG tarih/sayı, karar no) eklenmeli.

---

## Düzeltme önerileri (somut metin)

**(a) Ji vd. cümlesi yerine.** Formdaki cümle savunulamaz. Üç seçenek, güçlüden zayıfa:

1. **Kendi pilot sayınızı koyun.** Bu paketteki pilot (`08_pilot_raporu.md`), 50 hadis / 327 ravi
   mention üzerinde ölçüyor: şema-kısıtlı promptla çalışan bir LLM'in ürettiği aday ravi
   düğümlerinin **%10,1'inde (32/318)** `properties.name` değeri, modelin kendi verdiği kanıt
   alıntısında geçmiyor; **%4,1'i** kaynak metinde hiç substring olarak bulunmuyor. Tip düzeyinde
   şema sapması ise **%0**. Bu, formun iddia ettiğinden *farklı* ve *daha kullanışlı* bir tablo:
   sorun uydurma ravi değil, **kayda geçmemiş kanonikleştirme**.
2. Genel LLM olgusallık literatürüne atıf: Min vd. (2023) FActScore, Wei vd. (2024) SAFE.
   Bunlar KG çıkarımı değil uzun-form olgusallık ölçüyor; bunu açıkça yazın.
3. Cümleyi tamamen çıkarın. Halüsinasyonun var olduğunu kanıtlamak için sayıya ihtiyaç yok.

**(b) Türkçe hadis referansları.** İki uydurma referans, ekibin hadis literatürüne gerçekten
bakmadığını gösteriyor — bir 2209-A değerlendiricisinde (özellikle alan uzmanı Prof. Atay'da)
kötü izlenim bırakır. Alan uzmanından **3–5 gerçek referans** isteyin; üstelik klasik rical/tabakat
literatürünün kendisi (Tehzîbü'l-Kemâl, Takrîbü't-Tehzîb) K-2'nin otorite listesi tartışması için
formda atıf yapılması gereken şeydir.

**(c) Eklenmesi zorunlu, formda hiç olmayan literatür (2026 itibarıyla katkı iddiasını doğrudan
etkiliyor).** Künyeler `04b`'de; ham kayıtlar (başlık, yazar listesi, tarih, **özet metni**)
`arxiv_records.json`'da.

> **Provenans uyarısı:** aşağıdaki beş çalışmanın künyesi ve özeti arXiv Atom API'sinden
> programatik olarak çekildi. **Tam metinleri okunmadı.** Bu yüzden aşağıdaki nicel ifadeler
> (185.216 varyant, 9,33/10 vb.) yazarların *özetteki kendi beyanlarıdır*; yöntem kalitesi ve
> sonuçların sağlamlığı `[UNVERIFIED]`. İP0'da okunmaları gerekiyor — özellikle Wirahman (2026),
> çünkü K-2'nin özgünlük iddiası doğrudan ona bağlı.
- **Wirahman, T. (2026).** *Linking Hadith Narrator Identities Across Heterogeneous Arabic
  Biographical Databases: A Multi-Signal Entity Resolution Pipeline.* arXiv:2607.05424.
  → **K-2'yi büyük ölçüde önceler.** Sanadset 650K'daki 185.216 tekil ravi ad varyantını iki
  biyografi veritabanına bağlıyor; sinyalleri arasında **vefat yılı yakınlığı** (= muâsara) var.
  185.216 düğümlü, 814.093 kenarlı rivayet grafını açık kaynak yayımlıyor.
- **Raja, A. Z. (2026).** *Grading the Narrators: An Isnad-Rijal Framework for Claim-Level Provenance
  in Multi-Agent Knowledge Systems.* arXiv:2607.24117. → **İsnad–rical yönteminin bilgi sistemlerine
  aktarılması** çerçevesini önceler (serve/review/quarantine yönlendirmesi dahil).
- **Haque & Islam (2026).** *Hadith computational science in the age of large language models:
  a critical narrative review.* arXiv:2608.20364. → Alanın eleştirel haritası; "ravi kimlik
  çözümlemesi" ve "uzman-temelli doğrulamanın seyrekliği" açık problem olarak listeleniyor.
- **Asgari-Bidhendi vd. (2025).** *Rezwan: ... A 1.2M Corpus Development.* arXiv:2510.03781.
  → 1,2M rivayetlik LLM-destekli korpus; **zincir–metin ayrımında 6 uzman değerlendirmesiyle 9,33/10**.
  K-5'in ölçek iddiasını bağlamına oturtuyor.
- **Mghari, Bouras & El Hibaoui (2022).** Sanadset 650K. *Data in Brief* 44, 108540.
  `10.1016/j.dib.2022.108540`. → Bu pakette **doğrulandı ve kullanıldı** (HF `freococo/650k_sanadset`,
  **CC0-1.0**).
- **Kamran, Abro & Basharat (2023).** SemanticHadith. *Journal of Web Semantics* 78, 100797.
  `10.1016/j.websem.2023.100797`. → K-1 sıfırdan ontoloji tasarlamadan önce incelenmesi gereken
  mevcut ontoloji.
