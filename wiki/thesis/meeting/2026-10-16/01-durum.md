# Proje bir bakışta

## Ne yapıyoruz?

Bir büyük dil modeline (BDM, metin okuyan bir yapay zekâ modeli) hadis okutuyoruz. Model, isnaddaki (aktarım zincirindeki) ravileri, yani aktaran kişileri ve sıralarını öneriyor. Sabit kurallarla çalışan kontroller, kaynağın desteklemediği önerileri ayırıp inceleme kuyruğuna gönderiyor. Kuyruğa henüz gerçek bir kişi karar vermedi.

Bilgi grafında, kişileri ve aralarındaki bağlantıları tutuyoruz. Model buraya doğrudan yazamıyor. Kabul edilen her bilgi için kimin veya hangi adlı kuralın, ne zaman kabul ettiğini kaydediyoruz.

## Savunduğumuz fikir

Dil modeliyle kurulan bilgi katmanında kişinin kararını saklamalıyız. Kaynaktan yeniden çıkarılabilen bilgiyi yeniden çıkarmalı, saklamamalıyız. Bu, proje sahibinin seçtiği iddia; henüz danışman onayı almadık. Ana kanıtı hadis motoruyla, destekleyici sınamaları kimlik kararları ve kod hakkında soru cevaplama çalışmalarıyla sunacağız.

## Şimdiye kadar ne ölçtük?

Hadis çıkarımı sonuçlarını İfta adlı mevcut platformun etiketlerine göre ölçtük. Bunlar insanların hazırladığı bir doğru cevap anahtarı değil. Tek model kullandık: Claude Haiku 5.5. Hiçbir koşuda kişi karar vermedi.

| Ölçüm | Sonuç |
| --- | --- |
| Altı koleksiyondan 300 hadis, esnek eşleştirmeyle F1 | Kural tabanlı ayrıştırıcı: 0,923; yalnız şema verilen model: 0,890; tür açıklamaları ve alan ipuçlarıyla: 0,956 |
| "Değer alıntıda mı?" kontrolü, yalnız şema verilen model | Etiketlerle uyuşmayan 145 önerinin 122'sini yakaladı (%84); 33 yanlış alarm verdi. |
| İncelemesiz kabul edilenlerde precision | Kontrol ile 0,914'ten 0,985'e çıktı. |

F1, doğru bulduklarımızı ve kaçırdıklarımızı birlikte özetleyen puandır. Precision, kabul edilen önerilerin ne kadarının doğru olduğudur. Değer kontrolünün işaretlediklerinin çoğu uydurma ravi değildi; model adları Latin harfleriyle yazmış veya dil bilgisel biçimini değiştirmişti.

## Hangi belgeler hazır?

Tez taslağımız 55, makale taslağımız 11 sayfa; ikisi de İngilizce ve Türkçe hazır. Gönderilmemiş TÜBİTAK 2209-A form taslağımız, son metni hazır CSE 491 proje önerimiz ve hadis uzmanı için bilgi notlarımız var. Danışmanımız bunların hiçbirini henüz okumadı.

## Neler eksik?

İnsan etiketimiz ve insan incelemecimiz yok. Kimlik karar defteri yalnızca benzetimde var. Alan kurallarını motora eklemedik. Tek model denedik. Kaynak taramamız sistematik değildi.
