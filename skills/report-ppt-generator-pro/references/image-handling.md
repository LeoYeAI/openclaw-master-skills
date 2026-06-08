# Image Handling Guide

Guide for processing images in PPT generation.

## Supported Image Sources

### Local Files
```
/path/to/image.png
./images/chart.jpg
~/Pictures/photo.png
```

### Network URLs
```
https://example.com/image.png
https://cdn.company.com/assets/logo.svg
```

### Data URLs (Base64)
```
data:image/png;base64,iVBORw0KGgo...
```

---

## Image Processing Workflow

### Step 1: Validate Image Source

```javascript
function validateImageSource(source) {
  // Local file
  if (source.startsWith('/') || source.startsWith('./') || source.startsWith('~')) {
    return { type: 'local', path: source };
  }
  // Network URL
  if (source.startsWith('http://') || source.startsWith('https://')) {
    return { type: 'url', url: source };
  }
  // Base64
  if (source.startsWith('data:image')) {
    return { type: 'base64', data: source };
  }
  return { type: 'unknown' };
}
```

### Step 2: Determine Image Intent

Based on context or explicit instruction:

| Intent | Description | Recommended Layout |
|--------|-------------|-------------------|
| `data-chart` | Data visualization | Left Text + Right Image |
| `photo` | Team photo, event | Top Text + Bottom Image |
| `icon` | Small decorative | Inline with text |
| `background` | Full-slide background | Full Image Background |
| `screenshot` | Product screenshot | Left Text + Right Image |
| `logo` | Company/brand logo | Cover page or corner |

### Step 3: Calculate Dimensions

```javascript
// Target slide dimensions (16:9)
const SLIDE_WIDTH = 1920;
const SLIDE_HEIGHT = 1080;

// Common image placements
const PLACEMENTS = {
  // Right side (40% width)
  'right-side': { x: '60%', y: '15%', w: '35%', h: '70%' },
  // Bottom (40% height)
  'bottom': { x: '5%', y: '55%', w: '90%', h: '40%' },
  // Center
  'center': { x: '25%', y: '20%', w: '50%', h: '60%' },
  // Full slide
  'full': { x: 0, y: 0, w: '100%', h: '100%' },
  // Logo (corner)
  'logo': { x: '5%', y: '5%', w: '10%', h: 'auto' }
};
```

---

## Automatic Scaling

### HTML/CSS Approach

```css
.slide img {
  /* Scale down to fit, maintain aspect ratio */
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
}
```

### pptxgenjs Approach

```javascript
// Option 1: Specify width only (auto height)
slide.addImage({
  path: '/path/to/image.png',
  x: 1, y: 2, w: 4,
  sizing: { type: 'contain', w: 4, h: 3 }
});

// Option 2: Fit within bounds
slide.addImage({
  path: '/path/to/image.png',
  x: 1, y: 2, w: 4, h: 3,
  sizing: { type: 'contain', w: 4, h: 3 }
});

// Option 3: Cover area (may crop)
slide.addImage({
  path: '/path/to/image.png',
  x: 1, y: 2, w: 4, h: 3,
  sizing: { type: 'cover', w: 4, h: 3 }
});
```

---

## Cropping Guidelines

### When to Crop

1. **Background images** that don't match 16:9 ratio
2. **Wide screenshots** that exceed slide width
3. **Tall photos** that exceed slide height

### Crop Strategy

```javascript
function calculateCrop(imageWidth, imageHeight, targetRatio = 16/9) {
  const imageRatio = imageWidth / imageHeight;

  if (imageRatio > targetRatio) {
    // Image is wider - crop sides
    const newWidth = imageHeight * targetRatio;
    const cropX = (imageWidth - newWidth) / 2;
    return {
      crop: { left: cropX, right: cropX, top: 0, bottom: 0 },
      focus: 'center'
    };
  } else if (imageRatio < targetRatio) {
    // Image is taller - crop top/bottom
    const newHeight = imageWidth / targetRatio;
    const cropY = (imageHeight - newHeight) / 2;
    return {
      crop: { left: 0, right: 0, top: cropY, bottom: cropY },
      focus: 'center'
    };
  }

  return { crop: null, focus: 'none' };
}
```

### CSS Object-Fit for Cropping

```css
/* Cover (may crop) */
img.cover {
  object-fit: cover;
  width: 100%;
  height: 100%;
}

/* Contain (no crop, letterboxing) */
img.contain {
  object-fit: contain;
  width: 100%;
  height: 100%;
}
```

---

## Image Quality

### Compression Recommendations

| Image Type | Format | Quality |
|------------|--------|---------|
| Screenshots | PNG | Lossless |
| Photos | JPEG | 80-90% |
| Charts/Diagrams | PNG or SVG | Lossless |
| Logos | SVG or PNG | Lossless |

### Size Limits

- **Recommended max**: 2MB per image
- **Warning threshold**: 5MB per image
- **Hard limit**: 10MB per image

---

## Handling Network Images

### Download for PPTX Export

```javascript
async function downloadImage(url) {
  const response = await fetch(url);
  const buffer = await response.arrayBuffer();
  return Buffer.from(buffer);
}

// Use in pptxgenjs
const imageData = await downloadImage(imageUrl);
slide.addImage({
  data: imageData.toString('base64'),
  x: 1, y: 2, w: 4, h: 3
});
```

### Error Handling

```javascript
async function safeAddImage(slide, imageSource, options) {
  try {
    if (imageSource.startsWith('http')) {
      const imageData = await downloadImage(imageSource);
      slide.addImage({
        data: imageData.toString('base64'),
        ...options
      });
    } else {
      slide.addImage({
        path: imageSource,
        ...options
      });
    }
  } catch (error) {
    console.warn(`Failed to load image: ${imageSource}`);
    // Add placeholder text
    slide.addText('[图片加载失败]', {
      x: options.x,
      y: options.y,
      w: options.w,
      h: options.h,
      align: 'center',
      valign: 'middle'
    });
  }
}
```

---

## Image in HTML Template

### Basic Image Slide

```html
<div class="slide" id="slide-3">
  <h2 class="section-title">数据分析</h2>
  <div class="divider"></div>
  <div class="columns">
    <div class="column text">
      <ul>
        <li>用户增长显著，月活达到120万</li>
        <li>转化率提升至8.5%</li>
      </ul>
    </div>
    <div class="column image">
      <img src="/path/to/chart.png" alt="增长趋势图">
    </div>
  </div>
</div>
```

### Background Image Slide

```html
<div class="slide cover" style="background-image: url('/path/to/bg.jpg');">
  <div class="overlay"></div>
  <div class="cover-content">
    <h1>我们的愿景</h1>
    <p>成为行业领先者</p>
  </div>
</div>
```

```css
.slide.cover {
  background-size: cover;
  background-position: center;
}

.overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
}
```