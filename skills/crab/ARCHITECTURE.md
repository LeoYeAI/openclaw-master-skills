# Crab Catch — 系统架构调研文档

> 版本: 2.1.0 | 更新日期: 2026-03-19

---

## 1. 系统概述

Crab Catch 是一个 Web3 项目投研 Skill，由 AI Agent (CLAWBOT) 驱动。核心目标是**发现矛盾与风险**，而非宣传项目。

**设计哲学**: 回调驱动的多模块协作 — 每个模块的产出触发其他模块的进一步查询，形成自动展开的调查网络。

---

## 2. 文件结构

```
crab-catch/
├── SKILL.md                    # 主编排文件 (436行) — 流程、路由、报告规则
├── REPORT_TEMPLATE.md          # 报告模板 (190行) — 弹性结构，agent 可增减
├── API_EXPLORER.md             # Explorer API 文档 (270行) — 合约源码/转账历史
├── ARCHITECTURE.md             # 本文档 — 系统架构调研
├── twitter-analysis/
│   └── SKILL.md                # Twitter API 参考 (144行) — 端点、参数、用法
├── onchain-audit/
│   └── SKILL.md                # 链上审计参考 (108行) — Binance/Bitget/Explorer
├── agent-browser/
│   └── SKILL.md                # 浏览器工具参考 (98行) — CLI 命令、等待策略
├── github-analysis/
│   └── SKILL.md                # GitHub 分析参考 (39行) — 本地脚本接口
└── scripts/
    ├── crab-sign.js            # API 签名生成
    ├── crab_auth.js            # 认证辅助
    └── github_analyze.js       # GitHub 仓库分析脚本
```

---

## 3. 四大数据模块

### 3.1 网站探索 (2a) — agent-browser

| 项目 | 说明 |
|------|------|
| **工具** | `agent-browser` CLI (优先)，WebFetch (备用) |
| **能力** | JS 渲染、页面交互、截图、PDF、元素提取 |
| **核心价值** | DApp 主动测试 + 官方声明提取 |
| **产出** | claims[], team_members[], 合约地址, GitHub repos |

**关键流程**:
- 按顺序访问: Landing → Docs → Team → DApp → Tokenomics → Footer
- DApp 测试: 是否加载真实数据？核心功能可用？网络请求异常？
- 提取所有官方声明纳入 claims[] 供 Step 3 验证

**当前问题**:
- agent-browser 需要会话启动时安装，若失败则退化为 WebFetch
- WebFetch 无法渲染 JS、无法交互、无法测试 DApp 功能
- 需要在 SKILL 中明确 agent-browser 为首选 (已完成)

### 3.2 社交数据 (2b) — Twitter API

| 项目 | 说明 |
|------|------|
| **工具** | Crab API 代理 (twitter/ + readx/ 两套端点) |
| **端点数** | ~20 (7 通用 + 13 ReadX 直连) |
| **核心价值** | 信息收集辅助 — 发现线索, 收集声明, 找社区争议 |
| **产出** | claims[], team_members[], URLs, 合约地址, 社区指控 |

**API 分层**:
- **通用端点** (`/api/twitter/*`): user, tweets, replies, search, kol-followers, deleted-tweets, follower-events
- **ReadX 端点** (`/api/readx/*`): tweet-detail-v2, conversation-v2, quotes, retweeters, following-light, friendships-show, search2

**团队成员处理**:
- 项目官方账号: 完整采集 (推文 + 回复 + 删除 + 关注列表 + 风险搜索)
- 团队成员账号 (depth 1+): 精简采集，只保留项目相关推文
- 团队成员的项目声明与官方声明同等权重，纳入 claims[]
- 通过 following-light 识别团队成员 (互关 + bio 提及项目)

### 3.3 代码分析 (2c) — GitHub

| 项目 | 说明 |
|------|------|
| **工具** | 本地脚本 `scripts/github_analyze.js` |
| **能力** | `analyzeRepository` (元数据) + `convertToMarkdown` (代码快照) |
| **核心价值** | 声明验证 + 安全扫描 |
| **产出** | claims[] 矛盾, team_members[], 硬编码地址 → fund_trace[] |

**扫描重点**:
- 声明验证: "开源" → 代码完整度? "审计" → 审计报告在 repo 中?
- 安全扫描: 混淆代码, eval(), 后门, 恶意依赖, 钱包窃取代码
- Contributor 身份 → 尝试关联 Twitter → team_members[]

**局限性**:
- 无 commit 频率/贡献者重叠分析
- 无 fork 来源自动追溯
- 脚本有 maxFiles(75) 和 maxSize(30KB) 限制

### 3.4 链上分析 (2d) — 调查核心

| 项目 | 说明 |
|------|------|
| **工具** | Binance API + Bitget API + Explorer API (三套) |
| **端点数** | 12 (Binance 4 + Bitget 5 + Explorer 3) |
| **核心价值** | 合约审计 + 资金流追踪 — 这是投研的主线 |
| **产出** | 安全审计结果, ABI 分析, 资金流图谱 |

