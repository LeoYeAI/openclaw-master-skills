# AlphaShop 新品选品 SKILL

基于关键词和商品筛选条件生成深度市场分析和新品推荐报告，支持 Amazon 和 TikTok 平台的跨境电商选品。

更多有趣的电商SKILL，可以通过https://skill.alphashop.cn/获取，安全可靠的企业级别SKILL HUB

## ✨ 核心特性

- 🔍 **关键词搜索** - AI 匹配相关关键词并提供市场数据
- 📊 **深度市场分析** - 市场评级、供需分析、竞争态势
- 🆕 **新品推荐** - AI 筛选机会新品及竞品对比
- 🌍 **多平台支持** - Amazon（8个国家）和 TikTok（15个国家）

## 🚀 快速开始

### 配置密钥

在 OpenClaw config 中设置：

```json5
{
  skills: {
    entries: {
      "alphashop-sel-newproduct": {
        env: {
          ALPHASHOP_ACCESS_KEY: "你的AccessKey",
          ALPHASHOP_SECRET_KEY: "你的SecretKey"
        }
      }
    }
  }
}
```

密钥获取：访问 https://www.alphashop.cn/seller-center/apikey-management 申请。

## 🎯 使用方法

⚠️ **重要：两个 API 有先后依赖关系！**

### 步骤 1：关键词搜索

```bash
python3 scripts/selection.py search \
  --keyword "yoga pants" --platform "amazon" --region "US"
```

### 步骤 2：使用返回的 keyword 生成报告

```bash
python3 scripts/selection.py report \
  --keyword "yoga pants set" --platform "amazon" --country "US"
```

### 带筛选条件

```bash
python3 scripts/selection.py report \
  --keyword "phone" --platform "amazon" --country "US" \
  --listing-time "90" --min-price 10 --max-price 100 \
  --min-sales 1 --min-rating 3.5
```

## 📁 项目结构

```
alphashop-sel-newproduct/
├── SKILL.md                    # SKILL 配置文件
├── README.md                   # 本文档
├── QUICKSTART.md               # 快速开始指南
├── requirements.txt            # Python 依赖
├── references/
│   └── api.md                  # API 参考文档
├── scripts/
│   └── selection.py            # 选品主脚本
└── output/                     # 报告输出目录
```

## 📝 注意事项

1. **关键词依赖** - `report` 的 `--keyword` 必须来自 `search` 返回的结果，否则报 `KEYWORD_ILLEGAL`
2. **支持平台** - Amazon: US/UK/ES/FR/DE/IT/CA/JP；TikTok: ID/VN/MY/TH/PH/US/SG/BR/MX/GB/ES/FR/DE/IT/JP
3. **上架时间** - 仅支持 `"90"` 或 `"180"` 天
4. **响应时间** - 接口响应需要几十秒，请耐心等待

---

**最后更新**: 2026-03-19
