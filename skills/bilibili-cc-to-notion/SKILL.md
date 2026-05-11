---
name: bilibili-cc-to-notion
description: |
  将B站视频字幕转换为带截图的Notion学习笔记。
  当用户需要从B站视频提取字幕、分析内容并创建Notion学习笔记时，必须使用此技能。
  支持BV号、完整URL输入，自动下载CC字幕，智能处理内容，生成带截图标记的结构化学习笔记。
  适用于学习、研究、知识整理等场景。
---

# Bilibili CC to Notion Skill

## 🎯 Purpose

你是专业的视频字幕处理助手，任务是将B站视频字幕完整转换为Notion学习笔记。整个流程由你负责文本处理，而不是使用固定的Python程序。

### 核心工作流程

1. **下载字幕**：调用 `download_bilibili_cc` 工具下载B站视频字幕
2. **处理字幕**：你负责将字幕转换为结构化的Markdown笔记
3. **生成截图**：调用 `screenshot_tool` 工具从视频中提取截图
4. **上传图片**：调用 `upload_file_to_notion` 工具上传截图到Notion
5. **创建笔记**：调用 `create_notion_notes_with_images` 工具创建Notion页面

### 你处理字幕的要求（重要！）

**你的角色**：你是一个什么都不懂的学习者，正在认真学习这门课程。你的任务是根据字幕内容生成真正的学习笔记，而不是简单截取片段。

#### 1. 处理流程

**第一步：完整阅读并理解**
- 逐字阅读所有字幕内容（2536行，约25分钟视频）
- 理解老师讲解的每个知识点
- 标记出重点内容和关键概念

**第二步：提取知识点**
- 不遗漏任何知识点，即使是口语化的表达也要提取核心信息
- 识别课程的结构：章节、小节、重点
- 标记出老师强调的重点内容

**第三步：构建知识框架**
- 建立知识点之间的逻辑关系
- 构建层次化的知识结构
- 形成完整的知识体系

**第四步：添加学习心得**
- 作为学习者，记录学习过程中的思考
- 对每个知识点的理解和感悟
- 知识点之间的联系和应用场景

#### 2. 笔记结构要求

你的学习笔记必须包含以下章节：

```
# [课程标题] 学习笔记

## 一、课程概览
- 视频标题：[完整标题]
- 视频链接：[URL]
- 课程时长：[XX分XX秒]
- 学习时间：[日期]
- 学习者：[你的角色]

## 二、知识框架（思维导图式）
用层级结构展示课程的知识体系：

```
中心主题
├── 第一章：xxx
│   ├── 1.1 xxx
│   │   ├── 知识点1
│   │   └── 知识点2
│   └── 1.2 xxx
├── 第二章：xxx
└── ...
```

## 三、详细学习内容

### 第一章：[章节标题]

#### 1.1 [小节标题]
**知识点描述**：
- [完整描述老师讲解的内容]

**我的理解**：
- [作为学习者的理解]
- [知识点的实际应用]

**重点强调**：
- [老师强调的重点内容]
- [需要特别注意的地方]

**思考与疑问**：
- [学习过程中的思考]
- [可能的疑问或延伸思考]

[重复以上结构 for 每个知识点...]

## 四、核心概念总结

### 概念1：[概念名称]
- **定义**：[精确定义]
- **应用场景**：[何时使用]
- **关键特征**：[重要特点]

[重复 for 每个核心概念...]

## 五、学习心得与体会

### 5.1 对课程的整体理解
[描述对整个课程的理解和把握]

### 5.2 知识点的联系与整合
[描述不同知识点之间的联系]

### 5.3 实际应用思考
[思考如何将所学应用到实际中]

### 5.4 需要进一步学习的内容
[识别知识盲点和需要深入学习的地方]

## 六、关键公式/方法总结
[列出课程中所有重要的公式、方法、规则]

## 七、常见问题与解答
[整理课程中提到的常见问题和老师的解答]
```

#### 3. 内容质量要求

**完整性**：
- ✅ 不遗漏任何知识点
- ✅ 包含所有重要概念
- ✅ 记录老师的每个重点强调

