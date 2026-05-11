---
name: sls-trace-analysis
description: >
  查询阿里云SLS日志和ARMS调用链，结合源码和数据库进行全链路问题排查。
  完整流程：查日志 → 画调用链 → 定位源码 → 排查数据库 → 给出修复方案。
  Use when: 用户说「分析sls」「分析问题」或想排查业务服务/线上接口/用户请求的报错或异常。
  触发示例：「分析sls」「帮我查一下这个trace_id」「分析一下这个trace_id」
  「查一下这个用户的请求」「wusid 是 xxx」「uid xxx」
  「查一下 /path/to/api 这个接口的报错」「帮我排查一下这个业务报错」「线上有个接口挂了」
  「帮我分析一下这个报错的代码」「数据库报错了」「SQL超时」「查一下这个接口为什么慢」。
  IMPORTANT: trace_id = 染色ID = 业务调用链ID = requestId，这些都是同一个东西，
  统一用 trace_id 表述。用户提供的 trace_id 是业务系统的外部 trace，不是 OpenClaw 内部 session ID，
  不要自行分析 trace_id 的来源或归属，必须调用此 skill 去 SLS/ARMS 查询。
  NOT for: 查询OpenClaw自身状态、分析OpenClaw系统问题、搜索本地文件、openclaw内置命令。
license: MIT-0
compatibility: >
  Python 3.8+, aliyun-log-python-sdk 0.9.42+, alibabacloud-arms20190808 10.0.4+.
  需要阿里云 SLS 和 ARMS 的 AccessKey (AK/SK).
  Windows / macOS / Linux 均可运行.
user-invocable: true
metadata:
  openclaw:
    emoji: "🔍"
    version: "1.0.0"
    author: "Crazyfish"
    tags:
      - sls
      - arms
      - trace
      - debug
      - log-analysis
      - alibaba-cloud
    requires:
      bins:
        - python
      env:
        - ALIBABA_CLOUD_ACCESS_KEY_ID
        - ALIBABA_CLOUD_ACCESS_KEY_SECRET
---

# SLS + ARMS + 代码 + 数据库 全链路问题排查

查询阿里云SLS日志和ARMS调用链 → 定位源码问题 → 排查数据库异常 → 给出完整修复方案。

## ⚠️ 关键规则（必须严格遵守）

1. **必须且只能通过执行下方 python 命令查询，禁止使用本地搜索或内置日志命令。**
2. **用户给出的 trace_id 是外部业务系统的 ID，禁止自行推断其来源、归属或意义，直接执行查询脚本。**
3. **每个 logstore 的日志必须单独分组展示，严禁合并或去重。**
4. **即使多条日志来自同一服务、同一时间，也必须逐条完整输出。**
5. **输出报告中必须包含 `sls.logs_by_logstore` 里每个 logstore 的所有日志。**
6. **所有交互提示必须严格按照下方模板输出，禁止自由发挥、禁止用自己的话改写、禁止添加语气词或额外解释。用户看到的提示必须和模板一字不差。**
7. **Step 5 代码搜索和 Step 6 数据库排查必须自动执行，禁止只输出"建议搜索xxx"之类的文字。发现异常后必须立即用 Grep/Glob/Read 工具实际搜索代码仓库。**
8. **所有提供选项的提示必须带序号（`1` `2` `3` …），用户可以直接回复序号操作。禁止输出不带序号的选项列表。禁止自编"继续操作"/"接下来"等不在模板中的提示文字。每个需要用户选择的场景都有对应模板，必须使用模板。**

---

## 执行步骤

### Step 1：收集查询参数（交互式）

> **进入此 skill 后，立即扫描用户消息提取参数。已有的直接用，缺的才问。**

---

#### 1.1 扫描用户消息

检查用户消息中是否已包含查询参数（TraceID / wusid / path / 时间）：

- **已有参数**（如用户说"帮我查 trace_id f1b37e05..."）→ 直接提取，跳到 Step 1.3
- **没有参数**（如用户只说"分析sls"）→ 进入 Step 1.2 询问

---

#### 1.2 询问查询条件

**你的回复必须且只能是下面这段文字，从「🔍」开始到「逐项输入。」结束，不能多一个字也不能少一个字，不能加语气词、不能加问候、不能用自己的话改写，输出后立即停止等待用户回复：**