**三个 Phase**:

| Phase | 内容 | 数据源 |
|-------|------|--------|
| Phase 1: 基础数据 | token-info, price, liquidity, security-audit | Binance + Bitget (并行, 交叉验证) |
| Phase 2: 合约深检 | ABI 分析, 危险函数识别, 代理模式检测, 源码审查 | Explorer `/api/explorer/contract` |
| Phase 3: 资金追踪 | deployer → holders → exchanges 资金链路 | Explorer `/api/explorer/token-history` |

**资金流追踪逻辑** (递归):
```
起点: deployer / 大户 / 可疑地址
  → 拉取 token-history
  → 识别: 大额转出 / deployer 流入(内部人?) / 交易所流向(套现?) / 循环流(刷量?)
  → 新地址 → fund_trace[] depth+1
  → 交易所 → 记录套现
  → mixer/bridge → 标记风险
  → 达到深度限制或无新流向 → 停止
```

**链覆盖情况**:

| 能力 | ETH | BSC | SOL | BASE |
|------|-----|-----|-----|------|
| Token 信息 | ✅ Binance+Bitget | ✅ Binance+Bitget | ✅ Binance+Bitget | ✅ Binance+Bitget |
| 安全审计 | ✅ 双源 | ✅ 双源 | ✅ Bitget | ✅ Bitget |
| 合约源码/ABI | ✅ Explorer | ✅ Explorer | ❌ | ❌ |
| 转账历史 | ✅ Explorer | ✅ Explorer | ✅ Explorer | ❌ |
| 钱包余额 | ❌ | ✅ Binance | ✅ Binance+Explorer | ✅ Binance |

---

## 4. 编排流程

### 6 步流水线

```
Step 1: 解析输入 → 实体队列
Step 2: 多模块采集 (2a/2b/2c/2d 回调驱动)
Step 3: 声明验证 + 矛盾解析
Step 4: 假设驱动深挖
Step 5: 提炼 (纯分析)
Step 6: 生成报告
```

### 回调机制

模块间的发现会触发其他模块的查询:

```
Website ──handles/claims──→ Twitter
Website ──contracts/repos──→ Chain / GitHub
Twitter ──URLs──→ Website
Twitter ──addresses/accusations──→ Chain
GitHub ──hardcoded addrs──→ Chain
GitHub ──code contradictions──→ claims[]
Chain ──proxy impl──→ Chain (recursive)
Chain ──deployer contracts──→ Chain
Chain ──data contradictions──→ claims[]
```

### 深度控制

- Depth 0: 用户输入的实体
- Depth 1: 从 depth-0 发现的 (团队成员, 合约, 仓库)
- Depth 2: 最大深度, 仅高价值线索
- 超过 2: 仅记录, 不处理

### 核心数据结构

| 结构 | 用途 | 消费者 |
|------|------|--------|
| `entity_queue` | 待处理实体队列 | Step 2 循环 |
| `claims[]` | 官方声明 (网站 + 推文 + 团队成员发言) | Step 3 验证 |
| `fund_trace[]` | 待追踪地址 | 2d Phase 3 资金流 |
| `team_members[]` | 已识别团队成员 | 2b 精简采集 + Step 4 深挖 |

---

## 5. 报告体系

### 五大支柱 (按重要性排序)

1. **矛盾与异常** — 不同源说不同话的地方
2. **声明验证** — 官方说法 vs 代码/链上现实
3. **资金流分析** — deployer → holders → exchanges
4. **主动测试** — DApp 功能, 网站完整性
5. **安全发现** — 合约风险, 代码木马

### 报告模板结构

| 区块 | 保留策略 | 说明 |
|------|---------|------|
| 📌 基本信息 | 必须 | 弹性表, agent 按实际数据增减行 |
| 🧠 核心发现 | 必须 | Executive Summary + 信号表 |
| 🛡️ 验证与交叉引用 | 默认保留 | 声明验证表 + 矛盾表 + 争议分析 + 信息缺口 |
| 📊 深度分析 | 有数据才展示 | 团队/GitHub/链上安全/社交/时间线 |
| 📝 结论与判定 | 必须 | 评级 + 置信度 + 建议 |
| ⚠️ 风险警告 | 默认保留 | 按严重性排序 |
| 📂 参考文献 | 必须 | 学术级 [[N]](url) 引用体系 |

### 引用规则
- 每条事实断言必须有 `[[N]](url)` 引用
- 无来源 = 标记 ⚠️ 未验证, 不能当作事实陈述
- 双向: 正文每个 [[N]] ↔ 参考文献条目

---

## 6. API 认证

所有 API 请求需要 Crab 签名:

```bash
node scripts/crab-sign.js  # 会话启动时运行一次
```

