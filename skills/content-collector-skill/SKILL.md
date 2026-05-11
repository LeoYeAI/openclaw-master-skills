---
name: content-collector
description: Automatically collect and archive content from shared links in group chats. When a user shares a link (WeChat articles, Feishu docs, web pages, etc.) in any group chat and asks to archive/collect/save it, this skill triggers to fetch the content, create a Feishu document, and update the knowledge base table. Use when: (1) User shares a link and asks to "收录/转存/保存" content, (2) Need to archive web content to Feishu docs, (3) Building a personal knowledge base from shared links, (4) Organizing learning materials from various sources.
---

# Content Collector - 链接内容自动收录技能

## Overview

This skill enables automatic collection and archiving of content from shared links into a structured knowledge base.

**Core Workflow:**
```
Detect Link → Fetch Content → Create Feishu Doc → Update Table
```

## When to Use

### 模式1：主动触发（显式关键词）
当用户消息包含以下**触发词**时，立即执行收录：
- "收录" / "转存" / "保存" / "存档" / "存一下" / "归档" / "备份" / "收藏"
- "存到知识库" / "加入知识库" / "转飞书"

**示例：**
- "这个链接收录一下"
- "存到知识库"
- "转存这篇教程"

### 模式2：静默收录（自动检测）
在**群聊场景**中，自动检测以下链接并静默收录：
- 飞书文档/表格/Wiki（feishu.cn）
- 微信公众号文章（mp.weixin.qq.com）
- 技术博客/教程站点
- 知识分享类链接

**静默收录条件：**
1. 消息来自群聊（非私聊）
2. 消息包含可识别的知识类链接
3. 用户没有明确拒绝的意图

**两种模式优先级：**
```
检测到主动触发词 → 立即收录（显式模式）
未检测到触发词但检测到链接 → 静默收录（隐式模式）
```

## Supported Link Types

| Type | Example | Fetch Method |
|------|---------|--------------|
| WeChat Article | `https://mp.weixin.qq.com/s/xxx` | kimi_fetch |
| Feishu Doc | `https://xxx.feishu.cn/docx/xxx` | feishu_fetch_doc |
| Feishu Wiki | `https://xxx.feishu.cn/wiki/xxx` | feishu_fetch_doc |
| Web Page | General URLs | kimi_fetch / web_fetch |

## Global Availability (全局可用配置)

**生效范围：所有用户、所有群聊**

本技能已配置为全局可用，支持以下对象：

| 对象类型 | 支持状态 | 说明 |
|---------|---------|------|
| **所有用户** | ✅ 可用 | 任何用户分享的链接均可被收录 |
| **所有群聊** | ✅ 可用 | 支持技能中心群、养虾群、学习群等所有群组 |
| **私聊消息** | ✅ 可用 | 用户私信分享链接也可触发收录 |
| **多渠道** | ✅ 可用 | 飞书、其他渠道统一支持 |

**权限说明：**
- 任何用户均可触发收录（无需管理员权限）
- 收录的文档统一存储到指定的知识库目录
- 所有用户均可查看已收录的文档

---

## Installation & Permission Check (安装与权限检查)

在正式使用本技能前，系统必须自动或引导用户完成以下权限校验，以确保流程不中断：

### 1. 飞书权限清单
| 权限项 | 验证工具 | 目的 |
|-------|---------|------|
| **OAuth 授权** | `feishu_oauth` | 获取操作飞书文档和表格的用户凭证 |
| **知识库写入权限** | `feishu_create_doc` | 确保能在指定的 Space ID 下创建节点 |
| **多维表格编辑权限** | `feishu_bitable_app_table_record` | 确保能向指定的 app_token 写入记录 |
| **图片上传权限** | `feishu_im_bot_upload` | 允许将本地图片同步至飞书素材库 |

### 2. 预检流程 (Pre-flight Check)
每次“安装”或配置更新后，执行以下检查：
1. **验证 Space ID 可访问性**：尝试在指定目录下获取节点列表。
2. **验证 Table 结构**：检查 `关键词`、`原链接` 等必需字段是否存在。
3. **静默测试**：如果权限不足，立即通过 `feishu_oauth` 弹出授权引导，而非在执行收录时报错。

---

## Configuration

Before using, ensure these are configured in MEMORY.md:

```markdown
## Content Collector Config
- **Knowledge Base Table**: `[Your Bitable App Token]` (Bitable app_token)
- **Table URL**: [Your Bitable Table URL]
- **Default Table ID**: `[Your Table ID]` (will auto-detect if available)
- **Knowledge Base Space ID**: `[Your Space ID]` (所有文档创建在此知识库下)
- **Knowledge Base URL**: [Your Knowledge Base Homepage URL]
- **Content Categories**: 技术教程, 实战案例, 产品文档, 学习笔记
- **Global Access**: 所有用户可用，所有群聊可用
```

**Note**: 
1. This skill updates ONLY the configured knowledge base table. Do not create or update any other tables.
2. **All created documents must be saved under the designated Knowledge Base** using wiki_node parameter.
3. **Global Access**: 所有用户、所有群聊均可使用本技能，收录的文档对全员可见。

---

## 📚 知识库文档存储规则（必遵守）

所有收录的文档必须按照以下规则分类存储到知识库对应目录：

### 知识库目录结构

请参考各项目或团队定义的知识库标准目录结构进行存储。收录的文档通常存放在“素材”或“归档”类目录下。

### 文档分类映射规则

| 内容分类 | 存储目录 (wiki_node) | 命名前缀 | 示例 |
|----------|---------------------|----------|------|
| 技术教程 | `F9pFw9dxTiXmpsk5bNlco704nag` (内容文档) | 📖 | 📖 [标题] |
| 实战案例 | `F9pFw9dxTiXmpsk5bNlco704nag` (内容文档) | 🛠️ | 🛠️ [标题] |
| 产品文档 | `F9pFw9dxTiXmpsk5bNlco704nag` (内容文档) | 📄 | 📄 [标题] |
| 学习笔记 | `F9pFw9dxTiXmpsk5bNlco704nag` (内容文档) | 💡 | 💡 [标题] |
| 热点资讯 | `F9pFw9dxTiXmpsk5bNlco704nag` (内容文档) | 🔥 | 🔥 [标题] |
| 设计技能 | `F9pFw9dxTiXmpsk5bNlco704nag` (内容文档) | 🎨 | 🎨 [标题] |
| 工具推荐 | `F9pFw9dxTiXmpsk5bNlco704nag` (内容文档) | 🔧 | 🔧 [标题] |
| 训练营 | `F9pFw9dxTiXmpsk5bNlco704nag` (内容文档) | 🎓 | 🎓 [标题] |

### 文档命名规范

```
[Emoji前缀] [原标题] | 收录日期

示例：
📖 OpenClaw保姆级教程 | 2026-03-08
🛠️ 火山方舟自动化报表案例 | 2026-03-08
🔥 GPT-5.4发布解读 | 2026-03-08
```

### 文档模板

```markdown
# [Emoji] [原标题]

> 📌 **元信息**
> - 来源：[原始来源]
> - 原文链接：[原始URL]
> - 收录时间：YYYY-MM-DD
> - 内容分类：[技术教程/实战案例/产品文档/学习笔记/热点资讯/设计技能/工具推荐/训练营]
> - 关键词：[关键词1, 关键词2, 关键词3]

---

## 📋 核心要点

[3-5条核心内容摘要]

---

## 📝 正文内容

[完整的转存内容]

---

## 🔗 相关链接

- 原文链接：[原始URL]
- 知识库索引：[素材池文档索引链接]

---

📚 **收录时间**：YYYY-MM-DD  
🏷️ **分类**：[分类名]  
🔖 **关键词**：[关键词]
```

### 自动更新素材索引

每次收录完成后，必须：

1. **更新多维表格** - 添加新记录到素材池表格
2. **更新素材索引文档** - 在「📚 内容素材池文档索引」中添加条目
3. **更新分类统计** - 更新各分类的文档数量和占比

---

## Workflow

### Step 1: Detect and Parse Link

Extract URL from user message using regex or direct extraction.

### Step 2: Fetch Content

Choose appropriate fetch method based on URL pattern:

**For WeChat articles:**
```python
kimi_fetch(url="https://mp.weixin.qq.com/s/xxx")
```

**For Feishu docs:**
```python
feishu_fetch_doc(doc_id="https://xxx.feishu.cn/docx/xxx")
```