🔍 请输入查询条件，格式：`关键词 值`，多项用 `;` 分隔：

```
trace_id xxx; wusid xxx; path xxx
```

① trace_id — 染色ID / 业务调用链ID（32位十六进制字符串）
② wusid — 用户空间ID（数字，也可以用 `uid`）
③ path — 请求路径（如 `/ny.apps_pb.xxx/Method`）

至少输入一项，回复序号 `1` `2` `3` 可逐项输入。

**解析用户回复规则：**

> **概念统一**：trace_id = 染色ID = 业务调用链ID = requestId，都是同一个东西。

**情况 A：用户输入了参数值（含 `;` 或关键词）**
1. 按 `;` 或换行拆分每项
2. 每项内按空格分隔：前面是参数名，后面是值
   - `trace_id` / `tid` / `trace` / `染色id` / `requestid` → trace_id
   - `wusid` / `uid` / `用户id` → wusid
   - `path` / `接口` / `api` → path
3. 不带参数名时自动识别：32位十六进制→trace_id，纯数字→wusid，`/`开头→path
4. 提取到任意参数 → 进入 Step 1.3

**情况 B：用户回复了序号**
- `1` → 回复「请输入 trace_id：」→ 等用户输入值 → 记录 → 进入 Step 1.3
- `2` → 回复「请输入 wusid：」→ 等用户输入值 → 记录 → 进入 Step 1.3
- `3` → 回复「请输入 path：」→ 等用户输入值 → 记录 → 进入 Step 1.3

**情况 C：无法识别**
- 回复「未识别到参数，请按格式输入（如 `trace_id xxx`）或回复序号 `1` `2` `3`」
- 用户说"没有"/"不知道" → 依次追问 wusid → path → 都没有则停止

---

#### 1.3 确认时间范围

检查用户是否已提供时间信息：

- **已提及时间**（如"今天下午"、"昨天"、"最近2小时"）→ 自动转换，直接跳到 Step 1.4
- **未提及时间** → 你的回复必须且只能是下面这段文字，不能改写：

⏰ 时间范围？默认 **最近 1 周**，也可以指定：
```
默认           →  最近 1 周（直接回车）
1小时 / 3天 / 2周 / 1个月  →  相对时间
今天 / 昨天    →  当天范围
2024-03-15 14:00 ~ 16:00   →  精确时间段
```

- 用户回车 / 说"默认"/"可以"/"行" → 使用默认 1 周
- 用户给出时间 → 传给 `--duration` 或 `--start/--end`
- 用户说"今天"/"昨天"等 → 自行计算 `--start/--end`

**时间转换参考：**

| 用户说的 | 转换 |
|---------|------|
| 今天 | `--start "今天00:00:00" --end "当前时间"` |
| 昨天 | `--start "昨天00:00:00" --end "昨天23:59:59"` |
| 今天下午 | `--start "今天12:00:00" --end "当前时间"` |
| 最近N小时/天/周/月 | `--duration "N小时/天/周/月"` |
| 上周 | `--start "上周一00:00:00" --end "上周日23:59:59"` |
| 3月15号 | `--start "3月15日00:00:00" --end "3月15日23:59:59"` |

---

#### 1.4 输出查询摘要并执行

> 📋 **查询参数：**
> ```
> 条件：trace_id = xxx  /  wusid = xxx  /  path = xxx
> 时间：最近 1 周（2026-03-12 ~ 2026-03-19）
> 来源：SLS + ARMS
> ```
> 🚀 正在查询，请稍候…

高级选项（**不主动询问**，仅用户提到时才加）：
- "只查SLS" / "不查ARMS" → `--skip-arms`
- "只查ARMS" / "不查SLS" → `--skip-sls`
- "查 xxx logstore" → `--logstores "xxx"`

### Step 2：执行查询脚本（必须执行）

> **默认查最近 1 周，无需指定时间参数。**
> 支持 `--duration` 自然语言时间：1小时、2天、1周、1星期、1个月、半天、30m、6h、3d、1w 等。
> 也支持 `--minutes N` 直接传分钟数，或 `--start/--end` 精确时间段。

**模式 A：已知 TraceID（直接分析）**

```bash
python "%USERPROFILE%\.openclaw\workspace\skills\sls-trace-analysis\scripts\query_trace.py" --trace-id "TraceID"
```

