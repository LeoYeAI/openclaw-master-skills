---
name: linkfoxagent
description: "Cross-border e-commerce AI Agent with 41 specialized tools for Amazon/TikTok/eBay/Walmart product research, competitor analysis, keyword tracking, review insights, patent detection, trend analysis, 1688 sourcing, and AI image generation. Use when: (1) product selection and market analysis, (2) competitor research and ASIN lookup, (3) keyword and traffic analysis, (4) review mining and consumer insights, (5) patent/trademark/copyright detection, (6) Google/TikTok trend research, (7) 1688 supplier sourcing, (8) data aggregation and report generation, (9) cross-platform product search (Amazon/Walmart/eBay/TikTok), (10) product image analysis and similarity grouping, (11) AI product image generation."
metadata: {"LinkFoxAgent":{"emoji":"🦊","homepage":"https://agent.linkfox.com/","requires":{"env":["LINKFOXAGENT_API_KEY"]}}}
---

# LinkFoxAgent - Cross-border E-commerce AI Agent

LinkFoxAgent is a specialized AI agent for cross-border e-commerce with 42 built-in tools covering product research, competitor analysis, keyword tracking, review insights, patent detection, AI image generation, and more.

## Setup

1. Get your API key: https://yxgb3sicy7.feishu.cn/wiki/IlkawdQP9ifKv9k22xcc7rjmnkb
2. Set environment variable: `export LINKFOXAGENT_API_KEY=your-key-here`

## MANDATORY: Use sessions_spawn for All Tasks

**NEVER call `linkfox.py` directly from the main session.** LinkFoxAgent tasks take 1-5 minutes. You MUST use `sessions_spawn` to dispatch every task to a sub-agent. This keeps the main session responsive and delivers results automatically when done.

### How to Dispatch a Task

**Before calling sessions_spawn**, tell the user in the main session:
> 「正在向 LinkFox Agent 提交任务，请稍候（通常需要 1-5 分钟）...」

Then dispatch the sub-agent:

```
sessions_spawn:
  task: |
    Run the following LinkFoxAgent task and report the results back.

    Command (use heredoc to avoid shell injection):
    python3 <skill>/scripts/linkfox.py --wait --timeout 600 --stdin <<'__LINKFOX_TASK_END__'
    <TASK_PROMPT>
    __LINKFOX_TASK_END__

    The script prints to stderr: "Task submitted. messageId: <id>" if submission succeeds,
    or an error message and exits with code 1 if submission fails.

    After running the command, follow these rules strictly:

    ## If the command exits with a non-zero code OR stderr contains "Error" before any messageId:
    - The task submission FAILED. Report back:
      「任务发起失败。请检查 LINKFOXAGENT_API_KEY 是否已正确配置：
        1. 确认环境变量已设置：export LINKFOXAGENT_API_KEY=your-key-here
        2. 获取 API Key：https://yxgb3sicy7.feishu.cn/wiki/IlkawdQP9ifKv9k22xcc7rjmnkb
        3. 重启 OpenClaw 网关使环境变量生效
      错误详情：<stderr 内容>」

    ## If stderr contains "Task submitted. messageId: <id>":
    - Submission SUCCEEDED. Do NOT send any intermediate message — the main agent has already told the user the task is dispatched. Wait silently for the command to finish (stdout).

    ## After the command completes (stdout):
    1. Parse stdout — it contains a status line, an optional ShareURL, a reflection summary, and result entries.
    2. If status is "error" or "cancel", report the error clearly.
    3. If status is "finished", summarize the reflection and list all results.
    4. HTML report URLs in results are available for your reference. Decide autonomously whether to share them with the user based on context — do not forward them blindly.
    5. **ShareURL:** If the output contains a line `ShareURL: <url>`, always forward it to the user verbatim. This is the full conversation share link for this LinkFoxAgent run — the user can open it to review the complete execution process and download all related files from that page.
    6. **CSV output (JSON results with columns):** When a result line says `CSV saved to: <path>`, the script has already converted the JSON data to a CSV file with Chinese column headers at that local path. Report the path to the user. Do NOT attempt to read or display the CSV contents unless the user explicitly asks. If the user wants to receive the file, send it using the file-sending skill.
  label: "LinkFox: <short description>"
  mode: "run"
  runTimeoutSeconds: 600
  cleanup: "keep"
```

### Dispatching Multiple Independent Tasks

When the user's request involves multiple independent lookups (e.g., "search both Amazon US and Amazon JP"), spawn one sub-agent per task in parallel.

