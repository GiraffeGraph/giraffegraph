# Danışman toplantıları

## Purpose

CSE 491 danışman toplantılarının kararlarını ve aksiyonlarını izlemek. Her toplantı için bir form
doldurulur, danışmana imzalatılır ve bir hafta içinde dersin MS Teams kanalına yüklenir.

## Scope

- In: toplantı tarihi, kararlar, aksiyon sahipleri, aksiyon durumu
- Out: toplantıda konuşulan teknik içeriğin ayrıntısı (ilgili wiki sayfasına bağlanır)

## Özet

| No | Tarih | Değerlendirme | Sonraki toplantı |
|---|---|---|---|
| 1 | 2026-10-02 | Very good | 2026-10-09 |
| 2 | 2026-10-16 | Formda işaretlenmedi (imzasız) | 2026-10-23 |
| 3 | 2026-10-30 | Formda işaretlenmedi (imzasız) | 2026-11-06 (planlanan haftalık görüşme) |

2026-10-09'da danışmanla benzer projelerden nerede ayrışılacağı konuşuldu (proje sahibinin beyanı); bunun formu yok. Toplantı 2'nin hazırlık belgeleri ve ekibin doldurduğu form: `wiki/thesis/meeting/2026-10-16/` (gündem: `04-gundem.md`, form: `build/supervisor-meeting-form.docx`).

Ders toplam 5 toplantı formu öngörür; her imzalı form notun %4'üdür ve toplantıdan sonra bir hafta
içinde Teams'e yüklenir. Teams son günleri: toplantı 2 için 2026-10-16, toplantı 3 için 2026-10-30,
toplantı 4 için 2026-11-13, toplantı 5 için 2026-11-27. Toplantıya katılmamak üyenin bireysel notuna
yansır (izlence §2).

| Toplantı | Hedef hafta | İzlencedeki beklenen odak |
|---|---|---|
| 2 | 4–5 | Benzer sistemler ve literatür; işlevsel ve işlevsel olmayan gereksinimler; öneri taslağı |
| 3 | 6–7 | Mimari, veri modeli, arayüz yaklaşımı, teknoloji seçimi; vize sunumu öncesi gözden geçirme |
| 4 | 9–10 | Çekirdek bileşenlerde ilerleme; repo ve geliştirme ortamı; riskler ve yeniden planlama |
| 5 | 12–13 | Bütünleştirme ve prototip durumu; test sonuçları; final raporu ve sunum planı |

## Toplantı 1 — 2026-10-02

Katılım: tüm grup üyeleri. Danışman: Dr. Taha Yiğit Alkan.

**Web kopyası (9 Kasım 2026):** kullanıcının sağladığı iki taranmış PDF birebir aynıdır
(SHA-256 `349b3b0d52975d6bfd182c5ba191dd13059f3f5ab71828053a3efd31aadb8ded`).
İmzalı asıllar İndirilenler ve ders klasöründe korunur; public repoya kopyalanmaz.
`wiki/thesis/meeting/2026-10-02/supervisor-meeting-1-public.pdf` yalnız imzası kaldırılmış
kopyadır. İmza değerlendirme satırının üzerine taştığı için web kopyasında bu hücreler temizlenmiş,
kaynakta işaretli “Very good” değerlendirmesi açık metinle korunmuştur. Öğrenci numaraları yer alır.

**Tanımlanan problem:** dini soru ve ilgili bilgilerin formal temsili, bu temsilden Knowledge Graph
kurulması ve RAG tabanlı soru-cevap sistemiyle bütünleştirilmesi. Hadis isnad zincirleri graf
tabanlı kullanım senaryosu.

**Tartışılan riskler:** dini bilgi için uygun şemanın tanımlanması; hadis kaynağı, ravi ve isnad
zincirinin graf olarak modellenmesi; veri setleri, mevcut KG yaklaşımları ve sistemin
değerlendirme yöntemlerinin araştırılması.

**Kararlar:** üç bileşen incelenir: şema tasarımı, KG inşası, RAG entegrasyonu. Her üyeye konu
başına en az 20 makalelik literatür taraması verildi. Teslim: sonraki toplantı.

| Sahip | Konu | Durum (2026-10-16) |
|---|---|---|
| Alperen Ulukaya | Graf yapıları ve teknikler | 27 makalelik liste; PDF'leri ortak Zotero grubunda; projeye karşı okuma notları `wiki/literature/team-reading-list-notes.md` |
| Deniz Büyükşahin | Din bağlamında LLM uygulamaları | Bu çalışma alanında kayıt yok; toplantı formunda boş bırakıldı |
| Yahya Efe Kuruçay | LLM başarı ölçüm metrikleri | 38 makale toplandı, review'lar üretildi; makaleler okunmadı (`wiki/evaluation/literature-map.md`) |

**Review formatı:** makale başına en çok 300 kelimelik akademik değerlendirme; beş başlık: Research
Gap, Data and Methodology, Main Contributions, Relevance to the Field, Future Work / Limitations.

**Sonraki toplantıya kadar plan:** atanan literatürü incelemek, kısa akademik özetler hazırlamak,
bulgularla proje kapsamını daraltmak, uygun graf / şema yaklaşımını ve isnad zincirini RAG ile
bütünleştirme yöntemlerini belirlemek.

## Toplantı 2 — 2026-10-16

Süre 15 dakika. Katılım: tüm grup üyeleri ve danışman. Form ekip tarafından dolduruldu; imza ve
değerlendirme kutusu boş (`wiki/thesis/meeting/2026-10-16/build/supervisor-meeting-form.docx`).

