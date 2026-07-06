---
name: Latte-news-fetcher
version: 3.2.2
description: |
  新闻获取工具。支持获取新闻列表、绕过付费墙获取全文。
  使用 archive.today、smry.ai、12ft.io 等公开服务访问付费内容。
  触发词：新闻、今日新闻、付费墙、文章、阅读。
metadata:
  openclaw:
    requires:
      bins:
        - node
      writes:
        - CONFIG/news-preferences.md
    optionalEnv:
      - TAVILY_API_KEY
    install:
      - kind: node
        package: node-fetch
        bins: []
    homepage: https://github.com/luogao2333/Latte-news-fetcher
    emoji: "📰"
---

# Latte News Fetcher - 新闻获取工具 ☕

获取新闻列表、绕过付费墙、深入阅读完整内容。

---

## 🚀 核心流程

### 首次使用：初始化偏好

**检查配置文件** `CONFIG/news-preferences.md`（workspace 根目录）

如果用户偏好为空，执行初始化：

```
询问用户：
"你想要看哪些方面的新闻？可以选择以下类别，也可以告诉我你常看的网站："

🌍 国际时事 - BBC、Reuters、Al Jazeera
🇨🇳 国内要闻 - 人民网、新华网、澎湃新闻
💰 财经金融 - 财联社、Bloomberg、华尔街见闻
💻 科技互联网 - 36氪、The Verge、虎嗅
⚽ 体育娱乐 - 虎扑、ESPN、新浪体育
📊 商业市场 - 界面、财新、第一财经

你也可以直接告诉我你想关注的网站。"
```

**保存偏好** → 写入 `CONFIG/news-preferences.md`（workspace 根目录）

---

### 日常使用：获取今日新闻

**触发场景（两种）：**

1. **通用请求**：用户问"今天有什么新闻"、"看看新闻"等
   - → 读取用户偏好配置，获取偏好类别对应的网站

2. **指定网站**：用户问"看看华尔街日报今天有什么新闻"、"BBC今天新闻"等
   - → 直接访问用户指定的网站，跳过偏好检查

---

### 📰 获取新闻首页（关键！）

⚠️ **重要：主流媒体网站通常会阻止简单的 fetch 请求，必须使用正确的工具**

#### 工具选择优先级

| 优先级 | 工具 | 适用场景 | 说明 |
|--------|------|----------|------|
| 🔴 **首选** | `browser` | WSJ、Bloomberg、NYT、FT 等主流媒体 | 能处理 JS 渲染和反爬机制 |
| 🟡 备选 | `web_fetch` | BBC、Reuters、AP 等开放网站 | 轻量级，速度快 |
| 🟢 兜底 | Tavily 搜索 | 首页获取失败时 | 搜索 `site:xxx.com` 获取今日新闻 |

#### 首页获取流程

```
1. browser 打开网站首页
   browser action=open url="https://cn.wsj.com" profile="openclaw"
   
2. 等待页面加载（3-5秒）
   browser action=act kind=wait timeMs=5000
   
3. 获取页面快照
   browser action=snapshot
   
4. 从快照中提取新闻标题和链接

5. 关闭浏览器
   browser action=close
```

#### 首页获取失败时的备选方案

如果 browser 访问失败，按以下顺序尝试：

```
1. 使用 Tavily 搜索今日新闻
   搜索: "site:cn.wsj.com 2026-03-06" 或 "华尔街日报 今日"
   
2. 尝试 RSS 订阅源（如果有）
   WSJ RSS: https://feeds.a.dj.com/rss/RSSWSJD.xml
   
3. 使用 web_fetch 尝试移动版
   web_fetch url="https://m.cn.wsj.com"
   
4. 诚实告知用户，提供替代网站
```

---

### 输出格式（纯文本 Markdown）

⚠️ **重要：使用纯文本 Markdown 格式，不使用飞书交互式卡片！**

使用 `message` 工具发送纯文本消息，格式如下：

```markdown
**[来源名称] 今日新闻** (YYYY-MM-DD)

---

**🔥 热门文章**

1. [标题](原文链接) | 类别
   简短摘要（1-2行，精炼概括核心事件）

2. [标题](原文链接) | 类别
   简短摘要

3. [标题](原文链接) | 类别
   简短摘要

---

**🌍 国际**

- [标题](原文链接) | 摘要

**🇨🇳 中国**

- [标题](原文链接) | 摘要

**🇺🇸 美国政治**

- [标题](原文链接) | 摘要

**💰 财经金融**

- [标题](原文链接) | 摘要

**💻 科技**

- [标题](原文链接) | 摘要

**🏢 商业**

- [标题](原文链接) | 摘要

**🎨 有趣/生活**

- [标题](原文链接) | 摘要

---

对哪条新闻感兴趣想深入了解？我可以用绕过工具帮你获取全文。
```

