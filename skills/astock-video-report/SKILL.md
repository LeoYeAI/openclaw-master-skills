---
name: astock-video-report
description: A股每日复盘视频自动生成。完整工作流：拉取非凸科技真实行情数据 → 抓取热点新闻 → AI 归因分析 → 生成横屏 PPT 幻灯片 → 合成视频+封面图。当用户说「生成今日A股复盘视频」「A股日报」「出今天的复盘」或触发定时任务时使用。
version: 1.0.2
---

# A股每日复盘视频生成

## 快速开始

```bash
# 1. 安装依赖
bash scripts/setup.sh

# 2. 告诉 AI
「帮我生成今天的A股复盘视频」
```

## 依赖

| 依赖 | 安装方式 | 说明 |
|------|---------|------|
| Python 3.7+ | 系统自带 | |
| pillow | `pip install pillow` | 生成幻灯片 |
| fonttools + brotli | `pip install fonttools brotli` | 字体格式转换（首次自动安装） |
| ffmpeg | `brew install ffmpeg` / `apt install ffmpeg` | 合成视频 |
| ftshare-market-data | `skillhub install ftshare-market-data` | 非凸科技行情接口 |
| newsnow-reader | `skillhub install newsnow-reader` | 热点新闻抓取 |

或一键安装：`bash scripts/setup.sh`

## 完整工作流

```
Step 0    依赖检查               →  确认 ftshare-market-data / newsnow-reader 已安装
Step 1    ftshare-market-data   →  拉取涨跌幅榜、成交额榜、大盘指数
Step 2    newsnow-reader         →  抓取当日财经热点（华尔街见闻）
Step 3    AI 归因分析             →  交叉比对数据与新闻，生成每只股票归因
  🔸 检查点①  展示归因摘要 → 用户确认数据和分析
Step 4    make_slides.py         →  生成 7 张 1920×1080 横屏幻灯片
Step 5    用户确认幻灯片          →  发送 7 张预览图，用户确认后才继续
Step 6    make_video.py          →  合成 MP4 视频 + 封面 JPG
Step 7    生成发布文案            →  通知用户文件位置 + 完整文案
Step 8    询问是否发送文件        →  直接发送视频和封面给用户
```

## 输出路径

| 文件 | 默认路径 |
|------|----------|
| 视频（收盘） | `~/astock-output/YYYY-MM-DD-复盘.mp4` |
| 视频（盘中） | `~/astock-output/YYYY-MM-DD-intra-HHMM-复盘.mp4` |
| 封面（收盘） | `~/astock-output/YYYY-MM-DD-封面.jpg` |
| 封面（盘中） | `~/astock-output/YYYY-MM-DD-intra-HHMM-封面.jpg` |
| 幻灯片 | `~/astock-output/slides/YYYY-MM-DD/` |

## 执行时机与数据日期判断

执行前必须先判断当前属于哪种场景，决定数据日期和标注方式：

| 当前时间 | 数据日期 | 幻灯片标注 | 说明 |
|---------|---------|-----------|------|
| 交易日 15:00 后 ~ 23:59 | 当天 | `YYYY-MM-DD 收盘复盘` | 最佳执行时间 |
| 0:00 ~ 次交易日 9:30 前 | 上一个交易日 | `YYYY-MM-DD 收盘复盘` | API 数据仍为上个交易日 |
| 周末 / 节假日 | 最近一个交易日 | `YYYY-MM-DD 收盘复盘` | 同上 |
| 交易日 9:30 ~ 15:00 | 当天（盘中） | `YYYY-MM-DD HH:MM 盘中快报` | 数据为实时快照，非最终结果 |

**判断方法：**
1. 获取当前时间（北京时间）
2. 拉取任意一只股票数据，检查 `symbol_status.extra` 字段：
   - `"CLOSED"` / `"NOT_OPEN"` → 非交易时段，使用最近一个交易日的收盘数据
   - `"TRADING"` / `"CALL_AUCTION"` → 盘中，标注为盘中快报
   - 其他值（如 `"BREAK"` 午休等）→ 按盘中处理，标注当前时间
3. 根据场景自动设置 `--title` 参数：
   - `"CLOSED"` / `"NOT_OPEN"` → `--title "今日 A 股复盘"`
   - `"TRADING"` / `"CALL_AUCTION"` / 其他 → `--title "A 股盘中快报 HH:MM"`（HH:MM 为当前北京时间）
4. `--date` 参数：
   - 收盘场景：传交易日期，如 `"2026-03-16"`
   - 盘中场景：传 `"YYYY-MM-DD-intra-HHMM"`，如 `"2026-03-17-intra-1430"`，避免与收盘视频文件名冲突，且纯 ASCII 保证目录名兼容性

