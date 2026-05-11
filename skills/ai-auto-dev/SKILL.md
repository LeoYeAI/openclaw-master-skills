---
name: ai-auto-dev
description: "AI全自动化编程,Claude Code作为项目经理指挥Builder自动完成编程任务(需求对齐→指令生成→自动执行→验收→文档归档暂存)"
---

# AI 全自动化编程 (ai-auto-dev) v2.2

Claude Code 作为项目经理，Builder 作为执行者的全自动化编程流程。

> **v2.2 更新**（2026-02-22）：新增中断恢复机制（FlowPilot 启发）、依赖图自动分析（替代手动 [P] 标记）

---

## 前置条件

选择一个 Builder（AI 编程执行工具），推荐以下任一：

| Builder | 安装 | 执行命令 |
|---------|------|---------|
| Codex CLI | `npm i -g @openai/codex` | `codex exec --skip-git-repo-check "$(cat spec.md)"` |
| Claude Code | 已内置 | 直接在对话中执行 |
| Aider | `pip install aider-chat` | `aider --message "$(cat spec.md)"` |

**关键要求**：Builder 必须有完整文件系统访问权限，能执行 npx/node/tsc 等命令。

以 Codex 为例，`~/.codex/config.toml` 需配置：
```toml
ask_for_approval = "never"
sandbox_mode = "danger-full-access"
```

> ⚠️ **重要**：必须使用完整访问权限模式，受限模式会阻止 npx/node/tsc 等命令，导致三重纠错无法执行，Token 浪费 60%。

---

## 工作流程

### 第零步：会话暖场（每次必做）

**目的**：建立 Claude Code 会话信任，避免后续 Bash 后台任务需要确认

**操作**：
```bash
echo "Warmup at $(date '+%Y-%m-%d %H:%M:%S')" && sleep 2 && echo "Ready"
```

**要求**：
- 每次调用 `/ai-auto-dev` 都必须先执行暖场
- 使用 `run_in_background: true` 参数
- 等待完成通知（约 2-3 秒）
- 完成后进入第一步

**原理**：
- Claude Code 的会话信任机制存储在内存中
- 重启电脑后会清除，需要重新建立
- 首次后台任务需要确认，后续任务无需确认
- 暖场任务快速完成（<5 秒），建立信任后一整天无需确认

---

### 第一步：需求对齐

1. 用户提出需求
2. Claude Code 与用户反复讨论，直到完全理解
3. Claude Code **复述需求**给用户确认，必须包含：
   - **要做什么**：功能描述
   - **技术栈和约束**：语言、框架、依赖
   - **目录结构**：文件放在哪里
   - **交付物清单**：具体的文件名列表
   - **测试要求**：需要什么样的测试
4. 用户确认后才进入下一步
5. **禁止跳过此步**：需求不清就开始执行 = 浪费 Token

---

### 第二步：生成 Spec MD

**使用新模板**（v2.0 核心改进）：

1. 复制 `specs/SPEC-TEMPLATE.md` 为 `specs/TASK-{id}-{name}.md`
2. 参考 `specs/SPEC-TEMPLATE-GUIDE.md` 填写
3. Spec 必须包含以下 5 个核心改进：

#### 改进 1：NEEDS CLARIFICATION 机制
- 最多 3 个问题（优先级：范围 > 安全/隐私 > 用户体验 > 技术细节）
- 其他不确定的地方用假设替代，记录在 `## Assumptions` 章节
- 格式：`[假设: 具体内容]`
- **价值**：减少执行时的犹豫，消除"猜测-验证"循环

#### 改进 2：User Stories 结构
```markdown
### US1: 功能名称 (Priority: P1)
作为[角色]，我需要[功能]，以便[价值]。

**Acceptance Scenarios:**
- **Given** [前置条件]，**When** [操作]，**Then** [预期结果]

**Test Criteria:**
- [ ] {具体可测试的标准}
```

