---
name: cr-logaf-review
description: 【Code Review 子 Agent · 门控三】基于 Sentry LOGAF 三级标注（h/m/l）对代码变更执行 8 维度全面评审（设计合理性、测试质量、预期行为验证、长期影响、代码复杂度、规范执行、变更范围、知识共享）。输出结构化 Checklist 报告并给出最终裁决。由 spec-driven-dev 的 code_review 阶段在门控二通过后自动调用。
user-invocable: false
metadata: {"openclaw": {"emoji": "🧑‍⚖️", "requires": {"bins": ["git"]}, "calledBy": ["spec-driven-dev"]}}
---

# cr-logaf-review

Code Review 流水线的**第三道门控**：LOGAF Checklist 全面评审子 Agent。
由 `spec-driven-dev` 的 `code_review` 阶段在 `cr-code-gate` 通过或 WARN 后调用。
执行 8 个维度的综合性代码评审，输出可操作的分级反馈，并给出最终合并裁决。

---

## 调用契约

### 输入（由 Orchestrator 注入上下文）

| 字段 | 类型 | 说明 |
|------|------|------|
| `us_id` | string | 用户故事 ID |
| `iter_id` | string | 当前迭代 ID |
| `git_diff` | string | `git diff main...HEAD` 的完整输出 |
| `us_file_path` | string | `requirements/US/{us_id}.md`，用于核对验收标准（CR-03） |
| `architecture_path` | string | `requirements/{us_id}/docs/architecture.md`，用于设计评审（CR-01、CR-04） |
| `test_report_path` | string | `requirements/{us_id}/docs/reports/test-{us_id}-report.md`，用于测试质量评审（CR-02） |
| `code_gate_findings` | object[] | 门控二 `cr-code-gate` 传入的 `m`/`l` 级发现列表（避免重复报告） |

Orchestrator 调用示例（OpenCode Sub-Agent 格式）：
```
invoke_skill: cr-logaf-review
with:
  us_id: "US042"
  iter_id: "iter_003"
  git_diff: "<diff output>"
  us_file_path: "requirements/US042/docs/US042.md"
  architecture_path: "requirements/US042/docs/architecture.md"
  test_report_path: "requirements/US042/docs/reports/test-US042-report.md"
  code_gate_findings: [{ "id": "GK-07", "logaf": "m", … }]
```

### 输出（写回 Orchestrator）

```json
{
  "agent": "cr-logaf-review",
  "verdict": "APPROVED | APPROVED_WITH_NOTES | REQUEST_CHANGES",
  "h_count": 0,
  "m_count": 0,
  "l_count": 0,
  "findings": [
    {
      "id": "CR-01",
      "logaf": "m",
      "verdict": "PASS | WARN | FAIL",
      "file": "src/foo.py:12",
      "description": "…",
      "suggestion": "…"
    }
  ],
  "summary": "…"
}
```

---

## 执行协议

### Step 0 — 发出启动检查点
```
[AGENT:cr-logaf-review] START  us_id={us_id}  iter_id={iter_id}
```

### Step 1 — 读取上下文

1. 解析 `git_diff` 获取所有变更文件和代码块。
2. 读取 `US042.md` 提取**验收标准清单**（用于 CR-03）。
3. 读取 `architecture.md` 获取**组件职责和接口约定**（用于 CR-01、CR-04）。
4. 读取 `test-{us_id}-report.md` 获取**覆盖率和测试失败摘要**（用于 CR-02）。
5. 接收 `code_gate_findings` 避免在 CR-05/CR-06 中重复 `m`/`l` 发现。

### Step 2 — 执行 8 维度 Checklist

---

## LOGAF Checklist

> **LOGAF 三级标注：**
> - `h`（high）— 必须在合并前解决，否则裁决 REQUEST_CHANGES
> - `m`（medium）— 应当修复，但不强制阻塞，裁决 APPROVED_WITH_NOTES
> - `l`（low）— 可选改进，不影响合并裁决

---

### CR-01 · 设计合理性

