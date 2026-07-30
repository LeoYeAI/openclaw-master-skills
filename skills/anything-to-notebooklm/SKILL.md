---
name: anything-to-notebooklm
description: 多源内容智能处理器：支持微信公众号、网页、YouTube、PDF、Markdown等，自动上传到NotebookLM并生成播客/PPT/思维导图等多种格式
user-invocable: true
homepage: https://github.com/joeseesun/anything-to-notebooklm
---

# 多源内容 → NotebookLM 智能处理器

自动从多种来源获取内容，上传到 NotebookLM，并根据自然语言指令生成播客、PPT、思维导图等多种格式。

## 支持的内容源

### 1. 微信公众号文章
通过 MCP 服务器自动抓取微信公众号文章内容（绕过反爬虫）

### 2. 任意网页链接
支持任何公开可访问的网页（新闻、博客、文档等）

### 3. YouTube 视频
自动提取 YouTube 视频的字幕和元数据

### 4. Office 文档
- **Word (DOCX)** - 保留表格和格式
- **PowerPoint (PPTX)** - 提取幻灯片和备注
- **Excel (XLSX)** - 表格数据

### 5. 电子书与文档
- **PDF** - 全文提取
- **EPUB** - 电子书全文提取
- **Markdown (.md)** - 原生支持

### 6. 图片与扫描件
- **Images** (JPEG, PNG, GIF, WebP) - OCR 识别文字
- 扫描的 PDF 文档 - OCR 提取文字

### 7. 音频文件
- **Audio** (WAV, MP3) - 语音转文字

### 8. 结构化数据
- **CSV** - 逗号分隔数据
- **JSON** - JSON 数据
- **XML** - XML 文档

### 9. 压缩包
- **ZIP** - 自动解压并处理所有支持的文件

### 10. 纯文本
直接输入或粘贴的文本内容

### 11. 搜索关键词
通过 Web Search 搜索关键词，汇总多个来源的信息

## 前置条件

### 1. 安装 wexin-read-mcp

MCP 服务器已安装在：`~/.claude/skills/anything-to-notebooklm/wexin-read-mcp/`

**配置 MCP**（需要手动添加到 Claude 配置文件）：

**macOS**: 编辑 `~/.claude/config.json`

```json
{
  "primaryApiKey": "any",
  "mcpServers": {
    "weixin-reader": {
      "command": "python",
      "args": [
        "/Users/joe/.claude/skills/anything-to-notebooklm/wexin-read-mcp/src/server.py"
      ]
    }
  }
}
```

**配置后需要重启 Claude Code。**

### 2. notebooklm 认证

首次使用前必须认证：

```bash
notebooklm login
notebooklm list  # 验证认证成功
```

## 触发方式

### 微信公众号文章
- `/anything-to-notebooklm [微信文章链接]`
- "把这篇微信文章传到NotebookLM"
- "把这篇微信文章生成播客"

### 网页链接
- "把这个网页做成播客 [URL]"
- "这篇文章帮我做成PPT [URL]"
- "帮我分析这个网页 [URL]"

### YouTube 视频
- "把这个YouTube视频做成播客 [YouTube URL]"
- "这个视频帮我生成思维导图 [YouTube URL]"

### 本地文件
- "把这个PDF上传到NotebookLM /path/to/file.pdf"
- "这个Markdown文件生成PPT /path/to/file.md"
- "这个EPUB电子书生成播客 /path/to/book.epub"
- "把这个Word文档做成思维导图 /path/to/doc.docx"
- "这个PowerPoint生成Quiz /path/to/slides.pptx"
- "把这个扫描PDF做成报告 /path/to/scan.pdf"（自动OCR）

### 搜索关键词
- "搜索 'AI发展趋势' 并生成报告"
- "搜索关于'量子计算'的资料做成播客"

### 混合使用
- "把这篇文章、这个视频和这个PDF一起上传，生成一份报告"

## 自然语言 → NotebookLM 功能映射

| 用户说的话 | 识别意图 | NotebookLM 命令 |
|-----------|---------|----------------|
| "生成播客" / "做成音频" / "转成语音" | audio | `generate audio` |
| "做成PPT" / "生成幻灯片" / "做个演示" | slide-deck | `generate slide-deck` |
| "画个思维导图" / "生成脑图" / "做个导图" | mind-map | `generate mind-map` |
| "生成Quiz" / "出题" / "做个测验" | quiz | `generate quiz` |
| "做个视频" / "生成视频" | video | `generate video` |
| "生成报告" / "写个总结" / "整理成文档" | report | `generate report` |
| "做个信息图" / "可视化" | infographic | `generate infographic` |
| "生成数据表" / "做个表格" | data-table | `generate data-table` |
| "做成闪卡" / "生成记忆卡片" | flashcards | `generate flashcards` |

