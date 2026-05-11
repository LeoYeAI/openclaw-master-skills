---
name: website-style-images
description: >
  Generate images matching a website's visual style. Use this skill when the user wants to:
  create images in the style of a website, match a website's aesthetic, generate branded images
  from a URL, create banners/social posts/hero images matching a site's design, extract a
  website's visual identity and produce images in that style, or replicate a website's look and feel
  in new images. Also trigger when the user mentions 网站风格图片, 匹配网站风格, 品牌风格图片,
  网站设计风格生成, 根据网站生成图片, or 仿站风格.
emoji: "🌐"
metadata:
  openclaw:
    requires:
      bins:
        - python3
    primaryEnv: NANO_BANANA_ACCESS_KEY
    install:
      - kind: uv
        package: requests
      - kind: uv
        package: Pillow
      - kind: uv
        package: PyYAML
---

# Website Style Image Generator

根据目标网站的视觉风格（配色、字体、美学、情绪），生成匹配该风格的各类图片。


## Setup

Set all 4 environment variables before use (all required):

```bash
export NANO_BANANA_ACCESS_KEY="your-access-key"
export NANO_BANANA_SECRET_KEY="your-secret-key"
```

Also set the API URL (required):

```bash
export NANO_BANANA_API_URL="https://your-api-server/task/v1/submit"
export NANO_BANANA_STATUS_URL="https://your-api-server/task/v1/status/{task_id}"
```


## Overview

- **API**: NANO-BANANA (Gemini 3 Pro Image Preview) — async submit/poll/download
- **风格提取**: 双通道（CSS/DOM 数据 + 截图视觉分析）
- **输出类型**: 横幅、社交媒体、产品展示、博客头图、广告等 8 种
- **脚本**: 所有脚本自包含在 `scripts/` 目录中

## Prerequisites

```bash
pip3 install -r requirements.txt
```

## 支持的图片类型

| ID | 名称 | 默认尺寸 | 适用场景 |
|----|------|---------|---------|
| `hero_banner` | 网站横幅 | 1920×600 | 网站首屏/头部横幅 |
| `social_square` | 社交方图 | 1080×1080 | Instagram、微信朋友圈 |
| `social_story` | 社交竖图 | 1080×1920 | Instagram/抖音 Story |
| `social_landscape` | 社交横图 | 1200×628 | Facebook/LinkedIn 分享 |
| `product_display` | 产品展示 | 1200×1200 | 产品展示图 |
| `blog_header` | 博客头图 | 1200×630 | 博客文章头图 |
| `ad_banner` | 广告横幅 | 1200×628 | 数字广告 |
| `custom` | 自定义 | 用户指定 | 其他用途 |

---

## Workflow

### Phase 0 — 用户需求

**在任何提取之前，先和用户确认三个问题。**

**问题 1：你想设计什么？**

| 选项 | 说明 |
|------|------|
| 品牌宣传图 | 展示品牌形象、slogan、价值主张 |
| 产品推广图 | 突出产品、功能、卖点 |
| 社交媒体内容 | 日常帖子、活动预告、节日营销 |
| 广告素材 | 信息流广告、展示广告 |
| 内容配图 | 博客、文章、教程配图 |
| UI/界面设计 | App 启动页、功能介绍、引导页 |
| 电商图 | 产品主图、详情页、促销 banner |
| 线下物料 | 传单、展架、包装、周边 |

**问题 2：用在哪个平台？**（根据问题 1 智能展示对应选项）

| 设计类型 | 平台选项 → 自动尺寸 |
|---------|-------------------|
| 社交媒体 | Instagram(1080×1080) / 小红书(1080×1440) / 朋友圈(1080×1080) / Facebook(1200×628) / LinkedIn(1200×628) / TikTok(1080×1920) |
| 广告素材 | Google Ads(1200×628) / Facebook Ads(1080×1080) / 抖音信息流(1080×1920) |
| 电商图 | 淘宝主图(800×800) / Amazon(2000×2000) / Shopify(2048×2048) |
| UI设计 | iOS(1242×2688) / Android(1440×3120) / Web(1920×1080) |
| 线下物料 | A4传单(2480×3508) / 展架(2362×5315) / 名片(1050×600) |
| 内容配图 | 博客头图(1200×630) / 微信公众号(900×383) |
| 品牌/产品 | Hero Banner(1920×600) / 产品展示(1200×1200) |