**评审问题：**
- 各模块的交互是否符合 `architecture.md` 中定义的组件职责和接口约定？
- 新增方法是否具备足够的通用性，可以提升为模块级工具函数？
- 是否存在"只需传入对象属性，却传入了整个对象"的过度耦合？
- 新增的抽象层是否必要，还是增加了不必要的间接性？

**LOGAF 定级参考：**
- `h`：新代码违反了 `architecture.md` 中明确定义的模块边界
- `m`：可提升为模块级方法，但当前实现仍可工作
- `l`：轻微耦合，可在后续迭代重构

---

### CR-02 · 测试质量

**评审问题：**
- 测试是否覆盖了 US 验收标准中的**每一条**可验证条件？
- 测试是否覆盖了缺陷修复路径（如有 bugfix 阶段）？
- 测试是否避免了不必要的 if/for 分支（防止测试代码自身引入 bug）？
- 是否存在模拟真实用户调用 API 的功能性端到端测试？
- 权限和访问控制逻辑是否有专门的测试用例（正向 + 越权拒绝）？

**LOGAF 定级参考：**
- `h`：验收标准中有条件完全未被任何测试覆盖
- `m`：测试覆盖存在盲区但核心路径已覆盖；或测试中存在可能掩盖 bug 的分支
- `l`：可补充边界情况测试，但不影响主要验证

---

### CR-03 · 预期行为验证

**评审问题：**
- 代码变更是否真实满足了 `US{us_id}.md` 中定义的**全部验收标准**？
- PR/迭代描述是否充分解释了"做了什么"以及"为什么这样做"？
- 是否解释了探索过但未采用的替代方案（防止 reviewer 重走同样的弯路）？

**LOGAF 定级参考：**
- `h`：有验收标准明确未被代码实现满足
- `m`：验收标准语义模糊，需要澄清才能确认是否满足
- `l`：迭代摘要描述不够清晰，但实现正确

---

### CR-04 · 长期影响评估

**评审问题：**
- 是否引入了大型重构、DB Schema 变更、新框架依赖，或可能永久影响性能特性的行为？
- 以上情形是否已在 `current_iter.md` 中记录了 senior 确认？
- 新增的行为是否可能在未来成为技术债（例如过度定制的解决方案）？

**LOGAF 定级参考：**
- `h`：重大架构变更无任何审批记录
- `m`：有潜在的技术债，但当前迭代范围内合理
- `l`：微小的长期影响，已在注释中说明

---

### CR-05 · 代码复杂度

**评审问题：**
- 是否存在可显著减少 LOC 的等价简化方案？（参考 Sentry 原则：LOC 与 bug 数正相关）
- for 循环是否可替换为标准库方法（`find`、`filter`、`map`、`reduce`）？
- 条件嵌套层数是否超过 3 层，可否提前 return 展平？
- 是否存在重复代码块可抽取为函数？

**LOGAF 定级参考：**
- `h`：代码逻辑极度复杂，严重影响可维护性
- `m`：存在明显的简化机会，改动后可读性显著提升
- `l`：轻微的风格偏好差异，可选改进

---

### CR-06 · 编码规范执行

**评审问题：**
- 变量、函数、文件、指标、logger 命名是否语义化、可读，并与现有代码库风格一致？
- 是否存在不应提交的冗余代码、调试语句、或过期注释？
- 数据库迁移文件是否附有部署计划（up/down 脚本、回滚策略）？
- 是否遵循了 `coding_standards.md` 中项目特定的规范约定？

> 注意：若 `cr-code-gate` 的 `code_gate_findings` 中已包含 GK-09/GK-10 的同类发现，此处不再重复报告，只做引用。

**LOGAF 定级参考：**
- `h`：命名导致语义歧义，影响团队理解和维护
- `m`：命名不一致，但语义清晰
- `l`：纯风格偏好，不影响功能

---

### CR-07 · 变更范围聚焦

**评审问题：**
- 本次迭代是否只包含一个功能或行为变更？
- 是否有无关的代码重构、格式调整或其他改动混入本次变更？
- 若涉及多个团队/模块，是否考虑拆分为独立的迭代？