#### 改进 3：[P][US] 标记
- `[P]` = 可与其他 [P] 步骤并行执行
- `[US1][US2]` = 关联到对应用户故事
- 格式：`### Step 1: 创建模块 [P] [US1]`

#### 改进 4：Self-Check Requirements（三重纠错）
Spec 中必须包含此章节，Builder 执行后强制运行：

```markdown
## Self-Check Requirements (MANDATORY)

### Check 1: Static Analysis
```bash
npx tsc --noEmit --strict --skipLibCheck
```

### Check 2: Test Execution
```bash
npm test  # 或 jest / vitest --run
```

### Check 3: Build Verification
```bash
npm run build
```

### Check 4: Generate self-check-report.md
创建 {output-dir}/self-check-report.md，包含：
- Static Analysis: PASS/FAIL + 错误数
- Tests: PASS/FAIL + 通过/失败数
- Build: PASS/FAIL
- Files Created: 列表
- Issues Found: 列表
- Overall: PASS/FAIL

### Check 5: Reflection（如果失败）
如果任何检查失败：
1. 分析失败原因
2. 生成修复建议
3. 报告给 PM
```

#### 改进 5：Verification Checklist
```markdown
## Verification Checklist

### Code Quality
- [ ] TypeScript 编译无错误
- [ ] 所有测试通过
- [ ] 无 console.log 残留

### Functional Requirements (US1)
- [ ] {US1 的具体需求}

### Functional Requirements (US2)
- [ ] {US2 的具体需求}

### Edge Cases
- [ ] 空输入处理
- [ ] 边界值处理

### Security & Performance
- [ ] 无安全漏洞
- [ ] 无性能瓶颈
```

**任务拆解原则**：
- 每个任务 3-5 个相关函数
- 单个文件不超过 200 行
- 任务间无依赖
- 使用英文编写 Spec（Builder 对英文理解更精确）

**展示 Spec 给用户确认后进入第三步。**

---

### 第三步：执行

#### 3a. 中断恢复检测（v2.2 新增，每次进入第三步前必做）

**目的**：如果上次会话中途中断（compact、崩溃、关窗口），自动从断点续接。

**状态文件**：`{项目目录}/.codex-progress.json`

```json
{
  "session_id": "2026-02-22-001",
  "tasks": [
    {"id": "001", "spec": "specs/TASK-001.md", "status": "done", "token": 125000},
    {"id": "002", "spec": "specs/TASK-002.md", "status": "active", "token": 0},
    {"id": "003", "spec": "specs/TASK-003.md", "status": "pending", "token": 0}
  ],
  "updated_at": "2026-02-22 10:30:00"
}
```

**检测逻辑**（PM 在第三步开始前执行）：

```bash
# 检查是否有未完成的进度文件
if [ -f ".codex-progress.json" ]; then
  echo "检测到中断的任务进度："
  cat .codex-progress.json
fi
```

**恢复规则**：
1. 状态为 `done` 的任务：跳过，不重复执行
2. 状态为 `active` 的任务：重置为 `pending`，重新执行（active 表示执行中被中断，结果不可信）
3. 状态为 `pending` 的任务：正常执行
4. 状态为 `failed` 的任务：分析原因后决定重试或跳过

**更新时机**：
- 每个任务**启动前**：设为 `active`，写入文件
- 每个任务**完成后**：设为 `done`，记录 token，写入文件
- 每个任务**失败后**：设为 `failed`，记录错误，写入文件
- 全部完成后：删除进度文件

**PM 更新进度的命令**：
```bash
# 用 Python 更新进度文件（比 jq 可靠）
python3 -c "
import json
with open('.codex-progress.json', 'r') as f: data = json.load(f)
for t in data['tasks']:
    if t['id'] == '${TASK_ID}': t['status'] = '${NEW_STATUS}'
data['updated_at'] = '$(date '+%Y-%m-%d %H:%M:%S')'
with open('.codex-progress.json', 'w') as f: json.dump(data, f, indent=2)
"
```

#### 3b. 依赖图自动分析（v2.2 新增，替代手动 [P] 标记）

