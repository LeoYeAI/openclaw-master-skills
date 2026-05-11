# 问题 001：daily-review.js 提取逻辑太简单

**创建时间：** 2026-03-04  
**优先级：** 🔴 高  
**预计耗时：** 30 分钟  
**状态：** 待修复

---

## 📋 问题描述

### 现状

当前 `daily-review.js` 的 `analyzeFiles()` 方法只通过关键词匹配提取单行内容：

```javascript
// 第 82-104 行
const patterns = {
  project: [/✅.*完成/gi, /已完成/gi, /项目.*完成/gi],
  lesson: [/问题：/gi, /解决：/gi, /经验：/gi, /教训：/gi],
  moment: [/温暖/gi, /感动/gi, /谢谢/gi, /承诺/gi],
  decision: [/决定/gi, /选择/gi, /采用/gi],
  preference: [/喜欢/gi, /不喜欢/gi, /习惯/gi, /偏好/gi]
};

// 只匹配单行
lines.forEach((line, index) => {
  if (patterns.project.some(p => p.test(line))) {
    data.projects.push({
      date: file.date,
      content: line.trim(),  // ← 只保存这一行
      source: file.filename
    });
  }
});
```

### 问题

1. 只提取**匹配关键词的那一行**，不保留上下文
2. 不保留对话原文
3. 不做语义分析，无法识别重要程度
4. 无法实现 SKILL.md 中"详细对话记录"的设计目标

---

## 📊 影响分析

### 影响 1：丢失重要对话的详细信息

**例子：**
```markdown
## 💬 Amber 的批评 | 08:31

Amber: "当然要做严谨的调研啊，要只是敷衍了事，你不应该犯这样的错误"
小钳："你说得对！我确实犯了严重的错误"
```

**当前提取结果：**
```javascript
{ lessons: [{ content: "问题：当然要做严谨的调研啊" }] }
```

**应该提取的结果：**
```javascript
{
  criticalMoments: [{
    type: "lesson",
    importance: "critical",
    fullContent: "Amber: '当然要做严谨的调研啊...'\n小钳：'你说得对...'",
    context: "Amber 批评我调研敷衍",
    lesson: "调研 = 查资料 + 验证 + 有依据"
  }]
}
```

### 影响 2：凌晨整理脚本形同虚设

提取的信息太简略 → 更新到记忆文件的内容没有价值 → 整个整理流程失效

---

## ✅ 修复方案

### 步骤 1：引入 moment-detector 做语义分析

在 `analyzeFiles()` 方法中引入 `moment-detector.js`：

```javascript
// 在文件顶部引入
const MomentDetector = require('./moment-detector.js');

// 在 analyzeFiles 方法中
analyzeFiles(files) {
  const data = {
    criticalMoments: [],  // 新增
    projects: [],
    lessons: [],
    moments: [],
    decisions: [],
    preferences: []
  };

  const detector = new MomentDetector();

  files.forEach(file => {
    // 1. 先用关键词匹配（保留现有逻辑）
    const lines = file.content.split('\n');
    lines.forEach((line, index) => {
      // ... 现有代码 ...
    });
    
    // 2. 新增：调用 moment-detector 做语义分析
    const result = detector.detect(file.content);
    
    if (result && result.score >= 5) {
      // 提取完整对话段落
      const context = this.extractContext(lines, result.matched);
      
      data.criticalMoments.push({
        date: file.date,
        content: file.content,  // 保留完整原文
        type: result.type,
        score: result.score,
        suggestion: result.suggestion,
        context: context,
        source: file.filename
      });
    }
  });

  return data;
}
```

### 步骤 2：新增 extractContext 方法

```javascript
/**
 * 提取匹配行的上下文（前后各 5 行）
 */
extractContext(lines, matched) {
  const context = {
    before: [],
    matched: [],
    after: []
  };
  
  // 找到匹配行的索引
  const matchedIndices = [];
  lines.forEach((line, index) => {
    if (matched.keywords.some(k => line.includes(k)) ||
        matched.patterns.some(p => new RegExp(p).test(line))) {
      matchedIndices.push(index);
    }
  });
  
  // 提取上下文
  matchedIndices.forEach(idx => {
    const start = Math.max(0, idx - 5);
    const end = Math.min(lines.length, idx + 6);
    
    context.before.push(...lines.slice(start, idx));
    context.matched.push(lines[idx]);
    context.after.push(...lines.slice(idx + 1, end));
  });
  
  return context;
}
```

### 步骤 3：更新 updateEmotionMemory 处理 criticalMoments

在 `updateEmotionMemory()` 方法中增加对 `criticalMoments` 的处理：

```javascript
updateEmotionMemory(data) {
  // ... 现有代码 ...
  
  // 新增：处理 criticalMoments
  data.criticalMoments.forEach(moment => {
    if (moment.type === 'emotional' || moment.type === 'family') {
      if (!emotion.Amber.warmMoments) emotion.Amber.warmMoments = [];
      
      emotion.Amber.warmMoments.push({
        date: moment.date,
        content: moment.content,  // 完整原文
        context: moment.context,
        type: moment.type,
        importance: 'critical'
      });
    }
  });
  
  // ... 写入文件 ...
}
```

### 步骤 4：更新 updateKnowledgeBase 处理 criticalMoments

```javascript
updateKnowledgeBase(data) {
  // 合并 lessons 和 criticalMoments 中的经验教训
  const allLessons = [
    ...data.lessons,
    ...data.criticalMoments.filter(m => m.type === 'lesson')
  ];
  
  // ... 现有处理逻辑 ...
}
```

### 步骤 5：更新 updateCoreMemory 处理 criticalMoments

```javascript
updateCoreMemory(data) {
  // 处理 criticalMoments 中的情感交流、人生哲理等
  const criticalConversations = data.criticalMoments.filter(
    m => m.type === 'emotional' || m.type === 'philosophy' || m.type === 'promise'
  );
  
  criticalConversations.forEach(conv => {
    // 调用 memory-manager 的 updateCoreMemory 方法
    // 传入完整对话原文和上下文
  });
}
```

---

## 📝 修改文件清单

| 文件 | 修改内容 | 代码量 |
|------|----------|--------|
| `scripts/daily-review.js` | 引入 moment-detector + 增加 extractContext 方法 | +150 行 |
| `scripts/daily-review.js` | 更新 updateEmotionMemory | +30 行 |
| `scripts/daily-review.js` | 更新 updateKnowledgeBase | +10 行 |
| `scripts/daily-review.js` | 更新 updateCoreMemory | +20 行 |
| **总计** | | **+210 行** |

---

## ✅ 验收标准

- [ ] 能够提取完整对话原文，不只是单行
- [ ] 能够识别 critical 级别的重要时刻
- [ ] 保留对话上下文（前后各 5 行）
- [ ] 更新后的情感记忆包含完整对话内容
- [ ] 更新后的知识库包含详细经验教训
- [ ] 运行测试：`node scripts/daily-review.js` 无报错

---

## 🔗 相关文件

- 修改文件：`/root/openclaw/work/personify-memory/scripts/daily-review.js`
- 依赖文件：`/root/openclaw/work/personify-memory/scripts/moment-detector.js`

---

*最后更新：2026-03-04*
