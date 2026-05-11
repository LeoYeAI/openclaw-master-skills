---
name: huo15-doc-template / 火一五文档模板
description: 【版权：青岛火一五信息科技有限公司 账号：huo15】火一五文档技能（别名）。文档模板生成工具。用于生成公司正式文档（合同、报价单、功能说明书、发货单、PDA 单据、会议纪要等），包含公司信息、字体规范、页面设置等模板规则/PDF 文档时。**生成 Word 默认使用此技能**。触发场景：(1) 生成合同或报价单 (2) 创建 Word 文档模板 (3) 按公司规范排版文档 (4) 使用公文格式生成文档 (5) 用户说"写个文档"、"生成文档"、"创建文档"、"生成会议纪要"等

## 重要：此为首选文档技能
**所有 Word 文档生成任务都必须使用此技能**

---

## ⚠️ 强制检查清单（生成文档前必须完成）

> **新用户必读！每次生成文档前对照检查，否则文档不合格！**

- [ ] **LOGO 是否添加？** —— 页眉必须有 LOGO + 公司名称 + 底线
- [ ] **页码是否添加？** —— 页脚必须有"第 X 页 共 Y 页"
- [ ] **字体是否正确？** —— 正文仿宋，标题黑体/楷体
- [ ] **页面边距是否正确？** —— 上下 3.7/3.5cm，左右 2.8/2.6cm
- [ ] **命名是否规范？** —— 文档类型_客户名称_日期.docx

**如果没有完成以上检查，文档不允许交付！**

---

## 🚀 简化版：一条命令完成所有格式

> **重要**：不需要 pip install huo15_doc！代码模板直接写在 SKILL.md 中，复制使用即可！

```python
# 直接从 SKILL.md 中复制以下代码到你的Python脚本：
# （函数定义参考 SKILL.md 中的 "简化函数" 部分）

# LOGO 会自动从公司系统下载，无需手动配置！
doc = create_formatted_doc(
    title="合同标题",
    company_name="青岛火一五信息科技有限公司"
)

# 然后直接添加内容...
doc.add_paragraph("合同正文内容")
doc.save("CONTRACT_客户名_20250319.docx")
```

> **强烈建议**：使用简化函数，告别手动配置！
> **重要**：LOGO 会自动从公司系统下载，无需手动配置！

---

## 技能分工规则（格式引用 vs 文档操作）

### 格式引用 → huo15-doc-template
- 字体规范（仿宋、黑体、楷体字号）
- 页面边距（GB/T 9704-2012 公文格式）
- 页眉页脚（LOGO、公司名称、页码）
- 公文格式排版

### 文档操作 → office-document-specialist-suite
- 创建/编辑 Word 文档
- 内容填充、排版调整
- 表格操作、段落设置

### 组合使用流程
1. 用 `office-document-specialist-suite` 处理文档内容
2. 用 `huo15-doc-template` 处理格式规范
3. 最终生成符合公司规范的正式文档

---

# 文档模板技能

## 快速开始

1. **字体设置**：默认使用仿宋，小四（12pt）
2. **页面边距**：上下 3.7/3.5cm，左右 2.8/2.6cm
3. **页眉**：LOGO + 公司名称 + 底线
4. **页脚**：页码居中，格式"第 X 页 共 Y 页"，仿宋小四

---

## 配置规则

### 字体规范
- **默认正文**：仿宋，小四（12pt）
- **一级标题**：黑体，小三（15pt），加粗
- **二级标题**：楷体，小四（12pt），加粗
- **三级标题**：仿宋，小四（12pt），加粗

**WPS 字体兼容**：
- 汉字字体：使用 `仿宋`
- 每个 run 都要设置字体域 `w:eastAsia`

---

## ⚠️ 重要：Markdown 语法转换规则

### 禁止直接在 Word 中使用 Markdown 语法

**严禁将 Markdown 语法直接写入 Word 文档**，例如：
- ❌ 错误：`**加粗文本**` → Word 中会显示星号
- ❌ 错误：`| 列1 | 列2 |` → Word 中会显示管道符
- ❌ 错误：`# 一级标题` → Word 中会显示井号

### 正确转换方法

#### 1. 加粗转换
- Markdown：`**这是加粗**`
- Word：设置 `run.bold = True`