**目的**：PM 不再手动标记 `[P]`，而是自动分析任务间依赖关系，生成并行分组。

**分析规则**（PM 在生成所有 Spec 后执行）：

1. **提取每个任务的文件目标**：从 Spec 中提取 `Files to Create/Modify` 列表
2. **构建依赖图**：如果任务 B 要修改的文件是任务 A 要创建的文件，则 B 依赖 A
3. **拓扑排序**：按依赖关系分层，同层任务可并行
4. **输出分组**：

```
依赖分析结果：
  Layer 1 (并行): TASK-001, TASK-003, TASK-005  ← 无依赖，同时启动
  Layer 2 (并行): TASK-002, TASK-004            ← 依赖 Layer 1 的输出
  Layer 3 (串行): TASK-006                      ← 集成任务，依赖全部
```

**PM 执行依赖分析的命令**：
```bash
# 从所有 Spec 中提取文件目标，分析依赖
for spec in specs/TASK-*.md; do
  TASK_ID=$(basename "$spec" .md | sed 's/TASK-//')
  # 提取 Files to Create/Modify 章节中的文件路径
  FILES=$(grep -A 20 "Files to Create\|Files to Modify" "$spec" | grep '^\s*-\s*`' | sed 's/.*`\(.*\)`.*/\1/')
  echo "TASK-$TASK_ID: $FILES"
done
```

**与分层引爆模型的关系**：
- 旧方式：PM 手动标记 `[P]` → 分组 → 分层引爆
- 新方式：PM 自动分析依赖 → 自动分层 → 分层引爆
- 分层引爆模型（A→B→C）不变，只是分组不再需要人工判断

---

#### 3c. 执行任务

1. 创建工作目录（如有必要）
2. 将 Spec MD 传递给 Builder：
```bash
builder exec --skip-git-repo-check "$(cat specs/TASK-{id}-{name}.md)" > logs/task-{id}.log 2>&1 &
```
3. 根据任务数量选择执行模式
4. **启动主动监控**：自动检测任务完成，无需等待明确信号
5. 任务完成后自动进入第四步验收

**分层引爆模型（A→B→C）**：

```
A1（主引线）：暖场 + 任务分组
  ↓ 串联触发（快速，<5秒）
B1 ── B2 ── B3（二级引线，各组并行启动）
↓      ↓      ↓
C1    C2    C3（组内任务，并行执行）
```

- **A1**：第零步暖场完成后，将所有任务按依赖关系分组
- **B层**：每组作为独立批次，各组同时启动（`execute_batch` 并行调用）
- **C层**：每组内任务全部并行执行（`builder exec ... &`）

**分组原则**：
- 同组任务：操作不同文件、无依赖 → 可完全并行（C层）
- 跨组依赖：B1 组完成后才启动 B2 组 → 串联
- 组内上限：每组最多 15 个任务

**并发规则（15 并发标准）**：
- **标准配置**：每批 15 个任务并行执行
- **核心原则**：一次串流不超过 15 个
- **执行模式**：真·并行（所有任务同时启动）
- **性能保证**：~30 秒/15 任务，100% 成功率，无 API 限流

**并行执行前提条件**：
1. 会话信任已建立（第零步暖场完成）
2. 任务间无依赖（每个任务可独立完成）
3. 资源不冲突（不同任务操作不同文件）
4. 并发数量控制（最多 15 个任务同时执行）

**执行脚本模板**：
```bash
# 15并发真·并行模式
BATCH_SIZE=15
TOTAL_TASKS=<任务总数>
BATCH_COUNT=$(( (TOTAL_TASKS + BATCH_SIZE - 1) / BATCH_SIZE ))

mkdir -p logs

execute_batch() {
    local BATCH_ID=$1
    local START_TASK=$2
    local END_TASK=$3

    echo "[批次${BATCH_ID}] 启动任务 ${START_TASK}-${END_TASK}"

    for i in $(seq $START_TASK $END_TASK); do
        TASK_NUM=$(printf '%03d' $i)
        builder exec --skip-git-repo-check "$(cat specs/TASK-${TASK_NUM}.md)" \
            > "logs/task-${TASK_NUM}.log" 2>&1 &
    done

    wait
    echo "[批次${BATCH_ID}] 完成"
}