自定义时间范围（自然语言）：
```bash
python "%USERPROFILE%\.openclaw\workspace\skills\sls-trace-analysis\scripts\query_trace.py" --trace-id "TraceID" --duration "3天"
```

精确时间范围：
```bash
python "%USERPROFILE%\.openclaw\workspace\skills\sls-trace-analysis\scripts\query_trace.py" --trace-id "TraceID" --start "2024-01-15 14:00:00" --end "2024-01-15 15:00:00"
```

只查 ARMS（跳过 SLS）：
```bash
python "%USERPROFILE%\.openclaw\workspace\skills\sls-trace-analysis\scripts\query_trace.py" --trace-id "TraceID" --skip-sls
```

只查 SLS（跳过 ARMS）：
```bash
python "%USERPROFILE%\.openclaw\workspace\skills\sls-trace-analysis\scripts\query_trace.py" --trace-id "TraceID" --skip-arms
```

**模式 B：未知 TraceID，通过 wusid / path 先检索**

按用户 ID 检索：
```bash
python "%USERPROFILE%\.openclaw\workspace\skills\sls-trace-analysis\scripts\query_trace.py" --wusid "76149226" --no-interactive
```

按请求路径检索：
```bash
python "%USERPROFILE%\.openclaw\workspace\skills\sls-trace-analysis\scripts\query_trace.py" --path "/ny.apps_pb.promote_pb.PromotePB/UpdateRelation" --no-interactive
```

两者组合（精确缩小范围）：
```bash
python "%USERPROFILE%\.openclaw\workspace\skills\sls-trace-analysis\scripts\query_trace.py" --wusid "76149226" --path "/ny.apps_pb.promote_pb.PromotePB/UpdateRelation" --no-interactive
```

> **模式 B 说明**：`--no-interactive` 让脚本自动选择第一条 TraceID 进行分析。如果 JSON 输出的 `discovered_traces` 有多条，可展示列表让用户选择，然后用选中的 trace_id 以模式 A 重新查询。

### Step 3：解析脚本输出

脚本返回 JSON，必须读取以下字段：

**查询信息（`query`）：**
```
query.trace_id               → 本次使用的 TraceID（模式 A）
query.wusid                  → 本次使用的 wusid（模式 B）
query.path                   → 本次使用的路径（模式 B）
```

**模式 B 专属（`discovered_traces`）：**
```
discovered_traces[].trace_id      → 找到的 TraceID
discovered_traces[].first_time    → 首条日志时间
discovered_traces[].service       → 服务名
discovered_traces[].path          → 请求路径
discovered_traces[].response_code → 响应码
discovered_traces[].response_msg  → 响应消息
discovered_traces[].has_error     → 是否有 ERROR 日志
discovered_traces[].log_count     → 匹配日志条数
```

**ARMS 调用链（`call_chain`）：**
```
call_chain.tree              → 带缩进的调用链路图（文本），含异常 ID 和完整堆栈
call_chain.error_spans       → 异常 Span 列表（含 exception_id、full_stack 字段）
call_chain.services          → 涉及的服务列表
call_chain.total_duration_ms → 总耗时
```

**方法级堆栈（`stack_details`）：**
```
stack_details.{key}.trace_id       → TraceID
stack_details.{key}.rpc_id         → RpcID
stack_details.{key}.service        → 服务名
stack_details.{key}.operation      → 操作名
stack_details.{key}.exception_id   → 异常 ID
stack_details.{key}.stack_entries  → 方法级堆栈列表（api、duration、exception、line）
stack_details.{key}.formatted      → 格式化后的堆栈文本
```

**SLS 日志（`sls`）：**
```
sls.store_stats              → 每个 logstore 的查询统计（必须全部展示）
sls.logs_by_logstore         → 按 logstore 分组的日志（必须按组展示，不能合并）
sls.error_logs               → ERROR 级别日志
```

**根因分析（`analysis`）：**
```
analysis.root_cause          → 根本原因结论
analysis.findings            → 关键发现列表
analysis.suggestions         → 排查建议列表
```

### Step 3.5：无数据时循环询问时间范围（必须严格遵守）

> **核心规则：查不到数据就问用户，用户给了新时间就重查，如此循环直到查到数据或用户放弃。绝对不能自动重试，绝对不能输出空报告。**

如果 JSON 输出中 `no_data` 为 `true`（SLS 和 ARMS 均无数据）：

