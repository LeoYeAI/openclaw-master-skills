---
name: spec-driven-checkpoint
description: 为 spec-driven-dev 提供流程中断保存与恢复能力。在任意阶段触发 checkpoint 保存当前 Git 快照、迭代状态、Session 元数据和上下文重建包；rollback 命令可将 Git 仓库和 Agent 上下文恢复到任意历史 checkpoint。支持 save_checkpoint-{us_id} 和 rollback {ckpt_id} 触发。
user-invocable: true
metadata: {"openclaw": {"emoji": "🔖", "requires": {"bins": ["git"]}, "calledBy": ["spec-driven-dev"]}}
---

# spec-driven-checkpoint

> **设计前言 — 可行性分析**
>
> 在实现之前，必须明确 Coding Agent Session 的真实限制，以便选择最可靠的技术路径。

---

## 可行性分析

### 五个核心问题的可行性评估

| 问题 | 可行性 | 限制与解法 |
|------|--------|-----------|
| **保存 Git 快照** | ✅ 完全可行 | `git commit` + `git tag ckpt-{id}` — 成熟方案，完全可靠 |
| **保存阶段/迭代状态** | ✅ 完全可行 | 写入结构化 Markdown 文件，与 `current_iter.md` 同等可靠 |
| **捕获 Session ID** | ⚠️ 环境依赖 | OpenCode 通过 `$OPENCODE_SESSION_ID` 暴露；Claude Code CLI 通过 `$CLAUDE_SESSION_ID`；无法获取时生成本地 fallback UUID |
| **真正恢复对话历史** | ❌ 不可行 | **所有主流 Coding Agent（OpenCode、Claude Code、Cursor）均不支持跨 Session 导入原始对话历史**。对话历史存在 Agent 运行时内存中，进程退出即消失，无对外持久化 API |
| **上下文语义恢复** | ✅ 完全可行 | 用「重建 Prompt 包」替代原始历史。将关键决策、修复记录、状态快照压缩为结构化 Markdown，作为新 Session 的首条 context 注入，使新 Session 能精确接续工作 |

### 关键设计选择：重建 Prompt 而非回放历史

真正恢复对话历史在技术层面不可行，但**对话历史本身并非目标**——目标是让新 Session 知道：
1. 在做什么（任务/阶段/迭代）
2. 做到哪了（完成的文件、通过的测试）
3. 遇到什么问题（失败记录、待修复项）
4. 接下来要做什么（明确的下一步指令）

这四点完全可以通过结构化文档重建，效果等同于甚至优于原始对话历史（因为噪音更少）。

### Rollback 可行性

| 操作 | 可行性 | 实现 |
|------|--------|------|
| Git 仓库回滚 | ✅ | `git reset --hard ckpt-{id}` 或 `git checkout ckpt-{id}` |
| 恢复 working tree 文件 | ✅ | 附带 git reset |
| 恢复 Session 上下文 | ✅ | 将 checkpoint 文档作为新 Session 首条 context 注入 |
| 恢复原始 Session | ❌ | 技术不可行，用「重建 Session」替代 |

---

## 最终架构决策

```
checkpoint 保存
  ├─ [Git 层]     git commit(WIP) + git tag ckpt-{id}    ← 代码快照，硬保证
  ├─ [状态层]     写入 checkpoints/{ckpt_id}.md          ← 结构化状态文档
  └─ [重建层]     生成 resume_prompt 块                  ← 新 Session 启动包

rollback {ckpt_id}
  ├─ [Git 层]     git reset --hard ckpt-{id}             ← 代码回滚
  ├─ [状态层]     恢复 current_iter.md 快照              ← 状态回滚
  └─ [重建层]     输出 RESUME_CONTEXT 块                 ← 新 Session 启动
```

---

## 前置依赖

| 工具 | 用途 |
|------|------|
| `git` | 提交、打标签、reset、log |

---

## 路径常量

```
requirements/{us_id}/docs/checkpoints/                   ← checkpoint 目录
requirements/{us_id}/docs/checkpoints/index.md           ← 所有 checkpoint 索引
requirements/{us_id}/docs/checkpoints/{ckpt_id}.md       ← 单个 checkpoint 文档
```

**Checkpoint ID 格式：** `ckpt-{YYYYMMDD}-{HHmmss}-{8位hex}`
- 示例：`ckpt-20240115-143022-a3f8b21c`
- 8 位 hex 由 `git rev-parse --short=8 HEAD` 或随机生成提供
- 全局唯一，不依赖 Session ID

