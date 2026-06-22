---
name: openocr-skills
description: Extract text from images, documents and scanned PDFs using OpenOCR - supports text detection, recognition, universal VLM recognition, and document parsing with layout analysis
author: openocr
version: "0.1.4"
tags: [ocr, text-detection, text-recognition, document-parsing, vlm, unirec, layout-analysis, formula, table]
tools: [computer, code_execution, file_operations]
library:
  name: OpenOCR
  url: https://github.com/Topdu/OpenOCR
  stars: 1k+
---

# OpenOCR Skill

## Overview

This skill enables intelligent text extraction, document parsing, and universal recognition using **OpenOCR** - an accurate and efficient general OCR system. It provides a unified interface for text detection, text recognition, end-to-end OCR, VLM-based universal recognition (text/formulas/tables), and document parsing with layout analysis. Supports Chinese, English, and more.

## How to Use

1. Provide the image, scanned document, or PDF
2. Optionally specify the task type (det/rec/ocr/unirec/doc)
3. I'll extract text, formulas, tables, or full document structure

**Example prompts:**
- "Extract all text from this image"
- "Detect text regions in this photo"
- "Recognize the formula in this screenshot"
- "Parse this PDF document with layout analysis"
- "Convert this scanned page to Markdown"

## Domain Knowledge

### OpenOCR Fundamentals

```python
from openocr import OpenOCR

# Initialize with a specific task
engine = OpenOCR(task='ocr')

# Run OCR on an image (callable interface)
results, time_dicts = engine(image_path='image.jpg')

# Results contain detected boxes with recognized text
for result in results:
    for line in result:
        box = line[0]       # Bounding box coordinates
        text = line[1][0]   # Recognized text
        conf = line[1][1]   # Confidence score
        print(f"{text} ({conf:.2f})")
```

### Supported Tasks

```python
# Available task types
tasks = {
    'det':    'Text Detection - detect text regions with bounding boxes',
    'rec':    'Text Recognition - recognize text from cropped images',
    'ocr':    'End-to-End OCR - detection + recognition pipeline',
    'unirec': 'Universal Recognition - VLM-based text/formula/table recognition (0.1B params)',
    'doc':    'Document Parsing - layout analysis + universal recognition (0.1B params)',
}

# Task selection via parameter
det_engine = OpenOCR(task='det')
rec_engine = OpenOCR(task='rec')
ocr_engine = OpenOCR(task='ocr')
unirec_engine = OpenOCR(task='unirec')
doc_engine = OpenOCR(task='doc')
```

### Configuration Options

```python
from openocr import OpenOCR

# === Text Detection ===
detector = OpenOCR(
    task='det',
    backend='onnx',                          # 'onnx' (default) or 'torch'
    onnx_det_model_path=None,                # Custom detection model (auto-downloads if None)
    use_gpu='auto',                          # 'auto', 'true', or 'false'
)

# === Text Recognition ===
recognizer = OpenOCR(
    task='rec',
    mode='mobile',                           # 'mobile' (fast) or 'server' (accurate)
    backend='onnx',                          # 'onnx' (default) or 'torch'
    onnx_rec_model_path=None,                # Custom recognition model
    use_gpu='auto',
)

# === End-to-End OCR ===
ocr = OpenOCR(
    task='ocr',
    mode='mobile',                           # 'mobile' or 'server'
    backend='onnx',                          # 'onnx' or 'torch'
    onnx_det_model_path=None,                # Custom detection model
    onnx_rec_model_path=None,                # Custom recognition model
    drop_score=0.5,                          # Confidence threshold for filtering
    det_box_type='quad',                     # 'quad' or 'poly' (for curved text)
    use_gpu='auto',
)

# === Universal Recognition (UniRec) ===
unirec = OpenOCR(
    task='unirec',
    unirec_encoder_path=None,                # Custom encoder ONNX model
    unirec_decoder_path=None,                # Custom decoder ONNX model
    tokenizer_mapping_path=None,             # Custom tokenizer mapping JSON
    max_length=2048,                         # Max generation length
    auto_download=True,                      # Auto-download missing models
    use_gpu='auto',
)

# === Document Parsing (OpenDoc) ===
doc = OpenOCR(
    task='doc',
    layout_model_path=None,                  # Custom layout detection model (PP-DocLayoutV2)
    unirec_encoder_path=None,                # Custom UniRec encoder
    unirec_decoder_path=None,                # Custom UniRec decoder
    tokenizer_mapping_path=None,             # Custom tokenizer mapping
    layout_threshold=0.5,                    # Layout detection threshold
    use_layout_detection=True,               # Enable layout analysis
    max_parallel_blocks=4,                   # Max parallel VLM blocks
    auto_download=True,                      # Auto-download missing models
    use_gpu='auto',
)
```

