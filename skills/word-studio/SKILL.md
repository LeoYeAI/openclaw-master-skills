---
name: word-studio
description: Professional Word document generator. Use when user needs to create reports, papers, contracts, resumes, or any professional document. Supports docx/doc formats, charts, images, tables, TOC, and multi-language. Generates publication-ready documents. Word文档生成、专业报告、论文模板、合同制作。
version: 1.0.3
license: MIT-0
metadata: {"openclaw": {"emoji": "📄", "requires": {"bins": ["python3"]}}}
dependencies: "pip install python-docx pillow"
---

# Word Studio

Professional Word document generator that creates publication-ready documents in docx/doc formats.

## Features

- 📄 **Multi-Format**: Output as .docx or .doc
- 🎨 **Professional Templates**: 20+ document types
- 📊 **Charts & Tables**: Embedded Excel-style data
- 🖼️ **Image Support**: Insert images with professional layout
- 📑 **Auto TOC**: Generate table of contents
- 🌍 **Multi-Language**: Chinese, English, Japanese, Korean, etc.
- ✅ **WPS/Office Compatible**: Works everywhere
- 📐 **Smart Layout**: Auto-adjust for different content types

## Trigger Conditions

- "帮我写一份报告" / "Write a report for me"
- "生成Word文档" / "Generate Word document"
- "制作一份简历" / "Create a resume"
- "写论文" / "Write a paper"
- "制作标书" / "Create a bid document"
- "写工作总结" / "Write work summary"
- "生成会议纪要" / "Generate meeting minutes"
- "word-studio"

## Document Types

### Business (商务)
- 工作报告（周报/月报/年报）
- 项目计划书
- 商业计划书
- 投标书/标书
- 商务合同
- 会议纪要

### Academic (学术)
- 学术论文
- 开题报告
- 毕业论文
- 实验报告
- 文献综述
- 研究计划

### Government (公文)
- 通知公告
- 请示报告
- 函件
- 会议纪要
- 工作总结
- 调研报告

### Personal (个人)
- 中文简历
- 英文简历
- 求职信
- 自我介绍
- 个人陈述

### Legal (法律)
- 合同协议
- 授权委托书
- 法律意见书
- 起诉状
- 公证书

### Financial (财务)
- 财务报告
- 审计报告
- 预算方案
- 投资分析
- 尽职调查报告

---

## Step 1: Understand User Requirements

```
请提供以下信息：

文档类型：（报告/论文/简历/合同/其他）
文档标题：
主要内容：
格式要求：（docx/doc）
语言：（中文/英文）
特殊要求：（图表/目录/页眉页脚等）
```

---

## Step 2: Generate Document

### Python Script Template

