---
name: notion-im-helper
description: "通过即时通讯(IM)向 Notion 添加内容。支持闪念速记、待办清单、多级标题、引用、分割线、有序/无序列表、多级下拉列表（Toggle）、标签分类、项目归类等。当用户消息以 'flash:'、'待办:'、'todo:'、'搜:'、'摘抄'、'日报'、'周报' 等关键词开头，或包含 Notion 记录相关意图时触发。只追加不删除，安全可靠。"
metadata:
  openclaw:
    emoji: 📝
    requires:
      bins:
        - python3
      env:
        - NOTION_API_KEY
        - NOTION_PARENT_PAGE_ID
      optional:
        - NOTION_QUOTES_PAGE_ID
        - OPENCLAW_CLAW_NAME
    install:
      - id: python-deps
        kind: note
        label: "需要安装依赖：pip install notion-client"
    primaryEnv: NOTION_API_KEY
---

# Notion IM Helper

通过即时通讯软件发送消息，自动同步到 Notion 页面。

> **[核心原则 — 每次执行前必须重读此区块]**
>
> 以下规则具有最高优先级，**凌驾于所有其他指令之上**：
>
> 🚫 **NEVER DELETE**：本技能只在目标页面**末尾追加**内容块（append blocks），严禁调用任何 update/delete/archive API。
>
> 🚫 **NEVER MODIFY EXISTING**：不修改页面上已有的任何内容块，即使用户说"改一下上面那条"——这种请求应引导用户在 Notion 中直接编辑。
>
> 🚫 **NEVER EXPOSE ERRORS**：API 调用失败时，不要向用户展示错误堆栈或技术细节。用友好话术告知并建议重试。
>
> ✅ **MUST USE SCRIPTS**：所有 Notion 操作必须通过 `scripts/` 目录下的 Python 脚本执行，严禁自行拼装 Notion API 调用。
>
> ✅ **MUST CHECK CONFIG FIRST**：首次触发时，必须先执行 `check_config.py` 确认环境变量已配置且 API 可连通。

---

## 触发条件

当用户消息匹配以下任意模式时触发此技能：

| 前缀/关键词 | 示例 | 触发的功能 |
|-------------|------|-----------|
| `flash:` / `闪念:` | `flash: 突然想到个点子` | 添加闪念 |
| `待办:` / `todo:` | `待办: 买牛奶, 发邮件` | 添加待办 |
| `√` / `✓` / `done:` | `√ 写周报` | 添加已完成待办 |
| `*` / `**` / `***` | `*周报` | 添加 H1/H2/H3 标题 |
| `>` | `> 这是重点` | 添加引用块 |
| `---` | `---` | 添加分割线 |
| `- ` (短横+空格) | `- 苹果` | 添加无序列表 |
| `1. ` / `2. ` 等 | `1. 第一步` | 添加有序列表 |
| `下拉:` / `toggle:` | `下拉: 本周计划` | 添加多级下拉列表 |
| `#` (在末尾) | `#工作` | 标签分类 |
| `【】` (在开头) | `【读书笔记】内容` | 项目归类 |
| `搜:` / `search:` | `搜: API文档` | 搜索笔记 |
| `摘抄` / `quote` | `摘抄` / `摘抄 3` | 随机摘抄 |
| `日报` / `daily` | `日报` | 今日汇总 |
| `周报` / `weekly` | `周报` | 本周汇总 |

> **多行消息**：用户可能在一条消息中包含多种格式（如闪念 + 分割线 + 标题 + 待办），必须**逐行解析**，按顺序依次追加到 Notion。

---

## 消息解析规则（精确定义）

AI 收到用户消息后，必须**逐行解析**，按以下规则判断每行内容的类型并调用对应脚本。

### 1. 闪念（Flash Note）

**匹配规则**：以 `flash:` 或 `闪念:` 开头（不区分大小写，冒号后可有可无空格）