**Git Tag 格式：** `checkpoint/{ckpt_id}`
- 示例：`refs/tags/checkpoint/ckpt-20240115-143022-a3f8b21c`

---

## 触发方式

| 触发命令 | 含义 |
|---------|------|
| `save_checkpoint-{us_id}` | 手动保存 checkpoint |
| `checkpoint-{us_id}` | 同上（别名） |
| `rollback {ckpt_id}` | 回滚到指定 checkpoint |
| `rollback {ckpt_id} --git-only` | 仅回滚 Git，不输出重建 Prompt |
| `rollback {ckpt_id} --context-only` | 仅输出重建 Prompt，不操作 Git |
| `list_checkpoints-{us_id}` | 列出所有 checkpoint |

**自动触发（由 spec-driven-dev 在检测到以下情况时调用）：**
- 质量门控连续失败 3 次（`bugfix` 阶段自动保存）
- `code_review` 返回 `REQUEST_CHANGES` 前自动保存
- 任意阶段 `CHECKPOINT … STATUS=FAIL` 连续出现 3 次

---

## 操作一：保存 Checkpoint

### 输入参数

| 参数 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `us_id` | string | 是 | 用户故事 ID |
| `iter_id` | string | 是 | 当前迭代 ID |
| `stage` | string | 是 | 中断时所在阶段 |
| `interrupt_reason` | string | 否 | 中断原因描述；自动触发时由调用方填入 |
| `session_id` | string | 否 | Agent 运行时 Session ID；从环境变量读取 |
| `pending_items` | string | 否 | 未完成事项列表（自由文本） |
| `context` | string | 否 | 额外补充上下文 |

### 执行步骤

#### Step S-0 — 生成 Checkpoint ID

```bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
GIT_SHORT=$(git rev-parse --short=8 HEAD 2>/dev/null || openssl rand -hex 4)
CKPT_ID="ckpt-${TIMESTAMP}-${GIT_SHORT}"
```

#### Step S-1 — 捕获 Session ID

```bash
# 优先级：OpenCode → Claude Code → 环境变量 → 本地生成
SESSION_ID="${OPENCODE_SESSION_ID:-${CLAUDE_SESSION_ID:-${AGENT_SESSION_ID:-}}}"
if [ -z "$SESSION_ID" ]; then
  SESSION_ID="local-$(date +%s)-$(openssl rand -hex 4)"
fi
```

> Session ID 仅作为**元数据追溯**使用，不用于恢复原始会话。

#### Step S-2 — 保存 Git 快照

```bash
# 1. 暂存所有当前修改（包括未 commit 的 WIP）
git add -A

# 2. 检查是否有变更需要提交
if ! git diff --cached --quiet; then
  git commit -m "checkpoint(#{us_id}/{iter_id}): ${CKPT_ID} WIP auto-save"
fi

# 3. 打轻量标签，记录代码状态
git tag "checkpoint/${CKPT_ID}"

# 记录提交 SHA（即使无新提交也记录当前 HEAD）
GIT_SHA=$(git rev-parse HEAD)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
```

#### Step S-3 — 采集状态快照

```bash
# 采集以下信息用于写入 checkpoint 文档
MODIFIED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || git diff --name-only)
TEST_STATUS="从 requirements/{us_id}/docs/reports/test-{us_id}-report.md 读取最后测试状态"
ITER_SUMMARY="从 requirements/{us_id}/docs/iteration_summary/current_iter.md 读取全文"
```

#### Step S-4 — 写入 Checkpoint 文档

写入 `requirements/{us_id}/docs/checkpoints/{ckpt_id}.md`，使用下方**文档模板**。

#### Step S-5 — 更新索引

在 `requirements/{us_id}/docs/checkpoints/index.md` 追加一行：

```markdown
| {ckpt_id} | {YYYY-MM-DD HH:mm:ss} | {stage} | {iter_id} | {interrupt_reason} | {git_sha_short} |
```

#### Step S-6 — 推送标签到远端（可选）

```bash
git push origin "checkpoint/${CKPT_ID}"
```

```
[SKILL:spec-driven-checkpoint] CHECKPOINT saved STATUS=OK  id={ckpt_id}  git_sha={sha}
```

---

## Checkpoint 文档模板

````markdown
---
ckpt_id: {ckpt_id}
session_id: {session_id}
created_at: YYYY-MM-DD HH:mm:ss
us_id: {us_id}
iter_id: {iter_id}
stage: {stage}
interrupt_reason: {interrupt_reason}
git_sha: {git_sha}
git_branch: {git_branch}
git_tag: checkpoint/{ckpt_id}
status: ACTIVE
---