```python
python3 << 'PYEOF'
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
import os

def create_cover_page(doc, config):
    """Create professional cover page with vertical centering"""
    
    section = doc.sections[0]
    page_height = section.page_height
    page_width = section.page_width
    
    # 创建单列表格用于垂直居中
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # 设置表格高度为页面高度（减去边距）
    table_row = table.rows[0]
    table_row.height = page_height - section.top_margin - section.bottom_margin
    
    # 获取单元格
    cell = table.cell(0, 0)
    
    # 添加标题
    title_para = cell.paragraphs[0]
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_para.add_run(config['title'])
    title_run.font.size = Pt(26)
    title_run.font.bold = True
    title_run.font.name = '黑体'
    
    # 添加空行
    cell.add_paragraph()
    
    # 添加副标题
    if 'subtitle' in config:
        subtitle_para = cell.add_paragraph()
        subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle_run = subtitle_para.add_run(config['subtitle'])
        subtitle_run.font.size = Pt(16)
        subtitle_run.font.color.rgb = RGBColor(100, 100, 100)
        subtitle_run.font.name = '宋体'
    
    # 添加空行
    cell.add_paragraph()
    cell.add_paragraph()
    
    # 添加作者信息
    if 'author' in config:
        author_para = cell.add_paragraph()
        author_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        author_run = author_para.add_run(config['author'])
        author_run.font.size = Pt(14)
        author_run.font.name = '宋体'
    
    # 添加空行
    cell.add_paragraph()
    
    # 添加日期
    from datetime import datetime
    date_para = cell.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_run = date_para.add_run(datetime.now().strftime("%Y年%m月%d日"))
    date_run.font.size = Pt(14)
    date_run.font.name = '宋体'
    
    # 隐藏表格边框
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    borders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'none')
        border.set(qn('w:sz'), '0')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), 'auto')
        borders.append(border)
    tblPr.append(borders)
    
    return doc
    
    # 添加目录占位符
    if config.get('toc', False):
        toc_heading = doc.add_heading('目录', level=1)
        toc_para = doc.add_paragraph('（请在Word中右键此处，选择"更新域"生成目录）')
        doc.add_page_break()
    
    # 添加正文内容
    for section_data in config.get('sections', []):
        # 添加章节标题
        doc.add_heading(section_data['title'], level=1)
        
        # 添加段落内容
        for para in section_data.get('paragraphs', []):
            p = doc.add_paragraph(para)
            p.paragraph_format.first_line_indent = Cm(0.74)  # 首行缩进2字符
            p.paragraph_format.line_spacing = 1.5  # 1.5倍行距
        
        # 添加表格（如有）
        if 'table' in section_data:
            table_data = section_data['table']
            table = doc.add_table(rows=len(table_data), cols=len(table_data[0]))
            table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            for i, row_data in enumerate(table_data):
                for j, cell_text in enumerate(row_data):
                    table.cell(i, j).text = str(cell_text)
        
        # 添加图片（如有）
        if 'image' in section_data:
            img_path = section_data['image']
            if os.path.exists(img_path):
                doc.add_picture(img_path, width=Inches(5))
                last_paragraph = doc.paragraphs[-1]
                last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 添加图表（如有）
        if 'chart' in section_data:
            chart_info = section_data['chart']
            doc.add_paragraph(f"【图表：{chart_info['title']}】")
    
    # 添加页眉页脚
    if config.get('header', False):
        header = section.header
        header_para = header.paragraphs[0]
        header_para.text = config.get('header_text', '')
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    if config.get('footer', False):
        footer = section.footer
        footer_para = footer.paragraphs[0]
        footer_para.text = config.get('footer_text', '')
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    return doc

def save_document(doc, output_path, format='docx'):
    """Save document in specified format"""
    
    if format == 'doc':
        # docx转doc需要LibreOffice
        docx_path = output_path.replace('.doc', '.docx')
        doc.save(docx_path)
        
        # 尝试使用LibreOffice转换
        import subprocess
        try:
            subprocess.run([
                'soffice', '--headless', '--convert-to', 'doc',
                '--outdir', os.path.dirname(output_path),
                docx_path
            ], check=True, timeout=30)
            os.remove(docx_path)  # 删除临时docx
            return output_path
        except:
            # 如果LibreOffice不可用，返回docx
            final_path = output_path.replace('.doc', '.docx')
            os.rename(docx_path, final_path)
            return final_path
    else:
        doc.save(output_path)
        return output_path

# 示例配置
config = {
    'title': '示例文档标题',
    'subtitle': '副标题',
    'author': '作者姓名',
    'toc': True,
    'header': True,
    'header_text': '公司名称',
    'footer': True,
    'footer_text': '第 {PAGE} 页',
    'sections': [
        {
            'title': '第一章 引言',
            'paragraphs': [
                '这是第一段内容，需要首行缩进两个字符。',
                '这是第二段内容，继续阐述相关内容。'
            ]
        },
        {
            'title': '第二章 数据分析',
            'paragraphs': ['本章展示相关数据。'],
            'table': [
                ['项目', 'Q1', 'Q2', 'Q3', 'Q4'],
                ['销售额', '100', '150', '200', '250'],
                ['增长率', '10%', '50%', '33%', '25%']
            ]
        }
    ]
}

# 生成文档
output_dir = os.environ.get('OPENCLAW_WORKSPACE', os.getcwd())
output_path = os.path.join(output_dir, 'document.docx')

doc = create_document(config)
final_path = save_document(doc, output_path, 'docx')

print(f"✅ 文档已生成：{final_path}")
PYEOF
```

---

## Template Library

### 1. 工作报告模板

```python
WORK_REPORT = {
    'title': '2026年度工作总结报告',
    'toc': True,
    'header': True,
    'header_text': 'XX公司',
    'sections': [
        {'title': '一、工作概述', 'paragraphs': [...]},
        {'title': '二、主要工作内容', 'paragraphs': [...]},
        {'title': '三、工作成果', 'paragraphs': [...]},
        {'title': '四、存在问题', 'paragraphs': [...]},
        {'title': '五、下一步计划', 'paragraphs': [...]},
    ]
}
```

### 2. 学术论文模板

```python
ACADEMIC_PAPER = {
    'title': '论文标题',
    'author': '作者姓名',
    'toc': True,
    'sections': [
        {'title': '摘要', 'paragraphs': [...]},
        {'title': '关键词', 'paragraphs': [...]},
        {'title': '1 引言', 'paragraphs': [...]},
        {'title': '2 文献综述', 'paragraphs': [...]},
        {'title': '3 研究方法', 'paragraphs': [...]},
        {'title': '4 结果与分析', 'paragraphs': [...]},
        {'title': '5 结论', 'paragraphs': [...]},
        {'title': '参考文献', 'paragraphs': [...]},
    ]
}
```

### 3. 商务合同模板