> ⚠️ **`--date` 为必填参数，不能使用系统日期 `date.today()` 默认值。** 必须由 AI agent 根据以上逻辑判断正确的交易日期后显式传入。错误的日期会导致幻灯片标注与实际数据不符。

> ⚠️ 盘中数据为实时快照，涨跌幅和成交额会持续变化。幻灯片和视频中必须标注数据截取时间。

## 执行步骤

> **路径约定**：以下所有脚本路径均使用相对路径。`SKILL_DIR` 指本 skill 所在目录，运行时由 AI agent 自动解析。

### Step 0：检查依赖（自动）

执行前先检查必需的依赖 skill 是否已安装：

1. 检测 `ftshare-market-data` skill 是否存在（尝试定位其 `run.py`）
2. 检测 `newsnow-reader` skill 是否存在（尝试定位其 `scripts/fetch_news.py`）
3. 如果任一缺失，提示用户：
   ```
   ⚠️ 缺少必需的依赖 skill，请先运行：
   bash scripts/setup.sh
   或手动安装：
   skillhub install ftshare-market-data
   skillhub install newsnow-reader
   ```
4. 依赖齐全后，继续 Step 1

### Step 1：拉取行情数据

**1a. 确定交易日期（必须与用户确认）**

先拉取任意一只股票，从返回数据中判断市场状态：
- 检查 `symbol_status.extra`（参考「执行时机与数据日期判断」章节）
- 如果是 `TRADING` / `CALL_AUCTION` / 其他 → 交易日 = 今天，无需确认
- 如果是 `CLOSED` / `NOT_OPEN`（非交易时段）→ **必须询问用户确认数据日期**：
  ```
  当前市场未开盘，API 返回的是最近一个交易日的收盘数据。
  请确认：这份数据对应的交易日是哪天？（例如 2026-03-16）
  ```
  用户回答后，将该日期用于所有 `--date` 参数。

> ⚠️ **禁止自动推算交易日期。** 中国 A 股有节假日调休（如周末补班交易、春节/国庆长假），纯靠星期几推算会出错。必须让用户确认。

**1b. 拉取行情**

使用 `ftshare-market-data` skill 的 `run.py`：

```bash
# 全量 A 股数据（一次拉取，从中提取涨幅/跌幅/成交额 TOP5 + 统计涨跌家数）
python3 <ftshare-market-data>/run.py stock-quotes-list --order_by "change_rate desc" --page_no 1 --page_size 6000 \
  --filter '(ex_id = "XSHE" OR ex_id = "XSHG") AND (latest != null)'

# 从全量数据中提取：
# - 涨幅 TOP5：按 change_rate 降序取前5（过滤 change_rate != null）
# - 跌幅 TOP5：按 change_rate 升序取前5（过滤 change_rate != null 且 < 0）
# - 成交额 TOP5：按 turnover 降序取前5
# - 统计：change_rate>0 为上涨，<0 为下跌
# - 涨停：trading_status == "LIMIT_UP"
# - 跌停：trading_status == "LIMIT_DOWN"
# - 全市场成交额：sum(turnover) / 1e8 得"亿"

# 大盘指数
# 收盘场景：用 close 字段（latest 可能为 null）
# 盘中场景：用 latest 字段（此时为实时价格，close 为昨收）
python3 <ftshare-market-data>/run.py stock-security-info --symbol "000001.SH"  # 上证指数
python3 <ftshare-market-data>/run.py stock-security-info --symbol "399001.SZ"  # 深证成指
python3 <ftshare-market-data>/run.py stock-security-info --symbol "399006.SZ"  # 创业板指
```

> `<ftshare-market-data>` 指 ftshare-market-data skill 的安装目录，AI agent 会自动定位。

### Step 2：抓取热点新闻

```bash
python3 <newsnow-reader>/scripts/fetch_news.py wallstreetcn 8
```

> `<newsnow-reader>` 指 newsnow-reader skill 的安装目录。

### Step 3：AI 归因分析

获取到数据后，对每只涨跌异动股票，结合新闻进行归因：
- 明确有消息面的：直接引用新闻来源
- 无明确消息面的：标注「暂无明确消息面，技术位/资金面分析」
- 不猜测、不编造，不确定的标注「未经验证」

同时提取宏观新闻的市场关联：每条新闻对应受影响的板块或个股。

归因完成后，按以下标准格式展示给用户确认：

