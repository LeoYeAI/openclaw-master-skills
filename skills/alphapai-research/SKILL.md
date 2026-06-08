---
name: alphapai-research
description: Alpha派金融投研平台API技能，用于调用Alpha派（AlphaPai/PaiPai）的投资研究接口。覆盖五大核心能力：投研知识问答、投研数据检索、投资研究Agent（公司一页纸/业绩点评/调研大纲/主题选股/投资逻辑/可比公司/观点Challenge/行业一页纸/个股选基/主题选基/画图）、股票公告列表查询、投研图表搜索。当用户提到AlphaPai、Alpha派、PaiPai、投研问答、召回数据、公司一页纸、行业一页纸、业绩点评、调研大纲、投资逻辑、可比公司、选基、搜图表等关键词时，务必使用本skill。
metadata:
    version: 1.0
---

# AlphaPai Research Skill

基于Alpha派（AlphaPai）Open API 的投研能力技能。所有 API 调用均通过 `scripts/alphapai_client.py` 的 CLI 完成，无需手动编写请求代码。

## 输出原则

Alpha派各接口的返回内容均由专业投研模型生成，质量高、格式完整，**调用完成后应将原始输出直接呈现给用户，不做二次加工**：

- **禁止总结或压缩**：不得将原文缩写为摘要，不得用自己的语言改写
- **禁止截断**：无论内容多长，必须完整输出，不得以"以上为主要内容"等方式省略
- **保留原始格式**：Markdown 标题层级、加粗、列表、表格、引用块等结构一律原样保留
- **引用来源随正文输出**：若接口返回了参考来源（文档标题、日期、评分等），紧随正文完整呈现

> 若用户明确要求"总结"或"提炼"，则在完整输出原文之后，再额外附上总结，而非替代原文。

## 数据背景

Alpha派是讯兔科技开发的金融投研 AI 应用，具有丰富的投研场景数据。不同数据源对应不同质量与特征，对专业用户的判断至关重要：

- **路演纪要**：A股上市公司业绩会、券商路演、专家交流等一线会议内容
- **券商点评**：分析师每日给机构投资者发送的点评（时效性高，质量参差不齐）
- **微信公众号**：投研相关公众号及上市公司官方公众号内容
- **券商研报**：国内外券商分析师撰写的研究报告
- **公司公告**：上市公司在交易所发布的官方公告（最权威口径）
- **图表与数据**：公告/研报图片、表格，及EDB宏观/行业/个股时序数据

## 首次使用：配置 API Key

```bash
python scripts/alphapai_client.py config --set-key YOUR_API_KEY
# 非默认服务地址时追加：--set-url https://your-host
```

查看当前配置：

```bash
python scripts/alphapai_client.py config --show
```

> 如用户未提供 api_key，向其说明：可在 Alpha 派💻电脑端获取，或联系客户经理。不要在对话中回显完整 api_key。

## 接口一：投研知识问答

向 Alpha派的投研助手 PaiPai 提问，获取答案。按照**输出原则**完整呈现回答正文与引用来源，不做二次总结。

```bash
python scripts/alphapai_client.py qa --question "问题内容" [选项]
```

| 选项                      | 说明                                                                                            |
| ------------------------- | ----------------------------------------------------------------------------------------------- |
| `--question` / `-q`       | 问题内容（必填）                                                                                |
| `--mode Flash\|Think`     | 问答模式（默认 `Flash`）：`Flash`=简单搜索问答，一问一搜一答；`Think`=Wide Search，一问多搜一答 |
| `--context MSG [MSG ...]` | 多轮对话历史，按顺序传入                                                                        |
| `--web-search`            | 开启联网搜索                                                                                    |
| `--deep-reasoning`        | 开启深度推理                                                                                    |
| `--start YYYY-MM-DD`      | 数据筛选开始日期                                                                                |
| `--end YYYY-MM-DD`        | 数据筛选结束日期                                                                                |
| `--json`                  | 输出原始JSON（供程序解析）                                                                      |

**示例：**

```bash
# 基础问答（Flash 模式，默认）
python scripts/alphapai_client.py qa --question "贵州茅台2024年经营情况如何？"

# Think 模式（Wide Search，更广泛检索）
python scripts/alphapai_client.py qa --question "贵州茅台2024年经营情况如何？" --mode Think

# 多轮对话
python scripts/alphapai_client.py qa \
  --question "对行业的影响呢？" \
  --context "云南缺电对哪些公司会造成影响？" "影响主要集中在高耗能行业"

# 联网搜索 + 时间范围
python scripts/alphapai_client.py qa \
  --question "近期新能源车销量趋势" \
  --web-search --start 2025-01-01 --end 2025-03-01
```

