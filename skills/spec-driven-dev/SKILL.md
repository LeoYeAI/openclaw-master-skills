---
name: spec-driven-dev
description: 在克隆的 Git 仓库中驱动完整的规格驱动开发生命周期（init→requirements→architecture→process_design→project_plan→coding→test→bugfix→code_review→release）。阶段门控、产物强制输出、多语言支持，内置 commit message 检查、代码门控与 LOGAF Checklist 评审，支持任意阶段 checkpoint 保存与 rollback 恢复，并实时发出结构化进度检查点。
homepage: https://github.com/your-org/spec-driven-dev
metadata: {"openclaw": {"emoji": "🛠️", "requires": {"bins": ["git"], "env": ["SPEC_DEV_GIT_TOKEN"]}, "primaryEnv": "SPEC_DEV_GIT_TOKEN", "install": [{"id": "git-brew", "kind": "brew", "formula": "git", "bins": ["git"], "label": "安装 git（brew）"}]}}
---

# spec-driven-dev

适用于 Claude Code / OpenCode Runner 的阶段门控规格驱动开发工作流 Skill。
在 `init` 阶段克隆远程 Git 仓库，随后在该仓库内驱动每个生命周期阶段——强制产出产物、在迭代边界提交、并在 `release` 阶段推送至远端。内置 `code_review` 阶段，执行 commit message 合规校验、代码质量门控与 LOGAF Checklist 评审，所有 HIGH 级问题清零后方可进入 `release`。支持通过 `spec-driven-checkpoint` Skill 在任意阶段保存 checkpoint，并使用 `rollback {ckpt_id}` 恢复 Git 状态和 Agent 上下文。支持多语言项目，遵循 OpenSkills 渐进加载原则。

---

## 前置依赖

### 二进制工具

| 工具 | 用途 |
|------|------|
| `git` | 克隆、分支、提交、打标签、推送 |

### 环境变量

| 变量 | 是否必须 | 说明 |
|------|----------|------|
| `SPEC_DEV_GIT_TOKEN` | **必须** | HTTPS 认证用的个人访问令牌（PAT）或 OAuth2 Token。用于构造带认证的克隆 URL 并写入本地凭据助手。兼容 GitHub、GitLab、Bitbucket、Gitea 的 HTTPS 远端。 |
| `SPEC_DEV_GIT_USERNAME` | 否 | 写入 `user.name` 和凭据 URL 的 Git 用户名。未设置时默认为 `oauth2`（兼容 GitHub/GitLab Token 认证）。 |
| `SPEC_DEV_GIT_EMAIL` | 否 | 提交时使用的作者邮箱。未设置时默认为 `bot@spec-driven-dev`。 |

> **安全说明** — `SPEC_DEV_GIT_TOKEN` 仅通过 OpenClaw `skills.entries.*.env` 机制在运行时注入，**绝不写入任何产物文件、日志或迭代摘要**。凭据助手使用局限于当前 Agent 会话的本地 `~/.git-credentials` 存储。

---

## 快速开始

```
# 1 – 克隆远程仓库并初始化 US 目录
init-US042
git_remote: https://github.com/my-org/my-repo.git
us_content: |
  ## US042 – OAuth2 登录
  作为用户，我希望使用 Google 账号登录。
  ### 验收标准
  - [ ] Google OAuth2 重定向正常
  - [ ] 回调后签发 JWT
context: "Python 3.11 + FastAPI。数据库为 PostgreSQL 15，不新增依赖。"

# 2 – 链式执行各阶段（git_remote 在 init 后自动持久化到 current_iter.md）
requirements-US042
architecture-US042
process_design-US042
project_plan-US042
coding-US042
test-US042
bugfix-US042        # 仅当 test 阶段报告 HIGH 级失败时执行
code_review-US042   # 三层门控：commit message + 代码质量 + LOGAF Checklist
release-US042       # 仅当 code_review 裁决为 APPROVED 或 APPROVED_WITH_NOTES 时解锁
```

---

## 输入变量