**For general web pages:**
```python
kimi_fetch(url="https://example.com/article")
# or
web_fetch(url="https://example.com/article")
```

### Step 3: Analyze and Categorize

**智能分类判断：**
根据内容特征自动判断分类：

| 判断依据 | 分类 |
|----------|------|
| 包含"安装/配置/部署/教程"等词 | 📖 技术教程 |
| 包含"案例/实战/项目/演示"等词 | 🛠️ 实战案例 |
| 包含"安全/公告/版本/功能"等词 | 📄 产品文档 |
| 包含"学习/成长/指南/笔记"等词 | 💡 学习笔记 |
| 包含"发布/新功能/热点"等词 | 🔥 热点资讯 |
| 包含"设计/Prompt/美学"等词 | 🎨 设计技能 |
| 包含"工具/CLI/插件"等词 | 🔧 工具推荐 |
| 包含"训练营/课程/教学"等词 | 🎓 训练营 |

### Step 4: Process Images (图片处理)

When content contains images, download and upload them to Feishu:

**Image Processing Workflow:**
```python
# 1. Extract image URLs from markdown
import re
image_urls = re.findall(r'!\[.*?\]\((https?://[^\)]+)\)', markdown_content)

# 2. Download and upload each image
for img_url in image_urls:
    try:
        # Download image
        local_path = f"/tmp/img_{hash(img_url)}.jpg"
        download_image(img_url, local_path)
        
        # Upload to Feishu
        upload_result = feishu_im_bot_upload(
            action="upload_image",
            file_path=local_path
        )
        
        # Replace URL in markdown
        new_url = upload_result.get("image_key") or img_url
        markdown_content = markdown_content.replace(img_url, new_url)
        
    except Exception as e:
        # Keep original URL if upload fails
        print(f"Failed to process image {img_url}: {e}")
        continue
```

**Fallback Strategy:**
- If image upload fails, keep original URL
- Add warning note in document
- Include original source link for reference

### Step 5: Create Feishu Document (按知识库规则存储)

Convert processed markdown to Feishu document with proper organization:

```python
# 1. 确定分类和参数
content_category = classify_content(markdown_content)  # 📖/🛠️/📄/💡/🔥/🎨/🔧/🎓
emoji_prefix = get_emoji_prefix(content_category)  # 根据分类获取emoji
wiki_node = get_wiki_node_by_category(content_category)  # 获取存储目录

# 2. 生成文档标题
doc_title = f"{emoji_prefix} {original_title} | {today_date}"

# 3. 生成文档内容（使用标准模板）
doc_content = f"""# {emoji_prefix} {original_title}

> 📌 **元信息**
> - 来源：{source_name}
> - 原文链接：{original_url}
> - 收录时间：{today_date}
> - 内容分类：{content_category}
> - 关键词：{keywords}

---

## 📋 核心要点

{extract_key_points(markdown_content, 5)}

---

## 📝 正文内容

{processed_markdown_content}

---

## 🔗 相关链接

- 原文链接：{original_url}
- 知识库索引：[Your Index Document URL]

---

📅 **收录时间**：{today_date}  
🏷️ **分类**：{content_category}  
🔖 **关键词**：{keywords}
"""

# 4. 创建文档到知识库对应目录
feishu_create_doc(
    title=doc_title,
    markdown=doc_content,
    wiki_node=wiki_node  # 必须指定存储目录
)
```

**存储目录映射：**
| 分类 | wiki_node | 目录名 |
|------|-----------|--------|
| 所有素材 | `F9pFw9dxTiXmpsk5bNlco704nag` | 04-内容素材 |

**IMPORTANT**: 
1. All documents MUST be created under the designated Knowledge Base using wiki_node parameter.
2. Documents must follow the naming convention: `[Emoji] [Title] | [Date]`
3. Documents must use the standard template with metadata section.

### Step 6: Update Knowledge Base Table

Add record to the Bitable knowledge base (ONLY update this specific table):