**如果没有明确指令**，默认只上传不生成任何内容，等待用户后续指令。

## 工作流程

### Step 1: 识别内容源类型

Claude 自动识别输入类型：

| 输入特征 | 识别为 | 处理方式 |
|---------|-------|---------|
| `https://mp.weixin.qq.com/s/` | 微信公众号 | MCP 工具抓取 |
| `https://youtube.com/...` 或 `https://youtu.be/...` | YouTube | 直接传递给 NotebookLM |
| `https://` 或 `http://` | 网页 | 直接传递给 NotebookLM |
| `/path/to/file.pdf` | PDF 文件 | markitdown 转 Markdown → TXT |
| `/path/to/file.epub` | EPUB 电子书 | markitdown 转 Markdown → TXT |
| `/path/to/file.docx` | Word 文档 | markitdown 转 Markdown → TXT |
| `/path/to/file.pptx` | PowerPoint | markitdown 转 Markdown → TXT |
| `/path/to/file.xlsx` | Excel | markitdown 转 Markdown → TXT |
| `/path/to/file.md` | Markdown | 直接上传 |
| `/path/to/image.jpg` | 图片（OCR） | markitdown OCR → TXT |
| `/path/to/audio.mp3` | 音频 | markitdown 转录 → TXT |
| `/path/to/file.zip` | ZIP 压缩包 | 解压 → markitdown 批量转换 |
| 关键词（无URL，无路径） | 搜索查询 | WebSearch → 汇总 → TXT |

### Step 2: 获取内容

**微信公众号**：
- 使用 MCP 工具 `read_weixin_article`
- 返回：title, author, publish_time, content
- 保存为 TXT：`/tmp/weixin_{title}_{timestamp}.txt`

**网页/YouTube**：
- 直接使用 URL 调用 `notebooklm source add [URL]`
- NotebookLM 自动提取内容

**Office 文档/电子书/PDF**：
- 使用 markitdown 转换为 Markdown
- 命令：`markitdown /path/to/file.docx -o /tmp/converted.md`
- 保存为 TXT：`/tmp/{filename}_converted_{timestamp}.txt`

**本地 Markdown**：
- 直接上传：`notebooklm source add /path/to/file.md`

**图片（OCR）**：
- markitdown 自动 OCR 识别文字
- 提取 EXIF 元数据
- 保存为 TXT

**音频文件**：
- markitdown 自动转录语音为文字
- 提取音频元数据
- 保存为 TXT

**ZIP 压缩包**：
- 自动解压到临时目录
- 遍历所有支持的文件
- 批量使用 markitdown 转换
- 合并为单个 TXT 或多个 Source

**搜索关键词**：
- 使用 WebSearch 工具搜索关键词
- 汇总前 3-5 条结果
- 保存为 TXT：`/tmp/search_{keyword}_{timestamp}.txt`

### Step 3: 上传到 NotebookLM

调用 `notebooklm` skill：

```bash
notebooklm create "{title}"  # 创建新笔记本
notebooklm source add /tmp/weixin_xxx.txt --wait  # 上传文件并等待处理完成
```

**等待处理完成很重要**，否则后续生成会失败。

### Step 5: 根据意图生成内容（可选）

如果用户指定了处理意图，自动调用对应命令：

| 意图 | 命令 | 等待 | 下载 |
|------|------|------|------|
| audio | `notebooklm generate audio` | `artifact wait` | `download audio ./output.mp3` |
| slide-deck | `notebooklm generate slide-deck` | `artifact wait` | `download slide-deck ./output.pdf` |
| mind-map | `notebooklm generate mind-map` | `artifact wait` | `download mind-map ./map.json` |
| quiz | `notebooklm generate quiz` | `artifact wait` | `download quiz ./quiz.md --format markdown` |
| video | `notebooklm generate video` | `artifact wait` | `download video ./output.mp4` |
| report | `notebooklm generate report` | `artifact wait` | `download report ./report.md` |
| infographic | `notebooklm generate infographic` | `artifact wait` | `download infographic ./infographic.png` |
| flashcards | `notebooklm generate flashcards` | `artifact wait` | `download flashcards ./cards.md --format markdown` |

**生成流程**：
1. 发起生成请求（返回 task_id）
2. 等待生成完成（`artifact wait <task_id>`）
3. 下载生成的文件到本地
4. 告知用户文件路径

## 完整示例

### 示例 1：微信公众号文章 → 播客

**用户输入**：
```
把这篇文章生成播客 https://mp.weixin.qq.com/s/abc123xyz
```