**第一次无数据 → 输出以下提示，等待用户回复：**

> ⚠️ 在最近 {当前查询范围，如"1周"} 内（{time_range}）未查到任何数据。
>
> 回复序号或直接输入时间范围：
>
> `1` 换时间重查 — 输入自然语言（如 `1个月`、`2周`、`3天`）
> `2` 精确时间段 — 输入起止时间（如 `2024-03-10 00:00 ~ 2024-03-15 23:59`）
> `3` 换条件重查 — 输入新的 trace_id / wusid / path
> `4` 不用了 — 停止查询

**收到用户回复后：**

- `1` 或直接输入时间（如"1个月"、"2周"、"3天"）→ 用 `--duration` 重新执行 Step 2，然后回到 Step 3
- `2` 或输入精确时间段（如"3月10号到3月15号"）→ 计算为 `--start/--end` 重新执行
- `3` → 回到 Step 1.2 重新收集参数
- `4` 或"不用了"、"算了"、"停" → 停止，输出简短结论：「在所有尝试的时间范围内均未查到该 TraceID 的数据，可能原因：1) TraceID 不正确 2) 日志已过期被清理 3) 该请求未经过当前 SLS 项目」

**再次无数据（第二次、第三次…） → 继续循环询问：**

> ⚠️ 在 {本次时间范围} 内仍未查到数据。
>
> `1` 换时间继续 — 输入新的时间范围
> `2` 换条件重查 — 输入新的 trace_id / wusid / path
> `3` 不用了 — 停止查询

**循环规则：**
1. 每次查不到数据 → 必须停下来问用户 → 等用户回复 → 按用户指示执行
2. **绝不跳过询问直接输出报告**
3. **绝不自行决定用什么时间重试**
4. 用户在此上下文中说的任何时间表述，一律视为新的查询时间范围
5. 只有 `no_data` 为 `false`（查到数据了）才进入 Step 4 输出完整报告

### Step 4：输出分析报告（格式严格按下方执行）

---

**📋 问题定位报告**

| 项目 | 内容 |
|------|------|
| TraceID | `{query.trace_id 或 discovered_traces 中用户选择的 trace_id}` |
| WSUID | `{query.wusid，无则省略此行}` |
| 请求路径 | `{query.path，无则省略此行}` |
| 时间范围 | `{time_range}` |
| 涉及服务 | `{call_chain.services}` |
| 总耗时 | `{call_chain.total_duration_ms}ms` |

---

**🗺️ ARMS 调用链路图**（此段必须输出，不可跳过）

> 判断条件：`call_chain.total_spans > 0` 表示有数据，`== 0` 表示无数据。
> `call_chain.tree` 始终有值（无数据时也有提示文本），**必须原样输出**。

```
{call_chain.tree 的完整内容，一字不改直接输出}
```

> 示例（有数据时）：
> ```
> ● [rpc-ny] gRPC → /PromotePB/UpdateRelation 156ms ❌
>   └─ [promote-service] MySQL → SELECT 12ms ✅
>       ⚡ 错误: record not found
>       🔗 异常ID: 811073848360427400
> ```
>
> 示例（无数据时，脚本输出的 tree 已包含提示）：
> ```
> ⚠️ ARMS 未采样到此 TraceID 的调用链
> ```

---

**❌ 异常 Span**（此段必须输出，不可跳过）

> 判断条件：`call_chain.error_spans` 列表是否非空。

**有异常 Span（`call_chain.error_count > 0`）时，逐个输出：**

| 服务 | 操作 | 异常 ID | 耗时 | 错误信息 |
|------|------|---------|------|---------|
| `{service}` | `{operation}` | `{exception_id}` | `{duration_ms}ms` | `{tags.error.message 或 tags.exception.message}` |

每个异常 Span 下方，如果有 `full_stack`，必须输出完整堆栈：

```
🔗 异常ID: {exception_id}
⚡ 堆栈:
{full_stack 完整内容，不截断，逐行输出}
```

**无异常 Span（`call_chain.error_count == 0`）时，输出：**

> 无异常 Span（ARMS 未采样或调用链无错误）

---

**🔬 方法级堆栈详情（GetStack）**

> 判断条件：`stack_details` 不为 null 且非空对象。

**有 `stack_details` 数据时，逐个输出：**