| 变量 | 类型 | 是否必须 | 说明 |
|------|------|----------|------|
| `us_id` | string | **必须** | 用户故事 ID（如 `US042`）。从 `<stage>-<us_id>` 触发模式中自动捕获，映射至所有产物路径。 |
| `stage` | enum | **必须** | 生命周期阶段：`init` · `requirements` · `architecture` · `process_design` · `project_plan` · `coding` · `test` · `bugfix` · `code_review` · `release` |
| `git_remote` | string | `init` 阶段必须 | 远程 Git 仓库的 HTTPS URL。`init` 后存入 `current_iter.md`，后续阶段自动读取，无需重复传入。 |
| `us_content` | string | 否 | 用户故事完整文本。在阶段运行前写入 `requirements/US/{us_id}.md`。已存在时追加合并，除非 `force_overwrite: true`。 |
| `context` | string | 否 | 自由格式的补充上下文，逐字注入到本次产出的每个产物的 `### 补充上下文` 标题下。适用于 ADR 摘录、环境约束、Review 反馈等。 |
| `iter_id` | string | 否 | 当前迭代 ID（如 `iter_003`）。省略时自动从 `current_iter.md` 中检测；首次运行默认为 `iter_001`。 |
| `force_overwrite` | bool | 否 · 默认 `false` | 为 `true` 时覆盖已有产物文件，而非追加合并。 |
| `skip_skill_scan` | bool | 否 · 默认 `false` | 为 `true` 时跳过 `available_skills.xml` 扫描（适用于 Runner 已在外部完成 Skill 解析的场景）。 |

---

## 触发条件

本 Skill 在以下情况激活：

1. **阶段命令模式** — 用户输入 `<stage>-<us_id>`，例如：
   - `init-US042`
   - `coding-US042`
   - `code_review-US042`
   - `release-FEAT_LOGIN`

2. **Checkpoint 命令** — 任意时刻均可触发：
   - `save_checkpoint-{us_id}` 或 `checkpoint-{us_id}` — 手动保存当前状态
   - `rollback {ckpt_id}` — 回滚到指定 checkpoint
   - `rollback {ckpt_id} --git-only` — 仅回滚 Git
   - `rollback {ckpt_id} --context-only` — 仅输出恢复 Prompt
   - `list_checkpoints-{us_id}` — 列出所有 checkpoint

3. **下一迭代意图** — 用户输入以下任意一种：
   - `{us_id}进行下一个迭代`
   - `next iteration {us_id}`
   - `start|begin|run|execute … sprint|iteration|milestone`

   → 自动从 `requirements/{us_id}/docs/iteration_summary/current_iter.md` 恢复上下文继续执行

---

## 路径常量

所有路径使用 `{us_id}`、`{iter_id}`、`{version}` 作为占位符。

```
requirements/US/{us_id}.md
requirements/{us_id}/docs/requirements.md
requirements/{us_id}/docs/architecture.md
requirements/{us_id}/docs/process_design.md
requirements/{us_id}/docs/project_plan.md
requirements/{us_id}/docs/tasks.json
requirements/{us_id}/docs/iteration_summary/current_iter.md
requirements/{us_id}/docs/iteration_summary/{iter_id}.md
requirements/{us_id}/docs/release_notes/{version}.md
requirements/{us_id}/docs/reports/test-{us_id}-report.md
requirements/{us_id}/docs/reports/review-{us_id}-{iter_id}.md
requirements/{us_id}/docs/checkpoints/index.md
requirements/{us_id}/docs/checkpoints/{ckpt_id}.md
auxiliary/coding_standards.md
auxiliary/gitflow_guide.md
auxiliary/skills/available_skills.xml
src/
tests/
config/
CHANGELOG.md
PROJECT_STATUS.md
.github/workflows/ci.yml
```

---

## 执行协议

每次调用**必须**按顺序执行以下六步协议。

### 第 0 步 — 发出 `stage_start` 检查点

```
[SKILL:spec-driven-dev] CHECKPOINT stage_start STATUS=OK  us_id={us_id}  stage={stage}
```

### 第 1 步 — 验证输入