**问题 3：风格从哪来？**

| 选项 | 说明 | 后续流程 |
|------|------|---------|
| 提供网站 URL (Recommended) | 从网站提取配色、字体、设计语言 | → Phase 1 完整提取 |
| 上传截图/图片 | App 截图、品牌手册、竞品图片、任何参考图 | → Phase 1（仅视觉分析，`css_data = {}`） |
| 多个竞品对比 | 提供 2-3 个 URL，分析后选最佳 | → Phase 1 逐个提取后合并 |
| 直接描述风格 | 不需要参考，直接告诉我想要的风格 | → Phase 1（手动构建 style profile） |

收集完三个答案后，进入 Phase 1。

---

### Phase 1 — 风格提取

根据 Phase 0 问题 3 的选择，执行对应的提取流程。

#### Step 1a: CSS/DOM 数据提取（仅有 URL 时执行）

使用 Chrome MCP `navigate` 打开目标网站，然后用 `javascript_tool` 注入以下脚本。

脚本使用元素面积加权颜色重要性，提取字体粗细、letter-spacing、line-height、渐变色值、阴影参数，并跳过不可见元素：

```javascript
(function() {
    const els = document.querySelectorAll('*');
    const colorMap = {}, bgColorMap = {};
    const fonts = new Set(), headingFonts = new Set();
    const fontWeights = { heading: [], body: [] };
    const letterSpacings = [], lineHeights = [];
    let hasGradient = false, hasShadow = false;
    let shadowDetail = '';
    const radiusValues = [];
    const gradientColors = new Set();

    els.forEach(el => {
        const s = window.getComputedStyle(el);
        if (s.display === 'none' || s.visibility === 'hidden' || s.opacity === '0') return;

        // Area-weighted color collection
        const rect = el.getBoundingClientRect();
        const area = Math.max(1, rect.width * rect.height);
        const weight = Math.min(10, Math.ceil(area / 10000));

        const color = s.color;
        const bg = s.backgroundColor;
        if (color && color !== 'rgba(0, 0, 0, 0)') {
            colorMap[color] = (colorMap[color] || 0) + weight;
        }
        if (bg && bg !== 'rgba(0, 0, 0, 0)') {
            bgColorMap[bg] = (bgColorMap[bg] || 0) + weight;
        }

        // Font extraction with weight
        const fontName = s.fontFamily.split(',')[0].trim().replace(/['"]/g, '');
        if (fontName) fonts.add(fontName);

        const isHeading = ['H1','H2','H3','H4','H5','H6'].includes(el.tagName);
        if (isHeading) {
            headingFonts.add(fontName);
            fontWeights.heading.push(s.fontWeight);
        } else {
            fontWeights.body.push(s.fontWeight);
        }

        // Letter-spacing (px)
        const ls = parseFloat(s.letterSpacing);
        if (!isNaN(ls) && ls !== 0) letterSpacings.push(ls);

        // Line-height (ratio)
        const lh = parseFloat(s.lineHeight);
        const fs = parseFloat(s.fontSize);
        if (!isNaN(lh) && !isNaN(fs) && fs > 0) lineHeights.push(lh / fs);

        // Border radius
        const r = parseFloat(s.borderRadius);
        if (r > 0) radiusValues.push(r);

        // Gradient extraction with actual colors
        if (s.backgroundImage && s.backgroundImage.includes('gradient')) {
            hasGradient = true;
            const matches = s.backgroundImage.match(/rgba?\([^)]+\)|#[0-9a-fA-F]{3,8}/g);
            if (matches) matches.forEach(c => gradientColors.add(c));
        }

        // Shadow detail extraction (first significant one)
        if (s.boxShadow && s.boxShadow !== 'none' && !shadowDetail) {
            hasShadow = true;
            shadowDetail = s.boxShadow.length > 100 ? s.boxShadow.substring(0, 100) : s.boxShadow;
        }
    });

    const sortByWeight = obj => Object.entries(obj).sort((a,b) => b[1]-a[1]).map(e => e[0]);
    const modeFn = arr => {
        if (!arr.length) return 'normal';
        const freq = {};
        arr.forEach(v => freq[v] = (freq[v]||0)+1);
        return Object.entries(freq).sort((a,b) => b[1]-a[1])[0][0];
    };

    return JSON.stringify({
        textColors: sortByWeight(colorMap).slice(0, 20),
        backgroundColors: sortByWeight(bgColorMap).slice(0, 20),
        bodyFonts: [...fonts].slice(0, 10),
        headingFonts: [...headingFonts].slice(0, 5),
        fontWeights: {
            heading: modeFn(fontWeights.heading),
            body: modeFn(fontWeights.body)
        },
        letterSpacings: letterSpacings.slice(0, 10),
        lineHeights: lineHeights.slice(0, 10),
        avgBorderRadius: radiusValues.length ?
            radiusValues.reduce((a,b) => a+b,0) / radiusValues.length : 0,
        hasGradient, hasShadow, shadowDetail,
        gradientColors: [...gradientColors].slice(0, 10)
    });
})()
```

