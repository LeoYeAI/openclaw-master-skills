# Latte News Fetcher 📰

**智能新闻获取 + 付费墙绕过的 OpenClaw 技能**

> Named after my favorite coffee ☕

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ 功能特点

- 🌅 **每日新闻推送** - 获取当天最热门新闻 + 用户偏好类别新闻
- 🎯 **智能偏好** - 首次使用询问偏好，之后自动获取
- 🔗 **超链接格式** - 新闻标题附带原文链接，一键跳转
- 📖 **深入阅读** - 想了解某条新闻？获取全文 + AI 总结
- 🛡️ **付费墙绕过** - archive.today、smry.ai 等多种策略
- 🌐 **浏览器增强** - 智能识别反爬机制，自动切换工具
- 🌍 **70+ 专业网站** - 覆盖国际、国内、财经、科技、体育等领域

---

## 📦 安装

### ClawHub（推荐）

```bash
clawhub install latte-news-fetcher
```

### 手动安装

```bash
git clone https://github.com/luogao2333/Latte-news-fetcher.git
cp -r Latte-news-fetcher ~/.openclaw/workspace/skills/latte-news-fetcher
```

---

## 🚀 快速开始

### 通用请求

```
用户：今天有什么新闻
我：（获取偏好类别的新闻）
```

### 指定网站

```
用户：看看华尔街日报今天有哪些新闻
我：（直接获取 WSJ 今日新闻）
```

### 首次使用：设置偏好

```
用户：今天有什么新闻
我：你想要看哪些方面的新闻？可以选择以下类别：

     🌍 国际时事 - BBC、Reuters、Al Jazeera
     🇨🇳 国内要闻 - 人民网、新华网、澎湃新闻
     💰 财经金融 - 财联社、Bloomberg、华尔街见闻
     💻 科技互联网 - 36氪、The Verge、虎嗅
     ⚽ 体育娱乐 - 虎扑、ESPN、新浪体育
     📊 商业市场 - 界面、财新、第一财经

     你也可以直接告诉我你想关注的网站。

用户：国际和财经
我：（保存偏好，获取新闻）
```

---

## 📰 输出示例

```markdown
**华尔街日报中文版 今日新闻** (2026-03-06)

---

**🔥 热门文章**

1. [特朗普解雇国土安全部长克丽斯蒂·诺姆](https://cn.wsj.com/...) | 🇺🇸 美国政治
   特朗普解雇国土安全部长，由俄克拉荷马州共和党参议员马克韦恩·穆林接替。

2. [中国新GDP目标释放信号：经济步入减速新时代](https://cn.wsj.com/...) | 🇨🇳 中国
   中国将2026年经济增长目标设定在4.5%-5%，这是至少自上世纪90年代以来最低。

3. [英伟达将重心转离对华销售芯片](https://cn.wsj.com/...) | 💻 科技
   英伟达已停止生产面向中国市场的H200芯片，台积电产能转给Vera Rubin芯片。

---

**🌍 国际**

- [阿联酋考虑冻结伊朗资产](https://cn.wsj.com/...) | 如果阿联酋对伊朗影子融资网络采取行动...

**🇨🇳 中国**

- [中国承诺加大投资推动AI应用](https://cn.wsj.com/...) | 两会释放AI发展信号

---

对哪条新闻感兴趣想深入了解？我可以帮你获取全文。
```

---

## 📊 核心类别

| 类别 | 首选网站 | 备选网站 |
|------|----------|----------|
| 🌍 国际时事 | BBC, Reuters, Al Jazeera | AP, DW, NHK |
| 🇨🇳 国内要闻 | 人民网, 新华网, 澎湃新闻 | 中新网, 环球网, 新京报 |
| 💰 财经金融 | 财联社, Bloomberg, 华尔街见闻 | 第一财经, FT中文, 日经 |
| 💻 科技互联网 | 36氪, The Verge, 虎嗅 | TechCrunch, 钛媒体 |
| ⚽ 体育娱乐 | 虎扑, ESPN, 新浪体育 | BBC Sport, 懂球帝 |
| 📊 商业市场 | 界面, 财新, 第一财经 | 21世纪, 商业周刊 |

---

## 🔧 技术实现

### 智能工具选择

技能会根据网站特性自动选择最优工具：

| 场景 | 推荐工具 | 原因 |
|------|----------|------|
| 主流媒体首页（WSJ/Bloomberg/NYT） | `browser` | 反爬机制强，需要 JS 渲染 |
| 开放媒体（BBC/Reuters） | `web_fetch` 或 `browser` | 两者皆可 |
| 首页获取失败 | Tavily 搜索 `site:xxx.com` | 兜底方案 |

### 付费墙绕过策略

```
1. web_fetch 直接获取（免费信源）
      ↓ 失败
2. browser 访问页面（无付费墙）
      ↓ 失败（付费墙）
3. archive.today 归档版本（首选）
      ↓ 失败（无存档）
4. RemovePaywall / smry.ai
      ↓ 失败
5. Tavily 搜索替代信源
      ↓ 失败
6. 询问用户登录（会员网站）
      ↓ 失败
7. 诚实告知 + 提供已获取的摘要
```

### Tavily 搜索替代信源

当无法绕过付费墙时，使用 Tavily 搜索同一事件的其他报道：

```bash
curl -s --request POST \
  --url https://api.tavily.com/search \
  --header "Authorization: Bearer $TAVILY_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
    "query": "China 2026 GDP growth target 4.5% 5%",
    "max_results": 5,
    "search_depth": "basic"
  }'
```

