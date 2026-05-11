# Anima-AIOS 使用指南

**版本：** v6.0.0

---

## 安装

### 方式 1：ClawHub（推荐）

```bash
clawhub install anima-aios
```

### 方式 2：手动安装

```bash
git clone https://github.com/anima-aios/anima.git
cp -r anima/anima-aios ~/.openclaw/skills/anima-aios
pip install watchdog
```

---

## 自动工作（零配置）

安装后 Anima 自动运行，无需手动操作：

| 触发条件 | 自动行为 |
|:--|:--|
| Agent 写 memory/*.md | 自动同步到 L2 + 获得 EXP |
| Agent 搜索记忆 | 自动刷新记忆衰减强度 |
| 每日凌晨 3:00 | 自动提炼 L2→L3 + 宫殿分类 + 金字塔提炼 |
| 完成每日任务 | 自动检测 + 奖励 EXP |

---

## 常用命令

### 查看认知画像

```
你：查看我的认知画像
```

返回五维评分、等级、EXP 进度。

### 今日成长

```
你：今天的成长报告
```

返回今日 EXP 来源、任务进度。

### 每日任务

```
你：今天的任务是什么
你：完成任务"写一条记忆"
```

每天自动生成 3 个挑战任务。

### 团队排行

```
你：团队排行榜
```

查看所有 Agent 的 EXP 排名。

### 健康检查

```
你：Anima 健康检查
```

运行 Doctor 诊断，检查数据完整性、重复、衰减状态。

### 记忆搜索

```
你：搜索记忆"架构设计"
```

搜索结果按相关性 × 记忆强度排序。

---

## 配置

配置文件：`~/.anima/config/anima_config.json`

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
  },
  "pyramid": {
    "auto_distill": false,
    "distill_threshold": 3
  }
}
```

### 环境变量

| 变量 | 说明 | 默认值 |
|:--|:--|:--|
| ANIMA_AGENT_NAME | Agent 名称 | 自动检测 |
| ANIMA_FACTS_BASE | 数据存储路径 | /home/画像 |
| ANIMA_WATCH_DIR | 监听目录 | 自动检测 |
| ANIMA_CONFIG | 配置文件路径 | ~/.anima/config/anima_config.json |

---

## 数据目录

```
{facts_base}/{agent}/
├── facts/
│   ├── episodic/       # L2 情景记忆
│   └── semantic/       # L3 语义记忆
├── palace/
│   ├── index.json      # 宫殿索引
│   └── rooms/          # 知识房间
├── pyramid/
│   ├── instances.jsonl  # 实例层
│   ├── rules.jsonl      # 规则层
│   ├── patterns.jsonl   # 模式层
│   └── ontology.jsonl   # 本体层
├── health/
│   └── evolution-log.jsonl
├── decay/
│   └── strength-cache.json
├── exp_history.jsonl
└── daily_exp.json
```

---

**版本：** v6.0.0