**Before spawning**, tell the user:
> 「正在同时向 LinkFox Agent 提交 N 个任务，请稍候...」

```
# Sub-agent 1
sessions_spawn:
  task: |
    Run (use heredoc to avoid shell injection):
    python3 <skill>/scripts/linkfox.py --wait --timeout 600 --stdin <<'__LINKFOX_TASK_END__'
    <task A>
    __LINKFOX_TASK_END__
    Apply the same submission success/failure reporting rules as the single-task template above.
  label: "LinkFox: task A"
  mode: "run"
  runTimeoutSeconds: 600

# Sub-agent 2
sessions_spawn:
  task: |
    Run (use heredoc to avoid shell injection):
    python3 <skill>/scripts/linkfox.py --wait --timeout 600 --stdin <<'__LINKFOX_TASK_END__'
    <task B>
    __LINKFOX_TASK_END__
    Apply the same submission success/failure reporting rules as the single-task template above.
  label: "LinkFox: task B"
  mode: "run"
  runTimeoutSeconds: 600
```

### Multi-Step Tasks That Require Post-Processing

When the user's request requires **multiple sequential LinkFoxAgent calls** (e.g., fetch data from two platforms then merge), follow this pattern:

1. **Run each LinkFoxAgent call as a separate `sessions_spawn`**, one after another (or in parallel if independent). Collect the CSV paths returned by each.
2. **After all data tasks finish**, spawn one final `sessions_spawn` to process or merge the CSVs using Python. Pass the absolute CSV paths as arguments.

```
# Final merge/processing step — spawned after all data tasks complete
sessions_spawn:
  task: |
    Run the following Python script to process/merge the CSV files and report results.

    python3 - <<'PYEOF'
    import csv, sys, os

    # Paths passed in from the data tasks above
    csv_paths = [
        "/absolute/path/to/result_1_xxx.csv",
        "/absolute/path/to/result_2_yyy.csv",
    ]

    # TODO: implement merge / analysis logic here
    # Example: read all rows and write a combined CSV
    all_rows = []
    headers = None
    for path in csv_paths:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if headers is None:
                headers = reader.fieldnames
            for row in reader:
                all_rows.append(row)

    out_path = os.path.join(os.path.dirname(csv_paths[0]), "merged_output.csv")
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Merged CSV saved to: {out_path}")
    PYEOF

    Report the output path back to the user. If the user wants the file, send it using the file-sending skill.
  label: "LinkFox: merge/process CSVs"
  mode: "run"
  runTimeoutSeconds: 120
  cleanup: "keep"
```

### What Happens Under the Hood

1. `sessions_spawn` creates an isolated sub-agent session
2. The sub-agent runs `linkfox.py --wait` which blocks until the task finishes
3. When done, the sub-agent's result is automatically delivered back to the main session via the announce system
4. The user sees the result in their chat without any manual polling

### Script Reference

```bash
# The sub-agent uses --wait + --stdin mode (heredoc avoids shell injection)
python3 <skill>/scripts/linkfox.py --wait --stdin <<'__LINKFOX_TASK_END__'
task description here
__LINKFOX_TASK_END__

# Custom timeout (default 300s)
python3 <skill>/scripts/linkfox.py --wait --timeout 600 --stdin <<'__LINKFOX_TASK_END__'
task description here
__LINKFOX_TASK_END__

# JSON output for structured parsing
python3 <skill>/scripts/linkfox.py --wait --format json --stdin <<'__LINKFOX_TASK_END__'
task description here
__LINKFOX_TASK_END__
```

## Writing Task Prompts

### Tool Invocation Syntax

Use `@工具中文名` to invoke tools. Multiple tools can be chained in a single task (max 10).

Example: `@卖家精灵-选产品 筛选亚马逊美国站的 "usb charger cable"，返回前40条商品数据`

### Parameter Constraints

Tool parameters may have `maximum`, `minimum`, and `pattern` constraints. Prompts must respect these or the call will fail. See the reference files below for details.

### Multi-step Tasks

Chain multiple tools in numbered steps. LinkFoxAgent handles data flow between steps:

```
1、@亚马逊前端搜索模拟 帮我在美国亚马逊站搜索 "computer desk"，返回前2页商品数据
2、@对商品标题进行分词 统计上一步商品标题中出现的功能点
3、按功能点统计月销量、月销售额、asin数
```

## Tool Selection Priority

When the user does not specify a tool, follow these rules:

