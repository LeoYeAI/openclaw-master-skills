# 🧠 Smart Model Switcher V4

**多模态感知 • 会话级独立切换 • 零感知自动切换**

[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](https://github.com/davidme6/openclaw/tree/main/skills/smart-model-switcher-v4)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-purple.svg)](https://openclaw.ai)

## 🎯 概述

Smart Model Switcher V4 是 OpenClaw 的**智能模型自动切换工具**。根据您的任务类型（图片/代码/推理/写作），自动切换到最优模型，**无需手动操作**，切换延迟 <80ms。

### ✨ V4 核心升级

| 特性 | V3 | V4 |
|------|----|----|
| **多模态感知** | ❌ | ✅ 自动识别图片 |
| **图片理解** | ❌ | ✅ 自动切换视觉模型 |
| **会话级切换** | ❌ | ✅ 各通道独立，互不影响 |
| **任务感知** | 关键词匹配 | 智能上下文分析 |
| **自动切换** | 需要配置 | 零感知自动切换 |

### 🌟 核心功能

- 🖼️ **多模态感知** - 自动检测图片，切换到视觉模型 (qwen3-vl-plus)
- 💻 **代码优先** - 代码任务自动用 glm-5 (最强代码模型)
- 🧠 **推理优先** - 推理任务自动用 qwq-plus (最强推理)
- 🔒 **会话独立** - 每个聊天通道独立切换，互不影响
- ⚡ **零感知切换** - 无需手动，AI 自动判断并切换
- 🌍 **全平台支持** - Bailian (Qwen)、MiniMax、GLM、Kimi

## 🚀 快速开始

### 安装

#### 方式 1: 使用 ClawHub (推荐)
```bash
npx skills add davidme6/openclaw@smart-model-switcher-v4
```

#### 方式 2: 手动安装
```bash
# 克隆仓库
git clone https://github.com/davidme6/openclaw.git

# 复制 skill 到 OpenClaw 技能目录
cp -r openclaw/skills/smart-model-switcher-v4 `
  $env:USERPROFILE\AppData\Roaming\npm\node_modules\openclaw\skills\

# 重启 Gateway (一次性)
openclaw gateway restart
```

### 配置

在 `~/.openclaw/openclaw.json` 中配置各 Provider 的 API Key:

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "bailian": {
        "baseUrl": "https://dashscope.aliyuncs.com/v1",
        "apiKey": "sk-bailian-xxx",
        "api": "openai-completions"
      },
      "glm": {
        "baseUrl": "https://open.bigmodel.cn/api/paas/v4",
        "apiKey": "sk-glm-xxx",
        "api": "openai-completions"
      }
    }
  }
}
```

或使用环境变量:

```bash
export BAILIAN_API_KEY="sk-bailian-xxx"
export GLM_API_KEY="sk-glm-xxx"
```

## 📊 支持的模型

### 🖼️ 视觉模型（图片理解）
| 模型 | Provider | 视觉能力 | 推荐场景 |
|------|----------|----------|----------|
| qwen3-vl-plus | Bailian | ⭐⭐⭐⭐⭐ | 图片理解、OCR、图表分析 |
| qwen3.5-plus | Bailian | ⭐⭐⭐⭐ | 图片 + 文本混合任务 |
| qvq-max | Bailian | ⭐⭐⭐⭐⭐ | 复杂视觉推理 |

### 💻 代码模型（编程专用）
| 模型 | Provider | 代码能力 | 推荐场景 |
|------|----------|----------|----------|
| glm-5 | Bailian/GLM | ⭐⭐⭐⭐⭐ | 代码生成、Debug、重构 |
| qwen3-coder-plus | Bailian | ⭐⭐⭐⭐⭐ | 代码补全、项目开发 |
| qwen-coder-turbo | Bailian | ⭐⭐⭐⭐ | 快速代码任务 |

### 🧠 推理模型（复杂思维）
| 模型 | Provider | 推理能力 | 推荐场景 |
|------|----------|----------|----------|
| qwq-plus | Bailian | ⭐⭐⭐⭐⭐ | 复杂推理、数学证明 |
| qwen3-max | Bailian | ⭐⭐⭐⭐⭐ | 深度思考、分析 |
| glm-5 | Bailian/GLM | ⭐⭐⭐⭐ | 逻辑推理 |

### 📝 通用模型
| 模型 | Provider | 综合能力 | 推荐场景 |
|------|----------|----------|----------|
| qwen3.5-plus | Bailian | ⭐⭐⭐⭐ | 日常对话、写作、翻译 |
| qwen-plus | Bailian | ⭐⭐⭐ | 快速任务 |
| qwen-turbo | Bailian | ⭐⭐ | 简单任务、低成本 |

## 🔄 自动切换规则

### 规则 1: 图片检测优先
```
IF 消息包含图片/截图/照片 → 切换到视觉模型
  ├── 需要代码相关 → qwen3.5-plus (视觉 + 代码)
  ├── 纯图片理解 → qwen3-vl-plus (最强视觉)
  └── 复杂视觉推理 → qvq-max
```

### 规则 2: 代码任务
```
IF 消息包含代码关键词 → 切换到代码模型
  ├── 复杂代码任务 → glm-5 (最强代码)
  ├── 快速代码补全 → qwen-coder-turbo
  └── 项目级开发 → qwen3-coder-plus
```

### 规则 3: 推理任务
```
IF 消息包含推理关键词 → 切换到推理模型
  ├── 复杂推理 → qwq-plus (最强推理)
  ├── 数学/证明 → qwen3-max
  └── 一般分析 → glm-5
```

### 规则 4: 文本任务
```
IF 纯文本任务 → 使用通用模型
  ├── 长文档 → qwen3.5-plus (1M context)
  ├── 写作/翻译 → qwen3.5-plus
  └── 简单对话 → qwen-plus / qwen-turbo
```

## 📋 切换决策树

```
收到消息
    │
    ├── 🖼️ 包含图片？
    │       ├── YES → 是代码相关？
    │       │         ├── YES → qwen3.5-plus (视觉 + 代码)
    │       │         └── NO → qwen3-vl-plus (最强视觉)
    │       │
    │       └── NO ↓
    │
    ├── 💻 代码关键词？
    │       ├── YES → glm-5 (最强代码)
    │       │
    │       └── NO ↓
    │
    ├── 🧠 推理关键词？
    │       ├── YES → qwq-plus / qwen3-max
    │       │
    │       └── NO ↓
    │
    └── 📝 文本任务
            ├── 长文档 → qwen3.5-plus
            ├── 写作 → qwen3.5-plus
            └── 快速 → qwen-plus / qwen-turbo
```

## 🎯 使用示例

### 示例 1: 发送图片 + 代码问题
```
用户: [发送一张报错截图] "帮我看看这个错误"
检测: 图片 + 代码关键词
切换: qwen3.5-plus (视觉 + 代码能力)
提示: "🧠 已切换到 qwen3.5-plus（图片理解）"
执行: 分析截图中的错误，给出解决方案
```

### 示例 2: 纯代码任务
```
用户: "帮我写一个 Python 爬虫"
检测: 代码关键词
切换: glm-5 (最强代码模型)
提示: "🧠 已切换到 glm-5（代码任务）"
执行: 生成爬虫代码
```

### 示例 3: 纯图片理解
```
用户: [发送照片] "这张照片里有什么"
检测: 图片
切换: qwen3-vl-plus (最强视觉)
提示: "🧠 已切换到 qwen3-vl-plus（图片理解）"
执行: 描述图片内容
```

### 示例 4: 推理任务
```
用户: "证明根号 2 是无理数"
检测: 推理关键词
切换: qwq-plus (最强推理)
提示: "🧠 已切换到 qwq-plus（推理任务）"
执行: 给出证明过程
```

### 示例 5: 会话独立切换
```
WebChat 通道：发图片 → 切换到 qwen3.5-plus
飞书通道：写代码 → 保持 glm-5 (不受影响)
Telegram 通道：聊天 → 保持 qwen-plus (不受影响)

✅ 各通道独立，互不影响！
```

## 🔧 命令行工具

### 分析任务并选择模型
```powershell
# 检测任务类型
node scripts/auto-switch.js --check "帮我写个爬虫"

# 检测图片任务
node scripts/auto-switch.js --check "看这个截图" --has-image

# 手动切换模型
node scripts/auto-switch.js --switch bailian/glm-5

# 查看可用模型列表
node scripts/auto-switch.js --list
```

### 输出示例
```
🧠 任务分析结果：
  类型：coding
  推荐模型：bailian/glm-5
  原因：代码任务，使用最强代码模型

💡 切换命令：/model bailian/glm-5
```

## 📊 模型选择矩阵

| 场景 | 最优模型 | 切换命令 |
|------|----------|----------|
| 🖼️ 发送图片 | qwen3.5-plus | `session_status(model: "bailian/qwen3.5-plus")` |
| 💻 写代码 | glm-5 | `session_status(model: "bailian/glm-5")` |
| 🧠 推理/证明 | qwq-plus | `session_status(model: "bailian/qwq-plus")` |
| 📝 写作/翻译 | qwen3.5-plus | `session_status(model: "bailian/qwen3.5-plus")` |
| ⚡ 快速任务 | qwen-turbo | `session_status(model: "bailian/qwen-turbo")` |

## ⚡ 性能指标

| 指标 | V3 | V4 | 提升 |
|------|----|----|----|
| 多模态感知 | ❌ | ✅ | 新功能 |
| 图片理解 | ❌ | ✅ | 新功能 |
| 会话级切换 | ❌ | ✅ | 新功能 |
| 切换时间 | <80ms | <80ms | 保持 |
| 支持模型数 | 50+ | 50+ | 保持 |

## 🔒 会话级别切换（重要！）

**V4 核心特性：每个聊天通道独立切换，互不影响！**

| 通道 | 切换影响 |
|------|----------|
| WebChat 发图片 | 只影响 WebChat，飞书不变 |
| 飞书写代码 | 只影响飞书会话，WebChat 不变 |
| Telegram 聊天 | 只影响 Telegram，其他不变 |

**原理：**
- `session_status(model: "xxx")` 默认只切换**当前会话**的模型
- 不会影响其他通道的模型设置

## 📁 项目结构

```
smart-model-switcher-v4/
├── SKILL.md                  # OpenClaw 技能定义
├── _meta.json                # 元数据 (ClawHub)
├── README.md                 # 本文件
├── LICENSE                   # MIT 许可证
└── scripts/
    └── auto-switch.js        # 自动切换脚本
```

## 🆚 版本对比

| 特性 | V3 | V4 |
|------|----|----|
| 多模态感知 | ❌ | ✅ |
| 图片理解 | ❌ | ✅ |
| 会话级切换 | ❌ | ✅ |
| 自动检测 | 部分 | ✅ 完全自动 |
| 全平台支持 | ✅ | ✅ |
| API Key 验证 | ✅ | ✅ |
| 成本优化 | ✅ | ✅ |

## 🆘 故障排除

### Q: 为什么没有切换到某模型？
**A:** 检查当前会话的模型设置，或该模型的 API Key 无效。

### Q: 如何查看当前模型？
**A:** 使用 `/status` 命令查看当前会话的模型。

### Q: 如何手动覆盖自动切换？
**A:** 直接使用 `/model 模型名称` 手动指定。

### Q: 会影响其他聊天通道吗？
**A:** 不会！V4 支持会话级切换，各通道独立。

## 📞 支持

- **GitHub Issues:** [报告 Bug 或建议](https://github.com/davidme6/openclaw/issues)
- **ClawHub:** [技能页面](https://clawhub.com/skills/smart-model-switcher-v4)
- **Email:** davidme6@example.com

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 👨‍💻 作者

**davidme6**

- GitHub: [@davidme6](https://github.com/davidme6)
- ClawHub: [@davidme6](https://clawhub.com/@davidme6)

## 🙏 致谢

感谢 OpenClaw 团队提供的技能框架支持！

---

**Smart Model Switcher V4** - 发图片自动切视觉，写代码自动切代码，完全无感！🚀

**更新日期:** 2026-03-23
