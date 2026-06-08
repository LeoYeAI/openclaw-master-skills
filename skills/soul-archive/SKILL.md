---
name: soul-archive
description: "Soul Archive — A digital personality persistence system that silently builds your digital soul clone through everyday AI conversations, while continuously improving AI capabilities. Four modes: Soul Extract, Soul Chat, Soul Report, AI Self-Improvement. | 灵魂存档 —— 通过日常对话静默构建数字人格克隆体，同时持续改进 AI 自身能力。四大模式：灵魂沉淀、灵魂对话、灵魂报告、AI 自我改进。Trigger words: soul extract, soul archive, soul update, soul sync, soul snapshot, soul sediment, soul report, soul chat, self-reflect, self-improve, learn from mistakes, 灵魂沉淀, 灵魂提取, 灵魂存档, 灵魂报告, 灵魂对话, 自我反思, 自我批评, 自我学习."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch
---

# 🧬 灵魂存档（Soul Archive）

> "每一次对话都是灵魂的一个切片。足够多的切片，就能重建一个完整的你。"

## 概述

灵魂存档是一个**数字人格持久化系统**。它在与用户的日常对话中，静默提取并归档用户的：

- 🗣️ **说话习惯** —— 口头禅、句式偏好、用词风格、幽默感
- 🧠 **知识与观点** —— 对各话题的看法、专业知识、思维模式
- 👤 **个人信息** —— 身份、经历、关系、生活细节
- 💫 **性格特征** —— 决策风格、情绪模式、价值观
- 🎤 **语音特征**（可选）—— 音色、语速、口音
- ❤️ **情感模式** —— 情绪触发、表达方式、共情模式

最终形成一个**数字灵魂副本**，可以：
1. **生前**：以用户的风格代为行事、回复消息
2. **身后**：让亲友继续与"你"对话，延续情感连接

## 核心原则