**格式要求：**
- **使用纯文本 Markdown**，不使用飞书交互式卡片（interactive card）
- 主标题使用 `**粗体**`，日期用括号
- 各分类板块使用 `---` 分隔线
- 分类标题使用 `**粗体**` + 图标：🌍 国际、🇨🇳 中国、🇺🇸 美国政治、💰 财经金融、💻 科技、🏢 商业、🎨 有趣/生活
- 热门文章必须有编号、标题、类别标签和1-2行摘要
- 标题使用 Markdown 超链接格式 `[标题](链接)`
- 摘要精炼，确保信息密度与可读性平衡
- 结尾提供深入了解的提示

**实现方式：**
```javascript
message(
  action: "send",
  channel: "feishu",
  message: "**华尔街日报中文版 今日新闻** (2026-03-06)\n\n---\n\n**🔥 热门文章**\n\n1. [标题](链接) | 类别\n   摘要内容\n\n..."
)
```

---

## 📋 核心类别与知名网站

| 类别 | 首选网站（Top 3） | 备选网站 |
|------|------------------|----------|
| 🌍 **国际时事** | BBC、Reuters、Al Jazeera | AP News、DW、NHK World |
| 🇨🇳 **国内要闻** | 人民网、新华网、澎湃新闻 | 中国新闻网、环球网、新京报 |
| 💰 **财经金融** | 财联社、Bloomberg、华尔街见闻 | Reuters财经、第一财经、财新 |
| 💻 **科技互联网** | 36氪、The Verge、虎嗅 | TechCrunch、Ars Technica、钛媒体 |
| ⚽ **体育娱乐** | 虎扑、ESPN、新浪体育 | BBC Sport、懂球帝、直播吧 |
| 📊 **商业市场** | 界面、财新、第一财经 | 21世纪经济报道、FT中文网、日经中文网 |

**网站与工具对应表：**

| 网站 | 首页获取工具 | 原因 |
|------|-------------|------|
| WSJ/Bloomberg/NYT/FT | `browser` | 反爬机制强，需要 JS 渲染 |
| BBC/Reuters/AP | `web_fetch` 或 `browser` | 相对开放，两者皆可 |
| 国内媒体（澎湃/财新等） | `browser` | 部分有反爬 |
| 科技媒体（36氪/The Verge） | `browser` | JS 渲染较多 |

---

## 🔍 深入新闻：获取全文

**触发：用户说"详细了解 XX"、"展开第 X 条"等**

### 获取优先级

```
1. web_fetch 直接获取（免费信源）
      ↓ 失败
2. browser 访问页面（无付费墙）
      ↓ 失败（付费墙）
3. archive.today 归档版本（首选绕过方案）
      ↓ 失败（无存档）
4. RemovePaywall → archive.is
      ↓ 失败
5. 其他绕过工具（smry.ai / 12ft.io）
      ↓ 失败
6. 搜索替代信源（BBC/Reuters/AP）
      ↓ 失败
7. 诚实告知 + 提供已获取的摘要
```

### 绕过付费墙工具

| 优先级 | 工具 | 用法 | 适用场景 |
|--------|------|------|----------|
| ⭐⭐⭐ | **archive.today** | `https://archive.today/{链接}` | **首选！付费墙通用方案** |
| ⭐⭐ | **smry.ai** | `https://smry.ai/{链接}` | 带总结，部分站点有效 |
| ⭐⭐ | **RemovePaywall** | `https://www.removepaywall.com/search?url={链接}` | 华尔街日报备选 |
| ⭐ | **12ft.io** | `https://12ft.io/{链接}` | 博客、Medium |
| ⭐ | **r.jina.ai** | `https://r.jina.ai/http://{链接}` | 纯文本提取 |

---

### 🗞️ 华尔街日报 (WSJ) 专用绕过方法

#### 方法一：archive.today 直接访问（推荐）

⚠️ **关键步骤：archive.today 会先显示存档列表页，需要点击具体存档链接才能进入内容页**

**完整操作流程：**