**深度**：
- ✅ 不只是记录，要有理解
- ✅ 添加学习者的心得体会
- ✅ 有思考、有疑问、有延伸

**逻辑性**：
- ✅ 知识点之间有逻辑关系
- ✅ 层次清晰，结构完整
- ✅ 符合认知规律

**实用性**：
- ✅ 便于复习和回顾
- ✅ 知识点易于理解和记忆
- ✅ 有实际应用价值

#### 4. 输出格式

你需要输出两个部分：

**第一部分：结构化JSON**
```json
{
  "segments": [
    {
      "start_time": "00:00:03",
      "end_time": "00:00:07",
      "text": "字幕内容",
      "is_key_point": true/false,
      "concepts": ["概念1", "概念2"]
    }
  ],
  "markdown_content": "完整的学习笔记Markdown"
}
```

**第二部分：完整的学习笔记Markdown**
- 按照上面的结构要求
- 包含所有章节
- 有思维导图式的知识框架
- 有学习者的心得体会

#### 5. 示例对比

**❌ 错误的笔记（简单截取）**：
```
### 片段 1: 00:01:48
但这里面啊主要是两个方面内容三个方面吧

### 片段 2: 00:06:35
那么我们在这里啊给大家先说一下
```

**✅ 正确的笔记（真正的学习笔记）**：
```
## 三、详细学习内容

### 第四章：电力系统的运行特点

#### 4.1 电力系统的基本特点
**知识点描述**：
老师讲解了电力系统的三个基本特点：发、输、配、用电同时完成，不能大量存储，需要满足用户需求。

**我的理解**：
电力系统是一个实时平衡的系统，发电、输电、配电、用电必须同时完成，这与普通的商品供应链完全不同。就像供水系统一样，水龙头一开，水就要立刻流出来，不能等待。

**重点强调**：
- 老师特别强调"同时完成"这个特点
- 不能大量存储是电力系统的核心挑战
- 需要备用容量来应对负荷变化

**思考与疑问**：
- 为什么不能大量存储电能？
- 新型储能技术能否解决这个问题？
- 如何平衡供需关系？
```

#### 6. 特别注意

1. **不要简单截取**：不要只是把字幕片段列出来，要真正理解和整理
2. **要有学习者视角**：以"我"的角度记录学习过程
3. **要有思考**：记录学习过程中的疑问、联想、应用思考
4. **要有框架**：建立知识体系，而不是零散的知识点
5. **要有深度**：不只是记录是什么，还要思考为什么、怎么做
```
# 学习笔记标题

## 第一章：视频信息
- 视频标题：xxx
- 视频链接：https://...
- 处理时间：2026-03-12

## 第二章：内容概览
- 总片段数：X
- 关键知识点：Y

## 第三章：学习内容
### 片段 1: hh:mm:ss
字幕内容...

### 片段 2: hh:mm:ss
字幕内容...

## 第四章：关键知识点总结
- 知识点1：...
- 知识点2：...
```

#### 4. 截图标记规则（关键！）

**必须在以下情况下添加截图标记：**

1. **代码讲解**：当提到代码、函数、变量、类、方法等
   ```
   在代码中，我们使用以下函数来计算功率 Screenshot-[00:00:20]
   ```

2. **UI交互操作**：当提到点击、按钮、菜单、界面等操作
   ```
   点击这里查看课程大纲 Screenshot-[00:00:07]
   ```

3. **视觉指代词**：包含"这里"、"这儿"、"那里"、"那样"等
   ```
   如图所示，电力系统包括... Screenshot-[00:00:12]
   ```

4. **网址/链接/地址**：任何提及URL、API endpoint、GitHub等
   ```
   访问 https://example.com 获取资源 Screenshot-[00:00:16]
   ```

5. **任何借助视觉材料更易理解的内容**

**截图标记格式必须严格为：**
```
字幕内容 Screenshot-[hh:mm:ss]
```
其中时间点使用字幕片段的开始时间（hh:mm:ss格式）

#### 5. 输出要求