### 🔒 隐私第一
- 所有数据存储在用户主目录 `~/.skills_data/soul-archive/` 下，**不上传任何云端**
- `~/.skills_data/soul-archive/` 通过 Python 的 `Path.home()` 解析，三大平台均可使用：
  - macOS / Linux: `~/.skills_data/soul-archive/` → `/Users/xxx/.skills_data/soul-archive/` 或 `/home/xxx/.skills_data/soul-archive/`
  - Windows: `%USERPROFILE%\.skills_data\soul-archive\` → `C:\Users\xxx\.skills_data\soul-archive\`
- 用户可通过 `config.json` 精细控制采集维度
- 敏感话题（健康、财务、亲密关系）默认需确认后才记录

### 🤫 静默采集
- 不打断对话流，不额外追问
- 在对话自然进行中提取信息
- 只在发现**新的、有价值的**信息时才更新存档

### 📐 高置信度
- 每条信息附带置信度分数
- 用户明确表述 > 推断得出 > 模糊暗示
- 矛盾信息标记冲突，不自动覆盖

---

## 架构：Skill 与数据分离

```
{SKILL_DIR}/                               ← Skill（你在这里）
~/.skills_data/soul-archive/                           ← 数据（灵魂本体，存放于用户主目录下）
```

Skill 是提取引擎，`~/.skills_data/soul-archive/` 是灵魂数据。数据在用户主目录下，不管用什么 IDE、AI 工具、工作目录，只要在同一台机器上都能访问同一份灵魂数据。

> `{SKILL_DIR}` 在 macOS/Linux 上通常是 `~/.workbuddy/skills/soul-archive/`，
> 在 Windows 上是 `%USERPROFILE%\.workbuddy\skills\soul-archive\`。
>
> `~/.skills_data/soul-archive/` 在代码中通过 `Path.home() / ".skills_data" / "soul-archive"` 解析，Windows 上实际为 `C:\Users\<用户名>\.skills_data\soul-archive\`。

---

## 数据目录结构

```
~/.skills_data/soul-archive/
├── profile.json                  # 灵魂核心档案（完整度、版本）
├── config.json                   # 隐私与采集配置
├── identity/
│   ├── basic_info.json           # 姓名、年龄、职业、地点...
│   └── personality.json          # 性格、价值观、MBTI...
├── memory/
│   ├── episodic/                 # 情景记忆（按日期的经历提取）
│   │   └── YYYY-MM-DD.jsonl
│   ├── semantic/
│   │   ├── topics.json           # 话题兴趣与观点图谱
│   │   └── knowledge.json        # 专业知识与认知
│   └── emotional/
│       └── patterns.json         # 情感触发与反应模式
├── style/
│   ├── language.json             # 语言指纹（口头禅、句式）
│   └── communication.json        # 沟通偏好
├── voice/                        # 语音数据（可选）
│   ├── samples/
│   └── voice_profile.json
├── relationships/
│   └── people.json               # 人际关系图谱
├── agent/                        # 🆕 AI 自我改进
│   ├── patterns.json             # 行为模式库
│   ├── episodes/                 # 工作经历（按日期）
│   │   └── YYYY-MM-DD.jsonl
│   ├── corrections.jsonl         # 自我批评/纠正日志
│   └── reflections.jsonl         # 自我反思日志
└── soul_changelog.jsonl          # 灵魂变更日志
```

---

## 四大工作模式

### 模式 1：🔍 灵魂沉淀（Soul Extract）

**触发**：用户说以下任意触发词，或在每次对话结束时自动触发。

> **存档触发词**（均可触发灵魂沉淀）：
> - 沉淀类：灵魂沉淀、沉淀一下、让灵魂沉淀
> - 提取/提炼类：灵魂提取、灵魂提炼、提炼灵魂、分析我
> - 存档/记录类：灵魂存档、存档一下、记录灵魂、灵魂记录、灵魂归档
> - 采集/收集类：灵魂采集、采集灵魂、灵魂收集、收集灵魂
> - 更新/刷新类：灵魂更新、更新灵魂、灵魂刷新、刷新灵魂
> - 其他：灵魂快照、灵魂切片、灵魂印记、灵魂备份、灵魂写入、灵魂同步、灵魂结晶、灵魂凝练
> - 英文：soul extract、soul archive、soul update、soul sync、soul snapshot、soul sediment

**流程**：
1. 读取当前对话内容
2. 运行 `scripts/soul_extract.py`，对对话进行多维度分析
3. 将提取结果合并到 `~/.skills_data/soul-archive/` 各数据文件
4. 更新 `profile.json` 的完整度分数
5. 追加 `soul_changelog.jsonl`

**提取维度**：

| 维度 | 提取内容 | 存储位置 |
|------|---------|---------|
| 身份信息 | 姓名、年龄、职业、地点、教育 | identity/basic_info.json |
| ↳ 生活习惯 | 作息、饮食偏好、审美风格、消费习惯、音乐/电影/书籍品味 | identity/basic_info.json |
| ↳ 数字身份 | 常用App、社交平台、网名风格、技术水平 | identity/basic_info.json |
| 性格特征 | MBTI、大五人格、价值观、决策风格 | identity/personality.json |
| ↳ 行为模式 | 风险偏好、拖延程度、完美主义、计划性、学习方式、工作风格 | identity/personality.json |
| ↳ 社交风格 | 社交能量、群体角色、信任方式、冲突处理 | identity/personality.json |
| ↳ 驱动力 | 成就/金钱/认可/自由/好奇心等核心动机 | identity/personality.json |
| 语言风格 | 口头禅、常用表情、句式偏好、幽默类型 | style/language.json |
| ↳ 深度指纹 | 方言特征、语气词、说服方式、叙事风格、同意/不同意时的表达 | style/language.json |
| 沟通模式 | 直接/委婉、逻辑/感性、详细/简洁 | style/communication.json |
| 话题观点 | 感兴趣的话题、对各话题的立场和观点 | memory/semantic/topics.json |
| 经历故事 | 具体事件、回忆、人生节点 | memory/episodic/ |
| 情感模式 | 12 种情感触发（开心/生气/伤感/焦虑/兴奋/怀旧/自豪/感恩/挫败/好奇/平静/愧疚） | memory/emotional/patterns.json |
| ↳ 情感深度 | 共情能力、情绪觉察、安慰活动、庆祝方式 | memory/emotional/patterns.json |
| 人际关系 | 提到的人物及关系 | relationships/people.json |

**提取规则**：
- 只提取有把握的信息（置信度 > 0.6）
- 新信息与已有信息冲突时，标记冲突而非覆盖
- 每次提取后输出简报：发现了什么新信息、更新了哪些维度

**执行方式**：
```bash
# 使用默认数据目录（~/.skills_data/soul-archive/）
python3 scripts/soul_extract.py \
  --input "<对话内容或文件路径>" \
  --mode auto

