---
name: chart-generator
description: Data visualization chart generator. Use when user needs to create charts from data for reports, presentations, or documents. Supports bar, line, pie, scatter, radar charts with PNG/SVG output. 数据可视化、图表生成、数据报告。
version: 1.0.2
license: MIT-0
metadata: {"openclaw": {"emoji": "📊", "requires": {"bins": ["python3"]}}}
dependencies: "pip install matplotlib pandas openpyxl python-docx pillow"
---

# Chart Generator

Professional data visualization chart generator for reports, presentations, and documents.

## Features

- 📊 **Multiple Chart Types**: Bar, line, pie, scatter, radar, area, stacked
- 📁 **Multiple Data Sources**: CSV, Excel, JSON, manual, web, document extraction
- 🎨 **Professional Styling**: Clean, publication-ready charts with custom options
- 📐 **Flexible Output**: PNG, SVG, PDF, Word, Excel, Markdown, HTML
- 🔗 **Embed Support**: Direct embedding into documents
- 🌍 **Multi-Language**: Chinese, English, Japanese, Korean (no encoding issues)
- ✅ **Cross-Platform**: Windows, macOS, Linux

## Supported Chart Types

| Type | Use Case | Best For |
|------|----------|----------|
| **Bar Chart** | Compare values | Sales, rankings |
| **Line Chart** | Show trends | Time series, growth |
| **Pie Chart** | Show proportions | Market share, composition |
| **Scatter Plot** | Show correlation | Data relationships |
| **Radar Chart** | Multi-dimension | Performance comparison |
| **Area Chart** | Cumulative values | Stacked data |
| **Stacked Bar** | Composition | Multi-category breakdown |

## Trigger Conditions

- "帮我画图" / "Create a chart"
- "生成柱状图" / "Generate bar chart"
- "数据可视化" / "Data visualization"
- "做一个趋势图" / "Make a trend chart"
- "图表分析" / "Chart analysis"
- "chart-generator"

---

## Step 1: Understand Requirements

```
请提供以下信息：

图表类型：（柱状图/折线图/饼图/散点图/雷达图）
数据来源：（手动输入/CSV/Excel/JSON）
数据内容：
标题：
X轴标签：
Y轴标签：
输出格式：（PNG/SVG）
颜色要求：（默认/自定义）
```

---

## Step 2: Generate Chart

### Python Script Template

