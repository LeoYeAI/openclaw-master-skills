# BettaFish 设计指南

本指南说明 BettaFish 舆情分析 Skill 的设计规范和输出格式。

## 数据采集规范

**重要：本 Skill 不使用任何模拟数据**

所有数据必须通过以下方式实时获取：
- **WebSearch**: 搜索新闻、论坛、社交媒体
- **WebFetch**: 获取页面详细内容
- **Browser**: 访问关键页面
- **Curl**: 命令行获取 API 数据和特殊页面
- **video-frames**: 提取视频关键帧

## 报告内容规范

### 内容充实度要求

**HTML/Word/PDF 报告都必须包含丰富的文本内容，而不仅仅是视觉效果。**

参考示例报告的结构，每个报告必须包含：

1. **执行摘要**
   - 品牌声誉总览（2-3段深入分析）
   - 关键指标表现（KPI卡片 + 详细解读）
   - 主要结论与战略启示（4-5条具体结论）

2. **品牌声量与影响力分析**
   - 整体声量趋势（详细趋势描述 + 数据支撑）
   - 渠道声量分布（平台分析 + 扩散矩阵）
   - 区域声量分布（地域视角分析）

3. **关键事件深度回顾**
   - 每个事件包含：时间线表格 + 多方观点 + 关键数据
   - Query/Media/Insight 三引擎交叉分析框
   - 引用块展示分析师总结

4. **情感与认知分析**
   - 情感光谱分析（图表 + 详细解读）
   - 品牌联想分析
   - 核心议题深度剖析

5. **用户画像分析**
   - 人群属性（代际、地域、身份）
   - 核心触媒习惯

6. **声誉风险与机遇洞察**
   - 主要负面议题追踪
   - 潜在风险预警
   - 正面机遇挖掘

7. **结论与战略建议**
   - SWOT分析总结
   - 具体优化建议（分短期/中期/长期）
   - 下一周期监测重点

8. **数据附录**
   - 关键舆情指标汇总表
   - 权威来源清单

### 内容元素要求

**必须包含的内容元素**：
- ✅ 详细分析段落（每节3-5段）
- ✅ 数据表格（事件时间线、对比数据等）
- ✅ 高亮框（重要信息突出）
- ✅ 引用块（分析师总结、关键结论）
- ✅ 引擎视角框（Query/Media/Insight交叉分析）
- ✅ KPI卡片（配合详细解读）
- ✅ 图表（配合文字说明）

**禁止**：
- ❌ 只有视觉效果没有实质内容
- ❌ 使用模板化占位符文本
- ❌ 只有数据没有分析洞察

## 输出格式

本 Skill **同时生成三种格式的报告**：

### 1. Word 文档 (.docx)

**用途**:
- 正式汇报和向上级提交
- 打印存档
- 邮件附件发送
- 合规性文档

**生成方式**: 使用 `docx` subskill

**格式规范**:

| 元素 | 规范 |
|------|------|
| 封面 | 包含标题、副标题、日期、机构 |
| 目录 | 自动生成，含页码 |
| 正文字体 | Arial 12pt |
| 标题字体 | Arial Bold 14-18pt |
| 行距 | 1.5倍行距 |
| 页眉页脚 | 包含报告标题和页码 |

### 2. PDF 文档 (.pdf)

**用途**:
- 正式汇报
- 跨平台分享
- 不可编辑存档

**生成方式**: 使用 `pdf` subskill

**⚠️ 中文字体要求（重要）**：

PDF 生成时必须使用支持中文的字体，否则中文会显示为黑方块。

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 注册中文字体
pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))  # 宋体
pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))  # 黑体
pdfmetrics.registerFont(TTFont('MicrosoftYaHei', 'C:/Windows/Fonts/msyh.ttc'))  # 微软雅黑