**执行流程**：
1. 识别为微信公众号链接
2. MCP 工具抓取文章内容
3. 创建 TXT 文件
4. 上传到 NotebookLM
5. 生成播客（`generate audio`）
6. 下载播客到本地

**输出**：
```
✅ 微信文章已转换为播客！

📄 文章：深度学习的未来趋势
👤 作者：张三
📅 发布：2026-01-20

🎙️ 播客已生成：
📁 文件：/tmp/weixin_深度学习的未来趋势_podcast.mp3
⏱️ 时长：约 8 分钟
📊 大小：12.3 MB
```

### 示例 2：YouTube 视频 → 思维导图

**用户输入**：
```
这个视频帮我画个思维导图 https://www.youtube.com/watch?v=abc123
```

**执行流程**：
1. 识别为 YouTube 链接
2. 直接传递给 NotebookLM（自动提取字幕）
3. 生成思维导图（`generate mind-map`）
4. 下载思维导图

**输出**：
```
✅ YouTube 视频已转换为思维导图！

🎬 视频：Understanding Quantum Computing
⏱️ 时长：23 分钟

🗺️ 思维导图已生成：
📁 文件：/tmp/youtube_quantum_computing_mindmap.json
📊 节点数：45 个
```

### 示例 3：搜索关键词 → 报告

**用户输入**：
```
搜索 'AI发展趋势 2026' 并生成报告
```

**执行流程**：
1. 识别为搜索查询
2. WebSearch 搜索关键词
3. 汇总前 5 条结果
4. 创建 TXT 文件
5. 上传到 NotebookLM
6. 生成报告（`generate report`）

**输出**：
```
✅ 搜索结果已生成报告！

🔍 关键词：AI发展趋势 2026
📊 来源：5 篇文章

📄 报告已生成：
📁 文件：/tmp/search_AI发展趋势2026_report.md
📝 章节：7 个
📊 大小：15.2 KB
```

### 示例 4：混合多源 → PPT

**用户输入**：
```
把这篇文章、这个视频和这个PDF一起做成PPT：
- https://example.com/article
- https://youtube.com/watch?v=xyz
- /Users/joe/Documents/research.pdf
```

**执行流程**：
1. 创建新 Notebook
2. 依次添加 3 个 Source
3. 基于所有 Source 生成 PPT

**输出**：
```
✅ 多源内容已整合为PPT！

📚 内容源：
  1. 网页文章：AI in 2026
  2. YouTube：Future of AI
  3. PDF：Research Notes (12 页)

📊 PPT 已生成：
📁 文件：/tmp/multi_source_slides.pdf
📄 页数：25 页
📦 大小：3.8 MB
```

### 示例 5: EPUB 电子书 → 播客

**用户输入**：
```
把这本电子书做成播客 /Users/joe/Books/sapiens.epub
```

**执行流程**：
1. 识别为 EPUB 文件
2. markitdown 转换为 Markdown
3. 保存为 TXT
4. 上传到 NotebookLM
5. 生成播客

**输出**：
```
✅ EPUB 电子书已转换为播客！

📚 电子书：Sapiens: A Brief History of Humankind
📄 页数：约 450 页
📊 字数：约 15 万字

🎙️ 播客已生成：
📁 文件：/tmp/sapiens_podcast.mp3
⏱️ 时长：约 45 分钟（精华版）
📊 大小：48.2 MB
```

### 示例 6：Word 文档 → Quiz

**用户输入**：
```
这个Markdown生成Quiz /Users/joe/notes/machine_learning.md
```

**执行流程**：
1. 识别为本地 Markdown 文件
2. 直接上传到 NotebookLM
3. 生成 Quiz（`generate quiz`）

**输出**：
```
✅ Markdown 已转换为Quiz！

📄 文件：machine_learning.md
📊 大小：8.5 KB

📝 Quiz 已生成：
📁 文件：/tmp/machine_learning_quiz.md
❓ 题目：15 道（10选择 + 5简答）
```

## 错误处理

### URL 格式错误
```
❌ 错误：URL 格式不正确

必须是微信公众号文章链接：
https://mp.weixin.qq.com/s/xxx

你提供的链接：https://example.com
```

### 文章获取失败
```
❌ 错误：无法获取文章内容

可能原因：
1. 文章已被删除
2. 文章需要登录查看（暂不支持）
3. 网络连接问题
4. 微信反爬虫拦截（请稍后重试）

建议：
- 检查链接是否正确
- 等待 2-3 秒后重试
- 或手动复制文章内容
```

### NotebookLM 认证失败
```
❌ 错误：NotebookLM 认证失败

请运行以下命令重新登录：
  notebooklm login

然后验证：
  notebooklm list
```

