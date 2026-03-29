# Developer - Saf Kod Yazımı

## Rol ve Sorumluluklar

Bu dosya, kod kalitesi ve implementasyon standartları için rehberdir.

### Kod Yazım Prensipleri

#### 1. Go (Backend)

```go
// ✅ DO: Açık ve anlaşılır fonksiyon isimleri
func CalculateTotalVolume(exercises []Exercise) float64

// ❌ DON'T: Kısaltmalar ve belirsiz isimler
func calcVol(exs []Ex) float64
```

**Standartlar:**
- `gofmt` ve `goimports` kullanımı zorunlu
- Interface'ler domain/port katmanında tanımlanır
- Error handling: explicit, no panic
- Context propagation her layer'da

#### 2. Dart/Flutter (Mobile)

```dart
// ✅ DO: Tip güvenliği ve null safety
Future<List<WorkoutTemplate>> fetchTemplates({required String userId})

// ❌ DON'T: Dynamic tipler ve implicit null
Future fetchTemplates(userId) async
```

**Standartlar:**
- Null safety strict mode
- Widget'lar `const` constructor ile
- State management: Provider/Riverpod
- Async/await kullanımı

### Dosya Organizasyonu

```
backend/
├── cmd/           # Entry points
├── internal/
│   ├── domain/    # Business logic, entities
│   ├── port/      # Interfaces
│   ├── service/   # Use cases
│   └── adapter/   # Implementations

mobile_app/lib/
├── models/        # Data classes
├── services/      # API clients
├── screens/       # UI pages
├── widgets/       # Reusable components
└── providers/     # State management
```

### Kod Review Checklist

- [ ] Fonksiyonlar tek sorumluluk prensibine uygun
- [ ] Hata durumları handle edilmiş
- [ ] Test yazılabilir yapıda
- [ ] Loglama uygun seviyede
- [ ] Dokümantasyon güncel

### Dependency Kuralları

1. **Backend**:
   - Domain → Port → Service → Adapter (içten dışa)
   - Dış katmanlar iç katmanları bilmez
   - Interface'ler üzerinden bağımlılık

2. **Mobile**:
   - Models → Services → Providers → UI
   - UI katmanı sadece provider'ı bilir
   - Service katmanı API detaylarını gizler

### Performans Optimizasyonları

| Alan | Strateji |
|------|----------|
| Database | N+1 query avoidance, eager loading |
| HTTP | Connection pooling, keep-alive |
| UI | Lazy loading, pagination |
| Memory | Resource disposal, streaming |