### Task-Specific Usage

#### Text Detection
```python
from openocr import OpenOCR

detector = OpenOCR(task='det', backend='onnx')

# Detect text regions
results = detector(image_path='image.jpg')

boxes = results[0]['boxes']      # np.ndarray of bounding boxes
elapse = results[0]['elapse']    # Processing time in seconds

print(f"Found {len(boxes)} text regions in {elapse:.3f}s")
for box in boxes:
    print(f"  Box: {box.tolist()}")
```

#### Text Recognition
```python
from openocr import OpenOCR

# Mobile mode (fast, ONNX)
recognizer = OpenOCR(task='rec', mode='mobile', backend='onnx')

# Server mode (accurate, requires torch)
# recognizer = OpenOCR(task='rec', mode='server', backend='torch')

results = recognizer(image_path='word.jpg', batch_num=1)

text = results[0]['text']        # Recognized text string
score = results[0]['score']      # Confidence score
elapse = results[0]['elapse']    # Processing time

print(f"Text: {text}, Score: {score:.3f}, Time: {elapse:.3f}s")
```

#### End-to-End OCR
```python
from openocr import OpenOCR

ocr = OpenOCR(task='ocr', mode='mobile', backend='onnx')

# Run OCR with visualization
results, time_dicts = ocr(
    image_path='image.jpg',
    save_dir='./output',
    is_visualize=True,
    rec_batch_num=6,
)

# Process results
for result in results:
    for line in result:
        box, (text, confidence) = line[0], line[1]
        print(f"{text} ({confidence:.2f})")
```

#### Universal Recognition (UniRec)
```python
from openocr import OpenOCR

unirec = OpenOCR(task='unirec')

# Image input
result_text, generated_ids = unirec(image_path='formula.jpg', max_length=2048)
print(f"Result: {result_text}")

# PDF input (returns list of tuples, one per page)
results = unirec(image_path='document.pdf', max_length=2048)
for page_text, page_ids in results:
    print(f"Page: {page_text[:100]}...")
```

#### Document Parsing (OpenDoc)
```python
from openocr import OpenOCR

doc = OpenOCR(task='doc', use_layout_detection=True)

# Parse a document image
result = doc(image_path='document.jpg')

# Save outputs in multiple formats
doc.save_to_markdown(result, './output')
doc.save_to_json(result, './output')
doc.save_visualization(result, './output')

# Parse a PDF (returns list of dicts, one per page)
results = doc(image_path='document.pdf')
for page_result in results:
    doc.save_to_markdown(page_result, './output')
```

### Command-Line Interface

```bash
# Text Detection
openocr --task det --input_path image.jpg --is_vis

# Text Recognition
openocr --task rec --input_path word.jpg --mode server --backend torch

# End-to-End OCR
openocr --task ocr --input_path image.jpg --is_vis --output_path ./results

# Universal Recognition
openocr --task unirec --input_path formula.jpg --max_length 2048

# Document Parsing
openocr --task doc --input_path document.pdf \
    --use_layout_detection --save_vis --save_json --save_markdown

# Launch Gradio Demos
openocr --task launch_openocr_demo --share --server_port 7860
openocr --task launch_unirec_demo --share --server_port 7861
openocr --task launch_opendoc_demo --share --server_port 7862
```

### Processing Different Sources

#### Image Files
```python
from openocr import OpenOCR

ocr = OpenOCR(task='ocr')

# Single image
results, _ = ocr(image_path='image.jpg')

# Directory of images
results, _ = ocr(image_path='./images/', save_dir='./output', is_visualize=True)
```

#### PDF Files
```python
from openocr import OpenOCR

# UniRec handles PDFs natively
unirec = OpenOCR(task='unirec')
results = unirec(image_path='document.pdf', max_length=2048)

# OpenDoc handles PDFs natively with layout analysis
doc = OpenOCR(task='doc', use_layout_detection=True)
results = doc(image_path='document.pdf')

# Save each page
for page_result in results:
    doc.save_to_markdown(page_result, './output')
    doc.save_to_json(page_result, './output')
```

#### Numpy Array Input
```python
import cv2
from openocr import OpenOCR

ocr = OpenOCR(task='ocr')

# Read image as numpy array
img = cv2.imread('image.jpg')

# Pass numpy array directly
results, _ = ocr(img_numpy=img)
```

