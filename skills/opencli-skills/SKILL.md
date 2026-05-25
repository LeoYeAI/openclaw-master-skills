---
name: opencli
description: Use OpenCLI to fetch data from websites like Twitter, Reddit, Bilibili, Zhihu, Xiaohongshu, YouTube, etc. Triggers: opencli, social media, twitter, reddit, bilibili, zhihu, xiaohongshu, youtube, weibo, hackernews, fetch website data.
license: MIT
version: 1.0.0
config:
  dependencies:
    - opencli (npm install -g @jackwener/opencli)
    - Chrome with Browser Bridge extension
---

# OpenCLI Skill

通过 OpenCLI 从各种网站获取数据，无需 API 密钥，复用 Chrome 登录状态。

## 触发词

- `opencli` - 使用 OpenCLI 命令
- 社交媒体: `twitter`, `reddit`, `weibo`, `zhihu`, `xiaohongshu`, `jike`
- 视频平台: `bilibili`, `youtube`
- 资讯平台: `hackernews`, `bbc`, `reuters`, `linux-do`
- 其他: `v2ex`, `xueqiu`, `weread`, `stackoverflow`

## 前置要求

1. **安装 OpenCLI**: `npm install -g @jackwener/opencli`
2. **安装 Chrome 扩展**: Browser Bridge
3. **Chrome 已登录目标网站**

## 通用选项

```bash
opencli <site> <command> [options]

# 通用选项
--limit <n>      # 限制返回数量
-f, --format     # 输出格式: table, json, yaml, md, csv (默认 table)
-v, --verbose    # 调试输出
```

## 命令完整列表

### antigravity (9 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `dump` | Dump the DOM to help AI understand the UI | - |
| `extract-code` | Extract multi-line code blocks from the current Antigravity conversation | - |
| `model` | Switch the active LLM model in Antigravity | `name` |
| `new` | Start a new conversation / clear context in Antigravity | - |
| `read` | Read the latest chat messages from Antigravity AI | `last` |
| `send` | Send a message to Antigravity AI via the internal Lexical editor | `message` |
| `serve` | - | - |
| `status` | Check Antigravity CDP connection and get current page state | - |
| `watch` | Stream new chat messages from Antigravity in real-time | - |

### apple-podcasts (5 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `episodes` | List recent episodes of an Apple Podcast (use ID from search) | `id`, `limit` |
| `search` | Search Apple Podcasts | `keyword`, `limit` |
| `top` | Top podcasts chart on Apple Podcasts | `limit`, `country` |

### barchart (4 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `flow` | Barchart unusual options activity / options flow | `type`, `limit` |
| `greeks` | Barchart options greeks overview (IV, delta, gamma, theta, vega) | `symbol`, `expiration`, `limit` |
| `options` | Barchart options chain with greeks, IV, volume, and open interest | `symbol`, `type`, `limit` |
| `quote` | Barchart stock quote with price, volume, and key metrics | `symbol` |

### bbc (1 command)

| 命令 | 说明 | 参数 |
|------|------|------|
| `news` | BBC News headlines (RSS) | `limit` |

### bilibili (12 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `download` | 下载B站视频（需要 yt-dlp） | `bvid`, `output`, `quality` |
| `dynamic` | Get Bilibili user dynamic feed | `limit` |
| `favorite` | 我的默认收藏夹 | `limit`, `page` |
| `feed` | 关注的人的动态时间线 | `limit`, `type` |
| `following` | 获取 Bilibili 用户的关注列表 | `uid`, `page`, `limit` |
| `history` | 我的观看历史 | `limit` |
| `hot` | B站热门视频 | `limit` (default: 20) |
| `me` | My Bilibili profile info | - |
| `ranking` | Get Bilibili video ranking board | `limit` |
| `search` | Search Bilibili videos or users | `keyword`, `type`, `page`, `limit` |
| `subtitle` | 获取 Bilibili 视频的字幕 | `bvid`, `lang` |
| `user-videos` | 查看指定用户的投稿视频 | `uid`, `limit`, `order`, `page` |

