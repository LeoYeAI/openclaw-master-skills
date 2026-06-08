---
name: local-ai-search
description: Natural language search for local files (100G-1T). Supports xlsx, pptx, pdf, docx formats with location info. Triggered when user asks to search local/computer/folder content.
---

# Local AI Search

## 触发条件

**当用户说以下内容时，调用此 Skill：**
- "帮我在本地搜索..."
- "帮我在本电脑搜索..."
- "帮我在某个文件夹中搜索..."
- "搜索本地文件..."
- "搜索我的文档..."
- "在本机查找..."
- "从我的文件中查找..."
- 或任何涉及**本地/本机/文件夹内容检索**的请求

## 功能说明

本 Skill 提供本地文件的 AI 智能搜索功能：
- ✅ 支持 xlsx, pptx, pdf, docx, md 等格式
- ✅ 自然语言查询（用日常语言描述要找的内容）
- ✅ 指定文件夹范围进行搜索
- ✅ 返回文件位置信息（工作表名、幻灯片页码）
- ✅ 无需本地大模型，使用云端 API

## 使用方式

### 方式一：直接搜索（推荐）

```
用户: 帮我在本地搜索关于销售数据的内容
用户: 在 ~/Documents/Projects 文件夹中搜索 API 相关的文档
用户: 搜索本电脑中包含"关键词"的文件
```

### 方式二：指定目录搜索

```
用户: 帮我在 ~/Documents/Projects 文件夹中搜索技术文档
```

### 方式三：自然语言查询

```
用户: 帮我找一下第三季度的销售报告
用户: 搜索一下关于数字化转型的内容
用户: 找找看有没有关于项目计划的 PPT
```

## 调用流程

1. **检查服务状态**：确认 Khoj 服务是否运行
2. **确定搜索范围**：用户指定的文件夹，或默认已索引的知识库
3. **执行搜索**：使用自然语言查询本地文件
4. **返回结果**：显示匹配的文件名、位置信息、内容片段

---

## 快速验证（已测试）

```bash
# 1. 启动 Khoj 服务（嵌入式 PostgreSQL 模式）
export USE_EMBEDDED_DB="true"
khoj --anonymous-mode

# 2. 转换文档
~/.agents/skills/local-ai-search/scripts/convert.py ~/Documents/source -o ~/Documents/converted

# 3. 索引文件（API 方式）
curl -X PATCH "http://localhost:42110/api/content" \
  -F "files=@~/Documents/converted/example.xlsx.md"

# 4. 搜索查询
~/.agents/skills/local-ai-search/scripts/query.py "搜索内容"
```

### 验证结果示例

```
[1] 文件: test_data.xlsx.md
    工作表: Sales Data
    内容: | Month | Sales | | January | $10,000 |...

[2] 文件: test_slides.pptx.md
    幻灯片: 第 1 页
    内容: # Project Overview This is a test presentation...
```

---

## 概述

基于 Khoj 的本地 RAG 知识库解决方案，支持大规模文件（100G到1T）的全文检索和自然语言查询。通过 MarkItDown 转换 Office 文档，结合云端 LLM API 实现轻量级部署，适合资源受限环境。

---

## 需求背景

### 核心需求

| 需求项 | 具体要求 |
|---|---|
| **数据规模** | 建议小于1T的数据量，例如200GB 本地文件 |
| **文件格式** | xlsx, pptx, pdf, docx, md 等 |
| **检索方式** | 自然语言查询 |
| **大模型** | 云端 API（OpenAI/DeepSeek/Claude/Qwen/Kimi/Minmax） |
| **定位精度** | 来源文件 + 大致位置（工作表/幻灯片） |
| **集成方式** | 封装为 OpenCode Skill |

### 硬件约束

| 约束项 | 配置 |
|---|---|
| **设备** | 常规个人PC，例如MacBook Air M2 |
| **内存** | 8GB+ 可用内存 |
| **剩余空间** | 足够的磁盘空间（文档大小的 25-40%）。例如200G的文件，需要有80GB空闲空间，支持本地向量数据库存储RAG结果。 |
| **本地 LLM** | 无法部署（资源不足） |

---

## 技术架构

