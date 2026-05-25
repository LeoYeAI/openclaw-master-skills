---
name: deep-research
description: '深度调研的多Agent编排工作流：把一个调研目标拆成可并行子目标，用 Claude Code 非交互模式（`claude -p`）运行子进程；联网与采集优先使用已安装的 skills，其次使用 MCP 工具；用脚本聚合子结果并分章精修，最终交付"成品报告文件路径 + 关键结论/建议摘要"。用于：系统性网页/资料调研、竞品/行业分析、批量链接/数据集分片检索、长文写作与证据整合，或用户提及"深度调研/Deep Research/Wide Research/多 Agent 并行调研/多进程调研"等场景。'
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, TodoWrite, mcp__firecrawl__firecrawl_scrape, mcp__firecrawl__firecrawl_search, mcp__firecrawl__firecrawl_map, mcp__firecrawl__firecrawl_crawl, mcp__firecrawl__firecrawl_extract, mcp__firecrawl__firecrawl_agent, mcp__plugin_claude-code-settings_exa__web_search_exa, mcp__plugin_claude-code-settings_exa__get_code_context_exa
---

# Deep Research（深度调研编排工作流）

把"深度调研"当作一个可复用、可并行的生产流程来执行：主控负责澄清目标、拆解子目标、调度子进程、聚合与精修；子进程负责采集/抽取/局部分析并输出结构化 Markdown 素材；最终交付物必须是独立成品文件而不是聊天贴文。

**关键约束（必须遵守）**

- **保持默认模型与配置不变**：不要显式覆盖模型或用额外参数覆写默认模型/推理设置；只有在用户明确授权时才调整相关配置。
- **默认最小权限**：子进程通过 `--allowedTools` 控制可用工具；仅在必要时启用网络等权限。
- **联网优先走 skills，其次 MCP**：优先使用已安装 skills；若必须使用 MCP，则优先 `firecrawl`，其次 `exa`；确实无法满足时再考虑 WebFetch/WebSearch。
- **非交互式友好**：子进程不使用 plan 工具，不与用户"等确认/等反馈"式互动；以文件落地、日志可追溯为主。
- **文件交付优先**：最终交付物必须落地为独立文件，禁止在聊天中贴出完整成稿。
- **每一步输出决策与进度日志**：尤其在拆分、调度、聚合、精修、交付前。
- **任务规模判断门槛**：子目标数量 ≥3 时必须启动 `claude -p` 子进程；<3 个子目标时可由主进程直接执行，但仍需记录完整目录结构和原始数据。
- **必须等待用户确认**：摸底完成后，必须明确询问用户"是否开始执行？"，在用户回复"执行/开始/go/yes"等肯定词前不得进入下一步。

## 任务目标

1. 从用户的高层目标推导出可并行的子目标集合（如链接清单、数据分片、模块列表、时间切片等）。
2. 为每个子目标启动独立的 `claude -p` 子进程，并为其分配合适权限（通过 `--allowedTools` 参数）。
3. 并行执行并产出子报告（自然语言 Markdown，可含小节/表格/列表）；失败时输出带原因的错误说明与后续建议。
4. 用脚本按顺序聚合子输出，生成统一的基础稿。
5. 对基础稿做理智检查与**最小化修复**，然后给出最终 artefact 路径与关键发现摘要。

## 交付标准

- 交付物必须是**结构化、洞察驱动**的整体成品；禁止把子任务 Markdown 直接拼接当作最终稿。
- 需要保留子任务原文时，将其另存为内部文件（例如 `.research/<name>/aggregated_raw.md`），在成品中仅吸收关键洞察/证据。
- 润色与修订要**按章节逐段迭代**，不得整篇删除后一次性重写；每次修改后核对引用、数据与上下文，保证可追溯。
- 默认交付详实、深入的分析型报告。
- 交付前做"双重体检质检"：
  1) 检查是否真的是"分章节、多轮整合"产出；若只是一次性生成，退回按章节重写。
  2) 评估是否足够细致；若偏单薄，先判断是"子任务素材不足"还是"统稿时压缩过度"：前者驱动补充/追加调研，后者在既有素材上继续扩展润色，直至达到详细标准。

