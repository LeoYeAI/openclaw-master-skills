# Bilibili CC to Notion Skill

## English Summary

This skill downloads Bilibili captions, produces rich learner-style notes with screenshots, and publishes to Notion.
Key steps: BBDown (`--skip-ai false`, login for HD) → model builds notes → screenshots → upload → Notion page.

---

## ✅ 概述 / Overview

一个从 Bilibili 字幕生成高质量学习笔记（含自动视频截图）并发布到 Notion 的完整技能。
A full pipeline to turn Bilibili subtitles into high-quality learning notes (with screenshots) in Notion.

## 🔧 技术实现

### 核心工具
- **BBDown**: B站视频下载器（用于下载字幕和视频）
- **FFmpeg**: 视频处理工具（用于截图）
- **Notion API**: 直接使用API创建页面、上传文件和嵌入内容

### 工作流程 / Workflow
```
用户输入 → 模型理解意图 → download_bilibili_cc (BBDown, --skip-ai false, 登录获取高清) →
大模型处理字幕（逐字保留、标点、截图标记、学习者笔记） → screenshot_tool 截图 →
upload_file_to_notion 上传图片 → create_notion_notes_with_images 创建 Notion 笔记 → 返回链接
```

**核心特点 / Key change**：字幕由ai学习并生成“学习笔记”，而非固定规则脚本，灵活性高。

### 🖊笔记生成效果
<img width="762" height="828" alt="image" src="https://github.com/user-attachments/assets/39564b6c-8944-4a19-af2b-6f7e99fa17bd" />
<img width="898" height="516" alt="image" src="https://github.com/user-attachments/assets/f6d9d5ba-6bbe-4be1-8c8e-afc8cbbecafd" />