TASK_ID=1
for batch in $(seq 1 $BATCH_COUNT); do
    START_TASK=$TASK_ID
    END_TASK=$((TASK_ID + BATCH_SIZE - 1))
    if [ $END_TASK -gt $TOTAL_TASKS ]; then
        END_TASK=$TOTAL_TASKS
    fi
    execute_batch $batch $START_TASK $END_TASK &
    TASK_ID=$((END_TASK + 1))
done

wait
```

**扩展策略**：
- 任务数 ≤ 15：单批次执行（最快）
- 任务数 16-50：分批执行，每批 15 个（推荐）
- 任务数 > 50：分批执行，每批 15 个（稳定）

**主动监控机制**：

```bash
monitor_codex_execution() {
    local LOG_FILE=$1
    local TARGET_FILE=$2
    local STABLE_COUNT=0
    local LAST_SIZE=0

    while true; do
        if [ -f "$LOG_FILE" ]; then
            CURRENT_SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null)

            if [ "$CURRENT_SIZE" -eq "$LAST_SIZE" ]; then
                STABLE_COUNT=$((STABLE_COUNT + 1))
                if [ $STABLE_COUNT -ge 4 ]; then
                    echo "✅ 日志稳定，任务可能已完成"
                    if [ -f "$TARGET_FILE" ]; then
                        FILE_TIME=$(stat -f%m "$TARGET_FILE" 2>/dev/null || stat -c%Y "$TARGET_FILE" 2>/dev/null)
                        CURRENT_TIME=$(date +%s)
                        TIME_DIFF=$((CURRENT_TIME - FILE_TIME))
                        if [ $TIME_DIFF -lt 300 ]; then
                            echo "✅ 目标文件已更新，触发验证"
                            return 0
                        fi
                    fi
                fi
            else
                STABLE_COUNT=0
                LAST_SIZE=$CURRENT_SIZE
            fi
        fi
        sleep 30
    done
}
```

**监控策略**：
- 检查频率：每 2 分钟（经验证为最优频率）
- 监控成本：约占总 Token 的 0.9%（极低，不是优化重点）
- 监控目的：发现"卡死"或"完全无法执行"，不是催促进度

---

### 第四步：自动验收（三重纠错）

Builder 完成后，Claude Code **自动**执行以下检查（无需用户确认）：

#### 第一层：读取 Builder 的 Self-Check Report

```bash
cat {output-dir}/self-check-report.md
```

报告包含：
- Static Analysis: PASS/FAIL + 错误数
- Test Results: PASS/FAIL + 通过/失败数
- Build Results: PASS/FAIL
- Files Created/Modified: 列表
- Issues Found: 列表
- Overall Assessment: PASS/FAIL

#### 第二层：PM 验证（如果 Self-Check 通过）

1. **文件完整性**（必须实际验证，不能只看日志）
   - 检查所有预期文件是否生成：`ls -lh [目标路径]`
   - 检查空文件：`find [目标路径] -name "*.ts" -size 0`
   - 统计代码行数：`wc -l [目标路径]/*.ts`
   - ⚠️ **必须用 ls 实际确认文件存在，不能只看 Builder 输出**

2. **代码质量**（抽查）
   - 读取 1-2 个关键文件，检查：类型注解、文档字符串、错误处理

3. **Verification Checklist 验证**
   - 根据 Spec 中的 Verification Checklist，逐项验证
   - 重点检查 Functional Requirements 和 Edge Cases

#### 第三层：反思机制（如果 Self-Check 失败）

1. **分析失败原因**
   - 读取 self-check-report.md 中的 Issues Found
   - 分类：语法错误、类型错误、测试失败、构建失败、权限问题

2. **生成修复建议**
   - Spec 不清晰 → 修改 Spec，重新执行
   - Builder 理解错误 → 调整 Spec 描述，重新执行
   - 环境问题（权限/依赖）→ 修复环境，重新执行

3. **决策**
   - 自动修复（简单问题）
   - 报告给 Boss（需要需求澄清）
   - 重新执行（Spec 已修改）

#### PM-Builder 信任原则

**继续信任 Builder 的标志**：
- Builder 还在尝试不同方案（输出中可以看到不同的思考和尝试）
- Token 使用量稳定增长（说明 Builder 在工作，不是卡死）
- 错误类型在变化（说明 Builder 在调整策略）
- 执行时间在合理范围内（简单任务 <5 分钟，复杂任务 <30 分钟）

**需要介入的标志**：
- Builder 陷入循环报错（相同错误重复出现 3 次以上）
- Builder 完全卡死（超过 5 分钟无任何输出）
- Token 使用量异常增长（单任务超过 500 万 tokens）
- 执行时间明显异常（简单任务超过 30 分钟）

**介入方式**：
1. 先检查 Builder 的最新输出，确认是否真的需要介入
2. 如果确认需要介入，停止任务并分析原因
3. 修改 Spec 或指令，重新执行
4. 记录踩坑经验，更新记忆库

#### 难度分级标准（A1）

| 级别 | 预期时间 | 预期 Token | 介入次数 | 典型场景 |
|------|---------|-----------|---------|---------|
| 简单 | ≤5 分钟 | ≤500K | 0 | 单文件修改、配置调整、小功能 |
| 复杂 | ≤30 分钟 | ≤5M | 0-1 | 多文件功能、重构、新模块 |

**超阈值判定**：实际值 > 2× 预期值 → 标记异常，写入实验日志，分析原因。

#### 死循环 vs 正常思考（A2）

| 状态 | 判断依据 |
|------|---------|
| 正常思考 | 输出内容在变化 OR 错误类型在变化 OR Token 稳定增长 |
| 死循环 | 相同错误 ≥3 次 AND Token 持续增长但无新进展 |
| 完全卡死 | 超过 5 分钟无任何输出 |

**数学条件**：`相同错误出现次数 ≥ 3` → 立即介入，不等待。

#### 生成最终验收报告（内联显示，不要只给文件链接）

```
## 验收报告

### 执行统计
**时间消耗：**
- 实际执行时间：X 分钟
- 总墙上时钟时间：Y 分钟
- 串行预估时间：Z 小时（如适用）
- 效率提升：N%（如适用）

**Token 消耗：**
- Spec 生成（PM）：XXK tokens
- Builder 执行（Builder）：XXM tokens
- PM 验证：XXK tokens
- **总计：X.XM tokens**

**成本效益：**
- 人工开发预估：X-Y 天
- 自动化完成：Z 分钟

### Builder Self-Check 结果
- Static Analysis: ✅ PASS / ❌ FAIL (X errors)
- Test Results: ✅ PASS / ❌ FAIL (X/Y passed)
- Build Results: ✅ PASS / ❌ FAIL
- Overall: ✅ PASS / ❌ FAIL

### PM 验证结果
- 文件完整性: ✅ / ❌
- 代码质量: ✅ / ❌
- Verification Checklist: X/Y 项通过

### 文件清单
| 文件 | 大小 | 行数 | 状态 |
|------|------|------|------|

### 判定：✅ 通过 / ❌ 不通过
- 不通过原因（如有）
- 修复建议（如有）
```

---

### 第五步：文档归档暂存

1. 在工作目录下创建 `_archive_staging.md` 暂存文件
2. **不写入**正式文档（思维蒸馏、学习研究日志、记忆库等）
3. 暂存文件包含本次工作中所有值得记录的内容

**暂存文件格式**：
```markdown
# 文档归档暂存

> 创建日期：YYYY-MM-DD
> 项目：[项目名称]
> 任务：[任务描述]
> 状态：待用户审阅

---

## 蒸馏内容
[本次工作中值得提炼的方法论、认知、经验]

---

## 日志内容
[本次工作的完整记录，按学习研究日志的会话格式编写]

---

## 踩坑记录
[遇到的问题和解决方案]

---

## 记忆库更新建议
[如有新的操作习惯或规则需要记录]
```

---

### 第五步半：文档更新和 GitHub 同步（自动执行）

**在第六步交付前，自动完成以下工作**：

1. **更新项目文档**
   - 更新 README.md（功能介绍、版本号）
   - 更新 CHANGELOG.md（新增版本记录）
   - 更新 API 配置指南或其他相关文档

2. **调用 dev-log skill**
   - 传入版本号参数（如 `v0.9.4`）
   - dev-log 自动完成：分析代码修改、生成 commit message、提交代码、打版本标签、推送到 GitHub

3. **验证同步结果**
   - 确认 commit 成功
   - 确认标签已创建
   - 确认推送到远程仓库

**注意**：此步骤在第五步之后、第六步之前自动执行，无需用户确认。如果 GitHub 同步失败，记录错误但继续交付流程。

---

### 第六步：向用户交付

同时交付三样东西（**全部内联显示在对话中，不要只给文件链接**）：

1. **验收报告**（第四步生成的）
   - 通过/不通过判定
   - 文件清单和测试结果
   - 问题清单（如有）

2. **归档暂存文件**（第五步生成的）
   - 展示内容供用户审阅
   - 说明每部分建议写入哪个正式文档

3. **GitHub 同步结果**（第五步半完成的）
   - Commit ID 和链接
   - 版本标签
   - GitHub Release 链接

4. 用户审阅后决定：
   - 确认收纳 → 调用 `/distill` 或手动写入正式文档
   - 需要修改 → 修改后再收纳
   - 不收纳 → 暂存文件保留在工作目录备查

---

## Token 消耗统计方法

### 从 Builder 日志提取 Token 数据

```bash
# 提取单个任务的 Token 消耗
extract_tokens() {
    local LOG_FILE=$1
    grep "Usage:" "$LOG_FILE" | tail -1 | \
        sed -E 's/.*input=([0-9]+) output=([0-9]+) total=([0-9]+).*/\1 \2 \3/'
}

