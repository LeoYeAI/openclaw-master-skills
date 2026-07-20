---
name: anyshare-mcp-skills
description: "AnyShare 企业云盘技能。支持：搜索文件、上传/下载文件、分享链接读取、全文写作（生成大纲→确认→写正文）、Bot 智能问答。触发词：AnyShare、asmcp、文档库、文件管理、知识库、anyshare.aishu.cn 分享链接。"
homepage: "https://anyshare.aishu.cn"
metadata: '{"openclaw":{"category":"productivity","emoji":"📁","requires":{"bins":["agent-browser","mcporter"]},"openclawSkillsEntryFile":"openclaw.skill-entry.json"}}'
---

# AnyShare MCP 技能

> **首次使用本技能时，配置步骤的权威来源是 [setup.md](setup.md)。**
> SKILL.md 只做摘要+跳转，**配置细节以 setup.md 为准**（避免两处表述漂移）。

---

## ⚠️ 执行前必读

### 强制前置阅读（按需必读，否则跳过）

| 操作 | 必须先读 | 为何 |
|------|----------|------|
| 首次使用本技能（配置 asmcp.url） | **[setup.md](setup.md)** 全章 | 配置步骤唯一权威来源；包含 mcporter.json 写入、daemon 重启、openclaw.json 合并、企业地址确认话术 |
| 执行任何认证 / auth_login 前 | **[references/auth.md](references/auth.md)** 第 1~5 步 | 认证流程步骤编号、Cookie 提取方式、状态文件路径均以此为准 |
| 调用任何业务工具（file_search / upload / download 等）前 | **[references/tool-params.md](references/tool-params.md)** 对应工具节 | 参数格式（key=value）、固定字段、禁止传参、不传参；与此处示例保持一致 |
| **进入场景四（全文写作）前** | **本 SKILL.md → 场景四 → C8 进门卡点** | **必须持 docid；未持则先走 file_search 或场景五 获取，禁止绕过（C8 违规）** |
| 排障 / 401 / 认证失败 | **[references/troubleshooting.md](references/troubleshooting.md)** | 错误码含义、常见现象与处理方式均在此 |

### 硬卡点表

| # | 规则 | 关联场景 |
|---|------|---------|
| C1 | 搜索文件**只用 `file_search`**，禁止 RAG 类工具或目录树展开 | 场景一 |
| C2 | 展示搜索/列目录结果前，**必须先调 `file_convert_path` 再输出**（禁止跳过） | 场景一、场景五 |
| C3 | 上传/下载前，**必须用户明确回复"是"确认 docid**，禁止代选 | 场景二、场景三 |
| **C4** | **大纲未确认前禁止调用 `__大纲写作__1`**（大纲门闩） | 场景四 |
| **C5** | `source_ranges[].id` **必须传 id**（docid 最后一段），禁止传完整 docid | 场景四 |
| **C6** | **禁止用 screenshot 解析分享链接的 item_id**，以 `agent-browser get url` 为准 | 场景五 |
| **C7** | `item_id` **禁止臆造**，须从实际访问后的 URL 中解析 | 场景五 |
| **C8** | **进入 chat_send（全文写作）前必须持有 docid**。若尚无 docid，须先通过场景一（关键词搜索）或场景五（解析分享链接）获取，禁止自行判断"docid 不可用"而绕过本文档处理流程另起炉灶。 | 场景四 |
| **C9** | **在场原则（System-Internal-Only）**：持有 docid 后，所有后续操作（阅读、摘要、写作、导出）必须通过 AnyShare 工具完成，禁止下载到本地后跳出系统处理。C8 管"进入"，C9 管"离开"。 | 所有含 docid 的场景 |

---

## 🔄 完整执行流程

