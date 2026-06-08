---
name: report-ppt-generator-pro
description: "Generate professional PowerPoint presentations from text manuscripts and style examples. Use when users want to create PPT slides from written content, especially for work reports. Triggers: generate PPT, create slides, make presentation, convert to PowerPoint, PPT from document. Supports style extraction from example images, AI-generated illustrations, image embedding, and interactive HTML preview before export."
descriptionZh: "提供你的文稿及想要的风格示例图，会自动总结内容及风格，先通过 HTML 生成 PPT 预览，定稿后自动导出类似风格的.pptx 文件。"
---

# PPT Generator

## ⚠️ 依赖和权限声明

### 必需依赖

| 依赖 | 用途 | 配置要求 |
|------|------|----------|
| **nanobanana-skill** | AI 配图生成（可选功能） | 需要安装此 skill |
| **支持图片识别的 LLM** | 风格分析、大纲生成 | 用户自行配置任意支持图片识别的模型 |

### 文件系统访问

| 权限 | 用途 | 说明 |
|------|------|------|
| **读取本地文件** | 读取用户提供的风格示例图、文稿文件 | 仅读取用户明确指定的文件 |
| **写入本地文件** | 保存生成的 HTML 预览、PPTX 文件、AI 配图 | 默认保存到 `~/clawd/output/` 目录 |
| **读取 skill 目录** | 读取 assets/ 和 references/ 中的模板文件 | 仅限本 skill 目录内 |

### 外部 API 调用

| API | 用途 | 凭证要求 |
|-----|------|----------|
| **Google Gemini API** | AI 配图生成（通过 nanobanana-skill） | 需要在 nanobanana-skill 中配置 `GEMINI_API_KEY` |
| **LLM API** | 风格分析、内容生成 | 用户自行配置（支持图片识别的任意模型） |

### 可选功能

| 功能 | 依赖 | 是否必需 |
|------|------|----------|
| AI 配图生成 | nanobanana-skill + Gemini API Key | ❌ 可选 |
| 风格分析 | 支持图片识别的 LLM | ✅ 必需 |
| HTML 预览 | Canvas 工具或本地服务器 | ✅ 必需 |
| PPTX 导出 | pptxgenjs (内置) | ✅ 必需 |

---

Generate professional, editable PowerPoint presentations from text manuscripts with style matching.

## Workflow

```
用户输入（文稿 + 风格示例图 + 可选图片）
              │
              ▼
    ┌─────────────────┐
    │  Step 1: 风格分析 │
    │  支持图片识别的  │
    │  LLM 模型        │
    │  提取配色/布局   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  用户确认/调整   │  ← 对话迭代
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Step 2: 大纲生成 │
    │  总结文稿内容    │
    │  规划每页结构    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  是否需要AI配图？│  ← 可选项
    │  (Step 2.5)     │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
   是                否
    │                 │
    ▼                 │
┌─────────────┐       │
│ AI配图生成  │       │
│ nanobanana  │       │
└──────┬──────┘       │
       │              │
       └──────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │  Step 3: HTML生成 │
    │  16:9 横屏页面   │
    │  应用风格        │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Canvas 预览     │  ← 左右翻页、对话修改
    │  用户确认        │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Step 4: 导出PPTX │
    │  pptxgenjs      │
    │  可编辑文件      │
    └─────────────────┘
```

## Step 1: 风格分析

### 输入
- 风格示例图：用户提供的一张或多张 PPT 截图
- 可选：用户的风格偏好说明

### 执行

使用 `sessions_spawn` 调用**支持图片识别的 LLM 模型**分析风格（使用用户配置的默认模型）：

```javascript
sessions_spawn({
  model: "default",  // 使用用户配置的默认模型
  task: `分析这张 PPT 截图的视觉风格，提取以下信息：

1. 配色方案：
   - 主色（用于标题/重点）
   - 辅助色（用于副标题/装饰）
   - 背景色
   - 文字色

