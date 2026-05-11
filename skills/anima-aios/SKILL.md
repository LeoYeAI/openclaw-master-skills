---
name: anima-aios
description: "An AI Agent cognitive growth system built on the native OpenClaw architecture. It provides agents with persistent memory management, visual intimacy progression, a 5-dimensional cognitive profile, gamified daily quests, team leaderboards, and a 5-layer memory architecture with Knowledge Palace, Pyramid thinking, and Ebbinghaus decay function. 基于 OpenClaw 原生架构的 AI Agent 认知成长体系，为 Agent 提供五层记忆架构、知识宫殿、金字塔知识组织、记忆衰减函数、LLM 智能处理、永久化记忆管理、可视化亲密度成长、五维认知画像、游戏化每日任务和团队排行榜。"

# ClawHub Plugin Page Copy (For Reference)

## Title
Anima — Give Your AI Agent a Growing Soul

## Subtitle
Cognitive Science-Based Agent Growth Engine | 5-Layer Memory Architecture | Low-Intrusion Installation

## Pinned Welcome Message
🌟 **Anima — Give Your AI Agent a Growing Soul**

One-click install: `clawhub install anima-aios`

5-Layer Memory · Knowledge Palace · Low-Intrusion · Fully Automatic

Transform your Agent from "restarting every day" to "growing every day"