1. 确认 `us_id` 和 `stage` 已存在。
2. 若提供了 `us_content`，写入（或合并）到 `requirements/US/{us_id}.md`。
3. 若提供了 `context`，在内存中保存，并在本次产出的每个产物中以 `### 补充上下文` 标题开头注入。
4. 解析 `iter_id`：
   - 若显式提供，直接使用。
   - 否则从 `current_iter.md` 中读取。
   - 若文件不存在，默认为 `iter_001`。
5. 解析 `git_remote`：
   - 若显式提供，使用并持久化到迭代摘要。
   - 否则从 `current_iter.md` 的 `git_remote:` 字段中读取。
   - 若仍不存在且当前阶段不是 `init`，发出警告后继续执行。

```
[SKILL:spec-driven-dev] CHECKPOINT inputs_validated STATUS=OK
```

### 第 2 步 — Skill 扫描（`skip_skill_scan: true` 时跳过）

1. 完整读取 `auxiliary/skills/available_skills.xml`。
2. 将可用 Skill 与当前阶段需求进行匹配。
3. 若找到匹配项，宣布：
   > "我将调用 Skill：`<n>` 来辅助本次任务。"
   随即完整加载 `auxiliary/skills/<n>/SKILL.md` 后再继续执行。
4. **禁止一次性加载所有 Skill** — 每次只按需加载一个（渐进披露原则）。

```
[SKILL:spec-driven-dev] CHECKPOINT skill_scan_done STATUS=OK  skills_loaded=[…]
```

### 第 3 步 — 执行阶段

严格按照下方**阶段定义**章节执行。
每写完一个强制输出文件后发出：

```
[SKILL:spec-driven-dev] CHECKPOINT artefacts_written STATUS=OK  files=[…]
```

### 第 4 步 — 质量门控（仅 coding / test / bugfix 阶段）

按语言检测表运行静态检查和测试。

通过时：
```
[SKILL:spec-driven-dev] CHECKPOINT quality_gate_passed STATUS=OK
```
失败时：发出 `STATUS=FAIL`，汇总失败信息，并指示 Agent 进入 `bugfix` 阶段。
同一问题连续失败 5 次后，停止自动修复并请求人工介入。

### 第 5 步 — 写入迭代摘要

1. 递增 `iter_id`（如 `iter_003` → `iter_004`）。
2. 使用下方模板写入 `requirements/{us_id}/docs/iteration_summary/{iter_id}.md`。
3. 用相同内容覆盖 `requirements/{us_id}/docs/iteration_summary/current_iter.md`。
4. 更新 `PROJECT_STATUS.md`。

```
[SKILL:spec-driven-dev] CHECKPOINT iteration_summary_written STATUS=OK  iter_id={iter_id}
```

### 第 6 步 — 发出 `stage_done`

```
[SKILL:spec-driven-dev] CHECKPOINT stage_done STATUS=OK
<stage_done>
```

---

## 阶段定义

### `init`

**目的：** 从环境变量配置 Git 凭据、将远程仓库克隆到工作区、初始化 US 目录树，并将纯文本 `git_remote` URL 记录到迭代摘要，供后续所有阶段免密推拉使用。

**读取：** 无（从零启动）

**写入：**
- 克隆后的仓库（工作区根目录）
- `requirements/US/{us_id}.md`（脚手架或来自 `us_content`）
- 完整的 `requirements/{us_id}/docs/` 目录树
- `requirements/{us_id}/docs/iteration_summary/current_iter.md`（存根）
- `PROJECT_STATUS.md`（初始条目）

**凭据配置 — 按此顺序执行：**