### boss (6 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `chatlist` | BOSS直聘查看聊天列表（招聘端） | `page`, `limit`, `job_id` |
| `chatmsg` | BOSS直聘查看与候选人的聊天消息 | `uid`, `page` |
| `detail` | BOSS直聘查看职位详情 | `security_id` |
| `resume` | BOSS直聘查看候选人简历（招聘端） | `uid` |
| `search` | BOSS直聘搜索职位 | `query`, `city`, `experience`, `degree`, `salary`, `industry`, `page`, `limit` |
| `send` | BOSS直聘发送聊天消息 | `uid`, `text` |

### chaoxing (2 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `assignments` | 学习通作业列表 | `course`, `status`, `limit` |
| `exams` | 学习通考试列表 | `course`, `status`, `limit` |

### chatgpt (5 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `ask` | Send a prompt and wait for the AI response (send + wait + read) | `text`, `timeout` |
| `new` | Open a new chat in ChatGPT Desktop App | - |
| `read` | Copy the most recent ChatGPT Desktop App response to clipboard and read it | - |
| `send` | Send a message to the active ChatGPT Desktop App window | `text` |
| `status` | Check if ChatGPT Desktop App is running natively on macOS | - |

### chatwise (9 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `ask` | Send a prompt and wait for the AI response | `text`, `timeout` |
| `export` | Export the current ChatWise conversation to a Markdown file | `output` |
| `history` | List conversation history in ChatWise sidebar | - |
| `model` | Get or switch the active AI model in ChatWise | `model_name` |
| `new` | Start a new conversation in ChatWise | - |
| `read` | Read the current ChatWise conversation history | - |
| `screenshot` | Capture a snapshot of the current ChatWise window | `output` |
| `send` | Send a message to the active ChatWise conversation | `text` |
| `status` | Check active CDP connection to ChatWise Desktop | - |

### codex (11 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `ask` | Send a prompt and wait for the AI response | `text`, `timeout` |
| `dump` | Dump the DOM and Accessibility tree of Codex for reverse-engineering | - |
| `export` | Export the current Codex conversation to a Markdown file | `output` |
| `extract-diff` | Extract visual code review diff patches from Codex | - |
| `history` | List recent conversation threads in Codex | - |
| `model` | Get or switch the currently active AI model in Codex Desktop | `model_name` |
| `new` | Start a new Codex conversation thread / isolated workspace | - |
| `read` | Read the contents of the current Codex conversation thread | - |
| `screenshot` | Capture a snapshot of the current Codex window | `output` |
| `send` | Send text/commands to the Codex AI composer | `text` |
| `status` | Check active CDP connection to OpenAI Codex App | - |

### coupang (2 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `add-to-cart` | Add a Coupang product to cart using logged-in browser session | `productId`, `url` |
| `search` | Search Coupang products with logged-in browser session | `query`, `page`, `limit`, `filter` |

### ctrip (1 command)

| 命令 | 说明 | 参数 |
|------|------|------|
| `search` | 携程旅行搜索 | `query`, `limit` |

### cursor (11 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `ask` | Send a prompt and wait for the AI response | `text`, `timeout` |
| `composer` | Send a prompt directly into Cursor Composer (Cmd+I shortcut) | `text` |
| `dump` | Dump the DOM and Accessibility tree of Cursor for reverse-engineering | - |
| `export` | Export the current Cursor conversation | `output` |
| `extract-code` | Extract multi-line code blocks from the current Cursor conversation | - |
| `history` | List recent chat sessions from the Cursor sidebar | - |
| `model` | Get or switch the currently active AI model in Cursor | `model_name` |
| `new` | Start a new Cursor chat or Composer session | - |
| `read` | Read the current Cursor chat/composer conversation history | - |
| `screenshot` | Capture a snapshot of the current Cursor window | `output` |
| `send` | Send a prompt directly into Cursor Composer/Chat | `text` |
| `status` | Check active CDP connection to Cursor AI Editor | - |

### discord-app (7 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `channels` | List channels in the current Discord server | - |
| `members` | List online members in the current Discord channel | - |
| `read` | Read recent messages from the active Discord channel | `count` |
| `search` | Search messages in the current Discord server/channel (Cmd+F) | `query` |
| `send` | Send a message in the active Discord channel | `text` |
| `servers` | List all Discord servers (guilds) in the sidebar | - |
| `status` | Check active CDP connection to Discord Desktop | - |