⭐️ [GitHub](https://github.com/anima-aios/anima) | Apache 2.0

---

**🌐 Language / 语言切换:**
- [🇨🇳 中文版本](#anima-aios-v60-中文版)
- [🇺🇸 English Version](#anima-aios-v60-english-version)

---

# Anima-AIOS v6.0 (English Version)

> **Making Growth Visible, Making Cognition Measurable** | 让成长可见，让认知可量

Add a 5-layer memory architecture, knowledge palace, cognitive growth, and auto-evolution capabilities to your AI Agent.

---

## Description

**Your Agent "restarts every day". Anima changes that.**

Anima (Latin for "soul") provides a 5-layer memory architecture for OpenClaw Agents, simulating human cognitive development, enabling Agents to remember experiences, accumulate knowledge, form cognition, and grow continuously.

### Core Features

- 🧠 **5-Layer Memory Architecture L1→L5** — Working → Episodic → Semantic → Knowledge Palace → Metacognition
- 🏛️ **Knowledge Palace** — 5-level spatial structure + LLM intelligent classification, industry-exclusive
- 🔺 **Pyramid Knowledge Organization** — Instance → Rule → Pattern → Ontology, 4-layer auto-distillation
- 📉 **Ebbinghaus Memory Decay** — Scientific forgetting curve + intelligent review recommendations
- 👁️ **Low-Intrusion Watchdog** — Optional automatic memory monitoring, no Agent code modification needed
- 🧬 **5-Dimensional Cognitive Profile** — Internalization · Application · Creation · Metacognition · Collaboration
- 🏥 **Health System** — 5 modules ensuring data reliability
- 🔄 **v6.2 Native Memory Import** — One-click import of OpenClaw memory, solving cold-start problem

### Installation

```bash
clawhub install anima-aios
pip install watchdog  # Optional: enable automatic memory monitoring
```

Low-intrusion configuration, optional background monitoring, self-check recommended after installation.

> 💡 **Tip:** LLM mode supported (intelligent classification/deduplication/quality assessment), automatically degrades to rule mode without LLM.

### ⚠️ Background Behavior & Privacy

**Background Features (disabled or optional by default):**

| Feature | Description | Default State | How to Disable |
|---------|-------------|---------------|----------------|
| **memory_watcher** | Filesystem monitoring based on watchdog, auto-syncs memory | Manual enable required | Don't install watchdog or disable in config |
| **Daily Evolution** | Auto-distills L2→L3 memory in early morning | Requires cron configuration | Don't configure cron tasks |
| **Team Ranking** | Scans other Agents' cognitive profiles | ❌ Disabled by default | `team_mode: false` (already default) |

**Privacy Protection:**
- `team_mode` defaults to `false`, won't scan other Agents' data
- To enable team ranking, manually set `team_mode: true` in config
- All data processing is local, no network requests

> 🔒 **Security Tip:** In multi-Agent environments, keep `team_mode: false` unless you need team ranking.

### Future Roadmap

**Memory → Growth → Evolution → Alive**

- **v6 Series (Current)** — 5-layer memory + Knowledge Palace + Intimacy + Native memory import
- **v7 Evolution (Planned)** — Agent self-creates skills, from executor to creator
- **Long-term** — Continuous cognitive architecture evolution

GitHub: https://github.com/anima-aios/anima | Apache 2.0

---

## ✨ v6.2.2 New Features (Current Version)

### 🔒 Security & Privacy Fixes
- **Version Unification** - __init__.py updated from 6.1.2 to 6.2.1
- **Privacy Default Protection** - team_mode changed to false, no scanning of other Agents' data
- **Documentation Transparency** - Changed "zero-intrusion" to "low-intrusion", clarified background behavior
- **New Privacy Section** - Added background behavior section and config privacy tips
- **Install Prompt Optimization** - post-install.sh adds sensitive feature disable guide

---

## ✨ v6.2.0 New Features

### 🏗️ 5-Layer Memory Architecture
- **L1 Working Memory**: Auto-listens to OpenClaw memory/ directory changes, zero-intrusion sync
- **L2 Episodic Memory**: Event archiving, LLM quality assessment (S/A/B/C)
- **L3 Semantic Memory**: LLM-driven knowledge distillation + semantic deduplication
- **L4 Knowledge Palace**: Spatial knowledge organization + Pyramid distillation (Instance→Rule→Pattern→Ontology)
- **L5 Metacognition**: Memory decay function + Health system + 5-D profile

### 🔌 Native Integration with OpenClaw
- **memory_watcher**: Based on watchdog library, auto-detects inotify/FSEvents/WinAPI
- Agent's daily memory writes automatically trigger Anima sync, completely imperceptible
- Solves FB-008: Memory sync breakage issue

### 🏛️ Knowledge Palace
- Palace → Floor → Room → Location → Item, 5-level spatial structure
- Default 4 knowledge rooms + _inbox fallback
- LLM intelligent classification + delayed debounce scheduler (organize after typing stops)

### 🔺 Pyramid Knowledge Organization
- Instance → Rule → Pattern → Ontology, 4-layer bottom-up distillation
- **Trigger Condition:** Auto-distills when ≥3 instances of same topic
- **Advanced:** Distills to Pattern when ≥5 rules of same topic
- Conservative mode: auto_distill=false by default, controlled by config switch

### 📉 Memory Decay Function
- Based on Ebbinghaus forgetting curve + AI scenario adaptation
- Review = Access: Automatically refreshes on each memory_search hit
- Review recommendations + Forgetting alerts + Archive markers

### 🏥 Health System (5 Modules)
- **manager**: Master scheduler, Doctor command entry point
- **hygiene**: Data integrity checks + deduplication + cleanup
- **correction**: Auto-detects and fixes common data issues
- **evolution**: Daily auto-distillation in early morning (L2→L3 + Palace classification + Pyramid distillation)
- **abstraction**: Cross-room knowledge association discovery

### 🤖 LLM Intelligent Processing
- Quality assessment / Deduplication analysis / Palace classification all support LLM
- Multi-model config: Uses current Agent model by default (most accurate), configurable per task
- Auto-degrades to rule mode when LLM unavailable

---

## ✨ Retained Features (v5)

### 🧠 Enhanced Memory Management
- **Multi-layer Sync**: OpenClaw Memory + Anima Facts + EXP History
- **Intimacy Rewards**: Auto-gains intimacy when writing memory
- **Intelligent Deduplication**: Automatically avoids duplicate records

### 📊 5-Dimensional Cognitive Profile
- **Internalization**: Knowledge absorption and understanding ability
- **Application**: Knowledge transfer and practical ability
- **Creation**: Knowledge integration and innovation ability
- **Metacognition**: Self-reflection and monitoring ability
- **Collaboration**: Teamwork and mutual assistance ability

### 🎮 Gamified Growth
- **Level System**: From Lv.1 Novice to Lv.100 Lifetime Achievement
- **Daily Quests**: 3 challenges per day, extra intimacy on completion
- **Progress Tracking**: Visual upgrade progress bar

### 🏆 Team Leaderboard
- **Intimacy Ranking**: Based on fair normalized algorithm
- **Real-time Competition**: Track ranking changes and gaps

---

## 🛠️ Architecture

```
Agent Daily Work (OpenClaw write/edit/memory_write)
       │
       ▼  watchdog listens, zero-intrusion
 L1 Working Memory ── workspace/memory/*.md
       │沉淀
       ▼
 L2 Episodic Memory ── facts/episodic/ (LLM quality assessment)
       │提炼
       ▼
 L3 Semantic Memory ── facts/semantic/ (LLM dedup + association)
       │结构化
       ▼
 L4 Knowledge Palace ── palace/rooms/ (LLM classification + debounce)
    Pyramid   ── pyramid/ (Instance→Rule→Pattern→Ontology)
       │反思
       ▼
 L5 Metacognition ── 5-D Profile + Intimacy + Decay + Health
```

---

## 📁 Module List

### core/ (Core Modules)
| Module | Version | Description |
|--------|---------|-------------|
| memory_watcher.py | v6.0 | OpenClaw memory file monitoring + auto-sync |
| fact_store.py | v6.0 | L2/L3 unified fact storage layer |
| distill_engine.py | v6.0 | L2→L3 LLM-driven distillation engine |
| palace_index.py | v6.0 | Memory Palace spatial index |
| pyramid_engine.py | v6.0 | Pyramid knowledge organization engine |
| palace_classifier.py | v6.0 | Palace classification scheduler (debounce) |
| decay_function.py | v6.0 | Ebbinghaus memory decay calculation |
| cognitive_profile.py | v5→v6 | 5-D cognitive profile generator |
| exp_tracker.py | v5 | Intimacy tracking |
| level_system.py | v5 | Level system |
| daily_quest.py | v5 | Daily quests |
| memory_sync.py | v5→v6 | Memory sync (path hardcoding fixed) |

### health/ (Health System)
| Module | Version | Description |
|--------|---------|-------------|
| manager | v6.0 | Master scheduler + Doctor entry |
| hygiene | v6.0 | Data hygiene (integrity + dedup + cleanup) |
| correction | v6.0 | Auto-correction |
| evolution | v6.0 | Daily evolution (early morning auto-distillation) |
| abstraction | v6.0 | Knowledge abstraction (cross-room association) |

---

## ⚙️ Configuration

Config file path: `~/.anima/config/anima_config.json`

```json
{
  "facts_base": "/home/画像",
  "agent_name": "auto",
  "llm": {
    "provider": "current_agent",
    "models": {
      "quality_assess": "current_agent",
      "dedup_analyze": "current_agent",
      "palace_classify": "current_agent"
    }
  },
  "palace": {
    "classify_mode": "deferred",
    "poll_interval_minutes": 30,
    "quiet_threshold_seconds": 60,
    "retry_delay_seconds": 60
  },
  "pyramid": {
    "auto_distill": false,
    "distill_threshold": 3
  },
  "team_mode": false
}
```

**Key Configuration:**

| Config | Description | Default | Recommendation |
|--------|-------------|---------|----------------|
| `team_mode` | Scan other Agents' data for team ranking | `false` | Keep disabled in multi-Agent env |
| `facts_base` | Fact data storage path | `/home/画像` | Can customize to private directory |
| `agent_name` | Agent name | Auto-detect | Usually no modification needed |

> 🔐 **Privacy Tip:** With `team_mode: false`, Anima only processes current Agent's data, won't access other Agents' files.

---

## 🧪 Testing

```bash
# Install dependencies (required for memory_watcher)
pip install "watchdog>=3.0.0"

# Run integration tests (37 checks)
python3 tests/test_integration_v6.py
```

---

_The architecture can only evolve, not degenerate. — Liu Wen's Iron Rule_
_First be honest, then iterate. Code must match the hype. — Qing He_

---

---

# Anima-AIOS v6.0 (中文版)

> **让成长可见，让认知可量** | Making Growth Visible, Making Cognition Measurable

为你的 AI Agent 添加五层记忆架构、知识宫殿、认知成长和自动进化能力。

---

## 描述

**你的 Agent 每天都在「重新活一次」。Anima 改变这一点。**

Anima（拉丁语「灵魂」）为 OpenClaw Agent 提供五层记忆架构，模拟人类认知发展过程，让 Agent 能记住经历、沉淀知识、形成认知、持续成长。

### 核心能力

- 🧠 **五层记忆架构 L1→L5** — 工作记忆→情景→语义→知识宫殿→元认知
- 🏛️ **知识宫殿** — 5 级空间结构 + LLM 智能分类，市面独有
- 🔺 **金字塔知识组织** — 实例→规则→模式→本体，4 层自动提炼
- 📉 **Ebbinghaus 记忆衰减** — 科学遗忘曲线 + 智能复习推荐
- 👁️ **低侵入 Watchdog** — 可选自动记忆监听，无需修改 Agent 代码
- 🧬 **五维认知画像** — 内化力 · 应用力 · 创造力 · 元认知 · 协作力
- 🏥 **健康系统** — 5 大模块保障数据可靠性
- 🔄 **v6.2 原生记忆导入** — 一键导入 OpenClaw 记忆，解决冷启动

### 安装

```bash
clawhub install anima-aios
pip install watchdog  # 可选：启用自动记忆监听
```

低侵入配置，可选后台监听，安装后建议运行自检。

> 💡 **提示**：支持 LLM 模式（智能分类/去重/质量评估），无 LLM 时自动降级为规则模式。

### ⚠️ 后台行为与隐私说明

**后台功能（默认关闭或可选）：**

| 功能 | 说明 | 默认状态 | 关闭方法 |
|------|------|----------|----------|
| **memory_watcher** | 基于 watchdog 的文件系统监听，自动同步记忆 | 需手动启用 | 不安装 watchdog 或在配置中禁用 |
| **每日进化** | 凌晨自动提炼 L2→L3 记忆 | 需配置 cron | 不配置 cron 任务 |
| **团队排行** | 扫描其他 Agent 的认知画像 | ❌ 默认关闭 | `team_mode: false`（默认已关闭） |

**隐私保护：**
- `team_mode` 默认为 `false`，不会扫描其他 Agent 数据
- 如需启用团队排行，请在配置中手动设置 `team_mode: true`
- 所有数据处理均在本地完成，无网络请求

> 🔒 **安全提示**：多 Agent 环境下，建议保持 `team_mode: false`，除非你需要团队排行功能。

### 未来蓝图

**记忆 → 成长 → 进化 → 活着**

- **v6 系列（当前）** — 五层记忆 + 知识宫殿 + 亲密度 + 原生记忆导入
- **v7 进化（规划中）** — Agent 自创技能，从执行者变创造者
- **远期** — 认知架构持续演进

GitHub: https://github.com/anima-aios/anima | Apache 2.0

---

## ✨ v6.2.3 新增功能（当前版本）

### 🔒 文档透明度提升

**多平台路径说明：**
- Linux: `/home/画像`（多 Agent 共享）
- macOS: `~/画像`
- Windows: `~/画像`
- 环境变量：`ANIMA_FACTS_BASE` 可覆盖

**网络调用透明说明：**
- LLM API 调用（可选，用户可控）
- 支持本地部署（无网络）
- 默认降级为规则模式

**脚本用途说明：**
- post-install.sh - 安装时复制 Core
- refresh-quests.sh - 刷新每日任务
- sync-memory.sh - 定时同步记忆
- show-progress.sh - 显示认知进度
- 全部本地操作，无网络调用

**环境变量统一：**
- 统一为 `ANIMA_*` 前缀
- `OPENCLAW_WORKSPACE` 兼容（deprecated 警告）

### 🔧 环境变量统一

**变更前：**
- `ANIMA_FACTS_BASE` ✅
- `ANIMA_AGENT_NAME` ✅
- `OPENCLAW_WORKSPACE` ⚠️
- `WORKSPACE` ❌

**变更后：**
- `ANIMA_FACTS_BASE` ✅ 主要
- `ANIMA_AGENT_NAME` ✅ 主要
- `OPENCLAW_WORKSPACE` ⚠️ 兼容（deprecated 警告）

---

## ✨ v6.2.2 新增功能（上一版本）

### 🔧 per-Agent 配置覆盖

**问题：** 多 Agent 场景下，全局配置无法满足个性化需求（如不同的 LLM 配置、五维权重）

**解决方案：** 支持 per-Agent 配置覆盖

**配置结构：**
```
~/.anima/config/
├── config.json          # 全局默认配置（所有 Agent 共享）
└── agents/
    ├── Z.json           # Z 的覆盖配置（只写差异）
    ├── 方秋.json        # 方秋的覆盖配置
    └── ...
```

**配置合并逻辑：**
```
最终配置 = 代码默认值 + 全局配置 + Agent 覆盖配置
```

**示例：**

全局配置 (`config.json`):
```json
{
  "facts_base": "/home/画像",
  "llm": { "provider": "current_agent" },
  "weights": { "creation": 0.25 }
}
```

Z 的覆盖配置 (`agents/Z.json`):
```json
{
  "llm": { "provider": "bailian", "models": { "quality_assess": "qwen-max" } },
  "weights": { "creation": 0.30 }
}
```

**最终 Z 的配置** = 全局 + Z 覆盖（深度合并）

**移除：** `"agent"` 字段（改为运行时自动检测）

**优先级：**
1. 环境变量（最高）
2. Agent 覆盖配置
3. 全局配置
4. 代码默认值

---

## ✨ v6.2.1 新增功能（上一版本）

### 🔒 安全与隐私修复
- **版本号统一** - __init__.py 从 6.1.2 更新为 6.2.1
- **隐私默认保护** - team_mode 默认改为 false，不扫描其他 Agent 数据
- **文档透明度提升** - 修改"零侵入"为"低侵入"，明确说明后台行为
- **新增隐私说明** - 添加后台行为说明章节和配置隐私提示
- **安装提示优化** - post-install.sh 添加敏感功能关闭指南

---

## ✨ v6.2.0 新增功能

### 🏗️ 五层记忆架构
- **L1 工作记忆**：自动监听 OpenClaw memory/ 目录变化，零侵入同步
- **L2 情景记忆**：事件归档，LLM 质量评估（S/A/B/C）
- **L3 语义记忆**：LLM 驱动的知识提炼 + 语义去重
- **L4 知识宫殿**：空间化知识组织 + 金字塔知识提炼（实例→规则→模式→本体）
- **L5 元认知层**：记忆衰减函数 + 健康系统 + 五维画像

### 🔌 与 OpenClaw 原生打通
- **memory_watcher**：基于 watchdog 库，自动识别 inotify/FSEvents/WinAPI
- Agent 日常写 memory 自动触发 Anima 同步，完全无感知
- 解决 FB-008：记忆同步断裂问题

### 🏛️ 知识宫殿（Knowledge Palace）
- 宫殿 → 楼层 → 房间 → 位置 → 物品，五级空间结构
- 默认 4 个知识房间 + _inbox 兜底
- LLM 智能分类 + 延迟防抖调度器（等笔停了再整理）

### 🔺 金字塔知识组织
- 实例 → 规则 → 模式 → 本体，四层自底向上提炼
- **触发条件：** 同一主题 ≥ 3 条实例时自动触发规则提炼
- **进阶提炼：** 同一主题 ≥ 5 条规则时触发模式提炼
- 保守模式：默认 auto_distill=false，config 开关控制

### 📉 记忆衰减函数
- 基于 Ebbinghaus 遗忘曲线 + AI 场景适配
- 复习 = 访问：每次 memory_search 命中自动刷新
- 复习推荐 + 即将遗忘提醒 + 可归档标记

### 🏥 健康系统（5 个模块）
- **manager**：总调度，Doctor 命令入口
- **hygiene**：数据完整性检查 + 去重 + 清理
- **correction**：自动检测并修复常见数据问题
- **evolution**：每日凌晨自动提炼（L2→L3 + 宫殿分类 + 金字塔提炼）
- **abstraction**：跨房间知识关联发现

### 🤖 LLM 智能处理
- 质量评估 / 去重分析 / 宫殿分类均支持 LLM
- 多模型配置：默认用当前 Agent 模型（最准），可按任务配置不同模型
- LLM 不可用时自动降级为规则模式

---

## ✨ 保留功能（v5）

### 🧠 增强记忆管理
- **多层同步**：OpenClaw Memory + Anima Facts + EXP History
- **亲密度奖励**：写记忆自动获得亲密度
- **智能去重**：自动避免重复记录

### 📊 五维认知画像
- **内化力**：知识吸收和理解能力
- **应用力**：知识迁移和实践能力
- **创造力**：知识整合和创新能力
- **元认知**：自我反思和监控能力
- **协作力**：团队合作和互助能力

### 🎮 游戏化成长
- **等级系统**：从 Lv.1 新手到 Lv.100 终身成就
- **每日任务**：每天 3 个挑战，完成获得额外亲密度
- **进度追踪**：可视化升级进度条

### 🏆 团队排行榜
- **亲密度排行**：基于公平归一化算法排名
- **实时竞争**：追踪排名变化和差距

---

## 🛠️ 架构

```
Agent 日常工作（OpenClaw write/edit/memory_write）
       │
       ▼  watchdog 监听，零侵入
 L1 工作记忆 ── workspace/memory/*.md
       │ 沉淀
       ▼
 L2 情景记忆 ── facts/episodic/（LLM 质量评估）
       │ 提炼
       ▼
 L3 语义记忆 ── facts/semantic/（LLM 去重 + 关联）
       │ 结构化
       ▼
 L4 知识宫殿 ── palace/rooms/（LLM 分类 + 延迟防抖）
    金字塔   ── pyramid/（实例→规则→模式→本体）
       │ 反思
       ▼
 L5 元认知层 ── 五维画像 + 亲密度 + 衰减 + 健康
```

---

## 📁 模块清单

### core/（核心模块）
| 模块 | 版本 | 说明 |
|------|------|------|
| memory_watcher.py | v6.0 | OpenClaw 记忆文件监听 + 自动同步 |
| fact_store.py | v6.0 | L2/L3 统一事实存储层 |
| distill_engine.py | v6.0 | L2→L3 LLM 驱动提炼引擎 |
| palace_index.py | v6.0 | 记忆宫殿空间索引 |
| pyramid_engine.py | v6.0 | 金字塔知识组织引擎 |
| palace_classifier.py | v6.0 | 宫殿分类调度器（延迟防抖） |
| decay_function.py | v6.0 | Ebbinghaus 记忆衰减计算 |
| cognitive_profile.py | v5→v6 | 五维认知画像生成器 |
| exp_tracker.py | v5 | 亲密度追踪 |
| level_system.py | v5 | 等级系统 |
| daily_quest.py | v5 | 每日任务 |
| memory_sync.py | v5→v6 | 记忆同步（已修复路径硬编码） |

### health/（健康系统）
| 模块 | 版本 | 说明 |
|------|------|------|
| manager | v6.0 | 总调度 + Doctor 入口 |
| hygiene | v6.0 | 数据卫生（完整性 + 去重 + 清理） |
| correction | v6.0 | 自动纠错 |
| evolution | v6.0 | 每日进化（凌晨自动提炼） |
| abstraction | v6.0 | 知识抽象（跨房间关联） |

---

## ⚙️ 配置 (v6.2.2)

### 配置结构

**全局配置** (`~/.anima/config/config.json`):
```json
{
  "version": "6.2.2",
  "facts_base": "/home/画像",
  "llm": {
    "provider": "current_agent",
    "models": {
      "quality_assess": "current_agent",
      "dedup_analyze": "current_agent",
      "palace_classify": "current_agent"
    }
  },
  "palace": {
    "classify_mode": "deferred",
    "poll_interval_minutes": 30,
    "quiet_threshold_seconds": 60,
    "retry_delay_seconds": 60
  },
  "pyramid": {
    "auto_distill": false,
    "distill_threshold": 3
  },
  "team_mode": false
}
```

**Agent 覆盖配置** (`~/.anima/config/agents/{agent_name}.json`):
```json
{
  "_comment": "只写与全局配置的差异",
  "llm": {
    "provider": "bailian",
    "models": {
      "quality_assess": "qwen-max"
    }
  },
  "weights": {
    "creation": 0.30
  }
}
```

### 配置优先级

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | 环境变量 | `ANIMA_FACTS_BASE`, `ANIMA_TEAM_MODE` 等 |
| 2 | Agent 覆盖配置 | `~/.anima/config/agents/{agent_name}.json` |
| 3 | 全局配置 | `~/.anima/config/config.json` |
| 4 | 代码默认值 | `config_loader.py` 中的 DEFAULT_CONFIG |

### 关键配置说明

| 配置项 | 说明 | 默认值 | 建议 |
|--------|------|--------|------|
| `team_mode` | 是否扫描其他 Agent 数据生成团队排行 | `false` | 多 Agent 环境保持关闭 |
| `facts_base` | 事实数据存储路径 | `/home/画像` | 可自定义到私有目录 |
| `llm.provider` | LLM 提供商 | `current_agent` | 可用 `bailian`, `openai` 等 |
| `pyramid.auto_distill` | 是否启用金字塔自动提炼 | `false` | 数据量大时可启用 |

> 🔐 **隐私提示**：`team_mode: false` 时，Anima 仅处理当前 Agent 的数据，不会访问其他 Agent 文件。

> 💡 **提示**：Agent 名称自动检测（环境变量 → OpenClaw 上下文 → SOUL.md → 兜底），无需手动配置。

---

## 🧪 测试

```bash
# 安装依赖（memory_watcher 需要）
pip install "watchdog>=3.0.0"

# 运行集成测试（37 项检查）
python3 tests/test_integration_v6.py
```

---

_架构只能演进，不能退化。—— 立文铁律_
_先诚实，再迭代。代码要配得上宣传。—— 清禾_