## 接口二：投研知识检索（基于RAG技术）

获取会被送入大模型的原始底层原始数据，适合自行加工或构建自定义 RAG 流程。

```bash
python scripts/alphapai_client.py recall --query "查询问题" [选项]
```

| 选项                 | 说明                                                   |
| -------------------- | ------------------------------------------------------ |
| `--query` / `-q`     | 查询问题（必填）                                       |
| `--type TYPES`       | 数据类型，逗号分隔（不传则全类型）                     |
| `--no-cutoff`        | 返回截断前完整内容（默认截断，与送入大模型的数据一致） |
| `--start YYYY-MM-DD` | 数据筛选开始日期                                       |
| `--end YYYY-MM-DD`   | 数据筛选结束日期                                       |
| `--json`             | 输出原始JSON（供程序解析）                             |

**示例：**

```bash
# 检索和召回点评和Q&A类型数据
python scripts/alphapai_client.py recall \
  --query "贵州茅台2024年市值" \
  --type comment,qa \
  --start 2025-01-01 --end 2025-03-20

# 检索和召回全类型完整内容
python scripts/alphapai_client.py recall --query "宁德时代电池技术" --no-cutoff
```

### recallType 枚举值

选择 `--type` 参数时，根据用户意图选择合适的数据类型：

| 类型值                  | 含义                 | 特点                                     |
| ----------------------- | -------------------- | ---------------------------------------- |
| `comment`               | 券商点评             | 时效性最强，分析师每日发送，质量参差不齐 |
| `roadShow`              | 路演会议纪要         | 业绩会、券商路演、专家交流，一线投研内容 |
| `roadShow_ir`           | 上市公司官方路演纪要 | 官方披露，量少                           |
| `roadShow_us`           | 美股 earnings 纪要   | 美股上市公司业绩会                       |
| `roadShow_od`           | 私域会议纪要         | 内部渠道                                 |
| `report`                | 国内券商研报         | 深度分析，时效性较低                     |
| `foreign_report`        | 海外券商研报         | 摩根、花旗等头部机构                     |
| `wechat_public_article` | 微信公众号           | 行业资讯及上市公司官方公众号             |
| `ann`                   | 上市公司官方公告     | 最权威口径，交易所披露                   |
| `vps`                   | 基金定期报告         | 基金持仓、季报等                         |
| `table`                 | 公告/研报数据表格    | 结构化表格数据                           |
| `image`                 | 研报图片             | 产业链图示、指标对比图表                 |
| `qa`                    | 调研/路演中提取的Q&A | 结构化问答对                             |
| `edb`                   | EDB时序数据库        | 宏观、行业、个股时间序列数据             |

## 接口三：股票 Agent

`POST /alpha/open-api/v1/paipai/stock/agent` — SSE 流式，响应结构同接口一。业绩点评场景需先通过接口四获取公告ID。

> **输出要求**：严格遵照**输出原则**。Agent 生成内容通常较长（千字以上），必须完整输出全文，不得以任何形式截断、摘要或改写。Markdown 格式（标题、表格、加粗、列表）和参考来源原样保留。

---

### mode 1 — 个股业绩点评

根据公司公告、业绩会路演、研报，对公司最新财务报告进行点评。

**必填：** `--stock CODE:NAME` `--report-type TYPE` `--report-id ID` `--report-title TITLE` `--report-period PERIOD`（公告信息先用 `report` 命令查询）

**可选：** `--concern TEXT`（用户关注方向）

```bash
# Step 1：查询公告列表，获取 report-id 等信息
python scripts/alphapai_client.py report --code 603380.SH

# Step 2：调用业绩点评
python scripts/alphapai_client.py agent --mode 1 \
  --question "易德龙2025年一季报业绩点评" --stock 603380.SH:易德龙 \
  --report-type 季报 --report-id HANNC002658114224 \
  --report-title "易德龙:2025年第一季度报告" --report-period "2025年一季报"
```

### mode 2 — 公司一页纸

基于最新公告、路演、研报、点评，对公司进行初步完整分析。

**必填：** `--stock CODE:NAME`

