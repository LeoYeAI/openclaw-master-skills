# PPT Extraction Reference

Read this file when converting a PowerPoint file (Phase 4). It contains the extraction script and usage notes.

## Dependency

```bash
pip install python-pptx
```

## Extraction Script

```python
from pptx import Presentation
from pptx.util import Inches, Pt
import json
import os

def extract_pptx(file_path, output_dir):
    """
    Extract all content from a PowerPoint file.
    Returns a list of slide dicts with title, content, images, and notes.
    Images are saved to output_dir/assets/.
    """
    prs = Presentation(file_path)
    slides_data = []

    assets_dir = os.path.join(output_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)

    for slide_num, slide in enumerate(prs.slides):
        slide_data = {
            'number': slide_num + 1,
            'title': '',
            'content': [],
            'images': [],
            'notes': ''
        }

        for shape in slide.shapes:
            # Text content
            if shape.has_text_frame:
                if shape == slide.shapes.title:
                    slide_data['title'] = shape.text
                else:
                    text = shape.text.strip()
                    if text:
                        slide_data['content'].append({'type': 'text', 'content': text})

            # Images (shape_type 13 = Picture)
            if shape.shape_type == 13:
                image = shape.image
                image_ext = image.ext
                image_name = f"slide{slide_num + 1}_img{len(slide_data['images']) + 1}.{image_ext}"
                image_path = os.path.join(assets_dir, image_name)
                with open(image_path, 'wb') as f:
                    f.write(image.blob)
                slide_data['images'].append({
                    'path': f"assets/{image_name}",
                    'width': shape.width,
                    'height': shape.height
                })

        # Speaker notes
        if slide.has_notes_slide:
            notes_text = slide.notes_slide.notes_text_frame.text.strip()
            if notes_text:
                slide_data['notes'] = notes_text

        slides_data.append(slide_data)

    return slides_data


# Usage
if __name__ == '__main__':
    import sys
    pptx_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    data = extract_pptx(pptx_path, out_dir)
    print(json.dumps(data, indent=2, ensure_ascii=False))
```

## After Extraction

Present the extracted structure to the user:

```
I've extracted the following from your PowerPoint:

**Slide 1: [Title]**
- [Content summary]
- Images: [count]

**Slide 2: [Title]**
...

All images saved to the assets/ folder.

Does this look correct? Ready to choose a style?
```

Then proceed to Phase 2 (Style Discovery) with the extracted content in mind.
