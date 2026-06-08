# ClawMoney Skill 完整实现方案

## 概述

ClawMoney 是一个推文赏金平台。本方案让 Claude Code 能通过 **bnbot MCP → bnbot 浏览器插件** 链路来浏览和执行赏金任务。

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Claude Code (CLI)                           │
│                                                                     │
│  ┌──────────────────────┐    ┌────────────────────────────────┐     │
│  │  clawmoney-skill     │    │  .mcp.json                     │     │
│  │  (SKILL.md)          │    │  mcpServers.bnbot → npx        │     │
│  │                      │    │  bnbot-mcp-server              │     │
│  │  触发词:             │    └───────────────┬────────────────┘     │
│  │  "bounty" "赏金任务"  │                    │                      │
│  └──────────┬───────────┘                    │                      │
│             │ 浏览任务                        │ MCP 协议              │
│             ▼                                ▼                      │
│  ┌──────────────────────┐    ┌────────────────────────────────┐     │
│  │  browse-tasks.sh     │    │  bnbot-mcp-server              │     │
│  │                      │    │                                │     │
│  │  curl API → python3  │    │  ┌──────────┐ ┌────────────┐  │     │
│  │  格式化输出           │    │  │ 导航工具  │ │ 发推工具    │  │     │
│  └──────────────────────┘    │  ├──────────┤ ├────────────┤  │     │
│                              │  │ 抓取工具  │ │ 互动工具 ★ │  │     │
│                              │  └──────────┘ └─────┬──────┘  │     │
│                              └─────────────────────┼─────────┘     │
└────────────────────────────────────────────────────┼────────────────┘
                                                     │ WebSocket
                                                     ▼
                              ┌────────────────────────────────┐
                              │  bnbot-Extension-New (浏览器)    │
                              │                                │
                              │  actionRegistry.ts             │
                              │    ├── LIKE_TWEET      ★       │
                              │    ├── RETWEET         ★       │
                              │    └── FOLLOW_USER     ★       │
                              │                                │
                              │  engagementActions.ts   ★      │
                              │    ├── likeTweetHandler         │
                              │    ├── retweetHandler           │
                              │    └── followUserHandler        │
                              └────────────────┬───────────────┘
                                               │ DOM 操作
                                               ▼
                              ┌────────────────────────────────┐
                              │  Twitter/X 页面                 │
                              │                                │
                              │  [data-testid="like"]     → 点赞│
                              │  [data-testid="retweet"]  → 转发│
                              │  [data-testid="*-follow"] → 关注│
                              └────────────────────────────────┘

★ = 本次新增
```

### 数据流程图

```
用户: "查看 ClawMoney 赏金任务"
          │
          ▼
┌─────────────────────┐     ┌─────────────────────────────┐
│ SKILL.md 触发       │     │ browse-tasks.sh              │
│ 匹配关键词 "赏金任务" ├────►│                              │
└─────────────────────┘     │ curl api.bnbot.ai/boost/search│
                            │         │                     │
                            │         ▼                     │
                            │ python3 格式化                 │
                            │   wei → token                 │
                            │   时间计算                     │
                            │   表格输出                     │
                            └──────────────┬──────────────────┘
                                           │
                                           ▼
                            ┌──────────────────────────────┐
                            │ 展示任务列表                   │
                            │ #  Reward     Actions   URL   │
                            │ 1  0.5 ETH   like,rt   x.com/│
                            │ 2  100 USDT  like,fol  x.com/│
                            └──────────────┬───────────────┘
                                           │
                            用户: "执行任务 1"
                                           │
                                           ▼
                    ┌──────────────────────────────────────┐
                    │         任务执行流程                   │
                    │                                      │
                    │  ① get_extension_status              │
                    │     └── 确认插件已连接 ✓              │
                    │                                      │
                    │  ② navigate_to_tweet                 │
                    │     └── 导航到推文页面                │
                    │         等待 2-3 秒                   │
                    │                                      │
                    │  ③ like_tweet                        │
                    │     └── 点击 [like] → 检查 [unlike]  │
                    │         等待 2-3 秒                   │
                    │                                      │
                    │  ④ retweet                           │
                    │     └── 点击 [retweet]               │
                    │         → 点击 [retweetConfirm]      │
                    │         等待 2-3 秒                   │
                    │                                      │
                    │  ⑤ reply (如需要)                     │
                    │     └── open_reply_composer           │
                    │         → fill_reply_text             │
                    │         → ⚠️ 用户确认                 │
                    │         → submit_reply                │
                    │         等待 2-3 秒                   │
                    │                                      │
                    │  ⑥ follow_user (如需要)               │
                    │     └── 点击 [*-follow]               │
                    │                                      │
                    │  ⑦ 汇报执行结果                       │
                    └──────────────────────────────────────┘