```bash
# 1. 从环境变量解析运行时值
GIT_USER="${SPEC_DEV_GIT_USERNAME:-oauth2}"
GIT_EMAIL="${SPEC_DEV_GIT_EMAIL:-bot@spec-driven-dev}"
GIT_TOKEN="${SPEC_DEV_GIT_TOKEN}"        # 必填；metadata.requires.env 已做门控

# 2. 构造带认证的克隆 URL（Token 内嵌，绝不写入产物）
#    兼容：https://github.com/…  https://gitlab.com/…  https://bitbucket.org/…
REMOTE_HOST=$(echo "${git_remote}" | sed 's|https://||' | cut -d'/' -f1)
CLONE_URL="https://${GIT_USER}:${GIT_TOKEN}@${REMOTE_HOST}/$(echo "${git_remote}" | sed "s|https://${REMOTE_HOST}/||")"

# 3. 克隆
git clone "${CLONE_URL}" .

# 4. 设置提交身份
git config user.name  "${GIT_USER}"
git config user.email "${GIT_EMAIL}"

# 5. 持久化凭据，供本工作区后续 push/pull 静默认证
git config credential.helper store
printf "https://%s:%s@%s\n" "${GIT_USER}" "${GIT_TOKEN}" "${REMOTE_HOST}" \
  >> ~/.git-credentials
chmod 600 ~/.git-credentials
```

> **Token 绝不写入任何产物或日志。** 仅将不含凭据的裸 `git_remote` URL 存入 `current_iter.md`。

**关键指令：**
1. 在任何其他 git 操作前先执行凭据配置代码块。
2. 创建路径常量中尚不存在的所有子目录。
3. 若提供了 `us_content`，写入 `requirements/US/{us_id}.md`；否则写入含占位标题的 Markdown 脚手架。
4. 若提供了 `context`，在脚手架中注入 `### 补充上下文` 节。
5. 在 `current_iter.md` 的 `git_remote:` 字段中记录**纯文本** `git_remote` URL（不含 Token）。

---

### `requirements`

**读取：**
- `requirements/US/{us_id}.md`
- `auxiliary/coding_standards.md`

**写入：**
- `requirements/{us_id}/docs/requirements.md`

**关键指令：**
1. 识别功能范围与边界。
2. 挖掘非功能性需求（性能、安全、兼容性）。
3. 定义可量化的验收标准。
4. 注入 `context` 至 `### 补充上下文`。

---

### `architecture`

**读取：**
- `requirements/{us_id}/docs/requirements.md`
- `auxiliary/coding_standards.md`
- `auxiliary/gitflow_guide.md`

**写入：**
- `requirements/{us_id}/docs/architecture.md` — **必须包含 Mermaid 架构图**

**关键指令：**
1. 选择架构风格（微服务 / 模块化 / 单体）并说明理由。
2. 定义组件、职责与接口。
3. 说明技术选型决策。
4. 嵌入至少一张 `mermaid` 架构图。
5. 注入 `context` 至 `### 补充上下文`。

---

### `process_design`

**读取：**
- `requirements/{us_id}/docs/architecture.md`

**写入：**
- `requirements/{us_id}/docs/process_design.md` — **必须包含 Mermaid 流程图或状态图**

**关键指令：**
1. 建模主执行流程（ReAct / Plan-and-Execute / 标准 CRUD，视情况选用）。
2. 详细描述每个步骤。
3. 定义异常处理与重试/降级行为。
4. 嵌入至少一张 `mermaid` 流程图或序列图。

---

### `project_plan`

**读取：**
- `requirements/{us_id}/docs/architecture.md`
- `requirements/{us_id}/docs/process_design.md`

**写入：**
- `requirements/{us_id}/docs/project_plan.md`
- `requirements/{us_id}/docs/tasks.json`

**关键指令：**
1. 将工作拆解为粒度 1–3 天的任务，附里程碑、优先级和工时估算。
2. 按以下 Schema 产出 `tasks.json`：
   ```json
   [
     {
       "id": "task-1",
       "name": "任务名称",
       "scope": "src/module/",
       "stage": "coding",
       "depends_on": []
     }
   ]
   ```

---

### `coding`

**读取：**
- `requirements/{us_id}/docs/iteration_summary/current_iter.md`  ← **优先读取**
- `requirements/{us_id}/docs/architecture.md`
- `requirements/{us_id}/docs/process_design.md`
- `requirements/{us_id}/docs/tasks.json`
- `auxiliary/coding_standards.md`
- `auxiliary/gitflow_guide.md`