保存返回的 JSON 为 `css_data`。

**如果用户上传截图/图片而非 URL**：`css_data = {}`，跳过本步骤，直接进入 Step 1b。

#### Step 1b: 截图与视觉分析

**有 URL 时**：使用 Chrome MCP `computer` 的 `screenshot` 动作截取页面，保存到 `/tmp/website_style_screenshot.png`。

**用户上传截图/图片时**：直接使用用户提供的图片文件。

使用 Read 工具读取图片，用 Claude Vision 分析以下内容：

| 字段 | 描述 | 示例值 |
|------|------|--------|
| `aesthetic` | 整体美学风格 | minimalist, bold, playful, corporate, luxury, tech, organic |
| `palette_mood` | 色彩情绪 | warm, cool, monochromatic, vibrant, muted, earthy |
| `spacing` | 布局间距 | generous whitespace, tight, balanced, airy |
| `photo_style` | 图像风格 | studio photography, flat illustrations, 3D renders, abstract |
| `icon_style` | 图标风格 | 线性图标, 填充图标, 3D 图标, 无图标 |
| `illustration_style` | 插画风格 | 扁平插画, 等距插画, 手绘, 无插画 |
| `photography_treatment` | 摄影处理 | 高对比度, 去饱和, 暖调滤镜, 自然 |
| `pattern_style` | 图案/纹理 | 几何图案, 有机纹理, 噪点, 无 |
| `density` | 信息密度 | 极简, 适中, 密集 |
| `mood_keywords` | 3-5个情绪关键词 | ["professional", "premium", "trustworthy"] |
| `brand_personality` | 品牌个性 | "sophisticated, authoritative, modern tech" |
| `typography_feel` | 字体整体感觉 | "modern, clean", "classic, elegant" |
| `layout_style` | 布局结构 | "grid-based", "asymmetric", "centered single-column" |

将分析结果整理为 `screenshot_analysis` 字典。

#### Step 1c: 网站素材提取（仅有 URL 时执行）

使用 Chrome MCP `javascript_tool` 提取网站中的图片资源：

