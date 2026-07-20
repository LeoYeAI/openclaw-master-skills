# 技能整合指南

本指南详细说明如何使用 consulting-analysis 技能时，调用其他辅助技能完成数据收集和多格式输出。

---

## 1. 数据收集技能调用

### 1.1 deep-research-pro（深度研究）

**适用场景**：
- 需要深度背景调研
- 文献综述
- 学术研究
- 复杂主题的全面分析

**调用方式**：

```bash
# 假设 deep-research-pro 脚本路径
cd ~/.workbuddy/skills/deep-research-pro/scripts

# 执行深度研究
python research.py \
    --topic "中国护肤品市场规模 2024" \
    --max-sources 10 \
    --output /tmp/deep_research_result.json

# 或者直接使用其搜索功能
bash ddg-search.sh "skincare market size China growth rate" --max 8
```

**输出格式**：
```json
{
  "topic": "中国护肤品市场规模 2024",
  "sources": [
    {
      "title": "2024年中国护肤品行业报告",
      "url": "https://example.com/report",
      "snippet": "市场规模达到3450亿元...",
      "source": "艾瑞咨询"
    }
  ],
  "key_findings": [
    "市场规模年增长率8.5%",
    "线上渠道占比超过60%"
  ]
}
```

---

### 1.2 multi-search-engine（多引擎搜索）

**适用场景**：
- 中文市场数据（百度、微信、头条）
- 国际市场对比（Google、Bing）
- 特定平台搜索（官网、论坛）
- 多语言搜索

**调用方式**：

```bash
# 百度搜索（中文）
web_fetch "https://www.baidu.com/s?wd=护肤+市场规模+2024"

# 微信公众号文章
web_fetch "https://wx.sogou.com/weixin?type=2&query=护肤行业趋势"

# 今日头条新闻
web_fetch "https://so.toutiao.com/search?keyword=护肤品消费报告"

# Google 搜索（国际）
web_fetch "https://www.google.com/search?q=global+skincare+market+2024"

# 站内搜索（特定网站）
web_fetch "https://www.google.com/search?q=site:iresearch.cn+护肤+市场"
```

**高级搜索技巧**：

| 技巧 | 示例 | 说明 |
|------|------|------|
| 时间过滤 | `&tbs=qdr:w` | 过去一周 |
| 文件类型 | `filetype:pdf` | 搜索 PDF 文件 |
| 精确匹配 | `"护肤市场"` | 完全匹配短语 |
| 排除词 | `护肤品 -化妆品` | 排除化妆品 |

---

### 1.3 ddg-web-search（快速搜索）

**适用场景**：
- 快速补充搜索
- 备选搜索方案
- 简单查询
- 无 API 密钥限制

**调用方式**：

```bash
# DuckDuckGo Lite 搜索
web_fetch \
    "https://lite.duckduckgo.com/lite/?q=skincare+market+size+2024" \
    --maxChars 8000

# 区域过滤（美国）
web_fetch \
    "https://lite.duckduckgo.com/lite/?q=best+coffee+melbourne&kl=us-en" \
    --maxChars 8000
```

**结果解析**：
```
1. 2024 Skincare Market Report - Industry Analysis
   The global skincare market reached $180 billion in 2024...
   https://example.com/report

2. Top 10 Skincare Brands
   A comprehensive analysis of leading brands...
   https://example.com/brands
```

---

### 1.4 pdf（PDF数据提取）

**适用场景**：
- 提取上市公司财报数据
- 政府统计数据
- 行业研究报告
- 学术论文数据

**调用方式**：

#### 文本提取

```python
import pdfplumber

# 提取全文
with pdfplumber.open("report.pdf") as pdf:
    full_text = ""
    for page in pdf.pages:
        full_text += page.extract_text() + "\n"
    print(full_text)
```

#### 表格提取

```python
import pdfplumber
import pandas as pd

# 提取所有表格
with pdfplumber.open("annual_report.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # 检查表格不为空
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# 合并表格
combined_df = pd.concat(all_tables, ignore_index=True)
combined_df.to_excel("extracted_tables.xlsx", index=False)
```

#### 特定页面提取

```python
# 提取特定页面的表格
with pdfplumber.open("report.pdf") as pdf:
    # 提取第5页的表格
    page_5 = pdf.pages[4]
    table = page_5.extract_table()
    print(table)
```

---

## 2. 热点趋势数据（insights-hotspot）

**适用场景**：
- 市场动态追踪
- 行业热点分析
- 最新趋势研究
- 新闻舆情分析

**调用方式**：

```bash
cd ~/.workbuddy/skills/insights-hotspot/scripts

# 生成热点洞察报告
python insights_generator.py \
    --directions 1,2,3,4 \
    --days 2 \
    --top 10 \
    --formats html,markdown,word \
    --search-results search_results.json
```

