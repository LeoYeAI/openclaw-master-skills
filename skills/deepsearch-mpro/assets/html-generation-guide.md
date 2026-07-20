# HTML 报告生成指南

## 概述

本指南说明如何使用 `html-template.html` 生成专业的咨询研究报告 HTML 版本。

---

## 设计风格

**深蓝色政务/企业内报风格**：
- 左侧：树状导航（固定）
- 右侧：内容展示区
- 主色调：深蓝色（#1a2332）+ 橙色强调（#ff7d00）
- 数据密集：表格为主体，信息密度高

---

## 生成流程

### Step 1：准备 Markdown 报告

确保已完成 Markdown 格式的咨询研究报告，包含：

- 执行摘要（Abstract）
- 引言（Introduction）
- 正文章节（多个章节）
- 结论（Conclusion）
- 参考文献（References）
- 附录（可选）

### Step 2：解析 Markdown 结构

使用以下规则将 Markdown 转换为 HTML 模板变量：

#### 2.1 报告元数据

```javascript
// 提取报告标题
REPORT_TITLE = markdown.match(/^#\s+(.+)$/m)[1];

// 生成日期
DATE = new Date().toLocaleDateString('zh-CN');

// 数据来源数量
DATA_SOURCES = references.length;
```

#### 2.2 导航项生成

```javascript
// 提取所有 ## 标题作为导航项
NAV_ITEMS = '';

markdownHeaders.forEach((header, index) => {
    const id = header.toLowerCase().replace(/\s+/g, '-');
    NAV_ITEMS += `
        <li class="nav-item">
            <a class="nav-link" data-tab="${id}">${header}</a>
        </li>
    `;
});
```

#### 2.3 内容转换

**Markdown → HTML 转换规则**：

| Markdown 元素 | HTML 输出 |
|--------------|-----------|
| `## 标题` | `<h2 class="section-title">标题</h2>` |
| `### 标题` | `<h3 class="subsection-title">标题</h3>` |
| `#### 标题` | `<h4 class="subsubsection-title">标题</h4>` |
| `**粗体**` | `<strong>粗体</strong>` |
| `*斜体*` | `<em>斜体</em>` |
| `[链接](url)` | `<a href="url">链接</a>` |
| `> 引用` | `<blockquote><p>引用</p></blockquote>` |
| 表格 | 使用模板中的表格样式 |
| 列表 | `<ul>/<ol>` |

#### 2.4 关键发现框

将 Markdown 中的关键发现转换为：

```markdown
**核心发现**：
1. 发现1
2. 发现2
```

转换为：

```html
<div class="key-findings">
    <div class="key-findings-title">核心发现</div>
    <ol>
        <li>发现1</li>
        <li>发现2</li>
    </ol>
</div>
```

#### 2.5 参考文献格式

```markdown
[1] 作者. 标题[类型]. URL, 日期.
```

转换为：

```html
<div class="reference-item">
    [1] 作者. 标题[类型]. <a href="URL">URL</a>, 日期.
</div>
```

---

## 模板变量说明

### 必填变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `{{REPORT_TITLE}}` | 报告标题 | "2024年中国护肤市场分析报告" |
| `{{DATE}}` | 生成日期 | "2026年3月17日" |
| `{{DATA_SOURCES}}` | 数据来源数量 | "15" |
| `{{NAV_ITEMS}}` | 导航项HTML | `<li>...</li>` 列表 |
| `{{ABSTRACT_CONTENT}}` | 摘要内容 | 执行摘要HTML |
| `{{INTRODUCTION_CONTENT}}` | 引言内容 | 引言部分HTML |
| `{{MAIN_SECTIONS}}` | 正文章节 | 所有章节HTML |
| `{{REFERENCES_LIST}}` | 参考文献列表 | 参考文献 HTML |
| `{{APPENDIX_CONTENT}}` | 附录内容 | 附录部分HTML |

---

## 完整示例

### 输入：Markdown 报告

```markdown
# 2024年中国护肤市场分析报告

## Abstract

**核心发现**：
1. 市场规模达到 800 亿元
2. 年增长率 12%
3. 线上渠道占比 45%

---

## 1. Introduction

### 1.1 研究背景

本研究旨在分析中国护肤市场的现状与趋势...

### 1.2 市场规模

| 年份 | 市场规模 | 增长率 |
|------|---------|--------|
| 2022 | 650亿 | 10% |
| 2023 | 720亿 | 11% |
| 2024 | 800亿 | 12% |

**分析**：市场规模持续增长...

---

## References

[1] 艾瑞咨询. 2024年中国护肤品行业研究报告. https://...
```

### 输出：HTML 页面

使用 `html-template.html` + 变量替换生成完整的 HTML 页面。

---

## 使用说明

### 方式1：AI 自动生成

在 `consulting-analysis` 技能的阶段2中，AI 会：

1. 生成 Markdown 格式报告
2. 自动解析 Markdown 结构
3. 使用 `html-template.html` 生成 HTML
4. 输出两个文件：`report.md` 和 `report.html`

### 方式2：手动转换

```python
# 使用 Python 脚本转换
python scripts/generate_html.py --input report.md --template assets/html-template.html --output report.html
```

---

## 设计规范

### 颜色规范

| 元素 | 颜色代码 | 说明 |
|------|---------|------|
| 主色调（深蓝） | #1a2332 | 导航背景、标题 |
| 强调色（橙色） | #ff7d00 | 高亮、边框 |
| 内容背景 | #ffffff | 内容区 |
| 文字颜色 | #2c3e50 | 正文 |
| 次要文字 | #7f8c8d | 元数据 |

### 字体规范

- **主字体**：PingFang SC, Microsoft YaHei
- **标题**：700（粗体）
- **正文**：400（正常）
- **行高**：1.8

### 响应式断点

- **桌面**：> 1024px（左侧导航 + 右侧内容）
- **平板**：768px - 1024px（缩小导航）
- **手机**：< 768px（垂直布局）

---

## 输出要求

### 文件命名

- Markdown：`{主题关键词}-report-{日期}.md`
- HTML：`{主题关键词}-report-{日期}.html`

示例：
```
skincare-market-report-20260317.md
skincare-market-report-20260317.html
```

### 同步输出

**默认行为**：阶段2 完成后，同时输出 Markdown 和 HTML 两个文件。

---

## 注意事项

1. **数据可视化**：HTML 版本可以嵌入图表（使用 Chart.js 或 ECharts）
2. **交互性**：左侧导航支持点击跳转
3. **打印友好**：使用 `@media print` 隐藏导航，只打印内容
4. **SEO 优化**：使用语义化 HTML 标签
5. **可访问性**：添加 ARIA 标签

---

## 版本历史

- **v1.0.0**（2026-03-17）：初始版本，深蓝色政务风格