```python
python3 << 'PYEOF'
import os
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
from matplotlib import font_manager

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ChartGenerator:
    def __init__(self):
        self.fig = None
        self.ax = None
        
    def create_bar_chart(self, labels, values, title='', 
                         xlabel='', ylabel='', 
                         color='#3182ce', output_path=None):
        """Create bar chart"""
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        
        bars = self.ax.bar(labels, values, color=color, edgecolor='white', linewidth=0.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:,.0f}',
                        ha='center', va='bottom', fontsize=10)
        
        self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        self.ax.set_xlabel(xlabel, fontsize=12)
        self.ax.set_ylabel(ylabel, fontsize=12)
        
        # Clean styling
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            self.fig.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        
        return self.fig
    
    def create_line_chart(self, x_data, y_data_list, labels=None,
                         title='', xlabel='', ylabel='',
                         colors=None, output_path=None):
        """Create line chart"""
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        
        if colors is None:
            colors = ['#3182ce', '#48bb78', '#ed8936', '#e53e3e', '#9f7aea']
        
        for i, y_data in enumerate(y_data_list):
            color = colors[i % len(colors)]
            label = labels[i] if labels and i < len(labels) else f'Series {i+1}'
            self.ax.plot(x_data, y_data, marker='o', linewidth=2, 
                        color=color, label=label, markersize=6)
        
        self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        self.ax.set_xlabel(xlabel, fontsize=12)
        self.ax.set_ylabel(ylabel, fontsize=12)
        
        if labels:
            self.ax.legend(loc='best', framealpha=0.9)
        
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            self.fig.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        
        return self.fig
    
    def create_pie_chart(self, labels, values, title='',
                        colors=None, output_path=None):
        """Create pie chart"""
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        
        if colors is None:
            colors = ['#3182ce', '#48bb78', '#ed8936', '#e53e3e', '#9f7aea',
                     '#38b2ac', '#d69e2e', '#667eea']
        
        wedges, texts, autotexts = self.ax.pie(
            values, labels=labels, colors=colors[:len(values)],
            autopct='%1.1f%%', startangle=90,
            textprops={'fontsize': 11}
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if output_path:
            self.fig.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        
        return self.fig
    
    def create_scatter_plot(self, x_data, y_data, title='',
                           xlabel='', ylabel='',
                           color='#3182ce', output_path=None):
        """Create scatter plot"""
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        
        self.ax.scatter(x_data, y_data, c=color, alpha=0.6, s=50)
        
        # Add trend line
        z = np.polyfit(x_data, y_data, 1)
        p = np.poly1d(z)
        self.ax.plot(x_data, p(x_data), '--', color='#e53e3e', alpha=0.8, label='Trend')
        
        self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        self.ax.set_xlabel(xlabel, fontsize=12)
        self.ax.set_ylabel(ylabel, fontsize=12)
        self.ax.legend()
        
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            self.fig.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        
        return self.fig
    
    def create_multi_bar_chart(self, labels, data_dict, title='',
                              xlabel='', ylabel='', output_path=None):
        """Create grouped bar chart"""
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(labels))
        width = 0.8 / len(data_dict)
        
        colors = ['#3182ce', '#48bb78', '#ed8936', '#e53e3e', '#9f7aea']
        
        for i, (name, values) in enumerate(data_dict.items()):
            offset = (i - len(data_dict)/2 + 0.5) * width
            bars = self.ax.bar(x + offset, values, width, label=name,
                             color=colors[i % len(colors)], edgecolor='white')
        
        self.ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        self.ax.set_xlabel(xlabel, fontsize=12)
        self.ax.set_ylabel(ylabel, fontsize=12)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels)
        self.ax.legend()
        
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            self.fig.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        
        return self.fig
    
    def load_from_csv(self, csv_path, x_col=None, y_cols=None):
        """Load data from CSV file"""
        df = pd.read_csv(csv_path)
        
        if x_col is None:
            x_col = df.columns[0]
        if y_cols is None:
            y_cols = [col for col in df.columns if col != x_col]
        
        return {
            'x': df[x_col].tolist(),
            'y': {col: df[col].tolist() for col in y_cols},
            'df': df
        }
    
    def load_from_excel(self, excel_path, sheet_name=0, x_col=None, y_cols=None):
        """Load data from Excel file"""
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        if x_col is None:
            x_col = df.columns[0]
        if y_cols is None:
            y_cols = [col for col in df.columns if col != x_col]
        
        return {
            'x': df[x_col].tolist(),
            'y': {col: df[col].tolist() for col in y_cols},
            'df': df
        }
    
    def load_from_json(self, json_path):
        """Load data from JSON file"""
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def load_from_directory(self, dir_path, file_pattern='*.csv'):
        """Load and aggregate data from multiple files in directory"""
        import glob
        
        all_data = []
        for file_path in glob.glob(os.path.join(dir_path, file_pattern)):
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                continue
            df['source_file'] = os.path.basename(file_path)
            all_data.append(df)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()
    
    def extract_data_from_text(self, text):
        """Extract numerical data from text content"""
        import re
        
        # Find patterns like "Sales: 100" or "销售额：100万"
        patterns = [
            r'(\w+)\s*[:：]\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*[:：]\s*(\w+)',
        ]
        
        data = {}
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 2:
                    key, value = match
                    try:
                        data[key] = float(value)
                    except ValueError:
                        pass
        
        return data
    
    def save_to_png(self, output_path, dpi=150):
        """Save chart as PNG"""
        if self.fig:
            self.fig.savefig(output_path, dpi=dpi, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
            return output_path
    
    def save_to_svg(self, output_path):
        """Save chart as SVG"""
        if self.fig:
            self.fig.savefig(output_path, format='svg', bbox_inches='tight',
                           facecolor='white', edgecolor='none')
            return output_path
    
    def save_to_pdf(self, output_path):
        """Save chart as PDF"""
        if self.fig:
            self.fig.savefig(output_path, format='pdf', bbox_inches='tight',
                           facecolor='white', edgecolor='none')
            return output_path
    
    def save_to_base64(self, format='png'):
        """Convert chart to base64 string for embedding"""
        import io
        import base64
        
        if self.fig:
            buffer = io.BytesIO()
            self.fig.savefig(buffer, format=format, bbox_inches='tight',
                           facecolor='white', edgecolor='none')
            buffer.seek(0)
            img_str = base64.b64encode(buffer.read()).decode()
            return f'data:image/{format};base64,{img_str}'
    
    def embed_in_markdown(self, title='', caption=''):
        """Generate markdown with embedded chart"""
        base64_img = self.save_to_base64('png')
        
        md = f'\n'
        if title:
            md += f'## {title}\n\n'
        md += f'![{title}]({base64_img})\n'
        if caption:
            md += f'\n*{caption}*\n'
        
        return md
    
    def embed_in_html(self, title='', width='100%'):
        """Generate HTML with embedded chart"""
        base64_img = self.save_to_base64('png')
        
        html = f'''
<div class="chart-container">
    {f'<h3>{title}</h3>' if title else ''}
    <img src="{base64_img}" alt="{title}" style="max-width: {width};">
</div>
'''
        return html
    
    def save_to_word(self, output_path, title='', caption=''):
        """Save chart to Word document"""
        from docx import Document
        from docx.shared import Inches
        
        doc = Document()
        
        if title:
            doc.add_heading(title, level=2)
        
        # Save chart as temporary image
        temp_img = output_path.replace('.docx', '_temp.png')
        self.save_to_png(temp_img)
        
        # Add image to document
        doc.add_picture(temp_img, width=Inches(6))
        
        if caption:
            last_para = doc.paragraphs[-1]
            last_para.alignment = 1  # Center
        
        doc.save(output_path)
        
        # Clean up temp file
        if os.path.exists(temp_img):
            os.remove(temp_img)
        
        return output_path

# Example usage
generator = ChartGenerator()
output_dir = os.environ.get('OPENCLAW_WORKSPACE', os.getcwd())

# Bar chart
labels = ['Q1', 'Q2', 'Q3', 'Q4']
values = [150000, 180000, 220000, 280000]
generator.create_bar_chart(
    labels, values,
    title='2026 Quarterly Sales',
    xlabel='Quarter',
    ylabel='Sales ($)',
    output_path=os.path.join(output_dir, 'bar_chart.png')
)

# Line chart
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
product_a = [100, 120, 140, 160, 180, 200]
product_b = [80, 95, 110, 130, 150, 170]
generator.create_line_chart(
    months, [product_a, product_b],
    labels=['Product A', 'Product B'],
    title='Sales Trend',
    xlabel='Month',
    ylabel='Sales',
    output_path=os.path.join(output_dir, 'line_chart.png')
)

# Pie chart
pie_labels = ['Product A', 'Product B', 'Product C', 'Others']
pie_values = [35, 25, 20, 20]
generator.create_pie_chart(
    pie_labels, pie_values,
    title='Market Share',
    output_path=os.path.join(output_dir, 'pie_chart.png')
)

print(f"✅ Charts generated in: {output_dir}")
PYEOF
```