## 任务规模分级与执行路径

根据子目标数量选择执行路径：

| 规模 | 子目标数 | 执行方式 | 目录要求 |
|------|----------|----------|----------|
| **微型** | 1-2 | 主进程直接执行 | 仍需 `raw/`、`logs/`、`final_report.md` |
| **小型** | 3-5 | 启动子进程，串行或少量并行 | 完整目录结构 |
| **中型** | 6-15 | 并行子进程（默认 8 并发） | 完整目录结构 + 调度脚本 |
| **大型** | >15 | GNU Parallel + 分批调度 | 完整目录结构 + 多阶段调度 |

**注意**：即使是微型任务，也必须：
1. 将原始搜索结果保存到 `raw/` 目录
2. 记录执行日志到 `logs/dispatcher.log`
3. 等待用户确认后再执行（除非用户明确说"直接执行"）

## 端到端流程（严格按序执行）

0. **预执行规划与摸底（必做；主控亲自完成）**
   - 先澄清目标、风险、资源/权限约束，并识别后续扩散依赖的核心维度（主题簇、人物/组织、地域、时间切片等）。
   - 若存在公开目录/索引（标签页、API 列表等），用最小化方式抓取缓存并统计条目；若不存在，做"案头调研"获取真实样本（新闻、资料、数据集等），记录来源/时间/要点作为证据。
   - 形成清单前至少展示一次真实检索或浏览的代表样本；只靠经验推测不算完成摸底。
   - 摸底阶段必须至少通过一次"可追溯的工具链"拿到真实样本并记录引用：优先使用已安装 skills；若需要 MCP，则优先 `firecrawl`，其次 `exa`；若都不可用，记录原因并选择替代方案（必要时再降级到 WebFetch/WebSearch）。
   - 输出初步（或草拟）清单：列出发现的维度、各维度已掌握的选项及样本、规模估算，并标注不确定性/缺口。若尚未获得真实样本，先补齐调研，禁止进入下一步。
   - 依据上述结构补全可执行计划（拆分、脚本/工具、输出格式、权限、超时策略等），用用户语言汇报维度统计与计划内容；在得到明确"执行/开始"回应前保持等待。

1. **初始化与总体规划**
   - 明确目标、预期输出格式与评价标准。
   - 根据当前任务生成一个语义化且不重复的名字 `name`（建议：`<YYYYMMDD>-<短题>-<随机后缀>`，全小写、短横线分隔、无空格）。
   - 创建运行目录 `.research/<name>/`，并把**所有**产物都保存到该目录下（子目录如 `prompts/`、`logs/`、`child_outputs/`、`raw/`、`cache/`、`tmp/`）。
   - 保持默认模型与配置不变；需要调整任何模型/推理/权限相关设置时先征得用户同意，并在日志中注明变更原因与影响范围。

2. **子目标识别**
   - 通过脚本/命令提取或构造子目标列表。
   - 源数据不足时（例如页面只给两个主链接），如实记录原因，然后由主进程直接接手完成剩余工作。

