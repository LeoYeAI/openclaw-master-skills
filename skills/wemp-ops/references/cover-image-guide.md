# 封面图设计指南

## 五维度选择体系

封面图由 5 个独立维度交叉定义。每个维度独立选择，通过兼容矩阵确保组合合理。

```
文章内容 → 自动推荐五维度组合 → 老板确认/调整 → 组装 prompt → 生成
```

---

### 维度 1：构图类型（Type）

| 类型 | 构图方式 | 视觉区占比 | 适用文章 |
|------|---------|-----------|---------|
| `hero` | 大视觉冲击 + 标题覆盖，戏剧性构图 | 视觉 60-70% | 产品分析、重磅发布 |
| `conceptual` | 抽象概念可视化，信息分区，干净 | 视觉 50% | 技术架构、方法论 |
| `typography` | 文字为主体元素（40%+面积），极少视觉 | 文字 60% | 观点文、金句、声明 |
| `metaphor` | 具象物体隐喻抽象概念，符号化 | 视觉 60% | 成长、转型、哲理 |
| `split` | 左右或上下对比分屏，强烈视觉对照 | 各 50% | 对比文、before/after |
| `minimal` | 单一焦点 + 大量留白（60%+） | 视觉 30% | 极简核心概念、禅意 |

### 维度 2：配色方案（Palette）

| 配色 | 色值 | 视觉感受 | 适用 |
|------|------|---------|------|
| `tech-blue` | #1a1f5c → #7c3aed | 科技/紫蓝渐变 | AI产品、技术拆解 |
| `insight-blue` | #1e3a5f → #3b82f6 | 理性/深蓝 | 方法论、框架思考 |
| `action-orange` | #f97316 → #eab308 | 活力/橙黄 | 效率提升、实战 |
| `solution-green` | #10b981 → #f97316 | 解决方案/绿橙 | 场景方案、破局 |
| `trend-cyan` | #0891b2 → #06b6d4 | 趋势/蓝绿 | 行业观察、前沿 |
| `mono` | #1A1A1A + #F5F5F5 | 极简/黑白灰 | 哲理、极简、金句 |
| `warm` | #F5E6D0 + #D4956A + #7BA3A8 | 温暖/莫兰迪 | 个人故事、感悟 |
| `dark` | #0F172A + #3B82F6 + #06B6D4 | 高级/深色 | 电影感、高级观点 |

### 维度 3：渲染风格（Rendering）

| 渲染 | 视觉特征 | Prompt 关键词 |
|------|---------|-------------|
| `3d-icon` | 现代3D图标、光效、微渐变 | modern 3D style icons, subtle glow, depth |
| `flat-vector` | 扁平矢量、干净线条、无阴影 | flat vector, clean lines, no shadows, solid colors |
| `hand-drawn` | 手绘马克笔、不均匀线条 | hand-drawn marker style, uneven strokes, sketch quality |
| `screen-print` | 丝网印刷、半色调、2-4色 | screen print poster art, halftone dots, 2-4 flat colors, stencil-cut |

### 维度 4：文字密度（Text）

| 级别 | 文字内容 | 适用 |
|------|---------|------|
| `none` | 纯视觉，无文字 | 抽象概念封面（少用） |
| `title-only` | 仅主标题（**默认**） | 大多数文章 |
| `title-subtitle` | 主标题 + 副标题/系列名 | 系列文章、教程 |

### 维度 5：视觉强度（Mood）

| 级别 | 效果 | 适用 |
|------|------|------|
| `subtle` | 低对比、柔和、专业克制 | 方法论、学术类 |
| `balanced` | 中等对比（**默认**） | 大多数文章 |
| `bold` | 高对比、强冲击、饱和色 | 重磅观点、争议话题 |

---

## 兼容矩阵

### Type × Rendering

| Type \ Rendering | 3d-icon | flat-vector | hand-drawn | screen-print |
|---|:---:|:---:|:---:|:---:|
| `hero` | ✓✓ | ✓ | ✓ | ✓ |
| `conceptual` | ✓✓ | ✓✓ | ✗ | ✓ |
| `typography` | ✓ | ✓✓ | ✓ | ✓✓ |
| `metaphor` | ✓ | ✓ | ✓✓ | ✓✓ |
| `split` | ✓✓ | ✓✓ | ✓ | ✓ |
| `minimal` | ✓ | ✓✓ | ✓ | ✓✓ |

