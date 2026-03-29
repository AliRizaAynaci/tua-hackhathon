# CLINotes - Ana Yönetmelik (The Charter)

## Proje: Personal Trainer

Bu dosya, projenin üst düzey yönetmeliği ve kurallarını içerir.

---

## 1. Proje Misyonu

Fitness tutkunları için kişiselleştirilmiş antrenman takip uygulaması.
- **Backend**: Go + SQLite/PostgreSQL
- **Mobile**: Flutter
- **AI**: Gemini API entegrasyonu

---

## 2. Mimari İlkeler

### Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────┐
│           Application                   │
│  ┌─────────────────────────────────┐   │
│  │         Domain Layer            │   │
│  │    (Entities, Business Rules)   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │         Port Layer              │   │
│  │    (Interfaces, Contracts)    │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │       Service Layer             │   │
│  │    (Use Cases, Orchestration)   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │       Adapter Layer             │   │
│  │ (Handlers, Repositories, Ext)   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Kural**: İç katmanlar dış katmanları bilmez.

---

## 3. Development Workflow

### Branch Strategy

```
main
├── feature/workout-logs
├── feature/ai-program
├── hotfix/critical-bug
└── refactor/performance
```

### Commit Convention

```
type(scope): description

[optional body]

[optional footer]
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Example**: `feat(workout): add exercise completion tracking`

---

## 4. Kalite Standartları

### Definition of Done

- [ ] Feature implemente edildi
- [ ] Unit test'ler yazıldı ve geçiyor
- [ ] Code review tamamlandı
- [ ] Dokümantasyon güncellendi
- [ ] Integration test'ler geçiyor
- [ ] Performance impact değerlendirildi

### Non-Functional Requirements

| Metric | Target |
|--------|--------|
| API Response (p95) | < 200ms |
| Mobile Launch | < 2s |
| Offline Support | Core features |
| Battery Usage | < 5%/hour |
| Crash Rate | < 0.1% |

---

## 5. Team Structure

Proje 3 ana rol ile yönetilir:

| Role | File | Focus |
|------|------|-------|
| Team Lead | `.claude/team/team_lead.md` | Strategy, Planning |
| Developer | `.claude/team/developer.md` | Code Quality |
| QA Engineer | `.claude/team/qa_engineer.md` | Testing, QA |

---

## 6. Güvenlik Kuralları
n
### Authentication
- Session-based auth (not JWT)
- Bcrypt password hashing
- Rate limiting on auth endpoints

### Data Protection
- API keys in environment variables
- SQL injection prevention (parameterized queries)
- XSS protection (output encoding)

---

## 7. Deployment

### Environment

| Env | Branch | Database |
|-----|--------|----------|
| Local | any | SQLite |
| Staging | develop | PostgreSQL |
| Production | main | PostgreSQL |

### Docker Services

```yaml
services:
  - app (Go API)
  - postgres (Database)
  - redis (Cache/Rate Limit)
  - kafka (Notifications)
```

---

## 8. Monitoring

### Logs
- Structured logging (Zap)
- Correlation IDs
- Request/Response logging

### Metrics
- Request latency
- Error rates
- Database query performance
- Mobile app crashes

---

## 9. Dokümantasyon

| Document | Location |
|----------|----------|
| API Spec | `ARCHITECTURE.md` |
| Load Test Results | `LOAD_TEST_RESULTS.md` |
| Project Overview | `PROJECT_OVERVIEW.md` |
| CLI Notes | `.claude/CLINotes.md` |
| Team Guidelines | `.claude/team/*.md` |

---

## 10. Emergency Contacts

**Project Root**: `/Users/ali/Desktop/personal-trainer-v2/`

**Key Commands**:
```bash
# Start services
docker-compose up -d

# Run tests
go test ./...           # Backend
flutter test            # Mobile

# Load test
go run scripts/comprehensive_bench.go
```

---

*Last Updated: 2026-03-23*
*Version: 2.0*