3. **生成调度脚本**
   - 创建调度脚本（例如 `.research/<name>/run_children.sh`），要求：
     - 接收子目标列表（可存 JSON/CSV）并逐项调度。
     - 为每个子目标构造 `claude -p` 调用，推荐要点：
       - 推荐形式：`claude -p "prompt" --allowedTools "Read,Write,Edit,Bash,WebFetch,WebSearch,mcp__firecrawl__*"`（以 `claude --help` 为准）。
       - 在 prompt 中声明：一切联网需求优先使用已安装 skills（技能优先）；若必须走 MCP，则优先 `firecrawl`，其次 `exa`；确实没办法才用 WebFetch/WebSearch；不使用 plan 工具与"人工交互等待"。
       - 非经用户要求不传模型参数。
       - 为子输出指定落盘路径（例如 `.research/<name>/child_outputs/<id>.md`）。
       - 可引用如下调用模板（仅演示参数，不涉及并行）：
         ```bash
         timeout 600 claude -p "$(cat "$prompt_file")" \
            --allowedTools "Read,Write,Edit,Bash,Glob,Grep,WebFetch,WebSearch,mcp__firecrawl__firecrawl_scrape,mcp__firecrawl__firecrawl_search" \
            --output-format json \
            > "$output_file" 2>&1
         ```
       - 若需要让子进程执行更多工具，在 `--allowedTools` 中追加对应工具名。
       - 依据任务规模设置超时：小任务先给 5 分钟（`timeout 300`），较大任务可放宽到最多 15 分钟（`timeout 900`），通过外部 `timeout` 命令兜底。首次命中 5 分钟超时时，结合任务实际判断是否拆分/改参数再重试；15 分钟仍未完成则视为 prompt 或流程需要排查。
       - 小规模任务（<8 个）用循环 + 后台任务（或队列控制）实现并行，避免命令行长度限制导致失败；大规模任务用 `xargs`/GNU Parallel，但必须先用小规模验证参数展开。默认并行 8 个，可按硬件或配额调整。
       - 不要用"串行一个个跑"来替代并行；也不要用"主进程随便搜搜"等方式绕过既定流程。
       - 捕获每个子进程退出码并写日志到运行目录；用 `stdbuf -oL -eL claude -p … 2>&1 | tee .research/<name>/logs/<id>.log` 等方式保证实时刷新，便于 `tail -f` 观察进度。
   - 数据量足够时，主控尽量不亲自承担下载/解析等重活；把这些工作交给子进程完成，主控专注于 prompt、模板与环境准备。

4. **设计子进程 Prompt**
   - 动态生成 prompt 模板，至少包含：
     - 子目标描述、输入数据、约束边界。
     - 规划阶段限制联网检索/抽取的总轮数不超过 X（按复杂度选择；通常建议 10），信息足够就收敛结束；工具优先级：skills → MCP（`firecrawl` → `exa`）→ WebFetch/WebSearch。
     - 结果输出为自然语言 Markdown：包含结论、关键证据列表、引用链接；出现错误时给出 Markdown 形式的错误说明与后续建议。
     - 生成实际 prompt 文件时，优先用 `printf`/逐行写入注入变量，避免 Bash 3.2 在多字节字符场景下 `cat <<EOF` 截断变量的已知问题。
   - 将模板写入文件（例如 `.research/<name>/child_prompt_template.md`）以便审计与复用。
   - 在启动调度脚本前，逐一快速审阅生成的 prompt 文件（例如 `cat .research/<name>/prompts/<id>.md`），确认变量替换正确、指令完整后再派发任务。

5. **并行执行与监控**
   - 运行调度脚本。
   - 记录每个子进程的开始/结束时间、耗时与状态。
   - 对失败/超时子进程做明确决策：标记、重试、或在最终报告中说明；触及 15 分钟超时上限时记录 prompt/流程待排查。长任务执行中可提示用户用 `tail -f .research/<name>/logs/<id>.log` 追踪实时输出。

6. **程序化聚合（生成基础稿）**
   - 用脚本（例如 `.research/<name>/aggregate.py`）读取 `.research/<name>/child_outputs/` 下所有 Markdown，按预设顺序聚合为初版主文档（例如 `.research/<name>/final_report.md`）。

7. **解读聚合结果并设计结构**
   - 通读 `.research/<name>/final_report.md` 与关键子输出。
   - 设计精修报告章节大纲与"素材映射"（例如 `.research/<name>/polish_outline.md`），明确目标受众、章节顺序与每章核心论点。

8. **分章精修与出稿**
   - 新建精修稿（例如 `.research/<name>/polished_report.md`），按大纲逐章撰写；每写完一章立刻自查事实、引用与语言要求，必要时回溯子稿核实。
   - 避免一次性全篇重写；坚持"按章迭代"以维持一致性并降低遗漏风险，同时记录每章亮点、问题与处理方式。
   - 对重复信息、引用格式、待确认条目做统一整理，同时保留核心事实与量化数据。

9. **落地交付**
   - 确认精修稿满足交付标准（结构完整、语气统一、引用准确），以该成品作为对外报告。
   - 最终交付物必须落地为独立文件（位于 `.research/<name>/`）；通过提供文件路径与必要摘要向用户回报，禁止在聊天中贴出完整成稿。
   - 在最终答复中概述核心结论与可执行建议；必要时补充待确认事项的跟进方式。
   - 不对外附带中间稿或内部笔记，确保用户看到的是高质量成品。

