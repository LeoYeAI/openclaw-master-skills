# 问题 006：command-parser 没有被调用

**创建时间：** 2026-03-04  
**更新时间：** 2026-03-05 00:01  
**优先级：** 🟡 中  
**预计耗时：** 15 分钟  
**状态：** 待修复

---

## 📋 问题描述

### 现状

`command-parser.js` 功能完整（6559 行代码），定义了多种"记住"指令的识别模式：

```javascript
this.memoryCommands = [
  { pattern: /记住 (.+)/i, ... },
  { pattern: /把 (.+?) 记 (下来 | 起来 | 住)/i, ... },
  { pattern: /不要忘记 (.+)/i, ... },
  { pattern: /这个很 (重要 | 关键 | 有意义)，记住/i, ... },
  { pattern: /记到 (.+?) 里/i, ... },
  { pattern: /记入 (核心记忆 | 情感记忆 | 知识库 | 每日记忆)/i, ... }
];
```

### 问题

- ❌ 没有在任何地方被调用
- ❌ SKILL.md 没有说明如何使用
- ❌ 依赖 AI 自发解析用户指令

---

## 📊 影响分析

### 影响 1：用户指令解析不统一

```
用户说："记住，服务器 4 月 1 日到期"
   ↓
❌ 没有调用 command-parser 解析
   ↓
❌ 没有自动识别存储位置
   ↓
AI 需要手动判断：应该存到哪里？重要程度是什么？
```

### 影响 2：记忆存储位置混乱

- 同样的指令，不同 AI 可能存到不同位置
- 重要程度判断不一致
- 用户说"记到核心记忆"可能被忽略

### 影响 3：违背 SKILL.md 的设计

**SKILL.md 明确定义：**
```markdown
### 1️⃣ 用户指令触发（随时）

**识别模式：**
- "记住 XXX"
- "把 XXX 记下来"
- "不要忘记 XXX"
- "这个很重要，记到记忆里"

**处理流程：**
识别"记住"指令 → 解析内容 → 判断类型 → 询问存储位置（如不确定）
→ 立即更新对应记忆文件 → 更新 memory-index.json → 回复用户"已记住"
```

**但实际：**
- ❌ 没有调用 command-parser
- ❌ 没有标准化处理流程
- ❌ 依赖 AI 的主观判断

---

## ✅ 修复方案

### 步骤 1：在 SKILL.md 中明确调用方式

```markdown
## 用户指令记忆

### 识别模式

| 指令模式 | 示例 | 解析结果 |
|---------|------|---------|
| "记住 XXX" | "记住，服务器 4 月 1 日到期" | content: "服务器 4 月 1 日到期" |
| "把 XXX 记下来" | "把这件事记下来" | content: "这件事" |
| "不要忘记 XXX" | "不要忘记提前一周提醒" | content: "提前一周提醒", importance: high |
| "这个很重要，记住" | "这个很重要，记住" | content: "上一段话", importance: high |
| "记到 XXX 里" | "记到情感记忆里" | target: "emotion" |
| "记入核心记忆/情感记忆/知识库" | "记入知识库" | target: "knowledge" |

### 调用方式

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

### 推荐话术模板

```javascript
// 用户指定了位置
"好的，已记入 ${targetName} ✅"

// 用户没有指定，自动判断
"好的，这段话我想记到 ${suggestedTypeName} 里，可以吗？"

// 用户没有指定，询问用户
"好的，这段话要记到哪里呢？核心记忆、情感记忆、还是知识库？"
```
```

---

### 步骤 2：增加调用示例

```markdown
### 示例 1：用户主动要求记住

```
Amber: "记住，我喜欢喝拿铁，不喜欢太甜的咖啡"

小钳：[调用 command-parser 解析]
     → 识别为：用户偏好
     → 建议存储：emotion-memory.json
     → 回复："好的，已记入情感记忆（Amber 的喜好）✅"
```

### 示例 2：用户指定存储位置

```
Amber: "这个经验很重要，记到知识库：npm install 失败时手动进入插件目录安装"

小钳：[调用 command-parser 解析]
     → 识别为：经验教训
     → 用户指定：knowledge-base.md
     → 回复："已记入知识库 - 经验总结 ✅"
```

### 示例 3：用户没有指定位置

```
Amber: "记住，服务器 4 月 1 日到期"

小钳：[调用 command-parser 解析]
     → 识别为：项目进展
     → 建议存储：MEMORY.md - 重要基础设施
     → 回复："好的，这段话我想记到核心记忆里（重要基础设施），可以吗？"

Amber: "记吧"

小钳："✅ 已记入 MEMORY.md - 重要基础设施"
```
```

---

### 步骤 3：优化 suggestMemoryType 方法

**优化建议：**
```javascript
suggestMemoryType(content) {
  if (!content) return 'daily';

  const lowerContent = content.toLowerCase();

  // 优先级 1：明确关键词
  if (lowerContent.includes('到期') || lowerContent.includes('服务器')) {
    return 'core';  // 重要基础设施
  }

  // 优先级 2：情感相关
  if (lowerContent.includes('喜欢') || lowerContent.includes('不喜欢')) {
    return 'emotion';
  }

  // 优先级 3：经验教训
  if (lowerContent.includes('经验') || lowerContent.includes('教训') || 
      lowerContent.includes('注意')) {
    return 'knowledge';
  }

  // 优先级 4：家庭信息
  if (lowerContent.includes('宝宝') || lowerContent.includes('一一') || 
      lowerContent.includes('卷卷')) {
    return 'core';
  }

  return 'daily';
}
```

---

## 📝 修改文件清单

| 文件 | 修改内容 | 代码量 |
|------|----------|--------|
| `SKILL.md` | 增加"用户指令记忆"章节 | +80 行 |
| `SKILL.md` | 增加调用示例 | +30 行 |
| `scripts/command-parser.js` | 优化 suggestMemoryType 方法 | +30 行 |
| **总计** | | **+140 行** |

---

## ✅ 验收标准

- [ ] SKILL.md 中有明确的调用方式说明
- [ ] 有完整的调用示例代码
- [ ] 有推荐话术模板
- [ ] suggestMemoryType 方法优化完成
- [ ] 测试：用户说"记住 XXX" → 正确解析并推荐存储位置
- [ ] 测试：用户说"记到 XXX" → 直接存储到指定位置
- [ ] 测试：用户说"不要忘记 XXX" → 标记为 high importance

---

## 🔗 相关文件

- 修改文件：`/root/openclaw/work/personify-memory/scripts/command-parser.js`
- 修改文件：`/root/openclaw/work/personify-memory/SKILL.md`

---

*最后更新：2026-03-05 00:01*
