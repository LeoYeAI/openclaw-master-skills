---
name: tonic-system-deploy
description: >
  Software deployment workflow for systems with separate UAT and PROD environments.
  Use when: planning a bug fix deployment, choosing between Flow 1 (UAT-first) and
  Flow 2 (PROD-first), handling emergency hotfixes, executing rollbacks, or designing
  automated nightly deploy pipelines. Covers approval gates, human checkpoints,
  system automation nodes, Telegram notifications, and rollback procedures.
---

# tonic-system-deploy

Software Deployment Workflow — Dual-Environment (UAT + PROD)

---

## Background & Design Rationale

This skill was designed for systems where:

- **Two live environments co-exist**: UAT (testing/staging) and PROD (production)
- **Versions can diverge**: UAT may be ahead of PROD by several releases
- **Deployments are nightly**: automated pipelines run at scheduled times
- **Human approval is mandatory**: no code goes to PROD without explicit admin sign-off
- **Bugs require structured triage**: severity, origin environment, and version state all affect the deploy path

The key insight: **choosing the wrong deploy flow when versions are mismatched can introduce regressions**. Flow 1 assumes parity; Flow 2 handles divergence safely.

---

## Prerequisites — Before Choosing a Flow

### Step 0: Version Check (always do this first)

| Question | Answer → |
|----------|----------|
| Are UAT and PROD on the same version? | → **Flow 1** |
| Is UAT ahead of PROD by any version? | → **Flow 2** |
| Is this a critical/high severity bug? | → **Emergency Hotfix** (bypass pipeline) |
| Do you need to undo a bad deploy? | → **Rollback** |

### Version Mismatch Decision Tree

```
Bug found
    │
    ├─ severity = critical/high?
    │       └─ YES → Emergency Hotfix (skip pipeline)
    │
    ├─ UAT version == PROD version?
    │       └─ YES → Flow 1
    │
    └─ UAT version > PROD version?
            └─ YES → Flow 2
```

---

## Flow 1 — UAT-First (Versions Aligned)

**Scenario**: Bug found in UAT or PROD when both environments run the same version.
**Goal**: Fix → validate in UAT → promote to PROD.
**Result**: UAT and PROD converge to same patched version.

### Timeline

```
Bug reported
    │
    │ 🧑 HUMAN: Admin reviews + confirms bug (status: confirmed)
    ▼
[confirmed] — severity: low/medium only
    │
    │ 🤖 SYSTEM: Scheduled deploy time T1 (e.g. 20:00)
    │   - AI analyses root cause + records fix plan
    │   - Deploys fix to UAT environment
    │   - Status → deployed_uat
    ▼
[deployed_uat]
    │ 📲 Telegram: "Fix deployed to UAT. Please validate."
    │
    │ 🧑 HUMAN: Admin logs into UAT, validates fix
    │   - Runs through affected workflows
    │   - Confirms no regression
    │   - Clicks "Approve PROD Deploy" → status: pending_prod
    ▼
[pending_prod]
    │ 📲 Telegram: "Queued for PROD at T2."
    │
    │ 🤖 SYSTEM: Scheduled deploy time T2 (e.g. 22:00)
    │   - Deploys fix to PROD environment
    │   - Status → deployed_prod
    ▼
[deployed_prod] ✅ Flow 1 Complete
    │ 📲 Telegram: "Deployed to PROD. Flow 1 complete."
```

### Human Checkpoints (Flow 1)

| Checkpoint | Who | Action | Gate Condition |
|------------|-----|--------|----------------|
| Confirm bug | Admin/Manager | Mark as confirmed | Bug is reproducible and valid |
| UAT validation | Admin/Manager | Click "Approve PROD Deploy" | Fix works, no regression in UAT |

### Automation Nodes (Flow 1)

| Time | Node | Input Status | Output Status | Action |
|------|------|-------------|---------------|--------|
| T1 | Phase 1 | confirmed/planned | deployed_uat | AI analysis + UAT deploy |
| T2 | Phase 2 | pending_prod | deployed_prod | PROD deploy |

---

## Flow 2 — PROD-First (Versions Misaligned)