2. 布局结构：
   - 标题位置和样式
   - 内容区域划分
   - 留白比例

3. 字体风格：
   - 标题字体（粗细/大小层次）
   - 正文字体

4. 装饰元素：
   - 线条/形状
   - 图标/图形
   - 其他装饰

请以 JSON 格式输出风格描述。`,
  // 图片通过会话上下文传入
})
```

### 输出格式

```json
{
  "colors": {
    "primary": "#1E3A8A",
    "secondary": "#3B82F6",
    "background": "#FFFFFF",
    "text": "#1F2937",
    "accent": "#60A5FA"
  },
  "layout": {
    "titlePosition": "top-left",
    "titleSize": "large",
    "contentArea": "center",
    "whitespaceRatio": 0.3
  },
  "typography": {
    "titleFont": "bold, 36-48px",
    "bodyFont": "regular, 18-24px",
    "hierarchy": "clear distinction between title and body"
  },
  "decorations": {
    "shapes": ["rounded rectangles", "lines"],
    "icons": "minimal, line-style",
    "other": "subtle shadows"
  }
}
```

### 用户确认

展示分析结果，询问用户：
```
我分析了您提供的风格示例，提取出以下风格：
- 主色调：#1E3A8A（深蓝）
- 背景：白色
- ...

是否符合预期？需要调整哪些方面？
```

用户可以：
- 确认使用
- 修改颜色值
- 调整布局偏好
- 提供新的风格描述

---

## Step 2: 大纲生成

### 输入
- 文稿内容（文本）
- 可选图片列表（本地路径或 URL）
- 已确认的风格

### 执行

分析文稿结构，生成 PPT 大纲：

```
1. 封面页
   - 标题：{主标题}
   - 副标题：{副标题}
   - 图片：{可选封面图}

2. 目录页
   - 章节：{章节列表}

3. 章节页 x N
   - 标题：{章节标题}
   - 内容：{要点列表，每项 1-2 行}
   - 图片：{配图路径，注明位置意图}
   - 布局建议：{左文右图/上文下图/全图等}

4. 总结页
   - 关键结论
   - 下一步行动

5. 结束页
   - 感谢语
   - 联系方式
```

### 图片处理

如果用户提供了图片：

1. **识别图片意图**：根据上下文判断图片应该放在哪页
2. **规划图片位置**：
   - 数据图表 → 右侧或中央
   - 配图/照片 → 背景或侧边
   - 图标 → 标题旁或要点前
3. **记录图片路径**：本地路径或 URL

### 用户确认

展示大纲，询问：
```
我根据您的文稿生成了 PPT 大纲：

第1页：封面 - "季度工作汇报"
第2页：目录 - 3个章节
第3页：项目进展 - 左文右图布局
...

共 N 页。确认后我开始生成 HTML 预览。
需要调整页面顺序、合并/拆分页面吗？
```

---

## Step 2.5: AI 配图生成（可选）

### 询问用户

大纲确认后，询问用户是否需要 AI 生成配图：

```
您的 PPT 大纲已生成。是否需要我为您生成 AI 配图？

选择：
1. 全部页面生成配图
2. 仅部分页面生成配图（请告诉我哪些页）
3. 不需要配图，继续下一步
```

### 配图策略

根据页面类型生成不同风格的配图：

| 页面类型 | 配图风格 | 示例提示词 |
|----------|----------|-----------|
| 封面页 | 抽象科技/城市/行业背景 | "抽象科技背景，蓝色渐变，现代化数字城市，简洁几何图形" |
| 概述页 | 概念插图/流程图风格 | "业务流程概念图，简洁扁平风格，蓝色主色调" |
| 数据页 | 数据可视化风格 | "数据分析概念插图，图表和仪表盘，科技感" |
| 总结页 | 积极向上的概念图 | "成功合作概念图，握手或团队，商务风格" |

