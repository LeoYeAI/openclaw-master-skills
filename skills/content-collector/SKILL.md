---
name: content-collector
version: 1.0.0
description: >
  个人内容收藏与知识管理系统。收藏、整理、检索、二创。
  Use when: (1) 用户分享链接/文字/截图并要求保存或收藏,
  (2) 用户说"收藏这个"/"存一下"/"记录下来"/"save this"/"bookmark"/"clip this",
  (3) 用户要求按关键词/标签搜索之前收藏的内容,
  (4) 用户要求基于收藏内容生成小红书/社交媒体文案（二创/改写/洗稿）,
  (5) 用户发送 URL 并要求提取/总结/摘要内容,
  (6) 用户提到"之前看过一个..."/"上次收藏的..."等回忆性检索,
  (7) 用户转发或粘贴了一段内容（文章片段/推文/视频链接）并暗示想留存。
  即使用户没有明确说"收藏"，只要涉及保存外部内容、整理知识、检索历史收藏、
  或基于已收藏内容进行二次创作，都应使用此技能。
  已支持来源：博客、X/Twitter、网页、B站视频。
  内容类型：文字、长视频（B站可自动转录）、短视频。
---

# Content Collector — 个人内容收藏系统

收藏好内容 → 结构化整理 → 关键词检索 → 二次创作

## 数据位置

### 主存储（AI 检索用）
`<WORKSPACE>/collections/`

```
collections/
├── articles/       # 文章、博客、长文
├── tweets/         # X/Twitter 推文、短内容
├── videos/         # 视频内容（转录+笔记）
├── wechat/         # 微信公众号文章
├── ideas/          # 零散想法、灵感
├── index.md        # 全局索引（自动维护）
└── tags.md         # 标签索引（自动维护）
```

### Obsidian 同步（人工浏览用，可选）
`<YOUR_OBSIDIAN_VAULT>/收藏/`

```
收藏/
├── 文章/           # ← collections/articles
├── 视频/           # ← collections/videos
├── 推文/           # ← collections/tweets
├── 公众号/         # ← collections/wechat
└── 想法/           # ← collections/ideas
```

**每次收藏时必须同时写入两个位置。** Obsidian 版本的差异：
1. **文件名**：用中文标题（从 frontmatter title 取），不用 `YYYY-MM-DD-slug` 格式
2. **标签**：frontmatter 保留 `tags` 数组 + 正文第一行加 `#tag1 #tag2 ...` 格式（Obsidian 图谱和搜索用）
3. **aliases**：frontmatter 加 `aliases: [title]`，方便 Obsidian 双链搜索
4. **目录映射**：`articles→文章`、`videos→视频`、`tweets→推文`、`wechat→公众号`、`ideas→想法`

**Obsidian 写入模板**（伪代码）：
```
target_dir = <YOUR_OBSIDIAN_VAULT>/收藏/{中文目录}/
filename = sanitize(title).md   # 去掉 <>:"/\|?* 等非法字符，截断80字符
content = 原始 frontmatter（加 aliases） + "\n\n" + "#tag1 #tag2 ..." + "\n\n" + body
```

## 收藏工作流

### Supadata API（优先方案）
对于大部分 URL，优先使用 Supadata API 解析：
- 脚本：`SUPADATA_API_KEY=<key> python3 scripts/supadata_fetch.py <command> <url>`
- 环境变量：`SUPADATA_API_KEY` 存放在 TOOLS.md

| 内容类型 | 命令 | 说明 |
|---------|------|------|
| 网页/博客 | `web <url>` | 返回 Markdown 正文，1 credit |
| 视频转录 | `transcript <url> --text [--lang zh]` | YouTube/TikTok/X/Instagram/Facebook，1-2 credits |
| 社交媒体元数据 | `metadata <url>` | 标题、作者、互动数据，1 credit |

Supadata 不可用时的降级方案：
- 网页 → `web_fetch`
- B站 → 本地 bilibili 脚本（见下方）
- 需登录/内网 → Chrome Relay

### URL 内容（文章/博客/网页）
1. **优先** `supadata_fetch.py web <url>` 抓取正文
2. **降级** `web_fetch` 抓取正文
3. 提取标题、作者、发布日期、正文摘要、关键词
4. **提取有价值的插图**（默认执行，见下方「插图保存规范」）
5. 生成 `collections/articles/YYYY-MM-DD-slug.md`（含插图引用）
6. **HTML 快照保存**（仅重要文章）：对 P0/P1 级别的文章，额外保存一份原始 HTML 到 `collections/articles/YYYY-MM-DD-slug.html`，防止源页面删除后内容丢失。普通收藏不保存快照（避免磁盘膨胀）
7. **同步到 Obsidian** → `<YOUR_OBSIDIAN_VAULT>/收藏/文章/{标题}.md`（含插图复制）