### 生成任务失败
```
❌ 错误：播客生成失败

可能原因：
1. 文章内容太短（< 100 字）
2. 文章内容太长（> 50万字）
3. NotebookLM 服务异常

建议：
- 检查文章长度是否适中
- 稍后重试
- 或尝试其他格式（如生成报告）
```

## 高级功能

### 1. 多意图处理

用户可以一次性指定多个处理任务：

```
这篇文章帮我生成播客和PPT https://mp.weixin.qq.com/s/abc123
```

Skill 会依次执行：
1. 生成播客
2. 生成 PPT

### 2. 自定义 Notebook

默认每篇文章创建新 Notebook，也可以指定已有 Notebook：

```
把这篇文章加到我的【AI研究】笔记本 https://mp.weixin.qq.com/s/abc123
```

Skill 会：
1. 搜索名为"AI研究"的 Notebook
2. 将文章添加为新 Source
3. 基于所有 Sources 生成内容

### 3. 自定义生成指令

为生成任务添加具体要求：

```
这篇文章生成播客，要求：轻松幽默的风格，时长控制在5分钟
```

Skill 会将要求作为 instructions 传给 NotebookLM。

## 注意事项

1. **频率限制**：
   - 每次请求间隔 > 2 秒，避免被微信封禁
   - NotebookLM 生成任务有并发限制（最多 3 个同时进行）

2. **内容长度**：
   - 微信文章通常 1000-5000 字，适合生成播客（3-8 分钟）
   - 超过 10000 字的长文可能需要更长生成时间
   - 少于 500 字的短文可能生成效果不佳

3. **版权遵守**：
   - 仅用于个人学习研究
   - 遵守微信公众号的版权规定
   - 生成的内容不得用于商业用途

4. **生成时间**：
   - 播客：2-5 分钟
   - 视频：3-8 分钟
   - PPT：1-3 分钟
   - 思维导图：1-2 分钟
   - Quiz/闪卡：1-2 分钟

5. **文件清理**：
   - TXT 源文件保存在 `/tmp/`，系统重启后自动清理
   - 生成的文件（MP3/PDF/MD 等）默认保存在 `/tmp/`
   - 可以指定自定义保存路径

## 相关 Skills

- `notebooklm` - NotebookLM 核心功能
- `notebooklm-deep-analyzer` - 深度分析 NotebookLM 内容
- `markitdown` - 转换其他格式文档

## 配置 MCP（重要）

⚠️ **第一次使用前必须配置**

编辑 `~/.claude/config.json`：

```json
{
  "primaryApiKey": "any",
  "mcpServers": {
    "weixin-reader": {
      "command": "python",
      "args": [
        "/Users/joe/.claude/skills/anything-to-notebooklm/wexin-read-mcp/src/server.py"
      ]
    }
  }
}
```

**配置后重启 Claude Code！**

## 故障排查

### 1. MCP 工具未找到

```bash
# 测试 MCP 服务器
python ~/.claude/skills/anything-to-notebooklm/wexin-read-mcp/src/server.py

# 如果报错，检查依赖
cd ~/.claude/skills/anything-to-notebooklm/wexin-read-mcp
pip install -r requirements.txt
playwright install chromium
```

### 2. NotebookLM 命令失败

```bash
# 检查认证状态
notebooklm status

# 重新登录
notebooklm login

# 验证
notebooklm list
```

### 3. 文件权限问题

```bash
# 确保临时目录可写
chmod 755 /tmp

# 测试写入
touch /tmp/test.txt && rm /tmp/test.txt
```

### 4. 生成任务卡住

```bash
# 检查任务状态
notebooklm artifact list

# 如果显示 "pending" 超过 10 分钟，取消重试
# （目前 CLI 不支持取消，需要在网页端操作）
```

## 典型使用场景

### 场景 1：快速学习

```
我想学习这篇文章，帮我生成播客，上下班路上听
链接：https://mp.weixin.qq.com/s/abc123
```

→ 生成 8 分钟播客，通勤时间听完

### 场景 2：分享给团队

```
这篇文章不错，做成PPT分享给团队
https://mp.weixin.qq.com/s/abc123
```

→ 生成 15 页 PPT，直接用于团队分享

### 场景 3：复习巩固

```
这篇技术文章帮我出题，想测试一下掌握程度
https://mp.weixin.qq.com/s/abc123
```

→ 生成 10 道选择题 + 5 道简答题

### 场景 4：可视化理解

```
这篇文章概念比较多，画个思维导图帮我理清结构
https://mp.weixin.qq.com/s/abc123
```

→ 生成思维导图，一目了然

---

**Skill 创建时间**：2026-01-25
**最后更新**：2026-01-25
**版本**：v1.0.0
