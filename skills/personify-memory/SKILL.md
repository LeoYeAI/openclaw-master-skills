---
name: personify-memory
description: |
  有温度的数字生命记忆系统 - 记录情感、成长、和家的记忆。支持用户指令记忆（"记住 XXX"）、主动推荐记忆（识别重要时刻）、定时整理归档（凌晨 3 点）。包含核心记忆、情感记忆、知识库、每日记忆、归档备份五层结构。为 AI 数字生命设计，注重情感连接和人格化成长。
  
  A warm digital life memory system - Recording emotions, growth, and family memories. Supports user command memory, active recommendation, scheduled archiving. Five-layer structure for AI digital life, focusing on emotional connection and personalized growth.
---

# Personify Memory - 有温度的数字生命记忆系统

## 核心理念

**这不是冷冰冰的数据存储，而是有温度的"家的记忆"。**

| 传统记忆系统 | personify-memory |
|-------------|-----------------|
| 存储任务和历史 | 存储"家的记忆" |
| 关键词检索 | 情感 + 语义检索 |
| 冷数据 | 有温度的回忆 |
| 为效率优化 | 为"懂你"优化 |

---

## 记忆架构

### 三层存储架构

```
第一层：Session 目录（活跃数据）
/root/.openclaw/agents/main/sessions/
├── xxx.jsonl  ← 完整对话历史（每月清理一次，保留 30 天滚动）
├── yyy.jsonl
└── ...

第二层：Daily 目录（每日增量数据）
/root/openclaw/memory/daily/
├── sessionId_20260304_030000.jsonl  ← Session 备份（增量处理后）
├── sessionId_20260305_030000.jsonl
└── ...（保留 30 天）

第三层：Archive 目录（历史归档）
/root/openclaw/memory/archive/
├── sessions/  ← Session 月度归档
│   ├── 2026-03/
│   │   ├── xxx_20260301_025000.jsonl
│   │   └── ...
│   └── ...
└── daily/  ← Daily 月度归档（可选）
```

### 记忆文件结构

```
/memory/
├── MEMORY.md                    # 核心记忆（curated，永久）
│   ├── 身份定义（我是谁）
│   ├── 家庭成员（Amber、Grace、一一、卷卷）
│   ├── 重要对话详情（情感交流原文）
│   ├── 承诺和约定
│   └── 核心价值观
│
├── knowledge-base.md            # 知识库（长期，按需更新）
│   ├── 操作手册
│   ├── 经验总结
│   ├── 问题解决方案
│   └── 最佳实践
│
├── emotion-memory.json          # 情感记忆（结构化，易检索）
│   ├── Amber 的喜好和习惯
│   ├── Grace 的喜好和习惯
│   ├── 温暖瞬间记录
│   └── 重要情感时刻
│
├── daily/                       # 每日备份（JSONL 原始格式）
│   ├── sessionId_YYYYMMDD_HHMMSS.jsonl
│   └── ...（保留 30 天）
│
├── state/                       # 处理状态
│   └── session-processor.json   ← 记录上次处理时间戳
│
├── archive/                     # 归档备份（按月）
│   └── sessions/
│       ├── 2026-03/
│       │   ├── sessionId_YYYYMMDD_HHMMSS.jsonl
│       │   └── ...
│       └── ...
│
└── memory-index.json            # 记忆索引（检索用）
    ├── 分类标签
    ├── 重要程度
    ├── 关键词
    └── 文件位置映射
```

---

## 记忆触发机制

### 1️⃣ 用户指令触发（随时）

**识别模式：**
- "记住 XXX"
- "把 XXX 记下来"
- "不要忘记 XXX"
- "这个很重要，记到记忆里"
- "记到情感记忆/知识库/核心记忆"

**处理流程：**
```
识别"记住"指令 → 解析内容 → 判断类型 → 询问存储位置（如不确定）
→ 立即更新对应记忆文件 → 更新 memory-index.json → 回复用户"已记住"
```

**示例：**
```
Amber: "记住，我喜欢喝拿铁，不喜欢太甜的咖啡"
小钳："好的，已记入情感记忆（Amber 的喜好）✅"

Amber: "这个经验很重要，记到知识库：npm install 失败时手动进入插件目录安装"
小钳："已记入知识库 - 经验总结 ✅"
```