**输出内容**：
- 全球AI发展洞察
- 全球SaaS洞察
- AI营销运作转型洞察
- AI产品岗转型洞察
- 自定义方向洞察

---

## 3. 输出格式转换

### 3.1 Word 文档（docx）

**调用方式**：

```bash
cd ~/.workbuddy/skills/docx/scripts

# 从 Markdown 生成 Word
python generate_from_markdown.py \
    --input report.md \
    --output report.docx \
    --template consulting-template.docx
```

**手动创建**：

```python
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

# 创建文档
doc = Document()

# 添加标题
title = doc.add_heading('Z世代护肤市场分析报告', 0)

# 添加段落
doc.add_paragraph('这是报告摘要...')

# 添加表格
table = doc.add_table(rows=3, cols=3)
table.style = 'Table Grid'

# 添加图片
doc.add_picture('chart.png', width=Inches(5))

# 保存
doc.save('report.docx')
```

---

### 3.2 PPT 演示文稿（pptx）

**调用方式**：

```bash
cd ~/.workbuddy/skills/pptx/scripts

# 从 Markdown 生成 PPT
python generate_from_markdown.py \
    --input report.md \
    --output report.pptx \
    --template consulting-template.pptx
```

**手动创建**：

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# 创建演示文稿
prs = Presentation()

# 添加标题页
title_slide = prs.slides.add_slide(prs.slide_layouts[0])
title = title_slide.shapes.title
subtitle = title_slide.placeholders[1]

title.text = "Z世代护肤市场分析报告"
subtitle.text = "2024年度报告"

# 添加内容页
bullet_slide = prs.slides.add_slide(prs.slide_layouts[1])
shapes = bullet_slide.shapes

title_shape = shapes.title
body_shape = shapes.placeholders[1]

title_shape.text = "市场规模与增长趋势"

tf = body_shape.text_frame
tf.text = "市场规模达到3450亿元"
p = tf.add_paragraph()
p.text = "年增长率8.5%"
p.level = 1

# 添加图片
left = top = Inches(1)
height = Inches(4)
pic = slide.shapes.add_picture(
    'chart.png', left, top, height=height
)

# 保存
prs.save('report.pptx')
```

**PPT 设计建议**：

| 元素 | 建议 |
|------|------|
| 幻灯片数量 | 15-25张 |
| 每章幻灯片 | 3-5张 |
| 标题页 | 1张 |
| Abstract | 1张 |
| Conclusion | 1张 |
| 配色 | Midnight Executive / Forest & Moss / Coral Energy |
| 字体 | Georgia + Calibri（或类似组合） |
| 图表占比 | 每页至少一个视觉元素 |

---

## 4. 完整工作流示例

### 场景：生成 Z 世代护肤市场分析报告（全格式）

```bash
# 步骤1：生成分析框架（consulting-analysis）
# （由 AI 自动完成）

# 步骤2：数据收集（多技能并行）

# 2.1 使用 multi-search-engine 搜索中文数据
web_fetch "https://www.baidu.com/s?wd=Z世代+护肤+市场规模+2024"
web_fetch "https://wx.sogou.com/weixin?type=2&query=Z世代护肤消费"

# 2.2 使用 deep-research-pro 深度研究
cd ~/.workbuddy/skills/deep-research-pro/scripts
python research.py --topic "Gen-Z skincare market global" --max 10

# 2.3 使用 pdf 提取财报数据
python ~/.workbuddy/skills/pdf/scripts/extract_tables.py \
    annual_report.pdf --output financial_data.json

# 2.4 使用 insights-hotspot 获取热点
cd ~/.workbuddy/skills/insights-hotspot/scripts
python insights_generator.py \
    --directions 5 \
    --days 7 \
    --top 10 \
    --custom "Z世代护肤趋势" \
    --formats json

# 步骤3：生成 Markdown 报告（consulting-analysis）
# （由 AI 自动完成）

# 步骤4：转换为其他格式

# 4.1 生成 Word 文档
cd ~/.workbuddy/skills/docx/scripts
python generate_from_markdown.py \
    --input z-gen-skincare-report.md \
    --output z-gen-skincare-report.docx

# 4.2 生成 PPT 演示文稿
cd ~/.workbuddy/skills/pptx/scripts
python generate_from_markdown.py \
    --input z-gen-skincare-report.md \
    --output z-gen-skincare-report.pptx

# 步骤5：质量检查
python markitdown z-gen-skincare-report.docx
python markitdown z-gen-skincare-report.pptx

# 最终输出
# - z-gen-skincare-report.md
# - z-gen-skincare-report.docx
# - z-gen-skincare-report.pptx
```

---

## 5. 技能依赖检查脚本

```bash
#!/bin/bash
# check_dependencies.sh - 检查 consulting-analysis 依赖技能