### 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        OpenCode Skill                            │
│         rag query "搜索内容" --top-k 10                          │
│         rag index /path/to/files                                │
│         rag status                                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Khoj API Server                              │
│              localhost:42110                                    │
│         • 向量检索                                               │
│         • 对话生成                                               │
│         • 文件管理                                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐       ┌─────────────────────┐
│   PostgreSQL 数据库  │       │   云端 LLM API      │
│   (嵌入式 pgserver) │       │   多模型支持        │
│   • 向量存储         │       │   • Chat Model      │
│   • 文档索引         │       │   • 对话生成        │
│   • ~50-80GB        │       │   • 无本地占用      │
└─────────────────────┘       └─────────────────────┘
```

### 数据流

```
xlsx/pptx → MarkItDown 转换 → Markdown → Khoj 索引 → 向量数据库
                                    ↓
用户查询 → 向量检索 → 匹配片段 → 云端 LLM → 自然语言回答
                                    ↓
                           显示来源文件 + 位置
```

### 组件说明

| 组件 | 选择 | 理由 |
|---|---|---|
| **RAG 服务** | Khoj | 成熟（33k stars）、API 友好、内存占用低 |
| **文档转换** | MarkItDown | 微软开源、支持 xlsx/pptx、保留位置信息 |
| **向量数据库** | PostgreSQL（嵌入式） | 成熟稳定、pgvector 向量索引、8GB+ RAM 友好 |
| **Embedding** | 本地模型（sentence-transformers） | 免费、快速、隐私保护 |
| **LLM** | 云端 API | 解放内存压力、性能更好 |

---

## 安装部署

### 环境要求

- Python 3.10+
- macOS / Linux / Windows
- 建议 8GB+ 可用内存
- 足够的磁盘空间（文档大小的 25-40%）

### 平台支持

| 平台 | 支持状态 | 说明 |
|------|----------|------|
| macOS | ✅ 完全支持 | 原生支持，直接使用 |
| Linux | ✅ 完全支持 | 原生支持，直接使用 |
| Windows | ⚠️ 需要 WSL2 | 使用 WSL2 运行 Linux 环境 |

#### Windows 用户：安装 WSL2

**WSL2**（Windows Subsystem for Linux 2）让 Windows 可以直接运行 Linux，无需虚拟机或双系统。

```powershell
# 1. 在 Windows PowerShell（管理员模式）中运行
wsl --install

# 2. 重启电脑后，打开 "Ubuntu" 应用

# 3. 在 Ubuntu 终端中继续以下安装步骤
```

安装 WSL2 后，在 Ubuntu 终端中执行所有后续命令。

### 安装步骤

#### 1. 安装依赖

```bash
# 安装 Khoj
pip install khoj

# 安装 MarkItDown（含 Office 文档支持）
pip install "markitdown[xlsx,pptx]"
```

#### 2. 配置云端 LLM API

```bash
# OpenAI
export OPENAI_API_KEY="sk-xxx"

# DeepSeek（推荐，性价比高）
export OPENAI_API_KEY="sk-xxx"
export OPENAI_BASE_URL="https://api.deepseek.com/v1"

# Anthropic Claude
export ANTHROPIC_API_KEY="sk-xxx"
```

#### 3. 启动 Khoj 服务

```bash
# 嵌入式 PostgreSQL 模式（推荐个人使用）
export USE_EMBEDDED_DB="true"
khoj --anonymous-mode

# 访问 Web UI
open http://localhost:42110
```

---

## 使用指南

### 命令列表

| 命令 | 说明 | 示例 |
|---|---|---|
| `rag start` | 启动 Khoj 服务 | `rag start` |
| `rag stop` | 停止服务 | `rag stop` |
| `rag status` | 查看服务状态 | `rag status` |
| `rag convert <dir>` | 转换 xlsx/pptx 为 Markdown | `rag convert ~/Documents` |
| `rag index <dir>` | 索引文件到知识库 | `rag index ~/Documents/converted` |
| `rag query "<问题>"` | 查询知识库 | `rag query "第三季度销售数据"` |
| `rag clean` | 清理转换后的临时文件 | `rag clean` |
| `rag sync` | 增量同步目录到知识库 | `rag sync ~/Documents` |
| `rag schedule` | 管理定时同步任务 | `rag schedule ~/Documents --enable` |

### 文档转换

```bash
# 转换指定目录下的 xlsx/pptx 文件
markitdown convert ~/Documents/source -o ~/Documents/converted