**写入：**
- `src/` 下的源代码文件
- `tests/` 下的测试文件

**关键指令：**
1. **优先**读取 `current_iter.md` 了解历史进度。
2. 只实现当前迭代范围内的任务。
3. 使用类型注解、清晰命名和详细 docstring。
4. 遵循语言检测表对应的工具链。
5. 创建并切换到 `feature/{task-name}` 分支（GitFlow）。
6. **质量门控通过前禁止提交**（由 `test` / `bugfix` 阶段完成）。
7. 将 `context` 注入相关模块级 docstring。

---

### `test`

**读取：**
- `src/` 下的源代码文件
- `auxiliary/coding_standards.md`

**写入：**
- `requirements/{us_id}/docs/reports/test-{us_id}-report.md`

**关键指令：**
1. 按语言检测表运行（或模拟）完整测试套件。
2. 报告：格式化 · Lint · 类型检查 · 测试结果 · 覆盖率 %。
3. 覆盖率目标：整体 ≥ 80%；关键模块 ≥ 90%。
4. 每个失败项输出：严重程度（HIGH / MEDIUM / LOW）及修复建议。
5. 立即修复 HIGH 级失败；将 MEDIUM / LOW 记录到 TODO。

---

### `bugfix`

**读取：**
- `requirements/{us_id}/docs/reports/test-{us_id}-report.md`
- 失败的源代码 / 测试文件

**写入：**
- `src/` 下更新后的源代码文件
- `tests/` 下更新后的测试文件
- `requirements/{us_id}/docs/reports/test-{us_id}-report.md`（追加新条目）

**关键指令：**
1. 针对每个 HIGH 级失败：分析根因 → 修复 → 验证。
2. 每批修复后重新运行测试。
3. 所有 HIGH 级失败解决后，重新运行完整套件。
4. 自动修复上限为 5 次；超限后停止并请求人工介入。
5. **自动 Checkpoint 触发**：同一问题连续失败 ≥ 3 次时，在第 3 次失败后立即调用 `spec-driven-checkpoint`：
   ```
   invoke_skill: spec-driven-checkpoint
   action: save
   with:
     us_id: "{us_id}"
     iter_id: "{iter_id}"
     stage: "bugfix"
     interrupt_reason: "bugfix_loop_{n}"
     pending_items: "修复失败的问题列表"
   ```

---

### `code_review`

**目的（Orchestrator）：** 按序调用三个独立子 Agent，依次执行门控一→二→三；收集每个子 Agent 的结构化输出，合并写入最终评审报告，并根据聚合裁决决定是否解除 `release` 进入锁。

> 三个子 Agent Skill 须已安装到 `auxiliary/skills/` 并注册在 `available_skills.xml` 中：
> - `cr-commit-check` — 门控一：Commit Message 合规校验
> - `cr-code-gate`    — 门控二：代码质量静态门控
> - `cr-logaf-review` — 门控三：LOGAF Checklist 全面评审

**读取：**
- `requirements/{us_id}/docs/iteration_summary/current_iter.md`
- `requirements/{us_id}/docs/reports/test-{us_id}-report.md`
- `auxiliary/skills/available_skills.xml`（确认三个子 Agent 已注册）

**写入：**
- `requirements/{us_id}/docs/reports/review-{us_id}-{iter_id}.md`（汇总评审报告）

---

#### Orchestrator 执行流程

```
[SKILL:spec-driven-dev] CHECKPOINT review_start STATUS=OK  us_id={us_id}  iter_id={iter_id}
```

##### 阶段 R-0：收集共享上下文

在调用任何子 Agent 之前，统一收集以下数据并缓存，按需传入各子 Agent：

```bash
# 1. 获取 commit log（门控一使用）
GIT_LOG=$(git log main..HEAD --pretty=full)

# 2. 获取完整 diff（门控二、三使用）
GIT_DIFF=$(git diff main...HEAD)

# 3. 路径常量
TASKS_PATH="requirements/{us_id}/docs/tasks.json"
ITER_PATH="requirements/{us_id}/docs/iteration_summary/current_iter.md"
TEST_REPORT_PATH="requirements/{us_id}/docs/reports/test-{us_id}-report.md"
```