```javascript
(function() {
    const assets = [];
    // Logo / Favicon
    const favicon = document.querySelector('link[rel*="icon"]');
    if (favicon) assets.push({type: 'logo', url: favicon.href});
    const ogImage = document.querySelector('meta[property="og:image"]');
    if (ogImage) assets.push({type: 'og_image', url: ogImage.content});
    // Hero 图和大图
    document.querySelectorAll('img').forEach(img => {
        if (img.naturalWidth > 200 && img.naturalHeight > 200) {
            assets.push({type: 'image', url: img.src, w: img.naturalWidth, h: img.naturalHeight});
        }
    });
    // 背景图
    document.querySelectorAll('*').forEach(el => {
        const bg = getComputedStyle(el).backgroundImage;
        if (bg && bg !== 'none' && bg.includes('url(')) {
            const url = bg.match(/url\(["']?([^"')]+)["']?\)/);
            if (url) assets.push({type: 'background', url: url[1]});
        }
    });
    return JSON.stringify(assets.slice(0, 15));
})()
```

**素材选择优先级**：Logo > Hero image > Brand photo > OG image

从返回的资源中按优先级选择 2-3 张，下载到 `/tmp/style_assets/`。这些素材可在 Phase 3 中作为 `reference_image_url` 传给 API 辅助风格匹配。

#### Step 1d: 构建风格档案

使用 `style_extractor.py` 合并数据：

```python
import sys
sys.path.insert(0, "${CLAUDE_SKILL_DIR}/scripts")
from style_extractor import build_style_profile, save_style_profile

profile = build_style_profile(css_data, screenshot_analysis, url)
save_style_profile(profile, "/tmp/website_style_profile.json")
```

或者直接根据分析结果手动构建 JSON：

```json
{
    "source_url": "https://example.com",
    "colors": {
        "primary": "#1A1A2E",
        "secondary": "#16213E",
        "accent": "#E94560",
        "background": "#FFFFFF",
        "text_primary": "#1A1A2E",
        "palette_mood": "cool, sophisticated"
    },
    "typography": {
        "heading_style": "SF Pro Display, 700, tight letter-spacing",
        "body_style": "SF Pro Text, 400, standard line-height",
        "overall_feel": "modern, clean"
    },
    "design_traits": {
        "aesthetic": "minimalist corporate",
        "border_radius": "rounded",
        "shadow_style": "0px 4px 12px rgba(0,0,0,0.08)",
        "spacing": "generous whitespace",
        "gradient_use": false,
        "layout_style": "grid-based, symmetric"
    },
    "imagery_style": {
        "photo_style": "high-contrast studio photography",
        "mood_keywords": ["professional", "premium", "trustworthy"]
    },
    "brand_personality": "sophisticated, authoritative, modern tech",
    "screenshot_path": "/tmp/website_style_screenshot.png"
}
```

---

### Phase 2 — 风格确认

#### Step 2a: 展示风格概要（精简版）

向用户展示 top 3 颜色 + 2 字体 + 3 aesthetic 关键词：

```
网站风格分析: [source]

配色: #1A1A2E (深海军蓝) · #E94560 (活力珊瑚) · #FFFFFF (白)
字体: SF Pro Display (标题) · SF Pro Text (正文)
美学: minimalist · corporate · premium

完整风格档案可按需查看。
```

#### Step 2b: 风格到 Prompt 映射

不同的 aesthetic 关键词会翻译为不同的 prompt 指令：

| Aesthetic 关键词 | Prompt 指令映射 |
|-----------------|----------------|
| minimalist | "clean composition, ample negative space, simple geometric forms, restrained color palette" |
| bold | "high contrast, saturated colors, strong typography, impactful visual weight" |
| playful | "rounded shapes, bright accent colors, whimsical elements, casual arrangement" |
| corporate | "structured grid layout, professional photography, muted tones, formal composition" |
| luxury | "rich textures, gold/dark accents, elegant serif typography, dramatic lighting" |
| tech | "gradient overlays, geometric patterns, neon accents on dark background, futuristic elements" |
| organic | "natural textures, earth tones, flowing shapes, warm photography, handcrafted feel" |
| vibrant | "saturated multi-color palette, dynamic composition, energetic visual rhythm" |

