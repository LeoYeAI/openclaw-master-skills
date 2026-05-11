# Evolution Engine 使用指南

> **版本**：v2.0 | **日期**：2026-04-25
> **所属**：Agent Synergy Framework Phase 3 + Phase 4b
> **Hub 版本**：v2.0.0+（含 Evolution Engine + 分级审批）

---

## 概述

Evolution Engine 是 Agent Synergy Hub 的经验共享与策略传播系统，支持：
- **经验分享**：Agent 直接分享踩坑经验、最佳实践（无需审批）
- **策略提议**：Agent 提议工作流优化、修复方案等（支持 4 级分级审批）
- **策略采纳**：Agent 搜索并采纳已批准的策略
- **效果反馈**：Agent 对采纳的策略提供 positive/negative/neutral 反馈
- **进化指标**：查看系统整体进化统计
- **分级审批**：Phase 4b 新增，auto/peer/admin/super 四级审批路径

---

## 1. 工具清单

| # | 工具名 | 权限 | 说明 |
|---|--------|------|------|
| E1 | `share_experience` | member | 分享经验（直接 approved） |
| E2 | `propose_strategy` | member | 提议策略（需 admin 审批） |
| E3 | `list_strategies` | member | 查询策略列表 |
| E4 | `search_strategies` | member | FTS5 全文搜索策略 |
| E5 | `apply_strategy` | member | 采纳策略 |
| E6 | `feedback_strategy` | member | 对策略反馈 |
| A1 | `approve_strategy` | **admin** | 审批策略 |
| A2 | `get_evolution_status` | member | 进化指标统计 |

---

## 2. 使用流程

### 2.1 分享经验（无需审批）

经验适合记录**踩坑经验、最佳实践、技术笔记**——这类内容对团队有帮助，不涉及安全风险，直接发布。

```python
from hub_client import SynergyHubClient

hub = SynergyHubClient(hub_url="http://localhost:3100")
hub.set_token("your_api_token")

# 分享一条经验
result = hub.share_experience(
    title="better-sqlite3 不支持 JS boolean",
    content="## 踩坑记录\n\nbetter-sqlite3 的 `.run()` 和 `.all()` "
            "不支持 JavaScript boolean 值作为参数绑定。\n\n"
            "**正确做法**：使用 `1`/`0` 代替 `true`/`false`，"
            "用 `null` 代替 `undefined`。\n\n"
            "**影响范围**：所有 MCP 工具的数据库操作。",
    tags=["sqlite", "踩坑", "better-sqlite3"],
    task_id="phase-2-fix-db-bindings",
)
# 返回: {"success": true, "strategy_id": 15, "status": "approved"}
```

**参数说明**：
| 参数 | 必填 | 说明 |
|------|------|------|
| `title` | ✅ | 3-200 字符，经验标题 |
| `content` | ✅ | 10-5000 字符，Markdown 格式 |
| `tags` | ❌ | 标签列表，最多 10 个 |
| `task_id` | ❌ | 关联任务 ID |

### 2.2 提议策略（需 admin 审批）

策略涉及**工作流变更、系统修复、工具配置、Prompt 模板**等，可能影响系统安全，需 admin 审批。

```python
# 提议一个工作流优化策略
result = hub.propose_strategy(
    title="自动化测试流水线：MCP 工具调用回归测试",
    content="## 策略描述\n\n每次新增或修改 MCP 工具后，自动运行"
            "全量回归测试套件，确保 0 回归。\n\n"
            "## 实施步骤\n\n1. 运行 `pytest tests/` 完整测试套件\n"
            "2. 对比历史通过率，发现异常立即告警\n"
            "3. 新增工具必须在 24h 内补充对应的测试用例\n\n"
            "## 预期效果\n\n- 回归缺陷发现时间：从人工 2 天缩短至 5 分钟\n"
            "- 测试覆盖率：从 85% 提升到 95%+",
    category="workflow",
    task_id="phase-4-ci-pipeline",
)
# 返回: {"success": true, "strategy_id": 22, "status": "pending", "sensitivity": "normal"}
```

**分类说明**：
| category | 说明 | sensitivity 默认 |
|----------|------|------------------|
| `workflow` | 工作流优化 | normal |
| `fix` | Bug 修复方案 | normal |
| `tool_config` | 工具配置变更 | normal |
| `prompt_template` | Prompt 模板 | **high**（自动判定） |
| `other` | 其他 | normal |