```python
feishu_bitable_app_table_record(
    action="create",
    app_token="[Your App Token]",  # Configured in MEMORY.md
    table_id="[Your Table ID]",  # Will use correct table ID from the base
    fields={
        "关键词": keywords,
        "内容分类": content_category,
        "文档标题": [{"text": original_title, "type": "text"}],
        "来源": [{"text": source_name, "type": "text"}],
        "核心要点": [{"text": key_points, "type": "text"}],
        "飞书文档链接": {"link": new_doc_url, "text": "飞书文档", "type": "url"},
        "原链接": {"link": original_url, "text": "原文链接", "type": "url"}  # 新增：存储原始链接
    }
)
```

**Table Fields:**
| Field | Type | Description |
|-------|------|-------------|
| 关键词 | Text | Search keywords for the content |
| 内容分类 | Single Select | Category: 📖技术教程/🛠️实战案例/📄产品文档/💡学习笔记/🔥热点资讯/🎨设计技能/🔧工具推荐/🎓训练营 |
| 文档标题 | Text | Title of the archived document |
| 来源 | Text | Original source name |
| 核心要点 | Text | Key points summary (3-5 items) |
| 飞书文档链接 | URL | Link to the created Feishu document |
| 原链接 | URL | **Original source URL** - 新增字段，存储采集的原始链接 |

**IMPORTANT**: Only update the configured knowledge base table. Never create or modify other tables.

### Step 7: Update Content Index Document

After creating the document and updating the table, MUST update the index document:

```python
# 1. 获取当前索引文档内容
index_doc = feishu_fetch_doc(doc_id="[Your Index Doc ID]")

# 2. 在对应分类表格中添加新行
new_index_entry = f"| {original_title} | {source_name} | [查看]({new_doc_url}) |\n"

# 3. 更新分类统计
update_category_stats(content_category)

# 4. 更新总计数
update_total_count()
```

**或者直接追加到索引文档的末尾：**
```python
feishu_update_doc(
    doc_id="[Your Index Doc ID]",
    mode="append",
    markdown=f"""
| {original_title} | {source_name} | [查看]({new_doc_url}) |
"""
)
```

---

## Content Categorization Guide

| Category | Emoji | Description | Examples |
|----------|-------|-------------|----------|
| **技术教程** | 📖 | Step-by-step technical guides | Installation, configuration, API usage |
| **实战案例** | 🛠️ | Real-world implementation examples | Case studies, project demos |
| **产品文档** | 📄 | Product features, security notices | Release notes, security advisories |
| **学习笔记** | 💡 | Conceptual knowledge, methodologies | Best practices, architecture guides |
| **热点资讯** | 🔥 | Breaking news, releases | GPT-5.4, new features |
| **设计技能** | 🎨 | Design, prompts, aesthetics | AJ's prompts, design guides |
| **工具推荐** | 🔧 | Tools, CLI, plugins | gws, trae, autotools |
| **训练营** | 🎓 | Courses, bootcamps, tutorials | OpenClaw bootcamp |

**分类判断优先级：**
1. 优先根据用户指定分类
2. 其次根据标题关键词
3. 最后根据内容特征自动判断
4. 不确定时标记为"待分类"，请用户确认

## Delete Record Process

When user replies "删除" or "删除 [keyword]":

```python
# 1. Search records by keyword
feishu_bitable_app_table_record(
    action="list",
    app_token="[Your App Token]",
    table_id="[Your Table ID]",
    filter={
        "conjunction": "and",
        "conditions": [
            {"field_name": "关键词", "operator": "contains", "value": [keyword]}
        ]
    }
)

# 2. Confirm deletion
# If multiple found → list for user to select
# If single found → ask for confirmation

# 3. Execute deletion
feishu_bitable_app_table_record(
    action="delete",
    app_token="[Your App Token]",
    table_id="[Your Table ID]",
    record_id="record_id_to_delete"
)
```

## Error Handling

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| Fetch timeout | Network issue or heavy content | Retry with longer timeout, or use alternative fetch method |
| Unauthenticated | OAuth token expired or not authed | Trigger `feishu_oauth` to refresh user credentials |
| Permission denied | No write access to Space/Table | Check if user/bot has 'Editor' role in Feishu |
| Content too long | Exceeds API limits | Truncate or split into multiple documents |
| Table update failed | Wrong app_token or table_id | Verify configuration in MEMORY.md |
| Field Missing | "原链接" field not in table | Add the field to Bitable manually or via API |

### Recovery Steps

