# Bağlam kalitesi standardı

## Purpose

Wiki'yi ajanlar ve insanlar için işe yarar tutmak: dosya yapısı değil, nitelikli bağlam korunur.

## Scope

- In: bir sayfanın wiki'de yer hak etme ölçütü
- Out: herhangi bir konunun içeriği

## Mindset

Bağlam üründür. Klasör yapısı yalnız erişimi kolaylaştırır.

Bir sayfa, sonraki oturumda şu sorulara cevap verdiriyorsa değerlidir:

- Hangi sorun var?
- Bu yol neden seçildi?
- İddiayı hangi dosya, script ya da veri kanıtlıyor?
- Kural çiğnenirse ne bozulur?
- Doğru olduğunu nasıl sınarız?

## Rules

- MUST: türetilebilen bilgi wiki'ye kopyalanmaz, bağlanır. Wiki kararları, gerekçeleri, durumu ve
  yönlendirmeyi taşır. Gerekçe: `cache-and-ledger/README.md`; kopyalanan olgu kaynağı değişince çürür.
- MUST: her iddia bir kaynak çapasıyla biter: çalışma alanı köküne göre dosya yolu, gerekiyorsa
  bölüm ya da sembol (`wiki/sources/claude-science-results/pilot_isnad.py:align`).
- MUST: her sayı neyin, kaç veri üzerinde, hangi referansa karşı ve hangi tarihte ölçüldüğünü söyler.
  Yöntemi olmayan sayı `[UNVERIFIED]` etiketi taşır.
- MUST: yalnız güncel durum yazılır. Tarihçe git'te ve ADR'lerde yaşar.
- MUST: öneri ile karar ayırt edilir. Onaylanmamış protokol "öneri" diye etiketlenir.
- MUST: bilinmeyen şey açıkça "kayıtlı değil" diye yazılır; tahminle doldurulmaz.
- MUST NOT: yer tutucu ya da yalnız yönlendirme içeren sayfa.
- SHOULD: bölünmüş dosyalar tek cümleyi tekrar ediyorsa birleştirilir.
- SHOULD: sayfa adı ve başlıklar, aranacak kelimeleri içerir (`altın standart`, `over-merge`, `isnad`).

## Good context shape

```md
## Purpose
Bu sayfa neyi koruyor ya da mümkün kılıyor.

## Scope
Neyi kapsar, neyi kapsamaz.

## (içerik)
Karar, gerekçe, durum. Sayılar yöntemiyle.

## Rules
MUST / SHOULD ve gerekçesi.

## Source anchors
Çalışma alanı köküne göre yollar.

## Verification checklist
Gerçek davranışı sınayan adımlar.
```

## Anti-patterns

- Bir snapshot dosyasının içeriğini wiki'ye aktarmak
- Yöntemi yazılmamış sayı
- Bellekten yazılmış künye
- Gümüş standart sonucunu mutlak doğruluk gibi sunmak
- Gerçek davranışı sınamayan kontrol listesi

## Verification checklist

- [ ] Sayfa yalnız "ne"yi değil "neden"i de söylüyor
- [ ] Kaynak çapaları var ve dosyalar yerinde
- [ ] Yer tutucu içerik yok
- [ ] Her sayının yöntemi var
- [ ] Öneri ve karar ayrı etiketli

## Related docs

- `wiki/architecture/file-structure.md`
- `wiki/WIKI-CREATOR.md`
- `wiki/README.md`

## Last updated

2026-10-08
