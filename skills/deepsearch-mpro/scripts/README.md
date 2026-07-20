# Scripts 说明文档

## 概述

本目录包含用于自动化数据收集和质量检查的脚本。

---

## data_collector.py

### 功能

根据分析框架自动执行多源数据收集。

### 使用方法

```bash
python scripts/data_collector.py --framework analysis-framework.md --output data-package.json
```

### 参数说明

| 参数 | 说明 | 必需 |
|------|------|-----|
| `--framework` | 分析框架文件路径 | 是 |
| `--output` | 输出数据包文件路径 | 否（默认：data-package.json） |
| `--engines` | 使用的搜索引擎（逗号分隔） | 否（默认：baidu,bing,google） |
| `--max-sources` | 每个指标的最大来源数 | 否（默认：3） |

### 输出格式

```json
{
  "metadata": {
    "research_subject": "研究主题",
    "collection_date": "2024-03-17",
    "total_sources": 25,
    "engines_used": ["baidu", "bing", "google"]
  },
  "chapters": {
    "1": {
      "title": "章节标题",
      "metrics": {
        "市场规模（亿元）": {
          "value": 3450,
          "year": 2024,
          "source": "艾瑞咨询",
          "url": "https://example.com/report",
          "confidence": "high"
        }
      }
    }
  }
}
```

### 注意事项

- 需要安装依赖：`pip install requests beautifulsoup4`
- 脚本会自动进行多源验证
- 对于 P0 数据，至少尝试 3 个来源
- 搜索频率限制：每个搜索引擎每秒最多 1 次请求

---

## 依赖安装

```bash
pip install requests beautifulsoup4 lxml
```

### 说明

如需使用数据收集脚本，需要安装以下依赖：
- requests>=2.28.0
- beautifulsoup4>=4.11.0
- lxml>=4.9.0

---

## 注意事项

1. **搜索频率限制**：避免过于频繁的请求，尊重网站的 robots.txt
2. **数据隐私**：不要搜索或存储敏感个人信息
3. **版权意识**：尊重数据来源的版权，正确标注来源
4. **网络环境**：某些搜索引擎可能需要特定网络环境

---

## 故障排除

### 问题1：搜索失败

**原因**：网络连接问题或搜索引擎限制

**解决**：
- 检查网络连接
- 尝试使用其他搜索引擎
- 增加请求间隔时间

### 问题2：数据提取失败

**原因**：网页结构变化

**解决**：
- 更新脚本版本
- 手动补充数据

### 问题3：依赖安装失败

**原因**：Python 版本或环境问题

**解决**：
- 确保 Python 版本 >= 3.8
- 使用虚拟环境：`python -m venv venv`