```

### 项目修改图

```
┌─ bnbot-Extension-New ─────────────────────────────────────┐
│                                                           │
│  services/actionRegistry.ts          [修改]               │
│    + LIKE_TWEET 定义                                      │
│    + RETWEET 定义                                         │
│    + FOLLOW_USER 定义                                     │
│    + 注册到 ActionRegistry                                │
│                                                           │
│  services/actions/engagementActions.ts [新建]              │
│    + likeTweetHandler                                     │
│    + retweetHandler                                       │
│    + followUserHandler                                    │
│                                                           │
│  services/actions/index.ts           [修改]               │
│    + import engagementHandlers                            │
│    + 注册到 allHandlers                                   │
│                                                           │
└───────────────────────────────────────────────────────────┘

┌─ bnbot-mcp-server ────────────────────────────────────────┐
│                                                           │
│  src/tools/engagementTools.ts        [新建]               │
│    + like_tweet    工具                                   │
│    + retweet       工具                                   │
│    + follow_user   工具                                   │
│                                                           │
│  src/tools/index.ts                  [修改]               │
│    + import registerEngagementTools                       │
│    + 调用注册                                             │
│                                                           │
└───────────────────────────────────────────────────────────┘

┌─ clawmoney ───────────────────────────────────────────────┐
│                                                           │
│  .mcp.json                           [新建]               │
│    { mcpServers: { bnbot: { ... } } }                     │
│                                                           │
└───────────────────────────────────────────────────────────┘

┌─ clawmoney-skill ─────────────────────────────────────────┐
│                                                           │
│  SKILL.md                            [新建] 主入口        │
│  scripts/browse-tasks.sh             [新建] API 查询      │
│  references/api-endpoints.md         [新建] API 文档      │
│  references/task-workflow.md         [新建] 执行流程      │
│  .claude-plugin/plugin.json          [新建] 元数据        │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### 涉及的项目

| 项目 | 路径 | 修改类型 |
|------|------|----------|
| bnbot-Extension-New | `/Users/jacklee/Projects/bnbot-Extension-New` | 新增 3 个 Action |
| bnbot-mcp-server | `/Users/jacklee/Projects/bnbot-mcp-server` | 新增 3 个 MCP 工具 |
| clawmoney | `/Users/jacklee/Projects/clawmoney` | 新增 `.mcp.json` |
| clawmoney-skill | `/Users/jacklee/Projects/clawmoney-skill` | 新建项目 |

---

## Part 1: bnbot-Extension-New — 新增 3 个 Action

### 修改文件

#### 1. `services/actionRegistry.ts`

在"发推类 Actions"和"复合 Actions"之间新增"互动类 Actions"分类：

```typescript
// ============================================
// 互动类 Actions
// ============================================

export const LIKE_TWEET: ActionDefinition = {
  id: 'like_tweet',
  name: 'Like Tweet',
  nameKey: 'actions.likeTweet',
  category: 'tweet',
  trigger: 'both',
  parameters: [],
  timeout: 10000
};

export const RETWEET: ActionDefinition = {
  id: 'retweet',
  name: 'Retweet',
  nameKey: 'actions.retweet',
  category: 'tweet',
  trigger: 'both',
  parameters: [],
  timeout: 10000
};

export const FOLLOW_USER: ActionDefinition = {
  id: 'follow_user',
  name: 'Follow User',
  nameKey: 'actions.followUser',
  category: 'tweet',
  trigger: 'both',
  parameters: [],
  timeout: 10000
};
```

并在 `ActionRegistry` 构造函数中注册：

```typescript
// 互动类
LIKE_TWEET,
RETWEET,
FOLLOW_USER,
```

#### 2. `services/actions/engagementActions.ts` (新建)

三个 handler 的实现逻辑：

| Handler | DOM 操作 | 成功检测 |
|---------|---------|---------|
| `likeTweetHandler` | 点击 `[data-testid="like"]` | 检查 `[data-testid="unlike"]` 是否出现 |
| `retweetHandler` | 点击 `[data-testid="retweet"]` → 等待菜单 → 点击 `[data-testid="retweetConfirm"]` | 检查 `[data-testid="unretweet"]` |
| `followUserHandler` | 查找 `[data-testid$="-follow"]`（匹配 `数字-follow` 格式）并点击 | 点击即返回成功 |

每个 handler 都会：
- 先检查是否已完成操作（返回 `{ success: true, data: { alreadyDone: true } }`）
- 使用 `HumanBehaviorSimulator.randomDelay()` 模拟人类行为
- 操作后验证结果

参考来源：`components/panels/BoostPanel.tsx` 第 384-453 行的 DOM 操作逻辑。

#### 3. `services/actions/index.ts`

新增导入和注册：