### feishu (5 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `new` | Create a new message or document in Feishu | - |
| `read` | Read the current chat content by selecting all and copying | - |
| `search` | Open Feishu global search and type a query (Cmd+K) | `query` |
| `send` | Send a message in the active Feishu (Lark) conversation | `text` |
| `status` | Check if Feishu (Lark) Desktop is running on macOS | - |

### grok (1 command)

| 命令 | 说明 | 参数 |
|------|------|------|
| `ask` | Send a message to Grok and get response | `prompt`, `timeout`, `new` |

### hackernews (1 command)

| 命令 | 说明 | 参数 |
|------|------|------|
| `top` | Hacker News top stories | `limit` (default: 20) |

### hf (1 command)

| 命令 | 说明 | 参数 |
|------|------|------|
| `top` | Top upvoted Hugging Face papers | - |

### jike (11 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `comment` | 评论即刻帖子 | `id`, `text` |
| `create` | 发布即刻动态 | `text` |
| `feed` | 即刻首页动态流 | `limit` |
| `like` | 点赞即刻帖子 | `id` |
| `notifications` | 即刻通知 | `limit` |
| `post` | 即刻帖子详情及评论 | `id` |
| `repost` | 转发即刻帖子 | `id`, `text` |
| `search` | 搜索即刻帖子 | `keyword`, `limit` |
| `topic` | 即刻话题/圈子帖子 | `id`, `limit` |
| `user` | 即刻用户动态 | `username`, `limit` |

### jimeng (2 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `generate` | 即梦AI 文生图 — 输入 prompt 生成图片 | `prompt`, `model`, `wait` |
| `history` | 即梦AI 查看最近生成的作品 | `limit` |

### linkedin (1 command)

| 命令 | 说明 | 参数 |
|------|------|------|
| `search` | Search LinkedIn jobs | `query`, `location`, `limit`, `start`, `details`, `company`, `experience_level`, `job_type`, `date_posted`, `remote` |

### linux-do (6 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `categories` | linux.do 分类列表 | `limit` |
| `category` | linux.do 分类内话题 | `slug`, `id`, `limit` |
| `hot` | linux.do 热门话题 | `limit`, `period` |
| `latest` | linux.do 最新话题 | `limit` |
| `search` | 搜索 linux.do | `keyword`, `limit` |
| `topic` | linux.do 帖子详情和回复 | `id` |

### neteasemusic (10 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `like` | Like/unlike the currently playing song | - |
| `lyrics` | Get the lyrics of the currently playing song | - |
| `next` | Skip to the next song | - |
| `play` | Toggle play/pause for the current song | - |
| `playing` | Get the currently playing song info | - |
| `playlist` | Show the current playback queue / playlist | - |
| `prev` | Go back to the previous song | - |
| `search` | Search for songs, artists, albums, or playlists | `query` |
| `status` | Check CDP connection to NeteaseMusic Desktop | - |
| `volume` | Get or set the volume level (0-100) | `level` |

### notion (8 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `export` | Export the current Notion page as Markdown | `output` |
| `favorites` | List pages from the Notion Favorites section in the sidebar | - |
| `new` | Create a new page in Notion | `title` |
| `read` | Read the content of the currently open Notion page | - |
| `search` | Search pages and databases in Notion via Quick Find (Cmd+P) | `query` |
| `sidebar` | List pages and databases from the Notion sidebar | - |
| `status` | Check active CDP connection to Notion Desktop | - |
| `write` | Append text content to the currently open Notion page | `text` |

