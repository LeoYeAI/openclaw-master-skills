---
name: zhy-wechat-writing
version: 3.6.0
description: Use when generating a complete WeChat article from a topic, with optional source research, evidence tracking, illustration, HTML conversion, and draft-box publishing.
author: zhy
inputs:
  - name: topic
    type: string
    required: true
    description: 文章主题
  - name: urls
    type: array
    required: false
    description: 参考文章URL列表（可选）
  - name: slug
    type: string
    required: false
    description: 文章目录slug（建议使用英文/拼音kebab-case；未提供时会使用ASCII降级方案）
  - name: search_count
    type: integer
    required: false
    default: 5
    description: 网络搜索结果数量（用于检索阶段候选来源数量控制）
  - name: time_range_days
    type: integer
    required: false
    default: 30
    description: 优先检索时间范围（天），用于强调近期资料
  - name: search_sources
    type: array
    required: false
    default: ["official", "community", "practice"]
    description: 检索来源类型集合（official/community/practice）
  - name: with_illustrations
    type: boolean
    required: false
    default: true
    description: 是否在文章完成后自动配图（调用 zhy-article-illustrator 技能）
  - name: with_html_theme
    type: boolean
    required: false
    default: true
    description: 是否输出HTML主题样式文章（调用 zhy-markdown2wechat 技能，生成微信公众号内联样式 HTML）
  - name: illustration_density
    type: string
    required: false
    default: balanced
    description: 配图密度（minimal/balanced/rich），传递给 zhy-article-illustrator
  - name: illustration_upload
    type: boolean
    required: false
    default: false
    description: 是否将配图上传到七牛云图床并替换为 CDN URL，传递给 zhy-article-illustrator
  - name: illustration_aspect_ratio
    type: string
    required: false
    default: "16:9"
    description: 配图宽高比（如 16:9、4:3、1:1），传递给 zhy-article-illustrator
  - name: illustration_prompt_profile
    type: string
    required: false
    default: nano-banana
    description: 配图提示词配置档案，默认 `nano-banana`，强调高完成度编辑视觉与同篇统一风格
  - name: illustration_text_language
    type: string
    required: false
    default: zh-CN
    description: 图片内默认文字语言，默认简体中文
  - name: illustration_english_terms_whitelist
    type: array
    required: false
    default: []
    description: 允许在图片中保留英文展示的术语白名单，如产品名、协议名、缩写
  - name: illustration_image_provider
    type: string
    required: false
    default: xiaomi
    description: 配图生图通道，默认 `xiaomi`，支持 Xiaomi Gemini 兼容接口、Gemini 官方直连或 Gemini 原生代理
  - name: illustration_image_model
    type: string
    required: false
    default: gemini-3.1-flash-image-preview
    description: 配图模型名称，默认使用接口调用时的 `gemini-3.1-flash-image-preview`
  - name: illustration_image_size
    type: string
    required: false
    default: "1K"
    description: 配图图片清晰度/尺寸标识。使用 Xiaomi 接口时默认传 `1K`
  - name: illustration_image_base_url
    type: string
    required: false
    description: 配图 API 基础地址。可传入 Xiaomi Gemini 兼容接口、Gemini 官方地址或自建代理地址；未提供时由配图 skill 自行决定默认值
  - name: post_to_wechat
    type: boolean
    required: false
    default: true
    description: 是否在完成后自动保存到公众号草稿箱（默认不提交发布）
  - name: wechat_profile_dir
    type: string
    required: false
    description: Chrome profile目录（用于复用已登录态，提高发布稳定性）
outputs:
  - name: article_path
    type: string
    description: 最终生成的文章路径
  - name: sources_path
    type: string
    description: 素材证据池路径
  - name: illustrated_article_path
    type: string
    description: 配图后用于发布的文章路径
  - name: illustrations_dir
    type: string
    description: 配图输出目录
  - name: html_article_path
    type: string
    description: HTML主题样式文章路径
  - name: word_count
    type: integer
    description: 文章字数
  - name: review_score
    type: integer
    description: 审稿综合评分
  - name: wechat_draft_status
    type: string
    description: 发布到公众号草稿箱的状态（成功/失败与原因）