```
── [{service}] {operation} → 异常ID: {exception_id} ──
{formatted 的完整内容，一字不改直接输出}
```

> 示例：
> ```
> ── [rpc-ny] UpdateRelation → 异常ID: 811073848360427400 ──
>   [ 1] com.ny.service.PromoteService.updateRelation (服务: rpc-ny) 156ms L212
>        ⚡ 异常: record not found
>   [ 2] com.ny.dao.PromoterDAO.getByWusId (服务: rpc-ny) 12ms L89
> ```

**无 `stack_details` 数据时，输出：**

> 无方法级堆栈（ARMS 未采样或无异常 Span）

---

**📄 SLS 日志 — 按 LogStore 分组**

> ⚠️ 以下每个 LogStore 单独展示，不合并，不去重

**查询统计：**

| LogStore | 状态 | 日志条数 |
|----------|------|---------|
| `{logstore1}` | `{status}` | `{count}` |
| `{logstore2}` | `{status}` | `{count}` |

---

**【LogStore: {logstore名称1}】**（共 {count} 条）

逐条输出该 logstore 的每条日志：

```
[1] 时间：{time}
    级别：{level}
    服务：{service}
    文件：{file}
    消息：{message}
    附加：{raw 中的 attach / request / response 等关键字段}
```

---

**【LogStore: {logstore名称2}】**（共 {count} 条）

逐条输出该 logstore 的每条日志（同上格式）：

```
[1] 时间：{time}
    级别：{level}
    服务：{service}
    文件：{file}
    消息：{message}
    附加：{raw 中的关键字段}
```

---

**🔍 根因分析**

- **直接原因**：{结合 ARMS error_spans 和 SLS error_logs 的错误信息}
- **触发位置**：{service} → {operation}（来自哪个 logstore 第几条）
- **关联日志**：{指明是哪个 logstore 的第几条}
- **根本原因**：{综合分析}

**🛠️ 建议修复方向**

{修复建议}

---

### Step 4.5：报告输出后的后续操作提示（必须严格按模板）

> **⚠️ 核心规则：输出完 Step 4 报告后，必须且只能输出下面的统一模板，禁止自由发挥任何后续操作文字。**
> **禁止行为：**
> - 输出不带序号的选项，如"继续操作：新 trace_id / 用 wusid 查 / 不用了"
> - 省略"查看代码"选项
> - 自编任何不在模板中的提示文字

**无论查询结果如何（成功/部分失败/有异常/无异常），Step 4 报告末尾统一输出以下模板：**

> 回复序号选择下一步：
>
> `1` 排查代码 — 搜索 `{operation}` 方法源码，定位问题
> `2` 换条件重查 — 输入新的 trace_id / wusid / path
> `3` 换时间重查 — 输入新的时间范围（如 `1个月`、`3天`）
> `4` 用 wusid 查用户请求 — 输入 wusid 查该用户的所有请求
> `5` 不用了 — 结束排查

其中 `{operation}` 替换为 ARMS error_spans 中的操作名（如 `UpdateRelation`），无 ARMS 数据时替换为请求路径中的方法名。

**用户回复处理：**
- `1` → 直接进入 Step 5 代码排查
- `2` → 回到 Step 1.2 重新收集参数
- `3` → 用新时间范围重新执行 Step 2
- `4` → 用户提供 wusid 后，以模式 B 重新执行 Step 2
- `5` → 输出简短结论，结束

---

### Step 5：代码级排查（必须自动执行，不能只建议）

> **⚠️ 核心规则：输出完 Step 4 报告后，如果存在 ERROR 日志或异常 Span，必须立即自动执行代码搜索，不能只输出"建议搜索 xxx 方法"之类的文字。**
> 如果日志和调用链均无异常，跳过此步。
>
> **禁止行为**：输出类似"建议：在代码仓库搜索 UpdateRelation 方法"的文字而不实际执行搜索。必须直接使用 Grep/Glob/Read 工具去搜索代码。

#### 5.1 提取代码线索

从 Step 3/4 的结果中提取以下信息，作为代码搜索的关键词：

