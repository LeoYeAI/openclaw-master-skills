<div align="center">

[English](README.md) | **中文**

# nblm

### AI 编程助手通往 NotebookLM 的桥梁

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-purple.svg)](https://github.com/vercel-labs/add-skill)
[![License](https://img.shields.io/github/license/magicseek/nblm)](LICENSE)

<br/>

🧠 **零幻觉** — 答案完全基于你的文档
<br/>
⚡ **零切换** — 在编辑器中提问、上传、生成播客和幻灯片
<br/>
🔌 **无限来源** — 今天是 Z-Library，明天是 arXiv / Notion / Confluence

<br/>

<sub>支持 **Claude Code** · **Cursor** · **Windsurf** · **Codex** · 以及任何兼容 [Agent Skills](https://github.com/vercel-labs/add-skill) 的 AI 助手</sub>

<br/>

[安装](#安装) · [快速开始](#快速开始) · [命令](#命令) · [架构](#架构)

</div>

---

## 安装

### 推荐：使用 add-skill CLI

```bash
npx add-skill magicseek/nblm
```

适用于任何支持的 AI 助手。为特定助手安装：

```bash
# 仅 Claude Code
npx add-skill magicseek/nblm -a claude-code

# 全局安装（跨项目可用）
npx add-skill magicseek/nblm --global

# 多个助手
npx add-skill magicseek/nblm -a claude-code -a cursor -a opencode
```

### 备选：平台特定初始化

如果 `add-skill` 创建的符号链接在你的环境中无法正常工作（如 Cursor、Windows），可以直接生成平台特定文件：

**macOS / Linux:**
```bash
# 克隆仓库
git clone https://github.com/magicseek/nblm ~/.nblm

# 为你的 AI 助手初始化（在项目目录中运行）
python ~/.nblm/scripts/run.py init --ai cursor       # Cursor
python ~/.nblm/scripts/run.py init --ai claude       # Claude Code
python ~/.nblm/scripts/run.py init --ai codex        # Codex CLI
python ~/.nblm/scripts/run.py init --ai antigravity  # Antigravity
python ~/.nblm/scripts/run.py init --ai windsurf     # Windsurf
python ~/.nblm/scripts/run.py init --ai copilot      # GitHub Copilot
python ~/.nblm/scripts/run.py init --ai all          # 所有平台

# 列出可用平台
python ~/.nblm/scripts/run.py init --list
```

**Windows (PowerShell):**
```powershell
# 克隆仓库
git clone https://github.com/magicseek/nblm $env:USERPROFILE\.nblm

# 为你的 AI 助手初始化（在项目目录中运行）
python $env:USERPROFILE\.nblm\scripts\run.py init --ai cursor       # Cursor
python $env:USERPROFILE\.nblm\scripts\run.py init --ai claude       # Claude Code
python $env:USERPROFILE\.nblm\scripts\run.py init --ai codex        # Codex CLI
python $env:USERPROFILE\.nblm\scripts\run.py init --ai antigravity  # Antigravity
python $env:USERPROFILE\.nblm\scripts\run.py init --ai windsurf     # Windsurf
python $env:USERPROFILE\.nblm\scripts\run.py init --ai copilot      # GitHub Copilot
python $env:USERPROFILE\.nblm\scripts\run.py init --ai all          # 所有平台

# 列出可用平台
python $env:USERPROFILE\.nblm\scripts\run.py init --list
```

这会在你的项目目录中生成相应的技能/命令文件（如 `.cursor/commands/nblm.md`）。

### 首次运行

首次使用时，nblm 会自动：
- 创建隔离的 Python 环境（`.venv`）
- 安装 Python 和 Node.js 依赖
- 按需启动 agent-browser 守护进程

无需手动设置。如果缺少 Playwright 浏览器，在技能文件夹中运行 `npm run install-browsers`。

---

## 快速开始

### 1. Google 认证（仅需一次）

```
/nblm login
```

浏览器窗口将打开进行 Google 登录。只需执行一次。

### 2. 添加笔记本到库

前往 [notebooklm.google.com](https://notebooklm.google.com) → 创建笔记本 → 上传文档 → 设置"任何有链接的人"可访问

```
/nblm add <笔记本-url-或-id>
```

nblm 会自动查询笔记本以发现其内容和元数据。

### 3. 提问

```
/nblm ask "文档中关于认证的说明是什么？"
```

答案基于来源，带有上传文档的引用。

### 4. 管理笔记本

```
/nblm local          # 列出库中的笔记本
/nblm remote         # 列出 NotebookLM API 中的所有笔记本
/nblm status         # 显示认证和库状态
```

### 5. 上传来源

```
/nblm upload ./document.pdf           # 本地文件
/nblm upload-url https://example.com  # 网页 URL
/nblm upload-zlib <z-library-url>     # Z-Library 图书
```

---

## 命令

<details>
<summary><strong>📚 笔记本管理</strong></summary>

| 命令 | 说明 |
|------|------|
| `/nblm login` | Google 认证 |
| `/nblm status` | 显示认证和库状态 |
| `/nblm local` | 列出本地库中的笔记本 |
| `/nblm remote` | 列出 NotebookLM API 中的所有笔记本 |
| `/nblm create <名称>` | 创建新笔记本 |
| `/nblm delete [--id ID]` | 删除笔记本 |
| `/nblm rename <名称> [--id ID]` | 重命名笔记本 |
| `/nblm summary [--id ID]` | 获取 AI 生成的摘要 |
| `/nblm describe [--id ID]` | 获取描述和建议主题 |
| `/nblm add <url-或-id>` | 添加笔记本到本地库 |
| `/nblm activate <id>` | 设置活动笔记本 |

</details>

<details>
<summary><strong>📄 来源管理</strong></summary>

| 命令 | 说明 |
|------|------|
| `/nblm sources [--id ID]` | 列出笔记本中的来源 |
| `/nblm upload <文件>` | 上传本地文件（PDF、TXT、MD、DOCX） |
| `/nblm upload-zlib <url>` | 从 Z-Library 下载并上传 |
| `/nblm upload-url <url>` | 添加 URL 作为来源 |
| `/nblm upload-youtube <url>` | 添加 YouTube 视频作为来源 |
| `/nblm upload-text <标题> [--content TEXT]` | 添加文本作为来源 |
| `/nblm source-text <source-id>` | 获取完整索引文本 |
| `/nblm source-guide <source-id>` | 获取 AI 摘要和关键词 |
| `/nblm source-rename <source-id> <名称>` | 重命名来源 |
| `/nblm source-refresh <source-id>` | 重新获取 URL 内容 |
| `/nblm source-delete <source-id>` | 删除来源 |

</details>

<details>
<summary><strong>💬 聊天与查询</strong></summary>

| 命令 | 说明 |
|------|------|
| `/nblm ask <问题>` | 查询 NotebookLM |

</details>

<details>
<summary><strong>🎙️ 媒体生成</strong></summary>

| 命令 | 说明 |
|------|------|
| `/nblm podcast [--instructions TEXT]` | 生成音频播客（深度对话） |
| `/nblm podcast-status <task-id>` | 检查播客生成状态 |
| `/nblm podcast-download [输出路径]` | 下载最新播客 |
| `/nblm briefing [--instructions TEXT]` | 生成简短音频摘要 |
| `/nblm debate [--instructions TEXT]` | 生成辩论式音频 |
| `/nblm slides [--instructions TEXT]` | 生成幻灯片 |
| `/nblm slides-download [输出路径]` | 下载幻灯片 PDF |
| `/nblm infographic [--instructions TEXT]` | 生成信息图 |
| `/nblm infographic-download [输出路径]` | 下载信息图 |
| `/nblm media-list [--type TYPE]` | 列出生成的媒体 |
| `/nblm media-delete <id>` | 删除生成的媒体项 |

**媒体生成选项：**

| 选项 | 值 |
|------|-----|
| `--length` | `SHORT`、`DEFAULT`、`LONG` |
| `--instructions` | 内容的自定义指令 |
| `--wait` | 等待生成完成 |
| `--output` | 下载路径（需配合 `--wait`） |

</details>

---

## 架构

nblm 采用混合方式，优先使用 API 操作，浏览器自动化作为后备：

```
┌─────────────────────────────────────────────────────────────┐
│                       你的 AI 助手                           │
│              (Claude Code / Cursor / OpenCode)              │
└─────────────────────┬───────────────────────────────────────┘
                      │ /nblm 命令
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                         nblm                                │
├─────────────────────┬───────────────────────────────────────┤
│   notebooklm-py     │         agent-browser                 │
│   (API 操作)        │      (浏览器自动化)                    │
│                     │                                       │
│ • 创建笔记本        │ • Google 认证                          │
│ • 添加来源          │ • 文件上传（后备）                      │
│ • 聊天查询          │ • Z-Library 下载                       │
│ • 生成媒体          │ • 未来非 API 来源                      │
└─────────────────────┴───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Google NotebookLM                         │
│            (Gemini 驱动的文档问答)                           │
└─────────────────────────────────────────────────────────────┘
```

**核心组件：**

| 组件 | 作用 |
|------|------|
| **[notebooklm-py](https://github.com/teng-lin/notebooklm-py)** | NotebookLM API 操作的异步 Python 客户端 |
| **[agent-browser](https://github.com/vercel-labs/agent-browser)** | 用于认证和非 API 来源的无头浏览器守护进程 |
| **scripts/run.py** | 自动管理虚拟环境和依赖的入口点 |

**数据存储**（在 `data/` 目录）：
- `library.json` — 你的笔记本元数据
- `auth/google.json` — Google 认证状态
- `auth/zlibrary.json` — Z-Library 认证状态

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 找不到技能 | 验证安装：`ls ~/.claude/skills/nblm/` |
| `ModuleNotFoundError` | 始终使用 `/nblm` 命令 — 它们会自动管理环境 |
| 认证失败 | 使用可见浏览器运行 `/nblm login` |
| `DAEMON_UNAVAILABLE` | 确保已安装 Node.js，然后在技能文件夹中运行 `npm install` |
| 速率限制（50/天） | 等待 24 小时或使用其他 Google 账号 |
| 浏览器崩溃 | 运行 `python scripts/run.py cleanup_manager.py --preserve-library` |

更多详情，请查看 [references/troubleshooting.md](references/troubleshooting.md)。

---

## 致谢

nblm 基于这些优秀项目构建：

- **[notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill)** by PleasePrompto — 原始的 Claude Code NotebookLM 集成技能，使用浏览器自动化
- **[zlibrary-to-notebooklm](https://github.com/zstmfhy/zlibrary-to-notebooklm)** by zstmfhy — Z-Library 到 NotebookLM 管道
- **[notebooklm-py](https://github.com/teng-lin/notebooklm-py)** by teng-lin — NotebookLM 异步 Python API 客户端

其他依赖：
- **[agent-browser](https://github.com/vercel-labs/agent-browser)** — AI 助手的无头浏览器守护进程
- **[add-skill](https://github.com/vercel-labs/add-skill)** — AI 编程助手的通用技能安装器

---

## 限制

- **速率限制** — 免费层每个 Google 账号每天约 50 次查询
- **无会话持久化** — 每次查询独立（无"上一个答案"上下文）
- **手动创建笔记本** — 需要通过 [notebooklm.google.com](https://notebooklm.google.com) 创建笔记本和上传文档

## 许可证

MIT

---

<div align="center">

**nblm** — 从你的文档获取基于来源的答案，直接在你的编程助手中使用。

[报告问题](https://github.com/magicseek/nblm/issues) · [在 GitHub 上查看](https://github.com/magicseek/nblm)

</div>