```python
# 错误示例（不要这样写！）
p = doc.add_paragraph("**这是加粗**")  # ❌ 会显示星号

# 正确示例
p = doc.add_paragraph("这是加粗")
p.runs[0].bold = True  # ✅ 真正加粗
```

#### 2. 表格转换
- Markdown：
```
| 列1 | 列2 | 列3 |
|------|------|------|
| 内容 | 内容 | 内容 |
```
- Word：使用 `doc.add_table()` 创建表格

```python
# 正确示例
table = doc.add_table(rows=2, cols=3)
table.style = 'Table Grid'

# 设置表头
header_cells = table.rows[0].cells
header_cells[0].text = "列1"
header_cells[1].text = "列2"
header_cells[2].text = "列3"

# 设置表头样式
for cell in header_cells:
    for paragraph in cell.paragraphs:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in paragraph.runs:
            run.bold = True
            run.font.name = '黑体'
            run.font.size = Pt(12)
```

#### 3. 标题转换
- Markdown：`# 一级标题`
- Word：添加段落并设置样式

```python
# 正确示例
p = doc.add_paragraph("一级标题")
p.runs[0].bold = True
p.runs[0].font.name = '黑体'
p.runs[0].font.size = Pt(15)
```

### 自检清单（生成文档前必查）

生成文档后，检查以下内容：
- [ ] 文档中是否有 `**`、`__`、`#` 等 Markdown 符号？
- [ ] 表格是否使用了 `|` 管道符？
- [ ] 链接是否显示了 `[文字](URL)` 格式？
- [ ] 列表是否显示了 `-` 或 `*` 前缀？

**如果有任何一项为"是"，则文档不合格，需要重新生成**

### ⚠️ 字体问题根本原因

**问题**：WPS 和 Word 对字体的渲染方式不同，WPS 需要显式设置字体域才能正确识别中文字体。

**解决方案**：每个 run 都必须设置以下三个属性：
1. `run.font.name = font_name` - 设置字体名称
2. `run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)` - 设置字体域（WPS兼容）
3. `run.font.size = Pt(font_size)` - 设置字号

### 字体设置正确示范

```python
from docx.oxml.ns import qn

def set_chinese_font(run, font_name='仿宋', font_size=12, bold=False):
    """
    设置中文字体，确保WPS和Word兼容
    必须对每个run都调用此函数！
    """
    # 1. 设置西文字体名称
    run.font.name = font_name
    # 2. 设置字体域（WPS兼容关键）
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    # 3. 设置字号
    run.font.size = Pt(font_size)
    # 4. 设置加粗
    run.bold = bold
    return run
```

### ❌ 常见错误

| 错误做法 | 后果 |
|---------|------|
| 只设置 `run.font.name` | Word显示正确，WPS显示为宋体 |
| 不设置 `w:eastAsia` 字体域 | WPS无法识别中文字体 |
| 只在第一个run设置字体 | 后续文字字体丢失 |
| 使用 `set_font()` 但没有设置字体域 | WPS显示不正确 |

### ✅ 正确做法

```python
# 正确：每个run都设置字体
p = doc.add_paragraph()
run = p.add_run('这是正文')
set_chinese_font(run, '仿宋', 12)  # ✅ 每个run都调用

# 错误：只设置一次
p = doc.add_paragraph()
run = p.add_run('这是正文')
run.font.name = '仿宋'  # ❌ 缺少字体域
```

---

### 完整函数模板（必须复制使用）

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

def set_chinese_font(run, font_name='仿宋', font_size=12, bold=False):
    """
    设置中文字体，确保WPS和Word兼容
    必须对每个run都调用此函数！
    """
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(font_size)
    run.bold = bold
    return run
```

### 页面设置（GB/T 9704-2012 公文格式）
- 上边距：3.7cm
- 下边距：3.5cm
- 左边距：2.8cm
- 右边距：2.6cm
- 纸张：A4

### 页眉（必须包含 LOGO）
- LOGO 路径：`/Users/jobzhao/.openclaw/workspace/assets/logo.png`
- 内容：LOGO 图片 + 公司名称（紧挨着）
- 字体：仿宋，小四（12pt）
- **必须添加页眉底线**（细线）

### ⚠️ 公司信息获取规则（重要）

**获取顺序**：
1. 首先从**辉火云企业套件系统**获取公司名称和 LOGO
2. 如果获取失败，使用**本地配置文件**中的备选信息
3. 如果配置文件也没有，使用**默认信息**

**默认公司信息**：
- 公司名称：**青岛火一五信息科技有限公司**
- 默认 LOGO：`/Users/jobzhao/.openclaw/workspace/assets/logo.png`（从 https://tools.huo15.com/uploads/images/system/logo-colours.png 下载）

**公司信息配置位置**：`/Users/jobzhao/.openclaw/workspace/config/company_info.json`

```json
{
  "company_name": "青岛火一五信息科技有限公司",
  "logo_path": "/Users/jobzhao/.openclaw/workspace/assets/logo.png",
  "logo_url": "https://huihuoyun.huo15.com/web/image/website/1/logo",
  "fallback_logo_url": "https://tools.huo15.com/uploads/images/system/logo-colours.png"
}
```

**页眉代码示例（动态获取公司信息）**：

```python
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os
import json
import urllib.request

