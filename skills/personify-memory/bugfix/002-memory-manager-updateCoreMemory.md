# 问题 002：memory-manager.js 的 updateCoreMemory 直接追加到文件末尾

**创建时间：** 2026-03-04  
**优先级：** 🔴 高  
**预计耗时：** 20 分钟  
**状态：** 待修复

---

## 📋 问题描述

### 现状

当前 `memory-manager.js` 的 `updateCoreMemory()` 方法是 TODO 状态，直接追加内容：

```javascript
// 第 103-108 行
async updateCoreMemory(content, title, category, tags) {
  const filePath = path.join(this.basePath, 'MEMORY.md');
  
  // TODO: 实际实现应该解析 Markdown 并插入到合适位置
  // 这里简化处理，追加到文件末尾
  const appendContent = `\n\n---\n\n## ${title || '新记忆'}\n\n${content}\n`;
  fs.appendFileSync(filePath, appendContent, 'utf-8');
  
  return entry;
}
```

### 问题

1. 直接追加到文件末尾，破坏 MEMORY.md 的章节结构
2. 没有根据 category 插入到对应章节（情感交流/家庭信息/经验总结等）
3. 导致 MEMORY.md 越来越乱，无法按分类查找

---

## 📊 影响分析

### 影响 1：MEMORY.md 结构混乱

**期望结构：**
```markdown
# 🦞💰 小钳的长期记忆

## 👤 主人信息
...

## 💬 重要对话记录
- 情感交流内容
- 家庭信息

## 🦞 小钳的身份
...

## 📚 重要经验总结
- 经验教训内容
```

**实际结果（追加后）：**
```markdown
# 🦞💰 小钳的长期记忆

## 👤 主人信息
...

## 💬 重要对话记录
...

## 新记忆  ← 追加在这里，不属于任何章节
一些内容

## 🦞 小钳的身份
...

## 另一个新记忆  ← 又追加在这里
更多内容
```

### 影响 2：违背设计规范

SKILL.md 明确要求按分类存储，但当前实现没有按分类插入。

---

## ✅ 修复方案

### 步骤 1：定义章节映射

```javascript
// 在类构造函数中或作为常量
const SECTION_MAP = {
  '情感交流': '## 💬 重要对话记录',
  '家庭信息': '## 👨‍👩‍👦 家庭成员',
  '经验总结': '## 📚 重要经验总结',
  '人生哲理': '## 🤔 人生哲理',
  '承诺约定': '## 🤝 承诺约定',
  '项目进展': '## 🎯 当前项目状态',
  '用户偏好': '## 💡 偏好和习惯'
};
```

### 步骤 2：实现 Markdown 解析和插入

```javascript
async updateCoreMemory(content, title, category, tags) {
  const filePath = path.join(this.basePath, 'MEMORY.md');
  
  // 1. 读取现有内容
  let fileContent = '';
  if (fs.existsSync(filePath)) {
    fileContent = fs.readFileSync(filePath, 'utf-8');
  } else {
    // 文件不存在，创建模板
    fileContent = this.getMemoryTemplate();
  }
  
  // 2. 根据 category 找到对应章节
  const sectionTitle = SECTION_MAP[category] || '## 其他记录';
  const sectionIndex = fileContent.indexOf(sectionTitle);
  
  if (sectionIndex === -1) {
    // 章节不存在，追加到文件末尾
    const newSection = `\n\n${sectionTitle}\n\n`;
    const newEntry = `### ${title} | ${new Date().toISOString().split('T')[0]}\n\n${content}\n`;
    fileContent += newSection + newEntry;
  } else {
    // 3. 找到下一章节的位置
    const nextSectionIndex = fileContent.indexOf('##', sectionIndex + 2);
    const insertPos = nextSectionIndex !== -1 ? nextSectionIndex : fileContent.length;
    
    // 4. 生成新条目
    const newEntry = `\n\n### ${title} | ${new Date().toISOString().split('T')[0]}\n\n${content}\n\n`;
    
    // 5. 插入到正确位置
    fileContent = fileContent.slice(0, insertPos) + newEntry + fileContent.slice(insertPos);
  }
  
  // 6. 写入文件
  fs.writeFileSync(filePath, fileContent, 'utf-8');
  
  console.log(`✅ Core memory updated: ${filePath}`);
  
  return {
    id: `core_${Date.now()}`,
    title,
    content,
    category,
    tags,
    timestamp: new Date().toISOString()
  };
}
```

**关键代码解释：**

```javascript
// 找到下一章节的位置
const nextSectionIndex = fileContent.indexOf('##', sectionIndex + 2);
```
- 从当前章节位置后面 2 个字符开始（跳过 `##`）
- 查找下一个 `##` 出现的位置
- 这就是下一章节的起始位置
- **为什么要 `+ 2`？** 因为要跳过当前章节自己的 `##`，否则会找到自己