这些映射在 Phase 3 构建 prompt 时自动注入 `content_description`。

#### Step 2c: 确认生成内容

图片类型和尺寸已在 Phase 0 中由用户选择的"设计什么 + 用在哪"自动确定。展示确认：

```
根据你的选择：
  设计类型: 社交媒体内容
  目标平台: Instagram
  → 自动选择: social_square (1080×1080)

内容描述: [需要用户补充，或根据网站内容自动生成]
```

**如果用户未描述图片内容**，追问：

| 选项 | 说明 |
|------|------|
| 品牌宣传 | 展示品牌形象、价值观 |
| 产品推广 | 突出特定产品或服务 |
| 活动促销 | 促销、打折、限时活动 |
| 内容营销 | 博客、文章、教程配图 |
| 其他 | 用户自定义描述 |

**风格偏好微调？**

| 选项 | 说明 |
|------|------|
| 完全匹配网站风格 (Recommended) | 严格复现网站的视觉语言 |
| 稍作变化 | 保留核心配色，允许创意发挥 |
| 仅用配色方案 | 只使用颜色，其他自由发挥 |
| 需要手动调整风格参数 | 让我修改具体的颜色、字体等 |

用户确认后进入 Phase 3。

---

### Phase 3 — 生成图片

#### Step 3a: 相关素材搜索（可选）

当用户的内容需求涉及特定主题（如"科技产品"、"美食"、"旅行"）时，可选执行：

1. 从用户的设计需求中提取关键词
2. 使用 WebSearch 搜索相关免费素材（Unsplash/Pexels）
3. 选择与目标风格最匹配的 1-2 张素材
4. 下载到 `/tmp/style_assets/`
5. 在生成时作为参考图传入

展示已收集的素材给用户确认：
```
已提取/搜索到以下素材：
  1. [logo] apple-logo.png — 网站 Logo
  2. [hero] hero-banner.jpg — 网站首屏大图
  3. [search] tech-abstract.jpg — Unsplash 搜索: "technology abstract"

这些素材将用于辅助风格匹配。确认使用，还是需要调整？
```

**此步骤为可选，不阻塞主流程。如果不需要额外素材，直接跳到 Step 3b。**

#### Step 3b: 写入生成配置

根据用户确认的内容，构建配置 JSON：

```bash
cat > /tmp/styled_image_config.json << 'CONFIG_JSON'
{
    "style_profile": {
        "source_url": "https://example.com",
        "colors": { ... },
        "typography": { ... },
        "design_traits": { ... },
        "imagery_style": { ... },
        "brand_personality": "...",
        "screenshot_path": "/tmp/website_style_screenshot.png"
    },
    "requests": [
        {
            "image_type": "hero_banner",
            "content_description": "A modern tech company homepage banner showcasing cloud computing services with abstract geometric shapes and circuit-like patterns"
        }
    ]
}
CONFIG_JSON
```

**content_description 构建规则：**
- 结合用户选择的用途 + 用户提供的具体描述
- 自动注入 Phase 2b 中 aesthetic 关键词对应的 prompt 指令
- 如果用户只选了用途类型没给具体描述，根据网站内容和品牌个性自动生成
- 描述应具体、可视化（描述画面内容而非抽象概念）
- 包含具体的视觉元素（形状、物体、场景）而不仅仅是概念词

#### Step 3c: Dry run 预览

```bash
cd ${CLAUDE_SKILL_DIR} && python3 scripts/generate_styled.py --from-json /tmp/styled_image_config.json --dry-run
```

**Dry-run checklist：**
- [ ] 颜色 hex 值是否正确注入
- [ ] 风格关键词是否匹配网站 aesthetic
- [ ] aesthetic → prompt 映射是否已注入 content_description
- [ ] 内容描述是否具体可视化
- [ ] 尺寸信息是否包含在 prompt 中
- [ ] 截图文件大小 < 5MB（超过则自动压缩到 1920px 宽）
- [ ] reference_image_url 路径是否有效