# 公司信息配置
COMPANY_CONFIG_PATH = '/Users/jobzhao/.openclaw/workspace/config/company_info.json'
DEFAULT_LOGO_PATH = '/Users/jobzhao/.openclaw/workspace/assets/logo.png'

# 默认公司信息（当无法获取时使用）
DEFAULT_COMPANY_NAME = '青岛火一五信息科技有限公司'
FALLBACK_LOGO_URL = 'https://tools.huo15.com/uploads/images/system/logo-colours.png'
COMPANY_LOGO_URL = 'https://huihuoyun.huo15.com/web/image/website/1/logo'

def get_company_info():
    """
    获取公司信息，自动确保LOGO存在
    返回: (company_name, logo_path)
    
    注意：LOGO会自动下载到用户目录 ~/.huo15/assets/logo.png
    """
    company_name = COMPANY_NAME
    logo_path = ensure_logo_exists()  # 确保LOGO存在
    return company_name, logo_path

def add_header_with_logo(doc, logo_path=None, company_name=None):
    """添加页眉，包含 LOGO 图片 + 公司名称 + 底线"""
    # 获取公司信息
    if logo_path is None or company_name is None:
        company_name, logo_path = get_company_info()
    
    section = doc.sections[0]
    header = section.header
    header.paragraphs.clear()
    
    # 设置页眉高度
    section.header_distance = Cm(1.5)
    
    # 添加段落（左对齐）
    paragraph = header.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # 1. 添加 LOGO 图片（如果存在）
    if os.path.exists(logo_path):
        try:
            # 添加图片，高度 1cm，宽度自动
            run = paragraph.add_run()
            run.add_picture(logo_path, height=Cm(1.0))
        except Exception as e:
            # 如果图片加载失败，继续添加文字
            pass
    
    # 2. 添加公司名称（紧挨着 LOGO）
    run = paragraph.add_run(f' {company_name}')
    set_font(run, '黑体', 10)
    
    # 3. 添加页眉底线
    pPr = OxmlElement('w:pPr')
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '000000')
    pBdr.append(bottom)
    pPr.append(pBdr)
    paragraph._element.insert(0, pPr)
    
    return header
```

**重要提醒（强制执行）**：
- 生成文档时**必须调用** `add_header_with_logo(doc)` 函数
- LOGO 图片路径：`/Users/jobzhao/.openclaw/workspace/assets/logo.png`
- 如果图片不存在，**自动从公司系统下载**，或使用备用 LOGO
- 公司名称与 LOGO 之间保留一个空格，紧挨着显示
- **公司信息会自动从辉火云企业套件系统获取**，无需手动配置

**LOGO 添加检查清单（每次生成文档前必须自检）**：
- [ ] LOGO 图片文件是否存在于 `/Users/jobzhao/.openclaw/workspace/assets/logo.png`
- [ ] 代码中是否调用了 `add_picture()` 方法添加 LOGO
- [ ] 页眉中是否包含 LOGO + 公司名称 + 底线 三个元素
- [ ] 是否设置了页眉底线（`w:bottom` 边框）

**常见错误及解决方案**：

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 文档没有 LOGO | 代码中缺少 `add_picture()` 调用 | 必须调用 `run.add_picture(logo_path, height=Cm(1.0))` |
| LOGO 路径错误 | 图片路径写错或文件不存在 | 使用绝对路径，生成前检查 `os.path.exists(logo_path)` |
| LOGO 太大/太小 | 高度设置不合理 | 使用 `height=Cm(1.0)` 标准高度 |
| LOGO 和文字分开 | 没有在同一 paragraph 中添加 | LOGO 和公司名称必须在同一个 paragraph 中 |

**完整调用示例**：

```python
from docx import Document
from docx.shared import Cm
import os

