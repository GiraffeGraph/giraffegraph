# 07 — `13`'teki 16 açık soruya öneri ve gerekçe

Her satırda **öneri**, **gerekçe** ve **kanıt tipi** var. Nihai karar ekibe ve danışmana ait.

---

## Kapsam ve konumlandırma

**1. TÜBİTAK başvurusunun durumu nedir?**
**Öneri:** Bu paket bunu bilmiyor ve ben de öğrenemem. Ama karar ağacı şu:
- **Kabul edildiyse:** K-1…K-5 ve H1–H4 metni bağlayıcı. `03` §8'deki dört revizyon (R-a…R-d)
  danışman üzerinden **yazılı** onaya sunulur. Uydurma referanslar ve Ji vd. sayısı ise revizyon
  değil **hata düzeltmesidir** ve ara/sonuç raporunda düzeltilmiş hâliyle yer alır.
- **Değerlendirmedeyse:** `04a`'daki düzeltmeleri **hemen** yapın. Bir hakem Ji vd. 2023'ü açıp
  "%15–40" arasa bulamaz.
- **Reddedildiyse:** kısıt yok; `03` doğrudan uygulanır ve bitirme tezi geniş iddiayı alır.

**2. Tezin ana iddiası dar mı geniş mi?**
**Öneri: geniş iddia, ama hadis üzerinde derin kanıtla.** Yani: *"LLM destekli bilgi katmanları için
kaynak + karar defteri + türetilmiş görünüm mimarisi; hadis isnad vakasında ölçülmüş kanıt."*
**Gerekçe:** dar iddia (`hadis için güvenilir KG motoru`) 2026 itibarıyla **zayıflamış** — Wirahman
(2026) hadis ER'yi, Raja (2026) isnad-provenance çerçevesini, Asgari-Bidhendi vd. (2025) 1,2M'lik
LLM-destekli korpusu zaten yayımlamış. Dar iddianın rekabet alanı kalabalık. Geniş iddianın rekabeti
daha az ve `06a`+`12`+pilot birlikte onu destekliyor.
**Risk kontrolü:** geniş iddia, iki vaka (kod + Kur'an) *hafif* kalsa bile ayakta durur, çünkü
mimarinin alan-bağımsız çekirdeği (`02` §3.1) hadis verisinde de test edilmiş oluyor.

**3. Genelleme vakası teze girecek mi?**
**Öneri: kod vakası girer (hafif, 20 soruluk küme), Kur'an vakası vaka anlatısı olarak girer.**
**Gerekçe:** Kur'an olayı (`07` C) mimarinin üç failure mode'unu aynı anda gösteren gerçek bir
olaydır ve **hiç ek deney gerektirmez** — yazılması 1 gün. Kod vakası ise geniş iddianın
"aktarılabilirlik" eksenini tek başına taşıyor; tamamen "gelecek çalışma"ya atılırsa geniş iddia
kanıtsız kalır. Şirket kodu **kullanılmaz** (gizlilik).

## Veri

**4. Çalışma dili?**
**Öneri: Arapça birincil (Sanadset 650K, CC0 — bu pakette doğrulandı ve kullanıldı), Türkçe
ikincil ve farklı bir amaç için** (ravi adı normalizasyonu/ER, transliterasyon düzlemi).
**Gerekçe:** Türkçe tam isnad kaynağının varlığı `[UNVERIFIED]` — test edemedim, telifsiz bir
Türkçe derleme bulamadım. Tam isnad garantisi olan tek lisanslı kaynak Arapça. Türkçe meallerde
isnad kısaltılmışsa "Türkçe altın standart" *zincir* düzeyinde imkânsız ama *ravi kimlik* düzeyinde
hâlâ mümkün. **İP0'ın ilk görevi bunu ölçmek** (rastgele 50 metinde tam isnad oranı).
K-5'in dürüst adı: `03` §1.2.

**5. Ravi otorite listesi ve lisansı?**
**Öneri:** Hawramani `hadithtransmitters` (100.915 kayıt) + `muslimscholars.info` (25.247 kayıt).
İkisi de Wirahman (2026) tarafından kullanılmış ve eşleme korpusu açık yayımlanmış.
**Lisanslar ayrıca doğrulanmalı** `[UNVERIFIED]`.
**Hataları kim düzeltir:** kimse upstream'i düzeltmez. Tarih çelişkileri **karar defterine bir
`authority_conflict_resolved` olayı** olarak yazılır (`12` §3). Otorite listesi bir kaynak (S)
değil, küratörlü bir varlıktır; onun üzerindeki hükümler D'ye aittir.

**6. SemanticHadith yeniden kullanılacak mı?**
**Öneri: evet, Hadith Schema onun üzerine kurulsun.**
**Gerekçe:** Künye doğrulandı: Kamran, Abro & Basharat (2023), *Journal of Web Semantics* 78:100797.
Yeniden kullanım katkıyı azaltmaz — aksine "≥8 varlık tipi" taahhüdünü karşılamanın en hızlı yolu
ve **karşılaştırma zemini** verir. Sıfırdan tasarlamak, bir hakemin "mevcut ontolojiyi neden
kullanmadınız?" sorusuna cevapsız bırakır. Fark: SemanticHadith'te (muhtemelen) **aktarım olayı
reifiye değil** ve HITL/karar kaydı yok — özgün katkı orada.

## Mimari

**7. "Yüksek güven → otomatik kabul" kalacak mı?**
**Öneri: kalacak, ama (a) güven skoruna değil **risk skoruna** bağlanacak ve (b) her otomatik kabul
bir `policy_decision` olayı olarak deftere yazılacak.**
**Gerekçe — ölçülmüş:** güven skorunun doğruyu yanlıştan ayırma gücü **AUC 0,626**; 318 adayın
261'i tam olarak 0,90; 0,80–0,89 bandının doğruluğu (0,385) 0,90 bandından (0,904) **daha düşük**.
Yani mevcut politika modelin skor alışkanlığının rehinesi. Risk skoru = grounding ihlali + alan
kuralı ihlali + ER belirsizliği (hepsi deterministik). Ve **site metni düzeltilmeli**: `05` Bölüm C.

**8. Karar defteri bu dönemde uygulanacak mı?**
**Öneri: asgari sürüm, ve P0 önceliğinde.** `decision_events` append-only tablo + **içerik-adresli
hedef** + `rebuild.py`. Tam event sourcing **hayır**.
**Gerekçe:** içerik-adresli hedef olmadan `ReviewItem.item_ref = candidate_id` kalır ve **5 model ×
3 tekrar denemesinde 500 hadislik insan emeği her run'da sıfırlanır.** Bu, projeyi öldürecek tek
teknik kusurdur. Geri kalan event-sourcing özellikleri (upcaster, artımlı materialize) 6 ayda
gereksiz (`02` Saldırı 2).

**9. LLM şart mı?**
**Öneri: ravi mention çıkarımı ve zincir sırası için HAYIR. LLM iki yerde gerekli:
(i) belirsiz mention → otorite eşleştirmesinde aday önerme, (ii) sîga/edat varyasyonunun kural
yazmakla bitmeyen uzun kuyruğu.**
**Gerekçe — ölçülmüş:** deterministik ayrıştırıcı gevşek F1 **0,879**, şema-only LLM **0,865**
(fark ΔF1 = −0,017, %95 GA [−0,072, +0,039] sıfırı kapsıyor) ve deterministik ayrıştırıcı
**recall'de önde** (0,890 vs 0,853). Zincir sırası uyumu 0,995. Maliyet: sıfır token.
Alan-farkındalıklı prompt'la LLM öne geçiyor (F1 0,935) ama **uzun zincirlerde çöküyor**
(8–14 ravide recall 0,654 < ayrıştırıcının 0,776'sı).
**Mimari sonuç:** deterministik segmentasyon **önce**, LLM **zincir başına** ve yalnızca
mention→otorite belirsizliği için.

**10. Model listesi güncellenecek mi?**
**Öneri: evet, ama "aynı ailenin güncel sürümü" gerekçesiyle ve danışmandan yazılı onayla.**
Ek olarak: **model seçimi bir karıştırıcı değişken** — JSON-mode desteği modele göre değişir
(`05` #13). Deneyde bu **raporlanmalı**, aksi hâlde "mimari etkisi" ile "JSON-mode etkisi"
birbirine karışır. Bir açık model (vLLM) sıcaklık kontrolü için **zorunlu**: platform/API
modellerinde sıcaklık ayarı her zaman mümkün değil (pilotta desteklenmedi).

## Değerlendirme

**11. HITL kararlarını kim verecek? Kör protokol nasıl işleyecek?**
**Öneri:** `03` §5.1'deki atama. Özet: katman (a) altın standardı **2 öğrenci kodlayıcı**,
sistem çıktısını görmeden; katman (b) otorite eşlemesi **Prof. Atay + ikinci ilahiyat kodlayıcısı**,
sabit aday kümesinde bağımsız; C5'te karar veren **o hadisin altın standardını üretmemiş** kişi.
Atama tablosu önceden yazılır ve `decision_events.actor_id` ile **denetlenebilir** olur.
**Gerekçe:** `02b` #2 haklı — tek uzman hem HITL'de hem altın standartta olursa HITL koşulunun
precision'ı tanım gereği yüksek çıkar. Bu, H1'in tüm anlamını yok eder.

**12. Tekrarlar için sıcaklık?**
**Öneri: iki farklı tekrar tanımı, ayrı raporlanır.** Açık modeller: **T=0,7, 3 tohum** (örnekleme
varyansı). API modelleri: **3 prompt paraphrase** (prompt duyarlılığı). "3 tekrar" taahhüdü her
iki yolla da sağlanır.
**Gerekçe:** `02b` #5 haklı, T=0'da tekrar varyans üretmez. Ayrıca pilotta gördüm ki bazı
modellerde `temperature` parametresi **artık kabul edilmiyor** — "T=0 ile 3 tekrar" planı teknik
olarak da uygulanamaz hâle gelebilir.

**13. F1 mi F0.5 mi?**
**Öneri: birincil özet F0.5; F1 ve ham P/R her zaman yanında.**
**Gerekçe — ölçülmüş:** hata maliyeti asimetrik ve bu örneklemde **gözlendi**: `سفيان` üç ayrı
raviye (es-Sevrî, b. Uyeyne, b. Habîb) token alt-kümesi olarak eşit uzaklıkta; `ايوب` iki ayrı
kişiye; `ابراهيم` altı farklı ada. Bir yanlış birleştirme zincirin **hükmünü** değiştirir; bir
kaçırılan kenar sadece eksiklik yapar. Ama **F0.5'i tek başına raporlamayın**: pilotta recall
bağlayıcı kısıt (0,85–0,89), precision değil (0,87–1,00). Precision'a ağırlık veren bir özet,
asıl darboğazı gizler.

## İletişim ve itibar

**14. Site ↔ form tutarsızlıkları hangi yöne düzeltilecek?**
**Öneri: kodun gerçeğine doğru, `05` Bölüm C'deki somut metinlerle.**
- "Nothing enters the graph unapproved" → *"Every fact enters either through a human decision or
  through an explicitly recorded policy — and the record says which."*
- "Ungrounded claims are flagged" → C1 kapısı yazılana kadar **kalkar**.
- "reversible" → `rebuild.py` yazılana kadar **kalkar**, "auditable" kalır.
- "AI can suggest a schema" → **kalkar** veya "planned" etiketi alır.
- "Can I use it today? Not yet" ↔ form "uçtan uca çalışır": site *"The engine runs; the hadith
  domain layer and the paper are in development"* demeli. **LICENSE eklenmeli** — form "açık kaynak
  yayımlanmış" diyor, lisans yoksa hukuken açık kaynak değil.
- Katkıcı listesi: **ikisi de listelensin, roller yazılsın.** TÜBİTAK formu bağlayıcı olduğu için
  formdaki isimler değişmez.

**15. Doğrulanamayan referanslar nasıl ele alınacak?**
**Öneri:** `04a` ve `04b`'yi kullanın. Somut:
- **Sil:** Al-Khatib & Stein 2024 (ACL Anthology'de iki yazarın da böyle bir yayını yok),
  Bulut 2017 (böyle bir makale yok), Düzenli 2019 (doğrulanamadı).
- **Değiştir:** Ye vd. → EMNLP **2022** main, s. 1–17 (Findings 2023 değil).
  Bulut → **Aslan, Muhammed (2017)**, Bingöl Ü. İlahiyat Fak. Dergisi 5/10, 269–290.
  Düzenli → **Alam & Schneider (2021)**, arXiv:2102.02009.
- **Kaldır veya kendi sayınızla değiştir:** Ji vd.'ye atfedilen "%15–%40". Surveyin tam metninde
  o sayı yok ve survey KG çıkarımını kapsamıyor. Yerine pilotun kendi ölçümü konabilir
  (`08` §4.3 B3) — bu **daha güçlü** bir cümle, çünkü kendi verinizden.
- **Kural olarak benimseyin:** `06a`'nın disiplini — *bir script veya birincil kaynakla
  doğrulanmamış sayı iddiadır, olgu değildir.* Bu projede ihlal edildi; ihlalin kaynağı
  muhtemelen bir LLM'e kaynakça yazdırmaktı. `04b`'deki her künye Crossref/arXiv'den **çekildi**,
  elle yazılmadı; aynı yöntemi sürdürün.

**16. Yayın hedefi?**
**Öneri:** `09_yayin_plani.md`'de ayrıntılı. Özet: **UBMK/INISTA bildirisi (güvenli teslim) +
arXiv preprint (hemen) + bir uluslararası workshop (hedef)**. Dergi, lisans ekibi için 6 ayda
gerçekçi değil; ama açık veri seti bir **data paper** olarak (ör. *Data in Brief* — Sanadset'in
kendisi orada yayımlandı) ulaşılabilir ve düşük riskli.
