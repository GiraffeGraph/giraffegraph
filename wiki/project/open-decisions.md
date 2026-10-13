# Açık kararlar

## Purpose

Ekibin ve danışmanın vermesi gereken kararları, her biri için önerilen yanıtı ve kodun ya da ölçümün
bugün fiilen hangi yanıtı varsaydığını yan yana tutmak. Bir karar verilmeden fiilî durum karar gibi
aktarılmasın diye vardır.

## Scope

- In: 2026-09-30 paketindeki 16 açık soru, 2026-10 çalışmasında ortaya çıkan yeni sorular, her birinin
  karar sahibi ve statüsü
- Out: önerilerin tam gerekçesi (`wiki/sources/claude-science-results/07_acik_sorulara_oneriler.md`),
  verilmiş kararlar (`wiki/decisions/`, ilk ADR ile oluşur)

## Statü

2026-10-13 itibarıyla aşağıdaki 25 sorunun hiçbiri için ekip ya da danışman kararı kayıtlı değildir;
`wiki/decisions/` klasörü yoktur. "Fiilî durum" sütunu bir kararı değil, kodun ve ölçümlerin şu an
dayandığı varsayımı gösterir. Bu varsayımların çoğu tek kişinin çalışmasıyla oluştu ve ekipçe
görüşülmedi. Proje sahibinin beyanına göre (Yahya Efe Kuruçay, 2026-10-13) ekip, çerçeve kararını ona
bırakır; danışman onayı ayrıdır.

Karar sahibi kısaltmaları: **E** ekip, **D** danışman (Dr. Taha Yiğit Alkan), **U** alan uzmanı
(Prof. Dr. Rifat Atay).

## Kapsam ve konumlandırma

