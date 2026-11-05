# Türkçe sürüm: kurallar ve terimler

Tezin ve makalenin Türkçe sürümleri İngilizce kaynaktan çevrilir. İngilizce metin asıldır; bir bölüm
değiştiğinde Türkçe karşılığı aynı görevde güncellenir. TÜBİTAK formu yalnız Türkçedir.

## Dosyalar

| İngilizce kaynak | Türkçe sürüm |
|---|---|
| `chapters/NN-ad.md` | `chapters-tr/NN-ad.md` (aynı dosya adı) |
| `paper/paper.md` | `paper/paper-tr.md` |
| yok | `tubitak/form.md` |

## Çevrilmeyenler

Aşağıdakiler kaynaktaki hâliyle, karakteri karakterine kalır:

- Kod blokları, ters tırnak içindeki her şey (dosya yolları, kimlikler, komutlar, Arapça dizgiler)
- Atıf anahtarları: `[@anahtar]` ve `[@a; @b]`
- `<!-- ... -->` yorum satırları
- Görsel yolları: `![...](figures/...)`; yalnız köşeli parantez içindeki açıklama çevrilir
- `:::` ile başlayan blok işaretleri
- Model, veri kümesi, yazılım ve kişi adları
- Tablo yapısı: satır ve sütun sayısı, sütun sırası

## Sayılar

- Her sayı kaynaktakiyle aynıdır. Çeviri sayı eklemez, çıkarmaz, yuvarlamaz.
- Ondalık ayırıcı virgüldür: `0.923` → `0,923`. Binlik ayırıcı noktadır: `27,056` → `27.056`.
- Yüzde işareti sayıdan önce yazılır: `84%` → `%84`.
- Ters tırnak ve kod bloğu içindeki sayılara dokunulmaz.

## Terimler

Bir terim her yerde aynı karşılıkla yazılır.