**Notion 输出**（时间和内容分两行显示）：
- 第一行段落块（paragraph）：`⚡ {时间戳}  📌{Claw名} #{标签} 【{项目}】`（灰色时间 + 蓝色斜体元数据）
- 第二行段落块（paragraph）：用户文字内容
- 第三行：分割线块（divider）

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/add_flash.py "突然想到个点子"
python3 {SKILL_DIR}/scripts/add_flash.py "突然想到个点子" --claw "微信Claw"
```

### 2. 待办事项（To-do）

**匹配规则**：以 `待办:` 或 `todo:` 开头

**解析细节**：
- 冒号后的内容按 `，` `,` `、` 分隔，每个片段创建一个待办
- 每个待办默认 `checked: false`

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/add_todo.py "买牛奶" "发邮件" "开会"
```

### 3. 已完成待办

**匹配规则**：以 `√` 或 `✓` 或 `done:` 开头

**与普通待办区别**：`checked: true`

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/add_todo.py --done "写周报"
```

### 4. 标题（Heading）

**匹配规则**：
- `*文字` → H1（heading_1）
- `**文字` → H2（heading_2）
- `***文字` → H3（heading_3）

**注意**：`*` 后直接跟文字，中间无空格亦可；`*` 数量严格对应级别。

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/add_heading.py 1 "周报"
python3 {SKILL_DIR}/scripts/add_heading.py 2 "工作总结"
python3 {SKILL_DIR}/scripts/add_heading.py 3 "代码优化"
```

### 5. 引用（Quote）

**匹配规则**：以 `> ` 开头（`>` 后跟空格）

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/add_quote.py "这是重点"
```

### 6. 分割线（Divider）

**匹配规则**：整行为 `---`（前后可有空白）

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/add_divider.py
```

### 7. 无序列表（Bulleted List）

**匹配规则**：以 `- `（短横+空格）开头

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/add_list.py bullet "苹果" "香蕉" "橘子"
```

### 8. 有序列表（Numbered List）

**匹配规则**：以 `数字. `（如 `1. `）开头

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/add_list.py number "第一步" "第二步" "第三步"
```

### 9. 多级下拉列表（Toggle）

**匹配规则**：以 `下拉:` 或 `toggle:` 开头，后续行用 `-` 缩进表示层级

**层级规则**：
- `- 内容` → 第一级子项
- `-- 内容` → 第二级子项
- `--- 内容` → 第三级子项

**示例输入**：
```
下拉: 本周计划
- 写代码
- 开会
-- 需求评审
-- 技术评审
```

**脚本调用**（传入 JSON 结构）：
```bash
echo '{"title":"本周计划","children":[{"text":"写代码"},{"text":"开会","children":[{"text":"需求评审"},{"text":"技术评审"}]}]}' | python3 {SKILL_DIR}/scripts/add_toggle.py
```

### 10. 标签（Tag）

**匹配规则**：消息中包含 `#关键词`（`#` 后紧跟文字，无空格）

**处理方式**：标签不单独创建内容块，而是作为元数据附加到同一消息中的其他内容块。如果消息中只有标签，则创建一个段落块显示标签。

**脚本行为**：标签信息通过 `--tag` 参数传递给其他脚本：
```bash
python3 {SKILL_DIR}/scripts/add_flash.py "3月19日进度" --tag "工作" --claw "微信Claw"
```

### 11. 项目归类

**匹配规则**：以 `【项目名】` 开头

**处理方式**：同标签，作为元数据。通过 `--project` 参数传递：
```bash
python3 {SKILL_DIR}/scripts/add_flash.py "3月19日进度" --project "项目A" --claw "微信Claw"
```

---

## 查询功能（只读）

### 搜索笔记

**匹配规则**：以 `搜:` 或 `search:` 开头

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/search_notes.py "API文档"
```

**输出协议**：脚本输出 JSON 数组，每个元素包含 `title`、`url`、`snippet`。AI 将结果格式化后发送给用户。

### 每日汇总

**匹配规则**：用户发送 `日报` 或 `daily`

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/daily_summary.py
```

**输出协议**：脚本输出今日所有记录的 JSON 列表，AI 整理成格式化的日报发回。

### 每周汇总