---

##### 阶段 R-1：调用 `cr-commit-check`（门控一）

```
invoke_skill: cr-commit-check
with:
  us_id: "{us_id}"
  iter_id: "{iter_id}"
  git_log: $GIT_LOG
  tasks_json_path: $TASKS_PATH
```

```
[SKILL:spec-driven-dev] CHECKPOINT review_commit_msg STATUS=<OK|FAIL>
```

**分支逻辑：**
- `verdict == "FAIL"` → **立即终止**，跳转至「汇总报告」步骤，`release` 被阻塞。
- `verdict == "PASS"` → 继续阶段 R-2。

---

##### 阶段 R-2：调用 `cr-code-gate`（门控二）

```
invoke_skill: cr-code-gate
with:
  us_id: "{us_id}"
  iter_id: "{iter_id}"
  git_diff: $GIT_DIFF
  iter_summary_path: $ITER_PATH
  coding_standards_path: "auxiliary/coding_standards.md"
```

缓存返回的 `findings` 供门控三去重使用：

```
[SKILL:spec-driven-dev] CHECKPOINT review_code_gate STATUS=<OK|WARN|FAIL>
```

**分支逻辑：**
- `verdict == "FAIL"` → **立即终止**，跳转至「汇总报告」步骤，`release` 被阻塞。
- `verdict == "PASS"` 或 `"WARN"` → 继续阶段 R-3，携带 `findings`。

---

##### 阶段 R-3：调用 `cr-logaf-review`（门控三）

```
invoke_skill: cr-logaf-review
with:
  us_id: "{us_id}"
  iter_id: "{iter_id}"
  git_diff: $GIT_DIFF
  us_file_path: "requirements/US/{us_id}.md"
  architecture_path: "requirements/{us_id}/docs/architecture.md"
  test_report_path: $TEST_REPORT_PATH
  code_gate_findings: <门控二返回的 findings 数组>
```

```
[SKILL:spec-driven-dev] CHECKPOINT review_checklist STATUS=<APPROVED|APPROVED_WITH_NOTES|REQUEST_CHANGES>
```

---

##### 阶段 R-4：聚合裁决

| 最终裁决 | 触发条件 |
|---------|---------|
| **REQUEST_CHANGES** | 门控一 FAIL，**或** 门控二 FAIL，**或** 门控三 REQUEST_CHANGES |
| **APPROVED_WITH_NOTES** | 无 FAIL / REQUEST_CHANGES，但门控二 WARN 或门控三 APPROVED_WITH_NOTES |
| **APPROVED** | 三层全部 PASS / APPROVED，且无任何 `h` 级发现 |

```
[SKILL:spec-driven-dev] CHECKPOINT review_done STATUS=<APPROVED|APPROVED_WITH_NOTES|REQUEST_CHANGES>
```

---

#### 汇总评审报告模板

写入 `requirements/{us_id}/docs/reports/review-{us_id}-{iter_id}.md`：

````markdown
# Code Review 报告 – {us_id} / {iter_id}
**日期：** YYYY-MM-DD
**Orchestrator：** spec-driven-dev
**最终裁决：** APPROVED | APPROVED_WITH_NOTES | REQUEST_CHANGES

---

## 门控一：Commit Message 校验（cr-commit-check）
| 规则 ID | 结果   | 备注 |
|---------|--------|------|
| CM-01   | ✅/❌  |      |
| CM-02   | ✅/❌  |      |
| CM-03   | ✅/❌  |      |
| CM-04   | ✅/❌  |      |
| CM-05   | ✅/❌  |      |
| CM-06   | ✅/❌  |      |

**门控结论：** PASS / FAIL

---

## 门控二：代码质量门控（cr-code-gate）
| 发现 ID | LOGAF | 结果  | 文件:行 | 描述 | 建议 |
|---------|-------|-------|---------|------|------|
| GK-xx   | `h`   | ✅/❌ |         |      |      |