# Checkpoint {ckpt_id}

> **恢复此 checkpoint 请执行：** `rollback {ckpt_id}`

---

## 1. 中断上下文摘要

**中断阶段：** {stage}  
**中断时间：** YYYY-MM-DD HH:mm:ss  
**中断原因：** {interrupt_reason}  
**迭代进度：** {iter_id} — 已完成 N/M 个任务  
**Session ID：** {session_id}（仅作追溯，不用于会话恢复）

---

## 2. Git 状态快照

**提交 SHA：** `{git_sha}`  
**分支：** `{git_branch}`  
**Git Tag：** `checkpoint/{ckpt_id}`  

**本次中断前变更的文件：**
```
{modified_files_list}
```

**恢复 Git 状态命令：**
```bash
git reset --hard checkpoint/{ckpt_id}
# 或
git checkout -b restore/{ckpt_id} checkpoint/{ckpt_id}
```

---

## 3. 迭代状态快照

> 以下为中断时 current_iter.md 的完整内容副本

```markdown
{iter_summary_full_text}
```

---

## 4. 已完成任务

| 任务 ID | 描述 | 状态 | 关键文件 |
|---------|------|------|---------|
| task-1  | …    | ✅   | src/… |
| task-2  | …    | 🔄 进行中 | src/… |

---

## 5. 中断时的问题与修复记录

> 记录中断前的错误、尝试过的修复方案、已知结论

```
{pending_issues_and_fixes}
```

---

## 6. 待完成事项

> 恢复后需要立即处理的任务

- [ ] {pending_item_1}
- [ ] {pending_item_2}
- [ ] …

---

## 7. 重建 Prompt 包（RESUME_CONTEXT）

> ⚠️ 这是恢复 Agent Session 的核心。将此块完整粘贴/注入到新 Session 的第一条消息。

```
═══════════════════════════════════════════════════════
RESUME_CONTEXT — spec-driven-dev 会话恢复包
Checkpoint ID : {ckpt_id}
恢复时间      : {restore_timestamp}
═══════════════════════════════════════════════════════

## 你正在做什么

你是 spec-driven-dev Agent，正在处理用户故事 {us_id}。
你在 {stage} 阶段中断，中断原因：{interrupt_reason}。

当前 Git 分支：{git_branch}（代码已通过 git reset 恢复到中断时状态）

## 已完成的工作

{completed_tasks_summary}

## 中断时的状态

{interrupt_state_detail}

## 遇到的问题与已尝试的修复

{issues_and_fixes_summary}

## 接下来你需要做的

1. {next_action_1}
2. {next_action_2}
3. 继续从 {stage} 阶段的第 {resume_step} 步开始执行

## 关键文件状态

{key_files_status}

## 当前迭代摘要（来自 current_iter.md）

{iter_summary_condensed}

═══════════════════════════════════════════════════════
END RESUME_CONTEXT
恢复后请立即输出：[RESUMED FROM {ckpt_id}] 确认收到上下文
═══════════════════════════════════════════════════════
```

---

## 8. 补充上下文

{extra_context}
````

---

## Checkpoint 索引模板

文件路径：`requirements/{us_id}/docs/checkpoints/index.md`

```markdown
# Checkpoint 索引 — {us_id}

| Checkpoint ID | 创建时间 | 阶段 | 迭代 | 中断原因 | Git SHA | 状态 |
|--------------|---------|------|------|---------|---------|------|
| ckpt-… | … | coding | iter_003 | 测试失败 | a3f8b21c | ACTIVE |
| ckpt-… | … | bugfix | iter_003 | 手动保存 | 9c2e441a | ROLLED_BACK |
```

状态值：`ACTIVE`（可用）/ `ROLLED_BACK`（已被回滚到此点）/ `SUPERSEDED`（已有更新 checkpoint）

---

## 操作二：Rollback

### 命令格式

```
rollback {ckpt_id}
rollback {ckpt_id} --git-only
rollback {ckpt_id} --context-only
```

### 执行步骤

#### Step R-0 — 读取 Checkpoint 文档

读取 `requirements/{us_id}/docs/checkpoints/{ckpt_id}.md`，提取所有元数据字段。

若文档不存在，输出：
```
[SKILL:spec-driven-checkpoint] ERROR  checkpoint {ckpt_id} 不存在
请通过 list_checkpoints-{us_id} 查看可用的 checkpoint。
```

#### Step R-1 — 安全检查

```bash
# 检查当前工作区是否有未保存的变更
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "⚠️  当前工作区有未提交变更，回滚前将自动保存新 checkpoint"
  # 自动触发 save_checkpoint，保存当前状态后再回滚
fi
```