---

# 微信公众号写作系统

## Purpose

根据用户提供的主题（可选参考URL），自动完成公众号文章写作全流程：多来源检索与证据池整理、初稿生成、自审润色、参考资料整理，并可选自动配图与保存到公众号草稿箱（不提交发布）。

## When to Use

- 用户请求"写一篇关于XXX的公众号文章"
- 用户请求"生成公众号文章，主题是XXX"
- 用户需要完整的公众号文章创作流程
- 用户希望"写完后自动配图"或"写完后发到公众号草稿箱"

## Prerequisites

执行前需要确认：
- 用户已提供文章主题（`topic`）
- 如有参考文章 URL，可一并提供（`urls`）
- 若 `topic` 为纯中文且未提供 `slug`，建议补充英文/拼音 `kebab-case` 目录名；否则会使用 ASCII 降级方案

## Workflow

按照以下步骤顺序执行（产物默认落盘到 `articles/<slug>/...`，便于复跑与追溯）：

### Phase 0: Preflight

**目标**：确定可稳定复用的目录与路径规范

**操作**：
1. 计算 `slug`
   - 若用户提供 `slug`：直接使用（推荐：英文/拼音kebab-case）
   - 若 `topic` 含拉丁字母/数字：对其做kebab-case
   - 否则降级：`wechat-article-YYYYMMDD`
2. 创建目录：
   - `articles/<slug>/`
   - `articles/<slug>/sources/`
3. 规范：Markdown图片引用必须使用相对路径与 `/` 分隔符

### Step 1: 素材搜集

**目标**：搜集与主题相关的素材，并整理为可追溯的证据池

**操作**：
1. 若用户提供 `urls`：并行使用 `webfetch` 获取内容，提取要点，并记录URL与可获得的发布日期
2. 若用户未提供 `urls`：并行使用 `WebSearch` 做多来源检索（建议覆盖：官方文档 / X(Twitter) / Reddit / 技术论坛 / 微信公众号 / 工程实践）
   - official/authority：官方文档、标准/规范、权威媒体解读
   - community：X(Twitter)、Reddit、论坛/讨论
   - practice：GitHub issues、工程博客、案例复盘
   - 推荐并行 query 模板（按需组合，尽量加年份/时间范围以强调近期）：
     - `{topic} official documentation` / `{topic} release notes 2025 2026`
     - `{topic} site:x.com` / `{topic} site:twitter.com`
     - `{topic} site:reddit.com` / `{topic} site:reddit.com/r/<subreddit>`
     - `{topic} site:github.com issues` / `{topic} site:github.com discussions`
     - `{topic} site:stackoverflow.com` / `{topic} site:news.ycombinator.com`
     - `{topic} site:mp.weixin.qq.com` (公众号)
     - `{topic} 实战 复盘 踩坑 2025 2026` (中文工程实践)
3. 合并去重，按可信度分级（high/medium/low），形成证据池，落盘：
   - `articles/<slug>/sources/evidence.md`

**工具映射**：
- 本流程中的“搜索”使用：`WebSearch`
- 本流程中的“抓取网页内容”使用：`webfetch`

**关于 WebSearch（实现说明）**：
- 优先使用运行环境自带的 `WebSearch` 工具。
- 若当前环境没有可用的 `WebSearch`：用 `webfetch` 抓取公开搜索结果页（SERP），从结果中提取 URL 列表后再并行 `webfetch` 正文内容。

**证据池条目格式（每条必须包含）**：
- title
- url
- published_at（可得则写）
- source_type（official/community/practice）
- key_takeaways（3-6条要点，尽量可直接改写成正文素材）
- confidence（high/medium/low）

**停止条件（建议）**：
- 候选来源 8-12 条，其中 medium/high >= 5 条