```
用户输入
  │
  ▼
① 首次使用？── 是 ──→ 阅读 setup.md，执行 Step 1~4
  │                   → 向用户汇报 asmcp.url + 连通性
  │                   → 确认是否为**本企业**正式端点
  否
  ▼
② 认证检查（自动）── 失败 ──→ 认证恢复（references/auth.md 第 1~6 步）──→ 重试验证
  │                                           │
  │ 通过 ◀────────────────────────────────────┘
  ▼
③ 意图识别
  │
  ├─ 分享链接？── 是 ──→ 场景五（读取链接 → 获取 docid）
  │
  ├─ 书写类诉求？（生成/撰写/改写/续写/润色/文章/报告/文案/大纲/材料）── 是 ──→ 确认全文写作？
  │                                                                         │
  │                                                    是 ◀─────────────────┘
  │                                                    ▼
  │                                              ⚠️ C8 强制预检：
  │                                              "是否已持有本次写作所需的 docid？"
  │                                              否 ──→ 场景一（关键词搜索）获取 docid
  │                                              │        或场景五（解析分享链接）获取 docid
  │                                              │        获取后返回此节点重新判断
  │                                              是
  │                                              ▼
  │                                              场景四：全文写作
  │                                              ① docid/id → ② 大纲 → ③ 确认 → ④ 正文
  │
  │                                              否 ──→ chat_send 简化问答
  │
  ├─ 搜索 / 查看文件 ──→ 场景一
  │
  ├─ 上传文件 ──→ 场景二
  │
  └─ 下载文件 ──→ 场景三
```

---

## 📌 核心概念速查

| 术语 | 说明 | 传参规则 |
|------|------|---------|
| **docid** | 完整路径，`gns://` 开头，是文档在 AnyShare 系统内的唯一标识 | 传给 `folder_sub_objects`、`file_upload`、`file_osdownload`、`file_convert_path`（均须完整 `gns://…`） |
| **id** | docid 的最后一段 | 传给 `chat_send` 的 `source_ranges[].id`（**不传**完整 docid，见 C5） |
| **namepath** | 云盘展示用路径，由 `file_convert_path` 返回 | 仅供阅读，不作 docid 传参 |
| **sharedlink** | `https://anyshare.aishu.cn/link/AR...` | 用 `agent-browser get url` 解析 item_id |

> 完整说明：[references/concepts.md](references/concepts.md)

---

## 🏛️ AnyShare 在场原则（System-Internal-Only Principle）

> **这是本技能最根本的运行假设，所有场景均以此为前提。**

### 原则内容

**一旦通过 AnyShare 系统获取到 docid，该文档的所有后续操作都必须通过 AnyShare 工具完成，禁止跳出系统处理。**

换言之：

- ✅ 持有 docid → 用 `chat_send`（全文写作 / 摘要 / 问答）
- ✅ 持有 docid → 用 `file_convert_path`（查看路径）
- ✅ 持有 docid → 用 `file_osdownload`（下载，但下载后仍须回到 AnyShare 工具链处理）
- ❌ 持有 docid，却去下载文件到本地后用外部工具（markitdown、LLM 直接总结等）"替代" AnyShare 工具链 → **在场原则违规**

### 为什么这条原则重要

docid 是文档在 AnyShare 系统内的"在场证明"。AI 一旦持有 docid，意味着文档已经在 AnyShare 的管理范围内。跳出系统去处理，等于放弃了 AnyShare 已有的权限管控、操作审计、内容安全策略，是系统性风险。

### 典型失控模式（供自检）

| 失控模式 | 为什么会发生 | 正确做法 |
|----------|-------------|---------|
| "已有 docid，但还是下载了 PPTX 用 markitdown 提取内容" | AI 认为"外部工具效果更好" | 用 `chat_send` + `source_ranges` 替代 |
| "已有 docid，但决定直接帮用户总结内容" | AI 认为"用 LLM 总结更快" | 用 `chat_send` 简化问答替代 |
| "已有 docid，但去查本地文件" | AI 遗忘了 docid 的存在 | 回到 docid，用 AnyShare 工具继续 |

### 在场原则与 C8 的关系

C8 约束的是"进入 chat_send 前必须持有 docid"，在场原则约束的是"持有 docid 后不得离开 AnyShare 系统"。两者共同构成了完整的边界控制：C8 管入口，在场原则管出口。

---

## 📂 场景一：文件/关键词搜索

> **前置阅读**：tool-params.md → `file_search` 节（参数格式+固定字段说明）

### 步骤

**第 1 步：`file_search`**

```json
{
  "name": "file_search",
  "arguments": {
    "keyword": "<用户关键词>",
    "type": "doc",
    "start": 0,
    "rows": 25,
    "range": [],
    "dimension": ["basename"],
    "model": "phrase"
  }
}
```

> ⚠️ `dimension: ["basename"]` + `model: "phrase"` **必须固定**，不随关键词变化。省略会导致正文/多字段命中，而非按名匹配。

**第 2 步：展示结果（必须含三要素）**

