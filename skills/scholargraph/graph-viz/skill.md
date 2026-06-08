# Interactive Knowledge Graph / 交互式知识图谱

将知识图谱数据转换为交互式 D3.js 力导向图 HTML，支持节点探索和论文预览。

## 功能

- **D3.js 力导向布局**: 基于 D3.js v7，节点大小反映关联论文数，边粗细反映概念紧密度
- **交互操作**: 缩放平移、节点拖拽、点击查看详情、悬停 tooltip
- **侧面板**: 点击节点显示详情、关联节点列表和相关论文
- **论文预览**: 点击"查看演示"在新标签页打开简版论文演示
- **搜索功能**: 输入关键词高亮匹配节点并自动定位
- **图例**: 类别颜色映射和关系类型说明

## 用法

```bash
# 基本用法 — 从已有图谱生成交互式 HTML
lit graph-interactive dl-graph --output dl-interactive.html

# 不嵌入论文数据（更轻量）
lit graph-interactive my-graph --no-paper-viz
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<name>` | 图谱名称（必填） | - |
| `--output <file>` | 输出 HTML 文件路径 | `<name>-interactive.html` |
| `--no-paper-viz` | 不嵌入论文数据 | false（默认嵌入） |

## 可视化映射

### 节点

| 属性 | 映射规则 |
|------|---------|
| 大小（半径） | `15 + sqrt(paperCount) * 8`，上限 60px |
| 颜色 | foundation=#4FC3F7, core=#FFB74D, advanced=#CE93D8, application=#81C784 |
| 标签 | 节点名称，字号随半径缩放 |

### 边

| 属性 | 映射规则 |
|------|---------|
| 粗细 | `relationWeight + sharedPaperCount * 0.5`，范围 [1, 8]px |
| 颜色 | prerequisite=#EF5350, derived=#AB47BC, component=#42A5F5, related=#78909C |
| 样式 | prerequisite=实线, derived=长虚线, component=短虚线, related=点线 |
| 权重 | prerequisite=3, derived=2.5, component=2, related=1 |

### 力导向参数

```
forceLink:     distance = 120 - strokeWidth * 5
forceManyBody: strength = -200 - radius * 5
forceCollide:  radius + 8
forceCenter:   width/2, height/2
```

## 交互功能

| 操作 | 功能 |
|------|------|
| 滚轮 | 缩放画布 |
| 拖拽画布 | 平移视图 |
| 拖拽节点 | 移动节点位置 |
| 点击节点 | 右侧面板显示详情和论文列表 |
| 悬停节点 | tooltip 显示名称和论文数 |
| 搜索框 | 高亮匹配节点并自动定位 |
| 点击"查看演示" | 新标签页打开简版论文演示 |

## 集成 paper-viz

图谱和论文演示通过 `PaperVizBridge` 桥接：

1. `buildAllPaperPayloads(graph)` 从 literatureIndex 中提取每个节点的关联论文
2. 论文数据嵌入 HTML 的 `PAPER_DATA` 变量
3. 点击节点 → 侧面板显示论文列表
4. 点击"查看演示" → 客户端生成简版演示（Blob URL + 新标签页）

## 依赖

- **必须**: Bun 运行时，已保存的知识图谱（通过 `graph` 或 `review-graph` 命令创建）
- **前端**: D3.js v7（CDN 加载，无需安装）

## 模块文件

```
graph-viz/
  scripts/
    types.ts              # D3 图谱数据接口
    graph-data-adapter.ts # KnowledgeGraphData → D3GraphData
    html-generator.ts     # 生成交互式 HTML
    paper-viz-bridge.ts   # 图谱→论文演示桥接
  skill.md               # 本文件
```
