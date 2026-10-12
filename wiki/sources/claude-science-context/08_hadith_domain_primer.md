# 08 — Hadis alanı: mühendis için özet

> Bu belge Claude Code'un genel bilgisine dayanıyor, alan uzmanı onayı yok. `[VERIFY]` işaretliler özellikle kontrol edilmeli. Nihai otorite Prof. Dr. Rifat Atay ve klasik kaynaklar.

## Temel yapı
- **Hadis = isnad + metn.** İsnad, rivayet zinciridir (derleyiciden Hz. Peygamber'e ya da sahabiye). Metn, rivayet edilen sözün kendisidir.
- **Sîga (tahammül/edâ lafızları):** *ḥaddeṯenâ* (bize anlattı), *aḫberanâ* (bize haber verdi), *semiʿtu* (işittim), *ʿan* (…den; "an'ane"). Lafız, aktarımın biçimini ve gücünü kodlar. *ʿan* belirsizdir ve **tedlîs** tartışmalarıyla ilgilidir. Bu yüzden kenar (edge) üzerinde bir özellik olarak tutulmalıdır.
- **Rical / cerh-ta'dîl:** Ravilerin biyografisi ve güvenilirlik hükümleri (sika, sadûk, zayıf…). Otorite eserler arasında Tehzîbü'l-Kemâl (el-Mizzî), Tehzîbü't-Tehzîb ve Takrîbü't-Tehzîb (İbn Hacer) sayılabilir `[VERIFY]`.
- **Tabaka:** Kuşak katmanı (sahabe, tâbiûn, etbâu't-tâbiîn…). İbn Hacer Takrîb'de 12 tabaka kullanır `[VERIFY]`.
- **İttisâl (kesintisizlik) şartları:** **Muâsara** (çağdaşlık yeterli; genelde Müslim'e atfedilir) ve **likâ** (en az bir kez buluşmanın sabit olması; genelde Buhârî'ye atfedilir) `[VERIFY]`. Formdaki E-3 kuralları bu iki standarda denk düşüyor. "Likâ kaydı yok → HITL" kuralı, Buhârî standardının makine karşılığı olarak sunulabilir.
- **Ortak halka (common link / medâr):** Birçok isnadın tek bir raviden sonra dallandığı düğüm (Juynboll, Motzki tartışmaları). Sitedeki örnekte Yaḥyā b. Saʿīd al-Anṣārī, *innemâ'l-a'mâl* hadisinin bilinen medârıdır. Graf temsili bu tür ağ analizleri için doğal bir zemin (KG'yi haklı çıkaran sorgu türü).

## İsim yapısı: entity resolution'ın asıl zorluğu
- Bileşenler: **ism** (Süfyân), **nesep** (b. = ibn: "Süfyân b. Uyeyne"), **künye** (Ebû Muhammed), **lakap**, **nisbe** (el-Hilâlî, el-Kûfî, el-Ensârî).
- Aynı kişinin farklı yazımları: "Süfyân b. Uyeyne" / "İbn Uyeyne" / "Süfyân". Ebû Hüreyre'nin ismi rivayetlere göre farklı verilir (formdaki örnek "Abdurrahman b. Sahr").
- **Farklı kişi, aynı kısa ad (over-merge tehlikesi):** Tek başına "Süfyân", Süfyân es-Sevrî ile Süfyân b. Uyeyne arasında belirsizdir. Benzer şekilde "Hammâd" (b. Zeyd / b. Seleme). Klasik ilim bunu hoca/talebe bağlamı ve tabaka ile çözer `[VERIFY örnekler]`. **Sonuç:** ER bağlamsal olmalı (zincirdeki komşular + tabaka + coğrafya) ve bir **ravi otorite listesine linking** şeklinde kurulmalı. Salt string benzerliği yetmez.
- Transliterasyon düzlemleri: Arapça yazım (سفيان بن عيينة), akademik Latin (Sufyān b. ʿUyayna, sitede kullanılan), Türkçe TDV İA tarzı (Süfyân b. Uyeyne), sadeleştirilmiş Türkçe (Sufyan bin Uyeyne). Bir varlık düğümü, tüm düzlemlerdeki alias'ları taşımalı.

## Veri kaynakları (aday, lisans ve varlık doğrulanmalı)
| Kaynak | Ne sunar | Not |
|---|---|---|
| **Sanadset 650K** (Mghari vd., 2022, *Data in Brief*) `[VERIFY]` | Arapça hadisler, isnad/metn ayrımı ve ravi etiketleri | Tam isnad için en güçlü aday olabilir |
| **Hadith narrators dataset** (Kaggle, muslimscholars.info türevi) `[VERIFY]` | ~24k ravi: doğum/vefat, tabaka, hoca/talebe listeleri | Muâsara kuralı ve otorite listesi için aday. Kalitesi denetlenmeli |
| **SemanticHadith KG** (Kamran vd., 2023, *J. Web Semantics*) `[VERIFY]` | Kütüb-i Sitte için RDF ontoloji ve KG | Hazır ontoloji. **Hadith Schema'yı sıfırdan tasarlamadan önce incelenmeli.** Karşılaştırma/baz çizgi olabilir |
| **LK Hadith Corpus** (Altammami vd., 2020) `[VERIFY]` | Arapça-İngilizce paralel altı kitap | İngilizce/Arapça hizalama |
| Open Hadith Data (GitHub), sunnah.com | Metin koleksiyonları | Lisans kontrol edilmeli |
| Diyanet "Hadislerle İslam", Kütüb-i Sitte Türkçe tercümeleri (ör. İ. Canan) | Türkçe metin | **Telif riski.** İsnad genelde kısaltılmış olabilir `[VERIFY]`. Form R2 riskiyle ilgili |

## Mühendislik sonuçları
1. **İsnad bir yol (path), metn bir düğüm.** Aktarım olayı reifiye edilmeli: `(:Transmission {hadith_id, position, sigha})` ya da `NARRATED_FROM {hadith_id, position}` ile hadis-kapsamlı kenar. Mevcut kod aynı çiftin kenarlarını tek kenara indiriyor (`05` #9).
2. **Ön işleme:** İsnad/metn ayrımı ve zincirin ravi dizisine bölünmesi, çoğu zaman LLM'siz (kural/regex + sîga lügati) yapılabilir. Bu, LLM'in işini "sadece ravi adlarını otoriteye bağla" seviyesine indirir. Belki LLM'e hiç gerek bırakmaz. Deterministik parser + LLM karşılaştırması güçlü bir baz çizgi olur.
3. **Muâsara/tabaka kuralları dış bilgi ister.** Otorite listesinden gelen tarihler "karar" statüsündedir, ayrıca kaynaklara göre değişebilirler. Tarih çelişkisi bir review olayı olmalı.
4. **Altın standart iki katmanlı olmalı:** (a) metin → ravi mention span'leri ve zincir sırası (metinden doğrulanabilir), (b) mention → otorite ID (uzman hükmü). Uyum ölçümleri ayrı raporlanmalı.
5. **Hata maliyeti asimetrik.** Yanlış birleştirme ve uydurma ravi, kaçırılan kenardan daha pahalıdır. Precision ağırlıklı hedef (ör. F0.5) ve eşik seçimi gerekçelendirilmeli.