### 视频内容（YouTube/TikTok/X/Instagram/Facebook）
1. **元数据**: `supadata_fetch.py metadata <url>`
2. **转录**: `supadata_fetch.py transcript <url> --text --lang zh`
3. **内容提取**：基于转录文本提取核心观点、金句、要点
4. 生成 `collections/videos/YYYY-MM-DD-slug.md`
5. **同步到 Obsidian** → `<YOUR_OBSIDIAN_VAULT>/收藏/视频/{标题}.md`

### 纯文本/截图
1. 截图用 `image` 工具提取文字
2. 整理成结构化格式，来源可选补充

### B站视频（本地流程，Supadata 不支持 B站）
1. **元数据**：`python3 scripts/bilibili_extract.py <bvid_or_url>` → 标题、作者、时长、标签、数据指标
2. **评论区**：
   - 无登录（API）：3条热门
   - 已登录（浏览器 shadow DOM）：20+条，见 `references/bilibili-comments.md`
3. **视频转录**：`bash scripts/bilibili_transcribe.sh <bvid_or_url> [model]`
   - 依赖：yt-dlp、faster-whisper（uv）、opencc
   - 需浏览器已登录B站（yt-dlp 读取 cookie）
   - 模型：tiny/base(默认)/small/medium，base 约10-15分钟转录46分钟视频
   - 输出：`/tmp/bilibili_audio/<BVID>_transcript.json` + `.txt`
   - 注意：ASR 有识别错误，专有名词需人工校验
   - **降级方案**（转录失败时）：
     - yt-dlp cookie 过期 → 提示用户在 openclaw browser 重新登录 B站
     - faster-whisper 不可用 → 尝试 `whisper` CLI（`pip3 install openai-whisper`）
     - 全部失败 → 仅保存元数据+评论，在收藏文件中标注"转录未获取，待补充"，不阻塞收藏流程
4. **内容提取**：基于转录文本提取核心观点、金句、要点
5. 生成 `collections/videos/YYYY-MM-DD-slug.md`
6. **同步到 Obsidian** → `<YOUR_OBSIDIAN_VAULT>/收藏/视频/{标题}.md`

## 插图保存规范

**收藏文章时默认提取有价值的插图**，作为后续写作素材。

### 判断标准（哪些图值得保存）
- ✅ 架构图、流程图、框架图、对比图、数据可视化
- ✅ 概念说明图、示意图、信息图
- ❌ 装饰性 banner、logo、头像、广告
- ❌ 纯文字截图（直接引用文字更好）

### 操作流程
1. **发现插图**：用 browser `evaluate` 提取页面 `<img>` 列表（src + alt + caption）
2. **筛选**：排除装饰性图片（logo、小于 200px、SVG 图标等）
3. **下载**：用 CDN 原始 URL（避免 Next.js 等图片优化层），`curl -sL` 保存到：
   - collections 路径：`collections/{category}/images/{slug}/01-描述.png`
   - slug 与收藏文件的文件名 slug 一致
4. **嵌入收藏文件**：在正文中用 `## 插图` 章节，每张图包含：
   - `![alt](images/{slug}/filename.png)`
   - 斜体说明文字（来自 caption 或自行总结）
5. **同步到 Obsidian**：
   - 复制图片到 `<YOUR_OBSIDIAN_VAULT>/收藏/{中文目录}/images/{slug}/`
   - Obsidian 版本使用相同的相对路径引用

### 命名规范
- 文件名：`{序号}-{简短英文描述}.png`（如 `01-architecture-overview.png`）
- 目录名：与收藏文件 slug 一致（如 `evals-for-agents`）

### 注意
- 图片保存为本地副本，不依赖外部 URL（防止链接失效）
- 单篇文章通常 3-8 张有价值的图，不要过度收集

## 关联项目（自动匹配）

每次收藏内容后，自动将内容与当前活跃项目关联：

1. 读取 `<WORKSPACE>/memory/topics/projects.md` 获取活跃项目列表
2. 将收藏内容的标题、摘要、标签与每个项目的关键词匹配
3. 匹配到的项目写入收藏文件的 YAML frontmatter：
   ```yaml
   related_projects: ["wemp-ops", "xiaohongshu-ops"]
   project_notes: "这个案例可以用于公众号选题：AI调度人力的真实案例"
   ```
4. 同时在 `index.md` 中标注关联项目，方便按项目筛选素材

### 项目关键词（自动从 projects.md 提取）
- **wemp-ops**：公众号、写作、文章、排版、内容运营
- **xiaohongshu-ops**：小红书、笔记、种草、配图、短内容
- **content-collector**：收藏、知识管理、素材库