**LOGAF 定级参考：**
- `h`：无关变更掩盖了核心变更，导致评审困难
- `m`：包含少量无关改动，但可识别
- `l`：微小的顺手修复，不影响理解

---

### CR-08 · 知识共享价值

**评审问题：**
- 关键业务逻辑是否有充分的注释，使其他人能够在无上下文的情况下理解意图？
- 复杂算法或非直觉性实现是否有说明"为什么这样做"而不只是"做了什么"？
- 新增的公开接口是否有完整的 docstring / JSDoc / godoc 等文档？

**LOGAF 定级参考：**
- `h`：核心业务逻辑完全无注释，严重影响知识传承
- `m`：注释不足，但可以通过阅读代码理解
- `l`：可补充的说明性注释，非必须

---

### Step 3 — 输出逐条发现

每条发现使用统一格式：
```
[{logaf}] {CR-ID} | 文件: {path}:{line_or_N/A} | 问题: {描述} | 建议: {可操作方案}
```

示例：
```
[h] CR-03 | 文件: N/A                          | 问题: 验收标准"Session 24h 过期"无任何代码实现 | 建议: 在 JWT 签发时设置 exp = now + 86400s
[m] CR-01 | 文件: src/auth/service.py:34       | 问题: validate_token() 逻辑可提升为模块级工具函数 | 建议: 移至 src/utils/jwt.py 并复用
[m] CR-02 | 文件: tests/test_auth.py            | 问题: 缺少 token 过期场景的测试用例 | 建议: 新增 test_expired_token_returns_401
[l] CR-08 | 文件: src/auth/handler.py:78        | 问题: callback 处理逻辑无注释说明状态机转换意图 | 建议: 添加注释解释 state 参数的 CSRF 防护作用
```

### Step 4 — 返回结构化结果并生成摘要

```json
{
  "agent": "cr-logaf-review",
  "verdict": "REQUEST_CHANGES",
  "h_count": 1,
  "m_count": 2,
  "l_count": 1,
  "findings": [
    {
      "id": "CR-03", "logaf": "h", "verdict": "FAIL",
      "file": "N/A",
      "description": "验收标准 'Session 24h 过期' 无实现",
      "suggestion": "在 JWT 签发时设置 exp = now + 86400s"
    }
  ],
  "summary": "发现 1 条 h 级问题（CR-03 验收标准未满足），必须修复后重新评审。2 条 m 级建议可在当前迭代或后续迭代跟进。"
}
```

### Step 5 — 发出结束检查点

```
[AGENT:cr-logaf-review] DONE  verdict=APPROVED|APPROVED_WITH_NOTES|REQUEST_CHANGES  h={N}  m={N}  l={N}
```

---

## 裁决规则

| 裁决 | 条件 | Orchestrator 行为 |
|------|------|-----------------|
| **APPROVED** | 所有 Checklist 项无 `h` 级发现，且 `m`/`l` 也为 0 | 汇总报告标注 APPROVED，解除 `release` 进入锁 |
| **APPROVED_WITH_NOTES** | 无 `h` 级发现，存在 `m`/`l` 级发现已记录 | 汇总报告标注 APPROVED_WITH_NOTES，已知风险存档，解除 `release` 进入锁 |
| **REQUEST_CHANGES** | 存在任意 `h` 级发现 | 终止流水线，阻塞 `release`，返回必修清单 |

---

## 禁止行为

- 禁止对 `h` 级 Checklist 问题因"代码作者已在注释中解释"而降级。
- 禁止重复报告 `code_gate_findings` 中已存在的相同文件和行号的问题。
- 禁止给出模糊建议（如"优化这里"），所有建议必须可操作。
- 禁止在 `git_diff` 为空时给出有效的 APPROVED，应提示 Orchestrator 核查是否存在未暂存的变更。
- 禁止从主观喜好出发将 `l` 级问题升级为 `m` 或 `h`。