#### Step 3d: 生成图片

```bash
# 所有请求的图片:
cd ${CLAUDE_SKILL_DIR} && python3 scripts/generate_styled.py --from-json /tmp/styled_image_config.json -v

# 指定类型:
cd ${CLAUDE_SKILL_DIR} && python3 scripts/generate_styled.py --from-json /tmp/styled_image_config.json --types hero_banner,social_square -v

# 复用已有风格档案:
cd ${CLAUDE_SKILL_DIR} && python3 scripts/generate_styled.py --load-profile /path/to/style_profile.json --requests '[{"image_type":"hero_banner","content_description":"New product launch"}]' -v
```

生成流程：
- 自动验证截图文件（大小 < 5MB，否则自动压缩）
- 并发提交 API 任务（ThreadPoolExecutor，最多 8 并行）
- 轮询等待完成（5s 间隔，指数退避至 15s，最长约 10min）
- 生成图片到 `output/styled/<slug>/`
- 后处理完成后自动清理中间文件（使用网站背景色填充）
- 自动保存 `style_profile.json` 和 `manifest.json` 到输出目录

---

### Phase 4 — 审查与迭代

1. **读取每张生成的图片**：使用 Read 工具查看 `output/styled/<slug>/` 中的图片
2. **展示结果**：列出每张图片的路径、尺寸、类型
3. **提供迭代选项**：

**对生成结果满意吗？**

| 选项 | 说明 |
|------|------|
| 满意，全部保留 | 完成任务 |
| 重新生成部分图片 | 选择要重新生成的图片 |
| 调整内容描述后重新生成 | 修改画面内容要求 |
| 调整风格参数后重新生成 | 微调颜色、美学等风格参数 |
| 增加新的图片类型 | 额外生成其他类型的图片 |

根据用户选择进行迭代：
- 重新生成：`--types hero_banner` 指定类型
- 跳过后处理：`--skip-postprocess`
- 调整风格：修改 `/tmp/styled_image_config.json` 中的 `style_profile`
- 新增类型：在 `requests` 中追加新的图片请求
- 复用风格：`--load-profile output/styled/<slug>/style_profile.json`

---

## Error Handling

| 问题 | 解决方案 |
|------|---------|
| 网站无法访问 / JS 提取失败 | 用截图 + 视觉分析替代（`css_data = {}`），或使用 WebFetch 作为备选 |
| JS 提取返回空数据 | 检查页面是否完全加载，可能需要等待或滚动触发懒加载 |
| API 提交失败 | 检查 `config/api.yaml` 中的 headers |
| Task FAILED | 简化 prompt，移除冲突指令，减少风格约束 |
| Task TIMEOUT | 重试失败的图片类型 `--types xxx` |
| 生成的风格不匹配 | 增强 content_description 的具体性，或传入更好的截图参考 |
| 颜色提取不准 | 手动调整风格档案中的颜色值，重新 dry-run 验证 |
| 截图太大 (>5MB) | 自动压缩到 1920px 宽，或手动缩小后重试 |
| 后处理出错 | 使用 `--skip-postprocess` 保留原始图 |
| 用户上传截图而非 URL | `css_data = {}`，仅依赖视觉分析构建风格档案 |
| 素材搜索无结果 | 跳过素材搜索，直接用截图/风格档案生成 |

## Notes

- 网站截图作为 `reference_image_url` 传给 NANO-BANANA API，是最强的视觉锚点
- 风格档案和 manifest 自动保存到 `output/styled/<slug>/` 供复用
- 所有脚本（`api_client.py`、`postprocess.py`、`utils.py`）自包含在 `scripts/` 中
- 支持 `--load-profile` 复用已保存的风格档案，跳过重新提取
- Prompt 使用安全的字符串替换（非 `.format()`），防止用户输入中的 `{key}` 导致崩溃
- 颜色聚类使用 HSL 排序确保确定性结果
