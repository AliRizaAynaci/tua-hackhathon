# Agent Orchestrator

Bu dosya, parallel agent'ların koordinasyonu için kullanılan rehberdir.

## 🎛️ Orchestrator Pattern

```
┌─────────────────┐
│   ORCHESTRATOR  │
│   (Claude Main) │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│  PM   │ │  TL   │ │  DEV  │ │  QA   │
│ Agent │ │ Agent │ │ Agent │ │ Agent │
└───────┘ └───────┘ └───────┘ └───────┘
    │         │        │        │
    └─────────┴────────┴────────┘
              │
              ▼
        ┌─────────────┐
        │  STATE FILE │
        │ (Single SSOT│
        └─────────────┘
```

## 🔄 Parallel Execution Flow

### Senaryo: Login Feature

```
Time →
─────────────────────────────────────────────────────────────►

User: "Login sistemi yap"
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 0: ANALYSIS                                           │
│ Agent: Product Manager                                      │
│ Duration: ~5-10 min                                         │
│ Output: acceptance-criteria.md, sub-tasks.json              │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: PLANNING                                           │
│ Agent: Team Lead                                            │
│ Duration: ~5-10 min                                         │
│ Output: technical-plan.md, risk-assessment.md               │
└─────────────────────────────────────────────────────────────┘
  │
  ├──────────────────────┬──────────────────────┐
  │                      │                      │
  ▼                      ▼                      ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Backend Dev │    │ Frontend Dev│    │  DevOps     │
│ (Parallel)  │    │ (Parallel)  │    │  (Later)    │
│             │    │             │    │             │
│ - JWT Auth  │    │ - Login UI  │    │ - CI/CD     │
│ - API       │    │ - Forms     │    │ - Deploy    │
└─────────────┘    └─────────────┘    └─────────────┘
  │                      │                      │
  └──────────────────────┴──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: REVIEW                                             │
│ Agent: Team Lead                                            │
│ Blocker: Tüm implementasyonlar tamamlanmalı                │
│ Output: review-report.md                                    │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: QA                                                 │
│ Agent: QA Engineer                                          │
│ Blocker: Review onaylanmalı                                │
│ Output: qa-report.md                                        │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: APPROVED/DONE                                      │
│ All agents complete                                         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Agent Çalıştırma Komutları

### 1. Single Agent (Sequential)

```bash
# Product Manager çalıştır
claude agent:run product-manager --task=TASK-001

# State'i otomatik ilerlet
claude agent:next TASK-001
```

### 2. Parallel Agents

```bash
# Aynı anda birden fazla developer çalıştır
claude agent:run parallel \
  --agents=backend-developer,frontend-developer \
  --task=TASK-001

# State: IMPLEMENTATION
# Her developer bağımsız çalışır
```

### 3. Dependency Chain

```bash
# Review başlamadan önce tüm implementasyonlar bitmeli
claude agent:wait-for TASK-001 --state=IMPLEMENTATION --all-agents

# Sonra Team Lead review başlat
claude agent:run team-lead --task=TASK-001 --phase=review
```

## 📊 State Machine Guardrails

```javascript
// State transition validation
const validTransitions = {
  'BACKLOG': ['ANALYSIS'],
  'ANALYSIS': ['PLANNING'],
  'PLANNING': ['IMPLEMENTATION'],
  'IMPLEMENTATION': ['REVIEW'],
  'REVIEW': ['QA', 'CHANGES_REQUESTED'],
  'QA': ['APPROVED', 'CHANGES_REQUESTED'],
  'CHANGES_REQUESTED': ['IMPLEMENTATION'],
  'APPROVED': ['DONE'],
  'DONE': []
};