### 执行流程

#### 1. 分析页面内容，生成提示词

```javascript
// 对每个需要配图的页面
const imagePrompt = await generateImagePrompt(slideContent, styleColors);

// 示例输出
{
  "slide": 3,
  "type": "概念插图",
  "prompt": "数字化道路概念图，智慧交通，蓝色科技风格，简洁扁平化设计，现代城市道路俯视图，带有数据流线条，16:9横幅"
}
```

#### 2. 调用 nanobanana 生成图片

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/nanobanana-skill/nanobanana.py \
  --prompt "数字化道路概念图，智慧交通，蓝色科技风格，简洁扁平化设计" \
  --size 1344x768 \
  --output "/path/to/output/slide-3-illustration.png"
```

#### 3. 图片参数设置

```javascript
const imageConfig = {
  // 横版配图（适合 PPT）
  size: "1344x768",  // 16:9 横幅
  
  // 方形配图（适合图标、小插图）
  sizeSquare: "1024x1024",
  
  // 默认模型
  model: "gemini-3-pro-image-preview",
  
  // 快速模型（可选）
  modelFast: "gemini-2.5-flash-image",
  
  // 分辨率
  resolution: "1K"
};
```

### 配图提示词模板

#### 封面配图

```
{主题}概念背景图，{风格描述}，{主色调}渐变，
现代化{行业}场景，简洁几何图形装饰，
专业商务风格，适合PPT封面，16:9横幅
```

#### 内容页配图

```
{页面主题}概念插图，{具体描述}，
扁平化设计风格，{主色调}主色调，
简洁专业，适合PPT内容页，16:9横幅
```

#### 数据/图表配图

```
数据分析可视化概念图，{具体描述}，
科技感设计，{主色调}配色，
简洁现代，适合PPT数据展示页，16:9横幅
```

### 配图风格指南

根据提取的风格调整配图：

```javascript
function adaptPromptToStyle(basePrompt, extractedStyle) {
  const colorWords = {
    "#003366": "深蓝色",
    "#3366CC": "蓝色",
    "#1E3A8A": "海军蓝",
    "#22C55E": "绿色",
    "#F97316": "橙色"
  };
  
  const primaryColorWord = colorWords[extractedStyle.colors.primary] || "蓝色";
  
  return `${basePrompt}，${primaryColorWord}主色调，与PPT风格协调`;
}
```

### 生成后的处理

1. **保存图片**到工作目录
2. **更新大纲**中的图片路径
3. **展示预览**给用户确认
4. **可选调整**：用户可以说"重新生成第3页配图"

---

## Step 3: HTML 生成

### 16:9 页面规格

```css
.slide {
  width: 1920px;
  height: 1080px;
  aspect-ratio: 16 / 9;
  /* 或响应式： */
  width: 100%;
  aspect-ratio: 16 / 9;
}
```

### 模板参考

使用 `assets/html-template/` 中的模板：

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="base.css">
  <style>
    /* 注入用户风格 */
    :root {
      --primary-color: {{colors.primary}};
      --secondary-color: {{colors.secondary}};
      --background-color: {{colors.background}};
      --text-color: {{colors.text}};
    }
  </style>
</head>
<body>
  <div class="slide" id="slide-1">
    <!-- 内容 -->
  </div>
</body>
</html>
```

### 布局类型

参考 `references/work-report-layouts.md` 中的布局模板：
- 封面布局
- 标题+正文布局
- 左文右图布局
- 对比布局
- 数据展示布局

### 图片嵌入

```html
<!-- AI生成的配图 -->
<img src="/path/to/ai-generated-illustration.png" alt="配图描述">

<!-- 用户提供的图片 -->
<img src="/local/path/to/image.png" alt="描述">

<!-- 网络图片 -->
<img src="https://example.com/image.png" alt="描述">

<!-- 样式：自动缩放适配 -->
<style>
.slide img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
</style>
```