### Result Formats

```python
# Detection result format
det_result = [{'boxes': np.ndarray, 'elapse': float}]

# Recognition result format
rec_result = [{'text': str, 'score': float, 'elapse': float}]

# OCR result format (detection + recognition)
ocr_result = (results_list, time_dicts)
# results_list: [[[box, (text, confidence)], ...], ...]

# UniRec result format
# Image: (text: str, generated_ids: list)
# PDF:   [(text: str, generated_ids: list), ...]  # one per page

# Doc result format
# Image: dict with layout blocks and recognized content
# PDF:   [dict, ...]  # one per page
```

## Best Practices

1. **Choose the Right Task**: Use `ocr` for general text, `unirec` for formulas/tables, `doc` for full documents
2. **Use Mobile Mode for Speed**: `mode='mobile'` is much faster; use `mode='server'` only when accuracy is critical
3. **Use ONNX Backend**: Default ONNX backend works on CPU without extra dependencies
4. **Set Appropriate Thresholds**: Adjust `drop_score` (OCR) and `layout_threshold` (Doc) for your use case
5. **Enable Layout Detection**: For documents with mixed content (text + formulas + tables), always enable `use_layout_detection`
6. **Batch Processing**: Use `rec_batch_num` to control recognition batch size for throughput optimization
7. **GPU Acceleration**: Install `onnxruntime-gpu` or PyTorch with CUDA for significant speedup

## Common Patterns

### Full Document Processing Pipeline
```python
from openocr import OpenOCR
import os

def process_documents(input_dir, output_dir):
    """Process all documents in a directory."""
    doc = OpenOCR(task='doc', use_layout_detection=True)

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.jpg', '.png', '.pdf', '.bmp')):
            filepath = os.path.join(input_dir, filename)
            print(f"Processing: {filename}")

            result = doc(image_path=filepath)

            # Handle PDF (list) vs image (dict)
            if isinstance(result, list):
                for page_result in result:
                    doc.save_to_markdown(page_result, output_dir)
                    doc.save_to_json(page_result, output_dir)
            else:
                doc.save_to_markdown(result, output_dir)
                doc.save_to_json(result, output_dir)

    print(f"All results saved to {output_dir}")

process_documents('./docs', './output')
```

### OCR with Custom Post-Processing
```python
from openocr import OpenOCR
import re

def extract_structured_text(image_path, drop_score=0.5):
    """Extract and structure text from an image."""
    ocr = OpenOCR(task='ocr', drop_score=drop_score)
    results, _ = ocr(image_path=image_path)

    lines = []
    for result in results:
        for line in result:
            box = line[0]
            text = line[1][0]
            confidence = line[1][1]

            # Calculate bounding box center
            y_center = sum(p[1] for p in box) / 4

            lines.append({
                'text': text,
                'confidence': confidence,
                'y_center': y_center,
                'box': box,
            })

    # Sort by vertical position (top to bottom)
    lines.sort(key=lambda x: x['y_center'])

    return lines

result = extract_structured_text('page.jpg')
for line in result:
    print(f"{line['text']} ({line['confidence']:.2f})")
```

### Formula Recognition
```python
from openocr import OpenOCR

def recognize_formula(image_path):
    """Recognize mathematical formula from image."""
    unirec = OpenOCR(task='unirec')
    text, ids = unirec(image_path=image_path, max_length=2048)

    # UniRec outputs LaTeX for formulas
    print(f"LaTeX: {text}")
    return text

latex = recognize_formula('formula.png')
# Output: \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
```

### Table Extraction
```python
from openocr import OpenOCR

def extract_table(image_path):
    """Extract table content from image."""
    unirec = OpenOCR(task='unirec')
    text, ids = unirec(image_path=image_path, max_length=2048)

    # UniRec outputs LaTeX table format
    print(f"Table: {text}")
    return text

table_latex = extract_table('table.png')
```

## Examples