**可选：** `--language 中文|英文`（美股公司可选）`--template-text TEXT`（自定义公司一页纸模板，默认为空）

```bash
python scripts/alphapai_client.py agent --mode 2 \
  --question "亿纬锂能（300014.SZ）的公司一页纸" --stock 300014.SZ:亿纬锂能
```

### mode 3 — 个股调研大纲

快速生成调研一家公司时应该问的问题清单。

**必填：** `--stock CODE:NAME`

**可选：** `--template-text TEXT`（调研大纲中希望关注的内容要点，默认为空）

```bash
python scripts/alphapai_client.py agent --mode 3 \
  --question "巨星科技（002444.SZ）的调研问题大纲" --stock 002444.SZ:巨星科技
```

### mode 5 — 主题选股

根据事件、主题、关键词筛选相关股票。（`template` 值自动设为 `1`，无需手动传）

**必填：** `--template-text TEXT`（选股主题，与 `--question` 保持一致）

```bash
python scripts/alphapai_client.py agent --mode 5 \
  --question "和白酒相关的公司" --template-text "和白酒相关的公司"
```

### mode 7 — 投资逻辑

梳理一家公司近期事件，提炼投资逻辑。

**必填：** `--stock CODE:NAME`

**可选：** `--template-text TEXT`（关注的分析要点、维度、指标，默认为空）`--only-answer`（仅返回最终答案，不返回中间过程）

```bash
python scripts/alphapai_client.py agent --mode 7 \
  --question "亿纬锂能（300014.SZ）的公司投资逻辑" --stock 300014.SZ:亿纬锂能
```

### mode 8 — 可比公司

从业务经营、产业链位置上，检索最具对标性的其他公司。（`template` 值自动设为 `1`，无需手动传）

**必填：** `--stock CODE:NAME`

**可选：** `--concern TEXT`（对比过程中关注的话题，如产品参数、技术路线、估值、盈利等）

```bash
python scripts/alphapai_client.py agent --mode 8 \
  --question "比亚迪（002594.SZ）的可比公司" --stock 002594.SZ:比亚迪
```

### mode 9 — 观点 Challenge

利用Alpha派信息，对用户观点进行逻辑挑战，启发多角度思考。（`template` 值自动设为 `1`，无需手动传）

**必填：** `--template-text TEXT`（待 Challenge 的观点，与 `--question` 中观点描述保持一致）

**可选：** `--concern TEXT`（关注焦点，进一步限定 Challenge 范围）`--start / --end YYYY-MM-DD`（检索信息时间范围）

```bash
python scripts/alphapai_client.py agent --mode 9 \
  --question "Challenge该观点：小米汽车未来的增长" \
  --template-text "小米汽车未来的增长" \
  --concern "YU7" --start 2024-10-25 --end 2025-10-24
```

### mode 11 — 行业一页纸

基于最新公告、路演、研报、点评，对一个行业进行初步完整分析（细粒度行业通常更佳）。

**必填：** `--industry NAME`（行业名称）

**可选：** `--template-text TEXT`（自定义行业一页纸模板，默认为空）

```bash
python scripts/alphapai_client.py agent --mode 11 \
  --question "白酒的行业一页纸" --industry 白酒
```

### mode 12 — 个股选基

根据个股及公募基金定期报告，查找持仓个股权重最高的基金。

**必填：** `--stock-list CODE:NAME [...]` `--report-date DATE` `--fund-type TYPE`

**可选：** `--if-annual 0|1`（是否年报，默认0）

```bash
python scripts/alphapai_client.py agent --mode 12 \
  --question "环旭电子、中际旭创、卓胜微的持仓基金" \
  --report-date 2025-09-30 --fund-type 全部 \
  --stock-list 601231.SH:环旭电子 300308.SZ:中际旭创 300782.SZ:卓胜微
```

### mode 13 — 主题选基

根据事件、主题、关键词筛选相关基金。

**必填：** `--report-date DATE` `--fund-type 全部|主动|指数|ETF`

**可选：** `--if-annual 0|1`

```bash
python scripts/alphapai_client.py agent --mode 13 \
  --question "2025三季报持有房地产的主动基金有哪些？" \
  --report-date 2025-09-30 --fund-type 主动
```

### mode 15 — 画图

分析用户 query 并以图片方式展示调研结果，一图胜千言。

**必填：** `--picture-color 主色HEX 辅色HEX` `--picture-style PPT风格|科普风格`