# 创建文档
doc = Document()

# 1. 设置页面格式
for section in doc.sections:
    section.top_margin = Cm(3.7)
    section.bottom_margin = Cm(3.5)
    section.left_margin = Cm(2.8)
    section.right_margin = Cm(2.6)

# 2. 添加页眉（必须包含 LOGO）
logo_path = '/Users/jobzhao/.openclaw/workspace/assets/logo.png'

# 检查 LOGO 是否存在
if not os.path.exists(logo_path):
    raise FileNotFoundError(f"LOGO 图片不存在：{logo_path}")

section = doc.sections[0]
header = section.header
header.paragraphs.clear()
section.header_distance = Cm(1.5)

paragraph = header.add_paragraph()
paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

# 添加 LOGO
run = paragraph.add_run()
run.add_picture(logo_path, height=Cm(1.0))

# 添加公司名称
run = paragraph.add_run(' 青岛火一五信息科技有限公司')
set_font(run, '黑体', 10)

# 添加底线
# ...（参考上方完整代码）

# 3. 继续添加文档内容
# ...
```

### 页脚（GB/T 9704-2012 公文格式）
- **内容**：页码（如"第 1 页 共 3 页"）
- **位置**：页面下边缘居中
- **字体**：仿宋，小四（12pt）
- **WPS 兼容格式**：
  - 使用 `w:eastAsia` 字体域确保 WPS 识别
  - 数字同样使用仿宋字体
- **示例**：`第 1 页 共 3 页`

### 页脚代码示例（WPS 兼容）

```python
from docx.shared import Pt, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_footer_with_page_numbers(doc):
    """添加页脚，包含当前页和总页数，WPS 兼容"""
    section = doc.sections[0]
    
    # 设置页脚距离页面底部边距
    section.footer_distance = Cm(1.5)
    
    # 获取或创建页脚
    footer = section.footer
    
    # 添加段落（居中）
    paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 添加"第"字
    run1 = paragraph.add_run("第")
    run1.font.name = '仿宋'
    run1._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    run1.font.size = Pt(12)
    
    # 插入当前页码域（PAGE）
    run2 = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText1 = OxmlElement('w:instrText')
    instrText1.text = 'PAGE'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run2._element.append(fldChar1)
    run2._element.append(instrText1)
    run2._element.append(fldChar2)
    run2.font.name = '仿宋'
    run2._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    run2.font.size = Pt(12)
    
    # 添加"页 共"文字
    run3 = paragraph.add_run("页 共")
    run3.font.name = '仿宋'
    run3._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    run3.font.size = Pt(12)
    
    # 插入总页数域（NUMPAGES）
    run4 = paragraph.add_run()
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'begin')
    instrText2 = OxmlElement('w:instrText')
    instrText2.text = 'NUMPAGES'
    fldChar4 = OxmlElement('w:fldChar')
    fldChar4.set(qn('w:fldCharType'), 'end')
    run4._element.append(fldChar3)
    run4._element.append(instrText2)
    run4._element.append(fldChar4)
    run4.font.name = '仿宋'
    run4._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    run4.font.size = Pt(12)
    
    # 添加"页"字
    run5 = paragraph.add_run("页")
    run5.font.name = '仿宋'
    run5._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    run5.font.size = Pt(12)
```

---

## 📁 文档命名规则（必须遵循）

### 命名格式

```
[文档类型]_[客户名称]_[项目名称]_[日期]_[版本].docx
```

### 命名元素说明

| 元素 | 说明 | 示例 | 必填 |
|------|------|------|------|
| 文档类型 | 具体文档类型 | 合同、报价单、发货单、会议纪要、技术方案 | ✅ |
| 客户名称 | 客户公司简称 | 阿里、腾讯、华为、海尔 | ✅ |
| 项目名称 | 项目名称（可选） | ERP、MES、WMS、OA | ○ |
| 日期 | 文档日期，格式 YYYYMMDD | 20250319 | ✅ |
| 版本 | 版本号 v1.0（可选，默认 v1.0） | v1.0、v1.1、v2.0 | ○ |

### 文档类型编码

| 文档类型 | 编码 | 说明 |
|----------|------|------|
| 合同 | CONTRACT | 销售合同、服务合同 |
| 报价单 | QUOTE | 产品报价、项目报价 |
| 发货单 | DELIVERY | 发货清单、送货单 |
| 会议纪要 | MEMO | 会议记录、洽谈纪要 |
| 技术方案 | PROPOSAL | 解决方案、技术方案 |
| 功能说明书 | SPEC | 产品功能说明、需求规格 |
| 验收报告 | ACCEPTANCE | 项目验收、交付验收 |
| 发票 | INVOICE | 增值税发票、普通发票 |

### 命名示例

```
# 完整格式
CONTRACT_阿里_钉钉OA_20250319_v1.0.docx
QUOTE_腾讯_云ERP_20250318.docx
DELIVERY_海尔_WMS_20250317_v1.0.docx
MEMO_华为_技术洽谈_20250316.docx
PROPOSAL_海信_MES系统_20250315_v2.0.docx

