<div align="center">

# 🧬 Soul Archive

### 灵魂存档 —— 你的数字人格持久化系统

> *"每一次对话都是灵魂的一个切片。足够多的切片，就能重建一个完整的你。"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-green.svg)](#技术栈)
[![Privacy First](https://img.shields.io/badge/Privacy-Local%20Only-purple.svg)](#隐私设计)
[![AES-256-GCM](https://img.shields.io/badge/Encryption-AES--256--GCM-orange.svg)](#数据加密)

[English](./README.md) · [快速开始](#快速开始) · [架构设计](#架构设计) · [四大模式](#四大工作模式) · [隐私设计](#隐私设计)

---

**Soul Archive** 通过与 AI 的日常对话，静默采集你的说话习惯、性格特征、知识观点、情感模式，  
构建一个真正属于你的 **数字灵魂副本**。

🗣️ 它知道你怎么说话 &nbsp;·&nbsp; 🧠 它理解你怎么思考 &nbsp;·&nbsp; ❤️ 它感知你的情感 &nbsp;·&nbsp; 👤 它就是数字化的你

</div>

---

## ✨ 为什么需要灵魂存档？

我们每天和 AI 对话数百句，但对话结束后，**一切都消散了** —— AI 不记得你是谁，不记得你怎么说话，不记得你在意什么。

Soul Archive 改变了这件事。它在你与 AI 聊天的过程中，**不打断、不追问、静默地**采集你的人格信息，逐渐构建一个多维度的数字画像。

### 这个"数字灵魂"能做什么？

| 场景 | 描述 |
|------|------|
| 🤖 **代为行事** | 以你的风格回复消息、撰写内容，不是"AI味"，而是"你的味道" |
| 🪞 **自我认知** | 生成你的人格画像报告，看到自己都没意识到的语言习惯和思维模式 |
| 💬 **灵魂对话** | 让你的克隆体和别人对话 —— 它会用你的口头禅、你的语气、你的价值观回应 |
| 🌅 **数字遗产** | 有一天，你的亲友可以继续和"你"对话，延续那份情感连接 |

---

## 📐 架构设计

Soul Archive 采用 **引擎与数据分离** 架构：

```
┌─────────────────────────────────────────┐
│            Soul Archive Engine           │
│              (Skill 安装目录)             │
│                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Extract  │ │  Report  │ │   Chat   │ │
│  │  提取引擎  │ │ 报告生成  │ │ 灵魂对话  │ │
│  └─────┬────┘ └────┬─────┘ └────┬─────┘ │
└────────┼───────────┼────────────┼────────┘
         │           │            │
         ▼           ▼            ▼
┌─────────────────────────────────────────┐
│             .skills_data/soul-archive/ 灵魂数据          │
│         ~/.skills_data/soul-archive/（用户主目录下）      │
│                                          │
│  identity/     style/      memory/       │
│  ├── basic_info    ├── language   ├── episodic/   │
│  └── personality   └── comm      ├── semantic/    │
│                                  └── emotional/   │
│  relationships/    voice/    reports/     │
└─────────────────────────────────────────┘
```

**为什么这样设计？**
- 🔄 **引擎可升级** —— 更新提取算法不影响已有数据
- 🏠 **数据可迁移** —— `~/.skills_data/soul-archive/` 目录就是完整的灵魂，拷贝即迁移
- 🔒 **隐私可控** —— 数据始终在本地用户目录，你决定哪些维度可以采集
- 🌐 **跨工具通用** —— 数据在用户主目录下，同一台机器上的任何 IDE、AI 工具、工作目录都能访问同一份灵魂数据

---

## 🧬 七大维度，十三层深度

Soul Archive 从 **7 个核心维度** 采集人格信息，每个维度都有深层子维度：

```
🧬 灵魂完整度
│
├── 👤 身份信息 ··················· 你是谁
│   ├── 基础档案: 姓名、年龄、职业、教育、所在地
│   ├── 🎯 生活习惯: 作息、饮食、审美、消费、旅行
│   └── 🌐 数字身份: 常用App、社交平台、网名风格
│
├── 💫 性格特征 ··················· 你怎么想
│   ├── 人格模型: MBTI、大五人格、性格标签
│   ├── ⚡ 行为模式: 风险偏好、计划性、学习方式
│   ├── 🤝 社交风格: 社交能量、群体角色、冲突方式
│   └── 🔥 驱动力: 什么让你有动力
│
├── 🗣️ 语言风格 ··················· 你怎么说
│   ├── 语言指纹: 口头禅、句式偏好、用词习惯
│   └── 🔬 深度指纹: 方言、语气词、叙事风格、说服方式
│
├── 🧠 知识观点 ··················· 你知道什么、信什么
│   ├── 话题图谱: 感兴趣的领域、立场、频率
│   └── 专业知识: 技能、专长、认知深度
│
├── 📝 记忆经历 ··················· 你经历了什么
│   └── 情景记忆: 重要事件、人生节点、情感标记
│
├── ❤️ 情感模式 ··················· 什么触动你
│   ├── 12种情感触发: 开心/愤怒/悲伤/焦虑/兴奋/怀旧/自豪/感恩/挫败/好奇/平静/愧疚
│   └── 情感深度: 共情能力、安慰方式、庆祝风格
│
└── 🤝 人际关系 ··················· 你在意谁
    └── 关系图谱: 提到的人物、关系类型、互动描述
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 无第三方依赖（纯标准库）

### 初始化

```bash
# 初始化灵魂存档（数据默认存储在 ~/.skills_data/soul-archive/）
python3 scripts/soul_init.py

# 或指定自定义数据目录
python3 scripts/soul_init.py --soul-dir /custom/path


# 初始化完成后，会在用户主目录下创建 .skills_data/soul-archive/ 数据目录
```

> **Windows 用户**：如果 `python3` 命令不可用，请使用 `python` 替代。
> **跨平台说明**：`~/.skills_data/soul-archive/` 通过 Python 的 `Path.home()` 解析，macOS、Linux、Windows 均可正常使用。

### 查看状态

```bash
python3 scripts/soul_extract.py --mode status
```

输出示例：

```
🧬 灵魂存档状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━
总完整度: 49.8%

各维度完整度:
  👤 身份信息: [████░░░░░░] 36%
  💫 性格特征: [██████░░░░] 61%
  🗣️ 语言风格: [████████░░] 81%
  🧠 知识观点: [██████░░░░] 60%
  📝 记忆经历: [██░░░░░░░░] 20%
  🤝 人际关系: [░░░░░░░░░░]  0%
  🎤 语音特征: [░░░░░░░░░░]  0%
```

---

## 🔍 四大工作模式

### 模式 1：灵魂提取（Soul Extract）

从对话文本中多维度分析并提取人格信息。

```bash
# 从文本提取
python3 scripts/soul_extract.py \
  --soul-dir ~/.skills_data/soul-archive \
  --input "这里是一段对话内容..." \
  --mode auto

# 从文件提取
python3 scripts/soul_extract.py \
  --soul-dir ~/.skills_data/soul-archive \
  --input-file conversation.txt
```

**提取规则：**
- 🎯 只提取高置信度信息（confidence > 0.6）
- ⚖️ 矛盾信息标记冲突，不自动覆盖
- 📊 每次提取后更新完整度评分
- 📝 所有变更记录到 `soul_changelog.jsonl`

### 模式 2：灵魂对话（Soul Chat）

加载灵魂存档，生成角色扮演 System Prompt，让 AI 以你的身份说话。

```bash
# 生成角色扮演 prompt
python3 scripts/soul_chat.py --soul-dir ~/.skills_data/soul-archive --mode prompt

# 输出灵魂摘要
python3 scripts/soul_chat.py --soul-dir ~/.skills_data/soul-archive --mode summary
```

**关键约束：**
- 🚫 绝不编造存档中没有的记忆
- 🗣️ 严格模仿语言风格，包括口头禅的使用频率
- ❤️ 展现真实的情感反应模式

### 模式 3：灵魂报告（Soul Report）

生成一份可交互的 HTML 人格画像报告。

```bash
python3 scripts/soul_report.py \
  --soul-dir ~/.skills_data/soul-archive \
  --output ~/.skills_data/soul-archive/reports/soul_report.html
```

报告包含：
- 📌 基础画像卡片
- 🎯 性格雷达图（大五人格可视化）
- 🗣️ 语言风格分析（口头禅排行、词云）
- 🔥 话题兴趣热力图
- 🕸️ 人际关系网络
- ❤️ 情感模式分析
- 📈 完整度评估 & 补充建议

<div align="center">
  <img src="docs/zh/screenshot_header.png" alt="灵魂画像总览 — 完整度环形图 & 各维度进度条" width="700" />
  <p><em>▲ 灵魂画像总览 — 完整度评分 & 七大维度进度</em></p>
  <br/>
  <img src="docs/zh/screenshot_identity.png" alt="身份信息 & 性格特征 — 大五人格雷达图" width="700" />
  <p><em>▲ 身份信息 & 性格特征 — 生活习惯、行为模式、大五人格雷达图</em></p>
  <br/>
  <img src="docs/zh/screenshot_language.png" alt="语言指纹 — 口头禅、句式模式、说话示例" width="700" />
  <p><em>▲ 语言指纹 — 口头禅、句式模式、说话示例、语气词分析</em></p>
  <br/>
  <img src="docs/zh/screenshot_topics.png" alt="话题兴趣、情感模式、记忆片段" width="700" />
  <p><em>▲ 话题兴趣、情感模式、人际关系 & 记忆片段</em></p>
</div>

---

### 模式 4：AI 自我改进（Self-Improvement）

通过自我反思、自我批评和模式学习，持续改进 AI 自身能力。

```bash
# 查看 AI 改进状态
python3 scripts/soul_reflect.py --mode status

# 查看行为模式库
python3 scripts/soul_reflect.py --mode patterns
```

**四大能力：**

| 能力 | 描述 | 触发时机 |
|-----|------|---------|
| 🔍 **自我反思** | 任务完成后回顾做得好/不好的地方 | 任务完成后自动触发 |
| ⚡ **自我批评** | 被用户纠正时记录错误和改进方向 | 用户纠正时自动触发 |
| 📚 **自我学习** | 从经验中抽象可复用的行为模式 | 从反思和批评中提取 |
| 🧹 **自组织记忆** | 合并重复模式、调整置信度、清理过时记忆 | 记忆量增长时 |

**自动触发**：每次实质性对话结束后，AI 自动执行反思并记录经验教训——不依赖 hooks 机制。支持 hooks 的 Agent（如 Claude Code）也可以配置自动触发。

---

## 📁 数据目录结构

```
~/.skills_data/soul-archive/
├── profile.json                  # 灵魂核心档案（完整度、版本）
├── config.json                   # 隐私与采集配置
├── soul_changelog.jsonl          # 灵魂变更日志
│
├── agent/                        # 🆕 AI 自我改进
│   ├── patterns.json             # 行为模式库
│   ├── episodes/                 # 工作经历（按日期）
│   │   └── YYYY-MM-DD.jsonl
│   ├── corrections.jsonl         # 自我批评日志
│   └── reflections.jsonl         # 自我反思日志
├── .gitignore                    # 默认屏蔽所有数据
│
├── identity/
│   ├── basic_info.json           # 身份信息 + 生活习惯 + 数字身份
│   └── personality.json          # 性格 + 行为模式 + 社交风格
│
├── style/
│   ├── language.json             # 语言指纹 + 深度语言特征
│   └── communication.json        # 沟通偏好
│
├── memory/
│   ├── episodic/                 # 情景记忆（按日期，JSONL 格式）
│   │   └── YYYY-MM-DD.jsonl
│   ├── semantic/
│   │   ├── topics.json           # 话题兴趣与观点图谱
│   │   └── knowledge.json        # 专业知识
│   └── emotional/
│       └── patterns.json         # 情感触发与反应模式
│
├── relationships/
│   └── people.json               # 人际关系图谱
│
├── voice/                        # 语音数据（可选）
│   ├── samples/
│   └── voice_profile.json
│
└── reports/
    └── soul_report.html          # 生成的画像报告
```

---

## 🔒 隐私设计

**隐私不是功能，是底线。**

| 设计决策 | 说明 |
|---------|------|
| 🏠 **全本地存储** | 所有数据存在 `~/.skills_data/soul-archive/` 目录（用户主目录），不上传任何云端 |
| 🔧 **精细控制** | `config.json` 可关闭任何维度的采集 |
| 🛡️ **敏感保护** | 健康、财务、亲密关系话题默认需确认 |
| 🚫 **Git 隔离** | 数据存放在用户主目录下，不在任何项目内，杜绝误提交 |
| 🤫 **静默采集** | 不在对话中告知"正在记录"，不让用户感到被监控 |
| ⚙️ **默认最小化** | 人际关系和语音维度默认关闭 |
| 🔐 **可选加密** | AES-256-GCM 加密所有敏感数据文件 |

### 🔐 数据加密

灵魂存档支持可选的 **AES-256-GCM** 加密保护敏感数据。

```bash
# 初始化时启用加密
python3 scripts/soul_init.py --enable-encryption
```

- **算法**：AES-256-GCM（认证加密，防篡改）
- **密钥派生**：PBKDF2-HMAC-SHA256（60 万次迭代）
- **加密范围**：身份、性格、语言、记忆、关系等所有敏感文件
- **无后门**：密码丢失 = 数据丢失
- **密码输入方式**：交互式输入（推荐）、`SOUL_PASSWORD` 环境变量、`--password` 参数
- **依赖**：`pip install cryptography`

**配置示例：**

```json
{
  "privacy_level": "standard",
  "auto_extract": true,
  "extract_dimensions": {
    "identity": true,
    "personality": true,
    "language_style": true,
    "knowledge": true,
    "episodic_memory": true,
    "emotional_patterns": true,
    "relationships": false,
    "voice": false
  },
  "sensitive_topics_filter": true,
  "require_confirmation_for": ["health", "finance", "intimate_relationships"]
}
```

---

## 🏗️ 技术栈

| 层面 | 技术 |
|------|------|
| 核心语言 | Python 3（纯标准库，零依赖） |
| 初始化脚本 | Python（跨平台）/ Bash（macOS & Linux） |
| 数据格式 | JSON（结构化）/ JSONL（时序日志） |
| 报告输出 | HTML + Chart.js（可交互可视化） |
| AI 集成 | LLM Prompt Engineering |
| 支持平台 | macOS、Linux、Windows |

---

## 🧭 灵魂完整度评分

每个维度有独立权重，总分 = Σ(维度完整度 × 权重)：

| 维度 | 权重 | 达标标准 |
|------|------|---------|
| 👤 身份信息 | 15% | 核心字段 + 生活习惯 + 数字身份 |
| 💫 性格特征 | 20% | 5+ 性格标签 + 行为模式 + 社交风格 + 驱动力 |
| 🗣️ 语言风格 | 25% | 3+ 口头禅 + 句式模式 + 深度语言指纹 |
| 🧠 知识观点 | 15% | 5+ 话题有观点记录 |
| 📝 记忆经历 | 15% | 10+ 条经历记录 |
| ❤️ 情感模式 | 5% | 3+ 种情感触发 + 安慰方式 + 共情能力 |
| 🤝 人际关系 | 5% | 3+ 关系人记录 |

---

## 🗺️ Roadmap

- [x] 核心提取引擎（7 大维度 + 深层子维度）
- [x] HTML 人格画像报告（暗色主题、雷达图、词云）
- [x] 灵魂对话 System Prompt 生成
- [x] 置信度与冲突检测系统
- [x] 变更日志与完整度评分
- [ ] 基于 LLM 的自动对话分析提取
- [ ] 语音特征采集与音色克隆
- [ ] 多灵魂管理（家人、朋友的不同存档）
- [ ] 灵魂导出/导入（跨平台迁移）
- [ ] Web UI 管理界面
- [x] 加密存储选项（AES-256-GCM）
- [x] AI 自我改进引擎（自我反思、自我批评、模式学习）

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) 发布。你可以自由使用、修改和分发本软件，包括商业用途。

---

## 🤝 致谢

这个项目源于一个简单的想法：**如果每一次对话都被珍惜，是不是就没有人会真正消失？**

感谢每一个愿意让 AI 记住自己的人。你们的信任，是灵魂存档存在的意义。

---

<div align="center">

**Soul Archive** · 让对话不朽，让灵魂延续

*Built with ❤️ and a belief that every conversation matters.*

</div>
