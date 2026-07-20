# HTML 模板库

本目录包含 DeepSearch-Kpro 技能的所有 HTML 输出模板。

---

## 模板列表

| 模板文件 | 分析模型 | 使用场景 |
|---------|---------|---------|
| `product-overview-template.html` | 产品概览 | 展示产品/服务的核心定位和背景 |
| `target-users-template.html` | 目标用户分析 | 展示目标用户画像、需求、场景 |
| `core-features-template.html` | 核心功能 | 展示产品核心功能模块 |
| `business-model-canvas-template.html` | 商业模式画布 | 展示商业模式九大模块 |
| `porter-five-forces-template.html` | 波特五力分析 | 分析行业竞争格局 |
| `swot-analysis-template.html` | SWOT 分析 | 分析优势、劣势、机会、威胁 |
| `pestel-analysis-template.html` | PESTEL 分析 | 分析宏观环境六大维度 |
| `competitor-matrix-template.html` | 竞品对比矩阵 | 多维度对比分析竞争对手 |
| `timeline-template.html` | 关键时间线 | 展示关键事件和里程碑 |
| `key-metrics-template.html` | 关键指标 | 展示市场规模、增长率等关键数据 |

---

## 使用方式

### 1. 模板变量替换

每个模板使用 `{{变量名}}` 格式的占位符，使用时需要替换为实际内容。

**示例**：
```html
<!-- 模板中的占位符 -->
<h3>{{产品名称}}</h3>
<p>{{产品定位}}</p>

<!-- 替换后的实际内容 -->
<h3>悟空 Wukong</h3>
<p>企业级 AI 原生工作平台</p>
```

### 2. 模板组合使用

根据研究主题选择 2-4 个相关模板进行组合：

**AI 厂商/产品分析**：
```
产品概览 → PESTEL → 目标用户 → 竞品矩阵 → 商业模式画布 → SWOT → 核心功能
```

**市场竞争分析**：
```
产品概览 → PESTEL → 波特五力 → 竞品矩阵 → 关键指标
```

**商业模式分析**：
```
产品概览 → PESTEL → 商业模式画布 → SWOT
```

**行业研究分析**：
```
产品概览 → PESTEL → 波特五力 → 关键指标 → 时间线
```

---

## 样式说明

### 主模板文件

- **`../html-template.html`**：已包含所有可视化组件的完整 CSS 样式
- 模板支持左右布局（左侧导航 + 右侧内容）
- 已集成所有分析模型的可视化样式

### 颜色系统

| 颜色变量 | 用途 |
|---------|------|
| `--primary` (#FF6A00) | 主色调，强调重点 |
| `--secondary` (#1565C0) | 次要色，辅助信息 |
| `--dark` (#1a1a2e) | 深色背景，导航栏 |
| `--accent` (#E53E3E) | 强调色，警告/高亮 |
| `--green` (#38A169) | 成功/优势 |
| `--purple` (#805AD5) | 特色/创新 |

### 标签颜色类

```html
<span class="tag tag-orange">橙色标签</span>
<span class="tag tag-blue">蓝色标签</span>
<span class="tag tag-green">绿色标签</span>
<span class="tag tag-red">红色标签</span>
<span class="tag tag-purple">紫色标签</span>
<span class="tag tag-teal">青色标签</span>
```

### 强度指示类

```html
<span class="intensity intensity-high">极高</span>
<span class="intensity intensity-med">中等</span>
<span class="intensity intensity-low">低</span>
```

### 竞争力指示点

```html
<span class="dot dot-high"></span> 强
<span class="dot dot-mid"></span> 中
<span class="dot dot-low"></span> 弱
```

---

## 完整 HTML 页面结构

生成完整报告时，按以下顺序组合：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{{报告标题}}</title>
  <!-- 基础样式 -->
</head>
<body>
  <!-- 导航栏 -->
  <nav>...</nav>
  
  <!-- Hero 区域 -->
  <div class="hero">...</div>
  
  <!-- 内容区域 -->
  <div class="container">
    <!-- AI 厂商/产品分析推荐顺序 -->
    <!-- 1. 产品概览 -->
    <!-- 2. PESTEL 分析 -->
    <!-- 3. 目标用户 -->
    <!-- 4. 竞品矩阵 -->
    <!-- 5. 商业模式画布 -->
    <!-- 6. SWOT 分析 -->
    <!-- 7. 核心功能 -->
    <!-- 8. 关键指标（可选） -->
    <!-- 9. 时间线（可选） -->
    <!-- 10. 综合洞察与结论 -->
  </div>
  
  <!-- 页脚 -->
  <footer>...</footer>
</body>
</html>
```

---

## 注意事项

1. **数据真实性**：所有数据必须来自实际搜索结果，不得编造
2. **来源标注**：每个关键数据点应标注来源
3. **模板选择**：根据研究领域选择合适的模板组合
4. **响应式设计**：模板已支持移动端适配
5. **打印友好**：建议生成时考虑打印 CSS 优化

---

## 更新记录

- **v1.0.0** (2026-03-18): 初始版本，创建 10 个基础模板
