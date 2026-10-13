# Wiki yazma kuralları (ajanlar için)

Amaç: yüksek bağlam kaliteli, modüler wiki güncellemeleri.

Ana kural: **bağlam her şeydir.** Yapı yalnız bağlamı erişilebilir kılmak için vardır.

## When to write wiki

Aşağıdakilerden biri olduğunda wiki güncellenir:

- Yeni bir ölçüm yapıldı ya da alıntılanan bir sayı yeniden ölçüldü
- Metrik tanımı, eşleşme kriteri ya da altın standart protokolü değişti
- Ekip ya da danışman bir karar verdi (dil, veri kaynağı, model listesi, hipotez metni)
- Core'da bir kapı, kural ya da şema davranışı değişti
- Danışman toplantısı yapıldı
- Çalışma alanına klasör eklendi, kaldırıldı ya da kapsamı değişti
- Bir kaynakça kaydı doğrulandı ya da uydurma olduğu anlaşıldı
- Kullanıcı bir bilginin kaydedilmesini istedi

## Where to write (routing)

### 1. Var olan konu değişti

- Önce var olan dosya güncellenir.
- Değişiklik günlüğü tutulmaz.
- `Last updated` tarihi güncellenir.

### 2. Ölçüm ve değerlendirme

`wiki/evaluation/` altına. Ölçülen madde `correctness-measurement.md` içinde "Ölçülmemiş olanlar"
listesinden "Ölçülmüş olanlar" tablosuna geçer. Ham sayılar bir sonuç dosyasında durur; wiki o
dosyaya çapa verir.

### 3. Alan davranışı

`wiki/domains/<alan>/` altına (ör. `domains/hadith/schema.md`). İnce bir konu tek dosya kullanır.

### 4. Karar

`wiki/decisions/ADR-NNN-<slug>.md` oluşturulur, `decisions/INDEX.md` içinden bağlanır.
ADR yalnız **neden** ve **tartılmış alternatifleri** taşır. Yalnız ekibin ya da danışmanın onayladığı
şey ADR olur; Claude Science önerisi ADR değildir.

### 5. Taahhüt, açık karar, sıradaki iş

Bir taahhüdün kanıtı değiştiyse `wiki/project/tubitak-commitments.md`; bir soru doğdu ya da kapandıysa
`wiki/project/open-decisions.md`; bir iş bitti ya da sıra değiştiyse `wiki/project/roadmap.md`.

### 6. Toplantı

`wiki/project/supervisor-meetings.md` içine yeni başlık; özet tablosuna satır.

## Mandatory sections (new docs)

- Purpose
- Scope
- Source anchors (çalışma alanı köküne göre yollar)
- Rules (MUST / SHOULD)
- Verification checklist
- Related docs
- Last updated (`YYYY-MM-DD`)

## Update protocol

1. `wiki/README.md` okunur
2. `wiki/architecture/context-quality.md` okunur
3. `wiki/architecture/file-structure.md` okunur
4. `wiki/_templates/` içinden şablon alınır
5. İşe yarar bağlam yazılır: neden, sahip, çapa, kural, doğrulama
6. Yeni dosya `wiki/README.md` ve `architecture/file-structure.md` ağacına eklenir
7. Yerini alan dosya silinir; yönlendirme kalıntısı bırakılmaz

## Style

- Kısa cümle
- Belirsiz tavsiye yok
- MUST / SHOULD dili tutarlı
- Her sayı neyin, kaç veri üzerinde, hangi referansa karşı ölçüldüğünü söyler
- Taksonomik saflık yerine işe yarar bağlam

## Anti-patterns

- Her şeyi tek dev dosyaya yığmak
- Yer tutucu dosya
- `sources/` altındaki bir belgeyi yaşayan sayfaya kopyalamak; bağla
- `sources/` altındaki bir paket dosyasını düzenlemek
- Yöntemsiz sayı, bellekten künye
- Eksik kaynak çapası
- İlgili sayfalar arasında bağ kurmamak
- Aynı kuralı hem ADR'de hem konu sayfasında tekrarlamak

## Last updated

2026-10-13