```python
CONTRACT = {
    'title': '商务合同',
    'sections': [
        {'title': '第一条 合同双方', 'paragraphs': [...]},
        {'title': '第二条 合同标的', 'paragraphs': [...]},
        {'title': '第三条 价格与支付', 'paragraphs': [...]},
        {'title': '第四条 交付与验收', 'paragraphs': [...]},
        {'title': '第五条 违约责任', 'paragraphs': [...]},
        {'title': '第六条 争议解决', 'paragraphs': [...]},
    ]
}
```

### 4. 简历模板

```python
RESUME = {
    'title': '个人简历',
    'sections': [
        {'title': '基本信息', 'paragraphs': [...]},
        {'title': '教育背景', 'paragraphs': [...]},
        {'title': '工作经历', 'paragraphs': [...]},
        {'title': '项目经验', 'paragraphs': [...]},
        {'title': '技能证书', 'paragraphs': [...]},
        {'title': '自我评价', 'paragraphs': [...]},
    ]
}
```

---

## Font Configuration

### Cross-Platform Font Strategy (跨平台字体策略)

**优先使用开源免费字体，确保跨平台一致性：**

| 字体名称 | 类型 | 语言 | 许可证 |
|----------|------|------|--------|
| **Noto Sans** | 无衬线 | 全语言 | OFL (免费) |
| **Noto Serif** | 衬线 | 全语言 | OFL (免费) |
| **Noto Sans SC** | 无衬线 | 简体中文 | OFL (免费) |
| **Noto Serif SC** | 衬线 | 简体中文 | OFL (免费) |
| **Source Han Sans** | 无衬线 | 中日韩 | OFL (免费) |
| **Source Han Serif** | 衬线 | 中日韩 | OFL (免费) |
| **Liberation Sans** | 无衬线 | 拉丁 | OFL (免费) |
| **Liberation Serif** | 衬线 | 拉丁 | OFL (免费) |

### Platform Font Mapping (平台字体映射)

```python
def get_platform_fonts(platform, language):
    """Get fonts based on platform and language"""
    
    # 开源字体（首选，跨平台一致）
    OPEN_SOURCE_FONTS = {
        'body': {
            'zh': 'Noto Serif SC',
            'en': 'Liberation Serif',
            'ja': 'Noto Serif JP',
            'ko': 'Noto Serif KR',
            'default': 'Noto Serif'
        },
        'heading': {
            'zh': 'Noto Sans SC',
            'en': 'Liberation Sans',
            'ja': 'Noto Sans JP',
            'ko': 'Noto Sans KR',
            'default': 'Noto Sans'
        }
    }
    
    # 系统字体（回退方案）
    SYSTEM_FONTS = {
        'windows': {
            'body': {'zh': '宋体', 'en': 'Times New Roman'},
            'heading': {'zh': '黑体', 'en': 'Arial'}
        },
        'macos': {
            'body': {'zh': 'STSong', 'en': 'Times New Roman'},
            'heading': {'zh': 'STHeiti', 'en': 'Helvetica'}
        },
        'linux': {
            'body': {'zh': 'Noto Serif CJK SC', 'en': 'Liberation Serif'},
            'heading': {'zh': 'Noto Sans CJK SC', 'en': 'Liberation Sans'}
        }
    }
    
    # 优先使用开源字体
    body_font = OPEN_SOURCE_FONTS['body'].get(language, 
                 OPEN_SOURCE_FONTS['body']['default'])
    heading_font = OPEN_SOURCE_FONTS['heading'].get(language,
                   OPEN_SOURCE_FONTS['heading']['default'])
    
    return {
        'body': body_font,
        'heading': heading_font,
        'fallback': SYSTEM_FONTS.get(platform, SYSTEM_FONTS['linux'])
    }
```

### Font Installation Check

```python
def check_font_availability(font_name):
    """Check if font is available on system"""
    import subprocess
    import sys
    
    platform = sys.platform
    
    if platform == 'darwin':  # macOS
        result = subprocess.run(['fc-list', font_name], 
                              capture_output=True, text=True)
        return result.returncode == 0
    elif platform == 'win32':  # Windows
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts")
            return True
        except:
            return False
    else:  # Linux
        result = subprocess.run(['fc-list', f':family={font_name}'],
                              capture_output=True, text=True)
        return font_name in result.stdout

def get_available_font(preferred, fallbacks):
    """Get first available font from list"""
    for font in [preferred] + fallbacks:
        if check_font_availability(font):
            return font
    return 'serif'  # Ultimate fallback
```

---

## Compatibility

### WPS/Office Compatibility

```
✅ 使用标准OOXML格式
✅ 避免使用Office特有功能
✅ 图片嵌入而非链接
✅ 字体嵌入或回退机制
✅ 表格使用标准样式
```

### Format Support

