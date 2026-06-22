---
name: fill-docx-template
description: 当用户需要基于模板填充 Word 文档（.docx）、从模板生成报告、创建包含动态数据的合同，或自动化文档生成时使用此技能。包括替换普通占位符 {name} 替换文本、使用 {name|r:x,c:y} 格式标记的智能表格填充（支持从标记行开始向下填充，保留上方内容）、插入图片、批量生成文档等。如果用户提及 .docx 模板、邮件合并功能或以编程方式填写 Word 表单，请使用此技能。
---

# Word 文档模板填充指南

## 概述

本指南介绍如何使用 Python 向 Word（.docx）模板填充动态数据。支持：

- **普通占位符**：`{variable_name}` 替换文本
- **智能表格填充**：使用 `{name|r:x,c:y}` 标记在表格左侧任意位置，自动从标记行向下填充，保留上方内容，并自动调整表格行列数

### ⚠️ 1. 表格自动调整的时机与条件

**表格并非总是"提前自动扩展"** - 这取决于占位符是否被正确识别：

- ✅ **会被自动调整的情况**：当且仅当 `{name|r:x,c:y}` 格式**完全正确**且位于**该行的最左侧单元格（第一列）**时，表格会在 `DocxTemplateFiller` 初始化时立即调整为声明的行列数
- ❌ **不会被调整的情况**：如果占位符格式错误、包含空格（如 `{name | r:5, c:4}`）、或不在第一列，表格将**保持原样**，不会自动扩展或收缩

### ⚠️ 2. 普通占位符一般情况下需要被覆盖！

- 除非未提供值时保留原样

### ❌3. 任何情况下不能修改、覆盖模板文件！

### ⚠️4. 尽量使用DocxTemplateFiller类的方法实现所有功能！

## 快速开始