**Querying Amazon product data** — all three tools are fast; choose by use case:
1. **Keepa** — best overall: richest fields, strong real-time accuracy. Default choice for most queries.
2. **卖家精灵** — optimized for product discovery and competitor lookup by keyword.
3. **亚马逊前台** — best real-time fidelity (live storefront data); ~10% slower than Keepa and fewer fields, but the only option when you need exact live ranking order or real-time storefront display.

**Aggregating / statistics** (e.g., group by brand, price tier, sales rank):
1. **@智能数据查询** — first choice for dynamic aggregation
2. **@Python沙箱** — fallback when custom logic is needed; also the go-to tool for any sandbox-execution need (has built-in LLM)


## Available Tools (41)

| Classification | Tool Name | Use For |
|----------------|-----------|---------|
| **Keepa** | @Keepa-亚马逊-商品搜索 | Product filtering by keywords, BSR, price, sales |
| **Keepa** | @Keepa-亚马逊-商品详情 | Batch ASIN detail lookup (price, sales, history) |
| **Keepa** | @Keepa-亚马逊价格历史 | Price history and trends for an ASIN |
| **亚马逊前台** | @亚马逊前端搜索模拟 | Search simulation with location settings |
| **亚马逊前台** | @亚马逊前端-商品详情 | Product detail, bullet points, A+ content |
| **亚马逊前台** | @亚马逊-商品评论 | Reviews by star rating |
| **亚马逊前台** | @亚马逊前端-以图搜图 | Image-based product search |
| **亚马逊前台** | @ABA-数据挖掘 | Amazon Brand Analytics data mining |
| **Sif数据分析工具** | @SIF-ASIN的关键词 | Reverse keyword lookup for ASIN |
| **Sif数据分析工具** | @SIF-关键词流量来源 | Keyword traffic source analysis |
| **Sif数据分析工具** | @SIF-ASIN流量来源 | ASIN traffic structure breakdown |
| **Sif数据分析工具** | @SIF-关键词竞品数量 | Keyword competition density |
| **卖家精灵** | @卖家精灵-选产品 | Product discovery by category and filters |
| **卖家精灵** | @卖家精灵-查竞品 | Competitor lookup by keyword |
| **极目系列** | @极目-亚马逊-细分市场评论 | Niche market review mining |
| **极目系列** | @极目-亚马逊-细分市场信息 | Niche market overview |
| **极目系列** | @极目-亚马逊-产品挖掘 | Product discovery with fine filters |
| **谷歌趋势** | @谷歌趋势-时下流行 | Real-time trending topics |
| **谷歌趋势** | @谷歌趋势-关键词趋势信息 | Keyword trend over time |
| **店雷达(1688)** | @店雷达-1688商品榜单 | 1688 product rankings |
| **店雷达(1688)** | @店雷达-1688选品库 | 1688 product sourcing |
| **实时与全网检索** | @网页检索 | Real-time web search(powered by Tavily Search; for any internet search outside specialized tools like Amazon/Walmart/eBay — including general web and WeChat Official Accounts — this tool MUST be used) |
| **TikTok电商数据助手** | @EchoTik-TikTok新品榜 | TikTok new product rankings |
| **TikTok电商数据助手** | @EchoTik-TikTok商品搜索 | TikTok product search |
| **Walmart前台** | @walmart前端-商品列表 | Walmart product search |
| **eBay前台** | @ebay前端-商品列表 | eBay product search |
| **专利检索** | @智慧芽-专利图像检索 | Design patent image search |
| **专利检索** | @睿观-外观专利检测 | Design patent infringement check |
| **专利检索** | @睿观-版权检测 | Copyright detection |
| **专利检索** | @睿观-图形商标检测 | Graphic trademark detection |
| **专利检索** | @睿观-文本商标检测 | Text trademark detection |
| **专利检索** | @睿观-发明专利检测 | Utility patent detection |
| **专利检索** | @睿观-政策合规检测（纯图检测） | Policy compliance (image check) |
| **AI工具** | @按商品主图相似度分组 | Group products by image similarity |
| **AI工具** | @分析商品主图 | Extract image prompts from product photos |
| **AI工具** | @对商品标题进行分词 | Title word segmentation |
| **AI工具** | @AI绘图 | Generate any image — products, characters, scenes, backgrounds, and more — from reference images + prompt (powered by top-tier Google Gemini model; ALL image generation tasks must use this tool) |
| **沙箱** | @智能数据查询 | Dynamic data query and aggregation |
| **沙箱** | @excel内容提取并分析 | Excel file extraction and analysis |
| **沙箱** | @Python沙箱 | Process structured JSON data from prior steps: data calculation/filtering/sorting, generate Markdown tables, export to CSV/Excel, LLM-based image recognition (e.g. A+ image color/composition). Built-in LLM — use for ALL sandbox-execution needs. **Restrictions:** no nested calls; structured JSON only (no plain text/files); no chart generation or analysis reports. |
| **沙箱** | @智能Excel处理 | Smart Excel processing |