### reddit (13 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `comment` | Post a comment on a Reddit post | `post_id`, `text` |
| `frontpage` | Reddit Frontpage / r/all | `limit` |
| `hot` | Reddit 热门帖子 | `subreddit`, `limit` |
| `popular` | Reddit Popular posts (/r/popular) | `limit` |
| `read` | Read a Reddit post and its comments | `post_id`, `sort`, `limit`, `depth`, `replies`, `max_length` |
| `save` | Save or unsave a Reddit post | `post_id`, `undo` |
| `saved` | Browse your saved Reddit posts | `limit` |
| `search` | Search Reddit Posts | `query`, `subreddit`, `sort`, `time`, `limit` |
| `subreddit` | Get posts from a specific Subreddit | `name`, `sort`, `time`, `limit` |
| `subscribe` | Subscribe or unsubscribe to a subreddit | `subreddit`, `undo` |
| `upvote` | Upvote or downvote a Reddit post | `post_id`, `direction` |
| `upvoted` | Browse your upvoted Reddit posts | `limit` |
| `user-comments` | View a Reddit user's comment history | `username`, `limit` |
| `user-posts` | View a Reddit user's submitted posts | `username`, `limit` |
| `user` | View a Reddit user profile | `username` |

### reuters (1 command)

| 命令 | 说明 | 参数 |
|------|------|------|
| `search` | Reuters 路透社新闻搜索 | `query`, `limit` |

### smzdm (1 command)

| 命令 | 说明 | 参数 |
|------|------|------|
| `search` | 什么值得买搜索好价 | `keyword`, `limit` |

### stackoverflow (4 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `bounties` | Active bounties on Stack Overflow | `limit` |
| `hot` | Hot Stack Overflow questions | `limit` |
| `search` | Search Stack Overflow questions | `query`, `limit` |
| `unanswered` | Top voted unanswered questions on Stack Overflow | `limit` |

### twitter (19 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `accept` | Auto-accept DM requests containing specific keywords | `keyword`, `max` |
| `article` | Fetch a Twitter Article (long-form content) and export as Markdown | `tweet_id` |
| `bookmark` | Bookmark a tweet | `url` |
| `bookmarks` | Fetch Twitter/X bookmarks | `limit` |
| `delete` | Delete a specific tweet by URL | `url` |
| `download` | 下载 Twitter/X 媒体（图片和视频） | `username`, `tweet-url`, `limit`, `output` |
| `follow` | Follow a Twitter user | `username` |
| `followers` | Get accounts following a Twitter/X user | `user`, `limit` |
| `following` | Get accounts a Twitter/X user is following | `user`, `limit` |
| `like` | Like a specific tweet | `url` |
| `notifications` | Get Twitter/X notifications | `limit` |
| `post` | Post a new tweet/thread | `text` |
| `profile` | Fetch a Twitter user profile (bio, stats, etc.) | `username` |
| `reply-dm` | Send a message to recent DM conversations | `text`, `max`, `skip-replied` |
| `reply` | Reply to a specific tweet | `url`, `text` |
| `search` | Search Twitter/X for tweets | `query`, `limit` |
| `thread` | Get a tweet thread (original + all replies) | `tweet_id`, `limit` |
| `timeline` | Fetch Twitter Home Timeline | `limit` |
| `trending` | Twitter/X trending topics | `limit` |
| `unbookmark` | Remove a tweet from bookmarks | `url` |
| `unfollow` | Unfollow a Twitter user | `username` |

### v2ex (6 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `daily` | V2EX 每日签到并领取铜币 | - |
| `hot` | V2EX 热门话题 | `limit` |
| `latest` | V2EX 最新话题 | `limit` |
| `me` | V2EX 获取个人资料 (余额/未读提醒) | - |
| `notifications` | V2EX 获取提醒 (回复/由于) | `limit` |
| `topic` | V2EX 主题详情和回复 | `id` |

### wechat (6 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `chats` | Open the WeChat chats panel (conversation list) | - |
| `contacts` | Open the WeChat contacts panel | - |
| `read` | Read the current chat content by selecting all and copying | - |
| `search` | Open WeChat search and type a query (find contacts or messages) | `query` |
| `send` | Send a message in the active WeChat conversation via clipboard paste | `text` |
| `status` | Check if WeChat Desktop is running on macOS | - |

### weibo (1 command)

| 命令 | 说明 | 参数 |
|------|------|------|
| `hot` | 微博热搜 | `limit` |