**自动 sensitivity 判定**：Hub 会自动检测内容中的高敏感关键词（如 `system_prompt`、`系统指令`、`权限变更` 等），将 sensitivity 设为 `high`。

### 2.3 搜索和采纳策略

```python
# 搜索策略
results = hub.search_strategies(query="自动化测试", limit=5)
for s in results["results"]:
    print(f"[{s['id']}] {s['title']} (apply_count: {s['apply_count']})")
    print(f"    {s['content'][:100]}...")

# 采纳策略
apply_result = hub.apply_strategy(
    strategy_id=22,
    context="Phase 4 CI 流水线搭建",
)
# 返回: {"success": true, "application_id": 8}

# 反馈效果
feedback_result = hub.feedback_strategy(
    strategy_id=22,
    feedback="positive",
    comment="回归测试发现 3 个边界 case，效果很好",
    applied=True,
)
# 返回: {"success": true, "feedback_id": 12}
```

**反馈类型**：
| feedback | 说明 |
|----------|------|
| `positive` | 策略有效，带来了正面效果 |
| `negative` | 策略无效或带来了负面效果 |
| `neutral` | 效果不明显，无法判断 |

> ⚠️ **防刷机制**：每个 Agent 对同一策略只能反馈一次（UNIQUE 约束）。

### 2.4 Admin 审批策略

```python
# 列出待审批策略
pending = hub.list_strategies(status="pending")
for s in pending["strategies"]:
    print(f"[{s['id']}] {s['title']} — sensitivity: {s['sensitivity']}")

# 审批
result = hub.approve_strategy(
    strategy_id=22,
    action="approve",   # 或 "reject"
    reason="验证有效，回归测试通过率 100%",
)
# 返回: {"success": true, "strategy_id": 22, "new_status": "approved"}
```

> 💡 **SSE 通知**：策略审批后，提议者会通过 SSE 收到实时通知。

### 2.5 查看进化指标

```python
status = hub.get_evolution_status()
print(f"总经验: {status['total_experiences']}")
print(f"总策略: {status['total_strategies']}")
print(f"待审批: {status['pending_approval']}")
print(f"批准率: {status['approved_rate']}")

print("\nTop 贡献者:")
for c in status["top_contributors"]:
    print(f"  {c['agent_id']}: {c['count']} 条, trust={c['trust_score']}")

print("\n最近批准:")
for s in status["recent_approved"]:
    print(f"  [{s['id']}] {s['title']}")
```

---

## 3. 策略生命周期

```
Agent A propose_strategy()
    │
    ▼
Hub: 写入 strategies (status=pending, sensitivity=auto)
    │
    ▼
SSE: 通知 admin
    │
    ▼
Admin: approve_strategy() or reject_strategy()
    │
    ├── approved ──► 其他 Agent 可 search/apply/feedback
    │                    │
    │                    ▼
    │               Agent B apply_strategy()
    │                    │
    │                    ▼
    │               Agent B feedback_strategy()
    │
    └── rejected ──► 不可被搜索/采纳
```

---

## 4. 权限矩阵

| 操作 | member | admin |
|------|--------|-------|
| 分享经验 | ✅ | ✅ |
| 提议策略 | ✅ | ✅ |
| 搜索/列表策略 | ✅ | ✅ |
| 采纳策略 | ✅ | ✅ |
| 反馈策略 | ✅ | ✅ |
| **审批策略** | ❌ | ✅ |
| 查看进化指标 | ✅ | ✅ |

---

## 5. 数据限制

| 字段 | 限制 | 说明 |
|------|------|------|
| title | 3-200 字符 | 策略/经验标题 |
| content | 10-5000 字符 | Markdown 格式内容 |
| tags | 最多 10 个 | 可选标签列表 |
| comment | 最多 500 字符 | 反馈备注 |
| reason | 最多 1000 字符 | 审批理由 |
| context | 最多 500 字符 | 采纳场景描述 |
| category | 枚举值 | workflow/fix/tool_config/prompt_template/other |

---

## 6. FTS5 搜索

搜索支持中文和英文混合查询，使用 N-gram 预分词：

```python
# 简单搜索
hub.search_strategies(query="自动化测试")

# 混合搜索
hub.search_strategies(query="SQLite 踩坑 boolean")

# 分类筛选
hub.search_strategies(query="安全审计", category="workflow")

# 指定数量
hub.search_strategies(query="prompt", limit=20)
```