#### Step R-2 — Git 回滚（`--git-only` 或默认）

```bash
# 方式一：硬重置（在当前分支上回滚，会覆盖后续提交）
git reset --hard "checkpoint/{ckpt_id}"

# 方式二（推荐用于生产）：创建新分支，保留历史
git checkout -b "restore/{ckpt_id}-$(date +%Y%m%d%H%M%S)" \
             "checkpoint/{ckpt_id}"
```

> 默认使用方式二（创建新恢复分支），保留原有分支的完整历史。
> 用户可在恢复验证后决定是否合并或废弃原分支。

```
[SKILL:spec-driven-checkpoint] CHECKPOINT git_restored STATUS=OK
  branch=restore/{ckpt_id}-{ts}  sha={git_sha}
```

#### Step R-3 — 状态文件回滚（`--git-only` 时跳过）

将 checkpoint 文档中「迭代状态快照」节的内容写回 `current_iter.md`：

```bash
# 从 checkpoint 文档第 3 节提取快照内容，覆写 current_iter.md
cp requirements/{us_id}/docs/checkpoints/{ckpt_id}.md \
   /tmp/ckpt_iter_snapshot.md
# 提取 ## 3 节内容 → 写入 current_iter.md
```

#### Step R-4 — 更新索引

将 checkpoint 索引中该条目状态更新为 `ROLLED_BACK`，并在后面添加回滚时间戳。

#### Step R-5 — 输出重建 Prompt（`--git-only` 时跳过）

从 checkpoint 文档的第 7 节（RESUME_CONTEXT）提取完整内容，输出到终端：

```
════════════════════════════════════════════════════
以下为 RESUME_CONTEXT，请将其作为新 Session 的首条消息：
════════════════════════════════════════════════════

{resume_context_block}

════════════════════════════════════════════════════
Git 已恢复到分支：restore/{ckpt_id}-{ts}
当前 HEAD：{git_sha}
请在新 Session 中粘贴上方 RESUME_CONTEXT 后继续工作。
════════════════════════════════════════════════════
```

```
[SKILL:spec-driven-checkpoint] CHECKPOINT rollback_done STATUS=OK  id={ckpt_id}
```

---

## 操作三：列出 Checkpoints

```
list_checkpoints-{us_id}
```

读取 `requirements/{us_id}/docs/checkpoints/index.md` 并格式化输出：

```
Checkpoints for {us_id}
────────────────────────────────────────────────────────
ID                              时间              阶段     迭代      状态
ckpt-20240115-143022-a3f8b21c  2024-01-15 14:30  coding   iter_003  ACTIVE ← 最新
ckpt-20240114-091547-9c2e441a  2024-01-14 09:15  bugfix   iter_002  SUPERSEDED
────────────────────────────────────────────────────────
共 2 个 checkpoint。使用 rollback {id} 恢复。
```

---

## 与 spec-driven-dev 的集成协议

`spec-driven-dev` 在以下时机调用本 Skill：

| 时机 | 触发条件 | 传入参数 |
|------|---------|---------|
| 自动保存 | `bugfix` 阶段同一问题修复失败 ≥ 3 次 | `interrupt_reason: "bugfix_loop_N"` |
| 自动保存 | `code_review` 返回 `REQUEST_CHANGES` | `interrupt_reason: "review_rejected"` |
| 自动保存 | 任意阶段连续 FAIL ≥ 3 次 | `interrupt_reason: "stage_fail_N"` |
| 手动保存 | 用户触发 `save_checkpoint-{us_id}` | `interrupt_reason: "manual"` |
| 自动保存 | `release` 前最后保障 | `interrupt_reason: "pre_release"` |

调用格式：
```
invoke_skill: spec-driven-checkpoint
action: save
with:
  us_id: "{us_id}"
  iter_id: "{iter_id}"
  stage: "{current_stage}"
  interrupt_reason: "{reason}"
  pending_items: "{pending_description}"
  context: "{context}"
```

---

## 禁止行为

- 禁止在 rollback 后自动修改源代码文件，只做 git 操作和文档更新。
- 禁止在 checkpoint 文档中记录 `SPEC_DEV_GIT_TOKEN` 或任何凭据。
- 禁止删除 ROLLED_BACK 状态的 checkpoint 文档，保留完整历史。
- 禁止在无 `git tag` 支持的环境中静默跳过打标签步骤，应报告并暂停。
- 禁止在工作区有未保存变更时直接执行 rollback，必须先自动保存当前状态。
