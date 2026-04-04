# Story Template v1

Bu belge, ilk domain template olan `Story / Series / Film` icin minimum baslangic setini tanimlar.

## Hedef

Ilk template fazla genis olmamali. Generic engine'i zorlamadan ilk ucgeni kurmali:

- Structure
- Character
- Event

## Minimum Node Types

### Series

Koken eser veya ana universum.

### Season

Dizi odakli ise kullanilir. Film projesinde opsiyoneldir.

### Episode

Story template'te bir SourceUnit turu.

### Scene

Episode altindaki anlamli anlatim birimi.

### Character

Merkezi varlik tipi.

### Event

Hikaye icindeki izlenebilir olay.

### Location

Mekan bilgisi.

### Organization

Aile, ekip, kurum, faction gibi grup yapilari.

## Minimum Relation Types

### HAS_SEASON

`Series -> Season`

### HAS_EPISODE

`Season -> Episode`

### HAS_SCENE

`Episode -> Scene`

### APPEARS_IN

`Character -> Episode/Scene`

### OCCURS_IN

`Event -> Episode/Scene`

### INVOLVED_IN

`Character -> Event`

### PART_OF

`Character -> Organization`

### RELATED_TO

`Character -> Character`

Not:

`RELATED_TO` ilk fazda generic relation olabilir. Daha sonra `ALLY_OF`, `ENEMY_OF`, `LOVES`, `BETRAYS` gibi tipler schema studio veya AI suggestion katmanindan gelebilir.

## Ilk Fazda Ozel Tutulmayan Alanlar

Asagidaki kavramlar ilk template'te sabitlenmez, schema studio'dan gelir:

- Secret
- Goal
- Conflict
- Debt
- Bloodline
- Alliance
- Betrayal

Bu karar, generic cekirdegi story domain'ine erken kilitlememek icin alinir.
