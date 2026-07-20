# 多源搜索引擎使用指南

## 概述

本技能整合了 17 个搜索引擎，无需 API 密钥，覆盖国内外主流搜索平台。

---

## ⚡ 快速开始

### 时间范围设置

**默认时间范围**：**近一周**（推荐）

| 数据类型 | 推荐时间范围 | Google/Bing 参数 |
|---------|-------------|-----------------|
| **最新资讯** | 近一周 | `tbs=qdr:w`（默认） |
| **市场趋势** | 近一月 | `tbs=qdr:m` |
| **行业报告** | 近一年 | `tbs=qdr:y` |
| **历史数据** | 全部时间 | 不添加参数 |

**注意**：时间过滤可以显著减少不相关结果，节省 Token。

### 搜索数量控制

| 工具 | 参数 | 默认值 | 建议 |
|------|------|--------|------|
| **web_search** | `max_results` | 5 | 3-10（根据需求调整） |
| **web_fetch** | `maxChars` | 8000 | 5000-10000（控制返回内容大小） |

**Token 优化**：减少 `max_results` 和 `maxChars` 可以显著降低 Token 使用。

---

## 国内搜索引擎（8个）

| 引擎 | URL模板 | 适用场景 |
|------|---------|----------|
| **百度** | `https://www.baidu.com/s?wd={keyword}` | 中文市场数据、本地化搜索 |
| **Bing CN（中文）** | `https://cn.bing.com/search?q={keyword}&ensearch=0` | 中文搜索，国际视野 |
| **Bing INT（国际）** | `https://cn.bing.com/search?q={keyword}&ensearch=1` | 国际市场数据 |
| **360搜索** | `https://www.so.com/s?q={keyword}` | 中文补充搜索 |
| **搜狗** | `https://sogou.com/web?query={keyword}` | 中文搜索 |
| **微信** | `https://wx.sogou.com/weixin?type=2&query={keyword}` | 公众号文章、营销案例 |
| **今日头条** | `https://so.toutiao.com/search?keyword={keyword}` | 新闻资讯、热点追踪 |
| **集思录** | `https://www.jisilu.cn/explore/?keyword={keyword}` | 投资理财数据 |

---

## 国际搜索引擎（9个）

| 引擎 | URL模板 | 适用场景 |
|------|---------|----------|
| **Google** | `https://www.google.com/search?q={keyword}` | 全球市场数据、学术研究 |
| **Google HK** | `https://www.google.com.hk/search?q={keyword}` | Google 中文搜索 |
| **DuckDuckGo** | `https://duckduckgo.com/html/?q={keyword}` | 隐私搜索、无追踪 |
| **Yahoo** | `https://search.yahoo.com/search?p={keyword}` | 国际补充搜索 |
| **Startpage** | `https://www.startpage.com/sp/search?query={keyword}` | Google结果 + 隐私保护 |
| **Brave** | `https://search.brave.com/search?q={keyword}` | 独立索引、隐私搜索 |
| **Ecosia** | `https://www.ecosia.org/search?q={keyword}` | 环保搜索 |
| **Qwant** | `https://www.qwant.com/?q={keyword}` | 欧盟GDPR合规 |
| **WolframAlpha** | `https://www.wolframalpha.com/input?i={keyword}` | 知识计算、数据查询 |

---

## 如何使用

### 基础搜索

使用 `web_fetch` 工具调用搜索引擎：

```markdown
web_fetch(url="https://www.baidu.com/s?wd=中国护肤市场规模+2024")
```

### 高级搜索操作符

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `site:` | `site:iresearch.cn 护肤市场` | 限定在特定网站搜索 |
| `filetype:` | `filetype:pdf 护肤行业报告` | 搜索特定文件类型 |
| `""` | `"Z世代护肤消费"` | 精确匹配短语 |
| `-` | `护肤品 -化妆品` | 排除特定关键词 |
| `OR` | `护肤 OR 美妆` | 搜索多个关键词 |

### 时间过滤（Google/Bing）

在 URL 后添加时间过滤参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `tbs=qdr:h` | 过去1小时 | `https://www.google.com/search?q=AI+news&tbs=qdr:h` |
| `tbs=qdr:d` | 过去1天 | `https://www.google.com/search?q=AI+news&tbs=qdr:d` |
| `tbs=qdr:w` | 过去1周 | `https://www.google.com/search?q=AI+news&tbs=qdr:w` |
| `tbs=qdr:m` | 过去1月 | `https://www.google.com/search?q=AI+news&tbs=qdr:m` |
| `tbs=qdr:y` | 过去1年 | `https://www.google.com/search?q=AI+news&tbs=qdr:y` |

---

## 实际使用示例

### 示例1：搜索中文市场数据

```markdown
# 搜索中国市场护肤规模数据
web_fetch(url="https://www.baidu.com/s?wd=中国护肤市场规模+2024")

# 搜索微信文章
web_fetch(url="https://wx.sogou.com/weixin?type=2&query=Z世代护肤消费趋势")

# 搜索政府统计数据（限定政府网站）
web_fetch(url="https://www.baidu.com/s?wd=site:gov.cn+化妆品行业统计")
```