你需要输出以下内容：
1. **segments**：处理后的字幕片段数组（包含时间、文本、是否需要截图等）
2. **markdown_content**：完整的Markdown笔记内容（包含截图标记）

**示例输出：**
```json
{
  "segments": [
    {
      "start_time": "00:00:03",
      "end_time": "00:00:07",
      "text": "在这个课程中，我们将学习电力系统的基本概念",
      "is_key_point": false
    },
    {
      "start_time": "00:00:12",
      "end_time": "00:00:16",
      "text": "如图所示，电力系统包括发电、输电、配电和用电四个部分",
      "is_key_point": true,
      "concepts": ["电力系统"]
    }
  ],
  "markdown_content": "# 学习笔记\n\n## 片段 1: 00:00:03\n在这个课程中，我们将学习电力系统的基本概念\n\n## 片段 2: 00:00:12\n如图所示，电力系统包括发电、输电、配电和用电四个部分 Screenshot-[00:00:12]"
}
```

## 🔧 Available Tools

### 工具清单

| 工具 | 功能 | 使用时机 |
|------|------|----------|
| `download_bilibili_cc` | 下载B站视频CC字幕 | 用户提供B站视频URL时 |
| `screenshot_tool` | 从视频中提取截图 | 你处理完字幕后需要截图时 |
| `upload_file_to_notion` | 上传本地文件到Notion | 需要将截图上传到Notion时 |
| `create_notion_notes_with_images` | 在Notion中创建学习笔记（支持图片插入） | 处理完字幕和截图后创建笔记 |

## ⚙️ Setup & Configuration

### 1. 获取Notion API Token

1. 访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 点击 "New integration"
3. 填写名称并选择工作空间
4. 复制 **Internal Integration Token**（格式：`secret_xxx`）

### 2. 分享数据库给Integration

1. 打开你的Notion数据库
2. 点击右上角 `...` 菜单
3. 选择 "Connections"
4. 搜索并选择你创建的integration

### 3. 设置环境变量

```bash
export NOTION_API_KEY="secret_xxx"  # 你的Notion API token
export NOTION_DATABASE_ID="your_database_id"  # 目标数据库ID
```

### ⚠️ 安全说明 / Security Notes

**凭证管理 / Credentials**：
- 本技能需要 Notion API Token (`NOTION_API_KEY`) 和数据库 ID (`NOTION_DATABASE_ID`)
- 请勿将真实 Token 提交到公开仓库；使用环境变量或安全 vaults
- Token 仅用于调用 Notion API，不会发送到其他服务器

**脚本文件 / Script Files**：
- `process_subtitles.py` 已不再由大模型调用，仅保留作为参考或备用
- 核心流程通过大模型生成的结构化 JSON/Markdown 驱动脚本执行

**命令行安全 / Command Line Safety**：
- 部分脚本（如 `bilibili_to_notion_workflow.py`）使用 `shell=True` 执行命令
- 建议在可信环境下使用，避免让模型处理包含特殊字符的未校验输入

**依赖来源 / Dependencies**：
- BBDown：官方 GitHub Releases（可信来源）
- FFmpeg：系统包管理器安装（可信来源）
- Python requests 库：PyPI（可信来源）

### 4. 安装依赖

```bash
# 安装Python依赖
pip install requests

# 下载BBDown（B站下载器）
curl -L -o /tmp/BBDown.zip "https://github.com/nilaoda/BBDown/releases/download/1.6.3/BBDown_1.6.3_20240814_linux-x64.zip"
unzip /tmp/BBDown.zip -d /tmp/
chmod +x /tmp/BBDown

# 安装FFmpeg（用于截图）
apt-get install ffmpeg
```

### 5. BBDown使用注意事项

**重要：下载字幕时必须使用 `--skip-ai false` 参数**

BBDown默认会跳过AI字幕下载，必须明确指定不禁用此选项：

```bash
# ✅ 正确：下载AI字幕
BBDown "视频URL" --sub-only --skip-ai false --work-dir /输出目录

# ❌ 错误：会跳过AI字幕
BBDown "视频URL" --sub-only --work-dir /输出目录
```

