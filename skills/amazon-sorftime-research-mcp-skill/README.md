# Amazon Analyse Skill

> 亚马逊竞品Listing全维度穿透分析工具

对亚马逊竞品进行深度分析，包括文案逻辑、评论情感、关键词布局、市场动态等，生成专业竞品情报报告并自动保存为文档。

---

## 功能特性

| 功能模块 | 说明 |
|----------|------|
| **产品基础分析** | 价格、评分、排名、销量等核心指标 |
| **关键词布局** | 流量来源、自然曝光、竞品关键词分析 |
| **评论情感分析** | 优势聚类、痛点挖掘、改进建议 |
| **市场动态** | 销量趋势、季节性波动、竞争格局 |
| **战略建议** | 关键词策略、定价建议、Listing优化 |
| **报告保存** | 自动生成Markdown文档 |

---

## 快速开始

### 命令格式

```
/amazon-analyse <ASIN> [站点]
```

### 参数说明

| 参数 | 说明 | 可选值 | 默认值 |
|------|------|--------|--------|
| ASIN | 亚马逊产品标识码（10位） | - | 必填 |
| 站点 | 亚马逊站点 | US, GB, DE, FR, CA, JP, ES, IT, MX, AE, AU, BR, SA | US |

### 使用示例

```bash
# 分析美国站产品
/amazon-analyse B07PQFT83F US

# 分析德国站产品
/amazon-analyse B08N5WRWNW DE

# 分析日本站产品
/amazon-analyse B09XXX JP
```

---

## 分析报告内容

### 报告结构

```
1. 产品基础数据
   ├── 核心指标（价格、评分、排名）
   └── 市场表现（销量趋势、生命周期）

2. 关键词布局分析 (The Brain)
   ├── 流量关键词列表
   ├── 竞品关键词布局
   └── 文案构建逻辑

3. 评论定性分析 (The Voice)
   ├── 评论数据概览
   ├── 核心优势 Top 3
   ├── 核心痛点 Top 3
   └── 改进建议 Top 3

4. 竞争策略分析 (The Pulse)
   ├── 竞争优势
   ├── 竞争劣势
   ├── 市场机会
   └── 潜在威胁

5. 战略反击建议
   ├── 关键词策略
   ├── 定价策略
   ├── 产品优化方向
   └── Listing优化建议
```

---

## 输出文件

### 文件位置

```
项目目录/reports/
```

### 命名规则

```
analysis_{ASIN}_{站点}_{日期}.md

例如: analysis_B07PQFT83F_US_20260302.md
```

### 报告示例

```markdown
# 亚马逊竞品Listing全维度穿透分析报告

## 分析对象
- ASIN: B07PQFT83F
- 亚马逊站点: US
- 分析时间: 2026-03-02
- 数据来源: Sorftime MCP

## 第一部分：产品基础数据
### 核心指标
- 产品标题: Disney Store Official Buzz Lightyear...
- 品牌: Disney Store
- 价格: $39.95
- 评分: 4.70 / 5.0
- 评论数: 47,400
- 类目排名: #1 in Action Figures

...
```

---

## 数据来源

本工具使用 **Sorftime MCP** 服务获取亚马逊数据：

- 支持亚马逊14大站点
- 实时产品搜索与详情
- 用户评论分析（最多100条）
- 流量关键词数据
- 历史销量趋势

### Sorftime MCP API

```bash
curl -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{...}}'
```

---

## 配置

### API Key 配置

编辑 `项目目录/.mcp.json`：

```json
{
  "mcpServers": {
    "sorftime": {
      "type": "streamableHttp",
      "url": "https://mcp.sorftime.com?key=YOUR_API_KEY",
      "name": "Sorftime MCP",
      "description": "Sorftime 跨境电商平台数据服务"
    }
  }
}
```

### Sorftime API Key 获取

1. 访问 [Sorftime官网](https://www.sorftime.com)
2. 注册账号并申请API Key
3. 将API Key配置到 `.mcp.json` 文件

---

## 目录结构

```
项目目录/
├── .claude/
│   └── skills/
│       └── amazon-analyse/
│           ├── SKILL.md           # 技能定义文件
│           └── README.md          # 本文档
├── reports/                        # 分析报告输出目录
│   ├── analysis_xxx_US_20260302.md
│   └── archive/
│       ├── 2026/
│       └── 2025/
└── .mcp.json                       # MCP配置文件
```

---

## 故障排查

### 问题：ASIN未找到

**原因**：ASIN不在Sorftime数据库或已下架

**解决**：
1. 确认ASIN格式正确（10位字母数字）
2. 使用product_search工具验证
3. 检查产品是否在该站点上架

### 问题：API请求超时

**原因**：网络问题或API服务异常

**解决**：
1. 检查网络连接
2. 验证API Key是否有效
3. 增加超时时间：`curl --max-time 30`

### 问题：中文显示为乱码

**原因**：Unicode转义字符未解码

**解决**：现代工具会自动解码，或使用Python解码：
```python
import json
print(json.loads('"\\u4EA7\\u54C1"'))
```

---

## 最佳实践

### 1. 定期追踪竞品

建议每月分析一次核心竞品，监控其策略变化：

```bash
# 1月分析
/amazon-analyse B07PQFT83F US  # → analysis_xxx_US_20260115.md

# 2月分析
/amazon-analyse B07PQFT83F US  # → analysis_xxx_US_20260220.md

# 对比两次分析
diff reports/analysis_xxx_US_20260115.md reports/analysis_xxx_US_20260220.md
```

### 2. 多站点对比

同一产品在不同站点的表现可能不同：

```bash
/amazon-analyse B07PQFT83F US  # 美国站
/amazon-analyse B07PQFT83F DE  # 德国站
/amazon-analyse B07PQFT83F JP  # 日本站
```

### 3. 报告归档管理

定期整理旧报告：

```bash
# 归档6个月前的报告
mkdir -p reports/archive/2025/
mv reports/analysis_*_2025*.md reports/archive/2025/
```

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v2.0 | 2026-03-02 | 添加报告保存功能、故障排查、最佳实践 |
| v1.0 | 2026-02-20 | 初始版本 |

---

## 相关链接

- [Sorftime官网](https://www.sorftime.com)
- [Amazon MWS文档](https://developer.amazonservices.com/)
- [Claude Code文档](https://claude.com/claude-code)

---

## 许可证

MIT License

---

*最后更新: 2026-03-02*