**常见失败处理（新增）**：
- X/Reddit 登录墙或无法抓取正文：
  - 优先选择可公开访问的镜像/引用（二手报道需标注 `confidence=low/medium`），或改抓同一观点的博客/论坛转载；
  - 若必须引用原帖：只使用 WebSearch 结果摘要 + 其他独立来源佐证，不编造细节。
- SERP 抓取/解析失败（无 WebSearch 回退路径时）：
  - 改用“站内检索”策略：直接用 `webfetch` 抓官方站点的搜索/博客索引页或 GitHub 搜索页；
  - 仍无法覆盖时：向用户要 3-5 个关键 URL 或指定信息源清单。
- 去重与可信度：
  - 同一事实至少 2 个独立来源佐证；
  - 官方/一手文档优先标 `high`；社区讨论若无落地细节或无交叉验证标 `low`。

**输出**：`sources_path`（证据池路径）

---

### Step 2: 初稿生成

**目标**：基于素材生成公众号文章初稿

**写作要求**：
1. **标题**：吸引眼球，可使用以下技巧
   - 数字型：`5个方法让你...`
   - 提问型：`为什么...？`
   - 对比型：`A与B的区别...`
   - 悬念型：`你不知道的...`

2. **开头**（前3-5行）：
   - 提出痛点或引发共鸣
   - 设置悬念或提出问题
   - 明确文章价值

3. **正文结构**：
   - 使用小标题分段（## 或 ###）
   - 每段200-300字
   - 包含案例、数据支撑
   - 使用列表增强可读性

4. **结尾**：
   - 总结核心观点
   - 引导互动（点赞、在看、评论）
   - 可添加金句或行动呼吁

5. **字数要求**：1500-2500字

6. **可追溯性要求（新增硬约束）**：
   - 关键事实/数据/结论必须能在证据池中找到支撑
   - 文章末尾必须追加 `## 参考资料/来源`（5-10条链接，尽量带日期）

**输出**：Markdown 格式初稿，保存到：`articles/<slug>/article.md`

---

### Step 3: 智能审稿

**目标**：从四个维度审稿，发现问题

**审稿维度**：

| 维度 | 检查要点 | 权重 |
|------|---------|------|
| 逻辑 | 论点清晰、论据充分、推理合理 | 30% |
| 表达 | 语言流畅、无AI痕迹、口语化适度 | 25% |
| 数据 | 数据准确、案例恰当、引用规范 | 25% |
| 结构 | 标题吸引、段落分明、首尾呼应 | 20% |

**新增硬检查**：
- 可追溯性：关键论断是否能在证据池中找到支撑
- 标题一致性：标题承诺是否在正文明确兑现

**审稿操作**：
1. 逐段检查逻辑连贯性
2. 标记AI痕迹词汇（如"综上所述"、"不难看出"等）
3. 验证数据和案例的准确性
4. 检查结构和节奏

**评分标准**：
- 90-100分：优秀，可直接发布
- 80-89分：良好，小幅优化即可
- 70-79分：合格，需要修改
- 70分以下：需要重写

**输出**：审稿报告（包含问题和修改建议），建议保存到：`articles/<slug>/sources/review.md`

---

### Step 4: 润色打磨

**目标**：修复问题，提升文章质量

**润色操作**：

1. **去除AI痕迹**
   - 替换词汇：
     - `综上所述` → `总的来说`
     - `总而言之` → `说到底`
     - `由此可见` → `所以说`
     - `不难看出` → `我们能发现`
     - `众所周知` → `大家都知道`
   - 避免过于书面化的表达

2. **增强口语化**
   - 适当添加：`其实`、`说实话`、`不得不说`
   - 使用短句，避免长难句
   - 加入过渡词，增强流畅度

3. **优化节奏**
   - 长短句结合
   - 适当使用感叹句、反问句
   - 控制段落长度（建议不超过5行）

4. **修复审稿问题**
   - 根据审稿报告逐项修复
   - 补充缺失的数据或案例
   - 调整不合理的结构

**输出**：最终文章