SKILLS_DIR="$HOME/.workbuddy/skills"

echo "Checking consulting-analysis dependencies..."

# 必需技能
REQUIRED_SKILLS=(
    "deep-research-pro"
    "multi-search-engine"
    "ddg-web-search"
    "pdf"
    "docx"
    "pptx"
)

# 可选技能
OPTIONAL_SKILLS=(
    "insights-hotspot"
)

missing_required=()
missing_optional=()

# 检查必需技能
for skill in "${REQUIRED_SKILLS[@]}"; do
    if [ ! -d "$SKILLS_DIR/$skill" ]; then
        missing_required+=("$skill")
    else
        echo "✓ $skill"
    fi
done

# 检查可选技能
for skill in "${OPTIONAL_SKILLS[@]}"; do
    if [ ! -d "$SKILLS_DIR/$skill" ]; then
        missing_optional+=("$skill")
    else
        echo "○ $skill (optional)"
    fi
done

# 输出结果
if [ ${#missing_required[@]} -eq 0 ]; then
    echo ""
    echo "✓ All required skills are installed!"
else
    echo ""
    echo "✗ Missing required skills:"
    for skill in "${missing_required[@]}"; do
        echo "  - $skill"
    done
    echo ""
    echo "Please install missing skills before using consulting-analysis."
fi

if [ ${#missing_optional[@]} -gt 0 ]; then
    echo ""
    echo "Missing optional skills:"
    for skill in "${missing_optional[@]}"; do
        echo "  - $skill"
    done
    echo ""
    echo "These skills are optional but recommended for enhanced functionality."
fi
```

---

## 6. 故障排除

### 问题：搜索无结果

**可能原因**：
1. 网络连接问题
2. 搜索关键词不准确
3. 搜索引擎限制

**解决方案**：
```bash
# 尝试多个搜索源
web_fetch "https://www.baidu.com/s?wd=护肤市场"          # 百度
web_fetch "https://www.google.com/search?q=skincare"      # Google
web_fetch "https://lite.duckduckgo.com/lite/?q=skincare"  # DDG

# 调整关键词
web_fetch "https://www.baidu.com/s?wd=护肤品+行业+报告+2024"
```

### 问题：PDF 提取失败

**可能原因**：
1. PDF 是扫描图片（需要 OCR）
2. PDF 加密
3. 表格格式复杂

**解决方案**：
```python
# 1. 检查 PDF 是否加密
from pypdf import PdfReader
reader = PdfReader("report.pdf")
if reader.is_encrypted:
    reader.decrypt("password")

# 2. 如果是扫描 PDF，使用 OCR
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path('scanned.pdf')
for i, image in enumerate(images):
    text = pytesseract.image_to_string(image)
    print(f"Page {i+1}: {text}")

# 3. 调整表格提取参数
table = page.extract_table({
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
})
```

### 问题：格式转换失败

**可能原因**：
1. Markdown 格式错误
2. 依赖包缺失
3. 模板文件缺失

**解决方案**：
```bash
# 检查依赖
pip list | grep -E "python-docx|python-pptx"

# 重新安装
pip install --upgrade python-docx python-pptx

# 检查 Markdown 格式
python -m markdown report.md > test.html

# 使用基础模板（不指定模板）
python generate_from_markdown.py \
    --input report.md \
    --output report.docx
```

---

## 7. 最佳实践

### 数据收集策略

1. **混合搜索**：
   - 中文数据：优先 multi-search-engine（百度、微信）
   - 国际数据：优先 deep-research-pro + Google
   - 快速补充：ddg-web-search

2. **多源验证**：
   - 关键数据至少从2个来源验证
   - 标注数据可信度（high/medium/low）
   - 明确标注数据时间范围

3. **时间控制**：
   - 市场数据：最近1-3年
   - 财报数据：最新财报
   - 热点趋势：最近7天

### 报告生成策略

1. **格式选择**：
   - 快速分享：Markdown
   - 正式交付：Word
   - 演示汇报：PPT
   - 重要项目：全部生成

2. **内容一致性**：
   - 所有格式应保持内容一致
   - PPT 精简版，保持核心观点
   - Word 完整版，保留所有细节

3. **质量检查**：
   - 生成后立即检查所有格式
   - 重点关注数据准确性和格式一致性
   - 使用 markitdown 验证生成的 Word/PPT

---

## 8. 参考资料

- **consulting-analysis**: 主技能文档
- **deep-research-pro**: 深度研究技能
- **multi-search-engine**: 多引擎搜索技能
- **pdf**: PDF 处理技能
- **docx**: Word 文档技能
- **pptx**: PPT 演示文稿技能
- **insights-hotspot**: 热点洞察技能