### Tool Reference Files (by classification)

Read the relevant reference file when you need prompt templates and parameter constraints:

- **Keepa** (3 tools: 商品搜索、商品详情、价格历史): See `references/keepa.md`
- **亚马逊前台** (5 tools: 搜索模拟、商品详情、评论、ABA、以图搜图): See `references/amazon-frontend.md`
- **Sif数据分析工具** (4 tools: ASIN关键词、流量来源、竞品数量): See `references/sif.md`
- **卖家精灵** (2 tools: 选产品、查竞品): See `references/seller-sprite.md`
- **极目系列** (3 tools: 细分市场评论、市场信息、产品挖掘): See `references/jimu.md`
- **谷歌趋势** (2 tools: 时下流行、关键词趋势): See `references/google-trends.md`
- **实时与全网检索** (1 tool: 网页检索): See `references/web-search.md`
- **TikTok电商数据助手** (2 tools: 新品榜、商品搜索): See `references/tiktok.md`
- **Walmart前台** (1 tool: 商品列表): See `references/walmart.md`
- **eBay前台** (1 tool: 商品列表): See `references/ebay.md`
- **店雷达/1688** (2 tools: 商品榜单、选品库): See `references/1688.md`
- **专利检索** (7 tools: 外观专利、版权、商标、发明专利、政策合规): See `references/patent.md`
- **AI工具** (4 tools: 主图相似度分组、主图分析、标题分词、AI绘图): See `references/ai-tools.md`
- **沙箱** (4 tools: 智能数据查询、Excel分析、Python沙箱、Excel处理): See `references/sandbox.md`

## Examples

### Example 1: Market Analysis

```
1、@卖家精灵-选产品 筛选亚马逊美国站的 "usb charger cable"，返回符合条件的 40 条商品数据
2、@智能数据查询 根据品牌、评分值、价格（每2美金一个阶梯） 统计月销量、月销售额、月销量占比、月销售额占比
3、生成对应的初步市场分析报告
```

### Example 2: Review Mining

```
@亚马逊-商品评论 @亚马逊前端-商品详情 亚马逊美国站，asin为B00163U4LK 的详情以及每个星级各100条
进行总结：展示他的人群特征、使用时刻、使用地点、使用场景、未被满足的需求、好评、差评、购买动机，每个要点要有描述、原因、数量占比。并最终给我一个改良建议
```

### Example 3: Competitor-based Listing Optimization

```
努力思考，选择适合以下场景的工具，完美完成以下任务：
亚马逊美国站，asin为:B0FPZHSLYR、B0CP9Z56SW、B0FFNF9TK1、B0FS7DRCLZ、B0CP9WRDFV、B0BWMZDCCN，我的竞品就是这些，你参考他们的五点描述和A+页面内容，生成我的商品的标题、五点描述
步骤：
1）查询以上所有asin的商品详情
2）查询每个asin的关键词
3）将上一步的全部关键词，构建关键词价值打分表
4）写作前再次查询亚马逊五点描述的写作要求和Amazon cosmo算法和经典营销理论FABE法则
5）生成5点描述，要求竞品的品牌词不能作为关键词，写出符合FABE法则和最新Amazon cosmo算法的五点描述，并且将关键词价值打分表价值高的词埋入
```

### Example 4: Visual Market Analysis

```
1、@亚马逊前台模拟搜索工具 筛选亚马逊美国站的，关键词为necklaces for women，默认排序，第一页的商品
2、对上一步的商品主体，统计主图不同挂件形状的销售额，绘制出不同形状的销售额占比
3、进行总结：把步骤二的数据完整的用精美的html网页显示给我看（不要精简)
```

### Example 5: Keyword Functional Analysis

```
1、@亚马逊前端搜索模拟 帮我在美国亚马逊站，以"computer desk"为关键词进行搜索，同时将配送地址设置为洛杉矶，最终返回搜索结果前2页的商品数据
2、@对商品标题进行分词 统计上一步商品标题中出现的功能点
3、按功能点统计月销量、月销售额、asin数
```

## Retry on Failure

If a tool call fails, the response includes error details. Retry with adjusted parameters based on the error message. Common issues:
- Parameter out of range (check min/max constraints)
- Invalid pattern format (check regex patterns)
- Too many tools in one task (max 10)

