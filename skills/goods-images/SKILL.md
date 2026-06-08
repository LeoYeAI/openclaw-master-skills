---
name: goods-images
description: "Use when the user wants to generate product detail images or carousel/main images for e-commerce platforms like Taobao. Triggers on keywords like 商品图, 详情图, 产品图, 电商图, 淘宝图, 轮播图, 主图, or when user uploads a product photo and asks for marketing images."
---

# 商品详情图 & 轮播图生成 Skill

## Overview

根据用户提供的商品图片和描述，生成电商平台（淘宝/天猫/京东）的 **商品详情图**（9张）和/或 **商品轮播图**（5张）。

## 核心原则

1. **商品图必须保真。** 用户提供的商品图片中的图案、文字、Logo、颜色不得有任何改变。详情图和轮播图是在原图基础上做排版设计和文案包装，不是重新生成商品。
2. **用户零操作。** 全部后台自动完成，直接在对话中输出图片结果。不打开可见浏览器窗口，不让用户手动导出。
3. **环境自适应。** 优先使用 `run_command` + Python PIL 精确渲染中文文字，如果环境不支持则自动降级到 `generate_image` 方案。

## When to Use

- 用户上传了商品图片，要求生成详情图或轮播图
- 用户提供了商品文字描述，要求生成电商图片
- 用户提到"淘宝详情图"、"商品图"、"电商图"、"轮播图"、"主图"等关键词

## 需要收集的信息

| 必须 | 轮播图额外需要 | 可选 |
|------|-------------|------|
| 商品图片（至少1张） | 品牌 Logo（文字或图片） | 规格参数（尺寸/材质等） |
| 商品描述 | 活动内容（如"1件9折"） | 品牌故事 |
| | | 核心卖点 |

**输入处理**：
- 有图片 → 观察图片中的产品，推断品类、外观、卖点
- 仅文字 → 从描述中提取信息，用 `generate_image` 先生成 1 张商品图
- 信息不足时追问，**最多补问 1 轮**，其余从图片和描述中推断

**⚠️ 用户可能只要轮播图或只要详情图。** 如果用户明确说只要其中一种，跳过另一种。不确定时默认两种都生成。

## ⚠️ 执行清单（必读）

**你必须生成 14 张图片，不是 1 张！** 按以下步骤逐一执行：

### 轮播图（5张）
1. 用 `generate_image` 生成模特图1（传入用户原图作为 ImagePaths）
2. 用 `generate_image` 生成模特图2（传入用户原图作为 ImagePaths）
3. 用 `generate_image` 生成模特图3（传入用户原图作为 ImagePaths）
4. 用 PIL 脚本或 `generate_image` 在模特图上叠加 Logo + 活动条 + 卖点关键词，生成 carousel_01 ~ carousel_04
5. 用 PIL 脚本或 `generate_image` 生成 carousel_05（白底图，仅 Logo）

### 详情图（9张）
6. `generate_image` → 主图封面（传入原图）
7. `generate_image` → 卖点1（传入原图）
8. `generate_image` → 卖点2（传入原图）
9. `generate_image` → 卖点3（传入原图）
10. `generate_image` → 细节标注图（传入原图）
11. `generate_image` → 穿着/使用场景
12. `generate_image` → 产品参数表（传入原图）
13. `generate_image` → 尺码/规格表
14. `generate_image` → 售后保障

### 关键规则
- **每张图都要单独调用一次 `generate_image`**，不要试图一次生成多张
- **必须传入用户原图作为 ImagePaths**，否则 AI 会画出不一样的商品
- **Logo 和活动文字不要写在 generate_image 的 prompt 里**（AI 画中文会变形），应该用 PIL 后处理
- **背景不要纯白**，要有场景感

---

## 流程

```
输入 → 商品分析 → 风格判断 → 并行生成（详情图 + 轮播图）→ 直接输出
```

---

## Part 1: 商品分析

从用户输入提取：

| 分析项 | 来源 |
|-------|------|
| 商品品类 | 图片观察 + 描述（上衣/裤子/鞋/配饰/3C/家居/食品...） |
| 核心卖点（2-4个） | 描述 + 推断 |
| 目标人群 | 描述 + 推断（儿童/成人/男/女） |
| 商品风格 | 图片观察（潮酷/日系/运动/甜美/简约/商务...） |
| 卖点关键词 | 从描述中提取 2-3 个核心词（如"加绒"、"保暖"） |