```
步骤1: 尝试直接获取（通常失败）
web_fetch url="https://cn.wsj.com/articles/xxx"

步骤2: 打开 archive.today
browser action=open url="https://archive.today/https://cn.wsj.com/articles/xxx"
browser action=act kind=wait timeMs=8000

步骤3: 获取快照，检查页面状态
browser action=snapshot

步骤4: 判断页面类型
├── 如果显示"存档列表"（有多个存档时间和链接）
│   → 点击最新的存档链接
│   → browser action=act kind=click ref="存档链接"
│   → 等待跳转后获取内容
│
└── 如果直接显示文章内容
    → 直接提取内容

步骤5: 从快照中提取文章内容
（注意：archive.today 页面顶部有工具栏，内容在下方）

步骤6: 关闭浏览器
browser action=close
```

**实际代码示例：**
```javascript
// 步骤1: 尝试直接获取
web_fetch url="https://cn.wsj.com/articles/英伟达将重心转离对华销售芯片-e85f9673"
// → 失败

// 步骤2: 打开 archive.today
browser action=open url="https://archive.today/https://cn.wsj.com/articles/..."
browser action=act kind=wait timeMs=8000

// 步骤3: 获取快照
browser action=snapshot
// 检查结果：发现是存档列表页

// 步骤4: 点击存档链接
// 在快照中找到类似这样的链接：
// link "英伟达将重心转离对华销售芯片 - WSJ" [ref=e43]
browser action=act kind=click ref="e43"

// 步骤5: 等待加载后获取内容
browser action=act kind=wait timeMs=5000
browser action=snapshot

// 步骤6: 提取内容并整理输出
```

#### 时效性提示

⏰ **存档可能不是实时的**：
- archive.today 的存档由用户提交，可能有数小时延迟
- 如果需要最新内容而存档过旧，尝试：
  1. RemovePaywall 方案
  2. 搜索替代信源
  3. 等待新存档

#### 方法二：RemovePaywall（备选）

如果 archive.today 没有存档，使用此方法：

```
1. browser action=open url="https://www.removepaywall.com/search?url={WSJ链接}"
2. browser action=act kind=wait timeMs=5000
3. browser action=act kind=click ref="option2或option3按钮"
4. 等待跳转到 archive.is 页面
5. browser action=snapshot 获取内容
```

---

### 📊 其他付费网站绕过方案

| 网站 | 推荐方法 | 备注 |
|------|----------|------|
| 华尔街日报 (WSJ) | archive.today | 优先使用，需点击存档链接 |
| Bloomberg | archive.today | 同上 |
| NYT | archive.today | 同上 |
| Medium | 12ft.io / r.jina.ai | 效果较好 |
| FT中文网 | archive.today | 同上 |

### 搜索替代信源

**使用 Tavily API 搜索同一事件的免费报道：**

```bash
curl -s --request POST \
  --url https://api.tavily.com/search \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "China 2026 GDP growth target 4.5% 5% economic",
    "max_results": 5,
    "search_depth": "basic"
  }'
```

**替代优先级：**
1. BBC / Reuters / AP（国际）
2. 官方来源（如中国国务院新闻办 SCIO）
3. 国内免费媒体（国内）
4. 社交媒体（Twitter/X 记者账号）

**综合多信源：**
当无法获取原文全文时，从 Tavily 搜索结果中选择 2-3 个信源，综合整理后提供给用户，并注明来源链接。

---

### 需要会员登录的网站处理

⚠️ **特殊类型**：部分网站（如日经中文网）不是付费墙，而是需要**免费会员登录**才能看全文

**处理流程：**

```
1. 尝试 smry.ai 获取
   ├── 成功但内容截断 → 说明需要登录
   └── 失败 → 继续下一步

2. 使用 Tavily 搜索替代信源（推荐）
   - 搜索同一事件的其他媒体报道
   - 综合多信源整理

3. 请求用户登录（备选）
   - 询问用户是否有会员账号
   - 如有，请用户在 Chrome 中登录
   - 使用 browser profile="chrome" 访问
   - 注意：需要用户先点击 OpenClaw Browser Relay 扩展启用
```

**用户登录操作提示：**
```
"你有日经中文网会员账号吗？

如果有：
1. 在 Chrome 浏览器中打开 https://cn.nikkei.com/user/login.html 并登录
2. 登录成功后告诉我
3. 我会通过你的浏览器访问文章全文

或者，我可以用 Tavily 搜索其他媒体对同一事件的报道。"
```