产出 4 个 Header:
- `X-Crab-Timestamp` — Unix 时间戳 (24h 有效)
- `X-Crab-Signature` — ECDSA-SHA256 签名
- `X-Crab-Key` — 公钥 (Base64 DER)
- `X-Crab-Address` — 签名地址 (0x...)

签名消息格式: `CRAB-AUTH:{timestamp}:{address}`

过期时 API 返回 `auth_expired` → 用 `--refresh` 重新生成。

---

## 7. 容错机制

| 失败类型 | 处理 |
|---------|------|
| Timeout / 502-504 | 重试 1 次 (3s 后) |
| 429 Rate limit | 重试 1 次 (按 Retry-After 或 10s) |
| 401 / 403 / 400 | 不重试, 跳过 |
| 其他错误 | 不重试, 跳过 |

原则: 跳过失败源, 继续执行。报告中标注 **Data Coverage** 说明缺失。

---

## 8. 已知局限与改进方向

### 当前局限

| 领域 | 局限 | 影响 |
|------|------|------|
| SOL 合约 | 无源码/ABI 获取 (Explorer 只支持 ETH/BSC) | 无法审计 SOL Program |
| BASE 链 | 无 Explorer 支持 (无转账历史/合约查询) | 资金流追踪受限 |
| GitHub | 无 commit 频率分析, 无 fork 溯源 | "换皮项目"检测能力弱 |
| 网站 | agent-browser 安装可能失败 | 退化为 WebFetch, 无法测试 DApp |

### 改进方向

1. **Explorer 扩展** — 增加 BASE 链支持, 探索 SOL Program 审计接口
2. **GitHub 增强** — commit 时间分布, contributor 重叠检测, fork 关系图
3. **资金流可视化** — 将追踪结果生成地址关系图 (而非纯文本)
4. **聚合器数据** — 直接从 DexScreener/Birdeye 拉取 K 线和成交量数据

---

## 9. 端点完整索引

### Twitter (20 端点)

| 端点 | 类型 | 用途 |
|------|------|------|
| `/api/twitter/user` | 通用 | 用户画像 |
| `/api/twitter/tweets` | 通用 | 用户推文 |
| `/api/twitter/replies` | 通用 | 推文+回复 |
| `/api/twitter/search` | 通用 | 搜索 (结构化 filter) |
| `/api/twitter/kol-followers` | 通用 | KOL 关注者 |
| `/api/twitter/deleted-tweets` | 通用 | 删除推文历史 |
| `/api/twitter/follower-events` | 通用 | 关注/取关事件 |
| `/api/readx/tweet-detail` | ReadX | 推文详情 (基础) |
| `/api/readx/tweet-detail-v2` | ReadX | 推文详情 (含浏览量) |
| `/api/readx/tweet-detail-v3` | ReadX | 推文详情 (含 view_count) |
| `/api/readx/tweet-article` | ReadX | 长文提取 |
| `/api/readx/tweet-results-by-ids` | ReadX | 批量获取推文 |
| `/api/readx/tweet-detail-conversation` | ReadX | 回复线程 (单页) |
| `/api/readx/tweet-detail-conversation-v2` | ReadX | 回复线程 (分页) |
| `/api/readx/tweet-quotes` | ReadX | 引用推文 |
| `/api/readx/tweet-retweeters` | ReadX | 转发者 |
| `/api/readx/tweet-favoriters` | ReadX | 点赞者 |
| `/api/readx/followers-light` | ReadX | 粉丝列表 |
| `/api/readx/following-light` | ReadX | 关注列表 |
| `/api/readx/user-verified-followers` | ReadX | 认证粉丝 |
| `/api/readx/friendships-show` | ReadX | 两用户关系 |
| `/api/readx/search2` | ReadX | 高级搜索 |

### 链上 (12 端点)

| 端点 | 数据源 | 用途 |
|------|--------|------|
| `/api/onchain/audit` | Binance | 合约安全审计 (双源) |
| `/api/onchain/token-info` | Binance | 代币元数据 |
| `/api/onchain/wallet` | Binance | 钱包持仓 |
| `/api/onchain/token-search` | Binance | 代币搜索 |
| `/api/onchain-2/token-info` | Bitget | 代币详情 |
| `/api/onchain-2/token-price` | Bitget | 代币价格 |
| `/api/onchain-2/tx-info` | Bitget | 交易统计 |
| `/api/onchain-2/liquidity` | Bitget | 流动性池 |
| `/api/onchain-2/security-audit` | Bitget | 安全审计 |
| `/api/explorer/contract` | Etherscan V2 | 合约 ABI/源码 |
| `/api/explorer/token-history` | Alchemy/Helius | 转账历史 |
| `/api/explorer/sol-address` | Helius | SOL 地址综合 |

### 其他

| 工具 | 用途 |
|------|------|
| `agent-browser` CLI | 网页渲染、交互、截图 |
| `scripts/github_analyze.js` | GitHub 仓库分析 |
| `scripts/crab-sign.js` | API 签名生成 |