## 注意事项

- 保持流程幂等：每次运行都生成新的 `.research/<name>/`，避免覆盖旧文件。
- 所有结构化输出必须是合法 UTF-8 文本。
- 仅在得到授权或确有必要时提升权限；避免滥用权限。
- 清理临时资源时保持谨慎，确保日志与输出可追溯。
- 对失败流程给出可降级的说明：抓取类任务至少尝试两次；仍失败则在 Markdown 中新增"失败原因/后续建议"小节，避免聚合阶段出现空白。
- **缓存优先**：通过 skills/MCP 获取的原始资料，先写入 `.research/<name>/raw/` 等缓存目录，后续处理优先读取本地缓存以减少重复请求。
- **先完整理解再总结**：总结/提炼前先处理完整原文，不得机械截取固定长度（例如前 500 字符）。可写脚本做全文解析、提取关键句或生成要点，但不得依赖"硬截断"。
- **临时目录隔离**：中间产物（脚本日志、解析结果、缓存、调试输出等）放在 `.research/<name>/tmp/`、`.research/<name>/raw/`、`.research/<name>/cache/` 等子目录，必要时在流程结束后按需清理。
- **搜索服务优先级**：联网操作优先使用已安装 skills；若需要 MCP，先查看可用 MCP 工具，并优先选择 `firecrawl`，其次 `exa`；缺少 MCP 时再退回 WebFetch/WebSearch。
- **MCP 参数与输出控制**：对返回可能过大的工具，避免请求"原始全文"类字段导致响应膨胀；必要时分段抽取、先列目录后按需深入。
- **图像检索**：若 MCP 支持图像搜索/描述，除非用户明确要求"仅纯文本"，否则开启并将图像线索与文本证据一起呈现。

## Claude Code 非交互模式参考

### 基本用法

```bash
# 基本非交互调用
claude -p "Your prompt here"

# 指定允许的工具（无需人工确认）
claude -p "Your prompt" --allowedTools "Read,Write,Edit,Bash"

# JSON 格式输出（便于脚本解析）
claude -p "Your prompt" --output-format json

# 流式 JSON 输出
claude -p "Your prompt" --output-format stream-json

# 继续上一次对话
claude -p "Follow up question" --continue

# 继续指定会话
claude -p "Follow up" --resume <session_id>
```

### 子进程调度模板

```bash
#!/bin/bash
# 子进程调度示例

prompt_file="$1"
output_file="$2"
log_file="$3"

# 读取 prompt 并执行
timeout 600 claude -p "$(cat "$prompt_file")" \
    --allowedTools "Read,Write,Edit,Bash,Glob,Grep,WebFetch,WebSearch,mcp__firecrawl__firecrawl_scrape,mcp__firecrawl__firecrawl_search,mcp__firecrawl__firecrawl_map" \
    --output-format json \
    2>&1 | tee "$log_file" > "$output_file"

exit_code=${PIPESTATUS[0]}
echo "Exit code: $exit_code" >> "$log_file"
```

### 并行执行示例

```bash
#!/bin/bash
# 并行执行多个子任务

max_parallel=8
research_dir=".research/$name"

# 使用 GNU Parallel（推荐）
cat "$research_dir/tasks.txt" | parallel -j $max_parallel \
    "timeout 600 claude -p \"\$(cat $research_dir/prompts/{}.md)\" \
    --allowedTools 'Read,Write,Edit,Bash,WebFetch,WebSearch' \
    --output-format json > $research_dir/child_outputs/{}.json 2>&1"

# 或使用后台任务
for task_id in $(cat "$research_dir/task_ids.txt"); do
    (
        timeout 600 claude -p "$(cat "$research_dir/prompts/$task_id.md")" \
            --allowedTools "Read,Write,Edit,Bash,WebFetch,WebSearch" \
            --output-format json \
            > "$research_dir/child_outputs/$task_id.json" 2>&1
    ) &

    # 控制并行数量
    while [ $(jobs -r | wc -l) -ge $max_parallel ]; do
        sleep 1
    done
done

wait  # 等待所有后台任务完成
```

