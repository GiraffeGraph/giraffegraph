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

## Rules

- MUST: her toplantı kendi başlığı altında, imzalı formdaki bilgiyle yazılır.
- MUST: aksiyon durumu tarihle birlikte güncellenir.
- SHOULD: imzalı form PDF'i çalışma alanında saklanır; indirme klasörü kalıcı bir yer değildir.

## Source anchors

Ders belgeleri çalışma alanının dışında, ders reposunda durur (`/Users/efe/cse/CSE-491-Senior-Design-Project-I/`).

- İmzalı form, toplantı 1: `assignments/2026-2027-fall-efe-kurucay/giraffegraph/supervisor-meeting-1-2026-10-02.pdf`
- Boş form şablonu: `resources/2026-2027-fall/CSE491_Supervisor_Meeting_Form.docx`
- İzlence (toplantı kuralları §2, haftalık plan §5): `resources/2026-2027-fall/CSE491_Senior_Design_Project_I_Syllabus_Fall_2026-2027.pdf`
- Teams son günleri: ders reposu `README.md`, "Grading"

## Verification checklist

- [ ] Özet tablosundaki satır sayısı imzalı form sayısına eşit
- [ ] Her aksiyonun sahibi ve durumu var
- [ ] Sonraki toplantı tarihi son formla aynı

## Related docs

- `wiki/project/overview.md`
- `wiki/evaluation/literature-map.md`

## Last updated

2026-10-17
