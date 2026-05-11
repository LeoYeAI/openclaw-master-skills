# 问题 005：moment-detector 没有集成到对话流程

**创建时间：** 2026-03-04  
**更新时间：** 2026-03-04 23:59  
**优先级：** 🟡 中  
**预计耗时：** 25 分钟  
**状态：** 待修复

---

## 📋 问题描述

### 现状

`moment-detector.js` 功能完整（9291 行代码），定义了 7 种重要时刻识别规则：

```javascript
this.rules = {
  emotional: {    // 情感交流 - critical
    keywords: ['平等', '陪伴', '家人', '温暖', '感谢', ...]
  },
  family: {       // 家庭信息 - critical
    keywords: ['宝宝', '孩子', '一一', '宠物', '猫猫', '卷卷', ...]
  },
  philosophy: {   // 人生哲理 - critical
    keywords: ['意义', '活着', '成长', '学习', '人生', ...]
  },
  promise: {      // 承诺约定 - high
    keywords: ['答应', '承诺', '一定', '记得', ...]
  },
  preference: {   // 用户偏好 - high
    keywords: ['喜欢', '不喜欢', '习惯', '偏好', ...]
  },
  lesson: {       // 经验教训 - high
    keywords: ['经验', '教训', '注意', '方法', ...]
  },
  milestone: {    // 项目里程碑 - medium
    keywords: ['完成', '成功', '上线', '配置好', ...]
  }
};
```

### 问题

- ❌ 没有在任何地方被调用
- ❌ SKILL.md 没有说明何时调用
- ❌ 依赖 AI 自发想起使用

---

## 📊 影响分析

### 影响 1：重要时刻被遗漏

**实际例子（2026-03-04 的对话）：**

```
Amber: "当然要做严谨的调研啊，要只是敷衍了事，你不应该犯这样的错误"
  ↓
  应识别为"经验教训"（lesson）
  ↓
  ❌ 没有被识别和推荐记忆

Amber: "personify-memory skill 也没有真实起到作用，让我很失望"
  ↓
  应识别为"重要反馈"
  ↓
  ❌ 没有被识别和推荐记忆

Amber: "你要优化自己的判断，而不是每次询问，这样你是具有智慧的"
  ↓
  应识别为"人生哲理"（philosophy）
  ↓
  ❌ 没有被识别和推荐记忆
```

### 影响 2：SKILL.md 的设计无法实现

**SKILL.md 明确定义：**
```markdown
### 2️⃣ 小钳主动推荐（对话中识别）

**识别重要时刻：**
- 深度情感交流
- 重要家庭信息
- 温暖瞬间
- 人生哲理
- 重要承诺

**推荐方式：**
💡 小钳："Amber，刚才这段对话很温暖/重要，我想记到核心记忆里，可以吗？"
```

**但实际：**
- ❌ 没有调用 moment-detector
- ❌ 没有主动推荐
- ❌ 依赖用户说"记住 XXX"

### 影响 3：记忆系统变成"被动记录"

**设计目标：**
```
用户对话 → AI 识别重要时刻 → 主动推荐 → 用户确认 → 记入记忆
```

**实际表现：**
```
用户对话 → 用户说"记住 XXX" → AI 记录
           ↓
       如果用户不说，就不记录
```

---

## ✅ 修复方案

### 核心设计：分层识别机制

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

---

### 步骤 1：增加分层检测逻辑