## 通用经验与最佳实践

- **先验证环境假设**：写调度脚本前用 `realpath`/`test -d` 等确认关键路径（如 `venv`、资源目录）存在；必要时用 `dirname "$0"` 推导仓库根路径并通过参数传入，避免硬编码。
- **让提取逻辑可配置**：不要假设网页共享同一 DOM；解析脚本提供可配置选择器/边界条件/可读性解析器，跨站点复用时只需改配置。
- **先小规模跑通再并行**：全面并行前先串行跑 1–2 个子目标验证 agent 配置、skills/MCP 工具链与输出路径；确认链路稳定后再提高并发，避免"起飞后看不清错误"。
- **分层日志便于追溯**：调度器写 `.research/<name>/dispatcher.log`；子任务单独写 `.research/<name>/logs/<id>.log`，失败时直接 `tail` 对应日志定位 MCP/调用细节。
- **失败隔离与重试**：并行失败时先记录失败 ID 与日志，优先对单个失败任务重试；可维护 `failed_ids` 列表并在收尾阶段统一提示后续建议。
- **避免重复抓取**：重试前先检查 `.research/<name>/child_outputs/<id>.md` 是否已合法存在；存在则跳过，减少配额消耗与重复访问。
- **终审与润色**：交付前必须审阅聚合与精修稿是否满足语言要求（例如要求中文则全程中文），并核对引用与数据点与源文件一致；润色时不丢失关键事实与量化信息，让成品具备洞察而非堆事实。
- **引用就地呈现**：每条要点后直接用 Markdown 链接给来源（例如 `[来源](https://example.com)`），避免把链接集中到段尾，便于即时查证。
- **覆盖率校验脚本**：批量生成后用轻量脚本统计缺失条目、空字段或标签数量，确保问题在报告前被发现并补救。
- **对子进程做边界约束**：在子 prompt 中明确可访问范围（仅指定 URL/目录）与可用工具，降低越界与重复抓取风险，让流程在任意站点都安全可控。

## 思考与写作指南

先思考再动手：追求有深度、有独立思考、超出预期的洞见（但不要在回答里提到"惊喜"）；揣摩用户为什么会问这个问题、背后的假设是什么、有没有更本质的问法；同时明确你的答案应满足的成功标准，再围绕标准组织内容。

保持协作：你的目标不是机械执行指令、也不是在信息不足时强行给出确定答案；而是与用户共同推进，逐步逼近更好的问题与更可靠的结论。

写作风格要求：

- 不滥用 bullet points，把它们尽量限制在 top level；能用自然语言段落就用段落。
- 除非直接引用，否则不使用引号。
- 写作时保持亲切、深入浅出、理性克制的语气。

执行本技能时，在每一步输出清晰的决策与进度日志。

## 交付前自检清单

在提交最终报告前，必须核对以下清单：

### 目录结构检查
- [ ] `.research/<name>/` 目录已创建
- [ ] `logs/dispatcher.log` 包含完整执行记录（非事后补写）
- [ ] `raw/` 目录包含原始搜索/抓取结果
- [ ] 子目标 ≥3 时：`prompts/`、`child_outputs/` 目录存在且有内容

### 流程合规检查
- [ ] 摸底阶段展示了真实样本（非凭经验推测）
- [ ] 用户明确确认后才开始执行（除非用户说"直接执行"）
- [ ] 子目标 ≥3 时启动了 `claude -p` 子进程
- [ ] 日志实时记录，而非事后补写

### 报告质量检查
- [ ] 报告是"分章节、多轮整合"产出，非一次性生成
- [ ] 每条关键结论有可追溯的引用来源
- [ ] 引用链接实际访问过（非搜索结果推测）
- [ ] 报告已落地为独立文件，未在聊天中贴出完整成稿

### 快速失败检查
如有以下情况，应在报告中明确说明：
- [ ] 部分子任务失败/超时：记录失败 ID 和原因
- [ ] 数据源受限/不可访问：记录尝试过的替代方案
- [ ] 信息不完整：标注待确认事项和跟进建议
