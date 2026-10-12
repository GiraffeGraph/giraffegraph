# GiraffeGraph paneli

GiraffeGraph Core'un ürün içi paneli. Bir hadis metnindeki ravi zincirini çıkarma, emin olunamayan
önerileri inceleme ve grafa yazılmış zincirleri okuma adımlarını tek bir akışta sunar. Tanıtım sitesi
bu klasörde değildir.

Next.js 15 (App Router), React 19, TypeScript ve düz CSS kullanır; bileşen kütüphanesi ve Tailwind
yoktur. Arayüz metinleri Türkçedir.

## Ekranlar

| Adres | Ekran |
|---|---|
| `/` | Projeler: iki cümlelik tanıtım, her proje için durum satırı, "Yeni proje" |
| `/proje/[projectId]/yukle` | 1. adım, Metin yükle: yapıştır, `.json` dosyası seç ya da örnek hadisleri yükle |
| `/proje/[projectId]/cikar` | 2. adım, Zincirleri çıkar: yöntemi seç, bekleyen hadisleri tek düğmeyle işle |
| `/proje/[projectId]/incele` | 3. adım, İncele: insan kararı bekleyen öneriler tek tek; ardından grafa yazma |
| `/proje/[projectId]/oku` | 4. adım, Zincirleri oku: hadis listesi, metin, zincirler, alıntılar, ravi görünümü |
| `/proje/[projectId]/gelismis` | Gelişmiş: şema düzenleyici, adım adım işlem, iş kuyruğu, ham graf |

`/proje/[projectId]` adresi, işi kalan ilk adıma yönlendirir. Proje sayfalarının ortak çerçevesi
(başlık, durum satırı, dört adımlı gösterge) `ProjectShell` bileşenidir; adım ekranları proje kaydına ve
sayılara `useProject()` ile ulaşır.

## Klasörler

```txt
src/app/                     yönlendirme; her sayfa tek bir ekran bileşenini çağırır
src/styles/                  tokens.css (tasarım değişkenleri), base, ui, layout, screens, advanced
src/shared/ui/               düğme, adım göstergesi, boş/hata/yükleniyor durumları, Arapça metin, sözlük
src/shared/api/              API adresi ve hata açıklamaları
src/modules/projects/        API katmanı (api.ts, types.ts), proje durumu, projeler ve proje çerçevesi
src/modules/ingestion/       metin yükleme ve girdi ayrıştırma
src/modules/runs/            zincir çıkarma; Gelişmiş altındaki adım adım işlem ve iş kuyruğu
src/modules/review/          inceleme ekranı, neden cümleleri, düzeltme formu, karar geçmişi, grafa yazma
src/modules/graph/           zincir okuma ve ravi görünümü; Gelişmiş altındaki ham graf
src/modules/schema-studio/   Gelişmiş altındaki şema düzenleyici
public/samples/              "Örnek hadislerle dene" düğmesinin yüklediği 10 hadis ve kaynak notu
docs/screens/                ekran görüntüleri
```

Sunucuyla konuşan tek yer `src/modules/projects/api.ts` dosyasıdır.

## Tasarım

Renk, boşluk, yazı ve köşe değerlerinin tamamı `src/styles/tokens.css` içindeki CSS değişkenleridir ve
giraffegraph.com ile aynı paleti kullanır: koyu uzay mavisi zeminler, tek vurgu rengi olarak bal
bronzu. Anlam renkleri her zaman bir sözcük ya da simgeyle birlikte kullanılır: turkuaz "tamamlandı",
sıcak ton "senin kararını bekliyor", arduvaz "nötr". Arayüz yazısı Inter, başlıklar Palatino ailesi,
Arapça metin Noto Naskh Arabic'tir (`next/font` ile derleme sırasında indirilir). Arapça metin her
yerde `ArabicText` bileşeniyle, `dir="rtl"` ve `lang="ar"` ile basılır.

## Bilinen sınırlar

- Proje kartlarındaki ve adım göstergesindeki sayılar istemcide hesaplanır: proje başına hadis listesi
  ve açık inceleme kuyruğu okunur (`src/modules/projects/status.ts`).
- Sunucuda hangi dil modelinin tanımlı olduğunu söyleyen bir uç yoktur. Panel bunu, var olmayan bir
  hadis kimliğiyle işleme isteği göndererek anlar; sunucu sağlayıcıyı önce denetlediği için tanımsız
  sağlayıcıda 422 döner ve hiçbir işlem başlamaz (`isExtractionProviderConfigured`).
- Grafa yazılan bilgi geri alınamaz, kullanıcı hesabı yoktur, inceleyen adı tarayıcıda saklanır ve
  doğrulanmaz.

## Geliştirme

```bash
npm ci
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
npm run build
```

`NEXT_PUBLIC_API_BASE_URL` verilmezse `http://localhost:8000` kullanılır. `next dev` ile `next build`
aynı `.next` klasörünü kullanır; biri çalışırken diğerini klasörün bir kopyasında çalıştır.
`npm run lint` için ESLint yapılandırması yoktur. Docker Compose ile çalıştırma adımları kök
[`README.md`](../README.md) dosyasındadır.