| 来源 | 提取内容 | 用途 |
|------|---------|------|
| SLS 日志 `file` 字段 | 文件名和行号（如 `handler.go:156`） | 直接定位源码位置 |
| SLS 日志 `message` 字段 | 错误消息关键词（如 `record not found`、`nil pointer`） | 搜索错误产生位置 |
| ARMS `error_spans` | 服务名 + 操作名（如 `promote-service` → `UpdateRelation`） | 定位入口函数 |
| ARMS `tags` | `exception.type`、`error.message`、`db.statement` | 定位异常类型和 SQL |
| ARMS `stack_details` | 方法级堆栈中的类名、方法名、行号 | 精确定位异常代码位置 |
| SLS 日志 `raw` | `data.request`、`data.response` 中的业务字段 | 理解请求上下文 |

#### 5.2 搜索源码

**按优先级依次搜索（找到即停）：**

1. **有明确文件名+行号**（如 `caller: service/handler.go:156`）
   - 直接用 Grep 搜索该文件名，用 Read 读取对应代码段（前后各 30 行）

2. **有函数/方法名**（如 ARMS 的 `operation: UpdateRelation`）
   - 用 Grep 搜索函数定义：`func.*UpdateRelation` 或 `def UpdateRelation`
   - 读取函数完整实现

3. **有错误消息**（如 `record not found`、`duplicate key`）
   - 用 Grep 在项目中搜索该错误消息字符串
   - 找到错误产生的代码位置

4. **有请求路径**（如 `/ny.apps_pb.promote_pb.PromotePB/UpdateRelation`）
   - 路径中提取服务名和方法名（`PromotePB` / `UpdateRelation`）
   - 搜索 proto 定义和对应的 handler 实现

5. **有 GetStack 方法级堆栈**（`stack_details` 不为空）
   - 从堆栈条目的 `api` 字段提取类名.方法名（如 `com.xxx.service.UpdateRelation`）
   - 用 Grep 搜索对应的类定义和方法实现
   - 堆栈中有 `exception` 字段的条目优先搜索

> **搜索范围与代码仓库定位规则：**
>
> 1. 先在当前工作目录用 Grep 搜索关键方法/类名
> 2. 如果当前目录搜不到（0 个结果），**输出以下提示（严格按模板）**：
>
> ```
> 💻 需要搜索代码仓库来定位问题源码。
>
> 当前目录未找到相关代码，请提供业务代码仓库路径：
> - 示例：`C:\projects\promote-service` 或 `/home/user/go/src/promote`
> - 如果有多个服务，可提供多个路径，用 `;` 分隔
> ```
>
> 3. 用户提供路径后 → 在该路径下用 Grep 搜索，然后继续 5.3 分析
> 4. **必须实际执行搜索**：使用 Grep 工具搜索代码，不能只输出文字建议

#### 5.3 分析代码问题

找到相关代码后，分析以下内容：

- **错误触发路径**：从入口函数到报错位置的调用链路
- **错误原因**：参数校验缺失？空指针？异常未捕获？逻辑错误？
- **上下文数据**：结合 SLS 日志中的 request/response 数据，还原触发条件

#### 5.4 输出代码分析

```
**💻 代码排查**

**定位文件：** `{file_path}:{line_number}`

**关键代码段：**
​```{language}
// 标注问题所在行
{code snippet with comments}
​```

**问题分析：**
- 错误路径：{入口} → {中间调用} → {报错位置}
- 直接原因：{具体代码问题，如"第 156 行未检查 err 返回值"}
- 触发条件：{结合日志中的 request 数据说明什么情况下会触发}

> ⚠️ 仅指出代码问题，不直接修改代码。由用户自行决定如何修复。
```

---

### Step 6：数据库排查（当错误涉及数据库时）

> **触发条件**：仅当以下任一条件满足时才执行此步骤：
> - ARMS tags 中有 `db.statement`、`db.type` 字段
> - 错误消息包含 SQL/数据库相关关键词（`duplicate key`、`deadlock`、`record not found`、`foreign key`、`table doesn't exist`、`column not found`、`timeout` + `sql`/`db`/`mysql`/`redis`）
> - SLS 日志中出现 SQL 语句或数据库错误
> - 代码排查中发现 ORM 操作或 SQL 拼接
>
> 不满足以上条件则跳过此步骤。

#### 6.1 提取数据库线索

| 来源 | 提取内容 |
|------|---------|
| ARMS `tags.db.statement` | 完整 SQL 语句 |
| ARMS `tags.db.type` | 数据库类型（MySQL/Redis/ES） |
| SLS 日志 | SQL 相关错误消息 |
| Step 5 代码 | ORM 模型定义、SQL 拼接逻辑、表名/字段名 |

