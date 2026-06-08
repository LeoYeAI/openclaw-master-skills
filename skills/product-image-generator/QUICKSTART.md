# Quick Start Guide / 快速入门

## 5 分钟快速测试 Product Image Generator

### 前置准备 (1 分钟)

```bash
# 1. 进入你的项目目录
cd /your/project/path

# 2. 创建技能链接
mkdir -p .teamclaw-skills
ln -s ../../skills/product-image-generator .teamclaw-skills/

# 3. 验证链接
ls -la .teamclaw-skills/
```

### 运行测试 (3 分钟)

**方式 A: 使用测试文件**

```bash
# 运行技能，使用内置测试文件
/product-image-generator skills/product-image-generator/examples/test-products.md
```

**方式 B: 直接输入内容**

```bash
# 1. 运行技能
/product-image-generator

# 2. 粘贴以下内容:

产品名称：无线蓝牙耳机

核心卖点:
- 主动降噪 40dB
- 续航 32 小时
- 蓝牙 5.3
- 快速充电

目标用户：通勤族、学生

期望风格：科技感
平台：亚马逊
```

**方式 C: 指定选项**

```bash
/product-image-generator product.md \
  --style tech \
  --platform amazon \
  --scene studio
```

### 查看结果 (1 分钟)

生成的文件结构：

```
product-images/{product-slug}/
├── analysis.md              # 产品分析
├── outline.md               # 最终方案
├── prompts/                 # 生成提示词
│   ├── 01-hero-xxx.md
│   ├── 02-angle-xxx.md
│   └── ...
└── images/                  # 生成的图片
    ├── 01-hero-xxx.png
    ├── 02-angle-xxx.png
    └── ...
```

---

## 完整工作流程示例

### 示例：生成蓝牙耳机商品图

**Step 1: 准备商品描述**

```markdown
# 无线蓝牙耳机 Pro

## 卖点
- 主动降噪
- 32 小时续航
- 舒适佩戴

## 用户
通勤族、运动爱好者

## 平台
亚马逊

## 风格
科技感
```

**Step 2: 运行技能**

```bash
/product-image-generator earbuds.md
```

**Step 3: 回答确认问题**

技能会问你一些问题来更好地理解需求：

1. 主要卖点是什么？（可多选）
2. 目标客户是谁？
3. 主要使用场景？

**Step 4: 选择方案**

技能会生成 3 种策略方案供你选择：

- **方案 A**: 产品聚焦型 - 简洁专业
- **方案 B**: 场景融入型 - 生活化
- **方案 C**: 信息传达型 - 功能说明

**Step 5: 等待生成**

技能会自动生成所有图片，并保持风格一致性。

---

## 常用命令速查

### 基础命令

```bash
# 自动生成（风格自动选择）
/product-image-generator product.md

# 指定风格
/product-image-generator product.md --style minimal
/product-image-generator product.md --style premium
/product-image-generator product.md --style lifestyle
```

### 平台指定

```bash
# 亚马逊（主图纯白背景）
/product-image-generator product.md --platform amazon

# 淘宝（信息图风格）
/product-image-generator product.md --platform taobao

# Shopify（品牌化）
/product-image-generator product.md --platform shopify
```

### 参考图

```bash
# 使用参考图
/product-image-generator product.md --ref style.png

# 多张参考图
/product-image-generator product.md --ref style.png --ref competitor.jpg
```

### 组合使用

```bash
/product-image-generator product.md \
  --style tech \
  --scene studio \
  --platform amazon \
  --ref brand-guide.png
```

---

## 风格选择指南

| 产品类型 | 推荐风格 | 推荐场景 |
|----------|----------|----------|
| 电子产品 | tech, minimal | studio |
| 家居用品 | lifestyle, natural | lifestyle |
| 美妆护肤 | soft, premium | studio + lifestyle |
| 运动产品 | bold, lifestyle | lifestyle |
| 奢侈品 | luxury, premium | studio |
| 母婴产品 | soft, natural | lifestyle |
| 食品 | natural, minimal | studio |
| 服装配饰 | lifestyle, premium | lifestyle |

---

## 平台要求速查

| 平台 | 主图要求 | 图片数量 |
|------|----------|----------|
| Amazon | 纯白背景，无文字 | 最多 9 张 |
| Shopify | 灵活，可品牌化 | 无限 |
| eBay | 建议白底 | 最多 12 张 |
| Etsy | 生活化，故事性 | 最多 10 张 |
| Taobao | 可信息图 | 最多 15 张 |
| JD | 专业清晰 | 最多 15 张 |
| Pinduoduo | 突出性价比 | 最多 10 张 |

---

## 故障排除

### 问题：技能无法运行

**解决**：
```bash
# 检查技能链接
ls -la .teamclaw-skills/

# 应该看到 product-image-generator 链接
```

### 问题：图片风格不一致

**解决**：
- 确保使用相同的 `--style` 参数
- 使用 `--ref` 提供参考图
- 检查是否在同一会话中生成

### 问题：不符合平台要求

**解决**：
- 明确指定 `--platform` 参数
- 查看 `references/platforms/` 中的详细要求
- 主图必须遵守平台规定（如亚马逊纯白背景）

---

## 下一步

- 查看完整文档：`SKILL.md`
- 查看风格预设：`references/presets/`
- 查看平台要求：`references/platforms/`
- 使用测试文件：`examples/test-products.md`
