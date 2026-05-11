# Anima AIOS v6.2.2 发布说明

**发布日期：** 2026-03-26  
**类型：** 功能增强 - per-Agent 配置覆盖  
**上一版本：** v6.2.1 (2026-03-26)

---

## 🔧 核心功能

### per-Agent 配置覆盖

**问题：** 多 Agent 场景下，全局配置无法满足个性化需求

**现状：**
- 配置文件全局共享 (`~/.anima/config/anima_config.json`)
- 所有 Agent 共用同一份配置
- 无法 per-Agent 定制 LLM、权重等

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

---

## 📝 变更清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `config/config_loader.py` | 配置加载器（支持 per-Agent 覆盖） |
| `config/agents/template.json` | Agent 覆盖配置模板 |

### 修改文件

| 文件 | 变更 |
|------|------|
| `config/path_config.py` | 集成新的配置加载器，支持 v6.2.2 配置结构 |
| `config/anima_config.template.json` | 版本 6.2.1 → 6.2.2，添加注释 |
| `SKILL.md` | 添加 v6.2.2 说明 + 配置结构文档 |
| `__init__.py` | 版本 6.2.1 → 6.2.2 |

### 移除

| 项目 | 说明 |
|------|------|
| `"agent"` 字段 | 改为运行时自动检测 |

---

## 🎯 配置优先级

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | 环境变量 | `ANIMA_FACTS_BASE`, `ANIMA_TEAM_MODE` 等（最高） |
| 2 | Agent 覆盖配置 | `~/.anima/config/agents/{agent_name}.json` |
| 3 | 全局配置 | `~/.anima/config/config.json` |
| 4 | 代码默认值 | `config_loader.py` 中的 DEFAULT_CONFIG |

---

## 📊 影响评估

| 项目 | 影响 | 说明 |
|------|------|------|
| **现有用户** | 低 | 向后兼容，旧配置继续有效 |
| **多 Agent 用户** | 高 | 配置管理大幅简化 |
| **代码改动** | 中 | 新增配置加载器，修改 path_config |
| **文档更新** | 中 | SKILL.md 配置章节重写 |

---

## 🔙 向后兼容

### 旧配置自动迁移

**检测到旧配置** (`anima_config.json`):
```json
{
  "agent": "Z",
  "facts_base": "/home/画像",
  ...
}
```

**自动迁移为:**
```
~/.anima/config/
├── config.json          # 全局配置（不含 agent 字段）
└── agents/
    └── Z.json           # Z 的覆盖配置
```

### 兼容层

- `path_config.py` 优先使用新配置加载器
- 失败时回退到旧配置读取
- 环境变量优先级保持最高

---

## 🧪 测试建议

### 配置加载测试

```bash
# 测试配置加载器
cd /root/.openclaw/skills/anima-aios
python3 config/config_loader.py

# 测试路径配置
python3 config/path_config.py
```

### 多 Agent 场景测试

```bash
# Agent A 使用默认配置
ANIMA_AGENT_NAME=Z python3 anima_doctor.py

# Agent B 使用覆盖配置
ANIMA_AGENT_NAME=方秋 python3 anima_doctor.py

# 验证配置隔离
ANIMA_AGENT_NAME=Z python3 -c "from config.config_loader import get_config; print(get_config()['llm'])"
ANIMA_AGENT_NAME=方秋 python3 -c "from config.config_loader import get_config; print(get_config()['llm'])"
```

---

## 📋 使用指南

### 步骤 1：创建全局配置

```bash
cp ~/.anima/config/anima_config.json ~/.anima/config/config.json
# 编辑 config.json，移除 "agent" 字段
```

### 步骤 2：创建 Agent 覆盖配置（可选）

```bash
mkdir -p ~/.anima/config/agents
cp /root/.openclaw/skills/anima-aios/config/agents/template.json ~/.anima/config/agents/Z.json
# 编辑 Z.json，只写需要覆盖的配置项
```

### 步骤 3：验证配置

```bash
python3 config/config_loader.py
```

---

## 💡 使用场景

### 场景 1：不同 Agent 使用不同 LLM

**Z** (需要高质量评估):
```json
{
  "llm": {
    "provider": "bailian",
    "models": {
      "quality_assess": "qwen-max"
    }
  }
}
```

**方秋** (使用默认):
```json
{}  // 无需覆盖，使用全局配置
```

### 场景 2：不同 Agent 不同权重

**流萤** (侧重创造力):
```json
{
  "weights": {
    "creation": 0.30,
    "understanding": 0.15
  }
}
```

**枢衡** (侧重元认知):
```json
{
  "weights": {
    "metacognition": 0.25,
    "creation": 0.15
  }
}
```

---

## 🔗 相关链接

- GitHub: https://github.com/anima-aios/anima
- 问题报告：方秋 (2026-03-26)
- 方案设计：清禾 (2026-03-26)

---

_架构只能演进，不能退化。—— 立文铁律_
_先诚实，再迭代。代码要配得上宣传。—— 清禾_