**Scenario**: Bug found in PROD when UAT is ahead by one or more versions.
**Why not Flow 1?** Validating a PROD fix in a newer UAT environment risks false confidence — the fix may behave differently on the older PROD codebase.
**Goal**: Fix PROD directly → validate in PROD → cherry-pick back to UAT.
**Result**: PROD gets the fix immediately; UAT gets it merged back after PROD validation.

### Timeline

```
Bug found in PROD (UAT is ahead)
    │
    │ 🧑 HUMAN: Admin reviews + confirms bug
    │   - Selects: found_in_env = prod, fix_flow = flow2
    │   - Status → confirmed
    ▼
[confirmed]
    │
    │ 🤖 SYSTEM: Scheduled deploy time T1 (e.g. 20:00)
    │   - AI analyses root cause + records fix plan
    │   - Skips UAT entirely
    │   - Queues for PROD deploy → status: pending_prod
    ▼
[pending_prod]
    │ 📲 Telegram: "PROD deploy queued for T2 (Flow 2)."
    │
    │ 🤖 SYSTEM: Scheduled deploy time T2 (e.g. 22:00)
    │   - Deploys fix to PROD
    │   - Status → deployed_prod
    ▼
[deployed_prod]
    │ 📲 Telegram: "Deployed to PROD. Please validate PROD. Approve UAT merge when ready."
    │
    │ 🧑 HUMAN: Admin validates fix in PROD
    │   - Confirms fix works on production data/config
    │   - No regression in PROD workflows
    │   - Clicks "Approve Merge UAT" → status: pending_uat_merge
    ▼
[pending_uat_merge]
    │ 📲 Telegram: "UAT merge queued for T2 tonight."
    │
    │ 🤖 SYSTEM: Next T2 cycle (22:00)
    │   - Deploys/merges fix into UAT environment
    │   - Status → uat_merged
    ▼
[uat_merged] ✅ Flow 2 Complete
    │ 📲 Telegram: "Merged to UAT. Flow 2 complete."
```

### Human Checkpoints (Flow 2)

| Checkpoint | Who | Action | Gate Condition |
|------------|-----|--------|----------------|
| Confirm bug | Admin/Manager | Mark as confirmed + select flow2 | Bug confirmed in PROD, version mismatch verified |
| PROD validation | Admin/Manager | Click "Approve Merge UAT" | Fix verified in PROD, no regression |

### Automation Nodes (Flow 2)

| Time | Node | Input Status | Output Status | Action |
|------|------|-------------|---------------|--------|
| T1 | Phase 1 | confirmed/planned | pending_prod | AI analysis (skip UAT) |
| T2 | Phase 2a | pending_prod | deployed_prod | PROD deploy |
| T2 (next) | Phase 2b | pending_uat_merge | uat_merged | UAT deploy/merge |

### Flow 2 Important Note

> **T2 deadline matters.** If admin approves UAT merge before T2 on the same day, the merge runs that night. If approved after T2, it runs the following night's T2. Always communicate the cutoff time to the team.

---

## Status Reference

| Status | Flow | Colour | Meaning | Next Action |
|--------|------|--------|---------|-------------|
| `submitted` | Both | Grey | Bug reported, awaiting review | Admin confirms/rejects |
| `confirmed` | Both | Blue | Valid bug, enters pipeline | T1 auto-process |
| `analyzing` | Both | Purple | AI analysis running (transient) | Auto → planned |
| `planned` | Both | Indigo | AI fix plan recorded | T1 auto-deploy |
| `deployed_uat` | Flow 1 | Cyan | UAT deployed, awaiting human validation | Admin approves PROD |
| `pending_prod` | Both | Yellow | Queued for PROD at next T2 | T2 auto-deploy |
| `deployed_prod` | Both | Green | PROD deployed | Flow1: done; Flow2: admin approves UAT merge |
| `pending_uat_merge` | Flow 2 | Purple | Queued for UAT merge at next T2 | T2 auto-merge |
| `uat_merged` | Flow 2 | Teal | UAT updated with PROD fix | Flow 2 complete ✅ |
| `closed` | Both | Emerald | Manually closed | — |
| `rejected` | Both | Red | Not a valid bug | — |