# 无项目名称
CONTRACT_京东_20250319.docx
QUOTE_字节跳动_20250318.docx

# 有版本迭代
CONTRACT_小米_智能制造_20250319_v1.1.docx
SPEC_美团_外卖系统_20250314_v1.2.docx
```

### ⚠️ 命名规则

1. **使用下划线 `_` 分隔各元素**（不要用空格或连字符）
2. **客户名称使用中文简称**，去除"有限公司"、"股份有限公司"等后缀
3. **日期必须为 8 位数字**（YYYYMMDD）
4. **版本号格式为 vX.X**（如 v1.0、v2.1）
5. **禁止出现特殊字符**：`\/:*?"<>|`
6. **文件后缀必须为 .docx**

### 自动命名函数

```python
import datetime

def generate_doc_name(doc_type, customer_name, project_name="", version="v1.0"):
    """
    生成符合规范的文档名称
    
    参数:
        doc_type: 文档类型编码（如 CONTRACT, QUOTE）
        customer_name: 客户名称
        project_name: 项目名称（可选）
        version: 版本号（可选，默认 v1.0）
    
    返回:
        文档名称字符串，如 CONTRACT_阿里_钉钉OA_20250319_v1.0.docx
    """
    # 日期
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    
    # 清理客户名称（去除公司后缀）
    customer = customer_name.replace("有限公司", "").replace("股份有限公司", "").replace("集团", "").strip()
    
    # 清理项目名称
    project = project_name.strip() if project_name else ""
    
    # 构建名称
    parts = [doc_type, customer]
    if project:
        parts.append(project)
    parts.append(date_str)
    
    # 添加版本（如果不是默认版本）
    if version and version != "v1.0":
        parts.append(version)
    
    # 拼接并添加后缀
    doc_name = "_".join(parts) + ".docx"
    
    return doc_name

# 使用示例
# generate_doc_name("CONTRACT", "阿里巴巴有限公司", "钉钉OA", "v1.0")
# -> CONTRACT_阿里_钉钉OA_20250319_v1.0.docx

# generate_doc_name("QUOTE", "腾讯科技有限公司")
# -> QUOTE_腾讯_20250319.docx
```

### 检查清单（生成文档前必查）

- [ ] 文档名称是否包含文档类型？
- [ ] 客户名称是否为简称（去除有限公司等）？
- [ ] 日期是否为 8 位数字格式？
- [ ] 版本号格式是否正确（vX.X）？
- [ ] 是否使用了下划线分隔？
- [ ] 是否包含了 .docx 后缀？
- [ ] 是否有禁止的特殊字符？

---

## 🚀 简化函数：一条命令完成文档格式

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os
import urllib.request
import json

# ============== 配置区域 ==============
# 使用用户目录下的 .huo15 目录，跨平台通用
USER_HOME = os.path.expanduser("~")
LOGO_DIR = os.path.join(USER_HOME, ".huo15", "assets")
DEFAULT_LOGO_PATH = os.path.join(LOGO_DIR, "logo.png")
FALLBACK_LOGO_URL = 'https://tools.huo15.com/uploads/images/system/logo-colours.png'
COMPANY_NAME = '青岛火一五信息科技有限公司'

def ensure_logo_exists(logo_path=DEFAULT_LOGO_PATH):
    """确保 LOGO 存在，不存在则自动下载到用户目录"""
    if os.path.exists(logo_path) and os.path.getsize(logo_path) > 0:
        return logo_path
    
    # 创建目录并下载
    os.makedirs(os.path.dirname(logo_path), exist_ok=True)
    try:
        urllib.request.urlretrieve(FALLBACK_LOGO_URL, logo_path)
        print(f"✓ LOGO 已自动下载: {logo_path}")
    except Exception as e:
        raise FileNotFoundError(f"❌ LOGO 下载失败: {e}\n请检查网络后重试")
    
    return logo_path