| İngilizce | Türkçe |
|---|---|
| large language model (LLM) | büyük dil modeli (BDM); ilk geçişten sonra "model" |
| knowledge graph | bilgi grafı |
| human-in-the-loop | insan-döngülü |
| hallucination | halüsinasyon |
| unsupported fact | kaynağın desteklemediği olgu |
| schema drift | şema sapması |
| hadith, isnad, matn | hadis, isnad, metin |
| narrator, chain | ravi, zincir |
| chain position | zincir konumu |
| mention | geçiş (ravi geçişi) |
| candidate | aday |
| proposal (modelin çıktısı) | öneri |
| quotation | alıntı |
| check | kontrol |
| quotation-in-source check | alıntı-kaynakta kontrolü |
| value-in-quotation check | değer-alıntıda kontrolü |
| review, reviewer, review queue | inceleme, inceleyici, inceleme kuyruğu |
| reason code | gerekçe kodu |
| decision record | karar kaydı |
| decision ledger | karar defteri |
| acceptance, acceptance policy | kabul, kabul politikası |
| schema-only model / condition | yalnız şema verilen model / şema-only koşul |
| model with descriptions and hints | tip açıklamaları ve alan ipuçları eklenen model |
| rule-based parser | kural tabanlı ayrıştırıcı |
| strict / loose matching | katı / gevşek eşleştirme |
| reference labels | referans etiketleri |
| platform-derived labels | platform kaynaklı etiketler |
| gold standard | altın standart |
| matched / unmatched proposal | etiketle eşleşen / eşleşmeyen öneri |
| confidence (model's) | güven skoru |
| silent error | sessiz hata |
| scope (of a decision) | kapsam |
| student, teacher (zincirde) | öğrenci, hoca |
| held-out collection | dışarıda bırakılan kitap |
| six canonical collections | altı temel hadis kitabı |
| coding agent, tool call | kod ajanı, araç çağrısı |
| fresh / stale page | taze / bayat sayfa |
| backend, dashboard | arka uç, panel |
| Chapter, Section, Table, Figure, Appendix | Bölüm, Bölüm, Tablo, Şekil, Ek |
| Senior Design Project | Bitirme Projesi |
| run, condition | koşu, koşul |
| prompt | istem |
| pipeline | boru hattı |
| source unit, segment | kaynak birimi, segment |
| schema template, provider | şema şablonu, sağlayıcı |
| node, relation, property | düğüm, ilişki, özellik |
| unknown type / property | tanımsız tip / özellik |
| canonical graph | kanonik graf |
| acceptance record | kabul kaydı |
| test set, pilot set | test kümesi, pilot küme |
| baseline | taban çizgisi |
| requirement, out of scope | gereksinim, kapsam dışı |
| threats to validity | geçerlilik tehditleri |
| future work | gelecek çalışma |
| kinship reference | akrabalık ifadesi |
| transliterate, transliteration | çevriyazıya çevirmek, çevriyazı |
| grammatical case | ad hâli |
| span | metin aralığı |
| review workload | inceleme yükü |
| paired bootstrap interval | eşli bootstrap aralığı |

`precision`, `recall`, `F1`, `AUC`, `bootstrap`, `B-cubed` ve `commit` İngilizce kalır.

## Üslup

Metin, alanını bilen bir araştırmacının yazdığı düz akademik Türkçedir. Çeviri kokmaz: cümle
İngilizcenin sırasını değil, Türkçenin doğal sırasını izler.

- Özne biziz: "ölçtük", "bulduk", "sınamadık". Edilgen yapı yalnız yapanın önemsiz olduğu yerde kullanılır.
- TÜBİTAK formu bu kuralın istisnasıdır. Danışman 2026-11-05'te birinci çoğul kişili taslağı yapay zekâ
  kokulu buldu ve resmî üslupla bir örnek gönderdi. Formda planlanan iş edilgen gelecek zamanla
  ("ölçülecektir"), ön bulgu geçmiş zamanla ("işaretledi"), mevcut durum "hazırdır" ile yazılır; cümle
  sonları ve uzunlukları çeşitlenir. İki kanıt kontrolü formda "alıntının kaynakta bulunması denetimi" ve
  "adın alıntıda bulunması denetimi" adını taşır.
- Her iddia kaynaktaki kadar güçlüdür. Çeviri bir çekinceyi silmez, bir çekince eklemez.
- Uzun tire (—) ve kısa tire (–) noktalama olarak kullanılmaz; virgül, nokta, iki nokta ya da parantez
  kullanılır. Kaynakta tabloda ya da tarihte duran aralık tiresi aynen kalır.
- Şişirme sözcükler yazılmaz: "önemli bir rol oynar", "kritik", "çığır açan", "kapsamlı", "güçlü bir
  biçimde", "dikkat çekicidir", "altını çizmek gerekir".
- Dolgu yazılmaz: "şunu belirtmek gerekir ki", "bu bağlamda", "söz konusu", "-ması nedeniyle" zinciri.
  "Çünkü", "için", "-dığı için" yeter.
- "Yalnızca X değil, aynı zamanda Y" kalıbı ve üçlü sıralama alışkanlığı kaynakta yoksa eklenmez.
- Bir şey için tek ad kullanılır; aynı kavram paragraf içinde eşanlamlılarla dolaştırılmaz.
- Başlıklarda yalnız ilk sözcük ve özel adlar büyük harfle başlar.
- Kalın yazı kaynakta neredeyse oradadır; yeni kalın eklenmez.
- Düz tırnak (") kullanılır.
- Paragraf, son somut bilgiyle biter; genel bir iyimserlik cümlesiyle bitmez.

## Denetim

Çeviri bittiğinde her dosya çifti için şunlar aynı olmalıdır: sayıların kümesi (ondalık ve binlik
ayırıcı dönüştürüldükten sonra), atıf anahtarlarının sırası, ters tırnak içindeki dizgiler, tablo satır
sayısı, başlık sayısı ve düzeyi.