---

## Severity Rules

| Severity | Pipeline Eligible? | Notes |
|----------|--------------------|-------|
| `low` | ✅ Yes | Both flows |
| `medium` | ✅ Yes | Both flows |
| `high` | ❌ No | Emergency Hotfix only |
| `critical` | ❌ No | Emergency Hotfix, immediate escalation |

> Never let high/critical bugs wait for a scheduled pipeline. Treat them as emergency hotfixes.

---

## Emergency Hotfix (Bypass Pipeline)

**Scenario**: Critical or high severity bug in PROD. Cannot wait for scheduled T1/T2.

### Process

```
Critical bug found in PROD
    │
    │ 🧑 HUMAN: Admin confirms severity = critical/high
    │   - Does NOT enter pipeline (no confirmed status)
    │   - Opens direct hotfix branch
    ▼
Fix developed (manually or with AI assist)
    │
    │ 🧑 HUMAN: Admin deploys directly to PROD
    │   - Updates bug status to deployed_prod manually
    │   - Records fix details in ai_fix_diff field
    ▼
[deployed_prod] (manual)
    │ 📲 Telegram: "Emergency hotfix deployed to PROD. [Bug title]"
    │
    │ 🧑 HUMAN: Validates PROD immediately
    │
    └─ If UAT is ahead → manually cherry-pick to UAT branch
       If UAT is same version → update UAT as well
    ▼
✅ Emergency resolved
```

### Checklist for Emergency Hotfix

- [ ] Severity confirmed as critical/high before bypassing pipeline
- [ ] At least one other team member notified before deploy
- [ ] Fix deployed and validated within agreed SLA (e.g. P1: 1 hour, P2: 4 hours)
- [ ] Post-deploy smoke test completed (login, core workflow, affected feature)
- [ ] Bug status updated manually in system
- [ ] Telegram/Slack notification sent to stakeholders
- [ ] Post-incident note added to bug record (root cause, fix summary)
- [ ] UAT updated (cherry-pick or re-sync if needed)
- [ ] Incident review scheduled (within 48h for P1)

---

## Rollback Procedure

**Scenario**: A deploy (T1 or T2) introduces a regression or new failure.

### Decision: When to Rollback

```
Issue detected after deploy
    │
    ├─ Severity: minor UX glitch → Monitor, schedule fix in next pipeline
    │
    ├─ Severity: functional regression → Rollback immediately
    │
    └─ Severity: data corruption risk → Rollback + escalate + engage DBA
```

### Rollback Process

```
Regression detected post-deploy
    │
    │ 🧑 HUMAN: Admin confirms rollback needed
    │   - Record: what was deployed, when, what broke
    ▼
    │ 🤖 SYSTEM or 🧑 HUMAN: Execute rollback
    │   - Docker: docker compose down && git checkout <prev_tag> && docker compose up
    │   - DB migration: apply down migration if schema changed
    │   - Status of affected bugs → revert to previous status
    ▼
    │ 📲 Telegram: "Rollback executed for [version]. Monitoring."
    │
    │ 🧑 HUMAN: Post-rollback validation (5–10 min smoke test)
    │
    └─ Stable → document in HISTORY + schedule proper fix
       Unstable → escalate
```

### Rollback Checklist

- [ ] Previous working commit/tag identified (git log)
- [ ] Rollback scope defined (frontend / backend / both / DB)
- [ ] Affected bug statuses reverted in system
- [ ] Smoke test completed after rollback
- [ ] Root cause of regression documented
- [ ] Team + stakeholders notified
- [ ] Fix plan for the reverted change recorded

---

## Scheduled Deploy Times (Reference Only)

> ⚠️ These times are project-specific. Adapt per project SLA and business hours.

| Slot | Name | Phase | Typical Window |
|------|------|-------|----------------|
| T1 | UAT/PROD-queue Deploy | Phase 1 | Off-peak evening (e.g. 20:00) |
| T2 | PROD/UAT-merge Deploy | Phase 2 | Late evening (e.g. 22:00) |

