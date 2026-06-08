# Style Extraction Guide

Detailed guide for extracting visual style from PPT screenshots.

## Color Extraction

### Primary Colors to Identify

| Color Type | Usage | Extraction Method |
|------------|-------|-------------------|
| Primary | Main titles, key highlights, headers | Most prominent dark color |
| Secondary | Subtitles, accents, decorations | Secondary prominent color |
| Background | Slide background | Most common large-area color |
| Text | Body text color | Common text color |
| Accent | Call-to-action, emphasis | Small but notable color |

### Color Analysis Prompt

```
识别图片中的配色方案：

1. 找出最突出的深色作为主色（用于标题）
2. 找出辅助色（用于副标题/装饰）
3. 识别背景色（占据最大面积的纯色）
4. 识别文字色（正文颜色）
5. 找出强调色（用于按钮/重点标注）

输出十六进制色值。
```

### Common Color Schemes

**Business Blue**
```json
{
  "primary": "#1E3A8A",
  "secondary": "#3B82F6",
  "background": "#FFFFFF",
  "text": "#1F2937",
  "accent": "#60A5FA"
}
```

**Professional Gray**
```json
{
  "primary": "#374151",
  "secondary": "#6B7280",
  "background": "#F9FAFB",
  "text": "#111827",
  "accent": "#3B82F6"
}
```

**Warm Orange**
```json
{
  "primary": "#EA580C",
  "secondary": "#FB923C",
  "background": "#FFFBEB",
  "text": "#292524",
  "accent": "#F59E0B"
}
```

---

## Layout Analysis

### Key Layout Elements

1. **Title Position**
   - Top-left (most common)
   - Top-center
   - Left-side vertical

2. **Content Area**
   - Single column (centered)
   - Two columns (left-right)
   - Grid (2x2, 3x2)
   - Left text + Right image
   - Top text + Bottom image

3. **Whitespace Ratio**
   - Minimal (dense content)
   - Moderate (balanced)
   - Generous (clean, modern)

4. **Alignment Style**
   - Left-aligned (formal)
   - Center-aligned (balanced)
   - Justified (dense)

### Layout Analysis Prompt

```
分析这个PPT的布局结构：

1. 标题位置：左上/顶部居中/左侧竖排？
2. 内容区域：几列？图文如何分布？
3. 留白程度：紧凑/适中/宽松？
4. 对齐方式：左对齐/居中/两端对齐？

描述布局特点，给出百分比估计。
```

### Common Layout Patterns

**Title + Bullets**
```
┌─────────────────────────┐
│ [标题]                  │
│                         │
│ • 要点一                │
│ • 要点二                │
│ • 要点三                │
│                         │
└─────────────────────────┘
```

**Left Text + Right Image**
```
┌─────────────────────────┐
│ [标题]                  │
│ ┌────────┐ ┌──────────┐ │
│ │ 文字   │ │  图片    │ │
│ │ 内容   │ │          │ │
│ └────────┘ └──────────┘ │
└─────────────────────────┘
```

**Full Image Background**
```
┌─────────────────────────┐
│ [背景图片]              │
│                         │
│      [居中标题]         │
│      [副标题]           │
│                         │
└─────────────────────────┘
```

---

## Typography Analysis

### Font Characteristics

1. **Title Font**
   - Weight: bold / semi-bold / regular
   - Size: large (36-48px) / medium (28-36px)
   - Style: sans-serif / serif

2. **Body Font**
   - Weight: regular / light
   - Size: 18-24px typical
   - Line-height: 1.4-1.6

### Typography Analysis Prompt

```
分析这个PPT的字体风格：

1. 标题字体：粗细、大小估计
2. 正文字体：粗细、大小估计
3. 层次感：标题和正文的大小差异明显吗？
4. 字体类型：无衬线（现代感）/衬线（传统感）？

给出估计的像素值。
```

---

## Decoration Elements

### Common Decorations

1. **Shapes**
   - Lines (divider, underlines)
   - Rectangles (boxes, cards)
   - Circles (icons, bullets)
   - Rounded corners (modern feel)

2. **Icons**
   - Line icons (minimal)
   - Filled icons (bold)
   - Photo icons (realistic)

3. **Effects**
   - Shadows (subtle depth)
   - Gradients (modern)
   - Transparency (layering)

### Decoration Analysis Prompt

```
识别这个PPT的装饰元素：

1. 形状：线条、矩形、圆形？圆角还是直角？
2. 图标：有吗？线条式还是填充式？
3. 特效：阴影、渐变、透明度？
4. 整体风格：简约/丰富/华丽？

列出所有发现的装饰元素。
```

---

## Style JSON Schema

Complete style descriptor format:

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
    "contentLayout": "two-column",
    "whitespaceRatio": 0.3,
    "alignment": "left"
  },
  "typography": {
    "titleFont": "Microsoft YaHei",
    "titleWeight": "bold",
    "titleSize": 42,
    "bodyFont": "Microsoft YaHei",
    "bodyWeight": "regular",
    "bodySize": 20,
    "lineHeight": 1.5
  },
  "decorations": {
    "shapes": ["rounded rectangles", "horizontal lines"],
    "icons": "minimal line icons",
    "effects": ["subtle shadow"]
  },
  "overall": {
    "style": "professional modern",
    "mood": "clean business",
    "density": "moderate"
  }
}
```