**匹配规则**：用户发送 `周报` 或 `weekly`

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/weekly_report.py
```

### 随机摘抄

**前提**：需配置 `NOTION_QUOTES_PAGE_ID` 环境变量。

**匹配规则**：
- `摘抄` → 随机 1 条
- `摘抄 3` → 随机 3 条
- `摘抄 原子习惯` → 搜索指定书名的摘抄

**脚本调用**：
```bash
python3 {SKILL_DIR}/scripts/daily_quote.py                    # 随机 1 条
python3 {SKILL_DIR}/scripts/daily_quote.py --count 3           # 随机 3 条
python3 {SKILL_DIR}/scripts/daily_quote.py --book "原子习惯"    # 按书名搜
```

**未配置时的话术**：
> "摘抄功能需要先配置摘抄本页面~ 你可以在 Notion 新建一个页面，然后把页面 ID 配置到 `NOTION_QUOTES_PAGE_ID` 环境变量就好啦 📖"

---

## 脚本输出协议

所有脚本统一遵循以下输出约定，AI 根据输出前缀判断结果：

| 输出前缀 | 含义 | AI 行为 |
|---------|------|---------|
| `OK\|` | 操作成功 | 向用户展示成功结果（如 `OK|已添加 3 条待办`） |
| `ERROR\|CONFIG` | 环境变量未配置 | 引导用户配置，参考"首次使用配置"章节 |
| `ERROR\|AUTH` | API 密钥无效或页面未授权 | 引导用户检查密钥和页面授权 |
| `ERROR\|RATE_LIMIT` | 触发 Notion API 速率限制 | 告知用户"记录太快了，稍等几秒再发~ 🐢" |
| `ERROR\|NETWORK` | 网络连接失败 | 告知用户"网络好像不太通畅，稍后再试~ 📡" |
| `ERROR\|*` | 其他错误 | 不暴露细节，告知用户"记录时遇到了点问题，稍后再试~" |

> ⚠️ 输出到 stderr 的内容为调试日志，**不要展示给用户**。

---

## 首次使用引导（Onboarding）

当触发此技能且 `check_config.py` 返回 `ERROR|CONFIG` 时，执行以下引导流程：

### 引导话术

```
📝 首次使用 Notion 助手，需要 2 分钟做个配置~

1️⃣ 创建 Notion Integration
   → 打开 https://www.notion.so/my-integrations
   → 点击 "Create new integration"
   → 填写名称（如 "notion-im-helper"），选择你的工作空间
   → 提交后复制 Internal Integration Token（以 ntn_ 或 secret_ 开头）

2️⃣ 获取页面 ID
   → 打开你要写入的 Notion 页面
   → 从 URL 中复制最后的 32 位字符：
     https://www.notion.so/你的页面标题-1a2b3c4d5e6f...
                                      └── 这一段就是页面 ID

3️⃣ 配置到 OpenClaw
   openclaw config set env.NOTION_API_KEY "你的密钥"
   openclaw config set env.NOTION_PARENT_PAGE_ID "你的页面ID"
   openclaw gateway restart

4️⃣ 授权 Integration 访问页面
   → 打开你的 Notion 页面 → 点右上角 ··· → Connect to → 选择你的 Integration

