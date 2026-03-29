# Task Lifecycle Workflow

## State Machine

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   BACKLOG   │───▶│  ANALYSIS   │───▶│   PLANNING  │
│  (New Task) │    │  (Product   │    │  (Team Lead)│
│             │    │   Manager)  │    │             │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                              ┌──────────────┼──────────────┐
                              ▼              ▼              ▼
                        ┌─────────┐    ┌─────────┐    ┌─────────┐
                        │ BACKEND │    │ FRONTEND│    │ DEVOPS  │
                        │ (Dev)   │    │  (Dev)  │    │  (Dev)  │
                        └────┬────┘    └────┬────┘    └────┬────┘
                             │              │              │
                             └──────────────┼──────────────┘
                                            ▼
                                      ┌─────────────┐
                                      │   REVIEW    │
                                      │ (Team Lead) │
                                      └──────┬──────┘
                                             │
                                             ▼
                                      ┌─────────────┐
                                      │    QA       │
                                      │  (QA Eng)   │
                                      └──────┬──────┘
                                             │
                              ┌──────────────┴──────────────┐
                              ▼                             ▼
                       ┌─────────────┐               ┌─────────────┐
                       │   CHANGES   │◀──────────────│  APPROVED   │
                       │  REQUESTED  │               │             │
                       └─────────────┘               └──────┬──────┘
                                                            │
                                                            ▼
                                                     ┌─────────────┐
                                                     │   DONE      │
                                                     │  (Complete) │
                                                     └─────────────┘
```

## State Definitions

| State | Owner | Description | Next States |
|-------|-------|-------------|-------------|
| `BACKLOG` | User | Yeni task, henüz analiz edilmemiş | ANALYSIS |
| `ANALYSIS` | Product Manager | Requirements, acceptance criteria belirleniyor | PLANNING |
| `PLANNING` | Team Lead | Technical plan, architecture decisions | IMPLEMENTATION |
| `IMPLEMENTATION` | Developer | Kod yazılıyor | REVIEW |
| `REVIEW` | Team Lead | Technical review, code quality | QA or CHANGES_REQUESTED |
| `QA` | QA Engineer | Final review, security, edge cases | APPROVED or CHANGES_REQUESTED |
| `CHANGES_REQUESTED` | Developer | Revize ediliyor | REVIEW |
| `APPROVED` | QA Engineer | Onaylandı, merge edilebilir | DONE |
| `DONE` | - | Task tamamlandı | - |

## Parallel Execution Rules

1. **Independent Tasks**: Farklı task'ler aynı anda farklı state'lerde olabilir
2. **Blocking**: Bir task'in QA'ya geçmesi için önce Review'dan geçmesi gerekir
3. **Multiple Developers**: Backend ve Frontend developer'ları aynı task üzerinde parallel çalışabilir

## State File Format

```json
{
  "taskId": "TASK-001",
  "title": "Feature name",
  "currentState": "IMPLEMENTATION",
  "currentAgent": "backend-developer",
  "history": [
    {"state": "BACKLOG", "timestamp": "2024-01-01T10:00:00Z"},
    {"state": "ANALYSIS", "timestamp": "2024-01-01T10:30:00Z", "agent": "product-manager"},
    {"state": "PLANNING", "timestamp": "2024-01-01T11:00:00Z", "agent": "team-lead"},
    {"state": "IMPLEMENTATION", "timestamp": "2024-01-01T12:00:00Z", "agent": "backend-developer"}
  ],
  "dependencies": ["TASK-000"],
  "assignedAgents": ["backend-developer", "frontend-developer"],
  "artifacts": {
    "analysis": ".claude/state/TASK-001/analysis.md",
    "plan": ".claude/state/TASK-001/plan.md",
    "implementation": ".claude/state/TASK-001/impl.md",
    "review": ".claude/state/TASK-001/review.md",
    "qa": ".claude/state/TASK-001/qa.md"
  }
}
```

## Agent Handoff Protocol

1. **Current Agent completes work**
2. **Update state file** with results
3. **Set next state** and agent
4. **Notify next agent** (via state change)
5. **Next agent picks up** from state file

## Commands

```bash
# Create new task
claude agent:new-task "Task description"

# Check task status
claude agent:status TASK-001

# Trigger next agent
claude agent:handoff TASK-001

# List active tasks
claude agent:list --state=IMPLEMENTATION
```