| # | Soru | Öneri (Claude Science, 2026-09-30) | Fiilî durum | Sahip |
|---|---|---|---|---|
| 1 | TÜBİTAK başvurusunun durumu nedir? | Kabulse revizyonlar yazılı onaya sunulur; değerlendirmedeyse kaynakça hemen düzeltilir; retse kısıt kalkar | Gönderilmedi (proje sahibinin beyanı, 2026-10-13). Form taslaktır; hedefleri ve kaynakçası gönderilmeden önce değiştirilebilir | E |
| 2 | Tezin ana iddiası dar mı (hadis için güvenilir KG motoru), geniş mi (bilgi katmanları için genel mimari, hadis kanıtıyla)? | Geniş iddia, hadiste derin kanıtla | Tez ve makale taslakları dar çerçevededir: motor, kapılar ve hadis ölçümü. Taslaklar `wiki/thesis/` altındadır, gönderilmedi | E, D |
| 3 | Genelleme vakaları (kod tabanı, Kur'an) teze girer mi? | Kod vakası 20 soruluk kümeyle, Kur'an vakası anlatı olarak girer | İkisi için de ölçüm yok. Kur'an olayının kaydı: `wiki/sources/claude-science-context/07_case_codebase_wiki_and_quran.md` | E, D |

## Veri

| # | Soru | Öneri | Fiilî durum | Sahip |
|---|---|---|---|---|
| 4 | Çalışma dili: Arapça tam isnad mı, Türkçe meal mi, ikisi mi? | Arapça birincil; Türkçe yalnız ravi adı normalizasyonu için. Önce 50 Türkçe metinde tam isnad oranı ölçülür | Bütün ölçümler Arapça metinle yapıldı. Telifsiz Türkçe tam isnad kaynağı aranmadı, oran ölçülmedi. K-5 "Türkçe" altın standart taahhüt eder | E, D, U |
| 5 | Ravi otorite listesi hangi kaynaktan, hangi lisansla gelir? Hatalarını kim düzeltir? | Hawramani ve `muslimscholars.info`; çelişkiler karar kaydına yazılır | İndirilen adaylar İfta ravi profilleri (20.957) ve AR-Sanad ravi tablosudur (18.298). Lisans beyanları kayıtlı, yazılı izin yok. Hiçbiri sisteme bağlanmadı | E, U |
| 6 | SemanticHadith ontolojisi yeniden kullanılır mı? | Evet, Hadith Schema onun üzerine kurulur | Kullanılmadı. İsnad şablonu 2 düğüm ve 2 ilişki tipiyle sıfırdan yazıldı | E, U |

## Mimari

| # | Soru | Öneri | Fiilî durum | Sahip |
|---|---|---|---|---|
| 7 | "Yüksek güven → otomatik kabul" kalır mı? | Kalır; güven skoruna değil deterministik risk işaretlerine bağlanır ve her otomatik kabul kayda geçer | Kapıdan geçen aday incelemesiz kabul edilir ve kabul kaydı `auto_validated` politikasını gösterir. Güven eşiği de durur. 300 hadiste güven skorunun ayırma gücü AUC 0,634; aynı inceleme payında değer-alıntı kapısı güven eşiğinden fazla eşleşmeyen mention yakalar | E |
| 8 | Karar defteri bu dönemde uygulanır mı? | Asgari sürüm: ekleme yapılan karar tablosu, içerik adresli hedef, yeniden üretim betiği | `review_decisions` tablosu var (kim, ne zaman, süre, önceki ve sonraki değer). İçerik adresli hedef ve yeniden üretim betiği yok: karar aday kimliğine bağlıdır, yeniden çıkarımda taşınmaz | E |
| 9 | LLM şart mı? | Mention çıkarımı ve sıra için hayır; kimlik belirsizliği ve sîga çeşitliliği için evet. Deterministik bölütleme önce, LLM zincir başına | 300 hadiste kural tabanlı koşul şema-only LLM'i gevşek eşleşmede geçer, katı eşleşmede geride kalır; isnad-farkındalıklı LLM ikisini de geçer. Zincir başına çağrının tüm hadise üstünlüğü ölçülmedi (fark +0,008, aralık sıfırı içerir) | E |
| 10 | Model listesi güncellenir mi? | Evet, aynı ailelerin güncel sürümleriyle ve yazılı onayla; en az bir açık model şart | Koşulan tek model Claude Haiku 5.5. Açık model koşulmadı | E, D |

## Değerlendirme

| # | Soru | Öneri | Fiilî durum | Sahip |
|---|---|---|---|---|
| 11 | HITL kararını ve altın standardı kim üretir? Kör protokol nasıl işler? | Katman (a) iki öğrenci kodlayıcı, sistem çıktısını görmeden; katman (b) uzman ve ikinci ilahiyat kodlayıcısı; HITL kararını veren o hadisin altın standardını üretmemiş kişi | Kimse atanmadı. Etiketleme kiti hazır, gönderilmedi. Hiçbir koşuda inceleme kararı verilmedi | E, D, U |
| 12 | Tekrarlar için sıcaklık ne olur? | Açık modellerde T = 0,7 ile 3 tohum; API modellerinde 3 prompt yeniden yazımı; ayrı raporlanır | `anthropic` sağlayıcısı sıcaklık göndermez. Her koşul bir kez koşuldu | E |
| 13 | Özet metrik F1 mi, F0.5 mi? | Birincil özet F0.5; F1 ve ham P / R yanında | Raporlanan P, R ve F1'dir | E, D |
| 17 | Platform etiketi (İfta) cevap anahtarı olarak yeterli mi, insan altın standardı şart mı? | Öneri yok; soru 2026-10 çalışmasında doğdu | Ölçümlerin hepsi platform ve kural etiketine karşıdır; sayfalar bunu "etiket kümesiyle uyum" diye sunar. K-5 insan altın standardı taahhüt eder | D, U |
| 18 | Bu dönem yalnız çıkarım ve kimlik mi ölçülür, graf üzerinden soru-cevap da mı? | Öneri yok | CSE 491 kapsam ifadesi RAG tabanlı soru-cevabı içerir; L4 için soru kümesi ve kod yok | E, D |

## İletişim ve itibar

| # | Soru | Öneri | Fiilî durum | Sahip |
|---|---|---|---|---|
| 14 | Site ile form ve kod arasındaki tutarsızlıklar hangi yöne düzeltilir? | Kodun gerçeğine doğru; katkıcı listesinde iki isim de rolleriyle yer alır | `web` reposunun `fix/landing-claims` dalında 6 dosyalık metin düzeltmesi commit edildi ve `origin`'e gönderildi; `main`e alınmadı, yayında değil. Katkıcı listesi kararı yok | E |
| 15 | Formdaki doğrulanamayan referanslar nasıl ele alınır? | Üçü silinir ya da gerçek karşılığıyla değiştirilir; Ji vd.'ye atfedilen sayı kaldırılır | Doğrulanmış kaynakça hazır ve tez taslağı onu kullanır. Formun düzeltildiğine ya da danışmana bildirildiğine dair kayıt yok | E, D |
| 16 | Yayın hedefi nedir? | UBMK ya da INISTA bildirisi, arXiv ön baskı, bir uluslararası atölye | Makale biçimli taslak var, gönderilmedi. Hedef seçilmedi | E, D |
| 19 | Core hangi lisansla yayımlanır? | Öneri: lisans eklenir (form "açık kaynak" der) | Repo herkese açık, LICENSE dosyası yok | E |
| 20 | Hangi veri, hangi biçimde yeniden dağıtılabilir? | Form: yalnız üçlü düzeyinde açık yayın | İndirilen veri yeniden dağıtılmaz; değerlendirme kümeleri özel repodadır. Lisans beyanları sürüme göre değişir, Sanadset için iki beyan çelişir | E, D |
| 21 | Prototip davranışı (isnad bölütleme, kapılar, karar kaydı) ekipçe kabul edildi mi? | Öneri yok | Kod `main` dalındadır; ekip görüşmesi ve ADR yok | E |

## Cache and Ledger çalışmasından doğanlar (2026-10-13)

| # | Soru | Öneri | Fiilî durum | Sahip |
|---|---|---|---|---|
| 22 | "Ne saklanmalı" araştırması ayrı bir proje mi olur, hadis projesini mi destekler? | Öneri: hadis projesini destekler; genel sonuçlar tezin tartışma bölümüne girer. Gerekçe: hadis dışına taşınan iki fikir (kopya kontrolü, tanık notu) ölçümde tutmadı; tutan fikir (kararın kapsamı) isnadın tekrar eden yapısına yaslanır | Sonuçlar iki wiki sayfasında ve `cache-and-ledger/MEASUREMENTS.md` içindedir; ayrı repo ve ayrı plan yok | E, D |
| 23 | Kapsamı çelişkiyle daralan kimlik defteri Core'a alınır mı? | Öneri: içerik adresli karar hedefiyle (C3) birlikte alınır; önce gerçek bir inceleyiciyle küçük bir deneme | Benzetim Core'un `feat/identity-ledger` dalındadır; motor kodu yoktur | E |
| 24 | `cache-and-ledger/` kendi reposuna alınır mı? | Öneri yok | Klasör repo değildir; kopyası özel veri reposunda yedektir | E |
| 25 | Bu wiki ajan için nasıl yazılır: davranışı anlatan cümle mi, karar ve yol çapası mı? | Öneri: karar, gerekçe ve çapa; kodun ne yaptığını anlatan cümle yazılmaz (`wiki/evaluation/wiki-for-agents-experiments.md`, Rules) | Yaşayan sayfalar türetilebilir olgu da taşır (test sayıları üç sayfada tekrar eder); sayfalardaki 968 sayının 80'i atıf verilen dosyalarda bulunmaz | E |

## Rules

- MUST: "Fiilî durum" bir karar gibi aktarılmaz. Gerekçe: öneri ile karar ayrıdır; onaysız varsayım
  raporda "karar verildi" diye geçerse danışman ve TÜBİTAK karşısında dayanağı olmaz.
- MUST: bir soru karara bağlandığında `wiki/decisions/ADR-NNN-<slug>.md` yazılır, satır bu sayfadan
  silinir ve ilgili konu sayfası güncellenir.
- MUST: yeni bir açık soru ortaya çıktığında sonraki numarayla bu sayfaya eklenir; numaralar yeniden
  kullanılmaz. 1–16 numaraları `wiki/sources/claude-science-context/13_open_questions.md` ile aynıdır.
- SHOULD: karar toplantısına her soru için fiilî durumun ölçümü götürülür
  (`wiki/evaluation/engine-experiments.md`).

## Source anchors

- `wiki/sources/claude-science-context/13_open_questions.md` — 16 sorunun özgün metni
- `wiki/sources/claude-science-results/07_acik_sorulara_oneriler.md` — öneriler ve gerekçeleri
- `wiki/sources/olcum-nasil-yapilir.html` — danışmana sorulacak üç soru (17, 18 ve katkının tanımı)
- `giraffegraph-core/evaluation/results/2026-10-12-sixbooks300/compare-ifta.md` — soru 7 ve 9'un ölçümü
- `giraffegraph-core/backend/src/app/application/use_cases/review_management.py:list_acceptance_records` — kabul kaydı politikası
- `data/README.md` — lisans beyanları

## Verification checklist

- [ ] Her satırın sahibi var
- [ ] Karara bağlanmış hiçbir soru bu sayfada durmuyor; `wiki/decisions/` ile çapraz kontrol
- [ ] "Fiilî durum" sütunundaki her sayı çapa verilen dosyada bulunuyor
- [ ] `git -C web status --short` çıktısı soru 14'teki durumla aynı

## Related docs

- `wiki/project/tubitak-commitments.md`
- `wiki/project/roadmap.md`
- `wiki/project/overview.md`
- `wiki/evaluation/correctness-measurement.md`
- `wiki/evaluation/decision-ledger-experiments.md`
- `wiki/evaluation/wiki-for-agents-experiments.md`
- `wiki/sources/README.md`

## Last updated

2026-10-13