### 使用场景
- 写公众号文章前：`搜索关联 wemp-ops 的收藏` → 快速找到素材
- 写小红书前：`搜索关联 xiaohongshu-ops 的收藏` → 找到适合拆解的内容
- 选题会议：按项目汇总最近收藏 → 发现选题方向

## 存储格式

文件命名：`YYYY-MM-DD-slug.md`

```yaml
---
title: "标题"
source: "来源平台"
url: "原始链接"
author: "作者"
date_published: "发布日期"
date_collected: "收藏日期"
tags: [tag1, tag2, tag3]
category: "articles|tweets|videos|wechat|ideas"
language: "zh|en"
summary: "一句话摘要"
# 视频专属（可选）
duration: "时长"
platform: "bilibili|youtube"
bvid: "BV号"
stats: { views: 0, likes: 0, comments: 0 }
---
```

### 内容结构

- **内容概览**（条件触发，见下方规则）— Mermaid 图，一图看懂全文
- **核心观点** — 3-7个要点
- **要点摘录** — 原文金句（blockquote）
- **热门评论精选**（视频类）— 含点赞数
- **评论区观点摘要**（视频类）— 总结争议点
- **我的笔记** — 用户个人批注，后续补充
- **原文摘要** — 200-500字概要

### 英文内容翻译规范

当 `language: en` 时，收藏过程中的翻译遵循以下规则：

**翻译风格**（默认 storytelling，不需要每次询问）：

| 风格 | 效果 | 适用 |
|------|------|------|
| `storytelling` | 叙事流畅，过渡自然（**默认**） | 博客、观点文、技术分享 |
| `technical` | 精准简洁，术语密集 | API 文档、技术规范 |
| `conversational` | 口语化，像朋友聊天 | Twitter thread、播客转录、访谈 |
| `formal` | 正式结构化 | 学术论文、白皮书 |

**触发条件**：老板说"精翻"→ 用更仔细的翻译；说"学术风格"→ formal；默认不问直接用 storytelling。

**术语表**：翻译时参照 `<WORKSPACE>/references/glossary-ai-zh.md` 统一术语。首次出现的术语用 `中文（English）` 格式。

**欧化检查**：翻译后扫一遍欧化中文问题（多余连接词/被动语态/名词堆砌），参照 `wemp-ops/references/style-guide.md` 的"欧化中文自检"。

### 内容概览图生成规则

**触发条件**：正文 > 1000 字的 articles / wechat / videos（短推文、零散想法不画）。

**输出格式**：Mermaid 代码块，直接嵌入收藏文件的 `## 内容概览` 章节。Obsidian 原生渲染，不需要额外插件。

**图表类型自动选择**（按文章内容匹配）：

| 文章特征 | 图表类型 | Mermaid 语法 | 示例 |
|---------|---------|-------------|------|
| 方法论/框架/模型（分层、组件） | 思维导图 | `mindmap` | "AI PM 的 3 个核心能力" |
| 流程/步骤/演进（先后顺序） | 流程图 | `graph TB` | "AI 编程三次进化" |
| 对比/选择（A vs B） | 对比图 | `graph TB` + 并行 subgraph | "传统 PM vs AI PM" |
| 多实体互动/依赖关系 | 关系图 | `graph LR` | "Agent 各模块数据流" |
| 时间线/里程碑 | 时间线 | `graph LR` 线性 | "2024 AI 大事记" |
| 混合/不确定 | 思维导图 | `mindmap`（万能兜底） | — |

**生成要求**：
1. **节点文字用文章原始术语**，不用"概念1"、"模块A"等占位符
2. **层级不超过 3 层**——图是辅助理解，不是完整复述
3. **节点数量 5-15 个**——太少没信息量，太多一眼看不完
4. **遵守 Mermaid 语法规范**——详见 `references/mermaid-syntax-rules.md`，特别注意：
   - `1. ` 触发列表解析错误 → 用 `①` 或 `(1)` 或去掉空格
   - subgraph 带空格 → 用 `subgraph id["显示名"]` 格式
   - 节点引用用 ID 不用显示文本
   - 不要在节点文本中使用 Emoji
5. **配色使用语义色**：
   - 核心概念：`fill:#d3f9d8,stroke:#2f9e44`（绿）
   - 问题/挑战：`fill:#ffe3e3,stroke:#c92a2a`（红）
   - 方法/工具：`fill:#e5dbff,stroke:#5f3dc4`（紫）
   - 输出/结果：`fill:#c5f6fa,stroke:#0c8599`（青）

**嵌入格式示例**：
```markdown
## 内容概览

\`\`\`mermaid
mindmap
  root((AI PM 核心能力))
    问题定义
      从模糊需求到精确问题
      判断什么值得做
    上下文质量
      Context Engineering
      给 Agent 正确的信息
    判断力
      评估 Agent 产出
      知道何时人工介入
\`\`\`
```