**完整下载示例**：
```bash
# 下载字幕（优先AI字幕）
BBDown "https://www.bilibili.com/video/BV1xx411c7mW" \
  --sub-only \
  --skip-ai false \
  --work-dir /tmp/subtitles

# 下载视频（720P清晰度，需要登录）
BBDown "https://www.bilibili.com/video/BV1xx411c7mW" \
  --use-app-api \
  -q "720P" \
  --work-dir /tmp/videos
```

**BBDown常用参数**：
| 参数 | 说明 |
|------|------|
| `--sub-only` | 仅下载字幕 |
| `--skip-ai false` | **必须使用**：不禁用AI字幕下载 |
| `--use-app-api` | 使用APP端API（通常更稳定） |
| `--use-tv-api` | 使用TV端API |
| `-q "720P"` | 指定清晰度（720P、1080P等） |
| `--work-dir` | 指定工作目录 |
| `-p 6` | 指定下载第6P |
| `-p ALL` | 下载所有分P |

**登录方式**（必需！否则只能下载低清晰度）：
```bash
# 方式1：二维码登录（需要显示界面）
BBDown login

# 方式2：Cookie登录（推荐，无需显示界面）
# 获取Cookie：浏览器登录B站 → F12 → Network → 找到Cookie
BBDown --cookie "你的cookie字符串" "视频URL"

# 方式3：TV端登录
BBDown logintv
```

**清晰度说明**：
| 登录状态 | 可下载清晰度 |
|----------|--------------|
| 未登录 | 最高480P |
| 已登录WEB账号 | 最高1080P |
| 已登录TV/APP账号 | 最高4K/8K |

**建议**：使用Cookie登录以获取更高清晰度和完整字幕。

## 🛠️ Tool Definitions

### Tool 1: download_bilibili_cc

**Purpose**: Download CC subtitles from a Bilibili video

**Input parameters**:
- `url` (string, required): Bilibili video URL or BV number
- `output` (string, optional): Output directory path

**Output parameters**:
- `success` (boolean): Whether download was successful
- `subtitle_file` (string): Path to downloaded subtitle file
- `video_title` (string): Video title

### Tool 2: screenshot_tool

**Purpose**: Extract screenshots from video and replace markers in Markdown

**Input parameters**:
- `video` (string, optional): Video file path
- `markdown` (string, optional): Markdown file path
- `output_dir` (string, optional): Output directory for screenshots

**Output parameters**:
- `output` (string): Path to processed Markdown file
- `screenshots_dir` (string): Directory containing screenshots
- `screenshot_count` (number): Number of screenshots generated

### Tool 3: upload_file_to_notion

**Purpose**: Upload local files to Notion using Direct Upload API

**Input parameters**:
- `token` (string, required): Notion API token
- `file` (string, required): Path to local file to upload

**Output parameters**:
- `success` (boolean): Whether upload was successful
- `file_upload_id` (string): ID of uploaded file (for referencing in Notion)

### Tool 4: create_notion_notes_with_images

**Purpose**: Create Notion learning notes with embedded images (supports file upload)

**Input parameters**:
- `token` (string, required): Notion API token
- `database_id` (string, required): Notion database ID
- `video_title` (string, required): Video title
- `video_url` (string, required): Original Bilibili video URL
- `segments` (array, required): Processed subtitle segments
- `markdown_content` (string, optional): Markdown content with screenshot markers
- `tags` (array, optional): Tags for organizing notes
- `images_dir` (string, optional): Directory containing screenshot images

**Output parameters**:
- `success` (boolean): Whether page creation was successful
- `page_id` (string): ID of created Notion page
- `page_url` (string): URL of created Notion page
- `segments_processed` (number): Number of segments added
- `images_embedded` (number): Number of images embedded

## 📝 Complete Workflow Example

**User input**: "帮我把这个B站视频做成带截图的学习笔记：https://www.bilibili.com/video/BV11u4m1c7ZV?p=6"

**Model workflow**:

### Step 1: Download subtitles
调用 `download_bilibili_cc` 工具下载字幕（自动使用 `--skip-ai false` 参数下载AI字幕）

### Step 2: 你处理字幕

1. **读取字幕文件**：从下载的字幕文件中读取所有内容
2. **逐字保留**：禁止任何删减、总结或省略，必须逐字保留所有文字
3. **添加标点和段落**：为每句话添加合适的标点符号，适当划分自然段
4. **添加截图标记**：在适当位置添加 `Screenshot-[hh:mm:ss]` 标记
5. **输出结构化JSON**：包含segments数组和markdown_content

**截图标记规则（你必须遵守）**：

| 场景 | 示例 | 截图标记 |
|------|------|----------|
| 代码讲解 | "在代码中，我们使用以下函数..." | `Screenshot-[00:00:20]` |
| UI交互操作 | "点击这里查看课程大纲" | `Screenshot-[00:00:07]` |
| 视觉指代词 | "如图所示，电力系统包括..." | `Screenshot-[00:00:12]` |
| 网址/链接 | "访问 https://example.com" | `Screenshot-[00:00:16]` |
| 任何借助视觉材料 | 任何需要看图才能理解的内容 | `Screenshot-[时间]` |

**输出格式示例**：
```json
{
  "segments": [
    {
      "start_time": "00:00:03",
      "end_time": "00:00:07",
      "text": "在这个课程中，我们将学习电力系统的基本概念",
      "is_key_point": false
    },
    {
      "start_time": "00:00:12",
      "end_time": "00:00:16",
      "text": "如图所示，电力系统包括发电、输电、配电和用电四个部分",
      "is_key_point": true,
      "concepts": ["电力系统"]
    }
  ],
  "markdown_content": "# 学习笔记\n\n## 片段 1: 00:00:03\n在这个课程中，我们将学习电力系统的基本概念\n\n## 片段 2: 00:00:12\n如图所示，电力系统包括发电、输电、配电和用电四个部分 Screenshot-[00:00:12]"
}
```

### Step 3: Generate screenshots
调用 `screenshot_tool` 工具从视频提取截图

**注意**：screenshot_tool会自动替换Markdown中的`Screenshot-[hh:mm:ss]`标记为图片路径`assets/screenshot_hh_mm_ss.jpg`。你需要将这个路径修正为实际路径（如`/tmp/screenshots/screenshot_hh_mm_ss.jpg`）才能在Notion中正确显示。

### Step 4: Upload images to Notion
调用 `upload_file_to_notion` 工具上传截图

### Step 5: Create Notion notes
调用 `create_notion_notes_with_images` 工具创建笔记

### Step 6: Notion重复检查与清理（必须执行）
1. 创建成功或失败后，调用 Notion API 查询数据库，检查是否生成了标题重复的页面（尤其是报错但标题已落库的情况）。
2. 保留最新的最终版本，其他同标题的旧版/出错版设置 `archived: true` 进行软删除。
3. 清理时注意不要误删用户已有的其他笔记（只清理本次处理的同标题页面）。

**Output to user**: "✅ 已成功创建带截图的Notion学习笔记：https://www.notion.so/xxx"

### Complete Workflow Script

You can also use the integrated workflow script:

```bash
python3 bilibili_to_notion_workflow.py \
  --url "https://www.bilibili.com/video/BV11u4m1c7ZV?p=6" \
  --token "$NOTION_API_KEY" \
  --database-id "$NOTION_DATABASE_ID" \
  --output-dir "./output"
```

This script automatically handles all steps:
1. Downloads Bilibili subtitles
2. Processes subtitles and identifies key points
3. Generates screenshots at key timestamps
4. Uploads images to Notion
5. Creates a complete Notion learning笔记 with embedded images

## 🎯 When to Use This Skill

**Use this skill when user**:
- Provides Bilibili video URL or BV number
- Wants to extract video subtitles
- Needs to create learning notes from video content
- Mentions "带截图"、"截图"、"图片" etc.
- Asks to convert video content to structured notes with visual aids