**替代信源优先级：**
1. BBC / Reuters / AP（国际新闻）
2. 官方来源（如中国国务院新闻办 SCIO）
3. 国内免费媒体
4. 社交媒体（Twitter/X 记者账号）

**综合多信源**：选择 2-3 个信源，综合整理后提供给用户，注明来源链接。

### 会员登录网站处理

⚠️ **特殊类型**：部分网站（如日经中文网）不是付费墙，而是需要**免费会员登录**

**处理流程：**
1. 尝试 smry.ai → 内容截断说明需要登录
2. 使用 Tavily 搜索替代信源（推荐）
3. 询问用户是否可以登录 → 使用 `browser profile="chrome"` 访问

### archive.today 使用技巧

⚠️ **重要**：archive.today 会先显示存档列表页，需要点击具体存档链接：

```
1. 打开 https://archive.today/{原文链接}
2. 等待加载后获取快照
3. 如果显示存档列表 → 点击最新存档链接
4. 获取文章内容
```

⏰ **时效性**：存档可能有数小时延迟，如需最新内容请尝试其他方案。

---

## 🛠️ 工作流程

```
用户请求新闻
      │
      ├─── 用户指定网站？──Yes──→ 直接访问指定网站
      │         │
      │        No
      │         │
      │         ▼
      │    检查用户偏好配置
      │         │
      │    ┌────┴────┐
      │    │ 首次？   │
      │    └────┬────┘
      │     Yes │ No
      │    ┌────┴────┐
      │    ▼         ▼
      │  询问偏好   读取偏好
      │    │         │
      │    └────┬────┘
      │         │
      └─────────┤
                ▼
      ┌─────────────────┐
      │ browser 打开首页 │
      │ （主流媒体首选）  │
      └────────┬────────┘
               │
         ┌─────┴─────┐
         │  成功？    │
         └─────┬─────┘
          Yes  │  No
         ┌─────┴─────┐
         ▼           ▼
    提取新闻    备选方案
    标题链接    (Tavily/RSS)
         │           │
         └─────┬─────┘
               │
               ▼
      ┌─────────────────┐
      │ 输出新闻列表     │
      │ (纯文本Markdown) │
      └────────┬────────┘
               │
      用户选择深入了解
               │
               ▼
      ┌─────────────────┐
      │ 获取全文 + 总结  │
      │ archive.today   │
      └─────────────────┘
```

---

## 📂 文件结构

```
latte-news-fetcher/
├── SKILL.md                      # 主文档（工作流程）
├── README.md                     # 本文件
├── _meta.json                    # ClawHub 元数据
├── references/                   # 参考文档
│   ├── news-sources.md           # 70+ 新闻网站列表
│   ├── paywall-matrix.md         # 付费墙难度分析
│   ├── bypass-tools.md           # 绕过工具对比
│   ├── advanced-techniques.md    # 进阶技巧
│   └── free-sources.md           # 免费信源
└── scripts/                      # 可选脚本
    └── fetch_news.mjs            # Tavily 增强
```

### 用户配置文件

用户偏好存储在 workspace 根目录，不随技能更新丢失：

```
~/.openclaw/workspace/CONFIG/news-preferences.md
```

---

## ⚙️ 配置

### 必需

无。核心功能使用 `web_fetch` 和 `browser`，无需 API Key。

### 可选

- `TAVILY_API_KEY` - 使用 Tavily 搜索替代信源（更精准）

---

## 📝 更新日志

### v3.2.0 (2026-03-06)

- 🆕 **新增 Tavily API 完整使用示例** - curl 命令可直接复制使用
- 🆕 **新增"会员登录网站处理"流程** - 日经中文网等免费会员网站的处理方案
- 🆕 **新增"综合多信源"策略** - 无法获取原文时，从 2-3 个替代信源综合整理
- 🔧 **替代信源优先级更新** - 新增"官方来源"（如 SCIO）
- 📊 **工作流程图增加用户登录分支**

### v3.1.0 (2026-03-06)

- 🔄 **首页获取改用 browser 为首选** - 解决主流媒体反爬问题
- 🔧 **archive.today 流程优化** - 补充"点击存档链接"步骤
- 🆕 **新增首页获取失败备选方案** - Tavily 搜索、RSS、移动版
- 🆕 **新增"用户指定网站"分支** - 直接访问指定网站，跳过偏好检查
- ⏰ **添加存档时效性提示** - 提醒用户存档可能延迟
- 📊 **重构流程图** - 完整展示获取首页、失败备选、付费墙绕过路径

### v3.0.0 (2026-03-06)

- 🆕 新增每日新闻获取工作流
- 🆕 新增用户偏好配置
- 🆕 新增最热门 Top 3 功能
- 🔧 配置文件移至 workspace 根目录
- 📝 重写 README 和 SKILL 文档

### v2.0.0

- 新增绕过付费墙策略
- 新增参考文档

### v1.0.0

- 初始版本

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

**贡献指南：**
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 🐛 已知问题

- 部分网站（如 WSJ）首页需要 browser 工具，首次加载较慢
- archive.today 存档可能有数小时延迟
- 某些付费墙较难绕过，需要搜索替代信源

---

## 📮 反馈

- **Bug 报告**: [GitHub Issues](https://github.com/luogao2333/Latte-news-fetcher/issues)
- **功能建议**: [GitHub Discussions](https://github.com/luogao2333/Latte-news-fetcher/discussions)
- **OpenClaw 社区**: [Discord](https://discord.com/invite/clawd)

---

_Made with ☕ by the OpenClaw community_
