---
name: claw-presentation-creator
version: 2.0.0
description: Create professional PowerPoint presentations with python-pptx. Supports slides, charts, tables, images, and templates.
category: content-creation
license: MIT
---

# PPTX Skill v2.0

## Overview

Complete PowerPoint presentation creation and editing using `python-pptx`. Supports all common slide operations including text, images, charts, tables, and animations.

## Installation & Dependencies

### Required
```bash
pip install python-pptx pillow
```

### Optional
```bash
# For advanced chart support
pip install numpy

# For HTML conversion (advanced)
npm install puppeteer dom-to-pptx
```

## Quick Start

### Create First Presentation
```python
from pptx import Presentation

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Hello World"
prs.save('presentation.pptx')
print("✓ Presentation created!")
```

### Add Content Slide
```python
from pptx import Presentation

prs = Presentation()

# Title slide
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "My Presentation"
slide.placeholders[1].text = "Subtitle here"

# Content slide
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Agenda"
slide.placeholders[1].text = "• Point 1\n• Point 2\n• Point 3"

prs.save('output.pptx')
```

## Complete API Reference

### Slide Layouts

```python
from pptx import Presentation

prs = Presentation()

# Available layouts (indices may vary by template)
# 0 - Title Slide
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Title"
slide.placeholders[1].text = "Subtitle"

# 1 - Title and Content
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Heading"
slide.placeholders[1].text = "Content here"

# 2 - Section Header
slide = prs.slides.add_slide(prs.slide_layouts[2])

# 3 - Two Content
slide = prs.slides.add_slide(prs.slide_layouts[3])

# 4 - Comparison
slide = prs.slides.add_slide(prs.slide_layouts[4])

# 5 - Title Only
slide = prs.slides.add_slide(prs.slide_layouts[5])

# 6 - Blank
slide = prs.slides.add_slide(prs.slide_layouts[6])
```

### Text Formatting

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[1])

# Title formatting
title = slide.shapes.title
title.text = "Formatted Title"
title.text_frame.paragraphs[0].font.name = 'Arial'
title.text_frame.paragraphs[0].font.size = Pt(36)
title.text_frame.paragraphs[0].font.bold = True
title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)

# Content formatting
content = slide.placeholders[1]
tf = content.text_frame
tf.text = "First paragraph"

# Add paragraph with formatting
p = tf.add_paragraph()
p.text = "Second paragraph"
p.level = 0  # Indentation level
p.alignment = PP_ALIGN.LEFT

# Run-level formatting (within paragraph)
run = p.add_run()
run.text = "Bold text"
run.font.bold = True
run.font.size = Pt(14)
run.font.name = 'Arial'
run.font.color.rgb = RGBColor(0, 112, 192)  # Blue

run = p.add_run()
run.text = " and "

run = p.add_run()
run.text = "italic text"
run.font.italic = True
```

### Adding Images

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Blank layout

# Add image
left = top = Inches(1)
slide.shapes.add_picture(
    'image.jpg',
    left,
    top,
    width=Inches(5),
    height=Inches(3)  # Optional, maintains aspect ratio if omitted
)

# Add image with caption
slide.shapes.add_picture('logo.png', Inches(1), Inches(5), width=Inches(2))

# Add textbox for caption
txBox = slide.shapes.add_textbox(Inches(3.2), Inches(5), Inches(3), Inches(1))
tf = txBox.text_frame
tf.text = "Image caption here"

prs.save('with-image.pptx')
```

### Adding Tables