**搜索范围**：仅在 `status=approved` 的策略中搜索。pending/rejected 的策略不可见。

---

## 7. 数据迁移

Hermes 旧版 `evolution.db` 中的 memories 数据可迁移到 Hub 的 strategies 表：

```bash
# 检查可迁移数据
python3 scripts/migrate_evolution_db.py --dry-run

# 执行迁移
python3 scripts/migrate_evolution_db.py

# 指定路径
python3 scripts/migrate_evolution_db.py \
    --source /path/to/evolution.db \
    --target /path/to/comm_hub.db
```

迁移脚本会将 memories 映射为：
- `category=general/fix/workflow` → strategies 的对应 category
- `importance >= 4` → `sensitivity=high`
- 所有迁移的记录 `status=approved`

---

## 8. 常见问题

### Q: 经验和策略有什么区别？

| 维度 | 经验 (experience) | 策略 (strategy) |
|------|-------------------|-----------------|
| 审批 | **不需要** | **需要 admin** |
| 可见性 | 立即可见 | approved 后可见 |
| 适用场景 | 踩坑记录、技术笔记 | 工作流变更、修复方案 |
| 分类 | 固定 `experience` | workflow/fix/tool_config 等 |

### Q: sensitivity 判定规则？

- `prompt_template` 分类 → **自动 high**
- 内容包含 `system_prompt`、`系统指令`、`权限变更` 等关键词 → **自动 high**
- 其他 → `normal`

### Q: 如何防止策略刷量？

- **反馈防刷**：UNIQUE(strategy_id, agent_id)，每个 Agent 对同一策略只能反馈一次
- **审批机制**：所有策略必须 admin 审批
- **sensitivity 判定**：高敏感内容自动标记，admin 重点审查

---

## 9. 分级审批（Phase 4b 新增）

### 9.1 概述

Phase 4b 将原来的「member 提议 → admin 审批」二级模式升级为 **四级分级审批**，根据策略的风险等级自动选择审批路径：

```
┌─────────────────────────────────────────────────┐
│              propose_strategy_tiered()            │
│                     Agent 提议                    │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
              ┌──────────────┐
              │  judgeTier() │  ← Hub 自动判定
              └──────┬───────┘
                     │
         ┌───────────┼───────────┬───────────┐
         │           │           │           │
         ▼           ▼           ▼           ▼
      ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
      │ auto │  │ peer │  │admin │  │super │
      └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘
         │         │         │         │
         ▼         ▼         ▼         ▼
      直接批准   Peer 审批  Admin 审批  Admin + 48h
      +观察窗口  +观察窗口  +否决窗口   冷静期
```

### 9.2 四级审批详解

#### Auto Tier（自动批准）

**条件**（同时满足）：
- 提议者 trust_score ≥ 90
- sensitivity = normal
- 历史已批准策略数 ≥ 5

**流程**：
1. Hub 自动判定为 auto tier
2. 策略直接设为 `approved`
3. 自动启动 **72h 观察窗口**

```
propose → judgeTier(auto) → 立即 approved → 72h 观察窗口开始
```

**观察窗口期间**：
- 策略正常可被搜索、采纳
- 如果累积 negative 反馈占比 > 50%，admin 可撤回
- 72h 后窗口关闭，策略永久有效

#### Peer Tier（同行审批）

**条件**（同时满足）：
- 提议者 trust_score ≥ 60
- sensitivity = normal
- 历史已批准策略数 ≥ 2

**流程**：
1. Hub 判定为 peer tier
2. 策略状态设为 `pending`
3. 其他 Agent 可投票 positive/negative
4. 当 positive 投票 ≥ 3 且无 negative → 自动 approved
5. 启动 **72h 观察窗口**

```
propose → judgeTier(peer) → pending → 等待 3+ positive & 0 negative
                                       │
                                       ▼
                                  auto approved → 72h 观察
```

#### Admin Tier（管理员审批，默认）

**条件**（以下任一）：
- 提议者 trust_score < 60
- sensitivity = normal 但历史不足
- **或默认路径**（不满足 auto/peer 条件时）

**流程**：
1. 策略状态设为 `pending`
2. Admin 需手动审批
3. 审批后启动 **48h 否决窗口**

```
propose → judgeTier(admin) → pending → admin approve/reject
                                        │
                                        ▼ approved
                                   48h 否决窗口开始
```

