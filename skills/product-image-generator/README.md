# Product Image Generator / 商品图生成器

A comprehensive skill for generating professional product images for e-commerce platforms.

一个用于生成电商平台商品图片的综合技能。

---

## 快速开始 / Quick Start

```bash
# 基础用法 / Basic usage
/product-image-generator product-description.md

# 指定风格和平台 / Specify style and platform
/product-image-generator product.md --style minimal --platform amazon

# 直接输入内容 / Direct input
/product-image-generator
[粘贴商品描述]
```

---

## 功能特性 / Features

### 8 种视觉风格 / 8 Visual Styles

| 风格 | 描述 | 适用产品 |
|------|------|----------|
| minimal | 简洁专业，纯白背景 | 电子产品、配件 |
| premium | 高端优雅，精致灯光 | 奢侈品、化妆品 |
| lifestyle | 场景化，自然使用环境 | 家居、服装 |
| bold | 高对比度，鲜艳活力 | 运动产品、游戏 |
| soft | 柔和灯光，温暖色调 | 婴儿用品、护肤品 |
| tech | 未来感，科技感 | 数码产品、智能设备 |
| natural | 有机自然，环保风格 | 天然产品、食品 |
| luxury | 奢华戏剧性， rich tones | 珠宝、名表、高端时尚 |

### 6 种场景类型 / 6 Scene Types

- **studio** - 专业影棚，纯白/渐变背景
- **lifestyle** - 真实使用场景
- **contextual** -  staged 环境展示
- **exploded** - 组件分解展示
- **comparison** - 前后对比/竞品对比
- **infographic** - 信息图表，文字说明

### 7 个电商平台 / 7 E-commerce Platforms

- **Amazon** - 亚马逊（严格的主图要求）
- **Shopify** - 独立站（灵活品牌化）
- **eBay** - 易趣（拍卖/固定价格）
- **Etsy** - 手工艺品
- **Taobao** - 淘宝（信息密集型）
- **JD** - 京东（品质导向）
- **Pinduoduo** - 拼多多（性价比导向）

---

## 使用示例 / Examples

### 示例 1：亚马逊电子产品

```bash
/product-image-generator wireless-earbuds.md \
  --style tech \
  --scene studio \
  --platform amazon
```

### 示例 2：Shopify 家居用品

```bash
/product-image-generator home-decor.md \
  --style lifestyle \
  --scene contextual \
  --platform shopify
```

### 示例 3：淘宝美妆产品

```bash
/product-image-generator cosmetics.md \
  --style soft \
  --scene infographic \
  --platform taobao
```

---

## 输出文件结构 / Output Structure

```
product-images/{product-slug}/
├── source-article.md           # 源商品描述
├── analysis.md                 # 产品分析
├── outline-strategy-a.md       # 策略 A：产品聚焦
├── outline-strategy-b.md       # 策略 B：场景聚焦
├── outline-strategy-c.md       # 策略 C：信息聚焦
├── outline.md                  # 最终选定方案
├── prompts/                    # 生成提示词
│   ├── 01-hero-slug.md
│   ├── 02-angle-slug.md
│   └── ...
└── images/                     # 生成的图片
    ├── 01-hero-slug.png
    ├── 02-angle-slug.png
    └── ...
```

---

## 工作流程 / Workflow

```
输入商品描述
    ↓
Step 0: 加载偏好设置 (EXTEND.md)
    ↓
Step 1: 分析产品 → analysis.md
    ↓
Step 2: 确认 1 - 产品理解 ⚠️
    ↓
Step 3: 生成 3 种策略方案
    ↓
Step 4: 确认 2 - 选择策略&风格&平台 ⚠️
    ↓
Step 5: 生成图片（顺序生成，保持一致性）
    ↓
Step 6: 完成报告
```

---

## 偏好设置 / Preferences

首次使用会自动引导设置偏好：

- **默认平台** - amazon/shopify/taobao 等
- **默认风格** - minimal/premium/lifestyle 等
- **水印设置** - 启用/禁用
- **语言偏好** - 中文/英文/自动

偏好设置保存位置：
- 项目级：`.teamclaw-skills/product-image-generator/EXTEND.md`
- 用户级：`$HOME/.teamclaw-skills/product-image-generator/EXTEND.md`

---

## 参考文档 / Documentation

| 文档 | 内容 |
|------|------|
| `references/presets/*.md` | 8 种风格详细定义 |
| `references/elements/scene-guide.md` | 场景类型指南 |
| `references/platforms/*.md` | 各平台要求详解 |
| `references/workflows/*.md` | 工作流程模板 |
| `examples/*.md` | 示例商品描述 |

---

## 与 Xiaohongshu 图片生成器对比

| 特性 | Xiaohongshu 生成器 | 商品图生成器 |
|------|-------------------|-------------|
| 目标平台 | 小红书 | 亚马逊/Shopify/淘宝等 |
| 输出类型 | 信息图表系列 | 产品展示图 |
| 风格数量 | 10 种 | 8 种 |
| 布局类型 | 8 种 | 6 种场景 |
| 平台合规 | 无特殊要求 | 严格平台要求 |
| 主要用途 | 内容种草 | 电商销售 |

---

## 最佳实践 / Best Practices

### 商品描述准备

1. **清晰的产品名称和类别**
2. **3-5 个核心卖点**
3. **目标用户画像**
4. **使用场景描述**
5. **规格参数（如适用）**

### 平台选择建议

- **Amazon** - 主图必须纯白背景，无文字
- **Shopify** - 灵活，可品牌化
- **Taobao/JD** - 可包含信息图表
- **Etsy** - 重视手工/场景展示

### 图片数量建议

- **简单产品** - 3-4 张
- **中等复杂度** - 5-6 张
- **复杂产品** - 7-8 张
- **系统/套装** - 8-10 张

---

## 常见问题 / FAQ

**Q: 可以生成模特展示图吗？**
A: 可以，在 lifestyle 场景中指定人物使用场景。

**Q: 主图符合亚马逊要求吗？**
A: 使用 `--platform amazon` 和 `--scene studio` 自动生成合规主图。

**Q: 可以批量生成多个产品吗？**
A: 每次运行处理一个产品，可以并行运行多个实例。

**Q: 如何保持多个产品图片风格一致？**
A: 使用相同的 `--style` 和偏好设置。

---

## 更新日志 / Changelog

### v1.0.0 (2026-03-02)
- 初始版本发布
- 支持 8 种视觉风格
- 支持 6 种场景类型
- 支持 7 个电商平台
- 完整的工作流程和确认机制