```python
from pptx import Presentation
from pptx.util import Inches
from pptx.dml.color import RGBColor

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])

# Add table: 3 rows, 3 columns
rows = cols = 3
left = top = Inches(2)
width = Inches(6)
height = Inches(2)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# Set column widths
table.columns[0].width = Inches(2)
table.columns[1].width = Inches(2)
table.columns[2].width = Inches(2)

# Fill data
table.cell(0, 0).text = 'Header 1'
table.cell(0, 1).text = 'Header 2'
table.cell(0, 2).text = 'Header 3'
table.cell(1, 0).text = 'Row 1'
table.cell(1, 1).text = 'Data 1'
table.cell(1, 2).text = 'Data 2'
table.cell(2, 0).text = 'Row 2'
table.cell(2, 1).text = 'Data 3'
table.cell(2, 2).text = 'Data 4'

# Format cells
cell = table.cell(0, 0)
cell.fill.solid()
cell.fill.fore_color.rgb = RGBColor(0, 112, 192)  # Blue header
cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
cell.text_frame.paragraphs[0].font.bold = True

# Center align all cells
for row in table.rows:
    for cell in row.cells:
        cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

prs.save('with-table.pptx')
```

### Adding Charts

```python
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])

# Prepare chart data
chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('Revenue', (100000, 150000, 200000, 250000))
chart_data.add_series('Expenses', (80000, 100000, 120000, 140000))

# Add chart
x, y, cx, cy = Inches(1), Inches(1), Inches(8), Inches(5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,  # Chart type
    x, y, cx, cy,
    chart_data
).chart

# Customize chart
chart.has_title = True
chart.chart_title.text_frame.text = 'Quarterly Financials'
chart.value_axis.has_major_gridlines = True
chart.category_axis.tick_labels.font.size = Pt(10)

prs.save('with-chart.pptx')
```

### Chart Types

```python
from pptx.enum.chart import XL_CHART_TYPE

# Available chart types
XL_CHART_TYPE.COLUMN_CLUSTERED      # Clustered column
XL_CHART_TYPE.COLUMN_STACKED        # Stacked column
XL_CHART_TYPE.BAR_CLUSTERED         # Clustered bar
XL_CHART_TYPE.LINE                  # Line chart
XL_CHART_TYPE.PIE                   # Pie chart
XL_CHART_TYPE.PIE_EXPLODED          # Exploded pie
XL_CHART_TYPE.AREA                  # Area chart
XL_CHART_TYPE.XY_SCATTER            # Scatter plot
XL_CHART_TYPE.BUBBLE                # Bubble chart
XL_CHART_TYPE.DOUGHNUT              # Doughnut chart
XL_CHART_TYPE.RADAR                 # Radar chart
```

### Adding Shapes

```python
from pptx import Presentation
from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])

# Add rectangle
shape = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(1), Inches(1), Inches(3), Inches(2)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0, 112, 192)
shape.line.color.rgb = RGBColor(0, 0, 0)

# Add text to shape
tf = shape.text_frame
tf.text = "Click Shape"
tf.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
tf.paragraphs[0].alignment = PP_ALIGN.CENTER

# Add arrow
arrow = slide.shapes.add_shape(
    MSO_SHAPE.RIGHT_ARROW,
    Inches(4.5), Inches(1.5), Inches(2), Inches(1)
)

# Add ellipse
ellipse = slide.shapes.add_shape(
    MSO_SHAPE.OVAL,
    Inches(1), Inches(4), Inches(2), Inches(2)
)

prs.save('with-shapes.pptx')
```

### Using Templates

```python
from pptx import Presentation

# Use existing template
prs = Presentation('template.pptx')

# Add slides with template layouts
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Using Template"

# Access slide master
slide_master = prs.slide_master
print(f"Template has {len(slide_master.slide_layouts)} layouts")

prs.save('customized.pptx')
```

### Notes and Handouts

```python
from pptx import Presentation

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Slide with Notes"

# Add speaker notes
notes_slide = slide.notes_slide
notes_slide.notes_text_frame.text = """
Speaker Notes:
- Key point 1
- Key point 2
- Remember to mention Q3 results
"""

prs.save('with-notes.pptx')
```

## Complete Examples