## Part 2: 风格判断

| 风格 | 适用品类 | 配色方案 |
|------|---------|---------|
| **简约高端** | 数码3C、高端家居、护肤品、商务服饰 | 背景 #fafafa, 文字 #1a1a1a, 点缀 #c9a96e |
| **营销促销** | 食品零食、日用百货、平价商品 | 背景 #fff, 强调 #e63946, 点缀 #ff6b35 |
| **种草生活** | 时尚服饰、美妆、母婴、童装 | 背景 #fdf8f3, 文字 #3d3024, 点缀 #c17a50 |
| **科技未来** | 电子产品、智能设备、数码配件 | 背景 #0a0a0a, 文字 #fff, 点缀 #00d4ff |

---

## Part 3: 轮播图生成（5张）

### 规范

- 尺寸：**800×800 像素（正方形）**
- 5 张：3 张模特/场景图 + 1 张原图场景化 + 1 张商品特写
- 左上角：品牌 Logo
- **前 4 张左侧显示卖点关键词**（从描述提取，如"加绒"、"保暖"），半透明背景条+白色文字
- 前 4 张底部：促销活动条
- **背景不要纯白/纯灰**，应配合商品风格

### Step A: 生成模特/场景图

用 `generate_image` 生成 3 张图，**必须传入用户原图作为 ImagePaths**。

**⚠️ 根据商品品类决定构图和主体：**

| 品类 | 主体 | 构图 | Prompt 关键词 |
|------|------|------|-------------|
| 上衣（卫衣/T恤/外套） | 模特 | 半身照（头到臀） | `upper body shot, waist-up, cropped at hip` |
| 裤子/裙子 | 模特 | 下半身 | `lower body focus, hip to feet` |
| 全身套装/连衣裙 | 模特 | 全身照 | `full body shot` |
| 鞋子 | 脚部特写 | 特写 | `close-up of shoes on feet, ground level angle` |
| 帽子/围巾 | 模特 | 头肩特写 | `close-up, head and shoulders` |
| 数码3C/家居 | 产品 | 场景摆拍 | `product in lifestyle setting, styled flat lay` |
| 食品 | 产品 | 美食摄影 | `food photography, styled plating, appetizing` |

**⚠️ 背景配合商品风格：**

| 风格 | 背景场景 | Prompt 参考 |
|------|---------|------------|
| 潮酷/街头 | 涂鸦墙、砖墙、城市夜景 | `urban concrete wall with graffiti`, `city night lights bokeh` |
| 日系/文艺 | 庭院、咖啡店、公园 | `cozy cafe interior`, `park with warm sunlight` |
| 运动活力 | 操场、户外阳光 | `playground`, `outdoor bright sunlight` |
| 甜美可爱 | 花墙、游乐场 | `pink flower wall`, `pastel balloons` |
| 简约高端 | 大理石台面、极简空间 | `marble surface`, `minimal white interior` |
| 科技感 | 暗色桌面、霓虹灯 | `dark desk setup`, `neon accent lighting` |

**Prompt 模板（服饰类）**：
```
A [age]-year-old Asian [boy/girl/man/woman] model wearing [商品英文描述],
[姿态描述], [场景背景],
[构图方式] focusing on the [商品],
e-commerce fashion photography,
[lighting], professional catalog style, high resolution
```

**Prompt 模板（非服饰类）**：
```
Product photography of [商品英文描述],
[场景/摆放方式], [背景描述],
e-commerce product photography,
soft studio lighting, professional, high resolution, 800x800
```

3 张分别用不同姿态/角度和背景。

### Step B: 叠加 Logo + 活动条 + 卖点关键词

**Agent 应按以下优先级自动选择方案：**

#### 方案 1（首选）：`run_command` + Python PIL

先测试环境：
```bash
python3 -c "from PIL import Image; print('ok')" 2>/dev/null || pip install Pillow -q
```

如果可用，用以下脚本精确叠加中文 Logo、活动条和卖点关键词：