| 格式 | 支持 | 说明 |
|------|------|------|
| .docx | ✅ | 主要格式 |
| .doc | ⚠️ | 需要LibreOffice转换 |
| .pdf | ⚠️ | 需要额外转换 |
| .odt | ⚠️ | 需要额外转换 |

---

## Error Handling

```
字体缺失       → 使用系统默认字体
图片不存在     → 跳过图片，添加占位符
格式转换失败   → 保留docx格式
内容为空       → 添加占位文本
```

---

## Image Layout (图片排版)

### Image Layout Modes (图片排版模式)

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **居中** | 图片水平居中 | 单独展示的图片 |
| **左对齐** | 图片靠左，文字环绕 | 图文混排 |
| **右对齐** | 图片靠右，文字环绕 | 图文混排 |
| **全宽** | 图片占满页面宽度 | 大图展示 |
| **并排** | 多张图片并排 | 对比展示 |

### Image Size Standards (图片尺寸标准)

```python
IMAGE_SIZES = {
    'full_width': Inches(6.0),      # 全宽（A4减边距）
    'half_width': Inches(3.0),      # 半宽
    'third_width': Inches(2.0),     # 三分之一宽
    'quarter_width': Inches(1.5),   # 四分之一宽
    'thumbnail': Inches(1.0),       # 缩略图
}
```

### Image Insertion Code (图片插入代码)

```python
from docx.shared import Inches, Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def add_image_centered(doc, image_path, width=None, caption=None):
    """Add centered image with optional caption"""
    
    # 添加图片
    if width:
        pic = doc.add_picture(image_path, width=width)
    else:
        pic = doc.add_picture(image_path)
    
    # 居中对齐
    last_paragraph = doc.paragraphs[-1]
    last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 添加图注
    if caption:
        caption_para = doc.add_paragraph()
        caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption_run = caption_para.add_run(caption)
        caption_run.font.size = Pt(10)
        caption_run.font.color.rgb = RGBColor(128, 128, 128)
    
    return pic

def add_image_with_text_wrap(doc, image_path, position='left', width=Inches(2.5)):
    """Add image with text wrapping"""
    
    # 使用表格实现文字环绕效果
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    if position == 'left':
        img_cell = table.cell(0, 0)
        text_cell = table.cell(0, 1)
    else:
        img_cell = table.cell(0, 1)
        text_cell = table.cell(0, 0)
    
    # 添加图片到单元格
    img_cell.paragraphs[0].add_run().add_picture(image_path, width=width)
    img_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 隐藏表格边框
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    borders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'none')
        border.set(qn('w:sz'), '0')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), 'auto')
        borders.append(border)
    tblPr.append(borders)
    
    return table, text_cell

def add_images_side_by_side(doc, image_paths, width=Inches(2.8)):
    """Add multiple images side by side"""
    
    # 创建表格并排显示图片
    table = doc.add_table(rows=1, cols=len(image_paths))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    for i, img_path in enumerate(image_paths):
        cell = table.cell(0, i)
        cell.paragraphs[0].add_run().add_picture(img_path, width=width)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 隐藏表格边框
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    borders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'none')
        border.set(qn('w:sz'), '0')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), 'auto')
        borders.append(border)
    tblPr.append(borders)
    
    return table

def add_image_full_width(doc, image_path):
    """Add image that spans full page width"""
    
    # 获取页面宽度
    section = doc.sections[0]
    page_width = section.page_width
    left_margin = section.left_margin
    right_margin = section.right_margin
    
    # 计算可用宽度
    available_width = page_width - left_margin - right_margin
    
    # 添加图片
    pic = doc.add_picture(image_path, width=available_width)
    
    # 居中对齐
    last_paragraph = doc.paragraphs[-1]
    last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    return pic
```

### Image Caption Format (图注格式)

```python
def add_figure_caption(doc, figure_number, caption_text, position='below'):
    """Add formatted figure caption"""
    
    caption = f"图 {figure_number}  {caption_text}"
    
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    run = para.add_run(caption)
    run.font.size = Pt(10)
    run.font.name = '宋体'
    
    return para
```

---

## Usage Examples

### 生成工作报告

```
User: "帮我写一份2026年第一季度工作总结"

Agent:
1. 收集用户工作内容
2. 搜索相关数据
3. 使用工作模板生成结构
4. 调用word-studio生成文档
5. 输出专业Word文件
```

### 生成学术论文

```
User: "帮我写一篇关于AI发展趋势的论文"

Agent:
1. 搜索最新研究数据
2. 整理论文结构
3. 生成符合学术规范的格式
4. 插入图表和参考文献
5. 输出可提交的论文
```

---

## Notes

- 生成时间取决于文档复杂度
- 首次运行需要安装python-docx
- 建议使用docx格式以获得最佳兼容性
- 复杂文档建议分章节生成