# 创建样式时使用中文字体
title_style = ParagraphStyle(
    'CustomTitle',
    fontName='SimHei',  # 黑体
    fontSize=24
)
body_style = ParagraphStyle(
    'CustomBody',
    fontName='SimSun',  # 宋体
    fontSize=12
)
```

**字体规范**：
- 标题：黑体 (SimHei) 或 微软雅黑 (MicrosoftYaHei)
- 正文：宋体 (SimSun) 或 微软雅黑 (MicrosoftYaHei)
- 表格表头：黑体
- 表格内容：宋体

**⚠️ 中文字体要求（重要）**：

PDF 生成时必须使用支持中文的字体，否则中文会显示为黑方块。

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 注册中文字体
pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))  # 宋体
pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))  # 黑体
pdfmetrics.registerFont(TTFont('MicrosoftYaHei', 'C:/Windows/Fonts/msyh.ttc'))  # 微软雅黑

# 创建样式时使用中文字体
title_style = ParagraphStyle(
    'CustomTitle',
    fontName='SimHei',  # 黑体
    fontSize=24
)
body_style = ParagraphStyle(
    'CustomBody',
    fontName='SimSun',  # 宋体
    fontSize=12
)
```

**字体规范**:
- 正文：宋体 (SimSun) 12pt
- 标题：黑体 (SimHei) 14-18pt
- 表格表头：黑体，内容：宋体

### 3. HTML 交互报告 (.html)

**用途**:
- 演示展示
- 在线分享
- 交互探索

**生成方式**: 使用 `frontend-design` subskill

**设计风格**: Editorial/Magazine（编辑杂志风格）+ **分页导航**

**HTML 导航要求**：

1. **分页显示**：
   - 每个章节独立成页，默认只显示当前页
   - 使用 `display: none/block` 控制页面显示
   - 底部有上一页/下一页按钮

2. **侧边栏导航**：
   - 左侧固定侧边栏
   - 显示所有章节链接
   - 点击跳转到对应页面
   - 当前页面高亮显示

3. **键盘导航**：
   - 左右方向键切换页面
   - 提升浏览体验

4. **章节锚点**：
   - 每个章节有唯一ID
   - 支持URL直接跳转到指定章节

**HTML 结构示例**：
```html
<!-- 侧边栏导航 -->
<nav class="sidebar">
  <ul class="nav-menu">
    <li><a href="#" data-page="page-1">1. 执行摘要</a></li>
    <li><a href="#" data-page="page-2">2. 品牌声量分析</a></li>
    <!-- 更多章节... -->
  </ul>
</nav>

<!-- 分页内容 -->
<main class="main-content">
  <div id="page-1" class="page active">...</div>
  <div id="page-2" class="page">...</div>
</main>

<!-- 分页导航脚本 -->
<script>
  function goToPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
  }
</script>
```

## 编辑杂志风格规范

### 视觉方向

参考高端出版物如：
- **Monocle** - 全球事务与生活方式
- **Wallpaper*** - 设计与建筑
- **Port** - 男士时尚与文化
- **Kinfolk** - 极简生活美学

### 色彩系统

```css
/* 深海军蓝主题 */
--color-bg: #0a192f;           /* 深海蓝背景 */
--color-surface: #112240;       /* 卡片背景 */
--color-surface-light: #233554; /* 边框/分隔 */
--color-primary: #ffd700;       /* 金色强调 */
--color-secondary: #64ffda;     /* 青绿辅助 */
--color-accent: #ff6b6b;        /* 红色警示 */
--color-text: #e6f1ff;          /* 主文字 */
--color-text-muted: #8892b0;    /* 次要文字 */
```

### 字体系统

```css
/* 字体搭配 */
--font-display: 'Playfair Display', Georgia, 'Noto Serif SC', serif;  /* 标题 */
--font-body: 'Source Serif Pro', 'Noto Serif SC', serif;  /* 正文 */
--font-mono: 'JetBrains Mono', monospace;  /* 数据/代码 */
```

**选择理由**:
- **Playfair Display**: 高对比度衬线体，优雅权威
- **Source Serif Pro**: 可读性强，适合长文本
- **JetBrains Mono**: 等宽字体，数据展示清晰

### 布局原则

1. **不对称网格**
   - 打破常规对称，创造视觉张力
   - 主要内容偏左或偏右，留出不规则负空间

2. **慷慨留白**
   - 大段落间距（2-8rem）
   - 内容密度低，呼吸感强

3. **视觉层次**
   ```
   Hero: 杂志级大标题 + 动态背景
   ↓
   Stats: 不对称数据卡片网格
   ↓
   Charts: 艺术化数据可视化
   ↓
   Analysis: 杂志排版正文
   ↓
   Footer: 简洁收尾
   ```

### 动效设计

