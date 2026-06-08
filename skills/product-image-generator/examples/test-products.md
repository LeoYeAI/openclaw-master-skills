# Test Product Description / 测试商品描述

## Product 1: Wireless Earbuds / 无线蓝牙耳机

```markdown
# 无线蓝牙耳机 Pro

## 产品信息
**产品名称**: 无线蓝牙耳机 Pro
**产品类别**: 消费电子/音频设备
**价格区间**: 中高端 (¥299-399)

## 核心卖点
1. **主动降噪 (ANC)** - 最高 40dB 降噪深度
2. **长续航** - 单次 8 小时，总计 32 小时
3. **高音质** - 10mm 动圈，支持 AAC/SBC
4. **舒适佩戴** - 单耳仅 4.5g
5. **快速充电** - 充电 10 分钟，使用 2 小时
6. **蓝牙 5.3** - 稳定连接，低延迟

## 目标用户
- 通勤上班族
- 运动爱好者
- 学生群体
- 商务人士

## 产品规格
- 蓝牙版本：5.3
- 传输距离：10 米
- 电池容量：耳机 50mAh, 充电盒 400mAh
- 充电接口：USB-C
- 防水等级：IPX5
- 颜色：黑色、白色、蓝色

## 图片需求
**目标平台**: 亚马逊
**期望风格**: 科技感 (tech)
**图片数量**: 6-8 张
```

---

## Product 2: Portable Blender / 便携榨汁杯

```markdown
# 便携榨汁杯 Pro

## 产品信息
**产品名称**: 便携榨汁杯 Pro
**产品类别**: 小家电/厨房电器
**价格区间**: 中端 (¥199-299)

## 核心卖点
1. **300ml 容量** - 一人食完美份量
2. **USB-C 充电** - 充满可用 5 次
3. **304 不锈钢刀头** - 安全耐用
4. **一键启动** - 简单易用
5. **安全锁扣** - 防误触设计

## 目标用户
- 上班族
- 学生
- 健身爱好者
- 租房党

## 产品规格
- 容量：300ml
- 材质：食品级 PCTG + 304 不锈钢
- 电池：1500mAh
- 充电：USB-C
- 防水：IPX5
- 颜色：粉色、蓝色、白色

## 图片需求
**目标平台**: 淘宝
**期望风格**: 清新自然 (natural)
**图片数量**: 6 张
```

---

## Product 3: Luxury Watch / 高端手表

```markdown
# 经典机械手表

## 产品信息
**产品名称**: 经典机械手表
**产品类别**: 奢侈品/配饰
**价格区间**: 高端 (¥5000+)

## 核心卖点
1. **瑞士机芯** - 精准可靠
2. **蓝宝石镜面** - 防刮耐磨
3. **316L 精钢** - 坚固耐用
4. **50 米防水** - 日常生活防水
5. **经典设计** - 永恒优雅

## 目标用户
- 商务人士
- 手表收藏家
- 成功专业人士
- 礼品购买者

## 产品规格
- 机芯：瑞士自动机械
- 表壳：316L 精钢，40mm
- 镜面：蓝宝石水晶
- 防水：50 米
- 表带：真皮/精钢
- 颜色：银色、金色、黑色

## 图片需求
**目标平台**: Shopify
**期望风格**: 奢华 (luxury)
**图片数量**: 8 张
```

---

## How to Use These Test Files

### Method 1: Copy to Test Directory

```bash
# Copy any product above to test file
cp examples/test-products.md test-output/my-test.md

# Run the skill
/product-image-generator test-output/my-test.md
```

### Method 2: Direct Input

```bash
# Run skill and paste content directly
/product-image-generator

# Then paste any product description from above
```

### Method 3: With Options

```bash
# Specify style and platform
/product-image-generator examples/test-products.md \
  --style tech \
  --platform amazon
```

### Method 4: With Reference Image

```bash
# If you have a reference image
/product-image-generator examples/test-products.md \
  --ref your-style-guide.png \
  --style minimal
```