### Example 1: Business Presentation

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_business_presentation(output_file):
    prs = Presentation()
    
    # Slide 1: Title
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Q4 Business Review"
    slide.placeholders[1].text = "December 2024\nPresented by: John Doe"
    
    # Slide 2: Agenda
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Agenda"
    tf = slide.placeholders[1].text_frame
    tf.text = "Business Overview"
    for item in ["Financial Performance", "Key Achievements", "Challenges", "Next Steps"]:
        p = tf.add_paragraph()
        p.text = item
        p.level = 0
    
    # Slide 3: Financial Table
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(1))
    title.text_frame.text = "Financial Summary"
    title.text_frame.paragraphs[0].font.size = Pt(24)
    title.text_frame.paragraphs[0].font.bold = True
    
    # Add table
    rows, cols = 5, 4
    left, top, width, height = Inches(0.5), Inches(1.5), Inches(9), Inches(4)
    table = slide.shapes.add_table(rows, cols, left, top, width, height).table
    
    # Headers
    headers = ['Metric', 'Q1', 'Q2', 'Q3']
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0, 112, 192)
        cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.text_frame.paragraphs[0].font.bold = True
    
    # Data
    data = [
        ['Revenue', '$1.2M', '$1.5M', '$1.8M'],
        ['Expenses', '$0.8M', '$0.9M', '$1.0M'],
        ['Profit', '$0.4M', '$0.6M', '$0.8M'],
        ['Margin', '33%', '40%', '44%']
    ]
    for row_idx, row_data in enumerate(data, 1):
        for col_idx, value in enumerate(row_data):
            table.cell(row_idx, col_idx).text = value
    
    # Slide 4: Closing
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Thank You"
    slide.placeholders[1].text = "Questions?\n\ncontact@company.com"
    
    prs.save(output_file)
    print(f"✓ Presentation created: {output_file}")

# Usage
create_business_presentation('business-review.pptx')
```

### Example 2: Photo Gallery

```python
from pptx import Presentation
from pptx.util import Inches
import os

def create_photo_gallery(image_folder, output_file):
    """Create a photo gallery presentation"""
    prs = Presentation()
    
    # Title slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Photo Gallery"
    slide.placeholders[1].text = f"Images from {image_folder}"
    
    # Get images
    images = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    # Add images (2 per slide)
    for i in range(0, len(images), 2):
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        
        # First image
        if i < len(images):
            img_path = os.path.join(image_folder, images[i])
            slide.shapes.add_picture(img_path, Inches(0.5), Inches(1.5), width=Inches(4.5))
            
            # Caption
            txBox = slide.shapes.add_textbox(Inches(0.5), Inches(5.5), Inches(4.5), Inches(1))
            tf = txBox.text_frame
            tf.text = images[i]
            tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        # Second image
        if i + 1 < len(images):
            img_path = os.path.join(image_folder, images[i + 1])
            slide.shapes.add_picture(img_path, Inches(5), Inches(1.5), width=Inches(4.5))
            
            # Caption
            txBox = slide.shapes.add_textbox(Inches(5), Inches(5.5), Inches(4.5), Inches(1))
            tf = txBox.text_frame
            tf.text = images[i + 1]
            tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    prs.save(output_file)
    print(f"✓ Gallery created with {len(images)} images: {output_file}")