**强制要求（新增）**：
- 最终文章必须保留或补齐 `## 参考资料/来源`
- 参考资料建议保留 5-10 条，按 `official` / `community` / `practice` 分组更佳

---

### Step 5: 保存与输出

**操作**：
1. 创建输出目录（如果不存在）：
   - `articles/<slug>/`
2. 保存文章：
   - `articles/<slug>/article.md`
3. 输出执行摘要：
   - `article_path`
   - `sources_path`
   - 字数统计
   - 审稿评分

---

### Step 6: 自动配图（可选，调用 zhy-article-illustrator）

**触发条件**：`with_illustrations=true`

**目标**：为文章生成统一风格的高完成度配图，并产出插图版文章

**默认策略**：
- `article_path`：使用 `articles/<slug>/article.md`
- `slug`：复用当前文章 slug
- `density`：`illustration_density`（默认 balanced）
- `upload`：`illustration_upload`（默认 false）
- `aspect_ratio`：`illustration_aspect_ratio`（默认 16:9）
- `prompt_profile`：`illustration_prompt_profile`（默认 nano-banana）
- `text_language`：`illustration_text_language`（默认 zh-CN）
- `english_terms_whitelist`：`illustration_english_terms_whitelist`（默认空）
- `image_provider`：`illustration_image_provider`（默认 xiaomi）
- `image_model`：`illustration_image_model`（默认 gemini-3.1-flash-image-preview）
- `image_size`：`illustration_image_size`（默认 1K）
- `image_base_url`：`illustration_image_base_url`（默认 Xiaomi 接口地址，也支持 Gemini 原生代理）

**执行方式**：
1. 优先调用 `zhy-article-illustrator` 的一键流程脚本：
   ```bash
   node <zhy-article-illustrator>/scripts/illustrate-article.ts \
     --article articles/<slug>/article.md \
     --slug <slug> \
     --density <illustration_density> \
     --aspect-ratio <illustration_aspect_ratio> \
     --prompt-profile <illustration_prompt_profile> \
     --text-language <illustration_text_language> \
     --image-provider <illustration_image_provider> \
     --image-model <illustration_image_model> \
     [--image-size <illustration_image_size>] \
     [--image-base-url <illustration_image_base_url>] \
     [--upload]
   ```
2. 若 `illustration_english_terms_whitelist` 非空，则为每个术语追加 `--term <value>`，例如：
   ```bash
   --term Playwright --term Chromium --term Firefox --term WebKit
   ```
3. 默认沿用新版配图策略：
   - 先生成文章级 `visual-bible.md`
   - 再生成 `outline.md` 与 `prompts/`
   - 默认图片内文字为简体中文，仅白名单术语保留英文
   - 同一篇文章内所有图片共享统一风格体系
4. 写作技能在集成时应遵循以下字段映射：
   - `article_path -> --article`
   - `slug -> --slug`
   - `illustration_density -> --density`
   - `illustration_aspect_ratio -> --aspect-ratio`
   - `illustration_prompt_profile -> --prompt-profile`
   - `illustration_text_language -> --text-language`
   - `illustration_image_provider -> --image-provider`
   - `illustration_image_model -> --image-model`
   - `illustration_image_size -> --image-size`
   - `illustration_image_base_url -> --image-base-url`
   - `illustration_upload=true -> --upload`

**输出**：
- `illustrated_article_path`: `articles/<slug>/article.illustrated.md`
- `illustrations_dir`: `articles/<slug>/illustrations/<slug>/`
- `articles/<slug>/illustrations/<slug>/visual-bible.md`
- `articles/<slug>/illustrations/<slug>/outline.md`
- `articles/<slug>/illustrations/<slug>/prompts/`

**失败处理**：单张失败可重试一次；仍失败则记录并继续，最终输出失败清单。若部分图片失败，也应保留 `article.illustrated.md`，并插入图片占位注释。

---

### Step 7: HTML 主题样式输出（可选，调用 zhy-markdown2wechat）

**触发条件**：`with_html_theme=true`

