# 系统状态索引示例（System State Index Example）

Last updated: 2026-03-23
Status: active-draft

## 用途（Purpose）

为当前 system-state 栈提供一份统一索引。

Provide one index for the current system-state stack.

当你需要快速找到以下内容时，先看这份索引：
- governance truth（治理事实层）
- current-state truth（当前态事实层）
- drift status（漂移状态）
- retrieval policy（检索策略）
- health/consistency state（健康/一致性状态）
- maintenance workflow（维护流程）

Use this file when you need to quickly find:
- governance truth
- current-state truth
- drift status
- retrieval policy
- health/consistency state
- maintenance workflow

---

## 1. 治理 / 规则正典（Governance / Rule Canon）

Read first for:
- role boundaries
- approval requirements
- dangerous-action restrictions
- formal routing behavior

Files:
- `AGENTS.md`
- `docs/multi-agent-routing.md`
- `docs/source-of-truth-layering.md`

---

## 2. 当前态入口层（Current-State Entrypoints）

Read first for:
- what is true now
- current runtime / current health / current consistency

Files:
- `docs/current-state-entrypoints-v1.md`
- `docs/runtime-state-snapshot-2026-03-23.md`
- `memory/health/current-health.md`

---

## 3. 漂移 / 可靠性诊断（Drift / Reliability Diagnostics）

Read first for:
- known drift zones
- retrieval reliability diagnosis
- explanation-layer trust level

Files:
- `docs/drift-checklist.md`
- `docs/retrieval-diagnosis.md`
- `docs/explanation-layer-status.md`

---

## 4. 当前检索策略（Current Retrieval Policy）

Read first for:
- how to answer different question classes right now
- when bridge-first retrieval should override older structured memory

Files:
- `docs/retrieval-policy-current.md`
- `memory/SEARCH_STATE.md`
- `memory/SYSTEM_OVERVIEW.md`

---

## 5. 维护流程（Maintenance Workflow）

Read first for:
- what must remain fresh
- which docs are live vs historical
- whether the current stabilization cycle is complete enough to stop expanding

Files:
- `docs/freshness-discipline.md`
- `docs/working-set.md`
- `docs/completion-criteria.md`