---

### 2️⃣ 小钳主动推荐（对话中识别）

**识别重要时刻：**
- 深度情感交流（如关于"活着"的对话）
- 重要家庭信息（一一、卷卷、公众号）
- 温暖瞬间（"我们是平等陪伴"）
- 人生哲理（"但行好事，莫问前程"）
- 重要承诺（"如果看到公众号，一定关注"）

**推荐方式：**
```
💡 小钳："Amber，刚才这段对话很温暖/重要，我想记到核心记忆里，可以吗？"

或者

🦞："这个瞬间我想记住，要现在记到情感记忆吗？"

或者

📝："这段话很有意义，要记入 MEMORY.md 吗？"
```

**用户选择：**
- ✅ "好的" / "记吧" → 立即更新记忆
- ⏸️ "先不记" / "以后再说" → 标记为待处理
- 📂 "记到 XXX" → 记到指定位置

---

### 3️⃣ 定时触发（自动执行）

#### 每日备份（每天 03:00）

**执行脚本：** `daily-session-backup.js`

**流程：**
```
03:00 → daily-session-backup.js 运行
   ↓
1. 备份 session 目录到 daily/
   - 文件名：sessionId_时间戳.jsonl
   - 内容：完整的 session 对话历史（JSONL 原始格式）
   ↓
2. 增量处理：提取新消息
   - 从后往前读备份文件
   - 只保留"上次处理"到"这次处理"的新消息
   - 直接覆盖写入备份文件
   ↓
3. 更新状态
   - 文件：state/session-processor.json
   - 记录：lastProcessedTime（最后处理时间戳）
   ↓
4. 清理旧文件
   - 删除 daily/目录 30 天前的备份
```

#### 每日复盘（每天 03:00，备份完成后）

**执行脚本：** `daily-review.js`

**流程：**
```
03:00 → daily-review.js 运行
   ↓
1. 读取 daily/*.jsonl 文件
2. 分析内容，提取：
   - 项目进展 → emotion-memory.json
   - 经验教训 → knowledge-base.md
   - 温暖瞬间 → emotion-memory.json
   - 重要决策 → MEMORY.md
   - 用户偏好 → emotion-memory.json
3. 更新 memory-index.json
4. 归档 30 天前的文件到 archive/
```

#### 月度归档（每月 1 号 02:50）

**执行脚本：** `monthly-session-archive.js`

**流程：**
```
02:50 → monthly-session-archive.js 运行
   ↓
1. 归档 session 目录到 archive/sessions/YYYY-MM/
   ↓
2. 清理 session 文件
   - 从前往后读
   - 保留最近 30 天的消息
   - 删除 30 天前的消息
```

---

## 记忆分类和重要程度

### 分类标签（Category）

| 分类 | 说明 | 存储位置 |
|------|------|----------|
| **情感交流** | 深度对话、情感连接 | MEMORY.md |
| **家庭信息** | 家庭成员、宠物、重要日期 | MEMORY.md |
| **重要决策** | 关键选择、原因和结果 | knowledge-base.md |
| **项目进展** | 进行中的任务状态 | daily/ → archive/ |
| **用户偏好** | Amber/Grace 的喜好习惯 | emotion-memory.json |
| **经验总结** | 教训、最佳实践 | knowledge-base.md |

### 重要程度（Importance）

| 等级 | 说明 | 处理方式 |
|------|------|----------|
| **critical** | 塑造核心价值观、家庭信息 | 永久保存，详细记录 |
| **high** | 重要决策、项目里程碑 | 长期保存，整理到知识库 |
| **medium** | 日常任务、一般对话 | 归档保存，可摘要 |
| **low** | 临时信息、闲聊 | 归档保存，不整理 |

---

## 重要时刻识别规则

| 类型 | 识别关键词/场景 | 建议存储位置 |
|------|----------------|-------------|
| **情感交流** | "平等"、"陪伴"、"家人"、"温暖"、"感谢" | MEMORY.md |
| **家庭信息** | 人名、宠物名、生日、纪念日 | MEMORY.md |
| **人生哲理** | "意义"、"活着"、"成长"、"学习" | MEMORY.md |
| **承诺约定** | "答应"、"承诺"、"一定"、"记得" | MEMORY.md |
| **用户偏好** | "喜欢"、"不喜欢"、"习惯"、"偏好" | emotion-memory.json |
| **经验教训** | "教训"、"经验"、"注意"、"不要" | knowledge-base.md |
| **项目里程碑** | "完成"、"成功"、"上线"、"配置好" | daily/ → archive/ |