**Principles for choosing T1/T2:**
- T1 and T2 must have enough gap for human validation (minimum 1–2 hours)
- Both should be outside business hours unless urgency demands otherwise
- For 24/7 systems: choose lowest traffic window (check metrics)
- Emergency hotfix: no scheduled time — deploy ASAP after approval

---

## Telegram Notification Templates

Use these as the standard message format for each pipeline node.

### T1 Complete — Flow 1 (UAT deployed)
```
🔧 Bug Fix Pipeline — Flow 1 已部署 UAT

• #<id> [<severity>] <title>
• ...

📦 Release: <version>

✅ 請驗收 UAT：<UAT_URL>
確認後請點「批准推 PROD」。
下次 T2 時間：<T2_time>
```

### T2 Complete — Flow 1 (PROD deployed)
```
🚀 Bug Fix Pipeline — Flow 1 已部署 PROD

• #<id> [<severity>] <title>

✅ Flow 1 完成。UAT 與 PROD 版本已對齊。
```

### T1 Complete — Flow 2 (PROD queued)
```
🔧 Bug Fix Pipeline — Flow 2 已排隊部署 PROD

• #<id> [<severity>] <title>

⏳ 今晚 T2（<T2_time>）自動部署至 PROD。
部署後請驗收，確認後點「批准 Merge UAT」。
```

### T2 Complete — Flow 2 (PROD deployed, UAT pending)
```
🚀 Bug Fix Pipeline — Flow 2 已部署 PROD

• #<id> [<severity>] <title>

⚠️ 請登入 PROD 驗收。
確認正常後點「批准 Merge UAT」。
下次 T2 時間：<T2_time>
```

### T2 Complete — Flow 2 (UAT merged)
```
✅ Bug Fix Pipeline — Flow 2 完成

• #<id> [<severity>] <title>

🎉 Fix 已同步至 UAT。Flow 2 全流程完成。
```

### Emergency Hotfix
```
🚨 Emergency Hotfix — <PROD/UAT>

Bug: #<id> [<severity>] <title>
時間：<datetime>
部署人：<admin>

狀態：已部署，請立即驗收
需要跟進：<yes/no — UAT cherry-pick needed>
```

### Rollback
```
⚠️ Rollback 執行 — <environment>

原因：<brief reason>
回滾至：<version/commit>
時間：<datetime>
執行人：<admin>

狀態：已回滾，正在監控
下一步：<scheduled fix / investigation>
```

---

## Adapting This Workflow to a New Project

When setting up a new project with this workflow:

1. **Define T1 and T2** — pick times based on traffic patterns and SLA
2. **Set severity policy** — confirm which severities enter pipeline vs emergency hotfix
3. **Configure Telegram/notification channels** — who receives which notifications
4. **Add DB columns** — `fix_flow`, `found_in_env`, and status enum (see Status Reference)
5. **Implement Phase 1 + Phase 2 cron jobs** — schedule at T1 and T2
6. **Add approval endpoints** — `approve-prod`, `approve-uat-merge`, batch variants
7. **Add status badges + action buttons** — frontend must reflect all statuses clearly
8. **Test the full cycle in UAT first** — simulate a bug through both flows before going live
9. **Document rollback steps** — specific to the project's tech stack and DB

---

## Pre-Deploy Checklist (T1 / T2)

Run before every scheduled deploy window.

- [ ] **DB backup confirmed** — last backup < 24h, or trigger manual backup now
- [ ] **Monitoring alerts active** — error rate, response time, queue depth dashboards open
- [ ] **On-call admin reachable** — someone available to respond within 15 min post-deploy
- [ ] **Change freeze check** — not within a freeze window (see Change Freeze Policy)
- [ ] **Rollback path clear** — previous working commit/tag identified and noted
- [ ] **Dependent services healthy** — upstream/downstream APIs, DBs, message queues OK
- [ ] **Disk + memory OK** — server has headroom (>20% free disk, <80% memory)

---

## Post-Deploy Monitoring

After each T1 or T2 deploy, monitor for a minimum of **10 minutes** before standing down.

