# Agent Task State Template

## Task Information

```yaml
taskId: "TASK-XXX"
title: "Task title"
description: "Task description"
createdAt: "2024-01-01T00:00:00Z"
priority: "low|medium|high|critical"
```

## Current State

```yaml
currentState: "BACKLOG"
currentAgent: "product-manager"
startedAt: null
lastUpdated: "2024-01-01T00:00:00Z"
```

## State History

```yaml
history:
  - state: "BACKLOG"
    timestamp: "2024-01-01T00:00:00Z"
    agent: "user"
    notes: "Task created"
```

## Assignments

```yaml
assignments:
  analysis: "product-manager"
  planning: "team-lead"
  backend: null
  frontend: null
  devops: null
  qa: null
```

## Artifacts

```yaml
artifacts:
  analysis: null
  plan: null
  backendImpl: null
  frontendImpl: null
  devopsImpl: null
  review: null
  qaReport: null
```

## Dependencies

```yaml
dependencies:
  blocks: []      # This task blocks these tasks
  blockedBy: []   # This task is blocked by these tasks
```

## Completion Criteria

- [ ] Analysis complete
- [ ] Planning complete
- [ ] Implementation complete
- [ ] Review complete
- [ ] QA complete
- [ ] Approved

---

## Agent Notes

### Product Manager Notes
<!-- PM fills this during ANALYSIS -->

### Team Lead Notes
<!-- TL fills this during PLANNING -->

### Developer Notes
<!-- Dev fills this during IMPLEMENTATION -->

### QA Engineer Notes
<!-- QA fills this during QA -->