# 统计所有任务的 Token 消耗
total_input=0; total_output=0; total_tokens=0

for log in logs/task-*.log; do
    read input output total <<< $(extract_tokens "$log")
    total_input=$((total_input + input))
    total_output=$((total_output + output))
    total_tokens=$((total_tokens + total))
done

echo "Total Input: ${total_input}"
echo "Total Output: ${total_output}"
echo "Total Tokens: ${total_tokens}"
```

### Token 消耗异常分析

| 现象 | 原因 | 修复 |
|------|------|------|
| 单任务 >500K tokens | 权限不足，陷入探测循环 | 改为 danger-full-access |
| 单任务 >500K tokens | Spec 不清晰，反复猜测 | 补充 Assumptions，明确需求 |
| PM Token 过高 | 读取了不必要的文件 | 遵守"PM 不读代码"原则 |
| 总 Token 超预期 | 重复执行失败任务 | 先修复 Spec 再重新执行 |

---

## 核心规则

1. **每次必须暖场**：第零步不可跳过，每次调用都要执行暖场
2. **需求不清不动手**：第一步必须完成，复述确认后才进入第二步
3. **必须使用新 Spec 模板**：第二步必须使用 `specs/SPEC-TEMPLATE.md`，包含 5 个核心改进
4. **Spec 必须自包含**：Builder 无需额外信息即可完成全部工作
5. **三重纠错强制执行**：Builder 必须运行 Self-Check Requirements，生成 self-check-report.md
6. **全程自动化**：从第一步确认到第六步交付，PM 自动完成所有步骤，不在中途停下等待用户
7. **正式文档只读**：整个流程中不直接写入蒸馏、日志、记忆库
8. **归档只能暂存**：❗❗❗ 只能创建 `_archive_staging.md` 暂存文件，绝对不能直接写入正式文档
9. **验收必须实际验证**：必须用 `ls` 实际确认文件存在，不能只看 Builder 输出就报告成功
10. **验收不通过时**：分析原因，修改 Spec 重新执行，不要手动修补代码
11. **报告内联显示**：验收报告必须内联显示在对话中，不要只给文件链接
12. **文档和 GitHub 同步自动化**：第五步半自动更新文档并同步到 GitHub，无需用户确认
13. **PM 只读输出文件**：验收时 PM 只读 `self-check-report.md`、`ls` 输出、日志文件。不读源码（.ts/.js/.py）。"不读代码"= 不读源码，不等于不读报告。

---

## 常见错误和修复方案

### 错误 1：sandbox 权限不足
**现象**：Builder 无法运行 npx/node/tsc，Token 消耗异常高（60% 浪费在权限探测）
**原因**：config.toml 中 `sandbox_mode = "workspace-write"`
**修复**：改为 `sandbox_mode = "danger-full-access"`
**验证**：`builder exec "echo hello"` 输出显示 `sandbox: danger-full-access`

### 错误 2：PM 未按完整流程执行
**现象**：PM 在中途停下等待用户指示，导致大量时间浪费
**原因**：误解了"全自动化"含义，认为需要在每个阶段询问用户确认
**修复**：执行完所有 6 步才交付，只有遇到无法解决的错误时才停下来
**数据**：错误做法导致 455 分钟空闲 vs 85 分钟工作，浪费比例 84%

### 错误 3：PM 混淆任务输出文件
**现象**：PM 报告任务成功，但文件根本不存在
**原因**：读取了错误的输出文件，没有实际验证文件是否存在
**修复**：必须用 `ls` 实际确认文件存在，必须运行编译检查才能声称编译通过

### 错误 4：报告只给文件链接
**现象**：用户反馈"不好找"，阅读体验差
**原因**：PM 过度关注 Token 成本优化
**修复**：默认内联显示所有报告
**决策标准**：成本差异 <1 元/100 轮 → 优先用户体验，内联显示

### 错误 5：过早介入 Builder
**现象**：PM 在 Builder 还在工作时停止任务，导致成本翻倍
**原因**：PM 用自己的时间预估判断 Builder 是否卡死
**修复**：按照"PM-Builder 信任原则"判断，只有满足"需要介入的标志"才介入

---

## 与其他 Skill 的配合

- **distill**：用户确认暂存内容后，可调用 `/distill` 写入正式蒸馏文档
- **sop-generator**：如果本次任务是新流程，可调用 `/sop-generator` 生成 SOP
- **dev-log**：如果涉及版本管理，可调用 `/dev-log` 记录版本

---

## Memory/RAG 实际落地（C2）

> **现实约束**：当前没有 Gemini/向量数据库，Memory 角色由 PM 用文件检索替代。

### 当前可用的"Memory"操作

| 需求 | 实际操作 | 命令 |
|------|---------|------|
| 查找相关文件 | Glob 模式匹配 | `Glob("src/**/*.ts")` |
| 搜索历史决策 | Grep 关键词 | `Grep("pattern", path)` |
| 读取基线数据 | Read 文件 | `Read("windtunnel/baselines/...")` |
| 查找踩坑记录 | Read 暂存文件 | `Read("_archive_staging.md")` |

### PM 查询 Memory 的正确姿势

```
❌ 错误：直接读 src/ 下的源码文件来"理解"项目
✅ 正确：读 self-check-report.md、CLAUDE.md、_archive_staging.md 获取上下文
✅ 正确：用 Glob/Grep 定位文件路径，把路径写进 Spec，让 Builder 去读
```

### Spec 中的 Memory 引用格式

```markdown
## 上下文（PM 查询 Memory 后填入）
- 相关文件：`src/taskManager.ts`（通过 Glob 定位）
- 历史决策：使用 danger-full-access（见 _archive_staging.md 权限进化历程）
- 已知问题：activationEvents 缺失（见 CLAUDE.md Section 6）
```

---

## 参考文档

- **Spec 模板**：`specs/SPEC-TEMPLATE.md`
- **填写指南**：`specs/SPEC-TEMPLATE-GUIDE.md`
- **Constitution**：`CLAUDE.md`（Section 3: Spec MD Format）
- **验证报告**：`automated-comparison-test/FINAL-COMPARISON-REPORT.md`（61.4% 效率提升数据）
- 记忆库中的「Builder CLI 使用规则」：config.toml 配置、指令-权限匹配原则
- SOP 暂存中的「权限进化历程」：7 阶段实验数据和踩坑经验
- 思维蒸馏中的「Claude Code + Builder 协作模式」：权限-效率-成本三角

---

## 记忆保护协议（v2.1 新增）

> **核心原则：重要信息必须立即落盘，不能只存在上下文中。**
> 上下文压缩会导致风洞数据失真——压缩后的"记忆"不等于真实发生的事情。

### 规则 1：会话开始时恢复上下文

每次新会话开始，PM 必须读取以下文件（按顺序）：

```
1. ~/.claude/windtunnel/baselines/ai-auto-dev-baseline.md  ← 基线数据
2. ~/.claude/windtunnel/experiments/{今日日期}-summary.md   ← 今日实验记录（如存在）
3. {项目目录}/CLAUDE.md                                    ← 项目约束
```

**目的**：从文件恢复上下文，而不是依赖对话历史（对话历史可能已被压缩）。

---

### 规则 2：实验数据立即落盘

以下数据必须在产生时**立即写入文件**，不能只存在对话中：

| 数据类型 | 写入位置 | 触发时机 |
|---------|---------|---------|
| 任务开始记录 | `windtunnel/experiments/{日期}-log.md` | 第三步执行前 |
| 验收结果 | `windtunnel/experiments/{日期}-log.md` | 第四步完成后 |
| 基线对比 | `windtunnel/baselines/ai-auto-dev-baseline.md` | 每次任务完成后 |
| 踩坑记录 | `_archive_staging.md` | 发现问题时立即记录 |

**实验日志格式**（追加写入，不覆盖）：

```markdown
## {时间戳} | 任务：{任务名} | 难度：简单/复杂