```
📊 YYYY-MM-DD A股数据 & AI 归因（收盘复盘 / 盘中快报 HH:MM）

大盘指数
| 指数 | 最新价 | 涨跌幅 |
| 上证指数 | xxxx.xx | ±x.xx% |
| 深证成指 | xxxx.xx | ±x.xx% |
| 创业板指 | xxxx.xx | ±x.xx% |

市场概况
上涨 xxxx 家 | 下跌 xxxx 家 | 涨停 xx 家 | 跌停 xx 家 | 全市场成交额 xxxx 亿

涨幅 TOP5
| 股票 | 代码 | 涨跌幅 | 成交额 | AI 归因 |
| ... | ... | ... | ... | ... |

跌幅 TOP5
（同上格式）

成交额 TOP5
（同上格式）

今日宏观新闻 × 市场关联
| 标签 | 新闻 | AI 关联 |
| ... | ... | ... |
```

展示后询问用户：「数据和归因是否需要调整？确认后开始生成幻灯片。」
- 用户确认后进入 Step 4 生成幻灯片，有修改意见则先调整再继续

### Step 4：生成幻灯片

调用本 skill 的 `scripts/make_slides.py`，传入数据生成 7 张幻灯片：

```bash
python3 scripts/make_slides.py \
  --date "YYYY-MM-DD" \
  --outdir "~/astock-output" \
  --up "名称,代码,涨跌幅,成交额,AI归因|..." \
  --down "..." --vol "..." \
  --news "标签,标题,AI关联|..." \
  --idx "上证点位,涨跌幅,深证点位,涨跌幅,创业板点位,涨跌幅" \
  --stats "上涨家数,下跌家数,涨停家数,跌停家数,全市场成交额" \
  --title "今日 A 股复盘"
```

> `--title` 由 AI agent 根据「执行时机与数据日期判断」章节自动设置，无需用户指定。收盘后传 `"今日 A 股复盘"`，盘中传 `"A 股盘中快报 HH:MM"`。

幻灯片结构（固定 7 张）：
1. 封面（含大盘概览）
2. 涨幅 TOP5 + AI归因
3. 跌幅 TOP5 + AI归因
4. 成交额 TOP5 + AI归因
5. 今日宏观消息 + 市场关联
6. Skill 安装方法（推广页：展示非凸全套 4 个 ftshare 数据包，非本 skill 的硬依赖）
7. 结尾品牌页

### Step 5：用户确认幻灯片（必须）

⚠️ **合成视频前必须先让用户确认幻灯片。** 视频合成耗时较长，修改成本高。

流程：
1. 将 Step 4 生成的 `slides/<date>/` 目录下的 7 张图片发送给用户预览（`<date>` 与 `--date` 参数一致）
2. 询问用户是否满意，重点关注：
   - 数据是否正确（涨跌幅、指数点位）
   - AI 归因是否合理
   - 新闻关联是否准确
3. 用户可能的反馈及处理：
   - **「某只股票归因不对」** → 修改归因文案，重新生成对应幻灯片
   - **「新闻换一条」** → 替换新闻数据，重新生成新闻页（04_今日消息）
   - **「整体没问题」/ 「可以」** → 进入 Step 6 合成视频
   - **「重新生成」** → 回到 Step 3 重新归因分析
4. **只有用户明确确认后，才能执行 Step 6**

### Step 6：合成视频

```bash
python3 scripts/make_video.py \
  --slides-dir "~/astock-output/slides/YYYY-MM-DD" \
  --outdir "~/astock-output" \
  --date "YYYY-MM-DD"
```

BGM 默认使用 skill 自带的 `assets/bgm/eliveta-technology-474054.mp3`，也可通过 `--bgm` 指定其他文件。