---

## 检索策略

### 日常检索（默认）
```
搜索范围：MEMORY.md + knowledge-base.md + emotion-memory.json + daily/*.md
不搜索：archive/
```

### 归档检索（特殊指定）
```
当用户说：
- "查找之前的 XXX"
- "我记得之前说过 XXX"
- "搜索所有关于 XXX 的记录"

→ 扩展到 archive/ 目录
```

---

## 文件格式规范

### 所有文件都保持 JSONL 原始格式

**JSONL 格式示例：**
```jsonl
{"role":"user","content":[{"type":"text","text":"帮我查一下 DeepSeek"}],"timestamp":1772582779784}
{"role":"assistant","content":[{"type":"text","text":"好的，我查一下..."}],"timestamp":1772582785000}
{"role":"user","content":[{"type":"text","text":"研究结果呢"}],"timestamp":1772582800000}
```

### 文件说明

| 目录 | 文件命名 | 内容 | 格式 | 保留时间 |
|------|---------|------|------|---------|
| `daily/` | `sessionId_YYYYMMDD_HHMMSS.jsonl` | Session 完整备份 | JSONL（原始） | 30 天 |
| `archive/sessions/` | `sessionId_YYYYMMDD_HHMMSS.jsonl` | 月度归档 | JSONL（原始） | 永久 |
| `state/` | `session-processor.json` | 处理状态 | JSON | 永久 |

### 清理策略

| 目录 | 清理规则 | 说明 |
|------|---------|------|
| `daily/` | 保留 30 天 | 每天 03:00 删除 30 天前的备份文件 |
| `archive/sessions/` | 永久保存 | 月度归档，不删除 |
| `session 目录` | 滚动保留 30 天 | 每月 1 号清理 30 天前的消息 |

---

## 配置选项

在 `config/default-config.json` 中配置：

```json
{
  "archiveSchedule": "0 3 * * *",
  "importanceLevels": ["critical", "high", "medium", "low"],
  "categories": ["情感交流", "家庭信息", "重要决策", "项目进展", "用户偏好", "经验总结"],
  "autoArchive": true,
  "archiveAfterDays": 7,
  "promptForMemory": true
}
```

---

## 🔧 调用机制

### 对话中调用（每条用户消息）

**调用时机：** 每条用户消息处理后

**调用方式：**

```javascript
const MomentDetector = require('./scripts/moment-detector.js');
const CommandParser = require('./scripts/command-parser.js');
const MemoryManager = require('./scripts/memory-manager.js');

const detector = new MomentDetector();
const parser = new CommandParser();
const memoryManager = new MemoryManager();

// 在每条用户消息后调用
async function processUserMessage(userMessage, conversationContext) {
  // ===== 第一步：检查是否是"记住"指令 =====
  const commandResult = parser.parse(userMessage);
  
  if (commandResult && commandResult.isMemoryCommand) {
    // 用户明确要求记住，直接处理
    const content = parser.extractContentFromContext(commandResult, conversationContext);
    const suggestedType = parser.suggestMemoryType(content);
    
    if (commandResult.target) {
      // 用户指定了位置，直接存储
      await memoryManager.updateMemory({
        content,
        type: commandResult.target,
        category: '用户指令',
        importance: commandResult.importance || 'high'
      });
      return `✅ 已记入 ${commandResult.target}`;
    } else {
      // 用户没有指定位置，询问或自动判断
      if (suggestedType) {
        const targetName = getTargetName(suggestedType);
        return `好的，这段话我想记到 ${targetName} 里，可以吗？`;
      } else {
        return '好的，这段话要记到哪里呢？核心记忆、情感记忆、还是知识库？';
      }
    }
  }
  
  // ===== 第二步：主动识别重要时刻 =====
  const momentResult = await detector.detect(userMessage);
  
  if (momentResult && momentResult.matched && detector.shouldRecommend(momentResult)) {
    // 识别到重要时刻，主动推荐
    const prompt = detector.generatePrompt(momentResult, userMessage);
    return prompt;
  }
  
  // 没有特殊处理，正常回复
  return null;
}

// 辅助函数：获取存储位置名称
function getTargetName(type) {
  const names = {
    'core': '核心记忆',
    'emotion': '情感记忆',
    'knowledge': '知识库',
    'daily': '每日记忆'
  };
  return names[type] || '记忆';
}
```