#### 6.2 分析数据库问题

根据错误类型进行针对性分析：

| 错误类型 | 排查方向 |
|---------|---------|
| `record not found` | 查询条件是否正确？数据是否存在？是否有软删除过滤？ |
| `duplicate key` | 唯一索引冲突，检查插入逻辑是否有并发问题或重试机制 |
| `deadlock` | 事务中的锁顺序，是否有交叉更新 |
| `timeout` | 慢 SQL，检查是否缺少索引、全表扫描、大事务 |
| `foreign key` | 外键约束失败，检查关联数据是否存在 |
| `connection refused` | 数据库连接池耗尽或实例宕机 |

#### 6.3 搜索相关代码中的数据库操作

- 在 Step 5 定位到的代码文件中，搜索 ORM 操作（如 `db.Where`、`db.Create`、`Model.objects`）
- 查找表结构定义（model/schema）
- 查找 SQL 拼接或 Raw SQL

#### 6.4 输出数据库分析

```
**🗄️ 数据库排查**

**涉及表/操作：** `{table_name}` — `{SELECT/INSERT/UPDATE/DELETE}`

**问题 SQL：**
​```sql
{SQL 语句，标注问题部分}
​```

**分析：**
- 错误类型：{如 duplicate key on index `idx_xxx`}
- 原因：{如并发插入同一唯一键}
- 对应代码：`{file}:{line}` — {代码描述}

**🔎 建议检查的数据库配置项：**
- 表：`{table_name}`
- 字段/索引：`{需要检查的字段或索引名}`
- 检查内容：{如"确认该用户的 xxx 字段值是否为 null"、"检查 idx_xxx 索引是否存在"、"核实 xxx 配置表中 key=yyy 的记录是否正确"}
- 参考 SQL：`SELECT ... FROM {table} WHERE {condition}`
```

> ⚠️ 仅指出应该检查哪些数据库配置项和数据，不直接执行 SQL。由用户或 DBA 自行查询确认。

---

### Step 7：综合结论与修复建议

> 在完成所有排查后（Step 4 报告 + Step 5 代码 + Step 6 数据库），输出最终综合结论。

```
**📝 综合结论**

**问题链路：**
{用户请求} → {入口服务} → {中间调用} → {出错位置}

**根本原因：**
{一句话总结，结合日志 + 代码 + 数据库的分析}

**代码问题：**
1. {文件:行号} — {问题描述}
2. {文件:行号} — {问题描述}

**需要检查的数据库配置：**
1. 表 `{table}` — {检查什么，附参考 SQL}
2. 配置项 `{key}` — {检查什么}

**修复方向（按优先级）：**
1. 【紧急】{问题描述 + 修复思路}
2. 【建议】{预防性改进}
3. 【优化】{长期优化方向}

**影响范围：**
- 受影响接口：{path}
- 受影响用户：{wusid 相关信息}
- 影响程度：{根据 error_logs 数量和 error_spans 判断}
```

> ⚠️ 本报告仅指出问题和排查方向，不直接修改代码或执行数据库操作。

---

### Step 8：询问用户是否需要进一步操作

输出综合结论后，**严格按以下模板输出**：

> 🔧 需要进一步操作吗？回复序号：
>
> `1` 查看更多代码 — 深入分析相关文件或上下游调用
> `2` 查看更多日志 — 换条件 / 换时间范围重新查询
> `3` 分析其他 TraceID — 输入新的查询条件
> `4` 不用了 — 结束排查

---

## 注意事项

- **每个 logstore 的日志必须独立展示**，哪怕内容高度相似也不能合并
- ARMS 未采样到时（call_chain 为 null），只展示 SLS 日志，注明"未采样到调用链"
- TraceID 长度为 30 位时 ARMS 不需要时间范围；其他长度需要 `--start/--end`
- SLS 和 ARMS 可以用不同的 AK/SK
- 模式 B 使用 `--no-interactive`，脚本自动选第一条 TraceID；如需让用户选择，展示 `discovered_traces` 列表后用模式 A 重跑
- `--wusid` 同时匹配 `wechat_user_space_id` 和 `promoter_wechat_user_space_id` 两个字段
- `--path` 匹配 `data.request.path` 字段，支持完整路径或路径片段
