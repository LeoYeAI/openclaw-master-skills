# Work Report Layout Templates

Common layout patterns for work report presentations.

## Page Types

### 1. Cover Page (封面页)

```
┌────────────────────────────────────────┐
│                                        │
│                                        │
│           [主标题]                     │
│        2024年度工作汇报                │
│                                        │
│           [副标题]                     │
│        汇报人：张三                    │
│                                        │
│                                        │
│    [可选：底部装饰条或Logo]            │
└────────────────────────────────────────┘
```

**HTML Structure:**
```html
<div class="slide cover">
  <div class="cover-content">
    <h1 class="title">{{主标题}}</h1>
    <p class="subtitle">{{副标题}}</p>
  </div>
  <div class="cover-footer">
    <!-- Logo or decoration -->
  </div>
</div>
```

---

### 2. Table of Contents (目录页)

```
┌────────────────────────────────────────┐
│  目录                                  │
│  ──────────────────────────────        │
│                                        │
│    01   项目进展                       │
│                                        │
│    02   重点工作成果                   │
│                                        │
│    03   问题与挑战                     │
│                                        │
│    04   下阶段计划                     │
│                                        │
└────────────────────────────────────────┘
```

**HTML Structure:**
```html
<div class="slide toc">
  <h2 class="section-title">目录</h2>
  <div class="divider"></div>
  <ul class="toc-list">
    <li><span class="num">01</span> 项目进展</li>
    <li><span class="num">02</span> 重点工作成果</li>
    <li><span class="num">03</span> 问题与挑战</li>
    <li><span class="num">04</span> 下阶段计划</li>
  </ul>
</div>
```

---

### 3. Section Divider (章节页)

```
┌────────────────────────────────────────┐
│                                        │
│                                        │
│    ┌─────────────────────────────┐     │
│    │  PART 01                    │     │
│    │                             │     │
│    │  项目进展                   │     │
│    │                             │     │
│    └─────────────────────────────┘     │
│                                        │
│                                        │
└────────────────────────────────────────┘
```

---

### 4. Title + Bullets (标题+要点)

**Most common layout for content slides.**

```
┌────────────────────────────────────────┐
│  项目进展                              │
│  ──────────────────────────────        │
│                                        │
│  • 完成了核心功能开发，用户增长30%     │
│                                        │
│  • 优化了系统性能，响应时间降低50%     │
│                                        │
│  • 新增移动端适配，覆盖率达95%         │
│                                        │
└────────────────────────────────────────┘
```

**HTML Structure:**
```html
<div class="slide content">
  <h2 class="section-title">{{标题}}</h2>
  <div class="divider"></div>
  <ul class="bullet-list">
    <li>{{要点1}}</li>
    <li>{{要点2}}</li>
    <li>{{要点3}}</li>
  </ul>
</div>
```

---

### 5. Left Text + Right Image (左文右图)

**Best for: Data charts, screenshots, diagrams.**

```
┌────────────────────────────────────────┐
│  数据亮点                              │
│  ──────────────────────────────        │
│ ┌──────────────┐ ┌──────────────────┐  │
│ │              │ │                  │  │
│ │  文字内容    │ │     图表/图片    │  │
│ │              │ │                  │  │
│ │  • 要点1     │ │                  │  │
│ │  • 要点2     │ │                  │  │
│ │              │ │                  │  │
│ └──────────────┘ └──────────────────┘  │
└────────────────────────────────────────┘
```

**HTML Structure:**
```html
<div class="slide two-column">
  <h2 class="section-title">{{标题}}</h2>
  <div class="divider"></div>
  <div class="columns">
    <div class="column left">
      <p>{{文字内容}}</p>
      <ul>
        <li>{{要点}}</li>
      </ul>
    </div>
    <div class="column right">
      <img src="{{图片路径}}" alt="{{描述}}">
    </div>
  </div>
</div>
```

---

### 6. Top Text + Bottom Image (上文下图)

**Best for: Wide images, panoramic views.**

```
┌────────────────────────────────────────┐
│  团队建设                              │
│  ──────────────────────────────        │
│                                        │
│  本季度组织了3次团队活动，              │
│  增强了团队凝聚力。                    │
│                                        │
│ ┌────────────────────────────────────┐ │
│ │                                    │ │
│ │           活动照片                 │ │
│ │                                    │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

---

### 7. Two Column Comparison (对比布局)

**Best for: Before/After, Pros/Cons, Comparison.**

```
┌────────────────────────────────────────┐
│  优化对比                              │
│  ──────────────────────────────        │
│ ┌──────────────┐ ┌──────────────────┐  │
│ │   优化前     │ │     优化后       │  │
│ │   ──────     │ │     ──────       │  │
│ │              │ │                  │  │
│ │  响应时间    │ │  响应时间        │  │
│ │   2.5秒      │ │   1.2秒 ⬇52%    │  │
│ │              │ │                  │  │
│ └──────────────┘ └──────────────────┘  │
└────────────────────────────────────────┘
```

---

### 8. Grid Layout (网格布局)

**Best for: Multiple items, features, team members.**

```
┌────────────────────────────────────────┐
│  核心功能                              │
│  ──────────────────────────────        │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│ │  功能A  │ │  功能B  │ │  功能C  │   │
│ │         │ │         │ │         │   │
│ │  描述   │ │  描述   │ │  描述   │   │
│ └─────────┘ └─────────┘ └─────────┘   │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│ │  功能D  │ │  功能E  │ │  功能F  │   │
│ │         │ │         │ │         │   │
│ │  描述   │ │  描述   │ │  描述   │   │
│ └─────────┘ └─────────┘ └─────────┘   │
└────────────────────────────────────────┘
```

---

### 9. Full Image Background (全图背景)

**Best for: Impact statements, quotes, vision.**

```
┌────────────────────────────────────────┐
│ [背景图片]                             │
│                                        │
│                                        │
│         "我们的愿景是..."              │
│                                        │
│            — 张三                      │
│                                        │
│                                        │
└────────────────────────────────────────┘
```

---

### 10. Data Highlight (数据展示)

**Best for: Key metrics, KPIs.**

```
┌────────────────────────────────────────┐
│  关键数据                              │
│  ──────────────────────────────        │
│                                        │
│ ┌────────┐ ┌────────┐ ┌────────┐      │
│ │  30%   │ │  1.2M  │ │  95%   │      │
│ │  增长  │ │  用户  │ │  满意度│      │
│ └────────┘ └────────┘ └────────┘      │
│                                        │
│ ┌────────┐ ┌────────┐ ┌────────┐      │
│ │  2.5s  │ │  100+  │ │  24/7  │      │
│ │  响应  │ │  功能  │ │  支持  │      │
│ └────────┘ └────────┘ └────────┘      │
└────────────────────────────────────────┘
```

---

## Layout Selection Guide

| Content Type | Recommended Layout |
|--------------|-------------------|
| Introduction/Overview | Title + Bullets |
| Data/Chart | Left Text + Right Image |
| Comparison | Two Column |
| Multiple Items (3-6) | Grid 2x3 or 3x2 |
| Key Metrics | Data Highlight |
| Team/Features | Grid with icons |
| Impact Statement | Full Image Background |

---

## CSS Grid Templates

### Two Column (60/40)
```css
.columns {
  display: grid;
  grid-template-columns: 60% 40%;
  gap: 40px;
}
```

### Three Column (Equal)
```css
.columns-three {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 30px;
}
```

### Grid 2x3
```css
.grid-2x3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 20px;
}
```