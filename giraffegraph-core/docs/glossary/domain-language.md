# Domain Language

Bu sozluk ekipte ayni kelimeleri ayni anlamla kullanmak icin tutulur.

## Generic Core Terms

### SourceUnit

Sisteme verilen ham veri birimi.

Ornek:

- Episode transcript
- Script file
- Research paper

### Segment

SourceUnit'in islenebilir alt parcasi.

### ProcessingRun

Belirli bir pipeline ve schema ile SourceUnit uzerinde calisan tekil islem kaydi.

### Candidate

Extraction tarafinda uretilen, ama henuz canonical olmayan node veya relation adayi.

### Canonical Graph

Urunun gercek source of truth graph katmani.

### GraphDelta

Bir run'in graph uzerinde yarattigi degisiklik paketi.

### Schema

Node tipleri, relation tipleri, property alanlari, validation kurallari ve extraction hint'lerini kapsayan veri modeli.

### DomainTemplate

Belirli bir domain icin hazir schema ve pipeline paketi.

## Story Domain Terms

### Episode

Story template'te bir SourceUnit turu.

### Scene

Story template'te bir Segment veya Segment group'u.

### Character

Story graph'ta sahsiyet veya fail varlik.

### Event

Hikaye icinde graph'ta izlenen anlamli olay.

### RelationshipChange

Iki varlik arasindaki durum degisimi.
