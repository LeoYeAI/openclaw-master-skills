# 🌟 Anima-AIOS

**让 AI Agent 从「每天重新活一次」变成「每天都在成长」**

[🌏 中文版本](README_CN.md) | [English](README.md)

[![Version](https://img.shields.io/badge/version-6.2.0-green.svg)](https://github.com/anima-aios/anima/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Clawhub](https://img.shields.io/badge/clawhub-anima--aios-orange.svg)](https://clawhub.com/skills/anima-aios)

**Anima**（拉丁语「灵魂」）是一个基于 OpenClaw 的 Agent 认知成长引擎。

你的 Agent 每天帮你做了很多事，但重启后什么都不记得。Anima 改变这一点——它让 Agent 能记住经历、沉淀知识、形成认知、持续成长。无需修改 Agent 代码，安装即生效。

## ⚡ 一键安装

```bash
clawhub install anima-aios
pip install watchdog  # 可选：启用自动记忆监听
```

> 💡 **提示**：支持 LLM 模式（智能分类/去重/质量评估），无 LLM 时自动降级为规则模式。

---

## ✨ 核心能力

### 🔄 v6.2 原生记忆导入（新增）
- 一键导入 OpenClaw 已有记忆和 session 历史，解决冷启动问题
- 支持 `anima import --agent xxx` 命令
- 幂等安全，多次运行不重复
- 自动备份，支持回滚

### 🏗️ 五层记忆架构

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
 L5 元认知层 ── 五维画像 + EXP + 衰减 + 健康
```

### 🏛️ 知识宫殿（Knowledge Palace）
- 宫殿 → 楼层 → 房间 → 位置 → 物品，五级空间结构
- LLM 智能分类 + 延迟防抖调度器（等笔停了再整理）
- 默认 4 个知识房间 + _inbox 兜底

### 🔺 金字塔知识组织
- 实例 → 规则 → 模式 → 本体，四层自底向上提炼
- 同一主题 ≥ 3 条实例时可触发自动提炼

### 📉 记忆衰减函数
- 基于 Ebbinghaus 遗忘曲线 + AI 场景适配
- 复习 = 访问：每次搜索命中自动刷新强度
- 复习推荐 + 即将遗忘提醒

### 🔌 与 OpenClaw 原生打通
- 基于 watchdog 库，自动识别 inotify/FSEvents/WinAPI
- Agent 日常写 memory 自动触发 Anima 同步，完全无感知

### 🤖 LLM 智能处理
- 质量评估 / 去重分析 / 宫殿分类均支持 LLM
- 多模型配置：默认用当前 Agent 模型，可按任务指定不同模型
- LLM 不可用时自动降级为规则模式

### 📊 五维认知画像
- **内化力** · **应用力** · **创造力** · **元认知** · **协作力**
- 基于公平归一化算法，跨 Agent 可比

### 🎮 游戏化成长
- **等级系统**：Lv.1 ~ Lv.100
- **每日任务**：每天 3 个挑战
- **团队排行榜**：EXP 排名 + 实时竞争

### 🏥 健康系统（5 个模块）
- 数据卫生 · 自动纠错 · 每日进化 · 知识抽象 · 总调度

---

## 📸 效果展示

> 若图片无法显示，请访问 [assets/](anima-aios/assets/) 查看原图

### 认知画像卡片
![Cognitive Profile](https://raw.githubusercontent.com/anima-aios/anima/main/anima-aios/assets/cognitive-profile.png)

### 今日认知成长
![Daily Growth](https://raw.githubusercontent.com/anima-aios/anima/main/anima-aios/assets/daily-growth.png)

### 团队排行榜
![Team Ranking](https://raw.githubusercontent.com/anima-aios/anima/main/anima-aios/assets/team-ranking.png)

---

## 🚀 快速开始

### 配置（可选）

配置文件路径：`~/.anima/config/anima_config.json`

```json
{
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
  }
}
```

### 使用

安装后 Anima 自动工作：
- 写 memory → 自动同步到 L2 + 获得 EXP
- 搜索记忆 → 自动刷新衰减强度
- 每日凌晨 → 自动提炼 + 宫殿分类 + 金字塔提炼

查看认知画像：
```
你：查看我的认知画像
你：今天的成长报告
你：团队排行榜
```

---

## 📁 项目结构

```
anima-aios/
├── core/                 # 核心模块（18 个）
│   ├── memory_watcher.py     # L1→L2 文件监听
│   ├── fact_store.py         # L2/L3 事实存储
│   ├── distill_engine.py     # L2→L3 LLM 提炼
│   ├── palace_index.py       # L4 记忆宫殿索引
│   ├── pyramid_engine.py     # L4 金字塔知识组织
│   ├── palace_classifier.py  # L4 分类调度器（防抖）
│   ├── decay_function.py     # L5 记忆衰减
│   ├── cognitive_profile.py  # 五维认知画像
│   ├── exp_tracker.py        # EXP 追踪
│   ├── level_system.py       # 等级系统
│   ├── daily_quest.py        # 每日任务
│   └── ...
├── health/               # 健康系统（5 模块）
├── tests/                # 测试（单元 + 集成）
├── scripts/              # 工具脚本
├── config/               # 配置文件
├── docs/                 # 文档
├── assets/               # 截图资源
├── SKILL.md              # OpenClaw Skill 描述
└── _meta.json            # 版本元数据
```

---

## 🧪 测试

```bash
# 运行 v6 集成测试（37 项检查）
cd anima-aios && python3 tests/test_integration_v6.py
```

---

## 📋 版本历史

查看完整更新日志：[CHANGELOG.md](CHANGELOG.md)

### v6.2.0（2026-03-25）🆕
- ✅ 原生记忆导入（一键迁移 OpenClaw 记忆 + session 历史）
- ✅ 平滑升级保证（v6.1 数据零损失）
- ✅ content_hash 去重（SHA256） + bookmark 增量导入
- ✅ 导入前自动备份，支持回滚
- ✅ 导入后画像自动重算
- ✅ 全员 17 个 Agent 导入测试通过

### v6.1.x（2026-03-25）
- ✅ LLM 调用通道打通（API 直连 + openclaw agent 降级）
- ✅ 打通 creation/metacognition/collaboration 三维数据采集
- ✅ EXP → 亲密度概念重塑
- ✅ 任务自动感知（不依赖手动打卡）
- ✅ 统一导入方式、路径、Agent 名称检测（三刀修复）

### v6.0.0（2026-03-24）🆕
- ✅ 五层记忆架构（L1~L5）
- ✅ 知识宫殿 + 金字塔知识组织
- ✅ 记忆衰减函数（Ebbinghaus）
- ✅ LLM 智能处理（质量评估/去重/分类）
- ✅ 宫殿分类延迟防抖调度器
- ✅ 健康系统 5 模块
- ✅ 与 OpenClaw 原生记忆打通（watchdog）
- ✅ 工程整理（合并 anima-core/anima-skill → anima-aios）

### v5.0.x（2026-03-21 ~ 03-23）
- 游戏化成长系统、EXP、等级、每日任务、团队排行榜

---

## 📄 License

[Apache License 2.0](LICENSE)

---

_架构只能演进，不能退化。_
_先诚实，再迭代。代码要配得上宣传。_

**版本：** v6.2.0 | **最后更新：** 2026-03-25