```python
from PIL import Image, ImageDraw, ImageFont
import os

CANVAS = 800
FONT_PATHS = [
    '/System/Library/Fonts/PingFang.ttc',                        # macOS
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',    # Linux Noto
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',    # Linux Noto alt
    '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',  # Linux Droid
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',             # Linux 文泉驿
]

def get_font(size, bold=False):
    for fp in FONT_PATHS:
        if os.path.exists(fp):
            try:
                idx = 1 if bold and fp.endswith('.ttc') else 0
                return ImageFont.truetype(fp, size, index=idx)
            except:
                try: return ImageFont.truetype(fp, size, index=0)
                except: continue
    return ImageFont.load_default()

def add_overlay(img_path, output_path, logo_text,
                promos=None, keywords=None,
                tag_text=None, tag_sub='店铺折扣叠加官方立减'):
    """
    promos:   活动列表, e.g. ['1件9折', '3件85折'] — 支持 1-N 条
    keywords: 卖点关键词, e.g. ['加绒', '保暖'] — 左侧竖排显示
    tag_text: 标签文字, e.g. '秋冬上新' — 为 None 时根据当前月份自动判断
    """
    img = Image.open(img_path).convert('RGBA')
    ratio = max(CANVAS / img.width, CANVAS / img.height)
    img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
    left = (img.width - CANVAS) // 2
    img = img.crop((left, 0, left + CANVAS, CANVAS))

    overlay = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # ===== Logo（左上角 + 阴影）=====
    lf = get_font(32, bold=True)
    for dx, dy in [(2,2),(1,1)]:
        draw.text((24+dx, 20+dy), logo_text, fill=(0,0,0,80), font=lf)
    draw.text((24, 20), logo_text, fill=(255,255,255,250), font=lf)

    # ===== 卖点关键词（左侧竖排）=====
    if keywords:
        kf = get_font(36, bold=True)
        total_h = len(keywords) * 50
        ky = (CANVAS - total_h) // 2 - 40
        for kw in keywords:
            bb = draw.textbbox((0,0), kw, font=kf)
            kw_w = bb[2] - bb[0]
            draw.rounded_rectangle([16, ky-4, 16+kw_w+24, ky+42],
                                   radius=6, fill=(0,0,0,100))
            draw.text((29, ky+1), kw, fill=(0,0,0,60), font=kf)
            draw.text((28, ky), kw, fill=(255,255,255,250), font=kf)
            ky += 50

    # ===== 底部活动条 =====
    if promos:
        # 自动判断季节标签
        if tag_text is None:
            import datetime
            m = datetime.datetime.now().month
            tag_text = {1:'年货节',2:'开春上新',3:'春季上新',4:'春季上新',
                        5:'初夏上新',6:'夏季上新',7:'夏季上新',8:'秋季上新',
                        9:'秋季上新',10:'秋冬上新',11:'秋冬上新',12:'年终大促'}.get(m,'新品上市')

        h = 95; th = 32; y0 = CANVAS - h
        # 过渡阴影
        for i in range(30):
            draw.rectangle([0, y0-30+i, CANVAS, y0-29+i], fill=(0,0,0,int(i*6)))
        # 白色标签栏
        draw.rectangle([0, y0, CANVAS, y0+th], fill=(255,255,255,250))
        tf = get_font(14, bold=True)
        tb = draw.textbbox((0,0), tag_text, font=tf)
        tw = tb[2]-tb[0]+28
        draw.rounded_rectangle([14, y0+4, 14+tw, y0+4+24], radius=5, fill=(56,161,105))
        draw.text((28, y0+7), tag_text, fill='white', font=tf)
        sf = get_font(12)
        draw.text((14+tw+14, y0+9), tag_sub, fill=(170,170,170), font=sf)

        # 红色主条（渐变）
        my = y0 + th
        for x in range(CANVAS):
            r = min(int(210+20*x/CANVAS), 230)
            draw.line([(x,my),(x,CANVAS)], fill=(r, min(int(50+8*x/CANVAS),58), 55))

        # 活动文字（数字大 42px，文字小 22px，支持 N 条活动）
        nf = get_font(42, bold=True)
        xf = get_font(22, bold=True)
        def measure(s):
            return sum(draw.textbbox((0,0),c,font=nf if c.isdigit() else xf)[2]
                       -draw.textbbox((0,0),c,font=nf if c.isdigit() else xf)[0]+1 for c in s)
        sep_w = 40
        total_w = sum(measure(p) for p in promos) + sep_w * (len(promos) - 1)
        sx = (CANVAS - total_w) // 2
        cy = my + (CANVAS - my - 42) // 2

        for idx, promo in enumerate(promos):
            for c in promo:
                f = nf if c.isdigit() else xf
                yo = 0 if c.isdigit() else 16
                bb = draw.textbbox((0,0), c, font=f)
                draw.text((sx+1, cy+yo+1), c, fill=(0,0,0,40), font=f)
                draw.text((sx, cy+yo), c, fill=(255,255,255), font=f)
                sx += bb[2] - bb[0] + 1
            if idx < len(promos) - 1:
                sep_x = sx + sep_w // 2
                draw.line([(sep_x, cy+6), (sep_x, cy+38)], fill=(255,255,255,100), width=2)
                sx += sep_w

    img = Image.alpha_composite(img, overlay)
    img.convert('RGB').save(output_path, quality=95)
    print(f'已生成: {output_path}')
```