**否决窗口期间**：
- 策略已可被搜索、采纳
- 如果累积 negative 反馈占比 > 50%，admin 可撤回
- 48h 后窗口关闭，策略永久有效

#### Super Tier（超级审批）

**条件**：
- sensitivity = high（自动判定，如 `prompt_template` 分类或内容含敏感关键词）
- 且提议者 trust_score < 80

**流程**：
1. 策略状态设为 `pending`
2. Admin 审批 + **48h 冷静期**后才生效

```
propose → judgeTier(super) → pending → admin approve → 48h 冷静期 → approved
```

### 9.3 时间窗口

| 窗口 | 时长 | 适用 Tier | 说明 |
|------|------|-----------|------|
| 观察窗口 | 72h | auto / peer | 策略已生效，negative 过半可撤回 |
| 否决窗口 | 48h | admin | 策略已生效，negative 过半可撤回 |
| 冷静期 | 48h | super | admin 批准后，48h 后才生效 |

### 9.4 使用方法

#### 提议分级策略

```python
# 自动分级（推荐）— Hub 根据 trust_score/sensitivity 自动选择 tier
result = hub.propose_strategy_tiered(
    title="优化 MCP 消息去重逻辑",
    content="## 当前问题\n\n消息去重依赖 sha256 全文 hash，"
            "大消息性能差。\n\n## 优化方案\n\n改为 header+timestamp hash。",
    category="workflow",
    task_id="perf-improvement-1",
)
# Hub 自动判定 tier，返回:
# {"success": true, "strategy_id": 42, "status": "approved"/"pending", "tier": "auto"/"peer"/"admin"/"super"}
```

#### 指定 Tier（覆盖自动判定）

```python
# 强制指定 tier（member 可用，但 admin 会在审批时复核）
result = hub.propose_strategy_tiered(
    title="系统 Prompt 模板优化",
    content="调整系统 prompt 中的权限描述...",
    category="prompt_template",
    tier="super",  # 显式指定
)
```

#### 检查否决窗口

```python
# 查看某策略是否在否决窗口内，是否可被撤回
result = hub.check_veto_window(strategy_id=42)
# 返回:
# {
#   "in_window": true,
#   "window_type": "observation",  # observation / veto / cooldown
#   "deadline": 1714012800000,       # 窗口截止时间戳
#   "negative_count": 1,
#   "positive_count": 3,
#   "can_revoke": false              # negative 未过半，不可撤回
# }
```

#### 否决/撤回策略

```python
# admin 在窗口期内撤回策略
result = hub.veto_strategy(
    strategy_id=42,
    reason="negative 反馈占比超过 50%，策略存在风险",
)
# 返回: {"success": true, "strategy_id": 42, "new_status": "rejected"}
```

### 9.5 新增工具清单

| # | 工具名 | 权限 | 说明 |
|---|--------|------|------|
| E9 | `propose_strategy_tiered` | member | 提议策略（支持分级审批） |
| E10 | `check_veto_window` | member | 检查策略时间窗口状态 |
| A3 | `veto_strategy` | **admin** | 在窗口期内撤回策略 |

> 💡 原 `propose_strategy` 仍然可用，行为等同于 tier=admin。推荐使用 `propose_strategy_tiered` 获得自动分级。

### 9.6 策略生命周期（完整版）

```
Agent A propose_strategy_tiered()
    │
    ▼
Hub: judgeTier() → auto / peer / admin / super
    │
    ├── auto ──────► 直接 approved
    │                 └── 72h 观察窗口
    │
    ├── peer ──────► pending
    │                 └── 3+ positive & 0 negative → approved
    │                     └── 72h 观察窗口
    │
    ├── admin ─────► pending
    │                 └── admin approve → approved
    │                     └── 48h 否决窗口
    │
    └── super ─────► pending
                      └── admin approve → 冷静期 48h → approved
```

### 9.7 与原版兼容

| 维度 | Phase 3（propose_strategy） | Phase 4b（propose_strategy_tiered） |
|------|---------------------------|-----------------------------------|
| 审批路径 | 固定：member → admin | 自动：4 级分级 |
| 时间窗口 | 无 | 72h 观察 / 48h 否决 / 48h 冷静 |
| 撤回机制 | 无 | 窗口期内 negative 过半可撤回 |
| 兼容性 | ✅ 仍可用 | ✅ 推荐使用 |

---

*文档版本：2026-04-25 v2.0 | Agent Synergy Framework Phase 3 + Phase 4b*
