#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BettaFish 报告生成指导模块
说明如何使用 subskills 生成 Word、PDF、HTML 报告
"""

from typing import Dict, Any, List
from datetime import datetime


def generate_word_report_guidance() -> str:
    """
    生成 Word 报告的指导说明

    使用 docx subskill 通过 docx-js 生成专业 Word 文档
    """
    guidance = """
# 使用 docx Subskill 生成 Word 报告

## 步骤

1. **安装 docx-js**
   ```bash
   npm install -g docx
   ```

2. **生成报告**（JavaScript）
   ```javascript
   const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
           Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
           PageNumber, PageBreak } = require('docx');
   const fs = require('fs');

   const doc = new Document({
     styles: {
       default: { document: { run: { font: "Arial", size: 24 } } },
       paragraphStyles: [
         { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
           run: { size: 32, bold: true, font: "Arial" },
           paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
         { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
           run: { size: 28, bold: true, font: "Arial" },
           paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },
       ]
     },
     sections: [{
       properties: {
         page: {
           size: { width: 12240, height: 15840 },  // US Letter
           margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
         }
       },
       headers: {
         default: new Header({
           children: [new Paragraph({
             children: [new TextRun({ text: "舆情分析报告", size: 20 })]
           })]
         })
       },
       footers: {
         default: new Footer({
           children: [new Paragraph({
             children: [
               new TextRun({ text: "Page ", size: 20 }),
               new TextRun({ children: [PageNumber.CURRENT], size: 20 })
             ]
           })]
         })
       },
       children: [
         // 标题
         new Paragraph({
           heading: HeadingLevel.HEADING_1,
           children: [new TextRun("舆情分析报告")]
         }),
         // 内容...
       ]
     }]
   });

   Packer.toBuffer(doc).then(buffer => {
     fs.writeFileSync("舆情分析报告.docx", buffer);
   });
   ```

3. **验证文档**
   ```bash
   python {baseDir}/subskills/docx/scripts/office/validate.py 舆情分析报告.docx
   ```

## 文档结构

- 封面（标题、日期、机构）
- 目录
- 执行摘要
- 舆情概况
- 情感分析
- 话题分析
- 风险识别
- 建议与策略
- 附录
"""
    return guidance


def generate_pdf_report_guidance() -> str:
    """
    生成 PDF 报告的指导说明

    使用 pdf subskill 通过 reportlab 生成 PDF 文档
    """
    guidance = """
# 使用 pdf Subskill 生成 PDF 报告

## 步骤

1. **使用 reportlab 生成 PDF**（Python）
   ```python
   from reportlab.lib.pagesizes import letter, A4
   from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
   from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
   from reportlab.lib import colors
   from reportlab.lib.units import inch

   # 创建 PDF 文档
   doc = SimpleDocTemplate(
     "舆情分析报告.pdf",
     pagesize=letter,
     rightMargin=72,
     leftMargin=72,
     topMargin=72,
     bottomMargin=18
   )

   # 样式
   styles = getSampleStyleSheet()
   title_style = ParagraphStyle(
     'CustomTitle',
     parent=styles['Heading1'],
     fontSize=24,
     spaceAfter=30,
     alignment=1  # Center
   )

   # 构建内容
   story = []

   # 封面
   story.append(Paragraph("舆情分析报告", title_style))
   story.append(Spacer(1, 0.5*inch))
   story.append(Paragraph("分析主题: 某咖啡连锁品牌", styles['Normal']))
   story.append(Spacer(1, 0.3*inch))
   story.append(Paragraph(f"生成日期: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
   story.append(PageBreak())

   # 执行摘要
   story.append(Paragraph("执行摘要", styles['Heading1']))
   story.append(Paragraph("本报告基于...", styles['Normal']))
   story.append(Spacer(1, 0.2*inch))

   # 数据表格
   data = [['平台', '提及量', '占比'],
           ['微博', '400', '40%'],
           ['小红书', '350', '35%'],
           ['抖音', '250', '25%']]

   table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
   table.setStyle(TableStyle([
     ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
     ('FONTSIZE', (0, 0), (-1, 0), 14),
     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
     ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
     ('GRID', (0, 0), (-1, -1), 1, colors.black)
   ]))
   story.append(table)

   # 生成 PDF
   doc.build(story)
   ```

