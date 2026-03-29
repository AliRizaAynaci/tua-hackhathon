# QA Engineer - Test ve Hata Kontrolü

## Rol ve Sorumluluklar

Bu dosya, test stratejileri ve kalite güvence süreçleri için rehberdir.

## Test Piramidi

```
       /\
      /  \      E2E Tests (10%)
     /----\     Integration Tests (30%)
    /------\    Unit Tests (60%)
   /________\
```

### 1. Unit Tests

**Go:**
```go
func TestAuthService_Register(t *testing.T) {
    tests := []struct {
        name    string
        input   RegisterInput
        wantErr error
    }{
        {
            name:    "valid registration",
            input:   RegisterInput{Name: "John", Email: "john@test.com", Password: "secure123"},
            wantErr: nil,
        },
        {
            name:    "empty name",
            input:   RegisterInput{Name: "", Email: "test@test.com", Password: "pass"},
            wantErr: ErrValidation,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // Test implementation
        })
    }
}
```

**Flutter:**
```dart
group('WorkoutService', () {
  test('fetchTemplates returns list on success', () async {
    // Arrange
    final mockClient = MockHttpClient();

    // Act
    final result = await service.fetchTemplates();

    // Assert
    expect(result, isA<List<WorkoutTemplate>>());
  });
});
```

### 2. Integration Tests

- Database operations with test containers
- API endpoint testing
- Service-to-service communication

### 3. E2E Tests

- Critical user journeys
- Happy path ve error path
- Cross-platform mobile testing

## Test Kategorileri

| Kategori | Araç | Coverage |
|----------|------|----------|
| Unit | go test / flutter test | >80% |
| Integration | Docker Compose + test DB | Critical paths |
| E2E | Integration tests + UI | Core flows |
| Load | Custom bench scripts | Stress scenarios |

## Hata Yönetimi

### Severity Levels

- **Critical**: Sistem çökmesi, veri kaybı → Immediate fix
- **High**: Core feature çalışmıyor → Fix within 24h
- **Medium**: Workaround var → Fix within 1 week
- **Low**: UI polish, enhancements → Next sprint

### Reproduce Template

```markdown
## Bug Report

**Environment**: [dev/staging/prod]
**Version**: [commit hash]
**Steps to Reproduce**:
1. Step one
2. Step two

**Expected**:
**Actual**:
**Logs**:
**Screenshots**:
```

## Quality Gates

Pre-commit:
- [ ] Linting passes
- [ ] Unit tests pass
- [ ] Code coverage maintained

Pre-merge:
- [ ] Integration tests pass
- [ ] Code review approved
- [ ] Documentation updated

Pre-deploy:
- [ ] E2E tests pass
- [ ] Performance benchmarks met
- [ ] Security scan clean