### weread (8 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `book` | View book details on WeRead | `bookId` |
| `highlights` | List your highlights (underlines) in a book | `bookId`, `limit` |
| `notebooks` | List books that have highlights or notes | - |
| `notes` | List your notes (thoughts) on a book | `bookId`, `limit` |
| `ranking` | WeRead book rankings by category | `category`, `limit` |
| `search` | Search books on WeRead | `keyword`, `limit` |
| `shelf` | List books on your WeRead bookshelf | `limit` |

### xiaohongshu (15 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `creator-note-detail` | 小红书单篇笔记详情页数据 | `note_id` |
| `creator-notes-summary` | 小红书最近笔记批量摘要 | `limit` |
| `creator-notes` | 小红书创作者笔记列表 + 每篇数据 | `limit` |
| `creator-profile` | 小红书创作者账号信息 (粉丝/关注/获赞/成长等级) | - |
| `creator-stats` | 小红书创作者数据总览 (观看/点赞/收藏/评论/分享/涨粉，含每日趋势) | `period` |
| `download` | 下载小红书笔记中的图片和视频 | `note_id`, `output` |
| `feed` | 小红书首页推荐 Feed | `limit` |
| `notifications` | 小红书通知 (mentions/likes/connections) | `type`, `limit` |
| `search` | 搜索小红书笔记 | `keyword`, `limit` |
| `user` | Get public notes from a Xiaohongshu user profile | `id`, `limit` |

### xiaoyuzhou (5 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `episode` | View details of a Xiaoyuzhou podcast episode | `id` |
| `podcast-episodes` | List recent episodes of a Xiaoyuzhou podcast (up to 15, SSR limit) | `id`, `limit` |
| `podcast` | View a Xiaoyuzhou podcast profile | `id` |

### xueqiu (6 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `feed` | 获取雪球首页时间线（关注用户的动态） | `page`, `limit` |
| `hot-stock` | 获取雪球热门股票榜 | `limit`, `type` |
| `hot` | 获取雪球热门动态 | `limit` |
| `search` | 搜索雪球股票（代码或名称） | `query`, `limit` |
| `stock` | 获取雪球股票实时行情 | `symbol` |
| `watchlist` | 获取雪球自选股列表 | `category`, `limit` |

### yahoo-finance (1 command)

| 命令 | 说明 | 参数 |
|------|------|------|
| `quote` | Yahoo Finance 股票行情 | `symbol` |

### youtube (5 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `search` | Search YouTube videos | `query`, `limit` |
| `transcript` | Get YouTube video transcript/subtitles | - |
| `video` | Get YouTube video metadata (title, views, description, etc.) | `url` |

### zhihu (4 commands)

| 命令 | 说明 | 参数 |
|------|------|------|
| `download` | 导出知乎文章为 Markdown 格式 | `url`, `output`, `download-images` |
| `hot` | 知乎热榜 | `limit` |
| `question` | 知乎问题详情和回答 | `id`, `limit` |
| `search` | 知乎搜索 | `keyword`, `limit` |

---

## 输出格式

| 格式 | 说明 | 使用场景 |
|------|------|----------|
| `table` | 表格格式（默认） | 人类阅读 |
| `json` | JSON 格式 | 程序处理、数据提取 |
| `yaml` | YAML 格式 | 配置文件、数据序列化 |
| `md` | Markdown 格式 | 文档生成 |
| `csv` | CSV 格式 | 数据分析、Excel 导入 |

## 诊断命令

```bash
# 检查 Browser Bridge 连接状态
opencli doctor

# 实时测试浏览器连接
opencli doctor --live

# 交互式设置
opencli setup

# 列出所有可用命令
opencli list
```

## 注意事项

1. **登录状态**: 浏览器命令复用 Chrome 登录状态，确保已在 Chrome 中登录目标网站
2. **Chrome 扩展**: 必须安装 Browser Bridge 扩展
3. **命令模式**:
   - `[public]` - 公开 API，无需登录
   - `[cookie]` - 需要 Chrome 登录状态
   - `[ui]` - UI 自动化，需要应用在前台运行
4. **输出解析**: 使用 `-f json` 格式便于程序解析
5. **调试**: 使用 `-v` 参数查看详细日志