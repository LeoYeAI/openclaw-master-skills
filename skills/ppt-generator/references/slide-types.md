# 幻灯片页面类型

## 1. 封面页

用于演示开场。

**结构：**
- 超大主标题（font-black，居中）
- 副标语（font-light，灰色）
- 系列标识/Logo（可选）

**示例：**
```html
<div class="slide cover">
  <h1 class="text-5xl font-black text-white mb-6">重新定义效率</h1>
  <p class="text-xl font-light text-gray-400">AI时代的工作方式</p>
</div>
```

---

## 2. 标题冲击页

用于章节开始或重点强调。

**结构：**
- 单行/双行大标题
- 几乎无正文（最多一行辅助文字）

**示例：**
```html
<div class="slide impact">
  <h1 class="text-4xl font-black text-white text-center">
    不是更努力<br>而是更聪明
  </h1>
</div>
```

---

## 3. 金句强调页

用于引用、名言、核心观点。

**结构：**
- 大引号装饰
- 金句内容（font-bold）
- 来源/出处（font-light，灰色）

**示例：**
```html
<div class="slide quote">
  <span class="text-6xl text-gray-600">"</span>
  <p class="text-2xl font-bold text-white my-6">
    简单比复杂更难
  </p>
  <span class="text-lg font-light text-gray-500">— Steve Jobs</span>
</div>
```

---

## 4. 步骤说明页

用于流程、方法、操作指南。

**结构：**
- 动词型大标题
- 简洁说明（1-2行）
- 可选：步骤编号

**示例：**
```html
<div class="slide step">
  <span class="text-6xl font-black text-blue-500 mb-4">01</span>
  <h2 class="text-3xl font-bold text-white mb-4">明确目标</h2>
  <p class="text-lg font-light text-gray-400">
    先问自己：这件事最重要的结果是什么？
  </p>
</div>
```

---

## 5. 对比页

用于展示变化、差异、前后对比。

**结构：**
- 左右或上下分栏
- 对比元素使用不同颜色标识
- 简洁文字说明

**示例：**
```html
<div class="slide compare">
  <div class="text-center mb-8">
    <span class="text-red-400 line-through text-xl">传统方式</span>
  </div>
  <div class="text-center">
    <span class="text-green-400 text-3xl font-bold">全新体验</span>
  </div>
</div>
```

---

## 6. 数据展示页

用于关键数字、统计、成果。

**结构：**
- 超大数字（font-black）
- 单位/说明（font-light）
- 简短解释

**示例：**
```html
<div class="slide data">
  <span class="text-7xl font-black text-white">10x</span>
  <p class="text-xl font-light text-gray-400 mt-4">效率提升</p>
</div>
```

---

## 7. 列表页

用于多点说明，但必须保持极简。

**结构：**
- 标题
- 3-5 个要点（不能更多）
- 每个要点 ≤10 字

**示例：**
```html
<div class="slide list">
  <h2 class="text-2xl font-bold text-white mb-8">三个原则</h2>
  <ul class="space-y-6 text-xl">
    <li class="text-gray-300">• 少即是多</li>
    <li class="text-gray-300">• 专注核心</li>
    <li class="text-gray-300">• 持续迭代</li>
  </ul>
</div>
```

---

## 8. 结尾行动页

用于演示结束，呼吁行动。

**结构：**
- 总结金句
- 行动号召（CTA）
- 联系方式/二维码（可选）

**示例：**
```html
<div class="slide ending">
  <h1 class="text-3xl font-bold text-white mb-8">
    现在就开始改变
  </h1>
  <p class="text-xl font-light text-gray-400">
    扫码获取更多信息
  </p>
</div>
```

---

## 页面选择指南

| 内容类型 | 推荐页面类型 |
|---------|-------------|
| 演示开场 | 封面页 |
| 章节分隔 | 标题冲击页 |
| 核心观点 | 金句强调页 |
| 操作步骤 | 步骤说明页 |
| 前后对比 | 对比页 |
| 关键数据 | 数据展示页 |
| 多点说明 | 列表页（≤5点）|
| 演示结束 | 结尾行动页 |