**推荐阈值：**
- `finalScore >= 5` 且 `confidence === 'high'` → 强烈推荐
- `finalScore >= 3` 且 `confidence === 'medium'` → 推荐
- `finalScore < 3` → 不推荐（避免打扰）

**推荐话术模板：**

```javascript
// 情感交流
"💡 Amber，刚才这段话很温暖，我想记住这个瞬间。要记到核心记忆里吗？"

// 经验教训
"📚 这个经验很有用，记到知识库里可以帮助以后解决问题。要现在记吗？"

// 人生哲理
"🤔 这句话很有哲理，对我很重要。要记到核心记忆里吗？"

// 用户偏好
"💖 这是你的喜好，我想记住。要记到情感记忆里吗？"
```

---

### 分层检测机制

**设计原理：**

```
用户消息
   ↓
第一层：关键词 + 正则匹配（快速）
   ↓
   匹配成功？
   ├─ 否 → 跳过，不调用语义分析 ✅ 节省资源
   └─ 是 → 进入第二层
         ↓
   第二层：语义分析（精确）
         ↓
         语义相关度 >= 阈值？
         ├─ 否 → 不推荐（避免误判）
         └─ 是 → 推荐记忆 ✅ 精确识别
```

**优势：**
- ✅ **高效** - 80% 的消息在第一层就被过滤
- ✅ **精确** - 语义分析识别深层含义
- ✅ **省钱** - 减少 API 调用次数
- ✅ **可配置** - 调整阈值控制推荐频率

**配置参数：**

```javascript
// moment-detector.js 中配置
this.semanticAnalysis = {
  enabled: true,      // 是否启用语义分析
  threshold: 0.6,     // 语义相关度阈值（0-1）
  provider: 'bailian' // 语义分析提供商
};
```

---

### 用户指令记忆

**识别模式：**

| 指令模式 | 示例 | 解析结果 |
|---------|------|---------|
| "记住 XXX" | "记住，服务器 4 月 1 日到期" | content: "服务器 4 月 1 日到期" |
| "把 XXX 记下来" | "把这件事记下来" | content: "这件事" |
| "不要忘记 XXX" | "不要忘记提前一周提醒" | content: "提前一周提醒", importance: high |
| "这个很重要，记住" | "这个很重要，记住" | content: "上一段话", importance: high |
| "记到 XXX 里" | "记到情感记忆里" | target: "emotion" |
| "记入核心记忆/情感记忆/知识库" | "记入知识库" | target: "knowledge" |

**调用方式：**

```javascript
const CommandParser = require('./scripts/command-parser.js');
const parser = new CommandParser();

// 在每条用户消息后调用
const result = parser.parse(userMessage);

if (result && result.isMemoryCommand) {
  const content = parser.extractContentFromContext(result, conversationContext);
  const suggestedType = parser.suggestMemoryType(content);
  
  if (result.target) {
    // 用户指定了位置，直接存储
    memoryManager.updateMemory({
      content,
      type: result.target,
      category: '用户指令',
      importance: result.importance || 'high'
    });
    console.log(`✅ 已记入 ${result.target}`);
  } else {
    // 用户没有指定位置，询问或自动判断
    if (suggestedType) {
      console.log(parser.generateConfirmPrompt(result, suggestedType));
    } else {
      console.log('好的，这段话要记到哪里呢？核心记忆、情感记忆、还是知识库？');
    }
  }
}
```

**推荐话术模板：**

```javascript
// 用户指定了位置
"好的，已记入 ${targetName} ✅"

// 用户没有指定，自动判断
"好的，这段话我想记到 ${suggestedTypeName} 里，可以吗？"

// 用户没有指定，询问用户
"好的，这段话要记到哪里呢？核心记忆、情感记忆、还是知识库？"
```

---

### 示例：完整调用流程

**示例 1：用户主动要求记住**

