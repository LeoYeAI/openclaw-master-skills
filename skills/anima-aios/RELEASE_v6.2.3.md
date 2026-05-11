# Anima AIOS v6.2.3 发布说明

**发布日期：** 2026-03-26  
**类型：** 文档透明度提升 + 环境变量统一  
**上一版本：** v6.2.2

---

## 🔧 核心改进

### 1. 多平台路径说明

**新增：** SKILL.md 添加多平台路径支持表格

| 平台 | 默认路径 | 环境变量覆盖 |
|------|----------|-------------|
| **Linux** | `/home/画像` | `ANIMA_FACTS_BASE` |
| **macOS** | `~/画像` | `ANIMA_FACTS_BASE` |
| **Windows** | `~/画像` | `ANIMA_FACTS_BASE` |

**配置优先级：**
1. 环境变量 `ANIMA_FACTS_BASE`（最高）
2. 配置文件 `config.json`
3. 平台默认值

---

### 2. 网络调用说明

**新增：** SKILL.md + SECURITY.md 添加网络调用透明说明

**LLM API 调用（可选）：**

| 功能 | 用途 | 代码位置 |
|------|------|----------|
| **智能分类** | Knowledge Palace 分类 | `core/palace_classifier.py` |
| **语义去重** | Semantic Memory 去重 | `core/distill_engine.py` |
| **质量评估** | Episodic Memory 评估 | `core/quality_assessment.py` |

**安全机制：**
- ✅ API Key 用户自行提供
- ✅ 支持本地部署（无网络）
- ✅ 默认降级为规则模式（无 LLM）

---

### 3. 脚本用途说明

**新增：** SECURITY.md 添加所有脚本文件说明

| 脚本 | 用途 | 网络 | cron | 安全性 |
|------|------|------|------|--------|
| `post-install.sh` | 安装时复制 Core | ❌ | ❌ | ✅ |
| `refresh-quests.sh` | 刷新每日任务 | ❌ | ❌ | ✅ |
| `sync-memory.sh` | 定时同步记忆 | ❌ | ❌ | ✅ |
| `show-progress.sh` | 显示认知进度 | ❌ | ❌ | ✅ |

**所有脚本特点：**
- ✅ 仅本地文件操作
- ✅ 无网络调用
- ✅ 无 cron 注册
- ✅ 无系统修改

---

### 4. 环境变量统一

**改进：** config_loader.py 统一环境变量命名

**变更前：**
- `ANIMA_FACTS_BASE` ✅
- `ANIMA_AGENT_NAME` ✅
- `OPENCLAW_WORKSPACE` ⚠️
- `WORKSPACE` ❌

**变更后：**
- `ANIMA_FACTS_BASE` ✅ 主要
- `ANIMA_AGENT_NAME` ✅ 主要
- `OPENCLAW_WORKSPACE` ⚠️ 兼容（deprecated 警告）
- `WORKSPACE` ❌ 已移除

**Deprecated 警告：**
```python
import warnings
warnings.warn(
    "OPENCLAW_WORKSPACE is deprecated, use ANIMA_AGENT_NAME instead",
    DeprecationWarning,
    stacklevel=2
)
```

---

## 📝 变更清单

### 修改文件

| 文件 | 变更 | 说明 |
|------|------|------|
| `__init__.py` | 6.2.2 → 6.2.3 | 版本号更新 |
| `_meta.json` | 6.2.2 → 6.2.3 | 版本号更新 |
| `config_loader.py` | 添加 deprecated 警告 | 环境变量统一 |
| `SKILL.md` | 新增多平台路径 + 网络调用说明 | 文档透明度 |
| `SECURITY.md` | 新增脚本用途说明 | 文档透明度 |

### 新增文件

| 文件 | 说明 |
|------|------|
| `SECURITY_RESPONSE.md` | ClawHub 安全扫描正式回应 |
| `PLAN_v6.2.3.md` | v6.2.3 开发计划 |
| `RELEASE_v6.2.3.md` | 本文件 |

---

## 📊 影响评估

| 项目 | 影响 | 说明 |
|------|------|------|
| **现有用户** | 低 | 向后兼容，deprecated 警告 |
| **新用户** | 正面 | 文档更透明，易于理解 |
| **ClawHub 扫描** | 正面 | 回应所有关注点 |
| **代码质量** | 正面 | 环境变量统一 |

---

## 🧪 测试建议

### 环境变量测试
```bash
# 测试 ANIMA_AGENT_NAME
export ANIMA_AGENT_NAME=清禾
python3 core/config_loader.py

# 测试 OPENCLAW_WORKSPACE（应显示 deprecated 警告）
export OPENCLAW_WORKSPACE=/root/.openclaw/workspace-qinghe
python3 core/config_loader.py
```

### 多平台路径测试
```bash
# Linux
export ANIMA_FACTS_BASE=/home/画像
python3 core/path_config.py

# macOS
export ANIMA_FACTS_BASE=~/画像
python3 core/path_config.py
```

---

## 🔗 相关链接

- **GitHub:** https://github.com/anima-aios/anima
- **ClawHub:** k97dp1yp50dp76jfvr9a0yx63x83n2cb
- **安全回应:** SECURITY_RESPONSE.md
- **开发计划:** PLAN_v6.2.3.md

---

## 🙏 致谢

感谢 ClawHub 自动安全扫描系统的负责任审查，帮助我们提升文档透明度。

**架构只能演进，不能退化。**

---

_发布日期：2026-03-26_
_作者：清禾_