### Type × Mood

| Type \ Mood | subtle | balanced | bold |
|---|:---:|:---:|:---:|
| `hero` | ✓ | ✓✓ | ✓✓ |
| `conceptual` | ✓✓ | ✓✓ | ✓ |
| `typography` | ✓ | ✓✓ | ✓✓ |
| `metaphor` | ✓✓ | ✓✓ | ✓ |
| `split` | ✓ | ✓✓ | ✓✓ |
| `minimal` | ✓✓ | ✓✓ | ✗ |

### Palette × Rendering

| Palette \ Rendering | 3d-icon | flat-vector | hand-drawn | screen-print |
|---|:---:|:---:|:---:|:---:|
| `tech-blue` | ✓✓ | ✓ | ✗ | ✓ |
| `insight-blue` | ✓✓ | ✓✓ | ✗ | ✓ |
| `action-orange` | ✓✓ | ✓ | ✓ | ✓ |
| `solution-green` | ✓✓ | ✓ | ✓ | ✗ |
| `trend-cyan` | ✓✓ | ✓✓ | ✗ | ✓ |
| `mono` | ✓ | ✓✓ | ✓ | ✓✓ |
| `warm` | ✓ | ✓ | ✓✓ | ✓ |
| `dark` | ✓✓ | ✓ | ✗ | ✓✓ |

> ✓✓ 强推荐 | ✓ 可用 | ✗ 不推荐

**兼容检查**：选定五维度后，检查上方 3 张矩阵中是否有 ✗ 组合。有则提示调整。

---

## 内容信号自动推荐

根据文章关键词自动推荐五维度组合：

| 文章关键词/类型 | Type | Palette | Rendering | Text | Mood |
|---------------|------|---------|-----------|------|------|
| AI、产品、工具、拆解、评测 | `hero` | `tech-blue` | `3d-icon` | title-only | balanced |
| 架构、框架、系统、分层、原理 | `conceptual` | `insight-blue` | `flat-vector` | title-only | subtle |
| 观点、趋势、判断、声明、预测 | `typography` | `mono` | `screen-print` | title-only | bold |
| 成长、转型、个人经历、反思 | `metaphor` | `warm` | `hand-drawn` | title-only | balanced |
| vs、对比、before/after、选型 | `split` | `tech-blue` | `3d-icon` | title-only | bold |
| 极简、核心、本质、一个概念 | `minimal` | `mono` | `flat-vector` | title-only | subtle |
| 效率、实战、工具实操 | `hero` | `action-orange` | `3d-icon` | title-subtitle | balanced |
| 行业、前沿、趋势报告 | `hero` | `trend-cyan` | `3d-icon` | title-only | balanced |
| 解决方案、破局、方法 | `hero` | `solution-green` | `3d-icon` | title-only | balanced |
| 电影感、高级、深度长文 | `typography` | `dark` | `screen-print` | title-only | bold |

---

## 预设快捷方式

常用组合一键选择：

| 预设名 | Type | Palette | Rendering | 典型文章 |
|--------|------|---------|-----------|---------|
| `ai-product` | hero | tech-blue | 3d-icon | AI产品拆解（**最常用**） |
| `methodology` | conceptual | insight-blue | flat-vector | 方法论/框架文 |
| `bold-opinion` | typography | dark | screen-print | 观点输出/声明 |
| `pm-growth` | metaphor | warm | hand-drawn | 个人成长/转型 |
| `versus` | split | tech-blue | 3d-icon | 对比类文章 |
| `zen-core` | minimal | mono | flat-vector | 极简深度文 |
| `efficiency` | hero | action-orange | 3d-icon | 效率/实战 |
| `trend-report` | hero | trend-cyan | 3d-icon | 行业观察 |

Text 和 Mood 默认为 `title-only` + `balanced`，除非预设特别指定（如 bold-opinion → bold）。

---

## 尺寸规范

