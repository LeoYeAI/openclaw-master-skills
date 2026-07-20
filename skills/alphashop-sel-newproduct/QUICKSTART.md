# 快速开始指南

## 第一步：获取 API 凭证

本 skill 需要 AlphaShop/遨虾平台的 API 凭证。

### 如何获取

1. **联系平台方**
   - 内部用户：联系 AlphaShop/遨虾 平台管理员
   - 外部用户：访问 https://www.alphashop.cn 或相关平台申请

2. **提供必要信息**
   - 公司/团队信息
   - 使用场景说明
   - 预期调用量

3. **获取凭证**
   - `ALPHASHOP_ACCESS_KEY` - API 访问密钥
   - `ALPHASHOP_SECRET_KEY` - API 密钥

## 第二步：配置凭证

### 方式A：环境变量（临时使用）

```bash
export ALPHASHOP_ACCESS_KEY='你的AccessKey'
export ALPHASHOP_SECRET_KEY='你的SecretKey'
```

或使用 `.env` 文件：

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入真实凭证
vim .env

# 加载环境变量
source .env
```

### 方式B：OpenClaw 配置（推荐）

编辑 OpenClaw 配置文件（通常是 `~/.openclaw/openclaw.json`）：

```json
{
  "skills": {
    "entries": {
      "alphashop-sel-newproduct": {
        "env": {
          "ALPHASHOP_ACCESS_KEY": "你的AccessKey",
          "ALPHASHOP_SECRET_KEY": "你的SecretKey"
        }
      }
    }
  }
}
```

## 第三步：运行测试

### 基础测试

```bash
python3 scripts/selection.py report \
  --keyword "phone" \
  --platform "amazon" \
  --country "US"
```

### 带筛选条件

```bash
python3 scripts/selection.py report \
  --keyword "yoga pants" \
  --platform "amazon" \
  --country "US" \
  --listing-time "90" \
  --min-price 15 \
  --max-price 50 \
  --min-sales 10 \
  --min-rating 3.5
```

## 常见问题

### Q: 提示 "缺少必需的环境变量"？

A: 说明凭证未正确配置。请检查：
1. 环境变量是否已设置：`echo $ALPHASHOP_ACCESS_KEY`
2. OpenClaw 配置是否正确
3. 凭证是否有效

### Q: 提示 "KEYWORD_ILLEGAL" 错误？

A: 关键词必须使用关键词查询API返回的关键词。建议：
1. 先调用关键词查询API获取关键词列表
2. 从返回结果中选择关键词使用

### Q: 提示 "PRODUCT_RECALL_EMPTY" 错误？

A: 筛选条件太严，导致没有符合条件的商品。解决方案：
1. 放宽价格区间（如 1-500）
2. 放宽销量要求（如 0-10000）
3. 降低评分门槛（如 0-5.0）

## 下一步

查看完整文档：[SKILL.md](SKILL.md)