---

## Step 4: Canvas 预览

### 展示方式

使用 `canvas` 工具或本地服务器展示 HTML：

```javascript
// 方式1: canvas（需要 node）
canvas({
  action: "present",
  url: "file:///path/to/slides.html"
})

// 方式2: 本地服务器
// 启动服务器后用浏览器预览
```

### 交互功能

用户可以：
- **翻页**：点击左右箭头或按钮
- **对话修改**：说"把标题改成蓝色"、"调整第3页布局"
- **预览截图**：查看渲染效果

### 迭代修改

接收用户修改指令，更新 HTML，刷新预览。

---

## Step 5: 导出 PPTX

### 使用 pptxgenjs

```javascript
import pptxgen from "pptxgenjs";

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";

// 应用风格
pres.theme = {
  headFontFace: "Microsoft YaHei",
  bodyFontFace: "Microsoft YaHei"
};

// 添加幻灯片
let slide = pres.addSlide();

// 添加文本
slide.addText("标题", {
  x: 0.5, y: 0.5, w: "90%", h: 1,
  fontSize: 36, color: "1E3A8A", bold: true
});

// 添加 AI 生成的配图
slide.addImage({
  path: "/path/to/ai-generated-illustration.png",
  x: 6, y: 2, w: 4, h: 3
});

// 保存
pres.writeFile({ fileName: "output.pptx" });
```

### 风格映射

| HTML/CSS | pptxgenjs |
|----------|-----------|
| `color: #1E3A8A` | `color: "1E3A8A"` |
| `font-size: 36px` | `fontSize: 36` |
| `font-weight: bold` | `bold: true` |
| `background: #FFF` | `fill: "FFFFFF"` |

### 图片处理

```javascript
// 本地图片（包括 AI 生成的配图）
slide.addImage({ path: "/path/to/image.png", ... });

// 网络图片（先下载）
const imageData = await fetch(imageUrl);
slide.addImage({ data: imageData, ... });

// 自动缩放
// pptxgenjs 会自动处理，可指定 w/h 或使用 sizing
```

---

## HTML 转 PPTX 经验教训

### ⚠️ 常见陷阱

#### 1. 正则匹配嵌套 HTML 标签

**问题**：使用简单正则 `/class="slide"/` 会误匹配 `class="slide-content"`、`class="slide-header"` 等。

**错误示例**：
```javascript
// ❌ 错误：会匹配到 slide-content, slide-header 等
const regex = /<div class="slide[^"]*"/g;
```

**正确做法**：使用栈匹配嵌套结构
```javascript
// ✅ 正确：精确匹配顶层 slide div
function extractSlides(html) {
  const slides = [];
  // 精确匹配 slide 的开始标签，捕获类型
  const regex = /<div class="slide( cover| end)?"[^>]*>/g;
  let match;
  
  while ((match = regex.exec(html)) !== null) {
    const startPos = match.index;
    const slideType = match[1] ? match[1].trim() : 'content';
    
    // 用栈找到匹配的结束 </div>
    let depth = 1;
    let pos = startPos + match[0].length;
    
    while (depth > 0 && pos < html.length) {
      const openIdx = html.indexOf('<div', pos);
      const closeIdx = html.indexOf('</div>', pos);
      
      if (closeIdx === -1) break;
      
      if (openIdx !== -1 && openIdx < closeIdx) {
        depth++;
        pos = openIdx + 4;
      } else {
        depth--;
        pos = closeIdx + 6;
      }
    }
    
    slides.push({
      html: html.substring(startPos, pos),
      type: slideType
    });
  }
  
  return slides;
}
```

#### 2. 提取嵌套 div 内容

**问题**：`text-section` 内部还有嵌套 div，简单正则无法正确提取。