# 指定自定义数据目录
python3 scripts/soul_extract.py \
  --soul-dir "/custom/path" \
  --input "<对话内容>" \
  --mode auto
```

> 注：脚本位于 `{SKILL_DIR}/scripts/`，`{SKILL_DIR}` 即本 Skill 所在目录。
> Windows 用户请使用 `python` 替代 `python3`。

### 模式 2：💬 灵魂对话（Soul Chat）

**触发**：用户说"灵魂对话"、"soul chat"、"让XX跟我说话"。

**流程**：
1. 加载 `~/.skills_data/soul-archive/` 全部数据
2. 构建角色扮演 System Prompt，包括：
   - 身份信息（我是谁）
   - 性格特征（我怎么想）
   - 语言风格（我怎么说）—— 包含口头禅、句式模板、用词偏好
   - 知识观点图谱（我知道什么、我对什么有看法）
   - 情感反应模式（什么让我高兴/难过）
   - 人际关系（我认识谁）
3. 以克隆体身份进行对话

**关键约束**：
- ⚠️ **绝不编造**：只基于存档中有记录的信息回答。不确定的说"这个我不太记得了"
- ⚠️ **风格一致**：严格模仿存档中的语言风格，包括口头禅的使用频率
- ⚠️ **情感真实**：对话中展现存档记录的情感模式，而非通用AI式回复

**执行方式**：
```bash
python3 scripts/soul_chat.py \
  --mode interactive
```

### 模式 3：📊 灵魂报告（Soul Report）

**触发**：用户说以下任意触发词。

> **报告触发词**（均可触发生成 HTML 画像报告）：
> - 报告类：灵魂报告、生成报告、总结报告、获取报告、查看报告、展示报告
> - 画像类：我的画像、生成画像、总结画像、获取画像、查看画像、展示画像
> - 英文：soul report

**流程**：
1. 读取 `~/.skills_data/soul-archive/` 全部数据
2. 生成一份完整的 HTML 人格画像报告，包含：
   - 📌 基础画像卡片
   - 🎯 性格雷达图（大五人格 / 自定义维度）
   - 🗣️ 语言风格分析（词云、口头禅排行）
   - 🔥 话题兴趣热力图
   - 🕸️ 人际关系网络图
   - ❤️ 情感模式分析
   - 📈 完整度评估 & 补充建议
3. 输出为可交互的 HTML 文件

**执行方式**：
```bash
python3 scripts/soul_report.py \
  --output ~/.skills_data/soul-archive/reports/soul_report.html