// Blocker check
function canTransition(task, fromState, toState) {
  // Check if all assigned agents completed current phase
  const agents = getAssignedAgents(task, fromState);
  const allComplete = agents.every(agent =>
    agent.status === 'COMPLETED'
  );

  return allComplete && validTransitions[fromState].includes(toState);
}
```

## 🔄 Handoff Protocol

### Agent A → Agent B

```yaml
# Step 1: Agent A completes work
currentAgent: "backend-developer"
currentState: "IMPLEMENTATION"
status: "COMPLETED"
output:
  files_modified:
    - "src/auth/login.go"
    - "src/auth/jwt.go"
  tests_passed: true
  notes: "JWT auth implemented, tests passing"

# Step 2: Update state file
lastUpdated: "2024-03-24T12:00:00Z"
history:
  - state: "IMPLEMENTATION"
    agent: "backend-developer"
    timestamp: "2024-03-24T12:00:00Z"
    status: "COMPLETED"

# Step 3: Check if ready for next phase
assignments:
  backend: { status: "COMPLETED" }
  frontend: { status: "COMPLETED" }

# All implementation done → Move to REVIEW
currentState: "REVIEW"
currentAgent: "team-lead"

# Step 4: Notify next agent (via state change)
```

## 🧪 Example: Complete Task Flow

### Task: Add Exercise Logging

**Phase 0 - Product Manager:**
```markdown
## Task Analysis: Add Exercise Logging

### User Story
As a user, I want to log my exercises with sets/reps/weight
so that I can track my progress over time.

### Acceptance Criteria
- [ ] User can select exercise from list
- [ ] User can add multiple sets with reps/weight
- [ ] Logs are saved to backend
- [ ] User can view history

### Sub-tasks
1. [BACKEND] Exercise API endpoints
2. [BACKEND] Database schema for logs
3. [FRONTEND] Exercise logging UI
4. [FRONTEND] History view
5. [DEVOPS] Deploy updates

### Priority: High
```

**Phase 1 - Team Lead:**
```markdown
## Implementation Plan

### Architecture
- REST API: POST /api/exercises/:id/log
- Database: exercise_logs table
- Frontend: ExerciseLogForm component

### Parallel Assignments
- Backend Dev: Tasks 1, 2
- Frontend Dev: Tasks 3, 4
- DevOps: Task 5 (wait for merge)

### Dependencies
- Backend API → Frontend integration
- Both → DevOps deploy

### Risk: Medium
- Exercise list sync (cached vs live)
```

**Phase 2 - Parallel Implementation:**

```
Time →
Backend Dev:    [====API====][==Schema==][=Tests=]
                      │              │
Frontend Dev:   [====UI====][==Forms==][=History=]
                      │              │
                      └──────┬───────┘
                             ▼
                      [Integration]
```

**Phase 3 - Review (Team Lead):**
```markdown
## Review Report

### Backend ✅
- Clean architecture, follows patterns
- Tests adequate
- Minor: Add index on user_id column

### Frontend ✅
- Component structure good
- State management clean
- Suggestion: Add loading states

### Overall: APPROVED with minor notes
```

**Phase 4 - QA:**
```markdown
## QA Report

### Security ✅
- Input validation present
- Auth checks in place

### Edge Cases ⚠️
- Very long exercise names (>100 char) - handled
- Duplicate set entries - need check

### Coverage
- Unit: 85% ✅
- Integration: 70% ⚠️ (add more API tests)

### Status: APPROVED with notes
```

## 🛠️ Orchestrator Commands

```bash
# Task durumunu kontrol et
claude agent:status TASK-001

# Tüm task'leri listele
claude agent:list --all

# Belirli state'teki task'ler
claude agent:list --state=IMPLEMENTATION

# Agent loglarını gör
claude agent:logs TASK-001 --agent=backend-developer

# State'i manuel ilerlet (force - use carefully)
claude agent:advance TASK-001 --to=REVIEW

# Task'leri temizle
claude agent:cleanup --completed-before="7d"
```

## 📝 Notes

- **Orchestrator = Main Claude**: Agent çağrılarını yöneten ana instance
- **Her agent bağımsız**: Agent'lar birbirini beklemez (state file sync)
- **Review sequential**: Tüm impl → Review → QA sıralı
- **State file SSOT**: Tek kaynak task state dosyası