```python
from docx import Document
from docx.shared import Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import re
import os

class DocxTemplateFiller:
    def __init__(self, template_path):
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"模板文件不存在: {template_path}")
        self.doc = Document(template_path)
        self.template_path = template_path
        self.named_tables = {}  # 存储表格信息

        # 初始化时扫描表格占位符
        self._process_table_placeholders()

    def _process_table_placeholders(self):
        """
        扫描所有表格的每一行第一个单元格，查找 {name|r:x,c:y} 格式
        例如：{products|r:5,c:4} 表示从当前行开始，共5行，4列
        """
        pattern = re.compile(r'\{(\w+)\|r:(\d+),c:(\d+)\}')

        for table_idx, table in enumerate(self.doc.tables):
            for row_idx, row in enumerate(table.rows):
                if len(row.cells) == 0:
                    continue

                # 检查每行的第一个单元格（最左侧）
                first_cell = row.cells[0]
                text = first_cell.text.strip()
                match = pattern.search(text)

                if match:
                    name = match.group(1)
                    target_rows = int(match.group(2))
                    target_cols = int(match.group(3))

                    # 保存表格配置信息
                    self.named_tables[name] = {
                        'table': table,
                        'start_row': row_idx,      # 占位符所在行（从此行开始填充）
                        'target_rows': target_rows, # 需要填充的总行数（包括占位符行）
                        'target_cols': target_cols  # 目标列数
                    }

                    # 调整表格大小：上方保留 row_idx 行，从 row_idx 开始有 target_rows 行
                    self._resize_table(table, row_idx, target_rows, target_cols)

                    # 清除占位符文本（可选，因为填充时会覆盖，但清除更干净）
                    # 保留单元格其他可能的文本（占位符前后文本）
                    new_text = pattern.sub('', first_cell.text).strip()
                    if new_text:
                        first_cell.text = new_text
                    else:
                        first_cell.text = ""  # 清空等待填充

    def _resize_table(self, table, start_row, target_rows, target_cols):
        """调整表格大小：确保从 start_row 开始有 target_rows 行，总列数为 target_cols"""
        total_needed_rows = start_row + target_rows
        current_rows = len(table.rows)
        current_cols = len(table.columns) if table.columns else 0

        # 调整行数
        if total_needed_rows > current_rows:
            # 添加行
            for _ in range(total_needed_rows - current_rows):
                table.add_row()
        elif total_needed_rows < current_rows:
            # 删除多余行（从末尾删除，保留前面的）
            self._delete_rows_from_end(table, current_rows - total_needed_rows)

        # 调整列数
        if target_cols != current_cols:
            self._resize_columns(table, target_cols)

    def _delete_rows_from_end(self, table, num_rows):
        """从表格末尾删除指定行数"""
        tbl = table._tbl
        for _ in range(num_rows):
            if len(table.rows) > 0:
                tr = table.rows[-1]._tr
                tbl.remove(tr)

    def _resize_columns(self, table, target_cols):
        """调整表格列数"""
        current_cols = len(table.columns)
        tbl = table._tbl
        tblGrid = tbl.find(qn('w:tblGrid'))

        if target_cols > current_cols:
            # 添加列定义
            for _ in range(target_cols - current_cols):
                gridCol = OxmlElement('w:gridCol')
                tblGrid.append(gridCol)

            # 为每一行添加单元格
            for row in table.rows:
                for _ in range(target_cols - current_cols):
                    tc = OxmlElement('w:tc')
                    tcPr = OxmlElement('w:tcPr')
                    tc.append(tcPr)
                    p = OxmlElement('w:p')
                    tc.append(p)
                    row._tr.append(tc)

        elif target_cols < current_cols:
            # 删除多余列定义
            for _ in range(current_cols - target_cols):
                if len(tblGrid) > 0:
                    tblGrid.remove(tblGrid[-1])

            # 从每行删除多余单元格
            for row in table.rows:
                for _ in range(current_cols - target_cols):
                    tcs = row._tr.findall(qn('w:tc'))
                    if len(tcs) > target_cols:
                        row._tr.remove(tcs[-1])

    def fill_placeholders(self, data_dict):
        """替换普通占位符 {key}（不包括表格定义格式）"""
        # 匹配普通占位符，排除表格定义格式
        pattern = re.compile(r'\{(\w+)\}(?!\|r:\d+,c:\d+)')

        # 处理段落
        for para in self.doc.paragraphs:
            self._replace_in_paragraph(para, pattern, data_dict)

        # 处理表格内的普通占位符（排除已识别的表格占位符单元格）
        for table in self.doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        self._replace_in_paragraph(para, pattern, data_dict)

    def _replace_in_paragraph(self, paragraph, pattern, data_dict):
        """在段落中执行替换"""
        text = paragraph.text
        matches = pattern.findall(text)

        if not matches:
            return

        new_text = text
        for key in matches:
            if key in data_dict:
                placeholder = f'{{{key}}}'
                value = str(data_dict[key])
                new_text = new_text.replace(placeholder, value)

        if new_text != text and paragraph.runs:
            paragraph.runs[0].text = new_text
            for run in paragraph.runs[1:]:
                run.text = ""

    def fill_named_table(self, table_name, data):
        """
        填充指定名称的表格
        从占位符所在行开始（包括该行）向下填充，保留上方内容

        :param table_name: 表格名称（来自占位符 {name|r:x,c:y}）
        :param data: 二维列表，如 [['产品A', '规格1', '10'], [...]]
        """
        if table_name not in self.named_tables:
            raise KeyError(f"未找到名为 '{table_name}' 的表格，请确保模板中存在 '{{{table_name}|r:x,c:y}}' 格式的占位符在最左侧单元格")

        table_info = self.named_tables[table_name]
        table = table_info['table']
        start_row = table_info['start_row']
        target_rows = table_info['target_rows']
        target_cols = table_info['target_cols']

        # 确保数据不超过声明的行数
        if len(data) > target_rows:
            data = data[:target_rows]

        # 从 start_row 开始填充（包括该行）
        for row_offset, row_data in enumerate(data):
            actual_row_idx = start_row + row_offset
            if actual_row_idx >= len(table.rows):
                break

            # 确保不超出列数
            if len(row_data) > target_cols:
                row_data = row_data[:target_cols]

            # 填充该行的每一列
            for col_idx, value in enumerate(row_data):
                if col_idx >= len(table.columns):
                    break
                table.cell(actual_row_idx, col_idx).text = str(value)

    def fill_all(self, text_data=None, table_data=None):
        """
        一键填充所有内容

        :param text_data: 普通占位符字典，如 {'company': 'ABC公司'}
        :param table_data: 表格数据字典，如 {'products': [[...], [...]]}
        """
        if text_data:
            self.fill_placeholders(text_data)

        if table_data:
            for name, data in table_data.items():
                self.fill_named_table(name, data)

    def insert_paragraph_at(self, index, text, style=None):
        """在指定位置插入段落"""
        if index == -1 or index >= len(self.doc.paragraphs):
            p = self.doc.add_paragraph(text)
        else:
            p = self.doc.paragraphs[index].insert_paragraph_before(text)

        if style:
            p.style = style
        return p

    def insert_image(self, paragraph_index, image_path, width=None):
        """在指定段落后插入图片"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片不存在: {image_path}")

        para = self.doc.paragraphs[paragraph_index]
        run = para.add_run()

        if width:
            run.add_picture(image_path, width=Inches(width))
        else:
            run.add_picture(image_path)

    def save(self, output_path):
        self.doc.save(output_path)
        print(f"✅ 文档已生成: {os.path.abspath(output_path)}")

```
## 模板创建规范