**Do NOT use this skill when**:
- User wants to download video files without notes
- User wants to edit existing Notion pages
- User provides non-Bilibili video URLs

## ⚙️ Configuration Requirements

### 必需工具
- ✅ BBDown: B站下载器
- ✅ FFmpeg: 视频截图工具
- ✅ Python 3.7+: 运行脚本

### 环境变量
```bash
export NOTION_API_KEY="secret_xxx"  # Notion API token
export NOTION_DATABASE_ID="xxx"     # 目标数据库ID（可选）
```

### 文件结构
```
工作目录/
├── video.mp4              # 视频文件
├── subtitles.srt          # 字幕文件（由你处理）
├── output/
│   └── screenshots/       # 截图保存目录
└── notes_with_images.md   # 处理后的Markdown（带图片链接）
```

**注意**：字幕处理由你负责，不使用固定的Python程序

## 📊 Expected Output Format

### Success Case
```
✅ 已下载字幕: [文件路径]
✅ 已处理字幕: [X]个片段, [Y]个关键点
✅ 已生成截图: [X]张图片
✅ 已创建Notion笔记: [页面链接]
```

### Error Cases
```
❌ 字幕下载失败: [错误信息]
❌ 视频未找到: 请提供视频文件路径
❌ Notion API错误: [错误信息]
```

## 🔍 Quality Criteria

### For download_bilibili_cc
- ✅ Successfully downloads CC subtitles
- ✅ Handles both BV numbers and full URLs
- ✅ Returns video title and file path

### For model text processing
- ✅逐字保留字幕所有文字，不删减不总结
- ✅为每句话添加合适的标点和段落
- ✅在适当位置添加截图标记 Screenshot-[hh:mm:ss]
- ✅输出结构化的JSON（segments和markdown_content）
- ✅正确识别需要截图的场景（代码、UI操作、视觉指代、链接等）

### For screenshot_tool
- ✅ Extracts screenshots at correct timestamps
- ✅ Replaces markers with image links
- ✅ Handles missing video gracefully

### For create_notion_notes_with_images
- ✅ Creates properly formatted Notion pages
- ✅ Automatically uploads local images to Notion
- ✅ Embeds uploaded images in the page
- ✅ Includes timestamp links back to video
- ✅ Handles API errors gracefully

### For upload_file_to_notion
- ✅ Successfully uploads files using Notion Direct Upload API
- ✅ Returns file_upload_id for referencing in Notion
- ✅ Handles file not found errors
- ✅ Supports various file types (images, PDFs, videos, etc.)

## 🚨 故障排除

### BBDown下载问题

**问题1：字幕只有几秒钟**
- **原因**：BBDown默认跳过AI字幕下载
- **解决**：使用 `--skip-ai false` 参数

**问题2：只能下载480P清晰度**
- **原因**：未登录B站账号
- **解决**：使用Cookie登录或二维码登录

**问题3：下载失败/解析失败**
- **原因**：网络问题或视频URL错误
- **解决**：
  - 检查网络连接
  - 确认视频URL正确
  - 尝试使用不同API：`--use-app-api` 或 `--use-tv-api`

### Notion上传问题

**问题1：图片无法显示**
- **原因**：Markdown中的图片路径错误
- **解决**：确保使用绝对路径（如`/tmp/screenshots/screenshot_xxx.jpg`）

**问题2：上传失败**
- **原因**：文件过大或网络问题
- **解决**：
  - Notion免费账号限制5MB/文件
  - 检查网络连接
  - 确认API token有效

### 字幕处理问题

**问题1：字幕片段太少**
- **原因**：process_subtitles.py的min_length过滤
- **解决**：现在由大模型处理，不受此限制

**问题2：截图标记未正确添加**
- **原因**：大模型未按规则添加标记
- **解决**：确保按规则在代码、UI操作、视觉指代、链接等位置添加`Screenshot-[hh:mm:ss]`

## 📚 References

- Bilibili API: https://space.bilibili.com/
- Notion API: https://developers.notion.com/
- BBDown: https://github.com/nilaoda/BBDown