def set_chinese_font(run, font_name='仿宋', font_size=12, bold=False):
    """设置中文字体（WPS/Word兼容）"""
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(font_size)
    run.bold = bold
    return run

def add_header_with_logo(doc, logo_path=None, company_name=None):
    """添加页眉：LOGO + 公司名称 + 底线
    
    注意：LOGO会自动下载，无需手动配置
    """
    # 获取公司信息和LOGO路径
    _company_name, _logo_path = get_company_info()
    logo_path = logo_path or _logo_path
    company_name = company_name or _company_name
    
    section = doc.sections[0]
    header = section.header
    header.paragraphs.clear()
    section.header_distance = Cm(1.5)
    
    # 添加 LOGO + 公司名称
    paragraph = header.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    run = paragraph.add_run()
    run.add_picture(logo_path, height=Cm(1.0))
    
    run = paragraph.add_run(f' {company_name}')
    set_chinese_font(run, '黑体', 10)
    
    # 添加底线
    pPr = OxmlElement('w:pPr')
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '000000')
    pBdr.append(bottom)
    pPr.append(pBdr)
    paragraph._element.insert(0, pPr)

def add_footer_with_page_numbers(doc):
    """添加页脚：第 X 页 共 Y 页"""
    section = doc.sections[0]
    section.footer_distance = Cm(1.5)
    footer = section.footer
    paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 构建页码域
    for text, is_field in [("第", False), ("PAGE", True), ("页 共", False), ("NUMPAGES", True), ("页", False)]:
        run = paragraph.add_run(text)
        set_chinese_font(run, '仿宋', 12)
        if is_field:
            fldChar1 = OxmlElement('w:fldChar')
            fldChar1.set(qn('w:fldCharType'), 'begin')
            instrText = OxmlElement('w:instrText')
            instrText.text = text
            fldChar2 = OxmlElement('w:fldChar')
            fldChar2.set(qn('w:fldCharType'), 'end')
            run._element.clear()
            run._element.append(fldChar1)
            run._element.append(instrText)
            run._element.append(fldChar2)

def create_formatted_doc(title="", logo_path=None, company_name=None):
    """
    🚀 一条命令创建符合公司规范的 Word 文档
    
    参数:
        title: 文档标题（可选）
        logo_path: LOGO 图片路径（可选，默认自动查找/下载）
        company_name: 公司名称（可选，默认"青岛火一五信息科技有限公司"）
    
    返回:
        doc: python-docx Document 对象
    
    使用示例:
        doc = create_formatted_doc("销售合同")
        doc.add_paragraph("合同正文内容...")
        doc.save("CONTRACT_客户_20250319.docx")
    """
    # 1. 创建文档
    doc = Document()
    
    # 2. 设置页面边距（GB/T 9704-2012）
    for section in doc.sections:
        section.top_margin = Cm(3.7)
        section.bottom_margin = Cm(3.5)
        section.left_margin = Cm(2.8)
        section.right_margin = Cm(2.6)
    
    # 3. 添加页眉（LOGO + 公司名）
    add_header_with_logo(doc, logo_path, company_name)
    
    # 4. 添加页脚（页码）
    add_footer_with_page_numbers(doc)
    
    # 5. 设置默认字体
    style = doc.styles['Normal']
    style.font.name = '仿宋'
    style.font.size = Pt(12)
    style._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    
    # 6. 添加标题（如果提供）
    if title:
        p = doc.add_paragraph(title)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            set_chinese_font(run, '黑体', 22, True)
    
    return doc
```

### 简化函数使用流程

```python
# 步骤1：一条命令创建文档（自动包含 LOGO + 页码 + 字体）
doc = create_formatted_doc(
    title="销售合同",
    company_name="青岛火一五信息科技有限公司"
)

# 步骤2：添加文档内容
doc.add_paragraph("第一条：...")

# 步骤3：保存文档（按命名规范）
doc.save("CONTRACT_客户名_20250319.docx")