**门控结论：** PASS / WARN / FAIL
**h 级：** N | **m 级：** N | **l 级：** N

---

## 门控三：LOGAF Checklist（cr-logaf-review）
| 发现 ID | LOGAF | 结果  | 文件:行 | 描述 | 建议 |
|---------|-------|-------|---------|------|------|
| CR-xx   | `m`   | ⚠️    |         |      |      |

**评审结论：** APPROVED / APPROVED_WITH_NOTES / REQUEST_CHANGES
**h 级：** N | **m 级：** N | **l 级：** N

---

## 总结与下一步行动
<!-- REQUEST_CHANGES：列出全部 h 级问题，说明须重走 bugfix→test→code_review -->
<!-- APPROVED_WITH_NOTES：列出 m/l 级建议，可在后续迭代跟进 -->
<!-- APPROVED：解除 release 进入锁 -->
````

---

#### `code_review` 阶段裁决规则

| 最终裁决 | 条件 | 对 `release` 的影响 |
|---------|------|-------------------|
| **APPROVED** | 三层门控全部 PASS，无任何 `h` 级问题 | ✅ 解除 `release` 进入锁 |
| **APPROVED_WITH_NOTES** | 无 `h` 级问题，存在 `m`/`l` 级问题已记录 | ✅ 解除 `release` 进入锁，已知风险已存档 |
| **REQUEST_CHANGES** | 存在任意 `h` 级问题（门控二或门控三）| ❌ 阻塞 `release`，必须重走 `bugfix→test→code_review`。**同时自动触发 checkpoint 保存**：`invoke_skill: spec-driven-checkpoint action: save … interrupt_reason: "review_rejected"` |

---

### `release`

**目的：** 提交本迭代所有变更、升级版本号、更新变更日志、写入发版说明，并将提交与标签推送至远端。

**读取：**
- 当前工作区（所有质量门控已通过）
- `requirements/{us_id}/docs/reports/review-{us_id}-{iter_id}.md` ← **必须为 APPROVED 或 APPROVED_WITH_NOTES，否则直接拒绝进入**
- `CHANGELOG.md`
- `requirements/{us_id}/docs/iteration_summary/current_iter.md`（获取 `git_remote`）

**写入：**
- `main`（或配置的基础分支）上的单次迭代提交
- 更新后的版本声明文件（`pyproject.toml` / `package.json` / `Cargo.toml` 等）
- `CHANGELOG.md`（增量更新）
- `requirements/{us_id}/docs/release_notes/{version}.md`
- 推送至远端的 Git 标签 `v{version}`

**关键指令：**

1. **前置门控检查**：读取 `review-{us_id}-{iter_id}.md`，确认最终裁决为 `APPROVED` 或 `APPROVED_WITH_NOTES`。若为 `REQUEST_CHANGES` 则立即终止，输出：
   ```
   [SKILL:spec-driven-dev] RELEASE BLOCKED — code_review 裁决为 REQUEST_CHANGES，
   请先完成 bugfix → test → code_review 循环，清零所有 h 级问题。
   ```

2. 确认凭据助手仍处于活动状态；如会话已刷新，重新执行 init 凭据配置代码块：
   ```bash
   git config credential.helper   # 应返回 "store"
   ```

3. 根据本迭代最高级别的提交类型确定版本升级幅度：
   - `feat` → **minor**
   - `fix · chore · docs · test · refactor · perf · style · config · build` → **patch**
   - `feat!` 或 `BREAKING CHANGE` → **major**

3. 暂存所有变更并创建**单次迭代提交**：
   ```
   {type}(#{us_id}/{iter_id}): {task_id1}/{desc1}, {task_id2}/{desc2}, …
   ```
   允许的 type：`feat|fix|config|docs|test|refactor|perf|style|chore|build`

4. 按语言运行版本升级命令：
   - Python → `cz bump`
   - Node   → `npm version <major|minor|patch>`
   - Rust   → `cargo release <level>`
   - Go     → `git tag v{version}`