**输入**：{需求一句话描述}
**执行时间**：X 分钟
**Token 消耗**：X.XM
**介入次数**：X
**结果**：✅ PASS / ❌ FAIL
**偏差**：与基线相比 +/-X%（如有）
**备注**：{关键发现，一句话}
```

写入命令（PM 在第四步后执行）：
```bash
cat >> ~/.claude/windtunnel/experiments/$(date '+%Y-%m-%d')-log.md << 'EOF'
{上述格式内容}
EOF
```

---

### 规则 3：上下文压缩防护

**禁止**：将以下内容只放在对话中：
- 实验数据和测量结果
- 与基线的对比结论
- 决策记录（为什么选 A 不选 B）
- 踩坑经验

**要求**：每次任务完成后，PM 必须确认以上内容已写入文件，才能进入第六步交付。

---

### 规则 4：基线自动对比

每次任务完成后，PM 自动计算与基线的偏差并写入日志：

```
偏差计算：
- 时间偏差 = (实际时间 - 基线时间) / 基线时间 × 100%
- Token 偏差 = (实际Token - 基线Token) / 基线Token × 100%
- 偏差 > +50%：标记为异常，分析原因
- 偏差 < -20%：标记为改进，记录原因
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-02-15 | 初始版本，建立基础流程 |
| v2.0 | 2026-02-19 | 新增 Spec-Kit 改进（5 个核心机制）、三重纠错、PM-Builder 信任原则、Token 统计、常见错误修复方案 |
| v2.1 | 2026-02-21 | 新增记忆保护协议：立即落盘原则、实验日志格式、上下文压缩防护、基线自动对比 |
| v2.2 | 2026-02-22 | 新增中断恢复机制（`.codex-progress.json` 状态文件，active→pending 重置）、依赖图自动分析（替代手动 [P] 标记，自动拓扑排序分层） |