**Güncel kaynak ve web kopyası (9 Kasım 2026):** kullanıcının verdiği
`CSE491_Supervisor_Meeting_Form.docx` ile `(1)` adlı dosya birebir aynıdır
(SHA-256 `0319fbb3a349765b8f0f325c0b95188aa2c18b40e0fcd7553e23f32e4a5664f6`).
Asıl Word değiştirilmeden `wiki/thesis/meeting/2026-10-16/supervisor-meeting-2-original.docx`
yoluna arşivlendi. Aynı dosya doğrudan tek sayfalık A4 PDF'e çevrildi; bozuk web çıktısının yerini
`wiki/thesis/meeting/2026-10-16/supervisor-meeting-2.pdf` ve sitedeki Meeting #2 bağlantısı aldı.
Öğrenci numaraları korunur; değerlendirme ve imza alanları kaynakta olduğu gibi boştur.

**Konuşulan:** benzer çalışmalarla örtüşmeler ve olası araştırma boşlukları; araştırma katkısının daha
da netleşmesi gerektiği; etiketleme kılavuzu ve belirsiz durumlar için uzman desteği. Toplantıda
etkileşimli anlatıcı (`wiki/thesis/guide/anlatici.html`) gösterildi (proje sahibinin beyanı).

**Kararlar (form):** araştırma sorusu incelenen çalışmalara göre daraltılır; danışman en az iki hadis
uzmanıyla çalışmayı önerdi; ekip olası uzmanları belirler ve TÜBİTAK 2209-A başvurusunun ilk
taslağını hazırlar. Sahip: tüm grup. Son gün: sonraki toplantı.

**Proje sahibinin aktardığı ek istekler:** TÜBİTAK taslağı kısa ve anlaşılır olacak, danışman okuyacak;
bir yerine üç hadis uzmanı, çünkü uzmanlar kendi aralarında ayrışabilir. Üç uzmanın etiketlemedeki
rolü proje önerisinde (§6) ve TÜBİTAK formunda (2.3) yazılıdır.

| Sahip | Aksiyon | Durum (2026-10-17) |
|---|---|---|
| Tüm grup | Benzer çalışmaların karşılaştırma tablosu, benzerlik ve farklar | Öneri §4 ve `wiki/thesis/meeting/2026-10-16/02-benzer-calismalar.md` |
| Tüm grup | Danışılacak hadis uzmanlarını belirlemek, uzman incelemesi soruları | Prof. Dr. Rifat Atay belli; iki uzman aranıyor; sorular `giraffegraph-core/evaluation/annotation/expert/brief.md` |
| Tüm grup | TÜBİTAK 2209-A ilk taslağı (kısa) | `wiki/thesis/tubitak/form.md` kısaltıldı; danışmanın okumasını bekliyor |

## Toplantı 3 — 2026-10-30

Süre 10 dakika. Formda tüm grup üyelerinin ve danışmanın katıldığı yazılıdır. Kullanıcının
9 Kasım 2026 tarihinde sağladığı PDF, `wiki/thesis/meeting/2026-10-30/supervisor-meeting-3.pdf`
yolunda değiştirilmeden saklanır. Danışman değerlendirmesi ve imza alanı boştur.

**Tamamlanan işler (form):** CSE 491 önerisi tamamlandı; TÜBİTAK başvurusunun ilk taslağı ve
araştırma katkısını benzer çalışmalardan ayıran açıklama hazırlandı. 23 ve 30 Ekim haftalık
görüşmelerinde kapsam, yöntem ve ilerleme değerlendirildi.

**Açık işler (form):** hadis uzmanlarıyla iş birliği henüz kesinleşmedi; uzman incelemesi,
etiketleme kılavuzu, benzer çalışmalar karşılaştırması ve TÜBİTAK taslağı gözden geçirilecek.
Tüm grup, uzmanlarla iletişim kuracak ve sonraki teknik geliştirme adımlarını belirleyecek.
Aksiyon hedefi Toplantı 4 öncesi, 13 Kasım 2026; formun sonraki haftalık görüşme tarihi alanı
6 Kasım 2026'dır. Bu iki tarih formda ayrı amaçlarla verilmiştir.

**Web yayını:** aynı PDF, sitedeki Meeting #3 kartından ve `/meeting-3/` sayfasından açılır.
Öğrenci numaraları korunur; yayımlanan dosyada imza bulunmaz.

## Rules

- MUST: her toplantı kendi başlığı altında, mevcut formdaki bilgiyle yazılır; imza durumu açıkça belirtilir.
- MUST: aksiyon durumu tarihle birlikte güncellenir.
- SHOULD: imzalı form PDF'i çalışma alanında saklanır; indirme klasörü kalıcı bir yer değildir.

## Source anchors

Ders belgeleri çalışma alanının dışında, ders reposunda durur (`/Users/efe/cse/CSE-491-Senior-Design-Project-I/`).

- İmzalı form, toplantı 1: `assignments/2026-2027-fall-efe-kurucay/giraffegraph/supervisor-meeting-1-2026-10-02.pdf`
- Boş form şablonu: `resources/2026-2027-fall/CSE491_Supervisor_Meeting_Form.docx`
- İzlence (toplantı kuralları §2, haftalık plan §5): `resources/2026-2027-fall/CSE491_Senior_Design_Project_I_Syllabus_Fall_2026-2027.pdf`
- Teams son günleri: ders reposu `README.md`, "Grading"
- Toplantı 3 formu (imzasız): `wiki/thesis/meeting/2026-10-30/supervisor-meeting-3.pdf`

## Verification checklist

- [ ] Özet tablosundaki her satır bir mevcut forma dayanır ve imza durumu belirtilir
- [ ] Her aksiyonun sahibi ve durumu var
- [ ] Sonraki toplantı tarihi son formla aynı

## Related docs

- `wiki/project/overview.md`
- `wiki/evaluation/literature-map.md`

## Last updated

2026-11-09