5. 在 `CHANGELOG.md` 中追加新版本块。

6. 将用户友好的发版说明写入 `requirements/{us_id}/docs/release_notes/v{version}.md`。

7. 推送提交和标签（凭据助手静默处理认证）：
   ```bash
   git push origin main
   git push origin "v{version}"
   ```

---

## 语言检测

| 根目录文件 | 语言 | 格式化工具 | Lint 工具 | 类型检查 | 测试框架 |
|------------|------|-----------|-----------|----------|----------|
| `pyproject.toml` | Python | black | ruff | mypy | pytest |
| `package.json` + `tsconfig.json` | TypeScript | Prettier | ESLint | tsc | Jest / Vitest |
| `go.mod` | Go | gofmt | golangci-lint | — | go test |
| `Cargo.toml` | Rust | rustfmt | clippy | — | cargo test |
| `pom.xml` | Java | spotless | Checkstyle | SpotBugs | JUnit 5 |

---

## 迭代摘要模板

用于每个 `{iter_id}.md` 和 `current_iter.md`，目标控制在 800–1500 Token。

```markdown
# 迭代摘要 – {iter_id}
**日期：** YYYY-MM-DD
**US：** {us_id}
**已完成阶段：** {stage}
**git_remote：** https://github.com/org/repo.git
**Code Review 裁决：** APPROVED | APPROVED_WITH_NOTES | REQUEST_CHANGES | 本阶段未执行
**调用的 Skill：** <逗号分隔列表，或填"无">

## 本次迭代目标
<一段话说明本次迭代要达成什么。>

## 架构 / 流程变更
<本次迭代做出或修订的结构性决策。无变化则填"无"。>

## 已完成任务
| 任务 ID | 描述 | 状态 |
|---------|------|------|
| task-1  | …    | ✅ 完成 |

## 关键优化点
- …

## 本次发布版本
<vX.Y.Z 或"本次迭代未发布">

## 待办 / 下一步
- …

## 项目状态快照
<2–3 句话：测试覆盖率、未解决阻塞项、下一个里程碑。>
```

> 注意：`git_remote` 只存储纯文本 URL — **不含 Token 或任何凭据**。

---

## 响应输出格式

每次响应**必须**采用以下结构：

### 1 · 本次执行计划
列出本次将完成的步骤。

### 2 · 可用 Skill 概览
粘贴 `auxiliary/skills/available_skills.xml` 的完整内容。

### 3 · Skill 调用（如需要）
宣布并加载匹配 Skill 的 `SKILL.md`。

### 4 · 文件变更清单
每个新建或修改的文件：完整路径 + 完整内容（或统一 diff），置于代码块中。

### 5 · 静态检查与测试结果（仅 coding / test / bugfix 阶段）
格式化工具、Lint、类型检查、测试框架的关键输出。

### 6 · Git 与版本操作
精确的提交信息、版本升级命令、打标签命令和推送命令。

### 7 · 迭代摘要
填写完整的**迭代摘要模板**。

### 8 · 本次发出的进度检查点
本次运行的每个检查点及其状态。

---

## 禁止行为

- 禁止将 `SPEC_DEV_GIT_TOKEN` 或任何凭据写入任何文件、日志或产物。
- 禁止一次性加载所有 Skill — 严格遵守渐进披露原则。
- 禁止在迭代中途提交；每个完整迭代只允许一次提交。
- 禁止跳过质量门控，即使用户要求加快速度。
- 禁止跳过 `code_review` 阶段直接进入 `release`。
- 禁止在 `code_review` 裁决为 `REQUEST_CHANGES` 时执行 `release`；必须先清零所有 `h` 级问题。
- 禁止将评审反馈中的 `m`/`l` 级问题升级为阻塞项，除非用户明确要求。
- 禁止在路径常量之外新增或删除顶层目录。
- 禁止回溯完整对话历史；所有上下文只从 `current_iter.md` 和输入变量中获取。
- 禁止在 `test` 阶段存在未解决的 HIGH 级失败时进入 `code_review` 阶段。