# 转换单个文件
markitdown convert report.xlsx -o report.md
```

转换结果示例：

**Excel (xlsx)**:
```markdown
## Sheet1

| Name | Age | City |
|---|---|---|
| Alice | 30 | NYC |
| Bob | 25 | LA |

## Sheet2

| Product | Price |
|---|---|
| Apple | $1 |
```

**PowerPoint (pptx)**:
```markdown
<!-- Slide number: 1 -->

# Project Overview

This is the introduction...

<!-- Slide number: 2 -->

## Key Features

- Feature 1
- Feature 2
```

### 知识库索引

#### 方式一：Web UI

1. 打开 http://localhost:42110/config
2. 点击 "Add Content Source"
3. 选择文件夹路径
4. 等待索引完成

#### 方式二：API

```bash
curl -X PATCH "http://localhost:42110/api/content" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "files=@/path/to/document.md"
```

### 查询示例

```bash
# CLI 查询
khoj query "第三季度的销售数据在哪？"

# API 查询
curl "http://localhost:42110/api/search?q=第三季度销售数据&n=5" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**返回结果示例**：
```
来源文件: Q3_report.xlsx
位置: Sheet1
匹配内容:
| Month | Sales | Growth |
|---|---|---|
| July | $50,000 | +12% |
| August | $55,000 | +10% |
| September | $60,000 | +9% |

来源文件: sales.pptx
位置: Slide 5
匹配内容:
Q3 Sales Summary: Total $165,000
```

---

## 文件格式支持

| 格式 | 支持方式 | 位置信息 | 说明 |
|---|---|---|---|
| **xlsx/xls** | MarkItDown 转换 | ✅ 工作表名称 | 表格数据完整保留 |
| **pptx** | MarkItDown 转换 | ✅ 幻灯片编号 | 文本、表格提取 |
| **pdf** | Khoj 原生支持 | ✅ 页码 | 自动 OCR 扫描版 |
| **docx** | Khoj 原生支持 | ✅ 段落标题 | 完整文档结构 |
| **md/txt** | Khoj 原生支持 | ✅ 文件名 | 最佳支持 |
| **org** | Khoj 原生支持 | ✅ 文件名 | Emacs 用户友好 |

### 不支持的格式

| 格式 | 解决方案 |
|---|---|
| .epub | `pandoc book.epub -o book.md` |
| .html | `pandoc page.html -o page.md` |
| .rtf | `pandoc doc.rtf -o doc.md` |

---

## 空间与性能

### 空间估算

| 项目 | 空间占用 | 说明 |
|---|---|---|
| **原始文件** | 200GB | 保留不变 |
| **转换后 Markdown** | ~20-40GB | 索引后可删除 |
| **Khoj 安装** | ~0.5GB | Python 包 + 本地模型 |
| **向量数据库** | ~50-80GB | 索引文件 |
| **临时占用（最大）** | ~70-120GB | 索引过程中 |
| **最终占用** | ~250-280GB | 删除 Markdown 后 |

### 空间时间线

```
初始状态:     100GB 可用
安装后:       99.5GB 可用（-0.5GB）
转换后:       60-80GB 可用（-20-40GB）
索引完成:     10-30GB 可用（-50-80GB）← 最紧张时刻
删除 Markdown: 50-70GB 可用（+20-40GB）
```

### 性能指标

| 指标 | 数值 | 说明 |
|---|---|---|
| **索引速度** | ~1-2GB/小时 | 常规个人PC |
| **查询响应** | 50-200ms | 向量检索 |
| **对话生成** | 1-3秒 | 取决于云端 API |
| **内存占用** | ~200-500MB | 空闲时 |
| **索引时内存** | ~2-4GB | 取决于文件大小 |

---

## 云端 API 配置

### 支持的 LLM 提供商

