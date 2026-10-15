# Farkı nerede ve nasıl ortaya koyacağız

## Neyi iddia etmiyoruz?

Yeni şema (veri düzeni), daha yüksek çıkarım doğruluğu, belirsizliği insana sorma veya kaynak kaydetme fikrinin yeniliğini iddia etmiyoruz. Bilgi grafında (kişiler ve bağlantıları) kişinin kararını saklama, kaynaktan çıkarılabileni yeniden çıkarma iddiasını sınayacağız. Henüz danışman onayı almadık.

## D1: Değer, alıntının içinde mi?

Dil modeli (metin okuyan yapay zekâ modeli) doğru bir alıntı verip içinde bulunmayan bir ad önerebilir. Temsili örnek: metinde "Süfyân" yazarken model "Süfyân b. Uyeyne" yazabilir. Alıntı doğrudur; önerilen değer içinde yoktur. Bunu ayrı hata türü olarak ölçüyoruz.

Yalnız şema verilen Claude Haiku 5.5 koşusunda kontrol, 1.688 ravi önerisinin 155'ini (%9,2) işaretledi. İfta platformunun etiketleriyle uyuşmayan 145 önerinin 122'sini (%84) yakaladı; 33 yanlış alarm verdi, 23 uyuşmazlığı kaçırdı. Etiketler insan cevap anahtarı değil; kişi karar vermedi. İşaretlenenlerin çoğu uydurma ravi değil, Latin harflerine çevrilmiş veya dil bilgisel biçimi değiştirilmiş doğru adlardı.

İnsan etiketleriyle bu ayrımı yeniden sayacağız.

## D2: Her kontrol tek başına ne yakalıyor?

Aynı önerilerde kontrolleri ayrı ölçeceğiz. Buna ablation, yani parçaları çıkarıp katkılarını karşılaştırma diyoruz. Sonucu dil modeline puanlatmayacağız.

Model, Peygamber'i 10 kez ravi yazdı; değer kontrolü 2'sini yakaladı. Henüz eklemediğimiz "Peygamber ravi değildir" kuralı kalan 8'ini yakalardı.

İlahiyat alanından Prof. Dr. Rifat Atay, etiketleme kılavuzunu inceleyip açık soruları yanıtlayacak. Deniz ve Alperen, sistem çıktısını görmeden 50 hadisi bağımsız etiketleyecek. Uyumlarını karşılıklı F1 ile ölçeceğiz. F1, doğru bulduklarımızı ve kaçırdıklarımızı birlikte özetleyen puandır. Hadis başına süreyi kaydedeceğiz. Anlaşmazlıkları uzman karara bağlayacak.

## D3: Modelin eminliğinden daha yararlı mı?

Güven skoru, modelin kendi cevabına verdiği eminlik puanıdır. Kontrolü bununla aynı inceleme payında karşılaştıracağız.

İfta etiketlerinde güven skoru 0,85'in altındakileri incelemeye göndermek, 275 öneriyi (%16,3) gönderip 145 uyuşmazlığın 50'sini yakalıyor. İnsan etiketli biyomedikal BC5CDR verisinde ise kontrol 303 uyuşmazlığın 53'ünü, aynı inceleme payındaki güven skoru 58'ini yakaladı. Kontrol her yerde daha iyi değil.

İnsan etiketli hadislerde aynı pay karşılaştırmasını yapacağız. O hadisi etiketlememiş bir ekip üyesi inceleme kuyruğuna karar verecek. Karar süresini, ret oranını ve işaretlenenlerin daha sık reddedilip reddedilmediğini ölçeceğiz. Kuyruğa uzman karar vermeyecek; cevap anahtarını belirleyen kişi sistemi puanlamayacak.

## D4: Kişinin kararını yeniden kullanmak

Motor her kabul için karar veren kişiyi veya adlı kuralı ve zamanı kaydediyor. Ravi kimliği kararını yeniden kullanacak, nesil ve ölüm yılı kuralı çelişki bulursa geçerli olduğu alanı daraltacağız. Mekanizmanın yeni olduğunu iddia etmiyoruz; en yakın çalışma Zep'te kararı kişi yerine model veriyor.

AR-Sanad'ın 27.056 gerçek zincirindeki 150.904 ad geçişiyle benzetim yaptık; incelemeciyi veri etiketi temsil etti. Yalnız ada dayalı kararın hata oranı 0,100'dü. Çelişkide daraltma, kararı baştan dar bir alanda geçerli saymaya göre %48 daha az soru sordu. Sessiz hata (sormadan verilen yanlış karar) farkı geçiş başına 0,008'di. İfta'nın 205.514 geçişinde sonuç %32 ve 0,003'tü. Defter henüz motorda yok.

Kod çalışmasında, "kod neden böyle?" sorularına doğruluk kodla %0 ile %4, karar defteriyle %88 ile %100 oldu: 12 soru, ikişer koşu. İnsan kararlarıyla kimlik tekrar kullanımını sınayacağız.

## Aynı önerilerde karşılaştırma

Alperen'in önerdiği karşılaştırmanın ölçülen satırlarını mevcut koşulardan hesapladık: 300 hadis, yalnız şema verilen model, İfta etiketleri, esnek eşleştirme. Son satır kişi gerektiriyor; henüz ölçmedik. Precision, kabul edilenlerin doğru olan payı; recall, doğru cevapların ne kadarını bulduğumuzdur.

| Adım | Precision / Recall / F1 | Not |
| --- | --- | --- |
| 1. Yalnız model | 0,914 / 0,868 / 0,890 | İnceleme yok. |
| 2. + şema kontrolü | Değişmiyor | Haiku koşularında 910 çağrıda tanımsız tip çıkmadı; bir tanımsız özellik çıktı. |
| 3. + alıntı kaynakta mı kontrolü | Değişmiyor | Hiçbir şey işaretlemedi. |
| 4. + değer alıntıda mı kontrolü | 0,985 / 0,849 / 0,912 | İncelemesiz kabul edilenler; 155 öneri incelemeye gider. |
| 5. + insan incelemesi | Henüz ölçülmedi | Kişi gerekiyor. |

Recall biraz düşüyor çünkü işaretlenen öneriler silinmeden inceleme bekliyor. İnsan etiketleriyle yanlış önerileri, tamamen doğru zincirlerin payını, kişiye gönderilenleri ve kişinin değiştirdiklerini ölçeceğiz.

## Ne olursa haksız çıkarız

Kontrol, insan etiketlerine göre az hata yakalarsa veya güven skoru aynı inceleme payında aynı sayıda hata yakalarsa fark iddiamız desteklenmez.