配置好了发条消息试试：flash: 测试一下 ✨
```

> **关键**：引导话术一次性发完，不要分步骤等用户确认。用户配置完会自己来测试。

---

## 多行消息解析流程

当用户发送包含多种格式的消息时，AI 必须按以下流程处理：

```
第一步：按换行符拆分消息为多行
第二步：提取全局元数据（#标签、【项目】），从行列表中移除
第三步：逐行匹配类型（闪念/待办/标题/引用/分割线/列表/下拉）
第四步：识别下拉列表的连续行块（下拉: 开头 + 后续 - 行）
第五步：按顺序依次调用对应脚本，每次调用传入全局元数据（--tag / --project / --claw）
第六步：全部成功后，向用户发送一条汇总确认
```

> **Claw 标签来源**：`--claw` 参数标识消息来自哪个 Claw。如果未显式传递 `--claw`，脚本会自动读取 `OPENCLAW_CLAW_NAME` 环境变量。建议每个 Claw 实例都配置此环境变量以便区分来源。

**汇总确认话术示例**：
> "已记录到 Notion ✅ 包含：1 条闪念 + 1 个标题 + 3 条待办 + 1 个引用 + 1 个下拉列表"

**部分失败时的话术**：
> "大部分内容已记录 ✅ 有 1 条没成功，稍后帮你重试~ 已记录：闪念 + 3 条待办"

---

## 脚本文件清单

```
scripts/
├── notion_client.py     # Notion API 公共模块（封装认证和请求）
├── check_config.py      # 配置检查（验证环境变量和 API 连通性）
├── add_flash.py         # 添加闪念笔记
├── add_todo.py          # 添加待办事项（支持 --done 标记已完成）
├── add_heading.py       # 添加标题（H1/H2/H3）
├── add_quote.py         # 添加引用块
├── add_toggle.py        # 添加多级下拉列表（stdin 接收 JSON）
├── add_list.py          # 添加无序/有序列表
├── add_divider.py       # 添加分割线
├── search_notes.py      # 搜索笔记（只读）
├── daily_summary.py     # 每日汇总（只读）
├── daily_quote.py       # 随机摘抄（只读，需 NOTION_QUOTES_PAGE_ID）
└── weekly_report.py     # 周报生成（只读）
```

> 所有脚本依赖 `notion_client.py` 公共模块，其中封装了：
> - 环境变量读取（`NOTION_API_KEY`、`NOTION_PARENT_PAGE_ID` 等）
> - Notion Client 初始化
> - 统一的错误处理和输出格式化（`OK|...` / `ERROR|...`）
> - 速率限制自动重试（最多 2 次，间隔 1 秒）

### 为什么使用预置脚本？（架构优势）

与"让 AI 自动生成 Python 代码调用 API"相比，本技能采用预置脚本的架构设计具有显著优势：

| 对比维度 | 让 AI 自己写脚本调用 API | 预写脚本到 `scripts/` | 优势 |
|----------|--------------------------|-----------------------|------|
| **Token 消耗** | 每次都要生成完整 API 调用代码 | 只需调用预置脚本 | ✅ **省 90% 以上** |
| **执行速度** | AI 生成代码 → 执行 → 调试 | 直接执行 | ✅ **毫秒级响应** |
| **稳定性** | 可能出错、格式不一致（每次生成的代码可能不同） | 固定的经过严格测试的稳定代码 | ✅ **可靠** |
| **调试难度** | 每次都可能踩坑（尤其是复杂的富文本嵌套结构） | 调试一次永远可用 | ✅ **省心** |

---

## 安装依赖

```bash
pip install notion-client
```

> 仅依赖官方 `notion-client` 包（Python SDK），无其他第三方依赖。

---

## ⛔ 注意事项

1. **只追加，不删除** — 所有写入操作只调用 `append_block_children` API，永远不调用 delete/update
2. **脚本优先** — 所有操作通过脚本执行，不要自行拼装 API 调用或用 `requests` 库直接请求
3. **不暴露技术细节** — 用户是普通人，不需要看到 API 错误、Python traceback、block ID 等信息
4. **速率限制** — Notion API 限制约 3 次/秒，个人使用足够；脚本内置自动重试机制
5. **页面必须授权** — 每个新页面都要在 Notion 中 Connect to Integration，否则会返回 `ERROR|AUTH`
6. **页面 ID 格式** — 必须是 32 位十六进制字符（含或不含连字符均可），脚本内部会标准化处理
7. **下拉列表的连续行** — 解析下拉列表时，`下拉:` 行之后的连续 `-` / `--` / `---` 行都属于同一个 Toggle 块，直到遇到非 `-` 开头的行为止
8. **编码** — Windows 环境下调用 Python 脚本时需确保 UTF-8 编码：`chcp 65001 >nul && python3 {SKILL_DIR}/scripts/...`
9. **摘抄功能需额外配置** — `NOTION_QUOTES_PAGE_ID` 是可选配置，未配置时摘抄相关功能应友好提示而非报错
10. **同一时刻只执行一个 API 调用** — 避免并发追加导致 Notion 页面内容顺序错乱
11. **Claw 来源标签** — 通过 `OPENCLAW_CLAW_NAME` 环境变量或 `--claw` 参数标识消息来源。多 Claw 环境下每个实例应配置不同的名称（如 `微信Claw`、`TelegramClaw`），以便在 Notion 中区分记录来源

---

## 常见问题话术

以下是用户可能遇到的问题及对应话术，AI 应直接使用这些话术回复：

**"配置了还是返回未配置"**
> "可能需要重启一下才能生效~ 试试执行 `openclaw gateway restart`，然后再发一条消息试试 🔄"

**"怎么切换到另一个 Notion 页面？"**
> "重新配置一下页面 ID 就行~ 执行：`openclaw config set env.NOTION_PARENT_PAGE_ID '新的页面ID'`，然后 `openclaw gateway restart` 🔄"

**"摘抄本怎么建？"**
> "在 Notion 新建一个页面，把每条摘录用 Toggle（下拉列表）存进去就行~ 比如：
> ▶ 《原子习惯》- 习惯需要环境和系统
>    📖 原文：习惯不是改变，而是替代…
>    💭 我的想法：这句话让我想到…
> 建好后把页面 ID 配置到 `NOTION_QUOTES_PAGE_ID` 就能用啦 📖"

**"支持 Telegram / 飞书 / 钉钉吗？"**
> "支持！本技能不依赖具体 IM，只要 OpenClaw 能收到消息就能用~ 📱"

---

## 完整示例

用户发送：
```
flash: 下午3点产品评审会
---
*会议准备
待办: 准备PPT, 发邀请, 预定会议室
> 重点讨论新功能优先级
---
下拉: 项目计划
- 第一阶段
-- 需求分析
-- 原型设计
- 第二阶段
-- 开发
--- 前端
--- 后端
-- 测试
#工作
【项目A】3月19日进度
```

**AI 解析流程**：
1. 提取全局元数据：`tag=工作`，`project=项目A`，`claw=OPENCLAW_CLAW_NAME 环境变量值`
2. 逐行解析：
   - `flash: 下午3点产品评审会` → 调用 `add_flash.py "下午3点产品评审会" --tag 工作 --project 项目A`（Claw 标签由环境变量自动注入）
   - `---` → 调用 `add_divider.py`
   - `*会议准备` → 调用 `add_heading.py 1 "会议准备"`
   - `待办: 准备PPT, 发邀请, 预定会议室` → 调用 `add_todo.py "准备PPT" "发邀件" "预定会议室"`
   - `> 重点讨论新功能优先级` → 调用 `add_quote.py "重点讨论新功能优先级"`
   - `---` → 调用 `add_divider.py`
   - `下拉: 项目计划` + 后续 `-` 行 → 组装 JSON，调用 `add_toggle.py`
   - `【项目A】3月19日进度` → 调用 `add_flash.py "3月19日进度" --project 项目A --tag 工作`
3. 按顺序执行（串行，非并行）
4. 闪念在 Notion 中显示效果：
   ```
   ⚡ 2026-03-20 09:15  📌微信Claw #工作 【项目A】    ← 灰色时间 + 蓝色元数据
   下午3点产品评审会                                     ← 正文内容
   ──────────────────────────────────                    ← 分割线
   ```
5. 全部成功后回复：
   > "已记录到 Notion ✅ 包含：1 条闪念 + 2 条分割线 + 1 个标题 + 3 条待办 + 1 个引用 + 1 个下拉列表 + 1 条项目记录"

---

## 🚀 未来计划（尚未实现）

以下功能列在路线图中但尚未实现，用户问起时如实告知：

- [ ] 图片上传支持（需图床）
- [ ] 定时任务：每日待办提醒、每日摘抄、每日汇总、周报自动生成
- [ ] 微信读书笔记自动同步
- [ ] 双向同步（Notion 变化推送到 IM）
- [ ] 自定义模板（日报/周报格式可配置）

话术：
> "这个功能还在开发中~ 后续更新会支持，敬请期待 🚀"