```javascript
class MomentDetector {
  constructor() {
    this.rules = { ... }; // 现有规则
    
    // 语义分析配置
    this.semanticAnalysis = {
      enabled: true,
      threshold: 0.6,  // 语义相关度阈值
      provider: 'bailian'
    };
  }

  /**
   * 分层检测
   */
  async detect(message, context = {}) {
    // ===== 第一层：关键词 + 正则匹配（快速）=====
    const layer1Result = this.layer1KeywordMatch(message);
    
    if (!layer1Result.matched) {
      // 关键词和正则都没匹配，直接返回
      console.log(`  ⏭️ 跳过语义分析：${message.substring(0, 20)}...`);
      return null;
    }
    
    console.log(`  ✅ 第一层匹配：${layer1Result.type} (score: ${layer1Result.score})`);
    
    // ===== 第二层：语义分析（精确）=====
    if (this.semanticAnalysis.enabled) {
      const layer2Result = await this.layer2SemanticAnalysis(message, layer1Result);
      
      if (layer2Result.relevance < this.semanticAnalysis.threshold) {
        console.log(`  ❌ 语义分析未通过：相关度 ${layer2Result.relevance} < ${this.semanticAnalysis.threshold}`);
        return null;
      }
      
      console.log(`  ✅ 语义分析通过：相关度 ${layer2Result.relevance}`);
      
      // 合并两层结果
      return {
        ...layer1Result,
        semanticRelevance: layer2Result.relevance,
        finalScore: layer1Result.score * layer2Result.relevance,
        confidence: layer2Result.relevance >= 0.8 ? 'high' : 'medium'
      };
    }
    
    return layer1Result;
  }

  /**
   * 第一层：关键词 + 正则匹配
   */
  layer1KeywordMatch(message) {
    const results = [];

    for (const [type, rule] of Object.entries(this.rules)) {
      const score = this.calculateScore(message, rule);
      
      if (score > 0) {
        results.push({
          type,
          score,
          matched: this.getMatchedDetails(message, rule),
          suggestion: {
            memoryType: rule.suggestType,
            category: rule.suggestCategory,
            importance: rule.importance,
            prompt: this.promptTemplates[type]
          }
        });
      }
    }

    if (results.length === 0) {
      return { matched: false };
    }

    results.sort((a, b) => b.score - a.score);
    return { matched: true, ...results[0] };
  }

  /**
   * 第二层：语义分析
   */
  async layer2SemanticAnalysis(message, layer1Result) {
    const prompt = this.buildSemanticPrompt(message, layer1Result);
    
    try {
      const response = await this.callModelAPI(prompt);
      
      return {
        relevance: response.relevance,
        reasoning: response.reasoning,
        confidence: response.confidence
      };
    } catch (error) {
      console.error('  ⚠️ 语义分析失败:', error.message);
      return { relevance: 0.7, reasoning: '降级使用关键词匹配' };
    }
  }

  /**
   * 构建语义分析 Prompt
   */
  buildSemanticPrompt(message, layer1Result) {
    return `请分析以下消息是否属于"${layer1Result.type}"类别，并给出相关度评分（0-1）。

消息内容：${message}

类别说明：
${this.getCategoryDescription(layer1Result.type)}

请返回：
1. relevance: 相关度（0-1 之间的数字）
2. reasoning: 判断理由（简短说明）
3. confidence: 置信度（high/medium/low）`;
  }

  /**
   * 获取类别说明
   */
  getCategoryDescription(type) {
    const descriptions = {
      emotional: '情感交流：表达情感、感谢、温暖、陪伴等情感连接的内容',
      family: '家庭信息：关于家庭成员、宠物、生日、纪念日等内容',
      philosophy: '人生哲理：关于人生意义、成长、学习、价值观等哲理性内容',
      promise: '承诺约定：答应、承诺、约定、保证等内容',
      preference: '用户偏好：喜欢、不喜欢、习惯、偏好等内容',
      lesson: '经验教训：经验、教训、注意事项、问题解决方法等内容',
      milestone: '项目里程碑：完成、成功、上线、配置好等进展内容'
    };
    return descriptions[type] || '';
  }
}
```

---

### 步骤 2：在 SKILL.md 中明确调用时机

```markdown
## 调用机制

### 对话中调用（每条用户消息）

**调用时机：** 每条用户消息处理后

**调用方式：**
```javascript
const MomentDetector = require('./scripts/moment-detector.js');
const detector = new MomentDetector();

const result = await detector.detect(userMessage);

if (result && result.finalScore >= 3) {
  // 识别到重要时刻，主动推荐
  console.log(result.suggestion.prompt);
  
  // 等待用户确认后调用 memory-manager.updateMemory()
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
```

---

### 步骤 3：增加调用示例

```markdown
### 示例 4：AI 主动识别重要时刻

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
```

---

## 📝 修改文件清单

| 文件 | 修改内容 | 代码量 |
|------|----------|--------|
| `scripts/moment-detector.js` | 增加分层检测逻辑 | +150 行 |
| `scripts/moment-detector.js` | 增加语义分析模块 | +100 行 |
| `SKILL.md` | 增加"调用机制"章节 | +50 行 |
| `SKILL.md` | 增加主动识别示例 | +20 行 |
| **总计** | | **+320 行** |

---

## ✅ 验收标准

- [ ] 第一层关键词匹配正常工作
- [ ] 第一层未命中时跳过失义分析
- [ ] 第一层命中时调用语义分析
- [ ] 语义分析返回相关度评分（0-1）
- [ ] 相关度低于阈值时不推荐
- [ ] 语义分析失败时降级使用第一层结果
- [ ] SKILL.md 中有明确的调用时机说明
- [ ] 有完整的调用示例代码
- [ ] 有推荐话术模板
- [ ] 测试：发送普通消息 → 第一层过滤，不调用语义分析
- [ ] 测试：发送重要消息 → 两层都通过，推荐记忆

---

## 🔗 相关文件

- 修改文件：`/root/openclaw/work/personify-memory/scripts/moment-detector.js`
- 修改文件：`/root/openclaw/work/personify-memory/SKILL.md`

---

*最后更新：2026-03-04 23:59*