1. If fetch fails → Try alternative method (kimi_fetch → web_fetch)
2. If Feishu doc creation fails → Check OAuth status
3. If table update fails → Verify table structure and field names
4. Always report partial success (doc created but table not updated)

## Response Template

### 收录成功响应（流式Post格式）

```json
{
  "msg_type": "post",
  "content": {
    "post": {
      "zh_cn": {
        "title": "✅ 收录完成",
        "content": [
          [
            {"tag": "text", "text": "📄 "},
            {"tag": "text", "text": "{emoji} {原标题} | {日期}", "style": {"bold": true}}
          ],
          [{"tag": "text", "text": ""}],
          [
            {"tag": "text", "text": "💡 文档亮点：", "style": {"bold": true}}
          ],
          [
            {"tag": "text", "text": "• {亮点1}"}
          ],
          [
            {"tag": "text", "text": "• {亮点2}"}
          ],
          [
            {"tag": "text", "text": "• {亮点3}"}
          ],
          [{"tag": "text", "text": ""}],
          [
            {"tag": "text", "text": "🔗 "},
            {"tag": "a", "text": "查看飞书文档", "href": "{文档URL}"}
          ]
        ]
      }
    }
  }
}
```

**简洁输出示例：**
```
✅ 收录完成

📄 📖 OpenClaw配置指南 | 2026-03-08

💡 文档亮点：
• 完整配置示例，含9大模块详解
• 多Agent扩展配置方案
• 生产环境安全配置建议

🔗 查看飞书文档 → [点击打开](https://xxx.feishu.cn/docx/xxx)
```

### 静默收录响应（流式Post格式）

```json
{
  "msg_type": "post",
  "content": {
    "post": {
      "zh_cn": {
        "title": "✅ 已自动收录",
        "content": [
          [
            {"tag": "text", "text": "📄 "},
            {"tag": "text", "text": "{emoji} {原标题}", "style": {"bold": true}}
          ],
          [{"tag": "text", "text": ""}],
          [
            {"tag": "text", "text": "💡 亮点：{亮点摘要}"}
          ],
          [{"tag": "text", "text": ""}],
          [
            {"tag": "a", "text": "📎 查看文档", "href": "{文档URL}"}
          ]
        ]
      }
    }
  }
}
```

### 批量收录响应（流式Post格式）

```json
{
  "msg_type": "post",
  "content": {
    "post": {
      "zh_cn": {
        "title": "✅ 批量收录完成（{N}份）",
        "content": [
          [
            {"tag": "text", "text": "📄 {emoji1} {标题1}", "style": {"bold": true}}
          ],
          [
            {"tag": "text", "text": "   💡 {亮点1}"}
          ],
          [
            {"tag": "a", "text": "   🔗 查看", "href": "{链接1}"}
          ],
          [{"tag": "text", "text": ""}],
          [
            {"tag": "text", "text": "📄 {emoji2} {标题2}", "style": {"bold": true}}
          ],
          [
            {"tag": "text", "text": "   💡 {亮点2}"}
          ],
          [
            {"tag": "a", "text": "   🔗 查看", "href": "{链接2}"}
          ]
        ]
      }
    }
  }
}
```

**输出原则：**
1. **必须流式Post格式** - 使用 msg_type: post
2. **只包含3个核心要素：**
   - 文件名称（📄 Emoji + 标题 + 日期）
   - 文档亮点（💡 3-5条核心要点）
   - 飞书链接（🔗 点击查看）
3. **不输出其他信息** - 不显示分类、不显示表格更新、不显示统计
4. **保持简洁** - 每份文档3-5行内容

## Best Practices

1. **Always verify content was fetched correctly** before creating documents
2. **Extract key insights** from the content for the summary
3. **Use appropriate category** based on content nature
4. **Generate relevant keywords** for better searchability
5. **Keep source attribution** clear for copyright respect
6. **Handle partial failures gracefully** - document what succeeded and what failed
7. **Update index document** - Every new document must be added to the index
8. **Follow naming convention** - Use [Emoji] [Title] | [Date] format
9. **Store in correct directory** - Use wiki_node to place in right category

## 收录完成检查清单 (Checklist)

每次收录必须完成以下所有步骤：