**目标**：使用 `zhy-markdown2wechat` 技能将 Markdown 转换为带微信内联样式的 HTML

**操作**：
1. 选择输入文件：
    - 若 `with_illustrations=true` 且 `articles/<slug>/article.illustrated.md` 存在，则使用该文件
    - 否则使用 `articles/<slug>/article.md`
2. 将选中的 Markdown 文件记为 `<input_markdown>`
3. 调用 `zhy-markdown2wechat` 技能，执行转换脚本：
     ```bash
     node <zhy-markdown2wechat>/scripts/convert.js \
      <input_markdown> \
      <zhy-markdown2wechat>/resources/themes/default.css \
      articles/<slug>/article.zhy.html
     ```
     - 脚本零依赖（纯 Node.js），无需 `npm install`，自动在临时目录处理后清理
     - 输出包含 `<section id="MdWechat">` 容器与完整内联 CSS 样式
     - 如需换肤，可将第二个参数替换为 `resources/themes/` 下的其他主题文件（`apple.css` / `blue.css` / `dark.css` / `green.css` / `notion.css` / `vibrant.css`）
     - `<zhy-markdown2wechat>` 表示当前环境中该技能的安装目录，运行时应以实际路径为准
4. 输入文件示例：
    - 若存在插图版文章：`<input_markdown>=articles/<slug>/article.illustrated.md`
    - 若不存在插图版文章：`<input_markdown>=articles/<slug>/article.md`

**输出**：`html_article_path`（`articles/<slug>/article.zhy.html`）

**失败处理**：记录错误并在执行摘要中注明原因，跳过该步骤并继续后续流程

---

### Step 8: 保存到公众号草稿箱（可选，调用 zhy-wechat-publish）

**触发条件**：`post_to_wechat=true`

**默认行为**：通过微信官方 API 保存到草稿箱，不做最终发布提交

**前置条件**：
- `zhy-wechat-publish` 技能目录下的 `.env` 已配置 `WECHAT_APP_ID` 与 `WECHAT_APP_SECRET`
- 运行机器的公网 IP 已加入微信公众号后台 IP 白名单
- 若要自动生成封面，发布技能依赖的生图环境也必须可用（由 `zhy-article-illustrator` 提供）

**调用方式**：
- 正文必须是带内联样式的 HTML 文件
- 优先使用 Step 7 生成的 `article.zhy.html`；若不存在则跳过本步骤（或先补执行 Step 7）
- 默认推荐的稳定入口是直接调用 `wechat_draft.js`：
  ```bash
  node <zhy-wechat-publish>/scripts/wechat_draft.js \
    --title "文章标题" \
    --file "articles/<slug>/article.zhy.html" \
    [--author "作者"] \
    [--digest "摘要"] \
    [--thumb "封面media_id"] \
    [--source-url "原文链接"] \
    [--need-open-comment "1"] \
    [--only-fans-can-comment "1"]
  ```
- 若希望自动生成封面并发布，也可调用：
  ```bash
  node <zhy-wechat-publish>/scripts/publish_with_cover.js \
    --article "articles/<slug>/article.md" \
    --html "articles/<slug>/article.zhy.html" \
    [--title "文章标题"] \
    [--author "作者"] \
    [--source-url "原文链接"] \
    [--need-open-comment "1"] \
    [--only-fans-can-comment "1"]
  ```
- `<zhy-wechat-publish>` 表示当前环境中该技能的安装目录，运行时应以实际路径为准
- `wechat_draft.js` 未提供 `--thumb` 时会自动读取 `.env` 中的 `WECHAT_DEFAULT_THUMB_MEDIA_ID`
- `publish_with_cover.js` 会自动从文章中提取标题/摘要、生成单张 16:9 封面、上传封面，并将返回的 `media_id` 作为 `thumb_media_id`
- 发布脚本会在上传前自动展开 HTML 中的 `var(--xxx)` 样式变量，避免微信草稿箱丢失颜色与边框样式
- 发布脚本会在上传前自动将正文中的图片上传到微信正文图片接口，并将 `<img src>` 替换为微信返回的图片 URL
- 发布脚本会在上传前将原生列表结构降级为“普通段落 + 圆点/编号”，以兼容微信草稿箱再次进入编辑模式时的列表解析问题

