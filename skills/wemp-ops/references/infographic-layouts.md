# 公众号信息图布局库

正文配图中"信息图"类型的专用布局参考。与 `illustration-prompts.md` 中的 Type 维度配合使用。

> 本文件补充 `illustration-prompts.md` 中的 `framework` / `infographic` / `flowchart` / `comparison` Type。
> 当 Type 确定后，可从本文件选择更具体的信息图布局。

---

## 布局索引

| 布局 | 适用场景 | 推荐 Style |
|------|---------|-----------|
| `bento-grid` | 多主题概览、功能模块 | notion-sketch / tech-flat |
| `iceberg` | 表面vs深层、显性vs隐性 | notion-sketch / warm-doodle |
| `funnel` | 筛选/转化、漏斗逻辑 | tech-flat |
| `hub-spoke` | 核心概念+辐射分支 | notion-sketch / tech-flat |
| `bridge` | 问题→解决方案的跨越 | notion-sketch / warm-doodle |
| `hierarchical-layers` | 分层/金字塔/优先级 | tech-flat / notion-sketch |
| `linear-progression` | 时间线/进程/阶段演变 | notion-sketch / tech-flat |
| `dense-modules` | 高密度信息大图、完全指南 | tech-flat |

---

## 布局详细定义

### bento-grid（便当盒网格）

```
结构：模块化网格，不同大小的矩形单元
特点：混合 1x1、2x1、1x2 单元，Hero 单元突出主题
视觉：清晰的单元边界，每个单元有标题+简要内容+小图标
```

**适用**：
- "5个AI能力模块"全景图
- 产品功能总览
- 文章要点概览

**Prompt 指导**：
> Modular bento-grid layout with rectangular cells of mixed sizes. One hero cell (2x2) for the main concept, surrounded by smaller cells. Each cell has a title, brief content, and a simple icon. Clear boundaries between cells.

---

### iceberg（冰山图）

```
结构：水平线分割上下两部分
上方（水面上）：显而易见的、表面的（较小）
下方（水面下）：隐藏的、深层的（较大，占 60-70%）
视觉：上方明亮，下方渐暗；水线清晰
```

**适用**：
- "你看到的PM工作 vs 真实PM工作"
- "AI产品 — 用户看到的 vs 背后的工程"
- 表面现象 vs 根本原因

**Prompt 指导**：
> Iceberg diagram with a clear waterline dividing visible (above, smaller, brighter) from hidden (below, larger, darker). The underwater section is 3x the size of the above-water tip. Gradient showing depth. Labels on both sides.

---

### funnel（漏斗图）

```
结构：从宽到窄的漏斗形，3-5 层递进
视觉：每层颜色渐变或区分，层间有数字/百分比标注
底部是最终输出/结果
```

**适用**：
- "从100个需求到1个MVP"
- 用户转化漏斗
- 信息筛选/决策过滤

**Prompt 指导**：
> Funnel diagram tapering from wide (top) to narrow (bottom), with 3-5 distinct layers. Each layer has a label and a number/percentage. Colors gradient from light (top) to deep (bottom). Arrow at bottom pointing to the final output.

---

### hub-spoke（轮辐图）

```
结构：中心一个核心节点，4-8 个分支向外辐射
视觉：中心节点最大最醒目，分支大小一致，连接线清晰
可选：分支可以有二级子节点
```

**适用**：
- "Agent的6种记忆类型"
- 核心概念+多维解读
- 组织架构/能力地图

**Prompt 指导**：
> Hub-and-spoke diagram with one large central node connected to 4-8 smaller peripheral nodes by straight or curved lines. Central node is the main concept. Each spoke node has a title and brief description. Clean, radial arrangement.

---

### bridge（桥梁图）

```
结构：左侧是"现状/问题"，右侧是"目标/方案"，中间是跨越的桥
视觉：桥梁连接两岸，桥上标注"如何跨越"的关键步骤
底部是"深渊/风险"（可选）
```

**适用**：
- "传统PM → AI时代PM的跨越"
- 问题→解决方案
- 能力差距分析

**Prompt 指导**：
> Bridge diagram connecting "Problem" (left cliff) to "Solution" (right cliff). The bridge itself is labeled with 3-4 key actions/steps needed to cross. Optional: a gap/abyss below labeled with risks of not crossing.

---

### hierarchical-layers（层级/金字塔）

```
结构：3-5 层从底到顶递增/递减
视觉：金字塔形或堆叠层，底层最宽最基础，顶层最窄最高级
每层有标题+简述
```

**适用**：
- "Skill系统的3层架构"
- 马斯洛需求层次类比
- 技术栈分层

**Prompt 指导**：
> Pyramid/layered diagram with 3-5 horizontal layers, widest at bottom (foundation) tapering to narrow at top (highest level). Each layer has a distinct color, title, and 2-3 bullet points. Clear visual hierarchy.

---

### linear-progression（线性进程）

```
结构：从左到右（或从上到下）的时间线/阶段线
视觉：3-6 个节点，每个节点是一个阶段/里程碑，箭头连接
节点可以有日期、标题、简述
```

**适用**：
- "公众号运营4周复盘"
- 产品迭代路线图
- 技术演进历史

**Prompt 指导**：
> Horizontal timeline with 3-6 milestone nodes connected by arrows from left (earliest) to right (latest). Each node has a date/label on top and a brief description below. A progress indicator or color gradient showing advancement.

---

### dense-modules（高密度模块）

```
结构：6-7 个功能型模块紧密排列，几乎无留白
模块类型：
  - 品牌/选项阵列（4-8 项 + "最佳"推荐标记）
  - 规格刻度（数值量表 + 质量指标）
  - 深度解析（局部放大/拆解视图）
  - 场景对比（3-6 个使用场景 + 推荐）
  - 识别技巧（检查清单：看/测/查）
  - 踩坑警示（3-5 个误区 + 后果）
  - 快速参考（决策树/摘要表）
每个模块有编号/标签
```

**适用**：
- "AI PM完全指南"
- 产品选购攻略
- 完整知识体系一张图

**Prompt 指导**：
> High-density infographic with 6-7 distinct labeled modules packed tightly. Each module serves a specific purpose (selection grid, specification scale, deep-dive, scenario comparison, identification tips, warning zone, quick reference). Minimal whitespace. Each module has a coordinate label (MOD-1, MOD-2...). Information in every corner. Smaller text acceptable for density.

**注意**：这种布局信息量极大，建议配合 `tech-flat` 或 `mermaid-render` 风格，确保可读性。正文中最多用 1 次。

---

## 选择指南

| 文章内容特征 | 推荐布局 |
|-------------|---------|
| 文章介绍一个核心概念 + 多个分支/维度 | `hub-spoke` |
| 文章论述"表面看到的 vs 真正的" | `iceberg` |
| 文章有明确的层级/优先级关系 | `hierarchical-layers` |
| 文章有时间演进或阶段划分 | `linear-progression` |
| 文章是"问题→解决方案"结构 | `bridge` |
| 文章有筛选/转化/逐步减少的逻辑 | `funnel` |
| 文章需要多主题概览（5+ 主题） | `bento-grid` |
| 文章需要一张"完全指南"大图 | `dense-modules` |