对每条结果：**先调 `file_convert_path`** → 再展示：
- **名称**：`basename`
- **大小**：`size = -1` → 目录；`size ≥ 0` → 实际字节数
- **云盘路径**：`namepath`（来自 `file_convert_path` 返回）

> ⚠️ **C1 + C2**：禁止跳过 `file_convert_path`；禁止用 docid/序号代替 namepath 展示。

**第 3 步：用户确认 docid（如需操作）**

**分页提示（hits ≥ 25 时强制显示）：**
> 找到 X 条（已展示前 25 条），是否：
> 1. **查看更多**（翻页）  2. **更换关键词**  3. **缩小范围**（加 range）

**按文件夹名查看子文件：**
1. 搜索结果中找 `size = -1` 且 basename 一致的项
2. 对该 docid 先调 `file_convert_path` 展示目录 namepath（C2）
3. 再调 `folder_sub_objects` 列出子文件

---

## 📂 场景二：上传文件

### 步骤

**第 1 步：搜索目标目录**（`file_search` + `file_convert_path`，**必须 C3**）

**展示确认模板：**
> 即将上传到：
> - 文件名：`<本地文件名>`
> - 云盘路径：`file_convert_path` 返回的 `namepath`
> - docid：`gns://...`
>
> 确认继续？回复"是"，或提供其他目标路径。

**第 2 步：用户回复"是"后锁定 docid（C3）**

**第 3 步：`file_upload`**

```json
{
  "name": "file_upload",
  "arguments": {
    "docid": "<用户确认的 docid（完整）>",
    "file_path": "<本地真实路径>"
  }
}
```

**第 4 步：汇报**
- docid 必须展示为 **`gns://` 开头完整路径**（禁止只展示 id/十六进制串）
- 对新文件 docid 调 `file_convert_path`，一并展示 `namepath`

---

## 📂 场景三：下载文件

### 步骤

**第 1 步：搜索目标文件**（`file_search` + `file_convert_path`，**必须 C3**）

**展示确认模板：**
> 即将下载：
> - 文件名：`<basename>`
> - 大小：`<size> 字节`
> - 云盘路径：`file_convert_path` 返回的 `namepath`
> - docid：`gns://...`
>
> 确认继续？回复"是"，或选择其他文件。

**第 2 步：用户回复"是"后锁定 docid（C3）**

**第 3 步：`file_osdownload`**

```json
{
  "name": "file_osdownload",
  "arguments": {
    "docid": "<用户确认的 docid（完整）>"
  }
}
```

---

## 📂 场景四：全文写作

> **前置阅读**：tool-params.md → `chat_send` 节（参数格式、`source_ranges` 传参规则）

**入口**：用户已确认走全文写作流程。

### ⚠️ C8 进门卡点（C-gate 0）：进入前必须持有 docid

> **这是本场景的第一道门。任何时候未持有 docid，都必须先出去获取，不得绕过。**

**进门前自问：**
> "我是否已为本次写作任务持有至少一个可用的 docid？"

- **是** → 进入步骤 1
- **否（docid 尚未获取）** → 必须先执行以下之一：
  - **路径 A**：`file_search`（关键词搜索）→ 获取 docid → 返回本场景
  - **路径 B**：场景五（解析分享链接）→ 获取 docid → 返回本场景
  - **路径 C**：若用户直接提供了文件 docid → 直接进入步骤 1
  - **禁止**：自行判断"docid 拿不到"而改用本地写作、摘要总结等绕过手段（违者属 C8 违规）

> **C8 违规示例（摘录本次失控案例，供自检）：**
> - "这些是本地 PPTX 文件，不是知识库文档，source_ranges 用不了，所以我直接自己写"→ **C8 违规**，正确做法是先把文件上传 AnyShare 或找到云端对应 docid 再调用 chat_send
> - "这个文档没法获取 docid，直接帮用户总结好了" → **C8 违规**

### ⚠️ 大纲门闩（C4）

禁止跳过"生成大纲 → 用户确认"直接生成正文。

### 步骤

**第 1 步：确认文档 id（已在 C8 获取）**
- 分享链接 → 场景五解析出 id
- 关键词 → `file_search` 确认文档 id

**第 2 步：生成大纲（`__全文写作__2`）**

```json
{
  "name": "chat_send",
  "arguments": {
    "query": "<用户写作任务描述>",
    "selection": "",
    "times": 1,
    "skill_name": "__全文写作__2",
    "web_search_mode": "off",
    "datasource": [],
    "source_ranges": [{ "id": "<文档的 id>", "type": "doc" }],
    "template_id": 1,
    "interrupted_parent_qa_id": ""
  }
}
```

