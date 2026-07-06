# 免费新闻源与 RSS

## 推荐免费信源

### 国际通讯社（完全免费）

| 媒体 | 网址 | RSS | 特点 |
|------|------|-----|------|
| BBC News | bbc.com | ✅ | 国际新闻最全面 |
| Reuters | reuters.com | ✅ | 财经+国际 |
| AP News | apnews.com | ✅ | 美联社 |
| AFP | afp.com | ✅ | 法新社 |
| Al Jazeera | aljazeera.com | ✅ | 中东专家 |
| Deutsche Welle | dw.com | ✅ | 德国视角 |

### 美国媒体（部分免费）

| 媒体 | 免费程度 | RSS | 备注 |
|------|---------|-----|------|
| NPR | 免费 | ✅ | 广播新闻 |
| ProPublica | 免费 | ✅ | 调查报道 |
| PBS NewsHour | 免费 | ✅ | 深度报道 |
| CNN | 部分免费 | ✅ | 有限制 |
| Vox | 部分免费 | ✅ | 解释性新闻 |

### 财经媒体

| 媒体 | 免费程度 | RSS | 备注 |
|------|---------|-----|------|
| Yahoo Finance | 免费 | ✅ | 综合财经 |
| MarketWatch | 部分 | ✅ | 道琼斯旗下 |
| CoinDesk | 免费 | ✅ | 加密货币 |
| TechCrunch | 部分 | ✅ | 科技 |

---

## RSS 订阅

### 什么是 RSS

RSS (Really Simple Syndication) 是一种订阅格式，可以在不访问网站的情况下获取最新内容。

### RSS 阅读器

**推荐工具:**
- Feedly (feedly.com) - 在线 + App
- Inoreader (inoreader.com) - 功能强大
- NetNewsWire (Mac/iOS) - 原生体验
- FreshRSS (freshrss.org) - 自托管

### 常用 RSS 源

```
# 国际新闻
https://feeds.bbci.co.uk/news/rss.xml
https://www.reuters.com/rssFeed/worldNews
https://rss.nytimes.com/services/xml/rss/nyt/World.xml

# 财经
https://feeds.bbci.co.uk/news/business/rss.xml
https://www.reuters.com/rssFeed/businessNews

# 科技
https://feeds.feedburner.com/TechCrunch
https://www.wired.com/feed/rss

# 中文
https://feeds.bbci.co.uk/zhongsimps/rss.xml
https://www.bbc.com/zhongwen/simp/rss.xml
```

### Email 转 RSS

**工具:** 
- rss.app - 将 email newsletter 转为 RSS
- Feedly - 内置 newsletter to RSS 功能

**使用场景:**
- 订阅记者/机构的 email newsletter
- 保持邮箱清洁
- 集中阅读

---

## 搜索技巧

### Google 搜索免费版本

```
# 搜索免费转载
"{文章标题}" site:reddit.com OR site:hn.algolia.com

# 搜索替代信源
"{标题关键词}" (site:bbc.com OR site:reuters.com OR site:apnews.com)

# 搜索 PDF 版本
"{标题}" filetype:pdf

# 搜索 Twitter 讨论
"{标题}" site:twitter.com OR site:x.com
```

### Twitter/X 获取

**技巧:**
1. 搜索文章标题
2. 找记者/媒体账号
3. 他们经常发布文章链接
4. 有时附有 "gift link"（免费访问）

---

## 浏览器书签工具

### 快速访问

**创建书签，URL 设为:**

```javascript
// smry.ai
javascript:location.href='https://smry.ai/'+encodeURIComponent(location.href);

// 12ft.io
javascript:location.href='https://12ft.io/'+encodeURIComponent(location.href);

// 查看源代码
javascript:document.body.innerText;

// 禁用 JS 后刷新（需要扩展）
```

**使用:** 在付费页面点击书签即可

---

_最后更新: 2026-03-05_