> `--picture-color` 固定传**两个** HEX 值（主色、辅色），不含 `#` 前缀，如 `2A66F6 A5A8AF`，不可多传或少传。

**可选：** `--source 0|1`（0=仅图片，1=图文，默认0）

```bash
python scripts/alphapai_client.py agent --mode 15 \
  --question "黄金" --picture-color 2A66F6 A5A8AF --picture-style 科普风格
```

## 接口四：获取股票公告列表

查询某只股票在交易所公开的公告列表，用于获取业绩点评所需的公告ID。

```bash
python scripts/alphapai_client.py report --code <STOCK_CODE> [--json]
```

**示例：**

```bash
python scripts/alphapai_client.py report --code 603380.SH
```

## 接口五：搜图表

从研报和公告中搜索相关图片和表格。

```bash
python scripts/alphapai_client.py image --query "搜索内容" [选项]
```

| 选项                         | 说明                                                                                |
| ---------------------------- | ----------------------------------------------------------------------------------- |
| `--query` / `-q`             | 搜索内容（必填）                                                                    |
| `--files-range CODE [...]`   | 来源类型代码（可多个，默认不限制）：`3`=内资研报 `8`=外资研报 `6`=公告 `9`=三方研报 |
| `--topk N`                   | 返回数量(1-100，默认50)                                                             |
| `--recall-mode MODE`         | 召回模式: both(默认)/vector_only/es_only                                            |
| `--llm-rank`                 | 使用LLM重排序                                                                       |
| `--start / --end YYYY-MM-DD` | 发布日期范围                                                                        |
| `--json`                     | 输出原始JSON                                                                        |

**示例：**

```bash
python scripts/alphapai_client.py image --query "新能源车销量趋势" --topk 10 --start 2025-01-01
```

## 典型工作流

### 工作流1：投研问答

1. 确认配置存在（`config --show`）
2. 执行 `qa` 命令，回答和引用来源直接输出
3. 格式化呈现给用户

### 工作流2：获取原始数据自定义分析

1. 确认配置存在
2. 执行 `recall` 命令，根据需求选择 `--type` 和时间范围
3. 使用 `--json` 输出原始数据供后续脚本处理

### 工作流3：个股业绩点评（Agent）

1. 确认配置存在
2. 执行 `report --code <CODE>` 查询公告列表，获取 `stockReportId`、`stockReportTitle`、`stockReportPeriod`、`reportType`
3. 执行 `agent --mode 1` 并传入上述公告信息，得到业绩点评

### 工作流4：其他 Agent 场景

1. 确认配置存在
2. 根据场景选择 `--mode`，按接口三参数表传入必填项
3. 格式化呈现回答和引用来源

### 工作流5：图表搜索

1. 确认配置存在
2. 执行 `image --query "..."` 搜索相关图表
3. 从返回的 `imageUrl` 获取图片链接展示给用户

## 升级 Skill

当用户说"帮我升级 alphapai-research skill"或类似意图时，执行以下流程：

1. **获取远程版本信息**：通过 WebFetch 工具拉取安装指引文档：`https://open-api.rabyte.cn/alpha/open-api/v1/file/api-docs/install.md`
2. **解析远程版本**：读取返回文档 frontmatter 中的 `version` 字段
3. **读取本地版本**：读取当前 `SKILL.md` frontmatter 中的 `metadata.version` 字段
4. **版本对比与决策**：
    - 远程版本 == 本地版本 → 告知用户"alphapai-research 已是最新版本（vX.X.X），无需升级。"流程结束
    - 远程版本 > 本地版本 → 按照远程 `install.md` 中的 **升级安装** 流程执行
    - 远程版本 < 本地版本 → 告知用户"本地版本高于远程版本，可能使用了预发布版，跳过升级。"流程结束

> 升级安装的具体步骤（下载、解压、备份、替换、验证）完全遵照远程 `install.md` 文档中的指引执行，无需硬编码在此处。

## 参考文件

| 文件                          | 内容                                             | 何时读取                                       |
| ----------------------------- | ------------------------------------------------ | ---------------------------------------------- |
| `references/api_reference.md` | 完整 API 字段定义、响应结构、枚举值（含5个接口） | 调试异常响应、需要完整字段说明、参数含义不明时 |
| `scripts/alphapai_client.py`  | CLI 源码 + 可导入的 `AlphaPaiClient` 类          | 需要模块化/程序化调用，或排查 CLI 底层行为时   |