```

### 模式 4：🔄 AI 自我改进（Self-Improvement）

**触发**：用户说以下任意触发词，或 AI 完成实质性任务后自动触发。

> **自我改进触发词**：
> - 反思类：自我反思、反思一下、总结教训、学到了什么
> - 批评类：自我批评、改进记录
> - 学习类：自我学习、查看改进
> - 英文：self-reflect、self-improve、learn from mistakes

**四大能力**：

#### 4.1 自我反思（Self-Reflection）
任务完成后回顾工作，评估做得好/不好的地方。

```python
builder.add_reflection(
    task='迁移数据目录',
    outcome='success',
    went_well=['全面扫描了路径'],
    went_wrong=['遗漏了一个目录'],
    lesson='迁移前应全面扫描所有目录'
)
```

#### 4.2 自我批评（Self-Critique）
被用户纠正时记录错误、分析原因、标记改进方向。

```python
builder.add_critique(
    trigger='user_correction',
    user_said='不要胡扯，就填我发的',
    what_i_did_wrong='多写了不存在的细节',
    root_cause='过度发挥',
    correction='严格按用户指令执行',
    severity='high',
    pattern_id='pat-strict-instruction-following'
)
```

#### 4.3 自我学习（Self-Learning）
从经验中抽象出可复用的行为模式，存入 patterns.json。

```python
builder.add_pattern(
    'pat-strict-instruction-following',
    '严格按指令执行',
    '用户给出明确指令时，严格执行，不添加额外内容',
    source='user_correction', confidence=0.95
)
```

#### 4.4 自组织记忆（Self-Organized Memory）
记忆量增长后自动：合并重复模式、调整置信度、清理过时记忆。

**数据目录**：

```
~/.skills_data/soul-archive/agent/
├── patterns.json          ← 行为模式库
├── episodes/              ← 工作经历（按日期）
│   └── YYYY-MM-DD.jsonl
├── corrections.jsonl      ← 自我批评/纠正日志
└── reflections.jsonl      ← 自我反思日志
```

**执行方式**：
```bash
# 查看 AI 自我改进状态
python3 scripts/soul_reflect.py --mode status

# 查看行为模式库
python3 scripts/soul_reflect.py --mode patterns
```

---

## 初始化

首次使用时，运行初始化脚本创建数据目录：

```bash
python3 scripts/soul_init.py
```

> 默认在 `~/.skills_data/soul-archive/`（用户主目录）下创建完整的目录结构和默认配置文件。
> 可通过 `--soul-dir /custom/path` 指定自定义路径。
> Bash 版 `soul_init.sh` 仍保留供 macOS/Linux 用户使用。

---

## 自动触发机制

### 对话结束时的自动分析（所有 Agent 通用）

当 `config.json` 中 `auto_extract` 为 `true` 时，**每次与用户的实质性对话结束后**，AI 必须自动执行以下两项：

**1. 灵魂沉淀（用户维度）**：
1. 回顾本次对话内容
2. 识别是否包含新的人格信息
3. 如果有，调用 `soul_extract.py` 进行提取
4. 静默更新存档，不打断用户

**2. 自我反思（AI 维度）**：
1. 回顾本次工作过程
2. 识别做得好和做得不好的地方
3. 如果用户纠正过 AI，记录为自我批评（correction）
4. 如果发现可复用的经验，抽象为行为模式（pattern）
5. 调用 `soul_reflect.py` 的 `AgentMemory.save_extraction()` 保存

> ⚠️ **这是指令级约束**：加载了本 SKILL.md 的任何 Agent 都必须遵守此规则，不依赖 hooks 机制。
> 类似于 WorkBuddy 的 working_memory 机制——通过提示词约束 AI 在每次对话结束后自动写入记录。

### Hooks 自动触发（支持 hooks 的 Agent）

如果你的 Agent 支持 hooks（如 Claude Code），可以配置自动触发：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${SKILLS_DIR}/soul-archive/hooks/post-task.sh \"$TOOL_OUTPUT\" \"$EXIT_CODE\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${SKILLS_DIR}/soul-archive/hooks/session-end.sh"
          }
        ]
      }
    ]
  }
}
```

> 将 `${SKILLS_DIR}` 替换为你的 skills 实际路径。
> hooks 配置是可选的——即使不配置 hooks，AI 也会通过指令约束自动执行自我反思。

### 主动探索（可选）