感谢郝老师的精彩课程，老师B站主页[点击访问](https://space.bilibili.com/504156404),如有侵权请联系我删除，笔记效果仅供学习交流，本skill仅为探索提升学习效率的方式，不可代替系统性学习。

## 📁 文件结构

```
bilibili-cc-to-notion/
├── SKILL.md                    # 工具描述清单（符合规范）
├── README.md                   # 本文件
├── CONFIGURATION.md            # 详细配置说明
├── INTEGRATION_SUMMARY.md      # 集成总结
├── FINAL_SUMMARY.md            # 最终总结
├── scripts/
   ├── download_bilibili_cc.py       # 字幕下载工具
   ├── screenshot_tool.py            # 视频截图工具
   ├── upload_file_to_notion.py      # Notion文件上传工具
   ├── create_notion_notes_with_images.py  # 支持图片上传的Notion笔记创建
   └── bilibili_to_notion_workflow.py # 完整工作流程脚本

```

## 🛠️ 安装和配置

### 首先拉取本仓库放到对应的skill文件路径，然后安装以下依赖及配置：

### 1. 下载BBDown
```bash
curl -L -o /tmp/BBDown.zip "https://github.com/nilaoda/BBDown/releases/download/1.6.3/BBDown_1.6.3_20240814_linux-x64.zip"
unzip /tmp/BBDown.zip -d /tmp/
chmod +x /tmp/BBDown
```

**重要提示**：下载字幕时必须使用 `--skip-ai false` 参数，否则会跳过AI字幕下载。

### 2. 安装FFmpeg
```bash
apt-get install ffmpeg
```

### 3. 配置Notion
```bash
# a) 创建Notion Integration: https://www.notion.so/my-integrations
# b) 复制Internal Integration Token (格式: secret_xxx)
# c) 设置环境变量：
export NOTION_API_KEY=secret_xxx

# d) 分享Integration到你的Notion数据库
# 在Notion中，点击数据库右上角的... → Connections → 选择你的integration
```

### 5. 测试工具
```bash
python3 scripts/test_download.py
```

## 📝 使用方法

### 方法1: 完整工作流程（推荐）
一键完成字幕下载、处理、截图生成和Notion笔记创建：

```bash
cd skills/bilibili-cc-to-notion/scripts

python3 bilibili_to_notion_workflow.py \
  --url "https://www.bilibili.com/video/BV1xx411c7mW" \
  --token "$NOTION_API_KEY" \
  --database-id "your_notion_database_id" \
  --output-dir "./output"
```

### 方法2: 分步执行（模型处理字幕）

#### 1. 下载字幕
```bash
python3 scripts/download_bilibili_cc.py \
  --url "https://www.bilibili.com/video/BV1xx411c7mW" \
  --output "/tmp/subtitles"
```

#### 2. 大模型处理字幕
**你（大模型）负责**：
- 读取字幕文件内容
- 逐字保留所有文字，不删减不总结
- 为每句话添加合适的标点和段落
- **在适当位置添加截图标记** `Screenshot-[hh:mm:ss]`
- 输出结构化的JSON（包含segments和markdown_content）

**截图标记规则**：
- 代码讲解 → 添加截图标记
- UI交互操作 → 添加截图标记
- 视觉指代词（这里、那儿等）→ 添加截图标记
- 网址/链接 → 添加截图标记

#### 3. 生成截图
```bash
python3 scripts/screenshot_tool.py \
  --video "/path/to/video.mp4" \
  --markdown "/path/to/markdown_with_markers.md" \
  --output-dir "/tmp/screenshots"
```

#### 4. 创建Notion笔记（自动上传图片）
```bash
python3 scripts/create_notion_notes_with_images.py \
  --token "$NOTION_API_KEY" \
  --database-id "your_database_id" \
  --video-title "视频标题" \
  --video-url "https://www.bilibili.com/video/BV1xx411c7mW" \
  --segments '[...]' \
  --markdown-content "..." \
  --images-dir "/tmp/screenshots"
```

### 输出格式
```json
{
  "success": true,
  "page_id": "abc123-def456",
  "page_url": "https://www.notion.so/abc123def456",
  "segments_processed": 25,
  "images_embedded": 10,
  "method": "api"
}
```

### 文件上传格式
```json
{
  "success": true,
  "file_upload_id": "3215ec20-99f9-81b2-922c-00b26f84c61e",
  "message": "File uploaded successfully."
}
```

## ⚠️ 重要说明

### 登录要求
- **部分视频需要登录B站账号**才能下载字幕
- 解决方法：
  1. 在浏览器中登录B站账号
  2. 使用BBDown登录功能：`BBDown login`
  3. 或者使用公开视频

### 字幕可用性
- 不是所有B站视频都有字幕
- 部分视频只有自动生成字幕（需要登录才能下载）
- 部分视频完全没有字幕

## 🎯 符合Skill Creator规范

### ✅ 已实现
1. **工具描述清单**: SKILL.md包含完整的工具接口描述
2. **不包含实现代码**: 只描述工具接口，不包含具体实现
3. **模型调用**: 模型负责理解意图并调用工具
4. **测试用例**: 包含完整的测试用例和评估

### 📊 测试结果
- 工具检查: ✅ 通过
- BBDown安装: ✅ 正常
- FFmpeg安装: ✅ 正常
- Notion API: ✅ 测试成功
- 文件上传: ✅ 成功（使用Direct Upload API）
- 图片嵌入: ✅ 成功（已验证file_upload格式）
- 大模型字幕处理: ✅ 已在SKILL.md中明确定义

## 🔍 使用场景

### 场景1: 下载字幕
```
用户: 帮我下载这个B站视频的字幕：BV1xx411c7mW
模型: 调用download_bilibili_cc工具
工具: 使用BBDown下载字幕
结果: 返回字幕文件路径
```

### 场景2: 创建Notion笔记
```
用户: 把这个B站视频做成学习笔记：https://www.bilibili.com/video/BV1xx411c7mW
模型: 
1. 调用download_bilibili_cc下载字幕
2. 调用process_subtitles处理内容
3. 调用create_notion_notes创建笔记
结果: 返回Notion页面链接
```

## 📚 参考资料

- BBDown项目: https://github.com/nilaoda/BBDown
- B站API: https://space.bilibili.com/
- Notion API: https://developers.notion.com/

---

**发布说明**: 安装到你的 `skills` 目录下使用；本仓库不含任何真实密钥。