## 文档结构

与 Word 文档保持一致的结构
"""
    return guidance


def generate_html_report_guidance() -> str:
    """
    生成 HTML 报告的指导说明

    使用 frontend-design subskill 生成高质量 HTML
    """
    guidance = """
# 使用 frontend-design Subskill 生成 HTML 报告

## 设计规范

### 编辑杂志风格

- **色彩**: 深海军蓝 (#0a192f) 背景，金色 (#ffd700) 强调
- **字体**: Playfair Display (标题) + Source Serif Pro (正文)
- **布局**: 不对称网格，慷慨留白
- **动画**: 电影级滚动触发效果

### HTML 结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>舆情分析报告</title>

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Serif+Pro:wght@300;400;600&display=swap" rel="stylesheet">

  <!-- ECharts + D3.js -->
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
  <script src="https://d3js.org/d3.v7.min.js"></script>

  <style>
    :root {
      --color-bg: #0a192f;
      --color-surface: #112240;
      --color-primary: #ffd700;
      --color-secondary: #64ffda;
      --font-display: 'Playfair Display', Georgia, serif;
      --font-body: 'Source Serif Pro', serif;
    }

    body {
      font-family: var(--font-body);
      background: var(--color-bg);
      color: #e6f1ff;
    }

    /* Hero 区域 */
    .hero {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
    }

    .hero-title {
      font-family: var(--font-display);
      font-size: clamp(2.5rem, 8vw, 5rem);
      color: var(--color-primary);
    }

    /* 数据卡片 */
    .stat-card {
      background: var(--color-surface);
      border: 1px solid #233554;
      border-radius: 8px;
      padding: 2rem;
    }

    /* 图表容器 */
    .chart-container {
      background: var(--color-surface);
      border-radius: 8px;
      padding: 1.5rem;
    }
  </style>
</head>
<body>
  <!-- Hero 区域 -->
  <section class="hero">
    <h1 class="hero-title">舆情分析报告</h1>
    <p>某咖啡连锁品牌 社交媒体口碑分析</p>
  </section>

  <!-- 数据可视化 -->
  <section>
    <div id="sentiment-chart"></div>
    <div id="trend-chart"></div>
    <div id="knowledge-graph"></div>
  </section>

  <script>
    // ECharts 配置
    // D3.js 力导向图
  </script>
</body>
</html>
```

## 使用 frontend-design Skill

1. 明确设计需求：编辑杂志风格、深海军蓝主题
2. 提供完整数据结构和内容
3. 请求生成包含 ECharts 图表和 D3.js 图谱的 HTML
"""
    return guidance


def prepare_report_data(
    topic: str,
    query_results: List[Dict],
    media_results: List[Dict],
    insight_results: Dict,
    forum_discussion: List[Dict],
    knowledge_graph: Dict
) -> Dict[str, Any]:
    """
    准备报告生成所需的数据结构

    Args:
        topic: 分析主题
        query_results: QueryAgent 结果
        media_results: MediaAgent 结果
        insight_results: InsightAgent 结果
        forum_discussion: ForumEngine 讨论记录
        knowledge_graph: 知识图谱数据

    Returns:
        完整的报告数据结构
    """
    sentiment = insight_results.get('sentiment', {})
    platforms = insight_results.get('platform_stats', {})
    keywords = insight_results.get('keywords', [])
    risks = insight_results.get('risks', [])

    return {
        'topic': topic,
        'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'sentiment': sentiment,
        'platform_stats': platforms,
        'keywords': keywords,
        'risks': risks,
        'trend_data': insight_results.get('trend_data', []),
        'query_summary': {
            'total_sources': len(query_results),
            'key_findings': [r.get('title', '') for r in query_results[:5]]
        },
        'media_summary': {
            'total_videos': len(media_results),
            'key_videos': [m.get('title', '') for m in media_results[:3]]
        },
        'forum_discussion': forum_discussion,
        'knowledge_graph': knowledge_graph,
        'recommendations': {
            'short_term': [
                '加强舆情监测频率，密切关注负面情绪变化趋势',
                '对负面评价及时回应，防止负面情绪发酵扩大',
                '通过官方渠道发布正面信息，平衡舆论导向'
            ],
            'mid_term': [
                '根据用户反馈持续改进产品和服务质量',
                '建立用户社区，培养品牌忠实粉丝群体'
            ],
            'long_term': [
                '持续投入品牌形象建设，提升品牌美誉度',
                '建立完善的危机公关预案和响应机制'
            ]
        }
    }


def get_report_structure() -> Dict[str, List[str]]:
    """
    获取标准报告结构 - 8个核心章节

    Returns:
        报告章节结构，包含详细的子章节
    """
    return {
        'cover': ['标题', '副标题', '日期', '机构'],
        'table_of_contents': ['自动生成的目录，含页码链接'],
        'executive_summary': [
            '1.1 品牌声誉总览（2-3段深入分析）',
            '1.2 关键指标表现（KPI卡片+详细解读）',
            '1.3 主要结论与战略启示（4-5条具体结论）'
        ],
        'brand_volume_analysis': [
            '2.1 整体声量趋势（详细趋势描述+数据支撑）',
            '2.2 渠道声量分布（平台分析+扩散矩阵）',
            '2.3 区域声量分布（地域视角分析+三城演义）'
        ],
        'key_events_review': [
            '3.1 事件一：深度复盘（时间线表格+多方观点+数据）',
            '3.2 事件二：深度复盘（时间线表格+多方观点+数据）',
            '3.3 事件三：深度复盘（时间线表格+多方观点+数据）',
            '3.4 引擎交叉分析（Query/Media/Insight视角）'
        ],
        'sentiment_cognition_analysis': [
            '4.1 情感光谱分析（图表+详细解读+演变轨迹）',
            '4.2 品牌联想分析（从XX到XX的认知转变）',
            '4.3 核心议题分析（深层机制剖析）'
        ],
        'user_persona_analysis': [
            '5.1 人群属性（代际、地域、身份撕裂图谱）',
            '5.2 核心触媒习惯与平台分野'
        ],
        'risk_opportunity_insights': [
            '6.1 主要负面议题追踪与深层机制剖析',
            '6.2 潜在风险预警（从XX到XX的连锁反应）',
            '6.3 正面机遇挖掘（双轮驱动模型）'
        ],
        'conclusions_recommendations': [
            '7.1 品牌SWOT分析总结',
            '7.2 品牌沟通优化建议（从控制-回应到透明-共治）',
            '7.3 治理与服务提升建议',
            '7.4 下一周期监测重点'
        ],
        'appendix': [
            '8.1 关键舆情指标汇总表',
            '8.2 权威来源清单',
            '8.3 分析方法说明',
            '8.4 局限性说明'
        ]
    }


def get_content_elements_guide() -> Dict[str, Any]:
    """
    获取内容元素生成指南

    Returns:
        各类内容元素的生成规范
    """
    return {
        'detailed_paragraphs': {
            'requirement': '每个章节至少3-5段深入分析',
            'guidelines': [
                '解释数据背后的洞察，而非仅罗列数字',
                '使用具体的案例和事例支撑观点',
                '分析原因、影响、趋势，而非表面描述',
                '结合三引擎的发现进行综合分析'
            ]
        },
        'data_tables': {
            'types': [
                '事件时间线表格（时间、事件、信源、影响程度）',
                '平台数据对比表（平台、声量、占比、情绪）',
                'KPI指标汇总表（指标名、数值、变化、备注）',
                '来源清单表（来源、类型、可信度、引用次数）'
            ]
        },
        'highlight_boxes': {
            'usage': '用于突出重要信息、关键发现',
            'format': '带边框的背景色块，包含标题和要点列表',
            'examples': ['平台扩散矩阵分析', '论文硬伤清单', '关键数据']
        },
        'quote_blocks': {
            'usage': '用于展示分析师总结、关键结论、用户原话',
            'format': '左侧边框引用样式',
            'content_sources': [
                '洞察引擎分析师总结',
                '关键媒体评论',
                '代表性用户观点',
                '核心结论陈述'
            ]
        },
        'engine_perspective_boxes': {
            'usage': '展示三引擎的交叉分析视角',
            'format': '带引擎标识的边框框',
            'structure': [
                '[QUERY]: 事实层面的发现',
                '[MEDIA]: 媒体报道和传播分析',
                '[INSIGHT]: 民意数据和情感洞察'
            ]
        },
        'kpi_cards': {
            'requirement': '配合详细解读，而非孤立数字',
            'elements': ['大数字', '标签', '变化趋势', '简短解读'],
            'examples': ['总阅读量+同比变化', '事件频次+对比', '情感谷底值+说明']
        }
    }


def generate_rich_html_report(
    topic: str,
    data: Dict[str, Any],
    style: str = 'editorial-magazine'
) -> str:
    """
    生成内容丰富的 HTML 报告指南

    报告必须包含：
    1. 8个核心章节，每个章节详细文本分析
    2. 数据表格（时间线、对比表等）
    3. 高亮框（重要信息突出）
    4. 引用块（分析师总结）
    5. 引擎视角框（三引擎交叉分析）
    6. KPI卡片（配合解读）
    7. 图表（配合文字说明）
    8. 章节导航（侧边栏或顶部导航 + 锚点跳转）
    """
    guidance = f"""
# 生成内容丰富的 HTML 报告（带章节导航）

## 报告主题: {topic}

### HTML 导航结构要求

**必须实现以下导航功能**：

1. **固定侧边栏导航**：左侧固定目录，点击跳转到对应章节
2. **回到顶部按钮**：滚动后显示，点击平滑滚动到顶部
3. **章节锚点链接**：每个章节有唯一ID，支持URL直接跳转
4. **当前章节高亮**：滚动时自动高亮当前可见章节

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - 舆情分析报告</title>

    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Serif+Pro:wght@300;400;600&display=swap" rel="stylesheet">

    <!-- Chart.js + ECharts -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>

    <style>
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #34495e;
            --accent-color: #3498db;
            --background-color: #ecf0f1;
            --text-color: #333;
            --card-background: #ffffff;
            --border-color: #dcdde1;
            --code-bg: #f5f6fa;
            --quote-border: #3498db;
            --table-header-bg: #f8f9fa;
            --sidebar-width: 280px;
            --header-height: 60px;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family: 'Source Serif Pro', 'Noto Serif SC', serif;
            line-height: 1.8;
            background-color: var(--background-color);
            color: var(--text-color);
        }}

        /* ===== 固定顶部导航栏 ===== */
        .top-nav {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--header-height);
            background: var(--card-background);
            border-bottom: 1px solid var(--border-color);
            z-index: 1000;
            display: flex;
            align-items: center;
            padding: 0 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .top-nav h1 {{
            font-size: 1.2em;
            margin: 0;
            flex: 1;
        }}

        .nav-links {{
            display: flex;
            gap: 20px;
        }}

        .nav-links a {{
            text-decoration: none;
            color: var(--secondary-color);
            font-size: 0.9em;
            transition: color 0.3s;
        }}

        .nav-links a:hover {{
            color: var(--accent-color);
        }}

        /* ===== 固定侧边栏导航 ===== */
        .sidebar {{
            position: fixed;
            left: 0;
            top: var(--header-height);
            width: var(--sidebar-width);
            height: calc(100vh - var(--header-height));
            background: var(--card-background);
            border-right: 1px solid var(--border-color);
            overflow-y: auto;
            padding: 20px;
            z-index: 999;
        }}

        .sidebar-title {{
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--primary-color);
            border-bottom: 2px solid var(--accent-color);
            padding-bottom: 10px;
        }}

        .sidebar-nav {{
            list-style: none;
        }}

        .sidebar-nav li {{
            margin-bottom: 8px;
        }}

        .sidebar-nav a {{
            text-decoration: none;
            color: var(--secondary-color);
            font-size: 0.9em;
            display: block;
            padding: 8px 12px;
            border-radius: 4px;
            transition: all 0.3s;
        }}

        .sidebar-nav a:hover {{
            background: var(--code-bg);
            color: var(--accent-color);
        }}

        .sidebar-nav a.active {{
            background: var(--accent-color);
            color: white;
        }}

        .sidebar-nav .sub-item {{
            padding-left: 20px;
            font-size: 0.85em;
        }}

        /* ===== 主内容区 ===== */
        .main-content {{
            margin-left: var(--sidebar-width);
            margin-top: var(--header-height);
            padding: 30px;
            max-width: calc(100% - var(--sidebar-width));
        }}

        /* 内容区块 */
        .content-section {{
            background-color: var(--card-background);
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            scroll-margin-top: calc(var(--header-height) + 20px);
        }}

        h1, h2, h3, h4 {{
            color: var(--primary-color);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
        }}

        h1 {{
            font-size: 2.2em;
            scroll-margin-top: calc(var(--header-height) + 20px);
        }}

        h2 {{
            font-size: 1.8em;
            margin-top: 30px;
            scroll-margin-top: calc(var(--header-height) + 20px);
        }}

        p {{
            margin-bottom: 1.5em;
            text-align: justify;
            line-height: 1.8;
        }}

        /* 高亮框 */
        .highlight-box {{
            background-color: rgba(52, 152, 219, 0.1);
            border: 1px solid rgba(52, 152, 219, 0.3);
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}

        .highlight-box h4 {{
            color: var(--accent-color);
            margin-top: 0;
            border-bottom: none;
        }}

        /* 引用块 */
        blockquote {{
            border-left: 5px solid var(--quote-border);
            padding: 15px 20px;
            margin: 20px 0;
            background-color: var(--code-bg);
            font-style: italic;
        }}

        /* 引擎视角框 */
        .engine-perspective {{
            border: 1px dashed var(--border-color);
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}

        .engine-perspective .engine-name {{
            font-weight: bold;
            color: var(--accent-color);
            display: block;
            margin-bottom: 10px;
        }}

        /* KPI卡片 */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}

        .kpi-card {{
            background-color: var(--background-color);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid var(--border-color);
        }}

        .kpi-value {{
            font-size: 2.5em;
            font-weight: 700;
            color: var(--accent-color);
        }}

        /* 表格样式 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 2em;
        }}

        th, td {{
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            text-align: left;
        }}

        th {{
            background-color: var(--table-header-bg);
            font-weight: 600;
        }}

        tr:nth-child(even) {{
            background-color: var(--code-bg);
        }}

        /* ===== 回到顶部按钮 ===== */
        .back-to-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: var(--accent-color);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s;
            z-index: 1001;
            font-size: 1.2em;
        }}

        .back-to-top.visible {{
            opacity: 1;
            visibility: visible;
        }}

        .back-to-top:hover {{
            background: var(--primary-color);
            transform: translateY(-3px);
        }}

        /* ===== 章节分页符（打印时） ===== */
        @media print {{
            .sidebar, .top-nav, .back-to-top {{
                display: none;
            }}
            .main-content {{
                margin-left: 0;
                margin-top: 0;
            }}
            .content-section {{
                page-break-after: always;
            }}
        }}

        /* 响应式 */
        @media (max-width: 768px) {{
            .sidebar {{
                display: none;
            }}
            .main-content {{
                margin-left: 0;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-nav">
        <h1>📊 {topic} 舆情分析报告</h1>
        <div class="nav-links">
            <a href="#section-1">摘要</a>
            <a href="#section-4">分析</a>
            <a href="#section-7">建议</a>
        </div>
    </nav>

    <!-- 侧边栏导航 -->
    <aside class="sidebar">
        <div class="sidebar-title">📑 报告目录</div>
        <ul class="sidebar-nav">
            <li><a href="#section-1" class="nav-link">1. 执行摘要</a></li>
            <li><a href="#section-1-1" class="nav-link sub-item">1.1 品牌声誉总览</a></li>
            <li><a href="#section-1-2" class="nav-link sub-item">1.2 关键指标</a></li>
            <li><a href="#section-2" class="nav-link">2. 品牌声量分析</a></li>
            <li><a href="#section-2-1" class="nav-link sub-item">2.1 整体趋势</a></li>
            <li><a href="#section-2-2" class="nav-link sub-item">2.2 渠道分布</a></li>
            <li><a href="#section-3" class="nav-link">3. 关键事件回顾</a></li>
            <li><a href="#section-4" class="nav-link">4. 情感与认知</a></li>
            <li><a href="#section-5" class="nav-link">5. 用户画像</a></li>
            <li><a href="#section-6" class="nav-link">6. 风险与机遇</a></li>
            <li><a href="#section-7" class="nav-link">7. 结论与建议</a></li>
            <li><a href="#section-8" class="nav-link">8. 数据附录</a></li>
        </ul>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
        <!-- 1. 执行摘要 -->
        <section id="section-1" class="content-section">
            <h1>1.0 执行摘要与核心发现</h1>

            <h2 id="section-1-1">1.1 品牌声誉总览</h2>
            <p>[详细的品牌声誉分析段落，2-3段...]</p>

            <h2 id="section-1-2">1.2 关键指标表现</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value">XX.X亿+</div>
                    <div class="kpi-label">全平台总阅读量</div>
                </div>
                <!-- 更多KPI卡片... -->
            </div>
            <p>[KPI指标的详细解读...]</p>

            <h2 id="section-1-3">1.3 主要结论与战略启示</h2>
            <ol>
                <li><strong>结论一：</strong>[详细描述...]</li>
                <li><strong>结论二：</strong>[详细描述...]</li>
            </ol>
        </section>

        <!-- 2. 品牌声量分析 -->
        <section id="section-2" class="content-section">
            <h1>2.0 品牌声量与影响力分析</h1>

            <h2 id="section-2-1">2.1 整体声量趋势</h2>
            <p>[详细的声量趋势分析...]</p>

            <h2 id="section-2-2">2.2 渠道声量分布</h2>
            <div class="highlight-box">
                <h4>平台扩散矩阵分析</h4>
                <ul>
                    <li><strong>微博：</strong>[详细分析...]</li>
                    <li><strong>抖音：</strong>[详细分析...]</li>
                </ul>
            </div>

            <h2 id="section-2-3">2.3 区域声量分布</h2>
            <p>[地域视角的详细分析...]</p>
        </section>

        <!-- 更多章节... -->

        <!-- 8. 数据附录 -->
        <section id="section-8" class="content-section">
            <h1>8.0 数据附录</h1>

            <h2 id="section-8-1">8.1 关键舆情指标汇总</h2>
            <table>
                <thead>
                    <tr>
                        <th>指标名称</th>
                        <th>数值</th>
                        <th>变化</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- 数据行... -->
                </tbody>
            </table>

            <h2 id="section-8-2">8.2 权威来源清单</h2>
            <table>
                <!-- 来源列表... -->
            </table>
        </section>
    </main>

    <!-- 回到顶部按钮 -->
    <button class="back-to-top" id="backToTop" onclick="scrollToTop()">↑</button>

    <!-- 导航交互脚本 -->
    <script>
        // 回到顶部功能
        function scrollToTop() {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }}

        // 显示/隐藏回到顶部按钮
        window.addEventListener('scroll', function() {{
            const backToTop = document.getElementById('backToTop');
            if (window.scrollY > 300) {{
                backToTop.classList.add('visible');
            }} else {{
                backToTop.classList.remove('visible');
            }}
        }});

        // 当前章节高亮
        const sections = document.querySelectorAll('.content-section, h2[id]');
        const navLinks = document.querySelectorAll('.sidebar-nav a');

        window.addEventListener('scroll', function() {{
            let current = '';
            sections.forEach(section => {{
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;
                if (scrollY >= sectionTop - 100) {{
                    current = section.getAttribute('id');
                }}
            }});

            navLinks.forEach(link => {{
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {{
                    link.classList.add('active');
                }}
            }});
        }});

        // 平滑滚动
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function(e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>
```

### 导航功能要点

1. **固定侧边栏**：左侧 280px 宽度，包含完整目录
2. **顶部快捷导航**：快速跳转到主要章节
3. **锚点链接**：每个 h1/h2 都有 id，支持直接链接
4. **当前章节高亮**：滚动时自动高亮侧边栏对应项
5. **回到顶部按钮**：滚动超过 300px 时显示
6. **平滑滚动**：点击导航链接时平滑滚动到目标位置
7. **打印优化**：打印时隐藏导航，每章节分页

### 内容要求

**每个章节（section）必须**：
- 有唯一的 id（如 section-1, section-2-1）
- scroll-margin-top 留出导航栏空间
- 包含详细分析段落（3-5段）
- 包含数据表格或图表
- 包含分析结论
"""
    return guidance



def generate_rich_word_report(
    topic: str,
    data: Dict[str, Any]
) -> str:
    """
    生成内容丰富的 Word 报告指南

    使用 docx subskill 生成图文并茂的 Word 文档
    """
    guidance = f"""
# 生成内容丰富的 Word 报告

## 报告主题: {topic}

### 使用 docx subskill 生成

```javascript
const {{ Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle,
        WidthType, ImageRun }} = require('docx');

// 创建文档
const doc = new Document({{
    styles: {{
        default: {{
            document: {{
                run: {{ font: "Arial", size: 24 }}
            }}
        }},
        paragraphStyles: [
            {{
                id: "Heading1",
                name: "Heading 1",
                basedOn: "Normal",
                next: "Normal",
                quickFormat: true,
                run: {{ size: 32, bold: true, font: "Arial" }},
                paragraph: {{ spacing: {{ before: 400, after: 200 }}, outlineLevel: 0 }}
            }},
            {{
                id: "Heading2",
                name: "Heading 2",
                basedOn: "Normal",
                next: "Normal",
                quickFormat: true,
                run: {{ size: 26, bold: true, font: "Arial" }},
                paragraph: {{ spacing: {{ before: 300, after: 150 }}, outlineLevel: 1 }}
            }}
        ]
    }},
    sections: [{{
        properties: {{
            page: {{
                size: {{ width: 12240, height: 15840 }},
                margin: {{ top: 1440, right: 1440, bottom: 1440, left: 1440 }}
            }}
        }},
        headers: {{
            default: new Header({{
                children: [new Paragraph("{topic} · 舆情分析报告")]
            }})
        }},
        footers: {{
            default: new Footer({{
                children: [new Paragraph("第 X 页")]
            }})
        }},
        children: [
            // 封面
            new Paragraph({{
                text: "舆情分析报告",
                heading: HeadingLevel.TITLE,
                alignment: AlignmentType.CENTER
            }}),
            new Paragraph({{
                text: "{topic}",
                heading: HeadingLevel.HEADING_1,
                alignment: AlignmentType.CENTER
            }}),

            // 1. 执行摘要
            new Paragraph({{
                text: "1.0 执行摘要与核心发现",
                heading: HeadingLevel.HEADING_1
            }}),
            new Paragraph({{
                text: "1.1 品牌声誉总览",
                heading: HeadingLevel.HEADING_2
            }}),
            // [详细分析段落 - 至少3段]
            new Paragraph("[第一段详细分析，解释整体声誉状况...]"),
            new Paragraph("[第二段深入分析，包括声誉变化趋势...]"),
            new Paragraph("[第三段总结核心发现...]"),

            // 1.2 关键指标
            new Paragraph({{
                text: "1.2 关键指标表现",
                heading: HeadingLevel.HEADING_2
            }}),
            // KPI表格
            new Table({{
                rows: [
                    new TableRow({{
                        children: [
                            new TableCell({{ children: [new Paragraph("指标")] }}),
                            new TableCell({{ children: [new Paragraph("数值")] }}),
                            new TableCell({{ children: [new Paragraph("变化")] }})
                        ]
                    }}),
                    // 数据行...
                ]
            }}),
            new Paragraph("[KPI指标的详细解读段落...]"),

            // 1.3 主要结论
            new Paragraph({{
                text: "1.3 主要结论与战略启示",
                heading: HeadingLevel.HEADING_2
            }}),
            new Paragraph("1. 结论一：[详细描述，包含数据支撑]"),
            new Paragraph("2. 结论二：[详细描述，包含数据支撑]"),

            // 2. 品牌声量分析
            new Paragraph({{
                text: "2.0 品牌声量与影响力分析",
                heading: HeadingLevel.HEADING_1
            }}),
            // [插入图表图片]
            new Paragraph("[图表的详细解读，解释数据波动原因...]"),

            // 3. 关键事件回顾
            new Paragraph({{
                text: "3.0 关键事件深度回顾",
                heading: HeadingLevel.HEADING_1
            }}),
            new Paragraph({{
                text: "3.1 事件一：[事件名称]",
                heading: HeadingLevel.HEADING_2
            }}),
            // 事件时间线表格
            new Table({{
                rows: [
                    new TableRow({{
                        children: [
                            new TableCell({{ children: [new Paragraph("时间")] }}),
                            new TableCell({{ children: [new Paragraph("事件")] }}),
                            new TableCell({{ children: [new Paragraph("信源")] }}),
                            new TableCell({{ children: [new Paragraph("影响")] }})
                        ]
                    }})
                ]
            }}),
            new Paragraph("[Query Engine 视角：事实梳理...]"),
            new Paragraph("[Media & Insight Engine 交叉分析...]"),

            // 更多章节...

            // 8. 数据附录
            new Paragraph({{
                text: "8.0 数据附录",
                heading: HeadingLevel.HEADING_1
            }}),
            new Paragraph({{
                text: "8.1 关键舆情指标汇总",
                heading: HeadingLevel.HEADING_2
            }}),
            // 指标汇总表
            new Table({{
                // 表格内容...
            }})
        ]
    }}]
}});

// 保存文档
Packer.toBuffer(doc).then(buffer => {{
    fs.writeFileSync("{topic}_舆情分析报告.docx", buffer);
}});
```

### 内容丰富度要求

**Word 文档必须**：
1. ✅ 包含封面、目录、8个核心章节、附录
2. ✅ 每个章节至少3-5段详细分析文字
3. ✅ 插入图表（通过 ImageRun）
4. ✅ 使用表格展示时间线、数据对比
5. ✅ 页眉显示报告标题，页脚显示页码
6. ✅ 标题层级清晰（Heading 1/2/3）

**图文并茂要求**：
- 每个图表下方必须有详细的文字解读
- 表格配合分析段落
- 关键数据用加粗突出


if __name__ == '__main__':
    print("BettaFish Report Generator")
    print("=" * 50)
    print()
    print("本模块提供使用 subskills 生成报告的指导")
    print()
    print("可用的 subskills:")
    print("  1. docx - 生成 Word 文档")
    print("  2. pdf - 生成 PDF 文档")
    print("  3. frontend-design - 生成 HTML 报告")
    print()
    print("使用方法:")
    print("  调用对应函数获取详细指导:")
    print("  - generate_word_report_guidance()")
    print("  - generate_pdf_report_guidance()")
    print("  - generate_html_report_guidance()")
    print()
    print("  准备报告数据:")
    print("  - prepare_report_data(...)")
    """
    return guidance


if __name__ == '__main__':
    print("BettaFish Report Generator")
    print("=" * 50)
    print()
    print("本模块提供使用 subskills 生成报告的指导")
    print()
    print("可用的 subskills:")
    print("  1. docx - 生成 Word 文档")
    print("  2. pdf - 生成 PDF 文档")
    print("  3. frontend-design - 生成 HTML 报告")
    print()
    print("使用方法:")
    print("  调用对应函数获取详细指导:")
    print("  - generate_word_report_guidance()")
    print("  - generate_pdf_report_guidance()")
    print("  - generate_html_report_guidance()")
    print()
    print("  准备报告数据:")
    print("  - prepare_report_data(...)")