| 提供商 | API Key 环境变量 | 模型示例 |
|---|---|---|
| **OpenAI** | `OPENAI_API_KEY` | gpt-4o, gpt-4o-mini |
| **DeepSeek** | `OPENAI_API_KEY` + `OPENAI_BASE_URL` | deepseek-chat, deepseek-reasoner |
| **Anthropic** | `ANTHROPIC_API_KEY` | claude-3-5-sonnet |
| **Google** | `GEMINI_API_KEY` | gemini-2.0-flash |
| **Qwen/通义** | `OPENAI_API_KEY` + `OPENAI_BASE_URL` | qwen-turbo, qwen-plus |
| **Kimi/月之暗面** | `OPENAI_API_KEY` + `OPENAI_BASE_URL` | moonshot-v1-8k |
| **Minimax** | `OPENAI_API_KEY` + `OPENAI_BASE_URL` | abab6.5-chat |
| **本地 Ollama** | - | llama3, qwen2.5 |

### 配置文件示例

```yaml
# ~/.khoj/config.yml

# LLM 配置
chat-model:
  provider: openai  # 或 deepseek, anthropic
  model: gpt-4o-mini
  api-key: ${OPENAI_API_KEY}

# Embedding 配置（使用本地模型）
embedding-model:
  provider: local
  model: BAAI/bge-small-zh-v1.5

# 数据库配置
database:
  type: sqlite
  path: ~/.khoj/khoj.db
```

---

## 最佳实践

### 增量索引建议

```bash
# 1. 先小规模测试
rag convert ~/Documents/test_folder
rag index ~/Documents/test_folder_converted

# 2. 观察实际空间占用
du -sh ~/.khoj/

# 3. 根据测试结果推算全量需求
# 4. 分批索引核心文件
rag convert ~/Documents/important_folder
rag index ~/Documents/important_folder_converted
```

### 定期维护

```bash
# 查看索引状态
rag status

# 清理过期文件
rag clean

# 备份知识库
cp -r ~/.khoj ~/.khoj_backup_$(date +%Y%m%d)

# 重新索引（更换 Embedding 模型后）
khoj --regenerate
```

### 故障排查

| 问题 | 解决方案 |
|---|---|
| 服务启动失败 | 检查端口 42110 是否被占用 |
| 索引速度慢 | 减少并发、关闭其他应用 |
| 内存不足 | 使用云端 Embedding API |
| 查询无结果 | 检查文件格式、重新索引 |

---

## 安全与隐私

### 数据安全

| 项目 | 说明 |
|---|---|
| **本地数据** | 所有向量存储在本地 PostgreSQL |
| **Embedding** | 默认使用本地模型，数据不上传 |
| **LLM 对话** | 仅查询内容发送到云端 API |
| **API Key** | 存储在本地环境变量或配置文件 |

### 隐私建议

- 敏感文档可使用本地 Embedding 模型
- 对话内容会被发送到云端 LLM，注意脱敏
- API Key 不要提交到版本控制
- 定期备份 ~/.khoj/ 目录

---

## 扩展与集成

### OpenCode Skill 集成

```bash
# Skill 目录结构
~/.agents/skills/khoj-rag/
├── SKILL.md              # 本文档
├── khoj_cli.py           # CLI 封装脚本
├── config.yaml           # 默认配置
└── scripts/
    ├── start_server.sh   # 启动服务
    ├── convert.py        # 批量转换
    └── query.py          # 查询封装
```

### API 集成

```python
import requests

KHOJ_URL = "http://localhost:42110"
API_KEY = "your-api-key"

# 搜索
response = requests.get(
    f"{KHOJ_URL}/api/search",
    params={"q": "查询内容", "n": 5},
    headers={"Authorization": f"Bearer {API_KEY}"}
)

# 对话
response = requests.post(
    f"{KHOJ_URL}/api/chat",
    json={"q": "问题内容"},
    headers={"Authorization": f"Bearer {API_KEY}"}
)
```

### 客户端支持

| 客户端 | 说明 |
|---|---|
| **Web UI** | http://localhost:42110 |
| **Obsidian 插件** | 自动同步 Markdown 笔记 |
| **Emacs** | `M-x khoj` 命令 |
| **Desktop App** | 跨平台桌面客户端 |
| **API** | RESTful API 接口 |

---

## 增量同步

### 手动触发同步

当文件有更新时，可以手动触发增量同步：