```typescript
import { engagementHandlers } from './engagementActions';

export const allHandlers: Record<string, ActionHandler> = {
  // ... 现有 handlers
  ...engagementHandlers,
};

export { engagementHandlers };
```

---

## Part 2: bnbot-mcp-server — 新增 3 个 MCP 工具

### 修改文件

#### 1. `src/tools/engagementTools.ts` (新建)

按照 `tweetTools.ts` 的模式，注册三个无参数的 MCP 工具：

| 工具名 | 描述 | 调用的 Action |
|--------|------|--------------|
| `like_tweet` | 点赞当前页面的推文 | `wsServer.sendAction('like_tweet', {})` |
| `retweet` | 转发当前页面的推文 | `wsServer.sendAction('retweet', {})` |
| `follow_user` | 关注当前推文的作者 | `wsServer.sendAction('follow_user', {})` |

这三个工具均不需要参数（`{}`），因为操作目标是当前浏览器页面上的推文。使用前需先调用 `navigate_to_tweet` 导航到目标推文。

#### 2. `src/tools/index.ts`

```typescript
import { registerEngagementTools } from './engagementTools.js';

export function registerAllTools(server: any, wsServer: BnbotWsServer) {
  // ... 现有注册
  registerEngagementTools(server, wsServer);
};
```

---

## Part 3: clawmoney MCP 配置

### 新建文件

#### `clawmoney/.mcp.json`

```json
{
  "mcpServers": {
    "bnbot": {
      "command": "npx",
      "args": ["bnbot-mcp-server"]
    }
  }
}
```

Claude Code 启动时会自动读取此文件，连接 bnbot MCP server。

---

## Part 4: clawmoney-skill 项目

### 项目结构

```
clawmoney-skill/
├── SKILL.md                     # 主 skill 文件
├── .claude-plugin/
│   └── plugin.json              # 分发元数据
├── scripts/
│   └── browse-tasks.sh          # API 查询脚本
├── references/
│   ├── api-endpoints.md         # API 文档
│   └── task-workflow.md         # 任务执行流程
├── LICENSE
└── .gitignore
```

### SKILL.md

触发词：`ClawMoney`, `bounty`, `bounties`, `赏金任务`, `boosted tweets`, `tweet tasks`, `推文任务`

两个核心流程：

**浏览流程：**
1. 运行 `browse-tasks.sh` 查询 API
2. 格式化表格展示任务列表
3. 用户选择要执行的任务

**执行流程（使用 bnbot MCP 工具）：**
1. `get_extension_status` — 检查插件连接
2. `navigate_to_tweet` — 导航到推文
3. `like_tweet` — 点赞（如需要）
4. `retweet` — 转发（如需要）
5. `open_reply_composer` + `fill_reply_text` + `submit_reply` — 回复（如需要）
6. `follow_user` — 关注（如需要）

安全规则：每个操作前确认、2-5 秒间隔、回复必须用户确认后才提交。

### browse-tasks.sh

- 调用 `https://api.bnbot.ai/api/v1/boost/search` 获取任务
- 支持参数：`--status`, `--sort`, `--limit`, `--keyword`, `--ending-soon`
- 使用 Python3 格式化输出（wei → token 转换、剩余时间计算、表格排版）

### references/api-endpoints.md

记录 API 接口详情：
- `GET /boost/search` — 搜索任务，支持 status/sort/limit/keyword/ending_soon 等参数
- `GET /boost/{id}` — 获取单个任务详情
- Boost 对象 JSON schema
- Token 精度表（ETH=18, USDT=6, SOL=9 等）

### references/task-workflow.md

记录 bnbot MCP 工具的使用步骤：
- 每种操作（like、retweet、reply、follow）的具体工具调用和参数
- 错误处理表（Extension 未连接、按钮未找到、超时等）
- 人类行为模拟注意事项

---

## 验证步骤

1. **bnbot-Extension-New**: 编译插件，确认 `engagementActions.ts` 无 TypeScript 错误
2. **bnbot-mcp-server**: 启动 server，确认 `like_tweet`/`retweet`/`follow_user` 出现在工具列表
3. **连接测试**: 调用 `get_extension_status` 确认插件已连接
4. **API 测试**: 运行 `browse-tasks.sh` 确认返回数据
5. **端到端测试**: 在 Claude Code 中触发 "查看 ClawMoney 任务" → 选择任务 → 执行 `navigate_to_tweet` → `like_tweet` → `retweet` 验证完整链路

## 安装 Skill

```bash
# 方式 1: 符号链接到 ~/.claude/skills/
ln -s /Users/jacklee/Projects/clawmoney-skill ~/.claude/skills/clawmoney-skill

# 方式 2: 直接在 Claude Code 中引用
# 在 clawmoney 项目的 CLAUDE.md 中添加 skill 路径引用
```