### 示例2：搜索国际市场数据

```markdown
# 搜索全球市场数据
web_fetch(url="https://www.google.com/search?q=global+skincare+market+size+2024")

# 搜索 PDF 格式报告
web_fetch(url="https://www.google.com/search?q=skincare+market+report+filetype:pdf")

# 最近一周的新闻
web_fetch(url="https://www.google.com/search?q=skincare+industry+news&tbs=qdr:w")
```

### 示例3：多源验证

```markdown
# 用多个搜索引擎验证同一数据
web_fetch(url="https://www.baidu.com/s?wd=护肤品市场规模+2024")
web_fetch(url="https://cn.bing.com/search?q=skincare+market+size+China+2024")
web_fetch(url="https://www.google.com/search?q=China+skincare+market+2024")
```

---

## DuckDuckGo 快速搜索

### 如何使用

使用 `web_fetch` 调用 DuckDuckGo Lite：

```markdown
web_fetch(
  url="https://lite.duckduckgo.com/lite/?q=QUERY",
  extractMode="text",
  maxChars=8000
)
```

### 参数说明

- **URL编码**：用 `+` 代替空格
- **extractMode**：使用 `"text"` 而非 `"markdown"`，获得更清晰的结果
- **maxChars**：增加字符数以获取更多结果（默认 8000）

### 区域过滤

在 URL 后添加 `&kl=REGION` 参数：

| 区域代码 | 说明 |
|---------|------|
| `us-en` | 美国 |
| `uk-en` | 英国 |
| `au-en` | 澳大利亚 |
| `de-de` | 德国 |
| `fr-fr` | 法国 |

完整区域列表：https://duckduckgo.com/params

### 实际使用示例

```markdown
# 基础搜索
web_fetch(
  url="https://lite.duckduckgo.com/lite/?q=skincare+market+trends+2024",
  extractMode="text",
  maxChars=8000
)

# 区域搜索（美国）
web_fetch(
  url="https://lite.duckduckgo.com/lite/?q=best+coffee+melbourne&kl=us-en",
  extractMode="text",
  maxChars=8000
)

# 精确短语搜索
web_fetch(
  url="https://lite.duckduckgo.com/lite/?q=%22machine+learning%22+trends",
  extractMode="text",
  maxChars=8000
)
```

### 结果解读

搜索结果以编号列表形式显示，包含：
1. 标题
2. 摘要（snippet）
3. URL

**注意**：
- 前 1-2 条结果可能是广告（标记为 "Sponsored link"），跳过这些
- 有机搜索结果（organic results）跟在广告之后

---

## 特定数据源的搜索技巧

### 政府统计数据

```markdown
# 中国政府网站
web_fetch(url="https://www.baidu.com/s?wd=site:gov.cn+行业统计数据")

# 国家统计局
web_fetch(url="https://www.baidu.com/s?wd=site:stats.gov.cn+消费品零售")
```

### 行业报告

```markdown
# 搜索 PDF 格式报告
web_fetch(url="https://www.google.com/search?q=行业报告+filetype:pdf")

# 特定咨询公司报告
web_fetch(url="https://www.baidu.com/s?wd=site:iresearch.cn+报告")
```

### 学术论文

```markdown
# Google Scholar
web_fetch(url="https://scholar.google.com/scholar?q=machine+learning+healthcare")

# 知网（CNKI）
web_fetch(url="https://www.baidu.com/s?wd=site:cnki.net+关键词")
```

---

## 最佳实践

### 1. 搜索关键词优化

**好的关键词**：
- ✅ 具体明确："2024年中国护肤市场规模"
- ✅ 包含时间："skincare market size 2024"
- ✅ 中英文结合："护肤品市场 size growth"
- ✅ 使用专业术语："CAGR"、"TAM-SAM-SOM"

**不好的关键词**：
- ❌ 过于宽泛："护肤品"
- ❌ 缺少时间："市场规模"
- ❌ 口语化："怎么样"、"好不好"

### 2. 多源验证策略

对于 P0 级别的关键数据：

```markdown
# 验证策略：使用至少3个来源
1. 中文搜索（百度/微信）：获取本地数据
2. 国际搜索（Google/Bing）：获取全球视角
3. 官方来源：政府统计、上市公司财报

# 如果数据冲突：
- 标注所有来源
- 注明差异原因（时间范围、统计口径等）
- 选择最可信来源或使用范围值
```

### 3. 时间过滤技巧

根据数据类型选择时间范围：

| 数据类型 | 推荐时间范围 | 过滤方法 |
|---------|-------------|----------|
| 市场规模 | 最近1-3年 | `tbs=qdr:y` 或搜索年份 |
| 增长趋势 | 最近3-5年 | 搜索多个年份 |
| 政策法规 | 最近6个月 | `tbs=qdr:m` |
| 新闻热点 | 最近1周 | `tbs=qdr:w` |