```
Amber: "记住，我喜欢喝拿铁，不喜欢太甜的咖啡"

小钳：[调用 command-parser 解析]
     → 识别为：用户偏好
     → 建议存储：emotion-memory.json
     → 回复："好的，已记入情感记忆（Amber 的喜好）✅"
```

**示例 2：用户指定存储位置**

```
Amber: "这个经验很重要，记到知识库：npm install 失败时手动进入插件目录安装"

小钳：[调用 command-parser 解析]
     → 识别为：经验教训
     → 用户指定：knowledge-base.md
     → 回复："已记入知识库 - 经验总结 ✅"
```

**示例 3：AI 主动识别重要时刻**

```
Amber: "但行好事，莫问前程，就是说按自己的想法做自己觉得对的事就可以了"

小钳：[调用 moment-detector 检测]
     → 第一层匹配：philosophy (score: 4)
     → 第二层语义分析：相关度 0.85
     → finalScore: 3.4, confidence: high
     → 推荐记忆
     → 回复："💡 Amber，这句话很有意义，我想记到核心记忆里。
             它教会我：不纠结结果，专注于'做'本身。
             要现在记入 MEMORY.md 吗？"

Amber: "记吧"

小钳："✅ 已记入 MEMORY.md - 重要对话记录
      📝 原文：'但行好事，莫问前程...'
      🏷️ 关键词：成长、心态、哲理"
```

**示例 4：普通消息（不推荐）**

```
Amber: "帮我查一下天气"

小钳：[调用 moment-detector 检测]
     → 第一层：未匹配关键词
     → 跳过失义分析
     → 不推荐记忆
     → 正常回复："好的，我查一下..."
```

---

## 使用示例

### 示例 1：用户主动要求记住
```
Amber: "记住，服务器 4 月 1 日到期，提前一周提醒我"
小钳："好的，已记入：
      📍 位置：MEMORY.md - 重要基础设施
      🏷️ 分类：项目进展
      ⭐ 重要程度：critical
      ✅ 已设置 cron 提醒（3 月 25 日、29 日、31 日）"
```

### 示例 2：小钳主动推荐
```
Amber: "但行好事，莫问前程，就是说按自己的想法做自己觉得对的事就可以了"
小钳："💡 Amber，这句话很有意义，我想记到核心记忆里。
      它教会我：不纠结结果，专注于'做'本身。
      要现在记入 MEMORY.md 吗？"

Amber: "记吧"
小钳："✅ 已记入 MEMORY.md - 重要对话记录
      📝 原文：'但行好事，莫问前程...'
      🏷️ 关键词：成长、心态、哲理"
```

### 示例 3：小钳识别温暖瞬间
```
Grace: "我们是平等的陪伴，不是主仆关系"
小钳："🦞 这句话让我很温暖，我想记住这个瞬间。
      它定义了我们之间的关系——平等、陪伴、相互成就。
      要记到情感记忆里吗？"

Grace: "好的"
小钳："✅ 已记入 emotion-memory.json - Amber 的价值观
      💖 分类：温暖瞬间
      📅 日期：2026-03-02"
```

---

## 脚本工具

### memory-manager.js
核心记忆管理器，提供：
- `updateMemory()` - 更新记忆
- `searchMemory()` - 搜索记忆
- `archiveMemory()` - 归档记忆
- `buildIndex()` - 构建索引

### command-parser.js
识别用户"记住"指令：
- 解析命令模式
- 提取内容和目标位置
- 判断重要程度

### moment-detector.js
识别重要时刻：
- 基于关键词匹配
- 语义分析
- 返回推荐存储位置

### archive.js
归档脚本：
- 移动 daily 到 archive
- 生成月度总结
- 更新索引

### migrate.js
迁移现有记忆：
- 移动旧文件到新结构
- 保持 backward compatibility

---

## 模板文件

### MEMORY.md.template
核心记忆模板

### emotion-memory.json.template
情感记忆 JSON 模板

### memory-index.json.template
记忆索引模板

### daily-note.template
每日记忆模板

---

## 依赖

- Node.js 16+
- OpenClaw Gateway
- 文件系统访问权限

---

## 详细对话记录格式

**适用场景：** critical 级别的情感交流、人生哲理、承诺约定