**注意**：
- 脚本零依赖（纯 Node.js >= 16），无需 `npm install`
- 使用 `publish_with_cover.js` 时，需要本机可用 `bun`，因为封面生成会复用现有生图脚本
- 草稿保存后不会自动提交发布，需人工在公众号后台确认
- 标题长度不得超过 64 字符
- 若当前环境没有可用生图配置，优先改用 `wechat_draft.js` 直接上传 HTML，避免自动封面步骤失败

**成功标准**：输出 `上传草稿成功! 草稿 MEDIA_ID: xxx`

**失败排障清单**：

| 错误信息 | 原因与处理 |
|---------|----------|
| `[40013] invalid appid` | AppID 错误，检查发布技能目录下的 `.env` |
| `[40164] invalid ip` | 当前 IP 未加白名单，将报错中的 IP 加入公众号后台 |
| `[40007] invalid media_id` | 封面图 ID 无效，使用 `upload_image.js` 重新上传获取 |
| `缺少 Xiaomi/Gemini/OpenAI API Key` | 自动封面生成依赖的生图环境未配置，检查 `zhy-article-illustrator` 相关 `.env` |
| `article.zhy.html` 不存在 | Step 7 未执行或失败，检查 `with_html_theme=true` |
| 标题过长 | 控制标题 <= 64 字符 |

---

## Data Flow

```
用户输入（topic, urls?, slug?, search_count?, time_range_days?, ...）
         ↓
Preflight（确定slug与目录）
         ↓
素材搜集（WebSearch + webfetch → evidence.md）
         ↓
初稿生成（article.md）
         ↓
智能审稿（含可追溯性/标题一致性）
         ↓
润色打磨（强制References）
         ↓
自动配图（article.illustrated.md + illustrations/）
         ↓
HTML 主题样式输出（zhy-markdown2wechat → article.zhy.html）
         ↓
保存到草稿箱（不提交发布）
```

## Error Handling

| 异常情况 | 处理方式 |
|---------|---------|
| 搜索无结果 | 提示用户提供更多信息或参考URL |
| 参考文章无法访问 | 跳过该URL，继续处理其他素材 |
| 初稿质量过低 | 重新生成或提示用户提供更多素材 |
| 审稿评分<70 | 建议用户检查主题是否合适 |
| 配图失败 | 输出失败清单；可选择补图后再发布 |
| HTML 转换失败 | 记录错误并跳过该步骤（Step 7），继续后续流程 |
| 发布到草稿箱失败 | 输出排障清单（AppID/IP白名单/封面media_id/标题长度） |

## Example Usage

**输入**：
```
topic: "如何提高工作效率"
urls: ["https://mp.weixin.qq.com/xxx"]
search_count: 5
with_illustrations: true
with_html_theme: true
post_to_wechat: true
```

**执行流程**：
1. 搜索"如何提高工作效率"相关文章
2. 获取用户提供的参考文章内容
3. 生成初稿（约1500-2500字）
4. 审稿评分：85分
5. 润色优化后保存

**输出**：
```
article_path: articles/how-to-improve-work-efficiency/article.md
sources_path: articles/how-to-improve-work-efficiency/sources/evidence.md
illustrated_article_path: articles/how-to-improve-work-efficiency/article.illustrated.md
illustrations_dir: articles/how-to-improve-work-efficiency/illustrations/how-to-improve-work-efficiency/
html_article_path: articles/how-to-improve-work-efficiency/article.zhy.html
word_count: 2150
review_score: 92
wechat_draft_status: success
```

## Notes

- 文章风格应符合公众号调性：轻松、有用、有共鸣
- 避免敏感内容和过度营销
- 保持原创性，不要直接复制素材内容