**不做什么**：
- 不生成独立图片文件——Mermaid 文本直接嵌入 Markdown
- 不画太复杂的图——收藏文件的图是"速览"，不是完整笔记

## Obsidian 同步规范

每次写入 `collections/` 后，**必须**同时写入 Obsidian 版本。步骤：

1. 从刚写入的收藏文件读取 frontmatter
2. 构建 Obsidian 版本：
   - 保留 frontmatter 的 `title, source, url, author, date_published, date_collected, category, language, summary, duration, platform, bvid, tags`
   - 添加 `aliases: [title]`
   - 正文第一行加 `#tag1 #tag2 ...`（标签中的空格替换为 `_`）
3. 文件名 = `sanitize(title).md`（去掉 `<>:"/\|?*`，截断 80 字符）
4. 写入到 `<YOUR_OBSIDIAN_VAULT>/收藏/{中文目录}/`

目录映射：
| collections 目录 | Obsidian 目录 |
|---|---|
| articles/ | 文章/ |
| videos/ | 视频/ |
| tweets/ | 推文/ |
| wechat/ | 公众号/ |
| ideas/ | 想法/ |

**注意**：Obsidian 版本是 collections 的只读镜像。编辑应在 collections 原文件上进行，然后重新同步。

## 索引

每次收藏后更新：
- **index.md** — 按月份倒序，含标签和来源
- **tags.md** — 按标签聚合所有收藏

## 检索

1. 标签匹配：`tags.md` 中查找
2. 全文搜索：`grep -ril "keyword" collections/`
3. 返回匹配列表 + 摘要

## 二创 — 小红书内容生成

1. 按选题/标签从收藏库筛选素材
2. 参考 `references/xiaohongshu-style.md` 写作风格
3. 生成：emoji标题 + 口语化正文(300-800字) + 话题标签(5-10个)
4. 发布配合 `xiaohongshu-ops` 技能

## 联动 — 公众号写作供料

收藏库是 `wemp-ops` 公众号写作的素材来源之一。wemp-ops 选题时会自动检索收藏库：
- 标签匹配：`tags.md` 按关键词查找相关收藏
- 全文搜索：`grep -ril` 搜索 collections/ 目录
- 收藏文件中的"核心观点"、"要点摘录"、"我的笔记"可直接用于文章引用

**收藏时的写作友好建议**：
- `summary` 写清楚，便于快速判断是否相关
- `tags` 覆盖主题关键词，提高检索命中率
- "我的笔记"多写自己的思考和联想，这些是文章的独特视角

## 分类规则

| 来源 | 目录 | 备注 |
|------|------|------|
| 博客/网页 | `articles/` | 默认归类 |
| X/Twitter | `tweets/` | 短内容/thread |
| 微信公众号 | `wechat/` | 中文长文 |
| B站/YouTube/抖音 | `videos/` | B站可自动转录 |
| 零散想法 | `ideas/` | 非外部来源 |

## 标签规范

- 中文为主，英文专有名词保持英文
- 每条 3-8 个标签
- 常用：`AI`、`产品设计`、`电商`、`运营`、`技术`、`商业`、`创业`、`效率工具`、`思维模型`、`管理`

## 写作素材交接（Skill Handoff）

收藏完成后，检查内容是否与选题池中的选题相关：

1. 读 `<WORKSPACE>/collections/topics/topic-pool.md`（公众号）和 `<WORKSPACE>/collections/topics/xhs-topic-pool.md`（小红书）
2. 如果收藏内容的标签/主题与某个选题匹配，追加到 `<WORKSPACE>/temp/handoffs/collector-to-writing.md`：
   ```markdown
   ### <收藏标题>
   - 关联选题：<匹配到的选题>
   - 来源：<URL>
   - 收藏时间：<日期>
   - 可用角度：<这个素材可以怎么用在文章里，1-2句话>
   ```
3. 追加模式（append），不覆盖已有内容
4. 如果没有匹配的选题，跳过此步（不创建空文件）

**注意**：此步骤是补充性的，不替代已有的"关联项目"功能。交接文件面向下游写作 skill，关联项目面向收藏库内部检索。

## 命令速查

| 用户说 | 动作 |
|--------|------|
| "收藏这个 [URL/文字]" | 抓取→整理→存储→更新索引 |
| "搜索 [关键词]" | 搜索收藏库 |
| "最近收藏了什么" | 读 index.md |
| "关于 [标签] 的收藏" | 从 tags.md 筛选 |
| "用 [选题] 写篇小红书" | 二创生成 |
| "给这篇加个笔记" | 更新"我的笔记"部分 |
| "删除这条收藏" | 移除并更新索引 + 删除 Obsidian 对应文件 |
| "重新同步到 Obsidian" | 全量重新同步：`python3 scripts/sync_to_obsidian.py`（skill 目录下） |