| 用途 | 比例 | 生成尺寸 | 后处理 |
|------|------|---------|--------|
| 公众号封面 | 2.35:1 | `2560x1440`(16:9) | `sips -c 1090 2560` 裁剪 |
| 公众号次条 | 1:1 | `1920x1920` | 无 |
| 小红书封面 | 3:4 | `1680x2240` | 无 |

---

## Prompt 组装

### 步骤

1. **选定五维度**（自动推荐或手动选择）
2. **兼容矩阵校验**（检查 3 张矩阵无 ✗）
3. **存 prompt 文件**：`prompts/00-cover.md`（⛔ 先存后生）
4. **生成图片**
5. **裁剪**（如需 2.35:1）

### Prompt 模板

```markdown
---
type: [hero/conceptual/typography/metaphor/split/minimal]
palette: [配色名]
rendering: [渲染名]
text: [none/title-only/title-subtitle]
mood: [subtle/balanced/bold]
---

[渲染风格的 Prompt 关键词，从维度3表格中复制]

配色：[配色色值，从维度2表格中复制]

构图：[构图方式描述，从维度1表格中复制]

内容：
- 标题：「[中文标题]」
- 副标题：「[副标题，如有]」
- 视觉元素：[与文章主题相关的具象物体/抽象图形]

约束：
- 中文文字清晰可读
- 文字和视觉不重叠
- 不要 emoji
- 横版，高质量
```

### Seedream 调用

```bash
<WORKSPACE>/scripts/seedream-generate.sh \
  "[组装好的 prompt]" \
  cover.jpg "2560x1440" 1

# 裁剪为 2.35:1
sips -c 1090 2560 cover.jpg
```

---

## 多方案选择

每次封面图出 **2-3 个方案**供老板选择：

```markdown
## 方案 A（推荐）
- 预设：ai-product（hero + tech-blue + 3d-icon）
- 视觉：[具体视觉元素描述]

## 方案 B
- 预设：bold-opinion（typography + dark + screen-print）
- 视觉：[具体视觉元素描述]

## 方案 C（可选）
- 预设：methodology（conceptual + insight-blue + flat-vector）
- 视觉：[具体视觉元素描述]
```

方案之间必须在 **Type 或 Rendering** 上有明显差异（不只是换配色）。

---

## 生图工具优先级

1. **Seedream 5.0 Lite**（优先）：`<WORKSPACE>/scripts/seedream-generate.sh`，0.22元/张，无水印
2. **nano-banana-pro**（备选）：Gemini 免费层级，需去水印
3. **DashScope qwen-image-2.0-pro**（中文文字专用）：当 Seedream 中文渲染失败时
4. **HTML 截图**（兜底）：typography 类型封面可用 HTML 精确控制文字

---

## 内容结构图（可选）

放在文章开头、封面图之后，帮读者一图看全文。

### 风格

Graphic Recording / Visual Thinking 手绘风格：
- 白纸背景，无横线
- 黑色细线笔轮廓 + 彩色标记（青色、橙色、柔和红色）
- 放射状布局，箭头连接
- 16:9 比例

### Prompt 模板

```
Create a hand-drawn sketch visual summary about [文章主题].
Clean white paper background, no lines.
Art style: graphic recording / visual thinking.
Black fine-tip pen for outlines and text.
Colored markers (cyan, orange, soft red) for emphasis.
Main title "[文章标题]" centered in a 3D rectangular box.
Surround with radially distributed simple doodles, icons, and diagrams:
- [要点1]
- [要点2]
- [要点3]
Connect ideas with arrows. Clear hand-written block letters.
Layout 16:9, high quality.
```

### 决策规则

- 文章 ≥ 3 个主要观点：建议生成
- 文章内容简单或时间紧迫：可跳过

---

## 质量检查

- [ ] 五维度组合通过兼容矩阵检查
- [ ] Prompt 已保存到 `prompts/00-cover.md`
- [ ] 中文文字清晰可读
- [ ] 颜色鲜明，吸引眼球
- [ ] 主题契合文章内容
- [ ] 视觉和文字不重叠
- [ ] 裁剪后比例正确（2.35:1）