```bash
# 增量同步（只处理变化的文件）
~/.agents/skills/local-ai-search/scripts/sync.py ~/Documents

# 全量同步（强制重新索引所有文件）
~/.agents/skills/local-ai-search/scripts/sync.py ~/Documents --full

# 详细输出
~/.agents/skills/local-ai-search/scripts/sync.py ~/Documents --verbose
```

或使用 CLI：

```bash
# 增量同步
local-ai-search sync ~/Documents

# 全量同步
local-ai-search sync ~/Documents --full
```

### 定时自动同步

设置每小时自动同步：

```bash
# 启用定时同步（每小时）
~/.agents/skills/local-ai-search/scripts/schedule_sync.sh ~/Documents --enable

# 启用定时同步（每2小时）
~/.agents/skills/local-ai-search/scripts/schedule_sync.sh ~/Documents --enable --interval 2

# 查看定时同步状态
~/.agents/skills/local-ai-search/scripts/schedule_sync.sh --status

# 禁用定时同步
~/.agents/skills/local-ai-search/scripts/schedule_sync.sh --disable

# 立即执行一次同步
~/.agents/skills/local-ai-search/scripts/schedule_sync.sh ~/Documents --run
```

或使用 CLI：

```bash
# 启用定时同步
local-ai-search schedule ~/Documents --enable

# 设置每2小时同步
local-ai-search schedule ~/Documents --enable --interval 2

# 查看状态
local-ai-search schedule --status

# 禁用定时同步
local-ai-search schedule --disable
```

### 进度显示

在大规模索引时会显示进度：

```
扫描目录: ~/Documents
找到文件: 150 个
已索引: 120 个
需要同步: 30 个

[=============>         ] 60.0% (18/30) report.xlsx
✓ 成功: 28
✗ 失败: 2

同步完成！
```

### 同步原理

增量同步通过以下方式判断文件变化：

| 检查项 | 说明 |
|--------|------|
| 文件修改时间 | 文件被修改时时间会变化 |
| 文件大小 | 内容变化时大小会变化 |
| 已索引文件列表 | 对比 Khoj 已索引的文件 |

同步状态保存在 `~/.khoj/sync_state.json`，记录每个文件的同步状态。

---

## 常见问题

### Q1: 索引完成后可以删除 Markdown 文件吗？

**可以**。Khoj 已将内容存入向量数据库，Markdown 文件仅作为临时转换产物，索引完成后可安全删除，节省 20-40GB 空间。

### Q2: 如何处理内存限制？

- 使用嵌入式 PostgreSQL 模式（USE_EMBEDDED_DB=true）
- Embedding 使用本地模型（而非云端 API）
- LLM 使用云端 API（而非本地部署）
- 分批索引，避免一次性处理大量文件

### Q3: 查询结果能定位到具体单元格吗？

**默认不支持**。MarkItDown 保留工作表名称和幻灯片编号，但不保留单元格位置。如需精确定位，需自定义转换脚本。

### Q4: 支持实时文件监控吗？

**支持**。在 Khoj 配置中启用文件监控，文档变更会自动触发重新索引。

### Q5: 如何迁移到其他机器？

```bash
# 备份
tar -czf khoj_backup.tar.gz ~/.khoj/

# 恢复
tar -xzf khoj_backup.tar.gz -C ~/
```

---

## 参考资源

- [Khoj 官方文档](https://docs.khoj.dev/)
- [Khoj GitHub](https://github.com/khoj-ai/khoj)
- [MarkItDown GitHub](https://github.com/microsoft/markitdown)
- [DeepSeek API](https://platform.deepseek.com/)
- [OpenAI API](https://platform.openai.com/)

---

## 更新日志

| 版本 | 日期 | 说明 |
|---|---|---|
| 1.1.0 | 2026-03-20 | 新增增量同步、定时同步、进度显示功能 |
| 1.0.4 | 2026-03-20 | 添加 Windows 平台说明（需要 WSL2） |
| 1.0.3 | 2026-03-20 | 澄清数据库类型：Khoj 使用嵌入式 PostgreSQL（非 SQLite） |
| 1.0.1 | 2026-03-20 | 更新文档：数据规模调整，新增 LLM 支持 |
| 1.0.0 | 2026-03-20 | 初始版本 |

---

## 许可证

本 Skill 基于 MIT 许可证开源。Khoj 和 MarkItDown 分别遵循各自的许可证。