---

## Data Sources (数据来源)

### From CSV

```python
generator = ChartGenerator()
data = generator.load_from_csv('data.csv', x_col='Month', y_cols=['Sales', 'Profit'])

generator.create_line_chart(
    data['x'], 
    [data['y']['Sales'], data['y']['Profit']],
    labels=['Sales', 'Profit'],
    title='Monthly Performance'
)
```

### From Excel

```python
data = generator.load_from_excel('report.xlsx', sheet_name='Sheet1')
```

### Manual Input

```python
labels = ['A', 'B', 'C', 'D']
values = [100, 200, 150, 300]
generator.create_bar_chart(labels, values)
```

---

## Styling Options (样式选项)

### Colors

```python
# Single color
color='#3182ce'  # Blue

# Multiple colors
colors=['#3182ce', '#48bb78', '#ed8936', '#e53e3e']
```

### Size

```python
# Default size
figsize=(10, 6)

# Large for presentations
figsize=(16, 9)

# Square for reports
figsize=(8, 8)
```

---

## Security Notes

- ✅ No network calls or external endpoints
- ✅ No credentials or API keys required
- ✅ Local file processing only
- ✅ Open source dependencies (matplotlib, pandas)
- ✅ No data uploaded to external servers

---

## Notes

- Uses matplotlib for chart generation
- Supports CSV, Excel, and manual data input
- Output formats: PNG, SVG, PDF
- Chinese font support with Noto Sans SC
- Cross-platform compatible