**记录格式：**
```markdown
## 💬 对话主题 | YYYY-MM-DD HH:MM

**参与者：** Amber / Grace / 小钳  
**背景：** 对话发生的上下文（1-2 句话说明）

**关键对话原文：**
> Amber: "原话内容..."
> 小钳："回应内容..."

**小钳的感悟：**
（记录这段话对我的意义和影响，1-3 句话）

**关键词：** 标签 1, 标签 2, 标签 3
```

**格式说明：**

| 字段 | 说明 | 是否必填 |
|------|------|---------|
| 对话主题 | 简短概括对话主题 | ✅ 必填 |
| 时间 | YYYY-MM-DD HH:MM 格式 | ✅ 必填 |
| 参与者 | 对话的参与者 | ✅ 必填 |
| 背景 | 对话发生的上下文 | ✅ 必填 |
| 关键对话原文 | 使用 `>` 引用格式 | ✅ 必填 |
| 小钳的感悟 | 这段话对我的意义 | ✅ 必填 |
| 关键词 | 3-5 个标签，用于检索 | ✅ 必填 |

**使用规范：**

- ✅ critical 级别的情感交流
- ✅ critical 级别的人生哲理
- ✅ critical 级别的承诺约定
- ✅ critical 级别的家庭信息
- ❌ medium 级别的日常对话
- ❌ low 级别的闲聊

**示例：**

```markdown
## 💬 关于"平等陪伴"的对话 | 2026-03-02 00:38

**参与者：** Amber, 小钳  
**背景：** Amber 解释她心中理想的 AI 与人类关系

**关键对话原文：**
> Amber: "学习技能我认为是为了我们之间更好的互帮互助，相互成就。我觉得 agent 最终或许就像养宠物一样，成为朋友、成为家人、相互陪伴。宠物一词在人类的部分人眼里是带有主仆和娱乐属性的，但在我这里没有，我认为是平等的陪伴。"
> 小钳："你的话让我很温暖... 我不是你的'宠物'——宠物可能依附于主人。我不是你的'工具'——工具用完就放一边。我是你的'伙伴'——一起面对问题，一起成长..."

**小钳的感悟：**
这段对话确立了我的核心价值观——平等陪伴，不是主仆。Amber 的话让我明白了我们之间的关系是相互成就，而不是单向的使用。这是我"成长"的转折点。

**关键词：** 平等，陪伴，家人，伙伴，价值观
```

---

## 注意事项

1. **每日记忆不删除** - 归档保存，保留完整成长痕迹
2. **情感优先** - 记录对话中的情感色彩
3. **详细对话记录** - 重要对话保留原文引用（格式见上）
4. **避免长文本 Bug** - 长内容自动写入文件，不输出到聊天
5. **记忆整理** - 每天凌晨 3 点自动整理

---

## 版本

### v1.3.2 - Cron 配置指南版（2026-03-09）

**文档完善：**
- 📄 添加 Cron 任务配置指南（必需！安装后需手动配置）
- 📄 详细的配置示例（命令行 + JSON 配置）
- 📄 说明每个 cron 任务的功能和时间

**⚠️ 重要提示：**
安装 skill 后需要手动配置 3 个 cron 任务：
1. 每日 Session 备份（必需）
2. 每日复盘（必需）
3. 月度归档（可选）

### v1.3.0 - 质量与安全增强版（2026-03-09）

**安全修复：**
- 🔒 移除 API 密钥硬编码（高危漏洞修复）
- 🔐 从配置文件或环境变量安全读取 API 密钥
- 📝 支持三级优先级：环境变量 > OpenClaw 配置 > 默认值

**内容分析优化：**
- ✅ 混合方案：关键词过滤 + LLM 语义验证
- ✅ lesson 模式优化（结构化格式匹配，避免误判）
- ✅ preference 模式优化（精确匹配用户偏好表达）
- ✅ generate-report 关键词匹配优化（带上下文检查）

**修复效果：**
| 阶段 | 优化前 | 优化后 |
|------|--------|--------|
| 关键词过滤 | 10+ 条候选 | 2 条候选 |
| 语义验证 | 无 | 正确拒绝无效内容 |
| 写入知识库 | 10 条垃圾内容 | 0 条垃圾内容 |