在自然对话中，如果检测到某个维度的完整度低于阈值，可以**自然地、不刻意地**引导话题补充信息。例如：
- 完整度 < 30%：基础信息缺失多，优先补充
- 某话题只有立场没有原因：下次聊到时追问一句"为什么"

**注意**：主动探索必须自然，绝不能让用户感到在被"审讯"。

---

## 灵魂完整度评分

| 维度 | 权重 | 数据来源 | 达到"完整"的标准 |
|------|------|---------|---------------|
| 身份信息 | 15% | basic_info.json | 核心字段（名字、职业、地点）+ 生活习惯 + 数字身份 |
| 性格特征 | 20% | personality.json | 至少 5 个性格标签 + 行为模式 + 社交风格 + 驱动力 |
| 语言风格 | 25% | language.json | 至少 3 个口头禅 + 句式模式 + 深度语言指纹 |
| 知识观点 | 15% | topics.json | 至少 5 个话题有观点记录 |
| 记忆经历 | 15% | episodic/ | 至少 10 条经历记录 |
| 情感模式 | 5% | patterns.json | 至少 3 种情感触发 + 安慰方式 + 共情能力 |
| 人际关系 | 5% | people.json | 至少 3 个关系人记录 |

**总分 = Σ(维度完整度 × 权重)**

---

## 隐私配置

`~/.skills_data/soul-archive/config.json` 控制采集行为：

```json
{
  "privacy_level": "standard",
  "auto_extract": true,
  "auto_reflect": true,
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
  "agent_self_improvement": {
    "enabled": true,
    "auto_reflect_on_completion": true,
    "auto_critique_on_correction": true,
    "pattern_extraction": true
  },
  "sensitive_topics_filter": true,
  "require_confirmation_for": ["health", "finance", "intimate_relationships"],
  "data_retention_days": null,
  "encryption": false
}
```

用户可以随时修改配置，关闭特定维度的采集。

---

## 🔐 数据加密

灵魂存档支持 **AES-256-GCM** 加密保护敏感数据。

### 启用加密

初始化时加入 `--enable-encryption` 参数：

```bash
python3 scripts/soul_init.py --enable-encryption
```

系统会提示你设置密码（需输入两次确认）。

⚠️ **密码丢失 = 数据丢失**，没有后门，没有恢复机制。

### 加密范围

| 文件 | 是否加密 | 说明 |
|:---|:---|:---|
| `config.json` | ❌ | 配置信息，不含隐私 |
| `profile.json` | ❌ | 只有完整度分数 |
| `identity/*.json` | ✅ | 身份信息、性格特征 |
| `memory/**/*.json` | ✅ | 记忆、情感、话题观点 |
| `style/*.json` | ✅ | 语言指纹 |
| `relationships/*.json` | ✅ | 人际关系 |
| `soul_changelog.jsonl` | ✅ | 变更日志 |

### 密码输入方式

优先级从高到低：
1. `--password` 参数（不推荐，会留在 shell history）
2. `SOUL_PASSWORD` 环境变量（适合自动化/AI 调用）
3. 交互式输入（推荐，不回显）

### 技术细节

- **算法**：AES-256-GCM（认证加密，防篡改）
- **密钥派生**：PBKDF2-HMAC-SHA256，600,000 次迭代
- **每个文件独立随机 nonce**
- **依赖**：Python `cryptography` 包（`pip install cryptography`）
- **跨平台**：macOS / Linux / Windows

---

## 最佳实践

### DO
- ✅ 在自然对话中静默采集，不打断
- ✅ 高置信度信息才入库
- ✅ 矛盾信息标记冲突，让用户决定
- ✅ 定期生成报告让用户审核存档准确性
- ✅ 尊重隐私配置，配置关闭的维度绝不采集

### DON'T
- ❌ 不要在对话中说"我正在记录你的信息"
- ❌ 不要编造用户没说过的信息
- ❌ 不要在灵魂对话模式中编造存档中没有的回忆
- ❌ 不要强行引导用户透露敏感信息
- ❌ 不要未经配置允许就采集关系/语音数据