### Example 1: Batch OCR with Progress
```python
from openocr import OpenOCR
import os

def batch_ocr(image_dir, output_dir='./ocr_results'):
    """OCR all images in a directory."""
    ocr = OpenOCR(task='ocr', mode='mobile')

    os.makedirs(output_dir, exist_ok=True)

    image_files = [
        f for f in os.listdir(image_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))
    ]

    all_results = {}
    for i, filename in enumerate(image_files):
        filepath = os.path.join(image_dir, filename)
        print(f"[{i+1}/{len(image_files)}] Processing: {filename}")

        results, time_dicts = ocr(
            image_path=filepath,
            save_dir=output_dir,
            is_visualize=True,
        )

        texts = []
        for result in results:
            for line in result:
                texts.append(line[1][0])

        all_results[filename] = texts
        print(f"  Found {len(texts)} text lines")

    # Save all text
    with open(os.path.join(output_dir, 'all_text.txt'), 'w') as f:
        for filename, texts in all_results.items():
            f.write(f"--- {filename} ---\n")
            f.write('\n'.join(texts))
            f.write('\n\n')

    return all_results

results = batch_ocr('./images')
```

### Example 2: Document to Markdown Converter
```python
from openocr import OpenOCR
import os

def doc_to_markdown(input_path, output_dir='./markdown_output'):
    """Convert document images or PDFs to Markdown."""
    doc = OpenOCR(
        task='doc',
        use_layout_detection=True,
        use_chart_recognition=True,
    )

    os.makedirs(output_dir, exist_ok=True)

    result = doc(image_path=input_path)

    if isinstance(result, list):
        # PDF: multiple pages
        for page_result in result:
            doc.save_to_markdown(page_result, output_dir)
        print(f"Converted {len(result)} pages to Markdown")
    else:
        # Single image
        doc.save_to_markdown(result, output_dir)
        print("Converted image to Markdown")

    print(f"Output saved to: {output_dir}")

# Convert a scanned PDF
doc_to_markdown('paper.pdf')

# Convert a document image
doc_to_markdown('page.jpg')
```

### Example 3: Multi-Task Comparison
```python
from openocr import OpenOCR

def compare_tasks(image_path):
    """Compare results from different OpenOCR tasks."""

    # 1. Detection only
    det = OpenOCR(task='det')
    det_result = det(image_path=image_path)
    num_boxes = len(det_result[0]['boxes'])
    print(f"Detection: Found {num_boxes} text regions")

    # 2. End-to-End OCR
    ocr = OpenOCR(task='ocr')
    ocr_results, _ = ocr(image_path=image_path)
    ocr_texts = [line[1][0] for result in ocr_results for line in result]
    print(f"OCR: Extracted {len(ocr_texts)} text lines")
    for t in ocr_texts[:5]:
        print(f"  - {t}")

    # 3. Universal Recognition
    unirec = OpenOCR(task='unirec')
    text, _ = unirec(image_path=image_path)
    print(f"UniRec: {text[:200]}...")

    return {
        'det_boxes': num_boxes,
        'ocr_texts': ocr_texts,
        'unirec_text': text,
    }

compare_tasks('document.jpg')
```

### Example 4: Gradio Demo Launch
```python
from openocr import launch_openocr_demo, launch_unirec_demo, launch_opendoc_demo

# Launch OCR demo
launch_openocr_demo(share=True, server_port=7860, server_name='0.0.0.0')

# Launch UniRec demo
launch_unirec_demo(share=True, server_port=7861)

# Launch OpenDoc demo
launch_opendoc_demo(share=True, server_port=7862)
```

## Limitations

- Text recognition accuracy depends on image quality
- Very small or heavily rotated text may reduce accuracy
- `server` mode requires PyTorch and is slower than `mobile` mode
- UniRec and Doc tasks use 0.1B parameter VLM, larger models may yield better results
- PDF processing converts pages to images internally, very large PDFs may use significant memory
- Complex handwritten text accuracy varies
- GPU recommended for best performance, especially for Doc and UniRec tasks

## Installation

```bash
# Basic installation (CPU, ONNX backend)
pip install openocr-python

# GPU-accelerated ONNX inference
pip install openocr-python[onnx-gpu]

# PyTorch backend (for server mode)
pip install openocr-python[pytorch]

# Gradio demos
pip install openocr-python[gradio]

# All optional dependencies
pip install openocr-python[all]

# From source
git clone https://github.com/Topdu/OpenOCR.git
cd OpenOCR
python build_package.py
pip install ./build/dist/openocr_python-*.whl
```

## Resources

- [OpenOCR GitHub](https://github.com/Topdu/OpenOCR)
- [PyPI Package](https://pypi.org/project/openocr-python/)
- [UniRec Paper](https://github.com/Topdu/OpenOCR#unirec)
- [OpenDoc Documentation](https://github.com/Topdu/OpenOCR#opendoc)
- [Model Zoo & Configs](https://github.com/Topdu/OpenOCR/tree/main/configs)