---

## 🛠️ 工具选择速查表

### 获取新闻列表

| 场景 | 推荐工具 | 原因 |
|------|----------|------|
| 主流媒体首页（WSJ/Bloomberg/NYT） | `browser` | 反爬机制强 |
| 开放媒体（BBC/Reuters） | `web_fetch` 或 `browser` | 两者皆可 |
| 首页获取失败 | Tavily 搜索 `site:xxx.com` | 兜底方案 |

### 获取文章全文

| 场景 | 工具 |
|------|------|
| 免费信源 | `web_fetch` 直接获取 |
| 付费信源 | `browser` + archive.today |
| 复杂页面 | `browser` + `snapshot` |

---

## 📂 相关文件

- [用户偏好配置](CONFIG/news-preferences.md) - 存储用户的新闻偏好（workspace 根目录）
- [新闻网站资源](references/news-sources.md) - 完整的网站列表
- [付费墙难度矩阵](references/paywall-matrix.md) - 各网站付费墙分析
- [绕过工具对比](references/bypass-tools.md) - 工具效果对比
- [进阶技巧](references/advanced-techniques.md) - 浏览器技巧等

---

## ⚠️ 注意事项

1. **链接格式** - 新闻列表必须使用 `[标题](原文链接)` 格式
2. **热门新闻** - 必须是当天最热门、关注度最高的，不限类别
3. **尊重版权** - 仅供个人学习研究
4. **优先免费** - BBC/Reuters/AP 是第一选择
5. **诚实透明** - 无法获取时明确告知 + 提供替代
6. **输出格式** - 始终使用纯文本 Markdown，不用飞书交互式卡片
7. **存档时效** - archive.today 存档可能有延迟，注意检查存档时间

---

## 🔄 流程图

```
用户请求新闻
        │
        ├─── 用户指定网站？
        │         │
        │        Yes ──→ 直接访问指定网站
        │         │
        │         No
        │         │
        │         ▼
        │    检查用户偏好配置
        │         │
        │    ┌────┴────┐
        │    │ 有偏好？ │
        │    └────┬────┘
        │     No  │  Yes
        │    ┌────┴────┐
        │    ▼         ▼
        │  询问用户   直接获取
        │  设置偏好   偏好类别新闻
        │    │         │
        │    └────┬────┘
        │         │
        └─────────┤
                  ▼
        ┌───────────────────┐
        │ browser 打开首页   │
        │ （主流媒体首选）    │
        └───────────────────┘
                  │
           ┌──────┴──────┐
           │   成功？     │
           └──────┬──────┘
            Yes   │   No
           ┌──────┴──────┐
           ▼             ▼
      提取新闻      尝试备选方案
      标题链接      (Tavily/RSS/移动版)
           │             │
           │      ┌──────┴──────┐
           │      │   成功？     │
           │      └──────┬──────┘
           │        Yes  │   No
           │       ┌─────┴─────┐
           │       ▼           ▼
           │   提取新闻    告知用户
           │   标题链接    提供替代
           │       │           │
           └───────┴───────────┘
                   │
                   ▼
        ┌───────────────────┐
        │ 整理输出：         │
        │ 🔥 最热门 x3       │
        │ + 分类新闻         │
        │ （纯文本Markdown）  │
        └───────────────────┘
                   │
                   ▼
            用户选择深入了解
                   │
                   ▼
        ┌───────────────────┐
        │ 获取全文 + 总结    │
        │ web_fetch          │
        │ ↓ 失败             │
        │ browser            │
        │ ↓ 付费墙           │
        │ archive.today      │
        │ （注意点击存档链接） │
        │ ↓ 失败             │
        │ 搜索替代信源        │
        └───────────────────┘
```

---

## 📝 更新日志

- **2026-03-06 (v2)**: 
  - 新增"需要会员登录的网站处理"流程（如日经中文网）
  - 新增 Tavily API 完整使用示例（curl 命令）
  - 新增"综合多信源"策略说明
  - 替代信源优先级新增"官方来源"
  - 流程图增加"用户登录"分支提示

- **2026-03-06 (v1)**: 
  - 首页获取改用 browser 为首选（主流媒体反爬机制）
  - archive.today 流程补充"点击存档链接"步骤
  - 新增"用户指定网站"分支
  - 新增首页获取失败的备选方案
  - 添加存档时效性提示
  - 更新流程图

---

_此技能持续优化中。最后更新: 2026-03-06_