# Usage
# create_photo_gallery('./photos', 'gallery.pptx')
```

### Example 3: Invoice Presentation

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def create_invoice_pptx(invoice_data, output_file):
    """Create invoice as PowerPoint slide"""
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    
    # Title
    title = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(1))
    title.text_frame.text = "INVOICE"
    title.text_frame.paragraphs[0].font.size = Pt(36)
    title.text_frame.paragraphs[0].font.bold = True
    title.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # Invoice details
    details = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(4), Inches(2))
    tf = details.text_frame
    tf.text = f"Invoice #: {invoice_data['number']}\n"
    tf.text += f"Date: {invoice_data['date']}\n"
    tf.text += f"Due: {invoice_data['due_date']}"
    
    # Client info
    client = slide.shapes.add_textbox(Inches(5.5), Inches(1.5), Inches(4), Inches(2))
    tf = client.text_frame
    tf.text = f"Bill To:\n{invoice_data['client_name']}\n{invoice_data['client_address']}"
    
    # Items table
    rows = len(invoice_data['items']) + 2
    table = slide.shapes.add_table(rows, 4, Inches(0.5), Inches(4), Inches(9), Inches(3)).table
    
    # Headers
    headers = ['Description', 'Qty', 'Rate', 'Amount']
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0, 112, 192)
        cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.text_frame.paragraphs[0].font.bold = True
    
    # Items
    total = 0
    for row_idx, item in enumerate(invoice_data['items'], 1):
        amount = item['qty'] * item['rate']
        total += amount
        table.cell(row_idx, 0).text = item['description']
        table.cell(row_idx, 1).text = str(item['qty'])
        table.cell(row_idx, 2).text = f"${item['rate']:.2f}"
        table.cell(row_idx, 3).text = f"${amount:.2f}"
    
    # Total row
    table.cell(rows-1, 2).text = "Total:"
    table.cell(rows-1, 2).text_frame.paragraphs[0].font.bold = True
    table.cell(rows-1, 3).text = f"${total:.2f}"
    table.cell(rows-1, 3).text_frame.paragraphs[0].font.bold = True
    
    prs.save(output_file)
    print(f"✓ Invoice created: {output_file}")

# Usage
invoice = {
    'number': 'INV-2024-001',
    'date': '2024-01-15',
    'due_date': '2024-02-15',
    'client_name': 'ABC Corporation',
    'client_address': '123 Business St\nCity, State 12345',
    'items': [
        {'description': 'Web Development', 'qty': 40, 'rate': 100},
        {'description': 'Design', 'qty': 20, 'rate': 80},
        {'description': 'Consulting', 'qty': 10, 'rate': 150}
    ]
}
create_invoice_pptx(invoice, 'invoice.pptx')
```

## Error Handling

### Common Errors

#### Error: "Placeholder not found"
```python
# Solution: Check layout has the placeholder
slide = prs.slides.add_slide(prs.slide_layouts[0])
if len(slide.placeholders) > 1:
    slide.placeholders[1].text = "Subtitle"
```

#### Error: "Image not found"
```python
# Solution: Check file exists before adding
import os
if os.path.exists('image.jpg'):
    slide.shapes.add_picture('image.jpg', Inches(1), Inches(1))
else:
    print("Image file not found!")
```

#### Error: "Chart data error"
```python
# Solution: Ensure data categories and series match
chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3']  # Must match series length
chart_data.add_series('Revenue', (100, 150, 200))
```

## Best Practices

### 1. Use Master Slides for Consistency
```python
# Edit slide master for consistent branding
slide_master = prs.slide_master
title_layout = slide_master.slide_layouts[0]
```

### 2. Keep File Size Manageable
```python
# Compress images before adding
from PIL import Image
img = Image.open('large.jpg')
img.thumbnail((1920, 1080))
img.save('compressed.jpg', quality=85)
```

### 3. Use Standard Fonts
```python
# Use fonts available on most systems
title.text_frame.paragraphs[0].font.name = 'Arial'  # Safe choice
```

### 4. Limit Animations
```python
# python-pptx has limited animation support
# Create simple, clean slides instead
```

## Testing Your Setup

```python
# test-pptx.py
from pptx import Presentation
from pptx.util import Inches
import os

print("Testing PPTX setup...")

# Test 1: Create basic presentation
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Test Presentation"
prs.save('test-output.pptx')
assert os.path.exists('test-output.pptx')
print("✓ Basic creation test passed")

# Test 2: Add content
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Content Slide"
slide.placeholders[1].text = "Test content"
prs.save('test-output.pptx')
print("✓ Content addition test passed")

# Test 3: Load and verify
prs = Presentation('test-output.pptx')
assert len(prs.slides) == 2
print("✓ Load and verify test passed")

# Cleanup
os.remove('test-output.pptx')
print("✓ All tests passed!")
```

Run test:
```bash
python test-pptx.py
```

## License

MIT License - See LICENSE file for details.