**正确做法**：
```javascript
function extractTextSection(slideHtml) {
  const startMatch = slideHtml.match(/class="text-section"[^>]*>/);
  if (!startMatch) return null;
  
  const startPos = startMatch.index + startMatch[0].length;
  
  // 用栈找结束位置
  let depth = 1;
  let pos = startPos;
  
  while (depth > 0 && pos < slideHtml.length) {
    const openIdx = slideHtml.indexOf('<div', pos);
    const closeIdx = slideHtml.indexOf('</div>', pos);
    
    if (closeIdx === -1) break;
    
    if (openIdx !== -1 && openIdx < closeIdx) {
      depth++;
      pos = openIdx + 4;
    } else {
      depth--;
      pos = closeIdx + 6;
      if (depth === 0) {
        return slideHtml.substring(startPos, closeIdx);
      }
    }
  }
  return null;
}
```

#### 3. 背景图处理

**问题**：HTML 中的背景图（如 `cover_bg.png`）可能被误过滤，或路径处理不正确。

**正确做法**：
```javascript
// 封面页：先添加背景图，再添加半透明遮罩
function createCoverSlide(slide, slideHtml) {
  // 1. 背景图
  const bgPath = `${imgBasePath}/cover_bg.png`;
  if (fs.existsSync(bgPath)) {
    slide.addImage({ path: bgPath, x: 0, y: 0, w: 10, h: 5.625 });
  }
  
  // 2. 半透明遮罩（让文字更清晰）
  slide.addShape('rect', {
    x: 0, y: 0, w: 10, h: 5.625,
    fill: { color: '0d47a1', transparency: 20 }
  });
  
  // 3. 文字内容...
}
```

#### 4. 图片路径验证

**问题**：HTML 中的图片路径可能不存在，直接添加会报错。

**正确做法**：
```javascript
// 过滤有效图片
const validImages = images.filter(p => fs.existsSync(p));

if (validImages.length > 0) {
  // 添加图片...
} else {
  // 显示占位符
  slide.addShape('rect', {
    x: imgX, y: imgY, w: imgW, h: imgH,
    fill: { color: 'f5f5f5' },
    line: { color: 'cccccc', width: 1, dashType: 'dash' }
  });
  slide.addText('图片区域', {
    x: imgX, y: imgY + imgH / 2 - 0.2, w: imgW, h: 0.4,
    fontSize: 14, color: '999999', align: 'center'
  });
}
```

#### 5. 内容提取顺序

**问题**：HTML 中的内容顺序和预期不一致，导致解析遗漏。

**推荐顺序**：
```javascript
function createContentSlide(slide, slideHtml) {
  // 1. 提取标题栏
  const headerMatch = slideHtml.match(/class="slide-header"[^>]*>([\s\S]*?)<\/div>/);
  
  // 2. 提取 text-section（用栈匹配）
  const textHtml = extractTextSection(slideHtml);
  
  // 3. 提取图片（排除背景图）
  const images = extractImages(slideHtml);
  
  // 4. 处理文本内容
  if (textHtml) {
    // h2 标题
    // h3 之前的段落
    // 网格布局（five-grid, three-grid, four-grid）
    // 流程图（flow-chart）
    // h3 及其内容（需要 split 处理多个 h3）
  }
}
```

### ✅ 完整转换脚本模板

参考文件：`assets/scripts/html-to-pptx.js`

关键要点：
1. 使用栈匹配嵌套 HTML 结构
2. 分别处理不同类型的内容（段落、列表、网格、流程图）
3. 验证图片路径是否存在
4. 按正确顺序添加 PPT 元素（背景 → 遮罩 → 文字 → 图片）

---

## Resources

### references/
- `style-extraction.md` - 风格提取详细指南
- `work-report-layouts.md` - 工作汇报常用布局模板
- `image-handling.md` - 图片处理详细说明
- `ai-illustration-prompts.md` - AI 配图提示词模板

### assets/
- `html-template/` - HTML/CSS 模板文件
  - `base.css` - 基础样式
  - `slide.html` - 页面模板