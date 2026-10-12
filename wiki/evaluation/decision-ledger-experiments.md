# Karar defteri deneyleri: yeniden kullanım, kapsam ve kopya kontrolü

## Purpose

"The Cache and the Ledger" denemesinin iki iddiasını (kararı bir kez sakla; makine yalnız kopyayı
doğrulayabilir) etiketli veri üzerinde sınayan keşif deneylerinin sonucunu tutmak: hangi iddia tuttu,
hangisi tutmadı, hangi koşulda.

## Scope

- In: ravi kimliği kararlarının yeniden kullanım benzetimi (AR-Sanad), aynı benzetimin hadis dışı iki
  derlemde tekrarı, kopya kontrolünün insan etiketli bir derlemde tekrarı, emsal taraması
- Out: motorun 300 hadislik ölçümü (`wiki/evaluation/engine-experiments.md`), denemenin kendisi
  (`cache-and-ledger/README.md`), motor koduna alınmış bir özellik (bu deneylerin hiçbiri Core'da değildir)

## Statü

Keşif aşaması (2026-10-13). Betikler `cache-and-ledger/data/` altındadır; o klasör hiçbir repoda
izlenmez. Sonuçlar tek kişinin tek oturumunda üretildi; ekip ve danışman görmedi. Sayfadaki yorumlar
öneridir.

## BLUF

1. **Tutan:** hadiste bir ravi kararı çok kez yeniden kullanılır ve kararın *kapsamı* asıl tasarım
   değişkenidir. Kapsam baştan seçilmek yerine çelişkiden türetildiğinde (bir ad ancak çeliştiği
   görülünce bağlama bağlanır) aynı hata düzeyine yaklaşık yarı soruyla yaklaşılır.
2. **Tutan:** tabaka ve vefat yılı kuralı, tek tek olguları doğrulamak yerine bir kararın kapsamını
   daraltmak için kullanıldığında sessiz hata 0,053'ten 0,013'e iner ve soru sayısı artmaz.
3. **Tutmayan:** "hatalar kaynaktan kopyalanmayan kısımda toplanır" iddiası hadis dışında tekrar
   etmedi. İnsan etiketli biyomedikal metinde eşleşmeyen önerilerin %82,5'i kopyadır; modelin güven
   skoru orada kopya kontrolü kadar iyi yönlendirir.
4. **Tutmayan:** komşu bağlamına bağlı karar yalnız bağlam tekrar ediyorsa işe yarar. İsnadda eder;
   serbest metinde etmez ve yeniden kullanımı öldürür.
5. Mekanizma yeni değildir (Ripple-Down Rules, 1990). Açık görünen kısım uygulama ve ölçümdür: varlık
   kararları için kapsam basamakları ve çelişki dedektörü olarak deterministik alan kuralı.

## Tasarım

**Benzetim.** Etiketli zincirler sırayla okunur. Defter bir anahtarı ilk gördüğünde insana sorar
(cevap veri kümesinin etiketidir), sonra cevabı yeniden kullanır. *Soru* insana giden her şeydir: yeni
anahtar, denetim, kural sorusu. *Sessiz hata*, yeniden kullanılan ve etiketle çelişen, hiçbir insanın
görmediği cevaptır. İki oran da mention başına verilir; yeniden kullanım başına oran ayrıca yazılır.

**Veri.** AR-Sanad 280K'nın gerçek test zincirleri: 27.056 zincir, 150.904 mention, 6.378 kişi, 15.301
ayrı ad yazımı (`data/eval/ar-sanad-identity/`). Zincirde önce gelen ad *öğrenci*, sonra gelen
*hoca*dır. Etiketler veri kümesinindir; nasıl atandıkları kaynağında yazmaz (`data/README.md`). Adlar
normalize edilmedi. Sıra rastgele, 10 karıştırmanın ortalaması.

**Kapsam basamakları.** Defter her insan cevabını tam bağlamıyla saklar (öğrenci, ad, hoca → kişi).
Cevabın hangi anahtarla yeniden kullanılacağı saklanmaz; ad başına bir düzeydir ve görülen
çelişkilerden türetilir: ad → (öğrenci, ad) → (öğrenci, ad, hoca).

**Çelişki kaynakları.** (a) Rastgele denetim: yeniden kullanımların bir payı yine de insana sorulur.
(b) Kural: defterin önerdiği kişi ile komşusunun tabaka farkı [−1, 5] ya da vefat yılı farkı [−20, 85]
dışındaysa insana sorulur. Sınırlar aynı verinin gerçek komşu çiftlerinden seçildi; gerçek 123.848
çiftin 1.008'ini (%0,81) işaretler.

## Sonuç 1: bir karar kaç kez yeniden kullanılır

AR-Sanad, sabit anahtarlar.

| Karar neye bağlı | Soru | Soru / mention | Son %10'da soru / mention | Sessiz hata / mention | Sessiz hata / yeniden kullanım | Büyüme üssü |
|---|---:|---:|---:|---:|---:|---:|
| Ad | 15.301 | 0,101 | 0,057 | 0,099 | 0,110 | 0,64 |
| Ad + hoca | 50.877 | 0,337 | 0,244 | 0,025 | 0,037 | 0,81 |
| Öğrenci + ad | 51.244 | 0,340 | 0,244 | 0,006 | 0,009 | 0,80 |
| Öğrenci + ad + hoca | 84.939 | 0,563 | 0,458 | 0,002 | — | 0,89 |

Büyüme üssü, soru sayısının mention sayısına göre log-log eğimidir (verinin %1'i ile tamamı arası);
1'in altı, sorunun veriden yavaş büyüdüğünü gösterir. Bu, sabit bir test kümesi içindeki doygunluğu
ölçer; yeni bir kitaba geçişi ölçmez.

Belirsizlik birkaç adda toplanır: 15.301 adın 815'i (%5,3) birden çok kişiye gider ve mention'ların
%35,9'u bu adların altındadır. Çoğunluk kişisine gitmeyen 11.707 mention'ın %60,4'ü on adın, %86,2'si
yüz adın altındadır. Bu kütlenin %40,1'i akrabalık ifadesidir (`أبيه`, `أبي`, `جده`…).

Öğrenci bağlamının hoca bağlamından iyi ayırması büyük ölçüde bu ifadelerden gelir: "babasından"
ifadesi, kendinden önceki raviye bakılarak çözülür. Bağımsız kontrolde yalnız iç konumlarda fark
0,0031'e karşı 0,0202; akrabalık ifadeleri çıkarılınca 0,0027'ye karşı 0,0057'dir (mention başına).

## Sonuç 2: kapsamı çelişkiden türetmek

AR-Sanad, aynı benzetim.

| Politika | Soru / mention | Sessiz hata / mention |
|---|---:|---:|
| Sabit: ad | 0,101 | 0,099 |
| Sabit: ad; kural yalnız o olguyu insana sorar | 0,202 | 0,053 |
| Kapsam denetimle daralır (%5 denetim) | 0,185 | 0,024 |
| **Kapsam kuralla daralır** | **0,179** | **0,013** |
| Kapsam kural + %5 denetimle daralır | 0,225 | 0,010 |
| Geriye dönük: belirsiz adlar baştan biliniyor | 0,187 | 0,006 |
| Sabit: öğrenci + ad | 0,340 | 0,006 |

Aynı kural iki biçimde kullanıldı. Yalnız işaretlediği olguyu insana sorduğunda hata 0,053'te kalır.
İşaretlediği adın kapsamını da daralttığında hata 0,013'e iner: tek bir çelişki, o adın sonraki bütün
geçişlerini korur. Kural 490 adı daralttı; 815 belirsiz adın geri kalanı ya seyrektir ya da aynı
kuşaktan adaşlardır (kural çağdaşları ayıramaz).

"Geriye dönük" satır üst sınırdır: hangi adların belirsiz olduğu baştan bilinseydi, sabit
(öğrenci, ad) anahtarının hatasına 0,340 yerine 0,187 soruyla ulaşılırdı.

Sağlamlık: kişi dizisi aynı olan zincirler teke indirildiğinde (23.441 zincir) kuralla daralan kapsam
0,192 / 0,014, yalnız soran kural 0,201 / 0,057 verir. Dosya sırasıyla okunduğunda 0,177 / 0,016 ve
0,200 / 0,055.

## Sonuç 3: aynı benzetim hadis dışında

Bağlam anahtarı (önceki dizgi, dizgi). Biyomedikal derlemlerde bir dizgi belge başına bir kez sayıldı.
İki derlem de insan etiketlidir.

| Derlem | Fırsat | Belirsiz dizgi (dizgilerin / fırsatların payı) | Dizgi anahtarı: soru, hata / kullanım | Bağlam anahtarı: soru, hata / kullanım | Geriye dönük: soru, hata / kullanım |
|---|---:|---|---|---|---|
| AR-Sanad (isnad) | 150.904 | %5,3 / %35,9 | 0,101 · 0,110 | 0,340 · 0,009 | 0,187 · 0,008 |
| MedMentions (PubMed, UMLS) | 239.999 | %9,9 / %48,6 | 0,379 · 0,261 | 0,956 · 0,195 | 0,791 · 0,041 |
| BC5CDR (PubMed, MeSH) | 13.642 | %1,3 / %2,4 | 0,422 · 0,015 | 0,922 · 0,005 | 0,438 · 0,001 |

İsnadda aynı hoca-öğrenci çifti binlerce kez tekrar eder; bağlam anahtarı yeniden kullanılır. Serbest
metinde komşu dizgi tekrar etmez; bağlam anahtarı neredeyse her fırsatı yeni soruya çevirir. Defterin
kazancı, anahtarın derlemde ne kadar tekrar ettiğine ve o anahtar altındaki belirsizliğe bağlıdır; ikisi
de küçük bir etiketli örnekten ölçülebilir.

Bilgi ölçüsüyle: bir kişiyi adlandırmak AR-Sanad'da 9,65 bit ister; ad yazımı bilindiğinde geriye
0,39 bit kalır (MedMentions 12,76 → 0,46; BC5CDR 9,99 → 0,02). Kalan kısım yerine koyma tahminidir ve
bir kez geçen dizgileri sıfır sayar; alt sınır olarak okunur.

## Sonuç 4: kopya kontrolü hadis dışında tutmadı

BC5CDR test kümesinden 300 özet, Claude Haiku 5.5 (effort `low`), 2.774 insan etiketli dizgi. Model
her varlık için ad ve destekleyen alıntı verir. *Kopya*: alıntı metinde, ad alıntıda. *Dönüştürülmüş*:
ad kendi alıntısında yok. Eşleşme gevşek yüzey eşleşmesidir (eşit, içerme ya da token F1 ≥ 0,60).

| | Şema-only istem | "Adı harfi harfine kopyala" istemi |
|---|---:|---:|
| Öneri · precision · recall | 2.269 · 0,867 · 0,709 | 2.436 · 0,858 · 0,754 |
| Kopya: öneri (payı) · precision | 2.177 (%95,9) · 0,885 | 2.419 (%99,3) · 0,860 |
| Dönüştürülmüş: öneri (payı) · precision | 89 (%3,9) · 0,404 | 9 (%0,4) · 0,556 |
| Eşleşmeyenlerin kopya / dönüştürülmüş kısımdaki payı | %82,5 / %17,5 | %98,0 / %1,2 |
| Güven skorunun ayırma gücü (AUC) | 0,798 | 0,780 |
| Aynı inceleme payında yakalanan eşleşmeyen: kopya kontrolü / en düşük güven | 53 / 58 (92 öğe, 303 eşleşmeyen) | 7 / 9 (17 öğe, 345 eşleşmeyen) |

Dönüştürülmüş öneri tek tek daha risklidir (eşleşmeme oranı 0,60'a karşı 0,115) ama azdır. Eşleşmeyenlerin
çoğu metinden doğru kopyalanmış, insanların etiketlemediği dizgilerdir (`placebo`, `saline`, `mortality`).
Kopya kontrolü kaynağı kanıtlar; seçimin doğru olduğunu kanıtlamaz.

Hadiste aynı kontrol mention'ların %9,2'sini işaretlemiş ve eşleşmeyen 145 mention'ın 122'sini
kapsamıştı; güven skorunun AUC'si 0,634'tü (`wiki/evaluation/engine-experiments.md`). O sonucun iki
özel nedeni vardır: şema-only istem Arapça adları Latin harfine çeviriyordu, ve hem kontrol hem
puanlayıcı yüzey biçimine bakar; dönüştürülmüş bir ad ikisinden de yapısı gereği kalır.

Seçim hataları tekrar da etmez: şema-only koşuldaki 250 eşleşmeyen kopya 237 ayrı dizgidir. "Bu dizgi
bir kez reddedildi, sonra da reddet" kuralı sonraki hataların 13'ünü yakalar ve 11 doğru öğeyi yanlış
reddeder (20 karıştırma ortalaması).

Harcama: 0,20 USD (600 çağrı).

## Emsal

Bir alt ajan 2026-10-13'te birincil dizinlerden çekti; künyeler ayrıca doğrulanmadı.

| Konu | En yakın iş | Buradaki fark |
|---|---|---|
| Düzeltmeyi, yanılan kuralın yerel istisnası olarak eklemek | Ripple-Down Rules: Compton ve Jansen 1990, DOI 10.1016/S1042-8143(05)80017-2 | Aynı mekanizma. Varlık kararlarına ve deterministik alan kuralına uygulanması bulunmadı |
| Saklanan düzeltmenin yarıçapı; çelişkide daralma | GRACE: Hartvigsen vd. 2023, arXiv:2211.11031 | Gömme uzayında; burada açık bağlam anahtarı |
| İnsan sorusunu azaltan varlık çözümleme | CrowdER: Wang vd. 2012, arXiv:1208.1927; Mazumdar ve Saha, arXiv:1706.07719 | Kuram maliyetin ayrı varlık sayısıyla ölçeklendiğini söyler; saklanan kararın yeniden kullanım eğrisi ölçülmemiş |
| Kaynaktan kopya ile sadakat ilişkisi | Ladhak vd. 2022, arXiv:2108.13684 | Özetlemede biliniyor |
| İçerme kontrolü tek başına sinyal olarak | Raduta vd. 2026, arXiv:2607.17883 (RAGTruth'ta AUROC 0,627) | Zayıf sinyal bulgusu Sonuç 4 ile uyumlu |
| Türetilebilirlik = koşullu entropi sıfır | Kenig ve Suciu 2022, arXiv:1812.09987 | Veritabanı kuramında biliniyor |
| Ravi ayrıştırmada komşu bağlamı | Mahmoud vd. 2022, DOI 10.3390/info13020055 | Model iki komşuyu birlikte görür; öğrenci ve hoca yönü ayrı sınanmamış |

## Sınırlar

- "İnsan" veri kümesinin etiketidir: ilk cevap hatasız ve bedava sayılır. Soru sayısı dakika ya da
  uzmanlık değildir.
- AR-Sanad kişi etiketlerinin nasıl atandığı bilinmiyor; etiketle çelişki hata olmayabilir.
- Rastgele sıra doygunluğu ölçer. Yeni bir kitaba ya da yeni bir terminolojiye geçiş sınanmadı.
- Kuralın sınırları ölçüldüğü veriden seçildi; ayrı bir veride sınanmadı.
- Kural yalnız AR-Sanad'da denendi; başka bir alanda karşılığı kurulmadı.
- Kopya kontrolü tek model, tek derlem ve 300 belgede tekrarlandı; eşleşme yüzey biçimine bakar.
- Hiçbir deneyde gerçek bir insan karar vermedi.

## Rules

- MUST: "hatalar kopyalanmayan kısımda toplanır" cümlesi genel bir bulgu olarak yazılmaz. Gerekçe:
  hadis dışındaki tek tekrarda tutmadı (Sonuç 4).
- MUST: kapsam daraltma "yeni mekanizma" diye sunulmaz; Ripple-Down Rules'un bir uygulaması olarak
  sunulur.
- MUST: bu sayfadaki oranlar aktarılırken paydası (mention başına / yeniden kullanım başına) ve
  cevabın veri kümesi etiketi olduğu yazılır.
- SHOULD: K-3 kuralları (muâsara, tabaka) Core'a alınırken iki kullanım ayrı ölçülür: olguyu
  incelemeye yollamak ve kararın kapsamını daraltmak (`wiki/project/tubitak-commitments.md`, K-3).
- SHOULD: karar hedefinin içerik adresi tasarlanırken (C3) kapsam alanı saklanan değil türetilen bir
  değer olarak ele alınır.

## Source anchors

- `cache-and-ledger/data/explore-decision-growth.py`, `decision-growth-ar-sanad.json` — Sonuç 1
- `cache-and-ledger/data/explore-scoped-ledger.py`, `scoped-ledger-ar-sanad.json` — Sonuç 2, kural kalibrasyonu, bilgi ölçüleri
- `cache-and-ledger/data/explore-ledger-domains.py`, `ledger-domains-ar-sanad.json`, `ledger-domains-medmentions.json`, `ledger-domains-bc5cdr.json` — Sonuç 3
- `cache-and-ledger/data/explore-copy-check-bc5cdr.py`, `copy-check-bc5cdr.json` — Sonuç 4
- `data/eval/ar-sanad-identity/` — zincirler ve ravi tablosu
- `data/README.md`, "4. Two biomedical corpora" — MedMentions ve BC5CDR kaynakları, lisans beyanları
- `cache-and-ledger/README.md` — sınanan iddiaların kaynağı

Sağlamlık kontrolleri (teke indirme, dosya sırası, akrabalık payı, ret defteri) ve yön farkının bağımsız
kontrolü oturum içinde koşuldu; çıktıları dosya olarak kayıtlı değil.

## Verification checklist

- [ ] `python3 -I cache-and-ledger/data/explore-scoped-ledger.py data/eval/ar-sanad-identity/chains.jsonl data/eval/ar-sanad-identity/narrators.csv` çıktısı Sonuç 2 tablosuyla aynı
- [ ] `python3 -I cache-and-ledger/data/explore-ledger-domains.py chains data/eval/ar-sanad-identity/chains.jsonl` çıktısı Sonuç 3'ün ilk satırıyla aynı
- [ ] `copy-check-bc5cdr.json` içindeki `parts` alanı Sonuç 4 tablosuyla aynı
- [ ] Sayfada etikete karşı ölçülen hiçbir değer "doğruluk" diye anılmıyor

## Related docs

- `wiki/evaluation/engine-experiments.md`
- `wiki/evaluation/correctness-measurement.md`
- `wiki/evaluation/related-work.md`
- `wiki/project/tubitak-commitments.md`
- `wiki/project/roadmap.md`

## Last updated

2026-10-13