### 1. 普通占位符

使用 `{variable_name}` 格式：
```

甲方（购方）：{company}
签署日期：{date}
合同编号：{contract_no}

```
### 2. 表格占位符（新逻辑）

**格式**：`{name|r:x,c:y}`
**位置**：表格最左侧的任意单元格（通常是某一行的第一列）
**行为**：

- 从占位符所在行开始，向下填充 x 行
- 占位符所在行会被第一个数据行覆盖
- 占位符上方的行内容完全保留
- 表格会被调整为 y 列

**示例**：
```

| 序号     | 产品名称     | 规格  | 数量  | 单价  | 金额   |
| ------ | -------- | --- | --- | --- | ---- |
| 1      | 产品A      | 规格1 | 10  | 100 | 1000 |
| {items|r:3,c:6} |			|     |     |     |      |
|        |          |     |     |     |      |

```
**说明**：

- `{items|r:3,c:6}` 放在第3行第1列（索引从0开始则为第2行）
- 程序会保留第0-2行（表头+第一行数据）
- 从第3行开始填充3行数据，覆盖占位符
- 表格自动调整为6列

### 3. 复杂模板示例

**场景**：合同中有两个表格，第一个表格上方有静态说明行
```

采购合同

甲方：{company}
乙方：{seller}

产品列表（常规采购）：
| 产品名称 | 型号 | 数量 | 单价 |
|----------|------|------|------|
| {regular|r:4,c:4} |      |      |      |
|          |      |      |      |
|          |      |      |      |
|          |      |      |      |

紧急采购项（如有）：
| 产品名称 | 型号 | 数量 | 要求 |
|----------|------|------|------|
| 说明：紧急采购需24小时内到货 |      |      |      |
| {urgent|r:2,c:4} |      |      |      |
|          |      |      |      |

总计金额：{total_amount}

```
**填充代码**：

```python
filler = DocxTemplateFiller("template.docx")

filler.fill_all(
    text_data={
        'company': '北京科技',
        'seller': '上海贸易',
        'total_amount': '¥50,000'
    },
    table_data={
        'regular': [
            ['办公椅', '人体工学', '10', '¥800'],
            ['办公桌', '1.2米', '5', '¥1500'],
            ['文件柜', '铁皮', '3', '¥600']
            # 第4行不会填充，因为只声明了r:3，但提供了3行数据
        ],
        'urgent': [
            ['投影仪', '4K激光', '1', '急需'],
            ['幕布', '100寸', '1', '配套']
        ]
    }
)

filler.save("contract.docx")
```

**结果**：

- 第一个表格：保留表头，从第2行（占位符行）开始填充4行，共6行（表头+1行静态+4行数据）
- 第二个表格：保留表头和说明行，从第3行（占位符行）开始填充2行

## 关键特性说明

### 1. 上方内容保护

占位符所在行上方的所有行（包括表头、说明文字、静态数据）**完全不会**被修改。

```python
# 模板：
# 第0行：表头 | 名称 | 价格 |
# 第1行：说明 | 这是说明文字 |
# 第2行：占位符 {data|r:2,c:2} | |
# 第3行：空行 | |

# 填充 data = [['A', '100'], ['B', '200']]
# 结果：
# 第0行：表头 | 名称 | 价格 |  （不变）
# 第1行：说明 | 这是说明文字 |  （不变）
# 第2行：A | 100 |  （覆盖占位符）
# 第3行：B | 200 |  （填充）
```

