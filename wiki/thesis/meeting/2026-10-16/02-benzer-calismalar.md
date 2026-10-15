# Başkaları ne yapmış

## Hadis tarafı

Bu çalışmaları 8 ve 15 Ekim'de tam metinleriyle okuduk; aşağıda yalnız özetini okuduklarımızı ayrıca belirttik. "Bulamadık" dediğimiz özellikler, okuduğumuz metinlerde yoktu. Bilgi grafı, kişileri ve aralarındaki bağlantıları tutan yapıdır. F1, doğru bulunanlarla kaçırılanları birlikte özetleyen puandır.

| Çalışma | Ne yapıyor? | Bizden farkı |
| --- | --- | --- |
| SemanticHadith 2.0.1, Kamran, Butt ve Basharat (2026) | Altı koleksiyondan 34.458 hadisin bilgi grafını kuruyor. Dil modeli yerine özel eğitilmiş bir tanıyıcı kullanıyor. Üç uzman, koleksiyon başına rastgele 100 örneği kontrol etmiş. | Bilgi başına karar kaydı ve kaynak alıntısı kontrolü bulamadık. Aynı adı taşıyan kişileri işaretliyor veya dışarıda bırakıyor. Aday listesiyle uzmana sormayı gelecek çalışmaya bırakıyor. Biz kişinin kararını kaydedip yeniden kullanmayı sınayacağız. |
| Oumer (2025) | Özel eğitilmiş modeller, platform etiketlerine göre ravi F1'ında 0,98, ilişki F1'ında 0,95'e ulaşıyor. Sayılar yazarın model deposundan. | Çok sayıda etiketli eğitim verisine ihtiyaç duyuyor. Bizim iddiamız daha yüksek çıkarım puanı değil; önerinin kontrolü ve kişinin kararı. |
| AR-Sanad 280K, Mahmoud ve diğerleri (2022) | Ravi kimliğini belirliyor. Gerçek zincirlerde mikro F1 83,5; zincirlerin %60,6'sında en az bir yanlış ravi var. | Biz kimlik kararını hangi durumda yeniden kullanabileceğimizi sınayacağız. AR-Sanad v2 (2024) %94,6, Mosa (2025) %97,8 doğruluk bildiriyor; bunlar yapay zincirlerde ve yalnız özetlerini okuduk. |
| Rezwan (2025) ve Çinici (2026) | Hadis metinlerinde dil modeli kullanıyorlar. Değerlendirmeleri 0 ile 10 arası uzman puanları veya bir yazarın 100 kaydı sayısal sonuç vermeden kontrol etmesi biçiminde. | Biz aynı önerilerde her kontrolün ne yakaladığını insan etiketlerine göre ayrı ayrı ölçeceğiz. |

## Genel bilgi grafı tarafı

Okuma listemizdeki 27 makaleye, bir tarama yazısının işaret ettiği iki sistemi ekledik: toplam 29 çalışma. Dil modeli, metin okuyup öneri üreten yapay zekâ modelidir. Güven skoru, modelin kendi cevabına verdiği eminlik puanıdır.

| Çalışma | Ne yapıyor? | Bizden farkı |
| --- | --- | --- |
| Tsaneva ve diğerleri (2025), en yakın çalışma | Bilimsel bilgi grafını doğrulamak için dil modeli denetçileriyle insanları birleştiren dokuz iş akışı deniyor. İnsanlara bütün ilişkileri, az belgede geçenleri veya model denetçisiyle işlem hattının anlaşamadıklarını gösteriyor. | Yalnız anlaşmazlıkları insana gönderince F1, 75'ten 77 ile 79 arasına çıkıyor; 61 ile 75 arası insan kararı kullanılıyor. Modülleri tek başına değerlendirmediklerini yazıyorlar. Önceki otomatik denetçinin attığı ilişkilerin %34'ü doğruymuş. Biz kontrolleri ayrı ölçeceğiz. |
| KARMA (2025) | Birden çok dil modeli ajanıyla çalışıyor; doğrulama ajanlarını sırayla kaldırıp sonucu ölçüyor. | Sonucu dil modeli hakemi puanlıyor. Biz insan etiketlerini referans alacağız. |
| ODKE+ (Apple, 2025) | İkinci bir dil modeli, kaynağın her bilgiyi destekleyip desteklemediğini soruyor. %35 daha az uydurma bilgi ve %91'den %98,8'e çıkan precision bildiriyor. Precision, kabul edilenlerin doğru olan payıdır. | Nasıl ölçtüğünü açıklamıyor. Biz sabit kuralların etkisini dış referansla ölçeceğiz. |
| Knowledge Vault (Google, 2014) | Bilgiyi, doğrulukla uyumu ayarlanmış güven skoruna göre kabul ediyor. Doğruyla yanlışı ayırma ölçüsü AUC, otomatik etiketlerde 0,959, insan etiketlerinde 0,869. | Biz güven skoruyla kontrolü aynı inceleme payında karşılaştıracağız. |
| HoloClean (2017) | Düşük güvenli veri düzeltmelerini kullanıcıya sormayı öneriyor; bunu denemiyor. | Biz insan incelemesini ölçmeyi planlıyoruz. |
| Zep (2025) | Yeni bilgi eskiyle çelişince dil modeli eski bilgiyi geçersiz sayıyor. | Kararı kişi vermiyor. Biz kişinin kararını saklayıp yeniden kullanmayı sınayacağız. |
| GraphRAG (2024) ve Carriero ve diğerleri (2024) | Tasarımları gereği metinde kelimesi kelimesine bulunmayan çıktıları kabul ediyorlar. | Biz çıkarılan değerin modelin kendi alıntısında bulunmasını ayrı bir kontrol olarak ölçüyoruz. |

Okuduğumuz 29 çalışmanın hiçbirinde çıkarılan değerin modelin kendi alıntısında bulunup bulunmadığı kontrolünü bulamadık; taramamız sistematik değildi.
