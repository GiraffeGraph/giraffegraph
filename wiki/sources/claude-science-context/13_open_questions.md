# 13 — Ekibin karar vermesi gereken açık sorular

Claude Science bu soruların her biri için bir öneri ve gerekçe vermeli. Nihai karar ekibe ve danışmana ait.

## Kapsam ve konumlandırma
1. **TÜBİTAK başvurusunun durumu nedir?** (Kabul, ret, değerlendirmede; paket bunu bilmiyor.) Taahhütlerin ne kadar esnek olduğu buna bağlı.
2. Bitirme tezinin ana iddiası ne olacak? **"Hadis için güvenilir KG motoru"** mu (dar, TÜBİTAK ile birebir), yoksa **"LLM destekli bilgi katmanları için genel mimari + hadis kanıtı"** mı (geniş, `12`)? Geniş iddia daha değerli ama daha riskli.
3. Genelleme vakası (kod/Kur'an) teze girecek mi, yoksa "gelecek çalışma" mı kalacak?

## Veri
4. **Çalışma dili:** Arapça tam isnad (Sanadset vb.) mi, Türkçe meal mi, ikisi birden mi? Türkçe meallerde isnad kısaltılmışsa, "Türkçe altın standart" nasıl tanımlanacak?
5. Ravi otorite listesi hangi kaynaktan gelecek, lisansı ne? Otorite listesinin hatalarını kim düzeltecek (karar defteri)?
6. SemanticHadith gibi mevcut ontolojiler yeniden kullanılacak mı, yoksa K-1 sıfırdan mı tasarlanacak? (Yeniden kullanım, katkıyı azaltmaz, karşılaştırma zemini sağlar.)

## Mimari
7. Şu anki "yüksek güven → otomatik kabul" davranışı kalacak mı? Kalacaksa site metni düzeltilmeli. Kalmayacaksa insan bütçesi hesaplanmalı.
8. Karar defteri + yeniden üretilebilir graf (`12`) bu dönemde uygulanacak mı, yoksa sadece append-only karar tablosu gibi asgari bir sürüm mü?
9. LLM şart mı? İsnad ayrıştırmada deterministik parser (Cx) ne kadar ileri gidiyor? LLM'in gerçekten gerektiği tek yer ER belirsizliği olabilir mi?
10. Model listesi güncellenecek mi (Llama-3-8B → güncel aile üyeleri)?

## Değerlendirme
11. HITL kararlarını kim verecek (öğrenciler mi, uzman mı)? Altın standardı kim üretecek? Döngüselliği önleyecek kör protokol nasıl işleyecek?
12. Tekrarlar için sıcaklık ne olacak? (Formda 3 tekrar var. T=0'da anlamsız.)
13. Precision ve recall arasındaki ödünleşimde hangi hedef (F1 mi, F0.5 mi)? Gerekçe asimetrik hata maliyeti.

## İletişim ve itibar
14. Site ile form arasındaki tutarsızlıklar: katkıcı listesi (İbrahim Çakır / Alperen Ulukaya), "use it today? Not yet" ile "yayımlanmış ve çalışır" çelişkisi, lisans yokluğu. Hangi yöne düzeltilecek?
15. Formdaki doğrulanamayan referanslar (`02b`) nasıl ele alınacak?
16. Yayın hedefi: UBMK/INISTA (ulusal/bölgesel) mı, bir EMNLP/ACL workshop'u mu (ör. KG, dijital beşeri bilimler, Arapça NLP workshop'ları) mı, bir dergi mi?
