---
name: ppt-skill
version: 0.2.0
description: 触发关键词：演示、PPT、幻灯片、slides、presentation、keynote、deck、汇报、展示; 使用场景：用户需要生成演示文稿、汇报材料或教学幻灯片。
---

# Reveal.js PPT Skill

## Overview

触发关键词：演示、PPT、幻灯片、slides、presentation、keynote、deck、汇报、展示
使用场景：用户需要生成基于 Reveal.js 的 HTML 演示文稿，在浏览器中运行。

使用 Reveal.js 创建专业的 HTML 演示文稿，支持丰富的过渡效果、图表集成、演讲者备注等功能。

---

## 设计原则

**关键要求**：在创建任何演示文稿之前，必须先分析内容并选择合适的设计元素。

### 内容驱动设计

1. **分析主题**：这个演示文稿是关于什么的？它暗示了什么样的基调、行业或情绪？
2. **检查品牌**：如果用户提到公司/组织，考虑其品牌色彩和身份
3. **匹配配色**：选择反映主题的颜色
4. **声明方案**：在编写代码之前，解释你的设计选择

**必须遵守**：
- ✅ 在编写代码之前，声明你的内容驱动设计方案
- ✅ 使用网络安全字体或通过 \`@import\` 引入 Google Fonts
- ✅ 通过大小、粗细和颜色创建清晰的视觉层次
- ✅ 确保可读性：强对比度、适当的文字大小、整洁的对齐
- ✅ 保持一致性：在所有幻灯片中重复使用相同的模式、间距和视觉语言

### 配色方案选择

**创意选色原则**：
- **超越默认**：什么颜色真正匹配这个特定主题？避免自动驾驶式的选择
- **多角度考虑**：主题、行业、情绪、能量水平、目标受众、品牌身份
- **大胆尝试**：尝试意想不到的组合——医疗演示不一定要用绿色，金融不一定要用深蓝
- **构建调色板**：选择 3-5 种协调的颜色（主色 + 辅助色 + 强调色）
- **确保对比度**：文字必须在背景上清晰可读

**精选配色方案**（选择一个、调整它，或创建你自己的）：

| 编号 | 名称 | 颜色组合 |
|------|------|----------|
| 1 | **Classic Blue** | 深海军蓝 \`#1C2833\`、石板灰 \`#2E4053\`、银色 \`#AAB7B8\`、米白 \`#F4F6F6\` |
| 2 | **Teal & Coral** | 青色 \`#5EA8A7\`、深青 \`#277884\`、珊瑚 \`#FE4447\`、白色 \`#FFFFFF\` |
| 3 | **Bold Red** | 红 \`#C0392B\`、亮红 \`#E74C3C\`、橙 \`#F39C12\`、黄 \`#F1C40F\`、绿 \`#2ECC71\` |
| 4 | **Warm Blush** | 淡紫 \`#A49393\`、腮红 \`#EED6D3\`、玫瑰 \`#E8B4B8\`、奶油 \`#FAF7F2\` |
| 5 | **Burgundy Luxury** | 酒红 \`#5D1D2E\`、深红 \`#951233\`、铁锈 \`#C15937\`、金色 \`#997929\` |
| 6 | **Deep Purple & Emerald** | 紫色 \`#B165FB\`、深蓝 \`#181B24\`、翡翠 \`#40695B\`、白色 \`#FFFFFF\` |
| 7 | **Cream & Forest** | 奶油 \`#FFE1C7\`、森林绿 \`#40695B\`、白色 \`#FCFCFC\` |
| 8 | **Pink & Purple** | 粉红 \`#F8275B\`、珊瑚 \`#FF574A\`、玫瑰 \`#FF737D\`、紫色 \`#3D2F68\` |
| 9 | **Lime & Plum** | 青柠 \`#C5DE82\`、李子 \`#7C3A5F\`、珊瑚 \`#FD8C6E\`、蓝灰 \`#98ACB5\` |
| 10 | **Black & Gold** | 金色 \`#BF9A4A\`、黑色 \`#000000\`、奶油 \`#F4F6F6\` |
| 11 | **Sage & Terracotta** | 鼠尾草 \`#87A96B\`、赤陶 \`#E07A5F\`、奶油 \`#F4F1DE\`、炭灰 \`#2C2C2C\` |
| 12 | **Charcoal & Red** | 炭灰 \`#292929\`、红色 \`#E33737\`、浅灰 \`#CCCBCB\` |
| 13 | **Vibrant Orange** | 橙色 \`#F96D00\`、浅灰 \`#F2F2F2\`、炭灰 \`#222831\` |
| 14 | **Forest Green** | 黑色 \`#191A19\`、绿色 \`#4E9F3D\`、深绿 \`#1E5128\`、白色 \`#FFFFFF\` |
| 15 | **Retro Rainbow** | 紫 \`#722880\`、粉 \`#D72D51\`、橙 \`#EB5C18\`、琥珀 \`#F08800\`、金 \`#DEB600\` |
| 16 | **Vintage Earthy** | 芥末 \`#E3B448\`、鼠尾草 \`#CBD18F\`、森林绿 \`#3A6B35\`、奶油 \`#F4F1DE\` |
| 17 | **Coastal Rose** | 老玫瑰 \`#AD7670\`、海狸 \`#B49886\`、蛋壳 \`#F3ECDC\`、灰绿 \`#BFD5BE\` |
| 18 | **Orange & Turquoise** | 浅橙 \`#FC993E\`、灰青 \`#667C6F\`、白色 \`#FCFCFC\` |

### 幻灯片内容多样化

**多样化展示是关键**。即使幻灯片有相似的内容类型，也要变化视觉呈现：

- 在不同幻灯片使用**不同布局**：一页用分栏，另一页用堆叠盒子，第三页用带图标的标注
- 混合容器样式：纯文本、盒子、标注、引用块
- 使用**视觉层次**：\`<strong>\` 标记关键词，不同颜色区分类别
- 用其他元素（引用、标注、分栏）打破列表的单调
- 不要在连续幻灯片上重复相同的布局模式

**保持可扫描性**：
- 短要点，不是段落
- 每页尽可能只有一个主要观点
- 使用图标（Font Awesome）增加视觉趣味

**内容少时放大**：当幻灯片内容较少时，使用更大的字号填充空间，不要留下大片空白配小字。

### 视觉细节选项

**几何图案 (Geometric Patterns)**：
- 对角线分隔符代替水平线
- 不对称列宽（30/70、40/60、25/75）
- 90° 或 270° 旋转文字标题
- 圆形/六边形图片框架
- 角落三角形装饰
- 重叠形状增加深度

**边框与框架处理 (Border & Frame Treatments)**：
- 单侧粗边框（10-20pt）
- 双线边框配对比色
- 角括号代替完整边框
- L 形边框（上+左 或 下+右）
- 标题下划线强调（3-5pt 粗）

**排版处理 (Typography Treatments)**：
- 极端尺寸对比（72pt 标题 vs 11pt 正文）
- 全大写标题配宽字间距
- 超大编号显示
- 等宽字体用于数据/统计/技术内容
- 窄体字体用于密集信息
- 轮廓文字强调

**图表与数据样式 (Chart & Data Styling)**：
- 单色图表配单一强调色
- 水平条形图代替垂直
- 点图代替条形图
- 最少或无网格线
- 数据标签直接在元素上（无图例）
- 超大数字显示关键指标

**布局创新 (Layout Innovations)**：
- 全出血图片配文字叠加
- 侧边栏列（20-30% 宽度）用于导航/上下文
- 模块化网格系统（3×3、4×4 块）
- Z 形或 F 形内容流
- 浮动文字框覆盖彩色形状
- 杂志风格多栏布局

**背景处理 (Background Treatments)**：
- 纯色块占据 40-60% 幻灯片
- 渐变填充（仅垂直或对角线）
- 分割背景（两色，对角线或垂直）
- 边缘到边缘色带
- 负空间作为设计元素

### 布局技巧

**图表/表格布局规则**：
- ✅ **两栏布局（首选）**：标题横跨全宽，下方两栏 - 一栏文字/要点，另一栏特色内容。使用不等宽 flexbox（如 40%/60%）优化空间
- ✅ **全屏布局**：让特色内容（图表/表格）占据整个幻灯片以获得最大冲击力和可读性
- ❌ **禁止垂直堆叠**：不要将图表/表格放在文字下方的单列中 - 这会导致可读性差和布局问题

---

## 核心规范

### 技术选型

使用 Reveal.js 实现（功能强大、专业演示库、支持丰富的过渡效果和主题）

**优势**：
- 专为演示文稿设计，支持嵌套幻灯片（垂直/水平导航）
- 内置多种过渡动画和主题样式
- 支持 Markdown、代码高亮、演讲者备注
- 完善的键盘导航和触控支持
- 响应式设计，自动适配不同屏幕

**CDN 引入**：
\`\`\`html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reset.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/white.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
\`\`\`

### HTML 结构

\`\`\`html
<div class="reveal">
  <div class="slides">
    <section>
      <h1>第一页标题</h1>
      <p>第一页内容</p>
    </section>
    <section>
      <h2>第二页标题</h2>
      <ul>
        <li>要点一</li>
        <li>要点二</li>
      </ul>
    </section>
  </div>
</div>
\`\`\`

### 布局要求

- 每页视口：**100% 宽度 × 100% 高度**（必须铺满容器）
- 内容居中：Reveal.js 自动处理水平+垂直居中
- 字号：标题 48-72px，正文 24-32px
- 每页建议：1 个主标题 + 3-5 个要点
- 内容必须适应单页，不能溢出

**⭐ 关键布局样式（必须包含）**：
\`\`\`css
/* 确保 Reveal.js 铺满容器 */
.reveal {
  width: 100% !important;
  height: 100% !important;
}
.reveal .slides {
  width: 100% !important;
  height: 100% !important;
}
.reveal .slides section {
  width: 100% !important;
  height: 100% !important;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  box-sizing: border-box;
}
\`\`\`

### 交互配置

Reveal.js 初始化（必须包含）：
\`\`\`javascript
Reveal.initialize({
  hash: true,
  controls: true,
  progress: true,
  center: true,
  transition: "slide",
  keyboard: true,
  touch: true,
  mouseWheel: false,
  autoSlide: 0,
  // ⭐ 关键：使用 100% 确保铺满容器
  width: "100%",
  height: "100%",
  margin: 0,
  minScale: 1,
  maxScale: 1
});
\`\`\`

支持：键盘导航（← → ↑ ↓）、触摸滑动、全屏模式（F）、概览模式（ESC）

### 约束规范

**禁止**：
- 垂直滚动（每页内容必须适应视口）
- 复杂表单交互
- 需要滚动才能看到的内容
- 过多文字（每页控制在 50 字以内）

**注意**：
- 按逻辑段落分页，每页一个主题
- 确保引入 Reveal.js CDN 资源
- 在 DOMContentLoaded 后初始化 Reveal


---

## CSS 组件库

### CSS 变量定义

在 \`<style>\` 标签中定义以下 CSS 变量，便于统一管理主题：

\`\`\`css
:root {
  /* 背景色 */
  --background-color: #ffffff;
  --section-divider-bg: #f5f5f5;

  /* 主题色 */
  --primary-color: #2196F3;
  --secondary-color: #ff9800;
  --text-color: #222;
  --muted-color: #666;

  /* 组件色 */
  --box-bg: #f5f5f5;
  --box-border: #ddd;
  --box-radius: 8px;

  /* Callout 颜色 */
  --blue: #2196F3;
  --blue-bg: #e3f2fd;
  --orange: #ff9800;
  --orange-bg: #fff3e0;
  --green: #4caf50;
  --green-bg: #e8f5e9;
  --gray: #666;
  --gray-bg: #f5f5f5;
}
\`\`\`

### Boxes 盒子组件

\`\`\`css
/* 基础盒子 - 填充背景 */
.box {
  background: var(--box-bg);
  border: 1px solid var(--box-border);
  border-radius: var(--box-radius);
  padding: 20px;
  margin: 10px 0;
}

/* 轮廓盒子 - 仅边框 */
.box-outlined {
  border: 1px solid var(--box-border);
  border-radius: var(--box-radius);
  padding: 20px;
  margin: 10px 0;
  background: transparent;
}
\`\`\`

**使用示例**：
\`\`\`html
<div class="box">
  <p><strong>关键洞察</strong></p>
  <p>这是一个重要的信息盒子</p>
</div>
\`\`\`

### Callouts 标注组件

\`\`\`css
/* 基础标注 */
.callout {
  border-left: 6px solid var(--primary-color);
  padding: 15px 20px;
  margin: 15px 0;
  background: #f9f9f9;
  border-radius: var(--box-radius);
}

/* 颜色变体 */
.callout-blue { border-left-color: var(--blue); background: var(--blue-bg); }
.callout-orange { border-left-color: var(--orange); background: var(--orange-bg); }
.callout-green { border-left-color: var(--green); background: var(--green-bg); }
.callout-gray { border-left-color: var(--gray); background: var(--gray-bg); }

/* 顶部边框变体 */
.callout-top {
  border-left: none;
  border-top: 6px solid var(--primary-color);
}
\`\`\`

**使用示例**：
\`\`\`html
<div class="callout callout-blue">
  <p><strong>💡 提示</strong></p>
  <p>这是一个蓝色的提示标注</p>
</div>

<div class="callout callout-green">
  <p><strong>✅ 成功</strong></p>
  <p>操作已成功完成</p>
</div>
\`\`\`

### Blockquotes 引用块

\`\`\`css
.reveal blockquote {
  border-left: 4px solid var(--primary-color);
  padding-left: 20px;
  margin: 20px 0;
  font-style: italic;
  background: none;
  box-shadow: none;
  width: 100%;
}

.reveal blockquote cite {
  display: block;
  margin-top: 10px;
  font-style: normal;
  color: var(--muted-color);
}
\`\`\`

**使用示例**：
\`\`\`html
<blockquote>
  "设计不仅仅是外观和感觉，设计是它如何工作的。"
  <cite>— Steve Jobs</cite>
</blockquote>
\`\`\`

### 文字尺寸工具类

基础文字为 16pt，使用以下类在内容较少时放大：

\`\`\`css
.text-lg { font-size: 18pt !important; }   /* 稍大 */
.text-xl { font-size: 20pt !important; }   /* 中等强调 */
.text-2xl { font-size: 24pt !important; }  /* 强调 */
.text-3xl { font-size: 28pt !important; }  /* 很大 */
.text-4xl { font-size: 32pt !important; }  /* 最大正文 */

.text-muted { color: var(--muted-color) !important; }
.text-center { text-align: center !important; }
\`\`\`

### 多栏布局

**始终使用内联 CSS Grid**（不要创建工具类）：

\`\`\`html
<!-- 等宽两栏 -->
<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px;">
  <div>第一栏</div>
  <div>第二栏</div>
</div>

<!-- 三栏 -->
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px;">
  <div>第一栏</div>
  <div>第二栏</div>
  <div>第三栏</div>
</div>

<!-- 不等宽 -->
<div style="display: grid; grid-template-columns: 1fr 2fr; gap: 30px;">
  <div>窄侧边栏</div>
  <div>宽主内容</div>
</div>
\`\`\`


---

## 图表集成

使用 Chart.js 插件为幻灯片添加专业图表。

### 引入 Chart.js

在 CDN 资源部分添加：
\`\`\`html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>
\`\`\`

初始化时添加插件：
\`\`\`javascript
Reveal.initialize({
  // ... 其他配置
  plugins: [ RevealChart ],
  chart: {
    defaults: {
      color: "lightgray",
      borderColor: "lightgray"
    }
  }
});
\`\`\`

### 图表布局模式

**⚠️ 关键**：图表必须使用 flexbox 容器模式，否则会溢出！

#### 全屏图表

\`\`\`html
<section style="display: flex; flex-direction: column; height: 100%;">
  <h2>图表标题</h2>
  <div style="flex: 1; position: relative; min-height: 0;">
    <canvas data-chart="bar">
    <!--
    {
      "data": {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [{
          "label": "营收",
          "data": [45, 52, 61, 78],
          "backgroundColor": "#2196F3"
        }]
      },
      "options": {
        "maintainAspectRatio": false
      }
    }
    -->
    </canvas>
  </div>
</section>
\`\`\`

#### 左右分栏（图表 + 内容）

\`\`\`html
<section style="display: flex; flex-direction: column; height: 100%;">
  <h2>图表标题</h2>
  <div style="flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 30px; min-height: 0;">
    <div class="box" style="display: flex; flex-direction: column; justify-content: center;">
      <p><strong>关键洞察</strong></p>
      <ul>
        <li>第一个要点</li>
        <li>第二个要点</li>
        <li>第三个要点</li>
      </ul>
    </div>
    <div style="position: relative; min-height: 0; min-width: 0;">
      <canvas data-chart="pie">
      <!--
      {
        "data": {
          "labels": ["A", "B", "C"],
          "datasets": [{
            "data": [45, 35, 20],
            "backgroundColor": ["#2196F3", "#4caf50", "#ff9800"]
          }]
        },
        "options": {
          "maintainAspectRatio": false
        }
      }
      -->
      </canvas>
    </div>
  </div>
</section>
\`\`\`

#### 上下分栏（内容 + 图表）

\`\`\`html
<section style="display: flex; flex-direction: column; height: 100%;">
  <h2>图表标题</h2>
  <div style="flex: 1; display: grid; grid-template-rows: 1fr 2fr; gap: 20px; min-height: 0;">
    <div class="box" style="display: flex; align-items: center;">
      <p><strong>摘要：</strong>Q4 表现强劲，所有区域均超额完成目标。</p>
    </div>
    <div style="position: relative; min-height: 0; min-width: 0;">
      <canvas data-chart="line">
      <!--
      {
        "data": {
          "labels": ["1月", "2月", "3月", "4月", "5月", "6月"],
          "datasets": [{
            "label": "增长",
            "data": [100, 120, 135, 150, 180, 210],
            "borderColor": "#2196F3",
            "fill": false
          }]
        },
        "options": {
          "maintainAspectRatio": false
        }
      }
      -->
      </canvas>
    </div>
  </div>
</section>
\`\`\`

### 图表类型

支持的类型：\`bar\`、\`line\`、\`pie\`、\`doughnut\`、\`radar\`、\`polarArea\`、\`scatter\`

**常用场景**：
- **bar**：比较类别
- **line**：展示趋势
- **pie/doughnut**：展示占比
- **scatter**：展示变量关系

### 图表样式

\`\`\`json
"datasets": [{
  "data": [12, 19, 8, 15],
  "backgroundColor": ["#2196F3", "#ff9800", "#4caf50", "#e91e63"]
}]
\`\`\`

**常用配色数组**：
\`\`\`javascript
// 蓝色系
["#1565c0", "#1976d2", "#1e88e5", "#2196f3", "#42a5f5"]

// 暖色系
["#c62828", "#ef6c00", "#f9a825", "#2e7d32", "#1565c0"]

// 分类色（区分度高）
["#2196F3", "#ff9800", "#4caf50", "#e91e63", "#9c27b0"]
\`\`\`


---

## 高级特性

### Fragments 渐进式展示

点击逐步显示内容：

\`\`\`html
<p class="fragment">点击后出现</p>
<p class="fragment fade-up">向上滑入</p>
<p class="fragment highlight-red">变红高亮</p>
\`\`\`

**动画类型**：
- \`fade-in\`（默认）、\`fade-out\`
- \`fade-up\`、\`fade-down\`、\`fade-left\`、\`fade-right\`
- \`highlight-red\`、\`highlight-green\`、\`highlight-blue\`
- \`strike\`（删除线）

### 演讲者备注

按 \`S\` 键打开演讲者视图：

\`\`\`html
<section>
  <h2>幻灯片标题</h2>
  <p>可见内容</p>
  <aside class="notes">
    演讲者私人备注：
    - 记得提及 X
    - 过渡到下一个话题
  </aside>
</section>
\`\`\`

### 自定义背景

\`\`\`html
<!-- 纯色背景 -->
<section data-background-color="#283b95">

<!-- 图片背景 -->
<section data-background-image="image.jpg">
<section data-background-image="image.jpg" data-background-opacity="0.5">

<!-- 渐变背景 -->
<section data-background-gradient="linear-gradient(to bottom, #283b95, #17b2c3)">
\`\`\`

### Auto-Animate 自动动画

在幻灯片之间自动动画过渡，匹配 \`data-id\` 的元素会平滑过渡：

\`\`\`html
<section data-auto-animate>
  <h1>标题</h1>
</section>
<section data-auto-animate>
  <h1>标题</h1>
  <h2>副标题带动画出现</h2>
</section>
\`\`\`

### 代码高亮

\`\`\`html
<pre><code class="language-python">
def hello():
    print("Hello")
</code></pre>
\`\`\`

**行号高亮（点击逐步）**：
\`\`\`html
<pre><code data-line-numbers="1-2|3|4">
let a = 1;
let b = 2;
let c = x => 1 + 2 + x;
c(3);
</code></pre>
\`\`\`

### 过渡效果

\`\`\`html
<section data-transition="fade">
<section data-transition="slide">
<section data-transition="convex">
<section data-transition="zoom">
<section data-transition="none">
\`\`\`


---

## 最佳实践

### 专业设计规范

**字体选择**：
- 标题：使用无衬线字体（Inter、思源黑体、Noto Sans SC），字重 600-700
- 正文：字号不低于 24px 确保投影可读性，字重 400-500
- 数据/强调：可使用等宽字体（JetBrains Mono）突出关键数字

\`\`\`html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
\`\`\`

**视觉层次**：
- 建立清晰的信息层级：标题 > 副标题 > 正文 > 注释
- 运用留白管理呼吸空间，避免信息拥挤
- 通过字体大小、粗细、颜色差异引导视觉流线
- 重要信息使用色块、边框或图标辅助强调

**⭐ 信息结构增强**：
- **强烈推荐**：使用 **Infographic skill** 来生成专业信息图，代替纯文字列表
- **优势**：视觉冲击力强、信息传达高效、专业感更强

### 内容结构优化

**信息密度控制**：
- 每页不超过 7 个要点（符合认知负荷原则）
- 每个要点控制在 15 字以内
- 优先使用图表、图标替代纯文字
- 复杂数据拆分为多页递进展示

**标题层级规范**：
- H1：仅用于封面标题和章节分隔页
- H2：每页主标题，概括本页核心内容
- H3：小节标题，用于内容分组
- 避免超过 3 级标题层次

**逻辑递进结构**：
\`\`\`
封面页 → 目录/议程 → 背景/问题 → 分析/方案 → 数据/论证 → 结论/行动 → 致谢/Q&A
\`\`\`

### 快捷键速查

| 按键 | 功能 |
|------|------|
| ← → | 上一页/下一页 |
| F | 全屏模式 |
| S | 演讲者视图 |
| ESC | 概览/退出 |
| B / . | 黑屏暂停 |
| O | 幻灯片概览 |
| ? | 快捷键帮助 |


---

## 专业模板

### 重要说明

- 本场景运行在已有的 HTML 容器内，**不要输出** \`<!DOCTYPE>\`、\`<html>\`、\`<head>\`、\`<body>\` 等文档级标签
- **必须先输出完整的 DOM 结构**，再加载 Reveal.js 资源，确保用户可以实时看到元素上屏
- 样式可以通过 \`<style>\` 标签内联，脚本通过 \`<script>\` 标签引入

### 标准输出顺序

\`\`\`
1. Tailwind CSS CDN
2. 内联样式 (<style>) - 包含 CSS 变量和组件类
3. Reveal.js 容器结构 (<div class="reveal">)
4. 所有幻灯片内容 (<section>)
5. 自定义导航按钮
6. CDN 资源引入 (<link> 和 <script>)
7. 初始化脚本
\`\`\`

### 完整模板

\`\`\`html
<!-- 1. Tailwind CSS CDN -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- 2. 内联样式 -->
<style>
  @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap");
  
  /* CSS 变量 */
  :root {
    --primary-color: #2196F3;
    --secondary-color: #ff9800;
    --text-color: #222;
    --muted-color: #666;
    --box-bg: #f5f5f5;
    --box-border: #ddd;
    --box-radius: 8px;
    --blue: #2196F3;
    --blue-bg: #e3f2fd;
    --orange: #ff9800;
    --orange-bg: #fff3e0;
    --green: #4caf50;
    --green-bg: #e8f5e9;
  }
  
  /* 关键：确保铺满容器 */
  .reveal {
    font-family: "Noto Sans SC", "Inter", sans-serif;
    width: 100% !important;
    height: 100% !important;
  }
  .reveal .slides {
    width: 100% !important;
    height: 100% !important;
  }
  .reveal .slides > section {
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 60px;
    box-sizing: border-box;
  }
  
  /* 组件类 */
  .box {
    background: var(--box-bg);
    border: 1px solid var(--box-border);
    border-radius: var(--box-radius);
    padding: 20px;
    margin: 10px 0;
  }
  
  .callout {
    border-left: 6px solid var(--primary-color);
    padding: 15px 20px;
    margin: 15px 0;
    background: #f9f9f9;
    border-radius: var(--box-radius);
  }
  .callout-blue { border-left-color: var(--blue); background: var(--blue-bg); }
  .callout-orange { border-left-color: var(--orange); background: var(--orange-bg); }
  .callout-green { border-left-color: var(--green); background: var(--green-bg); }
  
  /* 文字尺寸 */
  .text-lg { font-size: 18pt !important; }
  .text-xl { font-size: 20pt !important; }
  .text-2xl { font-size: 24pt !important; }
  
  .reveal .slide-number { @apply text-sm text-gray-500 bg-transparent px-4 py-2; }
  .reveal .progress { @apply h-1; }
  .reveal .controls { @apply hidden; }
</style>

<!-- 3-4. Reveal.js 容器结构与内容 -->
<div class="reveal">
  <div class="slides">
    <!-- 封面页 -->
    <section>
      <h1 class="text-5xl font-bold mb-4">演示标题</h1>
      <p class="text-xl text-gray-600">副标题 | 日期</p>
    </section>
    
    <!-- 目录页 -->
    <section>
      <h2 class="text-4xl font-bold mb-8">议程</h2>
      <ol class="text-xl space-y-4">
        <li>背景介绍</li>
        <li>核心方案</li>
        <li>数据支撑</li>
        <li>下一步计划</li>
      </ol>
    </section>
    
    <!-- 内容页示例 -->
    <section>
      <h2 class="text-4xl font-bold mb-8">内容标题</h2>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px;">
        <div class="callout callout-blue">
          <p><strong>💡 关键洞察</strong></p>
          <p>这是一个重要的信息</p>
        </div>
        <div class="callout callout-green">
          <p><strong>✅ 成功指标</strong></p>
          <p>达成率 127%</p>
        </div>
      </div>
      <aside class="notes">演讲者备注内容</aside>
    </section>
    
    <!-- 数据展示页 -->
    <section>
      <h2 class="text-4xl font-bold mb-8">业绩增长概览</h2>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px;">
        <div class="text-center p-6 bg-blue-50 rounded-2xl">
          <span class="text-6xl font-bold text-blue-600">+127%</span>
          <span class="block mt-4 text-xl text-gray-600">营收增长</span>
        </div>
        <div class="text-center p-6 bg-green-50 rounded-2xl">
          <span class="text-6xl font-bold text-green-600">3.2M</span>
          <span class="block mt-4 text-xl text-gray-600">活跃用户</span>
        </div>
      </div>
    </section>
  </div>
</div>

<!-- 5. 自定义导航按钮 -->
<div class="fixed bottom-2 left-1/2 -translate-x-1/2 flex gap-2 z-50 bg-white/70 backdrop-blur-xl px-3 py-2 rounded-2xl shadow-lg border border-white/60">
  <button id="nav-prev" title="上一页" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-black/5 hover:scale-105 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-300 text-base">←</button>
  <div class="w-px h-4 bg-black/10 self-center"></div>
  <button id="nav-overview" title="概览 (ESC)" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-black/5 hover:scale-105 active:scale-95 transition-all duration-300 text-base">⊞</button>
  <div class="w-px h-4 bg-black/10 self-center"></div>
  <button id="nav-next" title="下一页" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-black/5 hover:scale-105 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-300 text-base">→</button>
</div>

<!-- 6. CDN 资源引入 -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reset.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/white.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
<!-- Chart.js 插件（可选） -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>

<!-- 7. 初始化脚本 -->
<script>
(function() {
  function initReveal() {
    if (typeof Reveal === "undefined") {
      setTimeout(initReveal, 50);
      return;
    }
    
    Reveal.initialize({
      hash: true,
      controls: false,
      progress: true,
      slideNumber: "c/t",
      transition: "fade",
      width: "100%",
      height: "100%",
      margin: 0,
      minScale: 1,
      maxScale: 1,
      plugins: typeof RevealChart !== "undefined" ? [RevealChart] : [],
      chart: {
        defaults: {
          color: "lightgray",
          borderColor: "lightgray"
        }
      }
    });
    
    // 自定义导航按钮事件
    var navPrev = document.getElementById("nav-prev");
    var navNext = document.getElementById("nav-next");
    var navOverview = document.getElementById("nav-overview");
    
    if (navPrev) navPrev.addEventListener("click", function() { Reveal.prev(); });
    if (navNext) navNext.addEventListener("click", function() { Reveal.next(); });
    if (navOverview) navOverview.addEventListener("click", function() { Reveal.toggleOverview(); });
    
    function updateNavButtons() {
      var indices = Reveal.getIndices();
      var totalSlides = Reveal.getTotalSlides();
      
      if (navPrev) navPrev.disabled = indices.h === 0;
      if (navNext) navNext.disabled = indices.h === totalSlides - 1;
    }
    
    Reveal.on("slidechanged", updateNavButtons);
    Reveal.on("ready", updateNavButtons);
  }
  
  initReveal();
})();
</script>
\`\`\`

### 关键要点

1. ✅ **先输出 DOM**：用户可以立即看到幻灯片结构和内容
2. ✅ **后加载资源**：CDN 资源放在 DOM 之后，避免阻塞渲染
3. ✅ **延迟初始化**：使用轮询检查 Reveal.js 是否加载完成
4. ✅ **容器适配**：移除所有文档级标签，直接输出可嵌入的片段
5. ✅ **流式友好**：按顺序输出，支持逐步渲染
6. ✅ **组件复用**：CSS 变量和组件类便于统一管理主题

---

## 参考文档

详细的图表配置和高级特性，请参阅：
- [图表详细文档](revealjs/references/charts.md)
- [高级特性文档](revealjs/references/advanced-features.md)
- [CSS 变量参考](revealjs/references/base-styles.css)

## 脚本工具

可用的辅助脚本（位于 \`revealjs/scripts/\` 目录）：
- \`create-presentation.js\`：生成演示文稿脚手架
- \`check-overflow.js\`：检查内容溢出
- \`check-charts.js\`：检查图表配置
