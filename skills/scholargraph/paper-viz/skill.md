# Paper Visualization / 论文可视化演示

将学术论文分析结果转换为交互式 HTML 幻灯片演示，支持编辑和 PPT 导出。

## 功能

- **幻灯片生成**: 自动将论文分析（标题、摘要、关键要点、方法论、实验、贡献、局限性、参考文献）转为 8+ 张幻灯片
- **PDF 图表提取**: 通过 pymupdf 从 PDF 中提取图表，嵌入演示
- **交互式 HTML**: 键盘/触摸/滚轮导航、编辑模式（E 键）、localStorage 自动保存
- **PPT 导出**: 通过 python-pptx 导出为 .pptx 文件
- **学术主题**: 深色/浅色两种学术主题，响应式排版

## 用法

```bash
# 基本用法 — 分析论文并生成演示
lit paper-viz "https://arxiv.org/abs/1706.03762" --output attention.html

# 指定模式和主题
lit paper-viz "https://arxiv.org/abs/2005.14165" --mode deep --theme academic-light

# 同时导出 PPT
lit paper-viz "https://arxiv.org/abs/1706.03762" --output paper.html --ppt

# 手动提供图表目录
lit paper-viz "https://example.com/paper" --figures ./my-figures
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<url>` | 论文 URL（必填） | - |
| `--mode <m>` | 分析深度 (quick/standard/deep) | deep |
| `--theme <t>` | 主题 (academic-dark/academic-light) | academic-dark |
| `--output <file>` | 输出 HTML 文件路径 | 自动生成 |
| `--ppt` | 同时导出 PPT | false |
| `--figures <dir>` | 手动指定图表目录 | 自动提取 |

## 幻灯片结构

| # | 幻灯片 | 内容来源 |
|---|--------|---------|
| 1 | 标题页 | title, authors, venue, year, keywords |
| 2 | 摘要页 | summary, abstract |
| 3-4 | 关键要点 | keyPoints[]（按重要度标注） |
| 5 | 方法论 | methodology.overview, approach, novelty |
| 6+ | 实验结果 | experiments, 提取的图表 |
| 7 | 贡献 | contributions[]（按显著度标注） |
| 8 | 局限与展望 | limitations[], futureWork[] |
| 9 | 参考文献 | relatedWork[], citations |

## 键盘快捷键（HTML 演示）

| 快捷键 | 功能 |
|--------|------|
| ← → / 空格 | 切换幻灯片 |
| Home / End | 跳转首/尾页 |
| E | 切换编辑模式 |
| 滚轮 / 触摸滑动 | 切换幻灯片 |

## 依赖

- **必须**: Bun 运行时, AI Provider（用于论文分析）
- **可选**: Python + pymupdf（PDF 图表提取）
- **可选**: Python + python-pptx（PPT 导出）

## 模块文件

```
paper-viz/
  scripts/
    types.ts              # 数据接口定义
    slide-builder.ts      # PaperAnalysis → PresentationData
    html-generator.ts     # 生成自包含 HTML
    pdf-figure-extractor.ts  # PDF 图表提取
    ppt-exporter.ts       # PPT 导出
  skill.md               # 本文件
```
