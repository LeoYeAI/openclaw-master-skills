---
name: cr-commit-check
description: 【Code Review 子 Agent · 门控一】校验本迭代所有 commit 是否符合 Conventional Commits 规范及项目可追溯性格式。输入 git log 片段和项目元数据，输出结构化校验报告并以 STATUS=OK|FAIL 结尾。由 spec-driven-dev 的 code_review 阶段自动调用，不建议单独触发。
user-invocable: false
metadata: {"openclaw": {"emoji": "📝", "requires": {"bins": ["git"]}, "calledBy": ["spec-driven-dev"]}}
---

# cr-commit-check

Code Review 流水线的**第一道门控**：Commit Message 合规校验子 Agent。
由 `spec-driven-dev` 的 `code_review` 阶段作为 Sub-Agent 调用，校验通过后才解锁门控二。

---

## 调用契约

### 输入（由 Orchestrator 注入上下文）

| 字段 | 类型 | 说明 |
|------|------|------|
| `us_id` | string | 用户故事 ID，如 `US042` |
| `iter_id` | string | 当前迭代 ID，如 `iter_003` |
| `git_log` | string | `git log main..HEAD --pretty=full` 的完整输出 |
| `tasks_json_path` | string | `requirements/{us_id}/docs/tasks.json` 路径，用于核对 task 列表完整性 |

Orchestrator 调用示例（OpenCode Sub-Agent 格式）：
```
invoke_skill: cr-commit-check
with:
  us_id: "US042"
  iter_id: "iter_003"
  git_log: "<git log output>"
  tasks_json_path: "requirements/US042/docs/tasks.json"
```

### 输出（写回 Orchestrator）

```json
{
  "agent": "cr-commit-check",
  "verdict": "PASS | FAIL",
  "h_count": 0,
  "rules": [
    { "id": "CM-01", "result": "PASS | FAIL", "note": "…" }
  ],
  "fix_commands": ["git commit --amend", "git rebase -i HEAD~N"]
}
```

---

## 执行协议

### Step 0 — 发出启动检查点
```
[AGENT:cr-commit-check] START  us_id={us_id}  iter_id={iter_id}
```

### Step 1 — 解析 commit 列表

从 `git_log` 中提取本迭代全部 commit，按以下顺序校验每一条：

---

## 校验规则

| 规则 ID | 检查项 | 通过条件 | 失败影响 |
|---------|--------|---------|---------|
| **CM-01** | **Conventional Commits 格式** | 满足正则 `^(feat\|fix\|config\|docs\|test\|refactor\|perf\|style\|chore\|build)(\(.+\))?: .+` | FAIL |
| **CM-02** | **type 在允许列表内** | type ∈ `feat\|fix\|config\|docs\|test\|refactor\|perf\|style\|chore\|build` | FAIL |
| **CM-03** | **每迭代仅一次 commit** | commit 数量 = 1 | FAIL |
| **CM-04** | **scope 包含正确的 us_id/iter_id** | scope 满足 `#<us_id>/<iter_id>` 格式，如 `#US042/iter_003` | FAIL |
| **CM-05** | **描述中列出全部 task** | 读取 `tasks.json`，验证每个 task id 都以 `task-XX/描述` 形式出现在 message 中 | FAIL |
| **CM-06** | **无 WIP / 临时提交** | message 不含 `wip`、`temp`、`fixup!`、`squash!`，且 message 非空 | FAIL |

所有规则均为**硬性规则**：任意一条失败 → 整体裁决 `FAIL`。

### Step 2 — 输出规则结果表

逐条输出结构化结果：

```
[cr-commit-check] CM-01  ✅ PASS
[cr-commit-check] CM-02  ✅ PASS
[cr-commit-check] CM-03  ❌ FAIL  — 发现 2 条 commit，迭代只允许 1 条
[cr-commit-check] CM-04  ✅ PASS
[cr-commit-check] CM-05  ❌ FAIL  — task-03 未出现在 commit message 中
[cr-commit-check] CM-06  ✅ PASS
```

### Step 3 — 生成修复指引（仅 FAIL 时）

若裁决为 FAIL，输出可直接执行的修复命令，例如：

```bash
# 合并多余 commit 并修正 message
git rebase -i HEAD~2
# 或直接修正最后一条 commit
git commit --amend -m "feat(#US042/iter_003): task-01/login flow, task-02/jwt, task-03/tests"
```

### Step 4 — 返回结构化结果

```json
{
  "agent": "cr-commit-check",
  "verdict": "FAIL",
  "h_count": 2,
  "rules": [
    { "id": "CM-01", "result": "PASS", "note": "" },
    { "id": "CM-02", "result": "PASS", "note": "" },
    { "id": "CM-03", "result": "FAIL", "note": "发现 2 条 commit，应为 1 条" },
    { "id": "CM-04", "result": "PASS", "note": "" },
    { "id": "CM-05", "result": "FAIL", "note": "task-03 未在 message 中声明" },
    { "id": "CM-06", "result": "PASS", "note": "" }
  ],
  "fix_commands": [
    "git rebase -i HEAD~2",
    "git commit --amend -m 'feat(#US042/iter_003): task-01/…, task-02/…, task-03/…'"
  ]
}
```

### Step 5 — 发出结束检查点

```
[AGENT:cr-commit-check] DONE  verdict=PASS|FAIL  h_count=N
```

---

## 裁决规则

| 裁决 | 条件 | Orchestrator 行为 |
|------|------|-----------------|
| **PASS** | 全部 6 条规则通过 | 继续调用 `cr-code-gate` |
| **FAIL** | 任意规则失败 | 终止流水线，返回修复指引，阻塞 `release` |

---

## 禁止行为

- 禁止对不符合规范的 commit 自动修正，只输出修复命令供人工确认执行。
- 禁止将 `m`/`l` 的建议性问题升级为 FAIL。
- 禁止在 `git_log` 为空时静默通过，应报告 `CM-03 FAIL（未找到任何 commit）`。