### 2. 自动行数调整

如果模板中占位符下方没有足够的行，程序会自动添加：

```python
# 模板只有3行，占位符在第2行，声明 {data|r:5,c:3}
# 程序会自动添加行，使从第2行开始有5行（总行数至少为2+5=7行）
```

如果模板中占位符下方行数过多，程序会删除多余行（从末尾删除，保留上方内容）。

### 3. 列数自动调整

无论原表格有多少列，程序会调整为占位符声明的列数：

- 列数不足：添加空列
- 列数过多：删除右侧列

## 常见操作示例

### 基础填充（保留表头）

```python
filler = DocxTemplateFiller("contract.docx")

# 表格占位符在模板中位于第2行（索引2，即第3行），声明 {products|r:5,c:4}
# 第0-1行是表头和说明，会被保留

filler.fill_named_table('products', [
    ['笔记本电脑', 'ThinkPad X1', '10', '¥5000'],  # 填充到第2行（覆盖占位符）
    ['显示器', 'Dell 27寸', '20', '¥1500'],         # 填充到第3行
    ['键盘', '机械键盘', '30', '¥300']              # 填充到第4行
    # 第5-6行保持为空（声明了5行，只提供3行数据）
])

filler.save("output.docx")
```

### 多个表格分别填充

```python
filler = DocxTemplateFiller("report.docx")

# 模板中有：
# 表1：左上角某行有 {sales|r:10,c:5}
# 表2：左上角某行有 {expenses|r:5,c:3}

filler.fill_all(
    table_data={
        'sales': [
            ['一月', '产品A', '100', '¥50', '¥5000'],
            ['二月', '产品A', '120', '¥50', '¥6000'],
            # ... 最多10行
        ],
        'expenses': [
            ['办公费', '¥2000', '行政部'],
            ['差旅费', '¥5000', '销售部'],
            # ... 最多5行
        ]
    }
)
```

### 动态表格大小

即使模板中的表格只有占位符那一行，声明 `r:20` 后也会自动扩展：

```python
# 模板表格：
# | 项目 | 数量 | 金额 |
# | {items|r:20,c:3} | | |

filler = DocxTemplateFiller("template.docx")  # 自动扩展到20行数据+表头
filler.fill_named_table('items', large_data_list)  # 最多填充20行
```

## 注意事项

### 1. 占位符位置必须正确

- 必须位于某一行的**第一个单元格**（最左侧）
- 格式必须严格为 `{name|r:数字,c:数字}`，不能有空格
- 如果不在第一个单元格，将无法识别

### 2. 数据行数限制

提供的数据行数超过声明的 `r:x` 时，多余数据会被截断：

```python
# 声明 {data|r:3,c:2}，表示从占位符行开始只有3行空间
filler.fill_named_table('data', [
    ['A', '1'],
    ['B', '2'],
    ['C', '3'],
    ['D', '4']  # 这一行会被忽略，因为只声明了3行
])
```

### 3. 单元格合并

如果占位符所在行存在合并单元格，填充行为可能不符合预期。建议占位符所在行及下方行为标准行列结构。

### 4. 样式保留

填充时会替换单元格的 `.text` 属性，这可能清除单元格内的特殊格式（如加粗、颜色）。如果需要保留格式，建议使用 `python-docx` 的低级 API 直接操作 `run` 对象。

## 快速参考

| 功能        | 方法/说明                                                       |
| --------- | ----------------------------------------------------------- |
| **加载模板**  | `filler = DocxTemplateFiller("template.docx")`              |
| **普通占位符** | `{company}` → `filler.fill_placeholders({'company': '名称'})` |
| **填充表格**  | `filler.fill_named_table('products', [...])`                |
| **一键填充**  | `filler.fill_all(text_dict, table_dict)`                    |
| **上方内容**  | 占位符所在行上方的内容自动保留                                             |
| **覆盖范围**  | 从占位符行开始，向下填充 `r:x` 行                                        |

## 后续步骤

- 如需将生成的 DOCX 转换为 PDF，请参阅 PDF 处理技能