**调用示例**：
```python
logo = '品牌名'
promos = ['1件9折', '3件85折']  # 支持 1-N 条
keywords = ['加绒', '保暖']     # 从商品描述提取

add_overlay('model1.png', 'carousel_01.jpg', logo, promos, keywords)
add_overlay('model2.png', 'carousel_02.jpg', logo, promos, keywords)
add_overlay('model3.png', 'carousel_03.jpg', logo, promos, keywords)
add_overlay('product.jpg', 'carousel_04.jpg', logo, promos, keywords)
add_overlay('product.jpg', 'carousel_05.jpg', logo)  # 白底图，无活动条/卖点
```

**⚠️ 执行完成后删除中间产物：**
```bash
rm -f /tmp/product-details/overlay.py
```

#### 方案 2（降级）：`generate_image` 直接生成

如果 `run_command` 不可用，把模特图传入 `generate_image` 的 `ImagePaths`，在 prompt 中描述叠加布局。中文文字可能不完美但可接受。

#### 方案 3（最后备选）：`browser_subagent` + HTML

用 HTML/CSS 精确渲染后截图。用户会看到浏览器窗口，体验较差，仅作最终兜底。

### 5 张轮播图内容

1. 模特/场景 正面（背景A）+ Logo + 卖点 + 活动条
2. 模特/场景 侧面（背景B）+ Logo + 卖点 + 活动条
3. 模特/场景 另一角度（背景C）+ Logo + 卖点 + 活动条
4. 商品原图场景化 + Logo + 卖点 + 活动条
5. 商品特写/白底图 + Logo（无活动条、无卖点）

---

## Part 4: 详情图生成（9张）

### 编排规划

从以下类型中选择 9 张（根据品类调整）：

| 优先级 | 类型 | 适用品类 |
|-------|------|---------|
| **★★★ 必选** | 主图封面 | 全部 |
| **★★☆ 建议** | 核心卖点图（2-3张） | 全部 |
| **★★☆ 建议** | 细节标注图 | 全部 |
| **★★☆ 建议** | 使用场景/穿着场景 | 服饰/家居/食品 |
| **★★☆ 建议** | 规格参数表 | 全部 |
| **★☆☆ 可选** | 尺码对照表 | 服饰/鞋类 |
| **★☆☆ 可选** | 包装清单 | 3C/家居/礼品 |
| **★☆☆ 可选** | 对比图/竞品优势 | 全部 |
| **★☆☆ 可选** | 搭配推荐 | 服饰 |
| **★★☆ 建议** | 售后保障 | 全部 |

### 详情图生成方式

**用 `generate_image` 逐张生成。** 每张传入用户原图作为 `ImagePaths`。

**Prompt 通用结构**：
```
E-commerce product detail page image, 790px wide, approximately 1100px tall.
[Layout: what's shown, where elements are positioned]
[Chinese text content as decorative elements]
Product: [商品描述]
Style: [风格配色], professional Taobao/Tmall product detail page design.
```

### 9 张详情图 Prompt 模板

**⚠️ 以下模板中的 `[占位符]` 需根据实际商品替换！**

#### 1. 主图封面
```
E-commerce hero banner, 790x1100px.
Large product photo centered, product: [商品描述].
Top: large bold Chinese title "[标题2-6字]".
Subtitle: "[副标题一句话]".
Season tag: "[年份+季节]新款".
Style: [风格配色], premium e-commerce design.
```