- [ ] **执行权限预检**（验证 OAuth 及 Space/Table 写入权限）
- [ ] 获取并处理原始内容（含图片）
- [ ] 智能分类并确定 Emoji 前缀
- [ ] 提取核心要点（3-5条）
- [ ] 生成关键词
- [ ] **创建飞书文档**（使用标准模板，指定 wiki_node）
- [ ] **更新多维表格**（添加完整记录，包含**原链接**字段）
- [ ] **更新文档索引**（在素材索引中添加条目）
- [ ] 发送收录完成通知给用户

**任何一步未完成，视为收录失败！**

## Integration with Memory

After each collection, update MEMORY.md:

```markdown
### YYYY-MM-DD - Content Collection
- **新增收录**: [Title]
- **来源**: [Source]
- **分类**: [Category]
- **知识库状态**: 共[N]条记录
- **索引更新**: ✅ 已更新
```

This skill is part of the core knowledge management system. Execute with care and attention to detail.

---

## 附录：图片处理解决方案

### 问题
原始网页中的图片无法直接显示在飞书文档中（外链限制）

### 解决方案

#### 方案1：自动下载上传（推荐）

**实现步骤**：

```python
import re
import requests
import os

def process_images_in_content(markdown_content):
    """
    处理 Markdown 内容中的图片：
    1. 提取图片URL
    2. 下载到本地
    3. 上传到飞书
    4. 替换为飞书图片链接
    """
    
    # 正则匹配 Markdown 图片: ![alt](url)
    img_pattern = r'!\[(.*?)\]\((https?://[^\)]+)\)'
    
    def replace_image(match):
        alt_text = match.group(1)
        img_url = match.group(2)
        
        try:
            # 1. 下载图片
            local_path = f"/tmp/img_{abs(hash(img_url)) % 100000}.jpg"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(img_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            # 2. 上传到飞书
            upload_result = feishu_im_bot_upload(
                action="upload_image",
                file_path=local_path
            )
            
            image_key = upload_result.get("image_key")
            
            # 3. 清理临时文件
            os.remove(local_path)
            
            # 4. 返回飞书图片格式
            if image_key:
                return f"![{alt_text}]({image_key})"
            else:
                # 上传失败，保留原链接并添加警告
                return f"![{alt_text}]({img_url})\n\n> ⚠️ 图片上传失败，已保留原链接: {img_url}"
                
        except Exception as e:
            # 处理失败，保留原链接
            return f"![{alt_text}]({img_url})\n\n> ⚠️ 图片处理失败: {str(e)[:50]}"
    
    # 执行替换
    processed_content = re.sub(img_pattern, replace_image, markdown_content)
    
    return processed_content
```

**使用方式**：
在创建文档之前调用：
```python
# 获取原始内容
raw_content = kimi_fetch(url=link)

# 处理图片
processed_content = process_images_in_content(raw_content)

# 创建文档（使用处理后的内容）
feishu_create_doc(
    title=title,
    markdown=processed_content
)
```

#### 方案2：保留原链接 + 备用方案

```python
def add_image_fallback_notice(markdown_content, original_url):
    """
    在文档末尾添加图片查看说明
    """
    notice = f"""

---

## 📎 原始图片资源

本文档中的图片已保留原始链接。
如图片无法显示，请查看原文：
[{original_url}]({original_url})

"""
    return markdown_content + notice
```

#### 方案3：批量图片归档

创建一个独立的「图片资源库」多维表格：

```python
# 收录时同时记录图片信息
feishu_bitable_app_table_record(
    action="create",
    app_token="图片资源库_token",
    fields={
        "文档标题": doc_title,
        "图片URL": img_url,
        "图片描述": alt_text,
        "原文链接": original_url,
        "收录状态": "待上传/已上传/失败"
    }
)
```

### 建议实施顺序

1. **短期**（立即）：使用方案2，保留原链接并添加查看提示
2. **中期**（本周）：实施方案1，自动下载上传核心文章的图片
3. **长期**（可选）：建立独立的图片资源库管理系统

### 注意事项

1. **图片大小限制**：飞书图片上传通常限制 10MB
2. **格式支持**：JPG、PNG、GIF 等常见格式
3. **网络超时**：下载图片时设置合理的超时时间（30秒）
4. **失败处理**：单张图片失败不应影响整篇文档收录
5. **版权注意**：确保有权限使用原网页中的图片

---

*图片处理方案 v1.0 - 2026-03-05*