**页面加载序列**:
```
0.0s - 背景渐变动画开始
0.2s - Label 文字淡入上滑
0.4s - 主标题淡入上滑
0.6s - 副标题淡入上滑
0.8s - 元信息淡入上滑
```

**滚动触发动画**:
```css
.reveal {
    opacity: 0;
    transform: translateY(50px);
    transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.reveal.active {
    opacity: 1;
    transform: translateY(0);
}
```

**微交互**:
- 卡片悬停：上移4px + 阴影加深
- 按钮悬停：背景色变化
- 图表悬停：数据点放大
- 图谱节点悬停：节点放大20%

### 视觉细节

1. **渐变网格背景**
   ```css
   background:
       radial-gradient(ellipse at 20% 80%, rgba(100, 255, 218, 0.03) 0%, transparent 50%),
       radial-gradient(ellipse at 80% 20%, rgba(255, 215, 0, 0.02) 0%, transparent 50%);
   ```

2. **噪点纹理**
   - 添加 subtle noise texture
   - 模拟纸张质感
   - opacity: 0.015

3. **金色细线装饰**
   - 卡片顶部渐变边框
   - 章节分隔线
   - 数据高亮

4. **戏剧性阴影**
   ```css
   box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
   ```

### 图表设计

**情感分布饼图**:
- 甜甜圈样式 (radius: ['45%', '75%'])
- 金色 + 青绿 + 红色配色
- 圆角边框 (borderRadius: 8)
- 悬停放大效果

**趋势折线图**:
- 平滑曲线 (smooth: true)
- 渐变填充区域
- 渐变色线条 (青绿到金色)
- 发光数据点

**平台柱状图**:
- 水平柱状图
- 渐变色填充
- 圆角末端

**知识图谱**:
- D3.js 力导向图
- 节点颜色按类型区分
- 可拖拽交互
- 悬停放大效果

## Subskills 使用指南

### docx Subskill

```javascript
// 生成 Word 文档
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        PageNumber } = require('docx');

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [/* content */]
  }]
});
```

### pdf Subskill

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("舆情分析报告", styles['Title']))
story.append(Spacer(1, 12))
# ... more content

doc.build(story)
```

### frontend-design Subskill

```
使用 frontend-design skill 生成 HTML 报告时指定：
- 风格: Editorial/Magazine
- 主题: 深海军蓝 (#0a192f) + 金色 (#ffd700)
- 字体: Playfair Display + Source Serif Pro
- 组件: Hero、数据卡片、ECharts 图表、D3.js 图谱
- 动画: 页面加载渐现、滚动触发、悬停效果
```

### video-frames Subskill

```bash
# 提取视频关键帧
{baseDir}/subskills/video-frames/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame.jpg
```

## 质量检查清单

### Word/PDF 文档

- [ ] 封面包含标题、日期、机构
- [ ] 目录自动生成
- [ ] 字体符合规范（Arial）
- [ ] 行距 1.5 倍
- [ ] 表格有标题行
- [ ] 页眉页脚正确

### HTML 报告

- [ ] 深海军蓝背景 (#0a192f)
- [ ] 金色强调色 (#ffd700)
- [ ] Playfair Display 标题字体
- [ ] Source Serif Pro 正文字体
- [ ] 渐变网格背景
- [ ] 噪点纹理
- [ ] 页面加载动画
- [ ] 滚动触发动画
- [ ] 情感分布饼图（艺术化）
- [ ] 趋势折线图（电影级动画）
- [ ] 知识图谱（D3.js 交互）
- [ ] 响应式布局

### 数据质量

- [ ] 所有数据来自真实 WebSearch
- [ ] 视频分析使用 video-frames 提取帧
- [ ] 搜索结果经过聚类采样
- [ ] 无模拟数据
- [ ] 不使用数据库

## 技术依赖

### Word 生成
- `docx` subskill (docx-js)

### PDF 生成
- `pdf` subskill (reportlab)

### HTML 生成
- **CDN 资源**:
  - Google Fonts (Playfair Display, Source Serif Pro)
  - ECharts 5.x
  - D3.js 7.x
  - html2canvas
  - jsPDF

### 视频分析
- `video-frames` subskill (ffmpeg)

### 数据处理
- `search_clustering.py` (TF-IDF + KMeans)
- `sentiment_analyzer.py` (规则引擎)
- `graph_generator.py` (D3.js 图谱数据)