#### 2-4. 核心卖点图（每个卖点一张）
```
Product feature highlight page, 790x1100px.
[左右分栏/上下分栏] layout for: [商品描述].
Feature title: "[卖点标题]" in large bold text.
Description: "[卖点说明1-3行]".
[产品细节照片/图标插画] showing the feature.
Style: [风格配色].
```

#### 5. 细节标注图
```
Product detail annotation page, 790x1100px.
Center: full product photo of [商品描述].
4 annotation callouts with connecting lines:
  - "[细节1]" pointing to [部位1]
  - "[细节2]" pointing to [部位2]
  - "[细节3]" pointing to [部位3]
  - "[细节4]" pointing to [部位4]
Clean background, professional annotation style.
```

#### 6. 使用场景/穿着场景
```
Lifestyle scene page, 790x1100px.
Title: "[场景标题]".
[模特穿着/产品使用] photo in [场景描述].
Subtitle: "[副标题]".
Style: [风格配色], aspirational lifestyle design.
```

#### 7. 规格参数表
```
Product specification page, 790x1100px, clean table layout.
Title: "产品参数".
Table rows:
  品名: [商品名]
  [面料/材质]: [具体信息]
  [适用人群]: [具体信息]
  [颜色]: [具体信息]
  [其他参数...]
Small product thumbnail below.
Style: [风格配色], clean grid.
```

#### 8. 尺码/规格对照表（服饰/鞋类）
```
Size chart page, 790x1100px.
Title: "尺码参考".
Table: [根据品类自动生成合适的尺码范围和度量项]
Note: "因测量方式不同，尺寸可能有1-3cm误差".
Size guide illustration.
Style: warm, parent-friendly design.
```

**⚠️ 尺码范围应根据商品品类自动调整：**
- 童装：110-160
- 成人男装：S/M/L/XL/2XL/3XL
- 成人女装：XS/S/M/L/XL/2XL
- 鞋类：36-45（或对应码）
- 非服饰品类跳过此图，替换为"包装清单"或"对比优势"

#### 9. 售后保障
```
After-sales guarantee page, 790x1100px.
Title: "售后保障".
4 guarantee icons in 2x2 grid:
  - 正品保证（shield icon）
  - 7天无理由退换（return icon）
  - 极速退款（refund icon）
  - 运费险（shipping icon）
Bottom: "品质之选 · 放心购买".
Style: trustworthy, warm, [风格配色].
```

---

## 输出规范

### 文件保存路径

所有生成的图片保存到 `/tmp/product-details/`：

| 图片类型 | 文件名 |
|---------|--------|
| 模特/场景原图 | `model1.png`, `model2.png`, `model3.png` |
| 轮播成品图 | `carousel_01.jpg` ~ `carousel_05.jpg` |
| 详情图 | `detail_01.png` ~ `detail_09.png` |
| 用户原图副本 | `product.jpg` |

### 展示方式

用 `view_file` 在对话中直接展示所有图片：

1. 先展示 5 张轮播图
2. 再展示 9 张详情图
3. 最后给出图片清单总结表格

---

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| `generate_image` 生成的图片不符合预期 | 调整 prompt 重新生成，最多重试 2 次 |
| PIL 不可用 | 自动降级到 `generate_image` 方案 |
| 用户原图分辨率过低 | 提示用户，但仍继续生成 |
| generate_image 调用失败 | 跳过该张图，继续生成其余图片，最后告知用户 |

---

## 注意事项

| ✅ 正确 | ❌ 错误 |
|---------|---------|
| `generate_image` 传入用户原图作为 ImagePaths | 不传原图导致商品外观偏差 |
| 所有中文文案由 AI 根据商品分析自动生成 | 要求用户自己写文案 |
| 模特/场景图背景有场景感 | 纯白或纯灰背景 |
| 直接在对话中输出图片 | 让用户手动去网页导出 |
| PIL 首选、generate_image 降级 | 硬依赖某个方案不做兜底 |
| 所有图片风格统一 | 每张图风格不一样 |
| 根据品类调整构图/尺码/场景 | 所有商品用同一套模板 |
| 卖点关键词从描述自动提取 | 遗漏用户描述中的核心卖点 |
| tag_text 根据季节自动生成 | 硬编码"秋冬上新" |