> 💡 **建议用户使用自己的 BGM**：多人使用同一首 BGM 容易被视频平台判定为搬运内容。推荐从 [Pixabay Music](https://pixabay.com/music/) 免费下载无版权音乐替换。

### Step 7：生成发布文案

视频合成完成后，根据当天的数据自动生成视频号发布所需的全套文案，格式如下：

**标题（二选一，各20字以内）**

收盘场景：
- 版本 A（悬念式）：结合当日最大涨停股或热点事件，例如：「XX今天涨停，AI告诉了我原因」
- 版本 B（数据式）：结合大盘表现，例如：「3152只股票上涨，AI复盘今日A股」

盘中场景（参考 `references/copywriting.md` 盘中模板）：
- 版本 A：「XX盘中涨停，AI实时分析原因」
- 版本 B：「大盘盘中跳水，AI找到了三个信号」

标题生成规则：
- 优先用当日最亮眼的数据（涨幅最大的股票、最热的新闻事件）
- 带一点悬念或反差感，引发点击欲
- 不超过20字，不堆砌关键词

**话题标签（固定 + 动态）**
```
固定：#AI量化 #A股复盘 #非凸科技 #OpenClaw
动态：根据当日涨停板块 / 热点事件自动补充2-3个，例如 #AI芯片 #新能源 #央行政策
```

**简短话术（视频号正文，100字以内）**
根据当天最大亮点写1-2句引导语，结构：
`[今日亮点一句话] + [AI是如何分析的] + [行动号召]`

例如：
> 今天AI存储板块集体爆发，朗科科技涨停。AI交叉比对新闻，5秒告诉你背后原因。
> 想让AI每天自动给你发这份复盘？评论区有安装方法。

**完整输出格式**

```
✅ 今日 A 股复盘视频已生成

📁 文件
   视频: ~/astock-output/<date>-复盘.mp4
   封面: ~/astock-output/<date>-封面.jpg
   规格: 1920×1080 横屏 · 30fps · 35s
   （<date> 为 --date 参数值，收盘为 YYYY-MM-DD，盘中为 YYYY-MM-DD-intra-HHMM）

📝 发布文案
   标题A: [生成的标题A]
   标题B: [生成的标题B]

   话题: #AI量化 #A股复盘 #非凸科技 #OpenClaw #[动态话题1] #[动态话题2]

   正文:
   [生成的100字以内话术]

⚠️ 数据仅供参考，不构成投资建议
```

### Step 8：发送视频文件

展示完整输出后，询问用户：「需要我把视频和封面直接发给你吗？」

- 用户确认 → 将视频 MP4 和封面 JPG 直接发送给用户
- 用户拒绝 → 告知文件路径，用户自行取用

## 注意事项

- **任何时间都可以执行**，AI agent 会自动判断数据日期和场景
- 最佳执行时间：交易日 15:30 后（收盘数据最完整）
- 盘中执行时，幻灯片会标注数据截取时间，提醒观众数据非最终结果
- 非交易日执行时，自动使用最近一个交易日的数据
- 所有分析仅供参考，不构成投资建议，输出中必须包含免责声明

## ⚠️ 金融数据铁律（最高优先级）

**所有 A 股价格、指数点位、涨跌幅、成交额数据，严禁猜测或估填。**

- 股票行情 → 必须通过 `ftshare-market-data` 实时拉取
- 大盘指数 → 通过 `stock-security-info` 查询真实点位：
  - 上证指数：`000001.SH`
  - 深证成指：`399001.SZ`
  - 创业板指：`399006.SZ`
  - ⚠️ 收盘场景：指数的 `latest` 字段可能返回 null，应使用 `close` 字段
  - ⚠️ 盘中场景：`latest` 字段为实时价格（不为 null），应使用 `latest` 字段；`close` 此时是昨日收盘价
- 上涨/下跌家数、涨停/跌停家数、全市场成交额 → 从 `stock-quotes-list` 全量数据中统计：
  - 拉取全量：`--page_size 6000 --filter '(ex_id = "XSHE" OR ex_id = "XSHG") AND (latest != null)'`
  - 上涨家数：`change_rate > 0` 的数量
  - 下跌家数：`change_rate < 0` 的数量
  - 涨停家数：`trading_status == "LIMIT_UP"` 的数量
  - 跌停家数：`trading_status == "LIMIT_DOWN"` 的数量
  - 全市场成交额：`sum(turnover)` 除以 1e8 得"亿"
  - 如统计失败，传 `"暂无,暂无,暂无,暂无,暂无"`。**不得填写估计值**
- 宁可输出不完整的幻灯片，也不能展示错误的金融数据

## 资产说明

静态资产（字体、BGM）**不随 skill 打包分发**，首次运行时自动下载到 `assets/` 目录。

也可手动预下载：
```bash
python3 scripts/ensure_assets.py
```

### BGM

- 文件：`assets/bgm/eliveta-technology-474054.mp3`（~4.5 MB，首次运行自动下载）
- 来源：[Pixabay Music](https://pixabay.com/music/)
- 授权：Pixabay Content License（免费用于个人和商业用途，无需署名）
- 作者：Eliveta

### 字体

- 文件：`assets/fonts/NotoSansSC-Regular.ttf`（~2.4 MB，首次运行自动下载）
- 来源：[Google Noto Fonts / fontsource CDN](https://fonts.google.com/noto/specimen/Noto+Sans+SC)
- 授权：SIL Open Font License 1.1（可自由分发和使用）
- 备注：如系统已有中文字体（macOS/Windows 通常自带），会优先使用系统字体

## 依赖 Skills

- `ftshare-market-data`（非凸科技行情接口）
- `newsnow-reader`（热点新闻抓取）

## 参考文档

- `references/data-schema.md` — 行情数据字段说明
- `references/copywriting.md` — 发布文案生成规范