# 完成！✅
```

> **重要**：使用 `create_formatted_doc()` 函数会自动处理：
> - ✅ 页面边距（3.7/3.5/2.8/2.6cm）
> - ✅ 页眉 LOGO + 公司名称 + 底线
> - ✅ 页脚页码（第 X 页 共 Y 页）
> - ✅ 默认字体（仿宋小四）
> - ✅ LOGO 不存在时自动下载

---

## 公司信息
- 公司名称：青岛火一五信息科技有限公司
- 社会信用代码：91370203MA3CKR364A
- 地址：青岛市市南区南京路 8 号创联工场 6 楼 615
- 电话：18554898815
- 邮箱：postmaster@huo15.com

## 文档结构

1. 合同标题 - 居中，黑体二号加粗
2. 合同编号 - 居中，仿宋三号
3. 签订日期 - 居中，仿宋三号
4. 一，二，三...章 - 楷体三号加粗
5. 签署栏 - 盖章、法定代表人、日期

## 表格样式
- 表头：加粗，仿宋小四
- 正文：仿宋，小四（12pt）
- 边框：Table Grid

---

## 实践经验总结（2026-03-14）

### WPS页码兼容问题解决方案

**问题**：之前生成的文档在WPS中页码显示不正确

**根因**：页码域代码实现方式不正确

**最终解决方案（2026-03-14验证通过）**：

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# 关键：正确添加域代码的方式
run2 = paragraph.add_run()
fldChar1 = OxmlElement('w:fldChar')
fldChar1.set(qn('w:fldCharType'), 'begin')
instrText1 = OxmlElement('w:instrText')
instrText1.text = 'PAGE'
fldChar2 = OxmlElement('w:fldChar')
fldChar2.set(qn('w:fldCharType'), 'end')
run2._element.append(fldChar1)  # 注意：用append不是set
run2._element.append(instrText1)
run2._element.append(fldChar2)
run2.font.name = '仿宋'
run2._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
run2.font.size = Pt(12)
```

**关键要点**：
1. 必须使用 `run._element.append()` 添加域元素，而不是其他方式
2. 每个run都要设置字体域：`run._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')`
3. 同时设置 `run.font.name = '仿宋'`
4. PAGE域显示当前页，NUMPAGES域显示总页数

**验证结果**：WPS和Word均正确显示页码

### WPS字体兼容性问题解决方案

**问题**：生成的文档在WPS中字体显示不正确（显示为宋体而非仿宋/黑体等）

**根因**：
1. 只设置了 `run.font.name`，没有设置 `w:eastAsia` 字体域
2. WPS 和 Word 对字体的渲染机制不同

**实践经验（2026-03-14验证通过）**：

```python
# 正确：每个run都要设置字体域
run.font.name = '仿宋'
run._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')  # 关键！
run.font.size = Pt(12)
```

**关键要点**：
1. **每个run都要设置字体域**：不能只设置一次，必须对每个run调用
2. **同时设置两个属性**：`run.font.name` + `run._element.rPr.rFonts.set()`
3. **正文样式也要设置**：
```python
style = doc.styles['Normal']
style.font.name = "仿宋"
style.font.size = Pt(12)
style._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
```
4. **字体域必须用正确的命名空间**：`qn('w:eastAsia')`

**验证结果**：WPS和Word均正确显示字体

---

## 实践经验总结（2026-03-19）

### 不要依赖pip安装包，代码模板就在SKILL.md中

**问题**：初次使用技能时，误以为需要 `pip install huo15_doc` 安装Python包才能使用

**根因**：看到SKILL.md中的 `from huo15_doc import create_formatted_doc` 就以为需要pip包

**经验教训**：
1. `huo15-doc-template` 是一个**文档模板规范技能**，不是pip包
2. 代码模板**直接写在SKILL.md中**，可以直接复制使用
3. 不需要任何pip安装，直接复制SKILL.md中的Python代码即可

**正确使用流程**：
1. 打开 `~/.openclaw/workspace/skills/huo15-doc-template/SKILL.md`
2. 找到"简化函数"部分的代码模板
3. 直接复制到Python脚本中使用
4. 确保LOGO文件存在（如不存在会自动下载）

**简化函数一键使用**：
```python
# 直接从SKILL.md复制此函数，无需pip安装！
doc = create_formatted_doc(
    title="知本元项目情况汇总",
    company_name="青岛火一五信息科技有限公司"
)
# 添加内容...
doc.save("文档名.docx")
```

**验证结果**：成功生成符合公司规范的Word文档