→ 展示大纲 → **等待用户确认**（C4）

**第 3 步：生成正文（`__大纲写作__1`）**

仅在大纲确认后调用（用第 2 步返回的 `conversation_id`）：

```json
{
  "name": "chat_send",
  "arguments": {
    "query": "基于大纲生成文档",
    "selection": "<已确认的大纲全文>",
    "conversation_id": "<步骤2返回的 conversation_id>",
    "times": 1,
    "skill_name": "__大纲写作__1",
    "web_search_mode": "off",
    "datasource": [],
    "source_ranges": [{ "id": "<文档的 id>", "type": "doc" }],
    "interrupted_parent_qa_id": ""
  }
}
```

**第 4 步：导出**（保存本地 / 上传至 AnyShare 复用场景二）

> ⚠️ **C5**：`source_ranges[].id` 传 id（docid 最后一段），不传完整 docid。

---

## 📂 场景五：分享链接读取

> **前置阅读**：auth.md → 登录填表步骤（账号密码索取+snapshot -i 用法）

**触发**：用户提供 `https://anyshare.aishu.cn/link/AR...`

> ⚠️ **C6 + C7**：item_id 只能从 `agent-browser get url` 解析，禁止 screenshot，禁止臆造。

### 步骤

**第 1 步：无头浏览器跟随重定向**

```bash
agent-browser open "https://anyshare.aishu.cn/link/<分享ID>"
agent-browser wait --load networkidle
agent-browser get url   ← 获取含 item_id 的落地 URL
```

**第 1.5 步：遇登录页 → 填入账号密码**
1. 向用户**当面索取**账号 + 密码（禁止从文件读取）
2. `agent-browser snapshot -i` 获取无障碍树 refs
3. `fill` 账号/密码 → `click` 登录 → `wait --load networkidle`
4. 再次 `get url` 获取登录后落地 URL

**第 2 步：解析 URL 中的 `item_id`**
1. 从 URL 提取 `item_id`（已 URL 编码）
2. 解码 → 完整 docid
3. 取最后一段 → id
4. 根据 `item_type` 分流：
   - `folder` → 第 3 步A
   - `file` / 其他 → 第 3 步B

**第 3 步A：文件夹**
1. `file_convert_path` → 展示目录 `namepath`（C2）
2. `folder_sub_objects` → 列出子文件

**第 3 步B：文件**
- 走场景四（全文写作）：id 传给场景四第 1 步
- 或简化问答：`chat_send` + `source_ranges`

---

## 🎯 意图模糊时的确认模板

当用户意图**不清晰**、无法判断是否在 AnyShare 操作或做哪类操作时，使用以下模板（仅一次，不叠套）：

```
请确认：
1. 目标系统：是否在 AnyShare 操作？
   1) 是
   2) 其他系统

2. 具体操作：
   1) 搜索 / 查看文件
   2) 上传或下载文件
   3) 智能问答 / 全文写作
   4) 其他（文档库浏览、换账号等）

回复示例：「1 2」表示在 AnyShare 上传或下载。
```

**回复 → 执行路径：**

| 回复 | 场景 |
|------|------|
| `1 + 1` | 场景一 |
| `1 + 2`（上传） | 场景二 |
| `1 + 2`（下载） | 场景三 |
| `1 + 3` | 场景四 |
| `1 + 4` | 澄清子意图 |
| `2` | 不走本技能 |

---

## 📖 补充资料（权威来源）

| 文件 | 权威内容 | 用于 |
|------|---------|------|
| **[setup.md](setup.md)** | asmcp.url 写入步骤、daemon 重启、企业地址确认话术 | 首次配置（**唯一权威来源**） |
| [references/auth.md](references/auth.md) | 认证 1~5 步、恢复 1~6 步、Token 刷新、状态文件 | 认证相关操作 |
| [references/concepts.md](references/concepts.md) | docid/id/namepath/sharedlink 完整说明 | 概念确认 |
| [references/tool-params.md](references/tool-params.md) | 各工具参数 schema、固定字段、禁止传参 | 工具调用前 |
| [references/troubleshooting.md](references/troubleshooting.md) | 错误码、常见现象与处理 | 排障 |
| [SECURITY.md](SECURITY.md) | 安全约束、敏感信息处理 | 安全审计 |
