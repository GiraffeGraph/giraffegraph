# Kaynak düzeni

- `app/`: yönlendirme. Sayfalar yalnızca ilgili modülün ekran bileşenini çağırır.
- `styles/`: tasarım değişkenleri (`tokens.css`) ve stil dosyaları; `app/globals.css` hepsini içe aktarır.
- `shared/ui/`, `shared/api/`, `shared/format.ts`: ekranların ortak kullandığı parçalar.
- `modules/projects/`: API katmanı, proje durumu, projeler sayfası, proje çerçevesi, Gelişmiş sayfası.
- `modules/ingestion/`: 1. adım, Metin yükle.
- `modules/runs/`: 2. adım, Zincirleri çıkar; Gelişmiş altındaki adım adım işlem ve iş kuyruğu.
- `modules/review/`: 3. adım, İncele.
- `modules/graph/`: 4. adım, Zincirleri oku; Gelişmiş altındaki ham graf.
- `modules/schema-studio/`: Gelişmiş altındaki şema düzenleyici.
- `modules/templates/`, `shared/hooks/`: boş yer tutucular.

Ekranların ve klasörlerin ayrıntısı [`../README.md`](../README.md) dosyasındadır.