### Metrics to Watch

| Metric | Healthy Threshold | Action if Breached |
|--------|------------------|--------------------|
| HTTP 5xx error rate | < 0.5% | Investigate immediately, consider rollback |
| API response time (p95) | < baseline + 20% | Check DB queries, cache hit rate |
| Memory usage | < 85% | Check for memory leaks in new code |
| CPU usage | < 80% sustained | Check for infinite loops or expensive queries |
| Login / auth success rate | > 99% | Auth regression — rollback candidate |
| Key business flow (e.g. task create) | Working end-to-end | Smoke test immediately post-deploy |

### Smoke Test Sequence (2–3 min)

1. Login with admin account
2. Navigate to the affected feature
3. Perform the action that triggered the bug
4. Confirm fix is working
5. Check 2–3 adjacent features for regression
6. Check system logs for new errors

> If any smoke test step fails → **rollback immediately**, do not wait.

---

## Multi-Service Deploy (Cross-Service Fixes)

**Scenario**: A bug fix requires changes to more than one service (e.g. backend API + frontend, or service A + service B).

### Deploy Order Principle

```
Always deploy in dependency order:
  Backend (API) first → Frontend second
  Shared library → Dependent services
  DB migration → Application code

Never deploy in reverse order — it risks breaking in-flight requests.
```

### Coordination Steps

1. **Map dependencies** — list all services affected and their dependency order
2. **Stage the deploys** — do not deploy all services simultaneously
3. **Validate between services** — after each service deploy, quick health check before next
4. **Single rollback plan** — define the exact reverse order and what to check at each step
5. **Lock window** — communicate to team that a multi-service deploy is in progress (no other deploys)

### Status Tracking for Multi-Service

Tag the bug with affected services. Use release notes to list which service each fix applies to:
```
[backend] Fix: null pointer in task update handler
[frontend] Fix: error boundary not catching API timeout
```

---

## Change Freeze Policy

Certain periods should have **no scheduled pipeline deploys** (T1/T2 suspended). Emergency hotfixes may still be approved by escalation.

### Recommended Freeze Windows

| Period | Recommended Action |
|--------|--------------------|
| Public holidays | Suspend T1/T2. Emergency hotfix requires 2-person approval. |
| Lunar New Year (3 days) | Full freeze. P1 only with CTO sign-off. |
| Major client go-live week | Freeze for that client's system. Other systems normal. |
| End-of-month financial close | Freeze financial modules. Other modules normal. |
| Planned system maintenance | Coordinate freeze window in advance, notify stakeholders. |

### Declaring a Freeze

1. Update HEARTBEAT.md or project config with freeze start/end dates
2. Notify team via Telegram/channel
3. Pipeline cron jobs remain scheduled but agent checks freeze flag before executing
4. Emergency hotfix during freeze: requires explicit approval from admin + one other senior (two-person rule)

### Freeze Flag (implementation)

In pipeline config or environment variable:
```
DEPLOY_FREEZE=true              # hard freeze, all deploys blocked
DEPLOY_FREEZE_MODULES=financial # module-specific freeze
DEPLOY_FREEZE_UNTIL=2026-02-05  # auto-lift date
```

---

## Quick Reference Card

```
FLOW SELECTION:
  Same version?  → Flow 1
  UAT ahead?     → Flow 2
  Critical/High? → Emergency Hotfix
  Freeze window? → Block (escalate for emergency)

FLOW 1: confirmed → [T1] deployed_uat → [human] pending_prod → [T2] deployed_prod ✅
FLOW 2: confirmed → [T1] pending_prod → [T2] deployed_prod → [human] pending_uat_merge → [T2] uat_merged ✅

ROLLBACK: detect → confirm → execute → validate → document

SEVERITY:
  low/medium  → pipeline eligible
  high/critical → emergency hotfix only

MULTI-SERVICE: backend first → validate → frontend → validate

PRE-DEPLOY: backup ✓ monitoring ✓ on-call ✓ freeze-check ✓ rollback-path ✓
POST-DEPLOY: monitor 10min → smoke test → stand down
```