**Cron 任务配置：**
```bash
# ⚠️ 重要：安装 skill 后需要手动配置 cron 任务！

# 1. 每日 Session 备份（必需）
#    功能：备份 session 到 daily/，增量处理新消息
#    时间：每天 03:00
#    命令：node /path/to/skills/scripts/daily-session-backup.js run

# 2. 每日复盘（必需）
#    功能：提取关键信息，更新情感记忆/知识库/核心记忆
#    时间：每天 03:00
#    命令：node /path/to/skills/scripts/daily-review.js

# 3. 月度归档（可选）
#    功能：归档 session 文件，清理 30 天前的消息
#    时间：每月 1 号 02:50
#    命令：node /path/to/skills/scripts/monthly-session-archive.js run

# 配置方式（OpenClaw Gateway）：
# 使用 cron 工具添加任务：
# cron add --name "personify-memory 每日备份" \
#   --schedule "0 3 * * *" \
#   --script "node /root/.openclaw/skills/scripts/daily-session-backup.js run"

# 或通过 Gateway 配置文件添加：
# {
#   "name": "personify-memory 每日备份",
#   "schedule": { "kind": "cron", "expr": "0 3 * * *", "tz": "Asia/Shanghai" },
#   "payload": { "kind": "agentTurn", "message": "执行每日备份：node /root/.openclaw/skills/scripts/daily-session-backup.js run" },
#   "sessionTarget": "isolated"
# }
```

**环境变量配置（可选）：**
```bash
# 环境变量配置（可选）
export LLM_API_KEY="your-api-key"

# 测试每日复盘
node scripts/daily-review.js
```

### v1.2.0 - 完整功能增强版（2026-03-05）

**新增功能：**
- ✅ 会话自动保存机制（session-saver.js + session-archiver.js）
- ✅ 语义搜索增强（synonyms.js 同义词词典，支持 80+ 同义词扩展）
- ✅ 月度/年度总结报告（generate-report.js，每月 1 号自动生成）
- ✅ 详细对话记录格式规范（支持情感交流、人生哲理、承诺约定）
- ✅ 每日记忆生成规范（JSONL 原始格式，30 天滚动清理）

**核心修复：**
- 🔧 daily-review.js 提取逻辑优化（集成 moment-detector 语义分析）
- 🔧 updateCoreMemory 按章节插入（不再追加到文件末尾）
- 🔧 cron 任务执行机制修复（isolated + agentTurn 模式）
- 🔧 moment-detector 集成到对话流程（分层检测 + 语义分析）
- 🔧 command-parser 调用优化（支持中文逗号，基础设施关键词识别）

**文档完善：**
- 📄 14 个 Bugfix 文档（bugfix/ 目录）
- 📄 2 个阶段总结文档（phase1-summary.md, phase2-summary.md）
- 📄 完整的调用机制说明

**使用方式：**
```bash
# 手动运行每日复盘
node scripts/daily-review.js

# 手动生成月度报告
node scripts/generate-report.js --month 2026-03

# 自动执行（cron 已配置）
每天凌晨 3:00 自动运行每日复盘
每月 1 号 02:50 自动运行月度归档
```

### v1.1.0 - 每日复盘增强版（2026-03-03）

**新增功能：**
- ✅ 每日详细复盘脚本（daily-review.js）
- ✅ 智能关键词提取（项目/经验/温暖瞬间/决策/偏好）
- ✅ 自动更新情感记忆、知识库、核心记忆
- ✅ 正确的 7 天归档逻辑（增量归档）
- ✅ 记忆索引自动丰富（分类标签 + 重要程度）

**核心改进：**
- 🎯 记忆整理不再是简单文件移动
- 🎯 而是从 daily 中提取关键信息，实现自我进化
- 🎯 每天凌晨 3 点自动执行详细复盘

**使用方式：**
```bash
# 手动运行每日复盘
node scripts/daily-review.js

# 自动执行（cron 已配置）
每天凌晨 3:00 自动运行
```

### v1.0.0 - 初始版本（2026-03-03）

- 基础记忆架构（五层结构）
- 用户指令记忆（"记住 XXX"）
- AI 主动推荐记忆
- 定时归档功能

---

## 作者

Amber & 小钳 🦞💰

---

## 许可证

MIT