```javascript
// 确定插入位置
const insertPos = nextSectionIndex !== -1 ? nextSectionIndex : fileContent.length;
```
- 如果找到了下一章节（`nextSectionIndex !== -1`）
- 插入位置就是下一章节的起始位置
- 如果没找到（`-1`），说明当前章节是最后一个
- 插入位置就是文件末尾

```javascript
// 插入新内容
fileContent = fileContent.slice(0, insertPos) + newEntry + fileContent.slice(insertPos);
```
- `fileContent.slice(0, insertPos)` - 插入位置**之前**的内容
- `newEntry` - 新的记忆条目
- `fileContent.slice(insertPos)` - 插入位置**之后**的内容
- 把它们拼接起来，新内容就插入到中间了

**图解：**
```
原文件：[章节 A 的内容][章节 B 的内容][章节 C 的内容]
                          ↑
                    insertPos = 章节 B 的起始位置

插入后：[章节 A 的内容][新记忆条目][章节 B 的内容][章节 C 的内容]
                              ↑
                        插在这里
```

**完整例子：**

假设 MEMORY.md 内容是：
```markdown
## 💬 重要对话记录
这是情感交流的内容

## 🦞 小钳的身份
这是身份定义

## 📚 重要经验总结
这是经验教训
```

现在要插入一个"情感交流"类别的记忆：

1. 找到当前章节位置：`sectionIndex = 0`（`## 💬 重要对话记录` 的位置）
2. 找到下一章节位置：`nextSectionIndex = 42`（`## 🦞 小钳的身份` 的位置）
3. 确定插入位置：`insertPos = 42`
4. 插入新内容：在位置 42 之前插入新记忆

结果：
```markdown
## 💬 重要对话记录
这是情感交流的内容

### Amber 的批评 | 2026-03-04  ← 新插入的内容

Amber 说要做严谨的调研...

## 🦞 小钳的身份
这是身份定义

## 📚 重要经验总结
这是经验教训
```

### 步骤 3：处理特殊情况

#### 情况 1：category 不在 SECTION_MAP 中

```javascript
const sectionTitle = SECTION_MAP[category] || '## 其他记录';
```

#### 情况 2：章节不存在

```javascript
if (sectionIndex === -1) {
  // 创建新章节
  const newSection = `\n\n${sectionTitle}\n\n`;
  const newEntry = `### ${title} | ${new Date().toISOString().split('T')[0]}\n\n${content}\n`;
  fileContent += newSection + newEntry;
}
```

#### 情况 3：文件不存在

```javascript
if (!fs.existsSync(filePath)) {
  fileContent = this.getMemoryTemplate();
}
```

---

## 📝 修改文件清单

| 文件 | 修改内容 | 代码量 |
|------|----------|--------|
| `scripts/memory-manager.js` | 定义 SECTION_MAP 常量 | +10 行 |
| `scripts/memory-manager.js` | 重写 updateCoreMemory 方法 | +80 行 |
| **总计** | | **+90 行** |

---

## ✅ 验收标准

- [ ] 能够根据 category 插入到对应章节
- [ ] 章节不存在时自动创建
- [ ] 文件不存在时使用模板创建
- [ ] 保持 MEMORY.md 结构完整
- [ ] 运行测试：`node scripts/memory-manager.js add "测试内容"` 无报错
- [ ] 检查 MEMORY.md 文件结构正确

---

## 🔗 相关文件

- 修改文件：`/root/openclaw/work/personify-memory/scripts/memory-manager.js`
- 目标文件：`/root/openclaw/work/personify-memory/../MEMORY.md`

---

*最后更新：2026-03-04*
