# v6.2.3 开发计划 - 文档透明度提升

**创建日期：** 2026-03-26  
**目标发布：** 2026-03-27  
**优先级：** P1（文档改进）

---

## 📋 任务清单

### P1-1: 多平台路径说明表格

**文件：** SKILL.md, SECURITY.md

**内容：**
```markdown
## 🌍 多平台路径支持

Anima 支持多平台自动检测，默认路径如下：

| 平台 | 默认路径 | 环境变量覆盖 |
|------|----------|-------------|
| **Linux** | `/home/画像` | `ANIMA_FACTS_BASE` |
| **macOS** | `~/画像` | `ANIMA_FACTS_BASE` |
| **Windows** | `~/画像` | `ANIMA_FACTS_BASE` |

**配置优先级：**
1. 环境变量 `ANIMA_FACTS_BASE`（最高）
2. 配置文件 `config.json`
3. 平台默认值
```

**状态：** 📋 待实施

---

### P1-2: 网络调用说明

**文件：** SKILL.md, SECURITY.md

**内容：**
```markdown
## 🌐 网络调用说明

Anima 仅在以下情况使用网络调用：

### LLM API 调用（可选）

**用途：**
- 智能分类（Knowledge Palace）
- 语义去重（Semantic Memory）
- 质量评估（Episodic Memory）

**代码位置：**
- `core/distill_engine.py`
- `core/palace_classifier.py`
- `core/quality_assessment.py`

**安全机制：**
- ✅ API Key 用户自行提供
- ✅ 支持本地部署（无网络）
- ✅ 默认降级为规则模式

**配置示例：**
```json
{
  "llm": {
    "provider": "bailian",
    "api_key": "YOUR_API_KEY"
  }
}
```

**无 LLM 模式：**
- 所有 LLM 功能自动降级为规则模式
- 无需网络连接
- 功能完整，质量略降
```

**状态：** 📋 待实施

---

### P1-3: 脚本用途说明

**文件：** SECURITY.md

**内容：**
```markdown
## 📜 脚本文件说明

### post-install.sh

**用途：** 安装时复制 Core 文件 + 安装依赖

**操作：**
1. 检查 Python 和 Git
2. 安装 watchdog（可选）
3. 复制 core/ 到 ~/.anima/
4. 复制 config/ 到 ~/.anima/

**安全性：**
- ✅ 仅本地文件操作
- ✅ 无网络调用
- ✅ 无 cron 注册
- ✅ 无系统修改

### scripts/*.sh

| 脚本 | 用途 | 网络 | cron | 安全性 |
|------|------|------|------|--------|
| `refresh-quests.sh` | 刷新每日任务 | ❌ | ❌ | ✅ |
| `sync-memory.sh` | 定时同步记忆 | ❌ | ❌ | ✅ |
| `show-progress.sh` | 显示认知进度 | ❌ | ❌ | ✅ |

**所有脚本特点：**
- ✅ 仅本地文件操作
- ✅ 无网络调用
- ✅ 无 cron 注册
- ✅ 无系统修改
```

**状态：** 📋 待实施

---

### P1-4: 统一环境变量命名

**文件：** config_loader.py

**当前状态：**
- `ANIMA_FACTS_BASE` ✅ 主要
- `ANIMA_AGENT_NAME` ✅ 主要
- `OPENCLAW_WORKSPACE` ⚠️ 兼容（待 deprecated）
- `WORKSPACE` ❌ 兜底（待移除）

**改进方案：**

```python
def _detect_agent_name(self) -> str:
    """检测 Agent 名称
    
    优先级：
    1. 环境变量 ANIMA_AGENT_NAME ✅
    2. OpenClaw 上下文 OPENCLAW_WORKSPACE ⚠️ (兼容)
    3. 自动扫描 SOUL.md ✅
    4. 兜底值 "unknown" ✅
    """
    # 1. 主要环境变量
    env_name = os.getenv("ANIMA_AGENT_NAME")
    if env_name:
        return env_name
    
    # 2. 兼容 OpenClaw 环境变量（deprecated 警告）
    workspace = os.getenv("OPENCLAW_WORKSPACE")
    if workspace:
        import warnings
        warnings.warn(
            "OPENCLAW_WORKSPACE is deprecated, use ANIMA_AGENT_NAME instead",
            DeprecationWarning,
            stacklevel=2
        )
        # 从路径提取 Agent 名称
        parts = workspace.split("/")
        for part in reversed(parts):
            if part.startswith("workspace-"):
                return part.replace("workspace-", "")
    
    # 3. 自动扫描 SOUL.md
    # ...
```

**状态：** 📋 待实施

---

### P1-5: 安全回应文档

**文件：** SECURITY_RESPONSE.md

**状态：** ✅ 已完成

---

## 📊 进度追踪

| 任务 | 状态 | 预计时间 | 实际时间 |
|------|------|----------|----------|
| P1-1: 多平台路径说明 | 📋 待实施 | 30 分钟 | - |
| P1-2: 网络调用说明 | 📋 待实施 | 30 分钟 | - |
| P1-3: 脚本用途说明 | 📋 待实施 | 30 分钟 | - |
| P1-4: 统一环境变量 | 📋 待实施 | 1 小时 | - |
| P1-5: 安全回应文档 | ✅ 已完成 | 30 分钟 | 30 分钟 |

**总计：** 预计 3 小时

---

## 🎯 验收标准

### 文档完整性
- [ ] SKILL.md 包含多平台路径表格
- [ ] SKILL.md 包含网络调用说明章节
- [ ] SECURITY.md 包含脚本用途说明
- [ ] SECURITY_RESPONSE.md 已发布

### 代码改进
- [ ] config_loader.py 统一环境变量命名
- [ ] 添加 deprecated 警告
- [ ] 所有测试通过

### 版本统一
- [ ] __init__.py: 6.2.3
- [ ] _meta.json: 6.2.3
- [ ] config_loader.py: 6.2.3
- [ ] RELEASE_v6.2.3.md: 已创建

---

## 📝 发布清单

### 新增文件
- [ ] RELEASE_v6.2.3.md

### 修改文件
- [ ] SKILL.md（多平台路径 + 网络调用）
- [ ] SECURITY.md（脚本用途）
- [ ] config_loader.py（环境变量统一）
- [ ] __init__.py（版本号）
- [ ] _meta.json（版本号）

### Git 提交
- [ ] Git commit
- [ ] Git push
- [ ] GitHub 已更新

### ClawHub 发布
- [ ] 更新插件页安全回应
- [ ] 发布到 ClawHub

---

## 🔗 相关链接

- **GitHub:** https://github.com/anima-aios/anima
- **ClawHub:** k97dp1yp50dp76jfvr9a0yx63x83n2cb
- **安全回应:** SECURITY_RESPONSE.md

---

_创建人：清禾_
_创建日期：2026-03-26_
